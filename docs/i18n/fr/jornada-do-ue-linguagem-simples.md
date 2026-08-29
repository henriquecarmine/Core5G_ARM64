<!-- sync: ea52a1c1 -->
> 🌐 Traduction en **français** du document canonique en portugais [`docs/jornada-do-ue-linguagem-simples.md`](../../jornada-do-ue-linguagem-simples.md). Toutes les langues : [INDEX](INDEX.md).

# Le parcours de l'UE en langage simple

> Guide de poche à garder ouvert à côté pendant que vous cliquez sur le **Parcours de l'UE**
> (dans le tableau de bord : **Topologie → bouton « Parcours de l'UE »**). Chaque écran du parcours est une
> ligne ici en dessous — **sans charabia**. Les noms techniques n'apparaissent qu'entre
> parenthèses, pour que vous reconnaissiez ce qui est à l'écran.

## L'idée en une phrase

Un téléphone qui rejoint le réseau, c'est comme **une personne qui arrive dans un immeuble** : elle arrive,
elle se présente, elle passe par la sécurité, elle reçoit la **clé d'une chambre** et une
**adresse**, et là elle peut **envoyer et recevoir du courrier**. C'est tout — le reste,
ce ne sont que des détails sur « qui fait quoi ».

---

## Projet 2 (OAI + RIC) — les 16 écrans

| À l'écran apparaît | Ce qui se passe (en simple) |
|---|---|
| **1. Le téléphone s'allume** | La personne arrive à la porte de l'immeuble. Le téléphone se réveille et va tenter d'entrer dans le réseau. |
| **2. Radio — connexion physique** | Elle se présente à l'accueil. C'est le contact physique (la « radio ») entre le téléphone et l'antenne. |
| **3. gNB ↔ Cœur — contrôle** | L'accueil (l'antenne) appelle l'administration de l'immeuble (le cœur du réseau) : « quelqu'un vient d'arriver ». |
| **4. Enregistrement de l'UE** | La personne se présente : « je suis untel, je veux entrer ». |
| **5. Le catalogue du Cœur (NRF)** | L'administration consulte la liste interne de l'immeuble : « qui s'occupe de la sécurité ? qui remet les clés ? ». |
| **6. Authentification** | La sécurité vérifie la pièce d'identité — est-ce bien vous ? Si ça ne correspond pas, pas d'entrée. |
| **7. Demande de session de données** | Une fois approuvé, vous demandez une « ligne » pour envoyer et recevoir des choses. |
| **8. Programmation du plan usager** | L'administration prévient le couloir des livraisons : « préparez le chemin du courrier de cette personne ». |
| **9. L'UE reçoit une IP** | Vous recevez la **clé de la chambre** et une **adresse** — maintenant vous pouvez recevoir du courrier. |
| **10. Données — aller** | Vous envoyez une lettre vers l'extérieur. |
| **11. Sortie — internet / appel** | La lettre quitte l'immeuble vers le monde (internet). |
| **12. Données — retour** | La réponse arrive et remonte jusqu'à vous. |
| **13. Collecte de données (RIC)** | Un **superviseur malin** commence à noter comment se porte le trafic (vitesse, affluence) — les chiffres viennent de l'antenne. |
| **14. Action sur l'antenne (RIC)** | Le superviseur décide et **ajuste le flux en temps réel** (il libère plus de place, change la file). C'est lui qui « touche à l'antenne » à distance. |
| **15. Planificateur à long terme** | Un planificateur étudie l'historique et envoie des **règles** au superviseur. C'est ici que l'**intelligence artificielle** entre en jeu. |
| **16. Le chemin complet** | L'immeuble entier d'un seul coup : ce qui est obligatoire et ce qui est le supplément « intelligent ». |

---

## Deux couleurs, deux types d'étapes

- 🟢 **obligatoire** — ça doit se produire, sinon vous n'entrez pas ou vous ne naviguez pas. C'est la
  **ligne de vie** (écrans 2 à 12).
- 🔵 **facultatif** — le supplément « intelligent » (le superviseur et le planificateur, écrans 13 à
  15). Le réseau fonctionne sans — mais c'est ici que réside l'IA.

## Le déclic le plus important : « qui décide » ≠ « qui transporte »

Dans l'immeuble, **l'administration** (qui décide, autorise, organise) est **séparée** des
**couloirs** (par où le courrier circule réellement). Ça porte un nom barbare (CUPS),
mais l'idée est simple et puissante : on peut **remplacer un couloir sans arrêter
l'administration**. C'est ce qui permet le prochain tour de magie 👇

---

## Projet 1 (Open5GS) — presque pareil, avec 2 différences

L'histoire est la même (le téléphone qui arrive dans l'immeuble). Seul ceci change :

1. **Il n'y a pas de superviseur malin** (le RIC). Le P1 va de l'écran 1 jusqu'au « chemin
   complet », sans les parties d'intelligence.
2. **Il y a une fin en plus : le couloir de secours** (le *failover*). Si le couloir de
   livraisons tombe en panne, l'administration **bascule sur un couloir de secours à l'instant** — et
   vous continuez à naviguer sans rien remarquer. C'est la preuve que séparer « qui décide »
   de « qui transporte » en vaut la peine.

---

## Comment s'en servir pour que le déclic se fasse

1. Ouvrez le **Parcours de l'UE** dans le tableau de bord et ce guide à côté.
2. Cliquez sur **Suivant** doucement, en lisant la légende de l'écran **et** la ligne ici.
3. Faites **2 ou 3 passages**. Au deuxième, vous anticiperez déjà ce qui vient.
4. Seulement après, si vous le souhaitez, regardez les noms techniques — maintenant ils ont une place dans
   l'histoire, ce ne sont plus des sigles isolés.

> Astuce : le même diagramme a un mode **« Flux de données »** (des petites boules qui circulent) et un
> **« Tour »** par couches. Le **Parcours** est la version pas à pas, guidée — commencez
> par elle.

---

## Les sigles s'expliquent sur l'écran lui-même

Depuis la **v0.81.0**, plus besoin de quitter le Parcours pour savoir ce qu'est
un sigle. Dans la légende de chaque étape :

- le **nom complet** apparaît **entre parenthèses** juste après le terme —
  *AMF (Access and Mobility Management Function)*, *N4 (SMF ↔ UPF)* ;
- **survoler** (ou toucher, ou arriver par **Tab**) ouvre une bulle avec
  **ce que c'est** et **à quoi ça sert** — en pt/en/es/fr ;
- **Échap** ferme la bulle.

Ce sont **128 termes** (v0.84.0) : les fonctions du cœur, les interfaces
N/E2/A1/O1/O2, les protocoles, les procédures, la pile radio (RRC/RLC/MAC/PHY),
ce qui se mesure (KPI, KQI, QoE, SLA, les compteurs KPM), le vocabulaire du RIC,
le monde des données (ETL, DIKW, OLAP, TSDB, PCA, k-means…) et les bases du
laboratoire.

**Où le glossaire fonctionne**

| Écran | Ce qu'il marque | Nom complet |
|---|---|---|
| Parcours de l'UE et Tour | titre et légende de chaque étape | une fois **par étape** |
| Schéma de la topologie | les étiquettes d'interface (N4, E2, Nausf…) | la bulle seulement — l'étiquette est trop petite |
| Cours et Études | résumé, concepts, formules, quiz | une fois **par page** |
| Les 10 labos de ML | les cartes de texte | une fois **par page** |

La différence entre « par étape » et « par page » est venue de regarder l'écran :
dans une légende courte, lue isolément, marquer chaque occurrence aide ; dans un
cours, non — la première page est sortie avec **338 soulignements** et est
devenue un champ de pointillés. Dans un cours, le terme se présente une fois, et
ensuite c'est déjà du vocabulaire.

À l'intérieur de `<code>` et `<pre>`, on ne marque **jamais** : là, le sigle est
littéral, et le souligner laisserait croire que le texte du programme a changé.

Le titre de l'étape est seulement marqué, sans le nom complet — c'est un titre,
et il doit tenir sur une ligne.

### Où cela vit, et comment ajouter un terme

`server/panel/static/ops/glossario.js`, en deux couches séparées à dessein :

| Couche | Ce que c'est | Traduit ? |
|---|---|---|
| `TERMOS` | le nom officiel 3GPP/O-RAN — ce qui va entre parenthèses | **non** (même règle que `static/i18n.js`) |
| `DICTS` | `<terme>.o` = ce que c'est · `<terme>.p` = à quoi ça sert | **oui**, dans les 4 langues |

Pour en ajouter un : une ligne dans `TERMOS` (mettez `null` quand il n'y a pas de
sigle à développer, comme *MySQL* ou *NG Setup*) et les deux explications dans
les quatre dictionnaires. `npm run test:i18n:parity` refuse un terme sans
explication, une explication sans terme et une langue manquante — un terme qui
se souligne et ouvre une bulle vide est une panne silencieuse, et c'est
justement celle que le test existe pour attraper.

Pour utiliser le glossaire sur un autre écran : chargez le script et appelez
`Glossario.marcar(élément)` — ou `Glossario.marcar([{el: titre, expandir:
false}, légende])` quand un titre et une légende partagent le « une fois par
étape ». Il ne touche qu'aux **nœuds de texte** : le HTML déjà présent passe
intact.
