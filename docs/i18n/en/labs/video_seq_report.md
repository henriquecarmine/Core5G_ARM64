<!-- sync: e8f9da69 -->
> 🌐 **English** translation of the canonical Portuguese doc [`docs/labs/video_seq_report.md`](../../../labs/video_seq_report.md). All languages: [INDEX](../INDEX.md) · sync checked by `docs/i18n/check-parity.py`.

# Video series — running the Open5GS + UERANSIM lab

This page gathers the support videos for the lab. There are **two formats**:


| Format                              | Target audience                                                                                                                     | Content                                                                                                   |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **Short series (1–3)** below        | Those setting up the environment on **GCP** in stages                                                                              | VM, Docker, condensed E2E bring-up.                                                                      |
| **Single video — local lab**        | Those running on **local Linux** (or a ready-made VM) who want to see **everything at once**, including **Wireshark** and **network tools** | Equivalent to the written lab guides **01 → 02 → 03** (core, UERANSIM/captures, wrap-up for the report). |


The `.md` files remain the reference for exact commands, evidence and rubric; the videos show the flow in practice.

---

## How to use this sequence

1. **GCP track:** watch episodes **1 → 2 → 3** in order (each stage assumes the previous one).
2. **Full local track:** use the [full video](#video-lab-completo-local) as an integrated view; go back to lab guides 01–03 to copy commands and assemble attachments.
3. Have the repository cloned and the lab guides open in another tab.
4. Pause and run the same commands in your terminal (if possible) — the goal is not just to “watch”, but to **replicate** and record evidence for the [submission report](03-relatorio-entrega-avaliacao.md).

---

## Episodes


| #     | Topic                            | What you should be able to do by the end                                                                                                        | Related written lab guide                                                                                                    |
| ----- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **1** | **VM on GCP**                    | Create/access a VM suitable for the lab (SSH, resources, a sense of the firewall).                                                              | [Pre-lab — GCP, SSH and bridge to the code](00-pre-lab-gcp-vm-e-acesso.md)                                                   |
| **2** | **Docker on the VM**             | Install Docker and Docker Compose v2; `docker run hello-world` (or equivalent) working.                                                         | [Docker installation — Ubuntu](00-docker-instalacao-ubuntu.md)                                                              |
| **3** | **End-to-end 5G system**         | Bring up core + RAN, a subscriber consistent with the UE, health checks and a sense of N2/N3/E2E.                                               | [Lab Guide 01 — Core](01-core-open5gs.md) · [Lab Guide 02 — UERANSIM / E2E](02-ueransim-n2-n3-e2e.md)                        |
| **★** | **Full lab (local)**             | Go through **lab guides 01 to 03** in one session; **tcpdump** / **Wireshark** (N2/N3); `ping` / routes / `docker`; wrap-up aligned with the report. | [01](01-core-open5gs.md) · [02](02-ueransim-n2-n3-e2e.md) · [03 — Report and evidence](03-relatorio-entrega-avaliacao.md) |


### 1) VM on GCP (`setup_vm_gcp`)

**Video:** [youtu.be/67Xey5GV1G4](https://youtu.be/67Xey5GV1G4)

Ideal for those who do not yet have the lab machine. Pay attention to the **zone**, the **VM size** (CPU/RAM/disk) and **how to open the terminal** (in-browser SSH vs `gcloud`), aligned with the pre-lab.

---

### 2) Docker installation (`installing_docker_gcp`)

**Video:** [youtu.be/76TMQdSAXSw](https://youtu.be/76TMQdSAXSw)

Focuses on the VM's Ubuntu environment. Confirm in your terminal:

```bash
docker --version
docker compose version
```

If something fails here, fix it **before** bringing up Open5GS.

---

### 3) End-to-end 5G system (`running_5G_system_e2e`)

**Video:** [youtu.be/dgGzGDYYE_c](https://youtu.be/dgGzGDYYE_c)

Covers the full flow (core, subscriber, UERANSIM, checks). While watching, compare with:

- the **core → subscriber → RAN** order in lab guides 01 and 02;
- the need for the **IMSI in MongoDB** to match the `supi` in `ueransim/configs/ue.yaml`;
- scripts `core/scripts/up_core.sh`, `core/scripts/add-subscriber.sh` (or equivalent), `ueransim/scripts/up_ran.sh` and `core/scripts/healthcheck.sh`.

---

### ★) Full lab — local (`full_lab_local_wireshark`)

**Video:** [youtu.be/ic3_CIllb9o](https://youtu.be/ic3_CIllb9o)

Same content described in the [detailed section below](#video-lab-completo-local); use it as the single reference if you prefer one recorded session (local Linux or a VM already with Docker).

---



## Full video — local run (lab guides 01 to 03, Wireshark and networking)

A **single** recording in a **local** environment (a Linux machine or a VM with Docker already usable), covering the same content as the written lab guides **from start to the wrap-up for submission**, with emphasis on **protocol visibility** and **networking commands**.

**Video:** [Full lab — lab guides 01 to 03 (Wireshark and networking)](https://youtu.be/ic3_CIllb9o)

### What the video covers (quick map)


| Phase                    | Written lab guide                                                     | Typical topics in the video                                                                                                                                                                                                                                            |
| ------------------------ | -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **01 — Core**            | [01-core-open5gs.md](01-core-open5gs.md)                             | Optional cleanup, `up_core`, MongoDB / subscriber aligned with `ue.yaml`, WebUI, `healthcheck.sh`, basic connectivity between containers.                                                                                                                                |
| **02 — UERANSIM and networking** | [02-ueransim-n2-n3-e2e.md](02-ueransim-n2-n3-e2e.md)         | `up_ran`, `ueransim` logs, **capture on the host** with `tcpdump` (e.g., SCTP **38412** for N2, UDP **2152** for GTP-U / N3), opening the PCAPs in **Wireshark** with filters `sctp.port == 38412` and `udp.port == 2152`, tests with `ping` / routes when the lab guide calls for it. |
| **03 — Report**          | [03-relatorio-entrega-avaliacao.md](03-relatorio-entrega-avaliacao.md) | How to relate *screenshots*, logs and PCAPs to evidence items **E1–E11**; suggested PDF structure; what counts as the minimum attachment.                                                                                                                              |


### Tools that commonly appear

- **Docker / Compose** — bringing up the core and the RAN, `docker ps`, `docker logs`, `docker exec` (e.g., `ip addr`, `ping` from the UE/container).
- **tcpdump** on the *host* — interfaces `docker0`, `br-`* or `any`, per [lab guide 02](02-ueransim-n2-n3-e2e.md) (NGAP over SCTP, GTP-U).
- **Wireshark** — NGAP dissection on N2 and GTP-U on N3; *screenshots* with a **visible filter** for the report ([criteria in lab guide 03](03-relatorio-entrega-avaliacao.md)).
- **Repository scripts** — `healthcheck.sh`, `test-system-status.sh`, `test_ue_connection.sh` (when applicable to your clone).

### Difference from episodes 1–3 (GCP)

The **1–3** series above focuses on **creating the VM on GCP** and installing Docker. The **full local video** assumes the OS and Docker are already fine and goes deeper into **lab guides 01–03**, **captures** and **submission** — useful for those working on their own laptop or who already have a provisioned VM.

---

## Mini checklist (after the series)

Mentally check off (or in the report) what is already valid in **your** environment:

- GCP VM reachable via SSH and with enough resources for Docker + several images.
- `docker` and `docker compose` working without errors.
- Open5GS core running and NFs healthy (per lab guide 01 / `healthcheck.sh`).
- Subscriber registered and **aligned** with `ue.yaml`.
- UERANSIM running, NG setup and, when applicable, the `uesimtun0` interface / data IP per lab guide 02.
- *(If you followed the full local video)* PCAP or Wireshark *screenshot* with N2 and/or N3 aligned with [lab guide 02](02-ueransim-n2-n3-e2e.md) and the rubric of [lab guide 03](03-relatorio-entrega-avaliacao.md).

---

**General labs index:** [INDICE.md](INDICE.md).
