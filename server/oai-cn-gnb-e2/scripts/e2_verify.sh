#!/bin/bash
# Sobe o E2 lab e valida + roda os xApps 7x cada — 100% EVENT-DRIVEN.
# Nada de timeout/sleep cego: espera o EVENTO "E2 SETUP RESPONSE" no log do gNB
# (bloqueia até o evento ou até o gNB morrer, via tail --pid), e cada teste
# (run_xapp) encerra no 1º evento de sucesso do E2.
# Uso: ./scripts/e2_verify.sh   (resultado em /tmp/e2_verify.log)
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"
R=/tmp/e2_verify.log; : > "$R"
log(){ echo "[$(date +%H:%M:%S)] $*" >> "$R"; }

# Trunca o log do gNB pra só observar os eventos DESTE bring-up (evita match antigo)
: > "$PROJECT_DIR/logs/gnb_oai.log" 2>/dev/null || true

# Validação de xApp = sobe SEM nrUE (SKIP_UE=1) por padrão: no box de 2 vCPUs,
# rodar gNB+nrUE em RFSIM satura os núcleos e o xApp estoura o timeout interno
# do FlexRIC. Sem o UE sobra 1 vCPU p/ RIC+xApp e a validação fica determinística.
# (E2 é gNB↔RIC, independe do UE.) Override: SKIP_UE=0 ./e2_verify.sh
export SKIP_UE="${SKIP_UE:-1}"
log "Subindo E2 lab (core v2 + RIC + gNB; SKIP_UE=$SKIP_UE)..."
"$SCRIPT_DIR/up_e2_lab_v2.sh" >> "$R" 2>&1

log "Aguardando EVENTO 'E2 SETUP RESPONSE' (condição, sem captura de PID)..."
# Espera o evento aparecer; quebra (falha) se o gNB sumir. Sem timeout, sem race.
while ! grep -q 'E2 SETUP RESPONSE' "$PROJECT_DIR/logs/gnb_oai.log" 2>/dev/null; do
    pgrep -x nr-softmodem >/dev/null || { log "FALHA: gNB caiu sem E2 setup."; log "DONE"; exit 1; }
    sleep 1
done
log "EVENTO confirmado: E2 setup gNB<->RIC."

log "Rodando xApps 7x cada (event-driven — encerram no 1o evento de E2)..."
for t in cust kpm rc; do
    ok=0
    for i in 1 2 3 4 5 6 7; do
        if "$SCRIPT_DIR/run_xapp.sh" "$t" >> "$R" 2>&1; then ok=$((ok+1)); fi
    done
    log ">>> $t: $ok/7 OK"
done

UE_IP=$(ip -4 addr show oaitun_ue1 2>/dev/null | grep -oP 'inet \K[0-9.]+' || true)
[ -n "$UE_IP" ] && log "UE attachado: $UE_IP (user plane ativo)" \
                || log "UE: sem oaitun no momento (xApps independem disso)."
log "DONE"
