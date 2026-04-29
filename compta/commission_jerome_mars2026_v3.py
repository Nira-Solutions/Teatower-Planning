"""
v3 — Verification finale par partenaire pour la commission mars 2026.
Pour chaque candidat, sortir TOUTES les SO + factures et leur statut.
Aussi : recherche large pour clients introuvables (Haine St Pierre, Ans, Gout-The Moulin).
"""
import xmlrpc.client
URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = "Teatower123"
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(m, meth, args, kw=None):
    return models.execute_kw(DB, uid, PWD, m, meth, args, kw or {})

# Known partners
KNOWN = {
    "Delhaize Recogne": 122091,
    "Intermarche Hannut (INTERMADIS)": 121874,
    "Carrefour Belgium - Corporate Village": 6596,
    "Hyper Carrefour Bomeree": 122467,
    "Hyper Carrefour Gosselies": 122466,
    "Carrefour Market Wellin": 122589,
    "Intermarche Hamoir": 122255,
    "Chez Jack (HORECA JACQUEMIN SRL)": 122410,
    "L'amandier Hotel": 122192,
    "VDM Patisserie": 121728,
    "Le Loft du Renard": 121779,
    "Villa Lorraine": 121215,
    "Urban Therapy": 3273,
    "Teroir de Magerotte": 121553,
}

print("="*80)
print("ALL SO + INVOICES par partenaire connu")
print("="*80)
for label, pid in KNOWN.items():
    print(f"\n##### {label} (#{pid}) #####")
    p = call("res.partner", "read", [[pid]],
             {"fields": ["name", "create_date", "category_id"]})[0]
    print(f"  name={p['name']!r}  created={p['create_date'][:10]}  cat={p['category_id']}")
    sos = call("sale.order", "search_read",
               [[("partner_id", "=", pid)]],
               {"fields": ["name", "date_order", "amount_untaxed", "state",
                           "invoice_status", "invoice_ids", "user_id"],
                "order": "date_order asc"})
    print(f"  SO total: {len(sos)}")
    for s in sos[:10]:
        user = s["user_id"][1] if s["user_id"] else "?"
        print(f"    {s['name']:10s} | {s['date_order'][:10]} | {s['amount_untaxed']:>9.2f} EUR | {s['state']:6s} | inv={s['invoice_status']} | by {user}")
    invs = call("account.move", "search_read",
                [[("partner_id", "=", pid),
                  ("move_type", "in", ["out_invoice", "out_refund"])]],
                {"fields": ["name", "invoice_date", "amount_untaxed",
                            "payment_state", "state", "move_type"],
                 "order": "invoice_date asc"})
    print(f"  Invoices total: {len(invs)}")
    for i in invs[:10]:
        print(f"    {i['name']:20s} | {i['invoice_date']} | {i['amount_untaxed']:>9.2f} | {i['move_type']:11s} | {i['state']:6s} | pay={i['payment_state']}")

# ----------------------------------------------------------------
# Recherche elargie pour clients introuvables
# ----------------------------------------------------------------
print("\n" + "="*80)
print("RECHERCHE ELARGIE — Carrefour Haine St Pierre / Hyper Carrefour Ans / Goût-Thé Moulin")
print("="*80)
for kw in ["Haine", "Hyper Carrefour", "Carrefour Ans", "ricardo_cazco", "lindsay_ghys",
           "willemskevin", "Gout", "Goût", "Thé du Moulin"]:
    ids = call("res.partner", "search",
               [[("name", "ilike", kw)]], {"limit": 30})
    if ids:
        ps = call("res.partner", "read", [ids],
                  {"fields": ["id", "name", "category_id", "email", "create_date"]})
        recent = [p for p in ps if (p.get("create_date") or "").startswith("2026")
                  or (p.get("create_date") or "").startswith("2025-1")
                  or (p.get("create_date") or "").startswith("2025-12")]
        if recent:
            print(f"\n  keyword={kw!r}  -> {len(recent)} recent matches")
            for p in recent:
                print(f"    #{p['id']}: {p['name']!r}  cat={p['category_id']}  email={p.get('email')}  created={p['create_date'][:10]}")
    # also email-based search
    email_ids = call("res.partner", "search",
                     [[("email", "ilike", kw)]], {"limit": 10})
    if email_ids:
        ps = call("res.partner", "read", [email_ids],
                  {"fields": ["id", "name", "category_id", "email", "create_date"]})
        print(f"\n  email contains {kw!r}  -> {len(ps)}")
        for p in ps:
            print(f"    #{p['id']}: {p['name']!r}  cat={p['category_id']}  email={p.get('email')}  created={p['create_date'][:10]}")

# ----------------------------------------------------------------
# SO mars 2026 par Jerome
# ----------------------------------------------------------------
print("\n" + "="*80)
print("SO mars 2026 — par Jerome Carlier (user)")
print("="*80)
users = call("res.users", "search_read",
             [[("name", "ilike", "Jerome")]],
             {"fields": ["id", "name", "login"]})
print("Users:", users)
jerome_ids = [u["id"] for u in users]
sos = call("sale.order", "search_read",
           [[("date_order", ">=", "2026-03-01"),
             ("date_order", "<=", "2026-03-31 23:59"),
             ("user_id", "in", jerome_ids),
             ("state", "in", ["sale", "done"])]],
           {"fields": ["name", "date_order", "amount_untaxed", "state",
                       "partner_id", "user_id"],
            "order": "date_order asc",
            "limit": 200})
print(f"\nTotal SO mars 2026 par Jerome: {len(sos)}")
for s in sos:
    pname = s["partner_id"][1] if s["partner_id"] else "?"
    print(f"  {s['name']:10s} | {s['date_order'][:10]} | {s['amount_untaxed']:>9.2f} EUR | {s['state']} | {pname}")
