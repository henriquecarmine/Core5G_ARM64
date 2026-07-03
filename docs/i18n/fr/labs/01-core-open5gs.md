<!-- sync: e8f9da69 -->
> 🌐 Traduction en **français** du document canonique en portugais [`docs/labs/01-core-open5gs.md`](../../../labs/01-core-open5gs.md). Toutes les langues : [INDEX](../INDEX.md) · synchronisation vérifiée par `docs/i18n/check-parity.py`.

# Guide 01 — Infrastructure et Core 5G (Open5GS)

**Objectifs :** Comprendre la stack conteneurisée du laboratoire ; démarrer le **5GC SA** (Open5GS) **sans RAN** ; valider NRF, SCP, AMF, SMF, UPF, MongoDB et les données d'abonnement alignées sur l'UE.

**Durée indicative :** 45–60 min (première exécution, y compris le *pull* des images).

**Support vidéo :** [index des vidéos du lab](video_seq_report.md) (série GCP et [walkthrough complet](https://youtu.be/ic3_CIllb9o) avec core + RAN + Wireshark).

---

## 1. Préparation de l'environnement

Exécutez et **conservez la sortie** dans les annexes du rapport (ou collez-la dans un bloc de code / PDF).

```bash
docker --version
docker compose version
uname -a
```

**Preuve :** *capture d'écran* ou copier-coller des trois commandes.

Vérifiez que le *daemon* Docker est actif :

```bash
docker info
```

**Preuve :** premières 15–20 lignes de la sortie (sans données sensibles).

---

## 2. Nettoyage optionnel (en cas de répétition du lab)

Uniquement si vous avez déjà exécuté le laboratoire et souhaitez un état propre :

```bash
cd open5gs-containerized/ueransim && ./scripts/down_ran.sh 2>/dev/null || true
cd ../core && ./scripts/down_core.sh
```

Pour **supprimer les volumes MongoDB** (abonnés et base `open5gs` réinitialisés — vérifiez que vous n'avez pas besoin des données) :

```bash
cd open5gs-containerized/core
docker compose down -v
```

**Preuve :** non obligatoire ; mentionnez dans le rapport si vous avez fait un *reset* total avec `-v`.

---

## 3. Démarrage du Core

Le script `up_core.sh` peut demander **`sudo`** pour activer l'*IP forwarding* sur la machine hôte (*host*) — acceptez si c'est la politique de votre machine.

```bash
cd open5gs-containerized/core
./scripts/up_core.sh
```

Attendez la fin du script. En cas d'échec d'un NF, consultez [core/docs/CORE.md](../../../../core/docs/CORE.md) et la section *Troubleshooting* du [README](../../../../README.md).

**Commandes de vérification immédiate** (avec le *working directory* dans `core/`) :

```bash
docker compose ps
docker network inspect core_net-sbi --format '{{json .IPAM.Config}}'
docker network inspect core_net-n2 --format '{{json .IPAM.Config}}'
docker network inspect core_net-n3 --format '{{json .IPAM.Config}}'
```

> Le préfixe `core_` dans le nom du réseau correspond au nom du dossier où s'exécute `docker compose` (par défaut, le nom du projet est celui du répertoire : `core`).

**Preuves obligatoires :**

1. **Capture ou texte** de `docker compose ps` avec les services principaux **Up** (mongodb, nrf, scp, amf, smf, upf, webui, …).
2. Confirmation des sous-réseaux attendus : **SBI** `10.10.0.0/16`, **N2** `10.20.0.0/16`, **N3** `10.30.0.0/16` (commande ci-dessus ou `docker network ls | grep core_`).

---

## 4. Abonné (Subscriber)

L'**IMSI / SUPI** dans le cœur doit correspondre à celui défini dans `ueransim/configs/ue.yaml` (champ `supi`, par exemple `imsi-001010000000002`). Sinon, l'UE ne s'enregistre pas correctement au Guide 02.

**Option A — WebUI (recommandé) :**

- URL : [http://localhost:9999](http://localhost:9999)
- Identifiants par défaut : `admin` / `1423` (voir [README](../../../../README.md) si le volume Mongo existait déjà et que l'utilisateur admin n'a pas été créé).

Utilisez **ADD A SUBSCRIBER** avec les mêmes paramètres que `ue.yaml` et que l'exemple dans [README.md](../../../../README.md) (clé **K**, **OPC**, **AMF**, slice, DNN).

**Si vous n'arrivez pas à vous connecter à la WebUI** (ancien volume sans *init*) :

```bash
cd open5gs-containerized/core
./scripts/add-webui-admin.sh
```

**Option B — Script (vérifiez l'alignement avec `ue.yaml`) :**

```bash
cd open5gs-containerized/core
./scripts/add-subscriber.sh
```

> Le script insère un IMSI fixe dans le code. S'il diffère du `supi` de `ue.yaml`, utilisez la WebUI ou ajustez le fichier `ue.yaml` / le script pour qu'ils soient **identiques**.

**Vérification manuelle (optionnelle, pour le rapport) :**

```bash
docker exec open5gs-mongodb-containerized mongosh open5gs --quiet --eval 'db.subscribers.countDocuments({})'
docker exec open5gs-mongodb-containerized mongosh open5gs --quiet --eval 'db.subscribers.find({}, {imsi:1, supi:1}).limit(3).toArray()'
```

**Preuve :** nombre de documents ≥ 1 et éventuel champ `imsi` cohérent avec l'UE.

---

## 5. Healthcheck et état sans RAN

```bash
cd open5gs-containerized/core
./scripts/healthcheck.sh
```

**Preuve :** joignez la sortie **complète** (fichier `.txt` ou PDF).

**Notes :**

- Les tests impliquant `ueransim` (réseau N3, NG Setup) peuvent **échouer ou apparaître en jaune** tant que le RAN n'est pas actif — c'est **attendu** dans ce guide. Expliquez dans le rapport : *« validation N2/N3 complète au Guide 02 »*.
- Le *healthcheck* suppose les *container names* du compose du core (ex. : `open5gs-amf-containerized`).

---

## 6. Web UI

Avec le core actif, ouvrez la WebUI (port **9999**).

**Preuve :** *capture d'écran* de la page après connexion ou du tableau de bord (sans mots de passe visibles).

---

## 7. Logs minimaux à collecter

Pour le rapport, conservez des **extraits récents** (dernières ~30–80 lignes) de :

```bash
cd open5gs-containerized/core
docker compose logs --tail 80 nrf
docker compose logs --tail 80 amf
docker compose logs --tail 80 smf
docker compose logs --tail 80 upf
```

(Si `docker compose` se plaint du service, utilisez le nom du service défini dans `docker-compose.yml`, ex. : `mongodb`, `amf`, `smf`.)

**Preuve :** fichier `logs-core-amostra.txt` (ou un fichier par NF) dans les annexes.

---

## 8. Arrêt (fin de journée / core uniquement)

```bash
cd open5gs-containerized/core
./scripts/down_core.sh
```

Pour supprimer également les volumes : `docker compose down -v` (dans le répertoire `core/`).

---

## Checklist Guide 01

- Versions Docker jointes  
- `docker compose ps` avec un core sain  
- Réseaux `core_net-sbi`, `core_net-n2`, `core_net-n3` identifiés  
- Abonné créé **aligné sur `ue.yaml`** (WebUI ou script + vérification)  
- `healthcheck.sh` joint (avec une note sur les tests qui dépendent du RAN)  
- Échantillon de logs NRF/AMF/SMF/UPF  
- Texte court : ce que sont N2/N3 et pourquoi une partie de la vérification n'a de sens qu'après le Guide 02  

**Références :** [core/docs/CORE.md](../../../../core/docs/CORE.md), [README.md](../../../../README.md).
