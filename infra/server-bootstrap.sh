#!/bin/bash
# Bootstrap idempotente do servidor ARM AWS: Docker, swap, DuckDNS, painel+Caddy.
# Roda DIRETO NO SERVIDOR (chamado remotamente por deploy.sh via SSH).
#
# Variáveis de ambiente esperadas (passadas pelo deploy.sh):
#   DUCKDNS_DOMAIN, DUCKDNS_TOKEN   - opcionais; se ausentes, pula a etapa DuckDNS
#   SWAP_SIZE_GB                    - default 8
#   SWAPPINESS                      - default 10
#   AWS_SERVER_HOST                 - domínio público (Caddyfile); sem ele, pula Caddy/painel
#   PANEL_USER, PANEL_PASSWORD      - credenciais admin do painel (acesso total)
#   PANEL_GUEST_USER, PANEL_GUEST_PASSWORD - credenciais guest (só leitura, OPCIONAL:
#       em branco => acesso de convidado desabilitado, só os admins entram)
#   Espera ~/core5g-panel.service.template enviado pelo deploy.sh (unit do systemd)

set -euo pipefail

SWAP_SIZE_GB="${SWAP_SIZE_GB:-8}"
SWAPPINESS="${SWAPPINESS:-10}"

echo "=========================================="
echo "1/5 - Docker Engine + Compose plugin"
echo "=========================================="
if command -v docker &> /dev/null; then
    echo "Docker já instalado: $(docker --version)"
else
    export DEBIAN_FRONTEND=noninteractive
    sudo apt-get update -y
    sudo apt-get install -y ca-certificates curl gnupg unzip make
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc
    . /etc/os-release
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $VERSION_CODENAME stable" \
        | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo usermod -aG docker "$(whoami)"
    sudo systemctl enable --now docker
    echo "Docker instalado: $(sudo docker --version)"
fi

# Shim docker-compose (v1) -> docker compose (v2 plugin): scripts de terceiros
# (oai-cn5g-fed/docker-compose/core-network.py) ainda chamam o binário antigo.
if ! command -v docker-compose &> /dev/null; then
    sudo tee /usr/local/bin/docker-compose > /dev/null <<'EOF'
#!/bin/bash
exec docker compose "$@"
EOF
    sudo chmod +x /usr/local/bin/docker-compose
    echo "Shim docker-compose -> docker compose criado em /usr/local/bin/docker-compose."
else
    echo "docker-compose já disponível: $(docker-compose version --short 2>/dev/null || echo ok)"
fi

echo ""
echo "=========================================="
echo "2/5 - Swap de ${SWAP_SIZE_GB}G (swappiness=${SWAPPINESS})"
echo "=========================================="
if sudo swapon --show | grep -q '/swapfile'; then
    echo "Swapfile já existe, pulando criação."
else
    sudo fallocate -l "${SWAP_SIZE_GB}G" /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    if ! grep -q '/swapfile' /etc/fstab; then
        echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab > /dev/null
    fi
    echo "vm.swappiness=${SWAPPINESS}" | sudo tee /etc/sysctl.d/99-swappiness.conf > /dev/null
    sudo sysctl --system > /dev/null
    echo "Swap criado."
fi
free -h

# Módulo sch_netem: necessário para os testes de interferência/distância do
# Projeto 1 (tc netem em uesimtun0). Não vem carregado por padrão; persistir
# para sobreviver a reboots.
if ! lsmod | grep -q '^sch_netem'; then
    sudo modprobe sch_netem 2>/dev/null && echo "Módulo sch_netem carregado." || echo "AVISO: sch_netem indisponível (instale linux-modules-extra)."
fi
echo 'sch_netem' | sudo tee /etc/modules-load.d/netem.conf > /dev/null

echo ""
echo "=========================================="
echo "3/5 - DuckDNS"
echo "=========================================="
if [ -z "${DUCKDNS_DOMAIN:-}" ] || [ -z "${DUCKDNS_TOKEN:-}" ]; then
    echo "DUCKDNS_DOMAIN/DUCKDNS_TOKEN não fornecidos, pulando."
else
    mkdir -p ~/duckdns
    cat > ~/duckdns/duck.sh <<SCRIPT
#!/usr/bin/env bash
echo url="https://www.duckdns.org/update?domains=${DUCKDNS_DOMAIN}&token=${DUCKDNS_TOKEN}&ip=" | curl -k -o ~/duckdns/duck.log -K -
SCRIPT
    chmod 700 ~/duckdns/duck.sh
    ~/duckdns/duck.sh
    echo "Resultado da atualização: $(cat ~/duckdns/duck.log)"
    if ! crontab -l 2>/dev/null | grep -q 'duckdns/duck.sh'; then
        ( crontab -l 2>/dev/null; echo "*/5 * * * * ${HOME}/duckdns/duck.sh >/dev/null 2>&1" ) | crontab -
        echo "Cron instalado (*/5 min)."
    else
        echo "Cron já configurado."
    fi
fi

echo ""
echo "=========================================="
echo "4/5 - Painel (venv Python)"
echo "=========================================="
if [ -d ~/server/panel ]; then
    sudo apt-get install -y "python3-venv" "python3-pip" > /dev/null
    if [ ! -x ~/server/panel/.venv/bin/python3 ]; then
        rm -rf ~/server/panel/.venv
        python3 -m venv ~/server/panel/.venv
    fi
    ~/server/panel/.venv/bin/pip install -q -r ~/server/panel/requirements.txt
    echo "Venv do painel pronto."
else
    echo "~/server/panel ainda não foi sincronizado (rode ./deploy.sh panel primeiro), pulando."
fi

echo ""
echo "=========================================="
echo "5/5 - Caddy (HTTPS, TLS-only) + serviço do painel (autentica via cookie)"
echo "=========================================="
if [ -z "${AWS_SERVER_HOST:-}" ]; then
    echo "AWS_SERVER_HOST não fornecido, pulando Caddy/painel."
elif [ -z "${PANEL_USER:-}" ] || [ -z "${PANEL_PASSWORD:-}" ]; then
    echo "PANEL_USER/PANEL_PASSWORD não fornecidos, pulando Caddy/painel."
else
    if ! command -v caddy &> /dev/null; then
        sudo apt-get install -y debian-keyring debian-archive-keyring apt-transport-https
        curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
            | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
        curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
            | sudo tee /etc/apt/sources.list.d/caddy-stable.list > /dev/null
        sudo apt-get update -y
        sudo apt-get install -y caddy
        echo "Caddy instalado: $(caddy version)"
    else
        echo "Caddy já instalado: $(caddy version)"
    fi

    # Auth agora é feita pelo próprio painel (sessão por cookie assinado),
    # não pelo Caddy — só assim a tela de login customizada funciona (o
    # basic_auth do Caddy dispara o popup nativo do navegador antes de a
    # página carregar, o que não dá pra substituir por HTML).
    sudo tee /etc/caddy/Caddyfile > /dev/null <<CADDYFILE
${AWS_SERVER_HOST} {
    reverse_proxy 127.0.0.1:8765
}
CADDYFILE
    sudo systemctl reload caddy 2>/dev/null || sudo systemctl restart caddy
    sudo systemctl enable caddy
    echo "Caddyfile gerado e Caddy (re)iniciado."

    # PANEL_SECRET assina o cookie de sessão; persiste em ~/.panel_secret no
    # servidor (fora do repo) pra sobreviver a redeploys sem invalidar sessões.
    if [ -z "${PANEL_SECRET:-}" ]; then
        if [ -f ~/.panel_secret ]; then
            PANEL_SECRET="$(cat ~/.panel_secret)"
        else
            PANEL_SECRET="$(openssl rand -hex 32)"
            echo "$PANEL_SECRET" > ~/.panel_secret
            chmod 600 ~/.panel_secret
        fi
    fi

    if [ -f ~/core5g-panel.service.template ] && [ -d ~/server/panel/.venv ]; then
        sed -e "s/__PANEL_USER__/${PANEL_USER}/" \
            -e "s/__PANEL_PASSWORD__/${PANEL_PASSWORD}/" \
            -e "s/__PANEL_GUEST_USER__/${PANEL_GUEST_USER:-}/" \
            -e "s/__PANEL_GUEST_PASSWORD__/${PANEL_GUEST_PASSWORD:-}/" \
            -e "s|__PANEL_EXTRA_USERS__|${PANEL_EXTRA_USERS:-}|" \
            -e "s/__PANEL_SECRET__/${PANEL_SECRET}/" \
            ~/core5g-panel.service.template \
            | sudo tee /etc/systemd/system/core5g-panel.service > /dev/null
        sudo systemctl daemon-reload
        sudo systemctl enable --now core5g-panel
        sudo systemctl restart core5g-panel
        echo "Serviço core5g-panel ativo: https://${AWS_SERVER_HOST}/"
    else
        echo "Unit template ou venv do painel ausente, serviço core5g-panel não instalado ainda."
    fi
fi

echo ""
echo "=========================================="
echo "Bootstrap concluído."
echo "=========================================="
