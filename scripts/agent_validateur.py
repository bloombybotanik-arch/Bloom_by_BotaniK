#!/usr/bin/env python3
"""
agent_validateur.py
-------------------
Agent 2 — Validateur Scientifique.

Rôle :
  - Lire les fiches en statut 'scientific_review' dans la queue
  - Analyser et classer les preuves par niveau d'évidence :
      * RCT (essais contrôlés randomisés)
      * Méta-analyses et revues systématiques
      * Études observationnelles
      * Données précliniques (in vitro, animal)
      * Tradition / usage ethnobotanique
  - Valider ou rejeter chaque claim
  - Identifier ce qui doit être corrigé avant publication
  - Mettre à jour review_status → 'validated' ou retour à 'collecting'
  - Router vers l'agent archiviste (agent 3)

NOTE : Le bloc LLM_CALL est le point d'intégration avec votre modèle AI.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE_PATH = ROOT / "agents_queue.json"
LOG_PATH = ROOT / "07_LOGS" / "update_log.md"

# Niveaux de preuve acceptés (du plus fort au plus faible)
EVIDENCE_LEVELS = [
    "RCT",
    "meta-analyse",
    "revue systematique",
    "etude observationnelle",
    "preclinique",
    "tradition",
    "avis expert",
]

# Section attendue dans la fiche après validation
VALIDATION_SECTION = "## Rapport de validation scientifique"


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
        f.write(f"\n- [{timestamp}] [VALIDATEUR] {message}")


def update_front_matter_status(content: str, new_status: str) -> str:
    pattern = r'(review_status:\s*)[^\n]+'
    replacement = f'\\g<1>{new_status}'
    if re.search(pattern, content):
        return re.sub(pattern, replacement, content)
    return content


def update_last_update(content: str) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    pattern = r'(last_update:\s*)[^\n]+'
    replacement = f'\\g<1>{today}'
    if re.search(pattern, content):
        return re.sub(pattern, replacement, content)
    return content


def llm_validate(plant_name: str, content: str) -> tuple:
    """
    POINT D'INTÉGRATION LLM — à remplacer par votre appel API réel.

    Retour :
      (validated_content: str, is_validated: bool)

    Exemple d'intégration :
      Le LLM reçoit la fiche enrichie et doit retourner :
      - La fiche annotée avec niveaux de preuve
      - Un verdict : validated / return_to_collecting
      - Les corrections à apporter si rejet
    """
    # Placeholder : ajoute la section de validation avec un message indicatif
    if VALIDATION_SECTION not in content:
        validation_block = f"""

{VALIDATION_SECTION}

| Claim | Niveau de preuve | Verdict | Commentaire |
|-------|-----------------|---------|-------------|
| TODO  | à déterminer    | Pending | À compléter par le Validateur pour {plant_name} |

**Verdict global :** Pending — revue manuelle requise.

**Corrections requises avant publication :**
- [ ] TODO : à lister par le validateur.
"""
        content = content + validation_block
    # Par défaut en mode placeholder : on valide (True)
    return content, True


def process_task(task: dict) -> dict:
    file_path = ROOT / task["file_path"]
    plant_name = task["plant_name"]

    if not file_path.exists():
        print(f"[VALIDATEUR][ERROR] Fichier introuvable : {file_path}")
        task["review_status"] = "error_file_not_found"
        return task

    content = file_path.read_text(encoding="utf-8")
    print(f"[VALIDATEUR] Validation de {file_path.name} ({plant_name})...")

    validated_content, is_validated = llm_validate(plant_name, content)

    if is_validated:
        new_status = "validated"
        next_agent = "archiviste"
        print(f"[VALIDATEUR] {file_path.name} → VALIDÉ (transmis à l'archiviste)")
    else:
        new_status = "collecting"
        next_agent = "veilleur"
        print(f"[VALIDATEUR] {file_path.name} → REJETÉ — retour au veilleur")

    validated_content = update_front_matter_status(validated_content, new_status)
    validated_content = update_last_update(validated_content)
    file_path.write_text(validated_content, encoding="utf-8")

    task["current_agent"] = next_agent
    task["review_status"] = new_status

    log_entry(f"{file_path.name} | {plant_name} → {new_status} | prochain : {next_agent}")
    return task


def main():
    queue = load_queue()
    if not queue:
        print("[VALIDATEUR] Queue vide.")
        return

    updated = False
    for i, task in enumerate(queue):
        if task.get("current_agent") != "validateur":
            continue
        if task.get("review_status") in ("schema_error", "error_file_not_found"):
            print(f"[VALIDATEUR][SKIP] {task['file_path']} (statut : {task['review_status']})")
            continue
        queue[i] = process_task(task)
        updated = True

    if updated:
        save_queue(queue)
    else:
        print("[VALIDATEUR] Aucune fiche à valider.")


if __name__ == "__main__":
    main()
