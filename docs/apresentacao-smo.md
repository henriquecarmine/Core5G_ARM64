# Apresentação — Plataformas de SMO (12/09/2026)

Cadeira **Gestão, Orquestração e Automação em Redes OpenRAN** · Prof. Lucas
Borges de Oliveira · 1ª parte da avaliação (30%) · **20 minutos, 3 vozes**.

A ferramenta estudada é o **SMO do O-RAN SC** (repositório `o-ran-sc/oam`),
rodando **de verdade** no nosso servidor ARM64. Cada item da avaliação é
respondido com um **teste real do painel**, na cadeira 5 do rail
("Gestão, Orquestração e Automação (SMO)"). O que aparece na tela é medido na
hora, não é slide.

> **A cola com os nomes** (o que cada um lê e o que aperta no painel) é gerada
> fora do repositório — os nomes não entram no git:
> `python3 pdfs/04-gestao-orquestracao/cola_apresentacao.py --integrantes "Voz 1,Voz 2,Voz 3"`
> → `pdfs/04-gestao-orquestracao/entrega/` (gitignored) e Área de trabalho.

---

## Antes de entrar — a ordem de partida

1. **Instância no ar** (console da AWS) e `https://core5g-arm64.duckdns.org` respondendo.
2. **Desligar o E2 lab do Projeto 2** (botão "E2 lab" na barra de serviços). O
   gNB e o UE simulados comem cerca de 3 dos 4 núcleos; com eles no ar o
   controlador do SMO chegou a não responder em 25 s. O SMO sozinho usa cerca
   de 5 GB de RAM e pouca CPU.
3. **Ligar o SMO** no botão **SMO** da barra de serviços (Projeto 2). Se já
   estiver verde, pular. Subir do zero leva uns 5 minutos.
4. **Reiniciar a O-DU simulada** se a telemetria acusar arquivo velho (a geração
   de medidas do simulador já travou uma vez): `docker restart pynts-o-du-o1`
   no servidor e esperar 1 minuto.
5. **Ctrl+Shift+R** no painel (a versão mudou).
6. Ensaiar **Arquitetura do SMO** e **Telemetria**, conferir os vereditos e **limpar**.

---

## O roteiro — 20 minutos, 3 vozes

Cada voz fica com blocos seguidos, para ninguém trocar de computador no meio.

| Tempo | Voz | Item da avaliação | Teste no painel | O que mostrar |
|---|---|---|---|---|
| 0:00–1:30 | 1 | abertura | Topologia → Tour até a Camada 8 | a banda SMO e a rede gerenciada por O1 |
| 1:30–5:00 | 1 | 1 Arquitetura · 2 Serviços · 3 Componentes | **Arquitetura do SMO** | 3 camadas, 15 contêineres arm64, 8 serviços no gateway, O-DU e O-RU conectados |
| 5:00–8:00 | 2 | 4 Interface O1 · 5 Gerenciamento | **O1: ler a configuração da O-DU** | 154 modelos YANG, gNB-DU e célula NR lidas pela O1 |
| 8:00–10:00 | 2 | 5 Provisionamento | **O1: provisionar e desfazer** | PATCH aceito, valor dentro do equipamento, desfeito |
| 10:00–12:00 | 2 | 7 Ciclo de vida de NFs | **Ciclo de vida de uma função de rede** | O-RU encerrado, SMO percebe em ~1 s, call home em ~10 s |
| 12:00–14:30 | 3 | 8 Falhas | **Falhas: alarme VES até o Kafka** | alarme linkDown CRITICAL no Kafka em ~1 s, e a limpeza |
| 14:30–16:30 | 3 | 8 Monitoramento e telemetria | **Telemetria: medidas 3GPP da O-DU** | arquivo TS 28.532, FileReady, heartbeats |
| 16:30–18:30 | 3 | 4 O2 · 6 O-Cloud | **O-Cloud e O2** | inventário do O-Cloud e a lacuna do O2 |
| 18:30–20:00 | 1 | conclusão | — | o que o SMO do O-RAN SC entrega e o que falta |

Em cada teste: botão no rail → **▶ Iniciar teste** (pré-voo) → a **faixa de
execução** acende (cada etapa abre um cartão ao clique) → ler o **Resumo** e a
caixa **"O que acabou de acontecer"** → **limpar**. O botão **mapa** do console
mostra onde, na topologia, aquilo está acontecendo, já com zoom.

---

## O que dizer em cada bloco

### Abertura (voz 1)

- SMO = Service Management and Orchestration: a camada que opera a rede O-RAN
  inteira — configura, mede, recebe falhas, gerencia o ciclo de vida.
- Escolhemos o **SMO do O-RAN SC** porque é a implementação de referência da
  O-RAN Alliance e porque já tínhamos o Non-RT RIC do O-RAN SC no lab.
- **Rodando em ARM64 nativo**: 7 imagens só existiam em x86 e foram construídas
  por nós (troca de base ou compilação).

### 1–3 · Arquitetura, serviços, componentes (voz 1)

- **common**: Traefik (entrada), Keycloak (identidade), MariaDB, Kafka, topologia.
- **oam**: controlador SDN-R (OpenDaylight, O1), ODLUX (console), coletor VES.
- **network**: O-DU e O-RU simulados (pynts) — os elementos gerenciados.
- Componentes O-RAN suportados: **O1** com a O-DU, **M-plane** do Open
  Fronthaul com o O-RU (híbrido direto; hierárquico via O-DU), **VES**.
- Fora do OAM: **A1** (é do Non-RT RIC) e **O2** (é do projeto INF).

### 4–5 · O1 e gerenciamento (voz 2)

- O1 = NETCONF/YANG. O controlador expõe **RESTCONF** (HTTP/JSON) e fala
  NETCONF com o elemento.
- A O-DU anuncia **154 modelos YANG** (49 O-RAN, 30 3GPP).
- Lemos a árvore 3GPP **ManagedElement → GNBDUFunction → NRCellDU**.

### 5 · Provisionamento (voz 2)

- Escrita = RESTCONF **PATCH** → NETCONF **edit-config**.
- A prova é o valor **dentro do datastore da O-DU**, não a tela do SMO.
- Aplicar, verificar e **desfazer**.

### 7 · Ciclo de vida (voz 2)

- Encerrar → o controlador percebe a perda (≈1 s) → instanciar → o elemento liga
  para o SMO (**call home**) e é montado de novo (≈10 s), sem configuração manual.
- O banco do controlador guarda: Unmounted → Mounted → Connected.
- Quem encerra e instancia aqui é o Docker; num O-RAN completo seria o O-Cloud
  pelo **O2 (DMS)**.

### 8 · Falhas (voz 3)

- Caminho: elemento → **VES** (HTTPS) → coletor → tópico `SEC_FAULT_OUTPUT` no
  **Kafka** → consumidores. Alarme **linkDown CRITICAL** e a **limpeza (NORMAL)**.
- Honesto: a O-DU simulada não gera alarmes sozinha; o teste faz o papel dela,
  com o formato VES 7.2.1.

### 8 · Telemetria (voz 3)

- A O-DU grava a cada 60 s um arquivo **3GPP TS 28.532** e avisa por VES
  **FileReady** — o SMO não precisa varrer os elementos.
- Heartbeats ("estou vivo") e pnfRegistration ("cheguei").

### 4 e 6 · O2 e O-Cloud (voz 3)

- **O OAM do O-RAN SC não implementa O2.** No O-RAN SC, O2 (IMS e DMS) é do
  projeto **INF**, sobre StarlingX.
- O teste mostra o que um O2 IMS exporia do nosso O-Cloud: recursos (ARM64
  Neoverse, 4 vCPU, 15 GB), runtime e o consumo de cada função (~5 GB).

### Conclusão (voz 1)

- Entrega forte em **O1, M-plane, VES/falhas, telemetria e identidade**.
- **Não entrega O2/O-Cloud** nem integra sozinho com o Non-RT RIC (A1).
- Achados de engenharia (em `server/smo/README.md`), nenhum de ARM64: JDK 11
  atual e ZIP64, Traefik antigo × Docker 29, script de realm sem `USER`.

---

## Perguntas prováveis

- **Por que simuladores e não o gNB?** O gNB monolítico do OAI não tem agente O1.
- **Onde está o O2?** No projeto INF do O-RAN SC (IMS/DMS). Não faz parte do OAM.
- **Híbrido × hierárquico?** No híbrido o SMO gerencia o O-RU direto pelo
  M-plane; no hierárquico só a O-DU fala com o O-RU.
- **NETCONF × RESTCONF?** O mesmo modelo YANG; NETCONF sobre SSH/TLS com XML,
  RESTCONF sobre HTTP com JSON.
- **Quanto custa rodar?** ~5 GB de RAM para SMO + simuladores (teste O-Cloud).

## Plano B

- Se um teste falhar ao vivo: o **Resumo** do console diz o motivo; mostrar o
  **Histórico** (resultados salvos) da execução anterior.
- Se o servidor cair: as saídas completas estão em `server/smo/logs/` no
  servidor e os prints em `server/panel/test/screenshots/`.
