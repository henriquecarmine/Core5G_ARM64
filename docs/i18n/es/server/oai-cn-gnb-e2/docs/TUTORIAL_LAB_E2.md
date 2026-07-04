<!-- sync: e8f9da69 -->
> 🌐 Traducción al **español** del documento canónico en portugués [`server/oai-cn-gnb-e2/docs/TUTORIAL_LAB_E2.md`](../../../../../../server/oai-cn-gnb-e2/docs/TUTORIAL_LAB_E2.md). Todos los idiomas: [INDEX](../../../INDEX.md) · sincronización verificada por `docs/i18n/check-parity.py`.

# Tutorial — Laboratorio OAI + Interfaz E2 (FlexRIC)

Guía paso a paso para reproducir el laboratorio **5G SA nativo** (Core Docker + gNB/nrUE RFSIM + nearRT-RIC + xApps) con pruebas de **Service Models E2** (custom, RC, KPM).

> **Alcance:** este lab corre en el **host** (Docker solo para el Core). **No** utiliza Kind multicluster ni integración con SD-RAN/Aether.

> **Imágenes del Core en arm64:** las imágenes `oaisoftwarealliance/*:v1.5.1` no existen en DockerHub para `linux/arm64`. Fueron compiladas de forma nativa en este proyecto. Consulta la guía completa en [OAI-CORE-ARM64.md](OAI-CORE-ARM64.md) antes de intentar levantar el Core en un host Graviton2/Apple Silicon.

---

## 1. Resultados obtenidos (resumen)

| Procedimiento | Estado | Evidencia |
|--------------|--------|-----------|
| Core OAI (UPF-VPP, scenario 1) | ✅ OK | Contenedores `oai-amf`, `oai-smf`, `oai-upf`, … |
| Build gNB + nrUE con E2 agent | ✅ OK | `nr-softmodem` con `--build-e2`, FlexRIC branch `dev` |
| Build nearRT-RIC + xApps (submodule) | ✅ OK | `build_flexric_tools.sh` |
| Attach UE (IMSI 208950000000032, slice 222/123) | ✅ OK | `RRCSetupComplete`, PDU session |
| E2 SETUP (gNB ↔ nearRT-RIC) | ✅ OK | `[E2-AGENT]: E2 SETUP RESPONSE rx` |
| Custom SMs (MAC/RLC/PDCP/GTP, IDs 142–148) | ✅ OK | `xapp_cust_moni`, E2 node registrado |
| **E2SM-RC** v1.03 | ✅ OK | INDICATION con `RRCSetupComplete` decodificado (ASN.1) |
| **E2SM-KPM** v2.03 (slice 222/123) | ✅ OK | INDICATIONs periódicas con `DRB.UEThp*`, `RRU.PrbTot*` |
| PoC KPM+RC (`xapp_kpm_rc`) | ⚠️ No validado end-to-end | Binario compilado; usar tras KPM/RC aislados |
| SLICE / TC (emuladores FlexRIC) | ❌ N/A | No soportados en el agente E2 del gNB OAI monolítico |

**Versiones alineadas:** E2AP v2 (`E2AP_V2`) + E2SM-KPM v2.03 (`KPM_V2_03`), branch FlexRIC **`dev`**.

---

## 2. Arquitectura

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

## 3. Prerrequisitos

- Ubuntu 22.04+ con Docker, Python 3, sudo
- ~8 GB de RAM libre, ~15 GB de disco (Core + build OAI + FlexRIC)
- IPv4 forwarding: `sudo sysctl -w net.ipv4.ip_forward=1`
- Cuenta Docker Hub (pull de imágenes OAI)

Documentación complementaria:

- [INSTALACAO_GNB_OAI.md](INSTALACAO_GNB_OAI.md) — dependencias y build base del RAN
- [SLIDES_LAB_E2.md](../../../../../../server/oai-cn-gnb-e2/docs/SLIDES_LAB_E2.md) — presentación de los resultados (formato Marp)
- [E2_FLEXRIC.md](E2_FLEXRIC.md) — operación E2/FlexRIC
- [E2_SERVICE_MODELS.md](E2_SERVICE_MODELS.md) — detalles RC/KPM/custom SMs

---

## 4. Preparación (una vez)

### 4.1 Clonar / entrar en el proyecto

```bash
cd ric/code/oai-cn-gnb-e2
```

### 4.2 Instalar dependencias OAI

```bash
cd openairinterface5g/cmake_targets
./build_oai --ninja -I
cd ../..
```

### 4.3 Compilar gNB + nrUE **con agente E2**

```bash
./scripts/build_e2.sh
```

Salida esperada (final):

```
Build concluído. Binários em: openairinterface5g/cmake_targets/ran_build/build/
  nr-softmodem (com E2 agent)
  nr-uesoftmodem
```

Log completo: `logs/build_e2.log`

### 4.4 Compilar nearRT-RIC, Service Models y xApps

```bash
./scripts/build_flexric_tools.sh
```

Esto compila:

- `nearRT-RIC` (submodule FlexRIC)
- SMs: `libkpm_sm.so`, `librc_sm.so`, `libmac_sm.so`, …
- xApps: `xapp_kpm_moni`, `xapp_rc_moni`, `xapp_kpm_rc`, …

Las libs se copian a **`flexric-lib/`** (path local del proyecto).

> **Importante:** el Core OAI usa **AMF Region ID = 128**. La `libkpm_sm.so` instalada en `/usr/local/lib/flexric/` (versión antigua) **fallaba** al generar INDICATIONs KPM. Usa siempre **`flexric-lib/`** del submodule `dev`.

---

## 5. Levantar el laboratorio

### Opción A — Lab completo E2 (recomendado)

```bash
./scripts/up_e2_lab.sh
```

Secuencia: Core → nearRT-RIC → gNB + nrUE (con `--e2_agent.sm_dir flexric-lib/`).

### Opción B — Paso a paso manual

```bash
# 1. Core 5G (UPF-VPP, scenario 1)
./scripts/up_core.sh

# 2. nearRT-RIC (submodule dev + flexric-lib/)
./scripts/up_flexric.sh

# 3. gNB + nrUE (RFSIM, slice 222/123)
./scripts/up_gnb_oai.sh
```

### Verificar Core

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep oai
```

Ejemplo:

```
oai-amf     Up ...
oai-smf     Up ...
oai-upf     Up ...
```

### Verificar E2 en el gNB

```bash
grep -E '\[E2 AGENT\]|\[E2-AGENT\]' logs/gnb_oai.log | tail -15
```

Log esperado (con `flexric-lib/`):

```
[E2 NODE]: Args 127.0.0.1 .../flexric-lib/
[E2 AGENT]: nearRT-RIC IP Address = 127.0.0.1, PORT = 36421, RAN type = ngran_gNB, nb_id = 3584
[E2 AGENT]: Opening plugin from path = .../flexric-lib/libkpm_sm.so
[E2-AGENT]: E2 SETUP-REQUEST tx
[E2-AGENT]: E2 SETUP RESPONSE rx
```

### Verificar attach del UE

```bash
grep RRCSetupComplete logs/gnb_oai.log | tail -3
grep -i registered logs/ue_oai.log | tail -3
```

---

## 6. Pruebas E2 — Service Models

### 6.1 Custom SMs (MAC, RLC, PDCP, GTP)

Plain encoding; funciona independientemente del slice.

```bash
./scripts/test_e2_sm.sh cust
# ou exploração rápida:
./scripts/explore_e2_sm.sh quick
```

Log típico (`logs/xapp_cust_moni.log`):

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

Orden crítico: **RIC → xApp RC → gNB → UE** (suscripción antes del attach).

```bash
./scripts/test_e2_rc_attach.sh
```

Log típico (`logs/xapp_rc_attach.log`):

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

> **Nota:** el `xapp_rc_moni` puede terminar con timeout en `sync_ui.c` después de la **primera** INDICATION — comportamiento conocido del ejemplo upstream. La INDICATION ya fue capturada antes del crash.

### 6.3 E2SM-KPM (métricas 3GPP, slice lab)

Slice alineado con el Core/AMF: **SST=222, SD=123** (ver `openairinterface5g/scripts/ue.conf` y `gnb.conf`).

```bash
./scripts/test_e2_kpm.sh

# Parâmetros opcionais:
KPM_SST=222 KPM_SD=123 XAPP_DURATION=45 KPM_TRAFFIC=1 ./scripts/test_e2_kpm.sh
```

Log típico (`logs/xapp_kpm_lab.log`):

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

Con `KPM_TRAFFIC=1` (por defecto), el script genera ping hacia el DN (`192.168.73.135`) vía la interfaz UE (`12.1.1.x`), aumentando el throughput medido.

### 6.4 Exploración por suite

```bash
./scripts/explore_e2_sm.sh rc      # foco RC
./scripts/explore_e2_sm.sh kpm     # foco KPM
./scripts/explore_e2_sm.sh oran    # KPM + RC
./scripts/explore_e2_sm.sh layers  # custom MAC/RLC/PDCP/GTP
./scripts/explore_e2_sm.sh full    # todas (demorado)
```

---

## 7. Detener el laboratorio

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

## 8. Configuración relevante

| Parámetro | Valor lab | Archivo |
|-----------|-----------|----------|
| PLMN | 208 / 95 | `gnb.conf`, `ue.conf` |
| S-NSSAI | SST **222**, SD **123** | `gnb.conf`, `ue.conf` |
| IMSI UE | 208950000000032 | `ue.conf` |
| AMF IP (gNB) | 192.168.70.129 (host, iface `demo-oai`) | `gnb.conf` |
| nearRT-RIC | 127.0.0.1:36421 | `gnb.conf` → `e2_agent.near_ric_ip_addr` |
| SMs E2 | `flexric-lib/` (proyecto) | `--e2_agent.sm_dir` en los scripts |
| KPM filtro slice | `KPM_SST=222`, `KPM_SD=123` | env vars en los scripts KPM |

Ejemplo de `e2_agent` en `openairinterface5g/scripts/gnb.conf`:

```
e2_agent = {
  near_ric_ip_addr = "127.0.0.1";
  sm_dir = ".../flexric-lib/";   # override via --e2_agent.sm_dir nos scripts
};
```

---

## 9. Scripts de referencia

| Script | Función |
|--------|--------|
| `build_e2.sh` | Compila gNB/nrUE con E2 agent |
| `build_flexric_tools.sh` | Compila RIC, SMs, xApps; puebla `flexric-lib/` |
| `sync_flexric_lib.sh` | Copia los `.so` del build FlexRIC → `flexric-lib/` |
| `up_e2_lab.sh` | Core + RIC + gNB + UE |
| `up_flexric.sh` / `down_flexric.sh` | nearRT-RIC |
| `up_gnb_oai.sh` / `down_gnb_oai.sh` | gNB + nrUE |
| `test_e2_kpm.sh` | Prueba KPM slice 222/123 |
| `test_e2_rc_attach.sh` | Prueba RC con attach nuevo |
| `test_e2_sm.sh` | Pruebas por SM (`cust`, `rc`, `kpm`, …) |
| `explore_e2_sm.sh` | Suites de exploración |

Logs: directorio **`logs/`** (`gnb_oai.log`, `ue_oai.log`, `nearRT-RIC.log`, `xapp_kpm_lab.log`, …).

---

## 10. Solución de problemas

### KPM timeout / crash del gNB

**Síntoma:**

```
cp_amf_region_id_to_bit_string: Assertion `src < 64' failed
```

**Causa:** `libkpm_sm.so` de `/usr/local` incompatible con AMF Region ID 128.

**Solución:**

```bash
./scripts/build_flexric_tools.sh
./scripts/down_flexric.sh && ./scripts/down_gnb_oai.sh
./scripts/test_e2_kpm.sh
```

### Crash de nearRT-RIC `E2 Node not found in the tree`

**Causa:** xApps “zombie” conectándose al RIC sin nodo E2 registrado, o gNB desalineado tras el restart del RIC.

**Solución:**

```bash
./scripts/down_flexric.sh
pkill -f xapp_ 2>/dev/null || true
./scripts/up_flexric.sh
./scripts/down_gnb_oai.sh && ./scripts/up_gnb_oai.sh
```

### RC sin INDICATIONs

- Suscribir **antes** del attach: `./scripts/test_e2_rc_attach.sh`
- RC es **aperiódico** (eventos RRC); el attach del UE dispara `RRCSetupComplete`

### KPM sin métricas (ceros)

- Confirmar PDU session en el slice 222/123
- Usar `KPM_TRAFFIC=1` y verificar ping al DN
- Aumentar `XAPP_DURATION=60`

### `xapp_oran_moni` (/usr/local)

No usar para KPM en este lab — filtro SST=1 por defecto. Usar `./scripts/test_e2_kpm.sh`.

---

## 11. Secuencia mínima de reproducción (lista de verificación)

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

## 12. Próximos pasos (opcional)

- Validar `xapp_kpm_rc` (monitor KPM + RC Control) con tráfico sostenido
- Aumentar la duración de las pruebas para series temporales de métricas KPM
- Integrar la recolección automática de logs en un pipeline de CI local

---

*Documento generado con base en las pruebas ejecutadas en jun/2026 en el host de desarrollo del proyecto `oai-cn-gnb-e2` (asignatura RIC / Cesar School).*
