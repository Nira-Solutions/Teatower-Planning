# -*- coding: utf-8 -*-
"""
Lettrage ING (14) + Belfius (36) du 03/09/2026 -- nouvelles lignes depuis la passe du 01/09.

  A. Encaissements clients lettres par communication structuree (Foncière Namur,
     Newpharma x2, DelEmbourg).
  B. Virement interne ING -> Belfius 12.000 (580000, les 2 cotes lettres entre eux).
  C. Repointages selon la pratique etablie (SumUp -> 583004, Smartbox -> 580004,
     ING Belgique / Google -> 440000, cotisation MasterCard -> 650000,
     achat Get your mug -> 612000).

    python lettrage_32_ing_belfius_20260903.py        -> DRY-RUN
    python lettrage_32_ing_belfius_20260903.py apply   -> execution
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
    """reconcile()/unlink() renvoient None -> Fault de marshalling cote client
    alors que l operation a reussi cote serveur."""
    try:
        return call(model, method, args, kw)
    except xmlrpc.client.Fault as e:
        if "cannot marshal None" in str(e):
            return None
        raise


def acc(code):
    r = call("account.account", "search_read", [[["code", "=", code]]], {"fields": ["id"]})
    return r[0]["id"]


ACC_400 = acc("400000")
ACC_440 = 192
ACC_650 = 281
ACC_657 = 292        # 657000 Escomptes accordes (charge)
ACC_757 = 347        # 757100 Ecarts de reglement positifs (produit)
ACC_612 = acc("612000")
ACC_580000 = 233     # Internal Transfers of Funds (lettrable)
ACC_580004 = 1225    # Bons cadeaux Smartbox
ACC_583004 = 1188    # SumUp Waterloo
JRN_MISC = 11
DATE_OD = "2026-09-03"

P_ING = 119760       # ING Belgique SA
P_GOOGLE = 115144    # GOOGLE CLOUD EMEA LIMITED

APPLY = len(sys.argv) > 1 and sys.argv[1] == "apply"
print("MODE :", "APPLY" if APPLY else "DRY-RUN")
print("=" * 96)


def suspense(bsl_id):
    b = call("account.bank.statement.line", "read", [[bsl_id]], {"fields": ["move_id"]})[0]
    ls = call("account.move.line", "search_read", [[["move_id", "=", b["move_id"][0]]]],
              {"fields": ["id", "account_id", "reconciled", "amount_residual"]})
    s = [l for l in ls if l["account_id"][1].startswith("499")]
    return s[0] if s else None


def recv_line(move_name):
    mv = call("account.move", "search_read", [[["name", "=", move_name]]], {"fields": ["id"]})[0]
    ls = call("account.move.line", "search_read",
              [[["move_id", "=", mv["id"]],
                ["account_id.account_type", "=", "asset_receivable"]]],
              {"fields": ["id", "amount_residual", "reconciled"]})
    return ls[0]


def write_off(lines_ids, libelle, partner_id, account_id, tol=5.0):
    restes = call("account.move.line", "read", [lines_ids], {"fields": ["id", "amount_residual"]})
    ouvertes = [l for l in restes if abs(l["amount_residual"]) > 0.004]
    if not ouvertes:
        return None
    net = round(sum(l["amount_residual"] for l in ouvertes), 2)
    if abs(net) > tol:
        print("      [!] residu %.2f > %.2f EUR -> laisse ouvert" % (net, tol))
        return None
    if net > 0:   # debit restant -> charge (escompte accorde)
        lines = [(0, 0, {"account_id": account_id, "debit": 0.0, "credit": abs(net),
                         "partner_id": partner_id, "name": libelle}),
                 (0, 0, {"account_id": ACC_657, "debit": abs(net), "credit": 0.0,
                         "partner_id": partner_id, "name": libelle})]
    else:         # credit restant -> produit
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
# A. ENCAISSEMENTS CLIENTS -- communication structuree
# ---------------------------------------------------------------------------
print("\n### A. ENCAISSEMENTS CLIENTS (comm. structuree) ###")

CLIENTS = [
    dict(bsl=20703, montant=318.00, partner=2988,
         factures=["INV/2026/03802"],
         note="Fonciere Namur / Ibis Namur Centre, comm +++000/0044/23806+++ "
              "= INV/2026/03802 (318,00). Ecart 0,00."),
    dict(bsl=20716, montant=806.28, partner=5459,
         factures=["INV/2026/03013", "INV/2026/03705"],
         note="Newpharma, le virement porte les DEUX comm. structurees : "
              "+++000/0040/08827+++ (371,38) + +++000/0043/70252+++ (434,90) "
              "= 806,28. Ecart 0,00."),
    dict(bsl=20720, montant=438.53, partner=5733,
         factures=["INV/2026/03752"],
         note="DelEmbourg / Delhaize Embourg, comm ***000/0044/01372*** "
              "= INV/2026/03752 (438,55). Ecart 0,02 -> write-off."),
]

for c in CLIENTS:
    s = suspense(c["bsl"])
    if s is None:
        print("\n  BSL %d [SKIP] deja traitee" % c["bsl"])
        continue
    print("\n  BSL %d  +%.2f" % (c["bsl"], c["montant"]))
    lignes = []
    for f in c["factures"]:
        l = recv_line(f)
        lignes.append(l["id"])
        print("     %-18s ligne %-8d res=%9.2f rec=%s" % (f, l["id"], l["amount_residual"], l["reconciled"]))
    print("     %s" % c["note"])
    if not APPLY:
        continue
    if s["reconciled"]:
        print("     [SKIP] deja lettree")
        continue
    call("account.move.line", "write", [[s["id"]],
                                        {"account_id": ACC_400, "partner_id": c["partner"]}])
    ids = [s["id"]] + lignes
    call_void("account.move.line", "reconcile", [ids])
    print("     [OK] repointee 400000 + reconcile(%s)" % ids)
    write_off(ids, "Ecart reglement BSL%d %s" % (c["bsl"], c["factures"][0]),
              c["partner"], ACC_400)


# ---------------------------------------------------------------------------
# B. VIREMENT INTERNE ING -> BELFIUS
# ---------------------------------------------------------------------------
print("\n\n### B. VIREMENT INTERNE 12.000 (ING -> Belfius) ###")
sing, sbel = suspense(20718), suspense(20692)
print("  BSL 20718 ING     -12.000,00  suspense=%s" % (sing and sing["id"]))
print("  BSL 20692 BELFIUS +12.000,00  suspense=%s" % (sbel and sbel["id"]))
print("  Meme reference personnelle 6df2bddd941f42a5bc86f6c88b44b846 des 2 cotes.")
if APPLY and sing and sbel:
    call("account.move.line", "write", [[sing["id"], sbel["id"]], {"account_id": ACC_580000}])
    call_void("account.move.line", "reconcile", [[sing["id"], sbel["id"]]])
    print("  [OK] les 2 cotes repointes 580000 puis lettres")


# ---------------------------------------------------------------------------
# C. REPOINTAGES
# ---------------------------------------------------------------------------
print("\n\n### C. REPOINTAGES ###")
REPOINTS = [
    (20691,  4452.85, ACC_583004, None, "SumUp Waterloo -- versement hebdo (arrive desormais sur Belfius)"),
    (20698,     20.00, ACC_580004, None, "Bon cadeau Smartbox PDN-001954290"),
    (20689,    -31.00, ACC_440, P_ING, "ING Belgique facture 2026/01/006174929 du 31/08"),
    (20690,     -2.25, ACC_650, None, "ING cotisation MasterCard Business 08/26"),
    (20719,    -30.61, ACC_440, P_GOOGLE, "GOOGLE *ADS6553294698"),
    (20717,    -34.00, ACC_612, None, "Achat Get your mug (Liege) -- fournitures"),
]

for bsl, montant, account, partner, note in REPOINTS:
    s = suspense(bsl)
    if s is None:
        print("  BSL %-6d [SKIP] deja traitee -- %s" % (bsl, note))
        continue
    print("  BSL %-6d %11.2f -> compte %-5d %-8s | %s" % (
        bsl, montant, account, ("p%d" % partner) if partner else "", note))
    if not APPLY:
        continue
    vals = {"account_id": account}
    if partner:
        vals["partner_id"] = partner
    call("account.move.line", "write", [[s["id"]], vals])
    print("        [OK] repointee")

print("\n" + "=" * 96)
rest = call("account.bank.statement.line", "search_count",
            [[["journal_id", "in", [14, 36]], ["is_reconciled", "=", False]]])
print("Lignes ING+Belfius encore non lettrees : %d" % rest)
