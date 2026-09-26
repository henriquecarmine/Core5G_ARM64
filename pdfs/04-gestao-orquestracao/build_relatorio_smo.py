#!/usr/bin/env python3
"""Gera o relatório da 1ª parte da avaliação (Plataformas de SMO) em PDF.

HTML (logo da CESAR School, diagrama e figura embutidos) -> PDF pelo Chrome ->
entrega/ (gitignored) e Área de trabalho.

Os nomes dos integrantes NÃO ficam no repositório: vão por argumento, na ordem
dos casos (as vozes 1, 2 e 3 da apresentação).

Uso: python3 build_relatorio_smo.py --integrantes "Nome 1,Nome 2,Nome 3"

Os números vêm das execuções dos testes do painel contra o SMO no servidor do
grupo em 11/09/2026 (server/smo/smo_*.sh); o texto não recalcula nada.
"""
import argparse
import base64
import html
import io
import os
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
LOGO = os.path.join(REPO, "server/panel/static/ops/cesar-marca.svg")
CAPTURA = os.path.join(REPO, "server/panel/test/screenshots/topology-p2-smo-tecnico.png")
OUT = os.path.join(HERE, "entrega")
NOME = "RELATORIO_SMO_ORAN_SC"

GIT = "https://github.com/henriquecarmine/Core5G_ARM64"
PAINEL = "https://core5g-arm64.duckdns.org"
ODLUX = "https://odlux.oam.smo.core5g-arm64.duckdns.org"

CSS = """
@page { size: A4; margin: 20mm 19mm 18mm;
  @bottom-right { content: counter(page); font: 9pt Helvetica, Arial, sans-serif; color: #5a6b7c; } }
@page :first { @bottom-right { content: none; } }
*{box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{font:11.2pt/1.55 Georgia,'Times New Roman',serif;color:#20272e;margin:0}
a{color:#1f5f9e;text-decoration:none}
.capa{height:255mm;display:flex;flex-direction:column;text-align:center;page-break-after:always}
.capa .logo{margin:6mm auto 0}
.capa .inst{font:600 11pt/1.5 Helvetica,Arial,sans-serif;color:#33465a;margin-top:7mm}
.capa .inst b{color:#f04e23}
.capa .meio{flex:1;display:flex;flex-direction:column;justify-content:center}
.capa h1{font:700 22pt/1.2 Helvetica,Arial,sans-serif;color:#1a2733;margin:0 12mm}
.capa .sub{font:400 12.5pt/1.45 Helvetica,Arial,sans-serif;color:#5a6b7c;margin:5mm 16mm 0}
.capa .fio{width:40mm;height:2px;background:#f04e23;margin:9mm auto}
.capa .quem{font:400 11.5pt/1.7 Helvetica,Arial,sans-serif;color:#33465a}
.capa .quem b{color:#1a2733}
.capa .pe{font:400 11pt/1.5 Helvetica,Arial,sans-serif;color:#33465a}
h2{font:700 14pt/1.25 Helvetica,Arial,sans-serif;color:#1a2733;margin:18pt 0 6pt;page-break-after:avoid;border-bottom:1.5px solid #f04e23;padding-bottom:3pt}
h3{font:700 11.5pt/1.25 Helvetica,Arial,sans-serif;color:#1a2733;margin:13pt 0 4pt;page-break-after:avoid}
h2.quebra{page-break-before:always;margin-top:0}
.resp{font:400 9.8pt/1.4 Helvetica,Arial,sans-serif;color:#5a6b7c;margin:-2pt 0 8pt}
p{margin:0 0 7.5pt;text-align:justify;hyphens:auto}
table{border-collapse:collapse;width:100%;margin:6pt 0 11pt;font:9.4pt/1.38 Helvetica,Arial,sans-serif;font-variant-numeric:tabular-nums;page-break-inside:avoid}
th{border-bottom:1.4pt solid #33465a;padding:3.5pt 6pt;text-align:left;vertical-align:bottom}
td{border-bottom:.5pt solid #d3dbe4;padding:3pt 6pt;vertical-align:top}
td.n{text-align:right;white-space:nowrap}
caption{caption-side:top;text-align:left;font:600 9.4pt/1.35 Helvetica,Arial,sans-serif;color:#33465a;padding-bottom:3pt}
figure{margin:8pt 0 10pt;page-break-inside:avoid;text-align:center}
figure svg{width:100%;height:auto}
figure img{max-width:100%;border:1px solid #d3dbe4}
figcaption{font:9.2pt/1.35 Helvetica,Arial,sans-serif;color:#5a6b7c;margin-top:5px;text-align:left}
.box{background:#f5f7f9;border-left:3px solid #33465a;padding:6pt 10pt;font:9.8pt/1.45 Helvetica,Arial,sans-serif;margin:6pt 0 10pt;page-break-inside:avoid}
.box.ev{background:#f2f7f1;border-left-color:#3f7a3a}
.box.at{background:#fdf5ee;border-left-color:#e08a2e}
.box p{margin:0 0 3pt;text-align:left}
.cam{font:600 9.4pt/1.9 Helvetica,Arial,sans-serif;color:#33465a;margin:2pt 0 9pt;page-break-inside:avoid}
.cam b{display:inline-block;border:1px solid #c9d1da;border-radius:3px;padding:0 6px;background:#fff;font-weight:600;line-height:1.6}
.cam i{font-style:normal;color:#8a96a3;margin:0 4px}
.sim{color:#2c6e35;font-weight:700}
.parc{color:#b26a12;font-weight:700}
.nao{color:#b4451f;font-weight:700}
code{font:9.3pt 'DejaVu Sans Mono',Consolas,monospace;color:#2a3a4a;word-break:break-word}
ul{margin:0 0 8pt;padding-left:17pt} li{margin-bottom:3pt}
.kw{font:9.8pt/1.4 Helvetica,Arial,sans-serif;color:#33465a}
.ref p{text-align:left;padding-left:14pt;text-indent:-14pt;font-size:10pt;margin-bottom:4pt}
.junto{page-break-inside:avoid}
.fecho{border-left:3px solid #f04e23;background:#fdf5ee;padding:7pt 11pt;margin:8pt 0 0;page-break-inside:avoid}
.fecho p{margin:0;text-align:left;font:10.5pt/1.5 Helvetica,Arial,sans-serif}
"""


# ---------------------------------------------------------------------------
# Diagrama da arquitetura (SVG desenhado aqui, coordenadas de 900 x 590)
# ---------------------------------------------------------------------------
def _caixa(x, y, w, h, cls, titulo, linhas):
    t = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" class="{cls}"/>',
         f'<text x="{x + 12}" y="{y + 24}" class="t">{titulo}</text>']
    for i, ln in enumerate(linhas):
        t.append(f'<text x="{x + 12}" y="{y + 44 + i * 16}" class="s">{ln}</text>')
    return "".join(t)


def _linha(x1, y1, x2, y2, cls, rotulo=None, seta=False):
    m = ' marker-end="url(#seta)"' if seta else ""
    s = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}"{m}/>'
    if rotulo:
        cx, cy, w = (x1 + x2) / 2, (y1 + y2) / 2, 7 * len(rotulo) + 14
        s += (f'<rect x="{cx - w / 2}" y="{cy - 10}" width="{w}" height="20" rx="10" class="chip"/>'
              f'<text x="{cx}" y="{cy + 4}" class="ct">{rotulo}</text>')
    return s


def diagrama():
    p = ['<svg viewBox="0 0 900 590" xmlns="http://www.w3.org/2000/svg" role="img" '
         'aria-label="Arquitetura do SMO do O-RAN SC em três camadas">',
         '<defs><marker id="seta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
         'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#6b7a89"/></marker></defs>',
         '<style>'
         '.band{fill:#f3f1fb;stroke:#d6d0f2}.bandn{fill:#edf6f0;stroke:#c3dfcb}'
         '.b{fill:#fff;stroke:#6b5bd6;stroke-width:1.6}.bn{fill:#fff;stroke:#2f8f4e;stroke-width:1.6}'
         '.bx{fill:#fff;stroke:#8a96a3;stroke-width:1.4}'
         '.t{font:700 15px Helvetica,Arial,sans-serif;fill:#1a2733}'
         '.s{font:400 12.5px Helvetica,Arial,sans-serif;fill:#4a5a6a}'
         '.bl{font:700 12px Helvetica,Arial,sans-serif;letter-spacing:.08em;fill:#5b4fb8;text-anchor:end}'
         '.bln{fill:#2c6e35}'
         '.l{stroke:#6b5bd6;stroke-width:1.6}.ln{stroke:#2f8f4e;stroke-width:1.8}.lx{stroke:#6b7a89;stroke-width:1.4}'
         '.chip{fill:#fff;stroke:#c9d1da}.ct{font:600 11.5px Helvetica,Arial,sans-serif;fill:#33465a;text-anchor:middle}'
         '.nota{font:italic 12px Helvetica,Arial,sans-serif;fill:#4a5a6a}'
         '</style>']
    # faixas das camadas
    p.append('<rect x="10" y="86" width="880" height="152" rx="8" class="band"/>'
             '<text x="878" y="106" class="bl">COMMON — PLATAFORMA</text>'
             '<rect x="10" y="256" width="880" height="142" rx="8" class="band"/>'
             '<text x="878" y="276" class="bl">OAM — GERÊNCIA</text>'
             '<rect x="10" y="416" width="880" height="160" rx="8" class="bandn"/>'
             '<text x="878" y="562" class="bl bln">NETWORK — ELEMENTOS GERENCIADOS</text>')
    # ligações (antes das caixas, para ficarem por baixo)
    p.append(_linha(170, 43, 203, 43, "lx", seta=True))
    p.append(_linha(235, 68, 152, 116, "lx", seta=True))
    p.append(_linha(104, 196, 104, 288, "l", "proxy", seta=True))
    p.append(_linha(184, 329, 260, 329, "l", "RESTCONF", seta=True))
    p.append(_linha(300, 290, 290, 196, "l", "OAuth"))
    p.append(_linha(440, 290, 447, 196, "l", "SQL"))
    p.append(_linha(640, 290, 640, 198, "l", "tópicos", seta=True))
    p.append(_linha(320, 368, 335, 448, "ln", "O1 · NETCONF/TLS"))
    p.append(_linha(450, 368, 560, 448, "ln", "M-plane · NETCONF"))
    p.append(_linha(250, 487, 184, 487, "ln", "M-plane"))
    p.append(_linha(670, 470, 700, 370, "ln", "VES · HTTPS", seta=True))
    # caixas
    p.append(_caixa(20, 18, 150, 50, "bx", "Operador", ["navegador"]))
    p.append(_caixa(205, 18, 240, 50, "bx", "Caddy do painel", ["HTTPS público, com bloqueios"]))
    p.append(_caixa(24, 118, 160, 78, "b", "gateway", ["Traefik · entrada", "HTTPS e call home"]))
    p.append(_caixa(198, 118, 160, 78, "b", "identity", ["Keycloak + PostgreSQL", "usuários e papéis"]))
    p.append(_caixa(372, 118, 150, 78, "b", "persistence", ["MariaDB", "estado e alarmes"]))
    p.append(_caixa(536, 118, 176, 78, "b", "kafka", ["+ zookeeper, bridge, ui", "barramento de eventos"]))
    p.append(_caixa(726, 118, 150, 78, "b", "topology", ["NTSim-NG · TAPI", "topologia"]))
    p.append(_caixa(24, 290, 160, 78, "b", "odlux", ["console do operador"]))
    p.append(_caixa(262, 290, 228, 78, "b", "controller", ["SDN-R · OpenDaylight", "cliente NETCONF da O1"]))
    p.append(_caixa(580, 290, 196, 78, "b", "ves-collector", ["VES 7.2.1", "falhas, medidas, registro"]))
    p.append(_caixa(24, 448, 160, 78, "bn", "o-ru-hierarchical", ["O-RU simulado", "gerenciado pela O-DU"]))
    p.append(_caixa(250, 448, 190, 78, "bn", "pynts-o-du-o1", ["O-DU simulada", "154 modelos YANG"]))
    p.append(_caixa(480, 448, 190, 78, "bn", "pynts-o-ru-hybrid", ["O-RU simulado", "114 modelos YANG"]))
    for i, ln in enumerate(["Call home: cada elemento", "liga para o SMO ao iniciar", "(gateway, portas 4334 SSH",
                            "e 4335 TLS)."]):
        p.append(f'<text x="700" y="{466 + i * 16}" class="nota">{ln}</text>')
    p.append("</svg>")
    return "".join(p)


def captura_smo():
    """Recorte da coluna do SMO na topologia do painel (captura do teste visual)."""
    if not os.path.exists(CAPTURA):
        return ""
    try:
        from PIL import Image
    except ImportError:
        return ""
    buf = io.BytesIO()
    Image.open(CAPTURA).crop((1615, 305, 2195, 1350)).save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def logo(largura_mm):
    with open(LOGO, encoding="utf-8") as f:
        svg = f.read()
    return svg.replace('width="561" height="500"',
                       f'width="{largura_mm}mm" height="{largura_mm * 500 / 561:.1f}mm"', 1)


# ---------------------------------------------------------------------------
# Peças de texto
# ---------------------------------------------------------------------------
def tab(cab, linhas, legenda="", num=()):
    h = [f"<table>{f'<caption>{legenda}</caption>' if legenda else ''}<tr>"]
    h += [f"<th>{c}</th>" for c in cab]
    h.append("</tr>")
    for ln in linhas:
        h.append("<tr>" + "".join(f'<td{" class=n" if i in num else ""}>{c}</td>' for i, c in enumerate(ln)) + "</tr>")
    h.append("</table>")
    return "".join(h)


def caminho(*passos):
    return '<div class="cam">' + "<i>→</i>".join(f"<b>{p}</b>" for p in passos) + "</div>"


def evidencia(teste, script, *linhas):
    corpo = "".join(f"<p>{ln}</p>" for ln in linhas)
    return (f'<div class="box ev"><p><b>Evidência — teste “{teste}”</b> '
            f'(<a href="{GIT}/blob/main/server/smo/{script}"><code>server/smo/{script}</code></a>, 11/09/2026)</p>{corpo}</div>')


SIM, PARC, NAO = '<span class="sim">Sim</span>', '<span class="parc">Parcial</span>', '<span class="nao">Não</span>'


def pagina(n1, n2, n3):
    e = html.escape
    n1, n2, n3 = e(n1), e(n2), e(n3)
    fig = captura_smo()
    figura2 = (f'<figure><img src="{fig}" style="width:92mm" alt="Coluna do SMO na topologia do painel">'
               '<figcaption><b>Figura 2</b> — O SMO na topologia do painel do grupo (visão técnica, captura de '
               '11/09/2026). Em cima, a banda do SMO; embaixo, a rede gerenciada. O ponto verde indica contêiner '
               'em execução no momento da captura.</figcaption></figure>') if fig else ""

    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Relatório — SMO do O-RAN SC (OAM) em ARM64</title><style>{CSS}</style></head><body>

<section class="capa">
  <div class="logo">{logo(40)}</div>
  <div class="inst"><b>CESAR School</b><br>Especialização em Open RAN — Redes Abertas e Tecnologias Emergentes<br>
  Gestão, Orquestração e Automação em Redes OpenRAN</div>
  <div class="meio">
    <h1>Análise do SMO da O-RAN Software Community (OAM) em execução num servidor ARM64</h1>
    <div class="sub">Relatório da avaliação — 1ª parte (30%): Plataformas de Service Management and Orchestration (SMO)</div>
    <div class="fio"></div>
    <div class="quem">Trabalho em grupo<br><b>{n1}</b><br><b>{n2}</b><br><b>{n3}</b><br><br>
    Professor: Lucas Borges de Oliveira</div>
  </div>
  <div class="pe">Recife, 15 de setembro de 2026</div>
</section>

<h2 style="margin-top:0">Resumo</h2>
<p>Este relatório analisa o SMO da O-RAN Software Community (O-RAN SC), na solução do projeto OAM, nos oito
itens do objeto de estudo da disciplina. Em vez de nos limitarmos à documentação, implantamos a solução completa no
servidor ARM64 do grupo — o que exigiu reconstruir sete imagens que só eram publicadas para x86 — e verificamos cada
item com um teste reproduzível contra o SMO em execução. A ferramenta se mostrou sólida no que a O-RAN chama de
<i>RAN NF OAM</i>: a interface O1 por NETCONF/YANG, com leitura e escrita confirmadas dentro do elemento em menos de
0,6 s; o M-plane do Open Fronthaul; a supervisão de falhas e a telemetria por VES e Kafka; e a identidade com
Keycloak. Ela não implementa a interface O2 nem a gestão do O-Cloud, que no O-RAN SC ficam no projeto INF, e não
orquestra o ciclo de vida das funções de rede: percebe a queda de um elemento em cerca de 1 s e o remonta em cerca
de 10 s, mas quem encerra e instancia é a infraestrutura. O relatório está organizado em três casos e informa o
endereço do servidor e do repositório para consulta.</p>
<p class="kw"><b>Palavras-chave:</b> SMO; O-RAN SC; OAM; interface O1; NETCONF/YANG; VES; O2; ARM64.</p>

<h2>1. Introdução</h2>
<p>O SMO (<i>Service Management and Orchestration</i>) é a camada da arquitetura O-RAN que opera a rede de forma
centralizada: configura e inventaria as funções de rede, supervisiona falhas e desempenho, orquestra serviços e
gerencia a infraestrutura de nuvem (O-Cloud). Ele existe porque uma rede O-RAN é desagregada e multifornecedor:
configurar cada O-DU, O-CU, O-RU e RIC individualmente, em centenas de sites, não é eficiente nem escala
(OLIVEIRA, 2026).</p>
<p>A ferramenta estudada é o SMO da <b>O-RAN SC</b>, a comunidade de software aberto criada pela O-RAN Alliance
com a Linux Foundation, na solução <i>docker compose</i> do repositório <code>o-ran-sc/oam</code>. Escolhemos essa
ferramenta por ser a implementação aberta de referência das especificações e por complementar o laboratório do
grupo, que já usa componentes do O-RAN SC (o Non-RT RIC).</p>
<p><b>Método.</b> A solução foi implantada no servidor do grupo (seção 2) e, para cada item do objeto de estudo,
escrevemos um teste que conversa com o SMO pelo seu gateway, como um operador faria, e mede o resultado. Os testes
ficam no painel web do laboratório e no repositório. Os números deste relatório são dessas execuções, em
11/09/2026, e não da documentação; os mesmos testes foram a base da apresentação oral de 12/09/2026. O texto segue
a divisão da apresentação, em três casos (Tabela 1). O trabalho — implantação, testes, apresentação e relatório —
foi feito em conjunto pelos três integrantes do grupo.</p>
{tab(["Caso", "Itens do objeto de estudo", "Testes"], [
    ["1 — Arquitetura, serviços e componentes", "1 Arquitetura · 2 Serviços e funções · 3 Componentes O-RAN suportados",
     "<code>smo_arquitetura.sh</code>"],
    ["2 — Interface O1, provisionamento e ciclo de vida", "4 Interface O1 · 5 Gerenciamento, provisionamento e orquestração · 7 Ciclo de vida de NFs",
     "<code>smo_o1_leitura.sh</code>, <code>smo_o1_provisionamento.sh</code>, <code>smo_ciclo_vida.sh</code>"],
    ["3 — Falhas, telemetria, O-Cloud e O2", "8 Monitoramento, telemetria e falhas · 6 O-Cloud · 4 Interface O2",
     "<code>smo_falhas.sh</code>, <code>smo_telemetria.sh</code>, <code>smo_ocloud.sh</code>"],
], "Tabela 1 — Organização do relatório: casos, itens da avaliação e testes")}

<h2>2. Ambiente, servidor e acesso</h2>
<h3>2.1 O servidor do grupo</h3>
<p>O SMO roda no servidor do laboratório <b>Core5G_ARM64</b>, uma instância AWS EC2 com processador Graviton2
(ARM64, núcleo Neoverse-N1), 4 vCPU, 16 GiB de memória e disco de 80 GB, com Docker 29.6.0 e Docker Compose 5.2.0.
O mesmo servidor hospeda o laboratório das outras disciplinas da especialização (núcleo 5G, gNB e UE simulados,
Non-RT RIC e near-RT RIC) e um painel web de operação, publicado por um proxy Caddy com certificado válido. Por
custo, a instância fica desligada fora dos horários de uso; e, por memória, o SMO (cerca de 4,7 GB) não roda ao
mesmo tempo que a pilha 5G completa.</p>

<h3>2.2 Acesso para o professor</h3>
<p>Todo o material pode ser consultado e reproduzido:</p>
<ul>
<li><b>Repositório público:</b> <a href="{GIT}">{GIT}</a>. A pasta
<a href="{GIT}/tree/main/server/smo"><code>server/smo/</code></a> tem os scripts de construção das imagens ARM64,
de subida e dos sete testes, os ajustes do compose e um README com cada problema encontrado e sua correção; o
roteiro da apresentação está em <a href="{GIT}/blob/main/docs/apresentacao-smo.md"><code>docs/apresentacao-smo.md</code></a>
e o histórico das mudanças no <code>CHANGELOG.md</code> (versões 0.90.0 a 0.98.0).</li>
<li><b>Painel do laboratório:</b> <a href="{PAINEL}">{PAINEL}</a>. No menu lateral, o grupo
“Gestão, Orquestração e Automação (SMO)” tem os sete testes deste relatório e o modal “SMO ao vivo”, com os
elementos sob gerência, os alarmes e os últimos eventos do barramento. A opção “Entrar como aluno”, na tela de
login, dá acesso somente de leitura; para executar os testes, o grupo fornece uma credencial de operador.</li>
<li><b>Console do SMO (ODLUX):</b> <a href="{ODLUX}">{ODLUX}</a>, com login pelo Keycloak do próprio SMO e conta de
operador fornecida pelo grupo.</li>
</ul>
<p>Como a instância é ligada sob demanda, pedimos que o acesso ao painel e ao console seja combinado com o grupo;
o repositório está sempre disponível.</p>

<h3>2.3 Por que houve construção de imagens</h3>
<p>As imagens do O-RAN SC para o SMO são publicadas só para amd64 (conferido com <code>skopeo inspect</code> em
11/09/2026). O grupo reconstruiu as sete que faltavam para ARM64 com duas estratégias (Tabela 2). Na troca de
base, os diretórios da aplicação são copiados da imagem oficial para uma base aarch64 da mesma família, sem
executar nada amd64; na compilação, usam-se os Dockerfiles do próprio O-RAN SC, cujas bases Ubuntu são
multiarquitetura. Os demais serviços (Traefik, Keycloak, PostgreSQL, MariaDB, Kafka) já tinham imagem oficial
multiarquitetura.</p>
{tab(["Componente", "Versão fixada", "Estratégia", "Por quê"], [
    ["Controlador SDN-R (OpenDaylight)", "13.0.1", "troca de base", "aplicação Java sobre base x86"],
    ["Console ODLUX", "13.0.1", "troca de base", "arquivos estáticos servidos por nginx"],
    ["Coletor VES", "1.12.5", "troca de base", "aplicação Java sobre base x86"],
    ["NTSim-NG (base) e servidor de topologia", "1.5.2", "compilação", "binários C: libyang, sysrepo, libnetconf2, netopeer2"],
    ["Simuladores pynts de O-DU e de O-RU", "<code>1212417</code>", "compilação", "mesmas bibliotecas NETCONF em C"],
], "Tabela 2 — As sete imagens reconstruídas para ARM64 (repositório oam em <code>bfdfa32</code>)")}

<h2>3. O SMO do O-RAN SC diante dos serviços do SMO (SMOS)</h2>
<p>Na aula 1, os serviços do SMO (SMOS) foram divididos em quatro grupos: serviços base de plataforma, de operação e
infraestrutura, de automação e aplicações, e de entrega e garantia (OLIVEIRA, 2026). Usamos essa divisão para situar a
ferramenta antes de entrar nos casos. A Tabela 3 resume o que a solução OAM cobre; os detalhes e as medições estão
nas seções 4 a 6.</p>
{tab(["Grupo", "SMOS", "No SMO do O-RAN SC (OAM)", "Situação"], [
    ["Plataforma", "SME — Service Management and Exposure",
     "O gateway (Traefik) expõe cada serviço por nome e o Keycloak autentica por OAuth; não há registro nem descoberta de serviços entre SMOS.", PARC],
    ["Plataforma", "DME — Data Management and Exposure",
     "O Kafka recebe um tópico por domínio de evento VES (falhas, medidas, heartbeat, registro), com acesso HTTP pela kafka-bridge; não há catálogo de tipos de dados nem controle de assinaturas.", PARC],
    ["Operação e infraestrutura", "RAN NF OAM",
     "É o núcleo da solução: provisionamento por NETCONF/RESTCONF, supervisão de falhas (VES e notificações NETCONF), relatórios de medidas em arquivo (3GPP TS 28.532) e eventos em fluxo (VES). Rastreamento, coleta de logs e gestão de software das PNFs não foram exercitados.", SIM],
    ["Operação e infraestrutura", "TE&amp;IV — Topology Exposure and Inventory",
     "Há um servidor de topologia (NTSim-NG com TAPI) e o inventário de elementos montados no controlador; a exposição de topologia não foi exercitada nos testes.", PARC],
    ["Operação e infraestrutura", "NFO e FOCOM",
     "Ausentes: dependem da interface O2 (DMS e IMS), que no O-RAN SC é do projeto INF.", NAO],
    ["Automação e aplicações", "rApp Management, A1 Related, PMI, AI/ML workflow, RAN Analytics, Software Package Onboarding",
     "Fora do OAM: no O-RAN SC ficam em outros projetos, como o Non-RT RIC.", NAO],
    ["Entrega e garantia", "SO e SA",
     "Ausentes: não há orquestração nem garantia de serviço ou de fatia de rede.", NAO],
], "Tabela 3 — Cobertura dos grupos de SMOS pela solução OAM do O-RAN SC")}
<p>A conclusão já aparece aqui: o OAM do O-RAN SC é, essencialmente, um <b>SMO de gerência de funções de rede</b>
(FCAPS pela O1 e pelo M-plane), com a plataforma mínima para isso funcionar. Orquestração, O-Cloud e automação
ficam em outros projetos da mesma comunidade.</p>

<h2 class="quebra">4. Caso 1 — Arquitetura, serviços e componentes</h2>
<div class="resp">Itens 1, 2 e 3 do objeto de estudo</div>

<h3>4.1 Arquitetura</h3>
<p>A solução é dividida em três camadas, cada uma um projeto <i>docker compose</i> que sobe nesta ordem
(Figura 1). A camada <b>common</b> é a plataforma: o gateway Traefik, porta de entrada HTTPS e do NETCONF
<i>call home</i>; o Keycloak, com seu PostgreSQL, para usuários, papéis e login; o MariaDB onde o controlador guarda
estado, alarmes e histórico; o Kafka com Zookeeper, a ponte HTTP e o console; e o servidor de topologia. A camada
<b>oam</b> é a gerência propriamente dita: o controlador SDN-R, baseado no OpenDaylight, que é o cliente NETCONF da
O1; o console ODLUX; e o coletor de eventos VES. A camada <b>network</b> são os elementos gerenciados: uma O-DU e dois
O-RU simulados pelo pynts, o simulador do próprio O-RAN SC.</p>
<figure>{diagrama()}
<figcaption><b>Figura 1</b> — Arquitetura do SMO do O-RAN SC como implantada no servidor do grupo. Linhas roxas:
tráfego interno do SMO; verdes: interfaces com os elementos. A O-DU também envia VES (medidas, heartbeat); a linha
foi omitida para não cruzar o desenho. O Caddy é do servidor do grupo, não do upstream (seção 7).</figcaption></figure>
{tab(["Camada", "Contêineres", "Papel", "Imagem ARM64"], [
    ["common", "<code>gateway</code>", "Traefik: termina HTTPS, roteia por nome e recebe o NETCONF call home", "oficial"],
    ["common", "<code>identity</code>, <code>identitydb</code>", "Keycloak e PostgreSQL: usuários, papéis e login OAuth", "oficial"],
    ["common", "<code>persistence</code>", "MariaDB do controlador: conexões, alarmes e histórico", "oficial"],
    ["common", "<code>zookeeper</code>, <code>kafka</code>, <code>kafka-bridge</code>, <code>kafka-ui</code>", "barramento de eventos, acesso HTTP e console", "oficial"],
    ["common", "<code>topology</code>", "servidor de topologia (NTSim-NG + OpenDaylight, TAPI)", "compilada"],
    ["oam", "<code>controller</code>", "SDN-R/OpenDaylight: NETCONF com os elementos, RESTCONF para os consumidores", "troca de base"],
    ["oam", "<code>odlux</code>", "console web do operador", "troca de base"],
    ["oam", "<code>ves-collector</code>", "recebe eventos VES e publica no Kafka", "troca de base"],
    ["network", "<code>pynts-o-du-o1</code>", "O-DU simulada, com O1", "compilada"],
    ["network", "<code>pynts-o-ru-hybrid</code>, <code>pynts-o-ru-hierarchical</code>", "O-RU simulados, com M-plane", "compilada"],
], "Tabela 4 — Os 15 contêineres em execução (9 na common, 3 na oam, 3 na network)")}

<h3>4.2 Serviços e funções disponibilizados</h3>
<p>Cada serviço do SMO tem um nome, e o Traefik roteia o HTTPS por esse nome. O teste leu as rotas direto da API do
gateway: são <b>8 serviços</b> (Tabela 5), além das portas de call home 4334 (SSH) e 4335 (TLS), encaminhadas ao
controlador. Na época da medição os nomes ainda usavam o domínio de exemplo do upstream
(<code>smo.o-ran-sc.org</code>); depois o grupo o trocou por um subdomínio do servidor (seção 7).</p>
{tab(["Serviço", "Nome no gateway", "Função"], [
    ["controller", "<code>controller.dcn.smo.o-ran-sc.org</code>", "O1: RESTCONF para consumidores e NETCONF com os elementos"],
    ["sdnc-web", "<code>odlux.oam.smo.o-ran-sc.org</code>", "console do operador (ODLUX): conexões, falhas, configuração"],
    ["identity", "<code>identity.smo.o-ran-sc.org</code>", "identidade: usuários, papéis e login (Keycloak)"],
    ["ves", "<code>ves-collector.dcn.smo.o-ran-sc.org</code>", "coleta de eventos VES: falhas, medidas, heartbeat, registro"],
    ["kafka-bridge", "<code>kafka-bridge.smo.o-ran-sc.org</code>", "barramento de eventos por HTTP"],
    ["kafka-ui", "<code>kafka-ui.smo.o-ran-sc.org</code>", "console do barramento Kafka"],
    ["topology", "<code>topology.smo.o-ran-sc.org</code>", "topologia e inventário (TAPI)"],
    ["gateway", "<code>gateway.smo.o-ran-sc.org</code>", "painel do próprio gateway"],
], "Tabela 5 — Serviços publicados pelo gateway")}
<p>Do ponto de vista do operador, as funções ficam no ODLUX: a aba <i>Connect</i> lista os elementos montados e o
estado da sessão NETCONF; a aba <i>Fault</i> mostra alarmes ativos e histórico; e há telas de configuração sobre os
modelos YANG de cada elemento. Os mesmos dados são acessíveis a qualquer sistema pelo RESTCONF do controlador e
pelos tópicos do Kafka — é por esses caminhos que os testes deste relatório trabalham.</p>

<h3>4.3 Componentes O-RAN suportados</h3>
<p>Um elemento é gerenciável na medida dos modelos YANG que ele anuncia ao se conectar. A O-DU simulada anunciou
<b>154 modelos</b> (49 da O-RAN, 30 do 3GPP, 38 da IETF e 37 outros) e o O-RU híbrido, <b>114</b> (39 da O-RAN). O
O-RU hierárquico não aparece no controlador, e isso é o esperado: no modelo hierárquico do M-plane, só a O-DU fala com
o O-RU. A Tabela 6 resume as interfaces.</p>
{tab(["Interface", "Entre", "Nesta solução", "Evidência"], [
    ["O1 (NETCONF/YANG)", "SMO ↔ O-DU (e O-CU)", SIM, "O-DU <i>connected</i> com 154 modelos YANG"],
    ["M-plane do Open Fronthaul, híbrido", "SMO ↔ O-RU", SIM, "O-RU <i>connected</i> com 114 modelos YANG"],
    ["M-plane, hierárquico", "O-DU ↔ O-RU", "Sim, fora da visão do SMO", "o O-RU hierárquico não é montado no controlador"],
    ["VES", "elementos → SMO", SIM, "coletor publicando cada domínio num tópico do Kafka"],
    ["A1", "Non-RT RIC ↔ near-RT RIC", NAO, "fica no projeto Non-RT RIC do O-RAN SC"],
    ["O2", "SMO ↔ O-Cloud", NAO, "fica no projeto INF do O-RAN SC (seção 6.3)"],
    ["E2", "near-RT RIC ↔ nós E2", "Não se aplica", "interface do near-RT RIC, não do SMO"],
], "Tabela 6 — Interfaces e componentes O-RAN")}
<p>Uma limitação prática para o laboratório: o gNB monolítico do OpenAirInterface, usado nas outras disciplinas, não
tem agente O1. Por isso a O1 foi demonstrada com os simuladores do O-RAN SC, que implementam os modelos da O-RAN e
do 3GPP de fato.</p>
{evidencia("Arquitetura do SMO", "smo_arquitetura.sh",
    "15 contêineres em 3 camadas, todos em imagens arm64 · 8 serviços roteados pelo gateway · 2 elementos O-RAN "
    "<i>connected</i> (O-DU pela O1 e O-RU híbrido pelo M-plane).",
    "Saúde pelo gateway: realm <code>onap</code> do Keycloak, <code>/ready</code> do controlador e página do ODLUX, "
    "todos com HTTP 200. Resultado: “arquitetura completa no ar — O1, M-plane e VES funcionando; A1 e O2 ficam fora do OAM”.")}
{figura2}

<h2>5. Caso 2 — Interface O1, provisionamento e ciclo de vida</h2>
<div class="resp">Itens 4 (O1), 5 e 7 do objeto de estudo</div>

<h3>5.1 Como a O1 é implementada</h3>
<p>A O1 é a interface de gerência dos elementos O-RAN e, nesta solução, é NETCONF (RFC 6241) com modelos YANG
(RFC 7950). O controlador SDN-R é o cliente NETCONF: cada elemento, ao iniciar, abre a conexão na direção do SMO
(<i>call home</i>, RFC 8071) pelas portas 4334 (SSH) ou 4335 (TLS) do gateway, e o controlador “monta” o elemento na
topologia <code>topology-netconf</code>. A partir daí, a árvore YANG do elemento fica exposta por RESTCONF (RFC 8040),
que é o mesmo modelo sobre HTTP com JSON. Quem consome — o ODLUX, os testes ou qualquer outro sistema — fala RESTCONF
com o controlador, que traduz para operações NETCONF no elemento. A O-DU usa NETCONF sobre TLS (porta 6513); o O-RU,
NETCONF sobre SSH (porta 830), como pede o M-plane.</p>
{caminho("painel ou ODLUX", "gateway (HTTPS)", "controlador (RESTCONF)", "NETCONF/TLS :6513", "O-DU (datastore sysrepo)")}

<h3>5.2 Leitura: o SMO enxerga a configuração do elemento</h3>
<p>O teste percorre a árvore de recursos de rede do 3GPP (TS 28.541) que a O-DU anuncia:
<code>ManagedElement → GNBDUFunction → NRCellDU</code>. Duas consultas RESTCONF, convertidas em <i>get-config</i>
NETCONF, trouxeram a configuração da gNB-DU e da célula NR em <b>512 ms</b> (433 ms em outra execução). Alguns valores
são os de fábrica do simulador (o nome <code>hostname_here</code>, o ARFCN igual a 1); o que importa é que vieram
do elemento pela O1.</p>
{tab(["Objeto", "Atributo", "Valor lido"], [
    ["GNBDUFunction", "gNBId · gNBIdLength · gNBDUId", "1 · 24 bits · 1"],
    ["GNBDUFunction", "gNBDUName", "<code>hostname_here</code>"],
    ["NRCellDU", "cellLocalId · nRPCI", "1 · 1"],
    ["NRCellDU", "arfcnDL · ssbFrequency", "1 · 1"],
    ["NRCellDU", "ssbSubCarrierSpacing · ssbPeriodicity", "15 kHz · 5 ms"],
    ["NRCellDU", "pLMNInfoList", "PLMN 310/410 com 6 fatias (SST 1 a 6)"],
    ["NRCellDU", "total de atributos", "21"],
], "Tabela 7 — Configuração da O-DU lida pela O1")}

<h3>5.3 Provisionamento: escrever, conferir no equipamento e desfazer</h3>
<p>Para provisionar, o teste muda um parâmetro visível e inofensivo — o nome da gNB-DU — por um <b>PATCH</b> RESTCONF,
que o controlador transforma em <i>edit-config</i> NETCONF. A prova não é a tela do SMO: o teste lê o valor de novo
pela O1 <b>e</b> dentro do datastore <code>running</code> da própria O-DU (sysrepo), e depois desfaz pelo mesmo
caminho. Se algo falhar no meio, o script restaura o valor original antes de sair.</p>
{tab(["Etapa", "Operação", "Resultado"], [
    ["1. Estado atual", "GET RESTCONF", "<code>gNBDUName = hostname_here</code>"],
    ["2. Escrita", "PATCH em <code>ManagedElement=ManagedElement-002/GNBDUFunction=GNBDUFunction-001/attributes</code>", "HTTP 200 em <b>289 ms</b>"],
    ["3. Verificação", "GET pela O1 e leitura no sysrepo da O-DU", "<code>core5g-apresentacao-185353</code> nos dois lados"],
    ["4. Reversão", "PATCH com o valor original", "HTTP 200; datastore de volta a <code>hostname_here</code>"],
], "Tabela 8 — Provisionamento pela O1, ponta a ponta (execução completa em 3 s)")}
<p><b>Análise.</b> Os mecanismos de gerenciamento e provisionamento são os da O1: operações de configuração sobre os
modelos YANG de cada elemento, síncronas, com confirmação do elemento, e a descoberta dos modelos no momento da conexão.
O que a solução não traz é <b>orquestração</b>: não há modelos de serviço, fluxos de trabalho que coordenem vários
elementos numa transação, nem intenção de alto nível. Cada escrita é por elemento, e coordenar mudanças em rede fica
para quem consome o RESTCONF.</p>

<h3>5.4 Ciclo de vida de uma função de rede</h3>
<p>O teste encerra o O-RU híbrido, mede quando o SMO percebe, instancia de novo e mede quando ele volta à gerência.
Encerrar e instanciar são feitos pelo Docker, porque a solução não tem quem faça isso (seção 6.3); o que se observa é
como o SMO acompanha cada fase.</p>
{tab(["Fase", "O que aconteceu", "Tempo"], [
    ["Em operação", "O-RU <i>connected</i> no controlador", "—"],
    ["Encerrar", "<code>docker stop</code>; o controlador registra a perda (elemento ausente)", "<b>1 s</b>"],
    ["Instanciar", "<code>docker start</code>; o O-RU faz call home e é montado de novo, sem configuração manual", "<b>10 s</b> (13 s em outra execução)"],
    ["Registro", "<i>connectionlog</i> do controlador: Unmounted 21:54:06,3 → Mounted 21:54:17,6 → Connected 21:54:18,0 (UTC)", "—"],
    ["De volta", "o O-RU anuncia de novo os 114 modelos YANG", "teste completo em 19 s"],
], "Tabela 9 — Ciclo de vida do O-RU percebido pelo SMO")}
<p><b>Análise.</b> No ciclo de vida, o SMO do O-RAN SC faz a parte de <b>supervisão</b>: percebe a queda em cerca de
um segundo, guarda o histórico e remonta o elemento automaticamente graças ao call home. Instanciar, escalar e encerrar
a função de rede — o papel do NFO, pela O2 DMS — não está na solução. Encontramos também uma limitação operacional: os
simuladores só fazem call home ao iniciar; se o controlador reiniciar, os elementos precisam ser recriados para voltar
à gerência.</p>

<h2 class="quebra">6. Caso 3 — Monitoramento, telemetria, falhas, O-Cloud e O2</h2>
<div class="resp">Itens 8, 6 e 4 (O2) do objeto de estudo</div>

<h3>6.1 Gerenciamento de falhas</h3>
<p>A solução tem dois canais de falha. Pelo <b>VES</b>, o elemento envia o evento ao coletor por HTTPS, e o coletor o
publica no tópico de falhas do Kafka, de onde qualquer sistema pode assinar (análise, rApps, o console do barramento).
Pelas <b>notificações NETCONF</b>, o controlador recebe os alarmes do elemento e os guarda no banco como alarmes ativos
e histórico, que o ODLUX mostra na aba <i>Fault</i>.</p>
{caminho("elemento", "VES 7.2.1 (HTTPS)", "ves-collector", "Kafka: unauthenticated.SEC_FAULT_OUTPUT", "consumidores")}
<p>O teste levanta um alarme <b>linkDown</b> na interface <code>fronthaul-0</code>, com severidade CRITICAL, e depois o
limpa. A O-DU simulada não tem uma receita de alarmes; por isso o teste faz o papel do elemento, com o mesmo formato
VES 7.2.1 que ela usaria. Todo o caminho a partir do coletor é o real.</p>
{tab(["Evento", "Coletor VES", "Chegada ao tópico de falhas", "Conteúdo no Kafka"], [
    ["Alarme", "HTTP 202", "<b>1,27 s</b> após o envio", "CRITICAL · linkDown em fronthaul-0 · origem pynts-o-du-o1"],
    ["Limpeza", "HTTP 202", "<b>472 ms</b> após o envio", "NORMAL · mesma condição e origem"],
], "Tabela 10 — Alarme e limpeza pelo caminho de falhas")}
<p>O tópico passou de 5 para 7 eventos. No mesmo momento, o controlador tinha 0 alarmes NETCONF ativos e 6 no
histórico — o outro canal, alimentado pelas notificações dos elementos.</p>

<h3>6.2 Monitoramento e telemetria</h3>
<p>A O-DU mede sozinha. Sua configuração de desempenho (PM) define coleta a cada <b>60 s</b>, validade de 180 s e três
contadores de usuários ativos por DRB. A cada período, ela grava um arquivo XML no formato <i>measData</i> do 3GPP
(TS 28.532) e, em vez de esperar o SMO perguntar, avisa por um evento VES <b>FileReady</b>, que chega ao tópico de
desempenho do Kafka com o endereço do arquivo.</p>
{caminho("O-DU mede (60 s)", "arquivo 3GPP TS 28.532", "VES FileReady", "Kafka: SEC_3GPP_PERFORMANCEASSURANCE_OUTPUT", "consumidor busca o arquivo")}
{tab(["Item", "Valor medido"], [
    ["Contadores configurados", "DRB.MeanActiveUeDl, DRB.MeanActiveUeUl, DRB.MaxActiveUeDl"],
    ["Último arquivo", "<code>A20260911.2152+0000-2153+0000_1_pynts-o-du-o1.xml</code>, gravado 59 s antes da leitura (3 arquivos guardados)"],
    ["Objeto medido e período", "<code>ManagedElement=pynts-o-du-o1,GNBCUCPFunction=1,NRCellCU=1</code> · PT1M"],
    ["Valores (grupos 5.1.1.4.1 e 5.1.1.4.2)", "DRB.MeanActiveUeDl = 0 · DRB.MeanActiveUeUl = 17 · DRB.MaxActiveUeDl = 3"],
    ["Aviso no Kafka", "<code>PyNTS_FileReady</code>, domínio <code>stndDefined</code>, anunciando o arquivo seguinte por SFTP"],
    ["Eventos recebidos por tópico", "140 avisos de medida · 5 heartbeats · 4 registros de PNF"],
], "Tabela 11 — Telemetria da O-DU")}
<p>Os <b>heartbeats</b> dizem ao SMO quem está vivo, e o <b>registro de PNF</b> (<i>pnfRegistration</i>) é o aviso do
elemento de que acabou de chegar. <b>Análise:</b> a solução entrega bem o transporte de telemetria — aviso por evento,
barramento com um tópico por domínio e acesso por HTTP. Nenhum dos 15 contêineres, porém, busca e interpreta o
arquivo de medidas: a coleta fica para um consumidor (no ONAP, esse papel é do <i>Data File Collector</i>). Relatórios
de medidas em fluxo contínuo pela O1 também não foram demonstrados.</p>

<h3>6.3 O-Cloud e a interface O2</h3>
<p>Aqui a resposta é direta: <b>o OAM do O-RAN SC não implementa a O2</b>. Não há IMS (<i>Infrastructure Management
Services</i>, o inventário e a supervisão da nuvem) nem DMS (<i>Deployment Management Services</i>, a implantação das
funções de rede). No O-RAN SC, a O2 fica no projeto <b>INF</b>, sobre StarlingX, que pede uma máquina dedicada. Para
tornar a lacuna concreta, o teste lê do próprio servidor o que um IMS e um DMS exporiam do O-Cloud do laboratório
(Tabela 12).</p>
{tab(["Papel na O2", "Informação", "Valor no servidor"], [
    ["IMS: pool de recursos", "arquitetura · vCPU · memória · disco", "aarch64 (Neoverse-N1) · 4 · 15 GiB utilizáveis · 77 GB"],
    ["IMS: estado", "carga (1, 5 e 15 min)", "12,6 · 10,6 · 7,6 (a pilha 5G do laboratório estava ligada)"],
    ["DMS: gerenciador de implantação", "runtime", "Docker 29.6.0 · Compose 5.2.0"],
    ["DMS: implantações", "projetos do SMO", "smo-common (9 contêineres) · smo-oam (3) · smo-network (3)"],
    ["DMS: consumo", "memória dos maiores", "topology 1,23 GiB · controller 885 MiB · kafka 700 MiB · identity 577 MiB · ves-collector 372 MiB"],
    ["DMS: consumo", "total do SMO com os simuladores", "<b>4,7 GB</b>"],
], "Tabela 12 — O que uma O2 exporia do O-Cloud do laboratório (lido sem O2)")}
<p><b>Análise.</b> A carga medida mostra por que a gestão do O-Cloud importa: com a pilha 5G ligada, o controlador do
SMO chegou a ficar 25 s sem responder, e numa subida levou mais de 5 minutos para ficar saudável. Um SMO com O2
enxergaria essa disputa por recursos e poderia agir, por exemplo realocando funções de rede. Nesta solução, essa
informação só existe fora do SMO. Para a gestão do O-Cloud, portanto, o SMO do O-RAN SC precisa ser combinado com o
projeto INF ou com outro orquestrador que cumpra o papel da O2.</p>

<h2>7. Segurança, operação e achados de engenharia</h2>
<h3>7.1 Publicação do console na internet</h3>
<p>Para que o console pudesse ser acessado sem túnel, o grupo publicou só o ODLUX e o login pelo Caddy do servidor,
com certificado válido; o Traefik continua ouvindo apenas em 127.0.0.1. Antes disso, auditamos a configuração de
identidade que vem no upstream e encontramos, no realm <code>onap</code> do Keycloak: <b>auto-cadastro aberto</b>,
recuperação de senha ligada sem e-mail configurado, nenhuma proteção contra força bruta e seis usuários ativos, cinco
deles com a senha padrão pública do projeto. Um script idempotente (<code>smo_acesso_web.sh</code>) fecha o
cadastro e a recuperação, liga a proteção contra força bruta e deixa ativo um único operador. O Caddy também recusa
autenticação Basic, o formulário de login local do ODLUX — que emitia token para o administrador do controlador com a
senha padrão, o que confirmamos pela internet antes do bloqueio —, o console de administração e o realm
<code>master</code> do Keycloak.</p>
<p>Uma limitação permanece: com o OAuth ligado, o canal de notificações em tempo real do ODLUX (WebSocket) é recusado
pelo controlador, porque o console abre essa conexão sem credencial. O login, as abas <i>Connect</i> e <i>Fault</i> e
as demais telas funcionam pelo RESTCONF; só as notificações instantâneas do cabeçalho não chegam.</p>

<h3>7.2 Problemas encontrados na montagem</h3>
<p>Nenhum dos problemas abaixo é de ARM64: todos apareceriam num servidor x86 com o mesmo software de hoje. Eles mostram
que a solução de referência envelhece rápido em relação às suas dependências.</p>
{tab(["Sintoma", "Causa", "Correção"], [
    ["Servidor de topologia não sobe (<code>Invalid CEN header</code>)",
     "o OpenJDK 11 atual valida o campo ZIP64 dos jars (JDK-8302483) e os jars do Karaf não passam",
     "<code>-Djdk.util.zip.disableZip64ExtraFieldValidation=true</code> na imagem"],
    ["Todas as rotas do gateway respondem 404", "o Traefik v3.3.6 do upstream exige a API 1.24 do Docker, que o Docker 29 recusa",
     "Traefik v3.6.25, que negocia a versão"],
    ["Script de usuários do Keycloak falha", "exige a variável <code>USER</code> dentro do contêiner", "variável passada pelo script de subida"],
    ["ODLUX sem elementos após recriar o controlador", "cada contêiner novo escolhe outro <code>controllerId</code>, e o banco guarda as linhas com o id antigo",
     "realinhar o banco ao id atual a cada subida"],
    ["RESTCONF sem resposta depois de religar a instância", "o Traefik passou a usar o endereço de outra rede Docker, onde o gateway não estava",
     "gateway conectado às três redes do SMO"],
    ["Controlador lento ou marcado como não saudável", "disputa de CPU com a pilha 5G do laboratório", "não rodar as duas juntas"],
], "Tabela 13 — Problemas e correções (documentados no README de server/smo)")}

<h2>8. Avaliação consolidada</h2>
{tab(["Item do objeto de estudo", "Avaliação", "Síntese"], [
    ["1. Arquitetura", SIM, "três camadas bem separadas (plataforma, gerência, rede), 15 contêineres, um gateway como entrada única"],
    ["2. Serviços e funções de SMO", PARC, "8 serviços; forte em gerência de NFs, sem registro de serviços, catálogo de dados, orquestração ou garantia"],
    ["3. Componentes O-RAN suportados", SIM, "O-DU pela O1, O-RU pelo M-plane (híbrido e, indiretamente, hierárquico) e VES; A1 e E2 fora"],
    ["4. Interfaces O1 e O2", PARC, "O1 completa e verificada (leitura em ~0,5 s, escrita confirmada no elemento); O2 ausente"],
    ["5. Gerenciamento, provisionamento e orquestração", PARC, "gerenciamento e provisionamento por elemento funcionam; não há orquestração"],
    ["6. Gestão do O-Cloud", NAO, "sem IMS nem DMS; a informação existe só fora do SMO"],
    ["7. Ciclo de vida de NFs", PARC, "supervisiona (perda em ~1 s, remontagem em ~10 s por call home); não instancia nem encerra"],
    ["8. Monitoramento, telemetria e falhas", SIM, "alarme ao Kafka em ~0,5–1,3 s, medidas TS 28.532 com FileReady, heartbeats e alarmes NETCONF; sem coletor de arquivos"],
], "Tabela 14 — Os oito itens da avaliação")}
<p><b>Pontos fortes.</b> Aderência real às especificações que implementa: os elementos anunciam modelos da O-RAN e do
3GPP, a O1 é NETCONF de verdade, e o VES segue o formato 7.2.1 com um tópico por domínio. Tudo é acessível por APIs
abertas (RESTCONF e Kafka), o que permitiu automatizar os testes sem passar pela interface gráfica. Os simuladores do
próprio O-RAN SC tornam a ferramenta estudável sem hardware de rádio.</p>
<p><b>Limitações.</b> Cobre só uma parte dos SMOS: não tem O2, O-Cloud, orquestração nem garantia de serviço, e depende
de outros projetos do O-RAN SC para A1 e rApps. As configurações de segurança do upstream são de laboratório e
precisam ser endurecidas antes de qualquer exposição. As dependências fixadas (JDK, Traefik) já não funcionam com as
versões atuais sem ajustes.</p>
<p><b>Para a 2ª parte (26/09).</b> O provisionamento e a gerência de uma pilha Open RAN com esta ferramenta devem se
apoiar no que ela entrega — O1, M-plane, falhas e telemetria — sobre funções de rede com agente O1, como os
simuladores do O-RAN SC, já que o gNB do OpenAirInterface do laboratório não tem O1. A instanciação das funções de
rede precisará de um orquestrador externo que faça o papel da O2 DMS, e esse limite deve aparecer explicitamente na
análise.</p>

<h2 class="quebra">9. Conclusão</h2>
<div class="junto">
<p>A pergunta que o trabalho faz — o que uma plataforma de SMO entrega, de fato — tem, no caso do SMO da O-RAN SC,
uma resposta que só a implantação revela. A solução OAM é uma implementação <b>funcional e verificável</b> da
gerência de funções de rede O-RAN, e não uma maquete: os elementos anunciam modelos YANG reais da O-RAN e do 3GPP,
a O1 é NETCONF de verdade, e tudo o que a interface gráfica mostra está disponível por APIs abertas. Foi isso que
permitiu responder a cada item da avaliação com uma medição, e não com uma citação da documentação.</p>
<p>O que medimos no servidor do grupo, em ARM64 nativo:</p>
<ul>
<li>a leitura da configuração 3GPP de uma O-DU pela O1, em <b>512 ms</b>, com os 154 modelos YANG que ela anuncia;</li>
<li>a escrita de um parâmetro pela O1, aceita em <b>289 ms</b> e confirmada <b>dentro do datastore do elemento</b>,
e depois desfeita pelo mesmo caminho;</li>
<li>a queda de um O-RU percebida em <b>1 s</b> e a remontagem automática por call home em <b>10 s</b>, com o
histórico registrado pelo controlador;</li>
<li>um alarme VES no barramento do SMO em <b>1,27 s</b>, e a limpeza em <b>472 ms</b>;</li>
<li>as medidas 3GPP TS 28.532 da O-DU chegando por aviso <b>FileReady</b>, sem o SMO precisar consultar o elemento;</li>
<li>o conjunto inteiro — 15 contêineres e os simuladores — operando com <b>4,7 GB</b> de memória e pouca CPU.</li>
</ul>
</div>
<p>A mesma implantação mostra com clareza onde a ferramenta termina. Ela cobre bem um dos serviços de SMO da
arquitetura O-RAN, o <i>RAN NF OAM</i>, e a plataforma mínima que ele exige; não implementa a interface <b>O2</b> nem
a gestão do <b>O-Cloud</b>, não orquestra o ciclo de vida das funções de rede e não traz os serviços de entrega e
garantia. No O-RAN SC, essas peças existem, mas em outros projetos — o INF, para a O2, e o Non-RT RIC, para a A1 e as
rApps. Some-se a isso que as configurações de segurança que vêm no upstream são de laboratório: encontramos o
auto-cadastro aberto e cinco usuários com senha pública, o que tivemos de fechar antes de publicar o console. A
conclusão prática é que o SMO da O-RAN SC deve ser tratado como <b>base de referência e ambiente de estudo</b>, e não
como produto pronto: quem for usá-lo precisa saber exatamente quais interfaces ele cobre e compor o resto.</p>
<p>Para a 2ª parte da avaliação, esse limite vira o plano de trabalho: usaremos o que a ferramenta entrega — O1,
M-plane, falhas e telemetria — para provisionar e gerenciar a pilha Open RAN, sobre funções de rede que tenham
agente O1, e trataremos a instanciação dessas funções por um orquestrador externo, no papel que caberia à O2 DMS,
dizendo isso de forma explícita na análise. Por fim, uma observação de método: todo o ambiente, os sete testes e os
números deste relatório estão no repositório público do grupo e podem ser reproduzidos por terceiros — inclusive
os problemas que encontramos e como foram corrigidos.</p>
<div class="fecho"><p><b>Em uma frase:</b> o SMO da O-RAN SC gerencia funções de rede O-RAN com solidez e
transparência, mas orquestrar a rede e a nuvem que a sustenta ainda exige outras peças.</p></div>

<h2>Referências</h2>
<div class="ref">
<p>3GPP. <b>TS 28.532</b>: Management and orchestration; Generic management services. 3rd Generation Partnership Project.</p>
<p>3GPP. <b>TS 28.541</b>: Management and orchestration; 5G Network Resource Model (NRM). 3rd Generation Partnership Project.</p>
<p>BIERMAN, A.; BJORKLUND, M.; WATSEN, K. <b>RFC 8040</b>: RESTCONF Protocol. IETF, 2017.</p>
<p>BJORKLUND, M. <b>RFC 7950</b>: The YANG 1.1 Data Modeling Language. IETF, 2016.</p>
<p>ENNS, R. et al. <b>RFC 6241</b>: Network Configuration Protocol (NETCONF). IETF, 2011.</p>
<p>ONAP. <b>VES Event Listener 7.2.1</b>. Open Network Automation Platform.</p>
<p>OLIVEIRA, L. B. de. <b>Aula 0 — Revisão</b> e <b>Aula 1 — Service Management and Orchestrator (SMO)</b>. Gestão,
Orquestração e Automação em Redes OpenRAN. Recife: CESAR School, 2026. Slides de aula.</p>
<p>O-RAN ALLIANCE. <b>O-RAN Architecture Description</b> (O-RAN.WG1). Especificação técnica.</p>
<p>O-RAN ALLIANCE. <b>O-RAN Operations and Maintenance Interface Specification</b> (O1). Especificação técnica.</p>
<p>O-RAN ALLIANCE. <b>O-RAN Management Plane Specification</b> (Open Fronthaul M-plane, O-RAN.WG4.MP). Especificação técnica.</p>
<p>O-RAN ALLIANCE. <b>O2 Interface General Aspects and Principles</b> (O-RAN.WG6). Especificação técnica.</p>
<p>O-RAN SOFTWARE COMMUNITY. <b>Repositório oam</b> (solução docker compose do SMO). Disponível em:
<a href="https://github.com/o-ran-sc/oam">https://github.com/o-ran-sc/oam</a>. Documentação:
<a href="https://docs.o-ran-sc.org">https://docs.o-ran-sc.org</a>.</p>
<p>WATSEN, K. <b>RFC 8071</b>: NETCONF Call Home and RESTCONF Call Home. IETF, 2017.</p>
<p>Repositório do grupo: <b>Core5G_ARM64</b>. Disponível em: <a href="{GIT}">{GIT}</a>.</p>
</div>

<h2>Apêndice A — Como reproduzir</h2>
<p>No servidor, a partir de <code>server/smo/</code> do repositório:</p>
{tab(["Comando", "O que faz"], [
    ["<code>./build_arm64.sh</code>", "constrói as sete imagens ARM64 (primeira vez: 15 a 25 minutos)"],
    ["<code>./up_smo.sh</code>", "sobe common, usuários do Keycloak, oam e simuladores, com os ajustes do servidor"],
    ["<code>./test_smo.sh</code>", "confere o SMO pelo gateway: realm, controlador, elementos conectados, VES e Kafka"],
    ["<code>./smo_arquitetura.sh</code> … <code>./smo_ocloud.sh</code>", "os sete testes deste relatório (também no painel)"],
    ["<code>./smo_ao_vivo.sh</code>", "retrato do SMO em JSON: elementos, conexões, alarmes, barramento e contêineres"],
    ["<code>./down_smo.sh</code>", "derruba as três camadas na ordem inversa"],
])}
</body></html>"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--integrantes", required=True, help="três nomes separados por vírgula, na ordem dos casos")
    nomes = [n.strip() for n in ap.parse_args().integrantes.split(",") if n.strip()]
    if len(nomes) != 3:
        ap.error("o relatório tem 3 casos: passe exatamente três nomes")
    os.makedirs(OUT, exist_ok=True)
    hp = os.path.join(OUT, NOME + ".html")
    with open(hp, "w", encoding="utf-8") as f:
        f.write(pagina(*nomes))
    pdf = os.path.join(OUT, NOME + ".pdf")
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    if chrome:
        subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        "--print-to-pdf=" + pdf, "file://" + hp], check=True, capture_output=True, timeout=180)
    desk = next((d for d in (os.path.join(os.path.expanduser("~"), n) for n in ("Área de trabalho", "Desktop"))
                 if os.path.isdir(d)), None)
    if desk and os.path.exists(pdf):
        shutil.copy(pdf, desk)
        print("PDF na Área de trabalho:", os.path.join(desk, NOME + ".pdf"))
    print("pdf:", pdf)
