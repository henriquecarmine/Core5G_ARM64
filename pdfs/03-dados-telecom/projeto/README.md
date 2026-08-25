# projeto/ — projeto integrador (50%)

Pipeline analítico **reproduzível** sobre telemetria RAN do lab
`oai-cn-gnb-nonrt-nearrt`, conforme o
[briefing oficial](../../../external/cesar-school-repo/data/docs/briefing-projeto.md)
e os [temas por grupo](../../../external/cesar-school-repo/data/docs/temas-grupos.md).

**Grupo 6** · **Tema 1 — Vazão do usuário (UE-TP)**.
**Integrantes:** Henrique Carmine · Kelvin de Lima Gabriel · Klinger Carneiro Júnior.
**Mentor:** Prof. Dr. Jonas Augusto Kunzler (`jak@cesar.school`).
**Pergunta:** a vazão do UE sobe/desce **junto** com o uso de PRB e com o atraso?
Card do tema em [`temas-grupos.md`](../../../external/cesar-school-repo/data/docs/temas-grupos.md).

## Fonte de dados (trilha offline — a que vale nota)

Pacote oficial do docente, já disponível no submódulo:

```
external/cesar-school-repo/data/code/datasets/kpm-ue-tp-sample/
├── kpm.jsonl        # 100 amostras: baseline (20) · stress (60) · recovery (20)
├── kpm.sqlite       # o mesmo, curado
├── model.json       # MAD treinado no baseline
├── decision.json    # decisão "apply" — a política A1 em dry-run
└── db_summary.json  # contagem por fase
```

Cada linha do JSONL: `metrics` (`DRB.UEThpUl` vazão UL · `DRB.RlcSduDelayDl`
atraso DL · `RRU.PrbTotUl` uso de PRB UL), `phase`, `run_id`, `sample_index`,
`ingested_at`. Telemetria sintética RFSIM, sem dados pessoais.

## ETL — mini-lake (zonas da Aula 02)

```bash
python3 etl/build_lake.py        # raw (submódulo) → data/{bronze,silver,gold}
```

| Zona | Formato | Conteúdo |
|------|---------|----------|
| raw | JSONL (submódulo, intocado) | artefato KPM original |
| bronze | JSONL | amostras achatadas (1 linha = 1 medição) |
| silver | SQLite `kpm` | tipado, chave (`run_id`,`phase`,`sample_index`) |
| gold | JSON | agregados por fase: média/p95 das 3 métricas |

## Checkpoint 1 (25/08) — EDA · qualidade · 2 consultas · 2 plots

Reprodução: `python3 etl/build_lake.py && python3 eda_cp1.py`
(gera `data/` e `figures/`).

- **Qualidade** (`eda_cp1.py`): 100 amostras, 1 `run_id`, fases 20/60/20; **sem
  nulos, sem duplicatas** na chave, **sem gaps** no `sample_index`; `ingested_at`
  todo em **UTC (+00:00)**. Ressalva: no `recovery`, a **média** de vazão é puxada
  por poucos picos residuais — usar mediana/percentil e recorte por fase (a média
  sozinha engana).
- **Consulta 1 — agregados por fase:** baseline PRB≈2 · stress PRB≈97 ·
  recovery PRB≈3 → o salto de carga do stress é nítido nas 3 métricas.
- **Consulta 2 — a vazão anda junto com PRB e atraso? (correlação de Pearson):**
  **vazão × PRB = 0,924** · vazão × atraso = 0,484. Olhando **dentro de cada fase**,
  vazão × PRB se mantém (stress 0,98) e vazão × atraso ≈ 0 — o 0,48 global é só o
  contraste idle × carga entre fases.
- **Visualizações** (`figures/`): `cp1_serie_temporal.png` (vazão × PRB × atraso ao
  longo do experimento, faixas por fase) e `cp1_vazao_x_prb.png` (dispersão
  vazão × PRB por fase — a relação do tema).
- **Indicadores do tema** (`kpis/kpis.md`): (1) **vazão UL média/p95 por fase**
  (baseline 3,7 · stress 78 384 · recovery 8 619 — mediana **3,7**) e (2) **PRB UL
  médio por fase** (2 · 97 · 3). Conclusão: a vazão do usuário **acompanha de perto
  o uso de PRB** (rádio cheio → vazão alta).

## Entregáveis (briefing) — checklist

- [x] README com origem dos dados, reprodução e ética/licença (este arquivo)
- [x] Scripts de ETL e análise (`etl/build_lake.py`, `eda_cp1.py`)
- [x] **2 KPIs/KQIs do tema** — fórmula, unidade, granularidade (`kpis/kpis.md`)
- [x] Visualizações com insights acionáveis (`figures/` — 2 plots do CP1)
- [ ] Recomendação operacional **ou** política A1 em dry-run (CP técnico final)
- [ ] Seção de **limitações** (RFSIM × rede real, poucos UEs, viés, privacidade)
- [ ] Apresentação 20–25 min + defesa individual (Aula 06)

Escopo proporcional: limiares, estatística, regressão simples ou anomalia
básica — **sem exigência de ML sofisticado**.

## Cronograma de entregas (temas-grupos.md)

| Aula | Entrega do grupo |
|------|------------------|
| 02 — 06/08 | tema + pergunta + uso dos dados + ideia dos 2 indicadores |
| 03 — 08/08 | dados carregados, qualidade checada, primeiros gráficos/indicadores |
| 04 — 25/08 | 2 indicadores fechados (fórmula, unidade) + visualizações |
| 05 — 27/08 | análise final + recomendação/A1 simulado + limitações |
| 06 — 29/08 | apresentação e defesa |

Rubrica (5 × 2,0 pts) no [briefing](../../../external/cesar-school-repo/data/docs/briefing-projeto.md).
