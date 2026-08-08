<!-- sync: 95a1e8b1 -->
> 🌐 Traduction en **français** du document canonique en portugais [`core5g-arm64-bible.md`](../../../core5g-arm64-bible.md). Toutes les langues : [INDEX](INDEX.md) · synchronisation vérifiée par `docs/i18n/check-parity.py`.

# Core5G ARM64 — Bible du Projet

Document de référence unique et complet. Si vous (ou quelqu'un du groupe) arrivez
ici sans aucun contexte, ce fichier doit suffire à comprendre le quoi, le
pourquoi et le comment de tout ce qui existe dans ce dépôt et sur le serveur.

Pour l'historique chronologique pas à pas (le « journal de bord »), voir
[`CHANGELOG.md`](../../../CHANGELOG.md). Ce document-ci est la photographie
consolidée de l'état actuel + les explications conceptuelles.

---

## 1. Contexte de la matière

- **Matière 7 : RAN Intelligent Controller (RIC)** — spécialisation CESAR School.
- **Professeur :** Dr. Jonas Augusto Kunzler (`jak@cesar.school`).
- **Groupe (Groupe 6) :** Henrique, Klinger, Kelvin, Gilberto.
- **Thème tiré au sort (NGO §6.1) :** **UE-TP-rApp** — prévision de débit par UE
  (RSSI, RSRP, CQI, PRB, historique).

### Deux projets évalués (40 % chacun)

| Projet | Quoi | Où c'est | Statut |
|---|---|---|---|
| **Projet 1** | Open5GS conteneurisé + UERANSIM (Core 5G + RAN simulé) | `server/` (racine de ce dépôt) | ✅ Présenté le 13/06/2026 (Cours 03). Validé de bout en bout sur le serveur. |
| **Projet 2** | `oai-cn-gnb-e2` — OAI 5GC + gNB avec agent E2 + FlexRIC (near-RT RIC) + xApps | `server/oai-cn-gnb-e2/` | ⏳ En attente. Présentation le 20/06/2026 (Cours 06, 08:00–11:00, 20 min/groupe, même ordre que le Projet 1). |

Livrables du Projet 2 (selon le slide « Projeto 2 (40%) — roteiro e
prazos » de `pdfs/aula04-xapps_opensource.pdf`) :
- Implémenter `oai-cn-gnb` conformément à `server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md`.
- Rapport technique + démo (vidéo/logs).
- Extension optionnelle : xApp personnalisé ou cas A1/politiques.
- **Attention :** la grille officielle (`docs/avaliacao_seminario_aula06.md`) et le
  plan de tests (`docs/labs/04-projeto2-plano-testes.md`) cités dans les
  slides **n'étaient pas publiés** dans le dépôt d'origine
  (`jakunzler/cesar-school-repo`) au moment où nous avons vérifié — confirmer avec
  le professeur avant la remise.

---

## Crédits

Dépôt maintenu par **Henrique Carmine** —
[henriquecarmine@gmail.com](mailto:henriquecarmine@gmail.com) ·
[@henriquecarmine](https://github.com/henriquecarmine).

---

## 2. Comment tout cela fonctionne, expliqué à qui n'est pas technicien

Imaginez le réseau 5G comme une **entreprise de livraison** (genre La Poste), sauf qu'au
lieu de lettres elle livre de l'**internet** jusqu'à votre téléphone. Chaque conteneur
Docker ci-dessous est un « service » de cette entreprise, tournant isolé des autres.

### Le chemin que le téléphone parcourt (Projet 1 — Open5GS)

| Qui | Conteneur Docker | Ce qu'il fait, en une phrase |
|---|---|---|
| 📡 Antenne | `nr-gnb` (UERANSIM) | La tour cellulaire (simulée) — c'est par là que le téléphone parle au réseau. |
| 📱 Téléphone | `nr-ue` (UERANSIM) | Le téléphone (simulé) qui s'allume, s'enregistre et demande à utiliser internet. |
| 🛎️ Portier/accueil | `amf` | Premier contact : reçoit le téléphone, vérifie qui il est et l'oriente vers le bon service. |
| 🔐 Sécurité | `ausf` | Vérifie le « mot de passe » du téléphone — ne laisse passer que le véritable propriétaire de la carte SIM. |
| 🗂️ Fichier client | `udm` | Garde le profil de chaque client : quel forfait il a, ce qu'il peut accéder. |
| 🗄️ Base de données | `udr` + `mongodb` | Le fichier/la base où les données d'inscription sont réellement enregistrées. |
| 🚦 Contrôleur de règles | `pcf` | Décide les règles de chaque connexion : vitesse, priorité, politique d'usage. |
| 📋 Tableau d'affichage | `bsf` | Note quel contrôleur (`pcf`) s'occupe de quelle connexion, pour que d'autres services le retrouvent ensuite. |
| 🧭 Tri des voies | `nssf` | Choisit sur quelle « voie »/file (*slice*) ce téléphone doit rouler. |
| 🗺️ Gestionnaire logistique | `smf` | Organise la « route de livraison » : monte la session de données que le téléphone va utiliser. |
| 🚚 Camion de livraison | `upf-a` / `upf-b` | Transporte réellement les données (l'internet) d'un côté à l'autre. Deux camions, un en réserve. |
| 🌐 Destination finale (test) | `dn` | Un « monde extérieur » factice juste pour simuler l'internet réel pendant les tests. |
| ☎️ Annuaire téléphonique interne | `nrf` | Chaque service s'inscrit ici — c'est ainsi qu'un service trouve le numéro d'un autre. |
| 📞 Standardiste interne | `scp` | Transfère les appels entre les services (au lieu que chacun appelle directement l'autre). |
| 🖥️ Guichet d'accueil | `webui` | Écran web où l'on inscrit un nouveau « client » (abonné) dans le système. |

**Ordre réel de ce qui se passe quand un téléphone s'allume et demande internet :**
1. Le téléphone (`nr-ue`) aperçoit l'antenne (`nr-gnb`) et envoie un signal.
2. `amf` reçoit, vérifie qui c'est avec l'aide d'`ausf` (mot de passe) et d'`udm` (fichier).
3. `pcf` décide les règles de cette connexion et prévient le tableau (`bsf`).
4. `nssf` choisit la bonne voie, `smf` monte la route de données.
5. `upf-a`/`upf-b` (le camion) commence à transporter des données réelles entre le
   téléphone et le « monde extérieur » (`dn`, ou l'internet réel selon le cas).

Tout cela est du **3GPP standard** — Open5GS (Projet 1) et OAI (Projet 2) sont deux
« marques » différentes d'entreprise de livraison, mais avec les mêmes services.

### Le tableau de bord (ne fait pas partie du réseau 5G, c'est juste pour nous opérer)

| Conteneur/processus | Fonction, en une phrase |
|---|---|
| 🚪 Portier du tableau | `caddy` — vérifie utilisateur et mot de passe à l'entrée du site et ne laisse entrer que ceux qui ont un badge (login), en plus de chiffrer la connexion (HTTPS). |
| 🖱️ Bureau des boutons | `server/panel/server.py` (FastAPI/Uvicorn) — c'est lui qui appuie réellement sur le bouton allumer/éteindre le réseau quand vous cliquez à l'écran. |

> Résumé : le tableau de bord n'est qu'une télécommande pour allumer/éteindre/vérifier
> l'« entreprise de livraison » ci-dessus — il ne fait pas partie du réseau 5G lui-même.

---

## 2.a Pour le technicien télécom (qui a déjà touché à la radio)

Vous connaissez l'antenne, la couverture, la fréquence, vous avez peut-être déjà configuré une BTS ou un eNodeB
sur le terrain. Cette section parle votre langue — sans analogie d'entreprise de livraison,
sans code, sans protocole au niveau des octets.

### Ce qui tourne ici, en termes de radio

Ce projet simule une cellule 5G complète à l'intérieur d'un serveur ARM dans le cloud.
Il n'y a pas d'antenne physique, pas de RF réelle — mais **toute la logique de
signalisation, d'authentification et de transport de données est réelle**, exécutant les mêmes
protocoles qu'un réseau opérateur utilise.

**Paramètres radio du Projet 1 (UERANSIM) :**

| Paramètre | Valeur |
|---|---|
| Bande | n78 (3,3–3,8 GHz) — bande principale de la 5G SA au Brésil |
| Mode | TDD (Time Division Duplex) — DL et UL sur la même fréquence, séparés par le temps |
| Largeur de bande | 100 MHz |
| Numérologie (SCS) | 30 kHz (µ=1) |
| PRBs actifs | 66 (sur 132 au total pour 100 MHz / 30 kHz) |
| RSRP typique simulé | −79 dBm @ 100 m · −100 dBm @ 500 m · −111 dBm @ 1 km |
| Modèle de propagation | 3GPP TR 38.901 UMa NLOS |
| Débit crête théorique DL | ~665 Mbps (64-QAM, 4 couches MIMO) |
| Débit crête théorique UL | ~250 Mbps |

> UERANSIM simule la radio par logiciel : l'interface `uesimtun0` est
> l'équivalent logique du tunnel entre l'antenne et l'UE. Il n'y a pas d'échantillon IQ,
> il n'y a pas de FPGA — mais NAS, RRC, PDCP et GTP-U sont tous réellement exécutés.

### Les conteneurs — ce que chacun est, en termes que vous connaissez

Si vous avez travaillé avec la 4G/LTE, vous en reconnaîtrez la plupart. La 5G SA a renommé et
réorganisé les pièces, mais la fonction est la même.

| Conteneur | Équivalent 4G / LTE | Ce qu'il fait |
|---|---|---|
| `nr-gnb` (UERANSIM) | eNodeB (eNB) | La station-radio-base (simulée). Traite RRC, le scheduler de PRB, GTP-U avec le core. |
| `nr-ue` (UERANSIM) | UE / téléphone | L'appareil (simulé). Fait l'attach, la PDU session, « mesure » le RSRP/RSRQ, lance iperf3. |
| `amf` | MME | Contrôle d'accès, authentification, enregistrement et mobilité de l'UE. |
| `smf` | SGW-C + PGW-C | Contrôle le plan de données : définit la route du paquet, instruit l'UPF via PFCP. |
| `upf-a` / `upf-b` | SGW-U + PGW-U | Plan utilisateur. Reçoit GTP-U du gNB (N3) et achemine vers internet (N6). |
| `ausf` | HSS (partie auth) | Exécute le 5G-AKA — génère le vecteur d'authentification à partir du Ki et de l'OPc du SIM. |
| `udm` | HSS (partie données) | Profil de l'abonné : IMSI, forfait, slice (S-NSSAI), MSISDN. |
| `udr` + `mongodb` | HSS (stockage) | Base de données d'abonné. L'UDM lit ici. |
| `pcf` | PCRF | Politique de QoS : définit QFI, 5QI, règles de throttling par session. |
| `bsf` | (nouveau en 5G SA) | Enregistre quel PCF gère quelle session — évite les conflits quand l'AMF doit localiser le PCF d'un UE actif. |
| `nssf` | (nouveau en 5G SA) | Network Slice Selection — décide dans quelle tranche de réseau (URLLC, eMBB, mMTC) l'UE entre. |
| `nrf` | (nouveau en 5G SA) | Enregistrement des NFs : chaque fonction s'inscrit ici ; les autres consultent pour connaître l'adresse de qui elles doivent appeler. |
| `scp` | (nouveau en 5G SA) | Proxy de signalisation SBI — centralise les appels HTTP/2 entre NFs. |
| `dn` | PDN-GW / internet | Réseau de données de destination. Ici tourne le serveur iperf3 qui mesure le débit réel par le tunnel de l'UE. |

### Comment fonctionne la simulation de canal (tc netem)

Le tableau de bord a un mode « Conditions du canal » où vous choisissez distance et
interférence. Il n'y a pas de radio réelle — le tableau injecte des paramètres de
**Network Emulator (netem)** sur l'interface `uesimtun0` via `tc qdisc` :

```
tc qdisc replace dev uesimtun0 root netem delay <D>ms loss <L>%
```

Les valeurs sont dérivées du modèle 3GPP TR 38.901 UMa NLOS (path loss) et du
SINR pour chaque niveau d'interférence :

| Condition | RSRP approx. | Délai total | Perte totale | Équivalent terrain |
|---|---|---|---|---|
| 100 m, sans interférence | −79 dBm | 1 ms | 0% | UE proche de la tour, bonne visibilité |
| 500 m, interférence faible | −100 dBm | 13 ms | ~3% | Bonne couverture, co-canal léger (SINR ≈ 20 dB) |
| 1 km, interférence moyenne | −111 dBm | 40 ms | ~12% | Bord de cellule (SINR ≈ 15 dB) |
| 3 km, interférence élevée | −127 dBm | 100 ms | ~32% | UE à l'ombre, handover imminent (SINR ≈ 10 dB) |

### Différences entre le Projet 1 (UERANSIM) et le Projet 2 (OAI + FlexRIC)

| Aspect | Projet 1 — UERANSIM | Projet 2 — OAI nr-softmodem |
|---|---|---|
| Couche radio | Simulée (NAS/RRC/GTP-U via socket, sans PHY réelle) | RFSIM : PHY réelle en logiciel, sans matériel RF |
| Scheduler de PRBs | Implémenté dans UERANSIM (fixe) | Scheduler réel de l'OAI (round-robin / proportional fair) |
| Interface avec le RIC | Aucune — gNB monolithique, sans agent E2 | Agent E2 réel ; se connecte à FlexRIC et exporte les KPI par UE |
| Métriques radio accessibles | Seulement les logs internes | DRB.UEThpDl/Ul, RRU.PrbTotDl/Ul, SINR via E2SM-KPM |
| Analogie terrain | Drive test : vous n'avez que des logs de NAS | OMC de la BTS : KPI par UE en temps réel, contrôlable via xApp |

> Le Projet 1 suffit pour valider core + attach. Le Projet 2 est ce qu'un
> intégrateur de RIC aurait besoin pour mettre en service des xApps d'optimisation de PRB,
> de handover ou de QoS par UE.

---

## 2.b Pour l'ingénieur réseaux (vision O-RAN / 3GPP)

Si vous connaissez les télécommunications mais pas l'environnement Docker/Linux de ce projet,
cette section mappe chaque pièce à son rôle dans l'architecture O-RAN et le 3GPP 5G SA.

### Qu'est-ce que l'O-RAN et où ce projet s'insère-t-il

O-RAN (Open Radio Access Network) définit une architecture désagrégée de la RAN avec
des interfaces ouvertes. La division fonctionnelle adoptée par l'O-RAN Alliance est le
**Split 7.2x** (entre PHY-Low et PHY-High), qui sépare le nœud d'accès en :

```
┌──────────────────────────────────────────────────────────────┐
│ SMO (Service Management & Orchestration)                     │
│  · Non-RT RIC: rApps, políticas A1, gerência O1              │
│  · Horizonte de controle: > 1 s                              │
└───────────────────────────┬──────────────────────────────────┘
                            │ A1 (políticas) / O1 (FCAPS)
┌───────────────────────────▼──────────────────────────────────┐
│ Near-RT RIC (near-Real-Time RIC)                             │
│  · xApps: E2SM-KPM (métricas), E2SM-RC (controle)            │
│  · Horizonte de controle: 10 ms – 1 s                        │
│  · Implementação deste projeto: FlexRIC (Projeto 2)          │
└───────────────────────────┬──────────────────────────────────┘
                            │ E2 (E2AP / E2SM)
┌───────────────────────────▼──────────────────────────────────┐
│ O-gNB (agente E2 embutido)                                   │
│  ┌─────────────┐  ┌─────────────┐   ┌──────────────────────┐ │
│  │  O-CU-CP    │  │  O-CU-UP    │   │       O-DU           │ │
│  │ RRC / PDCP-C│  │  PDCP-U     │   │  RLC / MAC / PHY-Hi  │ │
│  └──────┬──────┘  └────── ┬─────┘   └──────────┬───────────┘ │
│         │ F1-C            │ F1-U               │             │
│         └────────────────-┘                    │ Open FH     │
└─────────────────────────────────────────────── │ (7.2x) ─────┘
                                                 │
                                        ┌─────────▼────────┐
                                        │      O-RU        │
                                        │  PHY-Low / RF    │
                                        └──────────────────┘
```

**Interfaces standardisées pertinentes :**

| Interface | Entre | Protocole |
|---|---|---|
| E2 | Near-RT RIC ↔ O-gNB | E2AP sur SCTP ; E2SM-KPM/RC |
| A1 | Non-RT RIC ↔ Near-RT RIC | REST/JSON ; politiques de ML/QoS |
| O1 | SMO ↔ tous les nœuds gérés | NETCONF/YANG |
| F1-C/U | O-CU ↔ O-DU | NG-AP + GTP-U (3GPP TS 38.473) |
| Open FH | O-DU ↔ O-RU | eCPRI sur Ethernet (Split 7.2x) |
| N2 | O-CU-CP ↔ AMF | NGAP sur SCTP |
| N3 | O-CU-UP ↔ UPF | GTP-U sur UDP |
| N4 | SMF ↔ UPF | PFCP sur UDP |

### Comment le Projet 1 (Open5GS + UERANSIM) s'insère

UERANSIM implémente un **gNB monolithique** (sans Split 7.2 — CU, DU et RU sont un
seul processus) et un **UE** qui parle NAS sur la stack simulée. C'est la référence
la plus simple du 3GPP 5G SA sans Near-RT RIC.

```
UERANSIM nr-gnb  ──N2 (NGAP)──►  AMF   ─ CP 5GC
                 ──N3 (GTP-U)──►  UPF-A ─ UP 5GC (N6 → dn → internet)
UERANSIM nr-ue   ──NAS / RRC──►  (interno ao nr-gnb)
                                   └─► uesimtun0 (TUN 10.60.0.x)
```

Il n'y a ni agent E2 ni Near-RT RIC dans le Projet 1. Les tests de débit et de
canal simulé via `tc netem` sur `uesimtun0` sont l'équivalent pratique de ce qui
serait mesuré via E2SM-KPM `DRB.UEThpDl/Ul` dans un environnement avec un RIC réel.

### Comment le Projet 2 (OAI + FlexRIC) ajoute le Near-RT RIC

OAI `nr-softmodem` en mode RFSIM implémente la stack RAN complète (PHY/MAC/
RLC/PDCP/RRC) **avec un agent E2 embarqué** (bibliothèque `openair2/E2AP/`). Le
Split 7.2 est supporté via F1/eCPRI, mais dans l'environnement de ce projet il tourne en
mode monolithique avec RFSIM (radio 100 % logicielle, sans matériel SDR).

```
OAI nr-softmodem (RFSIM)
  ├── CU-CP: RRC, PDCP-C
  ├── CU-UP: PDCP-U
  ├── DU:    RLC, MAC, PHY-Hi (simulado)
  ├── RU:    PHY-Low (RFSIM — sem hardware)
  └── E2 Agent ──E2AP──► FlexRIC (Near-RT RIC)
                              ├── xApp KPM: subscreve DRB.UEThpDl/Ul
                              └── xApp RC:  controla parâmetros RRC
```

**KPM pertinents pour le thème UE-TP-rApp (E2SM-KPM) :**

| KPM | Description | Granularité |
|---|---|---|
| `DRB.UEThpDl` | Débit DL par DRB par UE (kbps) | par UE |
| `DRB.UEThpUl` | Débit UL par DRB par UE (kbps) | par UE |
| `RRU.PrbTotDl` | PRBs utilisés en DL (%) | par cellule |
| `RRU.PrbTotUl` | PRBs utilisés en UL (%) | par cellule |
| `L1M.RS-SINR` | SINR mesuré à la couche physique | par UE |

### Où se trouve chaque conteneur Docker dans le modèle O-RAN

| Conteneur | Couche O-RAN | Interface exposée |
|---|---|---|
| `nr-gnb` / `nr-ue` (UERANSIM) | O-gNB monolithique (sans E2) + UE | N2, N3, NAS |
| OAI `nr-softmodem` (Proj.2) | O-gNB avec agent E2 | N2, N3, E2 |
| `flexric` (Proj.2) | Near-RT RIC | E2, A1 |
| `amf` | 5GC CP — terminaison N2 | N2 (NGAP), N11 |
| `smf` | 5GC CP — session management | N4 (PFCP), N11 |
| `upf-a/b` | 5GC UP — user plane | N3 (GTP-U), N6 |
| `ausf` | 5GC CP — auth 5G-AKA | Nausf (SBI) |
| `udm` | 5GC CP — subscriber data | Nudm (SBI) |
| `udr` | 5GC CP — data repository | Nudr (SBI) |
| `pcf` | 5GC CP — policy (AM/SM) | Npcf (SBI) |
| `nrf` | 5GC CP — NF discovery | Nnrf (SBI) |
| `bsf` | 5GC CP — binding support | Nbsf (SBI) |
| `nssf` | 5GC CP — slice selection | Nnssf (SBI) |
| `scp` | 5GC CP — SBI proxy | SBI indirect |
| `mongodb` | Backend de stockage | — (Nudr internal) |

### Flux NAS/RRC d'enregistrement (du point de vue du protocole)

```
UE                  gNB              AMF          AUSF    UDM    SMF    UPF
 │───Registration Req──►│──NGAP Init UE──►│               │      │      │
 │                      │◄──Auth Req──────│──Auth Req────►│      │      │
 │                      │                 │◄──Auth Ans────│      │      │
 │◄──Auth Req───────────│◄──Auth Req──────│               │      │      │
 │──Auth Resp──────────►│──Auth Resp─────►│               │      │      │
 │                      │                 │──Get Sub Data───────►│      │
 │◄──Security Mode Cmd──│◄────────────────│               │      │      │
 │──Security Mode Cmp──►│────────────────►│               │      │      │
 │◄──Reg Accept─────────│◄────────────────│               │      │      │
 │──PDU Session Req────►│────────────────►│──────────────────────►SMF   │
 │                      │                 │                      │──N4──►UPF
 │◄─PDU Session Accept──│◄────────────────│◄─────────────────────│      │
 │ (uesimtun0 UP)       │                 │                      │      │
 │═════════GTP-U sobre N3══════════════════════════════════════════►    │ N6►internet
```

---

## 3. Structure du dépôt

```
/
├── .env / .env.example        # credenciais de DEPLOY (host, SSH key, DuckDNS) — NUNCA vão pro servidor
├── deploy.sh                  # entrypoint único de deploy
├── core5g-arm64-bible.md      # este arquivo
├── CHANGELOG.md                # histórico cronológico de tudo que foi feito
├── infra/
│   ├── server-bootstrap.sh    # bootstrap idempotente do servidor (Docker, swap, DuckDNS, Caddy, painel)
│   └── core5g-panel.service   # unit systemd do painel server-side (template)
├── docs/
│   ├── labs/                  # guias de aula originais do curso (00–03, INDICE, video_seq_report)
│   └── blueprint-painel-observabilidade.md  # desenho do painel explicativo (não implementado)
├── pdfs/                      # slides das aulas (01–04) + planilha de grupos
├── ssl/
│   └── core5g_openran_arm64.pem   # chave SSH privada do servidor
├── client/                    # painel de controle web LOCAL (não roda no servidor)
│   ├── server.py              # backend FastAPI — só chama deploy.sh e streama saída
│   ├── static/index.html      # UI (HTML/CSS/JS puro, sem build step)
│   └── run.sh                 # cria venv, instala deps, sobe em :8765
└── server/                    # TUDO que é replicado/roda na máquina AWS
    ├── docker-compose.yml     # Projeto 1 (Open5GS) — name: open5gs-containerized fixo
    ├── .env / .env.example    # variáveis de IMAGEM do compose (sem segredos)
    ├── configs/open5gs/       # YAML de cada NF (amf.yaml, smf.yaml, bsf.yaml, ...)
    ├── scripts/                # up_core.sh, up_ran.sh, down.sh, healthcheck.sh, add-subscriber.sh, ...
    ├── overrides/
    ├── ueransim/               # docker-compose.yaml separado (gNB+UE simulados)
    ├── logs/                   # bind mounts de log por NF (gerado em runtime)
    ├── panel/                  # painel de controle web SERVER-SIDE (roda na própria AWS)
    │   ├── server.py           # bootstrap FastAPI (auth + cours en direct) — couches core/ops/lab.py
    │   ├── static/{ops,lab}/   # UI à deux couches : opérations (index/topologie) × leçons du lab
    │   ├── requirements.txt
    │   └── .venv/              # criado pelo bootstrap, não versionado
    └── oai-cn-gnb-e2/          # Projeto 2 — OAI 5GC + gNB + FlexRIC + xApps
```

### Pourquoi cette séparation

- **Racine** = outils d'orchestration locale (ne tournent jamais sur le serveur).
- **`server/`** = miroir exact de ce qui existe et tourne sur l'instance AWS.
- **`docs/`** = documentation pure, sans aucun fichier exécutable/config.
- Le `.env` a été délibérément **divisé en deux** : celui de la racine contient
  `AWS_SERVER_HOST`/`AWS_SERVER_USER`/`AWS_SSH_KEY_PATH`/`DUCKDNS_DOMAIN`/`DUCKDNS_TOKEN`
  (seulement pour que `deploy.sh` l'utilise localement) ; celui de `server/.env` ne contient que
  `OPEN5GS_IMAGE`/`WEBUI_IMAGE`/`MONGODB_IMAGE`/`UERANSIM_IMAGE`/`DN_IMAGE`
  (ce dont le `docker-compose.yml` a besoin *sur le serveur*). Ainsi aucun secret
  d'accès n'est envoyé au serveur via `rsync`.

---

## 4. Le serveur (AWS EC2 ARM)

| Élément | Valeur |
|---|---|
| Hostname | `core5g-arm64.duckdns.org` (DDNS — l'IP publique est dynamique) |
| IP d'origine (historique) | `3.145.40.200` — **ne jamais coder en dur**, toujours utiliser le hostname |
| Utilisateur | `ubuntu` |
| Clé SSH | `ssl/core5g_openran_arm64.pem` (Ed25519) |
| Type d'instance | **AWS EC2 `t4g.medium`** (Graviton2 / Neoverse-N1, `aarch64`) — 2 vCPU / 4 GB. (C'était `t4g.micro` au début du projet ; upgrade confirmé par `free` le 2026-06-22.) |
| Région AWS | `us-east-2` |
| OS | Ubuntu 24.04.4 LTS (`noble`), kernel `6.17.0-1017-aws`, `aarch64` |
| CPU | 2 vCPUs — `Neoverse-N1` (ARM Graviton2) |
| RAM | ~3,8 GiB (3825 MiB mesurés — `t4g.medium`) |
| Swap | 8 GiB dans `/swapfile`, `vm.swappiness=10`, persistant via `/etc/fstab` |
| Disque | ~29 GB au total |
| Docker | `29.6.0` (paquets `docker-ce`/`docker-ce-cli`/`containerd.io` architecture `arm64`, dépôt officiel Docker) |
| Docker Compose | `v5.1.4` (plugin) |

### Coûts et hygiène de disque

Les règles, valeurs et le runbook d'upgrade de CPU (le lab de RIC avec IA a besoin de
4 vCPU) vivent dans [`docs/POLITICA-DE-CUSTOS.md`](../../POLITICA-DE-CUSTOS.md).
Leçons permanentes du nettoyage du 2026-07-03 (le disque est descendu à 8 % libre ; est revenu
à 8,6 GB libres) :

- Le mysql du core P2 créait **un volume anonyme d'environ 197 Mo à chaque redémarrage**
  (nous en avons trouvé 16 orphelins = 3,1 GB). Corrigé à la racine : volume nommé
  `mysql-data` dans `oai-cn5g-v2/docker-compose-basic-nrf.yaml` — du coup les
  inscriptions d'UE se sont mises à persister entre les redémarrages.
- `docker volume prune -f` supprime **seulement les anonymes** (Docker ≥23) — les nommés
  (MongoDB des élèves) restent. Malgré tout : inspecter avant d'élaguer.
- Les images OAI **custom** (arm64 buildées, `oai-upf-vpp` porté) ne sont pas
  re-tirables — **ne jamais** les supprimer sans backup/évaluation. Les officielles v1.5.1 +
  `mysql:8.0` (legacy, ~2,6 GB) ont été supprimées après évaluation le 2026-07-03.

### Accès manuel (seulement pour le debug — préférer `./deploy.sh ssh`)

```bash
ssh -i ssl/core5g_openran_arm64.pem ubuntu@core5g-arm64.duckdns.org
```

### DuckDNS (IP dynamique)

- Domaine : `core5g-arm64.duckdns.org`.
- Token : stocké dans `.env` (`DUCKDNS_TOKEN`) — non dupliqué ici.
- Script `~/duckdns/duck.sh` sur le serveur + cron `*/5 * * * *` maintenant
  l'enregistrement à jour. Réinstallable/idempotent via
  `./deploy.sh bootstrap`.

### Docker

Installé via le **dépôt officiel Docker** (pas le paquet `docker.io` d'
Ubuntu) : `docker-ce`, `docker-ce-cli`, `containerd.io`,
`docker-buildx-plugin`, `docker-compose-plugin`. L'utilisateur `ubuntu` dans le groupe
`docker`. Tout est encapsulé dans `infra/server-bootstrap.sh`, idempotent.

---

## 5. Le flux de travail : tout en local, déploiement via `deploy.sh`

**Règle d'or :** ne jamais rien éditer directement sur le serveur via SSH manuel. Le
flux est toujours : éditer les fichiers dans `server/` (ou `infra/`) localement →
`./deploy.sh <comando>`.

```bash
./deploy.sh bootstrap          # instala Docker + swap + DuckDNS no servidor (idempotente)
./deploy.sh sync               # envia server/{docker-compose.yml,.env,configs,scripts,overrides,ueransim}
./deploy.sh sync-oai           # envia server/oai-cn-gnb-e2/ (~230MB, só quando precisar)
./deploy.sh up core             # sync + sobe só o core Open5GS
./deploy.sh up ran              # sync + sobe o RAN (UERANSIM)
./deploy.sh up all              # sync + sobe core + RAN
./deploy.sh down [core|ran|all]
./deploy.sh status              # docker compose ps + healthcheck.sh no servidor
./deploy.sh panel               # envia server/panel/ + roda bootstrap (Caddy + venv + systemd)
./deploy.sh ssh                 # sessão interativa (só debug)
```

`deploy.sh` lit `AWS_SERVER_HOST`/`AWS_SERVER_USER`/`AWS_SSH_KEY_PATH` du
`.env` de la racine — c'est pourquoi il n'y a jamais d'IP/hostname codé en dur dans le script.

### Tableau de bord visuel (`client/`)

Pour qui préfère cliquer sur un bouton plutôt que le terminal : un tableau de bord web qui tourne
**sur votre poste local** (pas sur le serveur) avec un bouton par commande de
`deploy.sh` et une console avec sortie en temps réel.

```bash
cd client && ./run.sh        # cria venv, instala deps, sobe em http://127.0.0.1:8765
```

- Le backend (`client/server.py`, FastAPI) fait seulement un `subprocess.Popen` de
  `deploy.sh` et streame stdout/stderr vers le navigateur — aucune logique de
  SSH/rsync dupliquée, `deploy.sh` reste la seule source de vérité.
- Les commandes exposées sont une liste fixe (`bootstrap`, `sync`, `sync-oai`,
  `up`/`down core|ran|all`, `status`) — le backend n'accepte pas de chaîne libre
  venant du navigateur.
- Bind uniquement sur `127.0.0.1`, sans authentification — suppose un usage local de
  développement, pas une exposition en réseau.
- C'est le premier échelon du tableau de bord plus grand décrit dans
  `docs/blueprint-painel-observabilidade.md` (qui prévoit des logs filtrables et
  une visualisation du flux de protocole en temps réel) — cette version ne fait encore que
  déclencher des commandes et montrer la sortie brute, sans parsing/filtres.

### Tableau de bord web sur le serveur (`server/panel/`), avec HTTPS + login

Version du tableau de bord accessible de n'importe où (pas seulement de votre poste),
publiée sur `https://core5g-arm64.duckdns.org/` avec utilisateur/mot de passe.

- Tourne **directement sur l'instance AWS** — `server/panel/server.py` (FastAPI)
  appelle les scripts locaux (`./scripts/up.sh`, `up_ran.sh`, `down_core.sh`,
  `down_ran.sh`, `healthcheck.sh`) sans aucun SSH impliqué. Bind uniquement sur
  `127.0.0.1:8765` — jamais exposé directement sur internet.
- **HTTPS automatique via Caddy** : `infra/server-bootstrap.sh` installe
  Caddy (dépôt officiel Cloudsmith) et génère `/etc/caddy/Caddyfile` devant
  le tableau de bord. Caddy obtient/renouvelle tout seul un certificat **Let's
  Encrypt gratuit** pour `core5g-arm64.duckdns.org` — il n'y a pas de certificat
  manuel à installer. Seul prérequis externe : les ports **80** (challenge
  ACME HTTP-01) et **443** (HTTPS) doivent être ouverts dans le Security Group
  de l'instance — **déjà ouverts et validés** (HTTP 308 → HTTPS, HTTPS 401 sans
  identifiant, 200 avec login, 403 pour le guest sur `/api/run/*`).
- **Login avec deux rôles**, via le `basic_auth` de Caddy lui-même (hash bcrypt
  généré avec `caddy hash-password`, jamais de mot de passe en clair sur le serveur) :
  - **admin** (`PANEL_USER`/`PANEL_PASSWORD` dans le `.env` de la racine) : accès
    total, exécute n'importe quelle commande.
  - **guest** (`PANEL_GUEST_USER`/`PANEL_GUEST_PASSWORD`) : visualise seulement —
    `server.py` refuse avec HTTP 403 tout `POST /api/run/*` venant de cet
    utilisateur (vérification côté backend, pas seulement un bouton caché dans le front-end). Le
    Caddy injecte `header_up X-Remote-User {http.auth.user.id}` pour que FastAPI
    sache qui s'est authentifié.
- **Processus persistant** : `infra/core5g-panel.service` (systemd,
  `Restart=always`, lance l'`uvicorn` du venv dans `server/panel/.venv`).
  Installé/mis à jour par le bootstrap.
- **Déploiement** : `./deploy.sh panel` synchronise `server/panel/` et lance le
  bootstrap (idempotent) — seul chemin pour mettre à jour le tableau de bord ou les
  identifiants (ne jamais rien éditer via SSH manuel sur le serveur, même règle
  d'or que le §5).
- **Télémétrie en temps réel** (`GET /api/telemetry`) : flux infini
  (NDJSON, une ligne de JSON toutes les 2s) avec RAM/swap/disque/load de l'hôte
  (lus depuis `/proc/meminfo` + `shutil.disk_usage` + `os.getloadavg()`,
  sans nouvelle dépendance) et CPU%/RAM par conteneur (`docker stats
  --no-stream --format '{{json .}}'`). Rendu dans l'UI sous forme de barres +
  tableau repliable, sans Prometheus/Grafana — l'instance n'a que 906 MiB
  de RAM, une stack d'observabilité lourde ne rentre pas de son côté.
- **Filtre de logs par service** (`GET /api/logs/{service}`) : liste de
  services découverte au runtime via `docker compose config --services`
  (dans les deux fichiers compose — core et `ueransim/`), puis `docker compose
  logs -f --tail 200 <service>` streamé vers la console de l'UI.
- **La télémétrie et les logs sont autorisés au guest** (ce sont de la lecture, pas de
  l'exécution) — seul `POST /api/run/*` renvoie un 403 à cet utilisateur.

---

## 6. Open5GS (Projet 1) — ce que fait chaque service

Tous les NFs (Network Functions) ci-dessous sont des rôles standardisés par le 3GPP.
Open5GS et OAI implémentent les mêmes rôles, seulement avec des binaires différents.

| Service | Interface principale | Rôle |
|---|---|---|
| `nrf` | SBI interne | « DNS » du core — chaque NF s'enregistre ici pour que les autres le trouvent |
| `scp` | SBI interne | proxy interne entre NFs (Service Communication Proxy) |
| `amf` | N1 (NAS) / N2 (NGAP) | porte d'entrée de la RAN — authentifie et déplace l'UE |
| `smf` | N4 (PFCP) / N11 | gère les sessions PDU (les « tunnels » de données) |
| `upf-a` / `upf-b` | N3 (GTP-U) / N6 | plan de données réel — failover/répartition de charge entre les deux |
| `ausf` | SBI interne | exécute l'authentification 5G-AKA |
| `udm` | SBI interne | profil de l'abonné (slice, clés de sécurité) |
| `udr` | SBI interne | base derrière l'UDM/PCF (backend MongoDB) |
| `pcf` | SBI interne (Npcf) | décide les règles de QoS/politique de session |
| `bsf` | SBI interne (Nbsf) | enregistre le *binding* PCF↔session pour la découverte par d'autres NFs (ex. : NEF/AF). **Élément manquant dans le projet original — voir §8.** |
| `nssf` | SBI interne | choisit le bon slice (S-NSSAI) pour l'UE |
| `webui` | HTTP :9999 | panneau admin d'Open5GS pour inscrire les abonnés |
| `mongodb` | — | base de données (subscribers, etc.) |
| `dn` | N6 | « internet » factice (alpine) juste pour que l'UPF ait où router/NAT |

**Détail pédagogique important :** chaque réseau docker dans le `docker-compose.yml`
(`net-n2`, `net-n3`, `net-n4`, `net-n6`, `net-sbi`) correspond 1:1 à une
interface 3GPP réelle — filtrer par réseau = filtrer par interface.

### RAN simulé (UERANSIM, dans `server/ueransim/`)

- `nr-gnb` : simule la station de base — parle N2/N3 avec le core.
- `nr-ue` : simule le téléphone — enregistrement NAS, ouvre la session PDU, expose
  l'interface `uesimtun0` pour tester la connectivité de bout en bout.

---

## 7. OAI + FlexRIC (Projet 2) — ce que fait chaque pièce

Dans `server/oai-cn-gnb-e2/` :

- **OAI 5GC** (`oai-cn5g-fed/`) : mêmes rôles de NF qu'Open5GS, mais
  empaquetés par OpenAirInterface, avec l'UPF en **VPP** (dataplane plus
  rapide) au lieu de l'UPF simple.
- **gNB OAI** (`nr-softmodem`, mode **RFSIM** — radio 100 % logicielle) : PHY/MAC/
  RLC/PDCP/RRC réels (pas simulés comme dans UERANSIM), avec un **agent E2
  embarqué** qui annonce les « RAN functions » (KPM = métriques, RC = contrôle, +
  SMs custom L2/L3) au near-RT RIC.
- **FlexRIC** (near-RT RIC) : reçoit l'E2 SETUP du gNB, enregistre les RAN
  functions disponibles, route SUBSCRIPTION/INDICATION/CONTROL entre le gNB
  et les xApps.
- **xApps** (`xapp_kpm_moni`, `xapp_kpm_rc`) : applications qui consomment réellement
  les métriques (KPM) ou les événements RRC (RC) via E2 — le « côté intelligent »
  du RIC.

Flux de démarrage documenté dans
`server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md` : Core → RIC → gNB → xApp.

### 7.a Projet 1 vs. Projet 2 — en quoi ils diffèrent exactement

Les deux implémentent un réseau 5G de bout en bout, mais à des points opposés du
spectre « simple et validé » ↔ « complexe et fidèle à l'O-RAN » :

| Aspect | Projet 1 (Open5GS + UERANSIM) | Projet 2 (OAI + FlexRIC) |
|---|---|---|
| Core 5G | Open5GS (images prêtes, `gradiant/open5gs`) | OAI CN5G (`oai-cn5g-fed/`), UPF en VPP |
| RAN | UERANSIM — gNB/UE **simulés en logiciel**, sans PHY/MAC réels | gNB OAI `nr-softmodem` en **RFSIM** — PHY/MAC/RLC/PDCP/RRC réels, radio 100 % logicielle (sans matériel RF) |
| Couche de contrôle externe (RIC) | **N'existe pas** — réseau monolithique, sans séparation données/contrôle | **FlexRIC** (near-RT RIC) connecté au gNB via E2AP (port 36421) |
| Intelligence/observabilité | Les scripts du tableau de bord (`tc netem`, `iperf3`) simulent le canal/mesurent le débit de l'extérieur | **xApps** (`xapp_kpm_moni`, `xapp_kpm_rc`) consomment les métriques/contrôlent le gNB depuis l'intérieur de l'architecture, via des Service Models E2 standardisés (KPM v2.03, RC v1.03) + SMs custom (MAC/RLC/PDCP/GTP) |
| Concept 3GPP/O-RAN illustré | Enregistrement NAS, session PDU, QoS, failover d'UPF — « le réseau 5G fonctionne » | Séparation **CU/DU/RIC**, *RAN programmable* : le RIC peut observer (KPM) et agir (RC) sur le gNB en temps quasi-réel — c'est le concept central de l'Open RAN |
| Complexité de build | Images Docker prêtes, juste `docker compose up` | Build C/C++ natif à partir du source (`build_oai`, FlexRIC), lourd en CPU/RAM/disque — il n'y a pas d'image prête pour ARM64 |
| État au 2026-06-18 | Complet, validé E2E (§9), déjà présenté | Build à partir de zéro en cours sur le serveur (voir `CHANGELOG.md` v0.8.0) — rien n'était fonctionnel avant cela, malgré des apparences de progrès antérieur |

En une phrase : le **Projet 1** prouve qu'un réseau 5G basique fonctionne de bout
en bout ; le **Projet 2** ajoute la couche de **RAN intelligente et
programmable** (RIC + xApps parlant E2 avec le gNB) qui est la définition
même de l'O-RAN — et c'est techniquement plus lourd parce qu'il n'y a pas d'image
Docker prête : tout est compilé à partir du source, natif `aarch64`.

### 7.b Build des images OAI 5G Core pour arm64

Les images Docker de l'OAI 5G Core (`oaisoftwarealliance/oai-{amf,smf,nrf,udr,udm,ausf,upf-vpp}:v1.5.1`) sur le Docker Hub sont **amd64-only** — il n'y a pas de variante `linux/arm64/v8`. Le serveur AWS t4g.micro (Graviton2, `aarch64`) n'a pas QEMU/binfmt-misc configuré, donc toute tentative de faire tourner ces images échoue avec `exec /usr/bin/python3: exec format error` et le conteneur sort avec le code 255.

#### Stratégie adoptée

Builder nativement pour arm64 sur le Mac Apple Silicon (Docker Desktop avec engine `linux/arm64`), exporter en `.tar`, transférer via `scp` et charger sur le serveur avec `docker load`. Les Dockerfiles sont vendorisés dans le dépôt sous `server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-*/docker/Dockerfile.*.ubuntu`.

Script : [`build-oai-arm64.sh`](../../../build-oai-arm64.sh) à la racine du dépôt.

```bash
./build-oai-arm64.sh build    # compila as 6 imagens localmente no Mac
./build-oai-arm64.sh save     # exporta para /tmp/oai-images/*.tar
./build-oai-arm64.sh upload   # scp dos .tar para o servidor
./build-oai-arm64.sh load     # docker load no servidor + rm dos .tar
./build-oai-arm64.sh all      # executa os 4 passos em sequência
```

#### Prérequis

| Prérequis | Détail |
|---|---|
| Machine | Mac Apple Silicon (M1/M2/M3/M4) — arm64 natif |
| Docker Desktop | ≥ 4.x avec engine `linux/arm64` activée |
| Espace disque | ≥ 20 GB libres (images intermédiaires + .tar exportés) |
| Temps | ~40 min par image × 6 = ~4 h au total |
| SSH key | `ssl/core5g_openran_arm64.pem` avec accès au serveur |
| `.env` | configuré avec `AWS_SERVER_HOST`, `AWS_SERVER_USER`, `AWS_SSH_KEY_PATH` |

> **Pourquoi Mac Apple Silicon ?** Docker Desktop sur M-series fait tourner les conteneurs `linux/arm64` _nativement_ — sans émulation QEMU. Compiler l'OAI (C++ lourd) via émulation prendrait 5–10× plus de temps et bloque fréquemment par OOM.

#### Comment compiler — pas à pas

**1. Cloner le dépôt et configurer le .env**

```bash
git clone https://github.com/henriquecarmine/Core5G_ARM64.git
cd Core5G_ARM64
cp .env.example .env
# editar .env: AWS_SERVER_HOST, AWS_SERVER_USER, AWS_SSH_KEY_PATH
```

**2. Compiler les 6 images**

```bash
./build-oai-arm64.sh build
# Cada docker build compila o OAI a partir do source dentro do container arm64.
# A ordem importa: AMF → SMF → NRF → UDR → UDM → AUSF
# Cache Docker é reutilizado em recompilações parciais.
```

Ce qui se passe à l'intérieur de chaque build (Dockerfile multi-stage) :
1. **base stage** — `apt-get install` des dépendances système + build tools
2. **base stage** — compilation de spdlog, Pistache, nlohmann/json et nghttp2 à partir du git
3. **builder stage** — `cmake` configure le projet + `make -j$(nproc)` compile le binaire
4. **target stage** — copie seulement le binaire et les `.so` nécessaires pour l'image finale minimale

**3. Exporter en .tar**

```bash
./build-oai-arm64.sh save
# Cria /tmp/oai-images/oai-{amf,smf,nrf,udr,udm,ausf}.tar (~60 MB cada)
```

**4. Envoyer au serveur**

```bash
./build-oai-arm64.sh upload
# scp de cada .tar para ~/ no servidor via SSH
```

**5. Charger dans le daemon Docker du serveur**

```bash
./build-oai-arm64.sh load
# docker load -i ~/oai-{comp}.tar && rm ~/oai-{comp}.tar  (para cada componente)
```

**Ou tout d'un coup :**

```bash
./build-oai-arm64.sh all
```

**Vérifier que les images sont réellement arm64 :**

```bash
# no servidor:
docker run --rm oaisoftwarealliance/oai-amf:v1.5.1 uname -m
# esperado: aarch64
```

#### Paramètres du build

| Paramètre | Valeur |
|---|---|
| `--platform` | `linux/arm64` |
| `--build-arg BASE_IMAGE` | `ubuntu:focal` (voir §8.5) |
| `--target` | nom du composant (ex. : `oai-amf`) |
| `-f` | `component/<comp>/docker/Dockerfile.<shortname>.ubuntu` |
| contexte | répertoire du composant (ex. : `component/oai-amf/`) |

#### Problèmes rencontrés — et comment ils ont été corrigés

Ce sont les erreurs qui apparaissent en essayant de compiler les images OAI pour arm64 **à partir du code original du dépôt**. Les patchs sont déjà appliqués dans ce dépôt ; cette section existe pour documenter le raisonnement et aider qui essaierait de faire de même sur une autre base de code.

**Bug 1 — `declare -A` non supporté dans le bash 3.2 de macOS**

macOS 14/15 est livré avec bash 3.2 (limitation de licence GPLv2). Le script original utilisait `declare -A COMPONENTS=(...)` (bash 4+), causant `oai: unbound variable` à l'exécution.

Correction : remplacé par une simple chaîne itérée avec `for comp in $COMPONENTS` :
```bash
COMPONENTS="oai-amf oai-smf oai-nrf oai-udr oai-udm oai-ausf"
# oai-upf-vpp excluído: requer libhyperscan (Intel-only, inexistente no arm64)
for comp in $COMPONENTS; do ...
```

**Bug 2 — Nom incorrect du Dockerfile**

Le Dockerfile s'appelle `Dockerfile.amf.ubuntu` (sans le préfixe `oai-`), pas `Dockerfile.oai-amf.ubuntu`. Le script générait le nom incorrect, causant « Dockerfile non trouvé » pour les 7 composants.

Correction : ajout de `shortname="${comp#oai-}"` pour retirer le préfixe avant de monter le chemin :
```bash
shortname="${comp#oai-}"   # oai-amf → amf
dockerfile="$ctx/docker/Dockerfile.${shortname}.ubuntu"
```

**Bug 3 — `libboost1.67-dev` non disponible dans le dépôt arm64 d'Ubuntu 18.04**

Le `build_helper.amf` (et les équivalents de chaque composant) pour `ubuntu18.04` ajoute le PPA `ppa:mhier/libboost-latest` et installe `libboost1.67-dev`. Ce PPA ne publie pas de paquets arm64 — l'`apt-get install` échoue avec `E: Unable to locate package libboost1.67-dev`, et le build avorte avec « AMF deps installation failed ».

Correction : passer `--build-arg BASE_IMAGE=ubuntu:focal`. Ubuntu 20.04 a Boost 1.71 dans les dépôts par défaut ; le `build_helper` a un case spécifique `ubuntu20.04` qui installe `libboost-all-dev` directement, sans PPA. Le Dockerfile supporte bionic, focal et jammy explicitement — utiliser focal est le chemin supporté.

**Bug 4 — `-msse4.2` codé en dur dans le CMakeLists.txt de tous les composants**

Après avoir résolu le Bug 3, la compilation échoue avec `cc: error: unrecognized command line option '-msse4.2'`. Le bloc de détection d'architecture dans chaque `src/*/CMakeLists.txt` a :

```cmake
if (CMAKE_SYSTEM_PROCESSOR STREQUAL "armv7l")
  set(C_FLAGS_PROCESSOR "-gdwarf-2 -mfloat-abi=hard -mfpu=neon -lgcc -lrt")
else (CMAKE_SYSTEM_PROCESSOR STREQUAL "armv7l")  # ← else genérico
  set(C_FLAGS_PROCESSOR "-msse4.2")              # ← flag x86 SSE4.2
endif()
```

Dans le build `linux/arm64`, `CMAKE_SYSTEM_PROCESSOR` est `aarch64` — tombe dans le `else` et tente de compiler avec `-msse4.2` (instruction x86 SIMD qui n'existe pas en ARM).

Correction appliquée dans les 5 composants affectés (`oai-amf`, `oai-smf`, `oai-nrf`, `oai-udr`, `oai-udm`, `oai-ausf`) :

```cmake
if (CMAKE_SYSTEM_PROCESSOR STREQUAL "armv7l")
  set(C_FLAGS_PROCESSOR "-gdwarf-2 -mfloat-abi=hard -mfpu=neon -lgcc -lrt")
elseif (CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|arm64")
  set(C_FLAGS_PROCESSOR "")   # ← ARM64 nativo, sem flags arquitetura-específicas
else()
  set(C_FLAGS_PROCESSOR "-msse4.2")
endif()
```

L'`oai-upf-vpp` utilise VPP avec un système de build propre et n'a pas cette flag.

**Bug 5 — `libasan2` invalide dans `build_helper.udm` fait taire l'`apt-get` entier**

Le `build_helper.udm` avait `libasan2` dans le `PACKAGE_LIST` ubuntu (ligne qui n'est pas présente dans les autres composants). `libasan2` n'existe pas dans Ubuntu 20.04 arm64 (`libasan5` est la version correcte, déjà incluse dans `specific_packages`). L'`apt-get install -y` échoue entièrement avec `E: Unable to locate package libasan2` — mais l'erreur est passée sous silence parce que le `ret=$?` suivant capture le code de sortie du bloc `if/case` (qui retourne 0 pour ubuntu20.04), pas de l'`apt-get`. Résultat : aucun paquet du `PACKAGE_LIST` n'est installé, y compris `libconfig++-dev`. Le cmake échoue alors avec `None of the required 'libconfig++' found`.

Correction : retirer la ligne `libasan2` (et le `libasan` générique qui n'existe pas non plus) du `PACKAGE_LIST` ubuntu dans `build_helper.udm`. Le `libasan5` est déjà dans `specific_packages` pour ubuntu20.04.

Fichier affecté : `server/.../oai-udm/build/scripts/build_helper.udm`

**`oai-upf-vpp` en arm64 — RÉSOLU avec Vectorscan (2026-06-21)**

Pendant longtemps l'`oai-upf-vpp` a été considéré comme « non portable » vers arm64. Le
diagnostic réel, en investiguant la source : le blocage était **une seule dépendance**
— le **Hyperscan** (`libhyperscan-dev`), bibliothèque de regex SIMD d'Intel
(SSE/AVX), inexistante dans Ubuntu arm64. Le plugin UPF de Travelping l'exige via
`pkg_check_modules(HS libhs)` (pkg-config pur).

La solution : le **[Vectorscan](https://github.com/VectorCamp/vectorscan)** est un fork
portable du Hyperscan — ARM NEON 100 % fonctionnel, **API/ABI-compatible**, même
SONAME `libhs.so.5`. C'est du **drop-in** : en compilant le Vectorscan et en l'installant, le
`pkg_check_modules(HS libhs)` le trouve et le GTP UPF est activé normalement
(`Found libhs, version 5.4.12`). Les autres « blocages » cités auparavant ne se sont pas
confirmés — le VPP 2101 **core n'utilise pas hyperscan**, et les chemins de lib étaient déjà
corrigés pour `aarch64-linux-gnu` dans le Dockerfile.

Étapes du portage (dans [`docker/Dockerfile.upf-vpp.ubuntu.arm64`](../../../server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-upf-vpp/docker/Dockerfile.upf-vpp.ubuntu.arm64)) :
1. Base `ubuntu:focal` (gcc-9 ; Vectorscan exige C++17/gcc≥9) + `cmake` récent
   via pip (focal a 3.16 ; Vectorscan demande ≥3.18.4).
2. Compiler le Vectorscan en retirant `-Werror` (gcc-9 donne un faux positif dans
   `state_compress.c` + la flag `-Wno-stringop-overread` n'existe que dans gcc-11) et
   en désactivant les extras (`BUILD_UNIT/TOOLS/EXAMPLES/BENCHMARKS/DOC=OFF`).
3. `sed` retirant `dh-systemd` du `DEB_DEPENDS` du VPP (paquet bionic-only qui
   casse le `make install-dep` sur focal ; ne sert qu'à empaqueter des `.deb`).
4. `sed` forçant `https://github.com` dans les URLs des paquets externes du VPP
   (le `rdma-core` téléchargeait par `http://github.com:80` → « connection refused »).
5. Copier le `libhs.so.5` (Vectorscan) dans l'image finale.

Résultat validé : `vpp` ELF **ARM aarch64**, `upf_plugin.so` résout
`libhs.so.5`. **Runtime validé** (docker `--privileged` + hugepages) : le VPP
boote complet et le plugin répond — `show plugins` liste `upf_plugin.so
21.01.1`, `show upf specification release` → `PFCP version: 15`. L'abort qui
apparaissait dans le `flowtable_init` **n'était pas un défaut du portage** : c'était le `main-heap`
adossé aux hugepages sans pages suffisantes ; avec `main-heap-page-size 4k`
(ou des hugepages dimensionnées) il monte normalement. **Piège opérationnel pour qui déploiera :**
n'adossez pas le main-heap avec plus de hugepages que l'hôte n'en a de libres — utilisez 4k ou
réservez des hugepages suffisantes (heap + buffers). Image dans
`artifacts/oai-images/oai-upf-vpp.tar` (~138 MB).

**Validation sur le Graviton réel (serveur AWS, 2026-06-22).** Image chargée sur le
serveur (`docker load`, arch=arm64) et lancée en standalone avec le box **au repos**
(`--cpus=1.5`, heap 2G/4k). Test **event-driven** (readiness par état : le socket
CLI existe OU le processus meurt — sans sleep/timeout fixe) avec **métriques réelles** :

| Check | Valeur mesurée sur le Graviton |
|---|---|
| `docker stats` | cpu 2,23% · mem 1,41 GiB / 3,74 GiB (37,8%) · 1 pid |
| `show version` | `vpp v21.01.1` (ARM) |
| `show plugins` | `upf_plugin.so 21.01.1` |
| `show upf specification release` | `PFCP version: 15` |
| `show memory main-heap` | total 1,99G · **usado 1,08G** · livre 938M |
| `show buffers` | pool `default-numa-0` 17.240 buffers |
| `upf_plugin.so` | lie à `libhs.so.5` (vectorscan) |

L'**usage réel du heap (1,08 GB)** explique pourquoi 1G échoue et 2G suffit : le flowtable
du plugin pré-alloue ~1 GB (défaut de compilation, sans `init.conf` dimensionnant).
Le conteneur s'est **auto-terminé** et a été retiré ; le load de l'hôte 0,3 → 1,0 (trivial).

> **Leçon apprise (enregistrée pour ne pas répéter) :** faire tourner VPP sur le box **pendant que le
> lab P2 est actif** (load ~30 sur les 2 vCPUs) avec un harness qui **ne
> s'auto-termine pas** a étouffé le `sshd` et a exigé un reboot. Règle : les tests de VPP sur le serveur
> seulement avec le box **au repos**, conteneur **`--rm` + auto-terminaison**, et attente d'un
> **état/événement** (jamais de timeout aveugle). Voir [[feedback-event-driven-nao-tempo]].

Il ne manque que l'**E2E complet** (session PFCP du SMF + GTP-U du gNB + trafic d'UE),
qui exige le core+RAN entier et une fenêtre sans cours — et le lab n'en dépend pas.

> Le lab principal continue d'utiliser l'UPF d'Open5GS (`open5gs-upfd`, P1) et le
> `oai-upf` simple_switch (P2, core v2.2.1) — ne dépend pas de cette image. Le portage
> existe par le principe Open RAN (« toute technologie O-RAN doit être ouverte ») et est
> candidat à un report upstream vers l'OAI.

#### Résultat — builds terminés le 2026-06-19

Compilation réalisée sur le Mac Apple Silicon (M-series) via Docker Desktop `linux/arm64`. Temps total : ~40 min par image (base stage + build from source + cmake + make). Images chargées sur le serveur AWS t4g.micro (Graviton2, Ohio) et vérifiées avec `uname -m → aarch64`.

| Image                          | Tag    | Taille  | Build SHA (digest)                                        |
|-------------------------------|--------|---------|-----------------------------------------------------------|
| oaisoftwarealliance/oai-amf   | v1.5.1 | 280 MB  | `sha256:404e88009215...` |
| oaisoftwarealliance/oai-smf   | v1.5.1 | 260 MB  | `sha256:90d5058e53c6...` |
| oaisoftwarealliance/oai-nrf   | v1.5.1 | 264 MB  | `sha256:49528805e9ae...` |
| oaisoftwarealliance/oai-udr   | v1.5.1 | 268 MB  | `sha256:3d2cab6d1063...` |
| oaisoftwarealliance/oai-udm   | v1.5.1 | 257 MB  | `sha256:f49f777b6d06...` |
| oaisoftwarealliance/oai-ausf  | v1.5.1 | 255 MB  | `sha256:e7a98d7f0ee8...` |

#### Où sont les fichiers

**Serveur AWS** (destination finale) :
```
# Imagens já carregadas no daemon Docker — prontas para uso:
docker images | grep oaisoftwarealliance
```

**Google Drive du projet** (copie permanente des `.tar`) :
```
PROJETOS/Core5G_ARM64/artifacts/oai-images/
├── oai-amf.tar    (63 MB)
├── oai-smf.tar    (60 MB)
├── oai-nrf.tar    (60 MB)
├── oai-udr.tar    (61 MB)
├── oai-udm.tar    (59 MB)
└── oai-ausf.tar   (59 MB)
# total: ~362 MB  — não versionados no git, ficam no Drive
```

Pour charger sur n'importe quel hôte arm64 sans recompiler :
```bash
# copiar do Drive para o servidor e carregar:
scp -i sua-chave.pem artifacts/oai-images/oai-amf.tar ubuntu@<servidor>:~/
ssh -i sua-chave.pem ubuntu@<servidor> "docker load -i ~/oai-amf.tar && rm ~/oai-amf.tar"
# repetir para cada componente
```

Pour exporter directement depuis le serveur de laboratoire (si vous avez un accès SSH) :
```bash
ssh ubuntu@core5g-arm64.duckdns.org "docker save oaisoftwarealliance/oai-amf:v1.5.1 -o ~/oai-amf.tar"
scp ubuntu@core5g-arm64.duckdns.org:~/oai-amf.tar .
docker load -i oai-amf.tar
```

> Guide complet de téléchargement (sans compiler) : [`OAI-CORE-ARM64.md §Download`](../../../server/oai-cn-gnb-e2/docs/OAI-CORE-ARM64.md)

Pour recompiler à partir de zéro (requiert Mac Apple Silicon + Docker Desktop) :
```bash
git clone https://github.com/henriquecarmine/Core5G_ARM64.git
cd Core5G_ARM64
cp .env.example .env   # preencher AWS_SERVER_HOST e AWS_SSH_KEY_PATH
./build-oai-arm64.sh build   # ~4 h total para os 6 componentes
./build-oai-arm64.sh save    # exporta para /tmp/oai-images/
./build-oai-arm64.sh upload  # scp para o servidor
./build-oai-arm64.sh load    # docker load no servidor
```

**Dockerfiles** avec tous les patchs arm64 appliqués :
```
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/docker/Dockerfile.<comp>.ubuntu
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/build/scripts/build_helper.<comp>
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/src/*/CMakeLists.txt
```

---

### 7.c Plan utilisateur en arm64 (OAI v2.2.1) + xApps event-driven

> **Pourquoi cette section existe.** Le core v1.5.1 que nous avons buildé (§7.b) **n'avait pas d'UPF
> en arm64** (l'`oai-upf-vpp` est Intel-only, dépend de `libhyperscan`). En pratique le
> Projet 2 n'avait que le plan de **contrôle** — l'UE n'obtenait jamais d'IP. L'OAI s'est mis à
> publier des images **multi-arch officielles** à partir du `v2.1.10` ; le **`v2.2.1`** a
> **7/7 NFs avec arm64**, y compris `oai-upf` (datapath `simple_switch`). Nous avons migré vers
> lui et le **user plane s'est mis à fonctionner** (l'UE obtient l'IP `12.1.1.x`, trafic réel).

**Où ça vit :** `server/oai-cn-gnb-e2/oai-cn5g-v2/` (parallèle au v1.5.1, ne le remplace pas).
Détails de config dans [`oai-cn5g-v2/README.md`](../../../server/oai-cn-gnb-e2/oai-cn5g-v2/README.md).
S'accorde avec le gNB actuel : PLMN **208/95**, TAC `0xa000`, slice **SST 222 / SD 123**,
DNN **default** (pool `12.1.1.0/26`), AMF fixe `192.168.70.132`, SNAT sur l'UPF (UE → internet).

**Monter le Projet 2 complet (par SSH) :**
```bash
cd server/oai-cn-gnb-e2
./oai-cn5g-v2/up_core_v2.sh    # para o Projeto 1, sobe o core v2.2.1, espera oai-amf RUNNING
./scripts/up_e2_lab_v2.sh      # near-RT RIC + gNB (RFSIM, 24 PRBs / 51 NRB) + nrUE
```

**Lancer les xApps — event-driven, sans timeout aveugle :**
```bash
./scripts/run_xapp.sh cust    # xApp MAC/RLC/PDCP/GTP (SM custom)
./scripts/run_xapp.sh kpm     # E2SM-KPM (métricas DRB/PRB)
./scripts/run_xapp.sh rc      # E2SM-RC (controle)
./scripts/e2_verify.sh        # sobe o lab + valida E2 SETUP + roda os 3 xApps 7x cada
```
Chaque `run_xapp.sh` **se termine au 1er événement de succès** (E2 connecté + souscrit/indication),
jamais par durée fixe — déterministe. Le prérequis vérifié par **état** (`pgrep -x
nearRT-RIC` + `nr-softmodem`), pas par `sleep`. CPU sous contrôle : cgroup avec `CPUQuota`
(`XAPP_CPU_QUOTA`, défaut `50%`) + `nice`.

#### Validation des xApps (résultat réel) et les 2 bugs qui étaient sur le chemin

En lançant `e2_verify.sh` (monte le lab sans UE + 3 xApps 7× chacun) : **cust 7/7, kpm 7/7, rc 5/7**
— les xApps se connectent au RIC et **souscrivent** les RAN functions (`Successfully subscribed to
RAN_FUNC_ID …`). Avant d'arriver à ce résultat, deux bugs (qui N'étaient PAS un « manque de CPU », comme
cela semblait au début) ont dû être corrigés :

1. **Plugins SM de mauvaise architecture (crash du RIC).** Le dépôt versionnait
   `flexric-lib/*.so` compilés pour **x86-64** ; sur un hôte **arm64** le `dlopen` du
   `nearRT-RIC` échoue (`load_plugin_ric: Assertion handle != NULL`). Pire : `sync-oai`
   répandait ces x86-64 par-dessus les arm64 que le serveur avait buildés. **Correction :**
   les `.so` sont sortis du git (ce sont des artefacts de build, arch-spécifiques ; voir `.gitignore`) et le
   `up_flexric.sh` **détecte maintenant l'architecture** et repeuple `flexric-lib/` depuis le build tree
   (`sync_flexric_lib.sh`) quand il manque OU est d'une autre arch. Auto-réparable.

2. **Faux négatif dans le `run_xapp.sh`.** Il utilisait `tail -F --pid | grep -m1` avec
   `set -o pipefail` : quand le `grep -m1` matche l'événement de succès et ferme le pipe, le `tail`
   meurt avec SIGPIPE et le `pipefail` marquait tout le pipeline comme un échec — rapportant
   `❌ FALHA` même avec le xApp souscrit. **Correction :** remplacé par un **poll sur le fichier**
   (`grep -q` en boucle jusqu'à l'événement OU la mort du processus), sans pipe, sans SIGPIPE.

#### Contrainte opérationnelle du box (2 vCPUs)

Le `nr-softmodem` et le `nr-uesoftmodem` en RFSIM font du **busy-poll** (chacun sature ~1 vCPU →
load > 20), et alors le chemin INDICATION→Report du RIC peut dépasser le timeout interne du
FlexRIC. C'est pourquoi la validation monte **sans le nrUE** (`SKIP_UE=1`, défaut dans `e2_verify.sh`) :
l'E2 est gNB↔RIC et ne dépend pas de l'UE, et il reste 1 vCPU entier pour le RIC+xApp (load < 2). Pour le
lab complet AVEC user plane, montez normalement (`SKIP_UE=0`) — mais ne lancez pas les 7× de xApp en même temps.

**Mesure sur le serveur (2026-06-22) — l'UE attach est mutuellement exclusif avec le guardrail
de cpuset.** Avec le guardrail actif (`oai-lab.slice AllowedCPUs=1` = tout le lab sur un seul
core), le nrUE **se synchronise** (PHY/RFSIM ok : `Initial sync successful, PCI 0`, RSRP 51 dB)
mais le **RRC inonde** (`TASK_RRC_NRUE task contains` 71k→112k) et l'UE **n'obtient pas d'IP** : le gNB
(CPUWeight 60) reste avec ~40 % du core et le nrUE (CPUWeight 20) seulement ~25 % — insuffisant pour le RRC
en temps réel. En libérant les **2 cores** (`AllowedCPUs=0-1`), chaque processus RFSIM gagne ~1
core et le **user plane fonctionne réellement** : l'UE attache, `oaitun_ue1=12.1.1.2`, et
`ping 8.8.8.8` par la tun donne **4/4, 0 % de perte, RTT ~111 ms**. Autrement dit, ce que la §7.c affirme
(l'UE obtient l'IP `12.1.1.x`) **se confirme — mais exige les 2 cores**, ce qui rouvre le risque de
freeze que le guardrail prévient. Trade-off : **soit** protection anti-freeze (1 core, sans UE),
**soit** user plane complet (2 cores, box dédié). Le test a été fait **sans timer** : revert
du cpuset par `trap EXIT` + attente d'événement (`ip monitor` pour l'IP, `tail -F --pid|grep -m1`
pour le flood) + monitor en `nice -20` (garantit le revert même sous saturation).

> **Recommandation pour qui montera une nouvelle instance :** utilisez **4 vCPU** (ex. : `t4g.xlarge`
> ou `c7g.xlarge`). Avec 4 cœurs — gNB sur un, UE sur un autre, RIC+xApp sur un autre, système sur un autre — le
> lab complet **avec user plane** tourne sans cpuset, sans guardrail et sans risque de freeze, et les
> xApps tournent en parallèle de l'UE (essentiel pour l'UE-TP-rApp). Les 2 vCPU sont le **chemin
> alternatif** (trade-off ci-dessus). Guide complet de reproduction jusqu'au user plane, avec les deux
> chemins : [`server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md`](../../../server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md).

> **Principe du projet : ZÉRO temps, tout sous contrôle.** Pas de `sleep`/timeout aveugle —
> les scripts se terminent par **événement/état** (`grep -m1` en stream, `tail -F --pid`, poll de
> condition). Voir la mémoire `feedback-event-driven-nao-tempo`.

---

## 8. Bugs réels rencontrés et corrigés

Ces problèmes existaient dans le matériel original du cours et ont été découverts
en testant réellement sur le serveur ARM — conservés ici pour ne pas se perdre.

### 8.1 — Images `gradiant/open5gs` sans build arm64

`gradiant/open5gs:2.7.6` et `gradiant/open5gs-webui:2.7.6` **n'ont pas** de
manifest `linux/arm64/v8` — à partir de la tag `2.7.3` gradiant ne publie que
`amd64`. `docker compose up` échouait avec
`no matching manifest for linux/arm64/v8`.

**Correction :** fixer dans `server/.env` :
```
OPEN5GS_IMAGE=gradiant/open5gs:2.7.2
WEBUI_IMAGE=gradiant/open5gs-webui:2.7.2
```
(`2.7.0`, `2.7.1` et `2.7.2` sont les dernières tags avec build arm64 confirmé
via l'API Docker Hub. `mongo:7.0` et `gradiant/ueransim:3.2.6` étaient déjà
arm64-ok, sans changement nécessaire.)

### 8.2 — Service BSF absent (PDU Session toujours rejetée)

Après que le core soit monté 100 % healthy, l'UE s'enregistrait (NAS OK) mais la session PDU
échouait toujours avec `PDU Session Establishment Reject [OUT_OF_LADN_SERVICE_AREA]`.

Cause racine (trouvée dans le log du PCF, pas dans celui de l'UE) : `No http.location` dans
`nbsf-handler.c:436` — le PCF tente d'enregistrer le *binding* de la session sur la
**BSF** via NRF, mais :
1. **Il n'y avait pas de service `bsf` dans le `docker-compose.yml`** (bien que le binaire
   `open5gs-bsfd` existe dans l'image).
2. Il existait déjà un `configs/open5gs/bsf.yaml` dans le projet original, mais avec l'
   adresse d'**exemple par défaut** (`127.0.0.15`), hors du schéma de réseau
   réel du projet (`10.10.0.x` sur `net-sbi`).

Autrement dit : élément oublié dans la configuration originale du cours, non causé par le
changement de version d'image (§8.1).

**Correction :**
- `server/configs/open5gs/bsf.yaml` : adresse corrigée en `10.10.0.18`
  (prochaine IP libre), client `scp` pointé vers `10.10.0.200:7777`.
- `server/docker-compose.yml` : nouveau service `bsf` ajouté (même standard
  que le `nssf`), conteneur `open5gs-bsf-containerized`.

Après avoir monté le BSF, une seconde erreur transitoire est encore apparue
(`Registration reject [95]` / `amf_npcf_am_policy_control_handle_create()
failed`) — état orphelin de tentatives de session précédentes. Résolu avec un
restart propre d'`amf`, `smf`, `pcf`, `bsf` (et les autres NFs du core).

### 8.3 — Nom du projet Compose non fixé (risque de perdre des données en déplaçant les dossiers)

Le `docker-compose.yml` n'avait pas de `name:` explicite en haut. Les **réseaux**
(`net-n2`, `net-n3` etc.) avaient déjà un `name:` fixe individuellement, mais les
**volumes nommés** du Mongo (`mongodb-data`, `mongodb-config`) non — leur
nom est dérivé du nom du répertoire où le `docker compose` est
exécuté. En réorganisant le dépôt (déplacer de `open5gs-containerized/` vers
`server/`), cela aurait recréé les volumes de zéro, **perdant le subscriber
inscrit**.

**Correction :** ajout de `name: open5gs-containerized` en haut du
`docker-compose.yml` — tout dossier/répertoire d'exécution futur maintient
les mêmes volumes/réseaux/conteneurs.

> Il vaut la peine d'envisager de reporter les bugs 7.1–7.3 au professeur — d'autres groupes
> utilisant le même matériel original tombent probablement sur les mêmes erreurs.

### 8.4 — Le venv du tableau de bord restait sans `pip` (vérification d'idempotence confondue par un état partiel)

Dans le bootstrap de `server/panel/`, l'étape de création du venv vérifiait
`[ ! -x ~/server/panel/.venv/bin/python3 ]` pour décider s'il fallait le recréer. Lors d'une
première tentative, `python3-venv` n'était pas encore installé quand le
`python3 -m venv` a tourné — l'`ensurepip` a échoué, mais le venv est resté partiellement
créé (seulement les symlinks de `python3`, sans `pip`/`activate`). À l'exécution
suivante, le symlink `python3` existait déjà et *était* exécutable, donc la vérification
d'idempotence considérait que le venv était ok et sautait la recréation — laissant
le `pip install` échouer avec « No such file or directory ».

**Correction :** installer `python3-venv`/`python3-pip` toujours (via `apt-get
install`, qui est déjà idempotent par nature) avant de vérifier/recréer le venv,
au lieu de tenter de déduire si le paquet est déjà installé.

### 8.5 — Rapports avec faux négatif (nom de conteneur ≠ service Compose)

Découverts **en lançant les rapports en direct** (pas au `bash -n`), v0.25.2. Ce sont des
bugs de notre couche de diagnostic, pas du matériel original — mais ils tromperaient le
professeur, donc ils valent l'enregistrement :

- **`test_ng_setup` / `test_registration` disaient « AMF n'est pas en marche »** avec l'
  AMF parfaitement en ligne. Cause : les scripts faisaient `docker inspect amf`, mais
  `amf` est le nom du **service Compose** — le **conteneur** s'appelle
  `open5gs-amf-containerized`. `docker inspect`/`exec`/`logs` exigent le nom du
  **conteneur** ; seul `docker compose logs` accepte le nom du **service**. L'
  `inspect` échouait → le croisement avec l'AMF devenait un avertissement → `test_ng_setup`
  concluait *« N2 non confirmée »* **même avec `NGSetupResponse` reçu**.
- **`test_ue_connection` montrait `IP public <!DOCTYPE html>`.** `wget
  http://ifconfig.me` renvoie la **page HTML**, pas l'IP. Corrigé en
  `http://ifconfig.me/ip` (texte pur) + extraction/validation de l'IP par regex.
- **Verdict final toujours « ok ».** `test_ue_connection` se terminait en `summary ...
  ok` indépendamment des vérifications. Réécrit avec des compteurs `fails`/`warns`
  et un verdict honnête (✗ critique / ! réserve / ✓ tout est passé).

**Leçon :** `bash -n` valide la syntaxe, pas la sémantique. Un rapport nouveau/modifié doit
**tourner en direct** avant le merge. Détails dans
[`docs/relatorios-didaticos.md`](../../relatorios-didaticos.md) §5.

### 8.6 — La démo E2E mesurait le bridge Docker, pas le tunnel 5G

L'étape de débit de la Démonstration E2E (`demo_e2e.sh`) faisait
`iperf3 -c 10.50.0.100` depuis l'intérieur du conteneur de l'UE. Mais le DN
(`open5gs-dn-containerized`, `10.50.0.100`) est sur le **même réseau Docker** où le
conteneur de l'UE a l'`eth0` — donc l'iperf sortait **directement par le bridge Docker, pas
par le tunnel 5G** (`uesimtun0`, pool `10.60.0.0/16`). Résultat : il ne mesurait pas le cœur
et échouait encore par *timing* du serveur `iperf3 -s -1`.

**Correction (v0.25.0) :** créer une **route temporaire vers le DN via `uesimtun0`** et
**lier l'origine à l'IP du tunnel** (`iperf3 -B 10.60.0.x`), forçant le chemin
réel `UE → gNB → UPF (NAT sur N6) → DN` ; la route est retirée à la fin. Validé en
direct : **149 Mbit/s** traversant le cœur 5G (avant : sans mesure). De plus, la
Démo E2E s'est mise à afficher la **commande réelle + sortie réelle + « Pourquoi »** de chaque étape.

---

## 9. Validation de bout en bout (état actuel confirmé)

Testé sur le serveur via `./deploy.sh up core` + `./deploy.sh up ran` :

1. `add-subscriber.sh` inscrit l'IMSI `001010000000002` dans MongoDB.
2. L'UE (UERANSIM) s'enregistre : NG Setup → Authentification 5G-AKA → Security Mode →
   `Initial Registration is successful`.
3. PDU Session Establishment Accept → `uesimtun0` monte avec l'IP `10.60.0.2`.
4. `ping -I uesimtun0 8.8.8.8` → **4/4 paquets, 0 % de perte, RTT ~10ms**.
5. `healthcheck.sh` : NRF healthy, N2/N3/N4/N6 tous OK, association PFCP
   établie, UE en marche avec connectivité active.

**Utilisation des ressources** avec core + RAN complets en marche : ~492 MiB / 906 MiB de
RAM, ~342 MiB de swap, CPU de chaque conteneur en dessous de 2 % (MongoDB le plus
lourd, ~13 % d'un core). **La petite instance soutient le Projet 1
complet avec de la marge.**

Le risque de RAM réel est pour le Projet 2 (le build de l'OAI à partir du source est
CPU/RAM-intensif) — pas encore mesuré, tester avec prudence.

**Vérification en direct de tous les rapports (2026-06-21, v0.25.0–0.25.3) :**
lancés réellement, pas seulement `bash -n`. **Projet 1** — `status`,
`system-status`, `ng-setup`, `registration`, `config-coherence`,
`ue-connection` et `upf-failover` (failover maintenant la connectivité) passent, tous
avec un en-tête de section, des vérifications colorées et un bloc « Résumé » ; 3 bugs de précision
trouvés et corrigés (§8.5). **Projet 2** — `e2-sm` (chaîne O-RAN de bout en bout,
7 souscriptions), `e2-kpm` (souscription OK, verdict honnête « sans trafic sur la
période ») et `e2-rc` (événements RRC de l'attach capturés) passent, sans bugs. La
Démonstration E2E mesure **149 Mbit/s** réels par le tunnel 5G (§8.6).

---

## 10. En attente / prochaines étapes

- [x] **Checklist de l'article scientifique (Prof. Jonas, 2026-07-02) — 7 sur 8
      terminés** (v0.32.0–0.33.1) : topologie avec bandes **CUPS** (plan de
      contrôle × plan utilisateur), **N1** explicite (logique via gNB) et
      **N11/Nsmf** étiqueté, layout re-quadrillé sans aucune ligne traversant
      le card d'un tiers (vérificateur dans `panel/test/check-topology.py`),
      IPs/ports standardisés, **thèmes clair/sombre** (règle d'or : consoles
      sombres dans les 2 thèmes avec palette ISO fixe `TERM` — jamais de variables de thème
      dans le contenu de terminal), annotations pédagogiques au démarrage de chaque service
      (`SERVICE_ROLES`), HTML avec `no-cache` (le déploiement arrive à l'instant) et
      **politique de coûts** ([`docs/POLITICA-DE-CUSTOS.md`](../../POLITICA-DE-CUSTOS.md)).
- [ ] **i18n — pt/en/es/fr** (item 1b du checklist ; décision 2026-07-03 : projet
      international, TOUT en 4 langues, fr inclus). **F1 prête (v0.34.0)** :
      infra `static/i18n.js` (dictionnaires + fallback lang→en→pt + test de
      parité `npm run test:i18n`), sélecteur 🌐, login + topbar traduits ;
      READMEs en 4 langues + `docs/i18n/<lang>/` avec `check-parity.py`.
      **Manquent** : F2 (index entier), F3 (topologie/JSONs), F4 (scripts bash
      via `LAB_LANG`) ; docs techniques en en à la demande. Règles dans le
      CONTRIBUTING §7 (le glossaire 3GPP/O-RAN ne se traduit pas).
- [ ] **Lab de RIC Near-RT/Non-RT avec IA** (scikit-learn aarch64 déjà vendorisé
      dans `server/panel/vendor/`) : xApp d'inférence dans la boucle des secondes +
      rApp d'entraînement dans le Non-RT. **Dépend de l'upgrade vers 4 vCPU** — analyse de
      coût et runbook du resize réversible dans la politique de coûts §3.
- [ ] Confirmer avec le professeur la grille/le plan de tests officiels du
      Projet 2 (non publiés dans le dépôt d'origine à la date de la vérification).
- [x] Diagnostic de l'état réel du Projet 2 (2026-06-18) : rien n'était
      fonctionnel — les `.so` de Service Model étaient x86-64 (incorrect pour ARM64),
      le seul log existant montrait E2SM-RC échouant avec un core dump, sans
      aucun binaire compilé sur le serveur. Voir `CHANGELOG.md` v0.8.0.
- [x] Builder et valider `server/oai-cn-gnb-e2/` (2026-06-19) : 6 images OAI
      5G Core arm64 construites sur le Mac Apple Silicon, chargées sur le serveur ;
      `up_e2_lab.sh` monte Core OAI + nearRT-RIC + gNB(E2) + nrUE ; E2 SETUP OK,
      8 RAN functions enregistrées (2,3,142–148), `test_e2_sm.sh all` passe
      (les xApps souscrivent KPM/RC/MAC/RLC/PDCP/GTP). L'UE arrive à `RRC_CONNECTED`.
- [x] **Stabilité de l'instance** (2026-06-19) : le gNB/nrUE RFSIM saturaient
      les 2 vCPUs du `t4g.medium` et **gelaient la machine** (plusieurs reboots
      forcés). Corrigé en enveloppant les processus natifs dans des *scopes* du
      systemd avec `CPUQuota` (120%/60%) + `CPUWeight=20` + `nice 10` dans
      `up_gnb_oai.sh` — réserve du CPU pour le système, empêche le freeze sans casser
      l'E2 (validé : machine réactive sous charge, le E2 SM test passe).
- [ ] **xApp UE-TP-rApp** (thème du groupe) : prévision de débit par UE à
      partir de RSSI/RSRP/CQI/PRB. Squelette dans `xapp_ue_tp_moni.c` ; manque le
      modèle de prévision. **Prochaine grande étape après la présentation.**
- [ ] **🧱 Upgrade vers 4 vCPU — blocage HW pour le rapport complet de KPM.**
      Collecter le KPM avec **débit réel** (données non-nulles pour l'analyse et l'
      UE-TP-rApp) exige UE+gNB RFSIM en temps réel, ce qui **ne rentre pas dans 2 vCPU sous
      le guardrail**. Forcer 2 cores (retirer le guardrail) **a gelé le box 2×**
      (reboots). Décision : le collecteur (`kpm_collect_real.sh`) **ne touche jamais au cpuset**
      et se conclut honnêtement en 2 vCPU ; **les données réelles dépendent d'une instance 4 vCPU**
      (`t4g.xlarge`). Pour l'instant, démonstration sûre = KPM signé + analyse sur l'
      échantillon (`kpm_analytics.sh`). Voir [`docs/KPM-COLETA-RESILIENTE.md`](../../../server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md).
- [x] **User plane de l'UE dans le Projet 2 — RÉSOLU dans le core v2.2.1** (2026-06-22) :
      l'UE attache, obtient l'IP `12.1.1.2` et a du trafic réel (`ping 8.8.8.8` 0 % de perte
      par l'`oaitun_ue1`). Le blocage **n'était pas** l'AUSF↔UDM HTTP/2 (celui-là était du
      core **v1.5.1**) ; dans le v2.2.1 le goulot est le **CPU** : en 2 vCPU avec le guardrail de
      cpuset (1 core), gNB et UE se partagent le core et le RRC de l'UE inonde. Avec les **2
      cores** libérés (ou **4 vCPU**, recommandé), l'UE attache normalement. Trade-off
      et procédure timer-free dans [`server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md`](../../../server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md)
      et §7.c.
- [ ] Persister les symlinks du FlexRIC (`/usr/local/lib/flexric` et
      `/usr/local/etc/flexric`) dans `infra/server-bootstrap.sh` — aujourd'hui ils sont
      créés à la main et se perdent en changeant d'instance.
- [x] Groupe « Projeto 2 — OAI/FlexRIC (E2) » dans le tableau de bord (`server.py` +
      `index.html`) : boutons up/down/test du E2 lab, même mécanisme
      générique `data-cmd` → `POST /api/run/{cmd}` du Projet 1.
- [ ] Évaluer le report des bugs du §8 au professeur/dépôt original.
- [ ] Implémenter le reste du blueprint du tableau de bord d'observabilité
      (`docs/blueprint-painel-observabilidade.md`) — la télémétrie (§5) et les
      logs filtrés (§5) déjà faits sans Loki/Grafana/Prometheus ; manque le
      capteur de protocole E2/NGAP/GTP-U + topologie interactive
      (pédagogique, plus ambitieux).
- [x] **Inscription d'UE** : formulaire dans le tableau de bord (IMSI/K/OPc/MSISDN/AMF)
      avec du texte d'aide par champ, appelle `./scripts/add-subscriber.sh` via
      `POST /api/subscriber` ; guest bloqué avec 403.
- [x] **Outils de test dans le tableau de bord** :
  - Test de débit : `iperf3` entre `ueransim` (uesimtun0) et `dn` —
    baseline ~150 Mbits/s confirmé (`scripts/test_throughput.sh`).
  - Test d'interférence/distance : `tc netem` sur uesimtun0 via
    `scripts/test_channel.sh` (modèles 3GPP TR 38.901 + Shannon). Idéal
    ~148 Mbit/s → 1km/moyenne ~608 Kbit/s (perte/RTT suivent).
- [x] **Colorimétrie ISO/ANSI + résumé pédagogique dans tous les tests**
      (v0.12.0) : lib `scripts/lib/testlog.sh` + rendu ANSI dans le tableau de bord ; chaque
      test se termine par « Ce qu'il a fait » + « Résultat » coloré. Voir `CHANGELOG.md`.
- [x] **Audit pédagogique + vérification en direct de tous les rapports**
      (v0.25.0–0.25.3) : Démo E2E avec commande/sortie réelle + « Pourquoi » et
      débit corrigé (149 Mbit/s par le tunnel 5G, §8.6) ; P1 et P2 lancés en
      direct, 3 bugs de précision corrigés (§8.5) ; guide dev dans
      [`docs/relatorios-didaticos.md`](../../relatorios-didaticos.md).
- [x] **Anti-freeze** : gNB/nrUE RFSIM tournent sous `systemd-run --scope` avec
      `CPUQuota`/`CPUWeight`/`nice` dans `up_gnb_oai.sh`, `test_e2_kpm.sh` et
      `test_e2_rc_attach.sh` — l'instance de 2 vCPUs ne gèle plus.

> **Piège opérationnel (5G-AKA / SQN) :** si l'UE ne s'enregistre pas et que le log montre
> `Authentication Failure due to SQN out of range`, le numéro de séquence de l'
> abonné (UDM/MongoDB) s'est désynchronisé du SIM. Solution : ré-inscrire l'
> abonné (`./scripts/add-subscriber.sh`, qui supprime+insère et remet le SQN à zéro) et
> redémarrer l'UE (`docker restart ueransim`). L'`uesimtun0` revient en quelques secondes.

---

## 11. Références à l'intérieur du dépôt

- [`README.md`](../../../README.md) — porte d'entrée : **comment reproduire** l'état
  actuel à partir de zéro, roadmap avec dates et **comment collaborer** (contact :
  [hc@cesar.school](mailto:hc@cesar.school) · [@henriquecarmine](https://github.com/henriquecarmine)).
- [`CHANGELOG.md`](../../../CHANGELOG.md) — historique chronologique détaillé de chaque action.
- [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) — comment collaborer (Issues/Discussions/PR, validation, version).
- [`docs/relatorios-didaticos.md`](../../relatorios-didaticos.md) — **guide dev du système de rapports** : lib `testlog.sh`, protocole de la Démo E2E, comment ajouter un rapport, gotchas (§8.5–8.6) et inventaire P1/P2.
- [`docs/blueprint-painel-observabilidade.md`](../../blueprint-painel-observabilidade.md) — conception du tableau de bord.
- [`docs/labs/`](../../labs) — guides originaux du cours (installation Docker, pré-lab GCP/VM, core Open5GS, UERANSIM, rapport de remise).
- [`server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md`](../../../server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md) — feuille de route officielle du Projet 2.
- [`server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md`](../../../server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md) — **guide de reproduction jusqu'au user plane** (UE avec IP + ping) : dimensionnement du CPU (**4 vCPU recommandé vs 2 vCPU alternatif**), démarrage du core v2.2.1 + E2 + xApps, et la procédure timer-free de libérer/reverter les 2 cores.
- [`server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md`](../../../server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md) — **Données dans la RAN** : pipeline pédagogique `kpm_analytics.sh` (Cours 06, slide 46) qui transforme le log KPM brut en série temporelle CSV + KPIs par UE + sparkline ; pont vers l'UE-TP-rApp et le Module 7 (Analyse de Données).
- [`server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md`](../../../server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md) — **ingénierie au millimètre** du `kpm_collect_real.sh` : collecte de KPM avec trafic réel **résiliente et 100 % par événement** (heartbeat « n'a pas planté », auto-retry, auto-revert du cpuset, watchdog anti-hang) — le standard « zéro temps » appliqué, pour la présentation en direct.
- `pdfs/` — slides des Cours 01–04 + tableur de composition des groupes (source de tout dans le §1).
