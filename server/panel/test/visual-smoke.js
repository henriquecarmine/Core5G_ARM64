#!/usr/bin/env node
/*
 * Teste de fumaça VISUAL do painel (server/panel/static/index.html).
 *
 * Renderiza o index.html num Chrome headless (puppeteer-core + Chrome do
 * sistema), sem precisar de servidor/login — valida o componente de LOADER
 * (barra global no topo + spinner por botão + estado "loading" dos toggles) e
 * gera um screenshot para inspeção.
 *
 * Uso:
 *   cd server/panel/test && npm install && npm test
 *   CHROME_PATH=/usr/bin/chromium npm test     # se o Chrome estiver noutro caminho
 *
 * Sai com código != 0 se qualquer asserção falhar (CI-friendly).
 */
const puppeteer = require('puppeteer-core');
const { subir } = require('./servidor');
const path = require('path');
const fs = require('fs');

const CAMINHO = '/static/ops/index.html';   // servido por HTTP: ver servidor.js
const SHOTS = path.resolve(__dirname, 'screenshots');

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
  const srv = await subir();
  const INDEX = srv.url(CAMINHO);
  const browser = await puppeteer.launch({
    executablePath: findChrome(),
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--force-color-profile=srgb'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1400, height: 620, deviceScaleFactor: 2 });
  page.on('pageerror', e => console.log('  [pageerror]', e.message));
  await page.goto(INDEX, { waitUntil: 'domcontentloaded' });
  await new Promise(r => setTimeout(r, 400)); // o script roda; os fetch falham e são tratados

  const loaderOn = () => page.evaluate(() => document.getElementById('top-loader').classList.contains('on'));
  const spinCount = (sel) => page.evaluate(s => document.querySelector(s)?.querySelectorAll('.btn-spin').length ?? -1, sel);

  // 0) helpers presentes
  assert(await page.evaluate(() =>
    typeof loaderInc === 'function' && typeof loaderDec === 'function' &&
    typeof btnLoading === 'function' && typeof withLoader === 'function' &&
    !!document.getElementById('top-loader')), 'helpers do loader presentes');
  console.log('PASS 0 · helpers + #top-loader presentes');

  // 0.b) a folha de identidade REALMENTE carregou.
  // Sem isto o teste é cego: com `file://` o `/static/tokens.css` aponta para a
  // raiz do disco, a página renderiza sem tokens e tudo "passa" mesmo assim.
  const ident = await page.evaluate(() => {
    const cs = getComputedStyle(document.documentElement);
    const v = (n) => cs.getPropertyValue(n).trim();
    return { surface: v('--surface'), ink: v('--ink'), accent: v('--accent'),
             ponte: v('--panel'), tema: document.documentElement.dataset.theme };
  });
  assert(/^#[0-9a-f]{6}$/i.test(ident.surface) && /^#[0-9a-f]{6}$/i.test(ident.ink),
    `tokens.css não carregou (--surface=${ident.surface || 'vazio'})`);
  assert(/^#[0-9a-f]{6}$/i.test(ident.ponte),
    `a ponte de nomes antigos quebrou (--panel=${ident.ponte || 'vazio'})`);
  console.log(`PASS 0.b · identidade carregada · tema=${ident.tema} · superfície ${ident.surface} · tinta ${ident.ink} · acento ${ident.accent}`);

  // 0.c) o CONSOLE é escuro nos dois temas — e o texto dele tem de continuar
  // legível quando a página está no claro. Isto já quebrou uma vez: ao migrar
  // as cores fixas para tokens, `color:#e6e6e6` virou `var(--ink)` e o texto
  // do console caiu para 1,42:1 no tema claro. O escopo `.superficie-escura`
  // resolve; este teste garante que continue resolvido.
  const lum = (s) => {
    const [r, g, b] = s.match(/\d+/g).map(Number)
      .map((c) => { c /= 255; return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };
  const razao = (a, b) => { const x = (lum(a) + 0.05) / (lum(b) + 0.05); return x > 1 ? x : 1 / x; };
  for (const tema of ['light', 'dark']) {
    await page.evaluate((t) => { document.documentElement.dataset.theme = t; }, tema);
    const con = await page.evaluate(() => {
      const o = document.querySelector('#output');
      const cs = getComputedStyle(o);
      return { cor: cs.color, fundo: cs.backgroundColor };
    });
    const c = razao(con.cor, con.fundo);
    assert(c >= 4.5, `console ilegível no tema ${tema}: ${c.toFixed(2)}:1 (mínimo 4,5)`);

    // e as cores ANSI do log, que é o que o console mais mostra
    const ESC = String.fromCharCode(27);
    const linha = `${ESC}[32mOK${ESC}[39m ${ESC}[33mATEN${ESC}[39m ${ESC}[31mERRO${ESC}[39m`;
    const spans = await page.evaluate((txt) => {
      const o = document.querySelector('#output');
      const antes = o.innerHTML;
      o.innerHTML = renderLogLine(txt).html;
      const cores = [...o.querySelectorAll('span[style]')].map((s) => getComputedStyle(s).color);
      o.innerHTML = antes;
      return { cores, fundo: getComputedStyle(o).backgroundColor };
    }, linha);
    assert(spans.cores.length === 3, `esperava 3 trechos coloridos no log, vi ${spans.cores.length}`);
    const pior = Math.min(...spans.cores.map((x) => razao(x, spans.fundo)));
    assert(pior >= 4.5, `cor de log ilegível no tema ${tema}: ${pior.toFixed(2)}:1`);
    console.log(`PASS 0.c · console legível no tema ${tema} · texto ${c.toFixed(2)}:1 · pior cor de log ${pior.toFixed(2)}:1`);
  }
  await page.evaluate(() => { document.documentElement.dataset.theme = 'dark'; });

  // 1) repouso
  assert((await loaderOn()) === false, 'barra apagada em repouso');
  console.log('PASS 1 · repouso: top-loader OFF');

  // 2) ação: barra ON + spinner no botão
  await page.evaluate(() => { loaderInc(); btnLoading(document.querySelector('[data-cmd]'), true); });
  assert((await loaderOn()) === true, 'barra acende na ação');
  assert(await spinCount('[data-cmd]') === 1, 'spinner aparece no botão');
  console.log('PASS 2 · ação: barra ON + spinner');

  // 3) limpeza
  await page.evaluate(() => { btnLoading(document.querySelector('[data-cmd]'), false); loaderDec(); });
  assert((await loaderOn()) === false, 'barra apaga ao limpar');
  assert(await spinCount('[data-cmd]') === 0, 'spinner removido');
  console.log('PASS 3 · limpeza: barra OFF + spinner removido');

  // 4) toggle entra em loading
  await page.evaluate(() => { loaderInc(); setToggleState(document.querySelector('[data-toggle]'), 'loading'); });
  assert((await page.evaluate(() => document.querySelector('[data-toggle]').dataset.state)) === 'loading', 'toggle em loading');
  console.log('PASS 4 · toggle: estado=loading');
  await page.evaluate(() => loaderDec());

  // 5) ref-count
  await page.evaluate(() => { loaderInc(); loaderInc(); });
  assert((await loaderOn()) === true, 'ON com 2 inc');
  await page.evaluate(() => loaderDec());
  assert((await loaderOn()) === true, 'ainda ON após 1 dec');
  await page.evaluate(() => loaderDec());
  assert((await loaderOn()) === false, 'OFF após 2o dec');
  console.log('PASS 5 · ref-count correto');

  // 6) withLoader auto-limpa mesmo com erro
  const after = await page.evaluate(async () => {
    try { await withLoader(document.querySelector('[data-cmd]'), async () => { throw new Error('boom'); }); } catch {}
    return (document.getElementById('top-loader').classList.contains('on') ? '1' : '0') + '|' +
           document.querySelector('[data-cmd]').querySelectorAll('.btn-spin').length;
  });
  assert(after === '0|0', 'withLoader limpa mesmo com exceção (' + after + ')');
  console.log('PASS 6 · withLoader auto-limpa após erro');

  // 7) estresse: 7 ciclos sempre voltam ao repouso (loader nunca preso)
  for (let i = 1; i <= 7; i++) {
    await page.evaluate(async () => { await withLoader(document.querySelector('[data-cmd]'), async () => new Promise(r => setTimeout(r, 5))); });
    assert((await loaderOn()) === false, `ciclo ${i}: voltou ao repouso`);
  }
  console.log('PASS 7 · 7 ciclos → sempre volta ao repouso');

  // 8) A FAIXA DE RÁDIO MOSTRA NÚMERO, não só acende.
  // Isto quebrou por 13 versões: a 0.67.0 removeu o elemento `rl-sub` e a linha
  // que escrevia nele ficou. Como ela roda DEPOIS de acender a faixa e ANTES de
  // preencher os valores, e o catch era mudo, a tela acendia bonita com quatro
  // traços e ninguém via. Verde não basta: o teste tem de LER o número.
  await page.setRequestInterception(true);
  const onReq = (req) => {
    const u = req.url();
    const j = (o) => req.respond({ status: 200, contentType: 'application/json', body: JSON.stringify(o) });
    if (u.includes('/api/topology/gnb-stats')) return j({ up: true, age: 0.4, nrb: 51, snr: 23.5, mcs: 17, prb: 9, bler: 1.5 });
    if (u.includes('/api/telemetry')) return j({ host: { cpu_pct: 5, mem_pct: 20, cpu_count: 4, load1: 0.5 }, containers: [],
      groups: { 'p1-core': 'off', 'p1-ran': 'off', 'p2-core': 'on', 'p2-e2lab': 'on', 'p2-nonrt': 'on' } });
    if (u.includes('/api/')) return j({});
    return req.continue();
  };
  page.on('request', onReq);
  await page.reload({ waitUntil: 'domcontentloaded' });
  await new Promise((r) => setTimeout(r, 3000));
  const radio = await page.evaluate(() => {
    const v = (id) => (document.getElementById(id) || {}).textContent;
    return { acesa: document.getElementById('ran-live')?.classList.contains('on'),
             snr: v('rl-snr'), mcs: v('rl-mcs'), prb: v('rl-prb'), tot: v('rl-prb-tot'), bler: v('rl-bler') };
  });
  page.off('request', onReq);
  await page.setRequestInterception(false);
  assert(radio.acesa, 'a faixa de rádio devia acender com o P2 no ar');
  const numero = (s) => s != null && s !== '—' && !isNaN(parseFloat(s));
  for (const [k, val] of Object.entries({ SNR: radio.snr, MCS: radio.mcs, PRB: radio.prb, 'PRB total': radio.tot, BLER: radio.bler })) {
    assert(numero(val), `${k} devia mostrar número e mostra "${val}"`);
  }
  assert(radio.snr === '23.5' && radio.tot === '51',
    `os valores deviam vir da API (SNR 23.5, total 51) e vieram "${radio.snr}"/"${radio.tot}"`);
  console.log(`PASS 8 · faixa de rádio com número real · SNR ${radio.snr} · MCS ${radio.mcs} · PRB ${radio.prb}/${radio.tot} · BLER ${radio.bler}`);

  // Screenshot de inspeção: projeto ativo + loaders em botões visíveis.
  await page.evaluate(() => {
    document.querySelectorAll('.tools-set').forEach(s => s.classList.toggle('active', s.dataset.tools === 'p1'));
    document.getElementById('tools-empty').classList.remove('show');
    // Cabeçalho v0.68: seletor de projeto + botão de energia + quadrantes.
    document.getElementById('proj-select').value = 'p1';
    document.querySelectorAll('.svc-set').forEach(g => g.classList.toggle('on', g.dataset.svc === 'p1'));
    const pw = document.getElementById('power-btn');
    pw.className = 'on'; document.getElementById('power-label').textContent = 'ligado';
    loaderInc();
    btnLoading(document.querySelector('.test-p1[data-cmd]'), true);
    btnLoading(document.getElementById('logs-btn'), true);
    setToggleState(document.querySelector('[data-toggle="p1-ran"]'), 'loading');
    const bar = document.createElement('div');
    bar.style.cssText = 'position:fixed;top:0;left:30%;width:35%;height:3px;z-index:99999;background:linear-gradient(90deg,transparent,#e8590c 35%,#ffd0a8,#e8590c 65%,transparent);box-shadow:0 0 10px #e8590c';
    document.body.appendChild(bar);
  });
  await new Promise(r => setTimeout(r, 200));
  await page.screenshot({ path: path.join(SHOTS, 'loaders.png'), clip: { x: 0, y: 0, width: 1400, height: 560 } });
  console.log('\nScreenshot: ' + path.join(SHOTS, 'loaders.png'));
  console.log('✅ TODOS OS TESTES PASSARAM (0–8).');
  await browser.close();
  await srv.fechar();
})().catch(e => { console.error('\n❌ ' + e.message); process.exit(1); });
