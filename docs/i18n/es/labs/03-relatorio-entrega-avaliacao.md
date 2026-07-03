<!-- sync: e8f9da69 -->
> 🌐 Traducción al **español** del documento canónico en portugués [`docs/labs/03-relatorio-entrega-avaliacao.md`](../../../labs/03-relatorio-entrega-avaliacao.md). Todos los idiomas: [INDEX](../INDEX.md) · sincronización verificada por `docs/i18n/check-parity.py`.

# Informe — entrega, estructura y criterios de evaluación (Open5GS + UERANSIM)

Este documento orienta a **estudiantes** (qué entregar) y a **docentes** (cómo evaluar).

**Material en video:** [lista de videos del laboratorio](video_seq_report.md). El [walkthrough completo](https://youtu.be/ic3_CIllb9o) recorre las guías 01–03 y muestra cómo cerrar las evidencias (incluyendo PCAP / Wireshark) para la entrega.

---

## 1. Formato de entrega

- **Formato aceptado:** PDF único **o** archivo `.zip`/`.7z` con PDF + anexos (logs en `.txt`; los PCAPs grandes pueden omitirse con justificación y *hash* o descripción de la captura).
- **Identificación en la primera página:** nombre completo, matrícula o identificación, grupo, fecha, título sugerido: «Laboratorio Open5GS + UERANSIM — Interfaces y Protocolos».
- **Versión del repositorio (recomendado):** salida de `git rev-parse --short HEAD` en la raíz del clon (si aplica).

---

## 2. Estructura sugerida del informe

1. **Resumen** (10–15 líneas): objetivos, lo que se ejecutó, principales resultados.
2. **Entorno:** SO, versiones `docker` / `docker compose`, RAM relevante (*pull* de imágenes).
3. **Guía 01 — Core:** referencia cruzada con evidencias ([01-core-open5gs.md](01-core-open5gs.md)).
4. **Guía 02 — UERANSIM:** ídem ([02-ueransim-n2-n3-e2e.md](02-ueransim-n2-n3-e2e.md)).
5. **Discusión:**
  - Papel de las interfaces **N2** (NGAP/SCTP) y **N3** (GTP-U) en el escenario containerizado.
  - Diferencias respecto a un gNB monolítico *vs.* *split* CU/DU (referencia conceptual; este laboratorio usa UERANSIM integrado).
  - Limitaciones (*emulation*, sin RF real, *stub* de celda, etc.).
6. **Conclusión** (5–8 líneas).
7. **Anexos** (numerados): A — salidas de comandos; B — logs; C — *prints*; D — PCAPs.

**Extensión sugerida:** 8–15 páginas **sin** anexos excesivos.

---

## 3. Inventario mínimo de evidencias (estudiante)


| ID  | Evidencia                                                                   | Guía |
| --- | --------------------------------------------------------------------------- | ---- |
| E1  | `docker --version` y `docker compose version`                               | 01   |
| E2  | `docker compose ps` (core saludable)                                        | 01   |
| E3  | Confirmación de redes `core_net-sbi` / `core_net-n2` / `core_net-n3` y subredes | 01   |
| E4  | Suscriptor creado (WebUI, script o `mongosh`) alineado con `ue.yaml`        | 01   |
| E5  | Salida completa `healthcheck.sh` (sin RAN o con nota sobre limitaciones)    | 01   |
| E6  | Muestra de logs NRF + AMF + SMF + UPF                                       | 01   |
| E7  | `docker ps` con `ueransim` **Up**                                           | 02   |
| E8  | Fragmentos relevantes `gnb.yaml` / `ue.yaml`                               | 02   |
| E9  | Logs UERANSIM + AMF con N2 / NG Setup                                       | 02   |
| E10 | (Opcional avanzado) PCAP o *print* Wireshark N2 (`sctp.port == 38412`)      | 02   |
| E11 | (Opcional avanzado) PCAP N3 o *print* Wireshark GTP-U (`udp.port == 2152`)  | 02   |
| E12 | Salida completa `test_ue_connection.sh`                                     | 02   |
| E13 | `healthcheck.sh` con el RAN encendido                                       | 02   |


Falta de **evidencia obligatoria** marcada en las guías → descuento en la rúbrica «Completitud».

---

## 4. Prints y capturas de pantalla

- **WebUI Open5GS:** 1 *print* (después del login o pantalla visible, sin contraseña).
- **Terminal:** *print* o texto monoespaciado; es preferible el texto buscable.
- **Wireshark:** *prints* con **filtro visible** — N2: `sctp.port == 38412`; N3: `udp.port == 2152`.

**Regla:** imágenes **legibles**; recortes con leyenda.

---

## 5. Buenas prácticas con logs

- No entregar logs de varios megabytes en el PDF; adjunta `.txt` o usa `tail -n 80`.
- Indica la **fecha/hora** de la recolección y el **contenedor** (`docker logs <nome>`).
- En caso de fallas, incluye el **primer** mensaje de error completo.

---

## 6. Rúbrica sugerida (100 puntos)


| Criterio             | Peso | Descripción                                                                  |
| -------------------- | ---- | ---------------------------------------------------------------------------- |
| **Completitud**      | 25   | Guías 01 y 02; evidencias E1–E13 donde aplique; anexos citados en el texto.  |
| **Corrección técnica** | 30 | Comandos e IPs coherentes con el proyecto; N2/N3 discutidos sin errores graves. |
| **Análisis**         | 25   | Limitaciones del lab; conexión con **interfaces y protocolos** 5G SA.         |
| **Claridad**         | 15   | Estructura, figuras numeradas, ortografía aceptable.                         |
| **Defensa / extra**  | 5    | PCAP N2 opcional; *troubleshooting* documentado; respuestas en la defensa.   |


---

## 7. Preguntas para la discusión

1. ¿Qué transporta el **N2** en relación con el **N3**?
2. ¿Por qué el compose UERANSIM depende de redes externas `core_net-n2` y `core_net-n3`?
3. ¿Qué es **PFCP** en el cruce SMF–UPF y cómo se relaciona con la sesión PDU?
4. ¿Qué cambiaría si el IMSI en el núcleo no correspondiera al `supi` del `ue.yaml`?

---

## 8. Lista de verificación final antes de enviar

- PDF con identificación completa  
- Figuras/tablas numeradas y citadas  
- Anexos con nombres claros (`anexoA-compose-ps.txt`, …)  
- Ninguna contraseña ni *token* en los logs  
- Referencias (Open5GS, UERANSIM, 3GPP, cuando aplique)

