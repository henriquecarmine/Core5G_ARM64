# ric-ai/ — material do laboratório de RIC com IA

Material da disciplina **"Aplicações de IA e ML em RIC"** (Prof. **Julio Tesolin**,
`jcct@cesar.school`) e as bases de dados dos casos de uso — a fundação do lab de
RIC com Inteligência Artificial (Near-RT / Non-RT RIC), incluindo o **UE-TP-rApp**
(previsão de throughput por UE), o tema do grupo.

## Conteúdo

### Aulas — `MLRAN_A0x.pdf`

| Aula | Slides | Conteúdo |
|---|---|---|
| **`MLRAN_A01.pdf`** | 135 | Ementa + introdução/motivação (SON → RIC, Near-RT × Non-RT, xApp × rApp, NWDAF, "do modelo aos dados") + fundamentos de IA. Ferramentas: **KNIME** (low-code) + **Python** (`scikit-learn` / `pytorch` / `tensorflow`). |
| **`MLRAN_A02.pdf`** | 98 | Revisão + **Aprendizado supervisionado**: Regressão e Classificação. |
| **`MLRAN_A03.pdf`** | 155 | **Proposta do Projeto Final** + Classificação + **Aprendizado não supervisionado**. |

Avaliação da disciplina: aplicar **2 técnicas de ML** a um caso de uso (traffic
steering, espectro dinâmico, otimização de energia, manutenção preditiva,
detecção de anomalias) — entrega **01/08/26**.

**Projeto final (A03):** reproduzir na prática um caso de uso do artigo *"RAN
Intelligent Controller (RIC): From open-source implementation to real-world
validation"* ([ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2405959524000067)) —
casos sorteados: **Localization**, **UE-TP** (previsão de throughput por UE) e
**Predictive Maintenance**. Dados brutos abertos:
[`FCCLab/sutd_5g_dataset_2023`](https://github.com/FCCLab/sutd_5g_dataset_2023/tree/dataset/dataset).

### Reproduções dos casos de uso — [`casos-artigo/`](casos-artigo/)

Reproduções abertas, em Python/scikit-learn, dos casos de uso do artigo de
referência sobre os dados reais do SUTD: **Localization** (Tabela 3) e
**Predictive Maintenance** (Tabela 7), cada um com experimento autocontido,
métricas, figuras e análise comparativa artigo × reprodução — incluindo a
pegadinha *instance × sequence* e os cuidados de vazamento/split temporal.
(O caso UE-TP tem o lab interativo no painel em `/lab/regressao`.)

### Lab interativo no painel — aulas + testes ao vivo

O material virou **produto interativo** no painel Core5G (`/lab`): **8 aulas**
(Fundamentos, Regressão = UE-TP, Classificação, **Localização**, **Manutenção
preditiva**, Clustering, Anomalia, PCA) + **Projeto final** (`/lab/projeto`). Cada
aula tem previsão ao vivo em JS, passo a passo, gerador de relatório e a seção
**"Os modelos, um a um"** (detalhamento de cada algoritmo — como funciona · como
usa os dados · como calcula — 16 algoritmos, 4 idiomas). As aulas de Localização e
Manutenção rodam sobre os **dados reais do SUTD** (split temporal 70:30).

Os 3 casos também rodam como **testes no servidor** (console do painel, Projeto 2):
`IA · Prever throughput (UE-TP)`, `IA · Localizar andar` e `IA · Detectar RRU
perdida` executam o experimento scikit-learn no EC2 e streamam as métricas ao vivo
(experimentos numpy-only em [`server/oai-cn-gnb-e2/scripts/ml/`](../../server/oai-cn-gnb-e2/scripts/ml/)).

### Datasets — `Base Fonts RIC/`

Tabelas sintéticas de KPIs de célula (RSRP/RSRQ/SINR, PRB, usuários ativos,
throughput, energia…), organizadas por técnica de ML.

**Regressão (supervisionado):**

| Dataset | Features | Alvo | Caso de uso |
|---|---|---|---|
| `traffic_prediction` | ActiveUsers, AvgSINR, PRBUtilization | **Throughput** | **= UE-TP-rApp** |
| `traffic_load_prediction` | + TxPower | **TrafficLoad** | traffic steering |
| `energy_prediction` | ActiveUsers, AvgSINR, PRBUtilization | **EnergyConsumption** | energy saving |
| `energy_prediction_boosting` | + TxPower, CellTemperature | **EnergyConsumption** | energy saving (boosting) |

**Classificação (supervisionado):**

| Dataset | Técnica | Features | Uso |
|---|---|---|---|
| `cell_congestion_tree` | Árvore de decisão | ActiveUsers, PRBUtilization, AvgSINR, TxPower, PacketLoss, SchedulingDelay | congestão de célula |
| `cell_failure_logistic` | Regressão logística | + CellTemperature | falha de célula (manut. preditiva) |
| `kNN_Practice_100rows` | k-NN | PRB_Usage, Active_Users, Throughput, SINR, RSRQ | estado da célula |
| `naivebayes_practice` | Naive Bayes | PRB_Usage, Active_Users, Throughput, SINR, RSRQ | estado da célula |
| `svm_interference_dataset` | SVM | RSRP, RSRQ, SINR, PRB_Usage, Active_Users | detecção de interferência (dataset maior) |

**Não supervisionado** — todos com as mesmas features
(Throughput_Mbps, Latency_ms, PRB_Utilization, Active_Users, Energy_Consumption_W):

| Dataset | Técnica | Caso de uso |
|---|---|---|
| `kmeans_practice` | k-means | segmentação/perfilamento de células |
| `dbscan_practive` | DBSCAN *(nome do arquivo grafado "practive")* | clustering por densidade |
| `aggclustering_practice` | Clustering hierárquico (aglomerativo) | agrupamento de células |
| `isolationforest_practice` | Isolation Forest | detecção de anomalia |
| `pca_practice` | PCA | redução de dimensionalidade |

## Contexto e dependências

- **Modelo**: esqueleto em `server/oai-cn-gnb-e2/.../xapp_ue_tp_moni.c`; falta o
  modelo de previsão. Wheels do **scikit-learn aarch64** já vendorizadas em
  `server/panel/vendor/` (ver `server/panel/vendor/README.md`) — alinhadas ao
  ferramental da disciplina. Os 3 casos já rodam como **testes de ML** no painel
  (`p2-ml-*`): experimentos numpy-only em `server/oai-cn-gnb-e2/scripts/ml/`, com o
  scikit-learn instalado no venv pelo `infra/server-bootstrap.sh`.
- **Pipeline de dados**: `kpm_analytics.sh` → CSV (KPM → KPI) já pronto; é o
  insumo do modelo. Guia: [`KPM-ANALYTICS.md`](../../server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md).
- **Bloqueio de hardware**: rodar o lab de IA no servidor depende de **4 vCPU**
  (em 2 vCPU o UE + gNB RFSIM não coexistem sob o guardrail anti-freeze). Análise
  e runbook do resize reversível: [`POLITICA-DE-CUSTOS.md §3`](../../docs/POLITICA-DE-CUSTOS.md).

> **Feito (v0.43.0 → 0.48.0):** datasets convertidos para CSV, **8 aulas
> interativas** no painel, e os 3 casos do artigo reproduzidos e integrados como
> **testes no servidor + aulas**. Plano original:
> [`docs/plano-lab-ric-ia.md`](../../docs/plano-lab-ric-ia.md).
>
> Curso base (as 6 aulas do Prof. Jonas): [`../base/`](../base/).
