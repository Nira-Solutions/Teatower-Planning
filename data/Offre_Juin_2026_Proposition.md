# Offre Juin 2026 — Version validée

**Statut** : Validé Nicolas — 11 mai 2026
**Auteur** : Nira
**Source data** : `compta/reports/2026-04-27_b2b_roadmap_data.md`

---

## Synthèse exécutive

Le mois de juin 2026 ouvre la roadmap B2B 12 mois. Deux campagnes en parallèle, **toutes deux focalisées sur les clients dormants** (sans commande > 6 mois). Pas d'envoi aux clients actifs — pas de cannibalisation.

| Campagne | Cible | Volume | CA cible | Marge nette |
|---|---|---|---|---|
| **A — Horeca dormants** | Horeca > 180j sans commande | 11 | +1 K€ | 47% (3+1 sur MB 63%) |
| **B — Revendeur dormants** | Revendeurs > 180j sans commande | 105 | +8 K€ | 57% (-10% sur MB 67%) |
| **TOTAL juin 2026** | | **116** | **+9 K€** | |

**Pas de code promo individuel.** Tracking conversion par croisement de listes Odoo automatique à J+30.

---

## Décisions clés validées 11/05/2026

1. **Horeca actifs (178) EXCLUS de la campagne** : pas de promo à des clients qui commandent déjà → on évite la cannibalisation et on préserve la mécanique 3+1 pour les vrais besoins de réactivation.
2. **Pas de code promo** : trop compliqué à suivre opérationnellement. Tracking par croisement Odoo (tag client + date commande juin).
3. **Revendeur dormants à -10%** (validé à la place du -15% initial) : marge meilleure (57%), reste très attractif pour des dormants.
4. **Pas d'échantillon staff** : retiré de l'offre Horeca, trop complexe à gérer en prépa.

---

## Campagne A — Horeca dormants

### Constat

| KPI Horeca dormants | Valeur |
|---|---|
| Dormants identifiés (> 180j, is_company, ≥ 1 commande historique) | 11 |
| Période de décrochage majoritaire | Été-automne 2025 |
| SKUs Horeca à fort enjeu | 8 boîtes HC250xxx (95% du CA Horeca à 61-63% MB) |

### Offre

- **3+1 sur boîtes HC25** (achetez 3 boîtes, la 4ᵉ offerte) — 1 réf au choix par tranche de 3
- **Frais de port offerts** dès 200 €
- **Conditions** : valable juin uniquement, commande minimum 6 boîtes

### Cible & tag

| Volume | Tag Odoo | Template Mailchimp |
|---|---|---|
| 11 dormants | `MC-202606-HORECA-DORMANT` | "Vous nous manquez" — focus retour + 3+1 + relance Jérôme top 5 J+10 |

### KPI

| Métrique | Cible |
|---|---|
| Réactivations | 3 sur 11 (~27%) |
| CA additionnel | +1 K€ |

### Mécanique économique

| Élément | Valeur |
|---|---|
| Prix moyen boîte HC25 | 14 € HT |
| Panier type 4 boîtes (3+1) | 42 € HT (3 × 14) |
| MB nominale boîte HC25 | 63% |
| MB nette après 3+1 | ~47% (boîte offerte = coût direct) |
| Marge plancher roadmap dormants | 30% → respectée |

---

## Campagne B — Revendeur dormants

### Constat

| KPI Revendeur dormants | Valeur |
|---|---|
| Dormants identifiés (> 180j, is_company, ≥ 1 commande historique) | 105 (segmentation finale après dedup) |
| CA historique cumulé estimé | ~120 K€ |
| Moyenne CA historique/client | ~1 150 € |
| Période de décrochage majoritaire | Été-automne 2025 |

**Pourquoi maintenant ?** Si on attend la campagne automne (octobre), 4 mois supplémentaires sans contact = beaucoup auront été récupérés par la concurrence ou rangé Teatower au placard. Juin = fenêtre courte pour reprendre contact avant la saison Noël (qui se prépare en septembre).

### Offre

- **-10% sur réassort libre** (toute commande ≥ 300 €)
- **Frais de port offerts** dès 250 €
- **Pas de SKU forcé** : le revendeur choisit ce qu'il veut (effet "carte blanche")
- **Conditions** : valable juin uniquement, 1 commande par client maximum

### Pourquoi cette mécanique (et pas un 3+1 comme Horeca)

| Critère | Horeca | Revendeur |
|---|---|---|
| Profil d'achat | Concentré sur 8 SKUs HC25 | Diversifié (infusettes + vrac + coffrets + glacés) |
| 3+1 fonctionnerait ? | Oui, achat répétitif sur même réf | Non, ils achètent diversifié |
| Mécanique optimale | Offre quantitative ciblée | Remise globale + liberté SKU |
| Effet psychologique | Augmenter fréquence | "Client roi" — reprendre contact sans contrainte |

### Cible & tag

| Volume | Tag Odoo | Template Mailchimp |
|---|---|---|
| 105 dormants | `MC-202606-REVENDEUR-DORMANT` | "Reprenons contact" — focus liberté + -10% + relance Jérôme top 20 J+10 |

### Top 20 dormants Revendeur à briefer à Jérôme (J+10)

Critère : CA historique cumulé ≥ 2 K€ (priorité commerciale terrain). Liste extraite d'Odoo le J-15.

### KPI

| Métrique | Cible |
|---|---|
| Réactivations | 13-15 sur 105 (~13%) |
| Panier moyen estimé | 580 € (vs 470 € moyenne Revendeur — réassort = panier plus gros) |
| CA additionnel | +8 K€ |
| Effet aval | Mise dans le pipe octobre (campagne automne premium) |

### Mécanique économique

| Élément | Valeur |
|---|---|
| MB Revendeur produit (hors coffrets Noël) | 67% |
| MB nette après -10% net | ~57% |
| Marge plancher roadmap dormants | 30% → respectée largement |

---

## Tracking conversion (sans code promo)

Décision 11/05 : pas de code promo individuel — trop complexe à suivre côté Vanessa.

À la place, tracking automatique par croisement de listes :

1. **Liste 1** : partners taggés `MC-202606-HORECA-DORMANT` ou `MC-202606-REVENDEUR-DORMANT` (les 116 destinataires)
2. **Liste 2** : `sale.order` confirmées entre 9 juin et 9 juillet 2026
3. **Croisement** : intersection des 2 listes = conversions identifiées
4. **Reporting J+30** : script Python génère le rapport (CA, taux conversion, top performers, dormants qui restent dormants)

Vanessa traite les commandes comme d'habitude. Elle applique l'offre si le client la mentionne (3+1 ou -10%). Pas de champ supplémentaire à saisir.

---

## Calendrier de préparation (J-X avant 9 juin)

| Date | Échéance | Responsable |
|---|---|---|
| **11 mai (J-30, fait)** | Validation offre + tagging Odoo + CSV Mailchimp + liste Vanessa | Nicolas + Nira |
| **15 mai (J-25)** | Brief créatif validé (objets, angles, visuels) | Stephan + Nicolas |
| **20 mai (J-20)** | Import CSV Mailchimp + création 2 audiences | Stephan |
| **20 mai (J-20)** | Stock check HC25 : min 50 boîtes/réf sur 8 best-sellers (volume juin = faible) | Stock-manager |
| **25 mai (J-15)** | Premiers drafts 2 templates Mailchimp | Stephan |
| **25 mai (J-15)** | Extraction top 20 Revendeur + top 5 Horeca dormants pour brief Jérôme | Nira |
| **27 mai (J-13)** | Revue templates + ajustements | Nicolas |
| **2 juin (J-7)** | Test envoi Mailchimp interne | Stephan |
| **3 juin (J-6)** | Brief Jérôme finalisé | Nicolas |
| **9 juin (J)** | **Envoi des 2 campagnes** | Stephan |
| **19 juin (J+10)** | Relance commerciale Jérôme top 20 + top 5 | Jérôme |
| **9 juillet (J+30)** | Reporting CA + taux conversion (croisement automatique) | Nicolas |

---

## Risques & arbitrages

### Risque 1 — Cannibalisation du pic d'octobre Revendeur
Les Revendeurs réactivés en juin pourraient "lisser" leur achat et moins commander en octobre. **Évaluation** : peu probable car juin = réassort (rotation magasin), octobre = renforcement automne/Noël (autre besoin). À vérifier en reporting J+90.

### Risque 2 — Tracking imparfait sans code
Si un client transfère le mail à un copain qui passe une commande, on ne saura pas que c'est venu du mailing. **Évaluation** : marginal sur 116 dormants, acceptable.

### Risque 3 — Bounces emails dormants
Sur 116 destinataires dormants, attendre 5-10 bounces (emails obsolètes). Vanessa nettoiera la liste Odoo en parallèle.

---

## Tags Odoo finalisés

| Tag | Volume | Statut |
|---|---|---|
| `MC-202606-HORECA-DORMANT` | 11 | Appliqué |
| `MC-202606-REVENDEUR-DORMANT` | 105 | Appliqué |
| ~~`MC-202606-HORECA-ACTIF`~~ | ~~178~~ | **Supprimé** (décision : pas d'envoi aux actifs) |

Convention : `MC-{YYYYMM}-{SEGMENT}-{FOCUS}` — préfixe `MC-` = audience Mailchimp, triable chronologiquement, traçabilité historique conservée dans Odoo.

---

## Livrables disponibles

- **CSV Mailchimp** (sans code promo) : `data/mailchimp_juin_2026.csv` — 112 lignes (11 + 101 avec email)
- **Liste Vanessa Excel** : `Liste_Vanessa_Juin_2026.xlsx` — 116 clients enrichis avec contacts, téléphones, adresses, CA 12M
- **Brief Stephan PDF** : `Brief_Stephan_Newsletters_Juin_2026.pdf`
- **Roadmap mise à jour** : `Roadmap_B2B_2026-2027.pdf`
