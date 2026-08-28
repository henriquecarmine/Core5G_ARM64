#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Escreve server/panel/static/tokens.css a partir de paleta.py.

Duas camadas, como manda a prática de design system:
  PRIMITIVA  --n-1..12, --a-*, --g-*, --w-*, --r-*   a cor em si
  SEMÂNTICA  --surface, --ink, --line, --accent...   o PAPEL da cor
A tela usa SÓ a semântica — é isso que faz claro e escuro serem coerentes em
vez de duas pinturas independentes.

Uso:  python3 tools/identidade/gerar_tokens.py
"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from paleta import todas, NOMES                      # noqa: E402

RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
DESTINO = os.path.join(RAIZ, "server", "panel", "static", "tokens.css")
E = todas()


def primitivas(tema, ind):
    linhas = []
    for fam, cores in E[tema].items():
        linhas.append(f"{ind}/* {NOMES[fam]} */")
        linhas.append(ind + " ".join(f"--{fam}-{i+1}:{c};" for i, c in enumerate(cores)))
    return "\n".join(linhas)


def semanticas(tema, ind):
    # traço forte: 9 no claro, 8 no escuro. O degrau 8 do claro mede 1,94:1 e
    # não serve de limite de componente (o mínimo é 3:1). Em vez de torcer a
    # rampa, o papel foi mapeado no degrau que mede — é para isso que a camada
    # semântica existe.
    forte = 9 if tema == "claro" else 8
    inset = 2 if tema == "claro" else 1
    tinta_no_acento = "#ffffff" if tema == "claro" else "#0d0d14"
    return f"""{ind}/* superfícies — da página ao painel elevado */
{ind}--surface:var(--n-1); --surface-2:var(--n-2); --surface-3:var(--n-3);
{ind}--surface-inset:var(--n-{inset});
{ind}/* traços */
{ind}--line:var(--n-6); --line-2:var(--n-7); --line-strong:var(--n-{forte});
{ind}/* tinta */
{ind}--ink:var(--n-12); --ink-2:var(--n-11); --ink-3:var(--n-9);
{ind}/* acento — a cor do produto: foco, seleção, ação principal, link */
{ind}--accent:var(--a-9); --accent-hover:var(--a-10);
{ind}--accent-ink:{tinta_no_acento};
{ind}--accent-text:var(--a-11); --accent-soft:var(--a-3); --accent-line:var(--a-7);
{ind}/* estado — sinalização padrão */
{ind}--good:var(--g-9); --good-text:var(--g-11); --good-soft:var(--g-3);
{ind}--warn:var(--w-9); --warn-text:var(--w-11); --warn-soft:var(--w-3);
{ind}--bad:var(--r-9);  --bad-text:var(--r-11);  --bad-soft:var(--r-3);
{ind}/* foco visível */
{ind}--focus:var(--a-9);"""


CSS = f"""/* =====================================================================
   Core5G_ARM64 — identidade visual.  ARQUIVO GERADO, não edite à mão.
   Receita: tools/identidade/paleta.py · Documento: docs/identidade-visual.md
   Regerar: python3 tools/identidade/gerar_tokens.py

   Colorimetria a serviço da programação visual: toda cor nasce em OKLCH
   (lightness perceptualmente uniforme) e vira sRGB pelo gerador. Ninguém
   escolhe hex à mão.

   Duas camadas: PRIMITIVA (a cor) e SEMÂNTICA (o papel). As telas usam SÓ a
   semântica — é isso que faz o tema claro e o escuro serem coerentes.

   Papéis dos 12 degraus (convenção Radix):
     1-2 fundo · 3-5 componente · 6-8 traço · 9-10 sólido · 11-12 texto
   Nas famílias de estado o par 9-10 sai da curva de propósito: recebe a
   lightness em que a cor PARECE a cor padrão de sinalização (âmbar a 0.64
   vira mostarda; vermelho claro demais vira rosa).

   Claro e escuro NÃO são inversão: cada um tem a sua curva de lightness e de
   croma. O escuro parte de #111112, não de preto puro, e a elevação nele é
   superfície mais clara — sombra não se enxerga sobre fundo escuro.
   ===================================================================== */

:root {{
  color-scheme: light dark;

  /* ---------- primitivas · TEMA CLARO ---------- */
{primitivas("claro", "  ")}

  /* ---------- papéis ---------- */
{semanticas("claro", "  ")}

  /* ---------- tipografia ----------
     Duas vozes, um sistema: o SISTEMA fala em monoespaçada (é um instrumento,
     e tabela de teste precisa de dígito de largura fixa); a AULA fala em sans
     (é texto para ler). */
  --fonte-instrumento: ui-monospace, "SF Mono", "JetBrains Mono", Menlo, Consolas, "Roboto Mono", monospace;
  --fonte-texto: ui-sans-serif, system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;

  /* escala de tipo — razão 1,25 ancorada em 16px */
  --t-micro:0.6875rem; --t-mini:0.75rem; --t-corpo:0.875rem; --t-base:1rem;
  --t-med:1.25rem; --t-gr:1.5rem; --t-disp:clamp(1.5rem, 1.1rem + 1.8vw, 2.25rem);
  --tr-etiqueta:0.08em;

  /* ---------- ritmo · múltiplos de 4 ---------- */
  --e-1:4px; --e-2:8px; --e-3:12px; --e-4:16px; --e-5:24px; --e-6:32px; --e-7:48px;

  /* ---------- forma ---------- */
  --r-sm:6px; --r-md:10px; --r-lg:14px; --r-full:999px;
  --traco:1px;

  /* ---------- elevação ---------- */
  --elev-1:0 1px 2px rgb(16 24 40 / .06), 0 4px 12px rgb(16 24 40 / .06);
  --elev-2:0 2px 4px rgb(16 24 40 / .07), 0 12px 32px rgb(16 24 40 / .09);
}}

/* ===================== TEMA ESCURO =====================
   Duas portas: a escolha explícita (data-theme) e a preferência do sistema. */
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
{primitivas("escuro", "    ")}
{semanticas("escuro", "    ")}
    --elev-1:0 1px 2px rgb(0 0 0 / .40), 0 4px 12px rgb(0 0 0 / .32);
    --elev-2:0 2px 4px rgb(0 0 0 / .45), 0 12px 32px rgb(0 0 0 / .40);
  }}
}}
:root[data-theme="dark"] {{
{primitivas("escuro", "  ")}
{semanticas("escuro", "  ")}
  --elev-1:0 1px 2px rgb(0 0 0 / .40), 0 4px 12px rgb(0 0 0 / .32);
  --elev-2:0 2px 4px rgb(0 0 0 / .45), 0 12px 32px rgb(0 0 0 / .40);
}}

/* ===================== o que a identidade impõe ===================== */

/* Ponto de estado com anel: garante o limite visível mesmo quando o
   preenchimento tem contraste baixo contra o fundo — o âmbar sobre fundo claro
   mede 2,0:1, e é o anel que o desenha. */
.estado-ponto {{
  width:8px; height:8px; border-radius:var(--r-full);
  box-shadow:0 0 0 1px var(--line-strong);
  display:inline-block; flex:none;
}}
.estado-ponto[data-estado="bom"]{{background:var(--good)}}
.estado-ponto[data-estado="atencao"]{{background:var(--warn)}}
.estado-ponto[data-estado="falha"]{{background:var(--bad)}}
.estado-ponto[data-estado="ocioso"]{{background:var(--n-8)}}

/* Foco sempre visível: anel de 2px com deslocamento. */
:where(a, button, input, select, textarea, [tabindex]):focus-visible {{
  outline:2px solid var(--focus); outline-offset:2px; border-radius:var(--r-sm);
}}

/* Quem pediu menos movimento, recebe menos movimento. */
@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{ animation-duration:.01ms !important; animation-iteration-count:1 !important;
    transition-duration:.01ms !important; scroll-behavior:auto !important; }}
}}
"""
open(DESTINO, "w", encoding="utf-8").write(CSS)
print(f"escrito {os.path.relpath(DESTINO, RAIZ)} — {len(CSS.splitlines())} linhas")
