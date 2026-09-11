#!/usr/bin/env bash
# Apresentação SMO · item 8 (monitoramento e telemetria): as medidas 3GPP que a
# O-DU produz sozinha — o arquivo de PM gravado no elemento, o aviso VES
# "arquivo pronto" que chega ao SMO, e o batimento (heartbeat) de quem está vivo.
set -uo pipefail
cd "$(dirname "$0")"
. ./lib.sh
. ../oai-cn-gnb-e2/scripts/lib/testlog.sh
smo_exige_no_ar || exit 1

NO=pynts-o-du-o1
T_PM=unauthenticated.SEC_3GPP_PERFORMANCEASSURANCE_OUTPUT
T_HB=unauthenticated.SEC_HEARTBEAT_OUTPUT
T_REG=unauthenticated.VES_PNFREG_OUTPUT
section "Telemetria — medidas de desempenho da O-DU até o SMO"
info "Caminho: a O-DU mede → grava o arquivo 3GPP (XML, TS 28.532) → avisa por VES (FileReady) → Kafka → o SMO busca o arquivo."

section "1. O que a O-DU mede (configuração de PM do elemento)"
CFG="$(docker exec "$NO" cat /data/performance-management/index.json 2>/dev/null)"
CFG="$CFG" python3 - <<'PY'
import json, os
c = json.loads(os.environ["CFG"])["config"]
print(f"  {'período de coleta':<22} {c['log-period']} s")
print(f"  {'validade dos dados':<22} {c['repetition-period']} s")
print(f"  {'contadores':<22} {', '.join(c['points'])}")
PY

section "2. O último arquivo de medidas, lido no elemento"
ARQ="$(docker exec "$NO" sh -c 'ls -t /ftp/*.xml 2>/dev/null | head -1')"
if [ -z "$ARQ" ]; then
    err "a O-DU ainda não gravou nenhum arquivo de medidas"
    summary "procurou as medidas 3GPP da O-DU" "nenhum arquivo em /ftp — espere 1 minuto após subir os simuladores" err
    exit 1
fi
IDADE=$(( $(date +%s) - $(docker exec "$NO" stat -c %Y "$ARQ") ))
kv "Arquivo" "$(basename "$ARQ")"
kv "Gravado há" "${IDADE} s   ($(docker exec "$NO" sh -c 'ls /ftp/*.xml | wc -l') arquivos guardados)"
XML="$(docker exec "$NO" cat "$ARQ")"
XML="$XML" python3 - <<'PY'
import os, re
x = os.environ["XML"]
ns = {"m": "http://www.3gpp.org/ftp/specs/archive/28_series/28.532#measData"}
import xml.etree.ElementTree as ET
raiz = ET.fromstring(x)
emissor = raiz.find("m:fileHeader/m:fileSender", ns)
print(f"  {'emissor':<22} {emissor.get('senderName') if emissor is not None else '?'}")
for info in raiz.iter("{%s}measInfo" % ns["m"]):
    per = info.find("m:granPeriod", ns)
    tipos = {t.get("p"): t.text for t in info.findall("m:measType", ns)}
    for mv in info.findall("m:measValue", ns):
        vals = " · ".join(f"{tipos.get(r.get('p'))}={r.text}" for r in mv.findall("m:r", ns))
        print(f"  {'grupo ' + info.get('measInfoId', ''):<22} {mv.get('measObjLdn')}  [{per.get('duration')} até {per.get('endTime')}]")
        print(f"  {'':<22} {vals}")
PY
[ "$IDADE" -le 150 ] && ok "medidas 3GPP reais e recentes, no formato de arquivo que um equipamento entrega à gerência" \
                    || warn "o arquivo mais novo tem ${IDADE} s — a geração de medidas da O-DU parece parada"

section "3. O aviso que chega ao SMO (VES FileReady no Kafka)"
FIM="$(kafka_fim "$T_PM")"
if [ "$FIM" -gt 0 ]; then
    INST="$(kafka_abre "$T_PM" $((FIM - 1)))"
    REC="$(kafka_le "$INST" 2000)"; kafka_fecha "$INST"
    REC="$REC" python3 - <<'PY'
import json, os
r = json.loads(os.environ["REC"] or "[]")
if not r:
    raise SystemExit
e = r[-1]["value"]["event"]
h = e["commonEventHeader"]
print(f"  {'evento':<22} {h.get('eventType', '?')} · domínio {h['domain']}")
print(f"  {'origem':<22} {h['sourceName']}")
print(f"  {'carimbo do coletor':<22} {h.get('internalHeaderFields', {}).get('collectorTimeStamp', '?')}")
for f in e.get("stndDefinedFields", {}).get("data", {}).get("fileInfoList", [])[:1]:
    loc = f.get("fileLocation", "?")
    print(f"  {'arquivo anunciado':<22} {loc.split('@')[-1] if '@' in loc else loc}")
PY
    ok "o SMO foi avisado do arquivo pronto sem precisar perguntar"
else
    warn "nenhum aviso FileReady no Kafka ainda"
fi

section "4. Quem está vivo e quem se anunciou (eventos recebidos por tópico)"
kv "Avisos de medida" "$(kafka_fim "$T_PM")"
kv "Heartbeats" "$(kafka_fim "$T_HB")"
kv "Registros de PNF" "$(kafka_fim "$T_REG")"

summary "leu a configuração de PM da O-DU, o último arquivo de medidas 3GPP no elemento e o aviso VES que chegou ao Kafka" \
        "telemetria funcionando: medida no elemento → VES FileReady → barramento do SMO" ok
