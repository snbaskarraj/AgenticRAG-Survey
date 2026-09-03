#!/usr/bin/env bash
set -euo pipefail

# Always run from this project folder, whether you call
#   ./run.sh
# or
#   cd everpuresep32026 && ./run.sh
cd "$(dirname "$0")"
export PATH="${HOME}/.local/bin:${PATH}"
export PYTHONPATH="${PWD}/src${PYTHONPATH:+:$PYTHONPATH}"
PORT="${PORT:-8501}"
URL="http://localhost:${PORT}"

if ! python3 -c "import streamlit, pandas" >/dev/null 2>&1; then
  python3 -m pip install --user --break-system-packages -r requirements.txt
fi

if python3 - "$PORT" <<'PY'
import sys, urllib.request
port = sys.argv[1]
try:
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1) as resp:
        sys.exit(0 if resp.status == 200 else 1)
except Exception:
    sys.exit(1)
PY
then
  echo "Chat UI is already running at ${URL}"
  echo "Open that URL and ask: What was the revenue in Q1 FY2026?"
  exit 0
fi

echo "Starting chat UI at ${URL}"
exec python3 -m streamlit run app.py --server.headless true --server.port "${PORT}"
