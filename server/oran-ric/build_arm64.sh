#!/usr/bin/env bash
# Fase 2 (subconjunto A1-real): build ARM64 do dbaas + A1 Mediator da fonte.
# Retagueia com os NOMES nexus3 que o compose do professor espera — assim o
# vendor/oran-sc-ric + overlay dele rodam sem alteração quando chegar a hora.
# Runbook: docs/instalacao-nonrt-arm64.md §9
set -euo pipefail
cd "$(dirname "$0")"
A1_VER="${A1_VER:-3.2.2}"
DBAAS_VER="${DBAAS_VER:-0.6.4}"

mkdir -p src
[ -d src/a1 ] || git clone --depth 1 --branch "$A1_VER" https://github.com/o-ran-sc/ric-plt-a1 src/a1
[ -d src/dbaas ] || git clone --depth 1 --branch "$DBAAS_VER" https://github.com/o-ran-sc/ric-plt-dbaas src/dbaas

echo "== dbaas $DBAAS_VER (redis + redismodule + sdlcli) =="
docker build -f Dockerfile.dbaas -t "core5g/ric-plt-dbaas:${DBAAS_VER}-arm64" .
echo "== a1mediator $A1_VER (Go + RMR 4.9.4 da fonte — a parte demorada) =="
docker build -f Dockerfile.a1mediator -t "core5g/ric-plt-a1:${A1_VER}-arm64" .

# nomes que o vendor/oran-sc-ric + overlay do professor esperam:
docker tag "core5g/ric-plt-dbaas:${DBAAS_VER}-arm64" "nexus3.o-ran-sc.org:10002/o-ran-sc/ric-plt-dbaas:${DBAAS_VER}"
docker tag "core5g/ric-plt-a1:${A1_VER}-arm64" "nexus3.o-ran-sc.org:10002/o-ran-sc/ric-plt-a1:${A1_VER}"
docker images | grep -E 'core5g/ric-plt' && echo && echo "Próximo: ./up_oran_a1.sh && ./test_a1_real.sh"
