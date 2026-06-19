#!/bin/bash
# Teste de throughput real UE -> DN via iperf3, ATRAVESSANDO o túnel 5G de
# verdade (UE -> gNB -> UPF -> DN). Garante que o tráfego sai por uesimtun0
# (rota dedicada pro DN), senão o kernel manda pelo bridge eth0 e o `tc netem`
# de interferência/distância (aplicado em uesimtun0) não teria efeito nenhum
# na medição. Ao final, imprime um RESUMO didático.
# Uso: ./scripts/test_throughput.sh [duracao_segundos]

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/testlog.sh
source "$SCRIPT_DIR/lib/testlog.sh"

DURATION="${IPERF_DURATION:-${1:-10}}"
DN_CONTAINER="open5gs-dn-containerized"
DN_IP="10.50.0.100"
UE_CONTAINER="ueransim"
UE_IMSI="${UE_IMSI:-imsi-001010000000002}"
TUN="uesimtun0"

section "Teste de Throughput (iperf3) — UE → DN pelo túnel 5G"

UE_IP="$(docker exec "$UE_CONTAINER" sh -c "ip -4 addr show $TUN 2>/dev/null | grep -oE '([0-9]+\.){3}[0-9]+' | head -1" 2>/dev/null || true)"
if [ -z "$UE_IP" ]; then
    err "interface $TUN não encontrada — o UE está registrado com sessão PDU ativa?"
    summary "tentou medir o throughput UE→DN pelo túnel 5G" \
            "não foi possível: UE sem sessão PDU (suba o Projeto 1 e registre o UE)" err
    exit 1
fi
kv "UE IP ($TUN)" "$UE_IP"
kv "Destino (DN)" "$DN_IP"

# Garante que o tráfego pro DN atravessa o túnel 5G (e não o bridge eth0).
docker exec "$UE_CONTAINER" ip route replace "$DN_IP/32" dev "$TUN" 2>/dev/null \
    && step "rota $DN_IP via $TUN (tráfego forçado pelo túnel 5G)"

# Condição de canal simulada ativa (tc netem aplicado por interferência/distância)
NETEM="$(docker exec "$UE_CONTAINER" tc qdisc show dev "$TUN" 2>/dev/null | grep -o 'netem.*' || true)"
if [ -n "$NETEM" ]; then
    NETEM_LOSS="$(echo "$NETEM" | grep -oE 'loss [0-9.]+%' || echo 'loss 0%')"
    NETEM_DELAY="$(echo "$NETEM" | grep -oE 'delay [0-9.]+m?s' || echo 'delay 0ms')"
    COND="ATIVA — ${NETEM_LOSS}, ${NETEM_DELAY}"
else
    COND="ideal (nenhuma interferência/distância aplicada)"
fi

docker exec -d "$DN_CONTAINER" sh -c "iperf3 -s -1 -p 5201 > /tmp/iperf3-server.log 2>&1"
sleep 1

step "rodando iperf3 por ${DURATION}s..."
echo ""
IPERF_OUT="$(docker exec "$UE_CONTAINER" iperf3 -c "$DN_IP" -p 5201 -B "$UE_IP" -t "$DURATION" 2>&1)"
echo "$IPERF_OUT"

# --- extrai métricas do iperf3 (independe da unidade K/M/G bits/sec) ---
SEND_BW="$(echo "$IPERF_OUT" | awk '/sender/{for(i=1;i<=NF;i++) if($i ~ /bits\/sec/){print $(i-1)" "$i; exit}}')"
RECV_BW="$(echo "$IPERF_OUT" | awk '/receiver/{for(i=1;i<=NF;i++) if($i ~ /bits\/sec/){print $(i-1)" "$i; exit}}')"
RETR="$(echo "$IPERF_OUT" | awk '/sender/{for(i=1;i<=NF;i++) if($i ~ /bits\/sec/){print $(i+1); exit}}')"
[ -z "$SEND_BW" ] && SEND_BW="n/d"
[ -z "$RECV_BW" ] && RECV_BW="n/d"
[ -z "$RETR" ] && RETR="0"

# --- mede perda/latência pelo túnel (ping força a interface) ---
PING_OUT="$(docker exec "$UE_CONTAINER" ping -I "$TUN" -c 10 -i 0.2 -W 2 "$DN_IP" 2>&1 || true)"
LOSS="$(echo "$PING_OUT" | grep -oE '[0-9]+(\.[0-9]+)?% packet loss' | head -1)"
RTT="$(echo "$PING_OUT" | sed -nE 's#.*= ([0-9.]+/[0-9.]+/[0-9.]+/[0-9.]+) ms#\1#p')"
[ -z "$LOSS" ] && LOSS="n/d"
if [ -n "$RTT" ]; then
    RTT_AVG="$(echo "$RTT" | cut -d/ -f2)"; RTT_MAX="$(echo "$RTT" | cut -d/ -f3)"; RTT_JIT="$(echo "$RTT" | cut -d/ -f4)"
else
    RTT_AVG="n/d"; RTT_MAX="n/d"; RTT_JIT="n/d"
fi

# --- estado do UE (RAN) via nr-cli ---
ST="$(docker exec "$UE_CONTAINER" nr-cli "$UE_IMSI" -e status 2>/dev/null || true)"
CM="$(echo "$ST" | awk -F': ' '/cm-state/{print $2}')"
MM="$(echo "$ST" | awk -F': ' '/mm-state/{print $2}')"
CELL="$(echo "$ST" | awk -F': ' '/current-cell/{print $2}')"
TAC="$(echo "$ST" | awk -F': ' '/current-tac/{print $2}')"
[ -z "$CM" ] && CM="?"; [ -z "$MM" ] && MM="?"; [ -z "$CELL" ] && CELL="?"

section "Medição"
kv "Sinal / canal simulado" "$COND"
kv "Estado do UE" "$CM · $MM"
kv "Célula servidora" "cell $CELL (TAC $TAC) · PLMN 001/01"
kv "Throughput (envio)" "$SEND_BW   (retransmissões TCP: $RETR)"
kv "Throughput (recepção)" "$RECV_BW"
kv "Perda de pacotes" "$LOSS"
kv "Latência RTT médio/máx" "${RTT_AVG} / ${RTT_MAX} ms   (jitter ${RTT_JIT} ms)"

if [ -n "$NETEM" ]; then
    summary "mediu a banda real UE→DN pelo túnel 5G com o canal degradado (interferência/distância via tc netem em $TUN)" \
            "banda reduzida e perda/latência elevadas — compare com o canal ideal: ${SEND_BW}, ${LOSS}" warn
else
    summary "mediu a banda real UE→DN pelo túnel 5G (iperf3) e o estado do rádio do UE" \
            "canal ideal: ${SEND_BW}, ${LOSS}. Aplique interferência/distância e rode de novo para ver cair." ok
fi
