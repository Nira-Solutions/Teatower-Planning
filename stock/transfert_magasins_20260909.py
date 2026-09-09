# -*- coding: utf-8 -*-
"""
Transfert exceptionnel vers les quatre magasins Teatower — 09/09/2026.

Contenu par magasin, décidé par Nicolas :
    2  COFFRET TT8        (et non 3 : voir plus bas)
   15  MENU-FR-2024
   15  MENU-NL-2024
   15  MENU-EN-2024
   24  A0304 Verre à thé double paroi 300ml

TROIS ARBITRAGES QUI EXPLIQUENT CES LIGNES :

1. « COFFRET-TT8 » et « A304 » n'existent pas sous ces codes. Les références
   réelles sont `COFFRET TT8` (espace, pas tiret) et `A0304`. Résolues sans
   ambiguïté, une seule correspondance chacune.

2. Les coffrets passent de 3 à 2 par magasin. Il y a 29 pièces en stock mais
   21 sont déjà réservées par d'autres commandes : 8 libres pour 12 demandés.
   Nicolas a choisi de rester dans le stock libre plutôt que de mettre une
   commande client en rupture.

3. « 15 menus de chaque » = les menus RÉELLEMENT utilisés, mesurés sur les
   mouvements Odoo : MENU-FR/NL/EN-2024 totalisent 546 mouvements sur 24 mois
   et bougent encore en août 2026. Les treize autres références `MENU*`
   (MENU2xxTT8, MENUxxTT14, MENUTT...) n'ont qu'UN mouvement chacune, daté du
   31/03/2025 — une écriture de migration, aucune sortie réelle. Ce sont des
   références mortes.

Le flux suit le schéma maison, vérifié sur les 12 derniers transferts : on
utilise le type « Transferts internes » DU MAGASIN destinataire, avec
TT/Stock en source. Pas de transit, pas de type Teatower.

Les pickings sont créés puis confirmés et réservés, mais PAS validés : la
marchandise n'a pas encore bougé physiquement.

    python transfert_magasins_20260909.py         -> DRY-RUN
    python transfert_magasins_20260909.py apply    -> execution
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


APPLY = "apply" in [a.lower() for a in sys.argv[1:]]

SRC = 8                       # TT/Stock
MAGASINS = [                  # (nom, picking_type_id, location_dest_id)
    ("Liège",    30, 4524),
    ("Rocourt", 104, 4712),
    ("Waterloo", 44, 4532),
    ("Namur",    56, 4540),
]
LIGNES = [                    # (product_id, code, quantité par magasin)
    (4334, "COFFRET TT8", 2),
    (4793, "MENU-FR-2024", 15),
    (4794, "MENU-NL-2024", 15),
    (4792, "MENU-EN-2024", 15),
    (4049, "A0304", 24),
]
ORIGINE = "Transfert exceptionnel magasins — 09/09/2026"

# --- contrôle de disponibilité avant d'écrire quoi que ce soit
print("=== DISPONIBILITÉ DANS TT/Stock ===")
enfants = call("stock.location", "search", [[("id", "child_of", SRC)]])
bloquant = False
for pid, code, q in LIGNES:
    quants = call("stock.quant", "search_read",
                  [[("product_id", "=", pid), ("location_id", "in", enfants)]],
                  {"fields": ["quantity", "reserved_quantity"]})
    dispo = sum(x["quantity"] - x["reserved_quantity"] for x in quants)
    besoin = q * len(MAGASINS)
    ok = "OK" if dispo >= besoin else "INSUFFISANT"
    if dispo < besoin:
        bloquant = True
    print(f"  {code:<16} besoin {besoin:>4}  libre {dispo:>8g}   {ok}")
if bloquant:
    print("\nSTOP — au moins une référence est insuffisante, rien n'est créé.")
    sys.exit(1)

print("\n=== TRANSFERTS À CRÉER ===")
for nom, ptype, dest in MAGASINS:
    print(f"\n  Magasin {nom}  (type {ptype}, TT/Stock -> location {dest})")
    for pid, code, q in LIGNES:
        print(f"     {q:>3} x {code}")

if not APPLY:
    print("\nDRY-RUN — rien n'a été écrit. Relancer avec 'apply'.")
    sys.exit(0)

crees = []
for nom, ptype, dest in MAGASINS:
    vals = {
        "picking_type_id": ptype,
        "location_id": SRC,
        "location_dest_id": dest,
        "origin": ORIGINE,
        "move_ids_without_package": [
            (0, 0, {"name": code, "product_id": pid, "product_uom_qty": q,
                    "location_id": SRC, "location_dest_id": dest})
            for pid, code, q in LIGNES
        ],
    }
    pk = call("stock.picking", "create", [vals])
    call("stock.picking", "action_confirm", [[pk]])
    try:
        call("stock.picking", "action_assign", [[pk]])
    except xmlrpc.client.Fault as e:
        if "cannot marshal None" not in str(e):
            raise
    info = call("stock.picking", "read", [[pk]], {"fields": ["name", "state"]})[0]
    crees.append((nom, info["name"], info["state"]))
    print(f"  {nom:<10} -> {info['name']}  ({info['state']})")

print("\n=== RÉSULTAT ===")
for nom, ref, etat in crees:
    print(f"  {nom:<10} {ref:<20} {etat}")
print("\nLes transferts sont réservés mais NON validés : à valider quand la "
      "marchandise part physiquement.")
