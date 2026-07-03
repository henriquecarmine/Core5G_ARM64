<!-- sync: e8f9da69 -->
> 🌐 **English** translation of the canonical Portuguese doc [`docs/labs/00-docker-instalacao-ubuntu.md`](../../../labs/00-docker-instalacao-ubuntu.md). All languages: [INDEX](../INDEX.md) · sync checked by `docs/i18n/check-parity.py`.

# Guide — Installing Docker Engine and Docker Compose v2 (Ubuntu)

**Objective:** install **Docker Engine** and the **Docker Compose v2** plugin (`docker compose`) on **Ubuntu 22.04 LTS** or **24.04 LTS**, in the form required by labs [01 — Core](01-core-open5gs.md) and [02 — UERANSIM](02-ueransim-n2-n3-e2e.md).

**Where to use it:** physical machine, local VM (VirtualBox/VMware), **GCP VM** ([Guide 00 — GCP](00-pre-lab-gcp-vm-e-acesso.md)) or another provider — the commands are the same on Ubuntu.

**Canonical reference (updates):** [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/).

---

## 1. Remove old packages (optional, recommended if a distro Docker was ever installed)

Avoids conflicts with versions packaged by the distribution:

```bash
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
  sudo apt-get remove -y "$pkg" 2>/dev/null || true
done
```

---

## 2. Dependencies and the official Docker repository key

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

---

## 3. Add the Docker *apt* repository

```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo "${VERSION_CODENAME}") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

If `apt-get update` fails with a *codename* error, check `VERSION_CODENAME` with `grep VERSION_CODENAME /etc/os-release` and compare it against the versions supported in Docker's documentation.

---

## 4. Install Docker Engine and Compose v2

```bash
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

- **`docker compose`** comes from the **`docker-compose-plugin`** package (the `docker compose` subcommand, *v2*).

---

## 5. Service and startup

```bash
sudo systemctl enable --now docker
sudo systemctl status docker --no-pager
```

Expected output: *active (running)*.

---

## 6. User without `sudo` (the `docker` group)

```bash
sudo usermod -aG docker "$USER"
```

**You must end the SSH session (or log off the graphical terminal) and reconnect**, or run in the current session:

```bash
newgrp docker
```

Without this, `docker` commands fail with *permission denied*.

---

## 7. Verification (mandatory for the report / video)

```bash
docker --version
docker compose version
docker info
```

**Quick test (optional):**

```bash
docker run --rm hello-world
```

**Evidence aligned with Guide 01:** attach or show the first lines of `docker --version`, `docker compose version` and `uname -a` (the `uname` can be run in the same block).

---

## 8. Common problems

| Symptom | What to do |
| ------- | ----------- |
| `permission denied` when running `docker` | `docker` group: `newgrp docker` or a new SSH session after `usermod`. |
| `docker compose` not found | Confirm the `docker-compose-plugin` package (e.g. `dpkg -l` and search for that name). |
| Corporate proxy | Configure a proxy for `apt` and for the Docker *daemon* according to the network policy. |
| ARM64 (`aarch64`) | The repository above uses `dpkg --print-architecture`, so it already resolves to `arm64` without manual adjustment — which is exactly what this project uses in production (AWS `t4g.micro`, Ubuntu 24.04.4, Docker `29.6.0`, `docker-ce`/`docker-ce-cli`/`containerd.io` packages on `arm64`). The only real concern is the **compose image**, not Docker itself: confirm that each image publishes a `linux/arm64/v8` manifest (e.g. `gradiant/open5gs` only publishes `arm64` up to tag `2.7.2` — see [`core5g-arm64-bible.md` §8.1](../../../../core5g-arm64-bible.md#81--imagens-gradiantopen5gs-sem-build-arm64)); without it, `docker compose up` fails with `no matching manifest for linux/arm64/v8`. |

---

## Checklist

- [ ] `docker-ce`, `docker-compose-plugin` installed.
- [ ] `sudo systemctl status docker` → *running*.
- [ ] User in the `docker` group and session renewed.
- [ ] `docker compose version` responds with *v2*.
- [ ] (Optional) `docker run --rm hello-world` completes successfully.

**Next step:** [Guide 00 — GCP](00-pre-lab-gcp-vm-e-acesso.md) (if you still need a VM/clone) or [01 — Core](01-core-open5gs.md).
