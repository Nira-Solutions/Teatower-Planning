# Audit Stocks Négatifs Odoo Teatower

**Date** : 2026-04-14
**Périmètre** : `stock.quant.quantity < 0` sur toutes locations internes (`usage='internal'`)
**Source** : XML-RPC `tea-tree.odoo.com` / DB `tsc-be-tea-tree-main-18515272`

---

## 1. Vue d'ensemble

| Indicateur | Valeur |
|---|---|
| Nombre de quants négatifs | **397** |
| Produits concernés | **222** (sur ~500) |
| Locations internes concernées | **119** |
| Quantité totale négative | **-239 496 unités** |
| Valeur totale négative (coût std) | **-35 007 EUR** |

Ordre de grandeur : presque la moitié du catalogue présente au moins un quant négatif. La majorité de la masse négative est concentrée sur les **échantillons (codes E0xxx)** et sur **`TT/Stock`** + ses emplacements `PICK`.

---

## 2. Répartition par location (top négatives)

| Location | Nb quants | Qté négative |
|---|---:|---:|
| `TT/Stock` (entrepôt principal) | 111 | **-76 748** |
| `TT/Stock/PICK` (zone picking globale) | n quelques-uns | **-150 000+** (cumul des E0xxx) |
| `WAT/Stock` (Waterloo) | ~20 | -3 200 |
| `LIEGE/Stock` | ~15 | -1 700 |
| `NAM/Stock` | ~5 | -150 |
| `POP/Stock` | 12 | -63 |
| `GMS/Stock` | 1 | -2 |
| `TT/Entrée` | 5 | -3,5 |
| Emplacements `TT/Stock/PICK/A|B|C-..` (cellules rack) | ~150 | de -1 à -92 chacun |

Les **magasins** (WAT/LIEGE/NAM) n'ont que des négatifs faibles et ponctuels — symptôme classique de transferts internes et ventes magasin désalignés. Le gros de la dette stock est sur **TT (entrepôt principal)**.

---

## 3. Top 20 produits les plus négatifs

| # | Code | Produit | Qté nég. | Valeur EUR | Locs |
|---:|---|---|---:|---:|---:|
| 1 | E0628 | Oasis du désert BIO (Echantillon) | -45 269 | -7 243 | TT/Stock/PICK |
| 2 | E0279 | Le panier de grand maman (Ech.) | -25 074 | -4 012 | 3 locs PICK |
| 3 | E0121 | Lady Dodo (Ech.) | -23 205 | -3 945 | 2 locs PICK |
| 4 | E0666 | English Breakfast (Ech.) | -21 400 | 0 (coût=0) | 2 locs PICK |
| 5 | E0626 | Sencha BIO (Ech.) | -13 881 | -2 082 | TT/Stock/PICK |
| 6 | E0880 | Blue Earl Grey BIO (Ech.) | -13 760 | -2 614 | TT/Stock/PICK |
| 7 | E0301 | Tisane tropicale (Ech.) | -11 660 | -1 982 | TT/Stock |
| 8 | C0019 | Sachet Teatower Classique | -9 030 | 0 | TT/Stock |
| 9 | E0913 | Féérie d'Hivers (Ech.) | -6 888 | 0 | TT/Stock |
| 10 | E0732 | Gourmandise de Noël (Ech.) | -5 162 | -774 | TT/Stock |
| 11 | E0711 | Offrande des Rois Mages (Ech.) | -5 162 | -774 | TT/Stock |
| 12 | E0891 | Trésor des lutins (Ech.) | -5 162 | -878 | TT/Stock |
| 13 | VR0767 | Vrac remplissage Earl Grey | -3 727 | 0 | WAT+TT+LIEGE+NAM |
| 14 | E0600 | La lampe merveilleuse (Ech.) | -2 591 | -440 | TT+LIEGE |
| 15 | E0778 | Spéculoos & Cie (Ech.) | -2 590 | -440 | TT/Stock |
| 16 | E0845 | Mamy Granny BIO (Ech.) | -2 590 | -440 | TT/Stock |
| 17 | E0793 | Orangipane (Ech.) | -2 590 | -414 | TT/Stock |
| 18 | VR0666 | Vrac remplissage English Breakfast | -2 556 | 0 | WAT+TT+LIEGE |
| 19 | E0638 | Sérénité BIO (Ech.) | -2 398 | -408 | TT/Stock |
| 20 | E0205 | Etoiles filantes (Ech.) | -2 398 | -384 | TT/Stock |

Constat fort : **17 / 20 sont des échantillons (E0xxx)**. Ils représentent à eux seuls ~85 % de la masse négative.

---

## 4. Enquête sur les 5 plus gros (analyse `stock.move`)

### 4.1 E0628 Oasis du désert (Ech.) — -45 269

Pattern observé sur les moves récents :

- `2026-04-10 TT/MO/03924` → consommation MO **21 875** vers `Virtual Locations/Production` (BoM échantillon).
- `2026-04-01/02 TT/IN+STOR P00399` → réception PO **63 000**.
- `2026-03-24 S04979` → livraison client **20 000**.
- `2026-02-13 S04920` → livraison client **26 500**.
- Plusieurs MO `OP/13636` mensuelles consomment 90→500 unités.

**Cause probable** : l'échantillon E0628 est consommé comme **composant** d'un kit/BoM (MO `TT/MO/03924`, `OP/13636`) en très grosses quantités, mais la recette/BoM est probablement déclenchée **avant la réception physique** ou utilise une **route GMS Backflush** qui décompte sans contrôle de stock disponible. Les ordres de fabrication tirent sur `TT/Stock` directement, pas sur le PICK où les pièces sont rangées.

### 4.2 / 4.3 / 4.4 / 4.5 (E0279, E0121, E0666, E0626)

Même schéma : tous ces échantillons sont **consommés dans les MO `OP/13636`** (constructeur d'assortiments) et dans les grosses commandes `S04920` / `S04762` / `S03825`. Les MO `TT/MO/03309`, `03425`, `02910` consomment les composants depuis `TT/Stock` mais on voit aussi des `STOR` (mise en stock zone PICK) qui n'arrivent qu'**après** la consommation.

**Pattern dominant** : décalage temporel **MO/livraison avant STOR** + **double comptage** entre `TT/Stock` (parent) et `TT/Stock/PICK/<cellule>` (enfant) qui n'est pas ré-agrégé proprement.

---

## 5. Catégorisation des causes (top 3 patterns)

### Pattern 1 — Échantillons consommés en MO sans réception préalable (~85 % de la masse négative)
Les échantillons E0xxx (kits-cadeaux, assortiments saisonniers) sont consommés par des ordres de fabrication d'assortiments (`OP/13636`, `MO/03xxx`) qui tirent sur `TT/Stock` sans que la réception physique du fournisseur ait été validée à temps. Résultat : la MO décompte, le PO arrive 1-3 jours plus tard, le solde reste négatif sur la cellule où la MO a tiré.

### Pattern 2 — Désynchro `TT/Stock` (parent) ↔ `TT/Stock/PICK/<cellule>` (enfants)
Beaucoup de quants négatifs sur des cellules picking précises (`A-06-00-01-02`, `C-01-00-00-01`, etc.) pour de **petites quantités**. Ce sont des **picks réservés sur la cellule** alors que le stock physique est dans une autre cellule du même rack. Les opérateurs picking ne replacent pas, ou les transferts internes intra-warehouse `TT/Stock → TT/Stock/PICK` ne sont pas créés/validés.

### Pattern 3 — Magasins WAT/LIEGE/NAM : transferts internes pas validés ou ventes magasin avant réassort
Quelques produits VR (vrac remplissage Earl Grey, English Breakfast) montrent du négatif simultané sur les 3 magasins : c'est l'effet d'une **vente magasin enregistrée sans transfert interne `TT/Stock → WAT/Stock` validé**, OU d'une règle de réassort (orderpoint) qui crée le mouvement mais ne le valide pas. Conforme à la note `feedback_transferts_internes` (priority=1, MAJ règle).

---

## 6. Recommandations (à valider par Nicolas avant exécution)

| Priorité | Action | Cible | Détail |
|---|---|---|---|
| **P1** | Inventaire physique ciblé "échantillons" | E0xxx top 12 | -157 000 unités qui ne sont sans doute pas réelles, juste mal séquencées. Faire un comptage physique et `inventory.adjustment` (Quants → "Apply") pour remettre à zéro ou à la valeur réelle, puis bloquer. |
| **P1** | Bloquer la consommation MO sans stock disponible | BoM échantillons | Sur les routes des MO d'assortiments (`OP/13636`), activer `restrict_partner_id` et surtout dans `mrp` cocher **"Reserve before scheduled date"** + désactiver le backflush automatique. |
| **P2** | Audit `TT/Stock/PICK` cellule par cellule | Top 20 cellules négatives | Lancer un `stock.warehouse.orderpoint` interne PICK→PICK, ou faire un transfert de regroupement de tous les quants positifs/négatifs d'un même produit dans `TT/Stock/PICK` parent (consolidation). |
| **P2** | Forcer `Allow Negative Stock = False` sur l'entrepôt TT | `stock.warehouse` | Empêche les futures ventes/MO de tirer en dessous de zéro. À tester d'abord en sandbox car risque de blocage des opérations. |
| **P3** | Réconciliation magasins | WAT/LIEGE/NAM | Lister tous les transferts `TT/Stock → <MAG>/Stock` en état `assigned` (non validés) depuis 30 jours et les valider en lot. Vérifier que les ventes magasin pointent bien sur `<MAG>/Stock` et pas `TT/Stock`. |
| **P3** | Script de surveillance hebdomadaire | dashboard | Ajouter un widget dashboard "Quants négatifs" avec alerte Slack si >50 nouveaux par semaine. Réutiliser `odoo/audit_negative_stock.py`. |
| **P4** | Nettoyer les coûts standard à 0 | E0666, C0019, E0913, VR0xxx | Plusieurs produits ont `standard_price = 0` ce qui masque l'impact valorisé. Mettre un coût même indicatif. |

---

## 7. Fichiers produits

- `odoo/audit_negative_stock.py` — script XML-RPC réutilisable
- `odoo/audit_neg_stats.json` — stats globales + top 20 + répartition par location
- `odoo/audit_neg_invest.json` — détail des 5 enquêtes (15 derniers moves chacun)
- `odoo/audit_stocks_negatifs_2026-04-14.md` — ce rapport
