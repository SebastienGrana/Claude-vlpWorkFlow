> **QUAND LIRE** : on joue une fiche `JNT*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache JNT<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier JNT — Une republication ne joint que les joints changés

**À quoi il sert.** Chaque republication passe `vlp.css`, `vlp.js` (et `couts.svg` sur la
feuille) dans `files` ; quand leurs octets diffèrent de la version en ligne, l'outil `Artifact`
refuse (« joints non lus ») et force une relecture. Après JNT, seuls les joints changés partent.

**Estimé.** 3 fiches · ≈9,00 $ — ≈3,00 $/fiche sur 86 clos (le 2026-09-29).

**Fait.** Rien. Ouvert le 2026-09-29, cadré en 3 fiches, `JNT1` à jouer.

**Session** : b293bb0b-835f-4938-bedc-3114bdb5643a

## Le socle commun

**Mesuré au cadrage (2026-09-29)** :
- les joints du kit sont en **LF dans l'index** et suivent `core.autocrlf` sur disque
  (`git ls-files --eol` : `i/lf w/crlf`) ; `.gitattributes` ne fixe que `*.sh`, `.githooks/*`, `*.md` ;
- `templates/vlp.css` 11 066 octets et `templates/vlp.js` 8 206 dans ce worktree (CRLF) — les
  tailles en ligne ; dans un worktree LF, 10 942 et 8 022 : le refus dépend du worktree ; et
  du `vlp.py` lancé : celui du plugin recopie les gabarits du dossier principal (LF) — la page
  de ce chantier est partie avec 10 942 octets de `vlp.css` ;
- `couts.svg` s'écrit par `vlp.py` en LF (1 ligne), identique partout ;
- l'essai « sans `files`, les joints restent » : fait une fois, version 185 de la feuille
  (`list` `scope: "files"`, tailles inchangées) ; la doc de l'outil le dit aussi.

**Où ça vit** dans `scripts/vlp.py` : `JOINTS` et `recopier_joints` (~l. 2082), `ligne_files`
(~l. 2101), ses trois appelants (`page`, `feuille`, `archive`) et `cmd_joints` ; le hook
`cmd_attente_hook` (~l. 4432), lancé après chaque `Artifact` (`hooks/hooks.json`). La règle :
`ARTEFACTS.md`, « Où vivent le CSS et les données » (« Chaque publication, même une
republication, passe `files` ») et « Une publication refusée ».

**Tranché au cadrage (l'utilisateur)** :
- savoir qu'un joint a changé = **une empreinte notée** par le hook après chaque publication
  réussie, par page ; la ligne `FILES` ne nomme que les joints dont l'empreinte diffère ; page
  jamais notée : tous, comme aujourd'hui ;
- les **fins de ligne dedans** : `.gitattributes` fixe `eol=lf` pour `.css`, `.js`, `.svg` ;
- une **fiche de mesure** d'abord, pour chiffrer le gain.

**Invariant** : une première publication passe toujours tous les joints ; un joint changé part
toujours. Un refus « joints non lus » sur un joint **réellement changé** reste légitime.

**Dehors** : les pages des autres projets (chacun republie à son rythme) ; la base `db` (`BDD`) ;
le paramètre `overwrite_unread` de l'outil (réservé à une demande explicite de l'utilisateur).

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `JNT1` | Compter les refus « joints non lus » | rien |
| `JNT2` | Les joints en LF partout | rien |
| `JNT3` | `FILES` ne nomme que les joints changés | `JNT2` |

---

<!-- FICHE:JNT1 -->
## JNT1 [x] — Compter les refus « joints non lus »

**Session** : b293bb0b-835f-4938-bedc-3114bdb5643a
**Dépend de** : rien.
**Fichiers** : aucun à modifier ; le résultat va dans ce fichier, sous la fiche (« Mesuré »).

**Prompt**
Sans code. Dans les transcriptions du kit (`~/.claude/projects/*vlpWorkflow*/*.jsonl`, lues par
`grep`/`py -c`, jamais ouvertes en entier), compter : (a) les résultats d'outil `Artifact` en
échec dont le texte dit un joint non lu — relever le texte exact d'un exemple ; (b) les
publications réussies, avec et sans `files` ; (c) le nombre de sessions touchées. En déduire
refus par publication. Chercher aussi un cas où un joint passé dans `files`, jamais lu dans la
session, n'a **pas** été refusé : dire s'il existe, ou « non trouvé ».

**Critère de fin**
1. Une section « Mesuré » sous cette fiche : les trois comptes bruts, la commande qui les
   rejoue, le texte exact du refus, et le cas « joint identique passé » ou « non trouvé ».

**Mesuré** (2026-09-29) — `py "context AI/99-jnt1-mesure.py"` (kit) ; motif `"*"` : tous projets.
- Kit : **187** publications avec `files`, 537 sans, 156 sessions ; **14 refus** « joints non
  lus » dans **12** sessions — **7,5 %** des publications avec `files` (14/187), 7,7 % des
  sessions qui publient (12/156). Tous projets : **23** refus sur 273 (8,4 %), 19 sessions sur 298.
- Texte exact : « Nothing was published or removed: this publish touches files whose published
  content is not what you last saw, and sending your copy could discard content you have not read. »
- Joint identique passé : **trouvé**, faisceau — **34** republications avec `files` réussies
  (sur 112) sans que la session ait publié ni lu les joints de cette page avant (tous projets :
  47 / 168). Une republication réussie prouve que les joints en ligne valaient ceux du disque.
- Observé au cadrage : un joint **changé** (CRLF → LF) passe sans refus quand la session l'a
  publié elle-même plus tôt (feuille, version 188).
- Un `grep` sur le texte compte aussi les citations : 13 fichiers, 76 occurrences.
<!-- /FICHE -->

---

<!-- FICHE:JNT2 -->
## JNT2 [x] — Les joints en LF partout

**Session** : b293bb0b-835f-4938-bedc-3114bdb5643a
**Dépend de** : rien.
**Fichiers** : `.gitattributes`, `scripts/test-vlp.py` — et les joints renormalisés.

**Prompt**
Ajouter à `.gitattributes` `*.css text eol=lf`, `*.js text eol=lf`, `*.svg text eol=lf`, puis
`git add --renormalize .` et récrire les copies de travail touchées (`git checkout --` fichier par
fichier, jamais sur un fichier modifié non commité). Un test dans `scripts/test-vlp.py` lit
`.gitattributes` du kit et vérifie les trois motifs.

**Critère de fin**
1. Octets comptés par Python : `templates/vlp.css` et `templates/vlp.js`, **0** `\r\n`, tailles
   brutes affichées avant/après (attendu 10 942 et 8 022).
2. `git ls-files --eol templates/vlp.css templates/vlp.js` : `w/lf attr/text eol=lf`.
3. Mutant par `vlp.py mutant` : le motif `*.css` retiré de `.gitattributes` → le test tombe.
4. `py scripts/test-vlp.py` : `OK`.
<!-- /FICHE -->

---

<!-- FICHE:JNT3 -->
## JNT3 [x] — `FILES` ne nomme que les joints changés

**Session** : b293bb0b-835f-4938-bedc-3114bdb5643a
**Dépend de** : `JNT2`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `ARTEFACTS.md` — et rien d'autre.

**Prompt**
`cmd_attente_hook`, sur un `PostToolUse` réussi avec `files` : note dans
`<contexte>/artefacts/publie` (une ligne par page et joint, tabulations : page, nom publié,
sha256) l'empreinte de chaque fichier passé ; une page republiée remplace les lignes des seuls
joints repassés (corrigé en jouant : tout remplacer effaçait la note d'un joint non renvoyé). `ligne_files`
reçoit la page et ne garde que les joints dont l'empreinte diffère de la note ; page non notée :
tous. `FILES {}` s'écrit quand rien n'a changé. `ARTEFACTS.md` : la règle « chaque publication
passe `files` » devient « le JSON de la ligne `FILES`, même vide » ; la phrase « non essayé » de
« Une publication refusée » cite l'essai de la version 185. Docstrings de `ligne_files` et du hook.

**Critère de fin**
1. Test sur un projet temporaire : page jamais notée → 2 joints ; hook simulé (JSON d'un
   `PostToolUse` avec `files`) → `publie` a 2 lignes ; `page` relancé → `FILES {}` ; `vlp.css`
   modifié → `FILES` ne nomme que lui ; un `PostToolUseFailure` n'écrit rien.
2. Mutant par `vlp.py mutant` : `ligne_files` qui ignore la note → un test tombe.
3. `py scripts/test-vlp.py` : `OK` ; pyright 0 erreur sur `scripts/vlp.py`.
<!-- /FICHE -->
