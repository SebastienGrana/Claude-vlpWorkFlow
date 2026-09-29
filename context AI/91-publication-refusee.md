> **QUAND LIRE** : on joue une fiche `LOC*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache LOC<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier LOC — Une publication refusée n'arrête plus le chantier

**À quoi il sert.** En `BTN6` (2026-09-27), la limite de 200 publications par jour
(`publish 429`) a bloqué la dernière fiche. Le chantier fait qu'une page refusée
attend dans une liste et part plus tard, et qu'on la relit en local en attendant.

**Estimé.** 1 fiches · ≈2,97 $ — ≈2,97 $/fiche sur 78 clos (le 2026-09-28).

**CLOS** le 2026-09-29. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** LOC1..LOC5 (2026-09-29) : la liste d'attente des pages refusées (attente ajouter/lister/retirer/hook, hooks sur Artifact), sa règle dans ARTEFACTS.md et l'aperçu local sans cache (apercu, /_telephone à 375 px), essayés pour de vrai — estimé 1 fiches ≈2,97 $ · cadré 5 · joué 5 fiches 11,74 $.

**Session** : fb3f5228-2d39-4a2d-9910-d73d5ffd4f10

## Le socle commun

Tranché au cadrage (2026-09-28, trois questionnaires, notes `PUB` comprises) :

- **Les deux volets** : la liste d'attente (`LOC1`–`LOC3`), l'aperçu local (`LOC4`),
  puis l'essai réel des deux (`LOC5`).
- **La liste** : `<contexte>/artefacts/en-attente`, écrite et lue par `vlp.py` seul.
  Une ligne par page, champs séparés par une tabulation :
  `<page, chemin relatif au dossier artefacts>` · `<url, ou aucune>` · `<heure du refus>`.
  Clé : la page — une nouvelle entrée remplace l'ancienne (la dernière gagne).
  Écriture dans un `.tmp` puis `os.replace`. Liste vide : le fichier disparaît.
  Une page jamais publiée (`aucune`) y entre : republiée, son url s'écrit par `cmd_lien`.
- **Les hooks sur `Artifact`** : un refus 429 ajoute la page et, une fois par jour et
  par projet, propose par `additionalContext` une tâche planifiée à la remise à zéro
  + 10 min, en heure locale, calculée depuis un `maintenant` passé en paramètre ; une
  publication réussie d'une page listée la retire. Chaque hook part deux fois
  (`python3` puis `py`) : idempotent. Tout autre refus (page non lue, vigile) : silence.
- **La republication, double filet** : la tâche planifiée — proposée, créée sur un oui
  de l'utilisateur — **et** la prochaine commande qui voit `ATTENTE=` dans la carte.
- **`.claude/launch.json`** : écrit par `vlp.py`, et sort du dépôt public (`.gitignore`) —
  il porte des chemins de machine (règle 4 de `CLAUDE.md`). Suivi par Git au
  2026-09-28 (`git ls-files .claude/`), 6 entrées écrites à la main.

Le texte du 429, relevé le 2026-09-27 (`context AI/88-boutons.md:352`) :
`publish 429: daily publish limit for your plan reached (200) — resets at UTC midnight`.
Mesuré par `LOC1` (2026-09-29 ; 4 résultats `Artifact` en 429 sur 223 occurrences brutes hors la session de `LOC1` (269 avec elle) de
`grep -o "publish 429" ~/.claude/projects/*/*.jsonl | wc -l` : le reste est de la discussion) :
- **429** : `is_error` vrai → `PostToolUseFailure` (kit `9c178cca`:1069 ; Cairn `ad875ef2`:2323) ; texte dans `error` (exemple de la doc, `1cba232a`:1756) ; appel = `file_path`, + `url` et `files` en republication (`9c178cca`:1062), sans `url` pour une page neuve. « Page non lue » : même événement, autre texte (`747d5037`:257) → trier par le texte. Vigile : `PreToolUse` (`aeb2fbf2`:404), qu'un `Post*` suive n'est pas établi.
- **Blocage de BTN6** : son prompt, « Republie chacune à son URL » (`88-boutons.md:322`), et son critère `(visuel)` (`:328`) ; l'étape 6 bis, elle, dit « Échec : une ligne, et continue » et n'a pas bloqué (`9c178cca`:1073, :1079).
- **`LOC5`, sans user la limite** : le refus vigile (page cassée, local) ; « non lue », probable, non mesuré ; le 429 seulement en JSON sur l'entrée standard.

| Nom | Où | Ce qu'il fait |
|---|---|---|
| `carte` | `scripts/vlp.py:655` | la carte injectée avant le 1er tour |
| `cmd_filet` | `scripts/vlp.py:1433` | `PostToolUse`/`PostToolUseFailure`, `additionalContext` |
| `cmd_vigile_hook`, `une_fois` | `scripts/vlp.py:4037`, `:422` | modèle de hook sur `Artifact` |
| `tampon_neuf` | `scripts/vlp.py:400` | une fois par nom |
| `trouver` | `scripts/vlp.py:552` | le projet d'un `file_path` |
| `champ(…, "contexte", "context AI/")` | `scripts/vlp.py:3338` | le dossier de contexte |
| `recopier_joints`, `ligne_files` | `scripts/vlp.py:1976`, `:1992` | la ligne `FILES` |
| `cmd_lien` | `scripts/vlp.py:3670` | écrit l'url d'une page |
| verrou des hooks | `scripts/test-vlp.py:2948` | compte les entrées exactes de `hooks/hooks.json` |

Invariants :

- Une heure écrite vient de l'horloge (`date`), jamais estimée.
- Un hook s'essaie en lui passant son JSON sur l'entrée standard (comme
  `filet_test`, `scripts/test-vlp.py:2739`). `/reload-plugins` est un geste de
  l'utilisateur : seule `LOC5` le demande.
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
| `LOC5` | Essayer la liste et l'aperçu pour de vrai | `LOC3`, `LOC4` |

`LOC4` est indépendante ; `LOC1` → `LOC2` → `LOC3` en chaîne ; `LOC5` en dernier.

---

<!-- FICHE:LOC1 -->
## LOC1 [x] — Mesurer le refus 429 de BTN6

**Session** : ae4ad37c-5d78-4003-b1ce-e63a8a4ece48
**Dépend de** : rien.
**Fichiers** : les transcriptions `~/.claude/projects/*/*.jsonl` (lecture seule),
`context AI/91-publication-refusee.md` (la ligne « Mesuré par LOC1 » du socle) — et rien d'autre.

**Prompt**
Le texte du 429 est connu (socle). Dans les transcriptions, trouve les appels
`Artifact` refusés par `publish 429` (kit et Cairn, le 2026-09-27) et relève :
- si le résultat d'outil porte `is_error` : l'événement est alors `PostToolUseFailure`,
  sinon `PostToolUse` ;
- ce que l'appel portait (`file_path`, `url`, `files`) : ce qu'un hook pourra lire ;
- ce qui a **bloqué** `BTN6` : un critère de fin, une étape de commande, ou la case —
  cite la ligne.
Fais de même pour deux autres refus, qui ne doivent **pas** entrer dans la liste :
une page non lue avant republication, et un refus de `vlp.py vigile`
(`Page cassée, publication refusée`). Dis lequel `LOC5` peut provoquer sans user la
limite. N'écris aucun code. Remplace la ligne « Mesuré par LOC1 » par le résultat,
en quatre lignes au plus.

**Critère de fin**
La ligne du socle cite, pour chacun des trois refus : l'événement, la transcription et
sa ligne ; plus la cause du blocage avec sa source. Nombre de 429 trouvés, compté par
`grep -o "publish 429" <fichiers> | wc -l` (commande donnée). `vlp.py valider` sur le
fichier rend `VALIDE`.
<!-- /FICHE -->

---

<!-- FICHE:LOC2 -->
## LOC2 [x] — Tenir la liste d'attente par script

**Session** : ae4ad37c-5d78-4003-b1ce-e63a8a4ece48
**Dépend de** : `LOC1`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `hooks/hooks.json` — et rien d'autre.

**Prompt**
Ajoute la sous-commande `vlp.py attente` (docstring à jour), au format du socle :
- `attente ajouter <page> [--url URL]` rend `ATTENTE <n>` ; `attente lister <dossier
  artefacts>` ; `attente retirer <page>`.
- Dans `carte`, une liste non vide ajoute une ligne `ATTENTE=<page> <url>` par page,
  avant le fichier de fiches courant.
- `attente hook`, sur le modèle de `cmd_vigile_hook` et `une_fois`, branché dans
  `hooks/hooks.json` sur l'événement mesuré par `LOC1`, `matcher` `Artifact` :
  - refus au texte du 429 → ajoute la page ; la première fois du jour pour ce
    projet (`tampon_neuf`), rend en `additionalContext` (forme de `cmd_filet`) :
    « remise à zéro à <HH:MM> locale ; propose une tâche planifiée à <HH:MM+10> qui
    republie la liste » — heure calculée d'un `maintenant` en paramètre ;
  - publication réussie (`PostToolUse`) d'une page listée → la retire ;
  - tout le reste, dont les deux autres refus de `LOC1` → rien, code 0.

**Critère de fin**
Un test dans `scripts/test-vlp.py`, sur un projet bâti en dossier temporaire :
ajouter deux fois la même page → 1 ligne, la seconde url ; retirer la dernière → fichier
absent ; la carte montre `ATTENTE=` ; hook nourri d'un 429 → ajout, et proposition au
premier appel seulement du jour ; d'un succès → retrait ; d'un refus vigile → rien ;
`maintenant` = 2026-09-28 20:00 en UTC+2 → `02:00`, tâche à `02:10`. Mutant : sans
`tampon_neuf`, la proposition revient au second appel → le test tombe. Suite entière
verte (compte brut), `pyright` 0 erreur sur `scripts/vlp.py`.
<!-- /FICHE -->

---

<!-- FICHE:LOC3 -->
## LOC3 [x] — Écrire la règle et republier la liste

**Session** : aefeee39-49c3-4e7e-9f88-608b0b6fdcd9
**Dépend de** : `LOC2`.
**Fichiers** : `ARTEFACTS.md`, `cloture.md`, `skills/chantier/SKILL.md`,
`skills/tache/SKILL.md`, `skills/tache/references/tache-page.md`,
`skills/init/SKILL.md` — et `methode-chantier.md` seulement si `LOC1` dit qu'un
critère de fin a bloqué.

**Prompt**
Écris dans `ARTEFACTS.md` une section « Une publication refusée », seul endroit de
la règle : un refus 429 ne bloque ni la case ni la clôture ; le hook note la page et
propose la tâche planifiée — la session la **propose** à l'utilisateur, et ne la crée
(`mcp__scheduled-tasks__create_scheduled_task`, une par projet) que sur son oui ; une
ligne `ATTENTE=` dans la carte fait republier d'abord (`read`, puis publication avec
`url` et `files`) — le hook retire la ligne ; une page sans url se publie comme une
première, puis `vlp.py lien` écrit son url. Les autres refus se corrigent, ils
n'attendent pas.
Remplace « échec : une ligne, et continue » (`skills/chantier/SKILL.md:255-261`,
`skills/init/SKILL.md:148`, `cloture.md:62`, `skills/tache/references/tache-page.md:27`)
par un renvoi d'une ligne à cette section. `chantier` et `tache`, qui lisent la carte,
gagnent une ligne : `ATTENTE=` → republier d'abord. Rien de plus : chaque ligne se
paye à chaque exécution.

**Critère de fin**
`grep -n "Une publication refusée" ARTEFACTS.md` rend 1 titre ; `grep -o` sur les
fichiers de la fiche compte les renvois (compte brut) ; la phrase d'échec ne reste
qu'aux endroits sans refus possible, listés ; `vlp.py renvois .` sans nouvel
avertissement ; suite `test-vlp.py` verte (compte brut).
<!-- /FICHE -->

---

<!-- FICHE:LOC4 -->
## LOC4 [x] — Regarder les pages en local, sans cache

**Session** : 5167a129-bd7e-438c-b2ff-699c419c1204
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
  Dans un projet équipé où `git check-ignore` ne couvre pas `.claude/launch.json`,
  il écrit quand même et rend une `GARDE:` qui le dit.
Chemins absolus de ce poste : permis dans ce fichier, qui sort du dépôt —
ajoute `.claude/launch.json` à `.gitignore` et retire-le de l'index par
`git rm --cached` (le fichier reste sur le disque). Dans `ARTEFACTS.md`, une ligne
pointe vers `vlp.py apercu`, sans recopier son détail.

**Critère de fin**
Un test dans `scripts/test-vlp.py`, en dossier temporaire : `apercu` deux fois →
une seule entrée `apercu-…`, une entrée voisine intacte ; sans `.gitignore` → `GARDE:` ;
`servir` sur un port libre rend `Cache-Control: no-store` et le cadre 375 px. Mutant :
l'en-tête retiré → le test tombe. Suite verte (compte brut), `pyright` 0 erreur ;
`git ls-files .claude/` ne rend plus `launch.json`.
<!-- /FICHE -->

---

<!-- FICHE:LOC5 -->
## LOC5 [x] — Essayer la liste et l'aperçu pour de vrai

**Session** : 4a29d6d4-1615-4d98-80ec-d0563c86f8e9
**Dépend de** : `LOC3`, `LOC4`.
**Fichiers** : `context AI/artefacts/91-publication-refusee.html` (republiée),
`context AI/artefacts/vlp.css` (modifié puis rendu à l'octet) — et rien d'autre.

**Prompt**
Demande d'abord à l'utilisateur `/reload-plugins` : les hooks de `LOC2` ne tournent
qu'après. Puis, sur le kit :
1. provoque le refus que `LOC1` a dit provocable : la liste ne doit **pas** bouger ;
2. `vlp.py attente ajouter` la page du chantier avec son url → `ATTENTE 1`, et la carte
   montre `ATTENTE=` ; republie comme la section de `LOC3` le dit → la liste se vide
   par le hook, sans `attente retirer` ;
3. `vlp.py apercu .`, lance l'entrée par `preview_start`, ouvre la page et la feuille
   dans `/_telephone` ; change une couleur de `vlp.css`, recharge : elle se voit sans
   vider le cache ; rends `vlp.css` à l'octet.
Le chemin du vrai 429 n'est prouvé que par le test de `LOC2` : dis-le, ne l'invente pas.

**Critère de fin** (visuel)
`attente lister` avant/après à chaque pas (comptes bruts) ; `git diff --stat
context AI/artefacts/vlp.css` vide à la fin ; l'utilisateur voit la page à 375 px et le
changement de couleur au simple rechargement, et le dit.
<!-- /FICHE -->
