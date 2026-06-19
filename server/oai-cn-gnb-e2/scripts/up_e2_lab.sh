#!/bin/bash
# Sobe laboratório completo: Core OAI + nearRT-RIC + gNB E2 + nrUE.
# Uso: ./scripts/up_e2_lab.sh
#
# Requer gNB compilado com E2: ./scripts/build_e2.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo "Laboratório E2: Core + FlexRIC + gNB + UE"
echo "=========================================="
echo ""

# 1. Core
if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -qE '^oai-amf$'; then
    echo "[1/4] Iniciando Core OAI..."
    "$SCRIPT_DIR/up_core.sh"
else
    echo "[1/4] Core OAI já em execução."
fi

# 1.5 — Liberar RAM para o gNB (binário C++ precisa de ~150 MB físicos ao iniciar).
# t4g.micro = 906 MB: OAI Core swapia ~600 MB, sobrando apenas ~40 MB livres.
# Paramos containers não-essenciais para E2 (gNB precisa só de AMF+NRF+SMF),
# depois reiniciamos em background enquanto gNB inicializa.
AVAIL_MB=$(awk '/MemAvailable/ {printf "%d", $2/1024}' /proc/meminfo 2>/dev/null || echo 999)
MEM_OK=1
if [ "$AVAIL_MB" -lt 200 ]; then
    MEM_OK=0
    echo ""
    echo "[1.5/4] Memória: ${AVAIL_MB}MB livres — parando containers não-essenciais para liberar RAM..."
    for c in oai-ext-dn oai-ausf oai-udm oai-udr mysql; do
        docker stop "$c" 2>/dev/null && printf '  parado: %s\n' "$c" || true
    done
    sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches' 2>/dev/null || true
    sleep 5
    AVAIL_MB=$(awk '/MemAvailable/ {printf "%d", $2/1024}' /proc/meminfo)
    echo "  Memória após liberação: ${AVAIL_MB}MB"
fi

# 2. nearRT-RIC
echo ""
echo "[2/4] Iniciando nearRT-RIC..."
"$SCRIPT_DIR/up_flexric.sh"

# 3. gNB + UE (com E2 agent)
echo ""
echo "[3/4] Iniciando gNB OAI + nrUE (E2 agent → 127.0.0.1)..."
"$SCRIPT_DIR/up_gnb_oai.sh"

# 3.5 — Restaurar containers parados para autenticação do UE
if [ "$MEM_OK" -eq 0 ]; then
    echo ""
    echo "[3.5/4] gNB ativo — reativando containers de auth/dados em background..."
    (
        for c in mysql oai-udr oai-udm oai-ausf oai-ext-dn; do
            docker start "$c" 2>/dev/null || true
            sleep 3
        done
    ) &
fi

# 4. Aguardar registro UE
echo ""
echo "[4/4] Aguardando UE registrar (45s, containers auth voltam a subir)..."
sleep 45

echo ""
echo "=========================================="
echo "Laboratório E2 pronto"
echo "=========================================="
echo ""
echo "Verificar E2 setup nos logs do gNB:"
echo "  grep -iE 'E2|RIC|setup' ${OAI_LOG_DIR:-$PROJECT_DIR/logs}/gnb_oai.log"
echo ""
echo "Testar Service Models:"
echo "  ./scripts/test_e2_sm.sh cust    # MAC/RLC/PDCP/GTP (recomendado com slice 222/123)"
echo "  ./scripts/test_e2_sm.sh oran    # KPM + RC (KPM exige slice SST=1)"
echo "  ./scripts/test_e2_sm.sh all"
echo ""
echo "Parar: ./scripts/down_e2_lab.sh"
