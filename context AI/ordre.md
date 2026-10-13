# L'ordre entre projets — la source de `vlp.py ordre`

> Lue par `vlp.py ordre` (chantier ORD). Ce fichier dit **quoi** et **dans quel ordre** ; le coût, la
> phase, le score, le nom et la dépendance de chaque pas se lisent dans la TODO de son projet, à la
> génération. Ce que le script écrit va dans `context AI/ordre/`, ignoré par Git.
>
> **Cairn est privé, le kit public** : ici, des codes de Cairn et leur ordre, jamais une description
> ni un coût de Cairn.

## Les projets

Une clé courte par projet, et son dossier, cherché à côté du kit. `.` : le projet de ce fichier
même, où qu'il soit cloné.

| Clé | Dossier |
|---|---|
| kit | `.` |
| cairn | `Cairn-VlpLib` |
| md | `MapDecorator` |

## La cible

Les codes de la V1 de MapDecorator, lus dans sa TODO le 2026-10-13.

| Projet | Codes |
|---|---|
| md | `MD4` `C2` `C1` `C3` `MD1` `C4` |

## Le chemin conseillé

Un pas par ligne, dans l'ordre conseillé. Les deux dernières colonnes ne servent qu'à un pas que
la TODO ne connaît pas (un chantier clos, une fiche) : son nom, et son coût — `✅ …` pour un pas
fait. Pour un pas que la TODO connaît, la dernière colonne est une note, montrée à côté.

| Pas | Projet | Nom, si la TODO n'en a pas | Coût, si la TODO n'en a pas ; sinon une note |
|---|---|---|---|
| `NET` | kit | le ménage | ✅ fait le 2026-10-12 |
| `ENA` | kit | enchaîner les fiches | ✅ clos le 2026-10-13 |
| `NWT` | kit | le kit voit un worktree | ✅ fait le 2026-10-12 |
| `SYM` | kit | un outil qui lit le .as | ✅ fait le 2026-10-12 |
| `MD4` | md | | avant `C2` |
| `MD5` | md | | avant `C2` |
| `MD7` | md | | avant `C2` |
| `MD2` | md | | |
| `MD3` | md | | |
| `C2` | md | | |
| `SCH` | cairn | | compté avec `REG` |
| `CLR` | cairn | | |
| `MEN` | cairn | | |
| `SEL` | cairn | | |
| `FAM11` | cairn | | 1 fiche |
| `PRS` | cairn | | |
| `REG` | cairn | | |
| `C1` | md | | |
| `C3` | md | | |
| `C4` | md | | |
| `MD1` | md | | après `C3` |

## Les dépendances ajoutées

Celles qu'aucune TODO n'écrit entre accents graves, ou qu'elle écrit sous un autre code ; chacune dit
d'où elle vient. Le reste se lit dans la colonne « Dépend de » des TODO.

| Pas | Dépend de | Pourquoi |
|---|---|---|
| `C1` | `FAM11` | la TODO de MapDecorator : `C1` attend `FAM` fusionné, dont `FAM11` est le pas du chemin |
| `PRS` | `FAM11` | la TODO de Cairn : `PRS` dépend de `FAM`, dont `FAM11` est le pas du chemin |
| `FAM11` | `NWT` | la page du 2026-10-12 : `NWT` avant `FAM11` |
| `C2` | `MD4` `MD5` `MD7` | la page du 2026-10-12 : les notes justes avant de coder |

## Les niveaux forcés

Un pas sans phase dans une TODO (un chantier clos) qui n'est pas obligatoire : la source dit son niveau.

| Pas | Niveau | Pourquoi |
|---|---|---|
| `NET` | conseillé | clos le 2026-10-12, conseillé sur la page du même jour |
| `ENA` | conseillé | clos le 2026-10-13, conseillé sur la page du 2026-10-12 |
| `SYM` | conseillé | clos le 2026-10-12, conseillé sur la page du même jour |

## Le jugement

- MapDecorator est la maison à décorer, Cairn le magasin qui fournit les meubles, le kit la boîte
  à outils.
- Le kit d'abord : ses audits et son ménage sont faits ; le reste de sa V1 se glisse entre deux
  vagues, une ligne à la fois, dans l'ordre du score.
- Puis Cairn livre ce que MapDecorator lit : `SCH` en tête, `FAM11` et la fusion de `FAM`, `PRS`,
  `REG`.
- Puis la V1 de MapDecorator se construit : `C1`, `C3`, `MD1` après `C3`, et `C4` ; toute la V1
  avant la V2.
- Dès maintenant, si tu veux : MapDecorator prépare ce qui n'attend pas Cairn — ses notes justes,
  son ménage, puis `C2`.
- Pas encore tranché : obligatoire ou conseillé, ce classement est à corriger si tu vois
  autrement ; `SCH` et `PRS` sont à cadrer ; deux séances en même temps, le kit et Cairn, vont plus
  vite mais demandent deux fois plus de suivi.
