<!-- sync: e8f9da69 -->
> 🌐 **English** translation of the canonical Portuguese doc [`docs/labs/00-pre-lab-gcp-vm-e-acesso.md`](../../../labs/00-pre-lab-gcp-vm-e-acesso.md). All languages: [INDEX](../INDEX.md) · sync checked by `docs/i18n/check-parity.py`.

# Pre-lab — GCP VM, SSH access and Docker (recording / demonstration)

This guide covers **creating the virtual machine on Google Cloud**, **two ways to access it from a terminal** and **the bridge to the lab code**. The **Docker installation** is in the dedicated guide [Docker Installation — Ubuntu](00-docker-instalacao-ubuntu.md).

**Audience:** anyone who will **record a video** or run the lab for the first time on GCP.

**Do not confuse this with Cloud Shell (`>_` at the top of the Console):** the Open5GS + UERANSIM lab requires a **dedicated VM** with Docker; Cloud Shell is not the recommended environment for this stack.

---

## 1. Two viable options for accessing the VM shell


| Option                                  | What it is                                                                                                                   | When to use it in the video                                                                                                                                                            |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A — SSH in the browser**              | In the GCP Console → Compute Engine → VM → **SSH** button: opens a terminal in the browser connected to the VM.              | **Minimal track:** requires installing nothing on the PC and no `gcloud`; ideal for beginners.                                                                                        |
| **B — `gcloud compute ssh` (optional)** | Local terminal with the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install), `gcloud auth login` and a configured project. | Anyone who already uses `gcloud` and prefers a local terminal window (font, *copy-paste*). **Not required** to complete the lab if you follow Option A and one of the methods in section 7 without the SDK. |


In both cases you are in a shell **inside the VM**; the only difference is the **client** (browser vs `gcloud`).

---

## 2. GCP prerequisites (before creating the VM)

1. A Google account with **billing** enabled on the project (Compute Engine charges for the running VM).
2. A created GCP project; note the **project ID** (e.g. `meu-projeto-lab`).
3. The **Compute Engine** API enabled (the Console usually offers “Enable” the first time you open Compute Engine).

**Demo tip:** use a lab project and **stop or delete the VM** when you finish to avoid ongoing cost.

---

## 3. Create the VM (suggested configuration)

In the Console: **Compute Engine → VM instances → Create instance**.

Suggestion aligned with the labs (Docker, several images, core + UERANSIM):


| Field                   | Suggested value                                                                                                                                                                       |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Name                    | E.g. `lab-open5gs`                                                                                                                                                                   |
| Region / zone           | Choose a nearby zone (e.g. `southamerica-east1-a`); if you use `gcloud` later, keep the **same zone** in the commands.                                                                |
| Machine series / type   | **T2A** (Tau T2A, ARM `aarch64`), **4 vCPU**, **8–16 GiB** of memory (16 GiB reduces the risk of failure during *pull* / *compose*). AWS equivalent validated in this project: **EC2 `t4g.micro`** (Graviton2 / Neoverse-N1) — see §4 of the [project Bible](../../../../core5g-arm64-bible.md). |
| OS                      | **Ubuntu 22.04 LTS** or **24.04 LTS**, **`aarch64`** image (on GCP, the **T2A** family already delivers Ubuntu ARM; in the AWS Console, choose the AMI marked **arm64**).             |
| Boot disk               | **50–80 GB** balanced or SSD (Docker images take up a lot of space).                                                                                                                  |
| Firewall                | **Allow HTTP/HTTPS** is optional. To open the WebUI over the **internet without `gcloud`** (section 7.1), you will create a **firewall rule** just for port **9999** (and tags on the VM). |


Create the instance and wait for the **Running** state.

**Why ARM and not x86_64:** this project was originally written with an **x86_64** VM in mind (`E2`/`N2`), but it was adapted and **validated end to end on a real ARM instance** (AWS `t4g.micro`, Ubuntu 24.04.4 LTS, kernel `6.17`, Docker `29.6.0` — `arm64` packages). Use ARM (`T2A` on GCP, `t4g`/`t4g.micro`+ on AWS) as the main guide: it is cheaper and already confirmed working without emulation. The only real concern found: **Docker images without an `arm64` build** — see the bug documented in [`core5g-arm64-bible.md` §8.1](../../../../core5g-arm64-bible.md#81--imagens-gradiantopen5gs-sem-build-arm64) (pin `gradiant/open5gs`/`gradiant/open5gs-webui` to tag `2.7.2`, already reflected in `server/.env`). If any image in your `docker compose` lacks an `arm64` manifest, that is the symptom to look for — it is not a reason to revert to x86_64 by default.

---

## 4. Option A — Open a terminal via SSH in the browser

1. **Compute Engine → VM instances**.
2. In the VM's row, click **SSH** (or **Connect** → SSH in the browser).
3. A window/tab opens with a terminal that is already authenticated.

**First connection:** there may be a delay while the keys are configured.

---

## 5. Option B — Local terminal with `gcloud compute ssh` (optional)

1. Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) and run:

```bash
gcloud auth login
gcloud config set project SEU_PROJECT_ID
```

1. Connect (replace `NOME_DA_VM` and `ZONA`):

```bash
gcloud compute ssh NOME_DA_VM --zone=ZONA
```

1. The first time, confirm the host fingerprint if `gcloud` asks.

From here on, the commands are **identical** to those in Option A (everything runs on the VM).

---

## 6. On the VM — Docker Engine and Compose v2

Run the full guide **on the VM**: **[00 — Docker Installation (Ubuntu)](00-docker-instalacao-ubuntu.md)** (official repository via `apt`, the `docker` group, verification and optional `hello-world` test).

Then quickly check (useful in the video and in the Guide 01 report):

```bash
docker --version
docker compose version
uname -a
```

---

## 7. WebUI on port 9999 — without requiring `gcloud` on the laptop

On the VM, the lab's WebUI responds at `http://127.0.0.1:9999`. **SSH in the browser** does not open a graphical browser inside the VM; to see the interface on **your computer**, use one of the options below. By combining **Option A** (SSH in the browser) with **7.1, 7.2 or 7.3**, you cover the lab using only the GCP Console and a browser terminal, **without** installing the Google Cloud SDK on the laptop.

### 7.1 Firewall rule + external IP (all via the GCP Console)

Suitable for a **classroom demo** or recording, as long as you accept exposing the port (mitigate with a restricted source or a temporary VM).

1. Note the VM's **external IP** (Compute Engine → instances).
2. **VPC network → Firewall → Create firewall rule:**
  - **Targets:** “Specified target tags”; example tag: `open5gs-webui`.
  - On the **instance**, under “Edit” → **Network tags**, add the same tag (`open5gs-webui`).
  - **Source IP ranges:** in a closed lab this can be your IP (`x.x.x.x/32`); **do not** use `0.0.0.0/0` in production (anyone on the internet would access the WebUI).
  - **Protocols and ports:** TCP **9999**.
3. With the core up, in the laptop browser: `http://IP_EXTERNO:9999`.

**Security:** the WebUI's default credentials are well known; treat the VM as **disposable** and tear down the rule or the VM after the lab.

### 7.2 HTTPS tunnel from the VM (without opening a port on the VPC)

Still in the browser SSH, on the VM, you can publish `localhost:9999` through a tunneling service (e.g. [Cloudflare Tunnel (*quick tunnel*)](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/do-more-with-tunnels/trycloudflare/) or [ngrok](https://ngrok.com/)). The provider returns an **HTTPS URL**; open it on the laptop — you need **neither** `gcloud` nor a firewall rule for 9999.

- Read the service's terms and limits; in class, prefer 7.1 with a restricted IP or a VM dedicated to the lab.

### 7.3 Without WebUI in the video — terminal only

Guide 01 allows creating the subscriber with `**./scripts/add-subscriber.sh`** (aligned with `ue.yaml`). Nothing prevents you from completing evidence without opening the browser; mention in the report that you used the script option.

### 7.4 Optional — local forwarding with `gcloud` (for those who already use the SDK)

If you have installed the Cloud SDK and prefer not to expose 9999 to the internet:

```bash
gcloud compute ssh NOME_DA_VM --zone=ZONA -- -L 9999:127.0.0.1:9999 -N
```

Keep this session open; in another terminal, use `gcloud compute ssh` without `-N` for commands. On the laptop: `http://localhost:9999`.

### 7.5 Advanced — local SSH with `-L` (without the `gcloud ssh` subcommand)

If you configure an **SSH key** in the VM metadata or OS Login and connect with `ssh usuário@IP_EXTERNO`, you can use:

```bash
ssh -L 9999:127.0.0.1:9999 usuario@IP_EXTERNO
```

(User and key details depend on the GCP Ubuntu image; the Console's Option A is usually simpler.)

**Reverse SSH tunnel** (`ssh -R`) is only practical if there is an SSH server **reachable on the internet** or a VPN (e.g. another fixed VM); that is why it is not the main route in this guide.

---

## 8. Get the lab code on the VM

Example with `git` (adjust the URL to the course's official repository):

```bash
sudo apt-get update
sudo apt-get install -y git
cd ~
git clone https://github.com/jakunzler/cesar-school-repo.git
cd cesar-school-repo/oran/code/open5gs-containerized
```

Check that the `core/` and `ueransim/` folders exist and that the scripts have execute permission (`chmod +x` on the `.sh` files if needed).

---

## 9. Video script (suggested order)

1. GCP Console: project, create VM, **SSH in the browser** (Option A) in 30–60 s.
2. **Track without `gcloud`:** stay in the browser SSH for Docker, the clone and the commands of guides 01/02; for WebUI use **7.1** (firewall + IP) or **7.2** (tunnel on the VM) or **7.3** (just `add-subscriber.sh`). **Track with SDK:** optionally show `gcloud compute ssh` (Option B) for the long block of commands.
3. `docker --version`, `docker compose version`, `uname -a`.
4. Follow [01-core-open5gs.md](01-core-open5gs.md) until a stable core + subscriber + WebUI **or** the subscriber script (per section 7).
5. Follow [02-ueransim-n2-n3-e2e.md](02-ueransim-n2-n3-e2e.md) with the core already up.
6. Mention [03-relatorio-entrega-avaliacao.md](03-relatorio-entrega-avaliacao.md) as the **submission** document (not as an execution step on the VM).

---

## 10. After the environment is ready — what next?

- **Yes:** with Docker installed and the repository cloned on the VM, you follow **Guide 01** (core) and then **Guide 02** (UERANSIM), in the order of the files [01-core-open5gs.md](01-core-open5gs.md) and [02-ueransim-n2-n3-e2e.md](02-ueransim-n2-n3-e2e.md).
- The file **[03 — Report, submission and assessment](03-relatorio-entrega-avaliacao.md)** is not a third “lab step” in the terminal: it describes **what to submit** (PDF/attachments) and the criteria. Typical flow: **00 (this doc, once) → 01 → 02 → writing the report per 03**.

---

## Quick checklist (instructor / recorder)

- Ubuntu **`aarch64`/ARM** VM (the `T2A` family on GCP; `t4g` on AWS — validated in this project), sufficient RAM and disk.
- SSH tested (browser; `gcloud` only if you will use Option B).
- Docker + Compose v2 working without sudo.
- Repo clone in the path expected by guides 01/02.
- Plan for the WebUI: firewall **9999** (7.1), tunnel on the VM (7.2), `add-subscriber.sh` (7.3) or `-L` with `gcloud`/`ssh` (7.4–7.5).
- Plan to shut down or delete the VM after recording.

**References:** [INDICE.md](INDICE.md), [README.md](../../../../README.md).
