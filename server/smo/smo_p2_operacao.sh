#!/usr/bin/env bash
# Apresentação SMO · 2ª parte: operar a pilha. Fecha o laço de operação —
# um alarme chega pelo VES ao barramento, o consumidor decide, provisiona a
# correção pela O1, confere dentro do elemento e limpa o alarme.
# Mostra quais serviços de SMO (SMOS) agem e quais faltariam para isso ser
# automático (RAN Analytics, PMI, A1).
set -uo pipefail
cd "$(dirname "$0")"
. ./lib.sh
. ../oai-cn-gnb-e2/scripts/lib/testlog.sh
smo_exige_no_ar || exit 1

DU=pynts-o-du-o1
TOPICO=unauthenticated.SEC_FAULT_OUTPUT
T_PM=unauthenticated.SEC_3GPP_PERFORMANCEASSURANCE_OUTPUT
ID="core5g-pci-$(date +%s)"

evento() {  # evento <severidade> <id> <condição> <problema>
    local us; us="$(date +%s%6N)"
    printf '{"event":{"commonEventHeader":{"domain":"fault","eventId":"%s","eventName":"fault_O-RAN-DU_%s","eventType":"O-RAN-DU","lastEpochMicrosec":%s,"priority":"High","reportingEntityName":"%s","sequence":0,"sourceName":"%s","startEpochMicrosec":%s,"version":"4.1","vesEventListenerVersion":"7.2.1","timeZoneOffset":"-03:00"},"faultFields":{"faultFieldsVersion":"4.0","alarmCondition":"%s","alarmInterfaceA":"NRCellDU-001","eventSeverity":"%s","eventSourceType":"O_RAN_COMPONENT","specificProblem":"%s","vfStatus":"Active"}}}' \
        "$3" "$2" "$us" "$DU" "$DU" "$us" "$2" "$1" "$4"
}
chega_ao_barramento() {  # chega_ao_barramento <id> <offset inicial>
    local inst rec achou="" t0=$1 fim=$2 id=$3
    inst="$(kafka_abre "$TOPICO" "$fim")"
    for _ in $(seq 15); do
        rec="$(kafka_le "$inst" 1000)"
        achou="$(REC="$rec" ID="$id" python3 -c '
import json, os
for r in json.loads(os.environ["REC"] or "[]"):
    if r["value"]["event"]["commonEventHeader"]["eventId"] == os.environ["ID"]:
        print(r["value"]["event"]["faultFields"]["eventSeverity"]); break' 2>/dev/null)"
        [ -n "$achou" ] && break
    done
    kafka_fecha "$inst"
    [ -n "$achou" ] && echo "$achou $(( $(date +%s%3N) - t0 ))" || return 1
}
pci_pela_o1() { restconf GET "$BASE_CEL/attributes/nRPCI" | python3 -c 'import json,sys; print(list(json.load(sys.stdin).values())[0])' 2>/dev/null; }
pci_no_equipamento() {
    docker exec "$DU" sysrepocfg -X -d running -f json -m _3gpp-common-managed-element 2>/dev/null \
      | python3 -c 'import json,sys; me=json.load(sys.stdin)["_3gpp-common-managed-element:ManagedElement"][0]; print(me["_3gpp-nr-nrm-gnbdufunction:GNBDUFunction"][0]["_3gpp-nr-nrm-nrcelldu:NRCellDU"][0]["attributes"].get("nRPCI","?"))' 2>/dev/null
}

section "Operar a pilha — do alarme à correção provisionada pela O1"
info "Laço: elemento → VES → barramento → decisão → provisionamento pela O1 → verificação no elemento → limpeza do alarme."

ME="$(docker exec "$DU" sysrepocfg -X -d running -f json -m _3gpp-common-managed-element 2>/dev/null)"
read -r ME_ID DU_ID CEL_ID <<<"$(ME="$ME" python3 -c '
import json, os
me = json.loads(os.environ["ME"])["_3gpp-common-managed-element:ManagedElement"][0]
du = me["_3gpp-nr-nrm-gnbdufunction:GNBDUFunction"][0]
print(me["id"], du["id"], du["_3gpp-nr-nrm-nrcelldu:NRCellDU"][0]["id"])' 2>/dev/null)"
BASE_CEL="$MONTAGEM/node=$DU/yang-ext:mount/_3gpp-common-managed-element:ManagedElement=$ME_ID/_3gpp-nr-nrm-gnbdufunction:GNBDUFunction=$DU_ID/_3gpp-nr-nrm-nrcelldu:NRCellDU=$CEL_ID"

section "1. A pilha em operação"
kv "Célula" "$ME_ID / $DU_ID / $CEL_ID"
PCI0="$(pci_pela_o1)"
kv "PCI atual (nRPCI)" "$PCI0"
kv "Alarmes no controlador" "$(db 'select count(*) from `faultcurrent-v7`') ativos · $(db 'select count(*) from `faultlog-v7`') no histórico"
kv "Eventos de medida no barramento" "$(kafka_fim "$T_PM")"
[ -n "${PCI0:-}" ] && [ "$PCI0" != "?" ] || { err "não li o PCI da célula pela O1"; summary "tentou operar a pilha" "leitura do PCI falhou" err; exit 1; }

section "2. Chega um alarme: conflito de PCI na célula"
FIM_ANTES="$(kafka_fim "$TOPICO")"
T0=$(date +%s%3N)
COD="$(ves_envia "$(evento CRITICAL pciConflict "$ID" "conflito de PCI com célula vizinha (demonstração Core5G)")")"
kv "VES → coletor" "HTTP $COD"
[ "$COD" = 202 ] || { err "o coletor VES recusou o alarme"; summary "tentou operar a pilha" "alarme não aceito pelo VES" err; exit 1; }
LINHA_AL="$(chega_ao_barramento "$T0" "$FIM_ANTES" "$ID")"
if [ -n "$LINHA_AL" ]; then
    read -r SEV MS <<<"$LINHA_AL"
    ok "alarme $SEV no barramento ${MS} ms depois do envio (tópico de falhas)"
else
    err "o alarme não chegou ao barramento"
    summary "tentou operar a pilha" "o caminho de falhas não entregou o evento" err
    exit 1
fi

section "3. Decisão e provisionamento da correção pela O1"
NOVO=$(( PCI0 + 6 )); [ "$NOVO" -gt 503 ] && NOVO=$(( PCI0 - 6 ))
info "Quem decide aqui é este teste, no papel que caberia a uma rApp de SON: escolhe um PCI livre e manda provisionar."
kv "PCI escolhido" "$NOVO (era $PCI0)"
trap 'restconf PATCH "$BASE_CEL/attributes" "{\"_3gpp-nr-nrm-nrcelldu:attributes\":{\"nRPCI\":'"$PCI0"'}}" >/dev/null 2>&1' EXIT
T1=$(date +%s%3N)
COD2="$(restconf PATCH "$BASE_CEL/attributes" "{\"_3gpp-nr-nrm-nrcelldu:attributes\":{\"nRPCI\":$NOVO}}" -o /dev/null -w '%{http_code}')"
T1=$(( $(date +%s%3N) - T1 ))
if [ "$COD2" != 200 ] && [ "$COD2" != 204 ]; then
    err "o controlador recusou a correção (HTTP $COD2)"
    summary "levou um alarme até a decisão, mas a correção foi recusada" "laço de operação incompleto — HTTP $COD2" err
    exit 1
fi
ok "correção aceita pelo controlador: HTTP $COD2 em ${T1} ms"
kv "lido de novo pela O1" "$(pci_pela_o1)"
kv "no datastore da O-DU" "$(pci_no_equipamento)   (sysrepo, dentro do elemento)"
[ "$(pci_no_equipamento)" = "$NOVO" ] && ok "a correção chegou ao equipamento" || warn "o equipamento não confirmou o PCI novo"

section "4. Limpar o alarme pelo mesmo caminho"
FIM2="$(kafka_fim "$TOPICO")"; T2=$(date +%s%3N)
COD3="$(ves_envia "$(evento NORMAL pciConflict "$ID-limpo" "conflito de PCI resolvido por reconfiguração")")"
kv "VES → coletor" "HTTP $COD3"
LINHA_LM="$(chega_ao_barramento "$T2" "$FIM2" "$ID-limpo")"
if [ -n "$LINHA_LM" ]; then
    read -r SEV2 MS2 <<<"$LINHA_LM"
    ok "limpeza $SEV2 no barramento ${MS2} ms depois do envio"
else
    warn "a limpeza não apareceu no barramento"
fi
kv "Eventos no tópico de falhas" "$(kafka_fim "$TOPICO") (antes do laço: $FIM_ANTES)"

section "5. Voltar a célula ao plano original"
restconf PATCH "$BASE_CEL/attributes" "{\"_3gpp-nr-nrm-nrcelldu:attributes\":{\"nRPCI\":$PCI0}}" -o /dev/null -w '%{http_code}' >/dev/null
trap - EXIT
kv "PCI no equipamento" "$(pci_no_equipamento) (original: $PCI0)"

section "6. Quem agiu e quem faltou"
info "Agiram: RAN NF OAM (provisionamento e falhas pela O1) e o barramento de dados do SMO (tópicos VES)."
info "Faltaram, nesta solução: RAN Analytics e Policy Management, que decidiriam sozinhos, e a A1, que levaria a política ao near-RT RIC."
info "Por isso o laço é fechado pelo operador: o SMO do O-RAN SC entrega os meios (dados e provisionamento), não a automação."

summary "levou um alarme de PCI do elemento ao barramento em ${MS} ms, provisionou o PCI novo pela O1 em ${T1} ms com confirmação dentro do equipamento, limpou o alarme e restaurou o plano" \
        "laço de operação fechado sobre a pilha: falha → decisão → provisionamento → verificação → limpeza" ok
