#!/bin/bash
# Para o Core OAI 5G v2.2.1. NÃO toca no Projeto 1 (open5gs-*).
# Uso: ./down_core_v2.sh
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
docker compose -f docker-compose-basic-nrf.yaml down
echo "Core v2.2.1 parado. Rollback p/ v1.5.1: ../scripts/up_core.sh"
