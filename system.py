import streamlit as st
import psutil
import pandas as pd
import time
from datetime import datetime

st.set_page_config(
    page_title="System Telemetry",
    layout="wide"
)

st.title("System Telemetry Dashboard")
st.caption("Live system performance monitoring")


if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(
        columns=[
            "time",
            "cpu",
            "ram",
            "disk",
            "net_sent",
            "net_recv"
        ]
    )

if "net_prev" not in st.session_state:
    st.session_state.net_prev = psutil.net_io_counters()

if "running" not in st.session_state:
    st.session_state.running = True

MAX_POINTS = 60

col_ctrl_1, col_ctrl_2 = st.columns(2)

with col_ctrl_1:
    if st.button("▶ Start"):
        st.session_state.running = True

with col_ctrl_2:
    if st.button("⏹ Stop"):
        st.session_state.running = False

m1, m2, m3, m4 = st.columns(4)

cpu_metric = m1.empty()
ram_metric = m2.empty()
disk_metric = m3.empty()
net_metric = m4.empty()

chart_cpu = st.empty()
chart_ram = st.empty()
chart_disk = st.empty()
chart_net = st.empty()


if st.session_state.running:
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    net_now = psutil.net_io_counters()
    net_sent = (net_now.bytes_sent - st.session_state.net_prev.bytes_sent) / 1024
    net_recv = (net_now.bytes_recv - st.session_state.net_prev.bytes_recv) / 1024
    st.session_state.net_prev = net_now

    now = datetime.now().strftime("%H:%M:%S")

    new_row = pd.DataFrame([{
        "time": now,
        "cpu": cpu,
        "ram": ram,
        "disk": disk,
        "net_sent": net_sent,
        "net_recv": net_recv
    }])

    st.session_state.data = (
        pd.concat([st.session_state.data, new_row])
        .tail(MAX_POINTS)
        .reset_index(drop=True)
    )


df = st.session_state.data

if not df.empty:
    cpu_metric.metric("CPU Usage", f"{df.iloc[-1]['cpu']:.1f} %")
    ram_metric.metric("RAM Usage", f"{df.iloc[-1]['ram']:.1f} %")
    disk_metric.metric("Disk Usage", f"{df.iloc[-1]['disk']:.1f} %")
    net_metric.metric(
        "Network KB/s",
        f"↑ {df.iloc[-1]['net_sent']:.1f} | ↓ {df.iloc[-1]['net_recv']:.1f}"
    )

    chart_cpu.line_chart(df.set_index("time")["cpu"], height=200)
    chart_ram.line_chart(df.set_index("time")["ram"], height=200)
    chart_disk.line_chart(df.set_index("time")["disk"], height=200)
    chart_net.line_chart(
        df.set_index("time")[["net_sent", "net_recv"]],
        height=200
    )

time.sleep(1)
st.rerun()
