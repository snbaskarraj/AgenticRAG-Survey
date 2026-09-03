#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="${HOME}/.local/bin:${PATH}"
export PYTHONPATH="${PWD}/src${PYTHONPATH:+:$PYTHONPATH}"
PORT="${GRADIO_PORT:-7860}"
URL="http://localhost:${PORT}"

if ! python3 -c "import gradio, pandas" >/dev/null 2>&1; then
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
  echo "Gradio chat UI is already running at ${URL}"
  exit 0
fi

echo "Starting Gradio chat UI at ${URL}"
exec python3 gradio_app.py
