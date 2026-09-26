#!/usr/bin/env python3
"""COLA da apresentação da 2ª PARTE (26/09): provisionar, gerenciar e acompanhar
uma pilha Open RAN com o SMO — 30 a 40 minutos, 3 vozes.

Feita para ser LIDA em voz alta por quem não domina o assunto: cada bloco traz
o que apertar, o que falar (texto pronto) e o que apontar na tela. No fim há
glossário com pronúncia, respostas prontas e uma colinha com os números.

Os NOMES não ficam no repositório: entram pela linha de comando.
Uso: python3 cola_apresentacao_p2.py --integrantes "Nome 1,Nome 2,Nome 3"
"""
import argparse
import html
import os
import shutil
import subprocess

import cola_apresentacao as c1

CSS, bloco, teste, lista = c1.CSS, c1.bloco, c1.teste, c1.lista
LOGO, OUT, PAINEL, RAIL = c1.LOGO, c1.OUT, c1.PAINEL, c1.RAIL
NOME = "COLA_APRESENTACAO_SMO_P2"
limpar = "no fim, aperte <b>limpar</b> (barra do console) antes do próximo bloco"


def tabela(cab, linhas):
    h = ["<table><tr>"] + [f"<th>{c}</th>" for c in cab] + ["</tr>"]
    for ln in linhas:
        h.append("<tr>" + "".join(f"<td>{c}</td>" for c in ln) + "</tr>")
    return "".join(h) + "</table>"


def pagina(v1, v2, v3):
    logo = ""
    if os.path.exists(LOGO):
        logo = open(LOGO, encoding="utf-8").read().replace('width="561" height="500"', 'width="46" height="41"', 1)
    e = html.escape
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Cola — 2ª parte: pilha Open RAN com o SMO</title><style>{CSS}</style></head><body>
<div class="hd">{logo}<div>
  <h1>Cola da apresentação — 2ª parte: provisionar, gerenciar e acompanhar uma pilha Open RAN</h1>
  <div class="sub">Gestão, Orquestração e Automação em Redes OpenRAN · Prof. Lucas Borges de Oliveira ·
  <b>26/09 · 30 a 40 minutos · 3 vozes</b> · painel ao vivo: {PAINEL}</div></div></div>

<div class="alerta"><b>Como usar esta cola:</b> o que está na caixa <b>lê</b> pode ser dito exatamente como está escrito —
foi feito para isso. A caixa <b>aperta</b> diz o que fazer no painel. A <b>aponta</b> diz para onde olhar na tela.
Ninguém precisa decorar nada: <b>os testes mostram os números sozinhos</b>, e vocês só explicam o que apareceu.</div>

{tabela(["Tempo (40 min)", "Se sobrar só 30 min", "Quem", "Bloco", "Teste no painel"], [
    ["0:00–3:00", "0:00–2:30", f"<b>{e(v1)}</b>", "Abertura", "—"],
    ["3:00–10:00", "2:30–9:00", f"<b>{e(v1)}</b>", "Caso 1 · A pilha entra sob gerência", "Pilha: instanciar e pôr sob gerência"],
    ["10:00–19:00", "9:00–17:00", f"<b>{e(v2)}</b>", "Caso 2 · Provisionar a pilha", "Provisionar a pilha (plano de rede)"],
    ["19:00–27:00", "17:00–24:00", f"<b>{e(v3)}</b>", "Caso 3 · Operar: do alarme à correção", "Operar: do alarme à correção"],
    ["27:00–33:00", "24:00–28:00", f"<b>{e(v2)}</b>", "Caso 4 · Criar uma célula nova", "Escalar: uma célula nova pela O1"],
    ["33:00–36:00", "<i>cortar</i>", f"<b>{e(v3)}</b>", "Os seis serviços da O1 (bloco extra)", "—"],
    ["36:00–40:00", "28:00–30:00", f"<b>{e(v1)}</b>", "Conclusão e perguntas", "—"],
])}

<h2>Antes de começar (15 minutos antes) — {e(v1)}</h2>
<ol class="check">
<li>Abra <b>{PAINEL}</b>, entre como <b>Professor</b> e aperte <b>Ctrl+Shift+R</b>.</li>
<li>No cabeçalho, o botão <b>SMO</b> tem de estar com o <b>ponto verde</b>. Se estiver apagado: quadrante
    <b>serviços</b> → botão <b>SMO</b> → OK. <b>Conte uns 6 minutos:</b> o ponto fica verde em uns 2 minutos e meio,
    mas os equipamentos só entram sob gerência depois disso. O painel recria sozinho o simulador que não se apresentar.</li>
<li><b>O passo que confirma que está tudo pronto:</b> aperte o botão <b>SMO</b> do cabeçalho, veja no
    <b>SMO ao vivo</b> os <b>2 elementos conectados</b> e feche. Só o ponto verde não basta — sem os dois elementos,
    os testes de provisionamento falham.</li>
<li>Quadrante <b>serviços</b>: se o botão <b>E2 lab</b> estiver verde, desligue (ele deixa o SMO lento).</li>
<li>Ensaio: {RAIL} → <b>Pilha: instanciar e pôr sob gerência</b> → <b>▶ Iniciar teste</b>. Tem de terminar em verde.
    Depois aperte <b>limpar</b>. (É o único teste demorado: cerca de 1 minuto.)</li>
<li>Deixe uma <b>segunda aba</b> aberta na <b>Topologia</b>.</li>
<li>Se algum teste falhar na hora: <b>Histórico → Resultados salvos</b> tem as execuções já feitas. Mostre de lá e siga.</li>
</ol>

<h2>Os blocos</h2>

{bloco("0:00–3:00", v1, "Abertura — o que é isso que vamos mostrar", "ninguém aperta nada ainda",
  ["deixe o painel aberto na tela, sem rodar nada"],
  ["Bom dia. Na primeira parte nós analisamos uma ferramenta de SMO: a do O-RAN Software Community. Hoje é a segunda parte, e a pergunta mudou.",
   "Antes a pergunta era “como essa ferramenta é por dentro”. Agora é: <b>dá para provisionar, gerenciar e acompanhar uma pilha Open RAN com ela?</b>",
   "Para responder, nós não vamos falar sobre a ferramenta: vamos <b>operar a rede na frente de vocês</b>, em quatro demonstrações, no nosso servidor. Todo número que aparecer na tela está sendo medido na hora.",
   "Só para situar: um <b>SMO</b> é o sistema que opera a rede inteira de um lugar só — ele configura os equipamentos, recebe os alarmes e coleta as medições. E a nossa <b>pilha</b> tem três funções de rede: uma <b>O-DU</b>, que é a unidade que processa o sinal, e dois <b>O-RU</b>, que são os rádios."],
  "nada ainda — olhe para a turma.")}

{bloco("3:00–10:00", v1, "Caso 1 — a pilha entra sob gerência sozinha", "como a rede aparece para o SMO",
  teste("Pilha: instanciar e pôr sob gerência") + ["(leva cerca de 1 minuto — fale enquanto ele roda)", limpar],
  ["Este teste desliga as três funções de rede e liga de novo. Enquanto ele roda, olhem o <b>inventário</b>: a lista de equipamentos do SMO esvazia e depois enche de novo, sozinha.",
   "O ponto mais importante é este: <b>ninguém cadastra equipamento no SMO</b>. Quando a função de rede liga, é <b>ela</b> que telefona para o SMO. Isso tem nome: chama-se <b>call home</b>. O SMO atende, registra o equipamento e pergunta o que ele sabe fazer.",
   "E o equipamento responde com uma lista: são os <b>modelos YANG</b>. Pensem nisso como o manual que o próprio equipamento entrega, dizendo tudo o que pode ser lido e configurado nele. A nossa O-DU entregou <b>154</b> modelos; o rádio, <b>114</b>.",
   "Olhem o tempo no resumo: a pilha inteira ficou sob gerência em <b>18 segundos</b>, sem ninguém configurar nada no SMO.",
   "Um detalhe que vale explicar: um dos três rádios <b>não aparece</b> na lista, e isso está certo. Ele está no modo hierárquico, em que quem cuida dele é a O-DU, e não o SMO. São três equipamentos, mas só dois falam direto com a gerência."],
  "o <b>inventário esvaziando e enchendo</b>, o tempo de cada equipamento e, no fim, os <b>2 elementos conectados</b>.",
  "se um equipamento demorar, espere: o teste tenta por até 3 minutos e nunca deixa a rede parada.")}

{bloco("10:00–19:00", v2, "Caso 2 — provisionar: configurar a rede pela O1", "o coração do trabalho",
  teste("Provisionar a pilha (plano de rede)") + [limpar],
  ["Provisionar é configurar a rede. É o que um operador faz quando liga uma célula nova ou muda um parâmetro.",
   "Este teste aplica três parâmetros de uma vez: o <b>nome</b> da unidade, o <b>PCI</b> da célula — que é o número de identificação dela no ar — e o <b>ARFCN</b>, que é o canal de frequência em que ela transmite.",
   "O caminho é sempre o mesmo: o painel pede ao SMO, o SMO traduz para a linguagem do equipamento e escreve lá dentro. Essa conversa entre o SMO e o equipamento é a interface <b>O1</b>.",
   "Agora reparem na parte que é a prova do trabalho: o teste <b>não acredita na tela do SMO</b>. Ele vai dentro do equipamento conferir se o valor chegou. É a coluna que diz “no datastore da O-DU”.",
   "Os três parâmetros entraram e foram conferidos em <b>903 milissegundos</b> — menos de um segundo.",
   "E aqui vem a análise que a avaliação pede. O SMO escreve <b>um parâmetro de cada vez</b>. Não existe uma operação que garanta tudo ou nada. Se falhasse no meio, a rede ficaria pela metade e quem teria que desfazer seria o operador. Neste teste, quem desfaz é o próprio script: no fim, tudo volta como estava."],
  "a coluna <b>no datastore da O-DU</b> com os vistos verdes, o tempo total e o <b>desfazer</b> no fim.",
  "se aparecer alguma escrita recusada, diga que aquele parâmetro é somente leitura naquele modelo e siga.")}

{bloco("19:00–27:00", v3, "Caso 3 — operar: um alarme chega e alguém resolve", "o dia a dia da rede",
  teste("Operar: do alarme à correção") + [limpar],
  ["Os dois casos anteriores foram a rede sendo montada e configurada. Agora é o dia a dia: alguma coisa dá errado e alguém precisa resolver.",
   "O problema aqui é um <b>conflito de PCI</b>: duas células vizinhas com o mesmo número de identificação. Na prática, o celular se confunde entre as duas.",
   "Primeiro o alarme sai do equipamento e chega ao SMO. Ele vai num formato padrão chamado <b>VES</b> e cai numa fila de mensagens, o <b>Kafka</b>, onde qualquer sistema pode ler. Isso levou <b>384 milissegundos</b>.",
   "Depois vem a correção: escolhemos um número de PCI livre e mandamos configurar pela O1. O SMO aceitou em <b>188 milissegundos</b>, e o valor foi conferido <b>dentro do equipamento</b>, como no caso anterior.",
   "Por último, o alarme é limpo pelo mesmo caminho — porque um alarme que ninguém encerra vira ruído permanente na operação.",
   "E agora a parte honesta, que também é análise: <b>quem decidiu o PCI novo fomos nós</b>, dentro do teste. O SMO entrega os dados e entrega o meio de configurar, mas não decide sozinho. Quem decidiria seria uma aplicação de análise ou uma política automática — e isso não faz parte desta solução."],
  "o tempo do alarme até a fila, o <b>HTTP 200</b> da correção e o valor novo dentro do equipamento.",
  "se a correção for recusada, mostre que o alarme chegou à fila — essa é a parte essencial do bloco.")}

{bloco("27:00–33:00", v2, "Caso 4 — criar uma célula que não existia", "capacidade nova na rede",
  teste("Escalar: uma célula nova pela O1") + [limpar],
  ["Até agora nós mudamos coisas que já existiam. Neste último caso, nós <b>criamos</b> uma coisa nova: uma célula.",
   "O teste faz o ciclo inteiro: cria a célula, confere dentro do equipamento, muda um parâmetro dela e por fim apaga. Isso é o que a Aula 2 chama de <b>CRUD</b> — criar, ler, alterar e apagar.",
   "A célula nova nasceu em <b>278 milissegundos</b> e, a partir daí, passou a ser gerenciada como qualquer outra: já dava para mudar a frequência dela.",
   "O que continua faltando é a camada de cima. Ninguém chega e pede “quero cobertura naquele bairro” para a célula aparecer sozinha. Não existe um modelo de serviço que faça isso. Isso seria <b>orquestração</b>, e a ferramenta não faz.",
   "Vale contar uma coisa que <b>não</b> deu certo, porque ela ensina: nós tentamos antes criar um equipamento novo inteiro, clonando um dos rádios. O equipamento sobe, mas o SMO nunca o enxerga como novo, porque os simuladores compartilham a mesma identidade. Criar função de rede com identidade própria seria papel da interface <b>O2</b>, que esta solução não tem."],
  "a contagem de células indo de <b>1 para 2</b> e voltando para 1 no fim.")}

{bloco("33:00–36:00", v3, "Bloco extra — os seis serviços da O1 (corte se estiver atrasado)", "amarra com a Aula 2",
  ["nada — é só fala"],
  ["Para fechar a análise no vocabulário da aula: a <b>Aula 2</b> divide a O1 em seis serviços de gerenciamento, os <b>MnS</b>.",
   "Nós exercitamos quatro deles. <b>Provisionamento</b> e <b>supervisão de falhas</b> por inteiro — foram os casos 2, 3 e 4. <b>Garantia de desempenho</b> e <b>gerência de arquivos</b> pela metade: as medições chegam e o aviso de arquivo pronto chega, mas o SMO não controla o que medir nem busca o arquivo.",
   "E dois não existem nesta solução: <b>rastreamento</b> e <b>gerência de software</b> dos equipamentos.",
   "Ou seja: a ferramenta entrega bem a parte de operar equipamentos, e não entrega a parte de orquestrar a rede."],
  "nada — é fala. Se quiser, deixe a topologia aberta ao fundo.")}

{bloco("36:00–40:00", v1, "Conclusão", "fecha e abre para perguntas",
  [],
  ["Resumindo o que vocês viram acontecer ao vivo: a pilha entrou sob gerência sozinha em <b>18 segundos</b>; configuramos três parâmetros em <b>menos de um segundo</b>, com prova dentro do equipamento; tratamos um alarme desde a chegada até a correção; e criamos e apagamos uma célula nova.",
   "A conclusão é a mesma da primeira parte, agora confirmada no uso: o SMO do O-RAN SC é <b>forte na gerência dos equipamentos</b> e não tem a camada de cima — orquestração, gestão da nuvem pela O2 e automação por políticas.",
   "Tudo o que mostramos está no nosso repositório, com os scripts, e roda em ARM64 nativo no nosso servidor. Obrigado — estamos à disposição para perguntas."],
  "nada — volte para a topologia se houver perguntas.")}

<h2>Glossário falado — como dizer cada palavra e o que ela significa</h2>
{tabela(["Palavra", "Como se lê", "Se precisar explicar, diga isto"], [
    ["SMO", "és-ême-ó", "O sistema que opera a rede inteira de um lugar só."],
    ["O-RAN", "ó-ran", "Rede de acesso aberta: as peças podem ser de fornecedores diferentes."],
    ["O1", "ó-um", "A interface por onde o SMO conversa com os equipamentos."],
    ["O-DU", "ó-dê-u", "A unidade que processa o sinal da antena."],
    ["O-RU", "ó-erre-u", "O rádio: o equipamento que transmite de verdade."],
    ["call home", "cól rôum", "O equipamento liga para o SMO quando sobe, e não o contrário."],
    ["YANG", "iang", "O “manual” que o equipamento entrega dizendo o que dá para ler e configurar nele."],
    ["NETCONF", "netcónfi", "O protocolo que a O1 usa para ler e escrever configuração no equipamento."],
    ["RESTCONF", "restcónfi", "O mesmo conteúdo, só que por HTTP: é assim que o painel fala com o SMO."],
    ["datastore", "dêita-stór", "A memória de configuração dentro do próprio equipamento."],
    ["VES", "vês", "O formato padrão dos eventos (alarmes e medições) que o equipamento envia."],
    ["Kafka", "cáfca", "A fila onde esses eventos ficam, e de onde qualquer sistema pode ler."],
    ["PCI", "pê-cê-í", "O número que identifica a célula no ar. Dois vizinhos iguais = conflito."],
    ["ARFCN", "arfecên", "O número do canal de frequência em que a célula transmite."],
    ["MnS", "ême-êne-ésse", "Os serviços de gerenciamento da O1, como a Aula 2 organiza."],
    ["CRUD", "crud", "Criar, ler, alterar e apagar."],
    ["O2", "ó-dois", "A interface do SMO com a nuvem. Não existe nesta solução."],
    ["orquestração", "—", "Coordenar várias peças a partir de um pedido só. É o que falta na ferramenta."],
])}

<h2>Se o professor perguntar — resposta pronta</h2>
<div class="qa"><b>Por que não usaram o gNB do laboratório de vocês?</b> ({e(v2)}) Porque ele não tem agente O1 — não sabe conversar com o SMO. Os simuladores do próprio O-RAN SC falam O1 de verdade.</div>
<div class="qa"><b>Isso que vocês mostraram é orquestração?</b> ({e(v2)}) Não. É gerenciamento e provisionamento. Orquestração precisaria de um modelo de serviço e de coordenação entre vários equipamentos, e a ferramenta não tem.</div>
<div class="qa"><b>Quem cria as funções de rede?</b> ({e(v1)}) No nosso laboratório, o Docker. Na arquitetura O-RAN isso seria o O-Cloud, pela interface O2 — que no O-RAN SC fica em outro projeto, não neste.</div>
<div class="qa"><b>O laço de correção é automático?</b> ({e(v3)}) Não. O SMO entrega os dados e o meio de configurar; a decisão foi nossa, dentro do teste. A decisão automática viria de uma aplicação de análise ou de política.</div>
<div class="qa"><b>Quais serviços da O1 vocês exercitaram?</b> ({e(v3)}) Provisionamento e falhas por inteiro; desempenho e arquivos pela metade; rastreamento e software de equipamento não existem nesta solução.</div>
<div class="qa"><b>Quanto isso consome de máquina?</b> ({e(v3)}) Cerca de 4,7 GB de memória, num servidor de 4 núcleos ARM64.</div>
<div class="qa"><b>Dava para usar isso numa operadora?</b> ({e(v1)}) Como camada de gerência, sim. Faltaria a orquestração, a O2 e endurecer a segurança — as senhas que vêm no projeto são de laboratório.</div>
<div class="qa"><b>Se não souberem responder:</b> digam a verdade — “isso a gente não testou; o que medimos foi tal coisa”. É melhor do que inventar, e o professor valoriza o limite bem marcado.</div>

<h2>Colinha de bolso — os números</h2>
{tabela(["Número", "Do quê"], [
    ["<b>18 s</b>", "a pilha inteira sob gerência depois de ser ligada"],
    ["<b>903 ms</b>", "os três parâmetros do plano de rede aplicados pela O1"],
    ["<b>384 ms</b>", "do alarme sair do equipamento até estar na fila do SMO"],
    ["<b>188 ms</b>", "a correção de PCI aceita e confirmada no equipamento"],
    ["<b>278 ms</b>", "a célula nova criada"],
    ["<b>154 e 114</b>", "modelos YANG que a O-DU e o rádio anunciaram"],
    ["<b>15 contêineres · 4,7 GB · 4 vCPU ARM64</b>", "o tamanho do SMO rodando no nosso servidor"],
])}

<footer>Gerado para uso do grupo — não versionar. {e(v1)} · {e(v2)} · {e(v3)} ·
Gestão, Orquestração e Automação em Redes OpenRAN · CESAR School</footer>
</body></html>"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--integrantes", required=True, help="três nomes separados por vírgula, na ordem das vozes")
    nomes = [n.strip() for n in ap.parse_args().integrantes.split(",") if n.strip()]
    if len(nomes) != 3:
        ap.error("a cola é para 3 vozes: passe exatamente três nomes")
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
