# dados-telecom/ — Análise de Dados em Redes de Telecom

Material da **Disciplina 9: "Análise de Dados em Redes de Telecom"**
(Prof. Dr. **Jonas Augusto Kunzler**, `jak@cesar.school`) — 24 h em 6 encontros,
sobre o lab `oai-cn-gnb-nonrt-nearrt` do docente (caso **UE-TP / load-anomaly**),
o mesmo eixo E2/KPM do nosso `server/oai-cn-gnb-e2`.

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
| 03 | 08/08/2026 | 5h | EDA/ETL + **Checkpoint 1** | — |
| 04 | 25/08/2026 | 3h30 | KPIs/KQIs + **Checkpoint 2** | — |
| 05 | 27/08/2026 | 3h30 | Capacidade/otimização + checkpoint técnico final | — |
| 06 | 29/08/2026 | 5h | Apresentações e **defesa** | — |

Há também um **resumo oficial das aulas 01–02**
(`resumo-aula01_02-analise_dados_teleco.pdf`, 10 págs.: DIKW, fontes por camada,
5 Vs, lake × warehouse × lakehouse, NWDAF/MDAS e o checklist do checkpoint) — *a
adicionar à pasta*.

## Avaliação

- **Projeto integrador (50%)** — pipeline + KPIs + apresentação/defesa na Aula 06
  → [`projeto/`](projeto/)
- **Exercícios individuais na plataforma (30%)** — `#data/aula01` … `#data/aula06`
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

| Grupo | Tema |
|-------|------|
| G1 | Vazão do usuário |
| G2 | Anomalia de carga |
| G3 | Latência / proxy de QoE |
| G4 | Risco de congestionamento |
| G5 | Visão agregada da célula |
| G6 | Economia de energia (intenção) |
| G7 | Política de QoS / steering |

## Referências

- TRIPATHI, N. D.; SHAH, V. K. *Fundamentals of O-RAN.* Wiley-IEEE Press, 2025. (Cap. 1–2)
- WONG, I. C.; CHOPRA, A.; RAJAGOPAL, S.; JANA, R. (Eds.) *Open RAN: The Definitive Guide.* Wiley-IEEE Press, 2024. (Caps. 1–3)
- YANG, K. et al. *6G Mobile Wireless Networks.* Wiley-IEEE, 2023.
- AUDY, J. L. N.; ANDRADE, G. K.; CIDRAL, A. *Fundamentos de sistemas de informação.* Bookman. (hierarquia DIKW)
- Dataset SUTD 5G — [`FCCLab/sutd_5g_dataset_2023`](https://github.com/FCCLab/sutd_5g_dataset_2023)
  (já usado em [`../02-ric-ai/casos-artigo/`](../02-ric-ai/casos-artigo/))
