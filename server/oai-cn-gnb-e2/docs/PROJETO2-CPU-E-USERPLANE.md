# Projeto 2 — Reprodução até o user plane (UE com IP) e dimensionamento de CPU

Guia **definitivo** para um colaborador sair do zero e chegar ao estado validado em
2026-06-22 no servidor Graviton: **Core OAI v2.2.1 + near-RT RIC + gNB (E2) + os 3 xApps
(KPM/cust/RC) + UE com IP real e tráfego pelo túnel 5G**.

Este documento foca em **CPU e user plane** — a parte que mais confunde e onde está o
trade-off importante. Para o que já está coberto em outros guias, ele aponta o link em vez
de repetir:

- **Compilar as imagens arm64 do Core** (AMF/SMF/NRF/UDR/UDM/AUSF + **oai-upf-vpp**):
  [`OAI-CORE-ARM64.md`](OAI-CORE-ARM64.md) e [bíblia §7.b](../../../core5g-arm64-bible.md).
- **Build do gNB/nrUE/FlexRIC + Service Models**: [`TUTORIAL_LAB_E2.md`](TUTORIAL_LAB_E2.md),
  [`INSTALACAO_GNB_OAI.md`](INSTALACAO_GNB_OAI.md), [`E2_FLEXRIC.md`](E2_FLEXRIC.md).
- **Regra de ouro do projeto:** nunca edite arquivos direto no servidor. Edite em `server/`
  na sua máquina e use `./deploy.sh` (e `./deploy.sh sync-oai` para este diretório).

---

## 0. TL;DR — o que você vai obter e o trade-off de CPU

| Bloco | Como validar | Depende do UE? |
|---|---|---|
| Core 5G (9 NFs) healthy | `docker ps` todos `healthy` | não |
| **E2 SETUP** gNB ↔ RIC | `[E2-AGENT]: E2 SETUP RESPONSE rx` no log do gNB | não |
| **xApps** KPM / cust / RC | `Successfully subscribed to RAN_FUNC_ID 2 / 142 / 3` | não |
| **User plane** (UE pega IP + ping) | `oaitun_ue1 = 12.1.1.2`, `ping 8.8.8.8` 0% perda | **sim** |

> **A regra que resume tudo:** o E2/RIC/xApps são **gNB↔RIC** e **não precisam do UE**. O
> user plane (UE com IP) precisa do nrUE rodando — e o nrUE é o que estoura a CPU.

**Dimensionamento (leia a §1 antes de subir nada):**
- **4 vCPU (recomendado):** tudo roda junto, sem truques, sem risco de freeze.
- **2 vCPU (alternativo — o que temos hoje):** ou você protege a máquina (guardrail de 1
  core, **sem** UE) **ou** roda o user plane completo (2 cores, box dedicado). Não dá os dois
  ao mesmo tempo. A §4 mostra como fazer o teste de user plane com segurança.

---

## 1. Dimensionamento de CPU — por que 4 vCPU é melhor

O gNB (`nr-softmodem`) e o UE (`nr-uesoftmodem`) rodam em **RFSIM** (rádio em software). Cada
um faz **busy-poll**: satura ~1 vCPU inteiro de forma contínua (não é pico — é constante,
porque o loop de samples roda em tempo real). Some o near-RT RIC e o sistema (sshd, Docker,
Caddy, painel) e você precisa de **núcleos suficientes para todos**.

### Conta de núcleos

| Processo | Demanda de CPU |
|---|---|
| `nr-softmodem` (gNB RFSIM) | ~1 core dedicado |
| `nr-uesoftmodem` (UE RFSIM) | ~1 core dedicado |
| `nearRT-RIC` + xApp | fração de 1 core (picos no INDICATION→Report) |
| Sistema (sshd, Docker, Caddy, painel, Core) | ~1 core |

→ **O lab completo COM user plane quer ~4 núcleos.** Por isso:

### Recomendado: instância de 4 vCPU

**AWS:** `t4g.xlarge` (4 vCPU / 16 GB) ou `c7g.xlarge` (4 vCPU / 8 GB), Graviton, Ubuntu
22.04+. Com 4 vCPU:
- gNB num core, UE noutro, RIC+xApp noutro, sistema noutro.
- **Sem cpuset, sem guardrail, sem freeze.** O UE attacha e os xApps rodam **ao mesmo tempo**.
- É o caminho que um colaborador deve preferir para desenvolver o **UE-TP-rApp** (precisa de
  KPM por UE **com** o UE ativo gerando tráfego).

> Se você for subir uma instância nova, **suba 4 vCPU**. Custa um pouco mais, mas elimina
> todo o resto desta seção.

### Alternativo: 2 vCPU (o box atual — `t4g.medium`)

Com só 2 núcleos, gNB + UE + sistema não cabem em tempo real. Em 2019–2026 isso causou
**congelamentos e reboots** (o gNB+UE saturavam os 2 vCPUs e o `sshd` morria — a máquina
ficava inacessível). A defesa foi um **guardrail por cpuset**:

```
oai-lab.slice  →  AllowedCPUs=1     # todo o lab (gNB+UE+RIC) pinado no CPU 1
                                    # CPU 0 fica reservado p/ sistema (sshd/Docker/painel)
```

Esse guardrail **mantém a máquina viva sob carga** (SSH ~2,5 s mesmo com o gNB no talo), mas
tem um custo: gNB e UE passam a **dividir um único core**. Resultado medido:

- O UE **sincroniza** (PHY/RFSIM OK: `Initial sync successful, PCI 0`, RSRP 51 dB)…
- …mas o **RRC inunda** — a fila `TASK_RRC_NRUE task contains …` cresce sem parar
  (71k → 112k → …) porque o UE não recebe CPU suficiente para processar RRC em tempo real
  (o gNB tem `CPUWeight=60`, o UE só `CPUWeight=20`).
- **O UE nunca pega IP.**

Por isso a validação canônica do P2 (E2 + xApps) roda **sem o UE** (`SKIP_UE=1`). Para testar
o user plane no box de 2 vCPU, é preciso **liberar temporariamente os 2 cores** — veja a §4.

---

## 2. Pré-requisitos

1. **Imagens arm64 do Core carregadas no servidor** (incluindo, opcionalmente, `oai-upf-vpp`).
   Ver [`OAI-CORE-ARM64.md`](OAI-CORE-ARM64.md). O lab usa o `oai-upf` (simple_switch) do
   v2.2.1 — o `oai-upf-vpp` é opcional (ver §6).
2. **gNB/nrUE/FlexRIC compilados** no servidor (`openairinterface5g/` + `flexric-lib/`).
   Ver [`TUTORIAL_LAB_E2.md`](TUTORIAL_LAB_E2.md) e [`INSTALACAO_GNB_OAI.md`](INSTALACAO_GNB_OAI.md).
3. **Diretório sincronizado:** `./deploy.sh sync-oai` (envia `server/oai-cn-gnb-e2/`).
4. **Projeto 1 parado** (P1 e P2 são mutuamente exclusivos): `./deploy.sh down all`.

Parâmetros do lab (já configurados, casam entre gNB e core v2.2.1):

| Item | Valor |
|---|---|
| PLMN | 208 / 95 |
| Slice | SST 222 / SD 123 |
| DNN | `default` (pool **12.1.1.0/26**) |
| gNB | `gnb_24prb.conf`, NRB=51, f=3469440000 Hz, banda n78 |
| nrUE | `--rfsim -r 51 --numerology 1 --band 78 -C 3469440000 --ssb 186` |
| AMF | 192.168.70.132 |

---

## 3. Caminho principal — subir e validar (E2 + xApps)

Conecte ao servidor (`./deploy.sh ssh`) e:

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

> **Princípio do projeto: ZERO tempo.** Os scripts terminam por **evento/estado**
> (`grep -m1` em stream, `tail -F --pid`, espera-até-condição), nunca por `sleep`/timeout
> cego. Ver memória `feedback-event-driven-nao-tempo` e bíblia §7.c.

Resultado medido (2026-06-22): **E2 SETUP OK**, **KPM/cust/RC os três subscritos**. Esse é o
deliverable avaliado do Projeto 2 e **não depende do UE**.

---

## 4. User plane — UE com IP + ping pelo túnel 5G

> **O que prova:** que o caminho de dados está completo — UE registra (NAS/5G-AKA), abre PDU
> session, ganha IP no pool `12.1.1.0/26` e tem conectividade real pela interface
> `oaitun_ue1`. Resultado medido: `oaitun_ue1 = 12.1.1.2`, `ping 8.8.8.8` → **4/4, 0% perda,
> RTT ~111 ms**.

### 4.a — Em 4 vCPU (recomendado): simplesmente suba com o UE

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

Em 4 vCPU isso funciona direto, **sem mexer em cpuset**, e você ainda pode rodar os xApps em
paralelo (sobra núcleo para o RIC+xApp). É o ambiente correto para desenvolver o
**UE-TP-rApp** (KPM por UE com tráfego real).

### 4.b — Em 2 vCPU (alternativo): liberar os 2 cores com segurança

No box de 2 vCPU, o UE só attacha se o lab usar **os dois núcleos** (`AllowedCPUs=0-1`) — o
que **remove o guardrail anti-freeze**. Para fazer isso sem travar a máquina e **sem nenhum
timer**, use o procedimento abaixo (validado em 2026-06-22). A segurança vem de **evento +
prioridade**, não de cronômetro:

- **`trap revert EXIT`** — o cpuset volta a `1` quando o processo termina (não por relógio).
- **Espera por evento puro** (`wait -n` entre dois watchers bloqueantes):
  - sucesso = `ip monitor address` captura o `oaitun_ue1` ganhando endereço (evento netlink);
  - falha = `tail -F --pid | grep -m1` detecta o flood do RRC.
- **`nice -20`** no monitor → ele é sempre escalonado e consegue reverter **mesmo se o lab
  saturar os 2 cores**.

Script (`scripts/ue_userplane_2cores.sh` — crie a partir deste bloco; é seguro e auto-reverte):

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

Depois de rodar, **confirme o revert**:

```bash
systemctl show oai-lab.slice -p AllowedCPUs --value     # → 1   (guardrail restaurado)
pgrep -x nr-uesoftmodem && echo "UE ON (revert falhou!)" || echo "UE OFF (ok)"
```

> ⚠️ **Por que não deixar os 2 cores ligados permanentemente:** sem o guardrail, um pico de
> gNB+UE pode sufocar o `sshd` e **travar a instância** (já aconteceu — exigiu reboot). O
> procedimento acima é para **provar** o user plane e **voltar ao estado seguro**. Se você
> quer o UE rodando de forma estável e contínua, **migre para 4 vCPU** (§1).

---

## 5. Estado final esperado e como deixar o servidor

Estado seguro (E2/xApps validados, guardrail ativo, UE off):

```bash
docker ps --format '{{.Names}}' | grep -cE 'oai-|mysql'    # 9
pgrep -x nearRT-RIC && pgrep -x nr-softmodem               # RIC e gNB ON
pgrep -x nr-uesoftmodem || echo "UE OFF"                   # UE off (seguro em 2 vCPU)
systemctl show oai-lab.slice -p AllowedCPUs --value        # 1
uptime                                                     # load baixo
```

Parar tudo: `./scripts/down_e2_lab.sh` e `./oai-cn5g-v2/down_core_v2.sh`.

---

## 6. `oai-upf-vpp` em arm64 (opcional)

O lab usa o `oai-upf` (simple_switch) do v2.2.1, que **já é multi-arch oficial**. O
`oai-upf-vpp` (dataplane VPP, mais rápido) foi **portado para arm64** neste projeto (era tido
como "não portável") — o bloqueio era só o Hyperscan (Intel-only), resolvido com **Vectorscan**
(fork ARM drop-in). Detalhes, build e validação em [bíblia §7.b](../../../core5g-arm64-bible.md)
e `artifacts/oai-images/oai-upf-vpp.tar`. **Não é necessário** para o user plane deste lab.

---

## 7. Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| UE não pega IP; `TASK_RRC_NRUE task contains` crescendo | CPU insuficiente (2 vCPU + guardrail = gNB e UE num core só) | §4.b (liberar 2 cores) ou migrar p/ 4 vCPU (§1) |
| SSH cai (`Connection reset` / `timed out`) sob carga | box saturado; processo pesado roubou o CPU 0 do `sshd` | trabalhe **destacado** (`nohup` + arquivo no servidor) e use `ssh -o ServerAliveInterval=10`; nunca rode processo pesado **fora** do `oai-lab.slice` |
| Máquina travou / inacessível | guardrail off + gNB+UE saturando os 2 cores | reboot pela console AWS; nunca deixe os 2 cores liberados sem o procedimento auto-revert da §4.b |
| `Authentication Failure ... SQN out of range` | SQN do assinante dessincronizou | recadastrar (`add-subscriber.sh`) e reiniciar o UE |
| gNB log: `No connected device, generating void samples` | é normal **antes** do nrUE conectar ao RFSIM (:4043); vira `RFsim: Number of antennas changed 0→1` quando conecta | aguardar o nrUE; se persistir, o nrUE morreu — ver `logs/ue_oai.log` |
| `exec format error` ao subir imagem do Core | imagem amd64 num host arm64 | carregar a imagem arm64 correta (`OAI-CORE-ARM64.md`) |

---

## 8. Referência rápida de comandos

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
