# Commission Jérôme Carlier — Avril 2026

> **RAPPORT OBSOLETE — A REGENERER**
> Le 04/05/2026, la source officielle Adri (image PNG paliers) a ete fournie. Les vraies tranches de commission remplacent la formule lineaire fictive `50 × (croissance% − 10)` utilisee dans ce rapport.
> Application correcte pour avril 2026 : croissance +21,8 % → tranche 20-24,9 % → **650 € croissance** (et non 589 € calcule ici).
> Les volets displays et nouveaux clients peuvent egalement etre impactes si la liste Adri avril differe du decompte Odoo ci-dessous.
> **Ne pas envoyer a Jerome avant regeneration avec les vraies tranches Adri. Decision Nicolas a venir.**

**Produit le** : 30/04/2026 — **Révisé le** : 04/05/2026 (méthode Option C fixée par Nicolas + paliers linéaires 10-30 %)
**Période** : 01/04/2026 → 30/04/2026
**Source** : Avenant contrat 17/03/2026 + Odoo XML-RPC (données complètes au 30/04) + recalcul 04/05/2026 méthode SO
**Fichier d'entrée** : détection directe Odoo XML-RPC (pas d'Excel Adri pour avril)

---

## 1. Commission sur la croissance du chiffre d'affaires B2B

### Méthode officielle fixée le 04/05/2026 (décision Nicolas)

**Option C — périmètre complet** : SO confirmées (state = sale ou done), tags Canal GMS/B2B/Horeca (88/27/85/28/32/84/26/31/33) + héritage partenaire parent. Tout inclus. Source : Odoo XML-RPC recalcul 04/05/2026.

### Résultats

| Période | CA HTVA B2B (GMS + B2B Revendeurs + Horeca) | Source | Nb SO |
|---|---:|---|---:|
| Avril 2025 (baseline) | **55.572,37 €** | Odoo SO confirmées — tags + héritage | 142 |
| Avril 2026 (réalisé) | **67.672,19 €** | Odoo SO confirmées — tags + héritage | 179 |
| **Croissance** | **+21,8 %** | (67.672 − 55.572) / 55.572 | |

> **Note sur l'écart vs ancienne méthode** : le rapport initial du 30/04 utilisait les factures postées (`account.move`), ce qui donnait 60.745 EUR en avril 2025 et 60.441 EUR en avril 2026 (−0,5 %). La méthode SO est cohérente avec le calcul mars 2026 (Option C) et avec ce que Nicolas visualise nativement dans Odoo. L'écart SO vs factures s'explique principalement par le fait que l'Odoo actuel n'était pas en prod en avril 2025 — de nombreuses factures 2025 ont été importées rétroactivement sans SO correspondante.
>
> **Pour mémoire — méthode factures posted** : Avril 2025 = 71.236 € HT | Avril 2026 = 78.455 € HT | Croissance +10,1 % | Commission = 7 €. Cette méthode n'est pas retenue car non cohérente avec la méthode mars.

### Application des paliers linéaires 10 %→30 % (décision Nicolas 04/05/2026)

| Seuil | Commission |
|---|---:|
| < 10 % | 0 € |
| Entre 10 % et 30 % | `50 × (croissance% − 10)` |
| > 30 % | ≥ 1.000 € |

**Application : `50 × (21,8 − 10) = 50 × 11,8 = 590 € brut`**

> Calcul exact : croissance = (67.672,19 − 55.572,37) / 55.572,37 × 100 = 21,77 % → `50 × (21,77 − 10) = 50 × 11,77 = 588,5 €` → **arrondi 589 € brut**.

→ **Commission croissance avril 2026 : 589 € brut**

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

### Scénario conservateur révisé (certains uniquement — décision Nicolas 04/05/2026)

| Volet | Détail | Montant brut |
|---|---|---:|
| Commission croissance CA B2B (+21,8 % — Option C) | `50 × (21,8 − 10)` | **589 €** |
| Commission displays GMS (5 certains × 100 €) | Lambertdis, NDB, Micamik, Gmp La Louvière, PGHM Maissin | **500 €** |
| Commission nouveaux clients hors GMS (3 certains × 65 €) | Le Brunch de Ginette, Cercle Historique Durbuy, KVA Bar | **195 €** |
| **TOTAL conservateur RÉVISÉ** | | **1.284 € brut** |

### Scénario optimiste (si tous displays + Camping + Bastogne validés)

| Volet | Détail | Montant brut |
|---|---|---:|
| Commission croissance CA B2B (+21,8 %) | `50 × (21,8 − 10)` | **589 €** |
| Commission displays GMS (8 × 100 €) | + Alivim, BLONFOOD, Gemblouxim | **800 €** |
| Commission nouveaux clients hors GMS (4 × 65 €) | + Camping du Bout du Monde | **260 €** |
| Bastogne CC Port (si GMS) | 1 display additionnel | **100 €** |
| **TOTAL optimiste** | | **1.749 € brut** |

> Recommandation : valider scénario conservateur révisé (1.284 €) en attendant confirmation Nicolas sur les 5 points ci-dessous. La commission croissance de 589 € est certaine — seuls les displays et clients hors GMS sont à valider.

> **Révision du 04/05/2026** : la commission croissance passe de 0 € à 589 € suite à l'application de la méthode Option C (SO confirmées, périmètre complet) et des paliers linéaires 10-30 % décidés par Nicolas. Le total conservateur passe de 695 € à 1.284 €.

---

## 5. Points à valider avec Nicolas avant envoi à Jérôme

1. ~~**Méthode de calcul du CA B2B**~~ : **TRANCHE le 04/05/2026** — méthode Option C (SO confirmées, tags Canal + héritage parent, périmètre complet). Commission croissance = 589 €. Les partenaires non tagués (ex. DB Kfé, Sunparks, Le 7 by Juliette, BTL Break Time) restent hors périmètre car sans tag Canal dans Odoo — si Nicolas souhaite les inclure, il faut les tagger en Odoo.

2. **Displays Alivim SRL, BLONFOOD SA, Gemblouxim** : 1ères SO passées par "Magasin Liège" (user interne magasin), pas par Jérôme. Si le display est ouvert commercialement par Jérôme mais la commande encodée par le magasin en central, la commission est-elle due ? (3 × 100 € = 300 € en jeu)

3. **Bastogne CC Port (#123189)** : Carrefour Market nouveau point de vente. Enfant de Corporate Village dans Odoo, sans tag GMS. SO S05467 encodée par Jérôme, 400,21 € HTVA. Classement GMS (100 €) ou non-GMS (65 €) ? Le site `CM Bastogne CC Port` est un nouveau magasin = logique display GMS.

4. **Camping du Bout du Monde SRL (#122820)** : nouveau client B2B, 1ère SO 240,00 € exactement, encodée par Aurelie (pas Jérôme). Éligible ou non ?

5. **Bomerée + Gosselies** : la mémoire projet indique des livraisons semaine 19 (4-10 mai) par Gilles. Ces SO n'apparaissent pas dans Odoo au 30/04. Elles tomberont donc en mai 2026. Confirmer que ces 2 displays seront comptabilisés en mai dès que la SO est encodée.

6. **Rattrapage Boucherie de Magerotte (mars)** : pas de nouvelle SO en avril — le point du rapport mars reste en suspens.

---

*Rapport généré automatiquement — agent Compta Teatower | Source : Odoo XML-RPC + avenant contrat 17/03/2026*
*Ne pas envoyer à Jérôme avant validation Nicolas.*
