#!/usr/bin/env node
/*
 * Smoke FUNCIONAL do i18n (F1: login + topbar): renderiza login.html e
 * index.html em Chrome headless, troca o idioma pelo seletor 🌐 e verifica
 * que as strings mudam de verdade (pt → en → es → fr) e persistem.
 * Gera screenshots/i18n-login-fr.png para inspeção.
 *
 * Uso: node i18n-smoke.js   (ou via npm run test:i18n)
 */
const path = require('path');
const fs = require('fs');
const puppeteer = require('puppeteer-core');

const STATIC = path.resolve(__dirname, '..', 'static');
const SHOTS = path.resolve(__dirname, 'screenshots');

function findChrome() {
  const c = [process.env.CHROME_PATH, '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium', '/usr/bin/chromium-browser'].filter(Boolean);
  for (const p of c) { try { if (fs.existsSync(p)) return p; } catch {} }
  throw new Error('Chrome não encontrado (defina CHROME_PATH)');
}
const assert = (cond, msg) => { if (!cond) throw new Error('FALHOU: ' + msg); };

const EXPECT = {
  pt: { enter: 'Entrar',       hint: 'registro de presença' },
  en: { enter: 'Sign in',      hint: 'attendance record' },
  es: { enter: 'Entrar',       hint: 'registro de asistencia' },
  fr: { enter: 'Se connecter', hint: 'registre de présence' },
};

(async () => {
  fs.mkdirSync(SHOTS, { recursive: true });
  const browser = await puppeteer.launch({
    executablePath: findChrome(), headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  // ---- login.html: troca de idioma pelo seletor + persistência ----
  let page = await browser.newPage();
  await page.evaluateOnNewDocument(() => { try { localStorage.setItem('c5g-lang', 'pt'); } catch {} });
  await page.goto('file://' + path.join(STATIC, 'login.html'), { waitUntil: 'domcontentloaded' });
  await new Promise(r => setTimeout(r, 300));
  for (const lang of ['pt', 'en', 'es', 'fr']) {
    await page.click('#lang-menu .lang-btn');                 // abre o seletor com bandeira
    await page.click(`#lang-menu li[data-lang="${lang}"]`);   // escolhe o idioma
    await new Promise(r => setTimeout(r, 120));
    const txt = await page.evaluate(() => ({
      enter: document.getElementById('btn-login').textContent.trim(),
      hint: document.getElementById('guest-hint').textContent,
      saved: localStorage.getItem('c5g-lang'),
      htmlLang: document.documentElement.lang,
    }));
    assert(txt.enter === EXPECT[lang].enter, `login/${lang}: botão Entrar = "${txt.enter}"`);
    assert(txt.hint.includes(EXPECT[lang].hint), `login/${lang}: guest hint não traduzido`);
    assert(txt.saved === lang, `login/${lang}: idioma não persistiu`);
    console.log(`PASS login · ${lang} (html lang=${txt.htmlLang})`);
  }
  await page.screenshot({ path: path.join(SHOTS, 'i18n-login-fr.png') });
  console.log('  screenshot: screenshots/i18n-login-fr.png');
  await page.close();

  // ---- index.html: topbar traduzido ao carregar com idioma salvo ----
  page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.evaluateOnNewDocument(() => { try { localStorage.setItem('c5g-lang', 'es'); } catch {} });
  await page.goto('file://' + path.join(STATIC, 'index.html'), { waitUntil: 'domcontentloaded' });
  await new Promise(r => setTimeout(r, 400));
  const tb = await page.evaluate(() => ({
    panel: document.querySelector('h1 [data-i18n="topbar.panel"]').textContent,
    kiosk: document.getElementById('kiosk-btn').textContent.trim(),
    proj: document.getElementById('active-proj-label').textContent,
  }));
  assert(tb.panel === '— Panel', `index/es: h1 = "${tb.panel}"`);
  assert(tb.kiosk.includes('Proyección'), `index/es: kiosk = "${tb.kiosk}"`);
  assert(tb.proj.includes('Ningún proyecto'), `index/es: projeto ativo = "${tb.proj}"`);
  assert(errors.length === 0, `index/es: pageerror: ${errors.join(' | ')}`);
  console.log('PASS index · topbar em espanhol ao carregar com idioma salvo');

  // F2: corpo do painel (rail, console, projetos, UE Lab) traduzido
  const body = await page.evaluate(() => ({
    empty: document.getElementById('tools-empty').textContent,
    ready: document.getElementById('output').textContent,
    pill: document.getElementById('status-pill').textContent,
    seeLogs: document.getElementById('logs-btn').textContent.trim(),
    uelabRun: document.getElementById('lab-run-btn').textContent.trim(),
    banner: document.getElementById('guest-banner').textContent,
  }));
  assert(body.empty.includes('Activa un proyecto'), `index/es F2: tools-empty = "${body.empty}"`);
  assert(body.ready.includes('Listo.'), `index/es F2: console ready = "${body.ready}"`);
  assert(body.pill === 'inactivo', `index/es F2: status pill = "${body.pill}"`);
  assert(body.seeLogs === 'Ver logs', `index/es F2: ver logs = "${body.seeLogs}"`);
  assert(body.uelabRun.includes('Medir throughput'), `index/es F2: UE Lab run = "${body.uelabRun}"`);
  assert(body.banner.includes('solo lectura'), `index/es F2: banner = "${body.banner}"`);
  console.log('PASS index · F2 (rail, console, banners, UE Lab) em espanhol');
  await page.close();

  await browser.close();
  console.log('✅ SMOKE i18n PASSOU (login 4 idiomas + topbar)');
})().catch(e => { console.error(e.message); process.exit(1); });
