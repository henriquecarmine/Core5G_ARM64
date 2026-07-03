<!-- sync: e8f9da69 -->
> 🌐 Traducción al **español** del documento canónico en portugués [`docs/labs/01-core-open5gs.md`](../../../labs/01-core-open5gs.md). Todos los idiomas: [INDEX](../INDEX.md) · sincronización verificada por `docs/i18n/check-parity.py`.

# Guía 01 — Infraestructura y Core 5G (Open5GS)

**Objetivos:** Comprender la stack containerizada del laboratorio; levantar el **5GC SA** (Open5GS) **sin RAN**; validar NRF, SCP, AMF, SMF, UPF, MongoDB y datos de suscripción alineados con el UE.

**Duración indicativa:** 45–60 min (primera ejecución, incluyendo *pull* de imágenes).

**Apoyo en video:** [índice de videos del lab](video_seq_report.md) (serie GCP y [walkthrough completo](https://youtu.be/ic3_CIllb9o) con core + RAN + Wireshark).

---

## 1. Preparación del entorno

Ejecute y **guarde la salida** en los anexos del informe (o péguela en un bloque de código / PDF).

```bash
docker --version
docker compose version
uname -a
```

**Evidencia:** *print* o copiar-pegar de los tres comandos.

Verifique si el *daemon* Docker está activo:

```bash
docker info
```

**Evidencia:** primeras 15–20 líneas de la salida (sin datos sensibles).

---

## 2. Limpieza opcional (si repite el lab)

Solo si ya ha ejecutado el laboratorio y quiere un estado limpio:

```bash
cd open5gs-containerized/ueransim && ./scripts/down_ran.sh 2>/dev/null || true
cd ../core && ./scripts/down_core.sh
```

Para **borrar volúmenes MongoDB** (suscriptores y base `open5gs` reiniciados — confirme que no necesita los datos):

```bash
cd open5gs-containerized/core
docker compose down -v
```

**Evidencia:** no obligatoria; mencione en el informe si usó *reset* total con `-v`.

---

## 3. Arranque del Core

El script `up_core.sh` puede pedir **`sudo`** para activar *IP forwarding* en el anfitrión (*host*) — acepte si es política de su máquina.

```bash
cd open5gs-containerized/core
./scripts/up_core.sh
```

Espere el fin del script. En caso de falla de algún NF, consulte [core/docs/CORE.md](../../../../core/docs/CORE.md) y la sección *Troubleshooting* del [README](../../../../README.md).

**Comandos de verificación inmediata** (con el *working directory* en `core/`):

```bash
docker compose ps
docker network inspect core_net-sbi --format '{{json .IPAM.Config}}'
docker network inspect core_net-n2 --format '{{json .IPAM.Config}}'
docker network inspect core_net-n3 --format '{{json .IPAM.Config}}'
```

> El prefijo `core_` en el nombre de la red corresponde al nombre de la carpeta donde corre el `docker compose` (por defecto, el nombre del proyecto es el del directorio: `core`).

**Evidencias obligatorias:**

1. **Print o texto** de `docker compose ps` con los servicios principales **Up** (mongodb, nrf, scp, amf, smf, upf, webui, …).
2. Confirmación de las subredes esperadas: **SBI** `10.10.0.0/16`, **N2** `10.20.0.0/16`, **N3** `10.30.0.0/16` (comando anterior o `docker network ls | grep core_`).

---

## 4. Suscriptor (Subscriber)

El **IMSI / SUPI** en el núcleo debe coincidir con el definido en `ueransim/configs/ue.yaml` (campo `supi`, por ejemplo `imsi-001010000000002`). De lo contrario, el UE no se registra correctamente en la Guía 02.

**Opción A — WebUI (recomendado):**

- URL: [http://localhost:9999](http://localhost:9999)
- Credenciales por defecto: `admin` / `1423` (ver [README](../../../../README.md) si el volumen Mongo ya existía y el usuario admin no fue creado).

Utilice **ADD A SUBSCRIBER** con los mismos parámetros que el `ue.yaml` y que el ejemplo en [README.md](../../../../README.md) (clave **K**, **OPC**, **AMF**, slice, DNN).

**Si no consigue iniciar sesión en el WebUI** (volumen antiguo sin *init*):

```bash
cd open5gs-containerized/core
./scripts/add-webui-admin.sh
```

**Opción B — Script (verifique la alineación con `ue.yaml`):**

```bash
cd open5gs-containerized/core
./scripts/add-subscriber.sh
```

> El script inserta un IMSI fijo en el código. Si es diferente del `supi` del `ue.yaml`, use la WebUI o ajuste el archivo `ue.yaml` / el script para que queden **iguales**.

**Verificación manual (opcional, para el informe):**

```bash
docker exec open5gs-mongodb-containerized mongosh open5gs --quiet --eval 'db.subscribers.countDocuments({})'
docker exec open5gs-mongodb-containerized mongosh open5gs --quiet --eval 'db.subscribers.find({}, {imsi:1, supi:1}).limit(3).toArray()'
```

**Evidencia:** número de documentos ≥ 1 y eventual campo `imsi` coherente con el UE.

---

## 5. Healthcheck y estado sin RAN

```bash
cd open5gs-containerized/core
./scripts/healthcheck.sh
```

**Evidencia:** adjunte la salida **completa** (archivo `.txt` o PDF).

**Notas:**

- Las pruebas que involucren `ueransim` (red N3, NG Setup) pueden **fallar o aparecer en amarillo** mientras el RAN no esté en marcha — es **esperado** en esta guía. Explique en el informe: *«validación N2/N3 completa en la Guía 02»*.
- El *healthcheck* asume *container names* del compose del core (ej.: `open5gs-amf-containerized`).

---

## 6. Web UI

Con el core activo, abra el WebUI (puerto **9999**).

**Evidencia:** *print* de la página tras el login o del panel (sin contraseñas visibles).

---

## 7. Logs mínimos a recolectar

Para el informe, guarde **fragmentos recientes** (últimas ~30–80 líneas) de:

```bash
cd open5gs-containerized/core
docker compose logs --tail 80 nrf
docker compose logs --tail 80 amf
docker compose logs --tail 80 smf
docker compose logs --tail 80 upf
```

(Si el `docker compose` se queja del servicio, use el nombre del servicio definido en `docker-compose.yml`, ej.: `mongodb`, `amf`, `smf`.)

**Evidencia:** archivo `logs-core-amostra.txt` (o un archivo por NF) en los anexos.

---

## 8. Cierre (fin del día / solo core)

```bash
cd open5gs-containerized/core
./scripts/down_core.sh
```

Para también eliminar volúmenes: `docker compose down -v` (en el directorio `core/`).

---

## Lista de verificación Guía 01

- Versiones Docker adjuntadas  
- `docker compose ps` con core saludable  
- Redes `core_net-sbi`, `core_net-n2`, `core_net-n3` identificadas  
- Suscriptor creado **alineado con `ue.yaml`** (WebUI o script + verificación)  
- `healthcheck.sh` adjuntado (con nota sobre pruebas que dependen del RAN)  
- Muestra de logs NRF/AMF/SMF/UPF  
- Texto corto: qué es N2/N3 y por qué parte de la verificación solo tiene sentido tras la Guía 02  

**Referencias:** [core/docs/CORE.md](../../../../core/docs/CORE.md), [README.md](../../../../README.md).
