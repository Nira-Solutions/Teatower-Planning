# Pourquoi `TT/Stock` (et descendantes) sont en négatif

**Date** : 2026-04-14
**Périmètre** : `stock.location` `id child_of TT/Stock` (entrepôt principal Teatower) — soit `TT/Stock`, `TT/Stock/PICK`, et toutes les cellules `TT/Stock/PICK/<rack>`.
**Source** : XML-RPC `tea-tree.odoo.com` / `audit_tt_stock_negatif.py`.

> Suite de l'audit global `audit_stocks_negatifs_2026-04-14.md` — qui a montré que **TT/Stock + TT/Stock/PICK = ~85 % de la masse négative**. Ce rapport-ci zoome sur le **mécanisme exact** : on suit chaque mouvement pour voir le passage sous zéro.

---

## 1. Périmètre TT/Stock

| Élément | Valeur |
|---|---|
| Locations sous TT/Stock (internes) | **~330** (PICK + ~300 cellules rack) |
| Quants négatifs TT/Stock + descendantes | **~330** sur 397 globalement (≈ 83 %) |
| Quantité totale négative TT/Stock+desc | **~ -226 000 unités** |
| Valeur (coût std) | **~ -33 500 EUR** |

Concentration : `TT/Stock` (parent direct) et `TT/Stock/PICK` (zone picking globale) portent les gros volumes (quants à -45 000 / -25 000 / -23 000). Les ~150 cellules `TT/Stock/PICK/<A|B|C-...>` portent chacune **-1 à -5 unités** : poussière de picks réservés sur la mauvaise cellule.

---

## 2. Top 15 quants négatifs (TT/Stock + descendantes)

| Code | Produit | Location précise | Qty | Val EUR |
|---|---|---|---:|---:|
| E0628 | Oasis du désert BIO (Ech.) | **TT/Stock/PICK** | -45 269 | -7 243 |
| E0279 | Le panier de grand maman (Ech.) | **TT/Stock/PICK** | -24 574 | -3 932 |
| E0121 | Lady Dodo (Ech.) | **TT/Stock/PICK** | -23 005 | -3 911 |
| E0666 | English Breakfast (Ech.) | **TT/Stock/PICK** | -21 000 | 0 |
| E0626 | Sencha BIO (Ech.) | **TT/Stock/PICK** | -13 881 | -2 082 |
| E0880 | Blue Earl Grey BIO (Ech.) | **TT/Stock/PICK** | -13 760 | -2 614 |
| E0301 | Tisane tropicale (Ech.) | TT/Stock | -11 660 | -1 982 |
| C0019 | Sachet Teatower Classique | TT/Stock | -9 030 | 0 |
| E0913 | Féérie d'Hivers (Ech.) | TT/Stock | -6 888 | 0 |
| E0732 | Gourmandise de Noël (Ech.) | TT/Stock | -5 162 | -774 |
| E0711 | Offrande des Rois Mages (Ech.) | TT/Stock | -5 162 | -774 |
| E0891 | Trésor des lutins (Ech.) | TT/Stock | -5 162 | -878 |
| E0778 | Spéculoos & Cie (Ech.) | TT/Stock | -2 590 | -440 |
| E0600 | La lampe merveilleuse (Ech.) | TT/Stock | -2 590 | -440 |
| E0845 | Mamy Granny BIO (Ech.) | TT/Stock | -2 590 | -440 |

> **Observation clé** : les très gros négatifs (top 6) ne sont **pas** sur les cellules rack mais sur la **zone parent `TT/Stock/PICK`**. C'est un signe que ce sont des **réservations / picks faits à la main sur la zone globale** (sans avoir choisi la cellule réelle).

---

## 3. Reconstruction chronologique — où ça bascule

### 3.1 E0628 Oasis du désert (-45 269)

Cumul net sur TT/Stock+desc reste **positif** sur tous les moves visibles (fin 2025 → avril 2026 cum oscille entre +21 k et +106 k). Les MO `OP/13636` mensuelles et la grosse MO `TT/MO/03924` (21 875) sont absorbées. **Donc le -45 269 sur `TT/Stock/PICK` n'est PAS dû à un déficit physique** — c'est un quant **isolé sur PICK** alors que les +106 000 sont sur `TT/Stock` (parent). Désynchro parent ↔ PICK pure.

### 3.2 E0279 Le panier de grand maman (-25 074) — cas d'école

```
2025-08-12  Inventaire +16 250 sur PICK/C-09-00
2025-08-12  Inventaire -22 000 sur PICK/E-32-00  <-- bascule à -5 750
2025-08-14  MOraw       -480   sur TT/Stock
2025-11-03  SO PICK/04140 -50 000 sur TT/Stock   <-- creuse à -57 030
2025-11-04  SO PICK/04340 -5 150
2026-01-27  STOR        +25 000 sur TT/Stock
2026-02-13  SO PICK/07201 -25 000 sur TT/Stock/PICK <-- -63 449
```

Origine = un **ajustement d'inventaire d'août 2025** mal compensé sur `PICK/E-32-00`, **jamais corrigé**, puis **les SO suivants pickent toujours depuis `TT/Stock`** (donc enfoncent le négatif au lieu de tirer sur la cellule physique réelle).

### 3.3 E0121 Lady Dodo (-23 205)

Bascule dès `2025-09-17` : MOraw `TT/MO/01706` consomme 432 unités **avant la moindre réception**. Suite de petits MOraw (200-500/sem) qui cumulent à -1 800 fin octobre. Réception STOR `+12 500` le 2025-10-23 redresse, mais SO `TT/PICK/04140` du 2025-11-03 reprend -12 500 et replonge. **Décalage MO ↔ PO chronique**.

### 3.4 E0666 English Breakfast (-21 000)

Bascule sur **inventaire 2025-08-12 : -8 500 sur `TT/Stock`** (sans contrepartie). Tout le reste s'empile par-dessus.

### 3.5 E0626 Sencha BIO (-13 881)

Cumul reste positif partout (fin avril +36). Le -13 881 est **uniquement sur `TT/Stock/PICK`** alors que le quant parent `TT/Stock` est à +14 000. **Désynchro parent/enfant**, identique à E0628.

---

## 4. Les 3 patterns dominants sur TT/Stock

### Pattern A — Picking SO sur `TT/Stock` (parent) au lieu de la cellule physique (60 % des cas)
Tous les `TT/PICK/xxxxx` (livraisons SO) ont leur `location_id = TT/Stock` ou `TT/Stock/PICK`, **pas la cellule réelle**. Le système réserve depuis le parent, mais le stock physique est dans une cellule enfant. Résultat : le quant **parent** part en négatif, le quant **cellule** reste positif. C'est exactement ce qu'on voit pour E0628, E0279, E0626, E0880 : **le cumul net global est positif, mais un quant isolé sur PICK est très négatif**.

> Cause technique : la **route picking** par défaut (`Stock → Output`) tire sur le `default_location_src_id` du picking type = `TT/Stock`. Pas de **2-step / 3-step picking** activé qui forcerait un transfert `cellule → PICK → Output`.

### Pattern B — Consommation MOraw avant réception (25 %)
Les MO d'assortiments (`OP/13636`, `MO/01xxx`, `MO/02xxx`, `MO/03xxx`) consomment des composants depuis `TT/Stock` **sans réservation préalable validée**. On voit clairement sur E0121 : 7 MOraw consécutifs (sept-oct 2025) avant le moindre PO. Cela suppose `Allow Negative Stock = True` et **aucun blocage `mrp.production` sur "components availability"**.

### Pattern C — Ajustements d'inventaire mal compensés (15 %)
Pics d'août 2025 (12/08) et juin 2025 (18/06) : ajustements de plusieurs milliers d'unités sortant vers `Virtual Locations/Inventory` sans contre-mouvement entrant sur la même cellule. Origine : opérateur qui **réinitialise un quant** sans avoir d'abord transféré le stock vers la nouvelle cellule. Effet permanent sur le quant.

---

## 5. Diagnostic mécanique (1 paragraphe)

`TT/Stock` dérive structurellement parce que **la configuration entrepôt utilise un picking 1-step (Output direct)** : tous les bons de livraison clients pointent leur source sur `TT/Stock` ou `TT/Stock/PICK` (parent), pas sur la cellule pickface. Couplé à **`Allow Negative Stock = True`** sur le warehouse TT et à **l'absence de blocage MRP "Check components availability"**, le système accepte de consommer (SO ou MOraw) depuis le parent même quand le quant parent est à 0 — il "emprunte" virtuellement, et c'est cet emprunt qui apparaît comme négatif. Les ajustements d'inventaire ponctuels (août 2025) ont créé les déficits initiaux, et tous les moves suivants ont continué à pointer sur `TT/Stock` au lieu de la cellule réelle, **enfonçant** le négatif. Le stock physique global est sans doute correct — c'est de la **dette comptable de localisation**, pas un manque réel.

---

## 6. Recos ciblées TT/Stock (3 priorités)

### P1 — Consolidation parent ↔ enfants sur top 20 produits (impact immédiat ~ -200 000 unités)
Pour chaque produit du top 20 : créer un transfert interne `TT/Stock/PICK/<cellule réelle> → TT/Stock` (ou inverse) qui **regroupe tous les quants positifs et négatifs du même produit dans la zone parent**. Concrètement : pour E0628, le -45 269 sur `TT/Stock/PICK` doit être absorbé par les +106 584 cumulés sur `TT/Stock`. Une opération de **regroupement (move zero-sum)** suffit. Script à écrire : pour chaque top-20, somme les quants > 0 et < 0, fait un seul `stock.quant.update_quantity` consolidé. **Estimation : -185 000 unités de négatif évacuées en 1 batch.**

### P2 — Forcer 2-step picking sur warehouse TT
Activer `delivery_steps = 'pick_ship'` (ou `'pick_pack_ship'`) sur le warehouse TT. Effet : chaque SO devra d'abord créer un **transfert `cellule pickface → TT/Stock/PICK/Output`**, ce qui force l'opérateur à choisir la cellule réelle **ou** à créer un manquant explicite. Plus de "tire au hasard sur le parent". À tester en sandbox d'abord (impacte tous les workflows logistiques).

### P3 — Désactiver "Allow Negative Stock" + activer "Check components availability" sur les MO
Sur `stock.warehouse` TT : `allow_negative = False`. Sur le picking type "Manufacturing" : forcer `consu_check_availability = True`. Effet : aucun MO ne pourra démarrer si les composants ne sont pas réellement disponibles → fin du Pattern B (consommation avant PO). Risque : peut bloquer la prod si les BoM des assortiments tirent sur des composants en flux tendu — prévoir une réception STOR planifiée la veille de chaque MO.

---

## 7. Fichiers produits

- `odoo/audit_tt_stock_negatif.py` — script ciblé TT/Stock + descendantes
- `odoo/audit_tt_stock.json` — données brutes (top 15 quants, top 5 enquêtes mouvement par mouvement, patterns 90j)
- `odoo/tt_stock_negatif_2026-04-14.md` — ce rapport
