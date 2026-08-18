# -*- coding: utf-8 -*-
"""
Cree (et envoie en Peppol) les avoirs de commission DSD Delhaize.

Gabarit repris de RINV/25-26/0269 :
  - out_refund sur partner 2912 (Delhaize Le Lion S.A), journal INV
  - ligne note   : "NC Teatower - Rebates MM/AAAA"
  - ligne produit: "Commissions DSP (8%) - <mois>" -> compte 614200, TVA 6 %
Base : 8 % du CA HT du mois sur child_of 2912, net des avoirs de reprise du mois
(cf. scripts/_delhaize_rfa_audit.py, methode validee sur 07/2025 -> 03/2026).

Les avoirs sont dates du JOUR (periode TVA courante) : les periodes avril->juin 2026
sont deja declarees a la TVA, on ne les rouvre pas. La periode couverte reste
identifiee par la ligne note + la reference.

    python delhaize_rfa_creer_avoirs.py            -> dry-run
    python delhaize_rfa_creer_avoirs.py --apply    -> creation + post + envoi Peppol
"""
import os
import sys
import xmlrpc.client
from datetime import date

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ["ODOO_PWD"]
DELHAIZE = 2912
JOURNAL = 9        # Customer Invoices
ACC_RFA = 869      # 614200 RFA et publicite
TAX_6 = 8          # TVA 6 %
FOURNISSEUR = "10072605"   # n° fournisseur Teatower chez Delhaize

# periode -> (libelle mois, montant HT = 8 % de la base nette)
AVOIRS = [
    ("04/2026", "avril 2026",   710.21),
    ("05/2026", "mai 2026",     609.37),
    ("06/2026", "juin 2026",   1292.15),
    ("07/2026", "juillet 2026", 956.75),
]

DRY = "--apply" not in sys.argv
TODAY = date.today().isoformat()

c = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common")
uid = c.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")
call = lambda mo, me, a, k=None: m.execute_kw(DB, uid, PWD, mo, me, a, k or {})

print(f"MODE: {'DRY-RUN (rien ecrit)' if DRY else 'APPLY (ecriture reelle)'}  date piece: {TODAY}\n")

# garde-fou : ne pas recreer un avoir de commission deja emis pour la meme periode
deja = call("account.move.line", "search_read",
            [[["account_id", "=", ACC_RFA], ["partner_id", "=", DELHAIZE],
              ["parent_state", "!=", "cancel"]]],
            {"fields": ["move_id", "name", "date"]})
notes = call("account.move.line", "search_read",
             [[["partner_id", "=", DELHAIZE], ["display_type", "=", "line_note"],
               ["name", "ilike", "Rebates"], ["parent_state", "!=", "cancel"]]],
             {"fields": ["name", "move_id"]})
periodes_faites = {n["name"].split("Rebates")[-1].strip() for n in notes}
print(f"periodes deja creditees : {', '.join(sorted(periodes_faites))}\n")

created = []
for periode, mois, montant in AVOIRS:
    if periode in periodes_faites:
        print(f"  SKIP  {periode} - avoir deja existant")
        continue
    vals = {
        "move_type": "out_refund",
        "partner_id": DELHAIZE,
        "journal_id": JOURNAL,
        "invoice_date": TODAY,
        "date": TODAY,
        "ref": f"Rebates {periode} - fournisseur {FOURNISSEUR}",
        "invoice_line_ids": [
            (0, 0, {"display_type": "line_note",
                    "name": f"NC Teatower - Rebates {periode}"}),
            (0, 0, {"name": f"Commissions DSP (8%) - {mois}",
                    "quantity": 1,
                    "price_unit": montant,
                    "account_id": ACC_RFA,
                    "tax_ids": [(6, 0, [TAX_6])]}),
        ],
    }
    if DRY:
        print(f"  DRY   avoir {periode} {mois:14} {montant:8.2f} HT  (TVA 6% -> {montant*1.06:8.2f} TTC)")
        continue
    mid = call("account.move", "create", [vals])
    mv = call("account.move", "read", [[mid]], {"fields": ["name", "amount_untaxed", "amount_total"]})[0]
    print(f"  CREE  {periode} -> id={mid} {montant:8.2f} HT / {mv['amount_total']:8.2f} TTC")
    created.append({"id": mid, "periode": periode})

# ---- POST ----
if created:
    print("\n=== POST ===")
    for cr in created:
        call("account.move", "action_post", [[cr["id"]]])
        mv = call("account.move", "read", [[cr["id"]]],
                  {"fields": ["name", "state", "amount_untaxed", "amount_total"]})[0]
        cr["name"] = mv["name"]
        print(f"  POSTE {mv['name']:20} {cr['periode']}  {mv['amount_untaxed']:8.2f} HT / {mv['amount_total']:8.2f} TTC  ({mv['state']})")

# ---- ENVOI PEPPOL ----
# account.move.action_send_and_print seul ne declenche PAS l'envoi : passer par le wizard.
if created:
    print("\n=== ENVOI PEPPOL ===")
    p = call("res.partner", "read", [[DELHAIZE]], {"fields": ["peppol_verification_state"]})[0]
    if p["peppol_verification_state"] != "valid":
        print(f"  STOP  partner 2912 peppol state={p['peppol_verification_state']} - envoi annule")
    else:
        for cr in created:
            ctx = {"active_model": "account.move", "active_ids": [cr["id"]], "active_id": cr["id"]}
            wiz = call("account.move.send.wizard", "create", [{"move_id": cr["id"]}], {"context": ctx})
            meth = call("account.move.send.wizard", "read", [[wiz]], {"fields": ["sending_methods"]})[0]["sending_methods"]
            if not meth or "peppol" not in meth:
                call("account.move.send.wizard", "write", [[wiz], {"sending_methods": ["peppol"]}])
            call("account.move.send.wizard", "action_send_and_print", [[wiz]], {"context": ctx})
            after = call("account.move", "read", [[cr["id"]]],
                         {"fields": ["peppol_move_state", "peppol_message_uuid"]})[0]
            ok = after.get("peppol_move_state") in ("processing", "done", "to_send")
            print(f"  {'SENT ' if ok else 'WARN '} {cr['name']:20} state={after.get('peppol_move_state')} uuid={after.get('peppol_message_uuid')}")
