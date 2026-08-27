#!/bin/bash
# Para o RAN gNB OAI (gNB + nrUE).
# Uso: ./scripts/down_gnb_oai.sh
#
# gNB e nrUE sobem como SERVICOS TRANSIENTES do systemd e como root
# (up_gnb_oai.sh: `sudo systemd-run --unit=oai-gnb` / `--unit=oai-nrue`).
# Parar a unit e o caminho certo: so matar o processo deixa a unit em 'failed'
# e obriga o `reset-failed` na proxima subida. O pkill fica como rede para o
# caminho nohup -- sempre com sudo, porque o painel roda como 'ubuntu' e os
# processos sao de root.
set -uo pipefail

echo "=========================================="
echo "Parando RAN gNB OAI (gNB + nrUE)"
echo "=========================================="
echo ""

# 1. as units transientes (nrUE primeiro: ele depende do gNB)
if command -v systemctl >/dev/null 2>&1; then
    for u in oai-nrue.service oai-gnb.service oai-nrue.scope oai-gnb.scope; do
        sudo systemctl stop "$u" 2>/dev/null || true
        sudo systemctl reset-failed "$u" 2>/dev/null || true
    done
fi

# 2. rede de seguranca (nohup ou processo orfao)
if pgrep -x "nr-uesoftmodem" >/dev/null 2>&1; then
    echo "Parando nrUE..."
    sudo pkill -x "nr-uesoftmodem" 2>/dev/null || true
    sleep 2
fi
if pgrep -x "nr-softmodem" >/dev/null 2>&1; then
    echo "Parando gNB..."
    sudo pkill -x "nr-softmodem" 2>/dev/null || true
    sleep 2
fi

# 3. insistir uma vez com SIGKILL antes de desistir
for p in nr-uesoftmodem nr-softmodem; do
    if pgrep -x "$p" >/dev/null 2>&1; then
        echo "$p resistiu ao TERM; enviando KILL..."
        sudo pkill -9 -x "$p" 2>/dev/null || true
        sleep 1
    fi
done

# 4. conferencia honesta (e o que o painel le por pgrep)
if pgrep -x "nr-softmodem" >/dev/null 2>&1 || pgrep -x "nr-uesoftmodem" >/dev/null 2>&1; then
    echo "ERRO: ainda em execucao: $(pgrep -ax 'nr-softmodem' ; pgrep -ax 'nr-uesoftmodem')" >&2
    echo "      Verifique se o sudo do painel esta liberado: sudo -n true" >&2
    exit 1
fi

echo "Processos encerrados."
echo ""
echo "=========================================="
echo "gNB OAI parado com sucesso!"
echo "=========================================="
echo ""
echo "💡 Para reiniciar: ./scripts/up_gnb_oai.sh"
echo ""
