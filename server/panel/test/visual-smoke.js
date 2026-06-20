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
const path = require('path');
const fs = require('fs');

const INDEX = 'file://' + path.resolve(__dirname, '..', 'static', 'index.html');
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

  // Screenshot de inspeção: projeto ativo + loaders em botões visíveis.
  await page.evaluate(() => {
    document.querySelectorAll('.tools-set').forEach(s => s.classList.toggle('active', s.dataset.tools === 'p1'));
    document.getElementById('tools-empty').classList.remove('show');
    document.querySelector('.proj-card[data-proj-card="p1"]').classList.add('active');
    const ap = document.getElementById('active-proj'); ap.classList.add('on');
    document.getElementById('active-proj-label').textContent = 'Projeto 1 · Open5GS no ar';
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
  console.log('✅ TODOS OS TESTES PASSARAM (0–7).');
  await browser.close();
})().catch(e => { console.error('\n❌ ' + e.message); process.exit(1); });
