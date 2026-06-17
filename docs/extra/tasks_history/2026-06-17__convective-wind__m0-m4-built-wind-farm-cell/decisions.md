# Decisions — convective-wind build session (2026-06-17)

Canonical log: [`../../../plans/convective_wind/decisions.md`](../../../plans/convective_wind/decisions.md) (DD-WN-*).
This file indexes the decisions *made or realized* this session.

## New / realized this session
- **DD-WN-16 — M3 = one turbine, TWO sub-peril fragility curves (logical fork, not a folder fork).** The M2
  folder-fork is justified (coupling machinery differs); M3 is **not** a folder fork (the asset is one turbine —
  shared subsystem/capex split + IEC anchor) but it **does** carry two sub-peril *parameterizations*. A tornado is
  more damaging than straight-line wind at the **same** 3-s gust → lower onset + steeper + full reach; strong wind →
  aero reach, onset at IEC survival. *Why:* modeling only reach (the first cut) under-stated the tornado tail; the
  loading mechanism genuinely differs. M4 samples each stream through its own curve.
- **Asset-cell placement** — `convective_wind/wind_farm/` (M2–M4), mirroring `hail/solar/` / `wildfire/solar/`; peril
  layers (layer0/m0/m1) stay above it; `solar/` is a future sibling cell. (Realizes the `peril → asset` house rule.)
- **Rename `wind/` → `convective_wind/`** — the folder is the *convective-wind peril* (tornado + strong wind), not
  "wind" generally; hurricane is a separate, deferred peril (DD-WN-2 / DD-WN-9).

## Corrected this session
- **AWN-29 (VaR aggregation direction)** — was "summing overstates the joint tail"; the 300k-yr MC proved it
  **understates** (~26%) — VaR is **super-additive** for these zero-inflated, NegBin-clustered tornado tails (the
  opposite of the textbook continuous case). Rule unchanged: read every tail metric off the **joint** distribution.

## Carried (settled earlier, honored here)
- **DD-WN-1** convective wind = one peril, two sub-perils (dual test) · **DD-WN-4/5** coupling buckets (strong wind
  site-conditioned; tornado areal path-aware) · **DD-WN-11** anchored subsystem logistic · **DD-WN-12/13** every
  metric off one MC, never Method 0 · **DD-WN-14/15** co-sample / disjoint-by-data-product (EAL additive, tail not).
- **AWN-31** strong-wind damage ≈0 (disruption/degradation deferred) · **AWN-26** curves approximate (dominant
  uncertainty) · **AWN-22** single-site (portfolio correlation deferred).

## New assumption
- **AWN-32** — sub-peril damage *severity* differs at the same gust (tornado > straight-line wind; mechanism, not
  just reach). `[OURS]`, basis for DD-WN-16.
