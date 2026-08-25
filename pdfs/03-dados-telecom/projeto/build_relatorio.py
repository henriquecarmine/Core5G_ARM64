#!/usr/bin/env python3
"""Gera o RELATÓRIO do Checkpoint 1 (Projeto Integrador · Grupo 6) e monta o ZIP
de entrega. Self-contained: logo da CESAR inline (SVG) e figuras embutidas (base64)
-> RELATORIO.html -> RELATORIO.pdf (Chrome headless).

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
        svg = f.read()
    # normaliza tamanho no cabeçalho
    return svg.replace('width="561" height="500"', 'width="54" height="48"', 1)


CSS = """
@page { size: A4; margin: 18mm 18mm 16mm; }
*{box-sizing:border-box}
body{font:11pt/1.5 Georgia,'Times New Roman',serif;color:#1a2430;max-width:174mm;margin:0 auto}
.hd{display:flex;align-items:center;gap:14px;border-bottom:2.5px solid #f04e23;padding-bottom:12px;margin-bottom:6px}
.hd .logo{flex:none}
.hd .t{flex:1}
.hd .disc{font:700 10pt/1.2 Helvetica,Arial,sans-serif;letter-spacing:.02em;color:#f04e23;text-transform:uppercase}
.hd h1{font:800 17pt/1.15 Helvetica,Arial,sans-serif;margin:2px 0 0;color:#12202e;letter-spacing:-.01em}
.hd .sub{font:400 10.5pt/1.3 Helvetica,Arial,sans-serif;color:#5a6b7c;margin-top:2px}
.meta{display:flex;flex-wrap:wrap;gap:4px 22px;font:10pt/1.5 Helvetica,Arial,sans-serif;color:#33465a;margin:10px 0 4px}
.meta b{color:#12202e}
h2{font:700 12.5pt/1.25 Helvetica,Arial,sans-serif;color:#12202e;margin:18pt 0 6pt;padding-top:8pt;border-top:1px solid #dfe5ec;page-break-after:avoid}
p{margin:0 0 8pt;text-align:justify;hyphens:auto}
b,strong{color:#12202e}
table{border-collapse:collapse;width:100%;margin:8pt 0 12pt;font:9.5pt/1.4 Helvetica,Arial,sans-serif;font-variant-numeric:tabular-nums;page-break-inside:avoid}
th{border-top:1.2pt solid #12202e;border-bottom:.7pt solid #12202e;padding:4pt 8pt;text-align:left;background:#f7f9fb}
td{border-bottom:.5pt solid #d3dbe4;padding:3.5pt 8pt}
tr:last-child td{border-bottom:1.2pt solid #12202e}
.num{text-align:right}
figure{margin:10pt 0 6pt;page-break-inside:avoid}
figure img{width:100%;border:1px solid #dfe5ec;border-radius:4px}
figcaption{font:9pt/1.35 Helvetica,Arial,sans-serif;color:#5a6b7c;margin-top:5px;text-align:center}
.callout{border:1px solid #dfe5ec;border-left:4px solid #f04e23;background:#fbfbf7;padding:9pt 13pt;font-size:10.5pt;margin:8pt 0}
code{font:9.5pt 'DejaVu Sans Mono',Consolas,monospace;background:#f2f4f7;padding:0 3pt;border-radius:2px}
ul{margin:0 0 8pt;padding-left:18pt} li{margin-bottom:3pt;text-align:justify}
footer{margin-top:16pt;padding-top:8pt;border-top:.7pt solid #b9c4cf;font:8.5pt/1.4 Helvetica,Arial,sans-serif;color:#7c8da0;text-align:center}
"""


def html():
    integrantes = " · ".join(INTEGRANTES)
    fig1, fig2 = b64img(os.path.join(FIG, "cp1_serie_temporal.png")), b64img(os.path.join(FIG, "cp1_vazao_x_prb.png"))
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Projeto Integrador — {GRUPO} — Checkpoint 1</title><style>{CSS}</style></head><body>
<div class="hd"><div class="logo">{logo_svg()}</div><div class="t">
  <div class="disc">CESAR School · {DISCIPLINA}</div>
  <h1>Projeto Integrador — Checkpoint 1</h1>
  <div class="sub">{TEMA}</div></div></div>
<div class="meta">
  <span><b>{GRUPO}:</b> {integrantes}</span>
  <span><b>Mentor:</b> {MENTOR}</span>
  <span><b>Entrega:</b> Aula 04 · 25/08/2026 (Checkpoint 1 — EDA)</span>
</div>

<h2>1. Tema e pergunta</h2>
<p>O {GRUPO} investiga a <b>vazão do usuário (UE-TP)</b> sobre a telemetria KPM do lab
<code>oai-cn-gnb-nonrt-nearrt</code>. <b>Pergunta:</b> a vazão do UE (<code>DRB.UEThpUl</code>)
sobe e desce <b>junto</b> com o uso de PRB (<code>RRU.PrbTotUl</code>) e com o atraso
(<code>DRB.RlcSduDelayDl</code>)? Todos os grupos usam os mesmos dados; muda a pergunta,
os dois indicadores e a recomendação.</p>

<h2>2. Fonte dos dados e ética</h2>
<p>Trilha offline oficial do docente (pacote <code>kpm-ue-tp-sample</code>): <b>100 amostras</b>
em três fases — <b>baseline</b> (20, ocioso), <b>stress</b> (60, sob carga) e <b>recovery</b>
(20, retorno ao ocioso). Telemetria <b>sintética (RFSIM)</b>, sem dados pessoais.
As unidades não são declaradas no artefato; adotamos a <b>convenção KPM O-RAN</b>
(<code>thp_ul</code> em kbps, <code>delay_dl</code> em ms, <code>prb_ul</code> em contagem de PRBs).
O carimbo <code>ingested_at</code> (04/08, UTC) é da <b>ingestão em lote</b>, não da medição
(o experimento é anterior); a ordem temporal usada é o <code>sample_index</code>.</p>

<h2>3. Pipeline (mini-lake, zonas da Aula 02)</h2>
<p>ETL reprodutível em <code>etl/build_lake.py</code> (stdlib): <b>raw</b> (JSONL do pacote) →
<b>bronze</b> (achatado) → <b>silver</b> (SQLite tipado, chave <code>run_id·phase·sample_index</code>)
→ <b>gold</b> (agregados por fase). A análise (<code>eda_cp1.py</code>) parte da zona silver.</p>

<h2>4. Qualidade dos dados</h2>
<p>Sobre as 100 amostras: <b>sem nulos</b> nas três métricas, <b>sem duplicatas</b> na chave,
<b>sem gaps</b> no <code>sample_index</code> (0–19 / 0–59 / 0–19) e <code>ingested_at</code>
todo em <b>UTC</b>. Ressalva: no <b>recovery</b>, a <b>média</b> de vazão (8.619) é puxada por
um <b>pico residual</b> — a <b>mediana (3,7)</b> mostra que o usuário já voltou ao ocioso;
por isso reportamos mediana e p95 além da média.</p>

<h2>5. Indicadores do tema</h2>
<p><b>Indicador 1 — Vazão UL por fase</b> (kbps): <code>média(thp_ul)</code> e <code>p95(thp_ul)</code>
agrupando por fase. <b>Indicador 2 — Utilização de PRB UL por fase</b> (PRBs): <code>média(prb_ul)</code>.</p>
<table><tr><th>Fase</th><th class="num">Vazão média</th><th class="num">Vazão p95</th>
  <th class="num">Vazão mediana</th><th class="num">PRB UL médio</th></tr>
<tr><td>baseline</td><td class="num">3,7</td><td class="num">3,8</td><td class="num">3,7</td><td class="num">2,0</td></tr>
<tr><td>stress</td><td class="num">78.383,8</td><td class="num">82.189,5</td><td class="num">80.023,7</td><td class="num">97,3</td></tr>
<tr><td>recovery</td><td class="num">8.619,3</td><td class="num">8.619,4</td><td class="num">3,7</td><td class="num">3,0</td></tr></table>
<p>A vazão e o PRB seguem a mesma forma: pequenos no ocioso (baseline/recovery) e altos sob carga
(stress). Uma eventual recomendação (a fechar no checkpoint final) seria: se a vazão <b>cair</b>
com o <b>PRB alto</b>, propor priorização/alívio de carga em <b>política A1 simulada</b> (dry-run,
sem atuação física na RAN).</p>

<h2>6. A vazão anda junto com PRB e atraso?</h2>
<p>Correlação de Pearson <b>global</b> (100 amostras): <b>vazão × PRB = 0,924</b> ·
vazão × atraso = 0,484. A correlação global, porém, <b>mistura as fases</b> (ocioso × carga).
Olhando <b>dentro</b> de cada fase:</p>
<table><tr><th>Fase</th><th class="num">vazão × PRB</th><th class="num">vazão × atraso</th></tr>
<tr><td>baseline</td><td class="num">— (PRB constante = 2)</td><td class="num">0,11</td></tr>
<tr><td>stress</td><td class="num">0,979</td><td class="num">0,16</td></tr>
<tr><td>recovery</td><td class="num">1,00</td><td class="num">−0,08</td></tr></table>
<div class="callout"><b>Resposta:</b> a vazão <b>acompanha o PRB de verdade</b> — a relação se
mantém mesmo dentro do stress (0,98). Já a vazão × atraso é <b>≈ 0 dentro de cada fase</b>: o
0,48 global vem apenas do <b>contraste entre fases</b>, não de uma dinâmica entre as duas.</div>

<figure><img src="{fig1}"><figcaption>Figura 1 — Vazão UL, PRB UL e atraso DL ao longo do experimento
(faixas por fase). O PRB e a vazão sobem juntos no stress; o pico isolado no início do recovery
é o que puxa a média.</figcaption></figure>
<figure><img src="{fig2}"><figcaption>Figura 2 — Vazão UL × PRB UL por fase: sob carga (stress),
mais PRB acompanha mais vazão; nas fases ociosas, ambos ficam no piso.</figcaption></figure>

<h2>7. Limitações — o que os indicadores NÃO provam</h2>
<ul>
<li><b>Correlação por fase:</b> a vazão × atraso "0,48" é contraste entre fases (≈0 dentro da fase).</li>
<li><b>Unidades por convenção</b> KPM (não declaradas no artefato).</li>
<li><b><code>ingested_at</code></b> é carimbo de ingestão, não a hora da medição; ordem = <code>sample_index</code>.</li>
<li><b>1 <code>run_id</code>, poucos UEs</b> (RFSIM): estatística didática, não de campus real.</li>
<li><code>delay_dl</code> é <b>proxy</b> de qualidade — não há MOS de aplicativo; vazão sintética do RFSIM.</li>
</ul>

<h2>8. Reprodução</h2>
<p>Com o pacote de dados ao lado (<code>data-raw/</code>):</p>
<p><code>python3 etl/build_lake.py &amp;&amp; python3 eda_cp1.py</code></p>
<p>Gera o mini-lake em <code>data/</code> e as figuras em <code>figures/</code>. Detalhe dos
indicadores em <code>kpis/kpis.md</code>.</p>

<footer>CESAR School · {DISCIPLINA} · {MENTOR} · {GRUPO}: {integrantes} · Checkpoint 1 (25/08/2026)</footer>
</body></html>"""


def build_pdf(html_path, pdf_path):
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    if not chrome:
        print("aviso: chrome não encontrado — PDF pulado", file=sys.stderr)
        return False
    subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox",
                    "--no-pdf-header-footer", "--print-to-pdf=" + pdf_path,
                    "file://" + html_path], check=True, capture_output=True, timeout=120)
    return True


def montar_zip():
    """Pasta self-contained grupo-6-projeto-integrador/ -> zip em ~/Downloads."""
    stage = os.path.join(OUT, "grupo-6-projeto-integrador")
    shutil.rmtree(stage, ignore_errors=True)
    os.makedirs(stage)
    # relatório
    shutil.copy(os.path.join(OUT, "RELATORIO.html"), stage)
    if os.path.exists(os.path.join(OUT, "RELATORIO.pdf")):
        shutil.copy(os.path.join(OUT, "RELATORIO.pdf"), stage)
    # código + docs + figuras
    for item in ["README.md", "eda_cp1.py", "kpis"]:
        src = os.path.join(HERE, item)
        dst = os.path.join(stage, item)
        (shutil.copytree if os.path.isdir(src) else shutil.copy)(src, dst)
    shutil.copytree(FIG, os.path.join(stage, "figures"))
    # ETL — variante standalone que lê de data-raw/
    os.makedirs(os.path.join(stage, "etl"))
    etl = open(os.path.join(HERE, "etl", "build_lake.py"), encoding="utf-8").read()
    etl = etl.replace(
        'REPO = PROJETO.parents[2]\nRAW = REPO / "external/cesar-school-repo/data/code/datasets/kpm-ue-tp-sample/kpm.jsonl"',
        'RAW = PROJETO / "data-raw/kpm.jsonl"')
    etl = etl.replace('.relative_to(REPO)', '.relative_to(PROJETO)')   # todos os prints
    open(os.path.join(stage, "etl", "build_lake.py"), "w", encoding="utf-8").write(etl)
    # dados brutos (pra rodar sem o submódulo)
    shutil.copytree(RAW_DIR, os.path.join(stage, "data-raw"))
    # deps: build_lake.py é stdlib; eda_cp1.py usa pandas + matplotlib
    with open(os.path.join(stage, "requirements.txt"), "w") as f:
        f.write("# só para eda_cp1.py (build_lake.py é stdlib puro)\npandas\nmatplotlib\n")
    # zip -> Downloads
    dl = os.path.join(os.path.expanduser("~"), "Downloads")
    zip_path = os.path.join(dl if os.path.isdir(dl) else OUT, "grupo-6-projeto-integrador.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(stage):
            for fn in files:
                fp = os.path.join(root, fn)
                z.write(fp, os.path.relpath(fp, OUT))
    return zip_path


if __name__ == "__main__":
    html_path = os.path.join(OUT, "RELATORIO.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html())
    ok = build_pdf(html_path, os.path.join(OUT, "RELATORIO.pdf"))
    zip_path = montar_zip()
    print(f"RELATORIO.html + {'RELATORIO.pdf' if ok else '(sem PDF)'} em {OUT}")
    print(f"ZIP de entrega: {zip_path}  ({os.path.getsize(zip_path)/1024:.0f} KB)")
