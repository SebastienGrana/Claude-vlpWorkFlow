# <projet> — à lire en premier, en entier, et seul

<Deux à quatre lignes : ce que le projet fait, et ce qu'il ne fait pas. Son
dossier, son dépôt. Les noms qu'il portait avant, s'ils traînent encore
ailleurs.>

## Où on en est — en cinq lignes

<Ce qui est prouvé, ce qui est ouvert, ce qui n'est pas commencé. Cinq lignes,
pas dix. Le détail daté est dans `<contexte>/08-etat.md` — l'ouvrir seulement
quand ces cinq lignes ne suffisent pas.>

## Quatre règles non négociables

1. **Annoncer le plan en une ou deux phrases avant d'agir**, et poser un
   questionnaire au moindre choix ouvert.
2. **Mesurer avant de corriger**, et afficher les comptes bruts à côté du
   verdict — un instrument muet rend son propre échec indiagnosticable.
3. <une règle propre au projet>
4. <ce qui ne part jamais dans git>

Prose en français, code et commentaires de code en anglais.

## Routage — ouvrir ceci, et rien d'autre

Cette table remplace la lecture de `00-INDEX.md`. Si la tâche n'y figure pas,
et seulement dans ce cas, ouvrir l'index.

| La tâche | Ouvrir |
|---|---|
| écrire ou modifier du code | `<contexte>/18-code.md` |
| créer un module, chercher où va un bout de code | `<contexte>/02-architecture.md` |
| ouvrir un chantier, ou le découper en fiches | **lancer `/vlp:chantier`** — la méthode vit dans le kit, pas ici |
| jouer une fiche `<X>*` | `<contexte>/<NN>-<chantier>.md` — chantier **ouvert** |
| reprendre après une longue interruption | `<contexte>/08-etat.md` |

## Économie de contexte

La fenêtre sature par **densité de contexte**, pas par volume horaire. Donc,
dans cet ordre :

- **Un fichier de contexte ne s'ouvre que si la table ci-dessus le nomme.** Le
  voisin d'un fichier utile n'est pas utile ; il n'est que du volume.
- **Ne jamais lire le dossier de contexte en entier**, ni le README.
- **Une tâche, une session.** `/clear` entre deux tâches : une session laissée
  ouverte relit tout son passé à chaque tour.
- **Explorer et lire avec un modèle léger**, garder le lourd pour ce qui décide.
- Grep ciblé plutôt que lecture de fichier entier, dans le code comme ici.
