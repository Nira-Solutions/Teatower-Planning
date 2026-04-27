"""Test sur 1 SO seulement (S05476 puis S05473 Delhaize) avant rollout."""
import sys, importlib.util, os, json
sys.path.insert(0, os.path.abspath("compta/scripts"))
spec = importlib.util.spec_from_file_location("invoice_mod", "compta/scripts/04_invoice_and_peppol.py")
# on ne va pas tout reimporter; on copie le script et on patch SO_NAMES
import xmlrpc.client, sys, io, json, datetime as dt
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = "Teatower123"
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", allow_none=True)
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

# Reuse helpers minimaux (copies, pas import)
def vat_to_be_endpoint(vat):
    if not vat: return None
    v = "".join(c for c in vat if c.isalnum()).upper()
    if v.startswith("BE"): v = v[2:]
    if len(v) == 9: v = "0"+v
    if len(v) == 10 and v.isdigit(): return v
    return None

def ensure_peppol_partner(partner_id):
    p = call("res.partner", "read", [[partner_id]],
             {"fields":["id","name","vat","country_id","peppol_eas","peppol_endpoint",
                        "peppol_verification_state","invoice_edi_format","is_peppol_edi_format"]})[0]
    out = {"partner_id": partner_id, "name": p["name"], "before": dict(p), "changes": {}}
    country = (p.get("country_id") or [None,None])[1]
    if country == "Belgium" and (not p.get("peppol_eas") or not p.get("peppol_endpoint")):
        ep = vat_to_be_endpoint(p.get("vat"))
        if ep:
            vals = {}
            if not p.get("peppol_eas"): vals["peppol_eas"] = "0208"
            if not p.get("peppol_endpoint"): vals["peppol_endpoint"] = ep
            try:
                call("res.partner", "write", [[partner_id], vals])
                out["changes"].update(vals)
            except Exception as e:
                out["error"] = f"set EAS/EP: {e}"; return out
        else:
            out["skip"] = "no VAT BE -> cannot derive endpoint"
    p2 = call("res.partner", "read", [[partner_id]],
              {"fields":["peppol_eas","peppol_endpoint","peppol_verification_state","invoice_edi_format","is_peppol_edi_format"]})[0]
    if p2.get("peppol_eas") and p2.get("peppol_endpoint") and not p2.get("invoice_edi_format"):
        try:
            call("res.partner", "write", [[partner_id], {"invoice_edi_format":"ubl_bis3"}])
            out["changes"]["invoice_edi_format"] = "ubl_bis3"
        except Exception as e:
            out["error"] = f"set edi_format: {e}"; return out
    p3 = call("res.partner", "read", [[partner_id]],
              {"fields":["peppol_eas","peppol_endpoint","peppol_verification_state","invoice_edi_format","is_peppol_edi_format"]})[0]
    out["after"] = p3
    out["peppol_ready"] = bool(p3.get("peppol_eas") and p3.get("peppol_endpoint") and p3.get("invoice_edi_format"))
    return out

def invoice_so_delivered(so_id):
    wiz_id = call("sale.advance.payment.inv", "create",
                  [{"advance_payment_method": "delivered"}],
                  {"context": {"active_model":"sale.order", "active_ids":[so_id], "active_id": so_id}})
    call("sale.advance.payment.inv", "create_invoices", [[wiz_id]],
         {"context": {"active_model":"sale.order", "active_ids":[so_id], "active_id": so_id}})
    so = call("sale.order", "read", [[so_id]], {"fields":["invoice_ids"]})[0]
    drafts = call("account.move", "search", [[("id","in",so["invoice_ids"]),("state","=","draft")]], {})
    return (drafts[-1] if drafts else None)

def post_move(mid): return call("account.move", "action_post", [[mid]])

def send_via_wizard(move_id, want_peppol=True):
    ctx = {"active_model":"account.move","active_ids":[move_id],"active_id":move_id,"discard_attachments": False}
    wiz_id = call("account.move.send.wizard","create", [{"move_id": move_id}], {"context": ctx})
    w = call("account.move.send.wizard","read", [[wiz_id]],
             {"fields":["sending_methods","sending_method_checkboxes","invoice_edi_format","mail_partner_ids","mail_template_id","alerts","extra_edis","extra_edi_checkboxes"]})[0]
    info = {"move_id": move_id, "wizard_id": wiz_id, "before": dict(w)}
    target = ["peppol"] if want_peppol else ["email"]
    cb = {x: {"checked": (x in target), "label": x, "readonly": False} for x in ["email","peppol","manual"]}
    vals = {"sending_method_checkboxes": cb, "sending_methods": target}
    if want_peppol: vals["invoice_edi_format"] = "ubl_bis3"
    try:
        call("account.move.send.wizard","write", [[wiz_id], vals])
    except Exception as e:
        info["write_error"] = str(e)
    w2 = call("account.move.send.wizard","read", [[wiz_id]],
              {"fields":["sending_methods","sending_method_checkboxes","invoice_edi_format","mail_partner_ids","mail_template_id","alerts"]})[0]
    info["after_write"] = w2
    try:
        r = call("account.move.send.wizard","action_send_and_print", [[wiz_id]])
        info["sent"] = True; info["return"] = r
    except Exception as e:
        info["sent"] = False; info["send_error"] = str(e)
    mv = call("account.move","read", [[move_id]],
              {"fields":["name","state","peppol_is_sent","peppol_move_state","peppol_message_uuid"]})[0]
    info["move_after"] = mv
    return info

# ----- TEST -----
TARGETS = ["S05473"]  # Delhaize SA -> deja Peppol valid + ubl_bis3
for name in TARGETS:
    print(f"\n###### {name} ######", flush=True)
    s = call("sale.order","search_read",[[("name","=",name)]],{"fields":["id","name","partner_invoice_id"]})[0]
    so_id = s["id"]
    invoice_partner_id = (s.get("partner_invoice_id") or [None])[0]
    print("invoice_partner_id:", invoice_partner_id, flush=True)
    mid = invoice_so_delivered(so_id)
    print("draft move:", mid, flush=True)
    post_move(mid)
    mv = call("account.move","read",[[mid]],{"fields":["name","state","amount_total","amount_untaxed"]})[0]
    print("posted:", mv, flush=True)
    act = ensure_peppol_partner(invoice_partner_id)
    print("peppol activation:", json.dumps(act, default=str, indent=2), flush=True)
    want = bool(act.get("peppol_ready"))
    si = send_via_wizard(mid, want_peppol=want)
    print("send result:", json.dumps(si, default=str, indent=2), flush=True)
