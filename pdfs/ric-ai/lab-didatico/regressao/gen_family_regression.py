#!/usr/bin/env python3
"""
Card "Regressão" (família) — config multi-dataset.

Começa SEMPRE com os datasets do Prof. Tesolin (valores originais das Base Fonts
RIC). O dataset sintético enriquecido entra como opção "Realista".
Saída: datasets_config.json  (consumido pelo card).
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import LeaveOneOut, KFold, cross_val_predict
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Na base didática (N=16) o MLP atinge max_iter sem convergir — esperado (e a
# lição: rede neural tem fome de dados). Silencia só o aviso repetido.
import warnings
from sklearn.exceptions import ConvergenceWarning
warnings.filterwarnings("ignore", category=ConvergenceWarning)

SEED = 42
BASE = Path(__file__).resolve().parent / "data"
OUT = Path(__file__).resolve().parent / "datasets_config.json"

# Faixa física (hard) e rótulo por KPI — comum a todos os datasets.
KPI = {
    "ActiveUsers":   {"label": "Usuários ativos",  "unit": "",    "hard": [0, 300], "dec": 0},
    "AvgSINR":       {"label": "SINR médio",        "unit": "dB",  "hard": [-10, 40], "dec": 0},
    "SINR":          {"label": "SINR",              "unit": "dB",  "hard": [-10, 40], "dec": 1},
    "PRBUtilization":{"label": "PRB utilizado",     "unit": "%",   "hard": [0, 100], "dec": 0},
    "TxPower":       {"label": "Potência Tx",       "unit": "dBm", "hard": [0, 46],  "dec": 0},
}
TARGET_UNIT = {"Throughput": "Mbps", "TrafficLoad": "", "EnergyConsumption": "kWh"}

DATASETS = [
    {"key": "traffic_prediction", "label": "UE-TP · Throughput", "file": "traffic_prediction.csv",
     "feat": ["ActiveUsers", "AvgSINR", "PRBUtilization"], "target": "Throughput",
     "source": "Prof. Tesolin", "usecase": "previsão de throughput por UE (UE-TP-rApp)"},
    {"key": "traffic_load", "label": "Traffic steering · Carga", "file": "traffic_load_prediction.csv",
     "feat": ["ActiveUsers", "AvgSINR", "PRBUtilization", "TxPower"], "target": "TrafficLoad",
     "source": "Prof. Tesolin", "usecase": "previsão de carga p/ traffic steering"},
    {"key": "energy", "label": "Energia · Consumo", "file": "energy_prediction.csv",
     "feat": ["ActiveUsers", "AvgSINR", "PRBUtilization"], "target": "EnergyConsumption",
     "source": "Prof. Tesolin", "usecase": "otimização de energia"},
    {"key": "enriquecido", "label": "Realista (sintético)", "file": "uetp_enriched.csv",
     "feat": ["ActiveUsers", "SINR", "PRBUtilization"], "target": "Throughput",
     "source": "sintético (não linear)", "usecase": "versão realista p/ aprofundar"},
]


def models():
    return {
        "Regressão Linear": LinearRegression(),
        "Ridge": Ridge(alpha=1.0, random_state=SEED),
        "Árvore de Decisão": DecisionTreeRegressor(max_depth=3, random_state=SEED),
        "Random Forest": RandomForestRegressor(n_estimators=200, max_depth=4, random_state=SEED),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=200, max_depth=2, learning_rate=0.05, random_state=SEED),
        "k-NN": make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=3)),
        "SVR (RBF)": make_pipeline(StandardScaler(), SVR(kernel="rbf", C=100, gamma="scale")),
        "MLP (10 neurônios)": make_pipeline(
            StandardScaler(),
            MLPRegressor(hidden_layer_sizes=(10,), max_iter=3000, random_state=SEED)),
    }


def build(dcfg):
    df = pd.read_csv(BASE / dcfg["file"])
    feat, tgt = dcfg["feat"], dcfg["target"]
    X, y = df[feat].to_numpy(float), df[tgt].to_numpy(float)
    cv = LeaveOneOut() if len(df) <= 50 else KFold(5, shuffle=True, random_state=SEED)

    table = []
    for name, m in models().items():
        yp = cross_val_predict(m, X, y, cv=cv)
        table.append({"model": name,
                      "rmse": round(float(np.sqrt(mean_squared_error(y, yp))), 3),
                      "mae": round(float(mean_absolute_error(y, yp)), 3),
                      "r2": round(float(r2_score(y, yp)), 4)})
    table.sort(key=lambda r: r["rmse"])
    lin = LinearRegression().fit(X, y)

    feats = [{"key": k, "label": KPI[k]["label"], "unit": KPI[k]["unit"], "hard": KPI[k]["hard"],
              "train": [round(float(df[k].min()), 1), round(float(df[k].max()), 1)], "decimals": KPI[k]["dec"]}
             for k in feat]

    # cenários = linhas reais (baixa/média/alta carga pelo alvo). Rótulo pela Hora quando existir.
    idx = np.argsort(y)
    picks = {"baixa": idx[0], "media": idx[len(idx) // 2], "pico": idx[-1]}
    hint = {"baixa": "carga baixa", "media": "carga média", "pico": "pico"}
    emoji = {"baixa": "🌙", "media": "🌆", "pico": "🏙️"}
    scen = {}
    for name, i in picks.items():
        vals = {k: round(float(df.iloc[i][k]), KPI[k]["dec"]) for k in feat}
        hr = f" (hora {int(df.iloc[i]['Hour'])})" if "Hour" in df.columns else ""
        scen[name] = {"label": f"{emoji[name]} {hint[name].capitalize()}{hr}", "hint": hint[name], "values": vals}

    start = {k: round(float(df.iloc[picks["media"]][k]), KPI[k]["dec"]) for k in feat}

    return {
        "label": dcfg["label"], "source": dcfg["source"], "usecase": dcfg["usecase"],
        "n_rows": int(len(df)),
        "features": feats,
        "target": {"key": tgt, "unit": TARGET_UNIT.get(tgt, ""),
                   "min": round(float(y.min()), 2), "max": round(float(y.max()), 2)},
        "live_model": {"features": feat, "intercept": round(float(lin.intercept_), 5),
                       "coef": {k: round(float(c), 5) for k, c in zip(feat, lin.coef_)}},
        "scenarios": scen, "start": start, "metrics_table": table,
    }


def main():
    out = {"family": "Regressão", "default": "traffic_prediction", "datasets": {}}
    for d in DATASETS:
        if not (BASE / d["file"]).exists():
            print(f"  (pula {d['key']}: {d['file']} ausente)"); continue
        out["datasets"][d["key"]] = build(d)
        t = out["datasets"][d["key"]]["metrics_table"][0]
        lm = out["datasets"][d["key"]]["live_model"]
        print(f"{d['key']:<20s} n={out['datasets'][d['key']]['n_rows']:>3d}  melhor={t['model']:<18s} "
              f"RMSE={t['rmse']:<7} | linear R2 via tabela")
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"\n{OUT.name} escrito ({len(out['datasets'])} datasets).")


if __name__ == "__main__":
    main()
