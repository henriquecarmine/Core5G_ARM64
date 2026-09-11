#!/usr/bin/env bash
# Apresentação SMO · item 8 (gerenciamento de falhas): um alarme percorre o
# caminho real de falhas do SMO — evento VES do elemento → coletor → tópico de
# falhas no Kafka → quem assina — e depois é limpo pelo mesmo caminho.
# A O-DU simulada não traz receita de alarmes, então o teste faz o papel do
# elemento, com o formato VES 7.2.1 que ela usaria.
set -uo pipefail
cd "$(dirname "$0")"
. ./lib.sh
. ../oai-cn-gnb-e2/scripts/lib/testlog.sh
smo_exige_no_ar || exit 1

TOPICO=unauthenticated.SEC_FAULT_OUTPUT
FONTE=pynts-o-du-o1
section "Falhas — um alarme do elemento até o barramento do SMO"
info "Caminho: elemento → VES (HTTPS) → ves-collector → Kafka ($TOPICO) → consumidores (análise, rApps, kafka-ui)."
kv "Elemento" "$FONTE"
kv "Tópico" "$TOPICO"

evento() {  # evento <severidade> <id>
    local us; us="$(date +%s%6N)"
    printf '{"event":{"commonEventHeader":{"domain":"fault","eventId":"%s","eventName":"fault_O-RAN-DU_linkDown","eventType":"O-RAN-DU","lastEpochMicrosec":%s,"priority":"High","reportingEntityName":"%s","sequence":0,"sourceName":"%s","startEpochMicrosec":%s,"version":"4.1","vesEventListenerVersion":"7.2.1","timeZoneOffset":"-03:00"},"faultFields":{"faultFieldsVersion":"4.0","alarmCondition":"linkDown","alarmInterfaceA":"fronthaul-0","eventSeverity":"%s","eventSourceType":"O_RAN_COMPONENT","specificProblem":"enlace do fronthaul caiu (demonstração Core5G)","vfStatus":"Active"}}}' \
        "$2" "$us" "$FONTE" "$FONTE" "$us" "$1"
}

# alarme <severidade> <id> — envia pelo VES e espera o evento aparecer no Kafka.
# Imprime o evento como chegou ao barramento; devolve 1 se não chegar em 15 s.
alarme() {
    local fim t0 cod inst rec achou=""
    fim="$(kafka_fim "$TOPICO")"
    t0=$(date +%s%3N)
    cod="$(ves_envia "$(evento "$1" "$2")")"
    kv "VES → coletor" "HTTP $cod"
    [ "$cod" = 202 ] || return 1
    inst="$(kafka_abre "$TOPICO" "$fim")"
    for _ in $(seq 15); do
        rec="$(kafka_le "$inst" 1000)"
        achou="$(REC="$rec" ID="$2" python3 -c 'import json,os
for r in json.loads(os.environ["REC"] or "[]"):
    if r["value"]["event"]["commonEventHeader"]["eventId"] == os.environ["ID"]:
        print(json.dumps(r["value"])); break' 2>/dev/null)"
        [ -n "$achou" ] && break
    done
    kafka_fecha "$inst"
    [ -n "$achou" ] || return 1
    ok "no tópico de falhas $(( $(date +%s%3N) - t0 )) ms depois do envio"
    LINHA="$achou" python3 - <<'PY'
import json, os
e = json.loads(os.environ["LINHA"])["event"]
h, f = e["commonEventHeader"], e["faultFields"]
print(f"  {'severidade':<22} {f['eventSeverity']}")
print(f"  {'condição':<22} {f['alarmCondition']} em {f.get('alarmInterfaceA', '')}")
print(f"  {'problema':<22} {f['specificProblem']}")
print(f"  {'origem':<22} {h['sourceName']}")
print(f"  {'carimbo do coletor':<22} {h.get('internalHeaderFields', {}).get('collectorTimeStamp', '?')}")
PY
}

ANTES="$(kafka_fim "$TOPICO")"
kv "Eventos no tópico antes" "$ANTES"

ID="core5g-fm-$(date +%s)"
section "1. O elemento levanta o alarme (CRITICAL)"
if ! alarme CRITICAL "$ID"; then
    err "o alarme não chegou ao tópico de falhas"
    summary "tentou levantar um alarme por VES até o Kafka" "o caminho de falhas não entregou o evento" err
    exit 1
fi

section "2. O elemento limpa o alarme (NORMAL)"
alarme NORMAL "$ID-limpo" && LIMPO=1 || { warn "a limpeza não apareceu no Kafka"; LIMPO=0; }

section "3. O que o SMO guarda"
kv "Eventos no tópico agora" "$(kafka_fim "$TOPICO") (antes: $ANTES)"
kv "Alarmes NETCONF no controlador" "$(db 'select count(*) from `faultcurrent-v7`') ativos · $(db 'select count(*) from `faultlog-v7`') no histórico"
info "Os alarmes por VES vão ao barramento; o controlador guarda os que chegam por notificação NETCONF — dois canais de falha da O-RAN."

if [ "$LIMPO" = 1 ]; then
    summary "levantou e limpou um alarme linkDown da O-DU por VES; os dois eventos chegaram ao tópico de falhas do Kafka" \
            "gerenciamento de falhas funcionando: elemento → VES → coletor → Kafka" ok
else
    summary "levantou um alarme por VES até o Kafka; a limpeza não foi confirmada" "falhas parcialmente confirmadas" warn
fi
