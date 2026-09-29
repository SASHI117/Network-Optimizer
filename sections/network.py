import os

import pandas as pd
import streamlit as st

from sections.signal_model_page import get_model
from utils import signal_model as sm
from utils.api_fetchers import get_cell_towers, get_weather


def _secret(name: str) -> str:
    """Env var or .streamlit/secrets.toml, so keys need not be typed each time."""
    try:
        return os.getenv(name) or st.secrets.get(name, "")
    except Exception:  # no secrets.toml
        return os.getenv(name, "")

def show():
    st.title("📡 Unified Network & Weather Analyzer")
    st.write("Enter coordinates and/or a specific cell (MCC/MNC/LAC/CID). We'll fetch towers and weather together.")

    # Sidebar – API keys
    st.sidebar.header("🔑 API Keys")
    OPENCELLID_KEY = st.sidebar.text_input("OpenCelliD Key", value=_secret("OPENCELLID_API_KEY"), type="password")
    WEATHER_KEY = st.sidebar.text_input("OpenWeatherMap Key", value=_secret("OPENWEATHER_API_KEY"), type="password")
    users_online = st.sidebar.slider("Assumed users online (cell load)", 1, 120, 30)

    # Inputs (both at once)
    st.subheader("📍 Inputs")
    left, right = st.columns(2)

    with left:
        st.markdown("**Coordinates (optional)**")
        lat = st.number_input("Latitude", value=40.712800, format="%.6f")
        lon = st.number_input("Longitude", value=-74.006000, format="%.6f")

    with right:
        st.markdown("**Cell Tower (optional)**")
        mcc = st.text_input("MCC (Mobile Country Code)", value="", placeholder="e.g., 472")
        mnc = st.text_input("MNC (Mobile Network Code)", value="", placeholder="e.g., 1")
        lac = st.text_input("LAC (Location Area Code)", value="", placeholder="e.g., 40")
        cid = st.text_input("Cell ID", value="", placeholder="e.g., 31231")

    # Helper to treat empty strings as None
    def _nz(x):
        x = (x or "").strip()
        return x if x != "" else None

    if st.button("🔍 Analyze Data"):
        if not OPENCELLID_KEY and not WEATHER_KEY:
            st.error("Please enter at least one API key in the sidebar.")
            return

        # -------------------- 📡 Towers --------------------
        towers_resp = {"cells": []}
        if OPENCELLID_KEY:
            towers_resp = get_cell_towers(
                OPENCELLID_KEY,
                lat=lat, lon=lon,
                mcc=_nz(mcc), mnc=_nz(mnc), lac=_nz(lac), cid=_nz(cid)
            ) or {"cells": []}

        df_towers = pd.DataFrame()
        tower_coords_for_weather = None

        if isinstance(towers_resp, dict) and towers_resp.get("cells"):
            df_towers = pd.DataFrame(towers_resp["cells"])
            # Try to grab one coordinate from towers for weather fallback
            for col_lat, col_lon in [("lat", "lon"), ("latitude", "longitude")]:
                if col_lat in df_towers.columns and col_lon in df_towers.columns:
                    coords = df_towers[[col_lat, col_lon]].dropna().head(1)
                    if not coords.empty:
                        tower_coords_for_weather = (float(coords.iloc[0, 0]), float(coords.iloc[0, 1]))
                        break

        st.subheader("📡 Towers")
        if not df_towers.empty:
            # Ensure columns are named lat/lon for st.map
            if "lat" not in df_towers.columns and "latitude" in df_towers.columns:
                df_towers = df_towers.rename(columns={"latitude": "lat"})
            if "lon" not in df_towers.columns and "longitude" in df_towers.columns:
                df_towers = df_towers.rename(columns={"longitude": "lon"})

            if {"lat", "lon"}.issubset(df_towers.columns):
                st.map(df_towers[["lat", "lon"]], zoom=12)

            st.dataframe(df_towers)

            if "averageSignalStrength" in df_towers.columns:
                # try numeric comparison; non-numeric will be NaN then ignored
                weak = df_towers[pd.to_numeric(df_towers["averageSignalStrength"], errors="coerce") < -90]
                if not weak.empty:
                    st.warning(f"⚠️ {len(weak)} weak-signal tower(s) detected (< -90 dBm).")
                else:
                    st.success("✅ All listed towers have acceptable signal strength.")
        else:
            if OPENCELLID_KEY:
                st.error("❌ No towers found or tower API failed. Check your inputs and OpenCelliD key.")
            else:
                st.info("ℹ️ Enter an OpenCelliD key to fetch towers.")

        # -------------------- 🌦 Weather --------------------
        weather = None
        weather_latlon_source = None
        final_lat, final_lon = None, None

        if WEATHER_KEY:
            # Prefer user coordinates if provided; otherwise use tower coords
            if lat is not None and lon is not None and str(lat) != "" and str(lon) != "":
                final_lat, final_lon = lat, lon
                weather_latlon_source = "user"
            elif tower_coords_for_weather:
                final_lat, final_lon = tower_coords_for_weather
                weather_latlon_source = "tower"

            if final_lat is not None and final_lon is not None:
                weather = get_weather(WEATHER_KEY, final_lat, final_lon)

        st.subheader("🌦 Weather")
        if weather and isinstance(weather, dict) and weather.get("cod") == 200:
            try:
                w_list = weather.get("weather", [])
                main = (w_list[0].get("main", "") if isinstance(w_list, list) and w_list else "").lower()
                desc = w_list[0].get("description", "") if isinstance(w_list, list) and w_list else ""
                temp = weather.get("main", {}).get("temp")

                if weather_latlon_source == "tower":
                    st.info("Used tower coordinates for weather (no user lat/lon provided).")

                headline = f"{desc.capitalize() or main.capitalize()}"
                if temp is not None:
                    headline += f" • {temp} °C"

                if "rain" in main:
                    st.warning(f"⚠️ {headline} — network conditions may be affected.")
                else:
                    st.success(f"✅ {headline} — no major impact expected.")
            except Exception as e:
                st.info(f"Weather data received but couldn't be parsed ({e}).")
                st.json(weather)
        else:
            if WEATHER_KEY:
                st.info("ℹ️ Weather API did not return results for the provided coordinates.")
            else:
                st.info("ℹ️ Enter an OpenWeatherMap key to see weather.")

        # -------------------- 📶 Live prediction --------------------
        st.subheader("📶 Predicted signal at your location")
        nearest_km = None
        if not df_towers.empty and {"lat", "lon"}.issubset(df_towers.columns):
            coords = df_towers[["lat", "lon"]].dropna()
            if not coords.empty:
                nearest_km = min(sm.haversine_km(lat, lon, r.lat, r.lon) for r in coords.itertuples())

        owm_main = ""
        if weather and weather.get("cod") == 200 and weather.get("weather"):
            owm_main = weather["weather"][0].get("main", "")
        category = sm.weather_category(owm_main)

        if nearest_km is None:
            st.info("Need at least one tower with coordinates to estimate distance.")
        else:
            model = get_model().model
            rssi = sm.predict_one(model, max(nearest_km, 0.05), users_online, category)
            c1, c2, c3 = st.columns(3)
            c1.metric("Nearest tower", f"{nearest_km:.2f} km")
            c2.metric("Weather input", category, owm_main or "no live weather", delta_color="off")
            c3.metric("Predicted signal", f"{rssi:.1f} dBm", sm.quality_label(rssi), delta_color="off")
            st.caption("Random Forest from the Signal Model page; trained on simulated data unless you uploaded measurements.")
