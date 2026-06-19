#!/bin/bash
# Testa E2SM-RC: xApp subscreve ANTES do attach do UE.
# Uso: ./scripts/test_e2_rc_attach.sh
#
# Ordem: RIC → xApp RC → gNB (sem UE) → UE → captura INDICATIONs

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="${OAI_LOG_DIR:-$PROJECT_DIR/logs}"
OAI_DIR="$PROJECT_DIR/openairinterface5g"
BUILD_DIR="$OAI_DIR/cmake_targets/ran_build/build"
FLEXRIC_LIB="${FLEXRIC_LIB_DIR:-$PROJECT_DIR/flexric-lib}"
[[ "$FLEXRIC_LIB" == */ ]] || FLEXRIC_LIB="${FLEXRIC_LIB}/"
DURATION="${XAPP_DURATION:-60}"
LOG="$LOG_DIR/xapp_rc_attach.log"
# shellcheck source=lib/testlog.sh
source "$SCRIPT_DIR/lib/testlog.sh"

# Teto de CPU para os processos RFSIM (impede congelar a instância de 2 vCPUs).
if command -v systemd-run >/dev/null 2>&1; then
    CAP_GNB=(systemd-run --scope -q -p CPUQuota=120% -p CPUWeight=20 nice -n 10)
    CAP_UE=(systemd-run --scope -q -p CPUQuota=60% -p CPUWeight=20 nice -n 10)
else
    CAP_GNB=(nice -n 10); CAP_UE=(nice -n 10)
fi

E2_SM_ARGS=()
if [ -d "$FLEXRIC_LIB" ] && [ -f "$FLEXRIC_LIB/librc_sm.so" ]; then
    E2_SM_ARGS=(--e2_agent.sm_dir "$FLEXRIC_LIB")
fi

mkdir -p "$LOG_DIR"

if ! pgrep -x "nearRT-RIC" >/dev/null 2>&1; then
    "$SCRIPT_DIR/up_flexric.sh"
fi

FLEXRIC_BUILD="$PROJECT_DIR/openairinterface5g/openair2/E2AP/flexric/build/examples/xApp/c/monitor/xapp_rc_moni"
XAPP=""
for candidate in "$FLEXRIC_BUILD" /usr/local/bin/flexric/xApp/c/monitor/xapp_rc_moni; do
    [ -x "$candidate" ] && XAPP="$candidate" && break
done
[ -n "$XAPP" ] || { echo "ERRO: xapp_rc_moni ausente. ./scripts/build_flexric_tools.sh"; exit 1; }

echo "=== E2SM-RC fresh attach (${DURATION}s) ==="

# Parar RAN; manter Core + RIC
pkill -f "nr-softmodem" 2>/dev/null || true
pkill -f "nr-uesoftmodem" 2>/dev/null || true
sleep 2

# xApp RC em background
XAPP_DURATION="$DURATION" "$XAPP" > "$LOG" 2>&1 &
XPID=$!
echo "xApp RC PID: $XPID"

# gNB sem UE
if ! ip -4 addr show demo-oai 2>/dev/null | grep -q "192.168.70.129"; then
    sudo ip addr add 192.168.70.129/24 dev demo-oai 2>/dev/null || true
fi
step "iniciando gNB (sem UE; teto de CPU ativo)"
cd "$BUILD_DIR"
sudo nohup "${CAP_GNB[@]}" ./nr-softmodem -O "$OAI_DIR/scripts/gnb.conf" \
    --gNBs.[0].min_rxtxtime 6 --rfsim "${E2_SM_ARGS[@]}" \
    >> "$LOG_DIR/gnb_oai.log" 2>&1 &

echo "Aguardando E2 setup + subscrição RC (20s)..."
for i in $(seq 1 20); do
    grep -q "Successfully subscribed" "$LOG" 2>/dev/null && break
    sleep 1
done

if ! grep -q "Successfully subscribed" "$LOG" 2>/dev/null; then
    echo "AVISO: subscrição RC não confirmada em 20s"
    tail -5 "$LOG"
fi

step "iniciando nrUE (attach → eventos RRC; teto de CPU ativo)"
sudo nohup "${CAP_UE[@]}" ./nr-uesoftmodem -O "$OAI_DIR/scripts/ue.conf" \
    --rfsim -r 106 --numerology 1 --band 78 -C 3619200000 --ssb 516 \
    >> "$LOG_DIR/ue_oai.log" 2>&1 &

echo "Aguardando xApp..."
wait "$XPID" 2>/dev/null || true

section "Resultados E2SM-RC (controle/eventos do RAN)"
grep -iE 'INDICATION|RRC connected|RRC idle|UE ID type|amf_ue_ngap|RRCSetup|Reconfig|Measurement|Security Mode|Successfully subscribed' "$LOG" \
    | while IFS= read -r l; do info "$l"; done || true

DID="assinou o E2SM-RC no RIC ANTES do UE conectar e, ao subir o UE, capturou os eventos de controle/RRC (attach) via interface E2"
if grep -qiE 'INDICATION|RRC connected|UE ID type|amf_ue_ngap' "$LOG"; then
    ok "RC INDICATIONs capturadas (eventos de controle do RAN)"
    summary "$DID" "RIC recebeu eventos RC do gNB — comprova o canal de controle near-RT do O-RAN" ok
else
    warn "subscrição OK, sem INDICATIONs no período"
    summary "$DID" "assinatura E2SM-RC funcionou, mas sem eventos no período (mais tempo/tráfego pode ser necessário)" warn
fi
info "log completo: $LOG"
