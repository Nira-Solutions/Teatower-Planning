"""Build OFFICIAL GMS catalog from Tarifs VRAC + INFU 2026 (Google Drive).
Looks up real EAN13 from Odoo by default_code."""
import xmlrpc.client, sys, io, json, datetime as dt
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- Source: 2 Google Drive Excel (extracted manually from contentSnippet) ---
ROWS = [
    # VRAC ----------------------------------------------------------------
    ("V0628","Oasis du désert - BIO","Vrac","Thé vert parfumé","Menthe crépue",100,True, 9.43,10.00),
    ("V0631","Le thé des amoureux","Vrac","Thé vert parfumé","Fraise - Rose - Lavande",80,False, 9.43,10.00),
    ("V0669","Vert Jasmin","Vrac","Thé vert parfumé","Jasmin",80,False, 9.43,10.00),
    ("V0895","Matcha Japonais","Vrac","Thé vert","Végétal - Umani - Iodé",50,False, 18.87,20.00),
    ("V0907","Matcha fruit de la passion","Vrac","Thé vert parfumé","Fruit de la passion",50,False, 23.58,25.00),
    ("V0910","Matcha Biscuit 50gr","Vrac","Thé vert parfumé","Biscuit",50,False, 23.58,25.00),
    ("V0626","Sencha - BIO","Vrac","Thé vert","Doux - Végétal",100,True, 9.43,10.00),
    ("V0751","I love you","Vrac","Thé vert parfumé","Rose - Mangue - Ananas",80,False, 9.43,10.00),
    ("V0880","Blue Earl Grey - BIO","Vrac","Thé noir parfumé","Bergamote - Bleuet",100,True, 9.43,13.00),
    ("V0600","La lampe merveilleuse","Vrac","Thé noir parfumé","Cerise - Jasmin - Orange",100,False, 9.43,10.00),
    ("V0635","Silhouette","Vrac","Maté parfumé","Menthe poivrée - Citronnelle - Orange",80,False, 9.43,10.00),
    ("V0878","Guarana Boost","Vrac","Maté parfumé","Orange - Guarana - Goji",100,False, 9.43,10.00),
    ("V0205","Etoiles filantes","Vrac","Infusion de rooibos","Cannelle - Anis - Camomille",100,False, 9.43,10.00),
    ("V0735","Pêche de vigne - BIO","Vrac","Infusion de rooibos","Pêche",100,True, 9.43,10.00),
    ("V0121","Lady Dodo","Vrac","Infusion de plantes","Fenouil - Camomille",80,False, 9.43,10.00),
    ("V0723","Namasté - BIO","Vrac","Infusion de plantes","Verveine - Orange - Citron",80,True, 9.43,10.00),
    ("V0279","Le panier de grand maman","Vrac","Infusion de fruits","Fraise - Mûre - Cassis - Framboise",80,False, 9.43,10.00),
    ("V0301","Tisane tropicale","Vrac","Infusion de fruits","Ananas - Pêche - Mangue",100,False, 9.43,10.00),
    ("V0832","La nana de Wépion","Vrac","Infusion de fruits","Fraise - Ananas - Cerise - Papaye",100,False, 9.43,10.00),
    ("V0868","Citron meringué","Vrac","Infusion de fruits","Citron - Ananas",100,False, 9.43,10.00),
    ("V0914","Rouge Printemps - BIO","Vrac","Infusion de fruits","Hibiscus – Cassis – Sureau",80,True, 9.43,10.00),
    # INFUSETTES ---------------------------------------------------------
    ("I0628","Oasis du désert - BIO","Infusettes","Thé vert parfumé","Menthe crépue",40,True, 10.38,11.00),
    ("I0631","Le thé des amoureux","Infusettes","Thé vert parfumé","Fraise - Rose - Lavande",40,False, 10.38,11.00),
    ("I0669","Vert Jasmin","Infusettes","Thé vert parfumé","Jasmin",40,False, 10.38,11.00),
    ("I0626","Sencha - BIO","Infusettes","Thé vert","Doux - Végétal",40,True, 10.38,11.00),
    ("I0751","I love you","Infusettes","Thé vert parfumé","Rose - Mangue - Ananas",40,False, 10.38,11.00),
    ("I0880","Blue Earl Grey - BIO","Infusettes","Thé noir parfumé","Bergamote - Bleuet",40,True, 10.38,11.00),
    ("I0600","La lampe merveilleuse","Infusettes","Thé noir parfumé","Cerise - Jasmin - Orange",40,False, 10.38,11.00),
    ("I0635","Silhouette","Infusettes","Maté parfumé","Menthe poivrée - Citronnelle - Orange",40,False, 10.38,11.00),
    ("I0878","Guarana Boost","Infusettes","Maté parfumé","Orange - Guarana - Goji",40,False, 10.38,11.00),
    ("I0205","Etoiles filantes","Infusettes","Infusion de rooibos","Cannelle - Anis - Camomille",40,False, 10.38,11.00),
    ("I0735","Pêche de vigne - BIO","Infusettes","Infusion de rooibos","Pêche",40,True, 10.38,11.00),
    ("I0121","Lady Dodo","Infusettes","Infusion de plantes","Fenouil - Camomille",40,False, 10.38,11.00),
    ("I0723","Namasté - BIO","Infusettes","Infusion de plantes","Verveine - Orange - Citron",40,True, 10.38,11.00),
    ("I0279","Le panier de grand maman","Infusettes","Infusion de fruits","Fraise - Mûre - Cassis - Framboise",40,False, 10.38,11.00),
    ("I0301","Tisane tropicale","Infusettes","Infusion de fruits","Passion - Pêche",60,False, 10.38,11.00),
    ("I0832","La nana de Wépion","Infusettes","Infusion de fruits","Fraise - Ananas - Cerise - Papaye",60,False, 10.38,11.00),
    ("I0868","Citron Meringué","Infusettes","Infusion de fruits","Citron - Ananas",60,False, 10.38,11.00),
    # INFUSETTES GLACÉES -------------------------------------------------
    ("GI0820","Marrakech Sunset BIO glacé","Grandes infusettes","Glacé - Thé vert parfumé","Menthe - Fleur d'Oranger",40,True, 8.96,9.50),
    ("GI0735","Pêche de vigne BIO glacée","Grandes infusettes","Glacé - Infusion de rooibos","Pêche",60,True, 8.96,9.50),
    ("GI0634","Gourmandise glacée","Grandes infusettes","Glacé - Infusion de fruits","Fruit rouge - Amande - Hibiscus",60,False, 8.96,9.50),
    ("GI0832","La Nana de Wépion glacé","Grandes infusettes","Glacé - Infusion de fruits","Fraise - Ananas - Cerise - Papaye",60,False, 8.96,9.50),
    ("GI0916","Verger d'été","Grandes infusettes","Glacé - Infusion de fruits","Pomme - Poire",60,False, 8.96,9.50),
    ("GI0912","Passion Exotique","Grandes infusettes","Glacé - Infusion de fruits","Mangue - Passion",60,False, 8.96,9.50),
]
print(f"source rows: {len(ROWS)}")

# --- Lookup EAN13 from Odoo ---
URL="https://tea-tree.odoo.com"; DB="tsc-be-tea-tree-main-18515272"
USER="nicolas.raes@teatower.com"; PWD="Teatower123"
common=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid=common.authenticate(DB,USER,PWD,{})
models=xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
def call(m,me,a,k=None): return models.execute_kw(DB,uid,PWD,m,me,a,k or {})

codes=[r[0] for r in ROWS]
prods=call("product.product","search_read",
    [[("default_code","in",codes)]],
    {"fields":["id","default_code","barcode","name","display_name"]})
by_code={p["default_code"]:p for p in prods}
print(f"matched in Odoo: {len(by_code)} / {len(codes)}")
missing=[c for c in codes if c not in by_code]
if missing: print("MISSING in Odoo:", missing)

catalog=[]
for code,name,cond,famille,saveur,grm,bio,prix_ht,pvc_tvac in ROWS:
    p=by_code.get(code) or {}
    catalog.append({
        "code": code,
        "ean": p.get("barcode") or "",
        "name": name,
        "odoo_name": p.get("name") or "",
        "conditionnement": cond,
        "famille": famille,
        "saveur": saveur,
        "grammage_g": grm,
        "bio": bio,
        "prix_ht": prix_ht,
        "pvc_tvac": pvc_tvac,
    })

# Group order: Vrac → Infusettes → Glacées
order={"Vrac":0,"Infusettes":1,"Grandes infusettes":2}
catalog.sort(key=lambda r:(order.get(r["conditionnement"],9), r["famille"], r["code"]))

print(f"\nsans EAN: {sum(1 for c in catalog if not c['ean'])}")
for c in catalog:
    if not c["ean"]:
        print(" - no EAN:", c["code"], c["name"])

import pathlib
out={
    "generated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
    "source": "Tarifs et bon de commande GMS 2026 — VRAC + INFU + INFU GLACÉ (Google Drive)",
    "count": len(catalog),
    "products": catalog,
}
pathlib.Path("gms-catalog/catalog.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print(f"\nwrote gms-catalog/catalog.json ({len(catalog)} products)")
