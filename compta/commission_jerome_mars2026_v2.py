"""
v2 — Investigation approfondie : sale.order + account.move + recherche elargie.
"""
import xmlrpc.client
from collections import defaultdict
import json

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

# ----------------------------------------------------------
# Investigate listed customers — broader search + sale.order
# ----------------------------------------------------------
LISTED = [
    ("Delhaize Recogne", ["Recogne", "046780"], "GMS"),
    ("Intermarche Hannut", ["Hannut", "INTERMADIS"], "GMS"),
    ("Carrefour Belgium - Corporate Village", ["Corporate Village"], "GMS"),
    ("Carrefour market Haine St Pierre", ["Haine", "St Pierre", "Saint Pierre", "Saint-Pierre"], "GMS"),
    ("Hyper Carrefour Bomeree", ["Bomeree", "Bomer"], "GMS"),
    ("Hyper Carrefour Gosselies", ["Hyper Carrefour Gosselies"], "GMS"),
    ("Hyper Carrefour Ans", ["Hyper Carrefour Ans", "Carrefour Ans"], "GMS"),
    ("Carrefour Market Wellin", ["Wellin"], "GMS"),
    ("Intermarche Hamoir", ["Hamoir"], "GMS"),
    ("Chez Jack", ["Chez Jack", "JACQUEMIN"], "Horeca"),
    ("L'Amandier - Libramont", ["amandier"], "Horeca"),
    ("VDM Patisserie", ["VDM"], "Horeca"),
    ("Le Loft du Renard", ["Loft du Renard"], "Horeca"),
    ("Le Gout-The du Moulin", ["Gout", "Goût", "Moulin", "willemskevin"], "Horeca"),
    ("La villa Lorraine", ["villa Lorraine"], "Horeca"),
    ("Urban Therapy - PARIS", ["Urban Therapy"], "Revendeur"),
    ("Boucherie de Magerotte", ["Magerotte", "Teroir"], "Revendeur"),
]

def find_partners(keywords):
    out = []
    for kw in keywords:
        ids = call("res.partner", "search",
                   [[("name", "ilike", kw)]], {"limit": 20})
        if ids:
            ps = call("res.partner", "read", [ids],
                      {"fields": ["id", "name", "category_id", "vat", "create_date", "email"]})
            out.extend(ps)
    # dedupe
    seen = set()
    uniq = []
    for p in out:
        if p["id"] not in seen:
            seen.add(p["id"])
            uniq.append(p)
    return uniq

def first_invoice(partner_id):
    invs = call("account.move", "search_read",
                [[("partner_id", "=", partner_id),
                  ("move_type", "=", "out_invoice"),
                  ("state", "=", "posted")]],
                {"fields": ["name", "invoice_date", "amount_untaxed", "payment_state"],
                 "order": "invoice_date asc",
                 "limit": 3})
    return invs

def first_sale_order(partner_id):
    sos = call("sale.order", "search_read",
               [[("partner_id", "=", partner_id),
                 ("state", "in", ["sale", "done", "draft", "sent"])]],
               {"fields": ["name", "date_order", "amount_untaxed", "state", "invoice_status"],
                "order": "date_order asc",
                "limit": 5})
    return sos

print("\n" + "="*80)
print("CLIENT-BY-CLIENT")
print("="*80)

results = {}
for label, keywords, kind in LISTED:
    print(f"\n##### {label} ({kind}) #####")
    parts = find_partners(keywords)
    print(f"  -> {len(parts)} partner candidates")
    interesting = []
    for p in parts:
        invs = first_invoice(p["id"])
        sos = first_sale_order(p["id"])
        # show if has invoice OR SO in 2026
        has_2026 = any(i["invoice_date"] and i["invoice_date"].startswith("2026") for i in invs) \
                or any(s["date_order"] and s["date_order"].startswith("2026") for s in sos)
        has_anything = bool(invs) or bool(sos)
        if has_anything:
            interesting.append((p, invs, sos))
    if not interesting:
        print("  !!! No partner has any invoice/order")
    for p, invs, sos in interesting[:5]:
        print(f"  partner #{p['id']}: {p['name']!r}  cat={p['category_id']}  email={p.get('email')}")
        for i in invs[:3]:
            print(f"      INV {i['name']} | {i['invoice_date']} | {i['amount_untaxed']:.2f} EUR | {i['payment_state']}")
        for s in sos[:3]:
            print(f"      SO  {s['name']} | {s['date_order'][:10]} | {s['amount_untaxed']:.2f} EUR | {s['state']} | inv={s['invoice_status']}")
    results[label] = [(p["id"], p["name"]) for p, _, _ in interesting]

print("\n" + "="*80)
print("CA B2B mars 2025 vs mars 2026 — methodo data-bi (par tag canal)")
print("="*80)

# All canaux tags
GMS_TAGS = [88, 27]
HORECA_TAGS = [84, 26, 79, 33, 31]
B2B_TAGS = [83, 85, 28]

def ca_for_period(date_from, date_to):
    """Return CA HT net per canal, classifying invoices by partner tags."""
    invoices = call("account.move", "search_read",
                    [[("move_type", "in", ["out_invoice", "out_refund"]),
                      ("state", "=", "posted"),
                      ("invoice_date", ">=", date_from),
                      ("invoice_date", "<=", date_to)]],
                    {"fields": ["amount_untaxed", "move_type", "partner_id", "name", "payment_state"]})
    print(f"  total invoices in {date_from}..{date_to}: {len(invoices)}")
    partner_ids = list({inv["partner_id"][0] for inv in invoices if inv["partner_id"]})
    parts = call("res.partner", "read", [partner_ids],
                 {"fields": ["id", "name", "category_id"]})
    cats_by_pid = {p["id"]: p["category_id"] for p in parts}

    by_canal = defaultdict(lambda: {"ht": 0.0, "n_inv": 0, "n_clients": set(), "paid": 0.0})
    for inv in invoices:
        sign = -1 if inv["move_type"] == "out_refund" else 1
        amt = sign * inv["amount_untaxed"]
        pid = inv["partner_id"][0] if inv["partner_id"] else 0
        cats = cats_by_pid.get(pid, [])
        if any(c in GMS_TAGS for c in cats):
            canal = "GMS"
        elif any(c in B2B_TAGS for c in cats):
            canal = "B2B Revendeurs"
        elif any(c in HORECA_TAGS for c in cats):
            canal = "Horeca"
        else:
            canal = "Autres"
        by_canal[canal]["ht"] += amt
        by_canal[canal]["n_inv"] += 1
        by_canal[canal]["n_clients"].add(pid)
        if inv["payment_state"] in ("paid", "in_payment", "reversed"):
            by_canal[canal]["paid"] += amt
    return by_canal

print("\n--- mars 2025 ---")
m2025 = ca_for_period("2025-03-01", "2025-03-31")
for canal, d in m2025.items():
    print(f"  {canal:20s} ht={d['ht']:>10.2f} EUR  paid={d['paid']:>10.2f}  invoices={d['n_inv']:>4}  clients={len(d['n_clients']):>4}")
total_b2b_2025 = sum(d["ht"] for c, d in m2025.items() if c != "Autres")
print(f"  >>> Total B2B (GMS+B2B+Horeca) mars 2025: {total_b2b_2025:.2f} EUR")

print("\n--- mars 2026 ---")
m2026 = ca_for_period("2026-03-01", "2026-03-31")
for canal, d in m2026.items():
    print(f"  {canal:20s} ht={d['ht']:>10.2f} EUR  paid={d['paid']:>10.2f}  invoices={d['n_inv']:>4}  clients={len(d['n_clients']):>4}")
total_b2b_2026 = sum(d["ht"] for c, d in m2026.items() if c != "Autres")
print(f"  >>> Total B2B (GMS+B2B+Horeca) mars 2026: {total_b2b_2026:.2f} EUR")

if total_b2b_2025 > 0:
    growth = (total_b2b_2026 / total_b2b_2025 - 1) * 100
    print(f"\n  Growth: {growth:+.1f}%")
print("\n=== DONE ===")
