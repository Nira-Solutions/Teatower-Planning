"""
Shopify Admin API client for Teatower.

Auth: OAuth client_credentials grant (24h token, auto-renewed).
Credentials read from env vars (User scope on Windows):
  SHOPIFY_CLIENT_ID
  SHOPIFY_CLIENT_SECRET
  SHOPIFY_STORE          (e.g. 263f0b-3.myshopify.com)
  SHOPIFY_API_VERSION    (default 2025-01)

Usage:
    from shopify_client import shopify
    shop = shopify.get("shop.json")
    products = shopify.get("products.json", params={"limit": 50})
    shopify.put(f"products/{pid}.json", json={"product": {"id": pid, "title": "..."}})
"""
import json
import os
import time
import urllib.parse
import urllib.request
import urllib.error


class ShopifyClient:
    def __init__(self):
        self.client_id = os.environ.get("SHOPIFY_CLIENT_ID")
        self.client_secret = os.environ.get("SHOPIFY_CLIENT_SECRET")
        self.store = os.environ.get("SHOPIFY_STORE")
        self.api_version = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
        if not all([self.client_id, self.client_secret, self.store]):
            raise RuntimeError(
                "Missing Shopify env vars (SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET / SHOPIFY_STORE)"
            )
        self._token = None
        self._token_expires_at = 0

    def _fetch_token(self):
        url = f"https://{self.store}/admin/oauth/access_token"
        data = urllib.parse.urlencode({
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=30) as r:
            payload = json.loads(r.read())
        self._token = payload["access_token"]
        self._token_expires_at = time.time() + int(payload.get("expires_in", 86400)) - 60
        return self._token

    def _get_token(self):
        if not self._token or time.time() >= self._token_expires_at:
            self._fetch_token()
        return self._token

    def request(self, method, endpoint, params=None, json_body=None, retries=3):
        endpoint = endpoint.lstrip("/")
        url = f"https://{self.store}/admin/api/{self.api_version}/{endpoint}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        body = json.dumps(json_body).encode() if json_body is not None else None
        for attempt in range(retries):
            req = urllib.request.Request(url, data=body, method=method)
            req.add_header("X-Shopify-Access-Token", self._get_token())
            req.add_header("Content-Type", "application/json")
            req.add_header("Accept", "application/json")
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    raw = r.read()
                    return json.loads(raw) if raw else {}
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    time.sleep(2 ** attempt)
                    continue
                if e.code == 401:
                    self._token = None
                    if attempt < retries - 1:
                        continue
                detail = e.read().decode(errors="replace")
                raise RuntimeError(f"Shopify {method} {endpoint} -> {e.code}: {detail}") from e
            except urllib.error.URLError:
                if attempt == retries - 1:
                    raise
                time.sleep(2 ** attempt)

    def get(self, endpoint, params=None):
        return self.request("GET", endpoint, params=params)

    def post(self, endpoint, json_body=None):
        return self.request("POST", endpoint, json_body=json_body)

    def put(self, endpoint, json_body=None):
        return self.request("PUT", endpoint, json_body=json_body)

    def delete(self, endpoint):
        return self.request("DELETE", endpoint)

    def graphql(self, query, variables=None):
        """Admin GraphQL. Leve une RuntimeError si la reponse contient des erreurs —
        l'API GraphQL repond 200 meme quand la requete echoue (droits manquants,
        champ inconnu), un appelant qui ne lit que le code HTTP croirait avoir reussi."""
        body = {"query": query}
        if variables:
            body["variables"] = variables
        r = self.request("POST", "graphql.json", json_body=body)
        if r.get("errors"):
            raise RuntimeError(f"Shopify GraphQL errors: {json.dumps(r['errors'])[:800]}")
        return r.get("data", {})


shopify = ShopifyClient()


if __name__ == "__main__":
    shop = shopify.get("shop.json")["shop"]
    print(f"Shop      : {shop['name']}")
    print(f"Domain    : {shop['domain']}")
    print(f"Plan      : {shop['plan_display_name']}")
    print(f"Currency  : {shop['currency']}")
    print(f"Country   : {shop['country_name']}")
    print(f"Email     : {shop['email']}")

    count = shopify.get("products/count.json")["count"]
    print(f"Products  : {count}")
