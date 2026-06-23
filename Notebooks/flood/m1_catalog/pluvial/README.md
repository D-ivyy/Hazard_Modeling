# M1 — Pluvial `[F]` catalog (the asset-independent rainfall-runoff field)

*The **pluvial branch** of the M1 fork: build the rainfall-runoff **source field** — SCS-CN runoff `Q` by annual
return period — for **every flood site of both assets** in one pass, with **one method everywhere**. Pluvial is
**the blind spot**: no free pluvial *depth* grid exists, so depth is **modeled**, not measured. The per-asset
ponded inundation depth (lidar ponding-fraction `f` / depression depth-cap) is derived in **M2** (JD-FL-19).*

**Where this sits:** [M0 evidence](../../m0_input_data/README.md) → **M1 (catalog — pluvial fork)** → M2 coupling →
M3 damage → M4 loss. Parent: [`m1_catalog/`](../README.md). Sibling forks: [`riverine/`](../riverine/README.md) ·
[`coastal/`](../coastal/README.md). Plan: [`m1_catalog.md`](../../../../docs/plans/flood/m1_catalog.md). Notebook:
[`01_catalog`](01_catalog.ipynb) (built).

## Method — Atlas 14 → SCS-CN, everywhere ([JD-FL-9](../../../../docs/plans/flood/decisions.md))
1. **Frequency** = **NOAA Atlas 14** point precipitation-frequency, **24-hr depth** at each RP (HDSC text service).
2. **Runoff** = **SCS Curve Number** (CN = 80, graded solar / soil-C): `Q = (P − 0.2S)²/(P + 0.8S)`, `S = 1000/CN − 10`.
3. **Field emitted** = the runoff `Q(site, RP)` — the *source term*. **Ponding** (`f`, depth-cap) is **M2's** job.

**Magnitude metric:** pluvial **runoff depth `Q`** (→ ponded inundation **depth, ft above ground** in M2) at return
period. Sites outside Atlas 14 coverage (Pacific NW = NOAA Atlas 2) → pluvial **0** (a low-rainfall control, not a
true zero).

## What `01_catalog` found
- 100-yr runoff `Q`: **Elizabeth ≈ 0.284 m · LA3 ≈ 0.247 m · Green River ≈ 0.113 m · Amazon ≈ 0.180 m.**
- **Shepherds Flat** is outside Atlas 14 (PNW) → pluvial **0** (AFL-W11).
- **Screening-grade** — no depth anchor (vs riverine's BLE), so pluvial depths are inherently softer/wider; the `r`/`f`
  ponding knobs are judgment, surfaced in M2 ([AFL-P2](../../../../docs/plans/flood/assumptions.md)).
- **Known-answer checks pass:** `Q` rises monotonically with return period; dry/uncovered sites read 0.

## Inputs → outputs
NOAA Atlas 14 (24-hr precip-frequency) → one shared **field** manifest
`data/flood/flood_pluvial_m1_catalog_manifest.json` (per-site runoff `Q` at each RP, rows tagged `asset`).
`event_family_id` is **reserved** (unused for pluvial). One method serves both assets; each asset's M2 filters to
its own sites and applies the terrain ponding.

## Decisions & assumptions
[JD-FL-9](../../../../docs/plans/flood/decisions.md) (Atlas 14 → SCS-CN pluvial) ·
[JD-FL-10](../../../../docs/plans/flood/decisions.md) (fork at M1) ·
[JD-FL-19](../../../../docs/plans/flood/decisions.md) (M1 = field, M2 = coupling). Assumptions **AFL-P1/P2** (pluvial
source + the `r`/`f` knobs, no depth anchor) · **AFL-W10/W11** (wind pad-gated ponding; PNW Atlas-2 gap). Register:
[`assumptions.md`](../../../../docs/plans/flood/assumptions.md).

**Next → M2 (coupling):** each asset pours `Q` over its terrain — solar = footprint ponding fraction × depth; wind =
per-node pad-gated ponding (raised pads shed the shallow sheet).
