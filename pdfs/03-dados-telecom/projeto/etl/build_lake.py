#!/usr/bin/env python3
"""ETL do projeto integrador: raw (pacote KPM do docente) → bronze → silver → gold.

Zonas conforme a Aula 02 (mini-lake). Stdlib apenas — reproduzível em qualquer
Python 3.9+, sem dependências.
"""
import json
import sqlite3
import statistics
from pathlib import Path

PROJETO = Path(__file__).resolve().parent.parent
REPO = PROJETO.parents[2]
RAW = REPO / "external/cesar-school-repo/data/code/datasets/kpm-ue-tp-sample/kpm.jsonl"
DATA = PROJETO / "data"

METRICAS = ["DRB.UEThpUl", "DRB.RlcSduDelayDl", "RRU.PrbTotUl"]


def p95(valores):
    ordenados = sorted(valores)
    return ordenados[min(len(ordenados) - 1, round(0.95 * len(ordenados)) - 1)]


def main():
    if not RAW.exists():
        raise SystemExit(
            f"raw não encontrado: {RAW}\n"
            "rode: git submodule update --init external/cesar-school-repo"
        )

    # bronze — 1 linha por medição, métricas achatadas
    bronze_dir = DATA / "bronze"
    bronze_dir.mkdir(parents=True, exist_ok=True)
    linhas = []
    with open(RAW) as f:
        for ln in f:
            reg = json.loads(ln)
            linhas.append(
                {
                    "run_id": reg["run_id"],
                    "phase": reg["phase"],
                    "sample_index": reg["sample_index"],
                    "ingested_at": reg["ingested_at"],
                    **{m: reg["metrics"].get(m) for m in METRICAS},
                }
            )
    bronze = bronze_dir / "kpm.jsonl"
    with open(bronze, "w") as f:
        for linha in linhas:
            f.write(json.dumps(linha) + "\n")

    # silver — SQLite tipado
    silver_dir = DATA / "silver"
    silver_dir.mkdir(parents=True, exist_ok=True)
    db = silver_dir / "kpm.sqlite"
    con = sqlite3.connect(db)
    con.execute("DROP TABLE IF EXISTS kpm")
    con.execute(
        """CREATE TABLE kpm (
            run_id TEXT NOT NULL, phase TEXT NOT NULL, sample_index INTEGER NOT NULL,
            ingested_at TEXT, thp_ul REAL, delay_dl REAL, prb_ul REAL,
            PRIMARY KEY (run_id, phase, sample_index))"""
    )
    con.executemany(
        "INSERT INTO kpm VALUES (?,?,?,?,?,?,?)",
        [
            (
                l["run_id"], l["phase"], l["sample_index"], l["ingested_at"],
                l["DRB.UEThpUl"], l["DRB.RlcSduDelayDl"], l["RRU.PrbTotUl"],
            )
            for l in linhas
        ],
    )
    con.commit()

    # gold — agregados por fase (base dos KPIs do grupo)
    gold_dir = DATA / "gold"
    gold_dir.mkdir(parents=True, exist_ok=True)
    agregados = []
    for (run_id, phase), grupo in _por_fase(linhas).items():
        item = {"run_id": run_id, "phase": phase, "amostras": len(grupo)}
        for m in METRICAS:
            valores = [l[m] for l in grupo if l[m] is not None]
            item[m] = {
                "media": round(statistics.mean(valores), 2),
                "p95": round(p95(valores), 2),
            }
        agregados.append(item)
    gold = gold_dir / "kpis_por_fase.json"
    gold.write_text(json.dumps(agregados, indent=2) + "\n")

    con.close()
    print(f"raw    {RAW.relative_to(REPO)} ({len(linhas)} amostras)")
    print(f"bronze {bronze.relative_to(REPO)}")
    print(f"silver {db.relative_to(REPO)}")
    print(f"gold   {gold.relative_to(REPO)}")
    for a in agregados:
        metricas = "  ".join(f"{m}: μ={a[m]['media']} p95={a[m]['p95']}" for m in METRICAS)
        print(f"  {a['phase']:<9} n={a['amostras']:<3} {metricas}")


def _por_fase(linhas):
    grupos = {}
    for l in linhas:
        grupos.setdefault((l["run_id"], l["phase"]), []).append(l)
    return grupos


if __name__ == "__main__":
    main()
