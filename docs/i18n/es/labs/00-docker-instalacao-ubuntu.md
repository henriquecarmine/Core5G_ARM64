<!-- sync: e8f9da69 -->
> 🌐 Traducción al **español** del documento canónico en portugués [`docs/labs/00-docker-instalacao-ubuntu.md`](../../../labs/00-docker-instalacao-ubuntu.md). Todos los idiomas: [INDEX](../INDEX.md) · sincronización verificada por `docs/i18n/check-parity.py`.

# Guía — Instalación del Docker Engine y Docker Compose v2 (Ubuntu)

**Objetivo:** instalar **Docker Engine** y el plugin **Docker Compose v2** (`docker compose`) en **Ubuntu 22.04 LTS** o **24.04 LTS**, en el formato exigido por los laboratorios [01 — Core](01-core-open5gs.md) y [02 — UERANSIM](02-ueransim-n2-n3-e2e.md).

**Dónde usar:** máquina física, VM local (VirtualBox/VMware), **VM en GCP** ([Guía 00 — GCP](00-pre-lab-gcp-vm-e-acesso.md)) u otro proveedor — los comandos son los mismos en Ubuntu.

**Referencia canónica (actualizaciones):** [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/).

---

## 1. Eliminar paquetes antiguos (opcional, recomendado si ya hubo Docker de la distro)

Evita conflicto con versiones empaquetadas por la distribución:

```bash
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
  sudo apt-get remove -y "$pkg" 2>/dev/null || true
done
```

---

## 2. Dependencias y clave del repositorio oficial Docker

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

---

## 3. Añadir el repositorio *apt* de Docker

```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo "${VERSION_CODENAME}") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

Si `apt-get update` falla con error de *codename*, verifique `VERSION_CODENAME` con `grep VERSION_CODENAME /etc/os-release` y compárelo con las versiones soportadas en la documentación de Docker.

---

## 4. Instalar Docker Engine y Compose v2

```bash
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

- **`docker compose`** viene del paquete **`docker-compose-plugin`** (subcomando `docker compose`, *v2*).

---

## 5. Servicio e inicialización

```bash
sudo systemctl enable --now docker
sudo systemctl status docker --no-pager
```

Salida esperada: *active (running)*.

---

## 6. Usuario sin `sudo` (grupo `docker`)

```bash
sudo usermod -aG docker "$USER"
```

**Es necesario cerrar la sesión SSH (o hacer *logoff* en el terminal gráfico) y conectarse de nuevo**, o ejecutar en la sesión actual:

```bash
newgrp docker
```

Sin eso, los comandos `docker` fallan con *permission denied*.

---

## 7. Verificación (obligatoria para el informe / video)

```bash
docker --version
docker compose version
docker info
```

**Prueba rápida (opcional):**

```bash
docker run --rm hello-world
```

**Evidencia alineada con la Guía 01:** adjunte o muestre las primeras líneas de `docker --version`, `docker compose version` y `uname -a` (el `uname` puede ejecutarse en el mismo bloque).

---

## 8. Problemas frecuentes

| Síntoma | Qué hacer |
| ------- | ----------- |
| `permission denied` al ejecutar `docker` | Grupo `docker`: `newgrp docker` o nueva sesión SSH tras `usermod`. |
| `docker compose` no encontrado | Confirme el paquete `docker-compose-plugin` (ej.: `dpkg -l` y busque por ese nombre). |
| Proxy corporativo | Configure proxy para `apt` y para el *daemon* Docker según la política de la red. |
| ARM64 (`aarch64`) | El repositorio anterior usa `dpkg --print-architecture`, por lo que ya resuelve a `arm64` sin ajuste manual — es exactamente lo que este proyecto usa en producción (AWS `t4g.micro`, Ubuntu 24.04.4, Docker `29.6.0`, paquetes `docker-ce`/`docker-ce-cli`/`containerd.io` en `arm64`). El único cuidado real es la **imagen del compose**, no el Docker en sí: confirme que cada imagen publica manifest `linux/arm64/v8` (ej.: `gradiant/open5gs` solo publica `arm64` hasta la tag `2.7.2` — ver [`core5g-arm64-bible.md` §8.1](../../../../core5g-arm64-bible.md#81--imagens-gradiantopen5gs-sem-build-arm64)); sin eso, `docker compose up` falla con `no matching manifest for linux/arm64/v8`. |

---

## Lista de verificación

- [ ] `docker-ce`, `docker-compose-plugin` instalados.
- [ ] `sudo systemctl status docker` → *running*.
- [ ] Usuario en el grupo `docker` y sesión renovada.
- [ ] `docker compose version` responde con *v2*.
- [ ] (Opcional) `docker run --rm hello-world` finaliza con éxito.

**Próximo paso:** [Guía 00 — GCP](00-pre-lab-gcp-vm-e-acesso.md) (si aún falta VM/clon) o [01 — Core](01-core-open5gs.md).
