# Identidade visual — Core5G_ARM64 (v0.82.0)

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
os tokens. Três nomes diziam "deu certo" (`--good`, `--green`, `#69db7c` solto),
e o acento do painel era **laranja** (`#e8590c`) — vizinho do âmbar de atenção,
duas cores brigando pelo mesmo significado.

Os dois lados da casa foram construídos com **convenções opostas**: o `ops`
declara o tema **escuro** no `:root` e o claro como sobreposição; o lab faz o
contrário. Ambos completos — mas o `ops` não atendia `prefers-color-scheme`, e
nenhuma cor tinha o mesmo nome nos dois lados.

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
| `c` contraponto | 200 | **o segundo acento** — existe porque o Lab de IA opõe duas categorias o tempo todo (supervisionado × não supervisionado), e um par precisa de dois matizes |
| `l` ao vivo | 350 | a aula sendo transmitida. Não é estado da rede nem o acento: é o único momento em que a sala inteira vê a mesma tela |

### A rampa categórica

A topologia distingue **8 domínios de rede** (RAN, core plano de controle, core
plano de usuário, non-RT RIC, O-RAN SC, externo, admin). Ali a cor é
**identidade de domínio, não estado** — por isso sai de rampa própria e nunca do
verde/âmbar/vermelho de sinalização, que naquela tela querem dizer *no ar /
atenção / fora*.

Oito matizes igualmente espaçados (45°) a partir do acento: `--cat-1` a
`--cat-8`. **A ordem é fixa** — categoria nova entra no próximo slot, nunca se
recicla matiz. A atribuição atual segue o matiz que cada domínio já tinha, onde
isso não criava colisão com um estado.

O acento é **azul-violeta**, não o azul-padrão de dashboard. Isso é deliberado:
o azul era usado ao mesmo tempo como "clique aqui" e como "informativo", e essa
colisão é metade da bagunça antiga. Agora ação e informação são a mesma família
(o acento), e o azul de estado deixou de existir.

### A rampa de série de gráfico

A categórica **não serve** para um gráfico de dispersão, e isso foi medido, não
suposto. Na topologia a cor sempre vem acompanhada do **nome da banda escrito
dentro dela** — a cor é reforço, não código. Num gráfico onde cada ponto é
colorido pelo grupo, a cor **é** o código, e aí a conta é outra: a separação
tem de valer para **todos os pares**, inclusive sob protanopia e deuteranopia.

Passando as 70 combinações de 4 dos 8 degraus categóricos pelo validador:
**nenhuma passa**. A melhor (`cat-1·3·5·7`) fica em ΔE 6,9 — abaixo do alvo de
8 — e várias reprovam até para visão normal. A causa é estrutural: os oito
degraus têm a **mesma lightness**, e é exatamente a lightness que sobrevive à
simulação de daltonismo. Oito matizes a 45° com o mesmo brilho viram, para um
dicromata, oito tons do mesmo cinza.

Por isso existe `--serie-1` a `--serie-4`, com **lightness própria por faixa**:

| | matiz | claro | escuro |
|---|---|---|---|
| `--serie-1` | 282° violeta | `#7b74f7` · 3,63:1 | `#8782fe` · 5,63:1 |
| `--serie-2` | 237° azul    | `#046b99` · 5,78:1 | `#0074a6` · 3,43:1 |
| `--serie-3` | 192° teal    | `#019d9a` · 3,28:1 | `#0aa7a4` · 5,99:1 |
| `--serie-4` | 102° oliva   | `#766a03` · 5,38:1 | `#7c7004` · 3,53:1 |

Medido (todos os pares, não só vizinhos): **CVD ΔE 15,1 no claro e 14,3 no
escuro** (alvo ≥8), **visão normal 15,3 e 15,6** (piso 15), **contraste ≥3:1**
contra o cartão em ambos os temas, sem exceção condicional.

Nenhum dos quatro matizes é matiz de estado — bom 150°, atenção 80°, falha 27°,
ao vivo 350° ficam de fora de propósito: uma série nunca pode ser lida como
"esta célula está boa". São **quatro e só quatro**, porque o maior *k* do lab é
4: cor de série não se recicla; um quinto grupo viraria "outros", nunca um
matiz gerado.

O croma de 0,108 nas faixas 2, 3 e 4 não é escolha — é o **teto do sRGB**
naquele par (lightness, matiz).

## Duas camadas de token

```
PRIMITIVA   --n-1..12, --a-*, --g-*, --w-*, --r-*    a cor em si
SEMÂNTICA   --surface, --ink, --line, --accent, ...  o PAPEL da cor
```

**A tela usa só a semântica.** É isso que faz claro e escuro serem coerentes em
vez de duas pinturas independentes: trocar de tema troca a primitiva por baixo,
e nenhuma regra de componente precisa saber disso.

## As medições

Colorimetria a serviço da **programação visual**: nenhuma cor entra no sistema
sem passar pelo contraste.

Tudo abaixo foi **medido**, não julgado a olho (`tools/identidade/medir.py`).

### Contraste (WCAG)

| par | claro | escuro | alvo |
|---|--:|--:|--:|
| `--ink` sobre `--surface` | 13,4:1 | 15,6:1 | 4,5 |
| `--ink-2` sobre `--surface` | 5,4:1 | 9,6:1 | 4,5 |
| `--ink-2` sobre `--surface-2` | 5,2:1 | 9,0:1 | 4,5 |
| `--ink-3` sobre `--surface` | 3,3:1 | 5,6:1 | 3,0 |
| texto colorido (degrau 11), pior caso | 5,1:1 | 9,1:1 | 4,5 |
| `--line-strong` sobre `--surface` | 3,4:1 | 3,1:1 | 3,0 |

**O anel do ponto de estado.** O âmbar sobre fundo claro mede **2,0:1** — é a
natureza do âmbar sobre branco, não um erro de escolha. Por isso `.estado-ponto`
carrega um anel em `--line-strong`: é ele que desenha o limite quando o
preenchimento não tem contraste para isso sozinho.

**Nota sobre `--line-strong`:** no tema claro o degrau 8 mede só **1,94:1** e não
serve como limite de componente (o mínimo é 3:1). Em vez de torcer a rampa, o
papel foi mapeado no degrau que mede: **9 no claro, 8 no escuro**. É exatamente
para isso que a camada semântica existe.

### Adaptação para daltonismo — fora do escopo

A paleta segue a **tabela normal** de sinalização: verde, âmbar e vermelho como
se espera que sejam, cada um na lightness em que *parece* a cor padrão. Não
distorcemos as cores para maximizar separação sob dicromacia — quando isso foi
tentado, o resultado foi um verde quase branco e um vermelho que sumia no fundo
escuro: otimizava a métrica, não a tela.

Adaptação para daltonismo é **estudo à parte**, para depois, e se aplica como
**função sobre esta tabela** (filtro de paleta), não redesenhando a paleta.

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
python3 tools/identidade/paleta.py        # imprime as 5 famílias nos 2 temas
python3 tools/identidade/medir.py         # contraste WCAG — sai != 0 se reprovar
python3 tools/identidade/gerar_tokens.py  # escreve server/panel/static/tokens.css
```

`paleta.py` é a receita: matiz, curva de lightness e croma. `oklch.py` é a
matemática. Mudou uma cor? Roda `medir.py` **antes** de aceitar — ele reprova
com código de saída != 0, então serve de porta em CI.

## Onde as telas estão

| | literais de cor |
|---|--:|
| `ops/index.html` | 250 → **4** (o scrim de cada tema e dois ANSI sem par) |
| 11 páginas do lab | 26 blocos de paleta → **0** (ponte única em `lab/lab-ponte.css`) |
| `login.html` | 24 → **1** |
| `ops/topology.html` | 66 → **26** (o resto vive no JS de desenho) |

As 12 páginas do lab foram fechadas na **v0.82.0**: dos 174 literais que havia,
sobraram **77**, todos no **relatório exportado** — o HTML que o aluno baixa e
abre no Word, onde não existe `var(--ink)` para resolver nem tema escuro, e por
isso as cores lá **têm de ser literais**. Estão marcadas com um comentário
dizendo isso, para ninguém "consertar" depois.

**Falta**: os arquivos JS que desenham (`flow-strip.js`, `energy.js`,
`mini-map.js`, `i18n.js`).

## O que os testes garantem

- `node test/paginas.js` — toda página HTML tem `<meta charset>` **no primeiro
  kilobyte** (o navegador não lê além disso) e carrega a identidade se pinta
  alguma coisa. Este teste nasceu de duas quebras reais: três páginas sem a
  etiqueta, e sete com a *palavra* "charset" enterrada num script, onde um
  `grep -L charset` deu falso-negativo. Por isso ele mede **posição**, não
  presença.
- `test/visual-smoke.js` 0.b — a folha de identidade carregou de verdade.
- `test/visual-smoke.js` 0.c — o console é legível **nos dois temas**, texto e
  cores de log, com piso de 4,5:1.
- `tools/identidade/medir.py` — contraste de todo par prometido, **inclusive as
  4 faixas da rampa de série** contra o cartão nos dois temas; sai com código
  != 0 quando reprova.
- `node test/paginas.js` — quem tem **botão de tema** lê e grava `c5g-theme`.
  As 12 páginas do lab tinham o botão e nenhuma gravava: o professor punha o
  tema claro para o projetor, entrava numa aula e voltava tudo escuro. Como o
  botão funcionava, não parecia defeito — parecia teimosia da tela.

## Fontes consultadas

- [OKLCH, explained for designers — UX Collective](https://uxdesign.cc/oklch-explained-for-designers-dc6af4433611)
- [Radix Colors — understanding the 12-step scale](https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale)
- [Color tokens: guide to light and dark modes in design systems](https://medium.com/design-bootcamp/color-tokens-guide-to-light-and-dark-modes-in-design-systems-146ab33023ac)
- [Building a Dark Mode Color Palette: Beyond Inverting Light Mode](https://colorarchive.org/guides/dark-mode-palette-guide/)
- [Mastering Elevation for Dark UI](https://medium.muz.li/mastering-elevation-for-dark-ui-a-comprehensive-guide-04cc770dd0d6)
- [Color Token Naming Conventions: Primitive, Semantic, and Component Layers](https://colorarchive.org/guides/color-token-naming-guide/)
