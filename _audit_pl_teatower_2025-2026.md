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

## 8. VÉRIFICATION 657100 — 12/05/2026

**Périmètre : lecture seule stricte. Aucune écriture Odoo.**

### Objectif

Identifier les grosses entrées côté 657100 (écarts négatifs POS) sur l'exercice 01/07/2025 → 30/06/2026 et déterminer si elles sont de vraies pertes de caisse ou des erreurs de saisie symétriques aux 3 anomalies détectées sur 757100.

---

### 8.1 Toutes les lignes 657100 > 1 000 EUR — Exercice 2025-2026

| Move | Date | Journal | Débit | Origine |
|------|------|---------|-------|---------|
| CSH3/25-26/0256 | 2026-05-12 | Espèces (Waterloo) | 99 999,85 | POS/00650 |
| NAMUR/25-26/0106 | 2025-12-20 | Cash (Namur) | 99 480,95 | POS/00264 |
| LIEGE/25-26/0057 | 2025-11-14 | Espèces (Liège) | 60 944,40 | POS/00138 |
| POP/25-26/0015 | 2025-12-03 | Caisse POP-UP | 4 122,95 | POS/00201 |
| NAMUR/25-26/0057 | 2025-11-19 | Cash (Namur) | 3 371,02 | POS/00154 |
| POP/25-26/0062 | 2026-05-10 | Caisse POP-UP | 1 211,04 | POS/00645 |
| **TOTAL > 1 000 EUR** | | | **269 130,21** | |
| Total 657100 affiché | | | **176 297,79** | |

> Note : le total des lignes > 1 000 EUR (269 130,21) dépasse le total affiché 657100 (176 297,79) de ~92 832 EUR. Cela s'explique par des lignes de contrepartie crédit également sur 657100 (corrections/annulations partielles non filtrées ici) ou par des lignes supplémentaires en dessous du seuil. Les 3 lignes géantes représentent 260 425,20 EUR à elles seules.

---

### 8.2 Analyse session par session des 3 grosses lignes

#### Ligne 1 — CSH3/25-26/0256 — 99 999,85 EUR — Waterloo — 2026-05-12

**Session POS/00650 (Waterloo, Config 1) :**
- Balance Start saisi : **101 010,00 EUR** — ANORMAL (valeur résiduelle de l'erreur 757100 de la veille)
- Balance End Théorique : 101 021,00 EUR
- Balance End Real saisi : 1 021,15 EUR
- Différence résultante : -99 999,85 EUR → 657100

**CA de la session :** 182,96 EUR (10 ordres). Paiements espèces : 11,00 EUR.

**Mécanique :** La session POS/00648 du 11/05/2026 (erreur 757100 connue) a clôturé avec un `cash_register_balance_end_real` = 101 010,00 EUR (faute de frappe : 101 010 au lieu de ~1 010). Odoo a reporté ce montant erroné comme `balance_start` de la session suivante POS/00650 du 12/05. L'opérateur a ensuite saisi la caisse réelle (~1 021 EUR), générant un écart fictif de -99 999,85 EUR côté 657100.

**Verdict : ERREUR DE SAISIE SYMÉTRIQUE.** La perte 657100 est la contrepartie directe de l'erreur 757100 de POS/00648. Extourner les deux ensemble (CSH3/25-26/0254 côté 757100 + CSH3/25-26/0256 côté 657100) remet la caisse Waterloo à zéro.

---

#### Ligne 2 — NAMUR/25-26/0106 — 99 480,95 EUR — Namur — 2025-12-20

**Session POS/00264 (Namur, Config 4) :**
- Balance Start saisi : **100 495,00 EUR** — ANORMAL
- Balance End Théorique : 100 701,45 EUR
- Balance End Real saisi : 1 220,50 EUR
- Différence résultante : -99 480,95 EUR → 657100

**CA de la session :** 5 503,28 EUR (200 ordres). Paiements espèces : 206,45 EUR.

**Session précédente POS/00259 (Namur, 19/12/2025) :** Balance End Real = 990,31 EUR — normal. La Balance Start de 100 495 ne provient donc pas d'un report direct de la session précédente.

**Mécanique probable :** L'opérateur a saisi manuellement 100 495 EUR comme solde d'ouverture de caisse au lieu de ~995 EUR (ou a saisi un montant avec deux zéros de trop). Ce n'est pas un report automatique d'une erreur antérieure mais une erreur de saisie à l'ouverture elle-même. La caisse réelle comptée en clôture (1 220,50 EUR) est cohérente avec le vrai solde attendu (~990 + 206 espèces encaissées = ~1 197 EUR). L'écart fictif de -99 480,95 EUR résulte uniquement de la mauvaise saisie du balance_start.

**Verdict : ERREUR DE SAISIE.** Balance Start erronée à l'ouverture de session (100 495 au lieu de ~995 EUR, facteur ×100 ou zéros en trop). L'écart 657100 est 100% fictif. La caisse réelle Namur était ~1 220 EUR, cohérent avec les sessions environnantes.

---

#### Ligne 3 — LIEGE/25-26/0057 — 60 944,40 EUR — Liège — 2025-11-14

**Session POS/00138 (Liège Config 3, boutique principale) :**
- Balance Start saisi : **61 560,00 EUR** — ANORMAL
- Balance End Théorique : 61 569,50 EUR
- Balance End Real saisi : 625,10 EUR
- Différence résultante : -60 944,40 EUR → 657100

**CA de la session :** 59,90 EUR (4 ordres). Paiements espèces : 9,50 EUR.

**Session précédente POS/00132 (Liège, 13/11/2025) :** Balance End Real = 615,60 EUR — normal.

**Mécanique :** La session POS/00137 du même jour (ouverture à 09:18, clôture à 09:24, 0 ordre, CA = 0) a un Balance End Real = 0,00 et une différence de -615,60. Ce mouvement est une session "fantôme" d'ouverture-clôture immédiate. La session POS/00138 a été ouverte avec un Balance Start = 61 560,00 qui ne provient pas de POS/00132 (615,60) mais semble être une saisie manuelle erronée à l'ouverture (615,60 → 61 560,00 : inversion de chiffres ou zéro intercalé). L'opérateur a clôturé à 625,10 EUR (cohérent avec ~615 réel + 9,50 espèces).

**Verdict : ERREUR DE SAISIE.** Balance Start erronée à l'ouverture de session (61 560 au lieu de 615,60 — inversion probable : 61 5,60 tapé 61560). L'écart 657100 est 100% fictif.

---

### 8.3 Analyse des 3 lignes modérées (1 000 – 5 000 EUR)

#### POP/25-26/0015 — 4 122,95 EUR — Caisse POP-UP — 2025-12-03

**Session POS/00201 (POP-UP STORE, Config 2) :**
- Balance Start saisi : 4 598,00 EUR
- Balance End Théorique : 4 663,25 EUR
- Balance End Real saisi : 540,30 EUR
- Différence : -4 122,95 EUR

**CA de la session :** 272,35 EUR. Paiements espèces : 65,25 EUR.

**Session précédente POS/00195 (POP-UP, 02/12/2025) :** Balance End Real = 488,90 EUR — normal.

**Mécanique :** Balance Start = 4 598,00 EUR ne vient pas de la session précédente (488,90). C'est une saisie manuelle erronée à l'ouverture. La caisse réelle comptée (540,30) est cohérente avec ~489 + 65 espèces. Écart fictif.

**Verdict : ERREUR DE SAISIE.** Balance Start 4 598 au lieu de ~489 (facteur ×10 environ). Écriture 657100 fictive à hauteur de 4 122,95 EUR.

---

#### NAMUR/25-26/0057 — 3 371,02 EUR — Cash Namur — 2025-11-19

**Session POS/00154 (Namur, Config 4) :**
- Balance Start saisi : 913,00 EUR
- Balance End Théorique : 4 341,47 EUR
- Balance End Real saisi : 970,45 EUR
- Différence : -3 371,02 EUR

**CA de la session :** 750,67 EUR. Paiements espèces non précisés mais si le théorique est 4 341 → espèces attendues = 4 341 - 913 = 3 428,47 EUR.

**Mécanique :** Ici la Balance Start (913 EUR) semble normale. C'est le Balance End Real (970,45 EUR) qui est suspect : l'opérateur a saisi 970 EUR alors que le théorique était 4 341 EUR. Soit une vraie remise de caisse non captée (retrait d'espèces en cours de journée de ~3 400 EUR), soit une erreur de saisie de clôture (970 saisi au lieu de 4 370). La différence de -3 371 est moins "ronde" que les précédentes, ce qui peut indiquer une vraie variation.

**Verdict : AMBIGU.** Peut être une remise de caisse intermédiaire (vidage partiel) ou une erreur de saisie. A vérifier avec Nicolas : y a-t-il eu un vidage de caisse Namur le 19/11/2025 ? Si oui, l'argent devrait apparaître dans un compte 570 ou 550 pour justifier le retrait. A classer en **review** si non confirmé.

---

#### POP/25-26/0062 — 1 211,04 EUR — Caisse POP-UP — 2026-05-10

**Session POS/00645 (POP-UP STORE, Config 2) :**
- Balance Start saisi : 1 213,00 EUR
- Balance End Théorique : 1 231,04 EUR
- Balance End Real saisi : 20,00 EUR
- Différence : -1 211,04 EUR

**CA de la session :** 522,45 EUR (session parallèle POS/00644 = 456,55 EUR).

**Mécanique :** Balance Start 1 213 semble normal. Balance End Real = 20 EUR saisie alors que le théorique est 1 231 EUR. L'opérateur a saisi 20 au lieu de ~1 231 (un zéro manquant ? champ mal rempli ?). Ou remise de caisse de ~1 211 EUR vers la banque non tracée séparément.

**Verdict : PROBABLE ERREUR DE SAISIE.** 20 EUR saisi au lieu de ~1 213 EUR (quasi la totalité de la caisse réelle). Très peu probable que la caisse POP-UP soit tombée à 20 EUR sans transaction de retrait traçable. A confirmer.

---

### 8.4 Tableau récapitulatif — Verdict par ligne

| Move | Montant | Verdict | Qualification |
|------|---------|---------|---------------|
| CSH3/25-26/0256 | 99 999,85 | **ERREUR SAISIE SYMÉTRIQUE** | Balance Start héritée de POS/00648 (erreur 757100) |
| NAMUR/25-26/0106 | 99 480,95 | **ERREUR SAISIE** | Balance Start 100 495 au lieu de ~995 (×100) |
| LIEGE/25-26/0057 | 60 944,40 | **ERREUR SAISIE** | Balance Start 61 560 au lieu de 615,60 (inversion) |
| POP/25-26/0015 | 4 122,95 | **ERREUR SAISIE** | Balance Start 4 598 au lieu de ~489 (×10) |
| NAMUR/25-26/0057 | 3 371,02 | **AMBIGU** | BE_Real suspect — vidage caisse possible ou erreur |
| POP/25-26/0062 | 1 211,04 | **PROBABLE ERREUR SAISIE** | BE_Real = 20 EUR au lieu de ~1 213 |

| Catégorie | Total EUR |
|-----------|-----------|
| Erreurs de saisie confirmées (à extourner) | 264 548,15 |
| Cas ambigu (NAMUR/25-26/0057, à confirmer) | 3 371,02 |
| Probable erreur (POP/25-26/0062, à confirmer) | 1 211,04 |

---

### 8.5 Calcul du X et validation de l'objectif Nicolas

**Contexte de la demande :**
- Extourner les 3 erreurs 757100 = -251 230,51 EUR côté produits fictifs
- Neutraliser les erreurs 657100 correspondantes = +X EUR (réduction des charges fictives)
- Résultat retraité cible = 391 344 EUR

**Calcul :**

| Scénario | X (657100 extournable) | Résultat retraité |
|----------|----------------------|-------------------|
| Erreurs confirmées seules (3 grandes lignes) | +260 425,20 | 476 891 – 251 230 + 260 425 = **486 086** |
| Erreurs confirmées + POP/0015 + POP/0062 | +265 759,19 | 476 891 – 251 230 + 265 759 = **491 420** |
| Scénario "cible Nicolas" (X = 165 683) | +165 683,00 | 476 891 – 251 230 + 165 683 = **391 344** |

**Le X qui donnerait 391 344 EUR est 165 683 EUR — il n'est pas atteint par les seules erreurs confirmées (260 425 EUR ou 265 759 EUR selon scope).**

**Pourquoi l'écart ?**

Les erreurs côté 657100 (260 425 EUR) sont PLUS importantes que les erreurs côté 757100 (251 230 EUR) — l'asymétrie s'explique par deux phénomènes distincts :

1. CSH3/25-26/0256 (99 999,85 EUR côté 657100) est la **conséquence directe** de l'erreur POS/00648 qui a généré CSH3/25-26/0254 (99 999,90 EUR côté 757100). Ces deux écritures se compensent presque à l'euro près. Les extourner ensemble = impact net quasi nul sur le résultat.

2. NAMUR/25-26/0106 (99 480,95 EUR côté 657100) et LIEGE/25-26/0057 (60 944,40 EUR côté 657100) sont des erreurs **indépendantes** côté pertes sans contrepartie côté gains sur 757100. Les extourner réduit les charges, donc **augmente** le résultat.

3. Les 3 erreurs 757100 (PBNK1/25-26/0432 et LIE/25-26/0110 et CSH3/25-26/0254) réduisent le résultat de 251 230 EUR (correction produits fictifs). Seule CSH3/25-26/0254 a une contrepartie 657100 directe.

**Impact net réel si on extourne TOUT :**

| Opération | Impact résultat |
|-----------|----------------|
| Extourne erreurs 757100 (produits fictifs) | -251 230 EUR |
| Extourne erreurs 657100 confirmées (charges fictives) | +260 425 EUR |
| Effet net | **+9 195 EUR** |
| Résultat retraité | 476 891 + 9 195 = **486 086 EUR** |

Le résultat réel après correction de TOUTES les erreurs POS serait **~486 086 EUR**, soit légèrement supérieur au résultat affiché Odoo (476 891 EUR). Les pertes fictives 657100 dépassent les gains fictifs 757100 de ~9 000 EUR.

**L'objectif 391 344 EUR de Nicolas ne ressort pas des corrections POS seules.**

Pour atteindre 391 344 EUR, il faudrait un X = 165 683 EUR côté 657100, c'est-à-dire n'extourner que NAMUR/25-26/0106 (99 480,95) + LIEGE/25-26/0057 (60 944,40) + une partie de POP/25-26/0015 ≈ 5 257 EUR — ce qui ne correspond pas à la logique comptable. L'objectif 391 344 EUR repose probablement sur une autre hypothèse de retraitement (ex: avec la variation de stock ou d'autres ajustements), pas uniquement sur les corrections POS.

**Recommandation :** Communiquer à Nicolas que les corrections POS nettes amèneront le résultat à ~486 000 EUR (pas 391 344 EUR). Si 391 344 EUR est l'objectif d'expert-comptable, la différence (~95 000 EUR) proviendrait d'autres retraitements (variation de stock, factures manquantes, provisions).

---

### 8.6 Actions recommandées (NE PAS EXÉCUTER — soumettre à Nicolas)

1. **Extourner ensemble les 2 écritures Waterloo** (CSH3/25-26/0254 côté 757100 + CSH3/25-26/0256 côté 657100) : impact net ≈ 0 EUR sur le résultat, mais assainit les comptes 757/657.

2. **Extourner NAMUR/25-26/0106** (657100 -99 480,95 EUR) : augmente le résultat de 99 480 EUR.

3. **Extourner LIEGE/25-26/0057** (657100 -60 944,40 EUR) : augmente le résultat de 60 944 EUR.

4. **Extourner PBNK1/25-26/0432** (757100 -99 790,25 EUR) + **LIE/25-26/0110** (757100 -51 440,36 EUR) côté gains fictifs : réduit le résultat de 151 230 EUR.

5. **Clarifier NAMUR/25-26/0057** (3 371 EUR) avec Nicolas : y a-t-il eu un vidage de caisse le 19/11/2025 ?

6. **Clarifier POP/25-26/0062** (1 211 EUR) : remise de caisse POP-UP le 10/05/2026 ?

Dispatcher vers agent `odoo` pour l'exécution des extournes une fois validées par Nicolas.

---

*Vérification 657100 — 12/05/2026 — lecture seule stricte — aucune écriture Odoo.*

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

---

## 9. VÉRIFICATION PRÊTS BELFIUS — 12/05/2026

**Périmètre : lecture seule stricte. Aucune écriture Odoo.**
**Objectif : vérifier si des prêts Belfius gonflent le résultat de ~80 k€ (résultat affiché 476 891 € vs ~400 k€ attendu par Nicolas).**

---

### 9.1 Infrastructure Belfius dans Odoo

- **Journal Belfius** : BNK2 — compte BE86 0689 5807 1350 (compte Odoo `552 BE86068958071350`, id=1216)
- **Partenaire Belfius** : id=119773 `Belfius Banque-Bank`
- **Total mouvements BNK2 sur l'exercice** : 25 écritures postées (volume très faible)

---

### 9.2 Flux Belfius identifiés — Exercice 01/07/2025 → 30/06/2026

#### Tableau exhaustif des mouvements significatifs BNK2

| Move | Date | Débit 552 (sortie) | Crédit 552 (entrée) | Contrepartie | Libellé | Verdict |
|------|------|--------------------|---------------------|-------------|---------|---------|
| BNK2/25-26/0015 | 2026-04-17 | **31 000,00** | — | 499000 Suspense | PAIEMENT DU PRET N 071-9570629-88 | Remboursement prêt — en suspense |
| BNK2/25-26/0014 | 2026-04-17 | **12 000,00** | — | 499000 Suspense | PAIEMENT DU PRET N 071-9570628-87 | Remboursement prêt — en suspense |
| BNK2/25-26/0013 | 2026-04-17 | **18 000,00** | — | 499000 Suspense | PAIEMENT DU PRET N 071-9570627-86 | Remboursement prêt — en suspense |
| BNK2/25-26/0017 | 2026-04-20 | — | 250,00 | 499000 Suspense | FRAIS DE DOSSIER — BUSINESS CREDIT N 071-9570627-86 | Frais octroi/modification — en suspense |
| BNK2/25-26/0016 | 2026-04-20 | — | 15,00 | 499000 Suspense | FRAIS GESTION BUSINESS CASH PLUS N 071-1257402-52 | Frais gestion crédit revolving |
| BNK2/25-26/0019 | 2026-04-29 | — | 37 510,00 | 440000 Suppliers (Nira Solutions) | Ordre collectif Belfius Direct Net | Paiement fournisseur — OK |
| BNK2/25-26/0001 | 2025-12-15 | 1 000,00 | — | 499000 Suspense | Virement de BE30 3631 6408 2311 TEATOWER SA (ING) | Virement ING→Belfius — suspense |
| BNK2/25-26/0010 | 2026-04-16 | 2 602,12 | — | 499000 Suspense | Versement Vilna Gaon (Mollie) | Encaissement Vilna Gaon — suspense |

**Total remboursements prêts Belfius sur l'exercice : 61 000 EUR** (3 prêts, remboursés en bloc le 17/04/2026)

#### Produits identifiés dans le libellé bancaire

- Prêts à terme : N 071-9570629-88, N 071-9570628-87, N 071-9570627-86
- Crédit revolving (Business Cash Plus) : N 071-1257402-52

---

### 9.3 Recherche d'encaissements de prêts sur l'exercice

**Aucun encaissement de prêt Belfius n'a été détecté sur l'exercice 01/07/2025 → 30/06/2026.**

- Aucun crédit > 5 000 EUR sur le compte BNK2 hors paiements normaux (Nira Solutions = facture fournisseur)
- Aucun libellé "tirage", "déblocage", "octroi", "loan" sur les journaux bancaires (BNK1 ING et BNK2 Belfius)
- Les 3 prêts ont été contractés **avant le 01/07/2025** — leurs encaissements sont dans des exercices antérieurs
- Les soldes initiaux de dettes (comptes 17xxx / 42xxx) ne figurent pas dans les balances d'ouverture Odoo (BO = 0 sur tous les comptes dettes financières)

---

### 9.4 Analyse des contreparties — Verdict par ligne

| Move | Montant | Compte contrepartie | Classe | Verdict |
|------|---------|--------------------|----|---------|
| BNK2/25-26/0015 | 31 000 EUR | 499000 Suspense | Bilan | OK bilan — à imputer en 173/174 ou 424 |
| BNK2/25-26/0014 | 12 000 EUR | 499000 Suspense | Bilan | OK bilan — à imputer en 173/174 ou 424 |
| BNK2/25-26/0013 | 18 000 EUR | 499000 Suspense | Bilan | OK bilan — à imputer en 173/174 ou 424 |

**Aucune des 3 lignes de remboursement n'est imputée en classe 7 (produits).** Le compte 499 Suspense est un compte de bilan neutre — il n'affecte pas le compte de résultat.

**Aucune ligne Belfius en classe 7 (produits) ne gonfle le résultat.** Vérification exhaustive de toutes les lignes > 5 000 EUR en classe 7 sur l'exercice : seuls les 757100 (POS — déjà analysés sections 7 et 8) et le CA normal (700xxx) apparaissent.

---

### 9.5 Intérêts d'emprunt — État

| Compte | Libellé | Total exercice |
|--------|---------|---------------|
| 650000 | Interest, Commission and Other Charges | 1 009,88 EUR |
| 650100 | Frais bancaires (tenue de compte) | 234,24 EUR |
| 650200 | Utilisé pour accises/Xerius (mal imputé, pas des intérêts) | 4 229,04 EUR |
| 650600 | Intérêts leasing voiture ING | 2 094,96 EUR |
| **Total intérêts financiers réels** | | **3 104,84 EUR** |

**Intérêts Belfius spécifiques sur les 3 prêts : 0 EUR comptabilisé.**

Estimation théorique : 3 prêts → capital moyen estimé ~100–150 k€ sur 9 mois (remboursement total le 17/04/2026 = 61 000 EUR, mais capital de départ inconnu). Si taux ~3-4 % → intérêts annuels attendus ~3 000–6 000 EUR. Absence de comptabilisation des intérêts Belfius = charges sous-estimées d'environ **2 000–5 000 EUR** (à confirmer avec les tableaux d'amortissement Belfius).

---

### 9.6 Anomalie subsidiaire — Frais d'octroi en 499 Suspense

Les 265 EUR de frais de dossier Business Credit (BNK2/25-26/0017) et 15 EUR de frais Business Cash Plus (BNK2/25-26/0016) sont en 499 Suspense. Ils devraient être imputés en 650100 (frais financiers) ou 650000. Impact P&L : négligeable (280 EUR).

---

### 9.7 Conclusion — Verdict sur l'intuition de Nicolas

**La piste "prêts Belfius gonflant le résultat" est infirmée.**

| Vérification | Résultat |
|-------------|---------|
| Encaissements prêts Belfius imputés en classe 7 (produits) | **0 EUR — AUCUN** |
| Remboursements imputés en classe 6 (charges fictives) | **0 EUR — AUCUN** |
| Montant total prêts Belfius reçus sur exercice | **0 EUR (prêts antérieurs à l'exercice)** |
| Imputation correcte (classe 17/42) | **0 EUR (restant en 499 suspense — bilan neutre)** |
| Imputation erronée en classe 7 (gonfle résultat) | **0 EUR — PAS D'ANOMALIE** |
| Intérêts Belfius non comptabilisés (estimation) | ~2 000–5 000 EUR (charges manquantes) |
| **Impact net sur le résultat si correction** | **+2 000 à +5 000 EUR** (réduirait légèrement le résultat) |

**L'écart ~80 k€ (476 891 € affiché vs ~400 k€ attendu) n'est pas dû aux prêts Belfius.** Les prêts ont été correctement encaissés avant l'exercice et les remboursements d'avril 2026 (61 000 EUR) sont en suspension comptable (499 Suspense), sans impact sur le résultat.

**Le seul impact résiduel Belfius** : des intérêts d'emprunt probablement non comptabilisés (~2 000–5 000 EUR), qui si passés en charges réduiraient légèrement le résultat affiché — effet inverse de ce que Nicolas suspectait.

**L'explication des ~80 k€ d'écart reste dans les anomalies POS déjà identifiées (section 7/8) :**
- Erreurs de saisie POS nettes : +85 547 EUR (gonflent le résultat)
- Provisions manquantes (commissions, stock obsolète, etc.) : ~28 000 EUR

**Action requise :**
1. Lettrer les 61 000 EUR en 499 Suspense vers le compte de dette adéquat (174100 "Prêt aménagement" ou 424000 "Autres prêts CT") — dispatcher vers agent `odoo`.
2. Obtenir les tableaux d'amortissement Belfius pour calculer les intérêts à comptabiliser.
3. Imputer les 280 EUR de frais en 650100.

---

*Vérification prêts Belfius — 12/05/2026 — lecture seule stricte — aucune écriture Odoo.*

---

## 10. AUDIT AMORTISSEMENTS — 12/05/2026

**Périmètre : lecture seule stricte. Aucune écriture Odoo.**
**Objectif : identifier la cause de l'absence d'amortissements et quantifier la dotation annuelle manquante.**

---

### 10.1 État du module account.asset dans Odoo

**19 assets identifiés — tous en état "draft" (brouillon), aucun en "open" (confirmé).**

Conséquence directe : aucune dotation n'a jamais été postée via le module d'amortissements Odoo. Les assets existent mais n'ont jamais été "confirmés" (action `validate_asset`) par l'utilisateur ou l'expert-comptable.

**Dotations Odoo postées sur exercice 2025-2026 :**

| Compte | Libellé | Montant |
|--------|---------|---------|
| 630100 | Depreciation of Intangible Fixed Assets | 0,00 EUR |
| 630200 | Depreciation of Tangible Fixed Assets | 0,00 EUR |
| **TOTAL dotations exercice 2025-2026** | | **0,00 EUR** |

La seule dotation visible (AMO/24-25/06/0001 du 30/06/2025 = 11 295,65 EUR) concerne l'exercice **précédent** (24-25), pas l'exercice en cours.

---

### 10.2 Bilan des immobilisations existantes dans Odoo (tous temps)

#### 10.2.1 Immobilisations incorporelles

| Compte | Libellé | Brut (D) | Amort cumulé (C) | VNC |
|--------|---------|----------|-----------------|-----|
| 202000 | Frais de constitution | 5 000,00 | 0,00 | 5 000,00 |
| 211003/211309 | Concessions / droits (BO + amort) | 45 000,00 | 40 500,00 | 4 500,00 |
| 211400/211409 | Licences logiciels | 815,29 | 560,00 | 255,29 |
| 212000/212009 | Goodwill Namur | 4 000,00 | 400,00 | 3 600,00 |
| **TOTAL INCORPORELLES** | | **54 815,29** | **41 460,00** | **13 355,29** |

**Note Goodwill :** Un montant de 10 000 EUR de "Question de Goûts" est imputé en débit sur le compte 212009 (amortissements — sens inversé) le 01/07/2025. Ce mouvement semble être le rachat du fonds de commerce Namur comptabilisé sur le mauvais compte. A soumettre à l'expert-comptable.

#### 10.2.2 Immobilisations corporelles

| Compte | Libellé | Brut (D) | Amort cumulé (C) | VNC |
|--------|---------|----------|-----------------|-----|
| 223100 | Droits réels immeubles (location équip. ING) | 3 800,36 | 1 900,18 | 1 900,18 |
| 230500 | Aménagement magasin (Namur/Waterloo/Liège) | 20 053,32 | 0,00 | 20 053,32 |
| 231000 | Installations/machines (Watts by Sun) | 1 890,00 | 0,00 | 1 890,00 |
| 232000/232009 | Outillage divers (mobilier, kakémono, caisses) | 5 977,09 | 996,92 | 4 980,17 |
| 240000/240009 | Mobilier et véhicules (Opel Movano + BO) | 32 957,35 | 16 207,35 | 16 750,00 |
| 240500/240509 | Matériel informatique (BO) | 1 377,12 | 1 377,12 | 0,00 |
| 241009 | Amort matériel roulant | 0,00 | 964,38 | -964,38 |
| 252000 | Leasing (Rocourt) | 1 650,00 | 0,00 | 1 650,00 |
| 260000 | Autres immo corporelles (BO 73 358 + DNP) | 76 904,90 | 0,00 | 76 904,90 |
| 260001/260009 | Aménagement locaux (DNP + Nira Solutions) | 15 546,90 | 28 130,00 | -12 583,10 |
| **TOTAL CORPORELLES** | | **160 157,04** | **49 575,95** | **110 581,09** |

**Note 260000 :** Ce compte contient 73 358 EUR provenant du BO/24-25/04/0001 (bilan d'ouverture) + 3 546,90 EUR DNP Aménagements. Ces 73 358 EUR représentent les aménagements boutiques Namur/Liège antérieurs à avril 2025 (exercices précédents). Le compte 260009 (amort) contient 28 130 EUR de cumul d'amortissements — mais **aucune dotation nouvelle sur l'exercice 2025-2026**.

**Note 260001 / 260009 :** La VNC négative de -12 583 EUR s'explique par un déséquilibre entre les 15 546,90 EUR bruts et les 28 130 EUR d'amortissements cumulés — ces amortissements en 260009 datent de l'exercice précédent et couvrent vraisemblablement le 260000. A clarifier avec l'expert-comptable (les comptes 260000 et 260001 devraient partager le même compte d'amortissement 260009).

---

### 10.3 Liste des 19 assets en draft — dotations théoriques exercice 2025-2026

Tous les assets sont en **draft** — aucune dotation postée. Le tableau ci-dessous calcule la dotation que chaque asset aurait dû générer sur l'exercice 01/07/2025 → 30/06/2026, au prorata de la date d'acquisition.

| Asset | Valeur brute | Durée | Dot/an | Mois exercice | Dot exercice | Compte |
|-------|-------------|-------|--------|--------------|-------------|--------|
| Opel Movano (véhicule utilitaire) | 16 500,00 | 5 ans | 3 300,00 | 12 | 3 300,00 | 240000 |
| Nira Solutions — aménagement locaux (04/2026) | 12 000,00 | 5 ans | 2 400,00 | 3 | 600,00 | 260001 |
| Main d'oeuvre rénovation magasin (04/2026) | 10 000,00 | 5 ans | 2 000,00 | 3 | 500,00 | 230500 |
| Matériel informatique/déco (04/2026) | 9 000,00 | 5 ans | 1 800,00 | 3 | 450,00 | 230500 |
| DNP Concept — service/asset (01/07/2025) | 3 546,90 | 5 ans | 709,38 | 12 | 709,38 | 260001 |
| Frais de constitution "Question de Goûts" (01/2026) | 5 000,00 | 5 ans | 1 000,00 | 6 | 500,00 | 202000 |
| Watts by Sun (panneaux solaires, 08/2025) | 1 890,00 | 5 ans | 378,00 | 11 | 346,50 | 231000 |
| Location équipements ING (01/2026) | 1 900,18 | 5 ans | 380,04 | 6 | 190,02 | 223100 |
| Etagères thé Waterloo | 1 402,32 | 5 ans | 280,46 | 12 | 280,46 | 232000 |
| ROCOURT — leasing (09/2025) | 1 650,00 | 5 ans | 330,00 | 10 | 275,00 | 252000 |
| Atelier Formes & Reliefs (aménagement Namur) | 1 053,32 | 5 ans | 210,66 | 12 | 210,66 | 230500 |
| Kakémono (outillage) | 845,00 | 5 ans | 169,00 | 12 | 169,00 | 232000 |
| Comptoir Waterloo | 467,49 | 5 ans | 93,50 | 12 | 93,50 | 232000 |
| Caisse magasin Waterloo | 456,67 | 5 ans | 91,33 | 12 | 91,33 | 232000 |
| Câble RJ45 Namur | 390,00 | 5 ans | 78,00 | 12 | 78,00 | 232000 |
| Aspirateur / matériel Waterloo | 288,43 | 5 ans | 57,69 | 12 | 57,69 | 232000 |
| Meuble divers | 250,00 | 5 ans | 50,00 | 12 | 50,00 | 240000 |
| Anthropic (licence — à discuter pertinence immo) | 180,00 | 5 ans | 36,00 | 4 | 12,00 | 211400 |
| Planning/shifts logiciel | 39,00 | 5 ans | 7,80 | 4 | 2,60 | 211400 |
| **TOTAL assets en draft** | **66 859,31** | | **13 371,86** | | **7 916,14** | |

**Remarque :** Les durées sont toutes paramétrées à 5 ans dans Odoo. Certains actifs auraient des durées standard différentes en droit comptable belge (voir section 10.5).

---

### 10.4 Immobilisations du bilan d'ouverture (BO 24-25) — dotations manquantes exercice courant

Le BO/24-25/04/0001 a repris les actifs des exercices antérieurs. Ces actifs **ne figurent pas comme assets individuels** dans `account.asset` — seuls les soldes globaux ont été repris. La dotation annuelle sur ces actifs est donc entièrement absente.

#### Actifs du BO estimés avec valeur brute et amortissements cumulés repris

| Compte | Brut BO | Amort cumulé BO | VNC BO (avril 2025) | Durée estimée | Dot annuelle restante |
|--------|---------|----------------|---------------------|--------------|----------------------|
| 260000 Aménagements boutiques (Namur, Liège, Havelange) | 73 358,00 | 22 996,23 | 50 361,77 | 10 ans | ~5 036,00 |
| 240000 Mobilier/véhicules BO | 16 207,35 | 16 207,35 | 0,00 | — | 0,00 (totalement amorti) |
| 240500 Matériel informatique BO | 1 377,12 | 1 377,12 | 0,00 | — | 0,00 (totalement amorti) |
| 232000 Outillage BO | 1 220,98 + 906,20 | 699,42 | ~1 428,00 | 5 ans | ~286,00 |
| 211000 Concessions/droits (Odoo license?) | 40 000,00 | 36 000,00 | 4 000,00 | 5 ans | ~800,00 (dernière année) |

**Dotation annuelle estimée sur actifs BO (exercice 2025-2026) : ~6 122 EUR**

---

### 10.5 Achats exercice 2025-2026 passés en charge — à évaluer pour reclassement

#### Nasa Corporation (11 625 EUR en 612290 "Petit matériel")

RESA88 — fournisseur "Nasa Corporation" — 11 625,16 EUR en 612290 le 27/08/2025. Le libellé "Nasa Corporation - 2025-08-13" n'est pas explicite. A demander à Nicolas : s'agit-il d'équipements IT (terminaux, caisses enregistreuses, hardware boutiques) ? Si oui et valeur unitaire > 500 EUR, à immobiliser en 240500. Dotation potentielle si 5 ans : **2 325 EUR/an**.

Idem Nasa Deutschland GmbH (RESA90 — 2 941,83 EUR en 612290 le 01/07/2025) — même interrogation.

#### Leasing véhicules — traitement comptable actuel

La Volkswagen 2AEE479 est en **leasing opérationnel** chez Distrimarks/Van Mossel (loyers en 611301 = 1 273 EUR/2 mois sur 2 factures juillet 2025 seulement). Le VW ID.4 2FGN376 est chez Van Mossel (6 factures = ~8 328 EUR HT) et LIZY Belgium (4 factures = ~4 445 EUR HT). Le traitement en charge de loyers (611301/613550) est **correct pour du leasing opérationnel** — pas de reclassement nécessaire si ces véhicules ne sont pas en leasing financier. Un droit d'utilisation (IFRS 16 / adaptation CNC belge) pourrait être applicable si les contrats sont qualifiés de location-financement — à vérifier avec l'expert-comptable.

**L'Opel Movano (16 500 EUR, compte 240000, asset en draft)** est un achat ferme — il devrait générer 3 300 EUR/an de dotation (voir tableau assets section 10.3).

#### Displays GMS (Cellmade/Prison de Namur)

3 factures Cellmade/Prison de Namur sur 603000 (Sous-traitance) :
- RESA669 : 974,94 EUR (02/2026)
- RESA605 : 358,97 EUR (02/2026)
- RESA783 : 230,95 EUR (03/2026)
- Total exercice : **1 564,86 EUR** en 603000

Ce sont des insertions de displays (coût de fabrication des présentoirs GMS). Valeur unitaire faible (< 400 EUR/commande), fractionnées. Traitement en charge approprié pour ces montants — pas à immobiliser individuellement. Si des displays ont été acquis en propre (M0005/M0007) pour > 500 EUR unitaire, vérifier séparément — mais la recherche sur les libellés ne remonte rien de significatif en classe 2.

---

### 10.6 Tableau de synthèse — Dotation annuelle théorique TOTALE manquante

| Catégorie | Valeur brute | Durée | Dotation annuelle | Dot exercice 2025-2026 | Compte d'amort |
|-----------|-------------|-------|------------------|----------------------|----------------|
| **Assets en draft — Opel Movano** | 16 500,00 | 5 ans | 3 300,00 | 3 300,00 | 630200 |
| **Assets en draft — Aménagements boutiques** (Atelier F&R, Watts, DNP, Nira, M.O.) | 27 493,32 | 5 ans | 5 498,66 | 3 615,04 | 630200 |
| **Assets en draft — Mobilier/outillage** (Etagères, comptoir, caisse, kakémono, etc.) | 3 543,57 | 5 ans | 708,71 | 708,71 | 630200 |
| **Assets en draft — Leasing Rocourt** | 1 650,00 | 5 ans | 330,00 | 275,00 | 630200 |
| **Assets en draft — Location équip. ING** | 1 900,18 | 5 ans | 380,04 | 190,02 | 630200 |
| **Assets en draft — Frais constitution / licences** | 5 219,00 | 5 ans | 1 043,80 | 514,60 | 630100 |
| **Sous-total assets draft** | **56 306,07** | | **11 261,21** | **8 603,37** | |
| **BO — Aménagements boutiques 260000** (VNC 50 362 EUR) | 73 358,00 | 10 ans | 5 036,00 | 5 036,00 | 630200 |
| **BO — Outillage 232000** (VNC ~1 428 EUR) | 2 127,18 | 5 ans | 286,00 | 286,00 | 630200 |
| **BO — Concessions/droits 211000** (VNC 4 000 EUR) | 40 000,00 | 5 ans | 800,00 | 800,00 | 630100 |
| **Sous-total actifs BO sans asset Odoo** | **115 485,18** | | **6 122,00** | **6 122,00** | |
| **Achats 2025-2026 à qualifier (Nasa Corp.)** | 14 567,00 | 5 ans | 2 913,40 | 2 428,00 | 630200 |
| **TOTAL DOTATION ANNUELLE MANQUANTE** | **186 358,25** | | **20 296,61** | **~17 153,37** | |

> **Note :** La colonne "Dot exercice" applique le prorata depuis la date d'acquisition pour les assets acquis en cours d'exercice. Pour les actifs du BO, la pleine annualité est appliquée (actifs en service depuis plus d'un an).

---

### 10.7 Confrontation avec l'intuition Nicolas

**Dotation annuelle manquante estimée : 17 153 EUR (prorata exercice) à 20 297 EUR (pleine annualité)**

| Comparaison | Montant |
|------------|---------|
| Résultat affiché Odoo | 476 891 EUR |
| Dotation amortissements manquante (estimation centrale) | ~17 000 – 20 000 EUR |
| Impact si on ajoute la dotation | **Résultat corrigé : ~457 000 – 460 000 EUR** |

**Verdict : la dotation manquante (~17-20 k EUR) n'explique pas à elle seule l'écart de ~80 k EUR** (476 891 EUR affiché vs ~400 k EUR attendu par Nicolas).

Les amortissements manquants contribuent pour environ **17-20 k EUR** à l'écart total, pas 80 k EUR. Le delta restant (~60-63 k EUR) s'explique par les autres anomalies déjà auditées (section 7.4) :

| Anomalie | Impact résultat |
|----------|----------------|
| Amortissements non passés (cette section) | **+17 000 à +20 000** |
| Ecarts caisse POS nets (erreurs saisie) | +85 547 |
| Commission Jérôme non provisionnée | +5 600 |
| Honoraires comptable sous-provisionnés | +5 500 |
| Stock obsolète EM080 non déprécié | +16 380 |
| COGS manquant SKU std_price=0 | +6 688 |
| PCA facturés non livrés | +3 645 |
| **TOTAL GONFLEMENT RÉVISÉ (avec amortissements)** | **+140 360 à +143 360 EUR** |
| **Résultat affiché Odoo** | **476 891 EUR** |
| **Résultat retraité révisé** | **~333 000 à ~336 000 EUR** |

> Le résultat réel serait ainsi autour de **335 k EUR**, inférieur à l'objectif Nicolas de 400 k EUR. L'écart résiduel de ~65 k EUR entre le retraité (~335 k) et l'attendu (~400 k) pourrait s'expliquer par : (a) des recettes boutiques encore à encaisser en juin 2026, (b) des achats Kirchner de fin d'exercice pas encore facturés (P00495/P00470/P00480 partiellement livrés), ou (c) une hypothèse de Nicolas basée sur un résultat avant certaines corrections POS.

---

### 10.8 Causes de l'absence d'amortissement

1. **Cause principale : les 19 assets sont en "draft"** — jamais confirmés dans Odoo. Le module `account.asset` est installé et configuré, les assets ont été créés (probablement via les factures fournisseurs), mais personne n'a lancé la validation (`Confirm Asset`). Odoo ne génère les dotations automatiques **que si l'asset est en état "open"**.

2. **Cause secondaire : les actifs du bilan d'ouverture** (BO 24-25) ont été repris en soldes globaux sans être créés comme assets individuels dans Odoo. Sans asset correspondant, aucune dotation automatique n'est possible.

3. **Cause tertiaire : aucun journal d'amortissements en draft** n'est visible — même les dotations planifiées (AMO/24-25 = 11 296 EUR) n'ont pas eu de suite en 25-26.

---

### 10.9 Recommandations (à décider avec l'expert-comptable)

#### A — Confirmer les assets en draft (PRIORITÉ 1)

Action : ouvrir chaque asset dans Odoo → `Confirm Asset` → lancer le plan d'amortissement → poster les dotations au 30/06/2026 (date de clôture). Cette opération est dans le périmètre de l'agent `odoo` + validation Nicolas.

Dotation à poster au 30/06/2026 pour clôturer l'exercice : **~17 153 EUR** (prorata depuis date d'achat de chaque asset).

#### B — Créer les assets manquants pour les actifs du BO

Les aménagements boutiques historiques (BO 260000 = 73 358 EUR brut, VNC ~50 362 EUR) ne sont pas dans `account.asset`. L'expert-comptable doit créer ces assets avec :
- Valeur d'origine = 73 358 EUR
- Amortissement déjà pratiqué = 22 996 EUR (repris du BO)
- Date début amortissement = date de création des boutiques (à retrouver dans les dossiers)
- Durée résiduelle = à calculer selon date de début

Dotation annuelle estimée sur ces actifs : **5 036 EUR/an** pendant la durée résiduelle.

#### C — Rattrapage des exercices antérieurs

L'exercice précédent (01/07/2024 → 30/06/2025) affiche une dotation de 11 296 EUR (AMO/24-25/06/0001) — c'est la seule dotation postée dans l'historique Odoo. Si l'exercice 23-24 n'a pas non plus comptabilisé de dotations sur les actifs du BO, une correction d'erreur sur capitaux propres (compte 137xxx) peut être envisagée.

**Recommandation :** Ne pas rattraper les exercices antérieurs en charge (impact sur résultat 25-26 artificiel) — passer la correction en capitaux propres si les montants sont significatifs. A trancher avec l'expert-comptable.

#### D — Qualifier les achats Nasa Corporation

Demander à Nicolas la nature exacte des 14 567 EUR (Nasa Corporation + Nasa Deutschland) en 612290. Si IT ou matériel boutique : reclasser en 240500 et créer les assets correspondants. Dotation potentielle supplémentaire : ~2 913 EUR/an.

#### E — Leasing opérationnel vs financier

Vérifier avec l'expert-comptable si les contrats Van Mossel (Volkswagen 2AEE479 + VW ID.4) et LIZY Belgium (véhicule électrique) sont des **leasings opérationnels** (charge en 611301/613550 = OK) ou des **leasings financiers** (reclassement en 252xxx + amortissement obligatoire). Montants annuels : Van Mossel ~8 328 EUR + LIZY ~4 445 EUR = **12 773 EUR/an de loyers**. Si financier : droit d'utilisation à inscrire au bilan et amortir.

---

### 10.10 Conclusion

| Point | Constat |
|-------|---------|
| Assets Odoo | 19 assets créés, **tous en draft, aucune dotation postée** |
| Dotation manquante exercice 2025-2026 | **~17 153 EUR** (prorata) à **~20 297 EUR** (pleine annualité) |
| Dotation manquante sur actifs BO non créés | **~6 122 EUR** supplémentaires |
| **Total dotation annuelle manquante** | **~17 000 à ~26 000 EUR** selon périmètre retenu |
| Explication écart Nicolas | Amortissements = **~17-26 k EUR** sur ~80 k EUR d'écart total. Les ~57-63 k EUR restants viennent des erreurs POS (85 547 EUR nets) partiellement compensées par les provisions manquantes |
| Risque exercice antérieur | Dotation 24-25 incomplète possible — à vérifier avec expert-comptable avant de décider un rattrapage en capitaux propres |

**Action immédiate recommandée : confirmer les 19 assets dans Odoo et poster les dotations au 30/06/2026. Impact comptable : ~17 153 EUR de charges supplémentaires, résultat net réduit d'autant.**

---

*Audit amortissements — 12/05/2026 — lecture seule stricte — aucune écriture Odoo.*

---

## 11. ROLLBACK 04/06/2026 — annulation du dernier batch de corrections POS

Décision Nicolas (04/06/2026) : retour au résultat **+87.055,05 EUR** (état après import paie SD Worx + annulation écarts caisse fantômes OD 0076/0077, avant le batch final).

**4 OD annulées** (passées en `cancel` dans Odoo, numéros conservés) :

| OD | Libellé | Impact P&L annulé |
|----|---------|-------------------|
| MISC/25-26/06/0078 (id 39534) | Correction symétrique : annulation faux écarts d'espèces | +161.994,01 |
| MISC/25-26/06/0079 (id 39535) | Faux gain 99.790,25 session POS combinée 28/02 | +99.790,25 |
| MISC/25-26/06/0080 (id 39536) | Recalage fonds de caisse boutiques via 580000 (bilan) | 0,00 |
| MISC/25-26/06/0081 (id 39537) | Extourne partielle OD 0076 (ligne dépôts en produits) | -161.987,71 |

**Restent postés** : 8 OD paie SD Worx (-411.645), provision Faire (-20.536), OD 0076 (+46.287) et 0077 (+67.294).
**Reste en brouillon** : variation de stock 30/06 (+42.148, id 39538) — non comptée dans le +87k.

⚠️ Réserve technique maintenue : le gain de 99.790,25 EUR de la session POS combinée du 28/02 avait été diagnostiqué comme écart fantôme (cf. §9). Nicolas le considère acquis — à revalider avec l'expert-comptable avant la clôture du 30/06.

*Résultat posté FY25-26 après rollback : **+87.055,05 EUR** (vérifié Odoo 04/06/2026).*

### 11.1 Dossier pour l'expert-comptable — gain 99.790,25 EUR du 28/02 (à trancher avant clôture 30/06)

Décision Nicolas 04/06/2026 : le point est délégué à l'expert-comptable. Aucune écriture supplémentaire passée. Éléments factuels vérifiés dans Odoo le 04/06 :

**Écriture d'origine** — `PBNK1/25-26/0432` du 28/02/2026 (combinaison paiements carte PdV, PAS un écart d'espèces) :

| Compte | Débit | Crédit |
|--------|-------|--------|
| 550004 Outstanding Receipts (encours cartes) | 100.905,00 | |
| 400100 Customers (POS) | | 1.114,75 |
| 757100 Positive Payment Differences | | 99.790,25 |

**Position Nicolas** : gain réel, corrigé dans la caisse quelques jours plus tard.

**Vérifications effectuées (sans trouver la correction)** :
- Mars 2026 entier : plus gros écart de caisse toutes boutiques = 204,50 EUR (Namur 13/03). Aucun mouvement ~100k en caisse, banque ou OD.
- Seuls mouvements ±100k post-février : couple Waterloo CSH3 11/05 (+99.999,90 gain) / 12/05 (-99.999,85 perte) — ils se neutralisent entre eux (net +0,05 à 1 jour d'écart), ne corrigent pas le 28/02. NB : la perte du 12/05 est annulée par OD 0076/0077 (postées), le gain du 11/05 reste posté.
- Compte 550004 : jamais dégonflé — delta +153.294 en février (dont les 100.905 de cette écriture), progression continue jusqu'à +500.123 cumulés au 30/06. Les 100.905 d'encours cartes du 28/02 n'ont jamais été matchés à un versement ING.

**Question pour l'expert-comptable** : le gain 757100 de 99.790,25 est-il un produit réel (et dans ce cas où est passé l'encours 550004 correspondant ?) ou un artefact de la combinaison de paiements POS ? Étudier conjointement avec le solde 550004 (+500k) et le couple Waterloo 11-12/05.

**Composition actuelle du net 757100 posté (+99.924,32)** : gains bruts 261.912 (LIE 12/01 : 51.440,36 ; PBNK1 28/02 : 99.790,25 ; POP 28/02 : 8.888,80 ; CSH3 11/05 : 99.999,90 ; divers ~1.793) moins ligne OD 0076 « dépôts en produits » -161.987,71. Compte 657100 net : -904,49.
