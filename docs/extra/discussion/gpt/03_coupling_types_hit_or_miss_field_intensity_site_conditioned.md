# 03 — Coupling Types: Hit-or-Miss vs Field Intensity vs Site-Conditioned

## Core distinction

These three are **three different ways the hazard connects to the asset before you apply the damage curve**.

They are coupling types: **how the hazard reaches the asset**.

They are different from exposure geometry, which is the shape of the asset: point, area, line, or portfolio.

The shortest version:

```text
hit-or-miss      = Did the event touch the asset?
field intensity  = What intensity did the asset experience?
site-conditioned = What local site level did the event create?
```

---

## 1. Big picture

Before loss, the adapter/coupling module is trying to produce something like this:

```text
hazard event + asset
        │
        v
coupling calculation
        │
        v
intensity / exposed fraction / local level at asset
        │
        v
damage curve
        │
        v
event loss
```

The three coupling types differ in the **middle step**.

```text
Areal hit-or-miss:
    event footprint overlaps asset?
    yes/no, or exposed fraction

Field intensity:
    read the hazard intensity at the asset
    temperature, wind speed, ground motion, etc.

Site-conditioned:
    compute the local site condition caused by the event
    flood depth, flame exposure, distance/intensity, etc.
```

---

## 2. Comparison table

| Coupling type | Plain-English question | Is there a “miss”? | Main input | Example hazards | Damage driver |
|---|---|---:|---|---|---|
| **Areal hit-or-miss** | Did the event footprint overlap the asset? | Yes | Event footprint / swath / path | Hail, tornado, convective wind | Conditional-on-hit severity |
| **Field intensity** | What intensity did the asset experience? | No, not in the same sense | Site intensity from a field | Heat, cold, synoptic wind, earthquake | Intensity → response/damage |
| **Site-conditioned** | What local level occurred at this specific site? | No spatial-factor miss | Local level after site conditioning | Flood depth, wildfire exposure | Level → component vulnerability |

---

## 3. Type 1: areal hit-or-miss

This is the easiest one to understand.

A hazard event has a **footprint**:

```text
hail swath
tornado path
convective wind footprint
```

The asset may or may not be inside that footprint.

```text
MISS

+--------------------------------+
|                                |
|     ########                   |
|     ########                   |
|                         A      |
|                                |
+--------------------------------+

A = asset
# = hazard footprint

Result:
    event happened regionally
    but it did not hit the asset
    event_loss = 0
```

```text
HIT

+--------------------------------+
|                                |
|              ########          |
|              ####A###          |
|              ########          |
|                                |
+--------------------------------+

Result:
    event hit the asset
    now use conditional severity
```

So for hit-or-miss hazards, the first question is:

```text
Did this event reach the asset?
```

Then, only if it reaches the asset, you ask:

```text
Given that it hit, how bad was the intensity?
Given that intensity, what damage ratio?
```

For a point asset:

```text
hit_probability ≈ event_footprint_area / search_area
```

For an area asset like a solar farm:

```text
hit_probability is not enough;
you may also need exposed_fraction
```

Example:

```text
Hail swath covers 40% of solar farm.
Hail size at exposed area = 55 mm.
Damage curve says 55 mm -> 15% damage ratio.
Loss applies to exposed part / affected components.
```

So the event-loss logic looks like:

```text
for each regional hail event:
    sample hit_or_miss

    if miss:
        event_loss = 0

    if hit:
        intensity = hail_size_at_asset
        damage_ratio = damage_curve(intensity)
        event_loss = damage_ratio × exposed_value
```

This is where the **spatial factor** belongs. It is a **hit probability**, not a damage haircut.

Very important:

```text
Correct:
    97% chance loss = 0
     3% chance loss = $50M

Incorrect shortcut:
    every event loss = 3% × $50M = $1.5M
```

The shortcut may preserve EAL, but it kills the tail because the rare big hit disappears.

---

## 4. Type 2: field intensity

Field intensity is different.

Here the hazard is not mainly a small footprint that either hits or misses. Instead, the asset is sitting inside a broader **hazard field**.

Think of a weather map:

```text
Temperature field

+-----------------------+
|  34°C   35°C   36°C   |
|  35°C    A     39°C   |
|  36°C   38°C   40°C   |
+-----------------------+

A = asset
```

The asset does not ask:

```text
Did the heat wave overlap me?
```

It asks:

```text
What temperature did I experience?
How long did I experience it?
```

So the coupling output is not a hit/miss flag. It is a site intensity:

```text
I_site = 39°C
```

Then the damage or response model says:

```text
39°C -> 8% production derating
or
39°C for 5 days -> revenue loss
```

For field intensity hazards, the logic is more like:

```text
for each simulated year:
    draw/read site intensity process

    intensity = value_of_field_at_asset

    if intensity below threshold:
        loss = 0 or small

    if intensity above threshold:
        loss = response_curve(intensity, duration)
```

Examples:

```text
Heat:
    local temperature / duration -> derating -> revenue loss

Cold:
    local temperature -> freeze vulnerability -> loss

Synoptic wind:
    site wind speed -> damage curve -> loss

Earthquake:
    site ground motion -> fragility/damage -> loss
```

There can still be zero loss, but the reason is different.

For hit-or-miss:

```text
zero loss because the event missed
```

For field intensity:

```text
zero loss because the experienced intensity was not damaging
```

That distinction matters.

ASCII:

```text
Hit-or-miss:
    event may not touch asset at all

Field intensity:
    asset has an intensity value every time;
    the value may be harmless or damaging
```

---

## 5. Type 3: site-conditioned

Site-conditioned is the subtle one.

It can look similar to field intensity because both involve a value at the site. But the modeling story is different.

In **site-conditioned** coupling, the loss is controlled by a **local level produced at that site**, often after local terrain, elevation, protection, drainage, fuel, or distance effects are considered.

The cleanest example is flood.

A regional storm happens. But the asset loss is not determined just by:

```text
did the storm footprint touch us?
```

And not simply:

```text
what was the rainfall intensity over the region?
```

The key question is:

```text
what flood depth occurred at this asset?
```

ASCII:

```text
Rain / river event
        │
        v
hydrology + hydraulics + site elevation
        │
        v
local flood depth at asset
        │
        v
damage curve
```

Or visually:

```text
             water surface
        ~~~~~~~~~~~~~~~~~~~~~
                ↑
                │  flood depth at asset
                ↓
        ┌───────────────┐
        │ equipment     │
        └───────────────┘
        ground / pad elevation
```

So for flood:

```text
local_depth = water_surface_elevation - asset_elevation

if local_depth <= 0:
    event_loss = 0

if local_depth > 0:
    damage_ratio = flood_depth_damage_curve(local_depth)
    event_loss = damage_ratio × exposed_value + downtime/BI
```

This is not hit-or-miss because we are not mainly using:

```text
regional event rate × footprint overlap probability
```

We are using:

```text
site water-level / depth distribution
```

For wildfire, site-conditioned might mean:

```text
distance to flame front
ember exposure
fuel around asset
local flame intensity
defensible space
```

The regional wildfire perimeter matters, but the loss is conditioned by the local site exposure.

---

## 6. Why site-conditioned is not just field intensity

This is probably the part that can feel confusing.

Both field intensity and site-conditioned models may produce a local number:

```text
field intensity:
    local temperature = 42°C
    local wind speed = 95 mph
    local ground motion = 0.35g

site-conditioned:
    local flood depth = 3 ft
    local wildfire exposure = high
```

The difference is how that local number is generated and what it means.

### Field intensity

The hazard itself is naturally a field.

```text
temperature field
wind-speed field
ground-motion field
```

The asset reads the field value at its location.

```text
field value at asset -> response curve
```

Example:

```text
Heat wave:
    temperature at solar farm = 43°C
    derating curve says output drops by X%
```

### Site-conditioned

The hazard creates a local condition after interacting with site-specific features.

```text
regional rainfall + river + drainage + elevation -> flood depth at asset
wildfire perimeter + fuels + distance + wind -> local exposure at asset
```

The site transforms the event into a local level.

```text
event + site conditions -> local level -> vulnerability curve
```

Example:

```text
Flood:
    regional rainfall is not enough.
    The asset loss depends on actual water depth at the asset.
```

So:

```text
Field intensity:
    read the field at the asset.

Site-conditioned:
    compute the site outcome caused by the event.
```

Or even shorter:

```text
Field intensity = "what did the map say at my location?"
Site-conditioned = "what did my specific site conditions turn the event into?"
```

---

## 7. One toy example for the same asset

Suppose the asset is a $100M solar farm.

### Hail: areal hit-or-miss

```text
Regional hail event occurs.
Does hail swath overlap solar farm?

No:
    loss = $0

Yes:
    hail size = 60 mm
    damage curve says 20%
    loss = $20M
```

Model shape:

```text
losses are jumpy:
    many zeros
    occasional large losses
```

### Heat: field intensity

```text
Heat wave occurs.
Solar farm is inside the temperature field.

Temperature at site = 44°C
Duration = 5 days
Derating curve says lost revenue = $1.2M
```

Model shape:

```text
losses are often smoother:
    low heat -> small/no loss
    extreme heat -> larger derating/revenue loss
```

### Flood: site-conditioned

```text
Flood event occurs.
Hydraulic model says depth at solar farm = 2.5 ft.

Flood damage curve says 35%
Physical loss = $35M
Downtime adds BI loss
```

Model shape:

```text
loss depends heavily on local level:
    depth below pad -> zero
    depth into equipment -> large
```

---

## 8. The three as formulas

These are not exact production formulas, but they are good mental formulas.

### Areal hit-or-miss

```text
H_i ~ Bernoulli(p_i)

if H_i = 0:
    L_i = 0

if H_i = 1:
    L_i = damage_curve(intensity_i) × exposed_value
```

Where:

```text
p_i = hit probability / overlap probability
```

The key random variable is:

```text
H_i = did it hit?
```

---

### Field intensity

```text
I_t = site intensity in year/event/day t

L_t = response_curve(I_t, duration_t)
```

The key random variable is:

```text
I_t = intensity experienced at the asset
```

There is no separate spatial-factor coin flip.

---

### Site-conditioned

```text
Z_t = local site level caused by event t

L_t = vulnerability_curve(Z_t)
```

For flood:

```text
Z_t = flood depth at asset
```

For wildfire:

```text
Z_t = local flame/ember exposure or distance/intensity measure
```

The key random variable is:

```text
Z_t = local level at this site
```

---

## 9. Why this matters for EAL/VaR

The coupling type controls the shape of the annual loss distribution.

```text
Areal hit-or-miss:
    lots of zeros + rare big jumps
    tail depends heavily on hit/miss randomness

Field intensity:
    losses follow site intensity distribution
    tail depends on extreme intensity/duration

Site-conditioned:
    losses follow local-level distribution
    tail depends on extreme local depth/exposure
```

So if we use the wrong coupling type, we build the wrong annual loss vector.

The classic error is using this for everything:

```text
loss = spatial_factor × conditional_loss
```

That only makes sense as an **expectation shortcut** for areal hit-or-miss. It is not the real event loss, and it is especially wrong for field intensity and site-conditioned hazards.

---

## 10. Best memory hook

Use this:

```text
Hail / tornado:
    "Did the footprint hit me?"

Heat / synoptic wind / earthquake:
    "What intensity did I experience?"

Flood / wildfire:
    "What local site level did the event create?"
```

And the deeper modeling rule:

```text
hit-or-miss:
    frequency = regional event rate × hit probability
    severity = conditional on hit

field intensity:
    frequency/intensity comes from site intensity process
    severity = intensity response curve

site-conditioned:
    frequency/level comes from local site-level distribution
    severity = level/component vulnerability curve
```

So yes, they are all “how hazard reaches asset,” but they are **three different physical stories**, and each one produces the event loss in a different way before everything fans back into the same common `event_record`.
