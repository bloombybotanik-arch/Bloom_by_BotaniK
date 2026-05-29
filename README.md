# Bloom by BotaniK

> Système de connaissance vivant autour des plantes

## Vision

Bloom by BotaniK est organisé comme un **système de connaissance vivant** autour des plantes. L'objectif est de structurer le savoir, vérifier les preuves, suivre les évolutions scientifiques et transformer cette matière en contenu, en produits et en décisions cohérentes.

Notre vision est de reconstruire un savoir utile sur les plantes, en reliant :
- l'humain,
- la nature,
- et la machine intelligente.

## Architecture du dépôt

```
Bloom_by_BotaniK/
├── AGENT.md                          # Instructions pour les agents IA
├── README.md                         # Ce fichier
├── .env.example                      # Variables d'environnement (template)
├── .gitignore
├── 00_MASTER/                        # Référence centrale et doctrine
│   ├── Bloom_by_BotaniK_Master_Reference.md
│   ├── 00_vision_why_bloom.md
│   ├── 01_schema_fiche_plante.md
│   ├── 02_workflow_agents.md
│   ├── 03_protocol_communication.md
│   ├── 04_bibliotheque_148_plantes.md
│   ├── 05_politique_preuves_et_claims.md
│   ├── 06_protocole_reset_homeostatique.md
│   ├── 07_synergies_bioavailability.md
│   ├── 08_exemples_cycles.md
│   └── 09_versioning_change_log.md
├── 01_AGENTS/                        # Définition des agents IA
│   ├── Agent_maitre.md
│   ├── Agent_Veilleur_botanique.md
│   ├── Agent_Validateur_scientifique.md
│   ├── Agent_Archiviste_editorial_Bloom.md
│   └── prompts/
│       ├── master_prompt_maitre.md
│       ├── master_prompt_veilleur.md
│       ├── master_prompt_validateur.md
│       └── master_prompt_archiviste.md
├── 02_LIBRARY/                       # Bibliothèque des plantes
│   ├── plant_schema_template.md
│   ├── plants/
│   ├── sources/
│   └── versions/
│       ├── changelog.md
│       └── archived/
├── 03_WORKFLOWS/                     # Processus et automatisations
├── 04_EVIDENCE/                      # Base de preuves scientifiques
├── 05_PRODUCTION/                    # Contenus prêts à publier
├── 06_TEMPLATES/                     # Templates réutilisables
├── 07_LOGS/                          # Journaux et traces
├── 08_ARCHIVE/                       # Archives
└── 09_TESTS/                         # Tests et validation
```

## Convention bilingue

- **Anglais** : structure technique (noms de dossiers, identifiants, clés)
- **Français** : contenu métier et documentation (README, doctrine Bloom, fiches plantes)

## Équipe agents

| Agent | Rôle |
|-------|------|
| Agent Maître | Coordination générale, orchestration |
| Agent Veilleur Botanique | Veille scientifique et mise à jour des données plantes |
| Agent Validateur Scientifique | Validation des claims et des preuves |
| Agent Archiviste Éditorial | Production et archivage du contenu |

---

*Bloom by BotaniK — Reconstruire le savoir utile sur les plantes.*
