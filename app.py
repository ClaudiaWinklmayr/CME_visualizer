import datetime as dt

import requests
import streamlit as st

import cme

st.title("LASCO C2 CME viewer")
day_col, time_col = st.columns(2)
day = day_col.date_input("Date", dt.date(2025, 2, 1))
time = time_col.time_input("Time (UT)", dt.time(2, 12))

if st.button("Find nearest CME and render video"):
    t = dt.datetime.combine(day, time)
    try:
        with st.spinner("Searching catalog and rendering video..."):
            st.session_state.event = cme.find_cme(t)
            st.session_state.video = cme.render(t)
    except (LookupError, FileNotFoundError, requests.RequestException) as e:
        st.session_state.pop("video", None)
        st.error(str(e))

# kept in session_state so the result survives the rerun triggered by the download button
if "video" in st.session_state:
    ev, path = st.session_state.event, st.session_state.video
    st.table({
        "Date/time (UT)": [f"{ev.time:%Y-%m-%d %H:%M:%S}"],
        "CPA [deg]": ["Halo" if ev.cpa != ev.cpa else f"{ev.cpa:g}"],
        "Width [deg]": [ev.width],
        "Remark": [ev.remark],
    })
    st.video(str(path))
    st.download_button("Download mp4", path.read_bytes(), path.name, "video/mp4")
