# 04 — Gestão, Orquestração e Automação em Redes OpenRAN (Borges)

**Prof. Lucas Borges de Oliveira** · OpenRAN Especialização 2025.2 · início em
08/09/2026 (18:30).

Slides na raiz desta pasta, com os nomes dados pelo professor.

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
(`build_arm64.sh`, `up_smo.sh`, `test_smo.sh`). O `test_smo.sh` gera as evidências
de cada item do objeto de estudo que o lab cobre: O1/NETCONF, VES, Keycloak,
topologia e Kafka.

## Material que já existe no repositório

- [`../01-ric/aula05-design_smo.pdf`](../01-ric/aula05-design_smo.pdf) — a aula
  de SMO do curso de RIC (Kunzler, 18/06): pilha OAI+OSC e as fases do lab.
- `external/cesar-school-repo/data/code/oai-cn-gnb-nonrt-nearrt/docs/FASE3_*.md`
  — a Fase 3 do lab do professor: SMO/OAM, O1 com simuladores, topologia.
