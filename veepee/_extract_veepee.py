"""Vente privée Veepee : consolide l'inventaire dispo et extrait Odoo (prix, TVA) + Shopify (textes FR/NL, photo)."""
import json, os, re, sys, xmlrpc.client
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from shopify_client import shopify
sys.stdout.reconfigure(encoding="utf-8")

# Inventaire « vente privée » (Google Sheet 16WucS…, Feuille 1 ; Feuille 2 = doublon de la fin)
RAW = """I0257 7 27/12/2027|I0280 5 27/05/2027|I0340 31 27/09/2027|I0483 5 15/10/2027|I0601 12 03/09/2027|I0607 14 01/04/2028|I0608 31 01/04/2028|I0610 9 03/12/2027|I0632 23 01/10/2027|I0635 18 01/04/2028|I0666 60 01/04/2028|I0685 6 13/04/2028|I0685 11 04/02/2028|I070 22 15/06/2027|I0728 16 13/04/2028|I0728 42 13/04/2028|I0737 4 24/08/2027|I0742 41 27/05/2027|I0772 4 03/09/2027|I0775 36 14/01/2028|I0778 11 01/10/2027|I0813 40 16/12/2027|I0816 9 01/08/2027|I0821 51 13/04/2028|I0822 46 08/01/2028|I0822 12 08/01/2028|I0826 39 14/01/2028|I0829 17 01/04/2028|I0834 37 01/10/2027|I0837 29 04/02/2028|I0837 13 04/02/2028|I0843 85 15/01/2027|I0847 48 04/02/2028|I0848 22 22/02/2028|I0866 49 13/04/2028|I0875 12 25/04/2028|I0875 20 25/04/2028|I0879 10 06/11/2027|I0885 13 15/06/2027|I0890 21 04/02/2028|I0897 44 13/04/2028|I0899 42 01/10/2027|I0900 9 25/04/2028|I0900 11 25/04/2028|V0483 13 06/11/2027|V0483 13 06/11/2027|V0601 10 04/02/2028|V0607 27 22/02/2028|V0635 14 01/04/2028|V0664 9 22/02/2028|V0709 31 04/01/2028|V0710 2 04/12/2027|V0742 21 22/02/2028|V0788 8 01/04/2028|V0793 8 18/03/2028|V0822 9 11/02/2028|V0838 15 27/12/2027|V0847 27 01/03/2028|V0870 8 04/02/2028|V0875 5 12/12/2027|V0885 15 22/02/2028|V0889 6 04/01/2028|V0899 12 24/08/2027|V0900 17 13/08/2027|V0905 41 -|C0191 25 -|C0192 95 -|C0193 2 -|C0187 7 -|C0188 59 -|C0185 171 -|C0186 298 -"""

inv = {}
for row in RAW.split("|"):
    ref, q, dlu = row.split()
    ref = ref.upper()
    e = inv.setdefault(ref, {"ref": ref, "qty": 0, "dlus": [], "lignes": 0})
    e["qty"] += int(q); e["lignes"] += 1
    if dlu != "-" and dlu not in e["dlus"]: e["dlus"].append(dlu)

U, D, L, P = "https://tea-tree.odoo.com", "tsc-be-tea-tree-main-18515272", "nicolas.raes@teatower.com", os.environ["ODOO_PWD"]
uid = xmlrpc.client.ServerProxy(U + "/xmlrpc/2/common").authenticate(D, L, P, {})
m = xmlrpc.client.ServerProxy(U + "/xmlrpc/2/object", allow_none=True)
x = lambda *a, **k: m.execute_kw(D, uid, P, *a, k)
taxes = {t["id"]: t["amount"] for t in x("account.tax", "search_read", [[["type_tax_use", "=", "sale"]]], fields=["amount"])}
prods = {p["default_code"]: p for p in x("product.product", "search_read", [[["default_code", "in", list(inv)]]],
         fields=["default_code", "name", "list_price", "taxes_id", "barcode", "qty_available"])}

Q = '''query($q:String!){productVariants(first:5,query:$q){nodes{sku price title
 product{title handle productType featuredImage{url} onlineStoreUrl descriptionHtml
 translations(locale:"nl"){key value}}}}}'''
out = []
for ref, e in inv.items():
    p = prods.get(ref)
    if p:
        rate = sum(taxes.get(t, 0) for t in p["taxes_id"])
        e.update(odoo_name=p["name"], ean=p["barcode"] or "", stock_odoo=p["qty_available"], tva=rate,
                 ht=round(p["list_price"], 4), ttc=round(p["list_price"] * (1 + rate / 100), 2))
    nodes = [n for n in shopify.graphql(Q, {"q": f'sku:"{ref}"'})["productVariants"]["nodes"] if n["sku"] == ref]
    if nodes:
        n = nodes[0]; pr = n["product"]; tr = {t["key"]: t["value"] for t in pr["translations"]}
        e.update(shop_price=n["price"], variant=n["title"], title_fr=pr["title"], title_nl=tr.get("title", ""),
                 body_fr=pr["descriptionHtml"], body_nl=tr.get("body_html", ""), photo=(pr["featuredImage"] or {}).get("url", ""),
                 url=pr["onlineStoreUrl"] or "", ptype=pr["productType"])
    out.append(e)
    print(ref, e["qty"], e.get("odoo_name"), e.get("ttc"), e.get("shop_price"), bool(e.get("body_nl")), bool(e.get("photo")))
Path(__file__).with_name("_veepee_data.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
