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

echo "[3/3] Subindo gNB + nrUE (24 PRBs, PLMN 208/95, slice 222/123 — casa com core v2)..."
GNB_CONF_PATH="$SCRIPT_DIR/gnb_24prb.conf" GNB_NRB=51 GNB_DL_FREQ=3469440000 \
    "$SCRIPT_DIR/up_gnb_oai.sh"

echo ""
echo "E2 lab v2 pronto. UE deve obter IP 12.1.1.x em ~40s (oaitun_ue1)."
echo "Testar xApps: ./scripts/test_e2_sm.sh cust | ./scripts/test_e2_sm.sh kpm"
echo "Parar RAN/RIC: ./scripts/down_e2_lab.sh   |  Parar core: ./oai-cn5g-v2/down_core_v2.sh"
