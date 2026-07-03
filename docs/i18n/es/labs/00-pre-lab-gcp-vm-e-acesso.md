<!-- sync: e8f9da69 -->
> 🌐 Traducción al **español** del documento canónico en portugués [`docs/labs/00-pre-lab-gcp-vm-e-acesso.md`](../../../labs/00-pre-lab-gcp-vm-e-acesso.md). Todos los idiomas: [INDEX](../INDEX.md) · sincronización verificada por `docs/i18n/check-parity.py`.

# Pre-lab — VM en GCP, acceso SSH y Docker (grabación / demostración)

Esta guía cubre la **creación de la máquina virtual en Google Cloud**, **dos formas de acceso por terminal** y **puente hacia el código del lab**. La **instalación de Docker** está en la guía dedicada [Instalación Docker — Ubuntu](00-docker-instalacao-ubuntu.md).

**Público:** quienes van a **grabar un video** o conducir el lab por primera vez en GCP.

**No confundir con el Cloud Shell (`>_` en la parte superior de la Consola):** el laboratorio Open5GS + UERANSIM exige una **VM dedicada** con Docker; el Cloud Shell no es el entorno recomendado para este stack.

---

## 1. Dos opciones viables de acceso al shell de la VM


| Opción                                  | Qué es                                                                                                                       | Cuándo usar en el video                                                                                                                                                                 |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A — SSH en el navegador**             | En la Consola GCP → Compute Engine → VM → botón **SSH**: abre un terminal en el navegador conectado a la VM.                 | **Ruta mínima:** no exige instalar nada en el PC ni `gcloud`; ideal para principiantes.                                                                                               |
| **B — `gcloud compute ssh` (opcional)** | Terminal local con [Google Cloud SDK](https://cloud.google.com/sdk/docs/install), `gcloud auth login` y proyecto configurado. | Quienes ya usan `gcloud` y prefieren ventana de terminal local (fuente, *copy-paste*). **No es obligatorio** para concluir el lab si sigue la Opción A y una de las formas de la sección 7 sin SDK. |


En ambos casos usted está en un shell **dentro de la VM**; la diferencia es solo el **cliente** (navegador vs `gcloud`).

---

## 2. Requisitos previos en GCP (antes de crear la VM)

1. Cuenta Google con **facturación** activa en el proyecto (Compute Engine cobra por la VM en ejecución).
2. Proyecto GCP creado; anote el **ID del proyecto** (ej.: `meu-projeto-lab`).
3. API **Compute Engine** habilitada (la Consola suele ofrecer “Activar” la primera vez que abre Compute Engine).

**Consejo para demostración:** use un proyecto de laboratorio y **detenga o elimine la VM** al terminar para evitar costo continuo.

---

## 3. Crear la VM (configuración sugerida)

En la Consola: **Compute Engine → Instancias de VM → Crear instancia**.

Sugerencia alineada con los labs (Docker, varias imágenes, core + UERANSIM):


| Campo                   | Valor sugerido                                                                                                                                                                        |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Nombre                  | Ej.: `lab-open5gs`                                                                                                                                                                    |
| Región / zona           | Elija una zona cercana (ej.: `southamerica-east1-a`); si usa `gcloud` después, mantenga la **misma zona** en los comandos.                                                            |
| Serie / tipo de máquina | **T2A** (Tau T2A, ARM `aarch64`), **4 vCPU**, **8–16 GiB** de memoria (16 GiB reduce el riesgo de falla en el *pull* / *compose*). Equivalente AWS validado en este proyecto: **EC2 `t4g.micro`** (Graviton2 / Neoverse-N1) — ver §4 de la [Biblia del proyecto](../../../../core5g-arm64-bible.md). |
| SO                      | **Ubuntu 22.04 LTS** o **24.04 LTS**, imagen **`aarch64`** (en GCP, la familia **T2A** ya entrega Ubuntu ARM; en la AWS Console, elija la AMI marcada **arm64**).                     |
| Disco de inicialización | **50–80 GB** balanceado o SSD (las imágenes Docker ocupan bastante espacio).                                                                                                          |
| Firewall                | **Permitir HTTP/HTTPS** es opcional. Para abrir la WebUI por **internet sin `gcloud`** (sección 7.1), creará una **regla de firewall** solo para el puerto **9999** (y etiquetas en la VM). |


Cree la instancia y espere el estado **En ejecución**.

**Por qué ARM y no x86_64:** este proyecto fue originalmente escrito pensando en una VM **x86_64** (`E2`/`N2`), pero fue adaptado y **validado de extremo a extremo en una instancia ARM real** (AWS `t4g.micro`, Ubuntu 24.04.4 LTS, kernel `6.17`, Docker `29.6.0` — paquetes `arm64`). Use ARM (`T2A` en GCP, `t4g`/`t4g.micro`+ en AWS) como guía principal: es más barato y ya confirmado funcionando sin emulación. Único cuidado real encontrado: **imágenes Docker sin build `arm64`** — ver bug documentado en [`core5g-arm64-bible.md` §8.1](../../../../core5g-arm64-bible.md#81--imagens-gradiantopen5gs-sem-build-arm64) (fijar `gradiant/open5gs`/`gradiant/open5gs-webui` en la tag `2.7.2`, ya reflejado en `server/.env`). Si alguna imagen de su `docker compose` no tiene manifest `arm64`, ese es el síntoma a buscar — no es motivo para volver a x86_64 por defecto.

---

## 4. Opción A — Abrir terminal vía SSH en el navegador

1. **Compute Engine → Instancias de VM**.
2. En la fila de la VM, haga clic en **SSH** (o **Conectar** → SSH en el navegador).
3. Una ventana/pestaña abre con terminal ya autenticado.

**Primera conexión:** puede haber retraso mientras se configuran las claves.

---

## 5. Opción B — Terminal local con `gcloud compute ssh` (opcional)

1. Instale el [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) y ejecute:

```bash
gcloud auth login
gcloud config set project SEU_PROJECT_ID
```

1. Conecte (sustituya `NOME_DA_VM` y `ZONA`):

```bash
gcloud compute ssh NOME_DA_VM --zone=ZONA
```

1. La primera vez, confirme la huella digital del host si el `gcloud` lo pregunta.

A partir de aquí los comandos son **idénticos** a los de la Opción A (todo corre en la VM).

---

## 6. En la VM — Docker Engine y Compose v2

Ejecute **en la VM** la guía completa: **[00 — Instalación Docker (Ubuntu)](00-docker-instalacao-ubuntu.md)** (repositorio oficial vía `apt`, grupo `docker`, verificación y prueba opcional `hello-world`).

Después, verifique rápidamente (útil en el video y en el informe de la Guía 01):

```bash
docker --version
docker compose version
uname -a
```

---

## 7. WebUI en el puerto 9999 — sin exigir `gcloud` en el laptop

En la VM, el WebUI del lab responde en `http://127.0.0.1:9999`. El **SSH en el navegador** no abre un navegador gráfico dentro de la VM; para ver la interfaz en **su computadora**, use una de las opciones de abajo. Combinando la **Opción A** (SSH en el navegador) con **7.1, 7.2 o 7.3**, usted cubre el lab usando solo Consola GCP y terminal en el navegador, **sin** instalar el Google Cloud SDK en el laptop.

### 7.1 Regla de firewall + IP externo (todo por la Consola GCP)

Indicado para **demo en aula** o grabación, siempre que acepte exponer el puerto (mitigue con origen restringido o VM temporal).

1. Anote el **IP externo** de la VM (Compute Engine → instancias).
2. **VPC network → Firewall → Create firewall rule:**
  - **Targets:** “Specified target tags”; tag de ejemplo: `open5gs-webui`.
  - En la **instancia**, en “Editar” → **Tags de red**, añada la misma tag (`open5gs-webui`).
  - **Source IP ranges:** en laboratorio cerrado puede ser su IP (`x.x.x.x/32`); **no** use `0.0.0.0/0` en producción (cualquiera en internet accedería a la WebUI).
  - **Protocols and ports:** TCP **9999**.
3. Con el core en marcha, en el navegador del laptop: `http://IP_EXTERNO:9999`.

**Seguridad:** las credenciales por defecto de la WebUI son conocidas; trate la VM como **descartable** y elimine la regla o la VM tras el lab.

### 7.2 Túnel HTTPS desde la VM (sin abrir puerto en la VPC)

Aún en el SSH del navegador, en la VM, puede publicar `localhost:9999` mediante un servicio de túnel (ej.: [Cloudflare Tunnel (*quick tunnel*)](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/do-more-with-tunnels/trycloudflare/) o [ngrok](https://ngrok.com/)). El proveedor devuelve una **URL HTTPS**; ábrala en el laptop — **no** es necesario `gcloud` ni regla de firewall para la 9999.

- Lea los términos y límites del servicio; en clase, prefiera 7.1 con IP restringido o VM solo para el lab.

### 7.3 Sin WebUI en el video — solo terminal

La Guía 01 acepta crear el suscriptor con `**./scripts/add-subscriber.sh`** (alineado con `ue.yaml`). Nada impide concluir evidencias sin abrir el navegador; mencione en el informe que usó la opción por script.

### 7.4 Opcional — reenvío local con `gcloud` (quienes ya usan SDK)

Si instaló el Cloud SDK y prefiere no exponer la 9999 en internet:

```bash
gcloud compute ssh NOME_DA_VM --zone=ZONA -- -L 9999:127.0.0.1:9999 -N
```

Mantenga esa sesión abierta; en otro terminal, `gcloud compute ssh` sin `-N` para comandos. En el laptop: `http://localhost:9999`.

### 7.5 Avanzado — SSH local con `-L` (sin subcomando `gcloud ssh`)

Si configura una **clave SSH** en el metadata de la VM u OS Login y se conecta con `ssh usuário@IP_EXTERNO`, puede usar:

```bash
ssh -L 9999:127.0.0.1:9999 usuario@IP_EXTERNO
```

(Los detalles de usuario y clave dependen de la imagen Ubuntu de GCP; la Opción A de la Consola suele ser más simple.)

**Túnel SSH reverso** (`ssh -R`) solo es práctico si existe un servidor SSH **alcanzable en internet** o VPN (ej.: otra VM fija); por eso no es la ruta principal de esta guía.

---

## 8. Obtener el código del laboratorio en la VM

Ejemplo con `git` (ajuste la URL al repositorio oficial de la asignatura):

```bash
sudo apt-get update
sudo apt-get install -y git
cd ~
git clone https://github.com/jakunzler/cesar-school-repo.git
cd cesar-school-repo/oran/code/open5gs-containerized
```

Verifique si las carpetas `core/` y `ueransim/` existen y que los scripts tienen permiso de ejecución (`chmod +x` en los `.sh` si es necesario).

---

## 9. Guion del video (sugerencia de orden)

1. Consola GCP: proyecto, crear VM, **SSH en el navegador** (Opción A) en 30–60 s.
2. **Ruta sin `gcloud`:** permanezca en el SSH del navegador para Docker, clon y comandos de las guías 01/02; para WebUI use **7.1** (firewall + IP) o **7.2** (túnel en la VM) o **7.3** (solo `add-subscriber.sh`). **Ruta con SDK:** opcionalmente muestre `gcloud compute ssh` (Opción B) para el bloque largo de comandos.
3. `docker --version`, `docker compose version`, `uname -a`.
4. Seguir [01-core-open5gs.md](01-core-open5gs.md) hasta core estable + suscriptor + WebUI **o** script de suscriptor (según la sección 7).
5. Seguir [02-ueransim-n2-n3-e2e.md](02-ueransim-n2-n3-e2e.md) con el core ya en marcha.
6. Mencionar [03-relatorio-entrega-avaliacao.md](03-relatorio-entrega-avaliacao.md) como documento de **entrega** (no como paso de ejecución en la VM).

---

## 10. Después del entorno listo — ¿qué seguir?

- **Sí:** con Docker instalado y repositorio clonado en la VM, usted sigue la **Guía 01** (core) y luego la **Guía 02** (UERANSIM), en el orden de los archivos [01-core-open5gs.md](01-core-open5gs.md) y [02-ueransim-n2-n3-e2e.md](02-ueransim-n2-n3-e2e.md).
- El archivo **[03 — Informe, entrega y evaluación](03-relatorio-entrega-avaliacao.md)** no es un tercer “paso de laboratorio” en el terminal: describe **qué entregar** (PDF/anexos) y criterios. Flujo típico: **00 (este doc, una vez) → 01 → 02 → elaboración del informe según 03**.

---

## Lista de verificación rápida (docente / grabador)

- VM Ubuntu **`aarch64`/ARM** (familia `T2A` en GCP; `t4g` en AWS — validado en este proyecto), RAM y disco suficientes.
- SSH probado (navegador; `gcloud` solo si va a usar la Opción B).
- Docker + Compose v2 funcionando sin sudo.
- Clon del repo en la ruta esperada por las guías 01/02.
- Plan para WebUI: firewall **9999** (7.1), túnel en la VM (7.2), `add-subscriber.sh` (7.3) o `-L` con `gcloud`/`ssh` (7.4–7.5).
- Plan para apagar o eliminar la VM tras la grabación.

**Referencias:** [INDICE.md](INDICE.md), [README.md](../../../../README.md).
