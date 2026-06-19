# Changelog

Registro cronológico das ações realizadas no projeto e no servidor ARM AWS.
Formato livre, em português, focado em "o que mudou e por quê".

Versões: `MAJOR.MINOR.PATCH` — MAJOR sobe quando o painel muda de forma
visível pro professor/apresentação; MINOR a cada bloco de funcionalidade;
PATCH em correções pontuais.

| Versão | Data       | Destaque                                        |
|--------|------------|-------------------------------------------------|
| 0.1.0  | 2026-06-18 | Infra AWS + Open5GS + UERANSIM funcionando      |
| 0.2.0  | 2026-06-18 | Painel FastAPI + Caddy HTTPS + auth admin/guest |
| 0.3.0  | 2026-06-19 | Telemetria em tempo real + filtro de logs       |
| 0.4.0  | 2026-06-19 | Cadastro de UE + ferramentas de teste           |
| 0.5.0  | 2026-06-19 | Modal UE + action bar + rodapé de versão        |
| 0.6.0  | 2026-06-18 | UE Lab unificado + logs coloridos + 3GPP/Shannon |
| 0.7.0  | 2026-06-18 | Legendas de fórmulas + dropdown duração + info banda + logs corrigidos + visão O-RAN |
| 0.8.0  | 2026-06-18 | Build do Projeto 2 (OAI/FlexRIC) no servidor + grupo "Projeto 2" no painel |

---

### Projeto 2 (OAI + FlexRIC/E2) — diagnóstico de estado real, build no servidor, botões no painel

- **Diagnóstico (2026-06-18)**: pesquisa nos `pdfs/` + inspeção direta do
  servidor mostraram que, ao contrário da impressão inicial ("progresso
  substancial"), **nada do Projeto 2 estava de fato funcional**:
  - `server/oai-cn-gnb-e2/flexric-lib/*.so` (8 libs de Service Model)
    eram binários **x86-64**, não `aarch64` — herdados do material do
    curso, inúteis no servidor ARM64 de produção.
  - O único log não-vazio (`logs/test_rc_run.log`) registrava uma
    **falha**: assertion error no E2SM-RC (`e2ap_dec_e42_setup_response`,
    `protocolIEs.list.count == 3` falhou) terminando em `Aborted (core
    dumped)`.
  - Não havia nenhum binário compilado (`nr-softmodem`, `nearRT-RIC`) em
    lugar nenhum do `~/server/oai-cn-gnb-e2/` remoto — só código-fonte.
  - Conclusão: Projeto 2 precisa ser **buildado do zero e validado**,
    não "religado" — com a apresentação em 2026-06-20 (Aula 06), restavam
    ~2 dias.
- **Decisão de execução**: build feito **direto no servidor de
  produção** (AWS `t4g.micro`, 906 MiB RAM), em vez de localmente, porque
  o build precisa ser nativo `aarch64` e o servidor é o único ambiente
  ARM64 disponível. Para caber na RAM, **Projeto 1 foi parado
  temporariamente** (`down_ran.sh` + `down_core.sh`) antes do build —
  RAM livre subiu de ~162 MiB para ~555 MiB.
- **Princípio confirmado com o usuário**: tudo que é código/config fica
  versionado no repo e chega ao servidor só via `./deploy.sh` (já
  existia `sync-oai` pra isso); a única coisa que roda via SSH direto é
  a **compilação em si** (não dá pra "deployar" um build nativo
  ARM64 como arquivo estático — tem que compilar na máquina de destino).
  Avaliada a ideia de criar um subcomando `build-oai` no `deploy.sh` e
  **descartada** por decisão do usuário ("tá bom como está").
- **Pipeline de build executado no servidor** (scripts 100% versionados
  em `server/oai-cn-gnb-e2/scripts/`, sincronizados via
  `./deploy.sh sync-oai`):
  1. `sudo ./build_oai --ninja -I` (dentro de
     `openairinterface5g/cmake_targets/`) — instala dependências de
     sistema (ninja, libsctp, libconfig, etc.) via apt. **Concluído com
     sucesso** ("BUILD SHOULD BE SUCCESSFUL").
  2. `./scripts/build_e2.sh` — clona o submódulo FlexRIC (branch `dev`)
     se ausente, compila `nr-softmodem` + `nr-uesoftmodem` com agente E2
     embutido (`-DE2AP_VERSION=E2AP_V2 -DKPM_VERSION=KPM_V2_03`). Em
     andamento no momento deste registro.
  3. *(pendente)* `./scripts/build_flexric_tools.sh` — compila o
     `nearRT-RIC` + xApps (`xapp_kpm_moni`, `xapp_kpm_rc`, etc.) e os 8
     `.so` de Service Model nativos `aarch64` (substituindo os x86-64
     herdados), via `sync_flexric_lib.sh`.
  4. *(pendente)* validação E2E: `up_e2_lab.sh`, `test_e2_sm.sh
     cust|oran|all`, `test_e2_kpm.sh`, `test_e2_rc_attach.sh`,
     `verify_e2_lab.sh`.
  5. *(pendente)* religar o Projeto 1 (`up_core.sh`/`up_ran.sh` ou
     painel) depois da validação, já que foi parado só pra liberar RAM.
- **Painel**: novo grupo **"Projeto 2 — OAI/FlexRIC (E2)"** na coluna de
  comandos (ao lado de "Projeto 1 — Open5GS"), com botões:
  `Up Core+gNB (OAI)`, `Up E2 lab (RIC+xApps)`, `Testar E2 SM (all)`,
  `Testar E2SM-KPM`, `Testar E2SM-RC (attach)`, `Down E2 lab`, `Down all
  (OAI)`. Reaproveita o mecanismo genérico já existente
  (`button[data-cmd]` → `POST /api/run/{cmd}`), só com novas entradas no
  dict `COMMANDS` de `server/panel/server.py` apontando pros scripts em
  `server/oai-cn-gnb-e2/scripts/` (cwd diferente do Projeto 1).

## [0.7.0] — 2026-06-18

### Painel — legendas, dropdown de duração, info de banda, logs coloridos corrigidos, visão macro O-RAN

#### Legendas das fórmulas (`formula-legend`)

Abaixo de cada `formula-box` no UE Lab, adicionada legenda em fonte monospace
10px explicando cada sigla usada:

- **Distância (3GPP UMa NLOS)**: `PL(d)` = path loss em dB; `d` = distância
  UE–antena em metros; `f_c` = frequência portadora (3,5 GHz para n78);
  `h_UT` = altura do UE (assumido 1,5 m); `UMa NLOS` = Urban Macro, sem
  visada direta (Non-Line-of-Sight, modelo 3GPP TR 38.901).
- **Interferência (Shannon-Hartley)**: `SINR` = Signal to Interference +
  Noise Ratio; `C_signal` = potência do sinal desejado; `N₀` = ruído
  térmico do canal; `I` = potência da interferência co-canal; `B` = largura
  de banda (100 MHz para n78); `C_max` = capacidade máxima do canal
  (Shannon); `C/I` = relação portadora/interferência em dB.

CSS adicionado: `.formula-legend` (10px, `#404858`, monospace, 1.6 line-height);
`.formula-legend em` (cor `#5a6a80`, não itálico).

#### Dropdown de duração do iperf3

`<select id="lab-duration">` com opções 5 s / 10 s / 30 s / 60 s (padrão: 10 s)
ao lado do botão "▶ Medir Throughput". CSS `#lab-duration` com `width:auto;
flex:none` para não esticar a linha inteira.

`lab-run-btn` passou a chamar `POST /api/throughput` com `{duration: int}` em
vez de `POST /api/run/test-throughput`:
```
const duration = document.getElementById('lab-duration').value;
body: JSON.stringify({ duration: parseInt(duration) })
```

**Novo endpoint** `POST /api/throughput` em `server.py`:
- Valida `duration` contra `_VALID_DURATIONS = {5, 10, 30, 60}` (fallback 10).
- Passa `IPERF_DURATION=str(duration)` para `stream_command(["./scripts/test_throughput.sh"])`.
- Bloqueado para guest (403).

**`test_throughput.sh`**: linha `DURATION="${1:-5}"` → `DURATION="${IPERF_DURATION:-${1:-10}}"`.
Script agora aceita a env var com prioridade máxima e mantém retrocompatibilidade
com passagem direta de argumento (`$1`). Duração padrão atualizada para 10 s.

#### Informações de banda em "Condições do Canal"

Barra `.channel-info-bar` inserida abaixo do título da seção:
```
5G NR n78 · TDD · 3.3–3.8 GHz · BW 100 MHz · SCS 30 kHz · 66 PRBs
· ↓ DL ~665 Mbps · ↑ UL ~250 Mbps
```
DL em azul (`.band-dl` → `#4dabf7`), UL em verde (`.band-ul` → `#69db7c`).
Fundo `#13151a`, borda `#1e2028`, fonte SF Mono 10.5px.

Valores derivados do padrão 5G NR n78 com BW 100 MHz, SCS 30 kHz, 66 PRBs,
eficiência espectral máxima (6 bits/s/Hz × 4 camadas DL, 1 camada UL típica).

#### Colorização de logs — fix definitivo

Problema: logs não exibiam cor alguma — apareciam todos na cor padrão
(`var(--text)`, branco).

Causa raiz identificada: a implementação anterior usava
`const u = line.toUpperCase()` e depois testava `u` com padrões de regex
contendo `\b` (word boundaries). O `\r` emitido pelo Docker antes do `\n`
ficava preso na string limpa, fazendo `\b` não reconhecer o início/fim de
palavra em alguns tokens. Combinado com ANSI residual em certas versões do
`mongosh` e do `open5gs`, a limpeza não era suficiente.

Correção tripla aplicada:
1. `lineColor(line)` reescrita para usar flag `/i` diretamente no regex, sem
   `.toUpperCase()` intermediário — mais robusto e legível.
2. `.replace(/\r/g, '')` adicionado após `stripAnsi()` tanto em `appendLine()`
   quanto em `labAppendLine()` — elimina `\r` antes de qualquer comparação.
3. Padrões ampliados: `REJECT`, `FAILED`, `EXCEPTION` adicionados como
   indicadores de erro (frequentes nos logs 5G/Open5GS que não usam a palavra
   literal `ERROR`).

Paleta final:
- `FATAL|CRITICAL|EMERG|ALERT` → `var(--red)`
- `\bERROR\b|REJECT|FAIL(ED)?|EXCEPTION` → `var(--red)`
- `WARN(ING)?` → `var(--yellow)`
- `\b(DEBUG|TRACE|DEBU)\b` → `#5a6170`
- `\bINFO\b|\bNOTICE\b|\bNOTI\b` → `var(--info)` (`#4dabf7`)
- demais → `var(--text)`

#### Visão macro O-RAN — sidebar e UE Lab

**Sidebar (seção Logs)**: `<details>` expansível com título "▸ Visão macro O-RAN"
contendo div `.oran-arch` (fundo `#0d0e11`, fonte monospace 10.5px, `white-space:pre`).
Diagrama ASCII mostra toda a pilha:
```
[SMO / Non-RT RIC]  ←─ A1 Policy ─→  [Near-RT RIC (FlexRIC)]
       ↕ O1                                   ↕ E2
  [O-gNB / gNB]  ←─ Open FH (7.2x) ─→  [O-RU]
  CU-CP · CU-UP · O-DU
       ↕ N2/N3                        ↕ E2SM-KPM xApp
    [5GC Open5GS]                  KPIs: DRB.UEThpDl/Ul
  AMF·SMF·UPF·PCF…                      RRU.PrbTotDl/Ul
       ↕ N6
    [DN / iperf3]
       ↕ GTP-U / uesimtun0
    [UERANSIM UE]
```

**UE Lab (coluna direita)**: `<details>` com mesmo estilo, mostrando onde o
`tc netem` (simulação de canal) e o `iperf3` (medição de throughput) se
encaixam no fluxo end-to-end.

CSS adicionado: `.oran-arch` + supressão do marcador `<summary>` (`list-style:none`,
`::-webkit-details-marker { display:none }`).

#### `SERVICE_LABELS` — interface 3GPP por NF

Mapa de rótulos nos logs do sidebar atualizado para incluir interface e papel
O-RAN de cada NF, ex.:
- `amf: 'AMF · N1/N2 · UE auth & mobility (NGAP)'`
- `upf-a: 'UPF-A · N3/GTP-U + N6 · user-plane primary'`
- `ueransim: 'UERANSIM · gNB(N2/N3) + UE → uesimtun0'`

#### `core5g-arm64-bible.md` — §2.b Para o engenheiro de redes

Nova seção inserida entre §2 (explicação para leigos) e §3 (contexto da
disciplina), dirigida a quem entende telecomunicações mas não conhece as
configurações específicas deste projeto:

- **Diagrama ASCII do Split 7.2** com O-CU-CP, O-CU-UP, O-DU, O-RU e
  interfaces F1-C/U, Open FH, E2, A1, O1.
- **Tabela de interfaces** (E2, A1, O1, F1-C, F1-U, Open FH, N2, N3, N4)
  com protocolo, origem/destino e função.
- **Projeto 1 vs Projeto 2**: UERANSIM é gNB monolítico sem agente E2 (sem
  visibilidade no RIC); OAI `nr-softmodem` + FlexRIC implementa agente E2
  real com E2SM-KPM.
- **Tabela de KPMs** do E2SM-KPM relevantes para UE-TP-rApp:
  `DRB.UEThpDl`, `DRB.UEThpUl`, `RRU.PrbTotDl`, `RRU.PrbTotUl`,
  `L1M.RS-SINR`.
- **Fluxo NAS/RRC de registro** em ASCII (UE → gNB → AMF → AUSF → UDM →
  SMF → UPF), com identificação de cada mensagem (Registration Request,
  Identity Request, Authentication, Security Mode, PDU Session Establishment).

---

## [0.6.0] — 2026-06-18

### Painel — UE Lab inteligente, logs coloridos, fórmulas reais

#### UE Lab (overlay unificado)

- **Tela unificada** de gestão de UE e testes: botão `⚗ UE Lab` na action
  bar abre overlay 92vw × 88vh, eliminando os controles dispersos na sidebar.
  Coluna esquerda: lista de subscribers do MongoDB + cadastro inline expansível.
  Coluna direita: configuração de canal (distância + interferência) + execução
  de testes + card de resultado + console de saída.

- **Lista de subscribers** (`GET /api/subscribers` → `list-subscribers.sh`):
  `mongosh open5gs --eval 'print(JSON.stringify(db.subscribers.find(...).toArray()))'`
  — retorna `[{imsi, msisdn}]`; botão Atualizar refaz a query sem reabrir o overlay.

- **Deletar UE** (`DELETE /api/subscriber/{imsi}` → `remove-subscriber.sh`):
  `db.subscribers.deleteOne({imsi:'...'})` via mongosh; botão `✕` por linha
  na tabela; validação de IMSI (6–15 dígitos) e bloqueio 403 para guest.

- **Formulário de cadastro** com terminologia de telecomunicações exclusiva
  (IMSI, MSISDN, Ki, OPc, AMF — sem CPF ou termos genéricos). Botão
  **Sugerir** em cada campo:
  - IMSI: contador sequencial em `localStorage` → `'00101' + n.padStart(10,'0')`.
  - MSISDN: sequencial → `'336' + (38060000+n).padStart(8,'0')`.
  - Ki / OPc: 16 bytes aleatórios via `crypto.getRandomValues` → hex maiúsculo.
  - AMF: constante `8000`.

#### Distâncias reais (3GPP TR 38.901 UMa NLOS)

Fórmula exibida no painel: `PL(d) = 13.54 + 39.08·log₁₀(d) + 20·log₁₀(f_c) − 0.6·(h_UT−1.5)`, f_c = 3.5 GHz.

| Opção | d    | PL (dB) | RSRP (dBm) | Delay | Loss |
|-------|------|---------|------------|-------|------|
| 100m  | 100m | 81 dB   | −79 dBm    | 1 ms  | 0%   |
| 500m  | 500m | 102 dB  | −100 dBm   | 8 ms  | 2%   |
| 1km   | 1km  | 113 dB  | −111 dBm   | 20 ms | 8%   |
| 3km   | 3km  | 129 dB  | −127 dBm   | 50 ms | 20%  |

#### Interferência com Shannon-Hartley

Fórmula exibida: `C = B·log₂(1 + SINR)`, B = 100 MHz; `SINR = C_signal / (N₀ + I)`.

| Nível | C/I    | SINR   | C_max      | Delay | Loss |
|-------|--------|--------|------------|-------|------|
| Fraca | > 20dB | 20 dB  | ~665 Mbps  | 5 ms  | 1%   |
| Média | ≈ 15dB | 15 dB  | ~498 Mbps  | 20 ms | 5%   |
| Alta  | < 10dB | 10 dB  | ~207 Mbps  | 50 ms | 15%  |

#### `server/scripts/test_channel.sh` (novo, substitui test_distance.sh + test_interference.sh para o UE Lab)

Combina distância e interferência em um único `tc qdisc replace`:
- Delay total: `D_delay + I_delay` ms.
- Loss total (probabilidades independentes): `D + I − D·I/100` %.
- Parâmetros: `./test_channel.sh <distance> <interference>` (ex.: `1km fraca`).

#### Card de resultado em evidência

Após rodar throughput: card fixo abaixo dos botões exibe banda em 32px bold
+ condições aplicadas (distância/interferência em vigor). Parse do iperf3:
`/(\d+\.?\d*)\s+(M|G|K)bits\/sec\s+(sender|receiver)/i`.

#### Colorização de logs (fix)

- `stripAnsi(s)` remove sequências ANSI (`\x1b[[0-9;]*[mGKJHFABCDSTlu]`)
  antes de colorir e antes de exibir — necessário porque `add-subscriber.sh`
  e mongosh emitem `\033[0;32m` que aparecia como texto literal no painel.
- Paleta aplicada ao console principal e ao console do UE Lab:
  - `FATAL/CRIT/EMERG/ALERT` → `var(--red)`
  - `ERROR` → `var(--red)`
  - `WARN(ING)` → `var(--yellow)`
  - `DEBUG/TRACE` → `#5a6170`
  - `INFO/NOTICE/NOTI` → `#4dabf7`
  - Demais → `var(--text)` (branco)

#### `POST /api/channel` (novo endpoint)

Recebe `{distance, interference}` JSON; valida contra listas permitidas;
chama `test_channel.sh distance interference`; streama saída. Bloqueado
para guest (403).

---

## [0.5.0] — 2026-06-19

### Painel — modal de UE, action bar, versionamento

- **Modal de cadastro de UE**: formulário migrado da sidebar para um modal
  centralizado (`+ Cadastrar UE` na action bar). Cada campo tem label,
  ajuda técnica em terminologia de telecomunicações (IMSI, MSISDN, Ki,
  OPc, AMF 3GPP TS 33.102) e botão **Sugerir** que gera um valor válido
  aleatório via `crypto.getRandomValues` (IMSI: MCC 001 + MNC 01 + MSIN
  aleatório de 10 dígitos; K/OPc: 128 bits hex; AMF: `8000`).
- **Action bar**: faixa horizontal entre a telemetria e o `<main>`,
  reservada para botões de ação globais. Primeiro botão: `+ Cadastrar UE`.
  Cresce com futuros botões sem poluir a sidebar.
- **Versão no rodapé**: `GET /api/version` lê `server/panel/VERSION`
  e retorna `{"version": "0.5.0"}`; o rodapé exibe
  `Core5G_ARM64 vX.Y.Z · Grupo 6 — UE-TP-rApp · CESAR School`.
- **`server/panel/VERSION`**: arquivo de texto com a versão atual
  (`0.5.0`), lido uma vez no startup do servidor.

---

## [0.1.0 → 0.4.0] — 2026-06-18 / 2026-06-19

## 2026-06-18

### Repositório local

- Replicado o conteúdo de `ric/code/open5gs-containerized` (repo
  `jakunzler/cesar-school-repo`) direto na raiz do projeto, sem pasta wrapper:
  `docker-compose.yml`, `.env`, `.env.example`, `configs/`, `scripts/`, `ueransim/`,
  `overrides/`, `logs/`, `README.md` + os `.md` de `docs/labs`.
- Replicado `ric/code/oai-cn-gnb-e2` em subpasta própria `oai-cn-gnb-e2/` (não
  flatten na raiz) porque colide em nome com o projeto anterior em `docs/`,
  `logs/`, `scripts/`, `ueransim/` e em arquivos como `up_core.sh`,
  `down_core.sh`, `fix-line-endings.sh`, `docker-compose.yaml`.
- Lidos os PDFs em `pdfs/` (slides das aulas 01–04 + planilha de grupos) para
  identificar o que precisa ser entregue:
  - Grupo do usuário (Henrique, Klinger, Kelvin, Gilberto) — tema **UE-TP-rApp**.
  - Projeto 1 (40%) — apresentado em 13/06/2026 (Aula 03), já concluído.
  - Projeto 2 (40%) — implementar `oai-cn-gnb-e2` conforme
    `oai-cn-gnb-e2/docs/E2_FLEXRIC.md`, entrega em 20/06/2026 (Aula 06).
    Rubrica/plano de testes oficiais ainda não publicados no repositório de
    origem no momento da leitura.
- Documentado blueprint do painel explicativo/observabilidade em
  `docs/blueprint-painel-observabilidade.md` (logs+métricas via
  Loki/Prometheus/Grafana, e camada de fluxo de protocolo E2/NGAP/GTP-U via
  sensor + topologia interativa). Nenhum código implementado ainda — só desenho.

### Configuração (`.env` / `.env.example`)

- Adicionadas variáveis de acesso ao servidor ARM AWS: `AWS_SERVER_HOST`,
  `AWS_SERVER_USER=ubuntu`, `AWS_SSH_KEY_PATH=./ssl/core5g_openran_arm64.pem`.
- Adicionadas variáveis do DuckDNS: `DUCKDNS_DOMAIN=core5g-arm64`,
  `DUCKDNS_TOKEN` (valor real só no `.env`, não no `.env.example`).
- `AWS_SERVER_HOST` migrado do IP fixo `3.145.40.200` para o hostname DDNS
  `core5g-arm64.duckdns.org`.

### Servidor ARM AWS (`3.145.40.200` → `core5g-arm64.duckdns.org`)

Specs identificadas: Ubuntu 24.04.4 LTS, kernel 6.17 aarch64, **2 vCPUs, 906 MiB
de RAM**, 29 GB de disco (26 GB livres antes das instalações). RAM é baixa para
o que está planejado (Open5GS + OAI/FlexRIC + observabilidade) — acompanhar de
perto, considerar upgrade de instância se houver OOM kill.

- **DuckDNS**: instalado `~/duckdns/duck.sh` (script oficial) + cron a cada
  5 min (`*/5 * * * * /home/ubuntu/duckdns/duck.sh`) para manter
  `core5g-arm64.duckdns.org` atualizado com o IP dinâmico da instância.
- **Docker**: instalado via repositório oficial Docker (não o pacote `docker.io`
  do Ubuntu) — `docker-ce`, `docker-ce-cli`, `containerd.io`,
  `docker-buildx-plugin`, `docker-compose-plugin`. Usuário `ubuntu` adicionado
  ao grupo `docker`. Serviço habilitado e testado com `docker run hello-world`.
- **Utilitários**: `make`, `unzip` instalados (`git`, `curl`, `jq` já vinham na
  imagem).
- **Swap**: criado `/swapfile` de 8 GB, persistido em `/etc/fstab`,
  `vm.swappiness=10` (prioriza RAM real, swap só como rede de segurança contra
  OOM kill). Disco após tudo: 11 GB usados, 18 GB livres.

### Deploy do Projeto 1 (Open5GS core) no servidor — teste de carga

- Transferidos `docker-compose.yml`, `.env`, `configs/`, `scripts/`, `overrides/`,
  `ueransim/` para `~/open5gs-containerized` no servidor via `rsync`.
- **Bug encontrado**: `gradiant/open5gs:2.7.6` e `gradiant/open5gs-webui:2.7.6`
  não têm manifest `linux/arm64/v8` (a gradiant só publica `amd64` a partir da
  2.7.3). `docker compose up` falhava com
  `no matching manifest for linux/arm64/v8`.
- **Correção**: `.env` e `.env.example` atualizados para
  `OPEN5GS_IMAGE=gradiant/open5gs:2.7.2` e
  `WEBUI_IMAGE=gradiant/open5gs-webui:2.7.2` (variável `WEBUI_IMAGE` nova,
  consumida pelo `docker-compose.yml` na linha do serviço `webui`) — últimas
  tags com build arm64 confirmado via Docker Hub API. `mongo:7.0` e
  `gradiant/ueransim:3.2.6` já eram arm64-ok, sem mudança.
- **Resultado**: `./scripts/up_core.sh` trouxe os 14 containers do core
  (`mongodb`, `nrf`, `scp`, `amf`, `smf`, `ausf`, `udm`, `udr`, `pcf`, `nssf`,
  `upf-a`, `upf-b`, `dn`, `webui`) todos `healthy`.
- **Uso de recursos** (`docker stats`, sistema ocioso): ~277 MiB de RAM somando
  todos os containers (MongoDB é o mais pesado, 141 MiB; WebUI 52 MiB; NFs
  individuais entre 2–9 MiB cada). Memória do host: 487Mi/906Mi usada, só
  303 MiB de swap consumido. CPU ~0% em todos os containers parados/idle.
  Conclusão: o core do Open5GS é leve o suficiente pra essa instância pequena.
- `./scripts/healthcheck.sh` confirmou: NRF healthy, N4 (SMF↔UPF-A/B) ok, N6
  (UPF↔DN) ok, associação PFCP estabelecida com 2 UPFs. Falhas esperadas em
  N2/N3 e "UE não está rodando" porque o RAN (UERANSIM) ainda não foi iniciado
  nesta rodada — só o core.

### Teste end-to-end (RAN + UE) — bug de BSF ausente encontrado e corrigido

- `./scripts/add-subscriber.sh` executado (IMSI `001010000000002`).
- `./scripts/up_ran.sh` subiu `ueransim` (gNB simulado + UE) sem erro, mas a
  interface `uesimtun0` nunca apareceu.
- **Bug encontrado**: log do UE mostrava
  `PDU Session Establishment Reject [OUT_OF_LADN_SERVICE_AREA]` após registro
  NAS bem-sucedido. Causa raiz (log do PCF): `No http.location` em
  `nbsf-handler.c:436` — o PCF tenta registrar o binding da sessão na **BSF**
  (Binding Support Function) via NRF, mas **não havia serviço `bsf` no
  `docker-compose.yml`**, apesar do binário `open5gs-bsfd` existir na imagem e
  de já existir um `configs/open5gs/bsf.yaml` no projeto original — só que
  com o endereço de exemplo padrão (`127.0.0.15`), fora do esquema de rede
  real do projeto (`10.10.0.x` em `net-sbi`). Item esquecido na configuração
  original do projeto, não causado pela troca de versão de imagem.
- **Correção**:
  - `configs/open5gs/bsf.yaml`: endereço SBI corrigido de `127.0.0.15` para
    `10.10.0.18` (próximo IP livre na faixa `net-sbi`), client `scp` apontado
    para `10.10.0.200:7777` (igual aos demais NFs).
  - `docker-compose.yml`: novo serviço `bsf` adicionado (mesmo padrão do
    `nssf`), container `open5gs-bsf-containerized`, healthcheck por
    `pgrep open5gs-bsfd`.
- Depois de subir o `bsf` e reiniciar `amf`, `smf`, `pcf` (havia estado órfão
  de sessão de tentativas anteriores causando um segundo erro,
  `Registration reject [95]` / `amf_npcf_am_policy_control_handle_create()
  failed` — resolvido com restart limpo de todos os NFs do core), o UE
  registrou e abriu sessão PDU com sucesso:
  `TUN interface[uesimtun0, 10.60.0.2] is up`.
- **Validação final**: `ping -I uesimtun0 8.8.8.8` — 4/4 pacotes, 0% perda,
  RTT ~10ms. Cadeia completa validada: UE → gNB (UERANSIM) → AMF/SMF (N1/N2)
  → PCF/BSF (policy) → UPF (N3/N4) → DN → internet real (N6/NAT).
- Uso de recursos com core + RAN completos rodando: 492Mi/906Mi RAM, 342MiB
  de swap, CPU de cada container abaixo de 2% (MongoDB o mais pesado, ~13%
  de um core). Instância pequena sustenta o Projeto 1 completo com folga.

### Pendências conhecidas

- Rubrica e plano de testes do Projeto 2 (`docs/avaliacao_seminario_aula06.md`,
  `docs/labs/04-projeto2-plano-testes.md` etc.) ainda não estavam publicados no
  repositório de origem — confirmar com o professor.
- Blueprint do painel de observabilidade documentado mas não implementado
  (fases 1–5 em `docs/blueprint-painel-observabilidade.md`).
- RAM da instância (906 MiB): validado que o Projeto 1 completo (core + RAN)
  roda confortavelmente (~492 MiB usados, 342 MiB de swap). Risco real
  permanece para o Projeto 2 (build do OAI a partir do source é
  CPU/RAM-intensivo) — testar e medir antes de assumir que cabe igual.
- Os fixes de `bsf.yaml`/`docker-compose.yml` (serviço BSF) existem só
  localmente neste projeto — não foram enviados de volta ao repositório de
  origem (`jakunzler/cesar-school-repo`). Avaliar se vale reportar ao
  professor, já que outros grupos usando o mesmo material provavelmente vão
  bater no mesmo erro.
- **Abrir portas 80 e 443 (TCP, origem 0.0.0.0/0) no Security Group da
  instância EC2** — sem isso, o Caddy nunca consegue emitir o certificado
  Let's Encrypt nem servir HTTPS externamente, mesmo já estando ativo e
  configurado corretamente no servidor. Porta 8765 (uvicorn) não deve ser
  aberta — só é usada internamente via `127.0.0.1` pelo Caddy. Passo a
  passo: console AWS → EC2 → Instances → selecionar a instância → aba
  "Security" → clicar no Security Group → "Edit inbound rules" → "Add rule"
  duas vezes (HTTP/80 e HTTPS/443, source "Anywhere-IPv4") → Save rules.
  Não há acesso a AWS CLI/credenciais configurados localmente para fazer
  isso via terminal.

### Reorganização: workflow "local → deploy.sh" + pasta `server/`

A partir de agora, mudanças no servidor passam a ser feitas só através de
`deploy.sh` — nada mais de comandos `ssh`/`rsync` ad-hoc direto no servidor.

Primeira versão manteve o Projeto 1 na raiz; revisado depois para um desenho
mais explícito: **`server/`** passa a conter tudo que de fato é
replicado/roda na máquina AWS (Projeto 1 + Projeto 2), separado da raiz
(orquestração) e de `docs/` (documentação).

- **`server/`** (novo): `docker-compose.yml`, `.env`/`.env.example`
  (só variáveis de imagem — `OPEN5GS_IMAGE`, `WEBUI_IMAGE` etc., sem
  segredos), `configs/`, `scripts/`, `overrides/`, `ueransim/`, `logs/` e
  `oai-cn-gnb-e2/` (Projeto 2, movido pra dentro). Tudo migrado com `mv`
  preservando histórico de edição.
- **`.env`/`.env.example` da raiz**: agora só credenciais/host de deploy
  (`AWS_SERVER_HOST`, `AWS_SERVER_USER`, `AWS_SSH_KEY_PATH`,
  `DUCKDNS_DOMAIN`, `DUCKDNS_TOKEN`) — nunca são enviadas ao servidor.
- **`docker-compose.yml`**: adicionado `name: open5gs-containerized` no topo
  do arquivo. Sem isso, mover o diretório (`open5gs-containerized` →
  `server`) teria recriado os volumes nomeados do Mongo
  (`mongodb-data`/`mongodb-config`, sem `name:` explícito) do zero, perdendo
  o subscriber cadastrado — as redes (`net-n2`, `net-n3` etc.) já tinham
  `name:` fixo e não seriam afetadas, mas os volumes não.
- **`infra/server-bootstrap.sh`** (novo): captura como código idempotente
  tudo que foi feito manualmente via SSH até aqui — instalar Docker
  (repo oficial), criar swap de 8G, instalar/configurar o cron do DuckDNS.
  Recebe `DUCKDNS_DOMAIN`, `DUCKDNS_TOKEN`, `SWAP_SIZE_GB`, `SWAPPINESS` como
  variáveis de ambiente.
- **`deploy.sh`** (novo, raiz): único entrypoint de deploy. Lê
  `AWS_SERVER_HOST`/`AWS_SERVER_USER`/`AWS_SSH_KEY_PATH` do `.env` (raiz).
  Subcomandos: `bootstrap`, `sync`, `sync-oai` (Projeto 2, ~230MB, sob
  demanda — não entra no `sync` normal), `up [core|ran|all]`,
  `down [core|ran|all]`, `status`, `ssh`.
- **Migração no servidor**: stack antigo parado em `~/open5gs-containerized`
  (`docker compose down` no core e no RAN), novo stack subido em `~/server`
  via `./deploy.sh up core` + `./deploy.sh up ran`. Confirmado que o
  subscriber sobreviveu à troca de diretório (graças ao `name:` fixo) — UE
  registrou direto, sem precisar rodar `add-subscriber.sh` de novo. IP
  `10.60.0.2`, conectividade ativa. Diretório antigo removido do servidor
  (`sudo rm -rf ~/open5gs-containerized`, alguns logs eram `root`-owned).
- Lição aprendida: usar sempre `$AWS_SERVER_HOST` (hostname DuckDNS) nos
  comandos, nunca o IP fixo `3.145.40.200` direto — o IP é dinâmico por
  definição, hardcodar ele de volta anula o propósito do DDNS.

### `core5g-arm64-bible.md` (novo)

Documento de referência único consolidando contexto da disciplina, estrutura
do repo, specs do servidor, workflow de deploy, explicação de cada NF
(Open5GS e OAI+FlexRIC), os 3 bugs encontrados/corrigidos (§7.1–7.3 do
documento) e estado de validação. Complementa o `CHANGELOG.md` (que é
cronológico) com uma "fotografia" consolidada do projeto.

### `client/` — painel de controle web local (novo)

UI local (não roda no servidor) pra disparar `deploy.sh` com botões em vez
de terminal, com saída em tempo real.

- **Stack**: backend `FastAPI` (`client/server.py`) + frontend estático
  (`client/static/index.html`, HTML/CSS/JS puro, sem build step). Decisão
  consciente: o backend só faz `subprocess.Popen` do `deploy.sh` e streama
  stdout/stderr — nenhuma lógica de SSH/rsync duplicada, `deploy.sh`
  continua a única fonte de verdade.
- **Comandos expostos** (mapa fixo em `COMMANDS`, sem string livre vinda do
  cliente): bootstrap, sync, sync-oai, up core/ran/all, down core/ran/all,
  status.
- **Streaming**: `POST /api/run/{command}` retorna `StreamingResponse`
  (`text/plain`), front-end lê via `fetch` + `ReadableStream` e escreve no
  console conforme chega — sem esperar o comando terminar.
- Bind em `127.0.0.1` apenas (sem exposição de rede, sem auth — uso local).
- `client/run.sh`: cria venv, instala `fastapi`+`uvicorn`, sobe em
  `http://127.0.0.1:8765`.
- Testado de ponta a ponta: servidor local respondeu HTTP 200, e
  `POST /api/run/status` streamou a saída real do `deploy.sh status`
  (healthcheck do servidor AWS) até o fim, com `exit code 0`.

### `server/panel/` — painel web no PRÓPRIO SERVIDOR, com HTTPS + login (novo)

Diferente do `client/` (roda no laptop, fala com o servidor via SSH), este
painel roda direto na instância AWS e executa os scripts locais
(`./scripts/up.sh`, `up_ran.sh`, `down_core.sh`, `down_ran.sh`,
`healthcheck.sh`) sem precisar de SSH.

- **`server/panel/server.py`**: FastAPI, sem autenticação própria — quem
  autentica é o Caddy na frente (bind em `127.0.0.1:8765`, nunca exposto
  direto). Endpoint `/api/whoami` expõe o usuário autenticado (lido do header
  `X-Remote-User`, injetado pelo Caddy) e seu papel (`admin`/`guest`).
  `/api/run/{command}` recusa com HTTP 403 qualquer requisição do usuário
  guest — checagem feita no backend, não só escondendo botão no front-end.
- **`server/panel/static/index.html`**: mesma UI do `client/`, mas sem os
  botões `sync`/`sync-oai`/`bootstrap` (esses só fazem sentido rodando do
  laptop). Mostra o usuário logado no header e, se for guest, exibe um
  banner laranja "modo somente leitura" e desabilita todos os botões.
- **Credenciais** (`.env` da raiz, nunca enviadas ao servidor em texto
  puro — só usadas localmente para gerar os hashes bcrypt do Caddyfile):
  `PANEL_USER`/`PANEL_PASSWORD` (acesso total) e
  `PANEL_GUEST_USER`/`PANEL_GUEST_PASSWORD` (somente leitura, não executa
  nenhum comando).
- **HTTPS**: via Caddy (`infra/server-bootstrap.sh`, etapas 4/5 e 5/5),
  instalado pelo repositório oficial Cloudsmith. Caddy gera automaticamente
  um certificado Let's Encrypt para `core5g-arm64.duckdns.org` (sem custo,
  sem instalação manual de certificado) — só funciona com as portas 80/443
  abertas no Security Group da instância (porta 80 é usada pelo desafio
  ACME HTTP-01; porta 443 é o HTTPS em si). A porta 8765 (FastAPI/Uvicorn)
  nunca é exposta para fora, só `127.0.0.1`.
- **Caddyfile** gerado dinamicamente pelo bootstrap (hash bcrypt calculado
  via `caddy hash-password`, nunca grava senha em texto puro no servidor):
  `basic_auth` com os dois usuários, `reverse_proxy 127.0.0.1:8765` injetando
  `header_up X-Remote-User {http.auth.user.id}` pro FastAPI saber quem
  autenticou.
- **`infra/core5g-panel.service`** (novo): unit systemd
  (`Restart=always`, `User=ubuntu`), sobe `uvicorn` a partir do venv do
  painel. Placeholder `__PANEL_GUEST_USER__` substituído via `sed` no
  bootstrap antes de instalar em `/etc/systemd/system/`.
- **`deploy.sh panel`** (novo subcomando): sincroniza `server/panel/` e
  roda o bootstrap (idempotente) para atualizar Caddy/venv/systemd.
- **Bug corrigido durante o deploy**: primeira tentativa de criar o venv
  falhou silenciosamente sem `pip` (`ensurepip` indisponível porque
  `python3-venv` ainda não estava instalado no momento da checagem
  `[ ! -x .venv/bin/python3 ]` — o symlink `python3` já existia de uma
  tentativa anterior, então o script pulava a recriação do venv mesmo
  quebrado). Corrigido instalando `python3-venv`/`python3-pip` sempre
  (idempotente via apt) antes de checar/recriar o venv.
- **Validado no servidor**: `systemctl is-active core5g-panel caddy` → 
  `active`/`active`; `curl 127.0.0.1:8765/` → HTTP 200. **Pendente**: acesso
  externo via `https://core5g-arm64.duckdns.org/` deu timeout — Security
  Group da instância ainda não libera as portas 80/443 (só SSH/22 hoje).
  Sem acesso à AWS CLI/console por aqui; usuário precisa abrir manualmente
  (ver pendências).

## [0.3.0 → 0.4.0] — 2026-06-19

### Portas 80/443 abertas no Security Group — painel validado fim a fim

Usuário abriu manualmente as portas no console AWS. Testado de fora:
HTTP 308 (redirect pra HTTPS), HTTPS 401 sem credencial, HTTPS 200 com
`hcarmine`/`guest`, e `POST /api/run/status` com guest devolvendo 403 como
esperado. Certificado Let's Encrypt emitido automaticamente pelo Caddy
(sem nenhuma instalação manual de certificado).

### `core5g-arm64-bible.md` — seção para leigos

Adicionada nova seção (logo após o contexto da disciplina) explicando cada
container Docker do Projeto 1 com analogia de "empresa de entregas" —
AMF/recepção, AUSF/segurança, UPF/caminhão de entrega, etc. — e o painel
(Caddy/porteiro + FastAPI/escritório dos botões). Seções seguintes
renumeradas (3–11).

### `server/panel/` — telemetria em tempo real + filtro de logs por serviço

Primeiros dois itens de um pedido maior do usuário (telemetria, logs,
cadastro de UE com identidade visual própria, ferramentas de teste de
banda/interferência/distância — ver pendências). Decisão consciente: nada
de Prometheus/Grafana/Loki por agora — a instância tem só 906 MiB de RAM e
já está ocupada com o core 5G; tudo implementado só com a stack que já
existe (FastAPI + JS puro), sem dependência nova.

- **`server/panel/server.py`**:
  - `list_services()`: descobre os serviços dos dois `docker-compose`
    (core + `ueransim/`) chamando `docker compose config --services` em
    runtime, em vez de manter uma lista hardcoded que ficaria
    desatualizada se o compose mudar.
  - `GET /api/services`: lista os serviços disponíveis pra UI montar o
    seletor.
  - `GET /api/logs/{service}`: `docker compose logs -f --tail 200
    <service>` streamado (reaproveita `stream_command`, já usado pros
    botões up/down). Liberado pra **admin e guest** — é leitura, não
    execução, então não passa pela checagem de 403 do `/api/run/*`.
  - `GET /api/telemetry`: stream infinito (NDJSON, uma linha de JSON a
    cada 2s) com métricas do host (`/proc/meminfo` pra RAM/swap,
    `shutil.disk_usage` pra disco, `os.getloadavg()` pra load) e por
    container (`docker stats --no-stream --format '{{json .}}'`, CPU% e
    uso de RAM). Também liberado pra guest.
- **`server/panel/static/index.html`**:
  - Faixa de telemetria abaixo do header (barras de RAM/swap/disco + load
    avg), atualizada via `fetch` + `ReadableStream` lendo NDJSON (mesmo
    padrão de streaming já usado nos comandos, sem `EventSource`/SSE
    nativo pra não introduzir um segundo jeito de consumir stream no
    mesmo arquivo).
  - `<details>` colapsável com tabela de containers (nome/CPU/RAM).
  - Novo grupo "Logs" na barra lateral: `<select>` com os serviços (via
    `/api/services`) + botão "Ver logs" (inicia streaming no console,
    usando `AbortController` pra poder parar — diferente dos botões de
    comando, que terminam sozinhos, `logs -f` nunca termina por conta
    própria) + botão "Parar logs".
  - Telemetria e logs ficam **fora** do grupo de botões `data-cmd`
    (`buttons[data-cmd]`) de propósito: o guest pode usá-los livremente,
    só os comandos de `/api/run/*` ficam bloqueados pra esse usuário.
- Validado em produção: `/api/services` retornou os 16 serviços reais
  (15 NFs + `ueransim`), `/api/telemetry` retornou métricas reais (RAM
  58%, 16 containers com CPU/RAM individual), `/api/logs/amf` streamou
  log real do container.

### `server/panel/` — cadastro de UE + ferramentas de teste (throughput/interferência/distância)

- **Cadastro de UE** (`POST /api/subscriber`): formulário no painel
  (IMSI obrigatório + MSISDN/K/OPc/AMF opcionais) chamando
  `add-subscriber.sh`, que ganhou overrides via env var (`SUB_IMSI`,
  `SUB_K`, `SUB_OPC`, `SUB_MSISDN`, `SUB_AMF`) sem quebrar o uso direto
  documentado nos labs (sem env vars, mantém o subscriber de teste
  padrão). Validação: IMSI 6–15 dígitos, K/OPc 32 hex. Texto de ajuda
  abaixo de cada campo, explicando em linguagem simples.
- **Throughput** (`./scripts/test_throughput.sh`, botão "Throughput
  (iperf3)"): mede a banda real atravessando o túnel 5G de verdade
  (UE → gNB → UPF → DN via `uesimtun0`), não o bridge direto do Docker.
  Conecta direto com o tema do grupo (UE-TP-rApp — previsão de
  throughput por UE). Precisou adicionar `iperf3` ao `apk add` do
  container `dn` em `docker-compose.yml` (já instalava `iproute2` e
  outras ferramentas de rede no startup, só faltava o iperf3).
- **Interferência** (`./scripts/test_interference.sh on|off`): injeta
  perda/atraso artificial em `uesimtun0` via `tc netem` (UERANSIM já
  vem com `iperf3` e `tc` pré-instalados na imagem, Ubuntu 22.04 —
  confirmado por inspeção do container antes de implementar). Como
  UERANSIM não modela RF real, este é o substituto prático assumido
  desde a sugestão original.
- **Distância relativa** (`./scripts/test_distance.sh
  perto|medio|longe|off`): mesmo mecanismo do `netem`, com perfis
  prontos (perto: 0%/5ms, médio: 3%/40ms, longe: 10%/120ms) simulando o
  efeito de afastar o UE da antena — substituto honesto pra path-loss
  real, que exigiria múltiplas células configuradas (fora de escopo).
- Todos os três comandos novos passam pela mesma checagem de guest
  (403 em `/api/run/*`) — só admin pode rodar.
- **Validado em produção** (core+RAN subidos via o próprio painel,
  `POST /api/run/up-all`): throughput baseline ~168 Mbits/s; com
  interferência ativa caiu para ~1.87 Mbits/s (queda de ~90x); perfil
  "longe" aplicou corretamente perda 10%/atraso 120ms.
