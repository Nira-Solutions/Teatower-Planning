# Modifications Planning Merchandiser — S21 (18-22/05/2026)

**Préparé** : 2026-05-15 (Nira) — **génération finale** : ce soir par Nicolas (autre PC)

---

## 1) AJOUT — Delhaize La Louvière (SO S05404) — **IMPLANTATION INITIALE**

| Champ | Valeur |
|---|---|
| **SO** | **S05404** — confirmé (`state=sale`) |
| **Date order** | 2026-04-20 |
| **Commercial** | Jérôme Carlier |
| **Partner (ship)** | **#123035 — Gmp La Louvière - Delhaize La Louvière** |
| **Adresse** | **Rue de la Franco-Belge 228, 7100 La Louvière** |
| **Téléphone** | **064 44 44 08** |
| **Email** | **chef44686@delhaize.be** |
| **Montant** | **515,66 € TTC** |
| **delivery_status** | marchandise **livrée 27/04 par transporteur seul** (sans pose Gilles) |
| **Comment Odoo** | "Client GMS 15/04/2026" (nouveau client) |
| **Lignes** | 10 réfs I0 (43,59 € chacune) + 2 réfs A0 (filtres) + V0914 (échantillon) + EM0072 (SRP) — **66 pièces I0/V0** |

**Tag planning** : **IMPLANTATION INITIALE** (jamais implanté, marchandise en attente sur place depuis 3 semaines)
**Budget temps sur place** : **1h** (pose SRP Kraft + montage 11 facings + étiquettes prix + photos avant/après)

**⚠️ Historique** : Marchandise livrée 27/04 par transporteur sans pose Gilles. Note Jérôme jamais transformée en task Gilles. Implantation initiale **différée de 3 semaines**, à faire **impérativement lundi 18/05**.

---

## 2) AJOUT — Intermarché Braine-le-Comte (même tournée)

| Champ | Valeur |
|---|---|
| **Partner** | **#123466 — Digretail - Intermarché Braine-le-Comte Digues** |
| **Adresse** | Rue des Digues 60, **7090 Braine-le-Comte** |
| **Téléphone** | +32 67 56 01 88 |
| **Email** | PDV09832@MOUSQUETAIRES.COM |
| **Contact** | **Mr Damien** (extrait du comment Odoo : "OK pour Gilles => Mr Damien") |
| **Dernière SO** | S05531 du 2026-05-05 — 562,81 € — **livrée le 05/05 par Gilles** (tournée précédente) |
| **sale_warn** | `warning` (à vérifier sur place) |

**Tag planning** : **VISITE** (sans réassort — last delivery 05/05 → 13 jours, pas besoin de réassort)
**Justification présence S21** : optimisation tournée La Louvière (proximité géo Braine-le-Comte ↔ La Louvière 25 km)
**Budget temps sur place** : 30 min

---

## 3) Trajet Google Maps (à valider par Nicolas dans la queue finale)

**Tournée recommandée** : lundi 18/05 ou mardi 19/05

| Segment | Distance estimée | Durée estimée |
|---|---|---|
| Baillonville → Intermarché Braine-le-Comte | ~105 km | ~1h15 |
| **Visite Braine-le-Comte** (sans réassort) | — | **0h30** |
| Intermarché Braine-le-Comte → Delhaize La Louvière | ~25 km | ~0h30 |
| **IMPLANTATION INITIALE La Louvière** (pose SRP + 11 facings + photos) | — | **1h00** |
| Delhaize La Louvière → Baillonville | ~100 km | ~1h10 |
| **TOTAL journée** | **~230 km** | **~4h25** |

**Départ recommandé** : **9h00** → arrivée Braine-le-Comte ~10h15, départ ~10h45, arrivée La Louvière ~11h15, fin implantation ~12h15, **retour Baillonville ~13h25**.
**Respect règle 16h30** : ✅ **OK très large** (marge ~3h05 pour 4-5 visites Tier B/C complémentaires sur le trajet retour si pertinent).

**Lien Google Maps à valider** :
https://www.google.com/maps/dir/Baillonville,+Belgium/Rue+des+Digues+60,+7090+Braine-le-Comte/Rue+de+la+Franco-Belge+228,+7100+La+Louvi%C3%A8re/Baillonville,+Belgium

---

## 4) Règle dure intégrée au script de génération

**Fichier** : `scripts/build_planning_pool.py`

**Modif** : ajout d'une fonction `display_name(store_name, billing_partner, parent_name, city, pid)` qui garantit **TOUJOURS** un nom de magasin lisible :
1. `store_name` nettoyé (strip prefix numérique `^\d{4,}` type ID Odoo)
2. fallback `billing_partner` (ex "SA Marer - AD Rochefort")
3. fallback `parent_name + ville` (ex "Delhaize Le Lion Bruxelles — sans nom propre")
4. ultime fallback `"Magasin #pid — ville — sans nom propre"`

**Impact détecté** sur planning_pool_2026-05-13.csv : **10 magasins avaient `store_name` vide** (apparaissaient sous forme `#7693 ` dans les briefs). Désormais ils s'afficheront avec leur billing_partner (ex `SA Marer - AD Rochefort (#7693)`).

**Aucun cas trouvé** de prefix numérique dans store_name actuel, mais la garde est en place pour prévention.

Le markdown du planning_pool affiche désormais : `{display_name} (#{pid})` au lieu de `#{pid} {store_name}`.

---

## Ce qu'il reste à faire CE SOIR (Nicolas, autre PC)

1. **Pull** repo Teatower master (modif script + cette note)
2. **Lancer** `python scripts/build_planning_pool.py` pour régénérer le pool
3. **Scanner** Displays Excel (règle obligatoire) + reports SO + cette note
4. **Inclure manuellement** dans la queue S21 :
   - **Lundi 18 ou mardi 19/05** : tournée **Braine-le-Comte (visite) + La Louvière (implantation S05404)**
   - Compléter avec 2-3 visites Tier B/C overdue sur le trajet (ex Carrefour Market Braine-l'Alleud #8339)
5. **Générer queue + brief Gilles** comme d'habitude (dashboard, exports HTML/MD)
6. **Push** → planning visible sur https://nira-solutions.github.io/Teatower-Planning/planning/
