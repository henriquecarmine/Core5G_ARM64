<!-- sync: e36a3f4e -->
> 🌐 **English** translation of the canonical Portuguese doc [`server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md`](../../../../../../server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md). All languages: [INDEX](../../../INDEX.md) · sync checked by `docs/i18n/check-parity.py`.

# E2 Interface and Service Models (FlexRIC)

Guide to operating the **E2** interface between the OAI gNB and a **nearRT-RIC** (FlexRIC), and testing O-RAN and custom **Service Models** (SMs).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Core OAI (AMF, SMF, UPF-VPP, ...)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │ N2 / N3
┌──────────────────────────┴──────────────────────────────────┐
│  gNB OAI (nr-softmodem)                                       │
│    └── E2 Agent ──E2AP──► nearRT-RIC (FlexRIC) :36421         │
│                              └── xApps (KPM, RC, MAC, ...)    │
└──────────────────────────┬──────────────────────────────────┘
                           │ RFSIM
                      nrUE (nr-uesoftmodem)
```

## Available Service Models

| SM | Type | Encoding | Recommended xApp | Notes |
|----|------|----------|------------------|-------|
| **E2SM-KPM** v2.03 | O-RAN | ASN.1 | `xapp_oran_moni` | 3GPP metrics (PRB, throughput, PDCP volume…) |
| **E2SM-RC** v1.03 | O-RAN | ASN.1 | `xapp_oran_moni` | RRC state, message copy, QoS control (PoC) |
| **MAC** | Custom | Plain | `xapp_gtp_mac_rlc_pdcp_moni` | L2 MAC KPIs per UE |
| **RLC** | Custom | Plain | `xapp_gtp_mac_rlc_pdcp_moni` | RLC KPIs per bearer |
| **PDCP** | Custom | Plain | `xapp_gtp_mac_rlc_pdcp_moni` | PDCP KPIs per bearer |
| **GTP** | Custom | Plain | `xapp_gtp_mac_rlc_pdcp_moni` | GTP-U NGU stats |

Default build versions: **E2AP v2.03** + **E2SM-KPM v2.03** (must match between gNB and FlexRIC).

## Versions and encoding (what THIS platform uses)

| Component | Version/value | Where it is defined |
|---|---|---|
| FlexRIC (embedded in OAI) | **2.0.0** | `openairinterface5g/openair2/E2AP/flexric/CMakeLists.txt` (`project(FlexRIC VERSION 2.0.0)`) |
| E2AP | v2.03 | build flag (`-DE2AP_VERSION=E2AP_V2`) |
| E2AP encoding | **ASN.1** (`E2AP_ENCODING="ASN"`, the default) | `flexric/CMakeLists.txt` line ~205; our scripts do **not** override it |
| FlatBuffers/FlatCC | **not used** | upstream alternative (`-DE2AP_ENCODING=FLATBUFFERS`, requires FlatCC installed); outside our build |

> For the paper: "E2AP with ASN.1 encoding (FlexRIC 2.0.0); FlatBuffers is
> supported by upstream FlexRIC, but not used on this platform."
> The custom SMs (MAC/RLC/PDCP/GTP) use their own encoding ("Plain",
> table above) — this belongs to the Service Model, not to E2AP.

Upstream documentation: `openairinterface5g/openair2/E2AP/README.md`

## Prerequisites

1. **FlexRIC** installed on the host (Service Models in `/usr/local/lib/flexric/`):

   ```bash
   # Se ainda não tiver FlexRIC:
   git clone https://gitlab.eurecom.fr/mosaic5g/flexric.git
   cd flexric && git checkout dev
   mkdir build && cd build
   cmake .. -GNinja -DE2AP_VERSION=E2AP_V2 -DKPM_VERSION=KPM_V2_03
   ninja && sudo ninja install
   ```

2. **FlexRIC submodule** in OAI (to build the E2 agent):

   ```bash
   # Automático via ./scripts/build_e2.sh
   ```

3. **OAI Core** operational (`./scripts/up_core.sh`).

## Building the gNB with E2 Agent

```bash
cd ric/code/oai-cn-gnb-e2
./scripts/build_e2.sh
```

This builds `nr-softmodem` and `nr-uesoftmodem` with `-DE2_AGENT=ON`. Log in `logs/build_e2.log` (~15–30 min on the first run).

## E2 configuration on the gNB

In `openairinterface5g/scripts/gnb.conf`:

```bash
e2_agent = {
  near_ric_ip_addr = "127.0.0.1";
  sm_dir = "/usr/local/lib/flexric/";
};
```

- `near_ric_ip_addr`: nearRT-RIC IP (localhost if FlexRIC runs on the same host).
- `sm_dir`: directory with `libkpm_sm.so`, `librc_sm.so`, `libmac_sm.so`, etc.

FlexRIC E2AP port: **36421** (O-RAN SC uses 36422 — requires recompilation with `e2ap_server_port`).

## Operational flow

### Option A — full lab (recommended)

```bash
./scripts/up_e2_lab.sh          # Core + RIC + gNB + UE
./scripts/test_e2_sm.sh cust    # testar MAC/RLC/PDCP/GTP
./scripts/down_e2_lab.sh
```

### Option B — step by step

```bash
./scripts/up_core.sh
./scripts/up_flexric.sh
./scripts/up_gnb_oai.sh
./scripts/test_e2_sm.sh cust
```

## Testing Service Models

```bash
# Custom SMs (funciona com slice 222/123 do laboratório)
XAPP_DURATION=30 ./scripts/test_e2_sm.sh cust

# O-RAN KPM + RC
./scripts/test_e2_sm.sh oran

# Todos os SMs
./scripts/test_e2_sm.sh all
```

### Check E2 setup

```bash
grep -iE 'E2|RIC|setup|indication' logs/gnb_oai.log
grep -iE 'E2|setup|indication' logs/nearRT-RIC.log
```

Signs of success:
- gNB: `E2 Setup` messages / SCTP connection to the RIC
- xApp: `RIC INDICATION` with periodic metrics

### KPM and S-NSSAI slice

By upstream default, the KPM xApp subscribes to **SST=1**. This lab uses **SST=222, SD=123**.

The `xapp_kpm_moni` and `xapp_kpm_rc` xApps (FlexRIC `dev` submodule) were adjusted for the lab slice:

```bash
# Padrão: SST=222 SD=123 (Core/AMF/gNB/UE)
./scripts/test_e2_kpm.sh

# Override
KPM_SST=222 KPM_SD=123 XAPP_DURATION=45 ./scripts/test_e2_kpm.sh

# Só SST (SD wildcard no agente)
KPM_SD=any ./scripts/test_e2_kpm.sh
```

Supported O-RAN metrics (3GPP TS 28.552): `DRB.PdcpSduVolumeDL/UL`, `DRB.UEThpDl/Ul`, `RRU.PrbTotDl/Ul`, etc.

Generate traffic during the test (`KPM_TRAFFIC=1` by default) for non-zero throughput/volume metrics.

**SMs:** the gNB and the nearRT-RIC must use the submodule libs (`flexric-lib/`), not `/usr/local/lib/flexric/` — the system-installed version fails with AMF Region ID 128 from the OAI Core. `./scripts/build_flexric_tools.sh` builds and syncs automatically.

**Note:** `xapp_oran_moni` (installed in `/usr/local`) still uses SST=1 — use `./scripts/test_e2_kpm.sh` for KPM in this lab.

## Scripts

| Script | Description |
|--------|-------------|
| `build_e2.sh` | Builds gNB/nrUE with E2 agent |
| `up_flexric.sh` | Starts nearRT-RIC |
| `down_flexric.sh` | Stops RIC and xApps |
| `up_e2_lab.sh` | Core + RIC + gNB + UE |
| `down_e2_lab.sh` | Stops gNB and RIC (`--all` includes Core) |
| `test_e2_kpm.sh` | KPM with lab slice (222/123) + traffic |
| `explore_e2_sm.sh` | Exploration suite (rc, oran, layers, full) |
| `test_e2_rc_attach.sh` | RC with synchronized attach (captures INDICATIONs) |
| `build_flexric_tools.sh` | Builds nearRT-RIC + dedicated xApps (dev) |

## Troubleshooting

| Problem | Likely cause | Solution |
|----------|----------------|---------|
| Build fails "submodules not downloaded" | Empty FlexRIC | `./scripts/build_e2.sh` (clones automatically) |
| gNB does not connect to the RIC | RIC stopped or wrong IP | `./scripts/up_flexric.sh`; check `near_ric_ip_addr` |
| xApp with no INDICATION (cust) | UE with no PDU session | Wait for registration; check AMF/SMF logs |
| xApp with no INDICATION (KPM) | SST=1 slice filter | Use `test_e2_sm.sh cust` or align the slice |
| `libkpm_sm.so` not found | FlexRIC not installed | `./scripts/build_flexric_tools.sh` |
| KPM crash / timeout | Misaligned SMs from `/usr/local` (AMF Region ID 128) | Use `flexric-lib/` via `./scripts/sync_flexric_lib.sh` |
| xApp crash `e2ap_dec_e42_setup_response` | xApp from `/usr/local` or `/opt/flexric` | `./scripts/test_e2_sm.sh` uses only xApps from the dev submodule |

## References

- [OAI E2AP README](../../../../../../server/oai-cn-gnb-e2/openairinterface5g/openair2/E2AP/README.md)
- [FlexRIC](https://gitlab.eurecom.fr/mosaic5g/flexric)
- [O-RAN E2SM-KPM](https://orandownloadsweb.azurewebsites.net/specifications)
- Upstream Docker Compose (without Core): `openairinterface5g/ci-scripts/yaml_files/5g_rfsimulator_flexric/`
