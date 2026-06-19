#!/bin/bash
# Remove subscriber do Open5GS (MongoDB) pelo IMSI.
# Uso: SUB_IMSI=001010000000001 ./remove-subscriber.sh
#   ou: ./remove-subscriber.sh 001010000000001
set -e
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

IMSI="${SUB_IMSI:-${1:-}}"
if [ -z "$IMSI" ]; then
    echo "Erro: IMSI não informado." >&2
    echo "Uso: SUB_IMSI=<imsi> $0" >&2
    exit 1
fi

echo "Removendo subscriber IMSI=$IMSI..."
RESULT=$(docker compose exec -T mongodb mongosh open5gs --quiet --eval \
    "print(JSON.stringify(db.subscribers.deleteOne({imsi:'${IMSI}'})))" \
    2>/dev/null | grep '^{' | head -1 || echo '{}')

DELETED=$(echo "$RESULT" | grep -o '"deletedCount":[0-9]*' | grep -o '[0-9]*' || echo "0")
if [ "${DELETED:-0}" -ge 1 ]; then
    echo "Subscriber removido com sucesso."
else
    echo "Subscriber não encontrado (IMSI=$IMSI)."
fi
