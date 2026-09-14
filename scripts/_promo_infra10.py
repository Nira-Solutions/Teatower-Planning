"""
Cree le code partenariat "INFRA10" — employes Infrabel, -10% catalogue.
Clone de BNP10 (Shopify DiscountCodeNode/1823412945235 + Odoo loyalty.program #51).

Shopify :
  - DiscountCodeBasic 10 %, tous clients, sans date de fin, usage illimite ;
  - cible la smart collection "Catalogue eligible promo" (exclut les produits
    taggues `no-promo`, dont le cheque cadeau) ;
  - combinesWith tout a false (ne se cumule avec aucune autre promo).

Odoo POS :
  - loyalty.program promo_code / rule with_code INFRA10 / reward 10 % order ;
  - memes pos_config_ids et sale_ok que le programme BNP10 #51 (relus en live) ;
  - pas de date_to, limit_usage=False.

DRY-RUN par defaut. Ecriture reelle :
    python scripts/_promo_infra10.py apply

Mot de passe Odoo lu dans ODOO_PWD (repo public).
"""
import json
import os
import sys
import xmlrpc.client

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify_client import shopify

CODE = "INFRA10"
SHOPIFY_TITLE = "INFRA10 — Employés Infrabel"
ODOO_NAME = "INFRA10 - Employes Infrabel (-10%)"
DATE_FROM = "2026-09-14"
STARTS_AT = "2026-09-13T22:00:00Z"  # 14/09 00:00 Bruxelles
COLLECTION_GID = "gid://shopify/Collection/693574893907"  # Catalogue eligible promo
BNP10_PROGRAM_ID = 51

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ.get("ODOO_PWD")
if not PWD:
    sys.exit("ODOO_PWD absent de l'environnement.")

APPLY = len(sys.argv) > 1 and sys.argv[1].lower() == "apply"


def gql(query, variables=None):
    res = shopify.post("graphql.json",
                       json_body={"query": query, "variables": variables or {}})
    if "errors" in res:
        raise RuntimeError(json.dumps(res["errors"], ensure_ascii=False))
    for _, payload in res.get("data", {}).items():
        if isinstance(payload, dict) and payload.get("userErrors"):
            raise RuntimeError(json.dumps(payload["userErrors"], ensure_ascii=False))
    return res["data"]


common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


def call(model, method, args, kw=None):
    return models.execute_kw(DB, uid, PWD, model, method, args, kw or {})


print(f"MODE={'APPLY' if APPLY else 'DRY-RUN'}\n")

# --- 1) Anti-doublon -------------------------------------------------------
if gql("query($c: String!) { codeDiscountNodeByCode(code: $c) { id } }",
       {"c": CODE})["codeDiscountNodeByCode"]:
    sys.exit(f"!! Code '{CODE}' deja present sur Shopify -> abandon.")
clash = call("loyalty.rule", "search_read",
             [[("code", "=ilike", CODE)], ["id", "code", "program_id"]],
             {"context": {"active_test": False}})
if clash:
    sys.exit(f"!! Code '{CODE}' deja present en Odoo : {clash} -> abandon.")
print(f"OK : aucun code '{CODE}' existant (Shopify + Odoo).")

# --- 2) Reference BNP10 en live -------------------------------------------
bnp = call("loyalty.program", "read", [[BNP10_PROGRAM_ID],
           ["name", "pos_config_ids", "sale_ok", "pos_ok"]])[0]
print(f"Reference Odoo : #{bnp['id']} {bnp['name']} | POS {bnp['pos_config_ids']} "
      f"| sale_ok={bnp['sale_ok']}")

# --- 3) Payloads ------------------------------------------------------------
shopify_input = {
    "title": SHOPIFY_TITLE,
    "code": CODE,
    "startsAt": STARTS_AT,
    "endsAt": None,
    "usageLimit": None,
    "appliesOncePerCustomer": False,
    "customerSelection": {"all": True},
    "combinesWith": {"orderDiscounts": False, "productDiscounts": False,
                     "shippingDiscounts": False},
    "customerGets": {"value": {"percentage": 0.1},
                     "items": {"collections": {"add": [COLLECTION_GID]}}},
}
program_vals = {
    "name": ODOO_NAME,
    "program_type": "promo_code",
    "applies_on": "current",
    "trigger": "with_code",
    "active": True,
    "date_from": DATE_FROM,
    "pos_ok": True,
    "sale_ok": bnp["sale_ok"],
    "limit_usage": False,
    "pos_config_ids": [(6, 0, bnp["pos_config_ids"])],
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
        "description": "INFRA10 - 10% employes Infrabel",
    })],
}
print("\n=== SHOPIFY ===")
print(json.dumps(shopify_input, indent=2, ensure_ascii=False))
print("\n=== ODOO ===")
print(json.dumps(program_vals, indent=2))

if not APPLY:
    print("\n>>> DRY-RUN : rien ecrit. Relancer avec 'apply'.")
    sys.exit(0)

# --- 4) Creation Shopify ---------------------------------------------------
data = gql("""mutation($d: DiscountCodeBasicInput!) {
    discountCodeBasicCreate(basicCodeDiscount: $d) {
      codeDiscountNode { id }
      userErrors { field message code } } }""", {"d": shopify_input})
node_id = data["discountCodeBasicCreate"]["codeDiscountNode"]["id"]
print(f"\n-> Shopify discount cree : {node_id}")

# --- 5) Creation Odoo ------------------------------------------------------
prog_id = call("loyalty.program", "create", [program_vals])
print(f"-> loyalty.program cree : #{prog_id}")

# --- 6) Relecture ----------------------------------------------------------
final = gql("""query($id: ID!) { codeDiscountNode(id: $id) { codeDiscount {
      ... on DiscountCodeBasic {
        title status startsAt endsAt usageLimit appliesOncePerCustomer
        combinesWith { orderDiscounts productDiscounts shippingDiscounts }
        codes(first:1){edges{node{code}}}
        customerGets { value { ... on DiscountPercentage { percentage } }
          items { __typename
            ... on DiscountCollections { collections(first:5){edges{node{id title}}} } } }
      } } } }""", {"id": node_id})
print("\n=== VERIF SHOPIFY ===")
print(json.dumps(final, indent=2, ensure_ascii=False))

prog = call("loyalty.program", "read", [[prog_id],
            ["name", "program_type", "trigger", "active", "date_from", "date_to",
             "pos_ok", "sale_ok", "pos_config_ids", "limit_usage", "rule_ids",
             "reward_ids"]])[0]
print("\n=== VERIF ODOO ===")
print(json.dumps(prog, indent=2))
print(json.dumps(call("loyalty.rule", "read", [prog["rule_ids"], ["mode", "code"]]), indent=2))
print(json.dumps(call("loyalty.reward", "read", [prog["reward_ids"],
      ["reward_type", "discount", "discount_mode", "discount_applicability",
       "discount_line_product_id"]]), indent=2))
