#!/usr/bin/env python3
"""Reconstrói os CSVs de classificação do professor: o pdftotext separa a coluna
de RÓTULO (texto) num bloco após as linhas de features. Aqui a gente casa de
volta: N linhas de features (nfeat tokens) + 1 header de rótulo + N valores."""
import subprocess, re
from pathlib import Path

BASE = Path(__file__).resolve().parent
SRC = BASE.parent.parent / "Base Fonts RIC"
OUT = BASE / "data"
OUT.mkdir(exist_ok=True)
FILES = ["cell_congestion_tree", "cell_failure_logistic", "kNN_Practice_100rows",
         "naivebayes_practice", "svm_interference_dataset"]


def numeric(tok):
    return bool(re.fullmatch(r"-?\d+(\.\d+)?", tok))


for f in FILES:
    txt = subprocess.run(["pdftotext", "-layout", str(SRC / f"{f}.pdf"), "-"],
                         capture_output=True, text=True).stdout
    lines = [re.sub(r"\s+", " ", l).strip() for l in txt.splitlines() if l.strip()]
    header = lines[0].split(" ")
    nfeat = len(header)
    feats, labels, label_name = [], [], None
    for l in lines[1:]:
        toks = l.split(" ")
        if len(toks) == nfeat and all(numeric(t) for t in toks):
            feats.append(toks)
        elif len(toks) == 1:
            if label_name is None:
                label_name = toks[0]
            else:
                labels.append(toks[0])
        else:
            print(f"  [{f}] linha inesperada ({len(toks)} tok): {l[:50]}")
    n = min(len(feats), len(labels))
    if len(feats) != len(labels):
        print(f"  [{f}] AVISO: {len(feats)} features x {len(labels)} rótulos -> uso {n}")
    cols = header + [label_name or "Label"]
    rows = [",".join(feats[i] + [labels[i]]) for i in range(n)]
    (OUT / f"{f}.csv").write_text(",".join(cols) + "\n" + "\n".join(rows) + "\n")
    # distribuição de classes
    from collections import Counter
    dist = Counter(labels[:n])
    print(f"{f:<26s} rótulo='{label_name}' n={n}  classes={dict(dist)}")
