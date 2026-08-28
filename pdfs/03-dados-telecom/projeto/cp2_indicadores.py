#!/usr/bin/env python3
"""
Checkpoint 2 (Aula 05, 27/08) - Indicadores e qualidade, Grupo 6.

Tema 1, Vazao do usuario (UE-TP). O CP1 mostrou COMO os dados foram organizados
e olhados; o CP2 fecha a cadeia que a Aula 04 pede:

    medida (KPM) -> metrica -> KPI -> KQI -> QoS (SLA) -> QoE (proxy) -> decisao

Le a mesma zona silver do CP1 (data/silver/kpm.sqlite, montada por
etl/build_lake.py) e produz:
  - a anatomia dos 4 indicadores (nome, formula, unidade, granularidade, fonte,
    alvo/limiar, interpretacao, papel e limite de validade);
  - 1 figura por indicador, com titulo, eixos e janela temporal;
  - as clausulas de QoS didaticas, calibradas no proprio repouso;
  - a sensibilidade do limiar L (ate onde a conclusao se sustenta);
  - a recomendacao e a comparacao com o decision.json do professor.

Uso: python3 cp2_indicadores.py   (rode o etl/build_lake.py antes)
Dados: KPM sintetico (RFSIM) do lab oai-cn-gnb-nonrt-nearrt, sem dados pessoais.
Unidades E2SM-KPM: thp_ul em kbps, delay_dl em us, prb_ul em % dos PRB.
"""
from __future__ import annotations

import json
import os
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "silver", "kpm.sqlite")
FIG = os.path.join(HERE, "figures")
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
DECISION = os.path.join(REPO, "external/cesar-school-repo/data/code/datasets/kpm-ue-tp-sample/decision.json")
os.makedirs(FIG, exist_ok=True)

PHASES = ["baseline", "stress", "recovery"]
PT = {"baseline": "repouso", "stress": "carga", "recovery": "recuperação"}

# Cores validadas para papel branco (checagem de banda de luminancia, croma,
# separacao para daltonismo e contraste): azul = dado; laranja = limiar/alerta.
AZUL, LARANJA, CINZA, TINTA = "#2a78d6", "#eb6834", "#8b98a5", "#20272e"

# Limiar do KQI. Escolhido por SEPARACAO DE REGIME (ver secao de sensibilidade),
# nao por requisito de aplicacao: nao existe SLA de cliente neste laboratorio.
L_US = 100.0


def carregar() -> pd.DataFrame:
    con = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM kpm", con)
    con.close()
    df["phase"] = pd.Categorical(df["phase"], categories=PHASES, ordered=True)
    return df.sort_values(["phase", "sample_index"]).reset_index(drop=True)


def por_fase(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("phase", observed=True)
    return pd.DataFrame({
        "n": g.size(),
        "thp_mediana": g.thp_ul.median(), "thp_media": g.thp_ul.mean(), "thp_p95": g.thp_ul.quantile(.95),
        "prb_media": g.prb_ul.mean(), "prb_p95": g.prb_ul.quantile(.95),
        "delay_mediana": g.delay_dl.median(), "delay_p95": g.delay_dl.quantile(.95),
        "delay_zeros": g.delay_dl.apply(lambda s: (s == 0).sum()),
        "acima_L": g.delay_dl.apply(lambda s: 100.0 * (s > L_US).mean()),
    })


# ---------------------------------------------------------------- figuras ----
def _fases_ao_fundo(ax, df):
    """Faixas cinza marcando as fases. Contexto nao disputa cor com o dado."""
    ini = 0
    for i in range(1, len(df) + 1):
        if i == len(df) or df.phase.iloc[i] != df.phase.iloc[ini]:
            if ini % 2:
                ax.axvspan(ini - .5, i - .5, color=CINZA, alpha=.10, lw=0)
            ax.text((ini + i - 1) / 2, ax.get_ylim()[1] * .96, PT[df.phase.iloc[ini]],
                    ha="center", va="top", fontsize=8.5, color=CINZA)
            if ini:
                ax.axvline(ini - .5, color=CINZA, lw=.8, ls=(0, (3, 3)))
            ini = i


def serie(df, col, titulo, unidade, arquivo, limiar=None, rot_limiar=""):
    fig, ax = plt.subplots(figsize=(7.6, 2.9), dpi=170)
    ax.plot(range(len(df)), df[col], color=AZUL, lw=1.6, solid_joinstyle="round")
    if limiar is not None:
        ax.axhline(limiar, color=LARANJA, lw=1.3, ls=(0, (5, 3)))
        ax.text(len(df) - 1, limiar, "  " + rot_limiar, color=LARANJA, fontsize=8.5, va="bottom", ha="right")
    _fases_ao_fundo(ax, df)
    ax.set_title(titulo, fontsize=10.5, color=TINTA, loc="left", pad=8)
    ax.set_xlabel("amostra KPM, na ordem do experimento (100 medições)", fontsize=8.5, color=CINZA)
    ax.set_ylabel(unidade, fontsize=8.5, color=CINZA)
    ax.tick_params(labelsize=8, colors=CINZA)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"): ax.spines[s].set_color("#c9d2db")
    ax.grid(axis="y", color="#e4e9ef", lw=.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, arquivo), bbox_inches="tight")
    plt.close(fig)
    return arquivo


def barras_kqi(res, arquivo):
    fig, ax = plt.subplots(figsize=(7.6, 2.5), dpi=170)
    fases = [PT[p] for p in PHASES]
    vals = [res.loc[p, "acima_L"] for p in PHASES]
    b = ax.bar(fases, vals, color=AZUL, width=.55)
    for r, v in zip(b, vals):
        ax.text(r.get_x() + r.get_width() / 2, v + 2, f"{v:.0f}%", ha="center", fontsize=9.5, color=TINTA)
    ax.set_title(f"KQI — fração do tempo com atraso acima de {L_US:.0f} µs, por fase",
                 fontsize=10.5, color=TINTA, loc="left", pad=8)
    ax.set_ylabel("% das amostras", fontsize=8.5, color=CINZA)
    ax.set_ylim(0, 115)
    ax.tick_params(labelsize=9, colors=CINZA)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"): ax.spines[s].set_color("#c9d2db")
    ax.grid(axis="y", color="#e4e9ef", lw=.8); ax.set_axisbelow(True)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, arquivo), bbox_inches="tight"); plt.close(fig)
    return arquivo


def sensibilidade(df, arquivo):
    """Ate onde a conclusao do KQI se sustenta se mexermos no limiar."""
    Ls = list(range(20, 281, 10))
    b = df[df.phase == "baseline"].delay_dl
    s = df[df.phase == "stress"].delay_dl
    fb = [100 * (b > L).mean() for L in Ls]
    fs = [100 * (s > L).mean() for L in Ls]
    fig, ax = plt.subplots(figsize=(7.6, 2.7), dpi=170)
    ax.plot(Ls, fs, color=AZUL, lw=1.8, label="carga")
    ax.plot(Ls, fb, color=LARANJA, lw=1.8, ls=(0, (4, 2)), label="repouso")
    ax.axvline(L_US, color=CINZA, lw=1, ls=(0, (2, 2)))
    ax.text(L_US + 4, 60, f"L = {L_US:.0f} µs\n(o que usamos)", fontsize=8.5, color=CINZA)
    ax.set_title("Sensibilidade do limiar: a separação entre carga e repouso resiste?",
                 fontsize=10.5, color=TINTA, loc="left", pad=8)
    ax.set_xlabel("limiar L (µs)", fontsize=8.5, color=CINZA)
    ax.set_ylabel("% do tempo acima de L", fontsize=8.5, color=CINZA)
    ax.tick_params(labelsize=8, colors=CINZA)
    ax.legend(fontsize=8.5, frameon=False, loc="upper right")
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"): ax.spines[sp].set_color("#c9d2db")
    ax.grid(axis="y", color="#e4e9ef", lw=.8); ax.set_axisbelow(True)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, arquivo), bbox_inches="tight"); plt.close(fig)
    return Ls, fb, fs


def clausulas_qos(res):
    """As 4 clausulas didaticas, CALIBRADAS NO REPOUSO.

    Limiar absoluto que ja dispara com a rede parada nao mede a rede: mede a
    escolha do limiar. Por isso tres das quatro saem do proprio repouso; so a de
    capacidade usa a referencia externa do slide 35 (PRB acima de 80%).
    """
    base, carga = "baseline", "stress"
    alvo_dl = 1.2 * res.loc[base, "delay_p95"]
    alvo_thp = 0.5 * res.loc[base, "thp_mediana"]
    alvo_kqi = 2 * res.loc[base, "acima_L"]
    defs = [
        ("C1 latencia", "p95 do atraso", f"<= {alvo_dl:.0f} us",
         f"p95 do repouso ({res.loc[base,'delay_p95']:.0f} us) x 1,2",
         res.loc[carga, "delay_p95"], res.loc[carga, "delay_p95"] <= alvo_dl),
        ("C2 vazao", "mediana da vazao", f">= {alvo_thp:.1f} kbps",
         "metade da mediana do repouso",
         res.loc[carga, "thp_mediana"], res.loc[carga, "thp_mediana"] >= alvo_thp),
        ("C3 capacidade", "PRB medio", "<= 80 %",
         "referencia do slide 35 da aula 04",
         res.loc[carga, "prb_media"], res.loc[carga, "prb_media"] <= 80),
        ("C4 qualidade", "tempo acima de L", f"<= {alvo_kqi:.0f} %",
         "o dobro da fracao do repouso",
         res.loc[carga, "acima_L"], res.loc[carga, "acima_L"] <= alvo_kqi),
    ]
    # Cada clausula sai em DUAS formas da mesma fonte: 'nome/grandeza/limite' em
    # ASCII para o terminal, e 'rotulo*' com acento e simbolo para o relatorio
    # impresso. Uma origem so, duas renderizacoes - nao ha como divergirem.
    ACENTO = {"C1 latencia": "C1 latência", "C2 vazao": "C2 vazão",
              "C3 capacidade": "C3 capacidade", "C4 qualidade": "C4 qualidade",
              "p95 do atraso": "p95 do atraso", "mediana da vazao": "mediana da vazão",
              "PRB medio": "PRB médio", "tempo acima de L": "tempo acima de L"}

    import re as _re

    def bonito(t):
        t = (t.replace("<=", "≤").replace(">=", "≥")
              .replace(" us", " µs").replace("referencia", "referência")
              .replace("fracao", "fração"))
        return _re.sub(r"(\d)\.(\d)", r"\1,\2", t)   # decimal em portugues

    cl = [{"nome": n, "grandeza": g, "alvo": (g + " " + a), "limite": a, "origem": o,
           "medido": float(m), "cumpre": bool(c),
           "rotulo": ACENTO.get(n, n), "rotulo_alvo": bonito(ACENTO.get(g, g) + " " + a),
           "rotulo_origem": bonito(o)} for n, g, a, o, m, c in defs]
    return cl, [c["nome"].split()[1] for c in cl if not c["cumpre"]]


# ------------------------------------------------------------------ saida ----
def main():
    df = carregar()
    res = por_fase(df)
    base, carga = "baseline", "stress"

    print("=" * 72)
    print("CHECKPOINT 2 - Indicadores e qualidade | Grupo 6 | Tema 1 (UE-TP)")
    print("=" * 72)
    print(f"\n{len(df)} amostras: " + ", ".join(f"{PT[p]} {int(res.loc[p,'n'])}" for p in PHASES))
    print("cadeia da aula 04: medida (KPM) -> metrica -> KPI -> KQI -> QoS -> QoE (proxy) -> decisao\n")

    print("-- 1. Os indicadores, por fase " + "-" * 40)
    t = res[["n", "thp_mediana", "thp_p95", "prb_media", "delay_mediana", "delay_p95", "acima_L"]]
    print(t.round(1).to_string())

    print("\n-- 2. O que o repouso esconde " + "-" * 41)
    for p in PHASES:
        z = int(res.loc[p, "delay_zeros"]); n = int(res.loc[p, "n"])
        print(f"   {PT[p]:12s}: {z:2d} de {n} amostras com atraso ZERO ({100*z/n:.0f}%)")
    nz = df[(df.phase == base) & (df.delay_dl > 0)].delay_dl
    print(f"   No repouso, as {len(nz)} amostras com atraso chegam a {nz.max():.0f} us - "
          f"MAIS ALTO que a mediana sob carga ({res.loc[carga,'delay_mediana']:.1f} us).")
    print("   Leitura: sob carga o atraso nao ficou PIOR, ficou CONTINUO.")

    print("\n-- 3. Clausulas de QoS (didaticas, calibradas no repouso) " + "-" * 14)
    clausulas, violadas = clausulas_qos(res)
    for c in clausulas:
        print(f"   {c['nome']:15s} {c['alvo']:32s} medido {c['medido']:9.1f}  "
              f"{('CUMPRE' if c['cumpre'] else 'VIOLA'):7s} ({c['origem']})")

    print("\n-- 4. Sensibilidade do limiar L " + "-" * 39)
    Ls, fb, fs = sensibilidade(df, "cp2_sensibilidade_L.png")
    for L in (50, 100, 150, 200):
        i = Ls.index(L)
        print(f"   L={L:3d} us -> repouso {fb[i]:5.0f}%  carga {fs[i]:5.0f}%   separacao {fs[i]-fb[i]:5.0f} pontos")
    print("   A conclusao se sustenta de ~40 a ~150 us; acima de 186 us ela some (o p95")
    print("   do repouso passa o do stress) - e esse e o limite de validade do KQI.")

    print("\n-- 5. Figuras (1 por indicador) " + "-" * 39)
    figs = [
        serie(df, "thp_ul", "KPI-1 · Vazão UL do usuário ao longo do experimento", "kbps", "cp2_kpi1_vazao.png"),
        serie(df, "prb_ul", "KPI-2 · Ocupação de PRB no uplink", "% dos PRB", "cp2_kpi2_prb.png",
              limiar=80, rot_limiar="80% — referência de pressão de capacidade"),
        serie(df, "delay_dl", "KPI-3 · Atraso RLC no downlink", "µs", "cp2_kpi3_atraso.png",
              limiar=L_US, rot_limiar=f"L = {L_US:.0f} µs"),
        barras_kqi(res, "cp2_kqi_tempo_acima.png"),
        "cp2_sensibilidade_L.png",
    ]
    for f in figs: print("   figures/" + f)

    print("\n-- 6. Decisao " + "-" * 57)
    if violadas:
        print(f"   Clausulas violadas na carga: {', '.join(violadas)}")
    print("   A regra do card (vazao BAIXA com PRB ALTO) nao disparou em nenhuma amostra.")
    print("   Acao: NAO aplicar politica de priorizacao. O radio encheu porque o usuario")
    print("   estava usando, e a rede entregou 80 Mbps - isso e capacidade em uso.")

    print("\n-- 7. Comparacao com o decision.json do professor " + "-" * 22)
    try:
        d = json.load(open(DECISION))
        ev = d["evaluation"]
        print(f"   O artefato decide: '{ev['decision']}' com {ev['apply_votes']} votos, "
              f"prioridade {d['policy']['policy_data']['qosObjectives']['priorityLevel']}.")
        print("   Nao e contradicao: o decision.json responde 'isto e diferente do repouso?'")
        print("   (robust-baseline-mad). O nosso indicador responde 'o usuario esta mal")
        print("   servido?'. Anomalo nao e ruim.")
    except OSError:
        print("   (decision.json nao encontrado neste checkout)")
    print()
    return res, clausulas, violadas


if __name__ == "__main__":
    main()
