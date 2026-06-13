# 01 — Wind × Wind-Farm V1: Scope & the Sub-Peril Taxonomy

*A discussion doc, not a plan. It exists to settle **what V1 actually models** before we open layer-0 / M0.
Wind is the first peril that is a **family**, not a single event — so the first job is to *decompose* it
honestly, then pick the most tractable, most material members to build first. Every section ends with a
decision; the owner's calls turn into `DD-WN-*` / `AWN-*` rows in `docs/plans/wind/`.*

---

## TL;DR (the whole argument in one screen)

1. **Wind is a sub-peril *family*, not one peril.** Tornado, straight-line convective wind, and hurricane
   are **genuinely different physical systems** — they pass the reference's dual split-test (distinct
   footprint **and** distinct data/metric), so they earn separate treatment. A *stronger vs weaker gust* is
   one peril; *a rotating vortex vs a broad outflow vs a regional cyclone field* is three.
2. **Wind is a wind turbine's *dominant* loss pathway.** Unlike solar (where hail and wildfire are #1/#2),
   the turbine is a tall, slender, aerodynamically-loaded structure — extreme wind is its defining structural
   hazard. So wind × wind-farm is the natural Hazard 3 of 3, and the loss is a **pure physical-damage** track.
3. **Route = inland-convective first: strong wind, then tornado. Hurricane deferred.** The two convective
   sub-perils together **tour two of the three coupling buckets we have already built** (tornado reuses
   hail's areal hit-or-miss; strong wind reuses wildfire's site-conditioned machinery), leaving only
   field-intensity (hurricane) — the genuinely unbuilt bucket — for later. See [`02`](02_coupling_buckets_and_wind.md).
4. **Strong wind is built *first* because the hazard arrives pre-integrated.** The **ASCE 7-22 design-wind
   map is a return-period 3-s-gust surface** — ASCE/NIST already did the probabilistic tail analysis — exactly
   the way FSim pre-integrated wildfire. That is the fastest path to a real number (mirrors the wildfire
   kickoff). Tornado second: rare, path-geometry-driven, the catastrophic tail.
5. **The hazard must be *authored*.** For hail (MESH) and wildfire (FSim) the event came pre-defined by the
   product. **No single product pre-defines a "wind event."** So we define it quantitatively, anchored in
   standards (NWS 58 mph, EF scale, ASCE 7-22, IEC 61400) — a new **layer-0** step above M0. See [`03`](03_hazard_definition_and_thresholds.md).
6. **The scope line is sharper for wind than for any prior peril.** For solar, "hazard" (hail, fire) and
   "resource" (sun) were obviously different things. For wind, **the hazard medium IS the resource medium** —
   so we must draw the line in words: hazard-tier wind = *extreme wind that structurally damages the turbine*
   (this repo); resource wind driving generation/revenue = the Performance tier (`model-gpr`).
7. **Two sites, mirroring hail's low-vs-high contrast:** **Traverse Wind Energy Center, OK** (high —
   tornado-alley + derecho corridor) and **Shepherds Flat, OR** (low — Columbia Gorge, minimal
   tornado/derecho). One unchanged engine, two very different risk pictures — the payoff.

---

## 1. Where we are, and why we're talking first

Hail × solar and wildfire × solar are both built end-to-end (shared `M0`/`M1` peril catalog → a `solar/`
cell for `M2–M4`). Wind mirrors that shape — but wind has **two firsts** that no prior peril had, and both
are scope traps if we rush:

- **It is a *family*.** "Wind" is not one event. If we model "wind" as a single peril we repeat the old
  model's false-generality mistake (one curve, one factor, one distribution across physics that differ). We
  have to decide *which members* we build, in *which order*, and *why* — before M0.
- **It is not pre-defined by a data product.** Hail's event ("severe hail ≥ 1 inch") came baked into MESH;
  wildfire's ("fire occurrence + flame-length classes") came baked into FSim. There is **no equivalent single
  product** that hands us "a wind event." We must author the definition — see [`03`](03_hazard_definition_and_thresholds.md).

The principles that decide the ties here:

- **Standard interface, not standard physics** — wind's members get *their own* physics behind the *same*
  typed interface; that is exactly what lets us split the family and **defer** the hardest member (hurricane)
  at zero architectural cost. The dual split-test ([P1](../../../principles/hazard_asset_specificity.md)) is the
  warrant for treating wind as a family.
- **Basics spot-on** — *the math is the product* — but also **don't over-claim coverage**: a correct tail on
  a mislabeled scope is still a credibility failure. "Wind risk" must not silently mean "convective wind only."
- **Modular from day one** — the shared compound-Poisson/NegBin Monte-Carlo loss engine **does not change**;
  each sub-peril ships value on its own and slots in by implementing the interface.

---

## 2. Wind is a sub-peril *family* — the split-test, applied

The Hazard_Data_Reference is explicit about *when* a phenomenon earns its own sub-peril tag. A phenomenon
splits only on **both** axes (the dual test, reference §2):

1. **Distinct physical footprint** — "a genuinely different physical system… not just a different intensity
   of the same process. *(A stronger vs weaker gust is one process.)*"
2. **Distinct data / magnitude metric.**

The reference's own verdict table rules: *"Tornado / Strong Wind — rotating vortex / straight-line field —
distinct footprint + SPC data split — Split [T]/[W] — correct."* Note the split is on **footprint geometry**,
not gust magnitude. Run the three convective-vs-cyclonic members through the test:

| Member | Physical system (footprint) | Magnitude metric / data | Splits? |
|---|---|---|---|
| **Tornado [T]** | rotating vortex — **narrow, intense path** | EF scale (damage-inferred) + path length × width; SPC SVRGIS path polygons | ✅ distinct footprint **and** distinct data (path geometry, unique to tornado) |
| **Strong / straight-line wind [W]** | straight-line field — **broad swath** (derecho, downburst, thunderstorm gust, synoptic high wind) | 3-s gust (kt, measured/damage-inferred); SPC severe-wind point reports + ASCE RP surface | ✅ distinct footprint **and** distinct data (point reports, no path) |
| **Hurricane** | rotating cyclone — **regional intensity field** | 3-s gust over a swath built from a track; public stochastic catalogs (STORM/RAFT) + Holland field | ✅ distinct footprint **and** distinct data (track + parametric field) |

All three pass. **Wind is a family of (at least) three peers**, each with its own footprint and its own
coupling type. The 3-s gust is the *shared* magnitude metric across all of them (the universal wind metric —
[`03`](03_hazard_definition_and_thresholds.md)), but the footprint geometry and the data path differ — which
is precisely what the dual test cares about.

> **DECISION WN-1 (gating).** Treat wind as a **sub-peril family** (tornado · strong wind · hurricane as
> distinct peers, each splitting on footprint + data), and build the taxonomy once before building any
> member? *(Recommended: yes — corroborated by the reference's own [T]/[W] verdict and the [P1](../../../principles/hazard_asset_specificity.md) dual test.)*

---

## 3. Why wind, why the turbine — the materiality case

For solar, hail and wildfire were chosen because they are the #1/#2 *loss drivers* on PV. For a **wind
turbine**, the dominant hazard *is wind itself* — and not the everyday resource wind, but the **extreme tail**:

- The reference puts tornado and strong wind in the **Destruction (Damage) family**, and names the wind
  turbine's dominant loss pathway as **Damage** (not disruption). So wind × wind-farm is a **pure
  physical-damage build** — the function/revenue-disruption track (energy-not-served, repair downtime) is
  *out of scope here*; it lives in the Performance tier and in repair-duration modeling.
- A utility-scale turbine is a tall (80–130 m hub), slender, aerodynamically-loaded structure whose damage
  mechanisms the reference lists directly: *"wind loading & overturning; debris impact; **turbine blade/tower
  failure**."* The primary exposed asset for convective wind is literally *"wind turbines (direct)."* This is
  the asset the hazard was made for.
- The loss is **asymmetric across the turbine's subsystems** — strong wind reaches the exposed aero
  subsystems (rotor/blades, nacelle/drivetrain); a tornado reaches further (it can take the tower). That
  subsystem distinction is real and feeds M3 (the old repo's `wind_config` already encoded it — see [`02`](02_coupling_buckets_and_wind.md) and the M3 plan).

So Hazard 3 = wind, asset = utility-scale onshore wind farm, is the natural completion of the
peril × asset map: it is the turbine's defining structural risk, and it is a clean damage track.

---

## 4. The route — inland-convective first, hurricane deferred

Wind has three buildable members. The order is **not** arbitrary; it falls out of two questions: *which is
most tractable (fastest to a real, defensible number)?* and *which reuses machinery we already have?*

```text
THE WIND FAMILY — build order
──────────────────────────────────────────────────────────────────────
  1. STRONG / STRAIGHT-LINE WIND  ──▶  SITE-CONDITIONED (bucket 3)
       broad swath; reuses WILDFIRE's M2; ASCE RP surface = pre-integrated
       hazard (like FSim) → FASTEST path to a real number.  High-frequency.

  2. TORNADO                       ──▶  AREAL HIT-OR-MISS (bucket 1)
       narrow path; reuses HAIL's Minkowski (path-aware thin rectangle).
       Rare per site → sparse Monte Carlo → the catastrophic tail.

  3. HURRICANE  [DEFERRED]         ──▶  FIELD-INTENSITY (bucket 2)
       regional field; the GENUINELY UNBUILT bucket. Holland wind field
       along a track → swath grid → portfolio correlation + EVT load-bearing.
──────────────────────────────────────────────────────────────────────
NET: inland-convective tours TWO already-built coupling types,
     leaving only field-intensity (hurricane) for later.
```

**Why strong wind first.** It is the wildfire of the wind family: the hazard arrives **pre-integrated**. The
ASCE 7-22 design-wind map is a return-period 3-s-gust surface — ASCE/NIST already baked the probabilistic
tail extrapolation into it (reference §4/§7: *"the maps embed the RP"*). That is the same situation as
FSim's BP+FLP for wildfire, so strong-wind M1 is **profile-assembly, not event-extraction**
([learning_logs/09](../../../learning_logs/09_pre_integrated_vs_extracted_catalog.md)) and M2 **reuses
wildfire's site-conditioned machinery**. Pre-integrated hazard = fastest path to a real number — exactly the
lesson the wildfire kickoff cashed in. (Frequency-regime bonus: strong wind is high-frequency, so its tail is
well-populated — the easy Monte-Carlo regime.)

**Why tornado second.** It reuses hail's areal hit-or-miss coupling — a narrow tornado path is a thin
rectangle (extreme aspect ratio), so hail's Minkowski sum `(√F+√s)²/A` becomes a **path-aware** variant
dominated by length × asset-extent. But tornado is **rare per site** (low strike probability at any point),
so the Monte Carlo is **sparse** — it exercises [learning_logs/10](../../../learning_logs/10_monte_carlo_effective_sample_size.md)
(effective sample size) and *forces* us to report TVaR alongside VaR (the old repo's F-scale model floors VaR
to $0 in the sparse regime). The catastrophic single-asset tail is the payoff and the harder validation.

**Why hurricane is deferred** (named, fence visible):
- It is the **genuinely unbuilt coupling bucket** — field-intensity (bucket 2). A hurricane is *always inside
  the wind field*; the question is never "did it hit," it is "what wind speed did the site experience." That
  needs a **Holland parametric wind field along a track → swath grid** — net-new machinery, not a reuse.
- It is **coastal**, not inland-convective — a different geography and a different data path (public
  stochastic catalogs STORM/RAFT + the Holland field), where **portfolio correlation and EVT become
  load-bearing** (one event hits many assets; the field tail must be extrapolated).
- It is therefore the **bigger build** and the natural *next* field-intensity peril — we name it as the
  future build and **where** the field-intensity machinery + EVT-at-portfolio-scale will earn their keep, and
  we **do not** build past the wall.

> **DECISION WN-2 (gating).** Build order = **strong wind (site-conditioned, ASCE-pre-integrated) → tornado
> (areal, path-aware) → hurricane DEFERRED (field-intensity)**? *(Recommended: yes — tractability +
> coupling-reuse + the honest deferral of the one unbuilt bucket.)*

---

## 5. The honest V1 label

Same forcing function as wildfire's exogenous-vs-endogenous honesty: state coverage limits in the open, so a
*partial* wind model is never mistaken for *total* wind risk.

> *Wind × Wind-Farm V1 models **inland-convective extreme wind only** — **strong / straight-line convective
> wind** (derecho, downburst, thunderstorm gust, synoptic high wind; site-conditioned via the ASCE 7-22
> return-period gust surface) and **tornado** (areal path-strike via the SPC path record). Magnitude = the
> **3-second peak gust** at hub height, mapped through an **anchored, IEC-survival-conditioned** turbine
> damage curve, and aggregated through the shared compound-Poisson/NegBin Monte Carlo. **Hurricane / tropical
> cyclone is a distinct, deferred sub-peril** (the field-intensity build). **Hail-on-turbine, lightning,
> ice/icing throw, and winter/synoptic non-convective extremes** are further distinct deferred channels. V1
> does **not** claim to cover total wind risk to the asset.*

This is the *basics-spot-on* honesty axis applied to scope: the math may be right, but a model that silently
calls "convective wind" the whole of "wind risk" repeats the old model's credibility problem in a new costume.

> **DECISION WN-3 (gating).** Adopt the honest V1 label above and lock it into `00_intent.md` + a `DD-WN-*`
> row? *(Recommended: yes.)*

---

## 6. The full deferred list (named, so the fences are visible)

Beyond the V1 convective members, the wind family — and the turbine's broader wind-adjacent exposure — has
several distinct deferred channels. Naming them is the point; each is a *different peril or process*, not a
setting of the V1 model:

| Deferred channel | Why it is distinct (not a V1 setting) | Coupling bucket / process |
|---|---|---|
| **Hurricane / tropical cyclone** | rotating regional cyclone; coastal; track + parametric (Holland) wind field; public stochastic catalogs | **Field-intensity (bucket 2)** — the genuinely unbuilt bucket; the next field-intensity build |
| **Hail-on-turbine** | distinct hazard *medium* (ice, not wind); already a built peril for solar — would be a new wind × hail cell, not a wind sub-peril | areal hit-or-miss (already built for solar) |
| **Lightning** | electrical/thermal, not aerodynamic; ignites/destroys via current, not gust; own frequency process (flash density) | distinct peril; not wind-driven structural loss |
| **Ice / icing & ice-throw** | accretion load + shed-ice projectile; a *winter* process; own magnitude metric (ice thickness) | distinct peril (the reference lists ice as its own hazard with its own metric) |
| **Winter / non-convective synoptic extremes** | broad-area high wind from synoptic systems (some of this *is* captured by the ASCE map as part of [W]) — the genuinely *non-convective* part (winter storms, ETCs) is out of the convective V1 scope | partially site-conditioned; flag the boundary |
| **Fatigue / sub-extreme operational loading** | gradual aerodynamic fatigue from *resource* wind — **Performance-tier**, not a catastrophic event | **out of this repo entirely** (see §7) |

> Most of the everyday "wind" a turbine sees is the *resource* wind that drives generation. V1 is explicitly
> the **extreme structural-damage tail** of the convective members only. (Honest-label discipline, §5.)

---

## 7. The scope line — hazard wind vs resource wind (the hard line)

This is the **critical** boundary for wind, and it must be in words because — unlike every prior peril — the
hazard medium *is* the resource medium.

```text
For SOLAR (hail, wildfire):  HAZARD medium  ≠  RESOURCE medium      (hail/fire vs sun — obvious)
For WIND:                    HAZARD medium  =  RESOURCE medium      (wind vs wind — BLURS)
                                                       ↓
                          we draw the line in WORDS, not by the medium
```

| | **Hazard-tier wind (THIS repo)** | **Performance-tier wind (`model-gpr`)** |
|---|---|---|
| What | **Extreme** wind that **structurally damages** the turbine | The wind **resource** driving generation/revenue |
| The question | "Did an extreme event break the structure?" → **physical loss** | "How much energy/revenue did the wind produce, and how variable?" → **P50/P90/P99 generation** |
| Magnitude | 3-s peak gust above the damage-onset threshold (IEC survival) | mean wind speed at hub height, power curve, capacity factor |
| Loss object | damage ratio × TIV (asset value) | generation shortfall / revenue variability |
| Output | EAL / VaR / PML / TVaR (% of TIV alongside $) | probabilistic generation forecast |

The hard line: **hazard-tier wind = the destructive tail; performance-tier wind = the productive body.** The
two share a medium and a metric family (wind speed) but they answer different questions, live in different
tiers, and must not be conflated. V1 models *only* the destructive tail of the convective members.

> **DECISION WN-4 (gating).** State this hard scope line explicitly in `00_intent.md` **and** as a `DD-WN-*`
> decision (it is the single most blur-prone boundary in the whole platform)? *(Recommended: yes — required
> by the AGENTS tier-scope mandate; for wind this is not optional housekeeping, it is the scope.)*

---

## 8. The two sites — Traverse (high) vs Shepherds Flat (low)

Hail proved the engine with a deliberate **low-vs-high** pair (Hayhurst, negligible vs Matrix, material), so
the same unchanged engine produces two very different risk pictures. Wildfire did the same (Hayhurst vs
Matrix). Wind mirrors it — two real utility-scale onshore wind farms, picked from the renewablesinfo boundary
DB (OSM/EIA polygons), straddling the convective-wind hazard gradient:

| | **Traverse Wind Energy Center** (HIGH / proving) | **Shepherds Flat** (LOW / baseline) |
|---|---|---|
| Location | Oklahoma | Oregon (Columbia Gorge) |
| Capacity | ~999 MW | ~845 MW |
| Why this site | **Tornado-alley + derecho corridor** — high strike-density geography; the site that *should* light up | Minimal tornado/derecho exposure; the calibration "near-zero" baseline |
| What it proves | the catastrophic-tail (tornado areal strike) and the well-populated strong-wind tail both register | the engine returns a *correctly small* number where the hazard is genuinely low (the negligible-but-not-zero check) |

The **boundary polygon** (from the boundary DB) gives the areal footprint for path/swath intersection (the
tornado coupling needs an *area*, not a point). The **per-turbine point locations** come from **USWTDB** — for
the per-turbine view (a long line of turbines has many times the strike exposure of a single point; the
reference: *"a point lookup understates linear assets"*). So: polygon for the areal/site footprint, USWTDB
points for the per-turbine resolution.

> ⚠️ **Owner action / to-verify at M0.** Confirm both boundary polygons resolve in the renewablesinfo
> boundary DB and that USWTDB has the turbine point clouds for both. The capacities here are nameplate
> approximations from the settled framing — pin the exact MW + turbine count + model at M0 (they scale TIV
> and the per-turbine count). *(Status: to-verify — see [AWN-*](../../../plans/wind/assumptions.md).)*

> **DECISION WN-5.** Lock the two-site pair (Traverse high / Shepherds Flat low), with polygon-for-footprint
> + USWTDB-for-turbine-points? *(Recommended: yes — direct hail/wildfire analogue; sites are real and in the
> boundary DB.)*

---

## 9. Light layer-0 / M0 / M1 sketch (context only — we still plan these step by step)

```text
LAYER-0  docs/plans/wind/00_hazard_definition.md   ← the NEW step, above M0 (wind is AUTHORED)
    └ author the hazard quantitatively: 3-s gust observable; event threshold μ
      (NWS 58 mph / EF0 65 mph); physical bound L (EF5 ceiling ≈ 113 m/s); the
      SECOND, asset-coupled threshold (IEC 61400 survival/design); bounded-GPD
      severity / ASCE RP surface. The two thresholds kept distinct. See 03.

M0  Notebooks/wind/m0_input_data/   (peril-shared)
    └ SPC SVRGIS (tornado paths + wind reports) · NOAA Storm Events · ASCE 7-22
      RP gust surface (point lookups) · ASCE Ch 32 tornado maps · USWTDB turbine
      points · the two site boundaries. Interpret every layer; record the
      population/reporting-bias caveat (SPC counts are population-biased — bias-
      correct before fitting frequency). Both sites are rural → historical EF
      severity likely understated (the rural-low-bias caveat).

M1  Notebooks/wind/m1_catalog/   (peril-shared)
    └ per-sub-peril event definition + λ + bounded-GPD severity:
        strong wind  = ASCE pre-integrated RP surface (profile-assembly, learning-09)
                       OR a SPC-extracted catalog (Poisson occurrence + GPD gust);
        tornado      = SPC path stats (EF-class probs, path length × width, areas).

    (then, per sub-peril, step by step:) M2 coupling — tornado areal (hail
    Minkowski, path-aware) · strong wind site-conditioned (wildfire reuse) ·
    M3 anchored turbine damage curve (IEC survival onset, operational state) ·
    M4 the SHARED compound-Poisson/NegBin MC, untouched, metrics off the SAMPLED
    distribution, % of TIV alongside dollars (NEVER the Method-0 expected-loss shortcut).
```

---

*Next: once the owner settles Decisions WN-1…WN-5, these graduate to `docs/plans/wind/` (`00_intent`,
`00_hazard_definition`, `decisions.md` `DD-WN-*`, `assumptions.md` `AWN-*`), and we open **layer-0**, then
**M0** — one layer at a time, no jumps. The coupling reasoning that justifies the build order is in
[`02`](02_coupling_buckets_and_wind.md); the authored hazard definition is in [`03`](03_hazard_definition_and_thresholds.md).*
