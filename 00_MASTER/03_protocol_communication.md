# 03 — Protocole de Communication des Agents

## Format de message standard

Tout échange entre agents suit ce format :

```
DE : [Agent expéditeur]
À : [Agent destinataire]
SUJET : [VEILLE | VALIDATION | PRODUCTION | ALERTE | INFO]
PRIORITÉ : [HAUTE | NORMALE | BASSE]
DATE : YYYY-MM-DD

CORPS :
[Contenu du message]

ACTION REQUISE : [Oui/Non] — [Délai]
PIECES JOINTES : [Fichiers concernés]
```

## Types de messages

### VEILLE
L'Agent Veilleur informe des nouvelles données découvertes.

### VALIDATION
L'Agent Validateur communique son verdict sur des données soumises.

### PRODUCTION
L'Agent Archiviste soumet des contenus pour review.

### ALERTE
Tout agent peut émettre une alerte sur une anomalie critique.

### INFO
Partage d'informations sans action requise.

## Règles de communication

1. Tout message doit référencer un fichier source
2. Les décisions sont documentées dans `07_LOGS/`
3. Tout désaccord remonte à l'Agent Maître
4. L'humain est alerté si aucun consensus en 24h
5. Les messages d'ALERTE sont toujours priorité HAUTE

## Matrice de communication

| Expéditeur | Destinataire | Type autorisé |
|-----------|-------------|---------------|
| Veilleur | Validateur | VEILLE, INFO |
| Validateur | Archiviste | VALIDATION, INFO |
| Archiviste | Maître | PRODUCTION, ALERTE |
| Maître | Tous | Tous |
| Tous | Maître | ALERTE |

---
*Version 1.0 — 2026-05-29*
