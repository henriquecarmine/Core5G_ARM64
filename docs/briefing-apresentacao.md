# Briefing da apresentação — Grupo 6, Tema 1 (UE-TP)

> Escrito na madrugada de 29/08 para a apresentação de **30/08**. É o que
> precisa estar na cabeça antes de entrar. O roteiro completo está no PDF
> `ROTEIRO_APRESENTACAO.pdf`; isto aqui é o que **não** está lá.

---

## ⚠ O que NÃO vem pelo git

`pdfs/03-dados-telecom/projeto/entrega/` está no `.gitignore`. Então **os três
arquivos da apresentação não viajam com o `git pull`**:

- `ROTEIRO_APRESENTACAO.pdf`
- `RELATORIO_CP2.pdf` ← o plano B se a rede cair
- `grupo-6-checkpoint-2.zip` ← o pacote da entrega

Eles estão na **Área de trabalho da estação antiga**. Duas saídas:

**1. Levar na mão** (pendrive, nuvem, e-mail para si mesmo). É o caminho seguro.

**2. Regerar na estação nova** — precisa de pandas e matplotlib:

```bash
cd pdfs/03-dados-telecom/projeto
python3 -m venv /tmp/venv && /tmp/venv/bin/pip install pandas matplotlib
/tmp/venv/bin/python build_relatorio_cp2.py   # relatório + zip + cópia na Área de trabalho
/tmp/venv/bin/python roteiro_apresentacao.py  # roteiro + cópia na Área de trabalho
```

Os dois scripts copiam o PDF para a Área de trabalho sozinhos. Precisa também de
`google-chrome` ou `chromium` no PATH — é ele que imprime o PDF.

---

## O estado do sistema, conferido ao vivo

**Painel v0.84.0, no ar.** `https://core5g-arm64.duckdns.org`

| | |
|---|---|
| Percurso login → última tela | **20,5 s**, zero erro |
| T1 do clique ao veredito | **1,8 s** |
| Contêineres | 13 de 15 no ar |
| Rádio | SNR 51,0 dB · MCS 28 · PRB 5/51 · BLER 0,0 |
| Carga | ~8 em 4 vCPU · CPU 77% · swap 0 |
| Suítes de teste | 8 de 8 verdes |

Os 2 contêineres fora são `ric_a1mediator` e `ric_dbaas` — a Fase 2 do O-RAN SC,
que a própria topologia rotula "em curso". **Não é falha**, é o que você conta.

Conferido: 19 de 19 instruções de tela do roteiro existem e respondem.

---

## As duas armadilhas

**1. Há três botões com ▶ visíveis ao mesmo tempo.** O que roda o teste é
**"▶ Iniciar teste"**, o verde **dentro** da caixa do pré-voo. Os outros dois
("Rodar teste selecionado" e "Os 7 temas lado a lado") ficam no menu, atrás do
modal — clicar neles não faz nada e o silêncio parece travamento.

**2. Nunca clique em "Os 7 temas lado a lado".** Ele roda os sete.

---

## Os números na mão — recalculados do banco silver

| | repouso | carga |
|---|---|---|
| Vazão mediana (kbps) | 3,7 | 80.023,7 |
| Ocupação do rádio (%) | 2,0 | 97,3 |
| Atraso mediano (µs) | 0,0 | 158,9 |
| Tempo acima de 100 µs | 25% | 100% |
| Amostras | 20 | 60 |

Todos batem com o dado. Também conferidos: **11 das 20** amostras do repouso com
atraso zero, as demais chegando a **218 µs**; o pico isolado de **172.317 kbps**
na recuperação puxando a média para **8.619** (mediana 3,7); correlação global
vazão×atraso **0,484**, e dentro da fase 0,11 / 0,16 / −0,08.

---

## O que foi corrigido na véspera — e por quê

Duas afirmações não batiam com os dados. As duas estão corrigidas no relatório,
no `kpis_cp2.md` e no roteiro.

**1. O limite de 186 µs.** O texto dizia *"acima de 186 o indicador se inverte,
porque o p95 do repouso ultrapassa o da carga"*. Media-se: p95 do repouso
**185,7 µs**, p95 da carga **191,2 µs** — o do repouso fica **abaixo**. A frase
se contradizia com os dois números impressos ao lado.

A versão certa: a separação é máxima num **patamar de 95 a 133 µs** (75 pontos),
resiste até ~157, chega a **zero em 179** e só **inverte em 198**. O número 186
continua certo de citar, por outra razão: **é o p95 do próprio repouso** —
passado o quase-pior caso da rede parada, as duas fases medem quase o mesmo.

**2. "Biblioteca padrão" e "dois comandos".** O ETL (`etl/build_lake.py`) é
stdlib puro. A análise (`cp2_indicadores.py`) usa pandas, matplotlib e numpy, e
o `requirements.txt` diz isso. São **três** comandos, com o `pip install` na
frente.

Se o professor perguntar por que reenviou: nenhum número, tabela, figura,
conclusão ou recomendação mudou — só a explicação de por que o limite existe.

---

## Dois detalhes que não estão escritos em lugar nenhum

- **A numeração das amostras reinicia por fase** (0..19, 0..59, 0..19). A chave
  real é `(run_id, phase, sample_index)`. "Sem buracos" é verdade **dentro de
  cada fase** — olhando `sample_index` sozinho, ele repete 40 vezes. A defesa do
  bloco 2 pergunta exatamente isso.
- O `decision.json` traz `actuation.mode = "emulate"`. Se perguntarem por
  dry-run, o campo se chama **emulate**.

---

## A quarta pergunta do bloco 5 — RESPONDIDA

> **Qual seria a política A1 se a regra tivesse disparado?**

**A resposta curta:** ela já está escrita no nosso código e nunca foi emitida
porque a regra não disparou. Está em `scripts/temas/temas_projeto.py`, na função
`a1_dryrun`, chamada no ramo `if fr > 0` do tema 1:

```json
{
  "policy_id": "ue-tp-prioridade-candidata",
  "policytype_id": "1",
  "ric_id": "ric-oran",
  "service_id": "analise-dados-rapp",
  "actuation": { "mode": "emulate" },
  "policy_data": {
    "scope":         { "ueId": "ue-any", "qosId": "qos-lab" },
    "qosObjectives": { "priorityLevel": 10 }
  },
  "lab_context": { "motivo": "vazão baixa com rádio cheio: usuário mal servido" }
}
```

**O que ela pede, em uma frase:** eleve a prioridade de escalonamento daquele UE
naquele QoS. Não é reserva de PRB — o schema do **tipo 1** (`OSC_Type1_1.0.0`,
`testdata/policy_type.json`) só tem `scope {ueId, qosId}` e
`qosObjectives {priorityLevel}`. É a única alavanca que o tipo dá.

**Por que `priorityLevel: 10`:** é o valor do próprio artefato do professor
(`decision.json` → `policy_data.qosObjectives.priorityLevel = 10`). Não foi
calibrado por nós — e é honesto dizer isso.

**Por onde ela desceria:** rApp no Non-RT (PMS, `:8081`) →
`PUT /a1-p/policytypes/1/policies/{id}` → **A1** → near-RT → gNB. Detalhe que
vale ponto: na Fase 1 o FlexRIC **não termina A1**; quem termina é o
`ric_a1mediator` da Fase 2 — exatamente os dois contêineres que a topologia
rotula "em curso".

**Em dry-run:** `actuation.mode = "emulate"`, o mesmo campo do `decision.json`.
Nada é aplicado na RAN; o efeito seria emulado com `tc tbf` no `oaitun` e medido
no `effect_report.json` (Δ médio before→after nas três features).

**O que ela NÃO pode pedir:** cota de PRB ou escalonamento de slice. Isso seria
E2SM-RC action 6, que o próprio slide do professor lista em "não afirmar".

**E o fecho honesto:** com **um único UE**, priorizar "ue-any" não tem contra
quem competir. A política faz sentido como mecanismo demonstrado, não como
ganho medido — que é a mesma humildade do resto do trabalho.

---

## ⚠ A INSTÂNCIA INTEIRA ESTÁ DESLIGADA

Não é só o laboratório: a **máquina EC2 foi parada** no fim do dia 29/08. E o
IAM `core5g-ops` **não tem** `ec2:StartInstances` — dá `UnauthorizedOperation`.
Então o primeiro passo é humano, **pelo console da AWS**. Sem isso, o domínio
não responde e nada mais nesta lista funciona.

## A ordem de partida, na sequência certa

1. **Ligar a instância no console da AWS.** ~1 min até o painel responder.
2. **Deployar ANTES de qualquer pessoa entrar** — há três coisas na fila e o
   deploy reinicia o serviço:
   ```bash
   ./deploy.sh panel      # v0.85.5: trava de ocupação, fuso, 5 exercícios nossos
   ```
   Fazer isto com o painel vazio é o ponto inteiro: em 29/08 o deploy caiu às
   15:28, dois minutos antes da aula do professor, e ele levou oito tentativas
   de login em treze minutos. A partir da v0.85.4 o próprio `deploy.sh` recusa
   se houver gente conectada (`FORCA=1` passa por cima).
3. **Ligar o Projeto 2 no ⏻** — leva 1 a 2 min: 13 contêineres, gNB/UE/RIC
   vivos, E2 em SCTP ESTAB, rádio com SNR ~50 dB e MCS 28.
   **Só 10 minutos antes**: a instância é `t4g.xlarge`, *burstable* — o lab a
   ~77% de CPU queima crédito e o baseline é 40%. Deixar rodando entrega uma
   máquina lenta bem na hora da demo.
4. **Ctrl+Shift+R** — obrigatório, o `?v=` muda a cada versão.
5. Conferir a régua: **três bolinhas verdes** e o quadrante **RÁDIO · E2 com
   números**. Sem número no rádio, o gNB não subiu.
3. Conferir na régua: **três bolinhas verdes** (Core, E2 lab, Non-RT) e o
   quadrante **RÁDIO·E2 com números**. Sem número no rádio, o gNB não subiu.
4. Rodar o T1 uma vez para aquecer e clicar em **limpar**.
5. Deixar o `RELATORIO_CP2.pdf` aberto noutra aba.

## Novidade que apareceu na madrugada

**As siglas se explicam sozinhas na tela.** Passe o mouse em qualquer sigla —
na Jornada do UE, nos rótulos do diagrama da topologia (N4, E2, Nausf…), nas
aulas e nos labs. Abre um balão com "o que é" e "para que serve". São 128
termos, em quatro idiomas.

Serve para a apresentação: se alguém perguntar o que é PRB ou E2SM-KPM no meio
da tela, dá para mostrar em vez de explicar.
