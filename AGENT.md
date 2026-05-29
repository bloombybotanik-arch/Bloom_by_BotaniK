# AGENT.md — Instructions pour les agents IA

## Bloom by BotaniK — Contexte général

Ce dépôt est le cerveau de Bloom by BotaniK : un système de connaissance vivant autour des plantes médicinales, adaptogènes et fonctionnelles.

## Règles fondamentales

1. **Toujours lire le MASTER** avant toute action : `00_MASTER/Bloom_by_BotaniK_Master_Reference.md`
2. **Ne jamais inventer** de données scientifiques — citer uniquement des sources validées
3. **Respecter la convention bilingue** : anglais pour la structure, français pour le contenu
4. **Versionner** toute modification significative dans `09_versioning_change_log.md`
5. **Suivre le protocole** de communication défini dans `03_protocol_communication.md`

## Agents actifs

| Agent | Fichier de référence | Rôle principal |
|-------|---------------------|----------------|
| Agent Maître | `01_AGENTS/Agent_maitre.md` | Orchestration et coordination |
| Agent Veilleur Botanique | `01_AGENTS/Agent_Veilleur_botanique.md` | Veille scientifique |
| Agent Validateur Scientifique | `01_AGENTS/Agent_Validateur_scientifique.md` | Validation des preuves |
| Agent Archiviste Éditorial | `01_AGENTS/Agent_Archiviste_editorial_Bloom.md` | Production de contenu |

## Workflow standard

```
Veilleur → collecte données → Validateur → vérifie preuves → Archiviste → produit contenu → Maître → valide et orchestre
```

## Priorités absolues

- Exactitude scientifique > vitesse de production
- Cohérence de marque > volume de contenu
- Preuve validée > claim marketing

---
*Dernière mise à jour : 2026-05-29*
