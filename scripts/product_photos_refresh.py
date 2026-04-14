#!/usr/bin/env python3
"""
product-data : refresh image_1920 de tous les product.template actifs selon règles :
- I0xxx / V0xxx -> Teatower_Packaging/ (nouveau pack)
- C0xxx         -> photo coffret
- P0xxx         -> photo accessoire
- D0xxx         -> photo display
- E0xxx / "echantillon" -> photo echantillon ou matière première (Teatower_Images/)

Backup de l'ancienne image dans ir.attachment(name='backup_image_old') avant écrasement.
Batch par 50. Log complet dans output/product_photos_refresh_log.json.
"""
import base64, json, os, re, sys, unicodedata, xmlrpc.client
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK_DIR = ROOT / "Teatower_Packaging"
IMG_DIR  = ROOT / "Teatower_Images"
OUT_DIR  = ROOT / "output"; OUT_DIR.mkdir(exist_ok=True)

URL   = "https://tea-tree.odoo.com"
DB    = "tsc-be-tea-tree-main-18515272"
LOGIN = "nicolas.raes@teatower.com"
PWD   = "Teatower123"

def norm(s):
    s = unicodedata.normalize("NFD", s or "").encode("ascii","ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()

def connect():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(DB, LOGIN, PWD, {})
    if not uid: sys.exit("Auth Odoo KO")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)
    return uid, models

def exe(models, uid, model, method, *args, **kw):
    # Odoo attend kw séparé ; si on passe fields via kw -> OK, sinon via args
    return models.execute_kw(DB, uid, PWD, model, method, list(args), kw or {})

def read(models, uid, model, ids, fields):
    return models.execute_kw(DB, uid, PWD, model, "read", [ids, fields])

def index_photos():
    """Index par premier nombre trouvé dans le nom de fichier (= code produit sans préfixe/legacy id)."""
    packs = {}
    imgs  = {}
    for d, bucket in [(PACK_DIR, packs), (IMG_DIR, imgs)]:
        if not d.exists(): continue
        for f in d.iterdir():
            if not f.is_file(): continue
            m = re.match(r"\s*(\d{3,5})", f.name)
            if not m: continue
            key = m.group(1).zfill(4)
            bucket.setdefault(key, f)
    return packs, imgs

def classify(ref, name):
    r = (ref or "").upper().strip()
    n = norm(name)
    if "echantillon" in n or "sample" in n or r.startswith("E0"):
        return "E0"
    for p in ("I0","V0","C0","P0","D0"):
        if r.startswith(p): return p
    return "OTHER"

def pick_photo(ref, name, kind, packs, imgs):
    """
    Retourne (path|None, reason).
    Matching clé = 4 derniers chiffres de la ref (ex V0257 -> 0257) OU nom.
    """
    r = (ref or "").upper()
    m = re.search(r"(\d{3,5})$", r)
    key = m.group(1).zfill(4) if m else None

    if kind in ("I0","V0"):
        if key and key in packs: return packs[key], "pack-by-ref"
        if key and key in imgs:  return imgs[key],  "img-fallback-by-ref"
        return None, "no-pack-found"
    if kind == "E0":
        if key and key in imgs:  return imgs[key], "matiere-by-ref"
        if key and key in packs: return packs[key], "pack-fallback"
        return None, "no-sample-found"
    if kind == "C0":
        if key and key in imgs: return imgs[key], "coffret-img"
        return None, "no-coffret-photo"
    if kind == "P0":
        if key and key in imgs: return imgs[key], "accessoire-img"
        return None, "no-accessoire-photo"
    if kind == "D0":
        if key and key in imgs: return imgs[key], "display-img"
        return None, "no-display-photo"
    return None, "other-skip"

def main(dry=False, limit=None):
    uid, models = connect()
    packs, imgs = index_photos()
    print(f"[photos] packs={len(packs)}  imgs={len(imgs)}")

    prod_ids = exe(models, uid, "product.template", "search",
                   [("active","=",True),("sale_ok","=",True)])
    if limit: prod_ids = prod_ids[:limit]
    print(f"[odoo] {len(prod_ids)} product.template actifs")

    # lecture en chunks (pas d'image ici — on la relit au moment du backup)
    rows = []
    for i in range(0, len(prod_ids), 200):
        rows += read(models, uid, "product.template", prod_ids[i:i+200],
                     ["id","name","default_code"])

    stats = {"I0":0,"V0":0,"C0":0,"P0":0,"D0":0,"E0":0,"OTHER":0}
    updated, already, manual = [], [], []

    # préparer opérations
    ops = []  # (tmpl_id, ref, name, kind, path, reason, had_img)
    for p in rows:
        kind = classify(p.get("default_code"), p.get("name"))
        stats[kind] += 1
        path, reason = pick_photo(p.get("default_code"), p.get("name"), kind, packs, imgs)
        had_img = None  # relu au moment du backup
        if not path:
            manual.append({"id":p["id"],"ref":p.get("default_code"),"name":p["name"],"kind":kind,"reason":reason})
            continue
        # si photo présente déjà -> on veut quand même la remplacer par la "cohérente"
        # mais si déjà OK (même fichier taille ~) on skip : on ne peut pas comparer sans checksum -> on backup + set
        ops.append((p["id"], p.get("default_code"), p["name"], kind, path, reason, had_img))

    print(f"[plan] ops={len(ops)}  manual={len(manual)}")

    if dry:
        Path(OUT_DIR/"product_photos_plan.json").write_text(
            json.dumps({"stats":stats,"ops":[{"id":o[0],"ref":o[1],"kind":o[3],"file":o[4].name,"reason":o[5]} for o in ops],"manual":manual},
                       indent=2, ensure_ascii=False), encoding="utf-8")
        print("DRY RUN -> output/product_photos_plan.json")
        return

    # exécution par batch 50
    for i in range(0, len(ops), 50):
        batch = ops[i:i+50]
        for tmpl_id, ref, name, kind, path, reason, had_img in batch:
            b64 = base64.b64encode(path.read_bytes()).decode()
            # backup ancienne image si présente
            old = read(models, uid, "product.template",[tmpl_id],["image_1920"])[0].get("image_1920")
            had_img = bool(old)
            if old:
                models.execute_kw(DB, uid, PWD, "ir.attachment","create",[{
                    "name":"backup_image_old",
                    "res_model":"product.template",
                    "res_id":tmpl_id,
                    "type":"binary",
                    "datas":old,
                }])
            models.execute_kw(DB, uid, PWD, "product.template","write",[[tmpl_id],{"image_1920":b64}])
            updated.append({"id":tmpl_id,"ref":ref,"name":name,"kind":kind,"file":path.name,"reason":reason,"backup":had_img})
        print(f"[batch] {i+len(batch)}/{len(ops)} maj")

    log = {"stats":stats,"updated":updated,"already_ok":already,"manual":manual}
    (OUT_DIR/"product_photos_refresh_log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OK. updated={len(updated)}  manual={len(manual)}")

if __name__ == "__main__":
    dry = "--dry" in sys.argv
    lim = None
    for a in sys.argv:
        if a.startswith("--limit="):
            lim = int(a.split("=")[1])
    main(dry=dry, limit=lim)
