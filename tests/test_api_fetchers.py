import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import api_fetchers  # noqa: E402


class Resp:
    def __init__(self, status, body=None, text=""):
        self.status_code, self._body, self.text = status, body, text

    def json(self):
        return self._body


def test_cell_lookup_normalises_json(monkeypatch):
    monkeypatch.setattr(api_fetchers.requests, "get", lambda url, params, timeout: Resp(
        200, {"lat": 17.7, "lon": 83.3, "net": 10, "cellid": 555, "averageSignalStrength": -95}))
    cells = api_fetchers.get_cell_towers("k", mcc="404", mnc="10", lac="1", cid="555")["cells"]
    assert cells[0]["mnc"] == 10 and cells[0]["cell"] == 555


def test_cell_lookup_falls_back_to_csv(monkeypatch):
    responses = iter([
        Resp(200, {"error": "Cell not found"}),
        Resp(200, text="radio,mcc,net,area,cell,unit,lon,lat\nLTE,404,10,1,555,0,83.3,17.7"),
    ])
    monkeypatch.setattr(api_fetchers.requests, "get", lambda url, params, timeout: next(responses))
    cell = api_fetchers.get_cell_towers("k", mcc="404", mnc="10", lac="1", cid="555")["cells"][0]
    assert (cell["radio"], cell["lat"], cell["lon"]) == ("LTE", 17.7, 83.3)


def test_network_errors_return_empty(monkeypatch):
    def boom(*a, **k):
        raise api_fetchers.requests.ConnectionError("offline")
    monkeypatch.setattr(api_fetchers.requests, "get", boom)
    assert api_fetchers.get_cell_towers("k", lat=1, lon=2) == {"cells": []}
    assert api_fetchers.get_weather("k", 1, 2) is None
