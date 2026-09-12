# 04 — Gestão, Orquestração e Automação em Redes OpenRAN (Borges)

**Prof. Lucas Borges de Oliveira** · OpenRAN Especialização 2025.2 · início em
08/09/2026 (18:30).

## Slides do professor

| Arquivo | Aula | Páginas |
|---|---|---|
| [`aula00-revisao.pdf`](aula00-revisao.pdf) | Aula 0 — Revisão | 64 |
| [`aula01-smo.pdf`](aula01-smo.pdf) | Aula 1 — SMO | 67 |

Nomes no padrão das outras cadeiras (`aulaNN-assunto.pdf`); no Classroom, os
arquivos se chamam "Aula 0 - Revisão.pdf" e "Aula 1 - SMO.pdf".

## Avaliação — 1ª parte (30%): plataformas de SMO

Anunciada no Classroom em 10/09/2026.

- **Grupo:** até 5 pessoas.
- **Objetivo:** investigar e analisar uma ferramenta ou framework de SMO
  (Service Management and Orchestration) para redes Open RAN.
- **Objeto de estudo:**
  1. arquitetura;
  2. serviços e funções de SMO disponibilizados;
  3. componentes O-RAN suportados;
  4. implementação das interfaces O1 e O2;
  5. mecanismos de gerenciamento, provisionamento e orquestração;
  6. capacidades de gerenciamento do O-Cloud;
  7. suporte ao ciclo de vida de Network Functions;
  8. mecanismos de monitoramento, telemetria e gerenciamento de falhas.
- **Entregáveis:**
  - apresentação oral de 20 min em **12/09 (sábado)**;
  - relatório até **15/09**.
- Os grupos e a ferramenta escolhida são registrados nos comentários do aviso,
  no Classroom.

## Laboratório

O SMO do O-RAN SC (OAM) roda no servidor ARM64: [`server/smo/`](../../server/smo/README.md)
(`build_arm64.sh`, `up_smo.sh`, `test_smo.sh`).

A apresentação usa **um teste real do painel por item da avaliação**, na cadeira
5 do rail — roteiro de 20 minutos, falas e perguntas prováveis em
[`docs/apresentacao-smo.md`](../../docs/apresentacao-smo.md):

| Item | Teste no painel | Script |
|---|---|---|
| 1–3 Arquitetura, serviços, componentes | Arquitetura do SMO | `smo_arquitetura.sh` |
| 4–5 O1, gerenciamento | O1: ler a configuração da O-DU | `smo_o1_leitura.sh` |
| 5 Provisionamento | O1: provisionar e desfazer | `smo_o1_provisionamento.sh` |
| 8 Falhas | Falhas: alarme VES até o Kafka | `smo_falhas.sh` |
| 8 Telemetria | Telemetria: medidas 3GPP da O-DU | `smo_telemetria.sh` |
| 7 Ciclo de vida de NFs | Ciclo de vida de uma função de rede | `smo_ciclo_vida.sh` |
| 4 e 6 O2, O-Cloud | O-Cloud e O2 | `smo_ocloud.sh` |

## Material que já existe no repositório

- [`../01-ric/aula05-design_smo.pdf`](../01-ric/aula05-design_smo.pdf) — a aula
  de SMO do curso de RIC (Kunzler, 18/06): pilha OAI+OSC e as fases do lab.
- `external/cesar-school-repo/data/code/oai-cn-gnb-nonrt-nearrt/docs/FASE3_*.md`
  — a Fase 3 do lab do professor: SMO/OAM, O1 com simuladores, topologia.
