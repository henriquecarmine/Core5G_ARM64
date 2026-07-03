<!-- sync: e8f9da69 -->
> 🌐 Traducción al **español** del documento canónico en portugués [`docs/labs/02-ueransim-n2-n3-e2e.md`](../../../labs/02-ueransim-n2-n3-e2e.md). Todos los idiomas: [INDEX](../INDEX.md) · sincronización verificada por `docs/i18n/check-parity.py`.

# Guía 02 — UERANSIM (gNB + UE), N2/N3 y prueba E2E

**Objetivos:** conectar el **UERANSIM** (gNB y UE en el mismo *contenedor*) al AMF Open5GS; validar **N2 (NGAP/SCTP)** y **N3 (GTP-U)**; comprobar el **registro** del UE y la **sesión PDU** con conectividad a Internet; recolectar evidencias del plano de usuario (capturas N3/N6 cuando sea posible).

**Prerrequisito:** [Guía 01](01-core-open5gs.md) concluida (core activo, suscriptor coherente con `ueransim/configs/ue.yaml`).

**Enfoque:** flujo SA de extremo a extremo y relación entre las interfaces **N2** (control) y **N3** (datos GTP-U).

**Rutas:** los comandos asumen la carpeta `open5gs-containerized/` en la raíz del laboratorio (ajusta a tu clon).

**Apoyo en video:** [índice de videos](video_seq_report.md) — el [video completo local](https://youtu.be/ic3_CIllb9o) incluye **tcpdump**, **Wireshark** (N2/N3) y pruebas de conectividad alineadas con esta guía.

---

## 1. Puesta en marcha del RAN (UERANSIM)

Con el **core** ya en ejecución (`core/scripts/up_core.sh`):

```bash
cd open5gs-containerized/ueransim
./scripts/up_ran.sh
```

El compose `ueransim/docker-compose.yaml` usa redes **externas** `core_net-n2` y `core_net-n3` creadas por el compose del **core**. Si aparece un error de red no encontrada, vuelve a la Guía 01 y levanta el core primero.

**Verificación:**

```bash
docker ps --filter name=ueransim --format '{{.Names}} {{.Status}}'
docker exec ueransim ps
```

**Evidencia obligatoria:** *print* o texto de `docker ps` con `ueransim` **Up**.

**Logs (fragmentos útiles):**

```bash
docker logs ueransim 2>&1 | tail -80
```

Indicadores de éxito típicos (la redacción exacta puede variar según la versión):

- **N2:** `NG Setup procedure is successful` (o mensaje equivalente de *NG Setup* completado).
- **UE:** estado **REGISTERED**, interfaz `uesimtun0` con IP en `10.60.x.x`.

Las advertencias de permisos o de temporización son comunes en laboratorio; el criterio es **registro estable** y **ping** en el paso 5.

---

## 2. Identidad del nodo RAN y del UE (para el informe)

Abre y **transcribe o adjunta** (con una breve leyenda) los campos relevantes de:

- `ueransim/configs/gnb.yaml`: `mcc`, `mnc`, `tac`, `amfConfigs` (dirección y puerto del AMF), `gtpIp` (IP N3 del gNB), `ngapIp` / `linkIp` (N2).
- `ueransim/configs/ue.yaml`: `supi`, `mcc`, `mnc`, `gnbSearchList`, `sessions` (APN/DNN).

**Preguntas guía:**

- ¿Cuál es el IPv4 del gNB/UERANSIM en la **N2**? (en el lab estándar: **10.20.0.101**.)  
- ¿Cuál es el IPv4 del lado GTP-U (N3) en el UERANSIM? (por defecto: **10.30.0.11**.)  
- ¿Cuál es la dirección del AMF en la N2? (por defecto: **10.20.0.11**, puerto **38412**.)

**Referencia:** [ueransim/docs/RAN.md](../../../../ueransim/docs/RAN.md).

---

## 3. Validación N2 (NGAP) — logs y verificación ampliada

### 3.1 Logs gNB / AMF

```bash
docker logs ueransim 2>&1 | grep -iE 'ng setup|ngap|amf' | tail -30
docker logs open5gs-amf-containerized 2>&1 | tail -80
```

**Evidencia:** fragmento en el que aparezca **NG Setup** exitoso o la aceptación del gNB por el AMF.

### 3.2 Script de estado del sistema (opcional)

Desde `core/` (con el RAN **ya** en marcha):

```bash
cd open5gs-containerized/core
./scripts/test-system-status.sh
```

Este script busca coincidencias en los logs (ej.: *NG Setup*, PFCP, IP del UE). Adjunta la salida si lo usas.

### 3.3 Captura N2 en el host (opcional / avanzado)

El proyecto no incluye un `capture-n2.sh` dedicado; puedes capturar **SCTP** en el puerto NGAP en el *host* (requiere `sudo`):

```bash
sudo tcpdump -i any -nn 'sctp and port 38412'
```

En otra terminal, **reinicia** el `ueransim` para forzar un nuevo *handshake* (`docker restart ueransim`), espera ~15 s, detén el `tcpdump` con Ctrl+C.

**En Wireshark:** filtro `sctp.port == 38412`; expande **NGAP** para ver `NGSetupRequest` / `NGSetupResponse` si el *dissector* está activo.

**Evidencia opcional (si realizas este paso):** *print* con SCTP + NGAP o adjunto `.pcap`.

---

## 4. Validación N3 y N6 — script de captura en el UPF

Con **core** y **ueransim** activos, desde `core/`:

```bash
cd open5gs-containerized/core
./scripts/capture-n3-n6-pcaps.sh
```

El script genera *pcaps* en `core/logs/upf/` (prefijos `n3-gtpu-*.pcap` y `n6-dn-*.pcap`) y dispara un *ping* desde el UE.

**En Wireshark (N3):**

- Filtro sugerido: `udp.port == 2152`  
- Observa **GTP-U** y, con tráfico generado, **G-PDU** con la IP interna del UE.

**Evidencia opcional:** *print* de Wireshark con **GTP-U** (puerto 2152) o adjunto de `.pcap` + una frase sobre el papel del TEID.

---

## 5. Prueba E2E — conectividad del UE

```bash
cd open5gs-containerized/ueransim
./scripts/test_ue_connection.sh
```

**Evidencia obligatoria:** salida **completa** del script (adjunto `.txt`).

**Complemento manual:**

```bash
docker exec ueransim ip addr show uesimtun0
docker exec ueransim ping -c 4 -I uesimtun0 8.8.8.8
```

**Evidencia:** IP asignada al UE y *ping* con pérdida 0% (o explicar las fallas con un fragmento de log).

---

## 6. Healthcheck global

Desde el directorio `core/`:

```bash
cd open5gs-containerized/core
./scripts/healthcheck.sh
```

**Evidencia:** salida completa. Con el RAN activo, las verificaciones N3 / NG Setup / PFCP deben estar **mucho más alineadas** que en la Guía 01.

---

## 7. Cierre

Orden sugerido: **RAN primero**, luego **core** (si vas a desmontar todo).

```bash
cd open5gs-containerized/ueransim
./scripts/down_ran.sh
```

(El core puede permanecer activo para nuevos ensayos.)

---

## Lista de verificación Guía 02

- *Contenedor* `ueransim` **Up**; logs con **NG Setup** exitoso (o equivalente).  
- Parámetros de `gnb.yaml` y `ue.yaml` descritos en el informe (N2/N3, PLMN, APN).  
- Fragmentos de log UERANSIM + AMF con N2/NG Setup.  
- (Opcional avanzado) Captura SCTP/NGAP en el *host* — *print* o `.pcap`.  
- (Opcional avanzado) Captura N3 vía `capture-n3-n6-pcaps.sh` — *print* Wireshark o `.pcap`.  
- Salida de `test_ue_connection.sh` (adjunto).  
- Salida de `healthcheck.sh` con el RAN encendido.  
- Párrafo en el informe: diferencia **N2** (*control / NGAP*) vs **N3** (*plano de usuario / GTP-U*).

**Referencias:** [ueransim/docs/RAN.md](../../../../ueransim/docs/RAN.md), [README.md](../../../../README.md) (*Troubleshooting*).

---

## Resumen de problemas frecuentes


| Síntoma                                | Causa probable                         | Qué verificar                              |
| -------------------------------------- | -------------------------------------- | ------------------------------------------ |
| `network core_net-n2 not found`        | Core no iniciado                       | `./scripts/up_core.sh` en `core/`.         |
| `slice-not-supported` / falla NG Setup | PLMN, TAC o SST/SD inconsistentes      | `gnb.yaml` vs `amf.yaml` / slice en el UDM. |
| UE sin IP                              | Suscriptor ausente o IMSI ≠ `ue.yaml`  | WebUI / Mongo; Guía 01.                    |
| Ping falla con IP asignada             | UPF / rutas / PFCP                     | Logs SMF y UPF; [README](../../../../README.md). |


