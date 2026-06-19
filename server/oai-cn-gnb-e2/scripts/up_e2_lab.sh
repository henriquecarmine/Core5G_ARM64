#!/bin/bash
# Sobe laboratório E2: nearRT-RIC + gNB OAI (com E2 agent) + Core OAI + nrUE.
# Uso: ./scripts/up_e2_lab.sh
#
# Requer gNB compilado com E2: ./scripts/build_e2.sh
#
# RÁDIO: usa 51 PRBs (20 MHz) por padrão — o gNB RFSIM em 106 PRBs satura os
#   2 vCPUs do t4g.medium (load >15) e derruba o tempo de resposta do Core.
#   Em 51 PRBs a CPU do gNB cai de ~200% para ~8%, deixando o Core e o RIC
#   rodarem JUNTOS de forma estável. Override: GNB_CONF_PATH/GNB_NRB no ambiente.
#
# MEMÓRIA: a partir do t4g.medium (3,7 GB) o Core completo + gNB + RIC cabem
#   juntos com folga, então o lab NÃO derruba mais o Core (modo "full").
#   Em instâncias pequenas (<1,5 GB livre) cai no modo "lite": para o Core,
#   omite o nrUE e sobe só AMF+NRF em background (comportamento antigo).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="${OAI_LOG_DIR:-$PROJECT_DIR/logs}"

echo "=========================================="
echo "Laboratório E2: RIC + gNB + Core OAI + UE"
echo "=========================================="
echo ""

# Config de rádio: 51 PRBs por padrão (CPU baixa, cabe em 2 vCPUs).
GNB_CONF_24="${SCRIPT_DIR}/gnb_24prb.conf"
if [ -z "${GNB_CONF_PATH:-}" ] && [ -f "$GNB_CONF_24" ]; then
    export GNB_CONF_PATH="$GNB_CONF_24"
    export GNB_NRB=51
    export GNB_DL_FREQ=3469440000   # 51 PRBs band 78, Point A=630684
fi

AVAIL_MB=$(awk '/MemAvailable/ {printf "%d", $2/1024}' /proc/meminfo 2>/dev/null || echo 0)
echo "RAM disponível: ${AVAIL_MB} MB"

if [ "$AVAIL_MB" -ge 1500 ]; then
    # ---------- MODO FULL (t4g.medium ou maior) ----------
    echo "Modo FULL: Core completo + gNB + RIC + UE juntos (RAM suficiente)."
    echo ""
    echo "[1/3] Garantindo Core OAI completo no ar..."
    if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -q '^oai-amf$'; then
        "$SCRIPT_DIR/up_core.sh"
    else
        echo "  Core já está rodando."
    fi

    echo ""
    echo "[2/3] Iniciando nearRT-RIC..."
    "$SCRIPT_DIR/up_flexric.sh"

    echo ""
    echo "[3/3] Iniciando gNB OAI + nrUE (E2 agent → 127.0.0.1, 51 PRBs)..."
    "$SCRIPT_DIR/up_gnb_oai.sh"
else
    # ---------- MODO LITE (instância pequena, <1,5 GB livre) ----------
    echo "Modo LITE: RAM baixa — Core parado, nrUE omitido, só AMF+NRF em bg."
    export SKIP_UE=1

    echo ""
    echo "[1/4] Parando containers OAI (liberar RAM para nr-softmodem)..."
    RUNNING_OAI=$(docker ps --format '{{.Names}}' 2>/dev/null | grep -E 'oai-|mysql|vpp-upf' || true)
    if [ -n "$RUNNING_OAI" ]; then
        echo "$RUNNING_OAI" | xargs docker stop 2>/dev/null | xargs -I{} echo "  parado: {}" || true
    else
        echo "  (nenhum container OAI rodando)"
    fi
    sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches' 2>/dev/null || true
    sleep 3

    echo ""
    echo "[2/4] Iniciando nearRT-RIC..."
    "$SCRIPT_DIR/up_flexric.sh"

    echo ""
    echo "[3/4] Iniciando gNB OAI (E2 agent → 127.0.0.1, 51 PRBs)..."
    "$SCRIPT_DIR/up_gnb_oai.sh"

    echo ""
    echo "[4/4] Subindo AMF e NRF em background (gNB registra via N2)..."
    (
        docker start oai-nrf 2>/dev/null
        for _ in $(seq 1 15); do
            STATUS=$(docker inspect -f '{{.State.Health.Status}}' oai-nrf 2>/dev/null || echo missing)
            [ "$STATUS" = "healthy" ] && break
            sleep 2
        done
        docker start oai-amf 2>/dev/null
        echo "AMF e NRF iniciados" >> "$LOG_DIR/up_core_bg.log"
    ) &

    echo ""
    echo "Aguardando AMF subir (30s)..."
    sleep 30
fi

echo ""
echo "=========================================="
echo "Laboratório E2 pronto"
echo "=========================================="
echo ""
echo "Containers OAI:"
docker ps --format 'table {{.Names}}\t{{.Status}}' 2>/dev/null | grep -E 'oai-|mysql|NAME' || true
echo ""
echo "Verificar E2 setup nos logs do gNB:"
echo "  grep -iE 'E2|RIC|setup' $LOG_DIR/gnb_oai.log"
echo ""
echo "Testar Service Models:"
echo "  ./scripts/test_e2_sm.sh cust    # MAC/RLC/PDCP/GTP (recomendado com slice 222/123)"
echo "  ./scripts/test_e2_sm.sh oran    # KPM + RC (KPM exige slice SST=1)"
echo "  ./scripts/test_e2_sm.sh all"
echo ""
echo "Parar: ./scripts/down_e2_lab.sh"
