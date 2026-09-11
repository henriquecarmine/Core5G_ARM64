#!/usr/bin/env bash
# Sobe o SMO do O-RAN SC (repositório oam, solution/) no Graviton, com as
# imagens do build_arm64.sh. Mesma sequência do setup.sh do upstream:
#   smo/common  gateway (Traefik), identity (Keycloak) + identitydb, persistence
#               (MariaDB), zookeeper, kafka, kafka-bridge, kafka-ui, topology
#   usuários e realm no Keycloak (create_users.py + identity/config.py)
#   smo/oam     controller (SDN-R/OpenDaylight, O1 NETCONF), odlux, ves-collector
#   network     simuladores pynts: O-DU (O1) e dois O-RU (M-plane)
#
# Uso: ./up_smo.sh [all|common|oam|network]     (padrão: all)
set -euo pipefail
cd "$(dirname "$0")"
. ./lib.sh
ALVO="${1:-all}"

case "$ALVO" in
    all)     QUAIS=("${CAMADAS[@]}") ;;
    common)  QUAIS=(smo/common) ;;
    oam)     QUAIS=(smo/oam) ;;
    network) QUAIS=(network) ;;
    *) echo "uso: $0 [all|common|oam|network]" >&2; exit 2 ;;
esac

[ -d "$SOL" ] || { echo "ERRO: $SOL não existe — rode ./build_arm64.sh antes." >&2; exit 1; }
falta=0
for camada in "${QUAIS[@]}"; do
    for img in $(imagens_da_camada "$camada"); do
        docker image inspect "$img" >/dev/null 2>&1 \
            || { echo "ERRO: imagem ausente ($camada): $img — ./build_arm64.sh" >&2; falta=1; }
    done
done
[ "$falta" = 0 ] || exit 1

# Cópia de trabalho, feita uma vez (./down_smo.sh --limpar apaga). Faz o que o
# adopt_to_environment.py do upstream faria, trocando o IP do host pelo IP fixo
# do gateway na rede dcn (ver compose/common.override.yaml e smo.env).
if [ ! -f "$RUN/.core5g" ]; then
    echo "== preparando $RUN =="
    mkdir -p "$(dirname "$RUN")"
    rsync -a --delete "$SOL/" "$RUN/"
    grep -rlE 'aaa\.bbb\.ccc\.ddd|\beth0\b' "$RUN" \
        --include='*.yaml' --include='*.json' --include='.env' \
      | xargs -r sed -i -e "s/aaa\.bbb\.ccc\.ddd/${SMO_GATEWAY_IP}/g" \
                        -e "s/\beth0\b/${SMO_HOST_IFACE}/g"
    # O identity/config.py roda num contêiner na rede dmz (abaixo), onde o
    # Keycloak atende como http://identity:8080 — o upstream usa o nome público.
    printf '\n# core5g: config.py do Keycloak roda na rede dmz\nUSE_LOCAL_HOST_FOR_IDENTITY_CONFIG=true\nIDENTITY_PROVIDER_URL_LOCAL_HOST=http://identity:8080\n' \
        >> "$RUN/smo/common/.env"
    touch "$RUN/.core5g"
fi

for camada in "${QUAIS[@]}"; do
    INICIO=$SECONDS
    case "$camada" in
        smo/common)
            echo "== smo/common =="
            # A topologia (NTSim-NG + OpenDaylight) é auxiliar e demora a ficar
            # saudável; não segura o resto: sobe à parte, sem --wait.
            mapfile -t SERVICOS < <(dc smo/common config --services | grep -vx topology)
            dc smo/common up -d --wait --wait-timeout 900 "${SERVICOS[@]}"
            dc smo/common up -d topology
            if [ ! -f "$RUN/.core5g-identity" ]; then
                echo "== usuários e realm no Keycloak =="
                # USER: o config.py cria também um usuário com o nome do usuário
                # Unix (getpass), e o UID do host não existe no /etc/passwd do contêiner.
                docker run --rm --network dmz --user "$(id -u):$(id -g)" -e HOME=/tmp -e USER="$(id -un)" \
                    -e PYTHONPATH=/tmp/py -e PYTHONWARNINGS="ignore:Unverified HTTPS request" \
                    -v "$PWD/$RUN:/solution" -w /solution python:3.12-slim sh -c '
                        pip -q --disable-pip-version-check install --target /tmp/py \
                            jproperties==2.1.2 requests==2.32.3 Jinja2==3.1.4 &&
                        python3 create_users.py users.csv -o smo/common/identity/authentication.json &&
                        python3 smo/common/identity/config.py'
                touch "$RUN/.core5g-identity"   # o realm só é criado uma vez
            fi
            ;;
        smo/oam)
            echo "== smo/oam (o ves-collector-configured é montado aqui, sobre a imagem arm64) =="
            dc smo/oam up -d --build --wait --wait-timeout 900
            ;;
        network)
            echo "== network (simuladores O1 / M-plane) =="
            # Os simuladores fazem o NETCONF call home só ao iniciar: se o
            # controlador reiniciou, só voltam a aparecer recriados. --no-deps
            # para não recriar mais nada junto.
            dc network up -d --force-recreate --no-deps
            ;;
    esac
    echo "   $camada no ar em $(( (SECONDS - INICIO) / 60 )) min $(( (SECONDS - INICIO) % 60 )) s"
done

echo
echo "== contêineres do SMO =="
docker ps --filter label=solution=o-ran-sc-smo --format '{{.Names}}\t{{.Status}}' | sort
docker ps --format '{{.Names}}\t{{.Status}}' | grep -E '^pynts-' | sort || true
echo
echo "Acesso (só localhost): túnel SSH para 127.0.0.1:${SMO_HTTPS_PORT} — ver README.md."
