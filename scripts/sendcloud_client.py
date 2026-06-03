"""
Sendcloud API client for Teatower.

Auth: HTTP Basic — Public key as username, Secret key as password.
Credentials read from env vars (User scope on Windows):
  SENDCLOUD_PUBLIC_KEY
  SENDCLOUD_SECRET_KEY

Generate a key in Sendcloud panel:
  Settings -> Integrations -> Sendcloud API -> New API key

Usage:
    from sendcloud_client import sendcloud
    me      = sendcloud.get("user")
    parcels = sendcloud.get("parcels", params={"limit": 50})
    methods = sendcloud.get("shipping_methods")

Doc API v2: https://api.sendcloud.dev/docs/sendcloud-public-api/
"""
import base64
import json
import os
import time
import urllib.parse
import urllib.request
import urllib.error

BASE_URL = "https://panel.sendcloud.sc/api/v2"


class SendcloudClient:
    def __init__(self):
        self.public_key = os.environ.get("SENDCLOUD_PUBLIC_KEY")
        self.secret_key = os.environ.get("SENDCLOUD_SECRET_KEY")
        if not all([self.public_key, self.secret_key]):
            raise RuntimeError(
                "Missing Sendcloud env vars (SENDCLOUD_PUBLIC_KEY / SENDCLOUD_SECRET_KEY). "
                "Generate a key in Sendcloud: Settings -> Integrations -> Sendcloud API."
            )
        token = f"{self.public_key}:{self.secret_key}".encode()
        self._auth = "Basic " + base64.b64encode(token).decode()

    def request(self, method, endpoint, params=None, json_body=None, retries=3):
        endpoint = endpoint.lstrip("/")
        url = f"{BASE_URL}/{endpoint}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        body = json.dumps(json_body).encode() if json_body is not None else None
        for attempt in range(retries):
            req = urllib.request.Request(url, data=body, method=method)
            req.add_header("Authorization", self._auth)
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
                detail = e.read().decode(errors="replace")
                raise RuntimeError(f"Sendcloud {method} {endpoint} -> {e.code}: {detail}") from e
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


sendcloud = SendcloudClient()


if __name__ == "__main__":
    me = sendcloud.get("user")["user"]
    print(f"Compte    : {me.get('company_name')}")
    print(f"Username  : {me.get('username')}")
    print(f"Email     : {me.get('email')}")
    print(f"Téléphone : {me.get('telephone')}")

    parcels = sendcloud.get("parcels", params={"limit": 5}).get("parcels", [])
    print(f"\nDerniers colis ({len(parcels)}):")
    for p in parcels:
        status = (p.get("status") or {}).get("message", "?")
        print(f"  #{p['id']} {p.get('name','')} -> {status} [{p.get('tracking_number','')}]")
