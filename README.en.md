# Core5G ARM64

**🌐 [Português](README.md) · English · [Español](README.es.md) · [Français](README.fr.md)**
<!-- sync: v0.34.0 -->

> 🌐 English translation of [README.md](README.md) — synced with **v0.34.0 (2026-07-03)**.
> Portuguese is the canonical language; linked documents are in Portuguese unless noted.

A complete 5G laboratory running on **AWS Graviton (ARM64)**, with its own web
control panel. It hosts **two independent projects** from the *RAN Intelligent
Controller (RIC)* course — CESAR School (group topic: **UE-TP-rApp**):

| Project | Stack | Folder | Status |
|---|---|---|---|
| **Project 1** | Open5GS (5GC) + UERANSIM (simulated gNB/UE) | `server/` | ✅ Presented 2026-06-13, validated end to end |
| **Project 2** | OAI 5GC + RFSIM gNB + E2 agent + **FlexRIC** (near-RT RIC) + xApps | `server/oai-cn-gnb-e2/` | ✅ Presented 2026-06-20 |

**Current phase (Jul/2026): scientific paper** — Prof. Jonas is writing the
paper (Overleaf) and requested a checklist of 8 platform improvements
(2026-07-02). Status: **7 of 8 done** in panel v0.34.x — topology with **CUPS**
bands (control vs. user plane), explicit **N1/N11** interfaces, overlap-free
layout, **light/dark themes**, **ISO log colors** in every terminal, didactic
annotations when each service starts, a **language selector (PT/EN/ES/FR)** and
the [cost policy](docs/POLITICA-DE-CUSTOS.md) (pt). Remaining: full panel
i18n beyond login/topbar.

> **Just want to understand the what/why of everything?** Read the
> [**project bible**](core5g-arm64-bible.md) (pt — full conceptual reference).
> For the chronological history, the [**CHANGELOG**](CHANGELOG.md) (pt). For the
> lab guides, [`docs/labs/`](docs/labs/) (pt).
>
> This README is the **front door**: how to reproduce the current state, what is
> missing and how to contribute.

---

## 1. How to get here (reproduction from scratch)

The workflow is **everything local, deploy via `deploy.sh`**. You never edit
files directly on the server — you edit `server/` on your machine and
`deploy.sh` mirrors it to the server over SSH/rsync.

### 1.1 Prerequisites

- An **AWS account** with an EC2 **ARM (Graviton)** instance, Ubuntu 22.04+.
  Recommended: **`t4g.medium`** (2 vCPU, 4 GB) — a `t4g.micro` only runs
  Project 1. **30 GB** EBS volume.
- Your local machine with `bash`, `git`, `rsync`, `ssh` and `openssl`.
- To **build** the OAI arm64 images: an **Apple Silicon Mac** (or another arm64
  machine) with Docker. The ready-made images are **not in git** (~362 MB) —
  they are distributed through the group's Google Drive.

### 1.2 Clone and configure

```bash
git clone https://github.com/henriquecarmine/Core5G_ARM64.git
cd Core5G_ARM64
cp .env.example .env
```

Edit `.env` (never commit it — it is in `.gitignore`):

```ini
AWS_SERVER_HOST=core5g-arm64.duckdns.org   # DuckDNS domain or instance IP
AWS_SERVER_USER=ubuntu
AWS_SSH_KEY_PATH=ssl/core5g_openran_arm64.pem   # your SSH key (.pem), NEVER commit

DUCKDNS_DOMAIN=core5g-arm64                 # optional: automatic dynamic IP
DUCKDNS_TOKEN=<your-token>

PANEL_USER=professor                        # Professor (admin) — full access
PANEL_PASSWORD=<strong-password>
PANEL_GUEST_USER=guest                      # enables Student access (read-only)
PANEL_GUEST_PASSWORD=<guest-password>       # optional (students join with name+e-mail)
PANEL_EXTRA_USERS=professor2:pass2          # extra admins: user:pass,user2:pass2
```

> **Roles (classroom mode):** the *Professor* operates (only **one at a time**);
> *Students* watch live and join with **name + e-mail** (no password). See §1.6.

### 1.3 Provision the server (once)

```bash
./deploy.sh bootstrap     # Docker + 8 GB swap + DuckDNS + Caddy (HTTPS) + panel
```

Idempotent — run it as often as you like. When it finishes, the panel answers at
`https://<your-host>/` with valid TLS (Let's Encrypt via Caddy) and a login page.

### 1.4 Project 1 — Open5GS + UERANSIM

```bash
./deploy.sh up all        # brings up the 5G Core (Open5GS) + RAN (UERANSIM)
./deploy.sh status        # docker ps + healthcheck (N2/N3/N4/N6)
```

End-to-end validation: the UE registers (5G-AKA), opens a PDU Session and gets
real connectivity (`ping -I uesimtun0 8.8.8.8` → 0% loss). All of this is also
exposed as buttons in the panel (UE Lab, E2E Demonstration).

### 1.5 Project 2 — OAI + FlexRIC (E2)

The OAI arm64 images must be loaded into the server's Docker:

```bash
# (on the arm64 Mac) build and export the 6 images — see bible §7.b:
cd server/oai-cn-gnb-e2 && ./build-oai-arm64.sh        # AMF→SMF→NRF→UDR→UDM→AUSF
# exports /tmp/oai-images/oai-*.tar (~60 MB each). Upload to the group's Drive.

# send the Project 2 directory (once, ~230 MB):
./deploy.sh sync-oai

# on the server: docker load -i ~/oai-<comp>.tar  (each component from Drive)
```

With the images loaded, the E2 lab starts **from the panel** (project selector →
*Project 2*) or over SSH:

```bash
./deploy.sh ssh
cd ~/server/oai-cn-gnb-e2
./scripts/up_e2_lab.sh           # OAI Core + nearRT-RIC + gNB(E2) + nrUE
./scripts/test_e2_sm.sh all      # exercises the 8 Service Models via xApps
```

> **Why `t4g.medium`?** The RFSIM gNB/nrUE are CPU-intensive. On 2 vCPUs they
> can saturate and **freeze the instance**. The guardrail uses **cgroup v2
> cpuset**: the `bootstrap` creates the `oai-lab.slice` pinned **off CPU 0**
> (`AllowedCPUs=1`), reserving one core for the system (SSH/Docker/panel/Caddy
> with maximum `CPUWeight`). The lab can never take the box down — the panel
> stays at ~600 ms and SSH at ~2.5 s even with gNB+nrUE at full load. (On this
> ARM kernel `CPUQuota`/CFS is not enforced, hence cpuset.) Details in
> [`infra/server-bootstrap.sh`](infra/server-bootstrap.sh).

### 1.6 Web panel — classroom mode

`https://<your-host>/` — the panel is a SPA (FastAPI + HTML/CSS/JS, no build
step). Core features: live telemetry, filtered/colored logs (ANSI/ISO) with a
**didactic explanation** at the end, UE Lab, E2E Demonstration, **project
selector** (starting one shuts the other down), **interactive topology** (real
containers/ports/networks, clickable) and the E2 Service Model tests — each with
a final **summary** of what it did and the outcome. UI in **4 languages**
(PT/EN/ES/FR, 🌐 selector) and **light/dark themes**.

On top of that, a **classroom mode** designed for presenting to an audience:

- **Professor / Student roles.** The *Professor* (admin) operates; *Students*
  (guests) watch read-only, joining with **name + e-mail** (1 click, no
  password) — the e-mail doubles as the class **attendance record**.
- **One Professor at a time.** The slot is "sticky": a different admin is
  blocked until the current one signs out or idles for 10 min.
- **LIVE mirror.** Everything the Professor runs is streamed in real time to
  the Students (console + which screen is open), via ring-buffer + polling —
  scales to the whole class without hurting the box.
- **Results + Replay.** Every run is saved to disk (survives restarts) and can
  be **replayed** line by line later. "Saved results" tab (Professor & Student).
- **Live RAN (P2).** Sparkline strip with the OAI gNB's real SNR/MCS/PRB/BLER,
  updating live during E2SM-KPM.
- **Projection (kiosk) mode.** "⛶ Projection" button → clean fullscreen for the
  projector.
- **Who is watching.** The Professor clicks the "👁 N students" badge to see the
  connected list and attendance.

---

## 2. What is still missing (roadmap)

| When | Item | State |
|---|---|---|
| **Short term** | **Full panel i18n — pt/en/es/fr** beyond login/topbar (phases F2 index, F3 topology, F4 bash scripts via `LAB_LANG`) | ⏳ F1 done (v0.34.0) |
| Short term | **UE-TP-rApp** xApp (per-UE throughput prediction: RSSI/RSRP/CQI/PRB) — the group's topic. **scikit-learn aarch64** wheels already vendored (`server/panel/vendor/`) | ⏳ Skeleton in `xapp_ue_tp_moni.c`; model missing |
| 🧱 **HW blocker** | **The RIC (Near/Non-RT) + AI lab and the full KPM report with real throughput need 4 vCPUs.** Cost analysis and reversible-resize runbook: [`docs/POLITICA-DE-CUSTOS.md`](docs/POLITICA-DE-CUSTOS.md) §3 (pt) | ⚠️ Awaiting approval (costs) |
| ✅ Done | **Paper checklist items 2–7 + themes** (Prof. Jonas, 2026-07-02) | ✅ v0.32.0–0.33.1 |
| ✅ Done | **Cost policy** (item 8) + disk hygiene (3.1 → 8.6 GB free) | ✅ [`docs/POLITICA-DE-CUSTOS.md`](docs/POLITICA-DE-CUSTOS.md) (pt) |
| ✅ Done | **UE user plane on Project 2** (core v2.2.1) | ✅ Validated 2026-06-22 |
| Mid term | E2/NGAP/GTP-U protocol sensor in the panel (observability blueprint) | 📋 Planned |
| Mid term | Persist the FlexRIC symlinks (`/usr/local/lib/flexric`) in `bootstrap` | 📋 Planned |
| Someday | Report the bible §8 bugs to the upstream OAI repository | 📋 Planned |

The canonical, detailed list lives in [bible §10](core5g-arm64-bible.md#10-pendências--próximos-passos) (pt).

---

## 3. Contributing

Contributions from the group (and anyone studying the lab) are welcome. The full
step-by-step guide is in **[`CONTRIBUTING.md`](CONTRIBUTING.md)** (pt). In short:

- **[Issues](../../issues)** — report a bug, propose an idea, ask a question.
- **[Discussions](../../discussions)** — talk / ask "how does X work".
- **Pull Request** — *fork* → branch → PR describing *what changed and why*.

Golden rules: always edit **locally** (`deploy.sh` is the only path to the
server); **secrets never enter git** (`.env`, `ssl/*.pem`); **student data**
(e-mails/roster) stays on the server only. Translations must keep the 4
languages in sync (`npm run test:i18n` and the docs parity checker).

**Collaborator access, or the OAI arm64 images from Drive?** Contact me:

- **Henrique Carmine** — [henriquecarmine@gmail.com](mailto:henriquecarmine@gmail.com) ·
  [@henriquecarmine](https://github.com/henriquecarmine)

---

## 4. Repository map

```
.
├── README.md                  ← front door (pt; en/es/fr variants alongside)
├── LICENSE                     ← MIT license
├── CONTRIBUTING.md            ← how to contribute (Issues/Discussions/PR, tests, versioning)
├── core5g-arm64-bible.md      ← full conceptual reference (pt)
├── CHANGELOG.md               ← chronological logbook (pt)
├── deploy.sh                  ← single deploy entrypoint (local → server)
├── .env.example               ← configuration template (copy to .env)
├── .github/                   ← Issue and Pull Request templates
├── docs/                      ← panel blueprint + lab guides
│   ├── POLITICA-DE-CUSTOS.md  ← costs, operating rules and CPU upgrade
│   ├── i18n/                  ← translated docs (en/es/fr mirrors)
│   └── relatorios-didaticos.md ← dev guide: how tests/reports work
├── infra/                     ← server bootstrap + panel systemd unit
└── server/                    ← everything that runs on the server
    ├── panel/                 ← web panel (FastAPI) — see panel/README.md
    │   ├── test/              ← headless tests (loaders, topology/themes, i18n)
    │   └── vendor/            ← scikit-learn aarch64 wheels (RIC + AI lab)
    ├── ueransim/              ← simulated RAN (Project 1)
    ├── scripts/               ← E2E demo, project switch, ISO log lib
    └── oai-cn-gnb-e2/         ← Project 2 (OAI + FlexRIC + xApps)
```

---

## 5. Team

- **Coordination (advisor):** Prof. Dr. Jonas Augusto Kunzler — [jak@cesar.school](mailto:jak@cesar.school)
- **Development and maintenance:** Henrique Carmine — Digital Forensics Expert
  (IT & Telecom Governance), MSc student in Open RAN advised by Prof. Jonas
  Kunzler — [henriquecarmine@gmail.com](mailto:henriquecarmine@gmail.com) ·
  [@henriquecarmine](https://github.com/henriquecarmine)

Project **coordinated by Prof. Dr. Jonas Augusto Kunzler** and **maintained by
Henrique Carmine**. CESAR School · *RAN Intelligent Controller (RIC)* course ·
topic **UE-TP-rApp**. **[MIT](LICENSE)** license.

---

## 6. Support this project

This lab stays **online 24/7** on an ARM server at AWS, paid out of pocket — so
anyone can study 5G/O-RAN, use it in class or in research. Keeping it online has
a real monthly cost, currently covered entirely by the maintainer.

If the project helped you, **any amount helps keep the server on** 🙏

> **PIX (Brazil):** `henrique@titannium.us` (e-mail key)

Thank you — every contribution keeps the lab available for the next person.
