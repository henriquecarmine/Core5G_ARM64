#!/usr/bin/env bash
# Apresentação SMO · 2ª parte: provisionar a pilha. Aplica um PLANO DE REDE em
# lote, pela O1, nas funções de rede sob gerência: escreve, confere dentro de
# cada elemento (datastore do próprio equipamento) e desfaz tudo no fim.
# É o coração da 2ª parte: gerenciamento e provisionamento de uma pilha.
set -uo pipefail
cd "$(dirname "$0")"
. ./lib.sh
. ../oai-cn-gnb-e2/scripts/lib/testlog.sh
smo_exige_no_ar || exit 1

DU=pynts-o-du-o1
RU=pynts-o-ru-hybrid
MARCA="$(date +%H%M%S)"

# ---- o elemento visto por dentro (datastore running, via sysrepo) ------------
no_equipamento() {  # no_equipamento <atributo>
    docker exec "$DU" sysrepocfg -X -d running -f json -m _3gpp-common-managed-element 2>/dev/null \
      | ATTR="$1" python3 -c '
import json, os, sys
me = json.load(sys.stdin)["_3gpp-common-managed-element:ManagedElement"][0]
du = me["_3gpp-nr-nrm-gnbdufunction:GNBDUFunction"][0]
cel = du["_3gpp-nr-nrm-nrcelldu:NRCellDU"][0]
valores = dict(du["attributes"])
valores.update(cel["attributes"])
print(valores.get(os.environ["ATTR"], "?"))' 2>/dev/null
}
pela_o1() {  # pela_o1 <url> <chave yang>
    restconf GET "$1" | CH="$2" python3 -c 'import json,os,sys; print(list(json.load(sys.stdin).values())[0].get(os.environ["CH"], "?"))' 2>/dev/null
}
escreve() { restconf PATCH "$1" "$2" -o /dev/null -w '%{http_code}'; }

section "Provisionamento da pilha — um plano de rede aplicado pela O1"
info "Caminho de cada escrita: painel → gateway → controlador (RESTCONF PATCH) → NETCONF edit-config → datastore do elemento."

# ---- descobre a árvore do elemento ------------------------------------------
ME="$(docker exec "$DU" sysrepocfg -X -d running -f json -m _3gpp-common-managed-element 2>/dev/null)"
read -r ME_ID DU_ID CEL_ID <<<"$(ME="$ME" python3 -c '
import json, os
me = json.loads(os.environ["ME"])["_3gpp-common-managed-element:ManagedElement"][0]
du = me["_3gpp-nr-nrm-gnbdufunction:GNBDUFunction"][0]
print(me["id"], du["id"], du["_3gpp-nr-nrm-nrcelldu:NRCellDU"][0]["id"])' 2>/dev/null)"
if [ -z "${CEL_ID:-}" ]; then
    err "não achei a árvore 3GPP na $DU"
    summary "tentou provisionar a pilha pela O1" "elemento sem ManagedElement/GNBDUFunction/NRCellDU" err
    exit 1
fi
BASE_DU="$MONTAGEM/node=$DU/yang-ext:mount/_3gpp-common-managed-element:ManagedElement=$ME_ID/_3gpp-nr-nrm-gnbdufunction:GNBDUFunction=$DU_ID"
BASE_CEL="$BASE_DU/_3gpp-nr-nrm-nrcelldu:NRCellDU=$CEL_ID"
kv "Elemento" "$DU · ManagedElement=$ME_ID / GNBDUFunction=$DU_ID / NRCellDU=$CEL_ID"

# ---- o plano: rótulo | url | chave YANG | corpo do PATCH | valor novo --------
PLANO=(
  "nome da gNB-DU|$BASE_DU/attributes|gNBDUName|_3gpp-nr-nrm-gnbdufunction:attributes|core5g-du-$MARCA"
  "PCI da célula|$BASE_CEL/attributes|nRPCI|_3gpp-nr-nrm-nrcelldu:attributes|7"
  "ARFCN de descida|$BASE_CEL/attributes|arfcnDL|_3gpp-nr-nrm-nrcelldu:attributes|632628"
)
section "1. Estado da pilha antes do plano"
declare -A ORIGINAL
for linha in "${PLANO[@]}"; do
    IFS='|' read -r rotulo url chave _ novo <<<"$linha"
    ORIGINAL[$chave]="$(pela_o1 "$url" "$chave")"
    kv "$rotulo ($chave)" "${ORIGINAL[$chave]}"
done

restaura() {
    for linha in "${PLANO[@]}"; do
        IFS='|' read -r _ url chave corpo _ <<<"$linha"
        orig="${ORIGINAL[$chave]}"
        case "$orig" in ''|'?') continue ;; esac
        case "$orig" in (*[!0-9]*) v="\"$orig\"" ;; (*) v="$orig" ;; esac
        escreve "$url" "{\"$corpo\":{\"$chave\":$v}}" >/dev/null
    done
}
trap restaura EXIT   # qualquer falha no meio devolve a pilha ao estado original

section "2. Aplicar o plano em lote (uma escrita por parâmetro)"
APLICADOS=0; FALHAS=0; T0=$(date +%s%3N)
for linha in "${PLANO[@]}"; do
    IFS='|' read -r rotulo url chave corpo novo <<<"$linha"
    case "$novo" in (*[!0-9]*) v="\"$novo\"" ;; (*) v="$novo" ;; esac
    t=$(date +%s%3N); cod="$(escreve "$url" "{\"$corpo\":{\"$chave\":$v}}")"; t=$(( $(date +%s%3N) - t ))
    if [ "$cod" = 200 ] || [ "$cod" = 204 ]; then
        kv "$rotulo" "$chave = $novo · HTTP $cod em ${t}ms"
        APLICADOS=$((APLICADOS + 1))
    else
        err "$rotulo ($chave): o controlador recusou — HTTP $cod"
        FALHAS=$((FALHAS + 1))
    fi
done
LOTE=$(( $(date +%s%3N) - T0 ))
[ "$APLICADOS" -gt 0 ] && ok "$APLICADOS parâmetro(s) aplicados na pilha em ${LOTE} ms"

section "3. Conferir dentro do equipamento (não na tela do SMO)"
CONFEREM=0
for linha in "${PLANO[@]}"; do
    IFS='|' read -r rotulo url chave _ novo <<<"$linha"
    o1="$(pela_o1 "$url" "$chave")"; dentro="$(no_equipamento "$chave")"
    if [ "$o1" = "$novo" ] && [ "$dentro" = "$novo" ]; then
        kv "$rotulo" "pela O1: $o1 · no datastore da O-DU: $dentro ✓"
        CONFEREM=$((CONFEREM + 1))
    else
        warn "$rotulo: pela O1 '$o1' · no equipamento '$dentro' (esperado '$novo')"
    fi
done
[ "$CONFEREM" = "${#PLANO[@]}" ] && ok "todo o plano chegou ao equipamento" || warn "parte do plano não foi confirmada no equipamento"

section "4. O que o SMO NÃO faz aqui"
info "Cada parâmetro é uma escrita independente: não há transação entre elementos, nem modelo de serviço ou fluxo de trabalho."
info "Se uma escrita falhar no meio, quem desfaz é o operador — neste teste, o próprio script."

section "5. Desfazer o plano (rollback conduzido pelo operador)"
restaura; trap - EXIT
VOLTOU=0
for linha in "${PLANO[@]}"; do
    IFS='|' read -r rotulo _ chave _ _ <<<"$linha"
    dentro="$(no_equipamento "$chave")"
    [ "$dentro" = "${ORIGINAL[$chave]}" ] && { kv "$rotulo" "de volta a $dentro"; VOLTOU=$((VOLTOU + 1)); } \
                                          || warn "$rotulo ficou em '$dentro' (original '${ORIGINAL[$chave]}')"
done
[ "$VOLTOU" = "${#PLANO[@]}" ] && ok "pilha de volta ao estado original" || warn "a pilha não voltou inteira ao estado original"

if [ "$FALHAS" = 0 ] && [ "$CONFEREM" = "${#PLANO[@]}" ] && [ "$VOLTOU" = "${#PLANO[@]}" ]; then
    summary "aplicou um plano de rede de ${#PLANO[@]} parâmetros na pilha pela O1 em ${LOTE} ms, conferiu dentro do equipamento e desfez" \
            "provisionamento da pilha ponta a ponta — escritas confirmadas no elemento e revertidas" ok
else
    summary "aplicou $APLICADOS de ${#PLANO[@]} parâmetros do plano pela O1" \
            "provisionamento parcial — veja as linhas em vermelho" warn
    exit 1
fi
