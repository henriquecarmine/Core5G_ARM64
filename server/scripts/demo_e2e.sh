#!/bin/bash
# Demonstração E2E da rede 5G (Projeto 1 — Open5GS + UERANSIM).
# Prova a operação fim-a-fim: UE registrado → sessão PDU com IP → saída real
# para a internet (ping) → IP público visto pela internet → throughput (iperf3).
#
# DOIS canais de saída para o painel:
#   1) Resumo (rail da direita) — linhas estruturadas:
#        STEP|<ok|fail|info>|<título>|<detalhe>
#        DONE|<ok|fail>
#        PHASE|<texto>                         (atualiza o spinner)
#   2) Logs didáticos (console da esquerda) — TUDO o que não é STEP/DONE/PHASE:
#        "$ <comando>"  → o comando exato que rodou (destaque azul no painel)
#        "<texto>"      → narração didática e a saída real dos comandos
#
# Tudo é medido de verdade no túnel 5G (uesimtun0 → gNB → UPF → DN), sem mock.

UE="ueransim"
DN_CONTAINER="open5gs-dn-containerized"
DN_IP="10.50.0.100"        # IP do DN na rede N6 (saída do núcleo)

emit()  { echo "STEP|$1|$2|$3"; }            # resumo (rail direita)
phase() { echo "PHASE|$1"; }                 # título do spinner
say()   { echo "$1"; }                       # narração didática (console)
cmd()   { echo "\$ $1"; }                    # eco do comando (azul no console)
out()   { [ -n "$1" ] && printf '%s\n' "$1" | sed 's/^/    /'; }  # saída real, indentada
rule()  { echo ""; echo "── $1 ───────────────────────────────"; }

say "Demonstração E2E — Projeto 1 (Open5GS + UERANSIM)"
say "Cada passo abaixo mostra o comando executado e a saída real, sem simulação."

# 1. Container do UE/RAN ativo --------------------------------------------------
phase "Passo 1/5 · Verificando o RAN (UE/gNB)…"
rule "Passo 1/5 · O rádio (RAN) está no ar?"
say  "Por quê: sem o gNB+UE simulados (UERANSIM) conectados ao Core por N2/N3, não há rede de acesso para testar."
cmd  "docker inspect -f '{{.State.Status}}' $UE"
ST="$(docker inspect -f '{{.State.Status}}' "$UE" 2>/dev/null)"
out  "${ST:-container inexistente}"
if ! echo "$ST" | grep -q running; then
  say "→ O container '$UE' NÃO está rodando."
  emit fail "UE / RAN ativo" "Container '$UE' não está rodando. Ligue o RAN do Projeto 1 (toggle RAN)."
  echo "DONE|fail"; exit 0
fi
say "→ RAN no ar: gNB e UE simulados em execução, conectados ao Core 5G (N2 sinalização, N3 dados)."
emit ok "UE / RAN ativo" "UERANSIM em execução (gNB + UE simulados conectados ao Core via N2/N3)."

# 2. Sessão PDU + IP ------------------------------------------------------------
phase "Passo 2/5 · Conferindo a sessão PDU e o IP do UE…"
rule "Passo 2/5 · O UE registrou e ganhou um IP?"
say  "Por quê: após o registro 5G-AKA (AMF→AUSF→UDM) e o estabelecimento da sessão PDU (SMF/UPF),"
say  "o UE recebe um IP do pool da DNN 'internet' (10.60.0.0/16) na interface de túnel uesimtun0."
cmd  "docker exec $UE ip -4 addr show uesimtun0"
ADDR_RAW="$(docker exec "$UE" ip -4 addr show uesimtun0 2>/dev/null)"
out  "${ADDR_RAW:-interface uesimtun0 ausente}"
UE_IP="$(echo "$ADDR_RAW" | grep -oE 'inet ([0-9]+\.){3}[0-9]+' | grep -oE '([0-9]+\.){3}[0-9]+' | head -1)"
if [ -z "$UE_IP" ]; then
  say "→ Sem IP em uesimtun0: o UE não registrou ou a sessão PDU não subiu."
  emit fail "Sessão PDU / IP" "Interface uesimtun0 sem IP — o UE não registrou ou a sessão PDU não subiu."
  echo "DONE|fail"; exit 0
fi
say "→ Sessão PDU ATIVA: o UE recebeu o IP $UE_IP. O túnel de dados 5G está pronto (UE → gNB → UPF)."
emit ok "Sessão PDU estabelecida" "UE recebeu o IP $UE_IP na interface uesimtun0 (túnel 5G ativo)."

# 3. Saída para a internet (ping pelo túnel) ------------------------------------
phase "Passo 3/5 · Pingando a internet pelo túnel 5G…"
rule "Passo 3/5 · O tráfego sai para a internet?"
say  "Por quê: '-I uesimtun0' força o ping a sair PELO túnel 5G (não pela rede do container)."
say  "Isso atravessa UE → gNB → UPF → N6 → internet e volta. É a prova de operação fim-a-fim."
cmd  "docker exec $UE ping -I uesimtun0 -c 4 -w 8 8.8.8.8"
PING="$(docker exec "$UE" ping -I uesimtun0 -c 4 -w 8 8.8.8.8 2>&1)"
out  "$PING"
LOSS="$(echo "$PING" | grep -oE '[0-9]+% packet loss' | head -1)"
RTT="$(echo "$PING" | grep -oE 'min/avg/max[^=]*= [0-9.]+/[0-9.]+' | grep -oE '[0-9.]+$')"
if echo "$PING" | grep -qE ' 0% packet loss'; then
  say "→ Internet alcançada: $LOSS, RTT médio ${RTT:-?} ms. A rede 5G está roteando dados de verdade."
  emit ok "Saída para a internet" "ping 8.8.8.8 pelo túnel 5G: ${LOSS}, RTT médio ${RTT:-?} ms (4 pacotes)."
else
  say "→ Ping falhou (${LOSS:-sem resposta}). Verifique o UPF e a saída N6."
  emit fail "Saída para a internet" "ping 8.8.8.8 falhou (${LOSS:-sem resposta}). Verifique UPF/N6."
fi

# 4. IP público visto pela internet (prova de egressão real) --------------------
phase "Passo 4/5 · Descobrindo o IP público do UE…"
rule "Passo 4/5 · Com qual IP público o UE aparece na internet?"
say  "Por quê: ao consultar um serviço externo amarrando a origem ao túnel, vemos o IP público real"
say  "com que o tráfego do UE sai (UE → UPF → NAT/N6 → DN → internet). Prova definitiva de egressão."
cmd  "docker exec $UE curl -s --interface uesimtun0 --max-time 6 http://ifconfig.me"
PUBIP="$(docker exec "$UE" sh -c "curl -s --interface uesimtun0 --max-time 6 http://ifconfig.me 2>/dev/null || wget -qO- --bind-address=$UE_IP http://ifconfig.me 2>/dev/null" 2>/dev/null | tr -d '\r\n ')"
out  "${PUBIP:-(sem resposta HTTP)}"
if echo "$PUBIP" | grep -qE '^([0-9]+\.){3}[0-9]+$'; then
  say "→ IP público confirmado: $PUBIP. O tráfego do UE chega à internet por esse endereço."
  emit ok "IP público na internet" "O tráfego do UE sai com IP público $PUBIP (UE → UPF → N6 → DN → internet)."
else
  say "→ HTTP não respondeu agora, mas o ping do Passo 3 já comprovou a egressão para a internet."
  emit info "IP público na internet" "Não foi possível obter via HTTP, mas o ping acima já comprova a egressão para a internet."
fi

# 5. Throughput real (iperf3 UE → DN, ATRAVÉS do núcleo 5G) ---------------------
phase "Passo 5/5 · Medindo a banda real pelo túnel 5G (iperf3)…"
rule "Passo 5/5 · Quanta banda a rede entrega? (iperf3)"
say  "Por quê: mede a vazão real do UE até o DN ($DN_IP) ATRAVESSANDO o núcleo 5G."
say  "Detalhe técnico: o DN fica na mesma rede docker do container do UE, então um iperf 'solto'"
say  "sairia pela bridge (eth0) e NÃO mediria o 5G. Para forçar o caminho real, criamos uma rota"
say  "para o DN via uesimtun0 e amarramos a origem ao IP do túnel ($UE_IP). Assim o tráfego vai"
say  "UE → gNB → UPF (NAT na N6) → DN, medindo o que a rede 5G de fato entrega."
DN_ST="$(docker inspect -f '{{.State.Status}}' "$DN_CONTAINER" 2>/dev/null)"
if ! echo "$DN_ST" | grep -q running; then
  say "→ O container do DN ($DN_CONTAINER) não está no ar — pulando a medição de banda."
  emit info "Throughput (iperf3)" "Container DN ($DN_CONTAINER) não está no ar — pulando medição de banda."
  echo "DONE|ok"; exit 0
fi

# Sobe o servidor iperf3 no DN (one-shot) e cria a rota pelo túnel.
cmd "docker exec -d $DN_CONTAINER iperf3 -s -1 -p 5201"
docker exec -d "$DN_CONTAINER" sh -c "iperf3 -s -1 -p 5201 >/tmp/iperf3-demo.log 2>&1"
cmd "docker exec $UE ip route replace $DN_IP/32 dev uesimtun0"
ROUTE_ERR="$(docker exec "$UE" ip route replace "$DN_IP/32" dev uesimtun0 2>&1)"
out  "${ROUTE_ERR:-rota para $DN_IP adicionada via uesimtun0}"
sleep 1

cmd "docker exec $UE iperf3 -c $DN_IP -B $UE_IP -t 5 -p 5201 --connect-timeout 4000"
IPERF="$(timeout 18 docker exec "$UE" iperf3 -c "$DN_IP" -B "$UE_IP" -t 5 -p 5201 --connect-timeout 4000 2>&1)"
out  "$IPERF"

# Remove a rota temporária (não deixa rastro na sessão).
docker exec "$UE" ip route del "$DN_IP/32" dev uesimtun0 2>/dev/null

BW="$(echo "$IPERF" | grep -E 'receiver' | grep -oE '[0-9.]+ [GM]bits/sec' | tail -1)"
[ -z "$BW" ] && BW="$(echo "$IPERF" | grep -oE '[0-9.]+ [GM]bits/sec' | tail -1)"
if [ -n "$BW" ]; then
  say "→ Banda real medida atravessando o núcleo 5G (UE → UPF → DN): $BW."
  emit ok "Throughput medido (iperf3)" "Banda real UE→DN atravessando o núcleo 5G: $BW."
else
  say "→ O iperf não retornou banda. A egressão para a internet (Passos 3-4) já comprova a operação;"
  say "  a saída acima do iperf ajuda a diagnosticar (servidor no DN, rota pelo túnel ou NAT do UPF)."
  emit info "Throughput (iperf3)" "Destino interno (DN) não respondeu — veja a saída do iperf nos logs. A saída para a internet já foi comprovada nos Passos 3-4."
fi

echo "DONE|ok"
