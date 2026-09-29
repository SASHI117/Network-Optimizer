import streamlit as st

from sections.landingpage import show as show_landing
from sections.network import show as show_network
from sections.signal_model_page import show as show_signal_model

st.set_page_config(page_title="Network Optimizer", layout="wide")

st.sidebar.title("📡 Network Optimizer")
PAGES = {
    "Overview": show_landing,
    "Network & Weather": show_network,
    "Signal Model": show_signal_model,
}
page = st.sidebar.radio("Go to", list(PAGES))
PAGES[page]()
