#!/usr/bin/env python3
"""Relatório da 2ª PARTE (70%): provisionar e gerenciar uma pilha Open RAN com
o SMO do O-RAN SC. Reaproveita o estilo do relatório da 1ª parte.

Os números vêm das execuções dos quatro testes no servidor do grupo em
25/09/2026 (server/smo/smo_p2_*.sh); o texto não recalcula nada.

Uso: python3 build_relatorio_p2.py --integrantes "Nome 1,Nome 2,Nome 3"
"""
import argparse
import html
import os
import shutil
import subprocess

import build_relatorio_smo as r1

CSS, tab, caminho, logo = r1.CSS, r1.tab, r1.caminho, r1.logo
SIM, PARC, NAO = r1.SIM, r1.PARC, r1.NAO
OUT, GIT, PAINEL = r1.OUT, r1.GIT, r1.PAINEL
NOME = "RELATORIO_SMO_P2_PILHA"


def ev(teste, script, *linhas):
    corpo = "".join(f"<p>{l}</p>" for l in linhas)
    return (f'<div class="box ev"><p><b>Evidência — teste “{teste}”</b> '
            f'(<a href="{GIT}/blob/main/server/smo/{script}"><code>server/smo/{script}</code></a>, 25/09/2026)</p>{corpo}</div>')


def pagina(n1, n2, n3):
    e = html.escape
    n1, n2, n3 = e(n1), e(n2), e(n3)
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Relatório — provisionamento e gerenciamento de uma pilha Open RAN com o SMO</title><style>{CSS}</style></head><body>

<section class="capa">
  <div class="logo">{logo(40)}</div>
  <div class="inst"><b>CESAR School</b><br>Especialização em Open RAN — Redes Abertas e Tecnologias Emergentes<br>
  Gestão, Orquestração e Automação em Redes OpenRAN</div>
  <div class="meio">
    <h1>Provisionamento e gerenciamento de uma pilha Open RAN com o SMO da O-RAN Software Community</h1>
    <div class="sub">Relatório da avaliação — 2ª parte (70%): provisionamento, gerenciamento e acompanhamento de uma
    pilha Open RAN utilizando SMO</div>
    <div class="fio"></div>
    <div class="quem">Trabalho em grupo<br><b>{n1}</b><br><b>{n2}</b><br><b>{n3}</b><br><br>
    Professor: Lucas Borges de Oliveira</div>
  </div>
  <div class="pe">Recife, 26 de setembro de 2026</div>
</section>

<h2 style="margin-top:0">Resumo</h2>
<p>Na 1ª parte analisamos o SMO da O-RAN Software Community (solução do projeto OAM) e concluímos que ele é sólido
na gerência de funções de rede e não traz orquestração, O-Cloud nem automação por políticas. Esta 2ª parte põe essa
conclusão à prova no uso: <b>provisionamos e operamos uma pilha Open RAN</b> com a mesma ferramenta, no servidor
ARM64 do grupo, em quatro casos medidos ao vivo. A pilha — uma O-DU e dois O-RU simulados — foi instanciada e
colocada sob gerência <b>em 18 s</b>, sem nenhuma configuração manual no controlador. Um plano de rede de três
parâmetros foi aplicado pela O1 <b>em 903 ms</b>, conferido dentro do datastore do equipamento e revertido. Um laço
de operação foi fechado da falha à correção: alarme no barramento <b>em 384 ms</b>, reconfiguração provisionada
<b>em 188 ms</b> e alarme limpo. E uma célula nova foi criada, alterada e apagada pela O1 (<b>HTTP 201 em 278 ms</b>),
com tudo confirmado dentro do elemento. O relatório descreve, caso a caso, os mecanismos de gestão, orquestração e
operação que a solução emprega — e os que ela não emprega, com a evidência de cada afirmação.</p>
<p class="kw"><b>Palavras-chave:</b> SMO; O-RAN SC; provisionamento; interface O1; NETCONF/YANG; operação de rede; O2.</p>

<h2>1. Objetivo e método</h2>
<p>A 2ª parte da avaliação pede usar a ferramenta de SMO analisada na 1ª parte para realizar o
<b>provisionamento, o gerenciamento e o acompanhamento de uma pilha Open RAN</b> e analisar os mecanismos de gestão,
orquestração e operação empregados pela solução. Os quatro casos deste relatório cobrem os três verbos:
provisionamento (casos 2 e 4), gerenciamento (casos 1 e 2) e acompanhamento (caso 3, com as falhas e a telemetria
que o SMO recebe continuamente). A ferramenta é o SMO da O-RAN SC, na solução <i>docker compose</i> do projeto OAM, rodando
no servidor do grupo (4 vCPU ARM64, 16 GiB), descrito no relatório da 1ª parte.</p>
<p>O método é o mesmo: em vez de descrever a documentação, <b>operamos a pilha de verdade</b> e medimos. Para cada
etapa do ciclo de vida operacional escrevemos um teste reproduzível, que conversa com o SMO pelo gateway como um
operador faria. Os quatro testes estão no painel do laboratório e no repositório, e os números deste relatório vêm
das execuções de 25/09/2026 (Tabela 1).</p>
{tab(["Caso", "Pergunta que responde", "Teste"], [
    ["1 — Instanciar a pilha", "Como as funções de rede entram sob gerência? O que o SMO faz sozinho?", "<code>smo_p2_pilha.sh</code>"],
    ["2 — Provisionar a pilha", "Como se aplica um plano de rede? A configuração chega ao equipamento?", "<code>smo_p2_provisiona.sh</code>"],
    ["3 — Operar a pilha", "Como é o dia a dia: da falha observada à correção aplicada?", "<code>smo_p2_operacao.sh</code>"],
    ["4 — Escalar a pilha", "Dá para criar capacidade nova, e não só alterar o que existe?", "<code>smo_p2_escala.sh</code>"],
], "Tabela 1 — Os quatro casos e os testes que os medem")}

<h2>2. A pilha Open RAN sob gerência</h2>
<p>A pilha é composta por três funções de rede simuladas pelo <i>pynts</i>, o simulador do próprio O-RAN SC, que
implementa os modelos YANG da O-RAN e do 3GPP e fala NETCONF de verdade (Tabela 2). O gNB do OpenAirInterface, usado
nas outras disciplinas do laboratório, não tem agente O1 e por isso não pode ser gerenciado por esta pilha — uma
limitação relevante, tratada na seção 7.</p>
{tab(["Função de rede", "Papel", "Interface com o SMO", "Modelos YANG"], [
    ["<code>pynts-o-du-o1</code>", "O-DU (unidade distribuída)", "O1 · NETCONF sobre TLS (:6513)", "154"],
    ["<code>pynts-o-ru-hybrid</code>", "O-RU no modelo híbrido", "M-plane do Open Fronthaul · NETCONF sobre SSH (:830)", "114"],
    ["<code>pynts-o-ru-hierarchical</code>", "O-RU no modelo hierárquico", "nenhuma: quem o gerencia é a O-DU", "—"],
], "Tabela 2 — A pilha Open RAN gerenciada nos quatro casos")}

<h2>3. Caso 1 — Instanciar a pilha e pô-la sob gerência</h2>
<p>Toda operação começa por saber o que existe. O teste encerra a pilha inteira e a instancia de novo, medindo o que
o SMO faz por conta própria. O resultado é que ele faz o essencial sozinho: <b>descobre, monta e inventaria</b>.
Nenhum elemento é cadastrado à mão no controlador; cada função de rede, ao subir, abre a conexão na direção do SMO
(NETCONF <i>call home</i>) e é montada automaticamente.</p>
{caminho("função de rede sobe", "call home (portas 4334/4335 do gateway)", "controlador monta o nó", "lê os modelos YANG", "inventário")}
{tab(["Fase", "O que aconteceu", "Medida"], [
    ["Pilha em operação", "inventário com a O-DU conectada", "1 elemento"],
    ["Encerrar", "as 3 funções de rede encerradas; o inventário esvazia", "<b>1 s</b>"],
    ["Instanciar", "O-RU híbrido conectado", "<b>4 s</b>"],
    ["Instanciar", "O-DU conectada (é quem anuncia mais modelos)", "<b>18 s</b>"],
    ["Sob gerência", "inventário completo: O-DU (154 modelos) e O-RU híbrido (114)", "2 elementos"],
    ["Registro", "connectionlog do controlador: Unmounted → Mounted → Connected por elemento", "auditável"],
], "Tabela 3 — Instanciação da pilha e entrada sob gerência")}
<p>O O-RU hierárquico não aparece no inventário, e isso é o comportamento correto: no modelo hierárquico do M-plane
quem o gerencia é a O-DU, não o SMO. Ou seja, a pilha tem três funções de rede, mas apenas duas fronteiras de
gerência — distinção que a própria ferramenta torna visível.</p>
{ev("Pilha: instanciar e pôr sob gerência", "smo_p2_pilha.sh",
   "Resultado: “pilha Open RAN instanciada e sob gerência do SMO — descoberta, montagem e inventário automáticos”. "
   "Toda a pilha sob gerência em 18 s, sem tocar na configuração do controlador.")}

<h2>4. Caso 2 — Provisionar a pilha</h2>
<p>Provisionar é aplicar um plano de rede sobre o que foi descoberto. O teste aplica três parâmetros do modelo 3GPP
na O-DU: o nome da gNB-DU, o <b>PCI</b> da célula e o <b>ARFCN</b> de descida. Cada um é um RESTCONF <b>PATCH</b> que
o controlador traduz em <i>edit-config</i> NETCONF dentro do elemento.</p>
{caminho("plano de rede", "RESTCONF PATCH", "controlador", "NETCONF edit-config", "datastore running do elemento")}
{tab(["Parâmetro", "Antes", "Depois", "Resposta", "Confirmado no equipamento"], [
    ["<code>gNBDUName</code>", "<code>hostname_here</code>", "<code>core5g-du-194611</code>", "HTTP 200 · 440 ms", "sim"],
    ["<code>nRPCI</code> (PCI)", "1", "7", "HTTP 200 · 221 ms", "sim"],
    ["<code>arfcnDL</code>", "1", "632628", "HTTP 200 · 234 ms", "sim"],
], "Tabela 4 — Plano de rede aplicado pela O1 (lote completo em 903 ms)", num=(1, 2))}
<p>Dois pontos merecem destaque na análise. O primeiro é a <b>verificação</b>: o teste não se contenta com a resposta
do SMO; lê o valor de volta pela O1 <b>e</b> dentro do datastore <code>running</code> do próprio simulador, por
<code>sysrepocfg</code>. Os três parâmetros bateram nos dois lados. O segundo é o <b>limite</b>: cada parâmetro é uma
escrita independente. Não há transação que cubra vários parâmetros ou vários elementos, não há modelo de serviço e
não há fluxo de trabalho. Se uma escrita falhasse no meio do plano, a pilha ficaria em estado misto e caberia ao
operador desfazer — no teste, quem desfaz é o próprio script, que reverte o plano inteiro ao final.</p>
{ev("Provisionar a pilha (plano de rede)", "smo_p2_provisiona.sh",
   "Resultado: “provisionamento da pilha ponta a ponta — escritas confirmadas no elemento e revertidas”. "
   "3 parâmetros aplicados em 903 ms; todos conferidos no datastore da O-DU e revertidos aos valores originais.")}

<h2>5. Caso 3 — Operar a pilha: da falha à correção</h2>
<p>Operar é o que acontece depois que a rede está no ar. O teste percorre o laço completo: um alarme de <b>conflito
de PCI</b> é levantado em nome da O-DU, sobe por VES até o coletor, é publicado no barramento Kafka, e a partir dele
uma decisão é tomada, provisionada pela O1, verificada no equipamento e o alarme é limpo.</p>
{caminho("alarme VES 7.2.1", "coletor", "Kafka: tópico de falhas", "decisão", "PATCH pela O1", "verificação no elemento", "limpeza")}
{tab(["Passo", "Medida", "Observação"], [
    ["Alarme aceito pelo coletor VES", "HTTP 202", "formato VES 7.2.1, domínio <i>fault</i>, severidade CRITICAL"],
    ["Alarme disponível no barramento", "<b>384 ms</b>", "tópico <code>unauthenticated.SEC_FAULT_OUTPUT</code>"],
    ["Correção provisionada pela O1", "HTTP 200 · <b>188 ms</b>", "PCI de 1 para 7"],
    ["Correção confirmada no equipamento", "PCI 7 no sysrepo da O-DU", "não é só a tela do SMO"],
    ["Alarme limpo (NORMAL)", "HTTP 202 · <b>399 ms</b> até o barramento", "tópico foi de 17 para 19 eventos"],
    ["Plano restaurado", "PCI de volta a 1", "o teste não deixa a pilha alterada"],
], "Tabela 5 — Laço de operação, da falha à correção")}
<p><b>Quem agiu.</b> Do lado da solução, agiram a gerência de funções de rede (falhas e provisionamento pela O1) e o
barramento de dados (o tópico VES onde o alarme ficou disponível para qualquer consumidor). <b>Quem não existe.</b>
A decisão — ler o alarme, escolher um PCI livre e mandar aplicar — foi tomada pelo nosso teste, no papel que caberia
a uma rApp de SON. Na arquitetura O-RAN, isso seria dos serviços de análise e de política, e a orientação chegaria ao
near-RT RIC pela interface A1; nenhum dos dois faz parte desta solução. A conclusão prática é precisa: <b>o SMO do
O-RAN SC entrega os meios do laço fechado — os dados e o provisionamento — mas não a automação</b>.</p>
{ev("Operar: do alarme à correção", "smo_p2_operacao.sh",
   "Resultado: “laço de operação fechado sobre a pilha: falha → decisão → provisionamento → verificação → limpeza”. "
   "No momento do teste o controlador tinha 0 alarmes ativos e 14 no histórico, e o barramento já acumulava 1.020 eventos de medida.")}

<h2>6. Caso 4 — Escalar a pilha com capacidade nova</h2>
<p>Os casos anteriores alteram o que existe. Este cria o que não existia: uma <b>célula nova</b> na O-DU, provisionada
pela O1. É o ciclo completo de operações de configuração — criar, ler, alterar e apagar — sobre o modelo de recursos
de rede do 3GPP.</p>
{tab(["Operação", "Chamada", "Resultado", "Verificação no equipamento"], [
    ["Criar", "RESTCONF POST na lista de células", "<b>HTTP 201 em 278 ms</b>", "a O-DU passa a ter 2 células"],
    ["Ler", "estado do datastore do elemento", "NRCellDU-002 · PCI 11 · cellLocalId 2", "atributos herdados da célula existente"],
    ["Alterar", "PATCH <code>arfcnDL=640000</code>", "HTTP 200", "640000 no sysrepo da O-DU"],
    ["Apagar", "DELETE da célula", "HTTP 204", "a pilha volta a 1 célula"],
], "Tabela 6 — Ciclo CRUD de um objeto de rede pela O1")}
<p>O resultado mostra que a pilha é <b>elástica do ponto de vista da configuração</b>: objetos de rede podem ser
criados e removidos em operação, e passam a ser gerenciados como qualquer outro assim que existem. O que não existe
é a camada acima: nenhum modelo de serviço gera essa célula a partir de uma intenção (“quero cobertura nesta área”),
e nada coordena a criação equivalente em vários elementos. Isso seria o papel do <i>Service and Slice Subnet
Orchestration</i> e do <i>Network Functions Orchestration</i>.</p>
<p><b>Uma tentativa que não funcionou, e o que ela ensina.</b> A primeira versão deste caso tentava escalar de outro
modo: instanciar um <b>contêiner novo</b> de função de rede, clonando a configuração de um O-RU existente, para ver o
SMO descobri-lo. O contêiner sobe, mas nunca aparece no inventário, porque os simuladores compartilham a identidade
NETCONF (chaves e configuração de call home montadas do mesmo diretório): para o SMO, o clone é o mesmo elemento.
Isso não é um defeito do SMO — é a demonstração concreta de que <b>instanciar funções de rede não é papel dele</b>.
Sem um O-Cloud com O2 DMS, que criaria a função de rede com identidade, certificados e endereço próprios, escalar a
pilha em número de elementos fica fora do alcance da solução.</p>
{ev("Escalar: uma célula nova pela O1", "smo_p2_escala.sh",
   "Resultado: “escalar a pilha pela O1 funciona ponta a ponta — criar, alterar e apagar objetos de rede, confirmados no elemento”.")}

<h2>7. Os mecanismos empregados pela solução</h2>
<p>Reunindo os quatro casos, a Tabela 7 responde diretamente ao que a avaliação pede analisar: quais mecanismos de
gestão, orquestração e operação a solução emprega, com a evidência de cada um e a lacuna correspondente.</p>
{tab(["Mecanismo", "Como a solução o emprega", "Evidência", "Situação"], [
    ["Descoberta e inventário", "call home NETCONF: a função de rede se apresenta e o controlador a monta e lê seus modelos YANG",
     "pilha sob gerência em 18 s (Caso 1)", SIM],
    ["Provisionamento de configuração", "CRUD sobre modelos YANG por RESTCONF/NETCONF, com confirmação no datastore do elemento",
     "plano de 3 parâmetros em 903 ms (Caso 2); célula criada e apagada (Caso 4)", SIM],
    ["Gerência de falhas", "dois canais: eventos VES publicados no barramento e notificações NETCONF guardadas pelo controlador",
     "alarme no barramento em 384 ms (Caso 3)", SIM],
    ["Acompanhamento: monitoramento e telemetria", "medidas 3GPP em arquivo, anunciadas por evento VES FileReady no barramento, sem o SMO consultar o elemento",
     "1.020 eventos de medida acumulados (Caso 3)", SIM],
    ["Exposição de dados", "um tópico Kafka por domínio de evento, aberto a qualquer consumidor, com acesso HTTP pela ponte",
     "o laço do Caso 3 consumiu o alarme do próprio barramento", PARC],
    ["Operação em laço fechado", "os meios existem, mas a decisão é externa: não há análise nem política na solução",
     "quem decidiu a correção foi o teste (Caso 3)", PARC],
    ["Transação e consistência", "escritas independentes, sem transação entre parâmetros ou elementos",
     "rollback conduzido pelo operador (Caso 2)", NAO],
    ["Orquestração de serviço", "ausente: nenhum modelo de serviço, intenção ou fluxo de trabalho",
     "a célula nova é criada objeto a objeto (Caso 4)", NAO],
    ["Ciclo de vida de funções de rede", "o SMO observa e reage, mas não instancia nem encerra funções de rede",
     "o clone de contêiner não vira elemento novo (Caso 4)", NAO],
    ["Gestão do O-Cloud (O2)", "ausente nesta solução; no O-RAN SC vive no projeto INF",
     "relatório da 1ª parte, seção 6.3", NAO],
], "Tabela 7 — Mecanismos de gestão, orquestração e operação")}

<h2>8. Limites e achados da operação</h2>
<ul>
<li><b>Funções de rede precisam falar O1.</b> O gNB do OpenAirInterface do laboratório não tem agente O1 e por isso
fica fora da gerência; a pilha usa os simuladores do O-RAN SC, que implementam os modelos de verdade.</li>
<li><b>Identidade das funções de rede.</b> Escalar em número de elementos exige que cada função de rede nasça com
identidade própria — o que, na arquitetura, seria entregue pela O2 DMS ao instanciá-la.</li>
<li><b>Estado após desligamento abrupto.</b> Ao religar o servidor para esta demonstração, o Kafka recusou-se a
iniciar porque o Zookeeper ainda guardava o registro do <i>broker</i> anterior (<code>NodeExists</code>); reiniciar o
Zookeeper antes do Kafka resolveu. É o tipo de operação que um SMO com gestão de O-Cloud trataria sozinho.</li>
<li><b>Disputa por recursos.</b> O SMO com a pilha consome cerca de 4,8 GiB dos 16 GiB do servidor; com a pilha 5G do
laboratório ligada ao mesmo tempo, o controlador chega a ficar sem resposta. Sem O2, o SMO não enxerga essa
disputa.</li>
</ul>

<h2>9. Conclusão</h2>
<div class="junto">
<p>A 2ª parte confirma, no uso, o que a 1ª parte havia concluído pela análise. Com o SMO da O-RAN SC nós
<b>provisionamos e operamos uma pilha Open RAN de ponta a ponta</b>: a pilha entrou sob gerência sozinha em 18 s,
recebeu um plano de rede aplicado e verificado dentro dos equipamentos em menos de um segundo, teve uma falha tratada
da observação à correção em pouco mais de meio segundo somando os dois trechos medidos, e ganhou — e perdeu —
capacidade nova por operações de criação e remoção pela O1.</p>
<p>Nada disso exigiu configurar o controlador à mão, e tudo foi confirmado dentro dos elementos, não apenas na tela do
SMO. Essa é a força da ferramenta: uma implementação fiel e verificável da gerência de funções de rede O-RAN, com
tudo acessível por interfaces abertas.</p>
<p>E o limite, que aparece com a mesma nitidez, é onde a operação deixa de ser gerência e passa a ser orquestração:
não há transação entre elementos, não há modelo de serviço, não há automação por políticas e não há gestão do
O-Cloud. Para operar uma rede real, o SMO do O-RAN SC precisa ser a <b>camada de gerência</b> de um conjunto maior —
com o projeto INF para a O2, o Non-RT RIC para a A1 e as rApps, e um orquestrador de serviço acima de tudo isso.</p>
</div>
<div class="fecho"><p><b>Em uma frase:</b> a pilha Open RAN foi provisionada e operada com sucesso pelo SMO do
O-RAN SC — e cada limite encontrado no caminho está exatamente onde a arquitetura O-RAN prevê outra peça.</p></div>

<h2>Referências</h2>
<div class="ref">
<p>3GPP. <b>TS 28.541</b>: Management and orchestration; 5G Network Resource Model (NRM). 3rd Generation Partnership Project.</p>
<p>BIERMAN, A.; BJORKLUND, M.; WATSEN, K. <b>RFC 8040</b>: RESTCONF Protocol. IETF, 2017.</p>
<p>ENNS, R. et al. <b>RFC 6241</b>: Network Configuration Protocol (NETCONF). IETF, 2011.</p>
<p>OLIVEIRA, L. B. de. <b>Aula 1 — Service Management and Orchestrator (SMO)</b>. Gestão, Orquestração e Automação em
Redes OpenRAN. Recife: CESAR School, 2026. Slides de aula.</p>
<p>O-RAN ALLIANCE. <b>O-RAN Operations and Maintenance Interface Specification</b> (O1). Especificação técnica.</p>
<p>O-RAN SOFTWARE COMMUNITY. <b>Repositório oam</b>. Disponível em:
<a href="https://github.com/o-ran-sc/oam">https://github.com/o-ran-sc/oam</a>.</p>
<p>WATSEN, K. <b>RFC 8071</b>: NETCONF Call Home and RESTCONF Call Home. IETF, 2017.</p>
<p>Relatório da 1ª parte e repositório do grupo: <a href="{GIT}">{GIT}</a>.</p>
</div>

<h2>Apêndice A — Como reproduzir</h2>
<p>Com o SMO no ar (botão <b>SMO</b> do painel, em <a href="{PAINEL}">{PAINEL}</a>), a partir de
<code>server/smo/</code> no servidor — ou pelos botões da cadeira 5 no painel, grupo “Parte 2”:</p>
{tab(["Comando", "Caso"], [
    ["<code>./smo_p2_pilha.sh</code>", "1 — instanciar a pilha e pô-la sob gerência"],
    ["<code>./smo_p2_provisiona.sh</code>", "2 — aplicar e desfazer um plano de rede pela O1"],
    ["<code>./smo_p2_operacao.sh</code>", "3 — laço de operação, do alarme à correção"],
    ["<code>./smo_p2_escala.sh</code>", "4 — criar, alterar e apagar uma célula pela O1"],
])}
</body></html>"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--integrantes", required=True, help="três nomes separados por vírgula")
    nomes = [n.strip() for n in ap.parse_args().integrantes.split(",") if n.strip()]
    if len(nomes) != 3:
        ap.error("passe exatamente três nomes")
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
