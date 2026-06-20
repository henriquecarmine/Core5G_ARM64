# Teste de fumaça visual do painel

Valida o componente de **loader** do painel (`server/panel/static/index.html`) —
a barra de progresso global no topo, o spinner por botão e o estado `loading`
dos toggles — renderizando o HTML num **Chrome headless** (sem precisar de
servidor nem login).

## Pré-requisitos
- Node 18+
- Google Chrome **ou** Chromium instalado (o teste acha sozinho; se estiver
  noutro caminho, use `CHROME_PATH`).

## Rodar
```bash
cd server/panel/test
npm install        # instala puppeteer-core (usa o Chrome do sistema)
npm test
```

Saída esperada: `PASS 0` … `PASS 7` + `✅ TODOS OS TESTES PASSARAM`.
Gera um screenshot em `screenshots/loaders.png` para inspeção.

`CHROME_PATH=/usr/bin/chromium npm test` se o navegador estiver em outro lugar.

## O que cada passo cobre
| Passo | Verifica |
|-------|----------|
| 0 | `loaderInc/Dec/btnLoading/withLoader` e `#top-loader` existem |
| 1 | Em repouso a barra está apagada |
| 2 | Uma ação acende a barra global + spinner no botão |
| 3 | Ao terminar, barra e spinner somem |
| 4 | Toggle entra no estado `loading` |
| 5 | Ref-count (2 inc / 2 dec) não deixa a barra presa |
| 6 | `withLoader` limpa tudo **mesmo quando a ação lança erro** |
| 7 | 7 ciclos seguidos sempre voltam ao repouso |

> Não dispara comandos no servidor — injeta o estado do loader via JS e inspeciona
> o DOM/CSS. Seguro para rodar em qualquer máquina.
