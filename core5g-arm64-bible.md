# Core5G ARM64 — Bíblia do Projeto

Documento de referência único e completo. Se você (ou alguém do grupo) chegar
aqui sem contexto nenhum, este arquivo deve bastar pra entender o quê, o
porquê e o como de tudo que existe neste repositório e no servidor.

Para o histórico cronológico passo a passo (o "diário de bordo"), veja
[`CHANGELOG.md`](CHANGELOG.md). Este documento aqui é a fotografia
consolidada do estado atual + explicações conceituais.

---

## 1. Contexto da disciplina

- **Disciplina 7: RAN Intelligent Controller (RIC)** — especialização CESAR School.
- **Professor:** Dr. Jonas Augusto Kunzler (`jak@cesar.school`).
- **Grupo (Grupo 6):** Henrique, Klinger, Kelvin, Gilberto.
- **Tema sorteado (NGO §6.1):** **UE-TP-rApp** — previsão de throughput por UE
  (RSSI, RSRP, CQI, PRB, histórico).

### Dois projetos avaliativos (40% cada)

| Projeto | O quê | Onde está | Status |
|---|---|---|---|
| **Projeto 1** | Open5GS containerizado + UERANSIM (Core 5G + RAN simulada) | `server/` (raiz deste repo) | ✅ Apresentado 13/06/2026 (Aula 03). Validado fim a fim no servidor. |
| **Projeto 2** | `oai-cn-gnb-e2` — OAI 5GC + gNB com agente E2 + FlexRIC (near-RT RIC) + xApps | `server/oai-cn-gnb-e2/` | ⏳ Pendente. Apresentação 20/06/2026 (Aula 06, 08:00–11:00, 20 min/grupo, mesma ordem do Projeto 1). |

Entregáveis do Projeto 2 (conforme slide "Projeto 2 (40%) — roteiro e
prazos" do `pdfs/aula04-xapps_opensource.pdf`):
- Implementar `oai-cn-gnb` conforme `server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md`.
- Relatório técnico + demo (vídeo/logs).
- Extensão opcional: xApp customizado ou caso A1/políticas.
- **Atenção:** a rubrica oficial (`docs/avaliacao_seminario_aula06.md`) e o
  plano de testes (`docs/labs/04-projeto2-plano-testes.md`) citados nos
  slides **não estavam publicados** no repositório de origem
  (`jakunzler/cesar-school-repo`) no momento em que checamos — confirmar com
  o professor antes da entrega.

---

## 2. Como tudo isso funciona, explicado para quem não é técnico

Pensa na rede 5G como uma **empresa de entregas** (tipo Correios), só que em
vez de cartas ela entrega **internet** até o seu celular. Cada container
Docker abaixo é um "departamento" dessa empresa, rodando isolado dos outros.

### O caminho que o celular percorre (Projeto 1 — Open5GS)

| Quem | Container Docker | O que faz, em uma frase |
|---|---|---|
| 📡 Antena | `nr-gnb` (UERANSIM) | A torre de celular (simulada) — é por onde o celular fala com a rede. |
| 📱 Celular | `nr-ue` (UERANSIM) | O celular (simulado) que liga, se registra e pede pra usar internet. |
| 🛎️ Porteiro/recepção | `amf` | Primeiro contato: recebe o celular, confere quem ele é e direciona pro setor certo. |
| 🔐 Segurança | `ausf` | Confere a "senha" do celular — só deixa passar quem é de fato o dono do chip. |
| 🗂️ Cadastro do cliente | `udm` | Guarda o perfil de cada cliente: qual plano tem, o que pode acessar. |
| 🗄️ Banco de dados | `udr` + `mongodb` | O arquivo/banco onde os dados de cadastro ficam gravados de fato. |
| 🚦 Fiscal de regras | `pcf` | Decide as regras de cada conexão: velocidade, prioridade, política de uso. |
| 📋 Quadro de avisos | `bsf` | Anota qual fiscal (`pcf`) está cuidando de qual conexão, pra outros setores acharem depois. |
| 🧭 Triagem de pista | `nssf` | Escolhe em qual "pista"/fila (*slice*) aquele celular deve andar. |
| 🗺️ Gerente de logística | `smf` | Organiza a "rota de entrega": monta a sessão de dados que o celular vai usar. |
| 🚚 Caminhão de entrega | `upf-a` / `upf-b` | Carrega de fato os dados (a internet) de um lado pro outro. Dois caminhões, um de reserva. |
| 🌐 Destino final (teste) | `dn` | Um "mundo exterior" fake só pra simular a internet real durante os testes. |
| ☎️ Catálogo telefônico interno | `nrf` | Todo departamento se cadastra aqui — é assim que um setor acha o telefone do outro. |
| 📞 Telefonista interna | `scp` | Repassa as ligações entre os departamentos (em vez de cada um ligar direto pro outro). |
| 🖥️ Balcão de atendimento | `webui` | Tela web onde a gente cadastra um novo "cliente" (assinante) no sistema. |

**Ordem real de quando um celular liga e pede internet:**
1. Celular (`nr-ue`) avista a antena (`nr-gnb`) e manda um sinal.
2. `amf` recebe, confere quem é com a ajuda de `ausf` (senha) e `udm` (cadastro).
3. `pcf` decide as regras dessa conexão e avisa o quadro (`bsf`).
4. `nssf` escolhe a pista certa, `smf` monta a rota de dados.
5. `upf-a`/`upf-b` (o caminhão) começa a carregar dados de verdade entre o
   celular e o "mundo exterior" (`dn`, ou a internet real quando é o caso).

Tudo isso é **3GPP padrão** — Open5GS (Projeto 1) e OAI (Projeto 2) são duas
"marcas" diferentes de empresa de entregas, mas com os mesmos departamentos.

### O painel de controle (não faz parte da rede 5G, é só pra gente operar)

| Container/processo | Função, em uma frase |
|---|---|
| 🚪 Porteiro do painel | `caddy` — confere usuário e senha na entrada do site e só libera quem tem crachá (login), além de deixar a conexão criptografada (HTTPS). |
| 🖱️ Escritório dos botões | `server/panel/server.py` (FastAPI/Uvicorn) — é quem de fato aperta o botão de ligar/desligar a rede quando você clica na tela. |

> Resumo: o painel é só um controle remoto pra ligar/desligar/checar a
> "empresa de entregas" acima — ele não faz parte da rede 5G em si.

---

## 2.a Para o técnico de telecom (quem já mexeu com rádio)

Você conhece antena, cobertura, frequência, talvez já configurou BTS ou eNodeB
no campo. Essa seção fala a sua língua — sem analogia de empresa de entregas,
sem código, sem protocolo no nível de bytes.

### O que está rodando aqui, em termos de rádio

Este projeto simula uma célula 5G completa dentro de um servidor ARM na nuvem.
Não tem antena física, não tem RF de verdade — mas **toda a lógica de
sinalização, autenticação e transporte de dados é real**, executando os mesmos
protocolos que uma rede operadora usa.

**Parâmetros de rádio do Projeto 1 (UERANSIM):**

| Parâmetro | Valor |
|---|---|
| Banda | n78 (3,3–3,8 GHz) — faixa principal do 5G SA no Brasil |
| Modo | TDD (Time Division Duplex) — DL e UL na mesma frequência, separados por tempo |
| Largura de banda | 100 MHz |
| Numerologia (SCS) | 30 kHz (µ=1) |
| PRBs ativos | 66 (de 132 totais para 100 MHz / 30 kHz) |
| RSRP típico simulado | −79 dBm @ 100 m · −100 dBm @ 500 m · −111 dBm @ 1 km |
| Modelo de propagação | 3GPP TR 38.901 UMa NLOS |
| Peak teórico DL | ~665 Mbps (64-QAM, 4 camadas MIMO) |
| Peak teórico UL | ~250 Mbps |

> O UERANSIM simula o rádio via software: a interface `uesimtun0` é o
> equivalente lógico do túnel entre a antena e o UE. Não há IQ sample,
> não há FPGA — mas NAS, RRC, PDCP e GTP-U são todos executados de verdade.

### Os containers — o que cada um é, em termos que você conhece

Se você trabalhou com 4G/LTE, vai reconhecer a maioria. O 5G SA renomeou e
reorganizou as peças, mas a função é a mesma.

| Container | Equivalente 4G / LTE | O que faz |
|---|---|---|
| `nr-gnb` (UERANSIM) | eNodeB (eNB) | A estação-rádio-base (simulada). Trata RRC, scheduler de PRB, GTP-U com o core. |
| `nr-ue` (UERANSIM) | UE / celular | O aparelho (simulado). Faz attach, PDU session, "mede" RSRP/RSRQ, roda iperf3. |
| `amf` | MME | Controle de acesso, autenticação, registro e mobilidade do UE. |
| `smf` | SGW-C + PGW-C | Controla o plano de dados: define a rota do pacote, instrui o UPF via PFCP. |
| `upf-a` / `upf-b` | SGW-U + PGW-U | Plano de usuário. Recebe GTP-U do gNB (N3) e encaminha para a internet (N6). |
| `ausf` | HSS (parte auth) | Executa o 5G-AKA — gera o vetor de autenticação a partir do Ki e do OPc do SIM. |
| `udm` | HSS (parte dados) | Perfil do assinante: IMSI, plano, slice (S-NSSAI), MSISDN. |
| `udr` + `mongodb` | HSS (storage) | Banco de dados de assinante. O UDM lê aqui. |
| `pcf` | PCRF | Política de QoS: define QFI, 5QI, regras de throttling por sessão. |
| `bsf` | (novo no 5G SA) | Registra qual PCF está gerenciando qual sessão — evita conflito quando o AMF precisa localizar o PCF de um UE ativo. |
| `nssf` | (novo no 5G SA) | Network Slice Selection — decide em qual fatia de rede (URLLC, eMBB, mMTC) o UE entra. |
| `nrf` | (novo no 5G SA) | Registro de NFs: cada função se cadastra aqui; outras consultam pra saber o endereço de quem precisam chamar. |
| `scp` | (novo no 5G SA) | Proxy de sinalização SBI — centraliza as chamadas HTTP/2 entre NFs. |
| `dn` | PDN-GW / internet | Rede de dados de destino. Aqui roda o servidor iperf3 que mede throughput real pelo túnel do UE. |

### Como a simulação de canal funciona (tc netem)

O painel tem um modo "Condições do Canal" onde você escolhe distância e
interferência. Não há rádio real — o painel injeta parâmetros de
**Network Emulator (netem)** na interface `uesimtun0` via `tc qdisc`:

```
tc qdisc replace dev uesimtun0 root netem delay <D>ms loss <L>%
```

Os valores são derivados do modelo 3GPP TR 38.901 UMa NLOS (path loss) e do
SINR para cada nível de interferência:

| Condição | RSRP aprox. | Delay total | Perda total | Equivalente de campo |
|---|---|---|---|---|
| 100 m, sem interferência | −79 dBm | 1 ms | 0% | UE próximo à torre, boa visada |
| 500 m, interferência fraca | −100 dBm | 13 ms | ~3% | Cobertura boa, co-canal leve (SINR ≈ 20 dB) |
| 1 km, interferência média | −111 dBm | 40 ms | ~12% | Borda de célula (SINR ≈ 15 dB) |
| 3 km, interferência alta | −127 dBm | 100 ms | ~32% | UE na sombra, handover iminente (SINR ≈ 10 dB) |

### Diferenças entre Projeto 1 (UERANSIM) e Projeto 2 (OAI + FlexRIC)

| Aspecto | Projeto 1 — UERANSIM | Projeto 2 — OAI nr-softmodem |
|---|---|---|
| Camada de rádio | Simulada (NAS/RRC/GTP-U via socket, sem PHY real) | RFSIM: PHY real em software, sem hardware RF |
| Scheduler de PRBs | Implementado no UERANSIM (fixo) | Scheduler real do OAI (round-robin / proportional fair) |
| Interface com RIC | Nenhuma — gNB monolítico, sem agente E2 | Agente E2 real; conecta ao FlexRIC e exporta KPIs por UE |
| Métricas de rádio acessíveis | Só logs internos | DRB.UEThpDl/Ul, RRU.PrbTotDl/Ul, SINR via E2SM-KPM |
| Analogia de campo | Drive test: você tem só logs de NAS | OMC da BTS: KPIs por UE em tempo real, controlável via xApp |

> Projeto 1 é suficiente para validar core + attach. Projeto 2 é o que um
> integrador de RIC precisaria para comissionar xApps de otimização de PRB,
> handover ou QoS por UE.

---

## 2.b Para o engenheiro de redes (visão O-RAN / 3GPP)

Se você conhece telecomunicações mas não o ambiente Docker/Linux deste projeto,
esta seção mapeia cada peça ao seu papel na arquitetura O-RAN e no 3GPP 5G SA.

### O que é O-RAN e onde este projeto se encaixa

O-RAN (Open Radio Access Network) define uma arquitetura desagregada da RAN com
interfaces abertas. A divisão funcional adotada pela O-RAN Alliance é o
**Split 7.2x** (entre PHY-Low e PHY-High), que separa o nó de acesso em:

```
┌──────────────────────────────────────────────────────────────┐
│ SMO (Service Management & Orchestration)                     │
│  · Non-RT RIC: rApps, políticas A1, gerência O1              │
│  · Horizonte de controle: > 1 s                              │
└───────────────────────────┬──────────────────────────────────┘
                            │ A1 (políticas) / O1 (FCAPS)
┌───────────────────────────▼──────────────────────────────────┐
│ Near-RT RIC (near-Real-Time RIC)                             │
│  · xApps: E2SM-KPM (métricas), E2SM-RC (controle)            │
│  · Horizonte de controle: 10 ms – 1 s                        │
│  · Implementação deste projeto: FlexRIC (Projeto 2)          │
└───────────────────────────┬──────────────────────────────────┘
                            │ E2 (E2AP / E2SM)
┌───────────────────────────▼──────────────────────────────────┐
│ O-gNB (agente E2 embutido)                                   │
│  ┌─────────────┐  ┌─────────────┐   ┌──────────────────────┐ │
│  │  O-CU-CP    │  │  O-CU-UP    │   │       O-DU           │ │
│  │ RRC / PDCP-C│  │  PDCP-U     │   │  RLC / MAC / PHY-Hi  │ │
│  └──────┬──────┘  └────── ┬─────┘   └──────────┬───────────┘ │
│         │ F1-C            │ F1-U               │             │
│         └────────────────-┘                    │ Open FH     │
└─────────────────────────────────────────────── │ (7.2x) ─────┘
                                                 │
                                        ┌─────────▼────────┐
                                        │      O-RU        │
                                        │  PHY-Low / RF    │
                                        └──────────────────┘
```

**Interfaces padronizadas relevantes:**

| Interface | Entre | Protocolo |
|---|---|---|
| E2 | Near-RT RIC ↔ O-gNB | E2AP sobre SCTP; E2SM-KPM/RC |
| A1 | Non-RT RIC ↔ Near-RT RIC | REST/JSON; políticas de ML/QoS |
| O1 | SMO ↔ todos os nós gerenciados | NETCONF/YANG |
| F1-C/U | O-CU ↔ O-DU | NG-AP + GTP-U (3GPP TS 38.473) |
| Open FH | O-DU ↔ O-RU | eCPRI sobre Ethernet (Split 7.2x) |
| N2 | O-CU-CP ↔ AMF | NGAP sobre SCTP |
| N3 | O-CU-UP ↔ UPF | GTP-U sobre UDP |
| N4 | SMF ↔ UPF | PFCP sobre UDP |

### Como Projeto 1 (Open5GS + UERANSIM) se encaixa

UERANSIM implementa um **gNB monolítico** (sem Split 7.2 — CU, DU e RU são um
processo único) e um **UE** que fala NAS sobre o stack simulado. É a referência
mais simples do 3GPP 5G SA sem Near-RT RIC.

```
UERANSIM nr-gnb  ──N2 (NGAP)──►  AMF   ─ CP 5GC
                 ──N3 (GTP-U)──►  UPF-A ─ UP 5GC (N6 → dn → internet)
UERANSIM nr-ue   ──NAS / RRC──►  (interno ao nr-gnb)
                                   └─► uesimtun0 (TUN 10.60.0.x)
```

Não há agente E2 nem Near-RT RIC no Projeto 1. Os testes de throughput e
canal simulado via `tc netem` em `uesimtun0` são o equivalente prático do que
seria medido via E2SM-KPM `DRB.UEThpDl/Ul` em um ambiente com RIC real.

### Como Projeto 2 (OAI + FlexRIC) adiciona o Near-RT RIC

OAI `nr-softmodem` em modo RFSIM implementa a stack de RAN completa (PHY/MAC/
RLC/PDCP/RRC) **com agente E2 embutido** (biblioteca `openair2/E2AP/`). O
Split 7.2 é suportado via F1/eCPRI, mas no ambiente deste projeto roda em
modo monolítico com RFSIM (rádio 100% em software, sem hardware SDR).

```
OAI nr-softmodem (RFSIM)
  ├── CU-CP: RRC, PDCP-C
  ├── CU-UP: PDCP-U
  ├── DU:    RLC, MAC, PHY-Hi (simulado)
  ├── RU:    PHY-Low (RFSIM — sem hardware)
  └── E2 Agent ──E2AP──► FlexRIC (Near-RT RIC)
                              ├── xApp KPM: subscreve DRB.UEThpDl/Ul
                              └── xApp RC:  controla parâmetros RRC
```

**KPMs relevantes para o tema UE-TP-rApp (E2SM-KPM):**

| KPM | Descrição | Granularidade |
|---|---|---|
| `DRB.UEThpDl` | Throughput DL por DRB por UE (kbps) | por UE |
| `DRB.UEThpUl` | Throughput UL por DRB por UE (kbps) | por UE |
| `RRU.PrbTotDl` | PRBs utilizados no DL (%) | por célula |
| `RRU.PrbTotUl` | PRBs utilizados no UL (%) | por célula |
| `L1M.RS-SINR` | SINR medido na camada física | por UE |

### Onde cada container Docker está no modelo O-RAN

| Container | Camada O-RAN | Interface exposta |
|---|---|---|
| `nr-gnb` / `nr-ue` (UERANSIM) | O-gNB monolítico (sem E2) + UE | N2, N3, NAS |
| OAI `nr-softmodem` (Proj.2) | O-gNB com agente E2 | N2, N3, E2 |
| `flexric` (Proj.2) | Near-RT RIC | E2, A1 |
| `amf` | 5GC CP — N2 termination | N2 (NGAP), N11 |
| `smf` | 5GC CP — session management | N4 (PFCP), N11 |
| `upf-a/b` | 5GC UP — user plane | N3 (GTP-U), N6 |
| `ausf` | 5GC CP — 5G-AKA auth | Nausf (SBI) |
| `udm` | 5GC CP — subscriber data | Nudm (SBI) |
| `udr` | 5GC CP — data repository | Nudr (SBI) |
| `pcf` | 5GC CP — policy (AM/SM) | Npcf (SBI) |
| `nrf` | 5GC CP — NF discovery | Nnrf (SBI) |
| `bsf` | 5GC CP — binding support | Nbsf (SBI) |
| `nssf` | 5GC CP — slice selection | Nnssf (SBI) |
| `scp` | 5GC CP — SBI proxy | SBI indireto |
| `mongodb` | Storage backend | — (Nudr internal) |

### Fluxo NAS/RRC de registro (do ponto de vista do protocolo)

```
UE                  gNB              AMF          AUSF    UDM    SMF    UPF
 │───Registration Req──►│──NGAP Init UE──►│               │      │      │
 │                      │◄──Auth Req──────│──Auth Req────►│      │      │
 │                      │                 │◄──Auth Ans────│      │      │
 │◄──Auth Req───────────│◄──Auth Req──────│               │      │      │
 │──Auth Resp──────────►│──Auth Resp─────►│               │      │      │
 │                      │                 │──Get Sub Data───────►│      │
 │◄──Security Mode Cmd──│◄────────────────│               │      │      │
 │──Security Mode Cmp──►│────────────────►│               │      │      │
 │◄──Reg Accept─────────│◄────────────────│               │      │      │
 │──PDU Session Req─────►│────────────────►│──────────────────────►SMF  │
 │                      │                 │                      │──N4──►UPF
 │◄─PDU Session Accept──│◄────────────────│◄─────────────────────│      │
 │ (uesimtun0 UP)       │                 │                      │      │
 │═════════GTP-U sobre N3══════════════════════════════════════════►│ N6►internet
```

---

## 3. Estrutura do repositório

```
/
├── .env / .env.example        # credenciais de DEPLOY (host, SSH key, DuckDNS) — NUNCA vão pro servidor
├── deploy.sh                  # entrypoint único de deploy
├── core5g-arm64-bible.md      # este arquivo
├── CHANGELOG.md                # histórico cronológico de tudo que foi feito
├── infra/
│   ├── server-bootstrap.sh    # bootstrap idempotente do servidor (Docker, swap, DuckDNS, Caddy, painel)
│   └── core5g-panel.service   # unit systemd do painel server-side (template)
├── docs/
│   ├── labs/                  # guias de aula originais do curso (00–03, INDICE, video_seq_report)
│   └── blueprint-painel-observabilidade.md  # desenho do painel explicativo (não implementado)
├── pdfs/                      # slides das aulas (01–04) + planilha de grupos
├── ssl/
│   └── core5g_openran_arm64.pem   # chave SSH privada do servidor
├── client/                    # painel de controle web LOCAL (não roda no servidor)
│   ├── server.py              # backend FastAPI — só chama deploy.sh e streama saída
│   ├── static/index.html      # UI (HTML/CSS/JS puro, sem build step)
│   └── run.sh                 # cria venv, instala deps, sobe em :8765
└── server/                    # TUDO que é replicado/roda na máquina AWS
    ├── docker-compose.yml     # Projeto 1 (Open5GS) — name: open5gs-containerized fixo
    ├── .env / .env.example    # variáveis de IMAGEM do compose (sem segredos)
    ├── configs/open5gs/       # YAML de cada NF (amf.yaml, smf.yaml, bsf.yaml, ...)
    ├── scripts/                # up_core.sh, up_ran.sh, down.sh, healthcheck.sh, add-subscriber.sh, ...
    ├── overrides/
    ├── ueransim/               # docker-compose.yaml separado (gNB+UE simulados)
    ├── logs/                   # bind mounts de log por NF (gerado em runtime)
    ├── panel/                  # painel de controle web SERVER-SIDE (roda na própria AWS)
    │   ├── server.py           # backend FastAPI — chama scripts locais, sem SSH
    │   ├── static/index.html   # UI (igual ao client/, sem sync/sync-oai/bootstrap)
    │   ├── requirements.txt
    │   └── .venv/              # criado pelo bootstrap, não versionado
    └── oai-cn-gnb-e2/          # Projeto 2 — OAI 5GC + gNB + FlexRIC + xApps
```

### Por que essa separação

- **Raiz** = ferramentas de orquestração local (nunca rodam no servidor).
- **`server/`** = espelho exato do que existe e roda na instância AWS.
- **`docs/`** = documentação pura, sem nenhum arquivo executável/config.
- O `.env` foi deliberadamente **dividido em dois**: o da raiz tem
  `AWS_SERVER_HOST`/`AWS_SERVER_USER`/`AWS_SSH_KEY_PATH`/`DUCKDNS_DOMAIN`/`DUCKDNS_TOKEN`
  (só pro `deploy.sh` usar localmente); o de `server/.env` tem só
  `OPEN5GS_IMAGE`/`WEBUI_IMAGE`/`MONGODB_IMAGE`/`UERANSIM_IMAGE`/`DN_IMAGE`
  (o que o `docker-compose.yml` precisa *no servidor*). Assim nenhum segredo
  de acesso é enviado pro servidor via `rsync`.

---

## 4. O servidor (AWS EC2 ARM)

| Item | Valor |
|---|---|
| Hostname | `core5g-arm64.duckdns.org` (DDNS — IP público é dinâmico) |
| IP original (histórico) | `3.145.40.200` — **nunca hardcodar**, sempre usar o hostname |
| Usuário | `ubuntu` |
| Chave SSH | `ssl/core5g_openran_arm64.pem` |
| SO | Ubuntu 24.04.4 LTS, kernel 6.17, `aarch64` |
| CPU | 2 vCPUs |
| RAM | 906 MiB (instância pequena, provável `t4g.micro`) |
| Swap | 8 GiB em `/swapfile`, `vm.swappiness=10`, persistente via `/etc/fstab` |
| Disco | ~29 GB total |

### Acesso manual (só pra debug — preferir `./deploy.sh ssh`)

```bash
ssh -i ssl/core5g_openran_arm64.pem ubuntu@core5g-arm64.duckdns.org
```

### DuckDNS (IP dinâmico)

- Domínio: `core5g-arm64.duckdns.org`.
- Token: armazenado em `.env` (`DUCKDNS_TOKEN`) — não duplicado aqui.
- Script `~/duckdns/duck.sh` no servidor + cron `*/5 * * * *` mantendo o
  registro atualizado. Reinstalável/idempotente via
  `./deploy.sh bootstrap`.

### Docker

Instalado via **repositório oficial Docker** (não o pacote `docker.io` do
Ubuntu): `docker-ce`, `docker-ce-cli`, `containerd.io`,
`docker-buildx-plugin`, `docker-compose-plugin`. Usuário `ubuntu` no grupo
`docker`. Tudo encapsulado em `infra/server-bootstrap.sh`, idempotente.

---

## 5. O fluxo de trabalho: tudo local, deploy via `deploy.sh`

**Regra de ouro:** nunca editar nada direto no servidor via SSH manual. O
fluxo é sempre: editar arquivos em `server/` (ou `infra/`) localmente →
`./deploy.sh <comando>`.

```bash
./deploy.sh bootstrap          # instala Docker + swap + DuckDNS no servidor (idempotente)
./deploy.sh sync               # envia server/{docker-compose.yml,.env,configs,scripts,overrides,ueransim}
./deploy.sh sync-oai           # envia server/oai-cn-gnb-e2/ (~230MB, só quando precisar)
./deploy.sh up core             # sync + sobe só o core Open5GS
./deploy.sh up ran              # sync + sobe o RAN (UERANSIM)
./deploy.sh up all              # sync + sobe core + RAN
./deploy.sh down [core|ran|all]
./deploy.sh status              # docker compose ps + healthcheck.sh no servidor
./deploy.sh panel               # envia server/panel/ + roda bootstrap (Caddy + venv + systemd)
./deploy.sh ssh                 # sessão interativa (só debug)
```

`deploy.sh` lê `AWS_SERVER_HOST`/`AWS_SERVER_USER`/`AWS_SSH_KEY_PATH` do
`.env` da raiz — por isso nunca tem IP/hostname hardcoded dentro do script.

### Painel visual (`client/`)

Pra quem prefere clicar em botão em vez de terminal: um painel web que roda
**na sua estação local** (não no servidor) com um botão por comando do
`deploy.sh` e console com saída em tempo real.

```bash
cd client && ./run.sh        # cria venv, instala deps, sobe em http://127.0.0.1:8765
```

- Backend (`client/server.py`, FastAPI) só faz `subprocess.Popen` do
  `deploy.sh` e streama stdout/stderr pro navegador — nenhuma lógica de
  SSH/rsync duplicada, `deploy.sh` continua a única fonte de verdade.
- Comandos expostos são uma lista fixa (`bootstrap`, `sync`, `sync-oai`,
  `up`/`down core|ran|all`, `status`) — o backend não aceita string livre
  vinda do navegador.
- Bind só em `127.0.0.1`, sem autenticação — assume uso local de
  desenvolvimento, não exposição em rede.
- É o primeiro degrau do painel maior descrito em
  `docs/blueprint-painel-observabilidade.md` (que prevê logs filtráveis e
  visualização de fluxo de protocolo em tempo real) — esta versão ainda só
  dispara comandos e mostra a saída crua, sem parsing/filtros.

### Painel web no servidor (`server/panel/`), com HTTPS + login

Versão do painel acessível de qualquer lugar (não só da sua estação),
publicada em `https://core5g-arm64.duckdns.org/` com usuário/senha.

- Roda **direto na instância AWS** — `server/panel/server.py` (FastAPI)
  chama os scripts locais (`./scripts/up.sh`, `up_ran.sh`, `down_core.sh`,
  `down_ran.sh`, `healthcheck.sh`) sem nenhum SSH envolvido. Bind só em
  `127.0.0.1:8765` — nunca exposto direto na internet.
- **HTTPS automático via Caddy**: `infra/server-bootstrap.sh` instala o
  Caddy (repositório oficial Cloudsmith) e gera `/etc/caddy/Caddyfile` na
  frente do painel. Caddy obtém/renova sozinho um certificado **Let's
  Encrypt gratuito** para `core5g-arm64.duckdns.org` — não há certificado
  manual para instalar. Único requisito externo: as portas **80** (desafio
  ACME HTTP-01) e **443** (HTTPS) precisam estar abertas no Security Group
  da instância — **já aberto e validado** (HTTP 308 → HTTPS, HTTPS 401 sem
  credencial, 200 com login, 403 pro guest em `/api/run/*`).
- **Login com dois papéis**, via `basic_auth` do próprio Caddy (hash bcrypt
  gerado com `caddy hash-password`, nunca senha em texto puro no servidor):
  - **admin** (`PANEL_USER`/`PANEL_PASSWORD` no `.env` da raiz): acesso
    total, executa qualquer comando.
  - **guest** (`PANEL_GUEST_USER`/`PANEL_GUEST_PASSWORD`): só visualiza —
    `server.py` recusa com HTTP 403 qualquer `POST /api/run/*` vindo desse
    usuário (checagem no backend, não só botão escondido no front-end). O
    Caddy injeta `header_up X-Remote-User {http.auth.user.id}` pro FastAPI
    saber quem autenticou.
- **Processo persistente**: `infra/core5g-panel.service` (systemd,
  `Restart=always`, roda o `uvicorn` do venv em `server/panel/.venv`).
  Instalado/atualizado pelo bootstrap.
- **Deploy**: `./deploy.sh panel` sincroniza `server/panel/` e roda o
  bootstrap (idempotente) — único caminho pra atualizar o painel ou as
  credenciais (nunca editar nada via SSH manual no servidor, mesma regra
  de ouro do §5).
- **Telemetria em tempo real** (`GET /api/telemetry`): stream infinito
  (NDJSON, uma linha de JSON a cada 2s) com RAM/swap/disco/load do host
  (lidos de `/proc/meminfo` + `shutil.disk_usage` + `os.getloadavg()`,
  sem dependência nova) e CPU%/RAM por container (`docker stats
  --no-stream --format '{{json .}}'`). Renderizado na UI como barrinhas +
  tabela colapsável, sem Prometheus/Grafana — a instância tem só 906 MiB
  de RAM, não cabe uma stack de observabilidade pesada do lado dela.
- **Filtro de logs por serviço** (`GET /api/logs/{service}`): lista de
  serviços descoberta em runtime via `docker compose config --services`
  (nos dois compose files — core e `ueransim/`), depois `docker compose
  logs -f --tail 200 <service>` streamado pro console da UI.
- **Telemetria e logs são liberados pro guest** (são leitura, não
  execução) — só `POST /api/run/*` é que devolve 403 pra esse usuário.

---

## 6. Open5GS (Projeto 1) — o que cada serviço faz

Todos os NFs (Network Functions) abaixo são papéis padronizados pelo 3GPP.
Open5GS e OAI implementam os mesmos papéis, só com binários diferentes.

| Serviço | Interface principal | Papel |
|---|---|---|
| `nrf` | SBI interno | "DNS" do core — todo NF se registra aqui para os outros acharem |
| `scp` | SBI interno | proxy interno entre NFs (Service Communication Proxy) |
| `amf` | N1 (NAS) / N2 (NGAP) | porta de entrada da RAN — autentica e move o UE |
| `smf` | N4 (PFCP) / N11 | gerencia sessões PDU (os "túneis" de dados) |
| `upf-a` / `upf-b` | N3 (GTP-U) / N6 | plano de dados de fato — failover/load balancing entre as duas |
| `ausf` | SBI interno | executa a autenticação 5G-AKA |
| `udm` | SBI interno | perfil do assinante (slice, chaves de segurança) |
| `udr` | SBI interno | banco por trás do UDM/PCF (backend MongoDB) |
| `pcf` | SBI interno (Npcf) | decide regras de QoS/política de sessão |
| `bsf` | SBI interno (Nbsf) | registra o *binding* PCF↔sessão pra descoberta por outros NFs (ex.: NEF/AF). **Item que faltava no projeto original — ver §8.** |
| `nssf` | SBI interno | escolhe o slice (S-NSSAI) certo pro UE |
| `webui` | HTTP :9999 | painel admin do Open5GS pra cadastrar assinantes |
| `mongodb` | — | banco de dados (subscribers, etc.) |
| `dn` | N6 | "internet" falsa (alpine) só pra UPF ter pra onde rotear/NAT |

**Detalhe pedagógico importante:** cada rede docker no `docker-compose.yml`
(`net-n2`, `net-n3`, `net-n4`, `net-n6`, `net-sbi`) corresponde 1:1 a uma
interface 3GPP real — filtrar por rede = filtrar por interface.

### RAN simulada (UERANSIM, em `server/ueransim/`)

- `nr-gnb`: simula a estação base — fala N2/N3 com o core.
- `nr-ue`: simula o celular — registro NAS, abre sessão PDU, expõe a
  interface `uesimtun0` pra testar conectividade fim a fim.

---

## 7. OAI + FlexRIC (Projeto 2) — o que cada peça faz

Em `server/oai-cn-gnb-e2/`:

- **OAI 5GC** (`oai-cn5g-fed/`): mesmos papéis de NF do Open5GS, mas
  empacotados pela OpenAirInterface, com UPF em **VPP** (dataplane mais
  rápido) em vez do UPF simples.
- **gNB OAI** (`nr-softmodem`, modo **RFSIM** — rádio 100% software): PHY/MAC/
  RLC/PDCP/RRC reais (não simulados como no UERANSIM), com um **agente E2
  embutido** que anuncia "RAN functions" (KPM = métricas, RC = controle, +
  SMs custom L2/L3) pro near-RT RIC.
- **FlexRIC** (near-RT RIC): recebe o E2 SETUP do gNB, registra as RAN
  functions disponíveis, roteia SUBSCRIPTION/INDICATION/CONTROL entre o gNB
  e as xApps.
- **xApps** (`xapp_kpm_moni`, `xapp_kpm_rc`): aplicações que de fato
  consomem métricas (KPM) ou eventos RRC (RC) via E2 — o "lado inteligente"
  do RIC.

Fluxo de subida documentado em
`server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md`: Core → RIC → gNB → xApp.

---

## 8. Bugs reais encontrados e corrigidos

Estes problemas existiam no material original do curso e foram descobertos
testando de verdade no servidor ARM — guardados aqui pra não se perderem.

### 8.1 — Imagens `gradiant/open5gs` sem build arm64

`gradiant/open5gs:2.7.6` e `gradiant/open5gs-webui:2.7.6` **não têm**
manifest `linux/arm64/v8` — a partir da tag `2.7.3` a gradiant só publica
`amd64`. `docker compose up` falhava com
`no matching manifest for linux/arm64/v8`.

**Correção:** fixar em `server/.env`:
```
OPEN5GS_IMAGE=gradiant/open5gs:2.7.2
WEBUI_IMAGE=gradiant/open5gs-webui:2.7.2
```
(`2.7.0`, `2.7.1` e `2.7.2` são as últimas tags com build arm64 confirmado
via Docker Hub API. `mongo:7.0` e `gradiant/ueransim:3.2.6` já eram
arm64-ok, sem mudança necessária.)

### 8.2 — Serviço BSF ausente (PDU Session sempre rejeitada)

Depois do core subir 100% healthy, o UE registrava (NAS OK) mas a sessão PDU
sempre falhava com `PDU Session Establishment Reject [OUT_OF_LADN_SERVICE_AREA]`.

Causa raiz (achada no log do PCF, não no do UE): `No http.location` em
`nbsf-handler.c:436` — o PCF tenta registrar o *binding* da sessão na
**BSF** via NRF, mas:
1. **Não havia serviço `bsf` no `docker-compose.yml`** (apesar do binário
   `open5gs-bsfd` existir na imagem).
2. Já existia um `configs/open5gs/bsf.yaml` no projeto original, mas com o
   endereço de **exemplo padrão** (`127.0.0.15`), fora do esquema de rede
   real do projeto (`10.10.0.x` na `net-sbi`).

Ou seja: item esquecido na configuração original do curso, não causado pela
troca de versão de imagem (§8.1).

**Correção:**
- `server/configs/open5gs/bsf.yaml`: endereço corrigido para `10.10.0.18`
  (próximo IP livre), client `scp` apontado para `10.10.0.200:7777`.
- `server/docker-compose.yml`: novo serviço `bsf` adicionado (mesmo padrão
  do `nssf`), container `open5gs-bsf-containerized`.

Depois de subir o BSF, ainda apareceu um segundo erro transitório
(`Registration reject [95]` / `amf_npcf_am_policy_control_handle_create()
failed`) — estado órfão de tentativas de sessão anteriores. Resolvido com
restart limpo de `amf`, `smf`, `pcf`, `bsf` (e os outros NFs do core).

### 8.3 — Nome do projeto Compose não fixado (risco de perder dados ao mover pastas)

`docker-compose.yml` não tinha um `name:` explícito no topo. As **redes**
(`net-n2`, `net-n3` etc.) já tinham `name:` fixo individualmente, mas os
**volumes nomeados** do Mongo (`mongodb-data`, `mongodb-config`) não — o
nome deles é derivado do nome do diretório onde o `docker compose` é
executado. Ao reorganizar o repo (mover de `open5gs-containerized/` pra
`server/`), isso teria recriado os volumes do zero, **perdendo o subscriber
cadastrado**.

**Correção:** adicionado `name: open5gs-containerized` no topo do
`docker-compose.yml` — qualquer pasta/diretório de execução futura mantém
os mesmos volumes/redes/containers.

> Vale considerar reportar os bugs 7.1–7.3 ao professor — outros grupos
> usando o mesmo material original provavelmente batem nos mesmos erros.

### 8.4 — Venv do painel ficava sem `pip` (checagem de idempotência confundida por estado parcial)

No bootstrap do `server/panel/`, a etapa de criar o venv checava
`[ ! -x ~/server/panel/.venv/bin/python3 ]` pra decidir se recriava. Numa
primeira tentativa, `python3-venv` ainda não estava instalado quando o
`python3 -m venv` rodou — o `ensurepip` falhou, mas o venv ficou parcialmente
criado (só os symlinks de `python3`, sem `pip`/`activate`). Na execução
seguinte, o `python3` symlink já existia e *era* executável, então a checagem
de idempotência achava que o venv estava ok e pulava a recriação — deixando
o `pip install` falhar com "No such file or directory".

**Correção:** instalar `python3-venv`/`python3-pip` sempre (via `apt-get
install`, que já é idempotente por natureza) antes de checar/recriar o venv,
em vez de tentar inferir se o pacote já está instalado.

---

## 9. Validação fim a fim (estado atual confirmado)

Testado no servidor via `./deploy.sh up core` + `./deploy.sh up ran`:

1. `add-subscriber.sh` cadastra IMSI `001010000000002` no MongoDB.
2. UE (UERANSIM) registra: NG Setup → Autenticação 5G-AKA → Security Mode →
   `Initial Registration is successful`.
3. PDU Session Establishment Accept → `uesimtun0` sobe com IP `10.60.0.2`.
4. `ping -I uesimtun0 8.8.8.8` → **4/4 pacotes, 0% perda, RTT ~10ms**.
5. `healthcheck.sh`: NRF healthy, N2/N3/N4/N6 todos OK, associação PFCP
   estabelecida, UE rodando com conectividade ativa.

**Uso de recursos** com core + RAN completos rodando: ~492 MiB / 906 MiB de
RAM, ~342 MiB de swap, CPU de cada container abaixo de 2% (MongoDB o mais
pesado, ~13% de um core). **A instância pequena sustenta o Projeto 1
completo com folga.**

O risco de RAM real fica para o Projeto 2 (build do OAI a partir do source é
CPU/RAM-intensivo) — ainda não medido, testar com cautela.

---

## 10. Pendências / próximos passos

- [ ] Confirmar com o professor a rubrica/plano de testes oficiais do
      Projeto 2 (não publicados no repo de origem na data da checagem).
- [ ] Buildar e validar `server/oai-cn-gnb-e2/` no servidor (medir uso de
      RAM/CPU do build do OAI — instância pequena pode não bastar).
- [ ] Avaliar reportar os bugs do §8 ao professor/repositório original.
- [ ] Implementar o restante do blueprint do painel de observabilidade
      (`docs/blueprint-painel-observabilidade.md`) — telemetria (§5) e
      logs filtrados (§5) já feitos sem Loki/Grafana/Prometheus; falta o
      sensor de protocolo E2/NGAP/GTP-U + topologia interativa
      (pedagógico, mais ambicioso).
- [x] **Cadastro de UE**: formulário no painel (IMSI/K/OPc/MSISDN/AMF)
      com help text por campo, chama `./scripts/add-subscriber.sh` via
      `POST /api/subscriber`; guest bloqueado com 403.
- [x] **Ferramentas de teste no painel**:
  - Teste de banda: `iperf3` entre `ueransim` (uesimtun0) e `dn` —
    baseline ~168 Mbits/s confirmado (`scripts/test_throughput.sh`).
  - Teste de interferência: `tc netem` em uesimtun0, botões on/off —
    5% perda + 50 ms delay → ~1.87 Mbits/s (~90× degradação confirmada).
  - Distância relativa: perfis perto/medio/longe/off via `tc netem` —
    longe (10%/120ms) aplicado e verificado via `tc qdisc show`.

---

## 11. Referências dentro do repositório

- [`CHANGELOG.md`](CHANGELOG.md) — histórico cronológico detalhado de cada ação.
- [`docs/blueprint-painel-observabilidade.md`](docs/blueprint-painel-observabilidade.md) — desenho do painel.
- [`docs/labs/`](docs/labs/) — guias originais do curso (instalação Docker, pré-lab GCP/VM, core Open5GS, UERANSIM, relatório de entrega).
- [`server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md`](server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md) — roteiro oficial do Projeto 2.
- `pdfs/` — slides das Aulas 01–04 + planilha de composição de grupos (fonte de tudo no §1).
