# Lettrage ING (BNK1) — 04/08/2026 — lignes NON lettrées

Rapport complet des 58 lignes ING non réconciliées à date. **9 lignes lettrées** (voir
`compta/lettrage_15_ing_20260804.py`), **49 restent non lettrées**, listées ci-dessous avec la
raison précise et ce qu'il faudrait pour débloquer.

## Résumé lettrage effectué (9 lignes, 3.404,90 EUR au total)

| BSL | Date | Montant | Partenaire | Document(s) | Écart | Traitement |
|---|---|---|---|---|---|---|
| 20062 | 30/07 | +199,00 | Virelles Nature | INV/2026/02150 | 0,00 | exact |
| 20077 | 30/07 | +256,41 | Virelles Nature | INV/2025/02201 | 0,00 | exact |
| 20066 | 30/07 | +366,11 | Hello Bio sprl (Pure Bastogne) | INV/2026/03314 | 0,00 | exact |
| 20078 | 30/07 | +684,26 | Chili Peppers - Intermarché Tilff | INV/2026/03435 | -0,01 | write-off 657100 |
| 20090 | 30/07 | +697,20 | SA LD Management - Intermarché Hamoir | INV/2026/02836 | -0,01 | write-off 657100 |
| 20102 | 31/07 | +344,45 | FQMS - Proxy Delhaize Quadrilatère Huy | INV/2026/03625 | 0,00 | exact |
| 20070 | 30/07 | +675,02 | Centrale Intermarché | INV/2026/03297 | +0,02 | write-off 757100 |
| 20080 | 31/07 | -7,26 | ING Belgique SA | RESA1222 (posté depuis draft) | 0,00 | exact |
| 20103 | 01/08 | -35,45 | ING Belgique SA | RESA1223 (posté depuis draft) | 0,00 | exact |

Note technique : RESA1222/RESA1223 étaient des factures fournisseur ING **en brouillon**
(auto-générées par la digitalisation des relevés de compte cartes, structure cohérente : frais
650100 + TVA déductible 411000 + contrepartie 440000, référence facture ING citée en clair dans
le libellé bancaire, montant exactement pile). Postées puis lettrées.

---

## 49 lignes NON lettrées

### A. Ambiguïté — plusieurs candidats à montant identique (aucune preuve fiable)

- **BSL 20089 SMARTBOX GROUP LIMITED (+40,40, 31/07)** — Smartbox Group (id 3240) a **4 factures
  ouvertes à exactement 40,40 EUR** (INV/2026/01053, INV/2026/00631, INV/2026/00440,
  INV/2026/00164). Le libellé bancaire (réf PDN-/PCI-, codes internes Smartbox) ne permet pas
  de discriminer. Lettrer au hasard = risque d'erreur. **Débloquer** : demander à Smartbox le
  détail de règlement (liste des factures couvertes par ce virement) ou accepter un lettrage FIFO
  assumé (à valider explicitement par Nicolas, ce n'est pas une preuve).
- **BSL 19784 SMARTBOX GROUP LIMITED (+67,00, 15/07)** — aucune facture ni combinaison (jusqu'à
  6 factures) de Smartbox Group ne somme à 67,00 EUR exactement. Même limite que ci-dessus.

### B. Aucune facture ouverte en face (partenaire identifié mais rien à lettrer)

- **BSL 19952 DYNAMIC FOOD SRL - Spar LLN (+436,84, 24/07)** — partner identifié (id 113216),
  **0 facture ouverte**. Soit déjà réglée par ailleurs, soit facture jamais émise.
- **BSL 20026 MOMIDISTRI SA (+688,87, 28/07)** — déjà documenté le 31/07 (voir
  `lettrage_ing_20260731_review.md`) : la communication structurée ***000/0040/27924*** réutilise
  la référence d'une facture **déjà soldée** le 20/07 (INV/2026/03056, Spar Momignies, 688,89).
  Spar Momignies n'a aucune autre facture ouverte. Probable **double paiement client** — situation
  inchangée depuis 5 jours, à arbitrer avec le client (rembourser ou affecter à une commande future).
- **BSL 20065 TOURNESOLS NAMUR SA (+144,84, 30/07)** — le libellé cite explicitement
  "INV/2026/01903 - 233.20 double pmt FAC/2024/07/0007". INV/2026/01903 est **déjà payée**
  (payment_state=paid depuis le 03/04/2026, montant 378,04). Le client n'a **aucune** facture
  ouverte actuellement. Le mot "double pmt" dans leur propre libellé suggère qu'ils savent qu'il
  s'agit d'un paiement en double/erroné de leur côté. **Débloquer** : contacter Tournesols Namur
  pour clarifier (remboursement ou affectation à une prochaine commande).

### C. Partenaire GMS identifié mais montant ne matche aucune facture ni combinaison

- **BSL 19466 NANRETAIL SA - Intermarché Naninne (+675,58, 01/07)** — le titulaire du compte
  (NANRETAIL SA) est le holding derrière Intermarché Naninne. Aucune facture ouverte sur
  NANRETAIL SA (id 2812) ni sur ses 2 contacts liés (Intermarché Naninne id 5506/5755 : 2 factures
  ouvertes 175,70 + 487,50 = 663,20, ne somme pas à 675,58). **Débloquer** : vérifier si
  NANRETAIL règle pour une autre enseigne du groupe (Carrefour Market Naninne, tagué NO-MERCH,
  id 9079) ou demander le détail du virement.
- **BSL 19660 ITM ALIMENTAIRE BELGIUM SA (+637,24, 09/07)** — compte de paiement centralisé du
  groupement Intermarché. "Centrale Intermarché" (id 124363) a 7 factures ouvertes
  (198,10 / 48,10 / 123,10 / 48,10 / 675,00 déjà lettrée / 235,60 / 714,00) : aucune combinaison
  ne somme à 637,24. **Débloquer** : demander le détail des factures couvertes par ce virement
  (ITM Alimentaire paie souvent pour plusieurs magasins en un virement groupé).
- **BSL 20063 VENTE PRIVEE.COM (+2.426,43, 30/07)** — gros client déballage/déstockage (Veepee).
  Aucune facture ouverte trouvée ni sur "VENTE-PRIVEE.COM" (id 123449), ni sur
  "VENTE-PRIVEE.COM - BEAUNE" (id 123480), ni sur "Veepee Northern Europe" (id 121975, dont l'unique
  ligne facture a un residual de 0,00 et un nom vide — anomalie à creuser séparément). Communication
  du virement : "/ADV/2000011982". **Débloquer** : vérifier s'il existe une facture Veepee non
  encore encodée dans Odoo pour cette référence ADV, ou si le partner correct est un autre
  contact du groupe Veepee non trouvé par recherche texte.

### D. Frais/prélèvements récurrents sans facture fournisseur encodée (déjà documentés, situation inchangée)

Ces cas ont été identifiés lors des passes précédentes (29/07, 31/07) : imputer directement
créerait une charge sans facture, **interdit sans validation explicite Nicolas** (règle dure).
Rien créé, comptes suggérés à titre indicatif si validation :

- **Frais carte ING** : 19460 (-2,25), 20104 (-2,25) — cotisation mensuelle carte crédit.
- **Google Ads** : 19480 (-437,07), 19703 (-500,00), 19972 (-500,00), 20110 (-194,46).
- **Google Cloud** : 19607 (-384,12).
- **Google Play** : 20079 (-21,98) — nouveau ce tour, même famille (compte suggéré 615200/616600).
- **Adobe** : 19638 (-36,29), 19728 (-60,49).
- **Intuit** : 19639 (-722,47).
- **Shopify** : 19788 (-526,99).
- **Sendcloud** : 19780 (-24,45) — un compte Sendcloud (id 113237) a une facture ouverte mais à
  133,80 EUR, pas 24,45 : pas de match, pas de lettrage.
- **Mastercard ING (règlement carte)** : 19804 (-755,90) — remboursement de dépenses carte déjà
  débitées séparément, pas une facture.
- **MIAMIO / NCA Europe (achats Faire par carte)** : 19853 (-342,77), 19857 (-180,51). ATTENTION
  historique : ne PAS coder en 440000 si imputé un jour (erreur passée constatée), le bon compte
  observé sur les autres achats Faire est 600000.
- **Facebook Payments (Meta Ads)** : 20123 (-50,00) — nouveau ce tour.
- **Bancontact Braderie Waterloo** : 20111 (-50,00) — dépense carte ponctuelle, nature à confirmer
  avec Nicolas (perso vs pro).

### E. Fournisseurs identifiés, aucune facture ouverte ou écart trop important

- **Kirchner, Fischer + Co GmbH — BSL 19625 (-12.837,54, 08/07)** : aucune référence facture dans
  le libellé ("Siehe Avis vom 07.07.26"). 47 factures Kirchner ouvertes ; le subset-sum trouve des
  dizaines de combinaisons exactes au centime — statistiquement inévitable avec autant de
  candidats, donc **aucune preuve fiable**. Nécessite l'avis Kirchner du 07/07 (signalé depuis le
  29/07, toujours pas obtenu).
- **Worldline SA/NV — BSL 19809 (-529,78, 16/07)** : réf "2260310704" = RESA1059 (626,31 ouverte),
  écart 96,53 EUR > tolérance 5 EUR — pas de lettrage forcé.
- **Radius Business Solutions — BSL 19871 (-308,80) et 19985 (-459,81)** : les factures
  référencées dans le libellé (RESA1201, RESA1195) sont déjà soldées via de vieux prélèvements de
  mars 2026 répartis en pool. Plus de contrepartie ouverte — audit Radius dédié nécessaire.
- **ONSS — BSL 19811 (-8.945,00, 16/07)** : compte 454000 existe mais toutes ses lignes ont un
  résiduel de 0,00 — rien à matcher. Audit ONSS/SD Worx dédié requis (doublons déjà identifiés
  par ailleurs).
- **Douanes et Accises — BSL 19746 (-1.040,40)**, **Proximus — BSL 19944 (-200,00)** : aucune
  facture fournisseur ouverte encodée.
- **CHEQUE GUICHET — BSL 20049 (-396,00, 29/07)** : aucune information sur le bénéficiaire, montant
  retiré au guichet en espèces/chèque, non identifiable depuis le relevé seul.
- **Fichiers de virements groupés SEPA — BSL 19735 (-1.574,53, 14/07) et 20087 (-117,60, 31/07)** :
  libellé de synthèse uniquement (référence fichier), bénéficiaire(s) non identifiable(s) sans le
  détail du fichier de virement (à demander à la banque ou retrouver dans l'historique ING app).

### F. Avances salariales (mécanisme historique auto-soldé, pas de contrepartie ouverte)

- Vansimpsen Audrey : 19610 (-500,00), 19739 (-500,00)
- van Ooteghem Camille : 19737 (-750,00)
- Cabosart Gilles : 19738 (-1.000,00)

Historiquement codées directement en 455000 Rémunérations sans ligne ouverte préalable à matcher
(chaque avance est auto-soldée dans son propre mouvement). Pas de "contrepartie ouverte" au sens
strict — compte suggéré 455000 si Nicolas valide le même traitement que d'habitude.

### G. Titres-repas / assurance / non-clients (encaissements hors flux commercial)

- **Pluxee** (titres-repas) : 19652 (+124,95), 19771 (+33,28), 20052 (+6,85).
- **Edenred** (titres-repas) : 19826 (+17,59), 20050 (+19,66).
- **Baloise Belgium** (assurance, adaptation salaire accident travail) : 19630 (+79,51).
- **iPiD Europe** (micro-dépôt de vérification bancaire, 0,01 EUR) : 19992.
- **DELWOL** (0,02 EUR) : même phénomène qu'iPiD — la communication structurée coïncide par
  hasard avec une facture déjà payée (INV/2026/03523, AD Delhaize Roodebeek, 539,30 EUR),
  montant totalement incompatible : micro-dépôt de vérification, pas une vraie correspondance.

Aucun de ces flux ne relève de la facturation clients/fournisseurs Odoo — hors périmètre lettrage.

---

## Synthèse

- **58 → 49** lignes non réconciliées sur ING (BNK1) après ce tour.
- **9 lignes lettrées aujourd'hui** = 3.404,90 EUR (7 encaissements clients + 2 factures ING
  Belgique), écarts cumulés 0,04 EUR passés en write-off 657100/757100 (2 négatifs 0,01 chacun +
  1 positif 0,02).
- Les 49 lignes restantes se répartissent en : 2 ambiguës (Smartbox, doublons de montant),
  3 sans contrepartie ouverte malgré partenaire identifié (Dynamic Food, Momidistri, Tournesols —
  ces 2 derniers = doubles paiements probables côté client), 3 GMS gros comptes centralisés sans
  combinaison exacte (Nanretail, ITM Alimentaire, Vente Privée), le reste = frais carte/SEPA
  récurrents sans facture encodée (Google/Adobe/Intuit/Shopify/Sendcloud/Meta), avances
  salariales, titres-repas, micro-dépôts de vérification, et 3 dossiers fournisseurs déjà connus
  nécessitant un avis externe (Kirchner, Radius, ONSS).
- Rien n'a été imputé sur un compte de charge/produit sans facture ouverte en face — conforme à
  la règle dure (pas d'écriture P&L sans validation explicite).
