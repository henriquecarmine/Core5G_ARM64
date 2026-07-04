<!-- sync: e36a3f4e -->
> 🌐 Traducción al **español** del documento canónico en portugués [`server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md`](../../../../../../server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md). Todos los idiomas: [INDEX](../../../INDEX.md) · sincronización verificada por `docs/i18n/check-parity.py`.

# Interfaz E2 y Service Models (FlexRIC)

Guía para operar la interfaz **E2** entre el gNB OAI y un **nearRT-RIC** (FlexRIC), y probar **Service Models** (SMs) O-RAN y personalizados.

## Arquitectura

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

## Service Models disponibles

| SM | Tipo | Encoding | xApp recomendado | Notas |
|----|------|----------|------------------|-------|
| **E2SM-KPM** v2.03 | O-RAN | ASN.1 | `xapp_oran_moni` | Métricas 3GPP (PRB, throughput, volumen PDCP…) |
| **E2SM-RC** v1.03 | O-RAN | ASN.1 | `xapp_oran_moni` | estado RRC, copia de mensajes, control QoS (PoC) |
| **MAC** | Custom | Plain | `xapp_gtp_mac_rlc_pdcp_moni` | KPIs L2 MAC por UE |
| **RLC** | Custom | Plain | `xapp_gtp_mac_rlc_pdcp_moni` | KPIs RLC por bearer |
| **PDCP** | Custom | Plain | `xapp_gtp_mac_rlc_pdcp_moni` | KPIs PDCP por bearer |
| **GTP** | Custom | Plain | `xapp_gtp_mac_rlc_pdcp_moni` | Estadísticas GTP-U NGU |

Versiones de compilación por defecto: **E2AP v2.03** + **E2SM-KPM v2.03** (deben coincidir entre gNB y FlexRIC).

## Versiones y codificación (lo que USA esta plataforma)

| Componente | Versión/valor | Dónde está definido |
|---|---|---|
| FlexRIC (integrado en OAI) | **2.0.0** | `openairinterface5g/openair2/E2AP/flexric/CMakeLists.txt` (`project(FlexRIC VERSION 2.0.0)`) |
| E2AP | v2.03 | flag de build (`-DE2AP_VERSION=E2AP_V2`) |
| Codificación de E2AP | **ASN.1** (`E2AP_ENCODING="ASN"`, el valor por defecto) | `flexric/CMakeLists.txt` línea ~205; nuestros scripts **no** lo sobrescriben |
| FlatBuffers/FlatCC | **no usado** | alternativa upstream (`-DE2AP_ENCODING=FLATBUFFERS`, requiere FlatCC instalado); fuera de nuestro build |

> Para el artículo: "E2AP con codificación ASN.1 (FlexRIC 2.0.0); FlatBuffers es
> soportado por FlexRIC upstream, pero no utilizado en esta plataforma."
> Los SMs personalizados (MAC/RLC/PDCP/GTP) usan encoding propio ("Plain",
> tabla de arriba) — eso es del Service Model, no del E2AP.

Documentación upstream: `openairinterface5g/openair2/E2AP/README.md`

## Requisitos previos

1. **FlexRIC** instalado en el host (Service Models en `/usr/local/lib/flexric/`):

   ```bash
   # Se ainda não tiver FlexRIC:
   git clone https://gitlab.eurecom.fr/mosaic5g/flexric.git
   cd flexric && git checkout dev
   mkdir build && cd build
   cmake .. -GNinja -DE2AP_VERSION=E2AP_V2 -DKPM_VERSION=KPM_V2_03
   ninja && sudo ninja install
   ```

2. **Submodule FlexRIC** en OAI (para compilar el E2 agent):

   ```bash
   # Automático via ./scripts/build_e2.sh
   ```

3. **Core OAI** operativo (`./scripts/up_core.sh`).

## Build del gNB con E2 Agent

```bash
cd ric/code/oai-cn-gnb-e2
./scripts/build_e2.sh
```

Esto compila `nr-softmodem` y `nr-uesoftmodem` con `-DE2_AGENT=ON`. Log en `logs/build_e2.log` (~15–30 min la primera vez).

## Configuración E2 en el gNB

En `openairinterface5g/scripts/gnb.conf`:

```bash
e2_agent = {
  near_ric_ip_addr = "127.0.0.1";
  sm_dir = "/usr/local/lib/flexric/";
};
```

- `near_ric_ip_addr`: IP del nearRT-RIC (localhost si FlexRIC corre en el mismo host).
- `sm_dir`: directorio con `libkpm_sm.so`, `librc_sm.so`, `libmac_sm.so`, etc.

Puerto E2AP FlexRIC: **36421** (O-RAN SC usa 36422 — requiere recompilación con `e2ap_server_port`).

## Flujo operativo

### Opción A — laboratorio completo (recomendado)

```bash
./scripts/up_e2_lab.sh          # Core + RIC + gNB + UE
./scripts/test_e2_sm.sh cust    # testar MAC/RLC/PDCP/GTP
./scripts/down_e2_lab.sh
```

### Opción B — paso a paso

```bash
./scripts/up_core.sh
./scripts/up_flexric.sh
./scripts/up_gnb_oai.sh
./scripts/test_e2_sm.sh cust
```

## Probar Service Models

```bash
# Custom SMs (funciona com slice 222/123 do laboratório)
XAPP_DURATION=30 ./scripts/test_e2_sm.sh cust

# O-RAN KPM + RC
./scripts/test_e2_sm.sh oran

# Todos os SMs
./scripts/test_e2_sm.sh all
```

### Verificar E2 setup

```bash
grep -iE 'E2|RIC|setup|indication' logs/gnb_oai.log
grep -iE 'E2|setup|indication' logs/nearRT-RIC.log
```

Indicios de éxito:
- gNB: mensajes `E2 Setup` / conexión SCTP al RIC
- xApp: `RIC INDICATION` con métricas periódicas

### KPM y slice S-NSSAI

Por defecto en upstream, el xApp KPM se suscribe a **SST=1**. Este laboratorio usa **SST=222, SD=123**.

Los xApps `xapp_kpm_moni` y `xapp_kpm_rc` (submodule FlexRIC `dev`) fueron ajustados para el slice del lab:

```bash
# Padrão: SST=222 SD=123 (Core/AMF/gNB/UE)
./scripts/test_e2_kpm.sh

# Override
KPM_SST=222 KPM_SD=123 XAPP_DURATION=45 ./scripts/test_e2_kpm.sh

# Só SST (SD wildcard no agente)
KPM_SD=any ./scripts/test_e2_kpm.sh
```

Métricas O-RAN soportadas (3GPP TS 28.552): `DRB.PdcpSduVolumeDL/UL`, `DRB.UEThpDl/Ul`, `RRU.PrbTotDl/Ul`, etc.

Genere tráfico durante la prueba (`KPM_TRAFFIC=1` por defecto) para métricas de throughput/volumen distintas de cero.

**SMs:** el gNB y el nearRT-RIC deben usar las libs del submodule (`flexric-lib/`), no `/usr/local/lib/flexric/` — la versión instalada en el sistema falla con AMF Region ID 128 del Core OAI. `./scripts/build_flexric_tools.sh` compila y sincroniza automáticamente.

**Nota:** `xapp_oran_moni` (instalado en `/usr/local`) todavía usa SST=1 — usa `./scripts/test_e2_kpm.sh` para KPM en este lab.

## Scripts

| Script | Descripción |
|--------|-----------|
| `build_e2.sh` | Compila gNB/nrUE con E2 agent |
| `up_flexric.sh` | Inicia el nearRT-RIC |
| `down_flexric.sh` | Detiene el RIC y los xApps |
| `up_e2_lab.sh` | Core + RIC + gNB + UE |
| `down_e2_lab.sh` | Detiene gNB y RIC (`--all` incluye el Core) |
| `test_e2_kpm.sh` | KPM con slice lab (222/123) + tráfico |
| `explore_e2_sm.sh` | Suite de exploración (rc, oran, layers, full) |
| `test_e2_rc_attach.sh` | RC con attach sincronizado (captura INDICATIONs) |
| `build_flexric_tools.sh` | Compila nearRT-RIC + xApps dedicados (dev) |

## Troubleshooting

| Problema | Causa probable | Solución |
|----------|----------------|---------|
| El build falla con "submodules not downloaded" | FlexRIC vacío | `./scripts/build_e2.sh` (clona automáticamente) |
| gNB no conecta al RIC | RIC detenido o IP incorrecta | `./scripts/up_flexric.sh`; verificar `near_ric_ip_addr` |
| xApp sin INDICATION (cust) | UE sin PDU session | Esperar el registro; verificar logs AMF/SMF |
| xApp sin INDICATION (KPM) | Filtro de slice SST=1 | Usar `test_e2_sm.sh cust` o alinear el slice |
| `libkpm_sm.so` not found | FlexRIC no instalado | `./scripts/build_flexric_tools.sh` |
| KPM crash / timeout | SMs de `/usr/local` desalineados (AMF Region ID 128) | Usar `flexric-lib/` vía `./scripts/sync_flexric_lib.sh` |
| xApp crash `e2ap_dec_e42_setup_response` | xApp de `/usr/local` o `/opt/flexric` | `./scripts/test_e2_sm.sh` usa solo xApps del submodule dev |

## Referencias

- [OAI E2AP README](../../../../../../server/oai-cn-gnb-e2/openairinterface5g/openair2/E2AP/README.md)
- [FlexRIC](https://gitlab.eurecom.fr/mosaic5g/flexric)
- [O-RAN E2SM-KPM](https://orandownloadsweb.azurewebsites.net/specifications)
- Docker Compose upstream (sin Core): `openairinterface5g/ci-scripts/yaml_files/5g_rfsimulator_flexric/`
