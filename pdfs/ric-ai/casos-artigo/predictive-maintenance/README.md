# PM-rApp (Predictive Maintenance) — reprodução do caso de uso (recorte Instance)

Reprodução aberta do classificador de RRUs ativas do artigo de referência da
disciplina: Ngo et al., *"RAN Intelligent Controller (RIC): From open-source
implementation to real-world validation"*, ICT Express 10(3), 2024
([DOI 10.1016/j.icte.2024.02.001](https://doi.org/10.1016/j.icte.2024.02.001)),
sobre os dados reais do walk test do SUTD
([`FCCLab/sutd_5g_dataset_2023`](https://github.com/FCCLab/sutd_5g_dataset_2023/tree/dataset/dataset)).

## O caso

Uma RRU pode seguir mandando heartbeat pela M-plane e ainda assim estar
defeituosa (antena solta, transmissão caindo na última milha) — para o EMS
ela parece saudável. O PM-rApp detecta o problema **pelo lado do UE**: com
as KPMs de rádio coletadas via KPM, classifica **quantas RRUs realmente
atendem a célula**. Se o modelo diz 1 e o EMS diz 2, dispara alerta para a
equipe de manutenção.

## O que o artigo reporta (Tabela 7)

| Recorte | Melhor modelo | Acc | F1 | Tamanho | Inferência |
|---|---|---|---|---|---|
| **Instance** (1 amostra) | **XGBoost** | **92,6%** | 0,925 | 298 kB | 1,5 µs |
| Instance | SVM | 90,8% | 0,914 | 130 kB | 23,7 µs |
| Sequence (janela 10) | DNN | 99,1% | 0,991 | 5,5 kB | 3,8 µs |

⚠️ **A pegadinha do enunciado:** a designação da disciplina é **Instance** —
e o número famoso do caso ("DNN 99,1%") é do recorte *sequence*. No bloco
que vale, o campeão é o **XGBoost (92,6%)**. Detalhe fino da tabela: o
Linear instance tem recall 1,000 com precisão 0,821 — ele "resolve" o recall
exagerando alarmes, um trade-off clássico de manutenção preditiva (alarme
falso custa uma visita técnica; falha perdida custa a rede no chão).
Mesmo padrão do UE-TP e da Localization.

## Nosso experimento — [`pm_experiment.py`](pm_experiment.py)

- **Dados:** cenários 3 e 4 da Tabela 1 do artigo — a mesma caminhada no
  andar 6 com **2 RRUs outdoor ativas** (classe 0, operação normal) ×
  **1 RRU ativa** (classe 1, "RRU defeituosa"); 4.366 amostras válidas a 2 Hz.
- **Features:** as 7 KPMs que o artigo declara coletar (RSRP, RSRQ, SINR,
  PDSCH PRBs, PDSCH MCS, PUSCH MCS, throughput DL), normalizadas em [0,1].
  **Fora, por vazamento:** os rótulos `lab_*` e `Label` — `lab_1rr` marca
  exatamente a trilha de 1 RRU; usá-lo como feature seria prever o alvo com
  o próprio alvo (no UE-TP essas colunas eram a armadilha de vazamento; aqui
  elas são o **alvo**, nunca entrada).
- **Modelos:** os 5 instance-based da Tabela 7; XGBoost → `GradientBoosting`
  do scikit-learn (mesma família, boosting de árvores) e DNN(1×7,20,1) →
  `MLPClassifier(hidden=(20,))`.
- **Dois protocolos de split:** (A) 70:30 aleatório, como no artigo; (B)
  70:30 **temporal** por trilha (treina no começo da caminhada, testa no fim).

## Resultados

**Protocolo B — split temporal (o número honesto):**

| Modelo | Acc (%) | Precisão | Recall | F1 | Tamanho (kB) | Inf. (µs) |
|---|---|---|---|---|---|---|
| Linear (logística) | 89,9 | 0,832 | 0,997 | 0,907 | 1,6 | 1,6 |
| SVM | 92,5 | 0,904 | 0,949 | 0,926 | 108 | 64,7 |
| Random Forest | 92,5 | 0,910 | 0,941 | 0,925 | 5.814 | 17,7 |
| **Gradient Boosting (~XGBoost)** | **92,5** | 0,909 | 0,943 | **0,925** | 135 | 2,7 |
| MLP ~ DNN(1×7,20,1) | 93,1 | 0,907 | 0,958 | 0,932 | 26 | 1,4 |

**Protocolo A — split aleatório (protocolo do artigo):** valores ficam
*abaixo* do temporal neste caso (RF 90,5%, GB 88,7% —
[tabela completa](results/metrics_random.csv)): como cada classe é uma
trilha contínua, o fim da caminhada é mais "parecido" com o começo dela do
que amostras embaralhadas de regiões de interferência distintas.

**Confronto com o artigo (recorte instance):**

| | Artigo (Tabela 7) | Nosso (temporal) |
|---|---|---|
| Boosting (XGBoost/GB) | 92,6% / F1 0,925 | **92,5% / F1 0,925** |
| SVM | 90,8% / F1 0,914 | 92,5% / F1 0,926 |
| Linear | 89,3% / F1 0,901 (recall 1,000) | 89,9% / F1 0,907 (recall 0,997) |
| DNN/MLP | 87,7% / F1 0,884 | 93,1% / F1 0,932 |
| RF | 89,5% / F1 0,895 | 92,5% / F1 0,925 |

O boosting reproduz a Tabela 7 em 0,1 p.p. (92,5 × 92,6), e até o
comportamento fino do Linear (recall ≈ 1 à custa de precisão) reaparece.
Discrepâncias esperadas: implementação (GradientBoosting × XGBoost; MLP do
sklearn × PyTorch com scheduler), hiperparâmetros padrão e split.

**Figuras** (`figures/`): série de throughput das duas configurações (o
"sintoma" visível da RRU perdida), matriz de confusão do melhor modelo e
importância de features.

## Como rodar

```bash
python3 -m venv .venv && .venv/bin/pip install numpy pandas scikit-learn matplotlib
.venv/bin/python pm_experiment.py
```

## Uso acadêmico

Material aberto do lab (licença MIT do repositório). Quem for usar em
trabalho de disciplina: **cite o repositório e o artigo**, rode o experimento
e escreva a própria análise — as Partes 1 e 2 do relatório (análise crítica
e fundamentação do algoritmo) são individuais por natureza.
