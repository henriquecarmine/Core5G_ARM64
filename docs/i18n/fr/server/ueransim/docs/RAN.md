<!-- sync: e36a3f4e -->
> 🌐 Traduction en **français** du document canonique en portugais [`server/ueransim/docs/RAN.md`](../../../../../../server/ueransim/docs/RAN.md). Toutes les langues : [INDEX](../../../INDEX.md) · synchronisation vérifiée par `docs/i18n/check-parity.py`.

# Documentation consolidée - RAN (UERANSIM)

Document unique regroupant les principales informations sur la RAN et UERANSIM.

---

## 1. Vue d'ensemble

UERANSIM simule le gNB et l'UE pour des tests avec le Core Open5GS. Le compose RAN utilise les réseaux externes `net-n2` et `net-n3` créés par le Core — **le Core doit être démarré en premier**.

---

## 2. Configuration du gNB

### gnb.yaml

- **PLMN** : MCC=001, MNC=01
- **TAC** : 7 (doit correspondre à l'AMF)
- **IPs** : linkIp/ngapIp sur N2 (10.20.0.101), gtpIp sur N3 (10.30.0.11)
- **AMF** : 10.20.0.11:38412
- **Slices** : SST=1 (sans SD — l'AMF ne prend pas en charge le SD)

### Réseau

- **N2** : Communication avec l'AMF (NGAP)
- **N3** : Trafic de données avec l'UPF (GTP-U)

---

## 3. Configuration de l'UE

### ue.yaml

- **SUPI** : imsi-001010000000002
- **Keys** : K, OP, OPC conformément à l'abonné dans MongoDB
- **gnbSearchList** : 10.20.0.101 (IP du gNB)
- **Session** : IPv4, APN=internet, SST=1

### Champs obligatoires

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

**Note** : `integrityMaxRate` doit être un objet avec `uplink` et `downlink` ; un format scalaire provoque une erreur de parsing.

---

## 4. Version d'UERANSIM

- **Recommandé** : v3.2.6
- **À éviter** : v3.2.7 — bug « AMF context not found » après le NG Setup

Si vous utilisez v3.2.7, le NG Setup peut réussir, mais l'UE ne parvient pas à s'enregistrer (le timer T3510 expire).

---

## 5. Route par défaut de l'UE (contournement de la PDU session)

### Problème

L'UE peut avoir une route par défaut via le réseau Docker (10.20.0.1 sur eth0) au lieu de la PDU session (10.60.0.1 sur eth1), faisant contourner l'UPF par le trafic.

### Solution

Script `ue-entrypoint-fix-route.sh` dans l'entrypoint de l'UE :

1. Attend une IP sur l'interface eth1 (10.60.x.x)
2. Vérifie que la passerelle 10.60.0.1 est accessible
3. Supprime l'ancienne route par défaut
4. Ajoute `default via 10.60.0.1 dev eth1`

### Vérification

```bash
docker exec ueransim ip route show default
# Esperado: default via 10.60.0.1 dev eth1
```

---

## 6. Abonné dans MongoDB

L'abonné doit exister avant que l'UE ne s'enregistre. Format correct :

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

Utilisez `add-subscriber.sh` dans le Core pour l'ajouter.

---

## 7. Scripts

### test_ue_connection.sh

- Vérifie l'IP de l'UE
- Ping vers 8.8.8.8, 8.8.4.4, 1.1.1.1
- DNS, HTTP
- Route par défaut et connectivité

### up_ran.sh / down_ran.sh

- Démarre/arrête le compose RAN (gNB + UE)

---

## 8. Troubleshooting

### L'UE ne trouve pas de cellules

- UE et gNB sur le même réseau (net-n2)
- Ping du gNB : `docker exec ueransim ping 10.20.0.101`
- TAC du gNB = 7 (identique à l'AMF)

### NG Setup OK, mais l'enregistrement échoue

- Symptôme : « AMF context not found »
- Solution : utiliser UERANSIM v3.2.6
- Vérifier : `docker compose logs ueransim-gnb | grep "AMF context"`

### UE avec IP mais le trafic ne passe pas par l'UPF

- Vérifier la route : `default via 10.60.0.1 dev eth1`
- Exécuter `ue-entrypoint-fix-route.sh` ou redémarrer l'UE avec le bon entrypoint

### État de l'UE

```bash
docker compose logs ueransim-ue | grep "UE switches to state"
# Esperado: MM-REGISTERED
# Problema: MM-DEREGISTERED/ATTEMPTING-REGISTRATION
```

---

## 9. Flux d'enregistrement

1. L'UE trouve le gNB (gnbSearchList)
2. Connexion RRC établie
3. UE → gNB → AMF (N2) : Registration Request
4. AMF → AUSF → UDM : authentification
5. AMF → SMF : création de la PDU session
6. SMF → UPF : PFCP
7. AMF → gNB : Registration Accept
8. L'UE reçoit une IP (10.60.0.10) sur l'interface PDU

---

## 10. Références

- [UERANSIM](https://github.com/aligungr/UERANSIM)
- [UERANSIM Release Notes](https://github.com/aligungr/UERANSIM/wiki/Release-Notes)

---

*Dernière mise à jour : 2026-03*
