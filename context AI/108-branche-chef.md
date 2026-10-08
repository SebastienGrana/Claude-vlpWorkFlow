> **QUAND LIRE** : on joue une fiche `BRA*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache BRA<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier BRA — `/vlp:chef` vérifie la branche dès son début

**Ouvert.** le 2026-10-08.

**À quoi il sert.** Un `/vlp:chef` lancé dans un worktree a trié toute la TODO, puis s'est arrêté : le plan ne
s'écrit que sur `main`, et ce contrôle n'arrive qu'en section 4. Le chantier met la garde dans `vlp.py trier`, avant le tri.

**Estimé.** 1 fiches · ≈3,95 $ — ≈3,95 $/fiche sur 91 clos (le 2026-10-08).

**Fait.** Rien. Ouvert le 2026-10-08, la nuit (canal B), cadré en 1 fiche selon le plan du soir, `BRA1` à jouer.

**Session** : a829c7ca-064c-4d82-946e-856f5f9aa760

## Le socle commun

Le découpage vient du plan du soir (`context AI/106-nuits.md`, section `### BRA`, réponse Q5 : script).

| Symbole | Fichier | Rôle |
|---|---|---|
| `cmd_trier` | `scripts/vlp_coeur.py` | la sous-commande `trier` ; ses `GARDE:` s'écrivent `sortie.write("GARDE: …\n")`, `return 1` |
| `git_texte(args, cwd)` | `scripts/vlp_coeur.py` | `(code, texte)` ; code `None` si Git ne se lance pas, jamais de traceback |
| `cmd_matin` | `scripts/vlp_coeur.py` | le modèle à suivre : `symbolic-ref --short -q HEAD`, `GARDE: HEAD est sur … pas sur main` |
| `tester_trier` | `scripts/test-vlp.py` | les tests de `trier`, dans un dossier temporaire **hors Git** |
| `git_matin`, `code_git` | `scripts/test-vlp.py` | aides Git des tests (`init -q -b main`, `switch -q -c …`) |
| `trier <projet>` | docstring de `scripts/vlp.py` | la doc de la sous-commande ; la garde s'y décrit |

Décisions prises au cadrage (la nuit, au plus sûr — à revoir le matin si besoin) :

- **Hors Git, le tri passe** : les tests de `tester_trier` tournent dans un dossier temporaire nu ; les
  faire tomber n'apporterait rien, un projet hors Git n'a pas de nuit (la boucle crée des worktrees).
- **Dans Git, branche ≠ `main` ou tête détachée : `GARDE:`**, avant toute lecture de la TODO, sortie 1.
- Le nom `main` est littéral, comme dans `cmd_matin` et `scripts/boucle.py` : pas de `branche_principale` ici.
- La vérification « fichier des nuits ignoré » de la section 4 de `/vlp:chef` **reste** : seule la branche part.

Hors du chantier : `plan ecrire` ne gagne pas de garde de branche (le plan ne l'a pas demandé) ; aucune autre
commande ne change.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `BRA1` | Garder `trier` hors de `main`, et le dire dans `/vlp:chef` | rien |

Une seule fiche : rien à paralléliser.

---

<!-- FICHE:BRA1 -->
## BRA1 [x] — Garder `trier` hors de `main`, et le dire dans `/vlp:chef`

**Session** : d07d8dca-b35a-403d-b775-407e75d4c15b
**Session** : 207c6c14-a02f-4b06-af9d-eb1734dad821 (relire)
**Dépend de** : rien.
**Fichiers** : `scripts/vlp_coeur.py`, `scripts/vlp.py`, `scripts/test-vlp.py`, `skills/chef/SKILL.md` — et rien d'autre.

**Prompt**
Dans `cmd_trier`, juste après la garde `equipe`, ajoute la garde de branche (socle, « Décisions ») :
`git rev-parse --is-inside-work-tree` qui échoue = hors Git, on continue ; sinon `symbolic-ref --short -q HEAD`
comme `cmd_matin` — tête détachée ou branche ≠ `main` : `GARDE: trier hors de main (branche <nom>) — le plan ne
s'écrit que sur main : rien trié`, sortie 1, rien d'autre imprimé.

Dans la docstring de `scripts/vlp.py`, entrée `trier <projet>`, ajoute une demi-ligne : la garde de branche.

Dans `tester_trier`, ajoute un cas dans **sa propre** fonction ou son propre `with` (ne réutilise pas la
variable d'un `with` voisin) : un dossier temporaire avec `git init -q -b main`, le même `CHANTIER.md` et la
même TODO → sortie 0 ; puis `git switch -q -c nuit/x` → sortie 1, une seule ligne, qui commence par `GARDE: trier hors de main`.

Dans `skills/chef/SKILL.md` : section 0, une puce courte — hors de `main`, `trier` s'arrête en `GARDE:`, qui se
dit et arrête le chef ; section 4, retire « `git branch --show-current` ≠ `main` » de la phrase « **Avant**
`plan ecrire` » et garde la vérification du fichier des nuits ignoré. Rien d'autre ne change dans la commande.

`pyright` sur les fichiers `.py` touchés : zéro erreur de plus qu'avant (compter avant et après).

**Critère de fin**
- `py -3 scripts/test-vlp.py` : le nouveau cas vert, zéro `ÉCART` (compte brut des verts affiché).
- Mutant : `vlp.py mutant scripts/vlp_coeur.py` qui inverse la comparaison à `main` de la nouvelle garde
  (un `<avant>` unique au fichier : `cmd_matin` porte déjà `!= "main"`), `--attendu` le libellé du nouveau cas → il tombe.
- `py -3 scripts/vlp.py trier .` dans ce worktree (branche `nuit/…`) : sortie 1, une ligne `GARDE: trier hors de main`.
- `grep -c "show-current" skills/chef/SKILL.md` : 0.
<!-- /FICHE -->
