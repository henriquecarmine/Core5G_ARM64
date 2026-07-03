# Documentation traduite — fr

> Miroir de la documentation canonique en portugais. Un fichier ici reproduit
> `<racine-du-dépôt>/<chemin>` ou `<racine-du-dépôt>/docs/<chemin>`. Chaque
> traduction porte un marqueur `<!-- sync: <hash> -->` en tête, vérifié par
> `docs/i18n/check-parity.py` (qui signale les orphelins et les traductions en
> retard sur l'historique git canonique).

## Travaux pratiques et exercices

Traduction française complète des guides de TP. Le glossaire 3GPP/O-RAN (AMF,
CUPS, E2SM-KPM, N1/N2/N3…) est conservé tel quel dans les spécifications — seule
l'explication autour est traduite. Le code, les commandes, les chemins de fichier
et les URL restent inchangés.

**Projet 1 — Open5GS + UERANSIM**

| Guide | Contenu |
|-------|---------|
| [Index](labs/INDICE.md) | Carte des guides de TP |
| [00 — Installation de Docker (Ubuntu)](labs/00-docker-instalacao-ubuntu.md) | Docker Engine + Compose v2 sur la VM |
| [00 — Pré-TP : GCP, SSH et VM](labs/00-pre-lab-gcp-vm-e-acesso.md) | Parcours cloud : VM, accès, pare-feu/WebUI |
| [01 — Cœur 5GC (Open5GS)](labs/01-core-open5gs.md) | Démarrer le cœur, l'abonné, la WebUI, vérifications |
| [02 — UERANSIM : N2/N3 et E2E](labs/02-ueransim-n2-n3-e2e.md) | gNB + UE, NGAP, GTP-U, tests, captures N3/N6 |
| [03 — Rapport, remise et évaluation](labs/03-relatorio-entrega-avaliacao.md) | Livrables, preuves obligatoires, barème |
| [Vidéos du TP](labs/video_seq_report.md) | Index des vidéos (les vidéos sont narrées en portugais) |

**Projet 2 — OAI 5GC + gNB + FlexRIC**

| Guide | Contenu |
|-------|---------|
| [Tutoriel du TP E2](server/oai-cn-gnb-e2/docs/TUTORIAL_LAB_E2.md) | Cœur OAI + near-RT RIC + gNB (E2) + xApps, de bout en bout |

## READMEs

Les quatre README de la racine : [README.fr.md](../../../README.fr.md).

---

Le portugais canonique se trouve dans [`docs/labs/`](../../labs/) et
[`server/oai-cn-gnb-e2/docs/`](../../../server/oai-cn-gnb-e2/docs/). Envie d'aider
à traduire davantage (bible, guides) ? Voir CONTRIBUTING (§7, i18n).
