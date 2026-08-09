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

  // cena → projeto + nós acesos + fluxos (sentido do dado) no mapa real.
  // Fluxo = [origem, destino, rótulo?]; sem rótulo, usa o iface do link do mapa.
  // ghost = LINHAGEM do dado (tracejado): de onde ele veio ANTES do teste —
  // um dado não nasce do além. note = "onde vive" em uma linha no cabeçalho.
  var MMAP = {
    reg:       { proj: 'p1', nodes: ['ueransim','amf','ausf','udm'], flows: [['ueransim','amf'],['amf','ausf'],['ausf','udm']],
                 ghost: [['mongodb','udm','perfil/chaves (K, OPc)']] },
    kpm:       { proj: 'p2', nodes: ['gnb','ric','xapps'], flows: [['gnb','ric'],['ric','xapps']],
                 ghost: [['ue','gnb','rádio (RFSIM)']] },
    rc:        { proj: 'p2', nodes: ['gnb','ric','xapps'], flows: [['gnb','ric'],['ric','xapps'],['ric','gnb']],
                 ghost: [['ue','gnb','rádio (RFSIM)']] },
    analytics: { proj: 'p2', nodes: ['xapps','panel'], flows: [['xapps','panel','CSV/logs']],
                 ghost: [['gnb','ric'],['ric','xapps']], note: 'métricas gravadas pelos xApps na última coleta E2' },
    ml:        { proj: 'p2', nodes: ['panel'], flows: [],
                 ghost: [['ue','gnb','rádio 5G (walk test SUTD)'],['gnb','panel','CSV de KPIs']],
                 note: 'o dado nasceu no rádio: walk test real (SUTD) → CSV no disco → treino no painel' },
    thp:       { proj: 'p1', nodes: ['ueransim','upf-a','dn'], flows: [['ueransim','upf-a'],['upf-a','dn']] },
    failover:  { proj: 'p1', nodes: ['ueransim','upf-a','upf-b','dn'], flows: [['ueransim','upf-a'],['ueransim','upf-b','N3'],['upf-b','dn']] },
    check:     { proj: 'p1', nodes: ['panel','amf','smf','upf-a','nrf'],
                 flows: [['panel','amf','SBI/HTTP'],['panel','smf',''],['panel','upf-a',''],['panel','nrf','']],
                 note: 'o painel consulta o estado real de cada função' },
    sub:       { proj: 'p1', nodes: ['panel','mongodb'], flows: [['panel','mongodb','INSERT no Mongo']],
                 ghost: [['user','caddy'],['caddy','panel']], note: 'o assinante nasce no SEU formulário e vai morar no MongoDB' },
    chan:      { proj: 'p1', nodes: ['ueransim','dn'], flows: [['ueransim','dn','N3+N6']] },
    a1:        { proj: 'p2', nodes: ['panel','nonrt-pms','a1sim'], flows: [['panel','nonrt-pms','REST (política JSON)'],['nonrt-pms','a1sim']],
                 note: 'a política nasce num JSON do repo e desce até o RAN simulado' },
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
    var byId = {}; topo.nodes.forEach(function (n) { byId[n.id] = n; });
    var FONT = 'font-family="-apple-system,sans-serif"';
    var ghost = mm.ghost || [];
    var flowKey = {}; mm.flows.concat(ghost).forEach(function (f) { flowKey[f[0] + '>' + f[1]] = 1; });
    var isFlow = function (a, b) { return flowKey[a + '>' + b] || flowKey[b + '>' + a]; };
    var gh = {}; ghost.forEach(function (f) { [f[0], f[1]].forEach(function (id) { if (!hi[id]) gh[id] = 1; }); });
    var findLink = function (a, b) {
      return (topo.links || []).filter(function (l) {
        return (l.from === a && l.to === b) || (l.from === b && l.to === a);
      })[0];
    };
    // rótulo do fluxo: 3º campo da cena; ausente → iface do link do mapa; '' → sem rótulo
    var flowLabel = function (f) {
      if (f.length > 2) return f[2];
      var l = findLink(f[0], f[1]); return l && l.iface;
    };

    // TODAS as interfaces do mapa (E2, A1, N1...), esmaecidas, com nome no meio —
    // as do fluxo ativo são puladas aqui e redesenhadas acesas logo abaixo.
    (topo.links || []).forEach(function (l) {
      var a = byId[l.from], b = byId[l.to]; if (!a || !b) return;
      if (isFlow(l.from, l.to)) return;
      var ca = center(a), cb = center(b);
      var op = l.planned ? '.35' : '.8';
      s += '<line x1="' + ca.x + '" y1="' + ca.y + '" x2="' + cb.x + '" y2="' + cb.y + '" stroke="#3a4048" stroke-width="1.5" opacity="' + op + '"' + (l.dashed || l.planned ? ' stroke-dasharray="7 6"' : '') + '/>';
      if (l.iface) s += '<text x="' + ((ca.x + cb.x) / 2) + '" y="' + ((ca.y + cb.y) / 2 - 6) + '" text-anchor="middle" ' + FONT + ' font-size="12" fill="#7d8590" stroke="#0d0e11" stroke-width="4" paint-order="stroke">' + esc(l.iface) + '</text>';
    });

    // Rótulos de fluxo/linhagem entram em lbl e são pintados DEPOIS dos nós
    // (senão as caixas cobrem o texto nos trechos diagonais).
    var lbl = '';
    // LINHAGEM do dado (tracejado, por baixo): de onde ele veio antes do teste
    ghost.forEach(function (f) {
      var a = byId[f[0]], b = byId[f[1]]; if (!a || !b) return;
      var ca = center(a), cb = center(b);
      s += '<line x1="' + ca.x + '" y1="' + ca.y + '" x2="' + cb.x + '" y2="' + cb.y + '" stroke="#f59f00" stroke-width="2.5" opacity=".4" stroke-dasharray="8 7"/>';
      var mx = (ca.x + cb.x) / 2, my = (ca.y + cb.y) / 2;
      var ang = (Math.atan2(cb.y - ca.y, cb.x - ca.x) * 180 / Math.PI).toFixed(1);
      s += '<polygon points="0,-7 14,0 0,7" fill="#f59f00" opacity=".5" transform="translate(' + mx + ',' + my + ') rotate(' + ang + ')"/>';
      var glabel = flowLabel(f);
      if (glabel) lbl += '<text x="' + mx + '" y="' + (my - 12) + '" text-anchor="middle" ' + FONT + ' font-size="14" font-style="italic" fill="#c9974d" stroke="#0d0e11" stroke-width="4" paint-order="stroke">' + esc(glabel) + '</text>';
    });
    // fluxo ativo: linha âmbar + seta no sentido do dado + NOME da interface + pacote
    mm.flows.forEach(function (f) {
      var a = byId[f[0]], b = byId[f[1]]; if (!a || !b) return;
      var ca = center(a), cb = center(b);
      s += '<line class="mm-flow" x1="' + ca.x + '" y1="' + ca.y + '" x2="' + cb.x + '" y2="' + cb.y + '" stroke="#f59f00" stroke-width="3" opacity=".6"/>';
      var mx = (ca.x + cb.x) / 2, my = (ca.y + cb.y) / 2;
      var ang = (Math.atan2(cb.y - ca.y, cb.x - ca.x) * 180 / Math.PI).toFixed(1);
      s += '<polygon class="mm-flow" points="0,-8 16,0 0,8" fill="#f59f00" opacity=".9" transform="translate(' + mx + ',' + my + ') rotate(' + ang + ')"/>';
      var flabel = flowLabel(f);
      if (flabel) lbl += '<text x="' + mx + '" y="' + (my - 14) + '" text-anchor="middle" ' + FONT + ' font-size="16" font-weight="700" fill="#ffb84d" stroke="#0d0e11" stroke-width="5" paint-order="stroke">' + esc(flabel) + '</text>';
      if (live) {
        var dur = (Math.hypot(cb.x - ca.x, cb.y - ca.y) / 220 + 0.6).toFixed(2);
        s += '<circle r="7" fill="#ffb84d"><animate attributeName="cx" from="' + ca.x + '" to="' + cb.x + '" dur="' + dur + 's" repeatCount="indefinite"/><animate attributeName="cy" from="' + ca.y + '" to="' + cb.y + '" dur="' + dur + 's" repeatCount="indefinite"/></circle>';
      }
    });
    // nós: TODOS com nome — aceso (âmbar), origem do dado (âmbar tracejado) ou apagado
    topo.nodes.forEach(function (n) {
      var on = hi[n.id], g = gh[n.id];
      s += '<rect x="' + n.x + '" y="' + n.y + '" width="184" height="66" rx="9" fill="'
        + (on ? '#2b2313' : g ? '#221d12' : '#181b22') + '" stroke="' + (on ? '#f59f00' : g ? '#8a6d1f' : '#2c313b')
        + '" stroke-width="' + (on ? 3 : g ? 1.5 : 1) + '"' + (g ? ' stroke-dasharray="6 5"' : '') + '/>';
      s += '<text x="' + (n.x + 92) + '" y="' + (n.y + 40) + '" text-anchor="middle" ' + FONT + ' font-size="' + (on ? 18 : 15) + '" font-weight="' + (on ? 700 : 500) + '" fill="' + (on ? '#ffb84d' : g ? '#d0a75c' : '#9aa1ab') + '">' + esc(n.label || n.id) + '</text>';
    });
    s += lbl + '</svg>';
    host.innerHTML = '<div class="mm-head"><b>◉</b> onde está rodando — mapa do projeto (' + mm.proj.toUpperCase() + ') · setas = sentido dos dados'
      + (mm.ghost ? ' · <span style="color:#8a6d1f">⇢ tracejado = de onde o dado veio</span>' : '')
      + (mm.note ? ' · <span style="color:#c9974d">' + mm.note + '</span>' : '')
      + ' <span style="margin-left:auto">▾</span></div>' + s;
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
