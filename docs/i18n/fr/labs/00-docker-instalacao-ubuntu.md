<!-- sync: e8f9da69 -->
> 🌐 Traduction en **français** du document canonique en portugais [`docs/labs/00-docker-instalacao-ubuntu.md`](../../../labs/00-docker-instalacao-ubuntu.md). Toutes les langues : [INDEX](../INDEX.md) · synchronisation vérifiée par `docs/i18n/check-parity.py`.

# Guide — Installation de Docker Engine et Docker Compose v2 (Ubuntu)

**Objectif :** installer **Docker Engine** et le plugin **Docker Compose v2** (`docker compose`) sur **Ubuntu 22.04 LTS** ou **24.04 LTS**, dans le format exigé par les travaux pratiques [01 — Core](01-core-open5gs.md) et [02 — UERANSIM](02-ueransim-n2-n3-e2e.md).

**Où l'utiliser :** machine physique, VM locale (VirtualBox/VMware), **VM sur GCP** ([Guide 00 — GCP](00-pre-lab-gcp-vm-e-acesso.md)) ou autre fournisseur — les commandes sont les mêmes sous Ubuntu.

**Référence canonique (mises à jour) :** [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/).

---

## 1. Supprimer les anciens paquets (optionnel, recommandé si Docker distro était déjà présent)

Évite les conflits avec les versions empaquetées par la distribution :

```bash
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
  sudo apt-get remove -y "$pkg" 2>/dev/null || true
done
```

---

## 2. Dépendances et clé du dépôt officiel Docker

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

---

## 3. Ajouter le dépôt *apt* de Docker

```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo "${VERSION_CODENAME}") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

Si `apt-get update` échoue avec une erreur de *codename*, vérifiez `VERSION_CODENAME` avec `grep VERSION_CODENAME /etc/os-release` et comparez avec les versions prises en charge dans la documentation de Docker.

---

## 4. Installer Docker Engine et Compose v2

```bash
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

- **`docker compose`** provient du paquet **`docker-compose-plugin`** (sous-commande `docker compose`, *v2*).

---

## 5. Service et démarrage

```bash
sudo systemctl enable --now docker
sudo systemctl status docker --no-pager
```

Sortie attendue : *active (running)*.

---

## 6. Utilisateur sans `sudo` (groupe `docker`)

```bash
sudo usermod -aG docker "$USER"
```

**Il est nécessaire de fermer la session SSH (ou de se *déconnecter* du terminal graphique) et de se reconnecter**, ou d'exécuter dans la session actuelle :

```bash
newgrp docker
```

Sans cela, les commandes `docker` échouent avec *permission denied*.

---

## 7. Vérification (obligatoire pour le rapport / la vidéo)

```bash
docker --version
docker compose version
docker info
```

**Test rapide (optionnel) :**

```bash
docker run --rm hello-world
```

**Preuve alignée sur le Guide 01 :** joignez ou montrez les premières lignes de `docker --version`, `docker compose version` et `uname -a` (le `uname` peut être exécuté dans le même bloc).

---

## 8. Problèmes fréquents

| Symptôme | Que faire |
| ------- | ----------- |
| `permission denied` en lançant `docker` | Groupe `docker` : `newgrp docker` ou nouvelle session SSH après `usermod`. |
| `docker compose` introuvable | Vérifiez le paquet `docker-compose-plugin` (ex. : `dpkg -l` puis recherchez ce nom). |
| Proxy d'entreprise | Configurez le proxy pour `apt` et pour le *daemon* Docker selon la politique du réseau. |
| ARM64 (`aarch64`) | Le dépôt ci-dessus utilise `dpkg --print-architecture`, il se résout donc déjà vers `arm64` sans ajustement manuel — c'est exactement ce que ce projet utilise en production (AWS `t4g.micro`, Ubuntu 24.04.4, Docker `29.6.0`, paquets `docker-ce`/`docker-ce-cli`/`containerd.io` en `arm64`). Le seul véritable point d'attention est l'**image du compose**, pas Docker lui-même : vérifiez que chaque image publie un manifest `linux/arm64/v8` (ex. : `gradiant/open5gs` ne publie `arm64` que jusqu'à la tag `2.7.2` — voir [`core5g-arm64-bible.md` §8.1](../../../../core5g-arm64-bible.md#81--imagens-gradiantopen5gs-sem-build-arm64)) ; sans cela, `docker compose up` échoue avec `no matching manifest for linux/arm64/v8`. |

---

## Checklist

- [ ] `docker-ce`, `docker-compose-plugin` installés.
- [ ] `sudo systemctl status docker` → *running*.
- [ ] Utilisateur dans le groupe `docker` et session renouvelée.
- [ ] `docker compose version` répond avec *v2*.
- [ ] (Optionnel) `docker run --rm hello-world` se termine avec succès.

**Étape suivante :** [Guide 00 — GCP](00-pre-lab-gcp-vm-e-acesso.md) (s'il manque encore la VM/le clone) ou [01 — Core](01-core-open5gs.md).
