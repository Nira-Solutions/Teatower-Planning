import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PASSWORD = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

# Search any partner with "Bertrix" in name OR city
partners = models.execute_kw(
    DB, uid, PASSWORD,
    "res.partner", "search_read",
    [[
        "|", "|", "|",
        ("name", "ilike", "Bertrix"),
        ("city", "ilike", "Bertrix"),
        ("street", "ilike", "Bertrix"),
        ("zip", "=", "6880"),
    ]],
    {"fields": ["id", "name", "parent_id", "street", "city", "zip", "phone", "email",
                "active", "sale_warn", "sale_warn_msg", "comment", "category_id"],
     "limit": 50}
)

print(f"=== {len(partners)} partners trouvés autour Bertrix (6880) ===\n")
for p in partners:
    parent = p["parent_id"][1] if p["parent_id"] else "—"
    print(f"#{p['id']:>7} | {p['name']:<55} | parent: {parent}")
    print(f"           {p.get('street', '')}, {p.get('zip', '')} {p.get('city', '')}")
    if p.get("phone"):
        print(f"           tel: {p['phone']}  email: {p.get('email', '')}")
    if p.get("sale_warn") and p["sale_warn"] != "no-message":
        print(f"           sale_warn: {p['sale_warn']} | msg: {p.get('sale_warn_msg', '')[:80]}")
    if p.get("comment"):
        c = p["comment"]
        if isinstance(c, str):
            print(f"           comment: {c[:150]}")
    print()

# Specifically look for any SO with Bertrix
print("\n=== SO confirmés où le partenaire contient 'Bertrix' ===")
sos = models.execute_kw(
    DB, uid, PASSWORD,
    "sale.order", "search_read",
    [[("state", "in", ["sale", "done"]),
      "|",
      ("partner_id.name", "ilike", "Bertrix"),
      ("partner_shipping_id.city", "ilike", "Bertrix")]],
    {"fields": ["id", "name", "partner_id", "partner_shipping_id", "date_order", "amount_total"],
     "order": "date_order desc",
     "limit": 30}
)
for s in sos:
    print(f"  {s['name']:<12} | {s['date_order'][:10]} | {s['amount_total']:>9.2f} EUR | partner: {s['partner_id'][1]} | ship: {s['partner_shipping_id'][1]}")
