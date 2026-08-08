#!/usr/bin/env bash
# Smoke do A1 Mediator REAL (northbound — a mesma API que o PMS consome):
#   healthcheck → criar policy type → criar política → ler de volta → limpar.
# É o teste do lado near-RT de verdade; a ligação PMS→mediator usa o
# application_configuration.oran.json (perfil oran do professor).
set -euo pipefail
cd "$(dirname "$0")"
A1="http://localhost:${A1MEDIATOR_HOST_PORT:-10000}"
ok()   { printf '  \033[32mOK\033[0m  %s\n' "$1"; }
fail() { printf '  \033[31mFALHOU\033[0m  %s\n' "$1" >&2; exit 1; }

echo "== 1. healthcheck =="
for i in $(seq 1 20); do curl -sf "$A1/A1-P/v2/healthcheck" >/dev/null && break; sleep 3; done
curl -sf "$A1/A1-P/v2/healthcheck" >/dev/null && ok "a1mediator vivo" || fail "healthcheck"

echo "== 2. policy type 20011 (janela do a1-routes.rt) =="
if curl -sf "$A1/A1-P/v2/policytypes" | grep -q 20011; then
    ok "type 20011 já existia"
else
    curl -sf -X PUT "$A1/A1-P/v2/policytypes/20011" -H 'Content-Type: application/json' -d '{
      "name": "core5g_qos", "description": "tipo de teste do lab",
      "policy_type_id": 20011,
      "create_schema": {"$schema":"http://json-schema.org/draft-07/schema#",
        "type":"object","properties":{"scope":{"type":"object"},
        "qosObjectives":{"type":"object"}},"additionalProperties":false}
    }' >/dev/null && ok "type 20011 criado" || fail "PUT policytype"
fi

echo "== 3. política via A1 =="
curl -sf -X PUT "$A1/A1-P/v2/policytypes/20011/policies/core5g-real-001" \
    -H 'Content-Type: application/json' \
    -d '{"scope":{"ueId":"ue-real"},"qosObjectives":{"priorityLevel":7}}' >/dev/null \
    && ok "política core5g-real-001 criada" || fail "PUT policy"

echo "== 4. leitura de volta =="
curl -sf "$A1/A1-P/v2/policytypes/20011/policies" | grep -q core5g-real-001 \
    && ok "política listada no mediator" || fail "GET policies"

echo "== 5. limpeza =="
curl -sf -X DELETE "$A1/A1-P/v2/policytypes/20011/policies/core5g-real-001" >/dev/null \
    && ok "política removida" || fail "DELETE"

echo
echo "✔ A1 Mediator REAL (O-RAN SC ric-plt-a1) respondendo o ciclo completo em ARM64 nativo."
