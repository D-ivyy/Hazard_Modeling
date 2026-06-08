# 02 — Adapter Dataflow: From Event Catalog to Event Loss Record

## Core answer

The question was whether the adapter is “two-way communication,” because the initial event catalog does **not** contain loss by default.

Yes — that intuition is correct:

> The **event catalog is not a loss catalog**. It contains hazard evidence. The event loss is produced downstream by coupling the event to the asset and applying exposure, geometry, damage, duration, and financial logic.

But architecturally, I would **not** call the core flow truly two-way. I would call it:

```text
one-way dataflow with lookups and derived outputs
```

Meaning: the adapter reads from the catalog and other inputs, computes derived loss records, and sends those forward. It normally should **not mutate the original hazard catalog**.

---

## 1. The raw catalog starts without loss

Think of the starting catalog like this:

```text
hazard_event_catalog

event_id     hazard_type     year     footprint/intensity     peak_intensity
--------     -----------     ----     -------------------     --------------
HAIL_001     hail            2032     swath polygon           55 mm
HAIL_002     hail            2032     swath polygon           38 mm
FLOOD_009    flood           2033     depth raster            3.2 ft
HEAT_014     heat            2034     temp field              42°C
```

There is **no dollar loss yet**.

The catalog says:

```text
what happened physically
```

It does not yet say:

```text
what it cost this asset
```

The catalog contract includes things like:

```text
event_id
hazard_type
event year or annual rate
event ontology
footprint or intensity reference
footprint area
peak intensity
resolution
climate baseline
provenance
```

These are inputs needed before coupling or loss simulation.

So the loss number is **manufactured downstream** by combining the event with the asset.

---

## 2. The adapter does not “go backward”; it “reaches back” to read inputs

The clean mental model is this:

```text
RAW EVENT CATALOG  ──read──┐
                           │
ASSET / EXPOSURE   ──read──┤
                           │
DAMAGE CURVES      ──read──┤
                           │
DURATION MODEL     ──read──┤
                           v
                     HAZARD ADAPTER
                           │
                           v
                  EVENT LOSS RECORD
```

The adapter may **look back into** the catalog many times:

```text
What was the event footprint?
What was the hail size?
What year did it occur?
What is the event family?
What is the intensity at this asset location?
```

But that is not really “two-way communication.” It is more like a function call:

```text
event_loss_record = adapter(event, asset, damage_curve, duration_model)
```

The event catalog is an input. The output is a new derived object.

---

## 3. Raw catalog versus enriched derived records

This is the cleanest way to see it:

```text
Layer 0: raw hazard evidence
    reports, radar, gauges, reanalysis, simulations

        │
        v

Layer 1: standardized hazard catalog
    event_id
    hazard_type
    year / rate
    footprint / intensity field
    peak intensity
    provenance

        │
        v

Layer 2: event × asset exposure record
    did it hit?
    local intensity at asset
    exposed fraction
    asset geometry used

        │
        v

Layer 3: damage / duration record
    damage ratio
    damage-state distribution
    downtime / recovery time
    BI-relevant duration

        │
        v

Layer 4: event loss record
    event_loss dollars
    physical damage
    business interruption
    event_max_loss
    recovery time

        │
        v

Layer 5: annual loss vector
    year_1_loss
    year_2_loss
    year_3_loss
    ...
```

So the loss is not “inside” the original catalog. It is produced after the catalog is joined with:

```text
asset exposure
+ coupling logic
+ geometry logic
+ damage curve
+ duration model
+ financial transformation
```

---

## 4. Two adapter-like things

There are really **two adapter-like things** that can exist:

| Name | Converts from | Converts to | Has loss yet? |
|---|---|---|---|
| **Catalog adapter** | raw vendor / hazard evidence | standardized hazard event catalog | No |
| **Loss adapter / coupling adapter** | standardized event + asset + damage logic | event loss record | Yes |

This is why the word “adapter” can get confusing.

A **catalog adapter** says:

```text
"This vendor's hail file / flood raster / heat grid
will be normalized into our standard hazard catalog schema."
```

A **loss adapter** says:

```text
"For this hazard event and this asset,
I know how to compute the actual event loss."
```

The cleaner naming would be:

```text
raw_hazard_adapter
    raw evidence -> hazard_event

hazard_asset_loss_adapter
    hazard_event + asset -> event_loss_record
```

That removes the confusion.

---

## 5. Example: hail catalog before and after the loss adapter

Start with raw / standardized hazard event:

```text
hazard_event = {
    event_id: "HAIL_001",
    year: 2032,
    hazard_type: "hail",
    footprint: swath_polygon,
    peak_hail_size: 55 mm,
    frequency_process: "Poisson or event catalog sample",
    provenance: "radar-derived hail swath"
}
```

No loss yet.

Now the hail loss adapter receives:

```text
hazard_event
asset = SolarFarm_A
asset_geometry = area polygon
asset_value = $150M
damage_curve = hail_size -> damage_ratio
duration_model = repair_time distribution
```

Then it does:

```text
1. Intersect hail swath with solar farm polygon.
2. Compute exposed fraction.
3. Read hail size at the asset.
4. Convert hail size to damage ratio using damage curve.
5. Convert damage ratio to physical dollars.
6. Sample / estimate downtime.
7. Add business interruption if modeled.
8. Emit event_loss_record.
```

Output:

```text
event_loss_record = {
    event_id: "HAIL_001",
    asset_id: "SolarFarm_A",
    hazard_type: "hail",
    local_intensity: 55 mm,
    exposed_fraction: 0.40,
    physical_damage: $12.0M,
    business_interruption: $1.5M,
    event_loss: $13.5M,
    recovery_time: 21 days
}
```

That output is **not pushed back into the original catalog**. It is a derived record linked by `event_id`.

---

## 6. Database mental model: do not overwrite the source table

Think of it like tables.

### Table A: hazard events

```text
event_id     hazard_type     year     intensity     footprint
--------     -----------     ----     ---------     ---------
HAIL_001     hail            2032     55 mm         polygon
HAIL_002     hail            2032     38 mm         polygon
```

### Table B: assets

```text
asset_id       asset_type     value     geometry
--------       ----------     -----     --------
SOLAR_A        solar          $150M     polygon
```

### Table C: derived event-asset exposure

```text
event_id     asset_id     hit?     local_intensity     exposed_fraction
--------     --------     ----     ---------------     ----------------
HAIL_001     SOLAR_A      yes      55 mm               0.40
HAIL_002     SOLAR_A      no       0                   0.00
```

### Table D: derived event loss

```text
event_id     asset_id     physical_loss     BI_loss     total_event_loss
--------     --------     -------------     -------     ----------------
HAIL_001     SOLAR_A      $12.0M            $1.5M       $13.5M
HAIL_002     SOLAR_A      $0                $0          $0
```

The adapter creates Tables C and D. It does not rewrite Table A.

That is the clean audit trail:

```text
source hazard event stays pure
derived exposure/loss records are traceable back to event_id
```

---

## 7. So is it two-way?

I would answer like this:

```text
Operationally: no, not two-way.
Conceptually: yes, it consults upstream information many times.
Governance-wise: yes, validation can send us back to revise inputs.
```

More carefully:

| Sense of “two-way” | Answer | Meaning |
|---|---:|---|
| Does the adapter read from the event catalog? | Yes | It needs footprint, intensity, year, event type, etc. |
| Does the adapter write loss back into the raw catalog? | Usually no | It should emit a separate derived event-loss record. |
| Can validation reveal the catalog/damage curve/adapter is wrong? | Yes | Then humans/modeling workflow revise inputs and rerun. |
| Does the annual aggregator talk back to the adapter during a simulation? | Usually no | It consumes event-loss records and sums them. |

So the best phrase is:

```text
not two-way communication;
a one-way pipeline with traceable upstream dependencies
and validation feedback loops.
```

---

## 8. The adapter is more like a “loss compiler”

Another useful analogy:

```text
source code  -> compiler -> executable
```

In our case:

```text
hazard catalog + asset + damage logic -> adapter -> event loss records
```

The compiler reads source code, but it does not rewrite the source code every time it compiles. It produces a compiled artifact.

Similarly:

```text
adapter reads hazard catalog
adapter reads asset exposure
adapter reads damage curves
adapter emits loss records
```

The original catalog remains the source of truth.

---

## 9. Why keeping it one-way matters

If the adapter writes losses directly back into the catalog, the catalog becomes mixed:

```text
hazard evidence + asset-specific loss result
```

That is dangerous because one hazard event can have many different losses depending on the asset.

Example:

```text
HAIL_001 on SolarFarm_A = $13.5M
HAIL_001 on Substation_B = $0.2M
HAIL_001 on Warehouse_C = $0.0M
```

So `event_loss` is not a property of the hazard event alone.

It is a property of:

```text
event × asset × vulnerability × financial basis
```

That is the big reason not to store it as if it were just part of the hazard catalog.

The hazard event can be reused across many assets:

```text
                  HAIL_001
                     │
        ┌────────────┼────────────┐
        v            v            v
   SolarFarm_A   Substation_B   Line_C
      $13.5M        $0.2M        $4.1M
```

Same event, different losses.

---

## 10. The object being created is really an `event_asset_loss_record`

The document calls the shared output an `event_record`, but to avoid confusion I would rename it mentally as:

```text
event_asset_loss_record
```

because it is not merely an event anymore.

It is:

```text
this event
on this asset
under this damage curve
under this financial basis
caused this loss
```

A clearer schema would be:

```text
event_asset_loss_record = {
    event_id,
    asset_id,
    hazard_type,
    year,

    coupling_type,
    exposure_geometry,
    hit_indicator,
    exposed_fraction,
    local_intensity,

    damage_ratio_or_distribution,
    physical_damage,
    event_duration,
    recovery_time,
    business_interruption,

    gross_event_loss,
    net_event_loss,
    vector_basis,

    provenance_links
}
```

That name makes the data lineage clearer.

---

## 11. The conceptual chain is exactly right

The correct chain is:

```text
initial event catalog
    -> coupling
    -> exposure
    -> geometry
    -> event loss drivers
    -> damage curves
    -> event loss number
```

More fully:

```text
hazard event
    │
    ├─ What kind of hazard is it?
    │      hail / flood / heat / wind / earthquake
    │
    ├─ How does it couple to the asset?
    │      hit-or-miss / field intensity / site-conditioned
    │
    ├─ What is the asset geometry?
    │      point / area / line / portfolio
    │
    ├─ What intensity reaches the asset?
    │      hail size, water depth, wind speed, temperature, PGA
    │
    ├─ What damage does that intensity create?
    │      damage curve / fragility / vulnerability
    │
    ├─ How long is the impairment?
    │      downtime / persistence / repair time
    │
    ├─ What is the financial consequence?
    │      physical damage + BI + terms
    │
    v
event loss
```

---

## 12. Final mental model

Use this as the clean version:

```text
The event catalog is evidence.
The adapter is the translator/calculator.
The event-loss record is the derived result.
The annual aggregator is the summing machine.
The risk metrics are readings off the final annual vector.
```

Or even shorter:

```text
catalog says: "what happened?"
adapter asks: "how does that event affect this asset?"
damage/duration/finance says: "how much does that effect cost?"
event_loss_record says: "this event caused this loss."
annual aggregator says: "what did the simulated year lose in total?"
metrics say: "what is the mean or tail of those years?"
```

The adapter is not just a passive format converter. In the loss-generation sense, it is the hazard-specific module that **turns catalog evidence into asset-specific event loss**. But architecturally, it should produce a new downstream record rather than writing loss back into the raw catalog.
