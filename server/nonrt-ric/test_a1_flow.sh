#!/usr/bin/env bash
# Smoke ponta a ponta do caminho A1 (nonRT):
#   1. PMS de pé e enxergando os 3 RICs (simuladores)
#   2. Carrega o policy type 1 no a1-sim-OSC (testdata do lab do docente)
#   3. PMS sincroniza o type
#   4. Registra o service "core5g" e cria a política core5g-smoke-001 VIA PMS
#   5. Prova que a política chegou NO SIMULADOR (o "A1 de verdade")
#   6. Limpa (DELETE)
set -euo pipefail
cd "$(dirname "$0")"

PMS="http://localhost:${NONRT_PMS_HTTP_PORT:-8081}"
SIM_OSC="http://localhost:30001"
ok()   { printf '  \033[32mOK\033[0m  %s\n' "$1"; }
fail() { printf '  \033[31mFALHOU\033[0m  %s\n' "$1" >&2; exit 1; }

echo "== 1. PMS vivo =="
curl -sf "$PMS/a1-policy/v2/status" | grep -q success && ok "status: success" \
    || fail "PMS não respondeu em $PMS (rodou ./up_nonrt.sh?)"

echo "== 2. RICs configurados =="
rics="$(curl -sf "$PMS/a1-policy/v2/rics")"
for r in ric1 ric2 ric3; do
    echo "$rics" | grep -q "\"$r\"" && ok "$r presente" || fail "$r ausente"
done

echo "== 3. policy type 1 → a1-sim-OSC =="
curl -sf -X PUT "$SIM_OSC/a1-p/policytypes/1" \
    -H 'Content-Type: application/json' -d @testdata/policy_type.json >/dev/null \
    && ok "type 1 carregado no simulador" || fail "PUT do policy type no simulador"

echo "== 4. PMS sincroniza o type (supervisão periódica; até ~90 s) =="
for i in $(seq 1 30); do
    curl -sf "$PMS/a1-policy/v2/policy-types" | grep -q '"1"' && break
    sleep 3
done
curl -sf "$PMS/a1-policy/v2/policy-types" | grep -q '"1"' \
    && ok "type 1 visível no PMS" || fail "PMS não sincronizou o type em 90 s"

echo "== 5. service + política via PMS =="
curl -sf -X PUT "$PMS/a1-policy/v2/services" \
    -H 'Content-Type: application/json' -d @testdata/service_smoke.json >/dev/null \
    && ok "service core5g registrado" || fail "registro do service"
curl -sf -X PUT "$PMS/a1-policy/v2/policies" \
    -H 'Content-Type: application/json' -d @testdata/policy_smoke.json >/dev/null \
    && ok "política core5g-smoke-001 criada via PMS" || fail "criação da política"

echo "== 6. política chegou no simulador (nonRT → A1 → nearRT-sim) =="
curl -sf "$SIM_OSC/a1-p/policies" | grep -q core5g-smoke-001 \
    && ok "core5g-smoke-001 presente no a1-sim-OSC" || fail "política não chegou ao simulador"
curl -sf "$PMS/a1-policy/v2/policies/core5g-smoke-001" | grep -q ue-smoke \
    && ok "leitura de volta via PMS confere" || fail "GET da política no PMS"

echo "== 7. limpeza =="
curl -sf -X DELETE "$PMS/a1-policy/v2/policies/core5g-smoke-001" >/dev/null \
    && ok "política removida" || fail "DELETE da política"

echo
echo "✔ Caminho A1 completo: PMS (nonRT) → A1 → simulador (nearRT), em ARM64 nativo."
