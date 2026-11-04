"""Urgences televente : rappel le jour ouvre suivant quand le merch n'a pas
trouve le responsable du magasin.

Regle Nicolas 04/11/2026 : « si le client a ete visite aujourd'hui mais le
responsable n'etait pas dispo, alors cree l'urgence dans le planning
televente au lendemain ».

Chaine :
  1. slack_photos_vers_odoo.py (import quotidien 18h, Slack #merchandiser)
     appelle detecter_absence() sur chaque message de visite. Si le
     responsable etait absent, il pose sur la fiche du magasin le tag
        [URGENCE TELEVENTE AAAA-MM-JJ visite AAAA-MM-JJ] <extrait du message>
     (1re date = jour ouvre suivant la visite = jour de l'appel).
  2. CE script lit ces tags dans Odoo (lecture seule) et ecrit
     data/televente_urgences.json (urgences de la fenetre + statut).
  3. build_televente_page.py met les urgences ouvertes EN TETE du jour prevu
     (hors quota DAILY) + un encart en haut du planning.

Cloture automatique d'une urgence :
  - commande confirmee (sale.order sale/done) depuis le jour de la visite ;
  - tag [APPEL AAAA-MM-JJ ...] date >= jour prevu ;
  - note de Vanessa dans le chatter (author 6491) depuis le jour prevu.
Une urgence non traitee reste affichee (badge « en retard ») pendant
FENETRE_JOURS jours puis disparait.

Usage : python scripts/televente_urgences.py [--date AAAA-MM-JJ]
"""
import argparse
import json
import os
import re
import unicodedata
from datetime import date, timedelta
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
OUT_JSON = DATA / "televente_urgences.json"
FENETRE_JOURS = 7          # une urgence non traitee reste visible 7 jours
VANESSA_AUTHOR_ID = 6491   # compte « Teatower team » repris par Vanessa

FERIES_BE = {
    date(2026, 1, 1), date(2026, 4, 6), date(2026, 5, 1), date(2026, 5, 14),
    date(2026, 5, 25), date(2026, 7, 21), date(2026, 8, 15), date(2026, 11, 1),
    date(2026, 11, 11), date(2026, 12, 25),
    date(2027, 1, 1), date(2027, 3, 29), date(2027, 5, 1), date(2027, 5, 6),
    date(2027, 5, 17), date(2027, 7, 21), date(2027, 8, 15), date(2027, 11, 1),
    date(2027, 11, 11), date(2027, 12, 25),
}

URG_RE = re.compile(r"\[URGENCE TELEVENTE (\d{4}-\d{2}-\d{2}) visite (\d{4}-\d{2}-\d{2})\]\s*([^<\[]*)")
APPEL_RE = re.compile(r"\[APPEL\s+(\d{4}-\d{2}-\d{2})", re.IGNORECASE)


# --------------------------------------------------------------- detection
def _norm(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s.lower())).strip()


# « Si Valentin n'est pas la, demander Illana » = consigne, pas une absence.
_CONDITIONNEL = re.compile(r"\b(si|quand|lorsque)\b.{0,60}")
_RESP = (r"(?:responsable|manager|gerant|gerante|chef de rayon|chef|personne de contact|"
         r"patron|patronne|directeur|directrice)")
_ABS = (r"(?:pas (?:la|ici|present|presente|presents|dispo|disponible|sur (?:le )?(?:site|place))"
        r"|n (?:est|etait) pas (?:la|present|presente|dispo|disponible)"
        r"|absent|absente|indisponible|en (?:reunion|formation|conge|vacances|repos))")
_PATTERNS = [
    re.compile(r"\bpas de " + _RESP + r"\b"),                       # pas de responsable sur place
    re.compile(r"\b" + _RESP + r"(?: \w+){0,4}? " + _ABS + r"\b"),   # responsable rayon pas la / en reunion
    re.compile(r"\bpersonne pour (?:me )?(?:valider|decider|prendre|repondre)"),
]
# Personne nommee : « Madame Looz est absente », « Nathalie Warnier pas presente »
_NOMME = re.compile(
    r"\b(?:M(?:r|me|adame|onsieur)\.?\s+[A-ZÉ][\w-]+|[A-ZÉ][a-zéèëï-]+\s+[A-ZÉ][A-Za-zéèëï-]+)\s+"
    r"(?:est\s+)?(?:pas\s+pr[ée]sente?|absente?|n.(?:est|[ée]tait)\s+pas\s+l[àa]|en\s+cong[ée])")
# Contraintes permanentes, pas une absence du jour : « responsable jamais la le jeudi »
_PERMANENT = re.compile(r"\bjamais\b|\btoujours\b")


def detecter_absence(texte):
    """Extrait de la ligne qui signale l'absence du responsable, sinon None."""
    for ligne in (texte or "").split("\n"):
        brut = re.sub(r"<[^>]+>", "", ligne).strip(" /.-*")
        if not brut:
            continue
        n = _CONDITIONNEL.sub(" ", _norm(brut))
        if _PERMANENT.search(n):
            continue
        brut_sans_cond = re.sub(r"\b(?:[Ss]i|[Qq]uand|[Ll]orsque)\b.{0,60}", " ", brut)
        if any(p.search(n) for p in _PATTERNS) or _NOMME.search(brut_sans_cond):
            return brut[:160]
    return None


def jour_ouvre_suivant(d):
    j = d + timedelta(days=1)
    while j.weekday() >= 5 or j in FERIES_BE:
        j += timedelta(days=1)
    return j


def tag_urgence(jour, visite, auteur, extrait):
    """Texte du tag pose dans res.partner.comment (sans balises HTML)."""
    return (f"[URGENCE TELEVENTE {jour:%Y-%m-%d} visite {visite:%Y-%m-%d}] "
            f"responsable absent ({auteur}) : {extrait}")


def deja_posee(comment, visite):
    txt = re.sub(r"<[^>]+>", " ", str(comment or ""))
    return any(m.group(2) == f"{visite:%Y-%m-%d}" for m in URG_RE.finditer(txt))


# --------------------------------------------------------------- collecte
def collecter(call, today):
    """Urgences de la fenetre, avec statut (ouverte / traitee ...)."""
    debut = today - timedelta(days=FENETRE_JOURS)
    parts = call("res.partner", "search_read",
                 [[("comment", "ilike", "URGENCE TELEVENTE")]],
                 {"fields": ["id", "name", "comment", "phone", "mobile", "email",
                             "street", "zip", "city"], "context": {"active_test": False}})
    out = []
    for p in parts:
        txt = re.sub(r"<[^>]+>", " ", str(p["comment"] or ""))
        tags = [(date.fromisoformat(m.group(1)), date.fromisoformat(m.group(2)), m.group(3).strip())
                for m in URG_RE.finditer(txt)]
        tags = [t for t in tags if t[0] >= debut]
        if not tags:
            continue
        jour, visite, extrait = max(tags)          # la plus recente par magasin
        statut = "ouverte"
        so = call("sale.order", "search_read",
                  [["&", ("state", "in", ["sale", "done"]),
                    "|", ("partner_id", "child_of", p["id"]), ("partner_shipping_id", "=", p["id"]),
                    ("date_order", ">=", f"{visite:%Y-%m-%d} 00:00:00")]],
                  {"fields": ["name", "date_order"], "limit": 1, "order": "date_order desc"})
        if so:
            statut = f"traitée — commande {so[0]['name']}"
        elif any(date.fromisoformat(a) >= jour for a in APPEL_RE.findall(txt)):
            statut = "traitée — appel noté"
        elif call("mail.message", "search_count",
                  [[("model", "=", "res.partner"), ("res_id", "=", p["id"]),
                    ("author_id", "=", VANESSA_AUTHOR_ID),
                    ("date", ">=", f"{jour:%Y-%m-%d} 00:00:00")]]):
            statut = "traitée — note Vanessa"

        enfants = call("res.partner", "search_read", [[("parent_id", "=", p["id"])]],
                       {"fields": ["name", "function", "phone", "mobile", "email"]})
        enfants = [c for c in enfants if (c.get("name") or "").strip()]
        enfants.sort(key=lambda c: (
            0 if re.search(r"respons|g[ée]rant|manager|chef|direct", c.get("function") or "", re.I) else 1,
            0 if (c.get("phone") or c.get("mobile")) else 1))
        c = enfants[0] if enfants else {}
        out.append({
            "pid": p["id"], "magasin": p["name"],
            "jour": jour.isoformat(), "visite": visite.isoformat(), "extrait": extrait,
            "statut": statut, "en_retard": statut == "ouverte" and jour < today,
            "contact_name": c.get("name") or "", "contact_function": c.get("function") or "",
            "phone": c.get("phone") or c.get("mobile") or p.get("phone") or p.get("mobile") or "",
            "email": c.get("email") or p.get("email") or "",
            "street": p.get("street") or "", "zip": p.get("zip") or "", "city": p.get("city") or "",
        })
    out.sort(key=lambda u: (u["jour"], u["magasin"]))
    return out


def charger(path=OUT_JSON):
    """Pour build_televente_page.py : liste des urgences (vide si absent)."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8")).get("urgences", [])
    except (OSError, ValueError):
        return []


def main():
    import xmlrpc.client
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", default=date.today().isoformat())
    args = ap.parse_args()
    today = date.fromisoformat(args.date)

    url, db = "https://tea-tree.odoo.com", "tsc-be-tea-tree-main-18515272"
    user, pwd = "nicolas.raes@teatower.com", os.environ["ODOO_PWD"]
    uid = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common").authenticate(db, user, pwd, {})
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

    def call(m, meth, a, k=None):
        return models.execute_kw(db, uid, pwd, m, meth, a, k or {})

    urg = collecter(call, today)
    DATA.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({"generated": today.isoformat(), "urgences": urg},
                                   ensure_ascii=False, indent=1), encoding="utf-8")
    ouvertes = [u for u in urg if u["statut"] == "ouverte"]
    print(f"[+] {len(urg)} urgence(s) sur {FENETRE_JOURS} j, dont {len(ouvertes)} ouverte(s) -> {OUT_JSON.name}")
    for u in urg:
        print(f"   {u['jour']}  {u['magasin'][:40]:40} {u['statut']}"
              f"{'  (EN RETARD)' if u['en_retard'] else ''}")


if __name__ == "__main__":
    main()
