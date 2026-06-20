#!/bin/bash
# Script para iniciar o RAN gNB OAI (gNB + nrUE nativos, modo RFSIM)
# Uso: ./scripts/up_gnb_oai.sh
#
# Requer: openairinterface5g compilado (./build_oai --gNB --nrUE -w SIMU -c)
# O Core deve estar rodando antes (./scripts/up_core.sh)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OAI_DIR="$PROJECT_DIR/openairinterface5g"
BUILD_DIR="$OAI_DIR/cmake_targets/ran_build/build"
LOG_DIR="${OAI_LOG_DIR:-$PROJECT_DIR/logs}"
FLEXRIC_LIB="${FLEXRIC_LIB_DIR:-$PROJECT_DIR/flexric-lib}"
[[ "$FLEXRIC_LIB" == */ ]] || FLEXRIC_LIB="${FLEXRIC_LIB}/"
E2_SM_ARGS=()
if [ -d "$FLEXRIC_LIB" ] && [ -f "$FLEXRIC_LIB/libkpm_sm.so" ]; then
    E2_SM_ARGS=(--e2_agent.sm_dir "$FLEXRIC_LIB")
fi
GNB_LOG="$LOG_DIR/gnb_oai.log"
UE_LOG="$LOG_DIR/ue_oai.log"

# --- Proteção contra congelamento da instância (2 vCPUs) ---------------------
# O gNB/nrUE RFSIM podem saturar os 2 vCPUs em picos e travar a máquina inteira
# (SSH/painel/Core deixam de responder até precisar reboot). Para impedir isso,
# rodamos os processos nativos dentro de um scope do systemd com teto de CPU
# (CPUQuota) e prioridade baixa (Nice). Mesmo num pico, o SO reserva CPU para
# sshd/painel/dockerd (Nice 0) e o lab degrada em vez de congelar.
# Override por ambiente: GNB_CPUQUOTA / UE_CPUQUOTA / RAN_NICE.
GNB_CPUQUOTA="${GNB_CPUQUOTA:-120%}"
UE_CPUQUOTA="${UE_CPUQUOTA:-60%}"
RAN_NICE="${RAN_NICE:-10}"
# Nota: 'Nice' não é propriedade de scope (só de service). Para scopes usamos
# CPUQuota (teto rígido) + CPUWeight (prioridade cgroup, default 100) e aplicamos
# a prioridade do escalonador via o comando 'nice' como prefixo do processo.
if command -v systemd-run >/dev/null 2>&1; then
    # --slice=oai-lab.slice: teto AGREGADO de 180% (90% dos 2 vcores) p/ todo o lab;
    # mesmo que gNB+UE+xApp queiram mais, a slice os limita JUNTOS, deixando CPU
    # livre p/ o sistema (ver guardrails em infra/server-bootstrap.sh).
    # Dentro do teto da slice, o gNB tem peso MAIOR (60) que o nrUE (20): o gNB
    # RFSIM precisa de ~1 core p/ não quebrar o timing do E2; o UE fica com a
    # sobra. Assim o lab cabe em 150% sem estrangular o gNB.
    CAP_GNB=(systemd-run --scope -q --unit=oai-gnb --slice=oai-lab.slice -p "CPUQuota=${GNB_CPUQUOTA}" -p "CPUWeight=60" nice -n "${RAN_NICE}")
    CAP_UE=(systemd-run --scope -q --unit=oai-nrue --slice=oai-lab.slice -p "CPUQuota=${UE_CPUQUOTA}" -p "CPUWeight=20" nice -n "${RAN_NICE}")
else
    CAP_GNB=(nice -n "${RAN_NICE}")
    CAP_UE=(nice -n "${RAN_NICE}")
    echo "AVISO: systemd-run ausente — só nice, sem teto rígido de CPU."
fi

# Config variável: suporta 24 PRBs (~150 MB RSS) para t4g.micro com pouca RAM
GNB_CONF="${GNB_CONF_PATH:-$OAI_DIR/scripts/gnb.conf}"
GNB_NRB="${GNB_NRB:-106}"
GNB_DL_FREQ="${GNB_DL_FREQ:-3619200000}"

echo "=========================================="
echo "Iniciando RAN gNB OAI (gNB + nrUE)"
echo "=========================================="
echo ""

# Verificar se o build existe
if [ ! -f "$BUILD_DIR/nr-softmodem" ] || [ ! -f "$BUILD_DIR/nr-uesoftmodem" ]; then
    echo "ERRO: Binários não encontrados em $BUILD_DIR"
    echo "      Compile primeiro:"
    echo "        cd openairinterface5g/cmake_targets"
    echo "        ./build_oai --ninja -I"
    echo "        ./build_oai --ninja --gNB --nrUE -w SIMU -c"
    exit 1
fi

# Verificar se gnb.conf e ue.conf existem
if [ ! -f "$OAI_DIR/scripts/gnb.conf" ]; then
    echo "ERRO: gnb.conf não encontrado em $OAI_DIR/scripts/"
    exit 1
fi
if [ ! -f "$OAI_DIR/scripts/ue.conf" ]; then
    echo "ERRO: ue.conf não encontrado em $OAI_DIR/scripts/"
    exit 1
fi

mkdir -p "$LOG_DIR"

# Configurar IP no host para o gNB alcançar o AMF (obrigatório)
# A interface demo-oai é criada pelo Docker quando o Core sobe
if ! ip -4 addr show demo-oai 2>/dev/null | grep -q "192.168.70.129"; then
    echo "Configurando IP 192.168.70.129 na interface demo-oai..."
    if ip link show demo-oai >/dev/null 2>&1; then
        sudo ip addr add 192.168.70.129/24 dev demo-oai 2>/dev/null || true
    else
        echo "ERRO: Interface demo-oai não encontrada."
        echo "      Inicie o Core primeiro: ./scripts/up_core.sh"
        exit 1
    fi
fi

# Parar instâncias anteriores se existirem
pkill -f "nr-softmodem" 2>/dev/null || true
pkill -f "nr-uesoftmodem" 2>/dev/null || true
# Limpa scopes do systemd de execuções anteriores (evita "unit already exists")
sudo systemctl reset-failed oai-gnb.scope oai-nrue.scope 2>/dev/null || true
sudo systemctl stop oai-gnb.scope oai-nrue.scope 2>/dev/null || true
sleep 2

echo "Iniciando gNB em background (conf: $GNB_CONF, NRB=$GNB_NRB, f=$GNB_DL_FREQ Hz)..."
cd "$BUILD_DIR"
echo "  (teto CPU: ${GNB_CPUQUOTA}, Nice ${RAN_NICE} — protege a instância contra freeze)"
sudo nohup "${CAP_GNB[@]}" ./nr-softmodem -O "$GNB_CONF" \
    --gNBs.[0].min_rxtxtime 6 \
    --rfsim \
    "${E2_SM_ARGS[@]}" \
    > "$GNB_LOG" 2>&1 &
GNB_PID=$!
echo "  gNB PID: $GNB_PID (logs: $GNB_LOG)"

echo "Aguardando gNB estabilizar..."
for i in $(seq 1 10); do
    sleep 1
    if ! kill -0 "$GNB_PID" 2>/dev/null; then
        echo "ERRO: gNB morreu durante a inicialização (PID $GNB_PID)."
        echo "      Verifique memória disponível (free -h) e o log: $GNB_LOG"
        exit 1
    fi
done

UE_PID=""
if [ "${SKIP_UE:-0}" = "1" ]; then
    echo "SKIP_UE=1 — nrUE omitido (libera ~438 MB para gNB + Core no t4g.micro)."
else
    echo "Iniciando nrUE em background..."
    if [ "$GNB_NRB" = "106" ]; then
        UE_RF_ARGS=(--rfsim -r 106 --numerology 1 --band 78 -C 3619200000 --ssb 516)
    elif [ "$GNB_NRB" = "51" ]; then
        UE_RF_ARGS=(--rfsim -r 51 --numerology 1 --band 78 -C 3469440000 --ssb 186)
    else
        UE_RF_ARGS=(--rfsim -r "$GNB_NRB" --numerology 1 --band 78 -C "$GNB_DL_FREQ")
    fi
    sudo nohup "${CAP_UE[@]}" ./nr-uesoftmodem -O "$OAI_DIR/scripts/ue.conf" \
        "${UE_RF_ARGS[@]}" \
        > "$UE_LOG" 2>&1 &
    UE_PID=$!
    echo "  nrUE PID: $UE_PID (logs: $UE_LOG)"
fi

echo ""
echo "=========================================="
echo "gNB OAI iniciado com sucesso!"
echo "=========================================="
echo ""
echo "PIDs: gNB=$GNB_PID${UE_PID:+, nrUE=$UE_PID}"
echo "Logs: $GNB_LOG${UE_PID:+, $UE_LOG}"
echo ""
echo "Para parar: ./scripts/down_gnb_oai.sh"
echo ""
