<!-- sync: e36a3f4e -->
> 🌐 **English** translation of the canonical Portuguese doc [`server/oai-cn-gnb-e2/docs/OAI-CORE-ARM64.md`](../../../../../../server/oai-cn-gnb-e2/docs/OAI-CORE-ARM64.md). All languages: [INDEX](../../../INDEX.md) · sync checked by `docs/i18n/check-parity.py`.

# OAI 5G Core — Build for arm64 (Apple Silicon → AWS Graviton2)

Complete guide to compile the Docker images of the OAI 5G Core Control Plane for
the `linux/arm64` architecture, export them as `.tar` and load them onto an AWS
t4g server (Graviton2 / aarch64).

---

## Don't want to compile? Download the ready-made images

The 6 images have already been compiled and are available. You don't need to build from scratch.

### Option A — Project Google Drive (recommended)

The `.tar` files are at:

```
PROJETOS/Core5G_ARM64/artifacts/oai-images/
├── oai-amf.tar    (63 MB)
├── oai-smf.tar    (60 MB)
├── oai-nrf.tar    (60 MB)
├── oai-udr.tar    (61 MB)
├── oai-udm.tar    (59 MB)
└── oai-ausf.tar   (59 MB)
```

> The `.tar` files are not versioned in git (they are too large), but they live permanently in the project's Google Drive.

To load onto an arm64 host:

```bash
# copiar os .tar para o servidor e carregar
scp -i sua-chave.pem oai-amf.tar ubuntu@<servidor>:~/
ssh -i sua-chave.pem ubuntu@<servidor> "docker load -i ~/oai-amf.tar && rm ~/oai-amf.tar"

# ou carregar direto no host local
docker load -i oai-amf.tar
```

Repeat for each component (`oai-smf`, `oai-nrf`, `oai-udr`, `oai-udm`, `oai-ausf`).

### Option B — Export from the lab server

The images are already loaded on the AWS Graviton2 server (`core5g-arm64.duckdns.org`).
If you have SSH access to the server, export directly from there:

```bash
ssh ubuntu@core5g-arm64.duckdns.org \
  "docker save oaisoftwarealliance/oai-amf:v1.5.1 | gzip" > oai-amf.tar.gz

# descompactar e carregar no seu host:
docker load -i oai-amf.tar.gz
```

Or copy the file without compression:

```bash
ssh ubuntu@core5g-arm64.duckdns.org "docker save oaisoftwarealliance/oai-amf:v1.5.1 -o ~/oai-amf.tar"
scp ubuntu@core5g-arm64.duckdns.org:~/oai-amf.tar .
docker load -i oai-amf.tar
```

### Verify after loading

```bash
docker images | grep oaisoftwarealliance
docker run --rm oaisoftwarealliance/oai-amf:v1.5.1 uname -m
# esperado: aarch64
```

---

## Why is compiling necessary?

The official images at `hub.docker.com/u/oaisoftwarealliance` are **exclusively
`amd64`** — there is no `linux/arm64/v8` variant published for the `v1.5.1` tag.
Any attempt to run these images on an arm64 host without QEMU configured fails with:

```
exec /usr/bin/python3: exec format error
```

and the container exits with code 255.

---

## Prerequisites

| Requirement | Detail |
|---|---|
| Build machine | Mac Apple Silicon (M1/M2/M3/M4) — native arm64 |
| Docker Desktop | ≥ 4.x with the `linux/arm64` engine enabled |
| Disk space | ≥ 20 GB free |
| Estimated time | ~40 min per image × 6 = ~4 h total |
| SSH access | PEM key with access to the target server |
| `.env` configured | `AWS_SERVER_HOST`, `AWS_SERVER_USER`, `AWS_SSH_KEY_PATH` |

> **Why Mac Apple Silicon?**
> Docker Desktop on M-series runs `linux/arm64` containers _natively_,
> without QEMU emulation. Compiling OAI (heavy C++ with ~200 files per component)
> via emulation would take 5–10× longer and frequently hangs due to OOM.

---

## Compiled images

| Component | 3GPP function | Size |
|---|---|---|
| `oai-amf:v1.5.1` | Access and Mobility Management Function | 280 MB |
| `oai-smf:v1.5.1` | Session Management Function | 260 MB |
| `oai-nrf:v1.5.1` | Network Repository Function | 264 MB |
| `oai-udr:v1.5.1` | Unified Data Repository | 268 MB |
| `oai-udm:v1.5.1` | Unified Data Management | 257 MB |
| `oai-ausf:v1.5.1` | Authentication Server Function | 255 MB |

> `oai-upf-vpp` **now compiles for arm64** (2026-06-21): the only blocker was
> Hyperscan (`libhyperscan-dev`, Intel-only); **Vectorscan** (ARM fork,
> drop-in `libhs`) solves it. Build via `docker/Dockerfile.upf-vpp.ubuntu.arm64`,
> image at `artifacts/oai-images/oai-upf-vpp.tar`. See bible §7.b. The lab itself
> uses the Open5GS UPF (`open5gs-upfd`) and the `oai-upf` simple_switch (core v2.2.1)
> — the 6 components above cover the entire Control Plane.

---

## How to compile — step by step

### 1. Clone the repository

```bash
git clone https://github.com/henriquecarmine/Core5G_ARM64.git
cd Core5G_ARM64
```

### 2. Configure the .env

```bash
cp .env.example .env
# editar .env:
#   AWS_SERVER_HOST=core5g-arm64.duckdns.org
#   AWS_SERVER_USER=ubuntu
#   AWS_SSH_KEY_PATH=./ssl/core5g_openran_arm64.pem
```

### 3. Compile the 6 images

```bash
./build-oai-arm64.sh build
```

Each `docker build` runs a multi-stage Dockerfile:

| Stage | What it does |
|---|---|
| **base** | `apt-get install` of the system dependencies + build tools (cmake, g++, boost…) |
| **base** | Compiles from source: spdlog, Pistache, nlohmann/json, nghttp2 |
| **builder** | `cmake` configures + `make -j$(nproc)` generates the component binary |
| **target** | Copies only the required binary and `.so` files → minimal final image |

### 4. Export the .tar files

```bash
./build-oai-arm64.sh save
# Cria /tmp/oai-images/oai-{amf,smf,nrf,udr,udm,ausf}.tar  (~60 MB cada)
```

### 5. Send to the server

```bash
./build-oai-arm64.sh upload
# scp de cada .tar para ~/ no servidor via SSH
```

### 6. Load into the server's Docker

```bash
./build-oai-arm64.sh load
# docker load -i ~/oai-{comp}.tar && rm ~/oai-{comp}.tar
```

### Or all at once

```bash
./build-oai-arm64.sh all
```

### 7. Verify the architecture

```bash
# no servidor:
docker run --rm oaisoftwarealliance/oai-amf:v1.5.1 uname -m
# esperado: aarch64
```

---

## Where the files live

**On the AWS server** (after `docker load`):
```bash
docker images | grep oaisoftwarealliance
```

**On the local Mac** (`.tar` for redistribution / backup):
```
/tmp/oai-images/oai-amf.tar    (~63 MB)
/tmp/oai-images/oai-smf.tar    (~60 MB)
/tmp/oai-images/oai-nrf.tar    (~60 MB)
/tmp/oai-images/oai-udr.tar    (~61 MB)
/tmp/oai-images/oai-udm.tar    (~59 MB)
/tmp/oai-images/oai-ausf.tar   (~59 MB)
```

**Dockerfiles with arm64 patches applied:**
```
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/docker/Dockerfile.<comp>.ubuntu
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/build/scripts/build_helper.<comp>
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/src/*/CMakeLists.txt
```

---

## Problems encountered and how they were fixed

These errors appear when compiling from the **original OAI code** without the
patches. The fixes are already applied in this repository.

---

### Bug 1 — `declare -A` does not work in macOS bash 3.2

**Symptom:** `oai: unbound variable` when running `build-oai-arm64.sh`

**Cause:** macOS 14/15 ships with bash 3.2 (GPLv2 license restriction). The
associative array `declare -A COMPONENTS=(...)` is bash 4+.

**Fix:**
```bash
# substituído por string simples
COMPONENTS="oai-amf oai-smf oai-nrf oai-udr oai-udm oai-ausf"
for comp in $COMPONENTS; do ...
```

---

### Bug 2 — Dockerfile name without the `oai-` prefix

**Symptom:** `Dockerfile não encontrado` for all components

**Cause:** The Dockerfiles are named `Dockerfile.amf.ubuntu`, not
`Dockerfile.oai-amf.ubuntu`.

**Fix:**
```bash
shortname="${comp#oai-}"   # oai-amf → amf
dockerfile="$ctx/docker/Dockerfile.${shortname}.ubuntu"
```

---

### Bug 3 — `libboost1.67-dev` unavailable in the Ubuntu 18.04 arm64 repository

**Symptom:** `E: Unable to locate package libboost1.67-dev` during `--install-deps`

**Cause:** The `build_helper` for `ubuntu18.04` uses the PPA `ppa:mhier/libboost-latest`,
which does not publish arm64 packages.

**Fix:** Use Ubuntu 20.04 (focal) as the base image:
```bash
docker build --build-arg BASE_IMAGE=ubuntu:focal ...
```
focal has Boost 1.71 in the standard repositories; the `build_helper` has a specific
`case` for `ubuntu20.04` that installs `libboost-all-dev` without a PPA.

---

### Bug 4 — `-msse4.2` hardcoded in every component's `CMakeLists.txt`

**Symptom:** `cc: error: unrecognized command line option '-msse4.2'`

**Cause:** The architecture-detection block in `src/*/CMakeLists.txt` only handles
`armv7l` explicitly; any other architecture (including `aarch64`) falls into
the `else` and gets the SSE4.2 flag — an x86 SIMD instruction invalid on ARM.

```cmake
# código original problemático:
else (CMAKE_SYSTEM_PROCESSOR STREQUAL "armv7l")
  set(C_FLAGS_PROCESSOR "-msse4.2")   # ← flag x86
endif()
```

**Fix** (applied to AMF, SMF, NRF, UDR, UDM, AUSF):
```cmake
elseif (CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|arm64")
  set(C_FLAGS_PROCESSOR "")   # ARM64 nativo, sem flags SIMD
else()
  set(C_FLAGS_PROCESSOR "-msse4.2")
endif()
```

---

### Bug 5 — invalid `libasan2` in `build_helper.udm` silences the entire `apt-get`

**Symptom:** cmake fails with `None of the required 'libconfig++' found` — only in the UDM

**Cause (chained):**

1. The ubuntu `PACKAGE_LIST` in `build_helper.udm` ended with `libasan2`
2. `libasan2` does not exist on Ubuntu 20.04 arm64 (the correct version is `libasan5`,
   already included in `specific_packages` for ubuntu20.04)
3. `apt-get install -y` with a nonexistent package in the list **fails entirely**
   — no other package in the list is installed
4. The error is silenced: the `ret=$?` right after captures the exit code of the
   `if/case` block (always 0 for ubuntu20.04), not of `apt-get`
5. `libconfig++-dev` is never installed → cmake cannot find `libconfig++`

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

**Fix:** remove the `libasan2` line from the ubuntu PACKAGE_LIST in `build_helper.udm`.

**File:** `server/.../oai-udm/build/scripts/build_helper.udm`

---

## Cross-references

- Full guide with project context: [`core5g-arm64-bible.md §7.b`](../../../../../../core5g-arm64-bible.md)
- Build script: [`build-oai-arm64.sh`](../../../../../../build-oai-arm64.sh)
- E2 tutorial (uses the Core images): [`TUTORIAL_LAB_E2.md`](TUTORIAL_LAB_E2.md)
