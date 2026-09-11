#!/usr/bin/env bash
# Verificação do SMO no ar, pelo mesmo caminho que um usuário usaria: HTTPS no
# gateway (Traefik) em 127.0.0.1:${SMO_HTTPS_PORT}, roteado pelo nome do serviço.
# Cada linha é uma evidência para o relatório da cadeira (O1, VES, identidade,
# topologia, barramento). Sai com 1 se alguma verificação essencial falhar.
set -uo pipefail
cd "$(dirname "$0")"
. ./lib.sh

DOM="$(grep -m1 '^HTTP_DOMAIN=' "$RUN/smo/common/.env" | cut -d= -f2)"
ADMIN_USER="$(grep -m1 '^ADMIN_USERNAME=' "$RUN/smo/oam/.env" | cut -d= -f2)"
ADMIN_PASS="$(grep -m1 '^ADMIN_PASSWORD=' "$RUN/smo/oam/.env" | cut -d= -f2)"
VES_USER="$(grep -m1 '^VES_ENDPOINT_USERNAME=' "$RUN/smo/oam/.env" | cut -d= -f2)"
VES_PASS="$(grep -m1 '^VES_ENDPOINT_PASSWORD=' "$RUN/smo/oam/.env" | cut -d= -f2)"
FALHAS=0

# curl no gateway local com o Host certo (sem /etc/hosts).
gw() {
    local host="$1"; shift
    curl -sk --max-time 20 --resolve "$host:${SMO_HTTPS_PORT}:127.0.0.1" "$@" \
        "https://$host:${SMO_HTTPS_PORT}${CAMINHO:-/}"
}
ok()    { printf '  ok    %s\n' "$*"; }
falha() { printf '  FALHA %s\n' "$*"; FALHAS=$((FALHAS + 1)); }
aviso() { printf '  aviso %s\n' "$*"; }

echo "== contêineres =="
while IFS=$'\t' read -r nome estado; do
    case "$estado" in
        *unhealthy*|*Exited*|*Restarting*|Created*) falha "$nome: $estado" ;;
        *) ok "$nome: $estado" ;;
    esac
done < <(docker ps -a --format '{{.Names}}\t{{.Status}}' \
           | grep -E '^(gateway|identity|identitydb|persistence|zookeeper|kafka|kafka-bridge|kafka-ui|topology|controller|odlux|ves-collector|pynts-.*)\b' | sort)

echo "== identidade (Keycloak, realm onap) =="
cod="$(CAMINHO=/realms/onap/.well-known/openid-configuration gw "identity.$DOM" -o /dev/null -w '%{http_code}')"
[ "$cod" = 200 ] && ok "OpenID do realm onap responde (HTTP 200)" || falha "realm onap: HTTP $cod"

echo "== O1: controlador SDN-R (OpenDaylight) =="
cod="$(CAMINHO=/ready gw "controller.dcn.$DOM" -o /dev/null -w '%{http_code}')"
[ "$cod" = 200 ] && ok "controlador pronto (/ready HTTP 200)" || falha "controlador /ready: HTTP $cod"
NOS="$(CAMINHO='/rests/data/network-topology:network-topology/topology=topology-netconf?content=nonconfig' \
       gw "controller.dcn.$DOM" -u "$ADMIN_USER:$ADMIN_PASS" -H 'Accept: application/yang-data+json')"
if echo "$NOS" | grep -q '"node-id"'; then
    NOS="$NOS" python3 - <<'PY'
import json, os
t = json.loads(os.environ["NOS"])["network-topology:topology"][0]
for n in t.get("node", []):
    nc = n.get("netconf-node-topology:netconf-node", {})
    st = nc.get("connection-status", "?")
    marca = "ok   " if st == "connected" else "aviso"
    print(f"  {marca} nó NETCONF {n['node-id']}: {st} "
          f"({nc.get('host', '?')}:{nc.get('port', '?')}, "
          f"{len(nc.get('available-capabilities', {}).get('available-capability', []))} capacidades YANG)")
PY
else
    aviso "nenhum nó NETCONF montado ainda (simuladores fazem call home após subir)"
fi

echo "== VES collector (evento heartbeat de teste) =="
# O VES não tem página de status: a prova é aceitar um evento (202) e publicá-lo
# no Kafka, que é o caminho de falhas e medidas dos equipamentos até o SMO.
AGORA_US="$(date +%s%6N)"
EVENTO="$(printf '{"event":{"commonEventHeader":{"domain":"heartbeat","eventId":"core5g-teste-%s","eventName":"heartbeat_core5g_teste","eventType":"core5g-teste","lastEpochMicrosec":%s,"priority":"Normal","reportingEntityName":"core5g-test_smo","sequence":0,"sourceName":"core5g-test_smo","startEpochMicrosec":%s,"version":"4.1","vesEventListenerVersion":"7.2.1","timeZoneOffset":"-03:00"},"heartbeatFields":{"heartbeatFieldsVersion":"3.0","heartbeatInterval":60}}}' \
    "$AGORA_US" "$AGORA_US" "$AGORA_US")"
cod="$(CAMINHO=/eventListener/v7 gw "ves-collector.dcn.$DOM" -u "$VES_USER:$VES_PASS" \
        -H 'Content-Type: application/json' -d "$EVENTO" -o /dev/null -w '%{http_code}')"
case "$cod" in
    202) ok "VES aceitou o heartbeat (HTTP 202)" ;;
    401) falha "VES recusou as credenciais (HTTP 401)" ;;
    *)   falha "VES não aceitou o evento (HTTP $cod)" ;;
esac

echo "== topologia (NTSim-NG, RESTCONF interno) =="
if docker exec topology curl -s -o /dev/null -w '%{http_code}' -u admin:admin http://localhost:8181 2>/dev/null | grep -qE '^(200|302|401|404)$'; then
    ok "RESTCONF da topologia abriu na 8181"
else
    falha "RESTCONF da topologia não responde na 8181"
fi

echo "== barramento (Kafka) =="
TOPICOS="$(docker exec kafka bin/kafka-topics.sh --bootstrap-server localhost:9092 --list 2>/dev/null \
            | grep -vE '^\s*$|^__' | tr '\n' ' ')"
if echo "$TOPICOS" | grep -qi heartbeat; then
    ok "o heartbeat chegou ao barramento; tópicos: $TOPICOS"
elif [ -n "${TOPICOS// /}" ]; then
    aviso "tópicos existem, mas nenhum de heartbeat: $TOPICOS"
else
    falha "nenhum tópico no Kafka (o VES não publicou)"
fi
# Os simuladores se anunciam ao SMO por VES (pnfRegistration) ao subir.
REG="$(docker exec kafka bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 \
         --topic unauthenticated.VES_PNFREG_OUTPUT --from-beginning --timeout-ms 10000 2>/dev/null \
       | grep -oE '"sourceId":"[^"]+"' | sort -u | sed 's/"sourceId"://' | tr '\n' ' ')"
[ -n "$REG" ] && ok "registro de PNF por VES: $REG" || aviso "nenhum pnfRegistration no Kafka ainda"

echo
echo "== memória =="
docker stats --no-stream --format '  {{.Name}}\t{{.MemUsage}}' | sort
free -h | head -2

echo
[ "$FALHAS" = 0 ] && echo "SMO OK" || echo "SMO com $FALHAS falha(s)"
[ "$FALHAS" = 0 ]
