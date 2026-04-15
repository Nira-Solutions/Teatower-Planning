# Compte rendu CRM Teatower — 2026-04-15

> Lecture seule. Aucune écriture CRM effectuée.

---

## 1. Photo globale du CRM

| Métrique | Valeur |
|---|---|
| Total enregistrements (leads + opps) | **914** |
| dont type `lead` (non qualifiés) | 297 |
| dont type `opportunity` (qualifiées) | 617 |
| Responsable dominant | Jérôme Carlier (904 / 914 = 99 %) |
| Avec activité planifiée | 70 (8 %) |
| Sans activité planifiée | 844 (92 %) |

---

## 2. Répartition par stage

| Stage | Nom | Total | Leads | Opps | Age moy. opps |
|---|---|---|---|---|---|
| 5 | **Nouveaux leads** | 520 | 297 | 223 | 218 j |
| 1 | **Nouveaux Prospects** | 29 | 0 | 29 | 208 j |
| 2 | Prospects Contactés | 20 | 0 | 20 | 222 j |
| 3 | Propal Envoyée | 47 | 0 | 47 | 216 j |
| 4 | Gagné | 275 | 0 | 275 | 152 j |
| 6 | Perdu | 2 | 0 | 2 | 158 j |
| 7 | Prospect dormant...?? | 21 | 0 | 21 | 215 j |

**Colonnes d'entrée ("Nouveaux leads") : stages 5 + 1 = 549 enregistrements non avancés.**

Remarque : les 297 leads de type `lead` (stage 5) ont tous été créés le **2026-04-14** — c'est l'import GMS Wallonie réalisé hier. Les 223 opportunités du même stage ont une ancienneté moyenne de 218 jours (import ou leads qualifiés bloqués depuis ~7 mois).

---

## 3. Répartition par responsable

| Utilisateur | Total | Leads | Opps |
|---|---|---|---|
| **Jérôme Carlier** (id=12) | 904 | 297 | 607 |
| Nicolas Raes (id=6) | 7 | 0 | 7 |
| Stephan Pire (id=15) | 2 | 0 | 2 |
| logistique@noenature.com (id=10) | 1 | 0 | 1 |

Jérôme porte **99 % du portefeuille CRM** à lui seul.

---

## 4. Répartition par tag

| Tag | Leads/Opps |
|---|---|
| GMS | 780 |
| Horeca | 71 |
| Revendeur | 34 |
| Grossiste | 9 |
| Horeca Vrac et infu | 7 |
| Institution | 5 |
| Sans tag | 19 |
| Autres tags (Bongo, Influenceuse, Noel 2025, etc.) | 0 |

Le CRM est **dominé à 85 % par le segment GMS** (grandes et moyennes surfaces).

---

## 5. Ancienneté des leads

- **297 leads type `lead`** : tous créés le 2026-04-14 (import GMS hier) → 0 jour d'ancienneté réelle à traiter.
- **617 opportunités** : ancienneté moyenne **188 jours** (environ 6 mois).
- Opportunités dans les stages d'entrée (5 + 1) : ancienneté moy. **~215 jours** — signal d'alerte : ces fiches stagnent depuis 7 mois sans progression.

---

## 6. Activités planifiées — zoom Jérôme

| Catégorie | Nb |
|---|---|
| Activités planifiées (Jérôme) | 66 |
| dont en retard (deadline < 2026-04-15) | ~34 |
| dont à venir (deadline >= 2026-04-15) | ~32 |
| Leads/opps Jérôme **sans** activité | 838 |

Les 66 activités couvrent seulement 7 % du portefeuille de Jérôme. 34 activités sont déjà en retard (dating de octobre 2025 à avril 2026).

---

## 7. Charge de travail Jérôme — Colonnes d'entrée

### Périmètre : stages 5 (Nouveaux leads) + 1 (Nouveaux Prospects) assignés à Jérôme

| Segment | Nb |
|---|---|
| Leads type `lead` (stage 5) | 297 |
| Opportunités stage 5 (Nouveaux leads) | 219 |
| Opportunités stage 1 (Nouveaux Prospects) | 29 |
| **Total à qualifier / traiter** | **545** |

### Hypothèse de traitement

- **15 min/fiche** en moyenne : appel de qualification (ou décision no-call), enrichissement fiche, planification activité suivante ou disqualification.
- Cette heuristique est valide pour des leads GMS structurés (nom magasin + adresse connu) — le travail est surtout de prendre contact, pas de recherche.

### Calcul de charge

| Paramètre | Valeur |
|---|---|
| Nombre de fiches à traiter | 545 |
| Temps unitaire | 15 min |
| **Charge totale** | **8 175 min = 136 h** |

### Temps disponible de Jérôme

Agenda 4 prochaines semaines (2026-04-15 → 2026-05-13) :
- 6 RDV terrain bookés (visites magasins + implantation S05382 Spar Namur mardi 2026-04-21)
- Total RDV : **6 h bookées** sur la période

Estimation temps dispo CRM (qualification leads) :
- Semaine = 40 h théoriques
- Temps terrain + admin + suivi commandes : ~30 h/semaine estimés
- **Temps réaliste dédié qualification leads : ~10 h/semaine** (2 h/jour sur 5 jours)
- Marge d'erreur : si tournées s'intensifient (implantations GMS), descendre à 6-8 h/semaine.

### Résultat

| Scénario | h/semaine CRM | Semaines | Date fin estimée |
|---|---|---|---|
| Optimiste (10 h/sem) | 10 | 13,6 | **2026-07-19** |
| Réaliste (8 h/sem) | 8 | 17 | **2026-08-16** |
| Serré (6 h/sem) | 6 | 22,7 | **2026-09-23** |

**Scénario de référence : 13-14 semaines à 10 h/semaine CRM → fin estimée mi-juillet 2026.**

---

## 8. Recommandations

### Alerte priorité 1 — Le backlog est déjà trop long
545 fiches d'entrée pour 1 commercial = environ 3,5 mois de qualification au rythme actuel. En attendant, les opportunités stagnent depuis 7 mois (age moy. 215 jours). Le taux d'activité est de 7 % seulement.

### Actions recommandées (à valider avec Nicolas)

1. **Prioriser par tag + potentiel CA** : traiter d'abord les Horeca (71) et GMS "chauds" (visites terrain planifiées) avant d'attaquer les 297 leads GMS de l'import d'hier. Ratio effort/CA probablement meilleur sur Horeca.

2. **Disqualification rapide en batch** : les 223 opportunités stage 5 vieilles de 215 jours pourraient avoir une règle de disqualification automatique si aucune activité créée depuis 90 jours. Proposition : les passer en "Prospect dormant" en lot, libérer le backlog de ~40 %.

3. **Cadence hebdo minimum** : créer une activité To-Do ou Call sur au moins 20 nouvelles fiches/semaine pour maintenir la progression sans saturer Jérôme.

4. **Délégation partielle** : les 297 leads GMS Wallonie (import batch du 2026-04-14) sont structurés et géolocalisés. Aurélie (Support Ventes) pourrait prendre en charge la qualification téléphonique de 50-100 d'entre eux sur la base du Playbook Support Ventes — à valider.

5. **Nettoyage tags** : les tags "GMS" (id=1) et "Gms" (id=8) coexistent — doublon à fusionner. Idem pour "Horeca" et "horeca Vrac et infu".

---

*Rapport généré le 2026-04-15 — lecture seule Odoo XML-RPC — Sales-CRM agent Teatower*
