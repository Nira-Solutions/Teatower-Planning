"""Active/configure/verifie Peppol pour TOUS les clients pro de Teatower.
- Pro = is_company OR vat renseigne, au niveau commercial_partner_id (dedup societe).
- BE : peppol_eas=0208, endpoint = n entreprise 10 chiffres SANS prefixe BE.
- Verifie l'endpoint sur le reseau ; n'active invoice_sending_method=peppol QUE si 'valid'.
- Non-BE / VAT illisible / sans VAT -> listes a REVOIR (pas touche, schema pays a confirmer).
- DRY-RUN par defaut. Ajouter --apply pour ecrire.
Usage : python scripts/peppol_activate_all.py [--apply]
"""
import re, sys, xmlrpc.client
URL='https://tea-tree.odoo.com'; DB='tsc-be-tea-tree-main-18515272'; USER='nicolas.raes@teatower.com'; PWD='Teatower123'
common=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common'); uid=common.authenticate(DB,USER,PWD,{})
models=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
def call(m,meth,a,k=None): return models.execute_kw(DB,uid,PWD,m,meth,a,k or {})

DRY = '--apply' not in sys.argv

def be_number(vat):
    """Renvoie le n entreprise BE 10 chiffres si VAT belge, sinon None."""
    if not vat: return None
    v=vat.upper().replace(' ','').replace('.','').replace('-','')
    if v.startswith('BE'):
        d=re.sub(r'\D','',v); return d if len(d)==10 else None
    if re.fullmatch(r'\d{10}', v): return v
    if re.fullmatch(r'\d{9}', v): return '0'+v  # ancien format 9 chiffres -> prefixe 0
    return None

FIELDS=['id','name','is_company','company_type','vat','country_id','customer_rank',
        'peppol_eas','peppol_endpoint','peppol_verification_state','invoice_sending_method']

# Tous les partners "societe ou avec VAT", clients (customer_rank>0 de preference mais on garde large)
dom=['&',('parent_id','=',False),'|',('is_company','=',True),('vat','!=',False)]
ids=call('res.partner','search',[dom])
rows=call('res.partner','read',[ids],{'fields':FIELDS})
# clients uniquement (au moins une vente) -> customer_rank>0 ; sinon on ignore les purs fournisseurs/contacts
pros=[r for r in rows if (r.get('customer_rank') or 0) > 0]

cat_ok=[]; cat_activate=[]; cat_fix=[]; cat_review=[]; cat_novat=[]
for r in pros:
    send=r.get('invoice_sending_method'); st=r.get('peppol_verification_state'); vat=r.get('vat')
    if send=='peppol' and st=='valid':
        cat_ok.append(r); continue
    if st=='valid':
        cat_activate.append(r); continue
    num=be_number(vat)
    if num:
        cat_fix.append((r,num))
    elif vat:
        cat_review.append(r)   # a un VAT mais non-BE/illisible
    else:
        cat_novat.append(r)    # pas de VAT -> impossible sur Peppol

print(f"MODE: {'DRY-RUN (rien ecrit)' if DRY else 'APPLY (ecriture reelle)'}")
print(f"CLIENTS PRO (societe/VAT, customer_rank>0): {len(pros)}")
print(f"  [A] deja OK (peppol+valid)        : {len(cat_ok)}")
print(f"  [B] valid -> a ACTIVER            : {len(cat_activate)}")
print(f"  [C] BE a (re)configurer + verifier: {len(cat_fix)}")
print(f"  [D] VAT non-BE/illisible (REVOIR) : {len(cat_review)}")
print(f"  [E] SANS VAT (hors Peppol)        : {len(cat_novat)}")
print()

def activate(pid): call('res.partner','write',[[pid],{'invoice_sending_method':'peppol'}])

print('=== [B] ACTIVATION (valid -> send=peppol) ===')
for r in cat_activate:
    if DRY: print(f"  DRY {r['id']:>6} {r['name'][:42]:42}")
    else:
        try: activate(r['id']); print(f"  OK  {r['id']:>6} {r['name'][:42]:42}")
        except Exception as e: print(f"  ERR {r['id']:>6} {r['name'][:30]} : {str(e)[:70]}")

print()
print('=== [C] RECONFIG BE 0208 + VERIF (+activation si valid) ===')
n_valid=0
for r,num in cat_fix:
    if DRY:
        print(f"  DRY {r['id']:>6} {r['name'][:36]:36} eas:{r.get('peppol_eas')}->0208 endp:{r.get('peppol_endpoint')}->{num}")
        continue
    try:
        call('res.partner','write',[[r['id']],{'peppol_eas':'0208','peppol_endpoint':num}])
        try: call('res.partner','button_account_peppol_check_partner_endpoint',[[r['id']]])
        except Exception: pass
        new=call('res.partner','read',[[r['id']]],{'fields':['peppol_verification_state']})[0]['peppol_verification_state']
        act=''
        if new=='valid':
            activate(r['id']); act=' +ACTIVE'; n_valid+=1
        print(f"  {new.upper():14} {r['id']:>6} {r['name'][:34]:34} -> {new}{act}")
    except Exception as e:
        print(f"  ERR {r['id']:>6} {r['name'][:30]} : {str(e)[:70]}")
if not DRY: print(f"  --> {n_valid}/{len(cat_fix)} ressortent valid + actives")

print()
print('=== [D] A REVOIR (VAT non-BE / illisible) ===')
for r in cat_review:
    print(f"  {r['id']:>6} {r['name'][:38]:38} VAT:{str(r.get('vat')):16} pays:{r.get('country_id') and r['country_id'][1]} state:{r.get('peppol_verification_state')}")

print()
print(f"=== [E] SANS VAT (hors Peppol) : {len(cat_novat)} clients (non listes) ===")
