#!/bin/bash
# Lista subscribers do Open5GS (MongoDB) como JSON.
# Saída: array JSON com {imsi, msisdn} por linha ou "[]" se vazio.
set -e
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

docker compose exec -T mongodb mongosh open5gs --quiet --eval \
    'print(JSON.stringify(db.subscribers.find({},{"imsi":1,"msisdn":1,"_id":0}).toArray()))' \
    2>/dev/null | grep '^\[' | head -1 || echo '[]'
