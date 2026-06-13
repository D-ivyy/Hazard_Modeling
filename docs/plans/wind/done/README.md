# done/ — completed wind layer write-ups

Completion records for built layers (the wind analogue of [`../../wildfire/done/`](../../wildfire/done/README.md)
and [`../../hail/done/`](../../hail/done/README.md)). Each is a short "what shipped + outcomes + pointers" record,
written when a layer is finished — distinct from the forward-looking plan docs (`../m0_input_data.md`, etc.).

Wind is **Hazard 3 of 3** (hail ✅ · wildfire ✅ · wind), built as a **sub-peril family** — strong / straight-line
wind first (site-conditioned, ASCE pre-integrated surface), tornado second (areal hit-or-miss, path-aware
Minkowski); hurricane (field-intensity) deferred. Records fork per sub-peril **only at M2** (where the coupling
differs); layer-0 / M0 / M1 and **M3 / M4 are shared** (one turbine curve; M4 combines both sub-perils into one
annual-loss distribution per site).

| Layer | Record | Status |
|---|---|---|
| layer-0 — hazard definition | `layer-0-hazard-definition.md` | planned ([plan](../00_hazard_definition.md)) |
| M0 — input data | `m0-input-data.md` | planned ([plan](../m0_input_data.md)) |
| M1 — catalog | `m1-catalog.md` | planned ([plan](../m1_catalog.md)) |
| M2 — strong-wind coupling | `strong-wind-m2-coupling.md` | planned ([plan](../m2_coupling.md)) |
| M2 — tornado coupling | `tornado-m2-coupling.md` | planned ([plan](../m2_coupling.md)) |
| M3 — wind-farm damage (shared) | `m3-damage.md` | planned ([plan](../m3_damage.md)) |
| M4 — wind-farm loss & metrics (shared, combined) | `m4-loss-metrics.md` | planned ([plan](../m4_loss_metrics.md)) |

*(No rows are ✅ yet — wind is at the planning stage. Each row flips to `✅ built (YYYY-MM-DD)` with an italic
outcome tag, mirroring wildfire's done table, as each notebook layer ships.)*
