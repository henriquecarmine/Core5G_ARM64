#!/usr/bin/env node
/*
 * Fumaça das 12 páginas do Lab, nos DOIS temas.
 *
 * Três coisas que já quebraram calado e por isso são medidas aqui:
 *
 * 1) TEMA LEMBRADO. Nenhuma das 12 gravava a escolha: o professor punha o tema
 *    claro para o projetor, entrava numa aula e voltava tudo escuro. Como o
 *    botão funcionava, não parecia defeito. (O `paginas.js` pega a ausência do
 *    código; aqui se confere que o tema REALMENTE se aplica na tela.)
 *
 * 2) GLOSSÁRIO COM CONTEÚDO. Um termo sublinhado cujo balão abre vazio é falha
 *    calada — a página parece certa. Aqui todo termo marcado tem de ter
 *    "o que é" e "para que serve".
 *
 * 3) GLOSSÁRIO FORA DO CÓDIGO. Dentro de <code>/<pre> a sigla é literal, não
 *    vocabulário: sublinhar ali sugere que o texto do programa mudou.
 *
 * Uso: node labs.js   (ou via npm run test:labs)
 */
const puppeteer = require('puppeteer-core');
const { subir } = require('./servidor');
const fs = require('fs');
const path = require('path');

const DIR = path.resolve(__dirname, '..', 'static', 'lab');
const PAGS = fs.readdirSync(DIR).filter((f) => /^lab-.*\.html$/.test(f)).sort();

function findChrome() {
  const c = [process.env.CHROME_PATH, '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium', '/usr/bin/chromium-browser'].filter(Boolean);
  for (const x of c) { try { if (fs.existsSync(x)) return x; } catch {} }
  throw new Error('Chrome não encontrado. Defina CHROME_PATH=/caminho/do/chrome');
}

(async () => {
  const srv = await subir();
  const browser = await puppeteer.launch({ executablePath: findChrome(), headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--force-color-profile=srgb'] });
  const erros = [];
  let marcadosTotal = 0;

  for (const arq of PAGS) {
    for (const tema of ['dark', 'light']) {
      const page = await browser.newPage();
      await page.setViewport({ width: 1400, height: 1000 });
      const js = [];
      page.on('pageerror', (e) => js.push(e.message.slice(0, 120)));
      await page.evaluateOnNewDocument((t) => {
        try { localStorage.setItem('c5g-theme', t); localStorage.setItem('c5g-lang', 'pt'); } catch (e) {}
      }, tema);
      await page.goto(srv.url('/static/lab/' + arq), { waitUntil: 'networkidle2' }).catch(() => {});
      await new Promise((r) => setTimeout(r, 700));

      const d = await page.evaluate(() => ({
        tema: document.documentElement.dataset.theme,
        temGlossario: !!window.Glossario,
        marcados: document.querySelectorAll('.glos-termo').length,
        emCodigo: document.querySelectorAll('code .glos-termo, pre .glos-termo, .mcode .glos-termo, .readout .glos-termo').length,
        vazios: [...new Set([...document.querySelectorAll('.glos-termo')]
          .map((e) => e.getAttribute('data-termo'))
          .filter((t) => { const g = window.Glossario && window.Glossario.explica(t); return !g || !g.o || !g.p; }))],
        // o mesmo termo não pode se apresentar duas vezes na mesma página
        repetidos: (() => {
          const c = {};
          for (const e of document.querySelectorAll('.glos-exp')) {
            const t = e.previousElementSibling && e.previousElementSibling.getAttribute('data-termo');
            if (t) c[t] = (c[t] || 0) + 1;
          }
          return Object.entries(c).filter(([, n]) => n > 1).map(([t, n]) => `${t}×${n}`);
        })(),
      }));

      const onde = `${arq} · ${tema}`;
      if (js.length) erros.push(`${onde}: erro de execução — ${js[0]}`);
      if (d.tema !== tema) erros.push(`${onde}: tema não aplicou (veio '${d.tema}')`);
      if (!d.temGlossario) erros.push(`${onde}: glossario.js não carregou`);
      if (!d.marcados) erros.push(`${onde}: nenhuma sigla marcada`);
      if (d.emCodigo) erros.push(`${onde}: ${d.emCodigo} termo(s) marcados DENTRO de código`);
      if (d.vazios.length) erros.push(`${onde}: termo sem explicação — ${d.vazios.join(', ')}`);
      if (d.repetidos.length) erros.push(`${onde}: nome por extenso repetido — ${d.repetidos.join(', ')}`);
      if (tema === 'dark') marcadosTotal += d.marcados;
      await page.close();
    }
  }

  await browser.close();
  await srv.fechar();

  if (erros.length) {
    console.error(`✗ LAB REPROVADO (${erros.length}):`);
    erros.slice(0, 20).forEach((e) => console.error('  -', e));
    process.exit(1);
  }
  console.log(`✅ ${PAGS.length} páginas do lab × 2 temas — sem erro, tema aplicado, ${marcadosTotal} siglas marcadas (nenhuma dentro de código, nenhuma sem explicação, nenhuma repetida)`);
})().catch((e) => { console.error(e); process.exit(1); });
