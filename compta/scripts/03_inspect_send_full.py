import xmlrpc.client, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = "Teatower123"
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

# 1) tous les champs du wizard
f = call("account.move.send.wizard", "fields_get", [], {"attributes": ["string","type","selection","required","readonly","help"]})
print("== account.move.send.wizard FIELDS ==", flush=True)
for k in sorted(f.keys()):
    print(f"  {k} :: {f[k].get('type')} :: {f[k].get('string')} :: req={f[k].get('required')}", flush=True)

# 2) factures recentes Peppol-sent
inv_ids = call("account.move", "search", [[("peppol_is_sent","=",True),("move_type","=","out_invoice")]], {"limit":3, "order":"id desc"})
if inv_ids:
    invs = call("account.move", "read", [inv_ids], {"fields":["id","name","state","partner_id","invoice_partner_display_name","peppol_is_sent","peppol_move_state","peppol_message_uuid","sending_data"]})
    print("\n== Sample invoices Peppol-sent ==", flush=True)
    print(json.dumps(invs, default=str, indent=2), flush=True)
else:
    print("\n(no peppol_is_sent invoice)", flush=True)

# 3) Verifier l'autorisation Peppol Teatower (compagnie)
comp = call("res.company", "fields_get", [], {"attributes":["string","type"]})
ck = sorted([k for k in comp if "peppol" in k.lower() or "edi" in k.lower() or "einvoice" in k.lower() or "e_invoice" in k.lower()])
print("\n== res.company Peppol/edi fields ==", flush=True)
for k in ck: print(f"  {k} :: {comp[k]}", flush=True)
crow = call("res.company", "read", [[1]], {"fields": ck})
print("\n== Teatower company state ==", flush=True)
print(json.dumps(crow, default=str, indent=2), flush=True)
