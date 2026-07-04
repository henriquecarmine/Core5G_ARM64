# ric-ai/ — material do laboratório de RIC com IA

Material da disciplina **"Aplicações de IA e ML em RIC"** (Prof. **Julio Tesolin**,
`jcct@cesar.school`) e as bases de dados dos casos de uso — a fundação do lab de
RIC com Inteligência Artificial (Near-RT / Non-RT RIC), incluindo o **UE-TP-rApp**
(previsão de throughput por UE), o tema do grupo.

## Conteúdo

- **`MLRAN_A01.pdf`** — Aula 01 (135 slides): ementa + introdução/motivação
  (SON → RIC, Near-RT × Non-RT, xApp × rApp, NWDAF, "do modelo aos dados") +
  fundamentos de IA. Ferramentas: **KNIME** (low-code) + **Python**
  (`scikit-learn` / `pytorch` / `tensorflow`). Avaliação: aplicar **2 técnicas de
  ML** a um caso de uso (traffic steering, espectro dinâmico, otimização de
  energia, manutenção preditiva, detecção de anomalias) — entrega 01/08/26.
- **`Base Fonts RIC/`** — datasets de treino (tabelas horárias sintéticas) dos
  casos de uso de regressão:

  | Dataset | Features | Alvo | Caso de uso |
  |---|---|---|---|
  | `traffic_prediction` | ActiveUsers, AvgSINR, PRBUtilization | **Throughput** | **= UE-TP-rApp** |
  | `traffic_load_prediction` | + TxPower | **TrafficLoad** | traffic steering |
  | `energy_prediction` | ActiveUsers, AvgSINR, PRBUtilization | **EnergyConsumption** | energy saving |
  | `energy_prediction_boosting` | + TxPower, CellTemperature | **EnergyConsumption** | energy saving (boosting) |

## Contexto e dependências

- **Modelo**: esqueleto em `server/oai-cn-gnb-e2/.../xapp_ue_tp_moni.c`; falta o
  modelo de previsão. Wheels do **scikit-learn aarch64** já vendorizadas em
  `server/panel/vendor/` (ver `server/panel/vendor/README.md`) — alinhadas ao
  ferramental da disciplina.
- **Pipeline de dados**: `kpm_analytics.sh` → CSV (KPM → KPI) já pronto; é o
  insumo do modelo. Guia: [`KPM-ANALYTICS.md`](../../server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md).
- **Bloqueio de hardware**: rodar o lab de IA no servidor depende de **4 vCPU**
  (em 2 vCPU o UE + gNB RFSIM não coexistem sob o guardrail anti-freeze). Análise
  e runbook do resize reversível: [`POLITICA-DE-CUSTOS.md §3`](../../docs/POLITICA-DE-CUSTOS.md).

> Próximo passo natural: converter os datasets (hoje em PDF) para **CSV** e montar
> um pipeline Python starter (treino + avaliação de 2 técnicas por caso de uso).
>
> Curso base (as 6 aulas do Prof. Jonas): [`../base/`](../base/).
