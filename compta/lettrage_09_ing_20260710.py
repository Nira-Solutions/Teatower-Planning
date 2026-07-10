# -*- coding: utf-8 -*-
"""
LETTRAGE ING 10/07/2026 -- 9 credits clients identifies (6 exact/multi-doc-exact, 4 write-off <=1EUR)
Methode validee (LOG 02/07, lettrage_08_ecarts.py) :
  1. Repointer ligne suspense 499000 du move BSL -> 400000 + partner
  2. reconcile([bsl_line, doc_line(s) facture/avoir])
  3. Si ecart residuel <= 1,00 EUR : creer OD (MISC id=11) 657100 (charge, sous-paiement)
     ou 757100 (produit, sur-paiement), reconcilier avec le residu.

BUG XML-RPC CORRIGE (10/07/26, cf compta/LOG.md) :
  account.move.line.write() DOIT recevoir le dict de valeurs comme 2e element
  positionnel de `args` (call(model, 'write', [[ids], {vals}])), PAS en kwargs
  (call(model, 'write', [[ids]], {vals}) --> TypeError: write() got an
  unexpected keyword argument). Le narratif precedent "Odoo 18 verrouille
  l'ecriture via XML-RPC" (lettrage_08_ecarts.py, rapport 03/06) etait FAUX --
  c'etait ce bug de syntaxe d'appel. Ce script est idempotent : si une BSL est
  deja reconciliee il la skip proprement (relancable sans risque).

Ce script est un ARCHIVE/TEMPLATE reutilisable, deja execute en production le
10/07/26 (9/9 cas OK, cf compta/LOG.md pour le detail chiffre). Le cas
Carrefour Belgium SARUB (BSL 19476, 4 documents nettes) a necessite un
write-off complementaire de 0,37 EUR cree manuellement le jour meme, car le
calcul d'ecart contenait un bug de signe desormais corrige ci-dessous
(amount_residual d'account.move.line est deja signe -- ne PAS le multiplier
par +1/-1 selon move_type, sous peine de double-inverser le signe des avoirs).
"""
import xmlrpc.client
import sys

import os

URL  = "https://tea-tree.odoo.com"
DB   = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD  = os.environ.get("ODOO_PWD")  # repo public -- jamais de mot de passe en clair, cf reference_credentials_materiel_tt
if not PWD:
    raise SystemExit("Definir la variable d'environnement ODOO_PWD avant d'executer ce script (creds dans Materiel TT.xlsx).")

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid    = common.authenticate(DB, USER, PWD, {})
m_obj  = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def call(model, method, args, kw=None):
    return m_obj.execute_kw(DB, uid, PWD, model, method, args, kw or {})

def p(*a):
    print(" ".join(str(x) for x in a))

ACC_499000 = 221
ACC_400000 = 162
ACC_657100 = 293   # Negative Payment Differences (client a sous-paye)
ACC_757100 = 347   # Positive Payment Differences (client a surpaye)
JOURNAL_MISC = 11
TODAY = "2026-07-10"

CASES = [
    {'bsl_id': 19550, 'docs': ['INV/2026/02882'], 'partner_id': 115618, 'label': 'La guinguette du Merry'},
    {'bsl_id': 19620, 'docs': ['INV/2026/02978'], 'partner_id': 60096, 'label': 'Maison de Repos Libert (via CPAS Marche-Famenne)'},
    {'bsl_id': 19622, 'docs': ['INV/2026/03309'], 'partner_id': 5625, 'label': 'Ramaut / Ramhoreca SA'},
    {'bsl_id': 19635, 'docs': ['INV/2026/03405'], 'partner_id': 7440, 'label': 'Cafermi'},
    {'bsl_id': 19478, 'docs': ['INV/2026/02907', 'RINV/25-26/0358'], 'partner_id': 8159, 'label': 'N.B.S. RETAIL - Delhaize de Marche'},
    {'bsl_id': 19487, 'docs': ['INV/2026/02740'], 'partner_id': 2899, 'label': 'Cotes Aromes - Francois CHLEIDE'},
    {'bsl_id': 19549, 'docs': ['INV/2026/02868'], 'partner_id': 2982, 'label': 'Helene BERTRAND'},
    {'bsl_id': 19609, 'docs': ['INV/2026/03231'], 'partner_id': 123845, 'label': 'Louis Delhaize - Haversin (paiement CYANAR)'},
    {'bsl_id': 19476, 'docs': ['INV/2026/02753', 'INV/2026/02865', 'RINV/25-26/0254', 'RINV/25-26/0257'], 'partner_id': 6596, 'label': 'Carrefour Belgium SARUB'},
]


def get_bsl(bsl_id):
    rows = call('account.bank.statement.line', 'read', [[bsl_id]],
        {'fields': ['move_id', 'is_reconciled', 'amount', 'partner_id', 'payment_ref']})
    if not rows:
        return None
    bsl = rows[0]
    mid = bsl['move_id'][0] if bsl.get('move_id') else None
    bsl['_move_id'] = mid
    if mid:
        mv = call('account.move', 'read', [[mid]], {'fields': ['state', 'name', 'line_ids']})
        bsl['_move_state'] = mv[0]['state']
        bsl['_move_name'] = mv[0]['name']
        bsl['_line_ids'] = mv[0]['line_ids']
    return bsl


def get_move_lines(ids, fields=None):
    if not ids:
        return []
    flds = fields or ['id', 'account_id', 'partner_id', 'debit', 'credit', 'amount_residual', 'reconciled', 'move_id']
    return call('account.move.line', 'read', [ids], {'fields': flds})


def find_suspense_line(line_ids):
    for ln in get_move_lines(line_ids):
        acc = ln['account_id'][0] if ln.get('account_id') else None
        if acc == ACC_499000:
            return ln
    return None


def get_doc(name):
    rows = call('account.move', 'search_read', [[['name', '=', name]]],
        {'fields': ['id', 'name', 'payment_state', 'amount_residual', 'amount_total', 'move_type']})
    return rows[0] if rows else None


def find_open_receivable_lines(move_id):
    return call('account.move.line', 'search_read',
        [[['move_id', '=', move_id], ['account_id', '=', ACC_400000], ['reconciled', '=', False]]],
        {'fields': ['id', 'amount_residual', 'debit', 'credit', 'reconciled']})


def call_reconcile_safe(line_ids):
    try:
        res = call('account.move.line', 'reconcile', [line_ids])
        return True, res
    except xmlrpc.client.Fault as f:
        msg = str(f.faultString)
        if 'cannot marshal' in msg.lower() or 'marshaling' in msg.lower() or 'nonetype' in msg.lower():
            return True, 'marshalling_false_fault_ignored'
        return False, msg


def create_writeoff(partner_id, amount_abs, debit_acc, credit_acc, label):
    vals = {
        'move_type': 'entry',
        'journal_id': JOURNAL_MISC,
        'date': TODAY,
        'ref': f"Write-off ecart reglement lettrage ING 10/07 - {label}",
        'line_ids': [
            (0, 0, {'account_id': debit_acc, 'partner_id': partner_id, 'debit': round(amount_abs, 2), 'credit': 0.0, 'name': f"Ecart reglement {label}"}),
            (0, 0, {'account_id': credit_acc, 'partner_id': partner_id, 'debit': 0.0, 'credit': round(amount_abs, 2), 'name': f"Ecart reglement {label}"}),
        ],
    }
    mid = call('account.move', 'create', [vals])
    call('account.move', 'action_post', [[mid]])
    mv = call('account.move', 'read', [[mid]], {'fields': ['name', 'line_ids']})
    return mid, mv[0]['line_ids'], mv[0]['name']


def process_case(case):
    bsl_id = case['bsl_id']
    docs = case['docs']
    partner_id = case['partner_id']
    label = case['label']

    p("=" * 90)
    p(f"BSL {bsl_id} -- {label} -- docs={docs}")
    p("=" * 90)

    result = {'bsl_id': bsl_id, 'label': label, 'status': None, 'error': None, 'writeoff_move': None}

    bsl = get_bsl(bsl_id)
    if not bsl:
        result['status'] = 'ERROR'; result['error'] = 'BSL introuvable'
        p("  ERREUR:", result['error']); return result
    if bsl['is_reconciled']:
        p("  BSL deja reconciliee -- SKIP")
        result['status'] = 'SKIP_DEJA_RECONCILED'; return result
    if bsl.get('_move_state') != 'posted':
        result['status'] = 'ERROR'; result['error'] = f"move state={bsl.get('_move_state')}"
        p("  ERREUR:", result['error']); return result

    bsl_amount = bsl['amount']
    p(f"  BSL amount={bsl_amount:.2f} move={bsl.get('_move_name')}")

    # 1) repointer suspense -> 400000 + partner
    susp = find_suspense_line(bsl.get('_line_ids', []))
    if not susp:
        # peut-etre deja repointee
        lines_all = get_move_lines(bsl.get('_line_ids', []))
        already = [l for l in lines_all if l['account_id'][0] == ACC_400000]
        if not already:
            result['status'] = 'ERROR'; result['error'] = 'Ligne 499000 introuvable et pas de 400000 non plus'
            p("  ERREUR:", result['error']); return result
        bsl_recv = already[0]
        p(f"  Ligne 400000 deja presente sur BSL : id={bsl_recv['id']}")
    else:
        # IMPORTANT : vals dict en 2e element POSITIONNEL de args, pas en kwargs.
        call('account.move.line', 'write', [[susp['id']], {'account_id': ACC_400000, 'partner_id': partner_id}])
        p(f"  Ligne suspense {susp['id']} repointee -> 400000 / partner {partner_id}")
        bsl_recv = get_move_lines([susp['id']])[0]

    bsl_aml_id = bsl_recv['id']

    # 2) recuperer lignes receivable ouvertes des docs
    doc_line_ids = []
    doc_infos = []
    total_docs_residual_signed = 0.0
    for dname in docs:
        d = get_doc(dname)
        if not d:
            result['status'] = 'ERROR'; result['error'] = f"Doc {dname} introuvable"
            p("  ERREUR:", result['error']); return result
        if d['payment_state'] == 'paid':
            p(f"    {dname} deja paid -- SKIP ce doc")
            continue
        recv_lines = find_open_receivable_lines(d['id'])
        if not recv_lines:
            result['status'] = 'ERROR'; result['error'] = f"Pas de ligne 400000 ouverte pour {dname}"
            p("  ERREUR:", result['error']); return result
        for rl in recv_lines:
            doc_line_ids.append(rl['id'])
            # NB : account.move.line.amount_residual est deja signe selon debit/credit
            # (positif pour une facture, negatif pour un avoir) -- PAS besoin de multiplier
            # par un signe base sur move_type (bug corrige le 10/07, cf compta/LOG.md).
            total_docs_residual_signed += rl['amount_residual']
        doc_infos.append((dname, d))
        p(f"    {dname} : type={d['move_type']} residual={d['amount_residual']:.2f} lines={[l['id'] for l in recv_lines]}")

    p(f"  Total net docs (signe) = {total_docs_residual_signed:.2f} vs BSL recu = {bsl_amount:.2f}")
    ecart = round(bsl_amount - total_docs_residual_signed, 2)
    p(f"  Ecart = BSL - docs = {ecart:+.2f}")

    # 3) reconcile groupe
    matching_ids = [bsl_aml_id] + doc_line_ids
    ok, res = call_reconcile_safe(matching_ids)
    if not ok:
        result['status'] = 'ERROR'; result['error'] = f"reconcile() echoue: {res}"
        p("  ERREUR:", result['error']); return result
    p(f"  reconcile({matching_ids}) -> OK ({res})")

    # 4) write-off si ecart residuel
    if abs(ecart) >= 0.005:
        ecart_abs = abs(ecart)
        if ecart_abs > 1.00:
            result['status'] = 'WARN_ECART_TROP_GRAND'
            result['error'] = f"Ecart {ecart:+.2f} > 1.00 EUR -- pas de write-off force"
            p("  ATTENTION:", result['error'])
        else:
            if ecart < 0:
                # BSL < docs nets : client a sous-paye -> charge 657100 debit / 400000 credit
                debit_acc, credit_acc = ACC_657100, ACC_400000
                p(f"  Ecart negatif -- write-off CHARGE 657100 {ecart_abs:.2f}")
            else:
                # BSL > docs nets : client a surpaye -> 400000 debit / 757100 credit
                debit_acc, credit_acc = ACC_400000, ACC_757100
                p(f"  Ecart positif -- write-off PRODUIT 757100 {ecart_abs:.2f}")

            wo_id, wo_lines, wo_name = create_writeoff(partner_id, ecart_abs, debit_acc, credit_acc, f"BSL{bsl_id}/{label}")
            p(f"  Write-off cree : {wo_name} (move_id={wo_id})")
            result['writeoff_move'] = wo_name

            # reconcilier la ligne 400000 du write-off avec le residu restant
            wo_lines_data = get_move_lines(wo_lines)
            wo_400_line = [l for l in wo_lines_data if l['account_id'][0] == ACC_400000]
            if wo_400_line:
                wo_aml_id = wo_400_line[0]['id']
                residual_open = call('account.move.line', 'search_read',
                    [[['id', 'in', matching_ids], ['reconciled', '=', False]]],
                    {'fields': ['id', 'amount_residual']})
                if residual_open:
                    ids2 = [wo_aml_id] + [r['id'] for r in residual_open]
                    ok2, res2 = call_reconcile_safe(ids2)
                    if not ok2:
                        result['status'] = 'ERROR'; result['error'] = f"reconcile write-off echoue: {res2}"
                        p("  ERREUR:", result['error']); return result
                    p(f"  reconcile write-off ({ids2}) -> OK")
                else:
                    p("  Aucune ligne residuelle ouverte trouvee (peut-etre deja soldee) -- verif finale")
    else:
        p("  Ecart nul -- pas de write-off")

    # 5) verif finale
    bsl_check = get_bsl(bsl_id)
    docs_check = [(dname, get_doc(dname)) for dname, _ in doc_infos]
    p("  --- VERIF FINALE ---")
    p(f"  BSL.is_reconciled = {bsl_check['is_reconciled']}")
    all_paid = True
    for dname, dcheck in docs_check:
        p(f"  {dname} : payment_state={dcheck['payment_state']} residual={dcheck['amount_residual']:.2f}")
        if dcheck['payment_state'] not in ('paid', 'reversed') and abs(dcheck['amount_residual']) > 0.01:
            all_paid = False

    if bsl_check['is_reconciled'] and all_paid:
        result['status'] = 'OK'
        p("  RESULTAT: OK")
    elif result['status'] is None:
        result['status'] = 'WARN'
        result['error'] = 'BSL non reconciliee ou doc(s) non solde(s) apres traitement'
        p("  RESULTAT: WARN --", result['error'])

    return result


if __name__ == '__main__':
    p("LETTRAGE ING 10/07/2026 -- 9 CAS")
    all_results = []
    for case in CASES:
        r = process_case(case)
        all_results.append(r)

    p("\n" + "=" * 90)
    p("RECAPITULATIF")
    p("=" * 90)
    for r in all_results:
        p(f"  BSL {r['bsl_id']:>6} | {r['label']:45} | status={r['status']:20} | wo={r.get('writeoff_move')} | err={r.get('error')}")
