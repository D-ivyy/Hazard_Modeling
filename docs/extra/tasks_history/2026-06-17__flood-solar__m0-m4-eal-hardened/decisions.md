# Decisions — flood × solar (indexes the canonical `docs/plans/flood/decisions.md`)

Canonical ADRs live in [`docs/plans/flood/decisions.md`](../../../plans/flood/decisions.md) (prefix `JD-FL-*`, newest
on top). This file is the session index + the one decision made this session.

| ID | Decision | Status |
|---|---|---|
| **JD-FL-8** | **Densify lower RPs via regression flow-frequency + a BLE-anchored rating** (not live HAND) — *this session* | **decided / built** |
| JD-FL-7 | Event-model bridge = annual-maximum MC sampling the RP loss curve | decided / built |
| JD-FL-6 | Depth source = national StreamStats+HAND, **FEMA-BLE-preferred**; BLE used for the proving site | decided |
| JD-FL-5 | ~~Single-gauge Log-Pearson III extraction~~ | **superseded by JD-FL-6** |
| JD-FL-4 | M1 as a sub-peril *family* + reserved `event_family_id` (add coastal later) | proposed |
| JD-FL-3 | Two sites — Hayhurst (low, reused) + national-EIA flood-screen high site (→ Elizabeth) | decided |
| JD-FL-2 | M1 frequency = pre-integrated RP depth grids (not LP-III extraction) | proposed |
| JD-FL-1 | Scope — riverine(+pluvial) physical damage to solar first; coastal cross-linked to hurricane, deferred | proposed |

## JD-FL-8 — the decision made this session (rationale in brief)

**Context.** JD-FL-7 shipped a 3-point loss curve whose 10-yr **onset depth was assumed** (`ONSET_DEPTH_FT=0.5`); EAL
is driven by exactly that frequent region. The promised hardening was "densify with StreamStats+HAND."

**On building it:** the literal HAND path was (a) **unavailable** — USGS watershed-delineation service 404, HAND
rasters are large S3 files — and (b) per the research, **least accurate here** (flat, low-relief LA alluvial plain,
where the BLE we'd anchor to is already HEC-RAS-grade). The NSS regression *was* reachable.

**Decision (option b of 4).** Get real flow-frequency `Q(T)` from regression, fit a **power-law rating pinned to both
real BLE depths**, read depth at the lower RPs. Persist raw `Q(T)` so a future swap to live HAND is just the depth step.

**Why.** Makes the lower-RP depths rest on **real data** (flow shape + two real BLE depth anchors) not a flat guess,
while staying runnable + honest. For a flat BLE-covered site, **anchoring to BLE beats raw HAND** (research's own
ranking). Only remaining assumption = the rating *shape* between anchors (sensitivity-tested; near-invariant to slope).

**Honest caveats carried forward.** Regression-Q standard error (±40–60%) **not yet** propagated as an MC overlay
(EAL still a point estimate); still annual-maximum, physical-damage-only; densified for the proving site only (regional
equation is LA-specific). **Revisit:** delineation service returns → swap in live HAND-SRC; or propagate Q-uncertainty.

Full text + options table: [`docs/plans/flood/decisions.md#jd-fl-8`](../../../plans/flood/decisions.md).
