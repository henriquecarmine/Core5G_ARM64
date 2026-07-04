<!-- sync: e36a3f4e -->
> 🌐 Traduction en **français** du document canonique en portugais [`server/oai-cn-gnb-e2/docs/INSTALACAO_GNB_OAI.md`](../../../../../../server/oai-cn-gnb-e2/docs/INSTALACAO_GNB_OAI.md). Toutes les langues : [INDEX](../../../INDEX.md) · synchronisation vérifiée par `docs/i18n/check-parity.py`.

# Installation et utilisation du gNB OAI (RFSIM)

Guide détaillé pour l'installation, le build et l'exécution du **gNB OAI** et du **nrUE** en mode **RFSIM** (simulateur de RF), intégré au Core OAI du projet oai-cn-gnb-e2.

> **Vous exécutez sur arm64 (AWS Graviton2 / Apple Silicon) ?** Les images Docker du Core OAI n'existent pas pour `linux/arm64` sur DockerHub. Elles doivent être compilées manuellement. Consultez [OAI-CORE-ARM64.md](OAI-CORE-ARM64.md) pour le guide complet de build, les 5 bugs rencontrés et comment les corriger.

---

## Sommaire

1. [Vue d'ensemble](#1-visão-geral)
2. [Prérequis](#2-pré-requisitos)
3. [Installation des dépendances](#3-instalação-de-dependências)
4. [Build de openairinterface5g](#4-build-do-openairinterface5g)
5. [Configuration réseau](#5-configuração-de-rede)
6. [Exécution](#6-execução)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Vue d'ensemble

Le gNB OAI est compilé à partir du code source de **openairinterface5g**. En mode **RFSIM**, aucun matériel de RF n'est nécessaire (USRP, etc.) : le gNB et le nrUE communiquent via un loopback interne.

| Composant | Description |
|------------|-----------|
| **nr-softmodem** | Binaire du gNB |
| **nr-uesoftmodem** | Binaire du nrUE (UE simulé) |
| **gnb.conf** | Configuration du gNB (AMF, PLMN, fréquences) |
| **ue.conf** | Configuration du nrUE (IMSI, clés, etc.) |

Le build génère les binaires dans :

```
openairinterface5g/cmake_targets/ran_build/build/
├── nr-softmodem
├── nr-uesoftmodem
├── librfsimulator.so
└── ...
```

---

## 2. Prérequis

- **Système** : Ubuntu 22.04 ou 24.04 (recommandé)
- **RAM** : ~8 GB libres pour le build
- **Espace disque** : ~10 GB pour le dépôt et le build
- **Kernel** : n'importe quel kernel récent (ex. : 6.17.x)
- **Core OAI** : doit être en cours d'exécution avant de démarrer le gNB (voir [README principal](../../../../../../server/oai-cn-gnb-e2/README.md))

---

## 3. Installation des dépendances

Exécutez **une seule fois** pour installer les paquets nécessaires :

```bash
cd ric/code/oai-cn-gnb-e2/openairinterface5g/cmake_targets
./build_oai -I
```

Ou, si vous préférez utiliser Ninja (recommandé) :

```bash
./build_oai --ninja -I
```

Le script `-I` installe, entre autres :

- `libxml2`, `libxml2-dev`
- `libconfig`, `libconfig-dev`
- `libsctp`, `libsctp-dev`
- `libforms-dev`, `libforms-bin` (pour nrscope)
- Compilateur, CMake, Ninja, etc.

---

## 4. Build de openairinterface5g

### 4.1 Build pour RFSIM (gNB + nrUE)

```bash
cd ric/code/oai-cn-gnb-e2/openairinterface5g/cmake_targets
./build_oai --ninja -I                    # Se ainda não instalou dependências
./build_oai --ninja --gNB --nrUE -w SIMU -c
```

| Option | Signification |
|-------|-------------|
| `--ninja` | Utilise Ninja au lieu de Make |
| `--gNB` | Compile le gNB (nr-softmodem) |
| `--nrUE` | Compile le nrUE (nr-uesoftmodem) |
| `-w SIMU` | Mode simulateur (RFSIM) — sans matériel de RF |
| `-c` | Clean build (efface le build précédent) |

Le build peut prendre **10 à 30 minutes** selon la machine.

### 4.2 Vérifier le build

```bash
ls -la ric/code/oai-cn-gnb-e2/openairinterface5g/cmake_targets/ran_build/build/nr-softmodem
ls -la ric/code/oai-cn-gnb-e2/openairinterface5g/cmake_targets/ran_build/build/nr-uesoftmodem
```

Si les fichiers existent et sont exécutables, le build a réussi.

### 4.3 Rebuild sans nettoyer

Pour recompiler sans effacer le build précédent (plus rapide) :

```bash
./build_oai --ninja --gNB --nrUE -w SIMU
```

---

## 5. Configuration réseau

Le gNB doit communiquer avec l'AMF dans le Core OAI. Le Core utilise le réseau Docker **demo-oai-public-net** avec le sous-réseau **192.168.70.0/24** et l'interface de bridge **demo-oai**.

### 5.1 Interface demo-oai

Quand le Core est en cours d'exécution, Docker crée l'interface **demo-oai**. Le gNB utilise :

- **GNB_IPV4_ADDRESS_FOR_NG_AMF** : 192.168.70.129
- **AMF** : 192.168.70.132

L'hôte doit avoir une IP dans le même sous-réseau. Après avoir démarré le Core :

```bash
# Verificar se a interface demo-oai existe
ip link show demo-oai

# Adicionar IP ao host na rede do Core (se necessário)
sudo ip addr add 192.168.70.129/24 dev demo-oai 2>/dev/null || true
```

### 5.2 Vérifier la connectivité

```bash
ping -c 2 192.168.70.132
```

Si le Core est en cours d'exécution et l'interface configurée, le ping doit fonctionner.

---

## 6. Exécution

### 6.1 Méthode recommandée : scripts du projet

Depuis le répertoire **ric/code/oai-cn-gnb-e2** :

```bash
# 1. Iniciar o Core (se ainda não estiver rodando)
./scripts/up_core.sh

# 2. Iniciar gNB + nrUE
./scripts/up_gnb_oai.sh
```

Le script `up_gnb_oai.sh` configure automatiquement l'IP 192.168.70.129 sur l'interface demo-oai (si elle existe) et :

- Vérifie que les binaires existent
- Démarre le gNB en arrière-plan
- Attend 10 s et démarre le nrUE en arrière-plan
- Écrit les logs dans `logs/gnb_oai.log` et `logs/ue_oai.log`

Pour arrêter :

```bash
./scripts/down_gnb_oai.sh
```

### 6.2 Exécution manuelle (run_gnb.sh / run_ue.sh)

Les scripts `run_gnb.sh` et `run_ue.sh` **doivent être exécutés depuis** `openairinterface5g/scripts/`, car ils utilisent des chemins relatifs au répertoire de build.

**Erreur courante** : exécuter depuis `code/` ou un autre répertoire provoque :

```
cd: ../cmake_targets/ran_build/build: No such file or directory
sudo: ./nr-softmodem: command not found
```

**Forme correcte** :

```bash
cd ric/code/oai-cn-gnb-e2/openairinterface5g/scripts
./run_gnb.sh
```

Dans un autre terminal :

```bash
cd ric/code/oai-cn-gnb-e2/openairinterface5g/scripts
./run_ue.sh
```

### 6.3 Exécution directe (sans scripts)

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

**Cause** : le script a été exécuté depuis le mauvais répertoire.

**Solution** : exécutez depuis `openairinterface5g/scripts/` :

```bash
cd ric/code/oai-cn-gnb-e2/openairinterface5g/scripts
./run_gnb.sh
```

Ou utilisez le script du projet : `./scripts/up_gnb_oai.sh`.

---

### 7.2 `sudo: ./nr-softmodem: command not found`

**Cause** : le build n'a pas été effectué ou le répertoire de build n'existe pas.

**Solution** :

```bash
cd ric/code/oai-cn-gnb-e2/openairinterface5g/cmake_targets
./build_oai --ninja -I
./build_oai --ninja --gNB --nrUE -w SIMU -c
```

Vérifiez que les binaires existent :

```bash
ls openairinterface5g/cmake_targets/ran_build/build/nr-softmodem
```

---

### 7.3 Le gNB ne se connecte pas à l'AMF — « Cannot assign requested address »

**Symptômes** : les logs affichent `failed to bind socket: 192.168.70.129`, `SCTP could not open socket`, `No AMF is associated to the gNB`.

**Cause** : l'hôte n'a pas l'IP 192.168.70.129. Le gNB doit se lier (bind) à cette IP pour NGAP (SCTP) et GTP-U.

**Solution** :

```bash
# 1. Verificar se a interface demo-oai existe (criada quando o Core sobe)
ip link show demo-oai

# 2. Adicionar o IP
sudo ip addr add 192.168.70.129/24 dev demo-oai

# 3. Reiniciar o gNB
./scripts/down_gnb_oai.sh
./scripts/up_gnb_oai.sh
```

Le script `up_gnb_oai.sh` ajoute désormais l'IP automatiquement si l'interface existe.

---

### 7.4 L'UE ne s'enregistre pas (SGMM-REG-INITIATED)

**Cause** : l'IMSI du nrUE n'est pas enregistré dans la base de données du Core.

**Solution** : utilisez les scripts de diagnostic et de correction :

```bash
./scripts/diagnose-ue-connection.sh
./scripts/fix-ue-subscriber.sh
```

Redémarrez le Core et le gNB après correction.

---

### 7.5 Erreur de PLMN / S-NSSAI

L'AMF du Core utilise **SST=222, SD=123**. Le `gnb.conf` dans `openairinterface5g/scripts/` peut utiliser `sst=1`. Si l'UE ne s'enregistre pas, vérifiez que `plmn_list` et `snssaiList` dans le `gnb.conf` sont compatibles avec l'AMF. L'AMF sert les slices configurés dans `SST_0`, `SD_0`, etc.

---

### 7.6 Le build échoue avec une erreur de dépendance

Relancez l'installation des dépendances :

```bash
./build_oai --ninja -I
```

Pour les paquets optionnels (pcre, libssh, libxml2) :

```bash
./build_oai --install-optional-packages
```

---

## Références

- [OAI 5G NR SA Tutorial (nrUE)](../../../../../../server/oai-cn-gnb-e2/openairinterface5g/doc/NR_SA_Tutorial_OAI_nrUE.md)
- [OAI 5G RFSIM (containers)](../../../../../../server/oai-cn-gnb-e2/openairinterface5g/ci-scripts/yaml_files/5g_rfsimulator/README.md)
- [README principal de oai-cn-gnb-e2](../../../../../../server/oai-cn-gnb-e2/README.md)
