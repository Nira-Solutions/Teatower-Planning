"""
ÉTAPE 5 — APPLY LETTRAGE BANCAIRE ING (version finale — 18 lignes cibles)
Journal : ING BE30 3631 6408 2311
Date    : 2026-06-03

CORRECTIONS v5 :
  1. Faux-échec marshalling XML-RPC : si reconcile() lève une exception contenant
     "cannot marshal" (ou tout Fault), on ré-interroge Odoo pour décider OK/ERROR.
  2. Skip des BSL déjà is_reconciled=True avant tout traitement.
  3. MATCH_ECART_CENTS : write-off via ligne supplémentaire sur le move de la BSL
     (avant reconcile) pour équilibrer l'écart → facture payment_state=paid garanti.
     Test sur 1 seule ligne (SA Barthe) avant les 5 autres.
     Fallback : account.payment.register si ajout de ligne refusé.
  4. VENDOR_BILL_MATCH : même mécanique côté fournisseur (suspense→440000+partner).
  5. Ordre : MATCH_EXACT (5) → VENDOR_BILL (7) → ECART_CENTS (6).
     Auto-vérification (is_reconciled + payment_state) ligne par ligne.
     Récap final complet.

FLAGS :
  DRY_RUN    = False  → mode apply (True = lecture seule)
  LIMIT_TEST = None   → traitement complet (mettre un entier pour tester N lignes)
"""

import xmlrpc.client
import re
from collections import defaultdict
from itertools import combinations
from datetime import date, datetime

# ══════════════════════════════════════════════════════════════════════════════
# FLAGS OPÉRATIONNELS
# ══════════════════════════════════════════════════════════════════════════════
DRY_RUN    = False   # False = applique les écritures
LIMIT_TEST = None    # None = traitement complet des 18 lignes

WRITE_OFF_SEUIL = 0.05  # EUR — seuil max écart absorbable

# ══════════════════════════════════════════════════════════════════════════════
# CONNEXION
# ══════════════════════════════════════════════════════════════════════════════
URL  = "https://tea-tree.odoo.com"
DB   = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD  = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid    = common.authenticate(DB, USER, PWD, {})
m_obj  = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def call(model, method, args, kw=None):
    return m_obj.execute_kw(DB, uid, PWD, model, method, args, kw or {})

# ══════════════════════════════════════════════════════════════════════════════
# COMPTE WRITE-OFF (657000) et FOURNISSEUR PAYABLE (440000)
# ══════════════════════════════════════════════════════════════════════════════
# Détecté dynamiquement ci-dessous ; ces valeurs sont des fallbacks si
# la détection échoue — adapter si le plan comptable diffère.
WRITEOFF_CODE_BSL_LT_INV = '657'   # BSL encaissé < montant facture → charge financière
WRITEOFF_CODE_BSL_GT_INV = '757'   # BSL encaissé > montant facture → produit financier
PAYABLE_ACCOUNT_CODE     = '440'   # 440xxx = fournisseurs

print("=" * 72)
print(f"LETTRAGE ING — {'DRY-RUN (LECTURE SEULE)' if DRY_RUN else 'APPLY MODE FINAL'}")
print(f"Date : {date.today()} | Seuil write-off : {WRITE_OFF_SEUIL:.2f} EUR")
if not DRY_RUN:
    print(f"LIMIT_TEST : {LIMIT_TEST if LIMIT_TEST else 'ILLIMITE — TRAITEMENT COMPLET (18 lignes)'}")
print("=" * 72)

# ══════════════════════════════════════════════════════════════════════════════
# 0. JOURNAL ING
# ══════════════════════════════════════════════════════════════════════════════
print("\n[0] Recherche journal ING ...")
journals = call('account.journal', 'search_read',
    [[['type', '=', 'bank']]],
    {'fields': ['id', 'name', 'bank_account_id', 'code', 'suspense_account_id']}
)

ing_journal = None
for j in journals:
    name_lower = (j.get('name') or '').lower()
    if 'ing' in name_lower or '3631' in name_lower or 'be30' in name_lower:
        ing_journal = j
        break

if not ing_journal:
    for j in journals:
        ba = j.get('bank_account_id')
        if ba and ('3631' in str(ba) or 'ING' in str(ba).upper()):
            ing_journal = j
            break

if not ing_journal:
    print("  ATTENTION : journal ING non identifié. Journaux disponibles :")
    for j in journals:
        print(f"    id={j['id']:4d} | code={j['code']:10s} | {j['name']}")
    journal_filter = []
    ing_journal_id = None
else:
    ing_journal_id = ing_journal['id']
    print(f"  Journal ING : id={ing_journal_id} | {ing_journal['name']} ({ing_journal['code']})")
    journal_filter = [['journal_id', '=', ing_journal_id]]

# Compte suspense du journal ING
ING_SUSPENSE_ACC_ID = None
if ing_journal and ing_journal.get('suspense_account_id'):
    ING_SUSPENSE_ACC_ID = ing_journal['suspense_account_id'][0]
    print(f"  Compte suspense ING : id={ING_SUSPENSE_ACC_ID} — {ing_journal['suspense_account_id'][1]}")

# ══════════════════════════════════════════════════════════════════════════════
# 0b. COMPTES WRITE-OFF ET PAYABLE
# ══════════════════════════════════════════════════════════════════════════════
print("\n[0b] Détection comptes write-off et payable ...")

def find_account_by_code_prefix(prefix, limit=1):
    """Retourne le premier compte dont le code commence par `prefix`."""
    accs = call('account.account', 'search_read',
        [[['code', 'like', prefix + '%'], ['deprecated', '=', False]]],
        {'fields': ['id', 'name', 'code'], 'limit': limit}
    )
    return accs[0] if accs else None

writeoff_debit_acc  = find_account_by_code_prefix(WRITEOFF_CODE_BSL_LT_INV)   # 657 = charges financières
writeoff_credit_acc = find_account_by_code_prefix(WRITEOFF_CODE_BSL_GT_INV)   # 757 = produits financiers
payable_acc         = find_account_by_code_prefix(PAYABLE_ACCOUNT_CODE)        # 440 = fournisseurs

if writeoff_debit_acc:
    print(f"  Write-off débit  (BSL<INV) : {writeoff_debit_acc['code']} {writeoff_debit_acc['name']} id={writeoff_debit_acc['id']}")
else:
    print(f"  ATTENTION : compte write-off débit ({WRITEOFF_CODE_BSL_LT_INV}xxx) non trouvé")

if writeoff_credit_acc:
    print(f"  Write-off crédit (BSL>INV) : {writeoff_credit_acc['code']} {writeoff_credit_acc['name']} id={writeoff_credit_acc['id']}")
else:
    print(f"  ATTENTION : compte write-off crédit ({WRITEOFF_CODE_BSL_GT_INV}xxx) non trouvé")

if payable_acc:
    print(f"  Compte payable   (440xxx)  : {payable_acc['code']} {payable_acc['name']} id={payable_acc['id']}")
else:
    print(f"  ATTENTION : compte payable ({PAYABLE_ACCOUNT_CODE}xxx) non trouvé")

# ══════════════════════════════════════════════════════════════════════════════
# 1. BANK STATEMENT LINES — FILTRÉES (skip déjà réconciliées)
# ══════════════════════════════════════════════════════════════════════════════
print("\n[1] Chargement BSL non réconciliées ...")

domain_bsl = [['is_reconciled', '=', False]] + journal_filter
bsl_all = call('account.bank.statement.line', 'search_read',
    [domain_bsl],
    {'fields': ['id', 'date', 'payment_ref', 'amount', 'partner_id',
                'journal_id', 'narration', 'transaction_type',
                'partner_name', 'move_id'],
     'limit': 2000}
)

bsl_entrees = [l for l in bsl_all if l['amount'] > 0]
bsl_sorties = [l for l in bsl_all if l['amount'] < 0]

print(f"  Total non réconciliées : {len(bsl_all)}")
print(f"    Encaissements (>0)   : {len(bsl_entrees)}")
print(f"    Décaissements (<0)   : {len(bsl_sorties)}")

# ══════════════════════════════════════════════════════════════════════════════
# 2. FACTURES CLIENTS OUVERTES
# ══════════════════════════════════════════════════════════════════════════════
print("\n[2] Chargement factures clients ouvertes ...")

inv_open = call('account.move', 'search_read',
    [[['move_type', '=', 'out_invoice'],
      ['state', '=', 'posted'],
      ['payment_state', 'in', ['not_paid', 'partial']]]],
    {'fields': ['id', 'name', 'partner_id', 'amount_residual',
                'invoice_date_due', 'invoice_date',
                'payment_reference', 'ref', 'invoice_origin'],
     'limit': 5000}
)
print(f"  Factures clients ouvertes : {len(inv_open)}")

inv_by_amount      = defaultdict(list)
inv_by_amt_partner = defaultdict(list)
inv_by_partner     = defaultdict(list)
inv_by_struct      = {}

RE_STRUCT = re.compile(r'\+\+\+(\d{3})[/ ]?(\d{4})[/ ]?(\d{5})\+\+\+')

def extract_struct_ref(text):
    if not text:
        return None
    m2 = RE_STRUCT.search(text)
    if m2:
        return f"+++{m2.group(1)}/{m2.group(2)}/{m2.group(3)}+++"
    return None

def normalize_struct(ref):
    if not ref:
        return None
    digits = re.sub(r'[^0-9]', '', ref)
    return digits if len(digits) == 12 else None

for inv in inv_open:
    amt = round(inv['amount_residual'], 2)
    pid = inv['partner_id'][0] if inv['partner_id'] else 0
    inv_by_amount[amt].append(inv)
    inv_by_amt_partner[(amt, pid)].append(inv)
    inv_by_partner[pid].append(inv)
    for field in ['payment_reference', 'name', 'ref']:
        raw = inv.get(field) or ''
        norm = normalize_struct(raw)
        if norm:
            inv_by_struct[norm] = inv
            break
    for field in ['payment_reference', 'ref']:
        raw = inv.get(field) or ''
        extracted = extract_struct_ref(raw)
        if extracted:
            norm = normalize_struct(extracted)
            if norm and norm not in inv_by_struct:
                inv_by_struct[norm] = inv

# ══════════════════════════════════════════════════════════════════════════════
# 3. FACTURES FOURNISSEURS OUVERTES
# ══════════════════════════════════════════════════════════════════════════════
print("\n[3] Chargement factures fournisseurs ouvertes ...")

vbill_open = call('account.move', 'search_read',
    [[['move_type', '=', 'in_invoice'],
      ['state', '=', 'posted'],
      ['payment_state', 'in', ['not_paid', 'partial']]]],
    {'fields': ['id', 'name', 'partner_id', 'amount_residual',
                'invoice_date_due', 'ref'],
     'limit': 5000}
)
print(f"  Factures fournisseurs ouvertes : {len(vbill_open)}")

vbill_by_amount = defaultdict(list)
for vb in vbill_open:
    amt = round(vb['amount_residual'], 2)
    vbill_by_amount[amt].append(vb)

# ══════════════════════════════════════════════════════════════════════════════
# 4. P4 : COMBINAISONS DE FACTURES (même partenaire)
# ══════════════════════════════════════════════════════════════════════════════
def find_invoice_combination(partner_id, target_amount, invoices_for_partner):
    if not invoices_for_partner or len(invoices_for_partner) < 2:
        return None, None
    invs   = invoices_for_partner[:8]
    amounts = [round(inv['amount_residual'], 2) for inv in invs]
    matching_combos = []
    for r in range(2, len(invs) + 1):
        for combo_indices in combinations(range(len(invs)), r):
            combo_sum = round(sum(amounts[i] for i in combo_indices), 2)
            ecart = round(abs(target_amount - combo_sum), 2)
            if ecart <= WRITE_OFF_SEUIL:
                combo_invs = [invs[i] for i in combo_indices]
                matching_combos.append((combo_invs, ecart))
        if len(matching_combos) > 1:
            return 'MULTI', None
    if len(matching_combos) == 1:
        return matching_combos[0][0], matching_combos[0][1]
    return None, None

# ══════════════════════════════════════════════════════════════════════════════
# 5. EXCLUSIONS
# ══════════════════════════════════════════════════════════════════════════════
EXCLU_KEYWORDS = [
    'edenred', 'monizze', 'eps monizze', 'pluxee', 'sodexo cheques',
    'smartbox', 'amazon payments', 'amazon marketplace', 'faire ', 'faire.com',
    'nira solutions', 'tilman', 'vilna gaon',
    'sd worx', 'sdworx',
    'cpas', 'bpost', 'bnb ', 'banque nationale',
]

def is_exclu_non_facture(bsl):
    ref = ((bsl.get('payment_ref') or '') + ' ' + (bsl.get('narration') or '')).lower()
    partner_name = (bsl.get('partner_name') or '').lower()
    if bsl.get('partner_id'):
        partner_name = bsl['partner_id'][1].lower()
    combined = ref + ' ' + partner_name
    for kw in EXCLU_KEYWORDS:
        if kw.lower() in combined:
            return True, kw
    return False, None

# ══════════════════════════════════════════════════════════════════════════════
# 6. MATCHING ENCAISSEMENTS (P0→P4)
# ══════════════════════════════════════════════════════════════════════════════
print("\n[4] Matching encaissements ...")

results_entrees = {
    'EXCLU_NON_FACTURE': [],
    'MATCH_EXACT':       [],
    'MATCH_ECART_CENTS': [],
    'MATCH_COMBO':       [],
    'MATCH_COMBO_ECART': [],
    'MATCH_PARTIEL':     [],
    'MULTI_CANDIDATS':   [],
    'AUCUN_MATCH':       [],
}

for bsl in bsl_entrees:
    amt           = round(bsl['amount'], 2)
    pid           = bsl['partner_id'][0] if bsl['partner_id'] else 0
    pay_ref       = bsl.get('payment_ref') or ''
    narration     = bsl.get('narration') or ''
    combined      = pay_ref + ' ' + narration
    partner_disp  = (bsl['partner_id'][1] if bsl['partner_id']
                     else bsl.get('partner_name') or 'INCONNU')

    exclu, exclu_kw = is_exclu_non_facture(bsl)
    if exclu:
        results_entrees['EXCLU_NON_FACTURE'].append({
            'bsl_id': bsl['id'], 'date': bsl['date'],
            'payment_ref': pay_ref[:60], 'amount': amt,
            'partner': partner_disp, 'exclu_kw': exclu_kw,
        })
        continue

    best_match  = None
    match_type  = None
    match_prio  = None
    match_ecart = 0.0
    candidates  = []

    # P1 : ref structurée
    struct_norm = normalize_struct(extract_struct_ref(combined))
    if not struct_norm:
        struct_norm = normalize_struct(combined.strip())
    if struct_norm and struct_norm in inv_by_struct:
        inv_c = inv_by_struct[struct_norm]
        inv_amt = round(inv_c['amount_residual'], 2)
        ecart = abs(amt - inv_amt)
        if ecart == 0.0:
            best_match, match_type, match_prio, match_ecart = inv_c, 'MATCH_EXACT', 'P1_STRUCT', 0.0
        elif ecart <= WRITE_OFF_SEUIL:
            best_match, match_type, match_prio, match_ecart = inv_c, 'MATCH_ECART_CENTS', 'P1_STRUCT_ECART', round(amt - inv_amt, 2)
        elif amt < inv_amt:
            best_match, match_type, match_prio = inv_c, 'MATCH_PARTIEL', 'P1_STRUCT_PARTIEL'
        else:
            candidates.append(('P1_STRUCT_TROP_PERCU', inv_c))

    # P2 : montant exact + partner
    if best_match is None and pid:
        key = (amt, pid)
        if key in inv_by_amt_partner:
            cands = inv_by_amt_partner[key]
            if len(cands) == 1:
                best_match, match_type, match_prio, match_ecart = cands[0], 'MATCH_EXACT', 'P2_AMT_PARTNER', 0.0
            else:
                candidates.extend([('P2_AMT_PARTNER_MULTI', c) for c in cands])

    # P2b : montant ±0,05 € + partner
    if best_match is None and pid and not candidates:
        for delta in [0.01, 0.02, 0.03, 0.04, 0.05]:
            for sign in [1, -1]:
                test_amt = round(amt + sign * delta, 2)
                key = (test_amt, pid)
                if key in inv_by_amt_partner:
                    cands = inv_by_amt_partner[key]
                    if len(cands) == 1:
                        best_match  = cands[0]
                        match_type  = 'MATCH_ECART_CENTS'
                        match_prio  = f'P2b_ECART_{abs(amt-test_amt):.2f}'
                        match_ecart = round(amt - test_amt, 2)
                        break
            if best_match:
                break

    # P3 : montant exact, un candidat global
    if best_match is None and not candidates:
        if amt in inv_by_amount:
            cands = inv_by_amount[amt]
            if len(cands) == 1:
                best_match, match_type, match_prio, match_ecart = cands[0], 'MATCH_EXACT', 'P3_AMT_UNIQUE', 0.0
            else:
                candidates.extend([('P3_AMT_MULTI', c) for c in cands])

    # P3b : montant approché, unique candidat global
    if best_match is None and not candidates:
        for delta in [0.01, 0.02, 0.03, 0.04, 0.05]:
            for sign in [1, -1]:
                test_amt = round(amt + sign * delta, 2)
                if test_amt in inv_by_amount:
                    cands = inv_by_amount[test_amt]
                    if len(cands) == 1:
                        best_match  = cands[0]
                        match_type  = 'MATCH_ECART_CENTS'
                        match_prio  = f'P3b_ECART_{abs(amt-test_amt):.2f}'
                        match_ecart = round(amt - test_amt, 2)
                        break
            if best_match:
                break

    # P4 : combinaisons multi-factures même partenaire
    if best_match is None and not candidates and pid:
        partner_invs = inv_by_partner.get(pid, [])
        combo_result, combo_ecart = find_invoice_combination(pid, amt, partner_invs)
        if combo_result == 'MULTI':
            candidates.append(('P4_COMBO_MULTI', None))
        elif combo_result is not None:
            ecart_abs  = combo_ecart if combo_ecart is not None else 0.0
            combo_type = 'MATCH_COMBO_ECART' if ecart_abs > 0 else 'MATCH_COMBO'
            results_entrees[combo_type].append({
                'bsl_id': bsl['id'], 'date': bsl['date'],
                'payment_ref': pay_ref[:60], 'amount': amt,
                'partner': partner_disp, 'partner_id': pid,
                'inv_ids':      [inv['id'] for inv in combo_result],
                'inv_names':    [inv['name'] for inv in combo_result],
                'inv_residuals': [round(inv['amount_residual'], 2) for inv in combo_result],
                'ecart': round(amt - round(sum(inv['amount_residual'] for inv in combo_result), 2), 2),
                'prio': 'P4_COMBO', 'invoices': combo_result,
            })
            continue

    if best_match:
        results_entrees[match_type].append({
            'bsl_id': bsl['id'], 'date': bsl['date'],
            'payment_ref': pay_ref[:60], 'amount': amt,
            'partner': partner_disp, 'partner_id': pid,
            'inv_name':    best_match['name'],
            'inv_id':      best_match['id'],
            'inv_residual': round(best_match['amount_residual'], 2),
            'inv_partner': best_match['partner_id'][1] if best_match['partner_id'] else '?',
            'ecart': match_ecart, 'prio': match_prio, 'invoice': best_match,
        })
    elif candidates:
        results_entrees['MULTI_CANDIDATS'].append({
            'bsl_id': bsl['id'], 'date': bsl['date'],
            'payment_ref': pay_ref[:60], 'amount': amt, 'partner': partner_disp,
            'nb_cands': len(candidates),
            'cands_preview': [c[1]['name'] if c[1] else c[0] for c in candidates[:3]],
        })
    else:
        results_entrees['AUCUN_MATCH'].append({
            'bsl_id': bsl['id'], 'date': bsl['date'],
            'payment_ref': pay_ref[:60], 'amount': amt, 'partner': partner_disp,
        })

# ══════════════════════════════════════════════════════════════════════════════
# 7. CATÉGORISATION DÉCAISSEMENTS
# ══════════════════════════════════════════════════════════════════════════════
print("\n[5] Catégorisation décaissements ...")

KEYWORDS_SORTIES = {
    'DOMICILIATION_SEPA': ['domiciliation', 'sdd', 'sepa dd', 'prelevement', 'incasso'],
    'CARTE_PUBLICITE':    ['mastercard', 'visa', 'google', 'meta ', 'facebook', 'instagram',
                           'linkedin', 'microsoft', 'apple ', 'stripe ', 'mollie', 'paypal',
                           'amazon ', 'aws ', 'shopify', 'sendcloud', 'mailchimp'],
    'SALAIRE_ONSS':       ['salaire', 'salary', 'loon', 'onss', 'dimona',
                           'groupe s', 'ucm ', 'partena', 'sd worx', 'sdworx'],
    'TVA_FISC':           ['tva', 'btw', 'taxe', 'belasting', 'spp finances', 'spf finances',
                           'fisc', 'ipp ', 'isoc', 'impot'],
    'LOCATION_UTILITES':  ['loyer', 'huur', 'electr', 'proximus', 'telenet', 'orange ',
                           'fluvius', 'sibelga', 'ores ', 'swde', 'eau ', 'assurance'],
}

def categorize_sortie(bsl):
    ref = ((bsl.get('payment_ref') or '') + ' ' + (bsl.get('narration') or '')).lower()
    for cat, kws in KEYWORDS_SORTIES.items():
        for kw in kws:
            if kw in ref:
                return cat
    return 'AUTRE'

results_sorties = {
    'VENDOR_BILL_MATCH':  [],
    'DOMICILIATION_SEPA': [],
    'CARTE_PUBLICITE':    [],
    'SALAIRE_ONSS':       [],
    'TVA_FISC':           [],
    'LOCATION_UTILITES':  [],
    'AUTRE':              [],
}

for bsl in bsl_sorties:
    amt_abs = round(abs(bsl['amount']), 2)
    partner_disp = (bsl['partner_id'][1] if bsl['partner_id']
                    else bsl.get('partner_name') or 'INCONNU')
    if amt_abs in vbill_by_amount:
        cands = vbill_by_amount[amt_abs]
        if len(cands) == 1:
            vb = cands[0]
            results_sorties['VENDOR_BILL_MATCH'].append({
                'bsl_id': bsl['id'], 'date': bsl['date'],
                'payment_ref': (bsl.get('payment_ref') or '')[:60],
                'amount':     -amt_abs,
                'vendor_bill': vb['name'],
                'vb_id':       vb['id'],
                'vb_partner':  vb['partner_id'][1] if vb['partner_id'] else '?',
                'vb_residual': round(vb['amount_residual'], 2),
                'partner_id':  vb['partner_id'][0] if vb['partner_id'] else None,
                'invoice':     vb,
            })
            continue
        else:
            cat = categorize_sortie(bsl)
            results_sorties[cat].append({
                'bsl_id': bsl['id'], 'date': bsl['date'],
                'payment_ref': (bsl.get('payment_ref') or '')[:60],
                'amount': -amt_abs, 'partner': partner_disp,
                'note': f'multi-cands vendor bill ({len(cands)})',
            })
            continue
    cat = categorize_sortie(bsl)
    results_sorties[cat].append({
        'bsl_id': bsl['id'], 'date': bsl['date'],
        'payment_ref': (bsl.get('payment_ref') or '')[:60],
        'amount': -amt_abs, 'partner': partner_disp,
    })

# ══════════════════════════════════════════════════════════════════════════════
# 8. AFFICHAGE RÉSUMÉ
# ══════════════════════════════════════════════════════════════════════════════
def sep(title=''):
    print('\n' + '─' * 72)
    if title:
        print(f'  {title}')
        print('─' * 72)

n_exact  = len(results_entrees['MATCH_EXACT'])
n_ecart  = len(results_entrees['MATCH_ECART_CENTS'])
n_combo  = len(results_entrees['MATCH_COMBO'])
n_vendor = len(results_sorties['VENDOR_BILL_MATCH'])

sep()
print(f"  ENCAISSEMENTS — MATCH_EXACT        : {n_exact}")
print(f"  ENCAISSEMENTS — MATCH_ECART_CENTS  : {n_ecart}")
print(f"  ENCAISSEMENTS — MATCH_COMBO        : {len(results_entrees['MATCH_COMBO'])}")
print(f"  DÉCAISSEMENTS — VENDOR_BILL_MATCH  : {n_vendor}")
print(f"  Cible totale auto-reconcilable     : {n_exact + n_ecart + n_vendor}")

for cat in ['MATCH_EXACT', 'MATCH_ECART_CENTS']:
    if results_entrees[cat]:
        sep(cat)
        for e in results_entrees[cat]:
            ecart_str = f" | ecart={e['ecart']:+.2f}" if e.get('ecart') else ''
            print(f"  BSL {e['bsl_id']} | {e['date']} | {e['amount']:.2f} EUR | "
                  f"{e['partner'][:28]} | {e['inv_name']}{ecart_str} | {e['prio']}")

if results_sorties['VENDOR_BILL_MATCH']:
    sep("VENDOR_BILL_MATCH")
    for e in results_sorties['VENDOR_BILL_MATCH']:
        print(f"  BSL {e['bsl_id']} | {e['date']} | {e['amount']:.2f} EUR | "
              f"{e['vb_partner'][:28]} | {e['vendor_bill']}")

# ══════════════════════════════════════════════════════════════════════════════
# 9. FONCTIONS DE RÉCONCILIATION
# ══════════════════════════════════════════════════════════════════════════════

def verify_reconciled(bsl_id, inv_id, is_vendor=False):
    """
    Ré-interroge Odoo pour vérifier l'état post-reconcile.
    Retourne (bsl_reconciled, inv_payment_state, inv_residual, matching_number).
    """
    bsl_check = call('account.bank.statement.line', 'read',
        [[bsl_id]], {'fields': ['is_reconciled', 'move_id']}
    )
    bsl_reconciled = bsl_check[0]['is_reconciled'] if bsl_check else None

    if is_vendor:
        inv_check = call('account.move', 'read',
            [[inv_id]], {'fields': ['payment_state', 'amount_residual']}
        )
    else:
        inv_check = call('account.move', 'read',
            [[inv_id]], {'fields': ['payment_state', 'amount_residual', 'line_ids']}
        )

    inv_payment_state = None
    inv_residual      = None
    matching_number   = None

    if inv_check:
        inv_payment_state = inv_check[0].get('payment_state')
        inv_residual      = inv_check[0].get('amount_residual')

        if not is_vendor:
            line_ids = inv_check[0].get('line_ids', [])
            if line_ids:
                matched_amls = call('account.move.line', 'search_read',
                    [[['id', 'in', line_ids],
                      ['account_id.account_type', '=', 'asset_receivable']]],
                    {'fields': ['matching_number', 'reconciled']}
                )
                for aml in matched_amls:
                    if aml.get('matching_number'):
                        matching_number = aml['matching_number']
                        break

    return bsl_reconciled, inv_payment_state, inv_residual, matching_number


def call_reconcile_safe(aml_ids):
    """
    Appelle account.move.line.reconcile() et gère le faux-échec
    "cannot marshal None" : si l'exception contient ce texte (ou est un
    xmlrpc.client.Fault), on ne panique pas — le commit serveur est déjà
    passé. On retourne (True, exception_str) pour que l'appelant vérifie
    en base.

    Retourne :
      (True,  None)          — reconcile() a retourné sans exception
      (True,  exc_str)       — exception de marshalling = faux-échec probable
      (False, exc_str)       — erreur réelle Odoo (AccessError, etc.)
    """
    try:
        call('account.move.line', 'reconcile', [aml_ids])
        return True, None
    except xmlrpc.client.Fault as f:
        # Fault Odoo avec code -1 = souvent résultat None non-marshalable
        # Fault avec code != 2 (UserError/ValidationError) = erreur réelle
        msg = str(f.faultString)
        if 'cannot marshal' in msg or f.faultCode == -1:
            return True, f"faux-echec marshalling (faultCode={f.faultCode}): {msg[:120]}"
        # Vraie erreur Odoo
        return False, f"Fault Odoo (faultCode={f.faultCode}): {msg[:200]}"
    except Exception as e:
        msg = str(e)
        if 'cannot marshal' in msg.lower():
            return True, f"faux-echec marshalling: {msg[:120]}"
        return False, msg[:200]


def get_bsl_suspense_aml(bsl_id):
    """Identifie la AML suspense du move généré par la BSL."""
    bsl_data = call('account.bank.statement.line', 'read',
        [[bsl_id]], {'fields': ['move_id', 'journal_id']}
    )
    if not bsl_data or not bsl_data[0].get('move_id'):
        return None, None

    move_id    = bsl_data[0]['move_id'][0]
    journal_id = bsl_data[0]['journal_id'][0] if bsl_data[0].get('journal_id') else None

    suspense_acc_id = ING_SUSPENSE_ACC_ID
    if not suspense_acc_id and journal_id:
        j_data = call('account.journal', 'read',
            [[journal_id]], {'fields': ['suspense_account_id']}
        )
        if j_data and j_data[0].get('suspense_account_id'):
            suspense_acc_id = j_data[0]['suspense_account_id'][0]

    amls = call('account.move.line', 'search_read',
        [[['move_id', '=', move_id]]],
        {'fields': ['id', 'account_id', 'account_type', 'debit', 'credit',
                    'reconciled', 'amount_residual', 'partner_id']}
    )

    suspense_aml  = None
    for a in amls:
        acc_type = a.get('account_type', '')
        acc_id   = a['account_id'][0] if a.get('account_id') else None

        if acc_type in ('asset_cash', 'asset_bank'):
            continue
        if suspense_acc_id and acc_id == suspense_acc_id:
            suspense_aml = a
            break
        if not suspense_aml and not a['reconciled']:
            suspense_aml = a

    return suspense_aml, move_id


def get_invoice_receivable_aml(invoice_id):
    """Récupère la AML receivable non lettrée de la facture client."""
    inv_data = call('account.move', 'read',
        [[invoice_id]], {'fields': ['line_ids', 'partner_id']}
    )
    if not inv_data:
        return None, None
    line_ids   = inv_data[0].get('line_ids', [])
    partner_id = inv_data[0]['partner_id'][0] if inv_data[0].get('partner_id') else None
    if not line_ids:
        return None, partner_id
    amls = call('account.move.line', 'search_read',
        [[['id', 'in', line_ids],
          ['account_id.account_type', '=', 'asset_receivable'],
          ['reconciled', '=', False]]],
        {'fields': ['id', 'debit', 'credit', 'amount_residual', 'partner_id', 'account_id']}
    )
    return amls, partner_id


def add_writeoff_line_to_bsl_move(move_id, ecart_signed, currency_id=None):
    """
    Ajoute une ligne de write-off sur le move de la BSL pour absorber l'écart.

    ecart_signed = BSL_amount - INV_residual
      > 0 : BSL encaissé > facture → ligne crédit 757xxx (produit financier)
      < 0 : BSL encaissé < facture → ligne débit  657xxx (charge financière)

    Odoo 18 : on doit reset le move en draft, ajouter la ligne, re-poster.
    Si reset_to_draft est refusé → on retourne l'erreur pour déclencher
    le fallback account.payment.register.

    Retourne (True, writeoff_aml_id) ou (False, error_str).
    """
    abs_ecart = abs(round(ecart_signed, 2))
    if abs_ecart < 0.005:
        return True, None   # écart négligeable

    if ecart_signed > 0:
        # BSL > INV : on a encaissé trop → produit financier
        wo_acc = writeoff_credit_acc
        wo_label = f"Ecart reglement client +{abs_ecart:.2f}"
        # Crédit 757 = debit=0, credit=abs_ecart → rééquilibre le move
        debit_wo  = 0.0
        credit_wo = abs_ecart
    else:
        # BSL < INV : on a encaissé moins → charge financière
        wo_acc = writeoff_debit_acc
        wo_label = f"Ecart reglement client -{abs_ecart:.2f}"
        # Débit 657 = debit=abs_ecart, credit=0
        debit_wo  = abs_ecart
        credit_wo = 0.0

    if not wo_acc:
        return False, f"Compte write-off non trouvé pour écart {'positif' if ecart_signed > 0 else 'négatif'}"

    # Lire le move pour l'état et le journal
    move_data = call('account.move', 'read',
        [[move_id]], {'fields': ['state', 'journal_id', 'partner_id', 'currency_id']}
    )
    if not move_data:
        return False, f"Move {move_id} introuvable"

    move_state = move_data[0].get('state')
    partner_id = move_data[0]['partner_id'][0] if move_data[0].get('partner_id') else False
    curr_id    = move_data[0]['currency_id'][0] if move_data[0].get('currency_id') else False

    # Reset to draft si posté
    if move_state == 'posted':
        try:
            call('account.move', 'button_draft', [[move_id]])
        except Exception as e:
            return False, f"button_draft refusé sur move {move_id}: {e}"

    # Ajouter la ligne write-off
    new_line = {
        'move_id':    move_id,
        'account_id': wo_acc['id'],
        'name':       wo_label,
        'debit':      debit_wo,
        'credit':     credit_wo,
    }
    if partner_id:
        new_line['partner_id'] = partner_id

    try:
        new_line_id = call('account.move.line', 'create', [new_line])
    except Exception as e:
        # Re-poster avant de retourner l'erreur
        try:
            call('account.move', 'action_post', [[move_id]])
        except Exception:
            pass
        return False, f"Création ligne write-off refusée: {e}"

    # Re-poster le move
    try:
        call('account.move', 'action_post', [[move_id]])
    except Exception as e:
        return False, f"action_post après write-off refusé: {e}"

    return True, new_line_id


def reconcile_bsl_with_invoice(bsl_entry, dry_run=True, test_mode=False):
    """
    Réconcilie une BSL encaissement avec une facture client.

    Corrections v5 :
    - Skip si BSL déjà is_reconciled=True
    - Faux-échec marshalling géré par call_reconcile_safe()
    - Écart ≤ WRITE_OFF_SEUIL : ajout ligne write-off sur move BSL AVANT reconcile
      pour garantir payment_state=paid (pas de facture en partial)
    """
    bsl_id   = bsl_entry['bsl_id']
    inv_id   = bsl_entry.get('invoice', {}).get('id') or bsl_entry.get('inv_id')
    ecart    = round(bsl_entry.get('ecart', 0.0), 2)
    inv_name = bsl_entry.get('inv_name', '?')

    result = {
        'bsl_id':   bsl_id,
        'inv_id':   inv_id,
        'inv_name': inv_name,
        'amount':   bsl_entry['amount'],
        'ecart':    ecart,
        'status':   None,
        'error':    None,
        'writeoff_amount': 0.0,
        'writeoff_aml_id': None,
    }

    if dry_run:
        result['status'] = 'DRY_RUN_SIMULE'
        return result

    # ── Skip BSL déjà réconciliée ──────────────────────────────────────────
    pre_check = call('account.bank.statement.line', 'read',
        [[bsl_id]], {'fields': ['is_reconciled']}
    )
    if pre_check and pre_check[0]['is_reconciled']:
        result['status'] = 'SKIP_DEJA_RECONCILIEE'
        result['error']  = 'BSL déjà is_reconciled=True — skippée'
        bsl_r, inv_ps, inv_res, mn = verify_reconciled(bsl_id, inv_id)
        result['bsl_is_reconciled']   = bsl_r
        result['inv_payment_state']   = inv_ps
        result['inv_amount_residual'] = inv_res
        result['matching_number']     = mn
        return result

    try:
        # ── Étape 1 : AML suspense de la BSL ──────────────────────────────
        suspense_aml, move_id = get_bsl_suspense_aml(bsl_id)
        if not suspense_aml:
            result['status'] = 'ERROR'
            result['error']  = 'AML suspense introuvable dans le move de la BSL'
            return result

        suspense_aml_id       = suspense_aml['id']
        result['suspense_aml_id'] = suspense_aml_id
        result['bsl_move_id']     = move_id

        # ── Étape 2 : AML receivable de la facture ─────────────────────────
        recv_amls, inv_partner_id = get_invoice_receivable_aml(inv_id)
        if not recv_amls:
            result['status'] = 'ERROR'
            result['error']  = 'Aucune AML receivable sur la facture (déjà lettrée ?)'
            return result

        recv_aml    = recv_amls[0]
        recv_aml_id = recv_aml['id']
        recv_acc_id = recv_aml['account_id'][0] if recv_aml.get('account_id') else None
        result['recv_aml_id'] = recv_aml_id

        if not recv_acc_id:
            result['status'] = 'ERROR'
            result['error']  = 'Compte receivable introuvable sur AML facture'
            return result

        # ── Étape 3 : Write-off AVANT repoint si écart > 0 ────────────────
        # On ajoute une ligne write-off sur le move de la BSL pour que le total
        # côté compte client = résiduel exact de la facture → full reconcile garanti.
        if abs(ecart) >= 0.005:
            wo_ok, wo_result = add_writeoff_line_to_bsl_move(move_id, ecart)
            if wo_ok:
                result['writeoff_amount']  = abs(ecart)
                result['writeoff_aml_id']  = wo_result
                result['writeoff_applied'] = True
                # Après le reset/re-post du move, l'AML suspense peut avoir changé d'id
                # → re-lire la suspense AML
                suspense_aml_refresh, _ = get_bsl_suspense_aml(bsl_id)
                if suspense_aml_refresh:
                    suspense_aml_id = suspense_aml_refresh['id']
                    result['suspense_aml_id'] = suspense_aml_id
            else:
                # Fallback : account.payment.register
                result['writeoff_error'] = wo_result
                try:
                    ctx = {
                        'active_model': 'account.move',
                        'active_ids': [inv_id],
                    }
                    wiz_id = call('account.payment.register', 'create',
                        [{'payment_difference_handling': 'reconcile',
                          'writeoff_account_id': writeoff_debit_acc['id'] if ecart < 0 else writeoff_credit_acc['id'],
                          'writeoff_label': f'Ecart {ecart:+.2f} EUR',
                          'journal_id': ing_journal_id,
                          'amount': abs(bsl_entry['amount']),
                         }],
                        {'context': ctx}
                    )
                    call('account.payment.register', 'action_create_payments', [[wiz_id]], {'context': ctx})
                    result['status']      = 'OK_WITH_WRITEOFF_VIA_PAYMENT_REGISTER'
                    result['method_used'] = 'payment_register_writeoff'
                except Exception as e_pr:
                    result['status'] = 'ERROR'
                    result['error']  = (
                        f"write-off ligne refusé ({wo_result}) ET "
                        f"payment.register refusé ({e_pr}). Réconciliation manuelle requise."
                    )
                    return result

                bsl_r, inv_ps, inv_res, mn = verify_reconciled(bsl_id, inv_id)
                result['bsl_is_reconciled']   = bsl_r
                result['inv_payment_state']   = inv_ps
                result['inv_amount_residual'] = inv_res
                result['matching_number']     = mn
                return result

        # ── Étape 4 : Repointer AML suspense → compte receivable ───────────
        write_vals = {'account_id': recv_acc_id}
        if inv_partner_id:
            write_vals['partner_id'] = inv_partner_id

        write_ok    = False
        write_error = None
        try:
            call('account.move.line', 'write', [[suspense_aml_id], write_vals])
            write_ok = True
        except Exception as e_write:
            write_error = str(e_write)
            result['write_error'] = write_error

        if not write_ok:
            # Fallback wizard
            try:
                wiz_id = call('account.reconcile.wizard', 'create', [{
                    'account_move_line_ids': [(4, recv_aml_id), (4, suspense_aml_id)],
                }])
                call('account.reconcile.wizard', 'reconcile', [[wiz_id]])
                write_ok = True
                result['method_used'] = 'wizard_reconcile_fallback'
            except Exception as e_wiz:
                result['status'] = 'ERROR'
                result['error']  = (
                    f"write() refusé: {write_error} | "
                    f"wizard refusé: {e_wiz}. Réconciliation manuelle requise."
                )
                return result

        # ── Étape 5 : Réconcilier les 2 AML ───────────────────────────────
        if write_ok and result.get('method_used') != 'wizard_reconcile_fallback':
            ok, exc_str = call_reconcile_safe([suspense_aml_id, recv_aml_id])
            if not ok:
                result['status'] = 'ERROR'
                result['error']  = f'reconcile() échoué: {exc_str}'
                return result
            if exc_str:
                result['marshalling_note'] = exc_str

            result['method_used'] = 'aml_reconcile' + ('_with_writeoff' if abs(ecart) >= 0.005 else '_exact')

        # ── Étape 6 : Vérification en base ────────────────────────────────
        bsl_r, inv_ps, inv_res, mn = verify_reconciled(bsl_id, inv_id)
        result['bsl_is_reconciled']   = bsl_r
        result['inv_payment_state']   = inv_ps
        result['inv_amount_residual'] = inv_res
        result['matching_number']     = mn

        # Déterminer statut final
        if not result.get('status'):
            if bsl_r and (inv_ps in ('paid', 'in_payment') or abs(inv_res or 999) < 0.02):
                result['status'] = 'OK' if abs(ecart) < 0.005 else 'OK_WITH_WRITEOFF'
            elif bsl_r:
                result['status'] = 'OK_PARTIAL'
                result['error']  = (
                    f"BSL réconciliée MAIS facture payment_state={inv_ps} "
                    f"residual={inv_res:.2f}. Vérifier manuellement."
                )
            else:
                result['status'] = 'ERROR'
                result['error']  = (
                    f"BSL.is_reconciled={bsl_r}, payment_state={inv_ps}, "
                    f"residual={inv_res}. Opération non confirmée."
                )

    except Exception as e:
        result['status'] = 'ERROR'
        result['error']  = str(e)

    return result


def reconcile_bsl_with_vendor_bill(bsl_entry, dry_run=True):
    """
    Réconcilie une BSL décaissement avec une facture fournisseur.
    Même mécanique : suspense → compte payable (440xxx) + partner, puis reconcile.
    Montants exacts → pas de write-off.
    """
    bsl_id  = bsl_entry['bsl_id']
    vb_id   = bsl_entry.get('invoice', {}).get('id') or bsl_entry.get('vb_id')
    vb_name = bsl_entry.get('vendor_bill', '?')

    result = {
        'bsl_id':  bsl_id,
        'vb_id':   vb_id,
        'vb_name': vb_name,
        'amount':  bsl_entry['amount'],
        'status':  None,
        'error':   None,
    }

    if dry_run:
        result['status'] = 'DRY_RUN_SIMULE'
        return result

    # Skip si déjà réconciliée
    pre_check = call('account.bank.statement.line', 'read',
        [[bsl_id]], {'fields': ['is_reconciled']}
    )
    if pre_check and pre_check[0]['is_reconciled']:
        result['status'] = 'SKIP_DEJA_RECONCILIEE'
        result['error']  = 'BSL déjà réconciliée — skippée'
        bsl_r, vb_ps, vb_res, _ = verify_reconciled(bsl_id, vb_id, is_vendor=True)
        result['bsl_is_reconciled'] = bsl_r
        result['vb_payment_state']  = vb_ps
        return result

    try:
        # AML suspense de la BSL
        suspense_aml, move_id = get_bsl_suspense_aml(bsl_id)
        if not suspense_aml:
            result['status'] = 'ERROR'
            result['error']  = 'AML suspense introuvable'
            return result

        suspense_aml_id = suspense_aml['id']

        # AML payable de la facture fournisseur
        vb_data = call('account.move', 'read',
            [[vb_id]], {'fields': ['line_ids', 'partner_id']}
        )
        if not vb_data:
            result['status'] = 'ERROR'
            result['error']  = 'Facture fournisseur introuvable'
            return result

        line_ids   = vb_data[0].get('line_ids', [])
        partner_id = vb_data[0]['partner_id'][0] if vb_data[0].get('partner_id') else None

        payable_amls = call('account.move.line', 'search_read',
            [[['id', 'in', line_ids],
              ['account_id.account_type', '=', 'liability_payable'],
              ['reconciled', '=', False]]],
            {'fields': ['id', 'amount_residual', 'account_id']}
        )

        if not payable_amls:
            result['status'] = 'ERROR'
            result['error']  = 'Aucune AML payable sur la facture fournisseur (déjà lettrée ?)'
            return result

        payable_aml    = payable_amls[0]
        payable_aml_id = payable_aml['id']
        payable_acc_id = payable_aml['account_id'][0] if payable_aml.get('account_id') else None

        # Si pas de compte payable trouvé sur la facture, fallback 440xxx
        if not payable_acc_id and payable_acc:
            payable_acc_id = payable_acc['id']

        # Repointer suspense → compte payable
        write_vals = {'account_id': payable_acc_id}
        if partner_id:
            write_vals['partner_id'] = partner_id

        write_ok    = False
        write_error = None
        try:
            call('account.move.line', 'write', [[suspense_aml_id], write_vals])
            write_ok = True
        except Exception as e_write:
            write_error = str(e_write)

        if not write_ok:
            try:
                wiz_id = call('account.reconcile.wizard', 'create', [{
                    'account_move_line_ids': [(4, payable_aml_id), (4, suspense_aml_id)],
                }])
                call('account.reconcile.wizard', 'reconcile', [[wiz_id]])
                write_ok = True
                result['method_used'] = 'wizard_reconcile_fallback'
            except Exception as e_wiz:
                result['status'] = 'ERROR'
                result['error']  = f'write() refusé: {write_error} | wizard refusé: {e_wiz}'
                return result

        if write_ok and result.get('method_used') != 'wizard_reconcile_fallback':
            ok, exc_str = call_reconcile_safe([suspense_aml_id, payable_aml_id])
            if not ok:
                result['status'] = 'ERROR'
                result['error']  = f'reconcile() échoué: {exc_str}'
                return result
            if exc_str:
                result['marshalling_note'] = exc_str
            result['method_used'] = 'aml_reconcile_exact'

        # Vérification
        bsl_r, vb_ps, vb_res, _ = verify_reconciled(bsl_id, vb_id, is_vendor=True)
        result['bsl_is_reconciled'] = bsl_r
        result['vb_payment_state']  = vb_ps
        result['vb_amount_residual'] = vb_res

        if bsl_r and (vb_ps in ('paid', 'in_payment') or abs(vb_res or 999) < 0.02):
            result['status'] = 'OK'
        elif bsl_r:
            result['status'] = 'OK_PARTIAL'
            result['error']  = f"BSL réconciliée MAIS vb payment_state={vb_ps} residual={vb_res}"
        else:
            result['status'] = 'ERROR'
            result['error']  = f"BSL.is_reconciled={bsl_r}, vb_ps={vb_ps}, vb_res={vb_res}"

    except Exception as e:
        result['status'] = 'ERROR'
        result['error']  = str(e)

    return result


# ══════════════════════════════════════════════════════════════════════════════
# 10. APPLICATION — ORDRE : MATCH_EXACT → VENDOR_BILL → ECART_CENTS
# ══════════════════════════════════════════════════════════════════════════════

OK_STATUTS = {'OK', 'OK_WITH_WRITEOFF', 'OK_WITH_WRITEOFF_VIA_PAYMENT_REGISTER',
              'OK_PARTIAL', 'SKIP_DEJA_RECONCILIEE'}

if DRY_RUN:
    print("\n" + "=" * 72)
    print("MODE DRY-RUN — AUCUNE ÉCRITURE. Passer DRY_RUN=False pour appliquer.")
    print("=" * 72)
else:
    sep()
    print("MODE APPLY — DÉBUT DU LETTRAGE (18 lignes cibles)")
    print("Ordre : MATCH_EXACT (encaissements) → VENDOR_BILL → ECART_CENTS")
    sep()

    apply_results  = []
    n_ok           = 0
    n_error        = 0
    n_skip         = 0
    n_writeoff     = 0
    total_writeoff = 0.0
    limit_hit      = False

    def log_result(res, label=''):
        global n_ok, n_error, n_skip, n_writeoff, total_writeoff
        status = res.get('status', 'ERROR')
        if status in OK_STATUTS:
            if status == 'SKIP_DEJA_RECONCILIEE':
                n_skip += 1
            else:
                n_ok += 1
            if res.get('writeoff_amount', 0) > 0:
                n_writeoff     += 1
                total_writeoff += res['writeoff_amount']
            mark = 'OK' if status != 'SKIP_DEJA_RECONCILIEE' else 'SKIP'
        else:
            n_error += 1
            mark = 'ERROR'

        bsl_id = res.get('bsl_id')
        inv_ref = res.get('inv_name') or res.get('vb_name', '?')
        print(f"  [{mark}] BSL {bsl_id} | {label} | {inv_ref}")
        print(f"         status={status} | method={res.get('method_used','?')}")
        print(f"         BSL.is_reconciled={res.get('bsl_is_reconciled')} | "
              f"payment_state={res.get('inv_payment_state') or res.get('vb_payment_state')} | "
              f"residual={res.get('inv_amount_residual') or res.get('vb_amount_residual')}")
        if res.get('matching_number'):
            print(f"         matching_number={res['matching_number']}")
        if res.get('writeoff_amount', 0) > 0:
            print(f"         write-off={res['writeoff_amount']:.2f} EUR | aml_id={res.get('writeoff_aml_id')}")
        if res.get('marshalling_note'):
            print(f"         NOTE marshalling (faux-echec gere): {res['marshalling_note'][:80]}")
        if status not in OK_STATUTS:
            print(f"         ERREUR: {res.get('error', '?')}")
            if res.get('write_error'):
                print(f"         write_error: {res.get('write_error')}")

    processed_total = 0

    # ══════ PHASE 1 : MATCH_EXACT encaissements ════════════════════════════
    todo = list(results_entrees['MATCH_EXACT'])
    if LIMIT_TEST:
        todo = todo[:max(0, LIMIT_TEST - processed_total)]
    print(f"\n--- PHASE 1 : MATCH_EXACT encaissements ({len(todo)} lignes) ---")

    for entry in todo:
        if LIMIT_TEST and processed_total >= LIMIT_TEST:
            limit_hit = True
            break
        print(f"\n  --> BSL {entry['bsl_id']} | {entry['date']} | "
              f"{entry['amount']:.2f} EUR | {entry['partner'][:30]} | {entry['inv_name']}")
        res = reconcile_bsl_with_invoice(entry, dry_run=False)
        apply_results.append(res)
        processed_total += 1
        log_result(res, f"{entry['amount']:.2f} EUR / {entry['inv_name']}")

    # ══════ PHASE 2 : VENDOR_BILL_MATCH décaissements ═════════════════════
    if not limit_hit:
        todo_vb = list(results_sorties['VENDOR_BILL_MATCH'])
        if LIMIT_TEST:
            todo_vb = todo_vb[:max(0, LIMIT_TEST - processed_total)]
        print(f"\n--- PHASE 2 : VENDOR_BILL_MATCH décaissements ({len(todo_vb)} lignes) ---")

        for entry in todo_vb:
            if LIMIT_TEST and processed_total >= LIMIT_TEST:
                limit_hit = True
                break
            print(f"\n  --> BSL {entry['bsl_id']} | {entry['date']} | "
                  f"{entry['amount']:.2f} EUR | {entry['vb_partner'][:30]} | {entry['vendor_bill']}")
            res = reconcile_bsl_with_vendor_bill(entry, dry_run=False)
            apply_results.append(res)
            processed_total += 1
            log_result(res, f"{entry['amount']:.2f} EUR / {entry['vendor_bill']}")

    # ══════ PHASE 3 : MATCH_ECART_CENTS (write-off) ═══════════════════════
    if not limit_hit:
        todo_ec = list(results_entrees['MATCH_ECART_CENTS'])
        if LIMIT_TEST:
            todo_ec = todo_ec[:max(0, LIMIT_TEST - processed_total)]

        if todo_ec:
            print(f"\n--- PHASE 3 : MATCH_ECART_CENTS write-off ({len(todo_ec)} lignes) ---")
            print("    TEST sur la 1ère ligne avant de dérouler les suivantes ...")

            # Test sur le 1er écart (SA Barthe si présent, sinon le premier)
            test_entry = todo_ec[0]
            print(f"\n  [TEST ECART] --> BSL {test_entry['bsl_id']} | {test_entry['date']} | "
                  f"BSL={test_entry['amount']:.2f} | INV={test_entry['inv_residual']:.2f} | "
                  f"ecart={test_entry['ecart']:+.2f} | {test_entry['inv_name']}")

            res_test = reconcile_bsl_with_invoice(test_entry, dry_run=False)
            apply_results.append(res_test)
            processed_total += 1
            log_result(res_test, f"TEST ecart {test_entry['ecart']:+.2f} / {test_entry['inv_name']}")

            # Vérifier que le test a réussi (payment_state=paid)
            test_ok = (
                res_test.get('status') in OK_STATUTS and
                res_test.get('status') != 'SKIP_DEJA_RECONCILIEE' and
                res_test.get('inv_payment_state') in ('paid', 'in_payment')
            )

            if test_ok:
                print(f"\n  [TEST ECART OK] payment_state=paid confirmé. Déroulement des {len(todo_ec)-1} suivantes ...")
                for entry in todo_ec[1:]:
                    if LIMIT_TEST and processed_total >= LIMIT_TEST:
                        limit_hit = True
                        break
                    if not (writeoff_debit_acc or writeoff_credit_acc):
                        print(f"  SKIP BSL {entry['bsl_id']} — comptes write-off non trouvés")
                        n_skip += 1
                        continue
                    print(f"\n  --> BSL {entry['bsl_id']} | {entry['date']} | "
                          f"BSL={entry['amount']:.2f} | INV={entry['inv_residual']:.2f} | "
                          f"ecart={entry['ecart']:+.2f} | {entry['inv_name']}")
                    res = reconcile_bsl_with_invoice(entry, dry_run=False)
                    apply_results.append(res)
                    processed_total += 1
                    log_result(res, f"ecart {entry['ecart']:+.2f} / {entry['inv_name']}")
            else:
                print(f"\n  [TEST ECART ECHEC] payment_state={res_test.get('inv_payment_state')} "
                      f"status={res_test.get('status')}.")
                print(f"  Les {len(todo_ec)-1} lignes restantes MATCH_ECART_CENTS sont SKIPPEES.")
                print(f"  Analyser l'erreur ci-dessus et corriger le script avant de relancer.")
                for entry in todo_ec[1:]:
                    n_skip += 1

    # ══════════════════════════════════════════════════════════════════════
    # RÉCAP FINAL
    # ══════════════════════════════════════════════════════════════════════
    sep()
    print("RECAPITULATIF FINAL")
    sep()
    print(f"""
  Lignes traitées          : {processed_total}
  OK (réconciliées)        : {n_ok}
  SKIP (déjà faites)       : {n_skip}
  ERREURS                  : {n_error}
  Write-off appliqués      : {n_writeoff}
  Montant total write-off  : {total_writeoff:.2f} EUR
""")

    # Statut par ligne
    print("  Détail par ligne :")
    print(f"  {'BSL_ID':>7} | {'Status':35s} | {'Ref':20s} | {'is_recon':8s} | {'pay_state':12s} | {'residual':>10s} | {'WO EUR':>7s}")
    print(f"  {'-'*7}-+-{'-'*35}-+-{'-'*20}-+-{'-'*8}-+-{'-'*12}-+-{'-'*10}-+-{'-'*7}")
    for r in apply_results:
        inv_ref   = (r.get('inv_name') or r.get('vb_name') or '?')[:20]
        bsl_r     = str(r.get('bsl_is_reconciled', '?'))
        pay_state = str(r.get('inv_payment_state') or r.get('vb_payment_state') or '?')
        residual  = r.get('inv_amount_residual') or r.get('vb_amount_residual')
        res_str   = f"{residual:.2f}" if isinstance(residual, float) else str(residual or '?')
        wo_str    = f"{r.get('writeoff_amount', 0):.2f}" if r.get('writeoff_amount', 0) > 0 else '-'
        status    = r.get('status', 'ERROR')[:35]
        print(f"  {r['bsl_id']:>7} | {status:35s} | {inv_ref:20s} | {bsl_r:8s} | {pay_state:12s} | {res_str:>10s} | {wo_str:>7s}")

    if n_error > 0:
        sep("ERREURS DÉTAILLÉES")
        for r in apply_results:
            if r.get('status') not in OK_STATUTS:
                print(f"  BSL {r['bsl_id']} | {r.get('inv_name') or r.get('vb_name')} | {r.get('error')}")

    print("\nScript terminé.")
