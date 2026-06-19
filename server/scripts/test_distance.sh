#!/bin/bash
# "Distância relativa" simulada. UERANSIM não modela path-loss/RSRP real por
# distância física (precisaria de múltiplas células configuradas com sinal
# diferente — fora de escopo aqui). Como substituto honesto, usamos o mesmo
# tc netem do teste de interferência, com perfis que imitam o efeito de
# afastar o UE da antena: mais distância = mais perda + mais atraso.
# Uso: ./scripts/test_distance.sh [perto|medio|longe|off]

set -e

PROFILE="${1:-perto}"
UE_CONTAINER="ueransim"

case "$PROFILE" in
    perto) LOSS="0%";  DELAY="5ms"   ;;
    medio) LOSS="3%";  DELAY="40ms"  ;;
    longe) LOSS="10%"; DELAY="120ms" ;;
    off)
        echo "Removendo efeito de distância de uesimtun0"
        docker exec "$UE_CONTAINER" tc qdisc del dev uesimtun0 root 2>/dev/null || echo "(nenhum perfil ativo)"
        exit 0
        ;;
    *)
        echo "Uso: $0 [perto|medio|longe|off]" >&2
        exit 1
        ;;
esac

echo "Perfil de distância: ${PROFILE} (perda ${LOSS}, atraso ${DELAY})"
docker exec "$UE_CONTAINER" tc qdisc replace dev uesimtun0 root netem loss "$LOSS" delay "$DELAY"
docker exec "$UE_CONTAINER" tc qdisc show dev uesimtun0
