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

1. **Intermarché Grâce-Hollogne** — IMPL (30 min) — zone Liège ouest ✓ intégré lundi 01/06 (partner #123900, SO S05636)
2. **Intermarché Mons** — IMPL (30 min) — zone Hainaut ✓ intégré mercredi 03/06 (partner #123966, SO S05644)
3. **Intermarché Rumes** — IMPL (30 min) — zone Hainaut (Tournaisis) ✓ intégré mercredi 03/06 (partner #123964, SO S05643)
4. **Delhaize Roodebeek** — IMPL (30 min) — zone Bruxelles ✓ intégré jeudi 04/06 (partner #123997, SO S05652)
5. **Intermarché Braine-le-Château** — IMPL (30 min) — zone Brabant Wallon ✓ **v2 28/05 : intégré jeudi 04/06 en PLACEHOLDER** (partner #TBD-233 / SO S05XXX) — **Nicolas finalise conversion lead CRM #233 + création SO avant lundi 01/06**.

**Clustering géo conseillé** :
- Mons + Rumes ensemble (jour Hainaut) ✓
- Roodebeek + Braine-le-Château ensemble (jour BXL/BW) — Roodebeek mardi/mercredi de préférence (accès magasin Delhaize) ✓ v2 : Roodebeek + Nivelles + Braine-le-Château IMPL + Tilff (jeudi 04/06)
- Grâce-Hollogne sur le jour Liège (avec Embourg, Fragnée, Fleron, Herve, Barchon) ✓

**Status partner** : possiblement nouveau client (lead Gagné <14j ou partner créé <14j → tag "À IMPLANTER" auto). Vérifier scan Odoo.

---

## Ajustements v5 (2026-05-29)

### Delhaize Ath #123144 — VISITE réassort thés glacés (mercredi 03/06)

- **Partner** : #123144 — Affilié 040490 - Delhaize Ath, Rue de l'Abbaye 6, 7800 Ath
- **Tier** : B — implantation initiale 22/04/2026 (SO S05437, 520,80 € TTC : 7 SKU GI0xxx × 12 unités + V0914 + Display M0005)
- **Cadence appliquée** : standard Tier B (~28-30j), pas de délai custom — next-visit 20/05 mais glissé hors queue S21. Au 03/06 = 42j depuis IMPL → **OVERDUE 12j**.
- **Source demande** : Nicolas 2026-05-29 — info terrain « énormément de thés glacés à remettre ».
- **Insertion v5** : mercredi 03/06 entre HC Mons Grands Prés et ITM Rumes (11:07-11:32, 25 min sur place). +30 min route HC Mons → Ath via N56/E429, +35 min Ath → Rumes via N7/R56/E42.
- **Décision Gerpinnes** : maintenu (option A confirmée Nicolas) — retour Baillonville 16:28 (marge 17 min sur cap 16h45 relevé même jour).
- **Brief** : check rotation SKU par SKU (GI0820 / GI0735 / GI0634 / GI0832 / GI0916 / GI0912 + V0914), photos avant/après, prise commande sur place si rupture sévère, noter contact responsable rayon (info manquante depuis IMPL).

---

## Ajustements v2 (2026-05-28, après publication v1)

### Retrait ITM Genappe jeudi 04/06 → reporté S24

- **Partner** : #2963 — GENADIS - Intermarché Genappe
- **Motif** : visite Gilles **jeudi 28/05 S22** → 7j d'écart avec planif jeudi 04/06 v1, **règle 14-21j Tier B non respectée**.
- **Action** : retiré du jeudi 04/06 v2, **reporté S24** (voir `demandes_S24.md`). Priorité haute (Tier B, 36j OVERDUE déjà au moment v1).

### Ajout ITM Braine-le-Château jeudi 04/06 (IMPL placeholder)

- **Lead CRM** : #233 "Intermarché Braine Le Château" — stage Gagné depuis 29/08/2025, **jamais converti en partner**.
- **Placeholder** : partner #TBD-233 / SO S05XXX / montant ~323 € (cohérent avec autres IMPL ITM S23 à 323,41 € TTC).
- **Action Nicolas avant lundi 01/06 matin** : convertir lead → res.partner, créer SO IMPL réelle, patcher le bloc jeudi (ID partner + n° SO + adresse précise + tel/mail merch).
- **Tag** : IMPLANTATION (30 min sur place).
- **Conséquence** : AD Filature #5443 (qui était proxy zone jeudi v1) **retiré du jeudi v2** — n'a plus de raison d'être maintenant que la vraie IMPL est planifiée. À reprendre dans une boucle BW future.
