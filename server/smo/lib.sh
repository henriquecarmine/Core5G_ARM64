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
