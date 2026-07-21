#!/usr/bin/env python3
"""PM-rApp / Predictive Maintenance (recorte Instance) — versão numpy-only.

Reproduz a Tabela 7 de Ngo et al., "RAN Intelligent Controller (RIC): From
open-source implementation to real-world validation", ICT Express 10(3), 2024
(DOI 10.1016/j.icte.2024.02.001): detecta pelo lado do UE quantas RRUs atendem
a célula — 2 RRUs ativas (classe 0, normal) x 1 RRU ativa (classe 1, defeito) —
a partir das KPMs de rádio do walk test do SUTD (andar 6).

Sem pandas/matplotlib (o venv do servidor só tem numpy + scikit-learn). Streama
a tabela de métricas; split temporal 70:30 por trilha.

Uso: python3 -u pm_experiment.py [--data DIR]
"""
from __future__ import annotations

import argparse
import os
import pickle
import sys
import time

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA = os.path.normpath(os.path.join(HERE, "..", "..", "data", "sutd"))
SEED = 42

# 7 KPMs do artigo (0-based no CSV). Os rótulos lab_*/Label ficam FORA: lab_1rr
# marca exatamente a trilha de 1 RRU — é o ALVO, nunca entrada.
COLS = [4, 5, 6, 9, 7, 8, 11]  # RSRP RSRQ SINR "PDSCH PRBs" PDSCH_MCS PUSCH_MCS throughput_DL
# Cenários 3 e 4 da Tabela 1: mesmo andar/rota, muda só o nº de RRUs ativas.
TRACES = {
    "Lvl6_AllRRUOn_Anomaly_label.csv": 0,  # 2 RRUs (operação normal)
    "Lvl6_1RRUOn_Anomaly_label.csv": 1,    # 1 RRU  (RRU "defeituosa")
}


def modelos():
    """Os 5 classificadores instance-based da Tabela 7. XGBoost -> Gradient
    Boosting do scikit-learn; DNN(1x7,20,1) -> MLP 1x20."""
    return {
        "Linear (logistica)": LogisticRegression(max_iter=5000),
        "SVM": SVC(random_state=SEED),
        "Random Forest": RandomForestClassifier(random_state=SEED),
        "Gradient Boosting (~XGBoost)": GradientBoostingClassifier(random_state=SEED),
        "MLP ~ DNN(1x7,20,1)": MLPClassifier(
            hidden_layer_sizes=(20,), solver="adam", max_iter=3000,
            random_state=SEED),
    }


def carregar(data_dir):
    partes = []
    for arq, rotulo in TRACES.items():
        caminho = os.path.join(data_dir, arq)
        a = np.genfromtxt(caminho, delimiter=",", skip_header=1, usecols=COLS)
        a = a[~np.isnan(a).any(axis=1)]
        y = np.full((a.shape[0], 1), rotulo, dtype=float)
        partes.append(np.hstack([a, y]))
    return partes


def split_temporal(partes, frac=0.7):
    tr, te = [], []
    for parte in partes:
        corte = int(len(parte) * frac)
        tr.append(parte[:corte])
        te.append(parte[corte:])
    return np.vstack(tr), np.vstack(te)


def avaliar(tr, te):
    X_tr, y_tr = tr[:, :-1], tr[:, -1]
    X_te, y_te = te[:, :-1], te[:, -1]
    print(f"  amostras: treino={len(tr)}  teste={len(te)}  (split temporal 70:30)")
    print()
    print(f"  {'Modelo':<30} {'Acc %':>6} {'Prec':>6} {'Rec':>6} {'F1':>6} "
          f"{'kB':>7} {'us/am':>7}", flush=True)
    print("  " + "-" * 72, flush=True)
    melhor = ("", -1.0)
    for nome, clf in modelos().items():
        pipe = make_pipeline(MinMaxScaler(), clf)
        pipe.fit(X_tr, y_tr)
        t0 = time.perf_counter()
        pred = pipe.predict(X_te)
        us = (time.perf_counter() - t0) / len(X_te) * 1e6
        prec, rec, f1, _ = precision_recall_fscore_support(
            y_te, pred, average="binary", zero_division=0)
        acc = accuracy_score(y_te, pred)
        kb = len(pickle.dumps(pipe)) / 1024
        print(f"  {nome:<30} {acc*100:6.1f} {prec:6.3f} {rec:6.3f} {f1:6.3f} "
              f"{kb:7.1f} {us:7.1f}", flush=True)
        if acc > melhor[1]:
            melhor = (nome, acc)
    return melhor


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=DEFAULT_DATA)
    args = ap.parse_args()
    if not os.path.isdir(args.data):
        print(f"dataset SUTD ausente: {args.data}", file=sys.stderr)
        return 1

    partes = carregar(args.data)
    print(f"  Base: walk test SUTD, andar 6, 2 RRUs x 1 RRU, "
          f"{sum(len(p) for p in partes)} amostras (2RRU={len(partes[0])}, 1RRU={len(partes[1])})")
    tr, te = split_temporal(partes)
    nome, acc = avaliar(tr, te)
    print()
    print(f"  Campeao (Instance): {nome} -> Acc {acc*100:.1f}%")
    print(f"  Artigo (Tabela 7, Instance): XGBoost 92,6% / F1 0,925")
    print(f"  (a famosa DNN 99,1% e' recorte *sequence*, fora da abordagem designada)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
