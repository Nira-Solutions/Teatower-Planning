# LOG Compta Teatower

## 2026-06-09 — Facturation B2B Peppol — 24 factures brouillon créées

- Type : création factures clients (out_invoice) mode delivered — BROUILLON uniquement, aucune postée, aucun envoi
- Périmètre : 37 SO invoice_status=to_invoice scannées, hors Tea Touch (6973), hors Shopify/Amazon/POS
- Vérification Peppol par client : champ peppol_verification_state + commercial_partner_id
- Lignes TRANSPORT forcées qty_delivered=qty_ordered (8 lignes) : S05755/S05753/S05748/S05744/S05740/S05724/S05722/S05721
- Factures créées en brouillon (24) :
  - inv_id=39842 S05761 KVA Bar 0720819470 HT=472,50 TVA=28,35 TTC=500,85
  - inv_id=39843 S05758 Christine Poncin 0717880766 HT=29,04 TVA=1,76 TTC=30,80
  - inv_id=39844 S05759 Christine Poncin 0717880766 HT=72,60 TVA=4,40 TTC=77,00
  - inv_id=39845 S05757 Carrefour Belgium 0448826918 HT=523,02 TVA=31,38 TTC=554,40
  - inv_id=39846 S05756 Cafes Delahaut 0418920135 HT=712,50 TVA=42,75 TTC=755,25
  - inv_id=39847 S05755 Alcodis SA 0438048535 HT=70,00 TVA=4,20 TTC=74,20
  - inv_id=39848 S05723 Wallonie Entreprendre 0793630244 HT=739,61 TVA=44,39 TTC=784,00
  - inv_id=39849 S05754 Delhaize Le Lion 0402206045 HT=305,14 TVA=18,34 TTC=323,48
  - inv_id=39850 S05753 Brasserie Miroir 0688912806 HT=60,00 TVA=3,60 TTC=63,60
  - inv_id=39851 S05749 DB Kfé SRL 0508863582 HT=472,50 TVA=28,35 TTC=500,85
  - inv_id=39852 S05748 Carrefour Belgium 0448826918 HT=184,36 TVA=11,08 TTC=195,44
  - inv_id=39853 S05746 D-trois SRL 0895931194 HT=305,08 TVA=18,32 TTC=323,40
  - inv_id=39854 S05744 Delhaize (Ferrières) 0402206045 HT=202,16 TVA=12,14 TTC=214,30
  - inv_id=39855 S05743 Sodexo Belgium 0407246778 HT=750,00 TVA=45,00 TTC=795,00
  - inv_id=39856 S05742 Pharmacie Badot 0651311250 HT=271,57 TVA=20,67 TTC=292,24
  - inv_id=39857 S05740 Amessia Boutique 1026857935 HT=85,28 TVA=5,12 TTC=90,40
  - inv_id=39858 S05739 Cocon Life store 0657633274 HT=479,54 TVA=28,78 TTC=508,32
  - inv_id=39859 S05738 Carrefour Market Bastogne 0442412248 HT=274,71 TVA=16,49 TTC=291,20
  - inv_id=39860 S05737 Antheco Intermarché 0828785123 HT=301,12 TVA=18,08 TTC=319,20
  - inv_id=39861 S05724 Autobus Latour 0401403519 HT=169,82 TVA=10,18 TTC=180,00
  - inv_id=39862 S05733 Carrefour Market Remouchamps 0446634817 HT=510,45 TVA=30,62 TTC=541,07
  - inv_id=39863 S05731 Lillodis SRL 0567568873 HT=174,36 TVA=10,48 TTC=184,84
  - inv_id=39864 S05728 Gerpidis SA 0802039451 HT=174,37 TVA=10,48 TTC=184,85
  - inv_id=39865 S05721 Moore Services Financiers 0748770516 HT=200,53 TVA=12,07 TTC=212,60
- TOTAL : HT=7.540,26 EUR | TVA=457,03 EUR | TTC=7.997,29 EUR
- Exclues Peppol non vérifié (8 SO) : S05767/S05730/S05729/S05741/S05722/S05621/S05763/S05727
- Exclues hors périmètre B2B (5 SO) : S05765/S05764/S05726/#48534/#48143 (Amazon/Shopify)
- Confirmé : 0 facture postée, 0 envoi Peppol effectué

## 2026-06-09 — POST OD ventilation 700000 — deux OD postees sur GO explicite Nicolas

- Type : action_post sur deux OD de reclassement canal (brouillons -> posted)
- OD 39813 | MISC/24-25/06/0034 | date 30/06/2025 | 186 554,03 EUR | posted OK
  - Debit 700000 : 186 554,03 | Credits : 700600 GMS 61 805,17 + 700300 Horeca 76 763,73 + 700500 Revendeurs 44 175,77 + 700700 Institutions 3 809,36
- OD 39826 | MISC/25-26/06/0086 | date 09/06/2026 | 821 416,36 EUR | posted OK
  - Debit 700000 : 821 416,36 | Credits : 700600 GMS 305 389,00 + 700300 Horeca 294 159,76 + 700500 Revendeurs 203 890,70 + 700700 Institutions 17 976,90
- Controles pre-post : state=draft, equilibre verifie (ecart 0,00), Tea Touch (6973) absent des deux OD
- Soldes apres post (credit - debit, comptes produits) :
  - 700000 FY24-25 : 83 609,90 EUR (residu Tea Touch + sans partenaire)
  - 700000 FY25-26 : -14 216,99 EUR (flux POS techniques a investiguer — hors perimetre OD)
  - 700600 GMS FY24-25 : 61 805,17 EUR | FY25-26 : 305 389,00 EUR
  - 700300 Horeca FY24-25 : 298 867,08 EUR | FY25-26 : 294 159,76 EUR
  - 700500 Revendeurs FY24-25 : 177 882,05 EUR | FY25-26 : 203 890,70 EUR
  - 700700 Institutions FY24-25 : 3 809,36 EUR | FY25-26 : 17 976,90 EUR

## 2026-06-09 — Ventilation CA B2B 700000 FY24-25 — OD brouillon creee

- Type : creation comptes + OD reclassement (brouillon, non postee)
- Comptes crees :
  - 700600 Ventes GMS (Grande Distribution) — ID Odoo 1220
  - 700700 Ventes Institutions / Corporate — ID Odoo 1221
  - Config : account_type=income, group 700-707, tag_id=1 (identique 700300/700500)
- OD creee : ID Odoo 39813 — journal MISC (ID 11) — date 30/06/2025 — etat DRAFT
  - Ref : Ventilation CA B2B 700000 par canal FY24-25
  - Debit 700000 (ID 320) : 186 554,03 EUR
  - Credit 700600 GMS : 61 805,17 EUR (46 clients GMS + AD Spa)
  - Credit 700300 Horeca : 76 763,73 EUR (NIJSKENS inclus, Vignee Management inclus)
  - Credit 700500 Revendeurs : 44 175,77 EUR (Revendeurs + DTC + dormants + petits non-id)
  - Credit 700700 Institutions : 3 809,36 EUR
  - Total debit = total credit = 186 554,03 EUR — equilibre verifie
- Exclus de l'OD (restent sur 700000) :
  - Tea Touch (ID 6973) : 73 263,98 EUR
  - Lignes sans partenaire : 10 345,92 EUR
  - Total residuel 700000 apres post eventuel : 83 609,90 EUR
- A FAIRE : Nicolas doit poster l'OD explicitement (action_post sur ID 39813)

## 2026-06-09 — Ventilation CA B2B 700000 FY25-26 (YTD) — OD brouillon creee

- Type : OD reclassement canal (brouillon, non postee)
- OD creee : ID Odoo 39826 — journal MISC (ID 11) — date 09/06/2026 — etat DRAFT
  - Ref : Ventilation CA B2B 700000 par canal FY25-26 (YTD)
  - Perimetre : factures out_invoice+out_refund 01/07/2025-09/06/2026 sur 700000
  - Solde total 700000 (factures clients) : 821 416,36 EUR
  - Debit 700000 (ID 320) : 804 364,85 EUR (ventilable certain)
  - Credit 700600 GMS (ID 1220) : 305 389,00 EUR — 93 partenaires
  - Credit 700300 Horeca (ID 915) : 294 159,76 EUR — 243 partenaires
  - Credit 700500 Revendeurs (ID 917) : 186 839,19 EUR — 202 partenaires
  - Credit 700700 Institutions (ID 1221) : 17 976,90 EUR — 80 partenaires
  - Total debit = total credit = 804 364,85 EUR — equilibre verifie
- Exclus de l'OD (restent sur 700000 en attente arbitrage) :
  - Tea Touch (ID 6973) : 0,00 EUR (faillite nov 2025 — aucun CA FY25-26 confirme)
  - Lignes sans partenaire : 0,00 EUR
  - A_ARBITRER (classification incertaine) : 17 051,51 EUR (350 clients, majoritairement personnes physiques sans tag)
- A FAIRE : Nicolas doit poster l'OD explicitement (action_post sur ID 39826)

## 2026-06-09 — OD 39826 FY25-26 — Finalisation ventilation 100% CA B2B

- Type : modification OD brouillon existante (non postee)
- OD modifiee : ID Odoo 39826 — etat DRAFT inchange
- Decision Nicolas/Nira : 17 051,51 EUR A_ARBITRER (350 micro-clients sans tag canal) affectes integralement au canal Revendeur
- Modifications appliquees en une transaction ORM (account.move write, commandes (1, id, vals)) :
  - Ligne 179408 debit 700000 : 804 364,85 -> 821 416,36 EUR
  - Ligne 179411 credit 700500 Revendeurs : 186 839,19 -> 203 890,70 EUR
- Lignes inchangees :
  - Ligne 179409 credit 700600 GMS : 305 389,00 EUR
  - Ligne 179410 credit 700300 Horeca : 294 159,76 EUR
  - Ligne 179412 credit 700700 Institutions : 17 976,90 EUR
- Controle equilibre : debit 821 416,36 = credit (305 389,00 + 294 159,76 + 203 890,70 + 17 976,90) = 821 416,36 EUR | ecart = 0,00 EUR
- Couverture : 100% du CA B2B facture FY25-26 ventile (vs 97,9% avant)
- Tea Touch (0 EUR) et flux POS (OD-RECLASSIF 700006) : absents de l'OD, confirme

## 2026-05-29 — Batch facturation B2B Peppol delta J+1 — 5 factures postées

- Type : facturation B2B hors GMS — wizard `delivered` + envoi Peppol (bucket A) / postée sans envoi (bucket B)
- SO scannées `to invoice` non-GMS : 14 total
- SO exclues GMS (tag GMS sur partner) : S05652 AD Delhaize Roodebeek, S05668 Intermarché Braine, S05643 Intermarché Rumes, S05644 Intermarché Mons
- SO exclues non livrées (qty_delivered=0 sur toutes lignes) : S05643, S05644
- SO exclues B2C (fiscal position EU B2C) : S05621 Jarosz, #48143 Jessica Masula
- SO exclues montant 0€ (100% remise, draft supprimés) : S05600 Café Ventuno, S05454 Marketing Teatower
- Hélène BERTRAND S05192 : déjà facturée le 28/05 (INV/2026/01652). Draft supprimé (ligne MENU 0€ résiduelle).
- B-Shock S05529 : déjà facturé le 28/05 (INV/2026/02728, 264,48 HT). Seule ligne résiduelle = filtres à thé 7,44 HT non encore facturés.

### Transport forcé qty_delivered=qty_ordered
- S05670 line 60308 TRANSPORT : 0→1 (10,00 EUR HT)
- S05666 line 60267 TRANSPORT : 0→1 (10,00 EUR HT)
- S00738 line 4648 TRANSPORT : 0→1 (10,00 EUR HT)

### Bucket A — Peppol OK (peppol_verification_state=valid) — 3 factures
| Facture | Partner | HT | TTC | Peppol state |
|---|---|---|---|---|
| INV/2026/02791 | MaxMara scrl (Max et moi) | 158,12 | 167,60 | processing |
| INV/2026/02794 | B-Shock Coaching - Cravette Cédric | 7,44 | 9,00 | processing |
| INV/2026/02795 | A2MG SRL | 198,12 | 210,00 | processing |
| **Total A** | | **363,68** | **386,60** | |

### Bucket B — Peppol KO (not_verified) — 2 factures — à statuer par Nicolas
| Facture | Partner | HT | TTC | Raison |
|---|---|---|---|---|
| INV/2026/02792 | Douaire Café srl | 160,00 | 169,60 | peppol not_verified |
| INV/2026/02793 | INFRABEL (Invoice Address) | 134,50 | 142,60 | peppol not_verified |
| **Total B** | | **294,50** | **312,20** | |

### Total batch 29/05
- Grand total : HT 658,18 EUR / TTC 698,80 EUR
- Anomalies : S05670 Douaire Café — 1 produit partiellement livré (HC250735 Pêche de vigne, 1 unité non livrée) ; facture partielle émise, solde à facturer à la prochaine livraison.

---

## 2026-05-19 — Facturation masse B2B — 67 SO — INV/2026/02542 à INV/2026/02605

- Type : facturation masse B2B — wizard `delivered` + envoi Peppol/email
- Périmètre : 67 SO (61 clean + 6 partielles avec livraison utile)
- Etape 1 — Transport forcé : 13 SO, 13 lignes TRANSPORT qty_delivered=product_uom_qty OK
- Etape 2 — Wizard facturation (4 batches x 20/20/18/7) : 64 factures draft créées, 0 erreur
  - IDs Odoo : 38243–38306
  - Total TTC : 38 819,04 EUR — Total TVA : 2 042,75 EUR
- Etape 3 — Post en lot (7 batches x 10) : 64/64 postées, 0 erreur
  - Références : INV/2026/02542 à INV/2026/02605
- Etape 4 — Envoi :
  - Peppol (54 factures) : envoi via account.move.send.wizard, mode peppol, UBL BIS 3.0
  - Email fallback (10 factures) : Le Fournil, L'Artiste, PAMPA, Cocoricoop, VENTE-PRIVEE.COM, Carrefour Belgium, La Thé Box, O'Brunch, La Pause Chocolat, Nouvel Air Coiffure
  - Erreurs envoi : 0
- SO exclues (non touchées) : S00738, S04347, S05192, S05454, S05529, S05484, S05582, S05585 (COFFRET partiel livré dans passe delivered), S05587, S05588

## 2026-05-19 — Audit SO B2B en attente de facturation

- Type : audit lecture seule — aucune écriture créée
- Périmètre : 75 SO `to_invoice` filtrées → 60 SO B2B (hors GMS 14, hors Shopify 1)
- Total HT estimé à facturer : 42 564,30 €
- SO urgentes (> 15j) : 10 dont S00738 (370j) et S04347 (183j) — anomalies historiques
- Transport à forcer qty_delivered : 13 SO
- Rapport transmis à Nicolas (texte agent, 2026-05-19)

## 2026-05-18 — Rapport commission Jérôme Carlier — Avril 2026 (v2 officiel)

- Type : rapport commission — vérification Odoo + adoption chiffres Adri
- Source : `Commission_avril_2026 (1).docx` (Adri) + Odoo XML-RPC (18/05/2026)
- Fichiers produits :
  - `compta/reports/2026-05-18_commission_jerome_avril2026.md`
  - `Teatower-Planning/commission/avril-2026/index.html` (v2 — remplace brouillon obsolète 04/05)
- Commit + push : 109974f (Teatower-Planning master)
- Résultat : 2 420 € brut (Version A — grossiste 130 € Adri) ou 2 290 € (Version B — grossiste 65 € mémoire stricte)
- Validation requise : règle grossiste 130 € à confirmer par Nicolas avant envoi Jérôme
- CA B2B Odoo avril 2026 : 67 672,19 € HT / CA Adri : 73 805 € / Croissance Adri : +16,2 % → 400 €

## 2026-04-30 — Batch facturation run 6 — 17 factures draft (SO S05487–S05513)

### Correction lignes transport (nouvelle règle : transport = service, toujours facturer si marchandise partie)
- S05497 Alcodis SA : line_id=56472 qty_delivered 0→1 (TRANSPORT 10,00 EUR HT)
- S05504 Al Picchio Rosso : line_id=56550 qty_delivered 0→1 (TRANSPORT 10,00 EUR HT)
- S05505 Le Coin 62 : line_id=56556 qty_delivered 0→1 (TRANSPORT 10,00 EUR HT)
- Delta total correction transport : +30,00 EUR HT / +36,30 EUR TTC

### SO exclus du batch (qty_delivered=0 sur toutes les lignes)
- S05509 BLONFOOD SA Intermarché Liège Blonden : 0 livré
- S05510 Gemblouxim Intermarché Gembloux : 0 livré

### Factures draft créées (IDs 37146–37162) — mode delivered — wizard sale.advance.payment.inv
- 17 factures draft | Total HT : 6 147,54 EUR | Total TTC : 6 538,80 EUR
- Regroupements par partner : S05489+S05490 (Delhaize affilié), S05494+S05495+S05499 (Smartbox), S05507+partenaire facturation

### Posting + envoi Peppol/Email (2026-04-30) — GO Nicolas
- 17/17 factures postées (action_post) — INV/2026/02329 à INV/2026/02345
- Partners modifiés (invoice_sending_method peppol activé) : Al Picchio Rosso (2783), Srl D'Ici Wépion (3248), Newpharma Compta (5459), Alivim SRL (123294)
- Envoi Peppol (11 factures) : INV/02329, 02330, 02331, 02332, 02333, 02334, 02336, 02338, 02340, 02342, 02344, 02345 — état=processing
- Fallback email (5 factures, peppol non valide) :
  - INV/02335 Musée de la fraise (peppol not_valid)
  - INV/02337 Smartbox Group (partenaire IE, peppol not_valid)
  - INV/02339 Alcodis SA (peppol not_verified)
  - INV/02341 DelEmbourg SRL (peppol not_verified)
  - INV/02343 CPSP Belgie NV (peppol not_verified)
- Aucune erreur d'envoi — 0 facture bloquée

---

## 2026-04-29 — Lettrage SEPA Kirchner Fischer (SL 17572 + SL 18090)

### (B) Lettrage SEPA Kirchner Fischer — 2 domiciliations

**SL 17572 — 30/03/2026 — -20 606,47 EUR — CAS B PARTIEL**
- Diagnostic : RESA562 avait 3 501,93 EUR deja lettres via BNK1/25-26/4199 (SL 17341, 18/03/2026, partial.reconcile id=11475). Residuel reel = 6 046,70 EUR, pas 9 548,63 EUR.
- Action : move BNK1/25-26/4385 (id=35216) remis en draft, compte suspense 499000 remplace par :
  - 440000 debit 6 046,70 EUR (RESA562 partiel) -> reconcile avec line 122154 -> RESA562 paid
  - 440000 debit 11 057,84 EUR (RESA564) -> reconcile avec line 122914 -> RESA564 paid
  - 499000 debit 3 501,93 EUR -> SUSPENSE residuel (ces 3501.93 correspondent a un paiement anterieurement applique sur RESA562 via une autre SL, a pointer dans la meme SL bancaire par Nicolas)
- Ecritures creees : move lines 163592, 163593, 163594 dans BNK1/25-26/4385

**SL 18090 — 22/04/2026 — -18 451,00 EUR — CAS C**
- Diagnostic : RESA734 (RGK26-00690) residuel facture = 6 105,30 EUR vs communication Kirchner = 5 944,74 EUR -> ecart +160,56 EUR. Aucun avoir ou partial reconcile existant. Origine non identifiee.
- Action : move BNK1/25-26/4798 (id=36792) remis en draft, compte suspense 499000 remplace par :
  - 440000 debit 11 969,66 EUR (RESA506) -> reconcile avec line 125260 -> RESA506 paid
  - 440000 debit 536,60 EUR (RESA735) -> reconcile avec line 125262 -> RESA735 paid
  - 499000 debit 5 944,74 EUR -> SUSPENSE RESA734 (ecart 160,56 a clarifier avec Kirchner)
- Ecritures creees : move lines 163595, 163596, 163597 dans BNK1/25-26/4798

**Residuels a traiter manuellement par Nicolas :**
1. SL 17572 : 3 501,93 EUR en suspense (499000) = paiement deja applique sur RESA562 via SL 17341 -> verifier si la SL 17341 est bien une domiciliation separee ou double-comptabilisation
2. SL 18090 : 5 944,74 EUR en suspense (499000) = RESA734 (6 105,30) non lettree -> ecart 160,56 EUR a clarifier avec Kirchner (avoir ? majoration ? note de debit ?)

**Factures lettrées ce batch :** RESA562 + RESA564 + RESA506 + RESA735 = 29 610,80 EUR TTC
**PAY00569 cancelled** (cree par erreur en debut de session, annule avant tout impact)

---

## 2026-04-29 — Lettrage 7 quick wins + diagnostic SEPA Kirchner

### (A) Lettrage 7 factures clients
- Méthode : account.payment.register wizard + write payment_ids sur statement line
- PAY00562 INV/2026/01848 1262.98 EUR Ramaut — SL 18118 du 23/04
- PAY00563 INV/2026/01549 1113.00 EUR Sorescol S.A. — SL 17908 du 14/04
- PAY00564 INV/2026/01675 651.90 EUR Sorescol S.A. — SL 18055 du 21/04
- PAY00565 INV/2026/02152 539.00 EUR Lambertdis SRL — SL 18158 du 27/04
- PAY00566 INV/2026/02141 477.00 EUR Le 7 by Juliette — SL 18164 du 27/04
- PAY00567 INV/2026/01511 333.22 EUR Wonka / Intermarche Heusy — SL 18165 du 27/04
- PAY00568 INV/2026/01590 277.00 EUR Sandrinette / Delonville — SL 18161 du 27/04
- Total lettre : 4 653.10 EUR TTC — 7 factures en state=in_payment

### (A) Skip 3 QW — raisons
- QW06 (Mardis 462.02 / Carrefour 462.02) : IBAN BE66... appartient a Mardis partner 3120, facture sur Carrefour corporate 6596 et Mardis a une facture a 462.03 (ecart 0.01 EUR) — mis en review
- QW07 (Cafes Delahaut 397.50) : pas d'IBAN dans la ligne bancaire, critere C3 non verifiable
- QW08 (Pure Bastogne 389.56) : idem, pas d'IBAN dans la ligne bancaire

### (C) Correction partner_id — 0 ligne modifiee
- 83 lignes sans partner_id examinées : 75 noms bancaires abrégés sans match exact Odoo, 8 sans partner_name

## 2026-04-22 — Batch facturation run 5 — 51 factures (INV/02178–02228)

- Type : creation + posting via wizard sale.advance.payment.inv mode=delivered
- SO eligibles : 59 (qty_delivered > qty_invoiced sur au moins une ligne)
- Ecarte : 2 Hyper Carrefour (S05457, S05459 — livraison semaine 04/05) + 3 qty_delivered=0 (S05404, S05412, S04443)
- Wizard : 54 factures draft crees (regroupement par partenaire Odoo)
- Postees : 51 factures — INV/2026/02178 a INV/2026/02228
- Non postees (TTC=0) : 3 — S05441 Cafes Delahaut, S05400 Laetitia Mariette, S05427 Sefora Jacobs
- Total HT : 8 720,02 EUR | TVA : 523,41 EUR | TTC : 9 243,43 EUR
- Rapport : compta/reports/2026-04-22.md

## 2026-04-21 — Complement batch facturation S05435 + S05436 (2 factures — run 4)

- Type : creation + posting + envoi Peppol (2 SO, 2 factures Odoo)
- Source : S05435 et S05436 signalees par Nicolas — pickings TT/PICK/08690 et 08691, type=internal, state=done (meme pattern runs 2-3)
- Methode : creation manuelle account.move ligne par ligne, action_post, account.move.send.wizard (ubl_bis3)
- Facture S05435 : id=36556, INV/2026/02169 — Floridis SA - Intermarche Floriffoux (id=2958) — 410,19 EUR HT / 436,31 EUR TTC — echeance 2026-05-21 — Peppol processing (peppol_verification_state=valid)
- Facture S05436 : id=36557, INV/2026/02170 — Affilie 043366 - AD Fosses-la-Ville (id=5441) — 408,22 EUR HT / 434,22 EUR TTC — echeance 2026-06-20 (60j) — Peppol processing (peppol_verification_state=not_verified, a surveiller)
- TRANSPORT ajoute sur les 2 factures (10 EUR HT, compte 700000, TVA 21%)
- Total run 4 : 818,41 EUR HT / 870,53 EUR TTC
- Total cumule jour : 10 136,10 EUR HT / 10 771,02 EUR TTC (28 factures, runs 1+2+3+4)
- Rapport : compta/reports/invoicing_batch_2026-04-21.md (section "Complement S05435 + S05436 — run 4")

## 2026-04-21 — Complément batch facturation S05434 (1 facture — run 3)

- Type : création + posting + envoi (1 SO, 1 facture Odoo)
- Source : S05434 signalée par Nicolas — picking TT/PICK/08689 type=internal/done (même cause que run 2)
- Méthode : création manuelle account.move, action_post, account.move.send.wizard (ubl_bis3)
- Facture créée : id=36545, INV/2026/02168
- Partenaire : SRL Spydis - Intermarche Spy (id=116686)
- Montant HT : 315,10 EUR (305,10 SO + 10 TRANSPORT) | TTC : 335,51 EUR
- Echéance : 2026-05-21 (30 jours)
- Envoi Peppol : peppol_verification_state=valid — partner forcé invoice_sending_method=peppol — peppol_move_state=processing
- Total cumulé jour : 9 317,69 EUR HT / 9 900,49 EUR TTC (26 factures, runs 1+2+3)
- Rapport : compta/reports/invoicing_batch_2026-04-21.md (section "Complement S05434 — run 3")

## 2026-04-21 — Complément batch facturation S05448–S05453 (5 factures — run 2)

- Type : création + posting + envoi batch (5 SO, 5 factures Odoo)
- Source : SO confirmés par Nicolas — pickings internal done (TT/PICK/08711, 08713, 08714, 08715, 08716)
- Méthode : création manuelle account.move (wizard delivered inapplicable — pickings type=internal), action_post, account.move.send.wizard
- Note méthode : le wizard sale.advance.payment.inv refuse car les pickings sont de type internal et non outgoing — création ligne par ligne avec qty_delivered et discount=30% repris des SO
- Factures créées : 5 (IDs Odoo 36540–36544)
- Numéros attribués : INV/2026/02163 à INV/2026/02167
- Montant total HT : 1 770,30 EUR | TTC : 1 884,05 EUR
- TRANSPORT ajouté : 5 factures (10 EUR HT, compte 700000, TVA 21% — absent des SO)
- Lignes EM0072 (SRP Kraft Horeca) : conservées avec disc=100% (subtotal=0) comme dans les SO
- Envoi Peppol (UBL BIS3) : 5 factures toutes en peppol_state=processing
  - INV/02163 (Delhaize de Bouge, id 36540) — uuid f7eb688b-9214-4a8b-98f8-f79d7da30066 — échéance 2026-06-20 (délai Delhaize 60j)
  - INV/02164 (BOISDIS Naninne, id 36541) — uuid 700b53f5-0f18-4194-b6c8-1df4c3da4b94
  - INV/02165 (BOISDIS Naninne, id 36542) — uuid 0fb63a93-dd91-4f56-a4cf-98ea4cee4e39
  - INV/02166 (SA Barthe Assesse, id 36543) — uuid 26b4776f-6ac1-44ac-ad91-10d0fd26e293
  - INV/02167 (Lambertdis Spar Manhay, id 36544) — uuid d0ee1e08-6b97-4157-8c41-e06c29a79b1a
- Rapport : compta/reports/invoicing_batch_2026-04-21.md (section "Complément 5 SO — run 2")

## 2026-04-21 — Batch facturation S05351–S05439 (20 factures)

- Type : création + posting + envoi batch (23 SO, 20 factures Odoo)
- Source : sale.order invoice_status=to_invoice, state=sale/done, picking outgoing done
- Méthode : sale.advance.payment.inv wizard (delivered), action_post, account.move.send.wizard
- Factures créées : 20 (IDs Odoo 36509–36528)
- Numéros attribués : INV/2026/02137 à INV/2026/02156
- Montant total HT : 7 232,29 EUR | TTC : 7 680,93 EUR
- Corrections avant posting : 5 lignes supprimées (I0880 x3, I0859 x1, I0376 x1) — qty_delivered=0 inclus par erreur dans le wizard
- Partenaires forcés peppol : 5 (Lambertdis, NDB Diffusion, PGHM, Le 7 by Juliette, Labrassine)
- Envoi Peppol (UBL BIS3) : 9 factures — INV/02137 (Cafés Préko, 75ca7ecd), INV/02138 (DB Kfé, 37eab94a), INV/02139 (Delhaize, 28e8393f), INV/02141 (Le 7 Juliette, 90c3b497), INV/02152 (Lambertdis, 06a1b47b), INV/02153 (NDB Diffusion, cec483d4), INV/02154 (Villa d'Olne, a646b0b7), INV/02155 (PGHM, d0829a62), INV/02156 (Labrassine, 3266785d) — statut : processing
- Envoi email : 9 factures — INV/02140 (La Thé Box), INV/02143 (Alcodis), INV/02144 (Cafes Delahaut), INV/02145 (Sunparks De Haan), INV/02146 (Volle Gas), INV/02147 (Carrefour Remouchamps), INV/02148 (Carrefour Belgium), INV/02149 (BTL SRL), INV/02150 (Virelles Nature)
- Non envoyées : 2 — INV/02142 (Smartbox Group, 60 EUR), INV/02151 (Clotuche Caroline Suzanne, 28 EUR) — pas d'email ni Peppol valide
- Review : S05424 Marketing Teatower (707,55 EUR HT, partenaire interne, action Nicolas requise)
- Sans livraison (non traitées) : 19 SO (S05404, S05412, S05425, S05426, S05429, S05434, S05435, S05436, S05440, S05442, S05444, S05445, S05447–S05453)
- Rapport scan : compta/reports/shipped_not_invoiced_2026-04-21.md
- Rapport batch : compta/reports/invoicing_batch_2026-04-21.md

## 2026-04-15 — Batch S05405-S05409 : correction renvoi Peppol (3 factures)

- Type : correction invoice_sending_method + renvoi Peppol
- Partenaires mis à jour (invoice_sending_method -> peppol) : SA VILLERSEM (115879), DelEmbourg invoice addr (5733), DelEmbourg parent (2909), SA Faimine invoice addr (9196), SA Faimine parent (3210)
- INV/2026/02094 (DelEmbourg) — peppol_state=processing | uuid=2dc8107b-51cc-45dc-98f8-62aeab83dd4c
- INV/2026/02095 (SA Faimine) — peppol_state=processing | uuid=a4cf80f7-24c5-4b50-a50d-d6a915855a2c
- INV/2026/02096 (SA VILLERSEM) — peppol_state=processing | uuid=f58a082f-029c-48c1-972d-ef807690dfa2
- Rapport : compta/reports/batch_S05405_S05409_2026-04-15.md

## 2026-04-15 — Batch facturation S05405–S05409

- Type : création + posting + envoi batch (5 SO)
- Source : S05405 / S05406 / S05407 / S05408 / S05409 — tous state=sale, tous entièrement livrés
- Méthode : sale.advance.payment.inv wizard (delivered), action_post, account.move.send.wizard
- Factures créées : 5 (IDs Odoo 36242–36246)
- Numéros attribués : INV/2026/02092 à INV/2026/02096
- Montant total HT : 1 240,03 EUR | TTC : 1 314,43 EUR
- Envoi Peppol : 2 factures — S05405 (BARVO/Carrefour Barvaux, uuid 8caf61ac) + S05408 (GIMALEX/Delhaize Fragnée, uuid 9766cd23) — statut : processing
- Envoi email : 3 factures — S05406 (SA VILLERSEM), S05407 (SA Faimine), S05409 (DelEmbourg)
- Fallback email : S05406 + S05409 (Peppol EAS/endpoint configurés sur partenaire mais invoice_sending_method non défini)
- Rapport : compta/reports/batch_S05405_S05409_2026-04-15.md

## 2026-04-15 — Batch facturation : TRANSPORT + Posting + Envoi

- Type : correction transport + validation + envoi batch
- Lignes TRANSPORT ajoutées : 2 nouvelles factures draft créées (Odoo 36236, 36237) pour S05403 (Volle Gas) et S05375 (Carrefour Remouchamps) — 10 EUR HT chacune, produit [TRANSPORT], compte 700000, TVA 21%
- Les 7 autres lignes TRANSPORT des SO concernés étaient déjà facturées (qty_inv=1)
- action_post : 36 factures postées (IDs 36200–36237, hors avoirs 36223/36235) — 0 échec
- Numéros attribués : INV/2026/02055 à INV/2026/02090
- Montant total HT batch complet : 14 581,15 EUR | TTC : 15 482,38 EUR
- Envoi Peppol : 14 factures (Van Der Valk, ILLICO RESTO, Europadrinks, Delhaize x2, Pascal CHERAIN, Moulins Burette, Cafés Antillia, Spinée SA, All in One, SRL Tartine, Au Comptoir Local, Smart fridges, Carrefour Remouchamps TRANSPORT)
- Envoi email : 21 factures
- Non envoyé : 1 (INV/2026/02077 — Clotuche Caroline Suzanne, id=122331, pas d'email ni Peppol)
- Rapport mis à jour : compta/reports/invoicing_batch_2026-04-15.md

## 2026-04-15 — Batch facturation (34 factures draft créées)

- Type : création factures clients batch
- Source : sale.order invoice_status=to_invoice, state=sale/done (85 SO scannés)
- Méthode : sale.advance.payment.inv wizard, mode "delivered" (qty_delivered)
- Factures draft créées : 34 (IDs Odoo 36200–36234 sauf 36223/36235 qui sont des avoirs)
- Montant total HT : 14 561,15 EUR | TTC : 15 461,18 EUR
- Exclus Amazon : 36 SO (741,40 EUR HT) — détectés via origin "Amazon Order"
- Exclus 0 EUR : 5 SO (Marketing Teatower, Newpharma, Laetitia Mariette, Perte marchandise)
- Exclus sans livraison : 8 SO (3 403,22 EUR HT en attente livraison)
- Avoirs draft détectés : 2 (36223 ann philippe verhelle, 36235 Lidwine Fetten) — à examiner
- Rapport : compta/reports/invoicing_batch_2026-04-15.md
- Statut : DRAFT — Nicolas doit valider (action_post) avant envoi

## 2026-04-15 — Rapport commandes expédiées non facturées

- Type : analyse / rapport
- Source : sale.order (state: sale/done, invoice_status: to invoice, picking outgoing: done)
- Résultat : 70 SO to_invoice identifiées, dont 70 avec au moins un outgoing picking done
- Montant total HT : 14 173,10 EUR
- Rapport : compta/reports/shipped_not_invoiced_2026-04-15.md
- Top 3 : The Torrefactory Project Sa (1 950 EUR) / Carrefour Belgium (1 646 EUR) / Moulins Burette (1 406 EUR)
- Alerte : 34 commandes e-commerce de déc. 2025 (> 120 jours) non régularisées

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
| 2026-04-14 | 367 | - |
