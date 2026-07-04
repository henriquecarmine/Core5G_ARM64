<!-- sync: 196ae2dd -->
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
