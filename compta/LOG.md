# LOG Compta Teatower

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
