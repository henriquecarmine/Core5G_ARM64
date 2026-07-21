# Localization-rApp — reprodução do caso de uso (recorte Instance)

Reprodução aberta do classificador de andar do artigo de referência da
disciplina: Ngo et al., *"RAN Intelligent Controller (RIC): From open-source
implementation to real-world validation"*, ICT Express 10(3), 2024
([DOI 10.1016/j.icte.2024.02.001](https://doi.org/10.1016/j.icte.2024.02.001)),
sobre os dados reais do walk test do SUTD
([`FCCLab/sutd_5g_dataset_2023`](https://github.com/FCCLab/sutd_5g_dataset_2023/tree/dataset/dataset)).

## O caso

O GPS não funciona bem dentro do prédio. O Localization-rApp estima **em qual
andar (4, 5 ou 6)** o UE está usando só as métricas de rádio que o RIC já
coleta via KPM — um classificador de 3 classes (andares → rótulos 0/1/2).
A saída alimenta o IM-rApp (gerência de interferência) e o Cell-TP-rApp.

## O que o artigo reporta (Tabela 3)

| Recorte | Melhor modelo | Acc | F1 | Tamanho | Inferência |
|---|---|---|---|---|---|
| **Instance** (1 amostra) | **XGBoost** | **84,4%** | 0,843 | 973 kB | 2,1 µs |
| Instance | DNN(1×7,30,3) | 83,4% | 0,836 | 1,7 kB | 2,1 µs |
| Sequence (janela 10) | LSTM | 91,1% | 0,912 | 201 kB | 27,4 µs |

⚠️ **A pegadinha do enunciado:** a designação da disciplina é **Instance** —
e o número famoso do caso ("LSTM 91,1%") é do recorte *sequence*. No bloco
que vale, o campeão é o **XGBoost (84,4%)**, com a DNN logo atrás; a DNN
instance é ~570× menor que o XGBoost, um trade-off relevante para rApp.
Mesmo padrão do UE-TP (lá: DNN sequence 0,90 × instance 0,84).

## Nosso experimento — [`localization_experiment.py`](localization_experiment.py)

- **Dados:** as 3 trilhas com 2 RRUs outdoor ativas (cenários 1–3 da Tabela 1
  do artigo; `Lvl4/Lvl5/Lvl6_AllRRUOn`), 6.479 amostras válidas a 2 Hz.
  A trilha `Lvl6_1RRUOn` fica de fora (outra configuração de rádio — é o
  dado do caso PM).
- **Features:** as 7 KPMs que o artigo declara coletar (RSRP, RSRQ, SINR,
  PDSCH PRBs, PDSCH MCS, PUSCH MCS, throughput DL), normalizadas em [0,1].
  **Fora, por vazamento:** `Corridor_tag` (é quase o alvo), rótulos `lab_*`
  e identificadores (PCI, C-RNTI, `_oid`).
- **Modelos:** os 5 instance-based da Tabela 3; XGBoost → `GradientBoosting`
  do scikit-learn (mesma família, boosting de árvores) e DNN(1×7,30,3) →
  `MLPClassifier(hidden=(30,))`.
- **Dois protocolos de split:** (A) 70:30 aleatório, como no artigo; (B)
  70:30 **temporal** por trilha — a 2 Hz, o split aleatório coloca amostras
  vizinhas de 0,5 s uma no treino e outra no teste, o que infla o resultado.

## Resultados

**Protocolo B — split temporal (o número honesto):**

| Modelo | Acc (%) | Precisão | Recall | F1 | Tamanho (kB) | Inf. (µs) |
|---|---|---|---|---|---|---|
| Linear (logística) | 80,1 | 0,835 | 0,800 | 0,804 | 1,7 | 1,3 |
| SVM | 82,4 | 0,857 | 0,824 | 0,828 | 150 | 95,0 |
| Random Forest | 84,0 | 0,840 | 0,845 | 0,839 | 8.539 | 13,8 |
| **Gradient Boosting (~XGBoost)** | **84,1** | 0,841 | 0,845 | **0,841** | 387 | 4,1 |
| MLP ~ DNN(1×7,30,3) | 80,6 | 0,808 | 0,811 | 0,806 | 30 | 1,4 |

**Protocolo A — split aleatório (protocolo do artigo):** Random Forest sobe
a 90,2% e o Gradient Boosting a 89,1% — acima do publicado, pelo efeito de
vizinhança temporal descrito acima ([tabela completa](results/metrics_random.csv)).

**Confronto com o artigo (recorte instance):**

| | Artigo (Tabela 3) | Nosso (temporal) | Nosso (aleatório) |
|---|---|---|---|
| Boosting (XGBoost/GB) | 84,4% / F1 0,843 | **84,1% / F1 0,841** | 89,1% |
| Linear | 80,2% / F1 0,805 | 80,1% / F1 0,804 | 78,2% |
| DNN/MLP | 83,4% / F1 0,836 | 80,6% / F1 0,806 | 84,8% |
| SVM | 82,5% / F1 0,829 | 82,4% / F1 0,828 | 83,8% |

O split temporal reproduz a Tabela 3 quase ponto a ponto (boosting, linear e
SVM a ≤0,3 p.p. do publicado). Discrepâncias esperadas: implementação
(GradientBoosting × XGBoost; MLP do sklearn × PyTorch com scheduler),
hiperparâmetros padrão e a composição exata do split de 30%.

**Figuras** (`figures/`): dispersão RSRP×SINR por andar, matriz de confusão
do melhor modelo e importância de features (RSRP/RSRQ dominam — a
"assinatura de rádio" de cada andar é o que o modelo aprende).

## Como rodar

```bash
python3 -m venv .venv && .venv/bin/pip install numpy pandas scikit-learn matplotlib
.venv/bin/python localization_experiment.py
```

## Uso acadêmico

Material aberto do lab (licença MIT do repositório). Quem for usar em
trabalho de disciplina: **cite o repositório e o artigo**, rode o experimento
e escreva a própria análise — as Partes 1 e 2 do relatório (análise crítica
e fundamentação do algoritmo) são individuais por natureza.
