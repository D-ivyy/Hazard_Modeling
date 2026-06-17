# 00 — Intent

*The seed for the flood pipeline. Captured before M0 planning — to be refined as we research and plan.*

## The goal

Take a **new peril — flood — and build the whole end-to-end workflow in notebooks**, step by step, exactly as hail,
wildfire, and wind were built. **V1 builds the solar cell first** — flood × solar, M0→M4 — and only **after it is
built and reviewed end-to-end** do we add the **wind-farm** cell off the same shared flood catalog (solar-first, then
wind, mirroring how wildfire was built). Flood is the **first peril owned outside the hail/wildfire/wind line**, so
it proves the M0→M4 interface generalizes to a peril nobody on the team has staked. Each step legible, every basic
verified, the **shared loss engine untouched**.

## Why flood (this pick)

Three reasons it earns the slot. (1) **Lowest redundancy.** Hail, wildfire, and wind (incl. hail × wind-farm) are all
built or planned by the repo owner; **flood is untouched**, so every cell here is genuinely new rather than a second
pass at owned territory. (2) **It extends the proven `× solar` path.** Flood × solar reuses the **site-conditioned**
coupling machinery from wildfire × solar and the shared loss engine — so the new work concentrates on the *flood
physics* (M0/M1 data + frequency, M3 depth-damage), not on re-deriving asset geometry. (3) **Data-rich, self-serve,
and already defined in the references.** FEMA NFHL, USGS gauges, return-period depth grids, and public DEMs make the
input data fetchable without a private feed — and the competitive-research **A-series** (A12/A20/A21/A22) already
pre-defines flood's taxonomy, catalog method, coupling, and damage form. So flood is an **inherited-definition**
peril (like wildfire from FSim), *not* an authored one (like wind): we adopt the A-series spine and concentrate the
build on plumbing it into our pipeline ([`01_references.md`](01_references.md)).

## What V1 is — and is NOT (the honest label — to be settled in JD-FL-1)

> **Flood is a sub-peril family** (A12): **Riverine `[R]`** (river-network-anchored), **Pluvial `[F]`** (grid-anchored
> local rainfall), **Coastal `[C]`** (coastline surge). **Flood V1 models *exogenous inland riverine + pluvial
> inundation* causing *physical equipment damage* to a utility-scale solar farm** — the asset as a **receptor** of an
> inundation depth that reaches its equipment. **Coastal `[C]` is deferred and cross-linked to hurricane** via a
> shared `event_family_id` (A12 §3 / A20 §6.8) — surge frequency follows tropical-cyclone tracks, so it rides the
> deferred hurricane field rather than being excluded. **Also out of scope:** foundation scour / erosion, long-term
> corrosion, water-quality effects, and **business-interruption loss** (the BI bucket — physical loss only, the A25
> acute × damage cell; matches the team's hazard-tier scope). **V1 does not claim to cover total flood risk.**

This honesty is *basics-spot-on* applied to scope: a correct tail on a mislabeled or over-claimed peril is still a
credibility failure — the exact thing the rebuild exists to escape. (Mirrors wildfire's DD-W1 and wind's DD-WN-1.)

## The asset (V1) — solar farm

A **solar farm** is a **dense areal polygon** → flood couples as **site-conditioned** (bucket 3, the wildfire row):
the flood-depth field is sampled over the asset footprint, **modulated by micro-elevation (DEM)**, and the asset's
equipment **height** is the susceptibility — base-level electrical (inverters, combiners, transformers) is destroyed
at shallow depth while elevated panels survive it. No hail-style Minkowski areal hit-or-miss; the coupling is the
depth field met against equipment height. Unlike wildfire, **micro-topography is load-bearing** — flood depth varies
sharply with a metre of elevation, so the asset's height relative to the flood surface *is* the coupling.

## Deferred to V2 (after V1 solar is built and reviewed) — wind farm

Once flood × solar runs M0→M4 and is reviewed, add the **wind-farm** cell off the **same shared flood M0/M1**. A wind
farm is a **sparse turbine point-cloud**, so flood is still site-conditioned but sampled **per-turbine pad elevation
vs the flood surface** (only low-lying turbines flood; foundation / base-electrical exposure). That point-cloud
geometry is what the owner is actively designing in the `wind/` and `hail-wind-farm` plans — so when V2 opens,
**coordinate the turbine-exposure approach with the owner first**, to reuse rather than diverge. **Not built until V1
solar is checked.**

## Domain principles for this pipeline

- **Standard interface, not standard physics** — flood gets site-conditioned coupling *behind the interface hail and
  wildfire already defined*; the loss engine never changes.
- **Basics spot-on** — tail metrics off the *sampled* loss distribution (never the expected-loss shortcut / Method 0);
  two thresholds kept distinct — the **flood event / return-period basis** (what the catalog counts) vs the **damage-
  onset depth** (where the depth-damage curve leaves zero — e.g. inverter-pad height); depth-frequency anchored in the
  standard flood-frequency literature, not assumed.
- **Modular from day one** — M0 / M1 are the shared peril catalog (built to serve the later wind cell too); M2→M4
  specialize to solar in V1. The wind fork is **only at M2** when V2 opens; M3 / M4 reuse the shared machinery.

## What success looks like (V1)

A reviewable, step-by-step notebook series that takes raw public flood data to a coherent *sampled* annual loss
distribution for a **solar farm** (EAL / VaR / PML / TVaR, **% of TIV**), honestly labeled as inland-riverine-and-
pluvial-only, built on site-conditioned coupling the platform already owns, every step legible, every basic verified —
and a shared M0/M1 catalog ready for the deferred wind-farm cell.

## Open questions (to resolve as we plan)

*The A-series pre-settles much of the spine — these are seeded as proposed decisions in [`decisions.md`](decisions.md);
the starred one is the genuinely-open call.*

- **★ Event-model bridge — RP grids → the shared compound-Poisson MC (THE load-bearing decision).** The flood
  reference world (HAZUS / First Street) computes loss at each return period then integrates the **exceedance curve →
  AAL**; our shared M4 is a **compound-Poisson MC** sampling events/year. Convert the RP depth grids into an event
  stream the MC can sample (the wildfire precedent — FSim pre-integrated → λ → same MC), or run an RP+AAL track and
  reconcile metrics. Settle before M4. ([JD-FL-?](decisions.md))
- **M1 frequency path** — *proposed decided:* **pre-integrated return-period depth grids** (A20 §3.3), USGS / Log-
  Pearson III as the validation cross-check ([learning_logs/09](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)). Confirm the actual public product (Fathom-US 2.0 vs FEMA Risk MAP vs licensed First Street) in M0. ([JD-FL-2](decisions.md))
- **Flood-type scope** — *proposed decided:* riverine + pluvial in V1, **coastal `[C]` deferred + hurricane-cross-linked**
  (A12). Decide riverine-only vs riverine+pluvial for the *first* M0 notebook (pluvial may lag). ([JD-FL-1](decisions.md))
- **Depth-damage curve source** — *proposed:* tabular **USACE building-archetype + per-asset DEM elevation offset**
  (A22 §2.4/§7.6); subsystem split (base electrical drowns shallow; elevated panels survive); **solar-specific curve
  deferred** (A22 Q7 — none exists publicly). ([JD-FL-?](decisions.md))
- **Two solar sites (low-vs-high flood contrast), mirroring hail's Hayhurst/Matrix.** A high-flood-exposure solar site
  (floodplain-adjacent) + a low baseline — possibly **reuse Hayhurst (TX desert)** as the low control for cross-peril
  coherence (the owner's stated preference). ([AFL-?](assumptions.md))
- **TIV basis** — estimate solar TIV from $/kW (no registry TIV yet); report % of TIV alongside dollars.
