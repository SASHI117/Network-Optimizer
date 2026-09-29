import os
from pathlib import Path

import pytest

AppTest = pytest.importorskip("streamlit.testing.v1").AppTest
APP = str(Path(__file__).resolve().parents[1] / "app.py")


@pytest.mark.parametrize("page", ["Overview", "Network & Weather", "Signal Model"])
def test_pages_render_without_exceptions(page, monkeypatch):
    monkeypatch.chdir(os.path.dirname(APP))
    at = AppTest.from_file(APP, default_timeout=120).run()
    at.sidebar.radio[0].set_value(page).run()
    assert not at.exception


def test_signal_model_page_reports_both_models(monkeypatch):
    monkeypatch.chdir(os.path.dirname(APP))
    at = AppTest.from_file(APP, default_timeout=120).run()
    at.sidebar.radio[0].set_value("Signal Model").run()
    labels = [m.label for m in at.metric]
    assert "Random Forest RMSE" in labels and "Path-loss baseline RMSE" in labels
