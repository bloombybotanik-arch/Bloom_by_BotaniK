#!/usr/bin/env python3
"""
agent_archiviste.py
-------------------
Agent 3 — Archiviste Éditorial.

Rôle :
  - Lire les fiches en statut 'validated' dans la queue
  - Transformer la fiche en version Bloom propre (ton de marque, disclaimers)
  - Mettre à jour le manifest.json (index des plantes actives)
  - Déplacer l'ancienne version vers 08_ARCHIVE/retired_plant_fiches/
  - Publier la nouvelle version dans 02_LIBRARY/plants/active/
  - Logger dans 07_LOGS/update_log.md
  - Retirer la tâche de la queue

NOTE : Le bloc LLM_CALL est le point d'intégration pour la mise en forme finale.
"""

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE_PATH = ROOT / "agents_queue.json"
LOG_PATH = ROOT / "07_LOGS" / "update_log.md"
ACTIVE_DIR = ROOT / "02_LIBRARY" / "plants" / "active"
ARCHIVE_DIR = ROOT / "08_ARCHIVE" / "retired_plant_fiches"
MANIFEST_PATH = ROOT / "manifest.json"

# Disclaimer Bloom standard à ajouter en tête de toute fiche publiée
BLOOM_DISCLAIMER = """---
> **Disclaimer Bloom by BotaniK** — Cette fiche est rédigée à titre informatif.
> Elle ne constitue pas un conseil médical. Consultez un professionnel de santé
> avant tout usage thérapeutique. Informations validées scientifiquement selon
> les données disponibles au moment de la publication.
---

"""


def load_queue() -> list:
    if not QUEUE_PATH.exists():
        return []
    return json.loads(QUEUE_PATH.read_text(encoding="utf-8"))


def save_queue(queue: list) -> None:
    QUEUE_PATH.write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")


def log_entry(message: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"\n- [{timestamp}] [ARCHIVISTE] {message}")


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {"plants": [], "last_updated": None, "total": 0}


def save_manifest(manifest: dict) -> None:
    manifest["last_updated"] = datetime.now(timezone.utc).isoformat()
    manifest["total"] = len(manifest["plants"])
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def update_manifest(plant_name: str, version: int, active_path: Path) -> None:
    manifest = load_manifest()
    entry = {
        "plant_name": plant_name,
        "version": version,
        "active_file": str(active_path.relative_to(ROOT)),
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    # Mettre à jour ou ajouter l'entrée
    plants = [p for p in manifest["plants"] if p["plant_name"] != plant_name]
    plants.append(entry)
    manifest["plants"] = sorted(plants, key=lambda p: p["plant_name"])
    save_manifest(manifest)


def archive_previous_versions(plant_name: str, version: int) -> int:
    """Archive les versions précédentes de la même plante dans active/."""
    archived = 0
    pattern = re.compile(rf"^{re.escape(plant_name.replace(' ', '_'))}_BLOOM_v(\d+)\.md$", re.IGNORECASE)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    for f in ACTIVE_DIR.glob("*.md"):
        m = pattern.match(f.name)
        if m:
            old_version = int(m.group(1))
            if old_version < version:
                dest = ARCHIVE_DIR / f.name
                shutil.move(str(f), str(dest))
                print(f"[ARCHIVISTE] Archive : {f.name} → retired_plant_fiches/")
                archived += 1
    return archived


def llm_format(plant_name: str, content: str) -> str:
    """
    POINT D'INTÉGRATION LLM — Mise en forme finale version Bloom.

    Le LLM doit transformer la fiche validée en :
      - Ton de marque Bloom (clair, scientifique, accessible)
      - Ajout du disclaimer standard
      - Structure propre et uniforme
      - Préparation des contenus dérivés (résumés, bullet points SEO)
    """
    # Placeholder : ajoute le disclaimer Bloom si absent
    if "Disclaimer Bloom" not in content:
        # Insérer après le front-matter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = f"---{parts[1]}---\n\n{BLOOM_DISCLAIMER}{parts[2]}"
        else:
            content = BLOOM_DISCLAIMER + content
    return content


def process_task(task: dict) -> bool:
    file_path = ROOT / task["file_path"]
    plant_name = task["plant_name"]
    version = task["version"]

    if not file_path.exists():
        print(f"[ARCHIVISTE][ERROR] Fichier introuvable : {file_path}")
        return False

    content = file_path.read_text(encoding="utf-8")
    print(f"[ARCHIVISTE] Publication de {file_path.name} ({plant_name} v{version})...")

    # Mise en forme finale
    formatted = llm_format(plant_name, content)

    # Archiver les anciennes versions
    nb_archived = archive_previous_versions(plant_name, version)
    if nb_archived:
        print(f"[ARCHIVISTE] {nb_archived} ancienne(s) version(s) archivée(s).")

    # Publier en active/
    ACTIVE_DIR.mkdir(parents=True, exist_ok=True)
    active_dest = ACTIVE_DIR / file_path.name
    file_path.write_text(formatted, encoding="utf-8")
    shutil.move(str(file_path), str(active_dest))
    print(f"[ARCHIVISTE] Publié : {active_dest.relative_to(ROOT)}")

    # Mettre à jour le manifest
    update_manifest(plant_name, version, active_dest)

    log_entry(f"Publié : {file_path.name} | {plant_name} v{version} → active/ | {nb_archived} ancienne(s) archivée(s)")
    return True


def main():
    queue = load_queue()
    if not queue:
        print("[ARCHIVISTE] Queue vide.")
        return

    new_queue = []
    published = 0
    for task in queue:
        if task.get("current_agent") != "archiviste" or task.get("review_status") != "validated":
            new_queue.append(task)
            continue
        success = process_task(task)
        if success:
            published += 1
            # La tâche est retirée de la queue (archivée avec succès)
        else:
            task["review_status"] = "archivage_error"
            new_queue.append(task)

    save_queue(new_queue)
    print(f"\n[ARCHIVISTE] {published} fiche(s) publiée(s) en active/ | {len(new_queue)} tâche(s) restantes en queue.")


if __name__ == "__main__":
    main()
