"""
11_restore_buy_route.py
Restauration route Buy sur les OP TT sans route dont le produit a un seller_ids,
et rapports pour arbitrage manuel.

Contexte (cf. LOG.md 2026-04-23 apres-midi) :
 - 298 OP TT sans route
 - 256 sur produits avec seller_ids (=> route Buy evidente)
 - 42 sans vendor (=> rapport arbitrage Nicolas)
 - 45 MO state=confirmed pre-fix 2026-03-27 / 2026-04-21 (=> rapport arbitrage)

Actions :
 1. search OP [warehouse_id=1 TT, route_id=False]
 2. resolve product -> product_tmpl_id -> seller_ids
 3. SPLIT : produits AVEC BoM active -> route Manufacture (6),
            produits SANS BoM active -> route Buy (5)
    (cf. patch 2026-04-27 : sans ce check, 249 produits I0/V0 avec BoM
     etaient bascules par erreur sur Buy au lieu de Manufacture, ce qui
     empechait le scheduler de generer les MO -> fix dans 12_fix_buy_to_manufacture.py)
 4. ecrit odoo/route_fix_20260423/42_no_vendor.md avec les 42 restants
 5. ecrit odoo/route_fix_20260423/45_confirmed_mo_pre_fix.md

LECTURE / DRY-RUN au dessus, WRITE uniquement sur step 3.
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
ROUTE_MANUFACTURE = 6  # cf. stock.route name=Manufacture
TT_WH_ID = 1

report = {"ts": datetime.now().isoformat(), "steps": []}

# ===================================================================
# STEP 1 : recuperer tous les OP TT sans route
# ===================================================================
print("=== STEP 1 : search OP TT sans route ===", flush=True)
ops_no_route = call(
    "stock.warehouse.orderpoint",
    "search_read",
    [[("warehouse_id", "=", TT_WH_ID), ("route_id", "=", False)]],
    {"fields": ["id", "name", "product_id", "route_id", "warehouse_id",
                "product_min_qty", "product_max_qty"]},
)
print(f"  {len(ops_no_route)} OP TT sans route trouves", flush=True)
report["n_ops_no_route_total"] = len(ops_no_route)

if not ops_no_route:
    print("  Rien a faire, on sort.", flush=True)
    sys.exit(0)

# ===================================================================
# STEP 2 : resolve product_id -> seller_ids + default_code
# ===================================================================
print("\n=== STEP 2 : resolve product seller_ids ===", flush=True)
product_ids = sorted({o["product_id"][0] for o in ops_no_route if o.get("product_id")})
products = call(
    "product.product",
    "read",
    [product_ids, ["id", "default_code", "name", "product_tmpl_id", "seller_ids", "type"]],
)
prod_by_id = {p["id"]: p for p in products}

# seller_ids sur product.product = hereditent du template en principe
# Double check via template pour les cas edge
tpl_ids = sorted({p["product_tmpl_id"][0] for p in products if p.get("product_tmpl_id")})
tpls = call(
    "product.template",
    "read",
    [tpl_ids, ["id", "default_code", "name", "seller_ids", "purchase_ok", "route_ids"]],
)
tpl_by_id = {t["id"]: t for t in tpls}

# Patch 2026-04-27 : identifier les templates avec BoM active pour split
# route Buy vs Manufacture. Sans ce check, 249 produits I0/V0 avec BoM
# se sont retrouves sur Buy au lieu de Manufacture -> scheduler ne generait
# pas les MO. Voir 12_fix_buy_to_manufacture.py pour le rattrapage.
tpls_with_bom = set()
if tpl_ids:
    boms = call(
        "mrp.bom",
        "search_read",
        [[("product_tmpl_id", "in", tpl_ids), ("active", "=", True)]],
        {"fields": ["id", "product_tmpl_id"]},
    )
    tpls_with_bom = {b["product_tmpl_id"][0] for b in boms}
print(f"  Templates avec BoM active : {len(tpls_with_bom)}", flush=True)

ops_with_bom = []       # -> route Manufacture (priorite : si BoM, on fabrique)
ops_with_vendor = []    # -> route Buy (pas de BoM, mais vendor -> achat)
ops_no_vendor = []      # -> arbitrage Nicolas (ni BoM, ni vendor)
for o in ops_no_route:
    if not o.get("product_id"):
        ops_no_vendor.append(o)
        continue
    pid = o["product_id"][0]
    prod = prod_by_id.get(pid)
    if not prod:
        ops_no_vendor.append(o)
        continue
    tpl = tpl_by_id.get(prod["product_tmpl_id"][0]) if prod.get("product_tmpl_id") else None
    tpl_id = tpl["id"] if tpl else None
    has_bom = tpl_id in tpls_with_bom
    sellers_prod = prod.get("seller_ids") or []
    sellers_tpl = tpl.get("seller_ids") if tpl else []
    sellers_tpl = sellers_tpl or []
    has_vendor = bool(sellers_prod or sellers_tpl)
    if has_bom:
        # Si le produit a une BoM active, on doit le FABRIQUER -> Manufacture
        # meme s'il a un vendor (le vendor pourra rester pour les composants)
        ops_with_bom.append(o)
    elif has_vendor:
        ops_with_vendor.append(o)
    else:
        ops_no_vendor.append(o)

print(f"  OP avec BoM active (-> Manufacture) : {len(ops_with_bom)}", flush=True)
print(f"  OP avec vendor sans BoM (-> Buy)    : {len(ops_with_vendor)}", flush=True)
print(f"  OP sans vendor sans BoM (arbitrage) : {len(ops_no_vendor)}", flush=True)
report["n_with_bom"] = len(ops_with_bom)
report["n_with_vendor"] = len(ops_with_vendor)
report["n_no_vendor"] = len(ops_no_vendor)

# ===================================================================
# STEP 3 : write route_id sur OP, en split Manufacture (BoM) / Buy (vendor)
# ===================================================================
print("\n=== STEP 3a : write route_id=Manufacture sur OP avec BoM active ===", flush=True)
ids_bom = [o["id"] for o in ops_with_bom]
written_bom = 0
write_errors_bom = []
for i in range(0, len(ids_bom), 100):
    chunk = ids_bom[i:i+100]
    try:
        call("stock.warehouse.orderpoint", "write",
             [chunk, {"route_id": ROUTE_MANUFACTURE}])
        written_bom += len(chunk)
        print(f"  chunk {i}-{i+len(chunk)} OK ({len(chunk)} -> Manufacture)", flush=True)
    except Exception as e:
        print(f"  chunk {i} FAIL : {str(e)[:200]}", flush=True)
        for rid in chunk:
            try:
                call("stock.warehouse.orderpoint", "write",
                     [[rid], {"route_id": ROUTE_MANUFACTURE}])
                written_bom += 1
            except Exception as e2:
                write_errors_bom.append({"id": rid, "err": str(e2)[:200]})
print(f"  Ecrits Manufacture : {written_bom} / {len(ids_bom)} ; erreurs : {len(write_errors_bom)}", flush=True)
report["steps"].append({"step": "3a_write_manufacture",
                        "written": written_bom, "errors": write_errors_bom})

print("\n=== STEP 3b : write route_id=Buy sur OP avec vendor sans BoM ===", flush=True)
ids_to_write = [o["id"] for o in ops_with_vendor]
written = 0
write_errors = []
for i in range(0, len(ids_to_write), 100):
    chunk = ids_to_write[i:i+100]
    try:
        call("stock.warehouse.orderpoint", "write", [chunk, {"route_id": ROUTE_BUY}])
        written += len(chunk)
        print(f"  chunk {i}-{i+len(chunk)} OK", flush=True)
    except Exception as e:
        print(f"  chunk {i} FAIL : {str(e)[:200]}", flush=True)
        for rid in chunk:
            try:
                call("stock.warehouse.orderpoint", "write", [[rid], {"route_id": ROUTE_BUY}])
                written += 1
            except Exception as e2:
                write_errors.append({"id": rid, "err": str(e2)[:200]})
print(f"  Ecrits Buy : {written} / {len(ids_to_write)} ; erreurs : {len(write_errors)}", flush=True)
report["steps"].append({"step": "3b_write_buy", "written": written, "errors": write_errors})

# Verif globale
all_ids_written = ids_bom + ids_to_write
remaining = call(
    "stock.warehouse.orderpoint",
    "search_count",
    [[("warehouse_id", "=", TT_WH_ID), ("route_id", "=", False),
      ("id", "in", all_ids_written)]],
)
print(f"  Verif : OP cibles encore sans route : {remaining} (attendu 0)", flush=True)
report["steps"].append({"step": "3_verify", "remaining_no_route": remaining})

# ===================================================================
# STEP 4 : rapport markdown des 42 sans vendor
# ===================================================================
print("\n=== STEP 4 : rapport 42 OP sans vendor ===", flush=True)
lines = [
    "# OP TT sans route ET sans vendor - 2026-04-23",
    "",
    f"Genere : {datetime.now().isoformat()}",
    "",
    f"Ces OP sont TT/Stock, `route_id=False`, et le produit n'a aucun `product.supplierinfo`.",
    f"Le scheduler Odoo ne peut rien faire pour eux (ni Buy, ni MO).",
    "",
    "## Arbitrage Nicolas",
    "",
    "- (A) ajouter un seller_ids au produit -> puis appliquer route Buy",
    "- (B) supprimer l'OP si produit non commande chez fournisseur",
    "- (C) laisser `route_id=False` si production interne future (ex: coffrets faits maison)",
    "",
    "| OP | Produit | Code | Tmpl | Type | min / max | Purchase OK |",
    "|---|---|---|---|---|---|---|",
]
rows_json = []
for o in ops_no_vendor:
    if not o.get("product_id"):
        lines.append(f"| {o['name']} (id={o['id']}) | _no product_ | - | - | - | {o.get('product_min_qty')} / {o.get('product_max_qty')} | - |")
        rows_json.append({"op_id": o["id"], "op_name": o["name"], "product": None})
        continue
    pid = o["product_id"][0]
    prod = prod_by_id.get(pid, {})
    tpl = tpl_by_id.get(prod.get("product_tmpl_id", [None])[0] if prod.get("product_tmpl_id") else None, {})
    tpl_id = tpl.get("id", "-")
    code = prod.get("default_code") or "-"
    pname = (prod.get("name") or "")[:80]
    ptype = prod.get("type") or "-"
    pur = tpl.get("purchase_ok") if tpl else "?"
    lines.append(
        f"| {o['name']} (id={o['id']}) | {pname} | {code} | {tpl_id} | {ptype} | {o.get('product_min_qty')} / {o.get('product_max_qty')} | {pur} |"
    )
    rows_json.append({
        "op_id": o["id"], "op_name": o["name"],
        "product_id": pid, "default_code": code, "product_name": pname,
        "tmpl_id": tpl_id, "type": ptype, "purchase_ok": pur,
        "min": o.get("product_min_qty"), "max": o.get("product_max_qty"),
    })
lines.append("")
lines.append(f"**Total** : {len(ops_no_vendor)} OP sans vendor")
with open(os.path.join(OUT_DIR, "42_no_vendor.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"  ecrit : {OUT_DIR}/42_no_vendor.md ({len(ops_no_vendor)} lignes)", flush=True)
report["no_vendor_rows"] = rows_json

# ===================================================================
# STEP 5 : rapport markdown des MO encore confirmed
# ===================================================================
print("\n=== STEP 5 : rapport MO state=confirmed ===", flush=True)
# Tous les MO confirmed (tout age) en base
mo_confirmed = call(
    "mrp.production",
    "search_read",
    [[("state", "=", "confirmed")]],
    {
        "fields": [
            "id", "name", "product_id", "product_qty", "state",
            "date_start", "create_date", "origin",
            "orderpoint_id", "procurement_group_id", "create_uid",
        ],
        "order": "create_date asc",
    },
)
print(f"  MO confirmed total : {len(mo_confirmed)}", flush=True)

lines2 = [
    "# MO state=confirmed pre-fix - 2026-04-23",
    "",
    f"Genere : {datetime.now().isoformat()}",
    "",
    f"Total : **{len(mo_confirmed)}** MO encore `state=confirmed` apres le cleanup du matin (`07_execute.py`).",
    "Ce sont des MO creees AVANT le fix de ce matin (residus du flood ou MO manuelles).",
    "",
    "## Arbitrage Nicolas",
    "",
    "- (A) cancel + unlink si aucune raw move done (standard route fix)",
    "- (B) laisser si MO legit en cours de prod (p.ex. C0200 coffret Matcha)",
    "- (C) convertir en PO si le produit doit etre achete chez fournisseur",
    "",
    "| MO | Produit | Qty | Create | Origin | OP | User |",
    "|---|---|---|---|---|---|---|",
]
rows_mo = []
for mo in mo_confirmed:
    pname = mo["product_id"][1] if mo.get("product_id") else "?"
    origin = mo.get("origin") or "-"
    op = mo["orderpoint_id"][1] if mo.get("orderpoint_id") else "-"
    u = mo["create_uid"][1] if mo.get("create_uid") else "-"
    lines2.append(
        f"| {mo['name']} (id={mo['id']}) | {pname[:60]} | {mo.get('product_qty')} | {str(mo.get('create_date'))[:16]} | {origin} | {op} | {u} |"
    )
    rows_mo.append({
        "mo_id": mo["id"], "mo_name": mo["name"],
        "product": pname, "qty": mo.get("product_qty"),
        "create_date": str(mo.get("create_date")),
        "origin": origin, "op": op, "user": u,
    })
lines2.append("")
lines2.append(f"**Total** : {len(mo_confirmed)} MO confirmed")
with open(os.path.join(OUT_DIR, "45_confirmed_mo_pre_fix.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines2))
print(f"  ecrit : {OUT_DIR}/45_confirmed_mo_pre_fix.md", flush=True)
report["mo_confirmed_rows"] = rows_mo
report["n_mo_confirmed"] = len(mo_confirmed)

# ===================================================================
# FINAL REPORT
# ===================================================================
with open(os.path.join(OUT_DIR, "11_restore_report.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, default=str, ensure_ascii=False)
print("\nrapport : odoo/route_fix_20260423/11_restore_report.json", flush=True)
print(f"\n=== RESUME ===", flush=True)
print(f"  OP TT sans route total    : {len(ops_no_route)}", flush=True)
print(f"  OP restauree route=Buy    : {written}", flush=True)
print(f"  OP sans vendor (arbitrage): {len(ops_no_vendor)} -> 42_no_vendor.md", flush=True)
print(f"  MO confirmed pre-fix      : {len(mo_confirmed)} -> 45_confirmed_mo_pre_fix.md", flush=True)
print("DONE.", flush=True)
