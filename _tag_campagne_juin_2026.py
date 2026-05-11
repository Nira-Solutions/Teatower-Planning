"""
Tagging Odoo pour campagne juin 2026 (Horeca + Revendeur dormants).

3 tags créés/appliqués :
- MC-202606-HORECA-ACTIF      : tag Horeca + dernière commande >= 2025-11-12
- MC-202606-HORECA-DORMANT    : tag Horeca + dernière commande <  2025-11-12 (ou aucune sur 24M)
- MC-202606-REVENDEUR-DORMANT : tag Revendeur + dernière commande <  2025-11-12

Génère aussi un code promo individuel par client (TT-J26-XXXXXX, déterministe MD5).

Sortie :
- CSV: data/mailchimp_juin_2026.csv (email, name, segment, promo_code)
- Tags appliqués dans Odoo (si DRY_RUN=False)
"""
import xmlrpc.client, sys, io, csv, hashlib, datetime as dt
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- CONFIG ---
DRY_RUN = False  # True = aucune écriture Odoo, juste compter
URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = "Teatower123"

CUTOFF_DATE = "2025-11-12"  # J-180 depuis 2026-05-11

# IDs tags Horeca et Revendeur (source: 2026-04-27_b2b_roadmap_data.md)
HORECA_TAG_IDS = [26, 84, 33, 31]
REVENDEUR_TAG_IDS = [28, 85, 80, 81]

NEW_TAGS = {
    "MC-202606-HORECA-ACTIF":      "Audience Mailchimp - Juin 2026 - Horeca actifs",
    "MC-202606-HORECA-DORMANT":    "Audience Mailchimp - Juin 2026 - Horeca dormants (relance)",
    "MC-202606-REVENDEUR-DORMANT": "Audience Mailchimp - Juin 2026 - Revendeur dormants (relance)",
}

OUT_CSV = Path(__file__).parent / "data" / "mailchimp_juin_2026.csv"

# --- ODOO CONNECTION ---
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def call(model, method, args, kwargs=None):
    return models.execute_kw(DB, uid, PWD, model, method, args, kwargs or {})

print(f"=== TAGGING CAMPAGNE JUIN 2026 ===")
print(f"Mode: {'DRY-RUN (aucune ecriture)' if DRY_RUN else 'EXECUTE (ecriture Odoo)'}")
print(f"Cutoff dormants: {CUTOFF_DATE} (= aujourd hui - 180j)\n")

# --- 1. Find/create new tags ---
new_tag_ids = {}
for tag_name, tag_descr in NEW_TAGS.items():
    existing = call("res.partner.category", "search",
                    [[("name", "=", tag_name)]], {"limit": 1})
    if existing:
        new_tag_ids[tag_name] = existing[0]
        print(f"Tag existant trouve: {tag_name} (id={existing[0]})")
    else:
        if DRY_RUN:
            new_tag_ids[tag_name] = -1
            print(f"Tag a creer (DRY): {tag_name}")
        else:
            tid = call("res.partner.category", "create",
                       [{"name": tag_name, "color": 4}])
            new_tag_ids[tag_name] = tid
            print(f"Tag CREE: {tag_name} (id={tid})")

# --- 2. Search partners by segment ---
# FILTRE STRICT: is_company=True (seulement les sociétés, pas contacts individuels)
# + filtre "au moins 1 commande historique" applique a l'etape 3
print(f"\n--- Recherche partners (is_company=True uniquement) ---")

horeca_partners = call("res.partner", "search_read",
    [[("category_id", "in", HORECA_TAG_IDS),
      ("active", "=", True),
      ("is_company", "=", True)]],
    {"fields": ["id", "name", "email", "category_id"], "limit": 5000})
print(f"Horeca companies tagges: {len(horeca_partners)}")

revendeur_partners = call("res.partner", "search_read",
    [[("category_id", "in", REVENDEUR_TAG_IDS),
      ("active", "=", True),
      ("is_company", "=", True)]],
    {"fields": ["id", "name", "email", "category_id"], "limit": 5000})
print(f"Revendeur companies tagges: {len(revendeur_partners)}")

# --- 3. Get last sale order per partner ---
def get_last_order_date(partner_ids):
    """Retourne {partner_id: 'YYYY-MM-DD'} ou {} si jamais commande."""
    if not partner_ids:
        return {}
    orders = call("sale.order", "search_read",
        [[("partner_id", "in", partner_ids),
          ("state", "in", ["sale", "done"])]],
        {"fields": ["partner_id", "date_order"], "order": "date_order desc"})
    last_per_partner = {}
    for o in orders:
        pid = o["partner_id"][0]
        if pid not in last_per_partner:
            last_per_partner[pid] = o["date_order"][:10]
    return last_per_partner

horeca_ids = [p["id"] for p in horeca_partners]
revendeur_ids = [p["id"] for p in revendeur_partners]

print(f"\n--- Recuperation dernieres commandes ---")
horeca_last = get_last_order_date(horeca_ids)
revendeur_last = get_last_order_date(revendeur_ids)
print(f"Horeca avec au moins 1 commande historique: {len(horeca_last)}/{len(horeca_partners)}")
print(f"Revendeur avec au moins 1 commande historique: {len(revendeur_last)}/{len(revendeur_partners)}")

# --- 4. Split actif/dormant ---
def gen_promo_code(partner_id):
    """Code unique deterministe par partner."""
    h = hashlib.md5(f"teatower-{partner_id}-202606".encode()).hexdigest()
    return f"TT-J26-{h[:6].upper()}"

# FILTRE STRICT: seulement les partners qui ont AU MOINS 1 commande dans l historique
# (sinon ce sont des prospects, pas des clients = on les exclut de la campagne de relance)
horeca_actif = []
horeca_dormant = []
horeca_no_history = 0
for p in horeca_partners:
    last = horeca_last.get(p["id"])
    if not last:
        horeca_no_history += 1
        continue  # pas client B2B
    p["promo_code"] = gen_promo_code(p["id"])
    p["last_order"] = last
    if last >= CUTOFF_DATE:
        horeca_actif.append(p)
    else:
        horeca_dormant.append(p)

revendeur_dormant = []
revendeur_actif_skipped = 0
revendeur_no_history = 0
for p in revendeur_partners:
    last = revendeur_last.get(p["id"])
    if not last:
        revendeur_no_history += 1
        continue  # pas client B2B
    p["promo_code"] = gen_promo_code(p["id"])
    p["last_order"] = last
    if last < CUTOFF_DATE:
        revendeur_dormant.append(p)
    else:
        revendeur_actif_skipped += 1

print(f"  (Horeca exclus - aucune commande historique: {horeca_no_history})")
print(f"  (Revendeur exclus - aucune commande historique: {revendeur_no_history})")

print(f"\n--- Segmentation BRUTE (avant dedup) ---")
print(f"Horeca ACTIF (>= {CUTOFF_DATE})     : {len(horeca_actif)}")
print(f"Horeca DORMANT (< {CUTOFF_DATE})    : {len(horeca_dormant)}")
print(f"Revendeur DORMANT (< {CUTOFF_DATE}) : {len(revendeur_dormant)}")
print(f"  (Revendeur actifs ignores cette campagne: {revendeur_actif_skipped})")

# --- DEDUP: un partner = 1 seul segment ---
# Priorite: HORECA-ACTIF > REVENDEUR-DORMANT > HORECA-DORMANT
assigned = {}  # partner_id -> segment
for p in horeca_actif:
    assigned[p["id"]] = ("HORECA-ACTIF", p)
for p in revendeur_dormant:
    if p["id"] not in assigned:
        assigned[p["id"]] = ("REVENDEUR-DORMANT", p)
for p in horeca_dormant:
    if p["id"] not in assigned:
        assigned[p["id"]] = ("HORECA-DORMANT", p)

# Rebuild lists post-dedup
horeca_actif    = [p for pid,(s,p) in assigned.items() if s == "HORECA-ACTIF"]
revendeur_dormant = [p for pid,(s,p) in assigned.items() if s == "REVENDEUR-DORMANT"]
horeca_dormant  = [p for pid,(s,p) in assigned.items() if s == "HORECA-DORMANT"]

print(f"\n--- Segmentation FINALE (apres dedup) ---")
print(f"Horeca ACTIF       : {len(horeca_actif)}")
print(f"Revendeur DORMANT  : {len(revendeur_dormant)}")
print(f"Horeca DORMANT     : {len(horeca_dormant)}")
print(f"TOTAL audiences juin: {len(horeca_actif) + len(horeca_dormant) + len(revendeur_dormant)}")

# --- 5. Filter partners with email (mailchimp ne sert a rien sans email) ---
def with_email(lst):
    return [p for p in lst if p.get("email") and "@" in (p.get("email") or "")]

ha_e = with_email(horeca_actif)
hd_e = with_email(horeca_dormant)
rd_e = with_email(revendeur_dormant)
print(f"\n--- Avec email valide ---")
print(f"Horeca ACTIF avec email     : {len(ha_e)}/{len(horeca_actif)}")
print(f"Horeca DORMANT avec email   : {len(hd_e)}/{len(horeca_dormant)}")
print(f"Revendeur DORMANT avec email: {len(rd_e)}/{len(revendeur_dormant)}")

# --- 6. Apply tags (or skip if DRY) ---
print(f"\n--- Application tags Odoo ---")
def apply_tag(partners, tag_id, tag_name):
    if not partners:
        print(f"  {tag_name}: 0 partners")
        return
    pids = [p["id"] for p in partners]
    if DRY_RUN:
        print(f"  {tag_name}: {len(pids)} partners (DRY, pas ecrit)")
        return
    # category_id est un many2many → command (4, id) pour add
    call("res.partner", "write",
         [pids, {"category_id": [(4, tag_id)]}])
    print(f"  {tag_name}: {len(pids)} partners TAGGED")

apply_tag(horeca_actif,     new_tag_ids["MC-202606-HORECA-ACTIF"],      "MC-202606-HORECA-ACTIF")
apply_tag(horeca_dormant,   new_tag_ids["MC-202606-HORECA-DORMANT"],    "MC-202606-HORECA-DORMANT")
apply_tag(revendeur_dormant, new_tag_ids["MC-202606-REVENDEUR-DORMANT"], "MC-202606-REVENDEUR-DORMANT")

# --- 7. Write CSV for Mailchimp ---
print(f"\n--- Export CSV Mailchimp ---")
OUT_CSV.parent.mkdir(exist_ok=True)
with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["email", "name", "segment", "promo_code", "last_order_date", "partner_id"])
    for p in ha_e:
        w.writerow([p["email"], p["name"], "HORECA-ACTIF", p["promo_code"], p["last_order"], p["id"]])
    for p in hd_e:
        w.writerow([p["email"], p["name"], "HORECA-DORMANT", p["promo_code"], p["last_order"], p["id"]])
    for p in rd_e:
        w.writerow([p["email"], p["name"], "REVENDEUR-DORMANT", p["promo_code"], p["last_order"], p["id"]])
print(f"CSV ecrit: {OUT_CSV}")
print(f"  -> {len(ha_e) + len(hd_e) + len(rd_e)} lignes")

# --- 8. Sample preview ---
print(f"\n--- Echantillon (5 par segment) ---")
def preview(lst, label):
    print(f"\n{label}:")
    for p in lst[:5]:
        print(f"  [{p['promo_code']}] {p['name'][:40]:40} | last={p['last_order']} | {p.get('email','(no email)')}")

preview(ha_e, "HORECA ACTIF")
preview(hd_e, "HORECA DORMANT")
preview(rd_e, "REVENDEUR DORMANT")

print(f"\n=== FIN ===")
print(f"Mode: {'DRY-RUN' if DRY_RUN else 'EXECUTE'}")
if DRY_RUN:
    print(f"=> Pour ecrire dans Odoo: passer DRY_RUN = False et relancer")
