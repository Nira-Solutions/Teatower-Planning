"""CA HTVA Carrefour Market / Hyper / Express - S2 2025 (01/07 -> 31/12)."""
import xmlrpc.client, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(m, me, a, k=None): return models.execute_kw(DB, uid, PWD, m, me, a, k or {})

DATE_FROM = "2025-07-01"
DATE_TO = "2025-12-31"

# Patterns Carrefour (Market / Hyper / Express)
# CM = Carrefour Market, CE = Carrefour Express
patterns = [
    re.compile(r"\bcarrefour\s+market\b", re.I),
    re.compile(r"\bcarrefour\s+hyper\b", re.I),
    re.compile(r"\bhyper\s+carrefour\b", re.I),
    re.compile(r"\bcarrefour\s+express\b", re.I),
    re.compile(r"^\s*cm\s+", re.I),        # "CM Bastogne ..."
    re.compile(r"^\s*ce\s+", re.I),        # "CE Xxx ..."
    re.compile(r"^\s*hc\s+", re.I),        # "HC Mons ..."
]

# 1) Cherche les partners
all_carr = call("res.partner", "search_read",
    [[("name", "ilike", "carrefour")]],
    {"fields": ["id", "name", "parent_id", "category_id"], "limit": 5000})

cm_extra = call("res.partner", "search_read",
    [["|", "|", ("name", "=ilike", "CM %"), ("name", "=ilike", "CE %"), ("name", "=ilike", "HC %")]],
    {"fields": ["id", "name", "parent_id", "category_id"], "limit": 5000})

seen = {p["id"]: p for p in all_carr}
for p in cm_extra:
    seen.setdefault(p["id"], p)

# Classifier
def classify(name):
    n = name or ""
    # HYPER : "Hyper Carrefour", "Carrefour Hyper", "Hypermarche/Hypermarkt Carrefour", "HC "
    if re.search(r"\bhyper(?:marche|marché|markt)?\s+carrefour\b|\bcarrefour\s+hyper\b|^\s*hc\s+", n, re.I):
        return "HYPER"
    if re.search(r"\bcarrefour\s+market\b|^\s*cm\s+", n, re.I):
        return "MARKET"
    if re.search(r"\bcarrefour\s+express\b|^\s*ce\s+", n, re.I):
        return "EXPRESS"
    return None

target_partners = []
excluded = []
for pid, p in seen.items():
    c = classify(p["name"])
    if c:
        target_partners.append((pid, p["name"], c))
    else:
        excluded.append((pid, p["name"]))

print(f"Partners Carrefour total trouves : {len(seen)}")
print(f"  - Match Market/Hyper/Express   : {len(target_partners)}")
print(f"  - Autres Carrefour (exclus)    : {len(excluded)}")

# Repartition
by_type = {"MARKET": 0, "HYPER": 0, "EXPRESS": 0}
for _, _, c in target_partners:
    by_type[c] += 1
print(f"    Market  : {by_type['MARKET']}")
print(f"    Hyper   : {by_type['HYPER']}")
print(f"    Express : {by_type['EXPRESS']}")

partner_ids = [pid for pid, _, _ in target_partners]
partner_type = {pid: c for pid, _, c in target_partners}
partner_name = {pid: n for pid, n, _ in target_partners}

# 2) Sale orders S2 2025
orders = call("sale.order", "search_read",
    [[("partner_id", "in", partner_ids),
      ("date_order", ">=", DATE_FROM),
      ("date_order", "<=", DATE_TO + " 23:59:59"),
      ("state", "in", ["sale", "done"])]],
    {"fields": ["name", "partner_id", "date_order", "amount_untaxed", "amount_total", "state"]})

print(f"\n=== Sale orders confirmes (sale + done) {DATE_FROM} -> {DATE_TO} ===")
print(f"Nb commandes : {len(orders)}")

total_ht = sum(o["amount_untaxed"] for o in orders)
total_ttc = sum(o["amount_total"] for o in orders)

# Par type
ht_by_type = {"MARKET": 0, "HYPER": 0, "EXPRESS": 0}
n_by_type = {"MARKET": 0, "HYPER": 0, "EXPRESS": 0}
for o in orders:
    pid = o["partner_id"][0]
    t = partner_type.get(pid)
    if t:
        ht_by_type[t] += o["amount_untaxed"]
        n_by_type[t] += 1

print(f"\n--- CA HTVA Carrefour Market / Hyper / Express - S2 2025 ---")
print(f"  MARKET  : {n_by_type['MARKET']:>3} cmd, {ht_by_type['MARKET']:>12,.2f} EUR HT")
print(f"  HYPER   : {n_by_type['HYPER']:>3} cmd, {ht_by_type['HYPER']:>12,.2f} EUR HT")
print(f"  EXPRESS : {n_by_type['EXPRESS']:>3} cmd, {ht_by_type['EXPRESS']:>12,.2f} EUR HT")
print(f"  -------")
print(f"  TOTAL   : {len(orders):>3} cmd, {total_ht:>12,.2f} EUR HT  ({total_ttc:,.2f} EUR TTC)")

# Detail
by_partner = {}
for o in orders:
    pid = o["partner_id"][0]
    by_partner.setdefault(pid, {"n": 0, "ht": 0, "type": partner_type.get(pid, "?")})
    by_partner[pid]["n"] += 1
    by_partner[pid]["ht"] += o["amount_untaxed"]

print(f"\n--- Detail par magasin (HT decroissant) ---")
for pid, d in sorted(by_partner.items(), key=lambda x: -x[1]["ht"]):
    print(f"  [{d['type']:7}] {partner_name[pid][:55]:55} : {d['n']:2} cmd, {d['ht']:>10,.2f} EUR HT")

print(f"\n--- Autres partners 'carrefour' exclus (verifier qu'on n'en oublie pas) ---")
for pid, n in excluded[:30]:
    print(f"  #{pid:6} {n}")
if len(excluded) > 30:
    print(f"  ... +{len(excluded)-30} autres")
