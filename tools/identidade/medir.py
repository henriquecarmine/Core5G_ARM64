#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mede o contraste WCAG de todos os pares que a identidade promete.

Sai com código != 0 se algum par ficar abaixo do alvo — dá para pôr em CI.
Uso:  python3 tools/identidade/medir.py
"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from paleta import todas                            # noqa: E402
from oklch import contraste                         # noqa: E402

E = todas()
falhas = []

# (rótulo, família+degrau do texto, família+degrau do fundo, alvo)
PARES = [
    ("tinta sobre a superfície",        ("n", 12), ("n", 1), 4.5),
    ("tinta 2ª sobre a superfície",     ("n", 11), ("n", 1), 4.5),
    ("tinta 3ª sobre a superfície",     ("n", 9),  ("n", 1), 3.0),
    ("tinta 2ª sobre o cartão",         ("n", 11), ("n", 2), 4.5),
    ("tinta sobre o painel aninhado",   ("n", 12), ("n", 3), 4.5),
    ("tinta 2ª no painel aninhado",     ("n", 11), ("n", 3), 4.5),
    ("texto do acento",                 ("a", 11), ("n", 1), 4.5),
    ("texto de bom",                    ("g", 11), ("n", 1), 4.5),
    ("texto de atenção",                ("w", 11), ("n", 1), 4.5),
    ("texto de falha",                  ("r", 11), ("n", 1), 4.5),
    ("texto de ao vivo",                ("l", 11), ("n", 1), 4.5),
]

for tema in ("claro", "escuro"):
    S = E[tema]
    forte = 9 if tema == "claro" else 8
    print(f"\n===== TEMA {tema.upper()} =====")
    for rot, (ff, di), (fb, db), alvo in PARES:
        fg, bg = S[ff][di-1], S[fb][db-1]
        v = contraste(fg, bg)
        ok = v >= alvo
        if not ok:
            falhas.append(f"{tema}: {rot} = {v:.2f}:1 (alvo {alvo})")
        print(f"  {'OK   ' if ok else 'FALHA'} {v:6.2f}:1  alvo {alvo:>3}  {rot}")
    # limite de componente: 3:1 é o mínimo para um contorno que delimita controle
    v = contraste(S["n"][forte-1], S["n"][0])
    ok = v >= 3.0
    if not ok:
        falhas.append(f"{tema}: --line-strong = {v:.2f}:1 (alvo 3.0)")
    print(f"  {'OK   ' if ok else 'FALHA'} {v:6.2f}:1  alvo 3.0  --line-strong (degrau {forte}) sobre a superfície")

    print("  -- sólidos de sinalização --")
    for f, nome in (("a", "acento"), ("g", "bom"), ("w", "atenção"), ("r", "falha"), ("l", "ao vivo")):
        s = S[f][8]
        no_fundo = contraste(s, S["n"][0])
        preto, branco = contraste(s, "#000000"), contraste(s, "#ffffff")
        rotulo = "preto" if preto > branco else "branco"
        nota = "" if no_fundo >= 3.0 else "  (o anel do ponto desenha o limite)"
        print(f"        {nome:9} {s}  no fundo {no_fundo:5.2f}:1 · rótulo {rotulo} {max(preto, branco):5.2f}:1{nota}")

if falhas:
    print("\n✗ CONTRASTE REPROVADO:")
    for f in falhas:
        print("  -", f)
    sys.exit(1)
# o console é escuro nos dois temas — mede contra o próprio fundo dele
from oklch import contraste as _c
v = _c("#d7dbe0", "#0d0e11")
print(f"\n  {'OK   ' if v >= 4.5 else 'FALHA'} {v:6.2f}:1  alvo 4.5  tinta do console sobre o console")
if v < 4.5:
    falhas.append(f"console: {v:.2f}:1")

if falhas:
    print("\n✗ CONTRASTE REPROVADO:")
    for f in falhas:
        print("  -", f)
    sys.exit(1)
print("\n✅ contraste OK em todos os pares prometidos, nos dois temas")
