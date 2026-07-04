<!-- sync: e36a3f4e -->
> 🌐 Traducción al **español** del documento canónico en portugués [`server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md`](../../../../../../server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md). Todos los idiomas: [INDEX](../../../INDEX.md) · sincronización verificada por `docs/i18n/check-parity.py`.

# Recolección KPM resiliente — ingeniería milimétrica (`kpm_collect_real.sh`)

Guía **línea por línea** del recolector de telemetría KPM con tráfico real, hecho para
correr **en vivo en una presentación** sin trabarse, sin perder la prueba y sin fallar.
Es la pieza que produce el `xapp_kpm_lab.log` con **datos reales** que el
[`kpm_analytics.sh`](KPM-ANALYTICS.md) transforma en CSV/KPI.

> ## ⚠️ Estado actual y dependencia de CPU (lee primero)
> **Un reporte completo de KPM con throughput real exige una instancia de 4 vCPU**
> (ej.: `t4g.xlarge`). En el `t4g.medium` (2 vCPU) actual, gNB y UE en RFSIM no
> coexisten en tiempo real **bajo el guardrail anti-freeze** (1 core); y **quitar el
> guardrail para liberar 2 cores congeló el box dos veces** (exigió reboot).
>
> **Decisión de ingeniería (la seguridad primero):** este script fue reescrito
> para **NUNCA tocar el cpuset**. En 2 vCPU detecta rápido que el UE no
> attacha, **detiene el UE** (no deja que inunde la memoria) y **concluye honestamente**
> "sin datos — usa 4 vCPU". En 4 vCPU el UE attacha naturalmente (sin relax) y la
> recolección rinde datos reales. **Demostración segura por ahora:** KPM suscrito + análisis
> sobre la muestra didáctica (`kpm_analytics.sh scripts/samples/kpm_sample.log`).

> **Para quien nunca vio el lab:** primero lee [`PROJETO2-CPU-E-USERPLANE.md`](PROJETO2-CPU-E-USERPLANE.md)
> (levantar el lab, dimensionamiento de CPU) y [`KPM-ANALYTICS.md`](KPM-ANALYTICS.md)
> (qué es KPM y el pipeline de análisis). Este documento es el **cómo** de la recolección.

---

## 1. Por qué existe este script (el problema que resuelve)

Recolectar KPM **con throughput real** exige tres cosas simultáneas:
1. el **UE attachado** (con IP) — si no, el gNB no reporta métricas por UE;
2. **tráfico** pasando por el túnel — si no, el throughput es cero;
3. todo esto en el box de **2 vCPU**, donde UE+gNB se disputan la CPU (ver
   [`PROJETO2-CPU-E-USERPLANE.md`](PROJETO2-CPU-E-USERPLANE.md)).

El 1º intento ingenuo (correr `test_e2_kpm.sh` directo) **recolectó 0 indicaciones**:
la ventana de recolección empezó **antes** de que el UE attachara (el attach lleva decenas de
segundos) → el gNB no tenía UE conectado → ninguna métrica. Lección: **la recolección
tiene que empezar por EVENTO (UE con IP), no por reloj.**

De ahí los tres requisitos que el profesor pidió, y que este script implementa:

| Requisito | Cómo lo cumple el script |
|---|---|
| **"No piensen que se trabó"** | **Heartbeat** en vivo (`⏳ … NÃO travou`) en cada evento del log |
| **"No perder la prueba"** | corre **en segundo plano** + graba en archivo; el panel guarda la consola |
| **"Si algo ocurre, reporta y completa — no falla"** | **auto-retry** con diagnóstico + **auto-revert**; concluye siempre |

---

## 2. Principio innegociable: TIEMPO CERO

Regla del proyecto (memoria `feedback-event-driven-nao-tempo`): **nada decide por
reloj** — ni `sleep`, ni `timeout`, ni duración fija, **ni como red de seguridad**.
Todo termina por **evento/estado**. Las primitivas usadas:

| Primitiva | Qué hace | Dónde en el script |
|---|---|---|
| `ip -o monitor address \| grep -qm1 oaitun_ue1` | bloquea (sin CPU) hasta el **evento netlink** de que el UE gane IP | espera del attach |
| `tail -n +1 -F --pid=$P arq \| grep -qm1 PADRÃO` | bloquea hasta que la línea-evento aparezca **O** el proceso `$P` muera | flood del RRC |
| `grep --line-buffered -m K PADRÃO` | termina **en la K-ésima** ocurrencia (evento de meta) | fin de la recolección (K indicaciones) |
| `wait -n A B` | retorna cuando el **1º** de los jobs A/B termina | carrera éxito×fallo |
| `tail -f --pid=$UEPID /dev/null; kill $XAPP` | espera (sin poll) la **muerte del UE** y mata el xApp | watchdog anti-hang |
| `trap revert EXIT` | dispara el cleanup por el **término del proceso**, no por tiempo | auto-revert del cpuset |

> **Por qué no se puede usar `sleep`:** un `sleep N` asume que "N segundos bastan" — y
> cuando no bastan (box lento, attach demorado), o cortas temprano (pierdes la
> prueba) o tarde (se traba). El evento es **determinístico**: termina exactamente
> cuando la condición real ocurre.

---

## 3. Anatomía del script — bloque por bloque

Archivo: [`scripts/kpm_collect_real.sh`](../../../../../../server/oai-cn-gnb-e2/scripts/kpm_collect_real.sh).

### 3.1 Cabecera y variables
```bash
set -u                       # erro em variável não definida (NÃO -e: queremos tratar falhas, não abortar)
NEED_IND="${NEED_IND:-20}"   # META de indicações = EVENTO de sucesso (sobrescrevível)
MAX_TRIES="${MAX_TRIES:-3}"  # nº de tentativas antes de concluir-com-o-que-há
```
`set -u` atrapa bugs de tipeo; **no** usamos `set -e` porque el script
**trata** las fallas (retry) en vez de morir en ellas.

### 3.2 Auto-revert (la red de seguridad, por evento)
```bash
revert() {  # mata xApp/ping/UE e DEVOLVE o cpuset a 1 core (guardrail anti-freeze)
  kill "$XAPP_PID"; sudo kill "$PING_PID"; sudo pkill -x nr-uesoftmodem; ...
  sudo systemctl set-property --runtime "$SLICE" AllowedCPUs=1
}
trap revert EXIT
```
**Por qué:** liberar los 2 cores quita la protección anti-freeze. El `trap … EXIT`
garantiza que, **pase lo que pase** (éxito, error, `kill`, fin normal), el
cpuset vuelve a 1 core y el lab pesado se detiene. Se dispara por el **evento de
término del proceso**, no por un cronómetro.

### 3.3 Precondiciones (falla limpia, sin trabarse)
```bash
pgrep -x nr-softmodem || { err "gNB não está rodando…"; exit 0; }
pgrep -x nearRT-RIC   || { err "RIC não está rodando…";  exit 0; }
[ -x "$XAPP" ]        || { err "xApp KPM não compilado…"; exit 0; }
```
`exit 0` (no 1): la prueba **concluye informando el requisito previo que falta**, en
vez de "fallar". El `trap` igual revierte.

### 3.4 NO toca el cpuset (la corrección de seguridad)
```bash
# (intencionalmente NÃO há set-property AllowedCPUs aqui)
NPROC=$(nproc); GUARD=$(systemctl show "$SLICE" -p AllowedCPUs --value)
[ "$NPROC" -le 2 ] && warn "2 vCPU: o UE provavelmente NÃO vai attachar; p/ dados reais use 4 vCPU"
```
**Por qué:** liberar los 2 cores (quitar el guardrail) fue lo que **congeló el box
dos veces**. El script corre bajo el cpuset vigente y **avisa** si hay solo 2 vCPU. En
4 vCPU el UE attacha sin necesidad de tocar nada. (Versiones antiguas hacían
`AllowedCPUs=0-1` — **removido por seguridad**.)

### 3.5 Loop de intentos (auto-retry)
```bash
while :; do
  attempt=$((attempt+1)); section "Tentativa $attempt de $MAX_TRIES"
  ...
  if [ "$attempt" -ge "$MAX_TRIES" ]; then warn "…concluo COM O QUE HÁ…"; break; fi
  step "repetindo automaticamente…"
done
```
Cada intento levanta el UE limpio. Si no funciona, **reporta el problema y repite**.
Agotados los intentos, **concluye** (no falla).

### 3.6 EVENTO 1 — esperar a que el UE tome IP (con heartbeat DEDUP)
```bash
( ip -o monitor address | grep -qm1 "oaitun_ue1" ) & W_OK=$!          # SUCESSO
( tail -F --pid="$UEPID" "$UE_LOG" | grep -qm1 -E "…contains [0-9]{5}" ) & W_BAD=$!  # FLOOD/morte
( tail -F --pid="$UEPID" "$UE_LOG" \
    | grep -oiE "Initial sync successful|PBCH|Cell Detected|UE synchronized|RRCSetup|Registration (accept|complete)|PDU Session" \
    | awk '!seen[$0]++ { print "  ⏳ UE: " $0 " (marco · NÃO travou)" }' ) & W_HB=$!  # HEARTBEAT DEDUP
wait -n "$W_OK" "$W_BAD"   # retorna no 1º evento (IP, flood ≥10000, ou morte do UE)
```
Tres procesos corriendo: **éxito** (IP vía netlink), **fallo** (flood de RRC =
cola **≥ 5 dígitos / ≥10000**, detectado temprano, o muerte del UE vía `--pid`) y
**heartbeat DEDUP** — `grep -o` extrae solo **hitos** (sync, PBCH, RRCSetup,
Registration, PDU Session) y `awk '!seen[$0]++'` imprime **cada hito una única
vez**. Esto evita los cientos de líneas que la versión antigua generaba (y que aún
le robaban CPU al propio UE). `wait -n` retorna en el primer evento. **`UEPID`** viene
del `MainPID` del scope — los `tail --pid` terminan si el UE muere. Cero `sleep`.

### 3.7 Tráfico + EVENTO 2 — recolectar K indicaciones
```bash
sudo ping -I oaitun_ue1 8.8.8.8 >/dev/null 2>&1 & PING_PID=$!     # tráfego pelo túnel
KPM_SST=222 KPM_SD=123 "$XAPP" "${SMDIR[@]}" > "$LOG" 2>&1 & XAPP_PID=$!
# watchdog ANTI-HANG (por evento): se o UE morre, mata o xApp → o tail abaixo encerra
( tail -f --pid="$UEPID" /dev/null; kill "$XAPP_PID" ) & W_DEATH=$!
# heartbeat por indicação + parada na K-ésima (grep -m K):
while read _; do c=$((c+1)); info "⏳ indicação KPM $c/$NEED_IND (NÃO travou)"; done \
  < <(tail -n +1 -F --pid="$XAPP_PID" "$LOG" | grep --line-buffered -m "$NEED_IND" "KPM ind_msg latency")
```
- `grep -m "$NEED_IND"` termina **exactamente** en la K-ésima indicación → evento de
  éxito. Cada línea leída es un **heartbeat** ("indicación c/K").
- `tail … --pid=$XAPP_PID` termina si el xApp muere.
- El **watchdog** `tail -f --pid=$UEPID /dev/null; kill $XAPP_PID` es el truco que
  **impide que se trabe**: bloquea (sin CPU) hasta que el UE muera y entonces mata el
  xApp, haciendo que el `tail` de la recolección termine. Así, ni "el UE se cayó",
  ni "el xApp detenido" dejan colgado el script — todo por evento.

### 3.8 Veredicto honesto (concluye siempre)
```bash
"$SCRIPT_DIR/kpm_analytics.sh" "$LOG"          # analisa o que coletou
if [ "$got" = 1 ]; then summary "…DADOS reais ($n indicações)…" ok
else summary "…sem atingir a meta — problema: $problem…" warn; fi
```
Corre el análisis sobre el log recolectado y **siempre** da un veredicto: ✓ con datos, o !
concluido-sin-fallar con el problema observado (el UE no attachó / RRC inundó / el
xApp se cayó / por debajo de la meta).

---

## 4. Cómo correr

### 4.1 Por el panel (recomendado en la presentación)
Proyecto 2 → grupo de pruebas → **"Recolectar KPM con tráfico (real, resiliente)"**.
La consola muestra el heartbeat en vivo (reflejado para los alumnos) y, al final, la
explicación "qué pasó". El resultado queda guardado en "Resultados".

### 4.2 Por línea de comandos
```bash
cd ~/server/oai-cn-gnb-e2
# pré-requisito: E2 lab no ar (core + RIC + gNB)
SKIP_UE=1 ./scripts/up_e2_lab_v2.sh      # sobe sem UE (o coletor cuida do UE)
./scripts/kpm_collect_real.sh            # coleta resiliente → logs/xapp_kpm_lab.log
./scripts/kpm_analytics.sh               # (o coletor já chama; rode de novo se quiser)
```
Parámetros (entorno):
- `NEED_IND=20` — cuántas indicaciones recolectar (meta/evento de éxito).
- `MAX_TRIES=3` — intentos antes de concluir-con-lo-que-hay.

---

## 5. Qué ves (salida esperada)

**Trabajando (heartbeat — NÃO travou):**
```
⏳ aguardando UE attachar — gNB sincronizando rádio (… NÃO travou)
⏳ indicação KPM 7/20 recebida (NÃO travou)
```
**Éxito:**
```
✓ UE ATTACHED — oaitun_ue1 = 12.1.1.2
✓ meta atingida: 20 indicações coletadas
… (kpm_analytics: CSV + KPIs por UE + sparkline)
Resultado: concluído com DADOS reais em 1 tentativa(s)
```
**Fallo tratado (concluye sin trabarse):**
```
✗ tentativa 1: PROBLEMA — RRC inundou (CPU insuficiente p/ sincronizar — 2 vCPU é o limite)
→ repetindo automaticamente…
…
Resultado: concluído SEM falhar — problema: … (provável limite de 2 vCPU; ideal 4 vCPU)
```

---

## 6. Por qué NO traba el box (seguridad de CPU)

- **NO toca el cpuset** — el guardrail (1 core para el lab, CPU 0 libre para
  sistema/SSH) queda intacto. Esta es la garantía principal: sin quitar el guardrail,
  el `sshd` nunca se ve ahogado → **no se congela**.
- **Detiene el UE en cuanto detecta una falla** (flood/sin attach) — no deja que la cola RRC
  crezca sin límite (evita presión de memoria).
- El script está **acotado por evento** (IP / flood ≥5 díg / muerte de proceso / K
  indicaciones) — ningún bucle gira para siempre, ningún `sleep` consume CPU en vano.
- Corre **en segundo plano** (`nohup … &`): si el SSH se cae, el recolector continúa, concluye y
  limpia solo; el resultado queda en el archivo.

> **Lección de los 2 freezes:** ambos vinieron de **quitar el guardrail** (liberar 2
> cores) — una vez con un contenedor VPP sin auto-término, otra con este recolector
> atascado esperando un evento que no llegaba mientras el UE inundaba. La corrección
> definitiva fue **nunca tocar el cpuset**; los datos reales quedan para el **upgrade de
> 4 vCPU** (§⚠️ arriba).

---

## 7. Solución de problemas

| Mensaje del script | Significado | Qué hacer |
|---|---|---|
| `RRC inundou (CPU insuficiente…)` | en 2 vCPU el UE no sincroniza en tiempo real | corre en **4 vCPU** (ideal) o acepta el retry |
| `o nrUE caiu antes de pegar IP` | el proceso del UE murió | ver `logs/ue_oai.log`; volver a registrar el suscriptor si es SQN |
| `o xApp KPM encerrou antes da meta` | el xApp se cayó/terminó | verificar `flexric-lib/libkpm_sm.so` (arch arm64) |
| `coletou só N indicações` | el UE attachó pero poco tráfico/tiempo | aumentar `NEED_IND` es contraproducente; asegura el ping activo |
| `gNB/RIC não está rodando` | el lab no está levantado | `./scripts/up_e2_lab_v2.sh` antes |

---

## 8. Dónde encaja esto

```
kpm_collect_real.sh   →  logs/xapp_kpm_lab.log   →  kpm_analytics.sh  →  logs/kpm_timeseries.csv
   (coleta resiliente)        (telemetria real)        (ETL+KPI+viz)         (insumo do modelo)
                                                                                    │
                                                                                    ▼
                                                                      UE-TP-rApp (Módulo 7)
```
La recolección resiliente es el **escalón que faltaba** entre "el E2/KPM funciona" y "tengo
datos reales para modelar". Con 4 vCPU, corre directo; en 2 vCPU, intenta, reporta y
concluye — siempre por evento, nunca por reloj.
