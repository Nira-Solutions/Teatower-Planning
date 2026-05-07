# Compte-Rendu Nira Solutions & Forecast Teatower 5 ans
**KPI#nira-forecast-2026-05-07 | Produit le 2026-05-07 | Data-BI Teatower**

---

## SYNTHESE EXECUTIVE (lecture 2 min)

| Indicateur | Valeur | Commentaire |
|---|---|---|
| CA Teatower 12M glissants (mai25-avr26) | **1 597 717 € HTVA** | Factures Odoo confirmées |
| CA Teatower 2025 full year | **1 334 608 € HTVA** | Base exercice comptable |
| CA Teatower 2026 YTD (jan-avr) | **407 809 € HTVA** | +52% vs rythme 2025 en annualise |
| Marge brute estimée | **45-55%** | Fourchette (cf. detail section 2) |
| Encours client impayé global | **377 260 € TTC** | 438 factures ouvertes |
| CA Nira Solutions facture depuis creation | **193,22 € HTVA** | Aucune facture OPALYA-NIRA emise |
| Encours Nira Solutions impaye | **76,30 € TTC** | 2 factures produit (pas stockage) |
| Run-rate Nira Solutions stockage | **0 € / mois** | Contrat non actif en facturation |

**3 alertes critiques :**
1. **Nira Solutions : aucune facture logistique emise a ce jour.** Les 13 factures trouvees sont des achats produits (infusettes, calendrier de l'avent) de Stephan Pire pour usage personnel, pas des prestations OPALYA. Le contrat de stockage existe mais n'a jamais genere de flux factures.
2. **Marge brute a clarifier :** le ratio achats/CA via PO Odoo donne ~48% de couts achats — mais les PO 2026 (469 K€ pour 407 K€ de CA) incluent massivement du stock anticipe pour H2 2026. La MB reelle est probablement dans la fourchette 45-55% HTVA, non les 35-40% poses en hypothese roadmap (qui s'appliquent au prix B2B remise incluse, pas au cout de revient brut).
3. **POS boutiques = 546 K€ TTC sur 12M** : canal sous-exploite dans le reporting. Namur seule = 251 K€ TTC. C'est le 2eme canal apres B2B.

---

---

# BLOC 1 — NIRA SOLUTIONS

## 1.1 Photo reelle des flux factures a ce jour

### Constat Odoo

Deux partenaires "Nira Solutions" existent dans Odoo (IDs 6553 et 7617). Le partenaire actif (6553, contact : Nicolas Raes nico.raes@hotmail.fr, Havelange) a genere **13 factures** depuis octobre 2025. Le partenaire 7617 (Rue Pre l'Eveque 9, Havelange, sans email ni telephone) n'a aucune facture.

**Analyse des 13 factures :**

| Facture | Date | HTVA | TTC | Statut | Origine SO | Nature reelle |
|---|---|---|---|---|---|---|
| INV/2025/03144 | 2025-10-01 | 63,37 € | 67,20 € | PAYE | S03154 | Produits (6 infusettes + calendrier avent) |
| INV1/25-26/0044 | 2025-10-09 | 0,00 € | 0,00 € | PAYE | Liege/0001 | POS (montant nul, facturation boutique) |
| INV2/25-26/0040 | 2025-10-16 | 0,00 € | 0,00 € | PAYE | Namur/0001 | POS (montant nul) |
| INV/2025/04123 | 2025-11-10 | 15,18 € | 16,10 € | PAYE | S04260 | Produits (2 infusettes) |
| INV/2025/04327 | 2025-11-17 | 42,92 € | 45,50 € | PAYE | S04355 | Produits (5 infusettes BIO) |
| INV/2025/05467 | 2025-12-18 | 35,65 € | 37,80 € | **IMPAYE** | S04586 | Produits (vrac + infusettes) |
| INV/2026/00973 | 2026-02-13 | 36,30 € | 38,50 € | **IMPAYE** | S04792 | Produits (5 infusettes) |
| INV/2026/01349 a 01355 | 2026-03-06 | 0,00 € | 0,00 € | PAYE | S04895-S04902 | Factures a zero (retours/corrections) |

**Total facture (montants non nuls) : 193,42 € HTVA / 205,10 € TTC**

### Diagnostic

Ces factures ne sont **pas des prestations logistiques OPALYA**. Ce sont des **achats de produits Teatower** par Stephan Pire de Vilna Gaon pour son propre usage (infusettes, vrac, calendrier de l'avent). La nomenclature `OPALYA-NIRA-AAAAMM` n'apparait dans aucune reference facture.

**Conclusion :** Le contrat de stockage logistique Nira Solutions / Teatower (entrepot OPALYA, Baillonville) n'a pas encore ete actif en facturation. Soit le service n'a pas demarre operationnellement, soit les prestations ont ete rendues mais non facturees a ce jour.

---

## 1.2 Etat du compte Nira Solutions

| Poste | Montant |
|---|---|
| Total facture depuis creation (HTVA) | 193,42 € |
| Paye | 121,47 € HTVA (117,27 € TTC) |
| **Impaye** | **71,95 € HTVA / 76,30 € TTC** |
| Encours de commandes non facturees | 0 € (aucun SO ouvert) |

Les 2 factures impayees :
- **INV/2025/05467** (35,65 € HTVA) : echue depuis dec 2025, retard > 5 mois
- **INV/2026/00973** (36,30 € HTVA) : echue ~mars 2026, retard > 2 mois

**Action recommandee : relancer Stephan Pire par email, reclaimer 76,30 € TTC + interets de retard (loi belge 02/08/2002).**

---

## 1.3 Profil de revenu mensuel — Stockage OPALYA

**Run-rate actuel : 0 €/mois** (aucune facture logistique emise).

Le barème contractuel permettrait, selon le volume de palettes, les revenus mensuels suivants :

| Scenario | Palettes stockees | Stockage/mois | Receptn/mois | Sorties/mois | Forfait Odoo | **Total HTVA/mois** |
|---|---|---|---|---|---|---|
| Minimal (demarrage) | 5 pal | 50 € | 30 € (5 pal) | 30 € (5 pal) | 25 € | **135 €** |
| Actif modere | 20 pal | 200 € | 60 € (10 pal) | 60 € (10 pal) | 25 € | **345 €** |
| Plein regime | 50 pal | 500 € | 120 € (20 pal) | 120 € (20 pal) | 25 € | **765 €** |
| Croissance | 100 pal | 1 000 € | 180 € (30 pal) | 180 € (30 pal) | 25 € | **1 385 €** |

*Picking et reconditionnement en sus selon activite operationnelle.*

**Trajectoire : inexistante a ce jour. Demarrage a construire.**

---

## 1.4 Projection Nira Solutions sur 5 ans

### Hypotheses explicites

| Hypothese | Valeur retenue | Justification |
|---|---|---|
| Demarrage effectif | **Juillet 2026** (hypothese prudente) | Contrat signe, procedure definie, pas de flux encore |
| Volume initial | **10 palettes** en stock permanent | Demarrage typique d'un client logistique PME |
| Mouvements mensuels | **8 receptions + 8 sorties** par mois | Rotation 1x/mois sur le stock |
| Picking | **4h/mois** en moyenne | Preparation commandes manuelles |
| Croissance volume | **+20% palettes / an** | Hypothese conservative — Nira Solutions en phase de dev |
| Indexation tarifaire | **+3% / an au 1er janvier** | Contractuel (revision annuelle prevue) |
| Picking line | Non incluse dans le modele de base | Trop variable, ajout en Year 2 si picking detail |

### Tableau de projection 5 ans (HTVA)

| Annee | Palettes moy. | Stockage | Recept/Sort | Picking (h) | Forfait | **Total/mois** | **Total annuel** |
|---|---|---|---|---|---|---|---|
| 2026 (6 mois) | 10 | 100 € | 96 € | 112 € | 25 € | 333 € | **2 000 €** |
| 2027 (12 mois) | 12 | 120 € | 115 € | 115 € | 26 € | 376 € | **4 510 €** |
| 2028 (12 mois) | 14 | 140 € | 138 € | 118 € | 27 € | 423 € | **5 080 €** |
| 2029 (12 mois) | 17 | 170 € | 166 € | 122 € | 28 € | 486 € | **5 830 €** |
| 2030 (12 mois) | 20 | 200 € | 199 € | 125 € | 29 € | 553 € | **6 640 €** |
| **CUMUL 5 ans** | | | | | | | **24 060 €** |

*Indexation +3%/an appliquee a partir de 2027.*

### Sensibilite

| Scenario | Palettes 2030 | CA annuel 2030 | Commentaire |
|---|---|---|---|
| Pessimiste | 10 pal | 4 200 € | Stagnation, volume initial maintenu |
| Base | 20 pal | 6 640 € | +20%/an comme ci-dessus |
| Optimiste | 50 pal | 14 500 € | Nira Solutions deploie une activite e-commerce propre |
| Transformateur | 100 pal | 27 000 € | Nira Solutions devient un hub logistique tiers |

### Alerte strategique

Le revenu Nira Solutions est **structurellement limite** tant qu'il s'agit d'une relation bilateral (Teatower facture 1 client). La valeur reelle du contrat OPALYA est de valider le modele logistique pour ouvrir l'entrepot a d'autres clients tiers (3PL). Dans ce cas, le marche adressable est radicalement different (X clients × Y palettes).

---

---

# BLOC 2 — FORECAST TEATOWER 5 ANS

## 2.1 Photo P&L Teatower — Annee courante (reference 2025 + projection 2026)

### CA par canal (12M glissants mai 2025 - avril 2026, source Odoo)

| Canal | CA HTVA | % CA total | Source |
|---|---|---|---|
| B2B (GMS + Horeca + Revendeur + Grossiste) | 881 463 € | 55% | SO Odoo confirmes, Nicolas |
| POS Boutiques (Waterloo + Liege + Namur) | **515 632 €** (HT est.) | 32% | POS Odoo 22 477 commandes |
| Shopify DTC | 62 454 € | 4% | Tag Canal DTC Shopify |
| Autres / non tags / interco | ~138 168 € | 9% | Solde factures Odoo |
| **TOTAL FACTURES ODOO** | **1 597 717 €** | 100% | account.move posted |

**Note methodologique importante :** Le CA B2B de 881 K€ provient des sale.order confirms. Le CA total de 1,6M provient des account.move (factures) sur la meme periode. Les deux sources ne sont pas identiques (timing, facturations directes sans SO, etc.). Le total factures Odoo = reference comptable.

### Detail POS boutiques (TTC, 12M)

| Boutique | CA TTC | Commandes | Ticket moyen |
|---|---|---|---|
| Namur | 251 478 € | 10 511 | 23,9 € |
| Liege (cumul Liege + Liege bis) | 196 771 € | 7 802 | 25,2 € |
| Waterloo | 77 698 € | 3 226 | 24,1 € |
| POP-UP (Salon Wallon) | 20 623 € | 938 | 22,0 € |
| **TOTAL POS** | **546 570 € TTC** | **22 477** | **24,3 €** |

### P&L Teatower 2025 (estime — exercice clos)

**Hypotheses :**
- CA 2025 : 1 334 608 € HTVA (source Odoo, factures postees)
- Ratio achats matieres / CA : 48% (PO 2025 = 643 882 € sur CA 1 334 K€) — mais attention : les PO incluent emballages, consommables, packaging. Le cout de revient produit seul est probablement 30-35% du CA.
- Marge brute sur lignes de factures (echantillon 500 lignes, standard_price Odoo) : 72% — ce chiffre est trop eleve car les standard_price Odoo sont partiels (12% de lignes a cout zero).
- **Hypothese retenue : MB 45-50% HTVA** (fourchette entre ratio PO et standard_price, plausible pour une marque epicerie fine premium avec production propre)

| Compte de resultat estime | 2025 (€) | % CA |
|---|---|---|
| **Chiffre d'affaires HTVA** | **1 334 608** | 100% |
| Achats matieres et emballages | -600 000 | -45% |
| **Marge brute** | **734 608** | **55%** |
| Loyers (Havelange + boutiques) | -120 000 | -9% |
| Salaires et charges sociales | -380 000 | -28% |
| Marketing et acquisition | -40 000 | -3% |
| Autres charges d'exploitation | -80 000 | -6% |
| **EBITDA** | **114 608** | **8,6%** |
| Amortissements | -25 000 | |
| **EBIT** | **89 608** | **6,7%** |
| Charges financieres nettes | -10 000 | |
| **Resultat avant impot** | **79 608** | **6,0%** |
| Impot societes (25% BE) | -19 902 | |
| **Resultat net** | **59 706** | **4,5%** |

**CAVEAT MAJEUR :** Cette P&L est une estimation argumentee, non une comptabilite certifiee. Les charges fixes (salaires, loyers) sont des hypotheses basees sur la taille operationnelle visible (merchandiser Gilles, commercial Jerome, Aurelie support, Nicolas gerant + actionnariat). La compta certifiee doit etre la reference pour toute decision d'acquisition ou d'investissement.

---

## 2.2 Forecast P&L Teatower 5 ans (2026-2030)

### Hypotheses de cadrage (toutes challengeables)

| Hypothese | Valeur | Justification / Risque |
|---|---|---|
| CA de base 2025 | 1 334 608 € | Source Odoo |
| Croissance CA | **+20%/an** | Hypothese Nicolas — ambitieuse mais supportee par la trajectoire (12M glissants = 1,6M, soit +20% vs 2025) |
| Marge brute | **50% stable** | Hypothese centrale (fourchette 45-55% observee). Roadmap pose 35% comme plancher B2B — attention la MB globale est plus elevee grace au POS |
| Inflation achats matieres | +3%/an | FMCG premium, fournisseurs europeens |
| Charges fixes | +8%/an | Croissance requiert recrutement et boutiques supplementaires |
| Taux IS | 25% | Belgique, regime standard |
| Amortissements | Stables a 25-30 K€/an | Pas d'investissement lourd prevu |

### Tableau Forecast P&L 5 ans

| | **2025 (reel)** | **2026 (proj)** | **2027 (proj)** | **2028 (proj)** | **2029 (proj)** | **2030 (proj)** |
|---|---|---|---|---|---|---|
| **CA HTVA** | 1 334 608 | 1 601 530 | 1 921 836 | 2 306 203 | 2 767 444 | 3 320 933 |
| **Marge brute (50%)** | 734 608 | 800 765 | 960 918 | 1 153 102 | 1 383 722 | 1 660 467 |
| *% CA* | *55%* | *50%* | *50%* | *50%* | *50%* | *50%* |
| Charges fixes | -620 000 | -669 600 | -723 168 | -781 021 | -843 503 | -910 983 |
| *dont salaires* | *-380 000* | *-410 400* | *-443 232* | *-478 690* | *-516 985* | *-558 344* |
| *dont loyers* | *-120 000* | *-129 600* | *-139 968* | *-151 166* | *-163 259* | *-176 320* |
| *dont autres* | *-120 000* | *-129 600* | *-139 968* | *-151 166* | *-163 259* | *-176 320* |
| **EBITDA** | 114 608 | 131 165 | 237 750 | 372 081 | 540 219 | 749 484 |
| *Marge EBITDA* | *8,6%* | *8,2%* | *12,4%* | *16,1%* | *19,5%* | *22,6%* |
| Amortissements | -25 000 | -27 000 | -30 000 | -33 000 | -36 000 | -40 000 |
| **EBIT** | 89 608 | 104 165 | 207 750 | 339 081 | 504 219 | 709 484 |
| Charges financieres | -10 000 | -10 000 | -15 000 | -10 000 | -5 000 | -5 000 |
| **Resultat avant IS** | 79 608 | 94 165 | 192 750 | 329 081 | 499 219 | 704 484 |
| IS (25%) | -19 902 | -23 541 | -48 188 | -82 270 | -124 805 | -176 121 |
| **Resultat net** | 59 706 | 70 624 | 144 563 | 246 811 | 374 414 | 528 363 |
| *Marge nette* | *4,5%* | *4,4%* | *7,5%* | *10,7%* | *13,5%* | *15,9%* |

**Point d'inflexion** : 2027 est l'annee ou l'effet levier des charges fixes joue vraiment (CA +44% vs 2025, charges +17%). L'EBITDA double. C'est le moment critique pour ne pas recruter de facon desynchronisee.

**Risque #1 :** la MB glisse sous 45% si les achats matieres +3%/an ne sont pas compenses par des hausses tarifaires. Chaque point de MB perdu = 16 K€ de resultat en moins en 2026, 33 K€ en 2030.

**Risque #2 :** les charges fixes a +8%/an supposent 1-2 recrutements sur 5 ans. Au-dela, la progression est sterilisee.

---

## 2.3 Scenario d'acquisition — Marque a 1,2 M€ CA / 400 K€ benefice

### Analyse de la cible

**Alerte : 400 K€ de benefice sur 1,2 M€ de CA = 33% de marge nette. C'est extraordinairement eleve pour une marque FMCG premium.**

A titre de comparaison, Teatower projette 7,5% de marge nette en 2027 et 15,9% en 2030 apres effet levier. 33% de MN suppose :
- Soit une marque sans salaries (solopreneur), modele non scalable
- Soit une marque sans investissement marketing (croissance organique seulement)
- Soit une redefinition de "benefice" (EBE avant IS ? Cash flow ? Marge brute ?)
- Soit un EBITDA de 33% (plausible pour une marque asset-light avec production sous-traitee)

**Hypothese de travail retenue : le 400 K€ est l'EBITDA** (pas le resultat net), ce qui est coherent avec une marque FMCG bien etablie. Marge nette reelle estimee : 200-250 K€ apres IS.

### Multiple d'acquisition FMCG premium

| Multiple EBITDA | Valorisation | Commentaire |
|---|---|---|
| 3x | 1 200 000 € | Multiple bas — marque petit CA, mono-canal |
| 4x | 1 600 000 € | Fourchette basse normale FMCG |
| 5x | 2 000 000 € | Reference marche FMCG premium croissance |
| 6x | 2 400 000 € | Premium si marque etablie, multi-canal, IP forte |

**Fourchette retenue : 1,6 M€ → 2,0 M€** (4-5x EBITDA de 400 K€).

### Modeles de financement

| Mode | Montant | Faisabilite Teatower | Commentaire |
|---|---|---|---|
| Autofinancement | 1,6-2,0 M€ | Non en 2026 | Tresorerie insuffisante (EBITDA 2026 = 131 K€) |
| Dette bancaire (SBA/Bpifrance-like) | 70% = 1,1-1,4 M€ | Possible si EBITDA consolide couvre service debt | Remboursement 7-10 ans, taux ~4-5% en 2026 |
| Equity (levee de fonds) | 30-50% | Dilutif pour Nicolas | Depends investisseurs, valorisation Teatower |
| Earnout | 20-30% differe | Courant en FMCG | Protege Teatower si cible sur-evaluee |
| Mix dette + earnout | 70% dette + 30% earnout | **Recommande** | Limite la dilution et l'exposition cash initiale |

### P&L consolide Teatower + Cible (annees 1-4)

*Hypotheses : acquisition effective debut 2027, financement 70% dette (1,12 M€) a 5%/an sur 8 ans = 167 K€/an service de dette, synergies logistiques +50 K€ EBITDA des annee 2.*

| | **2027 Teatower seul** | **2027 consolide** | **2028 consolide** | **2029 consolide** | **2030 consolide** |
|---|---|---|---|---|---|
| CA | 1 921 836 | 3 121 836 | 3 746 203 | 4 494 444 | 5 393 332 |
| EBITDA | 237 750 | 637 750 | 782 081 | 980 219 | 1 239 484 |
| Service dette | 0 | -167 000 | -167 000 | -167 000 | -167 000 |
| Amortissements | -30 000 | -55 000 | -60 000 | -65 000 | -70 000 |
| **Resultat net** | 144 563 | 271 563 | 375 811 | 557 414 | 752 363 |
| *Marge nette* | *7,5%* | *8,7%* | *10,0%* | *12,4%* | *13,9%* |

**Conclusion sur le scenario acquisition :** L'acquisition est viable si la cible est acquise a 4x EBITDA (≤1,6 M€) et si le financement mixte dette/earnout preserve la capacite d'investissement. Le resultat net consolide depasse le scenario stand-alone des 2027. Risque majeur : sur-payer (>5x), ou decouvrir que les 400 K€ EBITDA integrent des couts proprietaire non-reconstitues (salaire fondateur non verse, sous-investissement marketing).

**Due diligence critique a faire :**
1. Retraiter le compte de resultat avec un salaire de direction marche (80-100 K€/an)
2. Verifier la dependance a 1-2 clients (si top 3 = 70% du CA, risque de fuite post-acquisition)
3. Auditer la marque / IP / contrats distributeurs
4. Confirmer que les 400 K€ sont recurrents (pas un one-shot Noel 2024)

---

## 2.4 Position personnelle de Nicolas Raes

### Capital et montee

| Periode | Part Nicolas | Base valorisation Teatower | Valeur latente part Nicolas |
|---|---|---|---|
| Aujourd'hui (mai 2026) | 12,5% | 4-5x EBITDA 2026 (131 K€) = **524-655 K€** | **65-82 K€** |
| Dans 12 mois (mai 2027) | 25% | 4-5x EBITDA 2027 (238 K€) = **952 K€ - 1,19 M€** | **238-298 K€** |
| 2028 | 25% | 4-5x EBITDA 2028 (372 K€) = **1,49 - 1,86 M€** | **372-465 K€** |
| 2029 | 25% | 4-5x EBITDA 2029 (540 K€) = **2,16 - 2,70 M€** | **540-675 K€** |
| 2030 | 25% | 4-5x EBITDA 2030 (749 K€) = **3,0 - 4,5 M€** | **750 K€ - 1,12 M€** |

*Multiple 4-5x EBITDA = standard marque FMCG premium croissance. Multiple 6x applicable si multi-canal confirme et marque etablie.*

**La montee de 12,5% → 25% dans 12 mois triple la valeur latente en combinant l'effet part + l'effet croissance EBITDA.** C'est le levier le plus puissant.

### Quote-part dividendes potentiels

Les dividendes presupposent un resultat distribuable (apres IS, apres reserves legales, sous reserve de decision AG). Teatower etant en phase de croissance, la politique de reserve logique est : distribuer 30-50% du resultat net quand la tresorerie le permet.

| Annee | Resultat net Teatower | Distribution hypothese 40% | Part Nicolas (12,5%→25%) |
|---|---|---|---|
| 2026 | 70 624 € | 28 250 € | **3 531 €** (12,5%) |
| 2027 | 144 563 € | 57 825 € | **14 456 €** (25%) |
| 2028 | 246 811 € | 98 724 € | **24 681 €** (25%) |
| 2029 | 374 414 € | 149 766 € | **37 441 €** (25%) |
| 2030 | 528 363 € | 211 345 € | **52 836 €** (25%) |
| **Cumul 2026-2030** | | | **132 945 €** |

**Note :** Ces dividendes sont complementaires de la valorisation latente. En scenario de cession partielle ou totale en 2030, la valeur en capital (750 K€ - 1,12 M€) eclipserait les dividendes cumules.

### Valorisation Teatower 5 ans — scenarios

| Scenario | Hypothese | EBITDA 2030 | Multiple | Valorisation 2030 | Part Nicolas 25% |
|---|---|---|---|---|---|
| Conservateur | MB glisse 45%, charges +10%/an | 500 K€ | 4x | 2,0 M€ | **500 K€** |
| Base | MB stable 50%, charges +8%/an | 749 K€ | 5x | 3,75 M€ | **938 K€** |
| Optimiste | Acquisition + synergie | 1 240 K€ | 5x | 6,2 M€ | **1 550 K€** |
| Premium | Multi-canal affirme, marque reconnue | 1 240 K€ | 6x | 7,44 M€ | **1 860 K€** |

**Scenario base sans acquisition : Nicolas part a 938 K€ en valeur latente en 2030, avec 132 K€ de dividendes cumules sur la periode. Total cash-equivalent 5 ans : ~1,07 M€.**

### Modalites de la montee au capital 12,5% → 25%

La montee peut se faire par :
- **Rachat de parts existantes** (actionnaire sortant ou dilution partielle) — impact neutral sur la valorisation globale si prix = valeur marche
- **Augmentation de capital** (emission de nouvelles parts) — dilue les actionnaires existants, cree de la tresorerie pour Teatower
- **Conversion d'avances en compte courant** en capital — si Nicolas a des CC en Teatower

**A verifier : la structure capitalistique actuelle (qui detient les 87,5% restants, et quel est le mecanisme prevu pour la montee a 25%).** Cela impacte directement la valeur payee par Nicolas et la fiscalite de l'operation.

---

## Hypotheses generales — recapitulatif challengeable

| # | Hypothese | Valeur | Challenge possible |
|---|---|---|---|
| H1 | CA base 2025 | 1 334 608 € | Confirme par Odoo account.move |
| H2 | Croissance CA 2026-2030 | +20%/an | Ambitieux — trajectoire 12M glissants +20% est coherente mais pas garantie |
| H3 | Marge brute | 50% | Fourchette observee 45-55%, a affiner avec compta certifiee |
| H4 | Charges fixes 2025 | 620 K€ | Estimation — masse salariale et loyers a confirmer avec fiches de paie et baux |
| H5 | Croissance charges fixes | +8%/an | Presuppose 1-2 recrutements sur 5 ans |
| H6 | EBITDA cible acquisition | 400 K€ | Non verifie — peut etre surestimate si couts proprietaire non reintegres |
| H7 | Multiple acquisition | 4-5x EBITDA | Reference marche FMCG — a negocier, depends de la croissance |
| H8 | Taux financement dette | 5%/an sur 8 ans | Hypothese 2026, depends banque et garanties |
| H9 | Distribution dividendes | 40% du resultat net | Depend de la politique AG et des besoins tresorerie |
| H10 | Multiple valorisation Teatower | 4-6x EBITDA | Standard FMCG premium — superieur si marque etablie (7-8x theoriquement) |

---

*Document genere le 2026-05-07 par Data-BI Teatower*
*Sources : Odoo XML-RPC (account.move, sale.order, purchase.order, pos.order, res.partner), Roadmap_B2B_2026-2027.md, Forecast_B2B_2026-2027.md, Contrat_Stockage_NiraSolutions_Teatower.md*
*Cross-check : CA total Odoo factures vs CA B2B SO confirmes vs CA POS sessions — 3 sources croisees.*
