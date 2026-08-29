#!/bin/bash
# Para laboratório E2 (gNB, FlexRIC; Core permanece ativo).
# Uso: ./scripts/down_e2_lab.sh [--all]
#
# --all  também para o Core OAI
#
# down_gnb_oai.sh e down_flexric.sh CONFEREM o que sobrou e saem com 1 quando
# algo continua vivo. Esse veredito é a única coisa que o painel tem para saber
# se o lab realmente parou, então aqui ele não pode ser jogado fora: nada de
# `2>/dev/null` (que apagava a mensagem do erro) nem de `|| true` (que apagava o
# próprio erro). Sem `-e` de propósito -- queremos TENTAR os dois e só depois
# reportar, em vez de abortar no primeiro e deixar metade do lab de pé.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Parando laboratório E2..."

rc=0
"$SCRIPT_DIR/down_gnb_oai.sh" || rc=1
"$SCRIPT_DIR/down_flexric.sh" || rc=1

if [ "${1:-}" = "--all" ]; then
    "$SCRIPT_DIR/down_core.sh" || rc=1
fi

if [ "$rc" -ne 0 ]; then
    echo "ERRO: o laboratório E2 NÃO parou por inteiro (veja o erro acima)." >&2
    exit 1
fi

echo "Laboratório E2 parado."
