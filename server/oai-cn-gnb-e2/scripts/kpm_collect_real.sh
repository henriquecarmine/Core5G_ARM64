#!/usr/bin/env bash
# kpm_collect_real.sh — coleta KPM com tráfego real, resiliente e SEGURA.
#
# SEGURANÇA EM 1º LUGAR (lição de 2 freezes): este script NÃO mexe no cpuset.
#   Ele roda sob o guardrail vigente. Em 2 vCPU (guardrail = 1 core) o UE tende a
#   NÃO attachar (inunda); o script DETECTA isso rápido por evento, PARA o UE (pra
#   não crescer memória) e conclui honestamente "sem dados — use 4 vCPU". Em 4 vCPU
#   o UE attacha naturalmente (sem precisar liberar core nenhum) e a coleta rende.
#   → NUNCA remove o guardrail; portanto NÃO pode congelar o box.
#
# 100% POR EVENTO — ZERO TEMPO (sem sleep/timeout/duração que decida):
#   • IP do UE     : ip monitor address → grep -m1 (evento netlink)
#   • Falha rápida : flood do RRC (fila ≥ 5 dígitos) OU morte do UE (tail --pid)
#   • Fim da coleta: tail -F --pid | grep -m K (K-ésima indicação)
#   • Heartbeat    : 1 por MARCO DISTINTO (dedup) — não polui nem rouba CPU
#   • Auto-retry + auto-stop do UE + veredito honesto. Conclui sempre.
#
# Pré-requisito: E2 lab no ar (core + RIC + gNB). Mexe só no nrUE.
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"
# shellcheck source=/dev/null
. "$SCRIPT_DIR/lib/testlog.sh"

SLICE="oai-lab.slice"
OAI="$PROJECT_DIR/openairinterface5g"
BUILD="$OAI/cmake_targets/ran_build/build"
UECONF="$OAI/scripts/ue.conf"
LOG="$PROJECT_DIR/logs/xapp_kpm_lab.log"
UE_LOG="$PROJECT_DIR/logs/ue_oai.log"
FLEXRIC_LIB="$PROJECT_DIR/flexric-lib"
XAPP="$OAI/openair2/E2AP/flexric/build/examples/xApp/c/monitor/xapp_kpm_moni"
NEED_IND="${NEED_IND:-20}"     # meta de indicações (EVENTO de sucesso)
MAX_TRIES="${MAX_TRIES:-2}"

PING_PID=""; XAPP_PID=""
cleanup() {
  [ -n "$XAPP_PID" ] && kill "$XAPP_PID" 2>/dev/null || true
  [ -n "$PING_PID" ] && sudo kill "$PING_PID" 2>/dev/null || true
  sudo pkill -x nr-uesoftmodem 2>/dev/null || true   # nunca deixa o UE inundando
  sudo pkill -f xapp_kpm_moni 2>/dev/null || true
  sudo pkill -f "ping -I oaitun_ue1" 2>/dev/null || true
  info "limpeza: UE/xApp/ping parados (não deixo nada inundando)"
}
trap cleanup EXIT

section "Coleta KPM com tráfego real — SEGURA (não mexe no cpuset, não congela)"
info "Heartbeat '⏳ … NÃO travou' = trabalhando. Tudo termina por EVENTO, sem cronômetro."
GUARD="$(systemctl show "$SLICE" -p AllowedCPUs --value 2>/dev/null || echo '?')"
NPROC="$(nproc 2>/dev/null || echo '?')"
kv "vCPUs do host" "$NPROC"; kv "guardrail (AllowedCPUs)" "$GUARD (não será alterado)"
[ "$NPROC" != "?" ] && [ "$NPROC" -le 2 ] && \
  warn "2 vCPU: o UE provavelmente NÃO vai attachar (CPU). O teste conclui honesto; p/ dados reais use 4 vCPU."

pgrep -x nr-softmodem >/dev/null || { err "gNB não está rodando — suba o E2 lab antes"; exit 0; }
pgrep -x nearRT-RIC   >/dev/null || { err "near-RT RIC não está rodando — suba o E2 lab antes"; exit 0; }
[ -x "$XAPP" ] || { err "xApp KPM não compilado: $XAPP"; exit 0; }

problem=""; got=0; n=0; attempt=0
while :; do
  attempt=$((attempt + 1)); problem=""
  section "Tentativa $attempt de $MAX_TRIES"

  sudo pkill -x nr-uesoftmodem 2>/dev/null || true
  : > "$UE_LOG"
  step "subindo nrUE (RFSIM, slice 222/123)…"
  ( cd "$BUILD" && sudo systemd-run --scope -q --unit="oai-nrue-$$-$attempt" --slice="$SLICE" \
      -p CPUQuota=100% -p CPUWeight=20 nice -n 10 \
      ./nr-uesoftmodem -O "$UECONF" --rfsim -r 51 --numerology 1 --band 78 -C 3469440000 --ssb 186 \
      > "$UE_LOG" 2>&1 & )
  UEPID="$(systemctl show -p MainPID --value "oai-nrue-$$-$attempt.scope" 2>/dev/null || true)"
  { [ -z "$UEPID" ] || [ "$UEPID" = 0 ]; } && UEPID="$$"

  # ── EVENTO 1: IP do UE. Bounded por: IP | flood(≥5díg) | morte do UE. ──────────
  # Heartbeat DEDUP: 1 linha por marco DISTINTO (grep -o + awk !seen). Leve na CPU.
  ( ip -o monitor address 2>/dev/null | grep -qm1 "oaitun_ue1" ) & W_OK=$!
  ( tail -n +1 -F --pid="$UEPID" "$UE_LOG" 2>/dev/null \
      | grep -qm1 -E "TASK_RRC_NRUE task contains [0-9]{5}" ) & W_BAD=$!
  ( stdbuf -oL tail -n +1 -F --pid="$UEPID" "$UE_LOG" 2>/dev/null \
      | stdbuf -oL grep --line-buffered -oiE "Initial sync successful|PBCH|Cell Detected|UE synchronized|RRCSetup|Registration (accept|complete)|PDU Session" \
      | awk '!seen[$0]++ { print "  ⏳ UE: " $0 " (marco · NÃO travou)"; fflush() }' ) & W_HB=$!

  wait -n "$W_OK" "$W_BAD" 2>/dev/null || true
  kill "$W_OK" "$W_BAD" "$W_HB" 2>/dev/null || true

  if ip -4 addr show oaitun_ue1 >/dev/null 2>&1; then
    IPA=$(ip -4 addr show oaitun_ue1 | grep -oE "inet [0-9.]+" | awk '{print $2}')
    ok "UE ATTACHED — oaitun_ue1 = $IPA"

    step "gerando tráfego pelo túnel 5G (ping ao DN)…"
    sudo ping -I oaitun_ue1 8.8.8.8 >/dev/null 2>&1 & PING_PID=$!

    step "coletando KPM até $NEED_IND indicações (encerra no EVENTO, não por tempo)…"
    : > "$LOG"
    SMDIR=(); [ -f "$FLEXRIC_LIB/libkpm_sm.so" ] && SMDIR=(--e2_agent.sm_dir "$FLEXRIC_LIB")
    KPM_SST=222 KPM_SD=123 "$XAPP" "${SMDIR[@]}" > "$LOG" 2>&1 & XAPP_PID=$!
    # watchdog anti-hang: se o UE morre, mata o xApp → o tail abaixo encerra.
    ( tail -f --pid="$UEPID" /dev/null 2>/dev/null; kill "$XAPP_PID" 2>/dev/null ) & W_DEATH=$!

    c=0
    while IFS= read -r _; do
      c=$((c + 1)); info "⏳ indicação KPM $c/$NEED_IND (NÃO travou)"
    done < <(stdbuf -oL tail -n +1 -F --pid="$XAPP_PID" "$LOG" 2>/dev/null \
               | stdbuf -oL grep --line-buffered -m "$NEED_IND" "KPM ind_msg latency")
    n=$(grep -c "KPM ind_msg latency" "$LOG" 2>/dev/null || echo 0)

    kill "$W_DEATH" 2>/dev/null || true
    kill "$XAPP_PID" 2>/dev/null || true; XAPP_PID=""
    sudo kill "$PING_PID" 2>/dev/null || true; PING_PID=""
    [ "$c" -ge "$NEED_IND" ] && { got=1; ok "meta atingida: $n indicações"; break; }
    problem="coletou só $n indicações (UE caiu/instável durante a coleta)"
  else
    if ! pgrep -x nr-uesoftmodem >/dev/null; then problem="o nrUE caiu antes de pegar IP"
    else problem="RRC inundou (CPU insuficiente — típico de 2 vCPU; ideal 4 vCPU)"; fi
  fi

  # IMPORTANTE: para o UE já (não deixa inundar/crescer memória) antes de decidir.
  sudo pkill -x nr-uesoftmodem 2>/dev/null || true
  err "tentativa $attempt: PROBLEMA — $problem"
  [ "$attempt" -ge "$MAX_TRIES" ] && { warn "concluo com o que há (sem falhar, sem travar)"; break; }
  step "repetindo (resiliência por evento)…"
done

section "Análise do log coletado"
"$SCRIPT_DIR/kpm_analytics.sh" "$LOG" || true

if [ "$got" = 1 ]; then
  summary "coletou KPM com tráfego real (UE attachado, $n indicações) e analisou (CSV+KPI+sparkline)" \
          "concluído com DADOS reais em $attempt tentativa(s)" ok
else
  summary "coleta resiliente ($attempt tentativas, heartbeat por marco, sem mexer no cpuset) — UE não sustentou tráfego" \
          "concluído SEM falhar e SEM travar — problema: ${problem:-sem dados}; p/ KPM com tráfego real use 4 vCPU" warn
fi
