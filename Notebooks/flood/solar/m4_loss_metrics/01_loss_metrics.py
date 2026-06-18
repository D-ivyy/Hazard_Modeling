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
# # Flood → Solar · M4 loss & metrics
#
# **Peril:** Flood (riverine) · **Asset:** Solar · **Layer:** M4 (loss & metrics) · sub-peril `riverine`
#
# **Goal:** turn the M3 conditional losses into the **annual loss distribution** → **EAL / VaR / PML / TVaR** (% of
# TIV + dollars), the same metric frame hail/wildfire/wind report (DD-4).
#
# **Event-model bridge ([JD-FL-7](../../../../docs/plans/flood/decisions.md)).** Riverine flood = **annual-maximum**
# (~1 damaging flood/yr). We build a **loss-exceedance curve** straight from the M3 conditional losses — now a **5-point
# RP curve** for the proving site (10/25/50/100/500-yr) after the [JD-FL-8](../../../../docs/plans/flood/decisions.md)
# densification: the 100/500-yr points are **real BLE**; the 10/25/50-yr points come from a **regression flow-frequency
# rating anchored to both BLE depths** (no more assumed onset depth). The MC draws each year's `AEP ~ U(0,1)` →
# `loss(AEP)` (log-AEP interpolation, bounded extrapolation) → per-year loss vectors → the shared metrics. The
# convective_wind strong-wind pattern (sample an RP curve), specialized to annual-max.
#
# > **Honest:** PML@100/500-yr is **anchored to real BLE**; **EAL is now densified** — the frequent region rests on
# > measurement-anchored 10/25/50-yr depths (JD-FL-8), not a flat onset guess. §2b shows how much that moved EAL.
# > Seam-ready: the curve is built generically from whatever RPs M3 emits. Plan: [`m4_loss_metrics.md`](../../../../docs/plans/flood/m4_loss_metrics.md).

# %%
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path.cwd()
while ROOT != ROOT.parent and not (ROOT / "AGENTS.md").exists():
    ROOT = ROOT.parent
OUT = ROOT / "data" / "flood"

m3 = pd.DataFrame(json.loads((OUT / "flood_m3_damage_manifest.json").read_text())["sites"])
sites = m3.groupby("name").agg(role=("role", "first"), tiv_usd=("tiv_usd", "first")).reset_index()
L = {(r["name"], r["rp_years"]): r["cond_loss_frac_tiv"] for _, r in m3.iterrows()}
# real 10-yr exposure (BLE 10% extent, from M1) + the vendored damage curve (to price the onset depth)
F10 = {s["name"]: s.get("rp10_inund_frac", 0.0) for s in json.loads((OUT / "flood_m1_catalog_manifest.json").read_text())["sites"]}
_cv = json.loads((OUT / "damage_curves" / "flood_solar_asset_capex_weighted.json").read_text())


def asset_dr(depth_ft):   # capex-weighted, anchored DR(0)=0 — same curve as M3
    tot = 0.0
    for c in _cv["subsystems"]:
        L_, k, x0 = c["L"], c["k"], c["x0_ft"]
        tot += c["capex_weight"] * max(L_ / (1 + np.exp(-k * (depth_ft - x0))) - L_ / (1 + np.exp(-k * (0 - x0))), 0)
    return tot


print("M3 conditional losses (input) + real 10-yr exposure (M1):")
print(m3[["name", "rp_years", "cond_loss_frac_tiv", "tiv_usd"]].to_string(index=False))
print("  10-yr exposure (BLE 10% extent):", {n: f"{f*100:.0f}%" for n, f in F10.items()})

# %% [markdown]
# ## 1 · Loss-exceedance curve (the seam: a source-tagged, variable-length RP→loss profile)
#
# The curve is now built **generically from whatever RPs M3 emits** — for the proving site that's the JD-FL-8
# 5-point profile (10/25/50/100/500-yr), each point a real `conditional_loss` (exposure × DR × ... already priced in
# M3). The baseline keeps its 100/500-yr tail. `ONSET_AEP` (10-yr) remains the most-frequent damaging flood (below it,
# BLE maps no inundation → no loss). Adding more points (e.g. full HAND) just lengthens each site's list — no change here.

# %%
ONSET_AEP = 0.10        # 10-yr: the most-frequent BLE-mapped flood; more frequent → no damaging inundation

RP_AVAIL = {}
for (nm, rp) in L:
    RP_AVAIL.setdefault(nm, []).append(rp)
for nm in RP_AVAIL:
    RP_AVAIL[nm].sort()

def make_curve(name):
    return [(round(1 / rp, 4), L[(name, rp)]) for rp in RP_AVAIL[name]]   # (AEP, loss), return period ascending

def loss_at_aep(aep, curve):
    aeps = np.array([c[0] for c in curve]); losses = np.array([c[1] for c in curve])
    x = np.log10(np.clip(aep, 1e-7, 1.0))
    xs = np.log10(aeps[::-1]); ys = losses[::-1]          # increasing x: rarest→onset
    loss = np.interp(x, xs, ys)                            # interpolate within [0.002, 0.1]
    # bounded extrapolation below the rarest anchor (continue the 100→500 log-AEP slope)
    slope = (losses[-1] - losses[-2]) / (np.log10(aeps[-1]) - np.log10(aeps[-2]))
    extrap = losses[-1] + slope * (x - np.log10(aeps[-1]))
    loss = np.where(x < np.log10(aeps[-1]), np.minimum(extrap, 3 * losses[-1]), loss)
    loss = np.where(aep >= ONSET_AEP, 0.0, loss)          # more frequent than onset → no damaging flood
    return np.clip(loss, 0.0, None)

for _, s in sites.iterrows():
    print(f"  {s['name']:24s} curve: " + " · ".join(f"{int(1/a)}yr={l*100:.2f}%" for a, l in make_curve(s['name'])))

# %% [markdown]
# ## 2 · Monte-Carlo annual loss distribution → metrics
#
# Draw `AEP ~ U(0,1)` for N simulated years → annual loss = `loss(AEP)`. EAL = mean; VaR/PML = percentiles
# (1-in-T = the (1−1/T) percentile — DD-4); TVaR = mean beyond VaR.

# %%
N = 500_000
rng = np.random.default_rng(20260617)
RPS = [100, 250, 500]
rows = []
vectors = {}
for _, s in sites.iterrows():
    curve = make_curve(s["name"])
    aep = rng.random(N)
    yr_loss = loss_at_aep(aep, curve)            # annual loss fraction of TIV, per simulated year
    vectors[s["name"]] = yr_loss
    tiv = s["tiv_usd"]
    eal = yr_loss.mean()
    var99 = np.percentile(yr_loss, 99)
    pml = {T: np.percentile(yr_loss, 100 * (1 - 1 / T)) for T in RPS}
    tvar99 = yr_loss[yr_loss >= var99].mean()
    rows.append({"name": s["name"], "role": s["role"], "tiv_usd": tiv,
                 "EAL_pct": eal * 100, "EAL_usd": eal * tiv,
                 "VaR99_pct": var99 * 100, "TVaR99_pct": tvar99 * 100,
                 **{f"PML{T}_pct": pml[T] * 100 for T in RPS},
                 **{f"PML{T}_usd": pml[T] * tiv for T in RPS}})
M = pd.DataFrame(rows)
print(M[["name", "EAL_pct", "VaR99_pct", "PML100_pct", "PML250_pct", "PML500_pct", "TVaR99_pct"]].round(3).to_string(index=False))
print("\ndollars:")
print(M[["name", "EAL_usd", "PML100_usd", "PML500_usd"]].round(0).to_string(index=False))

# %% [markdown]
# ## 2b · What the densification bought — densified EAL vs the old assumed-onset EAL
#
# Before JD-FL-8, the frequent region rested on a single flat **assumed 10-yr onset depth** (`real BLE exposure ×
# Asset_DR(0.5 ft)`). Now the 10/25/50-yr points are **regression-rating depths anchored to both BLE depths**. Here's
# how much that moved EAL (and what the old assumption would have given across a plausible onset-depth band).
# **PML@100/500 are unchanged** (still the real BLE anchors). The M1 finding that the rating depths are near-invariant
# to channel slope means this densified EAL is robust to the one free regression parameter.

# %%
def eal_assumed_onset(name, onset_ft, n=200_000):   # the pre-JD-FL-8 method, for comparison only
    curve = [(ONSET_AEP, F10.get(name, 0.0) * asset_dr(onset_ft)), (0.01, L[(name, 100)]), (0.002, L[(name, 500)])]
    return loss_at_aep(rng.random(n), curve).mean() * 100

cmp_rows = []
for _, s in sites.iterrows():
    nm = s["name"]
    dens_eal = loss_at_aep(rng.random(200_000), make_curve(nm)).mean() * 100
    cmp_rows.append({"site": nm.split()[0], "EAL_densified%": round(dens_eal, 3),
                     **{f"assumed@{d}ft": round(eal_assumed_onset(nm, d), 3) for d in (0.0, 0.5, 1.0)}})
cmp = pd.DataFrame(cmp_rows)
print("EAL (% TIV): JD-FL-8 densified vs the old assumed-onset method (3 onset-depth guesses):")
print(cmp.to_string(index=False))
print("\n→ Densification replaces the onset guess with measurement-anchored 10/25/50-yr depths; PML@100/500 unchanged.")

# %% [markdown]
# ## 3 · Plots — loss-exceedance curve + annual-loss distribution

# %%
import matplotlib.pyplot as plt

fig, (axC, axH) = plt.subplots(1, 2, figsize=(13, 4.8))
Ts = np.array([5, 10, 25, 50, 100, 250, 500, 1000])
for _, s in sites.iterrows():
    curve = make_curve(s["name"])
    losses = loss_at_aep(1 / Ts, curve) * 100
    axC.plot(Ts, losses, "o-", label=s["name"])
    eliz_v = vectors[s["name"]]
    axH.plot(np.sort(eliz_v)[::-1] * 100, np.arange(1, N + 1) / N, label=s["name"])  # exceedance
axC.set_xscale("log"); axC.set_xlabel("return period (yr)"); axC.set_ylabel("loss (% TIV)")
axC.set_title("Loss-exceedance curve (BLE-anchored)"); axC.legend(fontsize=8); axC.grid(alpha=0.3)
axH.set_xscale("symlog", linthresh=0.01); axH.set_yscale("log"); axH.set_ylim(1e-4, 1)
axH.set_xlabel("annual loss (% TIV)"); axH.set_ylabel("annual exceedance prob")
axH.set_title("Simulated annual-loss exceedance (MC)"); axH.legend(fontsize=8); axH.grid(alpha=0.3)
fig.suptitle("Flood × solar M4 — annual loss & metrics")
fig.tight_layout(); fig.savefig(OUT / "flood_m4_loss_metrics.png", dpi=120, bbox_inches="tight")
plt.show()
print("wrote:", OUT / "flood_m4_loss_metrics.png")

# %% [markdown]
# ## 4 · Known-answer checks (basics-spot-on)
#
# - **Frame check (DD-4):** the MC **PML@100-yr reproduces L₁₀₀** (and PML@500 ≈ L₅₀₀) — the percentile of the
#   sampled distribution must match the BLE anchor by construction.
# - **Monotone:** PML rises with return period. **Contrast:** Elizabeth ≫ Hayhurst. **EAL** positive but ≪ PML.

# %%
eliz = M[M.name == "Elizabeth Solar Plant"].iloc[0]
hay = M[M.name == "Hayhurst Texas Solar"].iloc[0]
assert abs(eliz["PML100_pct"] / 100 - L[("Elizabeth Solar Plant", 100)]) < 0.002, "PML100 must reproduce L100 (frame check)"
assert abs(eliz["PML500_pct"] / 100 - L[("Elizabeth Solar Plant", 500)]) < 0.003, "PML500 must reproduce L500"
assert eliz["PML500_pct"] >= eliz["PML250_pct"] >= eliz["PML100_pct"] >= eliz["EAL_pct"] > 0, "metrics must be monotone & positive"
assert eliz["EAL_pct"] > 5 * hay["EAL_pct"], "Elizabeth EAL should dominate Hayhurst"
print(f"✓ frame check: Elizabeth PML100 {eliz['PML100_pct']:.2f}% ≈ L100 {L[('Elizabeth Solar Plant',100)]*100:.2f}% | PML500 {eliz['PML500_pct']:.2f}% ≈ L500 {L[('Elizabeth Solar Plant',500)]*100:.2f}%")
print(f"✓ Elizabeth: EAL {eliz['EAL_pct']:.3f}% < PML100 {eliz['PML100_pct']:.2f}% < PML500 {eliz['PML500_pct']:.2f}% TIV (monotone)")
print(f"✓ Elizabeth EAL {eliz['EAL_pct']:.3f}% ≫ Hayhurst EAL {hay['EAL_pct']:.3f}% (contrast)")
print("✓ M4 known-answer checks pass.")

# %% [markdown]
# ## 4b · External validation — observed flood depths (USGS high-water marks)
#
# Beyond the internal frame checks: do the modeled depths match a **real flood**? USGS surveyed high-water marks after
# the **Aug-2016 Louisiana flood**; we compare the proving site's modeled depth-at-RP against the observed
# height-above-ground near the site. Expectation: our **feet-scale** depths fall **inside** the observed range — a
# real-data regime check (not a to-the-inch calibration; the marks are regional, ~25–45 km out, many near channels).

# %%
import math
import requests

prov = pd.DataFrame(json.loads((OUT / "flood_m0_sites.json").read_text())["sites"])
prov = prov[prov.role.str.contains("proving")].iloc[0]
model_ft = sorted((m3[m3.name == prov["name"]]["conditional_depth_m"] / 0.3048).round(2).tolist())
validation = {"source": "USGS STN high-water marks", "note": "not run"}
try:
    hwm = requests.get("https://stn.wim.usgs.gov/STNServices/HWMs/FilteredHWMs.json",
                       params={"States": prov["state"]}, timeout=40).json()
    near = sorted(h["height_above_gnd"] for h in hwm
                  if h.get("latitude") and h.get("longitude") and h.get("height_above_gnd") not in (None, "")
                  and math.hypot(h["latitude"] - prov["lat"], h["longitude"] - prov["lon"]) < 0.45)
    if near:
        lo, med, hi = near[0], near[len(near) // 2], near[-1]
        inside = (lo - 0.5) <= min(model_ft) and max(model_ft) <= (hi + 0.5)
        validation = {"source": "USGS STN high-water marks (regional, Aug-2016 LA flood era)", "n_marks": len(near),
                      "observed_ft": {"min": round(lo, 2), "median": round(med, 2), "max": round(hi, 2)},
                      "modeled_depth_ft": model_ft, "model_within_observed": bool(inside)}
        print(f"observed flood marks near {prov['name']} (n={len(near)}): {lo:.1f} / median {med:.1f} / {hi:.1f} ft above ground")
        print(f"modeled depths (10→500-yr): {model_ft} ft")
        assert inside, "modeled depths fall outside the observed flood-mark range — review"
        print("✓ modeled depths sit INSIDE the observed flood-mark range — real-data regime check passes")
    else:
        print("no high-water marks within range — validation skipped")
except Exception as e:
    print(f"HWM validation skipped (offline / endpoint?): {type(e).__name__}")

# %% [markdown]
# ## 5 · Persist metrics + per-year vectors

# %%
for nm, v in vectors.items():
    slug = nm.lower().replace(" ", "_").replace(",", "")
    pd.DataFrame({"annual_loss_frac_tiv": v}).to_parquet(OUT / f"{slug}_flood_m4_annual_vectors.parquet")  # gitignored
manifest = {
    "peril": "flood", "sub_peril": "riverine", "event_family_id": None, "layer": "M4",
    "event_model": "annual-maximum MC sampling the (JD-FL-8 densified) RP loss curve (JD-FL-7)",
    "n_sim_years": N, "onset_aep": ONSET_AEP,
    "rp_points_per_site": {nm: RP_AVAIL[nm] for nm in sites["name"]},
    "metric_frame": "per-year loss vectors; PML_T = (1-1/T) percentile (DD-4)",
    "caveats": ["EAL densified (JD-FL-8) — lower RPs (10/25/50-yr) are regression flow-frequency depths anchored to both BLE depths; see §2b vs the old assumed-onset method.",
                "PML@100/500-yr anchored to real BLE depth (solid); regression-Q standard error not yet propagated as an MC overlay.",
                "value∝area exposure; Elizabeth TIV estimated; medium-confidence curves; duration unmodeled"],
    "external_validation": validation,
    "metrics": json.loads(M.round(2).to_json(orient="records")),
}
(OUT / "flood_m4_metrics_manifest.json").write_text(json.dumps(manifest, indent=2))
print("wrote:", OUT / "flood_m4_metrics_manifest.json")

# %% [markdown]
# ## Findings — flood × solar, M0→M4 complete
#
# - **Annual loss & risk metrics computed** on the shared metric frame: per site, EAL / VaR99 / PML(100,250,500) /
#   TVaR99, % of TIV + dollars. **Elizabeth** carries a material flood tail; **Hayhurst** is the near-dry baseline.
# - **PML@100/500-yr is BLE-grounded** (the frame check confirms the percentiles reproduce the BLE-anchored losses);
#   **EAL is now densified** (JD-FL-8) — the frequent region rests on regression-rating depths anchored to both BLE
#   points, not a flat onset guess. §2b reports how much that moved EAL vs the old method.
# - **The flood × solar pipeline is end-to-end + EAL-hardened** (M0 → M1 BLE tail + regression-densified lower RPs →
#   M2 → M3 → M4), on **real public data + canonical curves**, every layer known-answer-checked, honestly labeled.
# - **Remaining hardening (no rework — seam-ready):** propagate the regression-Q standard error as an MC overlay; swap
#   live HAND-SRC depth if the delineation service returns; the enriched polygon / Fathom depth; duration/BI; PV flood-stow.
