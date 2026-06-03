# -*- coding: utf-8 -*-
"""
LETTRAGE 07 — CLEANUP : annulation paiements orphelins + re-post moves BSL
Date : 2026-06-03

CONSTAT :
  6 paiements PAY00628→PAY00633 (ids 7274..7279) sont state=in_process,
  move_id=False (aucune écriture comptable réelle), reliés aux factures via
  reconciled_invoice_ids → les factures apparaissent "in_payment" artificiellement.

  Les 6 moves de BSL ont été passés en draft (button_draft) — ils sont équilibrés
  (550001 D / 499000 C), PAS de write-off ajouté. Il faut les reposter.

OBJECTIF "état propre" :
  - Paiements 7274..7279 supprimés ou annulés (plus aucun lien avec les factures)
  - Factures repassent payment_state=not_paid, amount_residual = montant plein
  - Moves BSL repassent state=posted, bsl.is_reconciled=False

PHASES :
  PHASE 1 : test sur paire 18827 / 7274 / INV/2026/02166 uniquement → STOP.
    Si facture NOT_PAID + move BSL posted + non-réconcilié → PHASE 2.
    Sinon : STOP + détail erreur.

Paires (bsl_id, pay_id, inv_name) :
  18827 / 7274 / INV/2026/02166
  18688 / 7275 / INV/2026/02537
  18235 / 7276 / INV/2026/01791
  17821 / 7277 / INV/2026/02007
  17574 / 7278 / INV/2026/02801
  14600 / 7279 / INV/2026/01962
"""

import xmlrpc.client

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

def hr(char="=", n=72):
    print(char * n)

# ══════════════════════════════════════════════════════════════════════════════
# DONNÉES DES 6 PAIRES
# ══════════════════════════════════════════════════════════════════════════════
PAIRS = [
    {'bsl_id': 18827, 'pay_id': 7274, 'inv_name': 'INV/2026/02166'},
    {'bsl_id': 18688, 'pay_id': 7275, 'inv_name': 'INV/2026/02537'},
    {'bsl_id': 18235, 'pay_id': 7276, 'inv_name': 'INV/2026/01791'},
    {'bsl_id': 17821, 'pay_id': 7277, 'inv_name': 'INV/2026/02007'},
    {'bsl_id': 17574, 'pay_id': 7278, 'inv_name': 'INV/2026/02801'},
    {'bsl_id': 14600, 'pay_id': 7279, 'inv_name': 'INV/2026/01962'},
]


# ══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ══════════════════════════════════════════════════════════════════════════════

def read_payment(pay_id):
    """Lit l'état du paiement."""
    rows = call('account.payment', 'read',
        [[pay_id]],
        {'fields': ['name', 'state', 'move_id', 'is_reconciled',
                    'reconciled_invoice_ids', 'amount', 'partner_id']}
    )
    return rows[0] if rows else None


def read_invoice(inv_name):
    """Lit payment_state et amount_residual de la facture."""
    rows = call('account.move', 'search_read',
        [[['name', '=', inv_name], ['move_type', '=', 'out_invoice']]],
        {'fields': ['id', 'name', 'payment_state', 'amount_residual', 'amount_total']}
    )
    return rows[0] if rows else None


def read_bsl(bsl_id):
    """Lit move_id, is_reconciled et state du move de la BSL."""
    rows = call('account.bank.statement.line', 'read',
        [[bsl_id]],
        {'fields': ['move_id', 'is_reconciled', 'amount', 'partner_id']}
    )
    if not rows:
        return None
    bsl = rows[0]
    move_id = bsl['move_id'][0] if bsl.get('move_id') else None
    move_state = None
    if move_id:
        mv = call('account.move', 'read', [[move_id]], {'fields': ['state', 'name']})
        if mv:
            move_state = mv[0]['state']
    bsl['_move_id']    = move_id
    bsl['_move_state'] = move_state
    return bsl


def try_cancel_payment(pay_id, pay_name):
    """
    Tente action_cancel sur le paiement.
    En Odoo 18 un paiement in_process sans écriture comptable :
      - action_cancel peut être disponible → tente d'abord
      - sinon tente action_draft puis unlink
      - en dernier ressort : unlink direct
    Retourne (méthode_utilisée, ok, message).
    """
    # Essai 1 : action_cancel
    try:
        call('account.payment', 'action_cancel', [[pay_id]])
        return 'action_cancel', True, 'OK'
    except xmlrpc.client.Fault as f:
        msg1 = str(f.faultString)[:200]
        print(f"    action_cancel refusé : {msg1[:120]}")

    # Essai 2 : action_draft (reset to draft) puis unlink
    try:
        call('account.payment', 'action_draft', [[pay_id]])
        print(f"    action_draft OK → tentative unlink ...")
        call('account.payment', 'unlink', [[pay_id]])
        return 'action_draft+unlink', True, 'OK'
    except xmlrpc.client.Fault as f:
        msg2 = str(f.faultString)[:200]
        print(f"    action_draft ou unlink refusé : {msg2[:120]}")

    # Essai 3 : unlink direct (si pas d'écriture comptable, ça devrait passer)
    try:
        call('account.payment', 'unlink', [[pay_id]])
        return 'unlink_direct', True, 'OK'
    except xmlrpc.client.Fault as f:
        msg3 = str(f.faultString)[:200]
        print(f"    unlink direct refusé : {msg3[:120]}")
        return 'all_failed', False, msg3


def post_bsl_move(bsl_id, move_id):
    """
    Re-poste le move de la BSL s'il est en draft.
    Retourne (ok, message).
    """
    # Vérifier état actuel
    mv = call('account.move', 'read', [[move_id]], {'fields': ['state', 'name']})
    if not mv:
        return False, f"move {move_id} introuvable"
    state = mv[0]['state']
    name  = mv[0].get('name', '?')
    print(f"    Move BSL {bsl_id} : id={move_id}, name='{name}', state={state}")

    if state == 'posted':
        print(f"    Déjà posted — rien à faire.")
        return True, 'already_posted'

    if state != 'draft':
        return False, f"state inattendu '{state}' — ne peut pas poster"

    try:
        call('account.move', 'action_post', [[move_id]])
        # Vérifier après
        mv2 = call('account.move', 'read', [[move_id]], {'fields': ['state']})
        new_state = mv2[0]['state'] if mv2 else '?'
        if new_state == 'posted':
            print(f"    action_post OK → state=posted")
            return True, 'posted'
        else:
            return False, f"action_post appelé mais state={new_state} après"
    except xmlrpc.client.Fault as f:
        msg = str(f.faultString)[:200]
        print(f"    action_post refusé : {msg[:120]}")
        return False, msg


def verify_pair(bsl_id, pay_id, inv_name):
    """
    Vérifie l'état final de la paire :
      - paiement : existe encore ? state ?
      - facture : payment_state, amount_residual
      - BSL : is_reconciled, move state
    Retourne un dict.
    """
    # Paiement
    pay_exists = False
    pay_state  = None
    try:
        p = call('account.payment', 'read', [[pay_id]], {'fields': ['state', 'name']})
        if p:
            pay_exists = True
            pay_state  = p[0]['state']
    except Exception:
        pass

    # Facture
    inv = read_invoice(inv_name)
    inv_ps  = inv['payment_state']    if inv else None
    inv_res = inv['amount_residual']  if inv else None
    inv_tot = inv['amount_total']     if inv else None

    # BSL
    bsl = read_bsl(bsl_id)
    bsl_rec        = bsl['is_reconciled']  if bsl else None
    bsl_move_state = bsl['_move_state']    if bsl else None
    bsl_move_id    = bsl['_move_id']       if bsl else None

    return {
        'pay_exists': pay_exists,
        'pay_state': pay_state,
        'inv_payment_state': inv_ps,
        'inv_amount_residual': inv_res,
        'inv_amount_total': inv_tot,
        'bsl_is_reconciled': bsl_rec,
        'bsl_move_state': bsl_move_state,
        'bsl_move_id': bsl_move_id,
    }


def is_clean(v):
    """
    Retourne True si la paire est dans l'état propre attendu :
      - paiement inexistant OU annulé (cancelled/draft sans écriture)
      - facture payment_state = not_paid, amount_residual = amount_total
      - BSL is_reconciled = False, move_state = posted
    """
    pay_ok = (not v['pay_exists']) or (v['pay_state'] in ('cancel', 'cancelled', 'draft'))
    inv_ok = (v['inv_payment_state'] == 'not_paid')
    bsl_ok = (v['bsl_is_reconciled'] is False) and (v['bsl_move_state'] == 'posted')
    return pay_ok and inv_ok and bsl_ok


def process_pair(pair):
    """
    Traite une paire. Retourne dict résultat.
    """
    bsl_id   = pair['bsl_id']
    pay_id   = pair['pay_id']
    inv_name = pair['inv_name']

    hr("-")
    print(f"  PAIRE : BSL {bsl_id} / PAY id={pay_id} / {inv_name}")
    hr("-")

    result = {
        'bsl_id': bsl_id, 'pay_id': pay_id, 'inv_name': inv_name,
        'status': None, 'error': None,
        'cancel_method': None, 'post_method': None,
    }

    # ── ÉTAT INITIAL ──────────────────────────────────────────────────────────
    print("\n  [DIAG INITIAL]")
    pay = read_payment(pay_id)
    if pay:
        print(f"    Payment id={pay_id} : name={pay.get('name')}, state={pay.get('state')}, "
              f"move_id={pay.get('move_id')}, "
              f"reconciled_invoice_ids={pay.get('reconciled_invoice_ids')}")
    else:
        print(f"    Payment id={pay_id} : INTROUVABLE (déjà supprimé ?)")

    inv = read_invoice(inv_name)
    if inv:
        print(f"    Facture {inv_name} : payment_state={inv.get('payment_state')}, "
              f"amount_residual={inv.get('amount_residual')}, "
              f"amount_total={inv.get('amount_total')}")
    else:
        print(f"    Facture {inv_name} : INTROUVABLE")

    bsl = read_bsl(bsl_id)
    if bsl:
        print(f"    BSL {bsl_id} : is_reconciled={bsl.get('is_reconciled')}, "
              f"move_id={bsl.get('_move_id')}, move_state={bsl.get('_move_state')}")
    else:
        print(f"    BSL {bsl_id} : INTROUVABLE")

    # Si paiement déjà absent → check si état propre
    if not pay:
        # Le paiement a peut-être déjà été supprimé dans un run précédent
        v = verify_pair(bsl_id, pay_id, inv_name)
        if is_clean(v):
            result['status'] = 'SKIP_DEJA_PROPRE'
            result.update(v)
            print("\n  --> Paiement déjà absent, état propre détecté. SKIP.")
            return result
        # Sinon il faut quand même reposter le move BSL
        print("\n  --> Paiement absent mais état pas encore propre — poursuite sur BSL.")

    # ── ÉTAPE 1 : ANNULER / SUPPRIMER LE PAIEMENT ────────────────────────────
    if pay:
        print(f"\n  [1] Annulation/suppression du paiement id={pay_id} ...")
        method, ok, msg = try_cancel_payment(pay_id, pay.get('name', '?'))
        result['cancel_method'] = method
        if not ok:
            result['status'] = 'ERROR'
            result['error']  = f"Impossible de supprimer/annuler le paiement : {msg}"
            print(f"  ERREUR : {result['error']}")
            return result
        print(f"  Paiement supprimé/annulé via '{method}'")

        # Vérifier que la facture est bien revenue en not_paid
        inv_check = read_invoice(inv_name)
        inv_ps_after = inv_check['payment_state'] if inv_check else '?'
        print(f"  Facture {inv_name} après suppression paiement : payment_state={inv_ps_after}")
        if inv_ps_after not in ('not_paid', 'partial'):
            # partial peut arriver si remises ou avoirs partiels — acceptable
            if inv_ps_after == 'paid':
                # paiement disparu mais facture paid → bizarre, continuer quand même
                print(f"  ATTENTION : facture toujours paid après suppression paiement — état à analyser")
    else:
        print(f"\n  [1] Paiement id={pay_id} absent — étape 1 sautée.")
        result['cancel_method'] = 'already_absent'

    # ── ÉTAPE 2 : RE-POSTER LE MOVE DE LA BSL ─────────────────────────────────
    bsl = read_bsl(bsl_id)
    if not bsl:
        result['status'] = 'ERROR'
        result['error']  = f"BSL {bsl_id} introuvable"
        print(f"\n  ERREUR : {result['error']}")
        return result

    move_id    = bsl['_move_id']
    move_state = bsl['_move_state']

    if not move_id:
        result['status'] = 'ERROR'
        result['error']  = f"BSL {bsl_id} n'a pas de move_id"
        print(f"\n  ERREUR : {result['error']}")
        return result

    print(f"\n  [2] Re-post du move BSL {bsl_id} (move_id={move_id}, state={move_state}) ...")
    post_ok, post_msg = post_bsl_move(bsl_id, move_id)
    result['post_method'] = post_msg
    if not post_ok:
        result['status'] = 'ERROR'
        result['error']  = f"Impossible de poster le move BSL : {post_msg}"
        print(f"  ERREUR : {result['error']}")
        return result

    # ── ÉTAPE 3 : VÉRIFICATION FINALE ─────────────────────────────────────────
    print(f"\n  [3] Vérification finale ...")
    v = verify_pair(bsl_id, pay_id, inv_name)
    result.update(v)

    print(f"    pay_exists          = {v['pay_exists']}  (pay_state={v['pay_state']})")
    print(f"    inv_payment_state   = {v['inv_payment_state']}")
    print(f"    inv_amount_residual = {v['inv_amount_residual']}")
    print(f"    inv_amount_total    = {v['inv_amount_total']}")
    print(f"    bsl_is_reconciled   = {v['bsl_is_reconciled']}")
    print(f"    bsl_move_state      = {v['bsl_move_state']}")

    if is_clean(v):
        result['status'] = 'OK'
        print(f"\n  RESULTAT : OK — paiement absent/annulé, facture not_paid, BSL move posted non-réconcilié")
    else:
        # Détailler pourquoi pas propre
        issues = []
        if v['pay_exists'] and v['pay_state'] not in ('cancel', 'cancelled', 'draft'):
            issues.append(f"paiement encore actif (state={v['pay_state']})")
        if v['inv_payment_state'] != 'not_paid':
            issues.append(f"facture payment_state={v['inv_payment_state']} (attendu not_paid)")
        if v['bsl_is_reconciled'] is not False:
            issues.append(f"BSL.is_reconciled={v['bsl_is_reconciled']} (attendu False)")
        if v['bsl_move_state'] != 'posted':
            issues.append(f"bsl_move_state={v['bsl_move_state']} (attendu posted)")
        result['status'] = 'WARN'
        result['error']  = " | ".join(issues)
        print(f"\n  RESULTAT : WARN — {result['error']}")

    return result


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — TEST SUR LA PAIRE 18827 / 7274 / INV/2026/02166 UNIQUEMENT
# ══════════════════════════════════════════════════════════════════════════════
hr()
print("LETTRAGE 07 — CLEANUP paiements orphelins + re-post moves BSL")
print("Date : 2026-06-03")
hr()

print("\n" + "=" * 72)
print("PHASE 1 — TEST UNIQUE : BSL 18827 / PAY id=7274 / INV/2026/02166")
print("=" * 72)

test_result = process_pair(PAIRS[0])

print("\n" + "=" * 72)
print("RÉSUMÉ PHASE 1")
print("=" * 72)
print(f"  status               = {test_result.get('status')}")
print(f"  cancel_method        = {test_result.get('cancel_method')}")
print(f"  post_method          = {test_result.get('post_method')}")
print(f"  pay_exists           = {test_result.get('pay_exists')}")
print(f"  inv_payment_state    = {test_result.get('inv_payment_state')}")
print(f"  inv_amount_residual  = {test_result.get('inv_amount_residual')}")
print(f"  bsl_is_reconciled    = {test_result.get('bsl_is_reconciled')}")
print(f"  bsl_move_state       = {test_result.get('bsl_move_state')}")
if test_result.get('error'):
    print(f"  error                = {test_result['error']}")

# ══════════════════════════════════════════════════════════════════════════════
# DÉCISION : PHASE 2 ?
# ══════════════════════════════════════════════════════════════════════════════
PHASE1_OK_STATUTS = {'OK', 'SKIP_DEJA_PROPRE'}

phase1_ok = (
    test_result.get('status') in PHASE1_OK_STATUTS
    and test_result.get('inv_payment_state') == 'not_paid'
    and test_result.get('bsl_move_state') == 'posted'
    and test_result.get('bsl_is_reconciled') is False
)

if not phase1_ok:
    print("\n" + "=" * 72)
    print("PHASE 1 ECHEC OU RESULTAT NON-PROPRE.")
    print("Les 5 paires restantes NE sont PAS traitées.")
    print("Analyser les lignes DIAG ci-dessus.")
    print("=" * 72)
    print("\nScript terminé (PHASE 1 ONLY).")
    import sys; sys.exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — 5 PAIRES RESTANTES
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PHASE 1 OK — DÉROULEMENT DES 5 PAIRES RESTANTES")
print("=" * 72)

all_results = [test_result]
for pair in PAIRS[1:]:
    res = process_pair(pair)
    all_results.append(res)

# ══════════════════════════════════════════════════════════════════════════════
# RÉCAPITULATIF FINAL
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("RÉCAPITULATIF FINAL — 6 PAIRES")
print("=" * 72)
header = f"  {'BSL':>6} | {'PAY_id':>6} | {'Facture':18} | {'Status':12} | {'INV_ps':10} | {'Residual':>9} | {'BSL_rec':7} | {'BSL_mv':7}"
print(header)
print("  " + "-" * (len(header) - 2))

n_ok = n_warn = n_err = n_skip = 0
for r in all_results:
    st = r.get('status', 'ERROR')
    if st == 'OK':             n_ok   += 1
    elif st == 'SKIP_DEJA_PROPRE': n_skip += 1
    elif st == 'WARN':         n_warn += 1
    else:                      n_err  += 1

    res_str = (f"{r['inv_amount_residual']:.2f}"
               if isinstance(r.get('inv_amount_residual'), (int, float))
               else str(r.get('inv_amount_residual', '?')))
    print(f"  {r['bsl_id']:>6} | {r['pay_id']:>6} | {r['inv_name']:18} | {st:12} | "
          f"{str(r.get('inv_payment_state','?')):10} | {res_str:>9} | "
          f"{str(r.get('bsl_is_reconciled','?')):7} | {str(r.get('bsl_move_state','?')):7}")

print(f"\n  OK={n_ok} | SKIP={n_skip} | WARN={n_warn} | ERREUR={n_err}")

if n_err > 0 or n_warn > 0:
    print("\n  DETAIL ANOMALIES :")
    for r in all_results:
        if r.get('status') not in ('OK', 'SKIP_DEJA_PROPRE'):
            print(f"  BSL {r['bsl_id']} / PAY {r['pay_id']} / {r['inv_name']} : {r.get('error')}")

print("\nScript terminé.")
