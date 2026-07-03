<!-- sync: e8f9da69 -->
> 🌐 Traduction en **français** du document canonique en portugais [`server/oai-cn-gnb-e2/docs/TUTORIAL_LAB_E2.md`](../../../../../../server/oai-cn-gnb-e2/docs/TUTORIAL_LAB_E2.md). Toutes les langues : [INDEX](../../../INDEX.md) · synchronisation vérifiée par `docs/i18n/check-parity.py`.

# Tutoriel — Laboratoire OAI + Interface E2 (FlexRIC)

Guide pas à pas pour reproduire le laboratoire **5G SA natif** (Core Docker + gNB/nrUE RFSIM + nearRT-RIC + xApps) avec des tests de **Service Models E2** (custom, RC, KPM).

> **Périmètre :** ce lab s'exécute sur l'**hôte** (Docker uniquement pour le Core). Il **n'**utilise **pas** Kind multicluster ni l'intégration avec SD-RAN/Aether.

> **Images du Core en arm64 :** les images `oaisoftwarealliance/*:v1.5.1` n'existent pas sur DockerHub pour `linux/arm64`. Elles ont été compilées nativement dans ce projet. Consultez le guide complet dans [OAI-CORE-ARM64.md](../../../../../../server/oai-cn-gnb-e2/docs/OAI-CORE-ARM64.md) avant de tenter de démarrer le Core sur un hôte Graviton2/Apple Silicon.

---

## 1. Résultats obtenus (résumé)

| Procédure | État | Preuve |
|--------------|--------|-----------|
| Core OAI (UPF-VPP, scénario 1) | ✅ OK | Conteneurs `oai-amf`, `oai-smf`, `oai-upf`, … |
| Build gNB + nrUE avec agent E2 | ✅ OK | `nr-softmodem` avec `--build-e2`, branche FlexRIC `dev` |
| Build nearRT-RIC + xApps (sous-module) | ✅ OK | `build_flexric_tools.sh` |
| Attachement UE (IMSI 208950000000032, slice 222/123) | ✅ OK | `RRCSetupComplete`, session PDU |
| E2 SETUP (gNB ↔ nearRT-RIC) | ✅ OK | `[E2-AGENT]: E2 SETUP RESPONSE rx` |
| Custom SMs (MAC/RLC/PDCP/GTP, IDs 142–148) | ✅ OK | `xapp_cust_moni`, nœud E2 enregistré |
| **E2SM-RC** v1.03 | ✅ OK | INDICATION avec `RRCSetupComplete` décodé (ASN.1) |
| **E2SM-KPM** v2.03 (slice 222/123) | ✅ OK | INDICATION périodiques avec `DRB.UEThp*`, `RRU.PrbTot*` |
| PoC KPM+RC (`xapp_kpm_rc`) | ⚠️ Non validé de bout en bout | Binaire compilé ; à utiliser après KPM/RC isolés |
| SLICE / TC (émulateurs FlexRIC) | ❌ N/A | Non pris en charge par l'agent E2 du gNB OAI monolithique |

**Versions alignées :** E2AP v2 (`E2AP_V2`) + E2SM-KPM v2.03 (`KPM_V2_03`), branche FlexRIC **`dev`**.

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  Core OAI (Docker) — oai-cn5g-fed/docker-compose                    │
│  AMF · SMF · NRF · UPF-VPP · UDM · UDR · AUSF · MySQL · DN          │
│  Rede: demo-oai (192.168.70.0/24)  ·  Slice lab: SST=222, SD=123    │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ NGAP / GTP-U
┌───────────────────────────────▼─────────────────────────────────────┐
│  RAN nativo (host) — openairinterface5g                             │
│  nr-softmodem (gNB + E2 agent)  ←RFSIM→  nr-uesoftmodem             │
│  IP host na demo-oai: 192.168.70.129                                │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ E2AP SCTP :36421
┌───────────────────────────────▼─────────────────────────────────────┐
│  nearRT-RIC + xApps (host) — FlexRIC submodule dev                  │
│  nearRT-RIC :36421  ·  iApp (E42) :36422                            │
│  xApps: xapp_kpm_moni, xapp_rc_moni, xapp_cust_moni, …              │
│  SMs: flexric-lib/ (submodule dev — **não** usar /usr/local)        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Pré-requis

- Ubuntu 22.04+ avec Docker, Python 3, sudo
- ~8 GB de RAM libre, ~15 GB de disque (Core + build OAI + FlexRIC)
- Transfert IPv4 (forwarding) : `sudo sysctl -w net.ipv4.ip_forward=1`
- Compte Docker Hub (pull des images OAI)

Documentation complémentaire :

- [INSTALACAO_GNB_OAI.md](../../../../../../server/oai-cn-gnb-e2/docs/INSTALACAO_GNB_OAI.md) — dépendances et build de base du RAN
- [SLIDES_LAB_E2.md](../../../../../../server/oai-cn-gnb-e2/docs/SLIDES_LAB_E2.md) — présentation des résultats (format Marp)
- [E2_FLEXRIC.md](../../../../../../server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md) — opération E2/FlexRIC
- [E2_SERVICE_MODELS.md](../../../../../../server/oai-cn-gnb-e2/docs/E2_SERVICE_MODELS.md) — détails RC/KPM/custom SMs

---

## 4. Préparation (une fois)

### 4.1 Cloner / entrer dans le projet

```bash
cd ric/code/oai-cn-gnb-e2
```

### 4.2 Installer les dépendances OAI

```bash
cd openairinterface5g/cmake_targets
./build_oai --ninja -I
cd ../..
```

### 4.3 Compiler gNB + nrUE **avec l'agent E2**

```bash
./scripts/build_e2.sh
```

Sortie attendue (finale) :

```
Build concluído. Binários em: openairinterface5g/cmake_targets/ran_build/build/
  nr-softmodem (com E2 agent)
  nr-uesoftmodem
```

Log complet : `logs/build_e2.log`

### 4.4 Compiler nearRT-RIC, Service Models et xApps

```bash
./scripts/build_flexric_tools.sh
```

Ceci compile :

- `nearRT-RIC` (sous-module FlexRIC)
- SMs : `libkpm_sm.so`, `librc_sm.so`, `libmac_sm.so`, …
- xApps : `xapp_kpm_moni`, `xapp_rc_moni`, `xapp_kpm_rc`, …

Les libs sont copiées vers **`flexric-lib/`** (chemin local du projet).

> **Important :** le Core OAI utilise **AMF Region ID = 128**. La `libkpm_sm.so` installée dans `/usr/local/lib/flexric/` (ancienne version) **plantait** lors de la génération des INDICATION KPM. Utilisez toujours **`flexric-lib/`** du sous-module `dev`.

---

## 5. Démarrer le laboratoire

### Option A — Lab complet E2 (recommandé)

```bash
./scripts/up_e2_lab.sh
```

Séquence : Core → nearRT-RIC → gNB + nrUE (avec `--e2_agent.sm_dir flexric-lib/`).

### Option B — Pas à pas manuel

```bash
# 1. Core 5G (UPF-VPP, scenario 1)
./scripts/up_core.sh

# 2. nearRT-RIC (submodule dev + flexric-lib/)
./scripts/up_flexric.sh

# 3. gNB + nrUE (RFSIM, slice 222/123)
./scripts/up_gnb_oai.sh
```

### Vérifier le Core

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep oai
```

Exemple :

```
oai-amf     Up ...
oai-smf     Up ...
oai-upf     Up ...
```

### Vérifier E2 sur le gNB

```bash
grep -E '\[E2 AGENT\]|\[E2-AGENT\]' logs/gnb_oai.log | tail -15
```

Log attendu (avec `flexric-lib/`) :

```
[E2 NODE]: Args 127.0.0.1 .../flexric-lib/
[E2 AGENT]: nearRT-RIC IP Address = 127.0.0.1, PORT = 36421, RAN type = ngran_gNB, nb_id = 3584
[E2 AGENT]: Opening plugin from path = .../flexric-lib/libkpm_sm.so
[E2-AGENT]: E2 SETUP-REQUEST tx
[E2-AGENT]: E2 SETUP RESPONSE rx
```

### Vérifier l'attachement de l'UE

```bash
grep RRCSetupComplete logs/gnb_oai.log | tail -3
grep -i registered logs/ue_oai.log | tail -3
```

---

## 6. Tests E2 — Service Models

### 6.1 Custom SMs (MAC, RLC, PDCP, GTP)

Encodage plain ; fonctionne indépendamment du slice.

```bash
./scripts/test_e2_sm.sh cust
# ou exploração rápida:
./scripts/explore_e2_sm.sh quick
```

Log typique (`logs/xapp_cust_moni.log`) :

```
Connected E2 nodes = 1
 Registered node 0 ran func id = 2    # KPM
 Registered node 0 ran func id = 3    # RC
 Registered node 0 ran func id = 142  # MAC
 Registered node 0 ran func id = 143  # RLC
 Registered node 0 ran func id = 144  # PDCP
 ...
```

### 6.2 E2SM-RC (événements RRC)

Ordre critique : **RIC → xApp RC → gNB → UE** (souscription avant l'attachement).

```bash
./scripts/test_e2_rc_attach.sh
```

Log typique (`logs/xapp_rc_attach.log`) :

```
Connected E2 nodes = 1
[xApp]: Successfully subscribed to RAN_FUNC_ID 3

      1 RC Indication Message received:
RAN Parameter Name = RRC Message
...
            <rrcSetupComplete>
                <rrc-TransactionIdentifier>1</rrc-TransactionIdentifier>
                ...
            </rrcSetupComplete>
```

> **Note :** le `xapp_rc_moni` peut se terminer par un timeout dans `sync_ui.c` après la **première** INDICATION — comportement connu de l'exemple upstream. L'INDICATION a déjà été capturée avant le crash.

### 6.3 E2SM-KPM (métriques 3GPP, slice du lab)

Slice aligné sur le Core/AMF : **SST=222, SD=123** (voir `openairinterface5g/scripts/ue.conf` et `gnb.conf`).

```bash
./scripts/test_e2_kpm.sh

# Parâmetros opcionais:
KPM_SST=222 KPM_SD=123 XAPP_DURATION=45 KPM_TRAFFIC=1 ./scripts/test_e2_kpm.sh
```

Log typique (`logs/xapp_kpm_lab.log`) :

```
Connected E2 nodes = 1
[xApp]: Successfully subscribed to RAN_FUNC_ID 2

      1 KPM ind_msg latency = ...
UE ID type = gNB, amf_ue_ngap_id = 7
ran_ue_id = 1
DRB.PdcpSduVolumeDL = 0 [Mb]
DRB.PdcpSduVolumeUL = 0 [Mb]
DRB.RlcSduDelayDl = 0.00 [μs]
DRB.UEThpDl = 18.04 [kbps]
DRB.UEThpUl = 19.18 [kbps]
RRU.PrbTotDl = 0 [%]
RRU.PrbTotUl = 2 [%]

      2 KPM ind_msg latency = ...
DRB.UEThpDl = 3.72 [kbps]
...
```

Avec `KPM_TRAFFIC=1` (par défaut), le script génère un ping vers le DN (`192.168.73.135`) via l'interface UE (`12.1.1.x`), augmentant le débit mesuré.

### 6.4 Exploration par suite

```bash
./scripts/explore_e2_sm.sh rc      # foco RC
./scripts/explore_e2_sm.sh kpm     # foco KPM
./scripts/explore_e2_sm.sh oran    # KPM + RC
./scripts/explore_e2_sm.sh layers  # custom MAC/RLC/PDCP/GTP
./scripts/explore_e2_sm.sh full    # todas (demorado)
```

---

## 7. Arrêter le laboratoire

```bash
# Só E2 (RIC + xApps)
./scripts/down_flexric.sh

# RAN (gNB + nrUE)
./scripts/down_gnb_oai.sh

# Lab E2 completo
./scripts/down_e2_lab.sh

# Core Docker
./scripts/down_core.sh

# Tudo
./scripts/down_all.sh
```

---

## 8. Configuration pertinente

| Paramètre | Valeur lab | Fichier |
|-----------|-----------|----------|
| PLMN | 208 / 95 | `gnb.conf`, `ue.conf` |
| S-NSSAI | SST **222**, SD **123** | `gnb.conf`, `ue.conf` |
| IMSI UE | 208950000000032 | `ue.conf` |
| AMF IP (gNB) | 192.168.70.129 (hôte, iface `demo-oai`) | `gnb.conf` |
| nearRT-RIC | 127.0.0.1:36421 | `gnb.conf` → `e2_agent.near_ric_ip_addr` |
| SMs E2 | `flexric-lib/` (projet) | `--e2_agent.sm_dir` dans les scripts |
| KPM filtre slice | `KPM_SST=222`, `KPM_SD=123` | variables d'env dans les scripts KPM |

Exemple `e2_agent` dans `openairinterface5g/scripts/gnb.conf` :

```
e2_agent = {
  near_ric_ip_addr = "127.0.0.1";
  sm_dir = ".../flexric-lib/";   # override via --e2_agent.sm_dir nos scripts
};
```

---

## 9. Scripts de référence

| Script | Fonction |
|--------|--------|
| `build_e2.sh` | Compile gNB/nrUE avec l'agent E2 |
| `build_flexric_tools.sh` | Compile RIC, SMs, xApps ; peuple `flexric-lib/` |
| `sync_flexric_lib.sh` | Copie les `.so` du build FlexRIC → `flexric-lib/` |
| `up_e2_lab.sh` | Core + RIC + gNB + UE |
| `up_flexric.sh` / `down_flexric.sh` | nearRT-RIC |
| `up_gnb_oai.sh` / `down_gnb_oai.sh` | gNB + nrUE |
| `test_e2_kpm.sh` | Test KPM slice 222/123 |
| `test_e2_rc_attach.sh` | Test RC avec nouvel attachement |
| `test_e2_sm.sh` | Tests par SM (`cust`, `rc`, `kpm`, …) |
| `explore_e2_sm.sh` | Suites d'exploration |

Logs : répertoire **`logs/`** (`gnb_oai.log`, `ue_oai.log`, `nearRT-RIC.log`, `xapp_kpm_lab.log`, …).

---

## 10. Troubleshooting

### Timeout KPM / crash du gNB

**Symptôme :**

```
cp_amf_region_id_to_bit_string: Assertion `src < 64' failed
```

**Cause :** `libkpm_sm.so` de `/usr/local` incompatible avec AMF Region ID 128.

**Solution :**

```bash
./scripts/build_flexric_tools.sh
./scripts/down_flexric.sh && ./scripts/down_gnb_oai.sh
./scripts/test_e2_kpm.sh
```

### Crash nearRT-RIC `E2 Node not found in the tree`

**Cause :** xApps « zombie » se connectant au RIC sans nœud E2 enregistré, ou gNB désaligné après le redémarrage du RIC.

**Solution :**

```bash
./scripts/down_flexric.sh
pkill -f xapp_ 2>/dev/null || true
./scripts/up_flexric.sh
./scripts/down_gnb_oai.sh && ./scripts/up_gnb_oai.sh
```

### RC sans INDICATION

- Souscrire **avant** l'attachement : `./scripts/test_e2_rc_attach.sh`
- RC est **apériodique** (événements RRC) ; l'attachement de l'UE déclenche `RRCSetupComplete`

### KPM sans métriques (zéros)

- Confirmer la session PDU dans le slice 222/123
- Utiliser `KPM_TRAFFIC=1` et vérifier le ping vers le DN
- Augmenter `XAPP_DURATION=60`

### `xapp_oran_moni` (/usr/local)

Ne pas utiliser pour KPM dans ce lab — filtre SST=1 par défaut. Utiliser `./scripts/test_e2_kpm.sh`.

---

## 11. Séquence minimale de reproduction (checklist)

```bash
cd ric/code/oai-cn-gnb-e2

# Build (uma vez)
./scripts/build_e2.sh
./scripts/build_flexric_tools.sh

# Subir stack
./scripts/up_e2_lab.sh
sleep 30

# Testes
./scripts/test_e2_sm.sh cust          # custom SMs
./scripts/test_e2_rc_attach.sh        # RC + attach
./scripts/test_e2_kpm.sh              # KPM slice 222/123

# Inspecionar
grep -E 'Successfully subscribed|INDICATION|UEThp' logs/xapp_*.log
grep 'E2 SETUP RESPONSE' logs/gnb_oai.log

# Parar
./scripts/down_e2_lab.sh
```

---

## 12. Prochaines étapes (optionnel)

- Valider `xapp_kpm_rc` (monitoring KPM + RC Control) avec un trafic soutenu
- Augmenter la durée des tests pour des séries temporelles de métriques KPM
- Intégrer la collecte automatique de logs dans un pipeline de CI local

---

*Document généré à partir des tests exécutés en juin 2026 sur l'hôte de développement du projet `oai-cn-gnb-e2` (cours RIC / Cesar School).*
