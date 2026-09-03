#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="${HOME}/.local/bin:${PATH}"
export PYTHONPATH="${PWD}/src${PYTHONPATH:+:$PYTHONPATH}"

if ! python3 -c "import streamlit, pandas" >/dev/null 2>&1; then
  python3 -m pip install --user --break-system-packages -r requirements.txt
fi

exec python3 -m streamlit run app.py --server.headless true --server.port 8501
