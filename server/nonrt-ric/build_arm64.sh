#!/usr/bin/env bash
# Build NATIVO (aarch64) das imagens do nonRT RIC — par mínimo A1:
#   core5g/nonrt-a1pms:<tag>-arm64   (A1 Policy Management Service, Java)
#   core5g/nonrt-a1sim:<tag>-arm64   (A1 Simulator near-RT, Python)
#
# Passo a passo completo: docs/instalacao-nonrt-arm64.md
# Rode NO SERVIDOR Graviton (ou em qualquer arm64 com Docker). ~5–10 min na
# primeira vez (Maven baixa dependências); builds seguintes usam cache.
set -euo pipefail
cd "$(dirname "$0")"

PMS_TAG="${PMS_TAG:-2.9.0}"    # versão validada em docs/non-rt-ric.md §4.2
SIM_TAG="${SIM_TAG:-2.8.0}"

ARCH="$(uname -m)"
if [ "$ARCH" != "aarch64" ] && [ "$ARCH" != "arm64" ]; then
    echo "AVISO: arquitetura $ARCH — as imagens sairão para a arquitetura local," >&2
    echo "não para o servidor Graviton. Prossiga só se for intencional." >&2
fi
command -v docker >/dev/null || { echo "ERRO: docker não encontrado." >&2; exit 1; }

# Fontes pinadas por tag (shallow). Para trocar de versão: rm -rf src/ e
# PMS_TAG=x.y.z SIM_TAG=a.b.c ./build_arm64.sh
mkdir -p src
[ -d src/a1pms ] || git clone --depth 1 --branch "$PMS_TAG" \
    https://github.com/o-ran-sc/nonrtric-plt-a1policymanagementservice src/a1pms
[ -d src/a1sim ] || git clone --depth 1 --branch "$SIM_TAG" \
    https://github.com/o-ran-sc/sim-a1-interface src/a1sim

echo "== build A1 PMS ${PMS_TAG} (Maven + jlink; a demora é aqui) =="
docker build -f Dockerfile.a1pms --build-arg PMS_TAG="$PMS_TAG" \
    -t "core5g/nonrt-a1pms:${PMS_TAG}-arm64" .

echo "== build A1 Simulator ${SIM_TAG} (Dockerfile oficial; alpine é multi-arch) =="
docker build -t "core5g/nonrt-a1sim:${SIM_TAG}-arm64" src/a1sim/near-rt-ric-simulator

echo
echo "== imagens geradas =="
docker images --format '{{.Repository}}:{{.Tag}}  {{.Size}}  ({{.Architecture}})' 2>/dev/null \
    | grep core5g/nonrt || docker images | grep core5g/nonrt
echo
echo "Próximo passo: ./up_nonrt.sh  (depois ./test_a1_flow.sh)"
