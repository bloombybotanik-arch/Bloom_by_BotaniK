#!/usr/bin/env python3
"""
validate_plants_json.py
Bloom by BotaniK — Validation stricte de plants.json avant publication

Ce script :
  1. Vérifie que plants.json est un JSON valide et parsable
  2. Valide la structure globale (liste non vide)
  3. Valide chaque fiche contre plant_schema.json (JSON Schema Draft-07)
  4. Détecte les doublons d'id
  5. Compte les champs optionnels manquants (avertissements non bloquants)
  6. Écrit un rapport détaillé dans 07_LOGS/validation_log.md
  7. Retourne exit code 0 si OK, 1 si erreurs bloquantes

Usage :
  python3 05_AUTOMATION/scripts/validate_plants_json.py

Variables d'environnement :
  PLANTS_JSON  : chemin du fichier (défaut: 03_BASE_DE_DONNEES/plants.json)
  SCHEMA_FILE  : chemin du schéma (défaut: 03_BASE_DE_DONNEES/plant_schema.json)
  LOG_PATH     : fichier de log (défaut: 07_LOGS/validation_log.md)
  STRICT_MODE  : 'true' pour échouer sur les avertissements (défaut: false)
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter

# --- Configuration ---
PLANTS_JSON = Path(os.environ.get('PLANTS_JSON', '03_BASE_DE_DONNEES/plants.json'))
SCHEMA_FILE = Path(os.environ.get('SCHEMA_FILE', '03_BASE_DE_DONNEES/plant_schema.json'))
LOG_PATH = Path(os.environ.get('LOG_PATH', '07_LOGS/validation_log.md'))
STRICT_MODE = os.environ.get('STRICT_MODE', 'false').lower() == 'true'

# Champs recommandés (non bloquants)
RECOMMENDED_FIELDS = ['nom_latin', 'categories', 'bienfaits', 'precautions', 'statut']

# Champs requis (bloquants si absents)
REQUIRED_FIELDS = ['id', 'nom', 'resume_bloom']


def load_json(path: Path, label: str) -> dict | list | None:
    """Charge un fichier JSON, retourne None si invalide"""
    if not path.exists():
        print(f"[ERROR] Fichier introuvable : {path}")
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON invalide dans {label} : {e}")
        return None


def validate_schema(plant: dict, schema: dict, idx: int) -> list:
    """
    Validation minimaliste contre le schéma sans dépendance externe.
    Retourne une liste d'erreurs (vide si OK).
    Utilise jsonschema si disponible, sinon validation manuelle.
    """
    errors = []

    # Essayer jsonschema d'abord
    try:
        import jsonschema
        try:
            jsonschema.validate(instance=plant, schema=schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema violation: {e.message}")
        return errors
    except ImportError:
        pass  # Fallback sur validation manuelle

    # Validation manuelle si jsonschema absent
    for field in REQUIRED_FIELDS:
        if not plant.get(field):
            errors.append(f"Champ requis manquant ou vide : '{field}'")

    # Vérifier l'id
    plant_id = plant.get('id', '')
    if plant_id and not all(c.isalnum() or c in '-_' for c in plant_id):
        errors.append(f"'id' invalide (doit être URL-safe) : '{plant_id}'")

    # Vérifier resume_bloom
    resume = plant.get('resume_bloom', '')
    if resume and len(resume) < 20:
        errors.append(f"'resume_bloom' trop court ({len(resume)} cars, minimum 20)")

    # Vérifier les types de listes
    for field in ['categories', 'bienfaits', 'precautions', 'synergie']:
        val = plant.get(field)
        if val is not None and not isinstance(val, list):
            errors.append(f"'{field}' doit être un tableau, reçu : {type(val).__name__}")

    # Vérifier statut
    statut = plant.get('statut')
    valid_statuts = {'collecting', 'reviewing', 'validated', 'needs_review', 'rejected', 'archived'}
    if statut and statut not in valid_statuts:
        errors.append(f"'statut' invalide : '{statut}' (attendu: {', '.join(sorted(valid_statuts))})")

    # Vérifier catégories
    valid_cats = {
        'adaptogene', 'anti-inflammatoire', 'immunitaire', 'digestif', 'nerveux',
        'hormonal', 'cardiovasculaire', 'hepatique', 'respiratoire', 'dermatologique',
        'antioxydant', 'antimicrobien', 'antifongique', 'analgesique', 'diuretique',
        'sedatif', 'tonique', 'autre'
    }
    for cat in plant.get('categories', []):
        if cat not in valid_cats:
            errors.append(f"Catégorie inconnue : '{cat}'")

    return errors


def check_warnings(plant: dict) -> list:
    """Vérifie les champs recommandés (non bloquants)"""
    warnings = []
    for field in RECOMMENDED_FIELDS:
        val = plant.get(field)
        if val is None or val == '' or val == []:
            warnings.append(f"Champ recommandé absent ou vide : '{field}'")
    return warnings


def write_log(results: dict):
    """Ecrit le rapport de validation dans le log"""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    status = 'PASS' if results['errors'] == 0 else 'FAIL'

    report = f"""
---
## Validation plants.json — {ts}

| Champ | Valeur |
|-------|--------|
| Status global | **{status}** |
| Plantes analysées | {results['total']} |
| Plantes valides | {results['valid']} |
| Plantes avec erreurs | {results['errors']} |
| Avertissements | {results['warnings']} |
| Doublons d'id | {results['duplicates']} |
| Mode strict | {'oui' if STRICT_MODE else 'non'} |
| Source | {PLANTS_JSON} |
"""
    if results['error_list']:
        report += "\n### Erreurs bloquantes\n"
        for e in results['error_list']:
            report += f"- {e}\n"

    if results['warning_list']:
        report += "\n### Avertissements\n"
        for w in results['warning_list']:
            report += f"- {w}\n"

    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(report)

    print(f"[OK] Rapport écrit : {LOG_PATH}")


def main() -> int:
    print("=" * 60)
    print("validate_plants_json.py — Bloom by BotaniK")
    print("=" * 60)

    # 1. Charger plants.json
    data = load_json(PLANTS_JSON, 'plants.json')
    if data is None:
        return 1

    # Normaliser
    if isinstance(data, list):
        plants = data
    elif isinstance(data, dict) and 'plants' in data:
        plants = data['plants']
    else:
        print("[ERROR] Structure plants.json non reconnue (attendu: liste ou {plants: []})")
        return 1

    if not plants:
        print("[ERROR] plants.json est vide (aucune plante)")
        return 1

    print(f"[OK] {len(plants)} plantes à valider")

    # 2. Charger le schéma
    schema = load_json(SCHEMA_FILE, 'plant_schema.json')
    if schema is None:
        print("[WARNING] Schéma introuvable — validation manuelle seulement")
        schema = {}

    # 3. Détecter les doublons d'id
    ids = [p.get('id', '') for p in plants]
    id_counts = Counter(ids)
    duplicates = {id_: count for id_, count in id_counts.items() if count > 1}

    all_errors = []
    all_warnings = []
    valid_count = 0
    error_count = 0

    # 4. Valider chaque fiche
    for i, plant in enumerate(plants):
        plant_name = plant.get('nom', f'plante_{i}')
        plant_id = plant.get('id', '?')
        prefix = f"[{i+1}/{len(plants)}] {plant_name} ({plant_id})"

        errors = validate_schema(plant, schema, i)
        warnings = check_warnings(plant)

        # Signaler les doublons
        if plant_id in duplicates:
            errors.append(f"ID dupliqué : '{plant_id}' apparait {duplicates[plant_id]}x")

        if errors:
            error_count += 1
            for e in errors:
                msg = f"{prefix} — ERREUR: {e}"
                all_errors.append(msg)
                print(f"[ERREUR] {msg}")
        else:
            valid_count += 1
            print(f"[OK] {prefix}")

        for w in warnings:
            msg = f"{prefix} — {w}"
            all_warnings.append(msg)
            print(f"[WARN]  {msg}")

    # 5. Résumé
    print("=" * 60)
    print(f"Résultat : {valid_count}/{len(plants)} valides | {error_count} erreurs | {len(all_warnings)} avertissements")
    if duplicates:
        print(f"[ERROR] Doublons détectés : {list(duplicates.keys())}")
    print("=" * 60)

    # 6. Rapport
    write_log({
        'total': len(plants),
        'valid': valid_count,
        'errors': error_count,
        'warnings': len(all_warnings),
        'duplicates': len(duplicates),
        'error_list': all_errors,
        'warning_list': all_warnings[:20]  # Max 20 warnings dans le log
    })

    # 7. Exit code
    if error_count > 0 or len(duplicates) > 0:
        print(f"[FAIL] Validation échouée : {error_count} erreur(s), {len(duplicates)} doublon(s)")
        return 1

    if STRICT_MODE and all_warnings:
        print(f"[FAIL] Mode strict : {len(all_warnings)} avertissement(s) non tolérés")
        return 1

    print("[PASS] Validation réussie — plants.json prêt pour publication")
    return 0


if __name__ == '__main__':
    sys.exit(main())
