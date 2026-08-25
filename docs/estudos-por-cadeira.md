# Estudos por cadeira — o painel organizado como a especialização (v0.64.0)

O painel tem duas redes (P1 = Open5GS + UERANSIM; P2 = OAI + FlexRIC + Non-RT
RIC) e, até a v0.63, uma lista plana de ~25 testes. A partir da v0.64.0 os
**exercícios (testes) e as aulas ficam divididos por cadeira** da especialização
Open RAN da CESAR School, no mesmo lugar onde o aluno já trabalha:

| Estudo | Cadeira | Professor | Bancada | Aulas detalhadas | Exercícios |
|---|---|---|---|---|---|
| 1 | Interfaces e Protocolos O-RAN | Prof. Jonas A. Kunzler | P1 | 1 (só a aula 01 foi compartilhada) | status, NG Setup, registro, coerência, E2E, throughput, failover |
| 2 | RAN Intelligent Controller (RIC) | Prof. Jonas A. Kunzler | P2 | 6 | E2 SM, E2SM-KPM (com/sem tráfego), E2SM-RC, coleta KPM real, ciclo A1 |
| 3 | Aplicações de IA e ML em RIC | Prof. Julio C. C. Tesolin | P2 | 9 (as páginas do Lab de IA) | UE-TP, Localização, Manutenção preditiva |
| 4 | Análise de Dados em Redes de Telecom | Prof. Jonas A. Kunzler | P2 / arquivo | 3 (+3 a caminho) | análise KPM (ETL/KPI) e **os 7 temas do projeto integrador** |

## Onde aparece

- **Console (`/`)**, rail esquerdo: grupo *Estudos · por cadeira* com um
  `<details>` por cadeira (estado aberto/fechado lembrado no navegador). Cada
  bloco de testes continua travando com o projeto que não está no ar
  (`data-proj-tests="p1|p2"`); os 7 temas usam `data-proj-tests="any"` porque
  rodam sobre arquivo e não precisam da RAN. O link *📖 Aulas* abre o hub da
  cadeira embutido no console (mesmo mecanismo do Lab de IA).
- **Hub da cadeira (`/lab/estudo/{1..4}`)**: resumo, bancada, link dos slides,
  lista das aulas, exercícios e, no Estudo 4, os dados do projeto (as 3 métricas
  KPM), os **7 temas com fórmula e unidade dos 2 indicadores** e as próximas aulas.
- **Aula (`/lab/estudo/{n}/aula/{k}`)**: objetivos, os conceitos na ordem dos
  slides, as fórmulas/métricas, *onde isso roda no nosso lab* (com o mini-mapa
  do projeto aceso na cena certa), os exercícios que a aula pede, um quiz de
  fixação e a fonte (arquivo e páginas dos slides).
- **Hub do Lab de IA (`/lab`)**: 4 cards no topo levam a cada Estudo (o Lab de
  IA é o Estudo 3).

## Conteúdo plugável (Fase C do plano de duas camadas)

Nada de HTML por aula. O conteúdo vive em JSON:

```
server/panel/static/lab/estudos/
├── index.json    # catálogo: 4 cadeiras, rótulos dos comandos, os 7 temas (fórmulas)
├── e1a01.json    # uma aula = um arquivo (extraído dos slides do professor)
├── e2a01.json … e2a06.json
└── e4a01.json … e4a03.json
```

Schema de uma aula: `id, n, titulo, slide, resumo, objetivos[], conceitos[{t,d}],
formulas[{nome,expr,vars,unidade,quando}], onde{scene,texto}, exercicios[cmd],
quiz[{q,a}], fontes`. `onde.scene` é o nome de uma cena do `mini-map.js`
(`reg · kpm · rc · analytics · ml · thp · failover · check · a1 · tema`).
Para adicionar uma aula: criar `eNaKK.json` e listar o id em `index.json`.
Duas páginas genéricas (`lab-estudo.html`, `lab-aula.html`, CSS em
`lab-estudos.css`) leem o caminho e renderizam. Rotas em `lab.py`.

## Os 7 temas do projeto integrador (Estudo 4)

`server/oai-cn-gnb-e2/scripts/temas/temas_projeto.py` (só biblioteca padrão) +
wrapper `scripts/p2_temas.sh t1..t7|all`; comandos `p2-tema-t1 … p2-tema-all`
em `ops.py`. Todos os grupos partem dos mesmos dados (o `kpm-ue-tp-sample` do
professor, vendorizado em `scripts/temas/samples/`); cada tema imprime a
pergunta do card, **as fórmulas dos 2 indicadores antes dos números**, as
tabelas por fase, a leitura, a recomendação como **política A1 em dry-run** (JSON
no formato do `decision.json` do professor) e as limitações. O T2 reproduz o
`model.json` do professor (`robust-baseline-mad`, `mad_floor 1.0`, limiar 3.5,
2 métricas, janela 5). Limiares ajustáveis por `TEMA_*` (documentados no
docstring).

Faixa de execução (`flow-strip.js`, cena `tema`): 💾 KPM (3 fases) → 🧪 silver →
📐 2 indicadores → 🧭 recomendação; mini-mapa (`mini-map.js`, `MMAP.tema`):
xApps → painel, com a linhagem UE → gNB → RIC → xApps tracejada.

### Fonte dos dados: sugerida × arquivo × colado

O nó 💾 da faixa abre o mesmo cartão de fonte de dados dos labs de ML, agora
para a chave `kpm`: **1.** amostra do professor; **2.** meus dados, por
**arquivo** (`.jsonl` no formato do professor, `.csv` largo com
`thp_ul,delay_dl,prb_ul[,phase,…]` ou o CSV longo do `kpm_analytics.sh`) ou
**colado à mão** na caixa de texto. Sem coluna de fase, as primeiras 20% viram
baseline (o script avisa). Endpoints: `GET /api/lab-data/kpm`,
`GET …/example`, `POST …/source`, `POST …/upload` (corpo cru, ≤ 8 MB; só o
professor). O arquivo fica em `panel_uploads/labdata/kpm/kpm_custom.txt` e
`run_command` injeta `KPM_FILE` nos comandos `p2-tema-*`.

## Testes

- `cd server/panel/test && node i18n-parity.js` — as chaves novas
  (`rail.estudos`, `rail.e1..e4`, `rail.aulas*`, `t.tema_*`) existem nos 4
  idiomas.
- `python3 server/oai-cn-gnb-e2/scripts/temas/temas_projeto.py --tema all --file
  server/oai-cn-gnb-e2/scripts/temas/samples/kpm_ue_tp_sample.jsonl` — rc 0 e a
  tabela "7 temas lado a lado".
- Smoke local (uvicorn na porta 8765 + curl): login → `/lab/estudo/{1,3,4}`,
  `/lab/estudo/4/aula/3` (200), `/lab/estudo/9` (404), `POST /api/run/p2-tema-t1`,
  upload de CSV colado sem fase + `p2-tema-t2` com `KPM_FILE`, CSV inválido → 400.

## Pendências

- Conteúdo das aulas só em PT (a UI do console segue nos 4 idiomas).
- Estudo 4: aulas 04–06 entram quando o professor compartilhar os slides.
- Estudo 1: só a aula 01 existe em PDF.
