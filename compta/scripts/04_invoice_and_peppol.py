"""
Execution :
1) Facture les 22 SO via wizard sale.advance.payment.inv mode 'delivered' (jamais 'all').
2) Poste les factures.
3) Active Peppol EDI sur les invoice_partners eligibles si invoice_edi_format vide.
4) Envoie chaque facture :
   - Si invoice_partner peppol_can et infos completes -> sending_methods=['peppol'], format=ubl_bis3.
   - Sinon -> fallback email standard.
5) Logge tout en JSON.
"""
import xmlrpc.client, sys, io, json, time, datetime as dt
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = "Teatower123"
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", allow_none=True)
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

SO_NAMES = ["S05473","S05463","S05472","S05459","S05471","S05474","S05470","S05404","S05480","S05457",
            "S05467","S05481","S05478","S05468","S05402","S05486","S05475","S05483","S05412","S05484",
            "S05485","S05476"]

LOG = {"started": dt.datetime.now().isoformat(), "rows": [], "peppol_activations": [], "errors": []}

# Pre-load SO
sos = call("sale.order", "search_read", [[("name","in",SO_NAMES)]],
           {"fields":["id","name","partner_id","partner_invoice_id","amount_to_invoice","invoice_status"]})
sos_by_name = {s["name"]: s for s in sos}

def vat_to_be_endpoint(vat):
    if not vat: return None
    v = "".join(c for c in vat if c.isalnum()).upper()
    if v.startswith("BE"): v = v[2:]
    if len(v) == 9: v = "0"+v  # forme historique
    if len(v) == 10 and v.isdigit(): return v
    return None

def ensure_peppol_partner(partner_id):
    """Active EDI Peppol pour un partner si possible. Retourne dict {ok, reason, fields_set}."""
    p = call("res.partner", "read", [[partner_id]],
             {"fields":["id","name","vat","country_id","peppol_eas","peppol_endpoint",
                        "peppol_verification_state","invoice_edi_format","is_peppol_edi_format"]})[0]
    out = {"partner_id": partner_id, "name": p["name"], "before": dict(p), "changes": {}}
    country = (p.get("country_id") or [None,None])[1]
    is_be = country == "Belgium"

    # Step a: si pas de EAS/EP, completer (BE seulement) depuis VAT
    if is_be and (not p.get("peppol_eas") or not p.get("peppol_endpoint")):
        ep = vat_to_be_endpoint(p.get("vat"))
        if ep:
            vals = {}
            if not p.get("peppol_eas"): vals["peppol_eas"] = "0208"
            if not p.get("peppol_endpoint"): vals["peppol_endpoint"] = ep
            try:
                call("res.partner", "write", [[partner_id], vals])
                out["changes"].update(vals)
            except Exception as e:
                out["error"] = f"set EAS/EP: {e}"
                return out
        else:
            out["skip"] = "no VAT BE -> cannot derive endpoint"

    # Re-read
    p2 = call("res.partner", "read", [[partner_id]],
              {"fields":["peppol_eas","peppol_endpoint","peppol_verification_state","invoice_edi_format","is_peppol_edi_format"]})[0]

    # Step b: invoice_edi_format = ubl_bis3 si EAS+EP renseignes
    if p2.get("peppol_eas") and p2.get("peppol_endpoint") and not p2.get("invoice_edi_format"):
        try:
            call("res.partner", "write", [[partner_id], {"invoice_edi_format":"ubl_bis3"}])
            out["changes"]["invoice_edi_format"] = "ubl_bis3"
        except Exception as e:
            out["error"] = f"set edi_format: {e}"
            return out

    # Final read
    p3 = call("res.partner", "read", [[partner_id]],
              {"fields":["peppol_eas","peppol_endpoint","peppol_verification_state","invoice_edi_format","is_peppol_edi_format"]})[0]
    out["after"] = p3
    out["peppol_ready"] = bool(p3.get("peppol_eas") and p3.get("peppol_endpoint") and p3.get("invoice_edi_format"))
    return out

def invoice_so_delivered(so_id):
    """Cree la facture en mode delivered. Retourne move_id."""
    wiz_id = call("sale.advance.payment.inv", "create",
                  [{"advance_payment_method": "delivered"}],
                  {"context": {"active_model":"sale.order", "active_ids":[so_id], "active_id": so_id}})
    res = call("sale.advance.payment.inv", "create_invoices",
               [[wiz_id]],
               {"context": {"active_model":"sale.order", "active_ids":[so_id], "active_id": so_id}})
    # recuperer la facture liee a la SO (etat draft)
    so = call("sale.order", "read", [[so_id]], {"fields":["invoice_ids"]})[0]
    inv_ids = so["invoice_ids"]
    drafts = call("account.move", "search", [[("id","in",inv_ids),("state","=","draft")]], {})
    if not drafts:
        # peut-etre deja postee
        return None, "no draft created (already invoiced?)"
    move_id = drafts[-1]
    return move_id, None

def post_move(move_id):
    return call("account.move", "action_post", [[move_id]])

def send_via_wizard(move_id, want_peppol=True):
    """Cree wizard, choisit sending method, envoie. Retourne dict resume."""
    # Open the wizard with default_get
    ctx = {"active_model":"account.move", "active_ids":[move_id], "active_id": move_id, "discard_attachments": False}
    wiz_id = call("account.move.send.wizard", "create", [{"move_id": move_id}], {"context": ctx})
    # Lire les valeurs prepares
    w = call("account.move.send.wizard", "read", [[wiz_id]],
             {"fields":["sending_methods","sending_method_checkboxes","invoice_edi_format","mail_partner_ids","mail_template_id","alerts","extra_edis"]})[0]
    info = {"move_id": move_id, "wizard_id": wiz_id, "before": dict(w)}

    # Build update : si peppol veut, force ['peppol']; sinon ['email']
    target = ["peppol"] if want_peppol else ["email"]
    vals = {}
    # Le checkbox json a la forme {method: {"checked": True, "label": ...}} - on essaie deux variantes
    cb = {x: {"checked": (x in target), "label": x, "readonly": False} for x in ["email","peppol","manual"]}
    vals["sending_method_checkboxes"] = cb
    vals["sending_methods"] = target
    if want_peppol:
        vals["invoice_edi_format"] = "ubl_bis3"
    try:
        call("account.move.send.wizard", "write", [[wiz_id], vals])
    except Exception as e:
        info["write_error"] = str(e)
    # Re-read
    w2 = call("account.move.send.wizard", "read", [[wiz_id]],
              {"fields":["sending_methods","sending_method_checkboxes","invoice_edi_format","mail_partner_ids","mail_template_id","alerts"]})[0]
    info["after_write"] = w2

    # Action
    try:
        call("account.move.send.wizard", "action_send_and_print", [[wiz_id]])
        info["sent"] = True
    except Exception as e:
        info["sent"] = False
        info["send_error"] = str(e)
    # Re-read move state Peppol
    mv = call("account.move", "read", [[move_id]],
              {"fields":["name","state","peppol_is_sent","peppol_move_state","peppol_message_uuid"]})[0]
    info["move_after"] = mv
    return info

# ====== EXECUTION ======
for name in SO_NAMES:
    row = {"so": name, "started": dt.datetime.now().isoformat()}
    s = sos_by_name.get(name)
    if not s:
        row["error"] = "SO not found"; LOG["rows"].append(row); continue
    so_id = s["id"]
    invoice_partner_id = (s.get("partner_invoice_id") or [None])[0]
    row["so_id"] = so_id
    row["invoice_partner_id"] = invoice_partner_id

    # 1) Facturer
    try:
        move_id, err = invoice_so_delivered(so_id)
        row["move_id"] = move_id; row["create_error"] = err
        if not move_id:
            LOG["rows"].append(row); continue
    except Exception as e:
        row["create_error"] = f"create wizard: {e}"
        LOG["rows"].append(row); continue

    # 2) Poster
    try:
        post_move(move_id)
        mv = call("account.move", "read", [[move_id]], {"fields":["name","state","amount_total","amount_untaxed"]})[0]
        row["invoice_name"] = mv["name"]; row["invoice_state"] = mv["state"]
        row["amount_total"] = mv["amount_total"]; row["amount_untaxed"] = mv["amount_untaxed"]
    except Exception as e:
        row["post_error"] = str(e)
        LOG["rows"].append(row); continue

    # 3) Activer Peppol partner si besoin
    if invoice_partner_id:
        try:
            act = ensure_peppol_partner(invoice_partner_id)
            row["peppol_partner"] = {"after": act.get("after"), "changes": act.get("changes"), "ready": act.get("peppol_ready"), "skip": act.get("skip"), "error": act.get("error")}
            if act.get("changes"):
                LOG["peppol_activations"].append({"partner_id": invoice_partner_id, "name": act.get("name"), "changes": act.get("changes")})
        except Exception as e:
            row["peppol_activation_error"] = str(e)

    # 4) Envoyer
    want_peppol = bool(row.get("peppol_partner",{}).get("ready"))
    try:
        si = send_via_wizard(move_id, want_peppol=want_peppol)
        row["send"] = si
    except Exception as e:
        row["send_error"] = str(e)

    LOG["rows"].append(row)
    print(f"[OK] {name} -> {row.get('invoice_name','?')} | total={row.get('amount_total')} | peppol={want_peppol}", flush=True)

LOG["ended"] = dt.datetime.now().isoformat()
with open("compta/scripts/_invoice_log.json","w",encoding="utf-8") as f:
    json.dump(LOG, f, indent=2, default=str)
print("\n=== DONE ===", flush=True)
print(f"Rows: {len(LOG['rows'])} | Peppol activations: {len(LOG['peppol_activations'])}", flush=True)
