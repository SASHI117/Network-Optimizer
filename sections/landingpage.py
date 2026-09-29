from pathlib import Path

import streamlit as st

HERO = Path(__file__).resolve().parents[1] / "Images" / "ai-generated-8259052.jpg"


def show():
    st.title("Network Optimizer 📡")
    st.image(str(HERO), width="stretch")
    st.markdown("""
    Estimate cellular signal quality at a location by combining **live cell-tower data**
    (OpenCelliD), **live weather** (OpenWeatherMap) and a **Random Forest** signal model.

    ### Pages
    - **Network & Weather**: nearby towers on a map, current weather, and the predicted
      signal at your coordinates from the nearest tower's distance, current weather and cell load.
    - **Signal Model**: how the model is trained and evaluated against a path-loss baseline,
      what-if predictions, and training on your own measurements (CSV upload).

    ### Notes
    - OpenCelliD's area search often returns nothing for India. There, look up a specific cell
      with **MCC, MNC, LAC and Cell ID** (visible in Android field-test / network-info apps).
    - API keys can be typed in the sidebar or set as `OPENCELLID_API_KEY` / `OPENWEATHER_API_KEY`
      (environment or `.streamlit/secrets.toml`).
    """)
