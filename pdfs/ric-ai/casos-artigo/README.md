# casos-artigo/ — reproduções abertas dos casos de uso do artigo de referência

Reproduções em Python/scikit-learn dos casos de uso de ML do artigo da
disciplina *"Aplicações de IA e ML em RIC"* — Ngo et al., *"RAN Intelligent
Controller (RIC): From open-source implementation to real-world validation"*,
ICT Express 10(3), 2024 — sobre os **dados reais** do walk test 5G do SUTD
([`FCCLab/sutd_5g_dataset_2023`](https://github.com/FCCLab/sutd_5g_dataset_2023/tree/dataset/dataset),
cópia em [`data/sutd/`](data/sutd/), ~1 MB, 4 trilhas a 2 Hz).

| Caso | Tarefa | Referência no artigo | Pasta |
|---|---|---|---|
| **Localization** | classificar o andar do UE (4/5/6) | Tabela 3 | [`localization/`](localization/) |
| **Predictive Maintenance** | detectar RRU perdida (2×1 RRUs) | Tabela 7 | [`predictive-maintenance/`](predictive-maintenance/) |
| UE-TP | prever throughput DL do UE | Tabela 4 | experimento no material do trabalho final (fora do repo); lab interativo no painel (`/lab/regressao`) |

Cada pasta tem o experimento autocontido (`*_experiment.py`), as tabelas de
métricas (`results/`), figuras (`figures/`) e um README com a análise
comparativa artigo × reprodução.

> **No painel Core5G**, os 3 casos também rodam ao vivo: como **testes no
> servidor** (`p2-ml-uetp`/`p2-ml-localizacao`/`p2-ml-pm` — versões numpy-only,
> sem pandas/matplotlib, em `server/oai-cn-gnb-e2/scripts/ml/`) e como **aulas
> interativas** (`/lab/regressao`, `/lab/localizacao`, `/lab/manutencao`).

## O fio condutor: instance × sequence

O artigo avalia cada caso em dois recortes — **instance** (o modelo vê 1
amostra) e **sequence** (janela de 10 amostras ≈ 5 s). Os números famosos
são todos *sequence* (LSTM 91,1% na Localization, DNN 0,90 no UE-TP, DNN
99,1% no PM), mas **a designação da disciplina para os três casos é
Instance**, onde os campeões são outros:

| Caso | "Número famoso" (sequence) | Campeão no recorte Instance |
|---|---|---|
| Localization | LSTM 91,1% | **XGBoost 84,4%** |
| UE-TP | DNN R² 0,90 | **DNN 0,84** (linear 0,83 logo atrás) |
| PM | DNN 99,1% | **XGBoost 92,6%** |

As reproduções aqui confirmam o recorte instance com split temporal honesto:
boosting 84,1% na Localization e 92,5% no PM — a ≤0,3 p.p. do publicado.

## Cuidados metodológicos (valem para os três casos)

- **Vazamento:** `Corridor_tag`, `lab_*` e `Label` nunca entram como feature
  (no PM, `lab_1rr` **é** o alvo; na Localization, `Corridor_tag` é quase o
  alvo). Identificadores (PCI, C-RNTI, `_oid`) idem.
- **Split temporal:** a 2 Hz, split aleatório põe amostras vizinhas de 0,5 s
  em treino e teste — cada experimento roda os dois protocolos e mostra a
  diferença.
- **Normalização [0,1] e 70:30**, como no protocolo do artigo.

## Uso acadêmico

Material aberto do lab (MIT). Em trabalho de disciplina: cite o repositório
e o artigo, rode o experimento e escreva análise e fundamentação próprias.
