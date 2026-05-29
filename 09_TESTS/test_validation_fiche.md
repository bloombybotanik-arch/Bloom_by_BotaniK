# Test — Validation d'une Fiche Plante Bloom

**Version** : 1.0  
**Type** : Test de cohérence et conformité  
**Responsable** : Agent_Validateur_scientifique  
**Mis à jour** : 2026-05-29

---

## Objectif

Vérifier qu'une fiche plante générée par le système multi-agents Bloom by BotaniK respecte l'ensemble des standards de qualité scientifiques, réglementaires et formels avant validation finale.

---

## Checklist de validation — Structure formelle

### 1. Conformité du nommage
- [ ] Fichier nommé `[NOM_PLANTE]_BLOOM_v[X].md`
- [ ] Nom de plante en majuscules (ex. `ASHWAGANDHA_BLOOM_v1.md`)
- [ ] Numéro de version correct (v1, v2...)
- [ ] Déposé dans `02_LIBRARY/plantes/`

### 2. Complétude des sections
- [ ] Section 1 — Identification botanique : tous les champs remplis
- [ ] Section 2 — Composition : au moins 1 principe actif renseigné
- [ ] Section 3 — Mécanismes d'action : au moins 1 voie renseignée
- [ ] Section 4 — Données cliniques : tableau études rempli
- [ ] Section 5 — Sécurité : contre-indications et populations à risque renseignées
- [ ] Section 6 — Allégations : au moins 1 claim évalué (VERT/ORANGE/ROUGE)
- [ ] Section 8 — Recommandations Bloom : dosage et forme renseignés
- [ ] Section 9 — Sources : au moins 1 référence PMID présente
- [ ] Section 10 — Historique : entrée v1.0 présente

---

## Checklist de validation — Qualité scientifique

### 3. Sources et niveau de preuve
- [ ] Toutes les études mentionnées ont un PMID valide
- [ ] Les fichiers `PMID[XXXXX]_[NOM_PLANTE].md` sont créés dans `02_LIBRARY/sources/`
- [ ] Le niveau de preuve (IàV) est cohérent avec les études listées
- [ ] Les méta-analyses / ECR sont privilégiés si disponibles

### 4. Cohérence des claims
- [ ] Tous les claims VERT figurent dans le registre CE 1924/2006
- [ ] Aucun claim ROUGE n'est présent dans les recommandations Bloom
- [ ] Les claims ORANGE ont leur condition clairement spécifiée
- [ ] Aucune référence à une maladie dans les claims

### 5. Sécurité
- [ ] La plante n'est pas interdite par l'ANSM en France
- [ ] Les interactions médicamenteuses majeures sont mentionnées
- [ ] Les populations à risque sont toutes évaluées

---

## Checklist de validation — Cohérence interne

- [ ] Le nom latin dans l'en-tête correspond au tableau d'identification
- [ ] Les dosages des recommandations Bloom sont dans la fourchette des études
- [ ] Le niveau de preuve de l'en-tête = niveau de preuve global section 4.2
- [ ] Le statut est `VALIDÉ` (pas `EN COURS` ou `ARCHIVÉ`)
- [ ] L'agent auteur = `Agent_Veilleur_botanique`
- [ ] L'agent validateur = `Agent_Validateur_scientifique`

---

## Résultat du test

```
Fiche testée : [NOM_PLANTE]_BLOOM_v[X].md
Date du test : [YYYY-MM-DD]
Testeur : Agent_Validateur_scientifique

Nombre de points vérifiés : [N]
Nombre de points validés : [N]
Nombre de points à corriger : [N]

Points à corriger :
- [Point 1]
- [Point 2]

Décision : [VALIDÉ / À CORRIGER / REJETÉ]
Signature Agent_Maitre : ______
```

---

## Seuils de validation Bloom

| Score | Décision |
|---|---|
| 100% des points obligatoires validés | VALIDÉ |
| 1 point obligatoire manquant | À CORRIGER |
| Multiple points manquants ou claim ROUGE présent | REJETÉ |

**Points obligatoires** : 1, 3, 4.1, 4.2, 5, 6 (tous les items marqués ci-dessus)
