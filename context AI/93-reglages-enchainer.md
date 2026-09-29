> **QUAND LIRE** : on joue une fiche `REG*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache REG<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier REG — Les réglages d'`enchainer` tranchés par `PAR5`, sans attendre `NUI`

**À quoi il sert.** `/vlp:enchainer` part par défaut en sous-agents (3,18 $/fiche contre
2,03 $ en `main`, `PAR6`), son joueur est Haiku (0 fiche finie sur 2, `PAR7`) et son
`model: sonnet` réécrit le cache à chaque appel (≈ 0,62 $, `PAR7`). Ce chantier pose les
réglages tranchés : défaut `main`, joueur Sonnet effort `low`, aucune bascule de modèle.

**Estimé.** 1 fiches · ≈3,03 $ — ≈3,03 $/fiche sur 80 clos (le 2026-09-29).

**Fait.** Rien. Ouvert le 2026-09-29, cadré en 3 fiches, `REG1` à jouer.

**Session** : 18a50f2c-b7a4-4044-bd16-d14df177ec7b

## Le socle commun

| Où | Aujourd'hui | Après `REG` |
|---|---|---|
| `skills/enchainer/SKILL.md:4` | `model: sonnet` | ligne retirée : la commande tourne dans le modèle de la session |
| `skills/enchainer/SKILL.md`, arguments | (rien) = sous-agents · `main` · `clear` | (rien) = `main` · `agents` = sous-agents · `clear` ; `main clear` se lit `clear` |
| `agents/fiche.md:4-5` | `model: haiku`, `effort: low` | `model: sonnet`, `effort: low` |
| `scripts/boucle.py`, `jouer()` et `main()` | `--model`, `--budget` transmis ; pas d'effort | `--effort E` transmis à `claude -p` tel quel, **sans défaut** |
| appel de `boucle.py` dans `enchainer clear` | `--plafond` seul | `--plafond … --model sonnet --effort low` |

- **Sonnet `low` vit à un seul endroit par mode** : `agents/fiche.md` pour `agents`, le texte
  d'`enchainer` pour `clear`. `boucle.py` reste neutre (aucune valeur par défaut). Le mode
  `main` ne choisit rien : c'est la session qui joue.
- Les modes `agents` et `clear` gardent leur fonctionnement : seul leur nom d'entrée ou leur
  modèle change. `vlp:jouer`, `vlp:relire` et `agents/relecture.md` ne bougent pas.
- `scripts/test-boucle.py` a un faux `claude` qui recopie ses arguments dans la ligne
  `result` (`FAUX`, en tête du fichier) : un test y lit ce que `boucle.py` a transmis.
- **Dehors**, renvoyé à `NUI` (TODO n° 72) : la relance plus forte sur refus, le chef en Opus,
  la borne de la nuit, un effort choisi fiche par fiche. Le plafond de 5 fiches ne change pas.
  Le Haiku du bac d'essai (`scripts/vlp.py`, `BAC_COMMANDES`) est voulu : on n'y touche pas.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `REG1` | Transmettre l'effort par `boucle.py` | rien |
| `REG2` | Faire partir `enchainer` en `main`, le joueur en Sonnet | `REG1` |
| `REG3` | Essayer `enchainer` rechargé, pour de vrai | `REG2` |

Rien de parallélisable : `REG2` appelle l'option de `REG1`, `REG3` essaie `REG2`.

---

<!-- FICHE:REG1 -->
## REG1 [x] — Transmettre l'effort par `boucle.py`

**Session** : 530c009b-ea97-49ff-a327-c115bd205a02
**Dépend de** : rien.
**Fichiers** : `scripts/boucle.py`, `scripts/test-boucle.py` — et rien d'autre.

**Prompt**
Ajoute à `scripts/boucle.py` une option `--effort` : quand elle est donnée, `jouer()`
ajoute `--effort <valeur>` à la commande `claude -p`, comme il le fait pour `--model` ;
absente, rien n'est ajouté. Aucune valeur par défaut, aucune liste de valeurs permises :
`claude` juge. Mets la docstring à jour (ligne d'usage).
Dans `scripts/test-boucle.py`, ajoute un cas qui lance `boucle.py` avec `--effort low` sur
le faux `claude`, et vérifie que la sortie porte `--effort,low` (le faux recopie ses
arguments séparés par des virgules) ; un second cas, sans l'option, vérifie que `--effort`
n'apparaît pas.

**Critère de fin**
`py -3 scripts/test-boucle.py` imprime `OK`. Mutant : retirer l'ajout de `--effort` dans
`jouer()` → le test imprime un écart et sort 1 ; rendre le fichier, `OK` revient. `pyright
scripts/boucle.py scripts/test-boucle.py` : 0 erreur (compte brut dans le compte rendu).
<!-- /FICHE -->

---

<!-- FICHE:REG2 -->
## REG2 [x] — Faire partir `enchainer` en `main`, le joueur en Sonnet

**Session** : 6592ddaf-e838-4aba-8d9b-61bcd7f12d7b
**Dépend de** : `REG1`.
**Fichiers** : `skills/enchainer/SKILL.md`, `agents/fiche.md` — et rien d'autre.

**Prompt**
Applique la table du socle. Dans `skills/enchainer/SKILL.md` : retire la ligne
`model: sonnet` ; sans argument, la commande joue en `main` ; le mot `agents` demande
les sous-agents (le fonctionnement actuel « sans argument ») ; `main clear` se lit comme
`clear` ; l'appel de `boucle.py` du mode `clear` passe `--model sonnet --effort low`.
Réécris la `description` et l'`argument-hint` en conséquence (`<alias>` suit toujours le
même ordre). Chaque phrase qui disait « sans `main` » pour désigner les sous-agents dit
désormais « avec `agents` ». Court : tout ajout se paye à chaque exécution.
Dans `agents/fiche.md`, `model: haiku` devient `model: sonnet`.

**Critère de fin**
Comptes bruts, depuis la racine : `grep -c "^model:" skills/enchainer/SKILL.md` → 0 ;
`grep -c "^model: sonnet" agents/fiche.md` → 1 ; `grep -o -- "--effort low" skills/enchainer/SKILL.md | wc -l`
→ au moins 1 ; `grep -o "Sans \`main\`" skills/enchainer/SKILL.md | wc -l` → 0 ;
`py -3 scripts/test-vlp.py` et `py -3 scripts/test-boucle.py` impriment `OK`.
<!-- /FICHE -->

---

<!-- FICHE:REG3 -->
## REG3 [ ] — Essayer `enchainer` rechargé, pour de vrai

**Dépend de** : `REG2`.
**Fichiers** : aucun à modifier.

**Prompt**
Dès le début, demande à l'utilisateur de lancer `/reload-plugins` (Claude ne peut pas le
faire). Puis pose un bac d'essai dans un dossier vide du scratchpad :
`py -3 scripts/vlp.py bac <dossier>` (deux fiches factices, `F1` et `F2`, sans risque) ;
ignore les commandes `claude -p` qu'il imprime. Donne le chemin à l'utilisateur : il ouvre
une session Claude Code dans ce dossier, y lance `/vlp:enchainer` sans argument, et
regarde. Arrête-toi et rends-lui la main ; lis le résultat seulement après son retour.

**Critère de fin** (visuel)
L'utilisateur voit `F1` jouée **dans la session**, sans sous-agent `vlp:fiche` dans le
panneau Tâches, et sa case cochée dans le fichier du bac ; la session garde le modèle choisi
au lancement (aucune bascule annoncée). Il le dit ; la fiche note ce qu'il a vu.
<!-- /FICHE -->
