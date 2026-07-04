<!-- sync: e36a3f4e -->
> 🌐 Traduction en **français** du document canonique en portugais [`server/oai-cn-gnb-e2/docs/OAI-CORE-ARM64.md`](../../../../../../server/oai-cn-gnb-e2/docs/OAI-CORE-ARM64.md). Toutes les langues : [INDEX](../../../INDEX.md) · synchronisation vérifiée par `docs/i18n/check-parity.py`.

# OAI 5G Core — Build pour arm64 (Apple Silicon → AWS Graviton2)

Guide complet pour compiler les images Docker de l'OAI 5G Core Control Plane vers
l'architecture `linux/arm64`, les exporter au format `.tar` et les charger sur un serveur AWS
t4g (Graviton2 / aarch64).

---

## Vous ne voulez pas compiler ? Téléchargez les images prêtes à l'emploi

Les 6 images ont déjà été compilées et sont disponibles. Vous n'avez pas besoin de faire le build à partir de zéro.

### Option A — Google Drive du projet (recommandée)

Les fichiers `.tar` se trouvent dans :

```
PROJETOS/Core5G_ARM64/artifacts/oai-images/
├── oai-amf.tar    (63 MB)
├── oai-smf.tar    (60 MB)
├── oai-nrf.tar    (60 MB)
├── oai-udr.tar    (61 MB)
├── oai-udm.tar    (59 MB)
└── oai-ausf.tar   (59 MB)
```

> Les `.tar` ne sont pas versionnés dans git (ils sont trop volumineux), mais ils restent en permanence sur le Google Drive du projet.

Pour charger sur un hôte arm64 :

```bash
# copiar os .tar para o servidor e carregar
scp -i sua-chave.pem oai-amf.tar ubuntu@<servidor>:~/
ssh -i sua-chave.pem ubuntu@<servidor> "docker load -i ~/oai-amf.tar && rm ~/oai-amf.tar"

# ou carregar direto no host local
docker load -i oai-amf.tar
```

Répétez pour chaque composant (`oai-smf`, `oai-nrf`, `oai-udr`, `oai-udm`, `oai-ausf`).

### Option B — Exporter depuis le serveur de laboratoire

Les images sont déjà chargées sur le serveur AWS Graviton2 (`core5g-arm64.duckdns.org`).
Si vous avez un accès SSH au serveur, exportez-les directement depuis là :

```bash
ssh ubuntu@core5g-arm64.duckdns.org \
  "docker save oaisoftwarealliance/oai-amf:v1.5.1 | gzip" > oai-amf.tar.gz

# descompactar e carregar no seu host:
docker load -i oai-amf.tar.gz
```

Ou copier le fichier sans compression :

```bash
ssh ubuntu@core5g-arm64.duckdns.org "docker save oaisoftwarealliance/oai-amf:v1.5.1 -o ~/oai-amf.tar"
scp ubuntu@core5g-arm64.duckdns.org:~/oai-amf.tar .
docker load -i oai-amf.tar
```

### Vérifier après le chargement

```bash
docker images | grep oaisoftwarealliance
docker run --rm oaisoftwarealliance/oai-amf:v1.5.1 uname -m
# esperado: aarch64
```

---

## Pourquoi faut-il compiler ?

Les images officielles sur `hub.docker.com/u/oaisoftwarealliance` sont **exclusivement
`amd64`** — il n'existe aucune variante `linux/arm64/v8` publiée pour le tag `v1.5.1`.
Toute tentative d'exécuter ces images sur un hôte arm64 sans QEMU configuré échoue avec :

```
exec /usr/bin/python3: exec format error
```

et le conteneur se termine avec le code 255.

---

## Prérequis

| Exigence | Détail |
|---|---|
| Machine de build | Mac Apple Silicon (M1/M2/M3/M4) — arm64 natif |
| Docker Desktop | ≥ 4.x avec le moteur `linux/arm64` activé |
| Espace disque | ≥ 20 GB libres |
| Temps estimé | ~40 min par image × 6 = ~4 h au total |
| Accès SSH | clé PEM avec accès au serveur cible |
| `.env` configuré | `AWS_SERVER_HOST`, `AWS_SERVER_USER`, `AWS_SSH_KEY_PATH` |

> **Pourquoi un Mac Apple Silicon ?**
> Docker Desktop sur les puces M-series exécute les conteneurs `linux/arm64` _nativement_,
> sans émulation QEMU. Compiler l'OAI (C++ lourd avec ~200 fichiers par composant)
> via émulation prendrait 5 à 10× plus de temps et se bloque fréquemment par OOM.

---

## Images compilées

| Composant | Fonction 3GPP | Taille |
|---|---|---|
| `oai-amf:v1.5.1` | Access and Mobility Management Function | 280 MB |
| `oai-smf:v1.5.1` | Session Management Function | 260 MB |
| `oai-nrf:v1.5.1` | Network Repository Function | 264 MB |
| `oai-udr:v1.5.1` | Unified Data Repository | 268 MB |
| `oai-udm:v1.5.1` | Unified Data Management | 257 MB |
| `oai-ausf:v1.5.1` | Authentication Server Function | 255 MB |

> `oai-upf-vpp` **compile désormais pour arm64** (2026-06-21) : le seul blocage était
> Hyperscan (`libhyperscan-dev`, Intel uniquement) ; **Vectorscan** (fork ARM,
> drop-in `libhs`) résout le problème. Build via `docker/Dockerfile.upf-vpp.ubuntu.arm64`,
> image dans `artifacts/oai-images/oai-upf-vpp.tar`. Voir la bible §7.b. Le lab lui-même
> utilise l'UPF d'Open5GS (`open5gs-upfd`) et l'`oai-upf` simple_switch (core v2.2.1)
> — les 6 composants ci-dessus couvrent tout le Control Plane.

---

## Comment compiler — étape par étape

### 1. Cloner le dépôt

```bash
git clone https://github.com/henriquecarmine/Core5G_ARM64.git
cd Core5G_ARM64
```

### 2. Configurer le .env

```bash
cp .env.example .env
# editar .env:
#   AWS_SERVER_HOST=core5g-arm64.duckdns.org
#   AWS_SERVER_USER=ubuntu
#   AWS_SSH_KEY_PATH=./ssl/core5g_openran_arm64.pem
```

### 3. Compiler les 6 images

```bash
./build-oai-arm64.sh build
```

Chaque `docker build` exécute un Dockerfile multi-stage :

| Stage | Ce qu'il fait |
|---|---|
| **base** | `apt-get install` des dépendances système + outils de build (cmake, g++, boost…) |
| **base** | Compile depuis les sources : spdlog, Pistache, nlohmann/json, nghttp2 |
| **builder** | `cmake` configure + `make -j$(nproc)` génère le binaire du composant |
| **target** | Copie uniquement le binaire et les `.so` nécessaires → image finale minimale |

### 4. Exporter les .tar

```bash
./build-oai-arm64.sh save
# Cria /tmp/oai-images/oai-{amf,smf,nrf,udr,udm,ausf}.tar  (~60 MB cada)
```

### 5. Envoyer vers le serveur

```bash
./build-oai-arm64.sh upload
# scp de cada .tar para ~/ no servidor via SSH
```

### 6. Charger dans le Docker du serveur

```bash
./build-oai-arm64.sh load
# docker load -i ~/oai-{comp}.tar && rm ~/oai-{comp}.tar
```

### Ou tout en une fois

```bash
./build-oai-arm64.sh all
```

### 7. Vérifier l'architecture

```bash
# no servidor:
docker run --rm oaisoftwarealliance/oai-amf:v1.5.1 uname -m
# esperado: aarch64
```

---

## Où se trouvent les fichiers

**Sur le serveur AWS** (après `docker load`) :
```bash
docker images | grep oaisoftwarealliance
```

**Sur le Mac local** (`.tar` pour redistribution / sauvegarde) :
```
/tmp/oai-images/oai-amf.tar    (~63 MB)
/tmp/oai-images/oai-smf.tar    (~60 MB)
/tmp/oai-images/oai-nrf.tar    (~60 MB)
/tmp/oai-images/oai-udr.tar    (~61 MB)
/tmp/oai-images/oai-udm.tar    (~59 MB)
/tmp/oai-images/oai-ausf.tar   (~59 MB)
```

**Dockerfiles avec les patches arm64 appliqués :**
```
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/docker/Dockerfile.<comp>.ubuntu
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/build/scripts/build_helper.<comp>
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/src/*/CMakeLists.txt
```

---

## Problèmes rencontrés et comment ils ont été corrigés

Ces erreurs apparaissent lors de la compilation à partir du **code OAI original** sans les
patches. Les correctifs sont déjà appliqués dans ce dépôt.

---

### Bug 1 — `declare -A` ne fonctionne pas dans le bash 3.2 de macOS

**Symptôme :** `oai: unbound variable` lors de l'exécution de `build-oai-arm64.sh`

**Cause :** macOS 14/15 est livré avec bash 3.2 (restriction de licence GPLv2). Le tableau
associatif `declare -A COMPONENTS=(...)` nécessite bash 4+.

**Correctif :**
```bash
# substituído por string simples
COMPONENTS="oai-amf oai-smf oai-nrf oai-udr oai-udm oai-ausf"
for comp in $COMPONENTS; do ...
```

---

### Bug 2 — Nom du Dockerfile sans le préfixe `oai-`

**Symptôme :** `Dockerfile não encontrado` pour tous les composants

**Cause :** Les Dockerfiles s'appellent `Dockerfile.amf.ubuntu`, et non
`Dockerfile.oai-amf.ubuntu`.

**Correctif :**
```bash
shortname="${comp#oai-}"   # oai-amf → amf
dockerfile="$ctx/docker/Dockerfile.${shortname}.ubuntu"
```

---

### Bug 3 — `libboost1.67-dev` indisponible dans le dépôt arm64 d'Ubuntu 18.04

**Symptôme :** `E: Unable to locate package libboost1.67-dev` pendant `--install-deps`

**Cause :** Le `build_helper` pour `ubuntu18.04` utilise le PPA `ppa:mhier/libboost-latest`
qui ne publie pas de paquets arm64.

**Correctif :** Utiliser Ubuntu 20.04 (focal) comme image de base :
```bash
docker build --build-arg BASE_IMAGE=ubuntu:focal ...
```
focal possède Boost 1.71 dans les dépôts par défaut ; le `build_helper` a un `case`
spécifique pour `ubuntu20.04` qui installe `libboost-all-dev` sans PPA.

---

### Bug 4 — `-msse4.2` codé en dur dans le `CMakeLists.txt` de tous les composants

**Symptôme :** `cc: error: unrecognized command line option '-msse4.2'`

**Cause :** Le bloc de détection d'architecture dans `src/*/CMakeLists.txt` ne traite
explicitement que `armv7l` ; toute autre architecture (y compris `aarch64`) tombe
dans le `else` et reçoit le flag SSE4.2 — une instruction SIMD x86 invalide sur ARM.

```cmake
# código original problemático:
else (CMAKE_SYSTEM_PROCESSOR STREQUAL "armv7l")
  set(C_FLAGS_PROCESSOR "-msse4.2")   # ← flag x86
endif()
```

**Correctif** (appliqué à AMF, SMF, NRF, UDR, UDM, AUSF) :
```cmake
elseif (CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|arm64")
  set(C_FLAGS_PROCESSOR "")   # ARM64 nativo, sem flags SIMD
else()
  set(C_FLAGS_PROCESSOR "-msse4.2")
endif()
```

---

### Bug 5 — `libasan2` invalide dans `build_helper.udm` fait échouer silencieusement tout l'`apt-get`

**Symptôme :** cmake échoue avec `None of the required 'libconfig++' found` — uniquement pour l'UDM

**Cause (en cascade) :**

1. Le `PACKAGE_LIST` ubuntu de `build_helper.udm` se terminait par `libasan2`
2. `libasan2` n'existe pas dans Ubuntu 20.04 arm64 (la version correcte est `libasan5`,
   déjà incluse dans `specific_packages` pour ubuntu20.04)
3. `apt-get install -y` avec un paquet inexistant dans la liste **échoue entièrement**
   — aucun autre paquet de la liste n'est installé
4. L'erreur est masquée : le `ret=$?` juste après capture le code de sortie du
   bloc `if/case` (toujours 0 pour ubuntu20.04), et non celui de l'`apt-get`
5. `libconfig++-dev` n'est jamais installé → cmake ne trouve pas `libconfig++`

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

**Correctif :** supprimer la ligne `libasan2` du PACKAGE_LIST ubuntu dans `build_helper.udm`.

**Fichier :** `server/.../oai-udm/build/scripts/build_helper.udm`

---

## Références croisées

- Guide complet avec le contexte du projet : [`core5g-arm64-bible.md §7.b`](../../../../../../core5g-arm64-bible.md)
- Script de build : [`build-oai-arm64.sh`](../../../../../../build-oai-arm64.sh)
- Tutoriel E2 (utilise les images du Core) : [`TUTORIAL_LAB_E2.md`](TUTORIAL_LAB_E2.md)
