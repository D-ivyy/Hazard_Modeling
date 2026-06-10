# Hazard_modeling

**Hazard Risk Modeling** for InfraSure's risk platform — modeling catastrophic natural-hazard
events (hurricane, hail, wildfire, flood, …) and the resulting **asset damage and losses**.
Produces asset-level **loss distributions** that feed the platform's overall **Total Loss** picture.

> **Tier 2 of 3** — Performance Modeling (normal ops · [`model-gpr`](model-gpr)) ·
> **Hazard Risk Modeling** _(this repo)_ · Overall Risk Modeling (Total Loss).

> **Notebooks-first build under way** — *hail × solar* runs end-to-end (M0→M4: catalog → coupling →
> damage → loss & metrics). Hazard **1 of 3** (hail ✅ · wildfire · wind), then a production architecture.
> Start at [`Notebooks/README.md`](Notebooks/README.md).

## Layout

```
Notebooks/               # worked pipelines, organized  peril → asset
  hail/                  #   shared catalog: M0 (data) + M1 (events + frequency)
    solar/               #   hail × solar — M2 coupling · M3 damage · M4 loss & metrics  ✅
docs/
  plans/                 # per-phase plans, decisions (DD-*), assumptions register
  principles/            # why we build this way
  learning_logs/         # what building taught us (not in the refs)
  google_drive_docs/     # local copies of the team's shared Drive reference set (+ links)
  extra/                 # scope/story + per-session task-history handoffs
data/                    # pipeline outputs (large parquets gitignored; manifests/summaries kept)
scripts/                 # one-off / utility scripts (e.g. the MRMS record scan)
.github/workflows/       # CI (GitHub Actions)
AGENTS.md / CLAUDE.md    # contributor + agent guidance (single source = AGENTS.md)
```

Plus local-only, **gitignored** cross-project symlinks: `model-gpr/`, `hazard_analysis/`,
`infrasure-hazard-competitive-research/`, `infrasure-damage-curves/`, `Learning/`.

## Getting started

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter lab            # notebooks live in Notebooks/
```

## References

- **Shared Google Drive — "InfraSure Hazard":** file index + folder links in
  [`docs/google_drive_docs/README.md`](docs/google_drive_docs/README.md).
- **Contributor / agent guidance:** [`AGENTS.md`](AGENTS.md).

## Status

Hazard **1 of 3** — *hail × solar* built end-to-end (M0→M4, real but record-limited numbers,
math-validated). Next: wildfire, then wind (notebooks-first), *then* a production folder architecture.
Start at [`Notebooks/README.md`](Notebooks/README.md).
