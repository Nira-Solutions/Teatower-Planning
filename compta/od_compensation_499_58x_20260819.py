# -*- coding: utf-8 -*-
"""
OD de compensation partielle : comptes d'attente 499x <-> comptes de transit 58x
--------------------------------------------------------------------------------
Au 30/06/2026 la balance de cloture FY25-26 affiche 651.655,96 EUR en comptes
d'attente 499x (499000 -648.230,09 + 499100 -3.425,87). Ce montant n'est pas
credible pour un comptable, et il ne l'est effectivement pas : il a en face
+402.040,52 EUR sur les comptes de transit 58x. Les deux cotes sont les deux
moities des MEMES flux d'encaissement (Bancontact, Visa/MC, Mollie, SumUp).

Origine de l'eclatement : MISC/25-26/06/0116 du 29/06/2026 a deplace
918.036,52 EUR des comptes 58x vers 499000. La compensation ne fait que
defaire cet eclatement artificiel - ce n'est pas un netting arbitraire entre
comptes sans rapport, c'est la meme ecriture qu'on recompose.

Solde net reel du bloc tresorerie transitoire : -249.615,44 EUR.

Effet : 15 comptes soldes a zero, remplaces par UNE ligne sur un compte dedie
et explicitement nomme. AUCUN impact sur le resultat - tous les comptes
concernes sont des comptes de bilan. Le resultat FY25-26 reste a -29.072,39.

ATTENTION - ce que cette OD ne fait PAS : elle rend le solde lisible, elle ne
l'explique pas. Les 249.615,44 restent des encaissements POS jamais rapproches
du compte bancaire. Le traitement de fond reste le rapprochement ligne a ligne
(Bancontact, Visa, Mollie, SumUp), qui viendra vider ce compte.

Usage : python od_compensation_499_58x_20260819.py [--apply]
"""
import os, sys, xmlrpc.client

URL = 'https://tea-tree.odoo.com'
DB = 'tsc-be-tea-tree-main-18515272'
USER = 'nicolas.raes@teatower.com'
PWD = os.environ.get('ODOO_PWD')
if not PWD:
    raise SystemExit('Definir ODOO_PWD')
uid = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/common').authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(URL + '/xmlrpc/2/object')


def c(mo, me, a, k=None):
    return m.execute_kw(DB, uid, PWD, mo, me, a, k or {})


DRY = '--apply' not in sys.argv
DATE = '2026-06-30'
JOURNAL = 11                      # Miscellaneous Operations
CODE_RESIDU = '489200'
NOM_RESIDU = u'Encaissements a reconcilier (POS et banque)'
LIBELLE = u'Compensation partielle comptes attente 499x / transit 58x'
REF = (u'Compensation partielle 499x <-> 58x au 30/06/2026 - defait '
       u'l eclatement cree par MISC/25-26/06/0116 - sans impact resultat')

print('MODE: %s | date %s\n' % ('DRY-RUN' if DRY else 'APPLY', DATE))

# --------------------------------------------------------- comptes concernes
accs = c('account.account', 'search_read',
         [['|', ('code', 'like', '58'), ('code', 'like', '499')]],
         {'fields': ['id', 'code', 'name']})
accs = [a for a in accs if a['code'][:2] in ('58', '49') and a['code'] != CODE_RESIDU]

soldes = []
for a in sorted(accs, key=lambda x: x['code']):
    g = c('account.move.line', 'read_group',
          [[('account_id', '=', a['id']), ('parent_state', '=', 'posted'),
            ('date', '<=', DATE)]],
          {'fields': ['balance'], 'groupby': [], 'lazy': False})
    b = round(g[0]['balance'], 2) if g and g[0]['__count'] else 0.0
    if abs(b) >= 0.005:
        soldes.append((a, b))

total = round(sum(b for _, b in soldes), 2)
print('=== SOLDES AU %s (a solder) ===' % DATE)
for a, b in soldes:
    print('  %-8s %-44s %14.2f' % (a['code'], a['name'][:44], b))
print('  %-8s %-44s %14.2f' % ('', 'SOLDE NET (-> compte de residu)', total))

# ------------------------------------------------------- compte de residu
ex = c('account.account', 'search_read', [[('code', '=', CODE_RESIDU)]], {'fields': ['id', 'name']})
if ex:
    rid = ex[0]['id']
    print('\n=== COMPTE DE RESIDU : %s existe deja (#%d %s)' % (CODE_RESIDU, rid, ex[0]['name']))
elif DRY:
    rid = None
    print('\n=== COMPTE DE RESIDU : DRY - creation de %s "%s"' % (CODE_RESIDU, NOM_RESIDU))
else:
    rid = c('account.account', 'create',
            [{'code': CODE_RESIDU, 'name': NOM_RESIDU,
              'account_type': 'liability_current', 'reconcile': True,
              'company_ids': [(6, 0, [1])]}])
    print('\n=== COMPTE DE RESIDU : %s cree (#%d) "%s"' % (CODE_RESIDU, rid, NOM_RESIDU))

# ------------------------------------------------------------------ l OD
lignes = []
for a, b in soldes:
    # on inverse chaque solde pour le ramener a zero
    lignes.append((a['id'], a['code'], a['name'], -b))
lignes.append((rid, CODE_RESIDU, NOM_RESIDU, total))

print('\n=== ECRITURE ===')
td = tc = 0.0
for _, code, nom, v in lignes:
    d = v if v > 0 else 0.0
    cr = -v if v < 0 else 0.0
    td += d; tc += cr
    print('  %-8s %-46s D=%13.2f C=%13.2f' % (code, nom[:46], d, cr))
print('  %-8s %-46s D=%13.2f C=%13.2f' % ('', 'TOTAUX', round(td, 2), round(tc, 2)))
if abs(round(td - tc, 2)) > 0.005:
    raise SystemExit('REFUS : ecriture desequilibree (%.2f)' % (td - tc))
print('  -> equilibree')

impact = 0.0
for a, b in soldes:
    t = c('account.account', 'read', [[a['id']]], {'fields': ['account_type']})[0]['account_type']
    if 'income' in t or 'expense' in t:
        impact += b
print('  -> impact resultat : %.2f EUR (doit etre 0,00)' % impact)
if abs(impact) > 0.005:
    raise SystemExit('REFUS : cette OD toucherait le compte de resultat.')

if DRY:
    print('\nDRY : rien ecrit.')
    raise SystemExit(0)

exist = c('account.move', 'search_read', [[('ref', '=', REF)]], {'fields': ['name', 'state']})
if exist:
    raise SystemExit('REFUS : OD deja passee (%s, %s) - doublon evite.' % (exist[0]['name'], exist[0]['state']))

vals = [(0, 0, {'account_id': aid, 'name': LIBELLE,
                'debit': v if v > 0 else 0.0, 'credit': -v if v < 0 else 0.0})
        for aid, code, nom, v in lignes]
mid = c('account.move', 'create',
        [{'move_type': 'entry', 'journal_id': JOURNAL, 'date': DATE,
          'ref': REF, 'line_ids': vals}])
c('account.move', 'action_post', [[mid]])
mv = c('account.move', 'read', [[mid]], {'fields': ['name', 'state']})[0]
print('\nOD POSTEE : %s | state=%s' % (mv['name'], mv['state']))

print('\n=== CONTROLE APRES ===')
for a, _ in soldes:
    g = c('account.move.line', 'read_group',
          [[('account_id', '=', a['id']), ('parent_state', '=', 'posted'), ('date', '<=', DATE)]],
          {'fields': ['balance'], 'groupby': [], 'lazy': False})
    b = round(g[0]['balance'], 2) if g and g[0]['__count'] else 0.0
    print('  %-8s %-44s %14.2f' % (a['code'], a['name'][:44], b))
g = c('account.move.line', 'read_group',
      [[('account_id', '=', rid), ('parent_state', '=', 'posted'), ('date', '<=', DATE)]],
      {'fields': ['balance'], 'groupby': [], 'lazy': False})
print('  %-8s %-44s %14.2f' % (CODE_RESIDU, NOM_RESIDU[:44], g[0]['balance']))
