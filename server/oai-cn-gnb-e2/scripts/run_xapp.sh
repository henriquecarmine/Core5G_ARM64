#!/bin/bash
# Roda um xApp monitor READ-ONLY contra o E2 lab em execução e encerra no
# PRIMEIRO EVENTO de sucesso (E2 conectado + subscrito/indicação) — não por
# duração/timeout. Determinístico e leve. Substitui os test_e2_*.sh.
# Uso: ./scripts/run_xapp.sh <cust|kpm|rc>
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MON="$PROJECT_DIR/openairinterface5g/openair2/E2AP/flexric/build/examples/xApp/c/monitor"

case "${1:-cust}" in
    cust) BIN=xapp_gtp_mac_rlc_pdcp_moni; SST=""; SD="" ;;
    kpm)  BIN=xapp_kpm_moni; SST=222; SD=123 ;;
    rc)   BIN=xapp_rc_moni; SST=""; SD="" ;;
    *) echo "uso: $0 <cust|kpm|rc>"; exit 1 ;;
esac

# Pré-requisito por ESTADO (não tempo): E2 lab no ar (RIC + gNB).
if ! pgrep -x nearRT-RIC >/dev/null || ! pgrep -x nr-softmodem >/dev/null; then
    echo "ERRO: E2 lab não está rodando (precisa de nearRT-RIC + gNB)."
    exit 2
fi
[ -x "$MON/$BIN" ] || { echo "ERRO: xApp $BIN não encontrado em $MON"; exit 3; }

# Cap de CPU (cgroup) pra NÃO travar painel/SSH/rfsim no box de 2 vCPUs.
CPU_QUOTA="${XAPP_CPU_QUOTA:-50%}"
SETENV=(--setenv=XAPP_DURATION=3600)   # teto alto: encerramos por evento, nunca por isto
[ -n "$SST" ] && SETENV+=(--setenv=KPM_SST="$SST" --setenv=KPM_SD="$SD")
SUCCESS_RE='Successfully subscribed to RAN_FUNC_ID|INDICATION|UEThp|DRB\.|Test xApp run SUCCESS'

OUT="$(mktemp)"
trap 'sudo pkill -9 -f "$BIN" 2>/dev/null || true; rm -f "$OUT"' EXIT

echo "=== xApp $BIN — encerra no 1º evento de sucesso (CPUQuota=$CPU_QUOTA) ==="
if command -v systemd-run >/dev/null 2>&1; then
    sudo systemd-run --scope -q --unit="oai-xapp-$$" \
        -p "CPUQuota=${CPU_QUOTA}" -p "CPUWeight=10" "${SETENV[@]}" \
        nice -n 15 stdbuf -oL "$MON/$BIN" >"$OUT" 2>&1 &
else
    XAPP_DURATION=3600 KPM_SST="${SST:-}" KPM_SD="${SD:-}" \
        nice -n 15 stdbuf -oL "$MON/$BIN" >"$OUT" 2>&1 &
fi
RUNPID=$!

# Bloqueia ATÉ o evento de sucesso aparecer OU o xApp morrer (tail --pid encerra
# junto com o processo). Sem sleep, sem timeout — puro evento.
if tail -F --pid="$RUNPID" -n +1 "$OUT" 2>/dev/null | grep -m1 -E "$SUCCESS_RE"; then
    echo ""
    echo "✅ SUCESSO — evento de E2 confirmado (xApp encerrado imediatamente)."
    exit 0
else
    echo ""
    echo "❌ FALHA — xApp encerrou sem confirmar evento de E2. Últimas linhas:"
    tail -5 "$OUT" 2>/dev/null | sed 's/^/  /'
    exit 1
fi
