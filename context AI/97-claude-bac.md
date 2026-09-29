> **QUAND LIRE** : on joue une fiche `CLI*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache CLI<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier CLI — Le bac dit comment ouvrir sa session

**À quoi il sert.** Ouvrir une session dans le bac a pris 3 allers-retours à `REG3` : `claude` hors
du `PATH`, puis le chemin `%APPDATA%` refusé dans le terminal de l'utilisateur. Le kit cherche
`claude.exe` à deux endroits, pas de la même façon ; une seule recherche, et `bac` qui la dit.

**Estimé.** 1 fiches · ≈3,01 $ — ≈3,01 $/fiche sur 84 clos (le 2026-09-29).

**Fait.** Rien. Ouvert le 2026-09-29, cadré en 1 fiche, `CLI1` à jouer.

**Session** : b293bb0b-835f-4938-bedc-3114bdb5643a

## Le socle commun

**Mesuré au cadrage (2026-09-29)**, depuis une session de l'app : `claude` absent du `PATH`
(`which claude`) ; `claude.exe` présent **en 2 versions** (2.1.281, 2.1.284) sous
`%APPDATA%\Claude\claude-code\` **et** sous
`%LOCALAPPDATA%\Packages\Claude_*\LocalCache\Roaming\Claude\claude-code\`. Le chemin `Packages`
marche donc dans l'app et hors d'elle ; `%APPDATA%` dans l'app seulement (`REG3`).
Aujourd'hui : `scripts/boucle.py:67` cherche `PATH` puis `%APPDATA%` ; `.githooks/pre-commit:20-32`
cherche `PATH`, `%APPDATA%`, puis `Packages` ; `vlp.py bac` (`scripts/vlp.py:5073`) imprime des
`claude -p` qui supposent `claude` sur le `PATH`.

**Tranché au cadrage (l'utilisateur)** :
- la recherche vit dans **`vlp.py claude`** ; `boucle.py` et `bac` s'en servent ; le hook sh garde
  sa copie, **alignée** sur le même ordre (il ne dépend pas de Python) ;
- l'ordre : `VLP_CLAUDE`, `PATH`, **`Packages` d'abord**, puis `%APPDATA%` — dans chaque dossier,
  la plus haute version, comparée en nombres (`2.1.10` > `2.1.9`) ;
- la commande d'ouverture imprimée par `bac` est en **PowerShell** seul.

**Dehors** : les deux `claude -p` de `bac`, écrits pour Bash (`< /dev/null`) et les essais de
`FIL3`, restent tels quels ; macOS et Linux au-delà du `PATH` ; installer `claude`.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `CLI1` | Écrire `vlp.py claude`, et s'en servir dans `boucle.py`, `bac` et le hook | rien |

Une seule fiche.

---

<!-- FICHE:CLI1 -->
## CLI1 [x] — Écrire `vlp.py claude`, et s'en servir dans `boucle.py`, `bac` et le hook

**Session** : b293bb0b-835f-4938-bedc-3114bdb5643a
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/boucle.py`, `.githooks/pre-commit`, `scripts/test-vlp.py`
— et rien d'autre.

**Prompt**
Dans `scripts/vlp.py`, une fonction `trouver_claude()` qui suit l'ordre du socle et rend un chemin
ou `None`, et la sous-commande `claude` : `CLAUDE <chemin>` (sort 0), ou
`GARDE: claude.exe introuvable — PATH, Packages et APPDATA vus` (sort 1). Docstring de tête : la
sous-commande. `bac` ajoute, après ses deux commandes, la ligne
`SESSION Set-Location "<dossier absolu>"; & "<chemin>"` — `claude` introuvable : la même ligne avec
`claude`, précédée de la `GARDE:` ; `bac` sort toujours 0. Dans `scripts/boucle.py`,
`trouver_claude(choix)` garde `choix`, puis lit `vlp.py claude` par son `vlp()` et ne cherche plus
lui-même (docstring de tête avec). Dans `.githooks/pre-commit`, `Packages` passe avant `%APPDATA%`.

**Critère de fin**
1. Tests dans `scripts/test-vlp.py`, sur des `LOCALAPPDATA`/`APPDATA` temporaires à faux
   `claude.exe` et un `PATH` sans `claude` : `Packages` gagne sur `APPDATA` ; `2.1.10` gagne sur
   `2.1.9` ; `VLP_CLAUDE` gagne sur tout ; rien → `GARDE:`, sort 1 ; `bac` imprime la ligne
   `SESSION` avec le chemin trouvé ; `boucle.py` rend le même chemin que `vlp.py claude`.
2. Mutant joué par `vlp.py mutant` : l'ordre `Packages`/`APPDATA` inversé → un test tombe.
3. Réel, ici : `vlp.py claude` rend le chemin `Packages` en 2.1.284. `py scripts/test-vlp.py` : `OK` ;
   pyright 0 erreur.
<!-- /FICHE -->
