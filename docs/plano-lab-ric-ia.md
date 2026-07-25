# Plano — Laboratório de RIC com IA (concluído)

> **Status: CONCLUÍDO (v0.43.0 → 0.48.0).** O plano foi executado: **8 aulas
> interativas** no painel (`/lab`), os datasets convertidos para CSV, e os **3
> casos do artigo** (UE-TP, Localization, Predictive Maintenance) reproduzidos e
> integrados como **testes no servidor** (`p2-ml-*`) **+ aulas**. Servidor já em
> **4 vCPU** (t4g.xlarge). O que segue fica como registro; só continua opcional o
> item 4 (ligar ao rApp em C) e o 5 (KNIME).

## Objetivo

Transformar o material do lab de IA (`pdfs/ric-ai/`) em um laboratório executável
de ML aplicado ao RIC — casando com a disciplina **"Aplicações de IA e ML em RIC"**
(Prof. Julio Tesolin) e com o **UE-TP-rApp** (previsão de throughput por UE), o
tema do grupo.

## O que já está pronto (não repetir)

- **Biblioteca completa, offline, ARM64**: scikit-learn 1.9.0 + numpy 2.5.0 +
  scipy 1.18.0 + joblib + threadpoolctl + narwhals — **6 wheels, 57 MB**, em
  `server/panel/vendor/wheels/` (fora do git; recriável por
  `server/panel/vendor/README.md`). **Instalado no venv automaticamente** pelo
  `infra/server-bootstrap.sh` (v0.47.0) — antes era passo manual.
- **Datasets de treino** em `pdfs/ric-ai/Base Fonts RIC/` (hoje em PDF).
- **Material didático**: `pdfs/ric-ai/MLRAN_A01.pdf` (Aula 01).
- **Pipeline de dados real**: `kpm_analytics.sh` → CSV (KPM → KPI), já pronto —
  fonte de dados *reais* quando o lab E2 rodar. Guia:
  [KPM-ANALYTICS.md](../server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md).
- **Esqueleto do rApp**: `server/oai-cn-gnb-e2/.../xapp_ue_tp_moni.c` (falta o modelo).

## Passos — executados ✅

Todos realizados (v0.43.0 → 0.48.0); registro do que foi feito em cada um:

1. **Datasets PDF → CSV.** ✅ Feito — CSVs por técnica em
   `pdfs/ric-ai/lab-didatico/<técnica>/data/` (via `parse_labels.py` + geradores).
2. **Pipeline Python starter** (`scikit-learn`), por caso de uso: carregar CSV →
   split → treinar → avaliar → comparar. ✅ Feito — cada aula treina 7–8 modelos e
   compara (RMSE/MAE/R² ou Acc/F1); os 3 casos do artigo rodam também como **testes
   no servidor** (numpy-only, `server/oai-cn-gnb-e2/scripts/ml/`, split temporal).
3. **Casos de uso ↔ dataset ↔ técnica sugerida:**

   | Caso de uso | Dataset | Alvo | Técnicas (ex.) |
   |---|---|---|---|
   | **Previsão de throughput** (UE-TP-rApp) | `traffic_prediction` | Throughput | LinearRegression vs. GradientBoosting |
   | Traffic steering | `traffic_load_prediction` | TrafficLoad | RandomForest vs. SVR |
   | Otimização de energia | `energy_prediction` | EnergyConsumption | Ridge vs. GradientBoosting |
   | Energia (boosting) | `energy_prediction_boosting` | EnergyConsumption | HistGradientBoosting (mais features) |

4. **Ligar ao rApp real**: alimentar o modelo com o CSV do `kpm_analytics.sh`
   (dados reais de KPM) além dos datasets sintéticos; conectar ao
   `xapp_ue_tp_moni.c` (EWMA hoje → modelo treinado). ⏳ **Opcional/futuro** — a
   ponte KPM→sklearn recomendada via **sidecar Python**, não porta C.
   Ver [non-rt-ric.md](non-rt-ric.md): a regressão é função de **Non-RT RIC**, o
   FlexRIC **não tem A1**, e nenhuma imagem do Non-RT RIC do O-RAN SC tem build
   ARM64 — o caminho testado é rodar local em x86_64.
5. **(Opcional) KNIME**: a disciplina usa KNIME (low-code); o mesmo fluxo pode
   ser reproduzido lá, com Python só quando necessário. ⏳ Não feito (opcional).

## Dependências / bloqueios

- **Treinar/experimentar localmente**: sem bloqueio (é CPU-leve; roda em qualquer
  máquina com as wheels).
- **Testes de ML no servidor** (`p2-ml-*`): sem bloqueio — sklearn em alguns
  milhares de linhas é CPU-leve, roda mesmo em 2 vCPU (diferente do teste KPM com
  tráfego, que satura o box).
- **Lab E2E no servidor** (UE + gNB RFSIM + coleta KPM real + inferência): depende
  de **4 vCPU** — em 2 vCPU o UE + gNB não coexistem sob o guardrail anti-freeze.
  **Destravado**: servidor já em **t4g.xlarge (4 vCPU)**. Runbook do resize:
  [POLITICA-DE-CUSTOS.md §3](POLITICA-DE-CUSTOS.md).

## Contexto da disciplina (Prof. Julio Tesolin)

- Ferramental: **KNIME + Python** (scikit-learn / pytorch / tensorflow).
- Avaliação: aplicar **2 técnicas** a **1** caso de uso; entregar relatório +
  script; prazo **01/08/26**.
- Casos de uso da ementa: traffic steering, espectro dinâmico, otimização de
  energia, manutenção preditiva, detecção de anomalias.

---

Referências: [`pdfs/ric-ai/README.md`](../pdfs/ric-ai/README.md) ·
[roadmap do README](../README.md) · [`server/panel/vendor/README.md`](../server/panel/vendor/README.md).
