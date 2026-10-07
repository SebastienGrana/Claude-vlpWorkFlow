> **QUAND LIRE** : on joue une fiche `ARP*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache ARP<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier ARP — Une session `claude -p` ne meurt plus en attendant l'arrière-plan

**Ouvert.** le 2026-10-08.

**À quoi il sert.** En `claude -p`, rendre la main finit la session : 8 sur 11 sont mortes à `VIT25` en attendant une
suite lancée en arrière-plan. Et la carte de `/vlp:tache` avertit à tort sous `/vlp:enchainer` en mode `main` ; son tampon s'entasse.

**Estimé.** 2,5 fiches · ≈9,93 $ — ≈3,97 $/fiche sur 90 clos (le 2026-10-08).

**Fait.** Rien. Ouvert le 2026-10-08 (TODO n° 105), cadré en 4 fiches, `ARP1` à jouer.

**Session** : 728b4261-6c4f-4698-9547-8070e73a1152

## Le socle commun

**Les trois défauts, et d'où ils viennent** (ligne 105 de la TODO, `context AI/08-etat.md`) :

- **la mort en `-p`** — série 1 de `VIT25` : 8 sessions sur 11 mortes ; série 2, la consigne ajoutée par
  `--append-system-prompt` (un relais `.py` passé en `--claude`) : **12 sur 12** au bout. Le relais est perdu,
  sa consigne aussi : décrite dans `08-etat.md` comme « pas d'arrière-plan, chaque commande au premier plan,
  timeout de 600 000 ms » ;
- **la fausse alerte** — `avertir_session` sort « session déjà notée » dès la 2e fiche jouée par `vlp:tache`
  dans la session du chef (mode `main`) ; vue à `MET8`, `MET9`, `MET10` ;
- **le tampon** — `vlp-carte-<clé>`, écrit par `carte_injectee`, jamais effacé : **1 185** fichiers le 2026-10-07.

**Les symboles** — leur ligne du jour : `py -3 scripts/vlp.py symboles <fichier> <nom>`.

| Symbole | Fichier | Rôle |
|---|---|---|
| `commande` | `scripts/boucle.py` | la ligne de chaque session `-p` ; `commun` sert aux deux branches (`--nuit` ou non) |
| `carte`, `carte_injectee`, `cmd_carte`, `options_carte` | `scripts/vlp_coeur.py` | la carte ; le tampon `vlp-carte-<clé>` (`RELAIS_SECONDES` = 30) ; ses options |
| `avertir_session`, `places_de_session` | `scripts/vlp_coeur.py` | l'alerte ; déjà muette sous `VLP_NUIT=1` ou sans `CLAUDE_CODE_SESSION_ID` |
| `tampon_neuf` | `scripts/vlp_hook.py` | le ménage existant : `vlp-hook-` et `vlp-filet-` de plus de 60 s |
| `carte_sous`, `FICHES_VIT20`, `AVERTI_VIT20` | `scripts/test-vlp.py` | les tests de l'alerte (`VIT20`) |
| `tester_niv1_injection` | `scripts/test-vlp.py` | compare les lignes d'injection des skills |
| `VLP_FAUX_ARGV` | `scripts/faux-claude.py` | le faux `claude` y écrit, une ligne JSON par lancement, les arguments reçus |

**Les noms retenus** (cadrage du 2026-10-08) :

- `PREMIER_PLAN` — la constante de `boucle.py` qui porte la consigne, passée par `--append-system-prompt` ;
- `--enchaine` — l'option de `carte`, posée par l'injection de `skills/enchainer/SKILL.md` ;
- `vlp-enchaine-<id de session>` — la marque, dans `tempfile.gettempdir()`, comme `vlp-carte-` ;
- la marque s'efface après **4 jours** (réponse de l'utilisateur) ; `vlp-carte-` après `RELAIS_SECONDES`.

**Invariants.** La consigne vit **dans `boucle.py` seul** : rien dans `skills/tache/` (cadrage, question 4).
Le plugin chargé suit `main`, pas ce worktree : une skill modifiée ne se voit dans l'app qu'après fusion.
Chaque fiche de code : test dans le fichier de tests nommé, mutant par `vlp.py mutant … --attendu`, pyright 0.

**Dehors.** Un `claude -p` lancé à la main, hors `boucle.py`, reste sans consigne. Les autres fichiers temporaires
du kit. Mesurer l'effet du ménage sur la vitesse de la carte.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `ARP1` | Donner la consigne « premier plan » à toute session `-p` | rien |
| `ARP2` | Essayer la consigne sur une vraie session `-p` | `ARP1` |
| `ARP3` | Taire l'alerte quand `enchainer` joue | rien |
| `ARP4` | Faire le ménage des tampons de la carte | `ARP3` |

`ARP1` et `ARP3` sont indépendantes. `ARP2` coûte de vrais tokens : seule fiche avec un essai payant.

---

<!-- FICHE:ARP1 -->
## ARP1 [x] — Donner la consigne « premier plan » à toute session `-p`

**Session** : 8192d019-ec3d-4e85-bb48-6f9fb56b8259
**Dépend de** : rien.
**Fichiers** : `scripts/boucle.py`, `scripts/test-boucle.py` — et rien d'autre.

**Prompt**
Dans `boucle.py`, écris la constante `PREMIER_PLAN` : la consigne ajoutée au prompt système de toute session `-p`.
💡 Proposé, à garder court : la session est non interactive, rendre la main la termine ; chaque commande se lance au
premier plan, jamais en arrière-plan, avec un timeout jusqu'à 600 000 ms ; n'attendre aucune notification.
Ajoute `--append-system-prompt PREMIER_PLAN` à la liste `commun` de `commande` : un seul endroit pour les
deux branches. Vérifie d'abord que l'option existe dans le vrai `claude` (`py -3 scripts/vlp.py claude`, puis
`<claude> --help`) ; absente, arrête-toi et rends la main. Ajoute une ligne à la docstring de `boucle.py`, là où
elle décrit les options d'une session.
Dans `test-boucle.py`, un cas `ARP1` : avec `VLP_FAUX_ARGV`, une session sans `--nuit` et une session `--nuit`
reçoivent toutes deux `--append-system-prompt` suivi du texte de `PREMIER_PLAN`.

**Critère de fin**
`py -3 scripts/test-boucle.py` : le cas `ARP1` passe, comptes bruts lus dans sa sortie.
Mutant : `py -3 scripts/vlp.py mutant scripts/boucle.py` sur l'ajout de `--append-system-prompt` (le retirer de
`commun`) avec `--attendu "ARP1"` → `MUTANT ATTRAPÉ`. pyright : 0 erreur sur les deux fichiers.
<!-- /FICHE -->

---

<!-- FICHE:ARP2 -->
## ARP2 [x] — Essayer la consigne sur une vraie session `-p`

**Session** : 8192d019-ec3d-4e85-bb48-6f9fb56b8259
**Dépend de** : `ARP1`.
**Fichiers** : `scripts/boucle.py` (lancé, pas modifié), un dossier d'essai dans le scratchpad — et rien d'autre.

**Prompt**
Prouve sur le vrai chemin que la session `-p` va au bout. Pose un bac (`py -3 scripts/vlp.py bac <dossier>`,
dossier du scratchpad), puis remplace sa fiche `F1` par une fiche dont le critère lance une commande longue —
`py -3 -c "import time; time.sleep(200); print('FINI')"`, au-delà des 120 s par défaut de Bash —,
et attend `FINI`. C'est le piège de `VIT25` : la tentation de passer en arrière-plan.
Lance `py -3 scripts/boucle.py <dossier> --plafond 1 --claude <claude> --model claude-opus-5-5 --effort medium
--budget 3`, au premier plan, depuis ce worktree (le `boucle.py` d'`ARP1`).
Puis déclare l'essai : `py -3 scripts/vlp.py essai <motif>`, le motif étant le dossier du bac sous `~/.claude/projects/`.
Lis la trace : la commande longue a-t-elle tourné sans `run_in_background: true` ?
⚠️ Une seule session, sans témoin sans consigne : elle prouve « pas morte », pas « grâce à la consigne » —
la cause, c'est la série 2 de `VIT25` (12 sur 12). Dis-le dans le compte rendu.

**Critère de fin**
La sortie de `boucle.py` montre `F1` cochée, aucune ligne `ARRÊT F1 non cochée`. Dans la trace : l'appel Bash de la
commande longue, `run_in_background` absent ou faux, et `FINI` dans son résultat. La ligne `ESSAI` d'`essai`, et le coût
lu par `vlp.py cout`, à côté de l'estimé (~1,5 à 2 $).
<!-- /FICHE -->

---

<!-- FICHE:ARP3 -->
## ARP3 [ ] — Taire l'alerte quand `enchainer` joue

**Dépend de** : rien.
**Fichiers** : `scripts/vlp_coeur.py`, `skills/enchainer/SKILL.md`, `scripts/test-vlp.py`, `scripts/vlp.py`
(sa docstring) — et rien d'autre.

**Prompt**
Ajoute l'option `--enchaine` à `carte` (`options_carte`). Quand elle est posée et que `CLAUDE_CODE_SESSION_ID` est
non vide, `cmd_carte` crée la marque `vlp-enchaine-<id>` dans `tempfile.gettempdir()` — à chaque appel, même relais :
sous Ubuntu, le premier appel de l'injection échoue. Un id qui n'est pas fait de chiffres, lettres et tirets : pas de marque.
Dans `avertir_session`, la marque de la session présente fait taire l'alerte.
Ajoute `--enchaine` aux trois appels de la ligne d'injection de `skills/enchainer/SKILL.md`. Regarde si
`tester_niv1_injection` compare `enchainer` aux autres skills : si oui, admets-y `--enchaine` comme `--session-neuve`.
Écris la nouvelle option dans la docstring de `vlp.py`, à `carte`.
Dans `test-vlp.py`, près des cas `VIT20` (`carte_sous`) : la marque posée, l'alerte se tait ; la marque d'une autre
session, l'alerte sort encore. Chaque cas dans son propre dossier temporaire.

**Critère de fin**
`py -3 scripts/test-vlp.py` : les cas `ARP3` passent, `VIT20` et `NIV1` aussi, comptes bruts lus dans la sortie.
Mutant : `vlp.py mutant scripts/vlp_coeur.py`, retirer le test de la marque dans `avertir_session`,
`--attendu "ARP3"` → `MUTANT ATTRAPÉ`. pyright : 0 erreur sur les fichiers `.py` touchés.
<!-- /FICHE -->

---

<!-- FICHE:ARP4 -->
## ARP4 [ ] — Faire le ménage des tampons de la carte

**Dépend de** : `ARP3`.
**Fichiers** : `scripts/vlp_hook.py`, `scripts/vlp_coeur.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Avant tout, compte les `vlp-carte-*` et `vlp-enchaine-*` du dossier temporaire :
`py -3 -c "import glob,os,tempfile; d=tempfile.gettempdir(); print([len(glob.glob(os.path.join(d,p))) for p in ('vlp-carte-*','vlp-enchaine-*')])"`.
Le ménage existe déjà dans `tampon_neuf` (`vlp_hook.py`) : sors sa boucle en une fonction de `vlp_hook.py`, qui
prend un dossier et des paires (préfixe, âge en secondes), et qu'appellent `tampon_neuf` (ses deux préfixes, 60 s)
et `carte_injectee` (`vlp-carte-` à `RELAIS_SECONDES`, `vlp-enchaine-` à 4 jours). Une `OSError` sur un
fichier passe au suivant : aujourd'hui, la première arrête toute la boucle. Le tampon frais de l'appel en cours n'est pas
effacé : `carte_injectee` fait le ménage avant d'écrire le sien.
Dans `test-vlp.py`, un cas `ARP4` sur un dossier temporaire : des fichiers vieillis par `os.utime`, chacun effacé
ou gardé selon son préfixe et son âge ; un fichier d'un autre préfixe, gardé.

**Critère de fin**
`py -3 scripts/test-vlp.py` : le cas `ARP4` passe, comptes bruts lus. Mutant : `vlp.py mutant`, l'âge des marques
réduit à celui de `vlp-carte-`, `--attendu "ARP4"` → `MUTANT ATTRAPÉ`. Le compte du début, puis une carte lancée
(`py -3 scripts/vlp.py carte --python "py -3"`), puis le même compte : avant → après, à côté de 1 185.
pyright : 0 erreur sur les fichiers touchés.
<!-- /FICHE -->
