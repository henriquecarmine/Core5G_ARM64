<!-- sync: e36a3f4e -->
> 🌐 **English** translation of the canonical Portuguese doc [`server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md`](../../../../../../server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md). All languages: [INDEX](../../../INDEX.md) · sync checked by `docs/i18n/check-parity.py`.

# Data in the RAN — from raw KPM to KPI (analytics pipeline)

Didactic guide to `scripts/kpm_analytics.sh`, which implements the **"exporting the
lab for analysis exercise"** from Lecture 06 (slide 46) and bridges Project 2
(RIC/E2) to the course **Data Analysis in Telecom Networks (Module 7)**.

> **The central idea (Lecture 06):** the SAME network has two lenses. The RIC sees
> the *control plane* (E2, near-RT decisions). Data analysis sees the same traffic
> as an *analytical data plane* (time series → KPI → decision). What
> `test_e2_kpm.sh` collects is the **analytical input** for the second lens.

---

## 1. The chain (why each stage exists)

Lecture 06 (slide 44, *Fundamentals of O-RAN*, Tripathi & Shah) defines the chain
from raw data to KPI. `kpm_analytics.sh` walks through
Collection→ETL→KPI→Visualization and points to the Decision:

| Stage | What it is | Where, in our lab |
|---|---|---|
| **Collection** | E2 INDICATION (E2SM-KPM), ~1/s | `logs/xapp_kpm_lab.log` (raw xApp text) |
| **Ingestion/ETL** | turn into a structured time series | `kpm_analytics.sh` → `logs/kpm_timeseries.csv` |
| **KPI** | aggregate measurements into an indicator | mean/max throughput per UE |
| **Visualization (EDA)** | see the shape of the data | ASCII sparkline (no dependencies) |
| **Decision** | xApp/rApp acts | UE-TP-rApp (the group's topic), A1 policies |

**Why this matters:** without this chain, KPM stays as machine-unreadable text.
With it, it becomes the input for EDA/ML — exactly what the UE-TP-rApp needs to
predict throughput per UE.

---

## 2. The raw data — actual log format

For each **INDICATION** (a report period ≈ 1 s), `xapp_kpm_moni` prints:

```
      4 KPM ind_msg latency = 1212 [μs]     ← cabeçalho: nº de sequência + latência
UE ID type = gNB, amf_ue_ngap_id = 1        ← dimensão: qual UE
ran_ue_id = 1
DRB.UEThpDl = 1320.00 kbps                  ← medida = valor unidade
DRB.UEThpUl = 8650.00 kbps
RRU.PrbTotDl = 14 %
RRU.PrbTotUl = 61 %
```

**Modeling (slide 39):** each `measName = value unit` line ≈ a **time-series
event** with *tags* (UE, slice, source). The name follows the 3GPP `Family.Name`
convention (it has a dot) — that is how the parser tells a measurement apart from a
context line (`ran_ue_id = 1` has no dot → not a measurement).

| measName | Meaning |
|---|---|
| `DRB.UEThpDl` / `DRB.UEThpUl` | throughput per UE on DL/UL (kbps) — **the central KPI of the UE-TP-rApp** |
| `RRU.PrbTotDl` / `RRU.PrbTotUl` | % of PRBs (radio blocks) used — cell occupancy |
| `DRB.PdcpSduVolume*` | PDCP data volume (how much was transferred) |

---

## 3. How to use

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

> Real-data collection requires the **UE attached + traffic**, which on 2 vCPU uses
> the 2-core window. `kpm_collect_real.sh` does this in a **resilient and 100%
> event-driven** way (heartbeat, no freezing, no failing) — see
> [`KPM-COLETA-RESILIENTE.md`](KPM-COLETA-RESILIENTE.md).

Output (abridged) on the didactic sample:

```
✓ INDICATIONs encontradas no log: 8
✓ série temporal extraída: 32 amostras → logs/kpm_timeseries.csv
  DRB.UEThpUl | ran:1   n=8  média=3721.25 kbps  máx=9120.00 kbps  (janela≈8s)
  RRU.PrbTotUl | ran:1  n=8  média=28.88 %       máx=66.00 %       (janela≈8s)
    ▁▁▄▇█▅▂▁     ← DRB.UEThpUl ao longo do tempo (burst de tráfego)
```

The CSV (`logs/kpm_timeseries.csv`) has the schema
`seq,latency_us,ue,measName,value,unit,slice` — ready to open in a
spreadsheet/notebook (pandas) at the **modeling** step (Module 7 / UE-TP-rApp).

---

## 4. Data prerequisite: throughput ≠ 0 requires a UE with traffic

Without a UE attached **generating traffic**, KPM is still subscribed, but
throughput comes out **~0** (`kpm_analytics.sh` detects this and explains it
instead of failing). For real data you need the **user plane active** — which, on
the 2 vCPU box, depends on the CPU trade-off described in
[`PROJETO2-CPU-E-USERPLANE.md`](PROJETO2-CPU-E-USERPLANE.md) (free the 2 cores or
use 4 vCPU). In other words, data analysis **depends** on a validated user plane —
the same thread that runs through the whole lab.

---

## 5. Next step — from analysis to model (UE-TP-rApp)

The CSV is the input for the group's assigned topic: **UE-TP-rApp** — predicting
throughput per UE from history (RSSI/RSRP/CQI/PRB/throughput). In the NGO benchmark
(slide 27) this rApp reaches **R² ≈ 0.90**. The skeleton is in
`openairinterface5g/openair2/E2AP/flexric/examples/xApp/c/monitor/xapp_ue_tp_moni.c`
(the model is missing). This guide's pipeline delivers exactly the time series that
feeds that model.

> The complete reference for the O-RAN analytics pipeline
> (VES→Kafka→InfluxDB→Grafana) is in Lecture 06 (slides 41–42) — it is the "data
> lake" version of what we do here with CSV.
