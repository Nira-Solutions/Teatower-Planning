# Audit configuration Odoo Teatower — 2026-04-14

> Base `tsc-be-tea-tree-main-18515272` — Odoo 18 — lecture seule XML-RPC.
> Données brutes : `odoo/audit_config_data.json` (12 domaines, 100 % OK).
> Consultant : agent ODOO Teatower, profil senior.

---

## 1. Entrepôts & routes

**Chiffres** : 8 warehouses (TT, GMS, LIEGE, WAT, NAM, POP, Sales, OPA), 22 picking types, 30 routes actives, 50 catégories produit.

- Ce qui va bien : un WH principal (TT) en 2-steps réception + pick_ship livraison, les 5 WH magasins en 1-step (cohérent pour un point de vente). OPALYA en 2-steps. Toutes les catégories sont en `standard` / `manual_periodic` → **valorisation comptable sans double écriture de stock** (simple, peu d'écart).
- Attention :
  - **30 routes actives pour 8 warehouses** — forte prolifération. Routes dupliquées (« Magasin Waterloo (copie) », « Stock Merchandiser (copie) ») — deux WH fantômes (`WAT copie` id=6, `Merchandiser copie` id=7) avec leurs propres routes `Recevoir/Livrer en 1 étape`. Pollution de l'UX sur la fiche produit (champ `route_ids`) et risque d'erreur de sélection.
  - Routes custom `Réapprovisionnement POP-UP/NAMUR/WAT/LIEGE/GMS` — doubles par rapport aux routes auto-générées `Magasin X: Réapprovisionner depuis Tea Tree`. À aligner sur une seule convention.
  - Picking type « Transferts internes » par WH magasin a `src=dst=Magasin/Stock` — c'est un placeholder, pas le type utilisé pour TT→WAT. Vérifier que les réassorts passent bien par un picking type avec `src=TT/Stock` et `dst=WAT/Stock` (cf. `feedback_transferts_internes.md`).
  - **Toutes les reservation methods = `at_confirm`** — OK mais rigide. Pour TT/Bons de livraison, passer en `manual` éviterait les réservations fantômes quand il manque du stock.
- Cassé/dangereux : `property_valuation = manual_periodic` sur les 50 catégories — **pas de valorisation perpetual**. Pour une PME avec ~1.7 M€ CA et du stock en GMS, c'est acceptable, mais la valeur stock comptable ne reflète la réalité qu'après l'inventaire périodique (risque clôture).
- 🎯 Top 3 :
  1. **Archiver les 2 WH « copie »** (ids 6 et 7) et leurs 6 routes associées — gain UX énorme, effort 30 min.
  2. **Consolider les routes de réapprovisionnement** : soit les custom, soit les auto, pas les deux. Effort 2 h.
  3. **Picking type « Bons de livraison » en `reservation_method=manual`** — évite les réservations auto sur stock négatif. Effort 5 min, bénéfice quotidien.

---

## 2. Orderpoints / Réapprovisionnement

**Chiffres** : **1 715 orderpoints** (attendu ~1716), 0 orphelin inactif, 0 doublon (product × location).

Répartition :
- TT/Stock : 526
- LIEGE/Stock : 378
- NAM/Stock : 370
- WAT/Stock : 362
- GMS/Stock : 47
- POP/Stock : 30
- Sales/Stock : 1, TT/Entrée : 1 (suspects)

- ✅ Base solide, zéro déchet. Formule maison min/max respectée.
- ⚠️ **1 orderpoint sur `TT/Entrée`** et **1 sur `Sales/Stock`** — mal placés (TT/Entrée est une location transit de réception, pas une source d'approvisionnement). À archiver.
  - `mto_route_count = 0` : pas de MTO activé. Normal pour un modèle B2B stock, mais pour les kits displays à la commande ça pourrait simplifier.
  - `supplierinfo_delay_0 = 1011 / 1529` — **66 % des fournisseurs n'ont pas de lead time renseigné**, donc l'orderpoint commande « pour aujourd'hui ». Très impactant quand Kirchner livre en 15-20 jours.
- 🔴 Le delay=0 fait que le scheduler peut déclencher des RFQ trop tard. À corriger en priorité.
- 🎯 Top 3 :
  1. **Renseigner `delay` sur les 1 011 supplierinfo à 0 j** — priorité Kirchner (~300 lignes). Effort 2 h script + 1 h validation.
  2. Archiver les 2 orderpoints mal placés. Effort 5 min.
  3. Ajouter **`security_lead`** (sécurité) sur `res.company` — 3 à 5 jours pour amortir les retards Kirchner. Effort 2 min.

---

## 3. Produits

**Chiffres** : 1 687 templates = 1 687 products (un seul product par template, variantes quasi inexistantes : 2 templates avec `attribute_line_ids`).

Répartition :
- 1 451 `consu + is_storable=True` ✅ (migration Odoo 18 faite)
- 166 `consu + is_storable=False` (consommables vrais, non stockés)
- 70 `service`
- **0 `type=product`** (ancien type, bien migré)

Problèmes :
- **698 produits (41 %) avec `purchase_ok=True` sans aucun fournisseur** (`seller_ids` vide). Exemples : V0706, I0706, E0706, ATELIER-TT-LIEGE, MP_1V0706…
- **594 produits (35 %) avec `standard_price=0`** et `sale_ok=True` — coût non renseigné → **marge fausse en facturation, valorisation stock = 0**.
- **752 products sans barcode** (45 %) — bloquant pour scan magasin & GMS.
- **209 templates sans `default_code`** — bloquant pour import/export Excel.
- **1 doublon** default_code : `MP_1V0253` (matière première en double).

- 🎯 Top 3 :
  1. **Remplir `standard_price` sur les 594 produits** (priorité GMS I0xxx/V0xxx où ~250 SKUs tournent chaque mois). Effort : 1 jour script + vérif manuelle. Impact direct sur la marge reportée.
  2. **Ajouter seller_ids manquants** (Kirchner pour vracs V0xxx, idem I0xxx) — sinon les orderpoints `buy` restent en erreur silencieuse. Effort 3 h.
  3. **Default_code obligatoire** (ajouter `sql_constraint` via base.automation ou script check). Effort 1 h.

---

## 4. BoM / MRP

**Chiffres** : 803 BoM (797 `normal`, 6 `phantom`). 2 407 MO total, **27 MO stales** (confirmed/progress depuis > 30 j). 0 BoM avec composant inactif.

- ✅ Zéro BoM cassée, ratio phantom faible et contrôlé (échantillons + FBA).
- ⚠️ 6 phantoms seulement alors que la doc parle de kits displays & packs Amazon — vérifier que tous les kits commerciaux sont bien phantomés (sinon stock fini reporté à tort).
- 🔴 **27 MO traîneuses** — bloquent des composants en réservation. Probable : MO confirmés jamais clôturés au magasin.
- 🎯 Top 3 :
  1. Clôturer ou annuler les 27 MO > 30 j. Effort 2 h.
  2. Auditer que chaque « display » / « pack » est bien en BoM phantom (sinon le stock fini est faux). Effort 3 h.
  3. Activer `components_availability` alert dans le dashboard MRP. Effort 10 min.

---

## 5. Ventes

**Chiffres** : 7 657 SO total — 7 276 confirmées sur 12 mois, 11 draft, 0 sent, 90 cancel. **965 SO (~13 %) sans `client_order_ref`** (devrait être systématique pour GMS).

- 6 pricelists, toutes actives : `Par défaut`, `Newsletter 5%`, `Odoo x Shopify PriceList`, **`Newsletter 5% (EUR)5413393800242`** (nom cassé, ressemble à un EAN GMS collé par erreur), `Newsletter 5% (EUR)`, `Merchandiser`.
- 16 payment terms, 9 delivery carriers.
- ✅ Volume OK, peu de cancel (1.2 %).
- ⚠️ Pricelist au nom cassé → à renommer ou archiver.
  - **965 SO sans référence client** → risque sur les rapprochements factures GMS.
- 🎯 Top 3 :
  1. **Rendre `client_order_ref` obligatoire** pour les clients GMS (via `ir.rule` ou `base.automation`). Effort 1 h.
  2. Renommer/archiver la pricelist `Newsletter 5% (EUR)5413393800242`. Effort 2 min.
  3. Auditer les 16 payment terms (trop pour une PME BE — normalement 30/60/immédiat + 3 variantes suffisent). Effort 30 min.

---

## 6. Achats

**Chiffres** : 459 PO, 355 confirmés sur 12 mois, **4 RFQ dormantes** (>30 j), 1 529 supplierinfo, **1 011 sans délai (66 %)**.

- ✅ Peu de RFQ dormantes, volume cohérent.
- 🔴 **delay=0 sur 66 % des lignes fournisseur** → scheduler bas-de-gamme, cf. §2.
- 🎯 Top 3 :
  1. Script de mass-update `delay` Kirchner (15 j), transporteurs, emballeurs. Effort 1 h.
  2. Nettoyer les 4 RFQ dormantes. Effort 15 min.
  3. Activer `purchase.order.invoice_control` = `on_received_qty` par défaut pour les fournisseurs import (3-way match). Effort 10 min/fournisseur.

---

## 7. Comptabilité

**Chiffres** : 25 journaux (4 sale INV/INV1/INV2/INV3/INV4, 1 BILL, 2 bank BNK1+MOL, 5 cash, MISC/OD + ~10 général), 84 taxes actives, 24 304 account.move postés. **339 factures clients ouvertes, dont 132 (> 60 j)** — 39 % de l'ouvert en retard.

- Taxes BE : 0/6/12/21 % présentes en sale ET purchase, 0% Cocont + 0% EU S/M/T/EX bien configurées. ✅ Belle couverture fiscale.
- **0 analytic plan** — pas d'analytique activée. Plus de visibilité par canal (B2B/GMS/Horeca/DTC) = aveugle sur la rentabilité par segment.
- ⚠️ 4 journaux de ventes + 4 journaux cash + 3 journaux divers (AMO, BO, CABA, POSS, STJ, SAL) → journaux trop nombreux, risque de mal-classement.
  - 132 factures > 60 j impayées → activer relances auto (Account Report Followup cron existe déjà !).
- 🔴 **132 / 339 factures impayées > 60 j** = ~39 % du portefeuille ouvert. Impact cash direct.
- 🎯 Top 3 :
  1. **Activer & paramétrer les follow-up levels** (cron déjà actif), envoi auto J+30/J+45/J+60. Effort 2 h.
  2. **Créer un plan analytique** « Canal » (GMS/Horeca/DTC/Shopify/Amazon) + règles d'auto-distribution via `team_id`. Effort 4 h, ROI énorme.
  3. Archiver les journaux de ventes INV2/INV3/INV4 si non utilisés (vérifier via `account.move` count). Effort 30 min.

---

## 8. Automations / ir.cron

**Chiffres** : 53 crons, **tous actifs**. 0 base.automation, 0 mail_server custom (Odoo SMTP natif), 0 fetchmail.

- ✅ Crons critiques tournent bien (Shopify 10-15 min, Amazon 30 min, scheduler MRP 1 j, OCR factures, PEPPOL 6-12 h).
- ⚠️ **« Amazon: sync feeds »** et **« Product Images: Get product images from Google »** et **« Sale Pdf Quote Builder »** = `9999 months` = désactivés silencieusement (jamais next call). Legacy.
- 0 `base.automation` → aucune règle business auto. Manqué : forcer format `I0xxx`, forcer `client_order_ref`, auto-attacher PDF devis.
- 🎯 Top 3 :
  1. **Créer des `base.automation`** : (a) normaliser `IOxxx→I0xxx` sur sale.order avant création ; (b) obliger `client_order_ref` pour GMS ; (c) alerter quand `standard_price=0` à la vente. Effort 2 h, récurrent.
  2. Désactiver/supprimer les 3 crons legacy `9999 months`. Effort 5 min.
  3. Mettre en place un SMTP custom (SendGrid/Brevo) pour les emails sortants — la délivrabilité native Odoo est correcte mais l'IP est partagée. Effort 1 h.

---

## 9. Séquences

**Chiffres** : 233 séquences. 9 prefixes en doublon (`Liege bis/`, `Liège/`, `Namur/`, `POP-UP STORE/`, `Waterloo/`, `COPIE/MO/`, `COPIE/SFP/`, `COPIE/PC/`, `COPIE/POS/`).

- Sale : prefix `S`, padding 5, standard ✅
- Purchase : prefix `P`, padding 5 ✅
- Account.move : par journal
- Account.payment : prefix `PAY`, padding 5

- ⚠️ Les `COPIE/...` = 4 séquences orphelines liées aux WH copies (cf. §1).
- ⚠️ Aucune séquence `no_gap` sur les factures (`account.move`) — en BE, c'est requis par la loi pour les factures de vente (numérotation continue sans trou). À vérifier côté journaux sale.
- 🎯 Top 3 :
  1. **Vérifier que les séquences `account.move` journaux sale sont bien `no_gap`** — obligation fiscale BE. Effort 15 min vérif.
  2. Supprimer les 4 séquences `COPIE/*` (si WH archivés). Effort 10 min.
  3. Unifier nomenclature magasins (`Liège/` vs `Liege bis/`). Effort 15 min.

---

## 10. Utilisateurs & permissions

**Chiffres** : 13 users total (12 internal actifs + 1 portal), **1 seule company**. Groupes : 56 à 66 par user.

Utilisateurs internes :
- admin (66 groups) — **à désactiver en prod**, c'est un super-user par défaut
- apps@teatower.com (62) — **compte de service ? vérifier**
- nicolas.raes (65), adrianne.buttiens (66) — admins métier
- 4 comptes magasin (magasinliege/namur/waterloo, info)
- stephan.pire, aurelie.thibaut, jerome.carlier, factures@noenature.com

- 🔴 **Compte `admin` actif** — classique vecteur de compromission. À désactiver après avoir vérifié qu'un user nommé a tous les droits.
- 🔴 `apps@teatower.com` à 62 groupes — si c'est un compte API, il ne devrait avoir que les droits minimaux (pas l'admin).
- ⚠️ `adrianne.buttiens` à 66 groupes = full admin. OK si co-founder, sinon downgrade.
- 🎯 Top 3 :
  1. **Désactiver `admin`** après clone d'un user nommé super-admin. Effort 30 min.
  2. **Créer une API key** pour un user technique dédié Shopify/Amazon (pas `apps`), et limiter ses droits. Effort 1 h.
  3. Auditer les droits des comptes magasin (doivent être POS/Stock, pas Accounting). Effort 30 min.

---

## 11. Intégrations

**Modules** : 236 installés, 24 apps. Shopify via `shopify_ept` (Emipro), Amazon via `sale_amazon` natif.

- ✅ Shopify EPT + Amazon Connector en place. Crons Shopify à 10 min (orders, products), 15 min (stock export). Amazon 30 min (delivery).
- ⚠️ `Amazon: sync feeds` désactivé (9999 months) — à investiguer, sinon les feeds sortants ne partent pas.
- ⚠️ **`delivery_sendcloud`** installé, `iot`, `sign`, `web_studio`, `documents`, `mass_mailing_sms` — vérifier lesquels sont vraiment utilisés (chaque app inutilisée = crons, fichiers, perfs).
- 🎯 Top 3 :
  1. Investiguer `Amazon: sync feeds` (désactivé). Effort 30 min.
  2. Désinstaller les modules inutilisés (économie crons). Effort 2 h.
  3. Tester fin-de-chaîne Shopify : cron Process Orders → sale.order → picking. Effort 1 h.

---

## 12. Qualité des données

**Chiffres** : 33 529 partenaires (gros volume — historique DTC + Shopify). 
- **1 631 clients sans email ni téléphone** (5 %).
- **51 VAT en doublon** (partners avec même TVA).
- **1 000 emails en doublon** (partners avec même email).

- ✅ Volume cohérent avec le CA.
- 🔴 51 doublons VAT = doublons clients B2B (TVA unique par entité). Risques : facturation au mauvais partenaire, mauvais reporting CA, pricelists incohérentes.
- 🔴 1 000 doublons email — souvent des comptes Shopify vs Odoo natif vs invités B2C. Typiquement fusionnables via l'outil de merge natif.
- 🎯 Top 3 :
  1. **Merger les 51 doublons VAT** (vue `res.partner.merge` natif). Effort 4 h.
  2. Script auto de merge par email exact pour les partners B2C sans commandes actives. Effort 2 h.
  3. Contrainte `sql_constraint` pour empêcher les nouveaux doublons VAT. Effort 30 min.

---

## Top 10 priorités consolidées (ROI)

| # | Prio | Titre | Pourquoi | Effort |
|---|------|-------|----------|--------|
| 1 | **P1** | Renseigner `delay` sur 1 011 supplierinfo (priorité Kirchner) | Le scheduler déclenche RFQ trop tard, ruptures de stock GMS | 2 h |
| 2 | **P1** | Remplir `standard_price` sur 594 produits | Marge fausse, valorisation stock = 0 | 1 j |
| 3 | **P1** | Relances auto factures (132 / 339 impayées > 60 j) | Cash direct, cron déjà en place à paramétrer | 2 h |
| 4 | **P1** | Désactiver admin + sécuriser apps@teatower.com | Risque sécurité majeur | 1 h 30 |
| 5 | **P1** | Merger les 51 doublons VAT B2B | Facturation + reporting corrects | 4 h |
| 6 | **P2** | base.automation IOxxx→I0xxx + client_order_ref obligatoire GMS | Évite 100 % d'erreurs manuelles | 2 h |
| 7 | **P2** | Archiver 2 WH « copie » + 4 séquences + routes associées | UX fiche produit, moins d'erreurs | 2 h |
| 8 | **P2** | Créer plan analytique « Canal » (GMS/Horeca/DTC/Shopify/Amazon) | Rentabilité par segment, base du forecast | 4 h |
| 9 | **P2** | Clôturer 27 MO traîneuses (>30 j) | Libère composants réservés | 2 h |
| 10 | **P3** | Seller_ids + default_code obligatoires, désinstaller modules morts, picking BL en `manual` | Propreté data + perfs | 1 j total |

---

*Fin audit — rédigé 2026-04-14, agent ODOO Teatower, 0 écriture effectuée.*
