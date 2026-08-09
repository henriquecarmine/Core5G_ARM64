#!/bin/bash
# Inicia o nearRT-RIC (FlexRIC) no host.
# Uso: ./scripts/up_flexric.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="${OAI_LOG_DIR:-$PROJECT_DIR/logs}"
RIC_LOG="$LOG_DIR/nearRT-RIC.log"
RIC_IP="${NEAR_RIC_IP:-127.0.0.1}"
FLEXRIC_LIB="${FLEXRIC_LIB_DIR:-$PROJECT_DIR/flexric-lib}"
[[ "$FLEXRIC_LIB" == */ ]] || FLEXRIC_LIB="${FLEXRIC_LIB}/"
FLEXRIC_CONF="${FLEXRIC_CONF:-$PROJECT_DIR/config/flexric/flexric.conf}"

# Preferir nearRT-RIC do submodule (mesma versão E2AP que gNB/xApps dev)
FLEXRIC_BUILD="$PROJECT_DIR/openairinterface5g/openair2/E2AP/flexric/build/examples/ric/nearRT-RIC"

RIC_BIN="${NEAR_RIC_BIN:-}"
if [ -n "$RIC_BIN" ] && [ -x "$RIC_BIN" ]; then
    :
elif [ "${FLEXRIC_USE_SUBMODULE:-1}" = "1" ] && [ -x "$FLEXRIC_BUILD" ]; then
    RIC_BIN="$FLEXRIC_BUILD"
else
    for candidate in \
        "$FLEXRIC_BUILD" \
        /usr/local/bin/flexric/ric/nearRT-RIC \
        /usr/local/bin/nearRT-RIC; do
        if [ -x "$candidate" ]; then
            RIC_BIN="$candidate"
            break
        fi
    done
fi

if [ -z "$RIC_BIN" ]; then
    echo "ERRO: nearRT-RIC não encontrado."
    echo "      Instale FlexRIC ou compile o submodule (ver docs/E2_FLEXRIC.md)."
    exit 1
fi

mkdir -p "$LOG_DIR"

# Garante plugins SM (.so) do MESMO arch do host. Os .so são artefatos de build
# específicos de arquitetura e NÃO são versionados; aqui sincronizamos do build
# tree (sync_flexric_lib.sh). Se já existirem mas forem de outra arquitetura
# (ex.: x86-64 num host arm64), o dlopen do nearRT-RIC falha com
# "load_plugin_ric: Assertion handle != NULL" — então re-sincronizamos.
case "$(uname -m)" in
    aarch64|arm64) WANT_ARCH='aarch64' ;;
    x86_64|amd64)  WANT_ARCH='x86-64' ;;
    *)             WANT_ARCH="$(uname -m)" ;;
esac
if [ ! -f "$FLEXRIC_LIB/libkpm_sm.so" ] || \
   ! file -b "$FLEXRIC_LIB/libkpm_sm.so" 2>/dev/null | grep -q "$WANT_ARCH"; then
    echo "SMs FlexRIC ausentes ou de outra arquitetura (host=$WANT_ARCH); sincronizando do build..."
    "$SCRIPT_DIR/sync_flexric_lib.sh" 2>/dev/null || "$SCRIPT_DIR/build_flexric_tools.sh"
fi

if pgrep -x "nearRT-RIC" >/dev/null 2>&1; then
    echo "nearRT-RIC já está em execução (PID $(pgrep -x 'nearRT-RIC'))."
    exit 0
fi

RIC_ARGS=(-p "$FLEXRIC_LIB")
[ -f "$FLEXRIC_CONF" ] && RIC_ARGS+=(-c "$FLEXRIC_CONF")
RIC_ARGS+=(-a "$RIC_IP")

echo "Iniciando nearRT-RIC ($RIC_BIN) em $RIC_IP (libs: $FLEXRIC_LIB)..."
# SERVIÇO transiente, não --scope: com --scope o cliente `systemd-run` ficava
# no cgroup do painel e, num restart do core5g-panel, o SIGTERM chegava nele —
# que repassava ao scope e derrubava o RIC junto (queda de 09/08, 'Signal 15').
# Sem --scope, o RIC nasce filho do PID 1, fora de qualquer cgroup do painel.
: > "$RIC_LOG"
if command -v systemd-run >/dev/null 2>&1; then
    sudo systemctl stop oai-flexric.service 2>/dev/null || true
    sudo systemctl reset-failed oai-flexric.service 2>/dev/null || true
    sudo systemd-run -q --collect --unit=oai-flexric --slice=oai-lab.slice \
        -p CPUWeight=40 -p CPUQuota=75% \
        -p "StandardOutput=append:$RIC_LOG" -p "StandardError=append:$RIC_LOG" \
        "$RIC_BIN" "${RIC_ARGS[@]}"
else
    nohup "$RIC_BIN" "${RIC_ARGS[@]}" > "$RIC_LOG" 2>&1 &
fi
sleep 2

if ! pgrep -x "nearRT-RIC" >/dev/null 2>&1; then
    echo "ERRO: nearRT-RIC falhou ao iniciar. Ver: $RIC_LOG"
    tail -20 "$RIC_LOG" 2>/dev/null || true
    exit 1
fi
RIC_PID="$(pgrep -x nearRT-RIC | head -1)"

echo "nearRT-RIC PID: $RIC_PID"
echo "Log: $RIC_LOG"
echo ""
echo "Porta E2AP padrão: 36421 (FlexRIC) / 36422 (O-RAN SC)"
echo "Parar: ./scripts/down_flexric.sh"
