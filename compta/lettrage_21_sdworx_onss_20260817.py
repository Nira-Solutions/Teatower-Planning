# -*- coding: utf-8 -*-
"""
LETTRAGE SD WORX / ONSS -- 17/08/2026.

Demande Nicolas : les gros paiements ONSS / precompte ont ete faits en direct depuis
Belfius et ING sans passer par SD Worx ; les factures SD Worx restent ouvertes alors
qu'une partie est payee. Solder les plus anciennes avec ce qui a reellement ete paye.

Ce que fait le script
---------------------
1. REPOINTAGE : les 4 lignes bancaires ONSS / SD Worx encore en suspens 499000 sont
   repointees vers 440000 Fournisseurs, partenaire SD Worx Secretariat Social (#7040).
   Bilan uniquement, aucun impact sur le compte de resultat.
2. REALIGNEMENT PARTENAIRE : les debits SD Worx portes par les fiches doublons
   (Sd Worx A.S.B.L #7368, Sd Worx Belgium S.A #7384) sont ramenes sur #7040, sinon
   Odoo ne peut pas les lettrer contre les factures.
3. LETTRAGE CIBLE : les 2 virements portant une reference de facture explicite dans
   leur communication sont lettres sur CETTE facture, pas en FIFO.
4. LETTRAGE FIFO : le solde disponible est impute sur les factures SD Worx ouvertes
   les plus anciennes d'abord, jusqu'a epuisement. La derniere facture servie reste
   en lettrage partiel (jamais de write-off : les ecarts ici sont des restes a payer,
   pas des ecarts de reglement, cf feedback_compta_ecart_reglement_tolerance).

NON TRAITE VOLONTAIREMENT
  - BSL 19746 (1.040,40) et 20276 (699,00) "Administration Generale" : ce sont les
    DOUANES ET ACCISES (comm. 970AI8902/F), pas du precompte. Rien a voir avec SD Worx.
  - BSL 20157 (16.714,08) : fichier de paie TEATOWER-SAL-20260801-MAIN -> 455000.
  - BSL 20352 (49.551,11) : Kirchner Fischer, fournisseur marchandise.
  - L'ecart de ~47.000 EUR entre l'encours Odoo et les 65.000 EUR annonces par
    l'associe : doublon suspecte factures SD Worx <-> OD de paie de juin 2026
    (cf OD "Apurement dette ONSS 454000 -- doublon" du 30/06). Analyse separee.
    Le FIFO ci-dessous vise decembre 2025 -> fevrier 2026, hors perimetre du doublon.

NOTE CONFIDENTIALITE : repo PUBLIC, pas de secret ici (ODOO_PWD en variable d'env).

Usage : python lettrage_21_sdworx_onss_20260817.py            (DRY-RUN)
        python lettrage_21_sdworx_onss_20260817.py --apply
"""

import os
import sys
import xmlrpc.client

sys.stdout.reconfigure(encoding="utf-8")
DRY = "--apply" not in sys.argv

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ.get("ODOO_PWD")
if not PWD:
    raise SystemExit("Definir ODOO_PWD avant d'executer (creds dans Materiel TT.xlsx).")

uid = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
m_obj = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


def call(model, method, args, kw=None):
    return m_obj.execute_kw(DB, uid, PWD, model, method, args, kw or {})


ACC_499000 = 221          # suspense bancaire
ACC_440000 = 192          # fournisseurs
SDW_MAIN = 7040           # SD Worx Secretariat Social (SD ASBL) - porte les factures
SDW_ALL = [7040, 116212, 7368, 7422, 7384]

# virements en suspens a rattacher a SD Worx (les 2 premiers = ONSS en direct)
SUSPENS = [
    (19187, 25000.00, "Belfius 10/06 -- ONSS affiliation AA/1415989-50"),
    (19811,  8945.00, "ING 16/07 -- ONSS comm. ***116/5516/51214***"),
    (20136,   324.36, "ING 03/08 -- SD Worx ASBL, doc 8955275"),
    (20296,    96.80, "ING 10/08 -- SD Worx ASBL, doc 9022482"),
]
# lettrage cible : bsl_id -> nom de la piece a solder en priorite
CIBLE = {20136: "RESA1273", 20296: "RESA1272"}


def call_reconcile_safe(line_ids):
    """reconcile() renvoie None -> Fault de marshalling alors que le lettrage a eu lieu."""
    try:
        return True, call("account.move.line", "reconcile", [line_ids])
    except xmlrpc.client.Fault as f:
        low = str(f.faultString).lower()
        if "cannot marshal" in low or "marshaling" in low or "nonetype" in low:
            return True, "marshalling_false_fault_ignored"
        return False, str(f.faultString)


def get_bsl(bsl_id):
    r = call("account.bank.statement.line", "read", [[bsl_id]],
             {"fields": ["id", "date", "amount", "payment_ref", "is_reconciled", "move_id"]})
    if not r:
        return None
    b = r[0]
    mv = call("account.move", "read", [[b["move_id"][0]]], {"fields": ["state", "line_ids"]})[0]
    b["_state"] = mv["state"]
    b["_line_ids"] = mv["line_ids"]
    return b


def amls(ids, flds=None):
    if not ids:
        return []
    return call("account.move.line", "read", [ids],
                {"fields": flds or ["id", "account_id", "partner_id", "debit", "credit",
                                    "amount_residual", "reconciled", "move_name", "date",
                                    "date_maturity", "name"]})


print("=" * 100)
print("LETTRAGE SD WORX / ONSS -- 17/08/2026")
print("MODE " + ("DRY-RUN (aucune ecriture)" if DRY else "APPLY -- ECRITURE REELLE DANS ODOO"))
print("=" * 100)

# ------------------------------------------------------- 1. repointage suspens
print("\n[1] REPOINTAGE 499000 -> 440000 / SD Worx #%d" % SDW_MAIN)
pool_cible, pool_fifo = {}, []
for bsl_id, montant, label in SUSPENS:
    b = get_bsl(bsl_id)
    if not b:
        print(f"  BSL {bsl_id} INTROUVABLE -- skip"); continue
    if b["_state"] != "posted":
        print(f"  BSL {bsl_id} move state={b['_state']} -- skip"); continue
    lines = amls(b["_line_ids"])
    susp = next((l for l in lines if (l["account_id"] or [None])[0] == ACC_499000), None)
    deja = next((l for l in lines if (l["account_id"] or [None])[0] == ACC_440000), None)
    if susp is None and deja is None:
        print(f"  BSL {bsl_id} : ni 499000 ni 440000 -- skip"); continue
    if susp is None:
        print(f"  BSL {bsl_id} : deja sur 440000 (aml {deja['id']}) -- repointage saute")
        aml = deja
    elif DRY:
        print(f"  DRY  BSL {bsl_id} {montant:>10,.2f}  aml {susp['id']} -> 440000 / #{SDW_MAIN}   {label}")
        aml = susp
    else:
        call("account.move.line", "write",
             [[susp["id"]], {"account_id": ACC_440000, "partner_id": SDW_MAIN}])
        aml = amls([susp["id"]])[0]
        print(f"  OK   BSL {bsl_id} {montant:>10,.2f}  aml {aml['id']} repointee   {label}")
    if bsl_id in CIBLE:
        pool_cible[bsl_id] = (aml["id"], CIBLE[bsl_id], montant)
    else:
        pool_fifo.append(aml["id"])

# --------------------------------------------- 2. realignement partenaire debits
print("\n[2] REALIGNEMENT PARTENAIRE DES DEBITS SD WORX DEJA EN 440000")
debits = call("account.move.line", "search_read",
              [[["partner_id", "in", SDW_ALL], ["account_id", "=", ACC_440000],
                ["parent_state", "=", "posted"], ["full_reconcile_id", "=", False],
                ["amount_residual", ">", 0.005]]],
              {"fields": ["id", "date", "move_name", "partner_id", "amount_residual", "name"],
               "order": "date asc", "limit": 200})
for l in debits:
    pid = l["partner_id"][0]
    if pid != SDW_MAIN:
        if DRY:
            print(f"  DRY  aml {l['id']} {l['date']} {l['amount_residual']:>10,.2f} "
                  f"#{pid} -> #{SDW_MAIN}   {(l['name'] or '')[:44]}")
        else:
            call("account.move.line", "write", [[l["id"]], {"partner_id": SDW_MAIN}])
            print(f"  OK   aml {l['id']} {l['date']} {l['amount_residual']:>10,.2f} "
                  f"#{pid} -> #{SDW_MAIN}   {(l['name'] or '')[:44]}")
    else:
        print(f"  --   aml {l['id']} {l['date']} {l['amount_residual']:>10,.2f} deja #{SDW_MAIN}")
    if l["id"] not in [v[0] for v in pool_cible.values()]:
        pool_fifo.append(l["id"])

pool_fifo = list(dict.fromkeys(pool_fifo))
print(f"\n  Pool FIFO : {len(pool_fifo)} lignes de debit")

# ------------------------------------------------------------ 3. lettrage cible
print("\n[3] LETTRAGE CIBLE (communication portant un numero de facture)")
for bsl_id, (aml_id, piece, montant) in pool_cible.items():
    mv = call("account.move", "search_read", [[["name", "=", piece]]],
              {"fields": ["id", "name", "amount_residual", "partner_id"]})
    if not mv:
        print(f"  {piece} INTROUVABLE -- {montant:,.2f} bascule en FIFO")
        pool_fifo.append(aml_id); continue
    inv = mv[0]
    cred = call("account.move.line", "search_read",
                [[["move_id", "=", inv["id"]], ["account_id", "=", ACC_440000],
                  ["reconciled", "=", False]]],
                {"fields": ["id", "amount_residual"]})
    if not cred:
        print(f"  {piece} : aucune ligne 440000 ouverte -- {montant:,.2f} bascule en FIFO")
        pool_fifo.append(aml_id); continue
    print(f"  BSL {bsl_id} {montant:>9,.2f} -> {piece} (residuel {cred[0]['amount_residual']:,.2f})")
    if not DRY:
        ok, res = call_reconcile_safe([aml_id, cred[0]["id"]])
        print(f"       {'OK' if ok else 'ERREUR'} {res if not ok else ''}")

# ------------------------------------------------------------- 4. lettrage FIFO
print("\n[4] LETTRAGE FIFO SUR LES FACTURES LES PLUS ANCIENNES")
dettes = call("account.move.line", "search_read",
              [[["partner_id", "in", SDW_ALL], ["account_id", "=", ACC_440000],
                ["parent_state", "=", "posted"], ["full_reconcile_id", "=", False],
                ["amount_residual", "<", -0.005]]],
              {"fields": ["id", "date", "date_maturity", "move_name", "partner_id",
                          "amount_residual", "name"],
               "order": "date_maturity asc, date asc", "limit": 200})

dispo = sum(l["amount_residual"] for l in amls(pool_fifo)) if pool_fifo else 0.0
print(f"  Disponible a imputer : {dispo:,.2f} sur {len(dettes)} dettes ouvertes "
      f"({-sum(l['amount_residual'] for l in dettes):,.2f})\n")

reste = dispo
pool = [dict(id=l["id"], res=l["amount_residual"]) for l in amls(pool_fifo)]
soldees, partielles = [], []
for d in dettes:
    du = -d["amount_residual"]
    if reste <= 0.005:
        break
    if d["partner_id"][0] != SDW_MAIN and not DRY:
        call("account.move.line", "write", [[d["id"]], {"partner_id": SDW_MAIN}])
    pris = min(du, reste)
    statut = "SOLDEE" if pris >= du - 0.005 else f"PARTIELLE (reste {du - pris:,.2f})"
    print(f"  {d['date_maturity'] or d['date']:<12}{(d['move_name'] or '')[:12]:<14}"
          f"du {du:>11,.2f}   impute {pris:>11,.2f}   {statut}")
    (soldees if pris >= du - 0.005 else partielles).append((d["move_name"], pris))
    if not DRY:
        besoin = du
        for p in pool:
            if besoin <= 0.005:
                break
            if p["res"] <= 0.005:
                continue
            ok, res = call_reconcile_safe([p["id"], d["id"]])
            if not ok:
                print(f"       ERREUR reconcile aml {p['id']} <-> {d['id']} : {res}")
                continue
            cur = amls([p["id"], d["id"]])
            p["res"] = next(x["amount_residual"] for x in cur if x["id"] == p["id"])
            besoin = -next(x["amount_residual"] for x in cur if x["id"] == d["id"])
    reste -= pris

print("\n" + "=" * 100)
print("RECAPITULATIF")
print("=" * 100)
print(f"  Factures soldees   : {len(soldees)}  -> " + ", ".join(s[0] for s in soldees))
print(f"  Factures partielles: {len(partielles)} -> " + ", ".join(s[0] for s in partielles))
if not DRY:
    apres = call("account.move.line", "search_read",
                 [[["partner_id", "in", SDW_ALL], ["account_id", "=", ACC_440000],
                   ["parent_state", "=", "posted"], ["full_reconcile_id", "=", False],
                   ["amount_residual", "<", -0.005]]],
                 {"fields": ["amount_residual"], "limit": 200})
    print(f"  Encours SD Worx APRES lettrage : {-sum(l['amount_residual'] for l in apres):,.2f} EUR "
          f"sur {len(apres)} lignes")
else:
    print("  (dry-run : relancer avec --apply pour ecrire)")
