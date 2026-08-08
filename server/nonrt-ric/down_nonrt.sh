#!/usr/bin/env bash
# Para e remove o nonRT RIC (containers + rede; imagens ficam).
set -euo pipefail
cd "$(dirname "$0")"
docker compose down
