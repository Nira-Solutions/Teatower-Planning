"""Détails complets Delhaize Bertrix Affilié 41092 #123303 + statut SO S05489."""
import xmlrpc.client
import json

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PASSWORD = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

PID = 123303

# 1. Détails complets partner
p = models.execute_kw(
    DB, uid, PASSWORD,
    "res.partner", "read",
    [[PID]],
    {"fields": [
        "id", "name", "parent_id", "street", "street2", "city", "zip", "country_id",
        "phone", "mobile", "email", "active", "sale_warn", "sale_warn_msg",
        "comment", "category_id", "property_payment_term_id", "property_product_pricelist",
        "user_id", "vat", "ref",
    ]}
)[0]

print("=" * 80)
print(f"PARTNER #{p['id']} — {p['name']}")
print("=" * 80)
for k, v in p.items():
    if v in (False, None, "", []):
        continue
    if isinstance(v, list) and len(v) == 2 and isinstance(v[1], str):
        v = f"[{v[0]}] {v[1]}"
    if k == "comment":
        print(f"\n--- comment ---\n{v}\n---")
    else:
        print(f"  {k:35s} : {v}")

# 2. Dernières SO Bertrix (toutes états)
print("\n" + "=" * 80)
print("DERNIÈRES SO Delhaize Bertrix Affilié #123303")
print("=" * 80)
sos = models.execute_kw(
    DB, uid, PASSWORD,
    "sale.order", "search_read",
    [["|", ("partner_id", "=", PID), ("partner_shipping_id", "=", PID)]],
    {"fields": ["id", "name", "date_order", "state", "amount_total", "invoice_status",
                "delivery_status", "user_id", "team_id"],
     "order": "date_order desc",
     "limit": 15}
)
for s in sos:
    user = s["user_id"][1] if s["user_id"] else "—"
    print(f"  {s['name']:<10} | {s['date_order'][:10]} | {s['state']:<8} | "
          f"{s['amount_total']:>8.2f} EUR | inv:{s.get('invoice_status', '—')} | "
          f"deliv:{s.get('delivery_status', '—')} | {user}")

# 3. Détail lignes S05489
print("\n" + "=" * 80)
print("LIGNES S05489 (dernière SO Bertrix)")
print("=" * 80)
so = models.execute_kw(
    DB, uid, PASSWORD,
    "sale.order", "search_read",
    [[("name", "=", "S05489")]],
    {"fields": ["id", "name", "state", "order_line", "amount_total", "delivery_status",
                "invoice_status", "date_order"]}
)
if so:
    so = so[0]
    print(f"  ID={so['id']}  state={so['state']}  total={so['amount_total']:.2f} EUR")
    print(f"  delivery_status={so.get('delivery_status')}  invoice_status={so.get('invoice_status')}")
    lines = models.execute_kw(
        DB, uid, PASSWORD,
        "sale.order.line", "read",
        [so["order_line"]],
        {"fields": ["product_id", "name", "product_uom_qty", "qty_delivered",
                    "qty_invoiced", "price_unit", "price_subtotal"]}
    )
    for l in lines:
        prod = l["product_id"][1] if l["product_id"] else "—"
        print(f"    {prod[:55]:<55} | ord={l['product_uom_qty']:>4} | "
              f"del={l['qty_delivered']:>4} | inv={l['qty_invoiced']:>4} | "
              f"PU={l['price_unit']:>6.2f} | sub={l['price_subtotal']:>7.2f}")

# 4. Stock pickings liés à Bertrix
print("\n" + "=" * 80)
print("DERNIÈRES LIVRAISONS Delhaize Bertrix")
print("=" * 80)
pickings = models.execute_kw(
    DB, uid, PASSWORD,
    "stock.picking", "search_read",
    [[("partner_id", "=", PID), ("state", "=", "done")]],
    {"fields": ["name", "scheduled_date", "date_done", "origin", "state"],
     "order": "date_done desc",
     "limit": 10}
)
for pk in pickings:
    print(f"  {pk['name']:<20} | done {pk.get('date_done', '—')[:10] if pk.get('date_done') else '—'} | "
          f"origin {pk.get('origin', '—')}")

# 5. Check parent Delhaize Le Lion + tag arret éventuel
if p.get("parent_id"):
    parent = models.execute_kw(
        DB, uid, PASSWORD,
        "res.partner", "read",
        [[p["parent_id"][0]]],
        {"fields": ["name", "sale_warn", "sale_warn_msg", "comment"]}
    )[0]
    print("\n" + "=" * 80)
    print(f"PARENT #{p['parent_id'][0]} — {parent['name']}")
    print("=" * 80)
    print(f"  sale_warn : {parent.get('sale_warn')}")
    if parent.get("sale_warn_msg"):
        print(f"  warn_msg  : {parent['sale_warn_msg'][:200]}")
    if parent.get("comment"):
        print(f"  comment   : {parent['comment'][:300]}")
