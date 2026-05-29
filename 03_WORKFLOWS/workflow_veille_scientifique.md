# Workflow — Veille Scientifique Bloom

**Version** : 1.0  
**Statut** : Actif  
**Responsable** : Agent_Veilleur_botanique  
**Mis à jour** : 2026-05-29

---

## Description

Ce workflow décrit le processus de veille scientifique continue sur les plantes de la bibliothèque Bloom by BotaniK, afin d'identifier les nouvelles publications, mettre à jour les niveaux de preuve et actualiser les fiches existantes.

---

## Objectifs

- Identifier les nouvelles études cliniques sur les 148 plantes sélectionnées
- Maintenir les niveaux de preuve à jour
- Détecter les nouvelles allégations EFSA validées ou rejetées
- Signaler les nouvelles alertes de sécurité (ANSM, EFSA)

---

## Fréquence

| Type de veille | Fréquence |
|---|---|
| Nouvelles publications PubMed | Mensuelle |
| Mises à jour EFSA | Trimestrielle |
| Alertes ANSM / EMA | Hebdomadaire |
| Mise à jour des fiches | Sur déclenchement |

---

## Étapes du workflow

### Étape 1 — Déclenchement
- [ ] Déclenchement automatique (calendrier) ou manuel (Agent_Maitre)
- [ ] Définition du périmètre : plante(s) cible(s) ou veille générale

### Étape 2 — Recherche documentaire (Agent_Veilleur_botanique)
**Bases à consulter :**
- [ ] PubMed / MEDLINE (requête : nom latin + indication)
- [ ] Cochrane Library (méta-analyses et revues systématiques)
- [ ] EFSA Journal (nouvelles opinions scientifiques)
- [ ] ANSM / EMA (alertes sécurité, monographies)
- [ ] Natural Medicines Database

**Filtres à appliquer :**
- Langues : EN, FR
- Limite de date : depuis la dernière veille
- Types d'études prioritaires : ECR, méta-analyses, revues systématiques
- Populations : humains adultes

### Étape 3 — Évaluation préliminaire (Agent_Veilleur_botanique)
- [ ] Lecture des abstracts
- [ ] Élimination des doublons et hors-sujet
- [ ] Cotation préliminaire de chaque étude : [Haute / Modérée / Faible qualité]
- [ ] Création des fichiers source : `PMID[XXXXX]_[NOM_PLANTE].md`

### Étape 4 — Analyse d'impact (Agent_Validateur_scientifique)
- [ ] Les nouvelles études modifient-elles le niveau de preuve existant ?
- [ ] Y a-t-il de nouveaux claims possibles ou des claims à retirer ?
- [ ] Y a-t-il de nouvelles alertes de sécurité ?
- [ ] Rapport d'impact transmis à l'Agent_Orchestrateur

### Étape 5 — Mise à jour (si impact détecté)
- [ ] Activation du workflow `workflow_fiche_plante.md` pour mise à jour
- [ ] Création d'une nouvelle version : `[NOM_PLANTE]_BLOOM_v[X+1].md`
- [ ] Archivage de la version précédente dans `02_LIBRARY/versions/`
- [ ] Mise à jour du `09_versioning_change_log.md`

### Étape 6 — Rapport de veille (Agent_Archiviste_editorial)
- [ ] Synthèse des publications analysées (nombre, type, impact)
- [ ] Liste des fiches mises à jour
- [ ] Liste des nouvelles alertes détectées
- [ ] Archivage du rapport dans `07_LOGS/`
- [ ] Transmission du rapport à l'Agent_Maitre

---

## Format du rapport de veille

```
RAPPORT DE VEILLE — Bloom by BotaniK
Date : [YYYY-MM-DD]
Période couverte : [du YYYY-MM-DD au YYYY-MM-DD]
Nombre de publications analysées : [N]
Nombre de publications retenues : [N]

Fiches mises à jour : [Liste]
Nouvelles alertes sécurité : [Liste ou Aucune]
Actions recommandées : [Liste]
```

---

## Fichiers concernés

- `02_LIBRARY/sources/` — Fichiers PMID sources
- `02_LIBRARY/plantes/` — Fiches plantes à mettre à jour
- `02_LIBRARY/versions/` — Archives des versions
- `07_LOGS/` — Rapports de veille archivés
- `00_MASTER/09_versioning_change_log.md` — Log global
