"""Source connectors.

Each connector exposes a single ``read(...)`` function returning a normalised
pandas DataFrame in the schema expected by the matching widget. The default
implementations route to the synthetic generator when no real credentials are
configured, so the public demo runs without any GCP access.

Production replaces each connector with a real client (BigQuery, GA4 API,
Search Console API, Google Ads API). The contract is the DataFrame shape, not
the underlying technology.
"""

from . import ga4, search_console, google_ads, bigquery

__all__ = ["ga4", "search_console", "google_ads", "bigquery"]
