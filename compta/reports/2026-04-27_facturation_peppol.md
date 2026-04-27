# Facturation 22 SO + envoi Peppol — 2026-04-27

## Décision Nicolas
GO complet : facturation `delivered` only, envoi Peppol prioritaire, fallback email si Peppol indispo.

## Étape 1 — Statut SO ambigues

Diagnostic via `stock.picking` + `stock.move` :

| SO | Picking | State | Date | Décision |
|---|---|---|---|---|
| S05478 (Delhaize Hotton) | TT/PICK/08812 | done | 2026-04-27 07:32:49 | **INCLURE** — picking + 9 moves done |
| S05476 (Carrefour M. Bievre) | TT/PICK/08810 | done | 2026-04-27 07:24:13 | **INCLURE** — picking + 1 move done |

→ **22 SO sur 22 facturables.**

## Étape 2 — Facturation (mode `delivered`, jamais `all`)

Wizard `sale.advance.payment.inv` → `create_invoices` → `account.move.action_post`.

**22/22 factures créées et postées** : numérotation INV/2026/02278 → INV/2026/02299.

Totaux :
- **HT facturé : 10 397,38 EUR**
- **TTC facturé : 11 028,32 EUR**
- Le delta vs scan initial (10 020 HT) vient de l'ajout des 2 SO ambigues + recalcul exact `qty_delivered` au moment du wizard.

## Étape 3 — Activation Peppol

Champs sociétaires Teatower (compagnie 1) :
- `peppol_can_send=True`, `account_peppol_proxy_state=receiver`, EAS=0208, EP=0656763145, contact=nicolas.raes@teatower.com → **OK pour émettre Peppol**.

**Algo d'activation par partner** (sur `partner_invoice_id` de chaque SO) :
1. Si BE et EAS/EP vide → renseigner `peppol_eas=0208` + `peppol_endpoint=<10 chiffres BCE>` (dérivé de `vat`).
2. Si `peppol_eas` + `peppol_endpoint` renseignés mais `invoice_edi_format` vide → set `invoice_edi_format='ubl_bis3'`.
3. Le wizard d'envoi Odoo détermine alors automatiquement `sending_methods=['peppol']`.

**15 partners activés cette session** :
| Partner ID | Nom | Changement |
|---|---|---|
| 2889 | Cocon Life store | invoice_edi_format=ubl_bis3 |
| 2892 | Coiffure By Sam | invoice_edi_format=ubl_bis3 |
| 2939 | Emilie Gigot - Green Coffee | invoice_edi_format=ubl_bis3 |
| 3042 | La Thé Box (FR) | invoice_edi_format=ubl_bis3 |
| 3043 | La Vieille Demeure | invoice_edi_format=ubl_bis3 |
| 3132 | Megan Houtvast | invoice_edi_format=ubl_bis3 |
| 3162 | Nouvel Air Coiffure | invoice_edi_format=ubl_bis3 |
| 3200 | Restaurant La Gloriette | invoice_edi_format=ubl_bis3 |
| 5459 | Newpharma Comptabilité | invoice_edi_format=ubl_bis3 |
| 5620 | Café Ventuno - Ventuno SA | invoice_edi_format=ubl_bis3 |
| 7440 | Cafermi | invoice_edi_format=ubl_bis3 |
| 7563 | CREAGORA | invoice_edi_format=ubl_bis3 |
| 59871 | SA Brasserie Delsart - Invoice | invoice_edi_format=ubl_bis3 |
| 123037 | GMP La Louvière - Invoice | invoice_edi_format=ubl_bis3 |
| 123207 | KVA Bar - Groupe DonGiovanni | invoice_edi_format=ubl_bis3 |

## Étape 4 — Envoi (`account.move.send.wizard.action_send_and_print`)

Stratégie : créer le wizard sans surcharger les méthodes — Odoo pré-coche `peppol` si `is_peppol_edi_format` est vrai et que verification!=not_valid, sinon `email`.

### Tableau final

| SO | Facture | Client (invoice partner) | HT | TTC | Méthode | Peppol state | UUID |
|---|---|---|---:|---:|---|---|---|
| S05473 | INV/2026/02279 | Delhaize Le Lion S.A | 2013,60 | 2134,58 | peppol | processing | 675b6e29… |
| S05463 | INV/2026/02280 | Café Ventuno, Ventuno SA | 937,50 | 993,75 | peppol | processing | 6497becc… |
| S05472 | INV/2026/02281 | Cafermi | 755,42 | 800,81 | peppol | processing | d60f4bdb… |
| S05459 | INV/2026/02282 | Carrefour Corporate Village | 720,46 | 763,70 | email | — | — |
| S05471 | INV/2026/02283 | KVA Bar - Groupe DonGiovanni | 540,00 | 572,40 | peppol | processing | 1304f46b… |
| S05474 | INV/2026/02284 | CREAGORA | 500,00 | 530,00 | peppol | processing | e669d805… |
| S05404 | INV/2026/02286 | GMP La Louvière (Invoice) | 480,16 | 515,66 | peppol | processing | 16122d25… |
| S05470 | INV/2026/02285 | Nouvel Air Coiffure | 483,18 | 512,20 | email | ready | — |
| S05480 | INV/2026/02287 | SA Brasserie Delsart (Invoice) | 465,00 | 492,90 | peppol | processing | b7b7ca14… |
| S05457 | INV/2026/02288 | Carrefour Corporate Village | 402,18 | 426,31 | email | — | — |
| S05467 | INV/2026/02289 | Carrefour Corporate Village | 400,21 | 424,25 | email | — | — |
| S05481 | INV/2026/02290 | Cocon Life store | 347,52 | 368,38 | peppol | processing | 6b1a77d2… |
| S05468 | INV/2026/02292 | Carrefour Corporate Village | 328,85 | 348,61 | email | — | — |
| S05478 | INV/2026/02291 | Delhaize Le Lion S.A | 321,96 | 341,28 | peppol | processing | 9b62155b… |
| S05486 | INV/2026/02294 | Megan Houtvast | 305,13 | 323,47 | email | — | — |
| S05402 | INV/2026/02293 | La Thé Box (FR) | 305,13 | 323,47 | email | — | — |
| S05412 | INV/2026/02297 | Newpharma Comptabilité | 242,55 | 257,10 | peppol | processing | 07f1dfca… |
| S05475 | INV/2026/02295 | Coiffure By Sam | 229,81 | 243,60 | peppol | processing | 7cca71ab… |
| S05483 | INV/2026/02296 | Emilie Gigot - Green Coffee | 227,92 | 241,60 | peppol | processing | e19b768e… |
| S05484 | INV/2026/02298 | Restaurant La Gloriette | 213,71 | 226,52 | peppol | processing | fe7b9796… |
| S05485 | INV/2026/02299 | La Vieille Demeure | 155,30 | 164,63 | peppol | processing | eefd96e0… |
| S05476 | INV/2026/02278 | Carrefour Corporate Village | 21,79 | 23,10 | email | — | — |

### Synthèse

- **Factures créées + postées** : 22/22
- **Total HT** : 10 397,38 EUR · **Total TTC** : 11 028,32 EUR
- **Envoyées Peppol** (`peppol_is_sent=True`, state=processing) : 14
- **Peppol queued / ready** (sera flushed par cron Odoo) : 1 (Nouvel Air Coiffure)
- **Total flux Peppol** : **15**
- **Fallback email** : 7
- **Partners Peppol activés** (champ `invoice_edi_format=ubl_bis3` set) : **15**

### Détail des 7 fallback email

| Partner | Raison |
|---|---|
| 6596 Carrefour Corporate Village | VAT et endpoint vides — partner pivot Carrefour Hyper, pas d'identifiant Peppol |
| 6596 idem (S05459, S05457, S05467, S05468, S05476) | toutes les factures Carrefour Hyper passent par 6596 |
| 3042 La Thé Box | FR, peppol_verification_state=not_valid |
| 3132 Megan Houtvast | peppol_verification_state=not_valid (BCE pas dans annuaire Peppol) |

### Erreurs / cas à traiter manuellement

Aucune erreur fatale. Points d'attention :

1. **Carrefour Corporate Village (6596)** : 6 factures envoyées par email. Le numéro BCE Carrefour Belgium SA pourrait être renseigné manuellement (BE0448.826.918) pour basculer en Peppol. Action recommandée : confirmer avec compta Carrefour leur identifiant Peppol officiel avant de l'activer.
2. **Nouvel Air Coiffure (3162)** : `peppol_move_state=ready` mais pas encore `is_sent` — le cron Odoo va le flusher (généralement < 1h). À surveiller.
3. **La Thé Box (3042) + Megan Houtvast (3132)** : `not_valid` côté annuaire Peppol — fallback email permanent jusqu'à enregistrement de leur côté.

## Logs techniques

- Diag complet : `compta/scripts/_diag_out.json`
- Log rollout : `compta/scripts/_rollout_log.json`
- Recap factures : `compta/scripts/_recap.json`
- Scripts : `compta/scripts/01_diag…py`, `02_inspect…py`, `03_inspect_send_full.py`, `04_invoice_and_peppol.py`, `04b_test_one.py`, `05_rollout.py`, `06_recap.py`
