<!-- sync: e8f9da69 -->
> 🌐 **English** translation of the canonical Portuguese doc [`server/oai-cn-gnb-e2/docs/TUTORIAL_LAB_E2.md`](../../../../../../server/oai-cn-gnb-e2/docs/TUTORIAL_LAB_E2.md). All languages: [INDEX](../../../INDEX.md) · sync checked by `docs/i18n/check-parity.py`.

# Tutorial — OAI Lab + E2 Interface (FlexRIC)

Step-by-step guide to reproduce the **native 5G SA** lab (Docker Core + gNB/nrUE RFSIM + nearRT-RIC + xApps) with **E2 Service Models** tests (custom, RC, KPM).

> **Scope:** this lab runs on the **host** (Docker only for the Core). It does **not** use Kind multicluster or integration with SD-RAN/Aether.

> **Core images on arm64:** the `oaisoftwarealliance/*:v1.5.1` images do not exist on DockerHub for `linux/arm64`. They were compiled natively in this project. See the full guide in [OAI-CORE-ARM64.md](OAI-CORE-ARM64.md) before trying to bring up the Core on a Graviton2/Apple Silicon host.

---

## 1. Results obtained (summary)

| Procedure | Status | Evidence |
|--------------|--------|-----------|
| OAI Core (UPF-VPP, scenario 1) | ✅ OK | Containers `oai-amf`, `oai-smf`, `oai-upf`, … |
| Build gNB + nrUE with E2 agent | ✅ OK | `nr-softmodem` with `--build-e2`, FlexRIC branch `dev` |
| Build nearRT-RIC + xApps (submodule) | ✅ OK | `build_flexric_tools.sh` |
| UE attach (IMSI 208950000000032, slice 222/123) | ✅ OK | `RRCSetupComplete`, PDU session |
| E2 SETUP (gNB ↔ nearRT-RIC) | ✅ OK | `[E2-AGENT]: E2 SETUP RESPONSE rx` |
| Custom SMs (MAC/RLC/PDCP/GTP, IDs 142–148) | ✅ OK | `xapp_cust_moni`, E2 node registered |
| **E2SM-RC** v1.03 | ✅ OK | INDICATION with `RRCSetupComplete` decoded (ASN.1) |
| **E2SM-KPM** v2.03 (slice 222/123) | ✅ OK | Periodic INDICATIONs with `DRB.UEThp*`, `RRU.PrbTot*` |
| KPM+RC PoC (`xapp_kpm_rc`) | ⚠️ Not validated end-to-end | Binary compiled; use after isolated KPM/RC |
| SLICE / TC (FlexRIC emulators) | ❌ N/A | Not supported by the E2 agent of the monolithic OAI gNB |

**Aligned versions:** E2AP v2 (`E2AP_V2`) + E2SM-KPM v2.03 (`KPM_V2_03`), FlexRIC branch **`dev`**.

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  Core OAI (Docker) — oai-cn5g-fed/docker-compose                    │
│  AMF · SMF · NRF · UPF-VPP · UDM · UDR · AUSF · MySQL · DN          │
│  Rede: demo-oai (192.168.70.0/24)  ·  Slice lab: SST=222, SD=123    │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ NGAP / GTP-U
┌───────────────────────────────▼─────────────────────────────────────┐
│  RAN nativo (host) — openairinterface5g                             │
│  nr-softmodem (gNB + E2 agent)  ←RFSIM→  nr-uesoftmodem             │
│  IP host na demo-oai: 192.168.70.129                                │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ E2AP SCTP :36421
┌───────────────────────────────▼─────────────────────────────────────┐
│  nearRT-RIC + xApps (host) — FlexRIC submodule dev                  │
│  nearRT-RIC :36421  ·  iApp (E42) :36422                            │
│  xApps: xapp_kpm_moni, xapp_rc_moni, xapp_cust_moni, …              │
│  SMs: flexric-lib/ (submodule dev — **não** usar /usr/local)        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Prerequisites

- Ubuntu 22.04+ with Docker, Python 3, sudo
- ~8 GB free RAM, ~15 GB disk (Core + OAI build + FlexRIC)
- IPv4 forwarding: `sudo sysctl -w net.ipv4.ip_forward=1`
- Docker Hub account (pull OAI images)

Additional documentation:

- [INSTALACAO_GNB_OAI.md](INSTALACAO_GNB_OAI.md) — dependencies and base RAN build
- [SLIDES_LAB_E2.md](../../../../../../server/oai-cn-gnb-e2/docs/SLIDES_LAB_E2.md) — presentation of the results (Marp format)
- [E2_FLEXRIC.md](E2_FLEXRIC.md) — E2/FlexRIC operation
- [E2_SERVICE_MODELS.md](E2_SERVICE_MODELS.md) — details of RC/KPM/custom SMs

---

## 4. Preparation (once)

### 4.1 Clone / enter the project

```bash
cd ric/code/oai-cn-gnb-e2
```

### 4.2 Install OAI dependencies

```bash
cd openairinterface5g/cmake_targets
./build_oai --ninja -I
cd ../..
```

### 4.3 Build gNB + nrUE **with E2 agent**

```bash
./scripts/build_e2.sh
```

Expected output (final):

```
Build concluído. Binários em: openairinterface5g/cmake_targets/ran_build/build/
  nr-softmodem (com E2 agent)
  nr-uesoftmodem
```

Full log: `logs/build_e2.log`

### 4.4 Build nearRT-RIC, Service Models and xApps

```bash
./scripts/build_flexric_tools.sh
```

This compiles:

- `nearRT-RIC` (FlexRIC submodule)
- SMs: `libkpm_sm.so`, `librc_sm.so`, `libmac_sm.so`, …
- xApps: `xapp_kpm_moni`, `xapp_rc_moni`, `xapp_kpm_rc`, …

The libs are copied to **`flexric-lib/`** (local project path).

> **Important:** the OAI Core uses **AMF Region ID = 128**. The `libkpm_sm.so` installed in `/usr/local/lib/flexric/` (old version) **crashed** when generating KPM INDICATIONs. Always use **`flexric-lib/`** from the `dev` submodule.

---

## 5. Bring up the lab

### Option A — Full E2 lab (recommended)

```bash
./scripts/up_e2_lab.sh
```

Sequence: Core → nearRT-RIC → gNB + nrUE (with `--e2_agent.sm_dir flexric-lib/`).

### Option B — Manual step by step

```bash
# 1. Core 5G (UPF-VPP, scenario 1)
./scripts/up_core.sh

# 2. nearRT-RIC (submodule dev + flexric-lib/)
./scripts/up_flexric.sh

# 3. gNB + nrUE (RFSIM, slice 222/123)
./scripts/up_gnb_oai.sh
```

### Verify the Core

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep oai
```

Example:

```
oai-amf     Up ...
oai-smf     Up ...
oai-upf     Up ...
```

### Verify E2 on the gNB

```bash
grep -E '\[E2 AGENT\]|\[E2-AGENT\]' logs/gnb_oai.log | tail -15
```

Expected log (with `flexric-lib/`):

```
[E2 NODE]: Args 127.0.0.1 .../flexric-lib/
[E2 AGENT]: nearRT-RIC IP Address = 127.0.0.1, PORT = 36421, RAN type = ngran_gNB, nb_id = 3584
[E2 AGENT]: Opening plugin from path = .../flexric-lib/libkpm_sm.so
[E2-AGENT]: E2 SETUP-REQUEST tx
[E2-AGENT]: E2 SETUP RESPONSE rx
```

### Verify UE attach

```bash
grep RRCSetupComplete logs/gnb_oai.log | tail -3
grep -i registered logs/ue_oai.log | tail -3
```

---

## 6. E2 tests — Service Models

### 6.1 Custom SMs (MAC, RLC, PDCP, GTP)

Plain encoding; works independently of the slice.

```bash
./scripts/test_e2_sm.sh cust
# ou exploração rápida:
./scripts/explore_e2_sm.sh quick
```

Typical log (`logs/xapp_cust_moni.log`):

```
Connected E2 nodes = 1
 Registered node 0 ran func id = 2    # KPM
 Registered node 0 ran func id = 3    # RC
 Registered node 0 ran func id = 142  # MAC
 Registered node 0 ran func id = 143  # RLC
 Registered node 0 ran func id = 144  # PDCP
 ...
```

### 6.2 E2SM-RC (RRC events)

Critical order: **RIC → xApp RC → gNB → UE** (subscription before attach).

```bash
./scripts/test_e2_rc_attach.sh
```

Typical log (`logs/xapp_rc_attach.log`):

```
Connected E2 nodes = 1
[xApp]: Successfully subscribed to RAN_FUNC_ID 3

      1 RC Indication Message received:
RAN Parameter Name = RRC Message
...
            <rrcSetupComplete>
                <rrc-TransactionIdentifier>1</rrc-TransactionIdentifier>
                ...
            </rrcSetupComplete>
```

> **Note:** `xapp_rc_moni` may end with a timeout in `sync_ui.c` after the **first** INDICATION — known behavior of the upstream example. The INDICATION was already captured before the crash.

### 6.3 E2SM-KPM (3GPP metrics, lab slice)

Slice aligned with the Core/AMF: **SST=222, SD=123** (see `openairinterface5g/scripts/ue.conf` and `gnb.conf`).

```bash
./scripts/test_e2_kpm.sh

# Parâmetros opcionais:
KPM_SST=222 KPM_SD=123 XAPP_DURATION=45 KPM_TRAFFIC=1 ./scripts/test_e2_kpm.sh
```

Typical log (`logs/xapp_kpm_lab.log`):

```
Connected E2 nodes = 1
[xApp]: Successfully subscribed to RAN_FUNC_ID 2

      1 KPM ind_msg latency = ...
UE ID type = gNB, amf_ue_ngap_id = 7
ran_ue_id = 1
DRB.PdcpSduVolumeDL = 0 [Mb]
DRB.PdcpSduVolumeUL = 0 [Mb]
DRB.RlcSduDelayDl = 0.00 [μs]
DRB.UEThpDl = 18.04 [kbps]
DRB.UEThpUl = 19.18 [kbps]
RRU.PrbTotDl = 0 [%]
RRU.PrbTotUl = 2 [%]

      2 KPM ind_msg latency = ...
DRB.UEThpDl = 3.72 [kbps]
...
```

With `KPM_TRAFFIC=1` (default), the script generates a ping to the DN (`192.168.73.135`) via the UE interface (`12.1.1.x`), increasing the measured throughput.

### 6.4 Exploration by suite

```bash
./scripts/explore_e2_sm.sh rc      # foco RC
./scripts/explore_e2_sm.sh kpm     # foco KPM
./scripts/explore_e2_sm.sh oran    # KPM + RC
./scripts/explore_e2_sm.sh layers  # custom MAC/RLC/PDCP/GTP
./scripts/explore_e2_sm.sh full    # todas (demorado)
```

---

## 7. Stop the lab

```bash
# Só E2 (RIC + xApps)
./scripts/down_flexric.sh

# RAN (gNB + nrUE)
./scripts/down_gnb_oai.sh

# Lab E2 completo
./scripts/down_e2_lab.sh

# Core Docker
./scripts/down_core.sh

# Tudo
./scripts/down_all.sh
```

---

## 8. Relevant configuration

| Parameter | Lab value | File |
|-----------|-----------|----------|
| PLMN | 208 / 95 | `gnb.conf`, `ue.conf` |
| S-NSSAI | SST **222**, SD **123** | `gnb.conf`, `ue.conf` |
| UE IMSI | 208950000000032 | `ue.conf` |
| AMF IP (gNB) | 192.168.70.129 (host, iface `demo-oai`) | `gnb.conf` |
| nearRT-RIC | 127.0.0.1:36421 | `gnb.conf` → `e2_agent.near_ric_ip_addr` |
| E2 SMs | `flexric-lib/` (project) | `--e2_agent.sm_dir` in the scripts |
| KPM slice filter | `KPM_SST=222`, `KPM_SD=123` | env vars in the KPM scripts |

Example `e2_agent` in `openairinterface5g/scripts/gnb.conf`:

```
e2_agent = {
  near_ric_ip_addr = "127.0.0.1";
  sm_dir = ".../flexric-lib/";   # override via --e2_agent.sm_dir nos scripts
};
```

---

## 9. Reference scripts

| Script | Function |
|--------|--------|
| `build_e2.sh` | Builds gNB/nrUE with E2 agent |
| `build_flexric_tools.sh` | Builds RIC, SMs, xApps; populates `flexric-lib/` |
| `sync_flexric_lib.sh` | Copies `.so` from the FlexRIC build → `flexric-lib/` |
| `up_e2_lab.sh` | Core + RIC + gNB + UE |
| `up_flexric.sh` / `down_flexric.sh` | nearRT-RIC |
| `up_gnb_oai.sh` / `down_gnb_oai.sh` | gNB + nrUE |
| `test_e2_kpm.sh` | KPM test slice 222/123 |
| `test_e2_rc_attach.sh` | RC test with fresh attach |
| `test_e2_sm.sh` | Tests per SM (`cust`, `rc`, `kpm`, …) |
| `explore_e2_sm.sh` | Exploration suites |

Logs: **`logs/`** directory (`gnb_oai.log`, `ue_oai.log`, `nearRT-RIC.log`, `xapp_kpm_lab.log`, …).

---

## 10. Troubleshooting

### KPM timeout / gNB crash

**Symptom:**

```
cp_amf_region_id_to_bit_string: Assertion `src < 64' failed
```

**Cause:** `libkpm_sm.so` from `/usr/local` incompatible with AMF Region ID 128.

**Solution:**

```bash
./scripts/build_flexric_tools.sh
./scripts/down_flexric.sh && ./scripts/down_gnb_oai.sh
./scripts/test_e2_kpm.sh
```

### nearRT-RIC crash `E2 Node not found in the tree`

**Cause:** "zombie" xApps connecting to the RIC without a registered E2 node, or a gNB misaligned after a RIC restart.

**Solution:**

```bash
./scripts/down_flexric.sh
pkill -f xapp_ 2>/dev/null || true
./scripts/up_flexric.sh
./scripts/down_gnb_oai.sh && ./scripts/up_gnb_oai.sh
```

### RC without INDICATIONs

- Subscribe **before** the attach: `./scripts/test_e2_rc_attach.sh`
- RC is **aperiodic** (RRC events); the UE attach triggers `RRCSetupComplete`

### KPM without metrics (zeros)

- Confirm the PDU session on slice 222/123
- Use `KPM_TRAFFIC=1` and check the ping to the DN
- Increase `XAPP_DURATION=60`

### `xapp_oran_moni` (/usr/local)

Do not use it for KPM in this lab — default SST=1 filter. Use `./scripts/test_e2_kpm.sh`.

---

## 11. Minimum reproduction sequence (checklist)

```bash
cd ric/code/oai-cn-gnb-e2

# Build (uma vez)
./scripts/build_e2.sh
./scripts/build_flexric_tools.sh

# Subir stack
./scripts/up_e2_lab.sh
sleep 30

# Testes
./scripts/test_e2_sm.sh cust          # custom SMs
./scripts/test_e2_rc_attach.sh        # RC + attach
./scripts/test_e2_kpm.sh              # KPM slice 222/123

# Inspecionar
grep -E 'Successfully subscribed|INDICATION|UEThp' logs/xapp_*.log
grep 'E2 SETUP RESPONSE' logs/gnb_oai.log

# Parar
./scripts/down_e2_lab.sh
```

---

## 12. Next steps (optional)

- Validate `xapp_kpm_rc` (KPM monitor + RC Control) with sustained traffic
- Increase test duration for KPM metric time series
- Integrate automatic log collection into a local CI pipeline

---

*Document generated based on the tests run in Jun/2026 on the development host of the `oai-cn-gnb-e2` project (RIC course / Cesar School).*
