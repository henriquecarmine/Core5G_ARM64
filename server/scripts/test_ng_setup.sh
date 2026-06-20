#!/bin/bash
# Teste NG Setup (N2) — Projeto 1.
# Verifica o procedimento NG Setup entre o gNB (UERANSIM) e o AMF (Open5GS),
# conforme aula01 (slide 76): associação SCTP + NGSetupRequest/Response.
# Log típico de sucesso: "NG Setup procedure is successful".

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"
# shellcheck source=lib/testlog.sh
source "$SCRIPT_DIR/lib/testlog.sh"

GNB_CONTAINER="ueransim"
AMF_CONTAINER="amf"
fails=0

section "NG Setup (N2) — gNB (UERANSIM) ↔ AMF (Open5GS)"

if ! docker inspect -f '{{.State.Status}}' "$GNB_CONTAINER" 2>/dev/null | grep -q running; then
    err "Container $GNB_CONTAINER não está rodando. Suba o RAN (Projeto 1) primeiro."
    summary "tentou validar o NG Setup (N2) entre gNB e AMF" \
            "RAN do Projeto 1 não está no ar — ative o Projeto 1 e o servidor RAN" err
    exit 0
fi

GNB_LOG=$(docker logs "$GNB_CONTAINER" 2>&1)

step "Procurando NGSetupResponse no log do gNB…"
NG_OK=$(printf '%s' "$GNB_LOG" | grep -ci "NG Setup procedure is successful")
if [ "$NG_OK" -gt 0 ]; then
    ok "gNB recebeu NGSetupResponse — N2 estabelecida ($NG_OK ocorrência(s))."
else
    if printf '%s' "$GNB_LOG" | grep -qi "NG Setup.*fail\|NGSetupFailure"; then
        err "NGSetupFailure no log do gNB — AMF rejeitou (PLMN/TAC/slice?)."
    else
        warn "Não encontrei 'NG Setup procedure is successful' no log do gNB."
    fi
    fails=$((fails+1))
fi

step "Conferindo associação SCTP/NGAP no AMF…"
if docker inspect -f '{{.State.Status}}' "$AMF_CONTAINER" 2>/dev/null | grep -q running; then
    AMF_LOG=$(docker logs --tail 200 "$AMF_CONTAINER" 2>&1)
    if printf '%s' "$AMF_LOG" | grep -qiE "ng-?setup|gNB-N2|NGAP.*gNB|\[gNB\]"; then
        ok "AMF registrou atividade NGAP do gNB (N2 ativa)."
        printf '%s' "$AMF_LOG" | grep -iE "ng-?setup|gNB-N2" | tail -2 | sed 's/^/    /'
    else
        info "AMF rodando, mas sem linha NGAP recente no tail (pode já ter logado antes)."
    fi
else
    warn "Container $AMF_CONTAINER não está rodando — não dá para cruzar com o AMF."
    fails=$((fails+1))
fi

if [ "$fails" -eq 0 ]; then
    summary "verificou o NG Setup (N2): NGSetupResponse no gNB + associação NGAP no AMF" \
            "N2 estabelecida — o gNB está conectado ao AMF (NG Setup com sucesso)" ok
else
    summary "verificou o NG Setup (N2): NGSetupResponse no gNB + associação NGAP no AMF" \
            "N2 não confirmada — veja os itens marcados acima (gNB/AMF no ar? PLMN/TAC coerentes?)" warn
fi
