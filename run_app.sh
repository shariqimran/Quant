#!/usr/bin/env bash
# Run from repo root. Optional: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
if [[ -f "${SCRIPT_DIR}/.venv/bin/activate" ]]; then
  # shellcheck source=/dev/null
  source "${SCRIPT_DIR}/.venv/bin/activate"
fi
exec streamlit run app.py "$@"
