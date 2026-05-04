# Commission Jérôme Carlier — Mars 2026

**Produit le** : 29/04/2026 — **Révisé le** : 04/05/2026 (décision Nicolas : Option C + paliers linéaires 10-30 %)
**Période** : 01/03/2026 → 31/03/2026
**Source** : Avenant contrat 17/03/2026 + Odoo XML-RPC + rapport data-bi `2026-04-30_CA_B2B_mars_reconciliation.md`
**Fichier d'entrée** : `Commission mars 2026.xlsx`

---

## 1. Commission sur la croissance du chiffre d'affaires B2B

### Méthode officielle fixée le 04/05/2026 (décision Nicolas)

**Option C — périmètre complet** : SO confirmées (state = sale ou done), tags Canal GMS/B2B/Horeca (88/27/85/28/32/84/26/31/33) + héritage partenaire parent. Tout inclus (Va.S.Co, Institutions). Source : rapport data-bi `2026-04-30_CA_B2B_mars_reconciliation.md`.

### Résultats

| Période | CA HTVA B2B (GMS + B2B Revendeurs + Horeca) | Source |
|---|---:|---|
| Mars 2025 (baseline avenant) | **72.700,00 €** | Figé dans l'avenant 17/03/2026 |
| Mars 2026 (réalisé — Option C) | **81.663,16 €** | Odoo XML-RPC SO mars 2026, 208 SO B2B |
| **Croissance** | **+12,3 % HT** | (81.663 − 72.700) / 72.700 |

### Application des paliers — formule linéaire 10 %→30 % (décision Nicolas 04/05/2026)

| Seuil | Commission |
|---|---:|
| < 10 % | 0 € |
| Entre 10 % et 30 % | `50 × (croissance% − 10)` |
| > 30 % | ≥ 1.000 € |

**Application : `50 × (12,3 − 10) = 50 × 2,3 = 115 € brut`**

| Croissance | Commission (exemples) |
|---|---:|
| < 10 % | 0 € |
| **12,3 %** | **115 €** |
| 18,7 % | 435 € |
| 30 % | 1.000 € |
| > 30 % | ≥ 1.000 € |

→ **Commission croissance mars 2026 : 115 € brut**

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

| Volet | Détail | Montant brut |
|---|---|---:|
| Commission croissance CA B2B (+12,3 % — Option C) | `50 × (12,3 − 10)` | **115 €** |
| Commission displays GMS | 2 × 100 € (Intermarché Hannut + Hamoir) | **200 €** |
| Commission nouveaux clients hors GMS | 4 × 65 € | **260 €** |
| **TOTAL RÉVISÉ** | | **575 € brut** |

> Revision du 04/05/2026 : passage de 460 € a 575 € suite a la decision Nicolas d'appliquer les paliers linéaires 10-30 % et la méthode Option C (CA B2B mars 2026 = 81.663 € HT, croissance +12,3 %, commission croissance = 115 €).
> Le payslip mars 2026 a été réglé sur 460 €. **Régularisation due : 115 €** (voir section 6).

---

## 5. Points à valider avec Nicolas avant envoi à Jérôme

1. **CA B2B mars 2026 = 76.140 €** : chiffre du rapport data-bi du 27/04 (perimetre 3 canaux + 20 overrides). Confirmer si c'est bien la définition employeur "B2B" du contrat. *(L'instance Odoo actuelle ne contient aucune facture mars 2025 — l'historique avant 04/2025 est sur l'ancien Tea Tree SA Odoo V14. C'est pourquoi on s'appuie sur le baseline contrat 72.700 €.)*

2. **Boucherie de Magerotte (S05073)** : on rattrape sur mars ou on régularise le payslip de février ?

3. **6 GMS sans 1ʳᵉ commande** (Recogne, Haine St Pierre, Bomerée, Gosselies, Wellin, + Ans absent) : confirmé qu'ils ne déclenchent pas la commission tant qu'aucune SO ≥ 240 € n'arrive ? Ils basculeront automatiquement le mois de leur 1ʳᵉ commande.

4. **Hyper Carrefour Ans** : aucun partenaire correspondant trouvé dans Odoo. Display installé mais partenaire pas créé ? À investiguer.

5. **Urban Therapy PARIS** vs `urbantherapy.be` : si une entité PARIS séparée existe, la créer dans Odoo et reconsidérer l'éligibilité (probable revendeur grossiste éventuellement à 2 clients = 130 € si SO > 500 €).

6. **Carrefour Corporate Village** était dans la liste — c'est un client historique. Si Jérôme a installé un nouveau display dans un nouveau magasin Carrefour de ce groupe, le considérer comme display GMS additionnel ? À clarifier.

---

---

## 6. Régularisations à faire

| Mouvement | Montant | Destinataire | Motif |
|---|---:|---|---|
| Payslip mars 2026 versé | 460 € | Jérôme Carlier | Payé sur base +4,7 % (méthode ancienne) |
| Commission révisée mars 2026 | 575 € | Jérôme Carlier | Méthode Option C + paliers 10-30 % |
| **Régularisation à verser** | **115 €** | Jérôme Carlier | Solde mars 2026 sur prochain payslip (mai 2026) |

> A intégrer dans le payslip d'avril 2026 ou mai 2026 en ligne "Régularisation commission mars 2026 — 115 €".

---

*Rapport généré automatiquement — agent Compta/Data Teatower | Source : Odoo XML-RPC + avenant contrat 17/03/2026*
*Révisé le 04/05/2026 — décision Nicolas : méthode Option C (périmètre complet SO) + paliers linéaires 10-30 %*
