<!-- sync: e36a3f4e -->
> 🌐 Traducción al **español** del documento canónico en portugués [`server/oai-cn-gnb-e2/docs/INSTALACAO_GNB_OAI.md`](../../../../../../server/oai-cn-gnb-e2/docs/INSTALACAO_GNB_OAI.md). Todos los idiomas: [INDEX](../../../INDEX.md) · sincronización verificada por `docs/i18n/check-parity.py`.

# Instalación y uso del gNB OAI (RFSIM)

Guía detallada para la instalación, build y ejecución del **gNB OAI** y del **nrUE** en modo **RFSIM** (simulador de RF), integrado al Core OAI del proyecto oai-cn-gnb-e2.

> **¿Ejecutando en arm64 (AWS Graviton2 / Apple Silicon)?** Las imágenes Docker del Core OAI no existen para `linux/arm64` en DockerHub. Necesitan compilarse manualmente. Consulta [OAI-CORE-ARM64.md](OAI-CORE-ARM64.md) para la guía completa de build, los 5 bugs encontrados y cómo corregirlos.

---

## Índice

1. [Visión general](#1-visão-geral)
2. [Requisitos previos](#2-pré-requisitos)
3. [Instalación de dependencias](#3-instalação-de-dependências)
4. [Build de openairinterface5g](#4-build-do-openairinterface5g)
5. [Configuración de red](#5-configuração-de-rede)
6. [Ejecución](#6-execução)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Visión general

El gNB OAI se compila a partir del código fuente de **openairinterface5g**. En modo **RFSIM**, no es necesario hardware de RF (USRP, etc.): el gNB y el nrUE se comunican vía loopback interno.

| Componente | Descripción |
|------------|-----------|
| **nr-softmodem** | Binario del gNB |
| **nr-uesoftmodem** | Binario del nrUE (UE simulado) |
| **gnb.conf** | Configuración del gNB (AMF, PLMN, frecuencias) |
| **ue.conf** | Configuración del nrUE (IMSI, claves, etc.) |

El build genera los binarios en:

```
openairinterface5g/cmake_targets/ran_build/build/
├── nr-softmodem
├── nr-uesoftmodem
├── librfsimulator.so
└── ...
```

---

## 2. Requisitos previos

- **Sistema**: Ubuntu 22.04 o 24.04 (recomendado)
- **RAM**: ~8 GB libres para el build
- **Espacio en disco**: ~10 GB para el repositorio y el build
- **Kernel**: Cualquier kernel reciente (ej.: 6.17.x)
- **Core OAI**: Debe estar en ejecución antes de iniciar el gNB (ver [README principal](../../../../../../server/oai-cn-gnb-e2/README.md))

---

## 3. Instalación de dependencias

Ejecuta **una vez** para instalar los paquetes necesarios:

```bash
cd ric/code/oai-cn-gnb-e2/openairinterface5g/cmake_targets
./build_oai -I
```

O, si prefieres usar Ninja (recomendado):

```bash
./build_oai --ninja -I
```

El script `-I` instala, entre otros:

- `libxml2`, `libxml2-dev`
- `libconfig`, `libconfig-dev`
- `libsctp`, `libsctp-dev`
- `libforms-dev`, `libforms-bin` (para nrscope)
- Compilador, CMake, Ninja, etc.

---

## 4. Build de openairinterface5g

### 4.1 Build para RFSIM (gNB + nrUE)

```bash
cd ric/code/oai-cn-gnb-e2/openairinterface5g/cmake_targets
./build_oai --ninja -I                    # Se ainda não instalou dependências
./build_oai --ninja --gNB --nrUE -w SIMU -c
```

| Opción | Significado |
|-------|-------------|
| `--ninja` | Usa Ninja en vez de Make |
| `--gNB` | Compila el gNB (nr-softmodem) |
| `--nrUE` | Compila el nrUE (nr-uesoftmodem) |
| `-w SIMU` | Modo simulador (RFSIM) — sin hardware de RF |
| `-c` | Clean build (borra el build anterior) |

El build puede tardar **entre 10 y 30 minutos** según la máquina.

### 4.2 Verificar el build

```bash
ls -la ric/code/oai-cn-gnb-e2/openairinterface5g/cmake_targets/ran_build/build/nr-softmodem
ls -la ric/code/oai-cn-gnb-e2/openairinterface5g/cmake_targets/ran_build/build/nr-uesoftmodem
```

Si los archivos existen y son ejecutables, el build fue exitoso.

### 4.3 Rebuild sin limpiar

Para recompilar sin borrar el build anterior (más rápido):

```bash
./build_oai --ninja --gNB --nrUE -w SIMU
```

---

## 5. Configuración de red

El gNB necesita comunicarse con el AMF en el Core OAI. El Core usa la red Docker **demo-oai-public-net** con subnet **192.168.70.0/24** e interfaz de bridge **demo-oai**.

### 5.1 Interfaz demo-oai

Cuando el Core está en ejecución, Docker crea la interfaz **demo-oai**. El gNB usa:

- **GNB_IPV4_ADDRESS_FOR_NG_AMF**: 192.168.70.129
- **AMF**: 192.168.70.132

El host necesita tener una IP en la misma subnet. Tras iniciar el Core:

```bash
# Verificar se a interface demo-oai existe
ip link show demo-oai

# Adicionar IP ao host na rede do Core (se necessário)
sudo ip addr add 192.168.70.129/24 dev demo-oai 2>/dev/null || true
```

### 5.2 Verificar conectividad

```bash
ping -c 2 192.168.70.132
```

Si el Core está en ejecución y la interfaz configurada, el ping debe funcionar.

---

## 6. Ejecución

### 6.1 Método recomendado: scripts del proyecto

Desde el directorio **ric/code/oai-cn-gnb-e2**:

```bash
# 1. Iniciar o Core (se ainda não estiver rodando)
./scripts/up_core.sh

# 2. Iniciar gNB + nrUE
./scripts/up_gnb_oai.sh
```

El script `up_gnb_oai.sh` configura automáticamente la IP 192.168.70.129 en la interfaz demo-oai (si existe) y:

- Verifica que los binarios existan
- Inicia el gNB en background
- Espera 10 s e inicia el nrUE en background
- Guarda logs en `logs/gnb_oai.log` y `logs/ue_oai.log`

Para detener:

```bash
./scripts/down_gnb_oai.sh
```

### 6.2 Ejecución manual (run_gnb.sh / run_ue.sh)

Los scripts `run_gnb.sh` y `run_ue.sh` **deben ejecutarse desde** `openairinterface5g/scripts/`, ya que usan rutas relativas al directorio de build.

**Error común**: ejecutarlos desde `code/` u otro directorio causa:

```
cd: ../cmake_targets/ran_build/build: No such file or directory
sudo: ./nr-softmodem: command not found
```

**Forma correcta**:

```bash
cd ric/code/oai-cn-gnb-e2/openairinterface5g/scripts
./run_gnb.sh
```

En otra terminal:

```bash
cd ric/code/oai-cn-gnb-e2/openairinterface5g/scripts
./run_ue.sh
```

### 6.3 Ejecución directa (sin scripts)

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

**Causa**: El script se ejecutó desde el directorio equivocado.

**Solución**: Ejecútalo desde `openairinterface5g/scripts/`:

```bash
cd ric/code/oai-cn-gnb-e2/openairinterface5g/scripts
./run_gnb.sh
```

O usa el script del proyecto: `./scripts/up_gnb_oai.sh`.

---

### 7.2 `sudo: ./nr-softmodem: command not found`

**Causa**: El build no se hizo o el directorio de build no existe.

**Solución**:

```bash
cd ric/code/oai-cn-gnb-e2/openairinterface5g/cmake_targets
./build_oai --ninja -I
./build_oai --ninja --gNB --nrUE -w SIMU -c
```

Verifica que los binarios existan:

```bash
ls openairinterface5g/cmake_targets/ran_build/build/nr-softmodem
```

---

### 7.3 El gNB no conecta con el AMF — "Cannot assign requested address"

**Síntomas**: Los logs muestran `failed to bind socket: 192.168.70.129`, `SCTP could not open socket`, `No AMF is associated to the gNB`.

**Causa**: El host no tiene la IP 192.168.70.129. El gNB necesita hacer bind en esa IP para NGAP (SCTP) y GTP-U.

**Solución**:

```bash
# 1. Verificar se a interface demo-oai existe (criada quando o Core sobe)
ip link show demo-oai

# 2. Adicionar o IP
sudo ip addr add 192.168.70.129/24 dev demo-oai

# 3. Reiniciar o gNB
./scripts/down_gnb_oai.sh
./scripts/up_gnb_oai.sh
```

El script `up_gnb_oai.sh` ahora agrega la IP automáticamente si la interfaz existe.

---

### 7.4 El UE no registra (SGMM-REG-INITIATED)

**Causa**: El IMSI del nrUE no está registrado en la base de datos del Core.

**Solución**: Usa los scripts de diagnóstico y corrección:

```bash
./scripts/diagnose-ue-connection.sh
./scripts/fix-ue-subscriber.sh
```

Reinicia el Core y el gNB tras corregir.

---

### 7.5 Error de PLMN / S-NSSAI

El AMF del Core usa **SST=222, SD=123**. El `gnb.conf` en `openairinterface5g/scripts/` puede usar `sst=1`. Si el UE no registra, verifica que `plmn_list` y `snssaiList` en el `gnb.conf` sean compatibles con el AMF. El AMF sirve los slices configurados en `SST_0`, `SD_0`, etc.

---

### 7.6 El build falla con error de dependencia

Ejecuta de nuevo la instalación de dependencias:

```bash
./build_oai --ninja -I
```

Para paquetes opcionales (pcre, libssh, libxml2):

```bash
./build_oai --install-optional-packages
```

---

## Referencias

- [OAI 5G NR SA Tutorial (nrUE)](../../../../../../server/oai-cn-gnb-e2/openairinterface5g/doc/NR_SA_Tutorial_OAI_nrUE.md)
- [OAI 5G RFSIM (containers)](../../../../../../server/oai-cn-gnb-e2/openairinterface5g/ci-scripts/yaml_files/5g_rfsimulator/README.md)
- [README principal de oai-cn-gnb-e2](../../../../../../server/oai-cn-gnb-e2/README.md)
