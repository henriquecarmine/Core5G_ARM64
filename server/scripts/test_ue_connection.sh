#!/bin/bash
# Teste de conexão fim-a-fim do UE (Projeto 1 — Open5GS + UERANSIM).
# Verifica, na ordem real da operação, que o UE registrado consegue usar a rede:
# ping a DNS públicos → resolução DNS → acesso HTTP (IP público) → rota padrão →
# alcance dos UPFs → registro N2/PFCP. Saída didática (cor + Resumo) padronizada
# pela lib/testlog.sh, igual aos demais relatórios do painel.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"
# shellcheck source=lib/testlog.sh
source "$SCRIPT_DIR/lib/testlog.sh"

UE_CONTAINER="ueransim"
TEST_HOSTS=("8.8.8.8" "8.8.4.4" "1.1.1.1")
TEST_URLS=("http://ifconfig.me" "http://icanhazip.com")
fails=0; warns=0

section "Conectividade fim-a-fim do UE — Projeto 1 (UERANSIM ↔ Open5GS)"

# Pré-condição: container do UE no ar -------------------------------------------
if ! docker inspect -f '{{.State.Status}}' "$UE_CONTAINER" 2>/dev/null | grep -q running; then
    err "Container $UE_CONTAINER não está rodando — suba o RAN (./scripts/up_ran.sh)."
    summary "tentou validar a conectividade fim-a-fim do UE" \
            "RAN do Projeto 1 fora do ar — ative o Projeto 1 e o servidor RAN" err
    exit 0
fi
ok "Container $UE_CONTAINER em execução."

# Pré-condição: UE tem IP (sessão PDU ativa) -----------------------------------
UE_ACTUAL_IP=$(docker exec "$UE_CONTAINER" ip addr show 2>/dev/null | grep -oP 'inet \K10\.60\.\d+\.\d+' | head -1 || echo "")
if [ -z "$UE_ACTUAL_IP" ]; then
    err "UE sem IP em uesimtun0 — a sessão PDU não subiu (registro 5G-AKA + SMF/UPF)."
    summary "tentou validar a conectividade fim-a-fim do UE" \
            "UE sem IP/sessão PDU — registre o assinante e reinicie o UE" err
    exit 0
fi
ok "Sessão PDU ativa — UE com IP $UE_ACTUAL_IP."

# Teste 1: ping a DNS públicos (egressão pelo túnel 5G) -------------------------
section "1/6 · Alcance da internet (ping a DNS públicos)"
step "Por quê: prova que o tráfego do UE sai pelo núcleo 5G até a internet e volta."
ping_ok=0
for host in "${TEST_HOSTS[@]}"; do
    if docker exec "$UE_CONTAINER" ping -c 2 -W 2 "$host" >/dev/null 2>&1; then
        RTT=$(docker exec "$UE_CONTAINER" ping -c 2 -W 2 "$host" 2>&1 | grep "avg" | awk -F'/' '{print $5}')
        ok "$host respondeu (RTT médio ${RTT:-?} ms)."; ping_ok=$((ping_ok+1))
    else
        warn "$host não respondeu."
    fi
done
[ "$ping_ok" -eq 0 ] && { err "Nenhum DNS público respondeu — sem egressão (verifique UPF/N6)."; fails=$((fails+1)); }

# Teste 2: resolução DNS -------------------------------------------------------
section "2/6 · Resolução de nomes (DNS)"
step "Por quê: navegar exige traduzir nomes em IPs; valida o DNS configurado na sessão."
TEST_DOMAIN="google.com"
if docker exec "$UE_CONTAINER" nslookup "$TEST_DOMAIN" >/dev/null 2>&1; then
    IP=$(docker exec "$UE_CONTAINER" nslookup "$TEST_DOMAIN" 2>&1 | grep -A1 "Name:" | grep "Address:" | awk '{print $2}' | head -1)
    ok "$TEST_DOMAIN resolveu para ${IP:-?}."
else
    warn "Falha ao resolver $TEST_DOMAIN (DNS da sessão PDU)."; warns=$((warns+1))
fi

# Teste 3: acesso HTTP + IP público --------------------------------------------
section "3/6 · Acesso HTTP e IP público"
step "Por quê: confirma navegação real e mostra com qual IP público o UE aparece na internet."
http_ok=0
for url in "${TEST_URLS[@]}"; do
    PUB=$(docker exec "$UE_CONTAINER" wget -q --timeout=5 -O- "$url" 2>/dev/null | head -1 | tr -d '\r')
    if [ -n "$PUB" ]; then
        ok "$url → IP público $PUB."; http_ok=$((http_ok+1))
    else
        warn "$url não respondeu."
    fi
done
[ "$http_ok" -eq 0 ] && { warn "Nenhum serviço HTTP respondeu (o ping acima já indica a egressão)."; warns=$((warns+1)); }

# Teste 4: rota padrão ---------------------------------------------------------
section "4/6 · Rota padrão do UE"
DEFAULT_GW=$(docker exec "$UE_CONTAINER" ip route 2>/dev/null | grep default | awk '{print $3}' | head -1)
if [ -n "$DEFAULT_GW" ]; then ok "Gateway padrão: $DEFAULT_GW."; else warn "Sem rota padrão no container."; warns=$((warns+1)); fi

# Teste 5: alcance dos UPFs ----------------------------------------------------
section "5/6 · Plano de dados (UPFs)"
step "Por quê: o UPF encaminha os dados (N3/N6); aqui só checamos alcance (ping pode ser bloqueado)."
for upf_ip in "10.40.0.21" "10.40.0.22"; do
    if docker exec "$UE_CONTAINER" ping -c 1 -W 1 "$upf_ip" >/dev/null 2>&1; then
        ok "UPF $upf_ip acessível."
    else
        info "UPF $upf_ip não responde ping (normal — não invalida o plano de dados)."
    fi
done

# Teste 6: sinalização N2 (AMF↔gNB), PFCP (SMF↔UPF) e registro do UE ------------
section "6/6 · Sinalização e registro (N2 · PFCP · NAS)"
step "Por quê: a conectividade só existe porque o controle subiu — N2, sessão PFCP e registro NAS."
if docker compose logs amf 2>&1 | grep -q "gNB-N2 accepted\|ngap.*accepted"; then
    ok "N2 estabelecida (gNB conectado ao AMF)."
else
    warn "N2 não encontrada nos logs do AMF."; warns=$((warns+1))
fi
if docker compose logs smf 2>&1 | grep -q "PFCP associated"; then
    UPF_COUNT=$(docker compose logs smf 2>&1 | grep -c "PFCP associated")
    ok "PFCP associada ($UPF_COUNT UPF(s) ligado(s) ao SMF)."
else
    warn "Associação PFCP não encontrada nos logs do SMF."; warns=$((warns+1))
fi
AMF_CONTEXT_ERROR=$(docker logs "$UE_CONTAINER" 2>&1 | grep -c "AMF context not found" || echo 0)
if [ "${AMF_CONTEXT_ERROR:-0}" -gt 0 ] 2>/dev/null; then
    err "Problema: 'AMF context not found' ($AMF_CONTEXT_ERROR ocorrência(s)) — rode test-system-status."
    fails=$((fails+1))
else
    UE_REG_STATE=$(docker logs "$UE_CONTAINER" 2>&1 | grep "UE switches to state" | tail -1 | grep -oP "\[MM-[^\]]+\]" || echo "")
    if echo "$UE_REG_STATE" | grep -q "REGISTERED"; then
        ok "UE registrado no AMF: $UE_REG_STATE."
    elif docker exec "$UE_CONTAINER" ping -c 1 -W 1 8.8.8.8 >/dev/null 2>&1; then
        info "Registro não visto no log, mas o UE tem IP e conectividade (sessão válida)."
    else
        warn "UE não parece registrado."; warns=$((warns+1))
    fi
fi

# Resumo -----------------------------------------------------------------------
kv "IP do UE" "$UE_ACTUAL_IP"
kv "Gateway padrão" "${DEFAULT_GW:-—}"
kv "DNS respondendo" "$ping_ok/${#TEST_HOSTS[@]} hosts · HTTP $http_ok/${#TEST_URLS[@]}"

WHAT="verificou a conectividade fim-a-fim do UE: ping a DNS, resolução DNS, HTTP (IP público), rota padrão, alcance dos UPFs e sinalização N2/PFCP/NAS"
if [ "$fails" -gt 0 ]; then
    summary "$WHAT" "UE $UE_ACTUAL_IP COM falhas críticas — veja os itens ✗ acima (egressão ou registro)" err
elif [ "$warns" -gt 0 ]; then
    summary "$WHAT" "UE $UE_ACTUAL_IP operacional com ressalvas — itens ! acima são não-críticos" warn
else
    summary "$WHAT" "UE $UE_ACTUAL_IP plenamente conectado — todas as checagens passaram (✓)" ok
fi
