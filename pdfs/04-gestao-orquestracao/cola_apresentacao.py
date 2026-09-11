#!/usr/bin/env python3
"""Gera a COLA da apresentação de SMO (12/09): o que cada um lê e o que aperta
no painel, bloco a bloco. Sai em PDF para abrir no celular ou imprimir.

Os NOMES dos integrantes não ficam neste arquivo nem no repositório (é
público): entram só na hora de gerar, pela linha de comando. A saída vai para
entrega/ (fora do git) e para a Área de trabalho.

Uso:
  python3 cola_apresentacao.py --integrantes "Nome 1,Nome 2,Nome 3"
A ordem dos nomes é a das vozes: 1 abre e fecha; 2 fica com a O1 e o ciclo de
vida; 3 fica com falhas, telemetria e O-Cloud.
"""
import argparse
import html
import os
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
LOGO = os.path.join(REPO, "server/panel/static/ops/cesar-marca.svg")
OUT = os.path.join(HERE, "entrega")
PAINEL = "https://core5g-arm64.duckdns.org"
RAIL = "rail da esquerda → <b>5 · Gestão, Orquestração e Automação (SMO)</b>"

CSS = """
@page { size: A4; margin: 14mm 13mm; }
* { box-sizing: border-box; }
body { font-family: -apple-system, "Segoe UI", Roboto, sans-serif; color: #1d2230; font-size: 12.5px; line-height: 1.5; margin: 0; }
.hd { display: flex; gap: 14px; align-items: center; border-bottom: 3px solid #6965c9; padding-bottom: 10px; margin-bottom: 12px; }
h1 { font-size: 20px; margin: 0; }
.sub { color: #555b6b; font-size: 12px; }
h2 { font-size: 15px; margin: 18px 0 8px; color: #494597; border-bottom: 1px solid #d9dce5; padding-bottom: 3px; break-after: avoid; page-break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 6px 0 10px; font-size: 12px; }
th, td { border: 1px solid #d9dce5; padding: 5px 7px; text-align: left; vertical-align: top; }
th { background: #f1f2f7; }
ol.check li { margin: 4px 0; }
.bloco { border: 1px solid #d9dce5; border-left: 6px solid #6965c9; border-radius: 8px; padding: 9px 12px; margin: 12px 0; page-break-inside: avoid; }
.bloco .top { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; }
.bloco .t { font-weight: 700; font-size: 14px; }
.bloco .quem { background: #6965c9; color: #fff; border-radius: 999px; padding: 1px 11px; font-weight: 700; font-size: 12px; white-space: nowrap; }
.bloco .tempo { color: #555b6b; font-weight: 600; white-space: nowrap; }
.item { color: #555b6b; font-size: 11.5px; margin: 1px 0 6px; }
.box { border-radius: 6px; padding: 6px 10px; margin: 6px 0; }
.box .lb { font-size: 10px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; margin-bottom: 2px; }
.aperta { background: #e8f4ea; border: 1px solid #b7dcbf; }
.aperta .lb { color: #026421; }
.aperta ol { margin: 2px 0 0 18px; padding: 0; }
.le { background: #f6f6fb; border: 1px solid #dcdcef; font-size: 13px; }
.le .lb { color: #494597; }
.le p { margin: 3px 0; }
.aponta { background: #fff5e0; border: 1px solid #f0d9a8; }
.aponta .lb { color: #7d4001; }
.falha { background: #fdeeee; border: 1px solid #efc4c4; font-size: 11.5px; }
.falha .lb { color: #8b2b3f; }
.alerta { background: #fdeeee; border: 1px solid #efc4c4; border-radius: 6px; padding: 8px 11px; margin: 8px 0; }
.qa { margin: 7px 0; page-break-inside: avoid; }
.qa b { color: #494597; }
footer { margin-top: 18px; color: #6b7080; font-size: 10.5px; border-top: 1px solid #d9dce5; padding-top: 6px; }
code { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 11px; background: #f1f2f7; padding: 0 3px; border-radius: 3px; }
"""


def lista(itens):
    return "<ol>" + "".join(f"<li>{i}</li>" for i in itens) + "</ol>"


def bloco(tempo, quem, titulo, item, aperta, le, aponta, falha=""):
    return f"""
<div class="bloco">
  <div class="top"><span class="t">{titulo}</span><span><span class="tempo">{tempo}</span> &nbsp;<span class="quem">{html.escape(quem)}</span></span></div>
  <div class="item">{item}</div>
  <div class="box aperta"><div class="lb">aperta no painel</div>{lista(aperta) if aperta else '<div>nada — olhe para a turma.</div>'}</div>
  <div class="box le"><div class="lb">lê</div>{''.join(f'<p>{p}</p>' for p in le)}</div>
  <div class="box aponta"><div class="lb">aponta na tela</div>{aponta}</div>
  {f'<div class="box falha"><div class="lb">se falhar</div>{falha}</div>' if falha else ''}
</div>"""


def teste(nome):
    return [f"{RAIL} → botão <b>{nome}</b>",
            "na janela que abre (pré-voo), aperte o verde <b>▶ Iniciar teste</b>",
            "enquanto roda: a <b>faixa</b> acima do console acende etapa por etapa — clique numa etapa para abrir o cartão dela, se quiser mostrar"]


def pagina(v1, v2, v3):
    logo = ""
    if os.path.exists(LOGO):
        logo = open(LOGO, encoding="utf-8").read().replace('width="561" height="500"', 'width="46" height="41"', 1)
    limpar = "no fim, aperte <b>limpar</b> (barra do console) antes do próximo bloco"
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Cola da apresentação — SMO do O-RAN SC</title><style>{CSS}</style></head><body>
<div class="hd">{logo}<div>
  <h1>Cola da apresentação — SMO do O-RAN SC</h1>
  <div class="sub">Gestão, Orquestração e Automação em Redes OpenRAN · Prof. Lucas Borges de Oliveira ·
  <b>12/09 · 20 minutos · 3 vozes</b> · painel ao vivo: {PAINEL}</div></div></div>

<table>
<tr><th>Tempo</th><th>Quem</th><th>Blocos</th><th>Itens da avaliação</th></tr>
<tr><td>0:00–5:00</td><td><b>{html.escape(v1)}</b></td><td>Abertura (Tour) · Arquitetura</td><td>1 arquitetura · 2 serviços · 3 componentes</td></tr>
<tr><td>5:00–12:00</td><td><b>{html.escape(v2)}</b></td><td>O1: leitura · Provisionamento · Ciclo de vida</td><td>4 O1 · 5 gerenciamento e provisionamento · 7 ciclo de vida</td></tr>
<tr><td>12:00–18:30</td><td><b>{html.escape(v3)}</b></td><td>Falhas · Telemetria · O-Cloud e O2</td><td>8 falhas e telemetria · 4 O2 · 6 O-Cloud</td></tr>
<tr><td>18:30–20:00</td><td><b>{html.escape(v1)}</b></td><td>Conclusão</td><td>—</td></tr>
</table>

<h2>Antes de começar (15 minutos antes) — {html.escape(v1)}</h2>
<ol class="check">
<li>Abra <b>{PAINEL}</b> e entre como <b>Professor</b>.</li>
<li>No topo, quadrante <b>serviços</b>, com o <b>Projeto 2</b> selecionado: se o botão <b>E2 lab</b> estiver verde,
    aperte e confirme <b>OK</b> para desligar. O gNB e o UE simulados comem 3 dos 4 núcleos e deixam o SMO lento.</li>
<li>O botão <b>SMO</b> tem de estar <b>verde</b>. Se estiver apagado: aperte, confirme <b>OK</b> e espere ~5 minutos até ficar verde.</li>
<li>Aperte <b>Ctrl+Shift+R</b> (a tela mudou de versão).</li>
<li>Ensaio: {RAIL} → <b>Arquitetura do SMO</b> → <b>▶ Iniciar teste</b>. No fim tem de aparecer
    <i>"Resultado: arquitetura completa no ar"</i>. Aperte <b>limpar</b>.</li>
<li>Ensaio: <b>Telemetria: medidas 3GPP da O-DU</b> → <b>▶ Iniciar teste</b>. Se aparecer
    <i>"a geração de medidas da O-DU parece parada"</i>: reiniciar a O-DU no terminal
    (<code>./deploy.sh ssh 'docker restart pynts-o-du-o1'</code>) e esperar 1 minuto. Aperte <b>limpar</b>.</li>
<li>Abra uma <b>segunda aba</b> na topologia: rail → <b>Topologia</b> (ou {PAINEL}/topology?proj=p2).
    No canto de baixo, à direita, o <b>primeiro botão da fileira de zoom</b> (antes do + e do −) tem de estar
    aceso, com borda colorida: é o zoom automático.</li>
</ol>
<div class="alerta"><b>Como todo teste funciona:</b> botão no rail → <b>▶ Iniciar teste</b> → a faixa acende →
no fim leia o <b>Resumo</b> e a caixa <b>"O que acabou de acontecer"</b> → <b>limpar</b>.
O botão <b>mapa</b> (barra do console) abre o mapa da rede com zoom no SMO, para mostrar onde aquilo acontece.
<b>Se um teste falhar na hora:</b> não conserte na frente da turma — leia o Resumo (ele diz o motivo) e siga para o próximo bloco.</div>

<h2>Os blocos</h2>
{bloco("0:00–1:30", v1, "Abertura — o que é um SMO e o que vamos mostrar", "abre a apresentação",
  ["vá para a aba da <b>Topologia</b>",
   "aperte <b>Tour</b> e depois <b>Próximo →</b> até o chip <b>Camada 8</b> (SMO) — o mapa aproxima sozinho",
   "aperte <b>Próximo →</b> uma vez (Camada 9, a rede gerenciada) e depois <b>Sair</b>"],
  ["SMO quer dizer <i>Service Management and Orchestration</i>: é a camada que opera a rede O-RAN inteira. Ela configura os equipamentos, recebe as falhas, coleta as medidas e cuida do ciclo de vida das funções de rede.",
   "A ferramenta que estudamos é o <b>SMO do O-RAN SC</b>, a implementação de referência da O-RAN Alliance. E não vamos mostrar slide: ele está rodando agora no nosso servidor, e cada item da avaliação vai ser respondido com um teste ao vivo.",
   "Um detalhe de engenharia: o servidor é ARM64. Sete imagens do SMO só existiam para x86, e nós construímos essas sete em ARM64."],
  "a banda violeta <b>SMO</b> e a banda verde <b>Rede gerenciada por O1</b> na topologia.")}

{bloco("1:30–5:00", v1, "Arquitetura, serviços e componentes", "itens 1, 2 e 3 da avaliação",
  ["volte para a aba do <b>painel</b>"] + teste("Arquitetura do SMO") + [limpar],
  ["A arquitetura tem três camadas. A <b>common</b> é a plataforma: o Traefik, que é a porta de entrada; o Keycloak, que cuida de usuários e papéis; o banco MariaDB; o Kafka, que é o barramento de eventos; e o servidor de topologia.",
   "A camada <b>oam</b> é a gerência: o controlador SDN-R, baseado no OpenDaylight, que é quem fala O1; o console ODLUX; e o coletor de eventos VES. A camada <b>network</b> são os elementos gerenciados: uma O-DU e dois O-RU simulados.",
   "Os serviços saem direto das rotas do gateway. E os componentes O-RAN suportados são a O-DU pela <b>O1</b> e o O-RU pelo <b>M-plane</b> do Open Fronthaul. O teste também diz o que <b>não</b> está aqui: a A1, que é do Non-RT RIC, e a O2, que o OAM não implementa."],
  "<b>15 contêineres</b> em arm64 · <b>8 serviços</b> no gateway · O-DU com <b>154</b> e O-RU com <b>114</b> modelos YANG · os avisos amarelos de A1 e O2.",
  "leia do jeito que está — o Resumo mostra o que falta em vermelho.")}

{bloco("5:00–8:00", v2, "O1 — o SMO lendo um equipamento", "itens 4 e 5 da avaliação",
  teste("O1: ler a configuração da O-DU") + [limpar],
  ["A interface <b>O1</b> é a gerência dos elementos O-RAN, e ela é NETCONF com modelos YANG. O que vamos ver é o SMO perguntando a configuração da O-DU.",
   "O caminho é: o painel chama o controlador por <b>RESTCONF</b>, que é HTTP com JSON; o controlador traduz para <b>NETCONF</b> e busca no equipamento.",
   "A O-DU anunciou <b>154 modelos YANG</b> — 49 da O-RAN e 30 do 3GPP. É por esses modelos que o SMO sabe o que pode ler e configurar. E o que lemos é a árvore de rede do 3GPP: o ManagedElement, a função gNB-DU e a célula NR, com PCI, frequência, SSB e as fatias por PLMN."],
  "<b>connected</b> (NETCONF em :6513) · <b>154 modelos</b> · os blocos <b>gNB-DU</b> e <b>célula NR</b> · o tempo da leitura (~0,5 s).")}

{bloco("8:00–10:00", v2, "Provisionamento — mudar, conferir no equipamento e desfazer", "item 5 da avaliação",
  teste("O1: provisionar e desfazer") + [limpar],
  ["Agora o SMO vai <b>escrever</b>. Vamos mudar o nome da gNB-DU — é um parâmetro visível e que não derruba nada.",
   "A escrita é um <b>PATCH</b> por RESTCONF, que o controlador transforma em <b>edit-config</b> do NETCONF.",
   "E a prova não é a tela do SMO: o teste confere o valor <b>dentro do datastore da O-DU</b>. Depois desfaz, e confere de novo. Aplicar, verificar e poder voltar: é isso que um provisionamento seguro precisa."],
  "<b>HTTP 200</b> na escrita · o nome novo em <b>\"no datastore da O-DU\"</b> · a volta ao nome original.",
  "se aparecer \"escrita recusada\", diga que o controlador recusou e mostre o código HTTP no Resumo.")}

{bloco("10:00–12:00", v2, "Ciclo de vida de uma função de rede", "item 7 da avaliação",
  teste("Ciclo de vida de uma função de rede") + ["(leva ~20 s: deixe a faixa andar enquanto fala)", limpar],
  ["Ciclo de vida é instanciar, operar e encerrar uma função de rede. O teste vai <b>encerrar</b> o O-RU e medir como o SMO percebe.",
   "O controlador registra a perda em cerca de <b>um segundo</b>. Quando o O-RU volta, ele mesmo liga para o SMO — é o <b>call home</b> — e é montado de novo em uns dez segundos, sem ninguém configurar nada.",
   "Tudo fica registrado no banco do controlador: Unmounted, Mounted, Connected. Um detalhe honesto: quem encerra e instancia aqui é o Docker. Num O-RAN completo, quem faz isso é o O-Cloud, a pedido do SMO, pela interface O2."],
  "<b>\"o SMO percebeu\"</b> (~1 s) · <b>\"call home → montado\"</b> (~10 s) · as linhas do <b>connectionlog</b>.")}

{bloco("12:00–14:30", v3, "Falhas — um alarme até o barramento do SMO", "item 8 da avaliação",
  teste("Falhas: alarme VES até o Kafka") + [limpar],
  ["Gerenciamento de falhas: o equipamento avisa que algo quebrou. Vamos levantar um alarme <b>linkDown</b> — o enlace do fronthaul caiu — com severidade crítica.",
   "O caminho é o padrão da O-RAN: o evento vai no formato <b>VES</b> até o coletor, que publica no tópico de falhas do <b>Kafka</b>. Dali qualquer sistema assina: análise, rApps, o console.",
   "Depois limpamos o alarme pelo mesmo caminho. E vale dizer: a O-DU simulada não gera alarmes sozinha, então o teste faz o papel dela, com o mesmo formato VES."],
  "<b>HTTP 202</b> no coletor · <b>\"no tópico de falhas … ms depois do envio\"</b> (~1 s) · severidade <b>CRITICAL</b> e depois <b>NORMAL</b>.")}

{bloco("14:30–16:30", v3, "Telemetria — as medidas da O-DU chegando ao SMO", "item 8 da avaliação",
  teste("Telemetria: medidas 3GPP da O-DU") + [limpar],
  ["Monitoramento e telemetria. A O-DU mede sozinha: a cada <b>60 segundos</b> ela grava um arquivo de medidas no padrão <b>3GPP TS 28.532</b>, com contadores de usuários ativos por DRB.",
   "E ela não espera o SMO perguntar: manda um aviso <b>VES FileReady</b> dizendo onde está o arquivo, e esse aviso cai no Kafka.",
   "No fim aparecem os contadores de tudo o que o SMO já recebeu: avisos de medida, heartbeats — o \"estou vivo\" — e registros de PNF, o \"cheguei\" quando o equipamento liga."],
  "<b>\"Gravado há … s\"</b> (menos de 2 minutos) · os valores dos contadores <b>DRB</b> · o <b>FileReady</b> com o arquivo anunciado.",
  "se aparecer \"a geração de medidas parece parada\": diga que o simulador parou de gerar e mostre o último arquivo mesmo assim.")}

{bloco("16:30–18:30", v3, "O-Cloud e O2 — o que existe e o que falta", "itens 4 e 6 da avaliação",
  teste("O-Cloud e O2 (o que existe e o que falta)") + [limpar],
  ["Aqui a resposta é honesta: o SMO do O-RAN SC <b>não implementa a O2</b>. No O-RAN SC, a O2 — o IMS, que inventaria a nuvem, e o DMS, que implanta as funções — fica no projeto <b>INF</b>, sobre StarlingX, que pede máquina dedicada.",
   "Mesmo assim, o teste mostra o que um IMS exporia do nosso O-Cloud: a máquina ARM64 com 4 vCPU e 15 GB, o Docker fazendo o papel do DMS e quanto cada função consome.",
   "O SMO inteiro com os simuladores usa perto de <b>5 GB</b> de memória."],
  "o aviso amarelo <b>\"não traz O2\"</b> · <b>aarch64 (Neoverse-N1)</b> · o total de memória no fim.")}

{bloco("18:30–20:00", v1, "Conclusão", "fecha a apresentação",
  [],
  ["Resumindo: o SMO do O-RAN SC entrega bem a <b>O1</b> — leitura e provisionamento —, o <b>M-plane</b>, as <b>falhas</b> e a <b>telemetria</b> por VES e Kafka, e a identidade com o Keycloak.",
   "O que ele não entrega é a <b>O2</b> e o <b>O-Cloud</b>, e ele não conversa sozinho com o Non-RT RIC pela A1.",
   "E montamos tudo em ARM64: os problemas que encontramos no caminho — JDK novo, Traefik antigo com Docker novo — estão documentados, e nenhum era de ARM. Obrigado."],
  "nada — volte para a topologia se quiserem perguntar sobre um componente.")}

<h2>Perguntas prováveis — quem responde</h2>
<div class="qa"><b>Por que simuladores e não o gNB do laboratório?</b> ({html.escape(v2)}) O gNB do OAI não tem agente O1. Por isso usamos a O-DU e os O-RU do próprio O-RAN SC, que falam O1 e M-plane de verdade.</div>
<div class="qa"><b>Onde está a O2?</b> ({html.escape(v3)}) No projeto INF do O-RAN SC (IMS e DMS sobre StarlingX). O OAM não traz O2.</div>
<div class="qa"><b>Modelo híbrido e hierárquico?</b> ({html.escape(v2)}) No híbrido o SMO gerencia o O-RU direto pelo M-plane; no hierárquico só a O-DU fala com o O-RU — por isso um dos O-RU não aparece no controlador.</div>
<div class="qa"><b>NETCONF × RESTCONF?</b> ({html.escape(v2)}) O mesmo modelo YANG: NETCONF é SSH ou TLS com XML; RESTCONF é HTTP com JSON.</div>
<div class="qa"><b>Por que o alarme é enviado pelo teste?</b> ({html.escape(v3)}) A O-DU simulada não traz receita de alarmes; o teste usa o formato VES que ela usaria, e o caminho do coletor ao Kafka é o real.</div>
<div class="qa"><b>E o Non-RT RIC?</b> ({html.escape(v1)}) Pela O-RAN ele mora dentro do SMO. No laboratório ele existe (banda âmbar da topologia), mas as duas pilhas ainda não conversam.</div>
<div class="qa"><b>Quanto custa rodar?</b> ({html.escape(v3)}) Perto de 5 GB de memória para o SMO e os simuladores, e pouca CPU.</div>

<footer>Gerado para uso do grupo — não versionar. {html.escape(v1)} · {html.escape(v2)} · {html.escape(v3)} ·
Gestão, Orquestração e Automação em Redes OpenRAN · CESAR School</footer>
</body></html>"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--integrantes", required=True, help='três nomes separados por vírgula, na ordem das vozes')
    nomes = [n.strip() for n in ap.parse_args().integrantes.split(",") if n.strip()]
    if len(nomes) != 3:
        ap.error("a cola é para 3 vozes: passe exatamente três nomes")
    os.makedirs(OUT, exist_ok=True)
    hp = os.path.join(OUT, "COLA_APRESENTACAO_SMO.html")
    with open(hp, "w", encoding="utf-8") as f:
        f.write(pagina(*nomes))
    pdf = os.path.join(OUT, "COLA_APRESENTACAO_SMO.pdf")
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    if chrome:
        subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        "--print-to-pdf=" + pdf, "file://" + hp], check=True, capture_output=True, timeout=180)
    desk = next((d for d in (os.path.join(os.path.expanduser("~"), n) for n in ("Área de trabalho", "Desktop"))
                 if os.path.isdir(d)), None)
    if desk and os.path.exists(pdf):
        shutil.copy(pdf, desk)
        print("PDF na Área de trabalho:", os.path.join(desk, "COLA_APRESENTACAO_SMO.pdf"))
    print("pdf:", pdf)
