#!/usr/bin/env python3
"""
Caso de uso do artigo de referência: PM-rApp / Predictive Maintenance
(recorte Instance)

Reprodução aberta do classificador de RRUs ativas do artigo:
  Ngo et al., "RAN Intelligent Controller (RIC): From open-source
  implementation to real-world validation", ICT Express 10(3), 2024.
  DOI 10.1016/j.icte.2024.02.001 — Tabela 7 (PM-rApp).

Contexto: uma RRU pode seguir mandando heartbeat pela M-plane e ainda assim
estar defeituosa (antena solta, transmissão caindo na última milha) — o EMS
a vê como saudável. O PM-rApp detecta pelo LADO DO UE: com as KPMs de rádio,
classifica quantas RRUs realmente atendem a célula. Se o modelo diz 1 e o
EMS diz 2, alerta a equipe de manutenção.

Dados: walk test do SUTD no andar 6 em duas configurações — 2 RRUs outdoor
ativas (classe 0) × 1 RRU ativa (classe 1):
  https://github.com/FCCLab/sutd_5g_dataset_2023  (branch: dataset)

O artigo avalia recortes instance e sequence. A designação da disciplina é
INSTANCE — onde o campeão da Tabela 7 é o XGBoost (Acc 92,6%, F1 0,925),
e não a DNN 99,1% (que é sequence, o número mais citado do caso).

Uso:
    python pm_experiment.py
Saídas:
    results/metrics_random.csv     protocolo do artigo (split 70:30 aleatório)
    results/metrics_temporal.csv   split temporal 70:30 por trilha
    figures/*.png                  série de throughput, matriz de confusão,
                                   importância de features
"""

from __future__ import annotations

import os
import pickle
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import (GradientBoostingClassifier,
                              RandomForestClassifier)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score,
                             precision_recall_fscore_support)
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC

HERE = os.path.dirname(os.path.abspath(__file__))
SUTD_DIR = os.path.join(HERE, "..", "data", "sutd")
FIG_DIR = os.path.join(HERE, "figures")
RES_DIR = os.path.join(HERE, "results")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)

SEED = 42

# As 7 KPMs que o artigo declara coletar (Seção 6.1.1). Os rótulos lab_*
# e Label ficam FORA das features: lab_1rr marca exatamente a trilha de
# 1 RRU — usá-lo como entrada seria prever o alvo com o próprio alvo.
FEATURES = ["RSRP", "RSRQ", "SINR", "PDSCH PRBs", "PDSCH_MCS",
            "PUSCH_MCS", "throughput_DL"]

# Cenários 3 e 4 da Tabela 1 do artigo (mesmo andar, mesma caminhada,
# muda só o número de RRUs outdoor ativas).
TRACES = {
    "Lvl6_AllRRUOn_Anomaly_label.csv": 0,  # 2 RRUs ativas (operação normal)
    "Lvl6_1RRUOn_Anomaly_label.csv": 1,    # 1 RRU ativa  (RRU "defeituosa")
}


def carregar():
    partes = []
    for arq, rotulo in TRACES.items():
        df = pd.read_csv(os.path.join(SUTD_DIR, arq))
        df = df[FEATURES].apply(pd.to_numeric, errors="coerce").dropna()
        df["rru_off"] = rotulo
        partes.append(df)
    return partes


def modelos():
    """Os 5 classificadores instance-based da Tabela 7 do artigo.

    XGBoost → GradientBoosting do scikit-learn (mesma família, boosting de
    árvores; alternativa viável prevista no enunciado). DNN(1x7,20,1) →
    MLPClassifier com 1 camada oculta de 20 neurônios, Adam."""
    return {
        "Linear (logística)": LogisticRegression(max_iter=5000),
        "SVM": SVC(random_state=SEED),
        "Random Forest": RandomForestClassifier(random_state=SEED),
        "Gradient Boosting (~XGBoost)":
            GradientBoostingClassifier(random_state=SEED),
        "MLP ~ DNN(1x7,20,1)": MLPClassifier(
            hidden_layer_sizes=(20,), solver="adam", max_iter=3000,
            random_state=SEED),
    }


def avaliar(X_tr, X_te, y_tr, y_te, protocolo):
    linhas = []
    melhor = (None, None, -1.0)
    for nome, clf in modelos().items():
        pipe = make_pipeline(MinMaxScaler(), clf)  # normalização [0,1] do artigo
        pipe.fit(X_tr, y_tr)
        t0 = time.perf_counter()
        pred = pipe.predict(X_te)
        us_amostra = (time.perf_counter() - t0) / len(X_te) * 1e6
        prec, rec, f1, _ = precision_recall_fscore_support(
            y_te, pred, average="binary", zero_division=0)
        acc = accuracy_score(y_te, pred)
        linhas.append({
            "Modelo": nome, "Acc (%)": round(acc * 100, 1),
            "Precisão": round(prec, 3), "Recall": round(rec, 3),
            "F1": round(f1, 3),
            "Tamanho (kB)": round(len(pickle.dumps(pipe)) / 1024, 1),
            "Inf. (µs/amostra)": round(us_amostra, 1),
        })
        if acc > melhor[2]:
            melhor = (nome, pipe, acc)
        print(f"  [{protocolo}] {nome:<30} Acc {acc*100:5.1f}%  F1 {f1:.3f}")
    tab = pd.DataFrame(linhas)
    tab.to_csv(os.path.join(RES_DIR, f"metrics_{protocolo}.csv"), index=False)
    return tab, melhor


def figuras(partes, melhor_nome, pipe, X_te, y_te):
    # Throughput ao longo da caminhada — o "sintoma" que o PM-rApp enxerga
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for parte, cor, nome in [(partes[0], "#55a868", "2 RRUs ativas"),
                             (partes[1], "#c44e52", "1 RRU ativa")]:
        thp = parte["throughput_DL"].to_numpy() / 1e6
        ax.plot(np.arange(len(thp)) * 0.5, thp, lw=0.6, alpha=0.8,
                color=cor, label=nome)
    ax.set_xlabel("Tempo de caminhada (s)")
    ax.set_ylabel("Throughput DL (Mbps)")
    ax.set_title("Andar 6 — mesma rota, com e sem a 2ª RRU")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "throughput_cenarios.png"), dpi=150)

    # Matriz de confusão do melhor modelo (split temporal)
    fig, ax = plt.subplots(figsize=(5.5, 5))
    ConfusionMatrixDisplay.from_estimator(
        pipe, X_te, y_te, display_labels=["2 RRUs", "1 RRU"],
        colorbar=False, ax=ax)
    ax.set_title(f"Matriz de confusão — {melhor_nome} (split temporal)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "matriz_confusao.png"), dpi=150)

    # Importância de features (Gradient Boosting)
    df_all = pd.concat(partes, ignore_index=True)
    gb = make_pipeline(MinMaxScaler(),
                       GradientBoostingClassifier(random_state=SEED))
    gb.fit(df_all[FEATURES], df_all["rru_off"])
    imp = gb[-1].feature_importances_
    ordem = np.argsort(imp)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh([FEATURES[i] for i in ordem], imp[ordem], color="#4c72b0")
    ax.set_title("Importância das KPMs (Gradient Boosting)")
    ax.set_xlabel("Importância (redução de impureza)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "importancia_features.png"), dpi=150)


def main():
    partes = carregar()
    df_all = pd.concat(partes, ignore_index=True)
    print(f"Amostras válidas: {len(df_all)} "
          f"(2 RRUs: {len(partes[0])}, 1 RRU: {len(partes[1])})")

    X, y = df_all[FEATURES], df_all["rru_off"]

    # Protocolo A — o do artigo: split 70:30 aleatório.
    print("\nProtocolo A — split aleatório 70:30 (como no artigo):")
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.3, random_state=SEED, stratify=y)
    avaliar(X_tr, X_te, y_tr, y_te, "random")

    # Protocolo B — split temporal 70:30 dentro de cada trilha.
    print("\nProtocolo B — split temporal 70:30 por trilha:")
    tr, te = [], []
    for parte in partes:
        corte = int(len(parte) * 0.7)
        tr.append(parte.iloc[:corte])
        te.append(parte.iloc[corte:])
    tr, te = pd.concat(tr), pd.concat(te)
    _, (nome, pipe, _) = avaliar(tr[FEATURES], te[FEATURES],
                                 tr["rru_off"], te["rru_off"], "temporal")

    figuras(partes, nome, pipe, te[FEATURES], te["rru_off"])
    print(f"\nSaídas em {RES_DIR} e {FIG_DIR}")


if __name__ == "__main__":
    main()
