<!-- sync: e8f9da69 -->
> 🌐 Traduction en **français** du document canonique en portugais [`docs/labs/02-ueransim-n2-n3-e2e.md`](../../../labs/02-ueransim-n2-n3-e2e.md). Toutes les langues : [INDEX](../INDEX.md) · synchronisation vérifiée par `docs/i18n/check-parity.py`.

# Guide 02 — UERANSIM (gNB + UE), N2/N3 et test E2E

**Objectifs :** connecter l'**UERANSIM** (gNB et UE dans le même *conteneur*) à l'AMF Open5GS ; valider **N2 (NGAP/SCTP)** et **N3 (GTP-U)** ; démontrer l'**enregistrement** de l'UE et la **session PDU** avec connectivité Internet ; recueillir des preuves du plan utilisateur (captures N3/N6 lorsque possible).

**Pré-requis :** [Guide 01](01-core-open5gs.md) terminé (core actif, abonné cohérent avec `ueransim/configs/ue.yaml`).

**Objectif principal :** flux SA de bout en bout et relation entre les interfaces **N2** (contrôle) et **N3** (données GTP-U).

**Chemins :** les commandes supposent le dossier `open5gs-containerized/` à la racine du laboratoire (ajustez selon votre clone).

**Support vidéo :** [index des vidéos](video_seq_report.md) — la [vidéo complète locale](https://youtu.be/ic3_CIllb9o) inclut **tcpdump**, **Wireshark** (N2/N3) et des tests de connectivité alignés sur ce guide.

---

## 1. Démarrage du RAN (UERANSIM)

Le **core** étant déjà en cours d'exécution (`core/scripts/up_core.sh`) :

```bash
cd open5gs-containerized/ueransim
./scripts/up_ran.sh
```

Le compose `ueransim/docker-compose.yaml` utilise les réseaux **externes** `core_net-n2` et `core_net-n3` créés par le compose du **core**. Si une erreur de réseau introuvable apparaît, revenez au Guide 01 et démarrez d'abord le core.

**Vérification :**

```bash
docker ps --filter name=ueransim --format '{{.Names}} {{.Status}}'
docker exec ueransim ps
```

**Preuve obligatoire :** *capture d'écran* ou texte de `docker ps` avec `ueransim` **Up**.

**Logs (extraits utiles) :**

```bash
docker logs ueransim 2>&1 | tail -80
```

Indicateurs de succès typiques (la formulation exacte peut varier selon la version) :

- **N2 :** `NG Setup procedure is successful` (ou message équivalent de *NG Setup* terminé).
- **UE :** état **REGISTERED**, interface `uesimtun0` avec IP dans `10.60.x.x`.

Les avertissements de permissions ou de temporisation sont fréquents en laboratoire ; le critère est un **enregistrement stable** et le **ping** à l'étape 5.

---

## 2. Identité du nœud RAN et de l'UE (pour le rapport)

Ouvrez et **transcrivez ou joignez** (avec une brève légende) les champs pertinents de :

- `ueransim/configs/gnb.yaml` : `mcc`, `mnc`, `tac`, `amfConfigs` (adresse et port de l'AMF), `gtpIp` (IP N3 du gNB), `ngapIp` / `linkIp` (N2).
- `ueransim/configs/ue.yaml` : `supi`, `mcc`, `mnc`, `gnbSearchList`, `sessions` (APN/DNN).

**Questions guides :**

- Quelle est l'IPv4 du gNB/UERANSIM sur **N2** ? (dans le lab par défaut : **10.20.0.101**.)  
- Quelle est l'IPv4 du côté GTP-U (N3) dans l'UERANSIM ? (par défaut : **10.30.0.11**.)  
- Quelle est l'adresse de l'AMF sur N2 ? (par défaut : **10.20.0.11**, port **38412**.)

**Référence :** [ueransim/docs/RAN.md](../../../../ueransim/docs/RAN.md).

---

## 3. Validation N2 (NGAP) — logs et vérification étendue

### 3.1 Logs gNB / AMF

```bash
docker logs ueransim 2>&1 | grep -iE 'ng setup|ngap|amf' | tail -30
docker logs open5gs-amf-containerized 2>&1 | tail -80
```

**Preuve :** extrait où apparaît un **NG Setup** réussi ou l'acceptation du gNB par l'AMF.

### 3.2 Script d'état du système (optionnel)

À partir de `core/` (avec le RAN **déjà** actif) :

```bash
cd open5gs-containerized/core
./scripts/test-system-status.sh
```

Ce script recherche des correspondances dans les logs (ex. : *NG Setup*, PFCP, IP de l'UE). Joignez la sortie si vous l'utilisez.

### 3.3 Capture N2 sur l'hôte (optionnel / avancé)

Le projet n'inclut pas de `capture-n2.sh` dédié ; vous pouvez capturer le **SCTP** sur le port NGAP sur l'*hôte* (nécessite `sudo`) :

```bash
sudo tcpdump -i any -nn 'sctp and port 38412'
```

Dans un autre terminal, **redémarrez** le `ueransim` pour forcer un nouveau *handshake* (`docker restart ueransim`), attendez ~15 s, arrêtez le `tcpdump` avec Ctrl+C.

**Dans Wireshark :** filtre `sctp.port == 38412` ; développez **NGAP** pour voir `NGSetupRequest` / `NGSetupResponse` si le *dissector* est actif.

**Preuve optionnelle (si vous réalisez cette étape) :** *capture d'écran* avec SCTP + NGAP ou fichier `.pcap` joint.

---

## 4. Validation N3 et N6 — script de capture sur l'UPF

Avec le **core** et le **ueransim** actifs, à partir de `core/` :

```bash
cd open5gs-containerized/core
./scripts/capture-n3-n6-pcaps.sh
```

Le script génère des *pcaps* sous `core/logs/upf/` (préfixes `n3-gtpu-*.pcap` et `n6-dn-*.pcap`) et lance un *ping* depuis l'UE.

**Dans Wireshark (N3) :**

- Filtre suggéré : `udp.port == 2152`  
- Observez le **GTP-U** et, avec du trafic généré, les **G-PDU** avec l'IP interne de l'UE.

**Preuve optionnelle :** *capture d'écran* de Wireshark avec **GTP-U** (port 2152) ou fichier `.pcap` joint + une phrase sur le rôle du TEID.

---

## 5. Test E2E — connectivité de l'UE

```bash
cd open5gs-containerized/ueransim
./scripts/test_ue_connection.sh
```

**Preuve obligatoire :** sortie **complète** du script (fichier `.txt` joint).

**Complément manuel :**

```bash
docker exec ueransim ip addr show uesimtun0
docker exec ueransim ping -c 4 -I uesimtun0 8.8.8.8
```

**Preuve :** IP attribuée à l'UE et *ping* avec 0 % de perte (ou expliquer les échecs avec un extrait de log).

---

## 6. Healthcheck global

Depuis le répertoire `core/` :

```bash
cd open5gs-containerized/core
./scripts/healthcheck.sh
```

**Preuve :** sortie complète. Avec le RAN actif, les vérifications N3 / NG Setup / PFCP devraient être **beaucoup plus alignées** qu'au Guide 01.

---

## 7. Arrêt

Ordre suggéré : **RAN d'abord**, puis **core** (si vous démontez tout).

```bash
cd open5gs-containerized/ueransim
./scripts/down_ran.sh
```

(Le core peut rester actif pour de nouveaux essais.)

---

## Checklist Guide 02

- *Conteneur* `ueransim` **Up** ; logs avec **NG Setup** réussi (ou équivalent).  
- Paramètres de `gnb.yaml` et `ue.yaml` décrits dans le rapport (N2/N3, PLMN, APN).  
- Extraits de log UERANSIM + AMF avec N2/NG Setup.  
- (Optionnel avancé) Capture SCTP/NGAP sur l'*hôte* — *capture d'écran* ou `.pcap`.  
- (Optionnel avancé) Capture N3 via `capture-n3-n6-pcaps.sh` — *capture d'écran* Wireshark ou `.pcap`.  
- Sortie de `test_ue_connection.sh` (fichier joint).  
- Sortie de `healthcheck.sh` avec le RAN activé.  
- Paragraphe dans le rapport : différence **N2** (*contrôle / NGAP*) vs **N3** (*plan utilisateur / GTP-U*).

**Références :** [ueransim/docs/RAN.md](../../../../ueransim/docs/RAN.md), [README.md](../../../../README.md) (*Troubleshooting*).

---

## Résumé des problèmes fréquents


| Symptôme                               | Cause probable                         | Que vérifier                                       |
| -------------------------------------- | -------------------------------------- | -------------------------------------------------- |
| `network core_net-n2 not found`        | Core non démarré                       | `./scripts/up_core.sh` dans `core/`.               |
| `slice-not-supported` / échec NG Setup | PLMN, TAC ou SST/SD incohérents        | `gnb.yaml` vs `amf.yaml` / slice dans l'UDM.       |
| UE sans IP                             | Abonné manquant ou IMSI ≠ `ue.yaml`    | WebUI / Mongo ; Guide 01.                          |
| Ping échoue avec IP attribuée          | UPF / routes / PFCP                    | Logs SMF et UPF ; [README](../../../../README.md). |

