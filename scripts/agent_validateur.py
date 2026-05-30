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
      * Données précliniques (in vitro, animale)
      * Tradition / usage ethnobotanique
  - Valider ou rejeter chaque claim
  - Identifier ce qui doit être corrigé avant publication
  - Mettre à jour review_status → 'validated' ou retour à 'collecting'
  - Router vers l'agent archiviste (agent 3)

NOTE : Le bloc LLM_CALL est le point d'intégration avec votre modèle AI.
"""

import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE_PATH = ROOT / "agents_queue.json"
LOG_PATH = ROOT / "07_LOGS" / "update_log.md"

DRAFTS_DIR = ROOT / "02_LIBRARY" / "plants" / "drafts"
VALIDATED_DIR = ROOT / "02_LIBRARY" / "plants" / "validated"
INBOX_DIR = ROOT / "02_LIBRARY" / "plants" / "inbox"

# Niveaux de preuve acceptés (du plus fort au plus faible)
EVIDENCE_LEVELS = [
    "RCT",
    "méta-analyse",
    "revue systématique",
    "étude observationnelle",
    "préclinique",
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
    if re.search(pattern, content):
        return re.sub(pattern, f'\\g<1>{new_status}', content)
    return content


def update_last_update(content: str) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    pattern = r'(last_update:\s*)[^\n]+'
    if re.search(pattern, content):
        return re.sub(pattern, f'\\g<1>{today}', content)
    return content


def llm_validate(plant_name: str, content: str) -> tuple:
    """
    POINT D'INTÉGRATION CLAUDE — validation scientifique via API Anthropic.

    Pour activer : décommenter le bloc ci-dessous et ajouter ANTHROPIC_API_KEY
    dans les secrets GitHub (Settings > Secrets and variables > Actions).

    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
    prompt = f'''
    Tu es un expert en phytothérapie et médecine botanique.
    Voici une fiche plante enrichie à valider scientifiquement :

    {content}

    Pour la plante {plant_name}, analyse chaque claim et :
    1. Classe les preuves par niveau d'évidence (RCT, méta-analyse, revue systématique,
       étude observationnelle, préclinique, tradition, avis expert)
    2. Valide ou rejette chaque claim selon les preuves disponibles
    3. Identifie les corrections à apporter avant publication
    4. Rends un verdict global : validé (prêt pour publication) ou rejeté (retour au veilleur)

    Retourne la fiche complète en Markdown avec la section ## Rapport de validation scientifique
    remplie, et le verdict global en fin de fiche.
    '''
    message = client.messages.create(
        model='claude-opus-4-5',
        max_tokens=4096,
        messages=[{'role': 'user', 'content': prompt}]
    )
    validated_content = message.content[0].text
    is_validated = 'verdict global : validé' in validated_content.lower()
    return validated_content, is_validated
    """
    # Placeholder : ajoute la section de validation avec un message indicatif
    if VALIDATION_SECTION not in content:
        validation_block = f"""

{VALIDATION_SECTION}

| Claim | Niveau de preuve | Verdict | Commentaires |
|-------|-----------------|---------|-------------|
| À FAIRE | à déterminer | En attente | À compléter par le Validateur pour {plant_name} |

**Verdict global :** En attente — revue manuelle requise.

**Corrections requises avant publication :**
- [ ] TODO : à lister par le validateur.
"""
        content = content + validation_block
    # Par défaut en mode placeholder : on valide (True)
    return content, True


def process_task(task: dict) -> dict:
    src_path = ROOT / task["file_path"]
    plant_name = task["plant_name"]

    if not src_path.exists():
        print(f"[VALIDATEUR][ERROR] Fichier introuvable : {src_path}")
        task["review_status"] = "error_file_not_found"
        return task

    content = src_path.read_text(encoding="utf-8")
    print(f"[VALIDATEUR] Validation de {src_path.name} ({plant_name})...")

    validated_content, is_validated = llm_validate(plant_name, content)

    if is_validated:
        new_status = "validated"
        next_agent = "archiviste"
        dest_dir = VALIDATED_DIR
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / src_path.name
        validated_content = update_front_matter_status(validated_content, new_status)
        validated_content = update_last_update(validated_content)
        src_path.write_text(validated_content, encoding="utf-8")
        shutil.move(str(src_path), str(dest_path))
        task["file_path"] = str(dest_path.relative_to(ROOT))
        print(f"[VALIDATEUR] {src_path.name} → validated/ | VALIDÉ (transmis à l'archiviste)")
        log_entry(f"Validé : drafts/{src_path.name} → validated/ | {plant_name}")
    else:
        new_status = "collecting"
        next_agent = "veilleur"
        INBOX_DIR.mkdir(parents=True, exist_ok=True)
        dest_path = INBOX_DIR / src_path.name
        validated_content = update_front_matter_status(validated_content, new_status)
        validated_content = update_last_update(validated_content)
        src_path.write_text(validated_content, encoding="utf-8")
        shutil.move(str(src_path), str(dest_path))
        task["file_path"] = str(dest_path.relative_to(ROOT))
        print(f"[VALIDATEUR] {src_path.name} → inbox/ | REJETÉ — retour au veilleur")
        log_entry(f"Rejeté : {src_path.name} → inbox/ | {plant_name} — retour au veilleur")

    task["current_agent"] = next_agent
    task["review_status"] = new_status
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
