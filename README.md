# Proportione Visio

[![Apache 2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/streamlit-1.40+-FF4B4B.svg)](https://streamlit.io)
[![Status](https://img.shields.io/badge/status-research%20artifact-orange.svg)](#status)

A multi-tenant Business Intelligence artifact that puts SME business KPIs and digital signals on the same view, quantifies their relationship, and surfaces prioritised recommendations through an optional LLM-mediated fusion layer.

This repository accompanies the paper *From systematic review to operational artifact: an LLM-mediated BI platform translating digital signals into business outcomes for SMEs* (CAPSI 2026, in submission), and is the public, reproducible counterpart of the production deployment running at `visio.proportione.com`.

## What you can do here

- **Run the demo locally with synthetic data**, no Google Cloud credentials needed.
- **Read the architecture** of a production multi-tenant BI artifact: see [ARQUITECTURA.md](ARQUITECTURA.md).
- **Cite the artifact** in your own work: see [CITATION.cff](CITATION.cff).
- **Adapt one of the connectors** to a different SaaS source by following the contract in `visio/connectors/`.

## Quick start (synthetic, ~2 min)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run visio/app.py
```

The demo opens in your browser, lists three synthetic tenants, and renders the methodological page template (`visio/pages/tenant_template.py`) for any of them. No external API is contacted.

## Quick start (real Google data, ~30 min one-off setup)

1. Install the cloud extras: `pip install -r requirements-cloud.txt`.
2. Provide credentials (one of):
    - `GOOGLE_APPLICATION_CREDENTIALS` pointing at a service-account JSON, or
    - `gcloud auth application-default login` if you prefer ADC.
3. Edit `visio/tenants/tenants.example.toml` to declare your real GA4 property ID, Search Console site, Ads customer ID, and BigQuery dataset.
4. `streamlit run visio/app.py` again.

The same pages now read live data instead of synthetic series. The L3 LLM layer remains a stub; bring your own model by replacing `visio/llm/stub.py`.

## Repository layout

```
visio-public/
├── ARQUITECTURA.md                  Architecture, OSS shares, replicability table
├── CITATION.cff                     Cite the artifact / paper
├── LICENSE                          Apache-2.0
├── README.md                        This file
├── requirements.txt                 Demo dependencies (synthetic only)
├── requirements-cloud.txt           Optional Google Cloud connectors
└── visio/
    ├── app.py                       Streamlit entry point
    ├── auth.py                      Email-based tenant routing (no secrets)
    ├── widgets/                     Reusable, sector-agnostic widgets
    │   ├── ga4.py
    │   ├── search_console.py
    │   ├── google_ads.py
    │   ├── finops.py
    │   └── kpi_card.py
    ├── connectors/                  Source readers (each one swappable)
    │   ├── ga4.py
    │   ├── search_console.py
    │   ├── google_ads.py
    │   └── bigquery.py
    ├── llm/
    │   └── stub.py                  Deterministic L3 stub
    ├── synthetic/
    │   └── generator.py             Realistic, non-attributable mock series
    ├── tenants/
    │   └── tenants.example.toml     Tenant declaration shape
    └── pages/
        └── tenant_template.py       The single sanitised page template
```

The production deployment uses the same `visio/widgets/` and `visio/connectors/` packages, and adds one private page per tenant. Tenant pages and the Core API are not part of this public release.

## Status

Research artifact. The CAPSI 2026 paper introduces the artifact methodologically; this repository is the reference implementation cited in the paper. The research line continues with empirical case studies on Iberian SMEs.

The 20-60-20 collaboration framework that organises the artifact's human-AI split has prior validations in two adjacent domains; see the paper and [ARQUITECTURA.md](ARQUITECTURA.md) §"The 20-60-20 collaboration model" for the cite chain.

## Responsible AI

The artifact is classified as **limited risk** under the EU AI Act (Reg. UE 2024/1689). Its design follows the seven principles of the EU AI HLEG (2019), the controls of ISO/IEC 42001:2023 are scoped as the management framework, and every recommendation produced by the LLM layer is logged with the assembled prompt, the model identifier, and the operator who acted on it. See [ARQUITECTURA.md](ARQUITECTURA.md) for the mapping.

## Contributing

Issue reports, replication studies, and connector contributions are welcome. The artifact is research code: it values clarity over generality, and connector implementations are deliberately minimal so that a reviewer can audit each one in a single sitting.

## Acknowledgements

This work is part of the doctoral research of Javier Cuervo López at the Department of Economics, Management, Industrial Engineering and Tourism (DEGEIT), Universidade de Aveiro, under the Doctoral Programme in Business and Innovation (DBI). The artifact is operated by Proportione, LDA and the public release is published under the Proportione GitHub organisation.

## Citation

If you use this artifact in academic work, please cite:

```bibtex
@inproceedings{cuervo2026visio,
    author    = {Cuervo López, Javier},
    title     = {{From systematic review to operational artifact: an LLM-mediated BI platform translating digital signals into business outcomes for SMEs}},
    booktitle = {{Proceedings of the 26th Conference of the Portuguese Association for Information Systems (CAPSI 2026)}},
    year      = {2026},
    address   = {Coimbra, Portugal},
    note      = {In submission}
}
```

For non-academic uses, please reference the artifact as `Proportione Visio` and link this repository.

## License

Apache License 2.0. See [LICENSE](LICENSE).
