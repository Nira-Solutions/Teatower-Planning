# -*- coding: utf-8 -*-
"""Tags [VISITE] depuis Slack #merchandiser — tournee Liege du 11/09 + Wepion 16/09.

Les passages des 07, 08, 14 et 15/09 sont deja traces (scripts precedents ou
picking/SO). Restaient sans aucune trace Odoo :
  - la tournee Liege du VENDREDI 11/09 : 6 magasins « pas besoin de remplir ».
    Le pool du 16/09 les sortait a 13-82 jours de retard alors qu'ils ont ete
    vus il y a 5 jours -- Delhaize Fragnee affichait 82j et arrivait 3e du
    classement OVERDUE.
  - Hyper Wepion le 16/09 (responsable absent, rayon encore rempli).

Le pid tague est celui que `build_planning_pool.py` liste (partner de livraison
quand le picking porte l'enfant), sinon le tag ne remonte pas dans le pool.

Usage : python scripts/slack_visites_vers_odoo_20260916.py [--apply]
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

VISITES = [
    # --- tournee Liege du vendredi 11/09/2026 (Gilles) ---
    (5580,   "2026-09-11", "Delhaize Fragnee",          "pas besoin de remplir (Gilles)"),
    (5439,   "2026-09-11", "Delhaize Longdoz",          "pas besoin de remplir (Gilles)"),
    (5653,   "2026-09-11", "Delhaize Saint-Lambert",    "pas besoin de remplir (Gilles)"),
    (125096, "2026-09-11", "Hyper Carrefour Herstal",   "pas besoin de remplir (Gilles)"),
    (8169,   "2026-09-11", "Delhaize Bois-de-Breux",    "pas besoin de remplir (Gilles)"),
    (119815, "2026-09-11", "Delhaize Barchon",          "pas besoin de remplir (Gilles)"),
    # --- mercredi 16/09/2026 ---
    (6597,   "2026-09-16", "Hyper Carrefour Wepion",
     "responsable absent, aucune commande passee, rayon encore bien rempli (Gilles)"),
]

TAG_RE = re.compile(r"\[VISITE (\d{4}-\d{2}-\d{2})", re.IGNORECASE)
print("MODE :", "APPLY" if APPLY else "DRY-RUN")
print()

for pid, d, libelle, issue in VISITES:
    r = call("res.partner", "read", [[pid]], {"fields": ["name", "display_name", "comment"]})[0]
    nom = r["name"] or r["display_name"] or "?"
    txt = re.sub(r"<[^>]+>", " ", str(r["comment"] or ""))
    if d in TAG_RE.findall(txt):
        print("=  #%-7s %-42s [VISITE %s] deja pose" % (pid, nom[:42], d))
        continue
    tag = ("<p>[VISITE %s — sans réassort] %s — %s (source Slack #merchandiser)</p>"
           % (d, libelle, issue))
    print("+  #%-7s %-42s [VISITE %s]  %s" % (pid, nom[:42], d, issue[:44]))
    if APPLY:
        call("res.partner", "write", [[pid], {"comment": (r["comment"] or "") + tag}])

print()
print("APPLIQUE." if APPLY else "DRY-RUN (--apply pour ecrire).")
