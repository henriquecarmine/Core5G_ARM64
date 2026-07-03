<!-- sync: e8f9da69 -->
> 🌐 Traducción al **español** del documento canónico en portugués [`docs/labs/video_seq_report.md`](../../../labs/video_seq_report.md). Todos los idiomas: [INDEX](../INDEX.md) · sincronización verificada por `docs/i18n/check-parity.py`.

# Serie en video — ejecución del laboratorio Open5GS + UERANSIM

Esta página reúne los videos de apoyo al lab. Hay **dos formatos**:


| Formato                             | Público objetivo                                                                                                                    | Contenido                                                                                                 |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **Serie corta (1–3)** abajo         | Quien monta el entorno en **GCP** por etapas                                                                                        | VM, Docker, puesta en marcha E2E resumida.                                                               |
| **Video único — laboratorio local** | Quien ejecuta en **Linux local** (o VM ya lista) y quiere ver **todo de una vez**, incluyendo **Wireshark** y **herramientas de red** | Equivalente a las guías escritas **01 → 02 → 03** (core, UERANSIM/capturas, cierre para el informe).       |


Los `.md` siguen siendo la referencia para comandos exactos, evidencias y rúbrica; los videos muestran el flujo en la práctica.

---

## Cómo usar esta secuencia

1. **Ruta GCP:** mira los episodios **1 → 2 → 3** en orden (cada etapa presupone la anterior).
2. **Ruta local completa:** usa el [video completo](#video-lab-completo-local) como visión integrada; vuelve a las guías 01–03 para copiar comandos y armar anexos.
3. Ten el repositorio clonado y las guías abiertas en otra pestaña.
4. Pausa y reproduce los mismos comandos en tu terminal (si es posible) — el objetivo no es solo “ver”, sino **replicar** y registrar evidencias para el [informe de entrega](03-relatorio-entrega-avaliacao.md).

---

## Episodios


| #     | Tema                             | Lo que debes lograr al final                                                                                                                    | Guía escrita relacionada                                                                                                     |
| ----- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **1** | **VM en GCP**                    | Crear/acceder a una VM adecuada para el lab (SSH, recursos, noción de firewall).                                                                | [Pre-lab — GCP, SSH y puente al código](00-pre-lab-gcp-vm-e-acesso.md)                                                       |
| **2** | **Docker en la VM**              | Instalar Docker y Docker Compose v2; `docker run hello-world` (o equivalente) funcionando.                                                      | [Instalación Docker — Ubuntu](00-docker-instalacao-ubuntu.md)                                                                |
| **3** | **Sistema 5G de extremo a extremo** | Levantar core + RAN, suscriptor coherente con el UE, chequeos de salud y noción de N2/N3/E2E.                                                | [Guía 01 — Core](01-core-open5gs.md) · [Guía 02 — UERANSIM / E2E](02-ueransim-n2-n3-e2e.md)                                  |
| **★** | **Laboratorio completo (local)** | Recorrer **las guías 01 a 03** en una sesión; **tcpdump** / **Wireshark** (N2/N3); `ping` / rutas / `docker`; cierre alineado con el informe. | [01](01-core-open5gs.md) · [02](02-ueransim-n2-n3-e2e.md) · [03 — Informe y evidencias](03-relatorio-entrega-avaliacao.md)   |


### 1) VM en GCP (`setup_vm_gcp`)

**Video:** [youtu.be/67Xey5GV1G4](https://youtu.be/67Xey5GV1G4)

Ideal para quien aún no tiene la máquina del laboratorio. Presta atención a la **zona**, el **tamaño de la VM** (CPU/RAM/disco) y **cómo abrir la terminal** (SSH en el navegador vs `gcloud`), alineado con el pre-lab.

---

### 2) Instalación de Docker (`installing_docker_gcp`)

**Video:** [youtu.be/76TMQdSAXSw](https://youtu.be/76TMQdSAXSw)

Se centra en el entorno Ubuntu de la VM. Confirma en tu terminal:

```bash
docker --version
docker compose version
```

Si algo falla aquí, resuélvelo **antes** de levantar Open5GS.

---

### 3) Sistema 5G E2E (`running_5G_system_e2e`)

**Video:** [youtu.be/dgGzGDYYE_c](https://youtu.be/dgGzGDYYE_c)

Cubre el flujo completo (core, suscriptor, UERANSIM, verificaciones). Al mirarlo, compara con:

- el orden **core → suscriptor → RAN** en las guías 01 y 02;
- la necesidad de que el **IMSI en MongoDB** coincida con el `supi` en `ueransim/configs/ue.yaml`;
- los scripts `core/scripts/up_core.sh`, `core/scripts/add-subscriber.sh` (o equivalente), `ueransim/scripts/up_ran.sh` y `core/scripts/healthcheck.sh`.

---

### ★) Laboratorio completo — local (`full_lab_local_wireshark`)

**Video:** [youtu.be/ic3_CIllb9o](https://youtu.be/ic3_CIllb9o)

Mismo contenido descrito en la [sección detallada abajo](#video-lab-completo-local); úsalo como referencia única si prefieres una única sesión grabada (Linux local o VM ya con Docker).

---



## Video completo — ejecución local (guías 01 a 03, Wireshark y red)

Grabación **única** en entorno **local** (máquina Linux o VM con Docker ya utilizable), recorriendo el mismo contenido de las guías escritas **desde el inicio hasta el cierre para la entrega**, con énfasis en **visibilidad de protocolo** y **comandos de red**.

**Video:** [Laboratorio completo — guías 01 a 03 (Wireshark y red)](https://youtu.be/ic3_CIllb9o)

### Lo que cubre el video (mapa rápido)


| Fase                     | Guía escrita                                                          | Temas típicos en el video                                                                                                                                                                                                                                                 |
| ------------------------ | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **01 — Core**            | [01-core-open5gs.md](01-core-open5gs.md)                               | Limpieza opcional, `up_core`, MongoDB / suscriptor alineado con `ue.yaml`, WebUI, `healthcheck.sh`, conectividad básica entre contenedores.                                                                                                                               |
| **02 — UERANSIM y red**  | [02-ueransim-n2-n3-e2e.md](02-ueransim-n2-n3-e2e.md)                   | `up_ran`, logs del `ueransim`, **captura en el host** con `tcpdump` (ej.: SCTP **38412** para N2, UDP **2152** para GTP-U / N3), apertura de los PCAPs en **Wireshark** con filtros `sctp.port == 38412` y `udp.port == 2152`, pruebas con `ping` / rutas cuando la guía lo pida. |
| **03 — Informe**         | [03-relatorio-entrega-avaliacao.md](03-relatorio-entrega-avaliacao.md) | Cómo relacionar *prints*, logs y PCAPs con las evidencias **E1–E11**; estructura sugerida del PDF; qué cuenta como anexo mínimo.                                                                                                                                           |


### Herramientas que suelen aparecer

- **Docker / Compose** — puesta en marcha del core y del RAN, `docker ps`, `docker logs`, `docker exec` (ej.: `ip addr`, `ping` desde el UE/contenedor).
- **tcpdump** en el *host* — interfaces `docker0`, `br-`* o `any`, según la [guía 02](02-ueransim-n2-n3-e2e.md) (NGAP en SCTP, GTP-U).
- **Wireshark** — disección NGAP en N2 y GTP-U en N3; *prints* con **filtro visible** para el informe ([criterios en la guía 03](03-relatorio-entrega-avaliacao.md)).
- **Scripts del repositorio** — `healthcheck.sh`, `test-system-status.sh`, `test_ue_connection.sh` (cuando aplique a tu clon).

### Diferencia respecto a los episodios 1–3 (GCP)

La serie **1–3** anterior se centra en **crear la VM en GCP** e instalar Docker. El **video completo local** asume que el SO y Docker ya están bien y profundiza en las **guías 01–03**, las **capturas** y la **entrega** — útil para quien trabaja en su propia notebook o ya tiene una VM aprovisionada.

---

## Mini lista de verificación (después de la serie)

Marca mentalmente (o en el informe) lo que ya es válido en **tu** entorno:

- VM GCP accesible por SSH y con recursos suficientes para Docker + varias imágenes.
- `docker` y `docker compose` funcionando sin error.
- Core Open5GS en ejecución y NFs saludables (según la guía 01 / `healthcheck.sh`).
- Suscriptor registrado y **alineado** con `ue.yaml`.
- UERANSIM activo, NG setup y, cuando aplique, interfaz `uesimtun0` / IP de datos según la guía 02.
- *(Si seguiste el video completo local)* PCAP o *print* Wireshark con N2 o N3 alineados con la [guía 02](02-ueransim-n2-n3-e2e.md) y con la rúbrica de la [guía 03](03-relatorio-entrega-avaliacao.md).

---

**Índice general de los labs:** [INDICE.md](INDICE.md).
