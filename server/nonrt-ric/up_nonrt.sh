#!/usr/bin/env bash
# Sobe o nonRT RIC (par mínimo A1): PMS + 3 A1 Simulators.
# Pré-requisito: imagens construídas com ./build_arm64.sh
set -euo pipefail
cd "$(dirname "$0")"

command -v docker >/dev/null || { echo "ERRO: docker não encontrado." >&2; exit 1; }
docker image inspect "core5g/nonrt-a1pms:${PMS_TAG:-2.9.0}-arm64" >/dev/null 2>&1 || {
    echo "ERRO: imagem do PMS não existe — rode ./build_arm64.sh primeiro." >&2; exit 1; }

docker compose up -d
echo
echo "Aguardando o PMS ficar healthy (Spring Boot sobe em ~10–30 s no Graviton)…"
for i in $(seq 1 30); do
    st="$(docker inspect -f '{{.State.Health.Status}}' nonrt-policy-agent 2>/dev/null || echo starting)"
    [ "$st" = "healthy" ] && break
    sleep 5
done
echo "PMS: ${st:-desconhecido}"
echo
echo "Endpoints:"
echo "  PMS          http://localhost:${NONRT_PMS_HTTP_PORT:-8081}/a1-policy/v2/status"
echo "  a1-sim-OSC   http://localhost:30001/  (A1 OSC_2.1.0)"
echo "  a1-sim-STD   http://localhost:30003/  (A1 STD_1.1.3)"
echo "  a1-sim-STDv2 http://localhost:30005/  (A1 STD_2.0.0)"
echo
echo "Smoke ponta a ponta: ./test_a1_flow.sh"
