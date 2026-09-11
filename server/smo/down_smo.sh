#!/usr/bin/env bash
# Derruba o SMO na ordem inversa da subida (simuladores → oam → common).
#   ./down_smo.sh            para e remove os contêineres (as imagens ficam)
#   ./down_smo.sh --limpar   idem + apaga a cópia de trabalho run/solution
#                            (a próxima subida refaz os ajustes do zero)
set -euo pipefail
cd "$(dirname "$0")"
. ./lib.sh

for (( i=${#CAMADAS[@]}-1; i>=0; i-- )); do
    camada="${CAMADAS[$i]}"
    [ -f "$RUN/$camada/docker-compose.yaml" ] || continue
    echo "== $camada =="
    dc "$camada" down
done

if [ "${1:-}" = --limpar ]; then
    rm -rf "$RUN"
    echo "cópia de trabalho apagada: $RUN"
fi
