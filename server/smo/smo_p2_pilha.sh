#!/usr/bin/env bash
# Apresentação SMO · 2ª parte (provisionamento e gerenciamento de uma pilha
# Open RAN): instancia a pilha de funções de rede e mede quanto tempo o SMO leva
# para colocar cada uma sob gerência, sem ninguém configurar o controlador.
# Quem instancia é o Docker (o papel que caberia ao O-Cloud pela O2 DMS); o que
# se mede aqui é o que o SMO faz: descobrir, montar e inventariar.
set -uo pipefail
cd "$(dirname "$0")"
. ./lib.sh
. ../oai-cn-gnb-e2/scripts/lib/testlog.sh
smo_exige_no_ar || exit 1

PILHA=(pynts-o-du-o1 pynts-o-ru-hybrid pynts-o-ru-hierarchical)
SOB_GERENCIA=(pynts-o-du-o1 pynts-o-ru-hybrid)   # o hierárquico é gerenciado pela O-DU
PAPEL_pynts_o_du_o1="O-DU · O1 (NETCONF/TLS)"
PAPEL_pynts_o_ru_hybrid="O-RU · M-plane híbrido (NETCONF/SSH)"
PAPEL_pynts_o_ru_hierarchical="O-RU · M-plane hierárquico (via O-DU)"
papel() { local v="PAPEL_${1//-/_}"; echo "${!v:-função de rede}"; }

estado() {
    restconf GET "$MONTAGEM/node=$1?content=nonconfig" \
      | python3 -c 'import json,sys; print(json.load(sys.stdin)["network-topology:node"][0]["netconf-node-topology:netconf-node"].get("connection-status","?"))' 2>/dev/null || echo ausente
}
inventario() {  # imprime "<node> <estado> <nº de modelos>" de tudo o que está montado
    restconf GET "$MONTAGEM?content=nonconfig" | python3 -c '
import json, sys
t = json.load(sys.stdin).get("network-topology:topology", [{}])[0]
for no in t.get("node", []):
    nc = no.get("netconf-node-topology:netconf-node", {})
    caps = nc.get("available-capabilities", {}).get("available-capability", [])
    print(no["node-id"], nc.get("connection-status", "?"), len(caps))
' 2>/dev/null
}
conta_montados() { inventario | grep -c connected || true; }

section "Pilha Open RAN — instanciar as funções de rede e pô-las sob gerência"
info "Ordem real de uma implantação: as NFs sobem, ligam para o SMO (call home) e o SMO as monta e inventaria sozinho."
kv "Pilha" "${#PILHA[@]} funções de rede simuladas (pynts)"
for nf in "${PILHA[@]}"; do kv "  $nf" "$(papel "$nf")"; done

section "1. Inventário do SMO antes"
ANTES="$(conta_montados)"
inventario | while read -r no est caps; do kv "$no" "$est · $caps modelos YANG"; done
kv "Elementos conectados" "$ANTES"

section "2. Encerrar a pilha (o O-Cloud faria isso pela O2 DMS; aqui, o Docker)"
T0=$(date +%s)
docker stop "${PILHA[@]}" >/dev/null 2>&1 && ok "as ${#PILHA[@]} funções de rede foram encerradas"
trap 'docker start "${PILHA[@]}" >/dev/null 2>&1' EXIT   # nunca deixa a pilha parada
for _ in $(seq 45); do
    [ "$(conta_montados)" = 0 ] && break
    sleep 2
done
kv "O SMO esvaziou o inventário em" "$(( $(date +%s) - T0 ))s"
RESTAM="$(conta_montados)"
[ "$RESTAM" = 0 ] && ok "nenhum elemento conectado: a pilha saiu do ar" || warn "ainda há $RESTAM elemento(s) conectado(s)"

section "3. Instanciar a pilha de novo"
T0=$(date +%s)
docker start "${PILHA[@]}" >/dev/null 2>&1 && ok "as ${#PILHA[@]} funções de rede foram instanciadas"
declare -A TEMPO
PENDENTES=("${SOB_GERENCIA[@]}")
for _ in $(seq 90); do
    NOVOS=()
    for nf in "${PENDENTES[@]}"; do
        if [ "$(estado "$nf")" = connected ]; then
            TEMPO[$nf]=$(( $(date +%s) - T0 ))
            kv "$nf" "connected em ${TEMPO[$nf]}s  ($(papel "$nf"))"
        else
            NOVOS+=("$nf")
        fi
    done
    PENDENTES=("${NOVOS[@]}")
    [ "${#PENDENTES[@]}" -eq 0 ] && break
    sleep 2
done
trap - EXIT
TOTAL=$(( $(date +%s) - T0 ))
if [ "${#PENDENTES[@]}" -ne 0 ]; then
    err "não entraram sob gerência em ${TOTAL}s: ${PENDENTES[*]}"
    summary "instanciou a pilha de ${#PILHA[@]} funções de rede" "nem todas voltaram à gerência do SMO" err
    exit 1
fi
ok "toda a pilha sob gerência em ${TOTAL}s, sem tocar na configuração do controlador"
info "O $(echo "${PILHA[2]}") não aparece no inventário de propósito: no M-plane hierárquico quem o gerencia é a O-DU."

section "4. Inventário do SMO depois"
inventario | while read -r no est caps; do kv "$no" "$est · $caps modelos YANG"; done
kv "Elementos conectados" "$(conta_montados) (antes: $ANTES)"

section "5. O que o SMO registrou de cada função de rede"
for nf in "${SOB_GERENCIA[@]}"; do
    LINHAS="$(db "select date_format(\`timestamp\`, '%H:%i:%s'), status from \`connectionlog-v7\` where \`node-id\` = '$nf' order by \`timestamp\` desc limit 3" | tac)"
    kv "$nf" "$(echo "$LINHAS" | awk '{printf "%s %s · ", $2, $1}' | sed 's/ · $//')"
done
info "É o inventário e o histórico que sustentam o provisionamento: o SMO só configura o que descobriu."

summary "encerrou e instanciou uma pilha de ${#PILHA[@]} funções de rede; o SMO as descobriu por call home e montou ${#SOB_GERENCIA[@]} sob gerência em ${TOTAL}s" \
        "pilha Open RAN instanciada e sob gerência do SMO — descoberta, montagem e inventário automáticos" ok
