# -*- coding: utf-8 -*-
"""MATCHER lecture seule des lignes bancaires SORTANTES non lettrees ING/Belfius
contre les factures fournisseurs ouvertes."""
import os, re, json, unicodedata, itertools
import xmlrpc.client

URL="https://tea-tree.odoo.com"; DB="tsc-be-tea-tree-main-18515272"
USER="nicolas.raes@teatower.com"; PWD=os.environ.get("ODOO_PWD")
common=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common"); uid=common.authenticate(DB,USER,PWD,{})
m=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model,method,args,kw=None): return m.execute_kw(DB,uid,PWD,model,method,args,kw or {})

def norm(s):
    s=unicodedata.normalize("NFKD",s or "").encode("ascii","ignore").decode()
    return re.sub(r"[^a-z0-9]+"," ",s.lower()).strip()

JOURNALS={14:"ING",36:"BELFIUS"}
rows=call("account.bank.statement.line","search_read",
   [[["journal_id","in",list(JOURNALS)],["is_reconciled","=",False],["amount","<",0]]],
   {"fields":["id","date","payment_ref","amount","partner_id","journal_id"],"order":"date asc, id asc"})
print(f"{len(rows)} lignes sortantes\n")

# toutes les factures fournisseurs ouvertes
bills=call("account.move","search_read",
   [[["move_type","in",["in_invoice","in_refund"]],["state","=","posted"],
     ["payment_state","in",["not_paid","partial"]]]],
   {"fields":["name","ref","invoice_date","amount_total","amount_residual","partner_id","payment_reference"]})
print(f"{len(bills)} factures fournisseurs ouvertes")
by_partner={}
for b in bills: by_partner.setdefault(b["partner_id"][0],[]).append(b)

partners=call("res.partner","search_read",[[["supplier_rank",">",0]]],{"fields":["name"]})
pmap=[(norm(p["name"]),p["id"],p["name"]) for p in partners if len(norm(p["name"]))>=4]

res=[]
for r in rows:
    ref=(r.get("payment_ref") or "").replace("\n"," ")
    nref=norm(ref); amt=abs(r["amount"]); j=JOURNALS[r["journal_id"][0]]
    cands=[]
    for npn,pid,pn in pmap:
        toks=npn.split()
        key=" ".join(toks[:2]) if len(toks)>=2 else npn
        if len(key)>=6 and key in nref: cands.append((pid,pn))
    detail=""; tag="---"
    seen=set()
    for pid,pn in cands:
        if pid in seen: continue
        seen.add(pid)
        bl=by_partner.get(pid,[])
        ex=[b for b in bl if abs(abs(b["amount_residual"])-amt)<0.005]
        ne=[b for b in bl if 0.005<=abs(abs(b["amount_residual"])-amt)<=5.0]
        pick=ex or ne or bl[:3]
        if ex: tag=f"{pn[:24]} |EXACT|"
        elif ne and tag=="---": tag=f"{pn[:24]} |<=5EUR|"
        elif tag=="---": tag=f"{pn[:24]} |{len(bl)} ouvertes|"
        if pick: detail+=" ; ".join(f"{b['name']}/{b.get('ref') or ''} {b['invoice_date']} res={b['amount_residual']:.2f}" for b in pick[:3])+" "
    print(f"{r['id']:>6} {j:<7} {r['date']} {r['amount']:>11,.2f} | {tag[:40]:40} | {detail[:150]}")
    res.append({"id":r["id"],"j":j,"date":r["date"],"amount":r["amount"],"ref":ref,"tag":tag,"detail":detail})
json.dump(res,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"_match_sortants_20260901.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
