import xmlrpc.client

URL="https://tea-tree.odoo.com"; DB="tsc-be-tea-tree-main-18515272"
USER="nicolas.raes@teatower.com"; PWD="Teatower123"
common=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid=common.authenticate(DB,USER,PWD,{})
m=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model,method,args,kw=None): return m.execute_kw(DB,uid,PWD,model,method,args,kw or {})

# Comptes finaux
# 650000 = frais bancaires (650100 = "Depreciation of Loan Issue Expenses" trop specifique)
# 611305 = carburant Nicolas Raes
# 611134 = entretien vehicule (controle technique)
# 613550 = location voitures (Sixt)
# 615330 = frais de restaurant
# 615400 = cotisations / Adobe
# 612410 = fournitures de bureau (Amazon, Lyreco, HomeDeco, Plan-it)
# 650110 = frais divers (parking Dusseldorf)
# 499000 = suspense id=221

ACC = {
    '650000': 281,
    '611305': 1202,
    '611134': 1212,
    '613550': 1205,
    '615330': 1147,
    '615400': 874,
    '612410': 849,
    '650110': 902,
    '499000': 221,
}

JOURNAL_MISC = 11

# (bsl_id, date, libelle, montant_bsl, acc_charge_id, acc_charge_code, sens)
# sens 'sortie': D acc_charge / C 499000
# sens 'entree': D 499000 / C acc_charge (correction Mastercard +22.50)
LOT = [
    # LOT A - Frais bancaires ING -> 650000
    (14290, '2025-11-01', 'ING frais tenue de compte oct.2025 n302279940',         -17.30, ACC['650000'], '650000', 'sortie'),
    (14293, '2025-11-01', 'ING cotisation Mastercard Business annuelle 5476-85',   -27.00, ACC['650000'], '650000', 'sortie'),
    (14898, '2025-11-30', 'ING frais tenue de compte n2025/01/003272604',           -9.68, ACC['650000'], '650000', 'sortie'),
    (14909, '2025-12-01', 'ING frais tenue de compte n2025/01/003407662',          -17.30, ACC['650000'], '650000', 'sortie'),
    (16266, '2026-01-30', 'ING correction cotisation Mastercard',                  +22.50, ACC['650000'], '650000', 'entree'),
    (16306, '2026-02-01', 'ING frais tenue de compte n2026/01/003774109',          -40.68, ACC['650000'], '650000', 'sortie'),
    (16935, '2026-03-01', 'ING cotisation mensuelle Mastercard fev.2026',           -2.25, ACC['650000'], '650000', 'sortie'),
    (17632, '2026-04-01', 'ING cotisation mensuelle Mastercard mars 2026',          -2.25, ACC['650000'], '650000', 'sortie'),
    (17816, '2026-04-10', 'ING micro-frais n2026/01/004564419',                    -0.61, ACC['650000'], '650000', 'sortie'),
    (18269, '2026-05-01', 'ING cotisation mensuelle Mastercard avr.2026',           -2.25, ACC['650000'], '650000', 'sortie'),
    (18818, '2026-06-01', 'ING cotisation mensuelle Mastercard mai 2026',           -2.25, ACC['650000'], '650000', 'sortie'),
    (18817, '2026-06-01', 'ING frais tenue de compte n2026/01/005069685 mai 2026', -31.00, ACC['650000'], '650000', 'sortie'),
    (19004, '2026-06-10', 'ING frais tenue de compte n2026/01/005196418',          -14.52, ACC['650000'], '650000', 'sortie'),
    # LOT A - Carburant -> 611305
    (16743, '2026-02-19', 'Q8 AYE AdBlue',                                        -21.75, ACC['611305'], '611305', 'sortie'),
    (16745, '2026-02-19', 'Q8 AYE carburant',                                     -40.00, ACC['611305'], '611305', 'sortie'),
    # LOT A - Vehicule
    (17557, '2026-03-27', 'AUTOSECURITE STATION 7 AYE controle technique',        -77.00, ACC['611134'], '611134', 'sortie'),
    (17845, '2026-04-12', 'Sixt Bruxelles location vehicule',                    -585.98, ACC['613550'], '613550', 'sortie'),
    # LOT A - Restaurant -> 615330
    (17680, '2026-04-03', 'sr-Get your mug Liege',                                -37.60, ACC['615330'], '615330', 'sortie'),
    (17983, '2026-04-17', 'AU BLEU SARRAU Erpent',                               -135.17, ACC['615330'], '615330', 'sortie'),
    # LOT A - Adobe -> 615400
    (17245, '2026-03-14', 'Adobe Creative Cloud Dublin mars 2026',                 -60.49, ACC['615400'], '615400', 'sortie'),
    (19069, '2026-06-14', 'Adobe Creative Cloud Dublin juin 2026',                 -60.49, ACC['615400'], '615400', 'sortie'),
    # LOT A - Fournitures bureau -> 612410
    (16181, '2026-01-24', 'Lyreco Belgium NV Vottem',                             -49.57, ACC['612410'], '612410', 'sortie'),
    # LOT A - Parking -> 650110 frais divers
    (16853, '2026-02-25', 'parkservice24.de Dusseldorf parking',                  -14.00, ACC['650110'], '650110', 'sortie'),
    # LOT B - Amazon -> 612410
    (14012, '2025-10-19', 'AMZN Mktp FR HX9JL1735',                              -41.66, ACC['612410'], '612410', 'sortie'),
    (14191, '2025-10-28', 'AMZN Mktp FR 8L1118EX5',                             -134.47, ACC['612410'], '612410', 'sortie'),
    (14950, '2025-12-01', 'AMZN Mktp FR ZX5DY2TC4',                              -45.91, ACC['612410'], '612410', 'sortie'),
    (17157, '2026-03-11', 'AMAZON.BE QG0YW6QT5',                                  -20.48, ACC['612410'], '612410', 'sortie'),
    (17158, '2026-03-11', 'WWW.AMAZON PF6112WV5',                                 -23.38, ACC['612410'], '612410', 'sortie'),
    (17315, '2026-03-17', 'AMAZON.BE WA8A75505',                                  -97.75, ACC['612410'], '612410', 'sortie'),
    (18401, '2026-05-08', 'AMAZON.BE N66EQ5IL4',                                  -79.90, ACC['612410'], '612410', 'sortie'),
    # LOT B - Autres fournitures -> 612410
    (16393, '2026-02-04', 'HomeDeco.nl Amsterdam',                               -131.96, ACC['612410'], '612410', 'sortie'),
    (16759, '2026-02-20', 'PLAN-IT 4203 Rocourt',                                  -67.99, ACC['612410'], '612410', 'sortie'),
]

# Verification
bsl_ids = [x[0] for x in LOT]
bsls = call('account.bank.statement.line', 'search_read', [[('id','in',bsl_ids)]], {'fields':['id','date','amount','payment_ref','is_reconciled']})
bsl_map = {b['id']: b for b in bsls}

print("=== VERIFICATION PRE-CREATION ===")
errors = []
total_charges = 0.0
for (bsl_id, date, label, amount, acc_id, acc_code, sens) in LOT:
    b = bsl_map.get(bsl_id)
    if not b:
        errors.append(f"BSL {bsl_id} INTROUVABLE")
        continue
    if abs(b['amount'] - amount) > 0.01:
        errors.append(f"MONTANT BSL {bsl_id}: attendu {amount} / trouve {b['amount']} '{label}'")
        continue
    if b['is_reconciled']:
        errors.append(f"DEJA LETTRE BSL {bsl_id} '{label}'")
        continue
    print(f"  OK {b['date']} {b['amount']:>9.2f} -> {acc_code}  {label[:55]}")
    total_charges += amount

if errors:
    print("\nERREURS:")
    for e in errors:
        print(f"  !! {e}")
    raise SystemExit("Erreurs detectees, arret.")

print(f"\nTotal charges nettes: {total_charges:.2f} EUR")
print("Verification OK, lancement creation OD...\n")

# Creation OD et lettrage
results = []

for (bsl_id, date, label, amount, acc_charge_id, acc_charge_code, sens) in LOT:
    b = bsl_map[bsl_id]
    abs_amount = abs(amount)

    # Construire les lignes OD
    if sens == 'sortie':
        # D acc_charge / C 499000
        lines = [
            (0, 0, {'account_id': acc_charge_id, 'debit': abs_amount, 'credit': 0.0, 'name': label}),
            (0, 0, {'account_id': ACC['499000'],  'debit': 0.0, 'credit': abs_amount, 'name': label}),
        ]
    else:
        # sens entree: D 499000 / C acc_charge (correction +22.50)
        lines = [
            (0, 0, {'account_id': ACC['499000'],  'debit': abs_amount, 'credit': 0.0, 'name': label}),
            (0, 0, {'account_id': acc_charge_id,  'debit': 0.0, 'credit': abs_amount, 'name': label}),
        ]

    # Creer OD en draft
    move_vals = {
        'journal_id': JOURNAL_MISC,
        'date': date,
        'ref': label,
        'line_ids': lines,
    }
    move_id = call('account.move', 'create', [move_vals])

    # Poster l'OD
    call('account.move', 'action_post', [[move_id]])

    # Lire le numero de l'OD
    move_data = call('account.move', 'read', [[move_id]], {'fields':['name']})[0]
    od_name = move_data['name']

    # Trouver la ligne 499000 dans l'OD
    od_lines = call('account.move.line', 'search_read', [
        [('move_id','=',move_id), ('account_id','=',ACC['499000'])]
    ], {'fields':['id','debit','credit','reconciled']})

    # Trouver la ligne 499000 dans la BNK (via move_id de la BSL)
    bsl_move_id = b['move_id'][0] if b.get('move_id') else None
    bk_lines = []
    if bsl_move_id:
        bk_lines = call('account.move.line', 'search_read', [
            [('move_id','=',bsl_move_id), ('account_id','=',ACC['499000'])]
        ], {'fields':['id','debit','credit','reconciled']})

    # Lettrage
    lettre = False
    if od_lines and bk_lines:
        od_line_id = od_lines[0]['id']
        bk_line_id = bk_lines[0]['id']
        try:
            call('account.move.line', 'reconcile', [[od_line_id, bk_line_id]])
            lettre = True
        except Exception as e:
            lettre = f"ERREUR: {str(e)[:80]}"

    results.append({
        'bsl_id': bsl_id,
        'date': date,
        'label': label,
        'amount': amount,
        'acc_code': acc_charge_code,
        'od_name': od_name,
        'move_id': move_id,
        'lettre': lettre,
    })
    print(f"  {od_name}  {date}  {amount:>9.2f}  {acc_charge_code}  lettrage={'OUI' if lettre is True else lettre}")

print("\n=== RECAP FINAL ===")
print(f"{'Date':<12} {'Montant':>9} {'Compte':<8} {'OD':<18} {'Lettrage'}")
print("-"*70)
total = 0.0
for r in results:
    ok = 'OUI' if r['lettre'] is True else ('NON - '+str(r['lettre'])[:30])
    print(f"{r['date']:<12} {r['amount']:>9.2f} {r['acc_code']:<8} {r['od_name']:<18} {ok}")
    total += r['amount']
print("-"*70)
print(f"{'TOTAL':>22} {total:>9.2f}")
