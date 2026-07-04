<!-- sync: e36a3f4e -->
> 🌐 Traducción al **español** del documento canónico en portugués [`server/ueransim/docs/RAN.md`](../../../../../../server/ueransim/docs/RAN.md). Todos los idiomas: [INDEX](../../../INDEX.md) · sincronización verificada por `docs/i18n/check-parity.py`.

# Documentación consolidada - RAN (UERANSIM)

Documento único con la información principal sobre la RAN y el UERANSIM.

---

## 1. Visión general

El UERANSIM simula gNB y UE para pruebas con el Core Open5GS. El compose RAN usa las redes externas `net-n2` y `net-n3` creadas por el Core — **el Core debe iniciarse primero**.

---

## 2. Configuración del gNB

### gnb.yaml

- **PLMN**: MCC=001, MNC=01
- **TAC**: 7 (debe corresponder al AMF)
- **IPs**: linkIp/ngapIp en N2 (10.20.0.101), gtpIp en N3 (10.30.0.11)
- **AMF**: 10.20.0.11:38412
- **Slices**: SST=1 (sin SD — el AMF no soporta SD)

### Red

- **N2**: Comunicación con el AMF (NGAP)
- **N3**: Tráfico de datos con el UPF (GTP-U)

---

## 3. Configuración del UE

### ue.yaml

- **SUPI**: imsi-001010000000002
- **Keys**: K, OP, OPC según el suscriptor en MongoDB
- **gnbSearchList**: 10.20.0.101 (IP del gNB)
- **Sesión**: IPv4, APN=internet, SST=1

### Campos obligatorios

```yaml
integrityMaxRate:
  uplink: full
  downlink: full

uacAic:
  mps: false
  mcs: false

uacAcc:
  normalClass: 0
  class11: false
  class12: false
  class13: false
  class14: false
  class15: false
```

**Nota**: `integrityMaxRate` debe ser un objeto con `uplink` y `downlink`; el formato escalar causa error de parsing.

---

## 4. Versión de UERANSIM

- **Recomendado**: v3.2.6
- **Evitar**: v3.2.7 — bug "AMF context not found" tras NG Setup

Si usas v3.2.7, el NG Setup puede ser exitoso, pero el UE no logra registrarse (el timer T3510 expira).

---

## 5. Ruta por defecto del UE (bypass de la PDU Session)

### Problema

El UE puede tener ruta por defecto vía la red Docker (10.20.0.1 en eth0) en vez de la PDU Session (10.60.0.1 en eth1), haciendo que el tráfico haga bypass del UPF.

### Solución

Script `ue-entrypoint-fix-route.sh` en el entrypoint del UE:

1. Espera IP en la interfaz eth1 (10.60.x.x)
2. Verifica que el gateway 10.60.0.1 esté accesible
3. Elimina la ruta por defecto antigua
4. Agrega `default via 10.60.0.1 dev eth1`

### Verificación

```bash
docker exec ueransim ip route show default
# Esperado: default via 10.60.0.1 dev eth1
```

---

## 6. Suscriptor en MongoDB

El suscriptor debe existir antes de que el UE se registre. Formato correcto:

```json
{
  "imsi": "001010000000002",
  "subscriber_profile": {
    "name": "default",
    "type": 1
  },
  "security": {
    "k": "465B5CE8B199B49FAA5F0A2EE238A6B0",
    "opc": "E8ED289DEBA952E4283B54E88E6183B8",
    "amf": "8000",
    "op_type": 1
  },
  "slice": [{
    "sst": 1,
    "default_indicator": true,
    "session": [{
      "name": "internet",
      "type": 3,
      "qos": { "index": 9 },
      "ambr": { "downlink": 1024000, "uplink": 1024000 }
    }]
  }]
}
```

Usa `add-subscriber.sh` en el Core para agregarlo.

---

## 7. Scripts

### test_ue_connection.sh

- Verifica IP del UE
- Ping a 8.8.8.8, 8.8.4.4, 1.1.1.1
- DNS, HTTP
- Ruta por defecto y conectividad

### up_ran.sh / down_ran.sh

- Levanta/baja el compose RAN (gNB + UE)

---

## 8. Troubleshooting

### El UE no encuentra celdas

- UE y gNB en la misma red (net-n2)
- Ping al gNB: `docker exec ueransim ping 10.20.0.101`
- TAC del gNB = 7 (igual al AMF)

### NG Setup OK, pero el registro falla

- Síntoma: "AMF context not found"
- Solución: usar UERANSIM v3.2.6
- Verificar: `docker compose logs ueransim-gnb | grep "AMF context"`

### UE con IP pero el tráfico no pasa por el UPF

- Verificar ruta: `default via 10.60.0.1 dev eth1`
- Ejecutar `ue-entrypoint-fix-route.sh` o reiniciar el UE con el entrypoint correcto

### Estado del UE

```bash
docker compose logs ueransim-ue | grep "UE switches to state"
# Esperado: MM-REGISTERED
# Problema: MM-DEREGISTERED/ATTEMPTING-REGISTRATION
```

---

## 9. Flujo de registro

1. El UE encuentra el gNB (gnbSearchList)
2. RRC connection established
3. UE → gNB → AMF (N2): Registration Request
4. AMF → AUSF → UDM: autenticación
5. AMF → SMF: creación de PDU Session
6. SMF → UPF: PFCP
7. AMF → gNB: Registration Accept
8. El UE recibe IP (10.60.0.10) en la interfaz PDU

---

## 10. Referencias

- [UERANSIM](https://github.com/aligungr/UERANSIM)
- [UERANSIM Release Notes](https://github.com/aligungr/UERANSIM/wiki/Release-Notes)

---

*Última actualización: 2026-03*
