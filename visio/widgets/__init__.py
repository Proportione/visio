"""Reusable, sector-agnostic widgets.

Each widget takes a normalised pandas DataFrame and renders a Streamlit block.
Widgets do not know how the data was produced (real Google API or synthetic),
which is why the same code path serves the public demo and the production
deployment.
"""

from .kpi_card import render_kpi_card
from .ga4 import render_ga4_panel
from .search_console import render_search_console_panel
from .google_ads import render_google_ads_panel
from .finops import render_finops_panel

__all__ = [
    "render_kpi_card",
    "render_ga4_panel",
    "render_search_console_panel",
    "render_google_ads_panel",
    "render_finops_panel",
]
