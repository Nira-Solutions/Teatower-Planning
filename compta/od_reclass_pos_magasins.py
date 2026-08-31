"""
OD de reclassement : CA POS 700000 -> comptes 7004xx par magasin  (v2)
---------------------------------------------------------------------
Remplace od_reclass_pos_magasins_20260819.py (v1), qui ne lisait que le journal
"Point de Vente" et laissait donc les tickets FACTURES au comptoir en 700000
(6.251,71 EUR sur juillet+aout 2026 constates le 31/08/26).

v2 :
  - source elargie : TOUTE ligne 700000 du mois rattachable a un magasin, que le
    move vienne d'une pos.session (journal Point de Vente) ou de la facture d'un
    ticket (pos.order.account_move -> journaux "Factures de ventes magasins ..."
    ou "Customer Invoices"). Le reste de 700000 (B2B, e-commerce) n'est pas touche.
  - IDEMPOTENT : calcule la cible du mois, retranche ce qui est deja sur les
    7004xx pour ce mois, et ne poste que le DELTA. Relancable autant de fois que
    voulu -- notamment le lendemain d'une cloture pour rattraper les sessions du
    dernier jour. Plus de refus "doublon" : s'il n'y a plus de delta, il ne se
    passe rien.

NE TOUCHE PAS AU FY25-26 (gele au 19/08/26). L'OD reclasse le produit seul, sans
les lignes produit : elle sert la presentation du compte de resultat, PAS
l'analyse de marge par magasin (celle-la reste sur les rapports POS).

Usage : python od_reclass_pos_magasins.py --month 2026-08 [--apply]
"""
import os, re, sys, calendar, xmlrpc.client
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

y,mo=int(MONTH[:4]),int(MONTH[5:7])
d_from=f"{MONTH}-01"; d_to=f"{MONTH}-{calendar.monthrange(y,mo)[1]:02d}"
print(f"MODE: {'DRY-RUN' if DRY else 'APPLY'} | periode {d_from} -> {d_to}\n")

CFG2ACC={4:'700410', 3:'700420', 5:'700420', 7:'700430', 1:'700440', 2:'700450'}
codes=set(CFG2ACC.values())|{'700000'}
accs={a['code']:a['id'] for a in c('account.account','search_read',
     [[['code','in',list(codes)]]],{'fields':['code']})}
ACC2CODE={v:k for k,v in accs.items()}

# --- mapping move -> magasin : sessions cloturees + factures de tickets --------
sess=c('pos.session','search_read',[[['move_id','!=',False]]],
       {'fields':['config_id','move_id']})
mv2cfg={s['move_id'][0]:s['config_id'][0] for s in sess}
# Extournes d'ecriture de fermeture (ticket d'une session deja cloturee facture
# apres coup) : Odoo ne remplit pas reversed_entry_id, la session est citee dans
# le ref -> "... liee a la session POS/00963".
sess_by_name={s['name']:s['config_id'][0] for s in
    c('pos.session','search_read',[[]],{'fields':['name','config_id']})}
extr=c('account.move','search_read',
    [[['journal_id.name','=','Point de Vente'],['ref','like','%session POS/%'],
      ['date','>=','2026-07-01']]],{'fields':['ref']})
for e in extr:
    mo=re.search(r'session (POS/\d+)', e['ref'] or '')
    if mo and mo.group(1) in sess_by_name:
        mv2cfg.setdefault(e['id'], sess_by_name[mo.group(1)])
orders=c('pos.order','search_read',
    [[['state','=','invoiced'],['account_move','!=',False],['date_order','>=','2026-06-25']]],
    {'fields':['config_id','account_move']})
for o in orders:
    mv2cfg.setdefault(o['account_move'][0], o['config_id'][0])

# --- cible du mois -------------------------------------------------------------
ml=c('account.move.line','search_read',
    [[['account_id','=',accs['700000']],['date','>=',d_from],['date','<=',d_to],
      ['parent_state','=','posted']]],
    {'fields':['move_id','balance','journal_id']})
cible=defaultdict(float); reste=defaultdict(float)
for l in ml:
    cfg=mv2cfg.get(l['move_id'][0])
    if cfg and CFG2ACC.get(cfg): cible[CFG2ACC[cfg]]+=-l['balance']
    else: reste[l['journal_id'][1]]+=-l['balance']
cible={k:round(v,2) for k,v in cible.items()}

# --- deja reclasse sur les 7004xx pour ce mois ---------------------------------
deja=defaultdict(float)
dl=c('account.move.line','search_read',
    [[['account_id','in',[accs[k] for k in set(CFG2ACC.values()) if k in accs]],
      ['date','>=',d_from],['date','<=',d_to],['parent_state','=','posted']]],
    {'fields':['account_id','balance']})
for l in dl: deja[ACC2CODE[l['account_id'][0]]]+=-l['balance']
deja={k:round(v,2) for k,v in deja.items()}

print("=== CIBLE DU MOIS (700000 rattachable a un magasin) ===")
for k in sorted(set(cible)|set(deja)):
    print(f"  {k}  cible {cible.get(k,0.0):12,.2f}   deja {deja.get(k,0.0):12,.2f}"
          f"   delta {round(cible.get(k,0.0)-deja.get(k,0.0),2):12,.2f}")
if reste:
    print("\n  700000 non rattachable a un magasin (laisse en 700000) :")
    for j,v in sorted(reste.items(), key=lambda x:-x[1]):
        print(f"    {j[:40]:40} {v:12,.2f}")

delta={k:round(cible.get(k,0.0)-deja.get(k,0.0),2) for k in set(cible)|set(deja)}
delta={k:v for k,v in delta.items() if abs(v)>=0.01}
total=round(sum(delta.values()),2)
if not delta or abs(total)<0.01:
    raise SystemExit("\nRien a reclasser : les 7004xx sont deja a jour sur ce mois.")

print(f"\n=== OD A POSTER (delta) ===")
for k,v in sorted(delta.items(), key=lambda x:-x[1]):
    print(f"  700000 -> {k}  {v:12,.2f}")
print(f"  {'TOTAL':21} {total:12,.2f}")

jid=c('account.journal','search_read',[[['type','=','general']]],{'fields':['name'],'limit':1})[0]
base=f"Reclassement CA magasins {MONTH}"
n=len(c('account.move','search_read',[[['ref','like',base+'%'],['journal_id','=',jid['id']],
        ['state','!=','cancel']]],{'fields':['name']}))
label=base if n==0 else f"{base} (complement {n})"

def leg(acc_id,amount):
    return (0,0,{'account_id':acc_id,'name':label,
                 'debit':round(amount,2) if amount>0 else 0.0,
                 'credit':round(-amount,2) if amount<0 else 0.0})
lines=[leg(accs['700000'], total)]
for code,v in sorted(delta.items()):
    lines.append(leg(accs[code], -v))

if DRY:
    print(f"\nDRY : OD non creee (journal {jid['name']}, date {d_to}, ref '{label}', {len(lines)} lignes)")
    raise SystemExit(0)

mid=c('account.move','create',[{'move_type':'entry','journal_id':jid['id'],
      'date':d_to,'ref':label,'line_ids':lines}])
c('account.move','action_post',[[mid]])
res=c('account.move','read',[[mid]],{'fields':['name','state']})[0]
print(f"\nOD POSTEE : {res['name']} | ref '{label}' | state={res['state']} | {total:,.2f} EUR reclasses")
