#!/usr/bin/env bash
# Apresentação SMO · item 7 (ciclo de vida de Network Functions): encerra e
# reinstancia uma função de rede e mede como o SMO percebe cada fase — a conexão
# cai, o elemento volta, liga para o SMO (call home) e é montado de novo.
# A orquestração do contêiner é do Docker: num O-RAN completo, quem instancia e
# encerra é o O-Cloud pelo O2 (DMS). O que o SMO vê é o mesmo.
set -uo pipefail
cd "$(dirname "$0")"
. ./lib.sh
. ../oai-cn-gnb-e2/scripts/lib/testlog.sh
smo_exige_no_ar || exit 1

NF="${SMO_NF:-pynts-o-ru-hybrid}"
section "Ciclo de vida — encerrar e reinstanciar uma função de rede"
info "Fases: em operação → encerrar → SMO percebe a queda → instanciar → call home → montado e conectado."
kv "Função de rede" "$NF"

estado() { restconf GET "$MONTAGEM/node=$NF?content=nonconfig" | python3 -c 'import json,sys; print(json.load(sys.stdin)["network-topology:node"][0]["netconf-node-topology:netconf-node"].get("connection-status","?"))' 2>/dev/null || echo ausente; }
espera_estado() {  # espera_estado <regex> <segundos> — imprime o estado final e os segundos
    local t0=$SECONDS s
    while :; do
        s="$(estado)"
        [[ "$s" =~ $1 ]] && { echo "$s $((SECONDS - t0))"; return 0; }
        (( SECONDS - t0 >= $2 )) && { echo "$s $((SECONDS - t0))"; return 1; }
        sleep 2
    done
}
trap 'docker start "$NF" >/dev/null 2>&1' EXIT   # nunca deixa a função de rede parada

INICIO="$(date -u '+%Y-%m-%d %H:%M:%S')"   # o connectionlog grava em UTC
section "1. Em operação"
E0="$(estado)"
kv "no controlador" "$E0"
[ "$E0" = connected ] || warn "a função de rede não estava conectada no início"

section "2. Encerrar (docker stop)"
docker stop "$NF" >/dev/null && ok "contêiner $NF encerrado"
read -r E1 S1 <<<"$(espera_estado '^(connecting|unable-to-connect|ausente)$' 90)"
kv "o SMO percebeu" "$E1 em ${S1}s"
[ "$E1" != connected ] && ok "o controlador registrou a perda do elemento" || warn "o controlador ainda mostra conectado"

section "3. Instanciar de novo (docker start)"
docker start "$NF" >/dev/null && ok "contêiner $NF iniciado"
read -r E2 S2 <<<"$(espera_estado '^connected$' 180)"
kv "call home → montado" "$E2 em ${S2}s"
trap - EXIT
if [ "$E2" != connected ]; then
    err "a função de rede não voltou a se conectar ao SMO"
    summary "encerrou e reinstanciou $NF" "o elemento não reconectou em 180 s" err
    exit 1
fi
ok "o elemento ligou para o SMO e foi montado de novo, sem ninguém configurar nada no controlador"

section "4. O que ficou registrado no SMO (connectionlog)"
db "select date_format(\`timestamp\`, '%H:%i:%s.%f'), status from \`connectionlog-v7\` where \`node-id\` = '$NF' and \`timestamp\` >= '$INICIO' order by \`timestamp\`" \
  | while IFS=$'\t' read -r quando status; do kv "${quando:0:12}" "$status"; done
CAPS="$(restconf GET "$MONTAGEM/node=$NF?content=nonconfig" | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["network-topology:node"][0]["netconf-node-topology:netconf-node"]["available-capabilities"]["available-capability"]))' 2>/dev/null)"
kv "capacidades de novo" "${CAPS:-?} modelos YANG"

summary "encerrou $NF, viu o SMO registrar a queda em ${S1}s, reinstanciou e o elemento voltou montado em ${S2}s" \
        "ciclo de vida percebido pelo SMO: encerrar → perda → instanciar → call home → conectado" ok
