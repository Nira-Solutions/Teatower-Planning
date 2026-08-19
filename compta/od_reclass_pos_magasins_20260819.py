"""
OD de reclassement : CA POS 700000 -> comptes 7004xx par magasin
----------------------------------------------------------------
Complement de pos_comptes_par_magasin_20260819.py (qui ne vaut que pour les
commandes creees APRES la pose de la position fiscale sur la pos.config).
Reclasse l'historique du FY26-27 mois par mois.

Source des montants : lignes 700000 du journal "Point de Vente", rattachees a
leur pos.session via session.move_id -> config_id. 100% des lignes sont
rattachees (0 orphelin verifie le 19/08/26).

NE TOUCHE PAS AU FY25-26 (gele au 19/08/26). L'OD reclasse le produit seul,
sans les lignes produit : elle sert la presentation du compte de resultat,
PAS l'analyse de marge par magasin (celle-la reste sur les rapports POS).

Usage : python od_reclass_pos_magasins_20260819.py --month 2026-07 [--apply]
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
MONTH=None
for i,a in enumerate(sys.argv):
    if a=='--month' and i+1<len(sys.argv): MONTH=sys.argv[i+1]
if not MONTH: raise SystemExit("--month YYYY-MM obligatoire")
if MONTH < '2026-07': raise SystemExit("REFUS : FY25-26 est gele, pas de reclassement avant 2026-07")

import calendar
y,mo=int(MONTH[:4]),int(MONTH[5:7])
d_from=f"{MONTH}-01"; d_to=f"{MONTH}-{calendar.monthrange(y,mo)[1]:02d}"
print(f"MODE: {'DRY-RUN' if DRY else 'APPLY'} | periode {d_from} -> {d_to}\n")

CFG2ACC={4:'700410', 3:'700420', 5:'700420', 7:'700430', 1:'700440', 2:'700450'}
codes=set(CFG2ACC.values())|{'700000'}
accs={a['code']:a['id'] for a in c('account.account','search_read',[[['code','in',list(codes)]]],{'fields':['code']})}

sess=c('pos.session','search_read',[[['state','=','closed'],['move_id','!=',False]]],{'fields':['config_id','move_id']})
mv2cfg={s['move_id'][0]:s['config_id'] for s in sess}
ml=c('account.move.line','search_read',
    [[['account_id.code','=','700000'],['journal_id.name','=','Point de Vente'],
      ['date','>=',d_from],['date','<=',d_to],['parent_state','=','posted']]],
    {'fields':['move_id','balance']})
agg=defaultdict(float); orphan=0.0
for l in ml:
    cfg=mv2cfg.get(l['move_id'][0])
    if not cfg: orphan+=-l['balance']; continue
    agg[CFG2ACC.get(cfg[0])]+=-l['balance']
if orphan:
    print(f"  !! {orphan:,.2f} EUR sur des moves sans session -> laisses en 700000")
agg={k:round(v,2) for k,v in agg.items() if k and round(v,2)}
total=round(sum(agg.values()),2)
if not total: raise SystemExit("Rien a reclasser sur cette periode.")

print("=== RECLASSEMENT ===")
for k,v in sorted(agg.items(), key=lambda x:-x[1]):
    print(f"  700000 -> {k}  {v:12,.2f}")
print(f"  {'TOTAL':21} {total:12,.2f}")

jid=c('account.journal','search_read',[[['type','=','general']]],{'fields':['name'],'limit':1})[0]
label=f"Reclassement CA magasins {MONTH}"
lines=[(0,0,{'account_id':accs['700000'],'name':label,'debit':total,'credit':0.0})]
for code,v in sorted(agg.items()):
    lines.append((0,0,{'account_id':accs[code],'name':label,'debit':0.0,'credit':v}))

if DRY:
    print(f"\nDRY : OD non creee (journal {jid['name']}, date {d_to}, {len(lines)} lignes)")
    raise SystemExit(0)

exist=c('account.move','search_read',[[['ref','=',label],['journal_id','=',jid['id']]]],{'fields':['name','state']})
if exist:
    raise SystemExit(f"REFUS : une OD '{label}' existe deja ({exist[0]['name']}, {exist[0]['state']}) - doublon evite.")
mid=c('account.move','create',[{'move_type':'entry','journal_id':jid['id'],'date':d_to,'ref':label,'line_ids':lines}])
c('account.move','action_post',[[mid]])
res=c('account.move','read',[[mid]],{'fields':['name','state','amount_total']})[0]
print(f"\nOD POSTEE : {res['name']} | state={res['state']} | {total:,.2f} EUR reclasses")
