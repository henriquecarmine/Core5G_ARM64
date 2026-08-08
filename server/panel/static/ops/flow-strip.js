/*
 * FlowStrip — o percurso dos dados, minimalista, em cima da tela de log.
 *
 * Enquanto um teste roda, uma faixa acima do console mostra de onde os dados
 * saem, por onde passam (interface), o momento do armazenamento e o resultado:
 *
 *   [📡 gNB] ──E2──▸ [🧠 RIC] ──▸ [📈 xApp] ──▸ [💾 kpm.log]        ✔
 *
 * Sem backend novo: as CENAS abaixo casam o comando executado e avançam o
 * fluxo por regex sobre as MESMAS linhas que o console já recebe (professor
 * via stream, aluno via LiveBuffer). Tokens de protocolo (NGAP, E2, KPM,
 * RMSE, iperf) não mudam com o LAB_LANG — os gatilhos seguem valendo nos
 * 4 idiomas. Comando sem cena ⇒ a faixa simplesmente não aparece.
 *
 * Vive DENTRO de área de console (escura nos dois temas): paleta FIXA,
 * nunca variáveis de tema (convenção nº 1 do README do painel).
 */
(function () {
  'use strict';

  var CSS = [
    '.fs-strip{display:none;align-items:center;gap:5px;padding:6px 10px;margin-bottom:6px;',
    '  background:#12141a;border:1px solid #2c3038;border-radius:6px;overflow-x:auto;',
    '  font-family:"SF Mono",Menlo,Consolas,monospace;font-size:10.5px;color:#8a8f98;flex:none}',
    '.fs-strip.on{display:flex}',
    '.fs-node{display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:999px;',
    '  border:1px solid #2c3038;background:#181b22;color:#6b7280;white-space:nowrap;transition:all .25s}',
    '.fs-node.active{color:#ffb84d;border-color:#8a5a1a;animation:fs-pulse 1.1s infinite}',
    '.fs-node.done{color:#69db7c;border-color:#2f6b3a}',
    '.fs-node.fail{color:#ff6b6b;border-color:#7a2e2e}',
    '.fs-edge{position:relative;flex:0 0 26px;height:2px;background:#2c3038;border-radius:2px;margin:0 1px}',
    '.fs-edge>i{position:absolute;top:-13px;left:50%;transform:translateX(-50%);',
    '  font-size:8.5px;font-style:normal;color:#4d5561;letter-spacing:.03em}',
    '.fs-edge.done{background:#2f6b3a}',
    '.fs-edge.active{background:#4d3a14}',
    '.fs-edge.active::after{content:"";position:absolute;top:-2px;left:0;width:6px;height:6px;',
    '  border-radius:50%;background:#ffb84d;animation:fs-travel .8s linear infinite}',
    '.fs-result{margin-left:auto;padding-left:8px;font-weight:700;visibility:hidden}',
    '.fs-result.ok{visibility:visible;color:#69db7c}',
    '.fs-result.fail{visibility:visible;color:#ff6b6b}',
    '@keyframes fs-travel{from{left:0}to{left:calc(100% - 6px)}}',
    '@keyframes fs-pulse{50%{box-shadow:0 0 9px rgba(255,184,77,.35)}}',
  ].join('\n');

  // ---- Cenas: percurso por comando -----------------------------------------
  // match: casa a CHAVE do comando (professor) ou o RÓTULO da execução (aluno,
  // vem do tee_to_live). nodes: [{id, txt}] — txt já com ícone. edges: rótulo
  // de interface entre nó i e i+1. triggers: linha que casa `re` avança o
  // fluxo até o nó `to` (cada gatilho dispara uma vez; ordem livre).
  var SCENES = [
    { match: /^(test-registration|test-ng-setup|test-ue-connection)$/,
      nodes: [{ id: 'ue', txt: '📱 UE' }, { id: 'gnb', txt: '📡 gNB' },
              { id: 'amf', txt: '🧭 AMF' }, { id: 'sec', txt: '🔐 AUSF/UDM' }],
      edges: ['N1', 'N2', 'SBI'],
      triggers: [
        { re: /UERANSIM|nr-ue|Registration|registr/i, to: 'gnb' },
        { re: /NGAP|NG Setup|InitialUE|\bAMF\b/i, to: 'amf' },
        { re: /AUSF|UDM|5G-AKA|\bAKA\b|autentic|authent/i, to: 'sec' },
      ] },
    { match: /^(p2-test-e2-kpm(-traffic)?|p2-kpm-real)$/,
      nodes: [{ id: 'gnb', txt: '📡 gNB (E2 agent)' }, { id: 'ric', txt: '🧠 FlexRIC' },
              { id: 'xapp', txt: '📈 xApp KPM' }, { id: 'store', txt: '💾 kpm log' }],
      edges: ['E2', 'E42', ''],
      triggers: [
        { re: /E2 SETUP|E2 Setup|assoc|conectad|connected/i, to: 'ric' },
        { re: /SUBSCRIPTION|INDICATION|KPM/i, to: 'xapp' },
        { re: /\.log|\.csv|salv|grava|arquiv|collect/i, to: 'store' },
      ] },
    { match: /^p2-test-e2-(rc|sm)$/,
      nodes: [{ id: 'gnb', txt: '📡 gNB (E2 agent)' }, { id: 'ric', txt: '🧠 FlexRIC' },
              { id: 'xapp', txt: '🎛 xApp' }, { id: 'ctl', txt: '⚙️ controle/SM' }],
      edges: ['E2', 'E42', ''],
      triggers: [
        { re: /E2 SETUP|E2 Setup|assoc|conectad|connected/i, to: 'ric' },
        { re: /SUBSCRIPTION|INDICATION|Service Model|E2SM/i, to: 'xapp' },
        { re: /CONTROL|\bRC\b|aplicad|applied/i, to: 'ctl' },
      ] },
    { match: /^p2-kpm-analytics$/,
      nodes: [{ id: 'raw', txt: '💾 kpm bruto' }, { id: 'etl', txt: '🧪 ETL' },
              { id: 'kpi', txt: '📐 KPIs' }, { id: 'viz', txt: '📊 série/decisão' }],
      edges: ['', '', ''],
      triggers: [
        { re: /pars|lendo|leitura|ETL|extra/i, to: 'etl' },
        { re: /KPI|indicador|m[ée]dia|percentil/i, to: 'kpi' },
        { re: /CSV|sparkline|s[ée]rie|decis|relat/i, to: 'viz' },
      ] },
    { match: /^p2-ml-/,
      nodes: [{ id: 'data', txt: '💾 dados SUTD' }, { id: 'train', txt: '🧮 treino' },
              { id: 'metr', txt: '📊 métricas' }],
      edges: ['', ''],
      triggers: [
        { re: /trein|train|fit|Boost|Forest|MLP|model/i, to: 'train' },
        { re: /RMSE|R2|R²|acur|accur|matriz|F1|precision/i, to: 'metr' },
      ] },
    { match: /^test-throughput$|throughput/i,
      nodes: [{ id: 'ue', txt: '📱 UE' }, { id: 'gnb', txt: '📡 gNB' },
              { id: 'upf', txt: '🔀 UPF' }, { id: 'dn', txt: '🌐 DN (iperf3)' }],
      edges: ['N1', 'N3', 'N6'],
      triggers: [
        { re: /uesimtun|PDU|sess/i, to: 'gnb' },
        { re: /iperf|Connecting|conectand/i, to: 'upf' },
        { re: /bits\/sec|Mbits|sender|receiver/i, to: 'dn' },
      ] },
    { match: /^test-upf-failover$/,
      nodes: [{ id: 'ue', txt: '📱 UE' }, { id: 'upfa', txt: '🔀 UPF-A' },
              { id: 'cut', txt: '✂️ falha' }, { id: 'upfb', txt: '🔀 UPF-B' }],
      edges: ['N3', '', 'N3'],
      triggers: [
        { re: /UPF-A|upf-a|tr[áa]fego|traffic/i, to: 'upfa' },
        { re: /derrub|matando|parando|down|failover|stopping/i, to: 'cut' },
        { re: /UPF-B|upf-b|recuper|recover|voltou/i, to: 'upfb' },
      ] },
    { match: /^(test-system-status|test-config-coherence|status)$/,
      nodes: [{ id: 'ctn', txt: '🐳 containers' }, { id: 'net', txt: '🔗 rede/config' },
              { id: 'verd', txt: '📋 veredito' }],
      edges: ['', ''],
      triggers: [
        { re: /rede|network|coer|coher|config|interface|N[234]\b/i, to: 'net' },
        { re: /resumo|resultado|conclus|veredito|summary|✅|❌/i, to: 'verd' },
      ] },
    { match: /^api-subscriber$|assinante/i,
      nodes: [{ id: 'cred', txt: '📝 IMSI/K/OPC' }, { id: 'dbctl', txt: '⚙️ open5gs-dbctl' },
              { id: 'store', txt: '💾 MongoDB' }],
      edges: ['', ''],
      triggers: [
        { re: /dbctl|docker exec|Adicionando|Removendo|Executando/i, to: 'dbctl' },
        { re: /inserid|adicionad|removid|sucesso|cadastrad|added|removed/i, to: 'store' },
      ] },
    { match: /^api-channel$|canal/i,
      nodes: [{ id: 'par', txt: '🎛 parâmetros' }, { id: 'ran', txt: '📡 UERANSIM (canal)' },
              { id: 'fx', txt: '🌐 efeito (ping)' }],
      edges: ['', ''],
      triggers: [
        { re: /UERANSIM|aplicand|apply|\btc\b|netem|delay|loss/i, to: 'ran' },
        { re: /ping|t[úu]nel|efeito|icmp|\bms\b/i, to: 'fx' },
      ] },
    { match: /^p3-test-a1$/,
      nodes: [{ id: 'pms', txt: '🧠 PMS (nonRT)' }, { id: 'type', txt: '📐 policy type' },
              { id: 'pol', txt: '📋 política' }, { id: 'sim', txt: '📡 a1-sim (nearRT)' }],
      edges: ['', '', 'A1'],
      triggers: [
        { re: /type 1/i, to: 'type' },
        { re: /criada via PMS|service core5g/i, to: 'pol' },
        { re: /presente no a1-sim|leitura de volta/i, to: 'sim' },
      ] },
    { match: /demo-e2e|Demonstra[çc][ãa]o E2E/i,
      nodes: [{ id: 'ue', txt: '📱 UE' }, { id: 'gnb', txt: '📡 gNB' },
              { id: 'upf', txt: '🔀 UPF' }, { id: 'dn', txt: '🌐 internet' },
              { id: 'metr', txt: '📊 medição' }],
      edges: ['N1', 'N3', 'N6', ''],
      triggers: [
        { re: /registr/i, to: 'gnb' },
        { re: /PDU|sess|endere[çc]o|address|uesimtun/i, to: 'upf' },
        { re: /ping|internet|naveg|browse/i, to: 'dn' },
        { re: /throughput|iperf|bits\/sec|Mbits/i, to: 'metr' },
      ] },
  ];

  var ANSI = /\x1b\[[0-9;]*m/g;
  var mounts = {};            // nome -> elemento host
  var cur = null;             // execução ativa: {scene, host, els, pos, fired}

  function injectCss() {
    var s = document.createElement('style');
    s.textContent = CSS;
    document.head.appendChild(s);
  }

  function render(scene, host) {
    var strip = document.createElement('div');
    strip.className = 'fs-strip on';
    var els = { nodes: [], edges: [] };
    scene.nodes.forEach(function (n, i) {
      if (i > 0) {
        var e = document.createElement('span');
        e.className = 'fs-edge';
        var iface = scene.edges[i - 1];
        if (iface) e.innerHTML = '<i>' + iface + '</i>';
        strip.appendChild(e);
        els.edges.push(e);
      }
      var d = document.createElement('span');
      d.className = 'fs-node';
      d.textContent = n.txt;
      strip.appendChild(d);
      els.nodes.push(d);
    });
    var r = document.createElement('span');
    r.className = 'fs-result';
    strip.appendChild(r);
    els.result = r;
    host.innerHTML = '';
    host.appendChild(strip);
    return els;
  }

  function setPos(pos) {
    // nós/arestas antes de `pos` ficam done; o nó `pos` pulsa e a aresta que
    // chega nele mostra o pacote viajando.
    if (!cur) return;
    cur.pos = pos;
    cur.els.nodes.forEach(function (n, i) {
      n.className = 'fs-node' + (i < pos ? ' done' : i === pos ? ' active' : '');
    });
    cur.els.edges.forEach(function (e, i) {
      // aresta i liga nó i ao nó i+1
      e.className = 'fs-edge' + (i < pos - 1 ? ' done' : i === pos - 1 ? ' active' : '');
    });
  }

  function begin(key, mountName) {
    end0();                                    // fecha faixa de execução anterior
    var host = mounts[mountName];
    if (!host || !key) return;
    var scene = null;
    for (var i = 0; i < SCENES.length; i++) {
      if (SCENES[i].match.test(String(key))) { scene = SCENES[i]; break; }
    }
    if (!scene) { host.innerHTML = ''; return; }
    cur = { scene: scene, host: host, els: render(scene, host), pos: 0, fired: [] };
    setPos(0);
  }

  function feed(line) {
    if (!cur) return;
    var txt = String(line == null ? '' : line).replace(ANSI, '');
    if (/^\$ /.test(txt)) return;   // eco do comando (stream_command) não é dado
    var trg = cur.scene.triggers;
    for (var i = 0; i < trg.length; i++) {
      if (cur.fired.indexOf(i) >= 0) continue;
      if (!trg[i].re.test(txt)) continue;
      cur.fired.push(i);
      var to = 0;
      for (var j = 0; j < cur.scene.nodes.length; j++) {
        if (cur.scene.nodes[j].id === trg[i].to) { to = j; break; }
      }
      if (to > cur.pos) setPos(to);
    }
  }

  function end0() { cur = null; }

  function end(ok) {
    if (!cur) return;
    if (ok) {
      cur.els.nodes.forEach(function (n) { n.className = 'fs-node done'; });
      cur.els.edges.forEach(function (e) { e.className = 'fs-edge done'; });
      cur.els.result.textContent = '✔';
      cur.els.result.className = 'fs-result ok';
    } else {
      var n = cur.els.nodes[cur.pos];
      if (n) n.className = 'fs-node fail';
      var e = cur.els.edges[cur.pos - 1];
      if (e) e.className = 'fs-edge';
      cur.els.result.textContent = '✖';
      cur.els.result.className = 'fs-result fail';
    }
    cur = null;   // faixa fica visível com o desfecho até a próxima execução
  }

  function attach(name, el) { if (el) mounts[name] = el; }

  injectCss();
  window.FlowStrip = { attach: attach, begin: begin, feed: feed, end: end };
})();
