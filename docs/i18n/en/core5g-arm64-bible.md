<!-- sync: e36a3f4e -->
> 🌐 **English** translation of the canonical Portuguese doc [`core5g-arm64-bible.md`](../../../core5g-arm64-bible.md). All languages: [INDEX](INDEX.md) · sync checked by `docs/i18n/check-parity.py`.

# Core5G ARM64 — Project Bible

A single, complete reference document. If you (or someone in the group) arrive
here with no context at all, this file should be enough to understand the what,
the why, and the how of everything that exists in this repository and on the
server.

For the step-by-step chronological history (the "logbook"), see
[`CHANGELOG.md`](../../../CHANGELOG.md). This document is the consolidated
snapshot of the current state + conceptual explanations.

---

## 1. Course context

- **Course 7: RAN Intelligent Controller (RIC)** — CESAR School specialization.
- **Professor:** Dr. Jonas Augusto Kunzler (`jak@cesar.school`).
- **Group (Group 6):** Henrique, Klinger, Kelvin, Gilberto.
- **Drawn topic (NGO §6.1):** **UE-TP-rApp** — per-UE throughput prediction
  (RSSI, RSRP, CQI, PRB, history).

### Two graded projects (40% each)

| Project | What | Where it is | Status |
|---|---|---|---|
| **Project 1** | Containerized Open5GS + UERANSIM (5G Core + simulated RAN) | `server/` (root of this repo) | ✅ Presented 13/06/2026 (Class 03). Validated end to end on the server. |
| **Project 2** | `oai-cn-gnb-e2` — OAI 5GC + gNB with E2 agent + FlexRIC (near-RT RIC) + xApps | `server/oai-cn-gnb-e2/` | ⏳ Pending. Presentation 20/06/2026 (Class 06, 08:00–11:00, 20 min/group, same order as Project 1). |

Project 2 deliverables (per the slide "Projeto 2 (40%) — roteiro e
prazos" of `pdfs/aula04-xapps_opensource.pdf`):
- Implement `oai-cn-gnb` per `server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md`.
- Technical report + demo (video/logs).
- Optional extension: custom xApp or A1/policy case.
- **Note:** the official rubric (`docs/avaliacao_seminario_aula06.md`) and the
  test plan (`docs/labs/04-projeto2-plano-testes.md`) cited in the
  slides **were not published** in the source repository
  (`jakunzler/cesar-school-repo`) at the time we checked — confirm with
  the professor before submission.

---

## Credits

Repository maintained by **Henrique Carmine** —
[henriquecarmine@gmail.com](mailto:henriquecarmine@gmail.com) ·
[@henriquecarmine](https://github.com/henriquecarmine).

---

## 2. How all this works, explained for non-technical readers

Think of the 5G network as a **delivery company** (like the postal service),
except that instead of letters it delivers **internet** to your phone. Each
Docker container below is a "department" of this company, running isolated from
the others.

### The path the phone travels (Project 1 — Open5GS)

| Who | Docker container | What it does, in one sentence |
|---|---|---|
| 📡 Antenna | `nr-gnb` (UERANSIM) | The cell tower (simulated) — it's how the phone talks to the network. |
| 📱 Phone | `nr-ue` (UERANSIM) | The (simulated) phone that turns on, registers, and asks to use the internet. |
| 🛎️ Doorman/reception | `amf` | First contact: receives the phone, checks who it is, and routes it to the right department. |
| 🔐 Security | `ausf` | Checks the phone's "password" — only lets through whoever actually owns the SIM. |
| 🗂️ Customer records | `udm` | Keeps each customer's profile: which plan they have, what they can access. |
| 🗄️ Database | `udr` + `mongodb` | The file/database where the registration data is actually stored. |
| 🚦 Rules inspector | `pcf` | Decides the rules of each connection: speed, priority, usage policy. |
| 📋 Bulletin board | `bsf` | Notes which inspector (`pcf`) is handling which connection, so other departments can find it later. |
| 🧭 Lane triage | `nssf` | Chooses which "lane"/queue (*slice*) that phone should travel in. |
| 🗺️ Logistics manager | `smf` | Organizes the "delivery route": sets up the data session the phone will use. |
| 🚚 Delivery truck | `upf-a` / `upf-b` | Actually carries the data (the internet) from one side to the other. Two trucks, one as backup. |
| 🌐 Final destination (test) | `dn` | A fake "outside world" just to simulate the real internet during tests. |
| ☎️ Internal phone directory | `nrf` | Every department registers here — that's how one department finds another's phone number. |
| 📞 Internal switchboard operator | `scp` | Relays the calls between departments (instead of each one calling the other directly). |
| 🖥️ Service desk | `webui` | Web screen where we register a new "customer" (subscriber) in the system. |

**Actual order when a phone turns on and asks for internet:**
1. The phone (`nr-ue`) spots the antenna (`nr-gnb`) and sends a signal.
2. `amf` receives it, checks who it is with the help of `ausf` (password) and `udm` (records).
3. `pcf` decides the rules of this connection and notifies the board (`bsf`).
4. `nssf` picks the right lane, `smf` builds the data route.
5. `upf-a`/`upf-b` (the truck) starts actually carrying data between the
   phone and the "outside world" (`dn`, or the real internet when applicable).

All of this is **standard 3GPP** — Open5GS (Project 1) and OAI (Project 2) are
two different "brands" of delivery company, but with the same departments.

### The control panel (not part of the 5G network, just for us to operate it)

| Container/process | Function, in one sentence |
|---|---|
| 🚪 Panel doorman | `caddy` — checks username and password at the site's entrance and only lets in whoever has a badge (login), plus keeps the connection encrypted (HTTPS). |
| 🖱️ Button office | `server/panel/server.py` (FastAPI/Uvicorn) — the one that actually presses the button to start/stop the network when you click on the screen. |

> Summary: the panel is just a remote control to start/stop/check the
> "delivery company" above — it is not part of the 5G network itself.

---

## 2.a For the telecom technician (someone who has worked with radio)

You know antennas, coverage, frequency, maybe you've configured a BTS or eNodeB
in the field. This section speaks your language — no delivery-company analogy,
no code, no byte-level protocol.

### What is running here, in radio terms

This project simulates a complete 5G cell inside an ARM server in the cloud.
There is no physical antenna, no real RF — but **all the signaling,
authentication, and data-transport logic is real**, running the same
protocols a carrier network uses.

**Project 1 radio parameters (UERANSIM):**

| Parameter | Value |
|---|---|
| Band | n78 (3.3–3.8 GHz) — the main 5G SA band in Brazil |
| Mode | TDD (Time Division Duplex) — DL and UL on the same frequency, separated in time |
| Bandwidth | 100 MHz |
| Numerology (SCS) | 30 kHz (µ=1) |
| Active PRBs | 66 (of 132 total for 100 MHz / 30 kHz) |
| Typical simulated RSRP | −79 dBm @ 100 m · −100 dBm @ 500 m · −111 dBm @ 1 km |
| Propagation model | 3GPP TR 38.901 UMa NLOS |
| Theoretical peak DL | ~665 Mbps (64-QAM, 4 MIMO layers) |
| Theoretical peak UL | ~250 Mbps |

> UERANSIM simulates the radio in software: the `uesimtun0` interface is the
> logical equivalent of the tunnel between the antenna and the UE. There is no
> IQ sample, no FPGA — but NAS, RRC, PDCP, and GTP-U are all actually executed.

### The containers — what each one is, in terms you know

If you've worked with 4G/LTE, you'll recognize most of them. 5G SA renamed and
reorganized the pieces, but the function is the same.

| Container | 4G / LTE equivalent | What it does |
|---|---|---|
| `nr-gnb` (UERANSIM) | eNodeB (eNB) | The (simulated) radio base station. Handles RRC, PRB scheduler, GTP-U with the core. |
| `nr-ue` (UERANSIM) | UE / phone | The (simulated) device. Does attach, PDU session, "measures" RSRP/RSRQ, runs iperf3. |
| `amf` | MME | Access control, authentication, registration, and UE mobility. |
| `smf` | SGW-C + PGW-C | Controls the data plane: defines the packet route, instructs the UPF via PFCP. |
| `upf-a` / `upf-b` | SGW-U + PGW-U | User plane. Receives GTP-U from the gNB (N3) and forwards to the internet (N6). |
| `ausf` | HSS (auth part) | Runs 5G-AKA — generates the authentication vector from the SIM's Ki and OPc. |
| `udm` | HSS (data part) | Subscriber profile: IMSI, plan, slice (S-NSSAI), MSISDN. |
| `udr` + `mongodb` | HSS (storage) | Subscriber database. The UDM reads from here. |
| `pcf` | PCRF | QoS policy: defines QFI, 5QI, per-session throttling rules. |
| `bsf` | (new in 5G SA) | Records which PCF is managing which session — avoids conflict when the AMF needs to locate the PCF of an active UE. |
| `nssf` | (new in 5G SA) | Network Slice Selection — decides which network slice (URLLC, eMBB, mMTC) the UE joins. |
| `nrf` | (new in 5G SA) | NF registry: each function registers here; others query it to find the address of whoever they need to call. |
| `scp` | (new in 5G SA) | SBI signaling proxy — centralizes the HTTP/2 calls between NFs. |
| `dn` | PDN-GW / internet | Destination data network. Here runs the iperf3 server that measures real throughput through the UE's tunnel. |

### How the channel simulation works (tc netem)

The panel has a "Channel Conditions" mode where you choose distance and
interference. There is no real radio — the panel injects
**Network Emulator (netem)** parameters into the `uesimtun0` interface via
`tc qdisc`:

```
tc qdisc replace dev uesimtun0 root netem delay <D>ms loss <L>%
```

The values are derived from the 3GPP TR 38.901 UMa NLOS model (path loss) and
from the SINR for each interference level:

| Condition | Approx. RSRP | Total delay | Total loss | Field equivalent |
|---|---|---|---|---|
| 100 m, no interference | −79 dBm | 1 ms | 0% | UE close to the tower, good line of sight |
| 500 m, weak interference | −100 dBm | 13 ms | ~3% | Good coverage, light co-channel (SINR ≈ 20 dB) |
| 1 km, medium interference | −111 dBm | 40 ms | ~12% | Cell edge (SINR ≈ 15 dB) |
| 3 km, high interference | −127 dBm | 100 ms | ~32% | UE in shadow, handover imminent (SINR ≈ 10 dB) |

### Differences between Project 1 (UERANSIM) and Project 2 (OAI + FlexRIC)

| Aspect | Project 1 — UERANSIM | Project 2 — OAI nr-softmodem |
|---|---|---|
| Radio layer | Simulated (NAS/RRC/GTP-U via socket, no real PHY) | RFSIM: real PHY in software, no RF hardware |
| PRB scheduler | Implemented in UERANSIM (fixed) | Real OAI scheduler (round-robin / proportional fair) |
| RIC interface | None — monolithic gNB, no E2 agent | Real E2 agent; connects to FlexRIC and exports per-UE KPIs |
| Accessible radio metrics | Internal logs only | DRB.UEThpDl/Ul, RRU.PrbTotDl/Ul, SINR via E2SM-KPM |
| Field analogy | Drive test: you only have NAS logs | BTS OMC: per-UE KPIs in real time, controllable via xApp |

> Project 1 is enough to validate core + attach. Project 2 is what a RIC
> integrator would need to commission xApps for PRB optimization, handover,
> or per-UE QoS.

---

## 2.b For the network engineer (O-RAN / 3GPP view)

If you know telecommunications but not this project's Docker/Linux environment,
this section maps each piece to its role in the O-RAN architecture and in
3GPP 5G SA.

### What O-RAN is and where this project fits

O-RAN (Open Radio Access Network) defines a disaggregated RAN architecture with
open interfaces. The functional split adopted by the O-RAN Alliance is
**Split 7.2x** (between PHY-Low and PHY-High), which separates the access node
into:

```
┌──────────────────────────────────────────────────────────────┐
│ SMO (Service Management & Orchestration)                     │
│  · Non-RT RIC: rApps, políticas A1, gerência O1              │
│  · Horizonte de controle: > 1 s                              │
└───────────────────────────┬──────────────────────────────────┘
                            │ A1 (políticas) / O1 (FCAPS)
┌───────────────────────────▼──────────────────────────────────┐
│ Near-RT RIC (near-Real-Time RIC)                             │
│  · xApps: E2SM-KPM (métricas), E2SM-RC (controle)            │
│  · Horizonte de controle: 10 ms – 1 s                        │
│  · Implementação deste projeto: FlexRIC (Projeto 2)          │
└───────────────────────────┬──────────────────────────────────┘
                            │ E2 (E2AP / E2SM)
┌───────────────────────────▼──────────────────────────────────┐
│ O-gNB (agente E2 embutido)                                   │
│  ┌─────────────┐  ┌─────────────┐   ┌──────────────────────┐ │
│  │  O-CU-CP    │  │  O-CU-UP    │   │       O-DU           │ │
│  │ RRC / PDCP-C│  │  PDCP-U     │   │  RLC / MAC / PHY-Hi  │ │
│  └──────┬──────┘  └────── ┬─────┘   └──────────┬───────────┘ │
│         │ F1-C            │ F1-U               │             │
│         └────────────────-┘                    │ Open FH     │
└─────────────────────────────────────────────── │ (7.2x) ─────┘
                                                 │
                                        ┌─────────▼────────┐
                                        │      O-RU        │
                                        │  PHY-Low / RF    │
                                        └──────────────────┘
```

**Relevant standardized interfaces:**

| Interface | Between | Protocol |
|---|---|---|
| E2 | Near-RT RIC ↔ O-gNB | E2AP over SCTP; E2SM-KPM/RC |
| A1 | Non-RT RIC ↔ Near-RT RIC | REST/JSON; ML/QoS policies |
| O1 | SMO ↔ all managed nodes | NETCONF/YANG |
| F1-C/U | O-CU ↔ O-DU | NG-AP + GTP-U (3GPP TS 38.473) |
| Open FH | O-DU ↔ O-RU | eCPRI over Ethernet (Split 7.2x) |
| N2 | O-CU-CP ↔ AMF | NGAP over SCTP |
| N3 | O-CU-UP ↔ UPF | GTP-U over UDP |
| N4 | SMF ↔ UPF | PFCP over UDP |

### How Project 1 (Open5GS + UERANSIM) fits

UERANSIM implements a **monolithic gNB** (no Split 7.2 — CU, DU, and RU are a
single process) and a **UE** that speaks NAS over the simulated stack. It is the
simplest 3GPP 5G SA reference without a Near-RT RIC.

```
UERANSIM nr-gnb  ──N2 (NGAP)──►  AMF   ─ CP 5GC
                 ──N3 (GTP-U)──►  UPF-A ─ UP 5GC (N6 → dn → internet)
UERANSIM nr-ue   ──NAS / RRC──►  (interno ao nr-gnb)
                                   └─► uesimtun0 (TUN 10.60.0.x)
```

There is no E2 agent or Near-RT RIC in Project 1. The throughput tests and the
simulated channel via `tc netem` on `uesimtun0` are the practical equivalent of
what would be measured via E2SM-KPM `DRB.UEThpDl/Ul` in an environment with a
real RIC.

### How Project 2 (OAI + FlexRIC) adds the Near-RT RIC

OAI `nr-softmodem` in RFSIM mode implements the full RAN stack (PHY/MAC/
RLC/PDCP/RRC) **with an embedded E2 agent** (the `openair2/E2AP/` library).
Split 7.2 is supported via F1/eCPRI, but in this project's environment it runs
in monolithic mode with RFSIM (radio 100% in software, no SDR hardware).

```
OAI nr-softmodem (RFSIM)
  ├── CU-CP: RRC, PDCP-C
  ├── CU-UP: PDCP-U
  ├── DU:    RLC, MAC, PHY-Hi (simulado)
  ├── RU:    PHY-Low (RFSIM — sem hardware)
  └── E2 Agent ──E2AP──► FlexRIC (Near-RT RIC)
                              ├── xApp KPM: subscreve DRB.UEThpDl/Ul
                              └── xApp RC:  controla parâmetros RRC
```

**KPMs relevant to the UE-TP-rApp topic (E2SM-KPM):**

| KPM | Description | Granularity |
|---|---|---|
| `DRB.UEThpDl` | DL throughput per DRB per UE (kbps) | per UE |
| `DRB.UEThpUl` | UL throughput per DRB per UE (kbps) | per UE |
| `RRU.PrbTotDl` | PRBs used in DL (%) | per cell |
| `RRU.PrbTotUl` | PRBs used in UL (%) | per cell |
| `L1M.RS-SINR` | SINR measured at the physical layer | per UE |

### Where each Docker container sits in the O-RAN model

| Container | O-RAN layer | Exposed interface |
|---|---|---|
| `nr-gnb` / `nr-ue` (UERANSIM) | O-gNB monolithic (no E2) + UE | N2, N3, NAS |
| OAI `nr-softmodem` (Proj.2) | O-gNB with E2 agent | N2, N3, E2 |
| `flexric` (Proj.2) | Near-RT RIC | E2, A1 |
| `amf` | 5GC CP — N2 termination | N2 (NGAP), N11 |
| `smf` | 5GC CP — session management | N4 (PFCP), N11 |
| `upf-a/b` | 5GC UP — user plane | N3 (GTP-U), N6 |
| `ausf` | 5GC CP — 5G-AKA auth | Nausf (SBI) |
| `udm` | 5GC CP — subscriber data | Nudm (SBI) |
| `udr` | 5GC CP — data repository | Nudr (SBI) |
| `pcf` | 5GC CP — policy (AM/SM) | Npcf (SBI) |
| `nrf` | 5GC CP — NF discovery | Nnrf (SBI) |
| `bsf` | 5GC CP — binding support | Nbsf (SBI) |
| `nssf` | 5GC CP — slice selection | Nnssf (SBI) |
| `scp` | 5GC CP — SBI proxy | SBI indirect |
| `mongodb` | Storage backend | — (Nudr internal) |

### NAS/RRC registration flow (from the protocol's point of view)

```
UE                  gNB              AMF          AUSF    UDM    SMF    UPF
 │───Registration Req──►│──NGAP Init UE──►│               │      │      │
 │                      │◄──Auth Req──────│──Auth Req────►│      │      │
 │                      │                 │◄──Auth Ans────│      │      │
 │◄──Auth Req───────────│◄──Auth Req──────│               │      │      │
 │──Auth Resp──────────►│──Auth Resp─────►│               │      │      │
 │                      │                 │──Get Sub Data───────►│      │
 │◄──Security Mode Cmd──│◄────────────────│               │      │      │
 │──Security Mode Cmp──►│────────────────►│               │      │      │
 │◄──Reg Accept─────────│◄────────────────│               │      │      │
 │──PDU Session Req────►│────────────────►│──────────────────────►SMF   │
 │                      │                 │                      │──N4──►UPF
 │◄─PDU Session Accept──│◄────────────────│◄─────────────────────│      │
 │ (uesimtun0 UP)       │                 │                      │      │
 │═════════GTP-U sobre N3══════════════════════════════════════════►    │ N6►internet
```

---

## 3. Repository structure

```
/
├── .env / .env.example        # credenciais de DEPLOY (host, SSH key, DuckDNS) — NUNCA vão pro servidor
├── deploy.sh                  # entrypoint único de deploy
├── core5g-arm64-bible.md      # este arquivo
├── CHANGELOG.md                # histórico cronológico de tudo que foi feito
├── infra/
│   ├── server-bootstrap.sh    # bootstrap idempotente do servidor (Docker, swap, DuckDNS, Caddy, painel)
│   └── core5g-panel.service   # unit systemd do painel server-side (template)
├── docs/
│   ├── labs/                  # guias de aula originais do curso (00–03, INDICE, video_seq_report)
│   └── blueprint-painel-observabilidade.md  # desenho do painel explicativo (não implementado)
├── pdfs/                      # slides das aulas (01–04) + planilha de grupos
├── ssl/
│   └── core5g_openran_arm64.pem   # chave SSH privada do servidor
├── client/                    # painel de controle web LOCAL (não roda no servidor)
│   ├── server.py              # backend FastAPI — só chama deploy.sh e streama saída
│   ├── static/index.html      # UI (HTML/CSS/JS puro, sem build step)
│   └── run.sh                 # cria venv, instala deps, sobe em :8765
└── server/                    # TUDO que é replicado/roda na máquina AWS
    ├── docker-compose.yml     # Projeto 1 (Open5GS) — name: open5gs-containerized fixo
    ├── .env / .env.example    # variáveis de IMAGEM do compose (sem segredos)
    ├── configs/open5gs/       # YAML de cada NF (amf.yaml, smf.yaml, bsf.yaml, ...)
    ├── scripts/                # up_core.sh, up_ran.sh, down.sh, healthcheck.sh, add-subscriber.sh, ...
    ├── overrides/
    ├── ueransim/               # docker-compose.yaml separado (gNB+UE simulados)
    ├── logs/                   # bind mounts de log por NF (gerado em runtime)
    ├── panel/                  # painel de controle web SERVER-SIDE (roda na própria AWS)
    │   ├── server.py           # backend FastAPI — chama scripts locais, sem SSH
    │   ├── static/index.html   # UI (igual ao client/, sem sync/sync-oai/bootstrap)
    │   ├── requirements.txt
    │   └── .venv/              # criado pelo bootstrap, não versionado
    └── oai-cn-gnb-e2/          # Projeto 2 — OAI 5GC + gNB + FlexRIC + xApps
```

### Why this separation

- **Root** = local orchestration tools (never run on the server).
- **`server/`** = exact mirror of what exists and runs on the AWS instance.
- **`docs/`** = pure documentation, without any executable/config file.
- The `.env` was deliberately **split in two**: the root one has
  `AWS_SERVER_HOST`/`AWS_SERVER_USER`/`AWS_SSH_KEY_PATH`/`DUCKDNS_DOMAIN`/`DUCKDNS_TOKEN`
  (only for `deploy.sh` to use locally); the `server/.env` one has only
  `OPEN5GS_IMAGE`/`WEBUI_IMAGE`/`MONGODB_IMAGE`/`UERANSIM_IMAGE`/`DN_IMAGE`
  (what the `docker-compose.yml` needs *on the server*). This way no access
  secret is sent to the server via `rsync`.

---

## 4. The server (AWS EC2 ARM)

| Item | Value |
|---|---|
| Hostname | `core5g-arm64.duckdns.org` (DDNS — public IP is dynamic) |
| Original IP (historical) | `3.145.40.200` — **never hardcode**, always use the hostname |
| User | `ubuntu` |
| SSH key | `ssl/core5g_openran_arm64.pem` (Ed25519) |
| Instance type | **AWS EC2 `t4g.medium`** (Graviton2 / Neoverse-N1, `aarch64`) — 2 vCPU / 4 GB. (It was `t4g.micro` at the start of the project; upgrade confirmed via `free` on 2026-06-22.) |
| AWS region | `us-east-2` |
| OS | Ubuntu 24.04.4 LTS (`noble`), kernel `6.17.0-1017-aws`, `aarch64` |
| CPU | 2 vCPUs — `Neoverse-N1` (ARM Graviton2) |
| RAM | ~3.8 GiB (3825 MiB measured — `t4g.medium`) |
| Swap | 8 GiB in `/swapfile`, `vm.swappiness=10`, persistent via `/etc/fstab` |
| Disk | ~29 GB total |
| Docker | `29.6.0` (`docker-ce`/`docker-ce-cli`/`containerd.io` packages, `arm64` architecture, official Docker repository) |
| Docker Compose | `v5.1.4` (plugin) |

### Costs and disk hygiene

Rules, values, and the CPU upgrade runbook (the AI RIC lab needs 4 vCPU) live in
[`docs/POLITICA-DE-CUSTOS.md`](../../POLITICA-DE-CUSTOS.md).
Permanent lessons from the 2026-07-03 cleanup (disk dropped to 8% free; back to
8.6 GB free):

- The P2 core's mysql created **an anonymous volume of ~197 MB per restart**
  (we found 16 orphans = 3.1 GB). Fixed at the root: named volume
  `mysql-data` in `oai-cn5g-v2/docker-compose-basic-nrf.yaml` — as a bonus, the
  UE registrations now persist across restarts.
- `docker volume prune -f` removes **only anonymous ones** (Docker ≥23) — the
  named ones (the students' MongoDB) stay. Even so: inspect before pruning.
- **Custom** OAI images (arm64 builds, ported `oai-upf-vpp`) are not
  re-pullable — **never** remove without a backup/review. The official v1.5.1 +
  `mysql:8.0` (legacy, ~2.6 GB) were removed after review on 2026-07-03.

### Manual access (debug only — prefer `./deploy.sh ssh`)

```bash
ssh -i ssl/core5g_openran_arm64.pem ubuntu@core5g-arm64.duckdns.org
```

### DuckDNS (dynamic IP)

- Domain: `core5g-arm64.duckdns.org`.
- Token: stored in `.env` (`DUCKDNS_TOKEN`) — not duplicated here.
- Script `~/duckdns/duck.sh` on the server + cron `*/5 * * * *` keeping the
  record updated. Reinstallable/idempotent via
  `./deploy.sh bootstrap`.

### Docker

Installed via the **official Docker repository** (not Ubuntu's `docker.io`
package): `docker-ce`, `docker-ce-cli`, `containerd.io`,
`docker-buildx-plugin`, `docker-compose-plugin`. User `ubuntu` in the
`docker` group. All encapsulated in `infra/server-bootstrap.sh`, idempotent.

---

## 5. The workflow: everything local, deploy via `deploy.sh`

**Golden rule:** never edit anything directly on the server via manual SSH. The
flow is always: edit files in `server/` (or `infra/`) locally →
`./deploy.sh <command>`.

```bash
./deploy.sh bootstrap          # instala Docker + swap + DuckDNS no servidor (idempotente)
./deploy.sh sync               # envia server/{docker-compose.yml,.env,configs,scripts,overrides,ueransim}
./deploy.sh sync-oai           # envia server/oai-cn-gnb-e2/ (~230MB, só quando precisar)
./deploy.sh up core             # sync + sobe só o core Open5GS
./deploy.sh up ran              # sync + sobe o RAN (UERANSIM)
./deploy.sh up all              # sync + sobe core + RAN
./deploy.sh down [core|ran|all]
./deploy.sh status              # docker compose ps + healthcheck.sh no servidor
./deploy.sh panel               # envia server/panel/ + roda bootstrap (Caddy + venv + systemd)
./deploy.sh ssh                 # sessão interativa (só debug)
```

`deploy.sh` reads `AWS_SERVER_HOST`/`AWS_SERVER_USER`/`AWS_SSH_KEY_PATH` from
the root `.env` — that's why there is never an IP/hostname hardcoded inside the
script.

### Visual panel (`client/`)

For those who prefer clicking a button instead of the terminal: a web panel that
runs **on your local workstation** (not on the server) with one button per
`deploy.sh` command and a console with real-time output.

```bash
cd client && ./run.sh        # cria venv, instala deps, sobe em http://127.0.0.1:8765
```

- The backend (`client/server.py`, FastAPI) only does `subprocess.Popen` of
  `deploy.sh` and streams stdout/stderr to the browser — no duplicated
  SSH/rsync logic, `deploy.sh` remains the single source of truth.
- The exposed commands are a fixed list (`bootstrap`, `sync`, `sync-oai`,
  `up`/`down core|ran|all`, `status`) — the backend does not accept a free-form
  string from the browser.
- Bind only on `127.0.0.1`, no authentication — assumes local development use,
  not network exposure.
- It's the first step of the larger panel described in
  `docs/blueprint-painel-observabilidade.md` (which envisions filterable logs
  and real-time protocol-flow visualization) — this version still only fires
  commands and shows the raw output, without parsing/filters.

### Web panel on the server (`server/panel/`), with HTTPS + login

A version of the panel accessible from anywhere (not just your workstation),
published at `https://core5g-arm64.duckdns.org/` with username/password.

- Runs **directly on the AWS instance** — `server/panel/server.py` (FastAPI)
  calls the local scripts (`./scripts/up.sh`, `up_ran.sh`, `down_core.sh`,
  `down_ran.sh`, `healthcheck.sh`) with no SSH involved. Bind only on
  `127.0.0.1:8765` — never exposed directly on the internet.
- **Automatic HTTPS via Caddy**: `infra/server-bootstrap.sh` installs
  Caddy (official Cloudsmith repository) and generates `/etc/caddy/Caddyfile` in
  front of the panel. Caddy obtains/renews on its own a **free Let's
  Encrypt certificate** for `core5g-arm64.duckdns.org` — there is no manual
  certificate to install. Only external requirement: ports **80**
  (ACME HTTP-01 challenge) and **443** (HTTPS) must be open in the instance's
  Security Group — **already open and validated** (HTTP 308 → HTTPS, HTTPS 401
  without credentials, 200 with login, 403 for the guest on `/api/run/*`).
- **Login with two roles**, via Caddy's own `basic_auth` (bcrypt hash
  generated with `caddy hash-password`, never a plaintext password on the server):
  - **admin** (`PANEL_USER`/`PANEL_PASSWORD` in the root `.env`): full
    access, runs any command.
  - **guest** (`PANEL_GUEST_USER`/`PANEL_GUEST_PASSWORD`): view only —
    `server.py` refuses with HTTP 403 any `POST /api/run/*` coming from this
    user (a backend check, not just a button hidden in the front-end). Caddy
    injects `header_up X-Remote-User {http.auth.user.id}` so FastAPI knows who
    authenticated.
- **Persistent process**: `infra/core5g-panel.service` (systemd,
  `Restart=always`, runs the venv's `uvicorn` in `server/panel/.venv`).
  Installed/updated by the bootstrap.
- **Deploy**: `./deploy.sh panel` syncs `server/panel/` and runs the
  bootstrap (idempotent) — the only way to update the panel or the
  credentials (never edit anything via manual SSH on the server, same golden
  rule from §5).
- **Real-time telemetry** (`GET /api/telemetry`): infinite stream
  (NDJSON, one JSON line every 2s) with host RAM/swap/disk/load (read
  from `/proc/meminfo` + `shutil.disk_usage` + `os.getloadavg()`,
  no new dependency) and per-container CPU%/RAM (`docker stats
  --no-stream --format '{{json .}}'`). Rendered in the UI as little bars +
  a collapsible table, without Prometheus/Grafana — the instance has only
  906 MiB of RAM, there's no room for a heavy observability stack on its side.
- **Per-service log filter** (`GET /api/logs/{service}`): the service list is
  discovered at runtime via `docker compose config --services`
  (in both compose files — core and `ueransim/`), then `docker compose
  logs -f --tail 200 <service>` is streamed to the UI console.
- **Telemetry and logs are allowed for the guest** (they are reads, not
  execution) — only `POST /api/run/*` returns 403 for this user.

---

## 6. Open5GS (Project 1) — what each service does

All the NFs (Network Functions) below are roles standardized by 3GPP.
Open5GS and OAI implement the same roles, just with different binaries.

| Service | Main interface | Role |
|---|---|---|
| `nrf` | internal SBI | core "DNS" — every NF registers here so the others can find it |
| `scp` | internal SBI | internal proxy between NFs (Service Communication Proxy) |
| `amf` | N1 (NAS) / N2 (NGAP) | the RAN's entry point — authenticates and moves the UE |
| `smf` | N4 (PFCP) / N11 | manages PDU sessions (the data "tunnels") |
| `upf-a` / `upf-b` | N3 (GTP-U) / N6 | the actual data plane — failover/load balancing between the two |
| `ausf` | internal SBI | runs the 5G-AKA authentication |
| `udm` | internal SBI | subscriber profile (slice, security keys) |
| `udr` | internal SBI | the database behind the UDM/PCF (MongoDB backend) |
| `pcf` | internal SBI (Npcf) | decides QoS/session-policy rules |
| `bsf` | internal SBI (Nbsf) | records the PCF↔session *binding* for discovery by other NFs (e.g., NEF/AF). **Item that was missing in the original project — see §8.** |
| `nssf` | internal SBI | picks the right slice (S-NSSAI) for the UE |
| `webui` | HTTP :9999 | Open5GS admin panel to register subscribers |
| `mongodb` | — | database (subscribers, etc.) |
| `dn` | N6 | fake "internet" (alpine) just so the UPF has somewhere to route/NAT to |

**Important teaching detail:** each docker network in `docker-compose.yml`
(`net-n2`, `net-n3`, `net-n4`, `net-n6`, `net-sbi`) corresponds 1:1 to a real
3GPP interface — filtering by network = filtering by interface.

### Simulated RAN (UERANSIM, in `server/ueransim/`)

- `nr-gnb`: simulates the base station — speaks N2/N3 with the core.
- `nr-ue`: simulates the phone — NAS registration, opens a PDU session, exposes
  the `uesimtun0` interface to test end-to-end connectivity.

---

## 7. OAI + FlexRIC (Project 2) — what each piece does

In `server/oai-cn-gnb-e2/`:

- **OAI 5GC** (`oai-cn5g-fed/`): the same NF roles as Open5GS, but
  packaged by OpenAirInterface, with a UPF in **VPP** (a faster dataplane)
  instead of the simple UPF.
- **OAI gNB** (`nr-softmodem`, **RFSIM** mode — radio 100% software): real PHY/MAC/
  RLC/PDCP/RRC (not simulated as in UERANSIM), with an **embedded E2 agent**
  that advertises "RAN functions" (KPM = metrics, RC = control, + custom L2/L3
  SMs) to the near-RT RIC.
- **FlexRIC** (near-RT RIC): receives the E2 SETUP from the gNB, registers the
  available RAN functions, routes SUBSCRIPTION/INDICATION/CONTROL between the
  gNB and the xApps.
- **xApps** (`xapp_kpm_moni`, `xapp_kpm_rc`): applications that actually
  consume metrics (KPM) or RRC events (RC) via E2 — the "smart side" of the RIC.

Bring-up flow documented in
`server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md`: Core → RIC → gNB → xApp.

### 7.a Project 1 vs. Project 2 — exactly how they differ

Both implement an end-to-end 5G network, but at opposite ends of the
"simple and validated" ↔ "complex and faithful to O-RAN" spectrum:

| Aspect | Project 1 (Open5GS + UERANSIM) | Project 2 (OAI + FlexRIC) |
|---|---|---|
| 5G Core | Open5GS (ready-made images, `gradiant/open5gs`) | OAI CN5G (`oai-cn5g-fed/`), UPF in VPP |
| RAN | UERANSIM — gNB/UE **simulated in software**, no real PHY/MAC | OAI gNB `nr-softmodem` in **RFSIM** — real PHY/MAC/RLC/PDCP/RRC, radio 100% software (no RF hardware) |
| External control layer (RIC) | **Does not exist** — monolithic network, no data/control separation | **FlexRIC** (near-RT RIC) connected to the gNB via E2AP (port 36421) |
| Intelligence/observability | Panel scripts (`tc netem`, `iperf3`) simulate the channel/measure bandwidth from the outside | **xApps** (`xapp_kpm_moni`, `xapp_kpm_rc`) consume metrics/control the gNB from within the architecture, via standardized E2 Service Models (KPM v2.03, RC v1.03) + custom SMs (MAC/RLC/PDCP/GTP) |
| 3GPP/O-RAN concept illustrated | NAS registration, PDU session, QoS, UPF failover — "the 5G network works" | **CU/DU/RIC** separation, *programmable RAN*: the RIC can observe (KPM) and act (RC) on the gNB in near-real time — the central concept of Open RAN |
| Build complexity | Ready-made Docker images, just `docker compose up` | Native C/C++ build from source (`build_oai`, FlexRIC), heavy on CPU/RAM/disk — there is no ready-made image for ARM64 |
| State on 2026-06-18 | Complete, validated E2E (§9), already presented | From-scratch build in progress on the server (see `CHANGELOG.md` v0.8.0) — nothing was functional before that, despite appearances of earlier progress |

In one sentence: **Project 1** proves that a basic 5G network works end
to end; **Project 2** adds the layer of **intelligent, programmable
RAN** (RIC + xApps speaking E2 with the gNB) that is the very
definition of O-RAN — and it is technically heavier because there is no
ready-made Docker image: everything is compiled from source, native
`aarch64`.

### 7.b Building the OAI 5G Core images for arm64

The OAI 5G Core Docker images (`oaisoftwarealliance/oai-{amf,smf,nrf,udr,udm,ausf,upf-vpp}:v1.5.1`) on Docker Hub are **amd64-only** — there is no `linux/arm64/v8` variant. The AWS t4g.micro server (Graviton2, `aarch64`) has no QEMU/binfmt-misc configured, so any attempt to run these images fails with `exec /usr/bin/python3: exec format error` and the container exits with code 255.

#### Strategy adopted

Build natively for arm64 on Mac Apple Silicon (Docker Desktop with the `linux/arm64` engine), export as `.tar`, transfer via `scp`, and load on the server with `docker load`. The Dockerfiles are vendored in the repository at `server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-*/docker/Dockerfile.*.ubuntu`.

Script: [`build-oai-arm64.sh`](../../../build-oai-arm64.sh) at the root of the repository.

```bash
./build-oai-arm64.sh build    # compila as 6 imagens localmente no Mac
./build-oai-arm64.sh save     # exporta para /tmp/oai-images/*.tar
./build-oai-arm64.sh upload   # scp dos .tar para o servidor
./build-oai-arm64.sh load     # docker load no servidor + rm dos .tar
./build-oai-arm64.sh all      # executa os 4 passos em sequência
```

#### Prerequisites

| Requirement | Detail |
|---|---|
| Machine | Mac Apple Silicon (M1/M2/M3/M4) — native arm64 |
| Docker Desktop | ≥ 4.x with the `linux/arm64` engine enabled |
| Disk space | ≥ 20 GB free (intermediate images + exported .tar) |
| Time | ~40 min per image × 6 = ~4 h total |
| SSH key | `ssl/core5g_openran_arm64.pem` with access to the server |
| `.env` | configured with `AWS_SERVER_HOST`, `AWS_SERVER_USER`, `AWS_SSH_KEY_PATH` |

> **Why Mac Apple Silicon?** Docker Desktop on M-series runs `linux/arm64` containers _natively_ — without QEMU emulation. Compiling OAI (heavy C++) via emulation would take 5–10× longer and frequently hangs from OOM.

#### How to compile — step by step

**1. Clone the repository and configure the .env**

```bash
git clone https://github.com/henriquecarmine/Core5G_ARM64.git
cd Core5G_ARM64
cp .env.example .env
# editar .env: AWS_SERVER_HOST, AWS_SERVER_USER, AWS_SSH_KEY_PATH
```

**2. Compile the 6 images**

```bash
./build-oai-arm64.sh build
# Cada docker build compila o OAI a partir do source dentro do container arm64.
# A ordem importa: AMF → SMF → NRF → UDR → UDM → AUSF
# Cache Docker é reutilizado em recompilações parciais.
```

What happens inside each build (multi-stage Dockerfile):
1. **base stage** — `apt-get install` of the system dependencies + build tools
2. **base stage** — compilation of spdlog, Pistache, nlohmann/json, and nghttp2 from git
3. **builder stage** — `cmake` configures the project + `make -j$(nproc)` compiles the binary
4. **target stage** — copies only the binary and `.so` needed for the minimal final image

**3. Export to .tar**

```bash
./build-oai-arm64.sh save
# Cria /tmp/oai-images/oai-{amf,smf,nrf,udr,udm,ausf}.tar (~60 MB cada)
```

**4. Send to the server**

```bash
./build-oai-arm64.sh upload
# scp de cada .tar para ~/ no servidor via SSH
```

**5. Load into the server's Docker daemon**

```bash
./build-oai-arm64.sh load
# docker load -i ~/oai-{comp}.tar && rm ~/oai-{comp}.tar  (para cada componente)
```

**Or all at once:**

```bash
./build-oai-arm64.sh all
```

**Verify that the images are really arm64:**

```bash
# no servidor:
docker run --rm oaisoftwarealliance/oai-amf:v1.5.1 uname -m
# esperado: aarch64
```

#### Build parameters

| Parameter | Value |
|---|---|
| `--platform` | `linux/arm64` |
| `--build-arg BASE_IMAGE` | `ubuntu:focal` (see §8.5) |
| `--target` | component name (e.g., `oai-amf`) |
| `-f` | `component/<comp>/docker/Dockerfile.<shortname>.ubuntu` |
| context | component directory (e.g., `component/oai-amf/`) |

#### Problems encountered — and how they were fixed

These are the errors that show up when trying to compile the OAI images for arm64 **from the repository's original code**. The patches are already applied in this repo; this section exists to document the reasoning and to help anyone trying to do the same on another code base.

**Bug 1 — `declare -A` not supported in macOS's bash 3.2**

macOS 14/15 ships with bash 3.2 (a GPLv2 licensing limitation). The original script used `declare -A COMPONENTS=(...)` (bash 4+), causing `oai: unbound variable` at runtime.

Fix: replaced with a simple string iterated with `for comp in $COMPONENTS`:
```bash
COMPONENTS="oai-amf oai-smf oai-nrf oai-udr oai-udm oai-ausf"
# oai-upf-vpp excluído: requer libhyperscan (Intel-only, inexistente no arm64)
for comp in $COMPONENTS; do ...
```

**Bug 2 — Wrong Dockerfile name**

The Dockerfile is named `Dockerfile.amf.ubuntu` (without the `oai-` prefix), not `Dockerfile.oai-amf.ubuntu`. The script generated the wrong name, causing "Dockerfile not found" for all 7 components.

Fix: added `shortname="${comp#oai-}"` to strip the prefix before building the path:
```bash
shortname="${comp#oai-}"   # oai-amf → amf
dockerfile="$ctx/docker/Dockerfile.${shortname}.ubuntu"
```

**Bug 3 — `libboost1.67-dev` not available in Ubuntu 18.04's arm64 repository**

The `build_helper.amf` (and each component's equivalent) for `ubuntu18.04` adds the `ppa:mhier/libboost-latest` PPA and installs `libboost1.67-dev`. This PPA does not publish arm64 packages — `apt-get install` fails with `E: Unable to locate package libboost1.67-dev`, and the build aborts with "AMF deps installation failed".

Fix: pass `--build-arg BASE_IMAGE=ubuntu:focal`. Ubuntu 20.04 has Boost 1.71 in the standard repositories; `build_helper` has a specific `ubuntu20.04` case that installs `libboost-all-dev` directly, without a PPA. The Dockerfile explicitly supports bionic, focal, and jammy — using focal is the supported path.

**Bug 4 — `-msse4.2` hardcoded in every component's CMakeLists.txt**

After resolving Bug 3, the compilation fails with `cc: error: unrecognized command line option '-msse4.2'`. The architecture-detection block in each `src/*/CMakeLists.txt` has:

```cmake
if (CMAKE_SYSTEM_PROCESSOR STREQUAL "armv7l")
  set(C_FLAGS_PROCESSOR "-gdwarf-2 -mfloat-abi=hard -mfpu=neon -lgcc -lrt")
else (CMAKE_SYSTEM_PROCESSOR STREQUAL "armv7l")  # ← else genérico
  set(C_FLAGS_PROCESSOR "-msse4.2")              # ← flag x86 SSE4.2
endif()
```

In the `linux/arm64` build, `CMAKE_SYSTEM_PROCESSOR` is `aarch64` — it falls into the `else` and tries to compile with `-msse4.2` (an x86 SIMD instruction that does not exist on ARM).

Fix applied to the 5 affected components (`oai-amf`, `oai-smf`, `oai-nrf`, `oai-udr`, `oai-udm`, `oai-ausf`):

```cmake
if (CMAKE_SYSTEM_PROCESSOR STREQUAL "armv7l")
  set(C_FLAGS_PROCESSOR "-gdwarf-2 -mfloat-abi=hard -mfpu=neon -lgcc -lrt")
elseif (CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|arm64")
  set(C_FLAGS_PROCESSOR "")   # ← ARM64 nativo, sem flags arquitetura-específicas
else()
  set(C_FLAGS_PROCESSOR "-msse4.2")
endif()
```

`oai-upf-vpp` uses VPP with its own build system and does not have that flag.

**Bug 5 — invalid `libasan2` in `build_helper.udm` silences the entire `apt-get`**

The `build_helper.udm` had `libasan2` in the ubuntu `PACKAGE_LIST` (a line not present in the other components). `libasan2` does not exist on Ubuntu 20.04 arm64 (`libasan5` is the correct version, already included in `specific_packages`). The whole `apt-get install -y` fails with `E: Unable to locate package libasan2` — but the error is silenced because the subsequent `ret=$?` captures the exit code of the `if/case` block (which returns 0 for ubuntu20.04), not of `apt-get`. Result: none of the `PACKAGE_LIST` packages are installed, including `libconfig++-dev`. cmake then fails with `None of the required 'libconfig++' found`.

Fix: remove the `libasan2` line (and the generic `libasan`, which also does not exist) from the ubuntu `PACKAGE_LIST` in `build_helper.udm`. `libasan5` is already in `specific_packages` for ubuntu20.04.

Affected file: `server/.../oai-udm/build/scripts/build_helper.udm`

**`oai-upf-vpp` on arm64 — RESOLVED with Vectorscan (2026-06-21)**

For a long time `oai-upf-vpp` was considered "not portable" to arm64. The
real diagnosis, after investigating the source: the blocker was **a single dependency**
— **Hyperscan** (`libhyperscan-dev`), Intel's SIMD regex library
(SSE/AVX), nonexistent on Ubuntu arm64. Travelping's UPF plugin requires it via
`pkg_check_modules(HS libhs)` (pure pkg-config).

The solution: **[Vectorscan](https://github.com/VectorCamp/vectorscan)** is a portable
fork of Hyperscan — 100% functional ARM NEON, **API/ABI-compatible**, same
`libhs.so.5` SONAME. It is **drop-in**: by compiling and installing Vectorscan, the
`pkg_check_modules(HS libhs)` finds it and the GTP UPF is enabled normally
(`Found libhs, version 5.4.12`). The other "blockers" mentioned earlier did not
hold up — VPP 2101 **core does not use hyperscan**, and the lib paths were already
fixed to `aarch64-linux-gnu` in the Dockerfile.

Porting steps (in [`docker/Dockerfile.upf-vpp.ubuntu.arm64`](../../../server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-upf-vpp/docker/Dockerfile.upf-vpp.ubuntu.arm64)):
1. Base `ubuntu:focal` (gcc-9; Vectorscan requires C++17/gcc≥9) + a recent `cmake`
   via pip (focal has 3.16; Vectorscan asks for ≥3.18.4).
2. Compile Vectorscan removing `-Werror` (gcc-9 gives a false positive in
   `state_compress.c` + the `-Wno-stringop-overread` flag only exists in gcc-11) and
   turning off the extras (`BUILD_UNIT/TOOLS/EXAMPLES/BENCHMARKS/DOC=OFF`).
3. `sed` removing `dh-systemd` from VPP's `DEB_DEPENDS` (a bionic-only package that
   breaks `make install-dep` on focal; only used to package `.deb`).
4. `sed` forcing `https://github.com` in the URLs of VPP's external packages
   (`rdma-core` was downloading via `http://github.com:80` → "connection refused").
5. Copy `libhs.so.5` (Vectorscan) into the final image.

Validated result: `vpp` ELF **ARM aarch64**, `upf_plugin.so` resolves
`libhs.so.5`. **Runtime validated** (docker `--privileged` + hugepages): VPP
boots fully and the plugin responds — `show plugins` lists `upf_plugin.so
21.01.1`, `show upf specification release` → `PFCP version: 15`. The abort that
appeared in `flowtable_init` **was not a porting defect**: it was the `main-heap`
backed by hugepages without enough pages; with `main-heap-page-size 4k`
(or properly sized hugepages) it comes up fine. **Operational gotcha for anyone deploying:**
do not back the main-heap with more hugepages than the host has free — use 4k or
reserve enough hugepages (heap + buffers). Image at
`artifacts/oai-images/oai-upf-vpp.tar` (~138 MB).

**Validation on the real Graviton (AWS server, 2026-06-22).** Image loaded on the
server (`docker load`, arch=arm64) and run standalone with the box **idle**
(`--cpus=1.5`, heap 2G/4k). **Event-driven** test (readiness by state: CLI socket
exists OR the process dies — no fixed sleep/timeout) with **real metrics**:

| Check | Value measured on the Graviton |
|---|---|
| `docker stats` | cpu 2.23% · mem 1.41 GiB / 3.74 GiB (37.8%) · 1 pid |
| `show version` | `vpp v21.01.1` (ARM) |
| `show plugins` | `upf_plugin.so 21.01.1` |
| `show upf specification release` | `PFCP version: 15` |
| `show memory main-heap` | total 1.99G · **used 1.08G** · free 938M |
| `show buffers` | pool `default-numa-0` 17,240 buffers |
| `upf_plugin.so` | links against `libhs.so.5` (vectorscan) |

The **real heap usage (1.08 GB)** explains why 1G fails and 2G suffices: the plugin's
flowtable pre-allocates ~1 GB (a compile-time default, with no `init.conf` sizing it).
The container **self-terminated** and was removed; host load 0.3 → 1.0 (trivial).

> **Lesson learned (recorded so as not to repeat it):** running VPP on the box **while the
> P2 lab is active** (load ~30 on the 2 vCPUs) with a harness that **does not
> self-terminate** choked `sshd` and required a reboot. Rule: VPP tests on the server
> only with the box **idle**, container **`--rm` + self-terminating**, and wait for
> **state/event** (never a blind timeout). See [[feedback-event-driven-nao-tempo]].

Only the **full E2E** is missing (SMF PFCP session + gNB GTP-U + UE traffic),
which requires the whole core+RAN and a window with no class — and the lab does not depend on it.

> The main lab still uses the Open5GS UPF (`open5gs-upfd`, P1) and the
> `oai-upf` simple_switch (P2, core v2.2.1) — it does not depend on this image. The port
> exists on the Open RAN principle ("all O-RAN technology must be open") and is
> a candidate for an upstream report to OAI.

#### Result — builds completed on 2026-06-19

Compilation done on Mac Apple Silicon (M-series) via Docker Desktop `linux/arm64`. Total time: ~40 min per image (base stage + build from source + cmake + make). Images loaded on the AWS t4g.micro server (Graviton2, Ohio) and verified with `uname -m → aarch64`.

| Image                         | Tag    | Size    | Build SHA (digest)                                        |
|-------------------------------|--------|---------|-----------------------------------------------------------|
| oaisoftwarealliance/oai-amf   | v1.5.1 | 280 MB  | `sha256:404e88009215...` |
| oaisoftwarealliance/oai-smf   | v1.5.1 | 260 MB  | `sha256:90d5058e53c6...` |
| oaisoftwarealliance/oai-nrf   | v1.5.1 | 264 MB  | `sha256:49528805e9ae...` |
| oaisoftwarealliance/oai-udr   | v1.5.1 | 268 MB  | `sha256:3d2cab6d1063...` |
| oaisoftwarealliance/oai-udm   | v1.5.1 | 257 MB  | `sha256:f49f777b6d06...` |
| oaisoftwarealliance/oai-ausf  | v1.5.1 | 255 MB  | `sha256:e7a98d7f0ee8...` |

#### Where the files are

**AWS server** (final destination):
```
# Imagens já carregadas no daemon Docker — prontas para uso:
docker images | grep oaisoftwarealliance
```

**Project Google Drive** (permanent copy of the `.tar` files):
```
PROJETOS/Core5G_ARM64/artifacts/oai-images/
├── oai-amf.tar    (63 MB)
├── oai-smf.tar    (60 MB)
├── oai-nrf.tar    (60 MB)
├── oai-udr.tar    (61 MB)
├── oai-udm.tar    (59 MB)
└── oai-ausf.tar   (59 MB)
# total: ~362 MB  — não versionados no git, ficam no Drive
```

To load on any arm64 host without recompiling:
```bash
# copiar do Drive para o servidor e carregar:
scp -i sua-chave.pem artifacts/oai-images/oai-amf.tar ubuntu@<servidor>:~/
ssh -i sua-chave.pem ubuntu@<servidor> "docker load -i ~/oai-amf.tar && rm ~/oai-amf.tar"
# repetir para cada componente
```

To export directly from the lab server (if you have SSH access):
```bash
ssh ubuntu@core5g-arm64.duckdns.org "docker save oaisoftwarealliance/oai-amf:v1.5.1 -o ~/oai-amf.tar"
scp ubuntu@core5g-arm64.duckdns.org:~/oai-amf.tar .
docker load -i oai-amf.tar
```

> Full download guide (without compiling): [`OAI-CORE-ARM64.md §Download`](../../../server/oai-cn-gnb-e2/docs/OAI-CORE-ARM64.md)

To recompile from scratch (requires Mac Apple Silicon + Docker Desktop):
```bash
git clone https://github.com/henriquecarmine/Core5G_ARM64.git
cd Core5G_ARM64
cp .env.example .env   # preencher AWS_SERVER_HOST e AWS_SSH_KEY_PATH
./build-oai-arm64.sh build   # ~4 h total para os 6 componentes
./build-oai-arm64.sh save    # exporta para /tmp/oai-images/
./build-oai-arm64.sh upload  # scp para o servidor
./build-oai-arm64.sh load    # docker load no servidor
```

**Dockerfiles** with all arm64 patches applied:
```
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/docker/Dockerfile.<comp>.ubuntu
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/build/scripts/build_helper.<comp>
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/src/*/CMakeLists.txt
```

---

### 7.c User plane on arm64 (OAI v2.2.1) + event-driven xApps

> **Why this section exists.** The v1.5.1 core we built (§7.b) **had no UPF
> on arm64** (`oai-upf-vpp` is Intel-only, depends on `libhyperscan`). In practice
> Project 2 only had a **control** plane — the UE never got an IP. OAI started
> publishing **official multi-arch images** from `v2.1.10` on; **`v2.2.1`** has
> **7/7 NFs with arm64**, including `oai-upf` (`simple_switch` datapath). We migrated to
> it and the **user plane started working** (the UE gets IP `12.1.1.x`, real traffic).

**Where it lives:** `server/oai-cn-gnb-e2/oai-cn5g-v2/` (parallel to v1.5.1, does not replace it).
Config details in [`oai-cn5g-v2/README.md`](../../../server/oai-cn-gnb-e2/oai-cn5g-v2/README.md).
Matches the current gNB: PLMN **208/95**, TAC `0xa000`, slice **SST 222 / SD 123**,
DNN **default** (pool `12.1.1.0/26`), fixed AMF `192.168.70.132`, SNAT on the UPF (UE → internet).

**Bring up the full Project 2 (over SSH):**
```bash
cd server/oai-cn-gnb-e2
./oai-cn5g-v2/up_core_v2.sh    # para o Projeto 1, sobe o core v2.2.1, espera oai-amf RUNNING
./scripts/up_e2_lab_v2.sh      # near-RT RIC + gNB (RFSIM, 24 PRBs / 51 NRB) + nrUE
```

**Run xApps — event-driven, no blind timeout:**
```bash
./scripts/run_xapp.sh cust    # xApp MAC/RLC/PDCP/GTP (SM custom)
./scripts/run_xapp.sh kpm     # E2SM-KPM (métricas DRB/PRB)
./scripts/run_xapp.sh rc      # E2SM-RC (controle)
./scripts/e2_verify.sh        # sobe o lab + valida E2 SETUP + roda os 3 xApps 7x cada
```
Each `run_xapp.sh` **stops on the 1st success event** (E2 connected + subscribed/indication),
never by fixed duration — deterministic. The prerequisite is checked by **state** (`pgrep -x
nearRT-RIC` + `nr-softmodem`), not by `sleep`. CPU under control: a cgroup with `CPUQuota`
(`XAPP_CPU_QUOTA`, default `50%`) + `nice`.

#### xApp validation (real result) and the 2 bugs in the way

Running `e2_verify.sh` (brings up the lab without a UE + 3 xApps 7× each): **cust 7/7, kpm 7/7, rc 5/7**
— the xApps connect to the RIC and **subscribe** to the RAN functions (`Successfully subscribed to
RAN_FUNC_ID …`). Before reaching this result, two bugs (which were NOT "lack of CPU", as
it seemed at first) had to be fixed:

1. **SM plugins of the wrong architecture (RIC crash).** The repo versioned
   `flexric-lib/*.so` compiled for **x86-64**; on an **arm64** host the `dlopen` of
   `nearRT-RIC` fails (`load_plugin_ric: Assertion handle != NULL`). Worse: `sync-oai`
   spread these x86-64 files on top of the arm64 ones the server had built. **Fix:**
   the `.so` files left git (they are build artifacts, arch-specific; see `.gitignore`) and
   `up_flexric.sh` now **detects the architecture** and repopulates `flexric-lib/` from the build tree
   (`sync_flexric_lib.sh`) when it is missing OR from another arch. Self-healing.

2. **False negative in `run_xapp.sh`.** It used `tail -F --pid | grep -m1` with
   `set -o pipefail`: when `grep -m1` matches the success event and closes the pipe, `tail`
   dies with SIGPIPE and `pipefail` marked the whole pipeline as failed — reporting
   `❌ FALHA` even with the xApp subscribed. **Fix:** replaced with a **file poll**
   (`grep -q` in a loop until the event OR the process dies), no pipe, no SIGPIPE.

#### Operational constraint of the box (2 vCPUs)

`nr-softmodem` and `nr-uesoftmodem` in RFSIM **busy-poll** (each saturates ~1 vCPU →
load > 20), and then the RIC's INDICATION→Report path can blow past FlexRIC's internal timeout. That's
why the validation comes up **without the nrUE** (`SKIP_UE=1`, default in `e2_verify.sh`):
E2 is gNB↔RIC and does not depend on the UE, and a whole vCPU is left for the RIC+xApp (load < 2). For the
full lab WITH user plane, bring it up normally (`SKIP_UE=0`) — but don't run the 7× xApp batch at the same time.

**Measurement on the server (2026-06-22) — the UE attach is mutually exclusive with the cpuset
guardrail.** With the guardrail active (`oai-lab.slice AllowedCPUs=1` = the whole lab on a single
core), the nrUE **synchronizes** (PHY/RFSIM ok: `Initial sync successful, PCI 0`, RSRP 51 dB)
but the **RRC floods** (`TASK_RRC_NRUE task contains` 71k→112k) and the UE **gets no IP**: the gNB
(CPUWeight 60) gets ~40% of the core and the nrUE (CPUWeight 20) only ~25% — insufficient for
real-time RRC. Releasing the **2 cores** (`AllowedCPUs=0-1`), each RFSIM process gets ~1
core and the **user plane actually works**: the UE attaches, `oaitun_ue1=12.1.1.2`, and
`ping 8.8.8.8` over the tun gives **4/4, 0% loss, RTT ~111 ms**. In other words, what §7.c states
(the UE gets IP `12.1.1.x`) **is confirmed — but it requires the 2 cores**, which reopens the freeze
risk the guardrail prevents. Trade-off: **either** anti-freeze protection (1 core, no UE),
**or** a full user plane (2 cores, dedicated box). The test was done **without a timer**: cpuset revert
via `trap EXIT` + wait for an event (`ip monitor` for the IP, `tail -F --pid|grep -m1`
for the flood) + a monitor at `nice -20` (guarantees the revert even under saturation).

> **Recommendation for anyone bringing up a new instance:** use **4 vCPU** (e.g., `t4g.xlarge`
> or `c7g.xlarge`). With 4 cores — gNB on one, UE on another, RIC+xApp on another, the system on another — the
> full lab **with user plane** runs without cpuset, without a guardrail, and with no freeze risk, and the
> xApps run in parallel with the UE (essential for the UE-TP-rApp). The 2 vCPU are the **alternative
> path** (trade-off above). Full reproduction guide up to the user plane, with both
> paths: [`server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md`](../../../server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md).

> **Project principle: ZERO time, everything under control.** No blind `sleep`/timeout —
> the scripts finish by **event/state** (`grep -m1` on a stream, `tail -F --pid`, condition
> polling). See the `feedback-event-driven-nao-tempo` memory.

---

## 8. Real bugs found and fixed

These problems existed in the original course material and were discovered
by actually testing on the ARM server — kept here so they don't get lost.

### 8.1 — `gradiant/open5gs` images without an arm64 build

`gradiant/open5gs:2.7.6` and `gradiant/open5gs-webui:2.7.6` **have no**
`linux/arm64/v8` manifest — from tag `2.7.3` on, gradiant only publishes
`amd64`. `docker compose up` was failing with
`no matching manifest for linux/arm64/v8`.

**Fix:** pin in `server/.env`:
```
OPEN5GS_IMAGE=gradiant/open5gs:2.7.2
WEBUI_IMAGE=gradiant/open5gs-webui:2.7.2
```
(`2.7.0`, `2.7.1`, and `2.7.2` are the last tags with an arm64 build confirmed
via the Docker Hub API. `mongo:7.0` and `gradiant/ueransim:3.2.6` were already
arm64-ok, no change needed.)

### 8.2 — Missing BSF service (PDU Session always rejected)

After the core came up 100% healthy, the UE would register (NAS OK) but the PDU
session always failed with `PDU Session Establishment Reject [OUT_OF_LADN_SERVICE_AREA]`.

Root cause (found in the PCF log, not the UE's): `No http.location` in
`nbsf-handler.c:436` — the PCF tries to register the session *binding* in the
**BSF** via NRF, but:
1. **There was no `bsf` service in `docker-compose.yml`** (even though the
   `open5gs-bsfd` binary exists in the image).
2. There already was a `configs/open5gs/bsf.yaml` in the original project, but with the
   **default example** address (`127.0.0.15`), outside the project's real
   network scheme (`10.10.0.x` on `net-sbi`).

In other words: an item forgotten in the original course configuration, not caused by the
image-version change (§8.1).

**Fix:**
- `server/configs/open5gs/bsf.yaml`: address corrected to `10.10.0.18`
  (next free IP), `scp` client pointed to `10.10.0.200:7777`.
- `server/docker-compose.yml`: new `bsf` service added (same pattern
  as `nssf`), container `open5gs-bsf-containerized`.

After bringing up the BSF, a second transient error still appeared
(`Registration reject [95]` / `amf_npcf_am_policy_control_handle_create()
failed`) — orphaned state from earlier session attempts. Resolved with a
clean restart of `amf`, `smf`, `pcf`, `bsf` (and the other core NFs).

### 8.3 — Compose project name not pinned (risk of losing data when moving folders)

`docker-compose.yml` had no explicit top-level `name:`. The **networks**
(`net-n2`, `net-n3`, etc.) already had a fixed `name:` individually, but the
Mongo **named volumes** (`mongodb-data`, `mongodb-config`) did not — their
name is derived from the name of the directory where `docker compose` is
run. When reorganizing the repo (moving from `open5gs-containerized/` to
`server/`), this would have recreated the volumes from scratch, **losing the
registered subscriber**.

**Fix:** added `name: open5gs-containerized` at the top of
`docker-compose.yml` — any future folder/run directory keeps
the same volumes/networks/containers.

> Worth considering reporting bugs 7.1–7.3 to the professor — other groups
> using the same original material probably hit the same errors.

### 8.4 — The panel's venv ended up without `pip` (idempotency check confused by partial state)

In the `server/panel/` bootstrap, the venv-creation step checked
`[ ! -x ~/server/panel/.venv/bin/python3 ]` to decide whether to recreate it. On a
first attempt, `python3-venv` was not yet installed when the
`python3 -m venv` ran — `ensurepip` failed, but the venv was left partially
created (only the `python3` symlinks, without `pip`/`activate`). On the next
run, the `python3` symlink already existed and *was* executable, so the idempotency
check thought the venv was fine and skipped recreation — leaving
`pip install` to fail with "No such file or directory".

**Fix:** always install `python3-venv`/`python3-pip` (via `apt-get
install`, which is idempotent by nature) before checking/recreating the venv,
instead of trying to infer whether the package is already installed.

### 8.5 — Reports with false negatives (container name ≠ Compose service)

Discovered by **running the reports live** (not with `bash -n`), v0.25.2. These are
bugs in our diagnostic layer, not in the original material — but they would mislead the
professor, so they're worth recording:

- **`test_ng_setup` / `test_registration` said "AMF is not running"** with the
  AMF perfectly up. Cause: the scripts ran `docker inspect amf`, but
  `amf` is the name of the **Compose service** — the **container** is named
  `open5gs-amf-containerized`. `docker inspect`/`exec`/`logs` require the
  **container** name; only `docker compose logs` accepts the **service** name. The
  `inspect` failed → the cross-check with the AMF became a warning → `test_ng_setup`
  concluded *"N2 not confirmed"* **even with `NGSetupResponse` received**.
- **`test_ue_connection` showed `public IP <!DOCTYPE html>`.** `wget
  http://ifconfig.me` returns the **HTML page**, not the IP. Fixed to
  `http://ifconfig.me/ip` (plain text) + IP extraction/validation by regex.
- **Final verdict always "ok".** `test_ue_connection` ended in `summary ...
  ok` regardless of the checks. Rewritten with `fails`/`warns` counters
  and an honest verdict (✗ critical / ! caveat / ✓ all passed).

**Lesson:** `bash -n` validates syntax, not semantics. A new/changed report must
**run live** before the merge. Details in
[`docs/relatorios-didaticos.md`](../../relatorios-didaticos.md) §5.

### 8.6 — The E2E demo measured the Docker bridge, not the 5G tunnel

The throughput step of the E2E Demonstration (`demo_e2e.sh`) ran
`iperf3 -c 10.50.0.100` from inside the UE container. But the DN
(`open5gs-dn-containerized`, `10.50.0.100`) is on the **same Docker network** where the
UE container has its `eth0` — so the iperf went out **straight through the Docker bridge, not
through the 5G tunnel** (`uesimtun0`, pool `10.60.0.0/16`). Result: it did not measure the core
and also failed due to `iperf3 -s -1` server *timing*.

**Fix (v0.25.0):** create a **temporary route to the DN via `uesimtun0`** and
**bind the source to the tunnel IP** (`iperf3 -B 10.60.0.x`), forcing the real path
`UE → gNB → UPF (NAT on N6) → DN`; the route is removed at the end. Validated live:
**149 Mbit/s** crossing the 5G core (before: no measurement). As a bonus, the
E2E Demo now echoes the **real command + real output + "Why"** of each step.

---

## 9. End-to-end validation (current confirmed state)

Tested on the server via `./deploy.sh up core` + `./deploy.sh up ran`:

1. `add-subscriber.sh` registers IMSI `001010000000002` in MongoDB.
2. The UE (UERANSIM) registers: NG Setup → 5G-AKA authentication → Security Mode →
   `Initial Registration is successful`.
3. PDU Session Establishment Accept → `uesimtun0` comes up with IP `10.60.0.2`.
4. `ping -I uesimtun0 8.8.8.8` → **4/4 packets, 0% loss, RTT ~10ms**.
5. `healthcheck.sh`: NRF healthy, N2/N3/N4/N6 all OK, PFCP association
   established, UE running with active connectivity.

**Resource usage** with the full core + RAN running: ~492 MiB / 906 MiB of
RAM, ~342 MiB of swap, each container's CPU below 2% (MongoDB the heaviest,
~13% of one core). **The small instance sustains the full Project 1
with room to spare.**

The real RAM risk is for Project 2 (building OAI from source is
CPU/RAM-intensive) — not yet measured, test with caution.

**Live verification of all reports (2026-06-21, v0.25.0–0.25.3):**
actually run, not just `bash -n`. **Project 1** — `status`,
`system-status`, `ng-setup`, `registration`, `config-coherence`,
`ue-connection`, and `upf-failover` (failover keeping connectivity) pass, all
with a section header, colored checks, and a "Summary" block; 3 precision bugs
found and fixed (§8.5). **Project 2** — `e2-sm` (end-to-end O-RAN chain,
7 subscriptions), `e2-kpm` (subscription OK, honest verdict "no traffic in the
period"), and `e2-rc` (RRC events from the attach captured) pass, no bugs. The
E2E Demonstration measures a real **149 Mbit/s** through the 5G tunnel (§8.6).

---

## 10. Pending / next steps

- [x] **Scientific-article checklist (Prof. Jonas, 2026-07-02) — 7 of 8
      done** (v0.32.0–0.33.1): topology with **CUPS** lanes (control
      plane × user plane), explicit **N1** (logical, via the gNB), and
      labeled **N11/Nsmf**, layout re-gridded with no line crossing a
      third-party card (checker in `panel/test/check-topology.py`),
      standardized IPs/ports, **light/dark themes** (golden rule: dark
      consoles in both themes with a fixed ISO `TERM` palette — never theme
      variables in terminal content), teaching annotations on each service's
      startup (`SERVICE_ROLES`), HTML with `no-cache` (deploy lands instantly) and
      a **cost policy** ([`docs/POLITICA-DE-CUSTOS.md`](../../POLITICA-DE-CUSTOS.md)).
- [ ] **i18n — pt/en/es/fr** (checklist item 1b; 2026-07-03 decision: international
      project, EVERYTHING in 4 languages, fr included). **F1 done (v0.34.0)**:
      `static/i18n.js` infra (dictionaries + fallback lang→en→pt + parity
      test `npm run test:i18n`), 🌐 selector, login + topbar translated;
      READMEs in 4 languages + `docs/i18n/<lang>/` with `check-parity.py`.
      **Remaining**: F2 (the whole index), F3 (topology/JSONs), F4 (bash scripts
      via `LAB_LANG`); technical docs in en on demand. Rules in
      CONTRIBUTING §7 (the 3GPP/O-RAN glossary is not translated).
- [ ] **Near-RT/Non-RT RIC lab with AI** (scikit-learn aarch64 already vendored
      in `server/panel/vendor/`): inference xApp in the seconds loop +
      training rApp on the Non-RT. **Depends on the upgrade to 4 vCPU** — cost
      analysis and the reversible-resize runbook in the cost policy §3.
- [ ] Confirm with the professor the official rubric/test plan for
      Project 2 (not published in the source repo as of the check date).
- [x] Diagnosis of Project 2's real state (2026-06-18): nothing was
      functional — the Service Model `.so` files were x86-64 (wrong for ARM64),
      the only existing log showed E2SM-RC failing with a core dump, with
      no compiled binary on the server. See `CHANGELOG.md` v0.8.0.
- [x] Build and validate `server/oai-cn-gnb-e2/` (2026-06-19): 6 OAI
      5G Core arm64 images built on Mac Apple Silicon, loaded on the server;
      `up_e2_lab.sh` brings up OAI Core + nearRT-RIC + gNB(E2) + nrUE; E2 SETUP OK,
      8 RAN functions registered (2,3,142–148), `test_e2_sm.sh all` passes
      (xApps subscribe to KPM/RC/MAC/RLC/PDCP/GTP). The UE reaches `RRC_CONNECTED`.
- [x] **Instance stability** (2026-06-19): the RFSIM gNB/nrUE saturated
      the `t4g.medium`'s 2 vCPUs and **froze the machine** (several forced
      reboots). Fixed by wrapping the native processes in systemd *scopes* with
      `CPUQuota` (120%/60%) + `CPUWeight=20` + `nice 10` in
      `up_gnb_oai.sh` — it reserves CPU for the system, prevents the freeze without breaking
      E2 (validated: machine responsive under load, E2 SM test passes).
- [ ] **xApp UE-TP-rApp** (the group's topic): per-UE throughput prediction from
      RSSI/RSRP/CQI/PRB. Skeleton in `xapp_ue_tp_moni.c`; the prediction model
      is missing. **Next big step after the presentation.**
- [ ] **🧱 Upgrade to 4 vCPU — HW blocker for the full KPM report.**
      Collecting KPM with **real throughput** (non-zero data for the analysis and the
      UE-TP-rApp) requires the UE+gNB RFSIM in real time, which **does not fit in 2 vCPU under
      the guardrail**. Forcing 2 cores (removing the guardrail) **froze the box 2×**
      (reboots). Decision: the collector (`kpm_collect_real.sh`) **never touches the cpuset**
      and concludes honestly on 2 vCPU; **real data depends on a 4 vCPU instance**
      (`t4g.xlarge`). For now, the safe demo = signed KPM + analysis over the
      sample (`kpm_analytics.sh`). See [`docs/KPM-COLETA-RESILIENTE.md`](../../../server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md).
- [x] **UE user plane in Project 2 — RESOLVED in core v2.2.1** (2026-06-22):
      the UE attaches, gets IP `12.1.1.2`, and has real traffic (`ping 8.8.8.8` 0% loss
      over `oaitun_ue1`). The blocker **was not** AUSF↔UDM HTTP/2 (that was in
      core **v1.5.1**); in v2.2.1 the bottleneck is **CPU**: on 2 vCPU with the cpuset
      guardrail (1 core), gNB and UE share the core and the UE's RRC floods. With the **2
      cores** released (or **4 vCPU**, recommended), the UE attaches normally. Trade-off
      and timer-free procedure in [`server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md`](../../../server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md)
      and §7.c.
- [ ] Persist the FlexRIC symlinks (`/usr/local/lib/flexric` and
      `/usr/local/etc/flexric`) in `infra/server-bootstrap.sh` — today they are
      created by hand and lost when switching instances.
- [x] "Projeto 2 — OAI/FlexRIC (E2)" group in the panel (`server.py` +
      `index.html`): up/down/test buttons for the E2 lab, the same generic
      `data-cmd` → `POST /api/run/{cmd}` mechanism as Project 1.
- [ ] Consider reporting the §8 bugs to the professor/original repository.
- [ ] Implement the rest of the observability panel blueprint
      (`docs/blueprint-painel-observabilidade.md`) — telemetry (§5) and
      filtered logs (§5) already done without Loki/Grafana/Prometheus; the
      E2/NGAP/GTP-U protocol sensor + interactive topology are still missing
      (pedagogical, more ambitious).
- [x] **UE registration**: a panel form (IMSI/K/OPc/MSISDN/AMF)
      with help text per field, calls `./scripts/add-subscriber.sh` via
      `POST /api/subscriber`; guest blocked with 403.
- [x] **Test tools in the panel**:
  - Bandwidth test: `iperf3` between `ueransim` (uesimtun0) and `dn` —
    baseline ~150 Mbits/s confirmed (`scripts/test_throughput.sh`).
  - Interference/distance test: `tc netem` on uesimtun0 via
    `scripts/test_channel.sh` (3GPP TR 38.901 + Shannon models). Ideal
    ~148 Mbit/s → 1km/medium ~608 Kbit/s (loss/RTT follow along).
- [x] **ISO/ANSI colorimetry + teaching summary in every test**
      (v0.12.0): `scripts/lib/testlog.sh` lib + ANSI render in the panel; each
      test ends with a colored "What it did" + "Result". See `CHANGELOG.md`.
- [x] **Teaching audit + live verification of all reports**
      (v0.25.0–0.25.3): E2E Demo with real command/output + "Why" and
      corrected throughput (149 Mbit/s through the 5G tunnel, §8.6); P1 and P2 run
      live, 3 precision bugs fixed (§8.5); dev guide in
      [`docs/relatorios-didaticos.md`](../../relatorios-didaticos.md).
- [x] **Anti-freeze**: the RFSIM gNB/nrUE run under `systemd-run --scope` with
      `CPUQuota`/`CPUWeight`/`nice` in `up_gnb_oai.sh`, `test_e2_kpm.sh`, and
      `test_e2_rc_attach.sh` — the 2 vCPU instance no longer freezes.

> **Operational gotcha (5G-AKA / SQN):** if the UE does not register and the log shows
> `Authentication Failure due to SQN out of range`, the subscriber's sequence number
> (UDM/MongoDB) has desynced from the SIM. Solution: re-register the
> subscriber (`./scripts/add-subscriber.sh`, which deletes+inserts and resets the SQN) and
> restart the UE (`docker restart ueransim`). `uesimtun0` comes back in seconds.

---

## 11. References within the repository

- [`README.md`](../../../README.md) — the entry point: **how to reproduce** the current
  state from scratch, roadmap with dates, and **how to contribute** (contact:
  [hc@cesar.school](mailto:hc@cesar.school) · [@henriquecarmine](https://github.com/henriquecarmine)).
- [`CHANGELOG.md`](../../../CHANGELOG.md) — detailed chronological history of every action.
- [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) — how to contribute (Issues/Discussions/PR, validation, versioning).
- [`docs/relatorios-didaticos.md`](../../relatorios-didaticos.md) — **dev guide for the reporting system**: `testlog.sh` lib, E2E Demo protocol, how to add a report, gotchas (§8.5–8.6), and P1/P2 inventory.
- [`docs/blueprint-painel-observabilidade.md`](../../blueprint-painel-observabilidade.md) — the panel's design.
- [`docs/labs/`](../../labs) — original course guides (Docker installation, GCP/VM pre-lab, Open5GS core, UERANSIM, delivery report).
- [`server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md`](../../../server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md) — the official Project 2 script.
- [`server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md`](../../../server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md) — **reproduction guide up to the user plane** (UE with IP + ping): CPU sizing (**4 vCPU recommended vs 2 vCPU alternative**), bringing up core v2.2.1 + E2 + xApps, and the timer-free procedure to release/revert the 2 cores.
- [`server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md`](../../../server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md) — **Data in the RAN**: teaching pipeline `kpm_analytics.sh` (Class 06, slide 46) that turns the raw KPM log into a CSV time series + per-UE KPIs + sparkline; a bridge to the UE-TP-rApp and Module 7 (Data Analysis).
- [`server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md`](../../../server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md) — **millimeter-precise engineering** of `kpm_collect_real.sh`: KPM collection with real traffic, **resilient and 100% event-driven** (a "not stuck" heartbeat, auto-retry, cpuset auto-revert, anti-hang watchdog) — the "zero time" standard applied, for the live presentation.
- `pdfs/` — slides of Classes 01–04 + the group-composition spreadsheet (the source of everything in §1).
