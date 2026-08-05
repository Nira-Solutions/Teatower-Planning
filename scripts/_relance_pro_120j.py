"""
Renvoie le template Odoo #35 "Dernier rappel" aux clients PRO echus > 120 jours.

Mecanique : wizard natif account_followup.manual_reminder (celui du bouton "Envoyer"
de l'ecran Relances), template force sur #35, join_invoices=True pour que les PDF
de factures soient bien joints -- le texte du template dit "la facture en piece jointe".

DRY-RUN par defaut : cree le wizard, affiche destinataire + sujet + corps rendu,
et NE DECLENCHE AUCUN ENVOI. Le wizard est transient, rien n'est ecrit durablement.
    python _relance120_send.py            -> dry-run
    python _relance120_send.py apply      -> envoi reel
    python _relance120_send.py apply 3236 -> envoi reel limite a un partenaire
"""
import os
import sys
import re
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ["ODOO_PWD"]
TEMPLATE_ID = 35  # "Dernier rappel"

c = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common")
uid = c.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")
call = lambda mo, me, a, k=None: m.execute_kw(DB, uid, PWD, mo, me, a, k or {})

# Clients PRO echus > 120j disposant d'une adresse mail (envoi du 05/08/2026).
# Exclus volontairement du perimetre, apres controle piece par piece :
#   - procedure collective en cours (ne pas relancer, declarer la creance) ;
#   - societe liee / intragroupe ;
#   - soldes couverts au centime pres par des avoirs non lettres -> lettrer ;
#   - comptes a qualifier (fournisseur ET client, flux de compensation) ;
#   - clients sans adresse mail -> relance telephonique ;
#   - B2C et micro-soldes <= 5 EUR (regle write-off).
TARGETS = [2926, 3236, 6596, 3015, 7879, 7649, 3163, 2966, 2907, 119814,
           3043, 121260, 2830, 3095, 7825, 8558, 116005, 9836]

APPLY = len(sys.argv) > 1 and sys.argv[1].lower() == "apply"
ONLY = int(sys.argv[2]) if len(sys.argv) > 2 else None
if ONLY:
    TARGETS = [ONLY]

strip = lambda h: re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", h or "")).strip()

print(f"UID={uid} | MODE={'APPLY (ENVOI REEL)' if APPLY else 'DRY-RUN'} | "
      f"{len(TARGETS)} destinataires\n")

parts = {p["id"]: p for p in call("res.partner", "read",
         [TARGETS, ["name", "email", "total_due", "total_overdue",
                    "followup_line_id", "followup_status"]])}

# controle : doublons d'adresse (Distrimarks / Noe Nature = meme groupe)
seen = {}
for pid, p in parts.items():
    seen.setdefault((p["email"] or "").lower(), []).append(p["name"])
for mail, names in seen.items():
    if len(names) > 1:
        print(f"!! MEME ADRESSE {mail} -> {names} (2 mails au meme destinataire)\n")

sent, failed = [], []
for pid in TARGETS:
    p = parts[pid]
    if not p["email"]:
        print(f"  #{pid} {p['name'][:40]} -> SANS EMAIL, ignore")
        continue
    ctx = {"active_model": "res.partner", "active_ids": [pid], "active_id": pid}
    try:
        wiz_vals = {
            "partner_id": pid,
            "template_id": TEMPLATE_ID,
            "email": True,
            "join_invoices": True,
            "print": False,
            "sms": False,
            "snailmail": False,
        }
        wiz_id = call("account_followup.manual_reminder", "create", [wiz_vals],
                      {"context": ctx})
        # forcer le rendu du template choisi
        call("account_followup.manual_reminder", "write",
             [[wiz_id], {"template_id": TEMPLATE_ID}], {"context": ctx})
        try:
            call("account_followup.manual_reminder", "_compute_template_values",
                 [[wiz_id]], {"context": ctx})
        except Exception:
            pass
        w = call("account_followup.manual_reminder", "read",
                 [[wiz_id], ["partner_id", "subject", "body", "email", "join_invoices",
                             "template_id", "attachment_ids"]], {"context": ctx})[0]

        print(f"  #{pid:>7} | {p['name'][:38]:<38} | -> {p['email']}")
        print(f"            du={p['total_due']:.2f} overdue={p['total_overdue']:.2f} "
              f"| niveau={p['followup_line_id']}")
        print(f"            sujet : {w['subject']}")
        print(f"            corps : {strip(w['body'])[:220]}")
        print(f"            join_invoices={w['join_invoices']} pj={w['attachment_ids']}")

        if APPLY:
            call("account_followup.manual_reminder", "process_followup",
                 [[wiz_id]], {"context": ctx})
            print("            -> ENVOYE")
            sent.append((pid, p["name"], p["email"]))
        print()
    except Exception as e:
        print(f"  #{pid} {p['name'][:40]} -> ERREUR : {e}\n")
        failed.append((pid, p["name"], str(e)[:200]))

print(f"\n=== BILAN === envoyes={len(sent)} | erreurs={len(failed)}")
for f in failed:
    print("  KO", f)
if not APPLY:
    print(">>> DRY-RUN : aucun mail parti. Relancer avec 'apply'.")
