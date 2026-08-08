/*
 * Energy ⚡ — a tabela ARM N1 × x86_64 ao fim de cada teste.
 * Honestidade por construção: números VIVOS da execução são medidos
 * (duração, RAM via /api/telemetry); a coluna x86 é ESTIMADA por fatores
 * de literatura (fontes numeradas) — o x86 não roda nesta máquina.
 * Dados: /static/ops/arm-vs-x86.json (gerado da pesquisa multi-fonte).
 */
(function () {
  'use strict';
  var CSS = [
    '.en-btn{opacity:.30;transition:all .3s;cursor:default}',
    '.en-btn.lit{opacity:1;cursor:pointer;color:#f59f00!important;text-shadow:0 0 8px rgba(245,159,0,.5)}',
    '.en-back{position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:500}',
    '.en-mod{position:fixed;z-index:501;top:50%;left:50%;transform:translate(-50%,-50%);',
    '  width:min(680px,94vw);max-height:88vh;overflow-y:auto;background:#12141a;',
    '  border:1px solid #3a3f48;border-radius:12px;padding:18px 20px;color:#c9d1d9;',
    '  font-family:-apple-system,"Segoe UI",sans-serif;font-size:12.5px;line-height:1.5;',
    '  box-shadow:0 16px 48px rgba(0,0,0,.6)}',
    '.en-mod h3{margin:0 0 2px;font-size:15px;color:#e6e6e6}',
    '.en-mod .sub{color:#8a8f98;font-size:11px;margin-bottom:12px}',
    '.en-mod .x{position:absolute;top:10px;right:14px;cursor:pointer;color:#8a8f98;font-size:15px}',
    '.en-t{width:100%;border-collapse:collapse;margin:6px 0 4px}',
    '.en-t th{font-size:9.5px;letter-spacing:.07em;text-transform:uppercase;color:#8a8f98;',
    '  text-align:left;padding:5px 8px;border-bottom:1px solid #2c3038}',
    '.en-t td{padding:6px 8px;border-bottom:1px solid #1c1f26;vertical-align:top}',
    '.en-t td.n1{color:#69db7c;font-weight:600}',
    '.en-t td.x86{color:#8a8f98}',
    '.en-t td.dl{color:#f59f00;font-weight:700;white-space:nowrap}',
    '.en-t .live{color:#4dabf7;font-size:10px;margin-left:4px}',
    '.en-t .est{color:#5c6370;font-size:10px;margin-left:4px}',
    '.en-t .src{color:#5c6370;font-size:10px}',
    '.en-bar{height:9px;border-radius:5px;background:#1c1f26;overflow:hidden;margin-top:3px}',
    '.en-bar>i{display:block;height:100%;border-radius:5px}',
    '.en-verd{margin:10px 0 4px;padding:10px 12px;border:1px solid #2f6b3a;border-radius:9px;background:#13210f22}',
    '.en-verd b{color:#69db7c}',
    '.en-why{margin-top:10px;border-top:1px solid #2c3038;padding-top:9px}',
    '.en-why>span{cursor:pointer;color:#74c0fc}',
    '.en-why .body{display:none;margin-top:7px;color:#c9d1d9;font-style:italic}',
    '.en-why.open .body{display:block}',
    '.en-cav{margin-top:9px;color:#8a8f98;font-size:10.5px}',
    '.en-src{margin-top:8px;font-size:10.5px;color:#8a8f98}',
    '.en-src a{color:#74c0fc;text-decoration:none}',
  ].join('\n');
  var st = document.createElement('style'); st.textContent = CSS; document.head.appendChild(st);

  var DATA = null, btn = null, last = null, modal = null, out = null;

  function fetchData() {
    if (DATA) return Promise.resolve(DATA);
    return fetch('/static/ops/arm-vs-x86.json?v=1').then(function (r) { return r.json(); })
      .then(function (d) { DATA = d; return d; });
  }
  function fmtDur(s) { return s >= 60 ? Math.floor(s / 60) + 'min ' + Math.round(s % 60) + 's' : Math.round(s) + 's'; }

  function render(d, tele) {
    function watts(cfg, u) { return cfg ? (DATA.power.vcpus * (cfg.idle + (cfg.max - cfg.idle) * u / 100)) : 0; }
    var cpu = tele && tele.host && tele.host.cpu_pct != null ? tele.host.cpu_pct : null;
    var liveW = cpu !== null && d.power
      ? '⚡ AGORA (CPU ' + cpu + '%): N1 ≈ <b style="color:#69db7c">' + watts(d.power.n1, cpu).toFixed(1) + ' W</b> · x86 equivalente ≈ <b style="color:#8a8f98">' + watts(d.power.x86, cpu).toFixed(1) + ' W</b> <span class="est">interp. linear Teads ' + d.power.src + '</span>'
      : '';
    var runLine = last
      ? 'Teste: <b>' + last.cmd + '</b> · duração medida: <b>' + fmtDur(last.dur) + '</b> · concluído ' + (last.ok ? '✔' : '✖')
      : 'Nenhum teste nesta sessão ainda — valores de referência.';
    var ram = tele && tele.host ? tele.host.mem_pct : null;
    var ramRow = ram !== null
      ? '<td class="n1">' + ram + '% de 16 GB<span class="live">● medido agora</span></td><td class="x86">≈ igual (mesma DRAM; ISA não muda a RAM)<span class="est">arquitetural</span></td><td class="dl">≈ 0%</td>'
      : '<td colspan=3 class="x86">telemetria indisponível</td>';
    var rows = d.rows.map(function (r) {
      return '<tr><td>' + r.label + ' <span class="src">' + (r.src || '') + '</span></td>'
        + '<td class="n1">' + r.n1 + (r.live ? '<span class="live">● medido</span>' : '') + '</td>'
        + '<td class="x86">' + r.x86 + '<span class="est">estimado (lit.)</span></td>'
        + '<td class="dl">' + r.delta + '</td></tr>';
    }).join('');
    var v = d.verdict;
    var verd = '<div class="en-verd"><b>e. VEREDITO — média ponderada:</b> N1 <b>' + v.n1 + '</b> × ' + v.x86 + ' x86_64'
      + '<div class="en-bar"><i style="width:' + v.n1 + '%;background:#2f9e44"></i></div>'
      + '<div class="en-bar"><i style="width:' + v.x86 + '%;background:#5c6370"></i></div>'
      + '<div style="margin-top:6px;font-size:11px;color:#8a8f98">' + v.pesos + '</div>'
      + '<div style="margin-top:4px">' + v.conclusao + '</div></div>';
    var extras = d.extras.map(function (e) {
      return '<tr><td>' + e.label + ' <span class="src">' + (e.src || '') + '</span></td>'
        + '<td class="n1">' + e.n1 + '</td><td class="x86">' + e.x86 + '</td><td class="dl">' + e.delta + '</td></tr>';
    }).join('');
    var srcs = d.sources.map(function (s) {
      return '[' + s.n + '] <a href="' + s.url + '" target="_blank" rel="noopener">' + s.title + '</a> <span style="color:#5c6370">(' + s.side + ')</span>';
    }).join(' · ');
    return '<span class="x">✕</span>'
      + '<h3>⚡ Eficiência — Arm Neoverse N1 (este servidor) × x86_64 (mesma geração)</h3>'
      + '<div class="sub">' + runLine + ' · AWS t4g.xlarge: 4 núcleos físicos N1 · 16 GB · vs m5.xlarge (Xeon Cascade Lake, 4 vCPU = 2 núcleos+SMT)</div>'
      + (liveW ? '<div class="sub" style="font-size:12px">' + liveW + '</div>' : '')
      + '<table class="en-t"><tr><th>Indicador</th><th>N1 (ARM)</th><th>x86_64</th><th>Δ</th></tr>'
      + rows
      + '<tr><td>d. RAM no processo</td>' + ramRow + '</tr>'
      + extras + '</table>'
      + verd
      + '<div class="en-why" id="en-why"><span>📖 Por que o ARM é mais eficiente? (clique)</span>'
      + '<div class="body">' + d.resumo70 + '</div></div>'
      + '<div class="en-cav">⚖️ Honestidade metodológica: ' + d.caveats.join(' · ') + '</div>'
      + '<div class="en-src">Fontes: ' + srcs + ' · <a href="' + d.formulas_url + '" target="_blank" rel="noopener">📐 Fórmulas item a item (docs/formulas-energia.md)</a></div>';
  }

  function close() { if (modal) { modal.b.remove(); modal.m.remove(); modal = null; } }
  function open() {
    Promise.all([fetchData(), fetch('/api/telemetry').then(function (r) { return r.json(); }).catch(function () { return null; })])
      .then(function (res) {
        close();
        var b = document.createElement('div'); b.className = 'en-back'; b.onclick = close;
        var m = document.createElement('div'); m.className = 'en-mod';
        m.innerHTML = render(res[0], res[1]);
        document.body.appendChild(b); document.body.appendChild(m);
        m.querySelector('.x').onclick = close;
        var why = m.querySelector('#en-why');
        why.querySelector('span').onclick = function () { why.classList.toggle('open'); };
        modal = { b: b, m: m };
      }).catch(function (e) { alert('tabela indisponível: ' + e); });
  }
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });

  window.Energy = {
    attach: function (el, alwaysLit, consoleEl) {
      btn = el; out = consoleEl || null;
      if (alwaysLit) { btn.classList.add('lit'); }
      btn.onclick = function () { if (btn.classList.contains('lit')) open(); };
    },
    begin: function (cmd) { last = { cmd: cmd, t0: Date.now(), ok: null, dur: 0 }; },
    end: function (ok) {
      if (last) { last.ok = ok; last.dur = (Date.now() - last.t0) / 1000; }
      if (btn) btn.classList.add('lit');   // o raio ACENDE após o teste
      // mini-linha automática no console — SÓ para testes com cena didática
      // (toggles/infra passam pelo runCommand mas não são testes; sem cena = sem energia)
      var isTest = window.FlowStrip && FlowStrip.sceneInfo && FlowStrip.sceneInfo(last && last.cmd || '').length > 0;
      if (out && last && last.dur > 1 && isTest) {
        fetchData().then(function (d) {
          var t = last.dur, p = d.power;
          var eN1 = (p.vcpus * p.n1.max * t / 3600).toFixed(2);
          var eX = (p.vcpus * p.x86.max * t / 3600).toFixed(2);
          var div = document.createElement('div');
          div.style.cssText = 'margin:4px 0;padding:3px 10px;border-left:2px solid #f59f00;font-size:10.5px;color:#8a8f98';
          div.innerHTML = '⚡ ' + Math.round(t) + 's · N1 ≈ <b style="color:#69db7c">' + eN1 + ' Wh</b> · x86 eq. ≈ ' + eX + ' Wh · <b style="color:#69db7c">−52%</b> '
            + '<span style="color:#5c6370">(estimado; teto@100%)</span> · '
            + '<a href="#" style="color:#74c0fc" onclick="Energy._open();return false">tabela ⚡</a>';
          out.appendChild(div);
          out.scrollTop = out.scrollHeight;
        }).catch(function () {});
      }
    },
    _open: function () { open(); },
  };
})();
