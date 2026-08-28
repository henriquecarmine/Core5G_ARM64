#!/usr/bin/env node
/*
 * Teste de fumaça VISUAL da TOPOLOGIA (server/panel/static/topology.html).
 *
 * Renderiza a página nos dois projetos (?proj=p2 e ?proj=p1) num Chrome
 * headless, stubando o fetch de /api/topology com os JSONs reais de
 * static/ — sem servidor nem login. Valida:
 *   - render sem pageerror;
 *   - bandas: P1=3 (RAN/CP/UP) · P2=5 (+ Non-RT RIC e near-RT O-RAN SC);
 *   - rótulos didáticos N1 e N11/Nsmf presentes (links e legenda);
 *   - links paralelos entre os mesmos nós (N1/N2 no P1) com offset;
 *   - os 4 modos de visualização e o tour re-renderizam sem erro.
 * Gera screenshots/topology-p2.png e screenshots/topology-p1.png.
 *
 * Uso:  cd server/panel/test && npm install && npm run test:topo
 *       CHROME_PATH=/usr/bin/chromium npm run test:topo
 */
const puppeteer = require('puppeteer-core');
const { subir } = require('./servidor');
const path = require('path');
const fs = require('fs');

const STATIC = path.resolve(__dirname, '..', 'static', 'ops');
const CAMINHO = '/static/ops/topology.html';   // servido por HTTP: ver servidor.js
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
  const srv = await subir();
  const PAGE = srv.url(CAMINHO);
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
      try { localStorage.setItem('c5g-theme', 'dark'); localStorage.setItem('c5g-lang', 'pt'); } catch {}  // tema/idioma iniciais determinísticos
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
    // P1: 3 bandas (RAN, CP, UP) · P2: 5 (+ Non-RT âmbar e O-RAN SC rosa, v0.53+)
    const wantBands = proj === 'p2' ? 5 : 3;
    assert(d.bands === wantBands, `${proj}: esperava ${wantBands} bandas, veio ${d.bands}`);
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

    // Jornada do UE (só P2): percorre as 15 etapas seguindo o pacote, sem erro
    if (proj === 'p2') {
      await page.click('#journey-btn');
      const jtotal = await page.evaluate(() => Number(document.getElementById('tour-step').textContent.split('/')[1]));
      assert(jtotal === 17, `p2: jornada esperava 17 etapas (16 + a1real v0.56), veio ${jtotal}`);
      for (let i = 0; i < jtotal - 1; i++) await page.click('#tour-next');
      assert(errors.length === 0, `p2: pageerror na jornada: ${errors.join(' | ')}`);
      await page.click('#tour-exit');
      console.log(`PASS p2 · Jornada do UE (${jtotal} etapas) sem erro`);
    } else {
      await page.click('#journey-btn');
      const jtotal = await page.evaluate(() => Number(document.getElementById('tour-step').textContent.split('/')[1]));
      assert(jtotal === 13, `p1: jornada esperava 13 etapas, veio ${jtotal}`);
      for (let i = 0; i < jtotal - 1; i++) await page.click('#tour-next');
      assert(errors.length === 0, `p1: pageerror na jornada: ${errors.join(' | ')}`);
      await page.click('#tour-exit');
      console.log(`PASS p1 · Jornada do UE (${jtotal} etapas · com failover de UPF) sem erro`);
    }

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

    // idioma: troca para FR → chrome, hint, legenda e textos didáticos (via tt) em francês
    await page.click('#lang-menu .lang-btn');            // abre o seletor com bandeira
    await page.click('#lang-menu li[data-lang="fr"]');   // escolhe francês
    await new Promise(r => setTimeout(r, 200));
    const fr = await page.evaluate(() => ({
      hint: document.getElementById('mode-hint').textContent,
      legend: document.getElementById('legend').textContent,
      roles: [...document.querySelectorAll('.node .role')].map(t => t.textContent),
      title: document.getElementById('topo-proj').textContent,
    }));
    assert(fr.hint.includes('Vue technique'), `${proj}/fr: hint = "${fr.hint}"`);
    assert(fr.legend.includes('Couches'), `${proj}/fr: legenda sem "Couches"`);
    assert(fr.roles.some(r => r === 'Mobilité'), `${proj}/fr: papel do AMF não traduzido (${fr.roles.join(',')})`);
    assert(fr.title.includes(proj === 'p1' ? 'Projet 1' : 'Projet 2'), `${proj}/fr: título = "${fr.title}"`);
    await page.click('#tour-btn');
    const tourT = await page.evaluate(() => document.getElementById('tour-title').textContent);
    assert(tourT.includes('Couche 1'), `${proj}/fr: tour = "${tourT}"`);
    await page.click('#tour-exit');
    assert(errors.length === 0, `${proj}/fr: pageerror: ${errors.join(' | ')}`);
    console.log(`PASS ${proj} · topologia em francês (chrome + nós + tour)`);
    await page.close();
  }

  await browser.close();

  await srv.fechar();
  console.log('✅ SMOKE DA TOPOLOGIA PASSOU (p2 + p1)');
})().catch(e => { console.error(e.message); process.exit(1); });
