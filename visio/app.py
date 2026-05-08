"""Streamlit entry point for the Visio public demo.

Run with::

    streamlit run visio/app.py
"""

from __future__ import annotations

import streamlit as st

from .auth import current_user
from .synthetic import TENANT_PROFILES
from .pages import tenant_template


def main() -> None:
    st.set_page_config(page_title="Proportione Visio (public demo)", layout="wide", page_icon="📊")

    user = current_user()
    st.sidebar.title("Proportione Visio")
    st.sidebar.caption("Public demo · synthetic data")
    st.sidebar.write(f"Signed in as **{user.display_name}**")
    st.sidebar.caption(f"{user.email}")

    options = [(tid, TENANT_PROFILES[tid].display_name) for tid in user.allowed_tenants if tid in TENANT_PROFILES]
    if not options:
        st.error("This user has no tenants configured.")
        return

    labels = [name for _, name in options]
    choice = st.sidebar.radio("Tenant", labels, index=0)
    tenant_id = options[labels.index(choice)][0]
    days = st.sidebar.slider("Window (days)", min_value=14, max_value=180, value=90, step=14)

    tenant_template.render(tenant_id=tenant_id, days=days)

    with st.sidebar.expander("About this demo"):
        st.markdown(
            "All data is synthetic. See `ARQUITECTURA.md` for the contract that "
            "production satisfies and the swap path to self-hosted components."
        )


if __name__ == "__main__":
    main()
