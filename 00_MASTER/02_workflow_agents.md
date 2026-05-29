# 02 — Workflow des Agents

## Vue d'ensemble du flux

```
[Trigger] → Agent Veilleur → Agent Validateur → Agent Archiviste → [Agent Maître] → [Output]
```

## Étapes détaillées

### Étape 1 : Collecte (Agent Veilleur Botanique)
- Surveille PubMed, Cochrane, Google Scholar, bases ethnobotaniques
- Identifie nouvelles études pertinentes
- Extrait données brutes et les structure selon `01_schema_fiche_plante.md`
- Signale au Validateur via `03_protocol_communication.md`

### Étape 2 : Validation (Agent Validateur Scientifique)
- Analyse la qualité méthodologique des études
- Évalue le niveau d'évidence (I à V)
- Vérifie la cohérence avec les données existantes
- Approve ou rejette avec justification

### Étape 3 : Production (Agent Archiviste Éditorial)
- Transforme les données validées en contenu publiable
- Génère fiches plantes, articles, posts réseaux sociaux
- Respecte la politique de claims (`05_politique_preuves_et_claims.md`)
- Archive dans `05_PRODUCTION/`

### Étape 4 : Orchestration (Agent Maître)
- Supervise le pipeline complet
- Gère les conflits et exceptions
- Décide de l'escalade vers l'humain
- Valide les outputs finaux

## Triggers de workflow

| Trigger | Agent initialisé | Fréquence |
|---------|-----------------|----------|
| Nouvelle étude PubMed | Veilleur | Quotidien |
| Mise à jour fiche plante | Validateur | Selon besoin |
| Demande de contenu | Archiviste | Sur demande |
| Review qualité | Maître | Mensuel |

## Niveaux d'évidence (Grille Bloom)

| Niveau | Description | Action |
|--------|-------------|--------|
| I | Méta-analyse / RCT de qualité | Claim fort autorisé |
| II | RCT unique | Claim modéré |
| III | Étude observationnelle | Claim prudent |
| IV | Consensus expert | Mention usage traditionnel |
| V | In vitro / animal | Aucun claim humain |

---
*Version 1.0 — 2026-05-29*
