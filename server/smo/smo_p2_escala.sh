#!/usr/bin/env bash
# Apresentação SMO · 2ª parte: escalar a pilha. Provisiona uma CÉLULA NOVA na
# O-DU pela O1 — criar, ler, alterar e apagar (CRUD) sobre o modelo 3GPP —,
# conferindo cada passo dentro do equipamento. É o provisionamento de capacidade
# nova numa pilha já em operação.
set -uo pipefail
cd "$(dirname "$0")"
. ./lib.sh
. ../oai-cn-gnb-e2/scripts/lib/testlog.sh
smo_exige_no_ar || exit 1

DU=pynts-o-du-o1
NOVA_ID="NRCellDU-002"
NOVO_PCI=11
NOVO_LOCAL=2

celulas_no_equipamento() {
    docker exec "$DU" sysrepocfg -X -d running -f json -m _3gpp-common-managed-element 2>/dev/null | python3 -c '
import json, sys
du = json.load(sys.stdin)["_3gpp-common-managed-element:ManagedElement"][0]["_3gpp-nr-nrm-gnbdufunction:GNBDUFunction"][0]
for c in du.get("_3gpp-nr-nrm-nrcelldu:NRCellDU", []):
    a = c.get("attributes", {})
    print(c["id"], "PCI=" + str(a.get("nRPCI", "?")), "cellLocalId=" + str(a.get("cellLocalId", "?")))' 2>/dev/null
}
quantas() { celulas_no_equipamento | grep -c . || true; }

section "Escalar a pilha — uma célula nova provisionada pela O1"
info "Capacidade nova numa pilha em operação: criar (POST), ler, alterar (PATCH) e apagar (DELETE) — as operações CRUD da gerência de funções de rede."

ME="$(docker exec "$DU" sysrepocfg -X -d running -f json -m _3gpp-common-managed-element 2>/dev/null)"
read -r ME_ID DU_ID <<<"$(ME="$ME" python3 -c '
import json, os
me = json.loads(os.environ["ME"])["_3gpp-common-managed-element:ManagedElement"][0]
print(me["id"], me["_3gpp-nr-nrm-gnbdufunction:GNBDUFunction"][0]["id"])' 2>/dev/null)"
if [ -z "${DU_ID:-}" ]; then
    err "não achei a gNB-DU no elemento"
    summary "tentou escalar a pilha com uma célula nova" "elemento sem GNBDUFunction" err
    exit 1
fi
BASE="$MONTAGEM/node=$DU/yang-ext:mount/_3gpp-common-managed-element:ManagedElement=$ME_ID/_3gpp-nr-nrm-gnbdufunction:GNBDUFunction=$DU_ID"
NOVA="$BASE/_3gpp-nr-nrm-nrcelldu:NRCellDU=$NOVA_ID"
kv "Elemento" "$DU · $ME_ID / $DU_ID"

section "1. A pilha hoje"
ANTES="$(quantas)"
celulas_no_equipamento | while read -r l; do kv "célula" "$l"; done
kv "Células na O-DU" "$ANTES"
docker exec "$DU" sysrepocfg -X -d running -f json -m _3gpp-common-managed-element 2>/dev/null \
  | grep -q "$NOVA_ID" && { warn "$NOVA_ID já existe no elemento; apagando antes de começar"; restconf DELETE "$NOVA" "" -o /dev/null -w '' >/dev/null; }

section "2. Criar a célula nova (RESTCONF POST → NETCONF edit-config)"
CORPO="$(restconf GET "$BASE/_3gpp-nr-nrm-nrcelldu:NRCellDU=NRCellDU-001" | ID="$NOVA_ID" PCI="$NOVO_PCI" LOC="$NOVO_LOCAL" python3 -c '
import json, os, sys
d = json.load(sys.stdin)["_3gpp-nr-nrm-nrcelldu:NRCellDU"][0]
d["id"] = os.environ["ID"]
a = d.setdefault("attributes", {})
a["nRPCI"] = int(os.environ["PCI"]); a["cellLocalId"] = int(os.environ["LOC"])
print(json.dumps({"_3gpp-nr-nrm-nrcelldu:NRCellDU": [d]}))' 2>/dev/null)"
if [ -z "$CORPO" ]; then
    err "não consegui ler a célula modelo pela O1"
    summary "tentou criar uma célula nova pela O1" "leitura da célula modelo falhou" err
    exit 1
fi
kv "Célula pedida" "$NOVA_ID · PCI $NOVO_PCI · cellLocalId $NOVO_LOCAL (demais atributos herdados da célula 001)"
trap 'restconf DELETE "$NOVA" "" -o /dev/null -w "" >/dev/null 2>&1' EXIT
T0=$(date +%s%3N); COD="$(restconf POST "$BASE" "$CORPO" -o /dev/null -w '%{http_code}')"; T0=$(( $(date +%s%3N) - T0 ))
if [ "$COD" != 201 ] && [ "$COD" != 204 ]; then
    err "o controlador recusou a criação (HTTP $COD)"
    summary "tentou criar a célula $NOVA_ID pela O1" "criação recusada — HTTP $COD" err
    exit 1
fi
ok "célula criada: HTTP $COD em ${T0} ms"

section "3. Conferir dentro do equipamento"
DEPOIS="$(quantas)"
celulas_no_equipamento | while read -r l; do kv "célula" "$l"; done
kv "Células na O-DU" "$DEPOIS (antes: $ANTES)"
celulas_no_equipamento | grep -q "^$NOVA_ID " && ok "a célula nova existe no datastore da O-DU, não só na tela do SMO" \
                                              || { err "a célula nova não apareceu no equipamento"; summary "criou a célula pela O1" "não confirmada no equipamento" err; exit 1; }

section "4. Alterar a célula nova (PATCH no ARFCN)"
COD2="$(restconf PATCH "$NOVA/attributes" '{"_3gpp-nr-nrm-nrcelldu:attributes":{"arfcnDL":640000}}' -o /dev/null -w '%{http_code}')"
ARFCN="$(docker exec "$DU" sysrepocfg -X -d running -f json -m _3gpp-common-managed-element 2>/dev/null | ID="$NOVA_ID" python3 -c '
import json, os, sys
du = json.load(sys.stdin)["_3gpp-common-managed-element:ManagedElement"][0]["_3gpp-nr-nrm-gnbdufunction:GNBDUFunction"][0]
for c in du.get("_3gpp-nr-nrm-nrcelldu:NRCellDU", []):
    if c["id"] == os.environ["ID"]: print(c.get("attributes", {}).get("arfcnDL", "?"))' 2>/dev/null)"
kv "PATCH arfcnDL=640000" "HTTP $COD2 · no equipamento: $ARFCN"
[ "$ARFCN" = 640000 ] && ok "a célula nova já é gerenciada como qualquer outra" || warn "o equipamento não confirmou o ARFCN novo"

section "5. Encerrar a célula (DELETE)"
COD3="$(restconf DELETE "$NOVA" "" -o /dev/null -w '%{http_code}')"
trap - EXIT
FINAL="$(quantas)"
kv "DELETE" "HTTP $COD3"
kv "Células na O-DU" "$FINAL (no começo: $ANTES)"
celulas_no_equipamento | grep -q "^$NOVA_ID " && warn "a célula nova ainda está no equipamento" || ok "a pilha voltou ao tamanho original"

section "6. O que isso mostra sobre a solução"
info "CRUD completo pela O1 sobre o modelo 3GPP: criar, ler, alterar e apagar objetos de rede, com confirmação dentro do equipamento."
info "O que continua fora: não há modelo de serviço que gere essa célula a partir de uma intenção, nem coordenação entre vários elementos — isso seria o SO e o NFO."

if [ "$DEPOIS" -gt "$ANTES" ] && [ "$FINAL" = "$ANTES" ]; then
    summary "criou a célula $NOVA_ID na O-DU pela O1 em ${T0} ms, conferiu no equipamento, alterou o ARFCN e apagou" \
            "escalar a pilha pela O1 funciona ponta a ponta — criar, alterar e apagar objetos de rede, confirmados no elemento" ok
else
    summary "tentou provisionar uma célula nova na pilha pela O1" "o ciclo de criação e remoção não fechou — veja acima" warn
    exit 1
fi
