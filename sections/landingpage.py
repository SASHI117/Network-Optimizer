# sections/landingpage.py
import streamlit as st

def show():
    st.title("Welcome to Network Optimizer 🚀")
    st.image("Images/ai-generated-8259052.jpg", use_container_width=True)
    st.write("Optimize your network using AI-powered insights.")
    
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
