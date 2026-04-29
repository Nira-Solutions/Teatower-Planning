"""
Fix 2026-04-29 : ajouter route Manufacture (id=6) sur les templates 1V0
sans route, qui ont une BoM active. Exclut 1V0905 (pas de BoM).

Lancer en dry-run :
    python fix_routes_1V0.py
Pour appliquer :
    python fix_routes_1V0.py --apply
"""
import sys
import xmlrpc.client
import json
from datetime import datetime

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PW = "Teatower123"

MANUFACTURE_ROUTE_ID = 6
APPLY = '--apply' in sys.argv

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
uid = common.authenticate(DB, USER, PW, {})
m = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

def call(model, method, args=None, kwargs=None):
    return m.execute_kw(DB, uid, PW, model, method, args or [], kwargs or {})

print(f"UID = {uid}  | Mode = {'APPLY' if APPLY else 'DRY-RUN'}")

# 1) Tous les templates 1V0
tmpl_ids = call('product.template', 'search', [[('default_code', '=ilike', '1V0%')]])
print(f"Templates 1V0 trouvés : {len(tmpl_ids)}")

tmpls = call('product.template', 'read', [tmpl_ids],
             {'fields': ['id', 'default_code', 'name', 'route_ids', 'active']})

# 2) BoM actives
boms = call('mrp.bom', 'search_read',
            [[('product_tmpl_id', 'in', tmpl_ids), ('active', '=', True)]],
            {'fields': ['id', 'product_tmpl_id', 'type']})
tmpl_with_bom = {b['product_tmpl_id'][0] for b in boms}
print(f"Templates avec BoM active : {len(tmpl_with_bom)}")

# 3) Cible = sans Manufacture, AVEC BoM
to_fix = []
to_skip_no_bom = []
already_ok = []
to_replace_buy = []  # ceux qui ont Buy seul -> on remplace par Manufacture

for t in tmpls:
    rids = t.get('route_ids') or []
    has_bom = t['id'] in tmpl_with_bom
    has_manufacture = MANUFACTURE_ROUTE_ID in rids
    if has_manufacture:
        already_ok.append(t)
        continue
    if not has_bom:
        to_skip_no_bom.append(t)
        continue
    if rids == []:
        to_fix.append(t)
    elif 5 in rids:  # Buy
        to_replace_buy.append(t)
    else:
        # autres cas non prévus
        to_fix.append(t)

print(f"\n[déjà OK Manufacture] {len(already_ok)}")
print(f"[à fixer — sans route, BoM OK] {len(to_fix)}")
for t in to_fix:
    print(f"  tmpl {t['id']} {t['default_code']:10s} {t['name'][:55]}")
print(f"\n[à remplacer Buy -> Manufacture] {len(to_replace_buy)}")
for t in to_replace_buy:
    print(f"  tmpl {t['id']} {t['default_code']:10s} {t['name'][:55]} (routes actuelles={t['route_ids']})")
print(f"\n[skip — sans BoM] {len(to_skip_no_bom)}")
for t in to_skip_no_bom:
    print(f"  tmpl {t['id']} {t['default_code']:10s} {t['name'][:55]} (routes={t['route_ids']})")

if not APPLY:
    print("\nDRY-RUN — Relancer avec --apply pour écrire.")
    sys.exit(0)

# ----- APPLY -----
print(f"\n>>> Application sur {len(to_fix) + len(to_replace_buy)} templates")
ok_fix = ko_fix = 0
errors = []

# Cas 1 : route_ids vide ou autre -> ajouter Manufacture
for t in to_fix:
    try:
        call('product.template', 'write', [[t['id']], {'route_ids': [(4, MANUFACTURE_ROUTE_ID)]}])
        ok_fix += 1
    except Exception as e:
        ko_fix += 1
        errors.append((t['id'], t['default_code'], str(e)[:200]))

# Cas 2 : Buy seul -> remplacer par Manufacture (set explicite)
ok_repl = ko_repl = 0
for t in to_replace_buy:
    try:
        call('product.template', 'write', [[t['id']], {'route_ids': [(6, 0, [MANUFACTURE_ROUTE_ID])]}])
        ok_repl += 1
    except Exception as e:
        ko_repl += 1
        errors.append((t['id'], t['default_code'], str(e)[:200]))

print(f"\nRésultat : ADD Manufacture OK={ok_fix} KO={ko_fix} | REPLACE Buy=>Manufacture OK={ok_repl} KO={ko_repl}")
if errors:
    print("\nErreurs :")
    for e in errors:
        print(f"  {e}")

# Verify
print("\n--- Vérification post-write ---")
all_ids = [t['id'] for t in to_fix + to_replace_buy]
verify = call('product.template', 'read', [all_ids], {'fields': ['id', 'default_code', 'route_ids']})
manufact_ok = sum(1 for t in verify if MANUFACTURE_ROUTE_ID in (t.get('route_ids') or []))
print(f"Templates avec Manufacture après write : {manufact_ok}/{len(all_ids)}")

# Log
log = {
    'datetime': datetime.now().isoformat(),
    'mode': 'APPLY',
    'to_fix_n': len(to_fix),
    'to_replace_buy_n': len(to_replace_buy),
    'to_skip_no_bom_n': len(to_skip_no_bom),
    'already_ok_n': len(already_ok),
    'ok_fix': ok_fix, 'ko_fix': ko_fix,
    'ok_repl': ok_repl, 'ko_repl': ko_repl,
    'errors': errors,
    'verify_manufacture_count': manufact_ok,
    'verify_total': len(all_ids),
}
with open('odoo/_fix_routes_1V0_2026-04-29.json', 'w', encoding='utf-8') as f:
    json.dump(log, f, ensure_ascii=False, indent=2, default=str)
print("[ecrit] odoo/_fix_routes_1V0_2026-04-29.json")
