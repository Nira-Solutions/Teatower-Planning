"""
_forecast_s48_s52.py — planning merch PRÉVISIONNEL S48 → S52 (Nicolas 16/11/2026).

Règles appliquées (REGLES.md + consignes 16/11) :
  - pool = data/planning_pool_<date>.csv (Actifs, hors télévente, hors centrale) ;
    dernière visite = pool, recalée par les visites S47 planifiées (§10) ;
  - échéance = last + cycle ; une visite simulée relance le cycle ;
  - vendredi : 1er stop centrale Intermarché Gosselies, arrivée avant 10:00 (§15) ;
    S52 : vendredi 25/12 férié -> centrale le jeudi 24/12 ;
  - boutiques Teatower : seule Waterloo dans la tournée (1×/semaine, mar-ven, >= 10:00) ;
    Namur / Liège / Rocourt = livraisons de fin de journée (Marvin, à partir de S49) ;
  - retour base <= 17:00 en S48, <= 15:30 dès S49 (camionnette à Marvin) ;
  - 08:30 départ, 25 min/visite, pause 30 min, trajets OSRM +15 %, hypers avant 12:00,
    contraintes jour/créneau par magasin (CONSTR).
Sortie : planning/_forecast_weeks.json (lu par _forecast_write.py).
"""
import csv, json, re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POOL = ROOT / "data" / "planning_pool_2026-11-16.csv"
TV = ROOT / "data" / "televente_pool_2026-11-16.csv"
MAT = json.loads((ROOT / "data" / "osrm_matrix_cache.json").read_text(encoding="utf-8"))
KEYS = MAT["keys"]; IDX = {k: i for i, k in enumerate(KEYS)}; DUR = MAT["dur"]

def tt(a, b):  # minutes, OSRM +15 %
    return round(DUR[IDX[a]][IDX[b]] / 60 * 1.15)

def hm(m): return f"{m // 60:02d}:{m % 60:02d}"
def M(s): h, m = s.split(":"); return int(h) * 60 + int(m)

# ---- contraintes magasin : jours autorisés (0=lun) + créneau d'arrivée [debut, fin_debut] par jour
ALL = {0, 1, 2, 3, 4}
HYPER_LATEST = M("11:35")
CONSTR = {
    "6999":   dict(days={1}, latest=HYPER_LATEST),                 # Hyper Marche : mardi uniquement
    "121818": dict(days=ALL - {4}, latest=HYPER_LATEST),           # Hyper Ans : jamais le vendredi
    "60001":  dict(days=ALL - {1}, latest=M("11:05")),             # Hyper Boncelles : pas mardi, 7h-11h30
    "59514":  dict(days=ALL - {2}),                                # Welkenraedt : pas mercredi
    "113498": dict(days=ALL - {1}),                                # Materne : pas mardi
    "119815": dict(win={0: (M("12:00"), M("23:00"))}),             # Barchon : fermé lundi matin
    "9461":   dict(days={1, 2, 3, 4}, latest=M("13:35"), win={3: (0, M("17:00"))}),  # St Michel
    "122589": dict(days={0, 4}),                                   # Wellin : lundi / vendredi
    "7283":   dict(days={0, 1}, win={0: (M("13:00"), M("23:00")), 1: (0, M("11:35"))}),  # Bouffioulx
    "5878":   dict(days=ALL - {3}),                                # Remouchamps : pas jeudi
    "5580":   dict(days=ALL - {0}),                                # Fragnée : pas lundi
    "5441":   dict(days=ALL - {1}),                                # Fosses : jamais mardi
    "121874": dict(days=ALL - {2}, latest=M("11:35")),             # ITM Hannut : matin, pas mercredi
    "115879": dict(days={2, 4}, latest=M("11:35")),                # Villers-le-Bouillet : mer/ven matin
    "122255": dict(days=ALL - {2}, win={1: (0, M("11:35"))}),      # Hamoir : ni mardi aprem ni mercredi
    "123302": dict(days={2, 3, 4}),                                # Erezée : pas lundi/mardi
    "59928":  dict(days=ALL - {0}),                                # Dolhain : jamais lundi
    "120035": dict(days=ALL - {2}),                                # Linthout : pas mercredi
    "3223":   dict(days=ALL - {3}),                                # LLN : Mr Snaps absent jeudi
    "2864":   dict(latest=M("11:35")),                             # CM Bastogne Pascalino : matin
    "6821":   dict(latest=M("11:35")),                             # CM Waterloo : 6h-12h
    "125351": dict(days=ALL - {1}),                                # Quadrilatère : pas mardi
    "128635": dict(days={0, 2}, earliest=M("11:00"), latest=M("13:35")),  # Frasnes-lez-Gosselies
    "2952":   dict(days={1, 4}, earliest=M("13:20")),              # Fernelmont : mar/ven >= 13:20
    "5442":   dict(earliest=M("12:30")),                           # Etalle : après 12:30
    "119818": dict(days=ALL - {2}, latest=M("12:30")),             # Ferrières : pas mercredi, tôt
    "TT_WATERLOO": dict(days={1, 2, 3, 4}, earliest=M("10:00")),
}
for p in ("124424", "7760", "125096", "6597", "9046", "113746"):
    CONSTR.setdefault(p, {})["latest"] = HYPER_LATEST
EXCLUDE = {"124364", "7070"}  # centrale (stop fixe vendredi) ; compte de facturation sans magasin

def window(pid, wd):
    c = CONSTR.get(pid, {})
    if wd not in c.get("days", ALL):
        return None
    lo, hi = c.get("earliest", 0), c.get("latest", M("23:00"))
    if wd in c.get("win", {}):
        a, b = c["win"][wd]; lo, hi = max(lo, a), min(hi, b)
    return lo, hi

# ---- semaines
WEEKS = [
    ("s48", date(2026, 11, 23), M("17:00")),
    ("s49", date(2026, 11, 30), M("15:30")),
    ("s50", date(2026, 12, 7), M("15:30")),
    ("s51", date(2026, 12, 14), M("15:30")),
    ("s52", date(2026, 12, 21), M("15:30")),
]
FERIES = {date(2026, 12, 25), date(2026, 12, 9)}  # 09/12 : journee annulee, personne de dispo (Nicolas 17/11)

# visites S47 planifiées (non encore faites) = dernière visite à leur date (§10)
S47 = {}
def load_s47():
    import sys; sys.path.insert(0, str(ROOT / "scripts"))
    import planning_data as P
    mon = date(2026, 11, 16)
    for i, d in enumerate(P.S47["days"]):
        for s in d["stops"]:
            m = re.search(r"#(\d+)\)", s["n"])
            if m: S47[m.group(1)] = mon + timedelta(days=i)

def schedule(route, wd, limit, start_key="BASE", t0=M("08:30"), fixed_first=None):
    """route = liste de (key, service_min). Renvoie (stops[(key,arr,dep)], retour, lunch) ou None."""
    t, cur, out, lunch = t0, start_key, [], None
    seq = ([fixed_first] if fixed_first else []) + route
    for i, (k, svc) in enumerate(seq):
        t += tt(cur, k)
        if fixed_first and i == 0:
            if t > M("09:55"):
                return None
        else:
            w = window(k, wd)
            if w is None: return None
            if t < w[0]: t = w[0]
            if t > w[1]: return None
        arr = t; t += svc
        out.append((k, arr, t))
        cur = k
        if lunch is None and t >= M("12:00"):
            lunch = (t, t + 30); t += 30
    t += tt(cur, "BASE")
    if lunch is None:
        lunch = (t, t + 30); t += 30  # pause prise en fin de tournée si journée courte
    return (out, t, lunch) if t <= limit else None

def main():
    load_s47()
    tv = {r["pid"] for r in csv.DictReader(open(TV, encoding="utf-8"))}
    pool = {r["pid"]: r for r in csv.DictReader(open(POOL, encoding="utf-8"))
            if r["statut"] == "Actif" and r["pid"] not in EXCLUDE and r["pid"] not in tv and r["pid"] in IDX}
    last = {p: date.fromisoformat(r["last_visit"]) for p, r in pool.items()}
    # visites faites mais pas encore visibles dans Odoo (queue S47 : Gilles le 13/11)
    for p, d in {"2952": date(2026, 11, 13)}.items():
        if p in last: last[p] = max(last[p], d)
    for p, d in S47.items():
        if p in last: last[p] = max(last[p], d)
    cycle = {p: int(r["cycle_days"]) for p, r in pool.items()}
    tier = {p: r["tier"] for p, r in pool.items()}
    # forcés S48 (reports du 20/11) : reprises glacés promises
    forced = {"s48": {"124365": "Reprise des thés glacés (demande Vanessa 10/11, reportée du 20/11) — compter, photo, noter sur le bon. Vérifier la réception de S06721.",
                      "116686": "Reprise des thés glacés promise lors de la livraison du 09/11 (reportée du 20/11)."}}
    result = []
    prev = {}
    for wid, mon, limit in WEEKS:
        fri = mon + timedelta(days=4)
        days = [mon + timedelta(days=i) for i in range(5) if mon + timedelta(days=i) not in FERIES]
        centrale_day = days[-1]
        def due(p): return last[p] + timedelta(days=cycle[p])
        cands = {}
        for p in pool:
            dd = due(p)
            gap = (fri - last[p]).days
            if dd <= fri:
                cands[p] = 1000 + (fri - dd).days + (15 if tier[p] == "A" else 0)
            elif dd <= fri + timedelta(days=10) and gap >= 21:
                cands[p] = 100 - (dd - fri).days        # remplissage (avance <= 10 j)
        for p in forced.get(wid, {}):
            cands[p] = 5000
        cands["TT_WATERLOO"] = 3000
        plans = {}
        remaining = dict(cands)
        # ordre de construction : vendredi (centrale) d'abord, puis jours contraints
        order = [centrale_day] + [d for d in days if d != centrale_day]
        for d in order:
            wd = d.weekday()
            ff = ("CENTRALE", 45) if d == centrale_day else None
            best = None
            seeds = sorted([p for p in remaining if window(p, wd)], key=lambda p: -remaining[p] - (400 if CONSTR.get(p, {}).get("days", ALL) != ALL else 0))[:15]
            for seed in [None] + seeds:
                route = [] if seed is None else [(seed, svc(seed))]
                if seed is not None and not schedule(route, wd, limit, fixed_first=ff):
                    continue
                route = grow(route, remaining, wd, limit, ff)
                val = sum(remaining[k] for k, _ in route)
                if best is None or val > best[0]:
                    best = (val, route)
            route = best[1]
            for k, _ in route: remaining.pop(k, None)
            plans[d] = route
        # Réparation : un magasin dû non casé prend la place d'un stop moins prioritaire
        for p in sorted([p for p in remaining if remaining[p] >= 1000], key=lambda p: -remaining[p]):
            best = None
            for d in days:
                wd = d.weekday()
                if window(p, wd) is None: continue
                ff = ("CENTRALE", 45) if d == centrale_day else None
                route = plans[d]
                opts = [(None, route)] + [(q, [x for x in route if x[0] != q]) for q, _ in route
                                          if cands.get(q, 0) < remaining[p] and cands.get(q, 0) < 3000]
                for q, base in opts:
                    for pos in range(len(base) + 1):
                        r2 = base[:pos] + [(p, svc(p))] + base[pos:]
                        sc = schedule(r2, wd, limit, fixed_first=ff)
                        if sc:
                            loss = cands.get(q, 0) if q else -1
                            if best is None or (loss, sc[1]) < best[0]:
                                best = ((loss, sc[1]), d, r2, q)
            if best:
                _, d, r2, q = best
                plans[d] = r2
                remaining.pop(p)
                if q: remaining[q] = cands[q]
        # Waterloo obligatoire : si pas placé, forcer dans le jour le moins coûteux
        if "TT_WATERLOO" in remaining:
            print(f"  [!] {wid} Waterloo non placé")
        week = []
        for d in days:
            wd = d.weekday()
            ff = ("CENTRALE", 45) if d == centrale_day else None
            route = plans[d]
            sch = schedule(route, wd, limit, fixed_first=ff)
            for k, _ in route:
                if k in pool:
                    prev.setdefault(wid, {})[k] = last[k].isoformat()
                    last[k] = d
            week.append(dict(date=d.isoformat(), centrale=bool(ff), stops=[(k, a, b) for k, a, b in sch[0]],
                             ret=sch[1], lunch=sch[2]))
        missed = sorted([p for p in remaining if remaining[p] >= 1000 and p in pool],
                        key=lambda p: -remaining[p])
        result.append(dict(id=wid, monday=mon.isoformat(), limit=limit, days=week,
                           missed=[(p, pool[p]["display_name"] or pool[p]["store_name"], (fri - due(p)).days) for p in missed],
                           forced=forced.get(wid, {})))
        n = sum(len(x["stops"]) for x in week)
        print(f"{wid}: {n} stops, retours {[hm(x['ret']) for x in week]}, non casés dus: {len(missed)}")
    (ROOT / "planning" / "_forecast_weeks.json").write_text(
        json.dumps(dict(weeks=result, prev_visit=prev, last={p: last[p].isoformat() for p in last}), default=str,
                   ensure_ascii=False, indent=1), encoding="utf-8")

def svc(k): return 20 if k == "TT_WATERLOO" else 25

def grow(route, remaining, wd, limit, ff):
    while len(route) < 9:
        base_sch = schedule(route, wd, limit, fixed_first=ff)
        base_ret = base_sch[1] if base_sch else 10**6
        best = None
        for p, w in remaining.items():
            if any(p == k for k, _ in route) or window(p, wd) is None:
                continue
            for pos in range(len(route) + 1):
                r2 = route[:pos] + [(p, svc(p))] + route[pos:]
                s = schedule(r2, wd, limit, fixed_first=ff)
                if not s: continue
                add = s[1] - base_ret - svc(p)
                maxadd = 45 if w >= 1000 else 20
                if add > maxadd: continue
                score = w / (max(add, 0) + 10)
                if best is None or score > best[0]:
                    best = (score, r2)
        if not best: break
        route = best[1]
    return route

if __name__ == "__main__":
    main()
