# 09 — Versioning & Change Log

> Journal des modifications du système Bloom by BotaniK.

## Convention de versioning

Bloom by BotaniK utilise la convention **SemVer** (Semantic Versioning) :

```
VERSION = MAJOR.MINOR.PATCH

MAJOR : Changement de doctrine ou restructuration complète
MINOR : Ajout de nouvelles plantes ou modules
PATCH : Corrections, mises à jour scientifiques, typos
```

## Types de changements

| Tag | Description |
|-----|-------------|
| `[ADDED]` | Nouvelle plante, fonctionnalité ou section |
| `[UPDATED]` | Mise à jour de données existantes |
| `[FIXED]` | Correction d'une erreur |
| `[REMOVED]` | Suppression d'un élément |
| `[DEPRECATED]` | Élément maintenu mais obsolète |
| `[SECURITY]` | Mise à jour sécurité ou conformité |

## Change Log

---

### [1.0.0] - 2026-05-29

#### [ADDED]
- Création initiale du dépôt Bloom by BotaniK
- Structure complète avec 9 dossiers principaux
- `00_MASTER/` : 10 fichiers de référence
- `01_AGENTS/` : 4 agents + 4 prompts
- `02_LIBRARY/` : template de fiche plante
- Bibliothèque initiale de 148 plantes (liste)
- README.md avec architecture complète
- AGENT.md avec instructions pour les agents IA

#### [ADDED] Agents IA
- Agent Maître (orchestration)
- Agent Veilleur Botanique (veille)
- Agent Validateur Scientifique (validation)
- Agent Archiviste Éditorial (production)

---

### Prochaines versions planifiées

#### [1.1.0] - Prévue T3 2026
- [ ] 10 premières fiches plantes complètes
- [ ] Workflow GitHub Actions pour veille automatique
- [ ] Intégration PubMed API

#### [1.2.0] - Prévue T4 2026
- [ ] 50 fiches plantes
- [ ] Base de données synergies complète
- [ ] Dashboard de suivi

#### [2.0.0] - Prévue 2027
- [ ] 148 fiches plantes complètes et validées
- [ ] Système agent IA autonome
- [ ] Intégration WordPress/e-commerce

---
*Maintenu par l'Agent Maître et l'Agent Archiviste*
