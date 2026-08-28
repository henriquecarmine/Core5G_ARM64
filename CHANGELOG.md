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
| 0.24.3 | 2026-06-20 | Nome completo do professor confirmado nos PDFs da disciplina: **Prof. Dr. Jonas Augusto Kunzler** (jak@cesar.school) — atualizado no README e nos rodapés |
| 0.24.4 | 2026-06-20 | Crédito do autor: contato via henriquecarmine@gmail.com + breve perfil (perito forense digital; mestrando em Open RAN com o Prof. Jonas) no README/CONTRIBUTING. Equipe final: Prof. Jonas · Henrique · Klinger · Kelvin (Gilberto não participou) |
| 0.24.5 | 2026-06-20 | Mobile: faltava o `<meta viewport>` no painel (renderizava a 980px no celular, ignorando o CSS) — corrigido + bloco responsivo (header/banner/projetos/RAN se adaptam). Aluno no celular agora vê o espelho ao vivo direito |
| 0.24.6 | 2026-06-21 | RAN ao vivo só aparece com SNR real (não mostra card vazio "—" enquanto o UE não anexa). Ajuste vindo do ensaio de pré-flight: E2/xApps OK; UE do P2 não anexa (bug AUSF↔UDM conhecido) ⇒ sem fonte PHY viva |
| 0.24.7 | 2026-06-21 | Créditos: projeto **coordenado pelo Prof. Dr. Jonas Augusto Kunzler** e **mantido por Henrique Carmine** (README + rodapés). Adicionada seção **"Apoie este projeto"** (PIX) + `FUNDING.yml` (botão Sponsor). Licença já com copyright de Henrique Carmine |
| 0.24.8 | 2026-06-21 | Vaga de Professor reassume sozinha quando está LIVRE (após restart do painel/deploy ou abandono): a aba recupera no próximo heartbeat, sem relogar. Aviso de "sessão não ativa" se auto-limpa e diferencia "vaga livre (reassumindo…)" de "outro professor com o controle" |
| 0.25.0 | 2026-06-21 | Demonstração E2E **didática**: o console agora mostra o **comando real e a saída real** de cada passo, com narração "por quê". **Fix do throughput**: o iperf3 agora atravessa de fato o núcleo 5G (rota pelo `uesimtun0` + bind à origem do túnel) em vez de sair pela bridge docker |
| 0.25.1 | 2026-06-21 | Auditoria didática de **todos os relatórios**: padrão lib (cor + "Resumo") confirmado em P1 e P2. Único fora do padrão (`test_ue_connection`) reescrito — usa a lib no corpo, guardas de erro com Resumo + `exit 0`, e **veredito honesto** (ok/atenção/falha em vez de sempre "ok") |
| 0.25.2 | 2026-06-21 | **Verificação ao vivo dos relatórios P1** revelou 3 bugs de precisão (que a auditoria estática não pegava) — todos corrigidos: (1) `ue_connection` mostrava `<!DOCTYPE html>` como "IP público" (ifconfig.me via wget) → usa `/ip` + valida IP; (2) `ng_setup` e (3) `registration` davam falso-negativo "AMF não está rodando" (nome de container errado: `amf` vs `open5gs-amf-containerized`), fazendo `ng_setup` dizer "N2 não confirmada" mesmo com NGSetupResponse OK |
| 0.25.3 | 2026-06-21 | **Documentação para colaboradores**: novo guia [`docs/relatorios-didaticos.md`](docs/relatorios-didaticos.md) — como o sistema de relatórios funciona (lib `testlog.sh`, protocolo da Demo E2E, como adicionar um relatório, gotchas verificados ao vivo, inventário P1/P2). Ligado no README (mapa) e no CONTRIBUTING (validação) |
| 0.25.4 | 2026-06-21 | **Bible atualizado** com a sessão 0.25.x: §8.5 (relatórios com falso-negativo — container ≠ serviço Compose, HTML como IP, veredito desonesto) e §8.6 (Demo E2E media a bridge Docker, não o túnel 5G); §9 com a verificação ao vivo de todos os relatórios; §10 e §11 com o item da auditoria e o link do guia |
| 0.25.5 | 2026-06-21 | **Modo projeção** agora mantém a **régua lateral de ações** visível (o professor opera testes/demo enquanto projeta). Antes o kiosk escondia o `#sidebar` inteiro; agora só esconde o que polui o datashow (barra de projetos, telemetria pesada, copiar/limpar) e restaura o grid de 2 colunas |
| 0.26.0 | 2026-06-21 | **Gerenciar Resultados salvos**: excluir **um** (✕ por item) ou **vários** (modo "Selecionar" com checkboxes + "Excluir selecionados" + "Tudo"), e **anotar uma observação** (✎) no relatório pra lembrar do que era. Tudo só para Professor (Aluno 403), com confirmação nas exclusões |
| 0.26.1 | 2026-06-21 | **Botão "⎋ Sair" (logout)** no topo do painel. Faltava UI para o `/api/logout` que já existia — sem ele, a vaga única de Professor só liberava após 10 min de carência. Agora o professor sai com 1 clique (com confirmação) e **libera a vaga na hora** para outro entrar |
| 0.27.0 | 2026-06-21 | **`oai-upf-vpp` portado para arm64** (antes tido como "não portável"): o bloqueio era só o Hyperscan (Intel-only); o **Vectorscan** (fork ARM, drop-in `libhs`) resolve. Novo `Dockerfile.upf-vpp.ubuntu.arm64`, imagem validada (vpp aarch64, GTP UPF habilitado, plugin resolve `libhs.so.5`), `.tar` em `artifacts/oai-images/` |
| 0.55.1 | 2026-08-08 | **Non-RT interligado em TODA a narrativa didática** (feedback do usuário: fluxo de dados não chegava ao non-RT e faltava a explicação passo a passo). (1) **Logs da topologia** (P2) ganham as seções "Non-RT RIC (PMS · A1)" e "A1 Simulator (OSC)" — por onde os dados correm agora inclui a camada SMO; (2) **dropdown de Logs & Diagnóstico** com as duas fontes novas; (3) **explicação pós-teste** do `p2-test-a1` (EXPLAIN): loop lento >1 s vs loop rápido E2, sincronização de policy type, política confirmada no sim, e o aviso honesto do near-RT simulado; (4) nó **FlexRIC** da topologia agora conta a lacuna A1 no próprio texto. Nota: "RAN+RIC vermelho" no diagnóstico era o estado REAL (E2 lab desligado à época) — status vivo funcionando como projetado |
| 0.55.0 | 2026-08-08 | **Fase 2 começou: A1 Mediator REAL do O-RAN SC em ARM64** (`server/oran-ric/`). Portadas da fonte as 2 primeiras imagens `ric-plt-*`: **dbaas 0.6.4** (redis+redismodule+sdlcli) e **a1mediator 3.2.2** (Go + **RMR 4.9.4 compilada da fonte com patch ARM64** — `immintrin.h`/`_mm_lfence()` → `__atomic_thread_fence`, o único problema de arquitetura real; o resto era toolchain alpine). Compose com rede/IPs idênticos ao `vendor/oran-sc-ric` + overlay do docente e retag com nomes nexus3 — a pilha E2 completa encaixará sem alterar nada. **Smoke 5/5 no ciclo A1AP v2** (`/A1-P/v2`): healthcheck, policy type 20011 (janela do `a1-routes.rt`), política criada/lida/removida no Mediator DE VERDADE — não mais simulador. Runbook §9 com o passo a passo e as 4 iterações de build. Roadmap: e2term/e2mgr/submgr + gNB `nr-softmodem-oran-sc` |
| 0.54.0 | 2026-08-08 | **Non-RT RIC consolidado DENTRO do Projeto 2** (pedido do usuário: "completar o Projeto 2 — O-RAN · near-RT + non-RT e suas funcionalidades", não um projeto à parte). O card P3 avulso saiu; o card do **Projeto 2** agora descreve "O-RAN · near-RT + non-RT RIC (E2/A1)" e tem **3 toggles**: Core (OAI) · E2 lab · **Non-RT RIC** (estado vivo pelo container `nonrt-policy-agent`). O teste **"Testar ciclo A1 (non-RT → near-RT)"** entrou na lista Testes · Projeto 2 (comandos renomeados `p3-*`→`p2-*`; cena FlowStrip acompanhou). E o **switch de projeto ficou ciente da pilha completa**: ativar P2 sobe também o Non-RT RIC (melhor esforço — sem imagens carregadas o switch não falha), e desligar P2/off derruba PMS + sims junto. Rotas 50=50 |
| 0.53.1 | 2026-08-08 | **Topologia ganha a camada Non-RT (banda SMO)**. `openran-topology.json` (P2): banda nova "Non-RT RIC (SMO) — políticas A1" com 2 nós de status vivo — **Non-RT RIC (PMS)** (`nonrt-policy-agent`) e **A1 Simulators** (`a1-sim-OSC`), com textos didáticos from/does/to — e 2 links: **A1** PMS→simuladores (o ciclo do teste) e **A1 tracejado/planned PMS→FlexRIC**, documentando VISUALMENTE a lacuna (FlexRIC sem terminação A1; fechar = Fase 2). Legenda de interfaces ganha o A1. Geometria validada (`check-topology.py` OK, nenhum link cruza card de terceiro) |
| 0.53.0 | 2026-08-08 | **Non-RT RIC no painel — botões minimalistas (Projeto 3)**. Terceiro card na barra de projetos: **Non-RT RIC · A1** com um único toggle (`PMS + A1 sims`, estado vivo via telemetria pelo container `nonrt-policy-agent`) — sem botão "ativar" exclusivo porque a camada é leve (~0,5 GB) e roda junto de P1/P2. No rail, grupo global "Non-RT RIC · A1" com um botão: **▶ Testar ciclo A1** (`p3-test-a1` → `test_a1_flow.sh`, os 7 passos streamados no console). Comandos `p3-up-nonrt`/`p3-down-nonrt`/`p3-test-a1` no COMMANDS (ops.py, camada operacional). FlowStrip ganhou a cena do teste: `🧠 PMS (nonRT) → 📐 policy type → 📋 política ─A1→ 📡 a1-sim (nearRT)` — o percurso da política acende sobre o log enquanto o teste roda (e espelha ao vivo para os alunos). Zero rotas novas (50 = 50); tudo pela infraestrutura existente de comandos/toggles |
| 0.52.1 | 2026-08-08 | **Non-RT RIC NO AR no servidor + painel v0.52 em produção**. A pendência do 0.52.0 fechou: tarballs ARM64 (245 MB) enviados ao Graviton, `docker load`, stack no ar (`nonrt-policy-agent` healthy + 3 a1-sims) e **smoke A1 7/7 verde no servidor** — mesmo resultado do Mac, byte a byte. Painel v0.49→0.52 deployado (duas camadas + FlowStrip servindo em produção; layout antigo do `static/` removido do servidor; systemd recarregado). Segredos do clone novo recuperados (`ssl/*.pem` via Termius; `server/.env` real puxado do servidor antes do sync — sem sobrescrever com template). `deploy.sh sync` agora inclui `nonrt-ric/` (excluindo `src/`) e dá chmod nos scripts dele. Consumo medido com tudo no ar: 1,1 GiB RAM de 15 (a instância está num tier maior que o previsto), disco 76%. Registro no runbook |
| 0.52.0 | 2026-08-08 | **Non-RT RIC em ARM64 nativo — o bloqueio do §3 contornado pela fonte**. Novo [`server/nonrt-ric/`](server/nonrt-ric/): par mínimo A1 construído **da fonte, nativamente no Graviton** — `Dockerfile.a1pms` (A1 Policy Management Service 2.9.0, build em 3 estágios Maven→jlink→debian-slim, **UID 1000** em vez do 120957 que estourava subuid rootless) e A1 Simulator 2.8.0 (Dockerfile oficial, alpine multi-arch). Compose espelha a **Fase 1 do lab do Prof. Kunzler** (submódulo `config/nonrtric/`): mesmos nomes de serviço (`nonrt-policy-agent`, `a1-sim-OSC/STD/STD-v2`), rede `oran-nonrt-net`, `application_configuration.json` (ric1/2/3 → simuladores, managedElement `oai_gnb_lab`) e testdata compatível — os roteiros dele rodam aqui sem adaptação. Scripts: `build_arm64.sh` (clona fontes pinadas + docker build), `up_nonrt.sh`/`down_nonrt.sh`, e **`test_a1_flow.sh`** — smoke ponta a ponta em 7 passos (PMS vivo → rics → policy type no sim → sync no PMS → service+política via PMS → **política verificada no simulador** → limpeza). Runbook completo do zero ao teste verde em [`docs/instalacao-nonrt-arm64.md`](docs/instalacao-nonrt-arm64.md) (pré-requisitos, o que cada passo faz, troubleshooting, limites); non-rt-ric.md atualizado com o desbloqueio. Limite inalterado: FlexRIC sem terminação A1 ⇒ conversa com simuladores; fechar a ponta = Fase 2 do docente (near-RT O-RAN SC + a1mediator). Pendente: rodar o build no servidor (artefatos viajam no próximo `deploy.sh sync`) |
| 0.51.1 | 2026-08-08 | **FlowStrip cobre TODOS os testes e operações com fluxo de dados**. Auditoria completa comando × cena: entram as 3 cenas que faltavam — **checagens** (`test-system-status` · `test-config-coherence` · `status`: 🐳 containers → 🔗 rede/config → 📋 veredito), **assinante** (cadastrar/remover: 📝 IMSI/K/OPC → ⚙️ open5gs-dbctl → 💾 MongoDB — momento do armazenamento no banco) e **canal** (🎛 parâmetros → 📡 UERANSIM/netem → 🌐 efeito no ping). E a lacuna estrutural: o **UE Lab tem console próprio** (`#lab-console`) que não passava pelos hooks — agora tem faixa própria (`flow-strip-lab`) com begin/feed/end em cadastrar, remover, aplicar/zerar canal e medir throughput. Gatilho do 💾 do assinante ancorado no resultado ("adicionado com sucesso"), não no banner do script (o teste de lógica pegou o salto). Sem cena por decisão: up/down (10) e switch de projeto — infra, não fluxo de dados. Cobertura final: 17/27 comandos do console com cena (todos os testes/analytics/ML) + demo E2E, assinantes, canal e throughput do UE Lab |
| 0.51.0 | 2026-08-08 | **FlowStrip — o percurso dos dados animado sobre a tela de log**. Enquanto um teste roda, uma faixa minimalista acima do console (e do log do modal de operação) mostra de onde os dados saem, por onde passam (interface anotada: N1/N2/N3/N6/SBI/E2/E42), o momento do armazenamento (💾) e o resultado (✔/✖): `[📡 gNB] ─E2→ [🧠 FlexRIC] ─E42→ [📈 xApp] → [💾 kpm log]`. Zero backend novo: `static/ops/flow-strip.js` define **cenas por comando** (registro/NGAP, E2-KPM/RC/SM, kpm-analytics = ETL→KPI→decisão, testes de ML SUTD, throughput, UPF failover, demo E2E) e avança o fluxo por regex sobre as MESMAS linhas que o console já recebe — professor via stream, **aluno via LiveBuffer (a animação replica ao vivo de graça)**. Gatilhos ancorados em tokens de protocolo (NGAP, E2 SETUP, INDICATION, RMSE, iperf) que não mudam com o LAB_LANG; comando sem cena ⇒ faixa não aparece; eco `$ cmd` ignorado (não é dado). Paleta fixa de console (convenção nº 1), hooks mínimos em `pushRunHeader`/`appendLine`/`runCommand`/`applyLiveEvent`/`runOperation`. Validado: sintaxe node ok (motor + inline de 1,7k linhas), teste de lógica com DOM stub (avanço sequencial gNB→RIC→xApp→💾, falha marca o nó atual em vermelho), rotas intactas. É o MVP do 'modo fluxo' da Fase B do [plano de duas camadas](docs/plano-duas-camadas-painel.md); V2 = eventos estruturados `FLOW|/STORE|/RESULT|` no testlog.sh |
| 0.50.0 | 2026-08-08 | **Painel em duas camadas (Fase A do plano) — operacional × didática, sem mudar uma rota**. O monólito `server.py` (~1,5k linhas) virou 4 módulos: `core.py` (infra compartilhada, sem rotas: sessão HMAC, vaga única de Professor, LiveBuffer, resultados, streaming de comandos, i18n do servidor), `ops.py` (camada **operacional**: serviços P1·P2, telemetria, topologia, logs, assinantes, `COMMANDS`), `lab.py` (camada **didática**: páginas `/lab/*` + dúvidas aluno→professor) e `server.py` como bootstrap (app, middleware de sessão, login/logout, sala de aula ao vivo). `static/` espelha a separação: `static/ops/` (index, topologia, JSONs) × `static/lab/` (10 aulas + `lab-i18n/models/stepper.js`); `login.html` e `i18n.js` seguem compartilhados na raiz. Regra de dependência unidirecional: a didática consome a operacional via API, **nunca** o contrário ([plano](docs/plano-duas-camadas-painel.md) — Fases B: logs Nível 0; C: hub por disciplina). Geradores do `lab-didatico/` e testes atualizados para os novos caminhos. **Prova de não-regressão**: diff de rotas por introspecção do app — **50 antes = 50 depois**, zero removidas/adicionadas; smoke autenticado de 28 endpoints OK; `check-topology.py` OK. Entrypoint intocado (`uvicorn server:app`) — systemd e deploy não mudam |
| 0.49.0 | 2026-07-25 | **Non-RT RIC documentado (e a lacuna admitida) + o dataset de energia que faltava**. (1) **Novo [`docs/non-rt-ric.md`](docs/non-rt-ric.md)**: as técnicas do Lab de IA são, pela arquitetura O-RAN, **função de Non-RT RIC** (horizonte > 1 s) — mas o Non-RT **não existe nesta pilha**; roda só o Near-RT (FlexRIC/E2). **Correção de fato na bíblia**: a tabela afirmava que o `flexric` expõe `E2, A1` — **não expõe** (o `src/` tem só `agent/lib/ric/sm/util/xApp`, não há `examples/rApp/`, e as ocorrências de "A1" no código são falso-positivo de hex do `sqlite3.c`/ASN.1/XML de encoder). Registrado também que o "UE-TP-rApp" (`xapp_ue_tp_moni.c`) é um **xApp** que prevê por **EWMA (α=0,3)**, não um rApp com modelo treinado. (2) **Bloqueio ARM64 medido**: `docker manifest inspect` das **7 imagens** do Non-RT RIC (O-RAN SC Release K) direto do servidor `aarch64` — **7/7 em `amd64` puro**, manifestos v2 de arquitetura única, sem multi-arch (mesmo padrão do `gradiant/open5gs` 2.7.3+); o box não tem handler binfmt/QEMU. (3) **Caminho de instalação testado ponta a ponta** na máquina local `x86_64`/podman 5.8.4: A1 Policy Management Service 2.9.0 sobe em **10,1 s** (Spring Boot 3.4.0/Java 17), com `/actuator/health` → `UP` e `/a1-policy/v2/rics` respondendo — documentados os 2 obstáculos reais (UID 120957 fora da faixa de subuid → `ignore_chown_errors`; `crun: setgroups` → `--user 0`). Limite explícito: sem A1 no FlexRIC, integra com o `a1-simulator`, **não** com o gNB real. (4) **Aula de regressão ganha o 5º dataset**: `energy_prediction_boosting` **extraído do PDF** do Prof. Tesolin (só existia como imagem de tabela) — 24 linhas, **5 features** incluindo `TxPower` e **`CellTemperature`**, que faltava no lab. Regenerado pelo `gen_family_regression.py` (LeaveOneOut CV): os 4 datasets antigos saem **byte-idênticos** (prova de reprodutibilidade do ambiente) e o novo entra com Gradient Boosting liderando (RMSE 0,058 / R² 0,997). Aviso didático registrado: as 5 features têm correlação ≥ 0,968 entre si, então os coeficientes lineares **não são interpretáveis** (`TxPower` sai negativo) — multicolinearidade, ótimo material de aula. (5) **Correções**: `deploy.sh` quebrava em clone novo porque exigia `server/.env` (gitignored) — agora recria do `.env.example` com mensagem clara em vez de `rsync error 23`; guardrails do `server-bootstrap.sh` diziam "2 vCPUs" fixo → agora `$(nproc)`; resumo do teste `p2-ml-pm` se contradizia ("Campeão: MLP 93,1%" vs "Resultado: Gradient Boosting") → agora nomeia os dois papéis |
| 0.48.0 | 2026-07-21 | **"Os modelos, um a um" — cada algoritmo explicado em detalhe nas aulas do Lab de IA**. Toda aula com comparação de modelos ganhou uma seção nova que detalha **cada algoritmo** em três frentes: **como funciona · como usa os dados · como calcula** (didático, com a intuição da conta — ex.: "minimiza a soma dos erros ao quadrado", "árvore parte por limiares", "kNN guarda tudo e compara na hora" — sem matemática pesada). Novo `lab-models.js` compartilhado (padrão do `lab-i18n.js`/`lab-stepper.js`) com **16 algoritmos**: Linear, Ridge, Árvore, Random Forest, Gradient Boosting, kNN, SVR e **MLP/DNN**; Logística, Naive Bayes, SVM; k-means, DBSCAN, Hierárquico; Isolation Forest; PCA. Cada aula declara sua lista (`data-model-deepdive="…"`) e o script renderiza um **acordeão** (CSS próprio, tema-aware). Seção inserida antes do Relatório nas **7 aulas** (regressão/classificação/localização/manutenção/clustering/anomalia/PCA; loc/manut herdam do tpl). Nota transversal: todos recebem os mesmos KPIs (via E2/KPM) — muda o que cada um faz com eles. PT (corpo das aulas ainda não i18n'd) |
| 0.47.0 | 2026-07-21 | **Os 3 casos do artigo (RIC-IA) viram testes no servidor + aulas** — o trabalho final do Prof. Julio Tesolin dentro da plataforma. (1) **3 testes de ML no console do painel** (`p2-ml-uetp/localizacao/pm`): rodam o experimento scikit-learn **no servidor**, sobre os dados reais do walk test SUTD (Ngo et al. 2024), e fazem *stream* da tabela de métricas ao vivo — recorte *Instance*, `GradientBoosting`≈XGBoost reproduz o artigo (Localization ~84%, PM ~92,5%, UE-TP R² ~0,84). Experimentos portados para **numpy puro** (o venv do servidor tem numpy/scipy/sklearn/joblib vendorizados, **sem** pandas/matplotlib); CSVs do SUTD vendorizados em `oai-cn-gnb-e2/data/sutd/`; `server-bootstrap.sh` instala as wheels **offline**. (2) **2 aulas novas no Lab de IA** — `/lab/localizacao` e `/lab/manutencao`: classificadores sobre os dados reais do SUTD, previsão ao vivo em JS, **split temporal 70:30**, no mesmo padrão das 6 aulas (stepper, modal de fórmula, gerador de relatório). i18n do painel +18 chaves ×4 (paridade **624×4** OK) + hub/lab-i18n +6×4. Relatórios completos dos 3 casos + resumo na área de trabalho |
| 0.46.1 | 2026-07-13 | **Resiliência do DNS dinâmico + professor adicional**. Incidente real: stop/start da instância EC2 → IP público novo, e o IP antigo foi **reciclado pela AWS para outro cliente** — o SSH acusou "host key changed" (máquina de estranho no endereço velho; nunca aceitar a chave às cegas) e o DuckDNS só corrigiria no tick de 5 min do cron. Consertos: registro atualizado na hora **via token local** (`.env` da raiz também serve de plano B: `curl duckdns.org/update?...&ip=`), e o `duck.sh` agora roda **no boot** (`@reboot` no crontab, aplicado no servidor e codificado no `infra/server-bootstrap.sh`). Recomendação registrada: **Elastic IP** elimina essa classe de problema. Também: **professor adicional cadastrado** via `PANEL_EXTRA_USERS` (credenciais só no `.env`, fora do git; logins verificados ao vivo com logout imediato p/ não ocupar a vaga única de professor) |
| 0.46.0 | 2026-07-13 | **Modo passo a passo nas aulas do Lab de IA** — resposta direta ao teste do Henrique ("fiquei perdido, não sabia onde clicar nem quando clicar em compreendi"). Novo `lab-stepper.js` compartilhado transforma cada aula (Fundamentos + 5 técnicas) num percurso guiado de **UM passo por vez**: barra fixa **"Passo X de Y"** com bolinhas de progresso clicáveis, **dica "👉 O que fazer aqui"** em cada etapa (só leitura × agora mexa × opcional), botões **◂ Voltar / Próximo passo ▸** (e setas do teclado), e a **etapa final explica exatamente quando clicar ✅ Entendi ou 🤔 Não entendi**. Reordenação didática: o conceito (📖) agora vem ANTES da escolha de base (🗂️). O passo atual fica salvo por aula (retoma de onde parou; concluir zera). Link **"ver a aula inteira"** restaura a visão antiga para quem prefere rolar. i18n completo: +16 chaves ×4 idiomas (paridade lab 162×4 verificada) |
| 0.45.0 | 2026-07-13 | **Lab de IA vira UM produto só com o painel** (6 pedidos do Henrique). (1) **As aulas abrem dentro do frame do console** (iframe embutido com barra própria: título, ⧉ página cheia, ✕) — o rail agora tem **um único item 🎓 Lab de IA**; acabou a sensação de "outro sistema". (2) **Modais de fórmula detalhados**: tabela **"As variáveis, uma a uma"** (símbolo → o que é → exemplo real) + tipo de fórmula + para que serve, nas 5 técnicas. (3) **Interligado ao sistema real**: caixa **"🔌 No sistema real"** em cada aula explica que os KPIs chegam pela E2 (E2SM-KPM) do 5G rodando por baixo, com botão que **dispara a coleta KPM real no console do painel** (postMessage → runCommand p2-kpm-real; professor executa, alunos acompanham ao vivo). (4) **Formulário do relatório em 4 idiomas** (data-i18n em título/campos/botões; +15 chaves ×4 no lab-i18n.js, paridade 147×4). (5) **Linha de compreensão** no fim de cada aula: **✅ Entendi → próxima** (grava o progresso e navega) · **🤔 Não entendi → escreve a dúvida** → `POST /api/lab/question` (JSONL em panel_results); professor vê a lista **"Dúvidas dos alunos"** no hub (`GET /api/lab/questions`, 403 p/ aluno). (6) Tema do painel reflete no lab embutido; links internos preservam o modo embed |
| 0.44.0 | 2026-07-13 | **Relatório v2 (minimalista) nas 5 técnicas do Lab de IA** — a entrega que supera o pedido. Novo design de impressão estilo suíço: capa com badge da técnica, **⚡ "Em 30 segundos"** (resumo executivo em 4 bullets computados do que o aluno rodou), **metodologia em 4 passos**, **tabela comparativa com barra visual integrada** (barras em células de tabela — à prova de Word), **a fórmula que o modelo aprendeu** com os coeficientes/loadings reais, exemplo interativo, **glossário de 1 linha por métrica**, caixa **"Limites & próximos passos"** (senso crítico) e código. Terceiro download: **⬇ script Python (.py)** — a entrega literal do professor (relatório + script); em Clustering/Anomalia/PCA o .py sai com **os dados do professor embutidos** (roda na hora). i18n do lab também no ar: motor `lab-i18n.js` (pt/en/es/fr, herda o idioma do login via cookie `c5g-lang` + seletor de bandeiras) com **Hub e Fundamentos** traduzidos |
| 0.43.0 | 2026-07-13 | **Lab de IA para RIC — jornada didática completa** (do zero ao relatório). Nova aba **🎓 Lab de IA** no painel (`/lab`): um **Hub da Jornada** que guia o aluno (Fundamentos + 5 técnicas) com **duas trilhas** (⚡ rodar+relatório · 📚 estudo no ritmo) e **progresso salvo no navegador**. **Aula 0 · Fundamentos** (o que é IA/ML, supervisionado × não supervisionado, laço O-RAN, ajudante "qual técnica uso?"). **5 técnicas** sobre os **datasets originais do Prof. Tesolin** (Base Fonts RIC): Regressão (UE-TP), Classificação (congestão Low/Med/High + falha No/Yes), Clustering (k-means + silhueta), Anomalia (Isolation Forest), PCA — cada uma com **Explica → Onde roda no O-RAN → Mexe ao vivo → Compara → Modal fórmula+Python** (o que o `fit` captura e o `transform` retorna) e **gerador de relatório** nas 3 partes do trabalho em **PDF (impressão) e Word (.doc)**, tudo client-side. Rotas `/lab`, `/lab/fundamentos`, `/lab/{regressao,classificacao,clustering,anomalia,pca}` + botões no rail P2. Datasets kNN/NaiveBayes/SVM ficaram de fora (PDFs paginados largos, extração não confiável) |
| 0.42.2 | 2026-07-04 | **Fix: login que falha dava 500 em vez de "senha inválida"**. O `/api/login` usava `req_lang(request)` no caminho de erro (senha errada / usuário inexistente / vaga ocupada) mas **não declarava `request` como parâmetro** — `NameError` → **500 Internal Server Error** em todo login incorreto (o login certo funcionava, por isso passou despercebido). Agora declara `request: Request` (FastAPI injeta) e devolve **401 com a mensagem traduzida**. Descoberto ao cadastrar o Prof. Tesolin |
| 0.42.1 | 2026-07-04 | **Jornada do UE ganha a etapa do NRF** (P1 e P2, 4 idiomas). Nova etapa **"O catálogo do Core (NRF)"** entre o registro e a autenticação: o NRF e seus raios SBI acendem como um **hub**, com os pacotes **convergindo para dentro** (todo NF se registra e se descobre ali) e o resto esmaecido — didático e sem virar espaguete. Responde à pergunta "como o AMF acha o AUSF/SMF/UDM?". P2 = 16 etapas; P1 = 13 (com os 8 raios: inclui NSSF/PCF/SCP). +4 chaves i18n (606×4); smoke atualizado |
| 0.42.0 | 2026-07-04 | **Jornada do UE também no Projeto 1** (Open5GS + UERANSIM, pt/en/es/fr). O percurso guiado do dado passo a passo agora cobre o P1: **12 etapas** — UE+gNB juntos no UERANSIM (rádio interno), N2, registro N1, autenticação + **seleção de slice (NSSF)**, sessão N11 + **política (PCF/BSF)**, N4/CUPS, IP (uesimtun0), dados N3/N6 (ida e volta) e — o destaque — o **failover de UPF** (UPF-A cai → SMF reprograma a UPF-B pela N4, que assume o tráfego, sem derrubar a sinalização: o valor concreto do CUPS). Motor da jornada **generalizado (P1+P2)** com desambiguação por interface (N1 vs N2 no mesmo par de nós). **+24 chaves i18n (602×4)**. Smoke cobre as 12 etapas do P1 + as 15 do P2 |
| 0.41.0 | 2026-07-03 | **Jornada do UE — visita guiada do dado passo a passo** (Projeto 2, pt/en/es/fr). Novo botão **"Jornada do UE"** na topologia: **15 etapas** seguindo o pacote do UE, do liga à internet, cada uma acendendo o(s) nó(s)+link(s) da etapa (resto esmaecido), com o **pacote animado no sentido certo** (ida e volta separadas), **selo obrigatório/opcional**, interface e porta. Cobre conexão física (RF), controle (N2/N1), autenticação (5G-AKA/SBI), sessão (N11), programação do user plane (N4/CUPS), IP, dados N3/N6 (uplink+downlink), e — o foco pedido — a **coleta e ação do RIC**: o near-RT coleta KPM pela E2 (dados que nascem na RU), decide nos xApps e **atua na RU** pela E2/RC (caminho real gNB→DU→RU no fronthaul 7.2), + o Non-RT/rApp treinando e enviando política pela A1. **+34 chaves i18n (578×4)**. Reusa o tour-box e a animação de fluxo; smoke estendido (15 etapas + botão escondido no P1) |
| 0.40.0 | 2026-07-03 | **Material do lab de RIC com IA integrado** (`pdfs/ric-ai/`): a disciplina **"Aplicações de IA e ML em RIC"** do Prof. **Julio Tesolin** — `MLRAN_A01.pdf` (Aula 01, 135 slides: SON→RIC, Near/Non-RT, xApp×rApp, "do modelo aos dados", fundamentos de IA; ferramental **KNIME + Python** scikit-learn/pytorch/tensorflow) — e as **4 bases de dados** dos casos de uso (`Base Fonts RIC/`): traffic/throughput, traffic load e energia (com variante boosting). O `traffic_prediction` (Throughput ← PRB/SINR/usuários) **é o UE-TP-rApp**, o tema do grupo; as wheels do scikit-learn aarch64 já vendorizadas casam com o ferramental da disciplina. O README de `ric-ai/` documenta conteúdo + dependências (bloqueio de 4 vCPU). Próximo passo: datasets PDF → CSV + pipeline Python starter |
| 0.39.0 | 2026-07-03 | **Corpo técnico traduzido — i18n de documentação COMPLETA** (pt canônico · en/es/fr). A **bíblia** (`core5g-arm64-bible.md`) + os **8 guias P2/RAN** (E2_FLEXRIC, E2_SERVICE_MODELS, KPM-ANALYTICS, KPM-COLETA-RESILIENTE, OAI-CORE-ARM64, INSTALACAO_GNB_OAI, PROJETO2-CPU, RAN) traduzidos nos 3 idiomas — somados aos labs (v0.38.0), fecham **todo o corpo de documentação** em 4 línguas. Estrutura idêntica ao canônico (fences/headings/tabelas batem nos 27 arquivos), glossário 3GPP/O-RAN preservado, código/comandos intocados, **links normalizados deterministicamente** (irmão traduzido → em-idioma; externos → caminho real; 0 regressões, 21 quebras remanescentes já existem no canônico). Cada `docs/i18n/<lang>/INDEX.md` ganha a seção "corpo técnico" + letreiro `docs/i18n/pt/`. Fecha o **ponto 1 do checklist do Prof. Jonas** de ponta a ponta (era 7/8 → **8/8**). Traduções por 15 agentes paralelos; 2 bíblias refeitas após limite de sessão. Também: `pdfs/` reorganizado em `base/` (curso) + `ric-ai/` (lab de IA) |
| 0.38.1 | 2026-07-03 | **Toolbar do console mais elegante**: copiar/limpar saíram da ponta direita e agora ficam **agrupados ao lado do status** ("ocioso"), como pílulas translúcidas com **ícone em traço** — **azul** (`var(--info)`) no copiar, **verde** (`var(--ok-fg)`) no limpar; cores theme-aware, legíveis nos 2 temas. Linha do console mais compacta e elegante. Kiosk continua escondendo os dois; i18n preservado (label em `<span data-i18n>`, SVG intacto; handler de copiar usa `setStatus`, não mexe no texto do botão) |
| 0.38.0 | 2026-07-03 | **i18n F6 — seletor com BANDEIRA + exercícios traduzidos + CI de paridade** (pt/en/es/fr). **Painel**: o `<select>` de idioma virou um seletor customizado com **bandeiras em SVG inline** (🇧🇷 PT · 🇺🇸 EN · 🇪🇸 ES · 🇫🇷 FR) — emoji de bandeira quebra no Windows (mostra "BR/US"), SVG desenha igual em todo SO; acessível (`role=listbox`, teclado, Escape, fecha ao clicar fora), nome nativo + check no ativo, centralizado no `i18n.js` (`mountLangMenu`, CSS injetado) p/ as 3 páginas não divergirem, e **nunca lança** (protege o login). Smokes atualizados p/ dirigir o widget. **Documentação dos exercícios traduzida** para en/es/fr: 7 roteiros do P1 (`docs/labs/`) + tutorial E2 do P2 = **8 arquivos × 3 = 24**, em `docs/i18n/<lang>/` (espelho do canônico, cabeçalho `<!-- sync: -->`). Glossário 3GPP/O-RAN preservado; blocos de código, comandos, caminhos e URLs intocados; links relativos reescritos p/ a nova profundidade (0 regressões — quebras remanescentes já existem no canônico). Estrutura verificada idêntica (fences/headings/tabelas batem nos 24). **Anti-apodrecimento**: novo `docs/i18n/GLOSSARY.md` (termos que não se traduzem + rótulos padronizados nos 4 idiomas) e **primeiro CI do repo** (`.github/workflows/i18n.yml`): paridade de dicionários + `check-parity.py` (defasagem via git) + smokes a cada push/PR |
| 0.37.0 | 2026-07-03 | **i18n F4+F5 — conteúdo didático completo + servidor/scripts** (pt/en/es/fr): F4 = anotações de serviço (`SERVICE_ROLES`), blocos "o que acabou de acontecer" (`TEST_EXPLAIN`, 5 testes), explicações de logs (`LOG_INFO`, 18 NFs), info-modais (arquitetura O-RAN, fluxo do teste, fórmulas Path Loss/SINR) e toda a Demo E2E/troca de projeto (títulos, confirmações, resumos) — resolvidos NO USO (respeitam troca de idioma), pt-canônico nos literais JS. F5 = cookie `c5g-lang` leva o idioma ao servidor: mensagens do `server.py` traduzidas (403 aluno, 409 vaga, 401, cabeçalho/rodapé do stream) e **`LAB_LANG` injetado nos scripts** — `testlog.sh` (×2 libs) traduz Resumo/O que fez/Resultado. **+145 chaves (544 × 4)**. Prosa interna dos scripts continua pt (migração incremental via LAB_LANG documentada) |
| 0.36.0 | 2026-07-03 | **i18n F3 — topologia quadrilíngue** (pt/en/es/fr): TODO o conteúdo didático dos DOIS diagramas traduzido — papéis e textos "de onde vem / o que faz / para onde vai" dos 35 nós, legendas de interfaces, camadas/bandas CUPS, tour guiado completo (2 projetos × 5 etapas), modos, hints, modal de nó (tipo/portas/rede/conexões/status) e logs. **+244 chaves (399 × 4 no total)**. Arquitetura anti-drift: os JSONs continuam pt-canônicos e o render usa `trf()` com fallback — em pt lê SEMPRE o JSON (dicionário nunca sobrepõe o canônico); pt das chaves de nós é gerado programaticamente dos JSONs. Seletor 🌐 na topologia com re-render completo na troca. Smoke estendido: chrome+nós+tour em francês nos 2 projetos |
| 0.35.0 | 2026-07-03 | **i18n F2 — painel inteiro em 4 idiomas** (pt/en/es/fr): barra de projetos (cards, ativar/desligar), rail completo (ferramentas, testes P1/P2, logs, histórico), console (status/copiar/limpar/mensagem inicial), banners (somente-leitura, AO VIVO, vaga de professor), modais de Resultados/Alunos/Demo (chrome, confirmações, prompts, vazios) e **UE Lab completo** (cadastro, ajudas de campo, condições de canal, botões de medição) — **+121 chaves** (155 × 4 no total), com re-render dinâmico na troca. Smoke estendido valida o corpo em espanhol. Falta: F3 (topologia/JSONs), F4 (scripts bash), textos didáticos longos (TEST_EXPLAIN/demo/infos — F3-didático) |
| 0.34.0 | 2026-07-03 | **i18n F1 — projeto internacional em 4 idiomas (pt/en/es/fr)** (decisão: traduzir TUDO; francês incluído). Painel: `static/i18n.js` (dicionários + `I18N.t`/`data-i18n`, fallback lang→en→pt, auto-detecção `navigator.language`, persistência `c5g-lang`), **seletor 🌐** e rota `/i18n.js` no-cache; **login + topbar traduzidos** (34 chaves × 4 idiomas). Glossário 3GPP/O-RAN não se traduz (regra no CONTRIBUTING §7). Testes novos: `npm run test:i18n` = paridade dos dicionários (chaves/órfãs/placeholders) + smoke funcional (troca de idioma real nos 4 + persistência). **Documentação**: `README.{en,es,fr}.md` completos com barra de idiomas 🌐; estrutura `docs/i18n/<lang>/` espelhando o canônico pt + `check-parity.py` (órfãos, marcador `<!-- sync -->`, defasagem via git). Faltam F2 (index inteiro), F3 (topologia), F4 (scripts via `LAB_LANG`) |
| 0.33.2 | 2026-07-03 | **Release de documentação de estado** — "uma pessoa nova consegue chegar até aqui". Novo [`docs/POLITICA-DE-CUSTOS.md`](docs/POLITICA-DE-CUSTOS.md) (ponto 8 do checklist: custos atuais ~US$28-30/mês, regras de operação, higiene de disco com causa-raiz, análise do upgrade p/ 4 vCPU do lab de RIC com IA + runbook de resize reversível). Novo [`server/panel/README.md`](server/panel/README.md) (arquitetura do painel + convenções que não podem quebrar: consoles escuros nos 2 temas/paleta TERM, verificador geométrico da topologia, versionamento). README raiz atualizado (fase atual = artigo, roadmap com checklist 7/8, mapa do repo com vendor/test/custos). Bible: §4 ganhou "Custos e higiene de disco" (lições dos volumes órfãos) e §10 registra o arco v0.32.0→0.33.1 + pendências i18n e lab de IA |
| 0.33.1 | 2026-07-03 | **Fix: navegador segurava painel ANTIGO no cache após deploys** — o professor via bugs já corrigidos ("cinza ilegível no claro", sem anotações didáticas) porque `/`, `/login` e `/topology` eram servidos SEM `Cache-Control` (cache heurístico do browser). Agora os 3 HTML vão com `no-cache, must-revalidate` (revalida a cada load; 304 quando não mudou — custo zero). Requer UM último hard-refresh (Ctrl+Shift+R); depois disso todo deploy chega na hora. Confirmado que o arquivo no servidor já tinha as correções (SERVICE_ROLES/TERM presentes) |
| 0.33.0 | 2026-07-03 | **Anotações didáticas na partida de serviços** (pedido do professor): quando um serviço/container sobe (docker compose `Container X Started/Healthy` ou os `Subindo/Iniciando X` dos scripts), o console anexa em AZUL uma descrição concisa do papel do componente — ex.: `oai-amf Started · AMF — registro e mobilidade do UE: porta de entrada do core (N1/N2)`. Dicionário `SERVICE_ROLES` cobre as NFs OAI e Open5GS, bancos, UERANSIM, gNB/nrUE e nearRT-RIC; funciona nos 3 consoles (principal, UE Lab, replay), com dedup de linhas consecutivas do mesmo serviço |
| 0.32.2 | 2026-07-03 | **Colorimetria ISO fixa em TODOS os terminais** (feedback do professor: relatórios de teste ficavam cinza/ilegíveis no tema claro). Causa: `ANSI_COLORS`/`tokenColor`/`lineColor` usavam variáveis de TEMA dentro dos consoles — que são escuros nos 2 temas; no claro, `var(--text)` virava quase-preto sobre preto. Agora os 3 renderizadores (console principal, UE Lab, replay de Resultados) compartilham a paleta `TERM` fixa (ANSI bright p/ fundo escuro: red #ff6b6b, green #69db7c, yellow #ffd43b, blue #74c0fc, cyan #66d9e8, magenta #da77f2 — 35/95 adicionados ao mapa SGR). Logs da topologia idem: corpo do modal virou terminal escuro fixo com paleta fixa |
| 0.32.1 | 2026-07-03 | **Fixes do tema claro + higiene do servidor** (feedback do professor). Painel: blocos didáticos (`.explain`/"Ver logs") dentro do console voltaram à paleta fixa de console — ficavam ilegíveis no claro (texto escuro sobre console escuro); foco visível no teclado + `prefers-reduced-motion` nas 3 páginas. Topologia: bolinhas do modo Fluxo com cor forte no claro (`--packet` #d9480f + contorno), bandas CUPS mais presentes (fill .13/stroke .6 no claro, .07/.45 no escuro), chips de rótulo brancos no claro; **imagens dos nós corrigidas p/ o stack real** (v2.2.1 e mysql:9.6.0 — mostravam v1.5.1/8.0). Servidor: **limpeza de disco 3.1G→8.6G livres** (16 volumes MySQL anônimos órfãos = 3.1GB + imagem dangling 660MB + journal 200MB + apt; depois, com aval do Henrique, imagens do stack legado OAI v1.5.1 + mysql:8.0 = ~2.6GB — oficiais, re-puxáveis; o oai-upf-vpp arm64 portado foi preservado); **causa-raiz corrigida** com volume nomeado `mysql-data` no compose do P2 (aplicar com `./deploy.sh sync-oai`; vale no próximo up). Docs: `E2_FLEXRIC.md` ganhou "Versões e codificação" (FlexRIC 2.0.0, E2AP ASN.1, FlatBuffers não usado) |
| 0.32.0 | 2026-07-02 | **Topologia CUPS + tema claro/escuro** (pontos 1–7 do checklist do Prof. Jonas). Topologia (P1 e P2): core dividido em **Plano de Controle (SBA, azul)** e **Plano de Usuário (laranja)** com bandas de fundo rotuladas (ênfase em CUPS); **N1 explícito** (tracejado UE↔AMF, interface lógica via gNB) e link AMF→SMF rotulado **N11/Nsmf**; layout re-gradeado com **nenhuma linha atravessando card de terceiro** — corrige o "RIC→UPF" apontado pelo professor (gNB/RIC/UPF na mesma coluna) e +6 travessias ocultas (mysql fora do canvas incluso); links paralelos (N1/N2 no P1) com offset perpendicular; IPs/portas padronizados (`N2: 38412/SCTP · SBI: 80/TCP`); tour por projeto com etapas CUPS; telemetria do P1 re-apontada ao NRF. **Tema claro/escuro** nas 3 páginas (toggle ☀/☾ persistido em localStorage, aplicado antes do paint; consoles/logs continuam escuros nos 2 temas p/ preservar a colorização). **Novos testes**: `check-topology.py` (verificador geométrico, CI-friendly) + `topology-smoke.js` (render headless P1/P2: bandas, N1, N11, offset, 4 modos, tour, tema) via `npm run test:topo`. **Vendor**: wheels aarch64 do scikit-learn p/ os RICs Near-RT/Non-RT (fora do git, política de binários; `server/panel/vendor/README.md`) |
| 0.31.2 | 2026-07-02 | **Fix logout confiável**: o `delete_cookie` agora repete os **mesmos atributos** do `set_cookie` (Secure/HttpOnly/SameSite/Path) — navegadores estritos ignoram a remoção quando os atributos não batem, e o aluno "voltava logado" ao abrir `/`. Front-end: `location.replace` no logout tira o painel do histórico (Voltar não reabre a sessão) |
| 0.31.1 | 2026-06-22 | **Fix: nó "xApps" da topologia parava de "levantar" (falso-vermelho)**. xApps são sob demanda e encerram no 1º evento (~2s), então `statusKey: proc:xapp_` nunca casava um processo vivo. Atrelado ao RIC (`proc:nearRT-RIC`): o nó fica **verde sempre que a plataforma de xApps está disponível** (RIC no ar). Infra do xApp validada ao vivo (cust/kpm assinaram E2 mesmo em load 12). Também: restaurado o login de aluno (guest) que o `.env` do Drive havia travado |
| 0.31.0 | 2026-06-22 | **Segurança: coletor KPM nunca mexe no cpuset + dependência de 4 vCPU documentada**. Forçar UE+tráfego nos 2 cores (removendo o guardrail) **congelou o box 2×** (reboots). `kpm_collect_real.sh` reescrito p/ **não tocar no cpuset** — em 2 vCPU detecta que o UE não attacha, **para o UE** e conclui honesto ("use 4 vCPU"); em 4 vCPU attacha sozinho. Heartbeat **dedup** (marcos distintos). **Demonstração segura** validada (análise sobre amostra). Documentado em README (roadmap), `KPM-COLETA-RESILIENTE.md` (⚠️ topo), bible §10: **relatório completo de KPM com throughput real depende de upgrade p/ 4 vCPU** |
| 0.77.1 | 2026-08-28 | **Os arquivos que desenham entram no sistema.** `mini-map.js`, `flow-strip.js`, `energy.js` e as traduções do `i18n.js` guardavam CSS-em-JS com os valores antigos: **188 literais trocados por papéis**. Os três componentes são superfícies escuras nos dois temas — receberam o mesmo escopo `.superficie-escura` do console, e daí em diante os papéis dos filhos resolvem sozinhos, sem uma linha de cor fixa. Verificado abrindo o mapa **sobre a página clara**: 16,00:1, escopo aplicado, zero erro de JavaScript nos dois temas. As **bandeiras** (Brasil, EUA, Espanha, França) ficam como estão — bandeira não é token. Literais fora do `tokens.css` no projeto: **239**, agora quase todos cores de gráfico das páginas de ML e do desenho da topologia |
| 0.77.0 | 2026-08-28 | **O lab, o login e a topologia entram no sistema — e a acentuação volta.** As 11 páginas do lab tinham **cada uma a sua cópia da paleta**: 26 blocos de cor distintos, com deriva entre eles. Foram **678 declarações de cor removidas**, trocadas por uma ponte única (`lab/lab-ponte.css`) de 20 nomes. Duas famílias novas nasceram de necessidades reais, não de gosto: **contraponto** (hue 200), porque o Lab de IA opõe supervisionado × não supervisionado o tempo todo e um par precisa de dois matizes; e a **rampa categórica** de 8 matizes igualmente espaçados, porque a topologia distingue 8 domínios de rede — ali cor é **identidade de domínio, não estado**, e não pode sair do verde/âmbar/vermelho que naquela tela querem dizer *no ar / atenção / fora*. **Defeito grave achado ao olhar o render:** sete páginas do lab exibiam *"RegressÃ£o"*, *"nÃºmero"* — a etiqueta `<meta charset>` não estava lá, e o meu `grep -L charset` de antes deu **falso-negativo** porque a palavra "charset" aparecia enterrada num script. Daí o teste novo **`test/paginas.js`**, que mede a **posição** da etiqueta (tem de caber no primeiro kilobyte, que é tudo que o navegador lê) e exige que toda página que pinta carregue a identidade — foi ele que encontrou o `login.html` e a `topology.html` ainda de fora. Verificado: 12 páginas do lab × 2 temas sem erro de JavaScript, e acentuação correta em todas |
| 0.76.0 | 2026-08-28 | **O painel inteiro sobre o sistema: 250 literais de cor → 4.** Migrado o que faltava, e cada categoria pediu uma solução diferente. Os **atributos SVG** do Painel do UE não aceitam `var()`, então viraram `style="fill:…"` sobre os papéis que o `.uep` já declarava. Os **38 estilos embutidos** no JS foram mapeados como o CSS. As **sparklines do rádio** perderam o mapa de cores: SNR era azul, MCS laranja, PRB **verde** e BLER **vermelho** — quatro gráficos de UMA série cada, onde o rótulo ao lado já nomeia a métrica, e a cor só mentia (BLER vermelho parecia "ruim" mesmo em zero; PRB verde parecia "bom" mesmo saturado). Agora todas usam o acento, pintadas por CSS, e o mapa de cores saiu junto com o parâmetro de `renderSpark`. A **paleta ANSI do terminal** passou a nascer dos papéis onde ANSI e o sistema querem dizer a mesma coisa (vermelho, verde, amarelo, azul, cinza, tinta); ciano e magenta não têm equivalente e seguem constantes. Isso só foi possível porque o console ganhou escopo na 0.75.1 — o comentário antigo dizia *"aqui NUNCA se usa variável de tema"*, e a regra caiu com a causa. Verificado: as três cores de log medem **9,3:1 ou mais** contra o fundo do console, **idênticas nos dois temas**. O teste 0.c passou a cobrir isso. Restam 4 literais: o scrim de cada tema e os dois ANSI |
| 0.75.1 | 2026-08-28 | **O console volta a ser legível no tema claro — e eu tinha quebrado.** Ao migrar os literais do painel para os papéis, `color:#e6e6e6` do `#output` virou `var(--ink)` — que no tema claro é tinta **escura**, sobre um console **preto**: **1,42:1**, texto praticamente invisível. A cor estava fixa de propósito, com um comentário duas linhas abaixo avisando (*"vive dentro de consoles escuros (dois temas): cores fixas"*), e a substituição mecânica passou por cima. A correção não é voltar a fixar cor: o console ganhou **escopo próprio** — `.superficie-escura` redefine as primitivas para a escala escura, e toda regra filha que usa `var(--ink)`, `var(--line)` ou `var(--surface)` acerta sozinha nos dois temas. Três regiões estavam afetadas: o `#output`, o bloco `.explain` e o **Painel do UE**. Resultado medido: **1,42:1 → 16,00:1**, idêntico nos dois temas. Teste novo **0.c** mede o contraste do console em claro e escuro e reprova abaixo de 4,5:1 — verificado removendo só a correção e vendo falhar (1,54:1). O resto da migração seguiu: **122 literais** viraram papéis dentro do `<style>`, os `rgba()` das cores antigas viraram `color-mix` sobre o token, e as duas sombras soltas passaram a usar `--elev-1/2`. Literais no `ops/index.html`: **250 → 67**, e os 2 que restam no CSS são o scrim de cada tema |
| 0.75.0 | 2026-08-28 | **A identidade entra no painel — e os testes deixam de ser cegos.** O `ops/index.html` passou a carregar o `tokens.css` e teve os **dois blocos de cor removidos** (58 declarações), trocados por uma **ponte**: os nomes antigos (`--panel`, `--text`, `--green`…) continuam válidos, mas o valor vem dos papéis do sistema — nenhum dos ~250 usos precisou mudar, e o arquivo ganhou claro e escuro coerentes de uma vez. O acento do painel era **laranja** (`#e8590c`), vizinho do âmbar de atenção: duas cores brigando pelo mesmo significado. Agora é o violeta do sistema. O rosa do **AO VIVO** ganhou família própria (hue 350) em vez de virar acento — é o único momento em que a sala inteira vê a mesma tela, e merece cor. **Descoberta no caminho:** os três testes de fumaça carregavam as páginas por `file://`, onde `/static/tokens.css` aponta para a raiz do disco — o painel era renderizado **sem a folha de identidade** e tudo passava assim mesmo. Verde falso, cego para uma classe inteira de quebra. Agora sobem um servidor estático (`test/servidor.js`) e carregam por HTTP, com asserção nova que **falha** se os tokens não vierem — verificada apagando o arquivo de propósito. Literais de cor no `ops`: **250 → 192** |
| 0.74.1 | 2026-08-28 | **Tabela normal de sinalização; daltonismo sai de escopo.** A 0.74.0 tinha distorcido a lightness das cores de estado para maximizar separação sob dicromacia — decisão revista: a paleta passa a seguir a **tabela normal**, cada cor na lightness em que *parece* a cor padrão (âmbar a 0,64 virava mostarda; vermelho claro demais vira rosa). Adaptação para daltonismo é estudo à parte, aplicado como **função sobre esta tabela**, não redesenhando a paleta. O que fica é a **colorimetria a serviço da programação visual**: contraste WCAG medido em todo par prometido, nos dois temas, por `tools/identidade/medir.py`, que **sai com código != 0 quando reprova** — serve de porta em CI. Corrigido também um defeito de rampa: nas famílias de estado o degrau 10 saía **mais claro** que o 9 (âmbar e vermelho), porque o 9 sai da curva e o 10 não saía junto; agora o 10 é a variante de passagem do mouse derivada do 9. As ferramentas foram reescritas para rodar **do repositório** (`tools/identidade/{oklch,paleta,medir,gerar_tokens}.py`) — antes apontavam para arquivos de rascunho e não eram reproduzíveis |
| 0.74.0 | 2026-08-28 | **Identidade visual: o painel deixa de ser pintado à mão.** Havia **225 literais de cor** em 20 arquivos (114 só no `ops/index.html`) e **186 dos 250 usos escritos direto na regra**, furando os tokens: dois azuis para a mesma coisa, três nomes para "deu certo", e — o pior — no `ops/index.html` e no `topology.html` **o tema claro era a única definição existente**, com o escuro sendo o que sobrava, enquanto no lab era o contrário. Agora existe sistema: cores pensadas em **OKLCH** (lightness perceptualmente uniforme, como Radix e Tailwind v4), **12 degraus com papel fixo** por família, e **duas camadas** — primitiva (a cor) e semântica (o papel) —, com a tela usando só a semântica. Claro e escuro **não são inversão**: cada um tem a sua curva, o escuro parte de `#111112` e a elevação nele é superfície mais clara, não sombra. Tudo **medido**, não julgado a olho: contraste WCAG em todos os pares (o `--line-strong` do claro foi remapeado do degrau 8 para o 9 porque o 8 media 1,94:1 e limite de componente pede 3:1) e separação sob daltonismo por simulação de Viénot + ΔE em OKLab — **verde × vermelho em 9,5**, acima do alvo. Verde × âmbar fica em 7,3 sob protanopia, na faixa que só vale com reforço, então virou **regra dura: estado nunca por cor sozinha** — cor + glifo + palavra, e o ponto de estado com anel obrigatório. Tipografia com **duas vozes**: o painel fala em monoespaçada (é instrumento, e tabela de teste precisa de dígito de largura fixa), a aula fala em sans. Prancha viva em `/static/design/identidade.html`, receita em [`docs/identidade-visual.md`](docs/identidade-visual.md), geradores em `tools/identidade/`. Junto: `lab-hub.html`, `lab-fundamentos.html` e `lab-projeto.html` **não tinham `<meta charset>`** — o hub renderizava "RIC â€" do zero" fora do FastAPI. As telas ainda NÃO usam os tokens; a migração é o próximo passo |
| 0.73.0 | 2026-08-28 | **O aluno registra o que acertou e o painel mostra a fração.** Os exercícios do professor entraram na 0.72.0 como lista de links; faltava o que interessa de verdade — **quantos por cento do total o aluno acertou**. Cada cartão agora mostra quanto o exercício vale, o aluno anota o que acertou ao terminar na plataforma, e a cadeira ganha uma linha de resumo (*89% de acerto — 2 de 7 exercícios registrados, 39 de 44 pontos*). A pontuação bruta não serve para comparar exercícios de tamanhos diferentes (9 e 22 pontos); a fração serve. O **denominador saiu do bundle da própria plataforma** — a estrutura de pontuação dos componentes — e cobre 23 dos 26 exercícios: as 14 aulas dos Módulos 07 e 09 e as 4 interfaces do 05 valem **22** (Conceitos 3 · Cenários 6 · Profundidade 3 · Sequência 10), fronthaul/eCPRI/ML/workflow e a aula 01 valem **9**. Os 3 que usam componente próprio ficaram **sem total declarado** em vez de receber um número inventado: nesses, o formulário pede os dois números. Onde o total é conhecido, ele vem do catálogo e **o navegador não escolhe o denominador** — o servidor recusa hash fora do catálogo e acerto fora do intervalo. Guardado por **e-mail**, não por login, porque os alunos entram todos pelo mesmo usuário convidado; cada um lê e escreve só o próprio, ninguém vê o de ninguém. Escrita atômica (temporário + `replace`), então uma queda no meio não deixa arquivo pela metade |
| 0.72.0 | 2026-08-28 | **Os exercícios do professor entram no painel.** O Prof. Jonas mantém as atividades das três cadeiras numa plataforma própria (Cloud Run, participação e conclusão contam na nota) e elas viviam fora do nosso caminho de estudo — quem abria o Estudo 4 não tinha como saber que existiam. Agora cada cadeira termina com **os exercícios daquele módulo**: **Módulo 05 → Estudo 1** (12), **Módulo 07 → Estudo 2** (7), **Módulo 09 → Estudo 4** (7), cada um com link direto para o seu exercício. O **Estudo 3** não tem módulo próprio na plataforma e recebe, com o aviso na tela, os **3 de IA/ML** que moram no Módulo 05. O painel **não copia enunciado nem responde nada por lá**: lista, leva até o exercício e — a parte que interessa — liga cada um ao que já temos, com a linha *"Prepare-se aqui"* apontando para a aula da cadeira, a página do Lab de IA ou o **comando do console** que treina aquilo (Interface A1 → `p2-test-a1`, KPIs e QoE → `p2-kpi-qoe`, EDA/ETL → `p2-kpm-analytics`). **Sem hardcode**: o domínio da plataforma fica uma vez só em `index.plataforma`, os itens guardam só o hash, e os rótulos dos comandos saem do catálogo (`p2-kpi-qoe` estava rodando desde a 0.65.0 sem rótulo nenhum). O teste de paridade i18n passou a cobrir **dois** dicionários — o `lab-i18n.js`, onde vive toda a moldura dos Estudos, estava fora dele: 893 chaves × 4 idiomas |
| 0.71.2 | 2026-08-28 | **Botão Topologia como o professor pediu**: ícone de rede (núcleo + 4 nós ligados), **apagado** enquanto nenhum projeto está no ar e **aceso** quando um liga — e o rótulo diz qual topologia vai abrir: *Topologia · P1* com o Projeto 1 no ar, *Topologia · P2* com o Projeto 2. O clique deixa de ser aposta |
| 0.71.1 | 2026-08-28 | **O botão da Topologia tinha sumido** — ao virar item fixo do grupo "Apresentar", ele saiu do conjunto do Projeto 2, que só tinha ele e ficou um `<div>` vazio: quem procurava onde sempre esteve não achava nada. O grupo subiu para o **topo do rail** (antes vinha depois dos conjuntos por projeto), o casco vazio saiu, e os quatro itens agora **apagam sem projeto no ar e acendem quando um liga** — o brilho conta o mesmo que as telas vão contar, porque elas mostram o estado vivo da rede. O **Mapa da rede** deixou de abrir com um aviso de "nenhum teste rodou": desenha a rede do projeto em foco, tudo apagado, e acende no teste |
| 0.71.0 | 2026-08-28 | **Grupo "Apresentar" no menu: as telas de infraestrutura deixam de se esconder.** As quatro telas que explicam a rede já existiam, mas estavam espalhadas e presas ao projeto ativo — a Topologia eram dois links, um dentro de cada conjunto por projeto, e a Arquitetura O-RAN era um botão solto no fim do grupo de logs. Agora vivem juntas no topo do rail, **sempre visíveis**: **Mapa da rede** · **Topologia e jornada do UE** (o tour pelas camadas e o caminho do dado) · **Arquitetura O-RAN** · **Containers e o que cada um faz** (abre a tabela com nome, função, CPU e RAM dos 28 containers). Explicar a rede não depende de ter projeto no ar, e era exatamente isso que as escondia; o link da topologia passou a seguir sozinho o projeto ligado |
| 0.70.0 | 2026-08-27 | **Mapa: um botão em cima, abre à parte.** O mapa deixou de disputar espaço com o resultado: o botão saiu da barra do console e foi para o topo, ao lado do liga/desliga (com o pulso âmbar enquanto um teste roda), e a janela abre **sobre a tela**, com o fundo escurecido, fechando no ✕ ou clicando fora. Sumiu o modo "encostada" e, com ele, a faixa que o console reservava, a classe `mm-docked` e o segundo estado de tamanho — menos código e uma decisão a menos para quem usa |
| 0.69.0 | 2026-08-27 | **A resposta virou tela: o Painel do UE.** A pergunta do professor ("o que temos sobre vazão do usuário e qual é a decisão?") era respondida por uma parede de números; agora o teste desenha a resposta **no ato**, dentro do console. É o "painel mínimo" do material — **headline + 2 cartões + 1 série temporal** — mais o caminho do dado em 4 passos: **coletado → tratado → resultado → ação**, fechando com o que os dados **não** permitem dizer. O motor emite uma linha `#PAINEL {json}` com os números **já calculados** (o navegador só desenha: a figura não pode divergir da tabela impressa). Gráfico segundo a régua de visualização: série única com a cor validada contra o fundo do console (banda de luminância, croma e contraste), **sem eixo duplo** (o PRB é cartão, não segundo eixo), bandas de fase em cinza para a cor ficar reservada ao dado, rótulo direto só no pico (é ele que explica média × mediana) e **crosshair com tooltip** no mouse. Estado nunca por cor sozinha: cada cartão traz a palavra ao lado do ponto |
| 0.68.1 | 2026-08-27 | **Os instrumentos explicam a si mesmos, e param de fingir que estão vivos.** Passar o mouse em cada medidor abre o que ele é e como lê-lo: nos 4 do rádio, os limiares do deck da aula 04 (SNR bom acima de 20 dB, MCS 28 é o teto, PRB acima de 80% é pressão de capacidade, BLER zero porque o canal é ideal) com o RFSIM dito em voz alta — é ele que explica por que quase não se mexem; nos 4 do servidor, o valor real mais o que aquele número significa, com destaque para o **swap**, cujo primeiro byte acima de zero é o sinal mais confiável de que o box vai travar. E a faixa de rádio ganhou **idade da amostra**: o gNB pode estar vivo e ter parado de reportar, e antes o painel mostrava o último número com a bolinha pulsando; agora, sem linha nova no log por mais de 10s, o quadrante esmaece, o pulso para e o título diz há quanto tempo aquele número é passado |
| 0.68.0 | 2026-08-27 | **Cabine de vidro: a tela inteira em 2 linhas.** O controle do laboratório virou **dropdown do projeto + botão de energia** ao lado do título — o painel é exclusivo, então um seletor diz o que dois cartões diziam, e o estado (LIGADO/DESLIGADO/PARCIAL/MUDANDO) mora no próprio botão. A régua de instrumentos virou **3 quadrantes com moldura e legenda** — SERVIDOR · SERVIÇOS · RÁDIO·E2 — para o olho ir direto. A **telemetria do servidor ganhou barra de progresso real e média móvel** (60 leituras, cerca de 2 min): a marca da média sobre a barra separa pico de regime. **Sem hardcode**: o total de PRBs agora vem do próprio gNB (`N_RB_DL` do log) em vez do `/ 51` escrito na tela; moldura, raio, legenda e a pilha monoespaçada viraram variáveis CSS únicas. **Sem dead code**: removidos 5 regras CSS órfãs, 2 funções nunca chamadas, o chip duplicado do topo e 8 chaves i18n sem dono. Rail e console adotaram a mesma gramática (moldura + legenda âmbar) e o log ganhou tipografia melhor (`ui-monospace`, 12px, entrelinha 1,65 — monoespaçada continua obrigatória por causa das tabelas alinhadas dos testes) |
| 0.67.0 | 2026-08-27 | **Barra de estado redesenhada: uma linha, e só o que está no ar.** A 0.66.0 tinha achatado a altura mas mantido os dois projetos lado a lado, cada um ocupando meia tela — largura desperdiçada com o projeto DESLIGADO e um vão no meio. O painel é exclusivo (um projeto por vez), então agora: o projeto **no ar** aparece inteiro (estado + servidores + desligar), as **métricas de rádio ocupam a sobra da mesma linha** (o `#ran-live` passou a viver dentro da barra — ele só existe quando o P2 está no ar) e o outro projeto **encolhe** para um botão de trocar no canto; sem nada no ar, os dois aparecem iguais, que é o único momento em que a escolha importa. A **sparkline só é desenhada quando o valor muda** — com o rádio simulado a linha reta atravessando a tela era ruído. Saiu também a duplicação do topo (o chip "Projeto X no ar" dizia o mesmo que a barra 40px abaixo), com CSS, JS e 12 chaves i18n órfãs removidos junto. Na projeção some só o projeto ocioso: o que está no ar continua na tela. **154px → 37px** de cabeçalho; o console foi a 655px |
| 0.66.0 | 2026-08-27 | **Cabeçalho enxuto e texto que se entende.** (1) Cada projeto virou **uma linha**: nome + o estado em **uma palavra colorida** (LIGADO verde · DESLIGADO vermelho · PARCIAL âmbar quando só parte subiu · MUDANDO piscando), com os servidores como chips pequenos e o botão à direita — o cabeçalho caiu de **154px para 71px**. (2) O log de **ativação** (modal de operação) passou a usar a mesma colorimetria ISO do console: verde = subiu (`Started`/`Healthy`), amarelo = subindo (`Creating`), vermelho = erro, azul = INFO — e a **anotação didática** "· o que este componente faz" agora aparece ali também. Antes era tudo cinza. (3) A faixa **RAN ao vivo** virou régua de 26px (era 90): mesmos 4 indicadores e sparklines, um oitavo da altura — os números do RFSIM quase não mudam e não mereciam aquele espaço. (4) **Revisão de texto teste por teste**: cada um dos 18 testes ganhou um bloco `antes` escrito no **futuro** ("vai pegar o log…") — o pré-voo mostrava os textos do `items`, que são escritos no passado ("leu o log…"), e narrava como já feito o que nem tinha começado; e a notação ambígua saiu de todo o painel e dos 4 dicionários (`~1 indicação/s` → "cerca de uma linha por segundo"; `~XGBoost` → "equivalente ao XGBoost"; `split 70:30` → "treina nos primeiros 70% do tempo e testa nos últimos 30%") |
| 0.65.2 | 2026-08-27 | **O mapa saiu da coluna do console: virou janela própria.** Com mapa + faixa de percurso + explicação na mesma coluna não sobrava tela para o resultado — que é o que se lê. Agora o mini-mapa é uma janela com dois tamanhos: **reduzida**, ancorada à direita, com o console **reservando** a faixa (padding) para o texto refluir em vez de ficar coberto; e **expandida**, modal com fundo escurecido e o mapa em tamanho legível. Fechada por padrão, abre pelo botão **🗺 mapa** na barra do console, que **pisca enquanto um teste corre** — o mapa não sobe sozinho por cima do log. Tamanho e estado ficam no navegador. Em tela estreita (<1120px) não há faixa a reservar e a janela sobrepõe mesmo. O log do console dobrou de altura (267→546px em 1440×900) |
| 0.65.1 | 2026-08-27 | **O "desligar" do Projeto 2 obedece** e **a tela que ensina antes de rodar**. (1) O botão do meio (E2 lab) nunca apagava: o `nearRT-RIC` sobe como **root** (`sudo systemd-run --unit=oai-flexric`) e o `down_flexric.sh` o matava com `pkill` **sem sudo** — o painel roda como `ubuntu`, o kill voltava *Operation not permitted* e o erro sumia no `|| true`. Agora os scripts de parada **param a unit** (`oai-flexric`, `oai-gnb`, `oai-nrue`), usam `sudo` e **conferem o que sobrou** em vez de anunciar sucesso; `process_running()` passou de `pgrep -f` para `-x` (nome exato), senão um `tail` de log ou o próprio `pkill` acendiam o botão. Validado no servidor: RIC de root, saída limpa, unit `inactive`. (2) **Guia da aula no pré-voo** (`GUIA`, começando pelo **T1 do Grupo 6**): o que faz · de onde vem o dado (rádio → gNB → E2 → xApp → arquivo) · por onde passa (bronze/silver/gold da aula 03) · **os dados de verdade** (novo `GET /api/lab-data/kpm/preview`: fonte em uso, nº de medições, fases e as 6 primeiras linhas) · a fórmula símbolo por símbolo · o que o teste vai fazer · como ler o resultado. A explicação pós-execução do T1 virou aula também: como ler a tabela, as duas correlações, o que vai no checkpoint e o que os dados **não** permitem afirmar |
| 0.65.0 | 2026-08-27 | **Teste da Aula 04 no painel** — os slides saíram (`pdfs/03-dados-telecom/aula04-kpis_kqis_qualidade.pdf`, 82 págs.) e viraram comando: **`p2-kpi-qoe`** percorre a cadeia do deck sobre a MESMA telemetria dos 7 temas — medida KPM → KPI (PRB, vazão, atraso por fase) → KQI (% do tempo acima de L) → **QoS** (4 cláusulas didáticas **calibradas no baseline**, porque limiar absoluto que já dispara no repouso mede a escolha do limiar, não a rede) → **QoE só como proxy** (não há MOS no lab) → diagnóstico capacidade × canal/jammer → **anatomia dos indicadores do Checkpoint 2** (nome · fórmula · unidade · granularidade · fonte · alvo · papel · limite de validade). Diz também o que o artefato **não** permite: das 6 famílias de KPI do slide 23, só Integridade e Utilização saem dos dados. Motor `scripts/temas/aula04_indicadores.py` (stdlib, reaproveita o loader dos temas); cena própria de 5 nós no flow-strip com pré-voo por degrau, mini-mapa e i18n nos 4 idiomas |
| 0.64.3 | 2026-08-25 | **Console dos testes legível de novo**: o mini-mapa "onde está rodando" engolia a coluna inteira (SVG 1300×900 a 100% de largura ⇒ ~790 px) e o log do teste sobrava como **uma linha ilegível no rodapé**. Causa raiz: a classe `.mm-box` nunca era aplicada ao host, então todo o CSS do mapa (caixa, altura, `.closed`) era letra morta — o clique no cabeçalho também não recolhia nada. Agora o mapa entra como **janela** (escala cheia, legível) já rolada até os nós acesos, com **⤢ tamanho real** e **▾ esconder** (escolha guardada no navegador); `#output` ganhou piso de 200 px e a coluna do console rola quando o mapa é aberto inteiro |
| 0.64.2 | 2026-08-25 | **Unidades das KPMs corrigidas** em todo o sistema e no CP1: `DRB.RlcSduDelayDl` em **µs** e `RRU.PrbTotUl` em **%** (slide 66 da aula 01 + log do FlexRIC; antes ms/PRBs); limiar do T3/T7 passa a marcar mudança de regime (100 µs), não QoE. Aula 04 do Estudo 4 (KPIs, KQIs, QoS e QoE) como **prévia** montada do plano de ensino (badge + nota até os slides saírem). Páginas `/lab/estudo/*` e `/lab/estudo/*/aula/*` em **pt/en/es/fr** (moldura via `lab-i18n.js`; conteúdo por `<id>.<lang>.json` com fallback pt). Cartão de fonte de dados (💾) rediagramado: rádio · rótulo · ação numa linha, arquivo/colar alinhados. IAM: `infra/iam-core5g-ops-policy.json` pronto para o admin anexar |
| 0.64.1 | 2026-08-25 | Pré-voo e "o que acabou de acontecer" próprios para os 8 comandos `p2-tema-*` (`TEST_EXPLAIN`): o que cada tema calcula, a fórmula dos 2 indicadores e a leitura, antes e depois de rodar |
| 0.64.0 | 2026-08-25 | **Estudos por cadeira (Fase C)**: rail do console com um dropdown por disciplina (Interfaces O-RAN · RIC · IA/ML em RIC · Análise de Dados), aulas detalhadas extraídas dos slides como JSON plugável (`static/lab/estudos/`, hubs `/lab/estudo/{n}` e aulas `/lab/estudo/{n}/aula/{k}` com objetivos, conceitos, fórmulas, "onde roda" no mini-mapa, exercícios e quiz) e **os 7 temas do projeto integrador** da disciplina 03 como comandos (`scripts/temas/temas_projeto.py`, stdlib; fórmulas impressas antes dos números; T2 = `robust-baseline-mad` do professor; política A1 só em dry-run) com fonte de dados trocável (amostra do professor · arquivo · colado à mão, `/api/lab-data/kpm`). Doc: [`docs/estudos-por-cadeira.md`](docs/estudos-por-cadeira.md) |
| 0.30.0 | 2026-06-22 | **Coleta KPM resiliente p/ apresentação** (`scripts/kpm_collect_real.sh`): coleta com tráfego real, **100% por evento (zero tempo)** — espera o UE attachar (`ip monitor`), coleta K indicações (`grep -m K`), heartbeat "não travou" por evento de log, **auto-retry** com diagnóstico, **auto-revert** do cpuset (trap) e **watchdog anti-hang** (`tail -f --pid /dev/null`). Botão no painel + guia milimétrico [`KPM-COLETA-RESILIENTE.md`](server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md). Resolve o "0 indicações" (coleta começava antes do attach) e atende o pedido: não trava, não perde o teste, completa sempre |
| 0.29.0 | 2026-06-22 | **Pipeline de análise KPM (Dados na RAN)**: novo `scripts/kpm_analytics.sh` — implementa o "exportar o lab para análise" da Aula 06 (slide 46): parseia `xapp_kpm_lab.log` (texto bruto E2SM-KPM) → série temporal CSV → KPIs por UE (throughput médio/máx, PRB) → sparkline ASCII, tudo didático (Coleta→ETL→KPI→Viz→Decisão, com o "porquê"). Amostra `scripts/samples/kpm_sample.log` + guia [`KPM-ANALYTICS.md`](server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md). Ponte p/ o UE-TP-rApp e o Módulo 7 |
| 0.28.0 | 2026-06-22 | **User plane do P2 validado no servidor + guia de CPU/reprodução**: religado o lab P2 (core v2.2.1 + RIC + gNB), E2 SETUP OK, xApps KPM/cust/RC subscritos. UE attacha e pega IP `12.1.1.2` com **ping 0% perda** — o gargalo era **CPU** (2 vCPU + cpuset = gNB e UE num core → RRC inunda), resolvido liberando os 2 cores (timer-free: `trap EXIT` + `wait -n` + `nice -20`) ou usando **4 vCPU**. Novo guia [`PROJETO2-CPU-E-USERPLANE.md`](server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md); bible §4/§7.c/§10 e README atualizados |

---

## [0.28.0] — 2026-06-22

**User plane do Projeto 2 validado no servidor real + guia de reprodução/CPU.**

Religado o lab P2 no Graviton (core v2.2.1 + near-RT RIC + gNB) e validado fim a
fim, tudo **event-driven (zero tempo)**:
- **E2 SETUP** gNB↔RIC: `[E2-AGENT]: E2 SETUP RESPONSE rx`.
- **xApps**: KPM (RAN_FUNC_ID 2), cust (142), RC (3) — todos subscritos.
- **User plane**: UE attacha, `oaitun_ue1 = 12.1.1.2`, `ping 8.8.8.8` → **4/4, 0%
  perda, RTT ~111 ms**.

**Descoberta:** o UE não pegava IP por **CPU**, não pelo bug AUSF↔UDM (esse era do
core v1.5.1). Em 2 vCPU com o guardrail de cpuset (lab num só core), gNB e UE
dividem o core e o RRC do UE inunda (`TASK_RRC_NRUE task contains` 71k→112k).
Liberando os **2 cores** (`AllowedCPUs=0-1`) — ou usando **4 vCPU** — o UE attacha
normal. Trade-off no box de 2 vCPU: **ou** proteção anti-freeze (1 core, sem UE)
**ou** user plane (2 cores, box dedicado).

**Procedimento timer-free** (o usuário "não gosta de nada com tempo"): liberar/
reverter os 2 cores sem cronômetro — `trap revert EXIT`, espera por evento
(`ip monitor address` p/ o IP, `tail -F --pid | grep -m1` p/ o flood, `wait -n`),
monitor em `nice -20` (garante o revert mesmo sob saturação).

**Doc:** novo guia [`server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md`](server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md)
— reprodução completa até o user plane, **4 vCPU (recomendado) vs 2 vCPU
(alternativo)**, com o script de teste auto-revert. Bible §4 (RAM/instância), §7.c
(CPU/user plane), §10 (UE resolvido), §11 (referência) e README (roadmap)
atualizados.

---

## [0.27.0] — 2026-06-21

**`oai-upf-vpp` portado para arm64 — o "não portável" caiu.** Por meses o
UPF-VPP foi documentado como impossível em ARM. Investigando a fonte, o bloqueio
real era **uma única dependência**: o **Hyperscan** (`libhyperscan-dev`), regex
SIMD da Intel (SSE/AVX), inexistente no Ubuntu arm64. O plugin UPF da Travelping
a busca via `pkg_check_modules(HS libhs)`.

**Solução — Vectorscan.** O [Vectorscan](https://github.com/VectorCamp/vectorscan)
é o fork portável do Hyperscan (ARM NEON 100% funcional, API/ABI-compatível,
mesmo SONAME `libhs.so.5`). É **drop-in**: compilado e instalado, o
`pkg_check_modules(HS libhs)` o encontra e o GTP UPF é habilitado
(`Found libhs, version 5.4.12`). Os demais "bloqueios" alegados não se
confirmaram — o VPP 2101 **core não usa hyperscan** e os paths de lib já eram
`aarch64-linux-gnu`.

**Novo `docker/Dockerfile.upf-vpp.ubuntu.arm64`** — diferenças vs. o x86:
1. Base `ubuntu:focal` (gcc-9, p/ C++17 do Vectorscan) + `cmake` recente via pip
   (focal tem 3.16; Vectorscan exige ≥3.18.4).
2. Compila o Vectorscan removendo `-Werror` (gcc-9 dá falso-positivo em
   `state_compress.c` + flag `-Wno-stringop-overread` gcc-11-only) e sem extras
   (`BUILD_UNIT/TOOLS/EXAMPLES/BENCHMARKS/DOC=OFF`).
3. `sed` tirando `dh-systemd` do `DEB_DEPENDS` do VPP (bionic-only; quebra o
   `make install-dep` no focal, só serve p/ `.deb`).
4. `sed` forçando `https://github.com` nos pacotes externos do VPP (o `rdma-core`
   baixava por `http://github.com:80` → "connection refused").
5. Copia o `libhs.so.5` do Vectorscan para a imagem final.

**Validação:** imagem `oaisoftwarealliance/oai-upf-vpp:v1.5.1` (~138 MB);
binário `vpp` ELF **ARM aarch64**; `upf_plugin.so` resolve
`libhs.so.5 => /lib/aarch64-linux-gnu/libhs.so.5`. **Runtime validado** (docker
`--privileged` + hugepages): VPP boota completo, `show plugins` lista
`upf_plugin.so 21.01.1`, `show upf specification release` → `PFCP version: 15`.
O abort no `flowtable_init` que aparecia antes **não era do porte**: era o
`main-heap` lastreado por hugepages sem páginas suficientes — com
`main-heap-page-size 4k` (ou hugepages dimensionadas) sobe normal.
`.tar` em `artifacts/oai-images/oai-upf-vpp.tar`.

**Validado no Graviton real (servidor AWS, 2026-06-22):** imagem carregada
(`docker load`, arch=arm64) e rodada standalone com o box ocioso. Teste
event-driven (readiness por estado, zero timeout) + métricas reais:
`docker stats` cpu 2,23% / mem 1,41 GiB; `show plugins` → `upf_plugin.so 21.01.1`;
`show upf specification release` → `PFCP version: 15`; `show memory main-heap` →
usado **1,08 G** (explica o heap de 2G: o flowtable pré-aloca ~1 GB); `upf_plugin.so`
liga em `libhs.so.5`. Container autoterminou.

**Lição (correção de processo):** uma 1ª tentativa rodou VPP **com o lab P2 ativo**
(load ~30) e um harness que **não autoterminava** — sufocou o `sshd` e o box
precisou de reboot. Regra adotada: teste de VPP no servidor só com o box **ocioso**,
container `--rm`+autotérmino, espera por **estado/evento** (nunca timeout cego).
Bible §4 também corrigida (RAM real ~3,8 GB / `t4g.medium`, não 906 MiB). Falta só
o E2E completo (PFCP do SMF + GTP-U do gNB + tráfego de UE), que exige core+RAN.

**Escopo:** o lab não depende desta imagem (P1 usa o UPF do Open5GS; P2 usa o
`oai-upf` simple_switch do core v2.2.1). O porte é pelo princípio Open RAN e é
candidato a report upstream para a OAI. Detalhes na bible §7.b.

---

## [0.26.1] — 2026-06-21

**Botão de logout no painel.** O endpoint `/api/logout` (que limpa a vaga de
Professor e o cookie) existia, mas **não tinha botão** — o professor não
conseguia sair, e a vaga única só liberava após `ADMIN_TAKEOVER_GRACE` (10 min).

- **Novo botão "⎋ Sair"** na barra do topo (`#logout-btn`), ao lado do "quem sou".
  Pede confirmação e, ao confirmar, chama `POST /api/logout` e volta para
  `/login`. Para Professor, o aviso explica que **libera a vaga** para outro
  entrar; para Aluno, é só "Sair do painel?".
- Resolve na prática a trava "um Professor por vez": agora dá para trocar de
  professor (ex.: do `hcarmine` para o `jonas`) na hora, sem esperar a carência.

**Gerenciamento dos Resultados salvos: excluir e anotar.** O modal de Resultados
só listava/abria/reproduzia — não dava para limpar nem identificar relatórios
antigos. Agora o Professor pode organizar o histórico (Aluno segue só leitura).

- **Excluir um:** botão **✕** em cada item da lista (com confirmação).
- **Excluir vários:** botão **☑ Selecionar** entra no modo seleção (checkboxes);
  **Tudo** marca/desmarca todos; **🗑 Excluir (N)** apaga os marcados de uma vez
  (novo endpoint `POST /api/results/delete` com lista de ids). Selecionar tudo +
  excluir = limpar o histórico inteiro.
- **Anotar observação:** botão **✎** em cada item abre um campo para uma nota
  livre (até 200 caracteres) — ex.: *"antes de corrigir o AMF"*. A nota aparece
  na lista (em itálico, sob o título) e no cabeçalho ao abrir o relatório.
  Persistida no JSON do resultado via `POST /api/results/{id}/note`.
- **Permissão:** todas as ações são **Professor-only** (backend responde 403 a
  Aluno); a UI esconde os botões para quem é Aluno.

---

## [0.25.5] — 2026-06-21

**Modo projeção operável.** O modo projeção (kiosk) escondia a régua lateral
inteira (`#sidebar`), deixando o professor sem os botões de ação durante a
projeção — para rodar um teste era preciso sair da projeção.

- **Correção:** o kiosk mantém o `#sidebar` (botões de ação) visível e restaura o
  grid de 2 colunas (`230px 1fr`). Continuam escondidos só os elementos que
  poluem o datashow: barra de projetos, painel de containers/telemetria pesada e
  os botões copiar/limpar do console. Console segue em fonte grande.

---

## [0.25.4] — 2026-06-21

**Bible consolida a sessão de relatórios didáticos.** A referência conceitual
([`core5g-arm64-bible.md`](core5g-arm64-bible.md)) passou a registrar o que foi
feito e aprendido nas versões 0.25.0–0.25.3, para não se perder:

- **§8.5 (novo):** relatórios com falso-negativo — nome de **container** vs nome
  de **serviço Compose** (`open5gs-amf-containerized` × `amf`), `ifconfig.me`
  devolvendo HTML em vez de IP, e veredito final sempre "ok". A lição: `bash -n`
  não pega bug semântico, relatório roda ao vivo antes do merge.
- **§8.6 (novo):** a Demo E2E media a **bridge Docker** em vez do túnel 5G
  (iperf saindo pela `eth0` porque o DN está na mesma rede do container do UE);
  corrigido com rota via `uesimtun0` + bind à origem (149 Mbit/s reais).
- **§9:** acrescentada a **verificação ao vivo de todos os relatórios** (P1 e P2)
  ao "estado atual confirmado".
- **§10 / §11:** item da auditoria no roadmap e link para o
  [guia de relatórios](docs/relatorios-didaticos.md) nas referências.

---

## [0.25.3] — 2026-06-21

**Guia de desenvolvedor do sistema de relatórios didáticos.** Documentação
minuciosa para um colaborador entender, manter e estender os testes/relatórios
do painel — consolidando o conhecimento das versões 0.25.0–0.25.2.

- **Novo:** [`docs/relatorios-didaticos.md`](docs/relatorios-didaticos.md) cobre:
  os dois tipos de relatório (testes do menu via `lib/testlog.sh` × Demo E2E via
  protocolo `STEP|`/`DONE|`/`PHASE|`); a API da lib (`section`/`ok`/`warn`/`err`/
  `summary`); o padrão didático ("Por quê" + veredito honesto); o passo a passo
  para **adicionar um relatório** (script → `COMMANDS` → botão); os **gotchas**
  reais (nome de container ≠ serviço compose, `exit 0` em pré-condição, rodar ao
  vivo porque `bash -n` não pega bug semântico); como **verificar ao vivo**
  (rsync de um script, subir/baixar lab, tirar ANSI); e o **inventário** de todos
  os relatórios P1 e P2 com o que cada um prova.
- **Integração:** linkado no [README](README.md) §4 (mapa do repositório) e no
  [CONTRIBUTING](CONTRIBUTING.md) §4 (validação antes do PR).

---

## [0.25.2] — 2026-06-21

**Verificação ao vivo de todos os relatórios P1 (com o Projeto 1 no ar).**
Rodar cada relatório de verdade — não só `bash -n` — expôs 3 bugs de precisão
que enganariam o professor/aluno. Todos corrigidos e re-testados ao vivo:

- **`test_ue_connection` — IP público falso:** o teste de HTTP usava
  `wget http://ifconfig.me`, que devolve **HTML** (não o IP), então o relatório
  exibia `IP público <!DOCTYPE html>`. Corrigido: usa `http://ifconfig.me/ip`
  (texto puro) e **extrai/valida o IP** por regex antes de rotular.
- **`test_ng_setup` — falso "AMF não está rodando":** o script procurava um
  container chamado `amf`, mas o nome real é `open5gs-amf-containerized` (o
  `amf` é só o nome do **serviço** compose). Com o `docker inspect` falhando, o
  cruzamento com o AMF caía em aviso e o veredito virava *"N2 não confirmada"* —
  **mesmo com o NGSetupResponse recebido**. Corrigido o nome do container; agora
  o veredito é *"N2 estabelecida — NG Setup com sucesso"*.
- **`test_registration` — mesmo bug de nome:** dava *"! Container amf não está
  rodando"* no cruzamento NAS. Corrigido; agora confirma *"AMF registrou a
  sinalização NAS do UE"*.

> Verificados ao vivo e aprovados: `status/system-status`, `ng-setup`,
> `registration`, `config-coherence`, `ue-connection` e `upf-failover` (failover
> mantendo conectividade). Todos com cabeçalho de seção, checagens coloridas e
> bloco "Resumo". Relatórios do **P2** (E2 SM/KPM/RC) seguem auditados (lib +
> Resumo) — validação ao vivo deles exige alternar para o Projeto 2.

---

## [0.25.1] — 2026-06-21

**Auditoria de indicadores didáticos em todos os relatórios.** Varredura de
todos os testes acionáveis pelo painel (P1 e P2) para garantir saída didática
consistente: cabeçalho de seção, checagens coloridas (✓/!/✗) e bloco **"Resumo"**
(*O que fez* / *Resultado*) padronizado pela `lib/testlog.sh`.

- **Resultado da auditoria:** a suíte já estava majoritariamente padronizada —
  todos os testes do menu P1 (`status`, `system-status`, `ng-setup`,
  `registration`, `config-coherence`, `upf-failover`) e P2 (`e2-sm`, `e2-kpm`,
  `e2-rc`), além de `throughput` e `channel`, usam a lib + Resumo.
- **Único fora do padrão — `test_ue_connection.sh`:** usava `echo "❌"` cru e
  saía com `exit 1` sem Resumo nos caminhos de erro, e o veredito final dizia
  sempre "ok". Reescrito: usa a lib no corpo inteiro (cor consistente), guardas
  de pré-condição com **Resumo + `exit 0`**, contadores de falha/atenção e
  **veredito honesto** (✗ crítico / ! ressalva / ✓ tudo passou). Cada um dos 6
  blocos ganhou a linha *"Por quê"* explicando o que prova.
- **`test_distance.sh` / `test_interference.sh`:** confirmados como utilitários
  de CLI legados, **não acionáveis pelo painel** (o painel usa `test_channel.sh`,
  que já é didático) — fora do escopo de relatório.

---

## [0.25.0] — 2026-06-21

**Demonstração E2E didática + medição de banda corrigida.** O modal da
Demonstração E2E (Projeto 1) tinha o console praticamente vazio — o aluno via o
resumo (passos ✓) mas *"não via nada"* do que foi feito. E o passo de throughput
contra o DN não retornava banda.

- **Logs didáticos:** o script agora envia ao console, em cada passo, o
  **comando exato** executado (`$ docker exec …`, destaque azul) seguido da
  **saída real** (ping, `ip addr`, `ifconfig.me`, iperf3) e uma linha *"Por quê"*
  explicando o que aquilo prova. O aluno acompanha a operação fim-a-fim na ordem
  real: RAN no ar → sessão PDU/IP → ping pela internet → IP público → banda.
- **Fix do throughput (iperf3):** o DN (`10.50.0.100`) fica na **mesma rede
  docker** do container do UE, então o iperf "solto" saía pela **bridge `eth0` e
  não pelo túnel 5G** — não media o núcleo e ainda falhava por timing. Agora o
  script cria uma **rota temporária para o DN via `uesimtun0`** e **amarra a
  origem ao IP do túnel** (`-B <IP do UE>`), forçando o caminho real
  UE → gNB → UPF (NAT na N6) → DN; a rota é removida ao final (sem rastro).
- **Diagnóstico honesto:** se o iperf ainda não retornar banda, a saída completa
  do comando vai pro console para diagnóstico, e o resumo deixa claro que a
  egressão para a internet (Passos 3-4) já comprova a operação fim-a-fim.

> Pendente de validação ao vivo: o fix do iperf foi escrito offline (servidor
> desligado). Rodar a Demonstração E2E com o Projeto 1 no ar confirma a banda.

---

## [0.24.8] — 2026-06-21

**Reassunção automática da vaga de Professor.** Depois de um `deploy` (que
reinicia o painel e zera o estado em memória) ou de um abandono, a aba do
professor ficava "órfã" e mostrava *"sua sessão não está mais ativa"* — e só
recarregar não resolvia (a sessão antiga não reassumia).

- **Backend:** o `/api/heartbeat` agora **reassume a vaga automaticamente quando
  ela está LIVRE** — a aba do professor recupera no próximo heartbeat (≤5s), sem
  relogar. Não rouba de um professor ativo (só pega o que já está livre), então a
  trava de "um por vez" continua valendo.
- **Frontend:** o aviso **se auto-limpa** quando a vaga é reassumida; e passou a
  diferenciar *"⏳ Reassumindo o controle…"* (vaga livre) de *"outro professor
  está com o controle"* (vaga realmente tomada).

---

## [0.24.7] — 2026-06-21

**Créditos + apoio ao projeto.**

- Créditos atualizados: o projeto é **coordenado pelo Prof. Dr. Jonas Augusto
  Kunzler** e **mantido por Henrique Carmine** — no README (Equipe) e nos rodapés
  do painel e do login.
- Nova seção **"Apoie este projeto"** no README: o lab roda 24/7 num servidor ARM
  custeado do bolso; PIX para quem quiser ajudar com o custo de manter no ar.
- `.github/FUNDING.yml` aponta o botão **Sponsor** do GitHub para a seção de apoio.

---

## [0.24.6] — 2026-06-21

**Ajuste do RAN ao vivo (achado do ensaio de pré-flight).** No ensaio com o
Projeto 2 real: o E2 conecta e os xApps rodam ("Connected E2 nodes = 1", "Test
xApp run SUCCESSFULLY"), mas o **UE não anexa** (bug conhecido AUSF↔UDM HTTP/2 do
P2, no roadmap) — logo o gNB não emite SNR e a faixa RAN ao vivo não tem dados.

- A faixa **só aparece quando há SNR real** (`d.up && d.snr != null`); antes
  poderia mostrar um card vazio com "—" durante o demo. Agora fica oculta até
  haver medição PHY de um UE conectado.
- Suíte de features validada **7×** (trava de admin, identidade por e-mail,
  espelho ao vivo, Resultados+Replay, viewers/roster, telemetria) — todas
  passaram. Mobile (espelho do aluno no celular) validado.

---

## [0.24.5] — 2026-06-20

**Responsividade mobile (alunos no celular).** Numa turma, os alunos entram pelo
telefone — e o painel renderizava a 980px (sem `<meta viewport>`), forçando zoom.

- Adicionado `<meta name="viewport" content="width=device-width, initial-scale=1">`
  ao painel (o login já tinha) — agora o CSS responsivo realmente aplica no celular.
- Bloco `@media (max-width:720px)`: top bar e banner **AO VIVO** quebram linha,
  cards de projeto empilham, RAN ao vivo vira 2 colunas, console com fonte
  legível, rodapé centralizado. O botão de projeção some no celular (é de operador).
- Validado headless a 390px: viewport correto, banner ao vivo e sparklines OK.

---

## [0.24.4] — 2026-06-20

**Crédito do autor + equipe final.** Contato do mantenedor passou a ser
[henriquecarmine@gmail.com](mailto:henriquecarmine@gmail.com) (README e
CONTRIBUTING), com um breve perfil — Perito Forense Digital (Governança de TI e
Telecomunicações), mestrando em Open RAN sob orientação do Prof. Jonas Kunzler.
Equipe final confirmada: **Prof. Dr. Jonas Augusto Kunzler · Henrique Carmine ·
Klinger · Kelvin** (Gilberto não participou do projeto).

---

## [0.24.3] — 2026-06-20

**Nome do professor confirmado nos documentos.** Conferindo os PDFs das aulas em
`pdfs/`, o orientador é **Prof. Dr. Jonas Augusto Kunzler** (jak@cesar.school) —
atualizado na Equipe (README) e nos rodapés do painel. Os nomes dos alunos nos
documentos constam só com o primeiro nome (planilha de composição, grupo UE-TP:
Henrique · Klinger · Kelvin · Gilberto).

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
