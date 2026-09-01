# -*- coding: utf-8 -*-
"""
Lettrage ING (14) + Belfius (36) du 01/09/2026 -- passe "tout".

  A. Reparation de la cascade de lettrages croises RADIUS (30 partials mal
     apparies depuis nov-2025) puis re-appariement par communication SEPA,
     ce qui debloque les 2 domiciliations ING de juillet.
  B. Lettrages facture <-> banque certains (Proximus x3, Worldline).
  C. Repointages 440000 + partenaire / 455000 / 451001 / 650000
     (pratique etablie ; aucun arbitrage P&L discretionnaire).

    python lettrage_30_ing_belfius_20260901.py         -> DRY-RUN
    python lettrage_30_ing_belfius_20260901.py apply    -> execution
"""
import os
import re
import sys
import xmlrpc.client
from collections import defaultdict

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
    """reconcile()/unlink() renvoient None -> Fault de marshalling cote client
    alors que l operation a reussi cote serveur."""
    try:
        return call(model, method, args, kw)
    except xmlrpc.client.Fault as e:
        if "cannot marshal None" in str(e):
            return None
        raise


ACC_440 = 192       # 440000 Suppliers
ACC_455 = 211       # 455000 Remuneration
ACC_451OSS = 934    # 451001 TVA a payer OSS
ACC_650 = 281       # 650000 Interest, Commission and Other Charges
ACC_657 = 292       # 657000 Financial Discounts Allowed  (charge)
ACC_757 = 347       # 757100 Positive Payment Differences (produit)
JRN_MISC = 11
DATE_OD = "2026-09-01"

APPLY = len(sys.argv) > 1 and sys.argv[1] == "apply"
print("MODE :", "APPLY" if APPLY else "DRY-RUN")
print("=" * 96)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def suspense(bsl_id):
    b = call("account.bank.statement.line", "read", [[bsl_id]],
             {"fields": ["move_id", "amount"]})[0]
    ls = call("account.move.line", "search_read", [[["move_id", "=", b["move_id"][0]]]],
              {"fields": ["id", "account_id", "reconciled", "amount_residual"]})
    s = [l for l in ls if l["account_id"][1].startswith("499")]
    return s[0] if s else None


def write_off(lines_ids, libelle, partner_id, tol=5.0):
    """Solde le residu restant sur les lignes 440000 fournies (<= tol)."""
    restes = call("account.move.line", "read", [lines_ids], {"fields": ["id", "amount_residual"]})
    ouvertes = [l for l in restes if abs(l["amount_residual"]) > 0.004]
    if not ouvertes:
        return None
    net = round(sum(l["amount_residual"] for l in ouvertes), 2)
    if abs(net) > tol:
        print("      [!] residu %.2f > %.2f EUR -> laisse ouvert" % (net, tol))
        return None
    if net > 0:   # debit restant sur 440000 -> produit
        lines = [(0, 0, {"account_id": ACC_440, "debit": 0.0, "credit": abs(net),
                         "partner_id": partner_id, "name": libelle}),
                 (0, 0, {"account_id": ACC_757, "debit": abs(net), "credit": 0.0,
                         "partner_id": partner_id, "name": libelle})]
    else:         # credit restant -> charge
        lines = [(0, 0, {"account_id": ACC_440, "debit": abs(net), "credit": 0.0,
                         "partner_id": partner_id, "name": libelle}),
                 (0, 0, {"account_id": ACC_657, "debit": 0.0, "credit": abs(net),
                         "partner_id": partner_id, "name": libelle})]
    od = call("account.move", "create", [{"journal_id": JRN_MISC, "date": DATE_OD,
                                          "ref": ("Write-off " + libelle)[:120],
                                          "line_ids": lines}])
    call("account.move", "action_post", [[od]])
    od_line = call("account.move.line", "search",
                   [[["move_id", "=", od], ["account_id", "=", ACC_440]]])
    call_void("account.move.line", "reconcile", [od_line + [l["id"] for l in ouvertes]])
    print("      [OK] write-off %.2f EUR (OD %d) lettre" % (net, od))
    return od


# ---------------------------------------------------------------------------
# A. RADIUS -- reparation de la cascade de lettrages croises
# ---------------------------------------------------------------------------
print("\n### A. RADIUS -- cascade de lettrages croises ###")
RADIUS = 114270
BAD_PARTIALS = [19866, 19867, 19868, 19869, 9127, 9128, 19871, 19872, 19873, 19874,
                19875, 19876, 19877, 19878, 19879, 19880, 19881, 19882, 19883, 19884,
                19885, 19886, 19887, 19888, 19889, 19890, 19891, 19892, 19893, 19894]
# P12917 (BNK1/25-26/5165 <-> RESA560, 519,70) volontairement CONSERVE :
# le libelle bancaire porte "RESA560" et le montant est exact au centime.


def radius_lines():
    ls = call("account.move.line", "search_read",
              [[["partner_id", "child_of", RADIUS],
                ["account_id.account_type", "=", "liability_payable"],
                ["parent_state", "=", "posted"]]],
              {"fields": ["id", "date", "move_id", "name", "debit", "credit",
                          "amount_residual", "reconciled"],
               "order": "date asc,id asc", "limit": 300})
    mv = call("account.move", "read", [sorted({l["move_id"][0] for l in ls})],
              {"fields": ["id", "name", "ref", "payment_reference", "statement_line_id"]})
    mvd = {x["id"]: x for x in mv}
    sl_ids = [x["statement_line_id"][0] for x in mv if x.get("statement_line_id")]
    sld = {x["id"]: x for x in call("account.bank.statement.line", "read", [sl_ids],
                                    {"fields": ["id", "payment_ref"]})} if sl_ids else {}
    for l in ls:
        mo = mvd[l["move_id"][0]]
        if mo.get("statement_line_id"):
            pr = str(sld.get(mo["statement_line_id"][0], {}).get("payment_ref") or "")
            seg = re.split(r"Communication\s*:", pr)
            txt = (seg[-1] if len(seg) > 1 else pr) + " " + str(l.get("name") or "")
        else:
            txt = " ".join(str(x or "") for x in
                           [mo.get("ref"), mo.get("payment_reference"), l.get("name")])
        t = txt.replace(" ", "").replace("-", "")
        k = re.findall(r"(?:BE)?(\d{12})", t)
        l["k"] = k[0] if k else (re.findall(r"(RESA\d{3,5})", txt) or [None])[0]
        l["mv"] = mo["name"]
    return ls


still = [p for p in BAD_PARTIALS
         if call("account.partial.reconcile", "search_count", [[["id", "=", p]]])]
print("  partials mal apparies encore en place : %d / %d" % (len(still), len(BAD_PARTIALS)))
if APPLY and still:
    call_void("account.partial.reconcile", "unlink", [still])
    print("  [OK] %d partials defaits" % len(still))

ls = radius_lines()
grp = defaultdict(list)
for l in ls:
    if abs(l["amount_residual"]) > 0.004:
        grp[l["k"]].append(l)
print("\n  re-appariement par communication SEPA :")
for k, items in sorted(grp.items(), key=lambda x: str(x[0])):
    deb = [i for i in items if i["amount_residual"] > 0]
    cre = [i for i in items if i["amount_residual"] < 0]
    solde = round(sum(i["amount_residual"] for i in items), 2)
    etat = "APPARIABLE" if (deb and cre) else "orphelin"
    print("   [%-10s] cle %-14s solde=%9.2f | %s" % (
        etat, str(k), solde,
        " ".join("%s(%+.2f)" % (i["mv"][:18], i["amount_residual"]) for i in items)))
    if k is None or not (APPLY and deb and cre):
        continue
    ids = [i["id"] for i in items]
    call_void("account.move.line", "reconcile", [ids])
    print("      [OK] reconcile(%s)" % ids)
    if abs(solde) <= 5.0:
        write_off(ids, "Ecart lettrage Radius %s" % k, RADIUS)

print("\n  domiciliations ING de juillet :")
for bsl, montant, cle in [(19871, 308.80, "261701699965"), (19985, 459.81, "261701759658")]:
    s = suspense(bsl)
    if s is None:
        print("   BSL %d [SKIP] deja traitee" % bsl)
        continue
    inv = [l for l in radius_lines() if l["k"] == cle and l["amount_residual"] < -0.004]
    print("   BSL %d  -%.2f  cle %s -> %s" % (
        bsl, montant, cle,
        ", ".join("%s res=%.2f" % (i["mv"], i["amount_residual"]) for i in inv) or "AUCUNE"))
    if not APPLY or not inv:
        continue
    if s["reconciled"]:
        print("      [SKIP] deja lettree")
        continue
    call("account.move.line", "write", [[s["id"]], {"account_id": ACC_440, "partner_id": RADIUS}])
    ids = [s["id"]] + [i["id"] for i in inv]
    call_void("account.move.line", "reconcile", [ids])
    print("      [OK] repointee 440000 + reconcile(%s)" % ids)
    write_off(ids, "Ecart lettrage Radius BSL%d" % bsl, RADIUS)


# ---------------------------------------------------------------------------
# B. LETTRAGES FACTURE <-> BANQUE
# ---------------------------------------------------------------------------
print("\n\n### B. LETTRAGES FACTURE <-> BANQUE ###")
PROXIMUS = 7157
WORLDLINE = 7194

# B0 : de-lettrer P20143 (RESA1199 3,40 <-> RBILL/26-27/07/0006) pour rendre
#      la note de credit 07/0006 entiere au virement du 24/07.
if call("account.partial.reconcile", "search_count", [[["id", "=", 20143]]]):
    print("\n  P20143 (RESA1199 3,40 <-> RBILL/26-27/07/0006) : a defaire")
    if APPLY:
        call_void("account.partial.reconcile", "unlink", [[20143]])
        print("      [OK] defait")
else:
    print("\n  P20143 : deja defait")

CAS = [
    dict(bsl=20548, montant=937.17, partner=PROXIMUS,
         pieces=[("RESA1239", 201430), ("RBILL/26-27/08/0001 (avoir)", 201256)],
         note="Communication SEPA 007604959089 + 007690346873 : "
              "986,78 (facture) - 49,61 (avoir) = 937,17. Ecart 0,00."),
    dict(bsl=20549, montant=100.00, partner=PROXIMUS,
         pieces=[("RESA1237", 201434), ("RBILL/26-27/08/0002 (avoir)", 201437)],
         note="Communication SEPA 007604959092 + 007600511574 : "
              "122,98 (facture) - 22,98 (avoir) = 100,00. Ecart 0,00. "
              "L avoir est sur la fiche Proximus SA de droit public (#125125)."),
    dict(bsl=19944, montant=200.00, partner=PROXIMUS,
         delettrer=[19993, 19994],
         pieces=[("RESA1197", 191871), ("RBILL/26-27/07/0006 (avoir)", 191876)],
         note="Communication SEPA 007604430233 + 007600510011 : "
              "245,95 - 45,96 = 199,99, verse 200,00 -> write-off 0,01. "
              "RESA1197 etait lettree a tort contre 2 soldes d ouverture du "
              "29/12/2025 (cf. project_lettrages_croises_radius_proximus)."),
    dict(bsl=20546, montant=541.17, partner=WORLDLINE,
         pieces=[("RESA1171", 192887)],
         partiel=True,
         note="Communication SEPA /INV/2260379939 : facture 621,54, preleve "
              "541,17 -> lettrage PARTIEL, 80,37 restent ouverts. Meme schema "
              "que juillet (RESA1059 626,31 preleve 529,78, reste 96,53)."),
]

for c in CAS:
    s = suspense(c["bsl"])
    if s is None:
        print("\n  BSL %d [SKIP] deja traitee" % c["bsl"])
        continue
    print("\n  BSL %d  -%.2f" % (c["bsl"], c["montant"]))
    for nom, lid in c["pieces"]:
        l = call("account.move.line", "read", [[lid]], {"fields": ["amount_residual", "reconciled"]})[0]
        print("     %-32s ligne %-8d res=%9.2f rec=%s" % (nom, lid, l["amount_residual"], l["reconciled"]))
    print("     %s" % c["note"])
    if not APPLY:
        continue
    for pid in c.get("delettrer", []):
        if call("account.partial.reconcile", "search_count", [[["id", "=", pid]]]):
            call_void("account.partial.reconcile", "unlink", [[pid]])
            print("     [OK] partial %d defait" % pid)
    if s["reconciled"]:
        print("     [SKIP] deja lettree")
        continue
    call("account.move.line", "write", [[s["id"]], {"account_id": ACC_440, "partner_id": c["partner"]}])
    ids = [s["id"]] + [lid for _, lid in c["pieces"]]
    call_void("account.move.line", "reconcile", [ids])
    print("     [OK] repointee 440000 + reconcile(%s)" % ids)
    if not c.get("partiel"):
        write_off(ids, "Ecart reglement BSL%d %s" % (c["bsl"], c["pieces"][0][0]), c["partner"])

# B1 : RESA1199 (3,40) <-> RBILL/26-27/07/0005 residuel (3,40)
print("\n  RESA1199 (3,40 credit) <-> RBILL/26-27/07/0005 residuel (3,40 debit)")
r99 = call("account.move.line", "read", [[191794]], {"fields": ["amount_residual", "reconciled"]})[0]
r05 = call("account.move.line", "read", [[191792]], {"fields": ["amount_residual", "reconciled"]})[0]
print("     RESA1199 res=%.2f | RBILL/26-27/07/0005 res=%.2f" % (r99["amount_residual"], r05["amount_residual"]))
if APPLY and abs(r99["amount_residual"] + r05["amount_residual"]) < 0.005 \
        and abs(r99["amount_residual"]) > 0.004:
    call_void("account.move.line", "reconcile", [[191794, 191792]])
    print("     [OK] reconcile([191794, 191792])")


# ---------------------------------------------------------------------------
# C. REPOINTAGES (clot le suspense 499000, sans lettrage)
# ---------------------------------------------------------------------------
print("\n\n### C. REPOINTAGES ###")
P_GOOGLE = 115144      # GOOGLE CLOUD EMEA LIMITED
P_ADOBE = 115886
P_INTUIT = 7386        # Intuit Mailchimp
P_SHOPIFY = 6420
P_SENDCLOUD = 113237
P_SKEEPERS = 7193
P_KIRCHNER = 7195
P_BELFIUS = 119773     # Belfius Banque-Bank
P_DOUANES = 115885     # Bureau Unique des Douanes et Accises
P_CILE = 7366          # Compagnie Intercommunale Liegeoise des Eaux

REPOINTS = [
    # --- 440000 + partenaire (precedents identiques dans le journal) --------
    (19480, -437.07, ACC_440, P_GOOGLE, "GOOGLE *ADS"),
    (19607, -384.12, ACC_440, P_GOOGLE, "Google Cloud EMEA (domiciliation)"),
    (19703, -500.00, ACC_440, P_GOOGLE, "GOOGLE *ADS"),
    (19972, -500.00, ACC_440, P_GOOGLE, "GOOGLE *ADS"),
    (20110, -194.46, ACC_440, P_GOOGLE, "GOOGLE *ADS"),
    (20204, -384.12, ACC_440, P_GOOGLE, "Google Cloud EMEA (domiciliation)"),
    (20380, -500.00, ACC_440, P_GOOGLE, "GOOGLE *ADS"),
    (20662, -500.00, ACC_440, P_GOOGLE, "GOOGLE *ADS"),
    (19638,  -36.29, ACC_440, P_ADOBE, "ADOBE"),
    (19728,  -60.49, ACC_440, P_ADOBE, "ADOBE"),
    (20257,  -36.29, ACC_440, P_ADOBE, "ADOBE"),
    (20377,  -60.49, ACC_440, P_ADOBE, "ADOBE"),
    (19639, -722.47, ACC_440, P_INTUIT, "Intuit Ireland (Mailchimp)"),
    (20256, -715.63, ACC_440, P_INTUIT, "Intuit Ireland (Mailchimp)"),
    (19788, -526.99, ACC_440, P_SHOPIFY, "SHOPIFY"),
    (20394, -491.71, ACC_440, P_SHOPIFY, "SHOPIFY"),
    (19780,  -24.45, ACC_440, P_SENDCLOUD, "Sendcloud 1-26-BE0060716"),
    (20178, -121.00, ACC_440, P_SENDCLOUD, "Sendcloud 1-26-BE0064771"),
    (20489, -258.25, ACC_440, P_SKEEPERS, "Skeepers"),
    (19625, -12837.54, ACC_440, P_KIRCHNER, "Kirchner domiciliation (avis 07/07/26)"),
    (20352, -49551.11, ACC_440, P_KIRCHNER, "Kirchner virement clearing 14/08"),
    (20635, -9912.97, ACC_440, P_KIRCHNER, "Kirchner domiciliation 27/08 (libelle SEPA tronque)"),
    (19746, -1040.40, ACC_440, P_DOUANES, "Douanes et Accises 970AI8902/F"),
    (20276, -699.00, ACC_440, P_DOUANES, "Douanes et Accises 970AI8902/F"),
    (20420,  -59.00, ACC_440, P_CILE, "CILE facture 70003928"),
    # --- frais bancaires Belfius -> 440000 + Belfius Banque-Bank ------------
    (18034,   -4.42, ACC_440, P_BELFIUS, "Belfius frais de tenue 02/26"),
    (18036,   -4.42, ACC_440, P_BELFIUS, "Belfius frais de tenue 03/26"),
    (18037,   -3.08, ACC_440, P_BELFIUS, "Belfius frais d expedition avis 03/26"),
    (18038,   -4.42, ACC_440, P_BELFIUS, "Belfius frais de tenue 04/26"),
    (18039,   -3.08, ACC_440, P_BELFIUS, "Belfius frais d expedition avis 04/26"),
    (18360,   -4.42, ACC_440, P_BELFIUS, "Belfius frais de tenue 05/26"),
    (19184,   -4.42, ACC_440, P_BELFIUS, "Belfius frais de tenue 06/26"),
    (18046,  -15.00, ACC_440, P_BELFIUS, "Belfius frais gestion Business Cash Plus 04/26"),
    (19839,  -15.00, ACC_440, P_BELFIUS, "Belfius frais gestion Business Cash Plus 07/26"),
    (19570,  -39.83, ACC_440, P_BELFIUS, "Belfius commission Business Cash Plus 07/26"),
    (18047, -250.00, ACC_440, P_BELFIUS, "Belfius frais de dossier credit 071-9570627-86"),
    (19190, -250.00, ACC_440, P_BELFIUS, "Belfius frais de dossier credit 071-9574936-30"),
    # --- charges financieres pures -> 650000 -------------------------------
    (19571,   -0.64, ACC_650, None, "Belfius interets 01.04-30.06.2026"),
    (19460,   -2.25, ACC_650, None, "ING cotisation MasterCard Business 06/26"),
    (20104,   -2.25, ACC_650, None, "ING cotisation MasterCard Business 07/26"),
    (20647, -180.00, ACC_650, None, "Frais garantie bancaire Trade Finance Services"),
    # --- remunerations -> 455000 -------------------------------------------
    (19735, -1574.53, ACC_455, None, "Fichier de virements SEPA (salaires)"),
    (20087,  -117.60, ACC_455, None, "Fichier de virements SEPA (salaires)"),
    (20288, -4909.57, ACC_455, None, "Fichier de virements SAL-20260801-TV"),
    (20157, -16714.08, ACC_455, None, "Ordre collectif Belfius TEATOWER-SAL-20260801-MAIN"),
    (19610,  -500.00, ACC_455, None, "Avance salaire Audrey Vansimpsen 07/07"),
    (19737,  -750.00, ACC_455, None, "Avance salaire Camille van Ooteghem 14/07"),
    (19738, -1000.00, ACC_455, None, "Avance salaire Gilles Cabosart 14/07"),
    (19739,  -500.00, ACC_455, None, "Avance salaire Audrey Vansimpsen 14/07"),
    (20391,  -750.00, ACC_455, None, "Avance salaire Camille van Ooteghem 14/08"),
    (20392, -1000.00, ACC_455, None, "Avance salaire Gilles Cabosart 14/08"),
    # --- TVA OSS -----------------------------------------------------------
    (20208,  -296.14, ACC_451OSS, None, "TVA OSS Q2.2026 (BE/BE0656763145/Q2.2026)"),
]

for bsl, montant, acc, partner, note in REPOINTS:
    s = suspense(bsl)
    if s is None:
        print("   BSL %d [SKIP] deja traitee" % bsl)
        continue
    if s is None:
        print("  BSL %-6d [SKIP] plus de ligne 499000 -- %s" % (bsl, note))
        continue
    print("  BSL %-6d %11.2f -> compte %-4d %-8s | %s" % (
        bsl, montant, acc, ("p%d" % partner) if partner else "", note))
    if not APPLY:
        continue
    vals = {"account_id": acc}
    if partner:
        vals["partner_id"] = partner
    call("account.move.line", "write", [[s["id"]], vals])
    print("        [OK] repointee")

print("\n" + "=" * 96)
rest = call("account.bank.statement.line", "search_count",
            [[["journal_id", "in", [14, 36]], ["is_reconciled", "=", False]]])
print("Lignes ING+Belfius encore non lettrees : %d" % rest)
