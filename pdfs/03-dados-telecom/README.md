# dados-telecom/ — Análise de Dados em Redes de Telecom

Material da **Disciplina 9: "Análise de Dados em Redes de Telecom"**
(Prof. Dr. **Jonas Augusto Kunzler**, `jak@cesar.school`) — 24 h em 6 encontros,
sobre o lab `oai-cn-gnb-nonrt-nearrt` do docente (caso **UE-TP / load-anomaly**),
o mesmo eixo E2/KPM do nosso `server/oai-cn-gnb-e2`. O repositório do professor
(briefing, lab, plano de ensino) está vendorizado em
[`external/cesar-school-repo/data/`](../../external/cesar-school-repo/data/) —
ver [docs/repo-professor.md](../../docs/repo-professor.md).

Fio condutor da disciplina:

```
fonte → ingestão → armazenamento → qualidade → transformação →
indicador → análise → visualização → decisão
```

## Calendário — 6 encontros (24 h)

| Aula | Data | Duração | Conteúdo | Slides |
|------|------|---------|----------|--------|
| 01 | 04/08/2026 | 3h30 | Fontes de dados + apresentação do projeto integrador | `aula01-intro_fontes_dados_telecom-2.pdf` |
| 02 | 06/08/2026 | 3h30 | Lakes/warehouses + definição preliminar do caso | `aula02-data_lakes_big_data.pdf` |
| 03 | 08/08/2026 | 5h | EDA/ETL + **Checkpoint 1** | `aula03-eda_etl_visualizacao.pdf` |
| 04 | 25/08/2026 | 3h30 | KPIs/KQIs + **Checkpoint 2** | `aula04-kpis_kqis_qualidade.pdf` |
| 05 | 27/08/2026 | 3h30 | Capacidade/otimização + checkpoint técnico final | — |
| 06 | 29/08/2026 | 5h | Apresentações e **defesa** | — |

Há também um **resumo oficial das aulas 01–02**
(`resumo-aula01_02-analise_dados_teleco.pdf`, 10 págs.: DIKW, fontes por camada,
5 Vs, lake × warehouse × lakehouse, NWDAF/MDAS e o checklist do checkpoint) — *a
adicionar à pasta*.

## Avaliação

- **Projeto integrador (50%)** — pipeline + KPIs + apresentação/defesa na Aula 06
  → [`projeto/`](projeto/)
- **Exercícios individuais na plataforma (30%)** —
  [cesar-activities → `#data`](https://cesar-activities-cxapa2g7ia-rj.a.run.app/#data),
  fluxos `#data/aula01` … `#data/aula06` (concluir em ritmo semanal; briefing:
  [`briefing-plataforma.md`](../../external/cesar-school-repo/data/docs/briefing-plataforma.md))
  → [`trabalhos/`](trabalhos/)
- **Engajamento técnico e checkpoints (20%)** — estudos de caso, checkpoints e
  defesa individual

## Projeto integrador (resumo do briefing)

**Produto:** pipeline reprodutível sobre telemetria RAN (lab
`oai-cn-gnb-nonrt-nearrt`, caso UE-TP / load-anomaly):

```
KPM E2 → JSONL/SQLite → MAD train/evaluate → policy A1 → (emulate|real) → effect_report
```

**Entregáveis:** grupo · ETL/análise · ≥2 KPIs/KQIs · visualizações ·
recomendação ou política A1 em dry-run · limitações · apresentação + defesa.

**Progressão:** caso (A02) → Checkpoint 1 EDA (A03) → Checkpoint 2 indicadores
(A04) → checkpoint técnico (A05) → defesa (A06).

**Trilhas:** a **offline é a obrigatória** para avaliação (artefatos KPM do
docente, regeneráveis com `run_ue_tp_experiment.sh`); a **live** (`--live`, se o
lab E2 estiver no ar) é complementar e não substitui a offline.

**Rubrica (10 pts):** dados 2 · ETL/reprodutibilidade 2 · KPIs/KQIs 2 ·
análise/recomendação 2 · governança/defesa 2. Análise proporcional (limiares,
estatística, regressão simples ou anomalia básica — sem exigir ML avançado).

**Features KPM do lab:** `DRB.UEThpUl` · `DRB.RlcSduDelayDl` · `RRU.PrbTotUl`.

### Temas dos grupos / seminários (mesmos dados, perguntas diferentes)

Cada grupo desenvolve o projeto e o seminário sobre um dos 7 temas:

| Tema | Assunto | No painel |
|------|---------|-----------|
| T1 | Vazão do usuário (UE-TP) | `p2-tema-t1` |
| T2 | Anomalia de carga | `p2-tema-t2` |
| T3 | Latência / proxy de QoE | `p2-tema-t3` |
| T4 | Risco de congestionamento | `p2-tema-t4` |
| T5 | Visão agregada da célula | `p2-tema-t5` |
| T6 | Economia de energia (intenção) | `p2-tema-t6` |
| T7 | Política de QoS / steering | `p2-tema-t7` |

Atenção: o número do **grupo não é** o número do tema. A distribuição está na
planilha "Projeto Integrador: Data" do professor (ex.: **Grupo 6 = Tema 1**,
Vazão do usuário; ver [`projeto/`](projeto/)).

## No painel (Estudo 4)

A disciplina vive no painel como **Estudo 4** (rail do console, dropdown
*Análise de Dados em Redes de Telecom*): as aulas 01–03 renderizadas dos slides
(`/lab/estudo/4/aula/{1,2,3}`: objetivos, conceitos, fórmulas, "onde roda" no
mini-mapa, exercícios, quiz), o teste **`p2-kpi-qoe`** com a cadeia da aula 04
(medida → KPI → KQI → QoS → QoE proxy → anatomia dos indicadores do CP2) e
**os 7 temas do projeto integrador** como
comandos (`p2-tema-t1 … p2-tema-all`): cada um imprime a pergunta do card, as
fórmulas dos 2 indicadores, as tabelas por fase, a leitura e a recomendação como
política A1 em dry-run, sobre os mesmos dados (`kpm-ue-tp-sample`) ou sobre um
arquivo/colagem do professor. Motor: `server/oai-cn-gnb-e2/scripts/temas/`.
Doc: [`docs/estudos-por-cadeira.md`](../../docs/estudos-por-cadeira.md).

## Referências

- TRIPATHI, N. D.; SHAH, V. K. *Fundamentals of O-RAN.* Wiley-IEEE Press, 2025. (Cap. 1–2)
- WONG, I. C.; CHOPRA, A.; RAJAGOPAL, S.; JANA, R. (Eds.) *Open RAN: The Definitive Guide.* Wiley-IEEE Press, 2024. (Caps. 1–3)
- YANG, K. et al. *6G Mobile Wireless Networks.* Wiley-IEEE, 2023.
- AUDY, J. L. N.; ANDRADE, G. K.; CIDRAL, A. *Fundamentos de sistemas de informação.* Bookman. (hierarquia DIKW)
- Dataset SUTD 5G — [`FCCLab/sutd_5g_dataset_2023`](https://github.com/FCCLab/sutd_5g_dataset_2023)
  (já usado em [`../02-ric-ai/casos-artigo/`](../02-ric-ai/casos-artigo/))
