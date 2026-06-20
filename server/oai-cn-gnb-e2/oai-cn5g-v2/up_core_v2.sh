#!/bin/bash
# Sobe o Core OAI 5G v2.2.1 (imagens oficiais multi-arch arm64) com UPF real (oai-upf,
# datapath simple_switch). Substitui o core v1.5.1 control-plane-only.
#
# Uso: ./up_core_v2.sh
#
# IMPORTANTE: remove o core OAI v1.5.1 antes de subir (mesmos nomes de container
# oai-amf/mysql e mesmo bridge demo-oai). NÃO toca no Projeto 1 (open5gs-*).

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[0/4] EXCLUSÃO MÚTUA: parando Projeto 1 (Open5GS/UERANSIM) — box tem 2 vCPUs..."
docker ps --format '{{.Names}}' | grep -iE 'open5gs|ueransim' | xargs -r docker stop >/dev/null 2>&1 || true
sudo pkill -9 -f mongosh 2>/dev/null || true

echo "[1/4] Removendo core OAI v1.5.1 (containers oai-*/mysql)..."
docker ps -a --format '{{.Names}}' | grep -E '^(oai-|mysql$)' | grep -viE 'open5gs' | xargs -r docker rm -f >/dev/null 2>&1 || true

echo "[2/4] Removendo redes OAI antigas em conflito (bridge demo-oai)..."
docker network ls --format '{{.Name}}' | grep -iE 'oai|demo-oai' | grep -viE 'open5gs' \
    | xargs -r -I{} docker network rm {} >/dev/null 2>&1 || true

echo "[3/4] Habilitando IP forwarding (N6/SNAT do UPF)..."
sudo sysctl -w net.ipv4.ip_forward=1 >/dev/null 2>&1 || true

echo "[4/4] Subindo core v2.2.1 (pull automático das imagens arm64)..."
docker compose -f docker-compose-basic-nrf.yaml up -d

echo "Aguardando oai-amf healthy (max 120s)..."
for _ in $(seq 1 40); do
    st=$(docker inspect -f '{{.State.Health.Status}}' oai-amf 2>/dev/null || echo missing)
    [ "$st" = "healthy" ] && break
    sleep 3
done
echo ""
docker compose -f docker-compose-basic-nrf.yaml ps
echo ""
echo "Validar associação PFCP/N4 SMF<->UPF:"
echo "  docker logs oai-smf 2>&1 | grep -iE 'association|pfcp|upf'"
echo "  docker logs oai-upf 2>&1 | grep -iE 'association|pfcp|datapath'"
echo "Depois subir o E2 lab (RIC+gNB) normalmente: ../scripts/up_e2_lab.sh"
echo "Rollback p/ v1.5.1: ./down_core_v2.sh && ../scripts/up_core.sh"
