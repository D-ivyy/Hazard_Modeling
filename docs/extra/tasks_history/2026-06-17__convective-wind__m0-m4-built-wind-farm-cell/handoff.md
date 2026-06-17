# Handoff — convective-wind built M0→M4, `wind_farm` asset cell, two-curve M3 (2026-06-17)

**Read me first.** Hazard **3 of 3** is done: **convective wind × wind farm** is built end-to-end and **pushed**
(`aamani-ai/Hazard_Modeling` @ `e445b42`). This session turned the 2026-06-13 *route-zero plan* into a working
pipeline, then restructured it to the house `peril → asset` shape and upgraded M3.

## 60-second summary
- **Built M1→M4** (layer-0 + M0 were partly done before) for two wind farms: **Traverse Wind Energy Center, OK**
  (proving, high-wind) + **Shepherds Flat, OR** (baseline). Both sub-perils — **tornado [T]** + **strong/straight-line
  wind [W]** — co-sampled into one annual-loss distribution per site.
- **Renamed `wind/` → `convective_wind/`** (the peril is not just "wind"; hurricane is a *separate*, deferred peril).
- **Asset cell**: `convective_wind/wind_farm/` holds M2 (folder-fork → `tornado/` · `strong_wind/`), M3, M4 — mirroring
  `hail/solar/` and `wildfire/solar/`. Peril layers (layer0, m0, m1) stay above it. A sibling `solar/` cell can be
  added later.
- **M3 upgraded to TWO sub-peril curves** ([DD-WN-16](../../../plans/convective_wind/decisions.md) / [AWN-32](../../../plans/convective_wind/assumptions.md)):
  one turbine, but **tornado is more damaging than straight-line wind at the *same* gust** (rotation defeats
  feathering + vertical/pressure/debris loads + EF damage-calibration) → lower onset + steeper + full reach, **not just
  wider reach** (the prior cut only varied reach). Strong wind = aero reach, onset at IEC survival. Both `DR(μ)≈0`.

## Headline numbers (300k-yr MC, % of TIV)
| Site | EAL | PML250 | TVaR99 | driver |
|---|---|---|---|---|
| Traverse (proving) | 0.064% ($0.89M) | **3.99%** | **4.88%** | tornado tail |
| Shepherds Flat (baseline) | 0.006% ($0.07M) | 0.15% | 0.35% | ~none (correctly small) |

Strong-wind EAL ≈ 0.006–0.02% (the **known-answer check** — gusts below IEC survival; its real impact is the deferred
disruption/degradation track, AWN-31). Aggregation: **EAL additive**, tail off the **joint**; summing per-sub-peril
VaRs **understates** the joint by ~26% (VaR super-additive for these zero-inflated NegBin tails — corrected from an
earlier "overstates" claim; the MC caught it).

## Repro
```bash
cd Hazard_modeling && source .venv/bin/activate
base=Notebooks/convective_wind/wind_farm
for f in m2_coupling/tornado/01_coupling m2_coupling/strong_wind/01_coupling m3_damage/01_damage m4_loss_metrics/01_loss_metrics; do
  jupytext --to notebook --execute "$base/$f.py"      # 0 errors; all known-answer checks pass
done
```

## NEXT ACTION roadmap (pick up here)
1. **Production folder architecture** — all three first cells (hail×solar, wildfire×solar, convective-wind×wind-farm)
   are built notebooks-first; the plan-of-record says *then* a production structure. This is the next major move.
2. **`infrasure-damage-curves`** — replace the approximate M3 curves (the dominant uncertainty, AWN-26) with
   calibrated turbine fragility; the two-curve sub-peril split (AWN-32) is the interface to preserve.
3. **Strong-wind disruption/degradation track** (AWN-31) — the real strong-wind impact (curtailment + fatigue),
   deferred to the Performance tier / BI / reliability.
4. **Hurricane peril** (field-intensity, separate) — watch the TC-tornado forward double-count flag (AWN-30).
5. **Portfolio correlation** (AWN-22) — single-site only today.
6. *(housekeeping)* The CONUS-grid + hail-MRMS work in the tree is **uncommitted and unrelated** — left untouched.

See [`task_context.md`](task_context.md) · [`decisions.md`](decisions.md) · [`notes.md`](notes.md).
