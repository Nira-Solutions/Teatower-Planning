"""
Rattrapage position fiscale canal sur les clients - 19/08/2026
--------------------------------------------------------------
Le canal d'un client se lit dans le compte de resultat via sa POSITION FISCALE
(FP GMS -> 700600, Horeca -> 700300, Revendeurs -> 700500, Institutions -> 700700),
pas via son tag. Un client tague mais sans FP tombe en 700000 = fourre-tout.

Les 4 FP canal ont ZERO mapping de taxe (verifie le 19/08/26) : elles ne
remappent que le compte de produit. La correction est donc fiscalement neutre.

Regles :
- on ne se fie qu'aux tags canoniques (les tags de campagne MC-*, "Canal B2B
  Direct", "Magasins" (=B2C) et DTC sont ignores)
- on n'ecrase QUE si la FP est vide ou generique ("Belgium B2B")
- une FP canal deja posee qui contredit le tag n'est PAS ecrasee : c'est un
  arbitrage metier, elle est listee pour Nicolas
- GARDE-FOU : seules les SOCIETES (is_company) ou fiches portant un n TVA sont
  eligibles. Des particuliers Shopify (Coralie Leonard #9838/#116452, Coralie
  Petitjean #122718, Coraline Spoiden #9340 - paniers 24-64 EUR) portent a tort
  un tag "Canal GMS" : sans ce garde-fou leur B2C basculait en 700600 et
  polluait le CA GMS.
- les SO ouvertes sont repatchees : sinon une SO encodee avant la correction
  garde fiscal_position_id=False et sa facture retombe en 700000
  (c'est exactement ce qui a fait fuir le fix du 14/08)

Usage : python fp_canal_rattrapage_20260819.py [--apply]
"""
import os, sys, xmlrpc.client
from collections import defaultdict

URL='https://tea-tree.odoo.com'; DB='tsc-be-tea-tree-main-18515272'
USER='nicolas.raes@teatower.com'
PWD=os.environ.get('ODOO_PWD')
if not PWD: raise SystemExit("Definir ODOO_PWD")
uid=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common').authenticate(DB,USER,PWD,{})
m=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
def c(mo,me,a,k=None): return m.execute_kw(DB,uid,PWD,mo,me,a,k or {})

DRY = '--apply' not in sys.argv
print(f"MODE: {'DRY-RUN' if DRY else 'APPLY'}\n")

# tags canoniques -> (libelle canal, FP id), par ordre de priorite
REGLES=[('GMS',        6,  {27,88}),
        ('Institutions',35, {29,30}),
        ('Horeca',     7,  {26,84,31,33}),
        ('Revendeurs', 8,  {28,32})]
GENERIQUES={1}  # Belgium B2B : FP par defaut, ecrasable

inv=c('account.move','search_read',
      [[['move_type','in',['out_invoice','out_refund']],['state','=','posted'],['invoice_date','>=','2025-08-01']]],
      {'fields':['partner_id'],'limit':30000})
pids=sorted({i['partner_id'][0] for i in inv if i['partner_id']})
ps=c('res.partner','read',[pids],{'fields':['name','property_account_position_id','category_id','is_company','vat']})
print(f"{len(ps)} clients factures sur 12 mois analyses\n")

todo=defaultdict(list); conflits=[]; exclus_b2c=[]
for p in ps:
    cats=set(p['category_id'])
    canal=fid=None
    for lib,f,tg in REGLES:
        if cats & tg: canal,fid=lib,f; break
    if not canal: continue
    if not (p.get('is_company') or p.get('vat')):
        exclus_b2c.append((p,canal)); continue
    cur=p['property_account_position_id']
    if cur and cur[0]==fid: continue
    if not cur or cur[0] in GENERIQUES:
        todo[(canal,fid)].append(p)
    else:
        conflits.append((p,canal,cur[1]))

print("=== A CORRIGER ===")
tot=0
for (canal,fid),lst in sorted(todo.items()):
    print(f"\n  {canal} (FP #{fid}) : {len(lst)} clients")
    for p in sorted(lst,key=lambda x:(x['name'] or ''))[:8]:
        cur=p['property_account_position_id']
        print(f"     #{p['id']:6} {(p['name'] or '(sans nom)')[:44]:44} (actuel: {cur[1] if cur else 'aucune'})")
    if len(lst)>8: print(f"     ... et {len(lst)-8} autres")
    tot+=len(lst)
print(f"\n  TOTAL A CORRIGER : {tot}")

print(f"\n=== EXCLUS PAR LE GARDE-FOU (particuliers tagues canal - tag a corriger) : {len(exclus_b2c)} ===")
for p,canal in exclus_b2c:
    print(f"  #{p['id']:6} {(p['name'] or '(sans nom)')[:44]:44} tag={canal}")

print(f"\n=== CONFLITS NON TOUCHES (FP canal deja posee, contredit le tag) : {len(conflits)} ===")
for p,canal,cur in conflits:
    print(f"  #{p['id']:6} {(p['name'] or '(sans nom)')[:44]:44} tag={canal:12} FP posee={cur}")

if DRY:
    print("\nDRY : rien ecrit.")
    raise SystemExit(0)

print("\n=== ECRITURE PARTENAIRES ===")
for (canal,fid),lst in sorted(todo.items()):
    ids=[p['id'] for p in lst]
    for i in range(0,len(ids),50):
        c('res.partner','write',[ids[i:i+50],{'property_account_position_id':fid}])
    print(f"  {canal:13} : {len(ids)} fiches -> FP #{fid}")

print("\n=== REPATCH DES SO OUVERTES ===")
allfix={p['id']:fid for (canal,fid),lst in todo.items() for p in lst}
sos=c('sale.order','search_read',
      [[['partner_id','in',list(allfix)],['state','in',['draft','sent','sale']],['invoice_status','!=','invoiced']]],
      {'fields':['name','partner_id','fiscal_position_id','state']})
n=0
for s in sos:
    want=allfix[s['partner_id'][0]]
    cur=s['fiscal_position_id']
    if cur and cur[0]==want: continue
    if cur and cur[0] not in GENERIQUES: continue
    c('sale.order','write',[[s['id']],{'fiscal_position_id':want}]); n+=1
print(f"  {n} SO ouvertes repatchees (sur {len(sos)} examinees)")
print("\nTermine.")
