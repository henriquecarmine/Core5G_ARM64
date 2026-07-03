# Core5G ARM64

**🌐 [Português](README.md) · [English](README.en.md) · [Español](README.es.md) · Français**
<!-- sync: v0.34.0 -->

> 🌐 Traduction française de [README.md](README.md) — synchronisée avec **v0.34.0 (2026-07-03)**.
> Le portugais est la langue canonique ; les documents liés sont en portugais sauf mention contraire.

Laboratoire 5G complet fonctionnant sur **AWS Graviton (ARM64)**, avec son
propre tableau de bord web. Il réunit **deux projets** indépendants du cours
*RAN Intelligent Controller (RIC)* — CESAR School (thème du groupe :
**UE-TP-rApp**) :

| Projet | Stack | Dossier | Statut |
|---|---|---|---|
| **Projet 1** | Open5GS (5GC) + UERANSIM (gNB/UE simulés) | `server/` | ✅ Présenté le 13/06/2026, validé de bout en bout |
| **Projet 2** | OAI 5GC + gNB RFSIM + agent E2 + **FlexRIC** (near-RT RIC) + xApps | `server/oai-cn-gnb-e2/` | ✅ Présenté le 20/06/2026 |

**Phase actuelle (juil./2026) : article scientifique** — le Prof. Jonas rédige
l'article (Overleaf) et a demandé une liste de 8 améliorations de la plateforme
(02/07/2026). État : **7 sur 8 terminées** dans le panneau v0.34.x — topologie
avec bandes **CUPS** (plan de contrôle × plan utilisateur), interfaces
**N1/N11** explicites, disposition sans chevauchements, **thèmes clair/sombre**,
couleurs **ISO** dans tous les terminaux, annotations didactiques au démarrage
de chaque service, **sélecteur de langue (PT/EN/ES/FR)** et la
[politique de coûts](docs/POLITICA-DE-CUSTOS.md) (pt). Reste : i18n complet du
panneau au-delà de login/topbar.

> **Vous voulez juste comprendre le quoi/pourquoi ?** Lisez la
> [**bible du projet**](core5g-arm64-bible.md) (pt — référence conceptuelle
> complète). Pour l'historique chronologique, le [**CHANGELOG**](CHANGELOG.md)
> (pt). Pour les guides de TP, [`docs/labs/`](docs/labs/) (pt).
>
> Ce README est la **porte d'entrée** : comment reproduire l'état actuel, ce
> qu'il reste à faire et comment contribuer.

---

## 1. Comment arriver jusqu'ici (reproduction depuis zéro)

Le flux de travail : **tout en local, déploiement via `deploy.sh`**. On ne
modifie jamais les fichiers directement sur le serveur — on édite `server/` sur
sa machine et `deploy.sh` répercute sur le serveur via SSH/rsync.

### 1.1 Prérequis

- Un **compte AWS** avec une instance EC2 **ARM (Graviton)**, Ubuntu 22.04+.
  Recommandé : **`t4g.medium`** (2 vCPU, 4 Go) — la `t4g.micro` ne fait tourner
  que le Projet 1. Volume EBS de **30 Go**.
- Votre machine locale avec `bash`, `git`, `rsync`, `ssh` et `openssl`.
- Pour **construire** les images OAI arm64 : un **Mac Apple Silicon** (ou une
  autre machine arm64) avec Docker. Les images prêtes **ne sont pas dans git**
  (~362 Mo) — elles sont distribuées via le Google Drive du groupe.

### 1.2 Cloner et configurer

```bash
git clone https://github.com/henriquecarmine/Core5G_ARM64.git
cd Core5G_ARM64
cp .env.example .env
```

Éditez le `.env` (ne le committez jamais — il est dans le `.gitignore`) :

```ini
AWS_SERVER_HOST=core5g-arm64.duckdns.org   # domaine DuckDNS ou IP de l'instance
AWS_SERVER_USER=ubuntu
AWS_SSH_KEY_PATH=ssl/core5g_openran_arm64.pem   # votre clé SSH (.pem), JAMAIS dans git

DUCKDNS_DOMAIN=core5g-arm64                 # optionnel : IP dynamique automatique
DUCKDNS_TOKEN=<votre-token>

PANEL_USER=professor                        # Professeur (admin) — accès complet
PANEL_PASSWORD=<mot-de-passe-fort>
PANEL_GUEST_USER=guest                      # active l'accès Étudiant (lecture seule)
PANEL_GUEST_PASSWORD=<mdp-guest>            # optionnel (les étudiants entrent avec nom+e-mail)
PANEL_EXTRA_USERS=professor2:mdp2           # admins supplémentaires : user:mdp,user2:mdp2
```

> **Rôles (mode salle de classe) :** le *Professeur* opère (un **seul à la
> fois**) ; l'*Étudiant* suit en direct et entre avec **nom + e-mail** (sans mot
> de passe). Détails au §1.6.

### 1.3 Provisionner le serveur (une fois)

```bash
./deploy.sh bootstrap     # Docker + swap 8 Go + DuckDNS + Caddy (HTTPS) + panneau
```

Idempotent — exécutez-le autant de fois que nécessaire. À la fin, le panneau
répond sur `https://<votre-hôte>/` avec un TLS valide (Let's Encrypt via Caddy)
et un écran de connexion.

### 1.4 Projet 1 — Open5GS + UERANSIM

```bash
./deploy.sh up all        # démarre le Cœur 5G (Open5GS) + RAN (UERANSIM)
./deploy.sh status        # docker ps + healthcheck (N2/N3/N4/N6)
```

Validation de bout en bout : l'UE s'enregistre (5G-AKA), ouvre une PDU Session
et obtient une connectivité réelle (`ping -I uesimtun0 8.8.8.8` → 0 % de perte).
Tout cela est aussi exposé en boutons dans le panneau (UE Lab, Démonstration E2E).

### 1.5 Projet 2 — OAI + FlexRIC (E2)

Les images OAI arm64 doivent être chargées dans le Docker du serveur :

```bash
# (sur le Mac arm64) construire et exporter les 6 images — voir bible §7.b :
cd server/oai-cn-gnb-e2 && ./build-oai-arm64.sh        # AMF→SMF→NRF→UDR→UDM→AUSF
# exporte /tmp/oai-images/oai-*.tar (~60 Mo chacune). À déposer sur le Drive du groupe.

# envoyer le répertoire du Projet 2 (une fois, ~230 Mo) :
./deploy.sh sync-oai

# sur le serveur : docker load -i ~/oai-<comp>.tar  (chaque composant du Drive)
```

Une fois les images chargées, le lab E2 démarre **depuis le panneau** (sélecteur
de projet → *Projet 2*) ou via SSH :

```bash
./deploy.sh ssh
cd ~/server/oai-cn-gnb-e2
./scripts/up_e2_lab.sh           # Cœur OAI + nearRT-RIC + gNB(E2) + nrUE
./scripts/test_e2_sm.sh all      # exerce les 8 Service Models via xApps
```

> **Pourquoi `t4g.medium` ?** Le gNB/nrUE RFSIM sont gourmands en CPU. Sur
> 2 vCPU ils peuvent saturer et **geler l'instance**. Le garde-fou utilise
> **cgroup v2 cpuset** : le `bootstrap` crée la slice `oai-lab.slice` épinglée
> **hors du CPU 0** (`AllowedCPUs=1`), réservant un cœur au système
> (SSH/Docker/panneau/Caddy avec `CPUWeight` maximal). Le lab ne peut donc
> jamais faire tomber la machine. (Sur ce noyau ARM, `CPUQuota`/CFS n'est pas
> appliqué ; d'où le cpuset.) Détails dans
> [`infra/server-bootstrap.sh`](infra/server-bootstrap.sh).

### 1.6 Panneau web — mode salle de classe

`https://<votre-hôte>/` — le panneau est une SPA (FastAPI + HTML/CSS/JS, sans
build). Fonctions de base : télémétrie en direct, logs filtrés/colorés
(ANSI/ISO) avec **explication didactique** à la fin, UE Lab, Démonstration E2E,
**sélecteur de projet** (en démarrer un éteint l'autre), **topologie
interactive** (conteneurs/ports/réseaux réels, cliquables) et les tests de
Service Model E2 — chacun avec un **résumé final**. Interface en **4 langues**
(PT/EN/ES/FR, sélecteur 🌐) et **thèmes clair/sombre**.

Par-dessus, un **mode salle de classe** conçu pour présenter à un auditoire :

- **Rôles Professeur / Étudiant.** Le *Professeur* (admin) opère ; l'*Étudiant*
  (invité) suit en lecture seule, en entrant avec **nom + e-mail** (1 clic, sans
  mot de passe) — l'e-mail sert de **registre de présence** du groupe.
- **Un Professeur à la fois.** La place est « collante » : un 2ᵉ admin est
  bloqué jusqu'à ce que l'actuel se déconnecte ou reste inactif 10 min.
- **Miroir EN DIRECT.** Tout ce que le Professeur exécute est retransmis en
  temps réel aux Étudiants (console + écran ouvert), via ring-buffer + polling.
- **Résultats + Replay.** Chaque exécution est sauvegardée sur disque (survit
  aux redémarrages) et peut être **rejouée** ligne par ligne.
- **RAN en direct (P2).** Sparklines avec SNR/MCS/PRB/BLER réels du gNB OAI.
- **Mode projection (kiosque).** Bouton « ⛶ Projection » → écran épuré en plein
  écran pour le vidéoprojecteur.
- **Qui regarde.** Le Professeur clique sur le badge « 👁 N étudiants » pour voir
  la liste des connectés et la présence.

---

## 2. Ce qu'il reste à faire (feuille de route)

| Quand | Élément | État |
|---|---|---|
| **Court terme** | **i18n complet du panneau — pt/en/es/fr** au-delà de login/topbar (phases F2 index, F3 topologie, F4 scripts bash via `LAB_LANG`) | ⏳ F1 livrée (v0.34.0) |
| Court terme | xApp **UE-TP-rApp** (prédiction de débit par UE) — thème du groupe. Wheels **scikit-learn aarch64** déjà intégrés (`server/panel/vendor/`) | ⏳ Il manque le modèle |
| 🧱 **Blocage HW** | **Le lab RIC (Near/Non-RT) avec IA et le rapport KPM avec débit réel exigent 4 vCPU.** Analyse de coût et runbook du redimensionnement réversible : [`docs/POLITICA-DE-CUSTOS.md`](docs/POLITICA-DE-CUSTOS.md) §3 (pt) | ⚠️ En attente d'approbation |
| ✅ Résolu | **Checklist de l'article, points 2–7 + thèmes** (Prof. Jonas, 02/07/2026) | ✅ v0.32.0–0.33.1 |
| ✅ Résolu | **Politique de coûts** (point 8) + hygiène du disque (3,1 → 8,6 Go libres) | ✅ (pt) |
| ✅ Résolu | **Plan utilisateur de l'UE sur le Projet 2** (cœur v2.2.1) | ✅ Validé le 22/06 |
| Moyen terme | Capteur de protocole E2/NGAP/GTP-U dans le panneau | 📋 Prévu |
| Moyen terme | Persister les symlinks FlexRIC dans le `bootstrap` | 📋 Prévu |
| Un jour | Signaler les bugs du §8 de la bible au dépôt OAI amont | 📋 Prévu |

La liste canonique et détaillée vit dans la [bible §10](core5g-arm64-bible.md#10-pendências--próximos-passos) (pt).

---

## 3. Contribuer

Les contributions du groupe (et de quiconque étudie le lab) sont les bienvenues.
Le guide complet est dans **[`CONTRIBUTING.md`](CONTRIBUTING.md)** (pt) :

- **[Issues](../../issues)** — signaler un bug, proposer une idée, poser une question.
- **[Discussions](../../discussions)** — discuter / demander « comment fonctionne X ».
- **Pull Request** — *fork* → branche → PR décrivant *ce qui a changé et pourquoi*.

Règles d'or : éditez **toujours en local** (`deploy.sh` est le seul chemin vers
le serveur) ; **les secrets n'entrent jamais dans git** (`.env`, `ssl/*.pem`) ;
**les données des étudiants** (e-mails/liste) restent uniquement sur le serveur.
Les traductions doivent garder les 4 langues en parité (`npm run test:i18n` et
le vérificateur de docs).

**Accès collaborateur, ou les images OAI arm64 du Drive ?** Contactez-moi :

- **Henrique Carmine** — [henriquecarmine@gmail.com](mailto:henriquecarmine@gmail.com) ·
  [@henriquecarmine](https://github.com/henriquecarmine)

---

## 4. Carte du dépôt

```
.
├── README.md                  ← porte d'entrée (pt ; variantes en/es/fr à côté)
├── LICENSE                     ← licence MIT
├── CONTRIBUTING.md            ← comment contribuer (pt)
├── core5g-arm64-bible.md      ← référence conceptuelle complète (pt)
├── CHANGELOG.md               ← journal chronologique (pt)
├── deploy.sh                  ← point d'entrée unique du déploiement (local → serveur)
├── .env.example               ← modèle de configuration (copier vers .env)
├── .github/                   ← modèles d'Issue et de Pull Request
├── docs/                      ← blueprint du panneau + guides de TP
│   ├── POLITICA-DE-CUSTOS.md  ← coûts, règles d'exploitation et upgrade CPU
│   ├── i18n/                  ← docs traduits (miroirs en/es/fr)
│   └── relatorios-didaticos.md ← guide dev : fonctionnement des tests/rapports
├── infra/                     ← bootstrap du serveur + unité systemd du panneau
└── server/                    ← tout ce qui tourne sur le serveur
    ├── panel/                 ← panneau web (FastAPI) — voir panel/README.md
    │   ├── test/              ← tests headless (loaders, topologie/thèmes, i18n)
    │   └── vendor/            ← wheels aarch64 de scikit-learn (lab RIC + IA)
    ├── ueransim/              ← RAN simulée (Projet 1)
    ├── scripts/               ← démo E2E, bascule de projet, lib de logs ISO
    └── oai-cn-gnb-e2/         ← Projet 2 (OAI + FlexRIC + xApps)
```

---

## 5. Équipe

- **Coordination (encadrement) :** Prof. Dr. Jonas Augusto Kunzler — [jak@cesar.school](mailto:jak@cesar.school)
- **Développement et maintenance :** Henrique Carmine — expert en criminalistique
  numérique (gouvernance TI & télécoms), étudiant en master Open RAN sous la
  direction du Prof. Jonas Kunzler —
  [henriquecarmine@gmail.com](mailto:henriquecarmine@gmail.com) ·
  [@henriquecarmine](https://github.com/henriquecarmine)

Projet **coordonné par le Prof. Dr. Jonas Augusto Kunzler** et **maintenu par
Henrique Carmine**. CESAR School · cours *RAN Intelligent Controller (RIC)* ·
thème **UE-TP-rApp**. Licence **[MIT](LICENSE)**.

---

## 6. Soutenir ce projet

Ce laboratoire reste **en ligne 24 h/24, 7 j/7** sur un serveur ARM chez AWS,
payé de la poche du mainteneur — pour que chacun puisse étudier la 5G/O-RAN,
l'utiliser en cours ou en recherche. Le maintenir en ligne a un coût mensuel réel.

Si le projet vous a été utile, **tout montant aide à garder le serveur allumé** 🙏

> **PIX (Brésil) :** `henrique@titannium.us` (clé e-mail)

Merci du fond du cœur — chaque aide garde le lab disponible pour la personne
suivante.
