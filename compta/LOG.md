# LOG Compta Teatower

## 2026-06-11 — OD BROUILLON variation de stock FY25-26 (id=40092)

| Champ | Valeur |
|---|---|
| Type | OD brouillon (state=draft, NON POSTÉ) |
| Journal | MISC (id=11) |
| Date | 30/06/2026 |
| Débit | 340000 Marchandises — 64.180,45 EUR |
| Crédit | 609400 Variation stocks marchandises — 64.180,45 EUR |
| Écart brut quant vs 340000 | 65.171,29 EUR |
| Écarté (coûts aberrants) | 990,84 EUR (Gyokuro MP coût>PV + Miel HH005) |
| Montant défendable retenu | 64.180,45 EUR |
| Statut | EN ATTENTE validation expert-comptable (>5.000 EUR) |

## 2026-06-11 — RESTAURATION RESA812 (Shyfter, id=35935)

| Champ | Avant | Apres |
|---|---|---|
| state | cancel | posted |
| payment_state | not_paid | not_paid |
| amount_total | 47,19 EUR | 47,19 EUR |
| ref | 2026040554 | 2026040554 |
| partner | Shyfter SA (#121991) | Shyfter SA (#121991) |
| invoice_date | 2026-04-10 | 2026-04-10 |
| invoice_date_due | 2026-05-10 | 2026-05-10 |

Methode : button_draft (cancel->draft) + action_post (draft->posted). Aucun paiement ni lettrage existant (not_paid), pas de reversal lie (reversed_entry_id=False). Move lines apres repost : 611129 D:39,00 / 411000 D:8,19 / 440000 C:47,19 — coheres avec TVA 21%. Aucune ecriture parasite creee aujourd'hui pour Shyfter. Les 4 autres annulations du lot (Shopify transport + Google Cloud) restent inchangees.


## 2026-06-10 — TACHE 1/2 LOT KIRCHNER/NASA/SINAS — SUITE RAPPROCHEMENT BANCAIRE — is_reconciled flags + write-offs + brouillons

### TACHE 1 : Clôture flags bancaires 3 lignes Kirchner (BNK 18130 / 18733 / 18090)

**Methode :** activation reconcile=True sur compte 499000 (id=221), action_undo_reconciliation + account.move.line.reconcile sur les paires ML 499000 (BNK <-> OD).
Pour BNK18090, l'undo avait defait les lettrages 440000 -> rebuild complet du move 36792 (reset draft + 3 lignes 440000+499000 + post + reconcile chaque ligne).

| BNK | Move bancaire | OD | is_reconciled apres | Factures restaurees |
|-----|--------------|-----|--------------------|--------------------|
| 18130 | BNK1/25-26/4829 (id=36892, poster) | MISC/25-26/04/0069 (id=39982) | True | RESA733 paid |
| 18733 | BNK1/25-26/5298 (id=38796) | MISC/25-26/05/0124 (id=39983) | True | RESA730+RESA729 inchanges |
| 18090 | BNK1/25-26/4798 (id=36792, rebuild) | MISC/25-26/04/0070 (id=39984) | True | RESA506 paid, RESA735 paid, RESA734 partial (160,56 ouvert) |

### TACHE 2 : Lettrage avec write-off BNK 17722 + BNK 18834

| BNK | Move bancaire | Facture | Ecart | Write-off compte | is_reconciled |
|-----|--------------|---------|-------|-----------------|--------------|
| 17722 | BNK1/25-26/4508 (id=35816) | RESA462 (4.360,69, Mount Everest) | 5,39 EUR | 657100 D=5,39 | True |
| 18834 | BNK1/25-26/5378 (id=39194) | RESA743 (1.198,65, Kirchner) | 0,74 EUR | 657100 C=0,74 (dans BNK move) | True |

**Impact P&L Tache 2 :** -6,13 EUR total (5,39 + 0,74 en 657100 Negative Payment Differences). Residuel = -67.016 - 6,13 = -67.022 EUR (negligeable, autorise par instruction Nicolas).

**Note BNK 18834 :** match par montant uniquement (ref RGK26-01990 introuvable dans Odoo). A confirmer si Nicolas identifie une autre facture.

### TACHE 3 : Brouillons Sinas + NASA

**SINAS GmbH (id=6421, Allemagne, Intra-Community FP=3) :**

| ID Odoo | Ref fournisseur | Montant | Date | BNK paiement | TVA |
|---------|----------------|---------|------|-------------|-----|
| 39990 | 197610 | 2.648,58 EUR | 2026-02-18 | BNK16715 | 0% (autoliquidation intracom) |
| 39991 | 199235 | 839,37 EUR | 2026-04-10 | BNK17832 | 0% (autoliquidation intracom) |
| 39992 | 199587 | 2.514,77 EUR | 2026-04-24 | BNK18129 | 0% (autoliquidation intracom) |

Compte charge : 600000 (Purchases of Raw Materials). State=draft. A poster apres validation Nicolas.

**NASA Corporation (id=6409, Japon, hors-UE) :**

| ID Odoo | Ref | Montant | Date | BNK | TVA |
|---------|-----|---------|------|-----|-----|
| 39993 | SOJP202604-0054 | 5.419,82 EUR (978.100 JPY) | 2026-04-23 | BNK18116 | 0% sur facture (TVA import via doc douanier) |

State=draft. A poster apres validation Nicolas.

**Recommandations NASA :**
1. RESA825 (id=36192, state=posted, amount=0 EUR, payment_state=paid, ref=SOJP202604-0054) = placeholder a corriger ou annuler (wizard reversal) avant de poster le brouillon id=39993 pour eviter doublon de ref.
2. TVA import (6% ou 21% sur valeur CIF) a saisir depuis le document douanier/agent en douane, pas depuis la facture fournisseur — compte TVA import deductible separate.
3. BNK 16571 (-5.161,89 EUR, 907.750 JPY, 12/02/2026) vs RESA581 (4.921,00 EUR, non_paid) : ecart 240,89 EUR = probablement frais de change/commission banque JPY. NE PAS LETTRER avant confirmation Nicolas. Apres confirmation : lettrage RESA581 + 240,89 EUR en 654000 ou 657000 (frais financiers change).

**Impact P&L Tache 3 :** 0 EUR (tous en brouillon, aucun poste).

### TACHE 4 : Lignes en suspens — docs a fournir

| BNK | Montant | Date | Communication | Statut |
|-----|---------|------|--------------|--------|
| 18022 (BNK1/25-26/4757) | -2.000,54 EUR | 2026-04-20 | Kirchner SEPA, ref "See Docket from 16.04.26" | Facture originale du 16/04 a fournir par Nicolas |
| 18525 (BNK1/25-26/5140) | -1.029,74 EUR | 2026-05-15 | Kirchner SEPA, ref RGK26-01561 | Ref non trouvee dans Odoo — facture originale a fournir |

### Compteurs apres ce lot

- Lignes ING lettrées dans ce lot : 5 (BNK 18130, 18733, 18090, 17722, 18834)
- Lignes ING non reconciliees restantes : 122 (vs 127 avant ce lot)
- Lignes en suspens actif (brouillons Sinas/NASA) : 4 BNK (16715, 17832, 18129, 18116) + 1 NASA ecart (16571)
- Lignes sans doc (tache 4) : 2 BNK (18022, 18525)
- Compte 499000 : reconcile=True (active pour permettre les lettrages 499000)

---

## 2026-06-11 — ANNULATION 5 DOUBLONS FOURNISSEURS — IMPACT P&L +2.428,12 EUR

**Contexte :** Audit P&L FY25-26. 5 factures fournisseurs en double identifiees et validees par Nicolas pour annulation.
Procedure : button_draft + button_cancel sur les doublons non payes. Aucune ecriture bancaire touchee.

| Annulee | ID Odoo | Fournisseur | Ref fournisseur | Date | Montant TTC | Conservee | Critere |
|---------|---------|-------------|----------------|------|-------------|-----------|---------|
| RESA539 | 30768 | Shopify | Bill #460671442 | 2025-12-17 | 777,43 EUR | RESA412 (id=27476) | RESA412 anterieure (id plus petit), les 2 non payees |
| RESA534 | 30718 | Shopify | Bill #474838643 | 2026-01-16 | 607,11 EUR | RESA484 (id=29800) | RESA484 anterieure, les 2 non payees |
| RESA752 | 34465 | Shopify | Bill #503279326 | 2026-03-17 | 628,47 EUR | RESA742 (id=34275) | RESA742 anterieure, les 2 non payees |
| RESA572 | 31080 | Google Cloud | 5473148878 | 2026-01-31 | 367,92 EUR | RESA525 (id=31002) | RESA525 anterieure, les 2 non payees |
| RESA812 | 35935 | Shyfter SA | 2026040554 | 2026-04-10 | 47,19 EUR | RESA824 (id=35945) | RESA824 est payee/lettree (payment=paid) |

**Impact P&L :** +2.428,12 EUR (reduction charges 6xxxxx/614140/611129).
**Etat final :** 5 factures state=cancel | 5 factures conservees state=posted.
**Aucun double paiement detecte** — toutes les factures annulees etaient not_paid/non lettrées.

---

## 2026-06-10 — LETTRAGE KIRCHNER NETS — BNK 18130 / 18733 / 18090 — NEUTRE P&L (hors 0,01 EUR)

**Contexte :** Rapprochement bancaire ING (BNK1) — lignes Kirchner, Fischer & Co GmbH (#7195) avec suspense 499000.
Méthode : OD MISC (reclassement 499000 -> 440000) + account.partial.reconcile sur les lignes 440000 et 499000.

| BNK | Date | Move BNK | Montant | Facture(s) lettrée(s) | Partiel lettré | Résiduel ouvert | Impact P&L |
|-----|------|----------|---------|----------------------|----------------|-----------------|-----------|
| 18130 | 2026-04-24 | BNK1/25-26/4829 | -1.184,86 | RESA733 (1.184,85) | intégral | 0,00 (soldée) | 0,01 EUR 657100 (write-off autorisé) |
| 18733 | 2026-05-26 | BNK1/25-26/5298 | -8.706,97 | RESA730 (6.821,21 intégral) + RESA729 (1.885,76 partiel) | RESA729: 1.885,76/2.025,90 | 140,14 EUR ouvert RESA729 | 0 |
| 18090 | 2026-04-22 | BNK1/25-26/4798 | -18.451,00 (part suspense 5.944,74) | RESA734 (5.944,74 partiel sur 6.105,30) | partiel | 160,56 EUR ouvert RESA734 | 0 |

**OD créées (postées) :**
- `MISC/25-26/04/0069` (id=39982) — BNK18130/RESA733 — 440000 D=1.184,85 + 657100 D=0,01 / 499000 C=1.184,86
- `MISC/25-26/05/0124` (id=39983) — BNK18733/RESA730+RESA729 — 440000 D=6.821,21+1.885,76 / 499000 C=8.706,97
- `MISC/25-26/04/0070` (id=39984) — BNK18090/RESA734 — 440000 D=5.944,74 / 499000 C=5.944,74

**Partial reconciles créés :** PR13988/13989 (CAS1), PR13990/13991/13992 (CAS2), PR13993/13994 (CAS3).
**Résultat P&L :** neutre sauf 0,01 EUR en 657100 (Negative Payment Differences) — autorisé par instruction.
**Factures non touchées :** RESA735 (déjà payée), RESA506 (déjà payée).
**Cas réservés intacts :** BNK17722, BNK18022, BNK18525, BNK18834.
**Base résultat :** -67.016 EUR inchangée (hors 0,01 EUR négligeable).

---

## 2026-06-10 — TACHE 1 : LETTRAGE DOUBLE-SALAIRE VERRIEST + VECCHIA — 1.518,83 EUR — NEUTRE P&L

**Contexte :** Estelle Verriest et Fiona Vecchia (employées) ont rendu leur double-salaire d'avril 2026.
Même traitement que la cohorte Logan/Tholet/Thibaut/Carlier (avril 2026).

**Méthode :** Modification des moves bancaires de la stmt line (remplacement 499000 Suspense -> 455000 Rémunération).

| Stmt line | Move bancaire | Employée | Montant | Compte imputé | Impact P&L |
|-----------|--------------|---------|---------|--------------|-----------|
| BNK1/25-26/4522 (id=17741) | BNK1/25-26/4522 (id=35881) | Estelle Verriest (#113334) | 975,53 EUR | Dr 550001 / Cr 455000 | 0 |
| BNK1/25-26/4526 (id=17745) | BNK1/25-26/4526 (id=35885) | Fiona Vecchia (#107544) | 543,30 EUR | Dr 550001 / Cr 455000 | 0 |

- Résultat P&L = INCHANGÉ. 455000 = compte bilan (classe 4 rémunérations dues).
- Compteur : 171 -> 169 lignes non lettrées (BNK1: 154, BNK2: 15).

---

## 2026-06-10 — TACHE 2 Phase B : IMPUTATION CHEQUES-REPAS + SMARTBOX — 27 LIGNES — 1.866,04 EUR — NEUTRE P&L

**Contexte :** Suite diagnostic Phase A. Decision Nicolas : imputer les 27 lignes bancaires Edenred/Pluxee/Monizze/Smartbox sur comptes d'attente dedies (classe 5), sans toucher les comptes 6/7.

**Compte 580004 cree :** id=1225 — "Bons cadeaux Smartbox" — account_type=asset_current — modele 580003.

**Tableau des 27 lignes imputees :**

| BSL ID | Date | Type | Montant EUR | Compte impute | Boutique |
|--------|------|------|-------------|--------------|---------|
| 17368 | 2026-03-19 | MONIZZE | 57,83 | 580003 | non identifiable |
| 17605 | 2026-03-31 | SMARTBOX | 199,08 | 580004 | non identifiable |
| 17607 | 2026-03-31 | MONIZZE | 43,38 | 580003 | non identifiable |
| 17650 | 2026-04-01 | EDENRED | 21,62 | 580003 | non identifiable |
| 17755 | 2026-04-08 | EDENRED | 21,43 | 580003 | non identifiable |
| 17758 | 2026-04-08 | MONIZZE | 21,60 | 580003 | non identifiable |
| 17762 | 2026-04-08 | EDENRED | 9,34 | 580003 | non identifiable |
| 17763 | 2026-04-08 | EDENRED | 31,45 | 580003 | non identifiable |
| 17801 | 2026-04-09 | PLUXEE | 65,58 | 580003 | non identifiable |
| 17841 | 2026-04-10 | PLUXEE | 14,29 | 580003 | non identifiable |
| 17923 | 2026-04-14 | SMARTBOX | 290,08 | 580004 | non identifiable |
| 18070 | 2026-04-21 | MONIZZE | 73,22 | 580003 | non identifiable |
| 18082 | 2026-04-22 | PLUXEE | 28,53 | 580003 | non identifiable |
| 18135 | 2026-04-24 | PLUXEE | 43,65 | 580003 | non identifiable |
| 18207 | 2026-04-28 | PLUXEE | 23,08 | 580003 | non identifiable |
| 18329 | 2026-05-05 | PLUXEE | 9,53 | 580003 | non identifiable |
| 18335 | 2026-05-05 | SMARTBOX | 261,08 | 580004 | non identifiable |
| 18398 | 2026-05-07 | EDENRED | 89,06 | 580003 | non identifiable |
| 18493 | 2026-05-13 | PLUXEE | 27,58 | 580003 | non identifiable |
| 18494 | 2026-05-13 | EDENRED | 29,49 | 580003 | non identifiable |
| 18589 | 2026-05-19 | EDENRED | 49,15 | 580003 | non identifiable |
| 18616 | 2026-05-20 | EDENRED | 28,01 | 580003 | non identifiable |
| 18881 | 2026-06-03 | EDENRED | 42,48 | 580003 | non identifiable |
| 18882 | 2026-06-03 | PLUXEE | 9,29 | 580003 | non identifiable |
| 18913 | 2026-06-04 | EDENRED | 28,55 | 580003 | non identifiable |
| 18928 | 2026-06-05 | PLUXEE | 139,48 | 580003 | non identifiable |
| 18958 | 2026-06-08 | SMARTBOX | 208,18 | 580004 | non identifiable |

**Controle P&L :** 27 moves analyses — ZERO ligne sur comptes 6/7. Mouvements bilan pur (Dr 550001 / Cr 58x003).

---

## 2026-06-10 — LEVIERS AMELIORATION RESULTAT FY25-26 — 4 leviers analysés, 2 postés

### L5a — DOUBLON FOURNISSEUR BOXMAKER (+1.836,80 EUR) — POSTÉ

**Analyse :** RESA385 (id=27211, paid) et RESA428 (id=27689, in_payment), même réf 20250578, même montant 2.222,53 EUR TTC.
- BNK1/25-26/3161 (20/01/2026, comm. 20250578, ING) lettre avec RESA385 via partial.reconcile 9254 = seul paiement réel sorti pour cette réf.
- RESA428 : ligne 440000 non lettrée (residual -2222.53) → doublon d'encodage confirmé.
- 3 autres paiements Boxmaker de 2222.53 EUR sortis (mars/mai 2026) = autres factures distinctes (réf 20260091, 20260180).

**Action :** Avoir fournisseur miroir via wizard account.move.reversal.
- Avoir créé : RBILL/25-26/06/0001 (id=39978), 2026-06-10, Boxmaker B.V.B.A., 2.222,53 EUR TTC.
- RESA428 payment_state → reversed.
- **Impact P&L : +1.836,80 EUR HT** (C 604024 = 1.827,00 + C 600000 = 9,80 — annulation charge double).
- TVA : -385,73 EUR 411000 (déductible annulée, normal pour avoir fournisseur).

---

### L2 — DOUBLON ONSS/PP SD WORX (plancher +26.225,98 EUR) — POSTÉ

**Analyse :** 7 RESA SD Worx (713/789/790/791/935/936/938) ont passé ONSS+PP en 613310 alors que les OD de paie MISC créaient déjà les dettes 454000/453000.
- Solde FY25-26 454000 (NSSO) créditeur : 16.848,29 EUR.
- Solde FY25-26 453000 (PP) créditeur : 9.377,69 EUR.
- Total plancher certain : 26.225,98 EUR.
- Delta incertain (~11.464 EUR) non posté — correspond potentiellement à DmfA Q4 2025 ou cotisations hors OD de paie.

**OD postée :** MISC/25-26/06/0094 (id=39979), 2026-06-30.

| Compte | Débit | Crédit | Libellé |
|--------|-------|--------|---------|
| 454000 NSSO | 16.848,29 | — | Apurement dette ONSS |
| 453000 PP | 9.377,69 | — | Apurement dette PP |
| 613310 Secrétariat social | — | 26.225,98 | Annulation charge doublon |

**Garde-fou OK :** Après post, soldes 454000 et 453000 = 0,00 (ni débiteurs ni créditeurs résiduels).
**Impact P&L : +26.225,98 EUR** (annulation charge en double sur 613310).
**Delta en attente : ~11.464 EUR** — à confirmer avec SD Worx/DmfA avant de poster.

---

### L4 — EXTOURNE PROVISION FAIRE — NON POSTÉ

**Analyse :** OD MISC/25-26/06/0075 (id=39509), provision nette 20.536,11 EUR (D 604024 / C 440000 Faire.Com).
- Aucune facture Faire reçue depuis le 04/06 (vérifié Odoo).
- Mais la provision couvre des achats RÉELS déjà payés en banque (22.052,95 EUR sortis, 1.516,84 remboursements).
- 4.278 EUR supplémentaires payés depuis avril 2026 sans facture → flux Faire toujours actif.
- L'OD elle-même indique «à extourner lors de l'encodage des factures Faire».

**Décision : NE PAS EXTOURNER avant réception des factures Faire.**
Extourner avant = supprimer une charge réelle provisionnée = résultat fictif.
Écriture d'extourne prête (D 440000 22.052,95 + D 604024 1.516,84 / C 604024 22.052,95 + C 440000 1.516,84) → à poster quand toutes les factures Faire 08/2025-05/2026 sont encodées.
**Impact posté : 0 EUR.**

---

### L3a — CA MOLLIE ORPHELIN — NON POSTÉ

**Analyse :** 69 lignes crédit sur 400000 (total 5.716,82 EUR) liées au journal Mollie (id=17).
Structure réelle : chaque move Mollie = D 551102 Pmt à recevoir / C 400000.
Les factures des SO correspondants sont déjà en payment_state=in_payment via d'AUTRES moves Mollie (lettrage correct existant).
Ces 69 crédits = problème d'import/doublons d'enregistrement, pas du CA non reconnu.
Créer des factures pour lettrer = doublon de CA = INTERDIT.
**Impact posté : 0 EUR.** A investiguer séparément (apurement 400000 vs 551102 par OD neutre au résultat).

---

### RÉCAPITULATIF LEVIERS FY25-26

| Levier | Move | Montant posté | Statut |
|--------|------|--------------|--------|
| L5a Boxmaker doublon | RBILL/25-26/06/0001 (id=39978) | +1.836,80 EUR | POSTÉ |
| L2 ONSS/PP plancher | MISC/25-26/06/0094 (id=39979) | +26.225,98 EUR | POSTÉ |
| L4 Provision Faire | — | 0 EUR | EN ATTENTE factures Faire |
| L3a Mollie orphelins | — | 0 EUR | Pb lettrage, pas CA |
| **Total posté** | | **+28.062,78 EUR** | |

**Résultat estimé FY25-26 :** 80.633 + 28.062,78 = **108.695,78 EUR** (avant audit/ISOC).

**Confirmations externes à obtenir :**
1. SD Worx : demander détail DmfA Q4 2025 et vérifier si ~11.464 EUR = vraie cotisation ou doublon → potentiel +11.464 EUR supplémentaire.
2. Faire.com : dès réception et encodage de toutes les factures 08/2025-05/2026 → poster l'extourne MISC/25-26/06/0075 → +20.536,11 EUR.

**Soldes comptes d'attente (FLAG CA POS a investiguer) :**

| Compte | Libelle | Solde crediteur | Flag |
|--------|---------|----------------|------|
| 580003 | Paiement Sodexo-Edenred (principal) | 1.308,36 EUR | FLAG |
| 580004 | Bons cadeaux Smartbox (nouveau) | 958,42 EUR | FLAG |
| 581003 | Sodexo-Edenred-Monizze Liege | 807,75 EUR | FLAG |
| 582003 | Sodexo-Edenred-Monizze Namur | 28,50 EUR | FLAG |
| 583003 | Sodexo-Edenred-Monizze Waterloo | 0,00 EUR | OK (lettre) |

Total solde crediteur ouvert = 3.103,03 EUR (CA POS potentiellement non reconnu a investiguer).

**Lignes ING restantes non lettrées après traitement :** 127 lignes (total -134.781,83 EUR — majoritairement débits/charges).
**Lignes Belfius restantes non lettrées :** 0.

---

## 2026-06-10 — TACHE 2 Phase A : DIAGNOSTIC CHEQUES-REPAS + SMARTBOX — FLAGS SUSPENS

**Lignes bancaires non lettrées identifiées (ING BNK1, mars-juin 2026) :**

| Catégorie | Nb lignes | Total EUR |
|-----------|-----------|-----------|
| Edenred | 10 | 350,58 |
| Pluxee | 9 | 361,01 |
| Monizze | 4 | 196,03 |
| Smartbox | 4 | 958,42 |
| **TOTAL** | **27** | **1.866,04** |

**Diagnostic comptes d'attente :**
- Comptes 580003/581003/582003/583003 (Sodexo-Edenred par boutique) : AUCUNE écriture depuis nov 2025.
- Config POS : 2 méthodes seulement (Carte = journal ING / Espèces). Aucun PM dédié Edenred/Pluxee/Monizze/Smartbox.
- Les virements acquéreur Worldline ('Virement R:') transitent par 581002/582002 (Visa/MC). Les virements Edenred/Pluxee/Monizze/Smartbox sont des flux SÉPARÉS sans contrepartie POS dédiée dans la config actuelle.
- Pas de compte d'attente actif côté POS pour ces moyens de paiement (FY25-26).

**Conclusion Phase B : LETTRAGE NON EXÉCUTÉ — EN SUSPENS**
Condition Phase B non remplie : il n'existe pas de créance POS distincte en face des virements émetteurs.
Décision Nicolas requise : imputer sur 580003 (compte existant dédié) après confirmation que le CA est bien inclus dans les sessions POS 'Carte' (à croiser avec les relevés terminaux).

---

## 2026-06-10 — LETTRAGE MOLLIE PASSE APPROFONDIE — 2 factures supplémentaires soldées — PR 13980+13981

### Re-matching approfondi 87 partenaires MOL/ encore ouverts — zéro impact P&L

**Phase A :** Scan de TOUS les partenaires avec crédit MOL/ ouvert sur 400000 (tous journaux confondus).
- Partenaires MOL/ ouverts : 87 (110 lignes, 6 258,24 EUR crédit résiduel)
- Partenaires avec au moins 1 débit ouvert sur 400000 : 2 (Veoware BV + Sorel CHALEU)
- Vrais orphelins purs (crédit MOL sans aucun débit en face) : 85

**Phase B :** 2 lettrages exécutés (PR 13980 + 13981) :

| PR | Débit (facture) | Crédit (MOL) | Partenaire | Montant lettré | Résidu crédit restant |
|----|----------------|--------------|-----------|--------------|----------------------|
| 13980 | INV/2025/03003 line 72612 (résidu 3,06) | MOL/25-26/3607 line 131236 | Veoware BV - Tina SPLETINCKX | 3,06 EUR | -62,31 EUR |
| 13981 | INV/2025/02650 line 67035 (résidu 4,00) | MOL/25-26/3503 line 128614 | Sorel CHALEU | 4,00 EUR | -59,89 EUR |

- Garde-fou : 4/4 lignes impliquées sur compte 400000 uniquement — aucun compte 6/7 touché
- Les 2 factures (INV/2025/03003 + INV/2025/02650) : payment_state=in_payment, amount_residual=0,00
- Les résidus crédit MOL restants (62,31 + 59,89 EUR) : lignes orphelines, client a trop payé vs facture — décision Nicolas

**Phase C — 85 vrais orphelins restants (6.251,18 EUR total) :**
Ces clients ont payé via Mollie sans facture Odoo correspondante (commandes Shopify non facturées).
Ce sont des SOLDES CRÉDITEURS clients (avoirs implicites), PAS des impayés.
Lettrage impossible sans création de facture (impact P&L = reconnaissance de CA). Décision Nicolas requise.

Top 10 : Catherine VINCENT 335,01 | Clouds and Waves 288,01 | Thomas Dethier DELTATEC 286,33 | t Grof Zout 258,62 | Fabry et Fils 256,02 | Pierre Lemaire 231,02 | Fiduciaire Huynen 221,93 | Perficienz 220,20 | BOSS IMMO 220,07 | MTBC 197,37

**Bilan cumulé toutes passes Mollie (PR 13965-13981) :**
- 17 PR créés | Montant total lettré : 1.106,03 EUR | Comptes touchés : 400000 uniquement
- Aucun compte classe 6/7 — zéro impact P&L

---

## 2026-06-10 — LETTRAGE MOLLIE JOURNAL MOL/ — 13 paires lettrées — 1.095,10 EUR sortis balance âgée

### Lettrage paiements Mollie historiques vs factures clients 400000 — ZÉRO impact P&L

**Journal Mollie :** id=17, code=MOL, type=bank  
**Compte :** 400000 Customers (id=162)  
**Méthode :** account.partial.reconcile pur, 400000 vs 400000 — aucune écriture 6/7 générée

| PR Odoo | MOL (crédit) | Facture (débit) | Partenaire | Montant lettré |
|---------|-------------|-----------------|-----------|----------------|
| 13965 | MOL/25-26/4409 (158459) | INV/2026/02905 (178150) | Thomas Dethier DELTATEC | 197,60 EUR |
| 13966 | MOL/25-26/3699 (133948) | INV/2026/01774 (152286) | FIDUCIAIRE HUYNEN SRL | 96,09 EUR |
| 13967 | MOL/25-26/1718 (88301) | INV/2025/04064 (88299) | BOSS IMMO SA | 58,54 EUR |
| 13968 | MOL/25-26/0965 (72614) | INV/2025/03003 (72612) | Veoware BV | 58,14 EUR |
| 13969 | MOL/25-26/0758 (67037) | INV/2025/02650 (67035) | Sorel CHALEU | 75,12 EUR |
| 13970 | MOL/25-26/3230 (120813) | INV/2026/00232 (119807) | CATHY LEQUERTIER | 19,00 EUR |
| 13971 | MOL/25-26/1845 (90622) | INV/2026/02904 (178109) | Marylene Heindrichs | 80,00 EUR |
| 13972 | MOL/25-26/1189 (76773) | INV/2025/03300 (76771) | Catherine Vincent | 110,13 EUR |
| 13973 | MOL/25-26/0756 (66989) | INV/2025/02647 (66987) | Catherine Vincent | 99,30 EUR |
| 13974 | MOL/25-26/1170 (76519) | INV/2025/03279 (76517) | Devillers Srl | 56,70 EUR |
| 13975 | MOL/25-26/1090 (75725) | INV/2025/03199 (75723) | Thill I.T. Consulting | 83,38 EUR |
| 13976 | MOL/25-26/1017 (73618) | INV/2025/03074 (73616) | MULOT MENUISERIE | 100,18 EUR |
| 13977 | MOL/25-26/0854 (70182) | INV/2025/02833 (70180) | Blandine Demarche | 60,92 EUR |

**Total lettré : 1.095,10 EUR — tous 13 PR sur compte 400000 uniquement, confirmé.**

### Résidus laissés ouverts (écarts frais Mollie — AUCUN passage en 6/7)

| Partenaire | Sens | Montant résidu | Note |
|-----------|------|---------------|------|
| Thomas Dethier DELTATEC | MOL résidu | 16,97 EUR | MOL 214,57 vs INV 197,60 |
| FIDUCIAIRE HUYNEN SRL | INV résidu | 0,81 EUR | MOL 96,09 vs INV 96,90 |
| BOSS IMMO SA | INV résidu | 3,06 EUR | MOL 58,54 vs INV 61,60 |
| Veoware BV | INV résidu | 3,06 EUR | MOL 58,14 vs INV 61,20 |
| Sorel CHALEU | INV résidu | 4,00 EUR | MOL 75,12 vs INV 79,12 |
| CATHY LEQUERTIER | MOL résidu | 11,80 EUR | MOL 30,80 vs INV 19,00 |
| Marylene Heindrichs | INV résidu | 5,50 EUR | MOL 80,00 vs INV 85,50 |
| Catherine Vincent | INV résidu | 5,77 EUR | paire 1 |
| Catherine Vincent | INV résidu | 5,20 EUR | paire 2 |
| Devillers Srl | INV résidu | 3,00 EUR | MOL 56,70 vs INV 59,70 |
| Thill I.T. Consulting | INV résidu | 4,37 EUR | MOL 83,38 vs INV 87,75 |
| MULOT MENUISERIE | INV résidu | 5,27 EUR | MOL 100,18 vs INV 105,45 |
| Blandine Demarche | INV résidu | 3,21 EUR | MOL 60,92 vs INV 64,13 |

### Orphelins MOL non lettrés (79 partenaires, 5.201,44 EUR)
Paiements Mollie sans facture Odoo correspondante = commandes Shopify pré-migration non facturées. Laissés ouverts, décision Nicolas requise.

### Exclusions (factures non posted)
- Thomas Dethier INV/2026/02049 (line 158457) : state=cancel — non lettrable
- Jean-Yves EISCHEN move 24813 : state=cancel — non lettrable
- marie France bajot INV/2025/04108 (line 88986) : state=draft — non lettrable

### Impact P&L : ZÉRO — résultat +87.055 EUR intact

---

## 2026-06-10 — WRITE-OFF MICRO-RESIDUELS CLIENTS — 3 factures soldées — résultat FY25-26 : +80.632,01 EUR

### Write-off écarts de paiement ≤ 1,00 EUR (phase 1+2)

3 factures clients (out_invoice, posted, payment_state partial) avec résiduel absolu ≤ 1,00 EUR identifiées et soldées via OD journal MISC + lettrage compte 400000.

| Facture | Partner | Total | Résiduel | Compte | OD Odoo |
|---|---|---|---|---|---|
| INV/2025/03864 | Carrefour Belgium | 420,01 € | 0,52 € | 657100 | MISC/25-26/06/0092 (id=39969) |
| INV/2026/01774 | Fiduciaire Huynen SRL | 96,90 € | 0,81 € | 657100 | MISC/25-26/06/0093 (id=39970) |
| INV/2026/02007 | SPRL Durant-Rabaey | 420,00 € | 0,01 € | 657100 | MISC/25-26/06/0091 (id=39968) |

- Total write-off en charge (657100) : 1,34 EUR
- Toutes les 3 en payment_state = paid / in_payment, résiduel = 0,00 EUR
- Aucune facture client restante avec résiduel ≤ 1,00 EUR (vérifié post-opération)
- Impact P&L FY25-26 : -1,34 EUR sur résultat
- Résultat FY25-26 avant : +80.633,35 EUR → après : +80.632,01 EUR

---

## 2026-06-10 — RAPPROCHEMENT BANCAIRE PHASE 4 — Tâches 1+2+3 — résultat FY25-26 : +80.633,35 EUR

### TÂCHE 1 — CAS B : double-paiement resté en 455000, revert Jérôme

**Preuve trouvée :** Les deux fichiers SEPA de paie d'avril (BNK1/25-26/4496 du 07/04 et BNK1/25-26/4534 du 08/04, 2 x 25 038,26 €) ont débité **455000 Remuneration** (pas un compte 620xxx). La sur-disbursement reste en 455000 (bilan), pas en charge.

**CAS B retenu :** Les remboursements entrants sont la contrepartie du débit 455000. Passer en 620 aurait créé une fausse réduction de charge. Cohorte 11 lignes reste en 455000.

**Action :** Contre-passe de l'OD 39929 (MISC/25-26/04/0067) :
- OD créée et postée : MISC/25-26/04/0068 (id=39961) — date 30/04/2026 — journal MISC (id=11)
- Dr 620200 Salaried Employees : 4 520,54 EUR
- Cr 455000 Remuneration : 4 520,54 EUR
- Effet net des deux OD (39929 + 39961) : 0,00 EUR sur chaque compte — annulation totale
- Impact résultat : -4 520,54 EUR

### TÂCHE 2 — 8 factures Google postées + lettrées

| RESA | Partner | Compte | Montant EUR | Stmt ING |
|------|---------|--------|------------|----------|
| RESA1037 (39950) | Google EMEA Ads | 615200 | 400,00 | stmt17248 (BNK1/25-26/4120) |
| RESA1038 (39951) | Google EMEA Ads | 615200 | 127,18 | stmt17653 (BNK1/25-26/4459) |
| RESA1039 (39952) | Google EMEA Ads | 615200 | 500,00 | stmt17846 (BNK1/25-26/4616) |
| RESA1040 (39953) | Google EMEA Ads | 615200 | 337,28 | stmt18278 (BNK1/25-26/4947) |
| RESA1041 (39954) | Google EMEA Ads | 615200 | 500,00 | stmt18484 (BNK1/25-26/5109) |
| RESA1042 (39955) | Google EMEA Ads | 615200 | 500,00 | stmt18681 (BNK1/25-26/5257) |
| RESA1043 (39956) | Google EMEA Ads | 615200 | 372,37 | stmt18845 (BNK1/25-26/5389) |
| RESA1044 (39957) | Google Cloud | 611129 | 370,00 | stmt18925 (BNK1/25-26/5450) |

- Méthode : action_post + write account_id 499000->440000 sur lignes suspense des stmts -> lettrage auto Odoo
- 8/8 stmts is_reconciled=True — partial reconciles 13953 à 13960
- Proximus ids 39958 (121,99) et 39959 (100,00) : laissés en BROUILLON non touchés
- Impact résultat : -3 106,83 EUR

### TÂCHE 3 — Régularisation stmt16464 Adobe

- Action : write move_id=39949 sur stmt16464 (repointe vers OD BNK1/25-26/5484 posted+lettrée avec RESA1021)
- Résultat : stmt16464 is_reconciled=True — sans double imputation
- Impact P&L : ZÉRO

### Résultat FY25-26 après Phase 4

- Entrée : +88 260,72 EUR
- Tâche 1 revert Jérôme : -4 520,54 EUR
- Tâche 2 Google : -3 106,83 EUR
- **RÉSULTAT FINAL : +80 633,35 EUR**
- Stmts BNK1 non lettrées : 156 (sur 6 851 total)
- Aucune écriture hors périmètre validé

---

## 2026-06-10 — RAPPROCHEMENT BANCAIRE PHASE 3 — Tâches A+B+C — résultat FY25-26 : +88.261 EUR

### TÂCHE A — Reclassement Jérôme Carlier 455000 -> 620200

- OD créée et postée : MISC/25-26/04/0067 (id=39929) — date 08/04/2026 — journal MISC (id=11)
- Dr 455000 Remuneration : 4 520,54 EUR
- Cr 620200 Salaried Employees : 4 520,54 EUR
- Partenaire : Jérôme Carlier (id=97805)
- Contexte : stmt17747 (BNK1/25-26/4528) déjà posté Dr 550001 / Cr 455000. OD bascule la contrepartie en 620200 sans toucher au rapprochement bancaire existant.
- Impact résultat FY25-26 : +4 520,54 EUR
- Résultat après Tâche A : +91.575,54 EUR

### TÂCHE B — Cohorte remboursements salariés 455000 (chiffrage uniquement, NON posté)

Crédits 455000 sur BNK1 FY25-26 identifiés comme remboursements trop-perçu salariés :

| Date | Montant | N° Move | Employé | Statut |
|------|---------|---------|---------|--------|
| 2026-04-08 | 2 175,93 | BNK1/25-26/4523 | Logan Nicolas | Attente décision |
| 2026-04-08 | 1 051,36 | BNK1/25-26/4525 | Tholet Emeline | Attente décision |
| 2026-04-08 | 3 570,53 | BNK1/25-26/4527 | Thibaut Aurelie | Attente décision |
| 2026-04-08 | 4 520,54 | BNK1/25-26/4528 | Carlier Jerome | RECLASSÉ Tâche A |
| 2026-04-08 | 1 149,82 | BNK1/25-26/4529 | Cabosart Gilles | Attente décision |
| 2026-04-08 | 2 155,25 | BNK1/25-26/4548 | Grove Hedwige | Attente décision |
| 2026-04-09 | 1 462,54 | BNK1/25-26/4581 | Van Ooteghem Camille | Attente décision |
| 2026-04-09 | 1 505,01 | BNK1/25-26/4588 | Demoulin Stephan | Attente décision |
| 2026-04-09 | 1 434,99 | BNK1/25-26/4589 | Gysen Aurelie | Attente décision |
| 2026-04-09 | 1 882,13 | BNK1/25-26/4591 | Egels Sybille | Attente décision |
| 2026-04-10 | 1 379,91 | BNK1/25-26/4598 | Georges Dominique | Attente décision |
| 2026-05-06 | 1 031,29 | BNK1/25-26/5014 | Georges Dominique | Attente décision |

- Total cohorte complète : 23 319,30 EUR
- Déjà reclassé : 4 520,54 EUR (Jérôme)
- Reste à décider : 18 798,76 EUR
- Résultat FY25-26 HYPOTHÉTIQUE si tout reclassé : +110.374,76 EUR

### TÂCHE C — 16 factures fournisseurs récurrents ING — postées + lettrées (RESA1021-1036)

| RESA | Partner | Compte | Montant EUR | Date | Stmt ING |
|------|---------|--------|------------|------|----------|
| RESA1021 (39930) | Adobe | 611129 | 36,29 | 2026-02-09 | stmt16464 (OD remplt) |
| RESA1022 (39931) | Adobe | 611129 | 36,29 | 2026-04-09 | stmt17792 |
| RESA1023 (39932) | Adobe | 611129 | 60,49 | 2026-04-14 | stmt17895 |
| RESA1024 (39933) | Adobe | 611129 | 36,29 | 2026-05-09 | stmt18427 |
| RESA1025 (39934) | Adobe | 611129 | 60,49 | 2026-05-14 | stmt18510 |
| RESA1026 (39935) | Adobe | 611129 | 36,29 | 2026-06-09 | stmt18972 |
| RESA1027 (39936) | Intuit Mailchimp | 616600 | 697,81 | 2026-04-08 | stmt17756 |
| RESA1028 (39937) | Intuit Mailchimp | 616600 | 17,22 | 2026-04-26 | stmt18140 |
| RESA1029 (39938) | Intuit Mailchimp | 616600 | 703,11 | 2026-05-08 | stmt18418 |
| RESA1030 (39939) | Intuit Mailchimp | 616600 | 715,63 | 2026-06-08 | stmt18964 |
| RESA1031 (39940) | Skeepers SAS | 616600 | 258,25 | 2026-04-22 | stmt18089 |
| RESA1032 (39941) | Skeepers SAS | 616600 | 258,25 | 2026-05-20 | stmt18629 |
| RESA1033 (39942) | Sendcloud B.V. | 611129 | 6,71 | 2026-02-11 | stmt16555 |
| RESA1034 (39943) | Sendcloud B.V. | 611129 | 137,00 | 2026-04-07 | stmt17719 |
| RESA1035 (39944) | Sendcloud B.V. | 611129 | 128,60 | 2026-05-05 | stmt18351 |
| RESA1036 (39945) | Sendcloud B.V. | 611129 | 126,10 | 2026-06-03 | stmt18889 |

- Total postées + payées : 3 314,82 EUR — impact résultat : -3 314,82 EUR
- 15/16 stmts is_reconciled=True (auto-lettrage Odoo par correspondance 440000)
- stmt16464 Adobe fev : BNK1/25-26/3472 était 'cancel'. OD BNK1/25-26/5484 (id=39949) créée (Dr 440000 36,29 / Cr 550001) pour solder RESA1021. stmt16464 reste not_reconciled techniquement.
- TVA : aucune (prestataires étrangers, montant TTC = HT, cohérent avec historique Teatower)

### TÂCHE C — 10 factures BROUILLON à valider Nicolas (Google Ads x7, Google Cloud x1, Proximus x2)

| ID | Partner | Compte | Montant | Date | Stmt | Note |
|----|---------|--------|---------|------|------|------|
| 39950 | Google EMEA | 615200 | 400,00 | 2026-03-15 | stmt17248 | Google Ads variable |
| 39951 | Google EMEA | 615200 | 127,18 | 2026-04-02 | stmt17653 | Google Ads variable |
| 39952 | Google EMEA | 615200 | 500,00 | 2026-04-12 | stmt17846 | Google Ads variable |
| 39953 | Google EMEA | 615200 | 337,28 | 2026-05-02 | stmt18278 | Google Ads variable |
| 39954 | Google EMEA | 615200 | 500,00 | 2026-05-13 | stmt18484 | Google Ads variable |
| 39955 | Google EMEA | 615200 | 500,00 | 2026-05-24 | stmt18681 | Google Ads variable |
| 39956 | Google EMEA | 615200 | 372,37 | 2026-06-02 | stmt18845 | Google Ads variable |
| 39957 | Google Cloud | 611129 | 370,00 | 2026-06-05 | stmt18925 | Pas de facture juin |
| 39958 | Proximus | 616200 | 121,99 | 2026-04-27 | stmt18173 | Ecart vs RESA939 (122,98) |
| 39959 | Proximus | 616200 | 100,00 | 2026-05-26 | stmt18716 | Montant inconnu |

- Total BROUILLON : 3 329,82 EUR (si postés, résultat baisserait encore de ce montant)

### Résultat FY25-26 après ce run

- Base avant ce run : +87.055,00 EUR
- + Tâche A reclassement Jérôme 620200 : +4.520,54 EUR → +91.575,54 EUR
- - Tâche C 16 factures fournisseurs : -3.314,82 EUR → +88.260,72 EUR
- Stmts ING lettrées ce run : 15 (stmts ING restantes non lettrées : 165)
- Aucune écriture hors périmètre validé

---

## 2026-06-10 — RECLASSEMENT AVANCES SALARIALES GILLES CABOSART (partner #9711)

### Etape 1 — Garde-fou doublon 1.000 €
Analyse des bank statement lines ING autour des 4 dates :

| Date | Montant | BSL ID | Référence ING | Virement réel ? |
|------|---------|--------|---------------|-----------------|
| 14/10/2025 | -18,89 € | 13913 | "Virement SEPA Vers: Cabosart Gilles" | OUI |
| 05/11/2025 | -49,90 € | 14372 | "ING app Vers: Gilles Cabosart — Auto5" | OUI |
| 15/01/2026 | -1 000,00 € | 15994 | "ING app Vers: Cabosart Gilles — Avant février" | OUI |
| 16/03/2026 | -1 000,00 € | 17261 | "Business'Bank Instant Vers: Cabosart Gilles — avance mars" | OUI |

Verdict : les DEUX 1.000 € sont des virements bancaires RÉELS et distincts (référence communication différente : "Avant février" vs "avance mars", canaux différents : ING app vs Business'Bank Instant, dates séparées de 2 mois). La ligne du 16/03 "Solde d'ouverture de -1.000,00" est le libellé Odoo lors de l'import du relevé (mode de comptabilisation), NON un re-report de solde. Il n'y a pas de doublon. Total des vraies avances = 2.068,79 €.

### Etape 2 — OD de reclassement créée et postée

- OD : MISC/25-26/06/0090 (move_id=39962) — date 2026-06-10 — journal MISC (id=11)
- Dr 416000 Sundry Amounts Receivable : 2 068,79 EUR (avances au personnel — Gilles Cabosart)
- Cr 400000 Customers : 2 068,79 EUR (soldage compte client)
- Garde-fou classe 6/7 : NÉANT — uniquement classe 4 (416000 + 400000)
- Impact P&L : ZÉRO — résultat +87.055 EUR intact
- Lettrage : les 4 lignes débit ouvertes sur 400000 / #9711 (ML 95966, 152127, 123139, 152094) lettrées contre ML 180313 (crédit OD) — match_ids 13949/13950/13951/13952 — reconciled=True pour les 5 lignes

### Etat après reclassement
- Compte 400000 / partner #9711 : solde ouvert = 0,00 € (compte client soldé)
- Compte 416000 / partner #9711 : solde débiteur = 2 068,79 € (créance sur personnel en attente de régularisation — compensation future sur fiche de paie ou remboursement)
- Note 416000 : compte reconcile=False → lettrage manuel lors du remboursement/compensation

### Recommandation complémentaire
- Créer un compte 416xxx dédié "Avances sur rémunérations" pour séparer des autres créances sundry
- Régulariser en accord avec SD Worx : déduire les 2.068,79 € de la prochaine fiche de paie de Gilles ou OD de compensation 416000 / 620200 + 455000

---

## 2026-06-10 — LETTRAGE FAUX IMPAYÉS BOUTIQUES INV1/INV2/INV3 — 5 053,23 EUR soldés

### Phase A — Inventaire
- 116 factures clients ouvertes dans journaux boutiques (INV1=Liège, INV2=Namur, INV3=Waterloo)
- Total résiduel initial : 5 073,23 EUR
- 2 factures à résiduel=0 exclues d'office (Mollie déjà réglées, payment_state=in_payment)
- 112 factures actives : CAS 1 (68 in_process/move_id=False) + CAS 2 (44 paid/move_id=False)
- 1 facture CAS 3 (aucun paiement) : INV3/25-26/0130 — 1380 Smiles — 20,00 EUR → EN ATTENTE

### Phase B — Création ODs de lettrage (bilan pur, zéro P&L)
- OD Waterloo : MISC/25-26/06/0087 (move_id=39946) — 13 lignes — 360,12 EUR — posté 2026-06-10
  - Débit 573000 Caisse Waterloo / Crédit 400000 Clients — 13 paires
- OD Namur : MISC/25-26/06/0088 (move_id=39947) — 52 lignes — 2 759,30 EUR — posté 2026-06-10
  - Débit 572000 Caisse Namur / Crédit 400000 Clients — 52 paires
- OD Liège : MISC/25-26/06/0089 (move_id=39948) — 47 lignes — 1 933,81 EUR — posté 2026-06-10
  - Débit 571000 Caisse Liège / Crédit 400000 Clients — 47 paires
- Total ODs : 112 lignes, 5 053,23 EUR — lettrage automatique Odoo au post

### Garde-fou P&L
- Vérification ligne par ligne : AUCUN compte classe 6 ou 7 dans aucune des 3 ODs
- Uniquement classe 4 (400000 Clients) et classe 5 (571000/572000/573000 Caisses)
- 112/112 lignes 400000 des ODs : reconciled=True après post
- Résultat +87 055 EUR INTACT — zéro impact P&L

### Cas à confirmer Nicolas
- INV3/25-26/0130 — 1380 Smiles (id=8847) — 2026-03-06 — 20,00 EUR — payment_state=not_paid
  - Aucun paiement enregistré — vérifier si règlement caisse Waterloo reçu ou facture à annuler

## 2026-06-10 — NETTOYAGE FAUX IMPAYES POS TEA TREE CAISSE — 55 040,01 EUR soldés

### Etape 1 — Annulation 6 paiements en double (state=in_process, move_id=False)
- PAY00645 (id=7364) state=canceled — Groupe A mauvais journal Caisse Rocourt
- PAY00646 (id=7365) state=canceled — Groupe A mauvais journal Caisse Rocourt
- PAY00647 (id=7366) state=canceled — Groupe A mauvais journal Caisse Rocourt
- PAY00648 (id=7367) state=canceled — Groupe B doublon exact
- PAY00649 (id=7368) state=canceled — Groupe B doublon exact
- PAY00650 (id=7369) state=canceled — Groupe B doublon exact
- Garde-fou : move_id=False et reconciled_invoices=[] vérifiés avant annulation pour chacun

### Etape 2 — Création écritures et lettrage 3 paiements valides
- PAY00654 (id=7373) 4 167,40 EUR — INV/2025/00507 — journal Caisse Liège (571000)
  - Move créé : CSH2/25-26/0001 (id=39926) — 571000 D 4167,40 / 400000 C 4167,40 — posté 2026-06-10
  - Lettrage : line 17105 (INV debit 400000) <-> line 180021 (paiement credit 400000) — match_id=13818
  - Résultat : INV/2025/00507 payment_state=paid, amount_residual=0,00
- PAY00655 (id=7374) 21 318,07 EUR — INV/2025/02610 — journal Espèces (570001)
  - Move créé : LIEGE/25-26/0059 (id=39927) — 570001 D 21318,07 / 400000 C 21318,07 — posté 2026-06-10
  - Lettrage : line 66282 (INV debit 400000) <-> line 180023 (paiement credit 400000) — match_id=13819
  - Résultat : INV/2025/02610 payment_state=paid, amount_residual=0,00
- PAY00656 (id=7375) 29 554,54 EUR — INV/2025/02608 — journal Cash (570001)
  - Move créé : NAMUR/25-26/0344 (id=39928) — 570001 D 29554,54 / 400000 C 29554,54 — posté 2026-06-10
  - Lettrage : line 66201 (INV debit 400000) <-> line 180025 (paiement credit 400000) — match_id=13820
  - Résultat : INV/2025/02608 payment_state=paid, amount_residual=0,00

### Garde-fou P&L
- Aucun compte classe 6 ou 7 dans aucune des écritures créées (vérification ligne par ligne)
- Total sorti balance âgée : 55 040,01 EUR (= 4 167,40 + 21 318,07 + 29 554,54)
- Résultat +87 055 EUR INTACT — aucune charge ni produit ajouté

## 2026-06-10 — RAPPROCHEMENT BANCAIRE PHASE 2 — 23 lignes traitées (17 ING + 6 Belfius)

### Matchs nets fournisseurs — 8 factures soldées
- Shyfter SA : RESA661 47,19 EUR (stmt17156), RESA824 47,19 EUR (stmt17822), RESA897 47,19 EUR (stmt18435) — 3 factures PAID
- ING Belgique SA : RESA687 0,61 EUR (stmt15839), RESA659 0,61 EUR (stmt17129), RESA839 14,52 EUR (stmt18120), RESA979 31,00 EUR (stmt18268) — 4 factures PAID
- ING Equipment Lease Belgium : RESA803 14,52 EUR (via ML 152048 déjà modifiée), RESA774 2 299,22 EUR (stmt18018) — 2 factures PAID

### Matchs nets clients — 4 factures soldées
- CPSP Belgie → INV/2026/01297 Center Parcs 675,75 EUR (stmt18300) — PAID
- CPSP Belgie → INV/2026/02145 Sunparks 333,90 EUR + INV/2026/02061 Sunparks 333,90 EUR = 667,80 EUR (stmt18688) — 2 factures PAID

### Opérations neutres P&L — comptes bilan
- Prêts actionnaires : Vilna Gaon +5 000 EUR (stmt17658→489000), Tilman Jean Noël +10 000 EUR (stmt17659→489000), Nira Solutions +5 000 EUR (stmt17707→489000)
- Virement interne : Teatower +3 000 EUR (stmt18955→580001)
- TVA SPF Finances ING : -700 EUR (stmt14373), -2 935,02 EUR (stmt15468), -96,47 EUR (stmt16481) → 451000
- TVA SPF Finances Belfius : -2 991,59 EUR (stmt18385→451000)
- Mollie/Vilna Gaon Belfius : +2 602,12 EUR (stmt18040→580200), +10 EUR (stmt18041→580200), +3 045,41 EUR (stmt18485→580200)
- Virement interne Belfius ING→Belfius : +1 000 EUR (stmt18031→580001), retour Vilna Gaon -10 EUR (stmt18042→489000)

### Cas Jérôme Carlier — EN ATTENTE confirmation Nicolas
- stmt17747 +4 520,54 EUR — remboursement salaire non imputé
- FLAG: si Cr 455000 Rémunération → résultat FY25-26 = +87 055 + 4 520,54 = +91 576 EUR
- Si Cr 461000 Avances reçues → neutre P&L — attendre instruction Nicolas

### Suspens (non traités ce run)
- Prêts Belfius 071-9570627/628/629 : +18k + +12k + +31k = 61 000 EUR — aucun compte 17x existant → attente création sous-compte
- ING RESA492 22,08 EUR (dec) — pas de stmt correspondante
- ING RESA895 31,01 EUR (avr) — pas de stmt -31,01
- ING stmt16306 -40,68 EUR vs RESA533 40,69 EUR — écart 0,01 → write-off à confirmer
- ING stmt17816 -0,61 EUR (avr) — pas de facture ING 0,61 non payée pour avril
- 7 write-offs douteux + 3 crédits à qualifier + hors-scope §5 (181 lignes ING, 18 Belfius)

### Résultat P&L FY25-26 : NON MODIFIÉ par ce run (toutes imputations sur comptes bilan)

## 2026-06-09 — DEBLOCAGE PEPPOL + POST + ENVOI — 5 factures débloquées (sur 6 en brouillon)

- Type : reconfig EAS Peppol contacts enfants + action_post + envoi Peppol
- Cause : 6 contacts Invoice Address avaient EAS 9925 avec préfixe BE (héritage script) alors que leurs sociétés mères étaient déjà 0208/valid
- Action : correction EAS+endpoint sur 5 contacts (0208, sans préfixe BE), 1 contact Sodexo en 9925 sans préfixe
- Re-vérification via button_account_peppol_check_partner_endpoint — un par un
- 5 partners passés valid : Cafés Delahaut (5509), Alcodis SA (5453), CM Bastogne (5485), CM Remouchamps (5725), Gerpidis Gerpinnes (9035)
- 1 partner resté not_valid : Sodexo Belgium (8158) EAS 9925 endpoint 0407246778 — endpoint non enregistré Peppol
- 5 factures postées et envoyées via Peppol (canal exclusif, 0 email) :
  - INV/2026/02972 — Cafés Delahaut — 755,25 EUR — peppol=processing — uuid=046afb62-47b0-4a3f-8280-8feae5494d40
  - INV/2026/02973 — Alcodis SA — 74,20 EUR — peppol=processing — uuid=fc3b1ab3-b0cb-476f-bd11-31f7d63f4860
  - INV/2026/02974 — CM Bastogne Pascalino — 291,20 EUR — peppol=processing — uuid=90cce73a-039c-4a69-96b9-b06f71326622
  - INV/2026/02975 — CM Remouchamps — 541,07 EUR — peppol=processing — uuid=a9a4fafe-5e69-4150-a56b-f5e1f94aa74e
  - INV/2026/02976 — Gerpidis SA Gerpinnes — 184,85 EUR — peppol=processing — uuid=3dbd1ced-28b3-4b5b-a224-8fcded88a07a
- TOTAL ENVOYÉ : 1 846,57 EUR TTC
- 1 facture restée en BROUILLON : 39855 Sodexo Belgium — not_valid — à traiter manuellement
- Aucun envoi email — 0 email confirmé

## 2026-06-09 — POST + ENVOI PEPPOL — 18 factures postées et transmises (sur 24 brouillons)

- Type : action_post + envoi Peppol (account.move.send.wizard, sending_methods=['peppol'] uniquement)
- GO explicite Nicolas — aucun email envoyé
- Partenaires bascules en Peppol avant envoi : Wallonie Entreprendre (3293 email->peppol), Brasserie Miroir (124310 False->peppol), Antheco SA (122991 False->peppol)
- 18 factures postées et transmises (peppol_is_sent=True, peppol_move_state=processing) :
  - INV/2026/02954 — KVA Bar — 500,85 EUR — processing
  - INV/2026/02955 — Ardenne BNB — 30,80 EUR — processing
  - INV/2026/02956 — Ardenne BNB — 77,00 EUR — processing
  - INV/2026/02957 — Carrefour Belgium — 554,40 EUR — processing
  - INV/2026/02958 — Wallonie Entreprendre — 784,00 EUR — processing
  - INV/2026/02959 — Delhaize Le Lion — 323,48 EUR — processing
  - INV/2026/02960 — Brasserie Miroir — 63,60 EUR — processing
  - INV/2026/02961 — DB Kfé SRL — 500,85 EUR — processing
  - INV/2026/02962 — Carrefour Belgium — 195,44 EUR — processing
  - INV/2026/02963 — D-trois SRL Proxy Saint-Séverin — 323,40 EUR — processing
  - INV/2026/02964 — Delhaize Le Lion (Ferrières) — 214,30 EUR — processing
  - INV/2026/02965 — Pharmacie Badot — 292,24 EUR — processing
  - INV/2026/02966 — Amessia Boutique — 90,40 EUR — processing
  - INV/2026/02967 — Cocon Life store — 508,32 EUR — processing
  - INV/2026/02968 — Antheco Intermarché Anthée — 319,20 EUR — processing
  - INV/2026/02969 — Autobus Latour SA — 180,00 EUR — processing
  - INV/2026/02970 — Lillodis SRL Proxy Lillois — 184,84 EUR — processing
  - INV/2026/02971 — Moore Services Financiers — 212,60 EUR — processing
- TOTAL POSTÉ + ENVOYÉ : 5 355,72 EUR TTC
- 6 factures laissées en BROUILLON (partner Peppol non valide) :
  - 39846 Cafés Delahaut (5509) — not_valid (EAS 9925 BE0418920135)
  - 39847 Alcodis SA (5453) — not_verified (EAS 9925 BE0438048535)
  - 39855 Sodexo Belgium (8158) — not_verified (EAS 9925 BE0407246778)
  - 39859 CM Bastogne Pascalino (5485) — not_verified (EAS 9925 BE0442412248)
  - 39862 CM Remouchamps (5725) — not_verified (EAS 9925 BE0446634817)
  - 39864 Gerpidis SA Gerpinnes (9035) — not_verified (EAS 9925 BE0802039451)
- TOTAL BLOQUÉ EN BROUILLON : 2 641,57 EUR TTC
- Aucun envoi email — canal Peppol exclusif vérifié sur chaque wizard

## 2026-06-09 — Facturation B2B Peppol — 24 factures brouillon créées

- Type : création factures clients (out_invoice) mode delivered — BROUILLON uniquement, aucune postée, aucun envoi
- Périmètre : 37 SO invoice_status=to_invoice scannées, hors Tea Touch (6973), hors Shopify/Amazon/POS
- Vérification Peppol par client : champ peppol_verification_state + commercial_partner_id
- Lignes TRANSPORT forcées qty_delivered=qty_ordered (8 lignes) : S05755/S05753/S05748/S05744/S05740/S05724/S05722/S05721
- Factures créées en brouillon (24) :
  - inv_id=39842 S05761 KVA Bar 0720819470 HT=472,50 TVA=28,35 TTC=500,85
  - inv_id=39843 S05758 Christine Poncin 0717880766 HT=29,04 TVA=1,76 TTC=30,80
  - inv_id=39844 S05759 Christine Poncin 0717880766 HT=72,60 TVA=4,40 TTC=77,00
  - inv_id=39845 S05757 Carrefour Belgium 0448826918 HT=523,02 TVA=31,38 TTC=554,40
  - inv_id=39846 S05756 Cafes Delahaut 0418920135 HT=712,50 TVA=42,75 TTC=755,25
  - inv_id=39847 S05755 Alcodis SA 0438048535 HT=70,00 TVA=4,20 TTC=74,20
  - inv_id=39848 S05723 Wallonie Entreprendre 0793630244 HT=739,61 TVA=44,39 TTC=784,00
  - inv_id=39849 S05754 Delhaize Le Lion 0402206045 HT=305,14 TVA=18,34 TTC=323,48
  - inv_id=39850 S05753 Brasserie Miroir 0688912806 HT=60,00 TVA=3,60 TTC=63,60
  - inv_id=39851 S05749 DB Kfé SRL 0508863582 HT=472,50 TVA=28,35 TTC=500,85
  - inv_id=39852 S05748 Carrefour Belgium 0448826918 HT=184,36 TVA=11,08 TTC=195,44
  - inv_id=39853 S05746 D-trois SRL 0895931194 HT=305,08 TVA=18,32 TTC=323,40
  - inv_id=39854 S05744 Delhaize (Ferrières) 0402206045 HT=202,16 TVA=12,14 TTC=214,30
  - inv_id=39855 S05743 Sodexo Belgium 0407246778 HT=750,00 TVA=45,00 TTC=795,00
  - inv_id=39856 S05742 Pharmacie Badot 0651311250 HT=271,57 TVA=20,67 TTC=292,24
  - inv_id=39857 S05740 Amessia Boutique 1026857935 HT=85,28 TVA=5,12 TTC=90,40
  - inv_id=39858 S05739 Cocon Life store 0657633274 HT=479,54 TVA=28,78 TTC=508,32
  - inv_id=39859 S05738 Carrefour Market Bastogne 0442412248 HT=274,71 TVA=16,49 TTC=291,20
  - inv_id=39860 S05737 Antheco Intermarché 0828785123 HT=301,12 TVA=18,08 TTC=319,20
  - inv_id=39861 S05724 Autobus Latour 0401403519 HT=169,82 TVA=10,18 TTC=180,00
  - inv_id=39862 S05733 Carrefour Market Remouchamps 0446634817 HT=510,45 TVA=30,62 TTC=541,07
  - inv_id=39863 S05731 Lillodis SRL 0567568873 HT=174,36 TVA=10,48 TTC=184,84
  - inv_id=39864 S05728 Gerpidis SA 0802039451 HT=174,37 TVA=10,48 TTC=184,85
  - inv_id=39865 S05721 Moore Services Financiers 0748770516 HT=200,53 TVA=12,07 TTC=212,60
- TOTAL : HT=7.540,26 EUR | TVA=457,03 EUR | TTC=7.997,29 EUR
- Exclues Peppol non vérifié (8 SO) : S05767/S05730/S05729/S05741/S05722/S05621/S05763/S05727
- Exclues hors périmètre B2B (5 SO) : S05765/S05764/S05726/#48534/#48143 (Amazon/Shopify)
- Confirmé : 0 facture postée, 0 envoi Peppol effectué

## 2026-06-09 — POST OD ventilation 700000 — deux OD postees sur GO explicite Nicolas

- Type : action_post sur deux OD de reclassement canal (brouillons -> posted)
- OD 39813 | MISC/24-25/06/0034 | date 30/06/2025 | 186 554,03 EUR | posted OK
  - Debit 700000 : 186 554,03 | Credits : 700600 GMS 61 805,17 + 700300 Horeca 76 763,73 + 700500 Revendeurs 44 175,77 + 700700 Institutions 3 809,36
- OD 39826 | MISC/25-26/06/0086 | date 09/06/2026 | 821 416,36 EUR | posted OK
  - Debit 700000 : 821 416,36 | Credits : 700600 GMS 305 389,00 + 700300 Horeca 294 159,76 + 700500 Revendeurs 203 890,70 + 700700 Institutions 17 976,90
- Controles pre-post : state=draft, equilibre verifie (ecart 0,00), Tea Touch (6973) absent des deux OD
- Soldes apres post (credit - debit, comptes produits) :
  - 700000 FY24-25 : 83 609,90 EUR (residu Tea Touch + sans partenaire)
  - 700000 FY25-26 : -14 216,99 EUR (flux POS techniques a investiguer — hors perimetre OD)
  - 700600 GMS FY24-25 : 61 805,17 EUR | FY25-26 : 305 389,00 EUR
  - 700300 Horeca FY24-25 : 298 867,08 EUR | FY25-26 : 294 159,76 EUR
  - 700500 Revendeurs FY24-25 : 177 882,05 EUR | FY25-26 : 203 890,70 EUR
  - 700700 Institutions FY24-25 : 3 809,36 EUR | FY25-26 : 17 976,90 EUR

## 2026-06-09 — Ventilation CA B2B 700000 FY24-25 — OD brouillon creee

- Type : creation comptes + OD reclassement (brouillon, non postee)
- Comptes crees :
  - 700600 Ventes GMS (Grande Distribution) — ID Odoo 1220
  - 700700 Ventes Institutions / Corporate — ID Odoo 1221
  - Config : account_type=income, group 700-707, tag_id=1 (identique 700300/700500)
- OD creee : ID Odoo 39813 — journal MISC (ID 11) — date 30/06/2025 — etat DRAFT
  - Ref : Ventilation CA B2B 700000 par canal FY24-25
  - Debit 700000 (ID 320) : 186 554,03 EUR
  - Credit 700600 GMS : 61 805,17 EUR (46 clients GMS + AD Spa)
  - Credit 700300 Horeca : 76 763,73 EUR (NIJSKENS inclus, Vignee Management inclus)
  - Credit 700500 Revendeurs : 44 175,77 EUR (Revendeurs + DTC + dormants + petits non-id)
  - Credit 700700 Institutions : 3 809,36 EUR
  - Total debit = total credit = 186 554,03 EUR — equilibre verifie
- Exclus de l'OD (restent sur 700000) :
  - Tea Touch (ID 6973) : 73 263,98 EUR
  - Lignes sans partenaire : 10 345,92 EUR
  - Total residuel 700000 apres post eventuel : 83 609,90 EUR
- A FAIRE : Nicolas doit poster l'OD explicitement (action_post sur ID 39813)

## 2026-06-09 — Ventilation CA B2B 700000 FY25-26 (YTD) — OD brouillon creee

- Type : OD reclassement canal (brouillon, non postee)
- OD creee : ID Odoo 39826 — journal MISC (ID 11) — date 09/06/2026 — etat DRAFT
  - Ref : Ventilation CA B2B 700000 par canal FY25-26 (YTD)
  - Perimetre : factures out_invoice+out_refund 01/07/2025-09/06/2026 sur 700000
  - Solde total 700000 (factures clients) : 821 416,36 EUR
  - Debit 700000 (ID 320) : 804 364,85 EUR (ventilable certain)
  - Credit 700600 GMS (ID 1220) : 305 389,00 EUR — 93 partenaires
  - Credit 700300 Horeca (ID 915) : 294 159,76 EUR — 243 partenaires
  - Credit 700500 Revendeurs (ID 917) : 186 839,19 EUR — 202 partenaires
  - Credit 700700 Institutions (ID 1221) : 17 976,90 EUR — 80 partenaires
  - Total debit = total credit = 804 364,85 EUR — equilibre verifie
- Exclus de l'OD (restent sur 700000 en attente arbitrage) :
  - Tea Touch (ID 6973) : 0,00 EUR (faillite nov 2025 — aucun CA FY25-26 confirme)
  - Lignes sans partenaire : 0,00 EUR
  - A_ARBITRER (classification incertaine) : 17 051,51 EUR (350 clients, majoritairement personnes physiques sans tag)
- A FAIRE : Nicolas doit poster l'OD explicitement (action_post sur ID 39826)

## 2026-06-09 — OD 39826 FY25-26 — Finalisation ventilation 100% CA B2B

- Type : modification OD brouillon existante (non postee)
- OD modifiee : ID Odoo 39826 — etat DRAFT inchange
- Decision Nicolas/Nira : 17 051,51 EUR A_ARBITRER (350 micro-clients sans tag canal) affectes integralement au canal Revendeur
- Modifications appliquees en une transaction ORM (account.move write, commandes (1, id, vals)) :
  - Ligne 179408 debit 700000 : 804 364,85 -> 821 416,36 EUR
  - Ligne 179411 credit 700500 Revendeurs : 186 839,19 -> 203 890,70 EUR
- Lignes inchangees :
  - Ligne 179409 credit 700600 GMS : 305 389,00 EUR
  - Ligne 179410 credit 700300 Horeca : 294 159,76 EUR
  - Ligne 179412 credit 700700 Institutions : 17 976,90 EUR
- Controle equilibre : debit 821 416,36 = credit (305 389,00 + 294 159,76 + 203 890,70 + 17 976,90) = 821 416,36 EUR | ecart = 0,00 EUR
- Couverture : 100% du CA B2B facture FY25-26 ventile (vs 97,9% avant)
- Tea Touch (0 EUR) et flux POS (OD-RECLASSIF 700006) : absents de l'OD, confirme

## 2026-05-29 — Batch facturation B2B Peppol delta J+1 — 5 factures postées

- Type : facturation B2B hors GMS — wizard `delivered` + envoi Peppol (bucket A) / postée sans envoi (bucket B)
- SO scannées `to invoice` non-GMS : 14 total
- SO exclues GMS (tag GMS sur partner) : S05652 AD Delhaize Roodebeek, S05668 Intermarché Braine, S05643 Intermarché Rumes, S05644 Intermarché Mons
- SO exclues non livrées (qty_delivered=0 sur toutes lignes) : S05643, S05644
- SO exclues B2C (fiscal position EU B2C) : S05621 Jarosz, #48143 Jessica Masula
- SO exclues montant 0€ (100% remise, draft supprimés) : S05600 Café Ventuno, S05454 Marketing Teatower
- Hélène BERTRAND S05192 : déjà facturée le 28/05 (INV/2026/01652). Draft supprimé (ligne MENU 0€ résiduelle).
- B-Shock S05529 : déjà facturé le 28/05 (INV/2026/02728, 264,48 HT). Seule ligne résiduelle = filtres à thé 7,44 HT non encore facturés.

### Transport forcé qty_delivered=qty_ordered
- S05670 line 60308 TRANSPORT : 0→1 (10,00 EUR HT)
- S05666 line 60267 TRANSPORT : 0→1 (10,00 EUR HT)
- S00738 line 4648 TRANSPORT : 0→1 (10,00 EUR HT)

### Bucket A — Peppol OK (peppol_verification_state=valid) — 3 factures
| Facture | Partner | HT | TTC | Peppol state |
|---|---|---|---|---|
| INV/2026/02791 | MaxMara scrl (Max et moi) | 158,12 | 167,60 | processing |
| INV/2026/02794 | B-Shock Coaching - Cravette Cédric | 7,44 | 9,00 | processing |
| INV/2026/02795 | A2MG SRL | 198,12 | 210,00 | processing |
| **Total A** | | **363,68** | **386,60** | |

### Bucket B — Peppol KO (not_verified) — 2 factures — à statuer par Nicolas
| Facture | Partner | HT | TTC | Raison |
|---|---|---|---|---|
| INV/2026/02792 | Douaire Café srl | 160,00 | 169,60 | peppol not_verified |
| INV/2026/02793 | INFRABEL (Invoice Address) | 134,50 | 142,60 | peppol not_verified |
| **Total B** | | **294,50** | **312,20** | |

### Total batch 29/05
- Grand total : HT 658,18 EUR / TTC 698,80 EUR
- Anomalies : S05670 Douaire Café — 1 produit partiellement livré (HC250735 Pêche de vigne, 1 unité non livrée) ; facture partielle émise, solde à facturer à la prochaine livraison.

---

## 2026-05-19 — Facturation masse B2B — 67 SO — INV/2026/02542 à INV/2026/02605

- Type : facturation masse B2B — wizard `delivered` + envoi Peppol/email
- Périmètre : 67 SO (61 clean + 6 partielles avec livraison utile)
- Etape 1 — Transport forcé : 13 SO, 13 lignes TRANSPORT qty_delivered=product_uom_qty OK
- Etape 2 — Wizard facturation (4 batches x 20/20/18/7) : 64 factures draft créées, 0 erreur
  - IDs Odoo : 38243–38306
  - Total TTC : 38 819,04 EUR — Total TVA : 2 042,75 EUR
- Etape 3 — Post en lot (7 batches x 10) : 64/64 postées, 0 erreur
  - Références : INV/2026/02542 à INV/2026/02605
- Etape 4 — Envoi :
  - Peppol (54 factures) : envoi via account.move.send.wizard, mode peppol, UBL BIS 3.0
  - Email fallback (10 factures) : Le Fournil, L'Artiste, PAMPA, Cocoricoop, VENTE-PRIVEE.COM, Carrefour Belgium, La Thé Box, O'Brunch, La Pause Chocolat, Nouvel Air Coiffure
  - Erreurs envoi : 0
- SO exclues (non touchées) : S00738, S04347, S05192, S05454, S05529, S05484, S05582, S05585 (COFFRET partiel livré dans passe delivered), S05587, S05588

## 2026-05-19 — Audit SO B2B en attente de facturation

- Type : audit lecture seule — aucune écriture créée
- Périmètre : 75 SO `to_invoice` filtrées → 60 SO B2B (hors GMS 14, hors Shopify 1)
- Total HT estimé à facturer : 42 564,30 €
- SO urgentes (> 15j) : 10 dont S00738 (370j) et S04347 (183j) — anomalies historiques
- Transport à forcer qty_delivered : 13 SO
- Rapport transmis à Nicolas (texte agent, 2026-05-19)

## 2026-05-18 — Rapport commission Jérôme Carlier — Avril 2026 (v2 officiel)

- Type : rapport commission — vérification Odoo + adoption chiffres Adri
- Source : `Commission_avril_2026 (1).docx` (Adri) + Odoo XML-RPC (18/05/2026)
- Fichiers produits :
  - `compta/reports/2026-05-18_commission_jerome_avril2026.md`
  - `Teatower-Planning/commission/avril-2026/index.html` (v2 — remplace brouillon obsolète 04/05)
- Commit + push : 109974f (Teatower-Planning master)
- Résultat : 2 420 € brut (Version A — grossiste 130 € Adri) ou 2 290 € (Version B — grossiste 65 € mémoire stricte)
- Validation requise : règle grossiste 130 € à confirmer par Nicolas avant envoi Jérôme
- CA B2B Odoo avril 2026 : 67 672,19 € HT / CA Adri : 73 805 € / Croissance Adri : +16,2 % → 400 €

## 2026-04-30 — Batch facturation run 6 — 17 factures draft (SO S05487–S05513)

### Correction lignes transport (nouvelle règle : transport = service, toujours facturer si marchandise partie)
- S05497 Alcodis SA : line_id=56472 qty_delivered 0→1 (TRANSPORT 10,00 EUR HT)
- S05504 Al Picchio Rosso : line_id=56550 qty_delivered 0→1 (TRANSPORT 10,00 EUR HT)
- S05505 Le Coin 62 : line_id=56556 qty_delivered 0→1 (TRANSPORT 10,00 EUR HT)
- Delta total correction transport : +30,00 EUR HT / +36,30 EUR TTC

### SO exclus du batch (qty_delivered=0 sur toutes les lignes)
- S05509 BLONFOOD SA Intermarché Liège Blonden : 0 livré
- S05510 Gemblouxim Intermarché Gembloux : 0 livré

### Factures draft créées (IDs 37146–37162) — mode delivered — wizard sale.advance.payment.inv
- 17 factures draft | Total HT : 6 147,54 EUR | Total TTC : 6 538,80 EUR
- Regroupements par partner : S05489+S05490 (Delhaize affilié), S05494+S05495+S05499 (Smartbox), S05507+partenaire facturation

### Posting + envoi Peppol/Email (2026-04-30) — GO Nicolas
- 17/17 factures postées (action_post) — INV/2026/02329 à INV/2026/02345
- Partners modifiés (invoice_sending_method peppol activé) : Al Picchio Rosso (2783), Srl D'Ici Wépion (3248), Newpharma Compta (5459), Alivim SRL (123294)
- Envoi Peppol (11 factures) : INV/02329, 02330, 02331, 02332, 02333, 02334, 02336, 02338, 02340, 02342, 02344, 02345 — état=processing
- Fallback email (5 factures, peppol non valide) :
  - INV/02335 Musée de la fraise (peppol not_valid)
  - INV/02337 Smartbox Group (partenaire IE, peppol not_valid)
  - INV/02339 Alcodis SA (peppol not_verified)
  - INV/02341 DelEmbourg SRL (peppol not_verified)
  - INV/02343 CPSP Belgie NV (peppol not_verified)
- Aucune erreur d'envoi — 0 facture bloquée

---

## 2026-04-29 — Lettrage SEPA Kirchner Fischer (SL 17572 + SL 18090)

### (B) Lettrage SEPA Kirchner Fischer — 2 domiciliations

**SL 17572 — 30/03/2026 — -20 606,47 EUR — CAS B PARTIEL**
- Diagnostic : RESA562 avait 3 501,93 EUR deja lettres via BNK1/25-26/4199 (SL 17341, 18/03/2026, partial.reconcile id=11475). Residuel reel = 6 046,70 EUR, pas 9 548,63 EUR.
- Action : move BNK1/25-26/4385 (id=35216) remis en draft, compte suspense 499000 remplace par :
  - 440000 debit 6 046,70 EUR (RESA562 partiel) -> reconcile avec line 122154 -> RESA562 paid
  - 440000 debit 11 057,84 EUR (RESA564) -> reconcile avec line 122914 -> RESA564 paid
  - 499000 debit 3 501,93 EUR -> SUSPENSE residuel (ces 3501.93 correspondent a un paiement anterieurement applique sur RESA562 via une autre SL, a pointer dans la meme SL bancaire par Nicolas)
- Ecritures creees : move lines 163592, 163593, 163594 dans BNK1/25-26/4385

**SL 18090 — 22/04/2026 — -18 451,00 EUR — CAS C**
- Diagnostic : RESA734 (RGK26-00690) residuel facture = 6 105,30 EUR vs communication Kirchner = 5 944,74 EUR -> ecart +160,56 EUR. Aucun avoir ou partial reconcile existant. Origine non identifiee.
- Action : move BNK1/25-26/4798 (id=36792) remis en draft, compte suspense 499000 remplace par :
  - 440000 debit 11 969,66 EUR (RESA506) -> reconcile avec line 125260 -> RESA506 paid
  - 440000 debit 536,60 EUR (RESA735) -> reconcile avec line 125262 -> RESA735 paid
  - 499000 debit 5 944,74 EUR -> SUSPENSE RESA734 (ecart 160,56 a clarifier avec Kirchner)
- Ecritures creees : move lines 163595, 163596, 163597 dans BNK1/25-26/4798

**Residuels a traiter manuellement par Nicolas :**
1. SL 17572 : 3 501,93 EUR en suspense (499000) = paiement deja applique sur RESA562 via SL 17341 -> verifier si la SL 17341 est bien une domiciliation separee ou double-comptabilisation
2. SL 18090 : 5 944,74 EUR en suspense (499000) = RESA734 (6 105,30) non lettree -> ecart 160,56 EUR a clarifier avec Kirchner (avoir ? majoration ? note de debit ?)

**Factures lettrées ce batch :** RESA562 + RESA564 + RESA506 + RESA735 = 29 610,80 EUR TTC
**PAY00569 cancelled** (cree par erreur en debut de session, annule avant tout impact)

---

## 2026-04-29 — Lettrage 7 quick wins + diagnostic SEPA Kirchner

### (A) Lettrage 7 factures clients
- Méthode : account.payment.register wizard + write payment_ids sur statement line
- PAY00562 INV/2026/01848 1262.98 EUR Ramaut — SL 18118 du 23/04
- PAY00563 INV/2026/01549 1113.00 EUR Sorescol S.A. — SL 17908 du 14/04
- PAY00564 INV/2026/01675 651.90 EUR Sorescol S.A. — SL 18055 du 21/04
- PAY00565 INV/2026/02152 539.00 EUR Lambertdis SRL — SL 18158 du 27/04
- PAY00566 INV/2026/02141 477.00 EUR Le 7 by Juliette — SL 18164 du 27/04
- PAY00567 INV/2026/01511 333.22 EUR Wonka / Intermarche Heusy — SL 18165 du 27/04
- PAY00568 INV/2026/01590 277.00 EUR Sandrinette / Delonville — SL 18161 du 27/04
- Total lettre : 4 653.10 EUR TTC — 7 factures en state=in_payment

### (A) Skip 3 QW — raisons
- QW06 (Mardis 462.02 / Carrefour 462.02) : IBAN BE66... appartient a Mardis partner 3120, facture sur Carrefour corporate 6596 et Mardis a une facture a 462.03 (ecart 0.01 EUR) — mis en review
- QW07 (Cafes Delahaut 397.50) : pas d'IBAN dans la ligne bancaire, critere C3 non verifiable
- QW08 (Pure Bastogne 389.56) : idem, pas d'IBAN dans la ligne bancaire

### (C) Correction partner_id — 0 ligne modifiee
- 83 lignes sans partner_id examinées : 75 noms bancaires abrégés sans match exact Odoo, 8 sans partner_name

## 2026-04-22 — Batch facturation run 5 — 51 factures (INV/02178–02228)

- Type : creation + posting via wizard sale.advance.payment.inv mode=delivered
- SO eligibles : 59 (qty_delivered > qty_invoiced sur au moins une ligne)
- Ecarte : 2 Hyper Carrefour (S05457, S05459 — livraison semaine 04/05) + 3 qty_delivered=0 (S05404, S05412, S04443)
- Wizard : 54 factures draft crees (regroupement par partenaire Odoo)
- Postees : 51 factures — INV/2026/02178 a INV/2026/02228
- Non postees (TTC=0) : 3 — S05441 Cafes Delahaut, S05400 Laetitia Mariette, S05427 Sefora Jacobs
- Total HT : 8 720,02 EUR | TVA : 523,41 EUR | TTC : 9 243,43 EUR
- Rapport : compta/reports/2026-04-22.md

## 2026-04-21 — Complement batch facturation S05435 + S05436 (2 factures — run 4)

- Type : creation + posting + envoi Peppol (2 SO, 2 factures Odoo)
- Source : S05435 et S05436 signalees par Nicolas — pickings TT/PICK/08690 et 08691, type=internal, state=done (meme pattern runs 2-3)
- Methode : creation manuelle account.move ligne par ligne, action_post, account.move.send.wizard (ubl_bis3)
- Facture S05435 : id=36556, INV/2026/02169 — Floridis SA - Intermarche Floriffoux (id=2958) — 410,19 EUR HT / 436,31 EUR TTC — echeance 2026-05-21 — Peppol processing (peppol_verification_state=valid)
- Facture S05436 : id=36557, INV/2026/02170 — Affilie 043366 - AD Fosses-la-Ville (id=5441) — 408,22 EUR HT / 434,22 EUR TTC — echeance 2026-06-20 (60j) — Peppol processing (peppol_verification_state=not_verified, a surveiller)
- TRANSPORT ajoute sur les 2 factures (10 EUR HT, compte 700000, TVA 21%)
- Total run 4 : 818,41 EUR HT / 870,53 EUR TTC
- Total cumule jour : 10 136,10 EUR HT / 10 771,02 EUR TTC (28 factures, runs 1+2+3+4)
- Rapport : compta/reports/invoicing_batch_2026-04-21.md (section "Complement S05435 + S05436 — run 4")

## 2026-04-21 — Complément batch facturation S05434 (1 facture — run 3)

- Type : création + posting + envoi (1 SO, 1 facture Odoo)
- Source : S05434 signalée par Nicolas — picking TT/PICK/08689 type=internal/done (même cause que run 2)
- Méthode : création manuelle account.move, action_post, account.move.send.wizard (ubl_bis3)
- Facture créée : id=36545, INV/2026/02168
- Partenaire : SRL Spydis - Intermarche Spy (id=116686)
- Montant HT : 315,10 EUR (305,10 SO + 10 TRANSPORT) | TTC : 335,51 EUR
- Echéance : 2026-05-21 (30 jours)
- Envoi Peppol : peppol_verification_state=valid — partner forcé invoice_sending_method=peppol — peppol_move_state=processing
- Total cumulé jour : 9 317,69 EUR HT / 9 900,49 EUR TTC (26 factures, runs 1+2+3)
- Rapport : compta/reports/invoicing_batch_2026-04-21.md (section "Complement S05434 — run 3")

## 2026-04-21 — Complément batch facturation S05448–S05453 (5 factures — run 2)

- Type : création + posting + envoi batch (5 SO, 5 factures Odoo)
- Source : SO confirmés par Nicolas — pickings internal done (TT/PICK/08711, 08713, 08714, 08715, 08716)
- Méthode : création manuelle account.move (wizard delivered inapplicable — pickings type=internal), action_post, account.move.send.wizard
- Note méthode : le wizard sale.advance.payment.inv refuse car les pickings sont de type internal et non outgoing — création ligne par ligne avec qty_delivered et discount=30% repris des SO
- Factures créées : 5 (IDs Odoo 36540–36544)
- Numéros attribués : INV/2026/02163 à INV/2026/02167
- Montant total HT : 1 770,30 EUR | TTC : 1 884,05 EUR
- TRANSPORT ajouté : 5 factures (10 EUR HT, compte 700000, TVA 21% — absent des SO)
- Lignes EM0072 (SRP Kraft Horeca) : conservées avec disc=100% (subtotal=0) comme dans les SO
- Envoi Peppol (UBL BIS3) : 5 factures toutes en peppol_state=processing
  - INV/02163 (Delhaize de Bouge, id 36540) — uuid f7eb688b-9214-4a8b-98f8-f79d7da30066 — échéance 2026-06-20 (délai Delhaize 60j)
  - INV/02164 (BOISDIS Naninne, id 36541) — uuid 700b53f5-0f18-4194-b6c8-1df4c3da4b94
  - INV/02165 (BOISDIS Naninne, id 36542) — uuid 0fb63a93-dd91-4f56-a4cf-98ea4cee4e39
  - INV/02166 (SA Barthe Assesse, id 36543) — uuid 26b4776f-6ac1-44ac-ad91-10d0fd26e293
  - INV/02167 (Lambertdis Spar Manhay, id 36544) — uuid d0ee1e08-6b97-4157-8c41-e06c29a79b1a
- Rapport : compta/reports/invoicing_batch_2026-04-21.md (section "Complément 5 SO — run 2")

## 2026-04-21 — Batch facturation S05351–S05439 (20 factures)

- Type : création + posting + envoi batch (23 SO, 20 factures Odoo)
- Source : sale.order invoice_status=to_invoice, state=sale/done, picking outgoing done
- Méthode : sale.advance.payment.inv wizard (delivered), action_post, account.move.send.wizard
- Factures créées : 20 (IDs Odoo 36509–36528)
- Numéros attribués : INV/2026/02137 à INV/2026/02156
- Montant total HT : 7 232,29 EUR | TTC : 7 680,93 EUR
- Corrections avant posting : 5 lignes supprimées (I0880 x3, I0859 x1, I0376 x1) — qty_delivered=0 inclus par erreur dans le wizard
- Partenaires forcés peppol : 5 (Lambertdis, NDB Diffusion, PGHM, Le 7 by Juliette, Labrassine)
- Envoi Peppol (UBL BIS3) : 9 factures — INV/02137 (Cafés Préko, 75ca7ecd), INV/02138 (DB Kfé, 37eab94a), INV/02139 (Delhaize, 28e8393f), INV/02141 (Le 7 Juliette, 90c3b497), INV/02152 (Lambertdis, 06a1b47b), INV/02153 (NDB Diffusion, cec483d4), INV/02154 (Villa d'Olne, a646b0b7), INV/02155 (PGHM, d0829a62), INV/02156 (Labrassine, 3266785d) — statut : processing
- Envoi email : 9 factures — INV/02140 (La Thé Box), INV/02143 (Alcodis), INV/02144 (Cafes Delahaut), INV/02145 (Sunparks De Haan), INV/02146 (Volle Gas), INV/02147 (Carrefour Remouchamps), INV/02148 (Carrefour Belgium), INV/02149 (BTL SRL), INV/02150 (Virelles Nature)
- Non envoyées : 2 — INV/02142 (Smartbox Group, 60 EUR), INV/02151 (Clotuche Caroline Suzanne, 28 EUR) — pas d'email ni Peppol valide
- Review : S05424 Marketing Teatower (707,55 EUR HT, partenaire interne, action Nicolas requise)
- Sans livraison (non traitées) : 19 SO (S05404, S05412, S05425, S05426, S05429, S05434, S05435, S05436, S05440, S05442, S05444, S05445, S05447–S05453)
- Rapport scan : compta/reports/shipped_not_invoiced_2026-04-21.md
- Rapport batch : compta/reports/invoicing_batch_2026-04-21.md

## 2026-04-15 — Batch S05405-S05409 : correction renvoi Peppol (3 factures)

- Type : correction invoice_sending_method + renvoi Peppol
- Partenaires mis à jour (invoice_sending_method -> peppol) : SA VILLERSEM (115879), DelEmbourg invoice addr (5733), DelEmbourg parent (2909), SA Faimine invoice addr (9196), SA Faimine parent (3210)
- INV/2026/02094 (DelEmbourg) — peppol_state=processing | uuid=2dc8107b-51cc-45dc-98f8-62aeab83dd4c
- INV/2026/02095 (SA Faimine) — peppol_state=processing | uuid=a4cf80f7-24c5-4b50-a50d-d6a915855a2c
- INV/2026/02096 (SA VILLERSEM) — peppol_state=processing | uuid=f58a082f-029c-48c1-972d-ef807690dfa2
- Rapport : compta/reports/batch_S05405_S05409_2026-04-15.md

## 2026-04-15 — Batch facturation S05405–S05409

- Type : création + posting + envoi batch (5 SO)
- Source : S05405 / S05406 / S05407 / S05408 / S05409 — tous state=sale, tous entièrement livrés
- Méthode : sale.advance.payment.inv wizard (delivered), action_post, account.move.send.wizard
- Factures créées : 5 (IDs Odoo 36242–36246)
- Numéros attribués : INV/2026/02092 à INV/2026/02096
- Montant total HT : 1 240,03 EUR | TTC : 1 314,43 EUR
- Envoi Peppol : 2 factures — S05405 (BARVO/Carrefour Barvaux, uuid 8caf61ac) + S05408 (GIMALEX/Delhaize Fragnée, uuid 9766cd23) — statut : processing
- Envoi email : 3 factures — S05406 (SA VILLERSEM), S05407 (SA Faimine), S05409 (DelEmbourg)
- Fallback email : S05406 + S05409 (Peppol EAS/endpoint configurés sur partenaire mais invoice_sending_method non défini)
- Rapport : compta/reports/batch_S05405_S05409_2026-04-15.md

## 2026-04-15 — Batch facturation : TRANSPORT + Posting + Envoi

- Type : correction transport + validation + envoi batch
- Lignes TRANSPORT ajoutées : 2 nouvelles factures draft créées (Odoo 36236, 36237) pour S05403 (Volle Gas) et S05375 (Carrefour Remouchamps) — 10 EUR HT chacune, produit [TRANSPORT], compte 700000, TVA 21%
- Les 7 autres lignes TRANSPORT des SO concernés étaient déjà facturées (qty_inv=1)
- action_post : 36 factures postées (IDs 36200–36237, hors avoirs 36223/36235) — 0 échec
- Numéros attribués : INV/2026/02055 à INV/2026/02090
- Montant total HT batch complet : 14 581,15 EUR | TTC : 15 482,38 EUR
- Envoi Peppol : 14 factures (Van Der Valk, ILLICO RESTO, Europadrinks, Delhaize x2, Pascal CHERAIN, Moulins Burette, Cafés Antillia, Spinée SA, All in One, SRL Tartine, Au Comptoir Local, Smart fridges, Carrefour Remouchamps TRANSPORT)
- Envoi email : 21 factures
- Non envoyé : 1 (INV/2026/02077 — Clotuche Caroline Suzanne, id=122331, pas d'email ni Peppol)
- Rapport mis à jour : compta/reports/invoicing_batch_2026-04-15.md

## 2026-04-15 — Batch facturation (34 factures draft créées)

- Type : création factures clients batch
- Source : sale.order invoice_status=to_invoice, state=sale/done (85 SO scannés)
- Méthode : sale.advance.payment.inv wizard, mode "delivered" (qty_delivered)
- Factures draft créées : 34 (IDs Odoo 36200–36234 sauf 36223/36235 qui sont des avoirs)
- Montant total HT : 14 561,15 EUR | TTC : 15 461,18 EUR
- Exclus Amazon : 36 SO (741,40 EUR HT) — détectés via origin "Amazon Order"
- Exclus 0 EUR : 5 SO (Marketing Teatower, Newpharma, Laetitia Mariette, Perte marchandise)
- Exclus sans livraison : 8 SO (3 403,22 EUR HT en attente livraison)
- Avoirs draft détectés : 2 (36223 ann philippe verhelle, 36235 Lidwine Fetten) — à examiner
- Rapport : compta/reports/invoicing_batch_2026-04-15.md
- Statut : DRAFT — Nicolas doit valider (action_post) avant envoi

## 2026-04-15 — Rapport commandes expédiées non facturées

- Type : analyse / rapport
- Source : sale.order (state: sale/done, invoice_status: to invoice, picking outgoing: done)
- Résultat : 70 SO to_invoice identifiées, dont 70 avec au moins un outgoing picking done
- Montant total HT : 14 173,10 EUR
- Rapport : compta/reports/shipped_not_invoiced_2026-04-15.md
- Top 3 : The Torrefactory Project Sa (1 950 EUR) / Carrefour Belgium (1 646 EUR) / Moulins Burette (1 406 EUR)
- Alerte : 34 commandes e-commerce de déc. 2025 (> 120 jours) non régularisées

## 2026-04-14 — Rapprochement bancaire ING (165 lignes)

### Identification des 165
- Source : `account.bank.statement.line` is_reconciled=False, journal ING BE30 3631 6408 2311 (id=14)
- Composition : 165 lignes ING uniquement (+ 77 autres journaux cash/caisse non traitées)
- Positives (encaissements) : 63 — Négatives (paiements) : 102

### Matches sûrs trouvés : 11
Critères : même montant exact (écart ≤ 0,01 EUR), même partenaire (direct ou commercial_parent), date BSL dans [date_facture - 5j, date_facture + 180j]

| BSL id | Date | Montant | Facture | Partenaire | Résultat |
|--------|------|---------|---------|------------|---------|
| 17823 | 2026-04-10 | +403,97 EUR | INV/2026/01151 | Belgradis - Intermarché Belgrade | lettré |
| 17827 | 2026-04-10 | +181,26 EUR | INV/2026/01521 | Les Mignées (via Quoibion Gestim) | lettré |
| 17813 | 2026-04-09 | +1 792,19 EUR | INV/2026/01178 | Pharmacie Saint Pierre SA | lettré |
| 17800 | 2026-04-09 | +90,00 EUR | INV/2026/01415 | l'Apaq-W | lettré |
| 17772 | 2026-04-08 | +345,10 EUR | INV/2026/01258 | SA Barthe - Intermarché Assesse | lettré |
| 17771 | 2026-04-08 | +715,50 EUR | INV/2026/01308 | Sorescol S.A. | lettré |
| 16934 | 2026-03-01 | -31,00 EUR | RESA670 | ING Belgique SA | lettré |
| 16651 | 2026-02-16 | -281,85 EUR | RESA573 | Easyplug S.R.L. / Ez Charge | lettré |
| 16646 | 2026-02-16 | -46,88 EUR | RESA671 | Action Belgium BVBA | lettré |
| 16398 | 2026-02-04 | -112,56 EUR | RESA686 | Happy Family Wouip | lettré |
| 16118 | 2026-01-21 | -14,52 EUR | RESA532 | ING Belgique SA | lettré |

**Total lettrés : 11 / 11 matches sûrs (100%)**

### Méthode technique utilisée
1. `account.move.line.write([susp_ml_id], {'account_id': acct_receivable_or_payable, 'partner_id': partner_id})` — remplace la ligne compte de passage (499000) par le compte tiers correct
2. `account.move.action_post([bsl_move_id])` — reposte l'écriture après modification
3. `account.move.line.reconcile([susp_ml_id, invoice_ml_id])` — lettrage des deux lignes tiers

### Résultat
- ING non rapprochées avant : 165
- ING non rapprochées après : 154
- Lettrées automatiquement : 11
- En review : 27 (Vilna Gaon x3, Shyfter ambigus x2, ING frais ambigus x3, partenaires sans facture ouverte x19)
- Sans partenaire ni match : 127

### Fichiers générés
- `compta/review/lettrages_review_2026-04-14.md` — détail des 27 cas en attente
| 2026-04-14 | 367 | - |
