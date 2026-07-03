<!-- sync: e8f9da69 -->
> 🌐 **English** translation of the canonical Portuguese doc [`docs/labs/02-ueransim-n2-n3-e2e.md`](../../../labs/02-ueransim-n2-n3-e2e.md). All languages: [INDEX](../INDEX.md) · sync checked by `docs/i18n/check-parity.py`.

# Lab Guide 02 — UERANSIM (gNB + UE), N2/N3 and E2E test

**Objectives:** connect **UERANSIM** (gNB and UE in the same *container*) to the Open5GS AMF; validate **N2 (NGAP/SCTP)** and **N3 (GTP-U)**; verify UE **registration** and **PDU Session** with Internet connectivity; collect user-plane evidence (N3/N6 captures when possible).

**Prerequisite:** [Lab Guide 01](01-core-open5gs.md) completed (core running, subscriber consistent with `ueransim/configs/ue.yaml`).

**Focus:** end-to-end SA flow and the relationship between the **N2** (control) and **N3** (GTP-U data) interfaces.

**Paths:** the commands assume the `open5gs-containerized/` folder at the lab root (adjust to your clone).

**Video support:** [video index](video_seq_report.md) — the [full local video](https://youtu.be/ic3_CIllb9o) includes **tcpdump**, **Wireshark** (N2/N3) and connectivity tests aligned with this lab guide.

---

## 1. Bringing up the RAN (UERANSIM)

With the **core** already running (`core/scripts/up_core.sh`):

```bash
cd open5gs-containerized/ueransim
./scripts/up_ran.sh
```

The `ueransim/docker-compose.yaml` compose uses the **external** networks `core_net-n2` and `core_net-n3` created by the **core** compose. If a network-not-found error appears, go back to Lab Guide 01 and bring up the core first.

**Verification:**

```bash
docker ps --filter name=ueransim --format '{{.Names}} {{.Status}}'
docker exec ueransim ps
```

**Mandatory evidence:** *screenshot* or text of `docker ps` with `ueransim` **Up**.

**Logs (useful excerpts):**

```bash
docker logs ueransim 2>&1 | tail -80
```

Typical success indicators (the exact wording may vary by version):

- **N2:** `NG Setup procedure is successful` (or an equivalent message for a completed *NG Setup*).
- **UE:** **REGISTERED** state, interface `uesimtun0` with IP in `10.60.x.x`.

Permission or timing warnings are common in the lab; the criterion is **stable registration** and **ping** in step 5.

---

## 2. Identity of the RAN node and the UE (for the report)

Open and **transcribe or attach** (with a brief caption) the relevant fields from:

- `ueransim/configs/gnb.yaml`: `mcc`, `mnc`, `tac`, `amfConfigs` (AMF address and port), `gtpIp` (gNB N3 IP), `ngapIp` / `linkIp` (N2).
- `ueransim/configs/ue.yaml`: `supi`, `mcc`, `mnc`, `gnbSearchList`, `sessions` (APN/DNN).

**Guiding questions:**

- What is the IPv4 of the gNB/UERANSIM on **N2**? (in the default lab: **10.20.0.101**.)  
- What is the IPv4 on the GTP-U (N3) side in UERANSIM? (default: **10.30.0.11**.)  
- What is the AMF address on N2? (default: **10.20.0.11**, port **38412**.)

**Reference:** [ueransim/docs/RAN.md](../../../../ueransim/docs/RAN.md).

---

## 3. N2 (NGAP) validation — logs and extended verification

### 3.1 gNB / AMF logs

```bash
docker logs ueransim 2>&1 | grep -iE 'ng setup|ngap|amf' | tail -30
docker logs open5gs-amf-containerized 2>&1 | tail -80
```

**Evidence:** an excerpt showing a successful **NG Setup** or the AMF accepting the gNB.

### 3.2 System status script (optional)

From `core/` (with the RAN **already** up):

```bash
cd open5gs-containerized/core
./scripts/test-system-status.sh
```

This script looks for matches in the logs (e.g., *NG Setup*, PFCP, UE IP). Attach the output if you use it.

### 3.3 N2 capture on the host (optional / advanced)

The project does not include a dedicated `capture-n2.sh`; you can capture **SCTP** on the NGAP port on the *host* (requires `sudo`):

```bash
sudo tcpdump -i any -nn 'sctp and port 38412'
```

In another terminal, **restart** `ueransim` to force a new *handshake* (`docker restart ueransim`), wait ~15 s, then stop `tcpdump` with Ctrl+C.

**In Wireshark:** filter `sctp.port == 38412`; expand **NGAP** to see `NGSetupRequest` / `NGSetupResponse` if the *dissector* is active.

**Optional evidence (if you perform this step):** *screenshot* with SCTP + NGAP or a `.pcap` attachment.

---

## 4. N3 and N6 validation — capture script on the UPF

With **core** and **ueransim** running, from `core/`:

```bash
cd open5gs-containerized/core
./scripts/capture-n3-n6-pcaps.sh
```

The script generates *pcaps* under `core/logs/upf/` (prefixes `n3-gtpu-*.pcap` and `n6-dn-*.pcap`) and triggers a *ping* from the UE.

**In Wireshark (N3):**

- Suggested filter: `udp.port == 2152`  
- Observe **GTP-U** and, with generated traffic, **G-PDU** with the UE's internal IP.

**Optional evidence:** Wireshark *screenshot* with **GTP-U** (port 2152) or a `.pcap` attachment + a sentence about the role of the TEID.

---

## 5. E2E test — UE connectivity

```bash
cd open5gs-containerized/ueransim
./scripts/test_ue_connection.sh
```

**Mandatory evidence:** **complete** output of the script (`.txt` attachment).

**Manual supplement:**

```bash
docker exec ueransim ip addr show uesimtun0
docker exec ueransim ping -c 4 -I uesimtun0 8.8.8.8
```

**Evidence:** IP assigned to the UE and *ping* with 0% loss (or explain failures with a log excerpt).

---

## 6. Global healthcheck

From the `core/` directory:

```bash
cd open5gs-containerized/core
./scripts/healthcheck.sh
```

**Evidence:** complete output. With the RAN running, the N3 / NG Setup / PFCP checks should be **much more aligned** than in Lab Guide 01.

---

## 7. Shutdown

Suggested order: **RAN first**, then **core** (if tearing everything down).

```bash
cd open5gs-containerized/ueransim
./scripts/down_ran.sh
```

(The core can stay running for further trials.)

---

## Lab Guide 02 checklist

- *Container* `ueransim` **Up**; logs with a successful **NG Setup** (or equivalent).  
- Parameters from `gnb.yaml` and `ue.yaml` described in the report (N2/N3, PLMN, APN).  
- UERANSIM + AMF log excerpts with N2/NG Setup.  
- (Advanced optional) SCTP/NGAP capture on the *host* — *screenshot* or `.pcap`.  
- (Advanced optional) N3 capture via `capture-n3-n6-pcaps.sh` — Wireshark *screenshot* or `.pcap`.  
- Output of `test_ue_connection.sh` (attachment).  
- Output of `healthcheck.sh` with the RAN up.  
- Paragraph in the report: difference between **N2** (*control / NGAP*) vs **N3** (*user plane / GTP-U*).

**References:** [ueransim/docs/RAN.md](../../../../ueransim/docs/RAN.md), [README.md](../../../../README.md) (*Troubleshooting*).

---

## Summary of common problems


| Symptom                                | Likely cause                           | What to check                                |
| -------------------------------------- | -------------------------------------- | -------------------------------------------- |
| `network core_net-n2 not found`        | Core not started                       | `./scripts/up_core.sh` in `core/`.           |
| `slice-not-supported` / NG Setup failure | Inconsistent PLMN, TAC or SST/SD      | `gnb.yaml` vs `amf.yaml` / slice in the UDM. |
| UE without IP                          | Missing subscriber or IMSI ≠ `ue.yaml` | WebUI / Mongo; Lab Guide 01.                 |
| Ping fails with an assigned IP         | UPF / routes / PFCP                    | SMF and UPF logs; [README](../../../../README.md). |


