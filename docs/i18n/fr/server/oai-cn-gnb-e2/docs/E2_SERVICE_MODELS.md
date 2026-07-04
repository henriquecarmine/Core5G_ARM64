<!-- sync: e36a3f4e -->
> 🌐 Traduction en **français** du document canonique en portugais [`server/oai-cn-gnb-e2/docs/E2_SERVICE_MODELS.md`](../../../../../../server/oai-cn-gnb-e2/docs/E2_SERVICE_MODELS.md). Toutes les langues : [INDEX](../../../INDEX.md) · synchronisation vérifiée par `docs/i18n/check-parity.py`.

# Exploration des Service Models E2 dans OAI

Guide pratique pour **E2SM-RC**, **E2SM-KPM** et **custom SMs** sur le gNB OAI monolithique (RFSIM).

## Carte des capacités

| SM | O-RAN / Custom | Ce qu'il expose | xApp | Fonctionne dans le lab (222/123) ? |
|----|----------------|-------------|------|----------------------------|
| **E2SM-RC** v1.03 | O-RAN | état RRC, copie de messages RRC, UE ID | `xapp_rc_moni` | **Oui** (apériodique) |
| **E2SM-KPM** v2.03 | O-RAN | PRB, débit, volume PDCP… | `xapp_kpm_moni` | OK (slice 222/123 via `test_e2_kpm.sh`) |
| **MAC** | Custom | KPIs MAC par UE | `xapp_cust_moni` | **Oui** |
| **RLC** | Custom | Stats par bearer | idem | **Oui** |
| **PDCP** | Custom | Stats par bearer | idem | **Oui** |
| **GTP** | Custom | Stats GTP-U NGU | idem | **Oui** (gNB-mono) |
| **SLICE / TC** | Custom | Slice / traffic control | émulateur FlexRIC | **Non** dans le RAN OAI |

## E2SM-RC — le plus intéressant pour le contrôle RAN

Implémentation OAI (`openairinterface5g/openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c`) :

### REPORT Service Style 1 — Message copy (apériodique)

Événements déclenchés quand l'UE achève des procédures RRC :

| Événement | Quand |
|--------|--------|
| **UE ID** | `RRC Setup Complete`, F1 UE Context Setup |
| **RRC Message copy** | `RRC Reconfiguration`, `Measurement Report`, `Security Mode Complete`, `RRC Setup Complete` |

Le xApp `xapp_rc_moni` décode l'ASN.1 et affiche l'UE ID (AMF NGAP ID, RAN UE ID) et le contenu RRC.

### REPORT Service Style 4 — UE Information (apériodique)

| Paramètre | Valeurs |
|-----------|---------|
| **RRC State Changed To** | `idle`, `inactive`, `connected` |

Déclenché lors des transitions RRC (ex. : attachement → `RRC_CONNECTED`).

### CONTROL Service Style 1 — Radio Bearer Control

| Action O-RAN | Comportement OAI |
|------------|-------------------|
| QoS flow mapping | PoC : **création d'un nouveau DRB** (OAI ne multiplexe pas plusieurs QoS flows dans un DRB) |

Tester avec `xapp_kpm_rc` (monitore KPM + envoie du RC Control). Le contrôle réel dans le RAN est limité — voir la branche `qoe-e2` upstream pour une démo complète.

## Scripts d'exploration

```bash
cd ric/code/oai-cn-gnb-e2

# Lab no ar
./scripts/up_e2_lab.sh

# Exploração rápida (custom + RC)
./scripts/explore_e2_sm.sh quick

# Aprofundar RC + PoC KPM/RC control
./scripts/explore_e2_sm.sh rc

# O-RAN KPM + RC agregado
./scripts/explore_e2_sm.sh oran

# Camadas L2/L3 detalhadas
./scripts/explore_e2_sm.sh layers

# Tudo
./scripts/explore_e2_sm.sh full
```

Tests individuels :

```bash
XAPP_DURATION=30 ./scripts/test_e2_sm.sh rc       # só RC
XAPP_DURATION=30 ./scripts/test_e2_sm.sh kpm_rc  # KPM + RC control PoC
XAPP_DURATION=30 ./scripts/test_e2_sm.sh gtp     # MAC/RLC/PDCP/GTP + DB sqlite
```

### Générer des événements RC pendant le test

RC est **apériodique** — les INDICATIONs apparaissent lors d'un attach/detach ou d'un handover. Pour voir des événements pendant `xapp_rc_moni` :

```bash
# Terminal 1: xApp RC (30s)
XAPP_DURATION=30 ./scripts/test_e2_sm.sh rc

# Terminal 2 (nos primeiros 10s): reiniciar UE para forçar RRC Setup
./scripts/down_gnb_oai.sh   # para gNB+UE
./scripts/up_gnb_oai.sh     # sobe de novo → novo RRC attach
```

## Quoi chercher dans les logs

```bash
# RC: state change, UE ID, mensagens RRC
grep -iE 'RRC connected|UE ID|RRCReconfiguration|INDICATION' logs/xapp_rc_moni.log

# Custom: métricas periódicas por UE
grep -iE 'MAC|RLC|PDCP|throughput|INDICATION' logs/xapp_cust_moni.log

# Agente E2 no gNB
grep -iE '\[E2 AGENT\].*RC|signal_rrc|signal_ue_id' logs/gnb_oai.log
```

Succès RC typique :

```
UE ID type = gNB, amf_ue_ngap_id = ...
RAN Parameter Value = RRC connected
RRC Message ... RRCSetupComplete
```

## E2SM-KPM — métriques O-RAN

Métriques 3GPP TS 28.552 : `DRB.PdcpSduVolumeDL/UL`, `DRB.UEThpDl/Ul`, `RRU.PrbTotDl/Ul`, etc.

Les xApps `xapp_kpm_moni` / `xapp_kpm_rc` (FlexRIC `dev`) utilisent par défaut **SST=222, SD=123** (`KPM_SST` / `KPM_SD`).

```bash
./scripts/test_e2_kpm.sh
./scripts/explore_e2_sm.sh kpm
KPM_SST=222 KPM_SD=123 XAPP_DURATION=45 ./scripts/test_e2_kpm.sh
```

`KPM_TRAFFIC=1` (par défaut) génère un ping vers le DN pendant le test pour des métriques de volume/débit.

PoC closed-loop : `KPM_SST=222 KPM_SD=123 ./scripts/test_e2_sm.sh kpm_rc`

## Custom SMs — données offline (ML/AI)

`xapp_gtp_mac_rlc_pdcp_moni` écrit dans `/tmp/xapp_db_*` (SQLite) :

```bash
ls /tmp/xapp_db_*
# sqlitebrowser /tmp/xapp_db_<timestamp>
```

Structs de référence (code OAI) :

- MAC : `mac_ue_stats_impl_t`
- RLC : `rlc_radio_bearer_stats_t`
- PDCP : `pdcp_radio_bearer_stats_t`
- GTP : `gtp_ngu_t_stats_t`

## xApps compilés localement

Les xApps dédiés (RC, KPM, KPM+RC) vivent dans le sous-module FlexRIC :

```
openairinterface5g/openair2/E2AP/flexric/build/examples/xApp/c/monitor/
  xapp_rc_moni
  xapp_kpm_moni
  xapp_gtp_mac_rlc_pdcp_moni
openairinterface5g/openair2/E2AP/flexric/build/examples/xApp/c/kpm_rc/
  xapp_kpm_rc
```

Compiler (automatique dans `explore_e2_sm.sh`) :

```bash
cd openairinterface5g/openair2/E2AP/flexric/build
cmake .. -GNinja -DE2AP_VERSION=E2AP_V2 -DKPM_VERSION=KPM_V2_03
ninja xapp_rc_moni xapp_kpm_moni xapp_kpm_rc xapp_gtp_mac_rlc_pdcp_moni
```

## Prochaines étapes intéressantes

| Objectif | Chemin |
|----------|---------|
| RC Control réel (nouveau DRB) | Branche upstream `qoe-e2` ou `xapp_kpm_rc` + trafic |
| KPM avec slice 222/123 | `./scripts/test_e2_kpm.sh` + `flexric-lib/` (sous-module dev) |
| CU/DU split + E2 | gNB split + E2 agent dans CU-CP/CU-UP/DU |
| O-RAN SC nearRT-RIC | Port E2AP 36422, framework xDevSM |
| Wireshark E2AP | Capturer SCTP :36421 localhost |

## Références

- [E2_FLEXRIC.md](E2_FLEXRIC.md) — exploitation du lab
- [OAI E2AP README](../../../../../../server/oai-cn-gnb-e2/openairinterface5g/openair2/E2AP/README.md)
- O-RAN E2SM-RC v01.03, E2SM-KPM v2.03
