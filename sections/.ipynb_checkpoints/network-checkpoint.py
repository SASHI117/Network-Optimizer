import streamlit as st
import pandas as pd
from utils.api_fetchers import get_cell_towers, get_weather

def show():
    st.title("📡 Network Health & Weather Impact")
    st.write("Analyze network signals and check weather conditions that impact connectivity.")

    # ⚠️ Country-specific warning
    st.warning("⚠️ OpenCelliD may not return results for **India** using latitude/longitude. "
               "For India, enter MCC/MNC/LAC/Cell ID manually. Works fine for other countries.")

    # Sidebar for API Keys
    st.sidebar.header("🔑 API Keys")
    OPENCELLID_KEY = st.sidebar.text_input("OpenCelliD Key", type="password")
    WEATHER_KEY = st.sidebar.text_input("OpenWeatherMap Key", type="password")

    # User Inputs
    st.subheader("📍 Location Input")
    mode = st.radio("Select Input Mode:", ["Latitude/Longitude", "MCC/MNC/LAC/Cell ID"])

    lat = lon = mcc = mnc = lac = cid = None

    if mode == "Latitude/Longitude":
        lat = st.number_input("Latitude", value=40.7128)
        lon = st.number_input("Longitude", value=-74.0060)  # Default NYC
    else:
        mcc = st.text_input("MCC (Mobile Country Code)")
        mnc = st.text_input("MNC (Mobile Network Code)")
        lac = st.text_input("LAC (Location Area Code)")
        cid = st.text_input("Cell ID")

    if st.button("🔍 Analyze Data"):
        if not OPENCELLID_KEY or not WEATHER_KEY:
            st.error("⚠️ Please enter both API keys to proceed!")
        else:
            with st.spinner("Fetching real-time data..."):
                towers = get_cell_towers(OPENCELLID_KEY, lat, lon, mcc, mnc, lac, cid)
                weather = get_weather(WEATHER_KEY, lat, lon) if lat and lon else None

                if towers:
                    df_towers = pd.DataFrame(towers.get("cells", []))  # adjust to API response

                    if not df_towers.empty:
                        st.subheader("📡 Weak Signal Towers")
                        if "averageSignalStrength" in df_towers.columns:
                            low_signal = df_towers[df_towers['averageSignalStrength'] < -90]
                            if not low_signal.empty:
                                st.map(low_signal[['lat', 'lon']], zoom=12)
                                st.dataframe(low_signal[['lat', 'lon', 'averageSignalStrength']])
                            else:
                                st.success("✅ All nearby towers have good signal strength!")
                        else:
                            st.info("ℹ️ No signal strength data available for this location.")
                    else:
                        st.error("❌ No towers found for the given input.")
                else:
                    st.error("❌ API fetch failed! Please check your keys or try again later.")

                # Weather Alert
                if weather:
                    df_weather = pd.json_normalize(weather)
                    weather_main = df_weather['weather'][0]['main'].lower()
                    if "rain" in weather_main:
                        st.warning(f"⚠️ Rain detected ({weather_main}). Network conditions may be affected!")
