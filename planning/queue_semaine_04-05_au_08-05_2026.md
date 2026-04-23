# Queue semaine du 4 au 8 mai 2026 (S19) — préparation

> Créée le 22/04/2026. Merchandiser : Gilles | Base : Baillonville (5377) | Horaire : 08h30 - 16h30.

## Livraisons merchandiser (commandes Nicolas 22/04/2026)

| SO | Magasin | Montant | Contraintes | Priorité |
|---|---|---|---|---|
| **S05457** | **Carrefour Hyper Boncelles** (Seraing 4100) | **426,31 €** | Hyper = matin obligatoire (7h-11h30). **Pas le mardi.** | HAUTE — livraison physique par Gilles (merchandiser) |
| **S05459** | **Hyper Carrefour Fléron** (Fléron 4620) | **763,70 €** | Hyper = matin obligatoire. | HAUTE — livraison physique par Gilles (merchandiser) |

→ Les deux sur la zone **Liège-Seraing-Fléron** (4100 / 4620). Jour cible : **lundi 04/05 ou mercredi 06/05** (pas mardi à cause Boncelles). Hyper en premier le matin. Sur 1 seule journée si route bien montée.

## Luxembourg (reportés S18 v3)

- **AD Bastogne** (Tier A) — à replanifier
- **CM Bouillon** — RDV calendar.event #425 à replanifier (encore actif Odoo)
- **Carrefour Florenville** — OVERDUE 85j, **priorité absolue S19**

→ Zone Lux = 1 journée complète dédiée (Bastogne + Florenville + Bouillon faisables ensemble).

## ⚠️ Nouveau client GMS — Carrefour Market Bastogne CC Port (lead #288, Gagné 20/04, confirmé 23/04)

- **Magasin** : Carrefour Market Bastogne CC Port — Rue Gustave Delperdange 3, 6600 Bastogne (≠ Pascalino Route de Marche 149)
- **Email** : bastogne@orkari.be | **Tel** : 061 21 00 50 | **N° affilié Carrefour** : 0523
- **Contact Carrefour** : michael_grosjean@franchisecrf.com (demande à faire auprès de **Mme Neuville**)
- **Commande confirmée** (dans description lead #288) : Rouge printanier, Les 6 glacés, Panier de grand-maman, Le thé des amoureux, Blue Earl Grey OU Lampe merveilleuse (selon stock), Pêche de vigne — **gamme en infusette, placée en rayon**.
- **Livraison** : **semaine du 4 mai** (demande client explicite) → livraison physique par Gilles, probablement **mardi 05/05** sur la tournée Luxembourg (AD Bastogne + CM Bastogne CC Port + Florenville + Bouillon).

**BLOCAGES — actions Nicolas avant planif S19** :
- [ ] **Créer le partner Odoo** (res.partner) — aujourd'hui lead.partner_id = False. Candidate : orkari.be comme parent.
- [ ] **Encoder le SO** avec les 6 réf ci-dessus + format infusette — sinon pas planifiable (règle §1 REGLES : pas de devis).
- [ ] **Décider qui fait la demande Carrefour** (Mme Neuville — Nicolas ou Vanessa ?) — Jérôme attend la réponse (message 23/04 09:11 sur lead #288).
- [ ] Vérifier stock des 6 réf en **infusette** (pas vrac) — notamment Blue Earl Grey / Lampe merveilleuse selon dispo.

## Reports S18 v3 et v4

- **Delhaize Ottignies** (Tier B, ~21j) — contrainte "pas le jeudi", contact Jolan Cailleu possible
- **CM Hannut (PR Macleky)** — OVERDUE ~110j, contrainte "visite que le jeudi"
- **ITM Hannut** (Intermadis SA) — ~20j, OK demander Mr Christophe Wereau — Tier A avg 1100 €
- **AD Rochefort** (Tier B, OVERDUE 60j — retiré S18 v4 car S17)
- **Delhaize Marche** (Tier A, OVERDUE 36j — retiré S18 v4 car S17)

## Thés glacés (briefing Nicolas antérieur)

- **AD Delhaize Fosses-la-Ville** (Odoo 5441) — revisite thés glacés prévue S19. Contrainte : mercredi (Leslie présente toute la journée). Jour cible : **mercredi 06/05**.

## Brief d'organisation préliminaire

Zones à couvrir sur 5 jours (vendredi 08/05 = ouvrable) :
- **Lundi 04/05** — Liège/Seraing/Fléron : Hyper Boncelles + Hyper Fléron (livraisons) + visites Liège non faites S18 (ex: Proxy St-Séverin si OVERDUE devient vrai)
- **Mardi 05/05** — Luxembourg : AD Bastogne + **CM Bastogne CC Port (nouveau GMS, lead #288 — livraison si SO encodé à temps)** + Florenville + CM Bouillon (+ Marche en retour si temps ok)
- **Mercredi 06/05** — Namur-Sud : AD Fosses (thés glacés) + AD Rochefort + autres OVERDUE zone 5xxx
- **Jeudi 07/05** — Hainaut ou BW : CM Hannut (jeudi-only) + Delhaize Ottignies (jeudi OK avec Jolan) + autres BW
- **Vendredi 08/05** — à définir selon reliquats

⚠️ **Ne pas revisiter S18 (sauf si vraie OVERDUE justifiée)** : Mons Grands Prés, Ath, Jambes, Fragnée, Cointe, Embourg, Remouchamps, CM Marche, Fernelmont, Uccle Bascule, Boondael, Woluwe, Wavre, Incourt.

## À valider avant génération S19

- [ ] Confirmer que les 2 livraisons Hyper Carrefour peuvent être faites par Gilles en 1 seule tournée (pas de grosses charges > 2 m³).
- [ ] Vérifier si Delhaize Ottignies nécessite mail préalable (Jolan Cailleu).
- [ ] Check statut CRM Bouillon et RDV #425 (replanifier ou annuler).
- [ ] Vérifier stocks thés glacés dispos pour AD Fosses 06/05.
