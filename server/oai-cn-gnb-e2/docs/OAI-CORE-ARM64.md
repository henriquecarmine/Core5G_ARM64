# OAI 5G Core — Build para arm64 (Apple Silicon → AWS Graviton2)

Guia completo para compilar as imagens Docker do OAI 5G Core Control Plane para
a arquitetura `linux/arm64`, exportar como `.tar` e carregar num servidor AWS
t4g (Graviton2 / aarch64).

---

## Por que é necessário compilar?

As imagens oficiais em `hub.docker.com/u/oaisoftwarealliance` são **exclusivamente
`amd64`** — não há variante `linux/arm64/v8` publicada para a tag `v1.5.1`.
Qualquer tentativa de rodar essas imagens num host arm64 sem QEMU configurado falha com:

```
exec /usr/bin/python3: exec format error
```

e o container sai com código 255.

---

## Pré-requisitos

| Requisito | Detalhe |
|---|---|
| Máquina de build | Mac Apple Silicon (M1/M2/M3/M4) — arm64 nativo |
| Docker Desktop | ≥ 4.x com engine `linux/arm64` habilitada |
| Espaço em disco | ≥ 20 GB livres |
| Tempo estimado | ~40 min por imagem × 6 = ~4 h no total |
| Acesso SSH | chave PEM com acesso ao servidor destino |
| `.env` configurado | `AWS_SERVER_HOST`, `AWS_SERVER_USER`, `AWS_SSH_KEY_PATH` |

> **Por que Mac Apple Silicon?**
> O Docker Desktop no M-series executa containers `linux/arm64` _nativamente_,
> sem emulação QEMU. Compilar o OAI (C++ pesado com ~200 arquivos por componente)
> via emulação levaria 5–10× mais tempo e frequentemente trava por OOM.

---

## Imagens compiladas

| Componente | Função 3GPP | Tamanho |
|---|---|---|
| `oai-amf:v1.5.1` | Access and Mobility Management Function | 280 MB |
| `oai-smf:v1.5.1` | Session Management Function | 260 MB |
| `oai-nrf:v1.5.1` | Network Repository Function | 264 MB |
| `oai-udr:v1.5.1` | Unified Data Repository | 268 MB |
| `oai-udm:v1.5.1` | Unified Data Management | 257 MB |
| `oai-ausf:v1.5.1` | Authentication Server Function | 255 MB |

> `oai-upf-vpp` **não é compilável para arm64**: depende de `libhyperscan-dev`
> (biblioteca de regex SIMD da Intel, inexistente no Ubuntu arm64) e de
> caminhos `/usr/lib/x86_64-linux-gnu/` hardcoded no Dockerfile final.
> O lab usa o UPF do Open5GS (`open5gs-upfd`) — os 6 componentes acima cobrem
> todo o Control Plane.

---

## Como compilar — passo a passo

### 1. Clonar o repositório

```bash
git clone https://github.com/henriquecarmine/Core5G_ARM64.git
cd Core5G_ARM64
```

### 2. Configurar o .env

```bash
cp .env.example .env
# editar .env:
#   AWS_SERVER_HOST=core5g-arm64.duckdns.org
#   AWS_SERVER_USER=ubuntu
#   AWS_SSH_KEY_PATH=./ssl/core5g_openran_arm64.pem
```

### 3. Compilar as 6 imagens

```bash
./build-oai-arm64.sh build
```

Cada `docker build` executa um Dockerfile multi-stage:

| Stage | O que faz |
|---|---|
| **base** | `apt-get install` das dependências de sistema + build tools (cmake, g++, boost…) |
| **base** | Compila do source: spdlog, Pistache, nlohmann/json, nghttp2 |
| **builder** | `cmake` configura + `make -j$(nproc)` gera o binário do componente |
| **target** | Copia apenas o binário e `.so` necessários → imagem final mínima |

### 4. Exportar os .tar

```bash
./build-oai-arm64.sh save
# Cria /tmp/oai-images/oai-{amf,smf,nrf,udr,udm,ausf}.tar  (~60 MB cada)
```

### 5. Enviar para o servidor

```bash
./build-oai-arm64.sh upload
# scp de cada .tar para ~/ no servidor via SSH
```

### 6. Carregar no Docker do servidor

```bash
./build-oai-arm64.sh load
# docker load -i ~/oai-{comp}.tar && rm ~/oai-{comp}.tar
```

### Ou tudo de uma vez

```bash
./build-oai-arm64.sh all
```

### 7. Verificar arquitetura

```bash
# no servidor:
docker run --rm oaisoftwarealliance/oai-amf:v1.5.1 uname -m
# esperado: aarch64
```

---

## Onde ficam os arquivos

**No servidor AWS** (após `docker load`):
```bash
docker images | grep oaisoftwarealliance
```

**No Mac local** (`.tar` para redistribuição / backup):
```
/tmp/oai-images/oai-amf.tar    (~63 MB)
/tmp/oai-images/oai-smf.tar    (~60 MB)
/tmp/oai-images/oai-nrf.tar    (~60 MB)
/tmp/oai-images/oai-udr.tar    (~61 MB)
/tmp/oai-images/oai-udm.tar    (~59 MB)
/tmp/oai-images/oai-ausf.tar   (~59 MB)
```

**Dockerfiles com patches arm64 aplicados:**
```
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/docker/Dockerfile.<comp>.ubuntu
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/build/scripts/build_helper.<comp>
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/src/*/CMakeLists.txt
```

---

## Problemas encontrados e como foram corrigidos

Estes erros aparecem ao compilar a partir do **código OAI original** sem os
patches. Os fixes já estão aplicados neste repositório.

---

### Bug 1 — `declare -A` não funciona no bash 3.2 do macOS

**Sintoma:** `oai: unbound variable` ao rodar `build-oai-arm64.sh`

**Causa:** macOS 14/15 vem com bash 3.2 (restrição de licença GPLv2). O array
associativo `declare -A COMPONENTS=(...)` é bash 4+.

**Fix:**
```bash
# substituído por string simples
COMPONENTS="oai-amf oai-smf oai-nrf oai-udr oai-udm oai-ausf"
for comp in $COMPONENTS; do ...
```

---

### Bug 2 — Nome do Dockerfile sem o prefixo `oai-`

**Sintoma:** `Dockerfile não encontrado` para todos os componentes

**Causa:** Os Dockerfiles se chamam `Dockerfile.amf.ubuntu`, não
`Dockerfile.oai-amf.ubuntu`.

**Fix:**
```bash
shortname="${comp#oai-}"   # oai-amf → amf
dockerfile="$ctx/docker/Dockerfile.${shortname}.ubuntu"
```

---

### Bug 3 — `libboost1.67-dev` indisponível no repositório arm64 do Ubuntu 18.04

**Sintoma:** `E: Unable to locate package libboost1.67-dev` durante `--install-deps`

**Causa:** O `build_helper` para `ubuntu18.04` usa o PPA `ppa:mhier/libboost-latest`
que não publica pacotes arm64.

**Fix:** Usar Ubuntu 20.04 (focal) como imagem base:
```bash
docker build --build-arg BASE_IMAGE=ubuntu:focal ...
```
O focal tem Boost 1.71 nos repositórios padrão; o `build_helper` tem um `case`
específico para `ubuntu20.04` que instala `libboost-all-dev` sem PPA.

---

### Bug 4 — `-msse4.2` hardcoded no `CMakeLists.txt` de todos os componentes

**Sintoma:** `cc: error: unrecognized command line option '-msse4.2'`

**Causa:** O bloco de detecção de arquitetura em `src/*/CMakeLists.txt` só trata
`armv7l` explicitamente; qualquer outra arquitetura (incluindo `aarch64`) cai
no `else` e recebe a flag SSE4.2 — instrução SIMD x86 inválida em ARM.

```cmake
# código original problemático:
else (CMAKE_SYSTEM_PROCESSOR STREQUAL "armv7l")
  set(C_FLAGS_PROCESSOR "-msse4.2")   # ← flag x86
endif()
```

**Fix** (aplicado em AMF, SMF, NRF, UDR, UDM, AUSF):
```cmake
elseif (CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|arm64")
  set(C_FLAGS_PROCESSOR "")   # ARM64 nativo, sem flags SIMD
else()
  set(C_FLAGS_PROCESSOR "-msse4.2")
endif()
```

---

### Bug 5 — `libasan2` inválido no `build_helper.udm` silencia o `apt-get` inteiro

**Sintoma:** cmake falha com `None of the required 'libconfig++' found` — apenas no UDM

**Causa (em cadeia):**

1. O `PACKAGE_LIST` ubuntu do `build_helper.udm` terminava com `libasan2`
2. `libasan2` não existe no Ubuntu 20.04 arm64 (a versão correta é `libasan5`,
   já incluída em `specific_packages` para ubuntu20.04)
3. `apt-get install -y` com um pacote inexistente na lista **falha inteiro**
   — nenhum outro pacote da lista é instalado
4. O erro é silenciado: o `ret=$?` logo após captura o código de saída do
   bloco `if/case` (sempre 0 para ubuntu20.04), não do `apt-get`
5. `libconfig++-dev` nunca é instalado → cmake não encontra `libconfig++`

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

**Fix:** remover a linha `libasan2` do PACKAGE_LIST ubuntu em `build_helper.udm`.

**Arquivo:** `server/.../oai-udm/build/scripts/build_helper.udm`

---

## Referências cruzadas

- Guia completo com contexto do projeto: [`core5g-arm64-bible.md §7.b`](../../../core5g-arm64-bible.md)
- Script de build: [`build-oai-arm64.sh`](../../../build-oai-arm64.sh)
- Tutorial E2 (usa as imagens do Core): [`TUTORIAL_LAB_E2.md`](TUTORIAL_LAB_E2.md)
