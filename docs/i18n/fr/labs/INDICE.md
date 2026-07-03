<!-- sync: e8f9da69 -->
> 🌐 Traduction en **français** du document canonique en portugais [`docs/labs/INDICE.md`](../../../labs/INDICE.md). Toutes les langues : [INDEX](../INDEX.md) · synchronisation vérifiée par `docs/i18n/check-parity.py`.

# Travaux pratiques — Open5GS + UERANSIM (Interfaces et protocoles)

Guides pour une exécution en salle ou de manière autonome et pour l'élaboration du **rapport de rendu**.

| Document | Contenu |
|-----------|----------|
| [**Vidéos du laboratoire**](video_seq_report.md) | Série GCP (3 épisodes) et **vidéo complète locale** — [walkthrough 01–03 + Wireshark](https://youtu.be/ic3_CIllb9o) |
| [00 — Pré-lab GCP, SSH et VM](00-pre-lab-gcp-vm-e-acesso.md) | Créer la VM, accès, firewall / WebUI (parcours cloud) |
| [00 — Installation Docker (Ubuntu)](00-docker-instalacao-ubuntu.md) | Docker Engine et Docker Compose v2 sur la VM |
| [01 — Infrastructure et Core 5GC (Open5GS)](01-core-open5gs.md) | Docker, démarrage du core, abonné, WebUI, vérifications initiales |
| [02 — UERANSIM : N2/N3 et test E2E](02-ueransim-n2-n3-e2e.md) | gNB + UE en conteneur, NGAP, GTP-U, tests et captures N3/N6 |
| [03 — Rapport, rendu et évaluation](03-relatorio-entrega-avaliacao.md) | Quoi rendre, preuves obligatoires, barème |
| [OAI Core arm64 — Build manuel](../../../../server/oai-cn-gnb-e2/docs/OAI-CORE-ARM64.md) | Compiler les images OAI pour arm64 : prérequis, pas à pas, 5 bugs résolus |
| [OAI Core v2.2.1 — user plane arm64](../../../../server/oai-cn-gnb-e2/oai-cn5g-v2/README.md) | Plan utilisateur réel sur arm64 (`oai-upf` simple_switch) : démarrer, valider, rollback |
| [Bible §7.c — user plane v2.2.1 + xApps event-driven](../../../../core5g-arm64-bible.md) | Démarrer core v2 + RIC + gNB, exécuter des xApps déterministes, restriction de 2 vCPUs |

**Prérequis :** Linux avec Docker et Docker Compose v2, utilisateur ayant la permission `docker` (et éventuellement `sudo` pour `sysctl` à l'initialisation du core et pour `tcpdump` sur l'*hôte*, si vous réalisez des captures avancées).

**Racine du projet (convention dans les commandes) :** `open5gs-containerized/` — ajustez les `cd` si votre clone se trouve dans un autre chemin (ex. : `code/open5gs-containerized`).

**Référence technique :** [README.md](../../../../README.md), [core/docs/CORE.md](../../../../core/docs/CORE.md), [ueransim/docs/RAN.md](../../../../ueransim/docs/RAN.md).
