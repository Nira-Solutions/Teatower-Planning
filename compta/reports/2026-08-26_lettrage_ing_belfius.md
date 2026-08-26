# Lettrage ING + Belfius — 26/08/2026

**Demande** : « lettre ING et Belfius ».
**Périmètre** : journaux 14 (ING BE30 3631 6408 2311) et 36 (Belfius BE86 0689 5807 1350).
**Résultat** : **103 → 97** lignes non lettrées. 6 opérations, 0 erreur.

Script : `compta/lettrage_27_ing_belfius_20260826.py` (dry-run puis `--apply`).
Outils : `compta/scan_lettrage_20260826.py`, `compta/match_lettrage_20260826.py`.

---

## Ce qui a été traité

| BSL | Date | Montant | Traitement | Pièce |
|---|---|---|---|---|
| ING 20541 | 24/08 | +332,51 | Lettré | INV/2026/03943 Spar Clavier (comm `000/0044/83117`) — écart +0,01 → write-off 757100 `MISC/26-27/08/0018` |
| ING 20542 | 24/08 | +789,61 | Lettré | INV/2026/03893 SPRL Durant-Rabaey (comm `000/0044/60279`) — écart −0,02 → write-off 657100 `MISC/26-27/08/0019` |
| BELF 20560 | 25/08 | −2 000,00 | Facture postée + lettrée | Vilna Gaon `INV/2026/00010` → **RESA1279** |
| BELF 20562 | 26/08 | −8 945,00 | Lettré (partiel) | ONSS `116/5516/51214` → SD Worx : RESA522 soldée (53,56) + RESA713 partielle (reste 1 903,03) |
| ING 20540 | 24/08 | +532,03 | Repointé sans lettrage | Cafermi — **double paiement**, crédit ouvert sur le compte client |
| BELF 20561 | 26/08 | +15 000,00 | Repointé 580000 | Virement interne ING → Belfius, contrepartie ING pas encore importée |

### Détails des deux cas non triviaux

**Vilna Gaon (2 000,00).** La pièce existait, mais en **brouillon** : `INV/2026/00010`, 1 652,89 sur 616600 Frais de marketing + 347,11 de TVA, échéance 25/08, `payment_reference` = `+++000/0001/68132+++`, exactement la communication structurée du virement Belfius. Le brouillon a été validé (→ RESA1279) puis lettré au centime. Rien d'arbitraire : la facture était déjà encodée et payée, il ne manquait que la validation.

**Cafermi (532,03).** Le virement du 24/08 arrive **sans communication**. `INV/2026/03522` (532,03) est déjà soldée — mais soldée par un **trop-perçu ancien** : le 21/10/2025, Cafermi avait payé deux fois `INV/2025/03524` (752,51), avec une communication erronée (`000/0023/78419`, celle d'une autre facture) ; 532,03 de ce crédit avaient été affectés le 14/07 à `INV/2026/03522`. Le client paie donc aujourd'hui une facture déjà apurée avec son propre argent. Traitement : crédit ouvert sur le compte client, sans lettrage.

> **À arbitrer** : Cafermi a désormais **752,51 € de crédit ouvert** (220,48 de 2025 + 532,03) contre une seule facture ouverte de 35,00 → solde client **−717,51 €**, en sa faveur. Rembourser, ou imputer sur les prochaines factures.

**ONSS (8 945,00).** Même montant et même référence ONSS que le paiement du 16/07 (BSL 19811), qui avait été lettré en 440000 / SD Worx Secrétariat Social contre les documents comptables 1BT1014 (RESA467 + RESA522) en FIFO. Le même schéma a été reproduit. Deux paiements identiques à 8 945,00 = probable plan d'apurement — **à confirmer** ; le lettrage est réversible si la clé d'imputation diffère.

---

## Non traité — pièce ou arbitrage manquant

### Encaissements clients bloqués

| Ligne | Montant | Blocage |
|---|---|---|
| ING 20381 Delhaize Le Lion | +2 652,97 | Avis `/ADV/2000058526` cité dans le libellé mais non fourni ; subset-sum ≤4 pièces = 18 combinaisons, aucune unique |
| ING 19660 + 20373 ITM Alimentaire | +637,24 / +160,61 | Paiements de centrale Intermarché ; IBAN BE75 3701 0623 0851 non enregistré, aucune combinaison sur les 38 factures ouvertes. Avis à réclamer (réfs 0000287398 / 0000290027) |
| ING 20522 Amazon Payments | +41,21 | Settlement marketplace (SLR4RLYM9OWD9M53), pas une facture client → rapport Amazon |

### Décaissements fournisseurs bloqués

| Ligne | Montant | Blocage |
|---|---|---|
| ING 19625 Kirchner (domiciliation) | −12 837,54 | 46 factures ouvertes (161 522,58) ; le subset trouvé fait 8 pièces → non unique. Avis de prélèvement requis |
| BELF 20352 Kirchner (clearing) | −49 551,11 | Idem, subset de 14 pièces → non unique. Avis de compensation requis |
| ING 19944 / 20548 / 20549 Proximus | −200 / −937,17 / −100 | 14 factures ouvertes (1 469,94) : aucun montant ni subset ne tombe. Factures non encodées ou plan de paiement |
| ING 20546 Worldline | −541,17 | 5 factures ouvertes (2 402,32), aucune à 541,17 → facture du mois non encodée |
| Radius, Sendcloud, Google, Skeepers, CILE, Adobe, Intuit, Shopify, Faire, Douanes | divers | **Aucune facture d'achat ouverte** à ces noms → charges directes à imputer, rien à lettrer |

### Arbitrages Nicolas

| Ligne | Montant | Question |
|---|---|---|
| BELF 20350 Nira Solutions | +10 000,00 | « Prêt actionnaire ». Aucun compte courant associé n'existe (489020 = NOE NATURE, 489030 = TEA TOUCH). **Créer 489040/489050, ou passer par 416100 / 489100 ?** |
| BELF 20353 Jean-Noël Tilman | +30 000,00 | Idem |
| BELF 19188 | +30 000,00 | Mise à disposition du crédit Belfius 071-9574936-30 → écriture de financement (173/174), pas un lettrage |
| BELF ×10 « CHARGES ÉCHUES CRÉDIT PROF. » | −273,64 / −410,46 / −706,91 / −2 559,85 récurrents | Mensualités capital + intérêts des crédits 071-9570627/28/29 et 071-9574936 → à ventiler sur le tableau d'amortissement |
| BELF frais de compte | −4,42 / −3,08 / −15,00 / −39,83 | Les 3 factures RESA832/894/1047 à 5,14 ne correspondent à aucun prélèvement ; ces lignes-ci n'ont pas de RESA → charges directes 650000/613xxx |
| ING avances salaires (van Ooteghem, Cabosart, Vansimpsen) | −750 / −1 000 / −500 récurrents | Avances sur salaire → 421/453 ou compte courant, pas un lettrage |

---

## Reste à faire pour vider la banque

Les 97 lignes restantes ne sont **pas** un problème de lettrage : ce sont, pour l'essentiel, des **charges sans pièce encodée** (domiciliations SaaS, frais bancaires) et des **écritures de financement** (crédits, prêts actionnaires). Trois chantiers, par ordre de rendement :

1. **Réclamer 4 avis de paiement** — Delhaize, Intermarché (×2), Kirchner (×2). Débloque ~66 k€ de lignes.
2. **Ventiler les mensualités de crédit** sur les tableaux d'amortissement Belfius — ~10 lignes récurrentes, à automatiser une fois la clé posée.
3. **Décider du compte des prêts actionnaires** (40 000 € encaissés en août) — arbitrage à trancher, c'est du bilan.
