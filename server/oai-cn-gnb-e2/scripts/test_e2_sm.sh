#!/bin/bash
# Executa xApps FlexRIC para testar Service Models via interface E2.
# Uso: ./scripts/test_e2_sm.sh [oran|cust|all|kpm|rc|gtp|kpm_rc|slice]
#
# Usa **apenas** xApps compilados no submodule FlexRIC (branch dev).
# Não utiliza /usr/local nem /opt/flexric (incompatíveis com o nearRT-RIC dev).
#
# Pré-requisitos:
#   - nearRT-RIC rodando (./scripts/up_flexric.sh)
#   - gNB com E2 agent (./scripts/up_gnb_oai.sh ou up_e2_lab.sh)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="${OAI_LOG_DIR:-$PROJECT_DIR/logs}"
DURATION="${XAPP_DURATION:-30}"
SM="${1:-cust}"
# shellcheck source=lib/testlog.sh
source "$SCRIPT_DIR/lib/testlog.sh"

E2_OK=0; SUBS=0; RAN_ANY=0   # acumuladores para o resumo final

FLEXRIC="$PROJECT_DIR/openairinterface5g/openair2/E2AP/flexric"
FLEXRIC_BUILD="$FLEXRIC/build"
XAPP_MONITOR="$FLEXRIC_BUILD/examples/xApp/c/monitor"
XAPP_KPM_RC="$FLEXRIC_BUILD/examples/xApp/c/kpm_rc"

mkdir -p "$LOG_DIR"

ensure_flexric_xapps() {
    local need=0
    for bin in xapp_gtp_mac_rlc_pdcp_moni xapp_rc_moni xapp_kpm_moni xapp_kpm_rc; do
        [ -x "$XAPP_MONITOR/$bin" ] || [ -x "$XAPP_KPM_RC/$bin" ] || need=1
    done
    if [ "$need" = "1" ]; then
        echo "Compilando xApps FlexRIC (submodule dev)..."
        "$SCRIPT_DIR/build_flexric_tools.sh"
    fi
}

resolve_xapp() {
    local name="$1"
    for dir in "$XAPP_MONITOR" "$XAPP_KPM_RC"; do
        if [ -x "$dir/$name" ]; then
            echo "$dir/$name"
            return 0
        fi
    done
    return 1
}

kill_stale_xapps() {
    pkill -f "/xapp_" 2>/dev/null || true
    sleep 1
}

ensure_ric_running() {
    if ! pgrep -x "nearRT-RIC" >/dev/null 2>&1; then
        step "nearRT-RIC não está rodando; iniciando..."
        "$SCRIPT_DIR/up_flexric.sh"
        sleep 2
    fi
    if ! pgrep -x "nearRT-RIC" >/dev/null 2>&1; then
        err "nearRT-RIC falhou ao iniciar (ver logs/nearRT-RIC.log)"
        exit 1
    fi
    ok "nearRT-RIC no ar (porta E2AP 36421)"
}

section "Teste E2 Service Models — O-RAN (gNB → E2 → near-RT RIC → xApps)"
ensure_flexric_xapps
ensure_ric_running
kill_stale_xapps

if ! pgrep -f "nr-softmodem" >/dev/null 2>&1; then
    err "gNB (nr-softmodem) NÃO está rodando — teste abortado."
    info "Sem o gNB não há nó E2 conectado ao RIC; cada xApp ficaria ${DURATION}s esperando à toa."
    info "Suba o Projeto 2: no painel use o seletor → Projeto 2, ou no servidor ./scripts/up_e2_lab.sh"
    info "Projeto 1 (Open5GS) e Projeto 2 (OAI) são mutuamente exclusivos — só um por vez."
    summary "tentou exercitar os Service Models via interface E2 com xApps do FlexRIC" \
            "abortado: gNB do Projeto 2 não está no ar (suba o Projeto 2 antes)" err
    exit 1
fi
ok "gNB (nr-softmodem) detectado — nó E2 disponível"

run_xapp() {
    local name="$1"
    local log_name="${2:-$name}"
    local log="$LOG_DIR/${log_name}.log"
    local bin
    bin="$(resolve_xapp "$name")" || {
        echo "ERRO: xApp '$name' não encontrado no build FlexRIC."
        echo "      Execute: ./scripts/build_flexric_tools.sh"
        exit 1
    }
    RAN_ANY=1
    step "executando $name por ${DURATION}s..."
    set +e
    timeout "$((DURATION + 20))" env XAPP_DURATION="$DURATION" "$bin" > "$log" 2>&1
    local rc=$?
    set -e
    if [ "$rc" -eq 124 ]; then
        info "timeout após ${DURATION}s (normal: o xApp roda por tempo fixo)"
    elif [ "$rc" -ne 0 ]; then
        warn "xApp terminou com código $rc (ver $log)"
        tail -5 "$log" 2>/dev/null | while IFS= read -r l; do warn "$l"; done || true
    fi
    # Contabiliza resultado para o resumo
    grep -qiE 'Connected E2 nodes *= *[1-9]' "$log" 2>/dev/null && E2_OK=1
    local s; s="$(grep -ciE 'Successfully subscribed' "$log" 2>/dev/null || echo 0)"
    SUBS=$((SUBS + s))
    grep -qiE 'Test xApp run SUCCESS' "$log" 2>/dev/null && ok "$name: ciclo assinar→indicação→cancelar OK"
    # Mostra as linhas relevantes coloridas
    grep -iE 'Connected E2 nodes|Successfully subscribed|Registered node|INDICATION|latency|Test xApp run SUCCESS' "$log" 2>/dev/null \
        | head -15 | while IFS= read -r l; do info "$l"; done || true
}

case "$SM" in
    oran)
        echo "=== E2SM-KPM + E2SM-RC (O-RAN) ==="
        echo "AVISO: xapp_oran_moni (/usr/local) é incompatível com este lab."
        echo "       Usando testes dedicados KPM + RC (submodule dev)..."
        KPM_SST="${KPM_SST:-222}" KPM_SD="${KPM_SD:-123}" \
            XAPP_DURATION="$DURATION" "$SCRIPT_DIR/test_e2_kpm.sh"
        XAPP_DURATION="$DURATION" run_xapp "xapp_rc_moni"
        ;;
    cust|custom|mac|rlc|pdcp|gtp)
        echo "=== MAC + RLC + PDCP + GTP (custom SMs, plain encoding) ==="
        echo "xApp: xapp_gtp_mac_rlc_pdcp_moni (submodule dev)"
        run_xapp "xapp_gtp_mac_rlc_pdcp_moni" "xapp_cust_moni"
        ;;
    all)
        echo "=== Todos os SMs suportados no submodule dev ==="
        run_xapp "xapp_gtp_mac_rlc_pdcp_moni" "xapp_cust_moni"
        run_xapp "xapp_rc_moni"
        run_xapp "xapp_kpm_moni"
        ;;
    kpm)
        echo "=== E2SM-KPM (slice lab SST=222 SD=123) ==="
        KPM_SST="${KPM_SST:-222}" KPM_SD="${KPM_SD:-123}" \
            XAPP_DURATION="$DURATION" "$SCRIPT_DIR/test_e2_kpm.sh"
        ;;
    rc)
        echo "=== E2SM-RC (monitor dedicado) ==="
        run_xapp "xapp_rc_moni"
        ;;
    gtp|layers)
        echo "=== MAC + RLC + PDCP + GTP ==="
        run_xapp "xapp_gtp_mac_rlc_pdcp_moni"
        ;;
    kpm_rc|kpm-rc)
        echo "=== E2SM-KPM monitor + E2SM-RC Control (PoC) ==="
        KPM_SST="${KPM_SST:-222}" KPM_SD="${KPM_SD:-123}" \
            XAPP_DURATION="$DURATION" run_xapp "xapp_kpm_rc"
        ;;
    slice)
        echo "=== SLICE SM (emulador FlexRIC; não suportado no OAI RAN) ==="
        echo "AVISO: SLICE/TC não estão disponíveis no agente E2 do gNB OAI monolítico."
        exit 1
        ;;
    *)
        echo "Uso: $0 [oran|cust|all|kpm|rc|gtp|kpm_rc|slice]"
        echo ""
        echo "  cust    - MAC, RLC, PDCP, GTP (plain) [padrão]"
        echo "  rc      - E2SM-RC"
        echo "  kpm     - E2SM-KPM (slice 222/123)"
        echo "  gtp     - MAC/RLC/PDCP/GTP"
        echo "  kpm_rc  - KPM + RC Control (PoC)"
        echo "  oran    - KPM + RC via scripts dedicados (não usa /usr/local)"
        echo "  all     - cust + rc + kpm"
        echo "  slice   - não suportado no OAI RAN"
        echo ""
        echo "Variáveis: XAPP_DURATION=30"
        exit 1
        ;;
esac

info "logs detalhados em: $LOG_DIR/"
if [ "$RAN_ANY" = 1 ]; then
    if [ "$E2_OK" = 1 ]; then
        summary "subiu o near-RT RIC, conectou o nó E2 do gNB e rodou xApps que leram os Service Models (KPM/RC/MAC/RLC/PDCP/GTP) pela interface E2" \
                "cadeia O-RAN provada fim-a-fim: gNB → E2 → RIC → xApps (${SUBS} assinatura(s) bem-sucedida(s))" ok
    else
        summary "rodou xApps do FlexRIC para exercitar os Service Models via E2" \
                "xApps rodaram, mas nenhum nó E2 conectou (gNB sem E2 SETUP) — verifique o gNB e o RIC" warn
    fi
fi
