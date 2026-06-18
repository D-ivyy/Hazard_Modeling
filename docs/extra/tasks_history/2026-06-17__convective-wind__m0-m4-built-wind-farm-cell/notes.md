# Notes — implementation detail, verification, metrics (2026-06-17)

## The two M3 curves (the upgrade)
One turbine, shared capex split (rotor 0.26 · nacelle 0.21 · tower 0.16 · foundation 0.12 · substation 0.09 ·
electrical 0.09 · civil 0.07). Per-sub-peril fragility `{subsystem: (x0_ms, k)}` — the loading mechanism differs:

```python
FRAG = {
  "strong_wind": {"rotor_blades":(60,0.30), "nacelle_drivetrain":(66,0.28), "substation":(62,0.28), "electrical":(64,0.28)},   # aero reach, IEC-survival onset
  "tornado":     {"rotor_blades":(52,0.25), "nacelle_drivetrain":(58,0.24), "tower":(66,0.22), "foundation":(80,0.20),
                  "substation":(54,0.24), "electrical":(56,0.24), "civil":(62,0.22)},                                          # all subsystems, lower onset + steeper
}
dr(v, sp) = Σ CAPEX[s] / (1 + exp(-k·(v - x0)))   over FRAG[sp]
```
- **DR by EF (tornado / strong wind):** EF2 0.36 / 0.07 · EF3 0.77 / 0.50 · EF4 0.94 / 0.65 · EF5 ~1.0 / 0.65.
- **Onset (DR≥5%):** tornado ≈ 44 m/s vs strong wind ≈ 54 m/s. `DR_tornado(v) > DR_strongwind(v)` at every gust.
- **Anchor:** `DR(μ=58 mph) ≈ 0` both (tornado 7e-4, strong wind ~0). `DR_strongwind(L) ≈ 0.65` (aero cap); `DR_tornado(L) → 1`.
- The params are **approximate** (AWN-26) — the dominant uncertainty; calibrated curves are the deferred upgrade.

## M4 metrics (seed 42, M=300,000 yr)
| | Traverse | Shepherds |
|---|---|---|
| TIV | $1,399M | $1,183M |
| λ_strongwind / λ_tornado(asset) | 0.90 / 0.2398 (NegBin φ=12) | 0.36 / 0.0025 (Poisson) |
| EAL | 0.0637% ($0.89M) | 0.0057% ($0.07M) |
| EAL_strongwind / EAL_tornado | 0.0203% / 0.0434% | 0.0057% / 0.0000% |
| VaR99 / PML250 / TVaR99 | 0.94% / 3.99% / 4.88% | 0.06% / 0.15% / 0.35% |
| zero-loss years | 38.4% | 69.8% |

VaR aggregation (Traverse): VaR99_sw $2.86M + VaR99_tor $6.89M = $9.76M vs **joint** $13.13M → summing
**understates** by ~26% (super-additive). EAL additive holds exactly (split sums to combined).

## Commands / verification
- Execute: `jupytext --to notebook --execute <nb>.py` (kernel `hazard_modeling`); verified **0 error outputs** in all 4
  regenerated `.ipynb` by scanning cell outputs for `output_type == "error"`.
- **Link-checker** (`/tmp/linkcheck.py`, ad-hoc): extracts relative markdown links from `.py`/`.md`/`.ipynb` under
  `Notebooks/convective_wind` + `docs/plans/convective_wind` + `docs/extra/discussion/convective_wind`, resolves each,
  reports missing. Restructure started at **42 broken** (all the +1-depth shift), ended at **0**.
- The restructure shifted every moved notebook one folder deeper, so every repo-root-relative link needed one extra
  `../`; sibling/in-cell links (`../strong_wind/`, `../m3_damage/`) were preserved automatically. m2-fork links fixed
  by `perl` +1; M3/M4 rewritten fresh with correct depth-4 links.

## Key insights
- **Mechanism vs reach** — the cleanest way to see why tornado damage > strong-wind damage at the same gust: a
  feathered turbine survives straight-line wind by design (onset = IEC survival, aero only); a tornado's rotation
  defeats feathering and adds loads the design never anticipated, and the EF scale is read *from* the damage. So the
  difference is per-subsystem onset/steepness, not just which subsystems are in play.
- **The MC earns its keep** — it caught the VaR-direction error (understate, not overstate). Verification > intuition
  for tail aggregation.
- **Staging discipline** — the working tree also has unrelated CONUS-grid + hail-MRMS + `.docx` churn; the wind commit
  staged explicit wind paths only (sanity-checked that nothing else leaked) — `*.parquet` is gitignored so only JSON
  manifests committed.
