"""Signal-strength (RSSI) regression: simulator, Random Forest, and baseline.

No labelled drive-test data was collected for this project, so training
data comes from a simulator built on the standard log-distance path-loss
model with log-normal shadowing. The pipeline (features -> model ->
evaluation -> live inference) is real; the numbers it learns are only as
good as the simulator. Upload a real CSV with the same columns in the app
to train on measurements instead.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

WEATHER = ["clear", "cloudy", "rainy"]
FEATURES = ["distance_km", "users_online", "weather_cloudy", "weather_rainy"]
TARGET = "signal_strength"

# Simulator parameters (typical urban macro-cell values at sub-6 GHz)
P0_DBM = -50.0          # received power at the reference distance
D0_KM = 0.05            # reference distance (50 m)
PATH_LOSS_EXP = 3.2     # urban environments: ~2.7-3.5
SHADOWING_SIGMA = 6.0   # log-normal shadowing, dB
# At sub-6 GHz, rain attenuation itself is small; these offsets stand in for
# wet foliage/building effects and are deliberately modest assumptions.
WEATHER_LOSS_DB = {"clear": 0.0, "cloudy": 0.5, "rainy": 2.5}
LOAD_LOSS_DB_PER_USER = 0.08   # crude proxy for interference under load


def path_loss_rssi(distance_km: np.ndarray) -> np.ndarray:
    d = np.maximum(np.asarray(distance_km, dtype=float), D0_KM)
    return P0_DBM - 10 * PATH_LOSS_EXP * np.log10(d / D0_KM)


def simulate(n: int = 3000, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    distance = rng.uniform(0.05, 5.0, n)
    users = rng.integers(1, 120, n)
    weather = rng.choice(WEATHER, n, p=[0.55, 0.3, 0.15])
    rssi = (
        path_loss_rssi(distance)
        - np.vectorize(WEATHER_LOSS_DB.get)(weather)
        - LOAD_LOSS_DB_PER_USER * users
        + rng.normal(0, SHADOWING_SIGMA, n)
    )
    return pd.DataFrame({
        "distance_km": distance.round(3),
        "users_online": users,
        "weather": weather,
        TARGET: np.clip(rssi, -130, -40).round(1),
    })


def to_features(df: pd.DataFrame) -> pd.DataFrame:
    missing = {"distance_km", "users_online", "weather"} - set(df.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    weather = df["weather"].astype(str).str.lower().str.strip()
    unknown = set(weather) - set(WEATHER)
    if unknown:
        raise ValueError(f"unknown weather values {sorted(unknown)}; expected {WEATHER}")
    return pd.DataFrame({
        "distance_km": df["distance_km"].astype(float),
        "users_online": df["users_online"].astype(float),
        "weather_cloudy": (weather == "cloudy").astype(int),
        "weather_rainy": (weather == "rainy").astype(int),
    })


@dataclass
class TrainResult:
    model: RandomForestRegressor
    metrics: dict
    test: pd.DataFrame   # held-out rows with predictions


def _scores(y, p) -> dict:
    return {
        "mae_db": round(float(mean_absolute_error(y, p)), 2),
        "rmse_db": round(float(math.sqrt(mean_squared_error(y, p))), 2),
        "r2": round(float(r2_score(y, p)), 3),
    }


def train(df: pd.DataFrame, seed: int = 42) -> TrainResult:
    X, y = to_features(df), df[TARGET].astype(float)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=seed)

    rf = RandomForestRegressor(n_estimators=300, min_samples_leaf=5, random_state=seed, n_jobs=-1)
    rf.fit(X_tr, y_tr)

    # Physics baseline: linear in log10(distance) plus the other inputs.
    # If the forest cannot beat this, it has learned nothing beyond path loss.
    def with_log(X_):
        return X_.assign(distance_km=np.log10(np.maximum(X_["distance_km"], D0_KM)))
    base = LinearRegression().fit(with_log(X_tr), y_tr)

    pred = rf.predict(X_te)
    test = X_te.assign(actual=y_te, predicted=pred.round(1), error=(pred - y_te).round(1))
    metrics = {
        "random_forest": _scores(y_te, pred),
        "log_distance_baseline": _scores(y_te, base.predict(with_log(X_te))),
        "irreducible_noise_rmse_db": SHADOWING_SIGMA,
        "n_train": len(X_tr),
        "n_test": len(X_te),
        "feature_importance": dict(zip(FEATURES, rf.feature_importances_.round(3).tolist(), strict=True)),
    }
    return TrainResult(rf, metrics, test)


def predict_one(model, distance_km: float, users_online: int, weather: str) -> float:
    row = pd.DataFrame([{"distance_km": distance_km, "users_online": users_online, "weather": weather}])
    return float(model.predict(to_features(row))[0])


def quality_label(rssi_dbm: float) -> str:
    """Rough LTE RSRP-style bands for display."""
    if rssi_dbm >= -80:
        return "Excellent"
    if rssi_dbm >= -90:
        return "Good"
    if rssi_dbm >= -100:
        return "Fair"
    return "Poor"


def weather_category(owm_main: str) -> str:
    """Map an OpenWeatherMap 'main' condition onto the model's categories."""
    main = (owm_main or "").lower()
    if main in {"rain", "drizzle", "thunderstorm", "snow"}:
        return "rainy"
    if main in {"clouds", "mist", "fog", "haze", "smoke", "dust"}:
        return "cloudy"
    return "clear"


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi, dlmb = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))
