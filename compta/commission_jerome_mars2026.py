"""
Calcul commission Jérôme Carlier — Mars 2026.

Règles (avenant 17/03/2026) :
- Croissance CA B2B (GMS+B2B Revendeurs+Horeca) HTVA, vs N-1.
- Barème (voir scale ci-dessous).
- Displays GMS : 100€/display, première commande ≥ 240€ HTVA.
- Nouveaux clients hors GMS : 65€/client, première commande ≥ 240€ HTVA.
- Grossiste = 2 clients si 1ère commande > 500€ HTVA.
"""
import xmlrpc.client
from datetime import datetime
from collections import defaultdict

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def call(model, method, args, kwargs=None):
    return models.execute_kw(DB, uid, PWD, model, method, args, kwargs or {})

print(f"UID: {uid}")

# ------------------------------------------------------------------
# 1. Find canal tags (B2B / GMS / Horeca)
# ------------------------------------------------------------------
print("\n=== Canal tags ===")
tag_ids = call("res.partner.category", "search_read",
               [[("name", "ilike", "GMS")]] +  # placeholder, see broader search below
               [], {"fields": ["id", "name", "parent_id"]})

# Broader: list all categories with relevant keywords
all_cats = call("res.partner.category", "search_read",
                [[("name", "ilike", "%")]],
                {"fields": ["id", "name", "parent_id"], "limit": 500})
relevant = [c for c in all_cats if any(k in c["name"].upper()
                                        for k in ["GMS", "HORECA", "B2B", "RESELLER", "REVENDEUR"])]
for t in relevant:
    print(t)
tag_ids = relevant

gms_tag_ids = [t["id"] for t in tag_ids if "GMS" in t["name"].upper()]
horeca_tag_ids = [t["id"] for t in tag_ids if "HORECA" in t["name"].upper() or "RECA" in t["name"].upper()]
b2b_tag_ids = [t["id"] for t in tag_ids if "B2B" in t["name"].upper() or "REVENDEUR" in t["name"].upper() or "RESELLER" in t["name"].upper()]

all_b2b_tags = gms_tag_ids + horeca_tag_ids + b2b_tag_ids
print(f"GMS tags: {gms_tag_ids}")
print(f"Horeca tags: {horeca_tag_ids}")
print(f"B2B Reseller tags: {b2b_tag_ids}")
print(f"All B2B-perimeter tags: {all_b2b_tags}")

# ------------------------------------------------------------------
# 2. CA B2B mars 2025 vs mars 2026
# ------------------------------------------------------------------
def ca_b2b(period_from, period_to):
    """CA HT net (out_invoice - out_refund) posted, partners with B2B tags."""
    # Find partners in B2B perimeter
    partner_ids = call("res.partner", "search",
                       [[("category_id", "in", all_b2b_tags)]], {"limit": 5000})
    print(f"  B2B partners (any tag): {len(partner_ids)}")

    # Sum invoiced lines for these partners in period
    invoices = call("account.move", "search_read",
                    [[("move_type", "in", ["out_invoice", "out_refund"]),
                      ("state", "=", "posted"),
                      ("invoice_date", ">=", period_from),
                      ("invoice_date", "<=", period_to),
                      ("partner_id", "in", partner_ids)]],
                    {"fields": ["amount_untaxed", "move_type", "partner_id", "name", "payment_state"]})
    total = 0.0
    paid = 0.0
    for inv in invoices:
        sign = -1 if inv["move_type"] == "out_refund" else 1
        amt = sign * inv["amount_untaxed"]
        total += amt
        if inv["payment_state"] in ("paid", "in_payment", "reversed"):
            paid += amt
    return {"invoiced": total, "paid": paid, "n_invoices": len(invoices)}

print("\n=== CA B2B mars 2025 ===")
mars_2025 = ca_b2b("2025-03-01", "2025-03-31")
print(mars_2025)

print("\n=== CA B2B mars 2026 ===")
mars_2026 = ca_b2b("2026-03-01", "2026-03-31")
print(mars_2026)

# ------------------------------------------------------------------
# 3. Vérification 1ère commande des clients listés (mars 2026)
# ------------------------------------------------------------------
LISTED_CLIENTS = [
    # (label, search_name, type)
    ("Delhaize Recogne", "Delhaize Recogne", "GMS"),
    ("Intermarche Hannut", "Intermarche Hannut", "GMS"),
    ("Carrefour Belgium - Corporate Village", "Corporate Village", "GMS"),
    ("Carrefour market Haine St Pierre", "Haine St Pierre", "GMS"),
    ("Hyper Carrefour Bomeree", "Bomeree", "GMS"),
    ("Hyper Carrefour Gosselies", "Gosselies", "GMS"),
    ("Hyper Carrefour Ans", "Ans", "GMS"),
    ("Carrefour Market Wellin", "Wellin", "GMS"),
    ("Intermarche Hamoir", "Hamoir", "GMS"),
    ("Chez Jack", "Chez Jack", "Horeca"),
    ("L'Amandier - Libramont", "Amandier", "Horeca"),
    ("VDM Patisserie", "VDM", "Horeca"),
    ("Le Loft du Renard", "Loft du Renard", "Horeca"),
    ("Le Gout-The du Moulin", "Gout-The du Moulin", "Horeca"),
    ("La villa Lorraine", "villa Lorraine", "Horeca"),
    ("Urban Therapy - PARIS", "Urban Therapy", "Revendeur"),
    ("Boucherie de Magerotte", "Magerotte", "Revendeur"),
]

def first_order_amount(name_search):
    """Find partner, then first sales invoice (posted) ever, returning untaxed amount."""
    partner_ids = call("res.partner", "search",
                       [[("name", "ilike", name_search)]], {"limit": 10})
    if not partner_ids:
        return []
    partners = call("res.partner", "read", [partner_ids],
                    {"fields": ["id", "name", "category_id", "vat"]})
    candidates = []
    for p in partners:
        invs = call("account.move", "search_read",
                    [[("partner_id", "=", p["id"]),
                      ("move_type", "=", "out_invoice"),
                      ("state", "=", "posted")]],
                    {"fields": ["name", "invoice_date", "amount_untaxed", "payment_state"],
                     "order": "invoice_date asc",
                     "limit": 5})
        candidates.append({"partner": p, "invoices": invs})
    return candidates

print("\n=== First orders for listed clients ===")
results = {}
for label, search, kind in LISTED_CLIENTS:
    print(f"\n--- {label} ({kind}) ---")
    res = first_order_amount(search)
    results[label] = res
    if not res:
        print("   no partner found")
        continue
    for r in res:
        p = r["partner"]
        print(f"   partner: {p['id']} - {p['name']} (cat={p['category_id']})")
        if not r["invoices"]:
            print(f"     (no posted invoice)")
        for i, inv in enumerate(r["invoices"][:3]):
            print(f"     inv {i+1}: {inv['name']} | {inv['invoice_date']} | {inv['amount_untaxed']:.2f} EUR | {inv['payment_state']}")

print("\n=== DONE ===")
