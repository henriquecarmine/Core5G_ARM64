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
