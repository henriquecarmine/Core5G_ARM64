#!/usr/bin/env python3
"""
Card "Anomalia" (não supervisionado) — dataset isolationforest_practice do prof.
Roda Isolation Forest DE VERDADE para rotular as células (normal/anomalia) em 3
níveis de sensibilidade. Para a célula-teste ao vivo (JS não roda IF), calibra um
limiar de distância padronizada consistente com o IF — mesmo princípio: anomalia
= fica longe da massa "normal".
Saída: datasets_config.json
"""
from __future__ import annotations
import json, subprocess, re
from pathlib import Path
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

SEED = 42
HERE = Path(__file__).resolve().parent
SRC = HERE.parent.parent / "Base Fonts RIC"
OUT = HERE / "datasets_config.json"
BASE_COLS = ["Throughput_Mbps", "Latency_ms", "PRB_Utilization", "Active_Users", "Energy_Consumption_W"]
KPI = {
    "Throughput_Mbps":     {"label": "Throughput",      "unit": "Mbps", "hard": [0, 1000], "dec": 0},
    "Latency_ms":          {"label": "Latência",        "unit": "ms",   "hard": [0, 200],  "dec": 0},
    "PRB_Utilization":     {"label": "PRB utilizado",   "unit": "%",    "hard": [0, 100],  "dec": 0},
    "Active_Users":        {"label": "Usuários ativos", "unit": "",     "hard": [0, 1000], "dec": 0},
    "Energy_Consumption_W":{"label": "Energia",         "unit": "W",    "hard": [0, 2000], "dec": 0},
    "Packet_Loss_Rate":    {"label": "Perda de pacotes","unit": "%",    "hard": [0, 100],  "dec": 2},
}
LEVELS = {"0.05": "baixa", "0.10": "média", "0.15": "alta"}


def numeric(t): return bool(re.fullmatch(r"-?\d+(\.\d+)?", t))


def load(pdf):
    txt = subprocess.run(["pdftotext", "-layout", str(SRC / pdf), "-"], capture_output=True, text=True).stdout
    lines = [re.sub(r"\s+", " ", l).strip() for l in txt.splitlines() if l.strip()]
    rows, extras, cur = [], {}, None
    for l in lines[1:]:
        toks = l.split(" ")
        if len(toks) == 6 and toks[0].lower().startswith("cell_") and all(numeric(t) for t in toks[1:]):
            rows.append([float(x) for x in toks[1:]])
        elif len(toks) == 1:
            if numeric(toks[0]) and cur is not None: extras[cur].append(float(toks[0]))
            elif not numeric(toks[0]): cur = toks[0]; extras.setdefault(cur, [])
    X = np.array(rows); cols = BASE_COLS.copy()
    for name, vals in extras.items():
        if len(vals) == len(rows) and name in KPI:
            X = np.column_stack([X, vals]); cols.append(name)
    return X, cols


def build():
    X, COLS = load("isolationforest_practice.pdf")
    scaler = StandardScaler().fit(X)
    Xs = scaler.transform(X)
    dist = np.linalg.norm(Xs, axis=1)  # distância padronizada à média (=0)

    levels = {}
    point_flags = {r: {} for r in range(len(X))}
    for lv in LEVELS:
        cont = float(lv)
        iforest = IsolationForest(contamination=cont, random_state=SEED, n_estimators=200)
        pred = iforest.fit_predict(Xs)  # 1 normal, -1 anomalia
        anom = pred == -1
        # limiar de distância consistente com o IF: entre a maior normal e a menor anomalia
        if anom.any() and (~anom).any():
            thr = float((dist[~anom].max() + dist[anom].min()) / 2)
        else:
            thr = float(np.quantile(dist, 1 - cont))
        levels[lv] = {"threshold": round(thr, 4), "count": int(anom.sum()), "label": LEVELS[lv]}
        for r in range(len(X)):
            point_flags[r][lv] = int(bool(anom[r]))

    feats = [{"key": c, "label": KPI[c]["label"], "unit": KPI[c]["unit"], "hard": KPI[c]["hard"],
              "train": [round(float(X[:, i].min()), 1), round(float(X[:, i].max()), 1)], "decimals": KPI[c]["dec"]}
             for i, c in enumerate(COLS)]
    points = [{**{c: round(float(X[r, i]), 2) for i, c in enumerate(COLS)},
               "dist": round(float(dist[r]), 3), "anom": point_flags[r]} for r in range(len(X))]
    start = {c: round(float(np.median(X[:, i])), KPI[c]["dec"]) for i, c in enumerate(COLS)}
    var = Xs.var(axis=0); order = list(np.argsort(var)[::-1])
    view = {"x": COLS[order[0]], "y": COLS[order[1]]}

    ds = {"label": "Isolation Forest", "source": "Prof. Tesolin", "usecase": "detectar células anômalas (manutenção preditiva)",
          "n_rows": int(len(X)), "features": feats, "points": points,
          "scaler": {"mean": [round(float(m), 5) for m in scaler.mean_], "std": [round(float(s), 5) for s in scaler.scale_]},
          "levels": levels, "default_level": "0.10", "dist_max": round(float(dist.max()), 3),
          "start": start, "view": view}
    return {"family": "Anomalia", "default": "isolationforest", "datasets": {"isolationforest": ds}}


def main():
    out = build(); OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    ds = out["datasets"]["isolationforest"]
    print(f"n={ds['n_rows']} feats={[f['key'] for f in ds['features']]}")
    for lv, d in ds["levels"].items():
        print(f"  contaminação {lv} ({d['label']}): {d['count']} anomalias, limiar dist={d['threshold']}")
    print(f"eixos={ds['view']} · {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
