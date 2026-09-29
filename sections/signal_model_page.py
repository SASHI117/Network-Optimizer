import pandas as pd
import streamlit as st

from utils import signal_model as sm


@st.cache_resource(show_spinner="Training Random Forest on simulated measurements...")
def default_model():
    return sm.train(sm.simulate())


def get_model():
    """The model trained on uploaded data if there is one, else the default."""
    return st.session_state.get("custom_model") or default_model()


def show():
    st.title("📶 Signal Strength Model")
    st.markdown(
        "A **Random Forest regressor** predicts received signal strength (dBm) from distance to the "
        "serving tower, cell load (users online) and weather. It is compared against a "
        "**log-distance path-loss baseline**, the standard physics model.\n\n"
        "> ⚠️ By default it trains on **simulated** data (log-distance path loss with 6 dB "
        "log-normal shadowing). Upload real measurements below to train on those instead."
    )

    uploaded = st.file_uploader(
        "Optional: CSV with columns distance_km, users_online, weather (clear/cloudy/rainy), signal_strength",
        type=["csv"],
    )
    if uploaded is not None:
        try:
            st.session_state["custom_model"] = sm.train(pd.read_csv(uploaded))
            st.success("Trained on your data.")
        except (ValueError, KeyError) as e:
            st.error(f"Could not train on this file: {e}")
    elif st.session_state.get("custom_model") and st.button("Revert to simulated data"):
        st.session_state.pop("custom_model")

    result = get_model()
    m = result.metrics

    st.subheader("Held-out performance")
    cols = st.columns(3)
    cols[0].metric("Random Forest RMSE", f"{m['random_forest']['rmse_db']} dB")
    cols[1].metric("Path-loss baseline RMSE", f"{m['log_distance_baseline']['rmse_db']} dB")
    cols[2].metric("Random Forest R²", m["random_forest"]["r2"])
    st.caption(
        f"{m['n_train']} training / {m['n_test']} test rows. On simulated data the shadowing noise "
        f"({m['irreducible_noise_rmse_db']} dB) is the floor no model can beat."
    )

    st.subheader("Actual vs predicted")
    st.scatter_chart(result.test, x="actual", y="predicted", height=320)

    st.subheader("Feature importance")
    st.bar_chart(pd.Series(m["feature_importance"], name="importance"), horizontal=True, height=220)

    st.subheader("What-if prediction")
    c1, c2, c3 = st.columns(3)
    dist = c1.slider("Distance to tower (km)", 0.05, 5.0, 1.0, 0.05)
    users = c2.slider("Users online in the cell", 1, 120, 30)
    weather = c3.selectbox("Weather", sm.WEATHER)
    rssi = sm.predict_one(result.model, dist, users, weather)
    st.metric("Predicted signal", f"{rssi:.1f} dBm", sm.quality_label(rssi), delta_color="off")

    st.download_button(
        "Download held-out predictions (CSV)",
        result.test.to_csv(index=False).encode(),
        file_name="signal_predictions.csv",
        mime="text/csv",
    )
