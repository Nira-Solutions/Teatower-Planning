# -*- coding: utf-8 -*-
"""
Complements aux fiches Odoo apres l'import Slack #merchandiser du 03/09/2026.

slack_photos_vers_odoo.py pose la note interne, les photos et le tag [VISITE],
mais `issue()` ne garde que la PREMIERE ligne du message. Les relevés
structurés de Gilles (contact, controle marchandise, stock, appareil) et les
observations commerciales sont perdus. Ce script les reporte.

  1. Carrefour Market Remouchamps  -> contact merchandiser Claire + tag [STOCK:]
                                      (releve complet du 03/09)
  2. Pharmacie Haulot-Bauche       -> le magasin REFUSE le reassort (rotation
                                      trop faible d'apres la responsable) :
                                      l'info conditionne la cadence, pas juste
                                      un "passage OK"
  3. Spar Namur                    -> precision terrain : la zone devient
                                      pietonne APRES 13H30 (Gilles, 03/09)

Usage : python scripts/maj_fiches_visites_20260903.py [--apply]
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

# (pid, marqueur d'idempotence, bloc a ajouter, commentaire ecran)
AJOUTS = [
    (5878, "Contact merchandiser: Claire",
     "<p><em>--- Relevé merchandiser du 03/09/2026 (Gilles, source Slack) ---</em></p>"
     "<p>Contact merchandiser: Claire<br>"
     "Contrôle marchandise : non<br>"
     "Stock : oui — thés glacés en réserve<br>"
     "Appareil : non</p>"
     "<p>[STOCK: réserve — thés glacés présents au 03/09/2026]</p>",
     "Remouchamps : contact Claire + relevé structuré + tag [STOCK:]"),

    (3181, "REFUS REASSORT",
     "<p>[REFUS REASSORT 2026-09-03] La responsable ne veut pas de réassort : "
     "rotation très faible. Doypacks changés dans la mesure du stock camionnette. "
     "À arbitrer : cadence à allonger ou passage en suivi téléphonique.</p>",
     "Haulot-Bauche : refus de réassort explicite (rotation faible)"),

    (122958, "après 13h30",
     "<p>Précision terrain (Gilles, 03/09/2026) : « Impossible de se garer. "
     "Zone piétonne après 13h30 ». Le créneau exact est donc <strong>après "
     "13h30</strong> — à confirmer si la restriction vaut tous les jours ou "
     "le jeudi seulement.</p>",
     "Spar Namur : creneau precis 13h30 releve sur le terrain"),
]

for pid, marqueur, bloc, libelle in AJOUTS:
    p = call("res.partner", "read", [[pid]], {"fields": ["display_name", "comment"]})[0]
    cur = p.get("comment") or ""
    plat = re.sub(r"<[^>]+>", " ", cur)
    print("\n#%d %s" % (pid, p["display_name"]))
    print("   %s" % libelle)
    if marqueur in plat:
        print("   [SKIP] deja present")
        continue
    if not APPLY:
        print("   [DRY] ajouterait le bloc")
        continue
    call("res.partner", "write", [[pid], {"comment": cur + bloc}])
    print("   [OK] ecrit")

# ---------------------------------------------------------------------------
# Photo orpheline du 03/09 14:15 (IMG_2703, message sans texte)
# ---------------------------------------------------------------------------
print("\n" + "=" * 92)
print("Photo orpheline Slack du 03/09 14:15 : IMG_2703 poste seul, sans libelle.")
print("  Meme nom et meme taille (2,0 Mo) que la photo du message")
print("  « Intermarché Jambes » de 14:13 -> reenvoi du meme cliche.")
print("  La fiche #3000 porte deja cette photo : rien a rattacher.")
atts = call("ir.attachment", "search_read",
            [[["res_model", "=", "res.partner"], ["res_id", "=", 3000],
              ["name", "like", "visite_2026-09-03"]]],
            {"fields": ["name"]})
print("  pieces jointes du 03/09 sur #3000 : %s" % [a["name"] for a in atts])
