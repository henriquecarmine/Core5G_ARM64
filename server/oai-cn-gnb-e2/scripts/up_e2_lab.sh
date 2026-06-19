#!/bin/bash
# Sobe laboratório E2: nearRT-RIC + gNB OAI (com E2 agent) + Core OAI + nrUE.
# Uso: ./scripts/up_e2_lab.sh
#
# Requer gNB compilado com E2: ./scripts/build_e2.sh
#
# ESTRATÉGIA DE MEMÓRIA (t4g.micro = 906 MB RAM):
#   nr-softmodem aloca 710 MB RSS ao inicializar (buffers IQ para 106 RBs @ 30 kHz).
#   OAI Core (8 containers C++) mais nearRT-RIC consomem ~300 MB adicionais.
#   Solução: inicia gNB + RIC PRIMEIRO (com containers parados), depois sobe
#   o Core em background. gNB reconecta ao AMF automaticamente quando ele sobe.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="${OAI_LOG_DIR:-$PROJECT_DIR/logs}"

echo "=========================================="
echo "Laboratório E2: RIC + gNB + Core OAI + UE"
echo "=========================================="
echo ""

# 1. Parar todos os containers OAI para liberar RAM ao gNB
echo "[1/4] Parando containers OAI (liberar ~300 MB para nr-softmodem)..."
RUNNING_OAI=$(docker ps --format '{{.Names}}' 2>/dev/null | grep -E 'oai-|mysql|vpp-upf' || true)
if [ -n "$RUNNING_OAI" ]; then
    echo "$RUNNING_OAI" | xargs docker stop 2>/dev/null | xargs -I{} echo "  parado: {}" || true
else
    echo "  (nenhum container OAI rodando)"
fi
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches' 2>/dev/null || true
sleep 3
AVAIL_MB=$(awk '/MemAvailable/ {printf "%d", $2/1024}' /proc/meminfo 2>/dev/null || echo 0)
echo "  RAM disponível: ${AVAIL_MB} MB (gNB precisa de ~710 MB)"
if [ "$AVAIL_MB" -lt 700 ]; then
    echo "  AVISO: menos de 700 MB disponíveis — gNB pode falhar por OOM."
    echo "         Para fix definitivo: upgrade para t4g.small (2 GB RAM)."
fi

# 2. nearRT-RIC (leve, ~80 MB; inicia antes do gNB para E2 setup imediato)
echo ""
echo "[2/4] Iniciando nearRT-RIC..."
"$SCRIPT_DIR/up_flexric.sh"

# 3. gNB + nrUE (710 MB RSS — principal consumidor de memória)
echo ""
echo "[3/4] Iniciando gNB OAI + nrUE (E2 agent → 127.0.0.1)..."
"$SCRIPT_DIR/up_gnb_oai.sh"

# 4. Subir Core OAI em background enquanto UE aguarda
echo ""
echo "[4/4] gNB ativo — subindo Core OAI em background (gNB reconecta ao AMF via N2)..."
(
    cd "$PROJECT_DIR"
    bash scripts/up_core.sh > "$LOG_DIR/up_core_bg.log" 2>&1 && echo "Core OAI pronto" >> "$LOG_DIR/up_core_bg.log" || true
) &

echo ""
echo "Aguardando UE registrar e Core subir (90s)..."
sleep 90

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
