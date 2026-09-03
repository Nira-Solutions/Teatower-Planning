# -*- coding: utf-8 -*-
"""
Envoi Peppol des 2 factures de rattrapage stockage Opalya (Terracotta Beauty #123541).

  INV/2026/04101  31/07/2026  260,15 EUR
  INV/2026/04102  31/08/2026  260,15 EUR

Methode : account.move.send.wizard (create -> action_send_and_print).
account.move.action_send_and_print() SEUL ne declenche pas l'envoi reel :
la facture reste en peppol_move_state='ready' au lieu de passer a 'processing'.
Cf. scripts/facturation_b2b_peppol.py etape 8.

Garde-fou : on force sending_methods = ['peppol'] et on refuse de tirer si le
wizard porte encore 'email' -- aucun mail ne doit partir au client.

    python envoi_peppol_opalya_20260903.py         -> DRY-RUN
    python envoi_peppol_opalya_20260903.py apply   -> envoi
"""
import os
import sys
import xmlrpc.client

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ["ODOO_PWD"]
UID = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common").authenticate(DB, USER, PWD, {})
_m = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")


def call(model, method, args, kw=None):
    return _m.execute_kw(DB, UID, PWD, model, method, args, kw or {})


FACTURES = ["INV/2026/04101", "INV/2026/04102"]
PARTNER = 123541

APPLY = len(sys.argv) > 1 and sys.argv[1] == "apply"
print("MODE :", "APPLY" if APPLY else "DRY-RUN")
print("=" * 92)

p = call("res.partner", "read", [[PARTNER]],
         {"fields": ["name", "peppol_verification_state", "peppol_eas",
                     "peppol_endpoint", "invoice_sending_method", "country_id"]})[0]
print("Client : %s" % p["name"])
print("  peppol_verification_state = %s | EAS %s | endpoint %s | methode %s | pays %s"
      % (p["peppol_verification_state"], p["peppol_eas"], p["peppol_endpoint"],
         p["invoice_sending_method"], (p.get("country_id") or [0, "-"])[1]))
if p["peppol_verification_state"] != "valid":
    sys.exit("ARRET : client non 'valid' -> on ne facture/envoie pas en Peppol")

moves = call("account.move", "search_read", [[["name", "in", FACTURES]]],
             {"fields": ["id", "name", "state", "invoice_date", "amount_total",
                         "peppol_move_state", "peppol_message_uuid"]})
print()
for mv in moves:
    print("-" * 92)
    print("%s  %s  %.2f  state=%s  peppol_move_state=%s"
          % (mv["name"], mv["invoice_date"], mv["amount_total"], mv["state"],
             mv.get("peppol_move_state")))
    if mv["state"] != "posted":
        print("  [SKIP] pas postee")
        continue
    if mv.get("peppol_move_state") in ("processing", "done"):
        print("  [SKIP] deja envoyee (uuid=%s)" % mv.get("peppol_message_uuid"))
        continue
    if not APPLY:
        print("  [DRY] enverrait via account.move.send.wizard, sending_methods=['peppol']")
        continue

    ctx = {"active_model": "account.move", "active_ids": [mv["id"]], "active_id": mv["id"]}
    wiz = call("account.move.send.wizard", "create", [{"move_id": mv["id"]}], {"context": ctx})
    meth = call("account.move.send.wizard", "read", [[wiz]], {"fields": ["sending_methods"]})[0]
    print("  wizard %d : sending_methods par defaut = %s" % (wiz, meth["sending_methods"]))
    if meth["sending_methods"] != ["peppol"]:
        call("account.move.send.wizard", "write", [[wiz], {"sending_methods": ["peppol"]}])
        meth = call("account.move.send.wizard", "read", [[wiz]], {"fields": ["sending_methods"]})[0]
        print("  force  -> sending_methods = %s" % meth["sending_methods"])
    if meth["sending_methods"] != ["peppol"]:
        print("  [ARRET] le wizard porte encore %s : un mail partirait au client"
              % meth["sending_methods"])
        continue
    call("account.move.send.wizard", "action_send_and_print", [[wiz]], {"context": ctx})
    after = call("account.move", "read", [[mv["id"]]],
                 {"fields": ["peppol_move_state", "peppol_message_uuid", "is_move_sent"]})[0]
    if after.get("peppol_move_state") in ("processing", "done", "to_send"):
        print("  [SENT] peppol_move_state=%s uuid=%s"
              % (after["peppol_move_state"], after.get("peppol_message_uuid")))
    else:
        print("  [WARN] peppol_move_state=%s -- envoi NON confirme"
              % after.get("peppol_move_state"))

print("\n" + "=" * 92)
for mv in call("account.move", "search_read", [[["name", "in", FACTURES]]],
               {"fields": ["name", "peppol_move_state", "peppol_message_uuid",
                           "is_move_sent"]}):
    print("  %-16s peppol=%-12s sent=%-5s uuid=%s"
          % (mv["name"], mv.get("peppol_move_state"), mv.get("is_move_sent"),
             mv.get("peppol_message_uuid")))
