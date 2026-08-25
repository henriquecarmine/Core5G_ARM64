#!/usr/bin/env python3
"""
Checkpoint 1 (Aula 04 · 25/08) — Exploração dos dados (EDA) do Projeto Integrador.

Parte do mini-lake gerado por etl/build_lake.py (zona silver: data/silver/kpm.sqlite)
e produz, conforme o briefing:
  - relatório de QUALIDADE (nulos, duplicatas, timezone, gaps, fases);
  - 2 CONSULTAS (SQL sobre a zona silver);
  - 2 VISUALIZAÇÕES (figures/);
  - 2 INDICADORES PRELIMINARES (recorte do tema — provável G6: economia de energia).

Uso:  python3 eda_cp1.py     (rode etl/build_lake.py antes)
Dados: telemetria KPM sintética (RFSIM) do lab oai-cn-gnb-nonrt-nearrt; sem dados
pessoais. Métricas: thp_ul (DRB.UEThpUl), delay_dl (DRB.RlcSduDelayDl),
prb_ul (RRU.PrbTotUl). 100 amostras, fases baseline(20)/stress(60)/recovery(20).
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
METRICS = {"thp_ul": ("Vazão UL", "kbps"),           # DRB.UEThpUl
           "delay_dl": ("Atraso DL (RLC)", "ms"),    # DRB.RlcSduDelayDl
           "prb_ul": ("PRB UL em uso", "PRBs")}      # RRU.PrbTotUl
PRB_BAIXA = 10.0   # limiar de "baixa carga": baseline/recovery ~2-3 PRB, stress ~97 → 10 separa com folga


def carregar() -> pd.DataFrame:
    con = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM kpm", con)
    con.close()
    df["phase"] = pd.Categorical(df["phase"], categories=PHASES, ordered=True)
    return df.sort_values(["phase", "sample_index"]).reset_index(drop=True)


def qualidade(df: pd.DataFrame) -> None:
    print("== QUALIDADE DOS DADOS ==")
    print(f"  amostras: {len(df)}  ·  run_id(s): {df.run_id.nunique()}  "
          f"({df.run_id.iloc[0]})")
    print(f"  por fase: {dict(df.phase.value_counts().reindex(PHASES))}")
    # nulos
    nul = df[list(METRICS)].isna().sum().to_dict()
    print(f"  nulos por métrica: {nul}  -> {'OK, sem nulos' if sum(nul.values())==0 else 'ATENÇÃO'}")
    # duplicatas na chave
    dup = df.duplicated(["run_id", "phase", "sample_index"]).sum()
    print(f"  duplicatas na chave (run_id,phase,sample_index): {dup}  "
          f"-> {'OK' if dup==0 else 'ATENÇÃO'}")
    # timezone
    off = df.ingested_at.str[-6:].unique()
    print(f"  timezone (offset de ingested_at): {list(off)}  -> tudo UTC" )
    # gaps no sample_index por fase
    print("  gaps no sample_index por fase:")
    for ph in PHASES:
        idx = df[df.phase == ph].sample_index.to_numpy()
        esperado = np.arange(idx.min(), idx.max() + 1)
        faltando = sorted(set(esperado) - set(idx))
        print(f"    {ph:<9} {idx.min()}..{idx.max()} (n={len(idx)})  "
              f"gaps: {faltando if faltando else 'nenhum'}")
    # sanidade de valores (a "anomalia" do recovery: média >> p95 = distribuição torta)
    print("  sanidade de valores (média × p95 da vazão por fase):")
    for ph in PHASES:
        s = df.loc[df.phase == ph, "thp_ul"]
        flag = " <-- média >> p95 (distribuição assimétrica: poucos picos altos)" \
               if s.mean() > s.quantile(.95) * 1.5 else ""
        print(f"    {ph:<9} média={s.mean():.1f}  p95={s.quantile(.95):.1f}{flag}")


def consultas(df: pd.DataFrame) -> None:
    con = sqlite3.connect(DB)
    print("\n== CONSULTA 1 — agregados por fase (SQL) ==")
    q1 = """SELECT phase, COUNT(*) n,
                   ROUND(AVG(thp_ul),1) thp_med, ROUND(AVG(delay_dl),1) delay_med,
                   ROUND(AVG(prb_ul),1) prb_med
            FROM kpm GROUP BY phase"""
    print(pd.read_sql_query(q1, con).set_index("phase").reindex(PHASES).to_string())

    print("\n== CONSULTA 2 — janelas de BAIXA CARGA (prb_ul <= %g) por fase (SQL) ==" % PRB_BAIXA)
    q2 = f"""SELECT phase, COUNT(*) n,
                    SUM(CASE WHEN prb_ul <= {PRB_BAIXA} THEN 1 ELSE 0 END) baixa_carga,
                    ROUND(100.0*SUM(CASE WHEN prb_ul <= {PRB_BAIXA} THEN 1 ELSE 0 END)/COUNT(*),1) pct_baixa
             FROM kpm GROUP BY phase"""
    print(pd.read_sql_query(q2, con).set_index("phase").reindex(PHASES).to_string())
    con.close()


def indicadores(df: pd.DataFrame) -> dict:
    """2 indicadores preliminares — recorte do tema (provável G6: economia de energia)."""
    baixa = df["prb_ul"] <= PRB_BAIXA
    ind = {
        "frac_baixa_carga_pct": round(100.0 * baixa.mean(), 1),
        "thp_media_baixa_carga_kbps": round(df.loc[baixa, "thp_ul"].mean(), 2),
        "delay_medio_baixa_carga_ms": round(df.loc[baixa, "delay_dl"].mean(), 1),
        "limiar_prb": PRB_BAIXA,
    }
    print("\n== INDICADORES PRELIMINARES (recorte G6 · economia de energia) ==")
    print(f"  (1) Fração do tempo em baixa carga (prb_ul <= {PRB_BAIXA}): "
          f"{ind['frac_baixa_carga_pct']}% das amostras")
    print(f"  (2) Nessas janelas — vazão média: {ind['thp_media_baixa_carga_kbps']} kbps · "
          f"atraso médio: {ind['delay_medio_baixa_carga_ms']} ms")
    return ind


def figuras(df: pd.DataFrame) -> None:
    ordem = df.reset_index(drop=True)          # já ordenado baseline→stress→recovery
    bordas = ordem.groupby("phase", observed=True).apply(lambda g: g.index.min()).reindex(PHASES)
    cores = {"baseline": "#dfeee0", "stress": "#f6dede", "recovery": "#dfe6f2"}

    # FIGURA 1 — série temporal das 3 métricas com faixas de fase
    fig, axs = plt.subplots(3, 1, figsize=(9, 7), sharex=True)
    for ax, (col, (lab, unit)) in zip(axs, METRICS.items()):
        ax.plot(ordem.index, ordem[col], lw=1.1, color="#2b4a66")
        for ph in PHASES:                       # faixas coloridas por fase
            sub = ordem[ordem.phase == ph]
            ax.axvspan(sub.index.min() - .5, sub.index.max() + .5,
                       color=cores[ph], zorder=0)
        ax.set_ylabel(f"{lab}\n({unit})")
        ax.grid(alpha=.25)
    for ph in PHASES:
        axs[0].text(df.reset_index().groupby("phase", observed=True).groups[ph].to_numpy().mean() if False
                    else bordas[ph], axs[0].get_ylim()[1], f" {ph}",
                    va="top", ha="left", fontsize=9, color="#555")
    axs[-1].set_xlabel("amostra (ordem do experimento)")
    fig.suptitle("Telemetria KPM ao longo do experimento — baseline → stress → recovery")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "cp1_serie_temporal.png"), dpi=150)

    # FIGURA 2 — distribuição por fase (boxplot) das 3 métricas
    fig, axs = plt.subplots(1, 3, figsize=(11, 4))
    for ax, (col, (lab, unit)) in zip(axs, METRICS.items()):
        ax.boxplot([df.loc[df.phase == ph, col] for ph in PHASES],
                   tick_labels=PHASES, showfliers=True)
        ax.set_title(lab)
        ax.set_ylabel(unit)
        ax.grid(alpha=.25, axis="y")
    fig.suptitle("Distribuição das métricas por fase (o salto de carga fica evidente)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "cp1_dist_por_fase.png"), dpi=150)
    print(f"\nFiguras salvas em {FIG}/  (cp1_serie_temporal.png, cp1_dist_por_fase.png)")


if __name__ == "__main__":
    df = carregar()
    qualidade(df)
    consultas(df)
    indicadores(df)
    figuras(df)
