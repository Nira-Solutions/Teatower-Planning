"""Active/configure/verifie Peppol pour les clients pro factures recemment.
- Ne touche QUE: peppol_eas, peppol_endpoint (config BE 0208), invoice_sending_method (=peppol si valid).
- N'active jamais un partenaire qui ne ressort pas 'valid'.
"""
import re, sys, xmlrpc.client
URL='https://tea-tree.odoo.com'; DB='tsc-be-tea-tree-main-18515272'; USER='nicolas.raes@teatower.com'; PWD='Teatower123'
common=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common'); uid=common.authenticate(DB,USER,PWD,{})
models=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
def call(m,meth,a,k=None): return models.execute_kw(DB,uid,PWD,m,meth,a,k or {})

SINCE='2026-04-15'
DRY = '--apply' not in sys.argv

def be_number(vat):
    if not vat: return None
    v=vat.upper().replace(' ','')
    if v.startswith('BE'):
        d=re.sub(r'\D','',v); return d if len(d)==10 else None
    if re.fullmatch(r'\d{10}', v): return v
    return None

FIELDS=['id','name','is_company','company_type','vat','country_id','peppol_eas','peppol_endpoint','peppol_verification_state','invoice_sending_method','invoice_edi_format']

inv=call('account.move','search_read',[[('move_type','=','out_invoice'),('state','=','posted'),('invoice_date','>=',SINCE)]],{'fields':['partner_id'],'limit':5000})
pids=sorted(set(i['partner_id'][0] for i in inv if i.get('partner_id')))
recs=call('res.partner','read',[pids],{'fields':['commercial_partner_id']})
comm=sorted(set(r['commercial_partner_id'][0] for r in recs if r.get('commercial_partner_id')))
rows=call('res.partner','read',[comm],{'fields':FIELDS})
pros=[r for r in rows if r.get('is_company') or r.get('company_type')=='company' or r.get('vat')]

cat_ok=[]; cat_activate=[]; cat_fix=[]; cat_review=[]

for r in pros:
    send=r.get('invoice_sending_method'); st=r.get('peppol_verification_state'); vat=r.get('vat')
    if send=='peppol' and st=='valid':
        cat_ok.append(r); continue
    if st=='valid':
        cat_activate.append(r); continue
    # not_valid / not_verified / not_valid_format
    num=be_number(vat)
    if num:
        cat_fix.append((r,num))
    else:
        cat_review.append(r)

print(f"MODE: {'DRY-RUN (rien ecrit)' if DRY else 'APPLY (ecriture reelle)'}")
print(f"PRO factures depuis {SINCE}: {len(pros)}")
print(f"  [A] deja activees (peppol+valid): {len(cat_ok)}")
print(f"  [B] valid mais a ACTIVER       : {len(cat_activate)}")
print(f"  [C] a RECONFIGURER (BE) + verif : {len(cat_fix)}")
print(f"  [D] a REVOIR (non-BE/illisible): {len(cat_review)}")
print()

def activate(pid):
    call('res.partner','write',[[pid],{'invoice_sending_method':'peppol'}])

# ---- [B] activer ----
print('=== [B] ACTIVATION (valid -> send=peppol) ===')
for r in cat_activate:
    old=r.get('invoice_sending_method')
    if DRY:
        print(f"  DRY {r['id']:>6} {r['name'][:38]:38} ({old}->peppol)")
    else:
        try:
            activate(r['id']); print(f"  OK  {r['id']:>6} {r['name'][:38]:38} ({old}->peppol)")
        except Exception as e:
            print(f"  ERR {r['id']:>6} {r['name'][:30]} : {str(e)[:70]}")

# ---- [C] reconfigurer + verifier + activer si valid ----
print()
print('=== [C] RECONFIG BE 0208 + VERIF (+activation si valid) ===')
for r,num in cat_fix:
    if DRY:
        print(f"  DRY {r['id']:>6} {r['name'][:34]:34} eas:{r.get('peppol_eas')}->0208 endp:{r.get('peppol_endpoint')}->{num}")
        continue
    try:
        call('res.partner','write',[[r['id']],{'peppol_eas':'0208','peppol_endpoint':num}])
        try: call('res.partner','button_account_peppol_check_partner_endpoint',[[r['id']]])
        except Exception: pass
        new=call('res.partner','read',[[r['id']]],{'fields':['peppol_verification_state']})[0]['peppol_verification_state']
        tag='VALID' if new=='valid' else new.upper()
        act=''
        if new=='valid':
            activate(r['id']); act=' +ACTIVE'
        print(f"  {tag:14} {r['id']:>6} {r['name'][:34]:34} -> {new}{act}")
    except Exception as e:
        print(f"  ERR {r['id']:>6} {r['name'][:30]} : {str(e)[:70]}")

# ---- [D] review ----
print()
print('=== [D] A REVOIR MANUELLEMENT (non-BE / VAT illisible) ===')
for r in cat_review:
    print(f"  {r['id']:>6} {r['name'][:38]:38} VAT:{str(r.get('vat')):16} state:{r.get('peppol_verification_state')}")
