"""BigQuery connector for FinOps + KPI series — synthetic by default."""

from __future__ import annotations

import os
import pandas as pd

from ..synthetic import TENANT_PROFILES, generate_finops, generate_kpi_series


def read_finops(tenant_id: str, days: int = 90) -> pd.DataFrame:
    if os.environ.get("VISIO_REAL_BQ") == "1":
        raise NotImplementedError(
            "Real BigQuery mode is not part of the public release."
        )
    tenant = TENANT_PROFILES.get(tenant_id)
    if tenant is None:
        raise KeyError(f"Unknown tenant_id: {tenant_id!r}")
    return generate_finops(tenant, days=days)


def read_kpi(tenant_id: str, days: int = 90) -> pd.DataFrame:
    if os.environ.get("VISIO_REAL_BQ") == "1":
        raise NotImplementedError(
            "Real BigQuery mode is not part of the public release."
        )
    tenant = TENANT_PROFILES.get(tenant_id)
    if tenant is None:
        raise KeyError(f"Unknown tenant_id: {tenant_id!r}")
    return generate_kpi_series(tenant, days=days)
