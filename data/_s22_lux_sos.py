"""Check SO récentes + delivery_status pour magasins Lux/Bastogne axe S22 mercredi 27/05."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PASSWORD = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

PIDS = {
    122091: "Delhaize Recogne (Libramont)",
    123303: "Delhaize Bertrix",
    123189: "CM Bastogne CC Port",
    8558:   "AD Delhaize Bastogne",
    123067: "Proxy Delhaize Maissin",
    122589: "CM Wellin (Tier B retard 21j)",
}

for pid, lbl in PIDS.items():
    print(f"\n=== #{pid} {lbl} ===")

    # Partner comment + warn
    p = models.execute_kw(
        DB, uid, PASSWORD, "res.partner", "read",
        [[pid]],
        {"fields": ["name", "phone", "email", "comment", "sale_warn", "sale_warn_msg"]}
    )[0]
    print(f"  Tel: {p.get('phone')}  Mail: {p.get('email')}")
    if p.get("comment"):
        c = p["comment"]
        if isinstance(c, str):
            print(f"  Comment: {c[:300]}")

    # SO ouvertes (sale) ou récentes
    sos = models.execute_kw(
        DB, uid, PASSWORD, "sale.order", "search_read",
        [["|", ("partner_id", "=", pid), ("partner_shipping_id", "=", pid)]],
        {"fields": ["name", "date_order", "state", "amount_total", "delivery_status",
                    "invoice_status"],
         "order": "date_order desc",
         "limit": 4}
    )
    for s in sos:
        print(f"  SO {s['name']:<10} | {s['date_order'][:10]} | {s['state']:<8} | "
              f"{s['amount_total']:>7.2f} EUR | deliv={s.get('delivery_status','-')} inv={s.get('invoice_status','-')}")
