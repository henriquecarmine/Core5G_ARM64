<!-- sync: e36a3f4e -->
> 🌐 **English** translation of the canonical Portuguese doc [`server/ueransim/docs/RAN.md`](../../../../../../server/ueransim/docs/RAN.md). All languages: [INDEX](../../../INDEX.md) · sync checked by `docs/i18n/check-parity.py`.

# Consolidated Documentation - RAN (UERANSIM)

Single document with the main information about the RAN and UERANSIM.

---

## 1. Overview

UERANSIM simulates a gNB and UE for testing with the Open5GS Core. The RAN compose uses the external networks `net-n2` and `net-n3` created by the Core — **the Core must be started first**.

---

## 2. gNB configuration

### gnb.yaml

- **PLMN**: MCC=001, MNC=01
- **TAC**: 7 (must match the AMF)
- **IPs**: linkIp/ngapIp on N2 (10.20.0.101), gtpIp on N3 (10.30.0.11)
- **AMF**: 10.20.0.11:38412
- **Slices**: SST=1 (no SD — the AMF does not support SD)

### Network

- **N2**: Communication with the AMF (NGAP)
- **N3**: Data traffic with the UPF (GTP-U)

---

## 3. UE configuration

### ue.yaml

- **SUPI**: imsi-001010000000002
- **Keys**: K, OP, OPC according to the subscriber in MongoDB
- **gnbSearchList**: 10.20.0.101 (gNB IP)
- **Session**: IPv4, APN=internet, SST=1

### Required fields

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

**Note**: `integrityMaxRate` must be an object with `uplink` and `downlink`; a scalar format causes a parsing error.

---

## 4. UERANSIM version

- **Recommended**: v3.2.6
- **Avoid**: v3.2.7 — "AMF context not found" bug after NG Setup

If you use v3.2.7, the NG Setup may succeed, but the UE cannot register (the T3510 timer expires).

---

## 5. UE default route (PDU session bypass)

### Problem

The UE may have a default route via the Docker network (10.20.0.1 on eth0) instead of the PDU session (10.60.0.1 on eth1), making the traffic bypass the UPF.

### Solution

The `ue-entrypoint-fix-route.sh` script in the UE entrypoint:

1. Waits for an IP on the eth1 interface (10.60.x.x)
2. Checks that the 10.60.0.1 gateway is reachable
3. Removes the old default route
4. Adds `default via 10.60.0.1 dev eth1`

### Verification

```bash
docker exec ueransim ip route show default
# Esperado: default via 10.60.0.1 dev eth1
```

---

## 6. Subscriber in MongoDB

The subscriber must exist before the UE registers. Correct format:

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

Use `add-subscriber.sh` in the Core to add it.

---

## 7. Scripts

### test_ue_connection.sh

- Checks the UE IP
- Ping to 8.8.8.8, 8.8.4.4, 1.1.1.1
- DNS, HTTP
- Default route and connectivity

### up_ran.sh / down_ran.sh

- Brings the RAN compose up/down (gNB + UE)

---

## 8. Troubleshooting

### UE does not find cells

- UE and gNB on the same network (net-n2)
- Ping the gNB: `docker exec ueransim ping 10.20.0.101`
- gNB TAC = 7 (same as the AMF)

### NG Setup OK, but registration fails

- Symptom: "AMF context not found"
- Solution: use UERANSIM v3.2.6
- Check: `docker compose logs ueransim-gnb | grep "AMF context"`

### UE with IP but traffic does not go through the UPF

- Check the route: `default via 10.60.0.1 dev eth1`
- Run `ue-entrypoint-fix-route.sh` or restart the UE with the correct entrypoint

### UE state

```bash
docker compose logs ueransim-ue | grep "UE switches to state"
# Esperado: MM-REGISTERED
# Problema: MM-DEREGISTERED/ATTEMPTING-REGISTRATION
```

---

## 9. Registration flow

1. UE finds the gNB (gnbSearchList)
2. RRC connection established
3. UE → gNB → AMF (N2): Registration Request
4. AMF → AUSF → UDM: authentication
5. AMF → SMF: PDU session creation
6. SMF → UPF: PFCP
7. AMF → gNB: Registration Accept
8. UE receives an IP (10.60.0.10) on the PDU interface

---

## 10. References

- [UERANSIM](https://github.com/aligungr/UERANSIM)
- [UERANSIM Release Notes](https://github.com/aligungr/UERANSIM/wiki/Release-Notes)

---

*Last updated: 2026-03*
