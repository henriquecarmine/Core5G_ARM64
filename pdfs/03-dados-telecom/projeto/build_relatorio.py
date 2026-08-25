#!/usr/bin/env python3
"""Gera o relatorio do Checkpoint 1 e monta o zip de entrega do grupo.
RELATORIO.html (logo da CESAR + figuras embutidas) -> RELATORIO.pdf via Chrome.
Uso: python3 build_relatorio.py
"""
import base64
import os
import shutil
import subprocess
import sys
import zipfile

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


def b64img(path):
    with open(path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def logo_svg():
    with open(LOGO, encoding="utf-8") as f:
        return f.read().replace('width="561" height="500"', 'width="54" height="48"', 1)


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
p{margin:0 0 8pt;text-align:justify}
table{border-collapse:collapse;width:100%;margin:8pt 0 12pt;font:10pt/1.4 Helvetica,Arial,sans-serif;font-variant-numeric:tabular-nums;page-break-inside:avoid}
th{border-bottom:1.5pt solid #33465a;padding:4pt 8pt;text-align:left}
td{border-bottom:.5pt solid #d3dbe4;padding:3.5pt 8pt}
.num{text-align:right}
figure{margin:10pt 0 6pt;page-break-inside:avoid}
figure img{width:100%;border:1px solid #e2e7ee}
figcaption{font:9.5pt/1.35 Helvetica,Arial,sans-serif;color:#5a6b7c;margin-top:5px}
.box{background:#f6f8f5;border-left:3px solid #4a7a3a;padding:8pt 12pt;font-size:11pt;margin:8pt 0}
code{font:10pt 'DejaVu Sans Mono',Consolas,monospace;color:#324}
ul{margin:0 0 8pt;padding-left:20pt} li{margin-bottom:4pt}
footer{margin-top:16pt;padding-top:8pt;border-top:.5pt solid #c3ccd5;font:9pt/1.4 Helvetica,Arial,sans-serif;color:#8593a1}
"""


def html():
    nomes = ", ".join(INTEGRANTES)
    fig1 = b64img(os.path.join(FIG, "cp1_serie_temporal.png"))
    fig2 = b64img(os.path.join(FIG, "cp1_vazao_x_prb.png"))
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Projeto Integrador - Grupo 6 - Checkpoint 1</title><style>{CSS}</style></head><body>
<div class="hd">{logo_svg()}<div class="t">
  <div class="disc">CESAR School &nbsp;|&nbsp; {DISCIPLINA}</div>
  <h1>Projeto Integrador — Checkpoint 1</h1>
  <div class="sub">{TEMA}</div></div></div>
<div class="meta">
  <div><b>{GRUPO}:</b> {nomes}</div>
  <div><b>Professor:</b> {MENTOR}</div>
  <div><b>Entrega:</b> Aula 04, 25/08/2026 (Checkpoint 1)</div>
</div>

<h2>1. Tema e pergunta</h2>
<p>O nosso grupo ficou com o tema da <b>vazão do usuário (UE-TP)</b>. A pergunta que
queremos responder é direta: a vazão de subida do UE (<code>DRB.UEThpUl</code>) sobe e
desce junto com o uso de PRB (<code>RRU.PrbTotUl</code>) e com o atraso
(<code>DRB.RlcSduDelayDl</code>)? Todos os grupos partem dos mesmos dados do laboratório;
o que muda de um pro outro é a pergunta, os dois indicadores e a recomendação no fim.</p>

<h2>2. De onde vêm os dados</h2>
<p>Usamos a trilha offline do professor (o pacote <code>kpm-ue-tp-sample</code>), que tem
100 amostras separadas em três fases: baseline (20 amostras, com a rede parada), stress
(60, sob carga) e recovery (20, voltando ao repouso). São dados de simulação (RFSIM), sem
nada pessoal. O artefato não informa a unidade de cada métrica, então adotamos a convenção
do KPM do O-RAN: <code>thp_ul</code> em kbps, <code>delay_dl</code> em ms e
<code>prb_ul</code> como quantidade de PRBs. Vale um cuidado: o campo <code>ingested_at</code>
(04/08, em UTC) é a hora em que os dados foram carregados, não a hora da medição, que é
anterior. Por isso usamos o <code>sample_index</code> como ordem no tempo.</p>

<h2>3. Como organizamos os dados</h2>
<p>O ETL está no <code>etl/build_lake.py</code>, escrito só com a biblioteca padrão do
Python. Ele monta um mini-lake em três zonas, como vimos na Aula 02: bronze (uma linha por
medição), silver (um SQLite com tipos e chave run_id/phase/sample_index) e gold (os
agregados por fase). A análise em <code>eda_cp1.py</code> parte da zona silver.</p>

<h2>4. Qualidade dos dados</h2>
<p>Nas 100 amostras não encontramos nulos nas três métricas, nem linhas repetidas na chave,
nem buracos no <code>sample_index</code> (vai de 0 a 19, 0 a 59 e 0 a 19). O
<code>ingested_at</code> está todo em UTC. O único ponto de atenção é o recovery: a média de
vazão (8.619) fica alta por causa de um pico isolado, mas a mediana (3,7) mostra que o
usuário já tinha voltado ao repouso. Por isso reportamos a mediana e o p95 junto com a média.</p>

<h2>5. Os dois indicadores</h2>
<p>O primeiro indicador é a vazão de subida por fase (média e p95 de <code>thp_ul</code>). O
segundo é a utilização média de PRB por fase (média de <code>prb_ul</code>). Os dois saem de
um <code>GROUP BY phase</code> na zona silver.</p>
<table><tr><th>Fase</th><th class="num">Vazão média</th><th class="num">Vazão p95</th>
  <th class="num">Vazão mediana</th><th class="num">PRB médio</th></tr>
<tr><td>baseline</td><td class="num">3,7</td><td class="num">3,8</td><td class="num">3,7</td><td class="num">2,0</td></tr>
<tr><td>stress</td><td class="num">78.383,8</td><td class="num">82.189,5</td><td class="num">80.023,7</td><td class="num">97,3</td></tr>
<tr><td>recovery</td><td class="num">8.619,3</td><td class="num">8.619,4</td><td class="num">3,7</td><td class="num">3,0</td></tr></table>
<p>Vazão e PRB seguem o mesmo desenho: baixos quando a rede está parada (baseline e recovery)
e altos sob carga (stress). A recomendação, que fechamos no checkpoint final, vai na linha de:
se a vazão cair com o PRB alto (rádio cheio mas usuário mal atendido), propor uma política A1
de alívio de carga, só em simulação, sem mexer de verdade na rede.</p>

<h2>6. A vazão anda junto com o PRB e o atraso?</h2>
<p>Na correlação de Pearson com as 100 amostras juntas deu vazão × PRB = 0,924 e vazão ×
atraso = 0,484. Só que essa conta global mistura as fases (repouso e carga). Quando olhamos
dentro de cada fase separada, o quadro muda:</p>
<table><tr><th>Fase</th><th class="num">vazão × PRB</th><th class="num">vazão × atraso</th></tr>
<tr><td>baseline</td><td class="num">PRB constante (=2)</td><td class="num">0,11</td></tr>
<tr><td>stress</td><td class="num">0,979</td><td class="num">0,16</td></tr>
<tr><td>recovery</td><td class="num">1,00</td><td class="num">−0,08</td></tr></table>
<div class="box"><b>Resposta:</b> a vazão acompanha o PRB de verdade, já que a relação
continua forte mesmo dentro do stress (0,98). Com o atraso é diferente: dentro de cada fase
a correlação fica perto de zero, então aquele 0,48 global vem só do contraste entre repouso e
carga, não de uma ligação real entre as duas.</div>

<figure><img src="{fig1}"><figcaption>Figura 1. Vazão, PRB e atraso ao longo do experimento,
com as fases marcadas. O PRB e a vazão sobem juntos no stress; o pico isolado no começo do
recovery é o que puxa a média.</figcaption></figure>
<figure><img src="{fig2}"><figcaption>Figura 2. Vazão contra PRB, por fase. Sob carga (stress),
mais PRB acompanha mais vazão; nas fases paradas, os dois ficam no chão.</figcaption></figure>

<h2>7. O que os indicadores não mostram</h2>
<ul>
<li>A vazão × atraso de 0,48 é efeito de comparar fases; dentro de cada fase não há relação.</li>
<li>As unidades são as da convenção KPM, o dado em si não as declara.</li>
<li>O <code>ingested_at</code> é a hora de carregar, não de medir; a ordem no tempo é o <code>sample_index</code>.</li>
<li>É um único run e poucos UEs (RFSIM). Serve pra aprender, não é estatística de rede real.</li>
<li>O atraso é um proxy de qualidade, não há nota de aplicativo; e a vazão é sintética do simulador.</li>
</ul>

<h2>8. Como reproduzir</h2>
<p>Com a pasta <code>data-raw/</code> do lado:</p>
<p><code>python3 etl/build_lake.py &amp;&amp; python3 eda_cp1.py</code></p>
<p>Isso gera o lake em <code>data/</code> e os gráficos em <code>figures/</code>. As contas dos
indicadores estão em <code>kpis/kpis.md</code>.</p>

<footer>{DISCIPLINA} · {MENTOR} · {GRUPO}: {nomes} · Checkpoint 1, 25/08/2026</footer>
</body></html>"""


def build_pdf(html_path, pdf_path):
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    if not chrome:
        print("aviso: chrome não encontrado, PDF pulado", file=sys.stderr)
        return False
    subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox",
                    "--no-pdf-header-footer", "--print-to-pdf=" + pdf_path,
                    "file://" + html_path], check=True, capture_output=True, timeout=120)
    return True


def montar_zip():
    stage = os.path.join(OUT, "grupo-6-projeto-integrador")
    shutil.rmtree(stage, ignore_errors=True)
    os.makedirs(stage)
    shutil.copy(os.path.join(OUT, "RELATORIO.html"), stage)
    if os.path.exists(os.path.join(OUT, "RELATORIO.pdf")):
        shutil.copy(os.path.join(OUT, "RELATORIO.pdf"), stage)
    for item in ["README.md", "eda_cp1.py", "kpis"]:
        src = os.path.join(HERE, item)
        (shutil.copytree if os.path.isdir(src) else shutil.copy)(src, os.path.join(stage, item))
    shutil.copytree(FIG, os.path.join(stage, "figures"))
    os.makedirs(os.path.join(stage, "etl"))
    etl = open(os.path.join(HERE, "etl", "build_lake.py"), encoding="utf-8").read()
    etl = etl.replace(
        'REPO = PROJETO.parents[2]\nRAW = REPO / "external/cesar-school-repo/data/code/datasets/kpm-ue-tp-sample/kpm.jsonl"',
        'RAW = PROJETO / "data-raw/kpm.jsonl"')
    etl = etl.replace('.relative_to(REPO)', '.relative_to(PROJETO)')
    open(os.path.join(stage, "etl", "build_lake.py"), "w", encoding="utf-8").write(etl)
    shutil.copytree(RAW_DIR, os.path.join(stage, "data-raw"))
    with open(os.path.join(stage, "requirements.txt"), "w") as f:
        f.write("# so para eda_cp1.py (build_lake.py e stdlib)\npandas\nmatplotlib\n")
    # zip na Area de trabalho
    desk = os.path.join(os.path.expanduser("~"), "Área de trabalho")
    dest = desk if os.path.isdir(desk) else OUT
    zip_path = os.path.join(dest, "grupo-6-projeto-integrador.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(stage):
            for fn in files:
                fp = os.path.join(root, fn)
                z.write(fp, os.path.relpath(fp, OUT))
    return zip_path


if __name__ == "__main__":
    html_path = os.path.join(OUT, "RELATORIO.html")
    open(html_path, "w", encoding="utf-8").write(html())
    ok = build_pdf(html_path, os.path.join(OUT, "RELATORIO.pdf"))
    zip_path = montar_zip()
    print(f"relatorio: {'PDF ok' if ok else 'sem PDF'}")
    print(f"zip: {zip_path}  ({os.path.getsize(zip_path)/1024:.0f} KB)")
