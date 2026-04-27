"""
Rollout sur les 20 SO restantes (S05476 et S05473 deja faites en test).
- Activer Peppol partner si invoice_partner BE et VAT presente.
- Wizard d'envoi : laisser Odoo decider sending_method base sur is_peppol_edi_format -> ne JAMAIS surcharger sending_methods (sinon il refuse Peppol pour partners non Peppol).
- Si is_peppol_edi_format True -> le wizard a deja sending=['peppol']; on envoie tel quel.
- Sinon -> sending=['email'] par defaut, on envoie tel quel.
"""
import xmlrpc.client, sys, io, json, datetime as dt
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = "Teatower123"
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", allow_none=True)
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

# 20 SO restantes (sans S05473 et S05476 deja faites)
SO_NAMES = ["S05463","S05472","S05459","S05471","S05474","S05470","S05404","S05480","S05457",
            "S05467","S05481","S05478","S05468","S05402","S05486","S05475","S05483","S05412","S05484",
            "S05485"]

LOG = {"started": dt.datetime.now().isoformat(), "rows": [], "peppol_activations": [], "errors": []}

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

def send_default(move_id):
    """Ouvre le wizard, n'ecrase rien (laisse Odoo decider methode), envoie."""
    ctx = {"active_model":"account.move","active_ids":[move_id],"active_id":move_id,"discard_attachments": False}
    wiz_id = call("account.move.send.wizard","create", [{"move_id": move_id}], {"context": ctx})
    w = call("account.move.send.wizard","read", [[wiz_id]],
             {"fields":["sending_methods","invoice_edi_format","mail_partner_ids","alerts"]})[0]
    info = {"wizard_id": wiz_id, "before": dict(w)}
    try:
        r = call("account.move.send.wizard","action_send_and_print", [[wiz_id]])
        info["sent"] = True; info["return"] = r
    except Exception as e:
        info["sent"] = False; info["send_error"] = str(e)
    mv = call("account.move","read", [[move_id]],
              {"fields":["name","state","peppol_is_sent","peppol_move_state","peppol_message_uuid"]})[0]
    info["move_after"] = mv
    return info

# Pre-charge SO
sos = call("sale.order","search_read",[[("name","in",SO_NAMES)]],
           {"fields":["id","name","partner_id","partner_invoice_id","amount_to_invoice"]})
sos_by_name = {s["name"]: s for s in sos}

for name in SO_NAMES:
    row = {"so": name}
    s = sos_by_name.get(name)
    if not s: row["error"]="SO not found"; LOG["rows"].append(row); continue
    so_id = s["id"]
    invoice_partner_id = (s.get("partner_invoice_id") or [None])[0]
    row["so_id"] = so_id; row["invoice_partner_id"] = invoice_partner_id
    try:
        # 1) facture delivered
        mid = invoice_so_delivered(so_id)
        if not mid: row["error"]="no draft created"; LOG["rows"].append(row); continue
        row["move_id"] = mid
        # 2) activate peppol partner first (so wizard sees correct state)
        if invoice_partner_id:
            act = ensure_peppol_partner(invoice_partner_id)
            row["peppol_partner"] = {"changes": act.get("changes"), "ready": act.get("peppol_ready"), "skip": act.get("skip"), "error": act.get("error"), "after": act.get("after")}
            if act.get("changes"):
                LOG["peppol_activations"].append({"partner_id": invoice_partner_id, "name": act.get("name"), "changes": act.get("changes")})
        # 3) post
        post_move(mid)
        mv = call("account.move","read",[[mid]],{"fields":["name","state","amount_total","amount_untaxed"]})[0]
        row["invoice_name"]=mv["name"]; row["invoice_state"]=mv["state"]
        row["amount_total"]=mv["amount_total"]; row["amount_untaxed"]=mv["amount_untaxed"]
        # 4) send
        si = send_default(mid)
        row["send"] = si
    except Exception as e:
        row["fatal"] = str(e); LOG["errors"].append({"so":name,"error":str(e)})
    LOG["rows"].append(row)
    method = (row.get("send",{}).get("before",{}) or {}).get("sending_methods")
    print(f"[{name}] -> {row.get('invoice_name','?')} | {row.get('amount_total','?')} TTC | method={method} | peppol_state={row.get('send',{}).get('move_after',{}).get('peppol_move_state')}", flush=True)

LOG["ended"] = dt.datetime.now().isoformat()
with open("compta/scripts/_rollout_log.json","w",encoding="utf-8") as f:
    json.dump(LOG, f, indent=2, default=str)
print("\nDONE", flush=True)
