# core5g-panel — painel web do laboratório

Painel **FastAPI + HTML/CSS/JS puro** (sem framework de front, sem
Prometheus/Grafana) que controla e observa o lab 5G. Roda no servidor como
serviço systemd (`core5g-panel`, porta local 8765) atrás do **Caddy** (HTTPS,
cookie de sessão). Deploy: `./deploy.sh panel` (rsync + bootstrap).

## Arquitetura

| Peça | Arquivo | O quê |
|---|---|---|
| Backend | [`server.py`](server.py) | Auth (Professor único + Alunos ao vivo), execução de scripts com **streaming** linha a linha, telemetria leve (/proc + docker stats), topologia com status vivo, resultados salvos. HTML servido com `Cache-Control: no-cache` (deploy chega na hora) |
| Painel | [`static/index.html`](static/index.html) | Console com **colorimetria ISO/ANSI**, cards de projeto (P1/P2 mutuamente exclusivos), UE Lab, demo E2E, modo projeção, resultados |
| Topologia | [`static/topology.html`](static/topology.html) | Diagrama SVG **orientado a dados** (JSONs abaixo): bandas CUPS, 4 modos, tour guiado, offset de links paralelos |
| Dados da topologia | [`static/openran-topology.json`](static/openran-topology.json) (P2) · [`static/openran-topology-p1.json`](static/openran-topology-p1.json) (P1) | Nós (x,y, textos didáticos, `statusKey`), links (iface), camadas (`band:true` = banda CUPS). Ver `_como_atualizar` dentro de cada JSON |
| Login | [`static/login.html`](static/login.html) | Professor (credenciais do `.env`) ou Aluno (nome+e-mail = presença) |
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

## Estado atual (v0.33.x — 2026-07-03)

Checklist do artigo (Prof. Jonas): pontos 2–7 + temas ✅ · **i18n pt/es/en
pendente** (strings hardcoded em pt nos 3 HTML + textos didáticos nos JSONs).
Roadmap completo: README raiz §2 e bible §10.
