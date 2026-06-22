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

## Créditos

Repositório mantido por **Henrique Carmine** —
[henriquecarmine@gmail.com](mailto:henriquecarmine@gmail.com) ·
[@henriquecarmine](https://github.com/henriquecarmine).

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
 │──PDU Session Req────►│────────────────►│──────────────────────►SMF   │
 │                      │                 │                      │──N4──►UPF
 │◄─PDU Session Accept──│◄────────────────│◄─────────────────────│      │
 │ (uesimtun0 UP)       │                 │                      │      │
 │═════════GTP-U sobre N3══════════════════════════════════════════►    │ N6►internet
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
| Chave SSH | `ssl/core5g_openran_arm64.pem` (Ed25519) |
| Tipo de instância | **AWS EC2 `t4g.medium`** (Graviton2 / Neoverse-N1, `aarch64`) — 2 vCPU / 4 GB. (Era `t4g.micro` no início do projeto; upgrade confirmado por `free` em 2026-06-22.) |
| Região AWS | `us-east-2` |
| SO | Ubuntu 24.04.4 LTS (`noble`), kernel `6.17.0-1017-aws`, `aarch64` |
| CPU | 2 vCPUs — `Neoverse-N1` (ARM Graviton2) |
| RAM | ~3,8 GiB (3825 MiB medidos — `t4g.medium`) |
| Swap | 8 GiB em `/swapfile`, `vm.swappiness=10`, persistente via `/etc/fstab` |
| Disco | ~29 GB total |
| Docker | `29.6.0` (pacotes `docker-ce`/`docker-ce-cli`/`containerd.io` arquitetura `arm64`, repositório oficial Docker) |
| Docker Compose | `v5.1.4` (plugin) |

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

### 7.a Projeto 1 vs. Projeto 2 — em que exatamente eles diferem

Os dois implementam uma rede 5G fim a fim, mas em pontos opostos do
espectro "simples e validado" ↔ "complexo e fiel ao O-RAN":

| Aspecto | Projeto 1 (Open5GS + UERANSIM) | Projeto 2 (OAI + FlexRIC) |
|---|---|---|
| Core 5G | Open5GS (imagens prontas, `gradiant/open5gs`) | OAI CN5G (`oai-cn5g-fed/`), UPF em VPP |
| RAN | UERANSIM — gNB/UE **simulados em software**, sem PHY/MAC reais | gNB OAI `nr-softmodem` em **RFSIM** — PHY/MAC/RLC/PDCP/RRC reais, rádio 100% software (sem hardware de RF) |
| Camada de controle externa (RIC) | **Não existe** — rede monolítica, sem separação dado/controle | **FlexRIC** (near-RT RIC) conectado ao gNB via E2AP (porta 36421) |
| Inteligência/observabilidade | Scripts do painel (`tc netem`, `iperf3`) simulam canal/medem banda de fora | **xApps** (`xapp_kpm_moni`, `xapp_kpm_rc`) consomem métricas/controlam o gNB de dentro da arquitetura, via Service Models E2 padronizados (KPM v2.03, RC v1.03) + SMs custom (MAC/RLC/PDCP/GTP) |
| Conceito 3GPP/O-RAN ilustrado | Registro NAS, sessão PDU, QoS, failover de UPF — "rede 5G funciona" | Separação **CU/DU/RIC**, *RAN programável*: o RIC pode observar (KPM) e atuar (RC) sobre o gNB em tempo quase-real — é o conceito central de Open RAN |
| Complexidade de build | Imagens Docker prontas, só `docker compose up` | Build C/C++ nativo a partir do source (`build_oai`, FlexRIC), pesado em CPU/RAM/disco — não tem imagem pronta pra ARM64 |
| Estado em 2026-06-18 | Completo, validado E2E (§9), já apresentado | Build do zero em andamento no servidor (ver `CHANGELOG.md` v0.8.0) — nada estava funcional antes disso, apesar de aparências de progresso anterior |

Em uma frase: o **Projeto 1** prova que uma rede 5G básica funciona ponta
a ponta; o **Projeto 2** acrescenta a camada de **RAN inteligente e
programável** (RIC + xApps falando E2 com o gNB) que é a própria
definição de O-RAN — e é tecnicamente mais pesado porque não há imagem
Docker pronta: tudo é compilado a partir do source, nativo `aarch64`.

### 7.b Build das imagens OAI 5G Core para arm64

As imagens Docker do OAI 5G Core (`oaisoftwarealliance/oai-{amf,smf,nrf,udr,udm,ausf,upf-vpp}:v1.5.1`) no Docker Hub são **amd64-only** — não há variante `linux/arm64/v8`. O servidor AWS t4g.micro (Graviton2, `aarch64`) não tem QEMU/binfmt-misc configurado, então qualquer tentativa de rodar essas imagens falha com `exec /usr/bin/python3: exec format error` e o container sai com código 255.

#### Estratégia adotada

Buildar nativamente para arm64 no Mac Apple Silicon (Docker Desktop com engine `linux/arm64`), exportar como `.tar`, transferir via `scp` e carregar no servidor com `docker load`. Os Dockerfiles estão vendorizados no repositório em `server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-*/docker/Dockerfile.*.ubuntu`.

Script: [`build-oai-arm64.sh`](build-oai-arm64.sh) na raiz do repositório.

```bash
./build-oai-arm64.sh build    # compila as 6 imagens localmente no Mac
./build-oai-arm64.sh save     # exporta para /tmp/oai-images/*.tar
./build-oai-arm64.sh upload   # scp dos .tar para o servidor
./build-oai-arm64.sh load     # docker load no servidor + rm dos .tar
./build-oai-arm64.sh all      # executa os 4 passos em sequência
```

#### Pré-requisitos

| Requisito | Detalhe |
|---|---|
| Máquina | Mac Apple Silicon (M1/M2/M3/M4) — arm64 nativo |
| Docker Desktop | ≥ 4.x com engine `linux/arm64` habilitada |
| Espaço em disco | ≥ 20 GB livres (imagens intermediárias + .tar exportados) |
| Tempo | ~40 min por imagem × 6 = ~4 h no total |
| SSH key | `ssl/core5g_openran_arm64.pem` com acesso ao servidor |
| `.env` | configurado com `AWS_SERVER_HOST`, `AWS_SERVER_USER`, `AWS_SSH_KEY_PATH` |

> **Por que Mac Apple Silicon?** O Docker Desktop no M-series roda containers `linux/arm64` _nativamente_ — sem emulação QEMU. Compilar o OAI (C++ pesado) via emulação levaria 5–10× mais tempo e frequentemente trava por OOM.

#### Como compilar — passo a passo

**1. Clonar o repositório e configurar o .env**

```bash
git clone https://github.com/henriquecarmine/Core5G_ARM64.git
cd Core5G_ARM64
cp .env.example .env
# editar .env: AWS_SERVER_HOST, AWS_SERVER_USER, AWS_SSH_KEY_PATH
```

**2. Compilar as 6 imagens**

```bash
./build-oai-arm64.sh build
# Cada docker build compila o OAI a partir do source dentro do container arm64.
# A ordem importa: AMF → SMF → NRF → UDR → UDM → AUSF
# Cache Docker é reutilizado em recompilações parciais.
```

O que acontece por dentro de cada build (multi-stage Dockerfile):
1. **base stage** — `apt-get install` das dependências de sistema + build tools
2. **base stage** — compilação de spdlog, Pistache, nlohmann/json e nghttp2 a partir do git
3. **builder stage** — `cmake` configura o projeto + `make -j$(nproc)` compila o binário
4. **target stage** — copia apenas o binário e `.so` necessários para a imagem final mínima

**3. Exportar para .tar**

```bash
./build-oai-arm64.sh save
# Cria /tmp/oai-images/oai-{amf,smf,nrf,udr,udm,ausf}.tar (~60 MB cada)
```

**4. Enviar para o servidor**

```bash
./build-oai-arm64.sh upload
# scp de cada .tar para ~/ no servidor via SSH
```

**5. Carregar no daemon Docker do servidor**

```bash
./build-oai-arm64.sh load
# docker load -i ~/oai-{comp}.tar && rm ~/oai-{comp}.tar  (para cada componente)
```

**Ou tudo de uma vez:**

```bash
./build-oai-arm64.sh all
```

**Verificar que as imagens são realmente arm64:**

```bash
# no servidor:
docker run --rm oaisoftwarealliance/oai-amf:v1.5.1 uname -m
# esperado: aarch64
```

#### Parâmetros do build

| Parâmetro | Valor |
|---|---|
| `--platform` | `linux/arm64` |
| `--build-arg BASE_IMAGE` | `ubuntu:focal` (ver §8.5) |
| `--target` | nome do componente (ex.: `oai-amf`) |
| `-f` | `component/<comp>/docker/Dockerfile.<shortname>.ubuntu` |
| contexto | diretório do componente (ex.: `component/oai-amf/`) |

#### Problemas encontrados — e como foram corrigidos

Estes são os erros que aparecem ao tentar compilar as imagens OAI para arm64 **a partir do código original do repositório**. Os patches já estão aplicados neste repo; esta seção existe para documentar o raciocínio e ajudar quem tentar fazer o mesmo em outra base de código.

**Bug 1 — `declare -A` não suportado no bash 3.2 do macOS**

macOS 14/15 vem com bash 3.2 (limitação de licença GPLv2). O script original usava `declare -A COMPONENTS=(...)` (bash 4+), causando `oai: unbound variable` ao rodar.

Correção: substituído por string simples iterada com `for comp in $COMPONENTS`:
```bash
COMPONENTS="oai-amf oai-smf oai-nrf oai-udr oai-udm oai-ausf"
# oai-upf-vpp excluído: requer libhyperscan (Intel-only, inexistente no arm64)
for comp in $COMPONENTS; do ...
```

**Bug 2 — Nome errado do Dockerfile**

O Dockerfile se chama `Dockerfile.amf.ubuntu` (sem o prefixo `oai-`), não `Dockerfile.oai-amf.ubuntu`. O script gerava o nome errado, causando "Dockerfile não encontrado" para todos os 7 componentes.

Correção: adicionado `shortname="${comp#oai-}"` para remover o prefixo antes de montar o caminho:
```bash
shortname="${comp#oai-}"   # oai-amf → amf
dockerfile="$ctx/docker/Dockerfile.${shortname}.ubuntu"
```

**Bug 3 — `libboost1.67-dev` não disponível no repositório arm64 do Ubuntu 18.04**

O `build_helper.amf` (e equivalentes de cada componente) para `ubuntu18.04` adiciona o PPA `ppa:mhier/libboost-latest` e instala `libboost1.67-dev`. Esse PPA não publica pacotes arm64 — o `apt-get install` falha com `E: Unable to locate package libboost1.67-dev`, e o build aborta com "AMF deps installation failed".

Correção: passar `--build-arg BASE_IMAGE=ubuntu:focal`. Ubuntu 20.04 tem Boost 1.71 nos repositórios padrão; o `build_helper` tem um case específico `ubuntu20.04` que instala `libboost-all-dev` diretamente, sem PPA. O Dockerfile suporta bionic, focal e jammy explicitamente — usar focal é o caminho suportado.

**Bug 4 — `-msse4.2` hardcoded no CMakeLists.txt de todos os componentes**

Após resolver o Bug 3, a compilação falha com `cc: error: unrecognized command line option '-msse4.2'`. O bloco de detecção de arquitetura em cada `src/*/CMakeLists.txt` tem:

```cmake
if (CMAKE_SYSTEM_PROCESSOR STREQUAL "armv7l")
  set(C_FLAGS_PROCESSOR "-gdwarf-2 -mfloat-abi=hard -mfpu=neon -lgcc -lrt")
else (CMAKE_SYSTEM_PROCESSOR STREQUAL "armv7l")  # ← else genérico
  set(C_FLAGS_PROCESSOR "-msse4.2")              # ← flag x86 SSE4.2
endif()
```

No build `linux/arm64`, `CMAKE_SYSTEM_PROCESSOR` é `aarch64` — cai no `else` e tenta compilar com `-msse4.2` (instrução x86 SIMD que não existe em ARM).

Correção aplicada nos 5 componentes afetados (`oai-amf`, `oai-smf`, `oai-nrf`, `oai-udr`, `oai-udm`, `oai-ausf`):

```cmake
if (CMAKE_SYSTEM_PROCESSOR STREQUAL "armv7l")
  set(C_FLAGS_PROCESSOR "-gdwarf-2 -mfloat-abi=hard -mfpu=neon -lgcc -lrt")
elseif (CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|arm64")
  set(C_FLAGS_PROCESSOR "")   # ← ARM64 nativo, sem flags arquitetura-específicas
else()
  set(C_FLAGS_PROCESSOR "-msse4.2")
endif()
```

O `oai-upf-vpp` usa VPP com sistema de build próprio e não tem essa flag.

**Bug 5 — `libasan2` inválido em `build_helper.udm` silencia o `apt-get` inteiro**

O `build_helper.udm` tinha `libasan2` no `PACKAGE_LIST` ubuntu (linha que não está presente nos outros componentes). O `libasan2` não existe no Ubuntu 20.04 arm64 (`libasan5` é a versão correta, já incluída em `specific_packages`). O `apt-get install -y` falha inteiro com `E: Unable to locate package libasan2` — mas o erro é silenciado porque o `ret=$?` subsequente captura o código de saída do bloco `if/case` (que retorna 0 para ubuntu20.04), não do `apt-get`. Resultado: nenhum pacote do `PACKAGE_LIST` é instalado, incluindo `libconfig++-dev`. O cmake então falha com `None of the required 'libconfig++' found`.

Correção: remover a linha `libasan2` (e o `libasan` genérico que também não existe) do `PACKAGE_LIST` ubuntu em `build_helper.udm`. O `libasan5` já está em `specific_packages` para ubuntu20.04.

Arquivo afetado: `server/.../oai-udm/build/scripts/build_helper.udm`

**`oai-upf-vpp` em arm64 — RESOLVIDO com Vectorscan (2026-06-21)**

Por muito tempo o `oai-upf-vpp` foi tido como "não portável" para arm64. O
diagnóstico real, ao investigar a fonte: o bloqueio era **uma única dependência**
— o **Hyperscan** (`libhyperscan-dev`), biblioteca de regex SIMD da Intel
(SSE/AVX), inexistente no Ubuntu arm64. O plugin UPF da Travelping a exige via
`pkg_check_modules(HS libhs)` (pkg-config puro).

A solução: o **[Vectorscan](https://github.com/VectorCamp/vectorscan)** é um fork
portável do Hyperscan — ARM NEON 100% funcional, **API/ABI-compatível**, mesmo
SONAME `libhs.so.5`. É **drop-in**: compilando o Vectorscan e instalando-o, o
`pkg_check_modules(HS libhs)` o encontra e o GTP UPF é habilitado normalmente
(`Found libhs, version 5.4.12`). Os outros "bloqueios" citados antes não se
confirmaram — o VPP 2101 **core não usa hyperscan**, e os caminhos de lib já
estavam corrigidos para `aarch64-linux-gnu` no Dockerfile.

Passos do porte (em [`docker/Dockerfile.upf-vpp.ubuntu.arm64`](server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-upf-vpp/docker/Dockerfile.upf-vpp.ubuntu.arm64)):
1. Base `ubuntu:focal` (gcc-9; Vectorscan exige C++17/gcc≥9) + `cmake` recente
   via pip (focal tem 3.16; Vectorscan pede ≥3.18.4).
2. Compilar o Vectorscan removendo `-Werror` (gcc-9 dá falso-positivo em
   `state_compress.c` + a flag `-Wno-stringop-overread` só existe no gcc-11) e
   desligando os extras (`BUILD_UNIT/TOOLS/EXAMPLES/BENCHMARKS/DOC=OFF`).
3. `sed` removendo `dh-systemd` do `DEB_DEPENDS` do VPP (pacote bionic-only que
   quebra o `make install-dep` no focal; só serve p/ empacotar `.deb`).
4. `sed` forçando `https://github.com` nas URLs dos pacotes externos do VPP
   (o `rdma-core` baixava por `http://github.com:80` → "connection refused").
5. Copiar o `libhs.so.5` (Vectorscan) para a imagem final.

Resultado validado: `vpp` ELF **ARM aarch64**, `upf_plugin.so` resolve
`libhs.so.5`. **Runtime validado** (docker `--privileged` + hugepages): o VPP
boota completo e o plugin responde — `show plugins` lista `upf_plugin.so
21.01.1`, `show upf specification release` → `PFCP version: 15`. O abort que
aparecia no `flowtable_init` **não era defeito do porte**: era o `main-heap`
lastreado por hugepages sem páginas suficientes; com `main-heap-page-size 4k`
(ou hugepages dimensionadas) sobe normal. **Pega operacional p/ quem deployar:**
não lastreie o main-heap com mais hugepages do que o host tem livre — use 4k ou
reserve hugepages suficientes (heap + buffers). Imagem em
`artifacts/oai-images/oai-upf-vpp.tar` (~138 MB).

**Validação no Graviton real (servidor AWS, 2026-06-22).** Imagem carregada no
servidor (`docker load`, arch=arm64) e rodada standalone com o box **ocioso**
(`--cpus=1.5`, heap 2G/4k). Teste **event-driven** (readiness por estado: socket
CLI existe OU processo morre — sem sleep/timeout fixo) com **métricas reais**:

| Check | Valor medido no Graviton |
|---|---|
| `docker stats` | cpu 2,23% · mem 1,41 GiB / 3,74 GiB (37,8%) · 1 pid |
| `show version` | `vpp v21.01.1` (ARM) |
| `show plugins` | `upf_plugin.so 21.01.1` |
| `show upf specification release` | `PFCP version: 15` |
| `show memory main-heap` | total 1,99G · **usado 1,08G** · livre 938M |
| `show buffers` | pool `default-numa-0` 17.240 buffers |
| `upf_plugin.so` | liga em `libhs.so.5` (vectorscan) |

O **uso real de heap (1,08 GB)** explica por que 1G falha e 2G basta: o flowtable
do plugin pré-aloca ~1 GB (default de compilação, sem `init.conf` dimensionando).
Container **autoterminou** e foi removido; load do host 0,3 → 1,0 (trivial).

> **Lição aprendida (registrada p/ não repetir):** rodar VPP no box **enquanto o
> lab P2 está ativo** (load ~30 nos 2 vCPUs) com um harness que **não
> autotermina** sufocou o `sshd` e exigiu reboot. Regra: testes de VPP no servidor
> só com o box **ocioso**, container **`--rm` + autotérmino**, e espera por
> **estado/evento** (nunca timeout cego). Ver [[feedback-event-driven-nao-tempo]].

Falta só o **E2E completo** (sessão PFCP do SMF + GTP-U do gNB + tráfego de UE),
que exige o core+RAN inteiro e uma janela sem aula — e o lab não depende disto.

> O lab principal continua usando o UPF do Open5GS (`open5gs-upfd`, P1) e o
> `oai-upf` simple_switch (P2, core v2.2.1) — não depende desta imagem. O porte
> existe pelo princípio Open RAN ("toda tecnologia O-RAN deve ser aberta") e é
> candidato a report upstream para a OAI.

#### Resultado — builds concluídos em 2026-06-19

Compilação realizada no Mac Apple Silicon (M-series) via Docker Desktop `linux/arm64`. Total de tempo: ~40 min por imagem (base stage + build from source + cmake + make). Imagens carregadas no servidor AWS t4g.micro (Graviton2, Ohio) e verificadas com `uname -m → aarch64`.

| Imagem                         | Tag    | Tamanho | Build SHA (digest)                                        |
|-------------------------------|--------|---------|-----------------------------------------------------------|
| oaisoftwarealliance/oai-amf   | v1.5.1 | 280 MB  | `sha256:404e88009215...` |
| oaisoftwarealliance/oai-smf   | v1.5.1 | 260 MB  | `sha256:90d5058e53c6...` |
| oaisoftwarealliance/oai-nrf   | v1.5.1 | 264 MB  | `sha256:49528805e9ae...` |
| oaisoftwarealliance/oai-udr   | v1.5.1 | 268 MB  | `sha256:3d2cab6d1063...` |
| oaisoftwarealliance/oai-udm   | v1.5.1 | 257 MB  | `sha256:f49f777b6d06...` |
| oaisoftwarealliance/oai-ausf  | v1.5.1 | 255 MB  | `sha256:e7a98d7f0ee8...` |

#### Onde estão os arquivos

**Servidor AWS** (destino final):
```
# Imagens já carregadas no daemon Docker — prontas para uso:
docker images | grep oaisoftwarealliance
```

**Google Drive do projeto** (cópia permanente dos `.tar`):
```
PROJETOS/Core5G_ARM64/artifacts/oai-images/
├── oai-amf.tar    (63 MB)
├── oai-smf.tar    (60 MB)
├── oai-nrf.tar    (60 MB)
├── oai-udr.tar    (61 MB)
├── oai-udm.tar    (59 MB)
└── oai-ausf.tar   (59 MB)
# total: ~362 MB  — não versionados no git, ficam no Drive
```

Para carregar em qualquer host arm64 sem recompilar:
```bash
# copiar do Drive para o servidor e carregar:
scp -i sua-chave.pem artifacts/oai-images/oai-amf.tar ubuntu@<servidor>:~/
ssh -i sua-chave.pem ubuntu@<servidor> "docker load -i ~/oai-amf.tar && rm ~/oai-amf.tar"
# repetir para cada componente
```

Para exportar diretamente do servidor de laboratório (se tiver acesso SSH):
```bash
ssh ubuntu@core5g-arm64.duckdns.org "docker save oaisoftwarealliance/oai-amf:v1.5.1 -o ~/oai-amf.tar"
scp ubuntu@core5g-arm64.duckdns.org:~/oai-amf.tar .
docker load -i oai-amf.tar
```

> Guia completo de download (sem compilar): [`OAI-CORE-ARM64.md §Download`](server/oai-cn-gnb-e2/docs/OAI-CORE-ARM64.md)

Para recompilar do zero (requer Mac Apple Silicon + Docker Desktop):
```bash
git clone https://github.com/henriquecarmine/Core5G_ARM64.git
cd Core5G_ARM64
cp .env.example .env   # preencher AWS_SERVER_HOST e AWS_SSH_KEY_PATH
./build-oai-arm64.sh build   # ~4 h total para os 6 componentes
./build-oai-arm64.sh save    # exporta para /tmp/oai-images/
./build-oai-arm64.sh upload  # scp para o servidor
./build-oai-arm64.sh load    # docker load no servidor
```

**Dockerfiles** com todos os patches arm64 aplicados:
```
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/docker/Dockerfile.<comp>.ubuntu
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/build/scripts/build_helper.<comp>
server/oai-cn-gnb-e2/oai-cn5g-fed/component/oai-<comp>/src/*/CMakeLists.txt
```

---

### 7.c Plano de usuário no arm64 (OAI v2.2.1) + xApps event-driven

> **Por que esta seção existe.** O core v1.5.1 que buildamos (§7.b) **não tinha UPF
> em arm64** (o `oai-upf-vpp` é Intel-only, depende de `libhyperscan`). Na prática o
> Projeto 2 só tinha plano de **controle** — o UE nunca pegava IP. A OAI passou a
> publicar imagens **multi-arch oficiais** a partir do `v2.1.10`; o **`v2.2.1`** tem
> **7/7 NFs com arm64**, incluindo `oai-upf` (datapath `simple_switch`). Migramos para
> ele e o **user plane passou a funcionar** (UE ganha IP `12.1.1.x`, tráfego real).

**Onde mora:** `server/oai-cn-gnb-e2/oai-cn5g-v2/` (paralelo ao v1.5.1, não o substitui).
Detalhes de config em [`oai-cn5g-v2/README.md`](server/oai-cn-gnb-e2/oai-cn5g-v2/README.md).
Casa com o gNB atual: PLMN **208/95**, TAC `0xa000`, slice **SST 222 / SD 123**,
DNN **default** (pool `12.1.1.0/26`), AMF fixo `192.168.70.132`, SNAT no UPF (UE → internet).

**Subir o Projeto 2 completo (por SSH):**
```bash
cd server/oai-cn-gnb-e2
./oai-cn5g-v2/up_core_v2.sh    # para o Projeto 1, sobe o core v2.2.1, espera oai-amf RUNNING
./scripts/up_e2_lab_v2.sh      # near-RT RIC + gNB (RFSIM, 24 PRBs / 51 NRB) + nrUE
```

**Rodar xApps — event-driven, sem timeout cego:**
```bash
./scripts/run_xapp.sh cust    # xApp MAC/RLC/PDCP/GTP (SM custom)
./scripts/run_xapp.sh kpm     # E2SM-KPM (métricas DRB/PRB)
./scripts/run_xapp.sh rc      # E2SM-RC (controle)
./scripts/e2_verify.sh        # sobe o lab + valida E2 SETUP + roda os 3 xApps 7x cada
```
Cada `run_xapp.sh` **encerra no 1º evento de sucesso** (E2 conectado + subscrito/indicação),
nunca por duração fixa — determinístico. Pré-requisito checado por **estado** (`pgrep -x
nearRT-RIC` + `nr-softmodem`), não por `sleep`. CPU sob controle: cgroup com `CPUQuota`
(`XAPP_CPU_QUOTA`, default `50%`) + `nice`.

#### Validação dos xApps (resultado real) e os 2 bugs que estavam no caminho

Rodando `e2_verify.sh` (sobe lab sem UE + 3 xApps 7× cada): **cust 7/7, kpm 7/7, rc 5/7**
— os xApps conectam ao RIC e **subscrevem** as RAN functions (`Successfully subscribed to
RAN_FUNC_ID …`). Até chegar nesse resultado, dois bugs (que NÃO eram "falta de CPU", como
parecia no começo) precisaram ser corrigidos:

1. **Plugins SM de arquitetura errada (crash do RIC).** O repo versionava
   `flexric-lib/*.so` compilados para **x86-64**; num host **arm64** o `dlopen` do
   `nearRT-RIC` falha (`load_plugin_ric: Assertion handle != NULL`). Pior: `sync-oai`
   espalhava esses x86-64 por cima dos arm64 que o servidor tinha buildado. **Correção:**
   os `.so` saíram do git (são artefatos de build, arch-específicos; ver `.gitignore`) e o
   `up_flexric.sh` agora **detecta a arquitetura** e repovoa `flexric-lib/` do build tree
   (`sync_flexric_lib.sh`) quando falta OU é de outro arch. Auto-curável.

2. **Falso-negativo no `run_xapp.sh`.** Usava `tail -F --pid | grep -m1` com
   `set -o pipefail`: quando o `grep -m1` casa o evento de sucesso e fecha o pipe, o `tail`
   morre com SIGPIPE e o `pipefail` marcava o pipeline inteiro como falha — reportando
   `❌ FALHA` mesmo com o xApp subscrito. **Correção:** trocado por **poll no arquivo**
   (`grep -q` em laço até o evento OU o processo morrer), sem pipe, sem SIGPIPE.

#### Restrição operacional do box (2 vCPUs)

O `nr-softmodem` e o `nr-uesoftmodem` em RFSIM fazem **busy-poll** (cada um satura ~1 vCPU →
load > 20), e aí o caminho INDICATION→Report do RIC pode estourar o timeout interno do
FlexRIC. Por isso a validação sobe **sem o nrUE** (`SKIP_UE=1`, default no `e2_verify.sh`):
o E2 é gNB↔RIC e não depende do UE, e sobra 1 vCPU inteiro pro RIC+xApp (load < 2). Para o
lab completo COM user plane, suba normal (`SKIP_UE=0`) — mas não rode os 7× de xApp junto.

**Medição no servidor (2026-06-22) — o UE attach é mutuamente exclusivo com o guardrail
de cpuset.** Com o guardrail ativo (`oai-lab.slice AllowedCPUs=1` = lab inteiro num só
core), o nrUE **sincroniza** (PHY/RFSIM ok: `Initial sync successful, PCI 0`, RSRP 51 dB)
mas o **RRC inunda** (`TASK_RRC_NRUE task contains` 71k→112k) e o UE **não pega IP**: o gNB
(CPUWeight 60) fica com ~40% do core e o nrUE (CPUWeight 20) só ~25% — insuficiente pro RRC
em tempo real. Liberando os **2 cores** (`AllowedCPUs=0-1`), cada processo RFSIM ganha ~1
core e o **user plane funciona de fato**: UE attacha, `oaitun_ue1=12.1.1.2`, e
`ping 8.8.8.8` pela tun dá **4/4, 0% perda, RTT ~111 ms**. Ou seja, o que a §7.c afirma
(UE ganha IP `12.1.1.x`) **se confirma — mas exige os 2 cores**, o que reabre o risco de
freeze que o guardrail previne. Trade-off: **ou** proteção anti-freeze (1 core, sem UE),
**ou** user plane completo (2 cores, box dedicado). O teste foi feito **sem timer**: revert
do cpuset por `trap EXIT` + espera por evento (`ip monitor` p/ o IP, `tail -F --pid|grep -m1`
p/ o flood) + monitor em `nice -20` (garante o revert mesmo sob saturação).

> **Recomendação p/ quem for subir uma instância nova:** use **4 vCPU** (ex.: `t4g.xlarge`
> ou `c7g.xlarge`). Com 4 núcleos — gNB num, UE noutro, RIC+xApp noutro, sistema noutro — o
> lab completo **com user plane** roda sem cpuset, sem guardrail e sem risco de freeze, e os
> xApps rodam em paralelo ao UE (essencial p/ o UE-TP-rApp). Os 2 vCPU são o **caminho
> alternativo** (trade-off acima). Guia completo de reprodução até o user plane, com os dois
> caminhos: [`server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md`](server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md).

> **Princípio do projeto: ZERO tempo, tudo sob controle.** Nada de `sleep`/timeout cego —
> os scripts terminam por **evento/estado** (`grep -m1` em stream, `tail -F --pid`, poll de
> condição). Ver memória `feedback-event-driven-nao-tempo`.

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

### 8.5 — Relatórios com falso-negativo (nome de container ≠ serviço Compose)

Descobertos **rodando os relatórios ao vivo** (não no `bash -n`), v0.25.2. São
bugs da nossa camada de diagnóstico, não do material original — mas enganariam o
professor, então valem o registro:

- **`test_ng_setup` / `test_registration` diziam "AMF não está rodando"** com o
  AMF perfeitamente no ar. Causa: os scripts faziam `docker inspect amf`, mas
  `amf` é o nome do **serviço Compose** — o **container** se chama
  `open5gs-amf-containerized`. `docker inspect`/`exec`/`logs` exigem o nome do
  **container**; só `docker compose logs` aceita o nome do **serviço**. O
  `inspect` falhava → o cruzamento com o AMF virava aviso → `test_ng_setup`
  concluía *"N2 não confirmada"* **mesmo com `NGSetupResponse` recebido**.
- **`test_ue_connection` mostrava `IP público <!DOCTYPE html>`.** `wget
  http://ifconfig.me` devolve a **página HTML**, não o IP. Corrigido para
  `http://ifconfig.me/ip` (texto puro) + extração/validação do IP por regex.
- **Veredito final sempre "ok".** `test_ue_connection` terminava em `summary ...
  ok` independentemente das checagens. Reescrito com contadores `fails`/`warns`
  e veredito honesto (✗ crítico / ! ressalva / ✓ tudo passou).

**Lição:** `bash -n` valida sintaxe, não semântica. Relatório novo/alterado tem
de **rodar ao vivo** antes do merge. Detalhes em
[`docs/relatorios-didaticos.md`](docs/relatorios-didaticos.md) §5.

### 8.6 — Demo E2E media a bridge Docker, não o túnel 5G

O passo de throughput da Demonstração E2E (`demo_e2e.sh`) fazia
`iperf3 -c 10.50.0.100` de dentro do container do UE. Mas o DN
(`open5gs-dn-containerized`, `10.50.0.100`) está na **mesma rede Docker** onde o
container do UE tem a `eth0` — então o iperf saía **direto pela bridge Docker, não
pelo túnel 5G** (`uesimtun0`, pool `10.60.0.0/16`). Resultado: não media o núcleo
e ainda falhava por *timing* do servidor `iperf3 -s -1`.

**Correção (v0.25.0):** criar uma **rota temporária para o DN via `uesimtun0`** e
**amarrar a origem ao IP do túnel** (`iperf3 -B 10.60.0.x`), forçando o caminho
real `UE → gNB → UPF (NAT na N6) → DN`; a rota é removida ao final. Validado ao
vivo: **149 Mbit/s** atravessando o núcleo 5G (antes: sem medição). De quebra, a
Demo E2E passou a ecoar o **comando real + saída real + "Por quê"** de cada passo.

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

**Verificação ao vivo de todos os relatórios (2026-06-21, v0.25.0–0.25.3):**
rodados de verdade, não só `bash -n`. **Projeto 1** — `status`,
`system-status`, `ng-setup`, `registration`, `config-coherence`,
`ue-connection` e `upf-failover` (failover mantendo conectividade) passam, todos
com cabeçalho de seção, checagens coloridas e bloco "Resumo"; 3 bugs de precisão
encontrados e corrigidos (§8.5). **Projeto 2** — `e2-sm` (cadeia O-RAN fim-a-fim,
7 assinaturas), `e2-kpm` (assinatura OK, veredito honesto "sem tráfego no
período") e `e2-rc` (eventos RRC do attach capturados) passam, sem bugs. A
Demonstração E2E mede **149 Mbit/s** reais pelo túnel 5G (§8.6).

---

## 10. Pendências / próximos passos

- [ ] Confirmar com o professor a rubrica/plano de testes oficiais do
      Projeto 2 (não publicados no repo de origem na data da checagem).
- [x] Diagnóstico do estado real do Projeto 2 (2026-06-18): nada estava
      funcional — `.so` de Service Model eram x86-64 (errado pra ARM64),
      único log existente mostrava E2SM-RC falhando com core dump, sem
      nenhum binário compilado no servidor. Ver `CHANGELOG.md` v0.8.0.
- [x] Buildar e validar `server/oai-cn-gnb-e2/` (2026-06-19): 6 imagens OAI
      5G Core arm64 construídas no Mac Apple Silicon, carregadas no servidor;
      `up_e2_lab.sh` sobe Core OAI + nearRT-RIC + gNB(E2) + nrUE; E2 SETUP OK,
      8 RAN functions registradas (2,3,142–148), `test_e2_sm.sh all` passa
      (xApps subscrevem KPM/RC/MAC/RLC/PDCP/GTP). UE chega a `RRC_CONNECTED`.
- [x] **Estabilidade da instância** (2026-06-19): o gNB/nrUE RFSIM saturavam
      os 2 vCPUs do `t4g.medium` e **congelavam a máquina** (vários reboots
      forçados). Corrigido envelopando os processos nativos em *scopes* do
      systemd com `CPUQuota` (120%/60%) + `CPUWeight=20` + `nice 10` em
      `up_gnb_oai.sh` — reserva CPU pro sistema, impede o freeze sem quebrar
      o E2 (validado: máquina responsiva sob carga, E2 SM test passa).
- [ ] **xApp UE-TP-rApp** (tema do grupo): previsão de throughput por UE a
      partir de RSSI/RSRP/CQI/PRB. Esqueleto em `xapp_ue_tp_moni.c`; falta o
      modelo de previsão. **Próximo grande passo após a apresentação.**
- [ ] **🧱 Upgrade para 4 vCPU — bloqueio de HW para o relatório completo de KPM.**
      Coletar KPM com **throughput real** (dados não-zero p/ a análise e o
      UE-TP-rApp) exige UE+gNB RFSIM em tempo real, o que **não cabe em 2 vCPU sob
      o guardrail**. Forçar 2 cores (remover o guardrail) **congelou o box 2×**
      (reboots). Decisão: o coletor (`kpm_collect_real.sh`) **nunca mexe no cpuset**
      e conclui honesto em 2 vCPU; **dados reais dependem de instância 4 vCPU**
      (`t4g.xlarge`). Por ora, demonstração segura = KPM assinado + análise sobre a
      amostra (`kpm_analytics.sh`). Ver [`docs/KPM-COLETA-RESILIENTE.md`](server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md).
- [x] **User plane do UE no Projeto 2 — RESOLVIDO no core v2.2.1** (2026-06-22):
      o UE attacha, pega IP `12.1.1.2` e tem tráfego real (`ping 8.8.8.8` 0% perda
      pela `oaitun_ue1`). O bloqueio **não era** o AUSF↔UDM HTTP/2 (esse era do
      core **v1.5.1**); no v2.2.1 o gargalo é **CPU**: em 2 vCPU com o guardrail de
      cpuset (1 core), gNB e UE dividem o core e o RRC do UE inunda. Com os **2
      cores** liberados (ou **4 vCPU**, recomendado), o UE attacha normal. Trade-off
      e procedimento timer-free em [`server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md`](server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md)
      e §7.c.
- [ ] Persistir os symlinks do FlexRIC (`/usr/local/lib/flexric` e
      `/usr/local/etc/flexric`) no `infra/server-bootstrap.sh` — hoje são
      criados à mão e se perdem ao trocar de instância.
- [x] Grupo "Projeto 2 — OAI/FlexRIC (E2)" no painel (`server.py` +
      `index.html`): botões up/down/test do E2 lab, mesmo mecanismo
      genérico `data-cmd` → `POST /api/run/{cmd}` do Projeto 1.
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
    baseline ~150 Mbits/s confirmado (`scripts/test_throughput.sh`).
  - Teste de interferência/distância: `tc netem` em uesimtun0 via
    `scripts/test_channel.sh` (modelos 3GPP TR 38.901 + Shannon). Ideal
    ~148 Mbit/s → 1km/media ~608 Kbit/s (perda/RTT acompanham).
- [x] **Colorimetria ISO/ANSI + resumo didático em todos os testes**
      (v0.12.0): lib `scripts/lib/testlog.sh` + render ANSI no painel; cada
      teste termina com "O que fez" + "Resultado" colorido. Ver `CHANGELOG.md`.
- [x] **Auditoria didática + verificação ao vivo de todos os relatórios**
      (v0.25.0–0.25.3): Demo E2E com comando/saída real + "Por quê" e
      throughput corrigido (149 Mbit/s pelo túnel 5G, §8.6); P1 e P2 rodados ao
      vivo, 3 bugs de precisão corrigidos (§8.5); guia dev em
      [`docs/relatorios-didaticos.md`](docs/relatorios-didaticos.md).
- [x] **Anti-freeze**: gNB/nrUE RFSIM rodam sob `systemd-run --scope` com
      `CPUQuota`/`CPUWeight`/`nice` em `up_gnb_oai.sh`, `test_e2_kpm.sh` e
      `test_e2_rc_attach.sh` — a instância de 2 vCPUs não congela mais.

> **Pega operacional (5G-AKA / SQN):** se o UE não registra e o log mostra
> `Authentication Failure due to SQN out of range`, o número de sequência do
> assinante (UDM/MongoDB) dessincronizou do SIM. Solução: re-cadastrar o
> assinante (`./scripts/add-subscriber.sh`, que deleta+insere e zera o SQN) e
> reiniciar o UE (`docker restart ueransim`). O `uesimtun0` volta em segundos.

---

## 11. Referências dentro do repositório

- [`README.md`](README.md) — porta de entrada: **como reproduzir** o estado
  atual do zero, roadmap com datas e **como colaborar** (contato:
  [hc@cesar.school](mailto:hc@cesar.school) · [@henriquecarmine](https://github.com/henriquecarmine)).
- [`CHANGELOG.md`](CHANGELOG.md) — histórico cronológico detalhado de cada ação.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — como colaborar (Issues/Discussions/PR, validação, versão).
- [`docs/relatorios-didaticos.md`](docs/relatorios-didaticos.md) — **guia dev do sistema de relatórios**: lib `testlog.sh`, protocolo da Demo E2E, como adicionar um relatório, gotchas (§8.5–8.6) e inventário P1/P2.
- [`docs/blueprint-painel-observabilidade.md`](docs/blueprint-painel-observabilidade.md) — desenho do painel.
- [`docs/labs/`](docs/labs/) — guias originais do curso (instalação Docker, pré-lab GCP/VM, core Open5GS, UERANSIM, relatório de entrega).
- [`server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md`](server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md) — roteiro oficial do Projeto 2.
- [`server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md`](server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md) — **guia de reprodução até o user plane** (UE com IP + ping): dimensionamento de CPU (**4 vCPU recomendado vs 2 vCPU alternativo**), subida do core v2.2.1 + E2 + xApps, e o procedimento timer-free de liberar/reverter os 2 cores.
- [`server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md`](server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md) — **Dados na RAN**: pipeline didático `kpm_analytics.sh` (Aula 06, slide 46) que transforma o log KPM bruto em série temporal CSV + KPIs por UE + sparkline; ponte para o UE-TP-rApp e o Módulo 7 (Análise de Dados).
- [`server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md`](server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md) — **engenharia milimétrica** do `kpm_collect_real.sh`: coleta KPM com tráfego real **resiliente e 100% por evento** (heartbeat "não travou", auto-retry, auto-revert do cpuset, watchdog anti-hang) — o padrão de "zero tempo" aplicado, para a apresentação ao vivo.
- `pdfs/` — slides das Aulas 01–04 + planilha de composição de grupos (fonte de tudo no §1).
