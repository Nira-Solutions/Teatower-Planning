# Queue semaine du 4 au 8 mai 2026 (S19) — préparation

> Créée le 22/04/2026. Merchandiser : Gilles | Base : Baillonville (5377) | Horaire : 08h30 - 16h30.

## Livraisons merchandiser

| SO | Magasin | Montant | État | Contraintes | Priorité |
|---|---|---|---|---|---|
| **S05457** | **Carrefour Hyper Boncelles** (Seraing 4100) | **426,31 €** | confirmé | Hyper = matin obligatoire (7h-11h30). **Pas le mardi.** | HAUTE — livraison physique par Gilles |
| **S05459** | **Hyper Carrefour Fléron** (Fléron 4620) | **763,70 €** | confirmé | Hyper = matin obligatoire. | HAUTE — livraison physique par Gilles |
| **S05467** | **Carrefour Market Bastogne CC Port** (nouveau GMS — lead #288) | **424,25 €** | **DEVIS — à valider Nicolas** | Gamme infusette + 6 glacés (qty 6 × -30%) + display offert. Implantation en rayon. | HAUTE — livraison + implantation Gilles |

→ Boncelles/Fléron sur zone **Liège-Seraing-Fléron** (lundi 04/05 ou mercredi 06/05, pas mardi). CC Port sur zone **Luxembourg** (mardi 05/05 avec AD Bastogne + Florenville + Bouillon).

## Luxembourg (reportés S18 v3)

- **AD Bastogne** (Tier A) — à replanifier
- **CM Bouillon** — RDV calendar.event #425 à replanifier (encore actif Odoo)
- **Carrefour Florenville** — OVERDUE 85j, **priorité absolue S19**

→ Zone Lux = 1 journée complète dédiée (Bastogne + Florenville + Bouillon faisables ensemble).

## CM Bastogne CC Port (nouveau GMS, devis S05467)

- **Partner Odoo** : #123189 "Carrefour market Bastogne CC Port" (enfant de Carrefour Belgium #6596, type=delivery, ref=0523)
- **Adresse** : Rue Gustave Delperdange 3, 6600 Bastogne | Tel 061 21 00 50 | bastogne@orkari.be
- **SO** : **S05467 DEVIS draft** (424,25 € TTC / 400,21 € HT — à valider Nicolas)
- Lignes (×6 chaque réf -30%) : I0279 Panier grand-maman, I0631 Thé des amoureux, I0880 Blue Earl Grey (alt I0600 Lampe merveilleuse), I0735 Pêche vigne + 6 glacés GI0820/GI0634/GI0735/GI0832/GI0916/GI0912. Display Teatower M0005 ×1 offert (-100%).
- **Facturation** : Carrefour Belgium Corporate Village (modèle intégré, comme Boncelles/Fléron)
- **Lead** : lien opportunity_id=288 fait

**À trancher par Nicolas** :
- [ ] Valider devis S05467 → passer en `sale` pour planification ferme
- [ ] **Rouge printanier** : réf pas trouvée dans le catalogue infusette — à préciser (→ Jérôme ?)
- [ ] **Les 6 glacés** : présélection GI0820/GI0634/GI0735/GI0832/GI0916/GI0912 (cf S05437 Ath) — à confirmer
- [ ] **Demande Carrefour Mme Neuville** (n° 0523) : toi ou Vanessa ? Jérôme attend la réponse (msg lead #288 du 23/04 09:11)

## Reports S18 v3 et v4

- **Delhaize Ottignies** (Tier B, ~21j) — contrainte "pas le jeudi", contact Jolan Cailleu possible
- **CM Hannut (PR Macleky)** — OVERDUE ~110j, contrainte "visite que le jeudi"
- **ITM Hannut** (Intermadis SA) — ~20j, OK demander Mr Christophe Wereau — Tier A avg 1100 €
- **Delhaize Marche** (Tier A, OVERDUE 36j — retiré S18 v4 car S17)

## ⛔ NE PAS VISITER S19 (info Nicolas 23/04)

- **Delhaize Beauraing** (DEMARS SA, partner #2905) — pas besoin de remplir. Contact rayon : Christelle ou Alison.
- **AD Rochefort** (Tier B) — pas besoin de remplir.

## Thés glacés (briefing Nicolas antérieur)

- **AD Delhaize Fosses-la-Ville** (Odoo 5441) — revisite thés glacés prévue S19. Contrainte : mercredi (Leslie présente toute la journée). Jour cible : **mercredi 06/05**.

## Brief d'organisation préliminaire

Zones à couvrir sur 5 jours (vendredi 08/05 = ouvrable) :
- **Lundi 04/05** — Liège/Seraing/Fléron : Hyper Boncelles + Hyper Fléron (livraisons) + visites Liège non faites S18 (ex: Proxy St-Séverin si OVERDUE devient vrai)
- **Mardi 05/05** — Luxembourg : AD Bastogne + **CM Bastogne CC Port (S05467 devis à valider — livraison + implantation)** + Florenville + CM Bouillon (+ Marche en retour si temps ok)
- **Mercredi 06/05** — Namur-Sud : AD Fosses (thés glacés) + autres OVERDUE zone 5xxx (AD Rochefort + Delhaize Beauraing exclus — pas besoin de remplir, info Nicolas 23/04)
- **Jeudi 07/05** — Hainaut ou BW : CM Hannut (jeudi-only) + Delhaize Ottignies (jeudi OK avec Jolan) + autres BW
- **Vendredi 08/05** — à définir selon reliquats

⚠️ **Ne pas revisiter S18 (sauf si vraie OVERDUE justifiée)** : Mons Grands Prés, Ath, Jambes, Fragnée, Cointe, Embourg, Remouchamps, CM Marche, Fernelmont, Uccle Bascule, Boondael, Woluwe, Wavre, Incourt.

## À valider avant génération S19

- [ ] Confirmer que les 2 livraisons Hyper Carrefour peuvent être faites par Gilles en 1 seule tournée (pas de grosses charges > 2 m³).
- [ ] Vérifier si Delhaize Ottignies nécessite mail préalable (Jolan Cailleu).
- [ ] Check statut CRM Bouillon et RDV #425 (replanifier ou annuler).
- [ ] Vérifier stocks thés glacés dispos pour AD Fosses 06/05.
