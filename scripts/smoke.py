#!/usr/bin/env python3
"""Smoke check for the public Visio demo.

Exits 0 if every layer wires correctly with synthetic data, non-zero otherwise.
Useful for CI and for an external reviewer wanting one-command reassurance that the
artifact reproduces.

Usage::

    python scripts/smoke.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from visio import connectors
from visio.llm import fuse
from visio.synthetic import TENANT_PROFILES


def main() -> int:
    failures: list[str] = []

    # 1. Three demo tenants exist with the documented sectors.
    expected_tenants = {"demo_education", "demo_thirdsector", "demo_services"}
    if set(TENANT_PROFILES) != expected_tenants:
        failures.append(f"Tenant set mismatch: {sorted(TENANT_PROFILES)}")

    # 2. Each tenant returns sane data for every connector.
    for tenant_id in TENANT_PROFILES:
        ga4 = connectors.ga4.read(tenant_id, days=90)
        sc = connectors.search_console.read(tenant_id, days=90)
        ads = connectors.google_ads.read(tenant_id, days=90)
        finops = connectors.bigquery.read_finops(tenant_id, days=90)
        kpi = connectors.bigquery.read_kpi(tenant_id, days=90)

        if len(ga4) != 90 or set(ga4.columns) != {"date", "sessions", "users", "conversions"}:
            failures.append(f"{tenant_id}: GA4 shape unexpected")
        if len(sc) != 90:
            failures.append(f"{tenant_id}: SC length unexpected")
        if ads.empty or "campaign" not in ads.columns:
            failures.append(f"{tenant_id}: Ads shape unexpected")
        if finops.empty or "service" not in finops.columns:
            failures.append(f"{tenant_id}: FinOps shape unexpected")
        if len(kpi) != 90 or "kpi_value" not in kpi.columns:
            failures.append(f"{tenant_id}: KPI shape unexpected")

        # 3. The deterministic LLM stub finds the lag-3 correlation we inject in
        # the synthetic generator. If this assertion ever fails, the synthetic
        # pipeline is no longer consistent with the stub contract.
        rec = fuse(
            signals={
                "ga4_conversions": ga4[["conversions"]],
                "sc_clicks": sc[["clicks"]],
                "ads_cost": ads.groupby("date", as_index=False)["cost_eur"].sum()[["cost_eur"]],
            },
            kpi_series=kpi,
        )
        if not rec.drivers:
            failures.append(f"{tenant_id}: LLM stub returned no drivers")
            continue
        top_name, top_corr, top_lag = rec.drivers[0]
        if top_name != "ga4_conversions":
            failures.append(f"{tenant_id}: top driver should be ga4_conversions, got {top_name}")
        if abs(top_corr) < 0.7:
            failures.append(f"{tenant_id}: top corr too weak: {top_corr}")
        if not (1 <= top_lag <= 5):
            failures.append(f"{tenant_id}: top lag outside expected 1-5d window: {top_lag}")

    if failures:
        print("SMOKE FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("SMOKE OK — 3 tenants, 5 connectors, LLM stub recovers lag-3 correlation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
