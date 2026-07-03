# Core5G ARM64

**🌐 [Português](README.md) · [English](README.en.md) · Español · [Français](README.fr.md)**
<!-- sync: v0.34.0 -->

> 🌐 Traducción al español de [README.md](README.md) — sincronizada con **v0.34.0 (2026-07-03)**.
> El portugués es el idioma canónico; los documentos enlazados están en portugués salvo indicación.

Laboratorio 5G completo ejecutándose en **AWS Graviton (ARM64)**, con panel web
de control propio. Reúne **dos proyectos** independientes de la asignatura
*RAN Intelligent Controller (RIC)* — CESAR School (tema del grupo: **UE-TP-rApp**):

| Proyecto | Stack | Carpeta | Estado |
|---|---|---|---|
| **Proyecto 1** | Open5GS (5GC) + UERANSIM (gNB/UE simulados) | `server/` | ✅ Presentado el 13/06/2026, validado de extremo a extremo |
| **Proyecto 2** | OAI 5GC + gNB RFSIM + agente E2 + **FlexRIC** (near-RT RIC) + xApps | `server/oai-cn-gnb-e2/` | ✅ Presentado el 20/06/2026 |

**Fase actual (jul/2026): artículo científico** — el Prof. Jonas está
redactando el artículo (Overleaf) y pidió una lista de 8 mejoras en la
plataforma (02/07/2026). Estado: **7 de 8 completadas** en el panel v0.34.x —
topología con bandas **CUPS** (plano de control × plano de usuario), interfaces
**N1/N11** explícitas, layout sin solapamientos, **temas claro/oscuro**, colores
**ISO** en todos los terminales, anotaciones didácticas al arrancar cada
servicio, **selector de idioma (PT/EN/ES/FR)** y la
[política de costes](docs/POLITICA-DE-CUSTOS.md) (pt). Pendiente: i18n completo
del panel más allá de login/topbar.

> **¿Solo quieres entender el qué/por qué de todo?** Lee la
> [**biblia del proyecto**](core5g-arm64-bible.md) (pt — referencia conceptual
> completa). Para la historia cronológica, el [**CHANGELOG**](CHANGELOG.md) (pt).
> Para los guiones de laboratorio, [`docs/labs/`](docs/labs/) (pt).
>
> Este README es la **puerta de entrada**: cómo reproducir el estado actual, qué
> falta y cómo colaborar.

---

## 1. Cómo llegar hasta aquí (reproducción desde cero)

El flujo es **todo local, deploy vía `deploy.sh`**. Nunca editas archivos
directamente en el servidor — editas `server/` en tu máquina y `deploy.sh` lo
refleja en el servidor por SSH/rsync.

### 1.1 Requisitos

- **Cuenta AWS** con una instancia EC2 **ARM (Graviton)**, Ubuntu 22.04+.
  Recomendado: **`t4g.medium`** (2 vCPU, 4 GB) — la `t4g.micro` solo ejecuta el
  Proyecto 1. Volumen EBS de **30 GB**.
- Tu máquina local con `bash`, `git`, `rsync`, `ssh` y `openssl`.
- Para **construir** las imágenes OAI arm64: un **Mac Apple Silicon** (u otra
  máquina arm64) con Docker. Las imágenes listas **no están en git** (~362 MB) —
  se distribuyen por el Google Drive del grupo.

### 1.2 Clonar y configurar

```bash
git clone https://github.com/henriquecarmine/Core5G_ARM64.git
cd Core5G_ARM64
cp .env.example .env
```

Edita el `.env` (nunca lo publiques en git — está en `.gitignore`):

```ini
AWS_SERVER_HOST=core5g-arm64.duckdns.org   # dominio DuckDNS o IP de la instancia
AWS_SERVER_USER=ubuntu
AWS_SSH_KEY_PATH=ssl/core5g_openran_arm64.pem   # tu clave SSH (.pem), NUNCA en git

DUCKDNS_DOMAIN=core5g-arm64                 # opcional: IP dinámica automática
DUCKDNS_TOKEN=<tu-token>

PANEL_USER=professor                        # Profesor (admin) — acceso total
PANEL_PASSWORD=<contraseña-fuerte>
PANEL_GUEST_USER=guest                      # habilita el acceso de Alumno (solo lectura)
PANEL_GUEST_PASSWORD=<contraseña-guest>     # opcional (los alumnos entran con nombre+correo)
PANEL_EXTRA_USERS=professor2:clave2         # admins extra: user:clave,user2:clave2
```

> **Roles (modo aula):** el *Profesor* opera (solo **uno a la vez**); el *Alumno*
> sigue la clase en vivo y entra con **nombre + correo** (sin contraseña). Ver §1.6.

### 1.3 Aprovisionar el servidor (una vez)

```bash
./deploy.sh bootstrap     # Docker + swap 8 GB + DuckDNS + Caddy (HTTPS) + panel
```

Idempotente — ejecútalo cuantas veces quieras. Al terminar, el panel responde en
`https://<tu-host>/` con TLS válido (Let's Encrypt vía Caddy) y pantalla de login.

### 1.4 Proyecto 1 — Open5GS + UERANSIM

```bash
./deploy.sh up all        # levanta el Core 5G (Open5GS) + RAN (UERANSIM)
./deploy.sh status        # docker ps + healthcheck (N2/N3/N4/N6)
```

Validación de extremo a extremo: el UE se registra (5G-AKA), abre una PDU
Session y obtiene conectividad real (`ping -I uesimtun0 8.8.8.8` → 0% de
pérdida). Todo esto también está expuesto como botones en el panel (UE Lab,
Demostración E2E).

### 1.5 Proyecto 2 — OAI + FlexRIC (E2)

Las imágenes OAI arm64 deben estar cargadas en el Docker del servidor:

```bash
# (en el Mac arm64) construir y exportar las 6 imágenes — ver biblia §7.b:
cd server/oai-cn-gnb-e2 && ./build-oai-arm64.sh        # AMF→SMF→NRF→UDR→UDM→AUSF
# exporta /tmp/oai-images/oai-*.tar (~60 MB cada una). Súbelas al Drive del grupo.

# enviar el directorio del Proyecto 2 (una vez, ~230 MB):
./deploy.sh sync-oai

# en el servidor: docker load -i ~/oai-<comp>.tar  (cada componente del Drive)
```

Con las imágenes cargadas, el laboratorio E2 se levanta **desde el panel**
(selector de proyecto → *Proyecto 2*) o por SSH:

```bash
./deploy.sh ssh
cd ~/server/oai-cn-gnb-e2
./scripts/up_e2_lab.sh           # Core OAI + nearRT-RIC + gNB(E2) + nrUE
./scripts/test_e2_sm.sh all      # ejercita los 8 Service Models vía xApps
```

> **¿Por qué `t4g.medium`?** El gNB/nrUE RFSIM son intensivos en CPU. Con 2 vCPU
> pueden saturar y **congelar la instancia**. La protección usa **cgroup v2
> cpuset**: el `bootstrap` crea la slice `oai-lab.slice` fijada **fuera de la
> CPU 0** (`AllowedCPUs=1`), reservando un núcleo para el sistema
> (SSH/Docker/panel/Caddy con `CPUWeight` máximo). Así el laboratorio nunca tumba
> la máquina. (En este kernel ARM `CPUQuota`/CFS no se aplica; por eso cpuset.)
> Detalles en [`infra/server-bootstrap.sh`](infra/server-bootstrap.sh).

### 1.6 Panel web — modo aula

`https://<tu-host>/` — el panel es una SPA (FastAPI + HTML/CSS/JS, sin build).
Funciones base: telemetría en vivo, logs filtrados/coloreados (ANSI/ISO) con
**explicación didáctica** al final, UE Lab, Demostración E2E, **selector de
proyecto** (encender uno apaga el otro), **topología interactiva**
(contenedores/puertos/redes reales, clicables) y las pruebas de Service Model
E2 — cada una con **resumen final**. Interfaz en **4 idiomas** (PT/EN/ES/FR,
selector 🌐) y **temas claro/oscuro**.

Además, un **modo aula** pensado para presentar ante un auditorio:

- **Roles Profesor / Alumno.** El *Profesor* (admin) opera; el *Alumno* (guest)
  sigue en modo solo lectura, entrando con **nombre + correo** (1 clic, sin
  contraseña) — el correo es el **registro de asistencia** del grupo.
- **Un Profesor a la vez.** El puesto es "pegajoso": un 2º admin queda bloqueado
  hasta que el actual salga (logout) o quede inactivo 10 min.
- **Espejo EN VIVO.** Todo lo que ejecuta el Profesor se transmite en tiempo
  real a los Alumnos (consola + pantalla abierta), vía ring-buffer + polling.
- **Resultados + Replay.** Cada ejecución se guarda en disco (sobrevive a
  reinicios) y puede **reproducirse** después, línea a línea.
- **RAN en vivo (P2).** Sparklines con SNR/MCS/PRB/BLER reales del gNB OAI.
- **Modo proyección (kiosk).** Botón "⛶ Proyección" → pantalla limpia a pantalla
  completa para el proyector.
- **Quién está mirando.** El Profesor pulsa el badge "👁 N alumnos" y ve la lista
  de conectados y la asistencia.

---

## 2. Qué falta (hoja de ruta)

| Cuándo | Ítem | Estado |
|---|---|---|
| **Corto plazo** | **i18n completo del panel — pt/en/es/fr** más allá de login/topbar (fases F2 index, F3 topología, F4 scripts bash vía `LAB_LANG`) | ⏳ F1 lista (v0.34.0) |
| Corto plazo | xApp **UE-TP-rApp** (predicción de throughput por UE) — tema del grupo. Wheels de **scikit-learn aarch64** ya incluidos (`server/panel/vendor/`) | ⏳ Falta el modelo |
| 🧱 **Bloqueo de HW** | **El laboratorio de RIC (Near/Non-RT) con IA y el informe KPM con throughput real requieren 4 vCPU.** Análisis de coste y runbook del resize reversible: [`docs/POLITICA-DE-CUSTOS.md`](docs/POLITICA-DE-CUSTOS.md) §3 (pt) | ⚠️ Pendiente de aprobación |
| ✅ Resuelto | **Checklist del artículo, puntos 2–7 + temas** (Prof. Jonas, 02/07/2026) | ✅ v0.32.0–0.33.1 |
| ✅ Resuelto | **Política de costes** (punto 8) + higiene de disco (3,1 → 8,6 GB libres) | ✅ (pt) |
| ✅ Resuelto | **Plano de usuario del UE en el Proyecto 2** (core v2.2.1) | ✅ Validado 22/06 |
| Medio plazo | Sensor de protocolo E2/NGAP/GTP-U en el panel | 📋 Planificado |
| Medio plazo | Persistir los symlinks de FlexRIC en el `bootstrap` | 📋 Planificado |
| Algún día | Reportar los bugs del §8 de la biblia al repositorio OAI original | 📋 Planificado |

La lista canónica y detallada vive en la [biblia §10](core5g-arm64-bible.md#10-pendências--próximos-passos) (pt).

---

## 3. Cómo colaborar

Las contribuciones del grupo (y de cualquiera que estudie el laboratorio) son
bienvenidas. La guía completa está en **[`CONTRIBUTING.md`](CONTRIBUTING.md)** (pt):

- **[Issues](../../issues)** — reportar un bug, proponer una idea, preguntar.
- **[Discussions](../../discussions)** — conversar / preguntar "cómo funciona X".
- **Pull Request** — *fork* → rama → PR describiendo *qué cambió y por qué*.

Reglas de oro: edita **siempre en local** (`deploy.sh` es el único camino al
servidor); **los secretos nunca entran en git** (`.env`, `ssl/*.pem`); **los
datos de alumnos** (correos/lista) se quedan solo en el servidor. Las
traducciones deben mantener los 4 idiomas en paridad (`npm run test:i18n` y el
verificador de docs).

**¿Acceso de colaborador o las imágenes OAI arm64 del Drive?** Escríbeme:

- **Henrique Carmine** — [henriquecarmine@gmail.com](mailto:henriquecarmine@gmail.com) ·
  [@henriquecarmine](https://github.com/henriquecarmine)

---

## 4. Mapa del repositorio

```
.
├── README.md                  ← puerta de entrada (pt; variantes en/es/fr al lado)
├── LICENSE                     ← licencia MIT
├── CONTRIBUTING.md            ← cómo colaborar (pt)
├── core5g-arm64-bible.md      ← referencia conceptual completa (pt)
├── CHANGELOG.md               ← diario cronológico (pt)
├── deploy.sh                  ← entrypoint único de deploy (local → servidor)
├── .env.example               ← plantilla de configuración (copiar a .env)
├── .github/                   ← plantillas de Issue y Pull Request
├── docs/                      ← blueprint del panel + guiones de laboratorio
│   ├── POLITICA-DE-CUSTOS.md  ← costes, reglas de operación y upgrade de CPU
│   ├── i18n/                  ← docs traducidos (réplicas en/es/fr)
│   └── relatorios-didaticos.md ← guía dev: cómo funcionan los tests/informes
├── infra/                     ← bootstrap del servidor + unidad systemd del panel
└── server/                    ← todo lo que corre en el servidor
    ├── panel/                 ← panel web (FastAPI) — ver panel/README.md
    │   ├── test/              ← tests headless (loaders, topología/temas, i18n)
    │   └── vendor/            ← wheels aarch64 de scikit-learn (lab RIC + IA)
    ├── ueransim/              ← RAN simulada (Proyecto 1)
    ├── scripts/               ← demo E2E, cambio de proyecto, lib de logs ISO
    └── oai-cn-gnb-e2/         ← Proyecto 2 (OAI + FlexRIC + xApps)
```

---

## 5. Equipo

- **Coordinación (orientación):** Prof. Dr. Jonas Augusto Kunzler — [jak@cesar.school](mailto:jak@cesar.school)
- **Desarrollo y mantenimiento:** Henrique Carmine — Perito Forense Digital
  (Gobernanza de TI y Telecomunicaciones), estudiante de máster en Open RAN bajo
  la orientación del Prof. Jonas Kunzler —
  [henriquecarmine@gmail.com](mailto:henriquecarmine@gmail.com) ·
  [@henriquecarmine](https://github.com/henriquecarmine)

Proyecto **coordinado por el Prof. Dr. Jonas Augusto Kunzler** y **mantenido por
Henrique Carmine**. CESAR School · asignatura *RAN Intelligent Controller (RIC)*
· tema **UE-TP-rApp**. Licencia **[MIT](LICENSE)**.

---

## 6. Apoya este proyecto

Este laboratorio está **en línea 24/7** en un servidor ARM de AWS, pagado del
bolsillo del mantenedor — para que cualquiera estudie 5G/O-RAN, lo use en clase
o en investigación. Mantenerlo en línea tiene un coste mensual real.

Si el proyecto te fue útil, **cualquier aporte ayuda a mantener el servidor
encendido** 🙏

> **PIX (Brasil):** `henrique@titannium.us` (clave e-mail)

Gracias de corazón — cada ayuda mantiene el laboratorio disponible para la
siguiente persona.
