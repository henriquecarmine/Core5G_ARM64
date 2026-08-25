#!/usr/bin/env bash
# Liga/desliga/consulta a instância EC2 do Core5G a partir da SUA máquina.
#
# Uso:
#   infra/aws-instance.sh ligar      # inicia, espera o DNS sarar e o painel subir
#   infra/aws-instance.sh desligar   # para a instância (computação deixa de cobrar)
#   infra/aws-instance.sh status     # estado + IP atual
#
# Pré-requisitos (UMA vez):
#   1. AWS CLI:        sudo dnf install -y awscli2        (Fedora)
#   2. Chave IAM:      console AWS -> IAM -> Users -> Create user (ex.: core5g-ops,
#      sem acesso ao console) -> Create access key (CLI) -> anexar a política de
#      menor privilégio do fim deste arquivo -> `aws configure` (region us-east-2)
#   3. .env da raiz:   adicionar AWS_INSTANCE_ID=i-xxxxxxxxxxxxxxxxx
#      (EC2 -> Instances -> coluna "Instance ID"; o .env é gitignored)
#
# Pós-ligar: a instância ganha IP público NOVO; o cron @reboot do servidor
# atualiza o DuckDNS em ~30-60 s (ver infra/server-bootstrap.sh) — o script
# espera isso e só termina quando o painel responder.

set -euo pipefail
cd "$(dirname "$0")/.."
set -a; . ./.env; set +a
: "${AWS_INSTANCE_ID:?defina AWS_INSTANCE_ID=i-... no .env (EC2 -> Instances)}"
: "${AWS_SERVER_HOST:?AWS_SERVER_HOST ausente no .env}"
REGION="${AWS_REGION:-us-east-2}"

case "${1:-status}" in
  ligar|start)
    echo "==> Iniciando ${AWS_INSTANCE_ID} (${REGION})"
    aws ec2 start-instances --region "$REGION" --instance-ids "$AWS_INSTANCE_ID" --output text >/dev/null
    aws ec2 wait instance-running --region "$REGION" --instance-ids "$AWS_INSTANCE_ID"
    ip=$(aws ec2 describe-instances --region "$REGION" --instance-ids "$AWS_INSTANCE_ID" \
         --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
    echo "==> Rodando. IP público novo: $ip"
    echo "==> Aguardando DuckDNS apontar ${AWS_SERVER_HOST} -> $ip (cron @reboot)"
    for _ in $(seq 1 24); do
      resolvectl flush-caches 2>/dev/null || true
      [ "$(getent hosts "$AWS_SERVER_HOST" | awk '{print $1}' | head -1)" = "$ip" ] && break
      sleep 10
    done
    echo "==> DNS: $(getent hosts "$AWS_SERVER_HOST" | awk '{print $1}' | head -1)"
    echo "==> Aguardando o painel subir (systemd)"
    for _ in $(seq 1 30); do
      v=$(curl -s --max-time 5 "https://${AWS_SERVER_HOST}/api/version" || true)
      if [ -n "$v" ]; then echo "==> Painel no ar: $v"; exit 0; fi
      sleep 10
    done
    echo "aviso: painel ainda não respondeu — dê mais um minuto e teste https://${AWS_SERVER_HOST}" >&2
    exit 1
    ;;
  desligar|stop)
    echo "==> Parando ${AWS_INSTANCE_ID} (${REGION})"
    aws ec2 stop-instances --region "$REGION" --instance-ids "$AWS_INSTANCE_ID" --output text >/dev/null
    aws ec2 wait instance-stopped --region "$REGION" --instance-ids "$AWS_INSTANCE_ID"
    echo "==> Parada. Computação não cobra mais (o disco EBS continua cobrando)."
    ;;
  status)
    aws ec2 describe-instances --region "$REGION" --instance-ids "$AWS_INSTANCE_ID" \
      --query 'Reservations[0].Instances[0].{estado:State.Name,ip:PublicIpAddress,tipo:InstanceType}' \
      --output table
    ;;
  *)
    echo "uso: $0 ligar|desligar|status" >&2
    exit 1
    ;;
esac

# ---------------------------------------------------------------------------
# Política IAM de menor privilégio para o usuário core5g-ops
# (arquivo pronto: infra/iam-core5g-ops-policy.json — conta 263069515288,
# instância i-0c7f76199afc9e27f em us-east-2). Start/Stop só nesta instância;
# Describe é read-only e a AWS exige recurso "*" para ele.
#
# O próprio core5g-ops NÃO consegue se anexar a política (permissions boundary
# nega iam:PutUserPolicy — testado em 25/08/2026). Anexe com um perfil admin:
#   aws iam put-user-policy --profile admin --user-name core5g-ops \
#       --policy-name core5g-ops-start-stop \
#       --policy-document file://infra/iam-core5g-ops-policy.json
# ou no console: IAM → Users → core5g-ops → Add permissions → Create inline
# policy → JSON → colar o arquivo → nome core5g-ops-start-stop.
# Conferir depois:  ./infra/aws-instance.sh status
# ---------------------------------------------------------------------------
