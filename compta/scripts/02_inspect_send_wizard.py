"""
Inspect account.move.send (et variantes) pour decouvrir la mecanique d'envoi Peppol.
"""
import xmlrpc.client, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = "Teatower123"
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

candidates = [
    "account.move.send",
    "account.move.send.wizard",
    "account.move.send.batch.wizard",
    "mail.compose.message",
    "account.peppol.send.wizard",
]
for mod in candidates:
    try:
        f = call(mod, "fields_get", [], {"attributes": ["string", "type", "selection"]})
        keys = [k for k in f if any(s in k.lower() for s in ["peppol","send","method","format","edi"])]
        print(f"\n== {mod} ({len(f)} fields, peppol/send subset {len(keys)}) ==", flush=True)
        for k in sorted(keys):
            sel = f[k].get("selection")
            print(f"  {k} :: {f[k].get('type')} :: {f[k].get('string')} :: sel={sel}", flush=True)
    except Exception as e:
        print(f"\n== {mod} : not found ({e}) ==", flush=True)

# Methodes utiles sur account.move
methods = call("account.move", "fields_get", [], {"attributes":["string"]})
# pas de listing methodes via xml-rpc; on liste par exec dry sur une facture:
# rien a faire, on testera live.

# Inspecter la valeur possible de invoice_edi_format sur res.partner
fp = call("res.partner", "fields_get", [["invoice_edi_format"]], {"attributes":["selection"]})
print("\n== res.partner invoice_edi_format selection ==", flush=True)
print(json.dumps(fp, default=str, indent=2), flush=True)

# settings courants e-invoice
ir_company = call("res.company", "search_read", [[]], {"fields":["id","name","country_id","vat","partner_id"]})
print("\n== Companies ==", flush=True)
print(json.dumps(ir_company, default=str, indent=2), flush=True)
