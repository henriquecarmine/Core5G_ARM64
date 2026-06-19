#!/bin/bash
# Configura o canal de rádio simulado em uesimtun0 via tc netem,
# combinando os efeitos de distância (path loss 3GPP TR 38.901 UMa NLOS)
# e interferência (C/I ratio baseado em Shannon–Hartley).
# Uso: ./test_channel.sh [distance] [interference]
#   distance    : none | 100m | 500m | 1km | 3km | off
#   interference: none | fraca | media | alta
# Exemplo: ./test_channel.sh 500m media

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/testlog.sh
source "$SCRIPT_DIR/lib/testlog.sh"

UE_CONTAINER="ueransim"
DN_IP="10.50.0.100"
DISTANCE="${1:-none}"
INTERFERENCE="${2:-none}"

# Confirma o efeito medindo pelo TÚNEL (ping -I força a interface uesimtun0).
ping_tunnel() {
    docker exec "$UE_CONTAINER" ip route replace "$DN_IP/32" dev uesimtun0 2>/dev/null || true
    docker exec "$UE_CONTAINER" ping -I uesimtun0 -c 6 -i 0.2 -W 2 "$DN_IP" 2>&1 \
        | grep -E 'packet loss|rtt' || echo "(sem resposta)"
}

# --- off: limpar qualquer qdisc ativo ---
if [ "$DISTANCE" = "off" ]; then
    section "Canal 5G — restaurar ideal"
    if docker exec "$UE_CONTAINER" tc qdisc del dev uesimtun0 root 2>/dev/null; then
        ok "configuração de canal removida"
    else
        info "nenhuma configuração ativa"
    fi
    summary "removeu qualquer interferência/distância simulada de uesimtun0" \
            "canal de volta ao ideal (sem perda nem atraso artificial)" ok
    exit 0
fi

# --- Parâmetros de distância (3GPP TR 38.901, UMa NLOS, f_c=3.5 GHz) ---
case "$DISTANCE" in
    none) D_DELAY=0;  D_LOSS=0;  D_JITTER=0; D_INFO="canal ideal (sem atenuação de percurso)" ;;
    100m) D_DELAY=1;  D_LOSS=0;  D_JITTER=0; D_INFO="PL = 102.6 dB · RSRP ≈ −44 dBm · delay ≈ 1 ms" ;;
    500m) D_DELAY=8;  D_LOSS=2;  D_JITTER=1; D_INFO="PL = 129.9 dB · RSRP ≈ −72 dBm · delay = 8 ms" ;;
    1km)  D_DELAY=20; D_LOSS=8;  D_JITTER=3; D_INFO="PL = 141.7 dB · RSRP ≈ −84 dBm · delay = 20 ms" ;;
    3km)  D_DELAY=50; D_LOSS=20; D_JITTER=8; D_INFO="PL = 159.6 dB · RSRP ≈ −102 dBm · delay = 50 ms (borda da célula)" ;;
    *)    err "distância inválida: $DISTANCE (use none|100m|500m|1km|3km|off)"; exit 1 ;;
esac

# --- Parâmetros de interferência (Shannon–Hartley, B=100 MHz 5G NR) ---
case "$INTERFERENCE" in
    none)  I_DELAY=0;  I_LOSS=0;  I_JITTER=0;  I_INFO="sem interferência" ;;
    fraca) I_DELAY=5;  I_LOSS=1;  I_JITTER=2;  I_INFO="C/I > 20 dB · SINR ≈ 20 dB · C_max ≈ 665 Mbps · PDR 99%" ;;
    media) I_DELAY=20; I_LOSS=5;  I_JITTER=8;  I_INFO="C/I ≈ 15 dB · SINR ≈ 15 dB · C_max ≈ 498 Mbps · PDR 95%" ;;
    alta)  I_DELAY=50; I_LOSS=15; I_JITTER=20; I_INFO="C/I < 10 dB · SINR ≈ 5 dB · C_max ≈ 207 Mbps · PDR 85%" ;;
    *)     err "interferência inválida: $INTERFERENCE (use none|fraca|media|alta)"; exit 1 ;;
esac

# --- Combinar parâmetros ---
TOTAL_DELAY=$(( D_DELAY + I_DELAY ))
TOTAL_LOSS=$(( D_LOSS + I_LOSS - D_LOSS * I_LOSS / 100 ))   # 1−(1−p₁)(1−p₂)
TOTAL_JITTER=$(( D_JITTER + I_JITTER ))

section "Canal 5G simulado — distância '$DISTANCE' + interferência '$INTERFERENCE'"
kv "Distância" "$D_INFO"
kv "Interferência" "$I_INFO"
kv "tc netem combinado" "delay ${TOTAL_DELAY}ms · jitter ${TOTAL_JITTER}ms · loss ${TOTAL_LOSS}%"

if [ "$TOTAL_DELAY" -eq 0 ] && [ "$TOTAL_LOSS" -eq 0 ]; then
    docker exec "$UE_CONTAINER" tc qdisc del dev uesimtun0 root 2>/dev/null || true
    ok "canal ideal: nenhuma restrição aplicada"
    summary "computou o canal a partir dos modelos 3GPP/Shannon (resultou em condição ideal)" \
            "sem degradação aplicada" ok
    exit 0
fi

# netem: jitter é o SEGUNDO valor do delay (não existe palavra-chave 'jitter').
NETEM_ARGS=""
if [ "$TOTAL_DELAY" -gt 0 ]; then
    NETEM_ARGS="delay ${TOTAL_DELAY}ms"
    [ "$TOTAL_JITTER" -gt 0 ] && NETEM_ARGS="$NETEM_ARGS ${TOTAL_JITTER}ms"
fi
[ "$TOTAL_LOSS" -gt 0 ] && NETEM_ARGS="$NETEM_ARGS loss ${TOTAL_LOSS}%"

if docker exec "$UE_CONTAINER" tc qdisc replace dev uesimtun0 root netem $NETEM_ARGS; then
    ok "aplicado em uesimtun0: $(docker exec "$UE_CONTAINER" tc qdisc show dev uesimtun0 | grep -o 'netem.*')"
else
    err "falha ao aplicar tc netem (container ueransim no ar?)"
    summary "tentou aplicar o canal degradado em uesimtun0" "falhou ao programar o tc netem" err
    exit 1
fi

step "efeito imediato (ping pelo túnel ao DN):"
PING="$(ping_tunnel)"
echo "$PING" | while IFS= read -r l; do info "$l"; done
PLOSS="$(echo "$PING" | grep -oE '[0-9]+(\.[0-9]+)?% packet loss' | head -1)"

summary "aplicou no rádio (uesimtun0) a perda/atraso equivalentes a '$DISTANCE' + '$INTERFERENCE' (modelos 3GPP/Shannon)" \
        "canal degradado ativo (${PLOSS:-perda configurada}). Rode o teste de throughput para ver a banda cair." warn
