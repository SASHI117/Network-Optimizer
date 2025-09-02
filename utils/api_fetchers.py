import requests
import csv
import io

def _safe_int(x):
    try:
        return int(x)
    except Exception:
        return None

def _safe_float(x):
    try:
        return float(x)
    except Exception:
        return None

def _normalize_cell_from_csv(cols):
    """
    CSV columns order (OpenCelliD):
    radio, mcc, net, area, cell, unit, lon, lat, range, samples,
    changeable, created, updated, averageSignalStrength
    """
    cell = {
        "radio": cols[0] if len(cols) > 0 else None,
        "mcc": _safe_int(cols[1]) if len(cols) > 1 else None,
        "mnc": _safe_int(cols[2]) if len(cols) > 2 else None,  # 'net' -> mnc
        "area": _safe_int(cols[3]) if len(cols) > 3 else None,  # LAC
        "cell": _safe_int(cols[4]) if len(cols) > 4 else None,  # CID
        "unit": _safe_int(cols[5]) if len(cols) > 5 else None,
        "lon": _safe_float(cols[6]) if len(cols) > 6 else None,
        "lat": _safe_float(cols[7]) if len(cols) > 7 else None,
        "range": _safe_int(cols[8]) if len(cols) > 8 else None,
        "samples": _safe_int(cols[9]) if len(cols) > 9 else None,
        "changeable": _safe_int(cols[10]) if len(cols) > 10 else None,
        "created": cols[11] if len(cols) > 11 else None,
        "updated": cols[12] if len(cols) > 12 else None,
        "averageSignalStrength": _safe_float(cols[13]) if len(cols) > 13 and cols[13] != "" else None,
    }
    return cell

def _normalize_cell_from_json(d):
    """
    Normalize /cell/get JSON into a cell dict compatible with your app.
    OpenCelliD JSON may use 'net' (MNC) and 'cellid' (CID).
    """
    cell = dict(d) if isinstance(d, dict) else {}
    if "net" in cell and "mnc" not in cell:
        cell["mnc"] = cell.get("net")
    if "cellid" in cell and "cell" not in cell:
        cell["cell"] = cell.get("cellid")
    # Ensure keys used by the UI exist (even if None)
    cell.setdefault("lat", cell.get("latitude"))
    cell.setdefault("lon", cell.get("longitude"))
    cell.setdefault("averageSignalStrength", cell.get("averageSignalStrength"))
    return cell

# 📡 Fetch cell towers (Lat/Lon search OR MCC/MNC/LAC/CID lookup)
def get_cell_towers(api_key, lat=None, lon=None, mcc=None, mnc=None, lac=None, cid=None, radius=5000, timeout=15):
    try:
        # ======== MCC/MNC/LAC/CID mode (single tower lookup) ========
        if mcc and mnc and lac and cid:
            # 1) Try JSON first
            url = "https://opencellid.org/cell/get"
            params = {
                "key": api_key,
                "mcc": mcc,
                "mnc": mnc,
                "lac": lac,
                "cellid": cid,
                "format": "json",
            }
            r = requests.get(url, params=params, timeout=timeout)
            if r.status_code == 200:
                data = r.json()
                # data can be {"error":"Cell not found"} or a dict with cell fields
                if isinstance(data, dict) and not data.get("error"):
                    cell = _normalize_cell_from_json(data)
                    return {"cells": [cell]}

            # 2) Fallback to CSV
            params["format"] = "csv"
            r = requests.get(url, params=params, timeout=timeout)
            if r.status_code == 200:
                text = r.text.strip()
                if text:
                    rows = list(csv.reader(io.StringIO(text)))
                    # If header present, skip it
                    if rows and rows[0] and ("radio" in ",".join(rows[0]).lower()):
                        rows = rows[1:]
                    if rows:
                        cell = _normalize_cell_from_csv(rows[0])
                        return {"cells": [cell]}
            # Nothing found
            return {"cells": []}

        # ======== Lat/Lon mode (nearby towers search) ========
        if lat is None or lon is None:
            return {"cells": []}

        url = "https://opencellid.org/api/cell/search"
        params = {
            "key": api_key,
            "lat": lat,
            "lon": lon,
            "distance": radius,   # meters
            "format": "json",
        }
        r = requests.get(url, params=params, timeout=timeout)
        if r.status_code == 200:
            data = r.json()
            # Some responses come as a list; others as {"cells":[...]}
            if isinstance(data, dict) and "cells" in data:
                return {"cells": data["cells"] or []}
            if isinstance(data, list):
                return {"cells": data}
            return {"cells": []}

        # Non-200
        print("OpenCelliD search error:", r.status_code, r.text[:300])
        return {"cells": []}

    except Exception as e:
        print("Cell Tower Fetch Error:", e)
        return {"cells": []}

# 🌦 Fetch weather from OpenWeatherMap
def get_weather(api_key, lat, lon, timeout=15):
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": "metric",
        }
        r = requests.get(url, params=params, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        print("Weather API Error:", r.status_code, r.text[:300])
        return None
    except Exception as e:
        print("Weather Fetch Error:", e)
        return None
