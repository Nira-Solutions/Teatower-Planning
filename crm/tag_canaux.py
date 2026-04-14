"""Tagging automatique des canaux commerciaux sur res.partner — Teatower.
Priorité Horeca > GMS > Amazon > Shopify > B2B Direct."""
import xmlrpc.client, re, datetime, sys, io, os

# Ensure UTF-8 stdout on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = "Teatower123"

TAG = {"GMS": 88, "Horeca": 84, "B2B": 85, "Shopify": 86, "Amazon": 87}

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def X(model, method, *args, **kw):
    return models.execute_kw(DB, uid, PWD, model, method, list(args), kw)
def READ(model, rec_ids, fields):
    return models.execute_kw(DB, uid, PWD, model, "read", [rec_ids], {"fields":fields})
def SEARCH(model, domain, **kw):
    return models.execute_kw(DB, uid, PWD, model, "search", [domain], kw)
def SEARCH_COUNT(model, domain):
    return models.execute_kw(DB, uid, PWD, model, "search_count", [domain])
def WRITE(model, rec_ids, vals):
    return models.execute_kw(DB, uid, PWD, model, "write", [rec_ids, vals])

print(f"[auth] uid={uid}")

# --- Etat initial ---
for k,tid in TAG.items():
    n = X("res.partner", "search_count", [("category_id","in",[tid])])
    print(f"[init] Canal {k}: {n} partners")

ALL_CANAL_IDS = list(TAG.values())

# Horeca keywords
HORECA_KW = [
    "hotel","hôtel","radisson","ibis","novotel","mercure","marriott","van der valk",
    "intercontinental","best western","b&b","gîte","gite","resort","spa ",
    "chambre d'hôte","restaurant","brasserie","bistro","bistrot","café","cafe",
    "taverne","auberge"," pub "," pub","lounge","rooftop","tea room","salon de thé",
    "crêperie","creperie","pizzeria"," bar "," bar ","domaine de ","chateau ","château "
]
# Weak kw (only if short and no GMS)
HORECA_STRONG_RE = re.compile("|".join([re.escape(k) for k in HORECA_KW]), re.IGNORECASE)

def has_canal(cats):
    return any(c in ALL_CANAL_IDS for c in (cats or []))

# --- Fetch all customer partners (customer_rank>0, active) ---
print("[fetch] customers…")
ids = X("res.partner","search",[("customer_rank",">",0),("active","=",True)], limit=20000)
print(f"[fetch] {len(ids)} customer partner ids")

fields = ["id","name","is_company","category_id","country_id","email","industry_id",
          "supplier_rank","customer_rank","sale_order_count"]
partners = []
BATCH = 500
for i in range(0, len(ids), BATCH):
    partners += READ("res.partner", ids[i:i+BATCH], fields)
print(f"[fetch] read {len(partners)} records")

log_lines = []
review_lines = []

def tag_partner(pid, tag_id, reason):
    X("res.partner","write",[pid], {"category_id":[(4, tag_id)]})
    log_lines.append(f"  - pid={pid} tag={tag_id} {reason}")

counters = {"Horeca":0, "Shopify":0, "Amazon":0, "B2B":0}
samples = {"Horeca":[], "Shopify":[], "Amazon":[], "B2B":[]}

# --- Étape 1 : Horeca ---
print("\n=== ETAPE 1 : Horeca ===")
for p in partners:
    if has_canal(p["category_id"]): continue
    if p["supplier_rank"] and not p["customer_rank"]: continue
    name = (p["name"] or "")
    industry_name = ""
    if p.get("industry_id"):
        industry_name = p["industry_id"][1] if isinstance(p["industry_id"], list) else ""
    hay = name + " " + (industry_name or "")
    if HORECA_STRONG_RE.search(hay):
        tag_partner(p["id"], TAG["Horeca"], f"horeca match name='{name}'")
        counters["Horeca"] += 1
        if len(samples["Horeca"]) < 10: samples["Horeca"].append(name)
        p["category_id"] = (p["category_id"] or []) + [TAG["Horeca"]]
print(f"[Horeca] taggés: {counters['Horeca']}")

# --- Étape 3 : Amazon (avant Shopify, priorité plus haute) ---
print("\n=== ETAPE 3 : Amazon ===")
# chercher sale orders avec client_order_ref style Amazon (xxx-xxxxxxx-xxxxxxx)
amz_order_ids = X("sale.order","search",
    [("client_order_ref","=like","___-_______-_______")], limit=5000)
amz_partner_ids = set()
if amz_order_ids:
    for i in range(0, len(amz_order_ids), 500):
        rows = READ("sale.order", amz_order_ids[i:i+500], ["partner_id"])
        for r in rows:
            if r["partner_id"]:
                amz_partner_ids.add(r["partner_id"][0])
print(f"[Amazon] {len(amz_partner_ids)} partners détectés via client_order_ref")

pmap = {p["id"]: p for p in partners}
for pid in amz_partner_ids:
    p = pmap.get(pid)
    if not p: continue
    if has_canal(p["category_id"]): continue
    name = p["name"] or ""
    if "amazon" in name.lower() or "fba" in name.lower():
        tag_partner(pid, TAG["Amazon"], "name contains amazon/fba")
    else:
        tag_partner(pid, TAG["Amazon"], "client_order_ref amazon pattern")
    counters["Amazon"] += 1
    if len(samples["Amazon"]) < 10: samples["Amazon"].append(name)
    p["category_id"] = (p["category_id"] or []) + [TAG["Amazon"]]

# Aussi ceux avec "amazon" dans le nom
for p in partners:
    if has_canal(p["category_id"]): continue
    if "amazon" in (p["name"] or "").lower() or re.search(r"\bfba\b", (p["name"] or "").lower()):
        tag_partner(p["id"], TAG["Amazon"], "name contains amazon")
        counters["Amazon"] += 1
        if len(samples["Amazon"]) < 10: samples["Amazon"].append(p["name"])
        p["category_id"] = (p["category_id"] or []) + [TAG["Amazon"]]
print(f"[Amazon] taggés: {counters['Amazon']}")

# --- Étape 2 : Shopify ---
print("\n=== ETAPE 2 : Shopify ===")
# Shopify = particuliers (is_company=False) avec au moins 1 commande
# heuristique : client_order_ref commence par "#"
shop_order_ids = X("sale.order","search",
    [("client_order_ref","=like","#%")], limit=20000)
shop_partner_ids = set()
if shop_order_ids:
    for i in range(0, len(shop_order_ids), 500):
        rows = READ("sale.order", shop_order_ids[i:i+500], ["partner_id"])
        for r in rows:
            if r["partner_id"]:
                shop_partner_ids.add(r["partner_id"][0])
print(f"[Shopify] {len(shop_partner_ids)} partners via client_order_ref '#...'")

for pid in shop_partner_ids:
    p = pmap.get(pid)
    if not p: continue
    if has_canal(p["category_id"]): continue
    # exclude pure companies — sauf si manifestement e-commerçant (skip exclusion simple)
    tag_partner(pid, TAG["Shopify"], "order_ref #shopify")
    counters["Shopify"] += 1
    if len(samples["Shopify"]) < 10: samples["Shopify"].append(p["name"])
    p["category_id"] = (p["category_id"] or []) + [TAG["Shopify"]]

# Fallback particuliers avec commandes sans autre canal
for p in partners:
    if has_canal(p["category_id"]): continue
    if p["is_company"]: continue
    if (p.get("sale_order_count") or 0) < 1: continue
    tag_partner(p["id"], TAG["Shopify"], "particulier avec commande (fallback DTC)")
    counters["Shopify"] += 1
    if len(samples["Shopify"]) < 10: samples["Shopify"].append(p["name"])
    p["category_id"] = (p["category_id"] or []) + [TAG["Shopify"]]
print(f"[Shopify] taggés: {counters['Shopify']}")

# --- Étape 4 : B2B Direct (fallback entreprises) ---
print("\n=== ETAPE 4 : B2B Direct ===")
for p in partners:
    if has_canal(p["category_id"]): continue
    if not p["is_company"]: continue
    if (p["customer_rank"] or 0) <= 0: continue
    if (p.get("sale_order_count") or 0) < 1: continue
    tag_partner(p["id"], TAG["B2B"], "entreprise avec commande (fallback)")
    counters["B2B"] += 1
    if len(samples["B2B"]) < 10: samples["B2B"].append(p["name"])
print(f"[B2B] taggés: {counters['B2B']}")

# --- Rapport final ---
print("\n=== RAPPORT FINAL ===")
active_customers = X("res.partner","search_count",[("customer_rank",">",0),("active","=",True)])
print(f"Clients actifs totaux: {active_customers}")
report = []
report.append("| Canal | Taggués ce run | Total canal | % couverture |")
report.append("|---|---|---|---|")
for k, tid in TAG.items():
    total = X("res.partner","search_count",[("category_id","in",[tid])])
    added = counters.get(k, 0) if k != "GMS" else 0
    pct = 100*total/active_customers if active_customers else 0
    report.append(f"| {k} | {added} | {total} | {pct:.1f}% |")
for line in report: print(line)

# Somme couverture
with_any_canal = X("res.partner","search_count",
    [("customer_rank",">",0),("active","=",True),("category_id","in",ALL_CANAL_IDS)])
print(f"\nCouverture globale: {with_any_canal}/{active_customers} = {100*with_any_canal/active_customers:.1f}%")

# Samples
print("\n=== SAMPLES ===")
for k, lst in samples.items():
    print(f"[{k}] " + " | ".join([s or "" for s in lst[:10]]))

# --- LOG ---
today = datetime.date.today().isoformat()
log_path = "C:/Users/FlowUP/Downloads/Claude/Claude/Teatower/crm/LOG.md"
with open(log_path, "a", encoding="utf-8") as f:
    f.write(f"\n## {today} — Tagging canaux commerciaux\n\n")
    for k in ("Horeca","Amazon","Shopify","B2B"):
        f.write(f"- Canal {k} : {counters[k]} partners tagués\n")
    f.write(f"- Couverture globale : {with_any_canal}/{active_customers} ({100*with_any_canal/active_customers:.1f}%)\n")
    f.write("\n### Détails\n")
    f.write("\n".join(log_lines[:200]))
    f.write("\n")
print(f"\n[log] {log_path}")
