# -*- coding: utf-8 -*-
"""
CORRECTION DU LETTRAGE CROISE COURCELLES <-> SPAR MOMIGNIES  (10/08/2026)

Chaine reconstituee integralement (prealable exige par la regle "ne jamais de-lettrer sans
avoir remonte toute la chaine") :

  09/07  BSL 19661 / BNK1/26-27/0146 : COURSES L SRL (Carrefour Market Courcelles) verse
         688,87 -- comm ***000/0040/27823*** -> lettre CORRECTEMENT sur INV/2026/03057
         (Courcelles, 688,89) avec write-off 0,02 (MISC/26-27/07/0122).  OK.

  20/07  BNK1/26-27/0301 : COURSES L SRL verse UNE SECONDE FOIS 688,89 -- meme communication
         ***000/0040/27823***, donc toujours INV/2026/03057, deja soldee.
         -> a ete lettre A TORT sur INV/2026/03056 (SPAR MOMIGNIES, 688,89), qui porte la
         communication voisine ***000/0040/27924***.  ERREUR.

  28/07  BSL 20026 : MOMIDISTRI SA (Spar Momignies) verse 688,87 -- comm ***000/0040/27924***
         = sa propre facture INV/2026/03056, mais celle-ci apparait deja payee.
         -> repointe en credit ouvert sur le compte client par lettrage_18 (10/08).

Etat reel : c'est COURCELLES qui a paye deux fois, pas Momignies. Momignies a paye une fois,
correctement, et sa facture a ete captee par le versement de Courcelles.

CORRECTION APPLIQUEE ICI :
  1. de-lettrage de BNK1/26-27/0301 <-> INV/2026/03056
  2. repointage du partenaire de cette ligne bancaire vers Carrefour Market Courcelles
     (#124365) : le double paiement reste en credit ouvert sur SON compte
  3. lettrage de BSL 20026 (688,87, Momidistri) sur INV/2026/03056 (688,89)
     -> ecart -0,02 <= 5,00 -> write-off 657100

Aucune ecriture de resultat hors le write-off d'ecart de reglement (seule ecriture autorisee
sans validation prealable, regle validee les 26 et 29/07/2026).

Usage : python lettrage_19_croise_momignies_20260810.py            (DRY-RUN)
        python lettrage_19_croise_momignies_20260810.py --apply
"""

import os
import sys
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ.get("ODOO_PWD")
if not PWD:
    raise SystemExit("Definir ODOO_PWD avant d'executer.")

uid = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
m_obj = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


def call(model, method, args, kw=None):
    return m_obj.execute_kw(DB, uid, PWD, model, method, args, kw or {})


ACC_400000 = 162
ACC_657100 = 293
JOURNAL_MISC = 11
TODAY = "2026-08-10"

BANK_MOVE_WRONG = "BNK1/26-27/0301"      # versement Courcelles du 20/07 mal lettre
INV_MOMIGNIES = "INV/2026/03056"         # facture Spar Momignies 688,89
PARTNER_COURCELLES = 124365              # Carrefour market Courcelles
BSL_MOMIDISTRI = 20026                   # versement reel Momidistri 688,87 (repointe le 10/08)

DRY = "--apply" not in sys.argv


def move_lines_on(move_name, acc):
    mv = call("account.move", "search_read", [[["name", "=", move_name]]], {"fields": ["id"]})
    if not mv:
        raise SystemExit(f"{move_name} introuvable")
    return call("account.move.line", "search_read",
                [[["move_id", "=", mv[0]["id"]], ["account_id", "=", acc]]],
                {"fields": ["id", "partner_id", "debit", "credit", "amount_residual",
                            "reconciled", "matched_credit_ids", "matched_debit_ids"]})


def call_safe(model, method, args):
    """reconcile() / remove_move_reconcile() renvoient None -> Fault de marshalling XML-RPC
    alors que l'operation a bien eu lieu cote serveur."""
    try:
        return True, call(model, method, args)
    except xmlrpc.client.Fault as f:
        low = str(f.faultString).lower()
        if "cannot marshal" in low or "marshaling" in low or "nonetype" in low:
            return True, "marshalling_false_fault_ignored"
        return False, str(f.faultString)


def call_reconcile_safe(line_ids):
    return call_safe("account.move.line", "reconcile", [line_ids])


print("MODE:", "DRY-RUN (rien ecrit)" if DRY else "APPLY (ecriture reelle)")

# --- etat initial -----------------------------------------------------------
wrong = move_lines_on(BANK_MOVE_WRONG, ACC_400000)
if len(wrong) != 1:
    raise SystemExit(f"attendu 1 ligne 400000 sur {BANK_MOVE_WRONG}, trouve {len(wrong)}")
wrong = wrong[0]
inv = call("account.move", "search_read", [[["name", "=", INV_MOMIGNIES]]],
           {"fields": ["id", "partner_id", "amount_total", "amount_residual", "payment_state"]})[0]
inv_line = move_lines_on(INV_MOMIGNIES, ACC_400000)[0]
bsl = call("account.bank.statement.line", "read", [[BSL_MOMIDISTRI]],
           {"fields": ["amount", "move_id", "is_reconciled"]})[0]
bsl_lines = call("account.move.line", "search_read",
                 [[["move_id", "=", bsl["move_id"][0]], ["account_id", "=", ACC_400000]]],
                 {"fields": ["id", "partner_id", "amount_residual", "reconciled"]})
if len(bsl_lines) != 1:
    raise SystemExit(f"attendu 1 ligne 400000 sur le BSL {BSL_MOMIDISTRI}, trouve {len(bsl_lines)}")
bsl_line = bsl_lines[0]

print(f"\nETAT INITIAL")
print(f"  {BANK_MOVE_WRONG} ligne {wrong['id']} partner={wrong['partner_id']} "
      f"credit={wrong['credit']} residual={wrong['amount_residual']} reconciled={wrong['reconciled']}")
print(f"  {INV_MOMIGNIES} total={inv['amount_total']} residual={inv['amount_residual']} "
      f"state={inv['payment_state']} (ligne {inv_line['id']})")
print(f"  BSL {BSL_MOMIDISTRI} amount={bsl['amount']} ligne={bsl_line['id']} "
      f"partner={bsl_line['partner_id']} residual={bsl_line['amount_residual']}")

ecart = round(bsl["amount"] - inv["amount_total"], 2)
print(f"\n  ecart cible apres correction = {ecart:+.2f} (write-off 657100 si <= 5,00)")

if DRY:
    print(f"\n  DRY  1. remove_move_reconcile([{wrong['id']}])")
    print(f"  DRY  2. write partner_id={PARTNER_COURCELLES} sur ligne {wrong['id']}")
    print(f"  DRY  3. reconcile([{bsl_line['id']}, {inv_line['id']}]) + write-off {abs(ecart):.2f}")
    raise SystemExit(0)

# --- 1. de-lettrage (idempotent) --------------------------------------------
if wrong["reconciled"] or abs(wrong["amount_residual"]) < 0.005:
    ok0, res0 = call_safe("account.move.line", "remove_move_reconcile", [[wrong["id"]]])
    if not ok0:
        raise SystemExit(f"remove_move_reconcile echoue: {res0}")
else:
    print("1. ligne deja de-lettree -- etape sautee")
after = call("account.move.line", "read", [[wrong["id"]]],
             {"fields": ["amount_residual", "reconciled"]})[0]
inv_after = call("account.move", "read", [[inv["id"]]],
                 {"fields": ["amount_residual", "payment_state"]})[0]
print(f"\n1. de-lettrage OK -- ligne {wrong['id']} residual={after['amount_residual']} "
      f"reconciled={after['reconciled']} | {INV_MOMIGNIES} residual={inv_after['amount_residual']} "
      f"state={inv_after['payment_state']}")

# --- 2. repointage du double paiement sur Courcelles ------------------------
call("account.move.line", "write", [[wrong["id"]], {"partner_id": PARTNER_COURCELLES}])
chk = call("account.move.line", "read", [[wrong["id"]]], {"fields": ["partner_id", "amount_residual"]})[0]
print(f"2. repointage OK -- ligne {wrong['id']} partner={chk['partner_id']} "
      f"residual={chk['amount_residual']} (credit ouvert Courcelles)")

# --- 3. lettrage du vrai versement Momidistri -------------------------------
inv_line = move_lines_on(INV_MOMIGNIES, ACC_400000)[0]
ok, res = call_reconcile_safe([bsl_line["id"], inv_line["id"]])
if not ok:
    raise SystemExit(f"reconcile echoue: {res}")
print(f"3. reconcile([{bsl_line['id']}, {inv_line['id']}]) -> OK ({res})")

if abs(ecart) >= 0.005:
    vals = {
        "move_type": "entry", "journal_id": JOURNAL_MISC, "date": TODAY,
        "ref": f"Write-off ecart reglement - correction lettrage croise {INV_MOMIGNIES} (Spar Momignies)",
        "line_ids": [
            (0, 0, {"account_id": ACC_657100, "partner_id": inv["partner_id"][0],
                    "debit": abs(ecart), "credit": 0.0, "name": f"Ecart reglement {INV_MOMIGNIES}"}),
            (0, 0, {"account_id": ACC_400000, "partner_id": inv["partner_id"][0],
                    "debit": 0.0, "credit": abs(ecart), "name": f"Ecart reglement {INV_MOMIGNIES}"}),
        ],
    }
    wo_id = call("account.move", "create", [vals])
    call("account.move", "action_post", [[wo_id]])
    wo = call("account.move", "read", [[wo_id]], {"fields": ["name", "line_ids"]})[0]
    wo_target = [l for l in call("account.move.line", "read", [wo["line_ids"]],
                                 {"fields": ["id", "account_id"]})
                 if l["account_id"][0] == ACC_400000]
    still_open = call("account.move.line", "search_read",
                      [[["id", "in", [bsl_line["id"], inv_line["id"]]], ["reconciled", "=", False]]],
                      {"fields": ["id"]})
    if wo_target and still_open:
        ok2, res2 = call_reconcile_safe([wo_target[0]["id"]] + [r["id"] for r in still_open])
        print(f"   write-off {wo['name']} ({abs(ecart):.2f} en 657100) reconcile -> {ok2} {res2}")
    else:
        print(f"   write-off {wo['name']} cree ({abs(ecart):.2f} en 657100)")

# --- verification finale ----------------------------------------------------
print("\nVERIFICATION")
inv_f = call("account.move", "read", [[inv["id"]]], {"fields": ["amount_residual", "payment_state"]})[0]
bsl_f = call("account.bank.statement.line", "read", [[BSL_MOMIDISTRI]], {"fields": ["is_reconciled"]})[0]
w_f = call("account.move.line", "read", [[wrong["id"]]],
           {"fields": ["partner_id", "amount_residual", "reconciled"]})[0]
print(f"  {INV_MOMIGNIES} residual={inv_f['amount_residual']} state={inv_f['payment_state']}")
print(f"  BSL {BSL_MOMIDISTRI} is_reconciled={bsl_f['is_reconciled']}")
print(f"  double paiement Courcelles : ligne {wrong['id']} partner={w_f['partner_id']} "
      f"residual={w_f['amount_residual']} reconciled={w_f['reconciled']}")
