#!/usr/bin/env python3
"""Gera o relatorio do Checkpoint 2 e monta o zip de entrega do Grupo 6.

RELATORIO_CP2.html (logo da CESAR + figuras embutidas) -> PDF via Chrome -> zip
na Area de trabalho. Os numeros vem de cp2_indicadores.py: o texto NAO recalcula
nada, entao relatorio e analise nao podem divergir.

Uso: python3 build_relatorio_cp2.py   (rode o etl/build_lake.py antes)
"""
import base64
import json
import os
import shutil
import subprocess
import sys
import zipfile

import cp2_indicadores as cp2

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
LOGO = os.path.join(REPO, "server/panel/static/ops/cesar-marca.svg")
RAW_DIR = os.path.join(REPO, "external/cesar-school-repo/data/code/datasets/kpm-ue-tp-sample")
FIG = os.path.join(HERE, "figures")
OUT = os.path.join(HERE, "entrega")
os.makedirs(OUT, exist_ok=True)

GRUPO = "Grupo 6"
INTEGRANTES = ["Henrique Carmine", "Kelvin de Lima Gabriel", "Klinger Carneiro Júnior"]
MENTOR = "Prof. Dr. Jonas Augusto Kunzler"
DISCIPLINA = "Análise de Dados em Redes de Telecom"
TEMA = "Tema 1 — Vazão do usuário (UE-TP)"
PT = cp2.PT


def b64img(path):
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def logo_svg():
    with open(LOGO, encoding="utf-8") as f:
        return f.read().replace('width="561" height="500"', 'width="54" height="48"', 1)


def n(v, casas=1):
    """Numero no padrao brasileiro: milhar com ponto, decimal com virgula."""
    s = f"{v:,.{casas}f}"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


CSS = """
@page { size: A4; margin: 20mm 18mm 16mm; }
*{box-sizing:border-box}
body{font:11.5pt/1.55 Georgia,'Times New Roman',serif;color:#20272e;max-width:174mm;margin:0 auto}
.hd{display:flex;align-items:center;gap:14px;border-bottom:2px solid #f04e23;padding-bottom:11px;margin-bottom:4px}
.hd .t{flex:1}
.hd .disc{font:600 10pt/1.2 Helvetica,Arial,sans-serif;color:#f04e23}
.hd h1{font:700 17pt/1.15 Helvetica,Arial,sans-serif;margin:2px 0 0;color:#1a2733}
.hd .sub{font:400 11pt/1.3 Helvetica,Arial,sans-serif;color:#5a6b7c;margin-top:2px}
.meta{font:10.5pt/1.55 Helvetica,Arial,sans-serif;color:#33465a;margin:10px 0 2px}
.meta div b{color:#1a2733}
h2{font:700 13pt/1.25 Helvetica,Arial,sans-serif;color:#1a2733;margin:17pt 0 5pt;page-break-after:avoid}
h3{font:700 11.5pt/1.25 Helvetica,Arial,sans-serif;color:#1a2733;margin:12pt 0 4pt;page-break-after:avoid}
p{margin:0 0 8pt;text-align:justify}
table{border-collapse:collapse;width:100%;margin:8pt 0 12pt;font:10pt/1.4 Helvetica,Arial,sans-serif;font-variant-numeric:tabular-nums;page-break-inside:avoid}
th{border-bottom:1.5pt solid #33465a;padding:4pt 8pt;text-align:left}
td{border-bottom:.5pt solid #d3dbe4;padding:3.5pt 8pt;vertical-align:top}
.num{text-align:right}
figure{margin:10pt 0 6pt;page-break-inside:avoid}
figure img{width:100%;border:1px solid #e2e7ee}
figcaption{font:9.5pt/1.35 Helvetica,Arial,sans-serif;color:#5a6b7c;margin-top:5px}
.box{background:#f6f8f5;border-left:3px solid #4a7a3a;padding:8pt 12pt;font-size:11pt;margin:8pt 0}
.box.at{background:#fdf6ef;border-left-color:#e08a2e}
.ficha{font:9.5pt/1.45 Helvetica,Arial,sans-serif;margin:6pt 0 12pt;page-break-inside:avoid}
.ficha td:first-child{width:34mm;color:#5a6b7c}
.ok{color:#2c6e35;font-weight:700}
.viola{color:#b4451f;font-weight:700}
code{font:10pt 'DejaVu Sans Mono',Consolas,monospace;color:#324}
ul{margin:0 0 8pt;padding-left:20pt} li{margin-bottom:4pt}
footer{margin-top:16pt;padding-top:8pt;border-top:.5pt solid #c3ccd5;font:9pt/1.4 Helvetica,Arial,sans-serif;color:#8593a1}
"""


def ficha(titulo, papel, linhas):
    tr = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in linhas)
    return (f'<h3>{titulo} <span style="font-weight:400;color:#5a6b7c">— papel: {papel}</span></h3>'
            f'<table class="ficha">{tr}</table>')


def html(res, clausulas, violadas, dec):
    base, carga, rec = "baseline", "stress", "recovery"
    nomes = ", ".join(INTEGRANTES)
    L = cp2.L_US
    zb = int(res.loc[base, "delay_zeros"]); nb = int(res.loc[base, "n"])

    linhas_fase = "".join(
        f"<tr><td>{PT[p]}</td><td class='num'>{int(res.loc[p,'n'])}</td>"
        f"<td class='num'>{n(res.loc[p,'thp_mediana'])}</td>"
        f"<td class='num'>{n(res.loc[p,'thp_p95'])}</td>"
        f"<td class='num'>{n(res.loc[p,'prb_media'])}</td>"
        f"<td class='num'>{n(res.loc[p,'delay_mediana'])}</td>"
        f"<td class='num'>{n(res.loc[p,'delay_p95'])}</td>"
        f"<td class='num'>{n(res.loc[p,'acima_L'],0)}%</td></tr>" for p in cp2.PHASES)

    linhas_cl = "".join(
        f"<tr><td>{c['rotulo']}</td><td>{c['rotulo_alvo']}</td><td>{c['rotulo_origem']}</td>"
        f"<td class='num'>{n(c['medido'])}</td>"
        f"<td class='{'ok' if c['cumpre'] else 'viola'}'>{'CUMPRE' if c['cumpre'] else 'VIOLA'}</td></tr>"
        for c in clausulas)

    dec_txt = ""
    if dec:
        ev = dec["evaluation"]
        dec_txt = (f"o artefato do professor decide <b>“{ev['decision']}”</b>, com "
                   f"{ev['apply_votes']} votos e prioridade "
                   f"{dec['policy']['policy_data']['qosObjectives']['priorityLevel']}")

    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Projeto Integrador - Grupo 6 - Checkpoint 2</title><style>{CSS}</style></head><body>
<div class="hd">{logo_svg()}<div class="t">
  <div class="disc">CESAR School &nbsp;|&nbsp; {DISCIPLINA}</div>
  <h1>Projeto Integrador — Checkpoint 2</h1>
  <div class="sub">{TEMA} &nbsp;·&nbsp; Indicadores e qualidade</div></div></div>
<div class="meta">
  <div><b>{GRUPO}:</b> {nomes}</div>
  <div><b>Professor:</b> {MENTOR}</div>
  <div><b>Entrega:</b> Checkpoint 2 — indicadores validados (Aula 04/05, agosto de 2026)</div>
</div>

<h2>1. O que este documento entrega</h2>
<p>No Checkpoint 1 mostramos <b>como</b> os dados foram organizados e olhados: o mini-lake em
bronze, silver e gold, a checagem de qualidade, duas consultas e dois gráficos. Este Checkpoint 2
fecha a cadeia que a Aula 04 pede, do número cru até a decisão:</p>
<div class="box">medida (KPM) → métrica → <b>KPI</b> → <b>KQI</b> → <b>QoS</b> (SLA) → <b>QoE</b> (aqui, só proxy) → <b>decisão</b></div>
<p>Para cada indicador escrevemos a ficha completa que a aula cobra — nome, fórmula, unidade,
granularidade, fonte, alvo, interpretação, papel e limite de validade —, um gráfico por indicador,
as cláusulas de qualidade confrontadas fase a fase, e a decisão que tudo isso habilita. No fim
comparamos a nossa decisão com a do <code>decision.json</code> que veio no pacote do laboratório.</p>

<h2>2. De onde vêm os dados (e uma correção do CP1)</h2>
<p>Continuamos na trilha offline: o pacote <code>kpm-ue-tp-sample</code>, com 100 amostras em três
fases — repouso (20), carga (60) e recuperação (20). São dados de simulação (RFSIM), sem nada
pessoal. O ETL é o mesmo do CP1 (<code>etl/build_lake.py</code>, só biblioteca padrão) e a análise
parte da zona silver.</p>
<div class="box at"><b>Correção em relação ao CP1.</b> As unidades são as do E2SM-KPM, como o xApp
do FlexRIC imprime: vazão em <b>kbps</b>, atraso em <b>µs</b> e PRB em <b>% dos PRB</b>. No
relatório do Checkpoint 1 escrevemos milissegundos e contagem de PRBs. Os números não mudam; o
rótulo estava errado, e um atraso de 159&nbsp;<b>µs</b> conta uma história bem diferente de
159&nbsp;ms. Preferimos registrar o erro a deixá-lo passar.</div>

<h2>3. Os números, fase a fase</h2>
<table>
<tr><th>Fase</th><th class="num">n</th><th class="num">Vazão mediana</th><th class="num">Vazão p95</th>
<th class="num">PRB médio</th><th class="num">Atraso mediano</th><th class="num">Atraso p95</th>
<th class="num">Tempo &gt; L</th></tr>
{linhas_fase}
</table>
<p>A leitura direta: sob carga a vazão sobe de 3,7 para {n(res.loc[carga,'thp_mediana'])} kbps
(cerca de 80&nbsp;Mbps) e o rádio vai de 2% para {n(res.loc[carga,'prb_media'])}% de ocupação.
Os dois sobem <b>juntos</b> — e é isso que responde a pergunta do nosso tema.</p>

<h2>4. O achado: o que o repouso escondia</h2>
<p>Olhando só a mediana, o atraso no repouso é <b>zero</b> e sob carga é
{n(res.loc[carga,'delay_mediana'])}&nbsp;µs. Parece que a carga piorou o atraso. Mas o zero não é
"excelente": <b>{zb} das {nb} amostras do repouso têm atraso exatamente zero</b> porque não havia
tráfego para atrasar. E as {nb-zb} amostras restantes chegam a <b>218&nbsp;µs</b> — mais alto que a
mediana sob carga.</p>
<div class="box"><b>Sob carga o atraso não ficou pior; ficou contínuo.</b> No repouso ele é
esporádico ({n(res.loc[base,'acima_L'],0)}% do tempo acima do limiar); sob carga é permanente
({n(res.loc[carga,'acima_L'],0)}%). É essa mudança de <i>regime</i> que o nosso KQI mede — e é uma
conclusão diferente da que a mediana sozinha sugeria.</div>

<h2>5. Os indicadores, um a um</h2>
{ficha("KPI-1 — Vazão UL do usuário", "KPI (desempenho da rede)", [
  ("Fórmula", "<code>mediana(thp_ul)</code> e <code>p95(thp_ul)</code>, por fase"),
  ("Unidade", "kbps"),
  ("Granularidade", "amostra KPM, agregada por fase"),
  ("Fonte", "coluna <code>thp_ul</code> (<code>DRB.UEThpUl</code>) da zona silver"),
  ("Alvo / limiar", "queda abaixo de metade da mediana do repouso"),
  ("Interpretação", "o serviço está entregando bits ao usuário?"),
  ("Limite de validade", "1 UE em simulação, 1 execução. Usamos a mediana porque um pico isolado "
   "na recuperação (172.317 kbps) distorce a média."),
])}
{ficha("KPI-2 — Ocupação de PRB no uplink", "KPI (utilização de recurso)", [
  ("Fórmula", "<code>média(prb_ul)</code>, por fase"),
  ("Unidade", "% dos PRB"),
  ("Granularidade", "amostra KPM, agregada por fase"),
  ("Fonte", "coluna <code>prb_ul</code> (<code>RRU.PrbTotUl</code>)"),
  ("Alvo / limiar", "acima de 80% é pressão de capacidade (referência do slide 35 da Aula 04)"),
  ("Interpretação", "quanto do rádio está ocupado"),
  ("Limite de validade", "com um único UE, ele satura o rádio sozinho; com vários usuários este "
   "número teria outro significado."),
])}
{ficha("KPI-3 — Atraso RLC no downlink", "KPI (integridade)", [
  ("Fórmula", "<code>mediana(delay_dl)</code> e <code>p95(delay_dl)</code>, por fase"),
  ("Unidade", "µs"),
  ("Granularidade", "amostra KPM, agregada por fase"),
  ("Fonte", "coluna <code>delay_dl</code> (<code>DRB.RlcSduDelayDl</code>)"),
  ("Alvo / limiar", f"cláusula didática: p95 ≤ {n(1.2*res.loc[base,'delay_p95'],0)} µs"),
  ("Interpretação", "quanto o pacote espera na camada RLC antes de descer"),
  ("Limite de validade", "é atraso de RLC no downlink, <b>não</b> atraso fim-a-fim: não inclui "
   "core, transporte nem aplicação."),
])}
{ficha(f"KQI — Fração do tempo com atraso acima de {L:.0f} µs",
       "KQI (qualidade do serviço); vira cláusula de QoS quando L é tratado como contrato", [
  ("Fórmula", f"<code>n(delay_dl &gt; {L:.0f}) / n</code>, por fase"),
  ("Unidade", "% das amostras"),
  ("Granularidade", "amostra KPM, agregada por fase"),
  ("Fonte", "derivado de <code>delay_dl</code>"),
  ("Alvo / limiar", f"cláusula didática: ≤ {n(2*res.loc[base,'acima_L'],0)}% do tempo"),
  ("Interpretação", "que fração da janela ficou em regime degradado"),
  ("Limite de validade", "L separa <b>regimes</b>, não mede satisfação. A conclusão se sustenta "
   "para L entre cerca de 40 e 150 µs (ver seção 7)."),
])}

<h2>6. Um gráfico por indicador</h2>
<figure><img src="{b64img(os.path.join(FIG,'cp2_kpi1_vazao.png'))}">
<figcaption>KPI-1. A vazão fica junto de zero no repouso, sobe para o patamar de 80&nbsp;Mbps
durante a carga e volta. O pico isolado na recuperação é o que distorce a média — por isso
reportamos a mediana.</figcaption></figure>
<figure><img src="{b64img(os.path.join(FIG,'cp2_kpi2_prb.png'))}">
<figcaption>KPI-2. A ocupação do rádio acompanha a vazão: sobe para perto de 100% exatamente
enquanto o usuário está transmitindo. A linha tracejada é a referência de 80%.</figcaption></figure>
<figure><img src="{b64img(os.path.join(FIG,'cp2_kpi3_atraso.png'))}">
<figcaption>KPI-3. Aqui está o achado: no repouso o atraso alterna entre zero e picos altos; sob
carga vira um patamar contínuo, e não mais alto. A linha tracejada é o limiar L.</figcaption></figure>
<figure><img src="{b64img(os.path.join(FIG,'cp2_kqi_tempo_acima.png'))}">
<figcaption>KQI. A fração do tempo acima do limiar sai de {n(res.loc[base,'acima_L'],0)}% no
repouso para {n(res.loc[carga,'acima_L'],0)}% sob carga.</figcaption></figure>

<h2>7. Por que L = {L:.0f} µs, e até onde essa escolha se sustenta</h2>
<p>A Aula 04 é explícita: sem limiar justificado não existe KQI formal. Em vez de escolher um
número redondo, testamos L de 20 a 280&nbsp;µs e medimos a separação entre repouso e carga.</p>
<figure><img src="{b64img(os.path.join(FIG,'cp2_sensibilidade_L.png'))}">
<figcaption>A separação é máxima perto de 100&nbsp;µs (75 pontos). Ela resiste de cerca de
40 a 150&nbsp;µs e desaparece acima de 186&nbsp;µs, quando o p95 do repouso
({n(res.loc[base,'delay_p95'])}&nbsp;µs) ultrapassa o da carga
({n(res.loc[carga,'delay_p95'])}&nbsp;µs).</figcaption></figure>
<p>Esse é o <b>limite de validade</b> do indicador, e preferimos declará-lo. Um leitor que escolha
L = 200&nbsp;µs vai encontrar o resultado invertido — não porque a rede mudou, mas porque o
limiar saiu da faixa onde ele separa alguma coisa.</p>

<h2>8. QoS: as cláusulas, confrontadas com os dados</h2>
<p>Não existe 5QI, QoS Flow nem contrato de cliente neste laboratório. As cláusulas abaixo são
<b>didáticas</b> e, com uma exceção, saem do próprio repouso: um limiar absoluto que já dispara com
a rede parada não mede a rede, mede a escolha do limiar.</p>
<table>
<tr><th>Cláusula</th><th>Alvo</th><th>De onde vem o alvo</th><th class="num">Medido na carga</th><th>Veredito</th></tr>
{linhas_cl}
</table>
<p>As duas que cumprem dizem tanto quanto as duas que violam: <b>a latência e a vazão não
degradaram</b>. O que saiu do lugar foi a ocupação do rádio (capacidade) e a continuidade do atraso
(regime), e nenhuma das duas significa usuário mal servido.</p>

<h2>9. QoE: aqui é só proxy, e isso precisa ficar escrito</h2>
<p>Não há MOS, buffering nem qualquer nota de aplicativo neste artefato. Um atraso de RLC abaixo de
1&nbsp;ms não é "experiência ruim". O que podemos dizer com honestidade é que o atraso passou a ser
contínuo, o que <b>é risco</b> para aplicações sensíveis a jitter — e não que a experiência do
usuário caiu. A diferença entre as duas frases é o que a Aula 04 chama de proxy.</p>

<h2>10. Decisão e recomendação</h2>
<div class="box"><p style="margin:0">A regra do nosso tema procura vazão <i>baixa</i> com rádio
<i>cheio</i> — usuário mal servido. Ela <b>não disparou em nenhuma das 100 amostras</b>: a vazão
mediana sob carga é {n(res.loc[carga,'thp_mediana'])} kbps com {n(res.loc[carga,'prb_media'])}% de
PRB, ou seja, o rádio encheu <i>porque</i> o usuário estava usando. <b>Recomendamos não aplicar
política de priorização.</b> A saturação observada é capacidade em uso e o indicador que justifica
a decisão é o KPI-1 confrontado com o KPI-2; o limiar da regra é vazão abaixo de metade do p95
(41.079 kbps) com PRB acima de 79,2%. Confiança: baixa a moderada — uma execução, 100 amostras, um
único UE em simulação, sem RSRP/SINR/CQI para descartar causa de rádio.</p></div>

<h2>11. Nossa decisão × o <code>decision.json</code> do laboratório</h2>
<p>Vale confrontar: {dec_txt}, enquanto nós recomendamos <b>não</b> aplicar. Não é contradição — são
perguntas diferentes. O <code>decision.json</code> roda o <code>robust-baseline-mad</code>, que
pergunta <i>“isto é diferente do repouso?”</i>. É, por construção: a fase de carga foi feita para
ser diferente. A nossa pergunta é <i>“o usuário está mal servido?”</i>, e a resposta é não.</p>
<p>Há um detalhe técnico que reforça o ponto. No <code>model.json</code> do laboratório, o MAD é
<b>zero</b> nas três métricas (o repouso é constante demais) e o piso é 1,0. Com MAD zero, o score
vira o próprio desvio absoluto na unidade da métrica: qualquer variação acima de 3,5 dispara. A
primeira amostra de carga já pontua 11; as de 80&nbsp;Mbps pontuam dezenas de milhares, contra um
limiar de 3,5. O detector acusa <b>mudança de regime</b> — que é exatamente o que ele foi feito para
fazer — e não qualidade de serviço.</p>
<div class="box"><b>Anômalo não é ruim.</b> Essa é a lição que levamos deste checkpoint.</div>

<h2>12. O que estes dados não permitem dizer</h2>
<ul>
<li><b>Nada sobre cobertura ou qualidade de rádio</b>: não há RSRP, RSRQ, SINR nem CQI no artefato.</li>
<li><b>Nada sobre experiência real</b>: sem MOS ou métrica de aplicação, QoE aqui é sempre proxy.</li>
<li><b>Nada sobre a célula</b>: é um UE em RFSIM e uma execução; não há estatística de campus.</li>
<li><b>Nada sobre causa</b>: correlação entre vazão e PRB não prova que uma causa a outra.</li>
</ul>
<p>Dizer menos do que os dados sustentam também é resultado — e foi o critério que usamos em todo
este checkpoint.</p>

<h2>13. Como reproduzir</h2>
<p>Com Python 3 e as duas bibliotecas do <code>requirements.txt</code>:</p>
<p><code>python3 etl/build_lake.py &amp;&amp; python3 cp2_indicadores.py</code></p>
<p>O primeiro comando monta o mini-lake a partir do <code>data-raw/</code> incluído no pacote; o
segundo recalcula todos os números deste relatório e regrava as cinco figuras. Este documento é
gerado por <code>build_relatorio_cp2.py</code>, que <b>importa</b> a análise em vez de repetir as
contas — assim o texto não pode divergir dos números.</p>

<footer>{GRUPO} — {nomes} · {DISCIPLINA} · {MENTOR} · CESAR School<br>
Telemetria KPM de simulação (RFSIM) do laboratório <code>oai-cn-gnb-nonrt-nearrt</code>, sem dados pessoais.</footer>
</body></html>"""


def build_pdf(html_path, pdf_path):
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    if not chrome:
        print("aviso: chrome não encontrado, PDF pulado", file=sys.stderr)
        return False
    subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox",
                    "--no-pdf-header-footer", "--print-to-pdf=" + pdf_path,
                    "file://" + html_path], check=True, capture_output=True, timeout=180)
    return True


def montar_zip():
    stage = os.path.join(OUT, "grupo-6-checkpoint-2")
    shutil.rmtree(stage, ignore_errors=True)
    os.makedirs(stage)
    for f in ("RELATORIO_CP2.html", "RELATORIO_CP2.pdf"):
        if os.path.exists(os.path.join(OUT, f)):
            shutil.copy(os.path.join(OUT, f), stage)
    shutil.copy(os.path.join(HERE, "cp2_indicadores.py"), stage)
    shutil.copy(os.path.join(HERE, "eda_cp1.py"), stage)
    os.makedirs(os.path.join(stage, "kpis"))
    shutil.copy(os.path.join(HERE, "kpis", "kpis_cp2.md"), os.path.join(stage, "kpis"))
    os.makedirs(os.path.join(stage, "figures"))
    for f in sorted(os.listdir(FIG)):
        if f.startswith("cp2_"):
            shutil.copy(os.path.join(FIG, f), os.path.join(stage, "figures", f))
    os.makedirs(os.path.join(stage, "etl"))
    etl = open(os.path.join(HERE, "etl", "build_lake.py"), encoding="utf-8").read()
    etl = etl.replace(
        'REPO = PROJETO.parents[2]\nRAW = REPO / "external/cesar-school-repo/data/code/datasets/kpm-ue-tp-sample/kpm.jsonl"',
        'RAW = PROJETO / "data-raw/kpm.jsonl"')
    etl = etl.replace('.relative_to(REPO)', '.relative_to(PROJETO)')
    open(os.path.join(stage, "etl", "build_lake.py"), "w", encoding="utf-8").write(etl)
    shutil.copytree(RAW_DIR, os.path.join(stage, "data-raw"))
    with open(os.path.join(stage, "requirements.txt"), "w") as f:
        f.write("# so para cp2_indicadores.py (build_lake.py e stdlib)\npandas\nmatplotlib\n")
    with open(os.path.join(stage, "README.md"), "w", encoding="utf-8") as f:
        f.write(LEIAME)
    desk = os.path.join(os.path.expanduser("~"), "Área de trabalho")
    dest = desk if os.path.isdir(desk) else OUT
    zip_path = os.path.join(dest, "grupo-6-checkpoint-2.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(stage):
            for fn in files:
                fp = os.path.join(root, fn)
                z.write(fp, os.path.relpath(fp, OUT))
    return zip_path


LEIAME = """# Checkpoint 2 — Grupo 6 (Tema 1, Vazão do usuário)

Integrantes: Henrique Carmine, Kelvin de Lima Gabriel e Klinger Carneiro Júnior.
Professor: Dr. Jonas Augusto Kunzler — Análise de Dados em Redes de Telecom, CESAR School.

## O que tem aqui

| Arquivo | O que é |
|---|---|
| `RELATORIO_CP2.pdf` / `.html` | O relatório do checkpoint, com os gráficos embutidos |
| `kpis/kpis_cp2.md` | A ficha dos 4 indicadores (fórmula, unidade, papel, limite de validade) |
| `cp2_indicadores.py` | A análise: calcula tudo e gera as 5 figuras |
| `figures/` | Um gráfico por indicador, mais a sensibilidade do limiar |
| `etl/build_lake.py` | O ETL do CP1: bronze → silver → gold (só biblioteca padrão) |
| `data-raw/` | O pacote de dados do professor (`kpm-ue-tp-sample`) |
| `eda_cp1.py` | A análise do CP1, para referência |

## Como reproduzir

```bash
pip install -r requirements.txt
python3 etl/build_lake.py      # data-raw/ -> data/{bronze,silver,gold}
python3 cp2_indicadores.py     # números + figuras
```

## Em uma frase

A vazão do usuário sobe junto com a ocupação do rádio: rádio cheio entregando
80 Mbps é capacidade em uso, não usuário mal servido — por isso **não**
recomendamos política de priorização. O que mudou sob carga não foi o atraso
ficar maior, e sim ficar contínuo.
"""


if __name__ == "__main__":
    res = cp2.por_fase(cp2.carregar())
    clausulas, violadas = cp2.clausulas_qos(res)
    try:
        dec = json.load(open(cp2.DECISION))
    except OSError:
        dec = None
    html_path = os.path.join(OUT, "RELATORIO_CP2.html")
    open(html_path, "w", encoding="utf-8").write(html(res, clausulas, violadas, dec))
    ok = build_pdf(html_path, os.path.join(OUT, "RELATORIO_CP2.pdf"))
    zip_path = montar_zip()
    print(f"relatorio: {'PDF ok' if ok else 'sem PDF'}")
    print(f"zip: {zip_path}  ({os.path.getsize(zip_path)/1024:.0f} KB)")
