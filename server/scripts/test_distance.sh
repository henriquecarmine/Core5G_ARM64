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
TUN="uesimtun0"
DN_IP="10.50.0.100"

# Confirma o efeito medindo pelo TÚNEL (ping -I força a interface uesimtun0).
confirm() {
    docker exec "$UE_CONTAINER" ip route replace "$DN_IP/32" dev "$TUN" 2>/dev/null || true
    echo "Medindo efeito pelo túnel ($DN_IP via $TUN)..."
    docker exec "$UE_CONTAINER" ping -I "$TUN" -c 8 -i 0.2 -W 2 "$DN_IP" 2>&1 \
        | grep -E 'packet loss|rtt' || echo "(sem resposta — verifique o UE)"
}

case "$PROFILE" in
    perto) LOSS="0%";  DELAY="5ms"   ;;
    medio) LOSS="3%";  DELAY="40ms"  ;;
    longe) LOSS="10%"; DELAY="120ms" ;;
    off)
        echo "Removendo efeito de distância de $TUN"
        docker exec "$UE_CONTAINER" tc qdisc del dev "$TUN" root 2>/dev/null || echo "(nenhum perfil ativo)"
        echo ""
        confirm
        echo ""
        echo "➜ Canal de volta ao ideal."
        exit 0
        ;;
    *)
        echo "Uso: $0 [perto|medio|longe|off]" >&2
        exit 1
        ;;
esac

echo "Perfil de distância: ${PROFILE} (perda ${LOSS}, atraso ${DELAY})"
docker exec "$UE_CONTAINER" tc qdisc replace dev "$TUN" root netem loss "$LOSS" delay "$DELAY"
docker exec "$UE_CONTAINER" tc qdisc show dev "$TUN"
echo ""
confirm
echo ""
echo "➜ Perfil '${PROFILE}' ATIVO. Rode o teste de throughput para ver a banda."
