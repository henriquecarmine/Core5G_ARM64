<!-- sync: e36a3f4e -->
> 🌐 **English** translation of the canonical Portuguese doc [`server/oai-cn-gnb-e2/docs/INSTALACAO_GNB_OAI.md`](../../../../../../server/oai-cn-gnb-e2/docs/INSTALACAO_GNB_OAI.md). All languages: [INDEX](../../../INDEX.md) · sync checked by `docs/i18n/check-parity.py`.

# Installation and Use of the OAI gNB (RFSIM)

Detailed guide for installation, build and execution of the **OAI gNB** and **nrUE** in **RFSIM** mode (RF simulator), integrated with the OAI Core of the oai-cn-gnb-e2 project.

> **Running on arm64 (AWS Graviton2 / Apple Silicon)?** The OAI Core Docker images do not exist for `linux/arm64` on DockerHub. They must be compiled manually. See [OAI-CORE-ARM64.md](OAI-CORE-ARM64.md) for the full build guide, the 5 bugs encountered and how to fix them.

---

## Table of contents

1. [Overview](#1-visão-geral)
2. [Prerequisites](#2-pré-requisitos)
3. [Dependency installation](#3-instalação-de-dependências)
4. [Build of openairinterface5g](#4-build-do-openairinterface5g)
5. [Network configuration](#5-configuração-de-rede)
6. [Execution](#6-execução)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Overview

The OAI gNB is compiled from the **openairinterface5g** source code. In **RFSIM** mode, no RF hardware (USRP, etc.) is needed: the gNB and the nrUE communicate via internal loopback.

| Component | Description |
|------------|-----------|
| **nr-softmodem** | gNB binary |
| **nr-uesoftmodem** | nrUE binary (simulated UE) |
| **gnb.conf** | gNB configuration (AMF, PLMN, frequencies) |
| **ue.conf** | nrUE configuration (IMSI, keys, etc.) |

The build generates the binaries in:

```
openairinterface5g/cmake_targets/ran_build/build/
├── nr-softmodem
├── nr-uesoftmodem
├── librfsimulator.so
└── ...
```

---

## 2. Prerequisites

- **System**: Ubuntu 22.04 or 24.04 (recommended)
- **RAM**: ~8 GB free for the build
- **Disk space**: ~10 GB for the repository and build
- **Kernel**: Any recent kernel (e.g. 6.17.x)
- **OAI Core**: Must be running before starting the gNB (see [main README](../../../../../../server/oai-cn-gnb-e2/README.md))

---

## 3. Dependency installation

Run **once** to install the required packages:

```bash
cd ric/code/oai-cn-gnb-e2/openairinterface5g/cmake_targets
./build_oai -I
```

Or, if you prefer to use Ninja (recommended):

```bash
./build_oai --ninja -I
```

The `-I` script installs, among others:

- `libxml2`, `libxml2-dev`
- `libconfig`, `libconfig-dev`
- `libsctp`, `libsctp-dev`
- `libforms-dev`, `libforms-bin` (for nrscope)
- Compiler, CMake, Ninja, etc.

---

## 4. Build of openairinterface5g

### 4.1 Build for RFSIM (gNB + nrUE)

```bash
cd ric/code/oai-cn-gnb-e2/openairinterface5g/cmake_targets
./build_oai --ninja -I                    # Se ainda não instalou dependências
./build_oai --ninja --gNB --nrUE -w SIMU -c
```

| Option | Meaning |
|-------|-------------|
| `--ninja` | Uses Ninja instead of Make |
| `--gNB` | Compiles the gNB (nr-softmodem) |
| `--nrUE` | Compiles the nrUE (nr-uesoftmodem) |
| `-w SIMU` | Simulator mode (RFSIM) — no RF hardware |
| `-c` | Clean build (deletes the previous build) |

The build can take **10–30 minutes** depending on the machine.

### 4.2 Verify the build

```bash
ls -la ric/code/oai-cn-gnb-e2/openairinterface5g/cmake_targets/ran_build/build/nr-softmodem
ls -la ric/code/oai-cn-gnb-e2/openairinterface5g/cmake_targets/ran_build/build/nr-uesoftmodem
```

If the files exist and are executable, the build succeeded.

### 4.3 Rebuild without cleaning

To recompile without deleting the previous build (faster):

```bash
./build_oai --ninja --gNB --nrUE -w SIMU
```

---

## 5. Network configuration

The gNB needs to communicate with the AMF in the OAI Core. The Core uses the Docker network **demo-oai-public-net** with subnet **192.168.70.0/24** and bridge interface **demo-oai**.

### 5.1 The demo-oai interface

When the Core is running, Docker creates the **demo-oai** interface. The gNB uses:

- **GNB_IPV4_ADDRESS_FOR_NG_AMF**: 192.168.70.129
- **AMF**: 192.168.70.132

The host must have an IP in the same subnet. After starting the Core:

```bash
# Verificar se a interface demo-oai existe
ip link show demo-oai

# Adicionar IP ao host na rede do Core (se necessário)
sudo ip addr add 192.168.70.129/24 dev demo-oai 2>/dev/null || true
```

### 5.2 Verify connectivity

```bash
ping -c 2 192.168.70.132
```

If the Core is running and the interface configured, the ping should work.

---

## 6. Execution

### 6.1 Recommended method: project scripts

From the **ric/code/oai-cn-gnb-e2** directory:

```bash
# 1. Iniciar o Core (se ainda não estiver rodando)
./scripts/up_core.sh

# 2. Iniciar gNB + nrUE
./scripts/up_gnb_oai.sh
```

The `up_gnb_oai.sh` script automatically configures the IP 192.168.70.129 on the demo-oai interface (if it exists) and:

- Checks that the binaries exist
- Starts the gNB in the background
- Waits 10 s and starts the nrUE in the background
- Writes logs to `logs/gnb_oai.log` and `logs/ue_oai.log`

To stop:

```bash
./scripts/down_gnb_oai.sh
```

### 6.2 Manual execution (run_gnb.sh / run_ue.sh)

The `run_gnb.sh` and `run_ue.sh` scripts **must be run from** `openairinterface5g/scripts/`, because they use paths relative to the build directory.

**Common mistake**: running from `code/` or another directory causes:

```
cd: ../cmake_targets/ran_build/build: No such file or directory
sudo: ./nr-softmodem: command not found
```

**Correct way**:

```bash
cd ric/code/oai-cn-gnb-e2/openairinterface5g/scripts
./run_gnb.sh
```

In another terminal:

```bash
cd ric/code/oai-cn-gnb-e2/openairinterface5g/scripts
./run_ue.sh
```

### 6.3 Direct execution (without scripts)

```bash
cd ric/code/oai-cn-gnb-e2/openairinterface5g/cmake_targets/ran_build/build

# Terminal 1: gNB
sudo ./nr-softmodem -O ../../../scripts/gnb.conf \
    --gNBs.[0].min_rxtxtime 6 \
    --rfsim

# Terminal 2: nrUE (após o gNB estar rodando)
sudo ./nr-uesoftmodem -O ../../../scripts/ue.conf \
    --rfsim -r 106 --numerology 1 --band 78 -C 3619200000 --ssb 516
```

---

## 7. Troubleshooting

### 7.1 `cd: ../cmake_targets/ran_build/build: No such file or directory`

**Cause**: The script was run from the wrong directory.

**Solution**: Run from `openairinterface5g/scripts/`:

```bash
cd ric/code/oai-cn-gnb-e2/openairinterface5g/scripts
./run_gnb.sh
```

Or use the project script: `./scripts/up_gnb_oai.sh`.

---

### 7.2 `sudo: ./nr-softmodem: command not found`

**Cause**: The build was not done or the build directory does not exist.

**Solution**:

```bash
cd ric/code/oai-cn-gnb-e2/openairinterface5g/cmake_targets
./build_oai --ninja -I
./build_oai --ninja --gNB --nrUE -w SIMU -c
```

Check that the binaries exist:

```bash
ls openairinterface5g/cmake_targets/ran_build/build/nr-softmodem
```

---

### 7.3 gNB does not connect to the AMF — "Cannot assign requested address"

**Symptoms**: Logs show `failed to bind socket: 192.168.70.129`, `SCTP could not open socket`, `No AMF is associated to the gNB`.

**Cause**: The host does not have the IP 192.168.70.129. The gNB needs to bind to that IP for NGAP (SCTP) and GTP-U.

**Solution**:

```bash
# 1. Verificar se a interface demo-oai existe (criada quando o Core sobe)
ip link show demo-oai

# 2. Adicionar o IP
sudo ip addr add 192.168.70.129/24 dev demo-oai

# 3. Reiniciar o gNB
./scripts/down_gnb_oai.sh
./scripts/up_gnb_oai.sh
```

The `up_gnb_oai.sh` script now adds the IP automatically if the interface exists.

---

### 7.4 UE does not register (SGMM-REG-INITIATED)

**Cause**: The nrUE's IMSI is not registered in the Core database.

**Solution**: Use the diagnosis and fix scripts:

```bash
./scripts/diagnose-ue-connection.sh
./scripts/fix-ue-subscriber.sh
```

Restart the Core and gNB after fixing.

---

### 7.5 PLMN / S-NSSAI error

The Core's AMF uses **SST=222, SD=123**. The `gnb.conf` in `openairinterface5g/scripts/` may use `sst=1`. If the UE does not register, check that the `plmn_list` and `snssaiList` in `gnb.conf` are compatible with the AMF. The AMF serves the slices configured in `SST_0`, `SD_0`, etc.

---

### 7.6 Build fails with a dependency error

Run the dependency installation again:

```bash
./build_oai --ninja -I
```

For optional packages (pcre, libssh, libxml2):

```bash
./build_oai --install-optional-packages
```

---

## References

- [OAI 5G NR SA Tutorial (nrUE)](../../../../../../server/oai-cn-gnb-e2/openairinterface5g/doc/NR_SA_Tutorial_OAI_nrUE.md)
- [OAI 5G RFSIM (containers)](../../../../../../server/oai-cn-gnb-e2/openairinterface5g/ci-scripts/yaml_files/5g_rfsimulator/README.md)
- [Main README of oai-cn-gnb-e2](../../../../../../server/oai-cn-gnb-e2/README.md)
