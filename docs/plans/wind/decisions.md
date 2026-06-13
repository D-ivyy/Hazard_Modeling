# Wind pipeline — decisions log

Running record of the non-obvious design decisions for the wind build, ADR-style
(context → options → decision → why → revisit trigger). `DD-WN-*` = wind-scoped (distinct from hail's `DD-*` and
wildfire's `DD-W*`). Newest on top. Full reasoning lives in the discussion docs
([`01 scope/taxonomy`](../../extra/discussion/wind/01_scope_and_sub_peril_taxonomy.md),
[`02 coupling buckets`](../../extra/discussion/wind/02_coupling_buckets_and_wind.md),
[`03 hazard definition`](../../extra/discussion/wind/03_hazard_definition_and_thresholds.md)).

---

## DD-WN-13 · Never the expected-loss shortcut (Method 0) — every metric off one sampled distribution

**Date:** 2026-06-13 · **Status:** decided (v1) · *to realize in M4* · doctrine: [`principles/basics_spot_on`](../../principles/basics_spot_on.md).

**Context.** The old repo stored each event's loss as `damage% × value × spatial_factor` — the expected loss
*averaged over* the hit/miss draw, not a realized sample — then fit a distribution to annual sums. By the Law of
Total Variance this preserves the mean (EAL) but **discards the dominant bimodal variance**, understating the tail.
Its *own* worked example (`strong-wind-var-worked-example.md`) shows Method 0 vs the correct compound-Poisson
Method 3 differ by **~12×** at VaR₉₉ ($9M vs $109M) **for strong wind specifically** — and PML/VaR fit as two
incoherent objects produced an impossible **~175×** invariant breach.

**Decision.** **Refuse Method 0.** Every wind metric — EAL/VaR/PML/TVaR — is read off **one** coherent
compound-Poisson/NegBin Monte-Carlo loss distribution ([DD-WN-12](#dd-wn-12--metrics-off-one-shared-compound-poissonnegbin-monte-carlo--of-tiv-alongside-dollars)),
stochastic kept stochastic past every nonlinearity, verified against a known-answer example.

**Why.** It is the cardinal error the entire rebuild exists to escape, and it is **worst exactly where wind is
worst**: at high frequency (strong wind) the gap is ~12×; at low frequency (tornado) Method 0 is "wrong but
harmless on small numbers" but the sampled distribution still floors VaR to $0 (Poisson floor) — which is *why*
TVaR must be reported alongside VaR for tornado. EAL alone survives Method 0 (linearity of expectation), so EAL
agreement is no proof of correctness.

**Revisit trigger.** None — this is a doctrine, not a tunable choice.

---

## DD-WN-12 · Metrics off one shared compound-Poisson/NegBin Monte-Carlo; % of TIV alongside dollars

**Date:** 2026-06-13 · **Status:** decided (v1) · *to realize in M4*.

**Context.** Hail and wildfire both read EAL/VaR/PML/TVaR off the **same** sampled compound engine; only the
per-year sampling differs. Wind must not introduce a second engine.

**Decision.** Wind reuses the **shared compound-Poisson/NegBin Monte-Carlo engine unchanged**. Strong wind samples
a site-conditioned rate (Poisson, well-populated tail); tornado samples a thinned areal rate (Poisson, sparse tail).
All risk metrics are reported as **% of TIV alongside the dollar value** (the platform convention) — never dollars
alone, because a number without its base is uninterpretable.

**Why.** *Modular from day one* — growth is by feeding the engine a new typed object, not editing it. The
low-vs-high site contrast (Shepherds Flat vs Traverse) pays off on one unchanged engine, exactly as Hayhurst vs
Matrix did for wildfire.

**Revisit trigger.** Portfolio correlation (multiple wind farms sharing a strong-wind swath) → a correlation /
dispersion term enters the sampling, still behind the same `draw_count()` interface.

---

## DD-WN-11 · Turbine damage = anchored subsystem logistic on 3-s gust; IEC-survival onset; operational-state aware; approximate

**Date:** 2026-06-13 · **Status:** decided (v1) · *to realize in M3*.

**Context.** M3 needs a 3-s-gust → damage curve for a turbine. The old repo had **no turbine-specific wind
fragility**: strong wind and hail borrowed generic `Real Estate_*` curves, and gust events were silently routed
onto the Tornado curve — a hack, not a curve. The reference's explicit mandate: *"for wind turbines, account for
operational state (feathered vs operating) and the survival wind speed in the curve, not just the design speed."*

**Decision.** Build an **anchored** curve: a capex-weighted blend of **subsystem** logistics (old-repo cost split —
rotor/blades ~0.26, nacelle/drivetrain ~0.21, tower ~0.16, foundation ~0.12, substation ~0.09, electrical ~0.09,
civil ~0.07), each on the **3-s gust** axis, with `DR(μ) ≈ 0` at the meteorological threshold and a **steep rise
near the IEC 61400 survival speed** (Ve50 ≈ 1.4·Vref ≈ 52–70 m/s). Note **operational state** (a feathered turbine
survives more than an operating one) as a curve modifier. Subsystem reach differs by sub-peril: strong wind loads
the **aero** subsystems (rotor, nacelle); a tornado reaching EF-level speeds also takes the **tower**. **Approximate
/ temporary** (Low confidence; the curve is the dominant, irreducible uncertainty — honest now, accurate later).

**Why.** Right axis (3-s gust), turbine-structured, IEC-anchored — anchoring removes the non-physical floor the
old generic logistics carried (`DR(μ) > 0` with no real damage). It encodes the **two-threshold** reality
([DD-WN-7](#dd-wn-7--two-thresholds-kept-distinct--meteorological-event-vs-asset-damage-onset)): most "severe wind"
(just over 58 mph) barely scratches a turbine; damage onset is far higher, at the IEC survival speed.

**Revisit trigger.** A calibrated, RE-specific turbine fragility curve (with explicit operational-state branches and
a conditional-DR *distribution*) ships in `infrasure-damage-curves`.

---

## DD-WN-10 · Two sites — Traverse OK (high/proving) vs Shepherds Flat OR (low/baseline)

**Date:** 2026-06-13 · **Status:** decided (v1) · *to realize in M0*.

**Context.** Hail and wildfire each used a low-vs-high pair to validate the model across an exposure range. Wind
needs the same: a site that should show a *material* convective-wind tail and one that should show near-zero.

**Decision.** **HIGH / proving = Traverse Wind Energy Center, Oklahoma (~999 MW)** — tornado-alley + derecho
corridor. **LOW / baseline = Shepherds Flat, Oregon (~845 MW)** — Columbia River Gorge, minimal tornado/derecho.
Areal footprint from the renewablesinfo boundary DB (OSM/EIA polygons); per-turbine point locations from **USWTDB**.

**Why.** Two real, large onshore farms across a wide convective-wind exposure range exercise both sub-perils' tails
on one engine. *Caveat:* both sites are **rural**, where SPC's EF rating is biased low (damage-inferred, capped by
the strongest damage indicator present) — so historical severity is likely understated at both
([AWN-1](assumptions.md)); flag, don't ignore.

**Revisit trigger.** A portfolio view (correlated strong-wind swath across multiple farms) or an offshore/coastal
asset (which would pull in the deferred hurricane field).

---

## DD-WN-9 · Hurricane / field-intensity (bucket 2) deferred — the genuinely unbuilt coupling type

**Date:** 2026-06-13 · **Status:** decided (v1, deferred) · Evidence: [`02 coupling buckets`](../../extra/discussion/wind/02_coupling_buckets_and_wind.md).

**Context.** Wind spans all three coupling buckets. Tornado = areal (bucket 1, reuses hail); strong wind =
site-conditioned (bucket 3, reuses wildfire). **Hurricane = field-intensity (bucket 2)** — a single event produces a
*continuous wind field over space* (no hit-or-miss), and unlike strong wind it is **not** pre-integrated into a site
profile: it builds a genuine per-event swath (Holland parametric wind field along a track), so every asset reads the
field value at its location, event by event.

**Decision.** **Defer hurricane.** V1 = inland-convective only. Name field-intensity explicitly as the future build:
public stochastic track catalog (STORM / RAFT) → **Holland wind field → swath grid → hurricane-wind curve
(x₀ ≈ 160 mph)** — and name *where* the new machinery becomes load-bearing: **portfolio correlation** (one storm
hits many assets together) and **EVT on the field tail** (extrapolating beyond the catalog return period).

**Why.** It is the one bucket the platform has not built — the biggest, coastal, field-intensity build — so it is
deferred *deliberately* to keep V1 buildable now on machinery we already own. *Modular from day one:* document the
wall + the migration path, don't build past it.

**Revisit trigger.** A coastal / offshore asset enters scope, or a portfolio of farms needs correlated wind-field
loss → stand up the field-intensity coupling as bucket 2.

---

## DD-WN-8 · Severity = bounded GPD on 3-s gust, truncated at L ≈ 113 m/s (EF5); ASCE RP surface = the pre-fit EVT curve

**Date:** 2026-06-13 · **Status:** decided (v1) · *to realize in layer-0 / M1* · doctrine: [`hazard_math/05`](../../../Learning/ML-DL/InfraSure_related/hazard_math/05_extreme_value_theory_tail_modeling.md).

**Context.** Wind severity is **continuous** magnitude (3-s gust) — *unlike* wildfire's 6 discrete FLP classes — so
wind cashes in the continuous-severity thread. EVT theory (note 05) says: prefer EVT **on magnitude/intensity** (then
map through the damage curve), and the shape parameter governs the tail — **ξ < 0 ⇒ bounded with a finite upper
endpoint**. A single turbine's physical damage is bounded; gust speed is physically bounded too.

**Decision.** Model gust magnitude above the event threshold μ with a **bounded GPD** — left-anchored at μ,
right-truncated at the physical bound **L ≈ 113 m/s (the EF5 ceiling, ~253 mph)** — giving **ξ < 0** (short upper
tail). Reuse the old repo's **analytic parameter solve** (`ξ = (μ_mean − μ)/(μ_mean − L)`, `σ = −ξ(L − μ)`), but
**fit μ_mean to observed gusts (SPC / Storm-Events)**, *not* back-solved from an NRI EAL target (the old repo's
weakness). For the strong-wind spine, the **ASCE RP→gust surface IS the pre-computed EVT return-level curve** —
ASCE/NIST already did the tail extrapolation — so reading several MRI maps = sampling the return-level function at
fixed exceedance probabilities; no separate fit needed.

**Why.** EVT-on-intensity is the right object (hazard observations are more available than asset-loss data; one
hazard tail feeds many asset curves). The bounded form is *correct physics* — do not assume ξ > 0 / unbounded for a
single bounded asset. *Reconcile:* the old repo used tornado L = 145 m/s (observed Doppler max); V1 adopts the EF5
damage-inferred ceiling 113 m/s as L — settled in layer-0. Flag the RP convention (empirical-Weibull vs EVD-fitted)
because it materially moves the PML/VaR tail.

**Revisit trigger.** A credible measured-gust record long enough to fit the tail directly, or a need for the
very-long-MRI tail (ASCE Appendix F, out to ~10⁴–10⁶-yr) driving a critical-asset decision.

---

## DD-WN-7 · Two thresholds, kept distinct — meteorological event (NWS ≥ 58 mph / EF) vs asset damage-onset (IEC survival)

**Date:** 2026-06-13 · **Status:** decided (v1) · *to realize in layer-0* · Evidence: [`03 hazard definition`](../../extra/discussion/wind/03_hazard_definition_and_thresholds.md).

**Context.** Wind has two natural thresholds that are easy to conflate — and conflating them is a modeling error.
The **meteorological** threshold is what the *catalog counts* (it sets λ); the **asset damage-onset** threshold is
where the *damage curve leaves zero*. They are far apart: a turbine is engineered to survive most "severe" wind.

**Decision.** Keep them **distinct**:
- **Event-count threshold μ (what the catalog counts, for λ).** Convective severe wind = **≥ 58 mph (≈ 25.9 m/s)** —
  the NWS severe-thunderstorm criterion (exactly the old repo's 25.92 m/s). Tornado = **EF scale** (EF0 65–85 / EF1
  86–110 / EF2 111–135 / EF3 136–165 / EF4 166–200 / EF5 > 200 mph, 3-s gust, damage-inferred via 28 damage
  indicators × 8 degrees of damage).
- **Damage-onset threshold (where the curve leaves zero).** Turbine **survival / design speed from IEC 61400** —
  wind classes I/II/III reference Vref = 50 / 42.5 / 37.5 m/s (10-min mean); the 50-yr extreme 3-s gust
  Ve50 ≈ 1.4·Vref ≈ 52–70 m/s. `DR(μ) ≈ 0`; the curve rises steeply only near IEC survival ([DD-WN-11](#dd-wn-11--turbine-damage--anchored-subsystem-logistic-on-3-s-gust-iec-survival-onset-operational-state-aware-approximate)).

**Why.** The catalog must count *events* (frequency) at the meteorological threshold, while the damage curve must
start at the *physical* onset — otherwise we'd either miss events (too high a count threshold) or invent damage
that isn't there (too low a damage onset, the old generic-curve floor). *Honest label:* the EF bins, the 58 mph
threshold, and the 3-s-gust metric come from the Hazard-Data-Reference; **IEC 61400 / Vref classes / the EF5
≈ 113 m/s ceiling come from the settled framing + old-repo HAZARD_LIMITS, not from that reference** — labeled as
such.

**Revisit trigger.** A turbine-specific operational-state survival curve (feathered vs operating) refines the
damage-onset threshold, or a revised EF scale changes the event bins.

---

## DD-WN-6 · Hazard observable = 3-second peak gust wind speed (the universal metric)

**Date:** 2026-06-13 · **Status:** decided (v1) · *to realize in layer-0*.

**Context.** A wind hazard "is not a single number" — we must pick the magnitude metric the vulnerability curve is
built around. Candidates: 10-min mean (IEC design basis), sustained vs gust, hub-height vs 33-ft reference.

**Decision.** The hazard observable is the **3-second peak gust wind speed**, at hub height for the asset-incident
value — the reference's *"universal metric — map it to a wind-load / fragility curve per asset."* The ASCE basic
wind maps are 3-s gust at 33 ft, Exposure C; the EF scale is a 3-s gust estimate; the damage curve is built on 3-s
gust. Do **not** replicate the old repo's gust-vs-sustained curve-swap hack (it silently routed gust events to the
Tornado curve and sustained to the Strong-Wind curve).

**Why.** One coherent metric across catalog, coupling, and damage. It is the cross-standard lingua franca (ASCE, EF,
NWS all in 3-s gust), so it lets a single fragility curve serve every wind sub-peril.

**Revisit trigger.** A sub-peril whose damage is governed by sustained loading or duration (e.g. fatigue) rather
than peak gust — then add a second observable behind the interface.

---

## DD-WN-5 · Tornado coupling = areal hit-or-miss (bucket 1) — reuse hail's Minkowski, path-aware thin rectangle

**Date:** 2026-06-13 · **Status:** decided (v1) · *to realize in M2* · Evidence: [`02 coupling buckets`](../../extra/discussion/wind/02_coupling_buckets_and_wind.md).

**Context.** A tornado has a **narrow, intense path** — *"low strike probability at any point, but near-total loss
within the path."* The design concern is **strike probability × effective plan area**. This is physically hail's
areal hit-or-miss, not a continuous field.

**Decision.** Tornado coupling = **areal hit-or-miss** (bucket 1), **reusing hail's Minkowski-sum coupling** in a
**path-aware variant**: a tornado path is a thin rectangle (extreme aspect ratio L ≫ w), so the Minkowski overlap
`(L+a)(w+a)` is dominated by **path length × asset extent** — a long/linear asset has many times the strike exposure
of a point. `λ_asset = λ_collection × p_hit` via Poisson thinning. Reuse the old repo's EF-class **areas**
(EF0 0.5 → EF5 20 km²) and **midpoints** for the path geometry. Per-turbine point-cloud (USWTDB) vs areal-footprint
distinction noted: a point lookup understates an areal/linear asset.

**Why.** It is the *standard physics* match — importing a field model here would be wrong, and reusing wildfire's
site-conditioned machinery would erase the hit-or-miss bimodality (the variance Method 0 destroyed). Tornado is
**rare per site** → sparse Monte Carlo → it exercises the effective-sample-size discipline
([learning_logs/10](../../learning_logs/10_monte_carlo_effective_sample_size.md)): report SE, use a
precision-matched known-answer tolerance, and report **TVaR alongside VaR** (VaR floors to $0 in the sparse tail).

**Revisit trigger.** A portfolio of turbines/farms where path-correlated multi-turbine strikes matter, or the ASCE
Ch 32 tornado design surface (a pre-integrated tornado RP, capped ~EF2) is adopted as a cross-check.

---

## DD-WN-4 · Strong-wind coupling = site-conditioned (bucket 3) — reuse wildfire's thin M2

**Date:** 2026-06-13 · **Status:** decided (v1) · *to realize in M2* · Corroborated by [`02 coupling buckets`](../../extra/discussion/wind/02_coupling_buckets_and_wind.md).

**Context.** Strong / straight-line convective wind is a **broad swath** (thunderstorm outflow, derecho, downburst,
synoptic high wind) — *"broad-area, so most/all of a portfolio is exposed simultaneously."* There is no hit-or-miss:
the asset is not missed, it **reads its local gust**. The reference: *"the ASCE design wind-speed map IS the surface
— sample the return-period 3-s gust at each asset… broad-area, so most/all of a portfolio is exposed simultaneously
(correlated loss)."*

**Decision.** Strong-wind coupling = **site-conditioned** (bucket 3), **reusing wildfire's thin M2 machinery**. M1
already produces `(λ, conditional gust severity)` at the asset from the pre-integrated profile
([DD-WN-3](#dd-wn-3--strong-wind-m1--profile-assembly-from-the-asce-rp-surface-pre-integrated-no-fit)); M2 is a
deliberately thin layer (no Minkowski overlap, no spatial factor) — we *document* the thinness rather than
manufacture coupling that isn't there.

**Why.** *Standard interface, not standard physics:* the physics differs from tornado (continuous field vs
hit-or-miss) but it is *identical* to wildfire's site-conditioned read — so reuse, don't reinvent. High frequency →
**well-populated Monte-Carlo tail** (the Matrix analogue), in deliberate contrast to tornado's sparse tail.

**Revisit trigger.** A portfolio where the broad-swath correlation across multiple farms must be modeled explicitly
(a correlation term in M2/M4, still behind the shared engine).

---

## DD-WN-3 · Strong-wind M1 = profile-assembly from the ASCE RP surface (pre-integrated; no λ-fit) — the wildfire analogue

**Date:** 2026-06-13 · **Status:** decided (v1) · *to realize in M1* · doctrine: [`learning_logs/09`](../../learning_logs/09_pre_integrated_vs_extracted_catalog.md).

**Context.** Learning-09's test: *classify the hazard by how its data arrives before choosing M1's machinery — does
the source give a probability / return-period, or a count / observation series?* For strong wind there is **no public
stochastic catalog** (operational ones are proprietary: Verisk, Moody's RMS). But the **ASCE 7-22 design-wind map
already embeds a probabilistic return-period analysis** — *"the RP surface exists even though a downloadable event
set does not."*

**Decision.** Strong-wind M1 = **profile-assembly** from the **ASCE 7-22 return-period 3-s-gust surface** — read the
per-site gust-by-MRI directly (RC I 300-yr / II 700-yr / III 1,700-yr / IV 3,000-yr; Appendix F out to ~10⁴–10⁶-yr).
The RP→gust relationship *is* the pre-computed EVT return-level curve. **No λ-fit, no dispersion test, no spatial
factor** — exactly as FSim's BP was pre-integrated for wildfire. The **extraction alternative** (fit Poisson
occurrence + bounded-GPD gust severity to the bias-corrected SPC / Storm-Events record) is the documented
cross-check, not the V1 spine.

**Why.** *Pre-integration is a borrow, not a free lunch:* we inherit ASCE/NIST's assumptions, vintage, and terrain-
exposure basis (Exposure C reference; terrain B/D adjust) and cannot re-test them — but it is the fastest path to a
real number (the FSim lesson), and it is the *correct* M1 machinery for a pre-integrated source. Honesty = the
uncertainty moved upstream, not vanished.

**Revisit trigger.** A public stochastic convective-wind catalog appears, or the ASCE vintage / terrain basis is
materially wrong for a site → switch to (or cross-check against) the SPC extraction path.

---

## DD-WN-2 · Route = inland-convective (strong wind then tornado); hurricane deferred; the hazard/performance scope boundary

**Date:** 2026-06-13 · **Status:** decided · Evidence: [`01 scope/taxonomy`](../../extra/discussion/wind/01_scope_and_sub_peril_taxonomy.md).

**Context.** Wind is a sub-peril family ([DD-WN-1](#dd-wn-1--wind-is-a-sub-peril-family-split-on-the-dual-test-footprint-and-data-metric)) spanning all three coupling buckets. We must
pick which sub-perils to build first, and draw the hazard-vs-performance line (because for wind the hazard medium IS
the resource medium).

**Decision.** V1 route = **inland-convective**: build **strong / straight-line wind first** (site-conditioned, ASCE
RP surface hands the hazard pre-integrated → fastest real number), **then tornado** (areal, path-strike geometry +
the rare catastrophic tail). **Hurricane / tropical cyclone = deferred**
([DD-WN-9](#dd-wn-9--hurricane--field-intensity-bucket-2-deferred--the-genuinely-unbuilt-coupling-type)). And draw the
**hard scope boundary**: hazard-tier wind = **extreme wind that structurally damages the turbine → physical loss
(THIS repo)**; performance-tier wind = **the wind resource driving generation/revenue (sibling `model-gpr`)**.

**Why.** Strong wind first because the ASCE RP surface is pre-integrated (the FSim parallel — fastest path to a
number); tornado second because path-strike geometry + the rare tail are a harder, sparser build. Inland-convective
tours **two already-built coupling types**, leaving only field-intensity (hurricane) for later. The scope boundary
must be *stated* because for wind it blurs — for solar (sun ≠ hail) it was obvious.

**Revisit trigger.** Hurricane enters scope (coastal/offshore asset), or a performance-tier need crosses into
structural damage (it shouldn't — that's the line).

---

## DD-WN-1 · Wind is a sub-peril family — split on the dual test (footprint AND data metric)

**Date:** 2026-06-13 · **Status:** decided · Evidence: Hazard-Data-Reference sub-peril split test; [`principles/hazard_asset_specificity`](../../principles/hazard_asset_specificity.md) dual test.

**Context.** "Wind" is not one peril. The reference splits **Tornado [T]** (rotating vortex) from **Strong / straight-
line wind [W]** on **footprint geometry**, and treats hurricane as its own peril. The sub-peril split test requires
**both** axes: (1) a genuinely **distinct physical footprint** (*"a stronger vs weaker gust is one system; a rotating
vortex vs a straight-line field is two"*), and (2) a **distinct data / magnitude metric**.

**Options.** A: one "wind model" with a single coupling (✗ — would force one spatial logic onto narrow-path and
broad-swath alike, the error the reference explicitly warns against). B: split per the dual test into sub-perils,
each dispatched to its own coupling bucket (✓).

**Decision.** **Option B.** Treat wind as a **sub-peril family**: tornado (areal hit-or-miss, bucket 1), strong wind
(site-conditioned, bucket 3), hurricane (field-intensity, bucket 2, deferred). Each emits the **same typed event
record / hazard distribution** to the shared engine; only the coupling physics differs.

**Why.** It is the dual test applied honestly, and it is the *"sub-perils matter"* payoff: the family spans all three
coupling buckets, so building wind tours coupling types the platform already owns. *Standard interface, not standard
physics* — specialize the physics per sub-peril, standardize the interface; don't over-split where the mechanism is
the same (tornado *is* hail's areal; strong wind *is* wildfire's site-conditioned), don't under-split where it
genuinely differs.

**Revisit trigger.** A new wind sub-peril is requested (hail-on-turbine, lightning, ice/rime, winter storm) — apply
the dual test; if it passes, stand it up as its own coupling row, reusing whichever bucket fits.
