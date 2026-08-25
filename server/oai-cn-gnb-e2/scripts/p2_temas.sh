#!/usr/bin/env bash
# p2_temas.sh — os 7 temas do Projeto Integrador (Análise de Dados em Redes de
# Telecom, Prof. Kunzler) sobre a telemetria KPM, no console do painel.
#   uso: ./scripts/p2_temas.sh t1|t2|...|t7|all
# Fonte dos dados (nesta ordem): KPM_FILE (dado enviado/colado pelo professor
# no painel) > amostra oficial do professor (kpm-ue-tp-sample, 100 amostras).
# Se KPM_SOURCE=real, usa o CSV da última coleta E2 (logs/kpm_timeseries.csv).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=/dev/null
. "$SCRIPT_DIR/lib/testlog.sh"

TEMA="${1:-all}"
EXP="$SCRIPT_DIR/temas/temas_projeto.py"
SAMPLE="$SCRIPT_DIR/temas/samples/kpm_ue_tp_sample.jsonl"
REAL="$PROJECT_DIR/logs/kpm_timeseries.csv"
PY="$(command -v python3 || true)"

declare -A NOME=( [t1]="Vazão do usuário (UE-TP)" [t2]="Detecção de anomalia de carga"
  [t3]="Latência e qualidade percebida (QoE)" [t4]="Risco de congestionamento"
  [t5]="Visão agregada da célula" [t6]="Economia de energia (só intenção)"
  [t7]="Política de QoS / steering (candidata)" [all]="os 7 temas lado a lado" )

section "Projeto Integrador — ${NOME[$TEMA]:-$TEMA}"
info "Mesmos dados para todos os grupos; muda a pergunta, os 2 indicadores e a recomendação."
kv "Disciplina" "Análise de Dados em Redes de Telecom (Prof. Dr. Jonas A. Kunzler)"
kv "Onde no O-RAN" "gNB (E2SM-KPM) → xApp → arquivo → análise aqui no painel; política A1 só em dry-run"

section "1. Pré-condições"
if [ -z "$PY" ]; then
    err "python3 não encontrado"; summary "procurou o interpretador" "python indisponível" err; exit 1
fi
if [ -n "${KPM_FILE:-}" ] && [ -f "$KPM_FILE" ]; then
    DATA="$KPM_FILE"; ok "fonte: dados enviados pelo professor no painel"
elif [ "${KPM_SOURCE:-}" = "real" ] && [ -f "$REAL" ]; then
    DATA="$REAL"; ok "fonte: última coleta E2 real desta RAN (kpm_analytics)"
else
    DATA="$SAMPLE"; ok "fonte: amostra oficial do professor (kpm-ue-tp-sample, 100 amostras, 3 fases)"
fi
[ -f "$DATA" ] || { err "arquivo de dados ausente: $DATA"; summary "procurou a telemetria KPM" "sem dados" err; exit 1; }
kv "Arquivo" "$DATA"
kv "Interpretador" "$PY (só biblioteca padrão)"

section "2. Indicadores, fórmulas e recomendação"
step "lendo o KPM (zona silver), calculando os indicadores do tema…"
OUT="$(mktemp)"; trap 'rm -f "$OUT"' EXIT
if "$PY" -u "$EXP" --tema "$TEMA" --file "$DATA" | tee "$OUT"; then
    VER="$(sed 's/\x1b\[[0-9;]*m//g' "$OUT" | grep -m1 '^Veredito:' | cut -d: -f2- | sed 's/^ *//')"
    summary "calculou os 2 indicadores de ${NOME[$TEMA]:-$TEMA} sobre a telemetria KPM" \
            "${VER:-veja a leitura acima}" ok
else
    rc=${PIPESTATUS[0]}
    err "a análise falhou (rc=$rc): o arquivo tem as 3 métricas (thp_ul, delay_dl, prb_ul)?"
    summary "tentou calcular os indicadores do tema" "falhou ao analisar os dados" err
    exit "$rc"
fi
