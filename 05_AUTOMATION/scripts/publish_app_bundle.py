#!/usr/bin/env python3
"""
publish_app_bundle.py
Bloom by BotaniK — Script de publication de l'App Bibliothèque

Ce script :
  1. Lit 03_BASE_DE_DONNEES/plants.json (source de vérité)
  2. Valide et enrichit les données
  3. Copie plants.json dans 06_APP_BIBLIOTHEQUE/data/
  4. Génère plants-index.json (id, nom, categories)
  5. Génère version-manifest.json (app_version, plants_version, build_id, source_commit)
  6. Génère app-version.js (window.BloomVersion)
  7. Copie version-manifest.json dans 03_BASE_DE_DONNEES/ (source de vérité)
  8. Écrit un rapport dans 07_LOGS/app_publish_log.md

Usage :
  python3 05_AUTOMATION/scripts/publish_app_bundle.py
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess
import sys

# --- Chemins absolus basés sur la position du script ---
ROOT        = Path(__file__).resolve().parents[2]
DB_DIR      = ROOT / "03_BASE_DE_DONNEES"
APP_DATA_DIR = ROOT / "06_APP_BIBLIOTHEQUE" / "data"
LOG_PATH    = ROOT / "07_LOGS" / "app_publish_log.md"

APP_DATA_DIR.mkdir(parents=True, exist_ok=True)


def git_short_sha() -> str:
    """Retourne le hash court du dernier commit Git, ou 'unknown'"""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            text=True
        ).strip()
    except Exception:
        return "unknown"


def build_version() -> str:
    """Génère une version au format YYYY.MM.DD-HH (heure UTC, déterministe)"""
    return datetime.now(timezone.utc).strftime("%Y.%m.%d-%H")


def write_manifest(app_version: str, plants_version: str, commit: str) -> dict:
    """Génère version-manifest.json dans APP_DATA_DIR et DB_DIR"""
    manifest = {
        "app_version":    app_version,
        "plants_version": plants_version,
        "generated_at":   datetime.now(timezone.utc).isoformat(),
        "source_commit":  commit,
        "build_id":       f"bloom-{app_version.replace('.', '').replace('-', '-')}"
    }
    for dest in [APP_DATA_DIR, DB_DIR]:
        out = dest / "version-manifest.json"
        out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[OK] version-manifest.json écrit : {out}")
    return manifest


def write_app_version_js(app_version: str, plants_version: str, commit: str, build_id: str, generated_at: str):
    """Génère app-version.js exposant window.BloomVersion"""
    content = f"""/**
 * app-version.js — AUTOMATIQUEMENT GÉNÉRÉ par publish_app_bundle.py
 * Ne pas modifier manuellement.
 */
window.BloomVersion = {{
  app_version: "{app_version}",
  plants_version: "{plants_version}",
  generated_at: "{generated_at}",
  source_commit: "{commit}",
  build_id: "{build_id}"
}};
if (typeof console !== 'undefined') {{
  console.info('[BloomVersion]', window.BloomVersion);
}}
"""
    path = APP_DATA_DIR / "app-version.js"
    path.write_text(content, encoding="utf-8")
    print(f"[OK] app-version.js écrit : {path}")


def load_plants() -> list:
    """Charge plants.json depuis DB_DIR"""
    src = DB_DIR / "plants.json"
    if not src.exists():
        print(f"[ERROR] plants.json introuvable : {src}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(src.read_text(encoding="utf-8"))
    if isinstance(data, list):
        plants = data
    elif isinstance(data, dict) and "plants" in data:
        plants = data["plants"]
    else:
        print("[ERROR] Format plants.json non reconnu.", file=sys.stderr)
        sys.exit(1)
    print(f"[OK] {len(plants)} plantes chargées depuis {src}")
    return plants


def validate_plant(plant: dict, idx: int) -> dict:
    """Valide et complète une fiche plante"""
    for field in ["nom", "resume_bloom"]:
        if not plant.get(field):
            print(f"[WARNING] Plante #{idx} manque '{field}' : {plant.get('nom', '?')}")
    if not plant.get("id"):
        plant["id"] = plant.get("nom", f"plante_{idx}").lower().replace(" ", "-")
    if not isinstance(plant.get("categories"), list):
        plant["categories"] = []
    for field in ["bienfaits", "precautions", "synergie"]:
        if not isinstance(plant.get(field), list):
            plant[field] = []
    if not plant.get("statut"):
        plant["statut"] = "validated"
    return plant


def build_index(plants: list) -> list:
    """Génère un index léger"""
    return [
        {
            "id":           p.get("id", ""),
            "nom":          p.get("nom", ""),
            "nom_latin":    p.get("nom_latin", ""),
            "categories":   p.get("categories", []),
            "resume_bloom": p.get("resume_bloom", "")[:150]
        }
        for p in plants
    ]


def write_json(path: Path, data, label: str):
    """Ecrit un fichier JSON propre"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] {label} écrit : {path}")


def write_log(plants_count: int, errors: list, version: str, build_id: str):
    """Journalise la publication"""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts     = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    status = "ok" if not errors else "warning"
    entry  = f"""
---
## Publication App Bibliothèque — {ts}
| Champ | Valeur |
|-------|--------|
| Status | {status} |
| Version | {version} |
| Build ID | {build_id} |
| Plantes publiées | {plants_count} |
| Erreurs | {len(errors)} |
"""
    if errors:
        entry += "\n### Erreurs\n" + "\n".join(f"- {e}" for e in errors) + "\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"[OK] Log mis à jour : {LOG_PATH}")


def main():
    print("=" * 60)
    print("publish_app_bundle.py — Bloom by BotaniK")
    print("=" * 60)
    errors = []

    # 0. Version + commit
    app_version    = build_version()
    plants_version = app_version
    commit         = git_short_sha()
    generated_at   = datetime.now(timezone.utc).isoformat()
    build_id       = f"bloom-{app_version.replace('.', '').replace('-', '-')}"
    print(f"[OK] Version : {app_version} | commit : {commit} | build : {build_id}")

    # 1. Charger les plantes
    plants = load_plants()

    # 2. Valider
    validated = []
    for i, plant in enumerate(plants):
        try:
            validated.append(validate_plant(plant, i))
        except Exception as e:
            err = f"Plante #{i} ({plant.get('nom', '?')}) : {e}"
            errors.append(err)
            print(f"[ERROR] {err}", file=sys.stderr)
    print(f"[OK] {len(validated)} plantes validées ({len(errors)} erreur(s))")

    # 3. Copier plants.json
    write_json(APP_DATA_DIR / "plants.json", validated, "plants.json")

    # 4. Générer l'index
    write_json(APP_DATA_DIR / "plants-index.json", build_index(validated), "plants-index.json")

    # 5. Générer version-manifest.json (app + db)
    manifest = write_manifest(app_version, plants_version, commit)

    # 6. Générer app-version.js
    write_app_version_js(app_version, plants_version, commit, build_id, generated_at)

    # 7. Log
    write_log(len(validated), errors, app_version, build_id)

    print("=" * 60)
    print(f"[DONE] {len(validated)} plantes publiées (v{app_version} / {build_id})")
    print("=" * 60)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
