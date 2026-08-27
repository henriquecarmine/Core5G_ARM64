#!/usr/bin/env bash
# p2_aula04.sh — a cadeia da Aula 04 (Analise de Dados em Redes de Telecom):
# medida KPM → KPI → KQI → QoS (SLA didatico) → QoE (proxy) → decisao, sobre a
# mesma telemetria dos 7 temas, terminando na anatomia dos indicadores do
# Checkpoint 2.
#   uso: ./scripts/p2_aula04.sh
# Fonte dos dados (nesta ordem): KPM_FILE (enviado/colado pelo professor no
# painel) > coleta E2 real (KPM_SOURCE=real) > amostra oficial do professor.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=/dev/null
. "$SCRIPT_DIR/lib/testlog.sh"

EXP="$SCRIPT_DIR/temas/aula04_indicadores.py"
SAMPLE="$SCRIPT_DIR/temas/samples/kpm_ue_tp_sample.jsonl"
REAL="$PROJECT_DIR/logs/kpm_timeseries.csv"
PY="$(command -v python3 || true)"

section "Aula 04 — Indicadores e qualidade (KPI · KQI · QoS · QoE)"
info "Da medicao de rede a experiencia percebida: cada degrau com a formula do slide, a unidade e o limiar."
kv "Disciplina" "Analise de Dados em Redes de Telecom (Prof. Dr. Jonas A. Kunzler)"
kv "Slides" "aula04-kpis_kqis_qualidade.pdf (25/08/2026)"
kv "Onde no O-RAN" "gNB (E2SM-KPM) → xApp → arquivo → indicadores aqui no painel; nada e aplicado na RAN"

section "1. Pre-condicoes"
if [ -z "$PY" ]; then
    err "python3 nao encontrado"; summary "procurou o interpretador" "python indisponivel" err; exit 1
fi
if [ -n "${KPM_FILE:-}" ] && [ -f "$KPM_FILE" ]; then
    DATA="$KPM_FILE"; ok "fonte: dados enviados pelo professor no painel"
elif [ "${KPM_SOURCE:-}" = "real" ] && [ -f "$REAL" ]; then
    DATA="$REAL"; ok "fonte: ultima coleta E2 real desta RAN (kpm_analytics)"
else
    DATA="$SAMPLE"; ok "fonte: amostra oficial do professor (kpm-ue-tp-sample, 100 amostras, 3 fases)"
fi
[ -f "$DATA" ] || { err "arquivo de dados ausente: $DATA"; summary "procurou a telemetria KPM" "sem dados" err; exit 1; }
kv "Arquivo" "$DATA"
kv "Interpretador" "$PY (so biblioteca padrao)"

section "2. A cadeia medida → KPI → KQI → QoS → QoE"
step "lendo o KPM, calculando os indicadores e confrontando com as clausulas…"
OUT="$(mktemp)"; trap 'rm -f "$OUT"' EXIT
if "$PY" -u "$EXP" --file "$DATA" | tee "$OUT"; then
    VER="$(sed 's/\x1b\[[0-9;]*m//g' "$OUT" | grep -m1 '^Veredito:' | cut -d: -f2- | sed 's/^ *//')"
    summary "percorreu a cadeia da Aula 04 e montou a anatomia dos indicadores do Checkpoint 2" \
            "${VER:-veja a leitura acima}" ok
else
    rc=${PIPESTATUS[0]}
    err "a analise falhou (rc=$rc): o arquivo tem as 3 metricas (thp_ul, delay_dl, prb_ul)?"
    summary "tentou percorrer a cadeia da Aula 04" "falhou ao analisar os dados" err
    exit "$rc"
fi
