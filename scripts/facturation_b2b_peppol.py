"""
Facturation B2B Peppol - Teatower
- Exclut les commandes B2C/web (team_id dans EXCLUDE_TEAM_IDS, ex: "Odoo x Shopify")
- Corrige EAS 9925 -> 0208 sur partenaires BE
- Force qty_delivered sur lignes TRANSPORT
- Cree factures en mode delivered (ne facture que qty_delivered - qty_invoiced > 0)
- Verifie le Peppol sur le PARTENAIRE DE FACTURATION REEL (partner_invoice_id de la SO,
  qui peut differer du partner_id principal, ex: adresses enfants) et non le partenaire
  principal — un partenaire enfant peut etre not_verified alors que le parent est valid.
- Poste les factures (skip les factures a 0.00 EUR, laissees en draft pour arbitrage manuel)
- Envoie via Peppol UNIQUEMENT si client valid, via account.move.send.wizard
  (sending_methods=['peppol'] + action_send_and_print). NOTE: account.move.action_send_and_print
  seul (sans passer par le wizard) NE DECLENCHE PAS l'envoi reel — l'invoice reste en
  peppol_move_state='ready' au lieu de passer a 'processing'. Toujours utiliser le wizard.
"""
import os, re, sys, xmlrpc.client
from datetime import date

URL='https://tea-tree.odoo.com'; DB='tsc-be-tea-tree-main-18515272'
USER='nicolas.raes@teatower.com'
PWD=os.environ.get('ODOO_PWD')  # repo public -- jamais de mot de passe en clair, cf reference_credentials_materiel_tt
if not PWD:
    raise SystemExit("Definir la variable d'environnement ODOO_PWD avant d'executer ce script (creds dans Materiel TT.xlsx).")
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

# SO a NE PAS facturer ce tour-ci. Cas typique : le TT/OUT est valide (la
# marchandise est sortie du stock vers la camionnette de Gilles) mais le client
# ne l'a pas encore recue — la livraison merch est planifiee plus tard. Facturer
# avant reception cree des litiges (surtout Carrefour, cf. rejets EDI 049/004/010).
# Usage : --exclude S05982,S06007,S05980
EXCLUDE_SO_NAMES = set()
for i, a in enumerate(sys.argv):
    if a == '--exclude' and i + 1 < len(sys.argv):
        EXCLUDE_SO_NAMES = {x.strip().upper() for x in sys.argv[i + 1].split(',') if x.strip()}
    elif a.startswith('--exclude='):
        EXCLUDE_SO_NAMES = {x.strip().upper() for x in a.split('=', 1)[1].split(',') if x.strip()}

print(f"MODE: {'DRY-RUN (rien ecrit)' if DRY else 'APPLY (ecriture reelle)'}")
if EXCLUDE_SO_NAMES:
    print(f"EXCLUSIONS manuelles: {', '.join(sorted(EXCLUDE_SO_NAMES))}")
print()

# =========================================================
# ETAPE 1 : Récupérer les SO to invoice (PRO uniquement, exclut B2C/web)
# =========================================================
EXCLUDE_TEAM_IDS = {4}  # 4 = "Odoo x Shopify" (B2C/web) — a adapter si d'autres teams B2C existent

sos_all = call('sale.order','search_read',
    [[['invoice_status','=','to invoice'],['state','in',('sale','done')]]],
    {'fields':['id','name','partner_id','partner_invoice_id','amount_total','team_id'],'limit':200})
sos_pro = [s for s in sos_all if not s.get('team_id') or s['team_id'][0] not in EXCLUDE_TEAM_IDS]
sos_excluded_b2c = [s for s in sos_all if s.get('team_id') and s['team_id'][0] in EXCLUDE_TEAM_IDS]
sos = [s for s in sos_pro if s['name'].upper() not in EXCLUDE_SO_NAMES]
sos_excluded_manual = [s for s in sos_pro if s['name'].upper() in EXCLUDE_SO_NAMES]

so_ids = [s['id'] for s in sos]
pid_to_sos = {}
for s in sos:
    pid = s['partner_id'][0]
    pid_to_sos.setdefault(pid,[]).append(s)

print(f"SO to invoice: {len(sos_all)} total | PRO retenues: {len(sos)} | exclues B2C/web: {len(sos_excluded_b2c)} | exclues manuellement: {len(sos_excluded_manual)}")
for s in sos_excluded_b2c:
    print(f"  EXCLU B2C  {s['name']:10} {s['partner_id'][1][:35]:35} team={s['team_id'][1]}")
for s in sos_excluded_manual:
    print(f"  EXCLU MANU {s['name']:10} {s['partner_id'][1][:35]:35} {s['amount_total']:.2f} EUR (--exclude)")

# =========================================================
# ETAPE 2 : Lire état Peppol des partenaires (principal + facturation reel)
# =========================================================
PFIELDS = ['id','name','vat','country_id','peppol_eas','peppol_endpoint','peppol_verification_state','invoice_sending_method','is_company','company_type']
inv_pids = set(s['partner_invoice_id'][0] for s in sos if s.get('partner_invoice_id'))
all_pids = sorted(set(pid_to_sos.keys()) | inv_pids)
partners = call('res.partner','read',[all_pids],{'fields':PFIELDS})
p_map = {p['id']:p for p in partners}

# =========================================================
# ETAPE 3 : Corriger EAS != 0208 (ex 9925) ET re-verifier les BE
#           deja en 0208 mais pas encore valides (endpoint manquant
#           ou verification jamais (re)declenchee)
# =========================================================
print("\n=== ETAPE 3 : CORRECTION/VERIFICATION PEPPOL BE (cible eas=0208 + state=valid) ===")
corrections = []  # {id, name, old_state, new_state}

for p in partners:
    eas = p.get('peppol_eas')
    vat = p.get('vat')
    st  = p.get('peppol_verification_state')
    country = p.get('country_id')
    pname = p.get('name') or f"(sans nom, ID={p['id']})"
    is_be = (country and country[1] == 'Belgium') or (vat and str(vat).upper().replace(' ','').startswith('BE'))
    if not is_be:
        continue
    # Rien a faire si deja conforme (eas=0208 + valid)
    if eas == '0208' and st == 'valid':
        continue
    num = be_number(vat)
    if not num:
        print(f"  SKIP  ID={p['id']} {pname[:40]} - VAT illisible ({vat})")
        corrections.append({'id':p['id'],'name':pname,'old_state':st,'new_state':'SKIP_NO_VAT'})
        continue
    if DRY:
        print(f"  DRY   ID={p['id']} {pname[:40]:40} eas:{eas}->0208 ep:{p.get('peppol_endpoint')}->{num} (state actuel={st})")
        continue
    m.execute_kw(DB,uid,PWD,'res.partner','write',[[p['id']],{'peppol_eas':'0208','peppol_endpoint':num}],{})
    try:
        m.execute_kw(DB,uid,PWD,'res.partner','button_account_peppol_check_partner_endpoint',[[p['id']]],[])
    except Exception as e:
        print(f"  WARN  verif {p['id']}: {str(e)[:100]}")
    new = m.execute_kw(DB,uid,PWD,'res.partner','read',[[p['id']]],{'fields':['peppol_verification_state','peppol_eas','peppol_endpoint']})[0]
    new_st = new['peppol_verification_state']
    tag = 'VALID  ' if new_st == 'valid' else new_st.upper()
    print(f"  {tag:20} ID={p['id']} {pname[:38]:38} eas={new['peppol_eas']} ep={new['peppol_endpoint']}")
    if new_st == 'valid':
        m.execute_kw(DB,uid,PWD,'res.partner','write',[[p['id']],{'invoice_sending_method':'peppol'}],{})
        print(f"    -> invoice_sending_method=peppol activé")
    corrections.append({'id':p['id'],'name':pname,'old_state':st,'new_state':new_st})
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
    # Peppol verifie sur le VRAI partenaire de facturation (peut differer du partner_id
    # principal, ex: adresse enfant "Invoice Address" avec son propre etat peppol)
    inv_pid = s['partner_invoice_id'][0] if s.get('partner_invoice_id') else s['partner_id'][0]
    p = p_map.get(inv_pid, {})
    peppol_state = p.get('peppol_verification_state')
    peppol_eas = p.get('peppol_eas')
    ll = so_lines.get(sid, [])

    # Lignes à facturer (delivered > invoiced) — seul le reellement livre compte,
    # meme si invoice_status SO='to invoice' a cause de produits en invoice_policy='order'
    to_bill = [l for l in ll if (l['qty_delivered'] - l['qty_invoiced']) > 0]
    # Exclure lignes shopify discount (0€, qty 0)
    real_to_bill = [l for l in to_bill if not ('SHOPIFY' in str(l.get('name','')).upper())]

    if not real_to_bill:
        so_nothing_delivered.append(s)
        print(f"  SKIP  {s['name']} - rien à facturer (delivered=0 ou tout déjà facturé)")
        continue

    if peppol_state != 'valid' or peppol_eas != '0208':
        so_blocked_peppol.append({'so':s,'partner':p,'inv_pid':inv_pid,'reason':f"state={peppol_state} eas={peppol_eas}"})
        print(f"  BLOCK {s['name']} - {s['partner_id'][1][:35]} - facturation-partner ID={inv_pid} peppol state={peppol_state} eas={peppol_eas}")
        continue

    so_facturable.append(s)
    print(f"  OK    {s['name']} - {s['partner_id'][1][:35]} - peppol=valid (partner ID={inv_pid}) -> A FACTURER")

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
            inv_pid = s['partner_invoice_id'][0] if s.get('partner_invoice_id') else s['partner_id'][0]
            created_invoices.append({'so':s['name'],'status':'draft','inv_id':inv_rec['id'],'inv_name':inv_rec['name'] or f"DRAFT_{inv_rec['id']}",'amount':inv_rec['amount_total'],'partner_id':s['partner_id'][0],'partner_name':s['partner_id'][1],'inv_pid':inv_pid})
        else:
            print(f"  WARN  {s['name']} - wizard lancé mais facture draft non trouvée")
            failed_invoices.append({'so':s['name'],'reason':'invoice not found after wizard'})
    except Exception as e:
        print(f"  ERR   {s['name']} : {str(e)[:120]}")
        failed_invoices.append({'so':s['name'],'reason':str(e)[:120]})

# =========================================================
# ETAPE 7 : Poster les factures (skip les 0.00 EUR -> laissees en draft)
# =========================================================
print("\n=== ETAPE 7 : POST FACTURES ===")

posted_invoices = []
zero_amount = []
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
    if inv_info.get('amount', 0) == 0:
        print(f"  SKIP-0EUR {inv_info['inv_name']} pour {inv_info['so']} - montant 0.00 EUR, laissee en DRAFT (arbitrage manuel, pas d'interet a poster/envoyer un Peppol a 0€)")
        zero_amount.append(inv_info)
        continue
    try:
        m.execute_kw(DB,uid,PWD,'account.move','action_post',[[inv_id]],[])
        rec = call('account.move','read',[[inv_id]],{'fields':['name','state','amount_total']})
        print(f"  POSTED {rec[0]['name']} | {inv_info['partner_name'][:30]:30} | {rec[0]['amount_total']:.2f} EUR | state={rec[0]['state']}")
        inv_info['status'] = 'posted'
        inv_info['inv_name'] = rec[0]['name']
        posted_invoices.append(inv_info)
    except Exception as e:
        print(f"  ERR   POST {inv_info.get('inv_name','')} : {str(e)[:120]}")
        failed_invoices.append({'so':inv_info['so'],'reason':f"POST ERR: {str(e)[:100]}"})

# =========================================================
# ETAPE 8 : Envoi Peppol
# =========================================================
# IMPORTANT : account.move.action_send_and_print() seul NE DECLENCHE PAS l'envoi reel
# (l'invoice reste peppol_move_state='ready'). Il FAUT passer par le wizard
# account.move.send.wizard : create({'move_id':inv_id}) puis action_send_and_print()
# sur le wizard. Verifie -> peppol_move_state passe a 'processing' avec un peppol_message_uuid.
print("\n=== ETAPE 8 : ENVOI PEPPOL ===")

peppol_sent = []
peppol_failed = []

for inv_info in posted_invoices:
    inv_id = inv_info['inv_id']
    inv_pid = inv_info.get('inv_pid', inv_info['partner_id'])
    p = p_map.get(inv_pid, {})
    if p.get('peppol_verification_state') != 'valid':
        print(f"  SKIP  {inv_info['inv_name']} - invoice-partner ID={inv_pid} peppol not valid (state={p.get('peppol_verification_state')})")
        peppol_failed.append({'inv':inv_info['inv_name'],'reason':f"peppol state={p.get('peppol_verification_state')}"})
        continue
    if DRY:
        print(f"  DRY   SEND PEPPOL {inv_info['inv_name']} -> {inv_info['partner_name']}")
        peppol_sent.append(inv_info)
        continue
    try:
        ctx = {'active_model':'account.move','active_ids':[inv_id],'active_id':inv_id}
        wiz_id = m.execute_kw(DB,uid,PWD,'account.move.send.wizard','create',[{'move_id':inv_id}],{'context':ctx})
        wiz = call('account.move.send.wizard','read',[[wiz_id]],{'fields':['sending_methods']})
        methods = wiz[0]['sending_methods']
        if not methods or 'peppol' not in methods:
            # forcer peppol explicitement si pas selectionne par defaut
            m.execute_kw(DB,uid,PWD,'account.move.send.wizard','write',[[wiz_id],{'sending_methods':['peppol']}])
        m.execute_kw(DB,uid,PWD,'account.move.send.wizard','action_send_and_print',[[wiz_id]],{'context':ctx})
        mo_after = call('account.move','read',[[inv_id]],{'fields':['peppol_move_state','peppol_message_uuid']})[0]
        if mo_after.get('peppol_move_state') in ('processing','done','to_send'):
            print(f"  SENT  PEPPOL {inv_info['inv_name']} -> {inv_info['partner_name'][:30]} | state={mo_after['peppol_move_state']} uuid={mo_after.get('peppol_message_uuid')}")
            peppol_sent.append(inv_info)
        else:
            print(f"  WARN  {inv_info['inv_name']} - wizard execute mais peppol_move_state toujours '{mo_after.get('peppol_move_state')}' (envoi non confirme)")
            peppol_failed.append({'inv':inv_info['inv_name'],'reason':f"peppol_move_state={mo_after.get('peppol_move_state')} apres wizard"})
    except Exception as e:
        print(f"  ERR   PEPPOL {inv_info['inv_name']} : {str(e)[:150]}")
        peppol_failed.append({'inv':inv_info['inv_name'],'reason':str(e)[:150]})

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

print(f"\nFactures 0.00 EUR non postees (draft, arbitrage manuel) : {len(zero_amount)}")
for z in zero_amount:
    print(f"  {z['inv_name']} | SO={z['so']} | {z['partner_name']}")

print(f"\nFactures postées : {len(posted_invoices)}")
print(f"Factures Peppol envoyées : {len(peppol_sent)}")
print(f"Factures Peppol ECHEC : {len(peppol_failed)}")
for f in peppol_failed:
    print(f"  {f['inv']} : {f['reason'][:80]}")

print(f"\nSO bloquées Peppol (non facturées) : {len(so_blocked_peppol)}")
for b in so_blocked_peppol:
    p = b['partner']
    pname = str(p.get('name') or f"(adresse enfant, ID={b.get('inv_pid')})")
    print(f"  {b['so']['name']:12} | {pname[:40]:40} | inv_partner_id={b.get('inv_pid')} | {b['reason']} | VAT={p.get('vat')} | EP={p.get('peppol_endpoint')}")

print(f"\nSO sans livraison (non facturées) : {len(so_nothing_delivered)}")
for s in so_nothing_delivered:
    print(f"  {s['name']:12} | {s['partner_id'][1][:40]}")

print(f"\nErreurs : {len(failed_invoices)}")
for f in failed_invoices:
    print(f"  SO={f['so']} : {f['reason']}")
