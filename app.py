import streamlit as st
from sections.landingpage import show as show_landing
from sections.network import show as show_network
from sections.ai_assistant import show as show_ai_assistant

# Page setup
st.set_page_config(page_title="Network Optimizer", layout="wide")

# Sidebar
st.sidebar.title("📡 Network Optimizer")
page = st.sidebar.radio("Go to", ["Landing Page", "Network", "AI Assistant"])

# Page navigation
if page == "Landing Page":
    show_landing()
elif page == "Network":
    show_network()
elif page == "AI Assistant":
    show_ai_assistant()
