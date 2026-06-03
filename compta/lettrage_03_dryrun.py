"""
ÉTAPE 3 — DRY-RUN LETTRAGE BANCAIRE ING (lecture seule, ZÉRO écriture)
Journal : ING BE30 3631 6408 2311
Cible   : 242 bank.statement.line non réconciliées (77 entrées + 165 sorties)
Date    : 2026-06-03

Logique :
  ENCAISSEMENTS (>0) :
    Matching par priorité :
      P1 — communication structurée +++xxx/xxxx/xxxxx+++ dans payment_ref
           vs payment_reference de la facture OU name de la facture
      P2 — montant exact + partner_id identique
      P3 — montant exact unique (un seul candidat toutes factures)
    Classes : MATCH_EXACT / MATCH_ECART_CENTS / MATCH_PARTIEL / MULTI_CANDIDATS / AUCUN_MATCH

  DÉCAISSEMENTS (<0) :
    Catégorisation uniquement (ZÉRO imputation) :
      - Domiciliations SEPA (mots-clés)
      - Cartes / Google / Meta / publicité
      - Virements ODIGO / salaires
      - Match facture fournisseur ouverte (in_invoice) par montant exact
      - Reste = manuel (liste pour Nicolas, PAS d'imputation P&L auto)

SEUIL WRITE-OFF retenu : 0,05 EUR
  Justification : TVA 21% sur petits montants → cent peut différer par arrondi
  ONSS, Stripe, Mollie fees → max 0,02 EUR ; 0,05 EUR couvre sans dépasser 0,10 EUR
  (0,10 EUR serait trop permissif pour des factures clients B2C à 10-20 EUR)

AUCUNE ÉCRITURE — sortie analyse uniquement.
"""

import xmlrpc.client
import re
from collections import defaultdict
from datetime import date

# ─── Connexion ────────────────────────────────────────────────────────────────
URL  = "https://tea-tree.odoo.com"
DB   = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD  = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid    = common.authenticate(DB, USER, PWD, {})
m      = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

WRITE_OFF_SEUIL = 0.05   # EUR — seuil write-off encaissements

# ─── Regex communication structurée belge ─────────────────────────────────────
RE_STRUCT = re.compile(r'\+\+\+(\d{3})[/ ]?(\d{4})[/ ]?(\d{5})\+\+\+')

def extract_struct_ref(text):
    """Retourne la ref structurée normalisée '+++xxx/xxxx/xxxxx+++' si trouvée."""
    if not text:
        return None
    m2 = RE_STRUCT.search(text)
    if m2:
        return f"+++{m2.group(1)}/{m2.group(2)}/{m2.group(3)}+++"
    return None

def normalize_struct(ref):
    """Normalise une ref structurée en supprimant les séparateurs."""
    if not ref:
        return None
    digits = re.sub(r'[^0-9]', '', ref)
    if len(digits) == 12:
        return digits
    return None

print("=" * 72)
print("DRY-RUN LETTRAGE ING — 2026-06-03 (LECTURE SEULE)")
print(f"Seuil write-off encaissements : {WRITE_OFF_SEUIL:.2f} EUR")
print("=" * 72)

# ═══════════════════════════════════════════════════════════════════════════════
# 0. IDENTIFIER LE JOURNAL ING
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[0] Recherche du journal ING BE30 3631 6408 2311 ...")

journals = call('account.journal', 'search_read',
    [[['type', '=', 'bank']]],
    {'fields': ['id', 'name', 'bank_account_id', 'code']}
)

ing_journal = None
for j in journals:
    name_lower = (j.get('name') or '').lower()
    if 'ing' in name_lower or '3631' in name_lower or 'be30' in name_lower:
        ing_journal = j
        break

if not ing_journal:
    # Fallback : chercher via bank_account
    for j in journals:
        ba = j.get('bank_account_id')
        if ba and ('3631' in str(ba) or 'ING' in str(ba).upper()):
            ing_journal = j
            break

if not ing_journal:
    print("  ATTENTION : journal ING non identifié par nom/IBAN.")
    print("  Journaux bank disponibles :")
    for j in journals:
        print(f"    id={j['id']:4d} | code={j['code']:10s} | {j['name']}")
    print("\n  On continue sur TOUTES les bank.statement.line non réconciliées.")
    journal_filter = []
else:
    print(f"  Journal ING trouvé : id={ing_journal['id']} | {ing_journal['name']} ({ing_journal['code']})")
    journal_filter = [['journal_id', '=', ing_journal['id']]]

# ═══════════════════════════════════════════════════════════════════════════════
# 1. CHARGER LES BANK STATEMENT LINES NON RÉCONCILIÉES
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[1] Chargement bank.statement.line non réconciliées ...")

domain_bsl = [['is_reconciled', '=', False]] + journal_filter
bsl_all = call('account.bank.statement.line', 'search_read',
    [domain_bsl],
    {'fields': ['id', 'date', 'payment_ref', 'amount', 'partner_id',
                'journal_id', 'narration', 'transaction_type',
                'partner_name'],
     'limit': 2000}
)

bsl_entrees = [l for l in bsl_all if l['amount'] > 0]
bsl_sorties = [l for l in bsl_all if l['amount'] < 0]

print(f"  Total non réconciliées : {len(bsl_all)}")
print(f"    Encaissements (>0)   : {len(bsl_entrees)}")
print(f"    Décaissements (<0)   : {len(bsl_sorties)}")

# ═══════════════════════════════════════════════════════════════════════════════
# 2. CHARGER LES FACTURES CLIENTS OUVERTES
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[2] Chargement factures clients ouvertes (not_paid + partial) ...")

inv_open = call('account.move', 'search_read',
    [[['move_type', '=', 'out_invoice'],
      ['state', '=', 'posted'],
      ['payment_state', 'in', ['not_paid', 'partial']]]],
    {'fields': ['id', 'name', 'partner_id', 'amount_residual',
                'invoice_date_due', 'invoice_date',
                'payment_reference', 'ref',
                'invoice_origin'],
     'limit': 5000}
)

print(f"  Factures ouvertes : {len(inv_open)}")

# Index 1 : par montant résiduel arrondi → liste factures
inv_by_amount = defaultdict(list)
for inv in inv_open:
    amt = round(inv['amount_residual'], 2)
    inv_by_amount[amt].append(inv)

# Index 2 : par (montant, partner_id) → liste factures
inv_by_amt_partner = defaultdict(list)
for inv in inv_open:
    amt = round(inv['amount_residual'], 2)
    pid = inv['partner_id'][0] if inv['partner_id'] else 0
    inv_by_amt_partner[(amt, pid)].append(inv)

# Index 3 : par référence structurée normalisée (sur payment_reference ET name)
inv_by_struct = {}
for inv in inv_open:
    for field in ['payment_reference', 'name', 'ref']:
        raw = inv.get(field) or ''
        norm = normalize_struct(raw)
        if norm:
            inv_by_struct[norm] = inv
            break
    # Aussi chercher le pattern +++ dans les champs texte
    for field in ['payment_reference', 'ref']:
        raw = inv.get(field) or ''
        extracted = extract_struct_ref(raw)
        if extracted:
            norm = normalize_struct(extracted)
            if norm and norm not in inv_by_struct:
                inv_by_struct[norm] = inv

print(f"  Factures avec ref structurée indexée : {len(inv_by_struct)}")

# ═══════════════════════════════════════════════════════════════════════════════
# 3. CHARGER LES FACTURES FOURNISSEURS OUVERTES
# ═══════════════════════════════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════════════════════════════
# 4. MATCHING ENCAISSEMENTS
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[4] Matching encaissements ...")
print(f"    Seuil write-off : {WRITE_OFF_SEUIL:.2f} EUR")

results_entrees = {
    'MATCH_EXACT':        [],   # match parfait (P1/P2/P3)
    'MATCH_ECART_CENTS':  [],   # écart <= seuil → write-off prévu
    'MATCH_PARTIEL':      [],   # paiement < facture (acompte probable)
    'MULTI_CANDIDATS':    [],   # plusieurs candidats, choix impossible
    'AUCUN_MATCH':        [],
}

for bsl in bsl_entrees:
    amt       = round(bsl['amount'], 2)
    pid       = bsl['partner_id'][0] if bsl['partner_id'] else 0
    pay_ref   = bsl.get('payment_ref') or ''
    narration = bsl.get('narration') or ''
    combined  = pay_ref + ' ' + narration

    best_match  = None
    match_type  = None
    match_prio  = None
    candidates  = []

    # ── P1 : communication structurée ─────────────────────────────────────
    struct_norm = normalize_struct(extract_struct_ref(combined))
    if not struct_norm:
        struct_norm = normalize_struct(combined.strip())

    if struct_norm and struct_norm in inv_by_struct:
        inv_candidate = inv_by_struct[struct_norm]
        inv_amt = round(inv_candidate['amount_residual'], 2)
        ecart = abs(amt - inv_amt)
        if ecart == 0.0:
            best_match = inv_candidate
            match_type = 'MATCH_EXACT'
            match_prio = 'P1_STRUCT'
        elif ecart <= WRITE_OFF_SEUIL:
            best_match = inv_candidate
            match_type = 'MATCH_ECART_CENTS'
            match_prio = 'P1_STRUCT_ECART'
        elif amt < inv_amt:
            best_match = inv_candidate
            match_type = 'MATCH_PARTIEL'
            match_prio = 'P1_STRUCT_PARTIEL'
        # Si amt > inv_amt (trop perçu) → multi-candidats possibles, pas de match auto
        else:
            candidates.append(('P1_STRUCT_TROP_PERCU', inv_candidate))

    # ── P2 : montant exact + partner ──────────────────────────────────────
    if best_match is None and pid:
        key = (amt, pid)
        if key in inv_by_amt_partner:
            cands = inv_by_amt_partner[key]
            if len(cands) == 1:
                best_match = cands[0]
                match_type = 'MATCH_EXACT'
                match_prio = 'P2_AMT_PARTNER'
            else:
                candidates.extend([('P2_AMT_PARTNER_MULTI', c) for c in cands])

    # ── P2b : montant exact + partner (tolérance cents) ───────────────────
    if best_match is None and pid and not candidates:
        for delta in [0.01, 0.02, 0.03, 0.04, 0.05]:
            for sign in [1, -1]:
                test_amt = round(amt + sign * delta, 2)
                key = (test_amt, pid)
                if key in inv_by_amt_partner:
                    cands = inv_by_amt_partner[key]
                    if len(cands) == 1:
                        ecart = abs(amt - test_amt)
                        if ecart <= WRITE_OFF_SEUIL:
                            best_match = cands[0]
                            match_type = 'MATCH_ECART_CENTS'
                            match_prio = f'P2b_AMT_PARTNER_ECART_{ecart:.2f}'
                            break
            if best_match:
                break

    # ── P3 : montant exact, un seul candidat global ───────────────────────
    if best_match is None and not candidates:
        if amt in inv_by_amount:
            cands = inv_by_amount[amt]
            if len(cands) == 1:
                best_match = cands[0]
                match_type = 'MATCH_EXACT'
                match_prio = 'P3_AMT_UNIQUE'
            else:
                candidates.extend([('P3_AMT_MULTI', c) for c in cands])

    # ── P3b : montant approché, unique candidat global ────────────────────
    if best_match is None and not candidates:
        for delta in [0.01, 0.02, 0.03, 0.04, 0.05]:
            for sign in [1, -1]:
                test_amt = round(amt + sign * delta, 2)
                if test_amt in inv_by_amount:
                    cands = inv_by_amount[test_amt]
                    if len(cands) == 1:
                        ecart = abs(amt - test_amt)
                        if ecart <= WRITE_OFF_SEUIL:
                            best_match = cands[0]
                            match_type = 'MATCH_ECART_CENTS'
                            match_prio = f'P3b_AMT_ECART_{ecart:.2f}'
                            break
            if best_match:
                break

    # ── Résolution finale ──────────────────────────────────────────────────
    if best_match:
        entry = {
            'bsl_id':    bsl['id'],
            'date':      bsl['date'],
            'payment_ref': pay_ref[:60],
            'amount':    amt,
            'partner':   bsl['partner_id'][1] if bsl['partner_id'] else bsl.get('partner_name') or 'INCONNU',
            'inv_name':  best_match['name'],
            'inv_id':    best_match['id'],
            'inv_residual': round(best_match['amount_residual'], 2),
            'inv_partner': best_match['partner_id'][1] if best_match['partner_id'] else '?',
            'ecart':     round(amt - round(best_match['amount_residual'], 2), 2),
            'prio':      match_prio,
        }
        results_entrees[match_type].append(entry)
    elif candidates:
        results_entrees['MULTI_CANDIDATS'].append({
            'bsl_id':   bsl['id'],
            'date':     bsl['date'],
            'payment_ref': pay_ref[:60],
            'amount':   amt,
            'partner':  bsl['partner_id'][1] if bsl['partner_id'] else bsl.get('partner_name') or 'INCONNU',
            'nb_cands': len(candidates),
            'cands_preview': [c[1]['name'] for c in candidates[:3]],
        })
    else:
        results_entrees['AUCUN_MATCH'].append({
            'bsl_id':   bsl['id'],
            'date':     bsl['date'],
            'payment_ref': pay_ref[:60],
            'amount':   amt,
            'partner':  bsl['partner_id'][1] if bsl['partner_id'] else bsl.get('partner_name') or 'INCONNU',
        })

# ═══════════════════════════════════════════════════════════════════════════════
# 5. CATÉGORISATION DÉCAISSEMENTS
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[5] Catégorisation décaissements ...")

# Mots-clés par catégorie (insensible à la casse)
KEYWORDS = {
    'DOMICILIATION_SEPA': [
        'domiciliation', 'sdd', 'sepa dd', 'prelevement', 'incasso',
        'core dd', 'b2b dd',
    ],
    'CARTE_PUBLICITE': [
        'mastercard', 'visa', 'google', 'meta ', 'facebook', 'instagram',
        'linkedin', 'microsoft', 'apple ', 'stripe ', 'mollie', 'paypal',
        'amazon ', 'aws ', 'shopify', 'sendcloud', 'mailchimp',
        'ads ', 'advertis',
    ],
    'VIREMENT_ODIGO': [
        'odigo', 'rtgs', 'fedwire',
    ],
    'SALAIRE_ONSS': [
        'salaire', 'salary', 'loon', 'onss', 'dimona', 'secretariat social',
        'groupe s', 'sodexo', 'edenred', 'ucm ', 'partena',
    ],
    'TVA_FISC': [
        'tva', 'btw', 'taxe', 'belasting', 'spp finances', 'spf finances',
        'fisc', 'ipp ', 'isoc', 'impot',
    ],
    'LOCATION_UTILITES': [
        'loyer', 'huur', 'electr', 'proximus', 'telenet', 'orange ',
        'fluvius', 'sibelga', 'ores ', 'swde', 'eau ', 'assurance',
        'verzekering',
    ],
}

def categorize_sortie(bsl):
    ref = ((bsl.get('payment_ref') or '') + ' ' + (bsl.get('narration') or '')).lower()
    for cat, kws in KEYWORDS.items():
        for kw in kws:
            if kw in ref:
                return cat
    return 'AUTRE'

results_sorties = {
    'VENDOR_BILL_MATCH':   [],  # match facture fournisseur ouverte par montant exact
    'DOMICILIATION_SEPA':  [],
    'CARTE_PUBLICITE':     [],
    'VIREMENT_ODIGO':      [],
    'SALAIRE_ONSS':        [],
    'TVA_FISC':            [],
    'LOCATION_UTILITES':   [],
    'AUTRE':               [],  # nécessite imputation manuelle
}

for bsl in bsl_sorties:
    amt_abs = round(abs(bsl['amount']), 2)
    pid     = bsl['partner_id'][0] if bsl['partner_id'] else 0

    # Test match facture fournisseur (montant abs = résiduel fournisseur)
    if amt_abs in vbill_by_amount:
        cands = vbill_by_amount[amt_abs]
        if len(cands) == 1:
            vb = cands[0]
            results_sorties['VENDOR_BILL_MATCH'].append({
                'bsl_id':      bsl['id'],
                'date':        bsl['date'],
                'payment_ref': (bsl.get('payment_ref') or '')[:60],
                'amount':      -amt_abs,
                'vendor_bill': vb['name'],
                'vb_id':       vb['id'],
                'vb_partner':  vb['partner_id'][1] if vb['partner_id'] else '?',
                'vb_residual': round(vb['amount_residual'], 2),
            })
            continue
        elif len(cands) > 1:
            # Multi-candidats → AUTRE (pas de match auto)
            cat = categorize_sortie(bsl)
            results_sorties[cat].append({
                'bsl_id':      bsl['id'],
                'date':        bsl['date'],
                'payment_ref': (bsl.get('payment_ref') or '')[:60],
                'amount':      -amt_abs,
                'note':        f'multi-cands vendor bill ({len(cands)})',
            })
            continue

    # Catégorisation par mots-clés
    cat = categorize_sortie(bsl)
    results_sorties[cat].append({
        'bsl_id':      bsl['id'],
        'date':        bsl['date'],
        'payment_ref': (bsl.get('payment_ref') or '')[:60],
        'amount':      -amt_abs,
        'partner':     bsl['partner_id'][1] if bsl['partner_id'] else bsl.get('partner_name') or 'INCONNU',
    })

# ═══════════════════════════════════════════════════════════════════════════════
# 6. AFFICHAGE RÉSULTATS
# ═══════════════════════════════════════════════════════════════════════════════

def sep(title=''):
    print('\n' + '─' * 72)
    if title:
        print(f'  {title}')
        print('─' * 72)

sep()
print("RÉSULTATS DRY-RUN")
sep()

# ── ENCAISSEMENTS ─────────────────────────────────────────────────────────────
print(f"\n{'':4}ENCAISSEMENTS ({len(bsl_entrees)} lignes)")
print(f"{'':4}{'─'*60}")

total_encaiss_auto = 0
for cls in ['MATCH_EXACT', 'MATCH_ECART_CENTS', 'MATCH_PARTIEL', 'MULTI_CANDIDATS', 'AUCUN_MATCH']:
    n = len(results_entrees[cls])
    flag = ''
    if cls == 'MATCH_EXACT':
        flag = '  <-- reconciliable auto ✓'
        total_encaiss_auto += n
    elif cls == 'MATCH_ECART_CENTS':
        flag = '  <-- reconciliable avec write-off'
        total_encaiss_auto += n
    print(f"    {cls:22s} : {n:3d}{flag}")

print()
print(f"    TOTAL reconciliable encaissements : "
      f"{len(results_entrees['MATCH_EXACT']) + len(results_entrees['MATCH_ECART_CENTS'])} / {len(bsl_entrees)}")

# Détail MATCH_EXACT
if results_entrees['MATCH_EXACT']:
    sep("DÉTAIL — MATCH_EXACT encaissements")
    for e in results_entrees['MATCH_EXACT']:
        prio_short = e['prio'].replace('_', ' ')
        print(f"  {e['date']} | {e['amount']:>10.2f} EUR | {e['partner'][:30]:30s} | "
              f"{e['inv_name']:20s} | {prio_short}")

# Détail MATCH_ECART_CENTS
if results_entrees['MATCH_ECART_CENTS']:
    sep("DÉTAIL — MATCH_ECART_CENTS (write-off prévu)")
    print(f"  {'Date':10s} | {'Montant BSL':>11s} | {'Résiduel INV':>12s} | {'Ecart':>6s} | {'Facture':20s} | Partenaire")
    print(f"  {'-'*10}-+-{'-'*11}-+-{'-'*12}-+-{'-'*6}-+-{'-'*20}-+-{'-'*30}")
    for e in results_entrees['MATCH_ECART_CENTS']:
        print(f"  {e['date']} | {e['amount']:>11.2f} | {e['inv_residual']:>12.2f} | {e['ecart']:>+6.2f} | "
              f"{e['inv_name']:20s} | {e['inv_partner'][:30]}")

# Détail MATCH_PARTIEL
if results_entrees['MATCH_PARTIEL']:
    sep("DÉTAIL — MATCH_PARTIEL (acomptes — à valider manuellement)")
    for e in results_entrees['MATCH_PARTIEL']:
        print(f"  {e['date']} | paiement {e['amount']:>10.2f} EUR < facture {e['inv_residual']:>10.2f} EUR | "
              f"{e['inv_name']} | {e['partner'][:30]}")

# Détail MULTI_CANDIDATS
if results_entrees['MULTI_CANDIDATS']:
    sep("DÉTAIL — MULTI_CANDIDATS (choix manuel requis)")
    for e in results_entrees['MULTI_CANDIDATS']:
        print(f"  {e['date']} | {e['amount']:>10.2f} EUR | {e['partner'][:30]:30s} | "
              f"{e['nb_cands']} candidats : {', '.join(e['cands_preview'][:3])}")

# Détail AUCUN_MATCH
if results_entrees['AUCUN_MATCH']:
    sep("DÉTAIL — AUCUN_MATCH encaissements (investigation requise)")
    for e in results_entrees['AUCUN_MATCH']:
        print(f"  {e['date']} | {e['amount']:>10.2f} EUR | {e['partner'][:30]:30s} | ref: {e['payment_ref']}")

# ── DÉCAISSEMENTS ──────────────────────────────────────────────────────────────
sep()
print(f"\n{'':4}DÉCAISSEMENTS ({len(bsl_sorties)} lignes)")
print(f"{'':4}{'─'*60}")

total_sorties_auto = len(results_sorties['VENDOR_BILL_MATCH'])
total_manuel       = sum(len(results_sorties[k]) for k in results_sorties if k != 'VENDOR_BILL_MATCH')

for cat in ['VENDOR_BILL_MATCH', 'DOMICILIATION_SEPA', 'CARTE_PUBLICITE',
            'VIREMENT_ODIGO', 'SALAIRE_ONSS', 'TVA_FISC', 'LOCATION_UTILITES', 'AUTRE']:
    n = len(results_sorties[cat])
    flag = '  <-- reconciliable auto ✓' if cat == 'VENDOR_BILL_MATCH' else '  (imputation manuelle)'
    print(f"    {cat:22s} : {n:3d}{flag}")

print()
print(f"    Matchables vendor bill (auto)  : {total_sorties_auto} / {len(bsl_sorties)}")
print(f"    Nécessitent imputation manuelle: {total_manuel} / {len(bsl_sorties)}")

# Détail VENDOR_BILL_MATCH
if results_sorties['VENDOR_BILL_MATCH']:
    sep("DÉTAIL — VENDOR_BILL_MATCH décaissements")
    print(f"  {'Date':10s} | {'Montant':>11s} | {'Fournisseur':30s} | {'Bill':20s} | Résiduel bill")
    print(f"  {'-'*10}-+-{'-'*11}-+-{'-'*30}-+-{'-'*20}-+-{'-'*14}")
    for e in results_sorties['VENDOR_BILL_MATCH']:
        print(f"  {e['date']} | {e['amount']:>11.2f} | {e['vb_partner'][:30]:30s} | "
              f"{e['vendor_bill']:20s} | {e['vb_residual']:>14.2f}")

# Détail AUTRE (pour Nicolas)
if results_sorties['AUTRE']:
    sep("DÉTAIL — AUTRE décaissements (imputation manuelle requise — liste Nicolas)")
    for e in results_sorties['AUTRE']:
        print(f"  {e['date']} | {e['amount']:>11.2f} | {e.get('partner','?')[:30]:30s} | {e['payment_ref']}")

# Détail catégories clés
for cat in ['DOMICILIATION_SEPA', 'CARTE_PUBLICITE', 'SALAIRE_ONSS', 'TVA_FISC']:
    if results_sorties[cat]:
        sep(f"DÉTAIL — {cat}")
        for e in results_sorties[cat]:
            print(f"  {e['date']} | {e['amount']:>11.2f} | {e.get('partner','?')[:30]:30s} | {e['payment_ref']}")

# ═══════════════════════════════════════════════════════════════════════════════
# 7. SYNTHÈSE GLOBALE
# ═══════════════════════════════════════════════════════════════════════════════
n_exact       = len(results_entrees['MATCH_EXACT'])
n_ecart       = len(results_entrees['MATCH_ECART_CENTS'])
n_partiel     = len(results_entrees['MATCH_PARTIEL'])
n_multi       = len(results_entrees['MULTI_CANDIDATS'])
n_aucun       = len(results_entrees['AUCUN_MATCH'])
n_vendor      = len(results_sorties['VENDOR_BILL_MATCH'])
n_manuel      = sum(len(results_sorties[k]) for k in results_sorties if k != 'VENDOR_BILL_MATCH')

total_auto    = n_exact + n_ecart + n_vendor
total_lines   = len(bsl_all)

sep()
print("SYNTHÈSE GLOBALE")
sep()
print(f"""
  Seuil write-off retenu           : {WRITE_OFF_SEUIL:.2f} EUR
  Justification : arrondi TVA 21%, Stripe/Mollie fees ≤ 0,02 EUR,
                  0,05 EUR couvre sans dépasser le seuil 0,10 EUR
                  qui serait trop permissif sur factures B2C 10-20 EUR.

  ┌─ ENCAISSEMENTS ({len(bsl_entrees):3d} lignes) ─────────────────────────────────────┐
  │  MATCH_EXACT       (auto, 0 risque)   : {n_exact:3d}                           │
  │  MATCH_ECART_CENTS (write-off ≤ 0,05) : {n_ecart:3d}                           │
  │  MATCH_PARTIEL     (acompte, manuel)  : {n_partiel:3d}                           │
  │  MULTI_CANDIDATS   (choix manuel)     : {n_multi:3d}                           │
  │  AUCUN_MATCH       (investigation)    : {n_aucun:3d}                           │
  │                                                                         │
  │  Reconciliables auto (EXACT + ECART)  : {n_exact + n_ecart:3d} / {len(bsl_entrees)}                    │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─ DÉCAISSEMENTS ({len(bsl_sorties):3d} lignes) ─────────────────────────────────────┐
  │  VENDOR_BILL_MATCH (auto, 0 risque)   : {n_vendor:3d}                           │
  │  Catégorisés (imputation manuelle)    : {n_manuel:3d}                           │
  │    dont DOMICILIATION_SEPA            : {len(results_sorties['DOMICILIATION_SEPA']):3d}                           │
  │    dont CARTE_PUBLICITE               : {len(results_sorties['CARTE_PUBLICITE']):3d}                           │
  │    dont SALAIRE_ONSS                  : {len(results_sorties['SALAIRE_ONSS']):3d}                           │
  │    dont TVA_FISC                      : {len(results_sorties['TVA_FISC']):3d}                           │
  │    dont LOCATION_UTILITES             : {len(results_sorties['LOCATION_UTILITES']):3d}                           │
  │    dont VIREMENT_ODIGO                : {len(results_sorties['VIREMENT_ODIGO']):3d}                           │
  │    dont AUTRE (investigation)         : {len(results_sorties['AUTRE']):3d}                           │
  │                                                                         │
  │  Reconciliables auto vendor bill      : {n_vendor:3d} / {len(bsl_sorties)}                   │
  └─────────────────────────────────────────────────────────────────────────┘

  ╔═════════════════════════════════════════════════════════════════════════╗
  ║  TOTAL RÉCONCILIABLE AUTO EN TOUTE SÉCURITÉ : {total_auto:3d} / {total_lines}           ║
  ║    = MATCH_EXACT ({n_exact}) + MATCH_ECART_CENTS ({n_ecart}) + VENDOR_BILL ({n_vendor})     ║
  ║                                                                         ║
  ║  RESTE MANUEL / INVESTIGATION         : {total_lines - total_auto:3d} / {total_lines}           ║
  ╚═════════════════════════════════════════════════════════════════════════╝

  RAPPEL : ce script est EN LECTURE SEULE. Aucune écriture effectuée.
  Après validation du dry-run par Nicolas → GO → script lettrage_04_apply.py
""")

print("Script terminé. Aucune écriture effectuée.")
