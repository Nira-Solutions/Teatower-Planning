"""
Envoi Peppol differe de factures DEJA postees (facturees en avance pour le resultat
de la semaine, envoyees au client seulement apres livraison).

Usage : python peppol_envoi_differe.py INV/2026/05004 INV/2026/05005 [--apply]

Garde-fou : une facture n'est envoyee que si TOUTES les livraisons de sa SO d'origine
sont 'done' (ou 'cancel'). Sinon elle est sautee et reste en peppol_move_state='ready'.
Envoi via account.move.send.wizard, cf. facturation_b2b_peppol.py ETAPE 8.
"""
import os, sys, xmlrpc.client
from datetime import datetime

URL='https://tea-tree.odoo.com'; DB='tsc-be-tea-tree-main-18515272'
USER='nicolas.raes@teatower.com'
PWD=os.environ.get('ODOO_PWD')  # repo public -- jamais de mot de passe en clair
if not PWD:
    raise SystemExit("Definir la variable d'environnement ODOO_PWD.")
uid=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common').authenticate(DB,USER,PWD,{})
m=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw if kw is not None else {})

DRY = '--apply' not in sys.argv
names = [a for a in sys.argv[1:] if not a.startswith('--')]
print(f"{datetime.now():%Y-%m-%d %H:%M} MODE {'DRY-RUN' if DRY else 'APPLY'} : {', '.join(names)}")

for name in names:
    mv = call('account.move','search_read',[[['name','=',name],['move_type','=','out_invoice']]],
              {'fields':['id','state','invoice_origin','peppol_move_state','partner_id']})
    if not mv:
        print(f"  ERR   {name} introuvable"); continue
    mv = mv[0]
    if mv['state'] != 'posted' or mv['peppol_move_state'] not in (False, 'ready'):
        print(f"  SKIP  {name} state={mv['state']} peppol={mv['peppol_move_state']} (deja envoyee ou non postee)"); continue
    so = call('sale.order','search_read',[[['name','=',mv['invoice_origin']]]],{'fields':['picking_ids']})
    picks = call('stock.picking','read',[so[0]['picking_ids']],{'fields':['name','state']}) if so else []
    pending = [p['name'] for p in picks if p['state'] not in ('done','cancel')]
    if pending:
        print(f"  WAIT  {name} ({mv['invoice_origin']}) livraison non validee : {', '.join(pending)} -> pas d'envoi"); continue
    if DRY:
        print(f"  DRY   SEND {name} -> {mv['partner_id'][1]}"); continue
    ctx = {'active_model':'account.move','active_ids':[mv['id']],'active_id':mv['id']}
    try:
        wiz = call('account.move.send.wizard','create',[{'move_id':mv['id']}],{'context':ctx})
        if 'peppol' not in (call('account.move.send.wizard','read',[[wiz]],{'fields':['sending_methods']})[0]['sending_methods'] or []):
            call('account.move.send.wizard','write',[[wiz],{'sending_methods':['peppol']}])
        call('account.move.send.wizard','action_send_and_print',[[wiz]],{'context':ctx})
    except xmlrpc.client.Fault as e:
        if 'marshal None' not in str(e):
            print(f"  ERR   {name} : {str(e)[:150]}"); continue
    after = call('account.move','read',[[mv['id']]],{'fields':['peppol_move_state','peppol_message_uuid']})[0]
    print(f"  {'SENT' if after['peppol_move_state'] in ('processing','done','to_send') else 'WARN'}  {name} -> "
          f"{mv['partner_id'][1]} | state={after['peppol_move_state']} uuid={after['peppol_message_uuid']}")
