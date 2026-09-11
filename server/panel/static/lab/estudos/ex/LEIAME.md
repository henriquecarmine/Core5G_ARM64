# Exercícios — os nossos

Um arquivo por exercício, nomeado pelo hash sem `#` e com `/` virando `-`:
`#data/aula01` → `ex/data-aula01.json`.

O catálogo (`../index.json`) continua sendo a fonte da lista, dos pontos e do
`partes`. Aqui ficam só as **perguntas**.

## Formato

```jsonc
{
  "h": "#data/aula01",           // tem de bater com o catálogo
  "rot": "Aula 01",
  "t": "DIKW, mapas e fontes",
  "pts": 22,                     // tem de bater com `pts` do catálogo
  "fonte": "de onde saiu o conteúdo — para o aluno poder voltar",
  "blocos": [
    { "nome": "Conceitos", "tipo": "escolha", "qs": [
        { "q": "enunciado",
          "alt": ["…", "…", "…", "…"],
          "ok": 2,               // índice da correta (base 0)
          "pts": 1,
          "porque": "por que essa e não as outras — aparece DEPOIS de responder" } ] },

    { "nome": "Sequência", "tipo": "ordem", "qs": [
        { "q": "enunciado",
          "itens": ["1º", "2º", "3º"],   // NA ORDEM CERTA; a tela embaralha
          "pts": 10,
          "porque": "…" } ] },

    { "nome": "Comparação", "tipo": "associar", "qs": [
        { "q": "Classifique cada característica.",
          "alvos": ["RAN tradicional", "vRAN", "O-RAN"],   // as opções do menu de cada item
          "itens": [
            { "t": "Hardware proprietário integrado", "ok": [0] },
            { "t": "Hardware COTS", "ok": [1, 2] }        // mais de um alvo aceito
          ],
          "pts": 10,
          "porque": "…" } ] }
  ]
}
```

## Regras

- **A soma dos `pts` das perguntas tem de dar o `pts` do exercício.** O teste
  `test:exercicios` reprova se não der — e o total gravado por aluno vem do
  catálogo, não do navegador, então uma soma errada viraria nota errada.
- `porque` é **obrigatório**. Um exercício que só diz "errou" não ensina; a
  diferença entre isto e a plataforma antiga do professor (que saiu do ar) é
  justamente a explicação.
- Em `ordem`, os `itens` são escritos **na ordem certa** e a tela embaralha.
  A correção dá **crédito parcial**: pontos proporcionais às posições certas.
- Em `associar`, cada item escolhe um alvo num menu; `ok` é a **lista** de
  alvos aceitos (um item pode valer em mais de uma coluna). A tela sorteia a
  ordem dos itens, então nunca alinhe itens e alvos de propósito. Crédito
  parcial: pontos proporcionais aos itens certos. O teste reprova item sem alvo
  válido e pergunta em que todo item aceita todo alvo.
- Conteúdo em **português**, como o resto dos Estudos. O glossário cuida das
  siglas na tela.
