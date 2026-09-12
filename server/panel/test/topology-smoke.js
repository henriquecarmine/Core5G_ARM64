#!/usr/bin/env node
/*
 * Teste de fumaça VISUAL da TOPOLOGIA (server/panel/static/topology.html).
 *
 * Renderiza a página nos dois projetos (?proj=p2 e ?proj=p1) num Chrome
 * headless, stubando o fetch de /api/topology com os JSONs reais de
 * static/ — sem servidor nem login. Valida:
 *   - render sem pageerror;
 *   - bandas: P1=3 (RAN/CP/UP) · P2=7 (+ Non-RT RIC, near-RT O-RAN SC, SMO e rede gerenciada por O1);
 *   - cada contêiner do SMO com o cartão completo (de onde vem, o que faz, para onde vai, imagem);
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
    // P1: 3 bandas (RAN, CP, UP) · P2: 7 (+ Non-RT âmbar e O-RAN SC rosa, v0.53+; SMO e rede O1, v0.91)
    const wantBands = proj === 'p2' ? 7 : 3;
    assert(d.bands === wantBands, `${proj}: esperava ${wantBands} bandas, veio ${d.bands}`);
    assert(d.bandLabels.some(l => l.includes('PLANO DE CONTROLE')), `${proj}: banda plano de controle`);
    assert(d.bandLabels.some(l => l.includes('PLANO DE USUÁRIO')), `${proj}: banda plano de usuário`);
    if (proj === 'p2') {
      assert(d.bandLabels.some(l => l.startsWith('SMO')), 'p2: banda do SMO');
      assert(d.bandLabels.some(l => l.includes('REDE GERENCIADA POR O1')), 'p2: banda da rede gerenciada por O1');
      const faltam = ['O1', 'M-plane', 'VES', 'Kafka', 'RESTCONF', 'OAuth'].filter(i => !d.labels.includes(i));
      assert(!faltam.length, `p2: interfaces do SMO ausentes no desenho: ${faltam.join(', ')}`);
    }
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
    const ttotal = await page.evaluate(() => Number(document.getElementById('tour-step').textContent.split('/')[1]));
    const tEsperado = proj === 'p2' ? 9 : 5;   // P2: + SMO e rede gerenciada por O1 (v0.91)
    assert(ttotal === tEsperado, `${proj}: tour esperava ${tEsperado} camadas, veio ${ttotal}`);
    const tourSemTexto = [];
    for (let i = 0; i < ttotal; i++) {
      const cap = await page.evaluate(() => document.getElementById('tour-caption').textContent);
      if (cap.length < 80 || cap.startsWith('topo.')) tourSemTexto.push(i + 1);
      await page.click('#tour-next');
    }
    assert(!tourSemTexto.length, `${proj}: camadas do tour sem legenda: ${tourSemTexto.join(', ')}`);
    assert(errors.length === 0, `${proj}: pageerror no tour: ${errors.join(' | ')}`);
    await page.click('#tour-exit');
    console.log(`PASS ${proj} · tour (${ttotal} camadas, todas com legenda) sem erro`);

    if (proj === 'p2') {
      // Cada contêiner do SMO tem a explicação completa no cartão, igual aos
      // outros nós: de onde vem, o que faz, para onde vai, imagem e conexões.
      const cartoes = await page.evaluate(() => TOPO.nodes.filter(n => /^(smo|sim)-/.test(n.id)).map(n => {
        openNode(n.id);
        const t = id => document.getElementById(id).textContent;
        const r = { id: n.id, from: t('nm-from'), does: t('nm-does'), to: t('nm-to'), tech: t('nm-tech') };
        document.getElementById('node-overlay').classList.remove('open');
        return r;
      }));
      assert(cartoes.length === 10, `p2: esperava 10 contêineres do SMO na topologia, veio ${cartoes.length}`);
      const rasos = cartoes.filter(c => [c.from, c.does, c.to].some(v => v.length < 25)
                                     || !c.tech.includes('Imagem') || !c.tech.includes('Conexões'));
      assert(!rasos.length, `p2: cartão sem explicação completa: ${rasos.map(c => c.id).join(', ')}`);
      assert(errors.length === 0, `p2: pageerror nos cartões do SMO: ${errors.join(' | ')}`);
      console.log(`PASS p2 · ${cartoes.length} contêineres do SMO com cartão completo (de onde vem · o que faz · para onde vai · imagem · conexões)`);

      // Zoom automático: a etapa da jornada enquadra os nós dela; desligado, o
      // mapa fica inteiro; ao sair, volta ao mapa inteiro.
      const espera = () => new Promise(r => setTimeout(r, 700));
      const vb = () => page.evaluate(() => document.getElementById('diagram').getAttribute('viewBox').split(' ').map(Number));
      await page.evaluate(() => fit());   // o tour acabou de sair: parte do mapa inteiro, sem animação pendente
      const cheio = await vb();
      const enquadra = (ids, v) => page.evaluate((ids, [x, y, w, h]) => ids
        .every(id => { const n = nodeById(id); return n.x >= x && n.x + 184 <= x + w && n.y >= y && n.y + 66 <= y + h; }), ids, v);
      // etapa compacta (A1 real, 3 nós num canto): o zoom tem de ser forte
      await page.evaluate(() => { startJourney(); showJourney(JOURNEY.findIndex(s => s.id === 'a1real')); });
      await espera();
      const perto = await vb();
      assert(perto[2] < cheio[2] * 0.6, `p2: zoom automático não aproximou na etapa A1 real (viewBox ${perto} × ${cheio})`);
      assert(await enquadra(['nonrt-pms', 'a1mediator', 'dbaas'], perto), 'p2: zoom automático cortou nós da etapa A1 real');
      // etapa alta (O1: a coluna do SMO até os simuladores): aproxima menos, mas enquadra todos
      await page.evaluate(() => showJourney(JOURNEY.findIndex(s => s.id === 'o1')));
      await espera();
      const o1 = await vb();
      assert(o1[2] < cheio[2], `p2: zoom automático não aproximou na etapa O1 (${o1})`);
      assert(await enquadra(['smo-controller', 'sim-odu', 'sim-oru-hybrid', 'sim-oru-hier'], o1), 'p2: zoom automático cortou nós da etapa O1');
      await page.click('#zauto');
      await espera();
      await page.evaluate(() => showJourney(JOURNEY.findIndex(s => s.id === 'ves')));
      await espera();
      const desligado = await vb();
      assert(Math.abs(desligado[2] - cheio[2]) < 1, `p2: com o zoom automático desligado o mapa não ficou inteiro (${desligado})`);
      await page.click('#zauto');
      await page.evaluate(() => endJourney());
      await espera();
      const saiu = await vb();
      assert(Math.abs(saiu[2] - cheio[2]) < 1, `p2: ao sair da jornada o mapa não voltou inteiro (${saiu})`);
      assert(errors.length === 0, `p2: pageerror no zoom automático: ${errors.join(' | ')}`);
      console.log('PASS p2 · zoom automático: aproxima na etapa, respeita o botão desligado e volta ao mapa inteiro ao sair');
    }

    // Jornada do UE (só P2): percorre as 20 etapas seguindo o pacote, sem erro
    if (proj === 'p2') {
      await page.click('#journey-btn');
      const jtotal = await page.evaluate(() => Number(document.getElementById('tour-step').textContent.split('/')[1]));
      assert(jtotal === 20, `p2: jornada esperava 20 etapas (17 + o SMO: o que é e como se liga, gestão O1 e eventos VES), veio ${jtotal}`);
      // A etapa 7 apresenta o SMO: o que é, para que serve e como se liga à rede do lab.
      const smo = await page.evaluate(() => {
        showJourney(JOURNEY.findIndex(s => s.id === 'smo'));
        return { titulo: document.getElementById('tour-title').textContent, legenda: document.getElementById('tour-caption').textContent };
      });
      assert(/SMO/.test(smo.titulo) && /para que serve/.test(smo.titulo), `p2: etapa 7 sem o título do SMO: "${smo.titulo}"`);
      assert(/gestão e orquestração/.test(smo.legenda) && /mesmo servidor/.test(smo.legenda) && /não tem O1/.test(smo.legenda),
        'p2: a etapa 7 não explica o que é o SMO e como ele se liga à nossa rede');
      // Glossário: a legenda de CADA etapa tem de sair marcada, e todo termo
      // marcado precisa ter balão com conteúdo. Um termo sublinhado cujo balão
      // abre vazio é falha calada — o teste percorre as 17 etapas conferindo.
      const glos = { etapasSemTermo: [], vazios: [], marcados: 0, expandidos: 0 };
      for (let i = 0; i < jtotal; i++) {
        const d = await page.evaluate((n) => {
          showJourney(n);
          const cap = document.getElementById('tour-caption');
          const termos = [...cap.querySelectorAll('.glos-termo')].map(e => e.getAttribute('data-termo'));
          return {
            termos,
            expandidos: cap.querySelectorAll('.glos-exp').length,
            // o texto visível não pode ter perdido nada na marcação
            vazios: termos.filter(t => { const g = window.Glossario.explica(t); return !g.o || !g.p; }),
            nested: /\([^()]*\([^()]*\)/.test(cap.textContent),
          };
        }, i);
        if (!d.termos.length) glos.etapasSemTermo.push(i + 1);
        glos.marcados += d.termos.length;
        glos.expandidos += d.expandidos;
        glos.vazios.push(...d.vazios);
        assert(!d.nested, `p2: etapa ${i + 1} ficou com parêntese dentro de parêntese`);
      }
      assert(glos.vazios.length === 0, `p2: termo marcado sem explicação: ${[...new Set(glos.vazios)].join(', ')}`);
      assert(glos.etapasSemTermo.length === 0, `p2: etapas sem nenhuma sigla marcada: ${glos.etapasSemTermo.join(', ')}`);
      assert(glos.expandidos >= 60, `p2: poucos nomes por extenso na jornada (${glos.expandidos})`);
      console.log(`PASS p2 · glossário nas ${jtotal} etapas (${glos.marcados} termos marcados, ${glos.expandidos} nomes por extenso)`);

      // Os rótulos do DESENHO também explicam. Aqui a marca não é um <span>
      // (não existe em SVG): é o próprio <text> que ganha a classe. Se alguém
      // mexer no render e perder a etiqueta, o rótulo volta a ser sigla nua.
      const svg = await page.evaluate(async () => {
        const ls = [...document.querySelectorAll('.link-label')];
        const marcados = ls.filter(e => e.classList.contains('glos-termo'));
        const semMarca = [...new Set(ls.filter(e => !e.classList.contains('glos-termo')).map(e => e.textContent))];
        const el = marcados[0];
        let balao = null;
        if (el) {
          el.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
          await new Promise(r => setTimeout(r, 60));
          const t = document.getElementById('glos-tip');
          balao = t && !t.hidden ? t.innerText : null;
        }
        const dica = document.querySelector('.lg-dica');
        return { total: ls.length, marcados: marcados.length, semMarca,
                 focaveis: marcados.filter(e => e.getAttribute('tabindex') === '0').length,
                 balao, dica: dica ? dica.textContent.trim() : null };
      });
      assert(svg.marcados >= 18, `p2: só ${svg.marcados} rótulos do desenho com glossário`);
      assert(svg.focaveis === svg.marcados, 'p2: rótulo do desenho marcado mas não alcançável por teclado');
      assert(svg.balao && svg.balao.length > 40, 'p2: o balão não abre no rótulo do desenho');
      assert(svg.dica, 'p2: falta a dica na legenda — ninguém descobre o balão sozinho');
      console.log(`PASS p2 · glossário no desenho (${svg.marcados}/${svg.total} rótulos; sem sigla: ${svg.semMarca.join(', ')})`);
      await page.keyboard.press('Escape');

      // e o balão abre de fato, no hover, com "o que é" e "para que serve"
      await page.evaluate(() => showJourney(3));
      await page.hover('#tour-caption .glos-termo');
      await new Promise(r => setTimeout(r, 150));
      const balao = await page.evaluate(() => {
        const t = document.getElementById('glos-tip');
        const alvo = document.querySelector('#tour-caption .glos-termo');
        return { aberto: !!t && !t.hidden, texto: t ? t.innerText : '',
                 descrito: alvo.getAttribute('aria-describedby'), foco: alvo.tabIndex };
      });
      assert(balao.aberto, 'p2: o balão do glossário não abriu no hover');
      assert(balao.texto.length > 60, `p2: balão do glossário quase vazio: "${balao.texto}"`);
      assert(balao.descrito === 'glos-tip', 'p2: falta aria-describedby no termo com balão aberto');
      assert(balao.foco === 0, 'p2: termo do glossário não alcançável por teclado');
      // Escape fecha
      await page.keyboard.press('Escape');
      const fechou = await page.evaluate(() => document.getElementById('glos-tip').hidden);
      assert(fechou, 'p2: Escape não fecha o balão do glossário');
      console.log('PASS p2 · balão do glossário abre no hover, é focável e fecha no Esc');

      await page.evaluate(() => showJourney(0));
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
    if (proj === 'p2') assert(fr.roles.includes('Identité') && fr.roles.includes('Événements'),
      `p2/fr: papéis do SMO não traduzidos (${fr.roles.join(',')})`);
    assert(fr.title.includes(proj === 'p1' ? 'Projet 1' : 'Projet 2'), `${proj}/fr: título = "${fr.title}"`);
    await page.click('#tour-btn');
    const tourT = await page.evaluate(() => document.getElementById('tour-title').textContent);
    assert(tourT.includes('Couche 1'), `${proj}/fr: tour = "${tourT}"`);
    await page.click('#tour-exit');
    assert(errors.length === 0, `${proj}/fr: pageerror: ${errors.join(' | ')}`);
    console.log(`PASS ${proj} · topologia em francês (chrome + nós + tour)`);
    await page.close();
  }

  // Minimapa dos processos (janela do console): quando um teste roda, o mapa
  // enquadra sozinho os componentes acesos; "mapa todo" volta ao desenho
  // inteiro, e a cor do resultado sobrevive ao redesenho.
  {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 900 });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.evaluateOnNewDocument((p1, p2) => {
      window.fetch = async (url) => new Response(String(url).includes('-p1') ? p1 : p2,
        { headers: { 'Content-Type': 'application/json' } });
    }, P1, P2);
    await page.goto(PAGE + '?proj=p2', { waitUntil: 'domcontentloaded' });
    await page.addScriptTag({ url: srv.url('/static/ops/mini-map.js') });
    const espera = () => new Promise(r => setTimeout(r, 400));
    const mini = () => page.evaluate(() => {
      const s = document.querySelector('#mm-teste svg');
      const l = document.querySelector('#mm-teste line.mm-flow');
      const pk = document.querySelector('#mm-teste circle.mm-pkt');
      return { vb: s && s.getAttribute('viewBox').split(' ').map(Number), cor: l && l.getAttribute('stroke'),
               pacotes: document.querySelectorAll('#mm-teste circle.mm-pkt').length, pacoteCor: pk && pk.getAttribute('fill') };
    });
    await page.evaluate(() => {
      const d = document.createElement('div'); d.id = 'mm-teste'; document.body.appendChild(d);
      MiniMap.attach('console', d); MiniMap.begin('a1');
    });
    await espera();
    const foco = await mini();
    assert(foco.vb && foco.vb[2] < 1800, `minimapa: não enquadrou os componentes do teste (${foco.vb})`);
    const dentro = await page.evaluate(([x, y, w, h]) => ['panel', 'nonrt-pms', 'a1sim']
      .every(id => { const n = nodeById(id); return n.x >= x && n.x + 184 <= x + w && n.y >= y && n.y + 66 <= y + h; }), foco.vb);
    assert(dentro, 'minimapa: o enquadramento cortou componentes do teste');
    assert(foco.pacotes > 0, 'minimapa: sem pacote animado durante o teste');
    await page.evaluate(() => MiniMap.end(true));
    await page.evaluate(() => document.querySelector('#mm-teste .mm-foco').click());
    await espera();
    const todo = await mini();
    assert(todo.vb[2] === 1800 && todo.vb[3] === 900, `minimapa: "mapa todo" não mostrou o desenho inteiro (${todo.vb})`);
    assert(todo.cor === 'var(--good)' && todo.pacotes > 0 && todo.pacoteCor === 'var(--good)',
      `minimapa: depois do fim, linha e pacotes deviam seguir na cor do resultado ao redesenhar (linha ${todo.cor}, ${todo.pacotes} pacotes em ${todo.pacoteCor})`);
    await page.evaluate(() => document.querySelector('#mm-teste .mm-foco').click());
    await espera();
    const volta = await mini();
    assert(volta.vb[2] < 1800, 'minimapa: "foco" não voltou a enquadrar');
    assert(errors.length === 0, `minimapa: pageerror: ${errors.join(' | ')}`);
    console.log('PASS minimapa · zoom automático nos componentes do teste; "mapa todo" alterna e o resultado sobrevive ao redesenho');
    await page.close();
  }

  await browser.close();

  await srv.fechar();
  console.log('✅ SMOKE DA TOPOLOGIA PASSOU (p2 + p1)');
})().catch(e => { console.error(e.message); process.exit(1); });
