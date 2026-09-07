# -*- coding: utf-8 -*-
"""
AD Spa (#7649) conteste le rappel. Verdict de l'audit :

  - INV/2026/03755 (344,06) : le client a raison, paye le 03/09, encaisse le
    04/09 (BSL 20783, virement VIRSPACO citant « INV/2026/03755 »). Lettree le
    07/09. Le rappel est parti avant l'imputation -- plus rien a reclamer.
  - INV/2025/00617 (364,02) + INV/2025/01061 (201,61) = 565,63 : aucune trace
    d'encaissement chez nous (ni communication structuree, ni montant, ni credit
    non affecte sur la centrale). Mais la piste du client tient : la centrale
    Delhaize paie pour ses affilies et nos encaissements centrale sont lettres
    sur le compte de la CENTRALE (#2912) -- une facture d'affilie reglee par la
    centrale reste alors ouverte pour toujours. Et ces deux pieces sont les
    SEULES creances Delhaize anterieures a 2026 encore ouvertes sur les 83
    partenaires du reseau.

On repousse donc la relance le temps d'obtenir les avis de paiement Delhaize de
mai a juillet 2025, et on trace le tout en note INTERNE sur la fiche.
Aucune ecriture comptable : rien n'est passe en perte, la creance reste due.

    python ad_spa_relance_20260907.py        -> DRY-RUN
    python ad_spa_relance_20260907.py apply   -> execution
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


PARTNER = 7649
NOUVELLE_DATE = "2026-10-15"

NOTE = (
    "<p><b>Contestation AD Spa du 07/09/2026 — audit du lettrage</b></p>"
    "<ul>"
    "<li><b>INV/2026/03755 (344,06 €) : le client a raison.</b> Payée le 03/09, "
    "encaissée le 04/09 (BSL 20783, virement VIRSPACO citant « INV/2026/03755 »), "
    "lettrée le 07/09. Le rappel est parti avant l'imputation. Rien à réclamer.</li>"
    "<li><b>INV/2025/00617 (364,02 €) et INV/2025/01061 (201,61 €) = 565,63 € : "
    "aucune trace d'encaissement chez nous.</b> Ni les communications structurées "
    "(+++000/0005/81188+++ et +++000/0014/28122+++), ni les montants 364,02 / "
    "201,61 / 565,63 n'apparaissent dans les relevés ING et Belfius, et la "
    "centrale Delhaize (#2912) ne porte aucun crédit non affecté.</li>"
    "<li><b>Mais la piste du client tient.</b> La centrale règle pour ses "
    "affiliés, et nos encaissements centrale sont lettrés sur le compte de la "
    "CENTRALE : une facture d'affilié payée par la centrale reste ouverte pour "
    "toujours chez nous. Ces deux pièces sont d'ailleurs les <b>seules</b> "
    "créances Delhaize antérieures à 2026 encore ouvertes sur les 83 partenaires "
    "du réseau.</li>"
    "<li><b>À obtenir :</b> les avis de paiement Delhaize (/ADV/) de mai à "
    "juillet 2025 — notamment /ADV/2000043229 (13/06/2025, 3.377,21 €) et "
    "/ADV/2000044634 (20/06/2025, 3.451,42 €). Même blocage que pour les "
    "4.462,53 € d'avis manquants d'août 2026.</li>"
    "</ul>"
    "<p>Relance repoussée au %s le temps d'obtenir les avis. La créance reste "
    "due, rien n'est passé en perte.</p>" % NOUVELLE_DATE
)

APPLY = len(sys.argv) > 1 and sys.argv[1] == "apply"
print("MODE :", "APPLY" if APPLY else "DRY-RUN")

p = call("res.partner", "read", [[PARTNER]],
         {"fields": ["name", "total_due", "total_overdue",
                     "followup_status", "followup_next_action_date"]})[0]
print("\n  %s (#%d)" % (p["name"], PARTNER))
print("  dû %.2f  échu %.2f  statut %s  prochaine relance %s"
      % (p["total_due"], p["total_overdue"], p["followup_status"],
         p["followup_next_action_date"]))
print("\n  ACTION : prochaine relance -> %s + note INTERNE sur la fiche"
      % NOUVELLE_DATE)

if APPLY:
    call("res.partner", "write", [[PARTNER],
                                  {"followup_next_action_date": NOUVELLE_DATE}])
    # subtype note = jamais visible du client (cf. regle maison)
    sub = call("ir.model.data", "check_object_reference", ["mail", "mt_note"])[1]
    call("mail.thread", "message_post",
         [[PARTNER]],
         {"body": NOTE, "subtype_id": sub, "model": "res.partner"}) \
        if False else call("res.partner", "message_post", [[PARTNER]],
                           {"body": NOTE, "subtype_id": sub})
    ap = call("res.partner", "read", [[PARTNER]],
              {"fields": ["followup_next_action_date"]})[0]
    print("  [OK] prochaine relance = %s, note interne postée"
          % ap["followup_next_action_date"])
else:
    print("  (dry-run : relancer avec 'apply')")
