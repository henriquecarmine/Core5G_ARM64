<!-- sync: e36a3f4e -->
> 🌐 **English** translation of the canonical Portuguese doc [`server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md`](../../../../../../server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md). All languages: [INDEX](../../../INDEX.md) · sync checked by `docs/i18n/check-parity.py`.

# Resilient KPM collection — millimeter-precise engineering (`kpm_collect_real.sh`)

**Line-by-line** guide to the KPM telemetry collector with real traffic, built to
run **live in a presentation** without freezing, without losing the test, and
without failing. It is the piece that produces `xapp_kpm_lab.log` with **real data**
that [`kpm_analytics.sh`](KPM-ANALYTICS.md) turns into CSV/KPI.

> ## ⚠️ Current status and CPU dependency (read first)
> **A complete KPM report with real throughput requires a 4 vCPU instance**
> (e.g., `t4g.xlarge`). On the current `t4g.medium` (2 vCPU), gNB and UE on RFSIM do
> not coexist in real time **under the anti-freeze guardrail** (1 core); and
> **removing the guardrail to free 2 cores froze the box twice** (required a reboot).
>
> **Engineering decision (safety first):** this script was rewritten to **NEVER
> touch the cpuset**. On 2 vCPU it quickly detects that the UE does not attach,
> **stops the UE** (does not let it flood memory), and **honestly concludes** "no
> data — use 4 vCPU". On 4 vCPU the UE attaches naturally (no relax) and collection
> yields real data. **Safe demonstration for now:** KPM subscribed + analysis on
> the didactic sample (`kpm_analytics.sh scripts/samples/kpm_sample.log`).

> **If you have never seen the lab:** first read [`PROJETO2-CPU-E-USERPLANE.md`](PROJETO2-CPU-E-USERPLANE.md)
> (bringing up the lab, CPU sizing) and [`KPM-ANALYTICS.md`](KPM-ANALYTICS.md)
> (what KPM is and the analytics pipeline). This document is the **how** of the
> collection.

---

## 1. Why this script exists (the problem it solves)

Collecting KPM **with real throughput** requires three simultaneous things:
1. the **UE attached** (with an IP) — otherwise the gNB does not report per-UE metrics;
2. **traffic** passing through the tunnel — otherwise throughput is zero;
3. all of that on the **2 vCPU** box, where UE+gNB compete for CPU (see
   [`PROJETO2-CPU-E-USERPLANE.md`](PROJETO2-CPU-E-USERPLANE.md)).

The naive first attempt (running `test_e2_kpm.sh` directly) **collected 0
indications**: the collection window started **before** the UE attached (the attach
takes tens of seconds) → the gNB had no connected UE → no metrics. Lesson: **the
collection must start on an EVENT (UE with IP), not on a clock.**

Hence the three requirements the professor asked for, which this script implements:

| Requirement | How the script meets it |
|---|---|
| **"Don't think it froze"** | Live **heartbeat** (`⏳ … NÃO travou`) on every log event |
| **"Don't lose the test"** | runs **detached** + writes to a file; the panel saves the console |
| **"If something happens, report and complete — do not fail"** | **auto-retry** with diagnostics + **auto-revert**; always concludes |

---

## 2. Non-negotiable principle: ZERO TIME

Project rule (memory `feedback-event-driven-nao-tempo`): **nothing decides by the
clock** — not `sleep`, not `timeout`, not a fixed duration, **not even as a safety
net**. Everything terminates on an **event/state**. The primitives used:

| Primitive | What it does | Where in the script |
|---|---|---|
| `ip -o monitor address \| grep -qm1 oaitun_ue1` | blocks (no CPU) until the UE's **netlink event** of gaining an IP | wait for attach |
| `tail -n +1 -F --pid=$P arq \| grep -qm1 PADRÃO` | blocks until the event line appears **OR** process `$P` dies | RRC flood |
| `grep --line-buffered -m K PADRÃO` | terminates **on the K-th** occurrence (goal event) | end of collection (K indications) |
| `wait -n A B` | returns when the **1st** of jobs A/B finishes | success×failure race |
| `tail -f --pid=$UEPID /dev/null; kill $XAPP` | waits (no polling) for the **UE's death** and kills the xApp | anti-hang watchdog |
| `trap revert EXIT` | fires cleanup on **process termination**, not on time | cpuset auto-revert |

> **Why `sleep` is not allowed:** a `sleep N` assumes "N seconds are enough" — and
> when they are not (slow box, slow attach), you either cut early (lose the test) or
> late (freeze). The event is **deterministic**: it ends exactly when the real
> condition happens.

---

## 3. Anatomy of the script — block by block

File: [`scripts/kpm_collect_real.sh`](../../../../../../server/oai-cn-gnb-e2/scripts/kpm_collect_real.sh).

### 3.1 Header and variables
```bash
set -u                       # erro em variável não definida (NÃO -e: queremos tratar falhas, não abortar)
NEED_IND="${NEED_IND:-20}"   # META de indicações = EVENTO de sucesso (sobrescrevível)
MAX_TRIES="${MAX_TRIES:-3}"  # nº de tentativas antes de concluir-com-o-que-há
```
`set -u` catches typos; we do **not** use `set -e` because the script **handles**
failures (retry) instead of dying on them.

### 3.2 Auto-revert (the safety net, event-driven)
```bash
revert() {  # mata xApp/ping/UE e DEVOLVE o cpuset a 1 core (guardrail anti-freeze)
  kill "$XAPP_PID"; sudo kill "$PING_PID"; sudo pkill -x nr-uesoftmodem; ...
  sudo systemctl set-property --runtime "$SLICE" AllowedCPUs=1
}
trap revert EXIT
```
**Why:** freeing the 2 cores removes the anti-freeze protection. The `trap … EXIT`
ensures that, **whatever happens** (success, error, `kill`, normal end), the cpuset
returns to 1 core and the heavy lab is stopped. It is fired by the
**process-termination event**, not by a timer.

### 3.3 Pre-conditions (clean failure, no freezing)
```bash
pgrep -x nr-softmodem || { err "gNB não está rodando…"; exit 0; }
pgrep -x nearRT-RIC   || { err "RIC não está rodando…";  exit 0; }
[ -x "$XAPP" ]        || { err "xApp KPM não compilado…"; exit 0; }
```
`exit 0` (not 1): the test **concludes by reporting the missing prerequisite**
instead of "failing". The `trap` still reverts.

### 3.4 It does NOT touch the cpuset (the safety fix)
```bash
# (intencionalmente NÃO há set-property AllowedCPUs aqui)
NPROC=$(nproc); GUARD=$(systemctl show "$SLICE" -p AllowedCPUs --value)
[ "$NPROC" -le 2 ] && warn "2 vCPU: o UE provavelmente NÃO vai attachar; p/ dados reais use 4 vCPU"
```
**Why:** freeing the 2 cores (removing the guardrail) is what **froze the box
twice**. The script runs under the current cpuset and **warns** if there are only
2 vCPU. On 4 vCPU the UE attaches without needing to touch anything. (Old versions
did `AllowedCPUs=0-1` — **removed for safety**.)

### 3.5 Attempt loop (auto-retry)
```bash
while :; do
  attempt=$((attempt+1)); section "Tentativa $attempt de $MAX_TRIES"
  ...
  if [ "$attempt" -ge "$MAX_TRIES" ]; then warn "…concluo COM O QUE HÁ…"; break; fi
  step "repetindo automaticamente…"
done
```
Each attempt brings the UE up cleanly. If it fails, it **reports the problem and
retries**. Once the attempts are exhausted, it **concludes** (does not fail).

### 3.6 EVENT 1 — wait for the UE to get an IP (with DEDUP heartbeat)
```bash
( ip -o monitor address | grep -qm1 "oaitun_ue1" ) & W_OK=$!          # SUCESSO
( tail -F --pid="$UEPID" "$UE_LOG" | grep -qm1 -E "…contains [0-9]{5}" ) & W_BAD=$!  # FLOOD/morte
( tail -F --pid="$UEPID" "$UE_LOG" \
    | grep -oiE "Initial sync successful|PBCH|Cell Detected|UE synchronized|RRCSetup|Registration (accept|complete)|PDU Session" \
    | awk '!seen[$0]++ { print "  ⏳ UE: " $0 " (marco · NÃO travou)" }' ) & W_HB=$!  # HEARTBEAT DEDUP
wait -n "$W_OK" "$W_BAD"   # retorna no 1º evento (IP, flood ≥10000, ou morte do UE)
```
Three processes running: **success** (IP via netlink), **failure** (RRC flood =
queue **≥ 5 digits / ≥10000**, detected early, or UE death via `--pid`) and
**DEDUP heartbeat** — `grep -o` extracts only **milestones** (sync, PBCH, RRCSetup,
Registration, PDU Session) and `awk '!seen[$0]++'` prints **each milestone only
once**. This avoids the hundreds of lines the old version generated (which still
stole CPU from the UE itself). `wait -n` returns on the first event. **`UEPID`**
comes from the scope's `MainPID` — the `tail --pid` processes end if the UE dies.
Zero `sleep`.

### 3.7 Traffic + EVENT 2 — collect K indications
```bash
sudo ping -I oaitun_ue1 8.8.8.8 >/dev/null 2>&1 & PING_PID=$!     # tráfego pelo túnel
KPM_SST=222 KPM_SD=123 "$XAPP" "${SMDIR[@]}" > "$LOG" 2>&1 & XAPP_PID=$!
# watchdog ANTI-HANG (por evento): se o UE morre, mata o xApp → o tail abaixo encerra
( tail -f --pid="$UEPID" /dev/null; kill "$XAPP_PID" ) & W_DEATH=$!
# heartbeat por indicação + parada na K-ésima (grep -m K):
while read _; do c=$((c+1)); info "⏳ indicação KPM $c/$NEED_IND (NÃO travou)"; done \
  < <(tail -n +1 -F --pid="$XAPP_PID" "$LOG" | grep --line-buffered -m "$NEED_IND" "KPM ind_msg latency")
```
- `grep -m "$NEED_IND"` terminates **exactly** on the K-th indication → success
  event. Each line read is a **heartbeat** ("indication c/K").
- `tail … --pid=$XAPP_PID` ends if the xApp dies.
- The **watchdog** `tail -f --pid=$UEPID /dev/null; kill $XAPP_PID` is the trick
  that **prevents freezing**: it blocks (no CPU) until the UE dies and then kills
  the xApp, making the collection's `tail` finish. This way neither "UE went down"
  nor "xApp stopped" hangs the script — all event-driven.

### 3.8 Honest verdict (always concludes)
```bash
"$SCRIPT_DIR/kpm_analytics.sh" "$LOG"          # analisa o que coletou
if [ "$got" = 1 ]; then summary "…DADOS reais ($n indicações)…" ok
else summary "…sem atingir a meta — problema: $problem…" warn; fi
```
It runs the analysis on the collected log and **always** gives a verdict: ✓ with
data, or ! concluded-without-failing with the observed problem (UE did not attach /
RRC flooded / xApp crashed / below the goal).

---

## 4. How to run

### 4.1 Through the panel (recommended for the presentation)
Project 2 → test group → **"Collect KPM with traffic (real, resilient)"**.
The console shows the live heartbeat (mirrored to the students) and, at the end, the
"what happened" explanation. The result is saved under "Saved results".

### 4.2 From the command line
```bash
cd ~/server/oai-cn-gnb-e2
# pré-requisito: E2 lab no ar (core + RIC + gNB)
SKIP_UE=1 ./scripts/up_e2_lab_v2.sh      # sobe sem UE (o coletor cuida do UE)
./scripts/kpm_collect_real.sh            # coleta resiliente → logs/xapp_kpm_lab.log
./scripts/kpm_analytics.sh               # (o coletor já chama; rode de novo se quiser)
```
Parameters (environment):
- `NEED_IND=20` — how many indications to collect (goal/success event).
- `MAX_TRIES=3` — attempts before concluding-with-what-there-is.

---

## 5. What you see (expected output)

**Working (heartbeat — did not freeze):**
```
⏳ aguardando UE attachar — gNB sincronizando rádio (… NÃO travou)
⏳ indicação KPM 7/20 recebida (NÃO travou)
```
**Success:**
```
✓ UE ATTACHED — oaitun_ue1 = 12.1.1.2
✓ meta atingida: 20 indicações coletadas
… (kpm_analytics: CSV + KPIs por UE + sparkline)
Resultado: concluído com DADOS reais em 1 tentativa(s)
```
**Handled failure (concludes without freezing):**
```
✗ tentativa 1: PROBLEMA — RRC inundou (CPU insuficiente p/ sincronizar — 2 vCPU é o limite)
→ repetindo automaticamente…
…
Resultado: concluído SEM falhar — problema: … (provável limite de 2 vCPU; ideal 4 vCPU)
```

---

## 6. Why it does NOT freeze the box (CPU safety)

- **Does NOT touch the cpuset** — the guardrail (1 core for the lab, CPU 0 free for
  system/SSH) stays intact. This is the main guarantee: without removing the
  guardrail, `sshd` is never starved → **no freeze**.
- **Stops the UE as soon as it detects failure** (flood/no attach) — does not let
  the RRC queue grow without bound (avoids memory pressure).
- The script is **event-bounded** (IP / flood ≥5 digits / process death / K
  indications) — no loop spins forever, no `sleep` wastes CPU.
- Runs **detached** (`nohup … &`): if SSH drops, the collector keeps going,
  concludes, and cleans up by itself; the result stays in the file.

> **Lesson from the 2 freezes:** both came from **removing the guardrail** (freeing
> 2 cores) — once with a VPP container that had no self-termination, once with this
> collector stuck waiting for an event that never came while the UE was flooding.
> The definitive fix was to **never touch the cpuset**; real data is left for the
> **4 vCPU upgrade** (§⚠️ at the top).

---

## 7. Troubleshooting

| Script message | Meaning | What to do |
|---|---|---|
| `RRC inundou (CPU insuficiente…)` | on 2 vCPU the UE does not sync in real time | run on **4 vCPU** (ideal) or accept the retry |
| `o nrUE caiu antes de pegar IP` | the UE process died | check `logs/ue_oai.log`; re-register the subscriber if it is SQN |
| `o xApp KPM encerrou antes da meta` | the xApp crashed/terminated | check `flexric-lib/libkpm_sm.so` (arm64 arch) |
| `coletou só N indicações` | UE attached but little traffic/time | increasing `NEED_IND` is counterproductive; make sure the ping is active |
| `gNB/RIC não está rodando` | the lab is not up | `./scripts/up_e2_lab_v2.sh` first |

---

## 8. Where this fits

```
kpm_collect_real.sh   →  logs/xapp_kpm_lab.log   →  kpm_analytics.sh  →  logs/kpm_timeseries.csv
   (coleta resiliente)        (telemetria real)        (ETL+KPI+viz)         (insumo do modelo)
                                                                                    │
                                                                                    ▼
                                                                      UE-TP-rApp (Módulo 7)
```
The resilient collection is the **missing step** between "E2/KPM works" and "I have
real data to model". With 4 vCPU it runs straight through; on 2 vCPU it tries,
reports, and concludes — always event-driven, never on a clock.
