# Commission Jérôme Carlier — Mars 2026

**Produit le** : 29/04/2026
**Période** : 01/03/2026 → 31/03/2026
**Source** : Avenant contrat 17/03/2026 + Odoo XML-RPC + rapport data-bi `2026-04-27_CA_avril_par_canal.md`
**Fichier d'entrée** : `Commission mars 2026.xlsx`

---

## 1. Commission sur la croissance du chiffre d'affaires B2B

### Résultats

| Période | CA HTVA B2B (GMS + B2B Revendeurs + Horeca) |
|---|---:|
| Mars 2025 (baseline avenant) | **72.700,00 €** |
| Mars 2026 (réalisé) | **76.140,00 €** |
| **Croissance** | **+4,7 %** |

> Source mars 2026 : rapport data-bi du 27/04/2026 (perimetre tags Canal GMS+B2B+Horeca + 20 overrides manuels). Note : "mars 2026 inclut une commande exceptionnelle non récurrente" — sans elle, le run rate est plus faible.

### Application du barème (avenant §1.3)

| Croissance vs N-1 | Commission |
|---|---:|
| > 30 % | ≥ 1.000 € |
| **< 10 %** | **0 €** |

→ **Commission croissance : 0 € brut**

---

## 2. Commission sur les displays GMS (100 €/display, 1ʳᵉ commande ≥ 240 € HTVA)

### Détail des 9 GMS listés

| # | Client | Partner Odoo | Créé | 1ʳᵉ SO mars 2026 | Statut |
|---|---|---|---|---:|---|
| 1 | Delhaize Recogne | #122091 | 13/03/26 | — aucune | ✗ pas de 1ʳᵉ commande |
| 2 | Intermarché Hannut (INTERMADIS) | #121874 | 06/03/26 | **S05122 — 681,57 €** | ✓ ELIGIBLE |
| 3 | Carrefour Belgium - Corporate Village | #6596 | 07/04/25 | — | ✗ client historique (94 SO depuis 04/2025) |
| 4 | Carrefour Market Haine Saint Pierre | #122412 | 24/03/26 | — aucune | ✗ pas de 1ʳᵉ commande |
| 5 | Hyper Carrefour Bomerée | #122467 | 26/03/26 | — aucune | ✗ pas de 1ʳᵉ commande |
| 6 | Hyper Carrefour Gosselies | #122466 | 26/03/26 | — aucune | ✗ pas de 1ʳᵉ commande |
| 7 | Hyper Carrefour Ans | introuvable Odoo | — | — | ✗ partenaire absent |
| 8 | Carrefour Market Wellin | #122589 | 30/03/26 | — aucune | ✗ pas de 1ʳᵉ commande |
| 9 | Intermarché Hamoir | #122255 | 18/03/26 | **S05230 — 681,57 €** | ✓ ELIGIBLE |

### Total displays éligibles : **2 × 100 € = 200 € brut**

> ⚠ 6 partenaires GMS ont été créés en mars (display installé) mais n'ont **pas encore passé de 1ʳᵉ commande** au 29/04. Ils ne déclenchent pas la commission ce mois-ci ; ils basculeront dans la commission du mois où la 1ʳᵉ commande ≥ 240 € sera enregistrée.

---

## 3. Commission sur les nouveaux clients hors GMS (65 €/client, 1ʳᵉ commande ≥ 240 € HTVA)

### Détail des 8 clients listés

| # | Client | Partner Odoo | 1ʳᵉ SO mars 2026 | Montant | Statut |
|---|---|---|---|---:|---|
| 1 | Chez Jack (HORECA JACQUEMIN SRL) | #122410 | S05263 — 24/03 | 275,00 € | ✓ ELIGIBLE |
| 2 | L'Amandier - Libramont (Hotel) | #122192 | S05213 — 16/03 | 240,00 € | ✓ ELIGIBLE (limite exacte) |
| 3 | VDM Pâtisserie | #121728 | S05089 — 02/03 | 632,58 € | ✓ ELIGIBLE |
| 4 | Le Loft du Renard | #121779 | S05100 — 04/03 | **50,00 €** | ✗ < 240 € |
| 5 | Le Goût-Thé du Moulin | (Le Comptoir du Moulin #105458) | — historique 10/2025 | — | ✗ client historique |
| 6 | La Villa Lorraine | #121215 | S05000 — 06/03 | **52,83 €** | ✗ < 240 € + commande annulée |
| 7 | Urban Therapy - PARIS | #3273 | — historique 10/2025 | — | ✗ client historique (urbantherapy.be) |
| 8 | Teroir de Magerotte (Boucherie de Magerotte) | #121553 | S05073 — 26/02 / facturé 06/03 | 356,64 € | ✓ ELIGIBLE (rattrapage février selon note Excel) |

### Total clients éligibles : **4 × 65 € = 260 € brut**

> ⚠ **Urban Therapy – PARIS** : le partenaire Odoo trouvé est `urbantherapy.be` (Bruxelles, client depuis 02/2025). Si une entité PARIS distincte a été créée séparément, à confirmer — sinon c'est un client historique non éligible.
> ⚠ **Boucherie/Teroir de Magerotte** : compté ici en rattrapage du mois de février (note Excel d'origine : *"Pas comptabilisé en février car inférieur à 240 € selon Adri mais erreur à voir => S05073"*). Le SO S05073 = 356,64 € HTVA (>240 €) → l'éligibilité est avérée. À valider par Nicolas si on rattrape sur mars ou si on régularise février.

---

## 4. Total commission mars 2026

| Volet | Montant brut |
|---|---:|
| Commission croissance CA B2B (+4,7 %) | **0 €** |
| Commission displays GMS (2 × 100 €) | **200 €** |
| Commission nouveaux clients hors GMS (4 × 65 €) | **260 €** |
| **TOTAL** | **460 € brut** |

---

## 5. Points à valider avec Nicolas avant envoi à Jérôme

1. **CA B2B mars 2026 = 76.140 €** : chiffre du rapport data-bi du 27/04 (perimetre 3 canaux + 20 overrides). Confirmer si c'est bien la définition employeur "B2B" du contrat. *(L'instance Odoo actuelle ne contient aucune facture mars 2025 — l'historique avant 04/2025 est sur l'ancien Tea Tree SA Odoo V14. C'est pourquoi on s'appuie sur le baseline contrat 72.700 €.)*

2. **Boucherie de Magerotte (S05073)** : on rattrape sur mars ou on régularise le payslip de février ?

3. **6 GMS sans 1ʳᵉ commande** (Recogne, Haine St Pierre, Bomerée, Gosselies, Wellin, + Ans absent) : confirmé qu'ils ne déclenchent pas la commission tant qu'aucune SO ≥ 240 € n'arrive ? Ils basculeront automatiquement le mois de leur 1ʳᵉ commande.

4. **Hyper Carrefour Ans** : aucun partenaire correspondant trouvé dans Odoo. Display installé mais partenaire pas créé ? À investiguer.

5. **Urban Therapy PARIS** vs `urbantherapy.be` : si une entité PARIS séparée existe, la créer dans Odoo et reconsidérer l'éligibilité (probable revendeur grossiste éventuellement à 2 clients = 130 € si SO > 500 €).

6. **Carrefour Corporate Village** était dans la liste — c'est un client historique. Si Jérôme a installé un nouveau display dans un nouveau magasin Carrefour de ce groupe, le considérer comme display GMS additionnel ? À clarifier.

---

*Rapport généré automatiquement — agent Compta/Data Teatower | Source : Odoo XML-RPC + avenant contrat 17/03/2026*
