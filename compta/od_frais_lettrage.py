import xmlrpc.client

URL="https://tea-tree.odoo.com"; DB="tsc-be-tea-tree-main-18515272"
USER="nicolas.raes@teatower.com"; PWD="Teatower123"
common=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid=common.authenticate(DB,USER,PWD,{})
m=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model,method,args,kw=None): return m.execute_kw(DB,uid,PWD,model,method,args,kw or {})

ACC_499 = 221

# Toutes les OD creees (move_id, bsl_id, label) - dans l'ordre de creation
# Format: (od_name, od_move_id, bsl_id)
# Lire les OD par ref pour retrouver leurs move_ids
OD_REFS = [
    ('ING frais tenue de compte oct.2025 n302279940',         14290),
    ('ING cotisation Mastercard Business annuelle 5476-85',   14293),
    ('ING frais tenue de compte n2025/01/003272604',          14898),
    ('ING frais tenue de compte n2025/01/003407662',          14909),
    ('ING correction cotisation Mastercard',                  16266),
    ('ING frais tenue de compte n2026/01/003774109',          16306),
    ('ING cotisation mensuelle Mastercard fev.2026',          16935),
    ('ING cotisation mensuelle Mastercard mars 2026',         17632),
    ('ING micro-frais n2026/01/004564419',                    17816),
    ('ING cotisation mensuelle Mastercard avr.2026',          18269),
    ('ING cotisation mensuelle Mastercard mai 2026',          18818),
    ('ING frais tenue de compte n2026/01/005069685 mai 2026', 18817),
    ('ING frais tenue de compte n2026/01/005196418',          19004),
    ('Q8 AYE AdBlue',                                         16743),
    ('Q8 AYE carburant',                                      16745),
    ('AUTOSECURITE STATION 7 AYE controle technique',         17557),
    ('Sixt Bruxelles location vehicule',                      17845),
    ('sr-Get your mug Liege',                                 17680),
    ('AU BLEU SARRAU Erpent',                                 17983),
    ('Adobe Creative Cloud Dublin mars 2026',                 17245),
    ('Adobe Creative Cloud Dublin juin 2026',                 19069),
    ('Lyreco Belgium NV Vottem',                              16181),
    ('parkservice24.de Dusseldorf parking',                   16853),
    ('AMZN Mktp FR HX9JL1735',                               14012),
    ('AMZN Mktp FR 8L1118EX5',                               14191),
    ('AMZN Mktp FR ZX5DY2TC4',                               14950),
    ('AMAZON.BE QG0YW6QT5',                                  17157),
    ('WWW.AMAZON PF6112WV5',                                  17158),
    ('AMAZON.BE WA8A75505',                                   17315),
    ('AMAZON.BE N66EQ5IL4',                                   18401),
    ('HomeDeco.nl Amsterdam',                                 16393),
    ('PLAN-IT 4203 Rocourt',                                  16759),
]

results = []

for (od_ref, bsl_id) in OD_REFS:
    # Trouver l'OD par ref (creee recemment - journal MISC id=11, state=posted)
    od_moves = call('account.move', 'search_read', [
        [('journal_id','=',11), ('ref','=',od_ref), ('state','=','posted')]
    ], {'fields':['id','name','date'], 'order':'id desc', 'limit':1})

    if not od_moves:
        results.append({'ref': od_ref, 'bsl_id': bsl_id, 'od_name': 'INTROUVABLE', 'lettre': 'ERREUR: OD non trouvee'})
        continue

    od_move = od_moves[0]
    od_move_id = od_move['id']
    od_name = od_move['name']

    # Ligne 499000 dans l'OD
    od_lines = call('account.move.line', 'search_read', [
        [('move_id','=',od_move_id), ('account_id','=',ACC_499), ('reconciled','=',False)]
    ], {'fields':['id','debit','credit','reconciled','amount_residual']})

    # Ligne 499000 dans la BSL
    bsl = call('account.bank.statement.line', 'read', [[bsl_id]], {'fields':['id','move_id','is_reconciled','amount']})[0]

    if bsl['is_reconciled']:
        results.append({'ref': od_ref, 'bsl_id': bsl_id, 'od_name': od_name, 'lettre': 'DEJA LETTRE'})
        continue

    bsl_move_id = bsl['move_id'][0]
    bk_lines = call('account.move.line', 'search_read', [
        [('move_id','=',bsl_move_id), ('account_id','=',ACC_499), ('reconciled','=',False)]
    ], {'fields':['id','debit','credit','reconciled','amount_residual']})

    if not od_lines:
        results.append({'ref': od_ref, 'bsl_id': bsl_id, 'od_name': od_name, 'lettre': 'ERREUR: ligne 499000 OD deja lettree ou absente'})
        continue
    if not bk_lines:
        results.append({'ref': od_ref, 'bsl_id': bsl_id, 'od_name': od_name, 'lettre': 'ERREUR: ligne 499000 BNK absente'})
        continue

    od_line_id = od_lines[0]['id']
    bk_line_id = bk_lines[0]['id']

    # Lettrage - reconcile retourne None que xmlrpc ne peut pas serialiser => attraper TypeError
    lettre = False
    try:
        call('account.move.line', 'reconcile', [[od_line_id, bk_line_id]])
        lettre = True
    except Exception as e:
        err_str = str(e)
        if 'cannot marshal None' in err_str or 'TypeError' in err_str:
            # Odoo a execute reconcile avec succes, None = retour vide normal
            lettre = True
        else:
            lettre = f"ERREUR: {err_str[:100]}"

    # Verification finale
    bsl_check = call('account.bank.statement.line', 'read', [[bsl_id]], {'fields':['is_reconciled']})[0]
    lettre_confirme = bsl_check['is_reconciled']

    results.append({
        'ref': od_ref,
        'bsl_id': bsl_id,
        'od_name': od_name,
        'lettre': 'OUI' if lettre_confirme else f"NON (lettre={lettre})"
    })
    print(f"  {od_name}  bsl={bsl_id}  lettre={'OUI' if lettre_confirme else 'NON'}")

print("\n=== RECAP LETTRAGE ===")
nb_ok = sum(1 for r in results if r['lettre'] == 'OUI' or r['lettre'] == 'DEJA LETTRE')
nb_err = len(results) - nb_ok
print(f"Lettre OK: {nb_ok}/{len(results)}  Erreurs: {nb_err}")
for r in results:
    status = r['lettre']
    print(f"  {r['od_name']:<25}  bsl={r['bsl_id']}  {status}")
