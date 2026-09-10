# -*- coding: utf-8 -*-
"""
Releve merchandiser Delhaize DEBROUX (#5729, Auderghem) du 10/09/2026.

Meme format que scripts/maj_fiches_visites_20260903.py : le bloc structure
(contact, controle marchandise, stock, appareil) est ajoute dans les notes
internes de la fiche res.partner.

  Personne de contact : Mr Hebert / Mr Cauchies
  Stock               : non   -> pas de reserve, donc PAS de tag [STOCK:]
  Controle            : oui
  Appareil            : non

Usage : python scripts/maj_fiche_delhaize_debroux_20260910.py [--apply]
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
UID = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
_m = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")


def call(model, method, args, kw=None):
    return _m.execute_kw(DB, UID, PWD, model, method, args, kw or {})


APPLY = "--apply" in sys.argv
print("MODE :", "APPLY" if APPLY else "DRY-RUN")
print("=" * 92)

PID = 5729
MARQUEUR = "Mr Hebert"
BLOC = (
    "<p><em>--- Relevé merchandiser — reporté le 10/09/2026 "
    "(dernier passage : 08/09/2026) ---</em></p>"
    "<p>Personne de contact : Mr Hebert / Mr Cauchies<br>"
    "Contrôle marchandise : oui<br>"
    "Stock : non — pas de réserve<br>"
    "Appareil : non</p>"
)

p = call("res.partner", "read", [[PID]], {"fields": ["display_name", "comment"]})[0]
cur = p.get("comment") or ""
plat = re.sub(r"<[^>]+>", " ", cur)

print("\n#%d %s" % (PID, p["display_name"]))
print("   notes actuelles (%d car.) : %s" % (len(cur), plat[-300:].strip() or "(vide)"))

if MARQUEUR in plat:
    print("   [SKIP] releve deja present")
elif not APPLY:
    print("   [DRY] ajouterait :")
    print("   " + re.sub(r"<[^>]+>", " ", BLOC))
else:
    call("res.partner", "write", [[PID], {"comment": cur + BLOC}])
    print("   [OK] ecrit")
