# Plano — Laboratório de RIC com IA (passo futuro)

> **Status: PLANEJADO** (marcador de próximo passo). O ferramental já está pronto;
> falta executar. Disparar quando houver sinal — e, para rodar no servidor, o
> upgrade para **4 vCPU** (ver [POLITICA-DE-CUSTOS.md §3](POLITICA-DE-CUSTOS.md)).

## Objetivo

Transformar o material do lab de IA (`pdfs/ric-ai/`) em um laboratório executável
de ML aplicado ao RIC — casando com a disciplina **"Aplicações de IA e ML em RIC"**
(Prof. Julio Tesolin) e com o **UE-TP-rApp** (previsão de throughput por UE), o
tema do grupo.

## O que já está pronto (não repetir)

- **Biblioteca completa, offline, ARM64**: scikit-learn 1.9.0 + numpy 2.5.0 +
  scipy 1.18.0 + joblib + threadpoolctl + narwhals — **6 wheels, 57 MB**, em
  `server/panel/vendor/wheels/` (fora do git; recriável por
  `server/panel/vendor/README.md`). Instalar sem internet:
  `pip install --no-index --find-links server/panel/vendor/wheels/ scikit-learn`.
- **Datasets de treino** em `pdfs/ric-ai/Base Fonts RIC/` (hoje em PDF).
- **Material didático**: `pdfs/ric-ai/MLRAN_A01.pdf` (Aula 01).
- **Pipeline de dados real**: `kpm_analytics.sh` → CSV (KPM → KPI), já pronto —
  fonte de dados *reais* quando o lab E2 rodar. Guia:
  [KPM-ANALYTICS.md](../server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md).
- **Esqueleto do rApp**: `server/oai-cn-gnb-e2/.../xapp_ue_tp_moni.c` (falta o modelo).

## Passos (a executar)

1. **Datasets PDF → CSV.** Converter as 4 tabelas de `Base Fonts RIC/` para CSV
   limpo (`pandas`-ready). Guardar em `pdfs/ric-ai/datasets/` (ou similar).
2. **Pipeline Python starter** (`scikit-learn`), por caso de uso: carregar CSV →
   split treino/teste → treinar **2 técnicas distintas** → avaliar (MAE/RMSE/R²) →
   comparar. Atende a avaliação da disciplina (2 técnicas por caso de uso).
3. **Casos de uso ↔ dataset ↔ técnica sugerida:**

   | Caso de uso | Dataset | Alvo | Técnicas (ex.) |
   |---|---|---|---|
   | **Previsão de throughput** (UE-TP-rApp) | `traffic_prediction` | Throughput | LinearRegression vs. GradientBoosting |
   | Traffic steering | `traffic_load_prediction` | TrafficLoad | RandomForest vs. SVR |
   | Otimização de energia | `energy_prediction` | EnergyConsumption | Ridge vs. GradientBoosting |
   | Energia (boosting) | `energy_prediction_boosting` | EnergyConsumption | HistGradientBoosting (mais features) |

4. **Ligar ao rApp real**: alimentar o modelo com o CSV do `kpm_analytics.sh`
   (dados reais de KPM) além dos datasets sintéticos; conectar ao
   `xapp_ue_tp_moni.c` (EWMA hoje → modelo treinado).
5. **(Opcional) KNIME**: a disciplina usa KNIME (low-code); o mesmo fluxo pode
   ser reproduzido lá, com Python só quando necessário.

## Dependências / bloqueios

- **Treinar/experimentar localmente**: sem bloqueio (é CPU-leve; roda em qualquer
  máquina com as wheels).
- **Rodar o lab E2E no servidor** (UE + gNB RFSIM + coleta KPM real + inferência):
  depende de **4 vCPU** — em 2 vCPU o UE + gNB não coexistem sob o guardrail
  anti-freeze. Runbook do resize reversível: [POLITICA-DE-CUSTOS.md §3](POLITICA-DE-CUSTOS.md).

## Contexto da disciplina (Prof. Julio Tesolin)

- Ferramental: **KNIME + Python** (scikit-learn / pytorch / tensorflow).
- Avaliação: aplicar **2 técnicas** a **1** caso de uso; entregar relatório +
  script; prazo **01/08/26**.
- Casos de uso da ementa: traffic steering, espectro dinâmico, otimização de
  energia, manutenção preditiva, detecção de anomalias.

---

Referências: [`pdfs/ric-ai/README.md`](../pdfs/ric-ai/README.md) ·
[roadmap do README](../README.md) · [`server/panel/vendor/README.md`](../server/panel/vendor/README.md).
