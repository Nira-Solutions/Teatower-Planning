# Commission Jérôme Carlier — Mars 2026

**Produit le** : 29/04/2026 — **Révisé le** : 04/05/2026 v2 (source officielle Adri : docx + image PNG paliers)
**Période** : 01/03/2026 → 31/03/2026
**Source** : Avenant contrat 17/03/2026 + docx Adri 04/05/2026 + image PNG paliers officiels
**Fichier d'entrée** : `Commission mars 2026.docx` (Adri)

> **v2 du 04/05/2026 — correction majeure** : les calculs précédents (v1) utilisaient une formule linéaire fictive `50 × (croissance% − 10)` qui n'existe pas dans l'avenant. La vraie table de paliers Adri a été fournie le 04/05/2026 (image PNG officielle). Ce rapport v2 applique la table correcte. Total corrigé : **1.475 € brut** (vs 575 € précédemment).

---

## 1. Commission sur la croissance du chiffre d'affaires B2B

### Périmètre retenu

**Option C** : SO confirmées (state = sale ou done), tags Canal GMS/B2B/Horeca (88/27/85/28/32/84/26/31/33) + héritage partenaire parent. Tout inclus (Va.S.Co, Institutions). Source : rapport data-bi `2026-04-30_CA_B2B_mars_reconciliation.md`.

### Résultats

| Période | CA HTVA B2B | Source |
|---|---:|---|
| Mars 2025 (baseline avenant) | **72.700,00 €** | Figé dans l'avenant 17/03/2026 |
| Mars 2026 (réalisé — Option C) | **81.663,16 €** | Odoo XML-RPC SO mars 2026, 208 SO B2B |
| **Croissance** | **+12,3 % HT** | (81.663 − 72.700) / 72.700 |

### Table des paliers officielle (source Adri — image PNG 04/05/2026)

| Croissance | Commission brute |
|---|---:|
| > 100 % | Proratisation sans plafond |
| 80 – 100 % | 6.000 € |
| 65 – 79,9 % | 4.500 € |
| 50 – 64,9 % | 3.200 € |
| 40 – 49,9 % | 2.200 € |
| 31 – 39,9 % | 1.500 € |
| 30 – 30,9 % | 1.000 € |
| 25 – 29,9 % | 850 € |
| 20 – 24,9 % | 650 € |
| 15 – 19,9 % | 400 € |
| **10 – 14,9 %** | **250 €** |
| < 10 % | 0 € |

**Application : croissance +12,3 % → tranche 10-14,9 % → 250 € brut**

---

## 2. Commission sur les displays GMS (100 €/display)

**Règle** : 100 € par display GMS installé en mars 2026. Pas de seuil SO ≥ 240 €. Source : liste Adri docx mars 2026.

### Liste officielle Adri — 9 magasins

| # | Magasin GMS | Commission |
|---|---|---:|
| 1 | Delhaize Recogne | 100 € |
| 2 | Intermarché Hannut | 100 € |
| 3 | Carrefour Belgium — Corporate Village | 100 € |
| 4 | Carrefour Market Haine Saint Pierre | 100 € |
| 5 | Hyper Carrefour Bomerée | 100 € |
| 6 | Hyper Carrefour Gosselies | 100 € |
| 7 | Hyper Carrefour Ans | 100 € |
| 8 | Carrefour Market Wellin | 100 € |
| 9 | Intermarché Hamoir | 100 € |
| **Total** | **9 displays** | **900 €** |

> Note : la v1 de ce rapport avait erronément appliqué un filtre "SO ≥ 240 € enregistrée dans Odoo" qui réduisait le décompte à 2 displays. Ce filtre n'existe pas dans les règles Adri. Le déclencheur est l'installation du display, pas une commande Odoo. Les 9 magasins de la liste Adri sont tous éligibles.

---

## 3. Commission sur les nouveaux clients hors GMS (65 €/client)

**Règle** : 65 € par nouveau client Horeca/Revendeur, 1ère commande ≥ 240 € HTVA. Source : liste Adri docx mars 2026.

### Liste Adri — sous-total 5 clients × 65 € = 325 €

| # | Client | Statut |
|---|---|---|
| 1 | Chez Jack (HORECA JACQUEMIN SRL) | Retenu par Adri |
| 2 | L'Amandier — Libramont | Retenu par Adri |
| 3 | VDM Pâtisserie | Retenu par Adri |
| 4 | Urban Therapy Paris | Retenu par Adri |
| 5 | Boucherie de Magerotte | Retenu par Adri (rattrapage février) |
| — | Le Goût-Thé du Moulin | Probablement exclu par Adri (client historique depuis 10/2025 dans l'ancien système — voir note) |

**Total : 5 × 65 € = 325 €**

> Note : le docx Adri liste 6 lignes cochées en Horeca/Revendeurs mais le sous-total explicite est 5 × 65 € = 325 €. La 6ème ligne la plus probable à être exclue est "Le Goût-Thé du Moulin" (Le Comptoir du Moulin #105458), classé client historique dans l'ancien rapport v1 (référencé dans Odoo depuis octobre 2025). Adri ayant tranché à 5, le chiffre 325 € est adopté tel quel sans remise en question.

---

## 4. Total commission mars 2026

| Volet | Détail | Montant brut |
|---|---|---:|
| Croissance CA B2B (+12,3 % — tranche 10-14,9 %) | Palier officiel Adri | **250 €** |
| Displays GMS | 9 × 100 € (liste Adri) | **900 €** |
| Nouveaux clients hors GMS | 5 × 65 € (sous-total Adri) | **325 €** |
| **TOTAL mars 2026** | | **1.475 € brut** |

---

## 5. Régularisation

| Mouvement | Montant |
|---|---:|
| Payslip mars 2026 versé | 460 € |
| Commission corrigée mars 2026 (source Adri v2) | 1.475 € |
| **Régularisation à payer** | **+1.015 €** |

**Action requise : verser 1.015 € à Jérôme Carlier sur payslip avril ou mai 2026** en ligne "Régularisation commission mars 2026".

---

*Rapport v2 généré le 04/05/2026 — agent Compta Teatower*
*Source officielle : Commission mars 2026.docx (Adri) + image PNG paliers officiels*
*v1 du 29/04-04/05/2026 obsolète — formule linéaire fictive remplacée par table de tranches Adri*
