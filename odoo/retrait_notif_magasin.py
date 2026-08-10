# -*- coding: utf-8 -*-
"""
Notifie le magasin par e-mail quand une commande de retrait arrive dans Odoo.

Depuis que les locations Shopify sont mappees sur les entrepots des magasins
(cf. shopify_map_liege_namur.py), une commande de vente qui atterrit sur LIEGE,
WAT ou NAM EST un retrait en magasin : les commandes expediees partent du
central, le profil de livraison Shopify ne contient que Somme-Leuze. Le critere
de detection est donc simplement l'entrepot, double d'un garde-fou sur
l'origine Shopify.

Ce script pose quatre objets dans Odoo :
  1. un champ `x_retrait_notifie` sur sale.order — garantit qu'un magasin n'est
     prevenu qu'une fois, meme si la commande est modifiee ensuite ;
  2. un parametre systeme par magasin, `teatower.retrait.email.<CODE>` — c'est
     la que se change une adresse, sans toucher au code ;
  3. un modele d'e-mail `mail.template`, modifiable dans l'interface ;
  4. une regle d'automatisation `base.automation` qui declenche l'envoi.

L'envoi est mis en FILE (`force_send=False`) et non emis dans la transaction :
une panne du serveur SMTP ne doit jamais empecher une commande d'arriver.
Un magasin sans adresse renseignee est simplement ignore — rien n'est envoye a
une adresse devinee.

Usage :
  python odoo/retrait_notif_magasin.py                    # audit
  python odoo/retrait_notif_magasin.py --apply
  python odoo/retrait_notif_magasin.py --set LIEGE=magasinliege@teatower.com
  python odoo/retrait_notif_magasin.py --test S12345      # envoi d'essai
  python odoo/retrait_notif_magasin.py --remove           # retire tout
"""
import argparse
import os
import sys
import xmlrpc.client

URL = "https://tea-tree.odoo.com"
DB = "tsc-be-tea-tree-main-18515272"
USER = "nicolas.raes@teatower.com"

ENTREPOTS = {3: "LIEGE", 4: "WAT", 5: "NAM"}
# Seule adresse communiquee a ce jour. Les autres restent vides volontairement :
# une notification de commande contient des donnees client, elle ne part pas a
# une adresse supposee.
EMAILS = {
    "WAT": "magasinwaterloo@teatower.com",
    "LIEGE": "",
    "NAM": "",
}
PARAM = "teatower.retrait.email."
XMLID_TMPL = "__teatower__.mail_template_retrait_magasin"
XMLID_ACTION = "__teatower__.action_notif_retrait_magasin"
XMLID_AUTO = "__teatower__.automation_notif_retrait_magasin"

SUJET = ("Retrait a preparer — {{ object.warehouse_id.name }} — "
         "commande {{ object.shopify_order_number or object.name }}")

CORPS = """
<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#2c2c2c">
  <p style="font-size:16px;margin:0 0 4px"><strong>Nouvelle commande a preparer</strong></p>
  <p style="margin:0 0 18px;color:#7a7a7a">
    Retrait en magasin — <t t-out="object.warehouse_id.name or ''">Magasin</t>
  </p>

  <table style="border-collapse:collapse;margin-bottom:18px">
    <tr><td style="padding:3px 16px 3px 0;color:#7a7a7a">Commande</td>
        <td style="padding:3px 0"><strong t-out="object.name or ''">S00000</strong>
        <t t-if="object.shopify_order_number">
          (Shopify <t t-out="object.shopify_order_number"/>)
        </t></td></tr>
    <tr><td style="padding:3px 16px 3px 0;color:#7a7a7a">Client</td>
        <td style="padding:3px 0"><t t-out="object.partner_id.name or ''">Client</t></td></tr>
    <tr t-if="object.partner_id.phone or object.partner_id.mobile">
        <td style="padding:3px 16px 3px 0;color:#7a7a7a">Telephone</td>
        <td style="padding:3px 0"><t t-out="object.partner_id.phone or object.partner_id.mobile"/></td></tr>
    <tr t-if="object.partner_id.email">
        <td style="padding:3px 16px 3px 0;color:#7a7a7a">E-mail</td>
        <td style="padding:3px 0"><t t-out="object.partner_id.email"/></td></tr>
    <tr><td style="padding:3px 16px 3px 0;color:#7a7a7a">Date</td>
        <td style="padding:3px 0"><t t-out="object.date_order or ''"/></td></tr>
    <tr><td style="padding:3px 16px 3px 0;color:#7a7a7a">Total</td>
        <td style="padding:3px 0"><strong t-out="format_amount(object.amount_total, object.currency_id)"/></td></tr>
  </table>

  <table style="border-collapse:collapse;width:100%;max-width:560px;font-size:13px">
    <tr style="background:#f2f1ec">
      <th style="text-align:left;padding:7px 10px;border-bottom:2px solid #d7dcd5">Article</th>
      <th style="text-align:right;padding:7px 10px;border-bottom:2px solid #d7dcd5">Qte</th>
    </tr>
    <t t-foreach="object.order_line" t-as="l">
      <tr t-if="l.display_type == False">
        <td style="padding:6px 10px;border-bottom:1px solid #e8e5df">
          <t t-out="l.product_id.default_code or ''"/>
          <t t-out="l.product_id.name or ''"/>
        </td>
        <td style="padding:6px 10px;border-bottom:1px solid #e8e5df;text-align:right">
          <t t-out="int(l.product_uom_qty)"/>
        </td>
      </tr>
    </t>
  </table>

  <p style="margin:18px 0 0;color:#7a7a7a;font-size:13px">
    Le client a ete informe que sa commande serait prete sous 24 heures.
    Preparez-la et gardez-la de cote ; le stock est deja deduit de l'entrepot du magasin.
  </p>
</div>
"""

# Contraintes de safe_eval, qui evalue le code des actions serveur :
#  . pas d'import — le module json n'est pas disponible, d'ou un parametre
#    systeme par magasin plutot qu'un seul parametre au format JSON ;
#  . pas d'affectation d'attribut (opcode STORE_ATTR interdit) — il faut donc
#    `order.write({...})` et non `order.x_retrait_notifie = True`.
CODE_ACTION = """
params = env['ir.config_parameter'].sudo()
template = env.ref('%s', raise_if_not_found=False)
for order in records:
    if order.x_retrait_notifie or not template:
        continue
    code = order.warehouse_id.code or ''
    adresse = (params.get_param('%s' + code) or '').strip()
    if not adresse:
        continue
    template.send_mail(
        order.id,
        force_send=False,
        email_values={'email_to': adresse, 'recipient_ids': [(5, 0, 0)]},
    )
    order.write({'x_retrait_notifie': True})
""" % (XMLID_TMPL, PARAM)

DOMAINE = ("[('state','=','sale'),('warehouse_id','in',[3,4,5]),"
           "('shopify_order_id','!=',False),('x_retrait_notifie','=',False)]")


def connect():
    pwd = os.environ.get("ODOO_PWD")
    if not pwd:
        raise SystemExit("Definir ODOO_PWD avant d'executer ce script.")
    uid = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common").authenticate(DB, USER, pwd, {})
    if not uid:
        raise SystemExit("Authentification Odoo refusee.")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

    def call(model, method, args, kw=None):
        return models.execute_kw(DB, uid, pwd, model, method, args, kw or {})

    return call


def ref(call, xmlid, model=None):
    mod, nom = xmlid.split(".", 1)
    r = call("ir.model.data", "search_read", [[("module", "=", mod), ("name", "=", nom)]],
             {"fields": ["res_id", "model"]})
    return r[0]["res_id"] if r else None


def poser_xmlid(call, xmlid, model, res_id):
    mod, nom = xmlid.split(".", 1)
    if not ref(call, xmlid):
        call("ir.model.data", "create", [{"module": mod, "name": nom,
                                          "model": model, "res_id": res_id}])


def audit(call):
    print("Adresses configurees par magasin :")
    params = call("ir.config_parameter", "search_read",
                  [[("key", "like", PARAM)]], {"fields": ["key", "value"]})
    vus = {p["key"].rsplit(".", 1)[-1]: p["value"] for p in params}
    for code in ENTREPOTS.values():
        v = vus.get(code)
        etat = v if v else ("(a renseigner)" if code in vus else "(non configure)")
        print(f"  {code:<7}{etat}")

    champ = call("ir.model.fields", "search_read",
                 [[("model", "=", "sale.order"), ("name", "=", "x_retrait_notifie")]],
                 {"fields": ["id"]})
    print(f"\n  champ x_retrait_notifie : {'present' if champ else 'absent'}")
    print(f"  modele d'e-mail         : {'present' if ref(call, XMLID_TMPL) else 'absent'}")
    aid = ref(call, XMLID_AUTO)
    if aid:
        a = call("base.automation", "read", [[aid]],
                 {"fields": ["name", "active", "trigger", "filter_domain"]})[0]
        print(f"  automatisation          : #{aid} active={a['active']} "
              f"trigger={a['trigger']}")
    else:
        print("  automatisation          : absente")

    n = call("sale.order", "search_count",
             [[("warehouse_id", "in", list(ENTREPOTS)), ("shopify_order_id", "!=", False)]])
    print(f"\n  {n} commandes de retrait deja passees (elles ne seront PAS renotifiees)")


def appliquer(call):
    # 1. champ de tracabilite
    if not call("ir.model.fields", "search_count",
                [[("model", "=", "sale.order"), ("name", "=", "x_retrait_notifie")]]):
        mid = call("ir.model", "search", [[("model", "=", "sale.order")]])[0]
        call("ir.model.fields", "create", [{
            "model_id": mid, "name": "x_retrait_notifie", "ttype": "boolean",
            "field_description": "Magasin notifie (retrait)",
            "state": "manual", "store": True,
        }])
        print("  champ x_retrait_notifie cree")
    else:
        print("  champ x_retrait_notifie deja present")

    # 2. parametres par magasin
    for code, adresse in EMAILS.items():
        cle = PARAM + code
        ex = call("ir.config_parameter", "search", [[("key", "=", cle)]])
        if ex:
            print(f"  parametre {cle} deja present, laisse tel quel")
        else:
            call("ir.config_parameter", "create", [{"key": cle, "value": adresse}])
            print(f"  parametre {cle} = {adresse or '(vide, a renseigner)'}")

    # 3. modele d'e-mail
    tid = ref(call, XMLID_TMPL)
    mid_so = call("ir.model", "search", [[("model", "=", "sale.order")]])[0]
    vals = {"name": "Retrait en magasin — notification du magasin",
            "model_id": mid_so, "subject": SUJET, "body_html": CORPS,
            "auto_delete": False, "use_default_to": False}
    if tid:
        call("mail.template", "write", [[tid], vals])
        print(f"  modele d'e-mail #{tid} mis a jour")
    else:
        tid = call("mail.template", "create", [vals])
        poser_xmlid(call, XMLID_TMPL, "mail.template", tid)
        print(f"  modele d'e-mail #{tid} cree")

    # 4. action serveur + automatisation
    aid = ref(call, XMLID_ACTION)
    av = {"name": "Notifier le magasin du retrait", "model_id": mid_so,
          "state": "code", "code": CODE_ACTION}
    if aid:
        call("ir.actions.server", "write", [[aid], av])
        print(f"  action serveur #{aid} mise a jour")
    else:
        aid = call("ir.actions.server", "create", [av])
        poser_xmlid(call, XMLID_ACTION, "ir.actions.server", aid)
        print(f"  action serveur #{aid} creee")

    bid = ref(call, XMLID_AUTO)
    bv = {"name": "Retrait en magasin : prevenir le magasin", "model_id": mid_so,
          "trigger": "on_create_or_write", "filter_domain": DOMAINE,
          "action_server_ids": [(6, 0, [aid])], "active": True}
    if bid:
        call("base.automation", "write", [[bid], bv])
        print(f"  automatisation #{bid} mise a jour")
    else:
        bid = call("base.automation", "create", [bv])
        poser_xmlid(call, XMLID_AUTO, "base.automation", bid)
        print(f"  automatisation #{bid} creee")

    # Les commandes deja passees sont marquees comme notifiees : on ne renvoie pas
    # douze e-mails sur des retraits deja remis au client.
    anciennes = call("sale.order", "search",
                     [[("warehouse_id", "in", list(ENTREPOTS)),
                       ("x_retrait_notifie", "=", False)]])
    if anciennes:
        call("sale.order", "write", [anciennes, {"x_retrait_notifie": True}])
        print(f"  {len(anciennes)} commandes anterieures marquees comme deja notifiees")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--set", dest="maj", help="CODE=adresse, ex. LIEGE=magasinliege@teatower.com")
    ap.add_argument("--test", help="nom d'une commande a notifier pour essai, ex. S12345")
    ap.add_argument("--remove", action="store_true")
    args = ap.parse_args()

    call = connect()

    if args.maj:
        code, _, adresse = args.maj.partition("=")
        code = code.strip().upper()
        if code not in ENTREPOTS.values():
            raise SystemExit(f"Code inconnu : {code}. Attendu : {list(ENTREPOTS.values())}")
        cle = PARAM + code
        ex = call("ir.config_parameter", "search", [[("key", "=", cle)]])
        if ex:
            call("ir.config_parameter", "write", [ex, {"value": adresse.strip()}])
        else:
            call("ir.config_parameter", "create", [{"key": cle, "value": adresse.strip()}])
        print(f"  {cle} = {adresse.strip() or '(vide)'}")
        audit(call)
        return

    if args.remove:
        bid = ref(call, XMLID_AUTO)
        if bid:
            call("base.automation", "write", [[bid], {"active": False}])
            print(f"  automatisation #{bid} desactivee")
        else:
            print("  aucune automatisation a desactiver")
        return

    if args.test:
        so = call("sale.order", "search_read", [[("name", "=", args.test)]],
                  {"fields": ["id", "name", "warehouse_id", "x_retrait_notifie"]})
        if not so:
            raise SystemExit(f"Commande {args.test} introuvable.")
        so = so[0]
        code = call("stock.warehouse", "read", [[so["warehouse_id"][0]]],
                    {"fields": ["code"]})[0]["code"]
        adresse = call("ir.config_parameter", "get_param", [PARAM + code])
        if not adresse:
            raise SystemExit(f"Aucune adresse configuree pour {code}.")
        tid = ref(call, XMLID_TMPL)
        call("mail.template", "send_mail", [tid, so["id"]],
             {"force_send": True,
              "email_values": {"email_to": adresse, "recipient_ids": [(5, 0, 0)]}})
        print(f"  e-mail d'essai envoye a {adresse} pour {so['name']} ({code})")
        return

    audit(call)
    if not args.apply:
        print("\n  Audit seul. Ajouter --apply pour poser l'automatisation.")
        return
    print()
    appliquer(call)
    print()
    audit(call)
    print("\n  Adresses manquantes : renseigner avec")
    print("    python odoo/retrait_notif_magasin.py --set LIEGE=...")
    print("    python odoo/retrait_notif_magasin.py --set NAM=...")


if __name__ == "__main__":
    sys.exit(main())
