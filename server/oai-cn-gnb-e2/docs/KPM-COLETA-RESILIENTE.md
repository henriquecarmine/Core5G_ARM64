# Coleta KPM resiliente — engenharia milimétrica (`kpm_collect_real.sh`)

Guia **linha a linha** do coletor de telemetria KPM com tráfego real, feito para
rodar **ao vivo numa apresentação** sem travar, sem perder o teste e sem falhar.
É a peça que produz o `xapp_kpm_lab.log` com **dados reais** que o
[`kpm_analytics.sh`](KPM-ANALYTICS.md) transforma em CSV/KPI.

> ## ⚠️ Estado atual e dependência de CPU (leia primeiro)
> **Relatório completo de KPM com throughput real exige uma instância de 4 vCPU**
> (ex.: `t4g.xlarge`). No `t4g.medium` (2 vCPU) atual, gNB e UE em RFSIM não
> coexistem em tempo real **sob o guardrail anti-freeze** (1 core); e **remover o
> guardrail para liberar 2 cores congelou o box duas vezes** (exigiu reboot).
>
> **Decisão de engenharia (segurança em 1º lugar):** este script foi reescrito
> para **NUNCA mexer no cpuset**. Em 2 vCPU ele detecta rápido que o UE não
> attacha, **para o UE** (não deixa inundar memória) e **conclui honestamente**
> "sem dados — use 4 vCPU". Em 4 vCPU o UE attacha naturalmente (sem relax) e a
> coleta rende dados reais. **Demonstração segura por ora:** KPM assinado + análise
> sobre a amostra didática (`kpm_analytics.sh scripts/samples/kpm_sample.log`).

> **Para quem nunca viu o lab:** primeiro leia [`PROJETO2-CPU-E-USERPLANE.md`](PROJETO2-CPU-E-USERPLANE.md)
> (subir o lab, dimensionamento de CPU) e [`KPM-ANALYTICS.md`](KPM-ANALYTICS.md)
> (o que é KPM e o pipeline de análise). Este documento é o **como** da coleta.

---

## 1. Por que este script existe (o problema que ele resolve)

Coletar KPM **com throughput real** exige três coisas simultâneas:
1. o **UE attachado** (com IP) — senão o gNB não reporta métricas por UE;
2. **tráfego** passando pelo túnel — senão o throughput é zero;
3. tudo isso no box de **2 vCPU**, onde UE+gNB disputam CPU (ver
   [`PROJETO2-CPU-E-USERPLANE.md`](PROJETO2-CPU-E-USERPLANE.md)).

A 1ª tentativa ingênua (rodar `test_e2_kpm.sh` direto) **coletou 0 indicações**:
a janela de coleta começou **antes** de o UE attachar (o attach leva dezenas de
segundos) → o gNB não tinha UE conectado → nenhuma métrica. Lição: **a coleta
tem de começar por EVENTO (UE com IP), não por relógio.**

Daí os três requisitos que o professor pediu, e que este script implementa:

| Requisito | Como o script atende |
|---|---|
| **"Não pensem que travou"** | **Heartbeat** ao vivo (`⏳ … NÃO travou`) a cada evento do log |
| **"Não perder o teste"** | roda **destacado** + grava em arquivo; o painel salva o console |
| **"Se algo ocorrer, reporta e completa — não falha"** | **auto-retry** com diagnóstico + **auto-revert**; conclui sempre |

---

## 2. Princípio inegociável: ZERO TEMPO

Regra do projeto (memória `feedback-event-driven-nao-tempo`): **nada decide por
relógio** — nem `sleep`, nem `timeout`, nem duração fixa, **nem como rede de
segurança**. Tudo termina por **evento/estado**. As primitivas usadas:

| Primitiva | O que faz | Onde no script |
|---|---|---|
| `ip -o monitor address \| grep -qm1 oaitun_ue1` | bloqueia (sem CPU) até o **evento netlink** do UE ganhar IP | espera do attach |
| `tail -n +1 -F --pid=$P arq \| grep -qm1 PADRÃO` | bloqueia até a linha-evento aparecer **OU** o processo `$P` morrer | flood do RRC |
| `grep --line-buffered -m K PADRÃO` | encerra **na K-ésima** ocorrência (evento de meta) | fim da coleta (K indicações) |
| `wait -n A B` | retorna quando o **1º** dos jobs A/B termina | corrida sucesso×falha |
| `tail -f --pid=$UEPID /dev/null; kill $XAPP` | espera (sem poll) a **morte do UE** e mata o xApp | watchdog anti-hang |
| `trap revert EXIT` | dispara o cleanup pelo **término do processo**, não por tempo | auto-revert do cpuset |

> **Por que não pode `sleep`:** um `sleep N` assume que "N segundos bastam" — e
> quando não bastam (box lento, attach demorado), ou você corta cedo (perde o
> teste) ou tarde (trava). O evento é **determinístico**: termina exatamente
> quando a condição real acontece.

---

## 3. Anatomia do script — bloco a bloco

Arquivo: [`scripts/kpm_collect_real.sh`](../scripts/kpm_collect_real.sh).

### 3.1 Cabeçalho e variáveis
```bash
set -u                       # erro em variável não definida (NÃO -e: queremos tratar falhas, não abortar)
NEED_IND="${NEED_IND:-20}"   # META de indicações = EVENTO de sucesso (sobrescrevível)
MAX_TRIES="${MAX_TRIES:-3}"  # nº de tentativas antes de concluir-com-o-que-há
```
`set -u` pega bugs de digitação; **não** usamos `set -e` porque o script
**trata** falhas (retry) em vez de morrer nelas.

### 3.2 Auto-revert (a rede de segurança, por evento)
```bash
revert() {  # mata xApp/ping/UE e DEVOLVE o cpuset a 1 core (guardrail anti-freeze)
  kill "$XAPP_PID"; sudo kill "$PING_PID"; sudo pkill -x nr-uesoftmodem; ...
  sudo systemctl set-property --runtime "$SLICE" AllowedCPUs=1
}
trap revert EXIT
```
**Por quê:** liberar os 2 cores remove a proteção anti-freeze. O `trap … EXIT`
garante que, **aconteça o que acontecer** (sucesso, erro, `kill`, fim normal), o
cpuset volta a 1 core e o lab pesado é parado. É disparado pelo **evento de
término do processo**, não por um cronômetro.

### 3.3 Pré-condições (falha limpa, sem travar)
```bash
pgrep -x nr-softmodem || { err "gNB não está rodando…"; exit 0; }
pgrep -x nearRT-RIC   || { err "RIC não está rodando…";  exit 0; }
[ -x "$XAPP" ]        || { err "xApp KPM não compilado…"; exit 0; }
```
`exit 0` (não 1): o teste **conclui informando o pré-requisito que falta**, em
vez de "falhar". O `trap` ainda reverte.

### 3.4 NÃO mexe no cpuset (a correção de segurança)
```bash
# (intencionalmente NÃO há set-property AllowedCPUs aqui)
NPROC=$(nproc); GUARD=$(systemctl show "$SLICE" -p AllowedCPUs --value)
[ "$NPROC" -le 2 ] && warn "2 vCPU: o UE provavelmente NÃO vai attachar; p/ dados reais use 4 vCPU"
```
**Por quê:** liberar os 2 cores (remover o guardrail) foi o que **congelou o box
duas vezes**. O script roda sob o cpuset vigente e **avisa** se há só 2 vCPU. Em
4 vCPU o UE attacha sem precisar mexer em nada. (Versões antigas faziam
`AllowedCPUs=0-1` — **removido por segurança**.)

### 3.5 Loop de tentativas (auto-retry)
```bash
while :; do
  attempt=$((attempt+1)); section "Tentativa $attempt de $MAX_TRIES"
  ...
  if [ "$attempt" -ge "$MAX_TRIES" ]; then warn "…concluo COM O QUE HÁ…"; break; fi
  step "repetindo automaticamente…"
done
```
Cada tentativa sobe o UE limpo. Se não der, **reporta o problema e repete**.
Esgotadas as tentativas, **conclui** (não falha).

### 3.6 EVENTO 1 — esperar o UE pegar IP (com heartbeat DEDUP)
```bash
( ip -o monitor address | grep -qm1 "oaitun_ue1" ) & W_OK=$!          # SUCESSO
( tail -F --pid="$UEPID" "$UE_LOG" | grep -qm1 -E "…contains [0-9]{5}" ) & W_BAD=$!  # FLOOD/morte
( tail -F --pid="$UEPID" "$UE_LOG" \
    | grep -oiE "Initial sync successful|PBCH|Cell Detected|UE synchronized|RRCSetup|Registration (accept|complete)|PDU Session" \
    | awk '!seen[$0]++ { print "  ⏳ UE: " $0 " (marco · NÃO travou)" }' ) & W_HB=$!  # HEARTBEAT DEDUP
wait -n "$W_OK" "$W_BAD"   # retorna no 1º evento (IP, flood ≥10000, ou morte do UE)
```
Três processos correndo: **sucesso** (IP via netlink), **falha** (flood de RRC =
fila **≥ 5 dígitos / ≥10000**, detectado cedo, ou morte do UE via `--pid`) e
**heartbeat DEDUP** — `grep -o` extrai só **marcos** (sync, PBCH, RRCSetup,
Registration, PDU Session) e `awk '!seen[$0]++'` imprime **cada marco uma única
vez**. Isso evita as centenas de linhas que a versão antiga gerava (e que ainda
roubavam CPU do próprio UE). `wait -n` retorna no primeiro evento. **`UEPID`** vem
do `MainPID` do scope — os `tail --pid` encerram se o UE morrer. Zero `sleep`.

### 3.7 Tráfego + EVENTO 2 — coletar K indicações
```bash
sudo ping -I oaitun_ue1 8.8.8.8 >/dev/null 2>&1 & PING_PID=$!     # tráfego pelo túnel
KPM_SST=222 KPM_SD=123 "$XAPP" "${SMDIR[@]}" > "$LOG" 2>&1 & XAPP_PID=$!
# watchdog ANTI-HANG (por evento): se o UE morre, mata o xApp → o tail abaixo encerra
( tail -f --pid="$UEPID" /dev/null; kill "$XAPP_PID" ) & W_DEATH=$!
# heartbeat por indicação + parada na K-ésima (grep -m K):
while read _; do c=$((c+1)); info "⏳ indicação KPM $c/$NEED_IND (NÃO travou)"; done \
  < <(tail -n +1 -F --pid="$XAPP_PID" "$LOG" | grep --line-buffered -m "$NEED_IND" "KPM ind_msg latency")
```
- `grep -m "$NEED_IND"` encerra **exatamente** na K-ésima indicação → evento de
  sucesso. Cada linha lida é um **heartbeat** ("indicação c/K").
- `tail … --pid=$XAPP_PID` encerra se o xApp morre.
- O **watchdog** `tail -f --pid=$UEPID /dev/null; kill $XAPP_PID` é o truque que
  **impede travar**: ele bloqueia (sem CPU) até o UE morrer e então mata o xApp,
  fazendo o `tail` da coleta terminar. Assim, nem "UE caiu", nem "xApp parado"
  penduram o script — tudo por evento.

### 3.8 Veredito honesto (conclui sempre)
```bash
"$SCRIPT_DIR/kpm_analytics.sh" "$LOG"          # analisa o que coletou
if [ "$got" = 1 ]; then summary "…DADOS reais ($n indicações)…" ok
else summary "…sem atingir a meta — problema: $problem…" warn; fi
```
Roda a análise no log coletado e **sempre** dá um veredito: ✓ com dados, ou !
concluído-sem-falhar com o problema observado (UE não attachou / RRC inundou /
xApp caiu / abaixo da meta).

---

## 4. Como rodar

### 4.1 Pelo painel (recomendado na apresentação)
Projeto 2 → grupo de testes → **"Coletar KPM com tráfego (real, resiliente)"**.
O console mostra o heartbeat ao vivo (espelhado para os alunos) e, no fim, a
explicação "o que aconteceu". O resultado fica salvo em "Resultados".

### 4.2 Por linha de comando
```bash
cd ~/server/oai-cn-gnb-e2
# pré-requisito: E2 lab no ar (core + RIC + gNB)
SKIP_UE=1 ./scripts/up_e2_lab_v2.sh      # sobe sem UE (o coletor cuida do UE)
./scripts/kpm_collect_real.sh            # coleta resiliente → logs/xapp_kpm_lab.log
./scripts/kpm_analytics.sh               # (o coletor já chama; rode de novo se quiser)
```
Parâmetros (ambiente):
- `NEED_IND=20` — quantas indicações coletar (meta/evento de sucesso).
- `MAX_TRIES=3` — tentativas antes de concluir-com-o-que-há.

---

## 5. O que você vê (saída esperada)

**Trabalhando (heartbeat — NÃO travou):**
```
⏳ aguardando UE attachar — gNB sincronizando rádio (… NÃO travou)
⏳ indicação KPM 7/20 recebida (NÃO travou)
```
**Sucesso:**
```
✓ UE ATTACHED — oaitun_ue1 = 12.1.1.2
✓ meta atingida: 20 indicações coletadas
… (kpm_analytics: CSV + KPIs por UE + sparkline)
Resultado: concluído com DADOS reais em 1 tentativa(s)
```
**Falha tratada (conclui sem travar):**
```
✗ tentativa 1: PROBLEMA — RRC inundou (CPU insuficiente p/ sincronizar — 2 vCPU é o limite)
→ repetindo automaticamente…
…
Resultado: concluído SEM falhar — problema: … (provável limite de 2 vCPU; ideal 4 vCPU)
```

---

## 6. Por que NÃO trava o box (segurança de CPU)

- **NÃO mexe no cpuset** — o guardrail (1 core para o lab, CPU 0 livre para
  sistema/SSH) fica intacto. Esta é a garantia principal: sem remover o guardrail,
  o `sshd` nunca é sufocado → **não congela**.
- **Para o UE assim que detecta falha** (flood/sem attach) — não deixa a fila RRC
  crescer sem limite (evita pressão de memória).
- O script é **bounded por evento** (IP / flood ≥5 díg / morte de processo / K
  indicações) — nenhum laço gira para sempre, nenhum `sleep` come CPU à toa.
- Roda **destacado** (`nohup … &`): se o SSH cair, o coletor continua, conclui e
  limpa sozinho; o resultado fica no arquivo.

> **Lição dos 2 freezes:** ambos vieram de **remover o guardrail** (liberar 2
> cores) — uma vez com um container VPP sem autotérmino, outra com este coletor
> preso esperando um evento que não vinha enquanto o UE inundava. A correção
> definitiva foi **nunca mexer no cpuset**; dados reais ficam para o **upgrade de
> 4 vCPU** (§⚠️ no topo).

---

## 7. Solução de problemas

| Mensagem do script | Significado | O que fazer |
|---|---|---|
| `RRC inundou (CPU insuficiente…)` | em 2 vCPU o UE não sincroniza em tempo real | rode em **4 vCPU** (ideal) ou aceite o retry |
| `o nrUE caiu antes de pegar IP` | processo do UE morreu | ver `logs/ue_oai.log`; recadastrar assinante se for SQN |
| `o xApp KPM encerrou antes da meta` | xApp caiu/terminou | conferir `flexric-lib/libkpm_sm.so` (arch arm64) |
| `coletou só N indicações` | UE attachou mas pouco tráfego/tempo | aumentar `NEED_IND` é contraproducente; garanta o ping ativo |
| `gNB/RIC não está rodando` | lab não está no ar | `./scripts/up_e2_lab_v2.sh` antes |

---

## 8. Onde isso se encaixa

```
kpm_collect_real.sh   →  logs/xapp_kpm_lab.log   →  kpm_analytics.sh  →  logs/kpm_timeseries.csv
   (coleta resiliente)        (telemetria real)        (ETL+KPI+viz)         (insumo do modelo)
                                                                                    │
                                                                                    ▼
                                                                      UE-TP-rApp (Módulo 7)
```
A coleta resiliente é o **degrau que faltava** entre "o E2/KPM funciona" e "tenho
dados reais para modelar". Com 4 vCPU, ela roda direto; em 2 vCPU, ela tenta,
reporta e conclui — sempre por evento, nunca por relógio.
