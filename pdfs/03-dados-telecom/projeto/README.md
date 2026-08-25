# projeto/ - Projeto Integrador (Grupo 6)

Nosso pipeline de análise sobre a telemetria RAN do lab
`oai-cn-gnb-nonrt-nearrt`, seguindo o
[briefing](../../../external/cesar-school-repo/data/docs/briefing-projeto.md) e a
distribuição de [temas por grupo](../../../external/cesar-school-repo/data/docs/temas-grupos.md).

Grupo 6, Tema 1 (Vazão do usuário / UE-TP). Integrantes: Henrique Carmine,
Kelvin de Lima Gabriel e Klinger Carneiro Júnior. Mentor: Prof. Dr. Jonas
Augusto Kunzler (jak@cesar.school).

A pergunta que a gente quer responder: a vazão do UE sobe e desce junto com o
uso de PRB e com o atraso? O card do tema está em
[temas-grupos.md](../../../external/cesar-school-repo/data/docs/temas-grupos.md).

## De onde vêm os dados

Usamos a trilha offline do professor (a que vale nota), que já vem no submódulo:

```
external/cesar-school-repo/data/code/datasets/kpm-ue-tp-sample/
├── kpm.jsonl        # 100 amostras: baseline (20), stress (60), recovery (20)
├── kpm.sqlite       # o mesmo, já curado
├── model.json       # MAD treinado no baseline
├── decision.json    # decisão "apply", a política A1 em dry-run
└── db_summary.json  # contagem por fase
```

Cada linha do JSONL traz `metrics` (`DRB.UEThpUl` = vazão UL, `DRB.RlcSduDelayDl`
= atraso DL e `RRU.PrbTotUl` = uso de PRB UL), mais `phase`, `run_id`,
`sample_index` e `ingested_at`. É telemetria sintética de RFSIM, então não tem
nenhum dado pessoal.

## ETL (mini-lake, as zonas da Aula 02)

```bash
python3 etl/build_lake.py        # raw (submódulo) -> data/{bronze,silver,gold}
```

| Zona | Formato | Conteúdo |
|------|---------|----------|
| raw | JSONL (submódulo, intocado) | artefato KPM original |
| bronze | JSONL | amostras achatadas (1 linha = 1 medição) |
| silver | SQLite `kpm` | tipado, chave (`run_id`,`phase`,`sample_index`) |
| gold | JSON | agregados por fase: média e p95 das 3 métricas |

## Checkpoint 1 (25/08): EDA, qualidade, 2 consultas, 2 gráficos

Para reproduzir: `python3 etl/build_lake.py && python3 eda_cp1.py` (gera `data/`
e `figures/`).

Qualidade (roda no `eda_cp1.py`): as 100 amostras têm 1 só `run_id`, fases
20/60/20, nenhum nulo, nenhuma duplicata na chave e nenhum gap no `sample_index`.
O `ingested_at` está todo em UTC. A única ressalva é o recovery: a média de vazão
fica puxada por uns poucos picos residuais, então usamos mediana e percentil e
olhamos por fase (a média sozinha engana).

As duas consultas em SQL:

1. Agregados por fase. Dá baseline PRB ≈ 2, stress PRB ≈ 97, recovery PRB ≈ 3,
   ou seja, o salto de carga do stress aparece claro nas três métricas.
2. A vazão anda junto com PRB e atraso? Correlação de Pearson global dá vazão ×
   PRB = 0,924 e vazão × atraso = 0,484. Só que, olhando dentro de cada fase, a
   de PRB se mantém (0,98 no stress) e a de atraso cai pra perto de zero. Ou
   seja, aquele 0,48 é só o contraste idle × carga entre as fases.

Os gráficos ficam em `figures/`: `cp1_serie_temporal.png` (as 3 métricas ao
longo do experimento, com faixas por fase) e `cp1_vazao_x_prb.png` (a dispersão
vazão × PRB por fase, que é a relação do nosso tema).

Os dois indicadores estão em `kpis/kpis.md`: vazão UL média e p95 por fase
(baseline 3,7, stress 78 384, recovery 8 619 mas mediana 3,7) e PRB UL médio por
fase (2, 97, 3). No fim, a vazão do usuário acompanha de perto o uso de PRB
(rádio cheio, vazão alta).

## Entregáveis do briefing

- [x] README com origem dos dados, reprodução e ética/licença (este arquivo)
- [x] Scripts de ETL e análise (`etl/build_lake.py`, `eda_cp1.py`)
- [x] 2 KPIs/KQIs do tema com fórmula, unidade e granularidade (`kpis/kpis.md`)
- [x] Visualizações com insight (`figures/`, os 2 gráficos do CP1)
- [ ] Recomendação operacional ou política A1 em dry-run (fecha no CP final)
- [ ] Seção de limitações (RFSIM x rede real, poucos UEs, viés, privacidade)
- [ ] Apresentação de 20-25 min + defesa individual (Aula 06)

O escopo é proporcional: limiares, estatística, regressão simples ou anomalia
básica. Não precisa de ML sofisticado.

## Cronograma das entregas (temas-grupos.md)

| Aula | Entrega do grupo |
|------|------------------|
| 02 (06/08) | tema + pergunta + uso dos dados + ideia dos 2 indicadores |
| 03 (08/08) | dados carregados, qualidade checada, primeiros gráficos |
| 04 (25/08) | 2 indicadores fechados (fórmula, unidade) + visualizações |
| 05 (27/08) | análise final + recomendação/A1 simulado + limitações |
| 06 (29/08) | apresentação e defesa |

A rubrica (5 × 2,0 pts) está no
[briefing](../../../external/cesar-school-repo/data/docs/briefing-projeto.md).
