#!/usr/bin/env bash
# SMO ao vivo — o retrato do SMO agora, em JSON, para o modal "SMO ao vivo" do
# painel (GET /api/smo). Só leitura, o que o operador acompanha no ODLUX:
# elementos sob gerência e as conexões deles, alarmes ativos e histórico, o
# barramento Kafka (quantos eventos cada tópico recebeu e o último) e os
# contêineres das três camadas. Mesmo acesso dos testes da apresentação: tudo
# pelo gateway local (lib.sh); nenhuma credencial sai daqui.
set -uo pipefail
cd "$(dirname "$0")"
. ./lib.sh

if ! docker ps --format '{{.Names}}' | grep -qx controller; then
    echo '{"no_ar": false}'
    exit 0
fi

export NOS CONEXOES ALARMES HISTORICO N_HISTORICO TOPICOS LIDOS CONTEINERES
EVENTO='severity, `node-id`, `object-id`, problem, `timestamp`'

NOS="$(restconf GET "$MONTAGEM?content=nonconfig")"
CONEXOES="$(db 'select `node-id`, status, `timestamp` from `connectionlog-v7` order by `timestamp` desc limit 8')"
ALARMES="$(db "select $EVENTO from \`faultcurrent-v7\` order by \`timestamp\` desc limit 20")"
HISTORICO="$(db "select $EVENTO from \`faultlog-v7\` order by \`timestamp\` desc limit 6")"
N_HISTORICO="$(db 'select count(*) from `faultlog-v7`')"

# Barramento: offset final de cada tópico e, com UM consumidor na ponte (uma
# partição por tópico, posicionada no último evento), o último de cada um.
TOPICOS=""
for t in $(kb "$BRIDGE/topics" | python3 -c 'import json,sys; print(" ".join(x for x in json.load(sys.stdin) if not x.startswith("__")))' 2>/dev/null); do
    TOPICOS+="$t $(kafka_fim "$t")"$'\n'
done
LIDOS="[]"
PEDIDO="$(python3 -c '
import json, os
ts = [(t, int(n)) for t, n in (l.split() for l in os.environ["TOPICOS"].splitlines() if l.strip()) if int(n) > 0]
print(len(ts))
print(json.dumps({"partitions": [{"topic": t, "partition": 0} for t, _ in ts]}))
print(json.dumps({"offsets": [{"topic": t, "partition": 0, "offset": n - 1} for t, n in ts]}))')"
N_COM_EVENTO="$(sed -n 1p <<<"$PEDIDO")"
if [ "${N_COM_EVENTO:-0}" -gt 0 ]; then
    g="core5g-vivo-$$-$RANDOM" v2='Content-Type: application/vnd.kafka.v2+json'
    inst="$BRIDGE/consumers/$g/instances/c"
    kb -X POST -H "$v2" -o /dev/null -d '{"name":"c","format":"json","enable.auto.commit":false}' "$BRIDGE/consumers/$g"
    kb -X POST -H "$v2" -o /dev/null -d "$(sed -n 2p <<<"$PEDIDO")" "$inst/assignments"
    kb -X POST -H "$v2" -o /dev/null -d "$(sed -n 3p <<<"$PEDIDO")" "$inst/positions"
    # a primeira leitura de um consumidor novo costuma voltar vazia
    for _ in 1 2 3 4; do
        LIDOS="$(NOVOS="$(kafka_le "$inst" 800)" python3 -c '
import json, os
lidos = json.loads(os.environ["LIDOS"])
try:
    novos = json.loads(os.environ["NOVOS"] or "[]")
except ValueError:
    novos = []
print(json.dumps(lidos + (novos if isinstance(novos, list) else [])))')"
        [ "$(python3 -c 'import json,os; print(len({r["topic"] for r in json.loads(os.environ["LIDOS"])}))')" -ge "$N_COM_EVENTO" ] && break
    done
    kafka_fecha "$inst"
fi

CONTEINERES="$(for camada in common oam network; do
    docker ps -a --filter "label=com.docker.compose.project=smo-$camada" --format "$camada\t{{.Names}}\t{{.State}}\t{{.Status}}"
done)"

python3 - <<'PY'
import json, os, time
from datetime import datetime, timezone

falhas = []

def linhas(var):
    return [l.split("\t") for l in os.environ.get(var, "").splitlines() if l.strip()]

def hora_utc(ts):
    """O banco do controlador grava em UTC; a tela mostra a hora do servidor."""
    try:
        return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc).astimezone().strftime("%H:%M:%S.%f")[:12]
    except ValueError:
        return ts

def evento(c):
    sev, no, obj, prob, ts = (c + [""] * 5)[:5]
    return {"hora": hora_utc(ts), "severidade": sev, "no": no, "objeto": obj, "problema": "" if prob == "NULL" else prob}

elementos = []
try:
    topo = json.loads(os.environ["NOS"]).get("network-topology:topology", [{}])[0]
    for no in topo.get("node", []):
        nc = no.get("netconf-node-topology:netconf-node", {})
        caps = [c["capability"] for c in nc.get("available-capabilities", {}).get("available-capability", [])]
        elementos.append({
            "no": no["node-id"], "estado": nc.get("connection-status", "?"),
            "endereco": f'{nc.get("host", "?")}:{nc.get("port", "?")}',
            "yang": len(caps), "oran": sum("o-ran-" in c for c in caps), "g3": sum("_3gpp-" in c for c in caps),
        })
except (ValueError, KeyError, IndexError):
    falhas.append("o1")

ultimo = {}
for r in json.loads(os.environ["LIDOS"]):
    try:
        h = r["value"]["event"]["commonEventHeader"]
    except (KeyError, TypeError):
        continue
    epoch = int(h.get("lastEpochMicrosec") or h.get("startEpochMicrosec") or 0) / 1e6
    ultimo[r["topic"]] = {
        "hora": datetime.fromtimestamp(epoch).strftime("%H:%M:%S") if epoch else "",
        "idade_s": int(time.time() - epoch) if epoch else None,
        "dominio": h.get("domain", ""), "evento": h.get("eventName", ""), "origem": h.get("sourceName", ""),
    }
barramento = [{"topico": t, "eventos": int(n), "ultimo": ultimo.get(t)}
              for t, n in (l.split() for l in os.environ["TOPICOS"].splitlines() if l.strip())]
if not barramento:
    falhas.append("kafka")

print(json.dumps({
    "no_ar": True,
    "gerado_em": time.strftime("%H:%M:%S"),
    "elementos": elementos,
    "conexoes": [{"hora": hora_utc(ts), "no": no, "estado": st} for no, st, ts in (c for c in linhas("CONEXOES") if len(c) == 3)],
    "alarmes": [evento(c) for c in linhas("ALARMES")],
    "historico": {"total": int(os.environ.get("N_HISTORICO") or 0), "itens": [evento(c) for c in linhas("HISTORICO")]},
    "barramento": barramento,
    "conteineres": [{"camada": c[0], "nome": c[1], "estado": c[2], "status": c[3]} for c in linhas("CONTEINERES") if len(c) == 4],
    "falhas": falhas,
}, ensure_ascii=False))
PY
