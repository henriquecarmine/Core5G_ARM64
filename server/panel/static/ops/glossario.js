// ============================================================================
// Glossário 5G / O-RAN — o que cada sigla é e para que serve.
//
// POR QUE ISTO EXISTE
// As legendas da Jornada do UE são densas de sigla: "o AMF pede ao SMF a sessão
// PDU (N11/Nsmf)". Quem já sabe, lê. Quem está aprendendo, trava. Este módulo
// marca cada termo NO TEXTO JÁ ESCRITO — sem reescrever as legendas — e faz duas
// coisas:
//   1. escreve o nome por extenso ENTRE PARÊNTESES, uma vez por bloco;
//   2. abre um balão no hover/foco/toque com "o que é" e "para que serve".
//
// AS DUAS CAMADAS, E POR QUE ELAS SÃO SEPARADAS
//   TERMOS  — o nome oficial 3GPP/O-RAN. NÃO se traduz, nos 4 idiomas (é a mesma
//             regra do static/i18n.js: traduz-se a explicação, nunca o termo).
//             Por isso ele mora aqui, uma vez só, fora dos dicionários.
//   DICTS   — a explicação, essa sim em pt/en/es/fr. Duas chaves por termo:
//             `<termo>.o` = o que é · `<termo>.p` = para que serve.
//   Paridade dos 4 idiomas e casamento TERMOS↔DICTS: test/i18n-parity.js.
//
// COMO USAR (a página não precisa saber de nada disto):
//   <script src="/static/ops/glossario.js?v=%VER%"></script>
//   Glossario.marcar(document.getElementById("tour-caption"));
// `marcar` percorre só NÓS DE TEXTO — o HTML que já está lá (chips, <b>, links)
// passa intacto. Chamar de novo no mesmo elemento é seguro: o que já foi
// marcado é ignorado.
//
// exp = null: nome de produto ou procedimento que não é sigla (MySQL, iperf3,
// NG Setup). Não ganha parêntese — só o balão.
// ============================================================================
(function () {
  'use strict';

  // --- 1. Os termos e o que entra entre parênteses -------------------------
  var TERMOS = {
    // rádio / RAN
    'UE': 'User Equipment',
    'gNB': 'next generation NodeB',
    'RAN': 'Radio Access Network',
    'O-RAN': 'Open Radio Access Network',
    'O-RAN SC': 'O-RAN Software Community',
    'RU': 'Radio Unit',
    'DU': 'Distributed Unit',
    'RF': 'Radio Frequency',
    'RFSIM': 'RF simulator',
    'UERANSIM': 'UE + RAN simulator',
    'PRB': 'Physical Resource Block',
    'SINR': 'Signal to Interference plus Noise Ratio',
    'CQI': 'Channel Quality Indicator',
    // núcleo — funções de rede
    'AMF': 'Access and Mobility Management Function',
    'SMF': 'Session Management Function',
    'UPF': 'User Plane Function',
    'UPF-A': 'User Plane Function A',
    'UPF-B': 'User Plane Function B',
    'NRF': 'Network Repository Function',
    'AUSF': 'Authentication Server Function',
    'UDM': 'Unified Data Management',
    'UDR': 'Unified Data Repository',
    'NSSF': 'Network Slice Selection Function',
    'PCF': 'Policy Control Function',
    'BSF': 'Binding Support Function',
    'SCP': 'Service Communication Proxy',
    'DN': 'Data Network',
    // interfaces — o parêntese diz QUEM FALA COM QUEM
    'N1': 'UE ↔ AMF',
    'N2': 'gNB ↔ AMF',
    'N3': 'gNB ↔ UPF',
    'N4': 'SMF ↔ UPF',
    'N6': 'UPF ↔ DN',
    'N11': 'AMF ↔ SMF',
    'E2': 'near-RT RIC ↔ gNB',
    'E42': 'xApp ↔ near-RT RIC',
    'A1': 'Non-RT RIC ↔ near-RT RIC',
    'O1': 'SMO ↔ O-RAN nodes',
    // protocolos e procedimentos
    'NAS': 'Non-Access Stratum',
    'NGAP': 'NG Application Protocol',
    'SCTP': 'Stream Control Transmission Protocol',
    'GTP-U': 'GPRS Tunnelling Protocol · User plane',
    'PFCP': 'Packet Forwarding Control Protocol',
    'SBI': 'Service Based Interface',
    'NG Setup': null,
    '5G-AKA': '5G Authentication and Key Agreement',
    'NAT': 'Network Address Translation',
    'CUPS': 'Control and User Plane Separation',
    'PDU Session': null,
    'PDU': 'Protocol Data Unit',
    'slice': null,
    'S-NSSAI': 'Single Network Slice Selection Assistance Information',
    'SST': 'Slice/Service Type',
    'SD': 'Slice Differentiator',
    'QoS': 'Quality of Service',
    'IMSI': 'International Mobile Subscriber Identity',
    // RIC — a camada de inteligência
    'RIC': 'RAN Intelligent Controller',
    'near-RT': 'near-Real-Time',
    'Non-RT': 'Non-Real-Time',
    'xApp': 'near-RT RIC app',
    'rApp': 'Non-RT RIC app',
    'PMS': 'Policy Management Service',
    'FlexRIC': 'near-RT RIC · OpenAirInterface',
    'KPM': 'Key Performance Measurement',
    'RC': 'RAN Control',
    'E2AP': 'E2 Application Protocol',
    'E2SM-KPM': 'E2 Service Model · Key Performance Measurement',
    'E2SM-RC': 'E2 Service Model · RAN Control',
    'A1AP': 'A1 Application Protocol',
    'SDL': 'Shared Data Layer',
    // bancos e ferramentas do lab
    'MySQL': null,
    'MongoDB': null,
    'iperf3': null,
  };

  // --- 2. As explicações, nos 4 idiomas ------------------------------------
  var DICTS = {

  // ---------------------------------------------------------------- pt (canônico)
  pt: {
    'ui.o': 'O que é', 'ui.p': 'Para que serve',

    'UE.o': 'O celular — qualquer aparelho que se conecta à rede 5G. No lab ele é simulado por software.',
    'UE.p': 'É o começo de tudo: registro, sessão de dados e tráfego nascem nele.',
    'gNB.o': 'A estação rádio-base do 5G — a "antena" que fala com o celular pelo ar.',
    'gNB.p': 'Liga o rádio ao núcleo: sinaliza pelo N2 e encaminha os dados do usuário pelo N3.',
    'RAN.o': 'A parte de rádio da rede: tudo o que fica entre o celular e o núcleo.',
    'RAN.p': 'Leva o sinal do ar até a rede — é onde a física vira pacote.',
    'O-RAN.o': 'A RAN aberta: as partes do rádio conversam por interfaces padronizadas e públicas.',
    'O-RAN.p': 'Permite misturar fornecedores e plugar inteligência (o RIC) na rede de rádio.',
    'O-RAN SC.o': 'A comunidade de software da O-RAN Alliance — a implementação de referência, aberta.',
    'O-RAN SC.p': 'É de lá que vêm o A1 Mediator, o PMS e os simuladores near-RT que rodam no lab.',
    'RU.o': 'A unidade de rádio: a ponta que transmite e recebe no ar.',
    'RU.p': 'É onde o comando do RIC chega no fim — potência, PRB, escalonamento.',
    'DU.o': 'A unidade distribuída: processa as camadas baixas do rádio, perto da antena.',
    'DU.p': 'Fica entre a RU e o núcleo do gNB; no lab o gNB é monolítico e faz esse papel sozinho.',
    'RF.o': 'Rádio-frequência: o meio físico, o ar.',
    'RF.p': 'É o enlace que carrega tudo; aqui ele é imitado por software.',
    'RFSIM.o': 'O simulador de rádio do OpenAirInterface: troca a antena por um canal em software.',
    'RFSIM.p': 'Deixa rodar UE e gNB de verdade sem hardware de rádio — é a base do nosso laboratório.',
    'UERANSIM.o': 'Simulador de UE e gNB no mesmo processo — o rádio entre eles é interno.',
    'UERANSIM.p': 'Usado no Projeto 1 para exercitar o núcleo sem pilha de rádio real.',
    'PRB.o': 'O bloco de recursos: a menor fatia de espectro e tempo que o escalonador entrega.',
    'PRB.p': 'É a moeda do rádio — quantos PRBs um UE recebe define a banda que ele tem.',
    'SINR.o': 'A relação entre o sinal desejado, a interferência e o ruído.',
    'SINR.p': 'Diz a qualidade do ar; é o que decide a modulação e a taxa de dados possíveis.',
    'CQI.o': 'A nota de 0 a 15 que o celular dá para o canal.',
    'CQI.p': 'É o relatório de qualidade vindo do UE — o gNB usa para escolher a modulação.',

    'AMF.o': 'A função do núcleo que fala com o celular: registro, autenticação e mobilidade.',
    'AMF.p': 'É a porta de entrada do UE na rede — sem passar por ela, ninguém se registra.',
    'SMF.o': 'A função que gerencia as sessões de dados do assinante.',
    'SMF.p': 'Cria a sessão, dá o IP ao UE e programa o UPF pelo N4.',
    'UPF.o': 'O plano de usuário: o roteador do núcleo, por onde passa o tráfego de verdade.',
    'UPF.p': 'Encaminha os pacotes do UE para fora e de volta — sem tocar na sinalização.',
    'UPF-A.o': 'A UPF principal do Projeto 1.',
    'UPF-A.p': 'Carrega o tráfego no caminho normal; se cair, o SMF reprograma a sessão na UPF-B.',
    'UPF-B.o': 'A segunda UPF do Projeto 1, de reserva.',
    'UPF-B.p': 'Assume o tráfego no teste de failover — resiliência sem derrubar a sinalização.',
    'NRF.o': 'O catálogo do núcleo: onde toda função de rede se registra ao subir.',
    'NRF.p': 'É como o AMF acha o AUSF e o SMF acha o PCF — descoberta de serviço, por SBI.',
    'AUSF.o': 'O servidor de autenticação do 5G.',
    'AUSF.p': 'Confere se o SIM é legítimo, com os vetores que o UDM fornece.',
    'UDM.o': 'A gestão dos dados do assinante — o "HSS do 5G".',
    'UDM.p': 'Gera os vetores de autenticação e diz a que serviços aquela linha tem direito.',
    'UDR.o': 'O repositório onde os dados do assinante ficam guardados.',
    'UDR.p': 'É a camada que fala com o banco — separa o dado da lógica que o usa.',
    'NSSF.o': 'A função que escolhe a fatia de rede certa para o UE.',
    'NSSF.p': 'Resolve qual S-NSSAI atende o pedido: banda larga, IoT, baixa latência.',
    'PCF.o': 'A função de política: as regras de QoS e de cobrança da sessão.',
    'PCF.p': 'Define quanta banda e que prioridade aquela sessão recebe.',
    'BSF.o': 'A função que amarra cada sessão ao PCF que cuida dela.',
    'BSF.p': 'Guarda o vínculo: dado o IP de um UE, diz qual PCF consultar.',
    'SCP.o': 'O proxy entre as funções do núcleo — um roteador das chamadas SBI.',
    'SCP.p': 'Concentra a comunicação: as funções falam com ele em vez de falarem entre si.',
    'DN.o': 'A rede de dados do outro lado do núcleo — a "internet" do laboratório.',
    'DN.p': 'É o destino do tráfego: ping, iperf3, qualquer serviço de fora.',

    'N1.o': 'A interface lógica entre o celular e o AMF, por onde viajam as mensagens NAS.',
    'N1.p': 'Leva registro e pedido de sessão; o gNB só transporta, não lê o conteúdo.',
    'N2.o': 'A interface de controle entre o rádio e o núcleo (NGAP sobre SCTP, porta 38412).',
    'N2.p': 'É por onde o núcleo comanda o gNB e o registro do UE atravessa.',
    'N3.o': 'O túnel de dados do usuário entre o rádio e o UPF (GTP-U).',
    'N3.p': 'Carrega o tráfego real — e não passa por nenhuma função de controle.',
    'N4.o': 'A interface que o SMF usa para programar o UPF (PFCP).',
    'N4.p': 'É a linha que separa quem decide de quem encaminha — a essência do CUPS.',
    'N6.o': 'A saída do núcleo para a rede de dados externa.',
    'N6.p': 'É a porta para a internet: roteamento, NAT, serviços de fora.',
    'N11.o': 'A interface entre o AMF e o SMF, por SBI (serviço Nsmf).',
    'N11.p': 'Por ela o AMF pede a criação da sessão de dados do UE.',
    'E2.o': 'A interface O-RAN entre o near-RT RIC e o nó de rádio.',
    'E2.p': 'Sobe medidas (KPM) e desce comandos (RC) — é o laço de inteligência fechando.',
    'E42.o': 'A interface interna entre o xApp e a plataforma do near-RT RIC.',
    'E42.p': 'É como o xApp assina métricas e envia decisões sem falar direto com o gNB.',
    'A1.o': 'A interface de políticas entre o RIC lento e o RIC rápido.',
    'A1.p': 'Desce objetivos e metas — não comanda rádio, orienta quem comanda.',
    'O1.o': 'A interface de gerência dos nós O-RAN: configuração, desempenho e falhas.',
    'O1.p': 'É por onde a operação coleta telemetria e aplica configuração em massa.',

    'NAS.o': 'A camada de sinalização direta entre o celular e o núcleo, invisível ao rádio.',
    'NAS.p': 'Carrega registro, autenticação e pedido de sessão de ponta a ponta.',
    'NGAP.o': 'O protocolo de aplicação da interface N2.',
    'NGAP.p': 'Formata as mensagens entre gNB e AMF: NG Setup, contexto de UE, handover.',
    'SCTP.o': 'O transporte da sinalização 5G: vários fluxos em uma conexão, com entrega confiável.',
    'SCTP.p': 'Evita que uma mensagem presa segure a fila inteira — por isso o N2 usa ele, não TCP.',
    'GTP-U.o': 'O protocolo que encapsula os pacotes do usuário em túneis.',
    'GTP-U.p': 'Faz o tráfego do UE atravessar a rede com o endereço dele preservado.',
    'PFCP.o': 'O protocolo do N4, entre o SMF e o UPF.',
    'PFCP.p': 'Instala as regras de encaminhamento: o que fazer com cada pacote da sessão.',
    'SBI.o': 'O estilo de comunicação do núcleo 5G: APIs REST sobre HTTP/2.',
    'SBI.p': 'As funções se chamam como serviços web, e não por interfaces ponto a ponto.',
    'NG Setup.o': 'O primeiro diálogo entre gNB e AMF, quando o rádio se apresenta ao núcleo.',
    'NG Setup.p': 'É o aperto de mão que abre o N2 — sem ele o gNB não atende ninguém.',
    '5G-AKA.o': 'O procedimento de autenticação mútua entre o celular e a rede.',
    '5G-AKA.p': 'Prova que o SIM é legítimo e deriva as chaves que protegem a sessão.',
    'NAT.o': 'A tradução de endereços na saída para a rede externa.',
    'NAT.p': 'Deixa o IP interno do UE alcançar a internet do laboratório.',
    'CUPS.o': 'A separação entre quem decide (o SMF) e quem encaminha (o UPF).',
    'CUPS.p': 'Permite crescer ou trocar o plano de dados sem mexer na sinalização.',
    'PDU Session.o': 'A sessão de dados do UE: o túnel lógico do celular até a rede de dados.',
    'PDU Session.p': 'É o que dá IP ao celular — sem sessão aberta não existe tráfego.',
    'PDU.o': 'A unidade de dados de um protocolo — o "pacote" daquela camada.',
    'PDU.p': 'No 5G você a encontra na PDU Session, a sessão que transporta os pacotes do UE.',
    'slice.o': 'Uma fatia lógica da rede, com recursos e regras próprias.',
    'slice.p': 'Deixa a mesma infraestrutura servir usos diferentes sem um atrapalhar o outro.',
    'S-NSSAI.o': 'O identificador de uma fatia de rede: o SST mais o SD.',
    'S-NSSAI.p': 'É o que o UE pede e o NSSF resolve na hora de escolher a slice.',
    'SST.o': 'O tipo de serviço da fatia (banda larga, baixa latência, IoT…).',
    'SST.p': 'Diz que comportamento aquela slice deve ter.',
    'SD.o': 'O número que separa duas fatias do mesmo tipo.',
    'SD.p': 'Permite vários clientes ou vários usos com o mesmo SST.',
    'QoS.o': 'O contrato de tratamento do tráfego: banda, latência, prioridade.',
    'QoS.p': 'É o que faz uma chamada não travar quando a rede enche.',
    'IMSI.o': 'A identidade do assinante gravada no SIM.',
    'IMSI.p': 'É a chave que o núcleo procura no banco para autenticar aquela linha.',

    'RIC.o': 'O controlador que observa a rede de rádio e decide sobre ela.',
    'RIC.p': 'Tira a inteligência de dentro do equipamento: política e otimização viram software.',
    'near-RT.o': 'O RIC rápido: decide na escala de 10 ms a 1 s.',
    'near-RT.p': 'Atua no rádio durante a sessão — escalonamento, handover, alocação de PRB.',
    'Non-RT.o': 'O RIC lento: decide acima de 1 s, junto da camada de gerência.',
    'Non-RT.p': 'Treina modelos com o histórico e desce políticas pelo A1.',
    'xApp.o': 'Aplicação que roda dentro do near-RT RIC.',
    'xApp.p': 'É onde mora a lógica: lê os KPM, decide e manda o controle pela E2.',
    'rApp.o': 'Aplicação que roda no Non-RT RIC / na camada de gerência.',
    'rApp.p': 'Treina com dados históricos e guia o near-RT por políticas A1.',
    'PMS.o': 'O serviço de políticas do Non-RT RIC — a nossa implementação do A1 em ARM64.',
    'PMS.p': 'Guarda os tipos e as instâncias de política e as entrega ao near-RT.',
    'FlexRIC.o': 'O near-RT RIC que usamos no lab, do OpenAirInterface.',
    'FlexRIC.p': 'Termina a E2 vinda do gNB e hospeda os xApps que leem e atuam.',
    'KPM.o': 'O serviço E2 que entrega as medidas de desempenho do rádio.',
    'KPM.p': 'É a fonte dos dados: throughput, PRB, SINR/CQI por UE e por célula.',
    'RC.o': 'O serviço E2 que permite comandar o rádio.',
    'RC.p': 'É por ele que o xApp muda escalonamento, handover, potência ou slice.',
    'E2AP.o': 'O protocolo da interface E2.',
    'E2AP.p': 'Cria as assinaturas, entrega as indicações e transporta os comandos de controle.',
    'E2SM-KPM.o': 'O modelo de serviço que descreve QUE métricas a E2 pode reportar.',
    'E2SM-KPM.p': 'É o dicionário do que se pode medir — sem ele o RIC não sabe o que pedir.',
    'E2SM-RC.o': 'O modelo de serviço que descreve QUE controles a E2 aceita.',
    'E2SM-RC.p': 'É o dicionário do que se pode mandar — o vocabulário da atuação.',
    'A1AP.o': 'O protocolo da interface A1, uma API REST.',
    'A1AP.p': 'Cria, lê e apaga políticas no near-RT RIC.',
    'SDL.o': 'A camada de dados compartilhada do RIC (no lab, um Redis).',
    'SDL.p': 'Guarda o estado para que os componentes do RIC não percam contexto.',

    'MySQL.o': 'O banco onde o Open5GS guarda os assinantes no Projeto 2.',
    'MySQL.p': 'É o fim da linha da autenticação: o UDR lê aqui o registro daquele IMSI.',
    'MongoDB.o': 'O banco de assinantes do Open5GS no Projeto 1.',
    'MongoDB.p': 'Guarda IMSI, chaves e perfil — o que o núcleo consulta no registro.',
    'iperf3.o': 'O gerador de tráfego que mede a vazão de ponta a ponta.',
    'iperf3.p': 'É a prova numérica de que a rede entregou banda de verdade.',
  },

  // ---------------------------------------------------------------- en
  en: {
    'ui.o': 'What it is', 'ui.p': 'What it is for',

    'UE.o': 'The phone — any device that attaches to the 5G network. In the lab it is simulated in software.',
    'UE.p': 'Everything starts here: registration, data session and traffic are all born in it.',
    'gNB.o': 'The 5G base station — the "antenna" that talks to the phone over the air.',
    'gNB.p': 'Links radio to core: it signals over N2 and forwards user data over N3.',
    'RAN.o': 'The radio side of the network: everything between the phone and the core.',
    'RAN.p': 'Carries the signal from the air into the network — where physics turns into packets.',
    'O-RAN.o': 'The open RAN: the radio parts talk through standardised, public interfaces.',
    'O-RAN.p': 'Lets you mix vendors and plug intelligence (the RIC) into the radio network.',
    'O-RAN SC.o': 'The O-RAN Alliance software community — the open reference implementation.',
    'O-RAN SC.p': 'It is where the A1 Mediator, the PMS and the near-RT simulators in this lab come from.',
    'RU.o': 'The radio unit: the tip that transmits and receives over the air.',
    'RU.p': 'It is where a RIC command finally lands — power, PRB, scheduling.',
    'DU.o': 'The distributed unit: it processes the lower radio layers, close to the antenna.',
    'DU.p': 'It sits between the RU and the gNB core; in this lab the gNB is monolithic and plays that role itself.',
    'RF.o': 'Radio frequency: the physical medium, the air.',
    'RF.p': 'It is the link that carries everything; here it is imitated in software.',
    'RFSIM.o': 'The OpenAirInterface radio simulator: it swaps the antenna for a software channel.',
    'RFSIM.p': 'Lets a real UE and gNB run with no radio hardware — the foundation of our lab.',
    'UERANSIM.o': 'A UE and gNB simulator in a single process — the radio between them is internal.',
    'UERANSIM.p': 'Used in Project 1 to exercise the core without a real radio stack.',
    'PRB.o': 'The resource block: the smallest slice of spectrum and time the scheduler hands out.',
    'PRB.p': 'It is the currency of the radio — how many PRBs a UE gets is the bandwidth it has.',
    'SINR.o': 'The ratio between the wanted signal, the interference and the noise.',
    'SINR.p': 'It states the quality of the air; it drives the modulation and the achievable data rate.',
    'CQI.o': 'The 0-to-15 grade the phone gives the channel.',
    'CQI.p': 'It is the quality report coming from the UE — the gNB uses it to pick the modulation.',

    'AMF.o': 'The core function that talks to the phone: registration, authentication and mobility.',
    'AMF.p': 'It is the UE’s front door into the network — nothing registers without it.',
    'SMF.o': 'The function that manages the subscriber’s data sessions.',
    'SMF.p': 'It creates the session, gives the UE an IP and programs the UPF over N4.',
    'UPF.o': 'The user plane: the core’s router, where the real traffic actually goes.',
    'UPF.p': 'Forwards the UE’s packets out and back — without ever touching signalling.',
    'UPF-A.o': 'The primary UPF in Project 1.',
    'UPF-A.p': 'It carries traffic on the normal path; if it dies, the SMF reprograms the session onto UPF-B.',
    'UPF-B.o': 'The second, standby UPF in Project 1.',
    'UPF-B.p': 'It takes over the traffic in the failover test — resilience without dropping signalling.',
    'NRF.o': 'The core’s catalogue: where every network function registers as it boots.',
    'NRF.p': 'It is how the AMF finds the AUSF and the SMF finds the PCF — service discovery over SBI.',
    'AUSF.o': 'The 5G authentication server.',
    'AUSF.p': 'Checks that the SIM is legitimate, using the vectors the UDM provides.',
    'UDM.o': 'Subscriber data management — the "5G HSS".',
    'UDM.p': 'Generates the authentication vectors and states which services that line is entitled to.',
    'UDR.o': 'The repository where subscriber data is stored.',
    'UDR.p': 'The layer that talks to the database — it keeps the data apart from the logic using it.',
    'NSSF.o': 'The function that picks the right network slice for the UE.',
    'NSSF.p': 'Resolves which S-NSSAI serves the request: broadband, IoT, low latency.',
    'PCF.o': 'The policy function: the QoS and charging rules of the session.',
    'PCF.p': 'Decides how much bandwidth and what priority that session gets.',
    'BSF.o': 'The function that binds each session to the PCF looking after it.',
    'BSF.p': 'Keeps the binding: given a UE’s IP, it says which PCF to ask.',
    'SCP.o': 'The proxy between core functions — a router for SBI calls.',
    'SCP.p': 'Concentrates the traffic: functions call it instead of calling each other.',
    'DN.o': 'The data network on the far side of the core — the lab’s "internet".',
    'DN.p': 'It is where the traffic is headed: ping, iperf3, any outside service.',

    'N1.o': 'The logical interface between the phone and the AMF, carrying the NAS messages.',
    'N1.p': 'It carries registration and the session request; the gNB only transports, it does not read.',
    'N2.o': 'The control interface between radio and core (NGAP over SCTP, port 38412).',
    'N2.p': 'It is how the core commands the gNB, and how UE registration crosses over.',
    'N3.o': 'The user data tunnel between the radio and the UPF (GTP-U).',
    'N3.p': 'It carries the real traffic — and goes through no control function at all.',
    'N4.o': 'The interface the SMF uses to program the UPF (PFCP).',
    'N4.p': 'It is the line between who decides and who forwards — the essence of CUPS.',
    'N6.o': 'The core’s way out to the external data network.',
    'N6.p': 'It is the door to the internet: routing, NAT, outside services.',
    'N11.o': 'The interface between the AMF and the SMF, over SBI (the Nsmf service).',
    'N11.p': 'It is how the AMF asks for the UE’s data session to be created.',
    'E2.o': 'The O-RAN interface between the near-RT RIC and the radio node.',
    'E2.p': 'Measurements go up (KPM) and commands come down (RC) — the intelligence loop closing.',
    'E42.o': 'The internal interface between an xApp and the near-RT RIC platform.',
    'E42.p': 'It is how an xApp subscribes to metrics and sends decisions without talking to the gNB directly.',
    'A1.o': 'The policy interface between the slow RIC and the fast RIC.',
    'A1.p': 'It sends down goals and targets — it does not command radio, it guides whoever does.',
    'O1.o': 'The management interface of O-RAN nodes: configuration, performance and faults.',
    'O1.p': 'It is how operations collect telemetry and push configuration at scale.',

    'NAS.o': 'The signalling layer straight between the phone and the core, invisible to the radio.',
    'NAS.p': 'It carries registration, authentication and the session request end to end.',
    'NGAP.o': 'The application protocol of the N2 interface.',
    'NGAP.p': 'It shapes the messages between gNB and AMF: NG Setup, UE context, handover.',
    'SCTP.o': 'The transport of 5G signalling: many streams in one connection, with reliable delivery.',
    'SCTP.p': 'It keeps one stuck message from holding up the whole queue — which is why N2 uses it, not TCP.',
    'GTP-U.o': 'The protocol that wraps user packets into tunnels.',
    'GTP-U.p': 'It lets the UE’s traffic cross the network with its own address preserved.',
    'PFCP.o': 'The protocol of N4, between the SMF and the UPF.',
    'PFCP.p': 'It installs the forwarding rules: what to do with each packet of the session.',
    'SBI.o': 'The 5G core’s communication style: REST APIs over HTTP/2.',
    'SBI.p': 'Functions call each other like web services rather than over point-to-point interfaces.',
    'NG Setup.o': 'The first exchange between gNB and AMF, when the radio introduces itself to the core.',
    'NG Setup.p': 'It is the handshake that opens N2 — without it the gNB serves nobody.',
    '5G-AKA.o': 'The mutual authentication procedure between the phone and the network.',
    '5G-AKA.p': 'It proves the SIM is legitimate and derives the keys that protect the session.',
    'NAT.o': 'Address translation on the way out to the external network.',
    'NAT.p': 'It lets the UE’s internal IP reach the lab’s internet.',
    'CUPS.o': 'The split between who decides (the SMF) and who forwards (the UPF).',
    'CUPS.p': 'It lets you grow or swap the data plane without touching signalling.',
    'PDU Session.o': 'The UE’s data session: the logical tunnel from the phone to the data network.',
    'PDU Session.p': 'It is what gives the phone an IP — with no session open there is no traffic.',
    'PDU.o': 'A protocol’s data unit — the "packet" of that layer.',
    'PDU.p': 'In 5G you meet it in the PDU Session, the session that carries the UE’s packets.',
    'slice.o': 'A logical slice of the network, with its own resources and rules.',
    'slice.p': 'It lets one infrastructure serve different uses without them getting in each other’s way.',
    'S-NSSAI.o': 'The identifier of a network slice: the SST plus the SD.',
    'S-NSSAI.p': 'It is what the UE asks for and what the NSSF resolves when picking the slice.',
    'SST.o': 'The service type of the slice (broadband, low latency, IoT…).',
    'SST.p': 'It states how that slice is meant to behave.',
    'SD.o': 'The number that tells two slices of the same type apart.',
    'SD.p': 'It allows several customers or several uses under the same SST.',
    'QoS.o': 'The contract for how traffic is treated: bandwidth, latency, priority.',
    'QoS.p': 'It is what keeps a call from stuttering when the network fills up.',
    'IMSI.o': 'The subscriber identity written into the SIM.',
    'IMSI.p': 'It is the key the core looks up in the database to authenticate that line.',

    'RIC.o': 'The controller that watches the radio network and makes decisions about it.',
    'RIC.p': 'It takes intelligence out of the equipment: policy and optimisation become software.',
    'near-RT.o': 'The fast RIC: it decides on a 10 ms to 1 s scale.',
    'near-RT.p': 'It acts on the radio during the session — scheduling, handover, PRB allocation.',
    'Non-RT.o': 'The slow RIC: it decides above 1 s, alongside the management layer.',
    'Non-RT.p': 'It trains models on history and sends policies down over A1.',
    'xApp.o': 'An application running inside the near-RT RIC.',
    'xApp.p': 'This is where the logic lives: it reads the KPM, decides, and sends control over E2.',
    'rApp.o': 'An application running on the Non-RT RIC / management layer.',
    'rApp.p': 'It trains on historical data and steers the near-RT through A1 policies.',
    'PMS.o': 'The Non-RT RIC policy service — our own A1 implementation on ARM64.',
    'PMS.p': 'It holds the policy types and instances and delivers them to the near-RT.',
    'FlexRIC.o': 'The near-RT RIC we run in the lab, from OpenAirInterface.',
    'FlexRIC.p': 'It terminates the E2 coming from the gNB and hosts the xApps that read and act.',
    'KPM.o': 'The E2 service that delivers radio performance measurements.',
    'KPM.p': 'It is the source of the data: throughput, PRB, SINR/CQI per UE and per cell.',
    'RC.o': 'The E2 service that allows commanding the radio.',
    'RC.p': 'It is how an xApp changes scheduling, handover, power or slice.',
    'E2AP.o': 'The protocol of the E2 interface.',
    'E2AP.p': 'It creates subscriptions, delivers indications and carries the control commands.',
    'E2SM-KPM.o': 'The service model describing WHICH metrics E2 can report.',
    'E2SM-KPM.p': 'It is the dictionary of what can be measured — without it the RIC cannot ask.',
    'E2SM-RC.o': 'The service model describing WHICH controls E2 accepts.',
    'E2SM-RC.p': 'It is the dictionary of what can be commanded — the vocabulary of acting.',
    'A1AP.o': 'The protocol of the A1 interface, a REST API.',
    'A1AP.p': 'It creates, reads and deletes policies on the near-RT RIC.',
    'SDL.o': 'The RIC’s shared data layer (a Redis, in this lab).',
    'SDL.p': 'It keeps the state so the RIC components do not lose context.',

    'MySQL.o': 'The database where Open5GS keeps subscribers in Project 2.',
    'MySQL.p': 'It is the end of the authentication chain: the UDR reads that IMSI’s record here.',
    'MongoDB.o': 'The Open5GS subscriber database in Project 1.',
    'MongoDB.p': 'It holds IMSI, keys and profile — what the core looks up during registration.',
    'iperf3.o': 'The traffic generator that measures end-to-end throughput.',
    'iperf3.p': 'It is the numeric proof that the network really delivered bandwidth.',
  },

  // ---------------------------------------------------------------- es
  es: {
    'ui.o': 'Qué es', 'ui.p': 'Para qué sirve',

    'UE.o': 'El móvil — cualquier equipo que se conecta a la red 5G. En el laboratorio está simulado por software.',
    'UE.p': 'Es el principio de todo: registro, sesión de datos y tráfico nacen en él.',
    'gNB.o': 'La estación base 5G — la "antena" que habla con el móvil por el aire.',
    'gNB.p': 'Une la radio al núcleo: señaliza por N2 y reenvía los datos del usuario por N3.',
    'RAN.o': 'La parte de radio de la red: todo lo que hay entre el móvil y el núcleo.',
    'RAN.p': 'Lleva la señal del aire hasta la red — es donde la física se vuelve paquete.',
    'O-RAN.o': 'La RAN abierta: las partes de la radio se hablan por interfaces estandarizadas y públicas.',
    'O-RAN.p': 'Permite mezclar fabricantes y enchufar inteligencia (el RIC) en la red de radio.',
    'O-RAN SC.o': 'La comunidad de software de la O-RAN Alliance — la implementación de referencia, abierta.',
    'O-RAN SC.p': 'De ahí vienen el A1 Mediator, el PMS y los simuladores near-RT que corren en el laboratorio.',
    'RU.o': 'La unidad de radio: la punta que transmite y recibe por el aire.',
    'RU.p': 'Es donde llega, al final, la orden del RIC — potencia, PRB, planificación.',
    'DU.o': 'La unidad distribuida: procesa las capas bajas de la radio, cerca de la antena.',
    'DU.p': 'Está entre la RU y el núcleo del gNB; aquí el gNB es monolítico y hace ese papel solo.',
    'RF.o': 'Radiofrecuencia: el medio físico, el aire.',
    'RF.p': 'Es el enlace que lo carga todo; aquí se imita por software.',
    'RFSIM.o': 'El simulador de radio de OpenAirInterface: cambia la antena por un canal en software.',
    'RFSIM.p': 'Permite correr UE y gNB de verdad sin hardware de radio — la base de nuestro laboratorio.',
    'UERANSIM.o': 'Simulador de UE y gNB en el mismo proceso — la radio entre ellos es interna.',
    'UERANSIM.p': 'Se usa en el Proyecto 1 para ejercitar el núcleo sin pila de radio real.',
    'PRB.o': 'El bloque de recursos: la porción más pequeña de espectro y tiempo que reparte el planificador.',
    'PRB.p': 'Es la moneda de la radio — cuántos PRB recibe un UE es el ancho de banda que tiene.',
    'SINR.o': 'La relación entre la señal deseada, la interferencia y el ruido.',
    'SINR.p': 'Dice la calidad del aire; decide la modulación y la tasa de datos posible.',
    'CQI.o': 'La nota de 0 a 15 que el móvil le pone al canal.',
    'CQI.p': 'Es el informe de calidad que llega del UE — el gNB lo usa para elegir la modulación.',

    'AMF.o': 'La función del núcleo que habla con el móvil: registro, autenticación y movilidad.',
    'AMF.p': 'Es la puerta de entrada del UE a la red — sin pasar por ella nadie se registra.',
    'SMF.o': 'La función que gestiona las sesiones de datos del abonado.',
    'SMF.p': 'Crea la sesión, da la IP al UE y programa el UPF por N4.',
    'UPF.o': 'El plano de usuario: el router del núcleo, por donde pasa el tráfico de verdad.',
    'UPF.p': 'Reenvía los paquetes del UE hacia fuera y de vuelta — sin tocar la señalización.',
    'UPF-A.o': 'El UPF principal del Proyecto 1.',
    'UPF-A.p': 'Lleva el tráfico por el camino normal; si cae, el SMF reprograma la sesión en el UPF-B.',
    'UPF-B.o': 'El segundo UPF del Proyecto 1, de reserva.',
    'UPF-B.p': 'Asume el tráfico en la prueba de failover — resiliencia sin tumbar la señalización.',
    'NRF.o': 'El catálogo del núcleo: donde cada función de red se registra al arrancar.',
    'NRF.p': 'Así el AMF encuentra al AUSF y el SMF al PCF — descubrimiento de servicio, por SBI.',
    'AUSF.o': 'El servidor de autenticación del 5G.',
    'AUSF.p': 'Comprueba que la SIM es legítima, con los vectores que aporta el UDM.',
    'UDM.o': 'La gestión de los datos del abonado — el "HSS del 5G".',
    'UDM.p': 'Genera los vectores de autenticación y dice a qué servicios tiene derecho esa línea.',
    'UDR.o': 'El repositorio donde se guardan los datos del abonado.',
    'UDR.p': 'Es la capa que habla con la base de datos — separa el dato de la lógica que lo usa.',
    'NSSF.o': 'La función que elige la porción de red adecuada para el UE.',
    'NSSF.p': 'Resuelve qué S-NSSAI atiende la petición: banda ancha, IoT, baja latencia.',
    'PCF.o': 'La función de política: las reglas de QoS y de tarificación de la sesión.',
    'PCF.p': 'Define cuánto ancho de banda y qué prioridad recibe esa sesión.',
    'BSF.o': 'La función que ata cada sesión al PCF que se ocupa de ella.',
    'BSF.p': 'Guarda el vínculo: dada la IP de un UE, dice a qué PCF preguntar.',
    'SCP.o': 'El proxy entre las funciones del núcleo — un router de las llamadas SBI.',
    'SCP.p': 'Concentra la comunicación: las funciones hablan con él en vez de entre sí.',
    'DN.o': 'La red de datos al otro lado del núcleo — la "internet" del laboratorio.',
    'DN.p': 'Es el destino del tráfico: ping, iperf3, cualquier servicio de fuera.',

    'N1.o': 'La interfaz lógica entre el móvil y el AMF, por donde viajan los mensajes NAS.',
    'N1.p': 'Lleva el registro y la petición de sesión; el gNB solo transporta, no lee el contenido.',
    'N2.o': 'La interfaz de control entre la radio y el núcleo (NGAP sobre SCTP, puerto 38412).',
    'N2.p': 'Por ahí el núcleo manda en el gNB y por ahí cruza el registro del UE.',
    'N3.o': 'El túnel de datos de usuario entre la radio y el UPF (GTP-U).',
    'N3.p': 'Lleva el tráfico real — y no pasa por ninguna función de control.',
    'N4.o': 'La interfaz que el SMF usa para programar el UPF (PFCP).',
    'N4.p': 'Es la línea que separa a quien decide de quien reenvía — la esencia del CUPS.',
    'N6.o': 'La salida del núcleo hacia la red de datos externa.',
    'N6.p': 'Es la puerta a internet: enrutamiento, NAT, servicios de fuera.',
    'N11.o': 'La interfaz entre el AMF y el SMF, por SBI (servicio Nsmf).',
    'N11.p': 'Por ella el AMF pide que se cree la sesión de datos del UE.',
    'E2.o': 'La interfaz O-RAN entre el near-RT RIC y el nodo de radio.',
    'E2.p': 'Suben medidas (KPM) y bajan órdenes (RC) — el lazo de inteligencia cerrándose.',
    'E42.o': 'La interfaz interna entre el xApp y la plataforma del near-RT RIC.',
    'E42.p': 'Así el xApp se suscribe a métricas y envía decisiones sin hablar directo con el gNB.',
    'A1.o': 'La interfaz de políticas entre el RIC lento y el RIC rápido.',
    'A1.p': 'Baja objetivos y metas — no manda en la radio, orienta a quien manda.',
    'O1.o': 'La interfaz de gestión de los nodos O-RAN: configuración, rendimiento y fallos.',
    'O1.p': 'Por ahí la operación recoge telemetría y aplica configuración a escala.',

    'NAS.o': 'La capa de señalización directa entre el móvil y el núcleo, invisible para la radio.',
    'NAS.p': 'Lleva registro, autenticación y petición de sesión de extremo a extremo.',
    'NGAP.o': 'El protocolo de aplicación de la interfaz N2.',
    'NGAP.p': 'Da forma a los mensajes entre gNB y AMF: NG Setup, contexto de UE, handover.',
    'SCTP.o': 'El transporte de la señalización 5G: varios flujos en una conexión, con entrega fiable.',
    'SCTP.p': 'Evita que un mensaje atascado retenga toda la cola — por eso N2 lo usa y no TCP.',
    'GTP-U.o': 'El protocolo que encapsula los paquetes del usuario en túneles.',
    'GTP-U.p': 'Hace que el tráfico del UE cruce la red conservando su propia dirección.',
    'PFCP.o': 'El protocolo de N4, entre el SMF y el UPF.',
    'PFCP.p': 'Instala las reglas de reenvío: qué hacer con cada paquete de la sesión.',
    'SBI.o': 'El estilo de comunicación del núcleo 5G: APIs REST sobre HTTP/2.',
    'SBI.p': 'Las funciones se llaman como servicios web, y no por interfaces punto a punto.',
    'NG Setup.o': 'El primer diálogo entre gNB y AMF, cuando la radio se presenta al núcleo.',
    'NG Setup.p': 'Es el apretón de manos que abre N2 — sin él el gNB no atiende a nadie.',
    '5G-AKA.o': 'El procedimiento de autenticación mutua entre el móvil y la red.',
    '5G-AKA.p': 'Demuestra que la SIM es legítima y deriva las claves que protegen la sesión.',
    'NAT.o': 'La traducción de direcciones en la salida hacia la red externa.',
    'NAT.p': 'Permite que la IP interna del UE alcance la internet del laboratorio.',
    'CUPS.o': 'La separación entre quien decide (el SMF) y quien reenvía (el UPF).',
    'CUPS.p': 'Permite crecer o cambiar el plano de datos sin tocar la señalización.',
    'PDU Session.o': 'La sesión de datos del UE: el túnel lógico del móvil hasta la red de datos.',
    'PDU Session.p': 'Es lo que da IP al móvil — sin sesión abierta no hay tráfico.',
    'PDU.o': 'La unidad de datos de un protocolo — el "paquete" de esa capa.',
    'PDU.p': 'En 5G aparece en la PDU Session, la sesión que transporta los paquetes del UE.',
    'slice.o': 'Una porción lógica de la red, con recursos y reglas propios.',
    'slice.p': 'Deja que una misma infraestructura sirva usos distintos sin estorbarse entre sí.',
    'S-NSSAI.o': 'El identificador de una porción de red: el SST más el SD.',
    'S-NSSAI.p': 'Es lo que pide el UE y lo que el NSSF resuelve al elegir la slice.',
    'SST.o': 'El tipo de servicio de la porción (banda ancha, baja latencia, IoT…).',
    'SST.p': 'Dice cómo debe comportarse esa slice.',
    'SD.o': 'El número que distingue dos porciones del mismo tipo.',
    'SD.p': 'Permite varios clientes o varios usos con el mismo SST.',
    'QoS.o': 'El contrato de trato del tráfico: ancho de banda, latencia, prioridad.',
    'QoS.p': 'Es lo que evita que una llamada se corte cuando la red se llena.',
    'IMSI.o': 'La identidad del abonado grabada en la SIM.',
    'IMSI.p': 'Es la clave que el núcleo busca en la base de datos para autenticar esa línea.',

    'RIC.o': 'El controlador que observa la red de radio y decide sobre ella.',
    'RIC.p': 'Saca la inteligencia de dentro del equipo: política y optimización se vuelven software.',
    'near-RT.o': 'El RIC rápido: decide en la escala de 10 ms a 1 s.',
    'near-RT.p': 'Actúa sobre la radio durante la sesión — planificación, handover, asignación de PRB.',
    'Non-RT.o': 'El RIC lento: decide por encima de 1 s, junto a la capa de gestión.',
    'Non-RT.p': 'Entrena modelos con el histórico y baja políticas por A1.',
    'xApp.o': 'Aplicación que corre dentro del near-RT RIC.',
    'xApp.p': 'Ahí vive la lógica: lee los KPM, decide y manda el control por E2.',
    'rApp.o': 'Aplicación que corre en el Non-RT RIC / la capa de gestión.',
    'rApp.p': 'Entrena con datos históricos y guía al near-RT mediante políticas A1.',
    'PMS.o': 'El servicio de políticas del Non-RT RIC — nuestra implementación del A1 en ARM64.',
    'PMS.p': 'Guarda los tipos y las instancias de política y se las entrega al near-RT.',
    'FlexRIC.o': 'El near-RT RIC que usamos en el laboratorio, de OpenAirInterface.',
    'FlexRIC.p': 'Termina el E2 que llega del gNB y hospeda los xApps que leen y actúan.',
    'KPM.o': 'El servicio E2 que entrega las medidas de rendimiento de la radio.',
    'KPM.p': 'Es la fuente de los datos: throughput, PRB, SINR/CQI por UE y por celda.',
    'RC.o': 'El servicio E2 que permite mandar en la radio.',
    'RC.p': 'Por él el xApp cambia planificación, handover, potencia o slice.',
    'E2AP.o': 'El protocolo de la interfaz E2.',
    'E2AP.p': 'Crea las suscripciones, entrega las indicaciones y transporta las órdenes de control.',
    'E2SM-KPM.o': 'El modelo de servicio que describe QUÉ métricas puede reportar el E2.',
    'E2SM-KPM.p': 'Es el diccionario de lo que se puede medir — sin él el RIC no sabe qué pedir.',
    'E2SM-RC.o': 'El modelo de servicio que describe QUÉ controles acepta el E2.',
    'E2SM-RC.p': 'Es el diccionario de lo que se puede mandar — el vocabulario de la actuación.',
    'A1AP.o': 'El protocolo de la interfaz A1, una API REST.',
    'A1AP.p': 'Crea, lee y borra políticas en el near-RT RIC.',
    'SDL.o': 'La capa de datos compartida del RIC (aquí, un Redis).',
    'SDL.p': 'Guarda el estado para que los componentes del RIC no pierdan contexto.',

    'MySQL.o': 'La base donde Open5GS guarda los abonados en el Proyecto 2.',
    'MySQL.p': 'Es el final de la cadena de autenticación: el UDR lee aquí el registro de ese IMSI.',
    'MongoDB.o': 'La base de abonados de Open5GS en el Proyecto 1.',
    'MongoDB.p': 'Guarda IMSI, claves y perfil — lo que el núcleo consulta en el registro.',
    'iperf3.o': 'El generador de tráfico que mide el caudal de extremo a extremo.',
    'iperf3.p': 'Es la prueba numérica de que la red entregó ancho de banda de verdad.',
  },

  // ---------------------------------------------------------------- fr
  fr: {
    'ui.o': 'Ce que c’est', 'ui.p': 'À quoi ça sert',

    'UE.o': 'Le téléphone — tout appareil qui se connecte au réseau 5G. Ici il est simulé en logiciel.',
    'UE.p': 'Tout commence par lui : enregistrement, session de données et trafic naissent là.',
    'gNB.o': 'La station de base 5G — l’« antenne » qui parle au téléphone par les ondes.',
    'gNB.p': 'Relie la radio au cœur : elle signale via N2 et achemine les données usager via N3.',
    'RAN.o': 'La partie radio du réseau : tout ce qui se trouve entre le téléphone et le cœur.',
    'RAN.p': 'Porte le signal de l’air jusqu’au réseau — c’est là que la physique devient paquet.',
    'O-RAN.o': 'Le RAN ouvert : les éléments radio dialoguent par des interfaces normalisées et publiques.',
    'O-RAN.p': 'Permet de mélanger les fournisseurs et de brancher de l’intelligence (le RIC) dans la radio.',
    'O-RAN SC.o': 'La communauté logicielle de l’O-RAN Alliance — l’implémentation de référence, ouverte.',
    'O-RAN SC.p': 'C’est de là que viennent l’A1 Mediator, le PMS et les simulateurs near-RT du labo.',
    'RU.o': 'L’unité radio : la pointe qui émet et reçoit dans l’air.',
    'RU.p': 'C’est là qu’aboutit la commande du RIC — puissance, PRB, ordonnancement.',
    'DU.o': 'L’unité distribuée : elle traite les couches basses de la radio, près de l’antenne.',
    'DU.p': 'Elle est entre la RU et le cœur du gNB ; ici le gNB est monolithique et tient ce rôle seul.',
    'RF.o': 'Radiofréquence : le milieu physique, l’air.',
    'RF.p': 'C’est le lien qui porte tout ; ici il est imité en logiciel.',
    'RFSIM.o': 'Le simulateur radio d’OpenAirInterface : il remplace l’antenne par un canal logiciel.',
    'RFSIM.p': 'Il permet de faire tourner un vrai UE et un vrai gNB sans matériel radio — la base du labo.',
    'UERANSIM.o': 'Simulateur d’UE et de gNB dans un même processus — la radio entre eux est interne.',
    'UERANSIM.p': 'Utilisé dans le Projet 1 pour éprouver le cœur sans pile radio réelle.',
    'PRB.o': 'Le bloc de ressources : la plus petite tranche de spectre et de temps distribuée par l’ordonnanceur.',
    'PRB.p': 'C’est la monnaie de la radio — le nombre de PRB d’un UE, c’est son débit.',
    'SINR.o': 'Le rapport entre le signal utile, l’interférence et le bruit.',
    'SINR.p': 'Il dit la qualité de l’air ; il décide de la modulation et du débit atteignable.',
    'CQI.o': 'La note de 0 à 15 que le téléphone donne au canal.',
    'CQI.p': 'C’est le rapport de qualité venu de l’UE — le gNB s’en sert pour choisir la modulation.',

    'AMF.o': 'La fonction du cœur qui parle au téléphone : enregistrement, authentification et mobilité.',
    'AMF.p': 'C’est la porte d’entrée de l’UE dans le réseau — sans elle, personne ne s’enregistre.',
    'SMF.o': 'La fonction qui gère les sessions de données de l’abonné.',
    'SMF.p': 'Elle crée la session, donne l’IP à l’UE et programme l’UPF via N4.',
    'UPF.o': 'Le plan usager : le routeur du cœur, par où passe le vrai trafic.',
    'UPF.p': 'Il achemine les paquets de l’UE vers l’extérieur et retour — sans toucher à la signalisation.',
    'UPF-A.o': 'L’UPF principal du Projet 1.',
    'UPF-A.p': 'Il porte le trafic sur le chemin normal ; s’il tombe, le SMF bascule la session sur l’UPF-B.',
    'UPF-B.o': 'Le second UPF du Projet 1, en réserve.',
    'UPF-B.p': 'Il reprend le trafic lors du test de bascule — résilience sans couper la signalisation.',
    'NRF.o': 'Le catalogue du cœur : là où chaque fonction réseau s’enregistre au démarrage.',
    'NRF.p': 'C’est ainsi que l’AMF trouve l’AUSF et le SMF le PCF — découverte de service, via SBI.',
    'AUSF.o': 'Le serveur d’authentification de la 5G.',
    'AUSF.p': 'Il vérifie que la SIM est légitime, avec les vecteurs fournis par l’UDM.',
    'UDM.o': 'La gestion des données d’abonné — le « HSS de la 5G ».',
    'UDM.p': 'Il produit les vecteurs d’authentification et dit à quels services la ligne a droit.',
    'UDR.o': 'Le référentiel où sont conservées les données d’abonné.',
    'UDR.p': 'C’est la couche qui parle à la base — elle sépare la donnée de la logique qui l’utilise.',
    'NSSF.o': 'La fonction qui choisit la tranche de réseau adaptée à l’UE.',
    'NSSF.p': 'Elle résout quel S-NSSAI sert la demande : haut débit, IoT, faible latence.',
    'PCF.o': 'La fonction de politique : les règles de QoS et de facturation de la session.',
    'PCF.p': 'Elle fixe le débit et la priorité que reçoit cette session.',
    'BSF.o': 'La fonction qui rattache chaque session au PCF qui s’en occupe.',
    'BSF.p': 'Elle garde le lien : à partir de l’IP d’un UE, elle dit quel PCF interroger.',
    'SCP.o': 'Le proxy entre les fonctions du cœur — un routeur des appels SBI.',
    'SCP.p': 'Il concentre la communication : les fonctions lui parlent au lieu de se parler entre elles.',
    'DN.o': 'Le réseau de données de l’autre côté du cœur — l’« internet » du laboratoire.',
    'DN.p': 'C’est la destination du trafic : ping, iperf3, tout service extérieur.',

    'N1.o': 'L’interface logique entre le téléphone et l’AMF, où circulent les messages NAS.',
    'N1.p': 'Elle porte l’enregistrement et la demande de session ; le gNB ne fait que transporter.',
    'N2.o': 'L’interface de contrôle entre la radio et le cœur (NGAP sur SCTP, port 38412).',
    'N2.p': 'C’est par là que le cœur commande le gNB et que l’enregistrement de l’UE transite.',
    'N3.o': 'Le tunnel de données usager entre la radio et l’UPF (GTP-U).',
    'N3.p': 'Il porte le vrai trafic — et ne traverse aucune fonction de contrôle.',
    'N4.o': 'L’interface que le SMF utilise pour programmer l’UPF (PFCP).',
    'N4.p': 'C’est la ligne entre celui qui décide et celui qui achemine — l’essence du CUPS.',
    'N6.o': 'La sortie du cœur vers le réseau de données externe.',
    'N6.p': 'C’est la porte vers internet : routage, NAT, services extérieurs.',
    'N11.o': 'L’interface entre l’AMF et le SMF, via SBI (service Nsmf).',
    'N11.p': 'C’est par elle que l’AMF demande la création de la session de données de l’UE.',
    'E2.o': 'L’interface O-RAN entre le near-RT RIC et le nœud radio.',
    'E2.p': 'Les mesures montent (KPM), les commandes descendent (RC) — la boucle d’intelligence.',
    'E42.o': 'L’interface interne entre le xApp et la plateforme du near-RT RIC.',
    'E42.p': 'C’est ainsi que le xApp s’abonne aux métriques et envoie ses décisions sans parler au gNB.',
    'A1.o': 'L’interface de politiques entre le RIC lent et le RIC rapide.',
    'A1.p': 'Elle descend des objectifs — elle ne commande pas la radio, elle oriente qui la commande.',
    'O1.o': 'L’interface de gestion des nœuds O-RAN : configuration, performance et pannes.',
    'O1.p': 'C’est par là que l’exploitation collecte la télémétrie et applique la configuration.',

    'NAS.o': 'La couche de signalisation directe entre le téléphone et le cœur, invisible à la radio.',
    'NAS.p': 'Elle porte l’enregistrement, l’authentification et la demande de session de bout en bout.',
    'NGAP.o': 'Le protocole applicatif de l’interface N2.',
    'NGAP.p': 'Il met en forme les messages entre gNB et AMF : NG Setup, contexte d’UE, handover.',
    'SCTP.o': 'Le transport de la signalisation 5G : plusieurs flux dans une connexion, en livraison fiable.',
    'SCTP.p': 'Il évite qu’un message bloqué retienne toute la file — d’où son usage sur N2 plutôt que TCP.',
    'GTP-U.o': 'Le protocole qui encapsule les paquets usager dans des tunnels.',
    'GTP-U.p': 'Il fait traverser le réseau au trafic de l’UE en préservant son adresse.',
    'PFCP.o': 'Le protocole de N4, entre le SMF et l’UPF.',
    'PFCP.p': 'Il installe les règles d’acheminement : que faire de chaque paquet de la session.',
    'SBI.o': 'Le style de communication du cœur 5G : des API REST sur HTTP/2.',
    'SBI.p': 'Les fonctions s’appellent comme des services web, et non par interfaces point à point.',
    'NG Setup.o': 'Le premier échange entre gNB et AMF, quand la radio se présente au cœur.',
    'NG Setup.p': 'C’est la poignée de main qui ouvre N2 — sans elle le gNB ne sert personne.',
    '5G-AKA.o': 'La procédure d’authentification mutuelle entre le téléphone et le réseau.',
    '5G-AKA.p': 'Elle prouve que la SIM est légitime et dérive les clés qui protègent la session.',
    'NAT.o': 'La traduction d’adresses à la sortie vers le réseau externe.',
    'NAT.p': 'Elle permet à l’IP interne de l’UE d’atteindre l’internet du laboratoire.',
    'CUPS.o': 'La séparation entre celui qui décide (le SMF) et celui qui achemine (l’UPF).',
    'CUPS.p': 'Elle permet d’étendre ou de remplacer le plan de données sans toucher à la signalisation.',
    'PDU Session.o': 'La session de données de l’UE : le tunnel logique du téléphone au réseau de données.',
    'PDU Session.p': 'C’est elle qui donne une IP au téléphone — sans session ouverte, pas de trafic.',
    'PDU.o': 'L’unité de données d’un protocole — le « paquet » de cette couche.',
    'PDU.p': 'En 5G on la rencontre dans la PDU Session, la session qui porte les paquets de l’UE.',
    'slice.o': 'Une tranche logique du réseau, avec ses propres ressources et ses propres règles.',
    'slice.p': 'Elle laisse une même infrastructure servir des usages différents sans se gêner.',
    'S-NSSAI.o': 'L’identifiant d’une tranche de réseau : le SST plus le SD.',
    'S-NSSAI.p': 'C’est ce que l’UE demande et ce que le NSSF résout pour choisir la slice.',
    'SST.o': 'Le type de service de la tranche (haut débit, faible latence, IoT…).',
    'SST.p': 'Il dit comment cette slice doit se comporter.',
    'SD.o': 'Le numéro qui distingue deux tranches de même type.',
    'SD.p': 'Il permet plusieurs clients ou plusieurs usages sous un même SST.',
    'QoS.o': 'Le contrat de traitement du trafic : débit, latence, priorité.',
    'QoS.p': 'C’est ce qui empêche un appel de hacher quand le réseau se remplit.',
    'IMSI.o': 'L’identité d’abonné inscrite dans la SIM.',
    'IMSI.p': 'C’est la clé que le cœur cherche en base pour authentifier cette ligne.',

    'RIC.o': 'Le contrôleur qui observe le réseau radio et décide à son sujet.',
    'RIC.p': 'Il sort l’intelligence de l’équipement : politique et optimisation deviennent du logiciel.',
    'near-RT.o': 'Le RIC rapide : il décide à l’échelle de 10 ms à 1 s.',
    'near-RT.p': 'Il agit sur la radio pendant la session — ordonnancement, handover, allocation de PRB.',
    'Non-RT.o': 'Le RIC lent : il décide au-delà d’une seconde, aux côtés de la couche de gestion.',
    'Non-RT.p': 'Il entraîne des modèles sur l’historique et descend des politiques via A1.',
    'xApp.o': 'Application qui tourne à l’intérieur du near-RT RIC.',
    'xApp.p': 'C’est là que vit la logique : elle lit les KPM, décide et envoie le contrôle via E2.',
    'rApp.o': 'Application qui tourne sur le Non-RT RIC / la couche de gestion.',
    'rApp.p': 'Elle s’entraîne sur des données historiques et guide le near-RT par des politiques A1.',
    'PMS.o': 'Le service de politiques du Non-RT RIC — notre implémentation de l’A1 en ARM64.',
    'PMS.p': 'Il conserve les types et les instances de politique et les remet au near-RT.',
    'FlexRIC.o': 'Le near-RT RIC utilisé au laboratoire, issu d’OpenAirInterface.',
    'FlexRIC.p': 'Il termine l’E2 venue du gNB et héberge les xApps qui lisent et agissent.',
    'KPM.o': 'Le service E2 qui livre les mesures de performance de la radio.',
    'KPM.p': 'C’est la source des données : débit, PRB, SINR/CQI par UE et par cellule.',
    'RC.o': 'Le service E2 qui permet de commander la radio.',
    'RC.p': 'C’est par lui que le xApp change l’ordonnancement, le handover, la puissance ou la slice.',
    'E2AP.o': 'Le protocole de l’interface E2.',
    'E2AP.p': 'Il crée les abonnements, livre les indications et transporte les commandes de contrôle.',
    'E2SM-KPM.o': 'Le modèle de service qui décrit QUELLES métriques l’E2 peut remonter.',
    'E2SM-KPM.p': 'C’est le dictionnaire du mesurable — sans lui le RIC ne sait pas quoi demander.',
    'E2SM-RC.o': 'Le modèle de service qui décrit QUELS contrôles l’E2 accepte.',
    'E2SM-RC.p': 'C’est le dictionnaire du commandable — le vocabulaire de l’action.',
    'A1AP.o': 'Le protocole de l’interface A1, une API REST.',
    'A1AP.p': 'Il crée, lit et supprime les politiques sur le near-RT RIC.',
    'SDL.o': 'La couche de données partagée du RIC (ici, un Redis).',
    'SDL.p': 'Elle garde l’état pour que les composants du RIC ne perdent pas le contexte.',

    'MySQL.o': 'La base où Open5GS conserve les abonnés dans le Projet 2.',
    'MySQL.p': 'C’est le bout de la chaîne d’authentification : l’UDR y lit la fiche de cet IMSI.',
    'MongoDB.o': 'La base d’abonnés d’Open5GS dans le Projet 1.',
    'MongoDB.p': 'Elle garde IMSI, clés et profil — ce que le cœur consulte à l’enregistrement.',
    'iperf3.o': 'Le générateur de trafic qui mesure le débit de bout en bout.',
    'iperf3.p': 'C’est la preuve chiffrée que le réseau a bien livré du débit.',
  },
};

  // --- 3. O casador -------------------------------------------------------
  // Alternativa mais LONGA primeiro, senão "UPF" comeria o "UPF-A" (o hífen é
  // fronteira de palavra, então \bUPF\b casa dentro de "UPF-A"). O `s?` final
  // aceita o plural que os textos usam: "os KPMs", "os xApps", "as slices".
  var ESC = function (s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); };
  var CHAVES = Object.keys(TERMOS).sort(function (a, b) { return b.length - a.length; });
  var RE = new RegExp('\\b(?:' + CHAVES.map(ESC).join('|') + ')s?\\b', 'g');

  var LANGS = ['pt', 'en', 'es', 'fr'];
  function idioma() {
    try { if (window.I18N && DICTS[window.I18N.lang]) return window.I18N.lang; } catch (e) { /* página sem i18n */ }
    return 'pt';
  }
  // Mesma cadeia do i18n.js do painel: <lang> → en → pt → vazio.
  function tr(chave) {
    var ordem = [idioma(), 'en', 'pt'];
    for (var i = 0; i < ordem.length; i++) {
      var v = DICTS[ordem[i]] && DICTS[ordem[i]][chave];
      if (v) return v;
    }
    return '';
  }

  // --- 4. Marcar o texto que já está na tela ------------------------------
  // Aceita um elemento, uma LISTA deles, ou `{el, expandir:false}` para marcar
  // sem escrever o nome por extenso — é o caso de um título, que precisa ficar
  // curto (o balão continua lá).
  // A lista importa: título e legenda do mesmo passo compartilham o "uma vez
  // só", senão o nome por extenso sairia duas vezes na mesma tela.
  function marcar(raizes) {
    var lista = Array.isArray(raizes) ? raizes : [raizes];
    var expandidos = {};
    for (var r = 0; r < lista.length; r++) {
      var item = lista[r];
      var raiz = item && item.el !== undefined ? item.el : item;
      var expandir = !(item && item.expandir === false);
      if (!raiz || !raiz.ownerDocument) continue;
      estilo(); liga();
      var doc = raiz.ownerDocument, nos = [];
      var w = doc.createTreeWalker(raiz, NodeFilter.SHOW_TEXT, {
        acceptNode: function (n) {
          // o que já foi marcado (e o conteúdo dos chips) não se mexe de novo
          return n.parentElement && n.parentElement.closest('.glos-termo, .glos-exp, .chip')
            ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
        },
      });
      while (w.nextNode()) nos.push(w.currentNode);
      for (var i = 0; i < nos.length; i++) troca(nos[i], expandir ? expandidos : null);
    }
  }

  // Há parêntese aberto antes desta posição? (o autor da legenda já estava
  // dentro de um aparte quando o termo apareceu)
  function aberto(txt, ate) {
    var d = 0;
    for (var i = 0; i < ate; i++) {
      var c = txt.charAt(i);
      if (c === '(') d++;
      else if (c === ')' && d > 0) d--;
    }
    return d > 0;
  }

  // `expandidos` nulo = só marcar (sem o nome por extenso).
  function troca(no, expandidos) {
    var txt = no.nodeValue;
    RE.lastIndex = 0;
    if (!RE.test(txt)) return;
    RE.lastIndex = 0;
    var doc = no.ownerDocument, frag = doc.createDocumentFragment(), fim = 0, m;
    while ((m = RE.exec(txt)) !== null) {
      var bruto = m[0];
      var termo = Object.prototype.hasOwnProperty.call(TERMOS, bruto) ? bruto : bruto.replace(/s$/, '');
      frag.appendChild(doc.createTextNode(txt.slice(fim, m.index)));
      var span = doc.createElement('span');
      span.className = 'glos-termo';
      span.setAttribute('data-termo', termo);
      span.tabIndex = 0;
      span.textContent = bruto;
      frag.appendChild(span);
      fim = m.index + bruto.length;

      var exp = TERMOS[termo], depois = txt.slice(fim);
      // Termo sozinho dentro de parênteses — "(RFSIM)" — recebe o nome por
      // extenso DENTRO deles, com travessão: "(RFSIM — RF simulator)".
      var sozinho = txt.charAt(m.index - 1) === '(' && depois.charAt(0) === ')';
      // Duas recusas, e a razão das duas é a mesma: nunca escrever parêntese
      // dentro de parêntese, nem dois parênteses colados.
      //   já dentro de um  → "N1 (UE↔AMF (Access and Mobility…))"
      //   um logo depois   → "E2 (near-RT RIC ↔ gNB) (KPM)"
      // Nesses casos fica só o balão — que o termo continua tendo.
      var cabe = sozinho || (!aberto(txt, m.index) && !/^\s*\(/.test(depois));
      if (expandidos && exp && !expandidos[termo] && cabe) {
        expandidos[termo] = true;
        var e = doc.createElement('span');
        e.className = 'glos-exp';
        e.textContent = sozinho ? ' — ' + exp : ' (' + exp + ')';
        frag.appendChild(e);
      }
    }
    frag.appendChild(doc.createTextNode(txt.slice(fim)));
    no.parentNode.replaceChild(frag, no);
  }

  // --- 5. O balão ---------------------------------------------------------
  var tip = null, alvo = null, ligado = false, estilado = false;

  function estilo() {
    if (estilado || typeof document === 'undefined') return;
    estilado = true;
    if (document.getElementById('c5g-glossario-css')) return;
    var st = document.createElement('style');
    st.id = 'c5g-glossario-css';
    st.textContent = [
      // O termo fica um degrau MAIS forte que a legenda em volta e o nome por
      // extenso um degrau mais fraco: a hierarquia sozinha diz o que é o quê.
      '.glos-termo{color:var(--ink);text-decoration:underline dotted var(--accent);',
      'text-decoration-thickness:1px;text-underline-offset:3px;cursor:help}',
      '.glos-termo:hover,.glos-termo:focus-visible{color:var(--accent-text);text-decoration-style:solid}',
      '.glos-exp{color:var(--ink-2)}',
      '#glos-tip{position:fixed;z-index:9999;max-width:min(320px,92vw);background:var(--surface);',
      'color:var(--ink);border:1px solid var(--line);border-radius:var(--r-md);padding:10px 12px;',
      'font-family:var(--fonte-texto);font-size:var(--t-mini);line-height:1.5;box-shadow:var(--elev-2);',
      'pointer-events:none}',
      '#glos-tip[hidden]{display:none}',
      '#glos-tip .gt-h{display:flex;flex-wrap:wrap;gap:2px 8px;align-items:baseline;',
      'margin-bottom:7px;padding-bottom:7px;border-bottom:1px solid var(--line)}',
      '#glos-tip .gt-h b{font-size:var(--t-corpo)}',
      '#glos-tip .gt-h span{color:var(--ink-2)}',
      '#glos-tip .gt-l{margin-top:5px}',
      '#glos-tip .gt-l i{display:block;font-style:normal;font-size:var(--t-micro);font-weight:600;',
      'letter-spacing:var(--tr-etiqueta);text-transform:uppercase;color:var(--ink-2)}',
    ].join('');
    (document.head || document.documentElement).appendChild(st);
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function balao() {
    if (tip && tip.isConnected) return tip;
    tip = document.createElement('div');
    tip.id = 'glos-tip';
    tip.setAttribute('role', 'tooltip');
    tip.hidden = true;
    document.body.appendChild(tip);
    return tip;
  }

  function linha(rotulo, texto) {
    return texto ? '<div class="gt-l"><i>' + esc(rotulo) + '</i>' + esc(texto) + '</div>' : '';
  }

  function mostra(el) {
    var t = el.getAttribute('data-termo');
    if (!t || !Object.prototype.hasOwnProperty.call(TERMOS, t)) return;
    var b = balao();
    b.innerHTML = '<div class="gt-h"><b>' + esc(t) + '</b>'
      + (TERMOS[t] ? '<span>' + esc(TERMOS[t]) + '</span>' : '') + '</div>'
      + linha(tr('ui.o'), tr(t + '.o')) + linha(tr('ui.p'), tr(t + '.p'));
    b.hidden = false;
    posiciona(el, b);
    el.setAttribute('aria-describedby', 'glos-tip');
    alvo = el;
  }

  function esconde() {
    if (alvo) alvo.removeAttribute('aria-describedby');
    alvo = null;
    if (tip) tip.hidden = true;
  }

  function posiciona(el, b) {
    b.style.left = '0px'; b.style.top = '0px';   // mede sem herdar a posição anterior
    var r = el.getBoundingClientRect(), c = b.getBoundingClientRect(), m = 8;
    var x = Math.max(m, Math.min(r.left + r.width / 2 - c.width / 2, window.innerWidth - c.width - m));
    var y = r.top - c.height - 10;
    if (y < m) y = r.bottom + 10;                // não coube em cima: desce
    b.style.left = Math.round(x) + 'px';
    b.style.top = Math.round(y) + 'px';
  }

  var alcance = function (n) {
    return n && n.closest ? n.closest('.glos-termo') : null;
  };

  function liga() {
    if (ligado || typeof document === 'undefined') return;
    ligado = true;
    document.addEventListener('mouseover', function (e) {
      var el = alcance(e.target); if (el && el !== alvo) mostra(el);
    });
    document.addEventListener('mouseout', function (e) {
      if (alcance(e.target) === alvo && alvo) esconde();
    });
    document.addEventListener('focusin', function (e) {
      var el = alcance(e.target); if (el) mostra(el);
    });
    document.addEventListener('focusout', function (e) {
      if (alcance(e.target)) esconde();
    });
    // Toque não tem hover: o toque abre, o toque fora fecha.
    document.addEventListener('click', function (e) {
      var el = alcance(e.target);
      if (!el) { esconde(); return; }
      if (el === alvo) esconde(); else mostra(el);
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') esconde(); });
    window.addEventListener('scroll', esconde, true);
    window.addEventListener('resize', esconde);
  }

  window.GLOSSARIO = {
    termos: TERMOS,
    dicts: DICTS,
    langs: LANGS,
    marcar: marcar,
    esconde: esconde,
    // usado pelos testes: o que o balão diria daquele termo, sem tocar no DOM
    explica: function (t) { return { exp: TERMOS[t], o: tr(t + '.o'), p: tr(t + '.p') }; },
  };
  window.Glossario = window.GLOSSARIO;
})();
