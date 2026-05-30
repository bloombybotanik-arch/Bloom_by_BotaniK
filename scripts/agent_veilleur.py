#!/usr/bin/env python3
"""
agent_veilleur.py  (alias agent1_veille)
-----------------------------------------
Agent 1 — Veilleur Botanique.

Flux séquentiel : inbox/ → [enrichissement] → drafts/

Rôle :
  - Lit les fiches en statut 'collecting' dans la queue
  - Enrichit le brouillon via Claude (ANTHROPIC_API_KEY) :
      * Sources et références botaniques
      * Actifs principaux et molécules clés
      * Synergies entre plantes
      * Signaux faibles (controverses, lacunes, risques)
      * Angles de vigilance (contre-indications, populations à risque)
  - Déplace le fichier enrichi de inbox/ vers drafts/
  - Met à jour review_status → 'scientific_review'
  - Route vers l'agent validateur (agent 2)
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

INBOX_DIR  = ROOT / "02_LIBRARY" / "plants" / "inbox"
DRAFTS_DIR = ROOT / "02_LIBRARY" / "plants" / "drafts"

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
    pattern = r'(review_status:\s*)[^\n]+'
    if re.search(pattern, content):
        return re.sub(pattern, f'\\g<1>{new_status}', content)
    return content.replace('---\n', f'---\nreview_status: {new_status}\n', 1)


def update_last_update(content: str) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    pattern = r'(last_update:\s*)[^\n]+'
    if re.search(pattern, content):
        return re.sub(pattern, f'\\g<1>{today}', content)
    return content


def llm_enrich(plant_name: str, content: str) -> str:
    """
    POINT D'INTÉGRATION CLAUDE — enrichissement botanique via API Anthropic.

    Pour activer : décommenter le bloc ci-dessous et ajouter ANTHROPIC_API_KEY
    dans les secrets GitHub (Settings > Secrets and variables > Actions).

    import anthropic
    client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
    prompt = f'''
    Tu es un expert botaniste. Voici une fiche plante en cours de rédaction :

    {content}

    Complète les sections suivantes pour la plante {plant_name} :
    - Actifs principaux (molécules, concentrations)
    - Synergies (plantes et actifs compatibles)
    - Signaux faibles (controverses, lacunes, risques émergents)
    - Angles de vigilance (contre-indications, interactions)
    - Sources (références PubMed, pharmacopées)

    Retourne la fiche complète en Markdown.
    '''
    message = client.messages.create(
        model='claude-opus-4-5',
        max_tokens=4096,
        messages=[{'role': 'user', 'content': prompt}]
    )
    return message.content[0].text
    """
    # Placeholder : ajoute les sections manquantes avec un marqueur TODO
    enriched = content
    for section in VEILLEUR_SECTIONS:
        if section not in enriched:
            enriched += f"\n\n{section}\n\n> TODO — À enrichir par le Veilleur Botanique (Claude) pour {plant_name}.\n"
    return enriched


def process_task(task: dict) -> dict:
    src_path = ROOT / task["file_path"]
    plant_name = task["plant_name"]

    if not src_path.exists():
        print(f"[VEILLEUR][ERROR] Fichier introuvable : {src_path}")
        task["review_status"] = "error_file_not_found"
        return task

    content = src_path.read_text(encoding="utf-8")
    print(f"[VEILLEUR] Enrichissement de {src_path.name} ({plant_name})...")

    # Enrichissement via Claude (ou placeholder)
    enriched = llm_enrich(plant_name, content)
    enriched = update_front_matter_status(enriched, "scientific_review")
    enriched = update_last_update(enriched)

    # Déplacement inbox/ → drafts/
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    dest_path = DRAFTS_DIR / src_path.name
    src_path.write_text(enriched, encoding="utf-8")
    shutil.move(str(src_path), str(dest_path))

    # Mise à jour de la queue
    task["file_path"] = str(dest_path.relative_to(ROOT))
    task["current_agent"] = "validateur"
    task["review_status"] = "scientific_review"

    log_entry(f"Enrichi + déplacé : inbox/{src_path.name} → drafts/ | {plant_name} → scientific_review")
    print(f"[VEILLEUR] {src_path.name} → drafts/ | scientific_review (transmis au validateur)")
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
