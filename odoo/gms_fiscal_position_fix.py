# -*- coding: utf-8 -*-
"""FIX canal GMS : position fiscale GMS (id 6) + hygiène des tags canal
sur toutes les enseignes GMS (Spar / Intermarché / Delhaize / Colruyt / Carrefour / Okay / Cora / Match / Alvo).
Effet : les futures factures imputent 700600 « Ventes GMS » au lieu de 700000 « Sales in Belgium ».
AUCUN impact TVA (la FP GMS ne porte aucun tax map — vérifié).
Usage: gms_fix.py [--apply]   (sans --apply = dry-run)
"""
import xmlrpc.client, os, sys, re, json, datetime
sys.stdout.reconfigure(encoding="utf-8")
APPLY = "--apply" in sys.argv
URL="https://tea-tree.odoo.com"; DB="tsc-be-tea-tree-main-18515272"
USER="nicolas.raes@teatower.com"; PWD=os.environ["ODOO_PWD"]
uid=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB,USER,PWD,{})
m=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def C(model,method,args,kw=None): return m.execute_kw(DB,uid,PWD,model,method,args,kw or {})

FP_GMS=6
TAG_GMS=27; TAG_CANAL_GMS=88
TAG_CONFLIT=[26,28,32,84,85]   # HoReCA, Revendeur, Grossiste, Canal Horeca, Canal B2B Direct
ENS=[("SPAR",r"(?<![a-z])spar(?![a-z])"),("INTERMARCHE",r"intermarch"),("DELHAIZE",r"delhaize"),
     ("COLRUYT",r"colruyt"),("OKAY",r"(?<![a-z])ok[ae]y(?![a-z])"),("CARREFOUR",r"carrefour"),
     ("CORA",r"(?<![a-z])cora(?![a-z])"),("MATCH",r"(?<![a-z])s?match(?![a-z])"),
     ("ALVO",r"(?<![a-z])alvo(?![a-z])")]
EXCLUDE_IDS={2903}  # DEDROP - Brasserie le Carrefour = Horeca, pas GMS

ids=C("res.partner","search",[["|",["customer_rank",">",0],["category_id","in",[27,88]]]],{"limit":30000})
recs=[]
for i in range(0,len(ids),500):
    recs+=C("res.partner","read",[ids[i:i+500]],
        {"fields":["id","name","category_id","property_account_position_id","parent_id","active"]})

def ens_of(n):
    n=(n or "").lower()
    for lbl,pat in ENS:
        if re.search(pat,n): return lbl
    return None

targets=[]
for r in recs:
    if r["id"] in EXCLUDE_IDS: continue
    e=ens_of(r["name"])
    if not e: continue
    fp=r["property_account_position_id"]
    need_fp = not (fp and fp[0]==FP_GMS)
    need_add = [t for t in (TAG_GMS,TAG_CANAL_GMS) if t not in r["category_id"]]
    need_del = [t for t in TAG_CONFLIT if t in r["category_id"]]
    if need_fp or need_add or need_del:
        targets.append({"id":r["id"],"name":r["name"],"ens":e,"old_fp":fp,
                        "old_tags":r["category_id"],"need_fp":need_fp,
                        "add":need_add,"del":need_del})

print(f"{'[APPLY]' if APPLY else '[DRY-RUN]'} {len(targets)} partners à corriger")
by_ens={}
for t in targets: by_ens[t["ens"]]=by_ens.get(t["ens"],0)+1
print("  par enseigne :", by_ens)
print(f"  FP à poser : {sum(1 for t in targets if t['need_fp'])}")
print(f"  tags canal en conflit à retirer : {sum(1 for t in targets if t['del'])}")

# SO ouvertes (non encore facturées) : aligner la FP pour que la prochaine facture tombe en 700600
pids=[t["id"] for t in targets]
so=C("sale.order","search_read",[[["partner_id","in",pids],["state","in",["draft","sent","sale"]],
      ["invoice_status","!=","invoiced"]]],
     {"fields":["name","partner_id","fiscal_position_id","invoice_status","amount_untaxed"]})
so_fix=[s for s in so if not (s["fiscal_position_id"] and s["fiscal_position_id"][0]==FP_GMS)]
print(f"  commandes ouvertes non facturées à réaligner : {len(so_fix)}")
for s in so_fix: print(f"     {s['name']} {s['partner_id'][1][:40]} {s['invoice_status']} FP={s['fiscal_position_id']} {s['amount_untaxed']:.2f}")

if not APPLY:
    print("\n(dry-run — relancer avec --apply)")
    sys.exit(0)

# --- ROLLBACK LOG ---
stamp="20260814"
json.dump(targets, open(f"gms_fix_rollback_{stamp}.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)

ok=err=0
for t in targets:
    vals={}
    if t["need_fp"]: vals["property_account_position_id"]=FP_GMS
    cmds=[(4,x) for x in t["add"]]+[(3,x) for x in t["del"]]
    if cmds: vals["category_id"]=cmds
    try:
        C("res.partner","write",[[t["id"]],vals]); ok+=1
    except Exception as ex:
        err+=1; print("  ERREUR",t["id"],t["name"],ex)
print(f"partners écrits : {ok} ok / {err} erreurs")

so_ok=0
for s in so_fix:
    try:
        C("sale.order","write",[[s["id"]],{"fiscal_position_id":FP_GMS}]); so_ok+=1
    except Exception as ex:
        print("  ERREUR SO",s["name"],ex)
print(f"commandes réalignées : {so_ok}/{len(so_fix)}")

# --- CONTROLE ---
chk=C("res.partner","read",[pids],{"fields":["id","name","property_account_position_id","category_id"]})
bad=[c for c in chk if not (c["property_account_position_id"] and c["property_account_position_id"][0]==FP_GMS)]
print("contrôle : partners encore sans FP GMS ->", len(bad), [b["name"] for b in bad][:10])
badtag=[c for c in chk if TAG_GMS not in c["category_id"] or TAG_CANAL_GMS not in c["category_id"]]
print("contrôle : partners sans les 2 tags GMS ->", len(badtag))
conf=[c for c in chk if any(x in TAG_CONFLIT for x in c["category_id"])]
print("contrôle : tags canal en conflit restants ->", len(conf))
