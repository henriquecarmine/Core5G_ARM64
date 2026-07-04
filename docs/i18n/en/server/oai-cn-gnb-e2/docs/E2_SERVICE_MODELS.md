<!-- sync: e36a3f4e -->
> 🌐 **English** translation of the canonical Portuguese doc [`server/oai-cn-gnb-e2/docs/E2_SERVICE_MODELS.md`](../../../../../../server/oai-cn-gnb-e2/docs/E2_SERVICE_MODELS.md). All languages: [INDEX](../../../INDEX.md) · sync checked by `docs/i18n/check-parity.py`.

# Exploring E2 Service Models in OAI

Practical guide to **E2SM-RC**, **E2SM-KPM**, and **custom SMs** on the monolithic OAI gNB (RFSIM).

## Capability map

| SM | O-RAN / Custom | What it exposes | xApp | Works in the lab (222/123)? |
|----|----------------|-------------|------|----------------------------|
| **E2SM-RC** v1.03 | O-RAN | RRC state, RRC message copy, UE ID | `xapp_rc_moni` | **Yes** (aperiodic) |
| **E2SM-KPM** v2.03 | O-RAN | PRB, throughput, PDCP volume… | `xapp_kpm_moni` | OK (slice 222/123 via `test_e2_kpm.sh`) |
| **MAC** | Custom | MAC KPIs per UE | `xapp_cust_moni` | **Yes** |
| **RLC** | Custom | Stats per bearer | same | **Yes** |
| **PDCP** | Custom | Stats per bearer | same | **Yes** |
| **GTP** | Custom | GTP-U NGU stats | same | **Yes** (gNB-mono) |
| **SLICE / TC** | Custom | Slice / traffic control | FlexRIC emulator | **No** on the OAI RAN |

## E2SM-RC — the most interesting one for RAN control

OAI implementation (`openairinterface5g/openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc.c`):

### REPORT Service Style 1 — Message copy (aperiodic)

Events triggered when the UE completes RRC procedures:

| Event | When |
|--------|--------|
| **UE ID** | `RRC Setup Complete`, F1 UE Context Setup |
| **RRC Message copy** | `RRC Reconfiguration`, `Measurement Report`, `Security Mode Complete`, `RRC Setup Complete` |

The `xapp_rc_moni` xApp decodes ASN.1 and prints the UE ID (AMF NGAP ID, RAN UE ID) and RRC content.

### REPORT Service Style 4 — UE Information (aperiodic)

| Parameter | Values |
|-----------|---------|
| **RRC State Changed To** | `idle`, `inactive`, `connected` |

Triggered on RRC transitions (e.g., attach → `RRC_CONNECTED`).

### CONTROL Service Style 1 — Radio Bearer Control

| O-RAN action | OAI behavior |
|------------|-------------------|
| QoS flow mapping | PoC: **creation of a new DRB** (OAI does not multiplex multiple QoS flows into one DRB) |

Test with `xapp_kpm_rc` (KPM monitor + sends RC Control). Actual control on the RAN is limited — see the upstream `qoe-e2` branch for a full demo.

## Exploration scripts

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

Individual tests:

```bash
XAPP_DURATION=30 ./scripts/test_e2_sm.sh rc       # só RC
XAPP_DURATION=30 ./scripts/test_e2_sm.sh kpm_rc  # KPM + RC control PoC
XAPP_DURATION=30 ./scripts/test_e2_sm.sh gtp     # MAC/RLC/PDCP/GTP + DB sqlite
```

### Generate RC events during the test

RC is **aperiodic** — INDICATIONs appear on attach/detach or handover. To see events during `xapp_rc_moni`:

```bash
# Terminal 1: xApp RC (30s)
XAPP_DURATION=30 ./scripts/test_e2_sm.sh rc

# Terminal 2 (nos primeiros 10s): reiniciar UE para forçar RRC Setup
./scripts/down_gnb_oai.sh   # para gNB+UE
./scripts/up_gnb_oai.sh     # sobe de novo → novo RRC attach
```

## What to look for in the logs

```bash
# RC: state change, UE ID, mensagens RRC
grep -iE 'RRC connected|UE ID|RRCReconfiguration|INDICATION' logs/xapp_rc_moni.log

# Custom: métricas periódicas por UE
grep -iE 'MAC|RLC|PDCP|throughput|INDICATION' logs/xapp_cust_moni.log

# Agente E2 no gNB
grep -iE '\[E2 AGENT\].*RC|signal_rrc|signal_ue_id' logs/gnb_oai.log
```

Typical RC success:

```
UE ID type = gNB, amf_ue_ngap_id = ...
RAN Parameter Value = RRC connected
RRC Message ... RRCSetupComplete
```

## E2SM-KPM — O-RAN metrics

3GPP TS 28.552 metrics: `DRB.PdcpSduVolumeDL/UL`, `DRB.UEThpDl/Ul`, `RRU.PrbTotDl/Ul`, etc.

The `xapp_kpm_moni` / `xapp_kpm_rc` xApps (FlexRIC `dev`) use **SST=222, SD=123** by default (`KPM_SST` / `KPM_SD`).

```bash
./scripts/test_e2_kpm.sh
./scripts/explore_e2_sm.sh kpm
KPM_SST=222 KPM_SD=123 XAPP_DURATION=45 ./scripts/test_e2_kpm.sh
```

`KPM_TRAFFIC=1` (default) generates a ping to the DN during the test for volume/throughput metrics.

Closed-loop PoC: `KPM_SST=222 KPM_SD=123 ./scripts/test_e2_sm.sh kpm_rc`

## Custom SMs — offline data (ML/AI)

`xapp_gtp_mac_rlc_pdcp_moni` writes to `/tmp/xapp_db_*` (SQLite):

```bash
ls /tmp/xapp_db_*
# sqlitebrowser /tmp/xapp_db_<timestamp>
```

Reference structs (OAI code):

- MAC: `mac_ue_stats_impl_t`
- RLC: `rlc_radio_bearer_stats_t`
- PDCP: `pdcp_radio_bearer_stats_t`
- GTP: `gtp_ngu_t_stats_t`

## Locally built xApps

The dedicated xApps (RC, KPM, KPM+RC) live in the FlexRIC submodule:

```
openairinterface5g/openair2/E2AP/flexric/build/examples/xApp/c/monitor/
  xapp_rc_moni
  xapp_kpm_moni
  xapp_gtp_mac_rlc_pdcp_moni
openairinterface5g/openair2/E2AP/flexric/build/examples/xApp/c/kpm_rc/
  xapp_kpm_rc
```

Build (automatic in `explore_e2_sm.sh`):

```bash
cd openairinterface5g/openair2/E2AP/flexric/build
cmake .. -GNinja -DE2AP_VERSION=E2AP_V2 -DKPM_VERSION=KPM_V2_03
ninja xapp_rc_moni xapp_kpm_moni xapp_kpm_rc xapp_gtp_mac_rlc_pdcp_moni
```

## Interesting next steps

| Goal | Path |
|----------|---------|
| Real RC Control (new DRB) | Upstream `qoe-e2` branch or `xapp_kpm_rc` + traffic |
| KPM with slice 222/123 | `./scripts/test_e2_kpm.sh` + `flexric-lib/` (dev submodule) |
| CU/DU split + E2 | gNB split + E2 agent in CU-CP/CU-UP/DU |
| O-RAN SC nearRT-RIC | E2AP port 36422, xDevSM framework |
| Wireshark E2AP | Capture SCTP :36421 localhost |

## References

- [E2_FLEXRIC.md](E2_FLEXRIC.md) — lab operation
- [OAI E2AP README](../../../../../../server/oai-cn-gnb-e2/openairinterface5g/openair2/E2AP/README.md)
- O-RAN E2SM-RC v01.03, E2SM-KPM v2.03
