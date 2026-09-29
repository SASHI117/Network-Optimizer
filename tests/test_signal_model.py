import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import signal_model as sm  # noqa: E402


def test_path_loss_decreases_with_distance():
    near, far = sm.path_loss_rssi([0.1, 2.0])
    assert near > far
    assert sm.path_loss_rssi([sm.D0_KM])[0] == pytest.approx(sm.P0_DBM)


def test_simulator_is_deterministic_and_plausible():
    a, b = sm.simulate(500, seed=3), sm.simulate(500, seed=3)
    pd.testing.assert_frame_equal(a, b)
    assert a[sm.TARGET].between(-130, -40).all()
    assert set(a["weather"]) == set(sm.WEATHER)


def test_to_features_validates_input():
    with pytest.raises(ValueError, match="missing columns"):
        sm.to_features(pd.DataFrame({"distance_km": [1.0]}))
    with pytest.raises(ValueError, match="unknown weather"):
        sm.to_features(pd.DataFrame({"distance_km": [1], "users_online": [3], "weather": ["foggy"]}))
    f = sm.to_features(pd.DataFrame({"distance_km": [1], "users_online": [3], "weather": [" Rainy "]}))
    assert f.iloc[0].to_dict() == {"distance_km": 1.0, "users_online": 3.0, "weather_cloudy": 0, "weather_rainy": 1}


def test_model_approaches_the_noise_floor():
    r = sm.train(sm.simulate(3000))
    rf, base = r.metrics["random_forest"], r.metrics["log_distance_baseline"]
    # nothing can beat the shadowing noise; a working model should be close to it
    assert rf["rmse_db"] < sm.SHADOWING_SIGMA * 1.15
    assert base["rmse_db"] < sm.SHADOWING_SIGMA * 1.1
    assert max(r.metrics["feature_importance"], key=r.metrics["feature_importance"].get) == "distance_km"
    assert sm.predict_one(r.model, 0.2, 10, "clear") > sm.predict_one(r.model, 4.0, 10, "clear")


@pytest.mark.parametrize("owm, expected", [
    ("Rain", "rainy"), ("Thunderstorm", "rainy"), ("Clouds", "cloudy"),
    ("Haze", "cloudy"), ("Clear", "clear"), ("", "clear"),
])
def test_weather_category(owm, expected):
    assert sm.weather_category(owm) == expected


def test_haversine_known_distance():
    # Visakhapatnam -> Hyderabad is roughly 500 km in a straight line
    assert sm.haversine_km(17.6868, 83.2185, 17.3850, 78.4867) == pytest.approx(502, abs=10)
    assert sm.haversine_km(10, 10, 10, 10) == 0


def test_quality_bands():
    assert [sm.quality_label(x) for x in (-70, -85, -95, -110)] == ["Excellent", "Good", "Fair", "Poor"]
