#!/usr/bin/env python3
"""
Lab didático de RIC-IA — card "Classificação" (estado da célula)

Gera dataset de KPIs de célula e treina/exporta classificadores para prever a
CATEGORIA da célula: Livre / Normal / Congestionada.
  data/cell_state.csv       dataset sintético (~700 amostras)
  model_config.json         config p/ o card interativo:
      * features (rótulo, unidade, faixa física + faixa de treino)
      * classes (nome, emoji, cor semântica)
      * live_model: Regressão Logística padronizada (scaler + coefs por classe)
        p/ previsão de classe + probabilidades ao vivo em JS
      * cenários coerentes p/ "Sugerir" + cenas multi-célula
      * tabela comparativa (Acurácia / F1-macro / inferência)
Determinístico. Uso: python gen_and_train_clf.py
"""
from __future__ import annotations
import json, time
from pathlib import Path
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
BASE = Path(__file__).resolve().parent
FEATURES = ["ActiveUsers", "PRBUtilization", "Latency", "PacketLoss"]
CLASSES = ["Livre", "Normal", "Congestionada"]
HARD = {"ActiveUsers": (0, 200), "PRBUtilization": (0, 100), "Latency": (1, 200), "PacketLoss": (0, 100)}
LABELS = {"ActiveUsers": ("Usuários ativos", ""), "PRBUtilization": ("PRB utilizado", "%"),
          "Latency": ("Latência", "ms"), "PacketLoss": ("Perda de pacotes", "%")}
DECIMALS = {"ActiveUsers": 0, "PRBUtilization": 0, "Latency": 0, "PacketLoss": 1}
CLASSMETA = {"Livre": ("🟢", "good"), "Normal": ("🟡", "warn"), "Congestionada": ("🔴", "bad")}


def label_of(prb, latency, loss):
    score = 0.55 * (prb / 100) + 0.30 * min(1, latency / 60) + 0.15 * min(1, loss / 12)
    return "Livre" if score < 0.35 else "Normal" if score < 0.62 else "Congestionada"


def sample(users, rng=None):
    def n(sd): return 0.0 if rng is None else float(rng.normal(0, sd))
    prb = float(np.clip(8 + users * 0.5 + n(6), 1, 100))
    latency = float(np.clip(6 + 45 * (prb / 100) ** 3 + n(3), 1, 200))
    loss = float(np.clip((prb - 72) / 2.5 + n(1.2), 0, 100))
    row = {"ActiveUsers": float(users), "PRBUtilization": round(prb, 1),
           "Latency": round(latency, 1), "PacketLoss": round(loss, 1)}
    row["State"] = label_of(prb, latency, loss)
    return row


def make_dataset(n_rows=700):
    rng = np.random.default_rng(SEED)
    rows = [sample(int(rng.integers(5, 201)), rng) for _ in range(n_rows)]
    df = pd.DataFrame(rows)[FEATURES + ["State"]]
    (BASE / "data").mkdir(exist_ok=True)
    df.to_csv(BASE / "data" / "cell_state.csv", index=False)
    return df


def build_models():
    return {
        "Regressão Logística": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
        "Árvore de Decisão": DecisionTreeClassifier(max_depth=5, random_state=SEED),
        "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=8, random_state=SEED),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=200, max_depth=3, random_state=SEED),
        "k-NN (k=7)": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=7)),
        "Naive Bayes": GaussianNB(),
        "SVM (RBF)": make_pipeline(StandardScaler(), SVC(kernel="rbf", C=10, gamma="scale")),
    }


def evaluate(models, X, y):
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    out = []
    for name, model in models.items():
        y_pred = cross_val_predict(model, X, y, cv=cv)
        model.fit(X, y)
        t0 = time.perf_counter()
        for _ in range(500):
            model.predict(X[:32])
        infer_us = (time.perf_counter() - t0) / (500 * 32) * 1e6
        out.append({"model": name,
                    "acc": round(float(accuracy_score(y, y_pred)), 4),
                    "f1": round(float(f1_score(y, y_pred, average="macro")), 4),
                    "infer_us": round(float(infer_us), 2)})
    return sorted(out, key=lambda r: -r["f1"])


def scenarios():
    defs = {"livre": 20, "normal": 100, "pico": 185}
    meta = {"livre": ("🟢 Célula livre", "pouca carga"),
            "normal": ("🟡 Uso normal", "carga média"),
            "pico": ("🔴 Congestionada", "PRB no talo")}
    res = {}
    for k, u in defs.items():
        v = sample(u, rng=None); v.pop("State")
        res[k] = {"label": meta[k][0], "hint": meta[k][1], "values": v}
    return res


def multi_scenarios():
    def cell(u, name):
        v = sample(u, rng=None); v.pop("State")
        return {"name": name, "values": v}
    return {
        "pico": {"label": "rede em pico", "cells": [
            cell(30, "Célula A"), cell(80, "Célula B"), cell(150, "Célula C"),
            cell(190, "Célula D"), cell(110, "Célula E")]},
        "mista": {"label": "rede mista", "cells": [
            cell(25, "Célula A"), cell(120, "Célula B"), cell(175, "Célula C")]},
    }


def main():
    df = make_dataset()
    X = df[FEATURES].to_numpy(float)
    y = df["State"].to_numpy()

    table = evaluate(build_models(), X, y)

    # Preditor ao vivo: Regressão Logística padronizada (interpretável + roda em JS)
    scaler = StandardScaler().fit(X)
    clf = LogisticRegression(max_iter=1000).fit(scaler.transform(X), y)
    order = list(clf.classes_)

    config = {
        "task": "classification",
        "classes": [{"name": c, "emoji": CLASSMETA[c][0], "sev": CLASSMETA[c][1]} for c in CLASSES],
        "features": [{"key": k, "label": LABELS[k][0], "unit": LABELS[k][1],
                      "hard": list(HARD[k]),
                      "train": [round(float(df[k].min()), 1), round(float(df[k].max()), 1)],
                      "decimals": DECIMALS[k], "primary": True} for k in FEATURES],
        "live_model": {
            "features": FEATURES,
            "mean": [round(float(m), 5) for m in scaler.mean_],
            "std": [round(float(s), 5) for s in scaler.scale_],
            "classes": order,
            "coef": [[round(float(c), 5) for c in row] for row in clf.coef_],
            "intercept": [round(float(b), 5) for b in clf.intercept_],
        },
        "scenarios": scenarios(),
        "multi": multi_scenarios(),
        "metrics_table": table,
        "n_rows": int(len(df)),
        "class_balance": {c: int((y == c).sum()) for c in CLASSES},
    }
    (BASE / "model_config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2))

    print(f"Dataset: {len(df)} linhas -> data/cell_state.csv")
    print("Balanço de classes:", config["class_balance"])
    print("\nTabela comparativa (5-fold CV, ordenada por F1-macro):")
    print(f"  {'Modelo':<22s} {'Acurácia':>9s} {'F1-macro':>9s} {'inf(us)':>8s}")
    for r in table:
        print(f"  {r['model']:<22s} {r['acc']:>9.4f} {r['f1']:>9.4f} {r['infer_us']:>8.2f}")
    print("\nmodel_config.json escrito.")


if __name__ == "__main__":
    main()
