<!-- sync: e36a3f4e -->
> 🌐 Traducción al **español** del documento canónico en portugués [`server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md`](../../../../../../server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md). Todos los idiomas: [INDEX](../../../INDEX.md) · sincronización verificada por `docs/i18n/check-parity.py`.

# Datos en la RAN — del KPM crudo al KPI (pipeline de análisis)

Guía didáctica de `scripts/kpm_analytics.sh`, que implementa el **"ejercicio de
exportar el lab para análisis"** de la Clase 06 (slide 46) y tiende el puente del Proyecto 2
(RIC/E2) hacia la materia **Análisis de Datos en Redes de Telecom (Módulo 7)**.

> **La idea central (Clase 06):** la MISMA red tiene dos lentes. El RIC ve el
> *control plane* (E2, decisiones near-RT). El análisis de datos ve el mismo
> tráfico como *data plane analítico* (series temporales → KPI → decisión). Lo que
> `test_e2_kpm.sh` recolecta es el **insumo analítico** para la segunda lente.

---

## 1. La cadena (por qué existe cada etapa)

La Clase 06 (slide 44, *Fundamentals of O-RAN*, Tripathi & Shah) define la cadena del
dato crudo al KPI. `kpm_analytics.sh` recorre Recolección→ETL→KPI→Visualización y
señala la Decisión:

| Etapa | Qué es | Dónde, en nuestro lab |
|---|---|---|
| **Recolección** | E2 INDICATION (E2SM-KPM), ~1/s | `logs/xapp_kpm_lab.log` (texto crudo del xApp) |
| **Ingestión/ETL** | volverse serie temporal estructurada | `kpm_analytics.sh` → `logs/kpm_timeseries.csv` |
| **KPI** | agregar medidas en un indicador | promedio/máx de throughput por UE |
| **Visualización (EDA)** | ver la forma de los datos | sparkline ASCII (sin dependencias) |
| **Decisión** | el xApp/rApp actúa | UE-TP-rApp (tema del grupo), políticas A1 |

**Por qué esto importa:** sin esa cadena, el KPM queda como texto ilegible para una
máquina. Con ella, se vuelve la entrada de EDA/ML — exactamente lo que el UE-TP-rApp
necesita para predecir throughput por UE.

---

## 2. El dato crudo — formato real del log

`xapp_kpm_moni` imprime, por **INDICATION** (un período de report ≈ 1 s):

```
      4 KPM ind_msg latency = 1212 [μs]     ← cabeçalho: nº de sequência + latência
UE ID type = gNB, amf_ue_ngap_id = 1        ← dimensão: qual UE
ran_ue_id = 1
DRB.UEThpDl = 1320.00 kbps                  ← medida = valor unidade
DRB.UEThpUl = 8650.00 kbps
RRU.PrbTotDl = 14 %
RRU.PrbTotUl = 61 %
```

**Modelado (slide 39):** cada línea `measName = valor unidade` ≈ un **evento de
serie temporal** con *tags* (UE, slice, fuente). El nombre sigue la convención 3GPP
`Família.Nome` (tiene punto) — así es como el parser distingue una medida de una
línea de contexto (`ran_ue_id = 1` no tiene punto → no es una medida).

| measName | Significado |
|---|---|
| `DRB.UEThpDl` / `DRB.UEThpUl` | throughput por UE en DL/UL (kbps) — **KPI central del UE-TP-rApp** |
| `RRU.PrbTotDl` / `RRU.PrbTotUl` | % de PRBs (bloques de radio) usados — ocupación de la celda |
| `DRB.PdcpSduVolume*` | volumen de datos PDCP (cuánto tráfico pasó) |

---

## 3. Cómo usar

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

> La recolección con datos reales exige el **UE attachado + tráfico**, lo que en
> 2 vCPU usa la ventana de 2 cores. `kpm_collect_real.sh` lo hace de forma
> **resiliente y 100% por evento** (heartbeat, sin trabarse, sin fallar) — ver
> [`KPM-COLETA-RESILIENTE.md`](KPM-COLETA-RESILIENTE.md).

Salida (resumida) sobre la muestra didáctica:

```
✓ INDICATIONs encontradas no log: 8
✓ série temporal extraída: 32 amostras → logs/kpm_timeseries.csv
  DRB.UEThpUl | ran:1   n=8  média=3721.25 kbps  máx=9120.00 kbps  (janela≈8s)
  RRU.PrbTotUl | ran:1  n=8  média=28.88 %       máx=66.00 %       (janela≈8s)
    ▁▁▄▇█▅▂▁     ← DRB.UEThpUl ao longo do tempo (burst de tráfego)
```

El CSV (`logs/kpm_timeseries.csv`) tiene el esquema
`seq,latency_us,ue,measName,value,unit,slice` — listo para abrir en
planilla/notebook (pandas) en el paso de **modelado** (Módulo 7 / UE-TP-rApp).

---

## 4. Requisito previo de datos: throughput ≠ 0 exige un UE con tráfico

Sin un UE attachado **generando tráfico**, el KPM incluso se suscribe, pero el
throughput viene **~0** (`kpm_analytics.sh` detecta esto y lo explica en vez de
fallar). Para datos reales hace falta el **user plane activo** — lo que, en el box de
2 vCPU, depende del trade-off de CPU descrito en [`PROJETO2-CPU-E-USERPLANE.md`](PROJETO2-CPU-E-USERPLANE.md)
(liberar los 2 cores o usar 4 vCPU). Es decir, el análisis de datos **depende** del
user plane validado — es el mismo hilo conductor del laboratorio.

---

## 5. Próximo paso — del análisis al modelo (UE-TP-rApp)

El CSV es la entrada del tema sorteado del grupo: **UE-TP-rApp** — predecir el throughput
por UE a partir del histórico (RSSI/RSRP/CQI/PRB/throughput). En el benchmark NGO
(slide 27) ese rApp alcanza **R² ≈ 0,90**. El esqueleto está en
`openairinterface5g/openair2/E2AP/flexric/examples/xApp/c/monitor/xapp_ue_tp_moni.c`
(falta el modelo). El pipeline de esta guía entrega exactamente la serie temporal que
alimenta ese modelo.

> Referencia completa del pipeline analítico O-RAN (VES→Kafka→InfluxDB→Grafana) en la
> Clase 06 (slides 41–42) — es la versión "data lake" de lo que aquí hacemos en CSV.
