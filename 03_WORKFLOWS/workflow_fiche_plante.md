# Workflow — Création d'une Fiche Plante Bloom

**Version** : 1.0  
**Statut** : Actif  
**Responsable** : Agent_Maitre  
**Mis à jour** : 2026-05-29

---

## Description

Ce workflow décrit le processus complet de création, validation et archivage d'une fiche plante dans le système multi-agents Bloom by BotaniK.

---

## Étapes du workflow

### Étape 1 — Initiation (Agent_Maitre)
- [ ] Réception de la demande de fiche (nouvelle plante ou mise à jour)
- [ ] Vérification que la plante figure dans `04_bibliotheque_148_plantes.md`
- [ ] Émission d'un Briefing BRF-YYYYMMDD-NNN à l'Agent_Orchestrateur
- [ ] Priorité assignée : [CRITIQUE / HAUTE / NORMALE / BASSE]

### Étape 2 — Orchestration (Agent_Orchestrateur)
- [ ] Réception du briefing
- [ ] Attribution de la mission à l'Agent_Veilleur_botanique
- [ ] Définition des critères de recherche et livrables attendus
- [ ] Ouverture d'un rapport de suivi

### Étape 3 — Recherche et collecte (Agent_Veilleur_botanique)
- [ ] Consultation des bases : PubMed, Cochrane, EFSA Journal, Natural Medicines
- [ ] Identification des études cliniques pertinentes (ECR en priorité)
- [ ] Extraction des PMID, années, populations, dosages, résultats
- [ ] Création des fichiers sources : `PMID[XXXXX]_[NOM_PLANTE].md` dans `02_LIBRARY/sources/`
- [ ] Niveau de preuve provisoire assigné : [I / II / III / IV / V]
- [ ] Rapport de veille transmis à l'Agent_Orchestrateur

### Étape 4 — Validation scientifique (Agent_Validateur_scientifique)
- [ ] Réception du rapport de veille
- [ ] Vérification de la qualité méthodologique des études
- [ ] Validation ou correction du niveau de preuve
- [ ] Analyse des claims possibles vs réglement CE 1924/2006 / EFSA / ANSM
- [ ] Attribution du statut par claim : VERT / ORANGE / ROUGE
- [ ] Rapport de validation transmis à l'Agent_Orchestrateur

### Étape 5 — Compilation de la fiche (Agent_Veilleur_botanique)
- [ ] Copie du template `06_TEMPLATES/plant_schema_template.md`
- [ ] Renommage : `[NOM_PLANTE]_BLOOM_v1.md`
- [ ] Remplissage de toutes les sections selon les données validées
- [ ] Dépôt dans `02_LIBRARY/plantes/`
- [ ] Notification à l'Agent_Orchestrateur

### Étape 6 — Validation finale (Agent_Maitre)
- [ ] Révision de la fiche complète
- [ ] Vérification de la conformité réglementaire globale
- [ ] Décision : VALIDÉ / À CORRIGER / REJETÉ
- [ ] Mise à jour du statut dans la fiche : `VALIDÉ`

### Étape 7 — Archivage (Agent_Archiviste_editorial)
- [ ] Réception de la fiche validée
- [ ] Mise à jour de l'index dans `02_LIBRARY/`
- [ ] Archivage dans `02_LIBRARY/versions/` si mise à jour
- [ ] Mise à jour du `09_versioning_change_log.md`
- [ ] Confirmation d'archivage à l'Agent_Maitre

---

## Critères de qualité

| Critère | Requis |
|---|---|
| Toutes les sections du template remplies | Oui |
| Au moins 3 études cliniques référencées | Recommandé |
| Niveau de preuve validé par Agent_Validateur | Obligatoire |
| Claims classés VERT/ORANGE/ROUGE | Obligatoire |
| Sources PMID créées dans `02_LIBRARY/sources/` | Obligatoire |
| Nommage conforme `[NOM_PLANTE]_BLOOM_v1.md` | Obligatoire |

---

## Durée estimée

- Recherche : 2–4h
- Validation : 1–2h
- Compilation : 1h
- **Total** : 4–7h par fiche

---

## Fichiers concernés

- `06_TEMPLATES/plant_schema_template.md` — Template source
- `02_LIBRARY/plantes/` — Dépôt des fiches finales
- `02_LIBRARY/sources/` — Sources PMID
- `02_LIBRARY/versions/` — Archives des versions précédentes
- `00_MASTER/09_versioning_change_log.md` — Log des modifications
