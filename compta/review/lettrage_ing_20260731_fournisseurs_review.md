# Revue lettrage ING — 31/07/2026 (2e passe, débits fournisseurs + autres flux)

Script : `compta/lettrage_14_ing_20260731_fournisseurs.py` (dry-run puis `--apply`), en
complément de `compta/lettrage_13_ing_20260731.py` (2 encaissements clients). Demande élargie
par Nicolas : lettrer tout ce qui est lettrable dans ING, y compris les débits fournisseurs et
tout flux ayant une contrepartie déjà ouverte en compta.

**Règle dure appliquée strictement** : aucune écriture n'est créée pour une ligne sans
contrepartie ouverte. Imputer un débit sans facture reviendrait à créer une charge (impact P&L),
interdit sans validation explicite de Nicolas. Seules les lignes avec une `account.move.line`
déjà postée et ouverte en face ont été lettrées.

## Lignes lettrées (3), toutes exactes (écart 0,00, aucun write-off)

| BSL | Date | Montant | Fournisseur | Document(s) | Écart | Preuve |
|---|---|---|---|---|---|---|
| 20044 | 29/07 | −12 087,45 | Kirchner, Fischer + Co GmbH | RESA792 (RGK26-02871, 11 735,45) + RESA912 (RGK26-03856, 352,00) | 0,00 | libellé SEPA cite les 2 références explicitement |
| 20042 | 29/07 | −957,00 | Sinas Gmbh & Co | RESA1117 (ref 201944) | 0,00 | montant exact, une seule facture ouverte à ce montant sur 3 |
| 20027 | 29/07 | −7,26 | ING Belgique SA | RESA1218 (ref 2026/01/005568163) | 0,00 | le relevé cite littéralement "FACTURE n° 2026/01/005568163" |

## Ambiguës — à arbitrer (contrepartie identifiée mais pas exploitable en l'état)

- **BSL 19871 Radius Business Solutions −308,80** et **BSL 19985 Radius −459,81** — les factures
  citées dans le libellé (RESA1201 réf. BE261701699965, RESA1195 réf. BE261701759658) sont
  **déjà soldées**, mais via de VIEUX prélèvements de mars 2026 (261700569279, 261700631667,
  261700681966) dont le résiduel avait été réparti sur plusieurs factures via un mécanisme de
  pool. Conséquence : ces 2 nouveaux débits ING n'ont plus aucune facture ouverte en face —
  **aucune contrepartie ouverte**, donc rien à lettrer ici selon la règle dure. Ce constat révèle
  un système de rapprochement Radius potentiellement désynchronisé (vieux crédits bancaires
  consommés contre de mauvaises factures) qui mériterait un audit dédié, séparé du lettrage
  courant.
- **BSL 19809 Worldline SA/NV −529,78** — le libellé cite la référence "2260310704", qui
  correspond bien à RESA1059 (626,31 EUR ouverte), mais l'écart est de **96,53 EUR**, largement
  au-dessus de la tolérance de 5 EUR. Pas de lettrage partiel forcé sans confirmation — à
  arbitrer (vérifier si une note de crédit Worldline existe séparément, ou si la référence
  correspond en réalité à une autre facture).
- **BSL 19625 Kirchner, Fischer + Co GmbH −12 837,54** ("Siehe Avis vom 07.07.26") — aucune
  référence facture dans le libellé. Recherche exhaustive (subset-sum) sur les 47 factures
  Kirchner ouvertes (173 410,62 EUR au total) : des dizaines de combinaisons tombent pile au
  centime près — avec 47 candidats c'est statistiquement inévitable, donc **aucune preuve
  fiable**. Nécessite l'avis de débit Kirchner du 07/07 (déjà signalé le 29/07, toujours non
  résolu).
- **BSL 19811 ONSS −8 945,00** — le compte `454000 National Social Security Office (NSSO)`
  existe et est utilisé pour les cotisations/PP, mais **toutes** ses lignes non réconciliées ont
  un résiduel de 0,00 EUR actuellement (30 lignes, somme nette = 0). Aucun montant ouvert à
  matcher malgré l'existence du compte. Ce point s'inscrit dans l'historique de doublons
  ONSS/SD Worx déjà documenté (cf. mémoire projet honoraires/leviers) — nécessite un audit ONSS
  dédié, hors périmètre d'un lettrage bancaire.
- **BSL 19735 −1 574,53** — "Votre fichier de virements en euros (SEPA)", paiement groupé
  multi-bénéficiaires. Le libellé de synthèse ne permet pas d'identifier les bénéficiaires
  individuels — nécessite le détail du fichier SEPA (export banque ou SD Worx) pour éclater.

## Sans contrepartie ouverte — imputation à valider par Nicolas (rien créé)

Ces débits n'ont **aucune facture fournisseur encodée dans Odoo** en face (paiements carte ou
domiciliation sans passage par le circuit achats). Les imputer créerait une charge P&L —
interdit sans validation explicite. Compte suggéré = compte historiquement utilisé pour ce type
de dépense chez Teatower (vérifié sur des factures déjà payées du même fournisseur), à titre
indicatif uniquement :

| BSL | Date | Montant | Libellé | Compte suggéré (historique) |
|---|---|---|---|---|
| 19972 | 28/07 | −500,00 | Google Ads (carte) | 615200 Publicité |
| 19703 | 13/07 | −500,00 | Google Ads (carte) | 615200 Publicité |
| 19480 | 02/07 | −437,07 | Google Ads (carte) | 615200 Publicité |
| 19607 | 07/07 | −384,12 | Google Cloud EMEA (domiciliation) | 611129 Licences informatiques |
| 19788 | 16/07 | −526,99 | Shopify (carte) | 611129 Licences informatiques |
| 19728 | 14/07 | −60,49 | Adobe (carte) | 611129 Licences informatiques |
| 19638 | 09/07 | −36,29 | Adobe (carte) | 611129 Licences informatiques |
| 19639 | 09/07 | −722,47 | Intuit Ireland (Mailchimp, carte) | 616600 Frais de marketing |
| 19944 | 24/07 | −200,00 | Proximus (domiciliation) | 616200 Téléphone |
| 19780 | 15/07 | −24,45 | Sendcloud (domiciliation) | 611129 Licences informatiques |
| 19746 | 14/07 | −1 040,40 | Administration Générale des Douanes et Accises | pas de précédent net — à valider avec Nicolas (un seul historique trouvé, direct 440000 sans facture, 09/2025) |
| 19804 | 16/07 | −755,90 | "Paiement ING : MASTERCARD 188 …" — règlement de relevé carte, pas une facture isolée | aucun (nécessite le détail du relevé carte pour ventiler) |
| 19460 | 01/07 | −2,25 | ING — décompte de frais n° 331900946 (non retrouvé comme facture encodée, contrairement à d'autres décomptes ING déjà en RESA) | 650100 (précédent ING, à confirmer) — ou encoder d'abord la facture ING correspondante |
| 20049 | 29/07 | −396,00 | CHEQUE GUICHET — aucune information sur le bénéficiaire | aucun (info insuffisante) |
| 19853 | 20/07 | −342,77 | MIAMIO Faire (carte, achat marchandise probable) | 600000 Purchases of Raw Materials — **PAS 440000** (voir avertissement ci-dessous) |
| 19857 | 20/07 | −180,51 | NCA Europe Design Faire (carte) | 600000 Purchases of Raw Materials — **PAS 440000** |

**Avertissement Faire (règle dure #3)** : l'historique montre que les paiements carte MIAMIO et
NCA Europe (achats via la marketplace Faire) ont déjà été codés **à tort en 440000 Suppliers**
par le passé (ex. RESA visibles aux dates 08/05, 31/03, 23/02, 14/12, 02/12/2025 — toutes en
440000). Le compte correct, constaté sur tous les AUTRES achats Faire de la même période (Sass
Belle, Matcha Passion, YOKO DESIGN, Der kleine Fratz, Ogo living, Matcha CO) est **600000
Purchases of Raw Materials**. Ce script n'impute de toute façon aucune de ces deux lignes (pas
de facture ouverte en face), mais le point est signalé pour ne pas reproduire l'erreur lors
d'une imputation manuelle future.

### Avances salariales (4 lignes)

| BSL | Date | Montant | Bénéficiaire | Compte suggéré |
|---|---|---|---|---|
| 19610 | 07/07 | −500,00 | Vansimpsen Audrey | 455000 Rémuneration |
| 19739 | 14/07 | −500,00 | Vansimpsen Audrey | 455000 Rémuneration |
| 19738 | 14/07 | −1 000,00 | Cabosart Gilles | 455000 Rémuneration |
| 19737 | 14/07 | −750,00 | van Ooteghem Camille | 455000 Rémuneration |

Historiquement ces avances sont codées **directement** sur 455000 Rémuneration (compte de
tiers-personnel, pas P&L), chaque mouvement se soldant intégralement dans son propre mouvement
bancaire (aucune ligne 455000 "ouverte" en attente actuellement — résiduel 0,00 sur tout
l'historique de ces 3 employés). Il n'y a donc pas de contrepartie ouverte au sens strict de la
règle de lettrage (pas de match, juste un repointage direct comme le veut la pratique
historique). Rien n'a été créé ici — à confirmer par Nicolas s'il souhaite le même traitement
que d'habitude (repointage direct 499000→455000, zéro impact P&L).

## Rappel — cas déjà exclus explicitement (règle 5)

- **BSL 20026 MOMIDISTRI SA +688,87** — non lettré, probable double paiement sur une facture
  Spar Momignies déjà soldée le 20/07 (voir `lettrage_ing_20260731_review.md`).

## Encaissements clients — pas de nouveau match

Reprise des encaissements clients encore ouverts (19466 NANRETAIL, 19660 ITM Alimentaire, 19784
Smartbox, 19952 Dynamic Food, 20008 Delwol, 20052 Pluxee, 20050 Edenred, 19992 iPiD) : aucun
nouveau match n'est apparu par rapport au diagnostic du même jour (`lettrage_ing_20260731_review.md`).
Situation inchangée.

## Faux impayés POS (règle 4)

Aucune des lignes ING de ce tour ne touche les factures INV/2025/04135-04142 ni les paiements
PAY091-098 déjà identifiés comme faux impayés POS. Rien à signaler de nouveau sur ce point.
