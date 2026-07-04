# Documentação — pt (canônica)

🌐 **pt (canônico)** · [en](../en/INDEX.md) · [es](../es/INDEX.md) · [fr](../fr/INDEX.md)

> O português é o **idioma canônico** do projeto: os arquivos moram no lugar de
> origem (`docs/labs/` e `server/oai-cn-gnb-e2/docs/`) e **não** são duplicados
> aqui. Esta página é apenas um **letreiro** — as traduções em
> `docs/i18n/{en,es,fr}/` espelham estes canônicos, e o
> `docs/i18n/check-parity.py` garante que não fiquem defasadas (o `pt` fica de
> fora da checagem de propósito: é a fonte da verdade).

## Laboratórios e exercícios

**Projeto 1 — Open5GS + UERANSIM**

| Guia | Conteúdo |
|------|----------|
| [Índice](../../labs/INDICE.md) | Mapa dos roteiros |
| [00 — Instalação Docker (Ubuntu)](../../labs/00-docker-instalacao-ubuntu.md) | Docker Engine + Compose v2 na VM |
| [00 — Pré-lab: GCP, SSH e VM](../../labs/00-pre-lab-gcp-vm-e-acesso.md) | Trilha em nuvem: VM, acesso, firewall/WebUI |
| [01 — Core 5GC (Open5GS)](../../labs/01-core-open5gs.md) | Subir o core, assinante, WebUI, verificações |
| [02 — UERANSIM: N2/N3 e E2E](../../labs/02-ueransim-n2-n3-e2e.md) | gNB + UE, NGAP, GTP-U, testes, capturas N3/N6 |
| [03 — Relatório, entrega e avaliação](../../labs/03-relatorio-entrega-avaliacao.md) | Entregáveis, evidências obrigatórias, rubrica |
| [Vídeos do laboratório](../../labs/video_seq_report.md) | Índice de vídeos (série GCP + walkthrough) |

**Projeto 2 — OAI 5GC + gNB + FlexRIC**

| Guia | Conteúdo |
|------|----------|
| [Tutorial do lab E2](../../../server/oai-cn-gnb-e2/docs/TUTORIAL_LAB_E2.md) | Core OAI + near-RT RIC + gNB (E2) + xApps, fim a fim |

## Corpo técnico

Documentação de referência (canônica em pt) — internos do 5GC, pilha E2/RIC e operação.

| Doc | Conteúdo |
|-----|----------|
| [Bíblia do projeto](../../../core5g-arm64-bible.md) | Documento-mãe: arquitetura, decisões, ciladas, roadmap |
| [E2 / FlexRIC](../../../server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md) | near-RT RIC, E2AP, Service Models, codificação |
| [E2 Service Models](../../../server/oai-cn-gnb-e2/docs/E2_SERVICE_MODELS.md) | KPM / RC e os demais SMs |
| [Analytics KPM](../../../server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md) | Pipeline KPM → CSV → KPI |
| [Coleta KPM resiliente](../../../server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md) | Captura KPM por evento, sem congelar |
| [Build do OAI Core arm64](../../../server/oai-cn-gnb-e2/docs/OAI-CORE-ARM64.md) | Compilar as imagens OAI para arm64 (5 bugs) |
| [Instalação do gNB OAI](../../../server/oai-cn-gnb-e2/docs/INSTALACAO_GNB_OAI.md) | Subida do gNB RFSIM |
| [P2 CPU e user plane](../../../server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md) | Limites de 2 vCPU, user plane, upgrade p/ 4 vCPU |
| [RAN (UERANSIM)](../../../server/ueransim/docs/RAN.md) | A RAN simulada |

## READMEs

README canônico da raiz: [README.md](../../../README.md).

---

Traduções: [en](../en/INDEX.md) · [es](../es/INDEX.md) · [fr](../fr/INDEX.md).
Termos que não se traduzem: [GLOSSARY.md](../GLOSSARY.md).
