"""Annoter 3 partners Odoo suite retour Gilles 12/05/2026 : Pas besoin de remplir."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

TARGETS = [
    (5729, "Delhaize Herman Debroux Auderghem"),
    (3223, "Delhaize Louvain-la-Neuve"),
    (10134, "Intermarché Chaumont-Gistoux"),
]

NOTE = "[GILLES 12/05/2026 — visite mardi 12/05] Pas besoin de remplir — magasin gère son rayon, pas de visite merchandiser nécessaire à l'avenir. Exclu du planning S21+."

for pid, label in TARGETS:
    p = models.execute_kw(DB, uid, PWD, "res.partner", "read", [pid], {"fields": ["name", "comment"]})[0]
    current = p.get("comment") or ""
    if NOTE.split(" — ")[0] in current:
        print(f"= {label} (#{pid}) — note déjà présente, skip")
        continue
    new_comment = (current + "\n\n" if current else "") + f"<p><strong>{NOTE}</strong></p>"
    models.execute_kw(DB, uid, PWD, "res.partner", "write", [[pid], {"comment": new_comment}])
    print(f"✓ {label} (#{pid}) — note ajoutée")

print("\nDone.")
