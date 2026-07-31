# Revue lettrage ING — 31/07/2026 (encaissements clients)

Script : `compta/lettrage_13_ing_20260731.py` (dry-run puis `--apply`).
Périmètre : uniquement les lignes **au crédit** (encaissements clients) sur BNK1
(ING BE30 3631 6408 2311), suite au lot du 29/07
(`compta/lettrage_12_ing_20260729.py` + `compta/review/lettrage_ing_20260729_review.md`).
44 lignes ING non rapprochées au total au moment du scan ; 2 nouvelles lignes clients lettrées,
le reste (débits fournisseurs/frais + encaissements déjà documentés ambigus) est hors périmètre
de cette demande ou inchangé depuis le 29/07.

Règle d'écart : écart ≤ **5,00 €** → write-off `657100`/`757100` ; écart > 5,00 € → lettrage
**partiel** sans write-off. Aucun des 2 cas traités n'a nécessité de write-off (écart nul).

## Lignes lettrées (2)

| BSL | Date | Montant | Client | Document(s) | Écart | Traitement |
|---|---|---|---|---|---|---|
| 20051 | 29/07 | 229,60 | Carrefour Market Remouchamps | INV/2026/03619 (229,60) | 0,00 | lettrage exact |
| 20028 | 28/07 | 1 549,30 | Cafés Préko s.a. | INV/2026/03215 (296,80) + INV/2026/03132 (278,25) + INV/2026/03086 (974,25) | 0,00 | lettrage groupé exact |

**20051** : le virement émane de "FONVAL" (compte BE16068244085874), pas du nom commercial du
magasin — cohérent avec un virement effectué par le titulaire/la société civile propriétaire de
la franchise Carrefour Market Remouchamps. Identifié sans ambiguïté par la communication
structurée belge `***000/0043/24075***`, qui correspond exactement au `payment_reference` de
INV/2026/03619 (229,60 pile).

**20028** : le libellé du virement instantané cite explicitement les 3 factures
(`Communication : INV/2026/03215-INV/2026/03132-INV/2026/03086`), dont la somme
(296,80 + 278,25 + 974,25 = 1 549,30) tombe pile sur le montant reçu.

## Non lettrées — à arbitrer (2 nouvelles)

- **20026 MOMIDISTRI SA +688,87** — le virement reprend la communication structurée
  `***000/0040/27924***`, qui correspond à `INV/2026/03056` (Spar Momignies, 688,89) — **mais
  cette facture est déjà soldée depuis le 20/07** (BSL BNK1/26-27/0301, même communication,
  full_reconcile 13801). Spar Momignies n'a **aucune** autre facture ouverte actuellement.
  Deux lectures possibles : double paiement du client (même communication réutilisée par erreur),
  ou la ligne du 20/07 était en réalité un paiement différent mal imputé. **Ne pas lettrer contre
  une facture déjà fermée** — nécessite un arbitrage (contact client ou vérification du relevé
  papier) avant toute action (remboursement, avoir, ou nouvelle facture à émettre).
- **20008 DELWOL +0,02** — la communication structurée `***000/0042/65471***` coïncide par
  hasard avec `INV/2026/03523` (AD Delhaize Roodebeek, 539,30, déjà payée) : montant totalement
  incompatible. Même phénomène que le cas iPiD documenté le 29/07 (coïncidence de communication
  structurée, pas une vraie correspondance) — très probablement un micro-dépôt de vérification
  bancaire. Ne pas lettrer.

## Non lettrées — hors flux clients (2 nouvelles, même catégorie que le 29/07)

- **20052 PLUXEE BELGIUM +6,85** et **20050 EDENRED BELGIUM +19,66** — opérateurs de titres-repas,
  même catégorie que 19630 (Baloise), 19652/19771 (Pluxee), 19826 (Edenred) déjà documentés le
  29/07. Pas de facture client correspondante à chercher.

## Inchangées depuis le 29/07 (toujours non reconciliées, aucune nouvelle info)

- **19466 NANRETAIL +675,58** — communication réutilisée d'une facture déjà payée ; écart de
  12,38 avec les 2 factures ouvertes du client (663,20). Ambigu, non lettré.
- **19660 ITM ALIMENTAIRE (Centrale Intermarché) +637,24** — aucune combinaison jusqu'à 4 des
  7 factures ouvertes ne tombe sur ce montant. Probable retenue centrale à documenter.
- **19784 Smartbox +67,00** — aucune combinaison sur 50 factures ouvertes, références du libellé
  introuvables dans Odoo.
- **19952 DYNAMIC FOOD +436,84** — 521,54 (déjà soldé le 15/07) − 84,70 (note de crédit ouverte)
  = 436,84 pile ; nécessite arbitrage (double paiement ou paiement du 15/07 mal imputé).
- **19992 iPiD +0,01** — micro-dépôt de vérification bancaire, pas une facture.

## Hors périmètre de cette demande (débits fournisseurs/frais)

Le scan a aussi remonté des lignes au débit (fournisseurs, frais, avances salaires) non traitées
ici puisque la demande portait explicitement sur les encaissements clients. Note pour un prochain
tour fournisseurs : **BSL 20044 Kirchner, Fischer + Co GmbH (−12.087,45)** cite explicitement
`RGK 26-02871 (11.735,45)` + `RGK26-03856 (352,00)` = 12.087,45 pile dans le libellé SEPA —
candidat propre pour un lettrage fournisseur direct.
