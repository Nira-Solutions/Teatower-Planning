"""translate_chatter_vanessa.py — Chatter Vanessa -> tags [APPEL] (planning televente).

Vanessa loggue ses retours d'appel en texte libre dans le chatter Odoo
(mail.message sur res.partner) sous le compte aurelie.thibaut@teatower.com
= res.users id 9, author_id = partner 6491 "Teatower team".

build_televente_pool.py ne lit QUE les tags [APPEL AAAA-MM-JJ REFUS|NRP] dans
res.partner.comment -> sans traduction, la cadence ne se recale jamais et les
refus reviennent dans la file chaque semaine.

A LANCER AVANT build_televente_pool.py, en scannant depuis la date du DERNIER
tag [APPEL] existant (pas depuis le lundi precedent : on rate les semaines
sautees).

Idempotent : ne re-tague pas si [APPEL <date> <type>] existe deja.

Usage :
    python translate_chatter_vanessa.py [SINCE=YYYY-MM-DD] [--apply]
    (sans --apply : dry-run, affiche ce qui serait ecrit)
"""

import os
import re
import sys
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"
PWD = os.environ.get("ODOO_PWD", "Teatower123")
VANESSA_PARTNER = 6491  # "Teatower team" = compte aurelie.thibaut@teatower.com

# Le compte 6491 sert aussi aux relances de factures et aux reponses clients :
# on ecarte ce bruit. Les notes d'appel sont courtes (< 160 car.) et en majuscules.
NOISE = ["facture", "peppol", "contact cr", "compte bancaire", "bonjour", "solde impay",
         "relev", "partenaire commercial", "unchecked partner", "cordialement",
         "merci pour votre"]
NRP_KW = ["injoign", "injoing", "rappeler", "pas de responsable", "absent", "ferm",
          "pas joignable", "non joignable", "rappel "]
REFUS_KW = ["refus", "decline", "décline", "pas intéress", "non merci"]
CMD_KW = ["commande"]

strip = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()


def main():
    since = next((a for a in sys.argv[1:] if not a.startswith("--")), "2026-07-15")
    apply_ = "--apply" in sys.argv

    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, USER, PWD, {})
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

    msgs = models.execute_kw(DB, uid, PWD, "mail.message", "search_read",
        [[("model", "=", "res.partner"), ("author_id", "=", VANESSA_PARTNER),
          ("date", ">=", since + " 00:00:00")]],
        {"fields": ["date", "res_id", "body"], "order": "date asc"})
    pids = sorted({m["res_id"] for m in msgs})
    pm = {p["id"]: p for p in models.execute_kw(DB, uid, PWD, "res.partner", "read",
          [pids], {"fields": ["name", "comment"]})} if pids else {}

    planned, commandes, skipped = {}, [], []
    for m in msgs:
        body, d, pid = strip(m["body"]), m["date"][:10], m["res_id"]
        low = body.lower()
        if not body or len(body) > 160 or any(n in low for n in NOISE):
            continue
        name = pm.get(pid, {}).get("name", "?")
        # COMMANDE prime : rien a taguer, la SO encodee recale last_order toute seule.
        if any(k in low for k in CMD_KW) and "plateforme" not in low and "refus" not in low:
            commandes.append((d, pid, name, body))
            continue
        if any(k in low for k in REFUS_KW):
            typ = "REFUS"
        elif any(k in low for k in NRP_KW):
            typ = "NRP"
        else:
            skipped.append((d, pid, name, body))
            continue
        planned.setdefault(pid, []).append((d, typ, body))

    writes = []
    for pid, items in sorted(planned.items()):
        comment = pm[pid].get("comment") or ""
        flat = strip(comment)
        new_tags = []
        for d, typ, body in items:
            if re.search(rf"\[APPEL\s+{d}\s+{typ}\]", flat, re.IGNORECASE):
                continue
            ctx = re.sub(r"^(REFUS|INJOIGNABLE|INJOINGABLE|INJOINGIABLE)\s*[=,:\-]?\s*",
                         "", body, flags=re.IGNORECASE).strip()
            tag = f"[APPEL {d} {typ}]"
            if ctx and len(ctx) < 120:
                tag += f" ({ctx} - note Vanessa)"
            new_tags.append(tag)
        if new_tags:
            writes.append((pid, pm[pid]["name"], new_tags, comment + "\n" + "\n".join(new_tags)))

    print(f"[*] {len(msgs)} messages depuis {since} | {len(writes)} fiches a taguer "
          f"| {len(commandes)} COMMANDE | {len(skipped)} non classes\n")
    for pid, name, tags, _ in writes:
        print(f"#{pid} {name}")
        for t in tags:
            print(f"      {t}")
    print("\n-- COMMANDE (pas de tag ; verifier que la SO existe) --")
    for d, pid, name, body in commandes:
        print(f"  {d} #{pid} {name} :: {body[:80]}")
    if skipped:
        print("\n-- NON CLASSES (a verifier a la main) --")
        for d, pid, name, body in skipped:
            print(f"  {d} #{pid} {name} :: {body[:100]}")

    if apply_:
        for pid, name, tags, newcomment in writes:
            models.execute_kw(DB, uid, PWD, "res.partner", "write", [[pid], {"comment": newcomment}])
        print(f"\n[OK] {len(writes)} fiches mises a jour "
              f"({sum(len(w[2]) for w in writes)} tags)")
    else:
        print(f"\n[DRY-RUN] relancer avec --apply pour ecrire")


if __name__ == "__main__":
    main()
