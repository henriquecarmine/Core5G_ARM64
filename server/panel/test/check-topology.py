#!/usr/bin/env python3
"""Verificador GEOMÉTRICO das topologias (static/openran-topology*.json).

Garante que o diagrama não induz leitura errada (ex.: linha N3 do gNB→UPF
passando por trás do card do RIC e parecendo uma conexão RIC→UPF):
- nenhum link (segmento centro-a-centro) atravessa card de nó que não é endpoint;
- nenhum card sobrepõe outro (folga mínima de 12px) nem sai do canvas;
- bandas CUPS (layers com band:true) não se sobrepõem nem engolem nós de
  outras camadas (mesmo padding do render: x±24, topo 30, base 14).

Uso: python3 check-topology.py            # valida os dois projetos
     python3 check-topology.py arq.json   # valida um arquivo específico
Sai com código != 0 se houver erro (CI-friendly). Avisos (<6px) não reprovam.
"""
import json
import sys
from pathlib import Path

NODE_W, NODE_H = 184, 66            # tamanho do card em topology.html
PAD_X, PAD_TOP, PAD_BOT = 24, 30, 14  # padding das bandas no render

STATIC = Path(__file__).resolve().parent.parent / "static"
DEFAULT = [STATIC / "openran-topology.json", STATIC / "openran-topology-p1.json"]


def center(n):
    return (n["x"] + NODE_W / 2, n["y"] + NODE_H / 2)


def rect(n, m=0.0):
    return (n["x"] - m, n["y"] - m, n["x"] + NODE_W + m, n["y"] + NODE_H + m)


def seg_hits_rect(a, b, r):
    """Liang-Barsky: True se o segmento a→b cruza o retângulo r."""
    x0, y0, x1, y1 = r
    dx, dy = b[0] - a[0], b[1] - a[1]
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, a[0] - x0), (dx, x1 - a[0]), (-dy, a[1] - y0), (dy, y1 - a[1])):
        if p == 0:
            if q < 0:
                return False
            continue
        t = q / p
        if p < 0:
            if t > t1:
                return False
            t0 = max(t0, t)
        else:
            if t < t0:
                return False
            t1 = min(t1, t)
    return t0 <= t1


def check(path):
    d = json.load(open(path))
    nodes = {n["id"]: n for n in d["nodes"]}
    cw, ch = d["canvas"]["w"], d["canvas"]["h"]
    problems, warns = [], []

    for n in d["nodes"]:
        if n["x"] < 0 or n["y"] < 0 or n["x"] + NODE_W > cw or n["y"] + NODE_H > ch:
            problems.append(f"FORA DO CANVAS: {n['id']} ({n['x']},{n['y']})")

    ids = list(nodes)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            ra, rb = rect(nodes[a]), rect(nodes[b], 12)
            if ra[0] < rb[2] and ra[2] > rb[0] and ra[1] < rb[3] and ra[3] > rb[1]:
                problems.append(f"CARDS PRÓXIMOS/SOBREPOSTOS (<12px): {a} × {b}")

    for lk in d["links"]:
        a, b = nodes.get(lk["from"]), nodes.get(lk["to"])
        if not a or not b:
            problems.append(f"LINK COM NÓ INEXISTENTE: {lk['from']}→{lk['to']}")
            continue
        ca, cb = center(a), center(b)
        for n in d["nodes"]:
            if n["id"] in (lk["from"], lk["to"]):
                continue
            if seg_hits_rect(ca, cb, rect(n)):
                problems.append(
                    f"LINK ATRAVESSA CARD: {lk['from']}→{lk['to']} ({lk['iface']}) passa por trás de '{n['id']}'")
            elif seg_hits_rect(ca, cb, rect(n, 6)):
                warns.append(f"quase-toque (<6px): {lk['from']}→{lk['to']} ({lk['iface']}) × '{n['id']}'")

    bboxes = {}
    for k, ly in d["layers"].items():
        if not ly.get("band"):
            continue
        ns = [n for n in d["nodes"] if n["layer"] == k]
        if ns:
            bboxes[k] = (min(n["x"] for n in ns) - PAD_X, min(n["y"] for n in ns) - PAD_TOP,
                         max(n["x"] + NODE_W for n in ns) + PAD_X, max(n["y"] + NODE_H for n in ns) + PAD_BOT)
    ks = list(bboxes)
    for i, a in enumerate(ks):
        for b in ks[i + 1:]:
            ra, rb = bboxes[a], bboxes[b]
            if ra[0] < rb[2] and ra[2] > rb[0] and ra[1] < rb[3] and ra[3] > rb[1]:
                problems.append(f"BANDAS SOBREPOSTAS: {a} × {b}")
    for k, bb in bboxes.items():
        for n in d["nodes"]:
            if n["layer"] != k:
                r = rect(n)
                if r[0] < bb[2] and r[2] > bb[0] and r[1] < bb[3] and r[3] > bb[1]:
                    problems.append(f"NÓ DE OUTRA CAMADA DENTRO DA BANDA {k}: {n['id']}")

    print(f"== {path} ==")
    for p in problems:
        print("  ERRO:", p)
    for w in warns:
        print("  aviso:", w)
    if not problems and not warns:
        print("  OK — geometria limpa")
    return bool(problems)


if __name__ == "__main__":
    paths = [Path(p) for p in sys.argv[1:]] or DEFAULT
    sys.exit(1 if any(check(p) for p in paths) else 0)
