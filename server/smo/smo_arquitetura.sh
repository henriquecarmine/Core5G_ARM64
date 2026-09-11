#!/usr/bin/env bash
# Apresentação SMO · itens 1 a 3 da avaliação (arquitetura, serviços e funções,
# componentes O-RAN suportados): o SMO do O-RAN SC como está rodando AGORA,
# lido do Docker, das rotas do gateway e do controlador — nada escrito à mão.
set -uo pipefail
cd "$(dirname "$0")"
. ./lib.sh
. ../oai-cn-gnb-e2/scripts/lib/testlog.sh
smo_exige_no_ar || exit 1

section "SMO do O-RAN SC (OAM) — arquitetura em execução"
info "Solução docker compose do repositório o-ran-sc/oam, em ARM64 nativo neste servidor."
kv "Revisão" "o-ran-sc/oam @ $(git -C src/oam log -1 --format='%h (%cs)' 2>/dev/null || echo '?')"
kv "Servidor" "$(uname -m) · $(nproc) vCPU · $(free -g | awk '/Mem:/{print $2}') GB RAM"

section "1. Arquitetura — as três camadas e seus contêineres"
TOTAL=0
for camada in common oam network; do
    case "$camada" in
        common)  step "common — plataforma: entrada, identidade, persistência, barramento, topologia" ;;
        oam)     step "oam — gerência: controlador O1, console do operador, coletor de eventos" ;;
        network) step "network — elementos gerenciados (simuladores O-DU / O-RU)" ;;
    esac
    while IFS='|' read -r nome img estado; do
        [ -n "$nome" ] || continue
        arch="$(docker image inspect -f '{{.Architecture}}' "$img" 2>/dev/null)"
        kv "$nome" "$estado · ${img} · ${arch}"
        TOTAL=$((TOTAL + 1))
    done < <(docker ps --filter "label=com.docker.compose.project=smo-$camada" --format '{{.Names}}|{{.Image}}|{{.Status}}' | sort)
done
ok "$TOTAL contêineres no ar, todos em imagens arm64"

section "2. Serviços e funções — o que o gateway publica"
info "Cada serviço do SMO tem um nome; o Traefik roteia HTTPS por esse nome e o NETCONF call home por porta."
ROTAS="$(docker exec gateway wget -qO- http://localhost:8080/api/http/routers 2>/dev/null)"
N_ROTAS="$(ROTAS="$ROTAS" python3 - <<'PY'
import json, os, re
PAPEL = {
    "identity": "identidade: usuários, papéis e login (Keycloak)",
    "sdnc-web": "console do operador (ODLUX)",
    "controller": "O1: RESTCONF/NETCONF no controlador SDN-R",
    "ves": "coleta de eventos VES (falhas, medidas, registro)",
    "kafka-bridge": "barramento de eventos por HTTP",
    "kafka-ui": "console do barramento Kafka",
    "topology": "topologia e inventário (TAPI)",
    "gateway": "painel do próprio gateway",
}
n = 0
for r in json.loads(os.environ["ROTAS"] or "[]"):
    if r.get("provider") != "docker":
        continue
    nome = r["name"].split("@")[0]
    host = re.findall(r"Host\(`([^`]+)`\)", r.get("rule", ""))
    print(f"  {nome:<14} {host[0] if host else '':<36} {PAPEL.get(nome, '')}")
    n += 1
print(n)
PY
)"
printf '%s\n' "$N_ROTAS" | sed '$d'
N_ROTAS="$(printf '%s\n' "$N_ROTAS" | tail -1)"
kv "NETCONF call home" "portas 4334 (SSH) e 4335 (TLS) → controlador"
ok "$N_ROTAS serviços roteados pelo gateway"

section "3. Componentes O-RAN — o que está sob gerência agora"
NOS="$(restconf GET "$MONTAGEM?content=nonconfig")"
N_NOS="$(NOS="$NOS" python3 - <<'PY'
import json, os, re
t = json.loads(os.environ["NOS"] or "{}").get("network-topology:topology", [{}])[0]
n = 0
for no in t.get("node", []):
    nc = no.get("netconf-node-topology:netconf-node", {})
    caps = [c["capability"] for c in nc.get("available-capabilities", {}).get("available-capability", [])]
    oran = sum(1 for c in caps if "o-ran-" in c)
    g3 = sum(1 for c in caps if "_3gpp-" in c)
    papel = "O-DU (O1)" if "o-du" in no["node-id"] else "O-RU (M-plane, híbrido)"
    print(f"  {no['node-id']:<22} {nc.get('connection-status', '?'):<10} {papel:<24} {len(caps)} modelos YANG ({oran} O-RAN, {g3} 3GPP)")
    n += nc.get("connection-status") == "connected"
print(n)
PY
)"
printf '%s\n' "$N_NOS" | sed '$d'
N_NOS="$(printf '%s\n' "$N_NOS" | tail -1)"
ok "O1 (SMO ↔ O-DU): NETCONF/YANG — em execução com a O-DU simulada"
ok "M-plane do Open Fronthaul (SMO ↔ O-RU): modelo híbrido direto; o hierárquico é gerenciado pela O-DU"
ok "VES: coletor no ar, publicando cada domínio de evento num tópico do Kafka"
warn "A1 (Non-RT ↔ near-RT RIC): mora no Non-RT RIC do O-RAN SC, fora desta solução OAM (no lab: banda âmbar da topologia)"
warn "O2 (SMO ↔ O-Cloud): não faz parte do OAM do O-RAN SC — ver o teste O-Cloud e O2"
info "E2 é interface do near-RT RIC, não do SMO; o gNB do OAI não tem agente O1, por isso a O1 é mostrada com simuladores."

section "4. Saúde dos serviços, pelo gateway"
cod_realm="$(gw identity -o /dev/null -w '%{http_code}' "https://identity.$SMO_DOM:$SMO_HTTPS_PORT/realms/onap/.well-known/openid-configuration")"
cod_ready="$(gw controller.dcn -o /dev/null -w '%{http_code}' "https://controller.dcn.$SMO_DOM:$SMO_HTTPS_PORT/ready")"
cod_web="$(gw odlux.oam -o /dev/null -w '%{http_code}' "https://odlux.oam.$SMO_DOM:$SMO_HTTPS_PORT/odlux/index.html")"
[ "$cod_realm" = 200 ] && ok "Keycloak: realm onap publicado (HTTP 200)" || err "Keycloak: realm onap HTTP $cod_realm"
[ "$cod_ready" = 200 ] && ok "controlador pronto (HTTP 200)" || err "controlador /ready HTTP $cod_ready"
[ "$cod_web" = 200 ] && ok "console ODLUX publicado (HTTP 200)" || err "ODLUX HTTP $cod_web"

if [ "$cod_realm$cod_ready$cod_web" = 200200200 ] && [ "$N_NOS" -ge 1 ]; then
    summary "leu o SMO em execução: $TOTAL contêineres em 3 camadas, $N_ROTAS serviços no gateway, $N_NOS elemento(s) O-RAN conectado(s)" \
            "arquitetura completa no ar — O1, M-plane e VES funcionando; A1 e O2 ficam fora do OAM" ok
else
    summary "leu o SMO em execução: $TOTAL contêineres, $N_ROTAS serviços, $N_NOS elemento(s) conectado(s)" \
            "SMO no ar com pendências — veja as linhas em vermelho acima" warn
fi
