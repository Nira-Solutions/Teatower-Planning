# -*- coding: utf-8 -*-
"""
RESA1293 (Fortamps, loyer magasin Waterloo, 3.000 EUR du 31/08/2026) : le
fournisseur confirme avoir ete paye. Le paiement existe bien -- BSL 20688 du
31/08, virement ING de 3.000 vers Fortamps BE67 0018 6056 5787 -- mais il a ete
impute DIRECTEMENT EN CHARGE sur 611121 « Loyer magasin et bureau de Liege »
au lieu d'etre lettre contre la facture.

C'est la recidive documentee du doublon de loyers (MISC/25-26/06/0305 du
30/06/2026 avait deja neutralise 7 factures Fortamps pour la meme raison) :
la charge est comptabilisee deux fois, une fois par la facture (611123
Waterloo) et une fois par le virement (611121 Liege), et le compte fournisseur
porte une dette ouverte egale au doublon.

Correctif applique ici -- celui prescrit apres la passe du 28/07/2026 :
repointer la contrepartie du virement de 611121 vers 440000 + Fortamps, puis
la lettrer contre RESA1293. Effet : RESA1293 passe `paid`, le doublon de
3.000 EUR disparait du P&L FY26-27 (611121 Liege allege de 3.000, la charge
reste portee une seule fois par 611123 Waterloo), zero impact tresorerie.

    python lettrage_34_fortamps_resa1293_20260907.py        -> DRY-RUN
    python lettrage_34_fortamps_resa1293_20260907.py apply   -> execution
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


def call_void(model, method, args, kw=None):
    try:
        return call(model, method, args, kw)
    except xmlrpc.client.Fault as e:
        if "cannot marshal None" in str(e):
            return None
        raise


ACC_440 = 192          # 440000 Suppliers
P_FORTAMPS = 120691
BSL = 20688            # virement ING -3.000,00 du 31/08/2026
FACTURE = "RESA1293"

APPLY = len(sys.argv) > 1 and sys.argv[1] == "apply"
print("MODE :", "APPLY" if APPLY else "DRY-RUN")
print("=" * 96)

# --- le virement ---------------------------------------------------------
b = call("account.bank.statement.line", "read", [[BSL]],
         {"fields": ["date", "amount", "payment_ref", "move_id"]})[0]
print("\nBSL %d  %s  %.2f" % (BSL, b["date"], b["amount"]))
print("  %s" % (b["payment_ref"] or "").replace("\n", " ")[:120])
banque = call("account.move.line", "search_read", [[["move_id", "=", b["move_id"][0]]]],
              {"fields": ["id", "account_id", "partner_id", "balance", "reconciled"]})
contrepartie = None
for l in banque:
    print("    ligne %-8d %-40s bal=%9.2f rec=%s"
          % (l["id"], l["account_id"][1][:40], l["balance"], l["reconciled"]))
    if not l["account_id"][1].startswith("55"):
        contrepartie = l

# --- la facture ----------------------------------------------------------
mv = call("account.move", "search_read", [[["name", "=", FACTURE]]],
          {"fields": ["id", "amount_total", "amount_residual", "payment_state"]})[0]
dette = call("account.move.line", "search_read",
             [[["move_id", "=", mv["id"]],
               ["account_id.account_type", "=", "liability_payable"]]],
             {"fields": ["id", "account_id", "balance", "reconciled", "amount_residual"]})[0]
print("\n%s  tot=%.2f  res=%.2f  %s" % (FACTURE, mv["amount_total"],
                                        mv["amount_residual"], mv["payment_state"]))
print("    ligne %-8d %-40s bal=%9.2f rec=%s"
      % (dette["id"], dette["account_id"][1][:40], dette["balance"], dette["reconciled"]))

# --- garde-fous ----------------------------------------------------------
if contrepartie is None:
    sys.exit("  [!] contrepartie du virement introuvable")
if contrepartie["reconciled"]:
    sys.exit("  [SKIP] la contrepartie est deja lettree")
if abs(contrepartie["balance"] + dette["balance"]) > 0.005:
    sys.exit("  [!] les deux montants ne s annulent pas -> arret")

print("\nACTION : ligne %d  %s -> 440000 + Fortamps (#%d), puis reconcile avec %d"
      % (contrepartie["id"], contrepartie["account_id"][1][:34], P_FORTAMPS, dette["id"]))

if APPLY:
    call("account.move.line", "write", [[contrepartie["id"]],
                                        {"account_id": ACC_440, "partner_id": P_FORTAMPS}])
    call_void("account.move.line", "reconcile", [[contrepartie["id"], dette["id"]]])
    ap = call("account.move", "read", [[mv["id"]]],
              {"fields": ["amount_residual", "payment_state"]})[0]
    print("  [OK] %s  res=%.2f  %s" % (FACTURE, ap["amount_residual"], ap["payment_state"]))
else:
    print("  (dry-run : relancer avec 'apply')")
