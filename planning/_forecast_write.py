"""
_forecast_write.py — transforme planning/_forecast_weeks.json en semaines S48..S52
au format planning_data.py (ajoutées / remplacées en fin de fichier) + WEEKS.
"""
import csv, json, re, time, urllib.request
from datetime import date, timedelta
from pathlib import Path
from pprint import pformat

ROOT = Path(__file__).resolve().parent.parent
W = json.loads((ROOT / "planning" / "_forecast_weeks.json").read_text(encoding="utf-8"))
POOL = {r["pid"]: r for r in csv.DictReader(open(ROOT / "data" / "planning_pool_2026-11-16.csv", encoding="utf-8"))}
GEO = json.loads((ROOT / "data" / "geo_gms_cache.json").read_text(encoding="utf-8"))
import sys; sys.path.insert(0, str(ROOT / "scripts"))
import planning_data as P

LATEST = {}
for v in vars(P).values():
    if isinstance(v, dict) and "days" in v:
        for d in v["days"]:
            for s in d.get("stops", []):
                m = re.search(r"#(\d+)\)", s.get("n", ""))
                if m: LATEST[m.group(1)] = s

JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
def hm(m): return f"{m // 60:02d}:{m % 60:02d}"
def ddmm(d): return d.strftime("%d/%m")

FIXED = {
    "CENTRALE": dict(n="Centrale Intermarché — Base de Gosselies / Superlog (#124364)", a="Rue du Colombier 9, 6041 Gosselies",
                     c="réception entrepôt — +32 71 25 72 65",
                     rg="livrer AVANT 10:00 | passer par la LOGE DE GARDE puis livrer à la RÉCEPTION DE L’ENTREPÔT"),
    "TT_WATERLOO": dict(n="Boutique Teatower Waterloo", a="Chaussée de Bruxelles 155, 1410 Waterloo",
                        c="équipe boutique Waterloo — +32 2 720 36 04",
                        rg="boutique ouverte à partir de 10:00 | parkings gratuits sur la Chaussée de Bruxelles et les rues adjacentes"),
    "124365": dict(n="Carrefour Market Courcelles (#124365)", a="Rue Philippe Monnoyer 62, 6180 Courcelles",
                   c="accueil / responsable — +32 71 45 22 82"),
}

# Marvin Nicolas (flexi-job) — livraisons boutiques en fin de journée, camionnette dès 15:30
def marvin(d):
    s49_50 = {0: "préparation 13:00-16:00 · livraison Rocourt + Liège 16:00-18:00",
              1: "livraison Namur 16:30-18:00", 2: "repos (camionnette quand même à l’entrepôt à 15:30)",
              3: "préparation 13:00-16:00 · livraison Rocourt + Liège 16:00-18:00",
              4: "livraison Namur 16:30-18:00"}
    s51 = {0: "préparation + livraison Rocourt + Liège 13:00-18:00", 1: "préparation + livraison Namur 13:00-18:00",
           2: "préparation + livraison Rocourt + Liège 13:00-18:00", 3: "préparation + livraison Namur 13:00-18:00",
           4: "livraison Rocourt + Liège + Namur 13:00-18:00 (grosse journée)"}
    s52 = {0: "préparation + livraison Rocourt + Liège 13:00-18:00 (grosse journée)",
           1: "préparation + livraison Namur 13:00-18:00 (grosse journée)",
           2: "livraison Rocourt + Liège + Namur 13:00-18:00 (grosse journée)", 3: "pas de prestation"}
    if d < date(2026, 11, 30): return None
    tab = s49_50 if d < date(2026, 12, 14) else s51 if d < date(2026, 12, 21) else s52
    return "🌙 Camionnette à Marvin (boutiques Teatower, fin de journée) : " + tab.get(d.weekday(), "—")

def km_route(keys):
    pts = ["BASE"] + keys + ["BASE"]
    coords = ";".join(f"{GEO[k][1]},{GEO[k][0]}" for k in pts)
    u = f"http://router.project-osrm.org/route/v1/driving/{coords}?overview=false"
    try:
        d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "route-planner/1.0"}), timeout=30).read())
        time.sleep(1)
        return str(round(d["routes"][0]["distance"] / 1000))
    except Exception:
        return "?"

def city(k):
    if k == "CENTRALE": return "Gosselies"
    if k == "TT_WATERLOO": return "Waterloo"
    if k == "124365": return "Courcelles"
    a = (LATEST.get(k) or {}).get("a") or ""
    m = re.search(r"\b\d{4}\s+([^,(]+)", a)
    c = m.group(1).strip() if m else POOL[k]["city"]
    return c.split(" (")[0].title() if c.isupper() else c.split(" (")[0]

def build_week(w):
    mon = date.fromisoformat(w["monday"]); fri = mon + timedelta(days=4)
    lim = w["limit"]
    days = []
    for d in w["days"]:
        dt = date.fromisoformat(d["date"]); wd = dt.weekday()
        stops, nb_v = [], 0
        lunch_start = d["lunch"][0]
        for i, (k, a, b) in enumerate(d["stops"]):
            if k in FIXED:
                base = dict(FIXED[k])
            else:
                L = LATEST.get(k, {})
                r = POOL[k]
                base = dict(n=L.get("n") or f'{r["display_name"] or r["store_name"]} (#{k})',
                            a=L.get("a") or f'{r["street"]}, {r["zip"]} {r["city"]}'.strip(", "),
                            c=L.get("c") or (f'{r["phone"]}' if r["phone"] else "accueil / responsable rayon — relever le nom"))
                for f in ("st", "re", "rg"):
                    if L.get(f): base[f] = L[f]
            s = {"t": f"{hm(a)} - {hm(b)}"}
            notes = []
            if k == "CENTRALE":
                s.update(k="livr", b=["Livraison", "Centrale Intermarché", "AVANT 10:00"], so="SO à reporter", ls="commande de la semaine", lsc="fresh")
                notes.append("1ᵉʳ stop, départ 08:30 PILE. N° de commande à reporter dès réception (la centrale commande le lundi/mardi). Colis chargés la veille.")
                if dt.weekday() == 3:
                    notes.append("Vendredi 25/12 férié : livraison avancée au jeudi 24/12 — à confirmer avec la centrale.")
            elif k == "TT_WATERLOO":
                prev = dt - timedelta(days=1)
                s.update(k="livr", b=["Dépôt marchandise"], ls="dépôt marchandise", lsc="fresh")
                notes.append(f"DÉPÔT — colis préparé le {JOURS[prev.weekday()].lower()} {ddmm(prev)}.")
            else:
                nb_v += 1
                r = POOL.get(k)
                s["k"] = "visite"
                bad = []
                if r:
                    bad.append(f'Tier {r["tier"]}')
                if k in w["forced"]:
                    bad.append("REPRISE GLACÉS"); notes.append(w["forced"][k])
                s["b"] = bad
                lv = date.fromisoformat(W["prev_visit"][w["id"]][k]) if k in W["prev_visit"].get(w["id"], {}) else None
                if lv:
                    gap = (dt - lv).days
                    cyc = int(POOL[k]["cycle_days"]) if k in POOL else 28
                    if gap > cyc: bad.append(f"{gap - cyc}j OVERDUE")
                    s["ls"] = f"{ddmm(lv)} ({gap}j)"
                    s["lsc"] = "fresh" if gap < 21 else "mid" if gap < 60 else "stale"
            s.update(base)
            if b <= lunch_start and (i + 1 == len(d["stops"]) or d["stops"][i + 1][1] > lunch_start) and lunch_start < d["ret"] - 30:
                notes.append(f"Pause déjeuner 30 min juste après ({hm(lunch_start)}-{hm(lunch_start + 30)}).")
            if notes: s["note"] = " ".join(notes)
            stops.append(s)
        keys = [k for k, _, _ in d["stops"]]
        cities = []
        for k in keys:
            c = city(k)
            if c not in cities: cities.append(c)
        parts = []
        if d["centrale"]: parts.append("1 livraison centrale")
        if "TT_WATERLOO" in keys: parts.append("1 dépôt boutique")
        parts.append(f"{nb_v} visites")
        day = {"h": f"{JOURS[wd]} {ddmm(dt)}", "sub": f"{len(stops)} stops ({', '.join(parts)})",
               "zone": " → ".join(cities), "km": km_route(keys), "ret": hm(d["ret"]), "lim": hm(lim),
               "stops": stops, "addrs": [s["a"] for s in stops]}
        mv = marvin(dt)
        if mv: day["evening"] = mv
        days.append(day)
    if mon == date(2026, 12, 21):
        days.append({"h": "Vendredi 25/12", "sub": "Noël — férié", "zone": "—", "stops": [], "off": "Jour férié : pas de tournée. La livraison centrale Intermarché est avancée au jeudi 24/12."})
    num = int(w["id"][1:])
    note = ("📅 PRÉVISIONNEL — à recaler chaque semaine avec le pool Odoo (commandes, visites réelles, demandes). "
            "🚚 Vendredi matin : livraison centrale Intermarché à Gosselies avant 10:00. 🏪 Boutique Waterloo pendant la tournée ; "
            "Namur, Liège et Rocourt en fin de journée")
    note += " (pas de passage de Gilles)." if num == 48 else " par Marvin (flexi-job)."
    if num >= 49:
        note += " ⏱️ RETOUR À L’ENTREPÔT 15:30 AU PLUS TARD : la camionnette part ensuite avec Marvin."
    if num == 52:
        note += " 🎄 Vendredi 25/12 férié : centrale le jeudi 24/12."
    if num == 48:
        bt = {b: "🌙 fin de journée, hors tournée de Gilles (Marvin ne démarre que le 30/11) — à organiser" for b in ("Namur", "Liège", "Rocourt")}
    else:
        jours = {"Namur": [], "Liège": [], "Rocourt": []}
        for x in days:
            for b in jours:
                if b in x.get("evening", "") and "livraison" in x.get("evening", ""):
                    jours[b].append(x["h"])
        bt = {b: "🌙 livré par <strong>Marvin</strong> en fin de journée : " + (", ".join(v) or "—") for b, v in jours.items()}
    return {"id": w["id"], "bt_txt": bt, "nav": f"S{num} · {ddmm(mon)}-{ddmm(fri)} (prévisionnel)", "active": False,
            "title": f"Semaine du {mon.day} au {fri.day} {'novembre' if fri.month == 11 else 'décembre'} 2026 (S{num}) — prévisionnel",
            "note": note, "days": days}

def main():
    out = []
    for w in W["weeks"]:
        wk = build_week(w)
        out.append(f"{wk['id'].upper()} = {pformat(wk, width=140, sort_dicts=False)}\n")
    p = ROOT / "scripts" / "planning_data.py"
    s = p.read_text(encoding="utf-8")
    head = s.split("\n# ---- PRÉVISIONNEL S48-S52")[0].split("\nWEEKS = [")[0].rstrip() + "\n"
    s = (head + "\n# ---- PRÉVISIONNEL S48-S52 (planning/_forecast_s48_s52.py, Nicolas 16/11/2026)\n"
         + "\n".join(out) + "\nWEEKS = [S47, S48, S49, S50, S51, S52]\n")
    p.write_text(s, encoding="utf-8")
    print("[+] planning_data.py : S48-S52 écrites")

if __name__ == "__main__":
    main()
