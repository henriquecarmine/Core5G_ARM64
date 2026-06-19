#!/bin/bash
# Sobe o painel de controle local em http://127.0.0.1:8765
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt

echo "Painel disponível em: http://127.0.0.1:8765"
exec uvicorn server:app --host 127.0.0.1 --port 8765
