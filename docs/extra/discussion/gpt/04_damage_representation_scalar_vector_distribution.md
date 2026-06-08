# 04 — Damage Representation: Scalar, Vector, and Distribution

## Core idea

In the **damage section**, “scalar / vector / distribution” is about **what the damage stage hands to the next stage after it has seen the hazard intensity at the asset**.

Severity is the size of loss given that an event affects the asset, and it is really a distribution, not just one number. The bridge from hazard intensity to loss is the damage/vulnerability curve.

The core question is:

```text
Given this event reached the asset at this intensity,
what should the damage stage emit?

Option A: one mean number?
Option B: a vector of possible damage states?
Option C: a full distribution of possible damage ratios?
```

---

## 1. First-principles view

Imagine a hail event reaches a solar farm.

```text
Hazard event:
    hail size at asset = 60 mm

Asset:
    solar farm
    asset value = $150M

Damage stage asks:
    What damage ratio should 60 mm hail produce?
```

A simple damage curve might say:

```text
60 mm hail -> 20% mean damage ratio
```

But real life is not exactly:

```text
every 60 mm hail event causes exactly 20% damage
```

Real life is more like:

```text
60 mm hail could cause:
    little damage at one site,
    moderate damage at another,
    severe damage at another,
depending on module type, angle, stow, tracker position, hail hardness,
wind direction, panel age, maintenance, etc.
```

So at the same intensity, there is a spread of possible outcomes.

That spread is what “scalar / vector / distribution” is trying to represent.

---

## 2. The pipeline location

You are here:

```text
hazard event
    │
    v
coupling / geometry
    │
    └──> intensity at asset, exposed fraction
              │
              v
        DAMAGE STAGE
              │
              ├── scalar mean damage ratio
              ├── damage-state vector
              └── full damage distribution
              │
              v
        event loss generation
              │
              v
        annual loss vector
              │
              v
        EAL / VaR / PML / TVaR
```

So this is **not yet the annual loss distribution**.

This is the **event-level damage representation**.

---

## 3. Scalar damage ratio

A **scalar** means one number.

Example:

```text
hail size = 60 mm
damage ratio = 20%
asset value = $150M

event physical loss = 20% × $150M = $30M
```

ASCII:

```text
60 mm hail
   │
   v
damage curve
   │
   v
20% damage ratio
   │
   v
$30M event loss
```

This is the simplest version.

| Representation | Meaning |
|---|---|
| Scalar | One mean damage ratio |
| Example | `damage_ratio = 0.20` |
| Good for | EAL, rough screening |
| Weakness | It loses the spread of outcomes |

The danger is that it treats the mean as the actual outcome.

But the true situation may be:

```text
same 60 mm hail:
    30% chance:  5% damage
    40% chance: 20% damage
    20% chance: 40% damage
    10% chance: 80% damage
```

The average might be around 25%, but VaR/PML care about the 40% and 80% cases. If we only carry the mean, we understate tail uncertainty.

That is why a scalar mean damage ratio is **fine for EAL but weak for tail metrics because there is no spread**.

---

## 4. Mean + uncertainty

This is one step richer than scalar.

Instead of saying:

```text
damage ratio = 20%
```

we say:

```text
mean damage ratio = 20%
uncertainty/spread = some parameter
```

For example:

```text
damage_ratio ~ Beta distribution with mean 20%
```

or conceptually:

```text
damage ratio is centered around 20%,
but actual sampled damage can be 5%, 15%, 35%, 60%, etc.
```

ASCII:

```text
60 mm hail
   │
   v
damage curve
   │
   v
mean = 20%, spread = medium
   │
   v
sample actual damage:
   year/event 1 -> 12%
   year/event 2 -> 31%
   year/event 3 -> 18%
   year/event 4 -> 55%
```

This is better for VaR/PML because the simulation can sample different actual outcomes instead of using the same mean every time.

| Representation | Meaning |
|---|---|
| Mean + uncertainty | Mean damage ratio plus dispersion |
| Example | `mean = 20%, sigma = 10%` |
| Good for | Simulation with secondary uncertainty |
| Weakness | You must assume a distribution shape |

This is better than scalar, but it assumes a parametric uncertainty form.

---

## 5. Damage-state vector

A **vector** means a list of probabilities across discrete damage states.

This usually comes from **fragility curves**.

Instead of saying:

```text
60 mm hail -> 20% damage
```

we say:

```text
60 mm hail -> probabilities of damage states
```

Example:

```text
damage_state_vector = {
    none:      20%
    slight:    30%
    moderate:  30%
    extensive: 15%
    complete:   5%
}
```

ASCII:

```text
60 mm hail
   │
   v
fragility curves
   │
   v
┌────────────┬─────────────┐
│ State      │ Probability │
├────────────┼─────────────┤
│ None       │ 20%         │
│ Slight     │ 30%         │
│ Moderate   │ 30%         │
│ Extensive  │ 15%         │
│ Complete   │ 5%          │
└────────────┴─────────────┘
```

Then we attach cost ratios to each state:

```text
none      -> 0%
slight    -> 5%
moderate  -> 20%
extensive -> 55%
complete  -> 100%
```

Then we can either calculate the expected damage:

```text
0.20×0% + 0.30×5% + 0.30×20% + 0.15×55% + 0.05×100%
= 20.8% mean damage ratio
```

or, better for simulation, we can sample a state:

```text
event 1 -> moderate  -> 20% damage
event 2 -> slight    -> 5% damage
event 3 -> complete  -> 100% damage
```

This is why fragility is powerful: it naturally carries uncertainty.

Vulnerability/damage curves produce a mean damage ratio, while fragility curves produce probabilities of damage states. The vulnerability value can be built from the fragility vector by costing each state and taking a weighted average.

---

## 6. Full damage distribution

A full **damage distribution** is the richest version.

Instead of discrete named states, we carry a distribution over damage-ratio bins.

Example:

```text
damage_ratio_distribution = {
    0–5%:     20%
    5–20%:    35%
    20–50%:   30%
    50–80%:   10%
    80–100%:   5%
}
```

ASCII:

```text
60 mm hail
   │
   v
damage distribution
   │
   v
┌────────────────────┬─────────────┐
│ Damage ratio bin   │ Probability │
├────────────────────┼─────────────┤
│ 0%  - 5%           │ 20%         │
│ 5%  - 20%          │ 35%         │
│ 20% - 50%          │ 30%         │
│ 50% - 80%          │ 10%         │
│ 80% - 100%         │ 5%          │
└────────────────────┴─────────────┘
```

Then the Monte Carlo can sample actual damage from this distribution.

```text
simulated event 1 -> 8% damage
simulated event 2 -> 42% damage
simulated event 3 -> 91% damage
```

This is strongest for VaR, PML, and TVaR because it preserves the tail of event damage.

---

## 7. Same event, four possible representations

Let’s use one example:

```text
Asset value = $150M
Hazard intensity = 60 mm hail
```

| Emit object | What the damage stage gives | How event loss is produced |
|---|---|---|
| Scalar | `damage_ratio = 20%` | `$150M × 20% = $30M` |
| Mean + uncertainty | `mean = 20%, spread = 10%` | sample around 20%, then multiply by value |
| Damage-state vector | `{none:20%, slight:30%, moderate:30%, extensive:15%, complete:5%}` | sample a state, then map state to cost |
| Full distribution | `{0–5%:20%, 5–20%:35%, 20–50%:30%, ...}` | sample a damage ratio from bins |

The more you move down the table, the more you preserve uncertainty.

---

## 8. Why this matters for EAL vs VaR

This is the key modeling point.

### Scalar version

```text
Every 60 mm hail event causes exactly $30M.
```

That gives a stable average, so EAL may be okay.

But it removes the possibility that some 60 mm hail events cause $5M and others cause $90M.

### Distribution version

```text
A 60 mm hail event has a range of possible losses.
```

That gives a more realistic tail.

ASCII:

```text
Scalar:
    60 mm -> $30M
    60 mm -> $30M
    60 mm -> $30M
    60 mm -> $30M

Distribution:
    60 mm -> $8M
    60 mm -> $28M
    60 mm -> $54M
    60 mm -> $110M
```

The average may be similar, but the tail is completely different.

And VaR/PML/TVaR live in the tail.

So the clean memory hook is:

```text
Scalar preserves the center.
Distribution preserves the tail.
```

---

## 9. Vulnerability curve versus fragility curve

This is probably the deepest conceptual distinction in that section.

### Vulnerability / damage curve

```text
intensity -> mean damage ratio
```

Example:

```text
60 mm hail -> 20% mean damage
```

This is a scalar.

### Fragility curve

```text
intensity -> probability of damage states
```

Example:

```text
60 mm hail -> 
    20% none
    30% slight
    30% moderate
    15% extensive
    5% complete
```

This is a vector.

Then you can convert the vector into a mean:

```text
fragility vector + cost per state -> vulnerability mean
```

ASCII:

```text
FRAGILITY VIEW
60 mm hail
   │
   v
probability over states
   │
   v
[none, slight, moderate, extensive, complete]

VULNERABILITY VIEW
60 mm hail
   │
   v
one expected damage ratio
   │
   v
20.8%
```

So:

```text
fragility = richer object
vulnerability = expected value summary
```

---

## 10. One-sentence explanation

> The damage stage can either emit a single expected damage ratio, a vector of probabilities over damage states, or a full distribution over possible damage ratios; these are different levels of richness for representing uncertainty in event severity.

Even shorter:

```text
Scalar       = one average damage number
Vector       = probabilities across damage states
Distribution = full spread of possible damage outcomes
```

---

## 11. Suggested wording for the document

The wording “scalar / vector / distribution” is directionally right, but “vector” can be confusing. I would phrase it as:

```text
The damage stage may emit one of four representations:
1. scalar mean damage ratio
2. mean + uncertainty
3. damage-state probability vector
4. discretized damage-ratio distribution
```

That is clearer than just saying:

```text
scalar / vector / distribution
```

because it tells the reader what the vector is a vector **of**.

---

## 12. Final mental model

```text
coupling tells us:
    what intensity reached the asset?

damage representation tells us:
    given that intensity, what range of damage outcomes is possible?

event-loss generation tells us:
    sample one actual outcome and convert it to dollars.

annual aggregation tells us:
    sum actual event losses into yearly losses.
```

So this section is the bridge between **engineering vulnerability** and the **loss vector** used for EAL/VaR/PML.
