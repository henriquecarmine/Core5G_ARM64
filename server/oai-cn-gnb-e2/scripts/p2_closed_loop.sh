#!/usr/bin/env bash
# p2_closed_loop.sh — o closed loop A1 das Aulas 05 e 06 (Analise de Dados em
# Redes de Telecom), OFFLINE: os 8 passos do roteiro da demo (baseline calmo →
# stress → decisao MAD → policy A1 → action_request → effect_report → rollback)
# sobre a mesma telemetria dos 7 temas, com os artefatos do lab do professor.
# Nada e aplicado na RAN: o tc e o envio ao PMS sao so impressos.
#   uso: ./scripts/p2_closed_loop.sh
# Fonte dos dados (nesta ordem): KPM_FILE (enviado/colado pelo professor no
# painel) > amostra oficial do professor.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=/dev/null
. "$SCRIPT_DIR/lib/testlog.sh"

EXP="$SCRIPT_DIR/temas/closed_loop.py"
SAMPLE="$SCRIPT_DIR/temas/samples/kpm_ue_tp_sample.jsonl"
OUT_DIR="$PROJECT_DIR/logs/closed_loop_offline"
PY="$(command -v python3 || true)"

section "Aulas 05 e 06 — Closed loop A1 (offline)"
info "Telemetria → decisao → policy → atuacao → evidencia, no formato dos artefatos do lab do professor."
kv "Disciplina" "Analise de Dados em Redes de Telecom (Prof. Dr. Jonas A. Kunzler)"
kv "Slides" "aula05-closed-loop-a1-open-ran.pdf · aula06-consolidacao_projetos.pdf"
kv "Onde no O-RAN" "rApp (Non-RT) decide → PMS/A1 → consumer (Near-RT) → actuator; aqui tudo em dry-run"

section "Pre-condicoes"
if [ -z "$PY" ]; then
    err "python3 nao encontrado"; summary "procurou o interpretador" "python indisponivel" err; exit 1
fi
if [ -n "${KPM_FILE:-}" ] && [ -f "$KPM_FILE" ]; then
    DATA="$KPM_FILE"; ok "fonte: arquivo escolhido no painel (enviado pelo professor ou cenario sugerido pelo servidor)"
else
    DATA="$SAMPLE"; ok "fonte: amostra oficial do professor (kpm-ue-tp-sample, 100 amostras, 3 fases)"
fi
[ -f "$DATA" ] || { err "arquivo de dados ausente: $DATA"; summary "procurou a telemetria KPM" "sem dados" err; exit 1; }
kv "Arquivo" "$DATA"
kv "Artefatos" "$OUT_DIR (sobrescritos a cada execucao)"

step "percorrendo os 8 passos do roteiro…"
OUT="$(mktemp)"; trap 'rm -f "$OUT"' EXIT
rm -rf "$OUT_DIR"
if "$PY" -u "$EXP" --file "$DATA" --out "$OUT_DIR" | tee "$OUT"; then
    VER="$(sed 's/\x1b\[[0-9;]*m//g' "$OUT" | grep -m1 '^Veredito:' | cut -d: -f2- | sed 's/^ *//')"
    summary "percorreu o closed loop A1 das aulas 05 e 06 em dry-run e gravou os artefatos" \
            "${VER:-veja a leitura acima}" ok
else
    rc=${PIPESTATUS[0]}
    err "o closed loop falhou (rc=$rc): o arquivo tem as 3 metricas (thp_ul, delay_dl, prb_ul) e fases?"
    summary "tentou percorrer o closed loop" "falhou ao analisar os dados" err
    exit "$rc"
fi
