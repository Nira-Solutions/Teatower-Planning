"""Scan Odoo for Famenne candidates to densify Friday 15/05/2026 planning."""
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


def search_read(model, domain, fields, limit=None, order=None):
    kw = {"fields": fields}
    if limit:
        kw["limit"] = limit
    if order:
        kw["order"] = order
    return models.execute_kw(DB, uid, PWD, model, "search_read", [domain], kw)


# Find partners in zones 6900, 6990, 6940
candidates_zip = ["6900", "6990", "6940"]
candidates_name = [
    "Marche-en-Famenne", "Marche", "Hotton", "Durbuy",
]

# GMS tag id = 27
partners = search_read(
    "res.partner",
    [
        ("category_id", "in", [27]),
        ("zip", "in", candidates_zip),
    ],
    ["id", "name", "zip", "city", "street", "phone", "mobile", "email", "comment", "sale_warn", "sale_warn_msg"],
    limit=50,
)

print(f"# {len(partners)} partners GMS in zones 6900/6990/6940")
for p in partners:
    arret = "ARRET" if (p.get("sale_warn") == "block" or "[ARRET" in (p.get("comment") or "")) else ""
    print(f"\n## {p['name']} (#{p['id']}) {arret}")
    print(f"  ZIP {p['zip']} {p.get('city','')}")
    print(f"  Adresse: {p.get('street','')}")
    print(f"  Tel: {p.get('phone','') or p.get('mobile','')}")
    print(f"  Email: {p.get('email','')}")
    comment = (p.get("comment") or "")[:500].replace("\n", " | ")
    print(f"  Comment: {comment}")

    # Sales for last 12 months
    since = (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d")
    sos = search_read(
        "sale.order",
        [
            ("partner_id", "child_of", p["id"]),
            ("state", "in", ["sale", "done"]),
            ("date_order", ">=", since),
        ],
        ["name", "date_order", "amount_total"],
        order="date_order desc",
    )
    if sos:
        last = sos[0]
        days_since = (datetime.now() - datetime.strptime(last["date_order"][:10], "%Y-%m-%d")).days
        avg = sum(s["amount_total"] for s in sos) / len(sos)
        total = sum(s["amount_total"] for s in sos)
        print(f"  SO count: {len(sos)}, last: {last['name']} {last['date_order'][:10]} ({days_since}j), avg: {avg:.0f}€, total: {total:.0f}€")
    else:
        print("  Pas de SO 12 derniers mois")
