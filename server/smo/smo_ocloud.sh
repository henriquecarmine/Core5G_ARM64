#!/usr/bin/env bash
# Apresentação SMO · itens 4 (O2) e 6 (capacidades de gerenciamento do O-Cloud):
# a resposta honesta. O OAM do O-RAN SC NÃO implementa O2 — no O-RAN SC, o O2
# (IMS e DMS) mora no projeto INF, sobre StarlingX. Este teste mostra o que um
# O2 IMS exporia do nosso O-Cloud, lido direto do servidor: pool de recursos,
# gerenciador de implantação e as funções implantadas com o que consomem.
set -uo pipefail
cd "$(dirname "$0")"
. ./lib.sh
. ../oai-cn-gnb-e2/scripts/lib/testlog.sh
smo_exige_no_ar || exit 1

section "O-Cloud e O2 — o que a solução tem e o que não tem"
warn "O OAM do O-RAN SC não traz O2: não há IMS nem DMS nesta solução."
info "No O-RAN SC, o O2 é do projeto INF (O2 IMS/DMS sobre StarlingX), que pede uma máquina dedicada."
info "Abaixo, o que um O2 IMS mostraria do nosso O-Cloud — lido do próprio servidor, sem O2 no meio."

section "1. Pool de recursos (o que o IMS inventariaria)"
kv "Arquitetura" "$(uname -m) ($(lscpu 2>/dev/null | awk -F: '/Model name/{gsub(/^ +/,"",$2); print $2; exit}'))"
kv "vCPU" "$(nproc)"
kv "Memória" "$(free -h | awk '/Mem:/{print $2 " total · " $7 " disponível"}')"
kv "Disco" "$(df -h / | awk 'NR==2{print $2 " total · " $4 " livre"}')"
kv "Carga" "$(cut -d' ' -f1-3 /proc/loadavg) (1 · 5 · 15 min)"

section "2. Gerenciador de implantação (o papel do DMS)"
kv "Runtime" "Docker $(docker version --format '{{.Server.Version}}') · Compose $(docker compose version --short)"
kv "Implantações do SMO" "$(docker compose ls --format json 2>/dev/null | python3 -c 'import json,sys; print(", ".join(p["Name"] + " (" + p["Status"] + ")" for p in json.load(sys.stdin) if p["Name"].startswith("smo-")))')"

section "3. Funções implantadas e o que consomem agora"
TOTAL_MEM=0
while IFS='|' read -r nome cpu mem; do
    kv "$nome" "CPU $cpu · memória $mem"
done < <(docker stats --no-stream --format '{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}' \
           $(docker ps -q --filter label=solution=o-ran-sc-smo) $(docker ps -q --filter name=pynts-) | sort)
USO="$(docker stats --no-stream --format '{{.MemUsage}}' $(docker ps -q --filter label=solution=o-ran-sc-smo) $(docker ps -q --filter name=pynts-) \
        | python3 -c 'import sys,re
tot=0
for l in sys.stdin:
    v,u=re.match(r"([\d.]+)(\w+)", l.split("/")[0].strip()).groups()
    tot+=float(v)*{"B":1e-6,"KiB":1/1024,"MiB":1,"GiB":1024}.get(u,1)
print(f"{tot/1024:.1f}")')"
ok "SMO + simuladores usando ${USO} GB de memória neste O-Cloud"

section "4. O que ficaria com o O2"
info "IMS (infraestrutura): inventário e alarmes do O-Cloud publicados ao SMO — aqui feitos à mão acima."
info "DMS (implantação): instanciar, escalar e encerrar NFs pelo SMO — aqui feito pelo Docker (ver o teste de ciclo de vida)."

summary "inventariou o O-Cloud do lab (recursos, runtime e funções implantadas) e deixou explícito que o OAM do O-RAN SC não implementa O2" \
        "O-Cloud visível e medido; O2 ausente nesta solução — fica no projeto INF do O-RAN SC" warn
