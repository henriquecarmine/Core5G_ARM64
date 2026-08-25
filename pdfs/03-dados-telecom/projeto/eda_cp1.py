#!/usr/bin/env python3
"""
Checkpoint 1 (Aula 04, 25/08) - EDA do Projeto Integrador, Grupo 6.

Tema 1, Vazao do usuario (UE-TP). A pergunta: a vazao do UE sobe/desce junto
com o uso de PRB e com o atraso?

Le a zona silver montada pelo etl/build_lake.py (data/silver/kpm.sqlite) e, como
pede o briefing, imprime:
  - um relatorio de qualidade (nulos, duplicatas, timezone, gaps, fases);
  - 2 consultas (agregados por fase; correlacao vazao x PRB x atraso);
  - 2 figuras (em figures/);
  - os 2 indicadores do tema (vazao UL media/p95 por fase; PRB UL medio por fase).

Uso: python3 eda_cp1.py  (rode o etl/build_lake.py antes).
Dados: KPM sintetico (RFSIM) do lab oai-cn-gnb-nonrt-nearrt, sem dados pessoais.
Metricas: thp_ul (DRB.UEThpUl), delay_dl (DRB.RlcSduDelayDl), prb_ul
(RRU.PrbTotUl). 100 amostras, fases baseline(20)/stress(60)/recovery(20).
"""
from __future__ import annotations

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
os.makedirs(FIG, exist_ok=True)

PHASES = ["baseline", "stress", "recovery"]          # ordem cronológica do experimento
METRICS = {"thp_ul": ("Vazão UL", "kbps"),           # DRB.UEThpUl  (alvo do tema)
           "delay_dl": ("Atraso DL (RLC)", "ms"),    # DRB.RlcSduDelayDl
           "prb_ul": ("PRB UL em uso", "PRBs")}      # RRU.PrbTotUl


def carregar() -> pd.DataFrame:
    con = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM kpm", con)
    con.close()
    df["phase"] = pd.Categorical(df["phase"], categories=PHASES, ordered=True)
    return df.sort_values(["phase", "sample_index"]).reset_index(drop=True)


def qualidade(df: pd.DataFrame) -> None:
    print("== QUALIDADE DOS DADOS ==")
    print(f"  amostras: {len(df)}  |run_id(s): {df.run_id.nunique()}  "
          f"({df.run_id.iloc[0]})")
    print(f"  por fase: {dict(df.phase.value_counts().reindex(PHASES))}")
    nul = df[list(METRICS)].isna().sum().to_dict()
    print(f"  nulos por métrica: {nul}  -> {'OK, sem nulos' if sum(nul.values())==0 else 'ATENÇÃO'}")
    dup = df.duplicated(["run_id", "phase", "sample_index"]).sum()
    print(f"  duplicatas na chave (run_id,phase,sample_index): {dup}  "
          f"-> {'OK' if dup==0 else 'ATENÇÃO'}")
    off = df.ingested_at.str[-6:].unique()
    print(f"  timezone (offset de ingested_at): {list(off)}  -> tudo UTC")
    # Nota temporal: ingested_at é carimbo de ingestão em lote, não a hora da medição
    print(f"  ingested_at: {df.ingested_at.nunique()} valor(es) distinto(s) -> carimbo de "
          "ingestão em lote (UTC); a hora da medição não vem por amostra (experimento de "
          "jun/25, ver source_path). Ordem temporal = sample_index.")
    # Nota de unidade: o artefato não declara; adotamos a convenção KPM O-RAN
    print("  unidades (convenção KPM, não declaradas no artefato): "
          "thp_ul=kbps, delay_dl=ms, prb_ul=contagem de PRBs.")
    print("  gaps no sample_index por fase:")
    for ph in PHASES:
        idx = df[df.phase == ph].sample_index.to_numpy()
        faltando = sorted(set(np.arange(idx.min(), idx.max() + 1)) - set(idx))
        print(f"    {ph:<9} {idx.min()}..{idx.max()} (n={len(idx)})  "
              f"gaps: {faltando if faltando else 'nenhum'}")
    print("  sanidade (média × p95 da vazão por fase):")
    for ph in PHASES:
        s = df.loc[df.phase == ph, "thp_ul"]
        flag = " <-- média puxada por pico(s) residual(is); usar mediana/p95 e recorte por fase" \
               if s.mean() > s.median() * 3 else ""
        print(f"    {ph:<9} média={s.mean():.1f}  mediana={s.median():.1f}  p95={s.quantile(.95):.1f}{flag}")


def consultas(df: pd.DataFrame) -> None:
    con = sqlite3.connect(DB)
    print("\n== CONSULTA 1 - agregados por fase (SQL) ==")
    q1 = """SELECT phase, COUNT(*) n,
                   ROUND(AVG(thp_ul),1) thp_med,
                   ROUND(AVG(prb_ul),1) prb_med, ROUND(AVG(delay_dl),1) delay_med
            FROM kpm GROUP BY phase"""
    print(pd.read_sql_query(q1, con).set_index("phase").reindex(PHASES).to_string())
    con.close()

    print("\n== CONSULTA 2 - a vazão anda junto com PRB e atraso? (correlação de Pearson) ==")
    corr = df[["thp_ul", "prb_ul", "delay_dl"]].corr().round(3)
    print(corr.to_string())
    print(f"  -> vazão×PRB = {corr.loc['thp_ul','prb_ul']:.3f}  |"
          f"vazão×atraso = {corr.loc['thp_ul','delay_dl']:.3f}")
    # Nota metodológica: a correlação global mistura as fases; o correto é olhar
    # dentro de cada fase (evita ler contraste idle × carga como se fosse dinâmica).
    print("  correlação DENTRO de cada fase (sem misturar idle × carga):")
    for ph in PHASES:
        s = df[df.phase == ph]
        cp = s.thp_ul.corr(s.prb_ul)
        cd = s.thp_ul.corr(s.delay_dl)
        nota = "  (PRB constante nesta fase -> correlação indefinida)" if s.prb_ul.std() == 0 else ""
        print(f"    {ph:<9} vazão×PRB={cp:.3f}  vazão×atraso={cd:.3f}{nota}")
    print("  Leitura: vazão×PRB se mantém dentro do stress (~0,98) = relação real;")
    print("  vazão×atraso ~0 dentro de cada fase (o 0,48 global vem só do contraste entre fases).")


def indicadores(df: pd.DataFrame) -> dict:
    """Os 2 indicadores do Tema 1 (Vazão do usuário)."""
    g = df.groupby("phase", observed=True)
    ind = {
        "vazao_ul": {ph: {"media": round(g.get_group(ph).thp_ul.mean(), 2),
                          "p95": round(g.get_group(ph).thp_ul.quantile(.95), 2)}
                     for ph in PHASES},
        "prb_ul_medio": {ph: round(g.get_group(ph).prb_ul.mean(), 1) for ph in PHASES},
    }
    print("\n== INDICADORES DO TEMA (Grupo 6, Vazão do usuário) ==")
    print("  (1) Vazão UL média / p95 por fase (kbps):")
    for ph in PHASES:
        print(f"        {ph:<9} média={ind['vazao_ul'][ph]['media']:>10}  p95={ind['vazao_ul'][ph]['p95']:>10}")
    print("  (2) Utilização média de PRB UL por fase (PRBs):")
    for ph in PHASES:
        print(f"        {ph:<9} {ind['prb_ul_medio'][ph]}")
    return ind


def figuras(df: pd.DataFrame) -> None:
    ordem = df.reset_index(drop=True)          # já ordenado baseline→stress→recovery
    cores = {"baseline": "#dfeee0", "stress": "#f6dede", "recovery": "#dfe6f2"}

    # FIGURA 1 - série temporal das 3 métricas com faixas de fase
    fig, axs = plt.subplots(3, 1, figsize=(9, 7), sharex=True)
    for ax, (col, (lab, unit)) in zip(axs, METRICS.items()):
        ax.plot(ordem.index, ordem[col], lw=1.1, color="#2b4a66")
        for ph in PHASES:
            sub = ordem[ordem.phase == ph]
            ax.axvspan(sub.index.min() - .5, sub.index.max() + .5, color=cores[ph], zorder=0)
        ax.set_ylabel(f"{lab}\n({unit})")
        ax.grid(alpha=.25)
    for ph in PHASES:
        i0 = ordem[ordem.phase == ph].index.min()
        axs[0].text(i0, axs[0].get_ylim()[1], f" {ph}", va="top", ha="left",
                    fontsize=9, color="#555")
    axs[-1].set_xlabel("amostra (ordem do experimento)")
    fig.suptitle("Vazão do usuário × PRB × atraso ao longo do experimento - baseline → stress → recovery")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "cp1_serie_temporal.png"), dpi=150)

    # FIGURA 2 - vazão UL × PRB UL (dispersão, colorida por fase): a relação do tema
    fig, ax = plt.subplots(figsize=(7.2, 5))
    for ph, c in [("baseline", "#2e7d32"), ("stress", "#c62828"), ("recovery", "#1565c0")]:
        sub = df[df.phase == ph]
        ax.scatter(sub.prb_ul, sub.thp_ul, s=28, alpha=.7, label=ph, color=c, edgecolors="none")
    ax.set_xlabel("PRB UL em uso (PRBs)")
    ax.set_ylabel("Vazão UL (kbps)")
    ax.set_title("Vazão do usuário sobe com o uso de PRB (por fase)")
    ax.grid(alpha=.25)
    ax.legend(title="fase")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "cp1_vazao_x_prb.png"), dpi=150)
    print(f"\nFiguras salvas em {FIG}/  (cp1_serie_temporal.png, cp1_vazao_x_prb.png)")


if __name__ == "__main__":
    df = carregar()
    qualidade(df)
    consultas(df)
    indicadores(df)
    figuras(df)
