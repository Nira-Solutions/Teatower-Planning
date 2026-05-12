"""Corriger les 3 partners Odoo : remplacer la note d'exclusion par un simple constat de visite."""
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

TARGETS = [(5729, "Debroux"), (3223, "LLN"), (10134, "Chaumont-Gistoux")]

OLD = "[GILLES 12/05/2026 — visite mardi 12/05] Pas besoin de remplir — magasin gère son rayon, pas de visite merchandiser nécessaire à l'avenir. Exclu du planning S21+."
NEW = "[GILLES — visite 12/05/2026] Rayon plein ce jour, pas besoin de remplir. (Visite ordinaire, magasin reste dans le cycle merchandiser normal.)"

for pid, label in TARGETS:
    p = models.execute_kw(DB, uid, PWD, "res.partner", "read", [pid], {"fields": ["name", "comment"]})[0]
    comment = p.get("comment") or ""
    # Remove wrapped <p><strong>OLD</strong></p>
    wrapper = f"<p><strong>{OLD}</strong></p>"
    if wrapper in comment:
        new_comment = comment.replace(wrapper, f"<p><em>{NEW}</em></p>")
        models.execute_kw(DB, uid, PWD, "res.partner", "write", [[pid], {"comment": new_comment}])
        print(f"✓ {label} (#{pid}) — note remplacée (factuel uniquement)")
    elif OLD in comment:
        new_comment = comment.replace(OLD, NEW)
        models.execute_kw(DB, uid, PWD, "res.partner", "write", [[pid], {"comment": new_comment}])
        print(f"✓ {label} (#{pid}) — note remplacée (raw)")
    else:
        print(f"? {label} (#{pid}) — note d'exclusion pas trouvée, comment actuel :\n{comment[:400]}\n---")

print("\nDone.")
