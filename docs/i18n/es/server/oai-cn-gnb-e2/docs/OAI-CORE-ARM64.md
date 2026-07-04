<!-- sync: e36a3f4e -->
> 🌐 Traducción al **español** del documento canónico en portugués [`server/oai-cn-gnb-e2/docs/OAI-CORE-ARM64.md`](../../../../../../server/oai-cn-gnb-e2/docs/OAI-CORE-ARM64.md). Todos los idiomas: [INDEX](../../../INDEX.md) · sincronización verificada por `docs/i18n/check-parity.py`.

# OAI 5G Core — Build para arm64 (Apple Silicon → AWS Graviton2)

Guía completa para compilar las imágenes Docker del OAI 5G Core Control Plane para
la arquitectura `linux/arm64`, exportarlas como `.tar` y cargarlas en un servidor AWS
t4g (Graviton2 / aarch64).

---

## ¿No quieres compilar? Descarga las imágenes ya listas

Las 6 imágenes ya fueron compiladas y están disponibles. No necesitas hacer el build desde cero.

### Opción A — Google Drive del proyecto (recomendada)

Los archivos `.tar` están en:

```
PROJETOS/Core5G_ARM64/artifacts/oai-images/
├── oai-amf.tar    (63 MB)
├── oai-smf.tar    (60 MB)
├── oai-nrf.tar    (60 MB)
├── oai-udr.tar    (61 MB)
├── oai-udm.tar    (59 MB)
└── oai-ausf.tar   (59 MB)
```

> Los `.tar` no se versionan en git (son muy grandes), pero permanecen de forma permanente en el Google Drive del proyecto.

Para cargar en un host arm64:

```bash
# copiar os .tar para o servidor e carregar
scp -i sua-chave.pem oai-amf.tar ubuntu@<servidor>:~/
ssh -i sua-chave.pem ubuntu@<servidor> "docker load -i ~/oai-amf.tar && rm ~/oai-amf.tar"

# ou carregar direto no host local
docker load -i oai-amf.tar
```

Repite para cada componente (`oai-smf`, `oai-nrf`, `oai-udr`, `oai-udm`, `oai-ausf`).

### Opción B — Exportar desde el servidor de laboratorio

Las imágenes ya están cargadas en el servidor AWS Graviton2 (`core5g-arm64.duckdns.org`).
Si tienes acceso SSH al servidor, expórtalas directamente desde allí:

```bash
ssh ubuntu@core5g-arm64.duckdns.org \
  "docker save oaisoftwarealliance/oai-amf:v1.5.1 | gzip" > oai-amf.tar.gz

# descompactar e carregar no seu host:
docker load -i oai-amf.tar.gz
```

O copiar el archivo sin compresión:

```bash
ssh ubuntu@core5g-arm64.duckdns.org "docker save oaisoftwarealliance/oai-amf:v1.5.1 -o ~/oai-amf.tar"
scp ubuntu@core5g-arm64.duckdns.org:~/oai-amf.tar .
docker load -i oai-amf.tar
```

### Verificar tras la carga

```bash
docker images | grep oaisoftwarealliance
docker run --rm oaisoftwarealliance/oai-amf:v1.5.1 uname -m
# esperado: aarch64
```

---

## ¿Por qué es necesario compilar?

Las imágenes oficiales en `hub.docker.com/u/oaisoftwarealliance` son **exclusivamente
`amd64`**: no hay ninguna variante `linux/arm64/v8` publicada para la tag `v1.5.1`.
Cualquier intento de ejecutar esas imágenes en un host arm64 sin QEMU configurado falla con:

```
exec /usr/bin/python3: exec format error
```

y el contenedor sale con código 255.

---

## Requisitos previos

| Requisito | Detalle |
|---|---|
| Máquina de build | Mac Apple Silicon (M1/M2/M3/M4) — arm64 nativo |
| Docker Desktop | ≥ 4.x con el engine `linux/arm64` habilitado |
| Espacio en disco | ≥ 20 GB libres |
| Tiempo estimado | ~40 min por imagen × 6 = ~4 h en total |
| Acceso SSH | clave PEM con acceso al servidor de destino |
| `.env` configurado | `AWS_SERVER_HOST`, `AWS_SERVER_USER`, `AWS_SSH_KEY_PATH` |

> **¿Por qué Mac Apple Silicon?**
> El Docker Desktop en los M-series ejecuta contenedores `linux/arm64` _de forma nativa_,
> sin emulación QEMU. Compilar el OAI (C++ pesado con ~200 archivos por componente)
> mediante emulación tomaría de 5 a 10× más tiempo y con frecuencia se cuelga por OOM.

---

## Imágenes compiladas

| Componente | Función 3GPP | Tamaño |
|---|---|---|
| `oai-amf:v1.5.1` | Access and Mobility Management Function | 280 MB |
| `oai-smf:v1.5.1` | Session Management Function | 260 MB |
| `oai-nrf:v1.5.1` | Network Repository Function | 264 MB |
| `oai-udr:v1.5.1` | Unified Data Repository | 268 MB |
| `oai-udm:v1.5.1` | Unified Data Management | 257 MB |
| `oai-ausf:v1.5.1` | Authentication Server Function | 255 MB |

> `oai-upf-vpp` **ahora compila para arm64** (2026-06-21): el único bloqueo era
> el Hyperscan (`libhyperscan-dev`, Intel-only); el **Vectorscan** (fork ARM,
> drop-in `libhs`) lo resuelve. Build mediante `docker/Dockerfile.upf-vpp.ubuntu.arm64`,
> imagen en `artifacts/oai-images/oai-upf-vpp.tar`. Ver bible §7.b. El lab en sí
> usa el UPF de Open5GS (`open5gs-upfd`) y el `oai-upf` simple_switch (core v2.2.1)
> — los 6 componentes anteriores cubren todo el Control Plane.

---

## Cómo compilar — paso a paso

### 1. Clonar el repositorio

```bash
git clone https://github.com/henriquecarmine/Core5G_ARM64.git
cd Core5G_ARM64
```

### 2. Configurar el .env

```bash
cp .env.example .env
# editar .env:
#   AWS_SERVER_HOST=core5g-arm64.duckdns.org
#   AWS_SERVER_USER=ubuntu
#   AWS_SSH_KEY_PATH=./ssl/core5g_openran_arm64.pem
```

### 3. Compilar las 6 imágenes

```bash
./build-oai-arm64.sh build
```

Cada `docker build` ejecuta un Dockerfile multi-stage:

| Stage | Qué hace |
|---|---|
| **base** | `apt-get install` de las dependencias del sistema + build tools (cmake, g++, boost…) |
| **base** | Compila desde el source: spdlog, Pistache, nlohmann/json, nghttp2 |
| **builder** | `cmake` configura + `make -j$(nproc)` genera el binario del componente |
| **target** | Copia solo el binario y los `.so` necesarios → imagen final mínima |

### 4. Exportar los .tar

```bash
./build-oai-arm64.sh save
# Cria /tmp/oai-images/oai-{amf,smf,nrf,udr,udm,ausf}.tar  (~60 MB cada)
```

### 5. Enviar al servidor

```bash
./build-oai-arm64.sh upload
# scp de cada .tar para ~/ no servidor via SSH
```

### 6. Cargar en el Docker del servidor

```bash
./build-oai-arm64.sh load
# docker load -i ~/oai-{comp}.tar && rm ~/oai-{comp}.tar
```

### O todo de una vez

```bash
./build-oai-arm64.sh all
```

### 7. Verificar la arquitectura

```bash
# no servidor:
docker run --rm oaisoftwarealliance/oai-amf:v1.5.1 uname -m
# esperado: aarch64
```

---

## Dónde quedan los archivos

**En el servidor AWS** (tras `docker load`):
```bash
docker images | grep oaisoftwarealliance
```

**En el Mac local** (`.tar` para redistribución / backup):
```
/tmp/oai-images/oai-amf.tar    (~63 MB)
/tmp/oai-images/oai-smf.tar    (~60 MB)
/tmp/oai-images/oai-nrf.tar    (~60 MB)
/tmp/oai-images/oai-udr.tar    (~61 MB)
/tmp/oai-images/oai-udm.tar    (~59 MB)
/tmp/oai-images/oai-ausf.tar   (~59 MB)
```

**Dockerfiles con parches arm64 aplicados:**
```
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/docker/Dockerfile.<comp>.ubuntu
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/build/scripts/build_helper.<comp>
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/src/*/CMakeLists.txt
```

---

## Problemas encontrados y cómo se corrigieron

Estos errores aparecen al compilar a partir del **código OAI original** sin los
parches. Los fixes ya están aplicados en este repositorio.

---

### Bug 1 — `declare -A` no funciona en el bash 3.2 de macOS

**Síntoma:** `oai: unbound variable` al ejecutar `build-oai-arm64.sh`

**Causa:** macOS 14/15 viene con bash 3.2 (restricción de licencia GPLv2). El array
asociativo `declare -A COMPONENTS=(...)` es de bash 4+.

**Fix:**
```bash
# substituído por string simples
COMPONENTS="oai-amf oai-smf oai-nrf oai-udr oai-udm oai-ausf"
for comp in $COMPONENTS; do ...
```

---

### Bug 2 — Nombre del Dockerfile sin el prefijo `oai-`

**Síntoma:** `Dockerfile não encontrado` para todos los componentes

**Causa:** Los Dockerfiles se llaman `Dockerfile.amf.ubuntu`, no
`Dockerfile.oai-amf.ubuntu`.

**Fix:**
```bash
shortname="${comp#oai-}"   # oai-amf → amf
dockerfile="$ctx/docker/Dockerfile.${shortname}.ubuntu"
```

---

### Bug 3 — `libboost1.67-dev` no disponible en el repositorio arm64 de Ubuntu 18.04

**Síntoma:** `E: Unable to locate package libboost1.67-dev` durante `--install-deps`

**Causa:** El `build_helper` para `ubuntu18.04` usa el PPA `ppa:mhier/libboost-latest`,
que no publica paquetes arm64.

**Fix:** Usar Ubuntu 20.04 (focal) como imagen base:
```bash
docker build --build-arg BASE_IMAGE=ubuntu:focal ...
```
El focal tiene Boost 1.71 en los repositorios por defecto; el `build_helper` tiene un `case`
específico para `ubuntu20.04` que instala `libboost-all-dev` sin PPA.

---

### Bug 4 — `-msse4.2` hardcoded en el `CMakeLists.txt` de todos los componentes

**Síntoma:** `cc: error: unrecognized command line option '-msse4.2'`

**Causa:** El bloque de detección de arquitectura en `src/*/CMakeLists.txt` solo trata
`armv7l` de forma explícita; cualquier otra arquitectura (incluyendo `aarch64`) cae
en el `else` y recibe la flag SSE4.2 — instrucción SIMD x86 inválida en ARM.

```cmake
# código original problemático:
else (CMAKE_SYSTEM_PROCESSOR STREQUAL "armv7l")
  set(C_FLAGS_PROCESSOR "-msse4.2")   # ← flag x86
endif()
```

**Fix** (aplicado en AMF, SMF, NRF, UDR, UDM, AUSF):
```cmake
elseif (CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|arm64")
  set(C_FLAGS_PROCESSOR "")   # ARM64 nativo, sem flags SIMD
else()
  set(C_FLAGS_PROCESSOR "-msse4.2")
endif()
```

---

### Bug 5 — `libasan2` inválido en el `build_helper.udm` silencia todo el `apt-get`

**Síntoma:** cmake falla con `None of the required 'libconfig++' found` — solo en el UDM

**Causa (en cadena):**

1. El `PACKAGE_LIST` ubuntu del `build_helper.udm` terminaba con `libasan2`
2. `libasan2` no existe en Ubuntu 20.04 arm64 (la versión correcta es `libasan5`,
   ya incluida en `specific_packages` para ubuntu20.04)
3. `apt-get install -y` con un paquete inexistente en la lista **falla por completo**
   — ningún otro paquete de la lista se instala
4. El error queda silenciado: el `ret=$?` inmediatamente después captura el
   código de salida del bloque `if/case` (siempre 0 para ubuntu20.04), no el del `apt-get`
5. `libconfig++-dev` nunca se instala → cmake no encuentra `libconfig++`

```bash
# trecho problemático em build_helper.udm (ubuntu PACKAGE_LIST):
PACKAGE_LIST="\
  $specific_packages \
  libcurl4-gnutls-dev \
  ...
  libasan2"          # ← não existe no focal arm64
```

```bash
# código que swallowa o erro:
$SUDO $INSTALLER install $OPTION $PACKAGE_LIST   # falha silenciosamente
if [[ $OS_DISTRO == "ubuntu" ]]; then
  case "$(get_distribution_release)" in
    "ubuntu18.04") ... ;;   # ubuntu20.04 não entra aqui → case retorna 0
  esac
fi
ret=$?   # ← captura 0 (do case), não o erro do apt-get
```

**Fix:** eliminar la línea `libasan2` del PACKAGE_LIST ubuntu en `build_helper.udm`.

**Archivo:** `server/.../oai-udm/build/scripts/build_helper.udm`

---

## Referencias cruzadas

- Guía completa con el contexto del proyecto: [`core5g-arm64-bible.md §7.b`](../../../../../../core5g-arm64-bible.md)
- Script de build: [`build-oai-arm64.sh`](../../../../../../build-oai-arm64.sh)
- Tutorial E2 (usa las imágenes del Core): [`TUTORIAL_LAB_E2.md`](TUTORIAL_LAB_E2.md)
