"""Deterministic L3 stub for the public demo.

Production replaces ``fuse`` with a real LLM call (Vertex / Anthropic / OSS).
The stub computes a simple correlation-and-lag analysis so the demo's
narratives are honest about the underlying numbers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Recommendation:
    """Structured recommendation returned by the L3 layer."""

    headline: str
    narrative: str
    drivers: list[tuple[str, float, int]] = field(default_factory=list)
    """List of ``(signal_name, correlation, optimal_lag_days)`` tuples sorted by abs correlation."""

    audit: dict = field(default_factory=dict)


def _aligned(signal: pd.Series, kpi: pd.Series, max_lag: int = 14) -> tuple[float, int]:
    """Best Pearson correlation between signal and kpi over lags 0..max_lag.

    Returns ``(correlation, lag)``. Positive lag means the signal precedes the KPI.
    """
    s = signal.to_numpy(dtype=float)
    k = kpi.to_numpy(dtype=float)
    if len(s) != len(k):
        n = min(len(s), len(k))
        s, k = s[-n:], k[-n:]
    best_corr, best_lag = 0.0, 0
    for lag in range(0, max_lag + 1):
        if lag == 0:
            a, b = s, k
        else:
            a, b = s[:-lag], k[lag:]
        if len(a) < 10:
            continue
        if np.std(a) == 0 or np.std(b) == 0:
            continue
        r = float(np.corrcoef(a, b)[0, 1])
        if abs(r) > abs(best_corr):
            best_corr, best_lag = r, lag
    return best_corr, best_lag


def fuse(signals: Mapping[str, pd.DataFrame], kpi_series: pd.DataFrame) -> Recommendation:
    """Combine normalised signals with the focal KPI series.

    Parameters
    ----------
    signals
        Mapping of signal name to a DataFrame whose first numeric column is treated
        as the daily value. Conventional names: ``"ga4_conversions"``, ``"sc_clicks"``,
        ``"ads_cost"``.
    kpi_series
        DataFrame with columns ``date``, ``kpi_name``, ``kpi_value``.
    """
    drivers: list[tuple[str, float, int]] = []
    if kpi_series.empty or not signals:
        return Recommendation(
            headline="No data",
            narrative="Insufficient data to compute drivers.",
            drivers=[],
            audit={"signals_seen": list(signals.keys())},
        )

    kpi = kpi_series["kpi_value"].astype(float).reset_index(drop=True)

    for name, df in signals.items():
        numeric_cols = df.select_dtypes(include="number").columns
        if len(numeric_cols) == 0:
            continue
        series = df[numeric_cols[0]].astype(float).reset_index(drop=True)
        if len(series) < 30:
            continue
        corr, lag = _aligned(series, kpi)
        drivers.append((name, round(corr, 3), lag))

    drivers.sort(key=lambda x: abs(x[1]), reverse=True)
    top = drivers[:3]

    if not top:
        return Recommendation(
            headline="No drivers detected",
            narrative="Signals did not show a stable lead/lag relationship with the focal KPI in this window.",
            drivers=[],
            audit={"signals_seen": list(signals.keys())},
        )

    headline_driver, headline_corr, headline_lag = top[0]
    sign = "positive" if headline_corr > 0 else "negative"
    headline = f"{headline_driver} leads the KPI with {sign} correlation {headline_corr:+.2f} at lag {headline_lag}d"

    bullets = "\n".join(
        f"- **{n}**: corr {c:+.2f}, optimal lag {l} day(s)"
        for n, c, l in top
    )
    narrative = (
        f"Top drivers in the last {len(kpi)} days:\n\n{bullets}\n\n"
        "Operator: review the top driver's investment line and confirm GO/NO-GO. "
        "Decision is logged with the prompt and model id (audit field)."
    )

    return Recommendation(
        headline=headline,
        narrative=narrative,
        drivers=top,
        audit={
            "model": "stub-v0.1-deterministic",
            "signals_seen": list(signals.keys()),
            "kpi_name": str(kpi_series["kpi_name"].iloc[-1]),
            "window_days": int(len(kpi)),
        },
    )
