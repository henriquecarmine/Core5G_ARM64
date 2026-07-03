<!-- sync: e8f9da69 -->
> 🌐 Traduction en **français** du document canonique en portugais [`docs/labs/video_seq_report.md`](../../../labs/video_seq_report.md). Toutes les langues : [INDEX](../INDEX.md) · synchronisation vérifiée par `docs/i18n/check-parity.py`.

# Série vidéo — exécution du laboratoire Open5GS + UERANSIM

Cette page regroupe les vidéos de support du lab. Il existe **deux formats** :


| Format                              | Public cible                                                                                                                        | Contenu                                                                                                   |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **Série courte (1–3)** ci-dessous   | Ceux qui montent l'environnement sur **GCP** par étapes                                                                             | VM, Docker, démarrage E2E résumé.                                                                        |
| **Vidéo unique — laboratoire local** | Ceux qui exécutent sous **Linux local** (ou VM déjà prête) et veulent tout voir **d'un seul coup**, y compris **Wireshark** et les **outils réseau** | Équivalent aux guides écrits **01 → 02 → 03** (core, UERANSIM/captures, finalisation pour le rapport). |


Les `.md` restent la référence pour les commandes exactes, les preuves et la rubrique ; les vidéos montrent le flux en pratique.

---

## Comment utiliser cette séquence

1. **Parcours GCP :** regardez les épisodes **1 → 2 → 3** dans l'ordre (chaque étape suppose la précédente).
2. **Parcours local complet :** utilisez la [vidéo complète](#video-lab-completo-local) comme vue intégrée ; revenez aux guides 01–03 pour copier les commandes et constituer les annexes.
3. Ayez le dépôt cloné et les guides ouverts dans un autre onglet.
4. Mettez en pause et reproduisez les mêmes commandes dans votre terminal (si possible) — l'objectif n'est pas seulement de « voir », mais de **répliquer** et d'enregistrer des preuves pour le [rapport de remise](03-relatorio-entrega-avaliacao.md).

---

## Épisodes


| #     | Thème                            | Ce que vous devez réussir à la fin                                                                                                               | Guide écrit associé                                                                                                          |
| ----- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **1** | **VM sur GCP**                   | Créer/accéder à une VM adaptée au lab (SSH, ressources, notion de pare-feu).                                                                    | [Pré-lab — GCP, SSH et pont vers le code](00-pre-lab-gcp-vm-e-acesso.md)                                                     |
| **2** | **Docker sur la VM**             | Installer Docker et Docker Compose v2 ; `docker run hello-world` (ou équivalent) fonctionnel.                                                   | [Installation Docker — Ubuntu](00-docker-instalacao-ubuntu.md)                                                              |
| **3** | **Système 5G de bout en bout**   | Démarrer core + RAN, abonné cohérent avec l'UE, vérifications de santé et notion de N2/N3/E2E.                                                  | [Guide 01 — Core](01-core-open5gs.md) · [Guide 02 — UERANSIM / E2E](02-ueransim-n2-n3-e2e.md)                               |
| **★** | **Laboratoire complet (local)**  | Parcourir les **guides 01 à 03** en une seule session ; **tcpdump** / **Wireshark** (N2/N3) ; `ping` / routes / `docker` ; finalisation alignée sur le rapport. | [01](01-core-open5gs.md) · [02](02-ueransim-n2-n3-e2e.md) · [03 — Rapport et preuves](03-relatorio-entrega-avaliacao.md) |


### 1) VM sur GCP (`setup_vm_gcp`)

**Vidéo :** [youtu.be/67Xey5GV1G4](https://youtu.be/67Xey5GV1G4)

Idéal pour ceux qui n'ont pas encore la machine du laboratoire. Faites attention à la **zone**, à la **taille de la VM** (CPU/RAM/disque) et à **comment ouvrir le terminal** (SSH dans le navigateur vs `gcloud`), en cohérence avec le pré-lab.

---

### 2) Installation de Docker (`installing_docker_gcp`)

**Vidéo :** [youtu.be/76TMQdSAXSw](https://youtu.be/76TMQdSAXSw)

Se concentre sur l'environnement Ubuntu de la VM. Confirmez dans votre terminal :

```bash
docker --version
docker compose version
```

Si quelque chose échoue ici, résolvez-le **avant** de démarrer Open5GS.

---

### 3) Système 5G E2E (`running_5G_system_e2e`)

**Vidéo :** [youtu.be/dgGzGDYYE_c](https://youtu.be/dgGzGDYYE_c)

Couvre le flux complet (core, abonné, UERANSIM, vérifications). En le regardant, comparez avec :

- l'ordre **core → abonné → RAN** dans les guides 01 et 02 ;
- la nécessité que l'**IMSI dans MongoDB** coïncide avec le `supi` dans `ueransim/configs/ue.yaml` ;
- les scripts `core/scripts/up_core.sh`, `core/scripts/add-subscriber.sh` (ou équivalent), `ueransim/scripts/up_ran.sh` et `core/scripts/healthcheck.sh`.

---

### ★) Laboratoire complet — local (`full_lab_local_wireshark`)

**Vidéo :** [youtu.be/ic3_CIllb9o](https://youtu.be/ic3_CIllb9o)

Même contenu que celui décrit dans la [section détaillée ci-dessous](#video-lab-completo-local) ; utilisez-la comme référence unique si vous préférez une seule session enregistrée (Linux local ou VM déjà avec Docker).

---



## Vidéo complète — exécution locale (guides 01 à 03, Wireshark et réseau)

Enregistrement **unique** en environnement **local** (machine Linux ou VM avec Docker déjà utilisable), parcourant le même contenu que les guides écrits **du début jusqu'à la finalisation pour la remise**, avec un accent sur la **visibilité de protocole** et les **commandes réseau**.

**Vidéo :** [Laboratoire complet — guides 01 à 03 (Wireshark et réseau)](https://youtu.be/ic3_CIllb9o)

### Ce que la vidéo couvre (aperçu rapide)


| Phase                    | Guide écrit                                                            | Sujets typiques dans la vidéo                                                                                                                                                                                                                                             |
| ------------------------ | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **01 — Core**            | [01-core-open5gs.md](01-core-open5gs.md)                               | Nettoyage optionnel, `up_core`, MongoDB / abonné aligné sur `ue.yaml`, WebUI, `healthcheck.sh`, connectivité de base entre conteneurs.                                                                                                                                   |
| **02 — UERANSIM et réseau** | [02-ueransim-n2-n3-e2e.md](02-ueransim-n2-n3-e2e.md)               | `up_ran`, logs du `ueransim`, **capture sur l'hôte** avec `tcpdump` (ex. : SCTP **38412** pour N2, UDP **2152** pour GTP-U / N3), ouverture des PCAP dans **Wireshark** avec les filtres `sctp.port == 38412` et `udp.port == 2152`, tests avec `ping` / routes lorsque le guide le demande. |
| **03 — Rapport**         | [03-relatorio-entrega-avaliacao.md](03-relatorio-entrega-avaliacao.md) | Comment relier les *captures d'écran*, logs et PCAP aux preuves **E1–E11** ; structure suggérée du PDF ; ce qui compte comme annexe minimale.                                                                                                                            |


### Outils qui apparaissent souvent

- **Docker / Compose** — démarrage du core et du RAN, `docker ps`, `docker logs`, `docker exec` (ex. : `ip addr`, `ping` depuis l'UE/le conteneur).
- **tcpdump** sur l'*hôte* — interfaces `docker0`, `br-`* ou `any`, selon le [guide 02](02-ueransim-n2-n3-e2e.md) (NGAP sur SCTP, GTP-U).
- **Wireshark** — dissection NGAP sur N2 et GTP-U sur N3 ; *captures d'écran* avec **filtre visible** pour le rapport ([critères dans le guide 03](03-relatorio-entrega-avaliacao.md)).
- **Scripts du dépôt** — `healthcheck.sh`, `test-system-status.sh`, `test_ue_connection.sh` (lorsque applicable à votre clone).

### Différence par rapport aux épisodes 1–3 (GCP)

La série **1–3** ci-dessus se concentre sur la **création de la VM sur GCP** et l'installation de Docker. La **vidéo complète locale** suppose que le système d'exploitation et Docker sont déjà OK et approfondit les **guides 01–03**, les **captures** et la **remise** — utile pour ceux qui travaillent sur leur propre ordinateur portable ou disposent déjà d'une VM provisionnée.

---

## Mini checklist (après la série)

Cochez mentalement (ou dans le rapport) ce qui est déjà valide dans **votre** environnement :

- VM GCP accessible par SSH et avec suffisamment de ressources pour Docker + plusieurs images.
- `docker` et `docker compose` fonctionnent sans erreur.
- Core Open5GS en cours d'exécution et NF saines (selon le guide 01 / `healthcheck.sh`).
- Abonné enregistré et **aligné** sur `ue.yaml`.
- UERANSIM actif, NG setup et, lorsque applicable, interface `uesimtun0` / IP de données selon le guide 02.
- *(Si vous avez suivi la vidéo complète locale)* PCAP ou *capture d'écran* Wireshark avec N2 et/ou N3 alignés sur le [guide 02](02-ueransim-n2-n3-e2e.md) et sur la rubrique du [guide 03](03-relatorio-entrega-avaliacao.md).

---

**Indice général des labs :** [INDICE.md](INDICE.md).