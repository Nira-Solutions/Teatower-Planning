# Recap de Cloture — Juin 2026 / Q2 / FY25-26
**Arrete au 30 juin 2026 — LECTURE SEULE**
*Document genere le 30/06/2026 — source Odoo XML-RPC, ecritures etat "posted"*
*Aucune ecriture n'a ete creee ou modifiee dans le cadre de ce document*

---

## SYNTHESE EXECUTIVE

| Indicateur | Valeur Odoo brute | Retraitement | Valeur corrigee |
|---|---|---|---|
| Resultat FY25-26 (brut Odoo) | **-13.652 EUR** | -99.999,90 (faux gain 11/05) | **-113.652 EUR** |
| Creances clients (hors POS/Tea Touch) | 158.599 EUR | — | 158.599 EUR |
| Creances "Tea Tree Caisse" (faux impayes POS) | 129.882 EUR | A debloquer | NON-REELLE |
| Creance Tea Touch (faillite) | 77.660 EUR | Perte probable | A PROVISIONNER |
| Fournisseurs a payer | 552.550 EUR | — | urgent: 457.198 echus |
| Stock (SVL Odoo) | 323.229 EUR | Ecart 340000 = 87.246 EUR | A INVENTORIER |
| Position TVA FY25-26 | -11.885 EUR | — | a recuperer |
| Lignes bancaires non reconciliees | 178 lignes | — | a lettrer |

**Alertes prioritaires clôture :**
1. Faux gain CSH3/25-26/0254 (11/05/2026) = **99.999,90 EUR toujours actif** sur 757100 → gonfle le resultat de ~100k → a neutraliser (hors de ce rapport, accord Nicolas requis)
2. "Tea Tree Caisse" 129.882 EUR en creances = faux impayes POS bloques — ecriture de deblocage requise
3. Creance Tea Touch 77.660 EUR + C/C 489030 = 41.000 EUR + loyers impayes ~32.500 EUR → exposition brute ~151k → perte sur creance a chiffrer et comptabiliser FY25-26
4. Fournisseurs echus >30j = **374.043 EUR** dont 341.141 EUR sans partner (a identifier)
5. Stock SVL (323k) vs compte 340000 bilan (236k) = ecart +87.246 EUR a expliquer
6. Caisse Cash Odoo 570001 = **160.582 EUR** — solde anormalement eleve, caisses physiques a reconcilier

---

## 1. RESULTAT P&L

### 1.1 Tableau synthetique

| Periode | Produits Classe 7 | Charges Classe 6 | Resultat brut Odoo | Nb lignes |
|---|---|---|---|---|
| Juin 2026 | -291.037 EUR (1) | +205.725 EUR (2) | -85.312 EUR | 10.047 |
| Q2 avril-juin 2026 | +115.595 EUR | -252.172 EUR | -136.577 EUR | 29.783 |
| FY25-26 cumul | +1.835.663 EUR | -1.849.315 EUR | **-13.652 EUR** | 119.640 |

*(1) Juin : total classe 7 NET DEBIT car les OD ventilation canaux (700000 debite, 700300/600/500 credites) et les reversals faux gains 757100 (net -348k en juin) faussent le mois pris isolement.*
*(2) Juin : total classe 6 NET CREDIT car extournes ONSS juin (46.130 EUR) + 657100 net +275k.*

> **Avertissement lecture juin/Q2** : les ecritures de regularisation annuelle (ventilation canaux OD, reversals faux gains, extournes ONSS) ont ete majoritairement passees en juin, ce qui rend le P&L mensuel et trimestriel non representatif de l'activite de la periode. Seul le cumul FY25-26 est fiable.

---

### 1.2 Resultat FY25-26 - Detail Produits (Classe 7)

| Compte | Libelle | Solde FY25-26 |
|---|---|---|
| 700006 | Recettes magasins 6% | +653.671 EUR |
| 700600 | Ventes GMS (Grande Distribution) | +333.197 EUR |
| 700300 | Ventes Horeca | +309.327 EUR |
| 700100 | Ventes e-commerce BE | +243.357 EUR |
| 700500 | Ventes revendeurs | +211.450 EUR |
| 700021 | Recettes magasins 21% | +88.105 EUR |
| **757100** | **Positive Payment Differences (POS)** | **-86.400 EUR (!)** |
| 700000 | Sales Belgium Trade Goods (residuel ventil.) | +33.653 EUR |
| 700102 | Ventes e-commerce FR | +25.759 EUR |
| 700700 | Ventes Institutions / Corporate | +17.977 EUR |
| 743001/100/901 | ATN / Cheques-repas / AIP | +4.710 EUR |
| 700104/105 | Ventes e-commerce NL/LU | +2.003 EUR |
| 708xxx | Remises accordees (net) | -2.437 EUR |
| **TOTAL PRODUITS** | | **+1.835.663 EUR** |

**Note 757100 :** Le compte 757100 a un solde NET DEBIT de -86.400 EUR sur l'annee (total credits 520.709 EUR, total debits 607.109 EUR). Cela signifie que les annulations de faux gains ont depasse les faux gains crees. Cependant, un faux gain de 99.999,90 EUR reste non neutralise (voir section 1.4).

---

### 1.3 Resultat FY25-26 - Detail Charges (Classe 6) - Top 20

| Compte | Libelle | Solde FY25-26 |
|---|---|---|
| 600000 | Achats matieres premieres | -414.305 EUR |
| 620200 | Remunerations employes | -274.275 EUR |
| 604024 | Achats marchandises TT boutiques | -225.631 EUR |
| 613290 | Honoraires de gestion | -177.690 EUR |
| **657100** | **Negative Payment Differences (POS)** | **+159.185 EUR (!)** |
| 620300 | Remunerations ouvriers | -94.557 EUR |
| 611121 | Loyer magasin et bureau Liege | -92.038 EUR |
| 611125 | Loyer entrepot Baillonville | -58.391 EUR |
| 621200 | Cotisations patronales employes | -56.780 EUR |
| 614140 | Frais de transport | -56.649 EUR |
| 616600 | Frais de marketing | -54.424 EUR |
| 611123 | Loyer magasin Waterloo | -53.310 EUR |
| 625000 | Pecule de vacances employes | -37.399 EUR |
| 612130 | Electricite | -36.165 EUR |
| 617000 | Personnel interimaire | -35.887 EUR |
| 621300 | Cotisations patronales ouvriers | -33.302 EUR |
| 611120 | Refacturation loyer | -28.712 EUR |
| 613240 | Honoraires Adrianne et Nicolas | -26.744 EUR |
| 611122 | Loyer magasin Namur | -18.338 EUR |
| 612290 | Petit materiel / outillage | -18.006 EUR |
| **TOTAL CHARGES** | | **-1.849.315 EUR** |

**Note 657100 :** Meme phenomene miroir de 757100. Le solde net +159.185 EUR (credit > debit) en classe 6 reduit les charges. Ces deux comptes POS additiones ont un impact net de +72.785 EUR sur le resultat (ils ameliorent le resultat apparent). Sans eux, le resultat serait de -13.652 - 72.785 = **-86.437 EUR**.

---

### 1.4 Retraitement Faux Gains POS (compte 757100)

**Historique des faux gains identifies FY25-26 et leur statut :**

| Date | Piece | Journal | Montant | Statut |
|---|---|---|---|---|
| 28/02/2026 | PBNK1/25-26/0432 | ING BE30 | 99.790,25 EUR | **ANNULE** (BNK1/5830 — 30/06) |
| 28/02/2026 | POP/25-26/0058 | Caisse POP-UP | 8.888,80 EUR | **ANNULE** (POP/0063 — 30/06) |
| 12/01/2026 | LIE/25-26/0110 | Espece Liege | 51.440,36 EUR | **ANNULE** (LIE/0363 — 30/06) |
| **11/05/2026** | **CSH3/25-26/0254** | **Caisse Waterloo** | **99.999,90 EUR** | **NON ANNULE — actif** |
| 21/06/2026 | CSH3/25-26/0291 | Caisse Waterloo | 70.077,15 EUR | **ANNULE** (MISC/06/0114 — 21/06) |
| 21/06/2026 | PBNK1/25-26/0725 | ING BE30 | 26.468,73 EUR | **ANNULE** (MISC/06/0114 — 21/06) + reversal BNK1/5831 30/06 (double — a verifier) |

**Consequence :**
- Seul **CSH3/25-26/0254** (11/05/2026, Caisse Waterloo, 99.999,90 EUR) est encore actif et gonfle les produits.
- Aucun reversal trouve pour cette piece au 30/06/2026.
- Point d'attention PBNK1/25-26/0725 : semble annule deux fois (MISC + reversal BNK1) — ecart de 26.468,73 EUR a verifier en sens inverse.

**Resultat retraite (estimation) :**

| | Montant |
|---|---|
| Resultat brut Odoo FY25-26 | -13.652 EUR |
| Retraitement : CSH3/25-26/0254 non neutralise (-) | -99.999,90 EUR |
| **Resultat retraite hors faux gain** | **-113.652 EUR** |

Note : Ce retraitement est indicatif. La neutralisation effective necessite un accord explicite de Nicolas et une ecriture comptable dediee.

---

## 2. BALANCE AGEE CLIENTS

### 2.1 Vraies factures (547 lignes, comptes 400xxx)

| Anciennete | Montant |
|---|---|
| Non echu | +79.400 EUR |
| Echu 1-30j | +37.165 EUR |
| Echu 31-60j | +17.259 EUR |
| Echu 61-90j | +7.068 EUR |
| **Echu >90j** | **+225.249 EUR** |
| **TOTAL** | **+366.141 EUR** |

### 2.2 Principaux debiteurs (vraies factures)

| Debiteur | Solde | Commentaire |
|---|---|---|
| **Tea Tree Caisse** | **+129.882 EUR** | FAUX IMPAYES POS — clients deja payes, bloques (cf. §2.3) |
| **Tea Touch** | **+77.660 EUR** | Creance faillite — a deprecier (cf. §2.4) |
| Delhaize Le Lion S.A | +33.844 EUR | GMS — en cours |
| Carrefour Belgium | +27.472 EUR | GMS — en cours |
| The Torrefactory Project | +5.353 EUR | |
| Cafes Delahaut | +3.300 EUR | |
| Smartbox Group | +3.075 EUR | |
| Urban Therapy | +2.654 EUR | |
| Va.S.Co | +2.650 EUR | |
| VENTE-PRIVEE.COM | +2.470 EUR | |
| Brasserie Maziers | +2.425 EUR | |
| Distrimarks S.A | +2.179 EUR | |
| Centrale Intermarche | +1.673 EUR | |
| Mix F&B SRL | +1.655 EUR | |
| Cafes Preko | +1.549 EUR | |
| Autres | ~52.000 EUR | |

**Creances reelles hors POS et Tea Touch : 366.141 - 129.882 - 77.660 = 158.599 EUR**

**Relances recommandees (echu >30j, hors POS et Tea Touch) :**
- Delhaize Le Lion et Carrefour Belgium : contacter les services comptables fournisseurs
- Creances >90j (net hors cas speciaux) : ~17.707 EUR — verifier factures open ou en litige

### 2.3 Faux impayes POS — "Tea Tree Caisse" (129.882 EUR)

Ces 129.882 EUR correspondent aux factures POS INV/2025/04135-04142 (PAY091-098) encore en etat "open" en Odoo alors que les paiements existent (state=paid sans move_id). Ce sont des faux impayes identifies (etapes 1+2 faites le 10/06/26 : 6 doublons annules + 55k lettres). Les ~130k restants sont BLOQUES et necessitent une intervention en devmode ou une OD bilan specifique. **Ne pas comptabiliser comme creance reelle.**

### 2.4 Creance Tea Touch (exposition totale)

| Compte | Solde | Nature |
|---|---|---|
| 400000 Clients | +77.660 EUR | Factures impayees |
| 611121/122 Loyers | +32.500 EUR | Loyers impayes Liege/Namur |
| 489030 C/C Tea Touch | +41.000 EUR | Compte courant |
| 550001 Bank | -5.000 EUR | Depot |
| 700000 / 451000 | -76.764 EUR | Ventes + TVA (netted) |
| **Exposition brute totale** | **~145.396 EUR** | |

Faillite Tea Touch prononcee en novembre 2025. La depreciation (compte 634xxx) doit etre comptabilisee en FY25-26 apres accord Nicolas et expert-comptable.

---

## 3. BALANCE AGEE FOURNISSEURS

### 3.1 Tableau

| Anciennete | Montant |
|---|---|
| Non echu | +95.351 EUR |
| Echu 1-7j | +38.265 EUR |
| Echu 8-30j | +44.890 EUR |
| **Echu >30j** | **+374.043 EUR** |
| **TOTAL A PAYER** | **+552.550 EUR** |

**Urgence J+7 (echu <= 7j) : 38.265 EUR**
**Urgence J+30 (echu <= 30j) : 83.155 EUR**

### 3.2 Top fournisseurs a payer

| Fournisseur | Solde | Commentaire |
|---|---|---|
| **Inconnu (sans partner)** | **+341.141 EUR** | ALERTE : lignes payable sans partner associe — a investiguer |
| Kirchner Fischer & Co GmbH | +125.759 EUR | Fournisseur principal matiere premiere |
| SD Worx Secretariat Social | +105.138 EUR | ONSS + prestations — inclut residuel post-extourne |
| Noe Nature S.A | +27.726 EUR | |
| Fanchon Sa | +20.600 EUR | |
| Tea Touch | +18.630 EUR | Dette envers Tea Touch (compensation possible avec creance) |
| Fortamps | +18.000 EUR | |
| Bevergam | +13.800 EUR | |
| Jean Noel Tilman | +11.660 EUR | |
| Duo Tableware Bvba | +9.220 EUR | |
| Nira Solutions | +6.737 EUR | |
| Creagency | +4.525 EUR | |
| Baloise Belgium | +4.012 EUR | |
| NOWJOBS NV | +3.843 EUR | |
| RESA S.A. | +3.652 EUR | |

**Points d'attention :**
- **341.141 EUR sans partner** : ces lignes sont problematiques pour la cloture. Peut etre des OD ou des banques non lettrees postees sur compte payable sans partner. A investiguer avant depot des comptes annuels.
- **SD Worx 105.138 EUR** : meme apres les extournes doublon (46.130 EUR), un solde reste. Verifier si les RESA de mai 2026 sont tous solds et si le PP est compris.
- **Tea Touch 18.630 EUR** : la dette peut etre compensee avec la creance client 77.660 EUR sous reserve des regles juridiques (liquidateur).

---

## 4. ETAT DU LETTRAGE BANCAIRE

### 4.1 Lignes non reconciliees au 30/06/2026

| Journal | Nb lignes | Montant net | Commentaire |
|---|---|---|---|
| ING BE30 3631 6408 2311 | 68 | -21.757 EUR | Principal compte courant operationnel |
| Cash (Caisse generale / Namur) | 35 | -26.047 EUR | Solde negatif anormal |
| Caisse Waterloo | 23 | -10.030 EUR | Solde negatif anormal |
| Espece Liege bis | 22 | -16.261 EUR | Solde negatif anormal |
| BE86068958071350 (Belfius) | 20 | -1.331 EUR | Compte credit professionnel |
| Caisse POP-UP | 8 | -1.656 EUR | |
| Caisse Rocourt | 1 | +735 EUR | |
| Especes | 1 | +316 EUR | |
| **TOTAL** | **178** | **-76.071 EUR** | |

### 4.2 Soldes comptes de tresorerie Odoo (au 30/06/2026)

| Compte | Libelle | Solde Odoo |
|---|---|---|
| 570001 | Cash | +160.582 EUR |
| 551102 | Paiements a recevoir Mollie | +288.474 EUR |
| 550001 | Bank | +16.628 EUR |
| 5500010 | ING | +1.900 EUR |
| 550004 | Outstanding Receipts | +8.443 EUR |
| 550007 | Outstanding Payments | +25.000 EUR |
| 571000 | Caisse Liege | +11.021 EUR |
| 572000 | Caisse Namur | +9.617 EUR |
| 572300 | Caisse Waterloo | +653 EUR |
| 552 | BE86068958071350 (Belfius) | -1.523 EUR |

**Points d'attention :**
- **570001 Cash = 160.582 EUR** : solde tres eleve pour une caisse physique. Inclut probablement les mouvements POS non lettres de toutes les boutiques. A reconcilier avec les encaissements physiques.
- **551102 Mollie = 288.474 EUR** : compte de transit Mollie pour paiements e-commerce + cartes POS. Ce montant doit etre reconcilie avec les extraits de paiement Mollie. Si non verse en banque, c'est de la tresorerie en transit.
- Les caisses boutiques (Liege +11k, Namur +9.6k, Waterloo +653) semblent coherentes mais a confronter aux encaissements physiques.

### 4.3 Residuel ING/Belfius (memoire Teatower)

La memoire indique ~156 lignes ING + 15 Belfius residuelles apres le chantier lettrage juin. Le releve au 30/06 montre 68 ING + 20 Belfius = **88 lignes restantes**. Progress realisé mais travail inacheve. Les lignes recentes (juin 2026) incluent : domiciliations, virements Carrefour/Belgradis, frais divers — plupart identifiables.

---

## 5. ANOMALIE ONSS/PP — SD WORX (613310)

### Extournes passees en juin 2026

| Date | Piece | Credit 613310 | Libelle |
|---|---|---|---|
| 18/06/2026 | MISC/25-26/06/0112 | +19.904,19 EUR | Extourne doublon ONSS+PP residuel SD Worx mars-mai 2026 |
| 30/06/2026 | MISC/25-26/06/0094 | +26.225,98 EUR | Annulation charge doublon ONSS+PP SD Worx (7 RESA mars-avril) |
| **Total extourne** | | **+46.130,17 EUR** | **Deja inclus dans le P&L FY25-26** |

Ces extournes sont **deja postees** et integrees dans le resultat calcule ci-dessus. Le doublon RESA detecte (<=43.789 EUR mentionne en memoire) a bien ete corrige et depasse (46.130 EUR recuperes).

**Solde SD Worx restant a payer : 105.138 EUR** (comprend ONSS courant + prestations + possible PP residuel). A verifier ligne par ligne avec les factures SD Worx.

---

## 6. POSITION TVA

### 6.1 TVA Q2 avril-juin 2026

| | Montant |
|---|---|
| TVA collectee (451xxx) | +32.240 EUR |
| TVA deductible (411xxx) | +44.569 EUR |
| **Position Q2** | **-12.329 EUR (a recuperer)** |

### 6.2 TVA FY25-26 cumul

| | Montant |
|---|---|
| TVA collectee (451xxx) | +187.889 EUR |
| TVA deductible (411xxx) | +199.773 EUR |
| **Position FY25-26** | **-11.885 EUR (a recuperer)** |

**Note :** La position TVA negative (a recuperer) sur l'annee entiere est coherente avec le fait que les achats (matiere premiere + marchandises) representent une base de TVA deductible importante. Verifier que les declarations trimestrielles deposees correspondent a ces mouvements Odoo — la reconciliation avec les declarations TVA deposees est a effectuer avec l'expert-comptable.

---

## 7. VALORISATION STOCK AU 30/06/2026

### 7.1 Valorisation SVL (Stock Valuation Layer Odoo)

| Categorie | Valeur (EUR) | Commentaire |
|---|---|---|
| Echantillons | 80.815 | A verifier — representatif? |
| Non categorise (All) | 42.682 | Produits sans categorie — a assigner |
| Composante | 34.181 | Ingredients / emballages en vrac |
| Accessoires | 32.775 | Theières, mugs, ustensiles |
| Fruits | 27.348 | Fruits secs / infusions |
| The Vert | 21.233 | |
| Matiere Premiere | 19.028 | Thes en vrac non transformes |
| The Noir | 11.922 | |
| Plantes | 10.806 | |
| Horeca | 9.658 | Produits canal Horeca |
| Rooibos | 8.664 | |
| Epices | 3.670 | |
| The Blanc | 3.477 | |
| Mate | 3.317 | |
| Coffret | 2.650 | |
| Thes glaces | 1.986 | |
| Noel 2025 | 1.836 | ALERTE : stock invendu Noel 2025 |
| Oolong | 1.855 | |
| Cafe | 1.407 | |
| Autres | ~4.919 | |
| **TOTAL SVL** | **323.229 EUR** | |

### 7.2 Ecart SVL vs Compte comptable 340000

| Source | Montant |
|---|---|
| Stock SVL Odoo (valorisation mouvements) | 323.229 EUR |
| Compte 340000 bilan (marchandises achetees pour revente) | 235.983 EUR |
| **Ecart** | **+87.246 EUR** |

Cet ecart est a analyser avant cloture. Il peut resulter de :
- Produits valorises via d'autres comptes que 340000 (ex : 300000 MP, 310000 produits finis)
- Ajustements manuels non reflechis dans les deux systemes
- Methode de valorisation (AVCO vs prix achat facture)

**L'inventaire physique au 30/06/2026 est indispensable** pour la cloture annuelle et devra etre compare au SVL Odoo. Le stock est un poste cle qui peut ameliorer le resultat (activation du stock final en fin d'exercice selon plan comptable belge, schema A).

**Alerte "Noel 2025" : 1.836 EUR** — stock invendu de la collection Noel 2025 reste valorise. Verifier obsolescence (depreciation a evaluer).

---

## 8. POINTS DE CLOTURE — RECOMMANDATIONS

*Ces elements sont des recommandations a valider avec Nicolas et l'expert-comptable. RIEN n'est poste.*

### 8.1 Ecritures obligatoires (bloquantes pour les comptes annuels)

| # | Sujet | Impact P&L estime | Priorite |
|---|---|---|---|
| A | Neutralisation faux gain CSH3/25-26/0254 (11/05/2026, 757100) | -99.999,90 EUR | CRITIQUE |
| B | Deblocage faux impayes POS "Tea Tree Caisse" (129.882 EUR) | Bilan uniquement | CRITIQUE |
| C | Depreciation creance Tea Touch (clients 77.660 + C/C 41.000 + loyers 32.500) | -130.000 a -151.160 EUR | CRITIQUE |
| D | Inventaire physique stock et ajustement SVL vs 340000 (+87.246 EUR) | Variable | OBLIGATOIRE |
| E | Identification des 341.141 EUR payable sans partner | Bilan | OBLIGATOIRE |

### 8.2 Ecritures estimatives (provisions et regularisations)

| # | Sujet | Estimation | Commentaire |
|---|---|---|---|
| F | Amortissements manquants (si pas encore passes via plan d'amort automatique) | A verifier | Comptes 630/630200 — verifier avec expert |
| G | Provision 13e mois / conges payes non pris | A evaluer | Calcul RH |
| H | Charges a imputer (factures recues apres 30/06 mais rattachables FY25-26) | A evaluer | Revue des charges recues en juillet |
| I | Regularisation TVA (si declarations trimestrielles divergent d'Odoo) | A calculer | Rapprocher declas officielles |
| J | Traitement C/C 489030 Tea Touch (41.000 EUR) | -41.000 EUR max | Selon decision actionnaire |
| K | Stock Noel 2025 invendu (1.836 EUR) | -1.836 EUR max | Si obsolete |
| L | SD Worx : verifier mai 2026 inclus dans l'extourne MISC/06/0112 | 0 - 15.000 EUR | Doublons mai non couverts par les OD |

### 8.3 Points de controle (non monetaires)

- Reconciliation declarations TVA deposees vs Odoo (positions -11.885 EUR a recuperer)
- Rapprochement Mollie 551102 (288.474 EUR) avec extraits de paiement
- Rapprochement caisse Cash 570001 (160.582 EUR) avec encaissements physiques
- Investigation lignes payable sans partner (341.141 EUR)
- Verification double annulation PBNK1/25-26/0725 (26.468 EUR)
- Reconciliation compte 340000 vs SVL : identifier les autres comptes stock utilises (300xxx, 310xxx)

### 8.4 Synthese impact P&L si toutes les ecritures de cloture sont passees

| Scenario | Resultat |
|---|---|
| Resultat brut Odoo | -13.652 EUR |
| + Neutralisation faux gain (A) | -113.652 EUR |
| + Depreciation Tea Touch minimale (C, clients seuls) | -191.312 EUR |
| + Depreciation Tea Touch maximale (C, clients + C/C + loyers) | -264.812 EUR |
| + Stock inventaire (D, selon inventaire physique — potentiel +42k si stock reel > SVL) | variable |
| **Fourchette resultat apres cloture** | **[-265k ; -150k] EUR** |

---

## 9. ANNEXES

### 9.1 Comptes actionnaires et emprunts (489xxx/174xxx)

| Compte | Solde | Nature |
|---|---|---|
| 489000 Sundry Amounts Payable | -19.990 EUR | Avances/prêts a rembourser |
| 489030 C/C Tea Touch | -41.000 EUR | Compte courant Tea Touch (creancier) |
| 174320 Emprunt Belfius 071-9570629-88 | -31.000 EUR | Emprunt bancaire en cours |

### 9.2 Rappel contexte OD annulees (memoire)

- OD 0078-0081 : annulees (memoire juin 2026)
- OD 39813 / 39826 (ventilation canaux) : postees 09/06 sans impact resultat global
- MISC/25-26/06/0094 (ONSS extourne) + MISC/25-26/06/0112 : postees et incluses

### 9.3 Flux POS a reparer (hors perimetre de ce rapport)

Le flux POS (cause racine des faux gains 757100) doit etre repare dans Odoo pour eviter la recidive en FY26-27. Ce point est hors perimetre compta (releve de l'agent odoo/config).

---

*Document etabli par agent Compta — Teatower SA — 30/06/2026*
*Source : Odoo XML-RPC, base tsc-be-tea-tree-main-18515272, ecritures etat "posted" uniquement*
*Aucune modification des donnees Odoo n'a ete effectuee dans le cadre de ce rapport*
