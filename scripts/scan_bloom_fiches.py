#!/usr/bin/env python3
"""
scan_bloom_fiches.py
--------------------
Scanne 02_LIBRARY/plants/inbox/ pour détecter les nouvelles fiches *_BLOOM_vN.md,
valide leur structure YAML, génère agents_queue.json et logue dans 07_LOGS/update_log.md.

Usage:
    python scripts/scan_bloom_fiches.py
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml  # pip install pyyaml

# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
INBOX_DIR = ROOT / "02_LIBRARY" / "plants" / "inbox"
QUEUE_PATH = ROOT / "agents_queue.json"
LOG_PATH = ROOT / "07_LOGS" / "update_log.md"

# ---------------------------------------------------------------------------
# Champs YAML obligatoires dans le front-matter de chaque fiche
# ---------------------------------------------------------------------------
REQUIRED_FIELDS = ["plant_name", "version", "review_status", "last_update"]

# Regex pour matcher le pattern de nommage : NOM_PLANTE_BLOOM_vN.md
FILE_PATTERN = re.compile(r"^(.+)_BLOOM_v(\d+)\.md$", re.IGNORECASE)


def parse_front_matter(file_path: Path) -> dict:
    """Extrait le front-matter YAML d'un fichier Markdown."""
    content = file_path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as exc:
        print(f"[WARN] YAML invalide dans {file_path.name}: {exc}")
        return {}


def validate_schema(metadata: dict, filename: str) -> list:
    """Retourne la liste des champs manquants."""
    return [f for f in REQUIRED_FIELDS if f not in metadata]


def load_queue() -> list:
    if QUEUE_PATH.exists():
        return json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    return []


def save_queue(queue: list) -> None:
    QUEUE_PATH.write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")


def log_entry(message: str) -> None:
    """Ajoute une ligne horodatée dans le journal Markdown."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{timestamp}] {message}"
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(entry)


def scan() -> None:
    if not INBOX_DIR.exists():
        print(f"[ERROR] Dossier inbox introuvable : {INBOX_DIR}")
        sys.exit(1)

    queue = load_queue()
    already_queued = {t["file_path"] for t in queue}
    new_tasks = []
    errors = []

    md_files = list(INBOX_DIR.glob("*.md"))
    print(f"[SCAN] {len(md_files)} fichier(s) dans inbox/")

    for fp in sorted(md_files):
        match = FILE_PATTERN.match(fp.name)
        if not match:
            print(f"[SKIP] Nom non conforme à la convention : {fp.name}")
            continue

        plant_name_raw, version_str = match.group(1), match.group(2)
        plant_name = plant_name_raw.upper().replace("_", " ")
        version = int(version_str)
        str_path = str(fp.relative_to(ROOT))

        if str_path in already_queued:
            print(f"[SKIP] Déjà en queue : {fp.name}")
            continue

        # Validation du schéma YAML
        metadata = parse_front_matter(fp)
        missing = validate_schema(metadata, fp.name)
        if missing:
            msg = f"Champs manquants dans {fp.name} : {', '.join(missing)}"
            print(f"[WARN] {msg}")
            errors.append(msg)
            log_entry(f"SCHEMA_ERROR — {msg}")
            # On intègre quand même la fiche en queue avec statut 'schema_error'
            review_status = "schema_error"
        else:
            review_status = metadata.get("review_status", "collecting")

        task = {
            "file_path": str_path,
            "plant_name": plant_name,
            "version": version,
            "current_agent": "veilleur",
            "review_status": review_status,
            "priority": 0,
            "queued_at": datetime.now(timezone.utc).isoformat(),
        }
        new_tasks.append(task)
        print(f"[ADD] {fp.name} → plant={plant_name!r}, v{version}, status={review_status!r}")
        log_entry(f"QUEUED — {fp.name} | plant={plant_name!r} | version={version} | status={review_status!r}")

    if new_tasks:
        queue.extend(new_tasks)
        save_queue(queue)
        print(f"[OK] {len(new_tasks)} tache(s) ajoutée(s) dans agents_queue.json")
    else:
        print("[INFO] Aucune nouvelle fiche détectée.")

    if errors:
        print(f"\n[RESUME] {len(errors)} erreur(s) de schéma détectée(s).")
        for e in errors:
            print(f"  - {e}")


if __name__ == "__main__":
    scan()
