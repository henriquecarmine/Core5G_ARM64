# -*- coding: utf-8 -*-
"""Gera server/panel/static/tokens.css a partir das escalas OKLCH.

Duas camadas, como manda a prática de design system:
  PRIMITIVA  --n-1..12, --a-*, --g-*, --w-*, --r-*   (a cor em si)
  SEMÂNTICA  --surface, --ink, --line, --accent...   (o PAPEL da cor)
A tela usa só a semântica. Trocar de tema troca a primitiva por baixo.
"""
import json, math, textwrap

E = json.load(open("/tmp/claude-1000/-home-henriquecarmine-Projetos-Core5G-ARM64/b971934c-422c-4ac5-81d0-c9f7cd1c0920/scratchpad/id/escalas.json"))
S = json.load(open("/tmp/claude-1000/-home-henriquecarmine-Projetos-Core5G-ARM64/b971934c-422c-4ac5-81d0-c9f7cd1c0920/scratchpad/id/solidos.json"))

# os sólidos afinados entram no degrau 9 de cada família
for tema, chave in (("claro","CLARO"), ("escuro","ESCURO")):
    for fam in ("a","g","w","r"):
        E[tema][fam][8] = S[chave][fam]

NOMES = {"n":"neutro","a":"acento","g":"bom","w":"atenção","r":"falha"}

def primitivas(tema, ind="  "):
    out=[]
    for fam, cores in E[tema].items():
        out.append(f"{ind}/* {NOMES[fam]} */")
        out.append(ind + " ".join(f"--{fam}-{i+1}:{c};" for i,c in enumerate(cores)))
    return "\n".join(out)

# ---- papéis. O degrau muda por tema onde a medição exigiu (ver identidade).
def semanticas(tema, ind="  "):
    # linha forte: 9 no claro (3,36:1) e 8 no escuro (3,12:1) — o degrau 8 do
    # claro mede 1,94:1 e não serve de limite de componente.
    forte = 9 if tema=="claro" else 8
    p = f"""
{ind}/* superfícies — do fundo da página ao painel elevado */
{ind}--surface:var(--n-1); --surface-2:var(--n-2); --surface-3:var(--n-3);
{ind}--surface-inset:var(--n-{2 if tema=='claro' else 1});
{ind}/* traços */
{ind}--line:var(--n-6); --line-2:var(--n-7); --line-strong:var(--n-{forte});
{ind}/* tinta */
{ind}--ink:var(--n-12); --ink-2:var(--n-11); --ink-3:var(--n-9);
{ind}/* acento — a cor do produto: foco, seleção, ação principal, link */
{ind}--accent:var(--a-9); --accent-hover:var(--a-10);
{ind}--accent-ink:{'#ffffff' if tema=='claro' else '#0d0d14'};
{ind}--accent-text:var(--a-11); --accent-soft:var(--a-3); --accent-line:var(--a-7);
{ind}/* estado — ISO. NUNCA sozinho: sempre com glifo e palavra. */
{ind}--good:var(--g-9); --good-text:var(--g-11); --good-soft:var(--g-3);
{ind}--warn:var(--w-9); --warn-text:var(--w-11); --warn-soft:var(--w-3);
{ind}--bad:var(--r-9);  --bad-text:var(--r-11);  --bad-soft:var(--r-3);
{ind}/* foco visível — obrigatório, e nunca só por cor */
{ind}--focus:var(--a-9);"""
    return p.strip("\n")

CSS = f"""/* =====================================================================
   Core5G_ARM64 — identidade visual.  ARQUIVO GERADO, não edite à mão:
   a receita está em docs/identidade-visual.md e o gerador imprime as
   escalas em OKLCH (lightness perceptualmente uniforme) e converte p/ sRGB.

   Duas camadas: PRIMITIVA (a cor) e SEMÂNTICA (o papel). As telas usam
   SÓ a semântica — é isso que faz o tema claro e o escuro serem coerentes
   em vez de duas pinturas independentes.

   Papéis dos 12 degraus (convenção Radix, verificada por medição):
     1-2 fundo · 3-5 fundo de componente · 6-8 traço · 9-10 sólido · 11-12 texto

   O claro e o escuro NÃO são inversão um do outro: cada um tem a sua curva
   de lightness e de croma. O escuro parte de #111112, não de preto puro.
   ===================================================================== */

:root {{
  color-scheme: light dark;

  /* ---------- primitivas · TEMA CLARO ---------- */
{primitivas("claro")}

  /* ---------- papéis ---------- */
{semanticas("claro")}

  /* ---------- tipografia ----------
     Duas vozes, um sistema: o SISTEMA fala em monoespaçada (é um
     instrumento; e tabela de teste precisa de dígito de largura fixa);
     a AULA fala em sans (é texto para ler). */
  --fonte-instrumento: ui-monospace, "SF Mono", "JetBrains Mono", Menlo, Consolas, "Roboto Mono", monospace;
  --fonte-texto: ui-sans-serif, system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;

  /* escala de tipo — razão 1.25, ancorada em 16px */
  --t-micro:0.6875rem; --t-mini:0.75rem; --t-corpo:0.875rem; --t-base:1rem;
  --t-med:1.25rem; --t-gr:1.5rem; --t-disp:clamp(1.5rem, 1.1rem + 1.8vw, 2.25rem);
  --tr-etiqueta:0.08em;   /* entreletra das etiquetas em caixa alta */

  /* ---------- ritmo · múltiplos de 4 ---------- */
  --e-1:4px; --e-2:8px; --e-3:12px; --e-4:16px; --e-5:24px; --e-6:32px; --e-7:48px;

  /* ---------- forma ---------- */
  --r-sm:6px; --r-md:10px; --r-lg:14px; --r-full:999px;
  --traco:1px;

  /* ---------- elevação ----------
     No claro a elevação é sombra; no escuro é SUPERFÍCIE MAIS CLARA
     (sombra não se enxerga sobre fundo escuro). */
  --elev-1:0 1px 2px rgb(16 24 40 / .06), 0 4px 12px rgb(16 24 40 / .06);
  --elev-2:0 2px 4px rgb(16 24 40 / .07), 0 12px 32px rgb(16 24 40 / .09);
}}

/* ===================== TEMA ESCURO =====================
   Só as primitivas e os poucos papéis que mudam de degrau são redefinidos;
   os nomes semânticos continuam iguais. Duas portas: a escolha explícita
   (data-theme) e a preferência do sistema. */
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
{primitivas("escuro","    ")}
{semanticas("escuro","    ")}
    --elev-1:0 1px 2px rgb(0 0 0 / .40), 0 4px 12px rgb(0 0 0 / .32);
    --elev-2:0 2px 4px rgb(0 0 0 / .45), 0 12px 32px rgb(0 0 0 / .40);
  }}
}}
:root[data-theme="dark"] {{
{primitivas("escuro","  ")}
{semanticas("escuro","  ")}
  --elev-1:0 1px 2px rgb(0 0 0 / .40), 0 4px 12px rgb(0 0 0 / .32);
  --elev-2:0 2px 4px rgb(0 0 0 / .45), 0 12px 32px rgb(0 0 0 / .40);
}}

/* ===================== regras que a identidade impõe ===================== */

/* Estado NUNCA por cor sozinha: o ponto de estado leva anel, e o componente
   que o usa leva glifo e palavra. Sob protanopia o par verde/âmbar mede 7,3
   — abaixo do alvo 8 —, e é o reforço que torna a leitura segura. */
.estado-ponto {{
  width:8px; height:8px; border-radius:var(--r-full);
  box-shadow:0 0 0 1px var(--line-strong);   /* garante o limite mesmo com fundo de baixo contraste */
  display:inline-block; flex:none;
}}
.estado-ponto[data-estado="bom"]{{background:var(--good)}}
.estado-ponto[data-estado="atencao"]{{background:var(--warn)}}
.estado-ponto[data-estado="falha"]{{background:var(--bad)}}
.estado-ponto[data-estado="ocioso"]{{background:var(--n-8)}}

/* Foco sempre visível, e não só por cor: anel com deslocamento. */
:where(a, button, input, select, textarea, [tabindex]):focus-visible {{
  outline:2px solid var(--focus); outline-offset:2px; border-radius:var(--r-sm);
}}

/* Quem pediu menos movimento, recebe menos movimento. */
@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{ animation-duration:.01ms !important; animation-iteration-count:1 !important;
    transition-duration:.01ms !important; scroll-behavior:auto !important; }}
}}
"""
d="/home/henriquecarmine/Projetos/Core5G_ARM64/server/panel/static/tokens.css"
open(d,"w",encoding="utf-8").write(CSS)
print(f"escrito {d} — {len(CSS.splitlines())} linhas")
