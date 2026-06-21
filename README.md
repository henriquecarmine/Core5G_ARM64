# Core5G ARM64

Laboratório 5G completo rodando em **AWS Graviton (ARM64)**, com painel web de
controle próprio. Reúne **dois projetos** independentes da disciplina
*RAN Intelligent Controller (RIC)* — CESAR School (tema **UE-TP-rApp**):

| Projeto | Stack | Pasta | Status |
|---|---|---|---|
| **Projeto 1** | Open5GS (5GC) + UERANSIM (gNB/UE simulados) | `server/` | ✅ Apresentado 13/06/2026, validado fim a fim |
| **Projeto 2** | OAI 5GC + gNB RFSIM + agente E2 + **FlexRIC** (near-RT RIC) + xApps | `server/oai-cn-gnb-e2/` | ✅ Funcional — apresentação **20/06/2026** |

> **Quer só entender o quê/porquê de tudo?** Leia a
> [**Bíblia do projeto**](core5g-arm64-bible.md) (referência conceitual completa,
> do leigo ao engenheiro O-RAN). Para o histórico cronológico, o
> [**CHANGELOG**](CHANGELOG.md). Para os roteiros de laboratório, [`docs/labs/`](docs/labs/).
>
> Este README é a **porta de entrada**: como reproduzir o estado atual, o que
> falta e como colaborar.

---

## 1. Como chegar até aqui (reprodução do zero)

O fluxo é **tudo local, deploy via `deploy.sh`**. Você nunca edita arquivos
direto no servidor — edita em `server/` na sua máquina e o `deploy.sh` reflete
no servidor por SSH/rsync.

### 1.1 Pré-requisitos

- **Conta AWS** com uma instância EC2 **ARM (Graviton)** Ubuntu 22.04+.
  Recomendado **`t4g.medium`** (2 vCPU, 4 GB) — o `t4g.micro` roda só o Projeto 1.
  Volume EBS de **30 GB**.
- Sua máquina local com `bash`, `git`, `rsync`, `ssh` e `openssl`.
- Para **construir** as imagens OAI arm64: um **Mac Apple Silicon** (ou outra
  máquina arm64) com Docker. As imagens prontas **não ficam no git** (~362 MB) —
  são distribuídas pelo Google Drive do grupo.

### 1.2 Clonar e configurar

```bash
git clone https://github.com/henriquecarmine/Core5G_ARM64.git
cd Core5G_ARM64
cp .env.example .env
```

Edite o `.env` (nunca commite — está no `.gitignore`):

```ini
AWS_SERVER_HOST=core5g-arm64.duckdns.org   # domínio DuckDNS ou IP da instância
AWS_SERVER_USER=ubuntu
AWS_SSH_KEY_PATH=ssl/core5g_openran_arm64.pem   # sua chave SSH (.pem), NUNCA commitar

DUCKDNS_DOMAIN=core5g-arm64                 # opcional: IP dinâmico automático
DUCKDNS_TOKEN=<seu-token>

PANEL_USER=professor                        # Professor (admin) — acesso total
PANEL_PASSWORD=<senha-forte>
PANEL_GUEST_USER=guest                      # habilita o acesso de Aluno (só-leitura)
PANEL_GUEST_PASSWORD=<senha-guest>          # opcional (alunos entram só com nome+e-mail)
PANEL_EXTRA_USERS=professor2:senha2         # admins extras: user:senha,user2:senha2
```

> **Papéis (modo sala de aula):** *Professor* opera (só **um por vez**); *Aluno*
> acompanha ao vivo, entra com **nome + e-mail** (sem senha). Detalhes em §1.6.

### 1.3 Provisionar o servidor (uma vez)

```bash
./deploy.sh bootstrap     # Docker + swap 8 GB + DuckDNS + Caddy (HTTPS) + painel
```

Idempotente — pode rodar quantas vezes quiser. Ao final, o painel já responde em
`https://<seu-host>/` com TLS válido (Let's Encrypt via Caddy) e tela de login.

### 1.4 Projeto 1 — Open5GS + UERANSIM

```bash
./deploy.sh up all        # sobe o Core 5G (Open5GS) + RAN (UERANSIM)
./deploy.sh status        # docker ps + healthcheck (N2/N3/N4/N6)
```

Validação fim a fim: o UE registra (5G-AKA), abre PDU Session e ganha
conectividade real (`ping -I uesimtun0 8.8.8.8` → 0% perda). Tudo isso também
está exposto em botões no painel (UE Lab, Demonstração E2E).

### 1.5 Projeto 2 — OAI + FlexRIC (E2)

As imagens OAI arm64 precisam estar carregadas no Docker do servidor:

```bash
# (no Mac arm64) construir e exportar as 6 imagens — ver bible §7.b:
cd server/oai-cn-gnb-e2 && ./build-oai-arm64.sh        # AMF→SMF→NRF→UDR→UDM→AUSF
# exporta /tmp/oai-images/oai-*.tar (~60 MB cada). Sobe pro Drive do grupo.

# enviar o diretório do Projeto 2 (uma vez, ~230 MB):
./deploy.sh sync-oai

# no servidor: docker load -i ~/oai-<comp>.tar  (cada componente do Drive)
```

Com as imagens carregadas, o lab E2 sobe **pelo painel** (seletor de projeto →
*Projeto 2*) ou via SSH:

```bash
./deploy.sh ssh
cd ~/server/oai-cn-gnb-e2
./scripts/up_e2_lab.sh           # Core OAI + nearRT-RIC + gNB(E2) + nrUE
./scripts/test_e2_sm.sh all      # exercita os 8 Service Models via xApps
```

> **Por que `t4g.medium`?** O gNB/nrUE RFSIM são CPU-intensivos. Em 2 vCPUs eles
> podem saturar e **congelar a instância**. O guardrail é via **cgroup v2 cpuset**:
> o `bootstrap` cria a slice `oai-lab.slice` fixada **fora da CPU 0** (`AllowedCPUs=1`),
> reservando um núcleo para o sistema (SSH/Docker/painel/Caddy com `CPUWeight` máximo).
> Assim o lab nunca derruba o box — painel ~600 ms e SSH ~2,5 s mesmo com gNB+nrUE no
> talo. (Neste kernel ARM o `CPUQuota`/CFS não é aplicado; por isso usamos cpuset.)
> Detalhe em [`infra/server-bootstrap.sh`](infra/server-bootstrap.sh).

### 1.6 Painel web — modo sala de aula

`https://<seu-host>/` — o painel é uma SPA (FastAPI + HTML/CSS/JS, sem build).
Recursos base: telemetria ao vivo, logs filtrados/coloridos (ANSI/ISO) com
**explicação didática** no fim, UE Lab, Demonstração E2E, **seletor de projeto**
(liga um e desliga o outro), **topologia interativa** (containers/portas/redes
reais, clicáveis) e os testes de Service Model E2 — cada um com **resumo final**
do que fez e o resultado.

Sobre isso, um **modo sala de aula** pensado para apresentar a um auditório:

- **Papéis Professor / Aluno.** O *Professor* (admin) opera; o *Aluno* (guest)
  acompanha em modo só-leitura. Aluno entra com **nome + e-mail** (1 clique, sem
  senha) — o e-mail é o **registro de presença** da turma.
- **Um Professor por vez.** A vaga é "pegajosa": um 2º admin diferente é bloqueado
  até o atual sair (logout) ou abandonar por 10 min. Protege a aula de alguém
  assumir o controle no meio.
- **Espelho AO VIVO.** Tudo que o Professor executa é transmitido em tempo real
  para os Alunos (console + qual tela ele abriu), via um *ring-buffer* + *polling* —
  escala para a turma inteira (N alunos custam ~o mesmo que 1) sem derrubar o box.
- **Resultados + Replay.** Cada execução é salva em disco (sobrevive a restart) e
  pode ser **reproduzida** depois, linha a linha — o professor reapresenta uma
  coleta sem subir nada. Aba "Resultados salvos" (Professor e Aluno).
- **RAN ao vivo (P2).** Faixa de *sparklines* com SNR/MCS/PRB/BLER reais do gNB
  OAI, atualizando ao vivo durante o E2SM-KPM.
- **Modo projeção (kiosk).** Botão "⛶ Projeção" → tela limpa em fullscreen pro
  datashow (RAN grande + console grande, sem controles).
- **Quem está assistindo.** O Professor clica no badge "👁 N alunos" e vê os
  conectados agora (nome + e-mail) e a presença acumulada. Dados pessoais ficam
  **só no servidor** — nunca no git.

> **Acesse sempre pelo domínio**, nunca pelo IP — o certificado é do domínio.
> Se o IP mudou e o navegador não abre, limpe o cache DNS local
> (macOS: `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`).

---

## 2. O que ainda falta (roadmap)

| Quando | Item | Estado |
|---|---|---|
| **20/06/2026** | Apresentar Projeto 2 (Aula 06, 08:00–11:00, 20 min) | 🎯 Pronto para apresentar |
| Curto prazo | xApp **UE-TP-rApp** (previsão de throughput por UE: RSSI/RSRP/CQI/PRB) — o tema sorteado do grupo | ⏳ Esqueleto em `xapp_ue_tp_moni.c`; falta o modelo de previsão |
| Curto prazo | Registro UE no Projeto 2 bloqueado por bug **AUSF↔UDM HTTP/2** (timeout de 1s hardcoded no AMF). E2/RIC/xApps funcionam; só o anexo NAS do UE falha | 🔧 Documentado; exige recompilar o AMF |
| Médio prazo | Sensor de protocolo E2/NGAP/GTP-U no painel (blueprint de observabilidade) | 📋 Planejado |
| Médio prazo | Persistir os symlinks do FlexRIC (`/usr/local/lib/flexric`) no `bootstrap` — hoje se perdem ao trocar de instância | 📋 Planejado |
| Quando der | Reportar os bugs do §8 da bible ao repositório OAI de origem | 📋 Planejado |

A lista canônica e detalhada vive na [bible §10](core5g-arm64-bible.md#10-pendências--próximos-passos).

---

## 3. Como colaborar

Contribuições do grupo (e de quem mais quiser estudar o lab) são bem-vindas. O
guia completo, passo a passo (inclusive pra quem nunca colaborou no GitHub), está
em **[`CONTRIBUTING.md`](CONTRIBUTING.md)**. Em resumo, há três espaços:

- **[Issues](../../issues)** — relatar bug, propor ideia ou tirar dúvida.
- **[Discussions](../../discussions)** — conversar / perguntar "como funciona X".
- **Pull Request** — *fork* → branch → PR descrevendo *o que mudou e por quê*.

Regras de ouro: edite **sempre local** (o `deploy.sh` é o único caminho até o
servidor); **segredos nunca entram no git** (`.env`, `ssl/*.pem`); **dados de
aluno** (e-mail/roster) ficam só no servidor. Versionamento e como validar antes
do PR: ver [`CONTRIBUTING.md`](CONTRIBUTING.md) §4 e §6.

**Acesso de colaborador, ou as imagens OAI arm64 do Drive?** Fale comigo:

- **Henrique Carmine** — [henriquecarmine@gmail.com](mailto:henriquecarmine@gmail.com) ·
  [@henriquecarmine](https://github.com/henriquecarmine)

---

## 4. Mapa do repositório

```
.
├── README.md                  ← você está aqui (porta de entrada)
├── LICENSE                     ← licença MIT
├── CONTRIBUTING.md            ← como colaborar (Issues/Discussions/PR, testes, versão)
├── core5g-arm64-bible.md      ← referência conceitual completa
├── CHANGELOG.md               ← diário de bordo cronológico
├── deploy.sh                  ← entrypoint único de deploy (local → servidor)
├── .env.example               ← modelo de configuração (copie para .env)
├── .github/                   ← modelos de Issue e de Pull Request
├── docs/                      ← blueprint do painel + roteiros de laboratório
├── infra/                     ← bootstrap do servidor + unit systemd do painel
└── server/                    ← tudo que roda no servidor
    ├── panel/                 ← painel web (FastAPI) + estáticos
    ├── ueransim/              ← RAN simulada (Projeto 1)
    ├── scripts/               ← demo E2E, troca de projeto, etc.
    └── oai-cn-gnb-e2/         ← Projeto 2 (OAI + FlexRIC + xApps)
```

---

## 5. Equipe

- **Professor (orientador):** Prof. Dr. Jonas Augusto Kunzler — [jak@cesar.school](mailto:jak@cesar.school)
- **Autor / mantenedor:** Henrique Carmine — Perito Forense Digital (Governança de TI e Telecomunicações), mestrando em Open RAN sob orientação do Prof. Jonas Kunzler — [henriquecarmine@gmail.com](mailto:henriquecarmine@gmail.com) · [@henriquecarmine](https://github.com/henriquecarmine)
- **Colaboradores:** Klinger · Kelvin

CESAR School · disciplina *RAN Intelligent Controller (RIC)* · tema **UE-TP-rApp**.

Licença **[MIT](LICENSE)**.
