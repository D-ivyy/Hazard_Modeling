#!/usr/bin/env python
"""LIVE probe of wind-hazard data sources for the 02_spc_storm_record notebook.

Sources probed:
  1) SPC tornado tracks (WCM "actual_tornadoes" CSV)  -- tornado path geometry spine
  2) SPC severe-WIND reports (WCM "actual_wind" CSV)   -- convective wind freq/severity
  3) NOAA Storm Events Database bulk CSV (NCEI)         -- episode structure + magnitude type

Run:  .venv/bin/python scripts/wind_data_probe.py [step]
where step in {versions, tornado, wind, stormevents, all}
"""
import sys, os, io, gzip, math, re, json
import requests

ROOT = "/Users/divy/code/work/infrasure_git_codes/Hazard_modeling"
RAW = os.path.join(ROOT, "data", "wind", "raw")
os.makedirs(RAW, exist_ok=True)

SITES = {
    "traverse_ok": (35.713427, -98.728532),
    "shepherds_or": (45.653389, -120.036724),
}
RADIUS_KM = 150.0

UA = {"User-Agent": "infrasure-hazard-modeling/0.1 (data-access probe)"}


def haversine_km(lat1, lon1, lat2, lon2):
    import numpy as np
    R = 6371.0088
    lat1 = np.radians(lat1); lon1 = np.radians(lon1)
    lat2 = np.radians(lat2); lon2 = np.radians(lon2)
    dlat = lat2 - lat1; dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    return 2*R*np.arcsin(np.sqrt(a))


def head(url, **kw):
    try:
        r = requests.head(url, headers=UA, timeout=30, allow_redirects=True, **kw)
        return r.status_code, r.headers.get("Content-Length"), r.headers.get("Content-Type"), r.url
    except Exception as e:
        return ("ERR", str(e), None, url)


def get(url, dest=None, **kw):
    r = requests.get(url, headers=UA, timeout=120, **kw)
    r.raise_for_status()
    if dest:
        with open(dest, "wb") as f:
            f.write(r.content)
    return r


def versions():
    import pandas, numpy
    print("pandas", pandas.__version__, "| numpy", numpy.__version__, "| requests", requests.__version__)
    try:
        import geopandas, shapely
        print("geopandas", geopandas.__version__, "| shapely", shapely.__version__)
    except Exception as e:
        print("geopandas/shapely:", e)


def probe_wcm_index():
    """List the WCM directory to find current filenames/years."""
    print("\n=== WCM directory listing https://www.spc.noaa.gov/wcm/ ===")
    try:
        r = get("https://www.spc.noaa.gov/wcm/")
        names = re.findall(r'href="([^"?][^"]*?)"', r.text)
        interesting = [n for n in names if re.search(r'actual|tornado|wind|hail|\.csv', n, re.I)]
        for n in sorted(set(interesting)):
            print("  ", n)
    except Exception as e:
        print("WCM index error:", e)


def find_tornado_url():
    """Try a range of years, return first that exists (newest first)."""
    base = "https://www.spc.noaa.gov/wcm/data/"
    for yr in range(2025, 2018, -1):
        url = f"{base}1950-{yr}_actual_tornadoes.csv"
        sc, cl, ct, final = head(url)
        print(f"  try {url} -> {sc} len={cl}")
        if sc == 200:
            return url
    return None


def find_wind_url():
    # LIVE-VERIFIED 2026-06: the WCM severe-WIND record is published ONLY as a
    # multi-year ZIP (1955-{yr}_wind.csv.zip), NOT as a bare "1955-YYYY_actual_wind.csv"
    # (that "_actual_" naming is the TORNADO convention; the bare wind CSV 404s).
    # Per-year YYYY_wind.csv files also exist but cover one year each.
    base = "https://www.spc.noaa.gov/wcm/data/"
    for yr in range(2025, 2018, -1):
        url = f"{base}1955-{yr}_wind.csv.zip"
        sc, cl, ct, final = head(url)
        print(f"  try {url} -> {sc} len={cl}")
        if sc == 200:
            return url
    return None


def step_tornado():
    import pandas as pd, numpy as np
    print("\n########## SOURCE 1: SPC tornado tracks ##########")
    probe_wcm_index()
    print("\n=== SVRGIS page check https://www.spc.noaa.gov/gis/svrgis/ ===")
    sc, cl, ct, final = head("https://www.spc.noaa.gov/gis/svrgis/")
    print("  svrgis page:", sc, ct, final)
    print("\n=== locate current tornado CSV ===")
    url = find_tornado_url()
    print("CHOSEN tornado URL:", url)
    if not url:
        print("NO tornado URL found")
        return
    dest = os.path.join(RAW, "spc_actual_tornadoes.csv")
    get(url, dest)
    sz = os.path.getsize(dest)
    print(f"downloaded {sz} bytes -> {dest}")
    df = pd.read_csv(dest)
    print("TOTAL ROWS:", len(df))
    print("COLUMNS:", list(df.columns))
    print("DTYPES:\n", df.dtypes)
    print("\nFIRST 3 ROWS:\n", df.head(3).to_string())
    print("\nYEAR RANGE:", df['yr'].min(), "-", df['yr'].max())

    # near-site counts on start point (slat/slon)
    for name, (lat, lon) in SITES.items():
        d = haversine_km(df['slat'].values, df['slon'].values, lat, lon)
        near = df[d <= RADIUS_KM].copy()
        print(f"\n--- {name}: tornadoes with START within {RADIUS_KM} km: {len(near)} ---")
        if name == "traverse_ok" and len(near):
            print("  mag distribution (F/EF, -9=unknown):")
            print(near['mag'].value_counts(dropna=False).sort_index().to_string())
            print("  path len (mi) stats:", near['len'].describe().to_dict())
            print("  path wid (yd) stats:", near['wid'].describe().to_dict())
            print("  fc (F-scale flag, 1=estimated post-2007 EF map?) value_counts:")
            if 'fc' in near.columns:
                print(near['fc'].value_counts(dropna=False).to_string())

    # POPULATION BIAS: counts by decade near Traverse + CONUS
    lat, lon = SITES['traverse_ok']
    d = haversine_km(df['slat'].values, df['slon'].values, lat, lon)
    near = df[d <= RADIUS_KM].copy()
    df['decade'] = (df['yr'] // 10) * 10
    near['decade'] = (near['yr'] // 10) * 10
    print("\n=== POPULATION/REPORTING BIAS (AWN-1) ===")
    print("CONUS-wide tornado counts by decade:")
    print(df.groupby('decade').size().to_string())
    print("\nNear-Traverse tornado counts by decade:")
    print(near.groupby('decade').size().to_string())
    print("\nCONUS weak (mag<=1) vs strong by decade (share of EF0/EF1):")
    df['weak'] = df['mag'] <= 1
    tab = df.groupby('decade')['weak'].agg(['sum', 'count'])
    tab['weak_share'] = tab['sum'] / tab['count']
    print(tab.to_string())
    print("\nF->EF break: mag distribution for 2006 vs 2007 vs 2008 (CONUS):")
    for y in (2006, 2007, 2008):
        sub = df[df['yr'] == y]
        print(f"  {y}: n={len(sub)} mag counts={sub['mag'].value_counts(dropna=False).sort_index().to_dict()}")
    print("\n'-9' / missing mag convention (CONUS counts of mag==-9):", int((df['mag'] == -9).sum()))
    print("rows with mag == -9 by decade:")
    print(df[df['mag'] == -9].groupby('decade').size().to_string())


def step_wind():
    import pandas as pd, numpy as np
    print("\n########## SOURCE 2: SPC severe WIND reports ##########")
    url = find_wind_url()
    print("CHOSEN wind URL:", url)
    if not url:
        print("NO wind URL found")
        return
    import zipfile
    if url.endswith(".zip"):
        zdest = os.path.join(RAW, os.path.basename(url))
        get(url, zdest)
        print("downloaded", os.path.getsize(zdest), "bytes ->", zdest)
        with zipfile.ZipFile(zdest) as zf:
            member = zf.namelist()[0]
            zf.extract(member, RAW)
            dest = os.path.join(RAW, member)
        print("unzipped member ->", dest, os.path.getsize(dest), "bytes")
    else:
        dest = os.path.join(RAW, "spc_wind.csv")
        get(url, dest)
        print("downloaded", os.path.getsize(dest), "bytes ->", dest)
    df = pd.read_csv(dest)
    print("TOTAL ROWS:", len(df))
    print("COLUMNS:", list(df.columns))
    print("\nFIRST 3 ROWS:\n", df.head(3).to_string())
    print("\nYEAR RANGE:", df['yr'].min(), "-", df['yr'].max())
    print("\nmag (knots) describe:", df['mag'].describe().to_dict())
    if 'mt' in df.columns:
        print("mt (magnitude type EG/MG/MS/etc) value_counts:")
        print(df['mt'].value_counts(dropna=False).to_string())
    for name, (lat, lon) in SITES.items():
        d = haversine_km(df['slat'].values, df['slon'].values, lat, lon)
        near = df[d <= RADIUS_KM]
        print(f"\n--- {name}: severe-wind reports within {RADIUS_KM} km: {len(near)} ---")
        if len(near):
            print("  mag(kt) describe:", near['mag'].describe().to_dict())
            if 'mt' in near.columns:
                print("  mt counts:", near['mt'].value_counts(dropna=False).to_dict())


def find_stormevents_year():
    """List the NCEI dir and find a recent details file."""
    base = "https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/"
    r = get(base)
    files = re.findall(r'href="(StormEvents_details-ftp_v1\.0_d\d{4}_c\d{8}\.csv\.gz)"', r.text)
    return base, sorted(set(files))


def step_stormevents():
    import pandas as pd, numpy as np
    print("\n########## SOURCE 3: NOAA Storm Events Database ##########")
    base, files = find_stormevents_year()
    print("NCEI dir reachable:", base)
    print("TOTAL details files listed:", len(files))
    print("Recent details filenames:")
    for f in files[-6:]:
        print("  ", f)
    # pick the most recent year details file
    target = files[-1]
    # prefer a complete recent year (not current partial) -- choose year-2 if available
    years = {}
    for f in files:
        m = re.search(r'_d(\d{4})_', f)
        if m:
            years[int(m.group(1))] = f
    yr = sorted(years)[-2] if len(years) >= 2 else sorted(years)[-1]
    target = years[yr]
    url = base + target
    print("\nCHOSEN year:", yr, "file:", target)
    sc, cl, ct, final = head(url)
    print("HEAD:", sc, "Content-Length:", cl, "bytes (~%.1f MB)" % (int(cl)/1e6 if cl and str(cl).isdigit() else 0))
    dest = os.path.join(RAW, target)
    get(url, dest)
    print("downloaded", os.path.getsize(dest), "bytes ->", dest)
    with gzip.open(dest, "rb") as f:
        df = pd.read_csv(f, low_memory=False)
    print("TOTAL ROWS:", len(df))
    print("COLUMNS:", list(df.columns))
    keycols = ['EVENT_TYPE', 'MAGNITUDE', 'MAGNITUDE_TYPE', 'BEGIN_LAT', 'BEGIN_LON',
               'END_LAT', 'END_LON', 'EPISODE_ID', 'EVENT_ID', 'DAMAGE_PROPERTY',
               'TOR_F_SCALE', 'TOR_LENGTH', 'TOR_WIDTH', 'STATE']
    print("\nEVENT_TYPE value_counts (top 25):")
    print(df['EVENT_TYPE'].value_counts().head(25).to_string())
    print("\nMAGNITUDE_TYPE value_counts:")
    print(df['MAGNITUDE_TYPE'].value_counts(dropna=False).to_string())
    print("\nTOR_F_SCALE value_counts:")
    print(df['TOR_F_SCALE'].value_counts(dropna=False).to_string())
    # sample tornado + thunderstorm wind rows
    tor = df[df['EVENT_TYPE'] == 'Tornado']
    print("\nSample Tornado rows (key cols):")
    print(tor[ [c for c in keycols if c in df.columns] ].head(3).to_string())
    tsw = df[df['EVENT_TYPE'] == 'Thunderstorm Wind']
    print("\nSample Thunderstorm Wind rows (key cols):")
    print(tsw[ [c for c in keycols if c in df.columns] ].head(3).to_string())
    # episode grouping demo: an EPISODE_ID with many events
    epcounts = df.groupby('EPISODE_ID').size().sort_values(ascending=False)
    big_ep = epcounts.index[0]
    print(f"\nEPISODE grouping demo: EPISODE_ID={big_ep} has {epcounts.iloc[0]} events:")
    cols2 = [c for c in ['EVENT_ID', 'EVENT_TYPE', 'STATE', 'CZ_NAME', 'BEGIN_DATE_TIME', 'MAGNITUDE', 'MAGNITUDE_TYPE'] if c in df.columns]
    print(df[df['EPISODE_ID'] == big_ep][cols2].head(15).to_string())
    print(f"\nDistinct EPISODE_IDs: {df['EPISODE_ID'].nunique()} | distinct EVENT_IDs: {df['EVENT_ID'].nunique()} | rows: {len(df)}")


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "all"
    if step in ("versions", "all"):
        versions()
    if step in ("tornado", "all"):
        step_tornado()
    if step in ("wind", "all"):
        step_wind()
    if step in ("stormevents", "all"):
        step_stormevents()
