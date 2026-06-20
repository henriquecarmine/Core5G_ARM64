#!/bin/bash
# Teste de Registro do UE (N1/NAS) — Projeto 1.
# Verifica o fluxo de registro do UE conforme aula01 (slide 79): Initial UE
# Message → Registration → PDU Session, e o estado final REGISTERED + IP em
# uesimtun0.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"
# shellcheck source=lib/testlog.sh
source "$SCRIPT_DIR/lib/testlog.sh"

GNB_CONTAINER="ueransim"
AMF_CONTAINER="amf"
fails=0

section "Registro do UE (N1/NAS) — UERANSIM ↔ AMF"

if ! docker inspect -f '{{.State.Status}}' "$GNB_CONTAINER" 2>/dev/null | grep -q running; then
    err "Container $GNB_CONTAINER não está rodando. Ative o Projeto 1 + RAN."
    summary "tentou validar o registro do UE (NAS)" \
            "RAN do Projeto 1 não está no ar" err
    exit 0
fi

UE_LOG=$(docker logs "$GNB_CONTAINER" 2>&1)

step "1) Registration accept (AMF aceitou o UE)…"
if printf '%s' "$UE_LOG" | grep -qi "Registration accept"; then
    ok "Registration accept recebido — UE autenticado/registrado."
else
    warn "Sem 'Registration accept' no log do UE."
    fails=$((fails+1))
fi

step "2) Estado de mobilidade do UE…"
UE_STATE=$(printf '%s' "$UE_LOG" | grep "UE switches to state" | tail -1 | grep -oP "\[MM-[^\]]+\]" || true)
if printf '%s' "$UE_STATE" | grep -q "REGISTERED"; then
    ok "UE em estado $UE_STATE."
elif [ -n "$UE_STATE" ]; then
    warn "UE em estado $UE_STATE (ainda não REGISTERED)."
    fails=$((fails+1))
else
    warn "Não consegui ler o estado de mobilidade do UE."
    fails=$((fails+1))
fi

step "3) Sessão PDU + IP em uesimtun0 (plano de usuário pronto)…"
UE_IP=$(docker exec "$GNB_CONTAINER" ip addr show 2>/dev/null | grep -oP 'inet \K10\.60\.\d+\.\d+' | head -1 || true)
if [ -n "$UE_IP" ]; then
    ok "Sessão PDU estabelecida — uesimtun0 com IP $UE_IP."
else
    if printf '%s' "$UE_LOG" | grep -qi "PDU Session establishment"; then
        warn "PDU Session iniciada nos logs, mas sem IP em uesimtun0 ainda."
    else
        warn "Sem IP em uesimtun0 — sessão PDU não concluída (SMF/UPF/APN?)."
    fi
    fails=$((fails+1))
fi

step "4) Lado do AMF (Initial UE Message / Registration complete)…"
if docker inspect -f '{{.State.Status}}' "$AMF_CONTAINER" 2>/dev/null | grep -q running; then
    AMF_LOG=$(docker logs --tail 300 "$AMF_CONTAINER" 2>&1)
    if printf '%s' "$AMF_LOG" | grep -qiE "InitialUEMessage|Registration complete|Registration request|UE Context"; then
        ok "AMF registrou a sinalização NAS do UE."
    else
        info "AMF sem linha NAS recente no tail (pode ter logado antes)."
    fi
else
    warn "Container $AMF_CONTAINER não está rodando."
fi

if [ "$fails" -eq 0 ]; then
    summary "verificou o registro do UE: Registration accept, estado REGISTERED, sessão PDU (IP em uesimtun0) e sinalização NAS no AMF" \
            "UE registrado e com plano de usuário pronto (IP ${UE_IP:-—}) — pronto para tráfego" ok
else
    summary "verificou o registro do UE: Registration accept, estado REGISTERED, sessão PDU (IP em uesimtun0) e sinalização NAS no AMF" \
            "Registro incompleto — veja os passos marcados (assinante no UDM? APN/slice coerentes? SMF/UPF no ar?)" warn
fi
