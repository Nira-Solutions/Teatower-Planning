# -*- coding: utf-8 -*-
"""Envoi des 4 factures HoneyHoney (CDM de Poyoux Sarts) vers vendor-bills@tea-tree.odoo.com
via mail.mail Odoo — 1 mail par PDF pour garantir 1 brouillon de facture fournisseur par document."""
import xmlrpc.client, base64, os, time

URL = "https://tea-tree.odoo.com"; DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"; PWD = "Teatower123"
common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
m = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

FOLDER = r"C:\Users\FlowUP\OneDrive\Teatower"
FACTURES = [
    ("Facture_HoneyHoney_250100005.pdf", "250100005", "386,18"),
    ("Facture_HoneyHoney_250500002.pdf", "250500002", "330,45"),
    ("Facture_HoneyHoney_251200005.pdf", "251200005", "976,91"),
    ("Facture_HoneyHoney_260200001.pdf", "260200001", "213,18"),
]

for fname, num, montant in FACTURES:
    path = os.path.join(FOLDER, fname)
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    att_id = call("ir.attachment", "create", [{
        "name": fname,
        "datas": b64,
        "mimetype": "application/pdf",
    }])
    mail_id = call("mail.mail", "create", [[{
        "subject": f"Facture fournisseur HoneyHoney {num}",
        "body_html": f"<p>Facture CDM de Poyoux Sarts (HoneyHoney) n° {num} — {montant} € TVAC.</p>",
        "email_to": "vendor-bills@tea-tree.odoo.com",
        "email_from": "nicolas.raes@teatower.com",
        "attachment_ids": [(6, 0, [att_id])],
        "auto_delete": False,
    }]])
    call("mail.mail", "send", [[mail_id] if isinstance(mail_id, int) else mail_id])
    mid = mail_id if isinstance(mail_id, int) else mail_id[0]
    state = call("mail.mail", "read", [[mid]], {"fields": ["state", "failure_reason"]})[0]
    print(f"{fname}: mail #{mid} -> state={state['state']} {state.get('failure_reason') or ''}")
    time.sleep(1)

print("Termine.")
