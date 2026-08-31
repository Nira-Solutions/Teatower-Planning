# -*- coding: utf-8 -*-
"""
Lettrage ING + Belfius du 31/08/2026.

Perimetre : les 6 lignes bancaires non lettrees pour lesquelles la piece est
certaine. Le reste (Delhaize, ITM 637,24 / 160,61, prets actionnaires,
Amazon, charges de credit Belfius) reste bloque -- cf. rapport.

Mecanique standard (cf. memoire reference_lettrage_ing_methode) :
  1. repointer la ligne suspense 499000 du move BSL vers le bon compte
  2. reconcilier avec la/les ligne(s) de la piece
  3. ecart <= 5 EUR -> write-off ; > 5 EUR -> lettrage partiel

    python lettrage_29_ing_belfius_20260831.py          -> DRY-RUN
    python lettrage_29_ing_belfius_20260831.py apply    -> execution
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
    """reconcile() renvoie None -> Fault de marshalling cote client alors que
    l operation a reussi cote serveur. On avale ce Fault precis."""
    try:
        return call(model, method, args, kw)
    except xmlrpc.client.Fault as e:
        if "cannot marshal None" in str(e):
            return None
        raise


ACC_400 = 162     # 400000 Customers
ACC_657 = 292     # 657000 Financial Discounts Allowed
ACC_580000 = 233  # 580000 Internal Transfers of Funds (lettrable)
ACC_580003 = 821  # 580003 Paiement Sodexo-Edenred (transit titres-repas)
ACC_757100 = 347  # 757100 Positive Payment Differences
JRN_MISC = 11
DATE_OD = "2026-08-31"
TOLERANCE = 5.0

# --- A. encaissements clients : repoint 400000 + reconcile facture -----------
CLIENTS = [
    dict(bsl=20602, susp=206163, montant=378.00,
         inv=[("INV/2026/03921", 203634, 378.00)],
         cle="comm. structuree ***000/0044/70787***",
         note="Le Pressoir Ardennais SRL -- montant exact."),
    dict(bsl=20658, susp=206733, montant=222.72,
         inv=[("INV/2026/03896", 203077, 222.72)],
         cle="comm. structuree ***000/0044/60582***",
         note="SAVEDIS / Spar Barvaux -- montant exact."),
    dict(bsl=20623, susp=206421, montant=198.11,
         inv=[("INV/2026/03647", 196673, 198.10)],
         cle="IBAN payeur BE75 3701 0623 0851 (ITM Alimentaire) + FIFO + cadence J+31",
         note="Centrale Intermarche. ITM paie facture par facture avec un arrondi "
              "au centime : precedents BSL 20070 (675,02 -> INV/2026/03297 675,00, "
              "write-off +0,02 le 04/08) et BSL 20185 (123,10 -> INV/2026/03420). "
              "Deux factures ouvertes a 198,10 (03647 du 27/07 et 03923 du 19/08) : "
              "on retient la plus ancienne, FIFO, et la cadence de paiement observee "
              "est J+30/31 (03297 30/06->30/07, 03420 08/07->06/08), soit 03647. "
              "Ecart +0,01 -> write-off 757100."),
]

# --- B. repointages simples (pas de lettrage) -------------------------------
REPOINTS = [
    dict(bsl=20617, susp=206193, montant=9.81, account=ACC_580003,
         note="EDENRED BELGIUM -- titres-repas boutiques, compte de transit 580003."),
    dict(bsl=20653, susp=206609, montant=31.95, account=ACC_580003,
         note="EDENRED BELGIUM -- titres-repas boutiques, compte de transit 580003."),
]

# --- C. virement interne ING -> Belfius -------------------------------------
INTERNES = [
    dict(bsl=20568, susp=205862, montant=-15000.00,
         contre=205683, contre_bsl=20561,
         note="Virement interne ING (BE30 3631 6408 2311) -> Belfius "
              "(BE86 0689 5807 1350) du 25/08, encaisse le 26/08. La contrepartie "
              "Belfius BSL 20561 est deja sur 580000 (ligne 205683, credit 15.000, "
              "non lettree) : on miroite le cote ING sur 580000 et on lettre les deux."),
]

APPLY = len(sys.argv) > 1 and sys.argv[1] == "apply"
print("MODE :", "APPLY" if APPLY else "DRY-RUN")
print("=" * 92)

# ---------------------------------------------------------------- A. clients
print("\n### A. ENCAISSEMENTS CLIENTS ###")
for cas in CLIENTS:
    inv_line = call("account.move.line", "read", [[cas["inv"][0][1]]],
                    {"fields": ["partner_id", "amount_residual"]})[0]
    cas["partner"] = inv_line["partner_id"][0]
    partner_nom = inv_line["partner_id"][1]
    susp = call("account.move.line", "read", [[cas["susp"]]],
                {"fields": ["account_id", "reconciled"]})[0]
    total_inv = sum(x[2] for x in cas["inv"])
    ecart = round(cas["montant"] - total_inv, 2)

    print("\nBSL %d  %.2f EUR  ->  %s" % (cas["bsl"], cas["montant"], partner_nom))
    print("   cle    : %s" % cas["cle"])
    for n, lid, res in cas["inv"]:
        print("   facture: %-16s ligne %-8d %9.2f" % (n, lid, res))
    print("   total factures %.2f | verse %.2f | ecart %+.2f" % (total_inv, cas["montant"], ecart))
    print("   suspense ligne %d sur %s (rec=%s)" % (cas["susp"], susp["account_id"][1], susp["reconciled"]))
    if 0 < abs(ecart) <= TOLERANCE:
        print("   -> write-off %.2f EUR (<= %.2f)" % (abs(ecart), TOLERANCE))
    elif abs(ecart) > TOLERANCE:
        print("   -> LETTRAGE PARTIEL, %.2f EUR restent ouverts" % abs(ecart))
    print("   %s" % cas["note"])

    if not APPLY:
        continue
    if susp["reconciled"]:
        print("   [SKIP] deja lettree")
        continue

    call("account.move.line", "write", [[cas["susp"]],
         {"account_id": ACC_400, "partner_id": cas["partner"]}])
    print("   [OK] suspense repointee sur 400000 + partenaire %d" % cas["partner"])

    ids = [cas["susp"]] + [x[1] for x in cas["inv"]]
    call_void("account.move.line", "reconcile", [ids])
    print("   [OK] reconcile(%s)" % ids)

    if 0 < abs(ecart) <= TOLERANCE:
        restes = call("account.move.line", "read",
                      [[cas["susp"]] + [x[1] for x in cas["inv"]]],
                      {"fields": ["id", "amount_residual"]})
        ouvertes = [l for l in restes if abs(l["amount_residual"]) > 0.001]
        if ouvertes:
            lib = "Ecart reglement BSL[%d]/%s - %s (%.2f vs %.2f, ecart %+.2f)" % (
                cas["bsl"], partner_nom, cas["inv"][0][0], total_inv, cas["montant"], ecart)
            if ecart > 0:   # trop-percu : 400000 au debit, gain en 757100
                lines = [(0, 0, {"account_id": ACC_400, "debit": abs(ecart), "credit": 0.0,
                                 "partner_id": cas["partner"], "name": lib}),
                         (0, 0, {"account_id": ACC_757100, "debit": 0.0, "credit": abs(ecart),
                                 "partner_id": cas["partner"], "name": lib})]
            else:           # moins-percu : charge 657000, 400000 au credit
                lines = [(0, 0, {"account_id": ACC_657, "debit": abs(ecart), "credit": 0.0,
                                 "partner_id": cas["partner"], "name": lib}),
                         (0, 0, {"account_id": ACC_400, "debit": 0.0, "credit": abs(ecart),
                                 "partner_id": cas["partner"], "name": lib})]
            od = call("account.move", "create", [{
                "journal_id": JRN_MISC, "date": DATE_OD,
                "ref": "Write-off " + lib, "line_ids": lines}])
            call("account.move", "action_post", [[od]])
            od_line = call("account.move.line", "search",
                           [[["move_id", "=", od], ["account_id", "=", ACC_400]]])
            call_void("account.move.line", "reconcile",
                      [od_line + [l["id"] for l in ouvertes]])
            print("   [OK] write-off %.2f EUR poste (OD %d) et lettre" % (abs(ecart), od))

# ------------------------------------------------------------- B. repointages
print("\n\n### B. REPOINTAGES (transit, sans lettrage) ###")
for cas in REPOINTS:
    susp = call("account.move.line", "read", [[cas["susp"]]],
                {"fields": ["account_id", "reconciled"]})[0]
    print("\nBSL %d  %.2f EUR  -- ligne %d sur %s" % (
        cas["bsl"], cas["montant"], cas["susp"], susp["account_id"][1]))
    print("   %s" % cas["note"])
    if not APPLY:
        continue
    if susp["account_id"][0] == cas["account"]:
        print("   [SKIP] deja repointee")
        continue
    call("account.move.line", "write", [[cas["susp"]], {"account_id": cas["account"]}])
    print("   [OK] repointee sur compte %d" % cas["account"])

# ---------------------------------------------------------- C. interne banque
print("\n\n### C. VIREMENTS INTERNES ###")
for cas in INTERNES:
    susp = call("account.move.line", "read", [[cas["susp"]]],
                {"fields": ["account_id", "reconciled"]})[0]
    contre = call("account.move.line", "read", [[cas["contre"]]],
                  {"fields": ["account_id", "reconciled", "amount_residual"]})[0]
    print("\nBSL %d  %.2f EUR  -- ligne %d sur %s" % (
        cas["bsl"], cas["montant"], cas["susp"], susp["account_id"][1]))
    print("   contrepartie BSL %d ligne %d sur %s res=%.2f rec=%s" % (
        cas["contre_bsl"], cas["contre"], contre["account_id"][1],
        contre["amount_residual"], contre["reconciled"]))
    print("   %s" % cas["note"])
    if not APPLY:
        continue
    if susp["reconciled"]:
        print("   [SKIP] deja lettree")
        continue
    call("account.move.line", "write", [[cas["susp"]], {"account_id": ACC_580000}])
    print("   [OK] repointee sur 580000")
    call_void("account.move.line", "reconcile", [[cas["susp"], cas["contre"]]])
    print("   [OK] reconcile([%d, %d])" % (cas["susp"], cas["contre"]))

# ------------------------------------------------------------------- controle
print("\n" + "=" * 92)
if not APPLY:
    print("DRY-RUN termine -- relancer avec 'apply' pour executer.")
else:
    print("CONTROLE FINAL")
    for cas in CLIENTS:
        b = call("account.bank.statement.line", "read", [[cas["bsl"]]],
                 {"fields": ["is_reconciled"]})[0]
        etats = []
        for n, lid, _ in cas["inv"]:
            mv = call("account.move", "search_read", [[["name", "=", n]]],
                      {"fields": ["name", "amount_residual", "payment_state"]})[0]
            etats.append("%s res=%.2f %s" % (mv["name"], mv["amount_residual"], mv["payment_state"]))
        print("  BSL %d lettree=%s | %s" % (cas["bsl"], b["is_reconciled"], " ; ".join(etats)))
    for cas in REPOINTS + INTERNES:
        b = call("account.bank.statement.line", "read", [[cas["bsl"]]],
                 {"fields": ["is_reconciled"]})[0]
        print("  BSL %d lettree=%s" % (cas["bsl"], b["is_reconciled"]))
    reste = call("account.bank.statement.line", "search_count",
                 [[["journal_id", "in", [14, 36]], ["is_reconciled", "=", False]]])
    print("\n  Lignes non lettrees ING+Belfius restantes : %d" % reste)
