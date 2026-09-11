#!/usr/bin/env bash
# Apresentação SMO · item 5 (gerenciamento, provisionamento e orquestração): o
# SMO MUDA a configuração de um elemento pela O1 e prova que a mudança chegou
# ao equipamento — depois desfaz. O parâmetro é o nome da gNB-DU (gNBDUName):
# visível, inofensivo e presente no modelo 3GPP que a O-DU anuncia.
set -uo pipefail
cd "$(dirname "$0")"
. ./lib.sh
. ../oai-cn-gnb-e2/scripts/lib/testlog.sh
smo_exige_no_ar || exit 1

NO=pynts-o-du-o1
section "Provisionamento pela O1 — escrever, conferir no equipamento, desfazer"
info "Caminho da escrita: painel → gateway → controlador (RESTCONF PATCH) → NETCONF edit-config → datastore running da O-DU."

ME="$(docker exec "$NO" sysrepocfg -X -d running -f json -m _3gpp-common-managed-element 2>/dev/null)"
read -r ME_ID DU_ID <<<"$(ME="$ME" python3 -c 'import json,os; me=json.loads(os.environ["ME"])["_3gpp-common-managed-element:ManagedElement"][0]; print(me["id"], me["_3gpp-nr-nrm-gnbdufunction:GNBDUFunction"][0]["id"])' 2>/dev/null)"
if [ -z "${DU_ID:-}" ]; then
    err "não achei a gNB-DU no datastore da O-DU"
    summary "tentou provisionar a O-DU pela O1" "elemento sem GNBDUFunction" err
    exit 1
fi
ATTR="$MONTAGEM/node=$NO/yang-ext:mount/_3gpp-common-managed-element:ManagedElement=$ME_ID/_3gpp-nr-nrm-gnbdufunction:GNBDUFunction=$DU_ID/attributes"
le_nome()     { restconf GET "$ATTR/gNBDUName" | python3 -c 'import json,sys; print(json.load(sys.stdin)["_3gpp-nr-nrm-gnbdufunction:gNBDUName"])' 2>/dev/null; }
le_no_equip() { docker exec "$NO" sysrepocfg -X -d running -f json -m _3gpp-common-managed-element 2>/dev/null | python3 -c 'import json,sys; me=json.load(sys.stdin)["_3gpp-common-managed-element:ManagedElement"][0]; print(me["_3gpp-nr-nrm-gnbdufunction:GNBDUFunction"][0]["attributes"]["gNBDUName"])' 2>/dev/null; }
escreve()     { restconf PATCH "$ATTR" "{\"_3gpp-nr-nrm-gnbdufunction:attributes\":{\"gNBDUName\":\"$1\"}}" -o /dev/null -w '%{http_code}'; }

ORIGINAL="$(le_nome)"
NOVO="core5g-apresentacao-$(date +%H%M%S)"
# se algo falhar no meio, o elemento volta ao nome original
trap '[ -n "${ORIGINAL:-}" ] && [ "$(le_nome)" != "$ORIGINAL" ] && escreve "$ORIGINAL" >/dev/null' EXIT

section "1. Estado atual, lido pela O1"
kv "gNBDUName" "$ORIGINAL"

section "2. Escrita (RESTCONF PATCH → NETCONF edit-config)"
kv "Caminho YANG" "ManagedElement=$ME_ID / GNBDUFunction=$DU_ID / attributes"
kv "Corpo" "{\"attributes\": {\"gNBDUName\": \"$NOVO\"}}"
T0=$(date +%s%3N); COD="$(escreve "$NOVO")"; T1=$(date +%s%3N)
if [ "$COD" != 200 ] && [ "$COD" != 204 ]; then
    err "o controlador recusou a escrita (HTTP $COD)"
    summary "tentou provisionar a O-DU pela O1" "escrita recusada — HTTP $COD" err
    exit 1
fi
ok "aceita pelo controlador: HTTP $COD em $((T1 - T0)) ms"

section "3. A mudança chegou ao equipamento?"
PELA_O1="$(le_nome)"; NO_EQUIP="$(le_no_equip)"
kv "lido de novo pela O1" "$PELA_O1"
kv "no datastore da O-DU" "$NO_EQUIP   (sysrepo, dentro do elemento)"
if [ "$PELA_O1" = "$NOVO" ] && [ "$NO_EQUIP" = "$NOVO" ]; then
    ok "o valor novo está no equipamento — não só na tela do SMO"
    APLICOU=1
else
    err "o valor não bateu nos dois lados"
    APLICOU=0
fi

section "4. Desfazer (o mesmo caminho, com o valor original)"
COD2="$(escreve "$ORIGINAL")"
VOLTOU="$(le_no_equip)"
kv "escrita de volta" "HTTP $COD2"
kv "no datastore da O-DU" "$VOLTOU"
[ "$VOLTOU" = "$ORIGINAL" ] && ok "elemento de volta ao estado original" || warn "o elemento não voltou ao nome original"
trap - EXIT

if [ "$APLICOU" = 1 ] && [ "$VOLTOU" = "$ORIGINAL" ]; then
    summary "mudou gNBDUName de '$ORIGINAL' para '$NOVO' pela O1, conferiu dentro da O-DU e desfez" \
            "provisionamento O1 ponta a ponta — escrita confirmada no equipamento e revertida" ok
else
    summary "tentou mudar gNBDUName pela O1 e conferir no equipamento" "provisionamento incompleto — veja acima" err
    exit 1
fi
