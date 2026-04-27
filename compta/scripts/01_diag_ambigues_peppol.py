"""
Diag :
1) S05478 et S05476 : qty_delivered>0 sans picking done -> creuser stock.move/picking.
2) Inventaire des partners deja Peppol-actifs : chercher les champs presents (peppol_eas, peppol_endpoint, peppol_verification_state, invoice_sending_method, invoice_edi_format / is_peppol_edi_format).
3) Sortir les 22 partners cibles : etat Peppol courant + TVA + pays.
"""
import xmlrpc.client, json, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = "Teatower123"
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

OUT = {}

# --- 1) Decouvrir les champs Peppol disponibles sur res.partner et account.move ---
def fields_of(model):
    f = call(model, "fields_get", [], {"attributes": ["string", "type", "selection"]})
    return f

partner_fields = fields_of("res.partner")
move_fields = fields_of("account.move")

peppol_partner_fields = sorted([k for k in partner_fields if "peppol" in k.lower() or "edi" in k.lower() or "einvoice" in k.lower() or "e_invoice" in k.lower()])
peppol_move_fields = sorted([k for k in move_fields if "peppol" in k.lower() or "edi" in k.lower() or "sending" in k.lower() or "einvoice" in k.lower()])

print("== res.partner Peppol-related fields ==", flush=True)
for k in peppol_partner_fields:
    print(f"  {k} :: {partner_fields[k].get('type')} :: {partner_fields[k].get('string')}", flush=True)
print("\n== account.move Peppol/sending-related fields ==", flush=True)
for k in peppol_move_fields:
    print(f"  {k} :: {move_fields[k].get('type')} :: {move_fields[k].get('string')}", flush=True)

OUT["partner_peppol_fields"] = peppol_partner_fields
OUT["move_peppol_fields"] = peppol_move_fields

# --- 2) Diag SO ambiguës ---
def diag_so(name):
    r = call("sale.order", "search_read", [[("name", "=", name)]],
             {"fields": ["id", "name", "state", "partner_id", "picking_ids", "amount_to_invoice", "order_line"]})
    if not r: return {"name": name, "found": False}
    so = r[0]
    pickings = call("stock.picking", "read", [so["picking_ids"]],
                    {"fields": ["id", "name", "state", "scheduled_date", "date_done", "picking_type_id", "location_dest_id"]}) if so["picking_ids"] else []
    # qty_delivered non-zero lines
    lines = call("sale.order.line", "read", [so["order_line"]],
                 {"fields": ["id", "product_id", "product_uom_qty", "qty_delivered", "qty_invoiced", "price_subtotal"]})
    nz = [l for l in lines if l.get("qty_delivered") or 0]
    # stock.move done lies aux SO lines
    move_ids = call("stock.move", "search", [[("sale_line_id", "in", so["order_line"])]])
    moves = call("stock.move", "read", [move_ids], {"fields": ["id", "state", "product_id", "product_uom_qty", "quantity", "date", "picking_id", "location_dest_id"]}) if move_ids else []
    return {
        "name": name, "found": True, "id": so["id"], "state": so["state"],
        "partner": so["partner_id"], "amount_to_invoice": so["amount_to_invoice"],
        "pickings": pickings,
        "nb_lines_delivered_nonzero": len(nz),
        "lines_delivered_nonzero": nz,
        "moves": moves,
    }

OUT["S05478"] = diag_so("S05478")
OUT["S05476"] = diag_so("S05476")

print("\n== Diag S05478 ==", flush=True)
print(json.dumps(OUT["S05478"], indent=2, default=str), flush=True)
print("\n== Diag S05476 ==", flush=True)
print(json.dumps(OUT["S05476"], indent=2, default=str), flush=True)

# --- 3) Partners cibles (22 SO) : etat Peppol + TVA ---
SO_NAMES = ["S05473","S05463","S05472","S05459","S05471","S05474","S05470","S05404","S05480","S05457",
            "S05467","S05481","S05478","S05468","S05402","S05486","S05475","S05483","S05412","S05484",
            "S05485","S05476"]

so_rows = call("sale.order", "search_read", [[("name","in",SO_NAMES)]],
               {"fields":["id","name","partner_id","partner_invoice_id","amount_to_invoice","state","invoice_status"]})
partner_ids = sorted({r["partner_invoice_id"][0] for r in so_rows if r.get("partner_invoice_id")} | {r["partner_id"][0] for r in so_rows if r.get("partner_id")})

# fields a lire en fonction de ce qui existe
read_fields = ["id","name","vat","country_id","email"] + [f for f in peppol_partner_fields]
read_fields = list(dict.fromkeys(read_fields))  # dedup keep order

partners_state = call("res.partner", "read", [partner_ids], {"fields": read_fields})

# --- 4) Echantillon de partners deja Peppol-valid ---
sample = []
if "peppol_verification_state" in partner_fields:
    valid_ids = call("res.partner", "search", [[("peppol_verification_state","=","valid")]], {"limit": 20})
    if valid_ids:
        sample = call("res.partner", "read", [valid_ids], {"fields": read_fields})

OUT["so_rows"] = so_rows
OUT["target_partners"] = partners_state
OUT["sample_peppol_valid"] = sample

print(f"\n== Sample partners Peppol valid : {len(sample)} ==", flush=True)
for p in sample[:5]:
    print(json.dumps({k:p.get(k) for k in read_fields if k in p}, default=str), flush=True)

print(f"\n== Target partners ({len(partners_state)}) ==", flush=True)
for p in partners_state:
    s = {k:p.get(k) for k in read_fields if k in p}
    print(json.dumps(s, default=str), flush=True)

with open("compta/scripts/_diag_out.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, indent=2, default=str)
print("\nSaved compta/scripts/_diag_out.json", flush=True)
