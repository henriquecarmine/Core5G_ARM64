#!/bin/bash
# Script para iniciar o Core OAI (5G CN)
# Uso: ./scripts/up_core.sh
#
# ARM64: oai-upf-vpp é Intel-only (amd64) e nunca fica healthy neste servidor.
# Aguardamos oai-amf healthy (suficiente para E2: gNB conecta via N2/NGAP).

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_DIR="$PROJECT_DIR/oai-cn5g-fed/docker-compose"

echo "=========================================="
echo "Iniciando Core OAI (5G CN)"
echo "=========================================="
echo ""

if ! docker info > /dev/null 2>&1; then
    echo "ERRO: Docker não está rodando."
    exit 1
fi

if [ ! -d "$COMPOSE_DIR" ]; then
    echo "ERRO: Diretório não encontrado: $COMPOSE_DIR"
    exit 1
fi

if [ ! -f "$COMPOSE_DIR/core-network.py" ]; then
    echo "ERRO: core-network.py não encontrado em $COMPOSE_DIR"
    exit 1
fi

echo "Habilitando IP forwarding..."
sudo sysctl -w net.ipv4.ip_forward=1 2>/dev/null || true
sudo sysctl -w net.ipv6.conf.all.forwarding=1 2>/dev/null || true
sudo iptables -P FORWARD ACCEPT 2>/dev/null || true

echo ""
echo "Iniciando containers OAI (AMF, SMF, NRF, UDM, UDR, AUSF, MySQL, DN)..."
cd "$COMPOSE_DIR"

# Roda em background — core-network.py fica monitorando healthchecks indefinidamente.
# No ARM64, oai-upf-vpp (AMD64-only) nunca fica healthy; encerramos quando AMF subir.
python3 core-network.py --type start-basic-vpp --scenario 1 &
NETPY_PID=$!

echo "Aguardando oai-amf healthy (max 120s)..."
WAITED=0
while [ "$WAITED" -lt 120 ]; do
    STATUS=$(docker inspect -f '{{.State.Health.Status}}' oai-amf 2>/dev/null || echo "missing")
    [ "$STATUS" = "healthy" ] && break
    sleep 3
    WAITED=$((WAITED + 3))
done

kill "$NETPY_PID" 2>/dev/null || true

STATUS=$(docker inspect -f '{{.State.Health.Status}}' oai-amf 2>/dev/null || echo "missing")
if [ "$STATUS" != "healthy" ]; then
    echo "ERRO: oai-amf não ficou healthy após ${WAITED}s (estado: $STATUS)"
    exit 1
fi

echo ""
docker ps --filter "name=oai-" --filter "name=mysql" \
    --format 'table {{.Names}}\t{{.Status}}'

echo ""
echo "=========================================="
echo "Core OAI pronto (CP healthy; UPF-VPP ignorado no ARM64)"
echo "=========================================="
echo ""
echo "Proximo passo: ./scripts/up_e2_lab.sh"
echo ""
