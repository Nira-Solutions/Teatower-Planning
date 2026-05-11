"""Brief Stephan PDF — version HTML direct avec largeurs colonnes explicites."""
from xhtml2pdf import pisa
from pathlib import Path

OUT = Path(__file__).parent.parent / "Brief_Stephan_Newsletters_Juin_2026.pdf"

# Total largeur dispo en landscape A4 = 29.7 - 2.4 (marges) = 27.3 cm
# Tous les widths en cm explicites dans les <col>

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@page { size: A4 landscape; margin: 1.2cm 1.2cm 1.5cm 1.2cm;
        @frame footer { -pdf-frame-content: footer_c; bottom: 0.4cm; left: 1.2cm; right: 1.2cm; height: 0.6cm; } }
body { font-family: Helvetica, Arial, sans-serif; font-size: 10pt; line-height: 1.45; color: #222; }
h1 { color: #0c4a30; font-size: 19pt; border-bottom: 2px solid #0c4a30; padding-bottom: 4px; margin: 0 0 6pt 0; }
h2 { color: #0c4a30; font-size: 13pt; margin: 14pt 0 4pt 0; border-bottom: 1px solid #d4a373; padding-bottom: 2px; }
h3 { color: #6b4423; font-size: 11pt; margin: 10pt 0 3pt 0; background: #f4e9d8; padding: 3px 7px; border-left: 3px solid #d4a373; }
p { margin: 3pt 0; }
strong { color: #0c4a30; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0; font-size: 9pt; table-layout: fixed; }
th { background: #0c4a30; color: #fff; padding: 5px 7px; text-align: left; border: 1px solid #0c4a30; font-weight: bold; }
td { padding: 5px 7px; border: 1px solid #ccc; vertical-align: top; word-wrap: break-word; }
tr.alt td { background: #f8f5ef; }
ul { margin: 3pt 0; padding-left: 18px; }
li { margin-bottom: 2pt; }
hr { border: 0; border-top: 1px solid #d4a373; margin: 8pt 0; }
pre { background: #f4e9d8; padding: 8px; border-left: 3px solid #d4a373; font-size: 8.5pt; font-family: 'Courier New', monospace; white-space: pre; }
.tag { font-family: 'Courier New', monospace; font-size: 9pt; background: #f4e9d8; padding: 1px 3px; }
.muted { color: #555; font-style: italic; font-size: 9pt; }
</style></head>
<body>

<h1>Brief Stephan — Newsletters Juin 2026</h1>

<p><strong>À :</strong> Stephan&nbsp;&nbsp;|&nbsp;&nbsp;<strong>De :</strong> Nicolas Raes&nbsp;&nbsp;|&nbsp;&nbsp;<strong>Date :</strong> 11 mai 2026&nbsp;&nbsp;|&nbsp;&nbsp;<strong>Envoi prévu :</strong> mardi 9 juin 2026, 9h00</p>

<hr/>

<h2>Le contexte en 30 secondes</h2>
<p>On démarre une <strong>roadmap B2B sur 12 mois</strong> (juin 2026 → mai 2027) avec un objectif simple : <strong>+200 K€ de CA additionnel</strong> sur la base actuelle de 881 K€. La mécanique : 1 ou 2 campagnes Mailchimp ciblées par mois, segment par segment (Horeca, Revendeur, GMS, Grossiste), avec une offre claire chacune.</p>

<p>Tu pilotes la partie newsletter Mailchimp de bout en bout. Moi je m'occupe des données Odoo (segmentation, tags, tracking). Vanessa pilote la suite : commandes entrantes, application de l'offre, SAV. Jérôme appuie en relance commerciale J+10 sur les comptes prioritaires.</p>

<p><strong>Principe juin :</strong> on cible UNIQUEMENT les clients dormants (qui n'ont pas commandé depuis > 6 mois). On n'envoie PAS aux Horeca actifs — pas de promo à des clients qui commandent déjà = pas de cannibalisation.</p>

<hr/>

<h2>Juin 2026 — 2 campagnes en parallèle</h2>
<table>
<colgroup>
  <col style="width:9.5cm"/>
  <col style="width:2cm"/>
  <col style="width:11.5cm"/>
  <col style="width:2.5cm"/>
</colgroup>
<thead><tr><th>Campagne</th><th>Volume</th><th>Offre</th><th>CA cible</th></tr></thead>
<tbody>
<tr><td><strong>A — Horeca dormant</strong><br/><span class="muted">(sans commande > 6 mois)</span></td>
    <td>11</td>
    <td>3+1 sur boîtes HC25 + relance Jérôme top 5</td>
    <td>+1 K€</td></tr>
<tr class="alt"><td><strong>B — Revendeur dormant</strong><br/><span class="muted">(sans commande > 6 mois)</span></td>
    <td>105</td>
    <td>-10% sur réassort libre ≥ 300€ + relance Jérôme top 20</td>
    <td>+8 K€</td></tr>
<tr><td><strong>TOTAL</strong></td><td><strong>116</strong></td><td></td><td><strong>+9 K€</strong></td></tr>
</tbody>
</table>

<p><strong>Tags Odoo correspondants</strong> (à utiliser pour créer les 2 audiences Mailchimp) :</p>
<ul>
<li>A → <span class="tag">MC-202606-HORECA-DORMANT</span></li>
<li>B → <span class="tag">MC-202606-REVENDEUR-DORMANT</span></li>
</ul>

<hr/>

<h2>Tracking de la conversion (sans code promo)</h2>
<p><strong>On ne demande PAS aux clients de saisir un code.</strong> C'est trop compliqué à suivre côté opérationnel.</p>
<p>À la place, on tracke automatiquement via croisement de listes Odoo :</p>
<ul>
<li>On sait <strong>qui a reçu chaque mailing</strong> (tag Odoo MC-202606-HORECA-DORMANT ou MC-202606-REVENDEUR-DORMANT)</li>
<li>On sait <strong>qui a commandé</strong> (sale.order date_order entre le 9 juin et le 9 juillet)</li>
<li><strong>Croisement</strong> → conversions identifiées automatiquement, sans code à saisir, sans champ à remplir</li>
</ul>
<p><strong>Workflow Vanessa :</strong> elle traite les commandes comme d'habitude. Si l'offre est mentionnée par le client (3+1 ou -10%), elle l'applique sur le devis. Pas de code à saisir, pas de champ supplémentaire.</p>
<p><strong>Reporting J+30 (9 juillet) :</strong> je sors la liste « partners taggés campagne juin qui ont passé commande entre 9 juin et 9 juillet » → liste exhaustive des conversions, CA généré, taux de réactivation.</p>

<hr/>

<h2>Les 2 templates à concevoir</h2>

<h3>Template A — Horeca dormant (11 destinataires)</h3>
<p><strong>Ton :</strong> « Vous nous manquez », retour aux fondamentaux, sincère mais pas larmoyant<br/>
<strong>Objet email proposé :</strong> « Cela fait un moment... 3+1 pour reprendre tranquillement ? »<br/>
<strong>Angle :</strong> On a remarqué qu'on ne s'est plus parlé. Voici une offre pour reprendre contact sans pression.<br/>
<strong>Particularité :</strong> Jérôme va appeler le top 5 de cette liste à J+10 si pas de retour</p>
<p><strong>Contenu obligatoire :</strong></p>
<ul>
<li>Offre : 3 boîtes HC25 achetées = 4ᵉ offerte, 1 réf au choix par tranche de 3</li>
<li>Min 6 boîtes, port offert dès 200 €, valable juin uniquement</li>
<li>Phrase d'accroche : « Nous avons remarqué que cela fait quelques mois que nous ne nous sommes pas parlés... »</li>
<li>CTA simple : « Répondez à cet email pour passer commande, ou appelez Vanessa »</li>
<li>Mention « Jérôme reste à votre disposition pour un échange, n'hésitez pas »</li>
</ul>

<h3>Template B — Revendeur dormant (105 destinataires)</h3>
<p><strong>Ton :</strong> Libre, respectueux, « vous choisissez ce que vous voulez », pas une opé promo classique<br/>
<strong>Objet email proposé :</strong> « Reprenons contact — votre choix, -10% sur toute la gamme 🍵 »<br/>
<strong>Angle :</strong> Pas de SKU forcé, pas de pack imposé. C'est <em>votre</em> réassort, à <em>votre</em> rythme. Juste -10% pour reprendre tranquillement.<br/>
<strong>Particularité :</strong> Jérôme va appeler le top 20 (CA historique ≥ 2 K€) à J+10</p>
<p><strong>Contenu obligatoire :</strong></p>
<ul>
<li>Offre : <strong>-10% sur toute commande ≥ 300 €</strong>, frais de port offerts dès 250 €</li>
<li>1 commande maximum par client, valable juin uniquement</li>
<li>Phrase d'accroche : « Cela fait un moment que nous n'avons plus eu de vos nouvelles. Plutôt que vous proposer un assortiment imposé, nous vous laissons carte blanche... »</li>
<li>CTA simple : « Passez commande via notre catalogue ou contactez Vanessa »</li>
<li>Lien vers le catalogue produits (page Shopify pro)</li>
</ul>

<hr/>

<h2>Calendrier de production</h2>
<table>
<colgroup>
  <col style="width:4cm"/>
  <col style="width:17cm"/>
  <col style="width:4.5cm"/>
</colgroup>
<thead><tr><th>Date</th><th>Échéance</th><th>Qui</th></tr></thead>
<tbody>
<tr><td><strong>11 mai (fait)</strong></td><td>Roadmap validée + tags Odoo posés + CSV généré</td><td>Nicolas</td></tr>
<tr class="alt"><td>15 mai (J-25)</td><td>Brief créatif validé (objets, angles, visuels)</td><td>Stephan + Nicolas</td></tr>
<tr><td>20 mai (J-20)</td><td>Import CSV dans Mailchimp + création des 2 audiences</td><td>Stephan</td></tr>
<tr class="alt"><td>25 mai (J-15)</td><td>Premiers drafts des 2 templates Mailchimp</td><td>Stephan</td></tr>
<tr><td>27 mai (J-13)</td><td>Revue templates + ajustements</td><td>Nicolas</td></tr>
<tr class="alt"><td>2 juin (J-7)</td><td>Envoi de test interne (nicolas, vanessa, stephan, jerome)</td><td>Stephan</td></tr>
<tr><td>3 juin (J-6)</td><td>Brief Jérôme : top 20 Revendeur + top 5 Horeca dormants</td><td>Nicolas</td></tr>
<tr class="alt"><td><strong>9 juin 9h00 (J)</strong></td><td><strong>Envoi des 2 campagnes (par segment)</strong></td><td>Stephan</td></tr>
<tr><td>12 juin (J+3)</td><td>Relance Mailchimp aux non-ouvreurs (objet alternatif)</td><td>Stephan</td></tr>
<tr class="alt"><td>19 juin (J+10)</td><td>Appels relance Jérôme top 20 + top 5</td><td>Jérôme</td></tr>
<tr><td>9 juillet (J+30)</td><td>Reporting CA + ROI campagne via croisement listes Odoo</td><td>Nicolas</td></tr>
</tbody>
</table>

<hr/>

<h2>KPI à tracker</h2>

<h3>Métriques Mailchimp (que tu nous remontes)</h3>
<table>
<colgroup><col style="width:11cm"/><col style="width:14.5cm"/></colgroup>
<thead><tr><th>Métrique</th><th>Cible</th></tr></thead>
<tbody>
<tr><td>Taux d'ouverture moyen sur les 2 campagnes</td><td>≥ 35% (sectoriel B2B premium) — visuel « vous nous manquez » booste l'ouverture</td></tr>
<tr class="alt"><td>Taux de clic moyen</td><td>≥ 8%</td></tr>
<tr><td>Désabonnements</td><td>&lt; 0,5%</td></tr>
<tr class="alt"><td>Bounces</td><td>attendu 5-10 sur 116 destinataires (~5-8%) — base partiellement périmée, c'est normal</td></tr>
</tbody>
</table>

<h3>Métriques business (qu'on calcule via Odoo, automatique)</h3>
<table>
<colgroup><col style="width:14cm"/><col style="width:11.5cm"/></colgroup>
<thead><tr><th>Métrique</th><th>Cible</th></tr></thead>
<tbody>
<tr><td>Commandes générées par les destinataires entre 9 juin et 9 juillet</td><td>16-18</td></tr>
<tr class="alt"><td>CA additionnel</td><td>+9 K€</td></tr>
<tr><td>Réactivations Revendeur dormant</td><td>13-15 sur 105 (~13%)</td></tr>
<tr class="alt"><td>Réactivations Horeca dormant</td><td>3 sur 11 (sur petit volume)</td></tr>
</tbody>
</table>

<hr/>

<h2>Workflow récap (qui fait quoi)</h2>
<pre>NICOLAS  -> segmente Odoo, tag, exporte CSV (email + nom uniquement)
              v
STEPHAN  -> importe CSV Mailchimp, cree 2 audiences, designe 2 templates
              v
              envoie les 2 mailings le 9 juin
              v
CLIENT   -> recoit email, passe commande en mentionnant l'offre (sans code)
              v
VANESSA  -> recoit la commande, applique l'offre sur le devis Odoo
              (3+1 ou -10% selon segment) -- pas de code a saisir
              v
JEROME   -> appelle top 20 Revendeur + top 5 Horeca dormants a J+10
              v
NICOLAS  -> J+30 reporting : croisement automatique listes Odoo
              -> liste conversions, CA, ROI
              -> ajuste la campagne juillet (Collection Glacee) en fonction</pre>

<hr/>

<h2>Points d'attention</h2>
<ol>
<li><strong>Pas de chevauchement :</strong> un même partner = 1 seul tag (dedup déjà faite). Aucun client ne recevra 2 mailings différents.</li>
<li><strong>Bounces probables :</strong> sur 116 dormants, attendre 5-10 bounces (emails obsolètes). Vanessa nettoiera la liste Odoo en parallèle.</li>
<li><strong>Anti-spam :</strong> planifie les 2 envois espacés : 9h00 → Revendeur dormant (105), 9h30 → Horeca dormant (11).</li>
<li><strong>A/B testing :</strong> si Mailchimp Pro le permet, tester 2 objets sur 10-20% de la base Revendeur dormant (105 = campagne principale) — l'objet gagnant part au reste.</li>
<li><strong>Pas d'envoi aux Horeca actifs :</strong> les 178 cafés/restos qui commandent activement ne reçoivent RIEN cette campagne (décision Nicolas : éviter la cannibalisation). Ils restent en base, on les sollicitera plus tard avec une mécanique adaptée.</li>
<li><strong>Limite du tracking sans code :</strong> si un client transfère le mail à un copain qui n'est pas dans la liste, on ne le saura pas. Acceptable car volume marginal sur 116 dormants.</li>
</ol>

<hr/>

<h2>Prochaine étape pour toi</h2>
<ol>
<li>Lis ce brief, dis-moi si l'angle / le ton / le calendrier te conviennent</li>
<li>Si OK, on bloque un point de 30 min cette semaine pour aligner sur les visuels</li>
<li>Tu peux déjà commencer à brainstormer les objets email et les accroches</li>
</ol>

<hr/>

<h2>Fichiers de référence</h2>
<ul>
<li>CSV Mailchimp : <span class="tag">data/mailchimp_juin_2026.csv</span> (112 lignes, sans code promo)</li>
<li>Roadmap complète : <span class="tag">Roadmap_B2B_2026-2027.pdf</span></li>
<li>Proposition offre juin : <span class="tag">Offre_Juin_2026_Proposition.pdf</span></li>
<li>Liste opérationnelle Vanessa : <span class="tag">Liste_Vanessa_Juin_2026.xlsx</span></li>
</ul>

<div id="footer_c" style="text-align:center; font-size:8pt; color:#888;">
Brief Stephan - Newsletters Juin 2026 - Teatower - page <pdf:pagenumber/>/<pdf:pagecount/>
</div>

</body></html>
"""

with open(OUT, "wb") as f:
    result = pisa.CreatePDF(HTML, dest=f, encoding="utf-8")
if result.err:
    print(f"ERREUR : {result.err}")
    raise SystemExit(1)
print(f"PDF genere : {OUT}")
print(f"Taille : {OUT.stat().st_size / 1024:.1f} Ko")
