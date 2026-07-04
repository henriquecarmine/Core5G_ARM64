<!-- sync: e36a3f4e -->
> 🌐 Traduction en **français** du document canonique en portugais [`server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md`](../../../../../../server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md). Toutes les langues : [INDEX](../../../INDEX.md) · synchronisation vérifiée par `docs/i18n/check-parity.py`.

# Projet 2 — Reproduction jusqu'au user plane (UE avec IP) et dimensionnement du CPU

Guide **définitif** pour qu'un contributeur parte de zéro et atteigne l'état validé le
2026-06-22 sur le serveur Graviton : **Core OAI v2.2.1 + near-RT RIC + gNB (E2) + les 3 xApps
(KPM/cust/RC) + UE avec IP réelle et trafic par le tunnel 5G**.

Ce document se concentre sur le **CPU et le user plane** — la partie la plus déroutante et où se
trouve le trade-off important. Pour ce qui est déjà couvert dans d'autres guides, il pointe vers
le lien plutôt que de répéter :

- **Compiler les images arm64 du Core** (AMF/SMF/NRF/UDR/UDM/AUSF + **oai-upf-vpp**) :
  [`OAI-CORE-ARM64.md`](OAI-CORE-ARM64.md) et [bible §7.b](../../../../../../core5g-arm64-bible.md).
- **Build du gNB/nrUE/FlexRIC + Service Models** : [`TUTORIAL_LAB_E2.md`](TUTORIAL_LAB_E2.md),
  [`INSTALACAO_GNB_OAI.md`](INSTALACAO_GNB_OAI.md), [`E2_FLEXRIC.md`](E2_FLEXRIC.md).
- **Règle d'or du projet :** ne modifiez jamais les fichiers directement sur le serveur. Modifiez-les
  dans `server/` sur votre machine et utilisez `./deploy.sh` (et `./deploy.sh sync-oai` pour ce répertoire).

---

## 0. TL;DR — ce que vous allez obtenir et le trade-off du CPU

| Bloc | Comment valider | Dépend du UE ? |
|---|---|---|
| Core 5G (9 NFs) healthy | `docker ps` tous `healthy` | non |
| **E2 SETUP** gNB ↔ RIC | `[E2-AGENT]: E2 SETUP RESPONSE rx` dans le log du gNB | non |
| **xApps** KPM / cust / RC | `Successfully subscribed to RAN_FUNC_ID 2 / 142 / 3` | non |
| **User plane** (UE obtient une IP + ping) | `oaitun_ue1 = 12.1.1.2`, `ping 8.8.8.8` 0% de perte | **oui** |

> **La règle qui résume tout :** l'E2/RIC/xApps sont **gNB↔RIC** et **n'ont pas besoin du UE**. Le
> user plane (UE avec IP) nécessite le nrUE en cours d'exécution — et c'est le nrUE qui fait exploser le CPU.

**Dimensionnement (lisez la §1 avant de démarrer quoi que ce soit) :**
- **4 vCPU (recommandé) :** tout tourne ensemble, sans astuces, sans risque de freeze.
- **2 vCPU (alternatif — ce que nous avons aujourd'hui) :** soit vous protégez la machine (guardrail de 1
  core, **sans** UE) **soit** vous exécutez le user plane complet (2 cores, box dédié). Impossible d'avoir les deux
  en même temps. La §4 montre comment faire le test du user plane en toute sécurité.

---

## 1. Dimensionnement du CPU — pourquoi 4 vCPU est préférable

Le gNB (`nr-softmodem`) et l'UE (`nr-uesoftmodem`) tournent en **RFSIM** (radio logicielle). Chacun
fait du **busy-poll** : il sature ~1 vCPU entier de façon continue (ce n'est pas un pic — c'est constant,
car la boucle de samples tourne en temps réel). Ajoutez le near-RT RIC et le système (sshd, Docker,
Caddy, panneau) et vous avez besoin de **suffisamment de cœurs pour tous**.

### Calcul des cœurs

| Processus | Demande de CPU |
|---|---|
| `nr-softmodem` (gNB RFSIM) | ~1 core dédié |
| `nr-uesoftmodem` (UE RFSIM) | ~1 core dédié |
| `nearRT-RIC` + xApp | fraction de 1 core (pics lors de l'INDICATION→Report) |
| Système (sshd, Docker, Caddy, panneau, Core) | ~1 core |

→ **Le lab complet AVEC user plane veut ~4 cœurs.** C'est pourquoi :

### Recommandé : instance de 4 vCPU

**AWS :** `t4g.xlarge` (4 vCPU / 16 GB) ou `c7g.xlarge` (4 vCPU / 8 GB), Graviton, Ubuntu
22.04+. Avec 4 vCPU :
- gNB sur un core, UE sur un autre, RIC+xApp sur un autre, système sur un autre.
- **Sans cpuset, sans guardrail, sans freeze.** L'UE s'attache et les xApps tournent **en même temps**.
- C'est la voie qu'un contributeur devrait préférer pour développer le **UE-TP-rApp** (nécessite du
  KPM par UE **avec** l'UE actif générant du trafic).

> Si vous démarrez une nouvelle instance, **démarrez avec 4 vCPU**. Cela coûte un peu plus cher, mais élimine
> tout le reste de cette section.

### Alternatif : 2 vCPU (le box actuel — `t4g.medium`)

Avec seulement 2 cœurs, gNB + UE + système ne tiennent pas en temps réel. En 2019–2026, cela a provoqué
des **gels et des reboots** (le gNB+UE saturaient les 2 vCPUs et le `sshd` mourait — la machine
devenait inaccessible). La parade a été un **guardrail par cpuset** :

```
oai-lab.slice  →  AllowedCPUs=1     # todo o lab (gNB+UE+RIC) pinado no CPU 1
                                    # CPU 0 fica reservado p/ sistema (sshd/Docker/painel)
```

Ce guardrail **maintient la machine en vie sous charge** (SSH ~2,5 s même avec le gNB à fond), mais
a un coût : le gNB et l'UE se mettent à **partager un seul core**. Résultat mesuré :

- L'UE **se synchronise** (PHY/RFSIM OK : `Initial sync successful, PCI 0`, RSRP 51 dB)…
- …mais le **RRC se noie** — la file `TASK_RRC_NRUE task contains …` croît sans arrêt
  (71k → 112k → …) car l'UE ne reçoit pas assez de CPU pour traiter le RRC en temps réel
  (le gNB a `CPUWeight=60`, l'UE seulement `CPUWeight=20`).
- **L'UE n'obtient jamais d'IP.**

C'est pourquoi la validation canonique du P2 (E2 + xApps) s'exécute **sans l'UE** (`SKIP_UE=1`). Pour tester
le user plane sur le box de 2 vCPU, il faut **libérer temporairement les 2 cores** — voir la §4.

---

## 2. Prérequis

1. **Images arm64 du Core chargées sur le serveur** (y compris, en option, `oai-upf-vpp`).
   Voir [`OAI-CORE-ARM64.md`](OAI-CORE-ARM64.md). Le lab utilise l'`oai-upf` (simple_switch) du
   v2.2.1 — l'`oai-upf-vpp` est optionnel (voir §6).
2. **gNB/nrUE/FlexRIC compilés** sur le serveur (`openairinterface5g/` + `flexric-lib/`).
   Voir [`TUTORIAL_LAB_E2.md`](TUTORIAL_LAB_E2.md) et [`INSTALACAO_GNB_OAI.md`](INSTALACAO_GNB_OAI.md).
3. **Répertoire synchronisé :** `./deploy.sh sync-oai` (envoie `server/oai-cn-gnb-e2/`).
4. **Projet 1 arrêté** (P1 et P2 sont mutuellement exclusifs) : `./deploy.sh down all`.

Paramètres du lab (déjà configurés, cohérents entre le gNB et le core v2.2.1) :

| Item | Valeur |
|---|---|
| PLMN | 208 / 95 |
| Slice | SST 222 / SD 123 |
| DNN | `default` (pool **12.1.1.0/26**) |
| gNB | `gnb_24prb.conf`, NRB=51, f=3469440000 Hz, bande n78 |
| nrUE | `--rfsim -r 51 --numerology 1 --band 78 -C 3469440000 --ssb 186` |
| AMF | 192.168.70.132 |

---

## 3. Chemin principal — démarrer et valider (E2 + xApps)

Connectez-vous au serveur (`./deploy.sh ssh`) et :

```bash
cd ~/server/oai-cn-gnb-e2

# 1) Core OAI v2.2.1 (para o P1 se estiver no ar; espera oai-amf healthy — por ESTADO)
./oai-cn5g-v2/up_core_v2.sh
docker ps        # esperado: 9 containers healthy (amf, smf, nrf, udr, udm, ausf, upf, mysql, ext-dn)

# 2) E2 lab. Para validar E2/xApps, NÃO suba o UE (libera CPU e evita o flood):
SKIP_UE=1 ./scripts/up_e2_lab_v2.sh

# 3) Confirmar E2 SETUP (gNB ↔ RIC) — por evento no log do gNB:
grep -E "E2 SETUP (REQUEST tx|RESPONSE rx)" logs/gnb_oai.log
#   [E2-AGENT]: E2 SETUP-REQUEST tx
#   [E2-AGENT]: E2 SETUP RESPONSE rx        ← gNB conectado ao RIC

# 4) Rodar os xApps (cada um encerra no 1º evento de sucesso — sem timer):
./scripts/run_xapp.sh kpm     # → Successfully subscribed to RAN_FUNC_ID 2
./scripts/run_xapp.sh cust    # → Successfully subscribed to RAN_FUNC_ID 142
./scripts/run_xapp.sh rc      # → Successfully subscribed to RAN_FUNC_ID 3
```

> **Principe du projet : ZÉRO temps.** Les scripts se terminent par **événement/état**
> (`grep -m1` sur un flux, `tail -F --pid`, attente-jusqu'à-condition), jamais par `sleep`/timeout
> aveugle. Voir la mémoire `feedback-event-driven-nao-tempo` et la bible §7.c.

Résultat mesuré (2026-06-22) : **E2 SETUP OK**, **KPM/cust/RC les trois souscrits**. C'est le
livrable évalué du Projet 2 et il **ne dépend pas du UE**.

---

## 4. User plane — UE avec IP + ping par le tunnel 5G

> **Ce que cela prouve :** que le chemin de données est complet — l'UE s'enregistre (NAS/5G-AKA), ouvre une PDU
> session, obtient une IP dans le pool `12.1.1.0/26` et a une connectivité réelle via l'interface
> `oaitun_ue1`. Résultat mesuré : `oaitun_ue1 = 12.1.1.2`, `ping 8.8.8.8` → **4/4, 0% de perte,
> RTT ~111 ms**.

### 4.a — En 4 vCPU (recommandé) : démarrez simplement avec le UE

```bash
cd ~/server/oai-cn-gnb-e2
./oai-cn5g-v2/up_core_v2.sh
./scripts/up_e2_lab_v2.sh        # SKIP_UE=0 (default) → sobe gNB + nrUE

# Espera-até-condição (por ESTADO, não por tempo): UE ganha IP
until ip -4 addr show oaitun_ue1 >/dev/null 2>&1; do
  pgrep -x nr-uesoftmodem >/dev/null || { echo "nrUE morreu"; break; }
done
ip -4 addr show oaitun_ue1 | grep inet           # → inet 12.1.1.2/...
ping -I oaitun_ue1 -c 4 8.8.8.8                   # → 0% packet loss
```

En 4 vCPU cela fonctionne directement, **sans toucher au cpuset**, et vous pouvez même exécuter les xApps en
parallèle (il reste un cœur pour le RIC+xApp). C'est l'environnement adéquat pour développer le
**UE-TP-rApp** (KPM par UE avec trafic réel).

### 4.b — En 2 vCPU (alternatif) : libérer les 2 cores en toute sécurité

Sur le box de 2 vCPU, l'UE ne s'attache que si le lab utilise **les deux cœurs** (`AllowedCPUs=0-1`) — ce
qui **supprime le guardrail anti-freeze**. Pour faire cela sans bloquer la machine et **sans aucun
timer**, utilisez la procédure ci-dessous (validée le 2026-06-22). La sécurité vient de l'**événement +
priorité**, pas d'un chronomètre :

- **`trap revert EXIT`** — le cpuset revient à `1` quand le processus se termine (pas par une horloge).
- **Attente par événement pur** (`wait -n` entre deux watchers bloquants) :
  - succès = `ip monitor address` capture le `oaitun_ue1` obtenant une adresse (événement netlink) ;
  - échec = `tail -F --pid | grep -m1` détecte le flood du RRC.
- **`nice -20`** sur le moniteur → il est toujours ordonnancé et parvient à revenir en arrière **même si le lab
  sature les 2 cores**.

Script (`scripts/ue_userplane_2cores.sh` — créez-le à partir de ce bloc ; il est sûr et s'auto-restaure) :

```bash
#!/bin/bash
# Testa o user plane do UE liberando os 2 cores, com revert garantido por EVENTO (sem timer).
# Rode com prioridade alta:  sudo nice -n -20 bash scripts/ue_userplane_2cores.sh
SLICE=oai-lab.slice
OAI=$HOME/server/oai-cn-gnb-e2/openairinterface5g
BUILD=$OAI/cmake_targets/ran_build/build
UECONF=$OAI/scripts/ue.conf
UE_LOG=$HOME/server/oai-cn-gnb-e2/logs/ue_oai.log
UNIT=oai-nrue-$$

revert(){
  sudo pkill -x nr-uesoftmodem 2>/dev/null
  sudo systemctl set-property --runtime "$SLICE" AllowedCPUs=1 2>/dev/null   # guardrail de volta
  pkill -P $$ 2>/dev/null                                                    # encerra watchers
}
trap revert EXIT                                  # revert por TÉRMINO, não por tempo

pgrep -x nr-softmodem >/dev/null || { echo "ABORT: gNB nao roda"; exit 1; }

# WATCHER de SUCESSO (evento netlink) — inicia ANTES do UE p/ não perder o add do endereço
( ip -o monitor address 2>/dev/null | grep -qm1 "oaitun_ue1" ) & WIN_OK=$!

# Libera os 2 cores
sudo systemctl set-property --runtime "$SLICE" AllowedCPUs=0-1
sudo pkill -x nr-uesoftmodem 2>/dev/null; : > "$UE_LOG"
cd "$BUILD" || exit 1
sudo systemd-run --scope -q --unit="$UNIT" --slice="$SLICE" -p CPUQuota=100% -p CPUWeight=20 \
  nice -n 10 ./nr-uesoftmodem -O "$UECONF" --rfsim -r 51 --numerology 1 --band 78 \
  -C 3469440000 --ssb 186 > "$UE_LOG" 2>&1 &
UEPID=$(systemctl show -p MainPID --value "$UNIT.scope" 2>/dev/null)

# WATCHER de FALHA (evento no log): flood RRC (>=6 dígitos) OU morte do UE (--pid encerra tail)
( tail -n +1 -F --pid="${UEPID:-$$}" "$UE_LOG" 2>/dev/null \
    | grep -qm1 -E "TASK_RRC_NRUE task contains [0-9]{6}" ) & WIN_BAD=$!

wait -n "$WIN_OK" "$WIN_BAD"                       # bloqueia até o 1º EVENTO — zero tempo

if ip -4 addr show oaitun_ue1 >/dev/null 2>&1; then
  echo "OK: UE ATTACHED — $(ip -4 addr show oaitun_ue1 | grep -oE 'inet [0-9.]+')"
  ping -I oaitun_ue1 -c 4 8.8.8.8 | tail -3
else
  echo "FALHA: UE nao attachou (flood/morte) mesmo com 2 cores"
fi
# trap EXIT reverte (cpuset=1, UE off) automaticamente
```

Après l'exécution, **confirmez le revert** :

```bash
systemctl show oai-lab.slice -p AllowedCPUs --value     # → 1   (guardrail restaurado)
pgrep -x nr-uesoftmodem && echo "UE ON (revert falhou!)" || echo "UE OFF (ok)"
```

> ⚠️ **Pourquoi ne pas laisser les 2 cores activés en permanence :** sans le guardrail, un pic de
> gNB+UE peut étouffer le `sshd` et **bloquer l'instance** (c'est déjà arrivé — a nécessité un reboot). La
> procédure ci-dessus sert à **prouver** le user plane et à **revenir à l'état sûr**. Si vous
> voulez que l'UE tourne de façon stable et continue, **migrez vers 4 vCPU** (§1).

---

## 5. État final attendu et comment laisser le serveur

État sûr (E2/xApps validés, guardrail actif, UE off) :

```bash
docker ps --format '{{.Names}}' | grep -cE 'oai-|mysql'    # 9
pgrep -x nearRT-RIC && pgrep -x nr-softmodem               # RIC e gNB ON
pgrep -x nr-uesoftmodem || echo "UE OFF"                   # UE off (seguro em 2 vCPU)
systemctl show oai-lab.slice -p AllowedCPUs --value        # 1
uptime                                                     # load baixo
```

Tout arrêter : `./scripts/down_e2_lab.sh` et `./oai-cn5g-v2/down_core_v2.sh`.

---

## 6. `oai-upf-vpp` en arm64 (optionnel)

Le lab utilise l'`oai-upf` (simple_switch) du v2.2.1, qui **est déjà multi-arch officiel**. L'
`oai-upf-vpp` (dataplane VPP, plus rapide) a été **porté vers arm64** dans ce projet (il était considéré
comme « non portable ») — le blocage n'était que Hyperscan (Intel uniquement), résolu avec **Vectorscan**
(fork ARM drop-in). Détails, build et validation dans [bible §7.b](../../../../../../core5g-arm64-bible.md)
et `artifacts/oai-images/oai-upf-vpp.tar`. **Non nécessaire** pour le user plane de ce lab.

---

## 7. Troubleshooting

| Symptôme | Cause probable | Action |
|---|---|---|
| L'UE n'obtient pas d'IP ; `TASK_RRC_NRUE task contains` qui croît | CPU insuffisant (2 vCPU + guardrail = gNB et UE sur un seul core) | §4.b (libérer 2 cores) ou migrer vers 4 vCPU (§1) |
| Le SSH tombe (`Connection reset` / `timed out`) sous charge | box saturé ; un processus lourd a volé le CPU 0 du `sshd` | travaillez **détaché** (`nohup` + fichier sur le serveur) et utilisez `ssh -o ServerAliveInterval=10` ; n'exécutez jamais de processus lourd **en dehors** de l'`oai-lab.slice` |
| Machine bloquée / inaccessible | guardrail off + gNB+UE saturant les 2 cores | reboot via la console AWS ; ne laissez jamais les 2 cores libérés sans la procédure auto-revert de la §4.b |
| `Authentication Failure ... SQN out of range` | le SQN de l'abonné s'est désynchronisé | ré-enregistrer (`add-subscriber.sh`) et redémarrer l'UE |
| log du gNB : `No connected device, generating void samples` | c'est normal **avant** que le nrUE se connecte au RFSIM (:4043) ; devient `RFsim: Number of antennas changed 0→1` lors de la connexion | attendre le nrUE ; s'il persiste, le nrUE est mort — voir `logs/ue_oai.log` |
| `exec format error` au démarrage d'une image du Core | image amd64 sur un hôte arm64 | charger la bonne image arm64 (`OAI-CORE-ARM64.md`) |

---

## 8. Référence rapide des commandes

```bash
# subir / parar
./oai-cn5g-v2/up_core_v2.sh                 ./oai-cn5g-v2/down_core_v2.sh
SKIP_UE=1 ./scripts/up_e2_lab_v2.sh         ./scripts/down_e2_lab.sh   # E2/xApps (sem UE)
./scripts/up_e2_lab_v2.sh                                              # + UE (só em 4 vCPU, ou §4.b em 2 vCPU)

# validar
grep -E "E2 SETUP RESPONSE rx" logs/gnb_oai.log
./scripts/run_xapp.sh kpm|cust|rc
ip -4 addr show oaitun_ue1 ; ping -I oaitun_ue1 -c 4 8.8.8.8

# CPU (2 vCPU)
systemctl show oai-lab.slice -p AllowedCPUs --value          # 1 = guardrail; 0-1 = liberado
sudo systemctl set-property --runtime oai-lab.slice AllowedCPUs=1   # restaurar guardrail
```
