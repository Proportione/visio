"""Realistic, non-attributable synthetic series for the Visio demo.

The aim is to produce DataFrames with the *shape* of real signal/KPI data —
weekly seasonality, slow trends, plausible noise, occasional outliers — without
any value tied to a real Proportione tenant.

Parameters are drawn from documented public ranges (e.g. "B2B SaaS conversion
rate typically 1–3%"), so a reviewer running the demo sees realistic dashboards
while a reader trying to identify a real customer cannot.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
import hashlib

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Tenant:
    """Synthetic tenant declaration."""

    tenant_id: str
    display_name: str
    sector: str  # "online_education" | "third_sector" | "professional_services"
    seed: int

    @property
    def rng(self) -> np.random.Generator:
        return np.random.default_rng(self.seed)


# Three demo tenants spanning different KPI families. Sector strings are the
# same coarse families used by the connectors so the demo flows end-to-end.
TENANT_PROFILES: dict[str, Tenant] = {
    "demo_education": Tenant(
        tenant_id="demo_education",
        display_name="Demo · online education provider",
        sector="online_education",
        seed=11,
    ),
    "demo_thirdsector": Tenant(
        tenant_id="demo_thirdsector",
        display_name="Demo · third-sector NGO",
        sector="third_sector",
        seed=37,
    ),
    "demo_services": Tenant(
        tenant_id="demo_services",
        display_name="Demo · professional services SME",
        sector="professional_services",
        seed=53,
    ),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _date_range(days: int) -> pd.DatetimeIndex:
    end = pd.Timestamp(date.today())
    return pd.date_range(end=end, periods=days, freq="D")


def _seasonal_curve(index: pd.DatetimeIndex, weekly_amp: float, yearly_amp: float = 0.0) -> np.ndarray:
    """Combined weekly + (optional) yearly seasonal multiplier centred on 1.0."""
    days = (index - index[0]).days.to_numpy()
    weekly = weekly_amp * np.cos(2 * np.pi * days / 7)
    yearly = yearly_amp * np.cos(2 * np.pi * days / 365.25) if yearly_amp else 0.0
    return 1.0 + weekly + yearly


def _trend(index: pd.DatetimeIndex, slope_per_year: float) -> np.ndarray:
    """Linear trend expressed as fractional growth per year."""
    days = (index - index[0]).days.to_numpy()
    return 1.0 + (slope_per_year * days / 365.25)


def _stable_noise(seed_input: str, size: int, scale: float) -> np.ndarray:
    """Deterministic per-series noise so two runs produce identical outputs."""
    seed = int(hashlib.sha1(seed_input.encode("utf-8")).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)
    return rng.normal(loc=0.0, scale=scale, size=size)


# ---------------------------------------------------------------------------
# Signal generators (L1 Ingest equivalents)
# ---------------------------------------------------------------------------

def generate_ga4(tenant: Tenant, days: int = 90) -> pd.DataFrame:
    """Daily GA4-shaped sessions / users / conversions for a tenant."""
    index = _date_range(days)
    base_sessions = {
        "online_education": 800,
        "third_sector": 350,
        "professional_services": 180,
    }[tenant.sector]

    seasonal = _seasonal_curve(index, weekly_amp=0.18, yearly_amp=0.05)
    trend = _trend(index, slope_per_year=0.20)
    sessions = base_sessions * seasonal * trend
    sessions *= 1.0 + _stable_noise(f"{tenant.tenant_id}-ga4-sessions", days, 0.08)
    sessions = np.clip(sessions, a_min=10, a_max=None)

    users = sessions * 0.78  # public industry ratio
    conversion_rate = {
        "online_education": 0.012,
        "third_sector": 0.008,
        "professional_services": 0.022,
    }[tenant.sector]
    conversions = sessions * conversion_rate * (1.0 + _stable_noise(f"{tenant.tenant_id}-ga4-conv", days, 0.15))
    conversions = np.clip(np.round(conversions), 0, None)

    return pd.DataFrame({
        "date": index.date,
        "sessions": np.round(sessions).astype(int),
        "users": np.round(users).astype(int),
        "conversions": conversions.astype(int),
    })


def generate_search_console(tenant: Tenant, days: int = 90) -> pd.DataFrame:
    """Daily Search Console-shaped clicks / impressions / position."""
    index = _date_range(days)
    base_impressions = {
        "online_education": 5200,
        "third_sector": 2100,
        "professional_services": 950,
    }[tenant.sector]

    seasonal = _seasonal_curve(index, weekly_amp=0.06)  # SC is less weekly-cyclical
    trend = _trend(index, slope_per_year=0.30)
    impressions = base_impressions * seasonal * trend
    impressions *= 1.0 + _stable_noise(f"{tenant.tenant_id}-sc-impressions", days, 0.10)
    impressions = np.clip(impressions, 50, None)

    ctr = 0.04 + 0.01 * np.sin(np.linspace(0, 4 * np.pi, days))
    clicks = impressions * ctr
    position = 12.0 + 4.0 * np.cos(np.linspace(0, 6 * np.pi, days))

    return pd.DataFrame({
        "date": index.date,
        "impressions": np.round(impressions).astype(int),
        "clicks": np.round(clicks).astype(int),
        "ctr": np.round(ctr, 4),
        "position": np.round(position, 2),
    })


def generate_google_ads(tenant: Tenant, days: int = 90) -> pd.DataFrame:
    """Daily Ads-shaped cost / clicks / conversions per campaign."""
    index = _date_range(days)
    campaigns = {
        "online_education": ["brand", "courses_pt", "courses_es", "remarketing"],
        "third_sector": ["donaciones_brand", "voluntariado", "campañas_eventos"],
        "professional_services": ["brand", "leads_pt", "leads_es"],
    }[tenant.sector]

    rows = []
    for campaign in campaigns:
        rng = np.random.default_rng(hash((tenant.seed, campaign)) % (2**31))
        base_cost = rng.uniform(20, 120)
        cpc = rng.uniform(0.40, 1.80)
        seasonal = _seasonal_curve(index, weekly_amp=0.12)
        cost = base_cost * seasonal * (1.0 + rng.normal(0, 0.18, days))
        cost = np.clip(cost, 1.0, None)
        clicks = cost / cpc
        conv_rate = rng.uniform(0.008, 0.04)
        conversions = clicks * conv_rate

        rows.append(pd.DataFrame({
            "date": index.date,
            "campaign": campaign,
            "cost_eur": np.round(cost, 2),
            "clicks": np.round(clicks).astype(int),
            "conversions": np.round(conversions, 1),
        }))

    return pd.concat(rows, ignore_index=True)


def generate_finops(tenant: Tenant, days: int = 90) -> pd.DataFrame:
    """Daily cloud cost by service — GCP-shaped."""
    index = _date_range(days)
    services = ["bigquery", "cloud_run", "cloud_storage", "vertex_ai", "logging"]
    rows = []
    for service in services:
        rng = np.random.default_rng(hash((tenant.seed, service)) % (2**31))
        base = rng.uniform(0.5, 12.0)
        cost = base + rng.normal(0, 0.2, days)
        cost = np.clip(cost, 0.05, None)
        rows.append(pd.DataFrame({
            "date": index.date,
            "service": service,
            "cost_eur": np.round(cost, 2),
        }))
    return pd.concat(rows, ignore_index=True)


# ---------------------------------------------------------------------------
# KPI generator (L2 Normalise equivalent of the business outcome series)
# ---------------------------------------------------------------------------

def generate_kpi_series(tenant: Tenant, days: int = 90) -> pd.DataFrame:
    """Daily focal KPI for the tenant.

    The KPI is correlated with GA4 conversions with a small lag and a low signal-to-noise
    ratio, so the demo can illustrate the artifact's lag-detection feature.
    """
    ga4 = generate_ga4(tenant, days=days)
    base = ga4["conversions"].astype(float).to_numpy()
    lagged = np.roll(base, shift=3)
    lagged[:3] = base[:3]

    rng = np.random.default_rng(tenant.seed + 7)
    kpi_unit = {
        "online_education": "matriculas_DECA",
        "third_sector": "donaciones_eur",
        "professional_services": "leads_cualificados",
    }[tenant.sector]

    if kpi_unit == "donaciones_eur":
        scale = 25.0
    elif kpi_unit == "matriculas_DECA":
        scale = 0.6
    else:
        scale = 1.4

    kpi = lagged * scale + rng.normal(0, scale * 0.4, days)
    kpi = np.clip(kpi, 0, None)

    return pd.DataFrame({
        "date": ga4["date"],
        "kpi_name": kpi_unit,
        "kpi_value": np.round(kpi, 2),
    })
