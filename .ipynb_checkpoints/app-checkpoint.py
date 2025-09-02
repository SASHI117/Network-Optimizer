import streamlit as st
from sections import landing
from sections import network
from sections import ai_assistant

st.set_page_config(
    page_title="📡 Network Optimizer",
    page_icon="📶",
    layout="wide"
)

# Sidebar Navigation
st.sidebar.title("📂 Navigation")
section = st.sidebar.radio("Go to:", ["🏠 Landing", "📡 Network Analysis", "🤖 AI Assistant"])

if section == "🏠 Landing":
    landing.show()
elif section == "📡 Network Analysis":
    network.show()
elif section == "🤖 AI Assistant":
    ai_assistant.show()
