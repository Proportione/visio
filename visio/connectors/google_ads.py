"""Google Ads connector — synthetic by default."""

from __future__ import annotations

import os
import pandas as pd

from ..synthetic import TENANT_PROFILES, generate_google_ads


def read(tenant_id: str, days: int = 90) -> pd.DataFrame:
    if os.environ.get("VISIO_REAL_ADS") == "1":
        raise NotImplementedError(
            "Real Google Ads mode is not part of the public release."
        )
    tenant = TENANT_PROFILES.get(tenant_id)
    if tenant is None:
        raise KeyError(f"Unknown tenant_id: {tenant_id!r}")
    return generate_google_ads(tenant, days=days)
