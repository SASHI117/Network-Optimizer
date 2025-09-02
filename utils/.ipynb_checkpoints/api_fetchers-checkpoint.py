import requests

# 📡 Fetch cell towers from OpenCelliD
def get_cell_towers(api_key, lat=None, lon=None, mcc=None, mnc=None, lac=None, cid=None, radius=5000):
    url = "https://opencellid.org/api/cell/search"
    params = {
        "key": api_key,
        "format": "json"
    }

    # If MCC/MNC/LAC/CellID provided (manual India testing)
    if mcc and mnc and lac and cid:
        params.update({"mcc": mcc, "mnc": mnc, "lac": lac, "cellid": cid})
    else:
        params.update({"lat": lat, "lon": lon, "distance": radius})

    response = requests.get(url, params=params)
    if response.status_code == 200:
        try:
            return response.json()
        except Exception as e:
            print("JSON Parse Error:", e)
            return None
    else:
        print("OpenCelliD Error:", response.text)
        return None


# 🌦 Fetch weather from OpenWeatherMap
def get_weather(api_key, lat, lon):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Weather API Error:", response.text)
        return None
