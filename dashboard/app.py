import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

DB = "data/telemetry.db"

st.set_page_config(page_title="AURA Hardware Health", layout="wide")
st.title("AURA — Hardware Health Dashboard")
st.caption("Edge telemetry and anomaly-monitoring prototype")

try:
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT 500", conn)
    conn.close()
except Exception:
    st.error("No telemetry database found. Start the collector first.")
    st.stop()

if df.empty:
    st.warning("No telemetry available.")
    st.stop()

df["timestamp"] = pd.to_datetime(df["timestamp"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Temperature °C", f"{df.iloc[0]['temperature_c']:.2f}")
c2.metric("Humidity %", f"{df.iloc[0]['humidity_pct']:.1f}")
c3.metric("Voltage V", f"{df.iloc[0]['voltage_v']:.3f}")
c4.metric("Current A", f"{df.iloc[0]['current_a']:.3f}")

for column, title in [
    ("temperature_c", "Temperature"),
    ("humidity_pct", "Humidity"),
    ("vibration_g", "Vibration"),
    ("voltage_v", "Voltage"),
    ("current_a", "Current"),
    ("power_w", "Power")
]:
    if column in df:
        fig = px.line(df.sort_values("timestamp"), x="timestamp", y=column, title=title)
        st.plotly_chart(fig, use_container_width=True)
