#!/bin/bash
# Coerência de configuração (Projeto 1) — gnb.yaml ↔ ue.yaml.
# Baseado no checklist do professor (aula01, slides 80–85): PLMN (MCC/MNC),
# slice (SST) e APN/DNN devem coincidir entre gNB, UE e assinante. Divergência
# é a causa mais comum de "N2 OK mas o UE não conecta".

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"
# shellcheck source=lib/testlog.sh
source "$SCRIPT_DIR/lib/testlog.sh"

GNB="ueransim/configs/gnb.yaml"
UE="ueransim/configs/ue.yaml"
fails=0

section "Coerência de config — gNB ↔ UE (PLMN · slice · APN)"

if [ ! -f "$GNB" ] || [ ! -f "$UE" ]; then
    err "Configs não encontradas ($GNB / $UE)."
    summary "tentou comparar gnb.yaml e ue.yaml" "arquivos de config ausentes" err
    exit 0
fi

gnb_mcc=$(grep -oP '^\s*mcc:\s*"?\K[0-9]+' "$GNB" | head -1)
gnb_mnc=$(grep -oP '^\s*mnc:\s*"?\K[0-9]+' "$GNB" | head -1)
gnb_sst=$(grep -oP 'sst:\s*\K[0-9]+' "$GNB" | head -1)
gnb_tac=$(grep -oP '^\s*tac:\s*\K[0-9]+' "$GNB" | head -1)
ue_mcc=$(grep -oP '^\s*mcc:\s*"?\K[0-9]+' "$UE" | head -1)
ue_mnc=$(grep -oP '^\s*mnc:\s*"?\K[0-9]+' "$UE" | head -1)
ue_sst=$(grep -oP 'sst:\s*\K[0-9]+' "$UE" | head -1)
ue_apn=$(grep -oP 'apn:\s*"?\K[A-Za-z0-9._-]+' "$UE" | head -1)
ue_supi=$(grep -oP 'supi:\s*"?\K[a-z0-9-]+' "$UE" | head -1)

cmp() {  # $1 rótulo  $2 valor gNB  $3 valor UE
    if [ -n "$2" ] && [ "$2" = "$3" ]; then
        ok "$1 coincide: $2"
    else
        err "$1 DIVERGE — gNB='$2' · UE='$3'"
        fails=$((fails+1))
    fi
}

cmp "PLMN MCC" "$gnb_mcc" "$ue_mcc"
cmp "PLMN MNC" "$gnb_mnc" "$ue_mnc"
cmp "Slice SST" "$gnb_sst" "$ue_sst"

if [ -n "$ue_apn" ]; then
    ok "APN/DNN do UE: $ue_apn (deve existir no perfil SMF/UPF do Open5GS)"
else
    warn "UE sem APN/DNN definido."
    fails=$((fails+1))
fi

kv "PLMN (gNB)" "${gnb_mcc}/${gnb_mnc}  ·  TAC ${gnb_tac:-?}"
kv "SUPI (UE)" "${ue_supi:-?}"

if [ "$fails" -eq 0 ]; then
    summary "comparou PLMN (MCC/MNC), slice (SST) e APN entre gnb.yaml e ue.yaml" \
            "Configs coerentes — PLMN/slice/APN batem; o UE deve registrar e conectar" ok
else
    summary "comparou PLMN (MCC/MNC), slice (SST) e APN entre gnb.yaml e ue.yaml" \
            "$fails divergência(s) — corrija para que o UE consiga registrar (slides 80–85)" err
fi
