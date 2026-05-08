"""Search Console panel — clicks, impressions, CTR, average position."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render_search_console_panel(df: pd.DataFrame) -> None:
    """Render the Search Console quartet.

    Expected schema: columns ``date``, ``impressions``, ``clicks``, ``ctr``, ``position``.
    """
    if df.empty:
        st.info("No Search Console data for this window.")
        return

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["date"], y=df["impressions"], name="Impressions", opacity=0.4))
    fig.add_trace(go.Scatter(x=df["date"], y=df["clicks"], name="Clicks", mode="lines", yaxis="y2"))
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=20, b=0),
        yaxis=dict(title="Impressions"),
        yaxis2=dict(title="Clicks", overlaying="y", side="right"),
        legend=dict(orientation="h", y=-0.2),
    )
    st.plotly_chart(fig, use_container_width=True)

    cols = st.columns(4)
    cols[0].metric("Impressions", f"{int(df['impressions'].sum()):,}")
    cols[1].metric("Clicks", f"{int(df['clicks'].sum()):,}")
    cols[2].metric("CTR", f"{df['ctr'].mean()*100:.2f}%")
    cols[3].metric("Avg position", f"{df['position'].mean():.1f}")
