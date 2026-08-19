# -*- coding: utf-8 -*-
"""
Client AWEX - Cellule Explort : structure + Peppol - 19/08/2026
---------------------------------------------------------------
AWEX existe deja en fiche #2808 (Place Sainctelette 2, 1080 Bruxelles,
TVA BE0267314479) mais :
  - elle est enregistree en FOURNISSEUR (supplier_rank=1, customer_rank=0),
    jamais utilisee en client - aucune facture, aucune commande
  - son Peppol est en schema 9925 avec endpoint prefixe "BE0267314479".
    Les clients BE doivent etre en 0208 + numero d'entreprise a 10 chiffres
    SANS prefixe : en l'etat, facturation_b2b_peppol.py aurait bloque la
    facture (il exige eas == '0208').

On ne cree donc PAS de doublon : on complete la fiche existante et on lui
greffe les deux adresses demandees.

Structure cible :
  #2808 Awex (societe, TVA BE0267314479)
    +- [invoice]  AWEX - Cellule Explort   Place Sainctelette 2, 1080 Bruxelles
    |                                      invoice@awex.be
    +- [delivery] AWEX - Cellule Explort - Nicolas Ravenel
                                           Bd Emile de Laveleye 91, 4020 Liege

Le Peppol est pose sur le PARENT *et* sur l'adresse de facturation : le
controle de facturation lit partner_invoice_id, et un enfant peut rester
not_verified alors que le parent est valid (cas Vanderlinden #5626 du 19/08).

Usage : python creer_client_awex_explort.py [--apply]
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
print('MODE: %s\n' % ('DRY-RUN' if DRY else 'APPLY'))

PARENT = 2808
BCE = '0267314479'          # TVA BE0267314479 -> endpoint Peppol schema 0208
BE = 20                     # country_id Belgium
FP_INSTITUTIONS = 35        # mappe 700000 -> 700700 Ventes Institutions / Corporate
TAG_INSTITUTION = 29

FACTURATION = {
    'name': u'AWEX - Cellule Explort',
    'type': 'invoice',
    'parent_id': PARENT,
    'street': u'Place Sainctelette, 2',
    'zip': '1080',
    'city': u'Bruxelles',
    'country_id': BE,
    'email': 'invoice@awex.be',
    'lang': 'fr_BE',
}
LIVRAISON = {
    'name': u'AWEX - Cellule Explort - Nicolas Ravenel',
    'type': 'delivery',
    'parent_id': PARENT,
    'street': u'Boulevard Emile de Laveleye, 91',
    'street2': u'Batiment Bluepoint (6e etage)',
    'zip': '4020',
    'city': u'Liege',
    'country_id': BE,
    'lang': 'fr_BE',
}


def peppol_vals():
    return {'peppol_eas': '0208', 'peppol_endpoint': BCE,
            'invoice_sending_method': 'peppol'}


def verifie(pid, label):
    try:
        c('res.partner', 'button_account_peppol_check_partner_endpoint', [[pid]], [])
    except Exception as e:
        print('    WARN verification : %s' % str(e)[:120])
    st = c('res.partner', 'read', [[pid]],
           {'fields': ['peppol_eas', 'peppol_endpoint', 'peppol_verification_state']})[0]
    print('    %-46s eas=%s endpoint=%s -> %s'
          % (label, st['peppol_eas'], st['peppol_endpoint'], st['peppol_verification_state']))
    return st['peppol_verification_state']


def cherche_enfant(vals):
    """anti-doublon : meme parent, meme type, meme code postal"""
    r = c('res.partner', 'search_read',
          [[('parent_id', '=', PARENT), ('type', '=', vals['type']),
            ('zip', '=', vals['zip'])]],
          {'fields': ['name', 'street', 'city'], 'context': {'active_test': False}})
    return r[0] if r else None


# --------------------------------------------------------------- etape 1
print('=== ETAPE 1 : fiche mere #%d ===' % PARENT)
p = c('res.partner', 'read', [[PARENT]],
      {'fields': ['name', 'vat', 'customer_rank', 'supplier_rank', 'peppol_eas',
                  'peppol_endpoint', 'peppol_verification_state',
                  'property_account_position_id', 'category_id']})[0]
print('  actuel : %s | TVA=%s | client=%d fournisseur=%d | peppol eas=%s ep=%s (%s)'
      % (p['name'], p['vat'], p['customer_rank'], p['supplier_rank'],
         p['peppol_eas'], p['peppol_endpoint'], p['peppol_verification_state']))

maj = peppol_vals()
if not p['customer_rank']:
    maj['customer_rank'] = 1          # la fiche n'etait que fournisseur
if not p['property_account_position_id']:
    maj['property_account_position_id'] = FP_INSTITUTIONS
if TAG_INSTITUTION not in p['category_id']:
    maj['category_id'] = [(4, TAG_INSTITUTION)]

if DRY:
    print('  DRY    write %s' % maj)
else:
    c('res.partner', 'write', [[PARENT], maj])
    print('  OK     eas 9925->0208, endpoint BE%s->%s, client active, FP Institutions, tag Institution'
          % (BCE, BCE))
    verifie(PARENT, 'AWEX (societe mere)')

# --------------------------------------------------------------- etape 2
print('\n=== ETAPE 2 : adresses ===')
ids = {}
for label, vals, peppol in (('FACTURATION', FACTURATION, True),
                            ('LIVRAISON', LIVRAISON, False)):
    ex = cherche_enfant(vals)
    if ex:
        print('  EXISTE %-11s #%d %s' % (label, ex['id'], ex['name']))
        ids[label] = ex['id']
        continue
    if DRY:
        print('  DRY    CREATE %-11s %s' % (label, vals['name']))
        print('         %s%s, %s %s'
              % (vals['street'], ', ' + vals.get('street2', '') if vals.get('street2') else '',
                 vals['zip'], vals['city']))
        if peppol:
            print('         + Peppol 0208/%s + envoi peppol + mail invoice@awex.be' % BCE)
        continue
    v = dict(vals)
    if peppol:
        v.update(peppol_vals())
    nid = c('res.partner', 'create', [v])
    ids[label] = nid
    print('  CREE   %-11s #%d %s' % (label, nid, vals['name']))
    if peppol:
        verifie(nid, 'AWEX - Cellule Explort (facturation)')

if DRY:
    print('\nDRY : rien ecrit.')
    raise SystemExit(0)

# --------------------------------------------------------------- etape 3
print('\n=== ETAPE 3 : verification finale ===')
tous = [PARENT] + list(ids.values())
for x in c('res.partner', 'read', [tous],
           {'fields': ['name', 'type', 'street', 'street2', 'zip', 'city', 'email',
                       'peppol_eas', 'peppol_endpoint', 'peppol_verification_state',
                       'invoice_sending_method', 'property_account_position_id']}):
    print('  #%-7d %-42s [%s]' % (x['id'], x['name'], x['type']))
    print('           %s%s | %s %s | %s'
          % (x['street'], ' / ' + x['street2'] if x['street2'] else '',
             x['zip'], x['city'], x['email'] or '-'))
    print('           peppol %s/%s -> %s | envoi=%s'
          % (x['peppol_eas'], x['peppol_endpoint'],
             x['peppol_verification_state'], x['invoice_sending_method']))
