#!/bin/bash
# Entrypoint único de deploy para o servidor ARM AWS.
# Tudo se edita LOCAL em server/; este script é o único caminho pra refletir no servidor.
#
# Uso:
#   ./deploy.sh bootstrap          - instala Docker + swap + DuckDNS no servidor (idempotente)
#   ./deploy.sh sync               - envia server/{docker-compose.yml,.env,configs,scripts,overrides,ueransim}
#   ./deploy.sh sync-oai           - envia server/oai-cn-gnb-e2/ (~230MB, sob demanda, não entra no sync normal)
#   ./deploy.sh up [core|ran|all]  - sync + sobe o stack (default: core)
#   ./deploy.sh down [core|ran|all]
#   ./deploy.sh status             - docker compose ps + healthcheck no servidor
#   ./deploy.sh panel               - envia server/panel/ + roda bootstrap (sobe/atualiza Caddy+painel HTTPS)
#   ./deploy.sh ssh [comando]      - roda o comando (ou abre sessão interativa)

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

if [ ! -f .env ]; then
    echo "ERRO: .env não encontrado em $PROJECT_DIR. Copie .env.example para .env e ajuste." >&2
    exit 1
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

: "${AWS_SERVER_HOST:?defina AWS_SERVER_HOST no .env}"
: "${AWS_SERVER_USER:?defina AWS_SERVER_USER no .env}"
: "${AWS_SSH_KEY_PATH:?defina AWS_SSH_KEY_PATH no .env}"

REMOTE="${AWS_SERVER_USER}@${AWS_SERVER_HOST}"
LOCAL_DIR="server"
REMOTE_DIR="server"
SSH_OPTS=(-o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 -i "$AWS_SSH_KEY_PATH")

remote_exec() {
    ssh "${SSH_OPTS[@]}" "$REMOTE" "$@"
}

# server/.env é gitignored (só pins de imagem, sem segredos), então um clone novo
# do repo não o tem — e o rsync do cmd_sync o lista explicitamente, abortando com
# "rsync error 23" que não diz o que fazer. Recria a partir do .env.example, que
# traz exatamente os mesmos valores.
ensure_server_env() {
    [ -f "$LOCAL_DIR/.env" ] && return 0
    if [ ! -f "$LOCAL_DIR/.env.example" ]; then
        echo "ERRO: $LOCAL_DIR/.env e $LOCAL_DIR/.env.example ausentes — clone incompleto." >&2
        exit 1
    fi
    echo "==> $LOCAL_DIR/.env ausente (é gitignored); criando a partir de $LOCAL_DIR/.env.example"
    cp "$LOCAL_DIR/.env.example" "$LOCAL_DIR/.env"
}

cmd_bootstrap() {
    echo "==> Enviando infra/server-bootstrap.sh e infra/core5g-panel.service para o servidor"
    rsync -az -e "ssh ${SSH_OPTS[*]}" infra/server-bootstrap.sh "$REMOTE:~/server-bootstrap.sh"
    rsync -az -e "ssh ${SSH_OPTS[*]}" infra/core5g-panel.service "$REMOTE:~/core5g-panel.service.template"
    echo "==> Executando bootstrap (idempotente)"
    remote_exec "DUCKDNS_DOMAIN='${DUCKDNS_DOMAIN:-}' DUCKDNS_TOKEN='${DUCKDNS_TOKEN:-}' SWAP_SIZE_GB='${SWAP_SIZE_GB:-8}' SWAPPINESS='${SWAPPINESS:-10}' AWS_SERVER_HOST='${AWS_SERVER_HOST:-}' PANEL_USER='${PANEL_USER:-}' PANEL_PASSWORD='${PANEL_PASSWORD:-}' PANEL_GUEST_USER='${PANEL_GUEST_USER:-}' PANEL_GUEST_PASSWORD='${PANEL_GUEST_PASSWORD:-}' PANEL_EXTRA_USERS='${PANEL_EXTRA_USERS:-}' bash ~/server-bootstrap.sh"
}

# Quem está USANDO o painel agora? Conta os clientes distintos no journal do
# serviço, ignorando o localhost. Existe porque em 29/08 eu reiniciei o painel
# em cima de três pessoas conectadas: tentei medir antes, a expressão de busca
# não casou nada, e eu li o resultado vazio como "não tem ninguém". Medição que
# falha tem de gritar, não devolver zero.
quem_esta_usando() {
    remote_exec "sudo journalctl -u core5g-panel --since '-${1:-10} min' --no-pager 2>/dev/null \
        | sed -n 's/.*INFO: *\([0-9.]*\):[0-9]* - \".*/\1/p' | grep -v '^127\.' | sort -u" 2>/dev/null
}

# Aborta se houver gente no painel. `FORCA=1 ./deploy.sh panel` passa por cima —
# de propósito: derrubar a sessão de alguém tem de ser uma decisão, não um
# efeito colateral de um comando de rotina.
conferir_ocupacao() {
    local ips n
    ips="$(quem_esta_usando 10)"
    n="$(printf '%s' "$ips" | grep -c . || true)"
    if [ "${FORCA:-0}" = "1" ]; then
        [ "$n" -gt 0 ] && echo "==> AVISO: $n cliente(s) no painel, e FORCA=1 — reiniciando mesmo assim."
        return 0
    fi
    if [ "$n" -gt 0 ]; then
        echo "" >&2
        echo "ABORTADO: $n cliente(s) usaram o painel nos últimos 10 minutos:" >&2
        printf '  · %s\n' $ips >&2
        echo "" >&2
        echo "Reiniciar agora derruba a sessão deles (e o Professor perde a vaga)." >&2
        echo "Se for mesmo necessário:  FORCA=1 $0 panel" >&2
        exit 1
    fi
    echo "==> Ninguém no painel nos últimos 10 minutos — pode reiniciar."
}

cmd_panel() {
    conferir_ocupacao
    echo "==> Sincronizando $LOCAL_DIR/panel/ -> $REMOTE:~/$REMOTE_DIR/panel"
    remote_exec "mkdir -p ~/$REMOTE_DIR/panel"
    rsync -az -e "ssh ${SSH_OPTS[*]}" "$LOCAL_DIR/panel/" "$REMOTE:~/$REMOTE_DIR/panel/"
    cmd_bootstrap
}

cmd_sync() {
    ensure_server_env
    echo "==> Sincronizando $LOCAL_DIR/ -> $REMOTE:~/$REMOTE_DIR"
    remote_exec "mkdir -p ~/$REMOTE_DIR"
    rsync -az -e "ssh ${SSH_OPTS[*]}" --exclude nonrt-ric/src \
        "$LOCAL_DIR/docker-compose.yml" "$LOCAL_DIR/.env" "$LOCAL_DIR/.env.example" \
        "$LOCAL_DIR/configs" "$LOCAL_DIR/scripts" "$LOCAL_DIR/overrides" "$LOCAL_DIR/ueransim" \
        "$LOCAL_DIR/nonrt-ric" \
        "$REMOTE:~/$REMOTE_DIR/"
    remote_exec "chmod +x ~/$REMOTE_DIR/scripts/*.sh ~/$REMOTE_DIR/nonrt-ric/*.sh 2>/dev/null || chmod +x ~/$REMOTE_DIR/scripts/*.sh"
}

cmd_sync_oai() {
    echo "==> Sincronizando $LOCAL_DIR/oai-cn-gnb-e2/ -> $REMOTE:~/$REMOTE_DIR/oai-cn-gnb-e2 (pode demorar, ~230MB)"
    remote_exec "mkdir -p ~/$REMOTE_DIR/oai-cn-gnb-e2"
    rsync -az -e "ssh ${SSH_OPTS[*]}" "$LOCAL_DIR/oai-cn-gnb-e2/" "$REMOTE:~/$REMOTE_DIR/oai-cn-gnb-e2/"
}

cmd_up() {
    local target="${1:-core}"
    cmd_sync
    case "$target" in
        core) remote_exec "cd ~/$REMOTE_DIR && ./scripts/up_core.sh" ;;
        ran)  remote_exec "cd ~/$REMOTE_DIR && ./scripts/up_ran.sh" ;;
        all)  remote_exec "cd ~/$REMOTE_DIR && ./scripts/up.sh && ./scripts/up_ran.sh" ;;
        *) echo "ERRO: target inválido '$target' (use core|ran|all)" >&2; exit 1 ;;
    esac
}

cmd_down() {
    local target="${1:-all}"
    case "$target" in
        core) remote_exec "cd ~/$REMOTE_DIR && docker compose down" ;;
        ran)  remote_exec "cd ~/$REMOTE_DIR/ueransim && docker compose down" ;;
        all)
            remote_exec "cd ~/$REMOTE_DIR/ueransim && docker compose down" || true
            remote_exec "cd ~/$REMOTE_DIR && docker compose down"
            ;;
        *) echo "ERRO: target inválido '$target' (use core|ran|all)" >&2; exit 1 ;;
    esac
}

cmd_status() {
    remote_exec "cd ~/$REMOTE_DIR && docker compose ps && echo '---' && ./scripts/healthcheck.sh"
}

cmd_ssh() {
    # Com argumentos, RODA o comando; sem eles, abre a sessão interativa.
    # Antes os argumentos eram descartados em silêncio: `./deploy.sh ssh "docker ps"`
    # abria um shell que esperava entrada para sempre, e parecia servidor travado.
    exec ssh "${SSH_OPTS[@]}" "$REMOTE" "$@"
}

case "${1:-}" in
    bootstrap) cmd_bootstrap ;;
    sync)      cmd_sync ;;
    sync-oai)  cmd_sync_oai ;;
    up)        cmd_up "${2:-core}" ;;
    down)      cmd_down "${2:-all}" ;;
    status)    cmd_status ;;
    panel)     cmd_panel ;;
    ssh)       shift; cmd_ssh "$@" ;;
    *)
        echo "Uso: $0 {bootstrap|sync|sync-oai|up [core|ran|all]|down [core|ran|all]|status|panel|ssh}" >&2
        exit 1
        ;;
esac
