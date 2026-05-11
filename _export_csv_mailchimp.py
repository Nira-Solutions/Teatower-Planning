"""Export CSV simple pour Mailchimp : email + name + segment (sans code promo).

Source : tags MC-202606-HORECA-DORMANT et MC-202606-REVENDEUR-DORMANT
dans Odoo (deja appliques).
"""
import xmlrpc.client, sys, io, csv
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = "Teatower123"

TAGS = {
    "MC-202606-HORECA-DORMANT":    "HORECA-DORMANT",
    "MC-202606-REVENDEUR-DORMANT": "REVENDEUR-DORMANT",
}

OUT_CSV = Path(__file__).parent / "data" / "mailchimp_juin_2026.csv"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(m, me, a, k=None): return models.execute_kw(DB, uid, PWD, m, me, a, k or {})

rows = []
for tag_name, seg_label in TAGS.items():
    ids = call("res.partner.category", "search", [[("name", "=", tag_name)]], {"limit": 1})
    if not ids:
        print(f"Tag {tag_name} introuvable.")
        continue
    partners = call("res.partner", "search_read",
        [[("category_id", "in", [ids[0]])]],
        {"fields": ["id", "name", "email"], "limit": 5000})
    for p in partners:
        email = (p.get("email") or "").strip()
        if not email or "@" not in email:
            continue
        rows.append({
            "email":      email,
            "name":       p.get("name") or "",
            "segment":    seg_label,
            "partner_id": p["id"],
        })
    print(f"  {tag_name}: {len(partners)} partners ({sum(1 for r in rows if r['segment'] == seg_label)} avec email)")

OUT_CSV.parent.mkdir(exist_ok=True)
with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["email", "name", "segment", "partner_id"])
    w.writeheader()
    w.writerows(rows)

print(f"\nCSV ecrit : {OUT_CSV}")
print(f"  Total lignes : {len(rows)}")
