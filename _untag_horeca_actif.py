"""Supprime le tag MC-202606-HORECA-ACTIF (campagne juin = dormants uniquement)."""
import xmlrpc.client, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = "Teatower123"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(m, me, a, k=None): return models.execute_kw(DB, uid, PWD, m, me, a, k or {})

TAG = "MC-202606-HORECA-ACTIF"

ids = call("res.partner.category", "search", [[("name", "=", TAG)]], {"limit": 1})
if not ids:
    print(f"Tag {TAG} non trouve.")
    sys.exit(0)

tag_id = ids[0]
print(f"Tag {TAG} (id={tag_id}) trouve.")

partners = call("res.partner", "search", [[("category_id", "in", [tag_id])]], {})
print(f"  -> {len(partners)} partners actuellement tagges.")

if partners:
    call("res.partner", "write", [partners, {"category_id": [(3, tag_id)]}])
    print(f"  -> {len(partners)} partners untagged.")

call("res.partner.category", "unlink", [[tag_id]])
print(f"Tag {TAG} supprime.")
