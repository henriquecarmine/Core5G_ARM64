# Dados na RAN — do KPM bruto ao KPI (pipeline de análise)

Guia didático do `scripts/kpm_analytics.sh`, que implementa o **"exercício de
exportar o lab para análise"** da Aula 06 (slide 46) e faz a ponte do Projeto 2
(RIC/E2) para a disciplina **Análise de Dados em Redes de Telecom (Módulo 7)**.

> **A ideia central (Aula 06):** a MESMA rede tem duas lentes. O RIC enxerga o
> *control plane* (E2, decisões near-RT). A análise de dados enxerga o mesmo
> tráfego como *data plane analítico* (séries temporais → KPI → decisão). O que o
> `test_e2_kpm.sh` coleta é o **insumo analítico** para a segunda lente.

---

## 1. A cadeia (por que cada etapa existe)

A Aula 06 (slide 44, *Fundamentals of O-RAN*, Tripathi & Shah) define a cadeia do
dado bruto ao KPI. O `kpm_analytics.sh` percorre Coleta→ETL→KPI→Visualização e
aponta a Decisão:

| Etapa | O que é | Onde, no nosso lab |
|---|---|---|
| **Coleta** | E2 INDICATION (E2SM-KPM), ~1/s | `logs/xapp_kpm_lab.log` (texto bruto do xApp) |
| **Ingestão/ETL** | virar série temporal estruturada | `kpm_analytics.sh` → `logs/kpm_timeseries.csv` |
| **KPI** | agregar medidas num indicador | média/máx de throughput por UE |
| **Visualização (EDA)** | ver a forma dos dados | sparkline ASCII (sem dependências) |
| **Decisão** | xApp/rApp atua | UE-TP-rApp (tema do grupo), políticas A1 |

**Por que isto importa:** sem essa cadeia, o KPM fica como texto ilegível por
máquina. Com ela, vira a entrada de EDA/ML — exatamente o que o UE-TP-rApp
precisa para prever throughput por UE.

---

## 2. O dado bruto — formato real do log

O `xapp_kpm_moni` imprime, por **INDICATION** (um período de report ≈ 1 s):

```
      4 KPM ind_msg latency = 1212 [μs]     ← cabeçalho: nº de sequência + latência
UE ID type = gNB, amf_ue_ngap_id = 1        ← dimensão: qual UE
ran_ue_id = 1
DRB.UEThpDl = 1320.00 kbps                  ← medida = valor unidade
DRB.UEThpUl = 8650.00 kbps
RRU.PrbTotDl = 14 %
RRU.PrbTotUl = 61 %
```

**Modelagem (slide 39):** cada linha `measName = valor unidade` ≈ um **evento de
série temporal** com *tags* (UE, slice, fonte). O nome segue a convenção 3GPP
`Família.Nome` (tem ponto) — é assim que o parser distingue uma medida de uma
linha de contexto (`ran_ue_id = 1` não tem ponto → não é medida).

| measName | Significado |
|---|---|
| `DRB.UEThpDl` / `DRB.UEThpUl` | throughput por UE no DL/UL (kbps) — **KPI central do UE-TP-rApp** |
| `RRU.PrbTotDl` / `RRU.PrbTotUl` | % de PRBs (blocos de rádio) usados — ocupação da célula |
| `DRB.PdcpSduVolume*` | volume de dados PDCP (quanto trafegou) |

---

## 3. Como usar

```bash
# 1) gerar dados reais — RECOMENDADO: coletor resiliente (espera o UE attachar
#    por EVENTO, gera tráfego, coleta K indicações, auto-retry, auto-revert):
./scripts/kpm_collect_real.sh       # → logs/xapp_kpm_lab.log + já chama a análise
                                    # detalhes milimétricos: docs/KPM-COLETA-RESILIENTE.md

# alternativa simples (pode colher 0 se o UE ainda não attachou no período):
./scripts/test_e2_kpm.sh            # KPM_TRAFFIC=1 (default) faz ping durante a coleta

# 2) analisar isoladamente (Coleta→ETL→KPI→Viz→Decisão, com o porquê):
./scripts/kpm_analytics.sh          # usa logs/xapp_kpm_lab.log por padrão
                                    # → gera logs/kpm_timeseries.csv

# experimentar sem o lab ao vivo (amostra didática com um burst de tráfego):
./scripts/kpm_analytics.sh scripts/samples/kpm_sample.log
```

> A coleta com dados reais exige o **UE attachado + tráfego**, o que em 2 vCPU usa
> a janela de 2 cores. O `kpm_collect_real.sh` faz isso de forma **resiliente e
> 100% por evento** (heartbeat, sem travar, sem falhar) — ver
> [`KPM-COLETA-RESILIENTE.md`](KPM-COLETA-RESILIENTE.md).

Saída (resumida) sobre a amostra didática:

```
✓ INDICATIONs encontradas no log: 8
✓ série temporal extraída: 32 amostras → logs/kpm_timeseries.csv
  DRB.UEThpUl | ran:1   n=8  média=3721.25 kbps  máx=9120.00 kbps  (janela≈8s)
  RRU.PrbTotUl | ran:1  n=8  média=28.88 %       máx=66.00 %       (janela≈8s)
    ▁▁▄▇█▅▂▁     ← DRB.UEThpUl ao longo do tempo (burst de tráfego)
```

O CSV (`logs/kpm_timeseries.csv`) tem o esquema
`seq,latency_us,ue,measName,value,unit,slice` — pronto para abrir em
planilha/notebook (pandas) no passo de **modelagem** (Módulo 7 / UE-TP-rApp).

---

## 4. Pré-requisito de dados: throughput ≠ 0 exige UE com tráfego

Sem UE attachado **gerando tráfego**, o KPM até é assinado, mas o throughput vem
**~0** (o `kpm_analytics.sh` detecta isso e explica em vez de falhar). Para dados
reais é preciso o **user plane ativo** — o que, no box de 2 vCPU, depende do
trade-off de CPU descrito em [`PROJETO2-CPU-E-USERPLANE.md`](PROJETO2-CPU-E-USERPLANE.md)
(liberar os 2 cores ou usar 4 vCPU). Ou seja, a análise de dados **depende** do
user plane validado — é o mesmo fio condutor do laboratório.

---

## 5. Próximo passo — da análise ao modelo (UE-TP-rApp)

O CSV é a entrada do tema sorteado do grupo: **UE-TP-rApp** — prever o throughput
por UE a partir do histórico (RSSI/RSRP/CQI/PRB/throughput). No benchmark NGO
(slide 27) esse rApp atinge **R² ≈ 0,90**. O esqueleto está em
`openairinterface5g/openair2/E2AP/flexric/examples/xApp/c/monitor/xapp_ue_tp_moni.c`
(falta o modelo). O pipeline deste guia entrega exatamente a série temporal que
alimenta esse modelo.

> Referência completa do pipeline analítico O-RAN (VES→Kafka→InfluxDB→Grafana) na
> Aula 06 (slides 41–42) — é a versão "data lake" do que aqui fazemos em CSV.
