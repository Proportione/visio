"""FinOps panel — cloud cost by service."""

import pandas as pd
import plotly.express as px
import streamlit as st


def render_finops_panel(df: pd.DataFrame) -> None:
    """Render daily cloud cost broken down by service.

    Expected schema: columns ``date``, ``service``, ``cost_eur``.
    """
    if df.empty:
        st.info("No FinOps data for this window.")
        return

    fig = px.area(df, x="date", y="cost_eur", color="service")
    fig.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.3))
    st.plotly_chart(fig, use_container_width=True)

    by_service = df.groupby("service", as_index=False)["cost_eur"].sum().sort_values("cost_eur", ascending=False)
    by_service["share_%"] = (by_service["cost_eur"] / by_service["cost_eur"].sum() * 100).round(1)
    st.dataframe(by_service, hide_index=True, use_container_width=True)
