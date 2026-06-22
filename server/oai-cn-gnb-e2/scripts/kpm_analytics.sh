#!/usr/bin/env bash
# kpm_analytics.sh — "exportar o lab para análise" (Aula 06, slide 46).
#
# PORQUÊ deste script (didático):
#   O xApp KPM (xapp_kpm_moni) entrega telemetria E2SM-KPM como TEXTO BRUTO em
#   logs/xapp_kpm_lab.log — uma INDICATION por período de report (~1 s), cada uma
#   com medidas por UE. Isso é o "data exhaust" do control plane (RIC). Para virar
#   INFORMAÇÃO, ele precisa percorrer a cadeia (Aula 06, slide 44):
#       Coleta → Ingestão/lake → ETL/EDA → Indicador (KPI) → Decisão
#   Este script faz Coleta→ETL→KPI→Visualização e aponta a Decisão. É o mesmo
#   workflow da disciplina "Análise de Dados em Redes de Telecom" (Módulo 7),
#   e o insumo direto do xApp/rApp do grupo (UE-TP-rApp: previsão de throughput).
#
# Uso:  ./scripts/kpm_analytics.sh [caminho/do/xapp_kpm_lab.log]
#       (default: logs/xapp_kpm_lab.log). Gera logs/kpm_timeseries.csv.
#
# Princípio do projeto: ZERO tempo cego — nada de sleep/timeout; só lê o arquivo.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=/dev/null
. "$SCRIPT_DIR/lib/testlog.sh"

LOG="${1:-$PROJECT_DIR/logs/xapp_kpm_lab.log}"
CSV="$PROJECT_DIR/logs/kpm_timeseries.csv"
SLICE="${KPM_SLICE:-222/123}"      # slice do lab (SST=222/SD=123); dimensão/tag
PERIOD_MS="${KPM_PERIOD_MS:-1000}" # período de report do KPM (~1 s) — eixo de tempo

# ─────────────────────────────────────────────────────────────────────────────
section "1. Coleta — de onde vêm os dados"
info "Fonte: $LOG"
kv "o que é" "saída do xApp E2SM-KPM (gNB OAI → FlexRIC → xApp), texto bruto"
kv "granularidade" "1 INDICATION por período de report (~${PERIOD_MS} ms)"
kv "por quê importa" "é a MESMA rede vista pela lente de DADOS (não de controle)"

if [ ! -f "$LOG" ]; then
    err "log não encontrado: $LOG"
    info "rode antes: ./scripts/test_e2_kpm.sh (KPM_TRAFFIC=1 gera tráfego p/ throughput)"
    summary "tentou ler a telemetria KPM" "arquivo de log ausente — nada a analisar" err
    exit 1
fi
N_IND=$(grep -c "KPM ind_msg latency" "$LOG" 2>/dev/null || echo 0)
ok "INDICATIONs encontradas no log: $N_IND"

# ─────────────────────────────────────────────────────────────────────────────
section "2. ETL — parse do texto para série temporal (CSV)"
kv "por quê" "cada linha 'measName = valor unidade' ≈ um EVENTO de série temporal"
kv "esquema (slide 39)" "timestamp · measName · valor · dimensões(UE,slice) · fonte"

# awk: estado por INDICATION (seq) e por UE; emite 1 linha CSV por medida.
mkdir -p "$(dirname "$CSV")"
awk -v OFS=',' -v SLICE="$SLICE" '
  BEGIN { print "seq","latency_us","ue","measName","value","unit","slice" }
  # Cabeçalho da INDICATION:  "   12 KPM ind_msg latency = 34567 [μs]"
  /KPM ind_msg latency/ {
    seq=$1+0; ue="-"; lat=""
    for (i=1;i<=NF;i++) if ($i=="=") { lat=$(i+1)+0; break }
    next
  }
  # Bloco por UE (dimensão): ran_ue_id é o mais específico
  /ran_ue_id =/        { ue="ran:" $NF; next }
  /amf_ue_ngap_id =/   { if (ue=="-") ue="amf:" $NF; next }
  # Medida 3GPP: nome no formato Familia.Nome (tem ponto), valor numérico
  /^[A-Za-z0-9]+\.[A-Za-z0-9._]+/ {
    name=$1; gsub(/\[.*\]/,"",name)          # tira [BinX=..] se houver
    if ($2=="=" && $3 ~ /^-?[0-9]+(\.[0-9]+)?$/) {
      unit=""; for (i=4;i<=NF;i++) unit=unit (i>4?" ":"") $i
      print seq, lat, ue, name, $3, unit, SLICE
    }
    next
  }
' "$LOG" > "$CSV"

N_ROWS=$(($(wc -l < "$CSV") - 1))
ok "série temporal extraída: $N_ROWS amostras → $CSV"
if [ "$N_ROWS" -gt 0 ]; then
    step "primeiras linhas (cabeçalho + 3):"
    head -4 "$CSV" | sed 's/^/    /'
fi

# Legenda didática das medidas mais comuns
section "Legenda das medidas (o que cada measName significa)"
kv "DRB.UEThpDl/Ul" "throughput por UE no DL/UL (kbps) — o KPI central do UE-TP-rApp"
kv "RRU.PrbTotDl/Ul" "% de PRBs (blocos de rádio) usados — ocupação da célula"
kv "DRB.PdcpSduVolume*" "volume de dados PDCP — quanto trafegou"

# ─────────────────────────────────────────────────────────────────────────────
section "3. KPI — do dado bruto ao indicador"
kv "por quê" "KPI condensa milhares de amostras num número de decisão (slide 44)"

if [ "$N_ROWS" -eq 0 ]; then
    warn "nenhuma medida KPM no log — provável AUSÊNCIA DE TRÁFEGO no período"
    info "o E2/subscription pode estar OK, mas sem UE gerando dados o throughput é ~0"
    info "para dados reais: UE attachado + ./scripts/test_e2_kpm.sh com KPM_TRAFFIC=1"
    summary "montou a cadeia Coleta→ETL e preparou o CSV" \
            "pipeline pronto, porém sem amostras (rode com tráfego para KPIs reais)" warn
    exit 0
fi

# KPIs por UE para throughput + ocupação de PRB (média, máx, nº de amostras)
awk -F',' -v PER="$PERIOD_MS" '
  NR==1 { next }
  $4 ~ /^DRB\.UEThp(Dl|Ul)$/ || $4 ~ /^RRU\.PrbTot(Dl|Ul)$/ {
    k=$4 " | " $3
    n[k]++; sum[k]+=$5; if ($5>max[k]) max[k]=$5; unit[k]=$6
  }
  END {
    for (k in n) {
      win = n[k]*PER/1000.0
      printf "  %-26s n=%-4d média=%.2f %-5s máx=%.2f %-5s (janela≈%.0fs)\n",
             k, n[k], sum[k]/n[k], unit[k], max[k], unit[k], win
    }
  }
' "$CSV" | sort
ok "KPIs calculados por UE (ex.: 'throughput UL médio por UE' — slide 46)"

# ─────────────────────────────────────────────────────────────────────────────
section "4. Visualização — EDA sem dependências (sparkline ASCII)"
kv "por quê" "a forma da curva revela bursts de tráfego (cf. plots NGO, slide 40)"

# Sparkline de DRB.UEThpUl ao longo das INDICATIONs (eixo de tempo = seq)
awk -F',' '$4=="DRB.UEThpUl"{print $5}' "$CSV" | awk '
  { v[NR]=$1; if($1>mx)mx=$1 }
  END {
    if (NR==0 || mx==0) { print "    (sem amostras de DRB.UEThpUl > 0)"; exit }
    # atribuição explícita: split("","") quebra por BYTE e corrompe glifos UTF-8
    b[1]="▁"; b[2]="▂"; b[3]="▃"; b[4]="▄"; b[5]="▅"; b[6]="▆"; b[7]="▇"; b[8]="█"
    line="    "
    for (i=1;i<=NR;i++){ idx=int(v[i]/mx*7)+1; if(idx<1)idx=1; line=line b[idx] }
    print line
    printf "    DRB.UEThpUl ao longo do tempo (máx=%.2f) — %d amostras\n", mx, NR
  }'

# ─────────────────────────────────────────────────────────────────────────────
section "5. Decisão — para onde isso vai"
kv "loop de controle" "KPI → xApp/rApp decide (slide 44: Decisão)"
kv "tema do grupo" "UE-TP-rApp prevê throughput por UE a partir dessas séries"
kv "Módulo 7" "este CSV é a entrada de EDA/ML (notebook, pandas) da Análise de Dados"
kv "artefato p/ levar" "$CSV (abra em planilha/notebook para o passo de modelagem)"

summary "extraiu a telemetria KPM (texto) para série temporal (CSV), calculou KPIs por UE e plotou a evolução do throughput" \
        "pipeline Coleta→ETL→KPI→Visualização completo; $N_ROWS amostras, pronto para modelagem (UE-TP-rApp / Módulo 7)" ok
