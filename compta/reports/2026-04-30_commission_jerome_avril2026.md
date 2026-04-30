# Commission Jérôme Carlier — Avril 2026

**Produit le** : 30/04/2026
**Période** : 01/04/2026 -> 30/04/2026
**Source** : Avenant contrat 17/03/2026 + Odoo XML-RPC (données complètes au 30/04) + rapport data-bi `2026-04-27_CA_avril_par_canal.md`
**Fichier d'entrée** : détection directe Odoo (pas d'Excel Adri pour avril)

---

## 1. Commission sur la croissance du chiffre d'affaires B2B

### Résultats

| Période | CA HTVA B2B (GMS + B2B Revendeurs + Horeca) | Source |
|---|---:|---|
| Avril 2025 (Odoo tags) | **60.745,21 €** | Odoo — 583 factures/avoirs tagués |
| Avril 2026 (Odoo tags, complet 30/04) | **60.440,74 €** | Odoo — 597 factures/avoirs tagués |
| **Croissance** | **-0,5 %** | Calcul direct |

> **Note importante sur le périmètre tags vs data-bi** : le rapport data-bi du 27/04 (forecast fin de mois) estimait un total 3 canaux à ~77.930 EUR en incluant ~20 partenaires non tagués dans Odoo identifiés par override manuel. La requête directe Odoo sur tags uniquement donne 60.440 EUR — un écart de -17.489 EUR. Le contrat (avenant 17/03/2026) ne spécifie pas la méthode d'attribution des canaux : soit on retient la méthode data-bi (77.930 EUR), soit on retient les tags Odoo seuls (60.440 EUR). **Ce point est à trancher par Nicolas** avant tout payslip.
>
> Le rapport data-bi indique par ailleurs : GMS 34.109 EUR | B2B 26.403 EUR | Horeca 17.418 EUR = **77.930 EUR** (scenario forecast retenu dans le tableau comparatif).

### Tableau comparatif selon les deux méthodes

| Méthode | Avril 2025 | Avril 2026 | Croissance | Commission barème |
|---|---:|---:|---:|---|
| Odoo tags seuls | 60.745 € | 60.441 € | **-0,5 %** | **0 €** |
| Data-bi (tags + overrides) — *rapport 27/04* | 65.627 € | ~77.930 € | **+18,7 %** | **0 €** (< 30%) |

> Quelle que soit la méthode retenue, la croissance reste sous le seuil de 30% déclencheur de commission.

### Application du barème (avenant §1.3)

| Croissance vs N-1 | Commission |
|---|---:|
| > 30 % | ≥ 1.000 € |
| **< 10 % (les deux méthodes)** | **0 €** |

> **Commission croissance : 0 € brut** (convergent sur les deux méthodes)

---

## 2. Commission sur les displays GMS (100 €/display, 1ʳᵉ commande ≥ 240 € HTVA)

### Partenaires GMS avec 1ʳᵉ SO en avril 2026 — détail

| # | Client | Partner Odoo | Créé | 1ʳᵉ SO avril 2026 | Montant HTVA | Encodé par | Statut |
|---|---|---|---|---|---:|---|---|
| 1 | Lambertdis SRL - Spar Manhay | #122944 | 11/04/26 | S05380 — 11/04 | 508,48 € | Jérôme Carlier | **ELIGIBLE** |
| 2 | NDB Diffusion - Spar Namur | #122958 | 11/04/26 | S05382 — 15/04 | 346,67 € | Jérôme Carlier | **ELIGIBLE** |
| 3 | Micamik SRL - Spar Godinne | #122995 | 14/04/26 | S05390 — 22/04 | 491,32 € | Jérôme Carlier | **ELIGIBLE** |
| 4 | Gmp La Louvière - Delhaize La Louvière | #123035 | 15/04/26 | S05404 — 20/04 | 480,16 € | Jérôme Carlier | **ELIGIBLE** |
| 5 | PGHM Distribution - Proxy Delhaize Maissin | #123067 | 16/04/26 | S05420 — 16/04 | 693,48 € | Jérôme Carlier | **ELIGIBLE** |
| 6 | Alivim SRL | #123294 | 28/04/26 | S05488 — 29/04 | 328,85 € | Magasin Liège | **A VALIDER** (pas Jérôme) |
| 7 | BLONFOOD SA - Intermarché Liège Blonden | #123345 | 30/04/26 | S05509 — 30/04 | 442,48 € | Magasin Liège | **A VALIDER** (pas Jérôme) |
| 8 | Gemblouxim - Intermarché Gembloux | #123346 | 30/04/26 | S05510 — 30/04 | 530,93 € | Magasin Liège | **A VALIDER** (pas Jérôme) |

### Partenaires GMS créés en avril SANS commande confirmée

| Client | Partner Odoo | Créé | Statut |
|---|---|---|---|
| Antheco SA - Intermarché Anthée | #122991 | 13/04/26 | Pas de SO confirmée — report au mois suivant |
| Gribouillon SRL | #123301 | 28/04/26 | Pas de SO confirmée — report au mois suivant |

### Rattrapages des 6 GMS de mars sans 1ʳᵉ commande

| Client | Partner Odoo | Situation au 30/04/2026 |
|---|---|---|
| Delhaize Recogne | #122091 | Toujours aucune SO confirmée |
| Carrefour Market Haine Saint Pierre | #122412 | Toujours aucune SO confirmée |
| Hyper Carrefour Bomerée | #122467 | Toujours aucune SO confirmée (*) |
| Hyper Carrefour Gosselies | #122466 | Toujours aucune SO confirmée (*) |
| Carrefour Market Wellin | #122589 | Toujours aucune SO confirmée |
| Hyper Carrefour Ans | #121818 | Toujours aucune SO confirmée |

> (*) Note mémoire : "Hyper Carrefour Bomerée + Gosselies ont reçu 2 SO en 2026-04-22 livrées par Gilles semaine 19". Odoo ne montre aucune SO confirmée sur ces partenaires au 30/04. Les commandes semaine 19 (4-10 mai) n'ont pas encore été encodées, ou sont liées à un autre partenaire/mécanisme. **A confirmer avec Nicolas.**

### Total displays éligibles certains : **5 × 100 € = 500 € brut**
### Total displays à valider (SO par Magasin Liège) : **3 × 100 € = 300 € sous réserve**

> Règle à clarifier : la commission GMS se déclenche-t-elle sur tout nouveau display ouvert par Teatower (y compris ceux où c'est le magasin lui-même qui encode sa 1ʳᵉ commande) ? Si oui : 8 displays, 800 €. Si uniquement SO encodées par Jérôme : 5 displays, 500 €.

---

## 3. Commission sur les nouveaux clients hors GMS (65 €/client, 1ʳᵉ commande ≥ 240 € HTVA)

### Détail des nouveaux clients non-GMS en avril 2026

| # | Client | Partner Odoo | Créé | 1ʳᵉ SO avril 2026 | Montant HTVA | Encodé par | Catégorie Odoo | Statut |
|---|---|---|---|---|---:|---|---|---|
| 1 | Ruiters Minina - Le Brunch de Ginette | #122940 | 11/04/26 | S05378 — 11/04 | 240,00 € | Jérôme Carlier | Canal B2B + HoReCA | **ELIGIBLE** (limite exacte = 240,00 €) |
| 2 | Cercle Historique Durbuy ASBL - La Maison des Mégalithes | #122938 | 11/04/26 | S05377 — 11/04 | 270,37 € | Jérôme Carlier | Canal B2B + HoReCA | **ELIGIBLE** |
| 3 | KVA Bar - Groupe DonGiovanni | #123207 | 24/04/26 | S05471 — 24/04 | 540,00 € | Jérôme Carlier | Grossiste (cat 32) | **ELIGIBLE** |
| 4 | Carrefour market Bastogne CC Port | #123189 | 23/04/26 | S05467 — 23/04 | 400,21 € | Jérôme Carlier | Sans tag (enfant de #6596 CV) | **BORDERLINE** — voir note |
| 5 | Camping du Bout du Monde SRL | #122820 | 07/04/26 | S05349 — 07/04 | 240,00 € | aurelie.thibaut@noenature.com | Canal B2B + HoReCA | **A VALIDER** (pas Jérôme) |

> **Bastogne CC Port (#123189)** : le partenaire est enregistré comme enfant de "Carrefour Belgium - Corporate Village" (#6596). Il n'a pas de tag GMS. Dans Odoo, la SO S05467 est encodée par Jérôme pour un montant de 400,21 € HTVA. Il s'agit d'un nouveau point de vente Carrefour Market — display nouveau. Deux lectures possibles :
> - Si on considère Bastogne comme GMS (logique métier) : commission display GMS 100 € (volet 2)
> - Si on considère Bastogne comme "client hors GMS" au sens du tag Odoo (cats=[]) : commission client 65 € (volet 3)
> **A trancher par Nicolas.** Dans ce rapport, Bastogne est laissé hors décompte final en attente de décision.

> **Camping du Bout du Monde SRL (#122820)** : créé le 07/04/26, cat [85,26] (Canal B2B + HoReCA). 1ère SO = S05349 le 07/04/26, 240,00 € HTVA, mais encodée par aurelie.thibaut@noeneau.com — pas par Jérôme. Si la commission est due uniquement sur les clients apportés par Jérôme, non éligible. Si elle est due sur tout nouveau client indépendamment du créateur de SO, éligible. **A trancher.**

### Rattrapages clients non-GMS de mars

| Client | Partner Odoo | Situation au 30/04/2026 |
|---|---|---|
| Le Loft du Renard | #121779 | Aucune nouvelle SO confirmée ≥ 240 € en avril |
| La Villa Lorraine | #121215 | Aucune nouvelle SO confirmée en avril |

### Total nouveaux clients éligibles certains : **3 × 65 € = 195 € brut**
### Total à valider (Bastogne + Camping) : **jusqu'à 2 × 65 € = 130 € supplémentaires** (ou 1 × 100 € si Bastogne requalifié GMS)

---

## 4. Total commission avril 2026

### Scénario conservateur (certains uniquement — SO par Jérôme, tags Odoo stricts)

| Volet | Détail | Montant brut |
|---|---|---:|
| Commission croissance CA B2B (-0,5 % ou +18,7 %) | < 30% dans les deux cas | **0 €** |
| Commission displays GMS (5 certains × 100 €) | Lambertdis, NDB, Micamik, Gmp La Louvière, PGHM Maissin | **500 €** |
| Commission nouveaux clients hors GMS (3 certains × 65 €) | Le Brunch de Ginette, Cercle Historique Durbuy, KVA Bar | **195 €** |
| **TOTAL conservateur** | | **695 € brut** |

### Scénario optimiste (si tous displays + Camping + Bastogne validés)

| Volet | Détail | Montant brut |
|---|---|---:|
| Commission croissance CA B2B | < 30% | **0 €** |
| Commission displays GMS (8 × 100 €) | + Alivim, BLONFOOD, Gemblouxim | **800 €** |
| Commission nouveaux clients hors GMS (4 × 65 €) | + Camping du Bout du Monde | **260 €** |
| Bastogne CC Port (si GMS) | 1 display additionnel | **100 €** |
| **TOTAL optimiste** | | **1.160 € brut** |

> Recommandation : valider scénario conservateur (695 €) en attendant confirmation Nicolas sur les 5 points ci-dessous.

---

## 5. Points à valider avec Nicolas avant envoi à Jérôme

1. **Méthode de calcul du CA B2B** : les deux méthodes (Odoo tags seuls = 60.441 EUR vs data-bi avec overrides = ~77.930 EUR) donnent la même conclusion (< 30% de croissance). En revanche, pour les mois futurs où le seuil sera potentiellement atteint, il faut fixer dès maintenant quelle méthode fait foi. Les tags Odoo ne couvrent qu'une partie des partenaires B2B (ex : DB Kfé, Sunparks, Le 7 by Juliette, BTL Break Time — clients historiques actifs — ne sont pas comptés car non tagués B2B dans l'onglet tags Odoo).

2. **Displays Alivim SRL, BLONFOOD SA, Gemblouxim** : 1ères SO passées par "Magasin Liège" (user interne magasin), pas par Jérôme. Si le display est ouvert commercialement par Jérôme mais la commande encodée par le magasin en central, la commission est-elle due ? (3 × 100 € = 300 € en jeu)

3. **Bastogne CC Port (#123189)** : Carrefour Market nouveau point de vente. Enfant de Corporate Village dans Odoo, sans tag GMS. SO S05467 encodée par Jérôme, 400,21 € HTVA. Classement GMS (100 €) ou non-GMS (65 €) ? Le site `CM Bastogne CC Port` est un nouveau magasin = logique display GMS.

4. **Camping du Bout du Monde SRL (#122820)** : nouveau client B2B, 1ère SO 240,00 € exactement, encodée par Aurelie (pas Jérôme). Éligible ou non ?

5. **Bomerée + Gosselies** : la mémoire projet indique des livraisons semaine 19 (4-10 mai) par Gilles. Ces SO n'apparaissent pas dans Odoo au 30/04. Elles tomberont donc en mai 2026. Confirmer que ces 2 displays seront comptabilisés en mai dès que la SO est encodée.

6. **Rattrapage Boucherie de Magerotte (mars)** : pas de nouvelle SO en avril — le point du rapport mars reste en suspens.

---

*Rapport généré automatiquement — agent Compta Teatower | Source : Odoo XML-RPC + avenant contrat 17/03/2026*
*Ne pas envoyer à Jérôme avant validation Nicolas.*
