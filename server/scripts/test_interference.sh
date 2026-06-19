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

case "$ACTION" in
    on)
        echo "Aplicando interferência simulada: perda ${LOSS}, atraso ${DELAY} em uesimtun0"
        docker exec "$UE_CONTAINER" tc qdisc replace dev uesimtun0 root netem loss "$LOSS" delay "$DELAY"
        docker exec "$UE_CONTAINER" tc qdisc show dev uesimtun0
        ;;
    off)
        echo "Removendo interferência simulada de uesimtun0"
        docker exec "$UE_CONTAINER" tc qdisc del dev uesimtun0 root 2>/dev/null || echo "(nenhuma interferência ativa)"
        ;;
    *)
        echo "Uso: $0 [on|off] [perda] [atraso]" >&2
        exit 1
        ;;
esac
