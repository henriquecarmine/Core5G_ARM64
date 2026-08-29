#!/bin/bash
# Alterna entre os projetos de forma EXCLUSIVA: desliga o que estiver no ar e
# sobe só o projeto escolhido. Os dois são independentes e pesados (RFSIM do
# Projeto 2 satura os 2 vCPUs), então rodar só um por vez é o correto.
#
# Uso: ./scripts/switch_project.sh <p1|p2|off>
# Emite linhas estruturadas para o painel + a saída crua dos sub-scripts
# (que o painel mostra no log ao vivo, ao lado dos passos):
#   PHASE|<texto>            -> atualiza o rótulo do spinner
#   STEP|<ok|fail>|<t>|<d>   -> passo concluído
#   DONE|<ok|fail>
# Qualquer outra linha = log cru do servidor.

TARGET="${1:-}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
P1_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"     # ~/server (Open5GS + UERANSIM)
P2_DIR="$P1_DIR/oai-cn-gnb-e2"             # OAI 5GC + gNB + FlexRIC
NONRT_DIR="$P1_DIR/nonrt-ric"              # Non-RT RIC (PMS + A1 sims) — parte do P2

phase() { echo "PHASE|$1"; }
emit()  { echo "STEP|$1|$2|$3"; }

down_p1() {
    phase "Desligando Projeto 1 (UERANSIM + Open5GS)…"
    local rc=0
    ( cd "$P1_DIR" && ./scripts/down_ran.sh ) 2>&1 || rc=1
    ( cd "$P1_DIR" && ./scripts/down_core.sh ) 2>&1 || rc=1
    if [ "$rc" -eq 0 ]; then
        emit ok "Projeto 1 desligado" "UERANSIM e Open5GS parados."
    else
        emit fail "Projeto 1 não parou por inteiro" "Algo do UERANSIM/Open5GS continua no ar — veja o log ao lado."
    fi
    return "$rc"
}

down_p2() {
    phase "Desligando Projeto 2 (gNB/RIC + OAI Core + Non-RT RIC)…"
    local rc=0
    ( cd "$P2_DIR" && ./scripts/down_e2_lab.sh ) 2>&1 || rc=1
    # Core OAI é o v2 (oai-cn5g-v2); down_core.sh v1 não para os containers v2.
    ( cd "$P2_DIR/oai-cn5g-v2" && ./down_core_v2.sh ) 2>&1 || rc=1
    # Non-RT RIC é melhor esforço (pode nem estar instalado): não conta para o rc.
    [ -x "$NONRT_DIR/down_nonrt.sh" ] && { ( cd "$NONRT_DIR" && ./down_nonrt.sh ) 2>&1 || true; }
    if [ "$rc" -eq 0 ]; then
        emit ok "Projeto 2 desligado" "gNB, near-RT RIC, Non-RT RIC e OAI Core parados."
    else
        emit fail "Projeto 2 não parou por inteiro" "gNB/RIC ou o OAI Core continuam no ar — veja o log ao lado."
    fi
    return "$rc"
}

case "$TARGET" in
    p1)
        down_p2
        phase "Subindo Open5GS Core (Projeto 1)…"
        if ( cd "$P1_DIR" && ./scripts/up.sh ) 2>&1; then
            emit ok "Open5GS Core no ar" "AMF/SMF/UPF/AUSF/UDM/UDR/NRF + UPF redundante."
        else
            emit fail "Open5GS Core" "Falha ao subir o core do Projeto 1."; echo "DONE|fail"; exit 0
        fi
        phase "Subindo RAN (UERANSIM gNB + UE)…"
        if ( cd "$P1_DIR" && ./scripts/up_ran.sh ) 2>&1; then
            emit ok "RAN no ar (UERANSIM)" "gNB + UE simulados conectados via N2/N3."
        else
            emit fail "RAN (UERANSIM)" "Falha ao subir o RAN do Projeto 1."; echo "DONE|fail"; exit 0
        fi
        echo "DONE|ok"
        ;;
    p2)
        down_p1
        phase "Subindo OAI Core + near-RT RIC + gNB (Projeto 2)…"
        # up_e2_lab_v2.sh garante o core v2 (up_core_v2.sh) e sobe RIC+gNB.
        if ( cd "$P2_DIR" && ./scripts/up_e2_lab_v2.sh ) 2>&1; then
            emit ok "Projeto 2 no ar" "OAI 5GC + gNB (E2 agent) + FlexRIC near-RT RIC prontos."
        else
            emit fail "Projeto 2" "Falha ao subir o lab E2 do Projeto 2."; echo "DONE|fail"; exit 0
        fi
        # Non-RT RIC (leve): completa a pilha O-RAN do P2. Melhor esforço — sem
        # as imagens (docker load pendente) o switch não falha por causa dele.
        if [ -x "$NONRT_DIR/up_nonrt.sh" ]; then
            phase "Subindo Non-RT RIC (PMS + A1 sims)…"
            if ( cd "$NONRT_DIR" && ./up_nonrt.sh ) 2>&1; then
                emit ok "Non-RT RIC no ar" "PMS (políticas A1) + 3 A1 Simulators prontos."
            else
                emit fail "Non-RT RIC" "Não subiu (imagens carregadas? ver docs/instalacao-nonrt-arm64.md) — P2 segue no ar sem ele."
            fi
        fi
        echo "DONE|ok"
        ;;
    off)
        # O painel (e o roteiro da apresentação) confiam neste DONE| para saber
        # se a máquina ficou de fato ociosa. Anunciar "ok" sem olhar era a falha
        # calada clássica: ninguém vê, e o lab segue queimando crédito.
        rc=0
        down_p1 || rc=1
        down_p2 || rc=1
        if [ "$rc" -eq 0 ]; then
            echo "DONE|ok"
        else
            echo "DONE|fail"
        fi
        ;;
    *)
        emit fail "Alvo inválido" "Use p1, p2 ou off."
        echo "DONE|fail"
        ;;
esac
