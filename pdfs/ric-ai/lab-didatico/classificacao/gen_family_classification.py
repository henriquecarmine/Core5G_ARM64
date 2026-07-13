#!/usr/bin/env python3
"""
Card "Classificação" (família) — config multi-dataset com os RÓTULOS ORIGINAIS
do professor (Base Fonts RIC). Não engenheira rótulo: usa os que ele deu.
  - cell_congestion_tree  -> Congestion (Low/Medium/High)  [multi-classe]
  - cell_failure_logistic -> Failure (No/Yes)              [binário]
Saída: datasets_config.json
"""
from __future__ import annotations
import json
from pathlib import Path
from collections import Counter
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import accuracy_score, f1_score

SEED = 42
BASE = Path(__file__).resolve().parent / "data"
OUT = Path(__file__).resolve().parent / "datasets_config.json"

KPI = {
    "ActiveUsers":     {"label": "Usuários ativos",        "unit": "",    "hard": [0, 300], "dec": 0},
    "PRBUtilization":  {"label": "PRB utilizado",          "unit": "%",   "hard": [0, 100], "dec": 0},
    "AvgSINR":         {"label": "SINR médio",             "unit": "dB",  "hard": [-10, 40], "dec": 0},
    "TxPower":         {"label": "Potência Tx",            "unit": "dBm", "hard": [0, 46],  "dec": 0},
    "PacketLoss":      {"label": "Perda de pacotes",       "unit": "%",   "hard": [0, 100], "dec": 1},
    "SchedulingDelay": {"label": "Atraso de agendamento",  "unit": "ms",  "hard": [0, 100], "dec": 0},
    "CellTemperature": {"label": "Temperatura da célula",  "unit": "°C",  "hard": [-20, 90], "dec": 0},
}
# rótulo original -> (nome exibido, emoji, severidade)
CLASSMETA = {"Low": ("Baixa", "🟢", "good"), "Medium": ("Média", "🟡", "warn"), "High": ("Alta", "🔴", "bad"),
             "No": ("Normal", "🟢", "good"), "Yes": ("Falha", "🔴", "bad")}

DATASETS = [
    {"key": "congestion", "label": "Congestionamento", "file": "cell_congestion_tree.csv",
     "target": "Congestion", "order": ["Low", "Medium", "High"], "start_class": "Medium",
     "source": "Prof. Tesolin", "usecase": "nível de congestionamento da célula (árvore de decisão)"},
    {"key": "failure", "label": "Falha de célula", "file": "cell_failure_logistic.csv",
     "target": "Failure", "order": ["No", "Yes"], "start_class": "No",
     "source": "Prof. Tesolin", "usecase": "prever falha da célula — manutenção preditiva (regressão logística)"},
]


def models():
    return {
        "Regressão Logística": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
        "Árvore de Decisão": DecisionTreeClassifier(max_depth=4, random_state=SEED),
        "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=5, random_state=SEED),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=150, max_depth=2, random_state=SEED),
        "k-NN": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=3)),
        "Naive Bayes": GaussianNB(),
        "SVM (RBF)": make_pipeline(StandardScaler(), SVC(kernel="rbf", C=10, gamma="scale")),
    }


def build(dcfg):
    df = pd.read_csv(BASE / dcfg["file"])
    tgt = dcfg["target"]
    feat = [c for c in df.columns if c != tgt]
    X, y = df[feat].to_numpy(float), df[tgt].to_numpy(str)
    minc = min(Counter(y).values())
    cv = StratifiedKFold(n_splits=min(5, minc), shuffle=True, random_state=SEED)

    table = []
    for name, m in models().items():
        yp = cross_val_predict(m, X, y, cv=cv)
        table.append({"model": name,
                      "acc": round(float(accuracy_score(y, yp)), 4),
                      "f1": round(float(f1_score(y, yp, average="macro")), 4)})
    table.sort(key=lambda r: -r["f1"])

    scaler = StandardScaler().fit(X)
    clf = LogisticRegression(max_iter=1000).fit(scaler.transform(X), y)
    # Binário: sklearn dá coef_ (1, nf) referente à classe positiva. Expande p/
    # formato softmax de 2 classes: classe0 = zeros, classe1 = w (softmax = sigmoid).
    lm_classes = list(clf.classes_)
    if clf.coef_.shape[0] == 1:
        lm_coef = np.vstack([np.zeros_like(clf.coef_[0]), clf.coef_[0]])
        lm_inter = np.array([0.0, clf.intercept_[0]])
    else:
        lm_coef, lm_inter = clf.coef_, clf.intercept_

    feats = [{"key": k, "label": KPI[k]["label"], "unit": KPI[k]["unit"], "hard": KPI[k]["hard"],
              "train": [round(float(df[k].min()), 1), round(float(df[k].max()), 1)], "decimals": KPI[k]["dec"]}
             for k in feat]
    classes = [{"name": c, "display": CLASSMETA[c][0], "emoji": CLASSMETA[c][1], "sev": CLASSMETA[c][2]}
               for c in dcfg["order"]]

    scen = {}
    for c in dcfg["order"]:
        row = df[df[tgt] == c].iloc[0]
        m = CLASSMETA[c]
        scen[c] = {"label": f"{m[1]} {m[0]}", "hint": f"classe {m[0].lower()}",
                   "values": {k: round(float(row[k]), KPI[k]["dec"]) for k in feat}}
    srow = df[df[tgt] == dcfg["start_class"]].iloc[0]
    start = {k: round(float(srow[k]), KPI[k]["dec"]) for k in feat}

    return {
        "label": dcfg["label"], "source": dcfg["source"], "usecase": dcfg["usecase"],
        "n_rows": int(len(df)), "target_name": tgt,
        "features": feats, "classes": classes,
        "live_model": {"features": feat,
                       "mean": [round(float(x), 5) for x in scaler.mean_],
                       "std": [round(float(x), 5) for x in scaler.scale_],
                       "classes": lm_classes,
                       "coef": [[round(float(c), 5) for c in row] for row in lm_coef],
                       "intercept": [round(float(b), 5) for b in lm_inter]},
        "scenarios": scen, "start": start, "metrics_table": table,
        "balance": dict(Counter(y)),
    }


def main():
    out = {"family": "Classificação", "default": "congestion", "datasets": {}}
    for d in DATASETS:
        out["datasets"][d["key"]] = build(d)
        r = out["datasets"][d["key"]]
        print(f"{d['key']:<12s} n={r['n_rows']:>3d} classes={r['balance']}  melhor={r['metrics_table'][0]['model']} "
              f"(F1={r['metrics_table'][0]['f1']})")
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"\n{OUT.name} escrito ({len(out['datasets'])} datasets). {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
