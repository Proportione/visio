"""GA4 connector.

Public demo: routes to ``visio.synthetic.generate_ga4``.
Production: replace ``read`` with a Google Analytics Data API call returning
the same DataFrame schema.
"""

from __future__ import annotations

import os
import pandas as pd

from ..synthetic import TENANT_PROFILES, generate_ga4


def read(tenant_id: str, days: int = 90) -> pd.DataFrame:
    """Return daily GA4 sessions / users / conversions for ``tenant_id``."""
    if os.environ.get("VISIO_REAL_GA4") == "1":
        # Production hook — implementers replace this branch with a real
        # google-analytics-data client call. Kept as a stub to keep the
        # public release credential-free.
        raise NotImplementedError(
            "Real GA4 mode is not part of the public release. "
            "Provide your own client by overriding visio.connectors.ga4.read."
        )

    tenant = TENANT_PROFILES.get(tenant_id)
    if tenant is None:
        raise KeyError(f"Unknown tenant_id: {tenant_id!r}")
    return generate_ga4(tenant, days=days)
