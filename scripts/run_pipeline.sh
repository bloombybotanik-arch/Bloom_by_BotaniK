#!/usr/bin/env bash
# =============================================================================
# run_pipeline.sh — Pipeline complet Bloom by BotaniK
# =============================================================================
# Usage :
#   ./scripts/run_pipeline.sh
#   ou via GitHub Actions / cron
#
# Ordre d'exécution :
#   1. scan_bloom_fiches.py  → détecte les nouvelles fiches et génère la queue
#   2. agent_maitre.py       → priorise les tâches dans la queue
#   3. agent_veilleur.py     → enrichit les brouillons
#   4. agent_validateur.py   → valide scientifiquement
#   5. agent_archiviste.py   → publie en active/ et archive les anciennes versions
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"

echo "======================================="
echo " BLOOM PIPELINE — $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "======================================="

# --- Vérification Python ---
if ! command -v python3 &>/dev/null; then
  echo "[ERROR] python3 non trouvé. Installez Python 3.9+."
  exit 1
fi

# --- Installation des dépendances minimales ---
python3 -m pip install --quiet pyyaml 2>/dev/null || true

cd "$ROOT"

# --- Étape 1 : Scan de l'inbox ---
echo ""
echo "[STEP 1/5] Scan de l'inbox..."
python3 scripts/scan_bloom_fiches.py

# --- Étape 2 : Agent maître (priorisation) ---
echo ""
echo "[STEP 2/5] Agent maître — priorisation de la queue..."
python3 scripts/agent_maitre.py

# --- Étape 3 : Agent veilleur ---
echo ""
echo "[STEP 3/5] Agent veilleur — enrichissement botanique..."
python3 scripts/agent_veilleur.py

# --- Étape 4 : Agent validateur ---
echo ""
echo "[STEP 4/5] Agent validateur — classification des preuves..."
python3 scripts/agent_validateur.py

# --- Étape 5 : Agent archiviste ---
echo ""
echo "[STEP 5/5] Agent archiviste — publication et archivage..."
python3 scripts/agent_archiviste.py

echo ""
echo "[DONE] Pipeline terminé — $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "  - Fiches actives : 02_LIBRARY/plants/active/"
echo "  - Fiches archivées : 08_ARCHIVE/retired_plant_fiches/"
echo "  - Logs : 07_LOGS/update_log.md"
echo "  - Queue restante : agents_queue.json"
