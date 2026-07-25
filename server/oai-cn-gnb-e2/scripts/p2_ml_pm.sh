#!/usr/bin/env bash
# p2_ml_pm.sh — roda o experimento Predictive Maintenance (scikit-learn) e
# streama a tabela de métricas ao vivo no console do painel.
#   Caso do artigo Ngo et al. 2024 (Tabela 7), recorte Instance, dados reais do
#   walk test 5G do SUTD. Sem tempo cego: só treina e imprime.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=/dev/null
. "$SCRIPT_DIR/lib/testlog.sh"

DATA_DIR="${SUTD_DIR:-$PROJECT_DIR/data/sutd}"
EXP="$SCRIPT_DIR/ml/pm_experiment.py"
PY="${PANEL_PY:-$HOME/server/panel/.venv/bin/python3}"
[ -x "$PY" ] || PY="$(command -v python3 || true)"

section "PM-rApp — Predictive Maintenance / RRU perdida (recorte Instance)"
info "Detecta pelo lado do UE se a célula está com 2 RRUs (normal) ou 1 (defeito)."
kv "Artigo" "Ngo et al. 2024, Tabela 7 (dados do walk test SUTD)"
kv "Abordagem" "Instance (1 amostra -> 1 previsão)"

section "1. Pré-condições"
if [ ! -d "$DATA_DIR" ]; then
    err "dataset SUTD ausente: $DATA_DIR"
    summary "tentou carregar os CSVs do walk test SUTD" \
            "dataset ausente — nada a treinar" err
    exit 1
fi
if [ -z "$PY" ]; then
    err 'python com scikit-learn não encontrado (venv: $HOME/server/panel/.venv)'
    summary "procurou o interpretador com scikit-learn" "python indisponível" err
    exit 1
fi
ok "dados em $DATA_DIR"
kv "Interpretador" "$PY"

section "2. Treino + métricas (scikit-learn, split temporal 70:30)"
step "treinando 5 classificadores instance-based e medindo Acc/Prec/Rec/F1…"
if "$PY" -u "$EXP" --data "$DATA_DIR"; then
    summary "treinou os 5 classificadores da Tabela 7 e imprimiu as métricas" \
            "MLP lidera (93,1%); Gradient Boosting (~XGBoost) reproduz o artigo (92,5% vs 92,6%)" ok
else
    rc=$?
    err "o experimento falhou (rc=$rc) — o venv tem scikit-learn instalado?"
    summary "rodou o experimento Predictive Maintenance" "falhou ao treinar" err
    exit "$rc"
fi
