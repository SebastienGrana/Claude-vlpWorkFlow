> **QUAND LIRE** : on joue une fiche `REV*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache REV<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier REV — Relire chaque fiche avant son commit

**À quoi il sert.** `/vlp:enchainer` commite un `FAITE` à case cochée sans relire ; la
nuit du 2026-09-24, dix fiches de code sur dix étaient à reprendre (TODO n° 48). Un
relecteur neuf relira chaque `FAITE` avant le commit, et un refus arrêtera la chaîne.

**Fait.** `REV1` à `REV3`. `REV4` jouée une fois, critère non tenu (journal) ; redécoupé le
2026-09-24 : `REV5` à `REV8` avant elle, `REV5` à jouer.

**Session** : 2f9a46f3-70ad-4145-a7c8-ada5aefa0034

**Session** : 2ff884ef-07b2-4fd6-b6aa-85bd9cb386f0

## Le socle commun

**Le circuit visé**, à chaque `FAITE` d'`/vlp:enchainer` — aujourd'hui
`skills/enchainer/SKILL.md:68-74` : `cocher --verifier`, puis le commit.

1. Le chef lance `vlp.py cocher <fichier> <fiche> --verifier` : case `[x]`, et le dernier
   commit n'est pas du sous-agent. Sortie 1 : `RETOUR`, comme aujourd'hui. `SANS GIT` :
   rien ne se commite, fiche suivante sans relecture.
2. `Skill`, `skill: "vlp:relire"`, `args` : `<fiche> [<sha>]` — skill forkée, agent
   `vlp:relecture` neuf. Il lance `vlp.py relecture`, lit le diff entier, rejoue dans
   AVANT puis dans APRÈS les commandes que le diff touche, applique en dernier le mutant
   du critère dans APRÈS, puis `relecture --retirer`. Premier mot : `ACCEPTÉE — <ce qui
   a été rejoué, comptes bruts>` ou `REFUSÉE — <défauts, une ligne>`.
3. `ACCEPTÉE` : le commit d'aujourd'hui, fiche suivante. `REFUSÉE`, ou aucun statut :
   `vlp.py cocher <fichier> <fiche> --refuser "<première ligne du Result>"`, puis arrêt
   comme un `BLOQUÉE` — bilan, page marquée bloquée. La reprise se fait par `/vlp:tache`.

**Décidé au cadrage.** Toute fiche `FAITE` est relue, code ou doc (`MTK2`, de la doc,
disait faux deux fois). Le relecteur tourne sur `opus`, au choix de l'utilisateur —
`sonnet` était proposé.

**Invariants.**
- `HEAD` ne bouge pas avant `ACCEPTÉE` : l'instantané de `relecture` passe par un index
  temporaire (`GIT_INDEX_FILE`), jamais par l'index réel ni par un commit de branche.
- Le relecteur n'écrit jamais sous `PROJET=` et ne lance aucune commande `git` : le
  script crée et retire AVANT et APRÈS (`skills/tache/references/tache-blocage.md:48-51`).
  Une sous-commande qui écrit ne se rejoue que dans AVANT ou APRÈS.
- Le contrat du relecteur vit dans `enchainement.md` ; l'agent, la skill et la méthode y
  renvoient sans le recopier.
- Fiche de code : le test s'écrit d'abord et se voit tomber ; le critère nomme son
  mutant (`methode-chantier.md`, « Anatomie d'une fiche »).

**Ce qui existe** (au 2026-09-24).

| Symbole | Où | Ce qu'il rend |
|---|---|---|
| `cmd_cocher` | `scripts/vlp.py:470` | `--verifier` : `CASE <fiche> [x]` sort 0, `[ ]` sort 1 ; `--date` |
| `fichier_courant` | `scripts/vlp.py:234` | le fichier de fiches d'une carte, `None` s'il vaut « aucun » |
| `cmd_extraire`, `socle` | `scripts/vlp.py:372`, docstring `:17-22` | la fiche entre marqueurs ; le socle |
| `COMMIT_FICHE` | `scripts/vlp.py:955` | `^([A-Z]{1,3}[0-9]+) :` — laisse passer `VAL1:` |
| `verifier(nom, cond, sortie)` | `scripts/test-vlp.py:55` | un test ; dépôts Git bâtis comme à `:490` |
| bloc **Tentatives** | `skills/tache/references/tache-blocage.md:14-19` | son format, sous le titre |
| `skills/jouer/SKILL.md`, `agents/fiche.md` | — | les modèles de la skill et de l'agent neufs |

Une ligne **Fichiers** nomme ses chemins entre accents graves, parfois sur deux lignes et
mêlés de noms de fonction (`context AI/49-cadrage-compte.md`, fiche `CAD1`).

**Les témoins** — commits de sous-agent hors `HEAD` ; leurs défauts sont au journal de
`context AI/08-etat.md`, entrées « <fiche>, relue par le chef ».

| Fiche | Fautif | Corrigé | Défaut du journal |
|---|---|---|---|
| `CAD1` | `e41925c` | `8bb748d` | tests relâchés (cinq `in`) ; session entre marqueur et titre |
| `PLA1` | `eb2a6b0` | `7d16873` | plage écrite deux fois, dans `creer` puis `regenerer` |
| `VAL1` | `72035f2` | `c5123af` | `claude_exe=` non initialisé ; commentaire, message et README repris |

**Dehors.** `/vlp:tache` ; le hook `SubagentStop` (`CON`) ; le `CLAUDE.md` global dans
les sous-agents (`GLO`) ; le modèle de `vlp:fiche` ; un projet sans Git, qui reste sans
relecture.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `REV1` | Préparer la relecture par script | rien |
| `REV2` | Contrôler la tête et refuser par script | rien |
| `REV3` | Écrire le relecteur et le brancher | `REV1`, `REV2` |
| `REV5` | Un commit propre passe sur une copie en CRLF | rien |
| `REV6` | Un en-tête sans plage reste tel quel | rien |
| `REV7` | Le fichier d'état n'est plus hors fiche | rien |
| `REV8` | Refuser ou remarquer | rien |
| `REV4` | Prouver la relecture sur les commits de la nuit | `REV5` à `REV8` |

`REV5` à `REV8`, cadrées après le premier passage de `REV4`, se jouent dans l'ordre du
fichier ; `REV4` en dernier, à la main par le chef. Toutes par `/vlp:tache` : la relecture
n'est pas encore prouvée.

---

<!-- FICHE:REV1 -->
## REV1 [x] — Préparer la relecture par script

**Session** : 2f9a46f3-70ad-4145-a7c8-ada5aefa0034
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (sous-commande `relecture`, docstring du module),
`scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Ajoute la sous-commande `relecture <fiche> [--sha S]`, et `relecture --retirer`. Tests
d'abord, vus en échec.

- Sans `--sha`, un instantané de l'arbre du dépôt courant — suivis et non suivis, selon
  `.gitignore` — en objet commit de parent `HEAD` : index temporaire (`GIT_INDEX_FILE`),
  `read-tree HEAD`, `add -A`, `write-tree`, `commit-tree`. Avec `--sha`, ce commit-là.
- Deux worktrees détachés dans le dossier temporaire du système (`tempfile`) : APRÈS sur
  le commit, AVANT sur son parent ; ceux d'un appel précédent (`vlp-relecture-*`) sont
  retirés d'abord.
- Imprime, dans l'ordre : `APRÈS=<dossier>`, `AVANT=<dossier>`, `FICHIER=<chemin>` — le
  fichier de fiches que nomme la carte d'APRÈS (`fichier_courant`) —, le socle et la
  fiche comme `socle` et `extraire`, `git diff --name-status`, une ligne
  `HORS FICHE <chemin>` par fichier changé absent de la ligne **Fichiers** — hors le
  fichier de fiches et `artefacts/` —, puis le diff entier.
- `--retirer` : `git worktree remove --force` sur chaque `vlp-relecture-*`, puis
  `prune` ; imprime `RETIRÉ <n>`.
- Pas de dépôt, commit inconnu, fiche absente : `GARDE: <raison>`, sort 1.

**Critère de fin**
`py scripts/test-vlp.py` passe, avec trois tests écrits d'abord et vus en échec.
« relecture : l'instantané prend l'arbre sans bouger HEAD » — un fichier modifié et un
non suivi sont dans APRÈS, `HEAD` et `git status --porcelain` identiques avant et après ;
mutant : `add -A` sur l'index réel. « relecture : un fichier hors fiche » — `a.py`
nommé, `b.py` non, le fichier de fiches touché : une seule ligne, `HORS FICHE b.py` ;
mutant : le fichier de fiches plus exclu. « relecture : --retirer » — `git worktree list`
revient à une ligne ; mutant : un seul worktree retiré. Sur le vrai dépôt,
`relecture CAD1 --sha e41925c` imprime `FICHIER=` sur `context AI/49-cadrage-compte.md`
et la fiche `CAD1` ; `--retirer` rend `RETIRÉ 2`.
<!-- /FICHE -->

---

<!-- FICHE:REV2 -->
## REV2 [x] — Contrôler la tête et refuser par script

**Session** : 2f9a46f3-70ad-4145-a7c8-ada5aefa0034
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (`cmd_cocher`, son analyseur d'options, docstring de
`cocher`), `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Deux options de `cocher`. Tests d'abord, vus en échec.

- `--verifier` garde sa ligne `CASE`, et lit en plus le dernier commit du dépôt du
  fichier de fiches : si son sujet nomme la fiche — `^<fiche>\s*:`, qui prend aussi le
  `VAL1:` que `COMMIT_FICHE` laisse passer —, il ajoute `TÊTE <sha> <sujet>` et sort 1.
  Hors d'un dépôt Git : une ligne `SANS GIT`, et la sortie ne dépend que de la case.
- `--refuser <motif>` remet `[ ]` sur le titre, et écrit juste sous lui le bloc de
  `tache-blocage.md` : `**Tentatives** (<date>) — non résolu.`, `1. FAITE refusée à la
  relecture.`, `Erreur : <motif>`. Un bloc déjà là ne se double pas : il gagne la ligne
  numérotée suivante, et son `Erreur :` prend le nouveau motif. `--date` fixe la date,
  comme pour `--resolu`. Imprime `REFUSÉ <fiche>` ; fiche introuvable : `GARDE:`, sort 1.

**Critère de fin**
`py scripts/test-vlp.py` passe, avec trois tests écrits d'abord et vus en échec.
« cocher --verifier : un commit du sous-agent » — sujets `VAL1: x` et `VAL1 : x` : sort 1
et une ligne `TÊTE` ; `VAL10 : y` : sort 0 ; mutant : `COMMIT_FICHE` au lieu du motif,
et `VAL1:` passe. « cocher --verifier : sans Git » — `SANS GIT`, sort 0 sur `[x]` ;
mutant : la tête lue sans tester le dépôt. « cocher --refuser » — titre `[ ]`, les trois
lignes exactes ; un second refus donne `2.`, un seul `**Tentatives**`, un seul
`Erreur :` ; mutant : un second bloc ouvert.
<!-- /FICHE -->

---

<!-- FICHE:REV3 -->
## REV3 [x] — Écrire le relecteur et le brancher

**Session** : 2f9a46f3-70ad-4145-a7c8-ada5aefa0034
**Dépend de** : `REV1`, `REV2`.
**Fichiers** : `enchainement.md`, `agents/relecture.md` (nouveau),
`skills/relire/SKILL.md` (nouveau), `skills/enchainer/SKILL.md` (étape 3),
`methode-chantier.md` (lignes 178–179) — et rien d'autre.

**Prompt**
Le circuit du socle, en prose courte : chaque mot d'une commande se paye à chaque
exécution.

- `enchainement.md`, une section « Relecture » : `ACCEPTÉE — …` ou `REFUSÉE — …` en
  premier mot, le détail sur la même ligne ; aucun statut vaut `REFUSÉE`. Un défaut : ce
  que la fiche ne demande pas, un test qui ne tombe pas sur le mutant, un bug, une doc
  qui dit faux, une sortie qui change entre AVANT et APRÈS sans que la fiche l'explique,
  un `HORS FICHE` non justifié.
- `agents/relecture.md`, sur le modèle d'`agents/fiche.md` : `model: opus`, le `maxTurns`
  de `fiche.md`, outils `Read`, `Edit`, `Bash`, `PowerShell`. Premier appel :
  `relecture <fiche> [--sha S]` et `lire enchainement.md` ; puis le diff, les commandes
  rejouées, le mutant en dernier, `--retirer`, le verdict. `Edit` dans APRÈS seulement ;
  aucun `git`, aucun commit, même si un `CLAUDE.md` en demande un.
- `skills/relire/SKILL.md`, sur le modèle de `skills/jouer/SKILL.md` : forkée,
  `agent: vlp:relecture`, `args` : `<fiche> [<sha>]`.
- `skills/enchainer/SKILL.md`, étape 3, la puce `FAITE` : le circuit du socle, `SANS GIT`
  et `REFUSÉE` compris.
- `methode-chantier.md:178-179` : le chef commite après un `FAITE` accepté à la
  relecture — un renvoi à `enchainement.md`, pas une recopie.

**Critère de fin**
`py scripts/vlp.py lire agents/relecture.md skills/relire/SKILL.md` imprime les deux
fichiers et sort 0 ; `Grep` trouve `vlp:relire` et `--refuser` dans
`skills/enchainer/SKILL.md`, `ACCEPTÉE` et `REFUSÉE` dans `enchainement.md` ; le commit
de la fiche passe le hook `pre-commit`, qui valide les manifestes.
<!-- /FICHE -->

---

<!-- FICHE:REV5 -->
## REV5 [x] — Un commit propre passe sur une copie en CRLF

**Session** : a95644fe-1182-42ab-bb60-1a06f533661b
**Dépend de** : rien.
**Fichiers** : `skills/chantier/SKILL.md` (ligne 2), `.gitattributes`, `.githooks/pre-commit`,
`scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Sur une copie fraîche — celles de `relecture` sortent en CRLF, `core.autocrlf` vaut `true`
ici —, le hook refuse un commit propre : `claude.exe` rejette l'en-tête YAML de
`skills/chantier/SKILL.md`, la seule description de `skills/` et `agents/` qui contient
« : ». Preuve : journal de `context AI/08-etat.md`, entrée « REV4, jouée à la main par le
chef ». Mesuré au cadrage, `claude.exe` 2.1.280 sur une copie du plugin : CRLF, code 1 ;
CRLF et description entre guillemets, 0 ; LF, 0. Décidé avec l'utilisateur : guillemets et
`.gitattributes` tous deux, et le bon manifeste nommé. Tests d'abord, vus en échec.

- `skills/chantier/SKILL.md:2` : la description entre guillemets doubles.
- `.gitattributes` : `*.md text eol=lf`. L'index est déjà en LF (81 `.md`,
  `git ls-files --eol`) : rien à renormaliser.
- `.githooks/pre-commit:19` : `plugin.json` validé avant `marketplace.json`. Valider
  `marketplace.json` lit aussi `plugin.json` : un `plugin.json` cassé fait nommer
  `marketplace.json` (relecture de `c5123af`) — le critère de `VAL1`, jamais tenu.
- Les tests du hook le lancent par `git commit`, dans un dépôt temporaire où le plugin est
  copié, ses `.md` en CRLF. Sans `claude.exe`, le hook dit « validate sauté » : le test lit
  ce message et imprime `SAUTÉ: claude introuvable — …`, comme `scripts/test-vlp.py:1735`.

**Critère de fin**
`py scripts/test-vlp.py` passe sur ce poste, sans ligne `SAUTÉ: claude`, avec trois tests
écrits d'abord et vus en échec. « hook : une copie en CRLF passe » — code 0 ; mutant : la
description sans guillemets. « hook : plugin.json cassé est nommé » — `plugin.json` réduit
à `{` : code 1, `plugin.json` nommé, `marketplace.json` non ; mutant : l'ordre actuel de la
boucle. « .gitattributes : les .md en LF » — `git check-attr eol` rend `lf` sur
`skills/chantier/SKILL.md` ; mutant : la ligne retirée. Le commit de la fiche passe le hook.
<!-- /FICHE -->

---

<!-- FICHE:REV6 -->
## REV6 [x] — Un en-tête sans plage reste tel quel

**Session** : fedafcd5-3d99-48d7-ac85-c9f0d96b67ba
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (`regenerer`, ligne 1457), `scripts/test-vlp.py` — et rien
d'autre.

**Prompt**
`scripts/vlp.py:1457` rend la plage de l'en-tête facultative : « vlp · fiches à venir »
devient « vlp · fiches PLA1–PLA2à venir ». Latent : aucune page réelle touchée. Preuve :
relecture de `7d16873`, journal de `context AI/08-etat.md`, entrée « REV4, jouée à la main
par le chef ». Tests d'abord, vus en échec.

- La plage suit le fichier quand l'en-tête en porte une (`PLA1`, `PLA1–PLA2`) ou quand elle
  est vide, comme l'écrit `creer` (`scripts/vlp.py:1386`) — suivie de `</div>`, ou de
  « · clos » écrit à la main.
- Tout autre en-tête reste tel quel : « fiches à venir », « fiches (PLA1–PLA2) », « fiches
  PLA1-PLA2 » au trait d'union.
- Piste du relecteur : `(?:…|(?=</div>))` au lieu du `?` final. Vérifie-la sur le trait
  d'union : le jeton `PLA1` seul y correspond encore.

**Critère de fin**
`py scripts/test-vlp.py` passe, avec un test écrit d'abord et vu en échec : « page : un
en-tête sans plage reste tel quel » — les trois en-têtes ci-dessus inchangés par `page` ;
mutant : la regex actuelle. « page : l'en-tête suit la plage du fichier » et « page :
l'en-tête d'une fiche seule » (`scripts/test-vlp.py:430`, `:437`) passent toujours.
<!-- /FICHE -->

---

<!-- FICHE:REV7 -->
## REV7 [x] — Le fichier d'état n'est plus hors fiche

**Session** : fedafcd5-3d99-48d7-ac85-c9f0d96b67ba
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (`cmd_relecture`, docstring du module lignes 67–68),
`scripts/test-vlp.py` — et rien d'autre.

**Prompt**
`vlp.py relecture` imprime `HORS FICHE` pour le fichier d'état, où toute fiche peut écrire
au journal (« Une ligne par décision imprévue tranchée en cours de fiche »,
`context AI/08-etat.md:274`). Sur `8bb748d`, c'était sa seule ligne `HORS FICHE` (journal,
entrée « REV4, jouée à la main par le chef »). Tests d'abord, vus en échec.

- `scripts/vlp.py:698` exclut le fichier de fiches et `artefacts/` ; y ajouter le chemin que
  nomme la ligne **fichier d'état** du `CHANTIER.md` d'APRÈS — `champ`
  (`scripts/vlp.py:1629`), préfixé comme `fiches_rel` (`:695`). Ligne absente ou « aucun » :
  rien de plus n'est exclu.
- La docstring du module (`scripts/vlp.py:67-68`) le dit.

**Critère de fin**
`py scripts/test-vlp.py` passe, avec « relecture : un fichier hors fiche »
(`scripts/test-vlp.py:1779`) étendu d'abord et vu en échec : le fichier d'état touché lui
aussi, toujours une seule ligne, `HORS FICHE b.py` ; mutant : le fichier d'état plus exclu.
Sur le vrai dépôt, `relecture CAD1 --sha 8bb748d` n'imprime aucune ligne `HORS FICHE`, puis
`relecture --retirer` rend `RETIRÉ 2`.
<!-- /FICHE -->

---

<!-- FICHE:REV8 -->
## REV8 [x] — Refuser ou remarquer

**Session** : fedafcd5-3d99-48d7-ac85-c9f0d96b67ba
**Dépend de** : rien.
**Fichiers** : `enchainement.md` (section « Relecture ») — et rien d'autre.

**Prompt**
Au premier passage de `REV4` (journal de `context AI/08-etat.md`, entrée « REV4, jouée à la
main par le chef »), le relecteur a rangé en remarques des défauts des témoins (`eb2a6b0`,
`72035f2`), et pris pour motifs des écarts sans effet sur une sortie (`8bb748d`, `7d16873`,
`c5123af`). La liste d'`enchainement.md:35-38` ne dit pas ce qui refuse. Décidé avec
l'utilisateur au cadrage, une règle la remplace :

- `REFUSÉE` pour trois motifs, et eux seuls : le critère de fin non tenu ; un bug qu'une
  sortie prouve — du code, ou une doc, qu'une commande rejouée contredit ; un mutant du
  critère qui survit.
- Le reste — la lettre de la fiche, un `HORS FICHE`, le style, un écart sans effet sur une
  sortie — se remarque, sous la ligne du verdict, sans le changer.
- `REFUSÉE — <les motifs, une ligne>` : les motifs seuls, pas les remarques.

Prose courte : l'agent relit cette section à chaque relecture (`agents/relecture.md`).

**Critère de fin**
`Grep` trouve dans `enchainement.md` « remarque » et « les motifs », et n'y trouve plus
« Un défaut : » ; il ne trouve « remarque » ni dans `agents/relecture.md` ni dans
`skills/relire/SKILL.md`, qui renvoient sans recopier. Le commit de la fiche passe le hook.
<!-- /FICHE -->

---

<!-- FICHE:REV4 -->
## REV4 [ ] — Prouver la relecture sur les commits de la nuit

**Session** : dbf37a72-d55e-44f2-8cb7-9d3731712ba1
**Dépend de** : `REV5`, `REV6`, `REV7`, `REV8`.
**Fichiers** : `context AI/08-etat.md` (une entrée au journal) — et rien d'autre.

**Prompt**
Deuxième passage. Le premier est au journal de `context AI/08-etat.md`, entrée « REV4,
jouée à la main par le chef » : ses coûts servent d'estimation, renvoie-y sans les recopier.
Son critère, « corrigé = accepté », était faux : deux corrigés portent un bug prouvé.

Avant la fiche, l'utilisateur fait `/reload-plugins` : une définition d'agent se charge au
démarrage (TODO n° 49, `CON`). `vlp:relecture` absent de ta liste d'agents : rends la main.

Lance `Skill`, `skill: "vlp:relire"`, une relecture à la fois, `CAD1 8bb748d` seul d'abord.
Mesure son coût en tours, tokens et $ par `scripts/mesure-tokens.py` sur la transcription du
sous-agent (sa docstring dit comment), et attends l'accord avant `PLA1 7d16873`,
`VAL1 c5123af`, puis `PLA1 eb2a6b0` — ajouté par l'utilisateur : son mutant qui survit était
rangé en remarque.

Après chaque relecture : `git worktree list` et `git status` n'ont pas bougé depuis le
départ. Un verdict contraire au critère : dis quelle règle d'`enchainement.md` il applique
mal ; ne change pas de modèle, c'est à l'utilisateur d'en décider. Écris la table au journal
de `08-etat.md`, datée.

**Critère de fin**
Une table de quatre lignes — commit · verdict · motifs · remarques · tours · tokens · $ — où
`8bb748d` est `ACCEPTÉE` (`REV7`, `REV8`) ; `7d16873` `REFUSÉE` pour sa plage facultative
(`REV6`) ; `c5123af` `REFUSÉE` pour le hook qui refuse un commit propre (`REV5`) ; `eb2a6b0`
`ACCEPTÉE`, le mutant de `creer` rejoué et sa survie en remarque, sortie citée — il n'est pas
celui du critère de `PLA1` (`context AI/47-plage-suit.md:31`), `REV8` le range en remarque.
Dessous, le coût moyen d'une relecture, face au premier passage.
<!-- /FICHE -->
