#!/usr/bin/env python3
"""COLA da apresentação da 2ª PARTE (26/09): provisionar e gerenciar uma pilha
Open RAN com o SMO — 40 minutos, 3 vozes. Reaproveita o estilo e os blocos da
cola da 1ª parte (cola_apresentacao.py).

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


def pagina(v1, v2, v3):
    logo = ""
    if os.path.exists(LOGO):
        logo = open(LOGO, encoding="utf-8").read().replace('width="561" height="500"', 'width="46" height="41"', 1)
    e = html.escape
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Cola — 2ª parte: provisionar e gerenciar uma pilha Open RAN com o SMO</title><style>{CSS}</style></head><body>
<div class="hd">{logo}<div>
  <h1>Cola da apresentação — 2ª parte: provisionar e gerenciar uma pilha Open RAN</h1>
  <div class="sub">Gestão, Orquestração e Automação em Redes OpenRAN · Prof. Lucas Borges de Oliveira ·
  <b>26/09 · 40 minutos · 3 vozes</b> · painel ao vivo: {PAINEL}</div></div></div>

<table>
<tr><th>Tempo</th><th>Quem</th><th>Bloco</th><th>Teste no painel</th></tr>
<tr><td>0:00–3:30</td><td><b>{e(v1)}</b></td><td>Abertura: o que a 1ª parte concluiu e o que vamos provar hoje</td><td>Topologia (Tour)</td></tr>
<tr><td>3:30–11:00</td><td><b>{e(v1)}</b></td><td>Caso 1 · Instanciar a pilha e pô-la sob gerência</td><td>Pilha: instanciar e pôr sob gerência</td></tr>
<tr><td>11:00–20:00</td><td><b>{e(v2)}</b></td><td>Caso 2 · Provisionar a pilha (plano de rede pela O1)</td><td>Provisionar a pilha (plano de rede)</td></tr>
<tr><td>20:00–28:00</td><td><b>{e(v3)}</b></td><td>Caso 3 · Operar: do alarme à correção</td><td>Operar: do alarme à correção</td></tr>
<tr><td>28:00–34:00</td><td><b>{e(v2)}</b></td><td>Caso 4 · Escalar a pilha</td><td>Escalar: uma função de rede nova</td></tr>
<tr><td>34:00–37:00</td><td><b>{e(v3)}</b></td><td>Os mecanismos: o que é do SMO e o que falta</td><td>SMO ao vivo · console ODLUX</td></tr>
<tr><td>37:00–40:00</td><td><b>{e(v1)}</b></td><td>Conclusão e próximos passos</td><td>—</td></tr>
</table>

<h2>Antes de começar (15 minutos antes) — {e(v1)}</h2>
<ol class="check">
<li>Abra <b>{PAINEL}</b> e entre como <b>Professor</b>. Aperte <b>Ctrl+Shift+R</b> (a versão mudou).</li>
<li>Quadrante <b>serviços</b>, Projeto 2: se o <b>E2 lab</b> estiver verde, desligue — ele come 3 dos 4 núcleos e deixa o SMO lento.</li>
<li>O botão <b>SMO</b> do cabeçalho tem de estar com o <b>ponto verde</b>. Se estiver apagado: quadrante serviços → <b>SMO</b> → OK, e espere ~5 minutos.</li>
<li>Aperte o botão <b>SMO</b> do cabeçalho e confira, no <b>SMO ao vivo</b>, os <b>2 elementos connected</b>. Feche.</li>
<li>Ensaio obrigatório: {RAIL} → <b>Pilha: instanciar e pôr sob gerência</b> → <b>▶ Iniciar teste</b>. Tem de terminar com
    <i>"pilha Open RAN instanciada e sob gerência"</i>. Aperte <b>limpar</b>. (Esse teste derruba e sobe as funções de rede: rodar antes evita surpresa.)</li>
<li>Abra uma <b>segunda aba</b> na <b>Topologia</b> e uma <b>terceira</b> no console ODLUX (já logado).</li>
</ol>

<div class="alerta"><b>Como todo teste funciona:</b> botão no rail → <b>▶ Iniciar teste</b> → a faixa acende etapa por etapa →
leia o <b>Resumo</b> e a caixa <b>"O que acabou de acontecer"</b> → <b>limpar</b>. O botão <b>mapa</b> mostra onde aquilo
acontece na rede. <b>Se um teste falhar:</b> leia o Resumo (ele diz o motivo), rode <b>uma</b> vez de novo e siga em frente.</div>

<h2>Os blocos</h2>
{bloco("0:00–3:30", v1, "Abertura — de analisar para operar", "o que muda da 1ª para a 2ª parte",
  ["vá para a aba da <b>Topologia</b>", "aperte <b>Tour</b> e avance até a banda do <b>SMO</b>, depois <b>Sair</b>"],
  ["Na 1ª parte nós analisamos o SMO do O-RAN SC nos oito itens e chegamos a uma conclusão: ele é forte na gerência de funções de rede — O1, M-plane, falhas e telemetria — e não traz O2, O-Cloud nem orquestração.",
   "Hoje a pergunta é outra: <b>dá para provisionar e operar uma pilha Open RAN com ele?</b> A resposta vem em quatro casos ao vivo: instanciar a pilha, provisionar um plano de rede, operar um alarme até a correção, e escalar com uma função de rede nova.",
   "Tudo roda agora, no nosso servidor ARM64, e cada número que vocês verão é medido na hora."],
  "a banda <b>SMO</b> e a banda <b>Rede gerenciada por O1</b> — a pilha que vamos operar.")}

{bloco("3:30–11:00", v1, "Caso 1 — Instanciar a pilha e pô-la sob gerência", "o começo de qualquer operação: descobrir o que existe",
  teste("Pilha: instanciar e pôr sob gerência") + ["(leva cerca de 1 minuto: deixe a faixa andar enquanto fala)", limpar],
  ["Uma pilha Open RAN é um conjunto de funções de rede: aqui, uma O-DU e dois O-RU. O teste <b>encerra a pilha inteira</b> e a <b>instancia de novo</b>, para vocês verem o SMO perceber tudo acontecendo.",
   "Repare no que ninguém faz: ninguém cadastra elemento no controlador. Cada função de rede, ao subir, <b>liga para o SMO</b> — é o call home do NETCONF — e o SMO a monta, lê os modelos YANG que ela anuncia e a põe no inventário.",
   "É esse inventário que sustenta todo o resto: o SMO só configura aquilo que descobriu. E quem instancia o contêiner aqui é o Docker, no papel que num O-RAN completo seria do O-Cloud, pela interface O2."],
  "o inventário <b>esvaziando</b> e depois <b>enchendo</b>, o tempo de call home de cada função de rede e o <b>connectionlog</b> (Unmounted → Mounted → Connected).",
  "se uma função de rede não voltar, rode o teste de novo: ele nunca deixa a pilha parada.")}

{bloco("11:00–20:00", v2, "Caso 2 — Provisionar a pilha", "o coração da avaliação: gerenciamento e provisionamento",
  teste("Provisionar a pilha (plano de rede)") + [limpar],
  ["Provisionar é aplicar um <b>plano de rede</b>: aqui, o nome da gNB-DU, o <b>PCI</b> da célula e o <b>ARFCN</b> de descida. Três parâmetros do modelo 3GPP que a O-DU anuncia.",
   "O caminho de cada escrita é o da O1: o painel manda um <b>PATCH</b> por RESTCONF ao controlador, que traduz para <b>edit-config</b> em NETCONF dentro do elemento. E a prova não é a tela do SMO: o teste confere cada valor <b>no datastore da própria O-DU</b>.",
   "Agora a parte honesta, que é o que a avaliação pede analisar: o SMO aplica <b>parâmetro por parâmetro</b>. Não há transação entre elementos, não há modelo de serviço, não há fluxo de trabalho. Se uma escrita falhar no meio, quem desfaz é o operador — neste teste, o próprio script, que reverte o plano inteiro no fim."],
  "o <b>lote</b> com o HTTP 200 e o tempo de cada escrita, a coluna <b>no datastore da O-DU</b> e o <b>desfazer</b> devolvendo tudo ao original.",
  "se alguma escrita for recusada, mostre o código HTTP no Resumo e diga que o parâmetro é somente leitura naquele modelo.")}

{bloco("20:00–28:00", v3, "Caso 3 — Operar: do alarme à correção", "gestão e operação do dia a dia",
  teste("Operar: do alarme à correção") + [limpar],
  ["Operar é o dia a dia depois que a rede está no ar. O teste simula um <b>conflito de PCI</b>: o elemento levanta um alarme, que sobe por <b>VES</b> até o coletor e é publicado no <b>barramento Kafka</b>, de onde qualquer sistema assina.",
   "Aí o laço se fecha: alguém lê o alarme, <b>decide</b> um PCI livre, <b>provisiona pela O1</b>, confere dentro do elemento e <b>limpa o alarme</b> pelo mesmo caminho. No fim a célula volta ao plano original.",
   "Quem decidiu aqui foi o nosso teste, no papel que caberia a uma rApp de SON. E é essa a análise: o SMO do O-RAN SC <b>entrega os meios</b> — os dados no barramento e o provisionamento pela O1 —, mas não a automação. Quem decidiria sozinho seria o RAN Analytics e o Policy Management, e quem levaria a política ao near-RT RIC seria a A1; nenhum dos dois está nesta solução."],
  "o tempo do alarme até o barramento, o <b>HTTP 200</b> da correção, o PCI novo <b>dentro do equipamento</b> e a limpeza.",
  "se a correção for recusada, diga que o PCI é somente leitura nesse simulador e mostre o alarme chegando ao barramento, que é o essencial do bloco.")}

{bloco("28:00–34:00", v2, "Caso 4 — Escalar a pilha", "ciclo de vida: a pilha cresce",
  teste("Escalar: uma função de rede nova") + ["(leva cerca de 1 minuto)", limpar],
  ["Escalar é acrescentar capacidade. O teste <b>instancia uma função de rede que não existia</b>, copiando a configuração de um dos O-RU e dando um nome próprio a ela.",
   "Ela sobe, liga para o SMO e entra no inventário <b>sozinha</b> — o inventário cresce na frente de vocês. Depois o teste a encerra e a remove, e a pilha volta ao tamanho original.",
   "Esse é o teste que separa as duas coisas que a avaliação pede distinguir: <b>descobrir, montar e gerenciar</b> é do SMO; <b>instanciar, escalar e encerrar</b> seria do O-Cloud pela O2 DMS — que no O-RAN SC vive no projeto INF, não no OAM. Aqui, quem fez esse papel foi o Docker."],
  "o inventário passando de 2 para 3 elementos e voltando, e o tempo do call home da função de rede nova.")}

{bloco("34:00–37:00", v3, "Os mecanismos, em uma tela", "análise pedida pela avaliação",
  ["botão <b>SMO</b> do cabeçalho → <b>SMO ao vivo</b>",
   "se quiserem ver a interface do operador: aba do <b>console ODLUX</b> → <b>Connect</b> e <b>Fault</b>"],
  ["Resumindo os mecanismos que a solução emprega: <b>descoberta e inventário</b> por call home; <b>provisionamento</b> por NETCONF/YANG com RESTCONF na frente; <b>supervisão de falhas</b> por dois canais, VES no barramento e notificações NETCONF no banco do controlador; <b>telemetria</b> por arquivo 3GPP com aviso FileReady; e <b>identidade</b> com Keycloak.",
   "E os que ela não emprega: não há orquestração de serviço, não há gestão de O-Cloud, não há automação orientada por políticas.",
   "Na prática, isso quer dizer que o SMO do O-RAN SC é uma base de gerência sólida sobre a qual ainda é preciso compor o resto."],
  "no SMO ao vivo: elementos sob gerência, alarmes e os últimos eventos do barramento — tudo o que os quatro casos produziram.")}

{bloco("37:00–40:00", v1, "Conclusão", "fecha a apresentação",
  [],
  ["Em quatro casos nós instanciamos uma pilha Open RAN, provisionamos um plano de rede nela pela O1 com confirmação dentro dos equipamentos, fechamos um laço de operação de um alarme até a correção, e escalamos a pilha com uma função de rede nova.",
   "O que o SMO do O-RAN SC entregou: descoberta automática, inventário, provisionamento verificável e os dados de operação num barramento aberto. O que ele não entregou: orquestração, O-Cloud pela O2 e automação por políticas.",
   "Tudo o que mostramos está no repositório do grupo, com os scripts e o passo a passo — e roda em ARM64 nativo, com as sete imagens que tivemos de reconstruir. Obrigado."],
  "nada — volte para a topologia se houver perguntas.")}

<h2>Perguntas prováveis — quem responde</h2>
<div class="qa"><b>Por que simuladores e não o gNB do laboratório?</b> ({e(v2)}) O gNB monolítico do OpenAirInterface não tem agente O1. As funções de rede do O-RAN SC falam O1 e M-plane de verdade.</div>
<div class="qa"><b>Isso é orquestração?</b> ({e(v2)}) Não. É gerenciamento e provisionamento. Orquestração exigiria modelo de serviço e fluxo entre elementos — o NFO e o SO, que esta solução não traz.</div>
<div class="qa"><b>Quem instancia as funções de rede?</b> ({e(v1)}) Aqui, o Docker. Num O-RAN completo, o O-Cloud pela O2 DMS; no O-RAN SC isso é o projeto INF, sobre StarlingX.</div>
<div class="qa"><b>O laço de operação é automático?</b> ({e(v3)}) Não: quem decide é o operador ou uma rApp. O SMO entrega os dados no barramento e o provisionamento pela O1.</div>
<div class="qa"><b>Dá para operar uma rede real com isso?</b> ({e(v1)}) Como base de gerência, sim; faltam orquestração, O-Cloud e o endurecimento de segurança — as senhas do upstream são de laboratório.</div>
<div class="qa"><b>Quanto custa rodar?</b> ({e(v3)}) Cerca de 4,7 GB de memória para o SMO com os simuladores, em 4 vCPU ARM64.</div>

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
