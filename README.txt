# 📡 AI Network Optimizer  

A Streamlit-based tool that combines **cell tower data (OpenCelliD)** and **real-time weather data (OpenWeatherMap)** to analyze and visualize how environmental conditions affect cellular connectivity.  

---

## 🚀 Features  
- 📶 Fetch nearby GSM network towers using OpenCelliD API  
- 🌦 Real-time weather impact analysis with OpenWeatherMap API  
- 🤖 AI-powered optimization insights for better connectivity  
- 📊 Interactive dashboard with Streamlit  

---

## 🛠 Tech Stack  
- Python 3.9+  
- Streamlit  
- Requests (for API calls)  
- Pandas & NumPy (for data processing)  
- Folium / Plotly (for maps & visualization)  

---

## 📂 Project Structure  
Network-Optimizer/
│── api_fetchers.py # Handles API calls (cell towers & weather data)
│── network.py # Core logic to process and analyze data
│── app.py # Streamlit dashboard entry point
│── requirements.txt # Python dependencies
│── README.md # Project documentation

---

## ⚙️ Setup Instructions  

### 1️⃣ Clone the Repository

git clone https://github.com/YOUR-USERNAME/Network-Optimizer.git
cd Network-Optimizer

2️⃣ Create Virtual Environment (Optional but Recommended)

python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Get API Keys
OpenCelliD API Key
OpenWeatherMap API Key

Create a .env file in the project root and add:
OPENCELLID_API_KEY=your_opencellid_key
OPENWEATHER_API_KEY=your_openweather_key

5️⃣ Run the Streamlit App
streamlit run app.py

🌍 Future Enhancements
📡 5G tower data integration

⛈ More advanced weather impact models

📊 Machine learning predictions for network optimization

🤝 Contributing
Contributions, issues, and feature requests are welcome!
Feel free to fork this repo and submit pull requests.
---



ChatGPT can make mistakes. Check important info. Se
