#!/usr/bin/env python3
"""Gera o roteiro da apresentacao do Grupo 6 (22 min, painel ao vivo).

Nao e slide: e o guia de quem apresenta - o que falar, o que clicar, os numeros
na mao e as perguntas provaveis com resposta. Sai em PDF para abrir no celular.

Os numeros vem de cp2_indicadores.py: se a analise mudar, o roteiro muda junto.
Uso: python3 roteiro_apresentacao.py
"""
import os
import shutil
import subprocess
import sys

import cp2_indicadores as cp2

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
LOGO = os.path.join(REPO, "server/panel/static/ops/cesar-marca.svg")
OUT = os.path.join(HERE, "entrega")
os.makedirs(OUT, exist_ok=True)


def n(v, casas=1):
    return f"{v:,.{casas}f}".replace(",", "\x00").replace(".", ",").replace("\x00", ".")


CSS = """
@page { size: A4; margin: 16mm 15mm 14mm; }
*{box-sizing:border-box}
body{font:11pt/1.5 Georgia,'Times New Roman',serif;color:#20272e;max-width:180mm;margin:0 auto}
.hd{display:flex;align-items:center;gap:12px;border-bottom:2px solid #f04e23;padding-bottom:9px}
.hd h1{font:700 16pt/1.15 Helvetica,Arial,sans-serif;margin:0;color:#1a2733}
.hd .sub{font:400 10.5pt/1.3 Helvetica,Arial,sans-serif;color:#5a6b7c;margin-top:2px}
h2{font:700 12.5pt/1.2 Helvetica,Arial,sans-serif;color:#1a2733;margin:15pt 0 6pt;page-break-after:avoid}
p{margin:0 0 7pt}
.passo{display:flex;gap:10px;margin:0 0 9pt;page-break-inside:avoid}
.passo .t{flex:0 0 20mm;font:700 10pt/1.35 Helvetica,Arial,sans-serif;color:#f04e23;padding-top:1px}
.passo .c{flex:1}
.passo .c b{color:#1a2733}
.fala{background:#f6f8fb;border-left:3px solid #2a78d6;padding:7pt 11pt;margin:5pt 0;font-style:italic}
.faz{font:9.5pt/1.4 Helvetica,Arial,sans-serif;color:#2c6e35;margin-top:4pt}
.faz b{color:#1a5c26}
table{border-collapse:collapse;width:100%;margin:7pt 0 11pt;font:10pt/1.4 Helvetica,Arial,sans-serif;font-variant-numeric:tabular-nums;page-break-inside:avoid}
th{border-bottom:1.5pt solid #33465a;padding:4pt 7pt;text-align:left}
td{border-bottom:.5pt solid #d3dbe4;padding:3.5pt 7pt;vertical-align:top}
.num{text-align:right;font-weight:700}
.q{font:600 10.5pt/1.4 Helvetica,Arial,sans-serif;color:#1a2733;margin:9pt 0 3pt}
.a{font:10pt/1.5 Georgia,serif;margin:0 0 8pt;padding-left:12pt;border-left:2px solid #e2e7ee}
.alerta{background:#fdf6ef;border-left:3px solid #e08a2e;padding:7pt 11pt;margin:7pt 0;font-size:10.5pt}
.check{font:10pt/1.6 Helvetica,Arial,sans-serif}
.check li{margin-bottom:3pt}
code{font:9.5pt 'DejaVu Sans Mono',Consolas,monospace;color:#324}
footer{margin-top:14pt;padding-top:7pt;border-top:.5pt solid #c3ccd5;font:9pt/1.4 Helvetica,Arial,sans-serif;color:#8593a1}
"""


def bloco(t, titulo, fala, faz):
    f = f'<div class="faz"><b>na tela:</b> {faz}</div>' if faz else ""
    return (f'<div class="passo"><div class="t">{t}</div><div class="c">'
            f'<b>{titulo}</b><div class="fala">{fala}</div>{f}</div></div>')


def html(res):
    base, carga, rec = "baseline", "stress", "recovery"
    L = cp2.L_US
    zb = int(res.loc[base, "delay_zeros"])
    logo = open(LOGO, encoding="utf-8").read().replace('width="561" height="500"', 'width="46" height="41"', 1)
    thp_c, thp_b = res.loc[carga, "thp_mediana"], res.loc[base, "thp_mediana"]
    prb_c, prb_b = res.loc[carga, "prb_media"], res.loc[base, "prb_media"]

    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Roteiro da apresentação — Grupo 6</title><style>{CSS}</style></head><body>
<div class="hd">{logo}<div>
  <h1>Roteiro da apresentação — Grupo 6</h1>
  <div class="sub">Tema 1, vazão do usuário (UE-TP) · <b>20 a 25 min + defesa individual</b> · painel ao vivo</div></div></div>

<h2>Antes de começar (10 minutos antes)</h2>
<ol class="check">
<li>Abra o painel e <b>ligue o Projeto 2</b> no botão ⏻ do topo. Leva 1 a 2 minutos.</li>
<li>Dê <b>Ctrl+Shift+R</b> para pegar a versão nova da tela.</li>
<li>Confira na régua de cima: <b>SERVIÇOS</b> com as três bolinhas verdes e o quadrante
    <b>RÁDIO·E2</b> aparecendo com números. Se o rádio não aparecer, o gNB não subiu.</li>
<li><b>Rode o T1 uma vez</b> para aquecer, leia o resultado e clique em <b>limpar</b>. Você já sabe
    o que vai aparecer e não se assusta na hora.</li>
<li>Deixe o <b>RELATORIO_CP2.pdf</b> aberto em outra aba. É o plano B se a rede cair.</li>
</ol>
<div class="alerta"><b>Se o painel falhar na hora:</b> não tente consertar na frente da turma.
Vá para a aba do PDF e apresente pelos gráficos — o roteiro abaixo funciona igual, você só troca
"clique" por "veja a figura". Diga com naturalidade: "o laboratório está fora agora, vou mostrar
pelos resultados que salvamos".</div>

<h2>Como a nota é dada (e por que o roteiro tem esta ordem)</h2>
<p>A rubrica do briefing vale 10 pontos, divididos em cinco critérios de 2,0. Cada bloco abaixo
existe para marcar um deles — se um bloco for cortado por falta de tempo, são 2 pontos em risco.</p>
<table>
<tr><th>Critério (2,0 cada)</th><th>Onde ele aparece na apresentação</th></tr>
<tr><td>Aquisição, preparação e qualidade dos dados</td><td>Bloco 2 — de onde vem e o que checamos</td></tr>
<tr><td>ETL, organização e reprodutibilidade</td><td>Bloco 3 — bronze/silver/gold e como reproduzir</td></tr>
<tr><td>Definição e interpretação de KPIs/KQIs</td><td>Bloco 4 — os indicadores, um a um</td></tr>
<tr><td>Análise, visualizações e recomendação</td><td>Bloco 5 — rodar ao vivo e a decisão</td></tr>
<tr><td>Governança, limitações, documentação e defesa</td><td>Bloco 6 — limites e o decision.json</td></tr>
</table>

<h2>O roteiro, minuto a minuto (22 min, três vozes)</h2>
<div class="alerta"><b>Dividam a fala entre os três.</b> A defesa é individual: quem apresentou um
bloco é quem vai ser perguntado sobre ele. Combinem quem fica com o quê e cada um estuda o seu
pedaço a fundo. Abaixo está uma sugestão de divisão.</div>

{bloco("0:00–2:00", "Abertura — quem somos e a pergunta &nbsp;<i>(Henrique)</i>",
 "Somos o Grupo 6: Henrique, Kelvin e Klinger. Nosso tema é a vazão do usuário. A pergunta que "
 "temos que responder é: a vazão do usuário sobe ou desce junto com o uso do rádio e com o atraso? "
 "Todos os sete grupos receberam exatamente os mesmos dados — o que muda de um grupo para o outro "
 "é a pergunta, os dois indicadores e a recomendação no fim. Vamos mostrar de onde veio o dado, o "
 "que fizemos com ele, o que encontramos e o que decidimos.",
 "nada ainda. Olhe para a turma e apresente os três nomes.")}

{bloco("2:00–5:30", "De onde vem o dado e o que checamos &nbsp;<i>(voz 2)</i>",
 "Ninguém digitou esses números. Um celular simulado se conecta à antena; a antena mede o que "
 "acontece com esse usuário e, cerca de uma vez por segundo, empacota num relatório padrão do "
 "O-RAN que sobe pela interface E2 até o RIC. Um programa assinante, o xApp, recebe e escreve uma "
 "linha num arquivo. São 100 medições em três momentos: repouso, carga e recuperação. Antes de "
 "analisar, checamos a qualidade: não há nulos nas três métricas, não há linhas duplicadas na "
 "chave, não há buracos na numeração das amostras, e o campo de horário está todo em UTC. Uma "
 "coisa que descobrimos: o carimbo de hora do arquivo é a hora em que os dados foram carregados, "
 "não a hora da medição — por isso usamos o índice da amostra como ordem no tempo.",
 "menu <b>Apresentar → Topologia · P2</b>. Percorra com o dedo: "
 "<b>celular → antena (gNB) → E2 → FlexRIC → xApp → arquivo</b>.")}

{bloco("5:30–9:00", "Como organizamos: o ETL e a reprodutibilidade &nbsp;<i>(voz 3)</i>",
 "O dado cru, do jeito que caiu, é a zona bronze — uma linha por medição, sem limpeza. A gente "
 "tipa cada campo, carimba a fase e ordena: isso vira a zona silver, um banco SQLite. E resume "
 "numa tabela de três linhas, uma por fase: é a zona gold. Isso é o padrão medallion da aula 02 e "
 "o ETL da aula 03, do começo ao fim. O ETL é um script só, com a biblioteca padrão do Python — "
 "sem dependência nenhuma; a análise usa pandas e matplotlib, declarados num requirements. "
 "Qualquer pessoa reproduz com três comandos: instala, monta o lake, roda a análise. O pacote "
 "que entregamos leva os dados brutos junto, então não depende do nosso computador.",
 "volte ao painel e clique em <b>T1 · Vazão do usuário</b>. O pré-voo já mostra bronze, silver e "
 "gold e as primeiras linhas do arquivo de verdade. Deixe essa tela aberta enquanto fala.")}

{bloco("9:00–13:30", "Os dois indicadores, definidos formalmente &nbsp;<i>(voz 2 ou 3)</i>",
 "O primeiro indicador é a vazão do usuário: a mediana e o p95 do throughput de subida, por fase, "
 "em kbps, saindo da coluna thp_ul da zona silver. Escolhemos a mediana porque há um pico isolado "
 "na recuperação que distorce a média. O segundo é a ocupação do rádio: a média do PRB por fase, "
 "em porcentagem. Além desses dois, definimos um KQI: a fração do tempo em que o atraso passa de "
 "100 microssegundos. E aqui está o que mais nos ensinou. Olhando só a mediana, o atraso parece "
 "piorar sob carga. Mas 11 das 20 amostras do repouso têm atraso ZERO — porque não havia tráfego "
 "para atrasar. E as 9 restantes chegam a 218 microssegundos, mais alto que a mediana sob carga. "
 "Ou seja: sob carga o atraso não ficou pior. Ficou contínuo. A mediana sozinha diria o contrário.",
 "mostre a ficha de cada indicador no relatório (seção 5) ou fale por cima do painel. "
 "<b>Diga a unidade em voz alta</b> — microssegundos, não milissegundos.")}

{bloco("13:30–18:00", "Rodar ao vivo, a análise e a recomendação &nbsp;<i>(Henrique)</i>",
 "Vou rodar agora, são dois segundos. [depois que aparecer] A vazão vai de 3,7 para 80 mil kbps e "
 "o rádio de 2 para 97 por cento: os dois sobem juntos. Isso já responde a pergunta do nosso tema. "
 "A regra do nosso card procura o caso ruim — vazão baixa com rádio cheio, usuário mal servido — e "
 "ela não disparou em nenhuma das 100 amostras. Por isso a nossa recomendação é NÃO aplicar "
 "política de priorização: o que vimos foi capacidade sendo usada. E a confiança que temos nisso é "
 "baixa a moderada, porque é uma execução, 100 amostras e um único usuário em simulação.",
 "clique em <b>▶ Iniciar teste</b>. Enquanto roda, aponte a faixa de percurso acendendo. Quando o "
 "<b>Painel do UE</b> aparecer, leia a frase de destaque e aponte os dois cartões e o gráfico.")}

{bloco("18:00–21:30", "Limitações, governança e o confronto com o artefato &nbsp;<i>(os três)</i>",
 "Para fechar, o que estes dados NÃO permitem dizer. Nada sobre cobertura, porque não há RSRP nem "
 "SINR no arquivo. Nada sobre experiência do usuário, porque não existe nota de vídeo nem MOS — o "
 "atraso é só um proxy. Nada sobre a célula, porque é um usuário em simulação. E nada sobre causa: "
 "vazão e PRB andarem juntos não prova que um causa o outro. Sobre governança: são dados "
 "sintéticos, sem nada pessoal, e a política que propomos seria sempre em dry-run — nada é "
 "aplicado na rede. Por último, um confronto: o decision.json que veio no pacote decide 'apply', e "
 "nós recomendamos não aplicar. Não é contradição, são perguntas diferentes: ele pergunta se isto "
 "é diferente do repouso, e é, por construção. Nós perguntamos se o usuário está mal servido, e "
 "não está. Anômalo não é ruim.",
 "role o painel até a última linha, que já lista o que os dados não permitem dizer. "
 "Se quiser, abra o relatório na seção 11 para mostrar o decision.json.")}

{bloco("21:30–22:00", "Fecho &nbsp;<i>(Henrique)</i>",
 "Em uma frase: a vazão acompanha o rádio, o que vimos foi capacidade em uso e não usuário mal "
 "servido, e por isso não recomendamos política. Obrigado — estamos à disposição para as perguntas.",
 "pare de clicar. Deixe o Painel do UE na tela durante as perguntas.")}

<h2>Defesa individual — o que cada um precisa saber sozinho</h2>
<p>O professor vai perguntar a cada um separadamente. A regra é simples: <b>quem apresentou o bloco
responde pelo bloco</b>. Abaixo, o mínimo que cada voz precisa dominar.</p>
<div class="q">Quem falou de <b>dados e qualidade</b> (bloco 2) precisa responder</div>
<div class="a">De onde vem cada uma das três métricas e o que ela significa · quantas amostras e
quantas fases · o que vocês checaram de qualidade e o que encontraram · por que o carimbo de hora
não serve como ordem temporal.</div>
<div class="q">Quem falou de <b>ETL</b> (bloco 3) precisa responder</div>
<div class="a">O que é bronze, silver e gold e o que muda entre elas · onde fica o código · como
outra pessoa reproduz · por que SQLite e não um CSV solto.</div>
<div class="q">Quem falou de <b>indicadores</b> (bloco 4) precisa responder</div>
<div class="a">A fórmula, a unidade e a granularidade dos dois indicadores · a diferença entre KPI e
KQI · por que a mediana e não a média · por que o limiar é 100 µs e até onde ele vale.</div>
<div class="q">Quem falou da <b>análise e da decisão</b> (bloco 5) precisa responder</div>
<div class="a">Por que não aplicar a política · o que a regra do card procura · por que a correlação
global de 0,48 não vale · qual seria a política A1 se a regra tivesse disparado.</div>

<h2>A colinha — os números na mão</h2>
<table>
<tr><th>O quê</th><th class="num">repouso</th><th class="num">carga</th><th>como falar</th></tr>
<tr><td>Vazão (mediana, kbps)</td><td class="num">{n(thp_b)}</td><td class="num">{n(thp_c)}</td>
    <td>"cerca de 80 megabits"</td></tr>
<tr><td>Ocupação do rádio (%)</td><td class="num">{n(prb_b)}</td><td class="num">{n(prb_c)}</td>
    <td>"o rádio praticamente cheio"</td></tr>
<tr><td>Atraso mediano (µs)</td><td class="num">{n(res.loc[base,'delay_mediana'])}</td>
    <td class="num">{n(res.loc[carga,'delay_mediana'])}</td><td>"microssegundos, não milissegundos"</td></tr>
<tr><td>Tempo acima de {L:.0f} µs</td><td class="num">{n(res.loc[base,'acima_L'],0)}%</td>
    <td class="num">{n(res.loc[carga,'acima_L'],0)}%</td><td>"passou a ser contínuo"</td></tr>
<tr><td>Amostras</td><td class="num">20</td><td class="num">60</td><td>"100 no total, com 20 de recuperação"</td></tr>
</table>
<p style="font-size:10pt;color:#5a6b7c">Se esquecer um número, não invente: diga "está no relatório"
e siga. Ninguém tira ponto por consultar; tira por afirmar errado.</p>

<h2>Perguntas prováveis — e o que responder</h2>

<div class="q">1. Por que vocês usaram a mediana e não a média?</div>
<div class="a">Porque na fase de recuperação existe um pico isolado de 172.317 kbps que puxa a média
para 8.619 enquanto a mediana é 3,7. A mediana descreve o que estava acontecendo na maior parte do
tempo; a média descreveria o pico.</div>

<div class="q">2. Por que o limiar é 100 microssegundos?</div>
<div class="a">Testamos de 20 a 280 e medimos a separação entre repouso e carga. Ela é máxima num
patamar de 95 a 133 µs — 75 pontos, 25% contra 100% —, então 100 está no meio da faixa, não na beirada.
E declaramos o limite: acima de 186 µs o indicador deixa de separar, e 186 é justamente o p95 do próprio
repouso — passado o quase-pior caso da rede parada, as duas fases medem quase o mesmo (5% contra 7%);
de 198 em diante chega a inverter. Está no relatório, com o gráfico.</div>

<div class="q">3. Vocês acharam correlação de 0,48 entre vazão e atraso. Isso não é relevante?</div>
<div class="a">Esse 0,48 é global, misturando as três fases. Dentro de cada fase a correlação cai
para perto de zero. O número global está comparando rede parada com rede sob carga — não é uma
relação entre as duas medidas, é a diferença entre dois mundos.</div>

<div class="q">4. Por que não aplicar a política? O rádio está a 97%.</div>
<div class="a">Porque rádio cheio com vazão alta é capacidade em uso, não usuário mal servido. A
regra procura vazão baixa COM rádio cheio, e isso não aconteceu em nenhuma amostra. Aplicar
priorização aqui seria resolver um problema que os dados não mostram.</div>

<div class="q">5. Mas o decision.json do laboratório decide "apply". Vocês contrariaram o artefato?</div>
<div class="a">São perguntas diferentes. O decision.json usa o robust-baseline-mad, que pergunta "isto
é diferente do repouso?" — e é, por construção. A nossa pergunta é "o usuário está mal servido?". E
tem um detalhe: no model.json o MAD é zero nas três métricas e o piso é 1,0, então qualquer variação
acima de 3,5 dispara. Ele acusa mudança de regime, não qualidade. Anômalo não é ruim.</div>

<div class="q">6. Isso vale para uma rede real?</div>
<div class="a">Não. É RFSIM, canal ideal, um único usuário e uma execução. Numa rede real teríamos
desvanecimento, interferência e vários usuários disputando o mesmo rádio. O que vale aqui é o
método, não o número.</div>

<div class="q">7. Qual a diferença entre KPI e KQI, no trabalho de vocês?</div>
<div class="a">O KPI olha a rede: quanto de rádio está ocupado, quantos bits passaram. O KQI olha o
serviço: a fração do tempo em que o atraso ficou acima do limiar. O KPI pode estar ótimo e o KQI
ruim — foi por isso que a aula 04 separou os dois.</div>

<div class="q">8. O que é PRB?</div>
<div class="a">É o pedacinho de rádio que a antena entrega a um usuário de cada vez. 97% significa
rádio praticamente cheio; 2%, rádio vazio.</div>

<div class="q">9. Vocês corrigiram alguma coisa do Checkpoint 1?</div>
<div class="a">Sim, e está registrado no relatório: as unidades. Tínhamos escrito o atraso em
milissegundos e o PRB em contagem de blocos. O correto é microssegundos e porcentagem. Os números
não mudaram, o rótulo estava errado — e um atraso de 159 microssegundos conta uma história bem
diferente de 159 milissegundos.</div>

<h2>Três regras para não escorregar</h2>
<ol class="check">
<li><b>Nunca diga "a QoE caiu".</b> Não temos MOS. Diga "é risco para a experiência".</li>
<li><b>Nunca diga que uma coisa causou a outra.</b> Diga "andam juntas" ou "acompanha".</li>
<li><b>Se não souber, diga que não sabe</b> e ofereça olhar o dado. É o que o professor cobra o
tempo todo: dizer menos do que os dados sustentam também é resultado.</li>
</ol>

<footer>Grupo 6 — Henrique Carmine, Kelvin de Lima Gabriel, Klinger Carneiro Júnior ·
Análise de Dados em Redes de Telecom · Prof. Dr. Jonas Augusto Kunzler · CESAR School</footer>
</body></html>"""


if __name__ == "__main__":
    res = cp2.por_fase(cp2.carregar())
    hp = os.path.join(OUT, "ROTEIRO_APRESENTACAO.html")
    open(hp, "w", encoding="utf-8").write(html(res))
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    pdf = os.path.join(OUT, "ROTEIRO_APRESENTACAO.pdf")
    if chrome:
        subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox",
                        "--no-pdf-header-footer", "--print-to-pdf=" + pdf,
                        "file://" + hp], check=True, capture_output=True, timeout=180)
    desk = os.path.join(os.path.expanduser("~"), "Área de trabalho")
    if os.path.isdir(desk) and os.path.exists(pdf):
        shutil.copy(pdf, desk)
        print("PDF na Área de trabalho:", os.path.join(desk, "ROTEIRO_APRESENTACAO.pdf"))
    print("html:", hp)
