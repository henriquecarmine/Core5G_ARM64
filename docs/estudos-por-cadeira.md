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
| 4 | Análise de Dados em Redes de Telecom | Prof. Jonas A. Kunzler | P2 / arquivo | 6 | análise KPM (ETL/KPI) e **os 7 temas do projeto integrador** |

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
├── e4a01.json … e4a06.json
└── ex/          # os exercícios (ver "Exercícios das cadeiras")
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

## Exercícios das cadeiras — todos no painel (v0.87.0)

Até a v0.86 os exercícios viviam na **Plataforma de Atividades da CESAR School**,
uma aplicação React do Prof. Jonas (Cloud Run, rotas por hash, conclusão
avisada ao docente por e-mail), e o painel só listava e levava até lá. A
plataforma **saiu do ar em setembro de 2026**. Os 27 exercícios passaram a ser
nossos: escritos no nosso formato, corrigidos na hora, com o porquê de cada
resposta, e o resultado gravado na ficha do aluno.

| Cadeira do painel | Módulo da especialização | Exercícios |
|---|---|--:|
| Estudo 1 — Interfaces e Protocolos O-RAN | Módulo 05 (`#oran`) | 12 |
| Estudo 2 — RAN Intelligent Controller (RIC) | Módulo 07 (`#ric`) | 7 |
| Estudo 3 — Aplicações de IA e ML em RIC | (usa 3 do Módulo 05, os de IA/ML) | 3 |
| Estudo 4 — Análise de Dados em Redes de Telecom | Módulo 09 (`#data`) | 8 |

O `h` de cada exercício (`#data/aula04`, `#oran/aulaa1`…) herdou o hash da
plataforma e continua sendo **só a chave estável** do resultado do aluno —
trocar o nome apagaria o histórico de quem já fez.

### Onde está cada coisa

```
server/panel/static/lab/estudos/
├── index.json          # catálogo: `atividades.itens` com rot, t, d, h, pts, partes, prep
└── ex/
    ├── LEIAME.md       # o formato (escolha · ordem · associar) e as regras
    └── <modulo>-<id>.json   # um arquivo por exercício: #ric/aula03 → ric-aula03.json
server/panel/static/lab/lab-exercicio.html   # /lab/estudo/{n}/exercicio/{slug}
server/panel/static/lab/lab-digitos.html     # /lab/digitos (inferência no navegador)
server/panel/static/lab/lab-dashboard-kpi.html  # /lab/dashboard-kpi (NOC sobre as 100 amostras KPM)
```

`prep` liga o exercício ao que se estuda antes, em três formas combináveis:
`{"aula": n}`, `{"cmd": "id"}` (comando do console) e `{"href": "/lab/…", "rot": "…"}`.

### Pontuação: fiel à estrutura do professor

A composição de cada exercício saiu do código da plataforma (os `maxPoints` e
as telas de cada componente), para que a nota continue comparável:

| Exercícios | Composição | Total |
|---|---|--:|
| 7 do Módulo 07, 6 aulas + lab do Módulo 09 | Conceitos 3 · Cenários 6 · Profundidade 3 · Sequência 10 | 22 |
| Interfaces A1, E2, O1, O2 (M05) | mesma composição, rótulos próprios | 22 |
| Aventura O-RAN (M05, aula 02) | Conceitos 3 · Mapeamento 6 · Fronthaul 3 · Comparação 10 | 22 |
| Lab Open5GS (M05) | Core 3 · Ordenar o roteiro 6 · N2/N3 e E2E 3 · Troubleshooting 10 | 22 |
| Fronthaul, eCPRI, ML na RAN, Workflow IA/ML (M05) | Quiz 3 · Situações 6 | 9 |
| Lab de dígitos (M05) · Dashboard KPI/NOC (M09) | Quiz 3 · Situações 6 | 9 |
| Aula 01 do M05 | Bloco 1 · 2 · 3 (3 cada) · Organizar funções nas unidades 6 | 15 |

Três exercícios da plataforma não tinham nota no original e ganharam agora:
**Aventura O-RAN** (o arrasta-e-solta e a classificação viraram o tipo
`associar`, com item que aceita mais de um alvo), **Lab Open5GS** (reescrito
para o nosso P1 — o original citava o ambiente `open5gs-containerized` do
professor, que o aluno não tem) e **Lab de dígitos**, que no site nunca
funcionou (o endpoint de inferência veio vazio no build) e aqui é uma página
de verdade com o modelo rodando no navegador. A **Aula 01 do M05** vale 15, e não os 9 que o painel anunciava desde a 0.73: o
levantamento antigo não viu a quarta tela do componente (arrastar 6 funções
para RU, DU e CU, 6 pontos). O **Dashboard KPI/NOC** era só
uma página no site; virou página + exercício de diagnóstico.

### Como foram escritos

Cada exercício cobre **os mesmos conceitos** do original, na mesma proporção —
foi para isso que o aluno estudou — mas nenhum foi copiado: no original a
certa era quase sempre a primeira alternativa e as erradas às vezes absurdas.
Os nossos têm distratores que representam confusões reais, a posição da certa
variando, `porque` em toda pergunta e cada fato conferido nos slides, nas
aulas do painel ou no código do lab. Onde o original estava errado, a versão
nossa corrige.

### O arquivo da plataforma (fora do git)

Antes de o site sair do ar, o bundle foi guardado em
`external/plataforma-cesar/2026-09-11/` (ignorado pelo git: é material do
professor e o repositório é público): `index.html`, `assets/`, `SHA256SUMS`,
`exercicios-extraidos.json` (módulos e os objetos de configuração de `#data` e
`#ric`), `fontes/<modulo>-<id>.js.txt` (o código de cada exercício, com as
subtelas e as constantes de dados) e `analise-4-especiais.md` (os quatro
interativos destrinchados, com gabaritos). Os scripts que extraíram tudo
(`extrair.js`, `extrair-oran.js`, `fontes-por-exercicio.js`) ficam junto. A
extração é estática: nenhum exercício foi aberto no site, porque abrir e
concluir avisava o professor por e-mail.

### Resultado e percentual

O que se compara entre exercícios de tamanhos diferentes é a **fração
acertada**. A página do exercício corrige, mostra o placar contra a média de
passagem (`media` do catálogo, 70%) e manda só os **acertos**; o total vem
sempre do catálogo, nunca do navegador. O hub da cadeira mostra o percentual de
cada um e o consolidado. Ninguém vê o resultado de ninguém.

Endpoints em `lab.py`, guardando em `RESULTS_DIR/estudos_resultados.json`
(escrita atômica via arquivo temporário + `replace`):

- `GET /api/estudos/resultados` — só o registro de quem está logado.
- `POST /api/estudos/resultado` — `{ex, acertos}`. Recusa hash fora do
  catálogo e acerto fora de `0..pts` (400).

**A chave é o e-mail, não o login**: os alunos entram todos pelo mesmo usuário
convidado e se identificam com nome + e-mail (o mesmo par que a presença já
usa). O Professor, que tem login próprio, é chaveado pelo login.

## Testes

- `cd server/panel/test && node i18n-parity.js` — as chaves novas
  (`rail.estudos`, `rail.e1..e4`, `rail.aulas*`, `t.tema_*`, `est.ativ_*`)
  existem nos 4 idiomas. Desde a 0.72.0 o teste cobre **dois** dicionários:
  `static/i18n.js` e `static/lab/lab-i18n.js` (este último estava fora, e é
  onde vive toda a moldura dos Estudos).
- `cd server/panel/test && node exercicios.js` — todo item do catálogo tem
  arquivo, pontos batendo, `porque` em toda pergunta, gabarito apontando para
  alternativa ou alvo que existe; e nenhuma página cita o domínio da plataforma.
- `python3 server/oai-cn-gnb-e2/scripts/temas/temas_projeto.py --tema all --file
  server/oai-cn-gnb-e2/scripts/temas/samples/kpm_ue_tp_sample.jsonl` — rc 0 e a
  tabela "7 temas lado a lado".
- Smoke local (uvicorn na porta 8765 + curl): login → `/lab/estudo/{1,3,4}`,
  `/lab/estudo/4/aula/3` (200), `/lab/estudo/9` (404), `POST /api/run/p2-tema-t1`,
  upload de CSV colado sem fase + `p2-tema-t2` com `KPM_FILE`, CSV inválido → 400.

## Pendências

- Os enunciados dos exercícios só em PT (aulas e UI seguem nos 4 idiomas).
- Estudo 1: só a aula 01 existe em PDF; os exercícios das aulas 02, 04 e 05 do
  Módulo 05 foram escritos a partir do escopo da plataforma e das aulas do RIC.

## Unidades das três KPMs (corrigido em 0.64.2)

O JSONL do professor não carrega unidade, mas o xApp KPM do FlexRIC imprime e o
slide 66 da aula 01 mostra: `DRB.UEThpUl` em **kbps**, `RRU.PrbTotUl` em **%**
(fração dos PRB de subida em uso) e `DRB.RlcSduDelayDl` em **µs**. Até a 0.64.1 o
painel e o CP1 do Grupo 6 diziam "ms" e "PRBs"; corrigido em `temas_projeto.py`,
`TEST_EXPLAIN`, `estudos/index.json`, cartão 💾 e nos arquivos de
`pdfs/03-dados-telecom/projeto/`. Consequência didática: 150 µs de atraso RLC não
é experiência ruim, então o limiar do T3/T7 (`TEMA_DELAY_MAX=100` µs) marca a
**mudança de regime** em relação ao baseline, não QoE.

## Idiomas e aulas em prévia

- A moldura de `/lab/estudo/N` e `/lab/estudo/N/aula/K` usa `lab-i18n.js`
  (chaves `est.*` e `aula.*`, 4 idiomas). O conteúdo vem de
  `estudos/<id>.<lang>.json` quando existe (en/es/fr) e cai para `<id>.json` (pt).
  Trocar de idioma recarrega a página.
- Aula sem slides publicados: `"slide": null, "previa": true, "nota": "..."` no
  JSON; o renderizador mostra badge e faixa de prévia e o rodapé cita as fontes.
  Exemplo: `e4a04.json` (KPIs, KQIs, QoS e QoE, montada do plano de ensino).
