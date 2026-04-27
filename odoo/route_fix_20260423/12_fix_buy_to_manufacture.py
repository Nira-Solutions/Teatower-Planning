"""
12_fix_buy_to_manufacture.py
Fix des 249 OP I0/V0 sur TT/Stock dont le produit a une BoM active mais
qui ont ete bascules par erreur sur route=Buy via 11_restore_buy_route.py.

Cause : 11_restore_buy_route.py a verifie seller_ids mais pas la presence
de mrp.bom active. Resultat : produits avec BoM ET seller_ids ont ete
mis sur Buy, ce qui empeche le scheduler de generer les MO.

Action :
 1. lire i0v0_buy_with_bom_TO_FIX.json (249 OP)
 2. resolve route Manufacture id via stock.route
 3. write route_id=<Manufacture> sur les 249 OP par chunks de 100
 4. sanity post-fix : recompter combien restent sur Buy avec BoM active
"""
import xmlrpc.client, json, sys, io, os
from datetime import datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = "Teatower123"
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

OUT_DIR = "C:/Users/FlowUP/OneDrive/Teatower/odoo/route_fix_20260423"
TT_WH_ID = 1

report = {"ts": datetime.now().isoformat(), "steps": []}

# ===================================================================
# STEP 1 : lire le JSON
# ===================================================================
print("=== STEP 1 : lire i0v0_buy_with_bom_TO_FIX.json ===", flush=True)
with open(os.path.join(OUT_DIR, "i0v0_buy_with_bom_TO_FIX.json"), "r", encoding="utf-8") as f:
    data = json.load(f)
op_ids = [r["op_id"] for r in data["rows"]]
print(f"  {len(op_ids)} OP a fixer", flush=True)
report["n_to_fix"] = len(op_ids)

# ===================================================================
# STEP 2 : resolve route Manufacture
# ===================================================================
print("\n=== STEP 2 : resolve route Manufacture ===", flush=True)
routes = call("stock.route", "search_read",
              [[("name", "=", "Manufacture")]],
              {"fields": ["id", "name"]})
print(f"  routes trouvees : {routes}", flush=True)
if not routes:
    # Variante FR
    routes = call("stock.route", "search_read",
                  [[("name", "ilike", "Manufact")]],
                  {"fields": ["id", "name"]})
    print(f"  fallback ilike Manufact : {routes}", flush=True)
if not routes:
    print("  ERREUR : aucune route Manufacture trouvee", flush=True)
    sys.exit(1)
route_manufacture = routes[0]["id"]
print(f"  -> route Manufacture id = {route_manufacture}", flush=True)
report["route_manufacture_id"] = route_manufacture

# ===================================================================
# STEP 3 : write route_id = Manufacture par chunks de 100
# ===================================================================
print("\n=== STEP 3 : write route_id=Manufacture par chunks de 100 ===", flush=True)
written = 0
write_errors = []
for i in range(0, len(op_ids), 100):
    chunk = op_ids[i:i+100]
    try:
        call("stock.warehouse.orderpoint", "write",
             [chunk, {"route_id": route_manufacture}])
        written += len(chunk)
        print(f"  chunk {i}-{i+len(chunk)} OK ({len(chunk)} OP -> Manufacture)", flush=True)
    except Exception as e:
        print(f"  chunk {i} FAIL : {str(e)[:200]}", flush=True)
        # retry record-by-record
        for rid in chunk:
            try:
                call("stock.warehouse.orderpoint", "write",
                     [[rid], {"route_id": route_manufacture}])
                written += 1
            except Exception as e2:
                write_errors.append({"id": rid, "err": str(e2)[:200]})
print(f"  Ecrits : {written} / {len(op_ids)} ; erreurs : {len(write_errors)}", flush=True)
report["steps"].append({"step": "3_write_manufacture",
                        "written": written, "errors": write_errors})

# ===================================================================
# STEP 4 : sanity post-fix
# ===================================================================
print("\n=== STEP 4 : sanity post-fix ===", flush=True)

# Verif 1 : les OP fixes ont bien route=Manufacture
ops_check = call("stock.warehouse.orderpoint", "read",
                 [op_ids, ["id", "name", "route_id"]])
ok = sum(1 for o in ops_check if o.get("route_id") and o["route_id"][0] == route_manufacture)
ko = [o for o in ops_check if not (o.get("route_id") and o["route_id"][0] == route_manufacture)]
print(f"  OP avec route=Manufacture : {ok} / {len(ops_check)}", flush=True)
if ko:
    print(f"  OP NON corriges : {len(ko)}", flush=True)
    for o in ko[:10]:
        print(f"    - {o['name']} (id={o['id']}) route={o.get('route_id')}", flush=True)
report["steps"].append({"step": "4_verify_manufacture",
                        "ok": ok, "ko_count": len(ko),
                        "ko_sample": ko[:20]})

# Verif 2 : query d'audit complete
# OP TT/Stock + produit I0/V0 + BoM active + route=Buy => doit retourner 0
print("\n  -- query d'audit complete (doit retourner 0) --", flush=True)
ROUTE_BUY = 5

# 1) Tous les OP TT/Stock
ops_tt = call("stock.warehouse.orderpoint", "search_read",
              [[("warehouse_id", "=", TT_WH_ID), ("route_id", "=", ROUTE_BUY)]],
              {"fields": ["id", "name", "product_id", "location_id"]})
# Filtre TT/Stock (location_id name = "TT/Stock")
ops_tt_stock = [o for o in ops_tt
                if o.get("location_id") and "Stock" in (o["location_id"][1] or "")]
print(f"  OP route=Buy sur warehouse TT : {len(ops_tt)}", flush=True)
print(f"  OP route=Buy sur TT/Stock     : {len(ops_tt_stock)}", flush=True)

# 2) Garder seulement produits I0/V0
prod_ids = sorted({o["product_id"][0] for o in ops_tt_stock if o.get("product_id")})
prods = call("product.product", "read",
             [prod_ids, ["id", "default_code", "product_tmpl_id"]]) if prod_ids else []
prod_by_id = {p["id"]: p for p in prods}

def is_i0v0(code):
    if not code:
        return False
    # I0xxx ou V0xxx (peut-etre 05V0 etc)
    import re
    return bool(re.search(r"(I0|V0)\d", code))

ops_i0v0 = []
for o in ops_tt_stock:
    if not o.get("product_id"):
        continue
    p = prod_by_id.get(o["product_id"][0])
    if not p:
        continue
    if is_i0v0(p.get("default_code")):
        ops_i0v0.append((o, p))
print(f"  OP TT/Stock + Buy + I0/V0     : {len(ops_i0v0)}", flush=True)

# 3) Filtrer ceux avec BoM active
tpl_ids = sorted({p["product_tmpl_id"][0] for _, p in ops_i0v0 if p.get("product_tmpl_id")})
boms = call("mrp.bom", "search_read",
            [[("product_tmpl_id", "in", tpl_ids), ("active", "=", True)]],
            {"fields": ["id", "product_tmpl_id"]}) if tpl_ids else []
tpls_with_bom = {b["product_tmpl_id"][0] for b in boms}
ops_with_bom = [(o, p) for o, p in ops_i0v0
                if p.get("product_tmpl_id") and p["product_tmpl_id"][0] in tpls_with_bom]
print(f"  OP TT/Stock + Buy + I0/V0 + BoM active : {len(ops_with_bom)} (attendu 0)", flush=True)
report["steps"].append({"step": "4_audit_query",
                        "remaining": len(ops_with_bom),
                        "sample": [{"op_id": o["id"], "op_name": o["name"],
                                    "code": p.get("default_code")}
                                   for o, p in ops_with_bom[:20]]})

# ===================================================================
# FINAL REPORT
# ===================================================================
report["sanity_ok"] = (len(ops_with_bom) == 0 and len(ko) == 0)
with open(os.path.join(OUT_DIR, "12_fix_report.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, default=str, ensure_ascii=False)
print("\nrapport : odoo/route_fix_20260423/12_fix_report.json", flush=True)
print(f"\n=== RESUME ===", flush=True)
print(f"  OP a fixer       : {len(op_ids)}", flush=True)
print(f"  Ecrits OK        : {written}", flush=True)
print(f"  Erreurs ecriture : {len(write_errors)}", flush=True)
print(f"  Sanity audit     : {len(ops_with_bom)} restants (attendu 0)", flush=True)
print(f"  Verdict          : {'OK' if report['sanity_ok'] else 'ALERTE'}", flush=True)
print("DONE.", flush=True)
