#!/usr/bin/env node
/*
 * Teste de fumaça VISUAL da TOPOLOGIA (server/panel/static/topology.html).
 *
 * Renderiza a página nos dois projetos (?proj=p2 e ?proj=p1) num Chrome
 * headless, stubando o fetch de /api/topology com os JSONs reais de
 * static/ — sem servidor nem login. Valida:
 *   - render sem pageerror;
 *   - 3 bandas CUPS (RAN, Plano de Controle, Plano de Usuário);
 *   - rótulos didáticos N1 e N11/Nsmf presentes (links e legenda);
 *   - links paralelos entre os mesmos nós (N1/N2 no P1) com offset;
 *   - os 4 modos de visualização e o tour re-renderizam sem erro.
 * Gera screenshots/topology-p2.png e screenshots/topology-p1.png.
 *
 * Uso:  cd server/panel/test && npm install && npm run test:topo
 *       CHROME_PATH=/usr/bin/chromium npm run test:topo
 */
const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

const STATIC = path.resolve(__dirname, '..', 'static');
const PAGE = 'file://' + path.join(STATIC, 'topology.html');
const SHOTS = path.resolve(__dirname, 'screenshots');
const P2 = fs.readFileSync(path.join(STATIC, 'openran-topology.json'), 'utf8');
const P1 = fs.readFileSync(path.join(STATIC, 'openran-topology-p1.json'), 'utf8');

function findChrome() {
  const candidates = [
    process.env.CHROME_PATH,
    '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium', '/usr/bin/chromium-browser',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ].filter(Boolean);
  for (const c of candidates) { try { if (fs.existsSync(c)) return c; } catch {} }
  throw new Error('Chrome não encontrado. Defina CHROME_PATH=/caminho/do/chrome');
}

const assert = (cond, msg) => { if (!cond) throw new Error('FALHOU: ' + msg); };

(async () => {
  fs.mkdirSync(SHOTS, { recursive: true });
  const browser = await puppeteer.launch({
    executablePath: findChrome(),
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--force-color-profile=srgb'],
  });

  for (const proj of ['p2', 'p1']) {
    const page = await browser.newPage();
    await page.setViewport({ width: 1480, height: 980, deviceScaleFactor: 2 });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.evaluateOnNewDocument((p1, p2) => {
      try { localStorage.setItem('c5g-theme', 'dark'); } catch {}  // tema inicial determinístico
      window.fetch = async (url) => {
        url = String(url);
        const j = (o, s = 200) => new Response(typeof o === 'string' ? o : JSON.stringify(o), { status: s, headers: { 'Content-Type': 'application/json' } });
        if (url.includes('/api/topology/logs')) return j({ sections: [] });
        if (url.includes('/api/topology/gnb-stats')) return j({ up: false });
        if (url.includes('/api/topology')) return j(url.includes('proj=p1') ? p1 : p2);
        return j({});
      };
    }, P1, P2);
    await page.goto(PAGE + '?proj=' + proj, { waitUntil: 'domcontentloaded' });
    await new Promise(r => setTimeout(r, 500));

    assert(errors.length === 0, `pageerror em ${proj}: ${errors.join(' | ')}`);

    const d = await page.evaluate(() => ({
      bands: document.querySelectorAll('.band').length,
      bandLabels: [...document.querySelectorAll('.band-label')].map(t => t.textContent),
      labels: [...document.querySelectorAll('.link-label')].map(t => t.textContent),
      links: document.querySelectorAll('.link').length,
      nodes: document.querySelectorAll('.node').length,
      legend: document.getElementById('legend').textContent,
    }));
    assert(d.bands === 3, `${proj}: esperava 3 bandas CUPS, veio ${d.bands}`);
    assert(d.bandLabels.some(l => l.includes('PLANO DE CONTROLE')), `${proj}: banda plano de controle`);
    assert(d.bandLabels.some(l => l.includes('PLANO DE USUÁRIO')), `${proj}: banda plano de usuário`);
    assert(d.labels.includes('N1'), `${proj}: rótulo N1 presente`);
    assert(d.labels.includes('N11/Nsmf'), `${proj}: rótulo N11/Nsmf presente`);
    assert(d.legend.includes('N11/Nsmf'), `${proj}: legenda com N11/Nsmf`);
    console.log(`PASS ${proj} · ${d.nodes} nós, ${d.links} links, bandas: ${d.bandLabels.join(' | ')}`);

    if (proj === 'p1') {
      // N1 e N2 entre os mesmos nós: os dois paths devem estar deslocados (offset)
      const dd = await page.evaluate(() => [...document.querySelectorAll('.link')].map(p => p.getAttribute('d')));
      assert(new Set(dd).size === dd.length, 'p1: dois links paralelos com o mesmo path (offset não aplicado)');
      console.log('PASS p1 · links paralelos N1/N2 com offset');
    }

    for (const m of ['simplificado', 'fluxo', 'troubleshooting', 'tecnico']) {
      await page.click(`.modes button[data-mode="${m}"]`);
      await new Promise(r => setTimeout(r, 120));
    }
    assert(errors.length === 0, `${proj}: pageerror nos modos: ${errors.join(' | ')}`);
    console.log(`PASS ${proj} · 4 modos re-renderizam sem erro`);

    await page.click('#tour-btn');
    for (let i = 0; i < 5; i++) await page.click('#tour-next');
    assert(errors.length === 0, `${proj}: pageerror no tour: ${errors.join(' | ')}`);
    await page.click('#tour-exit');
    console.log(`PASS ${proj} · tour (5 camadas) sem erro`);

    await new Promise(r => setTimeout(r, 200));
    await page.screenshot({ path: path.join(SHOTS, `topology-${proj}.png`) });
    console.log(`  screenshot: screenshots/topology-${proj}.png`);

    // tema claro: alterna, persiste e re-renderiza sem erro
    await page.click('#theme-btn');
    await new Promise(r => setTimeout(r, 150));
    const th = await page.evaluate(() => ({
      attr: document.documentElement.dataset.theme,
      saved: localStorage.getItem('c5g-theme'),
      links: document.querySelectorAll('.link').length,
    }));
    assert(th.attr === 'light' && th.saved === 'light', `${proj}: toggle de tema não aplicou/persistiu`);
    assert(th.links > 0, `${proj}: diagrama sumiu após trocar o tema`);
    assert(errors.length === 0, `${proj}: pageerror no toggle de tema: ${errors.join(' | ')}`);
    console.log(`PASS ${proj} · tema claro aplicado e re-renderizado`);
    await page.screenshot({ path: path.join(SHOTS, `topology-${proj}-light.png`) });
    console.log(`  screenshot: screenshots/topology-${proj}-light.png`);
    await page.close();
  }

  await browser.close();
  console.log('✅ SMOKE DA TOPOLOGIA PASSOU (p2 + p1)');
})().catch(e => { console.error(e.message); process.exit(1); });
