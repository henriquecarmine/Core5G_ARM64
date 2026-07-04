<!-- sync: e36a3f4e -->
> 🌐 **English** translation of the canonical Portuguese doc [`server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md`](../../../../../../server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md). All languages: [INDEX](../../../INDEX.md) · sync checked by `docs/i18n/check-parity.py`.

# Project 2 — Reproduction up to the user plane (UE with IP) and CPU sizing

**Definitive** guide for a contributor to go from scratch to the state validated on
2026-06-22 on the Graviton server: **OAI Core v2.2.1 + near-RT RIC + gNB (E2) + the 3 xApps
(KPM/cust/RC) + UE with a real IP and traffic through the 5G tunnel**.

This document focuses on **CPU and user plane** — the part that confuses most and where the
important trade-off lies. For what is already covered in other guides, it points to the link instead
of repeating:

- **Compile the arm64 Core images** (AMF/SMF/NRF/UDR/UDM/AUSF + **oai-upf-vpp**):
  [`OAI-CORE-ARM64.md`](OAI-CORE-ARM64.md) and [bible §7.b](../../../../../../core5g-arm64-bible.md).
- **Build the gNB/nrUE/FlexRIC + Service Models**: [`TUTORIAL_LAB_E2.md`](TUTORIAL_LAB_E2.md),
  [`INSTALACAO_GNB_OAI.md`](INSTALACAO_GNB_OAI.md), [`E2_FLEXRIC.md`](E2_FLEXRIC.md).
- **Project golden rule:** never edit files directly on the server. Edit under `server/`
  on your machine and use `./deploy.sh` (and `./deploy.sh sync-oai` for this directory).

---

## 0. TL;DR — what you will get and the CPU trade-off

| Block | How to validate | Depends on the UE? |
|---|---|---|
| Core 5G (9 NFs) healthy | `docker ps` all `healthy` | no |
| **E2 SETUP** gNB ↔ RIC | `[E2-AGENT]: E2 SETUP RESPONSE rx` in the gNB log | no |
| **xApps** KPM / cust / RC | `Successfully subscribed to RAN_FUNC_ID 2 / 142 / 3` | no |
| **User plane** (UE gets IP + ping) | `oaitun_ue1 = 12.1.1.2`, `ping 8.8.8.8` 0% loss | **yes** |

> **The rule that sums it all up:** E2/RIC/xApps are **gNB↔RIC** and **do not need the UE**. The
> user plane (UE with IP) needs the nrUE running — and the nrUE is what blows up the CPU.

**Sizing (read §1 before bringing anything up):**
- **4 vCPU (recommended):** everything runs together, no tricks, no risk of freeze.
- **2 vCPU (alternative — what we have today):** either you protect the machine (1-core guardrail,
  **without** the UE) **or** you run the full user plane (2 cores, dedicated box). You can't do both
  at the same time. §4 shows how to run the user-plane test safely.

---

## 1. CPU sizing — why 4 vCPU is better

The gNB (`nr-softmodem`) and the UE (`nr-uesoftmodem`) run in **RFSIM** (radio in software). Each
one does a **busy-poll**: it saturates ~1 full vCPU continuously (it's not a spike — it's constant,
because the sample loop runs in real time). Add the near-RT RIC and the system (sshd, Docker,
Caddy, panel) and you need **enough cores for all of them**.

### Core count

| Process | CPU demand |
|---|---|
| `nr-softmodem` (gNB RFSIM) | ~1 dedicated core |
| `nr-uesoftmodem` (UE RFSIM) | ~1 dedicated core |
| `nearRT-RIC` + xApp | fraction of 1 core (spikes on INDICATION→Report) |
| System (sshd, Docker, Caddy, panel, Core) | ~1 core |

→ **The full lab WITH user plane wants ~4 cores.** Hence:

### Recommended: 4 vCPU instance

**AWS:** `t4g.xlarge` (4 vCPU / 16 GB) or `c7g.xlarge` (4 vCPU / 8 GB), Graviton, Ubuntu
22.04+. With 4 vCPU:
- gNB on one core, UE on another, RIC+xApp on another, system on another.
- **No cpuset, no guardrail, no freeze.** The UE attaches and the xApps run **at the same time**.
- It's the path a contributor should prefer for developing the **UE-TP-rApp** (needs per-UE
  KPM **with** the UE active generating traffic).

> If you are going to spin up a new instance, **spin up 4 vCPU**. It costs a little more, but it eliminates
> all the rest of this section.

### Alternative: 2 vCPU (the current box — `t4g.medium`)

With only 2 cores, gNB + UE + system don't fit in real time. In 2019–2026 this caused
**freezes and reboots** (the gNB+UE saturated both vCPUs and `sshd` died — the machine
became unreachable). The defense was a **cpuset guardrail**:

```
oai-lab.slice  →  AllowedCPUs=1     # todo o lab (gNB+UE+RIC) pinado no CPU 1
                                    # CPU 0 fica reservado p/ sistema (sshd/Docker/painel)
```

This guardrail **keeps the machine alive under load** (SSH ~2.5 s even with the gNB flat out), but
it has a cost: the gNB and UE now **share a single core**. Measured result:

- The UE **synchronizes** (PHY/RFSIM OK: `Initial sync successful, PCI 0`, RSRP 51 dB)…
- …but **RRC floods** — the `TASK_RRC_NRUE task contains …` queue grows without stopping
  (71k → 112k → …) because the UE does not get enough CPU to process RRC in real time
  (the gNB has `CPUWeight=60`, the UE only `CPUWeight=20`).
- **The UE never gets an IP.**

That's why the canonical P2 validation (E2 + xApps) runs **without the UE** (`SKIP_UE=1`). To test
the user plane on the 2 vCPU box, you must **temporarily free both cores** — see §4.

---

## 2. Prerequisites

1. **arm64 Core images loaded on the server** (optionally including `oai-upf-vpp`).
   See [`OAI-CORE-ARM64.md`](OAI-CORE-ARM64.md). The lab uses the v2.2.1 `oai-upf` (simple_switch) —
   `oai-upf-vpp` is optional (see §6).
2. **gNB/nrUE/FlexRIC compiled** on the server (`openairinterface5g/` + `flexric-lib/`).
   See [`TUTORIAL_LAB_E2.md`](TUTORIAL_LAB_E2.md) and [`INSTALACAO_GNB_OAI.md`](INSTALACAO_GNB_OAI.md).
3. **Synchronized directory:** `./deploy.sh sync-oai` (sends `server/oai-cn-gnb-e2/`).
4. **Project 1 stopped** (P1 and P2 are mutually exclusive): `./deploy.sh down all`.

Lab parameters (already configured, they match between the gNB and core v2.2.1):

| Item | Value |
|---|---|
| PLMN | 208 / 95 |
| Slice | SST 222 / SD 123 |
| DNN | `default` (pool **12.1.1.0/26**) |
| gNB | `gnb_24prb.conf`, NRB=51, f=3469440000 Hz, n78 band |
| nrUE | `--rfsim -r 51 --numerology 1 --band 78 -C 3469440000 --ssb 186` |
| AMF | 192.168.70.132 |

---

## 3. Main path — bring up and validate (E2 + xApps)

Connect to the server (`./deploy.sh ssh`) and:

```bash
cd ~/server/oai-cn-gnb-e2

# 1) Core OAI v2.2.1 (para o P1 se estiver no ar; espera oai-amf healthy — por ESTADO)
./oai-cn5g-v2/up_core_v2.sh
docker ps        # esperado: 9 containers healthy (amf, smf, nrf, udr, udm, ausf, upf, mysql, ext-dn)

# 2) E2 lab. Para validar E2/xApps, NÃO suba o UE (libera CPU e evita o flood):
SKIP_UE=1 ./scripts/up_e2_lab_v2.sh

# 3) Confirmar E2 SETUP (gNB ↔ RIC) — por evento no log do gNB:
grep -E "E2 SETUP (REQUEST tx|RESPONSE rx)" logs/gnb_oai.log
#   [E2-AGENT]: E2 SETUP-REQUEST tx
#   [E2-AGENT]: E2 SETUP RESPONSE rx        ← gNB conectado ao RIC

# 4) Rodar os xApps (cada um encerra no 1º evento de sucesso — sem timer):
./scripts/run_xapp.sh kpm     # → Successfully subscribed to RAN_FUNC_ID 2
./scripts/run_xapp.sh cust    # → Successfully subscribed to RAN_FUNC_ID 142
./scripts/run_xapp.sh rc      # → Successfully subscribed to RAN_FUNC_ID 3
```

> **Project principle: ZERO time.** The scripts terminate on **event/state**
> (`grep -m1` on a stream, `tail -F --pid`, wait-until-condition), never on a blind `sleep`/timeout.
> See the memory `feedback-event-driven-nao-tempo` and bible §7.c.

Measured result (2026-06-22): **E2 SETUP OK**, **KPM/cust/RC all three subscribed**. This is the
graded deliverable of Project 2 and **does not depend on the UE**.

---

## 4. User plane — UE with IP + ping through the 5G tunnel

> **What it proves:** that the data path is complete — the UE registers (NAS/5G-AKA), opens a PDU
> session, gets an IP from the `12.1.1.0/26` pool and has real connectivity through the
> `oaitun_ue1` interface. Measured result: `oaitun_ue1 = 12.1.1.2`, `ping 8.8.8.8` → **4/4, 0% loss,
> RTT ~111 ms**.

### 4.a — On 4 vCPU (recommended): simply bring it up with the UE

```bash
cd ~/server/oai-cn-gnb-e2
./oai-cn5g-v2/up_core_v2.sh
./scripts/up_e2_lab_v2.sh        # SKIP_UE=0 (default) → sobe gNB + nrUE

# Espera-até-condição (por ESTADO, não por tempo): UE ganha IP
until ip -4 addr show oaitun_ue1 >/dev/null 2>&1; do
  pgrep -x nr-uesoftmodem >/dev/null || { echo "nrUE morreu"; break; }
done
ip -4 addr show oaitun_ue1 | grep inet           # → inet 12.1.1.2/...
ping -I oaitun_ue1 -c 4 8.8.8.8                   # → 0% packet loss
```

On 4 vCPU this works right away, **without touching cpuset**, and you can still run the xApps in
parallel (there's a spare core for the RIC+xApp). It's the correct environment for developing the
**UE-TP-rApp** (per-UE KPM with real traffic).

### 4.b — On 2 vCPU (alternative): free both cores safely

On the 2 vCPU box, the UE only attaches if the lab uses **both cores** (`AllowedCPUs=0-1`) — which
**removes the anti-freeze guardrail**. To do this without freezing the machine and **without any
timer**, use the procedure below (validated on 2026-06-22). The safety comes from **event +
priority**, not from a stopwatch:

- **`trap revert EXIT`** — the cpuset goes back to `1` when the process ends (not by the clock).
- **Pure event wait** (`wait -n` between two blocking watchers):
  - success = `ip monitor address` captures `oaitun_ue1` gaining an address (netlink event);
  - failure = `tail -F --pid | grep -m1` detects the RRC flood.
- **`nice -20`** on the monitor → it is always scheduled and can revert **even if the lab saturates
  both cores**.

Script (`scripts/ue_userplane_2cores.sh` — create it from this block; it's safe and self-reverts):

```bash
#!/bin/bash
# Testa o user plane do UE liberando os 2 cores, com revert garantido por EVENTO (sem timer).
# Rode com prioridade alta:  sudo nice -n -20 bash scripts/ue_userplane_2cores.sh
SLICE=oai-lab.slice
OAI=$HOME/server/oai-cn-gnb-e2/openairinterface5g
BUILD=$OAI/cmake_targets/ran_build/build
UECONF=$OAI/scripts/ue.conf
UE_LOG=$HOME/server/oai-cn-gnb-e2/logs/ue_oai.log
UNIT=oai-nrue-$$

revert(){
  sudo pkill -x nr-uesoftmodem 2>/dev/null
  sudo systemctl set-property --runtime "$SLICE" AllowedCPUs=1 2>/dev/null   # guardrail de volta
  pkill -P $$ 2>/dev/null                                                    # encerra watchers
}
trap revert EXIT                                  # revert por TÉRMINO, não por tempo

pgrep -x nr-softmodem >/dev/null || { echo "ABORT: gNB nao roda"; exit 1; }

# WATCHER de SUCESSO (evento netlink) — inicia ANTES do UE p/ não perder o add do endereço
( ip -o monitor address 2>/dev/null | grep -qm1 "oaitun_ue1" ) & WIN_OK=$!

# Libera os 2 cores
sudo systemctl set-property --runtime "$SLICE" AllowedCPUs=0-1
sudo pkill -x nr-uesoftmodem 2>/dev/null; : > "$UE_LOG"
cd "$BUILD" || exit 1
sudo systemd-run --scope -q --unit="$UNIT" --slice="$SLICE" -p CPUQuota=100% -p CPUWeight=20 \
  nice -n 10 ./nr-uesoftmodem -O "$UECONF" --rfsim -r 51 --numerology 1 --band 78 \
  -C 3469440000 --ssb 186 > "$UE_LOG" 2>&1 &
UEPID=$(systemctl show -p MainPID --value "$UNIT.scope" 2>/dev/null)

# WATCHER de FALHA (evento no log): flood RRC (>=6 dígitos) OU morte do UE (--pid encerra tail)
( tail -n +1 -F --pid="${UEPID:-$$}" "$UE_LOG" 2>/dev/null \
    | grep -qm1 -E "TASK_RRC_NRUE task contains [0-9]{6}" ) & WIN_BAD=$!

wait -n "$WIN_OK" "$WIN_BAD"                       # bloqueia até o 1º EVENTO — zero tempo

if ip -4 addr show oaitun_ue1 >/dev/null 2>&1; then
  echo "OK: UE ATTACHED — $(ip -4 addr show oaitun_ue1 | grep -oE 'inet [0-9.]+')"
  ping -I oaitun_ue1 -c 4 8.8.8.8 | tail -3
else
  echo "FALHA: UE nao attachou (flood/morte) mesmo com 2 cores"
fi
# trap EXIT reverte (cpuset=1, UE off) automaticamente
```

After running, **confirm the revert**:

```bash
systemctl show oai-lab.slice -p AllowedCPUs --value     # → 1   (guardrail restaurado)
pgrep -x nr-uesoftmodem && echo "UE ON (revert falhou!)" || echo "UE OFF (ok)"
```

> ⚠️ **Why not leave both cores enabled permanently:** without the guardrail, a gNB+UE spike
> can choke `sshd` and **freeze the instance** (it has happened — it required a reboot). The
> procedure above is to **prove** the user plane and **return to the safe state**. If you
> want the UE running stably and continuously, **migrate to 4 vCPU** (§1).

---

## 5. Expected final state and how to leave the server

Safe state (E2/xApps validated, guardrail active, UE off):

```bash
docker ps --format '{{.Names}}' | grep -cE 'oai-|mysql'    # 9
pgrep -x nearRT-RIC && pgrep -x nr-softmodem               # RIC e gNB ON
pgrep -x nr-uesoftmodem || echo "UE OFF"                   # UE off (seguro em 2 vCPU)
systemctl show oai-lab.slice -p AllowedCPUs --value        # 1
uptime                                                     # load baixo
```

Stop everything: `./scripts/down_e2_lab.sh` and `./oai-cn5g-v2/down_core_v2.sh`.

---

## 6. `oai-upf-vpp` on arm64 (optional)

The lab uses the v2.2.1 `oai-upf` (simple_switch), which **is already official multi-arch**. The
`oai-upf-vpp` (VPP dataplane, faster) was **ported to arm64** in this project (it was considered
"non-portable") — the only blocker was Hyperscan (Intel-only), solved with **Vectorscan**
(drop-in ARM fork). Details, build and validation in [bible §7.b](../../../../../../core5g-arm64-bible.md)
and `artifacts/oai-images/oai-upf-vpp.tar`. **Not required** for this lab's user plane.

---

## 7. Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| UE does not get an IP; `TASK_RRC_NRUE task contains` growing | insufficient CPU (2 vCPU + guardrail = gNB and UE on a single core) | §4.b (free both cores) or migrate to 4 vCPU (§1) |
| SSH drops (`Connection reset` / `timed out`) under load | box saturated; a heavy process stole CPU 0 from `sshd` | work **detached** (`nohup` + a file on the server) and use `ssh -o ServerAliveInterval=10`; never run a heavy process **outside** `oai-lab.slice` |
| Machine froze / unreachable | guardrail off + gNB+UE saturating both cores | reboot from the AWS console; never leave both cores freed without the self-revert procedure of §4.b |
| `Authentication Failure ... SQN out of range` | the subscriber's SQN got out of sync | re-register (`add-subscriber.sh`) and restart the UE |
| gNB log: `No connected device, generating void samples` | it's normal **before** the nrUE connects to RFSIM (:4043); it turns into `RFsim: Number of antennas changed 0→1` when it connects | wait for the nrUE; if it persists, the nrUE died — see `logs/ue_oai.log` |
| `exec format error` when bringing up a Core image | amd64 image on an arm64 host | load the correct arm64 image (`OAI-CORE-ARM64.md`) |

---

## 8. Quick command reference

```bash
# subir / parar
./oai-cn5g-v2/up_core_v2.sh                 ./oai-cn5g-v2/down_core_v2.sh
SKIP_UE=1 ./scripts/up_e2_lab_v2.sh         ./scripts/down_e2_lab.sh   # E2/xApps (sem UE)
./scripts/up_e2_lab_v2.sh                                              # + UE (só em 4 vCPU, ou §4.b em 2 vCPU)

# validar
grep -E "E2 SETUP RESPONSE rx" logs/gnb_oai.log
./scripts/run_xapp.sh kpm|cust|rc
ip -4 addr show oaitun_ue1 ; ping -I oaitun_ue1 -c 4 8.8.8.8

# CPU (2 vCPU)
systemctl show oai-lab.slice -p AllowedCPUs --value          # 1 = guardrail; 0-1 = liberado
sudo systemctl set-property --runtime oai-lab.slice AllowedCPUs=1   # restaurar guardrail
```
