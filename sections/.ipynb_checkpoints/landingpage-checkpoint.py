import streamlit as st

def show():
    st.title("📶 Network Optimizer")
    st.image("Images/ai-visual.jpg", use_container_width=True)

    st.markdown("""
    Welcome to **Network Optimizer** 🚀  
    This tool helps you analyze **cellular network coverage** 📡 and understand how **weather impacts connectivity** 🌦.

    ### 🔑 Features:
    - 📡 **Network Analysis**: Fetch nearby cell tower data from OpenCelliD.  
    - 🌦 **Weather Impact**: Get real-time weather conditions from OpenWeatherMap.  
    - 🤖 **AI Assistant**: Optimize your network performance using AI insights.  

    ### ⚠️ Important Notes:
    - OpenCelliD **may not return results for India** using latitude/longitude.  
    - For India, you must enter **MCC, MNC, LAC, and Cell ID manually**.  
    - Works smoothly for **other countries** with latitude/longitude search.  
    """)
