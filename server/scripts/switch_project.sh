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

phase() { echo "PHASE|$1"; }
emit()  { echo "STEP|$1|$2|$3"; }

down_p1() {
    phase "Desligando Projeto 1 (UERANSIM + Open5GS)…"
    ( cd "$P1_DIR" && ./scripts/down_ran.sh ) 2>&1 || true
    ( cd "$P1_DIR" && ./scripts/down_core.sh ) 2>&1 || true
    emit ok "Projeto 1 desligado" "UERANSIM e Open5GS parados."
}

down_p2() {
    phase "Desligando Projeto 2 (gNB/RIC + OAI Core)…"
    ( cd "$P2_DIR" && ./scripts/down_e2_lab.sh ) 2>&1 || true
    # Core OAI é o v2 (oai-cn5g-v2); down_core.sh v1 não para os containers v2.
    ( cd "$P2_DIR/oai-cn5g-v2" && ./down_core_v2.sh ) 2>&1 || true
    emit ok "Projeto 2 desligado" "gNB, near-RT RIC e OAI Core parados."
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
        echo "DONE|ok"
        ;;
    off)
        down_p1
        down_p2
        echo "DONE|ok"
        ;;
    *)
        emit fail "Alvo inválido" "Use p1, p2 ou off."
        echo "DONE|fail"
        ;;
esac
