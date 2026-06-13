# discussion/wind/

**Where we think out loud about wind — *before* we build it.** This folder is the deliberate "discuss in
detail, don't rush into M0" step the owner asked for. Nothing here is code or a plan-of-record; it is the
reasoning that *produces* the plan. Once a decision settles here, it graduates to `docs/plans/wind/`
(decisions `DD-WN-*`, assumptions `AWN-*`, and the layer-0 spec) and then to the notebooks.

Wind is **hazard 3 of 3** (hail ✅ · wildfire ✅ · **wind**), and it is the first peril that is a **sub-peril
family** rather than a single event. It is also the first peril where **no single data product pre-defines
the event** — so we must *author* the hazard definition ourselves, anchored in engineering and
meteorological standards. Both of those firsts are why we discuss before we plan: the scope fork
([`01`](01_scope_and_sub_peril_taxonomy.md)), the coupling map ([`02`](02_coupling_buckets_and_wind.md)),
and the authored hazard definition ([`03`](03_hazard_definition_and_thresholds.md)) all need to settle
before M0.

## Read order

| # | Doc | What it decides |
|---|---|---|
| 01 | [`01_scope_and_sub_peril_taxonomy.md`](01_scope_and_sub_peril_taxonomy.md) | **What V1 actually models** — wind as a sub-peril *family*; the materiality case (wind is a turbine's dominant hazard); why **inland-convective first** (strong wind + tornado) and **hurricane deferred**; the honest V1 label; the full deferred list; the two-site logic (Traverse high / Shepherds Flat low, mirroring hail's Hayhurst/Matrix). |
| 02 | [`02_coupling_buckets_and_wind.md`](02_coupling_buckets_and_wind.md) | **How the hazard *reaches* the asset** — the educational deep-dive on the three coupling buckets (areal hit-or-miss · field-intensity · site-conditioned), grounded in the reference's footprint taxonomy (point / narrow path / broad swath / regional field); where each wind sub-peril sits and **why**; the whole-platform coupling map (hail areal · wildfire site-conditioned · hurricane field-intensity), so "field-intensity vs the rest" finally clicks. Understand-before-M2. |
| 03 | [`03_hazard_definition_and_thresholds.md`](03_hazard_definition_and_thresholds.md) | **Why wind must be AUTHORED** (not inherited from a product) and the reasoning behind the layer-0 spec — the standards (NWS 58 mph, EF scale, ASCE 7-22, IEC 61400), the **two-threshold** insight (meteorological event threshold vs asset damage-onset), EVT-on-magnitude / bounded GPD / the ASCE RP surface as a pre-computed return-level curve, and the honest uncertainties. Understand-before-layer-0/M1. |

## Related (don't duplicate — link)

- The three coupling buckets, the platform-canonical source: [`../../../principles/hazard_asset_specificity.md`](../../../principles/hazard_asset_specificity.md) — and the original gpt deep-dive [`../gpt/03`](../gpt/03_coupling_types_hit_or_miss_field_intensity_site_conditioned.md).
- The settled wind plans these graduate into: [`../../../plans/wind/00_hazard_definition.md`](../../../plans/wind/00_hazard_definition.md) (layer-0) · [`../../../plans/wind/decisions.md`](../../../plans/wind/decisions.md) (`DD-WN-*`) · [`../../../plans/wind/00_intent.md`](../../../plans/wind/00_intent.md).
- The sibling wildfire discussion we mirror in spirit: [`../wildfire/README.md`](../wildfire/README.md).
- The pre-integrated-vs-extracted lesson strong-wind leans on: [`../../../learning_logs/09_pre_integrated_vs_extracted_catalog.md`](../../../learning_logs/09_pre_integrated_vs_extracted_catalog.md); the rare-event sample-size lesson tornado leans on: [`../../../learning_logs/10_monte_carlo_effective_sample_size.md`](../../../learning_logs/10_monte_carlo_effective_sample_size.md).
- The principles that govern every choice here: [`../../../principles/`](../../../principles/README.md). The scope-and-story anchor: [`../../00_scope_and_story.md`](../../00_scope_and_story.md).

## Status

🟡 **Open for discussion.** Seeded from the Hazard_Data_Reference (Keystone v1.1, Tornado & Strong-Wind
per-peril doc), the old `hazard_analysis` prior art (HAZARD_LIMITS, the bounded-GPD `mag_sim`, the F-scale
tornado model on commit `52db8e3`, the Method-0-vs-3 worked example), and the competitive/standards corpus
(NWS, EF, ASCE 7-22, IEC 61400). Awaiting the owner's calls on the open decisions before
`docs/plans/wind/` layer-0/M0/M1 planning hardens.
