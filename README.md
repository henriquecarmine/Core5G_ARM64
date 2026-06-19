# Core5G ARM64

Laboratório 5G completo rodando em **AWS Graviton (ARM64)**, com painel web de
controle próprio. Reúne **dois projetos** independentes da disciplina
*RAN Intelligent Controller (RIC)* — CESAR School, Grupo 6 (tema **UE-TP-rApp**):

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

PANEL_USER=<seu-admin>                      # login do painel (acesso total)
PANEL_PASSWORD=<senha-forte>
PANEL_GUEST_USER=guest                      # login só-leitura (demonstração)
PANEL_GUEST_PASSWORD=<senha-guest>
PANEL_EXTRA_USERS=grupo6:grupo6             # admins extras: user:senha,user2:senha2
```

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
> podem saturar e **congelar a instância**. Os processos nativos rodam dentro de
> *scopes* do systemd com teto rígido de CPU (`CPUQuota` 120%/60% + `CPUWeight`
> + `nice`), o que **reserva CPU para o sistema e impede o freeze** sem quebrar o
> E2. Detalhe em [`up_gnb_oai.sh`](server/oai-cn-gnb-e2/scripts/up_gnb_oai.sh).

### 1.6 Painel web

`https://<seu-host>/` — login (admin tem acesso total; guest é só-leitura).
Recursos: telemetria ao vivo, logs filtrados/coloridos, UE Lab, Demonstração
E2E, **seletor de projeto** (liga um e desliga o outro), **topologia interativa**
(containers/portas/redes reais, clicáveis) e os testes de Service Model E2 com
explicação didática de cada resultado. **Todos os testes** saem com colorimetria
consistente (ANSI/ISO) e um **resumo final** explicando o que o teste fez e o
resultado.

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

Contribuições do grupo (e de quem mais quiser estudar o lab) são bem-vindas.

1. **Fork / branch** a partir de `main`. Nunca trabalhe direto na `main` remota.
2. **Edite sempre local**, em `server/` — o `deploy.sh` é o único caminho até o
   servidor. Não edite arquivos no servidor por SSH (some no próximo deploy).
3. **Segredos nunca entram no git**: `.env` e a chave SSH (`ssl/*.pem`) estão no
   `.gitignore` — mantenha assim. Novos segredos vão em variáveis do `.env`.
4. **Documente o que mudou**: toda mudança visível entra no
   [`CHANGELOG.md`](CHANGELOG.md) e, se for conceitual, na
   [bible](core5g-arm64-bible.md). Versão em `server/panel/VERSION`
   (`MAJOR.MINOR.PATCH`).
5. **Teste antes de abrir PR**: `./deploy.sh status` (Projeto 1) e
   `./scripts/test_e2_sm.sh all` (Projeto 2) devem passar.
6. Abra o PR descrevendo **o que mudou e por quê** (mesmo espírito do CHANGELOG).

**Dúvidas, acesso ao lab ou às imagens OAI do Drive?** Fale comigo:

- **Henrique Carmine** — [hc@cesar.school](mailto:hc@cesar.school) ·
  [@henriquecarmine](https://github.com/henriquecarmine)

---

## 4. Mapa do repositório

```
.
├── README.md                  ← você está aqui
├── core5g-arm64-bible.md      ← referência conceitual completa
├── CHANGELOG.md               ← diário de bordo cronológico
├── deploy.sh                  ← entrypoint único de deploy (local → servidor)
├── .env.example               ← modelo de configuração (copie para .env)
├── docs/                      ← blueprint do painel + roteiros de laboratório
├── infra/                     ← bootstrap do servidor + unit systemd do painel
└── server/                    ← tudo que roda no servidor
    ├── panel/                 ← painel web (FastAPI) + estáticos
    ├── ueransim/              ← RAN simulada (Projeto 1)
    ├── scripts/               ← demo E2E, troca de projeto, etc.
    └── oai-cn-gnb-e2/         ← Projeto 2 (OAI + FlexRIC + xApps)
```

Projeto mantido por [@henriquecarmine](https://github.com/henriquecarmine) ·
CESAR School · Grupo 6 — UE-TP-rApp.
