"""Google Ads panel — cost / clicks / conversions per campaign."""

import pandas as pd
import plotly.express as px
import streamlit as st


def render_google_ads_panel(df: pd.DataFrame) -> None:
    """Render Ads cost stacked by campaign, with conversions table.

    Expected schema: columns ``date``, ``campaign``, ``cost_eur``, ``clicks``, ``conversions``.
    """
    if df.empty:
        st.info("No Google Ads data for this window.")
        return

    fig = px.bar(df, x="date", y="cost_eur", color="campaign", title=None)
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.3))
    st.plotly_chart(fig, use_container_width=True)

    summary = (
        df.groupby("campaign", as_index=False)
        .agg(cost_eur=("cost_eur", "sum"), clicks=("clicks", "sum"), conversions=("conversions", "sum"))
        .assign(cpc=lambda x: (x["cost_eur"] / x["clicks"]).round(2))
        .sort_values("cost_eur", ascending=False)
    )
    st.dataframe(summary, hide_index=True, use_container_width=True)
