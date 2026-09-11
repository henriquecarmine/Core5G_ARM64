#!/usr/bin/env bash
# Apresentação SMO · itens 4 e 5 (interface O1; gerenciamento): o SMO lê, pela
# O1, a configuração de um elemento O-RAN — os modelos 3GPP da gNB-DU e da célula
# NR que a O-DU simulada anuncia. Tudo por RESTCONF no controlador, que fala
# NETCONF com o elemento.
set -uo pipefail
cd "$(dirname "$0")"
. ./lib.sh
. ../oai-cn-gnb-e2/scripts/lib/testlog.sh
smo_exige_no_ar || exit 1

NO=pynts-o-du-o1
section "O1 — o SMO lendo a configuração de um elemento"
info "Caminho: painel → gateway → controlador SDN-R (RESTCONF) → NETCONF/TLS → O-DU."
kv "Elemento" "$NO (O-DU simulada, pynts)"

section "1. O elemento está montado no controlador?"
ESTADO="$(restconf GET "$MONTAGEM/node=$NO?content=nonconfig")"
LINHA="$(ESTADO="$ESTADO" python3 - <<'PY'
import json, os, collections
d = json.loads(os.environ["ESTADO"] or "{}").get("network-topology:node", [{}])[0]
nc = d.get("netconf-node-topology:netconf-node", {})
caps = [c["capability"] for c in nc.get("available-capabilities", {}).get("available-capability", [])]
fam = collections.Counter("O-RAN" if "o-ran-" in c else "3GPP" if "_3gpp-" in c else "IETF" if "ietf-" in c else "outros" for c in caps)
print(nc.get("connection-status", "ausente"), nc.get("host", "?"), nc.get("port", "?"), len(caps),
      " · ".join(f"{k} {v}" for k, v in fam.most_common()), sep="|")
PY
)"
IFS='|' read -r CON HOST PORTA NCAPS FAMILIAS <<<"$LINHA"
kv "Conexão" "$CON (NETCONF em $HOST:$PORTA)"
kv "Modelos YANG" "$NCAPS anunciados — $FAMILIAS"
if [ "$CON" != connected ]; then
    err "a O-DU não está conectada ao controlador"
    summary "tentou ler a O-DU pela O1" "elemento não conectado — rode o teste de ciclo de vida ou ./up_smo.sh network" err
    exit 1
fi
ok "O-DU conectada: o SMO sabe o que pode ler e configurar nela pelos modelos que ela anunciou"

section "2. Leitura pela O1 — ManagedElement → GNBDUFunction → NRCellDU"
ME="$(docker exec "$NO" sysrepocfg -X -d running -f json -m _3gpp-common-managed-element 2>/dev/null)"
CHAVES="$(ME="$ME" python3 -c 'import json,os; me=json.loads(os.environ["ME"])["_3gpp-common-managed-element:ManagedElement"][0]; du=me["_3gpp-nr-nrm-gnbdufunction:GNBDUFunction"][0]; print(me["id"], du["id"], du["_3gpp-nr-nrm-nrcelldu:NRCellDU"][0]["id"])' 2>/dev/null)"
read -r ME_ID DU_ID CEL_ID <<<"$CHAVES"
info "chaves da árvore: $ME_ID / $DU_ID / $CEL_ID"
BASE="$MONTAGEM/node=$NO/yang-ext:mount/_3gpp-common-managed-element:ManagedElement=$ME_ID/_3gpp-nr-nrm-gnbdufunction:GNBDUFunction=$DU_ID"
T0=$(date +%s%3N)
DU="$(restconf GET "$BASE/attributes")"
CEL="$(restconf GET "$BASE/_3gpp-nr-nrm-nrcelldu:NRCellDU=$CEL_ID/attributes")"
T1=$(date +%s%3N)
LIDO="$(DU="$DU" CEL="$CEL" python3 - <<'PY'
import json, os
du = json.loads(os.environ["DU"] or "{}").get("_3gpp-nr-nrm-gnbdufunction:attributes", {})
cel = json.loads(os.environ["CEL"] or "{}").get("_3gpp-nr-nrm-nrcelldu:attributes", {})
if not du:
    raise SystemExit(1)
print("gNB-DU (GNBDUFunction)")
for k in ("gNBId", "gNBIdLength", "gNBDUId", "gNBDUName", "priorityLabel"):
    if k in du: print(f"  {k:<22} {du[k]}")
print("célula NR (NRCellDU)")
for k in ("cellLocalId", "nRPCI", "arfcnDL", "ssbFrequency", "ssbSubCarrierSpacing", "ssbPeriodicity"):
    if k in cel: print(f"  {k:<22} {cel[k]}")
plmn = cel.get("pLMNInfoList", [])
if plmn:
    redes = sorted({f"{p['mcc']}/{p['mnc']}" for p in plmn})
    fatias = sorted(p.get("sst") for p in plmn)
    print(f"  {'PLMN e fatias':<22} {', '.join(redes)} · {len(plmn)} fatias (SST {', '.join(map(str, fatias))})")
print(f"  {'(atributos na célula)':<22} {len(cel)} no total")
PY
)"
if [ -z "$LIDO" ]; then
    err "o controlador não devolveu os atributos da gNB-DU"
    summary "tentou ler a O-DU pela O1" "leitura RESTCONF falhou" err
    exit 1
fi
printf '%s\n' "$LIDO"
ok "leitura pela O1 em $((T1 - T0)) ms (duas consultas RESTCONF → NETCONF get-config)"

section "3. Também sob gerência: o O-RU no modelo híbrido"
ORU="$(restconf GET "$MONTAGEM/node=pynts-o-ru-hybrid?content=nonconfig" | python3 -c 'import json,sys; nc=json.load(sys.stdin)["network-topology:node"][0]["netconf-node-topology:netconf-node"]; print(nc.get("connection-status"), len(nc["available-capabilities"]["available-capability"]))' 2>/dev/null)"
read -r ORU_CON ORU_CAPS <<<"$ORU"
[ "${ORU_CON:-}" = connected ] && ok "pynts-o-ru-hybrid conectado pelo M-plane, com $ORU_CAPS modelos YANG" \
                               || warn "pynts-o-ru-hybrid: ${ORU_CON:-ausente}"

summary "leu pela O1 a configuração 3GPP da O-DU ($NCAPS modelos YANG): gNB-DU e célula NR, via RESTCONF → NETCONF" \
        "gerenciamento O1 funcionando — o SMO enxerga a configuração real do elemento" ok
