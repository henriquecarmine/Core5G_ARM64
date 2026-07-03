<!-- sync: e8f9da69 -->
> 🌐 Traducción al **español** del documento canónico en portugués [`docs/labs/INDICE.md`](../../../labs/INDICE.md). Todos los idiomas: [INDEX](../INDEX.md) · sincronización verificada por `docs/i18n/check-parity.py`.

# Laboratorios — Open5GS + UERANSIM (Interfaces y Protocolos)

Guías para ejecución en aula o de forma autónoma y para elaboración del **informe de entrega**.

| Documento | Contenido |
|-----------|----------|
| [**Videos del laboratorio**](video_seq_report.md) | Serie GCP (3 episodios) y **video completo local** — [walkthrough 01–03 + Wireshark](https://youtu.be/ic3_CIllb9o) |
| [00 — Pre-lab GCP, SSH y VM](00-pre-lab-gcp-vm-e-acesso.md) | Crear VM, acceso, firewall / WebUI (ruta en la nube) |
| [00 — Instalación Docker (Ubuntu)](00-docker-instalacao-ubuntu.md) | Docker Engine y Docker Compose v2 en la VM |
| [01 — Infraestructura y Core 5GC (Open5GS)](01-core-open5gs.md) | Docker, arranque del core, suscriptor, WebUI, verificaciones iniciales |
| [02 — UERANSIM: N2/N3 y prueba E2E](02-ueransim-n2-n3-e2e.md) | gNB + UE en contenedor, NGAP, GTP-U, pruebas y capturas N3/N6 |
| [03 — Informe, entrega y evaluación](03-relatorio-entrega-avaliacao.md) | Qué entregar, evidencias obligatorias, rúbrica |
| [OAI Core arm64 — Build manual](../../../../server/oai-cn-gnb-e2/docs/OAI-CORE-ARM64.md) | Compilar imágenes OAI para arm64: requisitos previos, paso a paso, 5 bugs resueltos |
| [OAI Core v2.2.1 — user plane arm64](../../../../server/oai-cn-gnb-e2/oai-cn5g-v2/README.md) | Plano de usuario real en arm64 (`oai-upf` simple_switch): levantar, validar, rollback |
| [Biblia §7.c — user plane v2.2.1 + xApps event-driven](../../../../core5g-arm64-bible.md) | Levantar core v2 + RIC + gNB, ejecutar xApps deterministas, restricción de 2 vCPUs |

**Requisitos previos:** Linux con Docker y Docker Compose v2, usuario con permiso para `docker` (y eventualmente `sudo` para `sysctl` en la inicialización del core y para `tcpdump` en el *host*, si realiza capturas avanzadas).

**Raíz del proyecto (convención en los comandos):** `open5gs-containerized/` — ajuste los `cd` si su clon está en otra ruta (ej.: `code/open5gs-containerized`).

**Referencia técnica:** [README.md](../../../../README.md), [core/docs/CORE.md](../../../../core/docs/CORE.md), [ueransim/docs/RAN.md](../../../../ueransim/docs/RAN.md).
