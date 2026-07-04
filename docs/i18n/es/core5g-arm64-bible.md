<!-- sync: e36a3f4e -->
> 🌐 Traducción al **español** del documento canónico en portugués [`core5g-arm64-bible.md`](../../../core5g-arm64-bible.md). Todos los idiomas: [INDEX](INDEX.md) · sincronización verificada por `docs/i18n/check-parity.py`.

# Core5G ARM64 — Biblia del Proyecto

Documento de referencia único y completo. Si usted (o alguien del grupo) llega
aquí sin ningún contexto, este archivo debe bastar para entender el qué, el
porqué y el cómo de todo lo que existe en este repositorio y en el servidor.

Para el historial cronológico paso a paso (el "diario de a bordo"), vea
[`CHANGELOG.md`](../../../CHANGELOG.md). Este documento es la fotografía
consolidada del estado actual + explicaciones conceptuales.

---

## 1. Contexto de la asignatura

- **Asignatura 7: RAN Intelligent Controller (RIC)** — especialización CESAR School.
- **Profesor:** Dr. Jonas Augusto Kunzler (`jak@cesar.school`).
- **Grupo (Grupo 6):** Henrique, Klinger, Kelvin, Gilberto.
- **Tema sorteado (NGO §6.1):** **UE-TP-rApp** — predicción de throughput por UE
  (RSSI, RSRP, CQI, PRB, histórico).

### Dos proyectos evaluativos (40% cada uno)

| Proyecto | Qué | Dónde está | Estado |
|---|---|---|---|
| **Proyecto 1** | Open5GS containerizado + UERANSIM (Core 5G + RAN simulada) | `server/` (raíz de este repo) | ✅ Presentado el 13/06/2026 (Clase 03). Validado de extremo a extremo en el servidor. |
| **Proyecto 2** | `oai-cn-gnb-e2` — OAI 5GC + gNB con agente E2 + FlexRIC (near-RT RIC) + xApps | `server/oai-cn-gnb-e2/` | ⏳ Pendiente. Presentación 20/06/2026 (Clase 06, 08:00–11:00, 20 min/grupo, mismo orden del Proyecto 1). |

Entregables del Proyecto 2 (según la diapositiva "Projeto 2 (40%) — roteiro e
prazos" del `pdfs/aula04-xapps_opensource.pdf`):
- Implementar `oai-cn-gnb` según `server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md`.
- Informe técnico + demo (video/logs).
- Extensión opcional: xApp personalizado o caso A1/políticas.
- **Atención:** la rúbrica oficial (`docs/avaliacao_seminario_aula06.md`) y el
  plan de pruebas (`docs/labs/04-projeto2-plano-testes.md`) citados en las
  diapositivas **no estaban publicados** en el repositorio de origen
  (`jakunzler/cesar-school-repo`) en el momento en que verificamos — confirmar
  con el profesor antes de la entrega.

---

## Créditos

Repositorio mantenido por **Henrique Carmine** —
[henriquecarmine@gmail.com](mailto:henriquecarmine@gmail.com) ·
[@henriquecarmine](https://github.com/henriquecarmine).

---

## 2. Cómo funciona todo esto, explicado para quien no es técnico

Piense en la red 5G como una **empresa de mensajería** (como el correo), solo que
en lugar de cartas entrega **internet** hasta su celular. Cada contenedor
Docker de abajo es un "departamento" de esa empresa, ejecutándose aislado de los
demás.

### El camino que recorre el celular (Proyecto 1 — Open5GS)

| Quién | Contenedor Docker | Qué hace, en una frase |
|---|---|---|
| 📡 Antena | `nr-gnb` (UERANSIM) | La torre de celular (simulada) — es por donde el celular habla con la red. |
| 📱 Celular | `nr-ue` (UERANSIM) | El celular (simulado) que llama, se registra y pide usar internet. |
| 🛎️ Portero/recepción | `amf` | Primer contacto: recibe el celular, verifica quién es y lo dirige al sector correcto. |
| 🔐 Seguridad | `ausf` | Verifica la "contraseña" del celular — solo deja pasar a quien es de verdad el dueño del chip. |
| 🗂️ Registro del cliente | `udm` | Guarda el perfil de cada cliente: qué plan tiene, a qué puede acceder. |
| 🗄️ Base de datos | `udr` + `mongodb` | El archivo/base donde los datos de registro quedan efectivamente guardados. |
| 🚦 Inspector de reglas | `pcf` | Decide las reglas de cada conexión: velocidad, prioridad, política de uso. |
| 📋 Tablero de avisos | `bsf` | Anota qué inspector (`pcf`) está a cargo de qué conexión, para que otros sectores lo encuentren después. |
| 🧭 Clasificación de carril | `nssf` | Elige en cuál "carril"/fila (*slice*) debe circular ese celular. |
| 🗺️ Gerente de logística | `smf` | Organiza la "ruta de entrega": arma la sesión de datos que el celular va a usar. |
| 🚚 Camión de reparto | `upf-a` / `upf-b` | Transporta efectivamente los datos (la internet) de un lado a otro. Dos camiones, uno de reserva. |
| 🌐 Destino final (prueba) | `dn` | Un "mundo exterior" falso solo para simular la internet real durante las pruebas. |
| ☎️ Directorio telefónico interno | `nrf` | Todo departamento se registra aquí — así es como un sector encuentra el teléfono del otro. |
| 📞 Telefonista interna | `scp` | Transfiere las llamadas entre los departamentos (en lugar de que cada uno llame directo al otro). |
| 🖥️ Mostrador de atención | `webui` | Pantalla web donde registramos un nuevo "cliente" (suscriptor) en el sistema. |

**Orden real de cuando un celular llama y pide internet:**
1. El celular (`nr-ue`) avista la antena (`nr-gnb`) y manda una señal.
2. `amf` recibe, verifica quién es con la ayuda de `ausf` (contraseña) y `udm` (registro).
3. `pcf` decide las reglas de esa conexión y avisa al tablero (`bsf`).
4. `nssf` elige el carril correcto, `smf` arma la ruta de datos.
5. `upf-a`/`upf-b` (el camión) empieza a transportar datos de verdad entre el
   celular y el "mundo exterior" (`dn`, o la internet real cuando corresponde).

Todo esto es **3GPP estándar** — Open5GS (Proyecto 1) y OAI (Proyecto 2) son dos
"marcas" diferentes de empresa de mensajería, pero con los mismos departamentos.

### El panel de control (no forma parte de la red 5G, es solo para que la operemos)

| Contenedor/proceso | Función, en una frase |
|---|---|
| 🚪 Portero del panel | `caddy` — verifica usuario y contraseña en la entrada del sitio y solo deja pasar a quien tiene credencial (login), además de cifrar la conexión (HTTPS). |
| 🖱️ Oficina de los botones | `server/panel/server.py` (FastAPI/Uvicorn) — es quien de hecho aprieta el botón de encender/apagar la red cuando usted hace clic en la pantalla. |

> Resumen: el panel es solo un control remoto para encender/apagar/verificar la
> "empresa de mensajería" de arriba — no forma parte de la red 5G en sí.

---

## 2.a Para el técnico de telecom (quien ya trabajó con radio)

Usted conoce antena, cobertura, frecuencia, quizás ya configuró BTS o eNodeB
en campo. Esta sección habla su idioma — sin analogía de empresa de mensajería,
sin código, sin protocolo a nivel de bytes.

### Lo que está ejecutándose aquí, en términos de radio

Este proyecto simula una célula 5G completa dentro de un servidor ARM en la nube.
No hay antena física, no hay RF de verdad — pero **toda la lógica de
señalización, autenticación y transporte de datos es real**, ejecutando los
mismos protocolos que usa una red operadora.

**Parámetros de radio del Proyecto 1 (UERANSIM):**

| Parámetro | Valor |
|---|---|
| Banda | n78 (3,3–3,8 GHz) — banda principal del 5G SA en Brasil |
| Modo | TDD (Time Division Duplex) — DL y UL en la misma frecuencia, separados por tiempo |
| Ancho de banda | 100 MHz |
| Numerología (SCS) | 30 kHz (µ=1) |
| PRBs activos | 66 (de 132 totales para 100 MHz / 30 kHz) |
| RSRP típico simulado | −79 dBm @ 100 m · −100 dBm @ 500 m · −111 dBm @ 1 km |
| Modelo de propagación | 3GPP TR 38.901 UMa NLOS |
| Pico teórico DL | ~665 Mbps (64-QAM, 4 capas MIMO) |
| Pico teórico UL | ~250 Mbps |

> UERANSIM simula la radio por software: la interfaz `uesimtun0` es el
> equivalente lógico del túnel entre la antena y el UE. No hay muestra IQ,
> no hay FPGA — pero NAS, RRC, PDCP y GTP-U se ejecutan todos de verdad.

### Los contenedores — qué es cada uno, en términos que usted conoce

Si trabajó con 4G/LTE, va a reconocer la mayoría. El 5G SA renombró y
reorganizó las piezas, pero la función es la misma.

| Contenedor | Equivalente 4G / LTE | Qué hace |
|---|---|---|
| `nr-gnb` (UERANSIM) | eNodeB (eNB) | La estación-radio-base (simulada). Maneja RRC, scheduler de PRB, GTP-U con el core. |
| `nr-ue` (UERANSIM) | UE / celular | El equipo (simulado). Hace attach, PDU session, "mide" RSRP/RSRQ, ejecuta iperf3. |
| `amf` | MME | Control de acceso, autenticación, registro y movilidad del UE. |
| `smf` | SGW-C + PGW-C | Controla el plano de datos: define la ruta del paquete, instruye al UPF vía PFCP. |
| `upf-a` / `upf-b` | SGW-U + PGW-U | Plano de usuario. Recibe GTP-U del gNB (N3) y lo reenvía a internet (N6). |
| `ausf` | HSS (parte auth) | Ejecuta el 5G-AKA — genera el vector de autenticación a partir del Ki y del OPc del SIM. |
| `udm` | HSS (parte datos) | Perfil del suscriptor: IMSI, plan, slice (S-NSSAI), MSISDN. |
| `udr` + `mongodb` | HSS (storage) | Base de datos del suscriptor. El UDM lee aquí. |
| `pcf` | PCRF | Política de QoS: define QFI, 5QI, reglas de throttling por sesión. |
| `bsf` | (nuevo en 5G SA) | Registra qué PCF está gestionando qué sesión — evita conflicto cuando el AMF necesita localizar el PCF de un UE activo. |
| `nssf` | (nuevo en 5G SA) | Network Slice Selection — decide en cuál porción de red (URLLC, eMBB, mMTC) entra el UE. |
| `nrf` | (nuevo en 5G SA) | Registro de NFs: cada función se registra aquí; otras consultan para saber la dirección de a quién necesitan llamar. |
| `scp` | (nuevo en 5G SA) | Proxy de señalización SBI — centraliza las llamadas HTTP/2 entre NFs. |
| `dn` | PDN-GW / internet | Red de datos de destino. Aquí corre el servidor iperf3 que mide throughput real por el túnel del UE. |

### Cómo funciona la simulación de canal (tc netem)

El panel tiene un modo "Condiciones del Canal" donde usted elige distancia e
interferencia. No hay radio real — el panel inyecta parámetros de
**Network Emulator (netem)** en la interfaz `uesimtun0` vía `tc qdisc`:

```
tc qdisc replace dev uesimtun0 root netem delay <D>ms loss <L>%
```

Los valores se derivan del modelo 3GPP TR 38.901 UMa NLOS (path loss) y del
SINR para cada nivel de interferencia:

| Condición | RSRP aprox. | Delay total | Pérdida total | Equivalente de campo |
|---|---|---|---|---|
| 100 m, sin interferencia | −79 dBm | 1 ms | 0% | UE cerca de la torre, buena visibilidad |
| 500 m, interferencia leve | −100 dBm | 13 ms | ~3% | Buena cobertura, co-canal leve (SINR ≈ 20 dB) |
| 1 km, interferencia media | −111 dBm | 40 ms | ~12% | Borde de célula (SINR ≈ 15 dB) |
| 3 km, interferencia alta | −127 dBm | 100 ms | ~32% | UE en la sombra, handover inminente (SINR ≈ 10 dB) |

### Diferencias entre Proyecto 1 (UERANSIM) y Proyecto 2 (OAI + FlexRIC)

| Aspecto | Proyecto 1 — UERANSIM | Proyecto 2 — OAI nr-softmodem |
|---|---|---|
| Capa de radio | Simulada (NAS/RRC/GTP-U vía socket, sin PHY real) | RFSIM: PHY real por software, sin hardware RF |
| Scheduler de PRBs | Implementado en UERANSIM (fijo) | Scheduler real del OAI (round-robin / proportional fair) |
| Interfaz con RIC | Ninguna — gNB monolítico, sin agente E2 | Agente E2 real; se conecta al FlexRIC y exporta KPIs por UE |
| Métricas de radio accesibles | Solo logs internos | DRB.UEThpDl/Ul, RRU.PrbTotDl/Ul, SINR vía E2SM-KPM |
| Analogía de campo | Drive test: usted tiene solo logs de NAS | OMC de la BTS: KPIs por UE en tiempo real, controlable vía xApp |

> El Proyecto 1 es suficiente para validar core + attach. El Proyecto 2 es lo que
> un integrador de RIC necesitaría para comisionar xApps de optimización de PRB,
> handover o QoS por UE.

---

## 2.b Para el ingeniero de redes (visión O-RAN / 3GPP)

Si usted conoce telecomunicaciones pero no el entorno Docker/Linux de este proyecto,
esta sección mapea cada pieza a su papel en la arquitectura O-RAN y en el 3GPP 5G SA.

### Qué es O-RAN y dónde encaja este proyecto

O-RAN (Open Radio Access Network) define una arquitectura desagregada de la RAN con
interfaces abiertas. La división funcional adoptada por la O-RAN Alliance es el
**Split 7.2x** (entre PHY-Low y PHY-High), que separa el nodo de acceso en:

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

**Interfaces estandarizadas relevantes:**

| Interfaz | Entre | Protocolo |
|---|---|---|
| E2 | Near-RT RIC ↔ O-gNB | E2AP sobre SCTP; E2SM-KPM/RC |
| A1 | Non-RT RIC ↔ Near-RT RIC | REST/JSON; políticas de ML/QoS |
| O1 | SMO ↔ todos los nodos gestionados | NETCONF/YANG |
| F1-C/U | O-CU ↔ O-DU | NG-AP + GTP-U (3GPP TS 38.473) |
| Open FH | O-DU ↔ O-RU | eCPRI sobre Ethernet (Split 7.2x) |
| N2 | O-CU-CP ↔ AMF | NGAP sobre SCTP |
| N3 | O-CU-UP ↔ UPF | GTP-U sobre UDP |
| N4 | SMF ↔ UPF | PFCP sobre UDP |

### Cómo encaja el Proyecto 1 (Open5GS + UERANSIM)

UERANSIM implementa un **gNB monolítico** (sin Split 7.2 — CU, DU y RU son un
proceso único) y un **UE** que habla NAS sobre el stack simulado. Es la referencia
más simple del 3GPP 5G SA sin Near-RT RIC.

```
UERANSIM nr-gnb  ──N2 (NGAP)──►  AMF   ─ CP 5GC
                 ──N3 (GTP-U)──►  UPF-A ─ UP 5GC (N6 → dn → internet)
UERANSIM nr-ue   ──NAS / RRC──►  (interno ao nr-gnb)
                                   └─► uesimtun0 (TUN 10.60.0.x)
```

No hay agente E2 ni Near-RT RIC en el Proyecto 1. Las pruebas de throughput y
canal simulado vía `tc netem` en `uesimtun0` son el equivalente práctico de lo
que se mediría vía E2SM-KPM `DRB.UEThpDl/Ul` en un entorno con RIC real.

### Cómo el Proyecto 2 (OAI + FlexRIC) agrega el Near-RT RIC

OAI `nr-softmodem` en modo RFSIM implementa el stack de RAN completo (PHY/MAC/
RLC/PDCP/RRC) **con agente E2 embebido** (biblioteca `openair2/E2AP/`). El
Split 7.2 se soporta vía F1/eCPRI, pero en el entorno de este proyecto corre en
modo monolítico con RFSIM (radio 100% por software, sin hardware SDR).

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

**KPMs relevantes para el tema UE-TP-rApp (E2SM-KPM):**

| KPM | Descripción | Granularidad |
|---|---|---|
| `DRB.UEThpDl` | Throughput DL por DRB por UE (kbps) | por UE |
| `DRB.UEThpUl` | Throughput UL por DRB por UE (kbps) | por UE |
| `RRU.PrbTotDl` | PRBs utilizados en el DL (%) | por célula |
| `RRU.PrbTotUl` | PRBs utilizados en el UL (%) | por célula |
| `L1M.RS-SINR` | SINR medido en la capa física | por UE |

### Dónde está cada contenedor Docker en el modelo O-RAN

| Contenedor | Capa O-RAN | Interfaz expuesta |
|---|---|---|
| `nr-gnb` / `nr-ue` (UERANSIM) | O-gNB monolítico (sin E2) + UE | N2, N3, NAS |
| OAI `nr-softmodem` (Proy.2) | O-gNB con agente E2 | N2, N3, E2 |
| `flexric` (Proy.2) | Near-RT RIC | E2, A1 |
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
| `scp` | 5GC CP — SBI proxy | SBI indirecto |
| `mongodb` | Storage backend | — (Nudr internal) |

### Flujo NAS/RRC de registro (desde el punto de vista del protocolo)

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

## 3. Estructura del repositorio

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

### Por qué esta separación

- **Raíz** = herramientas de orquestación local (nunca corren en el servidor).
- **`server/`** = espejo exacto de lo que existe y corre en la instancia AWS.
- **`docs/`** = documentación pura, sin ningún archivo ejecutable/config.
- El `.env` fue deliberadamente **dividido en dos**: el de la raíz tiene
  `AWS_SERVER_HOST`/`AWS_SERVER_USER`/`AWS_SSH_KEY_PATH`/`DUCKDNS_DOMAIN`/`DUCKDNS_TOKEN`
  (solo para que `deploy.sh` lo use localmente); el de `server/.env` tiene solo
  `OPEN5GS_IMAGE`/`WEBUI_IMAGE`/`MONGODB_IMAGE`/`UERANSIM_IMAGE`/`DN_IMAGE`
  (lo que `docker-compose.yml` necesita *en el servidor*). Así ningún secreto
  de acceso se envía al servidor vía `rsync`.

---

## 4. El servidor (AWS EC2 ARM)

| Ítem | Valor |
|---|---|
| Hostname | `core5g-arm64.duckdns.org` (DDNS — la IP pública es dinámica) |
| IP original (histórico) | `3.145.40.200` — **nunca hardcodear**, usar siempre el hostname |
| Usuario | `ubuntu` |
| Clave SSH | `ssl/core5g_openran_arm64.pem` (Ed25519) |
| Tipo de instancia | **AWS EC2 `t4g.medium`** (Graviton2 / Neoverse-N1, `aarch64`) — 2 vCPU / 4 GB. (Era `t4g.micro` al inicio del proyecto; upgrade confirmado por `free` en 2026-06-22.) |
| Región AWS | `us-east-2` |
| SO | Ubuntu 24.04.4 LTS (`noble`), kernel `6.17.0-1017-aws`, `aarch64` |
| CPU | 2 vCPUs — `Neoverse-N1` (ARM Graviton2) |
| RAM | ~3,8 GiB (3825 MiB medidos — `t4g.medium`) |
| Swap | 8 GiB en `/swapfile`, `vm.swappiness=10`, persistente vía `/etc/fstab` |
| Disco | ~29 GB total |
| Docker | `29.6.0` (paquetes `docker-ce`/`docker-ce-cli`/`containerd.io` arquitectura `arm64`, repositorio oficial Docker) |
| Docker Compose | `v5.1.4` (plugin) |

### Costos e higiene de disco

Reglas, valores y el runbook de upgrade de CPU (el lab de RIC con IA necesita
4 vCPU) viven en [`docs/POLITICA-DE-CUSTOS.md`](../../POLITICA-DE-CUSTOS.md).
Lecciones permanentes de la limpieza del 2026-07-03 (el disco llegó a 8% libre; volvió
a 8,6 GB libres):

- El mysql del core P2 creaba **un volumen anónimo de ~197 MB por reencendido**
  (encontramos 16 huérfanos = 3,1 GB). Corregido de raíz: volumen nombrado
  `mysql-data` en `oai-cn5g-v2/docker-compose-basic-nrf.yaml` — de paso los
  registros de UE pasaron a persistir entre reencendidos.
- `docker volume prune -f` elimina **solo anónimos** (Docker ≥23) — los nombrados
  (MongoDB de los alumnos) quedan. Aun así: inspeccionar antes de podar.
- Las imágenes OAI **custom** (arm64 compiladas, `oai-upf-vpp` portado) no son
  re-descargables — **nunca** eliminar sin backup/evaluación. Las oficiales v1.5.1 +
  `mysql:8.0` (legado, ~2,6 GB) fueron eliminadas con evaluación el 2026-07-03.

### Acceso manual (solo para debug — preferir `./deploy.sh ssh`)

```bash
ssh -i ssl/core5g_openran_arm64.pem ubuntu@core5g-arm64.duckdns.org
```

### DuckDNS (IP dinámica)

- Dominio: `core5g-arm64.duckdns.org`.
- Token: almacenado en `.env` (`DUCKDNS_TOKEN`) — no duplicado aquí.
- Script `~/duckdns/duck.sh` en el servidor + cron `*/5 * * * *` manteniendo el
  registro actualizado. Reinstalable/idempotente vía
  `./deploy.sh bootstrap`.

### Docker

Instalado vía **repositorio oficial Docker** (no el paquete `docker.io` de
Ubuntu): `docker-ce`, `docker-ce-cli`, `containerd.io`,
`docker-buildx-plugin`, `docker-compose-plugin`. Usuario `ubuntu` en el grupo
`docker`. Todo encapsulado en `infra/server-bootstrap.sh`, idempotente.

---

## 5. El flujo de trabajo: todo local, deploy vía `deploy.sh`

**Regla de oro:** nunca editar nada directamente en el servidor vía SSH manual. El
flujo es siempre: editar archivos en `server/` (o `infra/`) localmente →
`./deploy.sh <comando>`.

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

`deploy.sh` lee `AWS_SERVER_HOST`/`AWS_SERVER_USER`/`AWS_SSH_KEY_PATH` del
`.env` de la raíz — por eso nunca tiene IP/hostname hardcodeado dentro del script.

### Panel visual (`client/`)

Para quien prefiere hacer clic en un botón en vez del terminal: un panel web que corre
**en su estación local** (no en el servidor) con un botón por comando de
`deploy.sh` y consola con salida en tiempo real.

```bash
cd client && ./run.sh        # cria venv, instala deps, sobe em http://127.0.0.1:8765
```

- El backend (`client/server.py`, FastAPI) solo hace `subprocess.Popen` de
  `deploy.sh` y transmite stdout/stderr al navegador — ninguna lógica de
  SSH/rsync duplicada, `deploy.sh` sigue siendo la única fuente de verdad.
- Los comandos expuestos son una lista fija (`bootstrap`, `sync`, `sync-oai`,
  `up`/`down core|ran|all`, `status`) — el backend no acepta string libre
  proveniente del navegador.
- Bind solo en `127.0.0.1`, sin autenticación — asume uso local de
  desarrollo, no exposición en red.
- Es el primer peldaño del panel mayor descrito en
  `docs/blueprint-painel-observabilidade.md` (que prevé logs filtrables y
  visualización de flujo de protocolo en tiempo real) — esta versión aún solo
  dispara comandos y muestra la salida cruda, sin parsing/filtros.

### Panel web en el servidor (`server/panel/`), con HTTPS + login

Versión del panel accesible desde cualquier lugar (no solo desde su estación),
publicada en `https://core5g-arm64.duckdns.org/` con usuario/contraseña.

- Corre **directamente en la instancia AWS** — `server/panel/server.py` (FastAPI)
  llama a los scripts locales (`./scripts/up.sh`, `up_ran.sh`, `down_core.sh`,
  `down_ran.sh`, `healthcheck.sh`) sin ningún SSH involucrado. Bind solo en
  `127.0.0.1:8765` — nunca expuesto directamente en internet.
- **HTTPS automático vía Caddy**: `infra/server-bootstrap.sh` instala
  Caddy (repositorio oficial Cloudsmith) y genera `/etc/caddy/Caddyfile` al
  frente del panel. Caddy obtiene/renueva por sí solo un certificado **Let's
  Encrypt gratuito** para `core5g-arm64.duckdns.org` — no hay certificado
  manual para instalar. Único requisito externo: los puertos **80** (desafío
  ACME HTTP-01) y **443** (HTTPS) necesitan estar abiertos en el Security Group
  de la instancia — **ya abierto y validado** (HTTP 308 → HTTPS, HTTPS 401 sin
  credencial, 200 con login, 403 para el guest en `/api/run/*`).
- **Login con dos roles**, vía `basic_auth` del propio Caddy (hash bcrypt
  generado con `caddy hash-password`, nunca contraseña en texto plano en el servidor):
  - **admin** (`PANEL_USER`/`PANEL_PASSWORD` en el `.env` de la raíz): acceso
    total, ejecuta cualquier comando.
  - **guest** (`PANEL_GUEST_USER`/`PANEL_GUEST_PASSWORD`): solo visualiza —
    `server.py` rechaza con HTTP 403 cualquier `POST /api/run/*` proveniente de ese
    usuario (verificación en el backend, no solo botón oculto en el front-end). El
    Caddy inyecta `header_up X-Remote-User {http.auth.user.id}` para que FastAPI
    sepa quién autenticó.
- **Proceso persistente**: `infra/core5g-panel.service` (systemd,
  `Restart=always`, corre el `uvicorn` del venv en `server/panel/.venv`).
  Instalado/actualizado por el bootstrap.
- **Deploy**: `./deploy.sh panel` sincroniza `server/panel/` y corre el
  bootstrap (idempotente) — único camino para actualizar el panel o las
  credenciales (nunca editar nada vía SSH manual en el servidor, misma regla
  de oro del §5).
- **Telemetría en tiempo real** (`GET /api/telemetry`): stream infinito
  (NDJSON, una línea de JSON cada 2s) con RAM/swap/disco/load del host
  (leídos de `/proc/meminfo` + `shutil.disk_usage` + `os.getloadavg()`,
  sin dependencia nueva) y CPU%/RAM por contenedor (`docker stats
  --no-stream --format '{{json .}}'`). Renderizado en la UI como barritas +
  tabla colapsable, sin Prometheus/Grafana — la instancia tiene solo 906 MiB
  de RAM, no cabe un stack de observabilidad pesado de su lado.
- **Filtro de logs por servicio** (`GET /api/logs/{service}`): lista de
  servicios descubierta en runtime vía `docker compose config --services`
  (en los dos compose files — core y `ueransim/`), luego `docker compose
  logs -f --tail 200 <service>` transmitido a la consola de la UI.
- **Telemetría y logs están liberados para el guest** (son lectura, no
  ejecución) — solo `POST /api/run/*` devuelve 403 para ese usuario.

---

## 6. Open5GS (Proyecto 1) — qué hace cada servicio

Todos los NFs (Network Functions) de abajo son papeles estandarizados por el 3GPP.
Open5GS y OAI implementan los mismos papeles, solo con binarios diferentes.

| Servicio | Interfaz principal | Papel |
|---|---|---|
| `nrf` | SBI interno | "DNS" del core — todo NF se registra aquí para que los otros lo encuentren |
| `scp` | SBI interno | proxy interno entre NFs (Service Communication Proxy) |
| `amf` | N1 (NAS) / N2 (NGAP) | puerta de entrada de la RAN — autentica y mueve al UE |
| `smf` | N4 (PFCP) / N11 | gestiona sesiones PDU (los "túneles" de datos) |
| `upf-a` / `upf-b` | N3 (GTP-U) / N6 | plano de datos de hecho — failover/load balancing entre las dos |
| `ausf` | SBI interno | ejecuta la autenticación 5G-AKA |
| `udm` | SBI interno | perfil del suscriptor (slice, claves de seguridad) |
| `udr` | SBI interno | base de datos detrás del UDM/PCF (backend MongoDB) |
| `pcf` | SBI interno (Npcf) | decide reglas de QoS/política de sesión |
| `bsf` | SBI interno (Nbsf) | registra el *binding* PCF↔sesión para descubrimiento por otros NFs (ej.: NEF/AF). **Ítem que faltaba en el proyecto original — ver §8.** |
| `nssf` | SBI interno | elige el slice (S-NSSAI) correcto para el UE |
| `webui` | HTTP :9999 | panel admin de Open5GS para registrar suscriptores |
| `mongodb` | — | base de datos (subscribers, etc.) |
| `dn` | N6 | "internet" falsa (alpine) solo para que el UPF tenga hacia dónde rutear/NAT |

**Detalle pedagógico importante:** cada red docker en el `docker-compose.yml`
(`net-n2`, `net-n3`, `net-n4`, `net-n6`, `net-sbi`) corresponde 1:1 a una
interfaz 3GPP real — filtrar por red = filtrar por interfaz.

### RAN simulada (UERANSIM, en `server/ueransim/`)

- `nr-gnb`: simula la estación base — habla N2/N3 con el core.
- `nr-ue`: simula el celular — registro NAS, abre sesión PDU, expone la
  interfaz `uesimtun0` para probar conectividad de extremo a extremo.

---

## 7. OAI + FlexRIC (Proyecto 2) — qué hace cada pieza

En `server/oai-cn-gnb-e2/`:

- **OAI 5GC** (`oai-cn5g-fed/`): mismos papeles de NF que Open5GS, pero
  empaquetados por OpenAirInterface, con UPF en **VPP** (dataplane más
  rápido) en vez del UPF simple.
- **gNB OAI** (`nr-softmodem`, modo **RFSIM** — radio 100% software): PHY/MAC/
  RLC/PDCP/RRC reales (no simulados como en UERANSIM), con un **agente E2
  embebido** que anuncia "RAN functions" (KPM = métricas, RC = control, +
  SMs custom L2/L3) para el near-RT RIC.
- **FlexRIC** (near-RT RIC): recibe el E2 SETUP del gNB, registra las RAN
  functions disponibles, rutea SUBSCRIPTION/INDICATION/CONTROL entre el gNB
  y las xApps.
- **xApps** (`xapp_kpm_moni`, `xapp_kpm_rc`): aplicaciones que de hecho
  consumen métricas (KPM) o eventos RRC (RC) vía E2 — el "lado inteligente"
  del RIC.

Flujo de arranque documentado en
`server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md`: Core → RIC → gNB → xApp.

### 7.a Proyecto 1 vs. Proyecto 2 — en qué exactamente difieren

Ambos implementan una red 5G de extremo a extremo, pero en puntos opuestos del
espectro "simple y validado" ↔ "complejo y fiel al O-RAN":

| Aspecto | Proyecto 1 (Open5GS + UERANSIM) | Proyecto 2 (OAI + FlexRIC) |
|---|---|---|
| Core 5G | Open5GS (imágenes listas, `gradiant/open5gs`) | OAI CN5G (`oai-cn5g-fed/`), UPF en VPP |
| RAN | UERANSIM — gNB/UE **simulados por software**, sin PHY/MAC reales | gNB OAI `nr-softmodem` en **RFSIM** — PHY/MAC/RLC/PDCP/RRC reales, radio 100% software (sin hardware de RF) |
| Capa de control externa (RIC) | **No existe** — red monolítica, sin separación dato/control | **FlexRIC** (near-RT RIC) conectado al gNB vía E2AP (puerto 36421) |
| Inteligencia/observabilidad | Scripts del panel (`tc netem`, `iperf3`) simulan canal/miden banda desde afuera | **xApps** (`xapp_kpm_moni`, `xapp_kpm_rc`) consumen métricas/controlan el gNB desde dentro de la arquitectura, vía Service Models E2 estandarizados (KPM v2.03, RC v1.03) + SMs custom (MAC/RLC/PDCP/GTP) |
| Concepto 3GPP/O-RAN ilustrado | Registro NAS, sesión PDU, QoS, failover de UPF — "la red 5G funciona" | Separación **CU/DU/RIC**, *RAN programable*: el RIC puede observar (KPM) y actuar (RC) sobre el gNB en tiempo casi-real — es el concepto central de Open RAN |
| Complejidad de build | Imágenes Docker listas, solo `docker compose up` | Build C/C++ nativo desde el source (`build_oai`, FlexRIC), pesado en CPU/RAM/disco — no hay imagen lista para ARM64 |
| Estado en 2026-06-18 | Completo, validado E2E (§9), ya presentado | Build desde cero en curso en el servidor (ver `CHANGELOG.md` v0.8.0) — nada estaba funcional antes de eso, a pesar de apariencias de progreso anterior |

En una frase: el **Proyecto 1** prueba que una red 5G básica funciona de punta
a punta; el **Proyecto 2** agrega la capa de **RAN inteligente y
programable** (RIC + xApps hablando E2 con el gNB) que es la propia
definición de O-RAN — y es técnicamente más pesado porque no hay imagen
Docker lista: todo se compila desde el source, nativo `aarch64`.

### 7.b Build de las imágenes OAI 5G Core para arm64

Las imágenes Docker del OAI 5G Core (`oaisoftwarealliance/oai-{amf,smf,nrf,udr,udm,ausf,upf-vpp}:v1.5.1`) en Docker Hub son **amd64-only** — no hay variante `linux/arm64/v8`. El servidor AWS t4g.micro (Graviton2, `aarch64`) no tiene QEMU/binfmt-misc configurado, así que cualquier intento de correr esas imágenes falla con `exec /usr/bin/python3: exec format error` y el contenedor sale con código 255.

#### Estrategia adoptada

Compilar nativamente para arm64 en el Mac Apple Silicon (Docker Desktop con engine `linux/arm64`), exportar como `.tar`, transferir vía `scp` y cargar en el servidor con `docker load`. Los Dockerfiles están vendorizados en el repositorio en `server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-*/docker/Dockerfile.*.ubuntu`.

Script: [`build-oai-arm64.sh`](../../../build-oai-arm64.sh) en la raíz del repositorio.

```bash
./build-oai-arm64.sh build    # compila as 6 imagens localmente no Mac
./build-oai-arm64.sh save     # exporta para /tmp/oai-images/*.tar
./build-oai-arm64.sh upload   # scp dos .tar para o servidor
./build-oai-arm64.sh load     # docker load no servidor + rm dos .tar
./build-oai-arm64.sh all      # executa os 4 passos em sequência
```

#### Prerrequisitos

| Requisito | Detalle |
|---|---|
| Máquina | Mac Apple Silicon (M1/M2/M3/M4) — arm64 nativo |
| Docker Desktop | ≥ 4.x con engine `linux/arm64` habilitada |
| Espacio en disco | ≥ 20 GB libres (imágenes intermedias + .tar exportados) |
| Tiempo | ~40 min por imagen × 6 = ~4 h en total |
| SSH key | `ssl/core5g_openran_arm64.pem` con acceso al servidor |
| `.env` | configurado con `AWS_SERVER_HOST`, `AWS_SERVER_USER`, `AWS_SSH_KEY_PATH` |

> **¿Por qué Mac Apple Silicon?** Docker Desktop en los M-series corre contenedores `linux/arm64` _nativamente_ — sin emulación QEMU. Compilar el OAI (C++ pesado) vía emulación llevaría 5–10× más tiempo y frecuentemente se traba por OOM.

#### Cómo compilar — paso a paso

**1. Clonar el repositorio y configurar el .env**

```bash
git clone https://github.com/henriquecarmine/Core5G_ARM64.git
cd Core5G_ARM64
cp .env.example .env
# editar .env: AWS_SERVER_HOST, AWS_SERVER_USER, AWS_SSH_KEY_PATH
```

**2. Compilar las 6 imágenes**

```bash
./build-oai-arm64.sh build
# Cada docker build compila o OAI a partir do source dentro do container arm64.
# A ordem importa: AMF → SMF → NRF → UDR → UDM → AUSF
# Cache Docker é reutilizado em recompilações parciais.
```

Lo que pasa por dentro de cada build (multi-stage Dockerfile):
1. **base stage** — `apt-get install` de las dependencias de sistema + build tools
2. **base stage** — compilación de spdlog, Pistache, nlohmann/json y nghttp2 desde git
3. **builder stage** — `cmake` configura el proyecto + `make -j$(nproc)` compila el binario
4. **target stage** — copia solo el binario y `.so` necesarios para la imagen final mínima

**3. Exportar a .tar**

```bash
./build-oai-arm64.sh save
# Cria /tmp/oai-images/oai-{amf,smf,nrf,udr,udm,ausf}.tar (~60 MB cada)
```

**4. Enviar al servidor**

```bash
./build-oai-arm64.sh upload
# scp de cada .tar para ~/ no servidor via SSH
```

**5. Cargar en el daemon Docker del servidor**

```bash
./build-oai-arm64.sh load
# docker load -i ~/oai-{comp}.tar && rm ~/oai-{comp}.tar  (para cada componente)
```

**O todo de una vez:**

```bash
./build-oai-arm64.sh all
```

**Verificar que las imágenes son realmente arm64:**

```bash
# no servidor:
docker run --rm oaisoftwarealliance/oai-amf:v1.5.1 uname -m
# esperado: aarch64
```

#### Parámetros del build

| Parámetro | Valor |
|---|---|
| `--platform` | `linux/arm64` |
| `--build-arg BASE_IMAGE` | `ubuntu:focal` (ver §8.5) |
| `--target` | nombre del componente (ej.: `oai-amf`) |
| `-f` | `component/<comp>/docker/Dockerfile.<shortname>.ubuntu` |
| contexto | directorio del componente (ej.: `component/oai-amf/`) |

#### Problemas encontrados — y cómo se corrigieron

Estos son los errores que aparecen al intentar compilar las imágenes OAI para arm64 **a partir del código original del repositorio**. Los patches ya están aplicados en este repo; esta sección existe para documentar el razonamiento y ayudar a quien intente hacer lo mismo en otra base de código.

**Bug 1 — `declare -A` no soportado en el bash 3.2 de macOS**

macOS 14/15 viene con bash 3.2 (limitación de licencia GPLv2). El script original usaba `declare -A COMPONENTS=(...)` (bash 4+), causando `oai: unbound variable` al ejecutarse.

Corrección: reemplazado por un string simple iterado con `for comp in $COMPONENTS`:
```bash
COMPONENTS="oai-amf oai-smf oai-nrf oai-udr oai-udm oai-ausf"
# oai-upf-vpp excluído: requer libhyperscan (Intel-only, inexistente no arm64)
for comp in $COMPONENTS; do ...
```

**Bug 2 — Nombre erróneo del Dockerfile**

El Dockerfile se llama `Dockerfile.amf.ubuntu` (sin el prefijo `oai-`), no `Dockerfile.oai-amf.ubuntu`. El script generaba el nombre erróneo, causando "Dockerfile no encontrado" para los 7 componentes.

Corrección: agregado `shortname="${comp#oai-}"` para eliminar el prefijo antes de armar la ruta:
```bash
shortname="${comp#oai-}"   # oai-amf → amf
dockerfile="$ctx/docker/Dockerfile.${shortname}.ubuntu"
```

**Bug 3 — `libboost1.67-dev` no disponible en el repositorio arm64 de Ubuntu 18.04**

El `build_helper.amf` (y equivalentes de cada componente) para `ubuntu18.04` agrega el PPA `ppa:mhier/libboost-latest` e instala `libboost1.67-dev`. Ese PPA no publica paquetes arm64 — el `apt-get install` falla con `E: Unable to locate package libboost1.67-dev`, y el build aborta con "AMF deps installation failed".

Corrección: pasar `--build-arg BASE_IMAGE=ubuntu:focal`. Ubuntu 20.04 tiene Boost 1.71 en los repositorios estándar; el `build_helper` tiene un case específico `ubuntu20.04` que instala `libboost-all-dev` directamente, sin PPA. El Dockerfile soporta bionic, focal y jammy explícitamente — usar focal es el camino soportado.

**Bug 4 — `-msse4.2` hardcoded en el CMakeLists.txt de todos los componentes**

Tras resolver el Bug 3, la compilación falla con `cc: error: unrecognized command line option '-msse4.2'`. El bloque de detección de arquitectura en cada `src/*/CMakeLists.txt` tiene:

```cmake
if (CMAKE_SYSTEM_PROCESSOR STREQUAL "armv7l")
  set(C_FLAGS_PROCESSOR "-gdwarf-2 -mfloat-abi=hard -mfpu=neon -lgcc -lrt")
else (CMAKE_SYSTEM_PROCESSOR STREQUAL "armv7l")  # ← else genérico
  set(C_FLAGS_PROCESSOR "-msse4.2")              # ← flag x86 SSE4.2
endif()
```

En el build `linux/arm64`, `CMAKE_SYSTEM_PROCESSOR` es `aarch64` — cae en el `else` e intenta compilar con `-msse4.2` (instrucción x86 SIMD que no existe en ARM).

Corrección aplicada en los 5 componentes afectados (`oai-amf`, `oai-smf`, `oai-nrf`, `oai-udr`, `oai-udm`, `oai-ausf`):

```cmake
if (CMAKE_SYSTEM_PROCESSOR STREQUAL "armv7l")
  set(C_FLAGS_PROCESSOR "-gdwarf-2 -mfloat-abi=hard -mfpu=neon -lgcc -lrt")
elseif (CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|arm64")
  set(C_FLAGS_PROCESSOR "")   # ← ARM64 nativo, sem flags arquitetura-específicas
else()
  set(C_FLAGS_PROCESSOR "-msse4.2")
endif()
```

El `oai-upf-vpp` usa VPP con sistema de build propio y no tiene esa flag.

**Bug 5 — `libasan2` inválido en `build_helper.udm` silencia el `apt-get` entero**

El `build_helper.udm` tenía `libasan2` en el `PACKAGE_LIST` ubuntu (línea que no está presente en los otros componentes). El `libasan2` no existe en Ubuntu 20.04 arm64 (`libasan5` es la versión correcta, ya incluida en `specific_packages`). El `apt-get install -y` falla entero con `E: Unable to locate package libasan2` — pero el error queda silenciado porque el `ret=$?` subsecuente captura el código de salida del bloque `if/case` (que devuelve 0 para ubuntu20.04), no del `apt-get`. Resultado: ningún paquete del `PACKAGE_LIST` se instala, incluyendo `libconfig++-dev`. El cmake entonces falla con `None of the required 'libconfig++' found`.

Corrección: eliminar la línea `libasan2` (y el `libasan` genérico que tampoco existe) del `PACKAGE_LIST` ubuntu en `build_helper.udm`. El `libasan5` ya está en `specific_packages` para ubuntu20.04.

Archivo afectado: `server/.../oai-udm/build/scripts/build_helper.udm`

**`oai-upf-vpp` en arm64 — RESUELTO con Vectorscan (2026-06-21)**

Por mucho tiempo el `oai-upf-vpp` fue considerado "no portable" a arm64. El
diagnóstico real, al investigar la fuente: el bloqueo era **una única dependencia**
— el **Hyperscan** (`libhyperscan-dev`), biblioteca de regex SIMD de Intel
(SSE/AVX), inexistente en Ubuntu arm64. El plugin UPF de Travelping la exige vía
`pkg_check_modules(HS libhs)` (pkg-config puro).

La solución: el **[Vectorscan](https://github.com/VectorCamp/vectorscan)** es un fork
portable del Hyperscan — ARM NEON 100% funcional, **API/ABI-compatible**, mismo
SONAME `libhs.so.5`. Es **drop-in**: compilando el Vectorscan e instalándolo, el
`pkg_check_modules(HS libhs)` lo encuentra y el GTP UPF se habilita normalmente
(`Found libhs, version 5.4.12`). Los otros "bloqueos" citados antes no se
confirmaron — el VPP 2101 **core no usa hyperscan**, y las rutas de lib ya
estaban corregidas para `aarch64-linux-gnu` en el Dockerfile.

Pasos del porte (en [`docker/Dockerfile.upf-vpp.ubuntu.arm64`](../../../server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-upf-vpp/docker/Dockerfile.upf-vpp.ubuntu.arm64)):
1. Base `ubuntu:focal` (gcc-9; Vectorscan exige C++17/gcc≥9) + `cmake` reciente
   vía pip (focal tiene 3.16; Vectorscan pide ≥3.18.4).
2. Compilar el Vectorscan removiendo `-Werror` (gcc-9 da falso-positivo en
   `state_compress.c` + la flag `-Wno-stringop-overread` solo existe en gcc-11) y
   desactivando los extras (`BUILD_UNIT/TOOLS/EXAMPLES/BENCHMARKS/DOC=OFF`).
3. `sed` removiendo `dh-systemd` del `DEB_DEPENDS` del VPP (paquete bionic-only que
   rompe el `make install-dep` en focal; solo sirve para empaquetar `.deb`).
4. `sed` forzando `https://github.com` en las URLs de los paquetes externos del VPP
   (el `rdma-core` descargaba por `http://github.com:80` → "connection refused").
5. Copiar el `libhs.so.5` (Vectorscan) a la imagen final.

Resultado validado: `vpp` ELF **ARM aarch64**, `upf_plugin.so` resuelve
`libhs.so.5`. **Runtime validado** (docker `--privileged` + hugepages): el VPP
bootea completo y el plugin responde — `show plugins` lista `upf_plugin.so
21.01.1`, `show upf specification release` → `PFCP version: 15`. El abort que
aparecía en el `flowtable_init` **no era defecto del porte**: era el `main-heap`
respaldado por hugepages sin páginas suficientes; con `main-heap-page-size 4k`
(o hugepages dimensionadas) sube normal. **Detalle operativo para quien deploye:**
no respalde el main-heap con más hugepages de las que el host tiene libres — use 4k o
reserve hugepages suficientes (heap + buffers). Imagen en
`artifacts/oai-images/oai-upf-vpp.tar` (~138 MB).

**Validación en el Graviton real (servidor AWS, 2026-06-22).** Imagen cargada en el
servidor (`docker load`, arch=arm64) y ejecutada standalone con el box **ocioso**
(`--cpus=1.5`, heap 2G/4k). Prueba **event-driven** (readiness por estado: el socket
CLI existe O el proceso muere — sin sleep/timeout fijo) con **métricas reales**:

| Check | Valor medido en el Graviton |
|---|---|
| `docker stats` | cpu 2,23% · mem 1,41 GiB / 3,74 GiB (37,8%) · 1 pid |
| `show version` | `vpp v21.01.1` (ARM) |
| `show plugins` | `upf_plugin.so 21.01.1` |
| `show upf specification release` | `PFCP version: 15` |
| `show memory main-heap` | total 1,99G · **usado 1,08G** · libre 938M |
| `show buffers` | pool `default-numa-0` 17.240 buffers |
| `upf_plugin.so` | enlaza con `libhs.so.5` (vectorscan) |

El **uso real de heap (1,08 GB)** explica por qué 1G falla y 2G basta: el flowtable
del plugin pre-asigna ~1 GB (default de compilación, sin `init.conf` dimensionando).
El contenedor **se autoterminó** y fue eliminado; load del host 0,3 → 1,0 (trivial).

> **Lección aprendida (registrada para no repetir):** correr VPP en el box **mientras el
> lab P2 está activo** (load ~30 en los 2 vCPUs) con un harness que **no
> se autotermina** ahogó al `sshd` y exigió reboot. Regla: las pruebas de VPP en el servidor
> solo con el box **ocioso**, contenedor **`--rm` + autotérmino**, y espera por
> **estado/evento** (nunca timeout ciego). Ver [[feedback-event-driven-nao-tempo]].

Falta solo el **E2E completo** (sesión PFCP del SMF + GTP-U del gNB + tráfico de UE),
que exige el core+RAN entero y una ventana sin clase — y el lab no depende de esto.

> El lab principal sigue usando el UPF de Open5GS (`open5gs-upfd`, P1) y el
> `oai-upf` simple_switch (P2, core v2.2.1) — no depende de esta imagen. El porte
> existe por el principio Open RAN ("toda tecnología O-RAN debe ser abierta") y es
> candidato a report upstream para OAI.

#### Resultado — builds concluidos el 2026-06-19

Compilación realizada en el Mac Apple Silicon (M-series) vía Docker Desktop `linux/arm64`. Tiempo total: ~40 min por imagen (base stage + build from source + cmake + make). Imágenes cargadas en el servidor AWS t4g.micro (Graviton2, Ohio) y verificadas con `uname -m → aarch64`.

| Imagen                         | Tag    | Tamaño  | Build SHA (digest)                                        |
|-------------------------------|--------|---------|-----------------------------------------------------------|
| oaisoftwarealliance/oai-amf   | v1.5.1 | 280 MB  | `sha256:404e88009215...` |
| oaisoftwarealliance/oai-smf   | v1.5.1 | 260 MB  | `sha256:90d5058e53c6...` |
| oaisoftwarealliance/oai-nrf   | v1.5.1 | 264 MB  | `sha256:49528805e9ae...` |
| oaisoftwarealliance/oai-udr   | v1.5.1 | 268 MB  | `sha256:3d2cab6d1063...` |
| oaisoftwarealliance/oai-udm   | v1.5.1 | 257 MB  | `sha256:f49f777b6d06...` |
| oaisoftwarealliance/oai-ausf  | v1.5.1 | 255 MB  | `sha256:e7a98d7f0ee8...` |

#### Dónde están los archivos

**Servidor AWS** (destino final):
```
# Imagens já carregadas no daemon Docker — prontas para uso:
docker images | grep oaisoftwarealliance
```

**Google Drive del proyecto** (copia permanente de los `.tar`):
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

Para cargar en cualquier host arm64 sin recompilar:
```bash
# copiar do Drive para o servidor e carregar:
scp -i sua-chave.pem artifacts/oai-images/oai-amf.tar ubuntu@<servidor>:~/
ssh -i sua-chave.pem ubuntu@<servidor> "docker load -i ~/oai-amf.tar && rm ~/oai-amf.tar"
# repetir para cada componente
```

Para exportar directamente desde el servidor de laboratorio (si tiene acceso SSH):
```bash
ssh ubuntu@core5g-arm64.duckdns.org "docker save oaisoftwarealliance/oai-amf:v1.5.1 -o ~/oai-amf.tar"
scp ubuntu@core5g-arm64.duckdns.org:~/oai-amf.tar .
docker load -i oai-amf.tar
```

> Guía completa de descarga (sin compilar): [`OAI-CORE-ARM64.md §Download`](../../../server/oai-cn-gnb-e2/docs/OAI-CORE-ARM64.md)

Para recompilar desde cero (requiere Mac Apple Silicon + Docker Desktop):
```bash
git clone https://github.com/henriquecarmine/Core5G_ARM64.git
cd Core5G_ARM64
cp .env.example .env   # preencher AWS_SERVER_HOST e AWS_SSH_KEY_PATH
./build-oai-arm64.sh build   # ~4 h total para os 6 componentes
./build-oai-arm64.sh save    # exporta para /tmp/oai-images/
./build-oai-arm64.sh upload  # scp para o servidor
./build-oai-arm64.sh load    # docker load no servidor
```

**Dockerfiles** con todos los patches arm64 aplicados:
```
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/docker/Dockerfile.<comp>.ubuntu
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/build/scripts/build_helper.<comp>
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/src/*/CMakeLists.txt
```

---

### 7.c Plano de usuario en arm64 (OAI v2.2.1) + xApps event-driven

> **Por qué existe esta sección.** El core v1.5.1 que compilamos (§7.b) **no tenía UPF
> en arm64** (el `oai-upf-vpp` es Intel-only, depende de `libhyperscan`). En la práctica el
> Proyecto 2 solo tenía plano de **control** — el UE nunca obtenía IP. La OAI pasó a
> publicar imágenes **multi-arch oficiales** a partir del `v2.1.10`; el **`v2.2.1`** tiene
> **7/7 NFs con arm64**, incluyendo `oai-upf` (datapath `simple_switch`). Migramos a
> él y el **user plane pasó a funcionar** (el UE obtiene IP `12.1.1.x`, tráfico real).

**Dónde vive:** `server/oai-cn-gnb-e2/oai-cn5g-v2/` (paralelo al v1.5.1, no lo sustituye).
Detalles de config en [`oai-cn5g-v2/README.md`](../../../server/oai-cn-gnb-e2/oai-cn5g-v2/README.md).
Encaja con el gNB actual: PLMN **208/95**, TAC `0xa000`, slice **SST 222 / SD 123**,
DNN **default** (pool `12.1.1.0/26`), AMF fijo `192.168.70.132`, SNAT en el UPF (UE → internet).

**Levantar el Proyecto 2 completo (por SSH):**
```bash
cd server/oai-cn-gnb-e2
./oai-cn5g-v2/up_core_v2.sh    # para o Projeto 1, sobe o core v2.2.1, espera oai-amf RUNNING
./scripts/up_e2_lab_v2.sh      # near-RT RIC + gNB (RFSIM, 24 PRBs / 51 NRB) + nrUE
```

**Ejecutar xApps — event-driven, sin timeout ciego:**
```bash
./scripts/run_xapp.sh cust    # xApp MAC/RLC/PDCP/GTP (SM custom)
./scripts/run_xapp.sh kpm     # E2SM-KPM (métricas DRB/PRB)
./scripts/run_xapp.sh rc      # E2SM-RC (controle)
./scripts/e2_verify.sh        # sobe o lab + valida E2 SETUP + roda os 3 xApps 7x cada
```
Cada `run_xapp.sh` **termina en el 1er evento de éxito** (E2 conectado + suscrito/indicación),
nunca por duración fija — determinístico. El prerrequisito se verifica por **estado** (`pgrep -x
nearRT-RIC` + `nr-softmodem`), no por `sleep`. CPU bajo control: cgroup con `CPUQuota`
(`XAPP_CPU_QUOTA`, default `50%`) + `nice`.

#### Validación de los xApps (resultado real) y los 2 bugs que estaban en el camino

Ejecutando `e2_verify.sh` (levanta el lab sin UE + 3 xApps 7× cada uno): **cust 7/7, kpm 7/7, rc 5/7**
— los xApps se conectan al RIC y **suscriben** las RAN functions (`Successfully subscribed to
RAN_FUNC_ID …`). Hasta llegar a ese resultado, dos bugs (que NO eran "falta de CPU", como
parecía al principio) tuvieron que ser corregidos:

1. **Plugins SM de arquitectura errónea (crash del RIC).** El repo versionaba
   `flexric-lib/*.so` compilados para **x86-64**; en un host **arm64** el `dlopen` del
   `nearRT-RIC` falla (`load_plugin_ric: Assertion handle != NULL`). Peor: `sync-oai`
   esparcía esos x86-64 por encima de los arm64 que el servidor había compilado. **Corrección:**
   los `.so` salieron del git (son artefactos de build, arch-específicos; ver `.gitignore`) y el
   `up_flexric.sh` ahora **detecta la arquitectura** y repuebla `flexric-lib/` del build tree
   (`sync_flexric_lib.sh`) cuando falta O es de otro arch. Auto-curable.

2. **Falso-negativo en `run_xapp.sh`.** Usaba `tail -F --pid | grep -m1` con
   `set -o pipefail`: cuando el `grep -m1` casa el evento de éxito y cierra el pipe, el `tail`
   muere con SIGPIPE y el `pipefail` marcaba el pipeline entero como falla — reportando
   `❌ FALHA` incluso con el xApp suscrito. **Corrección:** cambiado por **poll en el archivo**
   (`grep -q` en bucle hasta el evento O que el proceso muera), sin pipe, sin SIGPIPE.

#### Restricción operativa del box (2 vCPUs)

El `nr-softmodem` y el `nr-uesoftmodem` en RFSIM hacen **busy-poll** (cada uno satura ~1 vCPU →
load > 20), y entonces el camino INDICATION→Report del RIC puede exceder el timeout interno del
FlexRIC. Por eso la validación levanta **sin el nrUE** (`SKIP_UE=1`, default en `e2_verify.sh`):
el E2 es gNB↔RIC y no depende del UE, y sobra 1 vCPU entero para el RIC+xApp (load < 2). Para el
lab completo CON user plane, levante normal (`SKIP_UE=0`) — pero no corra los 7× de xApp junto.

**Medición en el servidor (2026-06-22) — el UE attach es mutuamente exclusivo con el guardrail
de cpuset.** Con el guardrail activo (`oai-lab.slice AllowedCPUs=1` = lab entero en un solo
core), el nrUE **sincroniza** (PHY/RFSIM ok: `Initial sync successful, PCI 0`, RSRP 51 dB)
pero el **RRC inunda** (`TASK_RRC_NRUE task contains` 71k→112k) y el UE **no obtiene IP**: el gNB
(CPUWeight 60) queda con ~40% del core y el nrUE (CPUWeight 20) solo ~25% — insuficiente para el RRC
en tiempo real. Liberando los **2 cores** (`AllowedCPUs=0-1`), cada proceso RFSIM gana ~1
core y el **user plane funciona de verdad**: el UE hace attach, `oaitun_ue1=12.1.1.2`, y
`ping 8.8.8.8` por la tun da **4/4, 0% pérdida, RTT ~111 ms**. O sea, lo que afirma la §7.c
(el UE obtiene IP `12.1.1.x`) **se confirma — pero exige los 2 cores**, lo que reabre el riesgo de
freeze que el guardrail previene. Trade-off: **o** protección anti-freeze (1 core, sin UE),
**o** user plane completo (2 cores, box dedicado). La prueba se hizo **sin timer**: revert
del cpuset por `trap EXIT` + espera por evento (`ip monitor` para el IP, `tail -F --pid|grep -m1`
para el flood) + monitor en `nice -20` (garantiza el revert incluso bajo saturación).

> **Recomendación para quien vaya a levantar una instancia nueva:** use **4 vCPU** (ej.: `t4g.xlarge`
> o `c7g.xlarge`). Con 4 núcleos — gNB en uno, UE en otro, RIC+xApp en otro, sistema en otro — el
> lab completo **con user plane** corre sin cpuset, sin guardrail y sin riesgo de freeze, y los
> xApps corren en paralelo al UE (esencial para el UE-TP-rApp). Los 2 vCPU son el **camino
> alternativo** (trade-off arriba). Guía completa de reproducción hasta el user plane, con los dos
> caminos: [`server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md`](../../../server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md).

> **Principio del proyecto: CERO tiempo, todo bajo control.** Nada de `sleep`/timeout ciego —
> los scripts terminan por **evento/estado** (`grep -m1` en stream, `tail -F --pid`, poll de
> condición). Ver memoria `feedback-event-driven-nao-tempo`.

---

## 8. Bugs reales encontrados y corregidos

Estos problemas existían en el material original del curso y fueron descubiertos
probando de verdad en el servidor ARM — guardados aquí para que no se pierdan.

### 8.1 — Imágenes `gradiant/open5gs` sin build arm64

`gradiant/open5gs:2.7.6` y `gradiant/open5gs-webui:2.7.6` **no tienen**
manifest `linux/arm64/v8` — a partir del tag `2.7.3` gradiant solo publica
`amd64`. `docker compose up` fallaba con
`no matching manifest for linux/arm64/v8`.

**Corrección:** fijar en `server/.env`:
```
OPEN5GS_IMAGE=gradiant/open5gs:2.7.2
WEBUI_IMAGE=gradiant/open5gs-webui:2.7.2
```
(`2.7.0`, `2.7.1` y `2.7.2` son los últimos tags con build arm64 confirmado
vía Docker Hub API. `mongo:7.0` y `gradiant/ueransim:3.2.6` ya eran
arm64-ok, sin cambio necesario.)

### 8.2 — Servicio BSF ausente (PDU Session siempre rechazada)

Después de que el core subiera 100% healthy, el UE se registraba (NAS OK) pero la sesión PDU
siempre fallaba con `PDU Session Establishment Reject [OUT_OF_LADN_SERVICE_AREA]`.

Causa raíz (encontrada en el log del PCF, no en el del UE): `No http.location` en
`nbsf-handler.c:436` — el PCF intenta registrar el *binding* de la sesión en la
**BSF** vía NRF, pero:
1. **No había servicio `bsf` en el `docker-compose.yml`** (a pesar de que el binario
   `open5gs-bsfd` existía en la imagen).
2. Ya existía un `configs/open5gs/bsf.yaml` en el proyecto original, pero con la
   dirección de **ejemplo por defecto** (`127.0.0.15`), fuera del esquema de red
   real del proyecto (`10.10.0.x` en la `net-sbi`).

O sea: ítem olvidado en la configuración original del curso, no causado por el
cambio de versión de imagen (§8.1).

**Corrección:**
- `server/configs/open5gs/bsf.yaml`: dirección corregida a `10.10.0.18`
  (siguiente IP libre), client `scp` apuntado a `10.10.0.200:7777`.
- `server/docker-compose.yml`: nuevo servicio `bsf` agregado (mismo patrón
  que el `nssf`), contenedor `open5gs-bsf-containerized`.

Después de levantar el BSF, todavía apareció un segundo error transitorio
(`Registration reject [95]` / `amf_npcf_am_policy_control_handle_create()
failed`) — estado huérfano de intentos de sesión anteriores. Resuelto con
restart limpio de `amf`, `smf`, `pcf`, `bsf` (y los otros NFs del core).

### 8.3 — Nombre del proyecto Compose no fijado (riesgo de perder datos al mover carpetas)

`docker-compose.yml` no tenía un `name:` explícito arriba. Las **redes**
(`net-n2`, `net-n3` etc.) ya tenían `name:` fijo individualmente, pero los
**volúmenes nombrados** de Mongo (`mongodb-data`, `mongodb-config`) no — el
nombre de ellos se deriva del nombre del directorio donde se ejecuta el
`docker compose`. Al reorganizar el repo (mover de `open5gs-containerized/` a
`server/`), esto habría recreado los volúmenes desde cero, **perdiendo el suscriptor
registrado**.

**Corrección:** agregado `name: open5gs-containerized` arriba del
`docker-compose.yml` — cualquier carpeta/directorio de ejecución futura mantiene
los mismos volúmenes/redes/contenedores.

> Vale considerar reportar los bugs 7.1–7.3 al profesor — otros grupos
> usando el mismo material original probablemente chocan con los mismos errores.

### 8.4 — El venv del panel quedaba sin `pip` (verificación de idempotencia confundida por estado parcial)

En el bootstrap del `server/panel/`, la etapa de crear el venv verificaba
`[ ! -x ~/server/panel/.venv/bin/python3 ]` para decidir si lo recreaba. En un
primer intento, `python3-venv` todavía no estaba instalado cuando el
`python3 -m venv` corrió — el `ensurepip` falló, pero el venv quedó parcialmente
creado (solo los symlinks de `python3`, sin `pip`/`activate`). En la ejecución
siguiente, el symlink `python3` ya existía y *era* ejecutable, así que la verificación
de idempotencia creía que el venv estaba ok y saltaba la recreación — dejando
que el `pip install` fallara con "No such file or directory".

**Corrección:** instalar `python3-venv`/`python3-pip` siempre (vía `apt-get
install`, que ya es idempotente por naturaleza) antes de verificar/recrear el venv,
en vez de intentar inferir si el paquete ya está instalado.

### 8.5 — Informes con falso-negativo (nombre de contenedor ≠ servicio Compose)

Descubiertos **ejecutando los informes en vivo** (no en `bash -n`), v0.25.2. Son
bugs de nuestra capa de diagnóstico, no del material original — pero engañarían al
profesor, así que valen el registro:

- **`test_ng_setup` / `test_registration` decían "AMF no está corriendo"** con el
  AMF perfectamente al aire. Causa: los scripts hacían `docker inspect amf`, pero
  `amf` es el nombre del **servicio Compose** — el **contenedor** se llama
  `open5gs-amf-containerized`. `docker inspect`/`exec`/`logs` exigen el nombre del
  **contenedor**; solo `docker compose logs` acepta el nombre del **servicio**. El
  `inspect` fallaba → el cruce con el AMF se convertía en advertencia → `test_ng_setup`
  concluía *"N2 no confirmada"* **incluso con `NGSetupResponse` recibido**.
- **`test_ue_connection` mostraba `IP público <!DOCTYPE html>`.** `wget
  http://ifconfig.me` devuelve la **página HTML**, no la IP. Corregido a
  `http://ifconfig.me/ip` (texto plano) + extracción/validación de la IP por regex.
- **Veredicto final siempre "ok".** `test_ue_connection` terminaba en `summary ...
  ok` independientemente de las verificaciones. Reescrito con contadores `fails`/`warns`
  y veredicto honesto (✗ crítico / ! reserva / ✓ todo pasó).

**Lección:** `bash -n` valida sintaxis, no semántica. Un informe nuevo/alterado tiene
que **correr en vivo** antes del merge. Detalles en
[`docs/relatorios-didaticos.md`](../../relatorios-didaticos.md) §5.

### 8.6 — La demo E2E medía el bridge Docker, no el túnel 5G

El paso de throughput de la Demostración E2E (`demo_e2e.sh`) hacía
`iperf3 -c 10.50.0.100` desde dentro del contenedor del UE. Pero el DN
(`open5gs-dn-containerized`, `10.50.0.100`) está en la **misma red Docker** donde el
contenedor del UE tiene la `eth0` — entonces el iperf salía **directo por el bridge Docker, no
por el túnel 5G** (`uesimtun0`, pool `10.60.0.0/16`). Resultado: no medía el núcleo
y encima fallaba por *timing* del servidor `iperf3 -s -1`.

**Corrección (v0.25.0):** crear una **ruta temporal hacia el DN vía `uesimtun0`** y
**amarrar el origen a la IP del túnel** (`iperf3 -B 10.60.0.x`), forzando el camino
real `UE → gNB → UPF (NAT en la N6) → DN`; la ruta se elimina al final. Validado en
vivo: **149 Mbit/s** atravesando el núcleo 5G (antes: sin medición). De paso, la
Demo E2E pasó a ecoar el **comando real + salida real + "Por qué"** de cada paso.

---

## 9. Validación de extremo a extremo (estado actual confirmado)

Probado en el servidor vía `./deploy.sh up core` + `./deploy.sh up ran`:

1. `add-subscriber.sh` registra el IMSI `001010000000002` en el MongoDB.
2. El UE (UERANSIM) se registra: NG Setup → Autenticación 5G-AKA → Security Mode →
   `Initial Registration is successful`.
3. PDU Session Establishment Accept → `uesimtun0` sube con IP `10.60.0.2`.
4. `ping -I uesimtun0 8.8.8.8` → **4/4 paquetes, 0% pérdida, RTT ~10ms**.
5. `healthcheck.sh`: NRF healthy, N2/N3/N4/N6 todos OK, asociación PFCP
   establecida, UE corriendo con conectividad activa.

**Uso de recursos** con core + RAN completos corriendo: ~492 MiB / 906 MiB de
RAM, ~342 MiB de swap, CPU de cada contenedor por debajo de 2% (MongoDB el más
pesado, ~13% de un core). **La instancia pequeña sostiene el Proyecto 1
completo con holgura.**

El riesgo de RAM real queda para el Proyecto 2 (el build del OAI desde el source es
CPU/RAM-intensivo) — todavía no medido, probar con cautela.

**Verificación en vivo de todos los informes (2026-06-21, v0.25.0–0.25.3):**
corridos de verdad, no solo `bash -n`. **Proyecto 1** — `status`,
`system-status`, `ng-setup`, `registration`, `config-coherence`,
`ue-connection` y `upf-failover` (failover manteniendo conectividad) pasan, todos
con encabezado de sección, verificaciones coloreadas y bloque "Resumen"; 3 bugs de precisión
encontrados y corregidos (§8.5). **Proyecto 2** — `e2-sm` (cadena O-RAN de extremo a extremo,
7 suscripciones), `e2-kpm` (suscripción OK, veredicto honesto "sin tráfico en el
período") y `e2-rc` (eventos RRC del attach capturados) pasan, sin bugs. La
Demostración E2E mide **149 Mbit/s** reales por el túnel 5G (§8.6).

---

## 10. Pendientes / próximos pasos

- [x] **Checklist del artículo científico (Prof. Jonas, 2026-07-02) — 7 de 8
      concluidos** (v0.32.0–0.33.1): topología con bandas **CUPS** (plano de
      control × plano de usuario), **N1** explícito (lógico vía gNB) y
      **N11/Nsmf** rotulado, layout re-grillado sin ninguna línea atravesando
      card de terceros (verificador en `panel/test/check-topology.py`),
      IPs/puertos estandarizados, **temas claro/oscuro** (regla de oro: consolas
      oscuras en los 2 temas con paleta ISO fija `TERM` — nunca variables de tema
      en contenido de terminal), anotaciones didácticas en el arranque de cada servicio
      (`SERVICE_ROLES`), HTML con `no-cache` (el deploy llega al instante) y
      **política de costos** ([`docs/POLITICA-DE-CUSTOS.md`](../../POLITICA-DE-CUSTOS.md)).
- [ ] **i18n — pt/en/es/fr** (ítem 1b del checklist; decisión 2026-07-03: proyecto
      internacional, TODO en 4 idiomas, fr incluido). **F1 lista (v0.34.0)**:
      infra `static/i18n.js` (diccionarios + fallback lang→en→pt + prueba de
      paridad `npm run test:i18n`), selector 🌐, login + topbar traducidos;
      READMEs en 4 idiomas + `docs/i18n/<lang>/` con `check-parity.py`.
      **Faltan**: F2 (index entero), F3 (topología/JSONs), F4 (scripts bash
      vía `LAB_LANG`); docs técnicos en en bajo demanda. Reglas en
      CONTRIBUTING §7 (el glosario 3GPP/O-RAN no se traduce).
- [ ] **Lab de RIC Near-RT/Non-RT con IA** (scikit-learn aarch64 ya vendorado
      en `server/panel/vendor/`): xApp de inferencia en el loop de segundos +
      rApp de entrenamiento en el Non-RT. **Depende del upgrade a 4 vCPU** — análisis de
      costo y runbook del resize reversible en la política de costos §3.
- [ ] Confirmar con el profesor la rúbrica/plan de pruebas oficiales del
      Proyecto 2 (no publicados en el repo de origen en la fecha de la verificación).
- [x] Diagnóstico del estado real del Proyecto 2 (2026-06-18): nada estaba
      funcional — los `.so` de Service Model eran x86-64 (erróneo para ARM64),
      el único log existente mostraba E2SM-RC fallando con core dump, sin
      ningún binario compilado en el servidor. Ver `CHANGELOG.md` v0.8.0.
- [x] Compilar y validar `server/oai-cn-gnb-e2/` (2026-06-19): 6 imágenes OAI
      5G Core arm64 construidas en el Mac Apple Silicon, cargadas en el servidor;
      `up_e2_lab.sh` levanta Core OAI + nearRT-RIC + gNB(E2) + nrUE; E2 SETUP OK,
      8 RAN functions registradas (2,3,142–148), `test_e2_sm.sh all` pasa
      (los xApps suscriben KPM/RC/MAC/RLC/PDCP/GTP). El UE llega a `RRC_CONNECTED`.
- [x] **Estabilidad de la instancia** (2026-06-19): el gNB/nrUE RFSIM saturaban
      los 2 vCPUs del `t4g.medium` y **congelaban la máquina** (varios reboots
      forzados). Corregido envolviendo los procesos nativos en *scopes* de
      systemd con `CPUQuota` (120%/60%) + `CPUWeight=20` + `nice 10` en
      `up_gnb_oai.sh` — reserva CPU para el sistema, impide el freeze sin romper
      el E2 (validado: máquina responsiva bajo carga, E2 SM test pasa).
- [ ] **xApp UE-TP-rApp** (tema del grupo): predicción de throughput por UE a
      partir de RSSI/RSRP/CQI/PRB. Esqueleto en `xapp_ue_tp_moni.c`; falta el
      modelo de predicción. **Próximo gran paso después de la presentación.**
- [ ] **🧱 Upgrade a 4 vCPU — bloqueo de HW para el informe completo de KPM.**
      Recolectar KPM con **throughput real** (datos no-cero para el análisis y el
      UE-TP-rApp) exige UE+gNB RFSIM en tiempo real, lo que **no cabe en 2 vCPU bajo
      el guardrail**. Forzar 2 cores (remover el guardrail) **congeló el box 2×**
      (reboots). Decisión: el recolector (`kpm_collect_real.sh`) **nunca toca el cpuset**
      y concluye honesto en 2 vCPU; **los datos reales dependen de una instancia 4 vCPU**
      (`t4g.xlarge`). Por ahora, demostración segura = KPM suscrito + análisis sobre la
      muestra (`kpm_analytics.sh`). Ver [`docs/KPM-COLETA-RESILIENTE.md`](../../../server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md).
- [x] **User plane del UE en el Proyecto 2 — RESUELTO en el core v2.2.1** (2026-06-22):
      el UE hace attach, obtiene IP `12.1.1.2` y tiene tráfico real (`ping 8.8.8.8` 0% pérdida
      por la `oaitun_ue1`). El bloqueo **no era** el AUSF↔UDM HTTP/2 (ese era del
      core **v1.5.1**); en el v2.2.1 el cuello de botella es **CPU**: en 2 vCPU con el guardrail de
      cpuset (1 core), gNB y UE dividen el core y el RRC del UE inunda. Con los **2
      cores** liberados (o **4 vCPU**, recomendado), el UE hace attach normal. Trade-off
      y procedimiento timer-free en [`server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md`](../../../server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md)
      y §7.c.
- [ ] Persistir los symlinks del FlexRIC (`/usr/local/lib/flexric` y
      `/usr/local/etc/flexric`) en `infra/server-bootstrap.sh` — hoy se
      crean a mano y se pierden al cambiar de instancia.
- [x] Grupo "Projeto 2 — OAI/FlexRIC (E2)" en el panel (`server.py` +
      `index.html`): botones up/down/test del E2 lab, mismo mecanismo
      genérico `data-cmd` → `POST /api/run/{cmd}` del Proyecto 1.
- [ ] Evaluar reportar los bugs del §8 al profesor/repositorio original.
- [ ] Implementar el resto del blueprint del panel de observabilidad
      (`docs/blueprint-painel-observabilidade.md`) — telemetría (§5) y
      logs filtrados (§5) ya hechos sin Loki/Grafana/Prometheus; falta el
      sensor de protocolo E2/NGAP/GTP-U + topología interactiva
      (pedagógico, más ambicioso).
- [x] **Registro de UE**: formulario en el panel (IMSI/K/OPc/MSISDN/AMF)
      con help text por campo, llama a `./scripts/add-subscriber.sh` vía
      `POST /api/subscriber`; guest bloqueado con 403.
- [x] **Herramientas de prueba en el panel**:
  - Prueba de banda: `iperf3` entre `ueransim` (uesimtun0) y `dn` —
    baseline ~150 Mbits/s confirmado (`scripts/test_throughput.sh`).
  - Prueba de interferencia/distancia: `tc netem` en uesimtun0 vía
    `scripts/test_channel.sh` (modelos 3GPP TR 38.901 + Shannon). Ideal
    ~148 Mbit/s → 1km/media ~608 Kbit/s (pérdida/RTT acompañan).
- [x] **Colorimetría ISO/ANSI + resumen didáctico en todas las pruebas**
      (v0.12.0): lib `scripts/lib/testlog.sh` + render ANSI en el panel; cada
      prueba termina con "Qué hizo" + "Resultado" coloreado. Ver `CHANGELOG.md`.
- [x] **Auditoría didáctica + verificación en vivo de todos los informes**
      (v0.25.0–0.25.3): Demo E2E con comando/salida real + "Por qué" y
      throughput corregido (149 Mbit/s por el túnel 5G, §8.6); P1 y P2 corridos en
      vivo, 3 bugs de precisión corregidos (§8.5); guía dev en
      [`docs/relatorios-didaticos.md`](../../relatorios-didaticos.md).
- [x] **Anti-freeze**: gNB/nrUE RFSIM corren bajo `systemd-run --scope` con
      `CPUQuota`/`CPUWeight`/`nice` en `up_gnb_oai.sh`, `test_e2_kpm.sh` y
      `test_e2_rc_attach.sh` — la instancia de 2 vCPUs ya no se congela.

> **Detalle operativo (5G-AKA / SQN):** si el UE no se registra y el log muestra
> `Authentication Failure due to SQN out of range`, el número de secuencia del
> suscriptor (UDM/MongoDB) se desincronizó del SIM. Solución: re-registrar el
> suscriptor (`./scripts/add-subscriber.sh`, que elimina+inserta y pone en cero el SQN) y
> reiniciar el UE (`docker restart ueransim`). El `uesimtun0` vuelve en segundos.

---

## 11. Referencias dentro del repositorio

- [`README.md`](../../../README.md) — puerta de entrada: **cómo reproducir** el estado
  actual desde cero, roadmap con fechas y **cómo colaborar** (contacto:
  [hc@cesar.school](mailto:hc@cesar.school) · [@henriquecarmine](https://github.com/henriquecarmine)).
- [`CHANGELOG.md`](../../../CHANGELOG.md) — historial cronológico detallado de cada acción.
- [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) — cómo colaborar (Issues/Discussions/PR, validación, versión).
- [`docs/relatorios-didaticos.md`](../../relatorios-didaticos.md) — **guía dev del sistema de informes**: lib `testlog.sh`, protocolo de la Demo E2E, cómo agregar un informe, gotchas (§8.5–8.6) e inventario P1/P2.
- [`docs/blueprint-painel-observabilidade.md`](../../blueprint-painel-observabilidade.md) — diseño del panel.
- [`docs/labs/`](../../labs) — guías originales del curso (instalación Docker, pre-lab GCP/VM, core Open5GS, UERANSIM, informe de entrega).
- [`server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md`](../../../server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md) — guía oficial del Proyecto 2.
- [`server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md`](../../../server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md) — **guía de reproducción hasta el user plane** (UE con IP + ping): dimensionamiento de CPU (**4 vCPU recomendado vs 2 vCPU alternativo**), arranque del core v2.2.1 + E2 + xApps, y el procedimiento timer-free de liberar/revertir los 2 cores.
- [`server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md`](../../../server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md) — **Datos en la RAN**: pipeline didáctico `kpm_analytics.sh` (Clase 06, diapositiva 46) que transforma el log KPM crudo en serie temporal CSV + KPIs por UE + sparkline; puente hacia el UE-TP-rApp y el Módulo 7 (Análisis de Datos).
- [`server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md`](../../../server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md) — **ingeniería milimétrica** del `kpm_collect_real.sh`: recolecta KPM con tráfico real **resiliente y 100% por evento** (heartbeat "no se trabó", auto-retry, auto-revert del cpuset, watchdog anti-hang) — el patrón de "cero tiempo" aplicado, para la presentación en vivo.
- `pdfs/` — diapositivas de las Clases 01–04 + planilla de composición de grupos (fuente de todo en el §1).
