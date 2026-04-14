# Lettrages en attente de révision — 2026-04-14

Journal ING BE30 3631 6408 2311 — 154 lignes non rapprochées restantes après traitement automatique

---

## Cas 1 — Vilna Gaon S.R.L. (3 paiements sortants sans facture correspondante)

Ces 3 virements sortants ont Vilna Gaon S.R.L. comme partenaire mais aucune facture fournisseur ouverte ne correspond.

| BSL id | Date | Montant | Référence |
|--------|------|---------|-----------|
| 16572 | 2026-02-12 | -5 250,00 EUR | ING app Vers: Vilna Gaon S.R.L - BE22068896796147 |
| 17049 | 2026-03-05 | -2 250,60 EUR | ING app Vers: Vilna Gaon S.R.L - BE22068896796147 |
| 17247 | 2026-03-14 | -2 000,00 EUR | ING app Vers: Vilna Gaon S.R.L - BE22068896796147 |

**Total : -9 500,60 EUR**
Action requise : vérifier factures fournisseur Vilna Gaon (RESA ou INV). Si non créées, créer les factures fournisseur correspondantes.

---

## Cas 2 — Factures mensuelles Shyfter (47,19 EUR) — correspondance ambiguë

| BSL id | Date | Montant | Libellé |
|--------|------|---------|---------|
| 17156 | 2026-03-11 | -47,19 EUR | INVOICE 2026030551 |
| 17822 | 2026-04-10 | -47,19 EUR | INVOICE 2026040554 |

Candidats possibles : RESA661 (Shyfter SA, 47,19 EUR, 10/03/2026), RESA700 (Amazon EU 47,19 EUR, 28/02/2026), RESA812 (Shyfter SA, 47,19 EUR, 10/04/2026)

Action : BSL 17156 → probablement RESA661 (Shyfter, même date), BSL 17822 → probablement RESA812 (Shyfter, même date). Confirmer avec Nicolas et imputer manuellement.

---

## Cas 3 — Frais ING 0,61 EUR — correspondance ambiguë entre 2 mois

| BSL id | Date | Montant | Libellé |
|--------|------|---------|---------|
| 17129 | 2026-03-10 | -0,61 EUR | ING (charges/frais/kosten) |
| 17816 | 2026-04-10 | -0,61 EUR | ING (charges/frais/kosten) |

Candidats : RESA659 (ING Belgique SA, 0,61 EUR, 09/03/2026), RESA687 (ING Belgique SA, 0,61 EUR, 08/02/2026)

Action : BSL 17129 → RESA659 (même mois mars), BSL 17816 → facturation avril (pas encore créée ou RESA posterior). Confirmer.

---

## Cas 4 — Frais ING 31,00 EUR — correspondance ambiguë entre 2 mois

| BSL id | Date | Montant |
|--------|------|---------|
| 17631 | 2026-04-01 | -31,00 EUR |

RESA670 (déjà lettrée dans ce run) et RESA787 (ING Belgique SA, 31,00 EUR, 31/03/2026)

Action : BSL 17631 → vérifier si RESA787 existe et est ouverte, imputer dessus.

---

## Cas 5 — Paiements sans facture ouverte (partner connu mais pas de ML correspondant)

| BSL id | Date | Montant | Partenaire | Commentaire |
|--------|------|---------|------------|-------------|
| 17350 | 2026-03-19 | +254,40 EUR | Au Fond de l'eau, Jeremy Gesquiere | Encaissement client — facture introuvable |
| 17045 | 2026-03-05 | -500,00 EUR | AURELIE HUET (Gysen Aurelie) | Avance salaire ? Voir HR |
| 16838 | 2026-02-24 | -221,50 EUR | Audrey Vansimpsen | Pas de facture fournisseur ni payable ouvert |
| 17195 | 2026-03-12 | -92,60 EUR | Audrey Vansimpsen | Idem |
| 16481 | 2026-02-09 | -96,47 EUR | Service Public Fédéral Finances | Impôt ? Créer écriture OD |
| 16154 | 2026-01-22 | +96,47 EUR | Alain ALBERT (HORS-PROVISIONS) | Remboursement Odoo/Provisions ? |
| 16443 | 2026-02-06 | +449,43 EUR | AL RETAIL - Delhaize BOONDAEL | Facture payée — créer ML de rapprochement |
| 16421 | 2026-02-05 | +209,24 EUR | Delhaize Braives | Idem — facture ouverte introuvable |
| 16265 | 2026-01-28 | +36,00 EUR | Banque Nationale Belgique SA (SIPS ASBL) | Encaissement ponctuel |
| 16117 | 2026-01-20 | -21,19 EUR | Carlier Jérôme | Remboursement frais ? Créer note de débit |
| 16091 | 2026-01-20 | -119,00 EUR | Carlier Jérôme | Idem |
| 15870 | 2026-01-09 | +31,08 EUR | Amazon Advertising | Remboursement Amazon Ads |
| 15662 | 2025-12-31 | +559,77 EUR | AL RETAIL - Delhaize BOONDAEL | Facture non trouvée |
| 15586 | 2025-12-29 | +513,54 EUR | Amazon Advertising | Encaissement Amazon |
| 15585 | 2025-12-29 | +210,00 EUR | Banque Nationale Belgique SA | Ponctuel |
| 15468 | 2025-12-22 | -2 935,02 EUR | SPF Finances / Cabinet Cecile Neven | TVA / impôt à identifier |
| 15063 | 2025-12-05 | +243,76 EUR | IN BW S.C.R.L. | Client — facture manquante |
| 14373 | 2025-11-05 | -700,00 EUR | SPF Finances | TVA / impôt |
| 13505 | 2025-09-17 | +543,06 EUR | Banque Nationale Belgique SA (DEPA) | Encaissement ponctuel |

---

## Lignes sans partenaire (132 lignes)

132 lignes n'ont pas de partenaire identifié dans Odoo (principalement paiements CB, virements divers, salaires, charges fixes). Ces lignes nécessitent soit :
- Un rapprochement manuel avec une écriture OD
- La création d'une facture fournisseur correspondante
- Une imputation directe sur compte de charges/produits

Action recommandée : traiter via l'interface Odoo Comptabilité > Rapprocher pour les lignes récurrentes (salaires, loyer, ING frais).
