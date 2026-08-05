"""
Cree le programme POS Odoo "BNP10" — code partenariat employes BNP, -10% catalogue.

Parite avec le discount Shopify existant (DiscountCodeNode/1823412945235,
"BNP10 - Employes BNP", 10% entire order, all customers, sans date de fin).

Choix encodes :
  - program_type 'promo_code' + rule.mode 'with_code' -> le caissier saisit BNP10
    dans le POS (bouton "Entrer un code"). Meme pattern que le programme #3
    "WATERLOO 10%" deja eprouve en caisse.
  - pos_ok=True / sale_ok=False : le canal en ligne est Shopify, pas Odoo eCommerce.
    sale_ok=False evite qu'un BNP10 atterrisse sur un devis B2B.
  - pos_config_ids = boutiques uniquement, POP-UP STORE (#2) EXCLU
    (config restreinte a 8 produits, cf. Salon Wallon).
  - pas de date_to : parite avec Shopify (code sans expiration).
  - limit_usage=False : usage illimite (code diffuse a tous les employes BNP).

DRY-RUN par defaut. Ecriture reelle :
    python scripts/_promo_bnp10_odoo_pos.py apply

Mot de passe Odoo lu dans la variable d'environnement ODOO_PWD (repo public).
"""
import json
import os
import sys
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ.get("ODOO_PWD")
if not PWD:
    sys.exit("ODOO_PWD absent de l'environnement.")

PROGRAM_NAME = "BNP10 - Employes BNP (-10%)"
CODE = "BNP10"
DATE_FROM = "2026-08-05"
POPUP_CONFIG_ID = 2  # a exclure imperativement

APPLY = len(sys.argv) > 1 and sys.argv[1].lower() == "apply"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


def call(model, method, args, kw=None):
    return models.execute_kw(DB, uid, PWD, model, method, args, kw or {})


print(f"UID={uid} | MODE={'APPLY' if APPLY else 'DRY-RUN'}\n")

# --- 1) Anti-doublon : un code BNP10 existe-t-il deja ? --------------------
clash = call("loyalty.rule", "search_read",
             [[("code", "=ilike", CODE)], ["id", "code", "program_id"]],
             {"context": {"active_test": False}})
if clash:
    print(f"!! Code '{CODE}' deja present en Odoo : {clash} -> abandon (pas de doublon).")
    sys.exit(1)
print(f"OK : aucun code '{CODE}' existant en Odoo.")

# --- 2) POS cibles ---------------------------------------------------------
configs = call("pos.config", "search_read", [[("active", "=", True)], ["id", "name"]])
targets = [c for c in configs if c["id"] != POPUP_CONFIG_ID]
target_ids = sorted(c["id"] for c in targets)
print("\n=== POS CIBLES ===")
for c in sorted(targets, key=lambda x: x["id"]):
    print(f"  #{c['id']} : {c['name']}")
assert POPUP_CONFIG_ID not in target_ids, "POP-UP dans la cible !"

# --- 3) Payload ------------------------------------------------------------
program_vals = {
    "name": PROGRAM_NAME,
    "program_type": "promo_code",
    "applies_on": "current",
    "trigger": "with_code",
    "active": True,
    "date_from": DATE_FROM,
    "pos_ok": True,
    "sale_ok": False,
    "limit_usage": False,
    "pos_config_ids": [(6, 0, target_ids)],
    "rule_ids": [(0, 0, {
        "mode": "with_code",
        "code": CODE,
        "minimum_amount": 0.0,
        "minimum_qty": 1,
        "reward_point_mode": "order",
        "reward_point_amount": 1.0,
    })],
    "reward_ids": [(0, 0, {
        "reward_type": "discount",
        "discount": 10.0,
        "discount_mode": "percent",
        "discount_applicability": "order",
        "required_points": 1.0,
        "description": "BNP10 - 10% employes BNP",
    })],
}
print("\n=== PAYLOAD ===")
print(json.dumps(program_vals, indent=2))

if not APPLY:
    print("\n>>> DRY-RUN : rien ecrit. Relancer avec 'apply'.")
    sys.exit(0)

# --- 4) Creation -----------------------------------------------------------
prog_id = call("loyalty.program", "create", [program_vals])
print(f"\n-> loyalty.program cree : #{prog_id}")

# --- 5) Relecture de controle ---------------------------------------------
prog = call("loyalty.program", "read", [[prog_id],
            ["name", "program_type", "trigger", "applies_on", "active", "date_from",
             "date_to", "pos_ok", "sale_ok", "pos_config_ids", "limit_usage",
             "rule_ids", "reward_ids", "company_id", "currency_id"]])[0]
print("\n=== VERIF PROGRAMME ===")
print(json.dumps(prog, indent=2))
print("=== VERIF RULE ===")
print(json.dumps(call("loyalty.rule", "read", [prog["rule_ids"],
      ["mode", "code", "minimum_amount", "minimum_qty", "reward_point_mode",
       "reward_point_amount"]]), indent=2))
print("=== VERIF REWARD ===")
print(json.dumps(call("loyalty.reward", "read", [prog["reward_ids"],
      ["reward_type", "discount", "discount_mode", "discount_applicability",
       "required_points", "discount_line_product_id"]]), indent=2))
