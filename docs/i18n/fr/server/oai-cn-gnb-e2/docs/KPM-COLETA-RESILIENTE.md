<!-- sync: e36a3f4e -->
> 🌐 Traduction en **français** du document canonique en portugais [`server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md`](../../../../../../server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md). Toutes les langues : [INDEX](../../../INDEX.md) · synchronisation vérifiée par `docs/i18n/check-parity.py`.

# Collecte KPM résiliente — ingénierie au millimètre (`kpm_collect_real.sh`)

Guide **ligne à ligne** du collecteur de télémétrie KPM avec trafic réel, conçu pour
s'exécuter **en direct lors d'une présentation** sans bloquer, sans perdre le test et sans
échouer. C'est la pièce qui produit le `xapp_kpm_lab.log` avec des **données réelles** que
le [`kpm_analytics.sh`](KPM-ANALYTICS.md) transforme en CSV/KPI.

> ## ⚠️ État actuel et dépendance au CPU (à lire en premier)
> **Un rapport complet de KPM avec débit réel exige une instance à 4 vCPU**
> (ex. : `t4g.xlarge`). Sur le `t4g.medium` (2 vCPU) actuel, le gNB et l'UE en RFSIM ne
> coexistent pas en temps réel **sous le guardrail anti-freeze** (1 cœur) ; et **retirer le
> guardrail pour libérer 2 cœurs a gelé le box deux fois** (a nécessité un reboot).
>
> **Décision d'ingénierie (la sécurité d'abord) :** ce script a été réécrit
> pour **NE JAMAIS toucher au cpuset**. Sur 2 vCPU, il détecte rapidement que l'UE ne
> s'attache pas, **arrête l'UE** (l'empêche d'inonder la mémoire) et **conclut honnêtement**
> « pas de données — utilisez 4 vCPU ». Sur 4 vCPU, l'UE s'attache naturellement (sans relax)
> et la collecte produit des données réelles. **Démonstration sûre pour l'instant :** KPM
> souscrit + analyse sur l'échantillon pédagogique (`kpm_analytics.sh scripts/samples/kpm_sample.log`).

> **Pour ceux qui n'ont jamais vu le lab :** lisez d'abord [`PROJETO2-CPU-E-USERPLANE.md`](PROJETO2-CPU-E-USERPLANE.md)
> (démarrer le lab, dimensionnement du CPU) et [`KPM-ANALYTICS.md`](KPM-ANALYTICS.md)
> (ce qu'est le KPM et le pipeline d'analyse). Ce document est le **comment** de la collecte.

---

## 1. Pourquoi ce script existe (le problème qu'il résout)

Collecter le KPM **avec un débit réel** exige trois choses simultanées :
1. l'**UE attaché** (avec IP) — sinon le gNB ne rapporte pas de métriques par UE ;
2. du **trafic** passant par le tunnel — sinon le débit est nul ;
3. tout cela sur le box de **2 vCPU**, où UE+gNB se disputent le CPU (voir
   [`PROJETO2-CPU-E-USERPLANE.md`](PROJETO2-CPU-E-USERPLANE.md)).

La 1ʳᵉ tentative naïve (lancer `test_e2_kpm.sh` directement) **a collecté 0 indication** :
la fenêtre de collecte a commencé **avant** que l'UE ne s'attache (l'attachement prend des
dizaines de secondes) → le gNB n'avait pas d'UE connecté → aucune métrique. Leçon : **la
collecte doit démarrer par ÉVÉNEMENT (UE avec IP), pas par horloge.**

D'où les trois exigences que le professeur a demandées, et que ce script met en œuvre :

| Exigence | Comment le script y répond |
|---|---|
| **« Ne pensez pas que c'est bloqué »** | **Heartbeat** en direct (`⏳ … NÃO travou`) à chaque événement du log |
| **« Ne pas perdre le test »** | s'exécute **détaché** + écrit dans un fichier ; le panneau enregistre la console |
| **« Si quelque chose se produit, il le signale et termine — il n'échoue pas »** | **auto-retry** avec diagnostic + **auto-revert** ; conclut toujours |

---

## 2. Principe non négociable : ZÉRO TEMPS

Règle du projet (mémoire `feedback-event-driven-nao-tempo`) : **rien ne décide par
horloge** — ni `sleep`, ni `timeout`, ni durée fixe, **ni comme filet de sécurité**. Tout se
termine par **événement/état**. Les primitives utilisées :

| Primitive | Ce qu'elle fait | Où dans le script |
|---|---|---|
| `ip -o monitor address \| grep -qm1 oaitun_ue1` | bloque (sans CPU) jusqu'à l'**événement netlink** de l'UE obtenant une IP | attente de l'attachement |
| `tail -n +1 -F --pid=$P arq \| grep -qm1 PADRÃO` | bloque jusqu'à ce que la ligne-événement apparaisse **OU** que le processus `$P` meure | flood du RRC |
| `grep --line-buffered -m K PADRÃO` | se termine **à la K-ième** occurrence (événement d'objectif) | fin de la collecte (K indications) |
| `wait -n A B` | retourne quand le **1er** des jobs A/B se termine | course succès×échec |
| `tail -f --pid=$UEPID /dev/null; kill $XAPP` | attend (sans poll) la **mort de l'UE** et tue le xApp | watchdog anti-hang |
| `trap revert EXIT` | déclenche le cleanup par la **fin du processus**, pas par le temps | auto-revert du cpuset |

> **Pourquoi `sleep` est interdit :** un `sleep N` suppose que « N secondes suffisent » — et
> quand elles ne suffisent pas (box lent, attachement long), soit vous coupez trop tôt (le
> test est perdu), soit trop tard (blocage). L'événement est **déterministe** : il se termine
> exactement quand la condition réelle se produit.

---

## 3. Anatomie du script — bloc par bloc

Fichier : [`scripts/kpm_collect_real.sh`](../../../../../../server/oai-cn-gnb-e2/scripts/kpm_collect_real.sh).

### 3.1 En-tête et variables
```bash
set -u                       # erro em variável não definida (NÃO -e: queremos tratar falhas, não abortar)
NEED_IND="${NEED_IND:-20}"   # META de indicações = EVENTO de sucesso (sobrescrevível)
MAX_TRIES="${MAX_TRIES:-3}"  # nº de tentativas antes de concluir-com-o-que-há
```
`set -u` attrape les bugs de frappe ; nous n'utilisons **pas** `set -e` car le script
**traite** les échecs (retry) au lieu d'en mourir.

### 3.2 Auto-revert (le filet de sécurité, par événement)
```bash
revert() {  # mata xApp/ping/UE e DEVOLVE o cpuset a 1 core (guardrail anti-freeze)
  kill "$XAPP_PID"; sudo kill "$PING_PID"; sudo pkill -x nr-uesoftmodem; ...
  sudo systemctl set-property --runtime "$SLICE" AllowedCPUs=1
}
trap revert EXIT
```
**Pourquoi :** libérer les 2 cœurs supprime la protection anti-freeze. Le `trap … EXIT`
garantit que, **quoi qu'il arrive** (succès, erreur, `kill`, fin normale), le cpuset revient
à 1 cœur et le lab lourd est arrêté. Il est déclenché par l'**événement de fin du processus**,
pas par un chronomètre.

### 3.3 Préconditions (échec propre, sans blocage)
```bash
pgrep -x nr-softmodem || { err "gNB não está rodando…"; exit 0; }
pgrep -x nearRT-RIC   || { err "RIC não está rodando…";  exit 0; }
[ -x "$XAPP" ]        || { err "xApp KPM não compilado…"; exit 0; }
```
`exit 0` (pas 1) : le test **conclut en indiquant le prérequis manquant**, au lieu
d'« échouer ». Le `trap` effectue tout de même le revert.

### 3.4 NE touche PAS au cpuset (le correctif de sécurité)
```bash
# (intencionalmente NÃO há set-property AllowedCPUs aqui)
NPROC=$(nproc); GUARD=$(systemctl show "$SLICE" -p AllowedCPUs --value)
[ "$NPROC" -le 2 ] && warn "2 vCPU: o UE provavelmente NÃO vai attachar; p/ dados reais use 4 vCPU"
```
**Pourquoi :** libérer les 2 cœurs (retirer le guardrail) est ce qui **a gelé le box deux
fois**. Le script s'exécute sous le cpuset en vigueur et **avertit** s'il n'y a que 2 vCPU. Sur
4 vCPU, l'UE s'attache sans qu'il faille toucher à quoi que ce soit. (Les anciennes versions
faisaient `AllowedCPUs=0-1` — **retiré par sécurité**.)

### 3.5 Boucle de tentatives (auto-retry)
```bash
while :; do
  attempt=$((attempt+1)); section "Tentativa $attempt de $MAX_TRIES"
  ...
  if [ "$attempt" -ge "$MAX_TRIES" ]; then warn "…concluo COM O QUE HÁ…"; break; fi
  step "repetindo automaticamente…"
done
```
Chaque tentative démarre l'UE propre. Si cela échoue, **il signale le problème et
recommence**. Une fois les tentatives épuisées, il **conclut** (n'échoue pas).

### 3.6 ÉVÉNEMENT 1 — attendre que l'UE obtienne une IP (avec heartbeat DEDUP)
```bash
( ip -o monitor address | grep -qm1 "oaitun_ue1" ) & W_OK=$!          # SUCESSO
( tail -F --pid="$UEPID" "$UE_LOG" | grep -qm1 -E "…contains [0-9]{5}" ) & W_BAD=$!  # FLOOD/morte
( tail -F --pid="$UEPID" "$UE_LOG" \
    | grep -oiE "Initial sync successful|PBCH|Cell Detected|UE synchronized|RRCSetup|Registration (accept|complete)|PDU Session" \
    | awk '!seen[$0]++ { print "  ⏳ UE: " $0 " (marco · NÃO travou)" }' ) & W_HB=$!  # HEARTBEAT DEDUP
wait -n "$W_OK" "$W_BAD"   # retorna no 1º evento (IP, flood ≥10000, ou morte do UE)
```
Trois processus s'exécutent : **succès** (IP via netlink), **échec** (flood de RRC =
file **≥ 5 chiffres / ≥10000**, détecté tôt, ou mort de l'UE via `--pid`) et
**heartbeat DEDUP** — `grep -o` extrait uniquement les **jalons** (sync, PBCH, RRCSetup,
Registration, PDU Session) et `awk '!seen[$0]++'` affiche **chaque jalon une seule
fois**. Cela évite les centaines de lignes que l'ancienne version générait (et qui volaient
encore du CPU à l'UE lui-même). `wait -n` retourne au premier événement. **`UEPID`** provient
du `MainPID` du scope — les `tail --pid` se terminent si l'UE meurt. Zéro `sleep`.

### 3.7 Trafic + ÉVÉNEMENT 2 — collecter K indications
```bash
sudo ping -I oaitun_ue1 8.8.8.8 >/dev/null 2>&1 & PING_PID=$!     # tráfego pelo túnel
KPM_SST=222 KPM_SD=123 "$XAPP" "${SMDIR[@]}" > "$LOG" 2>&1 & XAPP_PID=$!
# watchdog ANTI-HANG (por evento): se o UE morre, mata o xApp → o tail abaixo encerra
( tail -f --pid="$UEPID" /dev/null; kill "$XAPP_PID" ) & W_DEATH=$!
# heartbeat por indicação + parada na K-ésima (grep -m K):
while read _; do c=$((c+1)); info "⏳ indicação KPM $c/$NEED_IND (NÃO travou)"; done \
  < <(tail -n +1 -F --pid="$XAPP_PID" "$LOG" | grep --line-buffered -m "$NEED_IND" "KPM ind_msg latency")
```
- `grep -m "$NEED_IND"` se termine **exactement** à la K-ième indication → événement de
  succès. Chaque ligne lue est un **heartbeat** (« indication c/K »).
- `tail … --pid=$XAPP_PID` se termine si le xApp meurt.
- Le **watchdog** `tail -f --pid=$UEPID /dev/null; kill $XAPP_PID` est l'astuce qui
  **empêche le blocage** : il bloque (sans CPU) jusqu'à la mort de l'UE, puis tue le xApp, ce
  qui fait terminer le `tail` de la collecte. Ainsi, ni « UE tombé », ni « xApp arrêté » ne
  suspendent le script — tout par événement.

### 3.8 Verdict honnête (conclut toujours)
```bash
"$SCRIPT_DIR/kpm_analytics.sh" "$LOG"          # analisa o que coletou
if [ "$got" = 1 ]; then summary "…DADOS reais ($n indicações)…" ok
else summary "…sem atingir a meta — problema: $problem…" warn; fi
```
Lance l'analyse sur le log collecté et donne **toujours** un verdict : ✓ avec données, ou !
conclu-sans-échec avec le problème observé (UE non attaché / RRC inondé / xApp tombé / en
dessous de l'objectif).

---

## 4. Comment lancer

### 4.1 Via le panneau (recommandé en présentation)
Projet 2 → groupe de tests → **« Collecter le KPM avec trafic (réel, résilient) »**.
La console affiche le heartbeat en direct (reflété pour les étudiants) et, à la fin, la
explication « ce qui s'est passé ». Le résultat est enregistré dans « Résultats ».

### 4.2 En ligne de commande
```bash
cd ~/server/oai-cn-gnb-e2
# pré-requisito: E2 lab no ar (core + RIC + gNB)
SKIP_UE=1 ./scripts/up_e2_lab_v2.sh      # sobe sem UE (o coletor cuida do UE)
./scripts/kpm_collect_real.sh            # coleta resiliente → logs/xapp_kpm_lab.log
./scripts/kpm_analytics.sh               # (o coletor já chama; rode de novo se quiser)
```
Paramètres (environnement) :
- `NEED_IND=20` — combien d'indications collecter (objectif/événement de succès).
- `MAX_TRIES=3` — tentatives avant de conclure-avec-ce-qu'il-y-a.

---

## 5. Ce que vous voyez (sortie attendue)

**En cours (heartbeat — NÃO travou) :**
```
⏳ aguardando UE attachar — gNB sincronizando rádio (… NÃO travou)
⏳ indicação KPM 7/20 recebida (NÃO travou)
```
**Succès :**
```
✓ UE ATTACHED — oaitun_ue1 = 12.1.1.2
✓ meta atingida: 20 indicações coletadas
… (kpm_analytics: CSV + KPIs por UE + sparkline)
Resultado: concluído com DADOS reais em 1 tentativa(s)
```
**Échec géré (conclut sans blocage) :**
```
✗ tentativa 1: PROBLEMA — RRC inundou (CPU insuficiente p/ sincronizar — 2 vCPU é o limite)
→ repetindo automaticamente…
…
Resultado: concluído SEM falhar — problema: … (provável limite de 2 vCPU; ideal 4 vCPU)
```

---

## 6. Pourquoi ça NE bloque PAS le box (sécurité CPU)

- **NE touche PAS au cpuset** — le guardrail (1 cœur pour le lab, CPU 0 libre pour le
  système/SSH) reste intact. C'est la garantie principale : sans retirer le guardrail, le
  `sshd` n'est jamais étouffé → **pas de gel**.
- **Arrête l'UE dès qu'il détecte un échec** (flood/sans attachement) — empêche la file RRC
  de croître sans limite (évite la pression mémoire).
- Le script est **borné par événement** (IP / flood ≥5 chiffres / mort de processus / K
  indications) — aucune boucle ne tourne indéfiniment, aucun `sleep` ne consomme du CPU pour rien.
- S'exécute **détaché** (`nohup … &`) : si le SSH tombe, le collecteur continue, conclut et
  nettoie tout seul ; le résultat reste dans le fichier.

> **Leçon des 2 freezes :** les deux sont venus du fait de **retirer le guardrail** (libérer 2
> cœurs) — une fois avec un conteneur VPP sans auto-arrêt, une autre avec ce collecteur bloqué
> à attendre un événement qui ne venait pas pendant que l'UE inondait. Le correctif définitif a
> été de **ne jamais toucher au cpuset** ; les données réelles sont réservées à l'**upgrade vers
> 4 vCPU** (§⚠️ en haut).

---

## 7. Résolution de problèmes

| Message du script | Signification | Que faire |
|---|---|---|
| `RRC inundou (CPU insuficiente…)` | sur 2 vCPU l'UE ne se synchronise pas en temps réel | lancez en **4 vCPU** (idéal) ou acceptez le retry |
| `o nrUE caiu antes de pegar IP` | le processus de l'UE est mort | voir `logs/ue_oai.log` ; réenregistrer l'abonné si c'est SQN |
| `o xApp KPM encerrou antes da meta` | le xApp est tombé/terminé | vérifier `flexric-lib/libkpm_sm.so` (arch arm64) |
| `coletou só N indicações` | l'UE s'est attaché mais peu de trafic/temps | augmenter `NEED_IND` est contre-productif ; garantissez que le ping est actif |
| `gNB/RIC não está rodando` | le lab n'est pas actif | `./scripts/up_e2_lab_v2.sh` d'abord |

---

## 8. Où cela s'insère

```
kpm_collect_real.sh   →  logs/xapp_kpm_lab.log   →  kpm_analytics.sh  →  logs/kpm_timeseries.csv
   (coleta resiliente)        (telemetria real)        (ETL+KPI+viz)         (insumo do modelo)
                                                                                    │
                                                                                    ▼
                                                                      UE-TP-rApp (Módulo 7)
```
La collecte résiliente est le **maillon qui manquait** entre « l'E2/KPM fonctionne » et « j'ai
des données réelles à modéliser ». Avec 4 vCPU, elle s'exécute directement ; sur 2 vCPU, elle
tente, signale et conclut — toujours par événement, jamais par horloge.
