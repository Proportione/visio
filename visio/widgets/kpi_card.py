"""KPI card — focal business outcome with delta vs prior period."""

import pandas as pd
import streamlit as st


def render_kpi_card(kpi_series: pd.DataFrame, *, label: str | None = None) -> None:
    """Render the focal KPI as a Streamlit metric.

    Expected schema: columns ``date``, ``kpi_name``, ``kpi_value``.
    """
    if kpi_series.empty:
        st.info("No KPI data for this window.")
        return

    half = len(kpi_series) // 2
    prior, current = kpi_series.iloc[:half], kpi_series.iloc[half:]
    current_total = float(current["kpi_value"].sum())
    prior_total = float(prior["kpi_value"].sum())
    delta_pct = ((current_total - prior_total) / prior_total * 100.0) if prior_total else None

    name = label or kpi_series["kpi_name"].iloc[-1]
    st.metric(
        label=name,
        value=f"{current_total:,.0f}",
        delta=(f"{delta_pct:+.1f}% vs prior {len(prior)} days" if delta_pct is not None else None),
    )
