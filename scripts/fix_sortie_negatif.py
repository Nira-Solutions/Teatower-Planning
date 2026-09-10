# -*- coding: utf-8 -*-
"""
Garde-fou : resorbe le stock negatif des zones de sortie et debloque les livraisons.

PROBLEME
--------
L'entrepot Teatower (#1) est le seul des 9 a tourner en `pick_ship` (2 etapes :
TT/PICK puis TT/OUT via TT/Sortie). La logistique valide les TT/OUT avec les
quantites reelles expediees, sans attendre que la reservation soit faite depuis
TT/Sortie. Odoo autorise le negatif dans un emplacement interne : TT/Sortie
plonge donc en dessous de zero, et chaque nouveau TT/PICK sert a combler la
dette au lieu d'alimenter la commande qui l'a declenche. Cette commande-la
reste bloquee en `waiting`.

CORRECTION
----------
Un quant negatif dans TT/Sortie signifie : la marchandise est physiquement
partie EN PASSANT par la zone de sortie, mais TT/Stock la compte encore.
Le transfert interne TT/Stock -> TT/Sortie remet donc les compteurs d'aplomb
SANS creer ni detruire de stock : le total entrepot est inchange.
Ce n'est PAS un ajustement d'inventaire.

Ce qui ne peut pas etre couvert (TT/Stock lui-meme a court) est signale : la
c'est un vrai ecart physique, il faut un comptage, pas un script.

Usage : python scripts/fix_sortie_negatif.py [--apply]
"""
import os
import sys
import xmlrpc.client

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ["ODOO_PWD"]
UID = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
_m = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")


def call(model, method, args, kw=None):
    return _m.execute_kw(DB, UID, PWD, model, method, args, kw or {})


def safe(model, method, args, kw=None):
    """button_validate & co renvoient parfois None -> 'cannot marshal None'.
    L'ecriture a REUSSI : on avale l'erreur au lieu de rejouer l'action."""
    try:
        return call(model, method, args, kw)
    except TypeError as e:
        if "marshal None" in str(e):
            return None
        raise


# (entrepot, emplacement stock, emplacement sortie, type d'operation interne, type OUT)
SCOPE = dict(wh="Teatower", stock_loc=8, out_loc=11, internal_type=3, out_type=2)

APPLY = "--apply" in sys.argv
print("MODE :", "APPLY" if APPLY else "DRY-RUN")
print("=" * 96)

# ------------------------------- 1. dette de TT/Sortie + demande des livraisons ouvertes
#
# besoin(produit) = demande des TT/OUT encore ouverts  -  disponible reel en TT/Sortie
#                   (le disponible est negatif quand la zone est a decouvert, donc la
#                    dette et la demande s'additionnent naturellement)
#
libre_sortie, noms = {}, {}
for q in call("stock.quant", "search_read",
              [[["location_id", "=", SCOPE["out_loc"]]]],
              {"fields": ["product_id", "quantity", "reserved_quantity"]}):
    pid = q["product_id"][0]
    libre_sortie[pid] = libre_sortie.get(pid, 0.0) + q["quantity"] - q["reserved_quantity"]
    noms[pid] = q["product_id"][1]

demande = {}
for m in call("stock.move", "search_read",
              [[["location_id", "=", SCOPE["out_loc"]],
                ["state", "in", ["waiting", "confirmed", "partially_available", "assigned"]]]],
              {"fields": ["product_id", "product_uom_qty", "quantity"]}):
    pid = m["product_id"][0]
    manque = m["product_uom_qty"] - m["quantity"]
    if manque > 0:
        demande[pid] = demande.get(pid, 0.0) + manque
        noms.setdefault(pid, m["product_id"][1])

concernes = sorted(set(list(demande) + [p for p, v in libre_sortie.items() if v < 0]))
print("TT/Sortie : %d SKU a decouvert, %d SKU reclames par une livraison ouverte"
      % (sum(1 for v in libre_sortie.values() if v < 0), len(demande)))

# ------------------------------------------- 2. ce que TT/Stock peut reellement couvrir
lignes, decouverts = [], []
for pid in concernes:
    dispo_sortie = libre_sortie.get(pid, 0.0)
    besoin = demande.get(pid, 0.0) - dispo_sortie
    if besoin <= 0:
        continue
    dispo = call("stock.quant", "search_read",
                 [[["product_id", "=", pid],
                   ["location_id", "child_of", SCOPE["stock_loc"]]]],
                 {"fields": ["quantity", "reserved_quantity"]})
    libre = sum(d["quantity"] - d["reserved_quantity"] for d in dispo)
    prend = min(besoin, max(libre, 0))
    print("\n  %-52s sortie %-7.1f demande %-6.1f besoin %-6.1f stock %-8.1f -> transfere %.1f"
          % (noms[pid][:52], dispo_sortie, demande.get(pid, 0.0), besoin, libre, prend))
    if prend > 0:
        lignes.append((pid, noms[pid], prend))
    if prend < besoin:
        decouverts.append((noms[pid], besoin - prend))

# ---------------------------------------------------------------- 3. le transfert
picking_id = None
if lignes and APPLY:
    moves = [(0, 0, {
        "name": nom,
        "product_id": pid,
        "product_uom_qty": qte,
        "location_id": SCOPE["stock_loc"],
        "location_dest_id": SCOPE["out_loc"],
    }) for pid, nom, qte in lignes]
    picking_id = call("stock.picking", "create", [{
        "picking_type_id": SCOPE["internal_type"],
        "location_id": SCOPE["stock_loc"],
        "location_dest_id": SCOPE["out_loc"],
        "origin": "Regularisation TT/Sortie (garde-fou)",
        "move_ids": moves,
    }])
    safe("stock.picking", "action_confirm", [[picking_id]])
    safe("stock.picking", "action_assign", [[picking_id]])
    mids = call("stock.picking", "read", [[picking_id]], {"fields": ["move_ids"]})[0]["move_ids"]
    for m in call("stock.move", "read", [mids], {"fields": ["product_uom_qty"]}):
        call("stock.move", "write", [[m["id"]], {"quantity": m["product_uom_qty"], "picked": True}])
    safe("stock.picking", "button_validate", [[picking_id]])
    nom = call("stock.picking", "read", [[picking_id]], {"fields": ["name", "state"]})[0]
    print("\n  [OK] transfert %s [%s]" % (nom["name"], nom["state"]))

    # La regle de flux de l'entrepot (TT/Sortie -> Customers) enchaine
    # automatiquement une livraison sur tout ce qui entre en TT/Sortie. Sans
    # partenaire ni commande, c'est un fantome — et il RESERVE immediatement le
    # stock qu'on vient de remettre, ce qui laisse les vraies commandes bloquees.
    # On l'annule avant de relancer les reservations.
    fantomes = call("stock.picking", "search_read",
                    [[["origin", "=", nom["name"]], ["state", "not in", ["done", "cancel"]]]],
                    {"fields": ["name", "partner_id"]})
    for f in fantomes:
        if f["partner_id"]:
            print("  [!] %s a un partenaire (%s) — NON annulee, a verifier a la main"
                  % (f["name"], f["partner_id"][1]))
            continue
        safe("stock.picking", "action_cancel", [[f["id"]]])
        print("  [OK] livraison fantome %s annulee" % f["name"])
elif lignes:
    print("\n  [DRY] creerait 1 transfert interne TT/Stock -> TT/Sortie, %d ligne(s)" % len(lignes))

# ------------------------------------------------- 4. relancer les livraisons bloquees
bloques = call("stock.picking", "search_read",
               [[["picking_type_id", "=", SCOPE["out_type"]],
                 ["state", "in", ["waiting", "confirmed"]]]],
               {"fields": ["name", "origin", "partner_id"]})
print("\n" + "=" * 96)
print("Livraisons bloquees : %d" % len(bloques))
for b in bloques:
    if APPLY:
        safe("stock.picking", "action_assign", [[b["id"]]])
        etat = call("stock.picking", "read", [[b["id"]]], {"fields": ["state"]})[0]["state"]
        print("  %-16s %-10s -> %s" % (b["name"], b["origin"], etat))
    else:
        print("  %-16s %-10s (relancerait la reservation)" % (b["name"], b["origin"]))

# ---------------------------------------------------------------------- 5. alerte
if decouverts:
    print("\n" + "!" * 96)
    print("ECART PHYSIQUE REEL — TT/Stock ne couvre pas ces manques, un comptage est requis :")
    for nom, qte in decouverts:
        print("   %-52s %.1f unite(s)" % (nom[:52], qte))
