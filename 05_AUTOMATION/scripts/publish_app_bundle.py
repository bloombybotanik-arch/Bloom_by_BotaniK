#!/usr/bin/env python3
"""
publish_app_bundle.py
Bloom by BotaniK — Script de publication de l'App Bibliothèque

Ce script :
  1. Lit 03_BASE_DE_DONNEES/plants.json (source de vérité)
  2. Valide et enrichit les données si nécessaire
  3. Copie le fichier dans 06_APP_BIBLIOTHEQUE/data/plants.json
  4. Génère un index léger plants-index.json (id, nom, categories seulement)
  5. Génère version-manifest.json (versioning des données)
  6. Génère app-version.js (window.BloomVersion pour le bootstrap)
  7. Écrit un rapport dans 07_LOGS/app_publish_log.md

Usage :
  python3 05_AUTOMATION/scripts/publish_app_bundle.py

Variables d'environnement :
  PLANTS_JSON  : chemin source (défaut : 03_BASE_DE_DONNEES/plants.json)
  APP_DATA_DIR : dossier destination (défaut : 06_APP_BIBLIOTHEQUE/data)
  LOG_PATH     : fichier de log (défaut : 07_LOGS/app_publish_log.md)
"""
import json
import os
import sys
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# --- Configuration ---
PLANTS_JSON  = Path(os.environ.get('PLANTS_JSON',  '03_BASE_DE_DONNEES/plants.json'))
APP_DATA_DIR = Path(os.environ.get('APP_DATA_DIR', '06_APP_BIBLIOTHEQUE/data'))
LOG_PATH     = Path(os.environ.get('LOG_PATH',     '07_LOGS/app_publish_log.md'))


def get_git_commit() -> str:
    """Retourne le hash court du dernier commit Git, ou 'unknown'"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() or 'unknown'
    except Exception:
        return 'unknown'


def build_version_string() -> str:
    """Génère une version au format YYYY.MM.DD-NN (incrémenté automatiquement)"""
    now = datetime.now(timezone.utc)
    date_prefix = now.strftime('%Y.%m.%d')
    # Lire la version précédente pour incrémenter le compteur du jour
    manifest_path = APP_DATA_DIR / 'version-manifest.json'
    counter = 1
    if manifest_path.exists():
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                prev = json.load(f)
            prev_version = prev.get('plants_version', '')
            if prev_version.startswith(date_prefix):
                parts = prev_version.split('-')
                if len(parts) == 2 and parts[1].isdigit():
                    counter = int(parts[1]) + 1
        except Exception:
            pass
    return f"{date_prefix}-{counter:02d}"


def write_version_manifest(version: str, commit: str, generated_at: str):
    """Génère version-manifest.json dans APP_DATA_DIR"""
    manifest = {
        'app_version':    version,
        'plants_version': version,
        'generated_at':   generated_at,
        'source_commit':  commit
    }
    path = APP_DATA_DIR / 'version-manifest.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"[OK] version-manifest.json écrit : {path}")
    return manifest


def write_app_version_js(version: str, commit: str, generated_at: str):
    """Génère app-version.js exposant window.BloomVersion"""
    content = f"""/**
 * app-version.js
 * Bloom by BotaniK — Version globale de l'application
 *
 * Ce fichier est AUTOMATIQUEMENT GÉNÉRÉ par publish_app_bundle.py
 * Ne pas modifier manuellement.
 *
 * Exposé en window.BloomVersion pour être accessible
 * avant le chargement des modules ES.
 */

window.BloomVersion = {{
  app_version: "{version}",
  plants_version: "{version}",
  generated_at: "{generated_at}",
  source_commit: "{commit}"
}};

// Log de diagnostic (désactivable en prod)
if (typeof console !== 'undefined') {{
  console.info(
    `[BloomVersion] app=${{window.BloomVersion.app_version}}`,
    `plants=${{window.BloomVersion.plants_version}}`,
    `commit=${{window.BloomVersion.source_commit}}`
  );
}}
"""
    path = APP_DATA_DIR / 'app-version.js'
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[OK] app-version.js écrit : {path}")


def load_plants() -> list:
    """Charge et valide plants.json"""
    if not PLANTS_JSON.exists():
        print(f"[ERROR] plants.json introuvable : {PLANTS_JSON}", file=sys.stderr)
        sys.exit(1)
    with open(PLANTS_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Normaliser : accepter liste ou dict { plants: [] }
    if isinstance(data, list):
        plants = data
    elif isinstance(data, dict) and 'plants' in data:
        plants = data['plants']
    else:
        print("[ERROR] Format plants.json non reconnu.", file=sys.stderr)
        sys.exit(1)
    print(f"[OK] {len(plants)} plantes chargées depuis {PLANTS_JSON}")
    return plants


def validate_plant(plant: dict, idx: int) -> dict:
    """Valide et complète les champs manquants d'une fiche plante"""
    required = ['nom', 'resume_bloom']
    for field in required:
        if not plant.get(field):
            print(f"[WARNING] Plante #{idx} manque le champ '{field}' : {plant.get('nom', '?')}")
    # Générer un id si absent
    if not plant.get('id'):
        plant['id'] = plant.get('nom', f'plante_{idx}').lower().replace(' ', '-')
    # S'assurer que categories est une liste
    if not isinstance(plant.get('categories'), list):
        plant['categories'] = []
    # S'assurer que les listes sont bien des listes
    for field in ['bienfaits', 'precautions', 'synergie']:
        if not isinstance(plant.get(field), list):
            plant[field] = []
    # Ajouter le statut par défaut
    if not plant.get('statut'):
        plant['statut'] = 'validated'
    return plant


def build_index(plants: list) -> list:
    """Génère un index léger pour la recherche rapide"""
    return [
        {
            'id': p.get('id', ''),
            'nom': p.get('nom', ''),
            'nom_latin': p.get('nom_latin', ''),
            'categories': p.get('categories', []),
            'resume_bloom': p.get('resume_bloom', '')[:150]  # tronquer pour l'index
        }
        for p in plants
    ]


def write_json(path: Path, data, label: str):
    """Ecrit un fichier JSON propre"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OK] {label} écrit : {path}")


def write_log(plants_count: int, published: bool, errors: list, version: str):
    """Met à jour le journal de publication"""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    status = 'ok' if published and not errors else 'warning'
    entry = f"""
---
## Publication App Bibliothèque — {ts}
| Champ | Valeur |
|-------|--------|
| Status | {status} |
| Version | {version} |
| Plantes publiées | {plants_count} |
| Erreurs | {len(errors)} |
| Source | {PLANTS_JSON} |
| Destination | {APP_DATA_DIR} |
"""
    if errors:
        entry += "\n### Erreurs\n"
        for e in errors:
            entry += f"- {e}\n"
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(entry)
    print(f"[OK] Log mis à jour : {LOG_PATH}")


def main():
    print("=" * 60)
    print("publish_app_bundle.py — Bloom by BotaniK")
    print("=" * 60)
    errors = []

    # 0. Calcul de la version et du commit
    version      = build_version_string()
    commit       = get_git_commit()
    generated_at = datetime.now().astimezone().isoformat(timespec='seconds')
    print(f"[OK] Version du build : {version} | commit : {commit}")

    # 1. Charger les plantes
    plants = load_plants()

    # 2. Valider et enrichir
    validated = []
    for i, plant in enumerate(plants):
        try:
            validated.append(validate_plant(plant, i))
        except Exception as e:
            err = f"Plante #{i} ({plant.get('nom', '?')}) : {e}"
            errors.append(err)
            print(f"[ERROR] {err}", file=sys.stderr)
    print(f"[OK] {len(validated)} plantes validées ({len(errors)} erreur(s))")

    # 3. Copier plants.json complet dans l'app
    dest_plants = APP_DATA_DIR / 'plants.json'
    write_json(dest_plants, validated, 'plants.json complet')

    # 4. Générer l'index léger
    index = build_index(validated)
    dest_index = APP_DATA_DIR / 'plants-index.json'
    write_json(dest_index, index, 'plants-index.json')

    # 5. Générer version-manifest.json
    write_version_manifest(version, commit, generated_at)

    # 6. Générer app-version.js
    write_app_version_js(version, commit, generated_at)

    # 7. Rapport
    write_log(len(validated), True, errors, version)

    print("=" * 60)
    print(f"[DONE] {len(validated)} plantes publiées dans {APP_DATA_DIR} (v{version})")
    print("=" * 60)
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
