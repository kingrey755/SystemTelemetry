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
st.caption("System Performance")

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

MAX_POINTS = 60  

col1, col2, col3, col4 = st.columns(4)

cpu_metric = col1.empty()
ram_metric = col2.empty()
disk_metric = col3.empty()
net_metric = col4.empty()

chart_cpu = st.empty()
chart_ram = st.empty()
chart_disk = st.empty()
chart_net = st.empty()

net_prev = psutil.net_io_counters()

while True:
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    net_now = psutil.net_io_counters()
    net_sent = (net_now.bytes_sent - net_prev.bytes_sent) / 1024
    net_recv = (net_now.bytes_recv - net_prev.bytes_recv) / 1024
    net_prev = net_now

    now = datetime.now().strftime("%H:%M:%S")

    new_row = {
        "time": now,
        "cpu": cpu,
        "ram": ram,
        "disk": disk,
        "net_sent": net_sent,
        "net_recv": net_recv,
    }

    st.session_state.data = pd.concat(
        [st.session_state.data, pd.DataFrame([new_row])]
    ).tail(MAX_POINTS)

    df = st.session_state.data


    cpu_metric.metric("CPU Usage", f"{cpu:.1f} %")
    ram_metric.metric("RAM Usage", f"{ram:.1f} %")
    disk_metric.metric("Disk Usage", f"{disk:.1f} %")
    net_metric.metric("Network KB/s", f"↑ {net_sent:.1f} | ↓ {net_recv:.1f}")


    chart_cpu.line_chart(df.set_index("time")["cpu"], height=200)
    chart_ram.line_chart(df.set_index("time")["ram"], height=200)
    chart_disk.line_chart(df.set_index("time")["disk"], height=200)

    chart_net.line_chart(
        df.set_index("time")[["net_sent", "net_recv"]],
        height=200
    )

    time.sleep(1)
