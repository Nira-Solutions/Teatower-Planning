# -*- coding: utf-8 -*-
"""
LETTRAGE FORCE CARREFOUR - FIFO - 21/08/2026

Demande Nicolas : "Carrefour il faut vraiment que tu fasses du lettrage de force pcq ca
indique qu'il y a des impayes et le montant est gros dans la balance agee."

CONTEXTE (audit du 21/08, cf carrefour_audit*_20260821.py) :
  - 71 pieces ouvertes sur Carrefour Belgium (#6596 + enfants) = 28.744,02 EUR
  - 2 virements recus non lettres = 6.258,81 EUR (BSL 20156 du 03/08, BSL 20425 du 17/08)
  - Subset-sum EXHAUSTIF (DP en centimes, toutes tailles) :
        4.862,06 -> plus de 10.000.000 de sous-ensembles exacts
        1.396,75 -> 202.295 sous-ensembles exacts
    => aucune affectation deductible. Carrefour n'envoie pas d'avis de paiement.

DECISION : imputation FIFO (la plus ancienne facture d'abord), qui est la pratique standard
pour une centrale sans avis de paiement. Le solde net du compte client est IDENTIQUE quelle
que soit l'affectation ; seule change la repartition par tranche d'anciennete - ce qui est
precisement l'objet de la demande.

ATTENTION - ce que ce script NE fait PAS disparaitre :
  6.258,81 recu contre 28.744,02 ouvert => il restera 22.485,21 EUR REELLEMENT impayes.
  Ce n'est pas un artefact de lettrage (cf project_edi_carrefour_rejets : les factures
  rejetees en EDI n'entrent jamais dans le circuit de paiement de Carrefour).

Usage : python lettrage_24_carrefour_fifo_20260821.py            (DRY-RUN)
        python lettrage_24_carrefour_fifo_20260821.py --apply
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

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m_obj = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


def call(model, method, args, kw=None):
    return m_obj.execute_kw(DB, uid, PWD, model, method, args, kw or {})


ACC_499000 = 221
ACC_400000 = 162
CRF = 6596          # Carrefour Belgium (groupe integre)
BSL_IDS = [20156, 20425]

DRY = "--apply" not in sys.argv


def call_reconcile_safe(line_ids):
    try:
        return True, call("account.move.line", "reconcile", [line_ids])
    except xmlrpc.client.Fault as f:
        low = str(f.faultString).lower()
        if "cannot marshal" in low or "marshaling" in low or "nonetype" in low:
            return True, "marshalling_false_fault_ignored"
        return False, str(f.faultString)


def get_bsl(bsl_id):
    bsl = call("account.bank.statement.line", "read", [[bsl_id]],
               {"fields": ["move_id", "is_reconciled", "amount", "payment_ref"]})[0]
    mv = call("account.move", "read", [[bsl["move_id"][0]]], {"fields": ["state", "name", "line_ids"]})[0]
    bsl["_state"], bsl["_name"], bsl["_lines"] = mv["state"], mv["name"], mv["line_ids"]
    return bsl


def suspense_line(line_ids):
    for ln in call("account.move.line", "read", [line_ids],
                   {"fields": ["id", "account_id", "debit", "credit", "amount_residual"]}):
        if (ln["account_id"] or [None])[0] == ACC_499000:
            return ln
    return None


print("MODE:", "DRY-RUN (rien ecrit)" if DRY else "APPLY (ecriture reelle)")

# ---------------------------------------------------------------------------
# 1) les lignes bancaires
# ---------------------------------------------------------------------------
total_paye = 0.0
bsl_susp = []
for bid in BSL_IDS:
    b = get_bsl(bid)
    if b["is_reconciled"]:
        raise SystemExit(f"BSL {bid} deja lettree -- ABANDON (relire l'etat avant de rejouer)")
    if b["_state"] != "posted":
        raise SystemExit(f"BSL {bid} state={b['_state']} -- ABANDON")
    s = suspense_line(b["_lines"])
    if not s:
        raise SystemExit(f"BSL {bid} : pas de ligne 499000 -- ABANDON")
    print(f"  BSL {bid} ({b['_name']}) {b['amount']:>10,.2f}  suspense aml={s['id']} residual={s['amount_residual']:.2f}")
    total_paye += b["amount"]
    bsl_susp.append((bid, s))
print(f"  TOTAL a imputer : {total_paye:,.2f}\n")

# ---------------------------------------------------------------------------
# 2) les factures ouvertes, FIFO
# ---------------------------------------------------------------------------
open_lines = call("account.move.line", "search_read",
                  [[["account_id", "=", ACC_400000], ["partner_id", "child_of", CRF],
                    ["reconciled", "=", False], ["parent_state", "=", "posted"],
                    ["amount_residual", ">", 0]]],
                  {"fields": ["id", "move_name", "date", "amount_residual", "partner_id"],
                   "order": "date asc, id asc"})
print(f"  {len(open_lines)} lignes debitrices ouvertes, "
      f"total {sum(l['amount_residual'] for l in open_lines):,.2f}")

# les avoirs / trop-percus encore ouverts sur le groupe integre s'imputent aussi
open_credits = call("account.move.line", "search_read",
                    [[["account_id", "=", ACC_400000], ["partner_id", "child_of", CRF],
                      ["reconciled", "=", False], ["parent_state", "=", "posted"],
                      ["amount_residual", "<", 0]]],
                    {"fields": ["id", "move_name", "date", "amount_residual"], "order": "date asc"})
if open_credits:
    print(f"  + {len(open_credits)} credit(s) ouvert(s) a imputer :")
    for c in open_credits:
        print(f"      {c['move_name']:<20} {c['date']} {c['amount_residual']:>10,.2f}")
    total_paye += -sum(c["amount_residual"] for c in open_credits)
    print(f"  TOTAL a imputer (virements + avoirs) : {total_paye:,.2f}")

partners = {l["partner_id"][0] for l in open_lines}
if len(partners) > 1:
    print(f"  NOTE : {len(partners)} fiches partenaires concernees dans le groupe integre")

selected, cum = [], 0.0
for l in open_lines:
    if cum >= total_paye - 0.005:
        break
    selected.append(l)
    cum += l["amount_residual"]

print(f"\n  --- FIFO : {len(selected)} pieces retenues, cumul {cum:,.2f} ---")
run = 0.0
for l in selected:
    run += l["amount_residual"]
    solde = "SOLDEE" if run <= total_paye + 0.005 else f"PARTIELLE (reste {run - total_paye:,.2f})"
    print(f"    {l['move_name']:<20} {l['date']} {l['amount_residual']:>10,.2f}  cumul {run:>10,.2f}  {solde}")

reste = round(sum(l["amount_residual"] for l in open_lines) - total_paye, 2)
print(f"\n  Apres imputation : {reste:,.2f} EUR resteront ouverts sur Carrefour "
      f"(impaye REEL, pas un artefact de lettrage)")

# ---------------------------------------------------------------------------
# 3) execution
# ---------------------------------------------------------------------------
bank_susp_ids = [s["id"] for _, s in bsl_susp]
susp_ids = bank_susp_ids + [c["id"] for c in open_credits]
inv_ids = [l["id"] for l in selected]

if DRY:
    print(f"\n  DRY   write({bank_susp_ids}, account_id={ACC_400000}, partner_id={CRF})")
    print(f"  DRY   reconcile({susp_ids} + {len(inv_ids)} lignes de facture)")
    raise SystemExit(0)

call("account.move.line", "write", [bank_susp_ids, {"account_id": ACC_400000, "partner_id": CRF}])
print(f"\n  lignes suspense {bank_susp_ids} repointees -> 400000 / partner {CRF}")

ok, res = call_reconcile_safe(susp_ids + inv_ids)
if not ok:
    raise SystemExit(f"  ERREUR reconcile() : {res}")
print(f"  reconcile({len(susp_ids + inv_ids)} lignes) -> OK ({res})")

# ---------------------------------------------------------------------------
# 4) verification
# ---------------------------------------------------------------------------
print("\n  --- VERIF ---")
for bid in BSL_IDS:
    b = get_bsl(bid)
    print(f"   BSL {bid} ({b['_name']}) is_reconciled={b['is_reconciled']}")

after = call("account.move.line", "search_read",
             [[["account_id", "=", ACC_400000], ["partner_id", "child_of", CRF],
               ["reconciled", "=", False], ["parent_state", "=", "posted"],
               ["amount_residual", ">", 0]]],
             {"fields": ["move_name", "date", "amount_residual"], "order": "date asc"})
print(f"   Lignes debitrices encore ouvertes : {len(after)} | "
      f"total {sum(l['amount_residual'] for l in after):,.2f}")
if after:
    print(f"   Plus ancienne restante : {after[0]['move_name']} du {after[0]['date']} "
          f"({after[0]['amount_residual']:,.2f})")
