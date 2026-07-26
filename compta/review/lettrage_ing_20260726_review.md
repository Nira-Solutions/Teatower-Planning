# Lettrage ING 26/07/2026 — lignes NON lettrées (à statuer par Nicolas)

Sur les 54 crédits ING non rapprochés au 26/07/26, 38 cas ont été lettrés automatiquement
(cf `compta/LOG.md` entrée du 26/07/2026, script `compta/lettrage_11_ing_20260726.py`).
Les 15 crédits ci-dessous n'ont **pas** été touchés : 8 parce qu'ils ne sont manifestement pas des
paiements clients (RH/interne), 7 parce qu'aucun match fiable n'a pu être établi (écart trop grand,
doublon possible, ou trop d'invoices ouvertes candidates).

## A) Ambigus — nécessitent une décision manuelle (7 lignes / 3.336,69 EUR)

| BSL id | Date | Montant | Libellé | Raison |
|---|---|---:|---|---|
| 19466 | 01/07 | +675,58 | NANRETAIL SA (Intermarché Naninne, partner 2812) — communication ***000/0038/68983*** | Cette communication structurée pointe vers INV/2026/02700 (716,11 EUR), **déjà `paid`** depuis mai. Aucune facture ouverte NANRETAIL ne correspond à 675,58 EUR, seule ou en combinaison. Déjà signalé identique le 14/07/26 (non résolu depuis). Possible double paiement client ou réutilisation erronée de la communication — à clarifier avec le client avant tout lettrage. |
| 19660 | 09/07 | +637,24 | ITM ALIMENTAIRE BELGIUM SA (= Centrale Intermarché, partner 124363, même adresse Rue du Bosquet 4 LLN) | 6 factures ouvertes chez Centrale Intermarché (48,10 / 123,10 / 48,10 / 675,00 / 235,60 / 714,00 EUR) : aucune ne vaut 637,24 EUR seule, et aucune combinaison ne tombe juste. Déjà signalé identique le 14/07/26. |
| 19784 | 15/07 | +67,00 | Smartbox Group (partner 3240) — communication non-belge "PDN-001927257,PCI-001927370" | Client réel avec **80+ factures ouvertes** (petits montants type carte-cadeau : 24,20 à 179,30 EUR). Aucune facture seule ni paire évidente ne vaut exactement 67,00 EUR ; le format de communication (PDN/PCI, système Smartbox propre) ne correspond à aucune référence structurée belge stockée dans Odoo. Trop de candidats pour un matching fiable — à traiter manuellement (vérifier portail Smartbox pour le détail de la remise). |
| 19815 | 16/07 | +111,55 | Faire Wholesale B.V. (partner 6404, Faire.Com) | 2 lignes ouvertes seulement : INV/2026/02758 (127,20 EUR) et une écriture bancaire BNK1/25-26/5855 (232,46 EUR, pas une facture). Aucune ne correspond à 111,55 EUR ni en écart ≤5 EUR. À vérifier sur le portail Faire (probablement une commission/frais déduits par Faire avant virement, ou solde d'une autre commande non facturée côté Odoo). |
| 19876 | 20/07 | +688,89 | Courses L SRL (Carrefour Market Courcelles) — communication ***000/0040/27823*** identique à celle déjà utilisée | Ce paiement réutilise la même communication structurée que le BSL 19661 du 09/07, **déjà lettré le 14/07/26** sur INV/2026/03057 (688,89 EUR, désormais `paid`, résiduel 0). Aucune autre facture ouverte Carrefour Market Courcelles ne correspond. **Probable double paiement du client** — à vérifier avant tout traitement (remboursement éventuel, ou nouvelle facture à émettre si marchandise supplémentaire livrée). |
| 19914 | 22/07 | +720,44 | Spar Vaux-sur-Sûre (Louis Besseling Distribution, partner 125094) — communication ***000/0042/65976*** | La communication pointe vers INV/2026/03528 (total 720,44 EUR) mais cette facture est déjà `partial` avec résiduel de seulement 680,54 EUR (39,90 EUR déjà réglés par un autre canal). Le client semble avoir payé le **montant total de la facture** sans tenir compte du règlement partiel antérieur → risque de surpaiement de 39,90 EUR. Écart (39,90 EUR) > tolérance 5 EUR, situation à trancher par Nicolas (affecter le surplus à une prochaine facture, ou vérifier si le "partiel" antérieur est lui-même une erreur à corriger). |
| 19952 | 24/07 | +436,84 | Dynamic Food SRL - Spar Louvain-La-Neuve (partner 113216) — communication ***000/0040/30348*** | Cette communication pointe vers INV/2026/03067, **déjà `paid`** (résiduel 0, total 521,54 EUR). Seule ligne ouverte restante pour ce client : RINV/25-26/0342 (avoir, résiduel -84,70 EUR), qui ne se combine pas avec 436,84 pour retomber sur un montant cohérent. Communication probablement réutilisée par erreur côté client — à clarifier avant lettrage. |

## B) Hors-scope — pas des paiements clients (8 lignes / 4.055,33 EUR, non touchées)

| BSL id | Date | Montant | Libellé | Nature |
|---|---|---:|---|---|
| 19630 | 08/07 | +79,51 | Baloise Belgium S.A — "ADAPTATION SALAIRE A/26.00112 DATE ACCID" | Remboursement assurance salaire/accident du travail — famille 455000 neutre, pas un client (déjà signalé le 14/07). |
| 19652 | 09/07 | +124,95 | Pluxee Belgium — chèques-repas | Flux RH, pas un client. |
| 19771 | 15/07 | +33,28 | Pluxee Belgium — chèques-repas | Idem (2e occurrence dans ce lot). |
| 19826 | 17/07 | +17,59 | Edenred Belgium — chèques-repas | Idem famille RH (Pluxee/Edenred), pas un client. |
| 19682 | 10/07 | +500,00 | Virement instantané depuis TEATOWER BE86068958071350 (compte BNK2) | Virement interne entre comptes propres Teatower, pas un encaissement client. |
| 19812 | 16/07 | +300,00 | Idem — TEATOWER BNK2→BNK1 | Virement interne. |
| 19813 | 16/07 | +2.000,00 | Idem — TEATOWER BNK2→BNK1 | Virement interne. |
| 19950 | 24/07 | +1.000,00 | Idem — TEATOWER BNK2→BNK1 | Virement interne. |

## Résumé

- 54 crédits ING non rapprochés au 26/07/26 → **38 lettrés** (39 lignes bancaires, 16.241,92 EUR), **15 restants** (7 ambigus + 8 hors-scope).
- Aucune ligne débitrice (38 lignes, frais/fournisseurs/salaires/ONSS/cartes) n'a été touchée — hors périmètre explicite (write-off autorisé uniquement sur paiements clients).
