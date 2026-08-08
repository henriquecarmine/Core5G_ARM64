#!/usr/bin/env python3
"""
Caso de uso do artigo de referência: Localization-rApp (recorte Instance)

Reprodução aberta do classificador de andar do artigo:
  Ngo et al., "RAN Intelligent Controller (RIC): From open-source
  implementation to real-world validation", ICT Express 10(3), 2024.
  DOI 10.1016/j.icte.2024.02.001 — Tabela 3 (Localization-rApp).

Tarefa: classificar em qual andar (4, 5 ou 6 → rótulos 0, 1, 2) o UE está,
a partir das KPMs de rádio do walk test do SUTD (2 Hz, Samsung S22 Ultra):
  https://github.com/FCCLab/sutd_5g_dataset_2023  (branch: dataset)

O artigo avalia dois recortes: instance (1 amostra → 1 previsão) e
sequence (janela de 10 amostras). A designação da disciplina é INSTANCE —
onde o campeão da Tabela 3 é o XGBoost (Acc 84,4%, F1 0,843), e não o
LSTM 91,1% (que é sequence e costuma ser citado como "o resultado" do caso).

Uso:
    python localization_experiment.py
Saídas:
    results/metrics_random.csv     protocolo do artigo (split 70:30 aleatório)
    results/metrics_temporal.csv   split temporal 70:30 por trilha (sem
                                   vizinhos de 0,5 s vazando p/ o teste)
    figures/*.png                  dispersão por andar, matriz de confusão,
                                   importância de features
"""

from __future__ import annotations

import io
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

# As 7 KPMs que o artigo declara coletar (Seção 6.1.1). Identificadores
# (PCI, C-RNTI, _oid), Corridor_tag e os rótulos lab_*/Label ficam FORA:
# usá-los como feature seria vazamento (Corridor_tag é quase o alvo).
FEATURES = ["RSRP", "RSRQ", "SINR", "PDSCH PRBs", "PDSCH_MCS",
            "PUSCH_MCS", "throughput_DL"]

# Andar → rótulo, como no artigo ([4, 5, 6] → [0, 1, 2]). Só as trilhas
# com os 2 RRUs outdoor ativos (cenários 1–3 da Tabela 1); a trilha
# Lvl6_1RRUOn é outra configuração de rádio e pertence ao caso PM.
TRACES = {
    "Lvl4_AllRRUOn_Anomaly_label.csv": 0,
    "Lvl5_AllRRUOn_Anomaly_label.csv": 1,
    "Lvl6_AllRRUOn_Anomaly_label.csv": 2,
}


def carregar():
    partes = []
    for arq, rotulo in TRACES.items():
        df = pd.read_csv(os.path.join(SUTD_DIR, arq))
        df = df[FEATURES].apply(pd.to_numeric, errors="coerce").dropna()
        df["floor"] = rotulo
        partes.append(df)
    return partes


def modelos():
    """Os 5 classificadores instance-based da Tabela 3 do artigo.

    XGBoost → GradientBoosting do scikit-learn (mesma família, boosting de
    árvores; alternativa viável prevista no enunciado). DNN(1x7,30,3) →
    MLPClassifier com 1 camada oculta de 30 neurônios, Adam."""
    return {
        "Linear (logística)": LogisticRegression(max_iter=5000),
        "SVM": SVC(random_state=SEED),
        "Random Forest": RandomForestClassifier(random_state=SEED),
        "Gradient Boosting (~XGBoost)":
            GradientBoostingClassifier(random_state=SEED),
        "MLP ~ DNN(1x7,30,3)": MLPClassifier(
            hidden_layer_sizes=(30,), solver="adam", max_iter=3000,
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
            y_te, pred, average="macro", zero_division=0)
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


def figuras(df_all, melhor_nome, pipe, X_te, y_te):
    # Dispersão RSRP × SINR por andar — mostra por que o problema é separável
    fig, ax = plt.subplots(figsize=(7, 5))
    cores = ["#4c72b0", "#dd8452", "#55a868"]
    for rotulo, nome in [(0, "Andar 4"), (1, "Andar 5"), (2, "Andar 6")]:
        sub = df_all[df_all["floor"] == rotulo]
        ax.scatter(sub["RSRP"], sub["SINR"], s=4, alpha=0.35,
                   color=cores[rotulo], label=nome)
    ax.set_xlabel("RSRP (dBm)")
    ax.set_ylabel("SINR (dB)")
    ax.set_title("Walk test SUTD — assinatura de rádio por andar")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "dispersao_andar.png"), dpi=150)

    # Matriz de confusão do melhor modelo (split temporal)
    fig, ax = plt.subplots(figsize=(5.5, 5))
    ConfusionMatrixDisplay.from_estimator(
        pipe, X_te, y_te, display_labels=["Andar 4", "Andar 5", "Andar 6"],
        colorbar=False, ax=ax)
    ax.set_title(f"Matriz de confusão — {melhor_nome} (split temporal)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "matriz_confusao.png"), dpi=150)

    # Importância de features (Gradient Boosting, split temporal)
    gb = make_pipeline(MinMaxScaler(),
                       GradientBoostingClassifier(random_state=SEED))
    gb.fit(df_all[FEATURES], df_all["floor"])
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
          f"(por andar: {df_all['floor'].value_counts().sort_index().tolist()})")

    X, y = df_all[FEATURES], df_all["floor"]

    # Protocolo A — o do artigo: split 70:30 aleatório sobre o conjunto todo.
    # A 2 Hz, amostras vizinhas (0,5 s) caem uma no treino e outra no teste.
    print("\nProtocolo A — split aleatório 70:30 (como no artigo):")
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.3, random_state=SEED, stratify=y)
    avaliar(X_tr, X_te, y_tr, y_te, "random")

    # Protocolo B — split temporal 70:30 dentro de cada trilha: treina no
    # começo da caminhada, testa no fim. Mede generalização de verdade.
    print("\nProtocolo B — split temporal 70:30 por trilha:")
    tr, te = [], []
    for parte in partes:
        corte = int(len(parte) * 0.7)
        tr.append(parte.iloc[:corte])
        te.append(parte.iloc[corte:])
    tr, te = pd.concat(tr), pd.concat(te)
    _, (nome, pipe, _) = avaliar(tr[FEATURES], te[FEATURES],
                                 tr["floor"], te["floor"], "temporal")

    figuras(df_all, nome, pipe, te[FEATURES], te["floor"])
    print(f"\nSaídas em {RES_DIR} e {FIG_DIR}")


if __name__ == "__main__":
    main()
