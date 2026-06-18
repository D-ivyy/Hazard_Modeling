# Task context — convective-wind M0→M4 build + wind_farm asset cell (2026-06-17)

## Objective
Turn the 2026-06-13 *wind route-zero plan* into a working notebooks-first pipeline (M0→M4) for the convective-wind
peril, then conform it to the house `peril → asset` architecture and push it. Hazard **3 of 3**.

## Background
- The 2026-06-13 session settled the plan (layer-0 hazard definition + DD-WN-1..15 + M0–M4 plan docs + coupling
  discussion) — see [`../2026-06-13__wind__route-zero-planning/handoff.md`](../2026-06-13__wind__route-zero-planning/handoff.md).
- Hail × solar and wildfire × solar were already built end-to-end (the precedent for structure + the shared MC engine).
- **Governance rule (held throughout):** the Drive reference docs (`docs/google_drive_docs/`) are the primary source
  of truth for hazard taxonomy/methodology; any deviation = discuss → update the Drive doc first → then build. The
  taxonomy (convective wind = tornado + strong wind; hurricane separate) was conformed to the Drive set, not invented.

## Problems encountered & fixed
- **Folder name** `wind/` conflated the *peril* with the broader "wind" — renamed to `convective_wind/`.
- **Missing asset cell** — hail/wildfire use `peril/asset/` (e.g. `hail/solar/`); wind had M2–M4 at the peril level.
  Fixed: created `wind_farm/` and moved M2/M3/M4 under it.
- **M2 fork placement** — settled as a *folder*-fork **under** `m2_coupling/` (`tornado/`, `strong_wind/`), inside
  the asset cell; M3/M4 stay shared.
- **M3 under-modeled the sub-peril difference** — the first cut varied only *reach* (same onset/steepness). Corrected
  to two genuinely-different curves (tornado more severe at the same gust — the loading mechanism differs).
- **VaR aggregation direction** — an earlier prose claim said summing per-sub-peril VaRs *overstates* the joint; the
  300k-yr MC shows it *understates* (~26%; VaR super-additive for zero-inflated NegBin tails). Fixed in the M4
  notebook, discussion/04, and AWN-29.
- **Link integrity** — the restructure shifted every moved notebook one level deeper (+1 `../`). Fixed via a
  link-checker run iteratively to **0 broken** across 43 `.py`/`.md`/`.ipynb`.

## What we built / changed
- `convective_wind/wind_farm/` asset cell: `m2_coupling/{tornado,strong_wind}/`, `m3_damage/`, `m4_loss_metrics/` (+
  a `wind_farm/README.md` asset-cell overview).
- **M3 rewrite** — one turbine (shared capex split / IEC anchor), **two sub-peril fragility curves** (`dr_tornado`,
  `dr_strongwind`); 10 known-answer checks (incl. *tornado ≥ strong wind at every gust*, *tornado onset < strong-wind
  onset*).
- **M4 rewrite** — each sub-peril sampled through its own curve into one joint distribution; metrics off the joint.
- Registers: **DD-WN-16** (two-curve M3), **AWN-32** (sub-peril severity differs), AWN-29 corrected; m3 plan +
  done/README + Notebooks/README (tree + peril×asset matrix, incl. the straight-line-wind = *site-conditioned* fix) +
  AGENTS.md status (3 of 3).

## Files touched (committed `e445b42`)
- `Notebooks/convective_wind/**` (renamed from `wind/`; M1–M4 new; wind_farm restructure)
- `data/convective_wind/**` (JSON manifests; parquets gitignored)
- `docs/plans/convective_wind/**`, `docs/extra/discussion/convective_wind/**`
- `AGENTS.md`, `Notebooks/README.md`

## Status
**COMPLETE + pushed** (`aamani-ai/Hazard_Modeling` @ `e445b42`). All 9 notebooks execute 0 errors; all known-answer
checks pass; 0 broken links. Numbers real but record-limited and approximate (M3 curve is the dominant uncertainty).

## Next steps
Production folder architecture (the gate after all three first cells) · `infrasure-damage-curves` calibrated M3 ·
strong-wind disruption track (AWN-31) · hurricane peril (AWN-30) · portfolio correlation (AWN-22). See
[`handoff.md`](handoff.md) for the ordered roadmap.
