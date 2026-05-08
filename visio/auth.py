"""Authentication shim for the public demo.

The production system uses Google OAuth + email allow-list + BigQuery row-level
filters. None of those are appropriate for a public reproducible release, so this
module provides a deliberately simple shim:

- The demo runs without authentication.
- A reviewer can override ``current_user`` to test multi-tenant routing.

The architecture document describes the gap between this shim and the production
auth model so that no reader confuses the two.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    email: str
    display_name: str
    allowed_tenants: tuple[str, ...]


def current_user() -> User:
    """Return the current user.

    Public demo default: anonymous user with access to all synthetic tenants.
    Override via the ``VISIO_DEMO_USER`` env var (format ``email|name|tenant_a,tenant_b``).
    """
    raw = os.environ.get("VISIO_DEMO_USER")
    if raw:
        try:
            email, name, tenants = raw.split("|", 2)
            return User(email=email.strip(), display_name=name.strip(), allowed_tenants=tuple(t.strip() for t in tenants.split(",") if t.strip()))
        except ValueError:
            pass
    return User(
        email="anonymous@example.com",
        display_name="Anonymous reviewer",
        allowed_tenants=("demo_education", "demo_thirdsector", "demo_services"),
    )


def can_access(user: User, tenant_id: str) -> bool:
    return tenant_id in user.allowed_tenants
