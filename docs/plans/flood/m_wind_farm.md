# Plan: Flood × Wind-farm cell (V2)

*The second asset for the flood peril. Mirror the flood × solar build (M0→M4) but on the **wind-farm** asset — a
**sparse turbine point-cloud over a huge lease**, not a dense areal footprint. Reuses the flood engine (JD-FL-7
annual-max MC) and the convective_wind wind-farm asset template (USWTDB cloud + capex curve), with a genuinely new
M2 (per-node coupling) and M3 (greenfield flood × wind curve).*

> **Status: built end-to-end (M0→M4).** High site **Green River, IL** (Lee Co., 74 turbines, ~194 MW, **60% of
> turbines in the SFHA**) + baseline **Shepherds Flat, OR** (reused from convective_wind, **mapped-dry**). Two
> findings drove the design (below). Decisions: [`decisions.md`](decisions.md) (JD-FL-W1…4).

## The two findings that shaped the build

1. **Wind turbines are flood-immune in Texas (JD-FL-W2).** Unlike a solar farm (one contiguous footprint that
   floods as a unit), a wind farm's turbines are sited on **high ground**. Verified across the **entire east/coastal
   TX wind fleet** (44 farms, ~2,976 turbines, FEMA BLE coverage confirmed): **0 turbines in even the 500-yr
   floodplain.** So Texas — the solar high site's region, with the clean BLE reuse — gives **no** turbine-level flood
   exposure. The BLE-reuse path is a dead end for wind.
2. **Midwest river-valley wind genuinely floods (JD-FL-W3).** A corridor sweep (upper-Mississippi/Missouri/Illinois;
   12,666 turbines, 316 projects) found farms straddling the 1% floodplain — led by **Green River, IL** (~60% of
   turbines in the SFHA). That is the real high-flood wind site. **Cost:** it is **Zone A** (approximate floodplain —
   no BFE) and **outside BLE coverage**, so depth comes from JD-FL-6's *national fallback* (an **extent-based
   bathtub** off 3DEP), not the BLE shortcut (JD-FL-W4).

## Phase breakdown (built)

| Phase | M-step | What we built | Notebook | Status |
|------:|--------|---------------|----------|--------|
| 1 | M0 | Wind site screen + geometry: Midwest river-corridor SFHA screen → **Green River**; reuse **Shepherds Flat**; USWTDB turbine clouds; convex-hull boundary; substation node; TIV ($/kW). | `wind_farm/m0_input_data/01_wind_site_screen_and_geometry` | ✅ |
| 2 | M1 | **Per-turbine + substation depth-at-RP** via the **extent-based bathtub** (`WSE@SFHA-edge on 3DEP − ground − pad`), 100-yr (Zone A) & 500-yr (0.2% band). | `wind_farm/m1_catalog/01_catalog` | ✅ |
| 3 | M2 | **Per-node site-conditioned** coupling — which turbines flood + how deep, + the substation. Loss summed over flooded nodes, **not areal**. | `wind_farm/m2_coupling/01_coupling` | ✅ |
| 4 | M3 | **Greenfield flood × wind curve** — rotor/nacelle/tower **flood-immune** (0.63, DR 0); base vulnerable (foundation+electrical+civil+substation, ~0.37); shapes borrowed from flood×solar + a foundation judgment. Vendored. | `wind_farm/m3_damage/01_damage` | ✅ |
| 5 | M4 | **Annual-max MC** (JD-FL-7, reused) → EAL / VaR / PML / TVaR, % of TIV. Loss summed over flooded turbines + substation. | `wind_farm/m4_loss_metrics/01_loss_metrics` | ✅ |

## Key methods (vs flood × solar)

- **Asset geometry:** USWTDB turbine point cloud + a **convex-hull** boundary (the `renewablesinfo_org` boundary-DB
  symlink is absent here; the hull is the honest extent for a point cloud — AFL-W4). Baseline reuses convective_wind's
  cached boundary-DB polygon.
- **Depth (M1):** **extent-based bathtub** — Zone A has no BFE and no BLE, so the 1% floodplain *boundary* is the 1%
  water-surface contour; `depth = WSE(median of nearest SFHA-edge 3DEP samples) − turbine_ground − pad`. Sampled **at
  each turbine** (a point cloud), not over an areal footprint. Medium-low confidence (flat-water over a sloping Zone A
  floodplain) — StreamStats+HAND / detailed-study BFE is the documented upgrade.
- **Coupling (M2):** **per-node site-conditioned** — exposure = the identity + depth of **flooded turbines** + the
  substation; loss is a **sum over flooded nodes**, not solar's areal `exposure_fraction × conditional_depth`.
- **Damage (M3):** **greenfield** (no flood × wind in `infrasure-damage-curves`). Capex weights from the old-repo
  `wind_config`; rotor/nacelle/tower **immune** (elevated → DR 0); base vulnerable; curve shapes borrowed from the
  flood × solar library + a foundation-scour judgment. **Flood is a capped peril for wind** — a fully-inundated
  turbine loses only ~28% of its value (the immune top is 0.63).
- **Loss (M4):** the **same** JD-FL-7 annual-max MC as solar — the only difference is upstream (per-node summed L₁₀₀/
  L₅₀₀).

## Honest limits (carried) / upgrades (seam-ready)

- Bathtub depth (Zone A) → **StreamStats+HAND** densifies; lower-RP points harden EAL.
- Greenfield curve (low-medium confidence) → graduates to `infrasure-damage-curves`; foundation curve is judgment.
- Substation at a **centroid proxy** (AFL-W5); pad elevations assumed (AFL-W6); hull boundary; $/kW TIV.

## Files

- `decisions.md` — JD-FL-W1 (sites/baseline reuse), JD-FL-W2 (TX flood-immune finding), JD-FL-W3 (Midwest high
  site), JD-FL-W4 (extent-based bathtub depth).
- `assumptions.md` — AFL-W1…W6.
