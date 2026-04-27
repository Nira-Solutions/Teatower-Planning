"""
audit_i0v0_buy.py
Audit : OP TT/Stock sur produits I0/V0 ayant route Buy alors qu'une BoM active existe.
Lecture seule.
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
ROUTE_BUY = 5
ROUTE_MFG = 6
TT_WH_ID = 1

# Resolve route ids dynamiquement (pour etre sur)
routes = call("stock.route", "search_read",
              [[("name", "in", ["Buy", "Manufacture", "Acheter", "Fabriquer"])]],
              {"fields": ["id", "name", "active"]})
print("Routes trouvees :", routes, flush=True)
route_buy_id = next((r["id"] for r in routes if r["name"] in ("Buy", "Acheter")), ROUTE_BUY)
route_mfg_id = next((r["id"] for r in routes if r["name"] in ("Manufacture", "Fabriquer")), ROUTE_MFG)
print(f"  Buy id={route_buy_id} / Manufacture id={route_mfg_id}", flush=True)

# 1) Tous les OP TT avec route Buy
ops = call(
    "stock.warehouse.orderpoint",
    "search_read",
    [[("warehouse_id", "=", TT_WH_ID), ("route_id", "=", route_buy_id)]],
    {"fields": ["id", "name", "product_id", "route_id", "product_min_qty",
                "product_max_qty", "write_date"]},
)
print(f"\nOP TT route=Buy total : {len(ops)}", flush=True)

# 2) Filtre I0 / V0 sur default_code
prod_ids = sorted({o["product_id"][0] for o in ops if o.get("product_id")})
prods = call("product.product", "read",
             [prod_ids, ["id", "default_code", "name", "product_tmpl_id", "type"]])
prod_by_id = {p["id"]: p for p in prods}

def is_i0_v0(code):
    if not code:
        return False
    c = code.upper()
    # patterns vus : "I0832", "05I0832", "V0625", "05V0625", "06V0..."
    return ("I0" in c[:6] and any(ch in c for ch in "I")) or ("V0" in c[:6])

ops_i0v0 = []
for o in ops:
    pid = o["product_id"][0] if o.get("product_id") else None
    if not pid:
        continue
    code = (prod_by_id.get(pid, {}).get("default_code") or "").upper()
    # Detect strict : "I0xxx" ou "V0xxx" presents quelque part dans le code
    has_i0 = "I0" in code
    has_v0 = "V0" in code
    if has_i0 or has_v0:
        ops_i0v0.append((o, code, "I0" if has_i0 else "V0"))

print(f"OP I0/V0 sur route Buy : {len(ops_i0v0)}", flush=True)

# 3) Pour chaque produit concerne, verifier BoM active
tpl_ids = sorted({prod_by_id[o["product_id"][0]]["product_tmpl_id"][0]
                  for o, _, _ in ops_i0v0})
boms = call("mrp.bom", "search_read",
            [[("product_tmpl_id", "in", tpl_ids), ("active", "=", True)]],
            {"fields": ["id", "product_tmpl_id", "product_id", "type", "active"]})
bom_by_tpl = {}
for b in boms:
    tid = b["product_tmpl_id"][0]
    bom_by_tpl.setdefault(tid, []).append(b)
print(f"BoM actives trouvees : {len(boms)} sur {len(tpl_ids)} templates", flush=True)

# 4) Croise : produit I0/V0 + route Buy + BoM active = bug
rows = []
for o, code, fam in ops_i0v0:
    pid = o["product_id"][0]
    p = prod_by_id[pid]
    tid = p["product_tmpl_id"][0]
    boms_tpl = bom_by_tpl.get(tid, [])
    rows.append({
        "op_id": o["id"],
        "op_name": o["name"],
        "code": p.get("default_code"),
        "name": (p.get("name") or "")[:80],
        "tmpl_id": tid,
        "fam": fam,
        "min": o.get("product_min_qty"),
        "max": o.get("product_max_qty"),
        "route": "Buy",
        "write_date": o.get("write_date"),
        "n_bom_active": len(boms_tpl),
        "bom_ids": [b["id"] for b in boms_tpl],
    })

# 5) Focus I0832 (cas Nicolas)
print("\n--- Focus I0832 ---", flush=True)
i0832_prod = call("product.product", "search_read",
                  [[("default_code", "ilike", "I0832")]],
                  {"fields": ["id", "default_code", "name", "product_tmpl_id"]})
print(f"  produits matchant I0832 : {len(i0832_prod)}", flush=True)
for p in i0832_prod:
    print(f"  - {p['default_code']} / id={p['id']} / tmpl={p['product_tmpl_id']}", flush=True)
    tid = p["product_tmpl_id"][0]
    bs = call("mrp.bom", "search_read",
              [[("product_tmpl_id", "=", tid)]],
              {"fields": ["id", "active", "type", "product_qty"]})
    print(f"    BoM (toutes) : {bs}", flush=True)
    # OP actuel
    op_now = call("stock.warehouse.orderpoint", "search_read",
                  [[("product_id", "=", p["id"]), ("warehouse_id", "=", TT_WH_ID)]],
                  {"fields": ["id", "name", "route_id", "product_min_qty",
                              "product_max_qty", "write_date"]})
    print(f"    OP TT actuel : {op_now}", flush=True)

# 6) Stats par famille
i0_count = sum(1 for r in rows if r["fam"] == "I0")
v0_count = sum(1 for r in rows if r["fam"] == "V0")
i0_with_bom = sum(1 for r in rows if r["fam"] == "I0" and r["n_bom_active"] > 0)
v0_with_bom = sum(1 for r in rows if r["fam"] == "V0" and r["n_bom_active"] > 0)
print(f"\n=== STATS ===", flush=True)
print(f"  I0 sur Buy           : {i0_count}", flush=True)
print(f"  I0 sur Buy + BoM act : {i0_with_bom}", flush=True)
print(f"  V0 sur Buy           : {v0_count}", flush=True)
print(f"  V0 sur Buy + BoM act : {v0_with_bom}", flush=True)

# Save JSON
out = {
    "ts": datetime.now().isoformat(),
    "n_ops_buy_total": len(ops),
    "n_ops_i0v0_buy": len(ops_i0v0),
    "i0_total": i0_count,
    "v0_total": v0_count,
    "i0_with_bom": i0_with_bom,
    "v0_with_bom": v0_with_bom,
    "rows": rows,
}
with open(os.path.join(OUT_DIR, "audit_i0v0_buy.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, default=str, ensure_ascii=False)
print(f"\necrit : {OUT_DIR}/audit_i0v0_buy.json", flush=True)
