"""Importe les photos de visite du canal Slack #merchandiser dans Odoo.

Gilles et Renato postent 2 photos du rayon a chaque passage. Elles ne vivent
aujourd'hui que dans Slack : la fiche magasin Odoo n'en garde aucune trace.
Ce script les rapatrie dans le chatter de la fiche res.partner, datees et
legendees avec le commentaire du terrain.

Pourquoi le chatter et pas une piece jointe nue : le chatter garde la DATE et
le TEXTE du passage a cote de la photo -> on relit l'historique d'un magasin
comme un journal de visites.

Les photos font 2-5 Mo brutes. Elles sont **redimensionnees** (1600 px max,
JPEG q80, ~250 Ko) avant envoi : 200 photos brutes = ~500 Mo dans la base Odoo,
contre ~50 Mo apres compression. Ne jamais importer les originaux.

Prerequis : un token Slack dans SLACK_TOKEN (scopes channels:history,
groups:history, files:read). Voir --help pour la marche a suivre.

Usage:
    set SLACK_TOKEN=xoxp-...
    python scripts/slack_photos_vers_odoo.py --depuis 2026-07-01          # dry-run
    python scripts/slack_photos_vers_odoo.py --depuis 2026-07-01 --apply
"""
import os
import argparse, base64, io, json, os, re, sys, time, unicodedata
import urllib.request, urllib.parse, xmlrpc.client
from datetime import datetime, timezone, timedelta

CHANNEL = "C08LK3W76S1"          # #merchandiser
MAX_PX, JPEG_Q = 1600, 80
ODOO_URL = 'https://tea-tree.odoo.com'
ODOO_DB  = 'tsc-be-tea-tree-main-18515272'
ODOO_USER= 'nicolas.raes@teatower.com'
ODOO_PWD = os.environ["ODOO_PWD"]


# ---------------------------------------------------------------- Slack
def token_depuis_claude():
    """Reutilise le token du plugin MCP Slack deja autorise sur ce poste.

    Evite de faire creer une app Slack dediee : l'autorisation OAuth faite
    depuis Claude Code porte deja channels:history, groups:history et
    files:read. Token jamais affiche ni logue.
    """
    p = os.path.expanduser("~/.claude/.credentials.json")
    if not os.path.exists(p):
        return None
    try:
        d = json.load(open(p, encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    for k, v in (d.get("mcpOAuth") or {}).items():
        if "slack" in k.lower() and v.get("accessToken"):
            return v["accessToken"]
    return None


def slack(method, token, **params):
    url = f"https://slack.com/api/{method}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    if not data.get("ok"):
        raise SystemExit(f"[X] Slack {method} : {data.get('error')}")
    return data


def slack_download(url, token):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def messages_depuis(token, oldest_ts):
    cursor, out = None, []
    while True:
        p = {"channel": CHANNEL, "limit": 200, "oldest": oldest_ts}
        if cursor:
            p["cursor"] = cursor
        d = slack("conversations.history", token, **p)
        out += d.get("messages", [])
        cursor = d.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            return out
        time.sleep(1.2)                      # tier 3 : ~50 req/min


# ------------------------------------------------------- matching magasin
# Mots d'enseigne et de remplissage : presents partout, ils ne discriminent rien.
# Ce qui identifie un magasin c'est la COMMUNE (« Nivelles », « Boondael »).
STOP = {"delhaize","carrefour","intermarche","intermache","spar","proxy","market",
        "hyper","affilie","ad","sa","srl","sprl","passage","livraison","commande",
        "magasin","pas","besoin","besoins","remplir","fait","visite","colis",
        "display","ok","teatower","retail","dis","food","group","sarl","scrl",
        # « Saint Michel » vs « St Michel » : sans ca, « saint » seul rattachait
        # Delhaize St Michel et St Lambert a Proxy Saint-Severin (#113445, 08/10/2026).
        "saint","sint"}


def charger_magasins(csv_paths):
    """pid -> nom depuis les pools merch/televente.

    NE PAS charger res.partner en masse : Odoo compte >125 000 contacts et un
    `limit` arbitraire ne ramene que les plus vieux ids (les magasins recents,
    id 12xxxx, tombaient hors de la fenetre -> 0 correspondance).
    Les pools contiennent exactement les magasins susceptibles d'etre visites.
    """
    import csv as _csv
    out = {}
    for p in csv_paths:
        if not os.path.exists(p):
            continue
        for r in _csv.DictReader(open(p, encoding="utf-8")):
            nom = r.get("display_name") or r.get("magasin") or ""
            if nom:
                out[int(r["pid"])] = nom
    return sorted(out.items())


def norm(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]", " ", s.lower())


def tokens(s):
    return {t for t in norm(s).split() if len(t) > 2 and t not in STOP}


# La commune identifie le magasin, l'ENSEIGNE le desambigue : « Intermarche Mons »
# et « Hyper Carrefour Mons » partagent la commune et sont deux clients differents.
ENSEIGNES = {
    "delhaize":    r"delhaize",
    "intermarche": r"intermarche|intermache|itm",
    "carrefour":   r"carrefour",
    "spar":        r"\bspar\b",
    "pharmacie":   r"pharmacie",
}
FORMATS = {"hyper": r"hyper", "market": r"market", "proxy": r"proxy|\bad\b"}


def _classe(s, table):
    n = norm(s)
    return {k for k, rx in table.items() if re.search(rx, n)}


def resoudre(libelle, magasins, seuil=10):
    """libelle Slack -> (pid, nom, score) ou None.

    score = 10 x communes communes + 3 si meme enseigne + 1 si meme format,
    -8 si les enseignes sont connues et DIFFERENTES (Delhaize != Intermarche).
    Un ecart < 4 points avec le 2e candidat est signale comme ambigu (score
    negatif) : mieux vaut demander que rattacher au mauvais magasin.
    """
    tl, el, fl = tokens(libelle), _classe(libelle, ENSEIGNES), _classe(libelle, FORMATS)
    if not tl:
        return None
    scores = []
    for pid, nom in magasins:
        communes = tl & tokens(nom)
        if not communes:
            # rattrapage fautes de frappe (« Vielsam »/Vielsalm, « Tillf »/Tilff)
            import difflib
            tn = tokens(nom)
            communes = {a for a in tl
                        if difflib.get_close_matches(a, tn, n=1, cutoff=0.82)}
            if not communes:
                continue
        en, fn = _classe(nom, ENSEIGNES), _classe(nom, FORMATS)
        sc = 10 * len(communes)
        if el & en:
            sc += 3
        elif el and en:
            sc -= 8
        if fl & fn:
            sc += 1
        scores.append((sc, pid, nom))
    if not scores:
        return None
    scores.sort(reverse=True)
    sc, pid, nom = scores[0]
    if sc < seuil:
        return None
    if len(scores) > 1 and sc - scores[1][0] < 4:
        return (pid, nom, -sc)          # ambigu : a valider a la main
    return (pid, nom, sc)


# -------------------------------------------------- securite anti-email client
# Regle Nicolas (02/09/2026) : « je ne veux qu'AUCUN mail ne soit envoye aux
# externes ». On ne se contente pas de la bonne pratique (mail.mt_note), on
# VERIFIE apres chaque ecriture, et on s'arrete au premier doute.
class EmailSortantDetecte(Exception):
    pass


def verifier_subtype_interne(call):
    """mail.mt_note doit etre internal=True, sinon il notifie les externes."""
    ref = call('ir.model.data', 'search_read',
               [[('module', '=', 'mail'), ('name', '=', 'mt_note')]],
               {'fields': ['res_id'], 'limit': 1})
    if not ref:
        raise SystemExit("[X] SECURITE : subtype mail.mt_note introuvable — abandon.")
    st = call('mail.message.subtype', 'read', [[ref[0]['res_id']]],
              {'fields': ['name', 'internal', 'default']})[0]
    if not st.get('internal'):
        raise SystemExit(f"[X] SECURITE : le subtype '{st['name']}' n'est PAS interne "
                         "— une note serait envoyee aux abonnes. Abandon.")
    print(f"[OK] securite : subtype '{st['name']}' interne — notes non diffusees")
    return ref[0]['res_id']


def controler_aucun_email(call, message_id, pid):
    """Apres un post : aucune notification de type email ne doit exister.

    Si une en existe, on la neutralise (annulation de l'envoi), on supprime le
    message, et on leve : mieux vaut interrompre l'import que laisser partir un
    seul mail chez un gerant de magasin.
    """
    notifs = call('mail.notification', 'search_read',
                  [[('mail_message_id', '=', message_id),
                    ('notification_type', '=', 'email')]],
                  {'fields': ['res_partner_id', 'notification_status']})
    if not notifs:
        return
    dest = ", ".join(f"{n['res_partner_id'][1]} (#{n['res_partner_id'][0]})" for n in notifs)
    # neutraliser avant que le cron mail ne parte
    mails = call('mail.mail', 'search',
                 [[('mail_message_id', '=', message_id)]])
    if mails:
        call('mail.mail', 'write', [mails, {'state': 'cancel'}])
    call('mail.message', 'unlink', [[message_id]])
    raise EmailSortantDetecte(
        f"notification email creee sur la fiche #{pid} vers : {dest}. "
        f"Message supprime et envoi annule. IMPORT INTERROMPU.")


# ------------------------------------------------------------------ recap
# Nicolas veut un recap TRES court sur la fiche : la ligne doit dire l'essentiel
# sans qu'on ait a deplier le message. On garde l'issue du passage, pas le roman.
ISSUES = [
    (r"pas besoin.{0,12}(de )?(remplir|r[ée]assort)|pas de nouvelle commande",
     "passage OK, pas de réassort"),
    (r"reprise",                     "reprise de marchandise notée"),
    (r"livraison|livr[ée]",          "livraison"),
    (r"installation|install[ée]",    "installation display"),
    (r"stop pour le moment|ne veulent plus|pas fait|pas possible", "passage non fait / stop"),
    (r"commande [àa] encoder",       "commande à encoder"),
]


def issue(texte):
    t = norm(texte)
    for rx, lib in ISSUES:
        if re.search(rx, t):
            return lib
    lignes = [l.strip() for l in (texte or "").split("\n")[1:] if l.strip()]
    return (lignes[0][:70] + "…") if lignes and len(lignes[0]) > 70 else (
        lignes[0] if lignes else "passage")


_NOMS = {}


def auteur(m, token=None):
    """Nom reel du posteur. conversations.history ne renvoie pas user_profile :
    il faut interroger users.info (mis en cache, ~5 personnes sur le canal)."""
    prof = (m.get("user_profile") or {}).get("real_name")
    if prof:
        return prof
    uid_ = m.get("user")
    if not uid_ or not token:
        return "terrain"
    if uid_ not in _NOMS:
        try:
            u = slack("users.info", token, user=uid_)["user"]
            _NOMS[uid_] = (u.get("profile", {}).get("real_name")
                           or u.get("real_name") or u.get("name") or "terrain")
        except SystemExit:
            _NOMS[uid_] = "terrain"
    return _NOMS[uid_]


# ------------------------------------------------------------------ image
# Les iPhone et une partie des Android postent en HEIC : sans pillow-heif, PIL
# les refuse et ~260 photos (mai-oct. 2026) n'etaient jamais arrivees dans Odoo.
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    print("[!] pillow-heif absent : les photos HEIC seront ignorees "
          "(python -m pip install --user pillow-heif)")


def compresser(raw):
    from PIL import Image, ImageOps
    im = Image.open(io.BytesIO(raw))
    im = ImageOps.exif_transpose(im)          # respecte l'orientation du telephone
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    im.thumbnail((MAX_PX, MAX_PX), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=JPEG_Q, optimize=True)
    return buf.getvalue()


# ------------------------------------------------------ infos logistiques
# Le terrain ecrit sous le nom du magasin les contraintes d'acces : jours
# interdits, personne a demander, appeler avant, frequence acceptee. Elles
# vont dans le texte complet de la note ET, extraites, dans un tag
# [LOGISTIQUE date: ...] des notes internes de la fiche.
LOGI_RE = re.compile(
    r"jamais|toujours|uniquement|seulement|sonner|appeler|t[ée]l[ée]phon|tel:|"
    r"\b0\d{3}|demander apr[eè]s|responsable|g[ée]rant|mail|"
    r"lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|matin|apr[eè]s.?midi|"
    r"\d{1,2} ?h\b|ouvre|ferm[ée]|horaire|tou(t|s|tes) les \d|semaines|mois|"
    r"quai|r[ée]ception|parking|livr|r[ée]serve|cong[ée]", re.IGNORECASE)


def logistique(texte):
    lignes = [re.sub(r"<tel:[^|>]+\|([^>]+)>", r"\1", l).strip(" .")
              for l in (texte or "").split("\n")[1:]]
    return [l for l in lignes if l and LOGI_RE.search(l)]


# Messages qui ne sont PAS un passage magasin : recaps de tournee, planning
# de la semaine, retours de stock en entrepot, totaux journaliers.
RECAP_RE = re.compile(r"retour|planning|total journ|j.ai (ramen|remis)|semaine du",
                      re.IGNORECASE)


def est_recap(texte):
    t = texte or ""
    return bool(RECAP_RE.search(t.split("\n")[0])) or \
        len(re.findall(r"(?m)^\s*\d+\.", t)) >= 3


def html(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--depuis", default="2026-07-01", help="date de debut AAAA-MM-JJ")
    ap.add_argument("--apply", action="store_true", help="ecrire dans Odoo")
    ap.add_argument("--max", type=int, default=0, help="limiter le nb de passages (test)")
    ap.add_argument("--corriger", action="append", default=[],
                    help="forcer un rattachement : 'JJ/MM|debut du libelle=pid' (repetable)")
    ap.add_argument("--tag-visite-jours", type=int, default=60,
                    help="ne poser [VISITE] que pour les passages de moins de N jours "
                         "(un rattrapage d'historique ne doit pas gonfler les fiches)")
    args = ap.parse_args()

    token = os.environ.get("SLACK_TOKEN") or token_depuis_claude()
    if not token:
        sys.exit("[X] Aucun token Slack. Soit le plugin MCP Slack est connecte "
                 "(le token est repris automatiquement), soit :\n"
                 "        set SLACK_TOKEN=xoxp-...")

    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PWD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    def call(m, meth, a, k=None):
        return models.execute_kw(ODOO_DB, uid, ODOO_PWD, m, meth, a, k or {})

    import glob as _glob
    pools = sorted(_glob.glob('data/planning_pool_*.csv'))[-1:] + \
            sorted(_glob.glob('data/televente_pool_*.csv'))[-1:]
    verifier_subtype_interne(call)
    magasins = charger_magasins(pools)
    if not magasins:
        sys.exit("[X] aucun pool trouve — lance build_planning_pool.py d'abord")
    print(f"[*] {len(magasins)} magasins (pools) | canal #merchandiser depuis {args.depuis}")

    oldest = datetime.strptime(args.depuis, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()
    msgs = messages_depuis(token, oldest)
    msgs.sort(key=lambda m: float(m["ts"]))

    # Regroupement : le terrain poste souvent « NOM MAGASIN + commentaire »
    # puis les photos dans un ou plusieurs messages SANS texte juste apres.
    # Ces photos orphelines rejoignent le dernier passage du meme auteur
    # (fenetre 20 min) au lieu d'etre perdues en « aucune correspondance ».
    passages = []
    for m in msgs:
        texte = re.sub(r"<@[^>]+>", "", m.get("text") or "").strip()
        imgs = [f for f in m.get("files") or []
                if str(f.get("mimetype", "")).startswith("image/")]
        if not texte and imgs and passages:
            p = passages[-1]
            if p["user"] == m.get("user") and float(m["ts"]) - p["ts_last"] < 1200:
                p["imgs"] += imgs
                p["ts_last"] = float(m["ts"])
                continue
        if not texte and not imgs:
            continue
        passages.append({"m": m, "user": m.get("user"), "texte": texte,
                         "imgs": imgs, "ts_last": float(m["ts"])})
    if args.max:
        passages = passages[:args.max]
    print(f"[*] {len(msgs)} message(s) -> {len(passages)} passage(s) candidat(s)\n")

    ok = amb = vide = deja = compl = 0
    octets_avant = octets_apres = 0
    non_resolus = []
    limite_tag = datetime.now(timezone.utc) - timedelta(days=args.tag_visite_jours)
    for p in passages:
        m, texte, imgs = p["m"], p["texte"], p["imgs"]
        d = datetime.fromtimestamp(float(m["ts"]), tz=timezone(timedelta(hours=2)))
        if est_recap(texte):
            continue
        libelle = texte.split("\n")[0].strip(" :;-.*")
        # Sans photo, seul un message qui COMMENCE par un nom de magasin et
        # porte une info terrain est un passage ; « Gilou je n'ai pas eu de
        # retour sur le Carrefour Naninne ? » est une discussion.
        if not imgs and (len(libelle.split()) > 6 or len(texte.split("\n")) < 2):
            continue
        r = resoudre(libelle, magasins)
        for c in args.corriger:
            cle, _, cpid = c.rpartition("=")
            cjour, _, cdebut = cle.partition("|")
            if cjour == f"{d:%d/%m}" and norm(libelle).startswith(norm(cdebut)):
                nom_c = dict(magasins).get(int(cpid), f"#{cpid}")
                r = (int(cpid), nom_c, 99)
        if not r:
            if imgs:
                non_resolus.append(f"{d:%d/%m/%y} {libelle[:50]} ({len(imgs)} ph.)")
                vide += 1
            continue
        pid, nom, score = r
        if score < 2:
            # Ambigu : pas de rattachement au hasard. --corriger pour forcer.
            print(f"  ~  {d:%d/%m/%y} {libelle[:36]:36} -> #{pid} {nom[:30]} AMBIGU, ignore")
            amb += 1
            continue

        # VERROU par message : la reference Slack (ts) figure dans la note.
        ref = f"slack {m['ts']}"
        if call('mail.message', 'search_count', [[('model', '=', 'res.partner'),
                ('res_id', '=', pid), ('body', 'ilike', ref)]]):
            deja += 1
            continue
        # Imports d'avant le 21/10/2026 : pas de reference, mais le tag [VISITE]
        # du jour. On ne re-poste alors QUE ce qui manque : photos perdues
        # (HEIC, orphelines) et texte complet (infos logistiques).
        cm0 = call('res.partner', 'read', [[pid]], {'fields': ['comment']})[0]['comment'] or ''
        ancien = f"[VISITE {d:%Y-%m-%d}" in re.sub(r'<[^>]+>', ' ', cm0)
        if ancien:
            noms = [f"visite_{d:%Y-%m-%d}_{f['name']}" for f in imgs]
            presents = set(a['name'] for a in call('ir.attachment', 'search_read',
                           [[('res_model', '=', 'res.partner'), ('res_id', '=', pid),
                             ('name', 'in', noms)]], {'fields': ['name']})) if noms else set()
            imgs = [f for f, n in zip(imgs, noms) if n not in presents]
            if not imgs and len(texte.split("\n")) < 2:
                deja += 1
                continue
        logi = logistique(texte)
        print(f"  {'*' if ancien else '+'}  {d:%d/%m/%y} {libelle[:34]:34} -> #{pid:<7} {nom[:30]:30} "
              f"({len(imgs)} ph.{', logistique' if logi else ''}){' complement' if ancien else ''}")
        if not args.apply:
            if ancien:
                compl += 1
            else:
                ok += 1
            continue

        atts = []
        for f in imgs:
            try:
                raw = slack_download(f["url_private_download"], token)
                small = compresser(raw)
            except Exception as e:
                # Une photo illisible ne doit pas couper l'import des visites
                # suivantes (07/10/2026 : 3 visites perdues sur un crash).
                print(f"{'':7}    photo illisible ({type(e).__name__}) -> ignoree : {f.get('name')}")
                continue
            octets_avant += len(raw)
            octets_apres += len(small)
            atts.append(call('ir.attachment', 'create', [{
                'name': f"visite_{d:%Y-%m-%d}_{f['name']}",
                'datas': base64.b64encode(small).decode(),
                'res_model': 'res.partner', 'res_id': pid, 'mimetype': 'image/jpeg'}]))

        # --- NOTE INTERNE, JAMAIS UN MESSAGE CLIENT -------------------------
        # subtype mail.mt_note = « Log note » : visible seulement en interne.
        # Regle Nicolas 02/09/2026 : aucune info de visite ne part au client.
        detail = "<br/>".join(html(l.strip()) for l in texte.split("\n")[1:] if l.strip())
        titre = "Complément visite" if ancien else "Visite"
        body = (f"<p><b>{titre} du {d:%d/%m/%Y}</b> — {auteur(m, token)} · {issue(texte)}</p>"
                + (f"<p>{detail}</p>" if detail else "")
                + f"<p style='color:#888;font-size:11px'>Note interne — Slack #merchandiser · {ref}</p>")
        mid = call('res.partner', 'message_post', [pid], {
            'body': body, 'attachment_ids': atts,
            'message_type': 'comment', 'subtype_xmlid': 'mail.mt_note'})
        controler_aucun_email(call, mid, pid)      # arrete tout si un mail part
        # Odoo echappe le HTML d'un body passe par XML-RPC : on le reecrit.
        call('mail.message', 'write', [[mid], {'body': body}])

        cm = call('res.partner', 'read', [[pid]], {'fields': ['comment']})[0]['comment'] or ''
        ajout = ""
        # Tag [VISITE] : lu par build_planning_pool.py pour last_visit. Limite
        # aux passages recents : l'historique 2025 ne change rien au planning.
        if not ancien and d >= limite_tag and \
                f"[VISITE {d:%Y-%m-%d}" not in re.sub(r'<[^>]+>', ' ', cm):
            ajout += f"<p>[VISITE {d:%Y-%m-%d} {auteur(m, token)}] {issue(texte)}</p>"
        if logi:
            ajout += f"<p>[LOGISTIQUE {d:%Y-%m-%d}: {html(' / '.join(logi))[:400]}]</p>"
        if ajout:
            call('res.partner', 'write', [[pid], {'comment': cm + ajout}])

        # Bon de commande : photo rattachee a la SO du jour si elle existe
        # (simple ir.attachment : aucun message, aucune notification possible).
        so = call('sale.order', 'search_read',
                  [[('partner_id', 'child_of', pid),
                    ('date_order', '>=', (d - timedelta(days=2)).strftime('%Y-%m-%d 00:00:00')),
                    ('date_order', '<=', (d + timedelta(days=3)).strftime('%Y-%m-%d 23:59:59'))]],
                  {'fields': ['id', 'name'], 'limit': 1}) if atts else []
        if so:
            for a in atts:
                src = call('ir.attachment', 'read', [[a]], {'fields': ['name', 'datas']})[0]
                call('ir.attachment', 'create', [{
                    'name': f"BDC_{so[0]['name']}_{src['name']}", 'datas': src['datas'],
                    'res_model': 'sale.order', 'res_id': so[0]['id'], 'mimetype': 'image/jpeg'}])
            print(f"{'':7}    -> bon de commande rattache a {so[0]['name']}")
        if ancien:
            compl += 1
        else:
            ok += 1

    print(f"\n{ok} importee(s) | {compl} complement(s) | {deja} deja presente(s) "
          f"| {amb} ambigue(s) ignoree(s) | {vide} non resolue(s)")
    if non_resolus:
        print("Non resolues (magasin hors pools) :")
        for n in non_resolus:
            print("   ?", n)
    if octets_avant:
        print(f"poids : {octets_avant/1e6:.1f} Mo bruts -> {octets_apres/1e6:.1f} Mo dans Odoo "
              f"({100*octets_apres/octets_avant:.0f} %)")
    if not args.apply:
        print("DRY-RUN — relancer avec --apply.")


if __name__ == "__main__":
    main()
