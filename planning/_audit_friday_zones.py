"""Audit large des clients GMS sur la route vendredi 15/05.
Scan Famenne (69xx) + Lux Nord (6800-6900) + Hainaut Est sur trajet BLC (E411+R3+E42 = 5xxx sud, 6xxx ouest, 7xxx)."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import xmlrpc.client
from datetime import datetime, timedelta

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


def sr(model, domain, fields, limit=None, order=None):
    kw = {"fields": fields}
    if limit:
        kw["limit"] = limit
    if order:
        kw["order"] = order
    return models.execute_kw(DB, uid, PWD, model, "search_read", [domain], kw)


# Already planned S20 (don't list again)
PLANNED = {
    123346, 123294, 2913, 122995,  # lundi
    2777, 3191, 5729, 50967, 3223, 10134,  # mardi
    113498, 3000, 2821, 5441, 123069,  # mercredi
    123301, 2811, 2979, 8159, 3120, 123466,  # vendredi v5
}
# Visited S19 (don't suggest revisit)
VISITED_S19 = {
    123345, 122944, 123303, 123189,  # lundi+mercredi S19 cas connus
    # AD Bastogne, CM Hannut, ITM Hannut, Delhaize Ottignies, Florenville, Boncelles, Fleron, ...
    2864,  # Pascalino CM Bastogne (alt)
    2860,  # AD Bastogne SA Marer estimate
    7692,  # AD Rochefort (excluded)
    2905,  # Beauraing (excluded)
}

# Famenne + Marche → BLC trajet zones
ZIPS_FAMENNE = ["6900", "6940", "6990", "6997"]
ZIPS_NORTH_LUX = ["6800", "6810", "6830", "6840", "6850", "6870", "6880"]
ZIPS_SOUTH_NAMUR_HAINAUT = [
    "5000", "5060", "5070", "5080", "5100", "5170",  # Namur (partial)
    "5500", "5530", "5555", "5570", "5580", "5590",  # Dinant area
    "5650", "5660",  # Walcourt area
    "5300", "5380", "5377", "5340",  # Andenne / Ohey
]
ZIPS_HAINAUT_ROUTE = [
    "6000", "6001", "6010", "6020", "6030", "6040", "6041", "6042", "6043", "6044",  # Charleroi
    "6060", "6061", "6110", "6120", "6140", "6150",  # Anderlues etc
    "6180", "6182", "6183",  # Courcelles
    "6200", "6220", "6230", "6240", "6280",  # Gerpinnes etc
    "7000", "7010", "7020", "7030", "7040", "7050", "7060", "7080", "7090", "7100", "7110", "7170", "7180", "7190",
    "7800", "7860",  # Ath/Lessines
]

ALL_ZIPS = ZIPS_FAMENNE + ZIPS_NORTH_LUX + ZIPS_SOUTH_NAMUR_HAINAUT + ZIPS_HAINAUT_ROUTE


def fetch_partners(zips):
    return sr(
        "res.partner",
        [("category_id", "in", [27]), ("zip", "in", zips)],
        ["id", "name", "zip", "city", "street", "phone", "email", "comment", "sale_warn", "sale_warn_msg"],
    )


partners = fetch_partners(ALL_ZIPS)
print(f"# {len(partners)} partners GMS scannés sur {len(ALL_ZIPS)} codes postaux")

# Filter relevant: not planned, not S19 visited, not Arret
since = (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d")
candidates = []
arret_in_zone = []
no_so = []
visited_recent_S19 = []

for p in partners:
    if p["id"] in PLANNED:
        continue
    arret_flag = (p.get("sale_warn") == "block") or ("[ARRET" in (p.get("comment") or ""))
    if arret_flag:
        arret_in_zone.append(p)
        continue

    sos = sr(
        "sale.order",
        [("partner_id", "child_of", p["id"]), ("state", "in", ["sale", "done"]), ("date_order", ">=", since)],
        ["name", "date_order", "amount_total"],
        order="date_order desc",
    )
    if not sos:
        no_so.append(p)
        continue

    last = sos[0]
    days_since = (datetime.now() - datetime.strptime(last["date_order"][:10], "%Y-%m-%d")).days
    avg = sum(s["amount_total"] for s in sos) / len(sos)
    total = sum(s["amount_total"] for s in sos)

    if days_since < 8:
        visited_recent_S19.append((p, last, days_since, avg, total))
        continue

    p["_metrics"] = {"days_since": days_since, "avg": avg, "total": total, "so_count": len(sos), "last_name": last["name"], "last_date": last["date_order"][:10]}
    candidates.append(p)

# Tier classification
def tier(avg, total):
    if avg >= 500 and total >= 4000:
        return "A"
    if avg >= 300 and total >= 2000:
        return "B"
    return "C"


candidates.sort(key=lambda p: (-p["_metrics"]["days_since"], -p["_metrics"]["avg"]))


def overdue(t, dys):
    if t == "A" and dys > 20:
        return True
    if t == "B" and dys > 35:
        return True
    if t == "C" and dys > 50:
        return True
    return False


print(f"\n## {len(candidates)} candidats GMS Actif avec SO 12 derniers mois (HORS planning + HORS S19 + HORS Arret)")
print(f"\n### Tier A / B OVERDUE (priorité) :\n")
for p in candidates:
    m = p["_metrics"]
    t = tier(m["avg"], m["total"])
    ov = overdue(t, m["days_since"])
    if not ov:
        continue
    if t not in ("A", "B"):
        continue
    flag = "🔴 OVERDUE" if ov else ""
    print(f"- **{p['name']}** (#{p['id']}) — {p['zip']} {p.get('city','')} — Tier {t} {flag} {m['days_since']}j — last {m['last_name']} {m['last_date']} — avg {m['avg']:.0f}€, total {m['total']:.0f}€, {m['so_count']} SO")

print(f"\n### Tier C OVERDUE :\n")
for p in candidates:
    m = p["_metrics"]
    t = tier(m["avg"], m["total"])
    if t != "C" or not overdue(t, m["days_since"]):
        continue
    print(f"- **{p['name']}** (#{p['id']}) — {p['zip']} {p.get('city','')} — Tier C 🔴 {m['days_since']}j — last {m['last_name']} {m['last_date']} — avg {m['avg']:.0f}€, total {m['total']:.0f}€")

print(f"\n### Tier A / B NON-OVERDUE (zone trajet, info) :\n")
for p in candidates:
    m = p["_metrics"]
    t = tier(m["avg"], m["total"])
    if t not in ("A", "B") or overdue(t, m["days_since"]):
        continue
    print(f"- {p['name']} (#{p['id']}) — {p['zip']} — Tier {t} — {m['days_since']}j — avg {m['avg']:.0f}€")

print(f"\n### {len(arret_in_zone)} magasins ARRET dans la zone (info, à NE PAS visiter) :")
for p in arret_in_zone[:20]:
    print(f"- {p['name']} (#{p['id']}) {p['zip']}")

print(f"\n### {len(no_so)} magasins SANS SO 12 mois (dormant, hors mission merch) :")
for p in no_so[:20]:
    print(f"- {p['name']} (#{p['id']}) {p['zip']}")

print(f"\n### {len(visited_recent_S19)} magasins visités <8j (à NE PAS revisiter cette semaine) :")
for p, last, dys, avg, total in visited_recent_S19:
    print(f"- {p['name']} (#{p['id']}) {p['zip']} — last {last['name']} {last['date_order'][:10]} ({dys}j)")
