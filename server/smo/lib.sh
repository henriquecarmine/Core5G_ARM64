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

# Imagens do build_arm64.sh que cada camada exige.
imagens_da_camada() {
    case "$1" in
        smo/common) echo "$O_RAN_SC_TOPOLOGY_IMAGE" ;;
        smo/oam)    echo "$SDNC_IMAGE $SDNC_WEB_IMAGE $VES_COLLECTOR_IMAGE" ;;
        network)    echo "${LOCAL_DOCKER_REPO}pynts-o-du-o1:$PYNTS_VERSION ${LOCAL_DOCKER_REPO}pynts-o-ru-mplane:$PYNTS_VERSION" ;;
    esac
}
