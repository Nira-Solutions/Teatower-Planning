# -*- coding: utf-8 -*-
"""Neutralise 2 fiches GMS en DOUBLON qui polluaient le pool merch ET la bascule televente.

Deux magasins existent chacun sous deux fiches Odoo a la MEME adresse, avec deux
numeros d'affilie consecutifs. La fiche ancienne ne porte plus de commande depuis
l'ete, la recente est suivie normalement -- mais le pool, qui raisonne par pid,
voit l'ancienne comme un magasin jamais visite :

  #5916  Affilie 044470 - AD Jambes (Materne)     Av. Jean Materne 109, 5100 Jambes
         derniere SO 02/03/2026  ->  156 j de retard, 1er du classement OVERDUE
  #113498 Affilie 044471 - Delhaize Materne       Av. du Bourgmestre Jean Materne 109
         derniere SO 30/06/2026, visite le 07/09/2026  -> LA fiche vivante

  #5591  Affilie 043131 - AD Fernelmont           Rue d'Eghezee 16, 5380 Fernelmont
         derniere SO 30/06/2026  ->  50 j de retard
  #2952  AD Delhaize Fernelmont (Fernel-Dis n°43132)  Rue d'Eghezee 16, 5380 Fernelmont
         16 SO, derniere 03/09/2026, Tier A  -> LA fiche vivante

Sans ce tag, `check_couverture_gms.py` les bascule en televente : Vanessa
appellerait deux magasins que Gilles visite deja (cf. memory
feedback_planning_doublons_adresse -- le garde-fou pid rate les doublons).

Le tag [NO-MERCH est REVERSIBLE. Le vrai correctif est une FUSION des fiches
dans Odoo, qui est une operation destructive : elle reste a la main de Nicolas.

Usage : python scripts/_doublons_nomerch_20260916.py [--apply]
"""
import os
import re
import sys
import xmlrpc.client

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ["ODOO_PWD"]
uid = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
_m = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")


def call(mo, me, a, k=None):
    return _m.execute_kw(DB, uid, PWD, mo, me, a, k or {})


APPLY = "--apply" in sys.argv

DOUBLONS = [
    (5916, 113498, "Affilié 044471 - Delhaize Materne",
     "dernière commande 02/03/2026 ; la fiche vivante porte les SO et la visite du 07/09/2026"),
    (5591, 2952, "AD Delhaize Fernelmont (Fernel-Dis SRL n°43132)",
     "dernière commande 30/06/2026 ; la fiche vivante est Tier A, 16 SO, dernière le 03/09/2026"),
]

print("MODE :", "APPLY" if APPLY else "DRY-RUN")
print()
for pid, vivant, nom_vivant, motif in DOUBLONS:
    r = call("res.partner", "read", [[pid]], {"fields": ["name", "display_name", "comment"]})[0]
    nom = r["name"] or r["display_name"]
    txt = re.sub(r"<[^>]+>", " ", str(r["comment"] or ""))
    if "[NO-MERCH" in txt:
        print("=  #%-7s %-44s deja NO-MERCH" % (pid, nom[:44]))
        continue
    tag = ("<p>[NO-MERCH doublon] Doublon d'adresse avec #%d (%s) — %s. "
           "Hors planning merchandiser ET hors bascule télévente : le magasin est "
           "couvert sur l'autre fiche. À fusionner dans Odoo.</p>"
           % (vivant, nom_vivant, motif))
    print("+  #%-7s %-44s -> NO-MERCH, doublon de #%d" % (pid, nom[:44], vivant))
    if APPLY:
        call("res.partner", "write", [[pid], {"comment": (r["comment"] or "") + tag}])

print()
print("APPLIQUE." if APPLY else "DRY-RUN (--apply pour ecrire).")
