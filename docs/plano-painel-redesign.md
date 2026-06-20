# Plano — Redesign do painel + correção de ativação + testes dos labs

> Documento de planejamento (revisão antes de codar). Data: 2026-06-20.
> Escopo pedido pelo usuário: (1) topo = projetos + servidores com comando;
> (2) lateral esquerda = ferramentas **de cada projeto** (UE Lab, Demo,
> Topologia, Testes) trocando conforme o projeto ativo; (3) consertar o
> ativar/desativar dos serviços e definir o que pode subir junto; (4) montar
> os testes de cada lab a partir dos exercícios do professor (PDFs).

---

## 1. Bug "serviços não obedecem ativar/desativar" — diagnóstico

**Causa-raiz: descompasso v1 ↔ v2 do core OAI (Projeto 2).**

O servidor está rodando o **core OAI v2** (`oai-cn5g-v2/docker-compose-basic-nrf.yaml`,
9 containers `oai-*` v2.2.1, `mysql`), mas o painel ainda chama os scripts **v1**:

| Ação no painel | Script chamado (hoje) | Alvo real | Efeito |
|---|---|---|---|
| `p2-up-core` | `oai-cn-gnb-e2/scripts/up_core.sh` | compose **v1** `oai-cn5g-fed/docker-compose` | sobe core ERRADO (conflita com o v2) |
| `p2-down-core` | `oai-cn-gnb-e2/scripts/down_core.sh` | `docker compose down` no projeto **v1** | **não para os containers v2** → "desligar não obedece" |
| `p2-up-e2-lab` | `scripts/up_e2_lab.sh` | chama `up_core.sh` (v1) + flexric + gNB | usa core v1 |
| switch → P2 | `switch_project.sh` usa `up_e2_lab.sh`/`down_core.sh` (v1) | idem | troca de projeto quebrada p/ v2 |

Os scripts **v2 corretos** já existem no servidor:
`oai-cn5g-v2/up_core_v2.sh`, `oai-cn5g-v2/down_core_v2.sh`, `scripts/up_e2_lab_v2.sh`.
O `up_e2_lab_v2.sh` já garante o core v2 sozinho; o `up_core_v2.sh` já **derruba
Open5GS/UERANSIM** ao subir (exclusividade automática).

A detecção de estado (`server.py: read_group_status`) está **correta**: `p2-core`
casa com o container `oai-amf` (que existe no v2). O problema é só na **ação**.

### Correção (server-side, sem reescrever scripts)

Remapear `COMMANDS` em [server/panel/server.py](server/panel/server.py#L131-L134):

```python
"p2-up-core":     {"cmd": ["./up_core_v2.sh"],          "cwd": SERVER_DIR/"oai-cn-gnb-e2"/"oai-cn5g-v2"},
"p2-down-core":   {"cmd": ["./down_core_v2.sh"],        "cwd": SERVER_DIR/"oai-cn-gnb-e2"/"oai-cn5g-v2"},
"p2-up-e2-lab":   {"cmd": ["./scripts/up_e2_lab_v2.sh"],"cwd": SERVER_DIR/"oai-cn-gnb-e2"},
"p2-down-e2-lab": {"cmd": ["./scripts/down_e2_lab.sh"], "cwd": SERVER_DIR/"oai-cn-gnb-e2"},  # já OK (para gNB+RIC nativos)
```

E em [server/scripts/switch_project.sh](server/scripts/switch_project.sh): no
`down_p2` trocar `down_core.sh` → `oai-cn5g-v2/down_core_v2.sh`; no `case p2`
trocar `up_e2_lab.sh` → `scripts/up_e2_lab_v2.sh`.

---

## 2. Regras de co-ativação (o que sobe junto)

| Combinação | Permitido? | Motivo / como tratar |
|---|---|---|
| P1 Core sozinho | ✅ | base do P1 |
| P1 RAN sem Core | ❌ | `up_ran.sh` exige redes `net-n2/n3` do core → **UI deve travar RAN até Core on** |
| P1 Core + RAN | ✅ | caminho normal |
| P2 Core (OAI v2) sozinho | ✅ | leve (é o que está no ar agora) |
| P2 E2 lab sem Core | ⚠️ auto | `up_e2_lab_v2.sh` sobe o core v2 sozinho se faltar |
| P1 **e** P2 juntos | ❌ | **2 vCPUs**; RFSIM satura. Mutuamente exclusivos |

**Decisão de design:** a **ativação de PROJETO** (card "ativar" no topo) sempre
passa por `switch_project.sh` (exclusivo: derruba o outro, respeita ordem).
Os **toggles de servidor** dentro do projeto ativo ficam *dependency-aware*:
- RAN (P1) desabilitado enquanto Core (P1) estiver `off`;
- ligar um servidor de P2 com P1 no ar → primeiro oferece trocar de projeto.

---

## 3. Arquitetura da nova UI

```
┌─ Core5G_ARM64 — Painel ───────────────── ● P2 ativo ──── hcarmine (admin) ─┐
│ telemetria: CPU ▓▓░ · RAM ▓░ · Swap ░ · Disk ▓                            │  ← topo: marca + telemetria
├───────────────────────────────────────────────────────────────────────────┤
│ ┌ Projeto 1 · Open5GS ───────[ativar]┐  ┌ Projeto 2 · OAI/RIC ◉[ativar]─┐ │  ← faixa de projetos
│ │ Core ◯⏻   RAN ◯⏻                   │  │ Core ◉⏻   E2 lab ◯⏻           │ │     (servers = comando)
│ └────────────────────────────────────┘  └───────────────────────────────┘ │
├──────────────┬────────────────────────────────────────────────────────────┤
│ FERRAMENTAS  │  status: ocioso              [copiar] [limpar]              │
│ (do projeto  │ ┌────────────────────────────────────────────────────────┐ │
│  ativo)      │ │ console / saída                                         │ │
│ ▣ Topologia  │ │                                                        │ │
│ ▣ UE Lab     │ │                                                        │ │
│ ▣ Demo E2E   │ └────────────────────────────────────────────────────────┘ │
│ ── Testes ── │                                                            │
│ ▸ ...        │                                                            │
└──────────────┴────────────────────────────────────────────────────────────┘
```

- **Topo:** marca + telemetria + indicador de projeto ativo; abaixo a **faixa
  de 2 cards** (servidores = botão de comando), o ativo realçado.
- **Lateral esquerda (ícone + rótulo sempre):** mostra as ferramentas **do
  projeto ativo**, trocando ao trocar de projeto.
- Cores **padrão/referenciais** da paleta atual (verde=on, vermelho=off,
  âmbar=loading, laranja=ação).

---

## 4. Ferramentas por projeto (lateral)

| Projeto 1 · Open5GS | Projeto 2 · OAI/RIC |
|---|---|
| **Topologia P1** (Docker N2/N3/N4/N6, UE 10.60/16) | **Topologia P2** (Core→RIC→gNB→xApp, slice 208/95·222/123) |
| **UE Lab** (criar UE, throughput, atenuação) | *(UE é fixo no RFSIM; sem UE Lab)* |
| **Demonstração E2E** (UE→internet) | **Demo E2** (E2 SETUP → KPM → RC, guiada) |
| **Testes P1** (ver §5) | **Testes P2** (ver §5) |

> Cada projeto tem **sua própria topologia, UE Lab e demonstração**, como pedido.
> A lista lateral é dirigida por `_activeProj` (já existe no JS).

---

## 5. Plano de testes por lab (extraído dos PDFs do professor)

### Projeto 1 — Open5GS (aula01: "Exercício guiado — fluxo de registro")

| Teste | Status | Implementação |
|---|---|---|
| Status / Healthcheck dos NFs | ✅ existe | `healthcheck.sh` |
| **NG Setup OK** | ➕ novo | grep log AMF/gNB: `NG Setup procedure is successful` |
| **Registro do UE** | ➕ novo | grep `Initial UE Message` → `Registration accept`; estado do UE |
| **PDU Session + GTP-U** | ➕ novo | confirmar sessão PDU (SMF/N4) + TEID em uesimtun0 |
| Conectividade E2E (`ping -I uesimtun0 8.8.8.8`) | ✅ existe | `test_ue_connection.sh` |
| Throughput (iperf3) | ✅ existe | UE Lab |
| **Coerência de config** (PLMN, SST, APN em gnb.yaml/ue.yaml) | ➕ novo | diff dos campos-chave |
| Failover UPF-A/B | ✅ existe | `test_upf_failover.sh` |

### Projeto 2 — OAI/FlexRIC (aula04: "Demo guiada — laboratório E2")

| Teste | Status | Implementação |
|---|---|---|
| E2 SETUP gNB↔RIC (`Connected E2 nodes = 1`) | ✅ existe | `test_e2_sm.sh cust` |
| Custom SMs 142–148 | ✅ existe | idem |
| E2SM-KPM slice 222/123 | ✅ existe | `test_e2_kpm.sh` |
| **E2SM-KPM com tráfego** (`KPM_TRAFFIC=1`) | ➕ novo (var já suportada) | botão variante |
| E2SM-RC attach (`RRCSetupComplete`) | ✅ existe | `test_e2_rc_attach.sh` |
| Verificação completa (cust+kpm+rc) | ✅ existe | `e2_verify.sh` |
| Extensão A1 / política | ➕ futuro | aula03 |

> Conclusão: ~70% dos testes do professor **já existem**; o trabalho é
> reorganizá-los por projeto na lateral + adicionar 3 novos no P1 e 1 no P2.

---

## 6. Topologia por projeto

- **P1**: já existe (`openran-topology.json` + `topology.html`).
- **P2**: criar `openran-topology-p2.json` (Core OAI v2 → near-RT RIC →
  gNB RFSIM → xApps; slice 208/95 · 222/123) e parametrizar `topology.html`
  por `?proj=p1|p2`.

---

## 7. Mudanças arquivo-a-arquivo

| Arquivo | Mudança |
|---|---|
| [server/panel/server.py](server/panel/server.py) | remap `COMMANDS` p2-* → v2; +comandos dos testes novos do P1 |
| [server/scripts/switch_project.sh](server/scripts/switch_project.sh) | down/up do P2 via scripts v2 |
| `server/oai-cn-gnb-e2/scripts/` | +`test_ng_setup.sh`, `test_registration.sh`, `test_config_coherence.sh` (P1 ficam em `server/scripts/`) |
| [server/scripts/](server/scripts/) | novos testes P1 (NG setup, registro, coerência) |
| [server/panel/static/index.html](server/panel/static/index.html) | layout (topo cards + rail por projeto); JS `projButtons` + troca de ferramentas por `_activeProj` + guarda de dependência |
| `server/panel/static/topology.html` (+ json P2) | topologia por projeto |
| `server/panel/VERSION` + `CHANGELOG.md` | bump 0.14.0 |

---

## 8. Fases de execução (incremental, deploy a cada fase)

1. **Fase 1 — Ativação (fundação):** remap COMMANDS v2 + `switch_project.sh`.
   Deploy `panel` + `sync` e **validar no servidor** (ligar/desligar P2 de fato
   sobe/derruba os containers v2; switch P1↔P2 respeita exclusividade).
2. **Fase 2 — Layout:** topo com cards + servers; rail de ferramentas por
   projeto; guarda de dependência (RAN só com Core).
3. **Fase 3 — Testes novos:** scripts P1 (NG setup, registro, coerência) +
   variante KPM_TRAFFIC no P2; entradas na lateral por projeto.
4. **Fase 4 — Topologia do P2.**

---

## 9. Riscos / validação

- **`sync` envia scripts do P2** — usa o `cmd_sync` normal (seguro), **não**
  `sync-oai` (perigoso, sobrescreve build). Confirmar que os scripts novos do
  P2 entram no rsync de `oai-cn-gnb-e2/scripts/` sem arrastar artefatos.
- Cada fase termina por **estado/evento** (sem sleep cego), conforme regra do projeto.
- Testar guest (read-only) continua bloqueando ações.
