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
├── index.json    # catálogo: as cadeiras, rótulos dos comandos, os 7 temas (fórmulas)
├── e1a01.json    # uma aula = um arquivo (extraído dos slides do professor)
├── e2a01.json … e2a06.json
├── e4a01.json … e4a06.json
├── e5a00.json, e5a01.json   # Gestão e Orquestração (SMO): o professor começa na Aula 0
└── ex/          # os exercícios (ver "Exercícios das cadeiras")
```

Schema de uma aula: `id, n, titulo, slide, resumo, objetivos[], conceitos[{t,d}],
formulas[{nome,expr,vars,unidade,quando}], onde{scene,texto}, exercicios[cmd],
quiz[{q,a}], fontes`. `onde.scene` é o nome de uma cena do `mini-map.js`
(`reg · kpm · rc · analytics · ml · thp · failover · check · a1 · tema`, e as do
SMO: `smoarq · smoo1 · smoprov · smofm · smopm · smolcm · smoocloud`).
Para adicionar uma aula: criar `eNaKK.json` e listar o id em `index.json`; para
uma cadeira nova, uma entrada em `estudos` (nos 4 `index*.json`). As rotas de
`lab.py` aceitam as cadeiras e o número de aulas que o catálogo tiver. A URL
`/lab/estudo/N/aula/K` usa a **posição** K da aula na lista `aulas`; o número
mostrado na tela é o `n` do JSON, o do professor (a Aula 0 da cadeira 5 abre em
`aula/1`). Duas páginas genéricas (`lab-estudo.html`, `lab-aula.html`, CSS em
`lab-estudos.css`) leem o caminho e renderizam.

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

## Cenários sugeridos pelo servidor — 1, 2, 5, 10 celulares × distância × interferência (v0.89.0)

A amostra do professor tem **1 celular, sem distância nem interferência**. O
cartão 💾 dos testes de dados (os 7 temas, `p2-kpi-qoe`, `p2-closed-loop`)
ganhou uma segunda opção em "Sugerida pelo servidor": **gerar um cenário**.

| Parâmetro | Opções |
|---|---|
| celulares | 1 · 2 · 5 · 10 |
| distância | 100 m · 500 m · 1 km · 3 km (borda) · misturadas (100 m, 500 m, 1 km, 3 km em rodízio) |
| interferência | nenhuma · fraca (C/I 20 dB) · média (C/I 15 dB) · alta (C/I 5 dB), ativa nas amostras 20–44 do stress |

`server/oai-cn-gnb-e2/scripts/temas/cenarios_kpm.py` (stdlib, importado pelo
painel) gera os mesmos 100 instantes da amostra (baseline 20 · stress 60 ·
recovery 20), um registro por celular, no formato JSONL do professor, com
`"cenario": {"sintetico": true, …}` e `"radio": {dist_m, sinr_db,
interferencia_ativa}` em cada linha. **É dado sintético e cada teste diz isso.**

A cadeia do modelo é a mesma física do Lab do UE do P1 (`test_channel.sh`),
calibrada na amostra real:

1. perda de percurso 3GPP TR 38.901 UMa NLOS a 3,5 GHz (102,6 / 129,9 / 141,7 / 160,3 dB);
2. RSRP = 58,6 − PL (a calibração do Lab do UE: −44 dBm a 100 m);
3. SNR = min(30, 0,65·(RSRP + 105)) — mapa didático das faixas de drive test;
4. com interferência, SINR = 1 / (1/SNR + 1/(C/I)) em linear;
5. η = min(7,4 ; log2(1 + SINR)) (Shannon, teto ~256QAM);
6. vazão por celular = (80 023,7 kbps / N) · η / η_ref — os PRB divididos por igual;
7. atraso RLC = 158,9 · (1 + 0,35·(N − 1)) · √(η_ref/η) µs.

1 celular a 100 m sem interferência **reproduz a amostra real** (testado). A
janela de interferência deixa o PRB em 99% e derruba a vazão: a assinatura de
jammer da matriz do slide 26 da aula 05, dentro do mesmo arquivo.

**A explicação na tela.** Antes do resultado, cada teste imprime o bloco
"Cenário sugerido pelo servidor (DADOS SINTÉTICOS)": as 7 fórmulas, a tabela
por celular (distância, PL, RSRP, SNR, η, vazão **esperada × observada**, e o
mesmo com interferência), a célula (PRB, vazão somada e a queda com
interferência), quanto cada usuário recebe comparado a 1 celular perto, e
"como ler este teste neste cenário" — texto próprio para T1 a T7, aula 04 e
closed loop (no closed loop: quantos celulares já estão abaixo dos 8 Mbit/s da
política, caso em que o rate-limit não cortaria nada). As limitações de cada
tema passam a dizer que o dado é sintético, em vez de "1 UE em RFSIM".

**Vários celulares nos testes.** Com mais de um celular, as regras que olham o
tempo (média móvel do T4, janela do MAD, persistência do T7) rodam sobre a
**célula** — `Data.celula()`: uma linha por instante, vazão e atraso pela média
dos usuários, PRB da célula, e `thp_soma` para o T5. Na lista crua os usuários
se intercalariam e a "janela de 5" misturaria 5 celulares do mesmo instante.
Com a amostra real (1 celular) nada muda: as 10 saídas foram comparadas antes
e depois da mudança e são idênticas, fora horários e IDs.

API (`ops.py`): `GET /api/lab-data/kpm` devolve `opcoes` (do próprio gerador),
`cenario` e `has_suggested`; `POST /api/lab-data/kpm/suggest {ues, distancia,
interferencia}` (só Professor) gera `panel_uploads/labdata/kpm/kpm_sugerido.jsonl`
e passa a fonte para `suggested`; o `run_command` injeta `KPM_FILE` do arquivo em
uso; a prévia "os dados" mostra a coluna do celular.

Testes: `test_cenarios.py` (11, em `npm run test:tudo`) — determinismo, limites
físicos, equivalência com a amostra real, monotonia com N, distância e
interferência, PRB igual dentro e fora da janela, visão da célula, os três
scripts em 10 cenários. O cartão foi testado no Chrome com a API simulada.

**Não é possível (ainda) nos testes ao vivo:** o Lab do UE do P1 já aplica
distância e interferência de verdade (`tc netem` em `uesimtun0`), mas com **1**
UE; vários celulares ao vivo pedem subir N UEs no UERANSIM e medir a carga do box.

## Closed loop A1 das aulas 05 e 06 — `p2-closed-loop` (v0.88.0)

As aulas 05 e 06 fecham o laço que o projeto só recomenda: KPM → MAD →
decision → policy A1 → PMS/Mediator → consumer → action_request → actuator →
KPM after → effect_report → rollback. O código do lab do professor que faz isso
(`ai_policy_pipeline.py`, `closed_loop_actuator.py`, `kpm_store.py`,
`run_closed_loop_lab.sh`) está na cópia local do repositório dele
(`external/cesar-school-repo/data/code/oai-cn-gnb-nonrt-nearrt/`, MIT).

`server/oai-cn-gnb-e2/scripts/temas/closed_loop.py` (só biblioteca padrão,
reusa o carregador e o MAD de `temas_projeto.py`) + wrapper
`scripts/p2_closed_loop.sh` percorrem os **8 passos do roteiro da demo**
(slide 23 da aula 06) sobre a mesma telemetria dos 7 temas (ou o arquivo
enviado no cartão 💾, via `KPM_FILE`):

| Passo | O que o teste faz | Ao vivo seria |
|---|---|---|
| 1. Pré-checagem | lê o arquivo e define baseline / carga / depois pelas fases | Near-RT, PMS `/a1-policy/v2/status`, xApp, nrUE |
| 2. Baseline calmo | treina o MAD só no baseline → `model.json` | `KPM_TRAFFIC=0` |
| 3. Stress | resume a fase de carga | iperf UDP UL + `kpm_before` |
| 4. Decisão | janela das últimas 5 amostras, `apply` se a maioria é anômala (regra do `ai_policy_pipeline.py`) → `decision.json` | idem |
| 5. A1 | monta a policy (type 1, priorityLevel) em dry-run → `policy.json` | PMS → Mediator → RMR 20010/20011 |
| 6. Atuação | `action_request.json` (rate_limit 8 Mbit/s, `oaitun_ue1`, uplink); o `tc tbf` é **impresso** | `sudo tc qdisc add … tbf` |
| 7. After + report | `effect_report.json` com média, mediana, relativo e pp | nova KPM com o limite ativo |
| 8. Rollback | o `tc qdisc del` é **impresso**; fórmula de recuperação | remover e medir a volta |

Termina no **SEHAL** e grava os artefatos em
`server/oai-cn-gnb-e2/logs/closed_loop_offline/` (ignorado pelo git),
incluindo `actuator_events.jsonl`.

**O que o teste se recusa a afirmar.** O modo offline do professor usa como
"depois" a fase de recuperação do mesmo experimento (`run_closed_loop_lab.sh
--offline`: "after ≈ baseline"), e o `effect_report` dele mostra a vazão caindo
78 mil kbps como se fosse efeito. Não é: nenhum `tc` rodou. O nosso relatório
sai com `"causal": false` e a tela diz "NÃO É EFEITO DA ATUAÇÃO" — é a pergunta
do slide 73. Os números da execução **ao vivo** dos slides (135,8 → 39,0
Mbit/s; PRB −73,4 pp) aparecem como referência, marcados como copiados do slide.
`closed_loop.py` nem importa `subprocess`, e um teste garante isso.

Testes: `python3 server/oai-cn-gnb-e2/scripts/temas/test_closed_loop.py`
(também em `npm run test:tudo`): decisão `apply` na amostra, cadeia e artefatos
completos, relatório nunca causal, `observe` sem carga não gera policy nem
ação, sem fase "depois" não há relatório, contas da aula batendo com os slides.

**Ainda não feito:** a versão **ao vivo** (`tc tbf` de verdade na `oaitun_ue1`
sob iperf, KPM real antes/depois, rollback medido). Precisa do servidor ligado,
de trava de carga (tráfego de subida já saturou o box) e de dizer na tela que o
nosso lab não tem A1 Mediator nem consumer: a atuação sairia da decisão local.
A atuação real por E2SM-RC fica de fora (PoC no OAI; a action 6 derruba o gNB).

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
