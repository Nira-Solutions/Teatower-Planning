"""
Sanity check quotidien Odoo : detecter les basculements route anormaux.

A lancer en cron (exemple : 08:00 chaque matin) ou via GitHub Actions.
Retourne exit code != 0 si anomalie detectee.

Alerte si :
  1. Route Buy (5) desactivee
  2. Warehouse TT (1) contient la route Manufacture (6) dans ses route_ids
  3. > 1 template.route_ids contient Manufacture (seul C0200 id=10485 doit l'avoir)
  4. Orderpoints avec route_id=Manufacture sur un produit != C0200
  5. MO cree au nom d'un produit sans BoM active dans les 24 dernieres heures
"""
import xmlrpc.client, json, sys, io
from datetime import datetime, timedelta
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = "Teatower123"
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

ROUTE_BUY = 5
ROUTE_MFG = 6
LEGIT_MFG_TPL = [10485]  # C0200
TT_WH_ID = 1

alerts = []

# 1. Route Buy active ?
buy = call("stock.route", "read", [[ROUTE_BUY], ["active", "rule_ids"]], {"context": {"active_test": False}})[0]
if not buy["active"]:
    alerts.append("[CRITIQUE] Route Buy (id=5) DESACTIVEE. Les PO auto ne marchent plus.")
# Rules buy
rules_inactive = call("stock.rule", "search", [[("route_id", "=", ROUTE_BUY), ("active", "=", False)]],
                      {"context": {"active_test": False}})
if rules_inactive:
    alerts.append(f"[CRITIQUE] {len(rules_inactive)} rules Buy inactives : {rules_inactive}")

# 2. Warehouse TT : route Manufacture presente ?
wh = call("stock.warehouse", "read", [[TT_WH_ID], ["route_ids", "code"]])[0]
if ROUTE_MFG in (wh["route_ids"] or []):
    alerts.append(f"[CRITIQUE] WH {wh['code']} contient route Manufacture dans route_ids : {wh['route_ids']}")

# 3. Templates avec route Manufacture hors whitelist
tpl_mfg = call("product.template", "search", [[("route_ids", "in", [ROUTE_MFG])]])
illegit = [t for t in tpl_mfg if t not in LEGIT_MFG_TPL]
if illegit:
    tpls = call("product.template", "read", [illegit, ["id", "default_code", "name"]])
    alerts.append(f"[WARN] {len(illegit)} templates ont route Manufacture sans etre legit : {tpls[:5]}")

# 4. Orderpoints route_id=Manufacture hors produits C0200
legit_products = call("product.product", "search", [[("product_tmpl_id", "in", LEGIT_MFG_TPL)]])
ops_mfg = call("stock.warehouse.orderpoint", "search_read",
               [[("route_id", "=", ROUTE_MFG)]],
               {"fields": ["id", "name", "product_id"]})
illegit_ops = [o for o in ops_mfg if o["product_id"] and o["product_id"][0] not in legit_products]
if illegit_ops:
    alerts.append(f"[WARN] {len(illegit_ops)} orderpoints route=Manufacture sur produits non-legit : {illegit_ops[:5]}")

# 5. MO recents 24h sur produits sans BoM active
since = (datetime.utcnow() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
mo_ids = call("mrp.production", "search",
              [[("create_date", ">=", since), ("state", "in", ["draft", "confirmed", "progress"])]])
if mo_ids:
    mos = call("mrp.production", "read", [mo_ids, ["id", "name", "product_id"]])
    # Check produits sans BoM active
    prod_ids = list({mo["product_id"][0] for mo in mos if mo.get("product_id")})
    bom_active = set()
    if prod_ids:
        boms = call("mrp.bom", "search_read",
                    [[("product_tmpl_id.product_variant_ids", "in", prod_ids), ("active", "=", True)]],
                    {"fields": ["id", "product_tmpl_id"]})
        # resolve tpl->products
        tpl_ids = list({b["product_tmpl_id"][0] for b in boms})
        if tpl_ids:
            prods_ok = call("product.product", "search", [[("product_tmpl_id", "in", tpl_ids)]])
            bom_active = set(prods_ok)
    mo_no_bom = [mo for mo in mos if mo["product_id"] and mo["product_id"][0] not in bom_active]
    if mo_no_bom:
        alerts.append(f"[CRITIQUE] {len(mo_no_bom)} MO recents sur produits SANS BoM active : {[mo['name'] for mo in mo_no_bom[:10]]}")

# Output
result = {
    "ts": datetime.now().isoformat(),
    "alerts": alerts,
    "n_tpl_mfg": len(tpl_mfg),
    "n_ops_mfg": len(ops_mfg),
    "n_recent_mo_24h": len(mo_ids),
    "wh_tt_routes": wh["route_ids"],
    "route_buy_active": buy["active"],
}
print(json.dumps(result, indent=2, default=str, ensure_ascii=False))

if alerts:
    print("\n=== ALERTES ===", file=sys.stderr)
    for a in alerts:
        print(f"  {a}", file=sys.stderr)
    sys.exit(1)
else:
    print("\n=== OK : aucune anomalie detectee ===")
    sys.exit(0)
