#!/bin/bash
# Configura o canal de rádio simulado em uesimtun0 via tc netem,
# combinando os efeitos de distância (path loss 3GPP TR 38.901 UMa NLOS)
# e interferência (C/I ratio baseado em Shannon–Hartley).
# Uso: ./test_channel.sh [distance] [interference]
#   distance    : none | 100m | 500m | 1km | 3km | off
#   interference: none | fraca | media | alta
# Exemplo: ./test_channel.sh 500m media

set -e
UE_CONTAINER="ueransim"
DISTANCE="${1:-none}"
INTERFERENCE="${2:-none}"

# --- off: limpar qualquer qdisc ativo ---
if [ "$DISTANCE" = "off" ]; then
    echo "Removendo configuração de canal (uesimtun0)"
    docker exec "$UE_CONTAINER" tc qdisc del dev uesimtun0 root 2>/dev/null \
        || echo "(nenhuma configuração ativa)"
    exit 0
fi

# --- Parâmetros de distância ---
# Modelo: 3GPP TR 38.901, UMa NLOS, f_c = 3.5 GHz, h_UT = 1.5 m
# PL(d) = 13.54 + 39.08·log₁₀(d) + 20·log₁₀(3.5) − 0.6·(h_UT−1.5)
# RSRP estimado assumindo P_tx=46 dBm + G_tx=12 dBi − PL
case "$DISTANCE" in
    none) D_DELAY=0;  D_LOSS=0;  D_JITTER=0
          D_INFO="canal ideal (sem atenuação de percurso)"
          ;;
    100m) D_DELAY=1;  D_LOSS=0;  D_JITTER=0
          D_INFO="PL = 102.6 dB  ·  RSRP ≈ −44 dBm  ·  delay prop. ≈ 0.33 µs → 1 ms (processing)"
          ;;
    500m) D_DELAY=8;  D_LOSS=2;  D_JITTER=1
          D_INFO="PL = 129.9 dB  ·  RSRP ≈ −72 dBm  ·  delay = 8 ms"
          ;;
    1km)  D_DELAY=20; D_LOSS=8;  D_JITTER=3
          D_INFO="PL = 141.7 dB  ·  RSRP ≈ −84 dBm  ·  delay = 20 ms"
          ;;
    3km)  D_DELAY=50; D_LOSS=20; D_JITTER=8
          D_INFO="PL = 159.6 dB  ·  RSRP ≈ −102 dBm  ·  delay = 50 ms (borda da célula)"
          ;;
    *)    echo "Distância inválida: $DISTANCE (use none|100m|500m|1km|3km|off)" >&2; exit 1 ;;
esac

# --- Parâmetros de interferência ---
# Modelo: SINR = C/(N₀+I) → C = B·log₂(1+SINR) [Shannon–Hartley, B=100 MHz 5G NR]
case "$INTERFERENCE" in
    none)  I_DELAY=0;  I_LOSS=0;  I_JITTER=0
           I_INFO="sem interferência"
           ;;
    fraca) I_DELAY=5;  I_LOSS=1;  I_JITTER=2
           I_INFO="C/I > 20 dB  ·  SINR ≈ 20 dB  ·  C_max ≈ 665 Mbps (B=100MHz)  ·  PDR 99%"
           ;;
    media) I_DELAY=20; I_LOSS=5;  I_JITTER=8
           I_INFO="C/I ≈ 15 dB  ·  SINR ≈ 15 dB  ·  C_max ≈ 498 Mbps (B=100MHz)  ·  PDR 95%"
           ;;
    alta)  I_DELAY=50; I_LOSS=15; I_JITTER=20
           I_INFO="C/I < 10 dB  ·  SINR ≈  5 dB  ·  C_max ≈ 207 Mbps (B=100MHz)  ·  PDR 85%"
           ;;
    *)     echo "Interferência inválida: $INTERFERENCE (use none|fraca|media|alta)" >&2; exit 1 ;;
esac

# --- Combinar parâmetros ---
TOTAL_DELAY=$(( D_DELAY + I_DELAY ))
# Loss combinada: 1−(1−p₁)(1−p₂) ≈ p₁+p₂ para p pequenos
TOTAL_LOSS=$(( D_LOSS + I_LOSS - D_LOSS * I_LOSS / 100 ))
TOTAL_JITTER=$(( D_JITTER + I_JITTER ))

echo "=== Configuração do Canal 5G Simulado ==="
echo ""
echo "Distância: ${DISTANCE}"
echo "  ${D_INFO}"
echo ""
echo "Interferência: ${INTERFERENCE}"
echo "  ${I_INFO}"
echo ""
echo "tc netem combinado:"
echo "  delay ${TOTAL_DELAY}ms  jitter ${TOTAL_JITTER}ms  loss ${TOTAL_LOSS}%"
echo ""

if [ "$TOTAL_DELAY" -eq 0 ] && [ "$TOTAL_LOSS" -eq 0 ]; then
    # Canal ideal: remover qdisc se existir
    docker exec "$UE_CONTAINER" tc qdisc del dev uesimtun0 root 2>/dev/null \
        || true
    echo "Canal ideal: nenhuma restrição aplicada."
else
    docker exec "$UE_CONTAINER" tc qdisc replace dev uesimtun0 root netem \
        delay "${TOTAL_DELAY}ms" jitter "${TOTAL_JITTER}ms" loss "${TOTAL_LOSS}%"
    echo "Aplicado. Estado atual:"
    docker exec "$UE_CONTAINER" tc qdisc show dev uesimtun0
fi
