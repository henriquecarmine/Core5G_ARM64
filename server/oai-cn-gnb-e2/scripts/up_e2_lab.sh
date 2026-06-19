#!/bin/bash
# Sobe laboratório completo: Core OAI + nearRT-RIC + gNB E2 + nrUE.
# Uso: ./scripts/up_e2_lab.sh
#
# Requer gNB compilado com E2: ./scripts/build_e2.sh
#
# NOTA (t4g.micro — 906 MB RAM): nr-softmodem precisa de ~150 MB físicos ao iniciar.
# O OAI Core (8 containers C++) usa ~850 MB RSS, deixando ~50 MB livres — insuficiente.
# Estratégia: para 5 containers não-essenciais para E2 (gNB precisa apenas de AMF+NRF+SMF),
# libera page cache, sobe RIC + gNB, depois reinicia containers para auth de UE em background.

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

# 1.5 — Liberar RAM (sempre; os containers ficam swapeados de qualquer forma).
# Para oai-ext-dn, oai-ausf, oai-udm, oai-udr, mysql — gNB precisa só de AMF+NRF+SMF.
# Eles são reiniciados em background após gNB inicializar (passo 3.5).
echo ""
echo "[1.5/4] Liberando RAM para o gNB — parando containers de auth/dados..."
STOPPED_CONTAINERS=()
for c in oai-ext-dn oai-ausf oai-udm oai-udr mysql; do
    if docker stop "$c" 2>/dev/null; then
        STOPPED_CONTAINERS+=("$c")
        printf '  parado: %s\n' "$c"
    fi
done
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches' 2>/dev/null || true
sleep 5
AVAIL_MB=$(awk '/MemAvailable/ {printf "%d", $2/1024}' /proc/meminfo 2>/dev/null || echo 0)
echo "  RAM disponível: ${AVAIL_MB} MB"

# 2. nearRT-RIC
echo ""
echo "[2/4] Iniciando nearRT-RIC..."
"$SCRIPT_DIR/up_flexric.sh"

# 3. gNB + UE (com E2 agent)
echo ""
echo "[3/4] Iniciando gNB OAI + nrUE (E2 agent → 127.0.0.1)..."
"$SCRIPT_DIR/up_gnb_oai.sh"

# 3.5 — Restaurar containers de auth/dados em background para UE autenticar
if [ "${#STOPPED_CONTAINERS[@]}" -gt 0 ]; then
    echo ""
    echo "[3.5/4] gNB ativo — reativando containers de auth em background..."
    (
        for c in mysql oai-udr oai-udm oai-ausf oai-ext-dn; do
            docker start "$c" 2>/dev/null && echo "  iniciado: $c" || true
            sleep 4
        done
    ) &
    echo "  (mysql → udr → udm → ausf → ext-dn — ~45s para ficar healthy)"
fi

# 4. Aguardar registro UE (containers de auth precisam de ~45s para subir)
echo ""
echo "[4/4] Aguardando UE registrar (60s)..."
sleep 60

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
