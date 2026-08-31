# Lettrage ING + Belfius — 31/08/2026

**Demande** : « lettre tout ING et Belfius, tu sais quoi faire pour les clients ».
**Périmètre** : journaux 14 (ING BE30 3631 6408 2311) et 36 (Belfius BE86 0689 5807 1350).
**Résultat** : **108 → 102** lignes non lettrées. 6 opérations, 0 erreur.

Script : `compta/lettrage_29_ing_belfius_20260831.py` (dry-run puis `apply`).
Outils : `compta/scan_lettrage_20260831.py`, `compta/match_lettrage_20260831.py`.

---

## Ce qui a été traité

| BSL | Date | Montant | Traitement | Pièce / clé |
|---|---|---|---|---|
| ING 20602 | 26/08 | +378,00 | Lettré | `INV/2026/03921` Le Pressoir Ardennais — comm. `***000/0044/70787***`, montant exact |
| ING 20658 | 29/08 | +222,72 | Lettré | `INV/2026/03896` SAVEDIS / Spar Barvaux — comm. `***000/0044/60582***`, montant exact |
| ING 20623 | 27/08 | +198,11 | Lettré | `INV/2026/03647` Centrale Intermarché — écart +0,01 → write-off 757100 `OD 45338` |
| ING 20617 | 26/08 | +9,81 | Repointé 580003 | Edenred — titres-repas boutiques |
| ING 20653 | 28/08 | +31,95 | Repointé 580003 | Edenred — titres-repas boutiques |
| ING 20568 | 25/08 | −15 000,00 | Repointé 580000 + lettré | Virement interne ING → Belfius, contrepartie BSL 20561 du 26/08 |

### Le cas ITM / Centrale Intermarché — la piste écartée le 27/08 était la bonne

Les passes des 24 et 27/08 avaient classé les virements *ITM Alimentaire Belgium SA*
(IBAN BE75 3701 0623 0851) comme « paiements de centrale non identifiables, exiger l'avis »,
et avaient explicitement écarté le match au centime près comme une coïncidence.

Le **grand livre 400000 de Centrale Intermarché (#124363)** invalide cette lecture. Deux
paiements ITM y sont déjà lettrés, facture par facture, avec le même arrondi au centime :

| Paiement | Facture | Écart | Traitement |
|---|---|---|---|
| BSL 20070 du 30/07 — 675,02 | `INV/2026/03297` du 30/06 (675,00) | +0,02 | write-off 757100 `MISC/26-27/08/0003` |
| BSL 20185 du 06/08 — 123,10 | `INV/2026/03420` du 08/07 (123,10) | 0,00 | — |

ITM paie donc **une facture à la fois, à J+29/31**. Le virement du 27/08 (198,11) tombe sur
une facture de 198,10 — mais il y en a **deux ouvertes** : `INV/2026/03647` (27/07) et
`INV/2026/03923` (19/08). Retenue : **`INV/2026/03647`**, sur double corroboration — FIFO,
et la cadence J+31 (27/07 → 27/08) alors que 03923 se paierait vers le 18/09.

**Restent bloqués**, faute de pièce correspondante : 637,24 (09/07, réf 0000287398) et
160,61 (13/08, réf 0000290027). Aucune facture Intermarché — centrale ou point de vente —
n'existe à ces montants, ni aucune combinaison ≤3 pièces. `INV/2026/04002` (160,60) est datée
du **26/08**, elle n'existait pas au 13/08 : ce n'est pas le match.

> **À faire** : réclamer à ITM les avis 0000287398 et 0000290027 (797,85 € au total).

### Virement interne 15 000 €

Le côté Belfius (BSL 20561, 26/08) avait été repointé sur **580000** le 26/08, la contrepartie
ING n'étant pas encore importée. Elle l'est maintenant (BSL 20568, 25/08) : le côté ING a été
miroité sur 580000 et les deux lignes lettrées. Le compte de transfert revient à zéro sur cette
opération.

---

## Non traité — pièce ou arbitrage manquant

### Encaissements clients bloqués — 5 260,38 €

| Ligne | Date | Montant | Blocage |
|---|---|---|---|
| ING 20381 Delhaize Le Lion | 14/08 | +2 652,97 | Avis `/ADV/2000058526` cité dans le libellé, document manquant. Subset-sum ≤4 sur 93 pièces ouvertes = **4 solutions**, aucune unique |
| ING 20651 Delhaize Le Lion | 28/08 | +1 809,56 | Avis `/ADV/2000062072` cité, document manquant. Subset-sum ≤4 = **44 solutions** |
| ING 19660 ITM Alimentaire | 09/07 | +637,24 | Avis 0000287398 — 0 combinaison |
| ING 20373 ITM Alimentaire | 13/08 | +160,61 | Avis 0000290027 — 0 combinaison |

> Delhaize cite systématiquement un n° d'avis (`/ADV/2000…`) mais l'avis n'est jamais versé au
> dossier. **Deux avis manquants** immobilisent maintenant 4 462,53 €. Demander l'accès au portail
> fournisseur Delhaize réglerait le problème à la source.

### Autres crédits non lettrés — hors clients

| Ligne | Date | Montant | Nature |
|---|---|---|---|
| BELF 19188 | 10/06 | +30 000,00 | Tirage du prêt Belfius n° 071-9574936-30 |
| BELF 20350 | 14/08 | +10 000,00 | Prêt actionnaire **Nira Solutions** |
| BELF 20353 | 14/08 | +30 000,00 | Prêt actionnaire **Jean-Noël Tilman** |
| ING 20522 | 21/08 | +41,21 | Settlement Amazon (SLR4RLYM9OWD9M53) → rapport Amazon, pas une facture |
| ING 19992 | 27/07 | +0,01 | Virement test iPiD Europe |

> **Arbitrage toujours en attente (3e rappel)** : les deux prêts actionnaires (40 000 €) n'ont pas
> de compte courant dédié. Seuls `489020` (C/C NOE NATURE) et `489030` (C/C TEA TOUCH) existent.
> Il faut créer `489040` Nira Solutions et `489050` J.-N. Tilman — ou trancher pour 416100/489100.

### Décaissements fournisseurs bloqués

**Kirchner Fischer — 162 353 € ouverts sur 47 pièces.** Trois décaissements en attente :
12 837,54 (08/07), 49 551,11 (14/08), 9 912,97 (27/08).

- 12 837,54 et 49 551,11 : **0 combinaison** ≤4 pièces. Rien d'exploitable sans l'avis.
- 9 912,97 : le libellé SEPA cite `Z 008-004, 7.812,20`, `Z 008-004, 5,50` et
  `R RG K26-04484, 723,75`. Seul le troisième existe dans Odoo (`RESA969`, ref `RGK26-04484`,
  723,75 exact). Les trois montants cités totalisent 8 541,45 ≠ 9 912,97 : **le libellé est
  tronqué** (limite 140 caractères SEPA). Le subset-sum donne 4 solutions, dont **aucune** ne
  contient RESA969 — donc toutes fausses. Non lettré : lettrer les seuls 723,75 laisserait
  9 189,22 € d'avance fournisseur sans pièce.

> **À faire** : réclamer les avis Kirchner du 07/07, 14/08 et 27/08. Avec 162 k€ ouverts et un
> flux mensuel à 6 chiffres, ce compte fournisseur ne peut pas rester lettré à l'aveugle.

**Autres** : sinas GmbH 1 591,81 (26/08) — 2 factures ouvertes pour 2 225,91, aucune combinaison.
CILE 59,00 — aucune facture d'achat encodée. Belfius : les 3 factures RESA à 5,14 (832/894/1047)
ne correspondent à aucun prélèvement, et aucune RESA n'existe pour les frais de tenue de compte
(4,42 / 3,08 / 15,00 / 39,83) ni pour les charges de crédit (706,91 / 273,64 / 410,46 / 2 559,85,
récurrentes depuis mai). Ces dernières appellent une OD de charges financières — **pas d'écriture
sans ton accord**.

**Domiciliations sans facture d'achat encodée** (Google, Adobe, Shopify, Intuit, Worldline,
Sendcloud, Proximus, Skeepers, Radius, Meta) : inchangé, rien à lettrer, cf. mémoire méthode.

---

## État après la passe

- **102** lignes non lettrées ING + Belfius (62 ING / 40 Belfius), dont **9 crédits** pour 75 301,60 €
  — dont 70 000 € de prêts en attente d'arbitrage de compte.
- Encaissements clients réellement bloqués : **4 lignes, 5 260,38 €**, toutes en attente d'un avis
  de paiement (Delhaize ×2, ITM ×2).
