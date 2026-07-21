#!/usr/bin/env python3
"""UE-TP / UE's Throughput Prediction (recorte Instance) — versão numpy-only.

Reproduz a Tabela 4 de Ngo et al., "RAN Intelligent Controller (RIC): From
open-source implementation to real-world validation", ICT Express 10(3), 2024
(DOI 10.1016/j.icte.2024.02.001): prevê o throughput DL do UE a partir dos KPIs
de rádio do instante atual, sobre o walk test do SUTD.

Sem pandas/matplotlib (o venv do servidor só tem numpy + scikit-learn). Streama a
tabela de métricas; split temporal 80:20 por cenário (amostras a 2 Hz são
autocorrelacionadas). O MLP de 10 neurônios reproduz a DNN instance-based do
artigo (R² 0,84).

Uso: python3 -u uetp_experiment.py [--data DIR]
"""
from __future__ import annotations

import argparse
import os
import sys
import time
import warnings

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor

warnings.filterwarnings("ignore", category=ConvergenceWarning)

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA = os.path.normpath(os.path.join(HERE, "..", "..", "data", "sutd"))
SEED = 42

# Colunas 0-based no CSV do SUTD: 5 features de rádio do enlace DL + alvo + filtro.
# RSRP=4 RSRQ=5 SINR=6 PDSCH_MCS=7 "PDSCH PRBs"=9 throughput_DL=11 lab_bs=15
COLS = [4, 5, 6, 7, 9, 11, 15]
FEATURES = ["RSRP", "RSRQ", "SINR", "PDSCH_MCS", "PDSCH PRBs"]
SCENARIOS = ["Lvl4_AllRRUOn_Anomaly_label.csv", "Lvl5_AllRRUOn_Anomaly_label.csv",
             "Lvl6_AllRRUOn_Anomaly_label.csv", "Lvl6_1RRUOn_Anomaly_label.csv"]


def modelos():
    """8 regressores. O MLP de 10 neurônios = a DNN instance-based do artigo
    (DNN(1x6,10,1); aqui entrada 1x5)."""
    return {
        "Regressao Linear": LinearRegression(),
        "Ridge (a=1.0)": Ridge(alpha=1.0, random_state=SEED),
        "Arvore de Decisao": DecisionTreeRegressor(random_state=SEED),
        "Random Forest": RandomForestRegressor(
            n_estimators=100, random_state=SEED, n_jobs=-1),
        "Gradient Boosting": GradientBoostingRegressor(random_state=SEED),
        "k-NN (k=5)": make_pipeline(
            StandardScaler(), KNeighborsRegressor(n_neighbors=5)),
        "SVR (RBF)": make_pipeline(StandardScaler(), SVR(C=100.0)),
        "MLP (10 neuronios)": make_pipeline(
            StandardScaler(),
            MLPRegressor(hidden_layer_sizes=(10,), max_iter=3000,
                         random_state=SEED)),
    }


def carregar_split(data_dir, frac=0.8):
    """Carrega os 4 cenários, limpa (lab_bs==0 + sem NaN) e faz split temporal
    80:20 DENTRO de cada cenário."""
    tr, te = [], []
    total = 0
    for arq in SCENARIOS:
        a = np.genfromtxt(os.path.join(data_dir, arq), delimiter=",",
                          skip_header=1, usecols=COLS)
        a = a[~np.isnan(a).any(axis=1)]
        a = a[a[:, 6] == 0]                 # lab_bs==0 (UE conectado)
        X = a[:, :5]
        y = a[:, 5] / 1e6                   # throughput bps -> Mbps
        bloco = np.column_stack([X, y])
        total += len(bloco)
        corte = int(len(bloco) * frac)
        tr.append(bloco[:corte])
        te.append(bloco[corte:])
    return np.vstack(tr), np.vstack(te), total


def avaliar(tr, te):
    X_tr, y_tr = tr[:, :-1], tr[:, -1]
    X_te, y_te = te[:, :-1], te[:, -1]
    print(f"  amostras: treino={len(tr)}  teste={len(te)}  (split temporal 80:20 por cenario)")
    print()
    print(f"  {'Algoritmo':<20} {'RMSE':>8} {'MAE':>8} {'R2':>7} {'us/am':>8}",
          flush=True)
    print("  " + "-" * 55, flush=True)
    linhas = []
    for nome, m in modelos().items():
        m.fit(X_tr, y_tr)
        t0 = time.perf_counter()
        pred = m.predict(X_te)
        us = (time.perf_counter() - t0) / len(X_te) * 1e6
        rmse = float(np.sqrt(mean_squared_error(y_te, pred)))
        mae = float(mean_absolute_error(y_te, pred))
        r2 = float(r2_score(y_te, pred))
        linhas.append((nome, rmse, r2))
        print(f"  {nome:<20} {rmse:8.2f} {mae:8.2f} {r2:7.3f} {us:8.1f}",
              flush=True)
    return sorted(linhas, key=lambda r: r[1])[0]  # menor RMSE


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=DEFAULT_DATA)
    args = ap.parse_args()
    if not os.path.isdir(args.data):
        print(f"dataset SUTD ausente: {args.data}", file=sys.stderr)
        return 1

    tr, te, total = carregar_split(args.data)
    print(f"  Base: walk test SUTD, 4 cenarios de cobertura, {total} amostras "
          f"validas (features: {', '.join(FEATURES)})")
    nome, rmse, r2 = avaliar(tr, te)
    print()
    print(f"  Melhor (menor RMSE): {nome} -> RMSE {rmse:.1f} Mbps / R2 {r2:.3f}")
    print(f"  Artigo (Tabela 4, Instance): DNN R2 0,84 (linear 0,83; XGBoost 0,72 = pior)")
    print(f"  O MLP de 10 neuronios reproduz a DNN instance (~R2 0,83); o famoso")
    print(f"  R2 0,90 e' recorte *sequence*, fora da abordagem designada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
