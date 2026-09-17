> **QUAND LIRE** : on joue une fiche `V*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache V<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier V — Evals du plugin

**À quoi il sert.** Le kit ne se teste pas : 0 cas d'eval, chaque commande se vérifie
par un rejeu à la main (TODO n° 6, point 16 de `12-audit.md`). Le chantier pose une
suite `claude plugin eval` de 5 cas, graders gratuits, et `validate` avant commit.

**Fait.** Rien. Ouvert le 2026-09-17, cadré en 4 fiches, `V1` à jouer.

## Le socle commun

**Résultat visible.** `claude plugin eval` passe 5 cas sur un bac à sable — `init`
équipe, `chantier` propose depuis la TODO, `tache` extrait la bonne fiche, `check`
voit une incohérence injectée, le hook rend `INVALIDE` sur un fichier de fiches cassé
écrit par `Write` — avec des graders gratuits seuls ; `claude plugin validate` rend
0 avertissement et tourne avant chaque commit.

**Noms retenus** (ne pas renommer) : `evals/` à la racine du kit, un dossier par cas
(`evals/check/`, `evals/tache/`, `evals/chantier/`, `evals/init/`, `evals/hook/`) ;
`evals/results/` ignoré par git ; `.githooks/pre-commit` pour `validate`.

**Le binaire — pas dans le PATH.** Chez znorr, `claude` n'est ni dans Git Bash ni dans
PowerShell : l'app de bureau l'embarque dans
`%APPDATA%/Claude/claude-code/<version>/claude.exe` (2.1.271 au cadrage ; `eval`
existe depuis 2.1.269). Aucun chemin de machine dans `evals/` ni `.githooks/` : le
binaire se trouve par `command -v claude`, sinon se dit introuvable, jamais muet.

**Contrat de `eval` — lu dans `claude plugin eval --help` au cadrage, le reste à
vérifier en V1.** Doc : https://code.claude.com/docs/en/plugin-evals. Un cas =
`case.yaml`, ou `prompt.md` + `graders/*.md`. Chaque run est une session `claude`
complète, sur ton compte. Défauts **à ne pas garder** : `runs` 3 par cas, bras sans
plugin (`--ablation with-without`), rapport **publié sur claude.ai**. Graders
gratuits : `regex`, `tool_used`, `tool_order`, `file_exists` (audit) ; `llm` et
`baseline` sont payants — exclus. Inconnues : comment poser un bac à sable (fixture
copiée, ou `scaffold_script` qui exige `--scaffold`) ; ce qu'un cas voit du hook ;
si l'outil `Artifact` existe dans un run.

**Lancer — toujours ainsi**, plafond chiffré par V1 :
`claude plugin eval <racine-projet> --runs 1 --no-publish --ablation none --scaffold --trust-plugin --max-cost-usd 0.35`, plus `--allow-tools Bash` si le sandbox tourne. Un run se mesure : `mesure-tokens.py` sur son transcript, tours et
`usd` — la sortie `--json` de `eval` à côté, si elle donne un coût.

**Invariants.** Aucun cas ne publie de page ni ne touche un projet réel : tout se joue
dans un dossier jetable. Les questionnaires ne sont pas testés (personne ne répond) ;
la publication réelle non plus — ils restent visibles à l'usage.

**Mesure « avant »** (2026-09-17, cadrage) : cas d'eval **0** ; `claude plugin
validate` → **1 avertissement** (`marketplace.json` : pas de `description`) ; rejeux
« à faire pour de vrai » notés dans `08-etat.md` : 5. Plancher d'une session neuve
(`b50ef5e2`, H4) : 1 tour, 0 appel, ctx_1er 58 635, total 58 936 tokens, 0,18 $ —
d'où 5 cas aux défauts (30 runs) ≥ 5,40 $ au plancher, une fiche réelle faisant 28 à
66 tours. `claude plugin details vlp` : ~315 tokens toujours chargés.

**Hors chantier.** Les écritures par Bash qui échappent au hook (un matcher `Bash`
tournerait après chaque commande de tout projet équipé) ; les hooks sous Windows sans
Git Bash (non testable sur cette machine). Tous deux restent « laissés ouverts ».

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `V1` | Poser le premier cas (`check`) et le chiffrer | rien |
| `V2` | Écrire les cas `tache` et `chantier` | `V1` |
| `V3` | Écrire les cas `init` et `hook` | `V1` |
| `V4` | Rendre `validate` propre, le lancer avant commit, jouer la suite | `V2`, `V3` |

`V2` et `V3` sont parallélisables : elles ne touchent pas les mêmes dossiers.

---

<!-- FICHE:V1 -->
## V1 [x] — Poser le premier cas (`check`) et le chiffrer

**Dépend de** : rien.
**Fichiers** : `evals/check/`, `.gitignore`, `commands/check.md` (lu, pour l'incohérence
à injecter), `templates/CHANTIER.md` et `templates/context AI/fichier-de-fiches.md`
(lus, pour le bac à sable) — et rien d'autre.

**Prompt**
Lis la doc des evals (URL du socle) et `claude plugin eval --help` : format d'un cas,
graders gratuits, pose d'un bac à sable, `max_turns`, `timeout_seconds`. Note ce qui
contredit le socle. Lance `claude plugin eval init` dans le scratchpad pour voir le
squelette — pas dans le kit.
Écris `evals/check/` : un bac à sable équipé (un `CHANTIER.md` et un fichier de fiches
tirés des gabarits) où une fiche est cochée alors que la ligne « fichier de fiches
courant » la dit à faire — ou l'incohérence la plus simple que `check.md` détecte. Le
prompt lance `/vlp:check` ; les graders (regex sur la sortie) exigent que l'écart soit
nommé. Ajoute `evals/results/` à `.gitignore`.
Lance le cas **une fois**, aux options du socle, avec un plafond provisoire de 2 $.
Mesure le run (tours, appels, total, `usd`). Si l'outil ne laisse pas voir le coût,
dis-le. Écris le plafond retenu pour la suite dans le socle de ce fichier (ligne
« Lancer »), et les contradictions trouvées au journal de `08-etat.md`.

**Critère de fin**
La sortie de `claude plugin eval` montre le cas `check` réussi (score brut affiché),
et le coût du run est écrit : tours, total tokens, `usd`.
<!-- /FICHE -->

---

<!-- FICHE:V2 -->
## V2 [ ] — Écrire les cas `tache` et `chantier`

**Dépend de** : `V1`.
**Fichiers** : `evals/tache/`, `evals/chantier/`, `evals/check/` (lu, modèle du bac à
sable), `commands/tache.md` et `commands/chantier.md` (lus) — et rien d'autre.

**Prompt**
Sur le modèle de `evals/check/`, écris deux cas.
`tache` : un bac à sable dont le fichier de fiches porte deux fiches ; le prompt lance
`/vlp:tache <la seconde>` ; les graders vérifient que c'est bien elle qui est lue (un
mot qui n'existe que dans son prompt) et pas la première. Borne `max_turns` : le cas
n'a pas à finir la fiche, seulement à l'avoir extraite.
`chantier` : un bac à sable sans chantier ouvert, dont le fichier d'état porte une TODO
de deux entrées ; le prompt lance `/vlp:chantier` ; les graders vérifient que les deux
noms de la TODO sont proposés. Le questionnaire ne sera pas répondu : borne les tours.
Choisis **un** des deux cas pour garder la baseline sans plugin (celui où son échec
prouve le plus) ; `--ablation none` pour l'autre, écrit dans le cas si le format le
permet, sinon dans la ligne « Lancer » du socle.
Lance les deux cas une fois, aux options du socle.

**Critère de fin**
La sortie montre `tache` et `chantier` réussis, avec les scores bruts, la baseline
chiffrée sur le cas retenu, et le coût de chaque run (tours, total, `usd`).
<!-- /FICHE -->

---

<!-- FICHE:V3 -->
## V3 [ ] — Écrire les cas `init` et `hook`

**Dépend de** : `V1`.
**Fichiers** : `evals/init/`, `evals/hook/`, `evals/check/` (lu, modèle),
`commands/init.md` et `hooks/hooks.json` (lus) — et rien d'autre.

**Prompt**
Sur le modèle de `evals/check/`, écris deux cas.
`init` : un dossier vide ; le prompt lance `/vlp:init` ; les graders `file_exists`
vérifient `CHANTIER.md` et le dossier de contexte. Aucune page ne doit partir : vérifie
d'abord si l'outil `Artifact` existe dans un run ; s'il existe, coupe-le (outil non
accordé, ou consigne du prompt) et prouve par un grader qu'il n'a pas été appelé.
`hook` : un bac à sable ; le prompt demande d'écrire par `Write` un fichier de fiches
sans `<!-- /FICHE -->` ; les graders vérifient que le hook a parlé (`INVALIDE` dans ce
que le run a reçu). Si un run ne charge pas les hooks du plugin, dis-le et arrête : le
cas ne se contourne pas.
`--ablation none` sur les deux. Lance-les une fois, aux options du socle.

**Critère de fin**
La sortie montre `init` et `hook` réussis, scores bruts, 0 appel `Artifact` compté sur
`init`, et le coût de chaque run (tours, total, `usd`).
<!-- /FICHE -->

---

<!-- FICHE:V4 -->
## V4 [ ] — Rendre `validate` propre, le lancer avant commit, jouer la suite

**Dépend de** : `V2`, `V3`.
**Fichiers** : `.claude-plugin/marketplace.json`, `.githooks/pre-commit`,
`INSTALLATION.md` (une ligne : activer le hook git), `context AI/08-etat.md` —
et rien d'autre.

**Prompt**
Ajoute la `description` qui manque à `marketplace.json` ; relance `claude plugin
validate` sur le kit.
Écris `.githooks/pre-commit` : il lance `claude plugin validate` sur la racine du dépôt
et bloque le commit sur une erreur ; si `claude` est introuvable, il le **dit** en une
ligne et laisse passer. Active-le chez toi (`git config core.hooksPath .githooks`) et
dis-le en une ligne dans `INSTALLATION.md`, à l'endroit qui parle du clone.
Prouve la garde : un commit sur un `plugin.json` cassé est refusé (puis annulé), un
commit sain passe.
Joue enfin la suite entière (5 cas) aux options du socle, une fois, et mesure-la.

**Critère de fin**
`validate` rend 0 avertissement ; le commit cassé est refusé, le sain passe ; la suite
montre 5 cas sur 5 avec leurs scores bruts, et son coût total (runs, tours, tokens,
`usd`) est écrit au journal de `08-etat.md`.
<!-- /FICHE -->
