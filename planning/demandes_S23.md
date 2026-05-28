# Demandes / contraintes pour la prep S23 (2026-06-01 → 2026-06-05)

> Fichier alimenté au fil de la semaine S22 par Nicolas/Nira. À scanner **obligatoirement** au début de la génération de la queue S23 (en plus de `Displays Excel` archive, `planning_pool`, reports S22, et scan nouveaux clients/leads gagnés).

---

## Demandes nouvelles (à ajouter à la queue)

### Delhaize Embourg #2909 — VISITE (reportée de S22 → S23)

| Champ | Valeur |
|---|---|
| **Partner** | **#2909 — DelEmbourg SRL - Delhaize Embourg** |
| **Adresse** | Voie de l'Ardenne 57, **4053 Embourg** (Liège-est, Chaudfontaine) |
| **Tél** | 043 61 25 69 |
| **Email** | Kevin.Demarteau@affiliatesdelhaize.be |
| **Contact magasin** | **Kevin Demarteau** (merchandiser) |
| **Tier** | **A** — 16 SO confirmées / 12 mois, **7 854 € HT**, avg **654 €/mois** |
| **Dernière SO** | S05507 du **2026-04-30** — 435,41 € TTC (410,76 € HT) |
| **Écart au build S23** | ~32-36 j depuis dernière SO — cycle Tier A = 21 j → **OVERDUE ~11-15 j** |
| **Contraintes Odoo** | Aucune contrainte jour/horaire dans le `comment` (juste « demander Kevin Demarteau »). `sale_warn=no-message` (pas Arret). |
| **Géo / cluster** | **Axe Liège-est** — à grouper avec la boucle Liège : Fragnée #2965, Barchon #119815, Herve #120491, Fleron #7760, éventuellement Beyne/Chênée. Embourg s'insère entre Fragnée et Fleron (**+6 min de route nettes** seulement, OSRM). |
| **Source demande** | Nicolas — message 2026-05-27. Demandé d'abord pour S22 (jeu/ven) mais **impossible sans dépasser le cap 16:30** (jeu = mauvaise province BW ; ven = boucle Hesbaye/Namur saturée 7 stops, marge 15 min). Reporté S23. |

**Tag planning** : VISITE (30 min)
**Justification** : Tier A à 654 €/mois, OVERDUE sur cycle 21 j. À caler sur la boucle Liège (jour Liège de S23), pas un jour Brabant Wallon / Namur ouest.
**Note routage** : Baillonville → Embourg = ~47 min / 47 km (E25). Embourg est un détour quasi nul si la journée passe déjà par Fragnée/Fleron.

---

## 5 IMPLANTATIONS prioritaires S23 (demande Nicolas 2026-05-28)

À intégrer **obligatoirement** dans la queue S23. Sous-agent Planning doit identifier chaque partner Odoo (res.partner). Si absent du master Odoo, alerter Nicolas (NE PAS inventer ID).

1. **Intermarché Grâce-Hollogne** — IMPL (30 min) — zone Liège ouest
2. **Intermarché Mons** — IMPL (30 min) — zone Hainaut
3. **Intermarché Rumes** — IMPL (30 min) — zone Hainaut (Tournaisis)
4. **Delhaize Roodebeek** — IMPL (30 min) — zone Bruxelles
5. **Intermarché Braine-le-Château** — IMPL (30 min) — zone Brabant Wallon

**Clustering géo conseillé** :
- Mons + Rumes ensemble (jour Hainaut)
- Roodebeek + Braine-le-Château ensemble (jour BXL/BW) — Roodebeek mardi/mercredi de préférence (accès magasin Delhaize)
- Grâce-Hollogne sur le jour Liège (avec Embourg, Fragnée, Fleron, Herve, Barchon)

**Status partner** : possiblement nouveau client (lead Gagné <14j ou partner créé <14j → tag "À IMPLANTER" auto). Vérifier scan Odoo.
