#!/bin/bash
# Simula interferência de rádio injetando perda/atraso artificial na
# interface do UE (uesimtun0) via tc netem. UERANSIM não modela RF real,
# então este é o substituto prático: o efeito na banda/latência é real,
# mesmo que a causa não seja uma interferência de rádio de fato.
# Uso: ./scripts/test_interference.sh [on|off] [perda] [atraso]
#   ex: ./scripts/test_interference.sh on 5% 50ms

set -e

ACTION="${1:-on}"
LOSS="${2:-5%}"
DELAY="${3:-50ms}"
UE_CONTAINER="ueransim"
TUN="uesimtun0"
DN_IP="10.50.0.100"

# Confirma o efeito medindo pelo TÚNEL (ping -I força a interface uesimtun0).
confirm() {
    docker exec "$UE_CONTAINER" ip route replace "$DN_IP/32" dev "$TUN" 2>/dev/null || true
    echo "Medindo efeito pelo túnel ($DN_IP via $TUN)..."
    docker exec "$UE_CONTAINER" ping -I "$TUN" -c 8 -i 0.2 -W 2 "$DN_IP" 2>&1 \
        | grep -E 'packet loss|rtt' || echo "(sem resposta — verifique o UE)"
}

case "$ACTION" in
    on)
        echo "Aplicando interferência simulada: perda ${LOSS}, atraso ${DELAY} em $TUN"
        docker exec "$UE_CONTAINER" tc qdisc replace dev "$TUN" root netem loss "$LOSS" delay "$DELAY"
        docker exec "$UE_CONTAINER" tc qdisc show dev "$TUN"
        echo ""
        confirm
        echo ""
        echo "➜ Interferência ATIVA. Rode o teste de throughput para ver a banda cair."
        ;;
    off)
        echo "Removendo interferência simulada de $TUN"
        docker exec "$UE_CONTAINER" tc qdisc del dev "$TUN" root 2>/dev/null || echo "(nenhuma interferência ativa)"
        echo ""
        confirm
        echo ""
        echo "➜ Canal de volta ao ideal."
        ;;
    *)
        echo "Uso: $0 [on|off] [perda] [atraso]" >&2
        exit 1
        ;;
esac
