"""
Garde-fou du discount Shopify BNP10 : sortir le cheque cadeau du perimetre.

Probleme : BNP10 est configure sur "All products". Le produit "Cheque cadeau"
(gid 9280780370259) en fait partie -> un employe BNP peut acheter une carte
cadeau de 100 EUR pour 90 EUR, puis payer avec cette carte une commande sur
laquelle il applique a nouveau BNP10 => ~19% de remise reelle.

Solution reutilisable (vaut pour toutes les futures promos) :
  1) tag `no-promo` sur le produit a exclure ;
  2) smart collection "Catalogue eligible promo" = TAG NOT_EQUALS no-promo ;
  3) BNP10 cible cette collection au lieu de "All products".

Pour exclure un autre produit plus tard : lui poser le tag `no-promo`, la
collection et donc la promo se mettent a jour toutes seules.

DRY-RUN par defaut. Ecriture reelle :
    python scripts/_promo_bnp10_shopify_guard.py apply
"""
import json
import sys
import time

sys.path.insert(0, __file__.rsplit("\\", 1)[0] if "\\" in __file__ else ".")
from shopify_client import shopify

DISCOUNT_GID = "gid://shopify/DiscountCodeNode/1823412945235"
GIFTCARD_GID = "gid://shopify/Product/9280780370259"
EXCLUDE_TAG = "no-promo"
COLLECTION_TITLE = "Catalogue eligible promo"

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


print(f"MODE={'APPLY' if APPLY else 'DRY-RUN'}\n")

total = gql("{ productsCount { count } }")["productsCount"]["count"]
print(f"Produits au catalogue : {total}")
print(f"Cible : collection = {total - 1} produits (tout sauf le cheque cadeau)\n")

if not APPLY:
    print(">>> DRY-RUN : rien ecrit. Relancer avec 'apply'.")
    sys.exit(0)

# --- 1) tag no-promo sur le cheque cadeau ---------------------------------
gql("""mutation($id: ID!, $tags: [String!]!) {
         tagsAdd(id: $id, tags: $tags) { userErrors { field message } } }""",
    {"id": GIFTCARD_GID, "tags": [EXCLUDE_TAG]})
print(f"-> tag '{EXCLUDE_TAG}' pose sur le cheque cadeau")

# --- 2) smart collection ---------------------------------------------------
existing = gql("""query($q: String!) {
    collections(first: 5, query: $q) { edges { node { id title } } } }""",
               {"q": f"title:'{COLLECTION_TITLE}'"})["collections"]["edges"]
if existing:
    coll_id = existing[0]["node"]["id"]
    print(f"-> collection existante reutilisee : {coll_id}")
else:
    data = gql("""mutation($input: CollectionInput!) {
        collectionCreate(input: $input) {
          collection { id title handle }
          userErrors { field message } } }""",
               {"input": {
                   "title": COLLECTION_TITLE,
                   "descriptionHtml": "Collection technique : perimetre des promotions. "
                                      "Exclut les produits taggues 'no-promo' (cheques cadeaux).",
                   "ruleSet": {
                       "appliedDisjunctively": False,
                       "rules": [{"column": "TAG", "relation": "NOT_EQUALS",
                                  "condition": EXCLUDE_TAG}],
                   },
               }})
    coll_id = data["collectionCreate"]["collection"]["id"]
    print(f"-> collection creee : {coll_id} ({data['collectionCreate']['collection']['handle']})")

# --- 3) attendre le peuplement de la smart collection ----------------------
count = 0
for attempt in range(12):
    time.sleep(3)
    count = gql("""query($id: ID!) { collection(id: $id) { productsCount { count } } }""",
                {"id": coll_id})["collection"]["productsCount"]["count"]
    print(f"   peuplement... {count}/{total - 1}")
    if count >= total - 1:
        break

if count < total - 1:
    sys.exit(f"ABANDON : collection incomplete ({count}), BNP10 laisse sur 'All products'.")

# controle : le cheque cadeau n'y est pas
inside = gql("""query($id: ID!, $p: ID!) {
        collection(id: $id) { hasProduct(id: $p) } }""",
             {"id": coll_id, "p": GIFTCARD_GID})["collection"]["hasProduct"]
assert inside is False, "Le cheque cadeau est encore dans la collection !"
print("-> controle OK : cheque cadeau hors collection")

# --- 4) recadrer BNP10 sur la collection ----------------------------------
gql("""mutation($id: ID!, $d: DiscountCodeBasicInput!) {
        discountCodeBasicUpdate(id: $id, basicCodeDiscount: $d) {
          codeDiscountNode { id }
          userErrors { field message code } } }""",
    {"id": DISCOUNT_GID,
     "d": {"customerGets": {"value": {"percentage": 0.1},
                            "items": {"collections": {"add": [coll_id]}}}}})
print("-> BNP10 recadre sur la collection")

# --- 5) relecture ----------------------------------------------------------
final = gql("""query($id: ID!) { codeDiscountNode(id: $id) { codeDiscount {
      ... on DiscountCodeBasic {
        title status startsAt endsAt summary usageLimit appliesOncePerCustomer
        combinesWith { orderDiscounts productDiscounts shippingDiscounts }
        codes(first:1){edges{node{code}}}
        customerGets { value { ... on DiscountPercentage { percentage } }
          items { __typename
            ... on AllDiscountItems { allItems }
            ... on DiscountCollections { collections(first:5){edges{node{id title}}} } } }
      } } } }""", {"id": DISCOUNT_GID})
print("\n=== VERIF SHOPIFY ===")
print(json.dumps(final, indent=2, ensure_ascii=False))
