# Demandes / contraintes pour la prep S24 (2026-06-08 → 2026-06-12)

> Fichier alimenté au fil de la semaine S23 par Nicolas/Nira. À scanner **obligatoirement** au début de la génération de la queue S24 (en plus de `Displays Excel` archive, `planning_pool`, reports S23, et scan nouveaux clients/leads gagnés).

---

## Reports S23 → S24 (à intégrer obligatoirement)

### 5 magasins retirés mardi 02/06 v4 (doublons vendredi 29/05 S22)

Audit doublons 28/05 nuit : 5 magasins planifiés à la fois vendredi 29/05 (S22 — à exécuter par Gilles) ET mardi 02/06 v3 (S23) = revisites 3-7j, violation règle 14-21j espacement. Retirés mardi 02/06 v4 → à reprogrammer S24 (Tier B prioritaires sur la queue Namur/Hesbaye).

| Partner | Tier | OVERDUE @28/05 | avg/mois | Adresse | Contact magasin | Source |
|---|---|---|---|---|---|---|
| **#114704 — Delhaize Salzinnes** (Affilié 048652) | B | 51j | 258€ | Chaussée de Charleroi 22, 5000 Namur | Mme Wivine ou Manu — tel 081 40 80 40 — nicolas@adsalzinnes.be | Refonte mardi v4 |
| **#114681 — Delhaize de Bouge** (Affilié 041345) | B | 9j | 280€ | Chaussée de Louvain 336, 5004 Namur (Bouge) | Mme Destrée / Grandjean / Augustaine — tel 081 21 48 88 — helene.nols@affiliatesdelhaize.be | Refonte mardi v4 |
| **#3297 — Intermarché Bouge** (Windmill SA) | B | 9j | 242€ | Chaussée de Louvain 257, 5000 Bouge | Dany Decoster — tel 081 56 93 46 — pdv09883@mousquetaires.com | Refonte mardi v4 |
| **#3210 — Intermarché Faimes** (SA Faimine) | B | 15j | 219€ | Rue De Huy 27, 4317 Faimes | Accueil épicerie — tel 019 67 83 78 — PDV06089@mousquetaires.com | Refonte mardi v4 |
| **#2958 — Intermarché Floriffoux** (Floridis SA) | B | 10j | 290€ | Rue Emerée 4, 5150 Floriffoux | Loredana / Manon sur place — tel 081 44 05 39 — PDV09900@mousquetaires.com | Refonte mardi v4 |

**Cluster S24 conseillé** : Salzinnes + Delhaize Bouge + ITM Bouge = boucle Namur centre (5 min entre tous) — à grouper sur un jour Namur. Floriffoux + Faimes = axe N4/E42 Hesbaye sud — à grouper. Au build S24, viser 1 journée dédiée Namur/Hesbaye (5 magasins en une boucle) ou répartir sur 2 jours selon densité OVERDUE pool maître au 04/06.

**Justification** : tous Tier B avg 219-290€/mois. Au build S24 (08/06), seront 13-15j post-visite 29/05 → cycle 14-21j parfait, replanification idéale.

---

### ITM Genappe #2963 — VISITE (reportée de S23 v2 → S24)

| Champ | Valeur |
|---|---|
| **Partner** | **#2963 — GENADIS - Intermarché Genappe** |
| **Adresse** | Rue Louis Lalieux 22, **1470 Genappe** (Brabant Wallon) |
| **Tél** | 067 78 02 50 |
| **Email** | pdv09846@mousquetaires.com |
| **Contact magasin** | accueil épicerie (à demander sur place) |
| **Tier** | **B** — avg ~112 €/mois |
| **Dernière SO** | S05433 du **2026-03-25** — au build S23, 36j OVERDUE sur cycle 28j |
| **Dernière visite Gilles** | **jeudi 28/05/2026 (S22)** — boucle BW serrée |
| **Motif report** | Retiré de S23 v2 (jeudi 04/06) car 7j d'écart vs visite S22 → règle 14-21j Tier B non respectée. |
| **Cluster S24** | Boucle BXL/BW — à grouper avec d'autres magasins Brabant wallon (Wavre, Bierges, Ottignies, Sombreffe, etc.) selon dispos et OVERDUE pool maître au moment du build S24. |
| **Source demande** | Nicolas — validation ajustement S23 v2 le 2026-05-28. |

**Tag planning** : VISITE (30 min)
**Justification** : Tier B 36j OVERDUE déjà au build S23 — au build S24, sera ~43j OVERDUE → priorité haute sur la queue Brabant wallon S24.

---

## Demandes nouvelles (à ajouter à la queue S24)

### Demandes Nicolas du 03/06 (build S24 v1)

- **🚚 LIVRAISON HC Jambes #9046** (lundi 08/06) — **EN ATTENTE**. Nicolas : « tu verras plus tard, je te ré-interrogerai **jeudi 04/06** car il y a des **implantations à rajouter** dans le planning ». → Au point jeudi : (1) contenu/SO de la livraison Jambes à créer, (2) nouvelles implantations à intégrer (partners + SO + jours). Slot Jambes déjà posé lundi 1ᵉ stop (Hyper matin) dans S24 v1.
- **📦 Spar Namur #122958 — nouveau display x8** (lundi 08/06) — ✅ intégré S24 v1 (implantation).
- **📍 Delhaize Ottignies #3016** (vendredi 12/06) — ✅ slot posé S24 v1 (Tier A, pas jeudi/Galletas). **Nicolas se renseigne** sur l'objet exact (livraison SO S05664 du 28/05 non livrée, ou visite réassort) → à confirmer.

### À traiter jeudi 04/06 (re-interrogation Nicolas) — ✅ TRAITÉ (v2 build 04/06)

- ✅ **4 implantations intégrées v2** (demande Nicolas 04/06) :
  - **Delhaize Tubize #124182** (SO S05712, 738 €) → **mardi 09/06** (contrainte Odoo « pas le vendredi » ; ouvert mardi 08-20h vérif Google)
  - **Delhaize Amay #124178** (SO S05710, 342 €) → **jeudi 11/06** (axe retour Hesbaye→Huy)
  - **Proxy Delhaize Tihange #124180** (SO S05711, 342 €) → **jeudi 11/06** (enchaîné après Amay)
  - **Spar Beauvechain #124148** (SO S05703, 369 €) → **vendredi 12/06** 1ᵉ stop (⚠ fermé le mardi — vérif Google)
  - Les 4 SO livrées + facturées Peppol le 04/06. Fiches Odoo corrigées (email Amay, ville Tubize, note Tihange).
- ✅ **NOUVELLE RÈGLE HORAIRE DURE (Nicolas 04/06)** : journée Gilles = 8h travail + 30 min pause = **08:30 → 17:00, JAMAIS dépassé** (remplace cap 16h45). Tous les jours S24 recalés (départ 08:30, pause 30 min).
- ✅ **REPORT ITM Tilff #116869 (Tier A)** : passage jeudi 04/06 (S23) **non effectué** (signalé par Nicolas 04/06) → replanifié **jeudi 11/06** fin de boucle (Tihange → Tilff via E25 ; contrainte « Christine OK jeudi, pas vendredi » respectée).
- ⏳ Finaliser commande/livraison HC Jambes (toujours en attente — SO à créer avant lundi 08/06 matin).

---

## Alertes / actions Nicolas en attente

- **ITM Braine-le-Château** : si conversion lead CRM #233 + SO IMPL pas finalisée avant lundi 01/06, l'IMPL S23 (placeholder jeudi 04/06) ne peut pas être livrée → reporter en IMPL S24.
- **AD Delhaize Filature #5443** : retiré du jeudi S23 v2 (proxy zone Braine-le-Château plus pertinent maintenant que la vraie IMPL est planifiée). À reprendre dans une boucle BW S24/S25 (Tier C, 22j OVERDUE au build S23).
- **Walcourt #9016** : reporté depuis S21 (Jérôme à statuer relance commerciale avant revisite).
