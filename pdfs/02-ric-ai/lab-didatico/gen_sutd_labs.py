#!/usr/bin/env python3
"""
Gera os datasets_config.json das aulas Localization e Predictive Maintenance do
Lab de IA, a partir dos DADOS REAIS do walk test SUTD (Ngo et al. 2024).

Mesma estrutura do card de classificação (live_model logístico p/ inferência em
JS no browser; tabela compara 7 classificadores), mas:
  - features = as 7 KPMs do artigo (throughput em Mbps p/ leitura amigável);
  - métricas no SPLIT TEMPORAL 70:30 por trilha (o honesto p/ série a 2 Hz),
    consistente com os relatórios e os testes do servidor;
  - fonte = dados reais do SUTD (não a base sintética do professor).

Saída: localizacao/datasets_config.json e manutencao/datasets_config.json
"""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

SEED = 42
HERE = Path(__file__).resolve().parent
SUTD = HERE.parent / "casos-artigo" / "data" / "sutd"

# As 7 KPMs do artigo (throughput já convertido p/ Mbps). Chaves SEM espaço
# (viram id/atributo no card). Ordem = a das colunas no CSV do SUTD.
COLS_CSV = ["RSRP", "RSRQ", "SINR", "PDSCH_MCS", "PUSCH_MCS", "PDSCH PRBs", "throughput_DL"]
KPI = {
    "RSRP":          {"key": "RSRP",       "label": "RSRP (sinal)",     "unit": "dBm", "hard": [-125, -55], "dec": 0},
    "RSRQ":          {"key": "RSRQ",       "label": "RSRQ (qualidade)", "unit": "dB",  "hard": [-22, -3],   "dec": 0},
    "SINR":          {"key": "SINR",       "label": "SINR",             "unit": "dB",  "hard": [-10, 40],   "dec": 0},
    "PDSCH_MCS":     {"key": "PDSCH_MCS",  "label": "MCS (PDSCH)",      "unit": "",    "hard": [0, 28],     "dec": 0},
    "PUSCH_MCS":     {"key": "PUSCH_MCS",  "label": "MCS (PUSCH)",      "unit": "",    "hard": [0, 28],     "dec": 0},
    "PDSCH PRBs":    {"key": "PDSCH_PRBs", "label": "PRBs (PDSCH)",     "unit": "",    "hard": [0, 140],    "dec": 0},
    "throughput_DL": {"key": "throughput_DL", "label": "Throughput DL", "unit": "Mbps","hard": [0, 600],    "dec": 0},
}
FEATKEYS = [KPI[c]["key"] for c in COLS_CSV]  # chaves seguras, na ordem


def models():
    return {
        "Regressão Logística": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
        "Árvore de Decisão": DecisionTreeClassifier(max_depth=4, random_state=SEED),
        "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=8, random_state=SEED),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=150, max_depth=3, random_state=SEED),
        "k-NN": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5)),
        "Naive Bayes": GaussianNB(),
        "SVM (RBF)": make_pipeline(StandardScaler(), SVC(kernel="rbf", C=10, gamma="scale")),
    }


def carregar(traces):
    """Lê as trilhas do SUTD, seleciona as 7 KPMs (throughput em Mbps), limpa e
    devolve (df por trilha com chaves seguras + coluna 'y')."""
    partes = []
    for arq, classe in traces.items():
        raw = pd.read_csv(SUTD / arq)
        sub = raw[COLS_CSV].apply(pd.to_numeric, errors="coerce").dropna()
        sub = sub.rename(columns={c: KPI[c]["key"] for c in COLS_CSV})
        sub["throughput_DL"] = (sub["throughput_DL"] / 1e6).round(0)  # bps -> Mbps
        sub["y"] = classe
        partes.append(sub.reset_index(drop=True))
    return partes


def split_temporal(partes, frac=0.7):
    tr = pd.concat([p.iloc[:int(len(p) * frac)] for p in partes], ignore_index=True)
    te = pd.concat([p.iloc[int(len(p) * frac):] for p in partes], ignore_index=True)
    return tr, te


def build(spec):
    partes = carregar(spec["traces"])
    df = pd.concat(partes, ignore_index=True)
    X, y = df[FEATKEYS].to_numpy(float), df["y"].to_numpy(str)

    # métricas no split temporal 70:30 por trilha (o honesto p/ 2 Hz)
    tr, te = split_temporal(partes)
    Xtr, ytr = tr[FEATKEYS].to_numpy(float), tr["y"].to_numpy(str)
    Xte, yte = te[FEATKEYS].to_numpy(float), te["y"].to_numpy(str)
    table = []
    for name, m in models().items():
        m.fit(Xtr, ytr)
        yp = m.predict(Xte)
        table.append({"model": name,
                      "acc": round(float(accuracy_score(yte, yp)), 4),
                      "f1": round(float(f1_score(yte, yp, average="macro")), 4)})
    table.sort(key=lambda r: -r["f1"])

    # live_model logístico (inferência em JS): treina em TODOS os dados
    scaler = StandardScaler().fit(X)
    clf = LogisticRegression(max_iter=1000).fit(scaler.transform(X), y)
    classes_lm = list(clf.classes_)
    if clf.coef_.shape[0] == 1:  # binário -> softmax de 2 classes
        coef = np.vstack([np.zeros_like(clf.coef_[0]), clf.coef_[0]])
        inter = np.array([0.0, clf.intercept_[0]])
    else:
        coef, inter = clf.coef_, clf.intercept_

    feats = [{"key": KPI[c]["key"], "label": KPI[c]["label"], "unit": KPI[c]["unit"],
              "hard": KPI[c]["hard"],
              "train": [round(float(df[KPI[c]["key"]].min()), 1),
                        round(float(df[KPI[c]["key"]].max()), 1)],
              "decimals": KPI[c]["dec"]}
             for c in COLS_CSV]

    order = [c["name"] for c in spec["classes"]]
    classes = spec["classes"]
    # cenário representativo por classe = a mediana de cada feature naquela classe
    scen, start = {}, {}
    for c in classes:
        grp = df[df["y"] == c["name"]]
        vals = {KPI[k]["key"]: round(float(grp[KPI[k]["key"]].median()), KPI[k]["dec"])
                for k in COLS_CSV}
        scen[c["name"]] = {"label": f'{c["emoji"]} {c["display"]}',
                           "hint": c["hint"], "values": vals}
    start = dict(scen[spec["start"]]["values"])

    return {
        "label": spec["label"], "source": spec["source"], "usecase": spec["usecase"],
        "n_rows": int(len(df)), "target_name": spec["target_name"],
        "features": feats,
        "classes": [{"name": c["name"], "display": c["display"], "emoji": c["emoji"], "sev": c["sev"]}
                    for c in classes],
        "live_model": {"features": FEATKEYS,
                       "mean": [round(float(x), 5) for x in scaler.mean_],
                       "std": [round(float(x), 5) for x in scaler.scale_],
                       "classes": classes_lm,
                       "coef": [[round(float(c), 5) for c in row] for row in coef],
                       "intercept": [round(float(b), 5) for b in inter]},
        "scenarios": scen, "start": start, "metrics_table": table,
        "balance": {k: int(v) for k, v in Counter(y).items()},
    }


SPECS = {
    "localizacao": {
        "family": "Localização", "key": "andar",
        "label": "Localização — andar do UE", "target_name": "Andar",
        "source": "SUTD walk test (Ngo et al. 2024)",
        "usecase": "estimar o andar (4/5/6) do UE só com KPMs de rádio — Localization-rApp",
        "traces": {"Lvl4_AllRRUOn_Anomaly_label.csv": "andar4",
                   "Lvl5_AllRRUOn_Anomaly_label.csv": "andar5",
                   "Lvl6_AllRRUOn_Anomaly_label.csv": "andar6"},
        "classes": [
            {"name": "andar4", "display": "Andar 4", "emoji": "4️⃣", "sev": "good", "hint": "cobertura do 4º andar"},
            {"name": "andar5", "display": "Andar 5", "emoji": "5️⃣", "sev": "warn", "hint": "cobertura do 5º andar"},
            {"name": "andar6", "display": "Andar 6", "emoji": "6️⃣", "sev": "bad",  "hint": "cobertura do 6º andar"},
        ],
        "start": "andar5",
    },
    "manutencao": {
        "family": "Manutenção preditiva", "key": "rru",
        "label": "Manutenção preditiva — RRU perdida", "target_name": "RRUs ativas",
        "source": "SUTD walk test (Ngo et al. 2024)",
        "usecase": "detectar se a célula tem 2 RRUs ou 1 (defeito) pelo lado do UE — PM-rApp",
        "traces": {"Lvl6_AllRRUOn_Anomaly_label.csv": "rru2",
                   "Lvl6_1RRUOn_Anomaly_label.csv": "rru1"},
        "classes": [
            {"name": "rru2", "display": "2 RRUs (normal)", "emoji": "🟢", "sev": "good", "hint": "operação normal"},
            {"name": "rru1", "display": "1 RRU (defeito)", "emoji": "🔴", "sev": "bad",  "hint": "RRU perdida"},
        ],
        "start": "rru2",
    },
}


def main():
    for slug, spec in SPECS.items():
        cfg = {"family": spec["family"], "default": spec["key"],
               "datasets": {spec["key"]: build(spec)}}
        out = HERE / slug / "datasets_config.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(cfg, ensure_ascii=False, indent=2))
        r = cfg["datasets"][spec["key"]]
        best = r["metrics_table"][0]
        print(f"{slug:<12s} n={r['n_rows']:>4d} classes={r['balance']}  "
              f"melhor={best['model']} (F1={best['f1']}, acc={best['acc']})")
        print(f"             -> {out.relative_to(HERE)} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
