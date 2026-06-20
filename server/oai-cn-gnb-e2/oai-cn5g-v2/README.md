# Core OAI 5G v2.2.1 — com plano de usuário (UPF) no arm64

Deployment **paralelo** ao core v1.5.1 (`../oai-cn5g-fed/`). Objetivo: ter **UPF real
no arm64** (`oai-upf`, datapath `simple_switch`) — o que o v1.5.1 não tinha (UPF era
`oai-upf-vpp`, Intel-only; ver memória `project-oai-arm64-no-userplane`).

## Por que v2.2.1
A OAI publica imagens **multi-arch (amd64+arm64) oficiais** a partir do `v2.1.10`.
O `v2.2.1` (2026-04-14) tem **7/7 NFs com arm64**, incluindo `oai-upf`. Isso permite
dar `pull` em vez de buildar à mão (aposenta o `build-oai-arm64.sh`).

Verificado no Graviton2: `oai-upf:v2.2.1` baixa, `Arch=arm64`, roda nativo (`uname -m`
→ `aarch64`), binário `/openair-upf/bin/oai_upf` presente.

## Config (casa com o gNB atual — `../scripts/gnb_24prb.conf`)
- PLMN **MCC 208 / MNC 95**, TAC **0xa000** (=40960)
- Slice **SST 222 / SD 0x00007B** (=123), DNN **default** (pool 12.1.1.0/26)
- UPF: `enable_bpf_datapath: no` (simple_switch, userspace — sem dependência de kernel)
       + `enable_snat: yes` (UE alcança a internet via N6)
- AMF com IP fixo **192.168.70.132** (o gNB aponta N2 pra cá)
- DNS do UE: 8.8.8.8 / 1.1.1.1

## Como subir (no servidor; gated até validação)
```bash
./up_core_v2.sh          # remove core v1.5.1, sobe v2.2.1, espera AMF healthy
../scripts/up_e2_lab.sh  # RIC + gNB + nrUE (como sempre)
```

## Validação (o que provar que funcionou)
```bash
docker logs oai-smf 2>&1 | grep -iE 'association|pfcp|upf'   # PFCP/N4 SMF<->UPF UP
docker logs oai-upf 2>&1 | grep -iE 'association|datapath'
ip addr show oaitun_ue1                                       # UE ganhou IP 12.1.1.x
# tcpdump -v na N3 durante ping → mostra encapsulamento GTP-U (IP interno UE + externo túnel)
```

## Rollback (volta pro v1.5.1 control-plane-only)
```bash
./down_core_v2.sh
../scripts/up_core.sh
```

## Pendências / riscos conhecidos
- `trf-gen-cn5g:latest` (ext-dn): confirmar arm64; se não tiver, ext-dn não sobe — mas
  com SNAT no UPF o acesso à internet não depende dele (ext-dn é opcional).
- IMSI do nrUE precisa existir no `database/oai_db2.sql` (subscribers 20895000000003x).
- eBPF datapath fica como otimização futura (precisa features BPF do host).
