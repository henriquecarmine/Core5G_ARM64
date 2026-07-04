<!-- sync: e36a3f4e -->
> 🌐 Traduction en **français** du document canonique en portugais [`server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md`](../../../../../../server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md). Toutes les langues : [INDEX](../../../INDEX.md) · synchronisation vérifiée par `docs/i18n/check-parity.py`.

# Données dans le RAN — du KPM brut au KPI (pipeline d'analyse)

Guide pédagogique de `scripts/kpm_analytics.sh`, qui met en œuvre l'**« exercice
d'export du lab pour analyse »** du Cours 06 (slide 46) et fait le pont entre le Projet 2
(RIC/E2) et la matière **Analyse de Données dans les Réseaux de Télécom (Module 7)**.

> **L'idée centrale (Cours 06) :** le MÊME réseau a deux prismes. Le RIC voit le
> *control plane* (E2, décisions near-RT). L'analyse de données voit le même
> trafic comme un *data plane analytique* (séries temporelles → KPI → décision). Ce que
> `test_e2_kpm.sh` collecte est la **matière première analytique** pour le second prisme.

---

## 1. La chaîne (pourquoi chaque étape existe)

Le Cours 06 (slide 44, *Fundamentals of O-RAN*, Tripathi & Shah) définit la chaîne de la
donnée brute au KPI. `kpm_analytics.sh` parcourt Collecte→ETL→KPI→Visualisation et
pointe vers la Décision :

| Étape | Ce que c'est | Où, dans notre lab |
|---|---|---|
| **Collecte** | E2 INDICATION (E2SM-KPM), ~1/s | `logs/xapp_kpm_lab.log` (texte brut du xApp) |
| **Ingestion/ETL** | transformer en série temporelle structurée | `kpm_analytics.sh` → `logs/kpm_timeseries.csv` |
| **KPI** | agréger des mesures en un indicateur | moyenne/max de débit par UE |
| **Visualisation (EDA)** | voir la forme des données | sparkline ASCII (sans dépendances) |
| **Décision** | le xApp/rApp agit | UE-TP-rApp (thème du groupe), politiques A1 |

**Pourquoi c'est important :** sans cette chaîne, le KPM reste un texte illisible par
la machine. Avec elle, il devient l'entrée de l'EDA/ML — exactement ce dont le
UE-TP-rApp a besoin pour prédire le débit par UE.

---

## 2. La donnée brute — format réel du log

`xapp_kpm_moni` affiche, par **INDICATION** (une période de report ≈ 1 s) :

```
      4 KPM ind_msg latency = 1212 [μs]     ← cabeçalho: nº de sequência + latência
UE ID type = gNB, amf_ue_ngap_id = 1        ← dimensão: qual UE
ran_ue_id = 1
DRB.UEThpDl = 1320.00 kbps                  ← medida = valor unidade
DRB.UEThpUl = 8650.00 kbps
RRU.PrbTotDl = 14 %
RRU.PrbTotUl = 61 %
```

**Modélisation (slide 39) :** chaque ligne `measName = valor unidade` ≈ un **événement de
série temporelle** avec des *tags* (UE, slice, source). Le nom suit la convention 3GPP
`Família.Nome` (comporte un point) — c'est ainsi que le parser distingue une mesure d'une
ligne de contexte (`ran_ue_id = 1` n'a pas de point → n'est pas une mesure).

| measName | Signification |
|---|---|
| `DRB.UEThpDl` / `DRB.UEThpUl` | débit par UE en DL/UL (kbps) — **KPI central du UE-TP-rApp** |
| `RRU.PrbTotDl` / `RRU.PrbTotUl` | % de PRBs (blocs radio) utilisés — occupation de la cellule |
| `DRB.PdcpSduVolume*` | volume de données PDCP (combien de trafic est passé) |

---

## 3. Comment l'utiliser

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

> La collecte avec des données réelles exige l'**UE attaché + trafic**, ce qui, sur
> 2 vCPU, utilise la fenêtre des 2 cœurs. `kpm_collect_real.sh` le fait de façon
> **résiliente et 100 % par événement** (heartbeat, sans blocage, sans échec) — voir
> [`KPM-COLETA-RESILIENTE.md`](KPM-COLETA-RESILIENTE.md).

Sortie (résumée) sur l'échantillon pédagogique :

```
✓ INDICATIONs encontradas no log: 8
✓ série temporal extraída: 32 amostras → logs/kpm_timeseries.csv
  DRB.UEThpUl | ran:1   n=8  média=3721.25 kbps  máx=9120.00 kbps  (janela≈8s)
  RRU.PrbTotUl | ran:1  n=8  média=28.88 %       máx=66.00 %       (janela≈8s)
    ▁▁▄▇█▅▂▁     ← DRB.UEThpUl ao longo do tempo (burst de tráfego)
```

Le CSV (`logs/kpm_timeseries.csv`) a le schéma
`seq,latency_us,ue,measName,value,unit,slice` — prêt à ouvrir dans un
tableur/notebook (pandas) à l'étape de **modélisation** (Module 7 / UE-TP-rApp).

---

## 4. Prérequis de données : débit ≠ 0 exige un UE avec du trafic

Sans UE attaché **générant du trafic**, le KPM est bien souscrit, mais le débit reste
**~0** (`kpm_analytics.sh` le détecte et l'explique au lieu d'échouer). Pour des données
réelles, il faut un **user plane actif** — ce qui, sur le box de 2 vCPU, dépend du
compromis de CPU décrit dans [`PROJETO2-CPU-E-USERPLANE.md`](PROJETO2-CPU-E-USERPLANE.md)
(libérer les 2 cœurs ou utiliser 4 vCPU). Autrement dit, l'analyse de données **dépend** du
user plane validé — c'est le même fil conducteur du laboratoire.

---

## 5. Étape suivante — de l'analyse au modèle (UE-TP-rApp)

Le CSV est l'entrée du thème tiré au sort par le groupe : **UE-TP-rApp** — prédire le débit
par UE à partir de l'historique (RSSI/RSRP/CQI/PRB/débit). Dans le benchmark NGO
(slide 27), ce rApp atteint **R² ≈ 0,90**. Le squelette se trouve dans
`openairinterface5g/openair2/E2AP/flexric/examples/xApp/c/monitor/xapp_ue_tp_moni.c`
(le modèle manque). Le pipeline de ce guide fournit exactement la série temporelle qui
alimente ce modèle.

> Référence complète du pipeline analytique O-RAN (VES→Kafka→InfluxDB→Grafana) au
> Cours 06 (slides 41–42) — c'est la version « data lake » de ce que nous faisons ici en CSV.
