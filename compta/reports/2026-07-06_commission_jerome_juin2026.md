# Commission Jérôme Carlier — Juin 2026

> Produit le 06/07/2026. Base : document Adri `Commission_juin_2026 JEROME.docx` (volets clients) + calcul Odoo Option C (volet croissance CA).
> **À valider par Nicolas avant envoi à Jérôme.**

## Volet 1 — Croissance CA B2B

Méthode **Option C** (figée Nicolas 04/05/2026) : SO confirmées (`state ∈ sale/done`), tags Canal GMS/B2B/Horeca (88/27/85/28/32/84/26/31/33) + héritage partenaire parent, base HT (`amount_untaxed`).

| | Juin 2025 (baseline N-1) | Juin 2026 | Croissance |
|---|---:|---:|---:|
| CA B2B HT — brut Option C | 137.109,18 € | 92.389,82 € | −32,62 % |
| **CA B2B HT — baseline corrigée** | **63.845,20 €** | **92.389,82 €** | **+44,88 %** |
| SO retenues | 154 (hors Tea Touch) / 155 | 207 | — |

**Arbitrage Nicolas (06/07/2026) — exclusion Tea Touch.** La baseline juin 2025 brute était gonflée par une seule SO — `S01458 Tea Touch, 73.263,98 € HT` (53 % du mois) — client **en faillite novembre 2025**, vente jamais réglée, passée en perte sur créance. Comptée telle quelle, la croissance ressort à −32,6 % (palier <10 % → 0 €), ce qui pénaliserait Jérôme pour un CA fantôme. Décision : **retirer Tea Touch de la baseline** → croissance réelle **+44,88 %**.

**Vérification symétrique (06/07/2026).** Contrôle des pics des deux mois pour s'assurer que la croissance n'est pas gonflée par un outlier côté 2026 : juin 2026 est parfaitement plat — la plus grosse SO (Torrefactory S05866, 2.450 €) ne pèse que **2,65 %** du mois, aucune commande one-shot / grossiste / institution exceptionnelle. Côté 2025, seul Tea Touch était atypique (53,4 %). La croissance +44,88 % est donc **organique** : 63.845 € / 154 SO → 92.390 € / 207 SO (+34 % de commandes). Chiffre confirmé par Nicolas.

→ Tranche **40 – 49,9 %** de la table officielle → **commission croissance = 2.200 €**

## Volet 2 — Displays GMS (100 €/installation) — liste Adri

| Magasin | Commission |
|---|---:|
| Proxy Delhaize Ma Campagne | 100 € |
| Proxy Delhaize Roi Chevalier | 100 € |
| Spar Momignies | 100 € |
| Spar Clavier | 100 € |
| Delhaize Tubize | 100 € |
| Delhaize Montigny-le-Tilleul | 100 € |
| Carrefour Market Courcelles | 100 € |
| Carrefour Market Tilff | 100 € |
| Intermarché Ciney | 100 € |
| Delhaize Visé | 100 € |
| Delhaize Amay | 100 € |
| Proxy Delhaize Tihange | 100 € |
| Delhaize Flémalle | 100 € |
| Carrefour Market Tomberg (Woluwe) | 100 € |
| Hyper Carrefour Kraainem | 100 € |
| **Sous-total — 15 GMS** | **1.500 €** |

## Volet 3 — Nouveaux clients hors GMS (65 €/client Horeca-Revendeur, 130 €/grossiste, 1ère SO ≥ 240 € HT) — liste Adri

| Client | Catégorie | Commission |
|---|---|---:|
| Cuisines DOVY – Marche-en-Famenne | Horeca | 65 € |
| La Fleur et le Soleil | Horeca | 65 € |
| Centrale Intermarché | Grossiste | **130 €** (1ère SO S05778 du 10/06/2026 = 673,58 € HT ≥ 240 €) |
| **Sous-total — 2 Horeca + 1 grossiste** | | **260 €** |

> Note tag Odoo : le partner #124363 « Centrale Intermarché » est tagué **GMS** dans Odoo, pas « Grossiste » (id 32). Classé grossiste par Adri (130 € = 2 × Horeca) → on adopte Adri (accès terrain). Mistag Odoo à corriger éventuellement.

## Récapitulatif total — Juin 2026

| Volet | Montant brut |
|---|---:|
| 1. Croissance CA B2B (+44,88 %, Tea Touch exclu) | **2.200 €** |
| 2. Displays GMS (15 × 100 €) | **1.500 €** |
| 3. Nouveaux clients hors GMS (2 × 65 € + 1 grossiste × 130 €) | **260 €** |
| **TOTAL COMMISSION BRUTE — JUIN 2026** | **3.960 €** |

---

*Volets 2 et 3 = liste Adri (règle : en cas de divergence Adri/Odoo, on adopte le chiffre Adri, accès terrain). Volet 1 calculé via Odoo XML-RPC méthode Option C, avec exclusion de la créance Tea Touch en faillite (arbitrage Nicolas 06/07/2026). Centrale Intermarché confirmée éligible (1ère SO 673,58 € HT).*
