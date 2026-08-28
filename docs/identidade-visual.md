# Identidade visual — Core5G_ARM64 (v0.74.0)

> **Duas vozes, um sistema.** O laboratório é um *instrumento*; a aula é um
> *texto*. Não devem parecer a mesma coisa nem viver na mesma tela — mas saem da
> mesma paleta, do mesmo ritmo e das mesmas regras de contraste.

Prancha viva: **`/static/design/identidade.html`** (abre nos dois temas).
Arquivo de tokens: **`server/panel/static/tokens.css`** — **gerado**, não se edita
à mão. Geradores em `tools/identidade/`.

---

## Por que existe

Antes disto o painel tinha **225 literais de cor distintos** em 20 arquivos, 114
só em `ops/index.html`, e **186 dos 250 usos escritos direto na regra**, furando
os tokens. Dois azuis significavam a mesma coisa (`#1f6fe5` no lab, `#4d90ff` no
ops) e três nomes diziam "deu certo" (`--good`, `--green`, `#69db7c` solto). Pior:
no `ops/index.html` e no `topology.html` **o tema claro era a única definição
existente** — o escuro era o que sobrava; no lab, o contrário. Os dois lados da
casa foram construídos com regras opostas.

Não era questão de gosto. Era ausência de sistema.

## O método

Cores pensadas em **OKLCH**, não em HSL nem em hex. Em OKLCH o `L` é
perceptualmente uniforme: mexer nele muda o brilho de forma previsível em
qualquer matiz — em HSL, o mesmo `L` em amarelo e em azul dá contrastes
completamente diferentes. É o que Radix e o Tailwind v4 adotaram.

Cada família tem **12 degraus com papel fixo** (convenção Radix):

| degraus | papel |
|---|---|
| 1–2 | fundo da página e da superfície |
| 3–5 | fundo de componente |
| 6–8 | traço |
| 9–10 | sólido (a cor "cheia") |
| 11–12 | texto |

**Claro e escuro não são inversão.** Cada tema tem a sua curva de lightness e de
croma. O escuro parte de `#111112` — preto puro cansa a vista e exagera o
contraste; e no escuro a elevação é **superfície mais clara**, não sombra
(sombra não se enxerga sobre fundo escuro).

## As famílias

| família | hue | papel |
|---|--:|---|
| `n` neutro | 262 | tudo que não é estado. Croma baixo: o cinza é levemente azulado, nunca morto |
| `a` acento | 282 | **a cor do produto** — foco, seleção, ação principal, link. Nunca um estado |
| `g` bom | 150 | no ar, passou |
| `w` atenção | 80 | parcial, perto do limite |
| `r` falha | 27 | fora, erro |

O acento é **azul-violeta**, não o azul-padrão de dashboard. Isso é deliberado:
o azul era usado ao mesmo tempo como "clique aqui" e como "informativo", e essa
colisão é metade da bagunça antiga. Agora ação e informação são a mesma família
(o acento), e o azul de estado deixou de existir.

## Duas camadas de token

```
PRIMITIVA   --n-1..12, --a-*, --g-*, --w-*, --r-*    a cor em si
SEMÂNTICA   --surface, --ink, --line, --accent, ...  o PAPEL da cor
```

**A tela usa só a semântica.** É isso que faz claro e escuro serem coerentes em
vez de duas pinturas independentes: trocar de tema troca a primitiva por baixo,
e nenhuma regra de componente precisa saber disso.

## As medições

Tudo abaixo foi **medido**, não julgado a olho (`tools/identidade/medir_cvd.py`).

### Contraste (WCAG)

| par | claro | escuro | alvo |
|---|--:|--:|--:|
| `--ink` sobre `--surface` | 13,4:1 | 15,6:1 | 4,5 |
| `--ink-2` sobre `--surface` | 5,4:1 | 9,6:1 | 4,5 |
| `--ink-2` sobre `--surface-2` | 5,2:1 | 9,0:1 | 4,5 |
| `--ink-3` sobre `--surface` | 3,3:1 | 5,6:1 | 3,0 |
| texto colorido (degrau 11), pior caso | 5,1:1 | 9,1:1 | 4,5 |
| `--line-strong` sobre `--surface` | 3,4:1 | 3,1:1 | 3,0 |

**Nota sobre `--line-strong`:** no tema claro o degrau 8 mede só **1,94:1** e não
serve como limite de componente (o mínimo é 3:1). Em vez de torcer a rampa, o
papel foi mapeado no degrau que mede: **9 no claro, 8 no escuro**. É exatamente
para isso que a camada semântica existe.

### Daltonismo (ΔE em OKLab ×100, simulação de Viénot)

| par | visão normal | pior dicromacia | |
|---|--:|--:|---|
| verde × vermelho | 30,7 | **9,5** | acima do alvo 8 ✅ |
| verde × âmbar | 21,1 | **7,3** | faixa de piso (6–8) ⚠️ |
| âmbar × vermelho | 26,6 | 17,2 | ✅ |
| acento × qualquer estado | ≥29 | ≥7,3 | ✅ |
| **pior par do conjunto** | **21,1** | **7,3** | |

O par que assusta — verde × vermelho — passa. O par verde × âmbar fica em 7,3 sob
**protanopia**, na faixa que só é legítima **com codificação secundária**.

Tentei resolver por otimização e o resultado foi instrutivo: maximizando ΔE o
buscador entregou um verde quase branco e um vermelho que sumia no fundo escuro.
Estava otimizando a métrica, não a tela. A resposta certa é de projeto, não de
busca:

> ### Regra dura: estado nunca por cor sozinha
> Todo indicador de estado carrega **cor + glifo + palavra**. O ponto de estado
> leva um anel em `--line-strong`, que garante o limite visível mesmo quando o
> preenchimento tem contraste baixo (o âmbar sobre fundo claro mede 2,3:1 — o
> anel resolve). Isto não é enfeite: é o que torna a leitura segura para as ~8%
> de pessoas que não separam verde de vermelho, numa tela projetada para a turma.

## Tipografia — as duas vozes

```
--fonte-instrumento   monoespaçada   o PAINEL
--fonte-texto         sans           a AULA
```

A escolha é do domínio, não de estilo: equipamento de teste rotula tudo em
monoespaçada, e **tabela de resultado precisa de dígito de largura fixa** para
as colunas alinharem. O painel fala em mono — etiquetas em caixa alta,
entreletra `--tr-etiqueta`, denso. A aula fala em sans — medida de ~60
caracteres, entrelinha 1,7, ar.

Escala de tipo em razão 1,25 ancorada em 16px: `--t-micro` a `--t-disp`.

## Ritmo e forma

Espaçamento em **múltiplos de 4** (`--e-1` a `--e-7`). Raios `--r-sm/md/lg/full`.
Traço de 1px em `--traco`.

## A assinatura

O elemento que a marca repete é a **grade de recursos** — a grade tempo ×
frequência de um quadro 5G, o artefato mais característico do rádio. Aparece
literalmente no medidor de PRB (24 células que acendem) e, como motivo, na
moldura com etiqueta encaixada que envolve cada assunto do painel.

## Regras que o arquivo de tokens já impõe

- `.estado-ponto` com anel obrigatório e `data-estado` para a cor.
- `:focus-visible` com anel de 2px e deslocamento — foco sempre visível.
- `prefers-reduced-motion` respeitado globalmente.

## Como regerar

```bash
python3 tools/identidade/escalas.py       # imprime as 5 famílias, 2 temas
python3 tools/identidade/medir_cvd.py     # contraste + separação sob dicromacia
python3 tools/identidade/gerar_tokens.py  # escreve server/panel/static/tokens.css
```

Mudou uma cor? Roda a medição **antes** de aceitar. Nenhuma cor entra no sistema
sem passar pelo contraste e pelo ΔE.

## O que ainda não está feito

Os tokens existem e estão medidos, mas **as telas ainda não os usam** — a
migração dos 225 literais é o próximo passo, junto com a separação entre o
painel de operação e as telas de aula.

## Fontes consultadas

- [OKLCH, explained for designers — UX Collective](https://uxdesign.cc/oklch-explained-for-designers-dc6af4433611)
- [Radix Colors — understanding the 12-step scale](https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale)
- [Color tokens: guide to light and dark modes in design systems](https://medium.com/design-bootcamp/color-tokens-guide-to-light-and-dark-modes-in-design-systems-146ab33023ac)
- [Building a Dark Mode Color Palette: Beyond Inverting Light Mode](https://colorarchive.org/guides/dark-mode-palette-guide/)
- [Mastering Elevation for Dark UI](https://medium.muz.li/mastering-elevation-for-dark-ui-a-comprehensive-guide-04cc770dd0d6)
- [ISO 22324 — cores de código para alerta](https://en.wikipedia.org/wiki/ISO_22324)
- [Color Token Naming Conventions: Primitive, Semantic, and Component Layers](https://colorarchive.org/guides/color-token-naming-guide/)
