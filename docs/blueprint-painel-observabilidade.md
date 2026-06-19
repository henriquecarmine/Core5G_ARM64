# Blueprint — Painel Explicativo / Observabilidade em Tempo Real

Status: **proposta, nada implementado ainda**. Objetivo deste documento é registrar o
desenho antes de qualquer execução no servidor ARM AWS.

## Contexto

Hoje temos dois stacks docker rodando NFs 5G + RAN + RIC:

- `docker-compose.yml` (raiz) — Open5GS (Projeto 1): `nrf`, `scp`, `amf`, `smf`, `ausf`,
  `udm`, `udr`, `pcf`, `nssf`, `upf-a`, `upf-b`, `dn`, `webui`, `mongodb`, mais
  `ueransim/` (gNB + UE simulados).
- `oai-cn-gnb-e2/` (Projeto 2) — OAI 5GC (`oai-cn5g-fed`) + gNB OAI em RFSIM com
  **agente E2** embutido + **FlexRIC** (near-RT RIC) + xApps (`xapp_kpm_moni`,
  `xapp_kpm_rc`).

O problema: dá pra ver que os containers "estão de pé", mas não dá pra entender *o
que cada serviço está fazendo* sem ler logs crus espalhados em vários containers.
Quer um painel que torne isso visível em tempo real, com filtro de log, para quem
ainda não tem intuição sobre o papel de cada NF.

## Mapeamento NF → interface 3GPP/O-RAN (referência rápida)

| Serviço | Interface principal | Papel |
|---|---|---|
| `amf` | N1 (NAS, via gNB) / N2 (NGAP) | mobilidade, registro do UE |
| `smf` | N4 (PFCP, com UPF) / N11 (com AMF) | gestão de sessão PDU |
| `upf-a`/`upf-b` | N3 (GTP-U) / N6 (DN) | plano de dados |
| `ausf`/`udm`/`udr` | SBI interno | autenticação e perfil do assinante |
| `pcf`/`nssf` | SBI interno | política de QoS e seleção de slice |
| `nrf`/`scp` | SBI interno | descoberta de serviço e proxy entre NFs |
| gNB OAI (E2 agent) | E2AP (KPM, RC, SMs custom L2/L3) | expõe métricas/controle pro RIC |
| FlexRIC | E2AP | near-RT RIC — roteia SUBSCRIPTION/INDICATION/CONTROL |
| xApps | E2AP (consumidor) | lógica "inteligente" sobre as métricas/eventos |

Importante: cada rede docker do `docker-compose.yml` (`net-n2`, `net-n3`, `net-n4`,
`net-n6`, `net-sbi`) já corresponde 1:1 a uma interface 3GPP real — isso é uma
vantagem pedagógica grande para o painel (filtrar por rede = filtrar por interface).

## Dois níveis de observabilidade

### Nível 1 — Infra (logs + métricas de container)

Resolve "o serviço está vivo, e o que ele andou dizendo".

- **Logs**: `Promtail` (ou `Vector`) lendo `docker logs` (driver `json-file`) + os
  arquivos de log já existentes (`logs/`, `oai-cn-gnb-e2/logs/`) → `Loki` →
  consulta/filtro via `Grafana` (Explore).
- **Métricas**: `cAdvisor` + `node-exporter` → `Prometheus` — CPU/mem/rede por
  container, dashboards prontos no Grafana.
- Por que Loki em vez de stack ELK: o host ARM já vai estar ocupado com 5G core +
  RAN + RIC; Loki é uma fração do consumo de memória do Elasticsearch.

### Nível 2 — Fluxo de protocolo (o diferencial pedagógico)

Resolve "o que está cruzando essa interface agora, em português".

1. **Sensor de protocolo**: serviço Python (`pyshark`/`scapy`) escutando as redes
   docker relevantes (`net-n2`, `net-n3`, `net-n4`, a porta E2 `36421`) e decodificando
   NGAP / GTP-U / E2AP em eventos JSON estruturados, ex.:
   `{"interface": "N2", "msg": "InitialUEMessage", "ts": ...}`.
2. **Barramento de eventos**: publica esses eventos em algo leve — `Mosquitto`
   (MQTT) ou `Redis` pub/sub. Evitar Kafka aqui (peso desnecessário pro caso de uso).
3. **Front-end interativo**: app leve (Next.js ou SPA simples) que:
   - desenha a topologia real como diagrama vivo (UE → gNB → AMF/SMF → UPF → DN,
     RIC ↔ gNB via E2);
   - assina o barramento via WebSocket e "acende"/pulsa o nó ou aresta certa quando
     um evento cruza aquela interface;
   - mostra um tooltip/painel lateral com a mensagem decodificada + uma explicação
     em linguagem simples ("AMF acabou de autenticar o UE via N2");
   - embute o Grafana/Loki para busca de log mais avançada (por container,
     severidade, texto livre), em vez de reinventar busca de log.

## Fases sugeridas

| Fase | Entrega | Por quê primeiro/depois |
|---|---|---|
| 0 | Este blueprint | alinhamento antes de tocar no servidor |
| 1 | Loki + Promtail + Grafana | vitória rápida, valida imagens arm64 no servidor |
| 2 | Prometheus + cAdvisor + node-exporter | saúde/recursos por container |
| 3 | Sensor de protocolo (pyshark → MQTT) | camada que dá o "tempo real" de fato |
| 4 | Painel de topologia interativo (consome o barramento) | o "wow" pedagógico pedido |
| 5 (esticado) | Plugar ciclo A1 completo (Non-RT → A1 → Near-RT → E2 → RAN) no painel | quando o curso chegar nessa parte (rApps, políticas) |

## Considerações para o servidor ARM AWS

- Usar imagens **arm64 nativas** (Grafana, Loki, Prometheus, Mosquitto/Redis,
  cAdvisor todas têm build oficial multi-arch) — evitar qualquer imagem que force
  emulação QEMU, que destrói performance em Graviton.
- Orçamento de recursos: o stack de observabilidade deve ser deployado como um
  `docker-compose` **separado** dos labs (Projeto 1 / Projeto 2), para poder subir/
  derrubar independentemente e ser reaproveitado entre os dois.
- Retenção curta (24–48h) em Loki/Prometheus — isso é ferramenta de ensino/demo, não
  produção; não vale gastar disco do servidor com retenção longa.

## Decisões abertas (para quando formos implementar)

- Tipo exato da instância EC2 ARM (vCPU/RAM) — define quanto "Nível 2" cabe junto
  com os labs já rodando.
- Se o front-end customizado (Fase 4) vale a pena versus usar um painel Grafana
  customizado (menos trabalho, menos "wow" visual de topologia).
- Se o sensor de protocolo decodifica E2AP/NGAP "na mão" ou se existe alguma lib
  Python com dissector pronto (a confirmar) que evite reescrever isso do zero.

## Não-objetivos (por agora)

- Nenhum código, container ou script novo neste momento — este documento é só o
  desenho. Implementação entra em discussão separada quando o usuário pedir.
