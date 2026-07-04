<!-- sync: e36a3f4e -->
> 🌐 Traduction en **français** du document canonique en portugais [`server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md`](../../../../../../server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md). Toutes les langues : [INDEX](../../../INDEX.md) · synchronisation vérifiée par `docs/i18n/check-parity.py`.

# Interface E2 et Service Models (FlexRIC)

Guide pour exploiter l'interface **E2** entre le gNB OAI et un **nearRT-RIC** (FlexRIC), et tester des **Service Models** (SMs) O-RAN et personnalisés.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Core OAI (AMF, SMF, UPF-VPP, ...)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │ N2 / N3
┌──────────────────────────┴──────────────────────────────────┐
│  gNB OAI (nr-softmodem)                                       │
│    └── E2 Agent ──E2AP──► nearRT-RIC (FlexRIC) :36421         │
│                              └── xApps (KPM, RC, MAC, ...)    │
└──────────────────────────┬──────────────────────────────────┘
                           │ RFSIM
                      nrUE (nr-uesoftmodem)
```

## Service Models disponibles

| SM | Type | Encodage | xApp recommandé | Notes |
|----|------|----------|------------------|-------|
| **E2SM-KPM** v2.03 | O-RAN | ASN.1 | `xapp_oran_moni` | Métriques 3GPP (PRB, débit, volume PDCP…) |
| **E2SM-RC** v1.03 | O-RAN | ASN.1 | `xapp_oran_moni` | état RRC, copie de messages, contrôle QoS (PoC) |
| **MAC** | Custom | Plain | `xapp_gtp_mac_rlc_pdcp_moni` | KPIs L2 MAC par UE |
| **RLC** | Custom | Plain | `xapp_gtp_mac_rlc_pdcp_moni` | KPIs RLC par bearer |
| **PDCP** | Custom | Plain | `xapp_gtp_mac_rlc_pdcp_moni` | KPIs PDCP par bearer |
| **GTP** | Custom | Plain | `xapp_gtp_mac_rlc_pdcp_moni` | Stats GTP-U NGU |

Versions de compilation par défaut : **E2AP v2.03** + **E2SM-KPM v2.03** (doivent coïncider entre le gNB et FlexRIC).

## Versions et encodage (ce que CETTE plateforme utilise)

| Composant | Version/valeur | Où c'est défini |
|---|---|---|
| FlexRIC (intégré dans OAI) | **2.0.0** | `openairinterface5g/openair2/E2AP/flexric/CMakeLists.txt` (`project(FlexRIC VERSION 2.0.0)`) |
| E2AP | v2.03 | flag de build (`-DE2AP_VERSION=E2AP_V2`) |
| Encodage de l'E2AP | **ASN.1** (`E2AP_ENCODING="ASN"`, la valeur par défaut) | `flexric/CMakeLists.txt` ligne ~205 ; nos scripts **ne** l'écrasent **pas** |
| FlatBuffers/FlatCC | **non utilisé** | alternative upstream (`-DE2AP_ENCODING=FLATBUFFERS`, exige FlatCC installé) ; hors de notre build |

> Pour l'article : « E2AP avec encodage ASN.1 (FlexRIC 2.0.0) ; FlatBuffers est
> pris en charge par FlexRIC upstream, mais non utilisé sur cette plateforme. »
> Les SMs personnalisés (MAC/RLC/PDCP/GTP) utilisent leur propre encodage (« Plain »,
> tableau ci-dessus) — cela relève du Service Model, pas de l'E2AP.

Documentation upstream : `openairinterface5g/openair2/E2AP/README.md`

## Prérequis

1. **FlexRIC** installé sur l'hôte (Service Models dans `/usr/local/lib/flexric/`) :

   ```bash
   # Se ainda não tiver FlexRIC:
   git clone https://gitlab.eurecom.fr/mosaic5g/flexric.git
   cd flexric && git checkout dev
   mkdir build && cd build
   cmake .. -GNinja -DE2AP_VERSION=E2AP_V2 -DKPM_VERSION=KPM_V2_03
   ninja && sudo ninja install
   ```

2. **Sous-module FlexRIC** dans OAI (pour compiler l'E2 agent) :

   ```bash
   # Automático via ./scripts/build_e2.sh
   ```

3. **Core OAI** opérationnel (`./scripts/up_core.sh`).

## Build du gNB avec l'agent E2

```bash
cd ric/code/oai-cn-gnb-e2
./scripts/build_e2.sh
```

Cela compile `nr-softmodem` et `nr-uesoftmodem` avec `-DE2_AGENT=ON`. Log dans `logs/build_e2.log` (~15–30 min la première fois).

## Configuration E2 sur le gNB

Dans `openairinterface5g/scripts/gnb.conf` :

```bash
e2_agent = {
  near_ric_ip_addr = "127.0.0.1";
  sm_dir = "/usr/local/lib/flexric/";
};
```

- `near_ric_ip_addr` : IP du nearRT-RIC (localhost si FlexRIC tourne sur le même hôte).
- `sm_dir` : répertoire contenant `libkpm_sm.so`, `librc_sm.so`, `libmac_sm.so`, etc.

Port E2AP FlexRIC : **36421** (O-RAN SC utilise 36422 — nécessite une recompilation avec `e2ap_server_port`).

## Flux opérationnel

### Option A — laboratoire complet (recommandé)

```bash
./scripts/up_e2_lab.sh          # Core + RIC + gNB + UE
./scripts/test_e2_sm.sh cust    # testar MAC/RLC/PDCP/GTP
./scripts/down_e2_lab.sh
```

### Option B — pas à pas

```bash
./scripts/up_core.sh
./scripts/up_flexric.sh
./scripts/up_gnb_oai.sh
./scripts/test_e2_sm.sh cust
```

## Tester les Service Models

```bash
# Custom SMs (funciona com slice 222/123 do laboratório)
XAPP_DURATION=30 ./scripts/test_e2_sm.sh cust

# O-RAN KPM + RC
./scripts/test_e2_sm.sh oran

# Todos os SMs
./scripts/test_e2_sm.sh all
```

### Vérifier le E2 setup

```bash
grep -iE 'E2|RIC|setup|indication' logs/gnb_oai.log
grep -iE 'E2|setup|indication' logs/nearRT-RIC.log
```

Indices de succès :
- gNB : messages `E2 Setup` / connexion SCTP au RIC
- xApp : `RIC INDICATION` avec des métriques périodiques

### KPM et slice S-NSSAI

Par défaut upstream, le xApp KPM souscrit à **SST=1**. Ce laboratoire utilise **SST=222, SD=123**.

Les xApps `xapp_kpm_moni` et `xapp_kpm_rc` (sous-module FlexRIC `dev`) ont été ajustés pour le slice du lab :

```bash
# Padrão: SST=222 SD=123 (Core/AMF/gNB/UE)
./scripts/test_e2_kpm.sh

# Override
KPM_SST=222 KPM_SD=123 XAPP_DURATION=45 ./scripts/test_e2_kpm.sh

# Só SST (SD wildcard no agente)
KPM_SD=any ./scripts/test_e2_kpm.sh
```

Métriques O-RAN prises en charge (3GPP TS 28.552) : `DRB.PdcpSduVolumeDL/UL`, `DRB.UEThpDl/Ul`, `RRU.PrbTotDl/Ul`, etc.

Générez du trafic pendant le test (`KPM_TRAFFIC=1` par défaut) pour des métriques de débit/volume non nulles.

**SMs :** le gNB et le nearRT-RIC doivent utiliser les libs du sous-module (`flexric-lib/`), pas `/usr/local/lib/flexric/` — la version installée sur le système échoue avec l'AMF Region ID 128 du Core OAI. `./scripts/build_flexric_tools.sh` compile et synchronise automatiquement.

**Note :** `xapp_oran_moni` (installé dans `/usr/local`) utilise encore SST=1 — utilisez `./scripts/test_e2_kpm.sh` pour le KPM dans ce lab.

## Scripts

| Script | Description |
|--------|-----------|
| `build_e2.sh` | Compile le gNB/nrUE avec l'agent E2 |
| `up_flexric.sh` | Démarre le nearRT-RIC |
| `down_flexric.sh` | Arrête le RIC et les xApps |
| `up_e2_lab.sh` | Core + RIC + gNB + UE |
| `down_e2_lab.sh` | Arrête le gNB et le RIC (`--all` inclut le Core) |
| `test_e2_kpm.sh` | KPM avec slice lab (222/123) + trafic |
| `explore_e2_sm.sh` | Suite d'exploration (rc, oran, layers, full) |
| `test_e2_rc_attach.sh` | RC avec attachement synchronisé (capture les INDICATIONs) |
| `build_flexric_tools.sh` | Compile le nearRT-RIC + xApps dédiés (dev) |

## Dépannage

| Problème | Cause probable | Solution |
|----------|----------------|---------|
| Le build échoue « submodules not downloaded » | FlexRIC vide | `./scripts/build_e2.sh` (clone automatiquement) |
| Le gNB ne se connecte pas au RIC | RIC arrêté ou mauvaise IP | `./scripts/up_flexric.sh` ; vérifier `near_ric_ip_addr` |
| xApp sans INDICATION (cust) | UE sans PDU session | Attendre l'enregistrement ; vérifier les logs AMF/SMF |
| xApp sans INDICATION (KPM) | Filtre slice SST=1 | Utiliser `test_e2_sm.sh cust` ou aligner le slice |
| `libkpm_sm.so` not found | FlexRIC non installé | `./scripts/build_flexric_tools.sh` |
| KPM crash / timeout | SMs de `/usr/local` désalignés (AMF Region ID 128) | Utiliser `flexric-lib/` via `./scripts/sync_flexric_lib.sh` |
| xApp crash `e2ap_dec_e42_setup_response` | xApp de `/usr/local` ou `/opt/flexric` | `./scripts/test_e2_sm.sh` n'utilise que les xApps du sous-module dev |

## Références

- [OAI E2AP README](../../../../../../server/oai-cn-gnb-e2/openairinterface5g/openair2/E2AP/README.md)
- [FlexRIC](https://gitlab.eurecom.fr/mosaic5g/flexric)
- [O-RAN E2SM-KPM](https://orandownloadsweb.azurewebsites.net/specifications)
- Docker Compose upstream (sans Core) : `openairinterface5g/ci-scripts/yaml_files/5g_rfsimulator_flexric/`
