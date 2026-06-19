#!/bin/bash
# Teste de throughput real UE -> DN via iperf3, atravessando o túnel 5G
# de verdade (UE -> gNB -> UPF -> DN), não o bridge direto do Docker.
# Tema do grupo (UE-TP-rApp) é previsão de throughput por UE — esta é a
# medição real que alimentaria esse modelo.
# Uso: ./scripts/test_throughput.sh [duracao_segundos]

set -e

DURATION="${IPERF_DURATION:-${1:-10}}"
DN_CONTAINER="open5gs-dn-containerized"
DN_IP="10.50.0.100"
UE_CONTAINER="ueransim"

echo "=========================================="
echo "Teste de Throughput (iperf3) — UE -> DN"
echo "=========================================="
echo ""

UE_IP="$(docker exec "$UE_CONTAINER" sh -c "ip -4 addr show uesimtun0 2>/dev/null | grep -oE '([0-9]+\.){3}[0-9]+' | head -1")"
if [ -z "$UE_IP" ]; then
    echo "ERRO: interface uesimtun0 não encontrada — o UE está registrado com sessão PDU ativa?"
    exit 1
fi
echo "UE IP (uesimtun0): $UE_IP"
echo "Destino (DN): $DN_IP"
echo ""

docker exec -d "$DN_CONTAINER" sh -c "iperf3 -s -1 -p 5201 > /tmp/iperf3-server.log 2>&1"
sleep 1

echo "Rodando iperf3 por ${DURATION}s..."
echo ""
docker exec "$UE_CONTAINER" iperf3 -c "$DN_IP" -p 5201 -B "$UE_IP" -t "$DURATION"

echo ""
echo "=========================================="
echo "Teste concluído."
echo "=========================================="
