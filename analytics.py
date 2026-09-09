"""Visual analytics for the imported PyroLytic experiment database."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from literature_browser import query_experiments


def render() -> None:
    rows = query_experiments()
    if not rows:
        return
    frame = pd.DataFrame(rows)
    st.subheader("Yield analytics")
    st.caption("Explore reported values by temperature and feedstock. Each point is an extracted experiment.")

    types = sorted(frame["plastic_type"].dropna().unique().tolist())
    selected = st.selectbox("Feedstock for temperature chart", ["All"] + types, key="analytics_plastic")
    chart_frame = frame if selected == "All" else frame[frame["plastic_type"] == selected]
    chart_frame = chart_frame.dropna(subset=["temperature_c", "oil_yield_wt_pct"])
    if chart_frame.empty:
        st.info("No temperature and oil-yield pairs are available for this selection.")
    else:
        points = chart_frame[["temperature_c", "oil_yield_wt_pct"]].rename(
            columns={"temperature_c": "Temperature (°C)", "oil_yield_wt_pct": "Oil yield (wt%)"}
        ).sort_values("Temperature (°C)").set_index("Temperature (°C)")
        st.line_chart(points, y="Oil yield (wt%)", height=300)

    left, right = st.columns(2)
    with left:
        summary = (
            frame.groupby("plastic_type", dropna=False)["oil_yield_wt_pct"]
            .agg(["count", "mean", "min", "max"])
            .rename(columns={"count": "Experiments", "mean": "Mean oil yield", "min": "Minimum", "max": "Maximum"})
            .round(1)
        )
        st.markdown("**Oil yield by feedstock**")
        st.dataframe(summary, use_container_width=True)
    with right:
        confidence = frame.groupby("confidence", dropna=False).size().rename("Experiments")
        confidence.index = confidence.index.fillna("Unknown").astype(str)
        st.markdown("**Extraction confidence**")
        st.bar_chart(confidence, height=240)
