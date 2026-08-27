#!/bin/bash
# Para nearRT-RIC e xApps FlexRIC.
# Uso: ./scripts/down_flexric.sh
#
# O RIC sobe como SERVICO TRANSIENTE do systemd e como ROOT
# (up_flexric.sh: `sudo systemd-run --unit=oai-flexric`). Duas consequencias
# que ja quebraram o botao "E2 lab" do painel:
#   1. o painel roda como 'ubuntu'; `pkill` sem sudo num processo de root volta
#      "Operation not permitted", o erro some no `|| true` e o RIC continua vivo
#      -- o botao ficava aceso para sempre;
#   2. matar o processo de um servico deixa a unit em 'failed', e por isso o
#      up_flexric.sh precisa de um `reset-failed` antes de subir de novo.
# Por isso aqui: PARA A UNIT primeiro, pkill com sudo so como rede para o
# caminho nohup, e no fim CONFERE em vez de anunciar sucesso sem olhar.
set -uo pipefail

echo "Parando nearRT-RIC e xApps FlexRIC..."

# 1. o caminho normal: a unit transiente (para o servico e limpa o estado)
if command -v systemctl >/dev/null 2>&1; then
    sudo systemctl stop oai-flexric.service 2>/dev/null || true
    sudo systemctl reset-failed oai-flexric.service 2>/dev/null || true
fi

# 2. rede de seguranca: instalacao sem systemd (nohup) ou processo orfao.
#    COM sudo: o RIC roda como root e o painel nao.
sudo pkill -x "nearRT-RIC" 2>/dev/null || true

# 3. xApps (sobem em foreground/nohup pelos scripts de teste).
#    O colchete em [x]app_ nao muda o que casa (ainda e "xapp_"), mas impede
#    que o padrao case com a PROPRIA linha de comando do `sudo pkill` -- o
#    pkill so se exclui a si mesmo, nao ao sudo que o invocou, e sem o truque
#    ele mata o proprio wrapper e o console enche de "Killed".
sudo pkill -9 -f "[x]app_" 2>/dev/null || true

sleep 1

# 4. conferencia honesta: o painel le o estado por pgrep, entao o que importa
#    e o que sobrou de verdade -- nao o que o script gostaria de ter feito.
if pgrep -x "nearRT-RIC" >/dev/null 2>&1; then
    echo "ERRO: nearRT-RIC AINDA em execucao (PID $(pgrep -x nearRT-RIC | tr '\n' ' '))." >&2
    echo "      Verifique se o sudo do painel esta liberado: sudo -n true" >&2
    exit 1
fi
if pgrep -f "xapp_" >/dev/null 2>&1; then
    echo "Aviso: ainda ha xApp em execucao: $(pgrep -af 'xapp_' | head -3)" >&2
fi
echo "FlexRIC parado."
