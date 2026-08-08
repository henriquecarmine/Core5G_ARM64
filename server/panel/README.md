# core5g-panel — painel web do laboratório

Painel **FastAPI + HTML/CSS/JS puro** (sem framework de front, sem
Prometheus/Grafana) que controla e observa o lab 5G. Roda no servidor como
serviço systemd (`core5g-panel`, porta local 8765) atrás do **Caddy** (HTTPS,
cookie de sessão). Deploy: `./deploy.sh panel` (rsync + bootstrap).

## Arquitetura — duas camadas

Desde a v0.50.0 o backend é modular
([plano](../../docs/plano-duas-camadas-painel.md)): **operacional** (infra 5G)
e **didática** (aulas) separadas, com o `core` transversal. A didática consome
APIs da operacional; a operacional nunca conhece a didática. O entrypoint segue
`uvicorn server:app`.

| Peça | Arquivo | O quê |
|---|---|---|
| Bootstrap | [`server.py`](server.py) | `app` + middleware de sessão, login/logout, sala de aula ao vivo (vaga única de Professor, espectadores, presença/roster, navegação espelhada) |
| Infra compartilhada | [`core.py`](core.py) | Sessão por cookie HMAC, `LiveBuffer`, resultados persistidos, streaming de comandos, i18n do servidor — **sem rotas** |
| Camada operacional | [`ops.py`](ops.py) | Serviços/containers P1·P2, telemetria (/proc + docker stats), topologia com status vivo, logs, assinantes, testes, `COMMANDS`. HTML com `Cache-Control: no-cache` (deploy chega na hora) |
| Camada didática | [`lab.py`](lab.py) | Páginas `/lab/*` (aulas de ML + projeto final) e dúvidas aluno→professor |
| Painel | [`static/ops/index.html`](static/ops/index.html) | Console com **colorimetria ISO/ANSI**, cards de projeto (P1/P2 mutuamente exclusivos), UE Lab, demo E2E, modo projeção, resultados |
| Percurso dos dados | [`static/ops/flow-strip.js`](static/ops/flow-strip.js) | **FlowStrip**: faixa animada sobre o console/modal com o caminho dos dados do teste em execução (nós, interfaces, 💾 armazenamento, ✔/✖). Cenas por comando + gatilhos regex sobre o stream; espelha ao vivo para os alunos |
| Topologia | [`static/ops/topology.html`](static/ops/topology.html) | Diagrama SVG **orientado a dados** (JSONs abaixo): bandas CUPS, 4 modos, tour guiado, offset de links paralelos |
| Dados da topologia | [`static/ops/openran-topology.json`](static/ops/openran-topology.json) (P2) · [`static/ops/openran-topology-p1.json`](static/ops/openran-topology-p1.json) (P1) | Nós (x,y, textos didáticos, `statusKey`), links (iface), camadas (`band:true` = banda CUPS). Ver `_como_atualizar` dentro de cada JSON |
| Aulas do lab | [`static/lab/`](static/lab/) | `lab-*.html` (geradas por `pdfs/02-ric-ai/lab-didatico/`) + `lab-i18n.js`, `lab-models.js`, `lab-stepper.js` |
| Login | [`static/login.html`](static/login.html) | Professor (credenciais do `.env`) ou Aluno (nome+e-mail = presença) — compartilhado pelas duas camadas |
| i18n | [`static/i18n.js`](static/i18n.js) | Dicionários **pt/en/es/fr** + helper (`I18N.t`, `data-i18n`, fallback lang→en→pt, seletor 🌐, `localStorage c5g-lang`). F1 = login+topbar; toda chave nova entra nos 4 idiomas (`npm run test:i18n`) |
| Testes | [`test/`](test/) | `npm test` (loaders) · `npm run test:topo` (geometria dos JSONs + render headless com temas). Ver [test/README.md](test/README.md) |
| Vendor | [`vendor/`](vendor/) | Wheels aarch64 do scikit-learn p/ o lab de RIC com IA (fora do git — [vendor/README.md](vendor/README.md)) |

## Convenções que NÃO podem quebrar

1. **Consoles/terminais são escuros nos DOIS temas** (claro/escuro) e usam a
   paleta fixa `TERM` — **nunca variáveis de tema** dentro de conteúdo de
   terminal (no claro elas viram cor escura sobre fundo preto; bug v0.32.2).
2. **Tema**: `data-theme` no `<html>`, persistido em `localStorage`
   (`c5g-theme`), aplicado por script inline no `<head>` antes do paint.
3. **Colorimetria ISO nos logs**: scripts bash usam `server/scripts/lib/testlog.sh`
   (sempre emite ANSI); o front converte (`renderLogLine`) e coloriza por token
   o que vier sem ANSI. Partida de serviço ganha **anotação didática azul**
   (`SERVICE_ROLES` — descreve o papel de cada NF/container).
4. **Topologia**: após mudar `x,y`/links nos JSONs, rode
   `python3 test/check-topology.py` — nenhum link pode atravessar card de
   terceiro (era o bug "RIC→UPF" apontado pelo professor).
5. **Versionamento**: cada release ajusta [`VERSION`](VERSION) + linha no
   [CHANGELOG](../../CHANGELOG.md) (tabela, mais novo primeiro no bloco final).

## Estado atual (v0.34.x — 2026-07-03)

Checklist do artigo (Prof. Jonas): pontos 2–7 + temas ✅ · **i18n F1 pronta**
(infra + seletor 🌐 + login/topbar em pt/en/es/fr) · faltam F2 (index inteiro),
F3 (topologia) e F4 (scripts via `LAB_LANG`). Roadmap: README raiz §2 e bible §10.
