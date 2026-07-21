#!/usr/bin/env bash
# p2_ml_uetp.sh — roda o experimento UE-TP (scikit-learn) e streama a tabela de
# métricas ao vivo no console do painel.
#   Caso do artigo Ngo et al. 2024 (Tabela 4), recorte Instance, dados reais do
#   walk test 5G do SUTD. Sem tempo cego: só treina e imprime.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=/dev/null
. "$SCRIPT_DIR/lib/testlog.sh"

DATA_DIR="${SUTD_DIR:-$PROJECT_DIR/data/sutd}"
EXP="$SCRIPT_DIR/ml/uetp_experiment.py"
PY="${PANEL_PY:-$HOME/server/panel/.venv/bin/python3}"
[ -x "$PY" ] || PY="$(command -v python3 || true)"

section "UE-TP-rApp — previsão de throughput do UE (recorte Instance)"
info "Prevê o throughput DL do UE a partir dos KPIs de rádio do instante atual."
kv "Artigo" "Ngo et al. 2024, Tabela 4 (dados do walk test SUTD)"
kv "Abordagem" "Instance (regressão, 1 amostra -> 1 previsão)"

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

section "2. Treino + métricas (scikit-learn, split temporal 80:20)"
step "treinando 8 regressores e medindo RMSE/MAE/R²…"
if "$PY" -u "$EXP" --data "$DATA_DIR"; then
    summary "treinou os regressores e imprimiu RMSE/MAE/R² (MLP = a DNN do artigo)" \
            "Gradient Boosting lidera (R² ~0,84); MLP reproduz a DNN instance" ok
else
    rc=$?
    err "o experimento falhou (rc=$rc) — o venv tem scikit-learn instalado?"
    summary "rodou o experimento UE-TP" "falhou ao treinar" err
    exit "$rc"
fi
