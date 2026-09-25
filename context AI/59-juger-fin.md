> **QUAND LIRE** : on joue une fiche `JUG*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache JUG<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier JUG — Le gardien ne juge que la fin du message, pas tout le texte

**À quoi il sert.** Le gardien renvoie tout dernier message qui **cite** « En résumé » ou un mot
de `JAUGE`, même en prose — prouvé sur le relecteur de `FOR3` (TODO n° 65). JUG mesure trois
façons de ne juger que la fin, l'utilisateur en retient une, et gardien et mesure la suivent.

**Fait.** Rien. Ouvert le 2026-09-25, cadré en 3 fiches, `JUG1` à jouer.

**Session** : 7d3fa883-9860-4d26-b74b-bfc5119c1c51

## Le socle commun

**Décisions du cadrage (2026-09-25).** Mesurer avant de choisir. Une seule règle : `forme_texte`
reste partagée par le gardien et par `vlp.py forme`. Le texte de renvoi du gardien et
`agents/*.md` ne changent pas. Un essai en vrai clôt le chantier.

**Les règles candidates** — nom de `--regle`, et ce qu'elle juge :

| `--regle` | Partie du dernier message jugée |
|---|---|
| `tout` | le texte entier — la règle d'aujourd'hui |
| `tiret` | après la dernière ligne `---` ; sans `---`, le texte entier |
| `deux` | les deux dernières lignes non vides |
| `tete` | chaque ligne, mais le mot doit l'**ouvrir** une fois retirés espaces, `#`, `*`, `-`, `>` et émojis ; `«` n'est pas retiré, donc une citation ne compte pas |

Les deux formes vraies d'une fin hors contrat (`CLAUDE.md` de l'utilisateur) : le résumé **à
part**, jauge en **première** ligne puis « En résumé » ; ou le résumé en bas, **après un `---`**.

| Symbole | Où | Ce qu'il rend |
|---|---|---|
| `JAUGE`, `forme_texte(texte)` | `scripts/vlp.py:1195`, `:1198` | `(resume 0\|1, jauge 0\|1)` ; mot entier par `\b` (`FOR3`) |
| `lire_forme(chemin)` | `scripts/vlp.py:1208` | `(chars, resume, jauge, tete)` sur le **dernier** texte assistant |
| `cmd_forme(a, sortie)` | `scripts/vlp.py:1243` | une ligne par sous-agent, puis `FORME <n> sous-agents · … · resume <k> · jauge <k> · tete <k>` |
| parseur de `forme` | `scripts/vlp.py:2889` | options de la sous-commande |
| `cmd_gardien(entree, sortie)` | `scripts/vlp.py:1338` | `SubagentStop` : renvoi si `resume or jauge`, `stop_hook_active` faux |
| docstrings `forme`, `gardien` | `scripts/vlp.py:189`, `:205` | décrivent la règle : se corrigent avec elle |
| tests du gardien | `scripts/test-vlp.py:1797` | bloc `# gardien (chantier CON4)` ; faux positif « Pas bonne » `:1871` |
| tests de `forme` | `scripts/test-vlp.py:2028`, `:2074` | blocs `# GLO1` : transcriptions factices |

Tests : `py scripts/test-vlp.py` depuis la racine du kit ; la dernière ligne donne le compte.

**On ne fait pas.** Toucher `agents/fiche.md`, `agents/relecture.md` ni le texte de renvoi.
Juger la tête du relecteur (décision RLG). Couper la fin côté chef.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `JUG1` | Mesurer les trois règles sur les vraies transcriptions | rien |
| `JUG2` | Faire juger la règle retenue, au gardien et à la mesure | `JUG1` (choix de l'utilisateur) |
| `JUG3` | Essayer le gardien sur un vrai sous-agent | `JUG2` |

Rien n'est parallèle : chaque fiche part du résultat de la précédente.

---

<!-- FICHE:JUG1 -->
## JUG1 [x] — Mesurer les trois règles sur les vraies transcriptions

**Session** : b9951712-2f7d-4821-a7ac-5e131a03b7c5
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `context AI/08-etat.md` (fin du journal) — et rien d'autre.

**Prompt**
Donne à `forme_texte` un paramètre `regle` (défaut `tout`), qui juge la partie du texte dite par
la table du socle ; ajoute `--regle {tout,tiret,deux,tete}` à `forme` (défaut `tout`). Le
gardien ne change pas : il reste en `tout`. Tests, au bloc `# GLO1` : un texte qui cite
« En résumé » et « Pas bon » en milieu de phrase, sans `---` ➡️ `tete` rend `(0, 0)` ; un
résumé à part (`✅ **Tout va bien** — fait` puis `**En résumé**` puis une phrase) ➡️ `tete` rend
`(1, 1)` ; un `x\n---\n✅ Tout va bien` ➡️ `tiret` rend `(0, 1)`.

Puis mesure. Le corpus : les sous-agents depuis l'ouverture de `GLO` (sha par
`git log --oneline --grep "Chantier GLO ouvert"`), une fois par règle : `forme --depuis <sha>
--regle <r>`. Repère aussi le relecteur de `FOR3` renvoyé à tort : son message **renvoyé** n'est
pas son dernier ; recopie-le depuis sa transcription, c'est la pièce que `JUG2` testera.

Écris à la fin du journal une entrée `## <date> — JUG1` : les quatre lignes `FORME` brutes, les
sous-agents dont le verdict change d'une règle à l'autre, et le message renvoyé du relecteur
jugé par chaque règle. Ce compte compare les sous-agents *renvoyés* par règle, pas leur qualité.

**Critère de fin** (visuel)
`py scripts/test-vlp.py` : 0 échec, compte avant et après (trois tests de plus). Mutant : `tete`
qui juge le texte entier ➡️ le premier test tombe, puis rétablir. L'entrée `JUG1` est écrite ;
l'utilisateur la lit et **retient une règle**, écrite sous l'entrée.
<!-- /FICHE -->

---

<!-- FICHE:JUG2 -->
## JUG2 [x] — Faire juger la règle retenue, au gardien et à la mesure

**Session** : b9951712-2f7d-4821-a7ac-5e131a03b7c5
**Dépend de** : `JUG1`, et la règle retenue par l'utilisateur sous l'entrée `JUG1` du journal.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `context AI/08-etat.md` — et rien d'autre.

**Prompt**
Lis la règle retenue sous l'entrée `JUG1` du journal. Fais-en le défaut de `forme_texte` et de
`forme --regle` : le gardien la suit sans changer son code d'appel. `--regle tout` reste, pour
rejouer l'ancienne mesure. Corrige le commentaire de `forme_texte` et les docstrings `forme` et
`gardien` : un commentaire périmé oriente en silence.

Tests, au bloc `# gardien (chantier CON4)` : le relecteur avec le message renvoyé à tort
recopié en `JUG1` ➡️ muet ; un relecteur `ACCEPTÉE — ok` suivi du résumé à part ➡️ renvoyé ; les
tests existants restent verts (le cas `---\n✅ Tout va bien`, et « Pas bonne » muet).

Rejoue `forme --depuis <sha de GLO>` avec la nouvelle règle, et écris l'entrée `## <date> —
JUG2` : la ligne `FORME` avant (`--regle tout`) et après. Les chiffres de `FOR` au bilan
(`resume 0/2`, `jauge 1/2`, et 14/36, 23/36 avant `GLO3`) restent écrits : ajoute-leur « mesurés
en texte entier, voir `JUG2` » — un énoncé renversé se garde, marqué.

**Critère de fin**
`py scripts/test-vlp.py` : 0 échec, compte avant et après (deux tests de plus). Mutant : remettre
le défaut à `tout` ➡️ le test du relecteur renvoyé à tort tombe, puis rétablir.
<!-- /FICHE -->

---

<!-- FICHE:JUG3 -->
## JUG3 [ ] — Essayer le gardien sur un vrai sous-agent

**Dépend de** : `JUG2`.
**Fichiers** : `context AI/08-etat.md` (fin du journal) — et rien d'autre.

**Prompt**
Se joue par `/vlp:tache`, pas enchaîné : il faut l'outil `Agent`, qu'un sous-agent `vlp:fiche`
n'a pas. Le script du gardien est relu à chaque appel : pas besoin de relancer l'app.

Lance deux sous-agents `vlp:relecture`, l'un après l'autre. Au premier, demande un verdict
`ACCEPTÉE` qui **explique en prose** que le gardien renvoie « En résumé » et « Pas bon ». Au
second, un verdict `ACCEPTÉE` suivi d'un résumé à part, jauge en première ligne. Pour chacun,
lis dans sa transcription s'il a reçu le renvoi du gardien, et combien de fois.

Écris l'entrée `## <date> — JUG3` : les deux prompts, et pour chacun « renvoyé <k> fois », avec
la ligne `forme --depuis <heure du premier lancement>` brute. Ajoute le coût de la fiche
(`vlp.py cout`).

**Critère de fin** (visuel)
Premier sous-agent : renvoyé 0 fois. Second : renvoyé 1 fois, puis sa fin réécrite sans jauge.
L'entrée `JUG3` porte les deux comptes ; l'utilisateur la lit et décide de clore.
<!-- /FICHE -->
