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
    '  background:var(--bg);border:1px solid var(--line);border-radius:6px;overflow-x:auto;',
    '  font-family:"SF Mono",Menlo,Consolas,monospace;font-size:10.5px;color:var(--ink-3);flex:none}',
    '.fs-strip.on{display:flex}',
    '.fs-node{display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:999px;',
    '  border:1px solid var(--line);background:var(--surface);color:var(--ink-3);white-space:nowrap;transition:all .25s}',
    '.fs-node.active{color:var(--warn-text);border-color:var(--w-8);animation:fs-pulse 1.1s infinite}',
    '.fs-node.done{color:var(--good-text);border-color:var(--g-8)}',
    '.fs-node.fail{color:var(--bad-text);border-color:var(--r-8)}',
    '.fs-edge{position:relative;flex:0 0 26px;height:2px;background:var(--line);border-radius:2px;margin:0 1px}',
    '.fs-edge>i{position:absolute;top:-13px;left:50%;transform:translateX(-50%);',
    '  font-size:8.5px;font-style:normal;color:var(--n-8);letter-spacing:.03em}',
    '.fs-edge.done{background:var(--g-8)}',
    '.fs-edge.active{background:var(--warn-soft)}',
    '.fs-edge.active::after{content:"";position:absolute;top:-2px;left:0;width:6px;height:6px;',
    '  border-radius:50%;background:var(--warn-text);animation:fs-travel .8s linear infinite}',
    '.fs-result{margin-left:auto;padding-left:8px;font-weight:700;visibility:hidden}',
    '.fs-node.hasinfo{cursor:pointer}',
    '.fs-node.hasinfo:hover{border-color:var(--ink-3);color:var(--console-ink)}',
    '.fs-node.hasinfo i{font-style:normal;opacity:.55;margin-left:2px;font-size:9px}',
    '.fs-back{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:600}',
    '.fs-pop{position:fixed;z-index:601;max-width:390px;background:var(--bg);border:1px solid var(--line-2);',
    '  border-radius:10px;padding:14px 16px;box-shadow:0 12px 34px rgba(0,0,0,.5);',
    '  font-family:-apple-system,"Segoe UI",sans-serif;font-size:12.5px;color:var(--console-ink);line-height:1.5}',
    '.fs-pop h4{margin:0 0 8px;font-size:13.5px;color:var(--ink)}',
    '.fs-pop .sec{font-size:9px;letter-spacing:.08em;color:var(--ink-3);margin:9px 0 2px;text-transform:uppercase}',
    '.fs-pop code{font-family:"SF Mono",Menlo,monospace;font-size:11px;color:var(--accent-text);word-break:break-all}',
    '.fs-pop .hint{margin-top:10px;padding-top:8px;border-top:1px solid var(--line);color:var(--ink-3);font-size:11px}',
    '.fs-pop .x{position:absolute;top:8px;right:11px;cursor:pointer;color:var(--ink-3);font-size:14px}',
    // Fonte dos dados: cada opção é UMA linha (rádio · rótulo · ação à direita);
    // os meios de envio (arquivo / colar) ficam alinhados sob um rótulo curto.
    '.fs-src label.opt{display:flex;align-items:center;gap:8px;margin:6px 0 1px;cursor:pointer;color:var(--console-ink);line-height:1.3}',
    '.fs-src label.opt input{margin:0;flex:none;width:auto;height:auto;min-width:0}',   // o painel dá width:100% a todo input: o rádio engolia a linha
    '.fs-src .lbl{flex:1 1 auto;min-width:0;font-weight:600}',
    '.fs-src .act{flex:none;margin-left:auto;white-space:nowrap;font-size:11px}',
    '.fs-src .exp{margin-left:22px;color:var(--ink-3);font-size:11px}',
    '.fs-src a{color:var(--accent-text)}',
    '.fs-src .st{color:var(--good-text)}',
    '.fs-src .how{display:flex;flex-wrap:wrap;align-items:center;gap:5px 8px;margin:6px 0 0 22px}',
    '.fs-src .hk{flex:none;width:44px;font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3)}',
    '.fs-src input[type=file]{flex:1 1 180px;min-width:0;margin:0;font-size:11px;color:var(--ink-3)}',
    '.fs-src .paste{flex:1 1 100%;order:2;margin-left:52px;font:10.5px "SF Mono",Menlo,monospace;background:var(--console-bg);color:var(--console-ink);border:1px solid var(--line);border-radius:6px;padding:6px 8px;resize:vertical;min-height:58px}',
    '.fs-src .pastebtn{order:3;margin-left:52px;font:11px -apple-system,"Segoe UI",sans-serif;background:var(--surface-2);color:var(--console-ink);border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer}',
    '.fs-src .pastebtn:hover{border-color:var(--accent-text);color:var(--ink)}',
    '.fs-result.ok{visibility:visible;color:var(--good-text)}',
    '.fs-result.fail{visibility:visible;color:var(--bad-text)}',
    '@keyframes fs-travel{from{left:0}to{left:calc(100% - 6px)}}',
    '@keyframes fs-pulse{50%{box-shadow:0 0 9px rgba(255,184,77,.35)}}',
  ].join('\n');

  // ---- Cenas: percurso por comando -----------------------------------------
  // match: casa a CHAVE do comando (professor) ou o RÓTULO da execução (aluno,
  // vem do tee_to_live). nodes: [{id, txt}] — txt já com ícone. edges: rótulo
  // de interface entre nó i e i+1. triggers: linha que casa `re` avança o
  // fluxo até o nó `to` (cada gatilho dispara uma vez; ordem livre).
  var SCENES = [
    { name: "reg", match: /^(test-registration|test-ng-setup|test-ue-connection)$/,
      nodes: [{ id: 'ue', txt: '📱 UE' }, { id: 'gnb', txt: '📡 gNB' },
              { id: 'amf', txt: '🧭 AMF' }, { id: 'sec', txt: '🔐 AUSF/UDM' }],
      edges: ['N1', 'N2', 'SBI'],
      triggers: [
        { re: /UERANSIM|nr-ue|Registration|registr/i, to: 'gnb' },
        { re: /NGAP|NG Setup|InitialUE|\bAMF\b/i, to: 'amf' },
        { re: /AUSF|UDM|5G-AKA|\bAKA\b|autentic|authent/i, to: 'sec' },
      ] },
    { name: "kpm", match: /^(p2-test-e2-kpm(-traffic)?|p2-kpm-real)$/,
      nodes: [{ id: 'gnb', txt: '📡 gNB (E2 agent)' }, { id: 'ric', txt: '🧠 FlexRIC' },
              { id: 'xapp', txt: '📈 xApp KPM' }, { id: 'store', txt: '💾 kpm log' }],
      edges: ['E2', 'E42', ''],
      triggers: [
        { re: /E2 SETUP|E2 Setup|assoc|conectad|connected/i, to: 'ric' },
        { re: /SUBSCRIPTION|INDICATION|KPM/i, to: 'xapp' },
        { re: /\.log|\.csv|salv|grava|arquiv|collect/i, to: 'store' },
      ] },
    { name: "rc", match: /^p2-test-e2-(rc|sm)$/,
      nodes: [{ id: 'gnb', txt: '📡 gNB (E2 agent)' }, { id: 'ric', txt: '🧠 FlexRIC' },
              { id: 'xapp', txt: '🎛 xApp' }, { id: 'ctl', txt: '⚙️ controle/SM' }],
      edges: ['E2', 'E42', ''],
      triggers: [
        { re: /E2 SETUP|E2 Setup|assoc|conectad|connected/i, to: 'ric' },
        { re: /SUBSCRIPTION|INDICATION|Service Model|E2SM/i, to: 'xapp' },
        { re: /CONTROL|\bRC\b|aplicad|applied/i, to: 'ctl' },
      ] },
    { name: "analytics", match: /^p2-kpm-analytics$/,
      nodes: [{ id: 'raw', txt: '💾 kpm bruto' }, { id: 'etl', txt: '🧪 ETL' },
              { id: 'kpi', txt: '📐 KPIs' }, { id: 'viz', txt: '📊 série/decisão' }],
      edges: ['', '', ''],
      triggers: [
        { re: /pars|lendo|leitura|ETL|extra/i, to: 'etl' },
        { re: /KPI|indicador|m[ée]dia|percentil/i, to: 'kpi' },
        { re: /CSV|sparkline|s[ée]rie|decis|relat/i, to: 'viz' },
      ] },
    { name: "kpiqoe", match: /^p2-kpi-qoe$/,
      nodes: [{ id: 'med', txt: '💾 medida KPM' }, { id: 'kpi', txt: '📐 KPI' },
              { id: 'kqi', txt: '🎯 KQI' }, { id: 'qos', txt: '📜 QoS (SLA)' },
              { id: 'cp2', txt: '🧭 QoE · CP2' }],
      edges: ['', '', '', ''],
      triggers: [
        { re: /1\. Medida|dados carregados|formato lido|amostras/i, to: 'kpi' },
        { re: /3\. KQI|KQI-1|fracao do tempo|fração do tempo/i, to: 'kqi' },
        { re: /4\. QoS|clausula|cláusula|CUMPRE|VIOLA/i, to: 'qos' },
        { re: /5\. QoE|Checkpoint 2|anatomia|Veredito/i, to: 'cp2' },
      ] },
    { name: "tema", match: /^p2-tema-/,
      nodes: [{ id: 'raw', txt: '💾 KPM (3 fases)' }, { id: 'etl', txt: '🧪 silver' },
              { id: 'kpi', txt: '📐 2 indicadores' }, { id: 'dec', txt: '🧭 recomendação' }],
      edges: ['', '', ''],
      triggers: [
        { re: /formato detectado|dados carregados|amostras/i, to: 'etl' },
        { re: /F[óo]rmulas|indicador|\bI1\b|\bI2\b/i, to: 'kpi' },
        { re: /recomend|Pol[ií]tica A1|dry-run|Veredito|regra N[ÃA]O|regra disparou|lado a lado/i, to: 'dec' },
      ] },
    { name: "ml", match: /^p2-ml-/,
      nodes: [{ id: 'data', txt: '💾 dados SUTD' }, { id: 'train', txt: '🧮 treino' },
              { id: 'metr', txt: '📊 métricas' }],
      edges: ['', ''],
      triggers: [
        { re: /trein|train|fit|Boost|Forest|MLP|model/i, to: 'train' },
        { re: /RMSE|R2|R²|acur|accur|matriz|F1|precision/i, to: 'metr' },
      ] },
    { name: "thp", match: /^test-throughput$|throughput/i,
      nodes: [{ id: 'ue', txt: '📱 UE' }, { id: 'gnb', txt: '📡 gNB' },
              { id: 'upf', txt: '🔀 UPF' }, { id: 'dn', txt: '🌐 DN (iperf3)' }],
      edges: ['N1', 'N3', 'N6'],
      triggers: [
        { re: /uesimtun|PDU|sess/i, to: 'gnb' },
        { re: /iperf|Connecting|conectand/i, to: 'upf' },
        { re: /bits\/sec|Mbits|sender|receiver/i, to: 'dn' },
      ] },
    { name: "failover", match: /^test-upf-failover$/,
      nodes: [{ id: 'ue', txt: '📱 UE' }, { id: 'upfa', txt: '🔀 UPF-A' },
              { id: 'cut', txt: '✂️ falha' }, { id: 'upfb', txt: '🔀 UPF-B' }],
      edges: ['N3', '', 'N3'],
      triggers: [
        { re: /UPF-A|upf-a|tr[áa]fego|traffic/i, to: 'upfa' },
        { re: /derrub|matando|parando|down|failover|stopping/i, to: 'cut' },
        { re: /UPF-B|upf-b|recuper|recover|voltou/i, to: 'upfb' },
      ] },
    { name: "check", match: /^(test-system-status|test-config-coherence|status)$/,
      nodes: [{ id: 'ctn', txt: '🐳 containers' }, { id: 'net', txt: '🔗 rede/config' },
              { id: 'verd', txt: '📋 veredito' }],
      edges: ['', ''],
      triggers: [
        { re: /rede|network|coer|coher|config|interface|N[234]\b/i, to: 'net' },
        { re: /resumo|resultado|conclus|veredito|summary|✅|❌/i, to: 'verd' },
      ] },
    { name: "sub", match: /^api-subscriber$|assinante/i,
      nodes: [{ id: 'cred', txt: '📝 IMSI/K/OPC' }, { id: 'dbctl', txt: '⚙️ open5gs-dbctl' },
              { id: 'store', txt: '💾 MongoDB' }],
      edges: ['', ''],
      triggers: [
        { re: /dbctl|docker exec|Adicionando|Removendo|Executando/i, to: 'dbctl' },
        { re: /inserid|adicionad|removid|sucesso|cadastrad|added|removed/i, to: 'store' },
      ] },
    { name: "chan", match: /^api-channel$|canal/i,
      nodes: [{ id: 'par', txt: '🎛 parâmetros' }, { id: 'ran', txt: '📡 UERANSIM (canal)' },
              { id: 'fx', txt: '🌐 efeito (ping)' }],
      edges: ['', ''],
      triggers: [
        { re: /UERANSIM|aplicand|apply|\btc\b|netem|delay|loss/i, to: 'ran' },
        { re: /ping|t[úu]nel|efeito|icmp|\bms\b/i, to: 'fx' },
      ] },
    { name: "a1", match: /^p2-test-a1$/,
      nodes: [{ id: 'pms', txt: '🧠 PMS (nonRT)' }, { id: 'type', txt: '📐 policy type' },
              { id: 'pol', txt: '📋 política' }, { id: 'sim', txt: '📡 a1-sim (nearRT)' }],
      edges: ['', '', 'A1'],
      triggers: [
        { re: /type 1/i, to: 'type' },
        { re: /criada via PMS|service core5g/i, to: 'pol' },
        { re: /presente no a1-sim|leitura de volta/i, to: 'sim' },
      ] },
    { name: "demo", match: /demo-e2e|Demonstra[çc][ãa]o E2E/i,
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


  // ---- Cartões didáticos: o que é · onde vive · o que tem dentro ----------
  // (clique no chip da faixa; locais são os REAIS do servidor deste lab)
  var INFOS = {
    reg: {
      ue:  { q: 'O celular simulado. Tudo começa nele: é quem pede acesso à rede.', o: 'container <b>ueransim</b> (processo nr-ue) · túnel uesimtun0', d: 'A identidade do assinante: IMSI (o "CPF" da linha) e a chave secreta K — os mesmos gravados no MongoDB.' },
      gnb: { q: 'A antena simulada. Converte o rádio do UE em sinalização para o core.', o: 'container <b>ueransim</b> (gNB) · rede docker net-n2 = interface N2', d: 'A config da célula: PLMN (operadora), TAC (área) e o endereço do AMF a quem se reporta.' },
      amf: { q: 'O "cérebro de mobilidade" do core: recebe o registro e coordena a autenticação.', o: 'container <b>open5gs-amf-containerized</b> · NGAP/SCTP porta 38412', d: 'O contexto de cada UE registrado: quem está conectado, em que área, com que sessão.' },
      sec: { q: 'Os cofres de identidade: AUSF autentica, UDM/UDR guardam o perfil.', o: 'containers <b>open5gs-ausf/udm/udr</b> + MongoDB', d: 'As credenciais 5G-AKA (K/OPc) e o perfil do assinante — a prova de identidade acontece SEM a chave viajar pela rede.' },
    },
    kpm: {
      gnb:  { q: 'O gNB real (OAI) com o agente E2 embutido — ele CONTA o que vê ao RIC.', o: 'processo nativo <b>nr-softmodem</b> · log em oai-cn-gnb-e2/logs/gnb_oai.log', d: 'Métricas por UE a cada ~1 s: throughput, PRBs em uso, atraso — a matéria-prima do KPM.' },
      ric:  { q: 'O near-RT RIC (FlexRIC): roteia assinaturas e indicações entre gNB e xApps.', o: 'processo nativo <b>nearRT-RIC</b> · E2AP porta 36421/SCTP', d: 'As subscriptions ativas: quem pediu qual métrica, de qual gNB, com que período.' },
      xapp: { q: 'O aplicativo que consome as métricas — a "inteligência" plugável do RIC.', o: 'xapp_kpm_moni (exemplo C do FlexRIC), no host', d: 'As INDICATIONs decodificadas: measName = valor, UE a UE — que ele escreve no log.' },
      store:{ q: 'O momento do armazenamento: métricas viram ARQUIVO — nasce o dado bruto.', o: '<b>oai-cn-gnb-e2/logs/xapp_kpm_moni.log</b> (e kpm_timeseries.csv após o ETL)', d: 'Texto puro, 1 linha por medição — o "bronze" do nosso mini-lake, insumo da disciplina de dados.' },
    },
    rc: {
      gnb:  { q: 'O gNB com agente E2 — desta vez recebendo COMANDOS, não só reportando.', o: 'processo nativo <b>nr-softmodem</b>', d: 'Os Service Models E2SM-RC: as "alavancas" que o RIC pode puxar (ex.: forçar um attach).' },
      ric:  { q: 'O FlexRIC roteando o ciclo completo: observar E agir.', o: 'processo nativo <b>nearRT-RIC</b> · porta 36421', d: 'O par SUBSCRIPTION (ouvir) + CONTROL (mandar) da mesma sessão E2.' },
      xapp: { q: 'O xApp de controle: decide e envia o comando de volta.', o: 'exemplos C do FlexRIC (xapp_kpm_rc)', d: 'A lógica se-então do loop rápido: métrica entra, comando sai — em menos de 1 s.' },
      ctl:  { q: 'O efeito no RAN: o comando aplicado no gNB.', o: 'de volta ao <b>nr-softmodem</b>, via E2', d: 'A confirmação do CONTROL — o laço observar→decidir→agir fechado, visível no log.' },
    },
    analytics: {
      raw: { q: 'O log KPM bruto — o que o xApp escreveu durante a coleta.', o: '<b>oai-cn-gnb-e2/logs/xapp_kpm_moni.log</b>', d: 'Linhas de texto "measName = valor unidade" — ilegível para análise; perfeito como matéria-prima.' },
      etl: { q: 'A faxina: Extrair, Transformar, Carregar — texto vira tabela.', o: 'script <b>kpm_analytics.sh</b> (awk/python), no host', d: 'Parse de cada linha → série temporal estruturada (time, measName, valor, UE, slice).' },
      kpi: { q: 'A agregação: milhares de amostras viram POUCOS números que informam decisão.', o: 'calculado em memória pelo script', d: 'Throughput médio/máx por UE, ocupação de PRB — os KPIs (aula 04 da disciplina!).' },
      viz: { q: 'O resultado visível: a forma do tráfego no tempo.', o: '<b>logs/kpm_timeseries.csv</b> + sparkline ASCII no console', d: 'O CSV final — o mesmo insumo que alimentaria um UE-TP-rApp de verdade.' },
    },
    kpiqoe: {
      med: { dataKey: 'kpm', q: 'A medida crua do E2SM-KPM — o que a rede REPORTA, antes de virar indicador. KPM ≠ KPI (slide 17 da aula 04).', o: 'servidor: <b>oai-cn-gnb-e2/scripts/temas/samples/</b> (ou o arquivo que você enviou no cartão 💾)', d: 'RRU.PrbTotUl (%), DRB.UEThpUl (kbps), DRB.RlcSduDelayDl (µs) por amostra, com a fase (baseline · stress · recovery). Sem RSRP/SINR/CQI: canal do UE não está no artefato.' },
      kpi: { q: 'O KPI: desempenho da REDE. Média e p95 de PRB, mediana e p95 de vazão e de atraso, por fase.', o: 'GROUP BY fase em <b>scripts/temas/aula04_indicadores.py</b> (só biblioteca padrão)', d: 'A fórmula do slide sai impressa antes do número, e a escolha da agregação (mediana × média × p95) é justificada — o deck cobra isso no CP2.' },
      kqi: { q: 'O KQI: qualidade do SERVIÇO. A fração do tempo com atraso acima do limiar L — a série vira indicador de qualidade.', o: 'n(delay > L) / n por fase; L ajustável por <b>A04_DELAY_L</b>', d: 'L é limiar de MUDANÇA DE REGIME calibrado no baseline (slide 44: sem limiar justificado não há KQI formal), não requisito de aplicação.' },
      qos: { q: 'QoS: o KQI confrontado com o contrato. 4 cláusulas didáticas (latência, vazão, capacidade, qualidade) por fase.', o: 'alvos calibrados no baseline (p95 × folga) ou na referência do slide 35 (PRB > 80% = ruim)', d: 'Cláusula violada só na fase de carga = evidência; violada também no baseline = o limiar está errado, não a rede. Não há 5QI nem QoS Flow no artefato.' },
      cp2: { q: 'QoE é só PROXY aqui (não existe MOS no lab) — e a saída termina na anatomia de cada indicador, que é o entregável do Checkpoint 2.', o: 'nome · fórmula · unidade · granularidade · fonte · alvo/limiar · interpretação · papel · limite de validade', d: 'Também mostra o diagnóstico capacidade × canal/jammer e quais das 6 famílias de KPI o artefato NÃO permite medir.' },
    },
    tema: {
      raw: { dataKey: 'kpm', q: 'A telemetria KPM do lab do professor (kpm-ue-tp-sample): 100 medições em 3 fases (baseline 20 · stress 60 · recovery 20). Os MESMOS dados para os 7 grupos — muda a pergunta.', o: 'servidor: <b>oai-cn-gnb-e2/scripts/temas/samples/</b> · original: submódulo cesar-school-repo/data/code/datasets/kpm-ue-tp-sample/', d: '1 linha = 1 medição: DRB.UEThpUl (vazão UL, kbps), DRB.RlcSduDelayDl (atraso DL, µs), RRU.PrbTotUl (% de PRB) + fase, run_id, sample_index.' },
      etl: { q: 'A zona silver: cada linha tipada e ordenada por fase e sample_index — o mini-lake da Aula 02.', o: 'em memória, no <b>scripts/temas/temas_projeto.py</b> (só biblioteca padrão)', d: 'Contagem por fase, unidades por convenção KPM e os limiares derivados dos dados (PRB alto, vazão baixa, atraso máximo).' },
      kpi: { q: 'Os 2 indicadores obrigatórios do card do tema — a fórmula é impressa ANTES do número.', o: 'GROUP BY fase, percentis, correlação de Pearson, MAD, médias móveis', d: 'Tabelas por fase (média, mediana, p95, %), correlação global × dentro da fase, score de anomalia (robust-baseline-mad, o mesmo do model.json).' },
      dec: { q: 'A recomendação: uma política A1 candidata em DRY-RUN — nada é aplicado na RAN.', o: 'JSON no formato do decision.json do professor (policy_data.scope / qosObjectives)', d: 'Se a regra do tema disparou, o motivo; se não disparou, por que não (a leitura honesta) — e as limitações.' },
    },
    ml: {
      data: { dataKey: 'sutd', q: 'Medições REAIS de campo: o walk test 5G da universidade SUTD (Singapura) — material da disciplina \u201cAplicações de IA e ML em RIC\u201d do Prof. Julio C. C. Tesolin (CESAR School).', o: 'servidor: <b>oai-cn-gnb-e2/scripts/ml/</b> · cópia aberta no repo: pdfs/02-ric-ai/casos-artigo/data/sutd/', d: 'CSVs com RSRP, RSRQ, SINR, PRB e throughput medidos andando pelos andares 4/5/6 — cada linha é um instante rotulado.' },
      train:{ q: 'O treino: o modelo aprende o padrão que liga as medições ao alvo.', o: 'script <b>scripts/ml/*_experiment.py</b> (numpy puro, sem GPU), no host', d: 'Split temporal (passado treina, futuro testa — nunca o contrário!) e os modelos: Gradient Boosting, Random Forest, MLP…' },
      metr: { q: 'O boletim do modelo: quão bem ele prevê o que nunca viu.', o: 'impresso no console (e salvo no Histórico do painel)', d: 'RMSE/R² (regressão) ou acurácia/matriz de confusão (classificação) — compare com a tabela do artigo NGO et al. 2024.' },
    },
    thp: {
      ue:  { q: 'O celular simulado gerando tráfego de verdade.', o: 'container <b>ueransim</b> · túnel uesimtun0 (o "chip" com IP)', d: 'O cliente iperf3 empurrando bytes — como um download real.' },
      gnb: { q: 'A antena: todo byte do UE passa por ela antes do core.', o: 'container <b>ueransim</b> (gNB)', d: 'O encapsulamento do tráfego rumo ao UPF (GTP-U, rede net-n3).' },
      upf: { q: 'A "rodovia" do plano de usuário: encaminha pacotes, não os interpreta.', o: 'container <b>open5gs-upf-containerized-a</b> · redes N3/N6', d: 'As regras de encaminhamento da sessão PDU criadas pelo SMF via N4.' },
      dn:  { q: 'O "resto da internet" do lab: o destino do tráfego.', o: 'container <b>open5gs-dn-containerized</b> · servidor iperf3', d: 'O medidor: conta os bits/s que chegaram — o throughput impresso no resultado.' },
    },
    failover: {
      ue:   { q: 'O celular com uma sessão de dados ativa — a "vítima" do teste.', o: 'container <b>ueransim</b>', d: 'Tráfego contínuo que NÃO deveria cair quando o UPF morrer.' },
      upfa: { q: 'O UPF titular, por onde o tráfego corre primeiro.', o: 'container <b>open5gs-upf-containerized-a</b>', d: 'A sessão PDU ativa — até o teste derrubá-lo de propósito.' },
      cut:  { q: 'A falha proposital: o teste MATA o UPF-A para ver a rede reagir.', o: 'docker stop no upf-a (caos controlado)', d: 'O instante didático: resiliência não se assume, se TESTA.' },
      upfb: { q: 'O reserva assume: CUPS permite trocar o plano de usuário sem derrubar o controle.', o: 'container <b>open5gs-upf-containerized-b</b>', d: 'A sessão re-ancorada — o tráfego volta por outro caminho.' },
    },
    check: {
      ctn:  { q: 'A chamada de presença: quais containers estão de pé.', o: '<b>docker ps</b> no servidor', d: 'Estado e saúde de cada NF (running/healthy) — o primeiro suspeito de qualquer problema.' },
      net:  { q: 'A vistoria das estradas: as redes docker que representam as interfaces 3GPP.', o: 'redes <b>net-n2/n3/n4/n6/sbi</b>', d: 'Cada rede = uma interface real (N2, N3…) — se a rede sumiu, a interface caiu.' },
      verd: { q: 'O veredito: o resumo acionável da checagem.', o: 'impresso no console (e no Histórico)', d: 'OK/falha por item — o que um NOC olharia antes de escalar.' },
    },
    sub: {
      cred: { q: 'A identidade do novo assinante que você digitou.', o: 'formulário do UE Lab → API do painel', d: 'IMSI (15 dígitos), chave K e OPc (32 hex cada) — o "contrato" da linha.' },
      dbctl:{ q: 'O cartório: a ferramenta oficial do Open5GS para gravar assinantes.', o: 'script <b>add-subscriber.sh</b> → open5gs-dbctl dentro do container', d: 'O comando de INSERT validado — nada de mexer no banco na mão.' },
      store:{ q: 'O banco de assinantes do core — o HSS/UDR na prática.', o: 'container <b>open5gs-mongodb-containerized</b> · collection subscribers', d: 'O documento JSON do assinante: IMSI, chaves, QoS — o que o AMF consulta no registro.' },
    },
    chan: {
      par: { q: 'As condições de rádio que você escolheu simular (distância/interferência).', o: 'seletores do UE Lab → API do painel', d: 'Um par (distância, interferência) que vira parâmetros de rede reais.' },
      ran: { q: 'A degradação aplicada: o lab usa controle de tráfego Linux para "piorar o ar".', o: '<b>tc/netem</b> dentro do container ueransim', d: 'Delay, perda e banda impostos ao túnel — física simulada com ferramentas de rede.' },
      fx:  { q: 'A prova do efeito: o ping sente o canal novo.', o: 'ping do UE ao DN pelo túnel uesimtun0', d: 'O RTT antes × depois — a latência conta a história da distância.' },
    },
    a1: {
      pms:  { q: 'O Non-RT RIC: a camada de POLÍTICAS (loop lento, > 1 s) que construímos em ARM64.', o: 'container <b>nonrt-policy-agent</b> · API REST :8081/a1-policy/v2', d: 'Os services e políticas A1 registrados — decisões de gestão, não comandos de rádio.' },
      type: { q: 'O policy type: o CONTRATO da política — que campos ela pode ter.', o: '<b>server/nonrt-ric/testdata/policy_type.json</b> (o mesmo do lab do docente)', d: 'Um JSON Schema: scope (a quem se aplica) + qosObjectives (o que pedir). Política fora do schema é rejeitada.' },
      pol:  { q: 'A política em si: uma INSTÂNCIA do contrato, com valores concretos.', o: 'criada via PUT no PMS → desce pelo A1', d: 'ueId + qosObjectives (ex.: priorityLevel) — "trate este usuário assim".' },
      sim:  { q: 'O near-RT que recebe a política — aqui, um simulador (o FlexRIC não tem porta A1).', o: 'container <b>a1-sim-OSC</b> · :30001', d: 'O estado A1 do "near-RT": types e políticas aceitas — a prova de que a política DESCEU.' },
    },
    demo: {
      ue:   { q: 'O celular simulado — protagonista da demonstração fim-a-fim.', o: 'container <b>ueransim</b>', d: 'Registro + sessão + tráfego, na sequência — a jornada completa em um clique.' },
      gnb:  { q: 'A antena: rádio vira rede.', o: 'container <b>ueransim</b> (gNB)', d: 'N1/N2 para o controle, N3 para os dados.' },
      upf:  { q: 'O plano de usuário encaminhando o tráfego da demo.', o: 'container <b>open5gs-upf-containerized-a</b>', d: 'A sessão PDU ativa da demonstração.' },
      dn:   { q: 'A "internet" do lab: destino do ping e do iperf3.', o: 'container <b>open5gs-dn-containerized</b>', d: 'Conectividade real comprovada — não é mock.' },
      metr: { q: 'A medição que fecha a demo: número, não promessa.', o: 'iperf3 no DN, resultado no relatório de passos', d: 'O throughput medido — a prova de que a rede 5G inteira funcionou.' },
    },
  };

  // Tooltips das colunas dos datasets (passa o mouse no cabeçalho da amostra)
  var COLTIPS = {
    'Time': 'Instante da medição (série temporal — nunca embaralhar!)',
    'NR-ARFCN': 'Canal de rádio 5G NR (número absoluto da frequência)',
    'PCI': 'Physical Cell ID — identidade física da célula servidora',
    '_oid': 'ID interno do registro (gerado na coleta)',
    'RSRP': 'Potência do sinal de referência recebido (dBm) — quanto maior, melhor o sinal',
    'RSRQ': 'Qualidade do sinal de referência (dB) — potência descontando interferência',
    'SINR': 'Relação sinal/(interferência+ruído) (dB) — o quão "limpo" o canal está',
    'PDSCH_MCS': 'Esquema de modulação/codificação no downlink (0-28: maior = mais bits/símbolo)',
    'PUSCH_MCS': 'Esquema de modulação/codificação no uplink',
    'PDSCH PRBs': 'Blocos de recurso (PRB) alocados no downlink — quanto do espectro o UE usa',
    'PUSCH PRBs': 'Blocos de recurso alocados no uplink',
    'throughput_DL': 'Vazão de dados no downlink — O ALVO da previsão UE-TP',
    'C-RNTI': 'Identidade temporária do UE na célula',
    'Corridor_tag': 'Marcação do trecho do corredor no walk test',
    'lab_anom': 'Rótulo: houve anomalia induzida neste instante?',
    'lab_bs': 'Rótulo: estação base do experimento',
    'lab_inf': 'Rótulo: interferência ativa?',
    'lab_1rr': 'Rótulo: cenário com apenas 1 RRU ligada',
    'Label': 'Rótulo-alvo da classificação (ex.: andar / anomalia)',
  };

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
    strip.className = 'fs-strip on superficie-escura';
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
      d.className = 'fs-node' + (n.info ? ' hasinfo' : '');
      d.textContent = n.txt;
      if (n.info) {
        var ic = document.createElement('i'); ic.textContent = 'ⓘ'; d.appendChild(ic);
        d.title = 'clique: o que é, onde vive e o que tem dentro';
        (function (nn, dd) { dd.onclick = function () { openPop(nn, dd); }; })(n, d);
      }
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
      var base = 'fs-node' + (cur.scene.nodes[i].info ? ' hasinfo' : '');
      n.className = base + (i < pos ? ' done' : i === pos ? ' active' : '');
    });
    cur.els.edges.forEach(function (e, i) {
      // aresta i liga nó i ao nó i+1
      e.className = 'fs-edge' + (i < pos - 1 ? ' done' : i === pos - 1 ? ' active' : '');
    });
  }

  function begin(key, mountName) {
    closePop();
    end0();                                    // fecha faixa de execução anterior
    var host = mounts[mountName];
    if (!host || !key) return;
    var scene = null;
    for (var i = 0; i < SCENES.length; i++) {
      if (SCENES[i].match.test(String(key))) { scene = SCENES[i]; break; }
    }
    if (!scene) { host.innerHTML = ''; return; }
    var inf = INFOS[scene.name] || {};
    scene.nodes.forEach(function (n) { if (inf[n.id]) n.info = inf[n.id]; });
    cur = { scene: scene, host: host, els: render(scene, host), pos: 0, fired: [] };
    setPos(0);
    if (mountName === 'console' && window.MiniMap) MiniMap.begin(scene.name);
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
      cur.els.nodes.forEach(function (n, i) {
        n.className = 'fs-node' + (cur.scene.nodes[i].info ? ' hasinfo' : '') + ' done';
      });
      cur.els.edges.forEach(function (e) { e.className = 'fs-edge done'; });
      cur.els.result.textContent = '✔';
      cur.els.result.className = 'fs-result ok';
      if (window.MiniMap) MiniMap.end(true);
    } else {
      var n = cur.els.nodes[cur.pos];
      if (n) n.className = 'fs-node' + (cur.scene.nodes[cur.pos].info ? ' hasinfo' : '') + ' fail';
      var e = cur.els.edges[cur.pos - 1];
      if (e) e.className = 'fs-edge';
      cur.els.result.textContent = '✖';
      cur.els.result.className = 'fs-result fail';
      if (window.MiniMap) MiniMap.end(false);
    }
    cur = null;   // faixa fica visível com o desfecho até a próxima execução
  }

  // ---- Fonte dos dados (funções de ML): sugerida × CSV do professor -------
  // Por chave de dado: o texto do cartão muda, o mecanismo é o mesmo (GET
  // /api/lab-data/{key}, POST .../source, POST .../upload com o corpo cru).
  var SRC = {
    sutd: { def: 'o dataset SUTD original (4 cenários do walk test) descrito no cartão acima — reproduz o artigo.',
            cus: 'mesmas colunas do exemplo; seu CSV vira os 4 cenários.', accept: '.csv', paste: false,
            foot: '4 cenários no servidor · disciplina do Prof. Julio C. C. Tesolin' },
    kpm:  { def: 'a amostra oficial do professor (kpm-ue-tp-sample): 100 medições em 3 fases — a mesma dos 7 grupos.',
            cus: 'JSONL (formato do professor) ou CSV com thp_ul, delay_dl, prb_ul e, se tiver, phase. Sem fase, as primeiras 20% viram baseline.',
            accept: '.csv,.jsonl,.json,.txt', paste: true,
            foot: 'amostra do professor · disciplina Análise de Dados (Prof. Jonas A. Kunzler)' },
  };
  function srcHtml(key) {
    var s = SRC[key] || SRC.sutd;
    return '<div class="sec">Fonte dos dados desta função</div><div class="fs-src">'
      // Cada opção é uma linha só: rádio + rótulo (que pode quebrar) + ação à
      // direita (que nunca quebra). Antes o texto solto virava item flex e
      // quebrava palavra a palavra.
      + '<label class="opt"><input type="radio" name="fsrc" value="default">'
      +   '<span class="lbl">1. Sugerida pelo servidor</span>'
      +   '<a href="#" class="see act">👁 ver amostra</a></label>'
      + '<div class="exp">' + s.def + '</div>'
      + '<div class="smp" style="display:none;margin:5px 0 4px 20px;max-width:345px;overflow-x:auto;border:1px solid var(--line);border-radius:6px"></div>'
      + '<label class="opt"><input type="radio" name="fsrc" value="custom">'
      +   '<span class="lbl">2. Meus dados</span><span class="st act"></span></label>'
      + '<div class="exp">' + s.cus + ' '
      + '<a href="/api/lab-data/' + key + '/example" download>⬇ baixe o exemplo aqui</a></div>'
      + '<div class="how"><span class="hk">arquivo</span><input type="file" accept="' + s.accept + '"></div>'
      + (s.paste
          ? '<div class="how"><span class="hk">colar</span>'
            + '<textarea class="paste" rows="4" spellcheck="false" placeholder="thp_ul,delay_dl,prb_ul,phase\n3.7,0,2,baseline\n80023.7,158.9,99,stress"></textarea>'
            + '<button type="button" class="pastebtn">⬆ Usar o que colei</button></div>'
          : '')
      + '</div>';
  }
  function wireSrc(card, key) {
    var radios = card.querySelectorAll('input[name=fsrc]');
    var file = card.querySelector('input[type=file]');
    var st = card.querySelector('.st');
    function refresh() {
      fetch('/api/lab-data/' + key).then(function (r) { return r.json(); }).then(function (d) {
        radios.forEach(function (r) { r.checked = (r.value === d.source); });
        radios[1].disabled = !d.has_custom;
        st.textContent = d.has_custom ? (d.source === 'custom' ? '● em uso' : '(enviado)') : '';
      }).catch(function () {});
    }
    radios.forEach(function (r) {
      r.onchange = function () {
        fetch('/api/lab-data/' + key + '/source', { method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ source: r.value }) })
          .then(function (resp) { if (!resp.ok) return resp.json().then(function (e) { alert(e.detail || 'sem permissão'); }); })
          .then(refresh);
      };
    });
    var see = card.querySelector('.see'), smp = card.querySelector('.smp');
    if (see) see.onclick = function (e) {
      e.preventDefault();
      if (smp.style.display === 'block') { smp.style.display = 'none'; return; }
      smp.innerHTML = '<div style="padding:6px 9px;color:var(--ink-3);font-size:10px">carregando…</div>'; smp.style.display = 'block';
      fetch('/api/lab-data/' + key + '/example').then(function (r) { return r.text(); })
        .then(function (txt) {
          var lines = txt.trim().split('\n').filter(function (l) { return l.trim(); });
          var cols = lines[0].split(',');
          var html = '<table style="border-collapse:collapse;font-size:9px;font-family:\'SF Mono\',Menlo,monospace"><tr>'
            + cols.map(function (c) {
                var tip = COLTIPS[c.trim()] || 'coluna do dataset';
                return '<th title="' + tip.replace(/"/g, '&quot;') + '" style="padding:4px 7px;background:var(--surface);color:var(--accent-text);border-bottom:1px solid var(--line);white-space:nowrap;cursor:help;text-align:left">' + c + ' <span style="opacity:.4">ⓘ</span></th>';
              }).join('') + '</tr>'
            + lines.slice(1).map(function (l) {
                return '<tr>' + l.split(',').map(function (v) {
                  return '<td style="padding:3px 7px;color:var(--ink-2);border-bottom:1px solid var(--surface);white-space:nowrap">' + v + '</td>';
                }).join('') + '</tr>';
              }).join('')
            + '</table><div style="padding:5px 9px;color:var(--ink-3);font-size:9.5px">⋮ primeiras linhas · passe o mouse nos cabeçalhos · ' + ((SRC[key] || SRC.sutd).foot) + '</div>';
          smp.innerHTML = html;
        })
        .catch(function () { smp.innerHTML = '<div style="padding:6px 9px;color:var(--bad-text);font-size:10px">falhou ao carregar</div>'; });
    };
    function upload(txt) {
      st.textContent = 'enviando…';
      return fetch('/api/lab-data/' + key + '/upload', { method: 'POST',
        headers: { 'Content-Type': 'text/plain' }, body: txt })
        .then(function (resp) {
          if (!resp.ok) return resp.json().then(function (e) { st.textContent = ''; alert(e.detail || 'falhou'); });
          refresh();
        });
    }
    file.onchange = function () {
      var fl = file.files && file.files[0]; if (!fl) return;
      fl.text().then(upload);
    };
    var pb = card.querySelector('.pastebtn'), ta = card.querySelector('textarea.paste');
    if (pb && ta) pb.onclick = function () {
      var txt = (ta.value || '').trim();
      if (!txt) { alert('cole os dados primeiro (cabeçalho + linhas)'); return; }
      upload(txt + '\n');
    };
    refresh();
  }

  function attach(name, el) { if (el) mounts[name] = el; }

  // ---- popover didático: o que é · onde vive · o que tem dentro ----
  var pop = null;
  function closePop() {
    if (pop) { pop.back.remove(); pop.card.remove(); pop = null; }
  }
  function openPop(node, anchorEl) {
    closePop();
    var back = document.createElement('div');
    back.className = 'fs-back';
    back.onclick = closePop;
    var c = document.createElement('div');
    c.className = 'fs-pop';
    c.innerHTML = '<span class="x">✕</span><h4>' + node.txt + '</h4>'
      + '<div class="sec">O que é</div><div>' + node.info.q + '</div>'
      + '<div class="sec">Onde vive</div><div><code>' + node.info.o + '</code></div>'
      + '<div class="sec">O que tem dentro</div><div>' + node.info.d + '</div>'
      + (node.info.dataKey ? srcHtml(node.info.dataKey) : '')
      + '<div class="hint">💡 Enquanto o teste roda, o log abaixo é esta operação acontecendo — a faixa mostra POR ONDE o dado passa; o log mostra O QUE ele diz.</div>';
    document.body.appendChild(back);
    document.body.appendChild(c);
    c.querySelector('.x').onclick = closePop;
    if (node.info.dataKey) wireSrc(c, node.info.dataKey);
    var r = anchorEl.getBoundingClientRect();
    var top = r.bottom + 8, left = Math.max(8, Math.min(r.left, window.innerWidth - 406));
    if (top + c.offsetHeight > window.innerHeight - 8) top = Math.max(8, r.top - c.offsetHeight - 8);
    c.style.top = top + 'px'; c.style.left = left + 'px';
    pop = { back: back, card: c };
  }
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closePop(); });

  injectCss();
  // Briefing pré-teste: mini-topologia VIVA da cena (todas as arestas animando)
  function preview(key, hostEl) {
    var scene = null;
    for (var i = 0; i < SCENES.length; i++) if (SCENES[i].match.test(String(key))) { scene = SCENES[i]; break; }
    if (!scene) { hostEl.innerHTML = ''; return null; }
    var inf = INFOS[scene.name] || {};
    scene.nodes.forEach(function (n) { if (inf[n.id]) n.info = inf[n.id]; });
    var els = render(scene, hostEl);
    els.nodes.forEach(function (n, i) { n.className = 'fs-node' + (scene.nodes[i].info ? ' hasinfo' : '') + ' done'; });
    els.edges.forEach(function (e) { e.className = 'fs-edge active'; });
    els.result.textContent = '';
    return scene;
  }
  function sceneName(key) {
    for (var i = 0; i < SCENES.length; i++) if (SCENES[i].match.test(String(key))) return SCENES[i].name;
    return null;
  }
  function sceneInfo(key) {
    var scene = null;
    for (var i = 0; i < SCENES.length; i++) if (SCENES[i].match.test(String(key))) { scene = SCENES[i]; break; }
    if (!scene) return [];
    var inf = INFOS[scene.name] || {};
    return scene.nodes.map(function (n) { return { txt: n.txt, o: (inf[n.id] || {}).o || '' }; });
  }
  window.FlowStrip = { attach: attach, begin: begin, feed: feed, end: end, preview: preview, sceneInfo: sceneInfo, sceneName: sceneName };
})();
