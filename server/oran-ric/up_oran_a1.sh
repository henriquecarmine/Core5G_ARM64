#!/usr/bin/env bash
# Sobe o subconjunto A1-real da Fase 2: dbaas + A1 Mediator.
set -euo pipefail
cd "$(dirname "$0")"
docker compose up -d
echo "A1 Mediator: http://localhost:${A1MEDIATOR_HOST_PORT:-10000}/a1-p/healthcheck"
echo "Smoke: ./test_a1_real.sh"
