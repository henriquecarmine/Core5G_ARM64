# projeto/ — projeto integrador (50%)

Pipeline analítico **reproduzível** sobre telemetria RAN do lab
`oai-cn-gnb-nonrt-nearrt`, conforme o
[briefing oficial](../../../external/cesar-school-repo/data/docs/briefing-projeto.md)
e os [temas por grupo](../../../external/cesar-school-repo/data/docs/temas-grupos.md).

**Tema do grupo:** _a declarar_ (G1–G7 — o código deve constar neste README,
exigência do briefing).

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

## Entregáveis (briefing) — checklist

- [ ] README com origem dos dados, reprodução e ética/licença (este arquivo)
- [ ] Scripts de ETL e análise (`etl/`)
- [ ] **≥ 2 KPIs/KQIs formais** — fórmula, granularidade, fonte (`kpis/kpis.md`)
- [ ] Visualizações com insights acionáveis (`figures/`)
- [ ] Recomendação operacional **ou** política A1 em dry-run
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
