#!/usr/bin/env python3
"""
Card "Clustering" (família, NÃO supervisionado) — datasets do Prof. Tesolin.
Roda k-means (base do "Mexe" ao vivo via centróide mais próximo) e compara com
DBSCAN e hierárquico por SILHUETA. Sem rótulo — o modelo agrupa sozinho.
Saída: datasets_config.json
"""
from __future__ import annotations
import json, subprocess, re
from pathlib import Path
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics import silhouette_score

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
DATASETS = [
    {"key": "kmeans", "file": "kmeans_practice.pdf", "label": "Base k-means"},
    {"key": "dbscan", "file": "dbscan_practive.pdf", "label": "Base DBSCAN"},
    {"key": "agg",    "file": "aggclustering_practice.pdf", "label": "Base hierárquica"},
]


def numeric(t):
    return bool(re.fullmatch(r"-?\d+(\.\d+)?", t))


def load(pdf):
    """Lê as 5 features base (Cell_X + 5 números) + colunas EXTRA que o pdftotext
    joga em blocos separados (header de texto + N valores). Retorna (X, cols)."""
    txt = subprocess.run(["pdftotext", "-layout", str(SRC / pdf), "-"], capture_output=True, text=True).stdout
    lines = [re.sub(r"\s+", " ", l).strip() for l in txt.splitlines() if l.strip()]
    rows, extras, cur = [], {}, None
    for l in lines[1:]:
        toks = l.split(" ")
        if len(toks) == 6 and toks[0].lower().startswith("cell_") and all(numeric(t) for t in toks[1:]):
            rows.append([float(x) for x in toks[1:]])
        elif len(toks) == 1:
            if numeric(toks[0]) and cur is not None:
                extras[cur].append(float(toks[0]))
            elif not numeric(toks[0]):
                cur = toks[0]; extras.setdefault(cur, [])
    X = np.array(rows)
    cols = BASE_COLS.copy()
    for name, vals in extras.items():
        if len(vals) == len(rows) and name in KPI:
            X = np.column_stack([X, vals]); cols.append(name)
    return X, cols


def dbscan_best(Xs):
    """DBSCAN com eps varrido; escolhe o de melhor silhueta com >=2 clusters."""
    best = {"sil": None, "eps": None, "n": 0}
    for eps in [0.5, 0.8, 1.0, 1.3, 1.6, 2.0, 2.5]:
        lab = DBSCAN(eps=eps, min_samples=3).fit_predict(Xs)
        uniq = set(lab) - {-1}
        if len(uniq) >= 2:
            mask = lab != -1
            if mask.sum() > len(uniq):
                s = silhouette_score(Xs[mask], lab[mask])
                if best["sil"] is None or s > best["sil"]:
                    best = {"sil": round(float(s), 3), "eps": eps, "n": len(uniq)}
    return best


def build(d):
    X, COLS = load(d["file"])
    scaler = StandardScaler().fit(X)
    Xs = scaler.transform(X)

    kmeans = {}
    for k in (2, 3, 4):
        km = KMeans(n_clusters=k, n_init=10, random_state=SEED).fit(Xs)
        kmeans[str(k)] = {
            "labels": km.labels_.tolist(),
            "centroids_std": [[round(float(c), 4) for c in row] for row in km.cluster_centers_],
            "centroids_orig": [[round(float(c), 1) for c in scaler.inverse_transform([row])[0]] for row in km.cluster_centers_],
            "silhouette": round(float(silhouette_score(Xs, km.labels_)), 3),
        }
    kdef = 3
    agg_lab = AgglomerativeClustering(n_clusters=kdef).fit_predict(Xs)
    db = dbscan_best(Xs)
    algos = [
        {"name": f"k-means (k={kdef})", "sil": kmeans[str(kdef)]["silhouette"]},
        {"name": f"Hierárquico (k={kdef})", "sil": round(float(silhouette_score(Xs, agg_lab)), 3)},
        {"name": f"DBSCAN (eps={db['eps']})" if db["eps"] else "DBSCAN", "sil": db["sil"]},
    ]

    feats = [{"key": c, "label": KPI[c]["label"], "unit": KPI[c]["unit"], "hard": KPI[c]["hard"],
              "train": [round(float(X[:, i].min()), 1), round(float(X[:, i].max()), 1)], "decimals": KPI[c]["dec"]}
             for i, c in enumerate(COLS)]
    points = [{**{c: round(float(X[r, i]), 1) for i, c in enumerate(COLS)},
               "k": {str(k): int(kmeans[str(k)]["labels"][r]) for k in (2, 3, 4)}}
              for r in range(len(X))]
    start = {c: round(float(np.median(X[:, i])), KPI[c]["dec"]) for i, c in enumerate(COLS)}
    # eixos padrão = 2 features de maior variância (mais separam visualmente)
    var = Xs.var(axis=0)
    order = list(np.argsort(var)[::-1])
    view = {"x": COLS[order[0]], "y": COLS[order[1]]}

    return {"label": d["label"], "source": "Prof. Tesolin", "usecase": "agrupar células parecidas sem rótulo",
            "n_rows": int(len(X)), "features": feats, "points": points,
            "scaler": {"mean": [round(float(m), 5) for m in scaler.mean_], "std": [round(float(s), 5) for s in scaler.scale_]},
            "kmeans": kmeans, "default_k": kdef, "algos": algos, "start": start, "view": view}


def main():
    out = {"family": "Clustering", "default": "kmeans", "datasets": {}}
    for d in DATASETS:
        out["datasets"][d["key"]] = build(d)
        r = out["datasets"][d["key"]]
        print(f"{d['key']:<8s} n={r['n_rows']:>3d}  k-means sil(k=2/3/4)="
              f"{r['kmeans']['2']['silhouette']}/{r['kmeans']['3']['silhouette']}/{r['kmeans']['4']['silhouette']}"
              f"  algos={[(a['name'],a['sil']) for a in r['algos']]}")
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"\n{OUT.name}: {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
