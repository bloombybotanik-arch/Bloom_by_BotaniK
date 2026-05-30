#!/usr/bin/env python3
"""
agent_maitre.py
---------------
Agent Maître — Arbitre les priorités, trie la queue, détecte les conflits
et surveille la cohérence long terme du pipeline Bloom.

Rôle :
  - Prioriser les fiches (lancement produit, saisonnalité, rangée)
  - Trier la queue agents_queue.json
  - Détecter les doublons ou conflits de version
  - Logger les décisions dans 07_LOGS/update_log.md
"""

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE_PATH = ROOT / "agents_queue.json"
LOG_PATH = ROOT / "07_LOGS" / "update_log.md"

# ---------------------------------------------------------------------------
# Priorités métier (personnalisable)
# Les plantes listées ici sont traitées en premier (priorité élevée = plus tôt)
# ---------------------------------------------------------------------------
HIGH_PRIORITY_PLANTS = [
    # Ajouter ici les noms de plantes stratégiques pour Bloom
    # ex : "ASHWAGANDHA", "REISHI", "LION'S MANE"
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
        f.write(f"\n- [{timestamp}] [MAITRE] {message}")


def assign_priority(task: dict) -> int:
    """Calcule la priorité d'une tâche (plus le score est bas, plus elle passe avant)."""
    plant = task.get("plant_name", "").upper()
    version = task.get("version", 1)
    status = task.get("review_status", "collecting")

    score = 100  # Score de base

    # Bonus priorité si plante stratégique
    for hp in HIGH_PRIORITY_PLANTS:
        if hp.upper() in plant:
            score -= 50
            break

    # Bonus si la fiche a déjà commencé la revue
    if status == "scientific_review":
        score -= 20
    elif status == "validated":
        score -= 30

    # Bonus pour les versions plus récentes (révision urgente)
    score -= min(version * 5, 25)

    return score


def detect_conflicts(queue: list) -> list:
    """Détecte les doublons de nom de plante dans la queue."""
    seen = {}
    conflicts = []
    for task in queue:
        name = task.get("plant_name", "")
        if name in seen:
            conflicts.append((name, seen[name]["file_path"], task["file_path"]))
        else:
            seen[name] = task
    return conflicts


def main():
    queue = load_queue()
    if not queue:
        print("[MAITRE] Queue vide. Rien à prioriser.")
        return

    # Détection de conflits
    conflicts = detect_conflicts(queue)
    for name, path1, path2 in conflicts:
        msg = f"CONFLIT de version détecté pour {name!r} : {path1} vs {path2}"
        print(f"[MAITRE][WARN] {msg}")
        log_entry(msg)

    # Affectation des priorités
    for task in queue:
        task["priority"] = assign_priority(task)

    # Tri par priorité (score le plus bas d'abord)
    queue.sort(key=lambda t: (t["priority"], t["plant_name"], t["version"]))

    save_queue(queue)

    print(f"[MAITRE] {len(queue)} tâche(s) priorisée(s) :")
    for i, task in enumerate(queue, 1):
        print(f"  {i}. [{task['priority']:3d}] {task['plant_name']} v{task['version']} — {task['current_agent']} — {task['review_status']}")

    log_entry(f"Priorisation complète — {len(queue)} tache(s) dans la queue.")


if __name__ == "__main__":
    main()
