# Plano — Painel em duas camadas: operacional × didática

> Decisão de arquitetura (08/08/2026). Complementa o
> [blueprint de observabilidade](blueprint-painel-observabilidade.md) (visão de
> logs/métricas, "nada implementado ainda") e o
> [plano de redesign](plano-painel-redesign.md) (navegação por projeto, 06/2026).

## 1. O problema

O painel hoje é **um monolito que mistura duas naturezas**:

| | Camada operacional | Camada didática |
|---|---|---|
| O que é | serviços/containers P1·P2, telemetria, topologia, testes, deploy | aulas `/lab/*`, questões, roster/results (aluno × professor), projeto final |
| Rotas | `/api/services`, `/api/telemetry`, `/api/topology*`, `/api/demo-e2e`… | `/lab/*`, `/api/lab/*`, `/api/roster`, `/api/results*` |
| Cadência de mudança | estável (infra) | alta — muda a cada disciplina/aula |
| Público | operador do lab | alunos e professor |
| Risco de acoplar | mexer em aula derruba operação | operação engessa a evolução das aulas |

Evidência do acoplamento: `server.py` com ~1.500 linhas e `index.html` com
~2.600, servindo ambos os mundos. Com **3 disciplinas** já arquivadas em
`pdfs/` (e a 4ª por vir), cada aula nova vira página hardcoded dentro do
painel de operação. Não escala.

## 2. A decisão

Separar em duas camadas com fronteira explícita, **por fases, sem rewrite**:

```
┌──────────────────────────────────────────────────────┐
│  CAMADA OPERACIONAL (/, /ops)                        │
│  serviços · telemetria · topologia · LOGS · testes   │
│  fonte: docker/scripts do servidor                   │
├──────────────────────────────────────────────────────┤
│  CAMADA DIDÁTICA (/lab)                              │
│  hub por disciplina · aulas · questões · roster ·    │
│  results · projeto — consome a operacional via API,  │
│  nunca o contrário                                   │
└──────────────────────────────────────────────────────┘
```

Regra de dependência: a didática **pode** chamar APIs da operacional (ex.: aula
que mostra KPM ao vivo); a operacional **nunca** conhece a didática.

## 3. Fases

### Fase A — separar sem mudar comportamento ✅ (v0.50.0, 08/08/2026)

- `server.py` → `core.py` (infra compartilhada, sem rotas) + `ops.py` e
  `lab.py` (APIRouters); `server.py` vira bootstrap/auth/sala de aula.
  **Nenhuma rota mudou.**
- `static/` → `static/ops/` (index, topologia, JSONs) e `static/lab/`
  (aulas + js do lab); `login.html` e `i18n.js` seguem compartilhados na
  raiz. Geradores (`lab-didatico/`) e testes atualizados para os novos
  caminhos.
- Critério cumprido: **diff de rotas vazio** (50 = 50, verificado por
  introspecção do app) + smoke de 28 endpoints autenticados OK +
  `check-topology.py` OK.

### Fase B — a lacuna operacional: logs

O item que falta na camada operacional (e motivou o blueprint): **ver o que
cada NF está dizendo**, não só se está de pé.

- **Nível 0 (proporcional ao t4g):** endpoint `GET /api/logs/<container>?tail&grep`
  via `docker logs`, com UI de filtro por container **e por rede docker
  (`net-n2/n3/n4/n6/sbi`) = interface 3GPP** — a vantagem pedagógica já mapeada
  no blueprint, sem Loki/Grafana.
- Loki/Grafana/Prometheus (Nível 1 do blueprint) só se sobrar recurso — reavaliar
  contra a [política de custos](POLITICA-DE-CUSTOS.md) depois da Fase A.
- ✅ **MVP do "modo fluxo" entregue (v0.51.0)**: `static/ops/flow-strip.js` —
  faixa animada do percurso dos dados (nós · interfaces · 💾 · ✔/✖) sobre o
  console e o modal, cenas por comando, gatilhos regex no stream existente,
  espelhada ao vivo aos alunos. V2: eventos estruturados `FLOW|/STORE|/RESULT|`
  no `testlog.sh`; V3: cena por JSON ao lado da topologia.

### Fase C — reorganizar a didática (futuro, não agora)

- Hub `/lab` por **disciplina** (espelhando `pdfs/01-ric · 02-ric-ai ·
  03-dados-telecom`), aulas como conteúdo plugável (os geradores de
  `02-ric-ai/lab-didatico/` já produzem HTML — viram "pacotes" por disciplina).
- Roster/results ganham dimensão de disciplina/turma.
- Candidatos novos: lab do mini-lake (disciplina 03) e o "Projeto 3" Non-RT
  ([non-rt-ric.md](non-rt-ric.md)) — nascem já na camada certa.

## 4. O que NÃO muda agora

- Nenhuma rota, página ou script de deploy (Fase A é reorganização interna).
- As aulas existentes continuam como estão até a Fase C ("futuramente
  mexemos nas aulas").
- O pendente do [plano de redesign](plano-painel-redesign.md) (remap v1→v2 dos
  comandos P2) segue válido e é **pré-requisito** da Fase B (logs do core v2).

## 5. Ordem sugerida

1. Fase A (separação) — destrava tudo, risco baixo.
2. Remap v1→v2 do plano de redesign (se ainda pendente no servidor).
3. Fase B (logs Nível 0) — entrega visível para a disciplina 03 (fontes de
   dados/logs são literalmente o tema das aulas 01–02).
4. Fase C — quando a disciplina 03 pedir seu lab, já nasce no modelo novo.
