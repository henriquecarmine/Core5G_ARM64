<!-- sync: e8f9da69 -->
> 🌐 **English** translation of the canonical Portuguese doc [`docs/labs/INDICE.md`](../../../labs/INDICE.md). All languages: [INDEX](../INDEX.md) · sync checked by `docs/i18n/check-parity.py`.

# Labs — Open5GS + UERANSIM (Interfaces and Protocols)

Guides for classroom or self-paced execution and for producing the **submission report**.

| Document | Content |
|-----------|----------|
| [**Lab videos**](video_seq_report.md) | GCP series (3 episodes) and **full local video** — [walkthrough 01–03 + Wireshark](https://youtu.be/ic3_CIllb9o) |
| [00 — Pre-lab GCP, SSH and VM](00-pre-lab-gcp-vm-e-acesso.md) | Create VM, access, firewall / WebUI (cloud track) |
| [00 — Docker installation (Ubuntu)](00-docker-instalacao-ubuntu.md) | Docker Engine and Docker Compose v2 on the VM |
| [01 — Infrastructure and 5GC Core (Open5GS)](01-core-open5gs.md) | Docker, bringing up the core, subscriber, WebUI, initial checks |
| [02 — UERANSIM: N2/N3 and E2E test](02-ueransim-n2-n3-e2e.md) | gNB + UE in a container, NGAP, GTP-U, tests and N3/N6 captures |
| [03 — Report, submission and assessment](03-relatorio-entrega-avaliacao.md) | What to submit, mandatory evidence, rubric |
| [OAI Core arm64 — Manual build](../../../../server/oai-cn-gnb-e2/docs/OAI-CORE-ARM64.md) | Build OAI images for arm64: prerequisites, step by step, 5 resolved bugs |
| [OAI Core v2.2.1 — user plane arm64](../../../../server/oai-cn-gnb-e2/oai-cn5g-v2/README.md) | Real user plane on arm64 (`oai-upf` simple_switch): bring up, validate, rollback |
| [Bible §7.c — user plane v2.2.1 + event-driven xApps](../../../../core5g-arm64-bible.md) | Bring up core v2 + RIC + gNB, run deterministic xApps, 2 vCPU constraint |

**Prerequisites:** Linux with Docker and Docker Compose v2, a user with permission to run `docker` (and possibly `sudo` for `sysctl` when starting the core and for `tcpdump` on the *host*, if you do advanced captures).

**Project root (convention used in commands):** `open5gs-containerized/` — adjust the `cd` commands if your clone is in a different path (e.g. `code/open5gs-containerized`).

**Technical reference:** [README.md](../../../../README.md), [core/docs/CORE.md](../../../../core/docs/CORE.md), [ueransim/docs/RAN.md](../../../../ueransim/docs/RAN.md).
