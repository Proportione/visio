"""Single tenant page template.

Production has one private page per tenant; this template is the methodological
shape they all share. A reviewer can read this file to understand the layout
convention, then look at any production tenant page (private) and recognise
the same structure.
"""

from __future__ import annotations

import streamlit as st

from .. import connectors, llm
from ..synthetic import TENANT_PROFILES
from ..widgets import (
    render_finops_panel,
    render_ga4_panel,
    render_google_ads_panel,
    render_kpi_card,
    render_search_console_panel,
)


def render(*, tenant_id: str, days: int = 90) -> None:
    tenant = TENANT_PROFILES[tenant_id]

    st.title(tenant.display_name)
    st.caption(f"Sector: {tenant.sector} · window: {days} days")

    ga4 = connectors.ga4.read(tenant_id, days=days)
    sc = connectors.search_console.read(tenant_id, days=days)
    ads = connectors.google_ads.read(tenant_id, days=days)
    finops = connectors.bigquery.read_finops(tenant_id, days=days)
    kpi = connectors.bigquery.read_kpi(tenant_id, days=days)

    cols = st.columns([1, 2])
    with cols[0]:
        render_kpi_card(kpi)
    with cols[1]:
        rec = llm.fuse(
            signals={
                "ga4_conversions": ga4[["conversions"]],
                "sc_clicks": sc[["clicks"]],
                "ads_cost": ads.groupby("date", as_index=False)["cost_eur"].sum()[["cost_eur"]],
            },
            kpi_series=kpi,
        )
        st.subheader("Recommendation")
        st.info(rec.headline)
        st.markdown(rec.narrative)

    st.divider()

    tab_ga4, tab_sc, tab_ads, tab_finops = st.tabs(["GA4", "Search Console", "Google Ads", "FinOps"])
    with tab_ga4:
        render_ga4_panel(ga4)
    with tab_sc:
        render_search_console_panel(sc)
    with tab_ads:
        render_google_ads_panel(ads)
    with tab_finops:
        render_finops_panel(finops)

    with st.expander("Audit log (this view)"):
        st.json({"recommendation_audit": rec.audit, "tenant_id": tenant_id, "window_days": days})
