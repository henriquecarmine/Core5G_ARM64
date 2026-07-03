# Glossário de tradução — termos que **não** se traduzem

> Regra de ouro (CONTRIBUTING §7.2): **traduz-se a explicação, nunca o termo.**
> Os termos 3GPP/O-RAN e os nomes de software/protocolo abaixo ficam **idênticos
> em pt/en/es/fr** — como aparecem nos specs. Tudo o mais (prosa, títulos,
> células de tabela, legendas) é traduzido normalmente.
>
> This list is language-agnostic: the terms below stay verbatim in every
> language. Only the surrounding prose is translated.

Vale para o **painel** (`server/panel/static/i18n.js`) e para a **documentação**
(`docs/i18n/<lang>/`). Um tradutor — humano ou agente — deve manter este arquivo
aberto.

---

## 1. Nunca traduzir (fica idêntico nos 4 idiomas)

**Núcleo 5G — funções de rede (NFs)**
`AMF` · `SMF` · `UPF` · `NRF` · `AUSF` · `UDM` · `UDR` · `PCF` · `NSSF` · `BSF` · `SCP`

**Interfaces e pontos de referência**
`N1` · `N2` · `N3` · `N4` · `N6` · `N11` · `Nsmf` · `Nausf` · `Nudm` · `Nudr` · `Npcf` · `SBI`

**Protocolos**
`NAS` · `NGAP` · `GTP-U` · `PFCP` · `SCTP` · `HTTP/2` · `5G-AKA`

**Conceitos de rede**
`CUPS` · `PDU Session` · `slice` · `S-NSSAI` · `SST` · `SD` · `DNN` · `QoS` · `PRB` · `SINR` · `RSRP` · `Path Loss`

**RAN / O-RAN / RIC**
`gNB` · `UE` · `nrUE` · `RAN` · `O-RAN` · `near-RT RIC` · `Non-RT RIC` · `SMO` ·
`xApp` · `rApp` · `E2` · `E2AP` · `E2SM-KPM` · `E2SM-RC` · `E42` · `A1` · `O1` ·
`RFSIM` · `Service Model` · `KPM` · `RC`

**Stack / software / ferramentas**
`Open5GS` · `UERANSIM` · `OAI` · `FlexRIC` · `Docker` · `Docker Compose` ·
`MongoDB` · `MySQL` · `WebUI` · `Caddy` · `FastAPI` · `systemd` · `iperf3` ·
`tcpdump` · `Wireshark` · `arm64` · `Graviton` · `GCP` · `SSH` · `VM`

**Também intocável (não é glossário, é conteúdo literal):** blocos de código
(fenced e inline), saída de comandos, caminhos de arquivo/diretório, nomes de
variáveis de ambiente, nomes de container/serviço, URLs, IMSI, chaves (K/OPc),
IPs, portas e números. Comentários `#` **dentro** de blocos de código e rótulos
de diagramas ASCII ficam como estão (mexer neles é mexer no código).

---

## 2. Rótulos recorrentes (traduza sempre igual)

Para consistência entre os roteiros de laboratório:

| pt | en | es | fr |
|----|----|----|----|
| Objetivos | Objectives | Objetivos | Objectifs |
| Duração (indicativa) | (Indicative) duration | Duración (indicativa) | Durée (indicative) |
| Pré-requisitos | Prerequisites | Requisitos previos | Prérequis |
| Evidência | Evidence | Evidencia | Preuve |
| Entregáveis / O que entregar | Deliverables | Entregables | Livrables |
| Roteiro | Guide | Guía | Guide |
| Checklist | Checklist | Lista de verificación | Checklist |
| Assinante | Subscriber | Suscriptor | Abonné |
| Rede | Network | Red | Réseau |
| Resumo | Summary | Resumen | Résumé |
| O que fez | What it did | Qué hizo | Ce qui a été fait |
| Resultado | Result | Resultado | Résultat |

> Os três últimos (`Resumo` / `O que fez` / `Resultado`) também vivem em
> `server/scripts/lib/testlog.sh` (via `LAB_LANG`) — mantenha idênticos aqui e lá.

---

## 3. Verificação

- **Painel**: `cd server/panel/test && npm run test:i18n` — falha se faltar chave,
  sobrar órfã ou divergirem placeholders nos 4 dicionários.
- **Documentação**: `python3 docs/i18n/check-parity.py` — acusa órfãos e traduções
  defasadas (marcador `<!-- sync: <hash> -->` vs. histórico git do canônico).
- Ambos rodam no CI (`.github/workflows/i18n.yml`) a cada push/PR.
