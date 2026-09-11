#!/usr/bin/env bash
# Build NATIVO (aarch64) das imagens do SMO O-RAN SC (OAM) que só existem em
# amd64. O resto do SMO (Traefik, Keycloak, PostgreSQL, MariaDB, Kafka) já tem
# imagem oficial multi-arch e não passa por aqui.
#
#   core5g/oam-sdnr:13.0.1-arm64              SDN-R/OpenDaylight (O1, NETCONF)   troca de base
#   core5g/oam-sdnr-web:13.0.1-arm64          ODLUX, a web do SDN-R              troca de base
#   core5g/ves-collector:1.12.5-arm64         VES collector (falhas e medidas)   troca de base
#   core5g/nts-ng-base:1.5.2-arm64            base C do NTSim-NG                 compilada
#   core5g/smo-nts-ng-topology-server:1.5.2-arm64   topologia (TAPI) do SMO      compilada
#   core5g/pynts-o-du-o1:<rev>-arm64          simulador de O-DU com O1           compilado
#   core5g/pynts-o-ru-mplane:<rev>-arm64      simulador de O-RU (M-plane)        compilado
#
# "Troca de base": a imagem oficial é Java sobre uma base x86. Os diretórios da
# aplicação são copiados dela (só COPY, nada amd64 é executado) para a mesma
# família de base em aarch64. Ver os comentários de cada Dockerfile.*.
#
# Rode NO SERVIDOR Graviton. Uso:
#   ./build_arm64.sh            # tudo
#   ./build_arm64.sh rebase     # só as três trocas de base (minutos)
#   ./build_arm64.sh topology   # NTSim-NG base + servidor de topologia (a demora)
#   ./build_arm64.sh pynts      # simuladores O-DU/O-RU
set -euo pipefail
cd "$(dirname "$0")"

# Versões: as que o compose do SMO (repositório oam, OAM_REV) referencia.
SDNR_TAG="${SDNR_TAG:-13.0.1}"
VES_TAG="${VES_TAG:-1.12.5}"
NTS_TAG="${NTS_TAG:-1.5.2}"
OAM_REV="${OAM_REV:-bfdfa32}"      # o-ran-sc/oam, 2025-12-01
PYNTS_REV="${PYNTS_REV:-1212417}"  # o-ran-sc/sim-o1-ofhmp-interfaces, 2025-10-03
ALVO="${1:-all}"

ARCH="$(uname -m)"
if [ "$ARCH" != "aarch64" ] && [ "$ARCH" != "arm64" ]; then
    echo "AVISO: arquitetura $ARCH — as imagens sairão para a arquitetura local," >&2
    echo "não para o servidor Graviton. Prossiga só se for intencional." >&2
fi
command -v docker >/dev/null || { echo "ERRO: docker não encontrado." >&2; exit 1; }

# Clona (raso) e fixa o repositório no commit ou tag pedido.
fonte() {
    local repo="$1" dir="src/$1" ref="$2"
    [ -d "$dir/.git" ] || git clone -q --depth 30 "https://github.com/o-ran-sc/$repo.git" "$dir"
    if ! git -C "$dir" rev-parse -q --verify "$ref^{commit}" >/dev/null; then
        git -C "$dir" fetch -q --depth 1 origin "refs/tags/$ref:refs/tags/$ref" 2>/dev/null \
            || git -C "$dir" fetch -q --depth 300 origin
    fi
    git -C "$dir" checkout -q "$ref"
    echo "   $repo @ $(git -C "$dir" log -1 --format='%h %cs')"
}

etapa() { echo; echo "== $* =="; INICIO=$SECONDS; }
feito() { echo "   pronto em $(( (SECONDS - INICIO) / 60 )) min $(( (SECONDS - INICIO) % 60 )) s"; }

arquitetura_confere() {
    local img="$1" a
    a="$(docker image inspect -f '{{.Architecture}}' "$img")"
    [ "$a" = arm64 ] || { echo "ERRO: $img saiu $a, não arm64" >&2; exit 1; }
    echo "   $img → $a"
}

mkdir -p src
echo "== fontes =="
fonte oam "$OAM_REV"

if [ "$ALVO" = all ] || [ "$ALVO" = rebase ]; then
    etapa "SDN-R ${SDNR_TAG} (troca de base)"
    docker build -f Dockerfile.sdnr --build-arg SDNR_TAG="$SDNR_TAG" \
        -t "core5g/oam-sdnr:${SDNR_TAG}-arm64" .
    arquitetura_confere "core5g/oam-sdnr:${SDNR_TAG}-arm64"; feito

    etapa "ODLUX ${SDNR_TAG} (troca de base)"
    docker build -f Dockerfile.sdnr-web --build-arg SDNR_TAG="$SDNR_TAG" \
        -t "core5g/oam-sdnr-web:${SDNR_TAG}-arm64" .
    arquitetura_confere "core5g/oam-sdnr-web:${SDNR_TAG}-arm64"; feito

    etapa "VES collector ${VES_TAG} (troca de base)"
    docker build -f Dockerfile.ves --build-arg VES_TAG="$VES_TAG" \
        -t "core5g/ves-collector:${VES_TAG}-arm64" .
    arquitetura_confere "core5g/ves-collector:${VES_TAG}-arm64"; feito
fi

if [ "$ALVO" = all ] || [ "$ALVO" = topology ]; then
    fonte sim-o1-interface "$NTS_TAG"
    NTS=src/sim-o1-interface/ntsimulator

    etapa "NTSim-NG base ${NTS_TAG} (libyang, sysrepo, libnetconf2, netopeer2, ntsim-ng em C)"
    docker build -f "$NTS/deploy/base/ubuntu.Dockerfile" \
        --build-arg NTS_BUILD_VERSION="$NTS_TAG" \
        --build-arg NTS_BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        -t "core5g/nts-ng-base:${NTS_TAG}-arm64" "$NTS"
    arquitetura_confere "core5g/nts-ng-base:${NTS_TAG}-arm64"; feito

    etapa "servidor de topologia ${NTS_TAG}"
    # O Dockerfile oficial parte de nexus3.../nts-ng-base:latest (amd64); aqui a
    # base é a recém-compilada. Lido pela entrada padrão para não sujar o clone.
    # EXTRA_JAVA_OPTS: o default-jdk do Ubuntu 20.04 hoje é o OpenJDK 11.0.2x,
    # que valida o campo extra ZIP64 dos jars (JDK-8302483, desde 11.0.20). O
    # Karaf 4.3.3 do OpenDaylight 15.1.0 não passa ("Invalid CEN header") e o
    # RESTCONF nunca abre. A imagem oficial de 2023 escapou por ter um JDK
    # anterior; não é questão de arquitetura. A opção desliga só essa validação.
    { sed "s#^FROM .*nts-ng-base:.*#FROM core5g/nts-ng-base:${NTS_TAG}-arm64#" \
          "$NTS/deploy/smo-nts-ng-topology-server/Dockerfile"
      echo 'ENV EXTRA_JAVA_OPTS="-Djdk.util.zip.disableZip64ExtraFieldValidation=true"'
    } | docker build -f - --build-arg BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
          -t "core5g/smo-nts-ng-topology-server:${NTS_TAG}-arm64" \
          "$NTS/deploy/smo-nts-ng-topology-server"
    arquitetura_confere "core5g/smo-nts-ng-topology-server:${NTS_TAG}-arm64"; feito
fi

if [ "$ALVO" = all ] || [ "$ALVO" = pynts ]; then
    fonte sim-o1-ofhmp-interfaces "$PYNTS_REV"
    etapa "pynts ${PYNTS_REV}: base + O-DU (O1) + O-RU (M-plane)"
    make -C src/sim-o1-ofhmp-interfaces build-all
    for nf in o-du-o1 o-ru-mplane; do
        docker tag "pynts-$nf:latest" "core5g/pynts-$nf:${PYNTS_REV}-arm64"
        arquitetura_confere "core5g/pynts-$nf:${PYNTS_REV}-arm64"
    done
    feito
fi

echo
echo "== imagens core5g do SMO =="
docker images --format '{{.Repository}}:{{.Tag}}  {{.Size}}' \
    | grep -E '^core5g/(oam-|ves-|nts-|smo-|pynts-)' || true
