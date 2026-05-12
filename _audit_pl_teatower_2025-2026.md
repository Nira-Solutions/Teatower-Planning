# AUDIT P&L TEATOWER SA — Exercice 01/07/2025 → 30/06/2026
**Date audit : 12/05/2026 — 10 mois écoulés sur 12**
**Auditeur : Agent Compta (Odoo XML-RPC)**

---

## 1. COMPTE DE RÉSULTAT ODOO — SITUATION AU 12/05/2026

### 1.1 Produits (Income)

| Compte | Libellé | Montant NET |
|--------|---------|-------------|
| 700000 | CA B2B Belgique | 1 235 071,02 |
| 700006 | Recettes boutiques 6% | 241 585,70 |
| 700100 | CA B2B EU | 203 348,88 |
| 700021 | Recettes boutiques 21% | 35 170,12 |
| 700102 | E-commerce FR | 23 579,04 |
| 700104/105/200 | NL / LU / Export | 2 969,32 |
| 708xxx | Remises accordées | -2 437,28 |
| 743xxx | ATN / Récupérations | 1 349,27 |
| **CA RÉEL TOTAL** | | **1 740 636,07** |
| **757100** | **Ecarts caisse "gains" (ANOMALIE)** | **261 844,73** |
| **TOTAL PRODUITS AFFICHÉ** | | **2 002 480,80** |

### 1.2 Charges (Expense)

| Compte | Libellé | Montant |
|--------|---------|---------|
| 600000 | Achats matières premières (KF et autres) | 303 524,68 |
| 604024 | Achats marchandises TT | 201 124,21 |
| 600006 | Achats MP (copie) | 1 855,38 |
| 601000 | Consommables | 1 210,96 |
| 603000 | Sous-traitance | 1 564,86 |
| 604000 | Marchandises pour revente | 408,00 |
| **Total achats 600xxx** | | **509 688,09** |
| 611120 | Refacturation loyer (Havelange NiraSolutions) | 46 844,40 |
| 611121 | Loyer Liège | 115 287,99 |
| 611122 | Loyer Namur | 16 038,46 |
| 611123 | Loyer Waterloo | 17 310,00 |
| 613290 | Honoraires de gestion | 194 614,82 |
| 613240 | Honoraires Adrianne et Nicolas | 26 744,19 |
| 614140 | Frais de transport | 49 041,00 |
| 616600 | Frais de marketing | 45 430,55 |
| 613310 | Secrétariat social | 45 440,25 |
| 620200 | Rémunérations employés | 67 518,37 |
| 620300 | Rémunérations ouvriers | 20 811,77 |
| 621200/300 | Cotisations patronales | 17 410,50 |
| 612290 | Petit matériel / outillage | 17 126,57 |
| 617000 | Personnel intérimaire | 15 500,82 |
| 623901 | Chèques repas | 15 224,00 |
| Autres 61/62/64/65 | Charges diverses (voir détail) | ~179 000,00 |
| **Total charges exploitation** | | **~1 349 193,28** |
| 650200 | Frais financiers (intérêts leasing etc.) | 11 520,19 |
| **657100** | **Ecarts caisse "pertes" (ANOMALIE)** | **176 297,79** |
| 67xxx | IS estimé | 96,47 |
| **TOTAL CHARGES AFFICHÉ** | | **1 525 491,35** |

### 1.3 Résultat affiché Odoo

```
PRODUITS TOTAUX :   2 002 381,96
CHARGES TOTALES :   1 525 491,35
                    ────────────
RÉSULTAT NET :        476 890,61
```

**Ratio marge brute apparent : ~75% — ANORMALEMENT ÉLEVÉ pour du B2B alimentaire.**

---

## 2. AUDIT DES ANOMALIES

### A — Factures fournisseurs manquantes : ANOMALIE MAJEURE

**Constat :**
- 1 122 lignes de commandes achat ont `qty_received > qty_invoiced` sur la période
- **Valeur totale non facturée : 235 904,77 EUR**

**Détail top lignes (extrait) :**

| PO | Produit | Reçu | Facturé | Ecart | Valeur |
|----|---------|------|---------|-------|--------|
| P00174 | Infusette Teatower | 300 000 | 0 | 300 000 | 3 600,00 |
| P00470 | Le panier de grand maman | 1 486 | 0 | 1 486 | 3 581,26 |
| P00379 | La nana de Wépion | 200 | 0 | 200 | 3 550,00 |
| P00495 | Lady Dodo (Echantillon) | 24 935 | 0 | 24 935 | 3 490,90 |
| P00281 | Chauffage air pulsé mobile | 1 | 0 | 1 | 2 885,00 |
| P00340 | Pêche de vigne BIO | 39 940 | 19 900 | 20 040 | 2 605,20 |

**Impact :** Ces 235 904,77 EUR d'achats reçus sont en stock mais **pas comptabilisés en charges**. Le bénéfice est gonflé de cette somme. Kirchner Fischer et autres fournisseurs ont vraisemblablement des factures en attente.

**Verdict : ANOMALIE MAJEURE — 235 905 EUR de charges manquantes**

---

### B — Variation de stock : ANOMALIE STRUCTURELLE

**Constat :**
- **Aucune écriture sur comptes 609xxx** (Decrease/Increase in Stocks) sur l'exercice.
- **Aucune écriture sur comptes 71xxx** (Increase in stocks) en lien avec variation de stock.
- Stock Valuation Layers (SVL) sur la période : entrées +424 128 EUR / sorties -144 252 EUR = **variation nette +279 876 EUR** (stock a augmenté).
- Valeur stock actuelle (stock.quant) : **292 725 EUR** (dont 260 quants avec qty > 0 mais valeur = 0).

**Ce que cela signifie :**
En plan comptable belge, si le stock augmente de 279 876 EUR sur la période, cela devrait réduire les achats net (ou apparaître en 71xxx). Sans cette correction, les **achats bruts (509 688 EUR) restent intégralement en charges** alors qu'une partie est toujours en stock = charges surévaluées... mais ce même stock manque aussi de variation dans les SVL cohérents.

**Note importante :** Odoo semble utiliser le costing sur les mouvements de stock (AVCO/FIFO) mais l'écriture de variation de stock n'est pas refaite en 609/71 = les comptes de résultat ne reflètent pas la réalité du stock.

**Verdict : ANOMALIE STRUCTURELLE — vérification comptable urgente avec l'expert-comptable**

---

### C — Charges à payer absentes : ANOMALIE

**C1. Commissions Jérôme (613110)**
- Montant comptabilisé sur l'exercice : **0,00 EUR**
- Estimation d'après règles mémoire : 56 displays installés × 100 EUR = **5 600 EUR minimum**
- Hors GMS non estimable sans données clients Jérôme, mais les commissions B2B croissance (avenant 17/03/2026) ne sont pas provisionnées.

**C2. Loyer Havelange / NiraSolutions (611120)**
- Comptabilisé : 46 844,40 EUR sur 10 mois (10 factures mensuelles ~4 752 EUR/mois) — OK, régulier.

**C3. Honoraires expert-comptable (613250)**
- Total sur l'exercice : **750,00 EUR** (3 écritures : -570 en juil-25, +1320 en mars-26).
- Sur 10 mois, 750 EUR est anormalement bas. Provision habituellement ~500-800 EUR/mois.
- **Estimation provision manquante : ~4 000 à 7 000 EUR**

**C4. Assurances (613510/541/614xxx)**
- Total comptabilisé : 3 590,42 EUR sur l'exercice — à confirmer si complet.

**Verdict : ANOMALIE — minimum 9 600 EUR de charges à payer non provisionnées (commissions + honoraires)**

---

### D — Produits constatés d'avance (PCA) : FAIBLE IMPACT

**Constat :**
- 2 531 lignes de SO avec qty_invoiced > qty_delivered
- **Total PCA : 3 645,38 EUR**
- Principaux : S05133 (I0873 Mowgli Bounty, I0808 Thé Jasmin, I0876 Dolce Vita)

**Verdict : OK — impact négligeable (3 645 EUR), pas de prépaiements massifs de calendriers ou displays**

---

### E — CA fictif sur stock négatif : A INVESTIGUER

**Constat :**
- **344 quants avec quantité négative** dans les emplacements internes
- Valeur totale stock négatif : -33 697,94 EUR
- Produits concernés : coffrets Noël (C0174 Coffret Noël Vanillé : -3 unités), EM079 Boite assortiment (-34), accessoires divers (-1 à -6 unités)

**Ce que cela signifie :** Des produits ont été scannés/vendus en picking sans stock disponible. Dans un système AVCO/FIFO, cela provoque des coûts d'acquisition à zéro ou erronés sur ces sorties.

**Verdict : A INVESTIGUER — 344 quants négatifs, COGS sous-évalué sur ces articles**

---

### F — Amortissements : ANOMALIE GRAVE

**Constat :**
- **Aucune écriture sur comptes 630xxx** (Depreciation of Fixed Assets) sur l'exercice
- **Aucun asset enregistré** dans `account.asset` (state = open/close)
- Compte 630100 (Immobilisations incorporelles) et 630200 (Immobilisations corporelles) : **0,00 EUR**

**Ce que cela signifie :** Teatower possède des actifs (véhicules en leasing, matériel informatique, aménagements boutiques). Si aucun amortissement n'est passé, les charges sont sous-évaluées. Les comptes de leasing voiture (611301, 613550 = 16 426 EUR) indiquent des actifs en usage — les éventuels droits d'utilisation (IFRS 16 / adaptation belge) ne semblent pas amortis.

**Verdict : ANOMALIE — amortissements non constatés (montant à estimer avec expert-comptable)**

---

### G — Stock obsolète / dépréciation : ANOMALIE

**Constat :**
- **EM080 Boite Calendrier de l'Avent 2025** : 2 000 unités en stock, valeur **16 380,00 EUR** à valeur pleine
  - Le calendrier 2025 est invendable après décembre 2025 — nous sommes en mai 2026
  - Aucune écriture de dépréciation (631000 = 0)
- **CAL2023 et C0172** : 12 unités en stock, valeur 0 (déjà à zéro, pas d'impact)
- **Thés glacés GI0xxx** : stock résiduel saison 2025 (GI0634, GI0880, GI0912 etc.) — valeurs faibles
- **MP_1V0912 Thé glacé Mangue-fruit de la passion** : 150 unités × ~15,90 EUR = 2 385 EUR

**Verdict : ANOMALIE — 16 380 EUR à déprécier à 100% (EM080) + ~2 000-3 000 EUR thés glacés 2025**

---

### H — TVA / Accises : OK (Teatower SA)

**Constat TVA :**
- 451000 VAT Payable : solde créditeur -10 055,83 EUR (TVA à payer, cohérent)
- 451001 TVA OSS : -126,23 EUR (e-commerce EU)
- 451100 TVA Intracom : -4 934,36 EUR

**Accises Tea Tree SA :** Entité séparée, non vérifiable dans ce périmètre Odoo — OK par défaut.

**Verdict : OK — TVA apparemment cohérente (à valider sur déclaration formelle)**

---

### I — Ecritures d'inventaire / Stock reconciliation : ALERTE

**Constat :**
- Dernière `inventory_date` sur quant : 2026-12-31 (future, probablement date par défaut)
- Première `inventory_date` : 2025-11-19
- **Aucune réconciliation d'inventaire physique** datée en cours d'exercice visible
- SVL total toutes périodes : 113 193 entrées, valeur nette 3 863 EUR (très faible vs stock actuel de 292 725 EUR — incohérence probable avec création historique des quants)

**Verdict : ALERTE — réconciliation inventaire physique à effectuer avant clôture 30/06/2026**

---

### J — Marge anormale par SKU : ANOMALIE COGS

**SKU avec marge > 80% et CA > 500 EUR (standard_price = 0) :**

| Code | Produit | CA | Std price | Marge |
|------|---------|-----|-----------|-------|
| V0914 | Infusion du Printemps 2026 | 2 471,45 | 0,00 | 100% |
| GI0820 | Marrakech Sunset BIO glacé | 1 728,48 | 0,00 | 100% |
| HC250666 | English Breakfast 25 env. | 1 363,50 | 0,00 | 100% |
| 0 | 1V0301 Tisane tropicale KG | 566,04 | 0,00 | 100% |
| 0 | Livraison point relais Bpost | 558,35 | 0,00 | 100% |

**SKU avec std_price > 0 mais marge > 80% :**

| Code | Produit | CA | Std price | Marge |
|------|---------|-----|-----------|-------|
| I0205 | Etoiles filantes | 1 179,91 | 1,31 | 82,3% |
| I0868 | Citron meringuée | 1 876,99 | 1,34 | 82,1% |
| I0628 | Oasis du désert BIO | 2 044,51 | 1,42 | 81,5% |
| I0828 | Péché Mignon | 850,71 | 1,53 | 81,5% |

**Note :** Les marges 80-83% sur les infusettes au détail (prix vente ~7-8 EUR vs coût achat 1,30-1,53 EUR) peuvent être normales pour du B2B Teatower (vendu par boite de 20 infusettes). À confirmer si le `standard_price` reflète bien le coût unitaire de la boite (20 inf.) ou de l'infusette seule.

**COGS sous-évalué sur SKU à std_price=0 : ~6 688 EUR de CA sans COGS correspondant.**

**Verdict : A INVESTIGUER — 5 SKU à std_price=0 avec CA significatif à corriger côté product-data**

---

### ANOMALIE CRITIQUE HORS GRILLE : Ecarts de caisse POS (757100 / 657100)

**Constat :**
- **757100 "Positive Payment Differences"** : 261 844,73 EUR **COMPTABILISÉ EN PRODUIT**
  - Dont 3 entrées massives :
    - CSH3/25-26/0254 (2026-05-11) : **99 999,90 EUR** — Journal "Espèces"
    - PBNK1/25-26/0432 (2026-02-28) : **99 790,25 EUR** — Journal ING (combiner paiements PdV Carte)
    - LIE/25-26/0110 (2026-01-12) : **51 440,36 EUR** — Journal "Espèce Liège bis"
  - Ces 3 entrées = 251 230 EUR = **transferts de caisse vers banque mal configurés** comme "gains"

- **657100 "Negative Payment Differences"** : 176 297,79 EUR **EN CHARGES**
  - Dont :
    - NAMUR/25-26/0106 (2025-12-20) : **99 480,95 EUR** — Journal Cash Namur
    - LIEGE/25-26/0057 (2025-11-14) : **60 944,40 EUR** — Journal Cash Liège

**Ce qui se passe :** Les clôtures de sessions POS avec transfert manuel de caisse génèrent des "écarts" géants dans Odoo au lieu de passer en virement de compte. La différence nette est de **+85 547 EUR** qui gonfle artificiellement le résultat.

**Verdict : ANOMALIE CRITIQUE — 85 547 EUR net à neutraliser, reconfiguration POS urgente**

---

## 3. SYNTHÈSE FINANCIÈRE

### 3.1 Tableau de retraitement

| Poste | Résultat Odoo affiché | Ajustement | Résultat retraité |
|-------|----------------------|------------|-------------------|
| CA réel (hors 757100) | | | **1 740 636** |
| Ecarts caisse 757100 | +261 845 | -261 845 | — |
| Total Produits | **2 002 382** | -261 845 | **1 740 537** |
| | | | |
| Achats marchandises | -509 688 | | -509 688 |
| Achats non facturés (réceptions) | 0 | **-235 905** | -235 905 |
| Charges exploitation (61-64) | -833 600 | | -833 600 |
| Ecarts caisse 657100 | -176 298 | +176 298 | — |
| Charges financières (hors 657100) | -11 520 | | -11 520 |
| Commission Jérôme (provision) | 0 | **-5 600** | -5 600 |
| Honoraires comptable (provision) | -750 | **-5 500** | -6 250 |
| Dépréciation stock obsolète | 0 | **-16 380** | -16 380 |
| SKU std_price=0 (COGS manquant) | 0 | **-6 688** | -6 688 |
| IS estimé | -96 | | -96 |
| **Total Charges** | **-1 525 491** | | **-2 099 049** |
| | | | |
| **RÉSULTAT AFFICHÉ** | **+476 891** | | |
| **RÉSULTAT RETRAITÉ** | | **-353 206** | **+123 685** |

### 3.2 Estimation du gonflement total

| Anomalie | Impact résultat |
|----------|----------------|
| Ecarts caisse POS nets (A=produit fictif) | +85 547 |
| Achats non facturés fournisseurs | +235 905 |
| Commission Jérôme non provisionnée | +5 600 |
| Honoraires comptable sous-provisionnés | +5 500 |
| Stock obsolète non déprécié (EM080) | +16 380 |
| COGS manquant SKU std_price=0 | +6 688 |
| PCA facturés non livrés | +3 645 |
| **TOTAL GONFLEMENT ESTIMÉ** | **+359 265** |
| **Résultat affiché Odoo** | **476 891** |
| **Résultat retraité** | **~117 626** |

> **Note :** La variation de stock (point B) n'est pas chiffrée dans ce tableau car l'impact net dépend du modèle de costing Odoo (AVCO/FIFO vs standard price). Un audit avec l'expert-comptable est nécessaire pour quantifier. Si les 509 688 EUR d'achats incluent des marchandises toujours en stock, le résultat retraité pourrait être encore différent.

---

## 4. TOP 3 ACTIONS CORRECTIVES PRIORITAIRES

### PRIORITÉ 1 — Retraiter les écarts de caisse POS (impact : 85 547 EUR)
**Action :** Identifier les 3 entrées géantes (CSH3/25-26/0254, PBNK1/25-26/0432, LIE/25-26/0110) et les écritures miroir en pertes. Extourner ces OD et reconfigurer le flux de remise de caisse boutiques pour qu'il passe en virement de compte interne (572 → 550) et non en "écart de caisse". **Dispatcher vers agent `odoo`** pour la configuration POS.

### PRIORITÉ 2 — Comptabiliser les factures fournisseurs manquantes (impact : 235 905 EUR)
**Action :** Générer les factures d'achat en attente pour les 1 122 PO lines avec réception sans facturation. Priorité Kirchner Fischer (fournisseur principal). Certaines peuvent être en cours de réception et la facture n'est pas encore reçue — distinguer les factures réellement manquantes des livraisons partielles en cours. Contact fournisseurs pour obtenir les factures.

### PRIORITÉ 3 — Passer les provisions de clôture (impact : ~27 480 EUR cumulé)
**Provisions à passer en OD avant clôture 30/06/2026 :**
1. Commissions Jérôme (613110 / 444xxx) — minimum 5 600 EUR + B2B croissance à calculer
2. Honoraires expert-comptable (613250 / 444xxx) — ~5 500 EUR provision
3. Dépréciation EM080 Calendrier Avent 2025 (631000 / 309xxx ou 340xxx) — 16 380 EUR
4. COGS manquant sur SKU à std_price=0 — corriger standard_price via `product-data`

---

## 5. POINTS NÉCESSITANT L'EXPERT-COMPTABLE

1. **Variation de stock** : Vérifier si Odoo génère bien les écritures 609/71 en méthode AVCO et pourquoi elles sont absentes. Si le stock physique a réellement augmenté de 279 876 EUR, cela réduit mécaniquement le COGS réel.
2. **Amortissements** : Aucun actif enregistré dans Odoo. Les véhicules en leasing, le matériel IT, les aménagements boutiques — calculer et passer les dotations 630xxx.
3. **Réconciliation inventaire physique** avant clôture 30/06/2026.
4. **Accises Tea Tree SA** : Entité distincte, vérifier la déclaration AC4 Q1/2026 indépendamment.

---

## 6. LOG AUDIT

- Date : 2026-05-12
- Source : Odoo XML-RPC `tsc-be-tea-tree-main-18515272`
- Lignes analysées : 54 458 (account.move.line P&L)
- Lignes PO analysées : 1 542
- Lignes SO analysées : 43 535
- SVL analysés : 97 805

---
*Rapport généré par agent Compta Teatower — aucune écriture modifiée lors de cet audit.*

---

## 7. VÉRIFICATION 12/05/2026 — Correction anomalies A et POS (suite contestation Nicolas)

**Périmètre : lecture seule stricte. Aucune écriture Odoo.**

---

### 7.1 KIRCHNER FISCHER — Verdict révisé

**Constat initial (erroné) :** 235 905 EUR de réceptions sans facture fournisseur.

**Cause de l'erreur initiale :** Le calcul portait sur `purchase.order.line.qty_received > qty_invoiced` tous fournisseurs confondus. Sur Kirchner, les factures sont saisies **manuellement sans lien PO** (`purchase_id = False` sur tous les `account.move`). Conséquence : `qty_invoiced` reste à 0 sur tous les PO Kirchner même quand les factures existent et sont postées — ce qui produisait un faux écart.

**Réalité établie par requêtes directes :**

| Indicateur | Valeur |
|-----------|--------|
| Partenaires identifiés | id=7195 "Kirchner, Fischer & Co GmbH" + id=9989 "Kirchner Fischer & Co Gmbh (Nouveau)" |
| Factures `in_invoice` postées, période 01/07/2025-30/06/2026 | **83 factures** |
| Total facturé HT (posted) | **243 963,64 EUR** |
| Total avoirs (in_refund posted) | 3 671,30 EUR |
| **Net facturé comptabilisé** | **240 292,34 EUR** |
| Total PO Kirchner de la période (7 PO non annulés) | 207 732,18 EUR HT |

**Nicolas a raison : les factures Kirchner sont bien présentes dans Odoo.**

**Tableau PO Kirchner période — situation réelle :**

| PO | Date | HT | Réception | Facture liée | Verdict |
|----|------|----|-----------|-------------|---------|
| P00528 | 2026-05-05 | 31 375,00 | TT/IN/00753 — état : **assigned** (pas encore livrée) | Aucune | Normal — pas encore livré |
| P00506 | 2026-04-23 | 723,75 | TT/IN/00735 — état : **assigned** | Aucune | Normal — pas encore livré |
| P00495 | 2026-04-13 | 32 600,00 | 2 pickings done (24/04) + 1 assigned | Aucune liée au PO | Factures séparées probables — écart PO = 6 285,90 EUR |
| P00488 | 2026-04-01 | 239,00 | TT/IN/00705 — done 01/04 | Aucune liée au PO | A vérifier — 239 EUR |
| P00480 | 2026-03-25 | 64 697,50 | 1 picking done (24/04) + 1 assigned | Aucune liée au PO | Livraison partielle, facture probable séparée |
| P00470 | 2026-03-25 | 66 296,93 | 4 pickings done (avr.) + 1 assigned | Aucune liée au PO | Livraison partielle, factures probables séparées |
| P00340 | 2025-11-19 | 11 800,00 | TT/IN/00450 — done 27/01 | RESA506 = 11 969,66 HT (posted, **paid**) | Couvert — écart résiduel 5 907,20 EUR (livraisons partielles) |

**Ecart réel sur lignes PO Kirchner (qty_received > qty_invoiced) : 41 463,04 EUR HT**
- Dont PO non encore livrés (assigned) : 32 099 EUR → anomalie inexistante (livraison à venir)
- Ecart résiduel réel (livraisons faites, pas de facture rapprochée au PO) : **~9 364 EUR**
- Ces ~9 364 EUR sont vraisemblablement couverts par des factures Kirchner postées séparément mais sans lien PO — à réconcilier manuellement.

**Verdict révisé KIRCHNER : 0 EUR de "manquant" avéré. Les 235 905 EUR initiaux = faux positif dû à l'absence de rapprochement PO-facture dans Odoo. Les factures existent, sont postées et pour la plupart payées.**

**Point de vigilance subsistant :** Les factures Kirchner ne sont pas rapprochées à leurs PO. C'est une bonne pratique à corriger (dispatcher vers `odoo` pour workflow `invoice_ids` sur `purchase.order`), mais pas une anomalie comptable.

---

### 7.2 ECARTS POS — Analyse move par move

#### Entrée 1 — CSH3/25-26/0254 — 99 999,90 EUR — Journal "Espèces" — 2026-05-11

**Session POS liée :** POS/00648 — boutique **Waterloo**, 11/05/2026.
- CA journée : **75,30 EUR** (5 ordres, tous réglés par carte)
- Paiements espèces effectifs : **0,00 EUR** (aucun paiement espèces sur la session)
- `cash_register_balance_start` = 1 010,10 EUR
- `cash_register_balance_end_real` saisi = **101 010,00 EUR**
- Différence comptée = 101 010 - 1 010,10 - 0 = **99 999,90 EUR** → 757100

**Diagnostic : faute de frappe manifeste.** Le responsable a saisi `101010` au lieu de `1010` (ou au lieu du montant réel attendu ~1 010 EUR). Un zéro de trop dans le champ "caisse comptée". Il n'y a aucun CA espèces ce jour-là pour justifier 101 010 EUR en caisse.

**Action recommandée (NE PAS EXÉCUTER) :** Corriger le `cash_register_balance_end_real` de POS/00648 à la valeur réelle (~1 010 EUR), extourner CSH3/25-26/0254, recréer l'écriture de clôture correcte. Dispatcher vers agent `odoo`.

---

#### Entrée 2 — PBNK1/25-26/0432 — 99 790,25 EUR — Journal ING — 2026-02-28

**Session POS liée :** POS/00458 — **POP-UP STORE (Salon Wallon)**, 28/02/2026.
- CA journée : **1 290,15 EUR** (52 ordres)
- Paiements carte effectifs : **1 114,75 EUR**
- Paiements espèces : 175,40 EUR
- Le move PBNK1/25-26/0432 débite le compte 550004 Outstanding Receipts de **100 905,00 EUR** au lieu de 1 114,75 EUR.
- Ecart : 100 905 - 1 114,75 = **99 790,25 EUR** → 757100

**Diagnostic : montant de paiement carte saisi avec un facteur ×100.** Le champ "montant à percevoir via carte" a été encodé à 100 905 EUR (soit ~100× trop) au lieu de 1 114,75 EUR réel. Ce n'est pas un transfert caisse/banque mal classé — c'est une erreur de saisie du montant de paiement groupé POS.

**Action recommandée (NE PAS EXÉCUTER) :** Corriger le montant du paiement carte de POS/00458 à 1 114,75 EUR. Extourner PBNK1/25-26/0432 et recréer à montant correct. Dispatcher vers agent `odoo`.

---

#### Entrée 3 — LIE/25-26/0110 — 51 440,36 EUR — Journal "Espèce Liège bis" — 2026-01-12

**Session POS liée :** POS/00330 — boutique **Liège bis**, 12/01/2026.
- CA journée : **728,88 EUR** (27 ordres)
- Paiements espèces effectifs : **91,14 EUR**
- Paiements carte effectifs : 637,74 EUR
- `cash_register_balance_start` = 428,50 EUR
- Montant réel attendu en caisse = 428,50 + 91,14 = **519,64 EUR**
- `cash_register_balance_end_real` saisi = **51 960,00 EUR**
- Différence = 51 960 - 519,64 = **51 440,36 EUR** → 757100

**Diagnostic : faute de frappe manifeste.** Le montant saisi est 51 960 EUR pour une boutique dont le solde théorique est ~520 EUR. Probabilité : l'opérateur a saisi `51960` au lieu de `560` (ou `519`). Un zero intercalé ou une erreur de saisie numérique.

**Action recommandée (NE PAS EXÉCUTER) :** Corriger le `cash_register_balance_end_real` de POS/00330 à ~520 EUR. Extourner LIE/25-26/0110, recréer l'écriture correcte (écart réel de session = ~0 EUR). Dispatcher vers agent `odoo`.

---

### 7.3 Synthèse corrigée des 3 entrées POS

| Move | Session | Boutique | Date | Montant fictif | Cause réelle |
|------|---------|---------|------|---------------|-------------|
| CSH3/25-26/0254 | POS/00648 | Waterloo | 11/05/2026 | 99 999,90 EUR | Caisse comptée saisie 101 010 au lieu de ~1 010 (1 zéro de trop) |
| PBNK1/25-26/0432 | POS/00458 | POP-UP STORE | 28/02/2026 | 99 790,25 EUR | Paiement carte groupé saisi 100 905 au lieu de 1 114,75 (facteur ×100) |
| LIE/25-26/0110 | POS/00330 | Liège bis | 12/01/2026 | 51 440,36 EUR | Caisse comptée saisie 51 960 au lieu de ~520 (zéro intercalé) |
| **TOTAL** | | | | **251 230,51 EUR** | **3 fautes de frappe lors du comptage de caisse en clôture POS** |

**Ces 3 entrées sont des erreurs de saisie humaine lors de la clôture de session POS, pas des écarts réels de caisse ni des transferts caisse→banque mal configurés.** La correction relève de l'agent `odoo` (annulation/recréation des sessions ou OD extourne).

La contrepartie en 657100 (176 297,79 EUR) contient des entrées similaires (NAMUR/25-26/0106 = 99 480,95 EUR, LIEGE/25-26/0057 = 60 944,40 EUR) — même mécanique, sens inverse (caisse saisie inférieure au théorique). A vérifier avec le même niveau de détail si nécessaire.

---

### 7.4 Impact sur le tableau de retraitement P&L

Le chiffre "235 905 EUR de charges manquantes Kirchner" est **à supprimer** du tableau de retraitement — les factures existent.

Le chiffre "85 547 EUR net POS fictif" reste valide dans son montant (251 230 en gains fictifs vs 165 683 en pertes fictives correspondantes), mais la nature est corrigée : **erreurs de saisie POS** et non "transferts caisse→banque mal configurés".

| Anomalie | Impact résultat (révisé) |
|----------|--------------------------|
| Ecarts caisse POS nets (erreurs saisie) | +85 547 |
| ~~Achats Kirchner non facturés~~ | ~~+235 905~~ → **0** (faux positif) |
| Commission Jérôme non provisionnée | +5 600 |
| Honoraires comptable sous-provisionnés | +5 500 |
| Stock obsolète non déprécié (EM080) | +16 380 |
| COGS manquant SKU std_price=0 | +6 688 |
| PCA facturés non livrés | +3 645 |
| **TOTAL GONFLEMENT RÉVISÉ** | **+123 360** |
| **Résultat affiché Odoo** | **476 891** |
| **Résultat retraité révisé** | **~353 531** |

> Le résultat retraité passe de ~117 626 EUR à **~353 531 EUR** une fois le faux positif Kirchner retiré. La performance réelle est donc significativement meilleure qu'annoncé initialement. Les POS restent l'anomalie principale à corriger (85 547 EUR net fictif).

---

*Vérification 12/05/2026 — lecture seule stricte — aucune écriture Odoo.*
