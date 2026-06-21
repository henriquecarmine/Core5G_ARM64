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
| 0.9.0  | 2026-06-19 | `build-oai-arm64.sh` — script de build OAI arm64 + Bugs 1-3 corrigidos     |
| 0.10.0 | 2026-06-19 | 6 imagens OAI arm64 concluídas (Bugs 4-5), deployed no servidor AWS         |
| 0.11.0 | 2026-06-19 | Tela de login + topologia interativa + seletor de projeto + estabilidade da instância + README |
| 0.11.1 | 2026-06-19 | Fix: interferência/distância (P1) agora afetam a medição + resumo no throughput |
| 0.12.0 | 2026-06-19 | Colorimetria ISO/ANSI + resumo didático em TODOS os testes; fixes (canal, failover, anti-freeze KPM/RC) |
| 0.12.1 | 2026-06-19 | Testes agrupados por projeto no menu + bloqueio mútuo (só o projeto ativo testa) |
| 0.12.2 | 2026-06-20 | Plano de usuário arm64 (OAI v2.2.1) + xApps event-driven (run_xapp/e2_verify/up_e2_lab_v2) |
| 0.12.3 | 2026-06-20 | Trava de auth: guest vira opt-in (`.env` em branco ⇒ só admin/hcarmine entra) |
| 0.12.4 | 2026-06-20 | xApps validados (cust/kpm 7/7, rc 5/7): fix plugins arch-aware + falso-negativo do run_xapp |
| 0.13.0 | 2026-06-20 | Redesenho do painel: menu superior único (projeto ativo, seletor, ferramentas, telemetria) + sidebar lateral colapsável (hover-expand) por lab |
| 0.14.0 | 2026-06-20 | Fix v2 do ativar/desligar (P2) + reorganização: projetos+servidores no topo, ferramentas POR PROJETO na lateral, guarda de dependência (RAN só com Core) |
| 0.15.0 | 2026-06-20 | Testes do roteiro do professor (NG Setup/Registro/Coerência no P1 + KPM com tráfego no P2) + topologia POR PROJETO (cria a do P1 Open5GS) |
| 0.15.1 | 2026-06-20 | Guardrails de CPU (cgroup v2): lab limitado a 90% dos 2 vcores + ssh/docker/painel/caddy com prioridade máxima — o SSH não cai mais sob carga |
| 0.15.2 | 2026-06-20 | Guardrail definitivo via **cpuset**: lab fixado fora do CPU 0 (reservado p/ sistema). Painel ~600ms e SSH ~2.5s mesmo com gNB+nrUE no talo |
| 0.16.0 | 2026-06-20 | Loader em toda ação (barra global no topo + spinner por botão) + teste de fumaça visual headless |
| 0.16.1 | 2026-06-20 | Topo mais compacto: "Containers" inline antes dos monitores; cards de projeto mais baixos; "Desligar tudo" virou o botão do card ativo (≈3 linhas ganhas) |
| 0.16.2 | 2026-06-20 | Descrição curta de cada projeto ao lado do nome (P1: rede 5G fim-a-fim; P2: O-RAN RIC+xApps) |
| 0.17.0 | 2026-06-20 | Logs coloridos ISO (por token, nada em branco) + explicação didática no fim de cada log; fix v1→v2 (logs do P2 saíam vazios); snapshot finito por container |
| 0.17.1 | 2026-06-20 | Link "Ver logs do resultado" no fim dos testes que produzem logs (KPM/RC/conexão/registro): atalho clicável abre o log relevante (gNB/RIC/AMF/SMF/UPF/UERANSIM) |
| 0.18.0 | 2026-06-20 | Topologia revalidada: rótulos de interface na camada de topo (nunca mais atrás dos cards) + layout do P1 reorganizado sem sobreposição + legenda virou badge minimalista recolhível no canto inferior esquerdo (P1 e P2) |
| 0.19.0 | 2026-06-20 | Modo sala de aula: 1 Professor por vez (bloqueia 2º admin, libera após 30s idle) + Alunos acompanham AO VIVO o console do Professor (espelho por ring-buffer/polling) + banner "🔴 AO VIVO" + contagem de espectadores + papéis Professor/Aluno |
| 0.20.0 | 2026-06-20 | Resultados persistentes + Replay: cada execução do Professor é salva em disco (`server/panel_results/`) e some no restart nunca mais; aba "Resultados salvos" (Professor e Aluno) lista tudo e **reproduz** a execução com timing. Fase 2 do modo sala de aula |
| 0.21.0 | 2026-06-20 | RAN ao vivo (P2): faixa de sparklines com SNR/MCS/PRB/BLER reais do gNB OAI (PHY/MAC do UE), atualizando a cada 1,5s; aparece só com o Projeto 2 no ar e é espelhada pros Alunos (ambos consultam `/api/topology/gnb-stats`) |
| 0.21.1 | 2026-06-20 | Hardening da vaga de Professor: posse "pegajosa" — só libera por logout (ou após 10min de abandono, válvula de segurança); posse por sid, não cai por soluço de rede. Protege a aula de um aluno assumir numa janela curta |
| 0.22.0 | 2026-06-20 | Telemetria escala p/ a sala de aula: coletor ÚNICO em background + cache (antes cada aluno abria um stream e rodava `docker stats` a cada 2s — 30 alunos derrubariam o box de 2 vCPU). Agora N alunos custam o mesmo que 1. gnb-stats também cacheado |
| 0.23.0 | 2026-06-20 | Aluno identificado: entra com Nome + E-mail (1 passo, sem senha). Identidade assinada no cookie + roster de presença persistente; Professor vê "Alunos conectados" (nome+email) e a presença acumulada clicando no badge 👁 |
| 0.24.0 | 2026-06-20 | Modo projeção (kiosk): botão "⛶ Projeção" abre uma tela limpa em fullscreen pro datashow — RAN ao vivo grande, console em fonte grande, header enxuto (projeto + nº de alunos), sem sidebar/controles. Esc sai |
| 0.24.1 | 2026-06-20 | Onboarding de colaboradores: README atualizado (modo sala de aula, guardrail cpuset, usuários), `CONTRIBUTING.md`, modelos de Issue/PR (`.github/`), e **tags git** de toda a história do painel (v0.12.2 → v0.24.x). Issues + Discussions habilitados no GitHub |
| 0.24.2 | 2026-06-20 | Créditos/Equipe (Prof. Jonas · Henrique · Klinger · Kelvin) no README e nos rodapés do painel; remove o rótulo "Grupo 6"; adiciona a **licença MIT** |

---

## [0.24.2] — 2026-06-20

**Equipe + licença.**

- **Créditos:** seção "Equipe" no README e rodapés do painel (login + principal)
  passam a creditar **Prof. Jonas** (orientador), **Henrique Carmine** (autor/
  mantenedor) e os colaboradores **Klinger** e **Kelvin**. Removido o rótulo
  genérico "Grupo 6".
- **Licença:** adicionada a **MIT** (`LICENSE`), com copyright dos autores e
  menção à orientação. Referenciada no README.

---

## [0.24.1] — 2026-06-20

**Documentação de onboarding + espaço de colaboração + versionamento.**

- **README** atualizado para o estado atual: seção "modo sala de aula"
  (Professor/Aluno, um por vez, espelho ao vivo, Resultados+Replay, RAN ao vivo,
  projeção), correção do guardrail de CPU (é **cpuset**, não CPUQuota) e dos
  usuários (`professor`, sem `grupo6`).
- **`CONTRIBUTING.md`** — guia passo a passo de como colaborar (Issues /
  Discussions / Pull Request), como validar antes do PR, convenção de commit,
  versionamento (SemVer) e regras de ouro (segredos, dados de aluno, box 2 vCPU).
- **`.github/`** — modelos de Issue (bug / ideia) e de Pull Request.
- **Versionamento:** criadas **tags git anotadas** de toda a era do painel
  (`v0.12.2` … `v0.24.x`) — agora cada release tem seu ponto no histórico.
- **GitHub:** abas **Issues** e **Discussions** habilitadas como espaço de
  colaboração; contato em `hc@cesar.school`.

---

## [0.24.0] — 2026-06-20

**Modo projeção (kiosk) — tela limpa pro datashow.** Botão **"⛶ Projeção"** no
topo entra em **fullscreen** com uma vista de apresentação, legível do fundo da
sala:

- Esconde sidebar, cards de projeto e controles; mantém só o essencial — header
  enxuto (título + projeto ativo + **nº de alunos**), linha de saúde do box
  (CPU/RAM/Swap/Disk), a faixa **RAN ao vivo** ampliada (valores grandes +
  sparklines maiores) e o **console em fonte grande** (17px).
- Usa `requestFullscreen`; sai por **Esc**, pelo botão flutuante "✕ Sair da
  projeção" ou ao sair do fullscreen pelo navegador (sincronizado).
- É só uma camada de CSS sobre o painel — continua tudo ao vivo (console
  espelhado, RAN, telemetria); ideal para projetar a aula.

Fecha a sequência de melhorias do modo sala de aula (Resultados+Replay, RAN ao
vivo, hardening da vaga, telemetria escalável, aluno identificado, projeção).

---

## [0.23.0] — 2026-06-20

**Aluno identificado (controle unitário da turma).** O acesso de aluno deixou de
ser anônimo: agora pede **Nome + E-mail** (1 passo, sem senha) — o e-mail é a
chave única que filtra os curiosos e identifica quem é quem para atividades
futuras.

- **Login:** `/api/login/guest` recebe `{name, email}`, valida formato de e-mail
  (qualquer e-mail válido) e nome; a identidade vai **assinada no cookie**
  (sobrevive a restart). Papel continua Aluno (só-leitura).
- **Roster persistente:** cada entrada grava `{quando, nome, email}` em
  `panel_results/_roster.jsonl` (fora do git; é dado pessoal, fica só no
  servidor). `GET /api/roster` (só Professor) agrega por e-mail: quem entrou,
  quantas vezes, 1ª/última vez.
- **Lista ao vivo:** `GET /api/viewers` (só Professor) lista quem está assistindo
  agora (nome + e-mail). No painel, o badge **👁 N alunos** virou clicável e abre
  o modal "Alunos" com abas **Conectados agora** / **Presença (todos)**.
- Privacidade: e-mail nunca é exposto a outros alunos nem vai pro git — só o
  Professor vê.
- Validado: token com identidade (round-trip), regex de e-mail, viewers ao vivo
  e agregação do roster.

---

## [0.22.0] — 2026-06-20

**Telemetria que escala para a turma (não derruba o box de 2 vCPU).**

Resposta à pergunta "tem limite quando os alunos entram?": antes **não tinha**, e
era perigoso. O `/api/telemetry` era um **stream infinito por cliente** e, a cada
2s, **cada aluno** rodava `docker stats` (pesado) + `docker ps -a` no servidor e
**prendia uma thread** do pool (~40). Com 30 alunos: ~15 `docker stats`/s e ~30
conexões presas — saturava o box e matava o lab.

- **Coletor único em background:** uma thread (daemon) coleta host + containers +
  grupos a cada 2s e guarda em cache. `/api/telemetry` virou um **GET barato** que
  só devolve o último snapshot — **sem subprocess por cliente, sem thread presa**.
  Custo no servidor: **O(1), independente do nº de alunos**.
- **`/api/topology/gnb-stats` cacheado** (janela de 1,4s): N alunos pedindo o RAN
  ao vivo na mesma janela fazem **1 leitura de log** compartilhada, não N.
- Front: `startTelemetry` virou polling do GET cacheado (2,5s) em vez de ler um
  stream preso. `/api/live` já era O(1) (buffer em memória).
- Resultado: a sala de aula inteira só adiciona requisições leves (nível de ms);
  o trabalho pesado roda 1× a cada 2s, não 1× por aluno.

---

## [0.21.1] — 2026-06-20

**Hardening da vaga de Professor (segurança da aula).** A vaga de Professor único
ficou **pegajosa**, fechando a brecha em que um aluno poderia assumir o controle
numa janela curta de inatividade:

- Antes: a vaga liberava após 30s sem heartbeat — um aluno com senha de admin
  poderia assumir se o professor desse um soluço de rede. Agora a vaga **só libera
  por logout explícito**, ou após **10 min** sem heartbeat (válvula de segurança
  para o caso de o laptop morrer, evitando travar a vaga para sempre).
- A posse passou a valer por **sid** (não por "heartbeat recente"): o Professor
  ativo não perde o direito de executar por um soluço de rede no meio da demo.
  Ele só perde a vaga por logout, por reconexão própria (novo sid) ou por takeover
  após os 10 min.
- Mensagem de bloqueio (409) atualizada: sugere entrar como aluno OU pedir o
  logout do professor atual.
- Config: usuário `grupo6` removido; criado `professor` (admin). A trava garante
  hcarmine ⇄ professor: só um por vez.

---

## [0.21.0] — 2026-06-20

**RAN ao vivo — métricas PHY/MAC do gNB em sparklines.** Faixa nova abaixo dos
cards de projeto, visível **só quando o Projeto 2 está no ar** (gNB OAI ligado):
mostra **SNR, MCS, PRB e BLER** reais do UE simulado, em mini-gráficos coloridos
(ISO) que atualizam a cada 1,5s — a coleta sobe na tela em vez de só texto.

- Fonte: `/api/topology/gnb-stats` (já extraía PHY/MAC do log do gNB p/ a
  topologia); agora alimenta também a faixa do painel. Sparkline em SVG inline
  (sem libs), janela rolante de 40 amostras, área + linha por métrica.
- Auto-mirror: Professor e Aluno consultam o mesmo endpoint, então o aluno vê o
  mesmo gráfico ao vivo sem plumbing extra. Self-gating: só faz polling com
  `_activeProj === 'p2'`; some quando o gNB cai ou o UE ainda não conectou.
- Validado headless (faixa liga com P2 ativo, valores e sparklines renderizam).

---

## [0.20.0] — 2026-06-20

**Resultados persistentes + Replay (Fase 2 do modo sala de aula).**

- **Arquivo de Resultados.** Toda execução do Professor (testes, demos,
  throughput, troca de projeto, assinantes) é gravada em disco em
  `server/panel_results/<id>.json` (id por timestamp), com label, autor, duração,
  status e as linhas. Fica FORA da árvore sincronizada por `deploy.sh panel`, então
  **sobrevive a restart e a deploy**. Retenção: últimos 120, teto de 6000 linhas
  por resultado. Logs ao vivo NÃO são persistidos (são efêmeros por natureza).
- **Endpoints:** `GET /api/results` (lista, aberto a Professor e Aluno),
  `GET /api/results/{id}` (íntegra), `DELETE /api/results/{id}` (só Professor).
- **UI "Resultados salvos"** (rail · Histórico, sempre visível): lista com status,
  autor, data, duração e nº de linhas. Abrir mostra a saída na hora (colorida ISO);
  **▶ Reproduzir** reexibe linha a linha com timing — o professor reapresenta uma
  coleta KPM sem subir nada. Disponível também pro Aluno (só-leitura).
- Validado: persistência + prune (130→120), render + replay headless, e ao vivo
  (Professor roda → aparece em /api/results → Aluno lê a íntegra).

---

## [0.19.0] — 2026-06-20

**Modo sala de aula — 1 Professor, N Alunos ao vivo.** Todos abrem o mesmo link:
o professor entra com login e opera; os alunos entram com 1 clique ("Entrar como
aluno") e veem, em tempo real, tudo que o professor executa.

- **Trava de Professor único.** Estado em memória (`ACTIVE_ADMIN`) + `sid` no
  cookie de sessão. Um SEGUNDO admin diferente é barrado com **409** ("Já há um
  professor conectado"); o MESMO usuário pode reassumir (reconexão de outro
  dispositivo). A vaga libera sozinha após 30s sem heartbeat. Só o Professor
  ATIVO executa (`ensure_can_run` em todos os endpoints de execução; admin sem a
  vaga → 409).
- **Espelho ao vivo (Aluno).** A saída dos comandos do Professor é publicada num
  **ring-buffer compartilhado** com nº de sequência (`LiveBuffer` + `tee_to_live`);
  os alunos fazem **polling** de `/api/live?since=N` (escala pra turma inteira sem
  prender conexão/thread, ao contrário de SSE). Quem entra atrasado puxa o
  histórico recente. Eventos `begin`/`line`/`end`/`nav` espelham console + qual
  tela o professor abriu. O estado do projeto/ferramentas já era espelhado via
  telemetria.
- **UX.** Banner **🔴 AO VIVO** (com o que o professor faz) para o aluno; badge
  **👁 N alunos** para o professor (heartbeat 5s); papéis renomeados para
  **Professor/Aluno**; botão de login "Entrar como aluno (acompanhar ao vivo)".
- Aluno é estritamente só-leitura (nunca executa). Validado ao vivo: espelho
  begin→76×line→end, lock 409 (admin diferente) / 200 (reconexão), aluno 403 ao
  executar, nav propagado, contagem de espectadores.

> Fase 2 (depois): arquivo persistente de Resultados ("puxar do banco" coletas
> KPM/testes que sobrevivem a restart, navegável pelo aluno a qualquer momento).

---

## [0.18.0] — 2026-06-20

**Revalidação da topologia — minimalismo e zero sobreposição.**

- **Badges de interface nunca mais atrás dos cards.** Os rótulos (N2, SBI,
  Nausf, N4…) passaram a ser desenhados numa camada de topo (`gT`), acima dos
  nós; antes ficavam no grupo de links e eram cobertos por qualquer card que
  caísse sobre o ponto médio da seta. Pílula com fundo sólido + borda fina para
  leitura limpa sobre linhas e fundo.
- **Layout do Projeto 1 reorganizado** (`openran-topology-p1.json`): grade
  arejada, faixa de administração no topo, RAN à esquerda, malha do Core
  organizada e plano de usuário embaixo. Corrige a sobreposição real
  MongoDB×UDR e o estouro do canvas. Validado headless: **0 cards sobrepostos**
  (P1: 19 nós; P2: 16 nós).
- **Legenda virou badge minimalista** no canto inferior esquerdo, **recolhível**
  (começa fechada como "ⓘ Legenda" e não atrapalha a navegação; 1 clique abre
  Camadas + Interfaces). Saiu do rodapé — ganhamos a faixa inteira de baixo.
  Vale para os dois projetos.

---

## [0.17.1] — 2026-06-20

**Atalho "Ver logs" no resultado dos testes.** Quando um teste produz logs
(coletas E2SM-KPM/RC, conexão E2E do UE, NG Setup, registro, failover de UPF),
o painel agora exibe — logo após a explicação didática — uma faixa
**"📄 Ver logs do resultado:"** com botões-chip clicáveis para as fontes de log
relevantes (ex.: KPM → gNB e near-RT RIC; conexão do UE → AMF, SMF, UPF-A,
UERANSIM). Clicar carrega o log daquele serviço direto no console.

- `TEST_LOGS` (mapa cmd → fontes) + `appendLogLinks(cmd)`, chamado após
  `appendExplain(cmd)` no fim de `runCommand`.
- `startLogs(forceSvc)` aceita serviço explícito (string) vindo do chip e ainda
  funciona pelo botão "Ver logs" (que passa um Event); reflete a escolha no
  seletor quando a fonte está disponível.
- Validado headless (puppeteer): chips renderizam, clique dispara
  `startLogs('gnb')`, comandos sem logs (ex.: `status`) não geram faixa.

---

## [0.15.2] — 2026-06-20

**Correção do mecanismo do guardrail — agora a perfeição é medida.**

Ao medir a 0.15.1 sob carga, descobri que **`CPUQuota`/`cpu.max` (CFS bandwidth)
NÃO é enforçado neste kernel** (ARM/Graviton): forçar `cpu.max=100%` na slice
deixava o uso em >200% com `nr_throttled=0`. O teto nunca "mordia" — só o
`CPUWeight` funcionava (por isso o SSH sobrevivia, mas lento ~8s).

### Solução que funciona: cpuset (partição dura de núcleo)
- `oai-lab.slice` agora usa **`AllowedCPUs`** (cgroup v2 cpuset) para **fixar o
  lab fora do CPU 0** — em 2 vCPUs, o lab roda só no CPU 1 e o **CPU 0 fica
  inteiro reservado para o sistema** (ssh, docker, painel, Caddy). Independe de
  CFS bandwidth → funciona neste kernel.
- `CPUQuota=150%`/`MemoryHigh` ficam como rede de segurança (atuam onde CFS
  bandwidth existe; aqui são inócuos).
- `CPUWeight=10000` em ssh/docker/painel/caddy mantido (prioridade no CPU 0).

### Resultado medido (com gNB + nrUE no talo, o caso que travava tudo)
| Métrica | 0.15.1 (CPUQuota) | 0.15.2 (cpuset) |
|---|---|---|
| Painel (curl HTTPS) | lento/instável | **~600 ms** |
| SSH (conexão nova) | 6–9 s | **~2.5 s** |
| E2 SETUP do gNB | ok | **ok** (lab cabe em 1 core) |

- Aplicado por `infra/server-bootstrap.sh` (idempotente; reserva o CPU 0 mesmo
  se a instância tiver mais cores: `AllowedCPUs=1-(N-1)`).
- Recuperação: remover `oai-lab.slice` + drop-ins `*.service.d/cpu-guardrail.conf`
  + `systemctl daemon-reload`.

---

## [0.15.1] — 2026-06-20

**Guardrails de CPU** para o box de 2 vCPUs nunca mais ficar inacessível quando
o lab E2 satura (problema visto ao validar a 0.15.0: o `KPM_TRAFFIC=1` sobe o
nrUE, leva o load a ~30 e o SSH cai).

### Defesa em profundidade (cgroup v2, em `infra/server-bootstrap.sh` passo 6/6)
1. **`oai-lab.slice`** com `CPUQuota=180%` (= 90% dos 2 vcores) e `MemoryHigh=2.5G`:
   teto **agregado** do lab. Os lançadores pesados entram nela via
   `--slice=oai-lab.slice` (`up_gnb_oai.sh` → gNB e nrUE; `run_xapp.sh` → xApp).
   Garante ≥10% (~0.2 core) sempre livre para o sistema.
2. **`CPUWeight=10000`** em `ssh`/`docker`/`core5g-panel`/`caddy`: vencem a disputa
   de CPU, então o SSH e o painel continuam respondendo mesmo no pico.

### Prova
- Sob a MESMA carga que antes derrubava a sessão (lab + nrUE, load ~29), o
  **SSH respondeu 18/18** (zero quedas). Antes: quedas repetidas (exit 255).
- `cpu.max = 180000 100000` (180%) e `CPUWeight=10000` confirmados ao vivo no
  cgroup. O `load` alto é o sinal de *throttling*, não de saturação real (uso de
  CPU do lab fica em ≤1.8 cores).
- Idempotente; recuperação: remover `oai-lab.slice` + os drop-ins
  `*.service.d/cpu-guardrail.conf` e `systemctl daemon-reload`.
- Dica: sob pico, **derrube pelo painel** (serviço com prioridade alta responde
  mesmo quando o SSH está lento).

---

## [0.15.0] — 2026-06-20

Conteúdo dos labs alinhado aos **PDFs do professor** + topologia por projeto.

### Testes novos (a partir dos exercícios das aulas)
- **Projeto 1** (aula01 — "fluxo de registro" / checklist), em `server/scripts/`:
  - `test_ng_setup.sh` — confirma o NG Setup (N2): `NG Setup procedure is
    successful` no gNB + atividade NGAP no AMF.
  - `test_registration.sh` — Registration accept, estado `REGISTERED`, sessão
    PDU (IP em `uesimtun0`) e sinalização NAS no AMF.
  - `test_config_coherence.sh` — compara PLMN/SST/APN entre `gnb.yaml` e
    `ue.yaml` (divergência = causa comum de "N2 OK mas UE não conecta").
  - Entram no seletor "Testes do Projeto 1".
- **Projeto 2** (aula04, slide 43): botão **E2SM-KPM (com tráfego)**
  (`KPM_TRAFFIC=1`, ping ao DN sobe o throughput medido).

### Topologia por projeto
- `/api/topology?proj=p1|p2` serve a topologia certa (status ao vivo por nó).
- Criada `openran-topology-p1.json` (Open5GS 5GC + UERANSIM, 19 nós: AMF, SMF,
  UPF-A/B, AUSF, UDM/UDR, PCF, BSF, NSSF, NRF, SCP, Mongo, DN, WebUI + gNB/UE).
  A `openran-topology.json` permanece como a do Projeto 2.
- `topology.html` lê `?proj`, ajusta título e atualiza o status ao vivo do
  projeto certo. Os links da lateral já apontam para `/topology?proj=…`.

---

## [0.14.0] — 2026-06-20

Reorganização guiada pelo uso real + **correção do bug de ativação**.

### Fix — ativar/desligar do Projeto 2 (fundação)
- O painel chamava os scripts **v1** do OAI (`oai-cn5g-fed`), mas o servidor roda
  o core **v2** (`oai-cn5g-v2`, v2.2.1). O `down_core.sh` v1 não parava os
  containers v2 → "desligar não obedecia".
- Remapeado `COMMANDS` (`p2-up/down-core`, `p2-up-e2-lab`) e `switch_project.sh`
  para os scripts v2 (`up_core_v2`/`down_core_v2`/`up_e2_lab_v2`).
- **Validado no servidor:** down para os 9 containers; up sobe todos *healthy*.

### Reorganização da UI (por projeto)
- **Topo:** 2 cards de projeto lado a lado, cada um com seus **servidores
  (toggle = comando)** + "ativar" (troca exclusiva via `switch_project.sh`).
  O card ativo é realçado; telemetria continua no cabeçalho.
- **Lateral:** rail de **ferramentas do projeto ativo** (ícone + rótulo),
  trocando conforme `_activeProj`:
  - **P1:** Topologia · UE Lab · Demonstração E2E · Testes P1
  - **P2:** Topologia · Testes P2
  - **Logs** comum (oculto quando nada está no ar).
- **Guarda de dependência:** RAN (P1) só habilita com o Core (P1) no ar.
- Links de topologia já apontam para `/topology?proj=p1|p2` (visão por projeto
  vem na próxima etapa).

### Base para os testes do professor (PDFs)
- Plano em `docs/plano-painel-redesign.md`: a demo guiada do professor já bate
  com ~70% dos testes; faltam 3 no P1 (NG Setup, Registro, Coerência) e a
  variante KPM com tráfego no P2 — entram incrementalmente.

---

## [0.13.0] — 2026-06-20

**Redesenho da navegação do painel** (`server/panel/static/index.html`),
mantendo 100% da fiação de eventos/IDs — só mudou a estrutura visual.

### Menu superior (top bar)
- Tudo que é global subiu para um cabeçalho único, em duas faixas:
  - **Faixa 1:** marca + **indicador de projeto ativo** (`#active-proj`, pílula
    que mostra qual lab está no ar e acende em verde) + seletor de projeto
    (P1/P2/Desligar) + ferramentas (UE Lab, Demonstração E2E, Topologia) + whoami.
  - **Faixa 2:** telemetria (CPU/RAM/Swap/Disk) + `details` de containers.
- Removida a antiga `action-bar` (ferramentas e seletor migraram pro topo).

### Sidebar lateral colapsável
- O antigo painel esquerdo (260px fixos) virou um **rail de 64px** que
  **expande no hover** (288px) — "ao passar o mouse mostra tudo". Colapsado
  mostra só ícones; expandido mostra rótulos, toggles e testes.
- Conteúdo organizado **por lab**, com o grupo do projeto ativo realçado:
  - **Projeto 1 · Open5GS** — toggles Core/RAN + testes do P1.
  - **Projeto 2 · OAI/RIC** — toggles Core (OAI)/E2 lab + testes E2 do P2.
  - **Logs & Diagnóstico** (comum) — filtro de logs do projeto ativo + visão O-RAN.
- A sidebar expande **sobreposta** (não empurra o console, sem reflow).

### Notas
- `updateProjSelector` ganhou 2 efeitos de UI (badge do cabeçalho + highlight do
  grupo na sidebar); a lógica de estado/telemetria é a mesma.
- A UI de "menu superior" original (commit `adf8ad12`, de outra máquina) não
  existe neste clone — esta é uma **reconstrução do zero**.

---

## [0.12.4] — 2026-06-20

xApps do Projeto 2 **validados de ponta a ponta**: `e2_verify.sh` →
**cust 7/7, kpm 7/7, rc 5/7** (load < 2). No caminho, dois bugs — que NÃO eram
"falta de CPU", como parecia no início:

### 1. Plugins SM de arquitetura errada (crash do nearRT-RIC)

O repo versionava `server/oai-cn-gnb-e2/flexric-lib/*.so` compilados para
**x86-64**; num host **arm64** o `dlopen` do RIC falha
(`load_plugin_ric: Assertion handle != NULL`). E `sync-oai` espalhava esses
x86-64 por cima dos arm64 que o servidor havia buildado.

- Os `.so` saíram do versionamento (`git rm --cached` + `.gitignore`) — são
  artefatos de build, específicos de arquitetura.
- `up_flexric.sh` agora **detecta a arquitetura** do `.so` e repovoa
  `flexric-lib/` do build tree (`sync_flexric_lib.sh`) quando falta OU é de outro
  arch. Auto-curável em qualquer host.

### 2. Falso-negativo no `run_xapp.sh`

Usava `tail -F --pid | grep -m1` com `set -o pipefail`: ao casar o evento de
sucesso, o `grep -m1` fecha o pipe, o `tail` morre com SIGPIPE e o `pipefail`
marcava o pipeline inteiro como falha — reportava `❌ FALHA` mesmo com o xApp
subscrito (`Successfully subscribed to RAN_FUNC_ID …`). Trocado por **poll no
arquivo** (`grep -q` em laço até o evento OU o processo morrer): sem pipe, sem
SIGPIPE, 100% event-driven.

### Validação sem UE (SKIP_UE)

`up_e2_lab_v2.sh` passou a repassar `SKIP_UE`; `e2_verify.sh` sobe com
`SKIP_UE=1` por padrão. Sem o nrUE sobra 1 vCPU inteiro pro RIC+xApp (load < 2,
SSH estável) — o E2 é gNB↔RIC e independe do UE. Para o lab COM user plane:
`SKIP_UE=0` (mas sem rodar os 7× de xApp junto).

---

## [0.12.3] — 2026-06-20

### Auth — guest opt-in (trava "só hcarmine")

O acesso de convidado passou a ser **opt-in**: só existe quando
`PANEL_GUEST_USER`/`PANEL_GUEST_PASSWORD` vêm preenchidos no `.env`. Em branco,
o convidado fica **desabilitado** e só os admins (`PANEL_USER` +
`PANEL_EXTRA_USERS`) entram.

- `server.py`: flag `GUEST_ENABLED`; `POST /api/login/guest` responde **403**
  quando desabilitado (era a porta aberta — concedia sessão guest sem senha);
  `do_login` também só aceita o ramo guest se habilitado.
- `login.html`: botão "Entrar como convidado" e o divisor somem quando o guest
  está desabilitado (flag `__GUEST_ENABLED__` injetada no `/login`).
- `server-bootstrap.sh`: guard exige só `PANEL_USER`/`PANEL_PASSWORD`; guest
  opcional, sed robusto a valor vazio.

---

## [0.12.2] — 2026-06-20

Traz o **plano de usuário real no arm64** (Projeto 2) e os testes de xApp
**event-driven**. Integrado sobre a 0.12.1 mantendo todo o trabalho de painel/
testes já existente — só adiciona arquivos novos, sem conflito.

### Projeto 2 — user plane no arm64 (OAI v2.2.1)

O core v1.5.1 (§7.b) só tinha plano de controle: o `oai-upf-vpp` é Intel-only
(`libhyperscan`), então o UE nunca pegava IP. Adicionado deployment **paralelo**
em `server/oai-cn-gnb-e2/oai-cn5g-v2/` com as imagens **multi-arch oficiais
v2.2.1** (7/7 NFs com arm64, incl. `oai-upf` datapath `simple_switch`).

- Config casa com o gNB atual: PLMN 208/95, TAC `0xa000`, slice SST 222 / SD 123,
  DNN `default` (`12.1.1.0/26`), AMF fixo `192.168.70.132`, SNAT no UPF.
- `up_core_v2.sh` / `down_core_v2.sh` (sobe/derruba v2.2.1, exclusão mútua com P1).
- Validado fim a fim: UE ganha `oaitun_ue1` com IP `12.1.1.x`, tráfego real (GTP-U).

### xApps e E2 lab — event-driven

- `run_xapp.sh <cust|kpm|rc>`: roda o xApp e **encerra no 1º evento de sucesso**,
  nunca por duração. Pré-requisito por **estado** (`pgrep -x`), cgroup com
  `CPUQuota` (`XAPP_CPU_QUOTA`, default 50%) + `nice`.
- `up_e2_lab_v2.sh`: sobe o lab sobre o core v2.2.1; checa `oai-amf` por
  `.State.Running` (não `Health.Status`). Compatível com o `up_gnb_oai.sh` atual
  (GNB_NRB=51 → `-C 3469440000`).
- `e2_verify.sh`: orquestra tudo e roda os 3 xApps 7× cada, esperando o **evento**
  `E2 SETUP RESPONSE` no log do gNB (poll de condição, sem race de PID).
- **Achado:** o binário FlexRIC tem timeout interno compilado; com gNB+nrUE
  saturando os 2 vCPUs o xApp aborta ("Timeout waiting for Report"). Não é bug
  nosso — é limite de hardware. Mitigação: derrubar o nrUE (libera 1 vCPU; E2 é
  gNB↔RIC). Documentado no bible §7.c.

> Nota: este bloco foi feito em paralelo à linha que chegou à 0.12.1 (login/
> topologia/testes coloridos). Reconciliado mantendo ambos; a UI de menu superior
> proposta na linha paralela foi **descartada** em favor da UI 0.12.x existente.

---

## [0.12.1] — 2026-06-19

### Testes agrupados por projeto + bloqueio mútuo

- Os testes do menu lateral passam a ficar **dentro do grupo de cada projeto**:
  "Testes do Projeto 1" (Status/Healthcheck, status detalhado, conectividade do
  UE, failover UPF) sob Projeto 1; "Testes do Projeto 2" (E2 SM/KPM/RC) sob
  Projeto 2. O antigo grupo "Testes (gerais)" foi removido.
- **Bloqueio mútuo** (`refreshTestLocks`): só os testes do **projeto ativo**
  ficam habilitados; os do outro projeto (e ambos, quando nada está no ar)
  ficam desabilitados e esmaecidos, com a nota "Ative o Projeto X". O estado
  vem da telemetria (grupos on/off). UE Lab e Demonstração E2E (testes do
  Projeto 1, na barra superior) seguem o mesmo bloqueio.
- Não há "Testes globais": todos os testes atuais são específicos de um projeto
  (healthcheck/status checam o Open5GS).

---

## [0.12.0] — 2026-06-19

Padronização visual e didática de **todos os testes** do painel, mais correções
de bugs reais encontrados ao testar um por um.

### Colorimetria ISO/ANSI + resumo didático (todos os testes)

- Painel passa a **renderizar ANSI de verdade** nos dois consoles (principal e
  UE Lab): `renderLogLine` converte SGR em `<span>` coloridos (HTML-escapado),
  com fallback para o colorizador por conteúdo (`lineColor`, agora também
  reconhece ✓/✗/⚠). Verde=ok, amarelo=atenção, vermelho=erro, azul=info.
- Lib bash compartilhada **`scripts/lib/testlog.sh`** (P1 e P2): helpers
  minimalistas `section/ok/warn/err/info/step/kv` + bloco **`summary`**
  padronizado ("O que fez" + "Resultado" colorido).
- Refatorados com cor + resumo: `test_channel`, `test_throughput`,
  `test_ue_connection`, `test_upf_failover`, `test-system-status`,
  `healthcheck` (P1) e `test_e2_sm`, `test_e2_kpm`, `test_e2_rc_attach` (P2).

### Fix — interferência/distância não aplicava (bug do `jitter`)

`test_channel.sh` montava `tc netem ... jitter Xms`, mas `jitter` **não é
palavra-chave** do `tc` (respondia `What is "jitter"?` e não aplicava nada). O
relatório saía sempre igual. Corrigido para a forma certa (`delay <atraso>
<jitter> loss <perda>%`) + força a medição pelo túnel + ping de confirmação.
Validado: ideal 148 Mbit/s → 1km/media 608 Kbit/s (10% perda, 41 ms).

### Fix — `test_upf_failover` abortava (nomes de container desatualizados)

Usava `docker compose ps | grep "upf-a.*Up"` (não casa com o nome real
`open5gs-upf-containerized-a` nem com o status "running" do compose v2) e
`docker compose exec ueransim` (ueransim é container avulso). Trocado por
checagem robusta por serviço (`--status running`) e `docker exec` para o UE.

### Robustez — anti-freeze também nos testes KPM/RC

`test_e2_kpm.sh` e `test_e2_rc_attach.sh` reiniciavam o gNB/UE RFSIM **sem** o
teto de CPU (risco de congelar a instância). Passam a usar o mesmo
`systemd-run --scope` com `CPUQuota`/`CPUWeight`/`nice`. Validado: máquina
responsiva (echo < 0,5 s) sob load alto.

### Operação

- `test_e2_sm.sh` aborta na hora (com resumo) se o gNB não estiver no ar, em
  vez de travar 30 s por xApp.
- `sch_netem` carregado/persistido no `server-bootstrap.sh` (necessário para o
  `tc netem`).

---

## [0.11.1] — 2026-06-19

### Fix — testes de interferência/distância do Projeto 1 não tinham efeito

Os testes de interferência e distância aplicavam `tc netem` em `uesimtun0`,
mas **a medição não passava por essa interface**, então o resultado era sempre
o mesmo. Duas causas:

- **Roteamento:** a tabela do UE não tinha rota por `uesimtun0` — o tráfego pro
  DN (`10.50.0.100`) saía pelo bridge `eth0`, ignorando o túnel 5G e o `netem`.
  O `iperf3 -B` liga só o IP de origem, não força a interface. **Correção:**
  `test_throughput.sh` agora adiciona rota `/32` dedicada pro DN via `uesimtun0`,
  forçando a medição pelo túnel (onde o `netem` morde).
- **Módulo `sch_netem` ausente** no kernel (não carregado por padrão).
  **Correção:** `server-bootstrap.sh` carrega e persiste o módulo
  (`/etc/modules-load.d/netem.conf`).

Validado: ideal **171 Mbit/s** → interferência 5%/50ms **1.0 Mbit/s** →
distância "longe" 10%/120ms **604 Kbit/s**, com perda/RTT acompanhando.

### Resumo no fim do teste de throughput

`test_throughput.sh` passa a imprimir um bloco final: condição de canal
simulada (loss/delay ativos), estado do UE (`nr-cli`: CM/MM, célula, TAC),
throughput de envio/recepção, retransmissões TCP, perda de pacotes e latência
RTT médio/máx + jitter. Os testes de interferência/distância também medem e
mostram o efeito (perda/RTT pelo túnel) ao serem aplicados.

---

## [0.11.0] — 2026-06-19

Bloco grande de funcionalidade voltado à apresentação do Projeto 2 (20/06).

### Painel — tela de login dedicada

- `login.html` minimalista (tema escuro): usuário/senha + botão "Entrar como
  convidado". Substitui o popup de Basic Auth do Caddy por **autenticação de
  sessão via cookie HMAC** (`server.py`: `make_session_token`/`read_session_token`,
  middleware `require_session`, `PUBLIC_PATHS`). Caddy passou a ser **TLS-only**.
- Rodapé do login com repositório, versão, CESAR School e "Mantido por
  Henrique Carmine — @henriquecarmine".

### Painel — múltiplos usuários admin via `.env`

- `PANEL_EXTRA_USERS="user:senha,..."` no `.env` cria admins extras (acesso
  total) sem mexer no `PANEL_USER` principal. Plumbado de ponta a ponta:
  `.env` → `deploy.sh` → `server-bootstrap.sh` → unit systemd → `server.py`
  (dict `ADMIN_USERS`). Ex.: `grupo6:grupo6`.

### Painel — topologia interativa (containers reais)

- `topology.html` + `openran-topology.json`: inventário **real** (16 nós,
  20 links) com containers/portas/redes do lab, não um O-RAN genérico.
  Camadas, interfaces nomeadas (N2/N3/N4/E2/E42/SBI…), legenda fixa no rodapé,
  clique no nó → modal (de onde vem / o que faz / pra onde vai), overlay de
  logs, animação de pacotes no modo "Fluxo", tour guiado e stats de RAN ao vivo.
- Endpoints: `/topology`, `/api/topology` (status ao vivo), `/api/topology/logs`,
  `/api/topology/gnb-stats`.

### Painel — seletor de projeto + demo E2E + logs no modal

- Seletor mutuamente exclusivo (`switch_project.sh`, `/api/switch/{p1|p2|off}`):
  desliga um projeto e sobe o outro, com progresso minimalista.
- Demonstração E2E do Projeto 1 (`demo_e2e.sh`): ping + IP público + iperf3.
- Modal de operação em 2 colunas (passos + **logs ao vivo**), anti-flicker
  (linhas de container atualizadas no lugar), estados tri-state on/loading/off.
- Identidade visual unificada (ícones mono + descrição nos botões).
- Explicação didática (bloco azul) após cada teste E2 SM/KPM/RC explicando o
  que aconteceu. Rótulos de telemetria corrigidos (RAM 4G, Disk 30G).
- Rodapé do painel: crédito "projeto mantido por @henriquecarmine" em azul,
  discreto, à direita.

### Projeto 2 — estabilidade da instância (anti-freeze)

- O gNB/nrUE RFSIM saturavam os 2 vCPUs do `t4g.medium` e **congelavam a
  máquina** (vários reboots forçados em 19/06). Corrigido em `up_gnb_oai.sh`:
  processos nativos rodam em *scopes* do systemd com `CPUQuota` (120%/60%) +
  `CPUWeight=20` + `nice 10`. Reserva CPU pro sistema e impede o freeze **sem
  quebrar o E2** — validado: máquina responsiva sob carga, `test_e2_sm.sh all`
  passa, UE chega a `RRC_CONNECTED`.

### Documentação

- Novo **`README.md`** na raiz: porta de entrada com reprodução do zero,
  roadmap com datas e como colaborar (contato `hc@cesar.school`).
- Bible §10 atualizada (Projeto 2 funcional, anti-freeze, roadmap UE-TP-rApp,
  bug AUSF↔UDM, symlinks FlexRIC) + ponteiro para o README.

---

## [0.10.0] — 2026-06-19

### Build OAI arm64 — pipeline completo

6 imagens OAI 5G Core compiladas nativamente para `linux/arm64`, exportadas e
carregadas no servidor AWS t4g.micro (Graviton2, Ohio). Verificação:
`docker run oai-amf → uname -m → aarch64` ✔

#### Bug 4 — `-msse4.2` em todos os CMakeLists.txt

Flag SSE4.2 (x86 SIMD) hardcoded no `else` genérico do bloco de detecção de
arquitetura. Em `linux/arm64`, `CMAKE_SYSTEM_PROCESSOR = aarch64` cai nesse
`else` e o GCC rejeita a flag.

Correção: `elseif (aarch64|arm64) set(C_FLAGS_PROCESSOR "")` nos 6 componentes
(AMF, SMF, NRF, UDR, UDM, AUSF).

#### Bug 5 — `libasan2` no `build_helper.udm` silencia o `apt-get` inteiro

O `PACKAGE_LIST` ubuntu do `build_helper.udm` terminava com `libasan2`
(pacote inexistente no Ubuntu 20.04 arm64). O `apt-get install -y` falha
inteiro quando qualquer pacote da lista não existe. O erro é silenciado pelo
`ret=$?` pós-`case` (captura o código do bloco `if`, sempre 0) → `libconfig++-dev`
nunca instalado → cmake falha com `None of the required 'libconfig++' found`.

Correção: remover `libasan2` do PACKAGE_LIST ubuntu (o `libasan5` correto já
está em `specific_packages` para ubuntu20.04).

#### UPF-VPP excluído do build arm64

`libhyperscan-dev` é Intel-only — não existe no repositório Ubuntu focal arm64.
O lab usa Open5GS UPF; os 6 componentes de Control Plane são suficientes.

#### Resultado

| Imagem           | Tamanho | Status |
|------------------|---------|--------|
| oai-amf:v1.5.1  | 280 MB  | ✔ |
| oai-smf:v1.5.1  | 260 MB  | ✔ |
| oai-nrf:v1.5.1  | 264 MB  | ✔ |
| oai-udr:v1.5.1  | 268 MB  | ✔ |
| oai-udm:v1.5.1  | 257 MB  | ✔ |
| oai-ausf:v1.5.1 | 255 MB  | ✔ |

---

## [0.9.0] — 2026-06-19

### Build das imagens OAI 5G Core para arm64

#### Problema

As imagens `oaisoftwarealliance/oai-{amf,smf,nrf,udr,udm,ausf,upf-vpp}:v1.5.1`
no Docker Hub são amd64-only (sem `linux/arm64/v8`). O servidor AWS t4g.micro
(Graviton2, `aarch64`) falha ao tentar subir qualquer uma delas:
`exec /usr/bin/python3: exec format error`, container sai com código 255.

O servidor não tem QEMU/binfmt-misc — e adicionar emulação em produção seria
lento e frágil. Decisão: **compilar nativamente no Mac Apple Silicon**
(Docker Desktop `linux/arm64`), exportar como `.tar`, fazer `scp` para o
servidor e `docker load`.

#### `build-oai-arm64.sh` (novo, raiz do repo)

Script com 4 subcomandos encadeáveis:

```
./build-oai-arm64.sh build    # docker build --platform linux/arm64 nas 7 imagens
./build-oai-arm64.sh save     # docker save → /tmp/oai-images/*.tar
./build-oai-arm64.sh upload   # scp de cada .tar para ~/  no servidor
./build-oai-arm64.sh load     # docker load + rm do .tar no servidor
./build-oai-arm64.sh all      # sequência completa (padrão)
```

Lê `AWS_SERVER_HOST`, `AWS_SERVER_USER`, `AWS_SSH_KEY_PATH` do `.env` da
raiz — sem IP/hostname hardcoded. Usa o mesmo `.pem` que o `deploy.sh`.

#### Bugs encontrados e corrigidos no script

**Bug 1 — `declare -A` (bash 3.2 do macOS)**

macOS vem com bash 3.2 que não suporta arrays associativos (`declare -A`).
O script original lançava `oai: unbound variable` ao executar. Corrigido
substituindo o array por string simples `COMPONENTS="oai-amf oai-smf ..."` e
iterando com `for comp in $COMPONENTS`.

**Bug 2 — Dockerfile nomeado sem prefixo `oai-`**

O arquivo se chama `Dockerfile.amf.ubuntu`, não `Dockerfile.oai-amf.ubuntu`.
O script gerava o caminho errado e pulava todos os 7 componentes com "Dockerfile
não encontrado". Corrigido com `shortname="${comp#oai-}"` para remover o
prefixo antes de montar o nome do arquivo.

**Bug 3 — `libboost1.67-dev` não disponível para arm64 no Ubuntu 18.04**

O `build_helper.amf` (e equivalentes) adiciona o PPA `ppa:mhier/libboost-latest`
e tenta instalar `libboost1.67-dev`. Esse PPA não publica pacotes arm64, causando
`E: Unable to locate package libboost1.67-dev` e aborto com "AMF deps
installation failed" aos ~123 s de build.

Corrigido passando `--build-arg BASE_IMAGE=ubuntu:focal` ao `docker build`.
Ubuntu 20.04 tem Boost 1.71 nos repositórios padrão e o `build_helper` tem um
case `ubuntu20.04` que instala `libboost-all-dev` diretamente, sem PPA. O
Dockerfile suporta bionic, focal e jammy explicitamente — usar focal é o
caminho suportado pelo upstream para arm64.

**Bug 4 — `-msse4.2` hardcoded no CMakeLists.txt de todos os componentes**

Após o Bug 3 ser resolvido, a compilação falha com:
```
cc: error: unrecognized command line option '-msse4.2'
```
O bloco de detecção de arquitetura em cada `src/*/CMakeLists.txt` só trata
`armv7l` explicitamente; qualquer outra arquitetura cai no `else` e recebe
`-msse4.2` (flag SSE4.2 x86 que não existe em ARM64). Em build
`linux/arm64`, `CMAKE_SYSTEM_PROCESSOR = aarch64` → make falha em todos os
arquivos `.c/.cpp` que passam pelo GCC cross-compilado.

Corrigido editando o bloco `if/else/endif` nos CMakeLists.txt de
`oai-amf`, `oai-smf`, `oai-nrf`, `oai-udr`, `oai-udm`, `oai-ausf`:

```cmake
elseif (CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|arm64")
  set(C_FLAGS_PROCESSOR "")
```

`oai-upf-vpp` usa VPP com build system próprio — não afetado.

**Bug 5 — `libasan2` inválido silencia o `apt-get` inteiro no `build_helper.udm`**

O `PACKAGE_LIST` ubuntu do `build_helper.udm` terminava com `libasan2` (pacote
inexistente no Ubuntu 20.04 arm64). O `apt-get install -y` falha inteiro quando
qualquer pacote da lista não é encontrado. O erro é silenciado porque o `ret=$?`
subsequente captura o código de saída do bloco `if/case` (sempre 0 para
ubuntu20.04), não do `apt-get`. Resultado: `libconfig++-dev` nunca instalado →
`cmake` falha com `None of the required 'libconfig++' found`.

Corrigido removendo a linha `libasan2` (e depois `libasan` que também não existe
como pacote genérico) do `PACKAGE_LIST` ubuntu em `build_helper.udm`. O
`libasan5` já está em `specific_packages` para ubuntu20.04.

#### Estado em 2026-06-19

Build completo (Bugs 1–5 corrigidos) rodando para 6 componentes (AMF, SMF, NRF,
UDR, UDM, AUSF). `oai-upf-vpp` requer port adicional (libhyperscan-dev
indisponível em arm64 + caminhos x86_64 hardcoded). Próximos passos:
`save` → `upload` → `load` → `up_core.sh` (OAI 5GC no servidor) → validação E2E.

#### `core5g-arm64-bible.md` — §7.b (novo)

Nova subseção documentando a estratégia de build arm64, o script
`build-oai-arm64.sh`, pré-requisitos (Docker Desktop Apple Silicon), os 4 bugs
corrigidos e a tabela de parâmetros do `docker build`. Destinada a qualquer
pessoa que queira replicar o laboratório em hardware ARM64.

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
