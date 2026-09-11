#!/usr/bin/env python3
"""
Treina o MLP do lab de inferência de dígitos (/lab/digitos) e grava os pesos em
`digitos-mlp.json`, que a página carrega e executa em JavaScript puro.

Por que este script existe
--------------------------
O exercício original do professor mandava o desenho para um endpoint de nuvem
cuja URL estava vazia no build arquivado: a inferência nunca aconteceu. Aqui o
modelo roda no navegador do aluno, e este script é a "casa de treinamento"
(training host) daquele fluxo: quem quiser pode regerar o JSON e chegar ao
mesmo modelo.

Dados
-----
- Conjunto: MNIST (LeCun, Cortes e Burges), dígitos manuscritos 28×28 em tons de
  cinza 0–255, obtido do OpenML: dataset `mnist_784`, versão 1 (id 554), via
  `sklearn.datasets.fetch_openml`. O download fica em cache em
  `~/scikit_learn_data` (ou no diretório de `--dados`).
- Divisão: a oficial do MNIST, que o OpenML preserva na ordem das linhas —
  as 60 000 primeiras são treino e as 10 000 últimas são teste.
  Das 60 000 de treino, as 5 000 últimas ficam de fora como VALIDAÇÃO (escolha
  da melhor época); o modelo treina com as 55 000 restantes. O teste só é
  tocado uma vez, no fim.

Pré-processamento (idêntico ao da página — é esse o ponto)
------------------------------------------------------------
O MNIST já vem com o dígito reduzido para caber em 20×20 e centralizado pelo
centro de massa num quadro 28×28. O desenho do aluno não vem assim. Para que o
modelo veja em produção a MESMA distribuição que viu no treino, a página e este
script aplicam a mesma função `preprocessar`, passo a passo:

  1. recorte pela caixa do traço (menor retângulo com pixel > 0);
  2. reescala por média de área para caber em 20×20, mantendo a proporção
     (lado maior = 20, o outro = arredondado, mínimo 1);
  3. colagem num quadro 28×28 com o centro de massa em (13,5; 13,5),
     deslocamento inteiro arredondado para baixo de (x + 0,5) e preso na borda;
  4. normalização: divide por 255, valores em 0–1.

A função é aplicada também ao próprio MNIST (treino, validação e teste), o que
garante que treino e inferência vejam exatamente o mesmo formato de dado.

Aumento de dados (só no treino)
-------------------------------
Desenho em canvas não tem a espessura nem a inclinação típicas do MNIST. Cada
imagem de treino ganha UMA cópia alterada, sorteada com a semente: rotação
uniforme em ±12°, e com probabilidade 0,35 um engrossamento do traço (dilatação
em tons de cinza 2×2). A cópia passa pelo mesmo `preprocessar`. Treino
efetivo: 110 000 imagens. Validação e teste NÃO são aumentados.

Modelo
------
MLP 784 → 64 → 10: camada densa com ReLU, camada densa com softmax.
Inicialização He, Adam (taxa 1e-3, β1 0,9, β2 0,999), lotes de 128, entropia
cruzada, 15 épocas; fica a época de maior acurácia de validação.

Exportação
----------
Os pesos de cada camada são quantizados em inteiros de 8 bits simétricos com
uma escala por camada (peso ≈ escala × inteiro); os vieses ficam em ponto
flutuante com 6 algarismos significativos. A acurácia publicada é a do modelo
QUANTIZADO — é ele que o navegador executa.

Resultado da execução que gerou o JSON publicado
------------------------------------------------
- data: 2026-09-11
- semente: 20260911
- época escolhida: 15 de 15
- acurácia de validação (float): 98,10 %
- acurácia de teste do modelo em float: 97,61 %
- acurácia de TESTE do modelo quantizado (o que roda na página): 97,62 %
- ambiente: Python 3.14, numpy 2.5.3, scipy 1.18.1, scikit-learn 1.9.1, 4 CPUs x86_64
- tempo: ~2 min; tamanho do JSON: ~156 KB
- reprodutibilidade: duas execuções seguidas na mesma máquina geraram pesos
  inteiros e vieses idênticos (50 816 números, nenhuma diferença)
(os números exatos de cada execução são gravados em `metadados` no JSON; em
outra máquina, a multiplicação de matrizes do BLAS pode variar na última casa
e mudar um ou outro inteiro quantizado, sem efeito visível na acurácia)

Uso
---
    python3 -m venv venv && venv/bin/pip install numpy scipy scikit-learn
    venv/bin/python treinar_digitos.py            # grava digitos-mlp.json ao lado
    venv/bin/python treinar_digitos.py --dados /caminho/cache --saida x.json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import platform
import time
from pathlib import Path

import numpy as np
import scipy
import sklearn
from scipy import ndimage
from sklearn.datasets import fetch_openml

SEMENTE = 20260911
OCULTA = 64
EPOCAS = 15
LOTE = 128
TAXA = 1e-3
N_TREINO_OFICIAL = 60_000
N_VALIDACAO = 5_000
LADO = 28
CAIXA = 20


# --------------------------------------------------------------------------
# Pré-processamento — espelho exato de `preprocessar()` em lab-digitos.html
# --------------------------------------------------------------------------
def pesos_area(origem: int, destino: int) -> np.ndarray:
    """Matriz destino×origem da reescala por média de área.

    O pixel j do destino cobre o intervalo [j·r, (j+1)·r) da origem, r = origem/destino;
    cada pixel i da origem entra com o comprimento da sobreposição, dividido por r.
    Serve para reduzir e para ampliar, e é a mesma conta da página.
    """
    r = origem / destino
    w = np.zeros((destino, origem), dtype=np.float64)
    for j in range(destino):
        a, b = j * r, (j + 1) * r
        i0, i1 = int(math.floor(a)), min(origem, int(math.ceil(b)))
        for i in range(i0, i1):
            sob = min(b, i + 1) - max(a, i)
            if sob > 0:
                w[j, i] = sob / r
    return w


def arred(x: float) -> int:
    """Arredonda meio para cima, como Math.floor(x + 0.5) no JavaScript.
    (o `round` do Python arredonda meio para o par e divergiria da página)"""
    return int(math.floor(x + 0.5))


def preprocessar(img: np.ndarray) -> np.ndarray | None:
    """Imagem H×W de intensidade 0–255 (traço claro) → vetor 784 em 0–1."""
    ys, xs = np.nonzero(img > 0)
    if ys.size == 0:
        return None
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rec = img[y0:y1, x0:x1].astype(np.float64)                      # 1. recorte
    h, w = rec.shape
    s = CAIXA / max(h, w)
    nh, nw = max(1, arred(h * s)), max(1, arred(w * s))
    peq = pesos_area(h, nh) @ rec @ pesos_area(w, nw).T             # 2. 20×20
    massa = peq.sum()
    cy = (peq.sum(axis=1) @ np.arange(nh)) / massa
    cx = (peq.sum(axis=0) @ np.arange(nw)) / massa
    oy = min(max(arred((LADO - 1) / 2 - cy), 0), LADO - nh)         # 3. centro
    ox = min(max(arred((LADO - 1) / 2 - cx), 0), LADO - nw)
    q = np.zeros((LADO, LADO), dtype=np.float64)
    q[oy:oy + nh, ox:ox + nw] = peq
    return (q / 255.0).reshape(-1)                                  # 4. 0–1


def aumentar(img: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    ang = rng.uniform(-12.0, 12.0)
    out = ndimage.rotate(img.astype(np.float64), ang, reshape=False, order=1, mode="constant", cval=0.0)
    if rng.random() < 0.35:
        out = ndimage.grey_dilation(out, size=(2, 2))
    return np.clip(out, 0, 255)


def lote_preprocessado(imgs: np.ndarray) -> np.ndarray:
    out = np.zeros((len(imgs), LADO * LADO), dtype=np.float32)
    for k, im in enumerate(imgs):
        v = preprocessar(im)
        if v is not None:
            out[k] = v
    return out


# --------------------------------------------------------------------------
# MLP em numpy
# --------------------------------------------------------------------------
def softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def adiante(p: dict, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    h = np.maximum(0.0, x @ p["W1"].T + p["b1"])
    return h, softmax(h @ p["W2"].T + p["b2"])


def acuracia(p: dict, x: np.ndarray, y: np.ndarray) -> float:
    return float((adiante(p, x)[1].argmax(axis=1) == y).mean())


def treinar(xtr, ytr, xva, yva, rng):
    p = {
        "W1": (rng.standard_normal((OCULTA, 784)) * math.sqrt(2 / 784)).astype(np.float32),
        "b1": np.zeros(OCULTA, dtype=np.float32),
        "W2": (rng.standard_normal((10, OCULTA)) * math.sqrt(2 / OCULTA)).astype(np.float32),
        "b2": np.zeros(10, dtype=np.float32),
    }
    m = {k: np.zeros_like(v) for k, v in p.items()}
    v = {k: np.zeros_like(v) for k, v in p.items()}
    b1, b2, eps, t = 0.9, 0.999, 1e-8, 0
    melhor, melhor_ep, melhor_p = -1.0, 0, None
    for ep in range(1, EPOCAS + 1):
        ordem = rng.permutation(len(xtr))
        for i in range(0, len(ordem), LOTE):
            idx = ordem[i:i + LOTE]
            x, y = xtr[idx], ytr[idx]
            h, pr = adiante(p, x)
            d2 = pr.copy()
            d2[np.arange(len(y)), y] -= 1.0
            d2 /= len(y)
            g = {"W2": d2.T @ h, "b2": d2.sum(axis=0)}
            dh = (d2 @ p["W2"]) * (h > 0)
            g["W1"], g["b1"] = dh.T @ x, dh.sum(axis=0)
            t += 1
            for k in p:
                m[k] = b1 * m[k] + (1 - b1) * g[k]
                v[k] = b2 * v[k] + (1 - b2) * g[k] ** 2
                mh, vh = m[k] / (1 - b1 ** t), v[k] / (1 - b2 ** t)
                p[k] -= (TAXA * mh / (np.sqrt(vh) + eps)).astype(np.float32)
        acc = acuracia(p, xva, yva)
        print(f"  época {ep:2d}: validação {acc * 100:.2f} %")
        if acc > melhor:
            melhor, melhor_ep, melhor_p = acc, ep, {k: x.copy() for k, x in p.items()}
    return melhor_p, melhor, melhor_ep


def quantizar(w: np.ndarray) -> tuple[float, np.ndarray]:
    escala = float(np.abs(w).max()) / 127.0
    return escala, np.clip(np.rint(w / escala), -127, 127).astype(np.int8)


def sig(x: float, n: int = 6) -> float:
    return float(f"{x:.{n}g}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--dados", default=None, help="cache do fetch_openml (padrão: ~/scikit_learn_data)")
    ap.add_argument("--saida", default=str(Path(__file__).with_name("digitos-mlp.json")))
    args = ap.parse_args()

    t0 = time.time()
    print("baixando/lendo MNIST do OpenML (mnist_784 v1)…")
    X, y = fetch_openml("mnist_784", version=1, as_frame=False, parser="liac-arff", data_home=args.dados, return_X_y=True)
    X = X.reshape(-1, LADO, LADO)
    y = y.astype(np.int64)

    n_tr = N_TREINO_OFICIAL - N_VALIDACAO
    rng = np.random.default_rng(SEMENTE)
    print("pré-processando (o mesmo pipeline da página)…")
    xtr_orig = lote_preprocessado(X[:n_tr])
    xtr_aum = lote_preprocessado(np.stack([aumentar(im, rng) for im in X[:n_tr]]))
    xtr = np.concatenate([xtr_orig, xtr_aum])
    ytr = np.concatenate([y[:n_tr], y[:n_tr]])
    xva, yva = lote_preprocessado(X[n_tr:N_TREINO_OFICIAL]), y[n_tr:N_TREINO_OFICIAL]
    xte, yte = lote_preprocessado(X[N_TREINO_OFICIAL:]), y[N_TREINO_OFICIAL:]

    print(f"treinando MLP 784→{OCULTA}→10 com {len(xtr)} imagens…")
    p, acc_va, ep = treinar(xtr, ytr, xva, yva, rng)

    e1, q1 = quantizar(p["W1"])
    e2, q2 = quantizar(p["W2"])
    pq = {"W1": q1.astype(np.float32) * e1, "b1": p["b1"], "W2": q2.astype(np.float32) * e2, "b2": p["b2"]}
    acc_te_float = acuracia(p, xte, yte)
    acc_te = acuracia(pq, xte, yte)
    pred = adiante(pq, xte)[1].argmax(axis=1)
    confusao = np.zeros((10, 10), dtype=int)
    np.add.at(confusao, (yte, pred), 1)
    print(f"época escolhida {ep} · validação {acc_va * 100:.2f} % · teste float {acc_te_float * 100:.2f} % · "
          f"teste quantizado {acc_te * 100:.2f} %")

    modelo = {
        "formato": "digitos-mlp/1",
        "metadados": {
            "descricao": "MLP 784→64→10 treinado em MNIST para o lab /lab/digitos do painel Core5G_ARM64.",
            "gerado_por": "server/panel/static/lab/modelos/treinar_digitos.py",
            "data": dt.date.today().isoformat(),
            "semente": SEMENTE,
            "dataset": {
                "nome": "MNIST (LeCun, Cortes e Burges)",
                "origem": "OpenML mnist_784, versão 1 (id 554), via sklearn.datasets.fetch_openml",
                "divisao": "linhas 0–54999 treino, 55000–59999 validação (escolha de época), 60000–69999 teste (o teste oficial do MNIST)",
                "treino": n_tr, "validacao": N_VALIDACAO, "teste": len(yte),
                "aumento_treino": "1 cópia por imagem: rotação uniforme ±12°, dilatação 2×2 com prob. 0,35; treino efetivo = 110000",
            },
            "preprocessamento": [
                "recorte pela caixa do traço (pixels > 0)",
                "reescala por média de área para caber em 20×20 mantendo a proporção",
                "colagem em 28×28 com o centro de massa em (13,5; 13,5), deslocamento inteiro",
                "divisão por 255 (valores 0–1), vetor em ordem de linhas",
            ],
            "arquitetura": "densa 784→64 + ReLU; densa 64→10 + softmax",
            "treino": {"otimizador": "Adam", "taxa": TAXA, "lote": LOTE, "epocas": EPOCAS, "epoca_escolhida": ep,
                       "perda": "entropia cruzada", "inicializacao": "He"},
            "acuracia_validacao_float": round(acc_va, 4),
            "acuracia_teste_float": round(acc_te_float, 4),
            "acuracia_teste": round(acc_te, 4),
            "acuracia_teste_nota": "acurácia do modelo quantizado, o mesmo que a página executa",
            "matriz_confusao_teste": {"linhas": "rótulo verdadeiro 0–9", "colunas": "previsto 0–9", "valores": confusao.tolist()},
            "quantizacao": "pesos int8 simétricos por camada: peso = escala × inteiro; vieses float com 6 algarismos significativos",
            "ambiente": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                         "scikit_learn": sklearn.__version__},
            "tempo_s": round(time.time() - t0, 1),
        },
        "entrada": {"forma": [1, 784], "ordem": "linhas de cima para baixo, cada linha da esquerda para a direita",
                    "valores": "0 (fundo) a 1 (traço)"},
        "camadas": [
            {"tipo": "densa", "ativacao": "relu", "entradas": 784, "saidas": OCULTA, "escala": sig(e1, 8),
             "W": q1.reshape(-1).tolist(), "b": [sig(float(x)) for x in p["b1"]]},
            {"tipo": "densa", "ativacao": "softmax", "entradas": OCULTA, "saidas": 10, "escala": sig(e2, 8),
             "W": q2.reshape(-1).tolist(), "b": [sig(float(x)) for x in p["b2"]]},
        ],
    }
    # metadados indentados para leitura humana; cada vetor de pesos numa linha só
    vetores = {}
    for n, c in enumerate(modelo["camadas"]):
        for k in ("W", "b"):
            marca = f"@@{k}{n}@@"
            vetores[json.dumps(marca)] = json.dumps(c[k], separators=(",", ":"))
            c[k] = marca
    txt = json.dumps(modelo, ensure_ascii=False, indent=2)
    for marca, vetor in vetores.items():
        txt = txt.replace(marca, vetor)
    Path(args.saida).write_text(txt + "\n", encoding="utf-8")
    print(f"gravado {args.saida} ({len(txt.encode()) / 1024:.0f} KB) em {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
