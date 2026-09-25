> **QUAND LIRE** : on joue une fiche `REL*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache REL<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier REL — Le relecteur ne voit pas la suite

**À quoi il sert.** La skill `vlp:relire` injecte au relecteur la carte entière, titres des
fiches compris : en `REV4`, il y lisait « REV6 [x] — … », le défaut à trouver (TODO 55, `FUI`).
Le relecteur recevra une carte réduite, sans titres de fiches ni `PROCHAINE=`.

**Fait.** Rien. Ouvert le 2026-09-26, cadré en 3 fiches, `REL1` à jouer.

**Session** : a0c37d8b-64b2-4c7f-b1d6-cbf416b76457

## Le socle commun

Image : le correcteur recevait la copie avec le sommaire du manuel, où la faute était écrite.

**Décidé au cadrage (2026-09-26, par l'utilisateur).**

1. Fin : un test de `test-vlp.py` et son mutant ; pas de relecture rejouée en vrai.
2. Le relecteur garde une **carte réduite** — pas « plus de carte du tout ».
3. On mesure d'abord (`REL1`) ce que les relecteurs tirent de la carte ; `REL2` retire ce
   que `REL1` dit inutile, et au moins les titres de fiches et `PROCHAINE=`.
4. Dehors : la carte du sous-agent `vlp:fiche` (`skills/jouer/SKILL.md`) et celle du chef
   (`skills/enchainer/SKILL.md`) ne changent pas. La ligne `FICHIER=` que rend
   `vlp.py relecture` (le relecteur peut ouvrir tout le fichier de fiches) : si `REL1`
   montre qu'il le fait, c'est une ligne de TODO, pas une fiche ici.

**Ce qui existe, à réutiliser.**

| Symbole | Où | Ce qu'il fait |
|---|---|---|
| `carte(depart, sortie)` | `scripts/vlp.py:478` | `PROJET=`, `CHANTIER.md` entier ; chantier ouvert : un `n:titre` par fiche, puis `PROCHAINE=` (l. 506–512) |
| `carte_injectee(…)` | `scripts/vlp.py:519` | l'injection à trois appels et son tampon `--relais` de 30 s |
| parseur `carte` | `scripts/vlp.py:3287` | `dossier`, `--python`, `--relais` |
| `forme` | `scripts/vlp.py` (docstring l. 201) | liste les transcriptions `vlp:fiche` et `vlp:relecture` : 42 relecteurs le 2026-09-26 |
| `type_agent(chemin)` | `scripts/vlp.py:1383` | l'`agentType` du `.meta.json` voisin |
| tests de la carte | `scripts/test-vlp.py:60`, `:116` | bac temporaire, `mod.carte(depart, s)` |

Nom retenu : l'option **`--relecteur`** de `vlp.py carte`. Un test bâtit son projet dans un
dossier temporaire : jamais le vrai dépôt ni les vraies transcriptions (`ESD2`). Un nouveau
`with tempfile.TemporaryDirectory()` prend un nom neuf, pas `t` (piège vu en `ENC1`).
Aucun extrait de contenu de Cairn dans le dépôt : des comptes seulement.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `REL1` | Mesurer ce que le relecteur tire de la carte | rien |
| `REL2` | Donner à `vlp.py carte` l'option `--relecteur` | `REL1` |
| `REL3` | Injecter la carte réduite dans `vlp:relire` | `REL2` |

Strictement en série : chaque fiche lit le verdict de la précédente.

---

<!-- FICHE:REL1 -->
## REL1 [ ] — Mesurer ce que le relecteur tire de la carte

**Dépend de** : rien.
**Fichiers** : `context AI/38-audit-scripts/rel1-carte.py` (nouveau, jetable),
`context AI/66-relecteur-sans-suite.md` (le verdict, sous cette fiche) — et rien d'autre.

**Prompt**
Liste les transcriptions de relecteur par `vlp.py forme` (type `vlp:relecture`). Écris
un script jetable qui, pour chacune, relève dans les messages de l'assistant (texte et
entrées d'outil) :
- les identifiants de fiche cités autres que la fiche relue (premier argument de la
  skill) — un signe que les titres de la carte servent ;
- `PROCHAINE` cité ;
- les libellés en gras de `CHANTIER.md` cités (`contexte`, `kit`, `vérification`…) ;
- les `Read` du chemin donné par `FICHIER=` sans `offset`/`limit`, et les `Grep` dessus.
Sors les **comptes** par transcription et au total, jamais un extrait de texte.
Écris sous cette fiche un bloc `**Verdict REL1**` : la table des comptes, puis la liste
des parties de la carte que `--relecteur` garde, et pourquoi. `FICHIER=` lu en entier
au moins une fois : ajoute une ligne à la TODO de `context AI/08-etat.md`.

**Critère de fin**
`py "context AI/38-audit-scripts/rel1-carte.py"` rend une ligne par transcription et
une ligne de total, avec un compte de transcriptions égal à celui de `vlp:relecture`
dans `py scripts/vlp.py forme`, soit 42 au 2026-09-26 ou plus. Le bloc `**Verdict REL1**`
recopie ce total tel quel.
<!-- /FICHE -->

---

<!-- FICHE:REL2 -->
## REL2 [ ] — Donner à `vlp.py carte` l'option `--relecteur`

**Dépend de** : `REL1` — lis son bloc `**Verdict REL1**` avant d'écrire.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Ajoute `--relecteur` au parseur `carte`, et fais-le passer jusqu'à `carte()` par
`carte_injectee`. Avec lui, la carte d'un chantier ouvert n'écrit ni les lignes
`n:titre` des fiches, ni `PROCHAINE=`, ni ce que le verdict de `REL1` retire. Elle
garde `PYTHON=`, `PROJET=` et le reste. Sans l'option, la sortie ne change pas d'un
octet. Mets à jour la ligne `carte` de la docstring du module. Le tampon `--relais`
se comporte comme avant.

**Critère de fin**
`py scripts/test-vlp.py` passe, avec un test neuf `test_carte_relecteur`. Dans un
bac temporaire dont le chantier ouvert a une fiche `## ZZZ2 [x] — piège`, il vérifie
que `carte --relecteur` ne contient ni `piège`, ni `PROCHAINE=`, mais contient bien
`PROJET=`, et que `carte` sans l'option est inchangée. Donne les comptes bruts du
passage, avant et après.
Le mutant : l'option lue mais ignorée dans `carte()`. Il doit faire tomber ce test.
`pyright scripts/` : 0 erreur.
<!-- /FICHE -->

---

<!-- FICHE:REL3 -->
## REL3 [ ] — Injecter la carte réduite dans `vlp:relire`

**Dépend de** : `REL2`.
**Fichiers** : `skills/relire/SKILL.md`, `agents/relecture.md` — et rien d'autre.

**Prompt**
Dans `skills/relire/SKILL.md`, ajoute `--relecteur` aux trois appels `vlp.py carte` de
la ligne injectée. Corrige la phrase qui l'annonce (« puis `CHANTIER.md` en entier ») :
qu'elle dise, en une ligne, que la carte n'a ni titres de fiches ni `PROCHAINE=`, et
pourquoi (la suite du chantier peut contenir la réponse). Même chose, en un mot, là où
`agents/relecture.md` décrit la carte (ligne 11). Ne touche ni `skills/jouer/` ni
`skills/enchainer/`.

**Critère de fin**
`grep -c -- "--relecteur" skills/relire/SKILL.md` rend 3.
Le même grep sur `skills/jouer/SKILL.md` et `skills/enchainer/SKILL.md` rend 0.
Lancée telle quelle, avec `${CLAUDE_PLUGIN_ROOT}` remplacé par le kit, depuis le bac
de `test_carte_relecteur` ou un bac pareil, la ligne injectée sort 0 titre de fiche,
1 `PROJET=` et 0 `PROCHAINE=`. Donne les trois comptes.
<!-- /FICHE -->
