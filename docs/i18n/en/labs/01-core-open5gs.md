<!-- sync: e8f9da69 -->
> 🌐 **English** translation of the canonical Portuguese doc [`docs/labs/01-core-open5gs.md`](../../../labs/01-core-open5gs.md). All languages: [INDEX](../INDEX.md) · sync checked by `docs/i18n/check-parity.py`.

# Guide 01 — Infrastructure and 5G Core (Open5GS)

**Objectives:** Understand the lab's containerized stack; bring up the **5GC SA** (Open5GS) **without RAN**; validate NRF, SCP, AMF, SMF, UPF, MongoDB and subscription data aligned with the UE.

**Indicative duration:** 45–60 min (first run, including image *pull*).

**Video support:** [lab video index](video_seq_report.md) (GCP series and [full walkthrough](https://youtu.be/ic3_CIllb9o) with core + RAN + Wireshark).

---

## 1. Environment preparation

Run and **save the output** in the report attachments (or paste it into a code block / PDF).

```bash
docker --version
docker compose version
uname -a
```

**Evidence:** a screenshot or copy-paste of the three commands.

Check that the Docker *daemon* is active:

```bash
docker info
```

**Evidence:** the first 15–20 lines of the output (without sensitive data).

---

## 2. Optional cleanup (if repeating the lab)

Only if you have already run the lab and want a clean state:

```bash
cd open5gs-containerized/ueransim && ./scripts/down_ran.sh 2>/dev/null || true
cd ../core && ./scripts/down_core.sh
```

To **delete MongoDB volumes** (subscribers and the `open5gs` database reset — confirm you do not need the data):

```bash
cd open5gs-containerized/core
docker compose down -v
```

**Evidence:** not mandatory; mention in the report if you used a full *reset* with `-v`.

---

## 3. Bringing up the Core

The `up_core.sh` script may ask for **`sudo`** to enable *IP forwarding* on the host — accept if that is your machine's policy.

```bash
cd open5gs-containerized/core
./scripts/up_core.sh
```

Wait for the script to finish. If any NF fails, consult [core/docs/CORE.md](../../../../core/docs/CORE.md) and the *Troubleshooting* section of the [README](../../../../README.md).

**Immediate verification commands** (with the *working directory* in `core/`):

```bash
docker compose ps
docker network inspect core_net-sbi --format '{{json .IPAM.Config}}'
docker network inspect core_net-n2 --format '{{json .IPAM.Config}}'
docker network inspect core_net-n3 --format '{{json .IPAM.Config}}'
```

> The `core_` prefix in the network name corresponds to the name of the folder where `docker compose` runs (by default, the project name is the directory name: `core`).

**Mandatory evidence:**

1. **Screenshot or text** of `docker compose ps` with the main services **Up** (mongodb, nrf, scp, amf, smf, upf, webui, …).
2. Confirmation of the expected subnets: **SBI** `10.10.0.0/16`, **N2** `10.20.0.0/16`, **N3** `10.30.0.0/16` (the command above or `docker network ls | grep core_`).

---

## 4. Subscriber

The **IMSI / SUPI** in the core must match the one defined in `ueransim/configs/ue.yaml` (the `supi` field, for example `imsi-001010000000002`). Otherwise, the UE does not register correctly in Guide 02.

**Option A — WebUI (recommended):**

- URL: [http://localhost:9999](http://localhost:9999)
- Default credentials: `admin` / `1423` (see the [README](../../../../README.md) if the Mongo volume already existed and the admin user was not created).

Use **ADD A SUBSCRIBER** with the same parameters as `ue.yaml` and the example in [README.md](../../../../README.md) (**K** key, **OPC**, **AMF**, slice, DNN).

**If you cannot log in to the WebUI** (old volume without *init*):

```bash
cd open5gs-containerized/core
./scripts/add-webui-admin.sh
```

**Option B — Script (check alignment with `ue.yaml`):**

```bash
cd open5gs-containerized/core
./scripts/add-subscriber.sh
```

> The script inserts a hardcoded IMSI. If it differs from the `supi` in `ue.yaml`, use the WebUI or adjust the `ue.yaml` file / the script so they are **identical**.

**Manual verification (optional, for the report):**

```bash
docker exec open5gs-mongodb-containerized mongosh open5gs --quiet --eval 'db.subscribers.countDocuments({})'
docker exec open5gs-mongodb-containerized mongosh open5gs --quiet --eval 'db.subscribers.find({}, {imsi:1, supi:1}).limit(3).toArray()'
```

**Evidence:** document count ≥ 1 and an `imsi` field consistent with the UE, if present.

---

## 5. Healthcheck and state without RAN

```bash
cd open5gs-containerized/core
./scripts/healthcheck.sh
```

**Evidence:** attach the **complete** output (a `.txt` file or PDF).

**Notes:**

- Tests involving `ueransim` (the N3 network, NG Setup) may **fail or appear in yellow** while the RAN is not up — this is **expected** in this guide. Explain in the report: *«full N2/N3 validation in Guide 02»*.
- The *healthcheck* assumes the core compose's *container names* (e.g. `open5gs-amf-containerized`).

---

## 6. Web UI

With the core active, open the WebUI (port **9999**).

**Evidence:** a screenshot of the page after login or of the dashboard (with no passwords visible).

---

## 7. Minimum logs to collect

For the report, keep **recent excerpts** (the last ~30–80 lines) of:

```bash
cd open5gs-containerized/core
docker compose logs --tail 80 nrf
docker compose logs --tail 80 amf
docker compose logs --tail 80 smf
docker compose logs --tail 80 upf
```

(If `docker compose` complains about the service, use the service name defined in `docker-compose.yml`, e.g. `mongodb`, `amf`, `smf`.)

**Evidence:** a `logs-core-amostra.txt` file (or one file per NF) in the attachments.

---

## 8. Shutdown (end of day / core only)

```bash
cd open5gs-containerized/core
./scripts/down_core.sh
```

To also remove volumes: `docker compose down -v` (in the `core/` directory).

---

## Guide 01 Checklist

- Docker versions attached  
- `docker compose ps` with a healthy core  
- `core_net-sbi`, `core_net-n2`, `core_net-n3` networks identified  
- Subscriber created **aligned with `ue.yaml`** (WebUI or script + verification)  
- `healthcheck.sh` attached (with a note about tests that depend on the RAN)  
- Sample of NRF/AMF/SMF/UPF logs  
- Short text: what N2/N3 are and why part of the verification only makes sense after Guide 02  

**References:** [core/docs/CORE.md](../../../../core/docs/CORE.md), [README.md](../../../../README.md).
