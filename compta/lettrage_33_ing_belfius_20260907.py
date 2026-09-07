# -*- coding: utf-8 -*-
"""
Lettrage ING (14) + Belfius (36) du 07/09/2026 -- nouvelles lignes depuis la passe du 03/09.

  A. Encaissements clients lettres par communication structuree / n de facture.
  B. Sortie fournisseur NOWJOBS lettree (comm. structuree = n de facture).
  C. Virement interne ING -> Belfius 5.000 (580000, les 2 cotes lettres entre eux).
  D. Repointages selon la pratique etablie.

    python lettrage_33_ing_belfius_20260907.py        -> DRY-RUN
    python lettrage_33_ing_belfius_20260907.py apply   -> execution
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


ACC_400 = 162        # 400000 Customers
ACC_440 = 192        # 440000 Suppliers
ACC_455 = 211        # 455000 Remuneration
ACC_600 = 234        # 600000 Purchases of Raw Materials
ACC_612 = 838        # 612000 Fournitures
ACC_657 = 292        # 657000 Escomptes accordes (charge)
ACC_757 = 347        # 757100 Ecarts de reglement positifs (produit)
ACC_615330 = 1147    # 615330 frais de restaurant
ACC_580000 = 233     # Internal Transfers of Funds (lettrable)
ACC_580003 = 821     # Paiement Sodexo-Edenred (titres-repas)
ACC_583004 = 1188    # SumUp Waterloo
JRN_MISC = 11
DATE_OD = "2026-09-07"

P_BELFIUS = 119773
P_SENDCLOUD = 113237
P_SDWORX_ASBL = 7040
P_GOOGLE = 115144
P_FAIRE = 6404
P_NOWJOBS = 8351

APPLY = len(sys.argv) > 1 and sys.argv[1] == "apply"
print("MODE :", "APPLY" if APPLY else "DRY-RUN")
print("=" * 100)


def suspense(bsl_id):
    b = call("account.bank.statement.line", "read", [[bsl_id]], {"fields": ["move_id"]})[0]
    ls = call("account.move.line", "search_read", [[["move_id", "=", b["move_id"][0]]]],
              {"fields": ["id", "account_id", "reconciled", "amount_residual"]})
    s = [l for l in ls if l["account_id"][1].startswith("499")]
    return s[0] if s else None


def piece_line(move_name, kind):
    """kind = 'asset_receivable' ou 'liability_payable'"""
    mv = call("account.move", "search_read", [[["name", "=", move_name]]],
              {"fields": ["id", "partner_id"]})[0]
    ls = call("account.move.line", "search_read",
              [[["move_id", "=", mv["id"]], ["account_id.account_type", "=", kind]]],
              {"fields": ["id", "amount_residual", "reconciled", "account_id", "partner_id"]})
    return ls[0], mv


def write_off(lines_ids, libelle, partner_id, account_id, tol=5.0):
    restes = call("account.move.line", "read", [lines_ids], {"fields": ["id", "amount_residual"]})
    ouvertes = [l for l in restes if abs(l["amount_residual"]) > 0.004]
    if not ouvertes:
        return None
    net = round(sum(l["amount_residual"] for l in ouvertes), 2)
    if abs(net) > tol:
        print("      [!] residu %.2f > %.2f EUR -> laisse ouvert" % (net, tol))
        return None
    if net > 0:
        lines = [(0, 0, {"account_id": account_id, "debit": 0.0, "credit": abs(net),
                         "partner_id": partner_id, "name": libelle}),
                 (0, 0, {"account_id": ACC_657, "debit": abs(net), "credit": 0.0,
                         "partner_id": partner_id, "name": libelle})]
    else:
        lines = [(0, 0, {"account_id": account_id, "debit": abs(net), "credit": 0.0,
                         "partner_id": partner_id, "name": libelle}),
                 (0, 0, {"account_id": ACC_757, "debit": 0.0, "credit": abs(net),
                         "partner_id": partner_id, "name": libelle})]
    od = call("account.move", "create", [{"journal_id": JRN_MISC, "date": DATE_OD,
                                          "ref": ("Write-off " + libelle)[:120],
                                          "line_ids": lines}])
    call("account.move", "action_post", [[od]])
    od_line = call("account.move.line", "search",
                   [[["move_id", "=", od], ["account_id", "=", account_id]]])
    call_void("account.move.line", "reconcile", [od_line + [l["id"] for l in ouvertes]])
    print("      [OK] write-off %.2f EUR (OD %d) lettre" % (net, od))
    return od


# ---------------------------------------------------------------------------
# A. ENCAISSEMENTS CLIENTS
# ---------------------------------------------------------------------------
print("\n### A. ENCAISSEMENTS CLIENTS ###")

CLIENTS = [
    dict(bsl=20757, montant=179.81, pieces=["INV/2026/04014"],
         note="Dragon Phenix, comm ***000/0045/17368*** = INV/2026/04014 (179,81). Ecart 0,00."),
    dict(bsl=20762, montant=735.65, pieces=["INV/2026/03796", "RINV/26-27/0022"],
         note="KAIO Retail invest / Delhaize Ottignies : INV/2026/03796 (1.227,80) MOINS "
              "l'avoir RINV/26-27/0022 (492,13) = 735,67. Ecart 0,02 -> write-off. "
              "L'avoir est porte par la fiche doublon #3016, la facture par #5649."),
    dict(bsl=20765, montant=340.90, pieces=["INV/2026/03678"],
         note="Wonka / Intermarche Heusy, comm ***000/0043/57421*** = INV/2026/03678 (340,91). "
              "Ecart 0,01 -> write-off."),
    dict(bsl=20782, montant=191.10, pieces=["INV/2026/03865"],
         note="Chez Remy, communication en clair INV/2026/03865 (191,10). Ecart 0,00."),
    dict(bsl=20783, montant=344.06, pieces=["INV/2026/03755"],
         note="Virspaco / Delhaize affilie, communication en clair INV/2026/03755 (344,06). Ecart 0,00."),
    dict(bsl=20791, montant=319.20, pieces=["INV/2026/03446"],
         note="AD War / Delhaize Warmonceau, comm ***000/0042/40617*** = INV/2026/03446 (319,20). Ecart 0,00."),
    dict(bsl=20797, montant=354.40, pieces=["INV/2026/04050"],
         note="Mouch et Martine, comm ***000/0045/38182*** = INV/2026/04050 (354,40). Ecart 0,00."),
    dict(bsl=20800, montant=525.01, pieces=["INV/2026/03765"],
         note="JHM / Joffrey Helson Menuiserie, comm +++000/0044/04103+++ = INV/2026/03765 (525,01). Ecart 0,00."),
]

for c in CLIENTS:
    s = suspense(c["bsl"])
    if s is None:
        print("\n  BSL %d [SKIP] deja traitee" % c["bsl"])
        continue
    print("\n  BSL %d  +%.2f" % (c["bsl"], c["montant"]))
    lignes, partner = [], None
    for f in c["pieces"]:
        l, mv = piece_line(f, "asset_receivable")
        lignes.append(l["id"])
        if partner is None:
            partner = mv["partner_id"][0]
        print("     %-18s ligne %-8d res=%9.2f rec=%-5s partner=%s" % (
            f, l["id"], l["amount_residual"], l["reconciled"], mv["partner_id"][1][:32]))
    print("     %s" % c["note"])
    if not APPLY:
        continue
    if s["reconciled"]:
        print("     [SKIP] deja lettree")
        continue
    call("account.move.line", "write", [[s["id"]], {"account_id": ACC_400, "partner_id": partner}])
    ids = [s["id"]] + lignes
    call_void("account.move.line", "reconcile", [ids])
    print("     [OK] repointee 400000 + reconcile(%s)" % ids)
    write_off(ids, "Ecart reglement BSL%d %s" % (c["bsl"], c["pieces"][0]), partner, ACC_400)


# ---------------------------------------------------------------------------
# B. SORTIE FOURNISSEUR NOWJOBS
# ---------------------------------------------------------------------------
print("\n\n### B. SORTIE FOURNISSEUR -- NOWJOBS ###")
s = suspense(20726)
lb, mvb = (None, None)
if s is None:
    print("  BSL 20726 [SKIP] deja traitee")
else:
    lb, mvb = piece_line("RESA1206", "liability_payable")
    print("  BSL 20726 ING -4.114,79 du 02/09")
    print("  comm ***260/9430/20026*** -> 260943020026 contient 26094302 = facture NOWJOBS FA26094302")
    print("  RESA1206  ligne %d  res=%.2f  echeance 07/08  -> ecart 0,10 (write-off)"
          % (lb["id"], lb["amount_residual"]))
    if APPLY:
        call("account.move.line", "write", [[s["id"]],
                                            {"account_id": ACC_440, "partner_id": P_NOWJOBS}])
        ids = [s["id"], lb["id"]]
        call_void("account.move.line", "reconcile", [ids])
        print("  [OK] repointee 440000 + reconcile(%s)" % ids)
        write_off(ids, "Ecart reglement BSL20726 RESA1206", P_NOWJOBS, ACC_440)


# ---------------------------------------------------------------------------
# C. VIREMENT INTERNE ING -> BELFIUS 5.000
# ---------------------------------------------------------------------------
print("\n\n### C. VIREMENT INTERNE 5.000 (ING -> Belfius) ###")
sing, sbel = suspense(20779), suspense(20746)
print("  BSL 20779 ING     -5.000,00  suspense=%s" % (sing and sing["id"]))
print("  BSL 20746 BELFIUS +5.000,00  suspense=%s" % (sbel and sbel["id"]))
print("  Meme reference personnelle 74c62d3fcf0c4341881642c2b0de0b7c des 2 cotes.")
if APPLY and sing and sbel:
    call("account.move.line", "write", [[sing["id"], sbel["id"]], {"account_id": ACC_580000}])
    call_void("account.move.line", "reconcile", [[sing["id"], sbel["id"]]])
    print("  [OK] les 2 cotes repointes 580000 puis lettres")


# ---------------------------------------------------------------------------
# D. REPOINTAGES
# ---------------------------------------------------------------------------
print("\n\n### D. REPOINTAGES ###")
REPOINTS = [
    (20742,    625.63, ACC_583004, None, "SumUp PID1350335 -- versement quotidien (etait hebdo)"),
    (20766,    451.63, ACC_583004, None, "SumUp PID1351480 -- versement quotidien"),
    (20764,      9.81, ACC_580003, None, "Edenred titres-repas boutiques"),
    (20743,    -12.32, ACC_440, P_BELFIUS, "Belfius -- frais d'expedition des avis 09/26"),
    (20744,     -7.67, ACC_440, P_BELFIUS, "Belfius -- Business Pack Plus 09/26"),
    (20745, -17009.09, ACC_455, None, "Ordre collectif salaires du 04/09"),
    (20756,   -144.00, ACC_440, P_SENDCLOUD, "Sendcloud domiciliation 1-26-BE0075617"),
    (20760,   -591.86, ACC_440, P_SDWORX_ASBL, "SD Worx ASBL -- ref 9193737, aucune piece a ce montant (a documenter)"),
    (20787,   -384.12, ACC_440, P_GOOGLE, "Google Cloud domiciliation APPS COMMERCE teatower.com"),
    (20777,    -63.50, ACC_615330, None, "WEX sandwichs Marche-en-Famenne"),
    (20788,    -43.70, ACC_612, None, "Bureau Durbuy -- fournitures"),
    (20793,   -180.51, ACC_600, P_FAIRE, "Faire -- NCA Europe Design"),
    (20794,   -329.00, ACC_600, P_FAIRE, "Faire -- Eulenschnitt"),
    (20795,   -138.78, ACC_600, P_FAIRE, "Faire -- cool people club"),
    (20796,   -221.60, ACC_600, P_FAIRE, "Faire -- Sass & Belle"),
]

for bsl, montant, account, partner, note in REPOINTS:
    s = suspense(bsl)
    if s is None:
        print("  BSL %-6d [SKIP] deja traitee -- %s" % (bsl, note))
        continue
    print("  BSL %-6d %11.2f -> compte %-5d %-9s | %s" % (
        bsl, montant, account, ("p%d" % partner) if partner else "", note))
    if not APPLY:
        continue
    vals = {"account_id": account}
    if partner:
        vals["partner_id"] = partner
    call("account.move.line", "write", [[s["id"]], vals])
    print("        [OK] repointee")

print("\n" + "=" * 100)
rest = call("account.bank.statement.line", "search_count",
            [[["journal_id", "in", [14, 36]], ["is_reconciled", "=", False]]])
print("Lignes ING+Belfius encore non lettrees : %d" % rest)
