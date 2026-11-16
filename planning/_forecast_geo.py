"""
_forecast_geo.py — géocode les magasins GMS actifs du pool + points fixes, puis
calcule la matrice de temps de trajet OSRM (secondes, brut). Caches :
  data/geo_gms_cache.json      {cle: [lat, lon, source]}
  data/osrm_matrix_cache.json  {"keys": [...], "dur": [[...]]}
Usage : python planning/_forecast_geo.py data/planning_pool_YYYY-MM-DD.csv
"""
import csv, json, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEO = ROOT / "data" / "geo_gms_cache.json"
MAT = ROOT / "data" / "osrm_matrix_cache.json"
UA = {"User-Agent": "route-planner/1.0"}

FIXED = {
    "BASE": "Zone d'activité Nord 33, 5377 Baillonville",
    "CENTRALE": "Rue du Colombier 9, 6041 Gosselies",
    "TT_WATERLOO": "Chaussée de Bruxelles 155, 1410 Waterloo",
    "124365": "Rue Philippe Monnoyer 62, 6180 Courcelles",
}
FIXED_COORDS = {"BASE": (50.3340, 5.2830), "CENTRALE": (50.4680, 4.4550)}


def postal():
    out = {}
    for line in (ROOT / "data" / "geo" / "BE.txt").read_text(encoding="utf-8").splitlines():
        f = line.split("\t")
        out.setdefault(f[1], (float(f[9]), float(f[10])))
        out.setdefault(f[2].casefold(), (float(f[9]), float(f[10])))
    return out


def nominatim(q):
    u = ("https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=be&q="
         + urllib.parse.quote(q))
    try:
        d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20).read())
        time.sleep(1.1)
        return (float(d[0]["lat"]), float(d[0]["lon"])) if d else None
    except Exception:
        time.sleep(1.1)
        return None


def main(pool_csv):
    rows = [r for r in csv.DictReader(open(pool_csv, encoding="utf-8")) if r["statut"] == "Actif"]
    geo = json.loads(GEO.read_text(encoding="utf-8")) if GEO.exists() else {}
    pc = postal()
    addrs = dict(FIXED)
    for r in rows:
        addrs[r["pid"]] = f'{r["street"]}, {r["zip"]} {r["city"]}'.strip(", ")
    for k, a in addrs.items():
        if k in geo:
            continue
        if k in FIXED_COORDS:
            geo[k] = [*FIXED_COORDS[k], "fixed"]
            continue
        c = nominatim(a)
        src = "nominatim"
        if not c:
            r = next((x for x in rows if x["pid"] == k), None)
            if r:
                c = nominatim(f'{r["zip"]} {r["city"]}') if r["zip"] else None
            src = "nominatim-ville"
        if not c:
            r = next((x for x in rows if x["pid"] == k), {})
            c = pc.get(r.get("zip", "")) or pc.get(r.get("city", "").casefold())
            src = "cp"
        if c:
            geo[k] = [c[0], c[1], src]
        print(k, a, geo.get(k))
    GEO.write_text(json.dumps(geo, indent=1, ensure_ascii=False), encoding="utf-8")

    keys = [k for k in addrs if k in geo]
    n = len(keys)
    dur = [[0.0] * n for _ in range(n)]
    B = 50
    for i0 in range(0, n, B):
        for j0 in range(0, n, B):
            si = list(range(i0, min(n, i0 + B)))
            dj = list(range(j0, min(n, j0 + B)))
            pts = si + [j for j in dj if j not in si]
            coords = ";".join(f"{geo[keys[p]][1]},{geo[keys[p]][0]}" for p in pts)
            src = ";".join(str(pts.index(i)) for i in si)
            dst = ";".join(str(pts.index(j)) for j in dj)
            u = (f"http://router.project-osrm.org/table/v1/driving/{coords}"
                 f"?sources={src}&destinations={dst}&annotations=duration")
            d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read())
            for a, i in enumerate(si):
                for b, j in enumerate(dj):
                    dur[i][j] = d["durations"][a][b]
            time.sleep(1)
    MAT.write_text(json.dumps({"keys": keys, "addrs": addrs, "dur": dur}), encoding="utf-8")
    print(f"[+] {n} points, matrice OK")


if __name__ == "__main__":
    main(sys.argv[1])
