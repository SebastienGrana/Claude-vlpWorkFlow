> **QUAND LIRE** : on joue une fiche `LOC*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache LOC<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier LOC — Une publication refusée n'arrête plus le chantier

**À quoi il sert.** En `BTN6` (2026-09-27), la limite de 200 publications par jour
(`publish 429`) a bloqué la dernière fiche. Le chantier fait qu'une page refusée
attend dans une liste et part plus tard, et qu'on la relit en local en attendant.

**Estimé.** 1 fiches · ≈2,97 $ — ≈2,97 $/fiche sur 78 clos (le 2026-09-28).

**Fait.** Rien. Ouvert le 2026-09-28, cadré en 4 fiches, `LOC1` à jouer.

**Session** : fb3f5228-2d39-4a2d-9910-d73d5ffd4f10

## Le socle commun

Tranché au cadrage (2026-09-28, deux questionnaires) :

- **Les deux volets** : la liste d'attente (`LOC1`–`LOC3`) et l'aperçu local (`LOC4`).
- **La liste** : `<contexte>/artefacts/en-attente`, écrite et lue par `vlp.py` seul.
  Une ligne par page, champs séparés par une tabulation :
  `<page, chemin relatif au dossier artefacts>` · `<url, ou aucune>` · `<heure du refus>`.
  Une page déjà listée n'est pas ajoutée deux fois. Liste vide : le fichier disparaît.
- **La republication, double filet** : une tâche planifiée après la remise à zéro,
  **et** la prochaine commande qui voit la liste non vide dans la carte.
- **`.claude/launch.json`** : écrit par `vlp.py`, et sort du dépôt public (`.gitignore`) —
  il porte des chemins de machine (règle 4 de `CLAUDE.md`). Suivi par Git au
  2026-09-28 (`git ls-files .claude/`), 6 entrées écrites à la main.

Le refus 429, mesuré par `LOC1` : **<à remplir par LOC1 — événement, texte exact,
source, ce qui a bloqué BTN6>**.

| Nom | Où | Ce qu'il fait |
|---|---|---|
| `carte` | `scripts/vlp.py:655` | la carte injectée avant le 1er tour |
| `cmd_filet` | `scripts/vlp.py:1433` | déjà branché sur `PostToolUseFailure` |
| `cmd_vigile` | `scripts/vlp.py:4022` | `PreToolUse` sur `Artifact` : lit `file_path` |
| `cmd_joints` | `scripts/vlp.py:1999` | rend la ligne `FILES` |
| verrou des hooks | `scripts/test-vlp.py:2948` | compte les entrées exactes de `hooks/hooks.json` |

Invariants :

- Une heure écrite vient de `date`, jamais estimée.
- Un hook s'essaie en lui passant son JSON sur l'entrée standard (comme
  `filet_test`, `scripts/test-vlp.py:2739`) : `/reload-plugins` est un geste de
  l'utilisateur, aucune fiche ne l'attend.
- Du Python touché passe `pyright` (compte brut) ; une fiche de code nomme son test
  et son mutant (`methode-chantier.md`, « Anatomie d'une fiche »).
- Aucune nouvelle tentative de publication en boucle : chaque essai use la limite.

**Dehors** : la base `db` (`BDD`), le mode nuit (`NUI`), les verbes Git (`VRB`),
et le nettoyage des 6 entrées actuelles de `launch.json` — le script ne touche que la sienne.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `LOC1` | Mesurer le refus 429 de BTN6 | rien |
| `LOC2` | Tenir la liste d'attente par script | `LOC1` |
| `LOC3` | Écrire la règle et republier la liste | `LOC2` |
| `LOC4` | Regarder les pages en local, sans cache | rien |

`LOC4` est indépendante et peut se jouer à tout moment ; `LOC1` → `LOC2` → `LOC3` en chaîne.

---

<!-- FICHE:LOC1 -->
## LOC1 [ ] — Mesurer le refus 429 de BTN6

**Dépend de** : rien.
**Fichiers** : les transcriptions `~/.claude/projects/*/*.jsonl` (lecture seule),
`context AI/91-publication-refusee.md` (la ligne « Le refus 429 » du socle) — et rien d'autre.

**Prompt**
Trouve les refus de publication par la limite du jour : cherche `publish 429` dans
les transcriptions (kit et Cairn, le 2026-09-27). Pour chaque refus, relève :
- l'événement qui l'a porté : un résultat d'outil en erreur (`is_error`, donc
  `PostToolUseFailure`) ou un résultat normal (`PostToolUse`) ;
- le texte exact du refus, cité court, et ce qu'il dit de la remise à zéro ;
- ce que l'appel `Artifact` portait (`file_path`, `url`) : ce qu'un hook pourrait lire.
Puis dis ce qui a **bloqué** `BTN6` : un critère de fin, une étape de commande, ou
la case — cite la ligne de la fiche ou de la commande. N'écris aucun code.
Remplace la ligne « Le refus 429 » du socle par le résultat, en trois lignes au plus.

**Critère de fin**
La ligne du socle cite : l'événement, le texte, la transcription et sa ligne, la
cause du blocage avec sa source ; le nombre de refus trouvés, compté par
`grep -o "publish 429" <fichiers> | wc -l` (commande donnée). `vlp.py valider` sur
le fichier rend `VALIDE`.
<!-- /FICHE -->

---

<!-- FICHE:LOC2 -->
## LOC2 [ ] — Tenir la liste d'attente par script

**Dépend de** : `LOC1`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `hooks/hooks.json` — et rien d'autre.

**Prompt**
Ajoute la sous-commande `vlp.py attente` (docstring à jour) :
- `attente ajouter <page> [--url URL]` : ajoute la ligne au format du socle, heure
  locale lue sur l'horloge ; rend `ATTENTE <n>` ;
- `attente lister <dossier artefacts>` : une ligne par page, ou rien ;
- `attente retirer <page>` : retire la ligne, efface le fichier vide.
Dans `carte`, une liste non vide ajoute une ligne `ATTENTE=<page> <url>` par page,
avant le fichier de fiches courant.
Si `LOC1` dit que le refus arrive avec le `file_path` de la page : branche
`attente hook` sur l'événement mesuré, `matcher` `Artifact` — il ne réagit qu'au
texte du refus mesuré, ajoute la page, et se tait sur tout le reste. Sinon, pas de
hook : dis-le dans ton rapport, la prose de `LOC3` appellera `attente ajouter`.

**Critère de fin**
Un test dans `scripts/test-vlp.py`, sur un projet bâti en dossier temporaire :
ajouter deux fois la même page → 1 ligne ; retirer → fichier absent ; la carte
montre `ATTENTE=` ; le hook (s'il existe) nourri d'un refus ajoute, nourri d'un
succès n'ajoute rien. Mutant : l'ajout sans le contrôle de doublon → le test
tombe. Suite entière verte (compte brut), `pyright` 0 erreur sur `scripts/vlp.py`.
<!-- /FICHE -->

---

<!-- FICHE:LOC3 -->
## LOC3 [ ] — Écrire la règle et republier la liste

**Dépend de** : `LOC2`.
**Fichiers** : `ARTEFACTS.md`, `cloture.md`, `skills/chantier/SKILL.md`,
`skills/tache/SKILL.md`, `skills/init/SKILL.md` — et `methode-chantier.md`
seulement si `LOC1` dit qu'un critère de fin a bloqué.

**Prompt**
Écris dans `ARTEFACTS.md` une section « Une publication refusée », seul endroit de
la règle : un refus de la limite ne bloque ni la case ni la clôture ; la page va
dans la liste (par le hook, ou par `vlp.py attente ajouter`) ; une tâche planifiée
(`mcp__scheduled-tasks__create_scheduled_task`, une par projet, créée si absente)
la republie après la remise à zéro — l'heure dite par `LOC1` ; une ligne
`ATTENTE=` dans la carte fait republier d'abord (`read`, publication avec `url` et
`files`, puis `attente retirer`). Une page sans `url` se publie comme une première.
Dans les commandes et `cloture.md`, remplace « si une publication échoue, dis-le et
continue » (`skills/chantier/SKILL.md:260`, `skills/init/SKILL.md:148`,
`cloture.md:62`, et `skills/tache/SKILL.md` s'il la porte) par un renvoi d'une
ligne à cette section. `chantier` et `tache`, qui lisent la carte, gagnent une
ligne : `ATTENTE=` → republier d'abord. Rien de plus : chaque ligne se paye à chaque exécution.

**Critère de fin**
`grep -n "Une publication refusée" ARTEFACTS.md` rend 1 titre ; `grep -o` sur les
fichiers de la fiche compte les renvois (compte brut) ; la phrase « dis-le en une
ligne et continue » ne reste qu'aux endroits sans refus possible, listés ;
`vlp.py renvois .` sans nouvel avertissement ; suite `test-vlp.py` verte (compte brut).
<!-- /FICHE -->

---

<!-- FICHE:LOC4 -->
## LOC4 [ ] — Regarder les pages en local, sans cache

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `.gitignore`,
`.claude/launch.json`, `ARTEFACTS.md` — et rien d'autre.

**Prompt**
Ajoute deux sous-commandes (docstring à jour) :
- `vlp.py servir <dossier> <port>` : un `http.server` sur `127.0.0.1`, en-tête
  `Cache-Control: no-store`, types `.html .js .css .svg` en UTF-8 ; le chemin
  `/_telephone?page=<page>` rend la page dans un cadre de 375 px de large ;
- `vlp.py apercu <projet> [--port N]` : écrit ou remplace, dans
  `<projet>/.claude/launch.json`, la seule entrée `apercu-<nom du dossier>`, qui
  lance `servir` sur `<contexte>/artefacts` ; les autres entrées restent à l'octet.
Chemins absolus de ce poste : permis dans ce fichier, qui sort du dépôt —
ajoute `.claude/launch.json` à `.gitignore` et retire-le de l'index par
`git rm --cached` (le fichier reste sur le disque). Dans `ARTEFACTS.md`, une ligne
pointe vers `vlp.py apercu`, sans recopier son détail.

**Critère de fin**
Un test dans `scripts/test-vlp.py`, en dossier temporaire : `apercu` deux fois →
une seule entrée `apercu-…`, une entrée voisine intacte ; `servir` sur un port
libre rend `Cache-Control: no-store` et le cadre 375 px. Mutant : l'en-tête
retiré → le test tombe. Suite verte (compte brut), `pyright` 0 erreur ;
`git ls-files .claude/` ne rend plus `launch.json`.
<!-- /FICHE -->
