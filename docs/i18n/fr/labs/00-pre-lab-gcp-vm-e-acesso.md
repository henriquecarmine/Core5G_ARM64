<!-- sync: e8f9da69 -->
> 🌐 Traduction en **français** du document canonique en portugais [`docs/labs/00-pre-lab-gcp-vm-e-acesso.md`](../../../labs/00-pre-lab-gcp-vm-e-acesso.md). Toutes les langues : [INDEX](../INDEX.md) · synchronisation vérifiée par `docs/i18n/check-parity.py`.

# Pré-lab — VM sur GCP, accès SSH et Docker (enregistrement / démonstration)

Ce guide couvre la **création de la machine virtuelle sur Google Cloud**, **deux modes d'accès par terminal** et la **passerelle vers le code du lab**. L'**installation de Docker** se trouve dans le guide dédié [Installation Docker — Ubuntu](00-docker-instalacao-ubuntu.md).

**Public :** ceux qui vont **enregistrer une vidéo** ou mener le lab pour la première fois sur GCP.

**À ne pas confondre avec le Cloud Shell (`>_` en haut de la Console) :** le laboratoire Open5GS + UERANSIM exige une **VM dédiée** avec Docker ; le Cloud Shell n'est pas l'environnement recommandé pour cette stack.

---

## 1. Deux options viables d'accès au shell de la VM


| Option                                   | Description                                                                                                                      | Quand l'utiliser dans la vidéo                                                                                                                                                                   |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A — SSH dans le navigateur**                | Dans la Console GCP → Compute Engine → VM → bouton **SSH** : ouvre un terminal dans le navigateur relié à la VM.                               | **Parcours minimal :** ne nécessite d'installer ni logiciel sur le PC ni `gcloud` ; idéal pour les débutants.                                                                                                  |
| **B — `gcloud compute ssh` (optionnel)** | Terminal local avec le [Google Cloud SDK](https://cloud.google.com/sdk/docs/install), `gcloud auth login` et projet configuré. | Pour ceux qui utilisent déjà `gcloud` et préfèrent une fenêtre de terminal local (police, *copier-coller*). **Non obligatoire** pour terminer le lab si vous suivez l'Option A et l'une des méthodes de la section 7 sans SDK. |


Dans les deux cas, vous êtes dans un shell **à l'intérieur de la VM** ; la seule différence est le **client** (navigateur vs `gcloud`).

---

## 2. Prérequis sur GCP (avant de créer la VM)

1. Compte Google avec **facturation** activée sur le projet (Compute Engine facture la VM en cours d'exécution).
2. Projet GCP créé ; notez l'**ID du projet** (ex. : `meu-projeto-lab`).
3. API **Compute Engine** activée (la Console propose généralement « Activer » la première fois que vous ouvrez Compute Engine).

**Astuce pour la démonstration :** utilisez un projet de laboratoire et **arrêtez ou supprimez la VM** à la fin pour éviter des coûts continus.

---

## 3. Créer la VM (configuration suggérée)

Dans la Console : **Compute Engine → Instances de VM → Créer une instance**.

Suggestion alignée sur les labs (Docker, plusieurs images, core + UERANSIM) :


| Champ                   | Valeur suggérée                                                                                                                                                                         |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Nom                    | Ex. : `lab-open5gs`                                                                                                                                                                     |
| Région / zone           | Choisissez une zone proche (ex. : `southamerica-east1-a`) ; si vous utilisez `gcloud` ensuite, conservez la **même zone** dans les commandes.                                                               |
| Série / type de machine | **T2A** (Tau T2A, ARM `aarch64`), **4 vCPU**, **8–16 GiB** de mémoire (16 GiB réduit le risque d'échec du *pull* / *compose*). Équivalent AWS validé dans ce projet : **EC2 `t4g.micro`** (Graviton2 / Neoverse-N1) — voir §4 de la [Bible du projet](../../../../core5g-arm64-bible.md). |
| OS                      | **Ubuntu 22.04 LTS** ou **24.04 LTS**, image **`aarch64`** (sur GCP, la famille **T2A** fournit déjà Ubuntu ARM ; dans la Console AWS, choisissez l'AMI marquée **arm64**).                          |
| Disque de démarrage  | **50–80 GB** équilibré ou SSD (les images Docker occupent beaucoup d'espace).                                                                                                                |
| Firewall               | **Autoriser HTTP/HTTPS** est optionnel. Pour ouvrir la WebUI sur **internet sans `gcloud`** (section 7.1), vous créerez une **règle de firewall** uniquement pour le port **9999** (et des étiquettes sur la VM). |


Créez l'instance et attendez l'état **En cours d'exécution**.

**Pourquoi ARM et pas x86_64 :** ce projet a été initialement écrit en pensant à une VM **x86_64** (`E2`/`N2`), mais il a été adapté et **validé de bout en bout sur une instance ARM réelle** (AWS `t4g.micro`, Ubuntu 24.04.4 LTS, kernel `6.17`, Docker `29.6.0` — paquets `arm64`). Utilisez ARM (`T2A` sur GCP, `t4g`/`t4g.micro`+ sur AWS) comme guide principal : c'est moins cher et déjà confirmé fonctionnel sans émulation. Seul véritable point d'attention rencontré : **images Docker sans build `arm64`** — voir le bug documenté dans [`core5g-arm64-bible.md` §8.1](../../../../core5g-arm64-bible.md#81--imagens-gradiantopen5gs-sem-build-arm64) (épingler `gradiant/open5gs`/`gradiant/open5gs-webui` à la tag `2.7.2`, déjà reflété dans `server/.env`). Si une image de votre `docker compose` n'a pas de manifest `arm64`, c'est le symptôme à rechercher — ce n'est pas une raison pour revenir à x86_64 par défaut.

---

## 4. Option A — Ouvrir un terminal via SSH dans le navigateur

1. **Compute Engine → Instances de VM**.
2. Sur la ligne de la VM, cliquez sur **SSH** (ou **Connecter** → SSH dans le navigateur).
3. Une fenêtre/un onglet s'ouvre avec un terminal déjà authentifié.

**Première connexion :** il peut y avoir un délai pendant la configuration des clés.

---

## 5. Option B — Terminal local avec `gcloud compute ssh` (optionnel)

1. Installez le [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) et exécutez :

```bash
gcloud auth login
gcloud config set project SEU_PROJECT_ID
```

1. Connectez-vous (remplacez `NOME_DA_VM` et `ZONA`) :

```bash
gcloud compute ssh NOME_DA_VM --zone=ZONA
```

1. La première fois, confirmez l'empreinte du host si `gcloud` le demande.

À partir d'ici, les commandes sont **identiques** à celles de l'Option A (tout s'exécute sur la VM).

---

## 6. Sur la VM — Docker Engine et Compose v2

Exécutez **sur la VM** le guide complet : **[00 — Installation Docker (Ubuntu)](00-docker-instalacao-ubuntu.md)** (dépôt officiel via `apt`, groupe `docker`, vérification et test optionnel `hello-world`).

Ensuite, vérifiez rapidement (utile dans la vidéo et dans le rapport du Guide 01) :

```bash
docker --version
docker compose version
uname -a
```

---

## 7. WebUI sur le port 9999 — sans exiger `gcloud` sur le laptop

Sur la VM, la WebUI du lab répond sur `http://127.0.0.1:9999`. Le **SSH dans le navigateur** n'ouvre pas de navigateur graphique à l'intérieur de la VM ; pour voir l'interface sur **votre ordinateur**, utilisez l'une des options ci-dessous. En combinant l'**Option A** (SSH dans le navigateur) avec **7.1, 7.2 ou 7.3**, vous couvrez le lab en utilisant uniquement la Console GCP et le terminal dans le navigateur, **sans** installer le Google Cloud SDK sur le laptop.

### 7.1 Règle de firewall + IP externe (tout par la Console GCP)

Recommandé pour une **démo en salle** ou un enregistrement, à condition d'accepter d'exposer le port (atténuez avec une origine restreinte ou une VM temporaire).

1. Notez l'**IP externe** de la VM (Compute Engine → instances).
2. **VPC network → Firewall → Create firewall rule :**
  - **Targets :** « Specified target tags » ; tag exemple : `open5gs-webui`.
  - Sur l'**instance**, dans « Modifier » → **Tags réseau**, ajoutez le même tag (`open5gs-webui`).
  - **Source IP ranges :** en laboratoire fermé, cela peut être votre IP (`x.x.x.x/32`) ; **n'**utilisez **pas** `0.0.0.0/0` en production (n'importe qui sur internet accéderait à la WebUI).
  - **Protocols and ports :** TCP **9999**.
3. Avec le core actif, dans le navigateur du laptop : `http://IP_EXTERNO:9999`.

**Sécurité :** les identifiants par défaut de la WebUI sont connus ; traitez la VM comme **jetable** et supprimez la règle ou la VM après le lab.

### 7.2 Tunnel HTTPS depuis la VM (sans ouvrir de port dans le VPC)

Toujours dans le SSH du navigateur, sur la VM, vous pouvez publier `localhost:9999` via un service de tunnel (ex. : [Cloudflare Tunnel (*quick tunnel*)](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/do-more-with-tunnels/trycloudflare/) ou [ngrok](https://ngrok.com/)). Le fournisseur renvoie une **URL HTTPS** ; ouvrez-la sur le laptop — **ni** `gcloud` **ni** règle de firewall pour le 9999 ne sont nécessaires.

- Lisez les conditions et limites du service ; en cours, préférez 7.1 avec IP restreinte ou une VM dédiée au lab.

### 7.3 Sans WebUI dans la vidéo — terminal uniquement

Le Guide 01 permet de créer l'abonné avec `**./scripts/add-subscriber.sh`** (aligné sur `ue.yaml`). Rien n'empêche de compléter les preuves sans ouvrir le navigateur ; mentionnez dans le rapport que vous avez utilisé l'option par script.

### 7.4 Optionnel — redirection locale avec `gcloud` (pour ceux qui utilisent déjà le SDK)

Si vous avez installé le Cloud SDK et préférez ne pas exposer le 9999 sur internet :

```bash
gcloud compute ssh NOME_DA_VM --zone=ZONA -- -L 9999:127.0.0.1:9999 -N
```

Gardez cette session ouverte ; dans un autre terminal, `gcloud compute ssh` sans `-N` pour les commandes. Sur le laptop : `http://localhost:9999`.

### 7.5 Avancé — SSH local avec `-L` (sans la sous-commande `gcloud ssh`)

Si vous configurez une **clé SSH** dans les métadonnées de la VM ou OS Login et vous connectez avec `ssh usuário@IP_EXTERNO`, vous pouvez utiliser :

```bash
ssh -L 9999:127.0.0.1:9999 usuario@IP_EXTERNO
```

(Les détails de l'utilisateur et de la clé dépendent de l'image Ubuntu de GCP ; l'Option A de la Console est généralement plus simple.)

**Tunnel SSH inversé** (`ssh -R`) n'est pratique que s'il existe un serveur SSH **joignable sur internet** ou un VPN (ex. : une autre VM fixe) ; c'est pourquoi ce n'est pas la voie principale de ce guide.

---

## 8. Obtenir le code du laboratoire sur la VM

Exemple avec `git` (ajustez l'URL vers le dépôt officiel du cours) :

```bash
sudo apt-get update
sudo apt-get install -y git
cd ~
git clone https://github.com/jakunzler/cesar-school-repo.git
cd cesar-school-repo/oran/code/open5gs-containerized
```

Vérifiez que les dossiers `core/` et `ueransim/` existent et que les scripts ont la permission d'exécution (`chmod +x` sur les `.sh` si nécessaire).

---

## 9. Déroulé de la vidéo (suggestion d'ordre)

1. Console GCP : projet, créer la VM, **SSH dans le navigateur** (Option A) en 30–60 s.
2. **Parcours sans `gcloud` :** restez dans le SSH du navigateur pour Docker, le clone et les commandes des guides 01/02 ; pour la WebUI, utilisez **7.1** (firewall + IP) ou **7.2** (tunnel sur la VM) ou **7.3** (uniquement `add-subscriber.sh`). **Parcours avec SDK :** montrez éventuellement `gcloud compute ssh` (Option B) pour le long bloc de commandes.
3. `docker --version`, `docker compose version`, `uname -a`.
4. Suivre [01-core-open5gs.md](01-core-open5gs.md) jusqu'à un core stable + abonné + WebUI **ou** script d'abonné (selon la section 7).
5. Suivre [02-ueransim-n2-n3-e2e.md](02-ueransim-n2-n3-e2e.md) avec le core déjà actif.
6. Mentionner [03-relatorio-entrega-avaliacao.md](03-relatorio-entrega-avaliacao.md) comme document de **rendu** (et non comme étape d'exécution sur la VM).

---

## 10. Une fois l'environnement prêt — que faire ensuite ?

- **Oui :** avec Docker installé et le dépôt cloné sur la VM, vous suivez le **Guide 01** (core) puis le **Guide 02** (UERANSIM), dans l'ordre des fichiers [01-core-open5gs.md](01-core-open5gs.md) et [02-ueransim-n2-n3-e2e.md](02-ueransim-n2-n3-e2e.md).
- Le fichier **[03 — Rapport, rendu et évaluation](03-relatorio-entrega-avaliacao.md)** n'est pas une troisième « étape de laboratoire » dans le terminal : il décrit **quoi rendre** (PDF/annexes) et les critères. Flux typique : **00 (ce document, une fois) → 01 → 02 → élaboration du rapport selon 03**.

---

## Checklist rapide (enseignant / personne qui enregistre)

- VM Ubuntu **`aarch64`/ARM** (famille `T2A` sur GCP ; `t4g` sur AWS — validé dans ce projet), RAM et disque suffisants.
- SSH testé (navigateur ; `gcloud` uniquement si vous utilisez l'Option B).
- Docker + Compose v2 fonctionnels sans sudo.
- Clone du dépôt dans le chemin attendu par les guides 01/02.
- Plan pour la WebUI : firewall **9999** (7.1), tunnel sur la VM (7.2), `add-subscriber.sh` (7.3) ou `-L` avec `gcloud`/`ssh` (7.4–7.5).
- Plan pour éteindre ou supprimer la VM après l'enregistrement.

**Références :** [INDICE.md](INDICE.md), [README.md](../../../../README.md).
