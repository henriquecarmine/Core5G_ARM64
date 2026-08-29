# A Jornada do UE em linguagem simples

> Guia de bolso para abrir do lado enquanto você clica na **Jornada do UE**
> (no painel: **Topologia → botão "Jornada do UE"**). Cada tela da jornada é uma
> linha aqui embaixo — **sem grego**. Os nomes técnicos aparecem só entre
> parênteses, para você reconhecer o que está na tela.

## A ideia em uma frase

Um celular entrando na rede é como **uma pessoa chegando num prédio**: ela chega,
se identifica, passa pela segurança, ganha a **chave de um quarto** e um
**endereço**, e aí pode **mandar e receber correspondência**. É só isso — o resto
é detalhe de "quem faz o quê".

---

## Projeto 2 (OAI + RIC) — as 16 telas

| Na tela aparece | O que está acontecendo (simples) |
|---|---|
| **1. O celular liga** | A pessoa chega na porta do prédio. O celular acorda e vai tentar entrar na rede. |
| **2. Rádio — conexão física** | Ela encosta na portaria. É o contato físico (o "rádio") entre o celular e a antena. |
| **3. gNB ↔ Core — controle** | A portaria (antena) liga para a administração do prédio (o núcleo da rede): "chegou alguém". |
| **4. Registro do UE** | A pessoa se apresenta: "sou fulano, quero entrar". |
| **5. O catálogo do Core (NRF)** | A administração olha a lista interna do prédio: "quem cuida da segurança? quem entrega as chaves?". |
| **6. Autenticação** | A segurança confere o documento — é você mesmo? Se não bater, não entra. |
| **7. Pedido de sessão de dados** | Aprovado, você pede uma "linha" para mandar e receber coisas. |
| **8. Programa o plano de usuário** | A administração avisa o corredor de entregas: "prepare o caminho das cartas dessa pessoa". |
| **9. O UE recebe IP** | Você ganha a **chave do quarto** e um **endereço** — agora dá para receber correspondência. |
| **10. Dados — ida** | Você manda uma carta para fora. |
| **11. Saída — internet / chamada** | A carta sai do prédio para o mundo (a internet). |
| **12. Dados — volta** | A resposta chega e sobe de volta até você. |
| **13. Coleta de dados (RIC)** | Um **supervisor esperto** começa a anotar como está o movimento (velocidade, lotação) — os números vêm lá da antena. |
| **14. Ação na antena (RIC)** | O supervisor decide e **ajusta o fluxo em tempo real** (abre mais espaço, muda a fila). É ele "mexendo na antena" à distância. |
| **15. Planejador de longo prazo** | Um planejador estuda o histórico e manda **regras** para o supervisor. É aqui que a **inteligência artificial** entra. |
| **16. O caminho completo** | O prédio inteiro de uma vez: o que é obrigatório e o que é o extra "inteligente". |

---

## Duas cores, dois tipos de passo

- 🟢 **obrigatório** — tem que acontecer, senão você não entra ou não navega. É a
  **linha da vida** (telas 2 a 12).
- 🔵 **opcional** — o extra "inteligente" (o supervisor e o planejador, telas 13 a
  15). A rede funciona sem — mas é aqui que mora a IA.

## A sacada mais importante: "quem decide" ≠ "quem carrega"

No prédio, **a administração** (que decide, autoriza, organiza) é **separada** dos
**corredores** (por onde as cartas realmente andam). Isso tem um nome feio (CUPS),
mas a ideia é simples e poderosa: dá para **trocar um corredor sem parar a
administração**. É o que permite o próximo truque 👇

---

## Projeto 1 (Open5GS) — quase igual, com 2 diferenças

A história é a mesma (o celular chegando no prédio). Muda só isto:

1. **Não tem o supervisor esperto** (o RIC). O P1 vai da tela 1 até "o caminho
   completo", sem as partes de inteligência.
2. **Tem um final extra: o corredor reserva** (o *failover*). Se o corredor de
   entregas cai, a administração **muda para um corredor reserva na hora** — e
   você continua navegando sem perceber. É a prova de que separar "quem decide"
   de "quem carrega" vale a pena.

---

## Como usar para a ficha cair

1. Abra a **Jornada do UE** no painel e este guia do lado.
2. Clique **Próximo** devagar, lendo a legenda da tela **e** a linha aqui.
3. Passe **2 ou 3 vezes**. Na segunda, você já vai anteceder o que vem.
4. Só depois, se quiser, olhe os nomes técnicos — agora eles têm um lugar na
   história, não são mais siglas soltas.

> Dica: o mesmo diagrama tem um modo **"Fluxo de dados"** (bolinhas andando) e um
> **"Tour"** por camadas. A **Jornada** é a versão passo a passo, guiada — comece
> por ela.

---

## As siglas explicadas na própria tela

Desde a **v0.81.0** você não precisa mais sair da Jornada para saber o que é uma
sigla. Na legenda de cada passo:

- o **nome por extenso** aparece **entre parênteses** logo depois do termo —
  *AMF (Access and Mobility Management Function)*, *N4 (SMF ↔ UPF)*;
- **passar o mouse** (ou tocar, ou chegar pelo **Tab**) abre um balão com
  **o que é** e **para que serve** — em pt/en/es/fr;
- **Esc** fecha o balão.

São **128 termos** (v0.84.0): funções do núcleo, interfaces N/E2/A1/O1/O2,
protocolos, procedimentos, a pilha de rádio (RRC/RLC/MAC/PHY), o que se mede
(KPI, KQI, QoE, SLA, os contadores KPM), o vocabulário do RIC, o mundo de dados
(ETL, DIKW, OLAP, TSDB, PCA, k-means…) e os bancos do lab.

**Onde o glossário funciona**

| Tela | O que marca | Nome por extenso |
|---|---|---|
| Jornada do UE e Tour | título e legenda de cada passo | uma vez **por passo** |
| Desenho da topologia | os rótulos das interfaces (N4, E2, Nausf…) | só o balão — o rótulo é pequeno demais |
| Aulas e Estudos | resumo, conceitos, fórmulas, quiz | uma vez **por página** |
| 10 labs de ML | os cartões de texto | uma vez **por página** |

A diferença entre "por passo" e "por página" foi tirada de olhar a tela: numa
legenda curta, lida isolada, marcar toda ocorrência ajuda; numa aula, não —
a primeira página saiu com **338 sublinhados** e virou um campo pontilhado.
Numa aula o termo se apresenta uma vez, e depois já é vocabulário.

Dentro de `<code>` e `<pre>` **nunca** se marca: ali a sigla é literal, e
sublinhar sugeriria que o texto do programa mudou.

O título do passo é só marcado, sem o nome por extenso — ele é manchete e
precisa caber numa linha.

### Onde isso mora, e como acrescentar um termo

`server/panel/static/ops/glossario.js`, em duas camadas separadas de propósito:

| Camada | O que é | Traduz? |
|---|---|---|
| `TERMOS` | o nome oficial 3GPP/O-RAN — o que vai entre parênteses | **não** (mesma regra do `static/i18n.js`) |
| `DICTS` | `<termo>.o` = o que é · `<termo>.p` = para que serve | **sim**, nos 4 idiomas |

Para acrescentar: uma linha em `TERMOS` (use `null` se não for sigla a expandir,
como *MySQL* ou *NG Setup*) e as duas explicações nos quatro dicionários.
`npm run test:i18n:parity` reprova termo sem explicação, explicação sem termo e
idioma faltando — um termo que sublinha e abre balão vazio é falha calada, e é
essa que o teste existe para pegar.

Para usar o glossário noutra tela: carregue o script e chame
`Glossario.marcar(elemento)` — ou `Glossario.marcar([{el: titulo, expandir:
false}, legenda])` quando título e legenda dividirem o "uma vez por passo". Ele
só mexe em **nós de texto**: o HTML que já estiver lá passa intacto.
