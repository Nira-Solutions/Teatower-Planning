#!/usr/bin/env python3
"""
HC250 (boites Horeca 25 enveloppes) : B2C a 15,00 EUR TTC, PRO maintenu a 10,00 EUR HT.

Contexte
--------
Les 28 refs HC250 sont a `list_price` 10,00 HT (TVA 6 %). Le `list_price` est partage
par la liste [1] "Par defaut" = les 6 caisses POS **et** tout le B2B. Le monter a
14,1509 (= 15,00 TTC) ferait donc aussi monter le prix PRO.

Ce script decouple les deux canaux :
  1. liste [8] "Horeca - Tarif PRO 25 enveloppes" : base = [7] B2B, + regles fixes
     HC250 a 10,00 HT (jusqu'au 31/10) puis 11,00 HT (a partir du 01/11, hausse
     tarifaire 2026 deja actee).
  2. filet de securite dans [7] : regles 11,00 HT a partir du 01/11, sinon les pros
     non-Horeca retomberaient sur le list_price B2C (14,15) apres expiration des
     regles du 04/08.
  3. list_price des 28 refs -> 14,1509 HT = 15,00 TTC (POS magasins + Shopify).
  4. liste [3] "Odoo x Shopify" : regles fixes 15,00 TTC pour que les commandes web
     importees soient au bon prix dans Odoo.

Exclusion : HC250898 "Pinacolada Bio version Horeca x25" (list_price 1,00 / TVA 21 %
/ sans code-barre / jamais vendue) = fiche incoherente, laissee telle quelle.

Usage :  python hc250_b2c_15eur.py [--apply]
"""
import os, sys, json, datetime
import xmlrpc.client

APPLY = "--apply" in sys.argv

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USR = "nicolas.raes@teatower.com"
PWD = os.environ["ODOO_PWD"]

PL_B2B = 7          # "B2B - tarif en vigueur"
PL_DEFAULT = 1      # "Par defaut"
PL_NEWSLETTER = 2   # "Newsletter 5%"
PL_SHOPIFY = 3      # "Odoo x Shopify PriceList"
PL_MERCH = 6        # "Merchandiser"

PRIX_PRO_HT = 10.00           # tarif PRO actuel, inchange
PRIX_PRO_HT_NOV = 11.00       # hausse tarifaire 2026, revendeurs au 01/11
PRIX_B2C_TTC = 15.00          # demande Nicolas 14/08/26
TVA = 6.0
PRIX_B2C_HT = round(PRIX_B2C_TTC / (1 + TVA / 100), 4)   # 14.1509

FIN_TARIF_ACTUEL = "2026-10-31 23:59:59"
DEBUT_TARIF_NOV = "2026-11-01 00:00:00"

EXCLUS = {"HC250898"}

uid = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB, USR, PWD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


def ex(model, method, *args, **kw):
    return models.execute_kw(DB, uid, PWD, model, method, list(args), kw)


def w(msg=""):
    print(msg, flush=True)


rollback = {"generated": datetime.datetime.now().isoformat(), "apply": APPLY}
w(f"{'=' * 78}\nHC250 -> B2C 15,00 TTC / PRO 10,00 HT     mode={'APPLY' if APPLY else 'DRY-RUN'}\n{'=' * 78}")

# ---------------------------------------------------------------- 0. perimetre
tmpls = ex("product.template", "search_read", [["default_code", "like", "HC25"]],
           fields=["id", "default_code", "name", "list_price", "taxes_id"],
           order="default_code")
cibles = [t for t in tmpls if t["default_code"] not in EXCLUS]
ecartes = [t for t in tmpls if t["default_code"] in EXCLUS]

bad_tax = [t for t in cibles if t["taxes_id"] != [8]]
if bad_tax:
    w("ARRET : TVA inattendue sur " + ", ".join(t["default_code"] for t in bad_tax))
    sys.exit(1)

w(f"\n[0] Perimetre : {len(cibles)} refs HC250 (TVA 6 %), {len(ecartes)} ecartee(s)")
for t in ecartes:
    w(f"    ECARTEE  {t['default_code']} - {t['name'][:44]} (list_price {t['list_price']}, TVA {t['taxes_id']})")

tids = [t["id"] for t in cibles]
variants = ex("product.product", "search_read", [["product_tmpl_id", "in", tids]],
              fields=["id", "default_code", "product_tmpl_id"])
vid_by_tmpl = {v["product_tmpl_id"][0]: v["id"] for v in variants}
if len(variants) != len(cibles):
    w(f"ARRET : {len(variants)} variantes pour {len(cibles)} templates (attendu 1 pour 1)")
    sys.exit(1)

# ------------------------------------------------- 1. liste de prix [8] Horeca
existante = ex("product.pricelist", "search_read",
               [["name", "=", "Horeca - Tarif PRO 25 enveloppes"]],
               fields=["id", "name"])
b2b = ex("product.pricelist", "read", [PL_B2B], fields=["id", "name", "currency_id", "company_id"])[0]

if existante:
    pl_horeca = existante[0]["id"]
    w(f"\n[1] Liste Horeca deja presente : [{pl_horeca}] (aucune creation)")
else:
    w(f"\n[1] Creation liste 'Horeca - Tarif PRO 25 enveloppes'"
      f" (devise {b2b['currency_id'][1]}, societe {b2b['company_id'][1]})")
    pl_horeca = None
    if APPLY:
        pl_horeca = ex("product.pricelist", "create", [{
            "name": "Horeca - Tarif PRO 25 enveloppes",
            "currency_id": b2b["currency_id"][0],
            "company_id": b2b["company_id"][0],
        }])[0]
        w(f"    -> creee : [{pl_horeca}]")
rollback["pricelist_horeca_id"] = pl_horeca

# regles de la liste Horeca
def regles_hc250(pricelist_id):
    """Regle 'socle B2B' + 28x10,00 HT jusqu'au 31/10 + 28x11,00 HT des le 01/11."""
    items = [{
        "pricelist_id": pricelist_id, "applied_on": "3_global",
        "compute_price": "formula", "base": "pricelist", "base_pricelist_id": PL_B2B,
        "price_discount": 0.0, "price_surcharge": 0.0,
    }]
    for t in cibles:
        items.append({
            "pricelist_id": pricelist_id, "applied_on": "1_product",
            "product_tmpl_id": t["id"], "compute_price": "fixed",
            "fixed_price": PRIX_PRO_HT, "date_end": FIN_TARIF_ACTUEL,
        })
        items.append({
            "pricelist_id": pricelist_id, "applied_on": "1_product",
            "product_tmpl_id": t["id"], "compute_price": "fixed",
            "fixed_price": PRIX_PRO_HT_NOV, "date_start": DEBUT_TARIF_NOV,
        })
    return items

created_horeca = []
nb_items = ex("product.pricelist.item", "search_count",
              [["pricelist_id", "=", pl_horeca]]) if pl_horeca else 0
if nb_items:
    w(f"    {nb_items} regles deja en place sur [{pl_horeca}], rien a creer")
else:
    w(f"    regles a creer : 1 socle (base = [{PL_B2B}] {b2b['name']})"
      f" + {len(cibles)} x {PRIX_PRO_HT:.2f} HT (<= 31/10)"
      f" + {len(cibles)} x {PRIX_PRO_HT_NOV:.2f} HT (>= 01/11)")
    if APPLY and pl_horeca:
        created_horeca = ex("product.pricelist.item", "create", regles_hc250(pl_horeca))
        w(f"    -> {len(created_horeca)} regles creees")
rollback["items_horeca"] = created_horeca

# ------------------------------------- 2. filet de securite dans [7] B2B (01/11)
deja = ex("product.pricelist.item", "search_read",
          [["pricelist_id", "=", PL_B2B], ["product_tmpl_id", "in", tids],
           ["date_start", ">=", "2026-11-01 00:00:00"]],
          fields=["id", "product_tmpl_id"])
w(f"\n[2] Filet [{PL_B2B}] B2B : les 28 regles actuelles a 10,00 expirent le 31/10 ->"
  f" sans regle de relais les pros retomberaient sur le list_price B2C.")
if deja:
    w(f"    {len(deja)} regles >= 01/11 deja presentes, rien a creer")
    created_b2b = []
else:
    items_b2b = [{
        "pricelist_id": PL_B2B, "applied_on": "1_product", "product_tmpl_id": t["id"],
        "compute_price": "fixed", "fixed_price": PRIX_PRO_HT_NOV,
        "date_start": DEBUT_TARIF_NOV,
    } for t in cibles]
    w(f"    a creer : {len(items_b2b)} regles a {PRIX_PRO_HT_NOV:.2f} HT des le 01/11")
    created_b2b = ex("product.pricelist.item", "create", items_b2b) if APPLY else []
    if APPLY:
        w(f"    -> {len(created_b2b)} regles creees")
rollback["items_b2b"] = created_b2b

# ----------------------------------------------- 3. rattachement clients Horeca
lines = ex("sale.order.line", "search_read",
           [["product_id", "in", [v["id"] for v in variants]],
            ["state", "in", ["sale", "done"]],
            ["order_id.date_order", ">=", "2024-08-01"]],
           fields=["order_partner_id"])
acheteurs = sorted({l["order_partner_id"][0] for l in lines})
infos = ex("res.partner", "read", acheteurs,
           fields=["id", "name", "property_product_pricelist", "active"])

a_deplacer, depuis_newsletter, flags = [], [], {"merch": [], "autre": []}
for p in infos:
    pl = p["property_product_pricelist"]
    cur = pl[0] if pl else None
    if cur in (PL_B2B, PL_DEFAULT):
        a_deplacer.append(p)
    elif cur == PL_NEWSLETTER:
        # Newsletter 5 % est une liste B2C (1.597 tickets POS) : y figer le prix pro
        # ferait fuiter les 10,00 HT vers les particuliers abonnes. Ces pros sont donc
        # bascules sur la liste Horeca (ils perdent les 5 % sur le reste du catalogue).
        depuis_newsletter.append(p)
        a_deplacer.append(p)
    elif cur == PL_MERCH:
        flags["merch"].append(p)
    elif cur != pl_horeca:
        flags["autre"].append(p)

w(f"\n[3] Clients ayant achete du HC250 depuis 08/2024 : {len(infos)}")
w(f"    a basculer sur la liste Horeca : {len(a_deplacer)}")
if depuis_newsletter:
    w(f"    dont {len(depuis_newsletter)} venant de [{PL_NEWSLETTER}] Newsletter 5 %"
      f" -> PERDENT les 5 % sur le reste du catalogue : "
      + ", ".join(f"{p['name']} #{p['id']}" for p in depuis_newsletter))
for k, lst in flags.items():
    if lst:
        w(f"    NON touches ({k}) : {len(lst)} -> " + ", ".join(f"{p['name']} #{p['id']}" for p in lst))

rollback["clients"] = [{"id": p["id"], "name": p["name"],
                        "pricelist_avant": p["property_product_pricelist"][0]}
                       for p in a_deplacer]
if APPLY and pl_horeca and a_deplacer:
    for p in a_deplacer:
        ex("res.partner", "write", [p["id"]], {"property_product_pricelist": pl_horeca})
    w(f"    -> {len(a_deplacer)} clients rattaches a [{pl_horeca}]")

# --------------------------------------------------------- 4. list_price -> B2C
w(f"\n[4] list_price des {len(cibles)} refs : 10,00 HT -> {PRIX_B2C_HT} HT"
  f" = {round(PRIX_B2C_HT * (1 + TVA / 100), 2):.2f} TTC")
rollback["list_price_avant"] = {t["default_code"]: t["list_price"] for t in cibles}
if APPLY:
    ex("product.template", "write", tids, {"list_price": PRIX_B2C_HT})
    w(f"    -> {len(tids)} fiches mises a jour")

# ------------------------------------------------- 5. liste [3] Odoo x Shopify
vids = [vid_by_tmpl[t["id"]] for t in cibles]
deja3 = ex("product.pricelist.item", "search_read",
           [["pricelist_id", "=", PL_SHOPIFY], ["product_id", "in", vids]],
           fields=["id", "product_id", "fixed_price"])
w(f"\n[5] Liste [{PL_SHOPIFY}] Odoo x Shopify (prix fixes TTC, niveau variante)")
if deja3:
    w(f"    {len(deja3)} regles HC250 deja presentes -> mise a jour a {PRIX_B2C_TTC:.2f}")
    if APPLY:
        ex("product.pricelist.item", "write", [i["id"] for i in deja3],
           {"fixed_price": PRIX_B2C_TTC})
    created_shop = []
else:
    items3 = [{"pricelist_id": PL_SHOPIFY, "applied_on": "0_product_variant",
               "product_id": vid, "compute_price": "fixed",
               "fixed_price": PRIX_B2C_TTC} for vid in vids]
    w(f"    a creer : {len(items3)} regles a {PRIX_B2C_TTC:.2f} TTC")
    created_shop = ex("product.pricelist.item", "create", items3) if APPLY else []
    if APPLY:
        w(f"    -> {len(created_shop)} regles creees")
rollback["items_shopify"] = created_shop

# ------------------------------------------------------------------ rollback
path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "reports", "hc250_b2c_15eur_rollback.json")
os.makedirs(os.path.dirname(path), exist_ok=True)
if APPLY:
    json.dump(rollback, open(path, "w"), indent=1, ensure_ascii=False)
    w(f"\nRollback ecrit : {path}")

w(f"\n{'=' * 78}")
w("DRY-RUN termine - relancer avec --apply pour ecrire." if not APPLY else "APPLIQUE.")
