#!/bin/bash
# E2 lab sobre o core OAI v2.2.1: nearRT-RIC + gNB + nrUE.
# NÃO gerencia o core (use ../oai-cn5g-v2/up_core_v2.sh antes). Se o core não
# estiver healthy, sobe o v2.2.1 automaticamente.
#
# Uso: ./scripts/up_e2_lab_v2.sh
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "[1/3] Garantindo core OAI v2.2.1 RODANDO (e parando o Projeto 1)..."
# IMPORTANTE: checar .State.Running, não Health.Status (health fica "healthy"
# mesmo com o container PARADO → faria pular o up_core_v2 que para o Open5GS).
if [ "$(docker inspect -f '{{.State.Running}}' oai-amf 2>/dev/null || echo false)" != "true" ]; then
    echo "  core OAI não está rodando — subindo v2.2.1 (oai-cn5g-v2/up_core_v2.sh)..."
    bash "$PROJECT_DIR/oai-cn5g-v2/up_core_v2.sh"
else
    echo "  core OAI (oai-amf) já rodando."
fi

echo "[2/3] Subindo nearRT-RIC..."
"$SCRIPT_DIR/up_flexric.sh"
# Sem espera por tempo: o E2 agent do gNB reconecta ao RIC por conta própria
# (evento), então não precisa de sleep aqui.

# SKIP_UE: no box de 2 vCPUs, gNB e nrUE em RFSIM fazem busy-poll e saturam os
# dois núcleos — aí o caminho INDICATION→Report do RIC fica faminto e o xApp
# estoura o timeout interno do FlexRIC. Para VALIDAR xApps (E2 é gNB↔RIC, não
# precisa de UE), suba sem o nrUE: sobra 1 vCPU inteiro p/ RIC+xApp.
# Default: sobe COM nrUE (lab completo). Rode `SKIP_UE=1 ./up_e2_lab_v2.sh`
# para o modo de validação de xApp.
SKIP_UE="${SKIP_UE:-0}"
if [ "$SKIP_UE" = "1" ]; then
    echo "[3/3] Subindo gNB SEM nrUE (SKIP_UE=1 — modo validação de xApp, libera 1 vCPU)..."
else
    echo "[3/3] Subindo gNB + nrUE (24 PRBs, PLMN 208/95, slice 222/123 — casa com core v2)..."
fi
GNB_CONF_PATH="$SCRIPT_DIR/gnb_24prb.conf" GNB_NRB=51 GNB_DL_FREQ=3469440000 \
    SKIP_UE="$SKIP_UE" "$SCRIPT_DIR/up_gnb_oai.sh"

echo ""
if [ "$SKIP_UE" = "1" ]; then
    echo "E2 lab v2 (sem UE) pronto. gNB faz E2 SETUP com o RIC; sem oaitun_ue1."
else
    echo "E2 lab v2 pronto. UE deve obter IP 12.1.1.x em ~40s (oaitun_ue1)."
fi
echo "Testar xApps: ./scripts/run_xapp.sh cust | kpm | rc"
echo "Parar RAN/RIC: ./scripts/down_e2_lab.sh   |  Parar core: ./oai-cn5g-v2/down_core_v2.sh"
