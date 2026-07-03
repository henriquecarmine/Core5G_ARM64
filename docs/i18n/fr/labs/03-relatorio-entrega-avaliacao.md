<!-- sync: e8f9da69 -->
> 🌐 Traduction en **français** du document canonique en portugais [`docs/labs/03-relatorio-entrega-avaliacao.md`](../../../labs/03-relatorio-entrega-avaliacao.md). Toutes les langues : [INDEX](../INDEX.md) · synchronisation vérifiée par `docs/i18n/check-parity.py`.

# Rapport — remise, structure et critères d'évaluation (Open5GS + UERANSIM)

Ce document oriente les **étudiants** (ce qu'il faut remettre) et les **enseignants** (comment évaluer).

**Support vidéo :** [liste des vidéos du laboratoire](video_seq_report.md). La [démonstration complète](https://youtu.be/ic3_CIllb9o) parcourt les guides 01–03 et montre comment finaliser les preuves (y compris PCAP / Wireshark) pour la remise.

---

## 1. Format de remise

- **Format accepté :** PDF unique **ou** fichier `.zip`/`.7z` avec PDF + pièces jointes (logs en `.txt` ; les PCAP volumineux peuvent être omis avec justification et *hash* ou description de la capture).
- **Identification sur la première page :** nom complet, matricule ou identification, classe, date, titre suggéré : « Laboratoire Open5GS + UERANSIM — Interfaces et protocoles ».
- **Version du dépôt (recommandé) :** sortie de `git rev-parse --short HEAD` à la racine du clone (si applicable).

---

## 2. Structure suggérée du rapport

1. **Résumé** (10–15 lignes) : objectifs, ce qui a été exécuté, principaux résultats.
2. **Environnement :** système d'exploitation, versions `docker` / `docker compose`, RAM pertinente (*pull* des images).
3. **Guide 01 — Core :** référence croisée avec preuves ([01-core-open5gs.md](01-core-open5gs.md)).
4. **Guide 02 — UERANSIM :** idem ([02-ueransim-n2-n3-e2e.md](02-ueransim-n2-n3-e2e.md)).
5. **Discussion :**
  - Rôle des interfaces **N2** (NGAP/SCTP) et **N3** (GTP-U) dans le scénario conteneurisé.
  - Différences par rapport à un gNB monolithique *vs.* *split* CU/DU (référence conceptuelle ; ce laboratoire utilise UERANSIM intégré).
  - Limites (*emulation*, sans RF réel, *stub* de cellule, etc.).
6. **Conclusion** (5–8 lignes).
7. **Annexes** (numérotées) : A — sorties de commandes ; B — logs ; C — *captures d'écran* ; D — PCAP.

**Extension suggérée :** 8–15 pages **sans** annexes excessives.

---

## 3. Inventaire minimal de preuves (étudiant)


| ID  | Preuve                                                                          | Guide |
| --- | ------------------------------------------------------------------------------- | ----- |
| E1  | `docker --version` et `docker compose version`                                  | 01    |
| E2  | `docker compose ps` (core sain)                                                 | 01    |
| E3  | Confirmation des réseaux `core_net-sbi` / `core_net-n2` / `core_net-n3` et sous-réseaux | 01 |
| E4  | Abonné créé (WebUI, script ou `mongosh`) aligné sur `ue.yaml`                    | 01    |
| E5  | Sortie complète `healthcheck.sh` (sans RAN ou avec note sur les limites)        | 01    |
| E6  | Échantillon de logs NRF + AMF + SMF + UPF                                        | 01    |
| E7  | `docker ps` avec `ueransim` **Up**                                               | 02    |
| E8  | Extraits pertinents `gnb.yaml` / `ue.yaml`                                       | 02    |
| E9  | Logs UERANSIM + AMF avec N2 / NG Setup                                           | 02    |
| E10 | (Optionnel avancé) PCAP ou *capture d'écran* Wireshark N2 (`sctp.port == 38412`) | 02    |
| E11 | (Optionnel avancé) PCAP N3 ou *capture d'écran* Wireshark GTP-U (`udp.port == 2152`) | 02 |
| E12 | Sortie complète `test_ue_connection.sh`                                          | 02    |
| E13 | `healthcheck.sh` avec le RAN activé                                              | 02    |


Absence de **preuve obligatoire** marquée dans les guides → pénalité dans la rubrique « Complétude ».

---

## 4. Captures d'écran

- **WebUI Open5GS :** 1 *capture d'écran* (après connexion ou écran visible, sans mot de passe).
- **Terminal :** *capture d'écran* ou texte à chasse fixe ; le texte recherchable est préférable.
- **Wireshark :** *captures d'écran* avec **filtre visible** — N2 : `sctp.port == 38412` ; N3 : `udp.port == 2152`.

**Règle :** images **lisibles** ; recadrages légendés.

---

## 5. Bonnes pratiques avec les logs

- Ne pas remettre des logs de plusieurs mégaoctets dans le PDF ; joignez un `.txt` ou utilisez `tail -n 80`.
- Indiquez la **date/heure** de la collecte et le **conteneur** (`docker logs <nom>`).
- En cas d'échecs, incluez le **premier** message d'erreur complet.

---

## 6. Rubrique suggérée (100 points)


| Critère                  | Poids | Description                                                                   |
| ------------------------ | ----- | ---------------------------------------------------------------------------- |
| **Complétude**           | 25    | Guides 01 et 02 ; preuves E1–E13 lorsque applicable ; annexes citées dans le texte. |
| **Correction technique** | 30    | Commandes et IP cohérentes avec le projet ; N2/N3 discutés sans erreurs graves.   |
| **Analyse**              | 25    | Limites du lab ; lien avec les **interfaces et protocoles** 5G SA.           |
| **Clarté**               | 15    | Structure, figures numérotées, orthographe acceptable.                       |
| **Soutenance / extra**   | 5     | PCAP N2 optionnel ; *troubleshooting* documenté ; réponses à la soutenance.  |


---

## 7. Questions pour la discussion

1. Que transporte le **N2** par rapport au **N3** ?
2. Pourquoi le compose UERANSIM dépend-il des réseaux externes `core_net-n2` et `core_net-n3` ?
3. Qu'est-ce que le **PFCP** au croisement SMF–UPF et comment se rapporte-t-il à la session PDU ?
4. Que changerait-il si l'IMSI dans le cœur ne correspondait pas au `supi` du `ue.yaml` ?

---

## 8. Checklist final avant de soumettre

- PDF avec identification complète  
- Figures/tableaux numérotés et cités  
- Annexes aux noms clairs (`anexoA-compose-ps.txt`, …)  
- Aucun mot de passe ni *token* dans les logs  
- Références (Open5GS, UERANSIM, 3GPP, lorsque applicable)
