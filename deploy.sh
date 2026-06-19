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
#   ./deploy.sh ssh                - sessão interativa no servidor

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

cmd_bootstrap() {
    echo "==> Enviando infra/server-bootstrap.sh e infra/core5g-panel.service para o servidor"
    rsync -az -e "ssh ${SSH_OPTS[*]}" infra/server-bootstrap.sh "$REMOTE:~/server-bootstrap.sh"
    rsync -az -e "ssh ${SSH_OPTS[*]}" infra/core5g-panel.service "$REMOTE:~/core5g-panel.service.template"
    echo "==> Executando bootstrap (idempotente)"
    remote_exec "DUCKDNS_DOMAIN='${DUCKDNS_DOMAIN:-}' DUCKDNS_TOKEN='${DUCKDNS_TOKEN:-}' SWAP_SIZE_GB='${SWAP_SIZE_GB:-8}' SWAPPINESS='${SWAPPINESS:-10}' AWS_SERVER_HOST='${AWS_SERVER_HOST:-}' PANEL_USER='${PANEL_USER:-}' PANEL_PASSWORD='${PANEL_PASSWORD:-}' PANEL_GUEST_USER='${PANEL_GUEST_USER:-}' PANEL_GUEST_PASSWORD='${PANEL_GUEST_PASSWORD:-}' PANEL_EXTRA_USERS='${PANEL_EXTRA_USERS:-}' bash ~/server-bootstrap.sh"
}

cmd_panel() {
    echo "==> Sincronizando $LOCAL_DIR/panel/ -> $REMOTE:~/$REMOTE_DIR/panel"
    remote_exec "mkdir -p ~/$REMOTE_DIR/panel"
    rsync -az -e "ssh ${SSH_OPTS[*]}" "$LOCAL_DIR/panel/" "$REMOTE:~/$REMOTE_DIR/panel/"
    cmd_bootstrap
}

cmd_sync() {
    echo "==> Sincronizando $LOCAL_DIR/ -> $REMOTE:~/$REMOTE_DIR"
    remote_exec "mkdir -p ~/$REMOTE_DIR"
    rsync -az -e "ssh ${SSH_OPTS[*]}" \
        "$LOCAL_DIR/docker-compose.yml" "$LOCAL_DIR/.env" "$LOCAL_DIR/.env.example" \
        "$LOCAL_DIR/configs" "$LOCAL_DIR/scripts" "$LOCAL_DIR/overrides" "$LOCAL_DIR/ueransim" \
        "$REMOTE:~/$REMOTE_DIR/"
    remote_exec "chmod +x ~/$REMOTE_DIR/scripts/*.sh"
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
    exec ssh "${SSH_OPTS[@]}" "$REMOTE"
}

case "${1:-}" in
    bootstrap) cmd_bootstrap ;;
    sync)      cmd_sync ;;
    sync-oai)  cmd_sync_oai ;;
    up)        cmd_up "${2:-core}" ;;
    down)      cmd_down "${2:-all}" ;;
    status)    cmd_status ;;
    panel)     cmd_panel ;;
    ssh)       cmd_ssh ;;
    *)
        echo "Uso: $0 {bootstrap|sync|sync-oai|up [core|ran|all]|down [core|ran|all]|status|panel|ssh}" >&2
        exit 1
        ;;
esac
