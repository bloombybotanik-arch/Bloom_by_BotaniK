#!/usr/bin/env python3
"""
agent_veilleur.py
-----------------
Agent 1 — Veilleur Botanique.

Rôle :
  - Lire les fiches en statut 'collecting' dans la queue
  - Enrichir le brouillon avec :
      * Sources et références botaniques
      * Actifs principaux et molécules clés
      * Synergies entre plantes
      * Signaux faibles (controverses, lacunes, risques)
      * Angles de vigilance (contre-indications, populations à risque)
  - Mettre à jour review_status → 'scientific_review'
  - Router vers l'agent validateur (agent 2)

NOTE : Le bloc LLM_CALL est le point d'intégration avec votre modèle AI
       (Claude, GPT-4, Gemini, etc.). Remplacez le placeholder par votre appel API.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE_PATH = ROOT / "agents_queue.json"
LOG_PATH = ROOT / "07_LOGS" / "update_log.md"

# Sections attendues dans une fiche enrichie
VEILLEUR_SECTIONS = [
    "## Actifs principaux",
    "## Synergies",
    "## Signaux faibles",
    "## Angles de vigilance",
    "## Sources",
]


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
        f.write(f"\n- [{timestamp}] [VEILLEUR] {message}")


def update_front_matter_status(content: str, new_status: str) -> str:
    """Met à jour le champ review_status dans le front-matter YAML."""
    pattern = r'(review_status:\s*)[^\n]+'
    replacement = f'\\g<1>{new_status}'
    if re.search(pattern, content):
        return re.sub(pattern, replacement, content)
    # Si le champ n'existe pas, on l'ajoute juste avant la fermeture ---
    return content.replace('---\n', f'---\nreview_status: {new_status}\n', 1)


def update_last_update(content: str) -> str:
    """Met à jour le champ last_update dans le front-matter."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    pattern = r'(last_update:\s*)[^\n]+'
    replacement = f'\\g<1>{today}'
    if re.search(pattern, content):
        return re.sub(pattern, replacement, content)
    return content


def llm_enrich(plant_name: str, content: str) -> str:
    """
    POINT D'INTÉGRATION LLM — à remplacer par votre appel API réel.

    Entrepté :
      plant_name : nom de la plante (ex: "CANNABIS SATIVA")
      content    : contenu Markdown actuel de la fiche

    Retour :
      Contenu Markdown enrichi avec les sections veilleur.

    Exemple d'intégration Claude :
      import anthropic
      client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
      message = client.messages.create(
          model="claude-opus-4-5",
          max_tokens=4096,
          messages=[{"role": "user", "content": prompt}]
      )
      return message.content[0].text
    """
    # Placeholder : ajoute les sections manquantes avec un message indicatif
    enriched = content
    for section in VEILLEUR_SECTIONS:
        if section not in enriched:
            enriched += f"\n\n{section}\n\n> TODO — à compléter par le Veilleur Botanique pour {plant_name}.\n"
    return enriched


def process_task(task: dict) -> dict:
    file_path = ROOT / task["file_path"]
    plant_name = task["plant_name"]

    if not file_path.exists():
        print(f"[VEILLEUR][ERROR] Fichier introuvable : {file_path}")
        task["review_status"] = "error_file_not_found"
        return task

    content = file_path.read_text(encoding="utf-8")
    print(f"[VEILLEUR] Enrichissement de {file_path.name} ({plant_name})...")

    # Enrichissement via LLM (ou placeholder)
    enriched = llm_enrich(plant_name, content)

    # Mise à jour du statut et de la date
    enriched = update_front_matter_status(enriched, "scientific_review")
    enriched = update_last_update(enriched)

    file_path.write_text(enriched, encoding="utf-8")

    task["current_agent"] = "validateur"
    task["review_status"] = "scientific_review"

    log_entry(f"Enrichi : {file_path.name} | {plant_name} → scientific_review")
    print(f"[VEILLEUR] {file_path.name} → scientific_review (transmis au validateur)")
    return task


def main():
    queue = load_queue()
    if not queue:
        print("[VEILLEUR] Queue vide.")
        return

    updated = False
    for i, task in enumerate(queue):
        if task.get("current_agent") != "veilleur":
            continue
        if task.get("review_status") in ("schema_error", "error_file_not_found"):
            print(f"[VEILLEUR][SKIP] {task['file_path']} (statut : {task['review_status']})")
            continue
        queue[i] = process_task(task)
        updated = True

    if updated:
        save_queue(queue)
    else:
        print("[VEILLEUR] Aucune fiche à traiter.")


if __name__ == "__main__":
    main()
