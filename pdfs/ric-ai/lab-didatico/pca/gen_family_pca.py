#!/usr/bin/env python3
"""
Card "PCA" (redução de dimensionalidade) — dataset pca_practice do professor.
Exporta: variância explicada por componente, loadings (peso de cada KPI em cada
PC), projeção 2D (PC1×PC2) de cada célula, e o scaler+componentes para projetar
a célula-teste ao vivo em JS (z·W). Saída: datasets_config.json
"""
from __future__ import annotations
import json, subprocess, re
from pathlib import Path
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

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
    X, COLS = load("pca_practice.pdf")
    scaler = StandardScaler().fit(X)
    Z = scaler.transform(X)
    pca = PCA().fit(Z)
    proj = pca.transform(Z)

    feats = [{"key": c, "label": KPI[c]["label"], "unit": KPI[c]["unit"], "hard": KPI[c]["hard"],
              "train": [round(float(X[:, i].min()), 1), round(float(X[:, i].max()), 1)], "decimals": KPI[c]["dec"]}
             for i, c in enumerate(COLS)]
    points = [{**{c: round(float(X[r, i]), 2) for i, c in enumerate(COLS)},
               "pc1": round(float(proj[r, 0]), 3), "pc2": round(float(proj[r, 1]), 3)} for r in range(len(X))]
    start = {c: round(float(np.median(X[:, i])), KPI[c]["dec"]) for i, c in enumerate(COLS)}

    ds = {"label": "PCA", "source": "Prof. Tesolin", "usecase": "resumir muitos KPIs em poucas dimensões",
          "n_rows": int(len(X)), "features": feats, "points": points,
          "scaler": {"mean": [round(float(m), 5) for m in scaler.mean_], "std": [round(float(s), 5) for s in scaler.scale_]},
          "components": [[round(float(c), 4) for c in row] for row in pca.components_[:2]],
          "explained": [round(float(v), 4) for v in pca.explained_variance_ratio_],
          "start": start}
    return {"family": "PCA", "default": "pca", "datasets": {"pca": ds}}


def main():
    out = build(); OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    ds = out["datasets"]["pca"]
    ev = ds["explained"]
    print(f"n={ds['n_rows']} feats={[f['key'] for f in ds['features']]}")
    print("variância explicada:", [f"{v*100:.1f}%" for v in ev], "| PC1+PC2 =", f"{(ev[0]+ev[1])*100:.1f}%")
    print("loadings PC1:", dict(zip([f['key'] for f in ds['features']], ds['components'][0])))
    print(f"{OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
