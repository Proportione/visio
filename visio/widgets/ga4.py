"""GA4 panel — sessions, users and conversions over the window."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render_ga4_panel(df: pd.DataFrame) -> None:
    """Render the GA4 trio in one chart.

    Expected schema: columns ``date``, ``sessions``, ``users``, ``conversions``.
    """
    if df.empty:
        st.info("No GA4 data for this window.")
        return

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df["sessions"], name="Sessions", mode="lines"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["users"], name="Users", mode="lines"))
    fig.add_trace(go.Bar(x=df["date"], y=df["conversions"], name="Conversions", yaxis="y2", opacity=0.4))
    fig.update_layout(
        height=320,
        margin=dict(l=0, r=0, t=20, b=0),
        yaxis=dict(title="Sessions / Users"),
        yaxis2=dict(title="Conversions", overlaying="y", side="right"),
        legend=dict(orientation="h", y=-0.2),
    )
    st.plotly_chart(fig, use_container_width=True)

    cols = st.columns(3)
    cols[0].metric("Sessions", f"{int(df['sessions'].sum()):,}")
    cols[1].metric("Users", f"{int(df['users'].sum()):,}")
    cols[2].metric("Conversions", f"{int(df['conversions'].sum()):,}")
