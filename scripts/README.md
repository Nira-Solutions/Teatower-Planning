# scripts/ — sources maîtres planning + agents Teatower

## `build_planning_pool.py` — pool maître merchandiser

Génère depuis Odoo (XML-RPC, lecture seule) la liste maître des magasins GMS à visiter, avec leurs métriques de planification.

**Source unique** :
- `sale.order` (state ∈ `sale`/`done`)
- `stock.picking` outgoing done
- `res.partner` (avec `comment` parsé pour les tags `[VISITE YYYY-MM-DD]` et `[ARRET …]`)

**Sorties** : `data/planning_pool_YYYY-MM-DD.{csv,md}`

### Règles de calcul

| Champ | Définition |
|---|---|
| `tier` | A si avg_mois ≥ 400 €, B si 100-400 €, C si 30-100 €, X si < 30 € |
| `cycle_days` | 21j (A), 28j (B), 42j (C), 90j (X) — override Tier B pour nouveau client < 90j depuis 1ʳᵉ SO |
| `statut` | `Arret` si `sale_warn=block` ET `comment` contient `[ARRET` ; sinon `Actif` |
| `last_visit` | `max(stock.picking done, [VISITE YYYY-MM-DD] dans comment, last_so_date)` |
| `last_visit_source` | `picking` / `comment_tag` / `last_so` (lequel a gagné) |
| `next_visit` | `last_visit + cycle_days` |
| `retard_j` | `(today − next_visit)` si dépassé, sinon 0 |
| **`last_so_date`** | **`max(date_order)` sur sale.order où `partner_id`/`partner_shipping_id`/`partner_invoice_id` = magasin (state sale/done). Source UNIQUE.** |
| **`last_so_days_ago`** | **`today − last_so_date` (jours)** |
| **`last_so_label`** | **`"JJ/MM/AAAA (Xj)"` ou `"Jamais commandé"`** |

### Règle Nicolas — 21/05/2026 : "dernière visite" = SO Odoo uniquement

Le champ `last_so_date` est la **source unique de vérité** pour afficher la "dernière visite client" dans le planning merchandiser :

- ✅ **Autorisé** : interroger `sale.order` via XML-RPC, prendre `max(date_order)`.
- ❌ **INTERDIT** : déduire la dernière visite des anciens fichiers planning du repo (`planning/*.md`, `planning/*.html`, `planning/queue_semaine_*.md`, `data/queue.json` archivés).
- **Raison** : un magasin inscrit dans une queue ou un planning précédent n'a pas forcément été visité (annulation, dépassement horaire, contact absent). La seule preuve d'un passage commercial = une commande confirmée.

Cette règle est permanente et s'applique à toutes les générations planning futures.

### Rendu HTML `planning/index.html`

Chaque visite affiche un badge `<span class="last-so last-so-*">` :

| Classe | Plage |
|---|---|
| `last-so-fresh` (vert) | < 30 j |
| `last-so-mid` (orange) | 30-60 j |
| `last-so-stale` (rouge) | > 60 j |
| `last-so-never` (gris) | Jamais commandé |
| `last-so-too-fresh` (orange foncé, alerte) | < 7 j → visite probablement trop rapprochée |

Une alerte explicite remonte à Nicolas si une visite est planifiée < 14 j après la dernière SO (Tier B/C).

### Usage

```bash
python scripts/build_planning_pool.py --target-date 2026-05-21
# → data/planning_pool_2026-05-21.csv + .md
```

## Autres scripts

- `queue.py` : file des tâches agents (start/done) + commit/push automatique.
- `*.py` à la racine `data/` : scripts ad-hoc (audit, vérif, build_brief, etc.) — non maintenus comme "sources".
