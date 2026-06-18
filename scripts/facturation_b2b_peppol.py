"""
Facturation B2B Peppol - Teatower
- Corrige EAS 9925 -> 0208 sur partenaires BE
- Force qty_delivered sur lignes TRANSPORT
- Cree factures en mode delivered
- Poste les factures
- Envoie via Peppol uniquement si client valid
"""
import re, sys, xmlrpc.client
from datetime import date

URL='https://tea-tree.odoo.com'; DB='tsc-be-tea-tree-main-18515272'
USER='nicolas.raes@teatower.com'; PWD='Teatower123'
common=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid=common.authenticate(DB,USER,PWD,{})
m=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw if kw is not None else {})

def be_number(vat):
    if not vat: return None
    v = str(vat).upper().replace(' ','')
    if v.startswith('BE'):
        d = re.sub(r'\D','', v)
        return d if len(d) == 10 else None
    if re.fullmatch(r'\d{10}', v): return v
    return None

DRY = '--apply' not in sys.argv
print(f"MODE: {'DRY-RUN (rien ecrit)' if DRY else 'APPLY (ecriture reelle)'}")
print()

# =========================================================
# ETAPE 1 : Récupérer les SO to invoice
# =========================================================
sos = call('sale.order','search_read',
    [[['invoice_status','=','to invoice'],['state','=','sale']]],
    {'fields':['id','name','partner_id','amount_total'],'limit':200})

so_ids = [s['id'] for s in sos]
pid_to_sos = {}
for s in sos:
    pid = s['partner_id'][0]
    pid_to_sos.setdefault(pid,[]).append(s)

print(f"SO to invoice: {len(sos)} pour {len(pid_to_sos)} partenaires")

# =========================================================
# ETAPE 2 : Lire état Peppol des partenaires
# =========================================================
PFIELDS = ['id','name','vat','peppol_eas','peppol_endpoint','peppol_verification_state','invoice_sending_method','is_company','company_type']
partners = call('res.partner','read',[list(pid_to_sos.keys())],{'fields':PFIELDS})
p_map = {p['id']:p for p in partners}

# =========================================================
# ETAPE 3 : Corriger EAS 9925 -> 0208
# =========================================================
print("\n=== ETAPE 3 : CORRECTION EAS 9925 -> 0208 ===")
corrections = []  # {id, name, old_state, new_state}

for p in partners:
    eas = p.get('peppol_eas')
    vat = p.get('vat')
    st  = p.get('peppol_verification_state')
    if eas != '9925':
        continue
    num = be_number(vat)
    if not num:
        print(f"  SKIP  ID={p['id']} {p['name'][:40]} - VAT illisible ({vat})")
        corrections.append({'id':p['id'],'name':p['name'],'old_state':st,'new_state':'SKIP_NO_VAT'})
        continue
    if DRY:
        print(f"  DRY   ID={p['id']} {p['name'][:40]:40} eas:9925->0208 ep:{p.get('peppol_endpoint')}->{num}")
        continue
    m.execute_kw(DB,uid,PWD,'res.partner','write',[[p['id']],{'peppol_eas':'0208','peppol_endpoint':num}],{})
    try:
        m.execute_kw(DB,uid,PWD,'res.partner','button_account_peppol_check_partner_endpoint',[[p['id']]],[])
    except Exception as e:
        print(f"  WARN  verif {p['id']}: {str(e)[:100]}")
    new = m.execute_kw(DB,uid,PWD,'res.partner','read',[[p['id']]],{'fields':['peppol_verification_state','peppol_eas','peppol_endpoint']})[0]
    new_st = new['peppol_verification_state']
    tag = 'VALID  ' if new_st == 'valid' else new_st.upper()
    print(f"  {tag:20} ID={p['id']} {p['name'][:38]:38} eas={new['peppol_eas']} ep={new['peppol_endpoint']}")
    if new_st == 'valid':
        m.execute_kw(DB,uid,PWD,'res.partner','write',[[p['id']],{'invoice_sending_method':'peppol'}],{})
        print(f"    -> invoice_sending_method=peppol activé")
    corrections.append({'id':p['id'],'name':p['name'],'old_state':st,'new_state':new_st})
    p_map[p['id']]['peppol_verification_state'] = new_st
    p_map[p['id']]['peppol_eas'] = new['peppol_eas']
    p_map[p['id']]['invoice_sending_method'] = 'peppol' if new_st == 'valid' else p.get('invoice_sending_method')

# =========================================================
# ETAPE 4 : Lire lignes SO + forcer qty_delivered TRANSPORT
# =========================================================
print("\n=== ETAPE 4 : TRANSPORT QTY_DELIVERED ===")
lines = call('sale.order.line','search_read',
    [[['order_id','in',so_ids]]],
    {'fields':['id','order_id','product_id','product_uom_qty','qty_delivered','qty_invoiced','name'],'limit':5000})

from collections import defaultdict
so_lines = defaultdict(list)
for l in lines:
    so_lines[l['order_id'][0]].append(l)

transport_fixed = []
for s in sos:
    sid = s['id']
    ll = so_lines.get(sid, [])
    for l in ll:
        name_upper = (l.get('name') or '').upper()
        prod_name = str(l['product_id'][1] if l['product_id'] else '').upper()
        is_transport = 'TRANSPORT' in name_upper or 'TRANSPORT' in prod_name
        if is_transport and l['qty_delivered'] == 0 and l['product_uom_qty'] > 0:
            line_id = l['id']
            qty = l['product_uom_qty']
            if DRY:
                print(f"  DRY   SO {s['name']} ligne {line_id} TRANSPORT qty_delivered 0->{qty}")
            else:
                m.execute_kw(DB,uid,PWD,'sale.order.line','write',[[line_id],{'qty_delivered':qty}],{})
                print(f"  FIXED SO {s['name']} ligne {line_id} TRANSPORT qty_delivered 0->{qty}")
            transport_fixed.append({'so':s['name'],'line_id':line_id,'qty':qty})

if not transport_fixed:
    print("  (aucune ligne TRANSPORT à forcer)")

# =========================================================
# ETAPE 5 : Classifier les SO par eligibilité facturation
# =========================================================
print("\n=== ETAPE 5 : CLASSIFICATION SO ===")

# Recharger les lignes après fix transport (en apply)
if not DRY and transport_fixed:
    lines = call('sale.order.line','search_read',
        [[['order_id','in',so_ids]]],
        {'fields':['id','order_id','product_id','product_uom_qty','qty_delivered','qty_invoiced','name'],'limit':5000})
    so_lines = defaultdict(list)
    for l in lines:
        so_lines[l['order_id'][0]].append(l)

so_facturable = []    # valid peppol + qty livrée > 0
so_blocked_peppol = []  # pas valid peppol
so_nothing_delivered = []  # rien de livré

for s in sos:
    sid = s['id']
    pid = s['partner_id'][0]
    p = p_map[pid]
    peppol_state = p.get('peppol_verification_state')
    ll = so_lines.get(sid, [])

    # Lignes à facturer (delivered > invoiced)
    to_bill = [l for l in ll if (l['qty_delivered'] - l['qty_invoiced']) > 0]
    # Exclure lignes shopify discount (0€, qty 0)
    real_to_bill = [l for l in to_bill if not ('SHOPIFY' in str(l.get('name','')).upper())]

    if not real_to_bill:
        so_nothing_delivered.append(s)
        print(f"  SKIP  {s['name']} - rien à facturer (delivered=0 ou tout déjà facturé)")
        continue

    if peppol_state != 'valid':
        so_blocked_peppol.append({'so':s,'partner':p,'reason':peppol_state})
        print(f"  BLOCK {s['name']} - {p['name'][:35]} - peppol={peppol_state}")
        continue

    so_facturable.append(s)
    print(f"  OK    {s['name']} - {p['name'][:35]} - peppol=valid -> A FACTURER")

print(f"\n  Facturables Peppol: {len(so_facturable)}")
print(f"  Bloqués Peppol:     {len(so_blocked_peppol)}")
print(f"  Rien à livrer:      {len(so_nothing_delivered)}")

# =========================================================
# ETAPE 6 : Créer les factures (mode delivered)
# =========================================================
print("\n=== ETAPE 6 : CREATION FACTURES (delivered) ===")

# Récupérer le journal ventes
journals = call('account.journal','search_read',
    [[['type','=','sale'],['company_id.name','ilike','teatower']]],
    {'fields':['id','name'],'limit':5})
if not journals:
    journals = call('account.journal','search_read',
        [[['type','=','sale']]],
        {'fields':['id','name'],'limit':5})
print(f"  Journal ventes: {journals[0]['id']} - {journals[0]['name']}")
journal_id = journals[0]['id']

created_invoices = []
failed_invoices = []

for s in so_facturable:
    if DRY:
        print(f"  DRY   CREATE INVOICE for {s['name']} ({s['partner_id'][1]}) montant={s['amount_total']}")
        created_invoices.append({'so':s['name'],'status':'DRY','inv_name':None,'amount':s['amount_total']})
        continue

    try:
        # Vérifier si une facture draft existe déjà pour cette SO (éviter doublon)
        existing = call('account.move','search_read',
            [[['invoice_origin','=',s['name']],['move_type','=','out_invoice'],['state','=','draft']]],
            {'fields':['id','name','amount_total'],'limit':1,'order':'id desc'})
        if existing:
            inv_rec = existing[0]
            print(f"  EXIST {inv_rec['name'] or 'DRAFT_'+str(inv_rec['id'])} pour {s['name']} | {s['partner_id'][1][:30]} | {inv_rec['amount_total']:.2f} EUR (draft existante, skip creation)")
            created_invoices.append({'so':s['name'],'status':'draft','inv_id':inv_rec['id'],'inv_name':inv_rec['name'] or f"DRAFT_{inv_rec['id']}",'amount':inv_rec['amount_total'],'partner_id':s['partner_id'][0],'partner_name':s['partner_id'][1]})
            continue

        # Utiliser le wizard sale.advance.payment.inv en mode delivered
        ctx = {
            'active_ids': [s['id']],
            'active_model': 'sale.order',
            'active_id': s['id'],
        }
        wizard_id = m.execute_kw(DB,uid,PWD,'sale.advance.payment.inv','create',
            [{'advance_payment_method':'delivered','sale_order_ids':[[6,0,[s['id']]]]}], {'context':ctx})
        try:
            m.execute_kw(DB,uid,PWD,'sale.advance.payment.inv','create_invoices',
                [[wizard_id]], {'context':ctx})
        except Exception as e_inner:
            # L'erreur OdooMarshaller/dumps est fréquente quand create_invoices retourne
            # une action non sérialisable en XML-RPC — l'invoice est quand même créée.
            err_str = str(e_inner)
            if 'OdooMarshaller' not in err_str and 'dumps' not in err_str:
                raise
        # Récupérer la facture créée (chercher les drafts récentes liées à cette SO)
        inv = call('account.move','search_read',
            [[['invoice_origin','=',s['name']],['move_type','=','out_invoice'],['state','=','draft']]],
            {'fields':['id','name','amount_total','state'],'limit':5,'order':'id desc'})
        if inv:
            inv_rec = inv[0]
            print(f"  CREATED {inv_rec['name'] or '(no seq yet)'} pour {s['name']} | {s['partner_id'][1][:30]} | {inv_rec['amount_total']:.2f} EUR (draft)")
            created_invoices.append({'so':s['name'],'status':'draft','inv_id':inv_rec['id'],'inv_name':inv_rec['name'] or f"DRAFT_{inv_rec['id']}",'amount':inv_rec['amount_total'],'partner_id':s['partner_id'][0],'partner_name':s['partner_id'][1]})
        else:
            print(f"  WARN  {s['name']} - wizard lancé mais facture draft non trouvée")
            failed_invoices.append({'so':s['name'],'reason':'invoice not found after wizard'})
    except Exception as e:
        print(f"  ERR   {s['name']} : {str(e)[:120]}")
        failed_invoices.append({'so':s['name'],'reason':str(e)[:120]})

# =========================================================
# ETAPE 7 : Poster les factures
# =========================================================
print("\n=== ETAPE 7 : POST FACTURES ===")

posted_invoices = []
for inv_info in created_invoices:
    if inv_info.get('status') == 'DRY':
        print(f"  DRY   POST {inv_info['so']}")
        continue
    if inv_info.get('status') != 'draft':
        continue
    inv_id = inv_info['inv_id']
    if DRY:
        print(f"  DRY   POST {inv_info['inv_name']}")
        continue
    try:
        m.execute_kw(DB,uid,PWD,'account.move','action_post',[[inv_id]],[])
        rec = call('account.move','read',[[inv_id]],{'fields':['name','state','amount_total']})
        print(f"  POSTED {rec[0]['name']} | {inv_info['partner_name'][:30]:30} | {rec[0]['amount_total']:.2f} EUR | state={rec[0]['state']}")
        inv_info['status'] = 'posted'
        posted_invoices.append(inv_info)
    except Exception as e:
        print(f"  ERR   POST {inv_info.get('inv_name','')} : {str(e)[:120]}")
        failed_invoices.append({'so':inv_info['so'],'reason':f"POST ERR: {str(e)[:100]}"})

# =========================================================
# ETAPE 8 : Envoi Peppol
# =========================================================
print("\n=== ETAPE 8 : ENVOI PEPPOL ===")

peppol_sent = []
peppol_failed = []

for inv_info in posted_invoices:
    inv_id = inv_info['inv_id']
    pid = inv_info['partner_id']
    p = p_map[pid]
    if p.get('peppol_verification_state') != 'valid':
        print(f"  SKIP  {inv_info['inv_name']} - partner peppol not valid (state={p.get('peppol_verification_state')})")
        peppol_failed.append({'inv':inv_info['inv_name'],'reason':f"peppol state={p.get('peppol_verification_state')}"})
        continue
    if DRY:
        print(f"  DRY   SEND PEPPOL {inv_info['inv_name']} -> {inv_info['partner_name']}")
        peppol_sent.append(inv_info)
        continue
    try:
        # Envoyer via Peppol : action_send_and_print ou send_and_print_action
        # En Odoo 17/18, l'envoi edi se fait via account.move action_send_and_print
        # ou via le wizard account.move.send
        # Approche : créer wizard account.move.send avec send_peppol=True
        wizard_ctx = {'active_ids':[inv_id],'active_model':'account.move'}
        # Essai direct action
        try:
            send_wiz_id = m.execute_kw(DB,uid,PWD,'account.move.send','create',
                [{'move_ids':[[6,0,[inv_id]]],'send_peppol':True}],{'context':wizard_ctx})
            m.execute_kw(DB,uid,PWD,'account.move.send','action_send_and_print',[[send_wiz_id]],{'context':wizard_ctx})
            print(f"  SENT  PEPPOL {inv_info['inv_name']} -> {inv_info['partner_name'][:30]}")
            peppol_sent.append(inv_info)
        except Exception as e1:
            # Fallback: account.move _send_peppol direct
            try:
                m.execute_kw(DB,uid,PWD,'account.move','action_send_and_print',[[inv_id]],[])
                print(f"  SENT  PEPPOL (fallback) {inv_info['inv_name']} -> {inv_info['partner_name'][:30]}")
                peppol_sent.append(inv_info)
            except Exception as e2:
                print(f"  ERR   PEPPOL {inv_info['inv_name']} : {str(e2)[:120]}")
                peppol_failed.append({'inv':inv_info['inv_name'],'reason':str(e2)[:120]})
    except Exception as e:
        print(f"  ERR   PEPPOL {inv_info['inv_name']} : {str(e)[:120]}")
        peppol_failed.append({'inv':inv_info['inv_name'],'reason':str(e)[:120]})

# =========================================================
# RAPPORT FINAL
# =========================================================
print("\n" + "="*70)
print("RAPPORT FINAL")
print("="*70)
print(f"\nCorrections Peppol (EAS 9925->0208) : {len(corrections)}")
for c in corrections:
    print(f"  ID={c['id']} {c['name'][:40]:40} {c.get('old_state','?')} -> {c.get('new_state','?')}")

print(f"\nTransport lines forcées : {len(transport_fixed)}")
for t in transport_fixed:
    print(f"  {t['so']} ligne {t['line_id']} qty={t['qty']}")

print(f"\nFactures créées : {len(created_invoices)}")
for inv in created_invoices:
    status = inv.get('status','?')
    inv_name_str = inv.get('inv_name') or '(dry)'
    partner_str = (inv.get('partner_name') or '?')[:30]
    print(f"  {inv_name_str:20} | SO={inv['so']:10} | {partner_str:30} | {inv.get('amount',0):.2f} EUR | {status}")

print(f"\nFactures postées : {len(posted_invoices)}")
print(f"Factures Peppol envoyées : {len(peppol_sent)}")
print(f"Factures Peppol ECHEC : {len(peppol_failed)}")
for f in peppol_failed:
    print(f"  {f['inv']} : {f['reason'][:80]}")

print(f"\nSO bloquées Peppol (non facturées) : {len(so_blocked_peppol)}")
for b in so_blocked_peppol:
    p = b['partner']
    print(f"  {b['so']['name']:12} | {p['name'][:40]:40} | peppol={b['reason']} | VAT={p.get('vat')} | EAS={p.get('peppol_eas')} | EP={p.get('peppol_endpoint')}")

print(f"\nSO sans livraison (non facturées) : {len(so_nothing_delivered)}")
for s in so_nothing_delivered:
    print(f"  {s['name']:12} | {s['partner_id'][1][:40]}")

print(f"\nErreurs : {len(failed_invoices)}")
for f in failed_invoices:
    print(f"  SO={f['so']} : {f['reason']}")
