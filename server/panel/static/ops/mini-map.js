/*
 * MiniMap — "onde está rodando": o mapa do projeto inteiro em miniatura,
 * tudo esmaecido, com os componentes do teste ACESOS e pacotes animados no
 * sentido real dos dados. Vivo durante a execução (begin/end via FlowStrip).
 * Cenas → nós/fluxos do mapa: MMAP abaixo (artefatos acendem o componente
 * onde vivem — opção minimalista escolhida pelo usuário).
 */
(function () {
  'use strict';
  var CSS = [
    '.mm-box{margin:6px 0;border:1px solid #2c3038;border-radius:8px;background:#0d0e11;overflow:hidden}',
    '.mm-head{display:flex;align-items:center;gap:6px;padding:3px 10px;font:10px -apple-system,sans-serif;color:#8a8f98;cursor:pointer}',
    '.mm-head b{color:#f59f00}',
    '.mm-box svg{display:block;width:100%;height:auto}',
    '.mm-box.closed svg{display:none}',
  ].join('\n');
  var st = document.createElement('style'); st.textContent = CSS; document.head.appendChild(st);

  // cena → projeto + nós acesos + fluxos (sentido do dado) no mapa real
  var MMAP = {
    reg:       { proj: 'p1', nodes: ['ueransim','amf','ausf','udm'], flows: [['ueransim','amf'],['amf','ausf'],['ausf','udm']] },
    kpm:       { proj: 'p2', nodes: ['gnb','ric','xapps'], flows: [['gnb','ric'],['ric','xapps']] },
    rc:        { proj: 'p2', nodes: ['gnb','ric','xapps'], flows: [['gnb','ric'],['ric','xapps'],['ric','gnb']] },
    analytics: { proj: 'p2', nodes: ['xapps','panel'], flows: [['xapps','panel']] },
    ml:        { proj: 'p2', nodes: ['panel'], flows: [] },
    thp:       { proj: 'p1', nodes: ['ueransim','upf-a','dn'], flows: [['ueransim','upf-a'],['upf-a','dn']] },
    failover:  { proj: 'p1', nodes: ['ueransim','upf-a','upf-b','dn'], flows: [['ueransim','upf-a'],['ueransim','upf-b'],['upf-b','dn']] },
    check:     { proj: 'p1', nodes: ['amf','smf','upf-a','nrf'], flows: [] },
    sub:       { proj: 'p1', nodes: ['mongodb'], flows: [] },
    chan:      { proj: 'p1', nodes: ['ueransim','dn'], flows: [['ueransim','dn']] },
    a1:        { proj: 'p2', nodes: ['nonrt-pms','a1sim'], flows: [['nonrt-pms','a1sim']] },
    demo:      { proj: 'p1', nodes: ['ueransim','upf-a','dn'], flows: [['ueransim','upf-a'],['upf-a','dn'],['dn','upf-a']] },
  };
  var TOPO = { p1: null, p2: null }, hosts = {};

  function load(proj) {
    if (TOPO[proj]) return Promise.resolve(TOPO[proj]);
    var f = proj === 'p1' ? 'openran-topology-p1.json' : 'openran-topology.json';
    return fetch('/static/ops/' + f).then(function (r) { return r.json(); })
      .then(function (d) { TOPO[proj] = d; return d; });
  }
  function center(n) { return { x: n.x + 92, y: n.y + 33 }; }
  function esc(t) { return String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }

  function draw(host, mm, topo, live) {
    var W = (topo.canvas && topo.canvas.w) || 1300, H = (topo.canvas && topo.canvas.h) || 900;
    var hi = {}; mm.nodes.forEach(function (id) { hi[id] = 1; });
    var s = '<svg viewBox="0 0 ' + W + ' ' + H + '" xmlns="http://www.w3.org/2000/svg">';
    // bandas: cor da camada bem suave + nome, para o mapa ser reconhecível de longe
    for (var k in (topo.layers || {})) {
      var ly = topo.layers[k]; if (!ly.band) continue;
      var ns = topo.nodes.filter(function (n) { return n.layer === k; }); if (!ns.length) continue;
      var x0 = Math.min.apply(0, ns.map(function (n) { return n.x; })) - 24;
      var y0 = Math.min.apply(0, ns.map(function (n) { return n.y; })) - 30;
      var x1 = Math.max.apply(0, ns.map(function (n) { return n.x + 184; })) + 24;
      var y1 = Math.max.apply(0, ns.map(function (n) { return n.y + 66; })) + 14;
      var c = ly.color || '#22262e';
      s += '<rect x="' + x0 + '" y="' + y0 + '" width="' + (x1 - x0) + '" height="' + (y1 - y0) + '" rx="14" fill="' + c + '" fill-opacity=".05" stroke="' + c + '" stroke-opacity=".35"/>';
      s += '<text x="' + (x0 + 14) + '" y="' + (y0 + 20) + '" font-family="-apple-system,sans-serif" font-size="14" font-weight="600" fill="' + c + '" fill-opacity=".75">' + esc(ly.label || k) + '</text>';
    }
    // fluxos (por baixo dos nós acesos): linha + seta no sentido do dado + pacote animado
    var byId = {}; topo.nodes.forEach(function (n) { byId[n.id] = n; });
    mm.flows.forEach(function (f) {
      var a = byId[f[0]], b = byId[f[1]]; if (!a || !b) return;
      var ca = center(a), cb = center(b);
      s += '<line class="mm-flow" x1="' + ca.x + '" y1="' + ca.y + '" x2="' + cb.x + '" y2="' + cb.y + '" stroke="#f59f00" stroke-width="3" opacity=".55"/>';
      var mx = (ca.x + cb.x) / 2, my = (ca.y + cb.y) / 2;
      var ang = (Math.atan2(cb.y - ca.y, cb.x - ca.x) * 180 / Math.PI).toFixed(1);
      s += '<polygon class="mm-flow" points="0,-8 16,0 0,8" fill="#f59f00" opacity=".9" transform="translate(' + mx + ',' + my + ') rotate(' + ang + ')"/>';
      if (live) {
        var dur = (Math.hypot(cb.x - ca.x, cb.y - ca.y) / 220 + 0.6).toFixed(2);
        s += '<circle r="7" fill="#ffb84d"><animate attributeName="cx" from="' + ca.x + '" to="' + cb.x + '" dur="' + dur + 's" repeatCount="indefinite"/><animate attributeName="cy" from="' + ca.y + '" to="' + cb.y + '" dur="' + dur + 's" repeatCount="indefinite"/></circle>';
      }
    });
    // nós: TODOS com nome — apagados em cinza discreto, acesos em âmbar destacado
    topo.nodes.forEach(function (n) {
      var on = hi[n.id];
      s += '<rect x="' + n.x + '" y="' + n.y + '" width="184" height="66" rx="9" fill="'
        + (on ? '#2b2313' : '#181b22') + '" stroke="' + (on ? '#f59f00' : '#262a33') + '" stroke-width="' + (on ? 3 : 1) + '"/>';
      s += '<text x="' + (n.x + 92) + '" y="' + (n.y + 40) + '" text-anchor="middle" font-family="-apple-system,sans-serif" font-size="' + (on ? 17 : 14) + '" font-weight="' + (on ? 700 : 400) + '" fill="' + (on ? '#ffb84d' : '#6b7280') + '">' + esc(n.label || n.id) + '</text>';
    });
    s += '</svg>';
    host.innerHTML = '<div class="mm-head"><b>◉</b> onde está rodando — mapa do projeto (' + mm.proj.toUpperCase() + ') · setas = sentido dos dados <span style="margin-left:auto">▾</span></div>' + s;
    host.querySelector('.mm-head').onclick = function () { host.classList.toggle('closed'); };
    host.style.display = 'block';
  }

  function show(name, host, live) {
    var mm = MMAP[name];
    if (!mm || !host) { if (host) { host.style.display = 'none'; host.innerHTML = ''; } return; }
    load(mm.proj).then(function (topo) { draw(host, mm, topo, live); }).catch(function () {});
  }

  window.MiniMap = {
    attach: function (name, el) { hosts[name] = el; },
    preview: function (sceneName, el) { show(sceneName, el, true); },
    begin: function (sceneName) { show(sceneName, hosts.console, true); },
    end: function (ok) {
      var h = hosts.console; if (!h || !h.innerHTML) return;
      var c = ok ? '#2f9e44' : '#e03131';
      h.querySelectorAll('circle').forEach(function (x) { x.remove(); });   // congela: fim do fluxo
      h.querySelectorAll('line.mm-flow').forEach(function (l) { l.setAttribute('stroke', c); });
      h.querySelectorAll('polygon.mm-flow').forEach(function (p) { p.setAttribute('fill', c); });
    },
  };
})();
