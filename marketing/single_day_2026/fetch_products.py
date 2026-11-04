import xmlrpc.client, os, base64, json
URL="https://tea-tree.odoo.com"; DB="tsc-be-tea-tree-main-18515272"; USER="nicolas.raes@teatower.com"
PWD=os.environ.get("ODOO_PWD")
uid=xmlrpc.client.ServerProxy(URL+"/xmlrpc/2/common").authenticate(DB,USER,PWD,{})
m=xmlrpc.client.ServerProxy(URL+"/xmlrpc/2/object",allow_none=True)
codes=["A0271","A0304","V0839","V0617","V0841"]
out={}
here=os.path.dirname(os.path.abspath(__file__))
for c in codes:
    r=m.execute_kw(DB,uid,PWD,"product.product","search_read",[[["default_code","=",c]]],{"fields":["name","list_price","image_1920","description_sale"],"context":{"lang":"fr_FR"},"limit":1})
    if not r: out[c]=None; continue
    p=r[0]; img=p.pop("image_1920")
    if img:
        open(os.path.join(here,"img",c+".png"),"wb").write(base64.b64decode(img))
    p["has_img"]=bool(img); out[c]=p
print(json.dumps(out,ensure_ascii=False,indent=1))
