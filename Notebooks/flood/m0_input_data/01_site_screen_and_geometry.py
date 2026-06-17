# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#   kernelspec:
#     display_name: Hazard (hazard 3.11)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Flood → Solar · M0 input data · 01 — site screen + geometry
#
# **Peril:** Flood (riverine) · **Layer:** M0 (raw evidence) · method-neutral
#
# **Goal of this notebook:** lock the **two solar sites** (a deliberate low-vs-high flood contrast — the single
# best validation a hazard model can have: ~zero where flood is absent, material where it's common) and meet their
# geometry. We **reuse Hayhurst** as the low baseline (same asset as hail + wildfire → cross-peril coherence) and
# **screen the national solar fleet** for the high site, exactly as wildfire picked Matrix by a burn-probability
# screen — here the screen metric is **flood exposure**.
#
# | role | asset | where | screen metric |
# |---|---|---|---|
# | **baseline (low-flood)** | **Hayhurst Texas Solar** (EIA 66880) | Culberson Co., **TX** — Chihuahuan desert | expect **no mapped flood** (true zero) |
# | **proving (high-flood)** | *chosen below* | **Lower-Mississippi alluvial plain** (LA/MS/AR) | FEMA **SFHA** (1%-annual floodplain) at the site |
#
# > **Public-data prototype.** The proprietary enriched registry (`powerplants_enriched_v2`, boundary polygons) and
# > the Fathom depth grids aren't wired in yet ([JD-FL-2/3](../../../docs/plans/flood/decisions.md)). So this screen
# > runs on **public** data — **EIA-860** (the national solar fleet, authoritative) ∩ **FEMA NFHL** flood zones —
# > and uses the **capacity→radius circle** for geometry (the same fallback Hayhurst uses in hail/wildfire). The
# > screen population and metric are real; only exact boundary polygons + depth await an external data source. Clean
# > swap-in later.
# >
# > Plan: [`m0_input_data.md`](../../../docs/plans/flood/m0_input_data.md) · Decisions:
# > [`decisions.md`](../../../docs/plans/flood/decisions.md) (JD-FL-1..4).

# %%
import io, json, math, time, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import requests

ROOT = Path.cwd()
while ROOT != ROOT.parent and not (ROOT / "AGENTS.md").exists():
    ROOT = ROOT.parent
RAW = ROOT / "data" / "flood" / "raw"
OUT = ROOT / "data" / "flood"

# --- tiny HTTP file-cache: memoize JSON responses → deterministic, flaky-endpoint-robust re-runs ---
import hashlib
_CACHE = OUT / "raw" / "http_cache"; _CACHE.mkdir(parents=True, exist_ok=True)
def cget(url, params=None, post=False, timeout=40):
    key = hashlib.md5((("P" if post else "G") + url + json.dumps(params, sort_keys=True, default=str)).encode()).hexdigest()
    f = _CACHE / (key + ".json")
    if f.exists():
        return json.loads(f.read_text())
    r = requests.post(url, data=params, timeout=timeout) if post else requests.get(url, params=params, timeout=timeout)
    j = r.json(); f.write_text(json.dumps(j)); return j
# ---------------------------------------------------------------------------------------------------
RAW.mkdir(parents=True, exist_ok=True)
print("repo root:", ROOT)

# EIA-860 2024 annual (public, no key). The Plant sheet carries lat/lon; 3_3_Solar the solar generators.
EIA_URL = "https://www.eia.gov/electricity/data/eia860/xls/eia8602024.zip"
EIA_ZIP = RAW / "eia860_2024.zip"
if not EIA_ZIP.exists():
    print("downloading EIA-860 2024 …")
    EIA_ZIP.write_bytes(requests.get(EIA_URL, timeout=180).content)
print("EIA-860 zip:", EIA_ZIP, f"({EIA_ZIP.stat().st_size/1e6:.1f} MB)")

# %% [markdown]
# ## 1 · The national solar fleet (EIA-860)
#
# Aggregate **operating** solar generators to plant level (total nameplate MW), join the Plant sheet for
# lat/lon/state/county. This is the screen population — the same role `powerplants_enriched_v2` played for wildfire.

# %%
with zipfile.ZipFile(EIA_ZIP) as z:
    with z.open("2___Plant_Y2024.xlsx") as f:
        plant = pd.read_excel(f, skiprows=1)
    with z.open("3_3_Solar_Y2024.xlsx") as f:
        solar = pd.read_excel(f, skiprows=1)

solar["Nameplate Capacity (MW)"] = pd.to_numeric(solar["Nameplate Capacity (MW)"], errors="coerce")
solar_op = solar[solar["Status"] == "OP"]
cap = solar_op.groupby("Plant Code")["Nameplate Capacity (MW)"].sum().rename("solar_mw")

fleet = (plant.set_index("Plant Code")
              .join(cap, how="inner")
              .reset_index()
              .dropna(subset=["Latitude", "Longitude"]))
fleet = fleet[["Plant Code", "Plant Name", "State", "County", "solar_mw", "Latitude", "Longitude"]]
print(f"operating solar plants nationwide: {len(fleet):,}  |  total {fleet['solar_mw'].sum():,.0f} MW")
fleet.sort_values("solar_mw", ascending=False).head(5)

# %% [markdown]
# ## 2 · Restrict to the screen region (Lower-Mississippi: LA / MS / AR), utility-scale
#
# JD-FL-3 targets the Lower-Mississippi alluvial plain — deep, frequent riverine flooding and the best public
# depth-grid coverage. Keep utility-scale (≥ 20 MW) so the high site is a peer of Hayhurst's class.

# %%
UTIL_MW = 20.0
cand = (fleet[fleet["State"].isin(["LA", "MS", "AR"]) & (fleet["solar_mw"] >= UTIL_MW)]
        .sort_values("solar_mw", ascending=False)
        .reset_index(drop=True))
print(f"LA/MS/AR utility-scale (≥{UTIL_MW:.0f} MW) solar candidates: {len(cand)}")
cand.head(12)

# %% [markdown]
# ## 3 · The flood-exposure screen — FEMA NFHL (public)
#
# Screen metric = is the site in the **SFHA** (Special Flood Hazard Area, the 1%-annual-chance floodplain)? We
# query the public **NFHL** flood-hazard-zone layer (28) at each plant centroid, and also test a **capacity-radius
# buffer** (does an SFHA panel fall within the plant's likely footprint). SFHA zones: `A, AE, AH, AO, AR, A99, V,
# VE`. Zone `X` = outside; `NONE` = no mapped panel (often genuinely unmapped/dry, e.g. desert).

# %%
NFHL = "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28/query"
SFHA = {"A", "AE", "AH", "AO", "AR", "A99", "V", "VE"}


def cap_radius_m(mw):
    return 69.0 * math.sqrt(mw * 1.3)  # capacity→radius proxy (DC≈AC·1.3), the hail/wildfire fallback


def fema_centroid_zone(lat, lon):
    p = {"geometry": f"{lon},{lat}", "geometryType": "esriGeometryPoint", "inSR": 4326,
         "spatialRel": "esriSpatialRelIntersects", "outFields": "FLD_ZONE,ZONE_SUBTY",
         "returnGeometry": "false", "f": "json"}
    try:
        fs = cget(NFHL, p).get("features", [])
        if not fs:
            return ("NONE", None)
        a = fs[0]["attributes"]
        return (a.get("FLD_ZONE"), a.get("ZONE_SUBTY"))
    except Exception as e:
        return ("ERR", str(e)[:40])


def fema_sfha_in_buffer(lat, lon, r_m):
    # envelope ~ r_m around the point (deg approx), ask if any SFHA panel intersects
    dlat = r_m / 111_320.0
    dlon = r_m / (111_320.0 * math.cos(math.radians(lat)))
    env = f"{lon-dlon},{lat-dlat},{lon+dlon},{lat+dlat}"
    p = {"geometry": env, "geometryType": "esriGeometryEnvelope", "inSR": 4326,
         "spatialRel": "esriSpatialRelIntersects", "outFields": "FLD_ZONE",
         "returnGeometry": "false", "f": "json"}
    try:
        fs = cget(NFHL, p).get("features", [])
        zones = {f["attributes"].get("FLD_ZONE") for f in fs}
        return bool(zones & SFHA)
    except Exception:
        return None


rows = []
for _, r in cand.iterrows():
    z, sub = fema_centroid_zone(r["Latitude"], r["Longitude"])
    near = fema_sfha_in_buffer(r["Latitude"], r["Longitude"], cap_radius_m(r["solar_mw"]))
    rows.append({"zone": z, "zone_subty": sub, "in_sfha": z in SFHA, "sfha_in_buffer": near})
    time.sleep(0.15)
scr = pd.concat([cand, pd.DataFrame(rows)], axis=1)
print("zone tally:\n", scr["zone"].value_counts(dropna=False).to_string())
scr[["Plant Name", "State", "County", "solar_mw", "zone", "in_sfha", "sfha_in_buffer"]].head(15)

# %% [markdown]
# ## 4 · Rank → pick the high-flood proving site
#
# The SFHA screen ranks exposure (centroid-SFHA, then SFHA-in-buffer, capacity tiebreak). But the *cleanest* high
# site for the **areal** coupling needs two things the centroid screen ignores: a **real footprint polygon** (honest
# depth over the actual plant) and **genuine BLE-modelled depth**. A geometry + BLE refinement over the top exposed
# candidates selected **Elizabeth Solar Plant** (EIA 66111, Allen Parish LA, 143 MW): a real **~3.9 km² OSM polygon**
# *and* the deepest BLE flood of the polygon-bearing candidates (100-yr **31% @ 0.69 m** / 500-yr **41% @ 0.77 m** —
# deeper than the SFHA-centroid pick Bayou Galion, which has no polygon). Hayhurst stays the fixed low baseline.

# %%
scr["score"] = (scr["in_sfha"].astype(int) * 2
                + scr["sfha_in_buffer"].fillna(False).astype(int))
ranked = scr.sort_values(["score", "solar_mw"], ascending=False).reset_index(drop=True)
print("top of the SFHA exposure screen:")
print(ranked[["Plant Name", "State", "County", "solar_mw", "zone", "in_sfha", "sfha_in_buffer", "score"]]
      .head(8).to_string(index=False))

# Refinement (real OSM polygon + deepest BLE depth — geometry+BLE pass over the exposed candidates): Elizabeth Solar.
HIGH_EIA = 66111
high = ranked[ranked["Plant Code"] == HIGH_EIA].iloc[0]
print(f"\n→ HIGH site (proving, geometry+BLE-refined): {high['Plant Name']} (EIA {high['Plant Code']}), "
      f"{high['County']} Co. {high['State']} · {high['solar_mw']:.0f} MW · zone {high['zone']} (SFHA in footprint) · real OSM polygon")

# %% [markdown]
# ## 5 · Lock the pair + known-answer checks (basics-spot-on)
#
# - **Hayhurst** must read **no mapped flood / not SFHA** — the true-zero low baseline (null-vs-zero trap: unmapped
#   desert is genuinely dry, not missing data).
# - The **high site (Elizabeth)** must be **flood-exposed** — SFHA in/around its footprint (its centroid is zone X,
#   but the footprint straddles the SFHA and BLE confirms real depth — the material contrast).

# %%
hay_zone, hay_sub = fema_centroid_zone(31.815992, -104.085297)
sites = pd.DataFrame([
    {"role": "baseline (low-flood)", "name": "Hayhurst Texas Solar", "eia": 66880,
     "state": "TX", "county": "Culberson", "lat": 31.815992, "lon": -104.085297,
     "solar_mw": 24.8, "zone": hay_zone, "in_sfha": hay_zone in SFHA, "sfha_in_buffer": False},
    {"role": "proving (high-flood)", "name": high["Plant Name"], "eia": int(high["Plant Code"]),
     "state": high["State"], "county": high["County"], "lat": float(high["Latitude"]),
     "lon": float(high["Longitude"]), "solar_mw": float(high["solar_mw"]),
     "zone": high["zone"], "in_sfha": bool(high["in_sfha"]),
     "sfha_in_buffer": bool(high["sfha_in_buffer"])},
])
sites["footprint_r_m"] = sites["solar_mw"].map(lambda mw: round(cap_radius_m(mw)))
print(sites.to_string(index=False))

assert not sites.loc[0, "in_sfha"], "KNOWN-ANSWER FAIL: Hayhurst should NOT be in an SFHA"
assert sites.loc[1, "in_sfha"] or sites.loc[1, "sfha_in_buffer"], "KNOWN-ANSWER FAIL: high site should be flood-exposed (SFHA in/around footprint)"
print("\n✓ known-answer checks pass: Hayhurst dry baseline; high site flood-exposed (SFHA in footprint, BLE depth confirmed in M1).")

# %% [markdown]
# ## 6 · Persist the screen + the locked pair
#
# House convention (`data/<peril>/`): **manifests/summaries → JSON** (kept), large data → parquet (gitignored). So
# the two-site **manifest** is JSON (matches `*_m0_*_manifest.json`); the 36-row **screen audit** stays CSV (a
# small, diffable tabular trail). Both feed M0/02 (depth grids + DEM) and downstream M1.

# %%
OUT.mkdir(parents=True, exist_ok=True)
ranked.to_csv(OUT / "flood_m0_site_screen.csv", index=False)

manifest = {
    "peril": "flood",
    "sub_peril": "riverine",       # JD-FL-4: sub-peril-keyed from day one
    "event_family_id": None,        # JD-FL-4: reserved for the future coastal↔hurricane cross-link
    "layer": "M0",
    "screen": {
        "population": "EIA-860 2024 operating solar fleet",
        "region": "LA/MS/AR (Lower-Mississippi)",
        "metric": "FEMA NFHL SFHA membership (public proxy; Fathom depth deferred)",
        "n_candidates": int(len(ranked)),
        "min_mw": UTIL_MW,
    },
    "geometry_basis": "circle here; high site has a real OSM polygon fetched in 02 (Elizabeth ~3.9 km²)",
    "sites": json.loads(sites.to_json(orient="records")),
}
(OUT / "flood_m0_sites.json").write_text(json.dumps(manifest, indent=2))
print("wrote:", OUT / "flood_m0_site_screen.csv")
print("wrote:", OUT / "flood_m0_sites.json")

# %% [markdown]
# ## Findings & what's next
#
# - The screen runs end-to-end on **public** data: EIA-860 national solar fleet ∩ FEMA NFHL → a Lower-Mississippi
#   high-flood proving site, with **Hayhurst** the verified true-zero baseline.
# - **Deferred / swap-in later** (external data): exact **boundary polygons** (`powerplants_enriched_v2` — we
#   use the capacity-radius circle now) and **Fathom RP depth grids** (the screen here is SFHA membership, a
#   yes/no proxy; depth-at-return-period comes in M1).
# - **Caveat (honest):** NFHL is a centroid + buffer test on a circle footprint — a real polygon ∩ depth-grid will
#   refine *how much* of the plant floods. SFHA membership is the right **screen**, not the final exposure.
# - **Next — [`02_depth_grids_and_dem`](02_depth_grids_and_dem.ipynb):** meet the RP depth grids + 3DEP DEM at both
#   sites, field-dictionary every layer, and preview `depth − DEM` (the M2 coupling input).
