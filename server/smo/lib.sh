# Funções comuns de up_smo.sh / down_smo.sh / test_smo.sh (source, não executar).
# Espera estar em server/smo/ (os scripts fazem cd antes).

set -a; . ./smo.env; set +a
SOL=src/oam/solution   # clone pinado pelo build_arm64.sh (não é alterado)
RUN=run/solution       # cópia de trabalho com os ajustes deste servidor

# As três camadas do upstream, na ordem de subida.
CAMADAS=(smo/common smo/oam network)

# docker compose de uma camada: arquivo do upstream + override nosso, se houver.
# Projeto "smo-<camada>" para não colidir com outras pilhas do servidor.
dc() {
    local camada="$1"; shift
    local nome; nome="$(basename "$camada")"
    local args=(-p "smo-$nome" -f "$RUN/$camada/docker-compose.yaml")
    [ -f "compose/$nome.override.yaml" ] && args+=(-f "compose/$nome.override.yaml")
    docker compose "${args[@]}" "$@"
}

# ---------------------------------------------------------------------------
# Acesso ao SMO no ar — usado pelos testes da apresentação (smo_*.sh).
# Tudo passa pelo gateway em 127.0.0.1, como passaria um operador.
# ---------------------------------------------------------------------------
SMO_DOM="$HTTP_DOMAIN"   # do smo.env; o up_smo.sh aplica o mesmo na cópia de trabalho
MONTAGEM="data/network-topology:network-topology/topology=topology-netconf"

smo_env() { grep -m1 "^$1=" "$RUN/smo/oam/.env" | cut -d= -f2; }

# gw <serviço> [args do curl] <url> — curl no gateway local pelo nome do serviço
gw() { local host="$1.$SMO_DOM"; shift; curl -sk --max-time 25 --resolve "$host:${SMO_HTTPS_PORT}:127.0.0.1" "$@"; }

# restconf <MÉTODO> <caminho sob /rests/> [corpo JSON] [opções extras do curl]
# — a O1 pelo controlador. Ex.: restconf PATCH "$p" "$json" -o /dev/null -w '%{http_code}'
restconf() {
    local args=(-X "$1" -u "$(smo_env ADMIN_USERNAME):$(smo_env ADMIN_PASSWORD)" -H 'Accept: application/yang-data+json')
    local url="https://controller.dcn.$SMO_DOM:${SMO_HTTPS_PORT}/rests/$2"
    [ -n "${3:-}" ] && args+=(-H 'Content-Type: application/yang-data+json' -d "$3")
    shift "$(( $# < 3 ? $# : 3 ))"
    gw controller.dcn "${args[@]}" "$@" "$url"
}

# ves_envia <JSON> — devolve o código HTTP do coletor
ves_envia() {
    gw ves-collector.dcn -u "$(smo_env VES_ENDPOINT_USERNAME):$(smo_env VES_ENDPOINT_PASSWORD)" \
        -H 'Content-Type: application/json' -d "$1" -o /dev/null -w '%{http_code}' \
        "https://ves-collector.dcn.$SMO_DOM:${SMO_HTTPS_PORT}/eventListener/v7"
}

# Kafka pelo kafka-bridge do próprio SMO (HTTP): cada leitura pelo console do
# Kafka subia uma JVM (~6 s); pela ponte, meio segundo. Tópicos de 1 partição.
BRIDGE="https://kafka-bridge.$SMO_DOM:${SMO_HTTPS_PORT}"
kb() { gw kafka-bridge "$@"; }
# kafka_fim <tópico> — offset final (quantos eventos o tópico já recebeu)
kafka_fim() { kb "$BRIDGE/topics/$1/partitions/0/offsets" | python3 -c 'import json,sys; print(json.load(sys.stdin)["end_offset"])' 2>/dev/null || echo 0; }
# kafka_abre <tópico> <offset> — consumidor posicionado no offset; imprime a URL da instância
kafka_abre() {
    local g="core5g-$$-$RANDOM" v2='Content-Type: application/vnd.kafka.v2+json'
    kb -X POST -H "$v2" -o /dev/null -d '{"name":"c","format":"json","enable.auto.commit":false}' "$BRIDGE/consumers/$g"
    kb -X POST -H "$v2" -o /dev/null -d "{\"partitions\":[{\"topic\":\"$1\",\"partition\":0}]}" "$BRIDGE/consumers/$g/instances/c/assignments"
    kb -X POST -H "$v2" -o /dev/null -d "{\"offsets\":[{\"topic\":\"$1\",\"partition\":0,\"offset\":$2}]}" "$BRIDGE/consumers/$g/instances/c/positions"
    echo "$BRIDGE/consumers/$g/instances/c"
}
# kafka_le <instância> [ms] — lista JSON de registros · kafka_fecha <instância>
kafka_le() { kb -H 'Accept: application/vnd.kafka.json.v2+json' "$1/records?timeout=${2:-2000}"; }
kafka_fecha() { kb -X DELETE -o /dev/null "$1"; }

# db <SQL> — banco do controlador (MariaDB do compose, credenciais do upstream)
db() { docker exec persistence mariadb -usdnrdb -psdnrdb sdnrdb -N -B -e "$1" 2>/dev/null; }

# smo_alinha_controlador — cada contêiner novo do controlador escolhe outro
# controllerId, e o banco guarda conexões e alarmes com o id de quem os gravou.
# O ODLUX (Connect, Fault) filtra pelo id atual e mostraria zero, e o controlador
# deixa de atualizar o estado ("Unable to update connection-status"). Põe todas
# as linhas no id atual, lido do log do próprio controlador.
smo_alinha_controlador() {
    local id t
    id="$(docker exec controller sh -c "grep -ohE 'set controllerId [0-9a-f-]{36}' /opt/opendaylight/data/log/karaf.log*" | tail -1 | awk '{print $3}')"
    [ -n "$id" ] || { echo "AVISO: controllerId não encontrado no log do controlador" >&2; return 1; }
    for t in $(db "select table_name from information_schema.columns where table_schema = database() and column_name = 'controller-id'"); do
        db "update \`$t\` set \`controller-id\` = '$id' where \`controller-id\` <> '$id'"
    done
    echo "banco do controlador alinhado ao controllerId $id"
}

# smo_tema_odlux — o console ODLUX do upstream só tem o tema claro. O nginx do
# contêiner (location.rules, montado da cópia de trabalho) injeta no </head> da
# página o tema escuro de odlux/core5g-tema.css, que só vale com o aparelho no
# escuro. Reescreve o bloco entre os marcadores (sem trocar o inode do arquivo
# montado) e recarrega o nginx só quando algo mudou.
smo_tema_odlux() {
    local regras="$RUN/smo/oam/odlux/location.rules" css atual novo
    css="$(tr '\n' ' ' < odlux/core5g-tema.css | sed -E 's#/\*([^*]|\*+[^*/])*\*+/##g; s/[[:space:]]+/ /g')"
    case "$css" in *\'*|*'$'*) echo "AVISO: o tema não pode ter aspas simples nem \$ (vai numa string do nginx)" >&2; return 1 ;; esac
    atual="$(cat "$regras")"
    novo="$(printf '%s\n' "$atual" | awk '/# core5g-tema:inicio/{f=1} !f{print} /# core5g-tema:fim/{f=0}')
# core5g-tema:inicio — tema escuro do console (server/smo/odlux/core5g-tema.css)
location = /odlux/index.html {
    root /opt/bitnami/nginx/html;
    add_header Cache-Control \"no-cache\";
    sub_filter '</head>' '<style id=\"core5g-tema\">${css}</style></head>';
    sub_filter_once on;
}
# core5g-tema:fim"
    [ "$novo" = "$atual" ] && return 0
    printf '%s\n' "$novo" > "$regras.core5g" && cat "$regras.core5g" > "$regras" && rm "$regras.core5g"
    docker exec odlux nginx -t >/dev/null 2>&1 && docker exec odlux nginx -s reload \
        && echo "tema escuro do console ODLUX aplicado" \
        || { echo "AVISO: nginx do odlux recusou o tema; bloco removido" >&2
             printf '%s\n' "$atual" > "$regras.core5g" && cat "$regras.core5g" > "$regras" && rm "$regras.core5g"; return 1; }
}

# Para no começo do teste se o SMO estiver desligado (usa o testlog.sh).
smo_exige_no_ar() {
    if ! docker ps --format '{{.Names}}' | grep -qx controller; then
        err "o SMO não está no ar: o contêiner controller está parado"
        summary "procurou o SMO do O-RAN SC no servidor" "SMO desligado — ligue pelo botão SMO do painel (ou ./up_smo.sh)" err
        return 1
    fi
}

# Imagens do build_arm64.sh que cada camada exige.
imagens_da_camada() {
    case "$1" in
        smo/common) echo "$O_RAN_SC_TOPOLOGY_IMAGE" ;;
        smo/oam)    echo "$SDNC_IMAGE $SDNC_WEB_IMAGE $VES_COLLECTOR_IMAGE" ;;
        network)    echo "${LOCAL_DOCKER_REPO}pynts-o-du-o1:$PYNTS_VERSION ${LOCAL_DOCKER_REPO}pynts-o-ru-mplane:$PYNTS_VERSION" ;;
    esac
}
