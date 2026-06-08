# 01 — Hazard Adapters From First Principles

## Core definition

In this methodology, an **adapter** means:

> A hazard-specific translator that takes messy, hazard-specific evidence and converts it into the one shared format that the rest of the loss model understands.

Or even simpler:

```text
adapter = translator between "hazard world" and "loss-model world"
```

The key rule is:

> **Standardize the output, not the physics.**

Hail, flood, heat, wind, and earthquake are allowed to use different physics, but after each adapter finishes, they must all emit the same kind of `event_record` for the annual loss engine to consume.

---

## 1. Why do we need adapters at all?

Start with the basic problem.

Different hazards do **not** arrive in the same form.

```text
Hail data might look like:
    event footprint + hail size + swath area

Flood data might look like:
    water depth at asset + flood duration

Heat data might look like:
    hourly temperature + duration above threshold

Earthquake data might look like:
    ground acceleration at site

Wildfire data might look like:
    flame intensity / distance / ember exposure
```

Those are very different “languages.”

But downstream, the risk engine wants one clean thing:

```text
For this event, for this asset, what actual loss happened?
```

So the adapter is the thing that says:

```text
"I know how to interpret hail."
"I know how to interpret flood."
"I know how to interpret heat."
"But I will report the answer in the same standard format."
```

---

## 2. The simplest analogy: power outlet adapters

Imagine you travel with one laptop charger.

Different countries have different wall outlets:

```text
US outlet       UK outlet       EU outlet       India outlet
   ||             |||             oo              ooo
```

Your laptop does not want to understand every country’s electrical socket shape. It just wants usable power.

So you use an adapter:

```text
UK wall socket  ──>  adapter  ──>  your laptop charger
EU wall socket  ──>  adapter  ──>  your laptop charger
US wall socket  ──>  adapter  ──>  your laptop charger
```

In our hazard model:

```text
hail event      ──> hail adapter   ──> common event_record
flood event     ──> flood adapter  ──> common event_record
heat event      ──> heat adapter   ──> common event_record
earthquake      ──> quake adapter  ──> common event_record
```

The annual loss engine is like the laptop. It does **not** want to know every hazard’s physics. It just wants a standard input.

---

## 3. The adapter is not the whole model

This is important.

The adapter is **not** saying:

> “All hazards are the same.”

It is saying:

> “Each hazard can use its own physics, but it must hand off results in the same shape.”

Bad version:

```text
Force every hazard through one formula.
```

Good version:

```text
Let each hazard use its correct physics,
then standardize the output.
```

The old mistake was forcing every hazard through one spatial-factor formula, which works only for certain hit-or-miss hazards and fails for others like flood, heat, earthquake, and broad field wind.

---

## 4. What does an adapter actually do?

At a high level, each adapter answers this question:

```text
Given:
    one hazard event
    one asset

Return:
    the actual event loss for that asset
```

In pseudo-code:

```text
event_record = adapter.compute_event_loss(event, asset)
```

That `event_record` has to look standard no matter which hazard produced it.

Example shared output:

```text
event_record = {
    event_id,
    year,
    asset_id,
    hazard_type,
    event_loss,
    event_max_loss,
    loss_components,
    event_duration,
    recovery_time
}
```

So a hail adapter and flood adapter may think very differently internally, but externally they both hand over something like:

```text
event_id:        "HAIL_2032_041"
asset_id:        "SolarFarm_A"
hazard_type:     "hail"
event_loss:      $12,400,000
event_duration:  14 days
```

or:

```text
event_id:        "FLOOD_2032_009"
asset_id:        "Substation_B"
hazard_type:     "flood"
event_loss:      $7,800,000
event_duration:  21 days
```

Downstream, both are just event losses.

---

## 5. The adapter as a translator

Think of each hazard as speaking its own language:

| Hazard | Native language | Adapter translates into |
|---|---|---|
| Hail | footprint, hail size, swath, hit/miss | event loss record |
| Flood | depth at site, inundation duration | event loss record |
| Heat | temperature, duration, derating | event loss record |
| Earthquake | ground motion, site intensity | event loss record |
| Wind | gust speed, footprint or field | event loss record |

The annual aggregator only wants this:

```text
[event loss, event loss, event loss, ...]
```

It does not want this:

```text
[radar swath, water depth raster, hourly temperature grid, PGA map, wind field, ...]
```

That messy translation is the adapter’s job.

---

## 6. ASCII picture of the idea

```text
                  HAZARD-SPECIFIC WORLD
        ┌───────────────────────────────────────┐
        │ Hail: footprint + hail size           │
        │ Flood: depth + duration               │
        │ Heat: temperature + derating          │
        │ Earthquake: ground motion             │
        └───────────────────────────────────────┘
                         │
                         v
              ┌─────────────────────┐
              │ Hazard adapter       │
              │ "Translate this into │
              │  actual event loss"  │
              └─────────────────────┘
                         │
                         v
                  COMMON LOSS WORLD
        ┌───────────────────────────────────────┐
        │ event_id                              │
        │ year                                  │
        │ asset_id                              │
        │ hazard_type                           │
        │ event_loss                            │
        │ event_duration                        │
        │ recovery_time                         │
        │ loss_components                       │
        └───────────────────────────────────────┘
                         │
                         v
        ┌───────────────────────────────────────┐
        │ Annual aggregation                     │
        │ Sum event losses by simulated year     │
        └───────────────────────────────────────┘
                         │
                         v
        ┌───────────────────────────────────────┐
        │ EAL, VaR, PML, TVaR, AEP, OEP          │
        └───────────────────────────────────────┘
```

The adapter is the middle box.

---

## 7. Why not just use one universal formula?

Because hazards do not all “touch” assets the same way.

For hail, a spatial hit/miss idea can make sense:

```text
A hail swath either overlaps the solar farm or it does not.
```

So for hail:

```text
regional hail event
    └── maybe hits asset
            └── if hit, causes conditional damage
```

But for heat:

```text
A heat wave does not usually "miss" the asset.
The asset is in the temperature field.
The question is: how hot, for how long?
```

For flood:

```text
The key question is not footprint area / search area.
The key question is: what water depth occurs at the site?
```

So this is wrong:

```text
One universal formula:
    event_loss = spatial_factor × conditional_loss
```

Because that treats flood, heat, hail, and wind as if they all behave like the same kind of spatial coin flip.

The adapter approach fixes that:

```text
Hail adapter:
    use hit/miss footprint logic

Flood adapter:
    use water depth at asset

Heat adapter:
    use temperature and duration

Earthquake adapter:
    use ground motion at site

All emit:
    event_record with actual event_loss
```

---

## 8. Adapter versus aggregator

This distinction is very important.

| Piece | Job | Hazard-specific? |
|---|---|---|
| Adapter | Convert one hazard event into one event loss record | Yes |
| Aggregator | Combine event losses into annual losses | Mostly no |
| Metrics reader | Read EAL, VaR, PML, TVaR from annual vector | No |

So:

```text
Adapter asks:
    "What loss did this event cause?"

Aggregator asks:
    "What was the total loss in this simulated year?"

Metrics reader asks:
    "What is the mean? What is the 99th percentile?"
```

Or visually:

```text
adapter level:
    event 1 -> loss
    event 2 -> loss
    event 3 -> loss

aggregator level:
    year loss = loss_1 + loss_2 + loss_3

metrics level:
    EAL = average of many year losses
    VaR_99 = 99th percentile of many year losses
```

The adapter does **not** compute VaR.  
The adapter does **not** compute EAL.  
The adapter produces event-level loss records that make those later metrics possible.

---

## 9. Concrete example: hail adapter

Suppose we have a hail event.

Raw hazard data:

```text
event_id:       HAIL_001
hail size:      55 mm
footprint area: 80 square miles
storm location: polygon / swath
```

Asset data:

```text
asset_id:       SolarFarm_A
asset type:     solar farm
asset value:    $150M
geometry:       area asset
panel rating:   vulnerable above certain hail size
```

The hail adapter might do this:

```text
1. Does the hail footprint overlap the solar farm?
       yes / no

2. If no:
       event_loss = 0

3. If yes:
       read hail size at the asset

4. Use solar hail damage curve:
       55 mm hail -> maybe 15% damage ratio

5. Convert damage ratio to dollars:
       15% × $150M = $22.5M

6. Add downtime / business interruption if modeled

7. Emit common event_record
```

ASCII version:

```text
HAIL_001
  │
  ├─ footprint overlaps solar farm?
  │        │
  │        ├─ no  -> event_loss = $0
  │        │
  │        └─ yes -> hail size at asset = 55 mm
  │                    │
  │                    v
  │             damage curve
  │             55 mm -> 15%
  │                    │
  │                    v
  │             15% × $150M = $22.5M
  │
  v
event_record {
    hazard_type: "hail",
    event_loss: $22.5M,
    event_duration: ...
}
```

---

## 10. Concrete example: flood adapter

Flood is different.

Raw hazard data:

```text
event_id:      FLOOD_014
water depth:   raster / map
duration:      4 days above threshold
```

Asset data:

```text
asset_id:      Substation_B
asset value:   $40M
elevation:     2 feet above grade
component vulnerability: transformers, switchgear, controls
```

The flood adapter might do this:

```text
1. Read flood depth at the asset.
       example: 3.5 feet

2. Adjust for asset elevation / protection.
       effective depth maybe 1.5 feet inside critical area

3. Use flood damage curve.
       1.5 feet -> 25% physical damage

4. Convert to dollars.
       25% × $40M = $10M

5. Estimate downtime.
       30 days

6. Add business interruption if relevant.

7. Emit same common event_record.
```

ASCII version:

```text
FLOOD_014
  │
  ├─ depth at substation = 3.5 ft
  │
  ├─ adjust for elevation/protection
  │        effective depth = 1.5 ft
  │
  ├─ flood damage curve
  │        1.5 ft -> 25%
  │
  ├─ physical loss
  │        25% × $40M = $10M
  │
  └─ downtime / BI
           30 days -> revenue / service loss

  v
event_record {
    hazard_type: "flood",
    event_loss: $10M + BI,
    event_duration: 4 days,
    recovery_time: 30 days
}
```

Notice: no hail footprint hit/miss formula was forced onto flood.

---

## 11. Same output, different internals

This is the heart of adapters.

```text
                INSIDE ADAPTER                 OUTSIDE ADAPTER

Hail        footprint overlap + hail size  ─┐
Flood       depth at site + duration       ─┼─> common event_record
Heat        temperature + derating         ─┤
Quake       ground motion + fragility      ─┘
```

Inside the adapter:

```text
messy, hazard-specific, physics-specific
```

Outside the adapter:

```text
clean, standardized, hazard-agnostic
```

That is why the annual aggregator can be shared.

---

## 12. The adapter protects us from the wrong universal shortcut

The dangerous shortcut is this:

```text
event_loss = spatial_factor × conditional_loss
```

That can preserve the average, but it destroys the hit/miss randomness that VaR and PML need.

For a hail event, reality is more like:

```text
with 97% probability:
    loss = $0

with 3% probability:
    loss = $50M
```

The shortcut replaces that with:

```text
loss = 0.03 × $50M = $1.5M every time
```

Compare:

| Reality | Shortcut |
|---|---|
| Most events miss and cause $0 | Every event causes a small fake loss |
| Rare events hit and cause big loss | Big loss is smoothed away |
| Tail is preserved | Tail is destroyed |
| Good for VaR/PML | Bad for VaR/PML |

ASCII picture:

```text
Real hit/miss loss:
    $0    $0    $0    $0    $50M    $0    $0    $50M

Expected-loss shortcut:
    $1.5M $1.5M $1.5M $1.5M $1.5M  $1.5M $1.5M $1.5M
```

Same-ish mean, totally different tail.

The adapter prevents this by making each hazard compute actual event losses correctly before aggregation.

---

## 13. Adapter, coupling, and geometry

The adapter usually has to understand two things:

```text
1. Coupling:
   How does the hazard reach the asset?

2. Geometry:
   What shape is the asset?
```

| Concept | Meaning | Example |
|---|---|---|
| Coupling | How hazard physically reaches asset | hail hit/miss, heat field, flood depth |
| Geometry | Shape/layout of asset | point, area, line, portfolio |

So an adapter often asks:

```text
What coupling type is this?
What asset geometry is this?
What damage curve applies?
What event loss should I emit?
```

Example grid:

```text
                 POINT ASSET        AREA ASSET          LINE ASSET
                 -----------        ----------          ----------
Hail             substation         solar farm          transmission line
Flood            substation         solar farm          corridor
Heat             BESS site          solar farm          wind farm region
```

The same hazard may need slightly different math depending on geometry.

Hail on a point asset:

```text
Did swath hit the point?
```

Hail on a solar farm:

```text
What fraction of the area was hit?
```

Hail on a transmission line:

```text
What length of the line was crossed?
```

Same coupling family, different geometry kernel.

---

## 14. A compact definition

```text
A hazard adapter is a module that knows the hazard-specific physics
needed to turn raw hazard evidence + asset exposure into a standardized
actual event-loss record.
```

Even shorter:

```text
adapter = hazard-specific loss translator
```

---

## 15. What goes into an adapter?

A practical adapter may include or call several sub-pieces:

```text
Raw hazard event
    │
    v
Coupling logic
    "Does it hit? What intensity reaches the asset?"
    │
    v
Geometry logic
    "Point, area, line, or portfolio?"
    │
    v
Damage logic
    "Given intensity, what damage ratio?"
    │
    v
Duration logic
    "How long is the asset impaired?"
    │
    v
Financial pre-loss components
    "Physical damage, BI, repair, downtime"
    │
    v
Common event_record
```

In ASCII:

```text
adapter(event, asset):

    event + asset
        │
        ├─ coupling
        │     hit/miss? field intensity? local depth?
        │
        ├─ geometry
        │     point? area? line? portfolio?
        │
        ├─ severity
        │     intensity -> damage ratio
        │
        ├─ duration
        │     damage/persistence -> downtime
        │
        └─ emit event_record
```

Methodologically, the essential point is not exactly how the code is split. The essential point is the **seam**:

```text
hazard-specific logic above the seam
standardized event_record below the seam
```

---

## 16. Why this makes the system extensible

Suppose today we support only hail.

```text
hail adapter -> event_record -> annual aggregator -> metrics
```

Later we add flood.

Bad architecture:

```text
Rewrite annual aggregator for flood.
Rewrite metrics for flood.
Rewrite VaR logic for flood.
```

Good adapter architecture:

```text
flood adapter -> same event_record -> same annual aggregator -> same metrics
```

So adding a new hazard should mostly mean:

```text
build a new adapter
keep the downstream engine the same
```

That is why the universal interface lets a new hazard plug in without touching the metrics engine.

---

## 17. One simple toy example

Let’s say the annual aggregator only understands this:

```text
event_record = {
    year,
    event_loss
}
```

Now give it three hazards.

### Hail adapter output

```text
{ year: 2030, event_loss: $0       }
{ year: 2031, event_loss: $20M     }
{ year: 2032, event_loss: $0       }
```

### Flood adapter output

```text
{ year: 2030, event_loss: $5M      }
{ year: 2031, event_loss: $0       }
{ year: 2032, event_loss: $18M     }
```

### Heat adapter output

```text
{ year: 2030, event_loss: $1.2M    }
{ year: 2031, event_loss: $2.0M    }
{ year: 2032, event_loss: $0.8M    }
```

The aggregator does not care how those losses were created. It only does:

```text
annual_loss[2030] = sum(event losses in 2030)
annual_loss[2031] = sum(event losses in 2031)
annual_loss[2032] = sum(event losses in 2032)
```

That is the power of adapters.

---

## 18. The adapter boundary in one picture

```text
       hazard-specific side                 common side
 ┌────────────────────────────┐      ┌────────────────────────────┐
 │ Hail swath                 │      │ event_id                   │
 │ Flood depth raster         │      │ year                       │
 │ Heat time series           │ ───> │ asset_id                   │
 │ Wind gust footprint        │      │ hazard_type                │
 │ Earthquake ground motion   │      │ event_loss                 │
 └────────────────────────────┘      │ duration / recovery        │
                                     │ loss components            │
                                     └────────────────────────────┘
              adapter
```

Everything on the left can vary wildly.

Everything on the right must be standardized.

---

## 19. How to remember it

Use this phrase:

```text
Different physics in.
Same loss record out.
```

Or:

```text
Adapters localize hazard weirdness.
```

That means all the messy hazard-specific decisions stay inside the adapter, instead of leaking into the annual aggregation and risk metric logic.

---

## 20. Key lesson

The adapter is not just a software convenience. It is a modeling safeguard.

Without adapters, you are tempted to create one universal formula:

```text
loss = frequency × spatial factor × severity
```

That may give a reasonable EAL, but it can break VaR/PML because it smooths away the actual event structure.

With adapters, you preserve the correct physical story:

```text
hail:
    regional event -> hit/miss -> conditional damage -> event loss

flood:
    local depth -> component damage -> downtime -> event loss

heat:
    temperature duration -> production derating -> revenue loss

all:
    event loss record -> annual loss vector -> EAL/VaR/PML/TVaR
```

So when you see **adapter** in the document, read it as:

> “The hazard-specific module that converts raw hazard evidence into a standardized actual event loss, while preserving the right physics for that hazard.”
