"""
Retire la route Manufacture (id=6) de tous les product.template SAUF C0200 (id=10485).
"""
import xmlrpc.client, sys, json, random
URL="https://tea-tree.odoo.com"; DB="tsc-be-tea-tree-main-18515272"
USER="nicolas.raes@teatower.com"; PWD="Teatower123"
common=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid=common.authenticate(DB,USER,PWD,{})
m=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(model, method, args, kw=None):
    return m.execute_kw(DB, uid, PWD, model, method, args, kw or {})

KEEP = 10485  # C0200

# 1) Avant
before = call("product.template","search",[[("route_ids","in",[6])]])
print(f"Templates avec route Manufacture AVANT : {len(before)}")

targets = [t for t in before if t != KEEP]
print(f"Targets à nettoyer (hors {KEEP}) : {len(targets)}")

# 2) Write par chunks de 200
ok, fail = 0, []
for i in range(0, len(targets), 200):
    chunk = targets[i:i+200]
    try:
        call("product.template","write",[chunk, {"route_ids":[(3,6)]}])
        ok += len(chunk)
        print(f"  write OK : {i+len(chunk)}/{len(targets)}")
    except Exception as e:
        print(f"  FAIL chunk {i}: {e}")
        for tid in chunk:
            try:
                call("product.template","write",[[tid], {"route_ids":[(3,6)]}])
                ok += 1
            except Exception as e2:
                fail.append((tid, str(e2)[:120]))

print(f"\nRésultat : {ok} nettoyés, {len(fail)} échecs.")

# 3) Vérif APRÈS
after = call("product.template","search",[[("route_ids","in",[6])]])
print(f"Templates avec route Manufacture APRÈS : {len(after)}")
print(f"IDs restants : {after}")

# 4) Échantillon 5 random parmi targets
sample = random.sample(targets, min(5, len(targets)))
sample_read = call("product.template","read",[sample, ["id","default_code","name","route_ids"]])
print("\nÉchantillon 5 templates nettoyés :")
for r in sample_read:
    has6 = 6 in r["route_ids"]
    print(f"  {r['id']} | {r.get('default_code')} | route6={has6} | routes={r['route_ids']}")

# 5) C0200 check
c0200 = call("product.template","read",[[KEEP],["id","default_code","name","route_ids"]])[0]
print(f"\nC0200 ({KEEP}) : routes={c0200['route_ids']} | route6={6 in c0200['route_ids']}")

# 6) Route 6 active ?
r6 = call("stock.route","read",[[6],["id","name","active"]])[0]
print(f"Route 6 : {r6}")

if fail:
    with open("C:/Users/FlowUP/OneDrive/Teatower/odoo/_route_cleanup_failures.json","w",encoding="utf-8") as f:
        json.dump(fail, f, indent=2)
