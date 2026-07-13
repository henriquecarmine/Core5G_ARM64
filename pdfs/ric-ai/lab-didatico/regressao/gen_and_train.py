#!/usr/bin/env python3
"""
Lab didático de RIC-IA — card "Regressão" (UE-TP)

Gera um dataset 5G ENRIQUECIDO (KPIs realistas e correlacionados, com relação
levemente não linear via Shannon) e treina/exporta:
  - data/uetp_enriched.csv         dataset sintético (~600 amostras)
  - model_config.json              config p/ o card interativo:
       * features (rótulo, unidade, faixa física "hard", faixa de treino "train")
       * modelo linear (intercepto + coeficientes) p/ previsão ao vivo em JS
       * cenários coerentes p/ o botão "Sugerir" (pico/madrugada/borda/centro)
       * cenários multi-UE
       * tabela comparativa dos 7 modelos (RMSE/MAE/R²/inferência)

Determinístico (seed fixa). Uso: python gen_and_train.py
"""
from __future__ import annotations
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

SEED = 42
BASE = Path(__file__).resolve().parent
FEATURES = ["ActiveUsers", "RSRP", "SINR", "CQI", "MCS", "PRBUtilization"]
TARGET = "Throughput"

# Faixa física ("hard") de cada KPI — fora disso é IMPOSSÍVEL (erro vermelho).
HARD = {
    "ActiveUsers": (0, 200),
    "RSRP": (-140, -44),
    "SINR": (-10, 30),
    "CQI": (0, 15),
    "MCS": (0, 28),
    "PRBUtilization": (0, 100),
}
LABELS = {
    "ActiveUsers": ("Usuários ativos", ""),
    "RSRP": ("RSRP (potência do sinal)", "dBm"),
    "SINR": ("SINR (sinal/ruído)", "dB"),
    "CQI": ("CQI (qualidade do canal)", "0–15"),
    "MCS": ("MCS (modulação/codificação)", "0–28"),
    "PRBUtilization": ("PRB utilizado", "%"),
}
DECIMALS = {"ActiveUsers": 0, "RSRP": 0, "SINR": 1, "CQI": 0, "MCS": 0, "PRBUtilization": 0}


def physics(users: float, q: float, rng: np.random.Generator | None = None) -> dict:
    """Modelo gerador: de (carga de usuários, qualidade de posição q∈[0,1]) para
    todos os KPIs + throughput. q=1 = centro da célula (sinal ótimo), q=0 = borda.
    Throughput usa eficiência espectral de Shannn (log2) => levemente NÃO linear."""
    def n(sd):
        return 0.0 if rng is None else float(rng.normal(0, sd))

    rsrp = np.clip(-44 - (1 - q) * 92 + n(3), *HARD["RSRP"])
    sinr = np.clip(-8 + 34 * q - 3 * (users / 180) + n(1.5), *HARD["SINR"])
    cqi = int(np.clip(round((sinr + 10) / 40 * 15), *HARD["CQI"]))
    mcs = int(np.clip(round(cqi / 15 * 28), *HARD["MCS"]))
    prb = float(np.clip(12 + users * 0.48 + n(4), 1, 100))
    se = np.log2(1 + 10 ** (sinr / 10))          # eficiência espectral (Shannon)
    thr = se * (prb / 100) * 22
    thr = max(0.5, thr + (n(1) * 0.04 * thr))
    return {
        "ActiveUsers": float(users), "RSRP": round(rsrp, 1), "SINR": round(sinr, 1),
        "CQI": cqi, "MCS": mcs, "PRBUtilization": round(prb, 1),
        "Throughput": round(thr, 2),
    }


def make_dataset(n_rows=600) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    rows = []
    for _ in range(n_rows):
        users = int(rng.integers(5, 181))
        q = float(rng.uniform(0, 1))
        rows.append(physics(users, q, rng))
    df = pd.DataFrame(rows)[FEATURES + [TARGET]]
    (BASE / "data").mkdir(exist_ok=True)
    df.to_csv(BASE / "data" / "uetp_enriched.csv", index=False)
    return df


def build_models() -> dict:
    return {
        "Regressão Linear": LinearRegression(),
        "Ridge": Ridge(alpha=1.0, random_state=SEED),
        "Árvore de Decisão": DecisionTreeRegressor(max_depth=6, random_state=SEED),
        "Random Forest": RandomForestRegressor(n_estimators=200, max_depth=8, random_state=SEED),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=250, max_depth=3,
                                                       learning_rate=0.05, random_state=SEED),
        "k-NN (k=5)": make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=5)),
        "SVR (RBF)": make_pipeline(StandardScaler(), SVR(kernel="rbf", C=100, gamma="scale")),
    }


def evaluate(models, X, y) -> list[dict]:
    cv = KFold(n_splits=5, shuffle=True, random_state=SEED)
    out = []
    for name, model in models.items():
        y_pred = cross_val_predict(model, X, y, cv=cv)
        model.fit(X, y)
        n_rep = 500
        t0 = time.perf_counter()
        for _ in range(n_rep):
            model.predict(X[:32])
        infer_us = (time.perf_counter() - t0) / (n_rep * 32) * 1e6
        out.append({
            "model": name,
            "rmse": round(float(np.sqrt(mean_squared_error(y, y_pred))), 3),
            "mae": round(float(mean_absolute_error(y, y_pred)), 3),
            "r2": round(float(r2_score(y, y_pred)), 4),
            "infer_us": round(float(infer_us), 2),
        })
    return sorted(out, key=lambda r: r["rmse"])


def scenarios() -> dict:
    """Cenários coerentes (sem ruído) para o botão Sugerir."""
    defs = {
        "centro":    (25, 0.95),   # centro da célula, carga leve — sinal ótimo
        "madrugada": (8, 0.85),    # célula quase vazia — recursos sobrando
        "pico":      (170, 0.55),  # hora de pico — célula congestionada
        "borda":     (45, 0.08),   # borda da célula — sinal ruim
    }
    meta = {
        "centro": ("🎯 Centro da célula", "Sinal excelente, poucos usuários."),
        "madrugada": ("🌙 Madrugada", "Célula quase vazia, recurso sobrando."),
        "pico": ("🏙️ Hora de pico", "Célula lotada, PRB alto, SINR cai."),
        "borda": ("📶 Borda de célula", "Sinal fraco (RSRP/SINR baixos)."),
    }
    res = {}
    for k, (u, q) in defs.items():
        vals = physics(u, q, rng=None)
        vals.pop("Throughput")
        res[k] = {"label": meta[k][0], "hint": meta[k][1], "values": vals}
    return res


def multi_scenarios() -> dict:
    """Cenas multi-UE: lista de UEs (cada um com seus KPIs), sem throughput."""
    def ue(u, q, name):
        v = physics(u, q, rng=None); v.pop("Throughput")
        return {"name": name, "values": v}
    return {
        "congestionada": {
            "label": "🏙️ Célula congestionada (5 UEs, um na borda)",
            "ues": [
                ue(160, 0.9, "UE-1 centro"),
                ue(160, 0.6, "UE-2 meio"),
                ue(160, 0.5, "UE-3 meio"),
                ue(160, 0.3, "UE-4 afastado"),
                ue(160, 0.05, "UE-5 borda"),
            ],
        },
        "mista": {
            "label": "🌆 Mix de posições (3 UEs)",
            "ues": [ue(60, 0.9, "UE-1 centro"), ue(60, 0.45, "UE-2 meio"),
                    ue(60, 0.1, "UE-3 borda")],
        },
    }


def main():
    df = make_dataset()
    X = df[FEATURES].to_numpy(float)
    y = df[TARGET].to_numpy(float)

    table = evaluate(build_models(), X, y)

    # Preditor AO VIVO: modelo linear nos 3 KPIs independentes e intuitivos
    # (os do professor) — coeficientes com sinais que fazem sentido ao mexer.
    CORE = ["ActiveUsers", "SINR", "PRBUtilization"]
    lin = LinearRegression().fit(df[CORE].to_numpy(float), y)

    config = {
        "target": {"key": TARGET, "unit": "Mbps"},
        "features": [
            {
                "key": k, "label": LABELS[k][0], "unit": LABELS[k][1],
                "hard": list(HARD[k]),
                "train": [round(float(df[k].min()), 1), round(float(df[k].max()), 1)],
                "decimals": DECIMALS[k],
                "primary": k in CORE,
            }
            for k in FEATURES
        ],
        "live_model": {
            "features": CORE,
            "intercept": round(float(lin.intercept_), 5),
            "coef": {k: round(float(c), 5) for k, c in zip(CORE, lin.coef_)},
        },
        "scenarios": scenarios(),
        "multi": multi_scenarios(),
        "metrics_table": table,
        "n_rows": int(len(df)),
    }
    (BASE / "model_config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2))

    print(f"Dataset: {len(df)} linhas -> data/uetp_enriched.csv")
    print("\nTabela comparativa (5-fold CV, ordenada por RMSE):")
    print(f"  {'Modelo':<20s} {'RMSE':>7s} {'MAE':>7s} {'R2':>8s} {'inf(us)':>8s}")
    for r in table:
        print(f"  {r['model']:<20s} {r['rmse']:>7.3f} {r['mae']:>7.3f} {r['r2']:>8.4f} {r['infer_us']:>8.2f}")
    print(f"\nPreditor ao vivo (linear, 3 KPIs core): Throughput = {config['live_model']['intercept']}")
    for k, c in config['live_model']['coef'].items():
        print(f"        {c:+.4f} * {k}")
    print("\nmodel_config.json escrito.")


if __name__ == "__main__":
    main()
