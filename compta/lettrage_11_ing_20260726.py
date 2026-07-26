# -*- coding: utf-8 -*-
"""
LETTRAGE ING 26/07/2026 -- lot complet paiements clients (54 credits non reconciliees au 26/07/26).
Methode reprise de compta/lettrage_09/10_ing.py (validee, cf LOG.md) avec 2 extensions demandees
par Nicolas pour ce lot :
  1. Matching automatique des lignes SANS partner_id sur BSL, via :
     a) IBAN de l'emetteur (res.partner.bank.acc_number) ;
     b) communication structuree belge (account.move.payment_reference, format +++XXX/XXXX/XXXXX+++) ;
     c) reference facture explicite (INV/2026/xxxxx, RINV/xx-xx/xxxx) citee dans le libelle.
  2. Tolerance d'ecart relevee a 5,00 EUR (au lieu de 1,00 EUR) pour le write-off 657100/757100,
     validee explicitement par Nicolas pour cette tache. Au-dela : lettrage partiel sans write-off
     (facture reste partiellement payee), jamais de lettrage a l'aveugle.
Plusieurs cas necessitent de netter la facture ouverte avec une note de credit (RINV) ou une
vieille ligne de credit deja existante sur le compte 400000 du meme partner pour retomber pile
sur le montant recu (cf. detail case par case ci-dessous, montants verifies manuellement avant
ecriture dans CASES).
Cas laisses de cote (non traites par ce script, cf compta/review/lettrage_ing_20260726_review.md) :
  - 8 lignes non-client (Baloise, Pluxee x2, Edenred, virements internes Teatower BNK2->BNK1 x4)
  - 7 lignes ambigues (aucun match fiable, ecart trop grand ou doublon possible)
"""
import xmlrpc.client
import os

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ["ODOO_PWD"]

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m_obj = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


def call(model, method, args, kw=None):
    return m_obj.execute_kw(DB, uid, PWD, model, method, args, kw or {})


ACC_499000 = 221
ACC_400000 = 162
ACC_657100 = 293
ACC_757100 = 347
JOURNAL_MISC = 11
TODAY = "2026-07-26"
ECART_TOLERANCE = 5.00

# Chaque case : bsl_ids (liste, generalement 1 -- 2 pour le cas Anais Michoel double paiement),
# docs = liste de move.name a matcher sur le compte 400000 (peut inclure une RINV en negatif),
# extra_line_ids = ids account.move.line supplementaires deja identifies (vieilles lignes de credit
# non liees a une facture nommee, ex. BNK1/25-26/xxxx), partner_id = partner a utiliser pour le
# repointage (issu de la ligne 400000 reelle de la/les facture(s), pas necessairement l'IBAN emetteur),
# allow_partial = True si ecart > tolerance accepte volontairement en lettrage partiel (pas de write-off).
CASES = [
    {"bsl_ids": [19708], "docs": ["INV/2026/02060"], "partner_id": 5509, "label": "Cafes Delahaut (Facturation)"},
    {"bsl_ids": [19709], "docs": ["INV/2026/03423"], "partner_id": 113445, "label": "D-trois SRL - Proxy Delhaize Saint-Severin"},
    {"bsl_ids": [19710], "docs": ["INV/2026/03007"], "partner_id": 7982, "label": "CPSP Belgie NV (Sunparks Kempense Meren)"},
    {"bsl_ids": [19712], "docs": ["INV/2026/02972"], "partner_id": 5509, "label": "Cafes Delahaut (Facturation)"},
    {"bsl_ids": [19713], "docs": ["INV/2026/03334"], "partner_id": 124727, "label": "Delhaize Montigny"},
    {"bsl_ids": [19727], "docs": ["INV/2026/03072", "RINV/25-26/0344"], "partner_id": 2811, "label": "BARVO SA - Carrefour Market Barvaux"},
    {"bsl_ids": [19740], "docs": ["INV/2026/03011"], "partner_id": 3245, "label": "Sorescol S.A."},
    {"bsl_ids": [19741], "docs": ["INV/2026/03066"], "partner_id": 3223, "label": "SRL AD LLN - Delhaize Louvain-La-Neuve"},
    {"bsl_ids": [19764], "docs": ["INV/2026/03519"], "partner_id": 3089, "label": "Les Tables Imaginaires - Restaurant Rosalie"},
    {"bsl_ids": [19767], "extra_line_ids": [191099], "docs": ["INV/2026/03083"], "partner_id": 117367, "label": "Ma Pharmacie de Baillonville - Bayet Sarah"},
    {"bsl_ids": [19772], "docs": ["INV/2026/03422"], "partner_id": 124572, "label": "Spar Clavier"},
    {"bsl_ids": [19774], "docs": ["INV/2026/03107"], "partner_id": 8792, "label": "AL RETAIL - Delhaize Boondael"},
    {"bsl_ids": [19776], "docs": ["INV/2026/03457"], "partner_id": 124638, "label": "Delhaize Vise"},
    {"bsl_ids": [19797], "extra_line_ids": [170921], "docs": ["INV/2026/02864"], "partner_id": 5736, "label": "NIVALIM - Intermarche Nivelles"},
    {"bsl_ids": [19798, 19799], "docs": ["INV/2026/03444", "INV/2026/03363"], "partner_id": 2789, "label": "Anais Michoel - Les p'tits pots (2 paiements / 2 factures)"},
    {"bsl_ids": [19800], "docs": ["INV/2026/02878"], "partner_id": 120495, "label": "SRL LEJER"},
    {"bsl_ids": [19814], "docs": ["INV/2026/03141"], "partner_id": 6596, "label": "Carrefour Belgium (SARUB)"},
    {"bsl_ids": [19833], "docs": ["INV/2026/02577"], "partner_id": 6596, "label": "Carrefour Belgium (SARUB)"},
    {"bsl_ids": [19834], "docs": ["INV/2026/03517"], "partner_id": 2832, "label": "Boulangerie Les Co'Pains SPRL"},
    {"bsl_ids": [19835], "docs": ["INV/2026/03448"], "partner_id": 3219, "label": "SPRL Durant-Rabaey"},
    {"bsl_ids": [19836], "docs": ["INV/2026/02555"], "partner_id": 5561, "label": "Chateau Thermes & Golf SA"},
    {"bsl_ids": [19837], "docs": ["INV/2026/03298"], "partner_id": 123966, "label": "Intermarche Mons"},
    {"bsl_ids": [19858], "extra_line_ids": [147783], "docs": ["INV/2026/02970"], "partner_id": 114763, "label": "Lillodis SRL - Proxy Delhaize Lillois"},
    {"bsl_ids": [19861], "docs": ["INV/2026/03523"], "partner_id": 123997, "label": "AD Delhaize Roodebeek"},
    {"bsl_ids": [19862], "docs": ["INV/2026/03277", "RINV/25-26/0363"], "partner_id": 7649, "label": "Delhaize Le Lion Affilie 048900 - Ad Spa"},
    {"bsl_ids": [19864], "docs": ["INV/2026/03555"], "partner_id": 124572, "label": "Spar Clavier"},
    {"bsl_ids": [19878], "docs": ["INV/2026/03543", "RINV/26-27/0010"], "partner_id": 7150, "label": "AD Delhaize Fernelmont (Fernel-Dis SRL)"},
    {"bsl_ids": [19884], "docs": ["INV/2026/03211"], "partner_id": 5733, "label": "DelEmbourg SRL - Delhaize Embourg"},
    {"bsl_ids": [19885], "docs": ["INV/2026/03223"], "partner_id": 2988, "label": "Ibis Namur Centre"},
    {"bsl_ids": [19886], "docs": ["INV/2026/03417"], "partner_id": 59995, "label": "Delhaize Bois-de-Breux"},
    {"bsl_ids": [19887], "docs": ["INV/2026/03049"], "partner_id": 123346, "label": "Gembloux Intermarche"},
    {"bsl_ids": [19911], "docs": ["INV/2026/02294"], "partner_id": 3132, "label": "Megan Houtvast (paiement PARTIEL, reste 200.00 EUR ouvert)", "allow_partial": True},
    {"bsl_ids": [19912], "docs": ["INV/2026/03152", "RINV/25-26/0353"], "partner_id": 8559, "label": "SA Marer - AD Delhaize Bastogne"},
    {"bsl_ids": [19913], "docs": ["INV/2026/03184"], "partner_id": 8160, "label": "N.B.S. RETAIL - Delhaize de Marche"},
    {"bsl_ids": [19930], "docs": ["INV/2026/03065", "RINV/25-26/0341"], "partner_id": 10134, "label": "LSL RETAIL - Intermarche Chaumont-Gistoux"},
    {"bsl_ids": [19933], "docs": ["INV/2026/03553"], "partner_id": 125325, "label": "Made in Louise"},
    {"bsl_ids": [19934], "docs": ["INV/2026/03055"], "partner_id": 5509, "label": "Cafes Delahaut (Facturation)"},
    {"bsl_ids": [19949], "docs": ["INV/2026/02968"], "partner_id": 122991, "label": "Antheco SA - Intermarche Anthee"},
]


def get_bsl(bsl_id):
    rows = call("account.bank.statement.line", "read", [[bsl_id]],
        {"fields": ["move_id", "is_reconciled", "amount", "partner_id", "payment_ref"]})
    if not rows:
        return None
    bsl = rows[0]
    mid = bsl["move_id"][0] if bsl.get("move_id") else None
    bsl["_move_id"] = mid
    if mid:
        mv = call("account.move", "read", [[mid]], {"fields": ["state", "name", "line_ids"]})
        bsl["_move_state"] = mv[0]["state"]
        bsl["_move_name"] = mv[0]["name"]
        bsl["_line_ids"] = mv[0]["line_ids"]
    return bsl


def get_move_lines(ids, fields=None):
    if not ids:
        return []
    flds = fields or ["id", "account_id", "partner_id", "debit", "credit", "amount_residual", "reconciled", "move_id"]
    return call("account.move.line", "read", [ids], {"fields": flds})


def find_suspense_line(line_ids):
    for ln in get_move_lines(line_ids):
        acc = ln["account_id"][0] if ln.get("account_id") else None
        if acc == ACC_499000:
            return ln
    return None


def get_doc(name):
    rows = call("account.move", "search_read", [[["name", "=", name]]],
        {"fields": ["id", "name", "payment_state", "amount_residual", "amount_total", "move_type"]})
    return rows[0] if rows else None


def find_open_receivable_lines(move_id):
    return call("account.move.line", "search_read",
        [[["move_id", "=", move_id], ["account_id", "=", ACC_400000], ["reconciled", "=", False]]],
        {"fields": ["id", "amount_residual", "debit", "credit", "reconciled"]})


def call_reconcile_safe(line_ids):
    try:
        res = call("account.move.line", "reconcile", [line_ids])
        return True, res
    except xmlrpc.client.Fault as f:
        msg = str(f.faultString)
        if "cannot marshal" in msg.lower() or "marshaling" in msg.lower() or "nonetype" in msg.lower():
            return True, "marshalling_false_fault_ignored"
        return False, msg


def create_writeoff(partner_id, amount_abs, debit_acc, credit_acc, label):
    vals = {
        "move_type": "entry",
        "journal_id": JOURNAL_MISC,
        "date": TODAY,
        "ref": f"Write-off ecart reglement lettrage ING 26/07 - {label}",
        "line_ids": [
            (0, 0, {"account_id": debit_acc, "partner_id": partner_id, "debit": round(amount_abs, 2), "credit": 0.0, "name": f"Ecart reglement {label}"}),
            (0, 0, {"account_id": credit_acc, "partner_id": partner_id, "debit": 0.0, "credit": round(amount_abs, 2), "name": f"Ecart reglement {label}"}),
        ],
    }
    mid = call("account.move", "create", [vals])
    call("account.move", "action_post", [[mid]])
    mv = call("account.move", "read", [[mid]], {"fields": ["name", "line_ids"]})
    return mid, mv[0]["line_ids"], mv[0]["name"]


def process_case(case):
    bsl_ids = case["bsl_ids"]
    docs = case["docs"]
    partner_id = case["partner_id"]
    label = case["label"]
    extra_line_ids = case.get("extra_line_ids", [])
    allow_partial = case.get("allow_partial", False)
    print("=" * 90)
    print(f"BSL {bsl_ids} -- {label} -- docs={docs} extra={extra_line_ids}")
    result = {"bsl_ids": bsl_ids, "label": label, "status": None, "error": None, "writeoff_move": None}

    bsl_aml_ids = []
    total_bsl_amount = 0.0
    bsl_names = []
    for bsl_id in bsl_ids:
        bsl = get_bsl(bsl_id)
        if not bsl:
            result["status"] = "ERROR"; result["error"] = f"BSL {bsl_id} introuvable"; print(" ERREUR:", result["error"]); return result
        if bsl["is_reconciled"]:
            print(f" BSL {bsl_id} deja reconciliee -- SKIP"); result["status"] = "SKIP_DEJA_RECONCILED"; return result
        if bsl.get("_move_state") != "posted":
            result["status"] = "ERROR"; result["error"] = f"BSL {bsl_id} move state={bsl.get('_move_state')}"; print(" ERREUR:", result["error"]); return result
        total_bsl_amount += bsl["amount"]
        bsl_names.append(bsl.get("_move_name"))
        susp = find_suspense_line(bsl.get("_line_ids", []))
        if not susp:
            lines_all = get_move_lines(bsl.get("_line_ids", []))
            already = [l for l in lines_all if l["account_id"][0] == ACC_400000]
            if not already:
                result["status"] = "ERROR"; result["error"] = f"BSL {bsl_id} : ligne 499000 introuvable et pas de 400000 non plus"
                print(" ERREUR:", result["error"]); return result
            bsl_recv = already[0]
            print(f" BSL {bsl_id} : ligne 400000 deja presente : id={bsl_recv['id']}")
        else:
            call("account.move.line", "write", [[susp["id"]], {"account_id": ACC_400000, "partner_id": partner_id}])
            print(f" BSL {bsl_id} : ligne suspense {susp['id']} repointee -> 400000 / partner {partner_id}")
            bsl_recv = get_move_lines([susp["id"]])[0]
        bsl_aml_ids.append(bsl_recv["id"])

    print(f" Total BSL amount={total_bsl_amount:.2f} moves={bsl_names}")

    doc_line_ids = []
    doc_infos = []
    total_docs_residual_signed = 0.0
    for dname in docs:
        d = get_doc(dname)
        if not d:
            result["status"] = "ERROR"; result["error"] = f"Doc {dname} introuvable"; print(" ERREUR:", result["error"]); return result
        if d["payment_state"] == "paid":
            print(f"   {dname} deja paid -- SKIP ce doc"); continue
        recv_lines = find_open_receivable_lines(d["id"])
        if not recv_lines:
            result["status"] = "ERROR"; result["error"] = f"Pas de ligne 400000 ouverte pour {dname}"
            print(" ERREUR:", result["error"]); return result
        for rl in recv_lines:
            doc_line_ids.append(rl["id"])
            total_docs_residual_signed += rl["amount_residual"]
        doc_infos.append((dname, d))
        print(f"   {dname} : type={d['move_type']} residual={d['amount_residual']:.2f} lines={[l['id'] for l in recv_lines]}")

    for eid in extra_line_ids:
        el = get_move_lines([eid])[0]
        doc_line_ids.append(eid)
        total_docs_residual_signed += el["amount_residual"]
        print(f"   extra line {eid} : residual={el['amount_residual']:.2f} (move {el['move_id']})")

    print(f" Total net docs (signe) = {total_docs_residual_signed:.2f} vs BSL recu = {total_bsl_amount:.2f}")
    ecart = round(total_bsl_amount - total_docs_residual_signed, 2)
    print(f" Ecart = BSL - docs = {ecart:+.2f}")

    if abs(ecart) > ECART_TOLERANCE and not allow_partial:
        result["status"] = "ERROR"; result["error"] = f"Ecart {ecart:+.2f} > tolerance {ECART_TOLERANCE} EUR et allow_partial non force -- ABANDON (verifier case)"
        print(" ERREUR:", result["error"]); return result

    matching_ids = bsl_aml_ids + doc_line_ids
    ok, res = call_reconcile_safe(matching_ids)
    if not ok:
        result["status"] = "ERROR"; result["error"] = f"reconcile() echoue: {res}"; print(" ERREUR:", result["error"]); return result
    print(f" reconcile({matching_ids}) -> OK ({res})")

    if allow_partial and abs(ecart) > ECART_TOLERANCE:
        print(f" Lettrage PARTIEL volontaire (ecart {ecart:+.2f} > {ECART_TOLERANCE}) -- pas de write-off, facture restera partiellement payee")
    elif abs(ecart) >= 0.005:
        ecart_abs = abs(ecart)
        if ecart < 0:
            debit_acc, credit_acc = ACC_657100, ACC_400000
            print(f" Ecart negatif -- write-off CHARGE 657100 {ecart_abs:.2f}")
        else:
            debit_acc, credit_acc = ACC_400000, ACC_757100
            print(f" Ecart positif -- write-off PRODUIT 757100 {ecart_abs:.2f}")
        wo_id, wo_lines, wo_name = create_writeoff(partner_id, ecart_abs, debit_acc, credit_acc, f"BSL{bsl_ids}/{label}")
        print(f" Write-off cree : {wo_name} (move_id={wo_id})")
        result["writeoff_move"] = wo_name
        wo_lines_data = get_move_lines(wo_lines)
        wo_400_line = [l for l in wo_lines_data if l["account_id"][0] == ACC_400000]
        if wo_400_line:
            wo_aml_id = wo_400_line[0]["id"]
            residual_open = call("account.move.line", "search_read",
                [[["id", "in", matching_ids], ["reconciled", "=", False]]],
                {"fields": ["id", "amount_residual"]})
            if residual_open:
                ids2 = [wo_aml_id] + [r["id"] for r in residual_open]
                ok2, res2 = call_reconcile_safe(ids2)
                if not ok2:
                    result["status"] = "ERROR"; result["error"] = f"reconcile write-off echoue: {res2}"
                    print(" ERREUR:", result["error"]); return result
                print(f" reconcile write-off ({ids2}) -> OK")
            else:
                print(" Aucune ligne residuelle ouverte trouvee -- verif finale")
    else:
        print(" Ecart nul -- pas de write-off")

    bsl_checks = [get_bsl(b) for b in bsl_ids]
    docs_check = [(dname, get_doc(dname)) for dname, _ in doc_infos]
    print(" --- VERIF FINALE ---")
    all_recon = True
    for bc in bsl_checks:
        print(f" BSL {bc.get('_move_name')} is_reconciled = {bc['is_reconciled']}")
        if not bc["is_reconciled"]:
            all_recon = False
    all_paid = True
    for dname, dcheck in docs_check:
        print(f" {dname} : payment_state={dcheck['payment_state']} residual={dcheck['amount_residual']:.2f}")
        if dcheck["payment_state"] not in ("paid", "reversed") and abs(dcheck["amount_residual"]) > 0.01 and not allow_partial:
            all_paid = False
    if all_recon and (all_paid or allow_partial):
        result["status"] = "OK"
        print(" RESULTAT: OK")
    elif result["status"] is None:
        result["status"] = "WARN"
        result["error"] = "BSL non reconciliee(s) ou doc(s) non solde(s) apres traitement"
        print(" RESULTAT: WARN --", result["error"])
    return result


if __name__ == "__main__":
    all_results = []
    for case in CASES:
        r = process_case(case)
        all_results.append(r)

    print("\n" + "=" * 90)
    print("RECAPITULATIF")
    print("=" * 90)
    for r in all_results:
        print(f" BSL {str(r['bsl_ids']):>14} | {r['label']:60} | status={r['status']:20} | wo={r.get('writeoff_move')} | err={r.get('error')}")
