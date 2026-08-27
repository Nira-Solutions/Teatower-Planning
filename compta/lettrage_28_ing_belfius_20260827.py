# -*- coding: utf-8 -*-
"""
Lettrage ING + Belfius du 27/08/2026 -- ENCAISSEMENTS CLIENTS uniquement.

Mecanique standard (cf. memoire reference_lettrage_ing_methode) :
  1. repointer la ligne suspense 499000 du move BSL vers 400000 + partenaire
  2. reconcilier cette ligne avec la/les ligne(s) client de la facture
  3. si ecart <= 5 EUR : write-off OD 657000 / 400000
     si ecart  > 5 EUR : lettrage partiel, le solde reste ouvert et reclamable

    python lettrage_28_ing_belfius_20260827.py          -> DRY-RUN
    python lettrage_28_ing_belfius_20260827.py apply    -> execution
"""
import os
import sys
import xmlrpc.client

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ["ODOO_PWD"]

_c = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common")
UID = _c.authenticate(DB, USER, PWD, {})
_m = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")


def call(model, method, args, kw=None):
    return _m.execute_kw(DB, UID, PWD, model, method, args, kw or {})


def call_void(model, method, args, kw=None):
    """reconcile() et remove_move_reconcile() renvoient None -> Fault de marshalling
    alors que l'operation a reussi cote serveur. On avale ce Fault precis."""
    try:
        return call(model, method, args, kw)
    except xmlrpc.client.Fault as e:
        if "cannot marshal None" in str(e):
            return None
        raise


ACC_400 = 162   # 400000 Customers
ACC_657 = 292   # 657000 write-off charges (ecart negatif)
TOLERANCE = 5.0

# (bsl_id, ligne suspense 499000, [lignes client a lettrer], libelle)
CAS = [
    dict(bsl=20570, susp=205866, montant=402.40, partner=None,
         inv=[("INV/2026/03938", 204300, 402.40)],
         cle="comm. structuree +++000/0044/82612+++",
         note="Brasserie RN -- montant exact."),
    dict(bsl=20571, susp=205868, montant=239.39, partner=None,
         inv=[("INV/2026/03811", 201083, 239.40)],
         cle="comm. structuree +++000/0044/24715+++",
         note="Delhaize Montigny -- ecart 0,01 EUR, write-off."),
    dict(bsl=20572, susp=205870, montant=477.00, partner=None,
         inv=[("INV/2026/03616", 196235, 477.00)],
         cle="IBAN payeur BE76 0682 3660 9295",
         note="Sorescol S.A. -- montant exact."),
    dict(bsl=20587, susp=205900, montant=2302.00, partner=None,
         inv=[("INV/2026/02981", 179805, 924.02),
              ("INV/2026/03313", 188051, 1017.84),
              ("INV/2026/02991", 180423, 436.87)],
         cle="les 3 factures sont citees dans le libelle du virement",
         note="Carrefour Belgium -- 2.378,73 factures contre 2.302,00 verses. "
              "Ecart 76,73 EUR = le document 02070375405 du 17/08 cite en tete du "
              "libelle, absent d'Odoo. > 5 EUR -> lettrage partiel, le solde reste "
              "ouvert sur INV/2026/02991 et reste reclamable."),
]

APPLY = len(sys.argv) > 1 and sys.argv[1] == "apply"
print("MODE :", "APPLY" if APPLY else "DRY-RUN")
print("=" * 88)

for cas in CAS:
    # partenaire = celui de la facture
    inv_line = call("account.move.line", "read", [[cas["inv"][0][1]]],
                    {"fields": ["partner_id", "amount_residual", "move_id"]})[0]
    cas["partner"] = inv_line["partner_id"][0]
    partner_nom = inv_line["partner_id"][1]

    susp = call("account.move.line", "read", [[cas["susp"]]],
                {"fields": ["account_id", "credit", "debit", "reconciled", "partner_id"]})[0]
    total_inv = sum(x[2] for x in cas["inv"])
    ecart = round(cas["montant"] - total_inv, 2)

    print("\nBSL %d  %.2f EUR  ->  %s" % (cas["bsl"], cas["montant"], partner_nom))
    print("   cle    : %s" % cas["cle"])
    for n, lid, res in cas["inv"]:
        print("   facture: %-16s ligne %-8d %9.2f" % (n, lid, res))
    print("   total factures %.2f | verse %.2f | ecart %+.2f" % (total_inv, cas["montant"], ecart))
    print("   suspense ligne %d sur %s (rec=%s)" % (cas["susp"], susp["account_id"][1], susp["reconciled"]))
    if abs(ecart) <= TOLERANCE and ecart != 0:
        print("   -> write-off %.2f EUR sur 657000 (<= %.2f)" % (abs(ecart), TOLERANCE))
    elif abs(ecart) > TOLERANCE:
        print("   -> LETTRAGE PARTIEL, %.2f EUR restent ouverts" % abs(ecart))
    print("   %s" % cas["note"])

    if not APPLY:
        continue
    if susp["reconciled"]:
        print("   [SKIP] deja lettree")
        continue

    # 1. repointer 499000 -> 400000 + partenaire
    call("account.move.line", "write", [[cas["susp"]],
         {"account_id": ACC_400, "partner_id": cas["partner"]}])
    print("   [OK] suspense repointee sur 400000 + partenaire %d" % cas["partner"])

    # 2. lettrage
    ids = [cas["susp"]] + [x[1] for x in cas["inv"]]
    call_void("account.move.line", "reconcile", [ids])
    print("   [OK] reconcile(%s)" % ids)

    # 3. write-off de l'ecart si <= tolerance
    if 0 < abs(ecart) <= TOLERANCE:
        reste = call("account.move.line", "read", [[x[1] for x in cas["inv"]]],
                     {"fields": ["id", "amount_residual", "move_id"]})
        ouvertes = [l for l in reste if abs(l["amount_residual"]) > 0.001]
        if ouvertes:
            jrn = call("account.journal", "search", [[["type", "=", "general"]]], {"limit": 1})[0]
            od = call("account.move", "create", [{
                "journal_id": jrn, "date": "2026-08-27",
                "ref": "Ecart de reglement BSL %d - %s" % (cas["bsl"], partner_nom),
                "line_ids": [
                    (0, 0, {"account_id": ACC_657, "debit": abs(ecart), "credit": 0.0,
                            "partner_id": cas["partner"],
                            "name": "Ecart de reglement %s" % cas["inv"][0][0]}),
                    (0, 0, {"account_id": ACC_400, "debit": 0.0, "credit": abs(ecart),
                            "partner_id": cas["partner"],
                            "name": "Ecart de reglement %s" % cas["inv"][0][0]}),
                ]}])
            call("account.move", "action_post", [[od]])
            od_line = call("account.move.line", "search",
                           [[["move_id", "=", od], ["account_id", "=", ACC_400]]])
            call_void("account.move.line", "reconcile", [od_line + [l["id"] for l in ouvertes]])
            print("   [OK] write-off %.2f EUR poste (OD %d) et lettre" % (abs(ecart), od))

print("\n" + "=" * 88)
if not APPLY:
    print("DRY-RUN termine -- relancer avec 'apply' pour executer.")
else:
    print("CONTROLE FINAL")
    for cas in CAS:
        b = call("account.bank.statement.line", "read", [[cas["bsl"]]],
                 {"fields": ["is_reconciled", "amount"]})[0]
        etats = []
        for n, lid, _ in cas["inv"]:
            mv = call("account.move", "search_read", [[["name", "=", n]]],
                      {"fields": ["name", "amount_residual", "payment_state"]})[0]
            etats.append("%s res=%.2f %s" % (mv["name"], mv["amount_residual"], mv["payment_state"]))
        print("  BSL %d lettree=%s | %s" % (cas["bsl"], b["is_reconciled"], " ; ".join(etats)))
