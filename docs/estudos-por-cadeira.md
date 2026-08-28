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

## Exercícios do professor (Plataforma de Atividades — v0.72.0)

O Prof. Jonas mantém os exercícios das três cadeiras numa aplicação própria, a
**Plataforma de Atividades da CESAR School** (Cloud Run, pública, rotas por
hash). Participação e conclusão contam na nota — a plataforma avisa o docente
por e-mail. O painel **não reproduz os enunciados nem responde nada por lá**:
lista os exercícios e leva até eles, e liga cada um ao que já temos.

| Plataforma | Cadeira do painel | Exercícios |
|------------|-------------------|-----------:|
| Módulo 05 `#oran` — Interfaces e Protocolos O-RAN | Estudo 1 | 12 |
| Módulo 07 `#ric` — RAN Intelligent Controller (RIC) | Estudo 2 | 7 |
| Módulo 09 `#data` — Análise de Dados em Redes de Telecom | Estudo 4 | 7 |
| — | Estudo 3 (IA/ML em RIC) | 3, por referência cruzada ao Módulo 05 |

O Estudo 3 não tem módulo próprio na plataforma; recebe os três exercícios de
IA/ML que vivem no Módulo 05, com o aviso na tela de que vêm de lá.

Schema, dentro de cada estudo do `index.json`:

```jsonc
"atividades": {
  "modulo": "Módulo 09", "hash": "#data",   // "cruzada": true no Estudo 3
  "itens": [
    {"rot": "Aula 04", "t": "KPIs e QoE", "d": "…", "h": "#data/aula04",
     "prep": {"aula": 4, "cmd": "p2-kpi-qoe"}}
  ]
}
```

`prep` é a ponte para o nosso lab e aceita três formas, combináveis:
`{"aula": n}` (aula desta cadeira), `{"cmd": "id"}` (comando do console, rótulo
vindo de `index.comandos`) e `{"href": "/lab/…", "rot": "…"}` (página do Lab de
IA). O domínio da plataforma fica **uma vez só**, em `index.plataforma.url`; os
itens guardam apenas o hash.

Os textos dos exercícios são **citação literal** da plataforma e ficam em
português nos quatro `index*.json` — é o que o aluno vê ao clicar. Só a moldura
da seção é traduzida (chaves `est.ativ_*` em `lab-i18n.js`); `atividades.modulo`
vira "Module 0N" em en/fr.

Renderiza no fim de `/lab/estudo/N`, depois de "Próximas aulas": cartão por
exercício com rótulo, título, descrição, o botão **Abrir ↗** (ação principal,
abre em outra aba) e a linha "Prepare-se aqui" com os atalhos do nosso lab.

### Registro do resultado e o percentual (v0.73.0)

O que interessa entre exercícios de tamanhos diferentes não é a pontuação
bruta, é a **fração acertada**. O aluno faz o exercício na plataforma e
registra aqui quanto acertou; o painel calcula o percentual e consolida a
cadeira. Ninguém vê o resultado de ninguém.

O **denominador** saiu do bundle da própria plataforma (estrutura de pontuação
dos componentes React), não de estimativa — 23 dos 26 exercícios:

| Exercícios | Composição | Total |
|---|---|--:|
| 14 aulas dos Módulos 07 e 09 | Conceitos 3 · Cenários 6 · Profundidade 3 · Sequência 10 | 22 |
| Interfaces A1, E2, O1, O2 (M05) | mesma composição, rótulos próprios | 22 |
| Fronthaul, eCPRI, ML na RAN, Workflow IA/ML (M05) | Quiz 3 · Situações 6 | 9 |
| Aula 01 do M05 | Bloco 1 · 2 · 3, 3 pontos cada | 9 |
| Aventura O-RAN, Lab de dígitos, Lab Open5GS | componente próprio | **sem `pts`** |

Sem `pts` no item, o formulário pede os **dois** números; com `pts`, pede só os
acertos e o total vem do catálogo (o navegador não escolhe o denominador).

Endpoints em `lab.py`, guardando em `RESULTS_DIR/estudos_resultados.json`
(escrita atômica via arquivo temporário + `replace`):

- `GET /api/estudos/resultados` — só o registro de quem está logado.
- `POST /api/estudos/resultado` — `{ex, acertos[, total]}` ou `{ex, limpar}`.
  Recusa hash fora do catálogo (400) e acerto fora do intervalo (400).

**A chave é o e-mail, não o login**: os alunos entram todos pelo mesmo usuário
convidado e se identificam com nome + e-mail (o mesmo par que a presença já
usa). O Professor, que tem login próprio, é chaveado pelo login.

## Testes

- `cd server/panel/test && node i18n-parity.js` — as chaves novas
  (`rail.estudos`, `rail.e1..e4`, `rail.aulas*`, `t.tema_*`, `est.ativ_*`)
  existem nos 4 idiomas. Desde a 0.72.0 o teste cobre **dois** dicionários:
  `static/i18n.js` e `static/lab/lab-i18n.js` (este último estava fora, e é
  onde vive toda a moldura dos Estudos).
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
