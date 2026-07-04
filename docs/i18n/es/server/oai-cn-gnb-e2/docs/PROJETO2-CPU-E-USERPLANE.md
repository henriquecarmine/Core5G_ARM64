<!-- sync: e36a3f4e -->
> 🌐 Traducción al **español** del documento canónico en portugués [`server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md`](../../../../../../server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md). Todos los idiomas: [INDEX](../../../INDEX.md) · sincronización verificada por `docs/i18n/check-parity.py`.

# Proyecto 2 — Reproducción hasta el user plane (UE con IP) y dimensionamiento de CPU

Guía **definitiva** para que un colaborador parta de cero y llegue al estado validado el
2026-06-22 en el servidor Graviton: **Core OAI v2.2.1 + near-RT RIC + gNB (E2) + los 3 xApps
(KPM/cust/RC) + UE con IP real y tráfico por el túnel 5G**.

Este documento se centra en **CPU y user plane** — la parte que más confunde y donde está el
trade-off importante. Para lo que ya está cubierto en otras guías, apunta al enlace en vez
de repetir:

- **Compilar las imágenes arm64 del Core** (AMF/SMF/NRF/UDR/UDM/AUSF + **oai-upf-vpp**):
  [`OAI-CORE-ARM64.md`](OAI-CORE-ARM64.md) y [biblia §7.b](../../../../../../core5g-arm64-bible.md).
- **Build del gNB/nrUE/FlexRIC + Service Models**: [`TUTORIAL_LAB_E2.md`](TUTORIAL_LAB_E2.md),
  [`INSTALACAO_GNB_OAI.md`](INSTALACAO_GNB_OAI.md), [`E2_FLEXRIC.md`](E2_FLEXRIC.md).
- **Regla de oro del proyecto:** nunca edites archivos directamente en el servidor. Edita en `server/`
  en tu máquina y usa `./deploy.sh` (y `./deploy.sh sync-oai` para este directorio).

---

## 0. TL;DR — qué vas a obtener y el trade-off de CPU

| Bloque | Cómo validar | ¿Depende del UE? |
|---|---|---|
| Core 5G (9 NFs) healthy | `docker ps` todos `healthy` | no |
| **E2 SETUP** gNB ↔ RIC | `[E2-AGENT]: E2 SETUP RESPONSE rx` en el log del gNB | no |
| **xApps** KPM / cust / RC | `Successfully subscribed to RAN_FUNC_ID 2 / 142 / 3` | no |
| **User plane** (el UE obtiene IP + ping) | `oaitun_ue1 = 12.1.1.2`, `ping 8.8.8.8` 0% de pérdida | **sí** |

> **La regla que lo resume todo:** el E2/RIC/xApps son **gNB↔RIC** y **no necesitan el UE**. El
> user plane (UE con IP) necesita el nrUE en ejecución — y el nrUE es lo que dispara la CPU.

**Dimensionamiento (lee la §1 antes de levantar nada):**
- **4 vCPU (recomendado):** todo corre junto, sin trucos, sin riesgo de freeze.
- **2 vCPU (alternativo — lo que tenemos hoy):** o proteges la máquina (guardrail de 1
  core, **sin** UE) **o** corres el user plane completo (2 cores, box dedicado). No se pueden los dos
  al mismo tiempo. La §4 muestra cómo hacer la prueba de user plane con seguridad.

---

## 1. Dimensionamiento de CPU — por qué 4 vCPU es mejor

El gNB (`nr-softmodem`) y el UE (`nr-uesoftmodem`) corren en **RFSIM** (radio por software). Cada
uno hace **busy-poll**: satura ~1 vCPU entero de forma continua (no es un pico — es constante,
porque el loop de samples corre en tiempo real). Suma el near-RT RIC y el sistema (sshd, Docker,
Caddy, panel) y necesitas **núcleos suficientes para todos**.

### Cuenta de núcleos

| Proceso | Demanda de CPU |
|---|---|
| `nr-softmodem` (gNB RFSIM) | ~1 core dedicado |
| `nr-uesoftmodem` (UE RFSIM) | ~1 core dedicado |
| `nearRT-RIC` + xApp | fracción de 1 core (picos en INDICATION→Report) |
| Sistema (sshd, Docker, Caddy, panel, Core) | ~1 core |

→ **El lab completo CON user plane requiere ~4 núcleos.** Por eso:

### Recomendado: instancia de 4 vCPU

**AWS:** `t4g.xlarge` (4 vCPU / 16 GB) o `c7g.xlarge` (4 vCPU / 8 GB), Graviton, Ubuntu
22.04+. Con 4 vCPU:
- gNB en un core, UE en otro, RIC+xApp en otro, sistema en otro.
- **Sin cpuset, sin guardrail, sin freeze.** El UE hace attach y los xApps corren **al mismo tiempo**.
- Es el camino que un colaborador debería preferir para desarrollar el **UE-TP-rApp** (necesita
  KPM por UE **con** el UE activo generando tráfico).

> Si vas a levantar una instancia nueva, **levanta 4 vCPU**. Cuesta un poco más, pero elimina
> todo el resto de esta sección.

### Alternativo: 2 vCPU (el box actual — `t4g.medium`)

Con solo 2 núcleos, gNB + UE + sistema no caben en tiempo real. En 2019–2026 esto causó
**congelamientos y reboots** (el gNB+UE saturaban los 2 vCPUs y el `sshd` moría — la máquina
quedaba inaccesible). La defensa fue un **guardrail por cpuset**:

```
oai-lab.slice  →  AllowedCPUs=1     # todo o lab (gNB+UE+RIC) pinado no CPU 1
                                    # CPU 0 fica reservado p/ sistema (sshd/Docker/painel)
```

Este guardrail **mantiene la máquina viva bajo carga** (SSH ~2,5 s incluso con el gNB a tope), pero
tiene un costo: gNB y UE pasan a **compartir un único core**. Resultado medido:

- El UE **sincroniza** (PHY/RFSIM OK: `Initial sync successful, PCI 0`, RSRP 51 dB)…
- …pero el **RRC se inunda** — la cola `TASK_RRC_NRUE task contains …` crece sin parar
  (71k → 112k → …) porque el UE no recibe CPU suficiente para procesar RRC en tiempo real
  (el gNB tiene `CPUWeight=60`, el UE solo `CPUWeight=20`).
- **El UE nunca obtiene IP.**

Por eso la validación canónica del P2 (E2 + xApps) corre **sin el UE** (`SKIP_UE=1`). Para probar
el user plane en el box de 2 vCPU, es necesario **liberar temporalmente los 2 cores** — mira la §4.

---

## 2. Requisitos previos

1. **Imágenes arm64 del Core cargadas en el servidor** (incluyendo, opcionalmente, `oai-upf-vpp`).
   Ver [`OAI-CORE-ARM64.md`](OAI-CORE-ARM64.md). El lab usa el `oai-upf` (simple_switch) del
   v2.2.1 — el `oai-upf-vpp` es opcional (ver §6).
2. **gNB/nrUE/FlexRIC compilados** en el servidor (`openairinterface5g/` + `flexric-lib/`).
   Ver [`TUTORIAL_LAB_E2.md`](TUTORIAL_LAB_E2.md) y [`INSTALACAO_GNB_OAI.md`](INSTALACAO_GNB_OAI.md).
3. **Directorio sincronizado:** `./deploy.sh sync-oai` (envía `server/oai-cn-gnb-e2/`).
4. **Proyecto 1 detenido** (P1 y P2 son mutuamente excluyentes): `./deploy.sh down all`.

Parámetros del lab (ya configurados, coinciden entre gNB y core v2.2.1):

| Item | Valor |
|---|---|
| PLMN | 208 / 95 |
| Slice | SST 222 / SD 123 |
| DNN | `default` (pool **12.1.1.0/26**) |
| gNB | `gnb_24prb.conf`, NRB=51, f=3469440000 Hz, banda n78 |
| nrUE | `--rfsim -r 51 --numerology 1 --band 78 -C 3469440000 --ssb 186` |
| AMF | 192.168.70.132 |

---

## 3. Camino principal — levantar y validar (E2 + xApps)

Conéctate al servidor (`./deploy.sh ssh`) y:

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

> **Principio del proyecto: CERO tiempo.** Los scripts terminan por **evento/estado**
> (`grep -m1` en stream, `tail -F --pid`, espera-hasta-condición), nunca por `sleep`/timeout
> ciego. Ver la memoria `feedback-event-driven-nao-tempo` y la biblia §7.c.

Resultado medido (2026-06-22): **E2 SETUP OK**, **KPM/cust/RC los tres suscritos**. Ese es el
entregable evaluado del Proyecto 2 y **no depende del UE**.

---

## 4. User plane — UE con IP + ping por el túnel 5G

> **Qué demuestra:** que el camino de datos está completo — el UE registra (NAS/5G-AKA), abre PDU
> session, obtiene IP en el pool `12.1.1.0/26` y tiene conectividad real por la interfaz
> `oaitun_ue1`. Resultado medido: `oaitun_ue1 = 12.1.1.2`, `ping 8.8.8.8` → **4/4, 0% de pérdida,
> RTT ~111 ms**.

### 4.a — En 4 vCPU (recomendado): simplemente levanta con el UE

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

En 4 vCPU esto funciona de inmediato, **sin tocar cpuset**, y todavía puedes correr los xApps en
paralelo (sobra núcleo para el RIC+xApp). Es el entorno correcto para desarrollar el
**UE-TP-rApp** (KPM por UE con tráfico real).

### 4.b — En 2 vCPU (alternativo): liberar los 2 cores con seguridad

En el box de 2 vCPU, el UE solo hace attach si el lab usa **los dos núcleos** (`AllowedCPUs=0-1`) — lo
que **elimina el guardrail anti-freeze**. Para hacer esto sin colgar la máquina y **sin ningún
timer**, usa el procedimiento de abajo (validado el 2026-06-22). La seguridad viene de **evento +
prioridad**, no de cronómetro:

- **`trap revert EXIT`** — el cpuset vuelve a `1` cuando el proceso termina (no por reloj).
- **Espera por evento puro** (`wait -n` entre dos watchers bloqueantes):
  - éxito = `ip monitor address` captura el `oaitun_ue1` obteniendo dirección (evento netlink);
  - fallo = `tail -F --pid | grep -m1` detecta el flood del RRC.
- **`nice -20`** en el monitor → siempre se planifica y logra revertir **incluso si el lab
  satura los 2 cores**.

Script (`scripts/ue_userplane_2cores.sh` — créalo a partir de este bloque; es seguro y se auto-revierte):

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

Después de ejecutarlo, **confirma el revert**:

```bash
systemctl show oai-lab.slice -p AllowedCPUs --value     # → 1   (guardrail restaurado)
pgrep -x nr-uesoftmodem && echo "UE ON (revert falhou!)" || echo "UE OFF (ok)"
```

> ⚠️ **Por qué no dejar los 2 cores encendidos permanentemente:** sin el guardrail, un pico de
> gNB+UE puede ahogar el `sshd` y **colgar la instancia** (ya pasó — exigió reboot). El
> procedimiento anterior es para **demostrar** el user plane y **volver al estado seguro**. Si
> quieres el UE en ejecución de forma estable y continua, **migra a 4 vCPU** (§1).

---

## 5. Estado final esperado y cómo dejar el servidor

Estado seguro (E2/xApps validados, guardrail activo, UE off):

```bash
docker ps --format '{{.Names}}' | grep -cE 'oai-|mysql'    # 9
pgrep -x nearRT-RIC && pgrep -x nr-softmodem               # RIC e gNB ON
pgrep -x nr-uesoftmodem || echo "UE OFF"                   # UE off (seguro em 2 vCPU)
systemctl show oai-lab.slice -p AllowedCPUs --value        # 1
uptime                                                     # load baixo
```

Detener todo: `./scripts/down_e2_lab.sh` y `./oai-cn5g-v2/down_core_v2.sh`.

---

## 6. `oai-upf-vpp` en arm64 (opcional)

El lab usa el `oai-upf` (simple_switch) del v2.2.1, que **ya es multi-arch oficial**. El
`oai-upf-vpp` (dataplane VPP, más rápido) fue **portado a arm64** en este proyecto (se consideraba
"no portable") — el bloqueo era solo el Hyperscan (Intel-only), resuelto con **Vectorscan**
(fork ARM drop-in). Detalles, build y validación en [biblia §7.b](../../../../../../core5g-arm64-bible.md)
y `artifacts/oai-images/oai-upf-vpp.tar`. **No es necesario** para el user plane de este lab.

---

## 7. Troubleshooting

| Síntoma | Causa probable | Acción |
|---|---|---|
| El UE no obtiene IP; `TASK_RRC_NRUE task contains` creciendo | CPU insuficiente (2 vCPU + guardrail = gNB y UE en un solo core) | §4.b (liberar 2 cores) o migrar a 4 vCPU (§1) |
| El SSH se cae (`Connection reset` / `timed out`) bajo carga | box saturado; un proceso pesado robó el CPU 0 del `sshd` | trabaja **desacoplado** (`nohup` + archivo en el servidor) y usa `ssh -o ServerAliveInterval=10`; nunca corras un proceso pesado **fuera** del `oai-lab.slice` |
| La máquina se colgó / inaccesible | guardrail off + gNB+UE saturando los 2 cores | reboot por la consola AWS; nunca dejes los 2 cores liberados sin el procedimiento auto-revert de la §4.b |
| `Authentication Failure ... SQN out of range` | el SQN del suscriptor se desincronizó | volver a registrar (`add-subscriber.sh`) y reiniciar el UE |
| gNB log: `No connected device, generating void samples` | es normal **antes** de que el nrUE conecte al RFSIM (:4043); pasa a `RFsim: Number of antennas changed 0→1` cuando conecta | esperar al nrUE; si persiste, el nrUE murió — ver `logs/ue_oai.log` |
| `exec format error` al levantar imagen del Core | imagen amd64 en un host arm64 | cargar la imagen arm64 correcta (`OAI-CORE-ARM64.md`) |

---

## 8. Referencia rápida de comandos

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
