# Translated documentation — en

🌐 [pt](../pt/INDEX.md) · **en** · [es](../es/INDEX.md) · [fr](../fr/INDEX.md)

> Mirror of the canonical Portuguese docs. A file here mirrors `<repo-root>/<path>`
> or `<repo-root>/docs/<path>`. Every translation carries a `<!-- sync: <hash> -->`
> marker at the top, checked by `docs/i18n/check-parity.py` (which flags orphans
> and translations that fell behind the canonical git history).

## Labs & exercises

Full English translation of the lab guides. The 3GPP/O-RAN glossary (AMF, CUPS,
E2SM-KPM, N1/N2/N3…) is kept as in the specs — only the surrounding explanation
is translated. Code, commands, file paths and URLs are unchanged.

**Project 1 — Open5GS + UERANSIM**

| Guide | Content |
|-------|---------|
| [Index](labs/INDICE.md) | Map of the lab guides |
| [00 — Docker install (Ubuntu)](labs/00-docker-instalacao-ubuntu.md) | Docker Engine + Compose v2 on the VM |
| [00 — Pre-lab: GCP, SSH & VM](labs/00-pre-lab-gcp-vm-e-acesso.md) | Cloud track: VM, access, firewall/WebUI |
| [01 — Core 5GC (Open5GS)](labs/01-core-open5gs.md) | Bring up the core, subscriber, WebUI, first checks |
| [02 — UERANSIM: N2/N3 & E2E](labs/02-ueransim-n2-n3-e2e.md) | gNB + UE, NGAP, GTP-U, tests, N3/N6 captures |
| [03 — Report, delivery & assessment](labs/03-relatorio-entrega-avaliacao.md) | Deliverables, mandatory evidence, rubric |
| [Lab videos](labs/video_seq_report.md) | Video index (the videos are narrated in Portuguese) |

**Project 2 — OAI 5GC + gNB + FlexRIC**

| Guide | Content |
|-------|---------|
| [E2 lab tutorial](server/oai-cn-gnb-e2/docs/TUTORIAL_LAB_E2.md) | OAI core + near-RT RIC + gNB (E2) + xApps, end to end |

## Technical corpus

The reference documentation — 5GC internals, the E2/RIC stack, and operations.

| Doc | Content |
|-----|---------|
| [Project bible](core5g-arm64-bible.md) | Master document: architecture, decisions, pitfalls, roadmap |
| [E2 / FlexRIC](server/oai-cn-gnb-e2/docs/E2_FLEXRIC.md) | near-RT RIC, E2AP, Service Models, encoding |
| [E2 Service Models](server/oai-cn-gnb-e2/docs/E2_SERVICE_MODELS.md) | KPM / RC and the other SMs |
| [KPM analytics](server/oai-cn-gnb-e2/docs/KPM-ANALYTICS.md) | KPM → CSV → KPI pipeline |
| [Resilient KPM collection](server/oai-cn-gnb-e2/docs/KPM-COLETA-RESILIENTE.md) | Event-driven, non-freezing KPM capture |
| [OAI Core arm64 build](server/oai-cn-gnb-e2/docs/OAI-CORE-ARM64.md) | Building the OAI images for arm64 (5 bugs solved) |
| [OAI gNB install](server/oai-cn-gnb-e2/docs/INSTALACAO_GNB_OAI.md) | gNB RFSIM setup |
| [P2 CPU & user plane](server/oai-cn-gnb-e2/docs/PROJETO2-CPU-E-USERPLANE.md) | 2-vCPU limits, user plane, 4-vCPU upgrade |
| [RAN (UERANSIM)](server/ueransim/docs/RAN.md) | The simulated RAN |

## READMEs

The four root READMEs: [README.en.md](../../../README.en.md).

---

The canonical Portuguese lives at [`docs/labs/`](../../labs/) and
[`server/oai-cn-gnb-e2/docs/`](../../../server/oai-cn-gnb-e2/docs/). Helping
translate more of the corpus (bible, guides)? See CONTRIBUTING (§7, i18n).
