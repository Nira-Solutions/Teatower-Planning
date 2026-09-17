# -*- coding: utf-8 -*-
"""Rattrapage #merchandiser du 03 au 17/09/2026 : commentaires COMPLETS + photos.

L'import du soir (`slack_photos_vers_odoo.py`) ne pose qu'un recap d'une ligne
et a rate une partie de la periode :
  - jeton Slack expire du 11 au 13/09 -> tournee Liege du 11/09 sans photos ;
  - les tags [VISITE] poses a la main (scripts du 06, 11 et 16/09) servent de
    verrou d'idempotence -> photos du 07/09, 11/09 et 16/09 jamais importees ;
  - un 2e message le meme jour sur le meme magasin (Angleur 15/09) est ignore ;
  - « DELHAIZE Saint Michel » (Etterbeek, #9461) a ete rattache a Saint-Severin
    (#113445), et le matcher refait la meme erreur pour Saint-Lambert ;
  - les messages SANS photo (Spar Namur, Spar Erezee, Roodebeek) et les
    reponses en fil (Hyper Marche, Spar Namur, Sombreffe) sont ignores.

Ici : pid explicite par message Slack (ts), note interne mail.mt_note avec le
commentaire integral + le fil, photos compressees. Idempotent : une note deja
enrichie (marqueur « Slack #merchandiser · HH:MM ») n'est pas retouchee, une
photo deja attachee (visite_<date>_<fichier>) n'est pas re-envoyee.

Usage : python scripts/slack_merch_commentaires_20260917.py [--apply]
"""
import base64, html, json, os, re, sys, xmlrpc.client
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(__file__))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import slack_photos_vers_odoo as S

APPLY = "--apply" in sys.argv
DEPUIS = datetime(2026, 9, 3, tzinfo=timezone.utc).timestamp()

# ts Slack -> pid Odoo (pid du pool planning, verifie a la main)
PID = {
    "1788420857.405979": 119818,  # Delhaize Ferrieres
    "1788424874.305289": 5878,    # Carrefour Market Remouchamps
    "1788428497.426969": 116869,  # Intermarche Tilff
    "1788433460.507949": 2952,    # AD Delhaize Fernelmont
    "1788437108.538419": 122958,  # Spar Namur (pas de visite : parking)
    "1788437588.270589": 3000,    # Intermarche Jambes
    "1788439400.972549": 3181,    # Pharmacie Haulot-Bauche Assesse
    "1788767724.308749": 9046,    # Hyper Carrefour Jambes
    "1788768454.380379": 113498,  # Delhaize Materne
    "1788770823.218019": 122958,  # Spar Namur (STOP ?)
    "1788771247.443409": 114704,  # Delhaize Salzinnes
    "1788772945.852979": 5755,    # Intermarche Naninne
    "1788774901.002999": 3209,    # Intermarche Assesse
    "1788776014.301389": 7679,    # AD Ciney
    "1788779768.328629": 123302,  # Spar Erezee
    "1788851915.234629": 8689,    # Hyper Carrefour Wavre
    "1788853851.887509": 6821,    # Carrefour Market Waterloo
    "1788855379.303209": 114763,  # Proxy Delhaize Lillois
    "1788857522.890869": 9461,    # Proxy Delhaize St Michel (Etterbeek)
    "1788858849.902239": 5729,    # Delhaize Debroux
    "1788860241.420609": 123997,  # AD Delhaize Roodebeek
    "1788860432.391359": 50967,   # Proxy Delhaize Rixensart
    "1789113157.011459": 115879,  # Intermarche Villers-le-Bouillet
    "1789115683.421299": 125096,  # Hyper Carrefour Herstal
    "1789117883.545179": 5653,    # Delhaize St Lambert
    "1789119107.163329": 5439,    # Delhaize Longdoz
    "1789119858.836629": 5580,    # Delhaize Fragnee
    "1789122119.493979": 2909,    # Delhaize Embourg
    "1789123512.280899": 8169,    # Delhaize Bois-de-Breux
    "1789125791.605329": 119815,  # Delhaize Barchon
    "1789370411.864939": 2924,    # Delhaize Incourt
    "1789371334.767619": 121054,  # AD Delhaize Jodoigne
    "1789373041.206819": 10134,   # Intermarche Chaumont-Gistoux
    "1789373955.387399": 115220,  # Intermarche Wavre
    "1789374819.296609": 3223,    # Delhaize LLN
    "1789376715.059199": 113216,  # Spar LLN
    "1789381387.032539": 3153,    # Intermarche Nivelles
    "1789383506.682229": 7283,    # AD Bouffioulx
    "1789456021.502769": 6999,    # Hyper Carrefour Marche
    "1789458956.714129": 121196,  # Carrefour Market Angleur (09:55)
    "1789465359.164449": 121194,  # Intermarche Liege Cointe
    "1789467045.493219": 121196,  # Carrefour Market Angleur (12:10)
    "1789469137.192049": 3210,    # Intermarche Faimes
    "1789470872.282979": 121874,  # Intermarche Hannut
    "1789547803.199239": 6597,    # Hyper Carrefour Wepion
    "1789632907.499939": 113613,  # Hyper Carrefour Mons
    "1789638317.185819": 5441,    # AD Fosses-la-Ville
    "1789640463.885299": 123297,  # Spar Gembloux
    "1789643421.894909": 5449,    # AD Sombreffe
    "1789647035.586139": 114681,  # Delhaize Bouge
}
PAS_UNE_VISITE = {"1788437108.538419"}   # Spar Namur 03/09 : pas pu se garer

# Consigne de Nicolas en fil Slack (17/09) -> visible dans le planning
REGLES = {5449: "[REGLE: prochain passage — remettre un display neuf (abîmé le 17/09) + gamme de Noël]"}

# Mauvais rattachement de l'import auto du 08/09 : Saint Michel -> Saint-Severin
DEPLACER = {"msg": 2364328, "att": 107742, "de": 113445, "vers": 9461,
            "tag": "[VISITE 2026-09-08 Gilles]"}

token = S.token_depuis_claude() or os.environ.get("SLACK_TOKEN")
URL, DB = S.ODOO_URL, S.ODOO_DB
uid = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/common").authenticate(DB, S.ODOO_USER, S.ODOO_PWD, {})
_m = xmlrpc.client.ServerProxy(URL + "/xmlrpc/2/object")


def call(mo, me, a, k=None):
    return _m.execute_kw(DB, uid, S.ODOO_PWD, mo, me, a, k or {})


def texte_propre(t):
    t = re.sub(r"<@([A-Z0-9]+)>", lambda x: "@" + S.auteur({"user": x.group(1)}, token).split()[0], t or "")
    return t.replace("\xa0", " ")


def corps(m, d, lignes, fil):
    h = [f"<p><b>Visite du {d:%d/%m/%Y}</b> — {html.escape(S.auteur(m, token))} · "
         f"{html.escape(S.issue(m.get('text') or ''))}</p>"]
    if lignes:
        h.append("<p>" + "<br/>".join(html.escape(l) for l in lignes) + "</p>")
    if fil:
        h.append("<p><i>Fil Slack :</i><br/>" + "<br/>".join(
            f"<b>{html.escape(a)}</b> : {html.escape(t)}" for a, t in fil) + "</p>")
    h.append(f"<p style='color:#888;font-size:11px'>Note interne — Slack #merchandiser · {d:%H:%M}</p>")
    return "".join(h)


def main():
    print("MODE :", "APPLY" if APPLY else "DRY-RUN")
    S.verifier_subtype_interne(call)

    # 0. correction Saint Michel
    a = call("ir.attachment", "read", [[DEPLACER["att"]]], {"fields": ["res_id"]})
    if a and a[0]["res_id"] == DEPLACER["de"]:
        print(f"~  deplacement note+photo St Michel #{DEPLACER['de']} -> #{DEPLACER['vers']}")
        if APPLY:
            call("ir.attachment", "write", [[DEPLACER["att"]], {"res_id": DEPLACER["vers"]}])
            call("mail.message", "write", [[DEPLACER["msg"]], {"res_id": DEPLACER["vers"]}])
            cm = call("res.partner", "read", [[DEPLACER["de"]]], {"fields": ["comment"]})[0]["comment"] or ""
            cm2 = re.sub(r"<p>\s*" + re.escape(DEPLACER["tag"]) + r"[^<]*</p>", "", cm)
            if cm2 != cm:
                call("res.partner", "write", [[DEPLACER["de"]], {"comment": cm2}])

    msgs = sorted(S.messages_depuis(token, DEPUIS), key=lambda m: float(m["ts"]))
    n = {"note": 0, "maj": 0, "photos": 0, "tag": 0, "ok": 0}
    for m in msgs:
        pid = PID.get(m["ts"])
        if not pid:
            if (m.get("text") or "").strip():
                print(f"?  ts {m['ts']} non mappe : {m['text'][:50]!r}")
            continue          # doublons de photo sans texte (03/09 14:15, 07/09 12:15)
        d = datetime.fromtimestamp(float(m["ts"]), tz=timezone(timedelta(hours=2)))
        brut = texte_propre(m.get("text"))
        lignes = [l.strip() for l in brut.split("\n")[1:] if l.strip()]
        fil = []
        if m.get("reply_count"):
            for r in S.slack("conversations.replies", token, channel=S.CHANNEL, ts=m["ts"])["messages"][1:]:
                fil.append((S.auteur(r, token), texte_propre(r.get("text"))))
        body = corps(m, d, lignes, fil)
        marqueur = f"Slack #merchandiser · {d:%H:%M}"
        nom = call("res.partner", "read", [[pid]], {"fields": ["name"]})[0]["name"] or ""

        imgs = [f for f in m.get("files", []) if str(f.get("mimetype", "")).startswith("image/")]
        noms = {f"visite_{d:%Y-%m-%d}_{f['name']}": f for f in imgs}
        deja = call("ir.attachment", "search_read", [[("res_model", "=", "res.partner"), ("res_id", "=", pid),
                    ("name", "in", list(noms))]], {"fields": ["id", "name"]}) if noms else []
        manquantes = [k for k in noms if k not in {x["name"] for x in deja}]

        note = None
        if deja:
            r = call("mail.message", "search_read", [[("model", "=", "res.partner"), ("res_id", "=", pid),
                     ("attachment_ids", "in", [x["id"] for x in deja])]], {"fields": ["id", "body"], "limit": 1})
            note = r[0] if r else None
        if not note:
            r = call("mail.message", "search_read", [[("model", "=", "res.partner"), ("res_id", "=", pid),
                     ("body", "ilike", marqueur)]], {"fields": ["id", "body"], "limit": 1})
            note = r[0] if r else None

        etat = []
        if note and marqueur in html.unescape(note["body"] or "") and not manquantes:
            etat.append("deja complet")
            n["ok"] += 1
        elif note:
            etat.append(f"note #{note['id']} enrichie" + (f" +{len(manquantes)} photo(s)" if manquantes else ""))
        else:
            etat.append(f"nouvelle note ({len(manquantes)} photo(s))")

        cm = call("res.partner", "read", [[pid]], {"fields": ["comment"]})[0]["comment"] or ""
        txt = re.sub(r"<[^>]+>", " ", cm)
        tag_manque = (m["ts"] not in PAS_UNE_VISITE and f"[VISITE {d:%Y-%m-%d}" not in txt
                      and f"[TERRAIN {d:%Y-%m-%d}" not in txt)
        regle = REGLES.get(pid) if REGLES.get(pid, "") and REGLES[pid] not in txt else None
        if tag_manque:
            etat.append("+tag VISITE")
        if regle:
            etat.append("+REGLE")
        print(f"{d:%d/%m %H:%M} #{pid:<7} {nom[:34]:34} {' | '.join(etat)}")
        if not APPLY or etat[0] == "deja complet" and not tag_manque and not regle:
            continue

        if etat[0] != "deja complet":
            atts = []
            for k in manquantes:
                small = S.compresser(S.slack_download(noms[k]["url_private_download"], token))
                atts.append(call("ir.attachment", "create", [{
                    "name": k, "datas": base64.b64encode(small).decode(),
                    "res_model": "res.partner", "res_id": pid, "mimetype": "image/jpeg"}]))
                n["photos"] += 1
            if note:
                vals = {"body": body}
                if atts:
                    vals["attachment_ids"] = [(4, a) for a in atts]
                call("mail.message", "write", [[note["id"]], vals])
                n["maj"] += 1
            else:
                # NOTE INTERNE : sans mail.mt_note, Odoo notifie les abonnes (client compris)
                mid = call("res.partner", "message_post", [pid], {
                    "body": body, "attachment_ids": atts,
                    "message_type": "comment", "subtype_xmlid": "mail.mt_note"})
                S.controler_aucun_email(call, mid, pid)
                call("mail.message", "write", [[mid], {"body": body}])
                n["note"] += 1
        if tag_manque or regle:
            ajout = ""
            if tag_manque:
                ajout += f"<p>[VISITE {d:%Y-%m-%d} {S.auteur(m, token)}] {html.escape(S.issue(m.get('text') or ''))}</p>"
                n["tag"] += 1
            if regle:
                ajout += f"<p>{html.escape(regle)}</p>"
            call("res.partner", "write", [[pid], {"comment": cm + ajout}])

    print(f"\n{n['note']} note(s) creee(s) | {n['maj']} enrichie(s) | {n['photos']} photo(s) | "
          f"{n['tag']} tag(s) VISITE | {n['ok']} deja complete(s)")
    if not APPLY:
        print("DRY-RUN — relancer avec --apply.")


if __name__ == "__main__":
    main()
