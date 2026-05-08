"""Synthetic series generator for the public demo."""

from .generator import (
    generate_ga4,
    generate_search_console,
    generate_google_ads,
    generate_finops,
    generate_kpi_series,
    Tenant,
    TENANT_PROFILES,
)

__all__ = [
    "generate_ga4",
    "generate_search_console",
    "generate_google_ads",
    "generate_finops",
    "generate_kpi_series",
    "Tenant",
    "TENANT_PROFILES",
]
