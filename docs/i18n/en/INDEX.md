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

## READMEs

The four root READMEs: [README.en.md](../../../README.en.md).

---

The canonical Portuguese lives at [`docs/labs/`](../../labs/) and
[`server/oai-cn-gnb-e2/docs/`](../../../server/oai-cn-gnb-e2/docs/). Helping
translate more of the corpus (bible, guides)? See CONTRIBUTING (§7, i18n).
