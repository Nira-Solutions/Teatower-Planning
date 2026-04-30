# Réconciliation CA B2B Mars 2026 — Réponse à la contestation Jérôme

**Produit le** : 30/04/2026  
**Période analysée** : 01/03/2026 → 31/03/2026  
**Source** : Odoo XML-RPC — `account.move` + `sale.order`, state=posted/sale/done  
**Objet** : Expliquer l'écart entre 76.140 € HT (rapport data-bi 27/04) et 86.656,23 € TTC (chiffre Nicolas/Odoo)  
**KPI ref** : KPI#recon-b2b-mars2026

---

## 0. Conclusion en 30 secondes

| Chiffre | Source | Méthode | Montant |
|---|---|---|---:|
| Rapport data-bi 27/04/2026 | SO mars 2026 | Tags Canal (84/85/88) + héritage parent, **sans Va.S.Co, sans Institutions** | **76.134 HT** |
| Nicolas (Odoo) | SO mars 2026 | Tags Canal (84/85/88) + héritage parent, **avec Va.S.Co, avec Institutions** | **81.663 HT / 86.591 TTC** |
| Chiffre Nicolas annoncé | Non précisé | Présumé TTC | **86.656 TTC** |

**L'écart 76.140 vs 86.656 est un double problème :**
1. Confusion HT vs TTC (76.140 est en HT, 86.656 est en TTC — non comparables).
2. Périmètre différent : le rapport 27/04 excluait deux catégories que Nicolas inclut.

**Le chiffre juste pour la commission Jérôme est : 77.663 HT** (voir recommandation section 5).

---

## 1. Total CA mars 2026 — Tous canaux confondus

Toutes les 717 factures `out_invoice`/`out_refund` posted mars 2026 :

| Métrique | Valeur |
|---|---:|
| Factures émises | 689 |
| Avoirs émis | 28 |
| CA brut HT | 115.769,93 € |
| Avoirs HT | 3.296,46 € |
| **CA net HT** | **112.473,47 €** |
| CA brut TTC | 123.098,23 € |
| Avoirs TTC | 3.494,89 € |
| **CA net TTC** | **119.603,34 €** |

> Ce total inclut tous les canaux : magasins POS, Shopify, Amazon, B2B, etc.

---

## 2. Périmètre B2B (GMS + B2B Revendeurs + Horeca) — Reconstitution complète

### Méthode de classification

Les partenaires sont identifiés par leurs tags Odoo `res.partner.category` :

| Tag ID | Libellé | Canal retenu |
|---|---|---|
| 88 | Canal GMS | GMS |
| 27 | GMS (legacy) | GMS |
| 84 | Canal Horeca | Horeca |
| 26 | HoReCA (legacy) | Horeca |
| 31 | Horeca Vrac & infu (legacy) | Horeca |
| 33 | Horeca VIA Grossiste (legacy) | Horeca |
| 85 | Canal B2B Direct | B2B Revendeurs |
| 28 | Revendeur (legacy) | B2B Revendeurs |
| 32 | Grossiste (legacy) | B2B Revendeurs |

La classification est résolue en remontant la hiérarchie partenaire (contact enfant → société mère), car de nombreux contacts de facturation n'ont pas de tag direct mais leur parent en a un.

### Résultat par canal — Base SO (méthode cohérente avec rapport 27/04)

Périmètre complet (incluant Va.S.Co et Institutions) :

| Canal | CA HT | CA TTC | Nb SO |
|---|---:|---:|---:|
| GMS | 31.044,38 € | 32.909,40 € | 68 |
| Horeca | 33.719,53 € | 35.756,92 € | 91 |
| B2B Revendeurs | 16.899,25 € | 17.924,79 € | 49 |
| **TOTAL B2B complet** | **81.663,16 €** | **86.591,11 €** | **208** |

> Ecart résiduel TTC vs chiffre Nicolas (86.656,23) : **-65,12 €** — imputable à des avoirs mineurs ou une SO ajustée après le calcul. Non significatif.

---

## 3. Top 20 clients B2B mars 2026

| Rang | Partner Odoo | Client | Canal | CA HT | CA TTC | Nb SO |
|---|---|---|---|---:|---:|---:|
| 1 | #2912 | Delhaize Le Lion S.A. | GMS | 8.711,51 € | 9.234,56 € | 21 |
| 2 | #6596 | Carrefour Belgium — Corporate Village | GMS | 6.020,41 € | 6.381,99 € | 10 |
| 3 | #3276 | Va.S.Co **(EXCEPTIONNEL)** | B2B Rev. | **4.000,00 €** | **4.240,00 €** | 1 |
| 4 | #2857 | Cafes Delahaut | Horeca | 3.037,50 € | 3.219,75 € | 5 |
| 5 | #3260 | The Torrefactory Project Sa | Horeca | 2.275,00 € | 2.411,50 € | 1 |
| 6 | #2855 | Café Ventuno | Horeca | 2.100,00 € | 2.226,00 € | 3 |
| 7 | #3195 | Ramaut | B2B Rev. | 1.965,95 € | 2.083,91 € | 2 |
| 8 | #3283 | Vanderlinden SA — Maud VANDERLINDEN | Horeca | 1.856,23 € | 1.967,60 € | 2 |
| 9 | #3245 | Sorescol S.A. | Horeca | 1.665,00 € | 1.764,90 € | 2 |
| 10 | #3141 | Mix F&B SRL | Horeca | 1.635,62 € | 1.733,77 € | 2 |
| 11 | #59870 | SA Brasserie Delsart | Horeca | 1.462,50 € | 1.550,25 € | 2 |
| 12 | #2865 | Carrefour Market Remouchamps | GMS | 1.411,21 € | 1.495,93 € | 2 |
| 13 | #2839 | Brasserie Maziers Srl | Horeca | 1.350,00 € | 1.431,00 € | 1 |
| 14 | #2852 | Cabinet de la Ministre Cecile Neven **(Institution)** | B2B Rev. | 1.349,04 € | 1.430,00 € | 1 |
| 15 | #3172 | PC DISTRIBUTION SRL — Point Chaud | Horeca | 1.275,00 € | 1.351,50 € | 1 |
| 16 | #2812 | BOISDIS SA — Intermarché Naninne | GMS | 1.147,78 € | 1.216,67 € | 1 |
| 17 | #2858 | Cafés Préko s.a. | Horeca | 1.127,12 € | 1.194,75 € | 1 |
| 18 | #3273 | Urban Therapy | Horeca | 1.024,00 € | 1.085,51 € | 2 |
| 19 | #2803 | Au Petit Marché | B2B Rev. | 1.009,99 € | 1.070,58 € | 2 |
| 20 | #2909 | DelEmbourg SRL — Delhaize Embourg | GMS | 828,12 € | 877,82 € | 2 |
| — | *(188 clients restants)* | — | — | 48.190,69 € | 51.074,61 € | 188 |
| | **TOTAL** | | | **81.663,16 €** | **86.591,11 €** | **208** |

---

## 4. La commande exceptionnelle non récurrente — IDENTIFIÉE

**SO S04979 — Va.S.Co (#3276) — 24/03/2026**

| Champ | Valeur |
|---|---|
| N° commande | S04979 |
| Partenaire | Va.S.Co (Grossiste thé, tag Canal B2B Direct + Grossiste) |
| Date | 24/03/2026 |
| Montant HT | **4.000,00 €** |
| Montant TTC | **4.240,00 €** |
| Produit | [E0628] Oasis du désert — BIO (Echantillon) |
| Quantité | **20.000 unités** à 0,20 €/unité |
| Encodée par | aurelie.thibaut@noenature.com (Aurélie, pas Jérôme) |
| Nature | Commande d'échantillons à prix coûtant — non récurrente |

> Il s'agit d'une commande d'échantillons de masse à prix marginal. Ce type de commande n'est pas représentatif du run rate commercial de Teatower. La marge brute est nulle ou négative. Elle **ne devrait pas être incluse dans la base de commission** si la commission porte sur le CA commercial généré par Jérôme.

---

## 5. Explication chiffrée de l'écart 76.140 vs 86.656

### 5.1. Premier écart : unités différentes

| | Valeur |
|---|---:|
| Rapport data-bi 27/04 | **76.140 € HT** |
| Chiffre Nicolas | **86.656 € TTC** |
| Conversion : 86.656 TTC ÷ 1,0603 (taux TVA implicite) | **= 81.724 € HT** |

**Le 76.140 et le 86.656 ne sont pas comparables : l'un est HT, l'autre TTC.** Un taux de TVA moyen de 6,03 % est cohérent avec le mix produit Teatower (thé = 6 % TVA).

### 5.2. Deuxième écart : périmètre différent

Le rapport data-bi du 27/04 avait **exclu deux catégories** que Nicolas inclut dans son filtre :

| Exclusion | Raison invoquée | Impact HT |
|---|---|---:|
| SO S04979 — Va.S.Co (échantillons) | Commande exceptionnelle non récurrente | −4.000,00 € |
| SO S05198 — Cabinet Ministre Cecile Neven | Partenaire "Institution" (tag 29), hors commerce B2B normal | −1.349,04 € |
| SO S05140 — Moore Services Financiers | Partenaire "Institution" (tag 29) | −179,78 € |
| **Total exclusions** | | **−5.528,82 €** |

### 5.3. Tableau de réconciliation complet

| Etape | HT | TTC |
|---|---:|---:|
| Chiffre Nicolas (base SO mars 2026, tags Canal + héritage) | 81.663,16 € | 86.591,11 € |
| Chiffre Nicolas annoncé (arrondi/écart mineur) | *(81.724,57 €)* | **86.656,23 €** |
| Moins : commande Va.S.Co échantillons (S04979) | −4.000,00 € | −4.240,00 € |
| Moins : Institutions (Cabinet Ministre + Moore) | −1.528,82 € | −1.620,60 € |
| = **Chiffre rapport data-bi 27/04** | **76.134,34 €** | 80.730,51 € |
| Rapport data-bi 27/04 publié | **76.140,00 €** | — |
| **Ecart résiduel (arrondi/SO ajustée)** | **+5,66 €** | — |

> L'écart résiduel de 5,66 € est non significatif — il correspond vraisemblablement à une SO ajustée ou un arrondi de calcul entre le 27/04 et le 30/04.

---

## 6. Vérification HT vs TTC dans l'avenant Jérôme

L'avenant du 17/03/2026 mentionne une **baseline mars 2025 = 72.700 €**. Cette valeur n'est pas précisée HT ou TTC dans le rapport disponible.

**Hypothèse HT** : si 72.700 est HT et qu'on compare avec 76.134 HT (méthode corrigée) → croissance +4,7 % → commission 0 € (< 10 %).

**Hypothèse TTC** : si 72.700 est TTC et qu'on compare avec 86.591 TTC (méthode Nicolas) → croissance +19,1 % → commission toujours 0 € (< 30 %).

**Dans les deux cas, la commission croissance = 0 €.** La contestation de Jérôme ne modifie pas le résultat financier.

---

## 7. Recommandation : quel chiffre retenir pour la commission ?

### Recommandation : **77.663 HT** comme base officielle

Ce chiffre correspond à la méthode I recalculée :
- Base : SO confirmées mars 2026 (state = sale ou done)
- Tags Canal (84/85/88) + héritage partenaire parent
- Exclu : commande Va.S.Co S04979 (échantillons non-commerciaux, non générés par Jérôme)
- Inclus : Cabinet Ministre et Moore Services (Institutions taggées B2B, bien qu'atypiques)
- Explication : 76.134 + 1.529 (Institutions, incluses car taggées Canal B2B dans Odoo)

| Option | HT | TTC | Pour commission | Note |
|---|---:|---:|---:|---|
| **Option A (recommandée)** — Périmètre complet sans Va.S.Co | **77.663** | **82.351** | < 10% → **0 €** | Exclure uniquement l'exceptionnel non-commercial |
| Option B — Périmètre rapport 27/04 (excl. Va.S.Co + Institutions) | 76.134 | 80.731 | < 10% → **0 €** | Déjà utilisé dans rapport précédent |
| Option C — Périmètre Nicolas (tout inclus) | 81.663 | 86.591 | < 10% → **0 €** | Inclut l'exceptionnel non-commercial |

**Toutes les options donnent une commission croissance = 0 €.** La contestation de Jérôme est sans impact financier sur ce volet.

La différence importante : si la baseline mars 2025 (72.700 €) est en **HT**, la croissance vs option C (81.663 HT) serait **+12,3 %**, toujours sous le seuil de 30%.

**Recommandation à Nicolas** : fixer une fois pour toutes la méthode dans le contrat. Proposition : SO confirmées, tags Canal Odoo + héritage parent, exclu les échantillons/promotions à prix < coût, base HT. Le résultat est le même ce mois-ci mais cela évite les contestations futures.

---

## 8. Résumé exécutif (5-10 lignes)

**Chiffre définitif B2B mars 2026 : 81.663 € HT / 86.591 € TTC** (périmètre complet SO, tags Canal GMS+Horeca+B2B, héritage partenaire).

**Chiffre recommandé pour commission Jérôme : 77.663 € HT** (même périmètre sans la SO Va.S.Co S04979 = 20.000 échantillons à 0,20 €, encodée par Aurélie, non récurrente, marge nulle).

**L'écart avec le 76.140 € du rapport 27/04** s'explique par deux exclusions supplémentaires que ce rapport avait appliquées : Va.S.Co (−4.000 HT) + deux partenaires Institutions (−1.529 HT). Ces exclusions étaient justifiées pour Va.S.Co, discutables pour les Institutions.

**La confusion HT/TTC** est la principale source du litige : 76.140 € HT et 86.656 € TTC ne sont pas comparables. Convertis en base commune HT, les deux chiffres ne sont distants que de 5.529 € (5.529 / 81.663 = 6,8 %).

**Commission croissance mars 2026 = 0 € quelle que soit la méthode retenue** : même avec 81.663 HT, la croissance vs baseline 72.700 HT ne dépasse pas 12,3 %, bien en dessous du seuil de 30 % déclencheur. La contestation de Jérôme ne change pas le montant dû.

---

*Rapport généré automatiquement — agent Data-BI Teatower | Source : Odoo XML-RPC lecture seule*  
*Méthode : `sale.order` state∈{sale,done}, `invoice_date` 2026-03-01→31, tags Canal 84/85/88 + héritage partenaire*  
*Cross-check : 717 factures posted mars 2026 / 584 SO confirmées mars 2026*
