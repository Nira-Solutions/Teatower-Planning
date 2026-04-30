"""
Commission Jerome Carlier — Avril 2026
Periode : 01/04/2026 -> 30/04/2026
Avenant contrat 17/03/2026

Sections :
1. CA B2B avril 2026 vs avril 2025 (barème croissance)
2. Displays GMS nouveaux en avril + rattrapages des 6 GMS de mars
3. Nouveaux clients hors GMS en avril + rattrapages clients mars
"""
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def call(m, meth, args, kw=None):
    return models.execute_kw(DB, uid, PWD, m, meth, args, kw or {})

print("="*80)
print("SECTION 0 — Jerome Carlier user_id")
print("="*80)
users = call("res.users", "search_read",
             [[("name", "ilike", "Jerome")]],
             {"fields": ["id", "name", "login"]})
print("Users Jerome:", users)
jerome_ids = [u["id"] for u in users]

# ----------------------------------------------------------------
# SECTION 1 — CA B2B avril 2026
# Tags canal: Canal GMS=88, Canal Horeca=84, Canal B2B=85, GMS legacy=27, HoReCA legacy=26
# ----------------------------------------------------------------
print("\n" + "="*80)
print("SECTION 1 — CA B2B avril 2026 (factures posted out_invoice)")
print("="*80)

# Tags utilisés pour classification B2B
B2B_TAGS = [88, 84, 85, 27, 26]  # Canal GMS, Canal Horeca, Canal B2B, GMS legacy, HoReCA legacy

# CA avril 2026 via account.move (out_invoice posted, avril 2026)
invoices_april = call("account.move", "search_read",
                      [[("move_type", "in", ["out_invoice", "out_refund"]),
                        ("state", "=", "posted"),
                        ("invoice_date", ">=", "2026-04-01"),
                        ("invoice_date", "<=", "2026-04-30")]],
                      {"fields": ["name", "invoice_date", "amount_untaxed", "move_type",
                                  "partner_id", "invoice_line_ids"],
                       "limit": 2000})
print(f"\nFactures/avoirs posted avril 2026 total: {len(invoices_april)}")

# Pour chaque partenaire, récupérer les tags
partner_ids_april = list(set(i["partner_id"][0] for i in invoices_april if i["partner_id"]))
print(f"Partenaires distincts: {len(partner_ids_april)}")

partners_tags = {}
if partner_ids_april:
    for i in range(0, len(partner_ids_april), 100):
        chunk = partner_ids_april[i:i+100]
        ps = call("res.partner", "read", [chunk],
                  {"fields": ["id", "name", "category_id"]})
        for p in ps:
            cats_raw = p["category_id"]
            if cats_raw and isinstance(cats_raw[0], (list, tuple)):
                cats = [c[0] for c in cats_raw]
            else:
                cats = [c for c in cats_raw] if cats_raw else []
            partners_tags[p["id"]] = {
                "name": p["name"],
                "cats": cats
            }

# Ségrégation GMS / B2B / Horeca
GMS_TAGS = [88, 27]
HORECA_TAGS = [84, 26]
B2B_REV_TAGS = [85]

ca_gms = 0.0
ca_horeca = 0.0
ca_b2b = 0.0
ca_b2b_total = 0.0

# Override manuel partenaires connus B2B (même logique que rapport data-bi)
# On classe en B2B tout partenaire tagué GMS, Horeca ou B2B
for inv in invoices_april:
    if not inv["partner_id"]:
        continue
    pid = inv["partner_id"][0]
    cats = partners_tags.get(pid, {}).get("cats", [])
    sign = -1 if inv["move_type"] == "out_refund" else 1
    amt = inv["amount_untaxed"] * sign

    is_gms = any(c in GMS_TAGS for c in cats)
    is_horeca = any(c in HORECA_TAGS for c in cats)
    is_b2b = any(c in B2B_REV_TAGS for c in cats)

    if is_gms:
        ca_gms += amt
    elif is_horeca:
        ca_horeca += amt
    elif is_b2b:
        ca_b2b += amt

ca_b2b_total = ca_gms + ca_horeca + ca_b2b
print(f"\n  CA GMS avril 2026 (tagué): {ca_gms:>10.2f} EUR")
print(f"  CA Horeca avril 2026 (tagué): {ca_horeca:>10.2f} EUR")
print(f"  CA B2B Revendeurs avril 2026 (tagué): {ca_b2b:>10.2f} EUR")
print(f"  TOTAL B2B (3 canaux) avril 2026: {ca_b2b_total:>10.2f} EUR")

# Baseline avril 2025 (si dispo dans Odoo)
invoices_april_2025 = call("account.move", "search_read",
                           [[("move_type", "in", ["out_invoice", "out_refund"]),
                             ("state", "=", "posted"),
                             ("invoice_date", ">=", "2025-04-01"),
                             ("invoice_date", "<=", "2025-04-30")]],
                           {"fields": ["name", "invoice_date", "amount_untaxed", "move_type",
                                       "partner_id"],
                            "limit": 2000})
print(f"\nFactures/avoirs posted avril 2025 total: {len(invoices_april_2025)}")

partner_ids_2025 = list(set(i["partner_id"][0] for i in invoices_april_2025 if i["partner_id"]))
partners_tags_2025 = {}
if partner_ids_2025:
    for i in range(0, len(partner_ids_2025), 100):
        chunk = partner_ids_2025[i:i+100]
        ps = call("res.partner", "read", [chunk],
                  {"fields": ["id", "name", "category_id"]})
        for p in ps:
            cats_raw = p["category_id"]
            if cats_raw and isinstance(cats_raw[0], (list, tuple)):
                cats = [c[0] for c in cats_raw]
            else:
                cats = [c for c in cats_raw] if cats_raw else []
            partners_tags_2025[p["id"]] = {
                "name": p["name"],
                "cats": cats
            }

ca_gms_2025 = 0.0
ca_horeca_2025 = 0.0
ca_b2b_2025 = 0.0
for inv in invoices_april_2025:
    if not inv["partner_id"]:
        continue
    pid = inv["partner_id"][0]
    cats = partners_tags_2025.get(pid, {}).get("cats", [])
    sign = -1 if inv["move_type"] == "out_refund" else 1
    amt = inv["amount_untaxed"] * sign
    is_gms = any(c in GMS_TAGS for c in cats)
    is_horeca = any(c in HORECA_TAGS for c in cats)
    is_b2b = any(c in B2B_REV_TAGS for c in cats)
    if is_gms:
        ca_gms_2025 += amt
    elif is_horeca:
        ca_horeca_2025 += amt
    elif is_b2b:
        ca_b2b_2025 += amt

ca_b2b_total_2025 = ca_gms_2025 + ca_horeca_2025 + ca_b2b_2025
print(f"\n  CA GMS avril 2025 (Odoo): {ca_gms_2025:>10.2f} EUR")
print(f"  CA Horeca avril 2025 (Odoo): {ca_horeca_2025:>10.2f} EUR")
print(f"  CA B2B Revendeurs avril 2025 (Odoo): {ca_b2b_2025:>10.2f} EUR")
print(f"  TOTAL B2B (3 canaux) avril 2025: {ca_b2b_total_2025:>10.2f} EUR")

# ----------------------------------------------------------------
# SECTION 2 — Displays GMS — partenaires créés / 1ère SO en avril
# ----------------------------------------------------------------
print("\n" + "="*80)
print("SECTION 2 — Nouveaux partenaires GMS créés ou 1ère SO en avril 2026")
print("="*80)

# 2a) Partenaires GMS créés en avril 2026
gms_created_april = call("res.partner", "search_read",
                         [[("category_id", "in", GMS_TAGS),
                           ("create_date", ">=", "2026-04-01"),
                           ("create_date", "<=", "2026-04-30 23:59:59")]],
                         {"fields": ["id", "name", "create_date", "category_id"],
                          "order": "create_date asc"})
print(f"\nPartenaires GMS créés en avril 2026: {len(gms_created_april)}")
for p in gms_created_april:
    print(f"  #{p['id']:6d}: {p['name']!r:50s} créé={p['create_date'][:10]}  cats={p['category_id']}")

# 2b) Rattrapages des 6 GMS de mars sans 1ère commande
# (Recogne 122091, Haine St Pierre 122412, Bomerée 122467, Gosselies 122466, Wellin 122589)
# + Ans (introuvable en mars)
MARS_GMS_RATTRAPAGES = {
    "Delhaize Recogne": 122091,
    "Carrefour Market Haine Saint Pierre": 122412,
    "Hyper Carrefour Bomerée": 122467,
    "Hyper Carrefour Gosselies": 122466,
    "Carrefour Market Wellin": 122589,
}

print(f"\n--- Rattrapages 6 GMS de mars (vérification 1ère SO en avril) ---")
for label, pid in MARS_GMS_RATTRAPAGES.items():
    sos = call("sale.order", "search_read",
               [[("partner_id", "=", pid),
                 ("state", "in", ["sale", "done"])]],
               {"fields": ["name", "date_order", "amount_untaxed", "state", "user_id"],
                "order": "date_order asc",
                "limit": 10})
    print(f"\n  {label} (#{pid}): {len(sos)} SO confirmées au total")
    for s in sos:
        user = s["user_id"][1] if s["user_id"] else "?"
        print(f"    {s['name']:10s} | {s['date_order'][:10]} | {s['amount_untaxed']:>9.2f} EUR | {s['state']} | by {user}")

# Recherche Hyper Carrefour Ans
print("\n--- Recherche Hyper Carrefour Ans ---")
for kw in ["Carrefour Ans", "Ans", "Hyper Carrefour Ans"]:
    ids = call("res.partner", "search",
               [[("name", "ilike", kw),
                 ("create_date", ">=", "2026-01-01")]],
               {"limit": 20})
    if ids:
        ps = call("res.partner", "read", [ids],
                  {"fields": ["id", "name", "category_id", "create_date", "email"]})
        print(f"  kw={kw!r}: {len(ps)} résultats")
        for p in ps:
            print(f"    #{p['id']}: {p['name']!r}  cats={p['category_id']}  created={p['create_date'][:10]}")

# ----------------------------------------------------------------
# SECTION 3 — Nouveaux clients non-GMS en avril 2026
# ----------------------------------------------------------------
print("\n" + "="*80)
print("SECTION 3 — SO confirmées par Jérôme en avril 2026")
print("="*80)

# Toutes SO confirmées en avril 2026 par Jérôme
sos_april = call("sale.order", "search_read",
                 [[("date_order", ">=", "2026-04-01"),
                   ("date_order", "<=", "2026-04-30 23:59:59"),
                   ("user_id", "in", jerome_ids),
                   ("state", "in", ["sale", "done"])]],
                 {"fields": ["name", "date_order", "amount_untaxed", "state",
                             "partner_id", "user_id"],
                  "order": "date_order asc",
                  "limit": 500})
print(f"\nSO confirmées par Jérôme en avril 2026: {len(sos_april)}")
for s in sos_april:
    pname = s["partner_id"][1] if s["partner_id"] else "?"
    print(f"  {s['name']:10s} | {s['date_order'][:10]} | {s['amount_untaxed']:>9.2f} EUR | {s['state']} | {pname}")

# SO ≥ 240€ avec partenaires créés en 2026
print("\n--- Partenaires crees en 2026 avec SO >= 240 EUR en avril ---")
new_partners_2026 = call("res.partner", "search_read",
                         [[("create_date", ">=", "2026-01-01"),
                           ("create_date", "<=", "2026-04-30 23:59:59")]],
                         {"fields": ["id", "name", "create_date", "category_id"],
                          "limit": 500})
new_partner_ids_2026 = [p["id"] for p in new_partners_2026]
def extract_cat_ids(cat_list):
    if not cat_list:
        return []
    if isinstance(cat_list[0], (list, tuple)):
        return [c[0] for c in cat_list]
    return list(cat_list)

new_partner_cats = {p["id"]: extract_cat_ids(p["category_id"])
                    for p in new_partners_2026}
new_partner_names = {p["id"]: p["name"] for p in new_partners_2026}
new_partner_created = {p["id"]: p["create_date"][:10] for p in new_partners_2026}

print(f"Partenaires créés en 2026 (jusqu'au 30/04): {len(new_partner_ids_2026)}")

# Pour chaque nouveau partenaire 2026: trouver leur 1ère SO tous temps
sos_new_partners = call("sale.order", "search_read",
                        [[("partner_id", "in", new_partner_ids_2026),
                          ("state", "in", ["sale", "done"])]],
                        {"fields": ["name", "date_order", "amount_untaxed", "state",
                                    "partner_id", "user_id"],
                         "order": "date_order asc",
                         "limit": 1000})

# Grouper par partenaire — 1ère SO
first_so_by_partner = {}
for s in sos_new_partners:
    pid = s["partner_id"][0]
    if pid not in first_so_by_partner:
        first_so_by_partner[pid] = s

# Filtrer: 1ère SO en avril 2026 ET ≥ 240€
print("\n--- Nouveaux partenaires avec 1ère SO en AVRIL 2026 ≥ 240€ ---")
eligible_new = []
for pid, s in first_so_by_partner.items():
    date_so = s["date_order"][:10]
    if date_so >= "2026-04-01" and date_so <= "2026-04-30" and s["amount_untaxed"] >= 240.0:
        cats = new_partner_cats.get(pid, [])
        is_gms = any(c in GMS_TAGS for c in cats)
        entry = {
            "pid": pid,
            "name": new_partner_names.get(pid, "?"),
            "created": new_partner_created.get(pid, "?"),
            "cats": cats,
            "is_gms": is_gms,
            "so_name": s["name"],
            "so_date": date_so,
            "amount": s["amount_untaxed"],
            "user": s["user_id"][1] if s["user_id"] else "?"
        }
        eligible_new.append(entry)
        cat_label = "GMS" if is_gms else "non-GMS"
        print(f"  #{pid}: {new_partner_names.get(pid,'?')!r:50s} créé={new_partner_created.get(pid,'?')}  "
              f"1ère SO={s['name']} {date_so} {s['amount_untaxed']:.2f} EUR  [{cat_label}]  by {entry['user']}")

# 3b) Rattrapages clients hors GMS de mars
# Le Loft du Renard #121779 (50€ en mars) + Villa Lorraine #121215 (annulée)
MARS_NONSGMS_RATTRAPAGES = {
    "Le Loft du Renard": 121779,
    "La Villa Lorraine": 121215,
}
print("\n--- Rattrapages clients non-GMS de mars (nouvelle SO ≥ 240€ en avril?) ---")
for label, pid in MARS_NONSGMS_RATTRAPAGES.items():
    sos = call("sale.order", "search_read",
               [[("partner_id", "=", pid),
                 ("state", "in", ["sale", "done"]),
                 ("date_order", ">=", "2026-04-01"),
                 ("date_order", "<=", "2026-04-30 23:59:59")]],
               {"fields": ["name", "date_order", "amount_untaxed", "state", "user_id"],
                "order": "date_order asc"})
    if sos:
        for s in sos:
            user = s["user_id"][1] if s["user_id"] else "?"
            print(f"  {label} (#{pid}): {s['name']} | {s['date_order'][:10]} | {s['amount_untaxed']:.2f} EUR | {s['state']} | by {user}")
    else:
        print(f"  {label} (#{pid}): aucune SO confirmée en avril 2026")

# 3c) Cas CM Bastogne CC Port (lead #288, partner #123189, devis S05467)
print("\n--- CM Bastogne CC Port (lead #288, partner #123189, S05467) ---")
bastogne_pid = 123189
sos_bast = call("sale.order", "search_read",
                [[("partner_id", "=", bastogne_pid)]],
                {"fields": ["name", "date_order", "amount_untaxed", "state", "user_id"],
                 "order": "date_order asc"})
print(f"  Partner #123189 — SO totales: {len(sos_bast)}")
for s in sos_bast:
    user = s["user_id"][1] if s["user_id"] else "?"
    print(f"    {s['name']:10s} | {s['date_order'][:10]} | {s['amount_untaxed']:.2f} EUR | {s['state']} | by {user}")

# Chercher S05467 directement
s5467 = call("sale.order", "search_read",
             [[("name", "=", "S05467")]],
             {"fields": ["name", "date_order", "amount_untaxed", "state", "partner_id", "user_id"]})
print(f"  S05467 direct: {s5467}")

# ----------------------------------------------------------------
# SECTION 4 — Résumé final
# ----------------------------------------------------------------
print("\n" + "="*80)
print("SECTION 4 — RÉSUMÉ")
print("="*80)

if ca_b2b_total_2025 > 0:
    croissance = (ca_b2b_total - ca_b2b_total_2025) / ca_b2b_total_2025 * 100
    print(f"\nCroissance CA B2B avril 2026 vs avril 2025: {croissance:.1f}%")
    print(f"  Avril 2025 (Odoo): {ca_b2b_total_2025:.2f} EUR")
    print(f"  Avril 2026 (Odoo): {ca_b2b_total:.2f} EUR")
else:
    print(f"\nCA B2B avril 2025 (Odoo): {ca_b2b_total_2025:.2f} EUR — à confronter au rapport data-bi")
    print(f"CA B2B avril 2026 (data-bi): voir rapport (forecast 77.930 EUR)")

print(f"\nNouveaux partenaires créés en 2026 avec 1ère SO en avril ≥ 240€: {len(eligible_new)}")
gms_eligible = [e for e in eligible_new if e["is_gms"]]
non_gms_eligible = [e for e in eligible_new if not e["is_gms"]]
print(f"  dont GMS: {len(gms_eligible)}")
print(f"  dont non-GMS: {len(non_gms_eligible)}")
