# Documentación traducida — es

🌐 [pt](../pt/INDEX.md) · [en](../en/INDEX.md) · **es** · [fr](../fr/INDEX.md)

> Espejo de la documentación canónica en portugués. Un archivo aquí replica
> `<raíz-del-repo>/<ruta>` o `<raíz-del-repo>/docs/<ruta>`. Cada traducción lleva
> un marcador `<!-- sync: <hash> -->` al inicio, verificado por
> `docs/i18n/check-parity.py` (señala huérfanos y traducciones desactualizadas
> respecto al historial git canónico).

## Laboratorios y ejercicios

Traducción completa al español de las guías de laboratorio. El glosario 3GPP/O-RAN
(AMF, CUPS, E2SM-KPM, N1/N2/N3…) se mantiene como en las especificaciones — solo
se traduce la explicación alrededor. El código, los comandos, las rutas de archivo
y las URL no se modifican.

**Proyecto 1 — Open5GS + UERANSIM**

| Guía | Contenido |
|------|-----------|
| [Índice](labs/INDICE.md) | Mapa de las guías de laboratorio |
| [00 — Instalación de Docker (Ubuntu)](labs/00-docker-instalacao-ubuntu.md) | Docker Engine + Compose v2 en la VM |
| [00 — Pre-lab: GCP, SSH y VM](labs/00-pre-lab-gcp-vm-e-acesso.md) | Ruta en la nube: VM, acceso, firewall/WebUI |
| [01 — Core 5GC (Open5GS)](labs/01-core-open5gs.md) | Levantar el core, suscriptor, WebUI, verificaciones |
| [02 — UERANSIM: N2/N3 y E2E](labs/02-ueransim-n2-n3-e2e.md) | gNB + UE, NGAP, GTP-U, pruebas, capturas N3/N6 |
| [03 — Informe, entrega y evaluación](labs/03-relatorio-entrega-avaliacao.md) | Entregables, evidencias obligatorias, rúbrica |
| [Videos del laboratorio](labs/video_seq_report.md) | Índice de videos (los videos están narrados en portugués) |

**Proyecto 2 — OAI 5GC + gNB + FlexRIC**

| Guía | Contenido |
|------|-----------|
| [Tutorial del lab E2](server/oai-cn-gnb-e2/docs/TUTORIAL_LAB_E2.md) | Core OAI + near-RT RIC + gNB (E2) + xApps, de punta a punta |

## READMEs

Los cuatro README de la raíz: [README.es.md](../../../README.es.md).

---

El portugués canónico vive en [`docs/labs/`](../../labs/) y
[`server/oai-cn-gnb-e2/docs/`](../../../server/oai-cn-gnb-e2/docs/). ¿Quieres
ayudar a traducir más (biblia, guías)? Consulta CONTRIBUTING (§7, i18n).
