#!/usr/bin/env python3
"""
Insere a seção "🔍 Os modelos, um a um" (detalhamento de cada algoritmo via
lab-models.js) em cada aula, logo antes da seção de Relatório. Idempotente.

Alvos: as 5 páginas base servidas + o tpl de classificação (p/ localizacao e
manutencao herdarem ao rodar build_sutd_cards.py em seguida).
"""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent  # repo root
STATIC = ROOT / "server" / "panel" / "static"
TPL = Path(__file__).resolve().parent / "classificacao" / "card-classificacao.tpl.html"

# arquivo -> lista de modelos daquela aula (ordem = a da tabela)
TARGETS = {
    STATIC / "lab-regressao.html":    "linear,ridge,tree,rf,gb,knn,svr,mlp",
    STATIC / "lab-classificacao.html": "logistic,tree,rf,gb,knn,nb,svm",
    STATIC / "lab-clustering.html":   "kmeans,dbscan,agg",
    STATIC / "lab-anomalia.html":     "isoforest",
    STATIC / "lab-pca.html":          "pca",
    TPL:                              "logistic,tree,rf,gb,knn,nb,svm",
}

SECTION = """  <section class="card">
    <h2>🔍 Os modelos, um a um</h2>
    <p class="sub">Todos recebem os mesmos KPIs (coletados via E2/KPM). O que muda é o que cada um <b>faz</b> com eles — clique para abrir.</p>
    <div data-model-deepdive="__LIST__"></div>
  </section>
  <script src="/static/lab-models.js"></script>

"""
REPORT_H2 = "<h2>📄 Relatório</h2>"


def patch(path: Path, models: str) -> str:
    txt = path.read_text(encoding="utf-8")
    if "data-model-deepdive" in txt:
        return "já tinha"
    i = txt.find(REPORT_H2)
    if i < 0:
        return "SEM âncora de Relatório"
    sec = txt.rfind("<section", 0, i)     # início da seção de Relatório
    if sec < 0:
        return "SEM <section> antes do Relatório"
    block = SECTION.replace("__LIST__", models)
    txt = txt[:sec] + block + txt[sec:]
    path.write_text(txt, encoding="utf-8")
    return f"OK ({models})"


if __name__ == "__main__":
    for path, models in TARGETS.items():
        print(f"{path.name:<28s} {patch(path, models)}")
