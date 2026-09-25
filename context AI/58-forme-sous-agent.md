> **QUAND LIRE** : on joue une fiche `FOR*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache FOR<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier FOR — La forme du sous-agent, pour de vrai

**À quoi il sert.** Le dernier message d'un sous-agent porte « En résumé » et la jauge du
`CLAUDE.md` de l'utilisateur, que le chef lit et paye (TODO n° 62). FOR mesure si la phrase de
`GLO3` tient en session neuve, et sinon fait renvoyer cette fin par le gardien.

**Fait.** Rien. Ouvert le 2026-09-25, cadré en 3 fiches, `FOR1` à jouer. ⚠️ Relancer l'app
avant `/vlp:enchainer` : une définition d'agent se charge au démarrage.

**Session** : 669739ec-48a1-4796-aab1-ff74eaf24dd5

## Le socle commun

**Pourquoi la mesure de `GLO3` ne vaut rien.** La session `ca431cf8-…` a démarré à
2026-09-24T23:38:16Z, et `5e37964` (`GLO3`) est commité à 23:59:15Z ; aucun `/reload-plugins`
dans la session. Ses 14 sous-agents d'après le commit ont donc très probablement tourné avec
l'ancien `agents/fiche.md`. Aucune transcription ne garde le prompt système : on ne le prouve
pas, on remesure.

| Symbole | Où | Ce qu'il rend |
|---|---|---|
| `STATUTS`, `VERDICTS`, `JAUGE` | `scripts/vlp.py:1117`, `:1192`, `:1193` | mots de tête de fiche, de relecteur ; les cinq mots de la jauge |
| `lire_forme(chemin)` | `scripts/vlp.py:1196` | `(chars, resume, jauge, tete)` sur le **dernier** texte assistant |
| `cmd_forme(a, sortie)` | `scripts/vlp.py:1232` | une ligne par sous-agent `vlp:fiche`/`vlp:relecture`, puis `FORME <n> sous-agents · … · resume · jauge · tete` |
| `m.depart(chemin)` | `scripts/mesure-tokens.py:148` (via `mesure()`) | `(heure de la 1re ligne horodatée, err)` |
| `verdict_fin(d, deja_renvoye)` | `scripts/vlp.py:1296` | la raison de renvoyer un `vlp:fiche` qui s'arrête, ou `None` |
| `cmd_gardien(entree, sortie)` | `scripts/vlp.py:1328` | `SubagentStop` : `{"decision": "block", "reason": …}` ; muet pour le relecteur (chantier RLG) |
| docstring `gardien` | `scripts/vlp.py:197` | décrit ce que fait le gardien : se corrige avec lui |
| tests du gardien | `scripts/test-vlp.py:1797` | bloc `# gardien (chantier CON4)` : `gardien(d)` rend `(code, sortie)` |
| tests de `forme` | `scripts/test-vlp.py:2015` | bloc `# GLO1` : transcriptions factices + `.meta.json` |

Tests : `py scripts/test-vlp.py` depuis la racine du kit ; la dernière ligne donne le compte.

**On ne fait pas.** Couper la fin côté chef : le texte est déjà dans son contexte quand il le
lit, aucun token n'est gagné. Déplacer la phrase de `GLO3` dans `skills/jouer` ou
`skills/relire` : encore de la prose. La phrase de `GLO3` reste où elle est.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `FOR1` | Filtrer `forme --depuis` sur le départ du sous-agent | rien |
| `FOR2` | Mesurer `GLO3` en session neuve | `FOR1` |
| `FOR3` | Renvoyer la fin hors forme, fiche et relecteur | `FOR2` (décision de l'utilisateur) |

Rien n'est parallèle : `FOR2` mesure les sous-agents de `FOR1`, `FOR3` n'existe que si `FOR2` le
justifie.

---

<!-- FICHE:FOR1 -->
## FOR1 [x] — Filtrer `forme --depuis` sur le départ du sous-agent

**Session** : 669739ec-48a1-4796-aab1-ff74eaf24dd5
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Dans `cmd_forme`, `--depuis` compare aujourd'hui la borne au départ de la **session parente**
(`parent = …".jsonl"`, puis `m.depart(parent)`). Une longue session démarrée avant la borne
cache donc tous ses sous-agents, même ceux lancés après. Compare plutôt au départ de la
transcription du sous-agent elle-même (`m.depart(c)`), et affiche cette heure-là dans la ligne
par sous-agent. Mets à jour la ligne de docstring de `forme` (`scripts/vlp.py:195`) qui dit
« démarré à D ou après ».

Ajoute au bloc `# GLO1` de `scripts/test-vlp.py` un test : une transcription de sous-agent
dont la 1re ligne porte `"timestamp": "2026-09-25T12:00:00Z"`, dans une session parente
(`<dossier>.jsonl`) dont la 1re ligne porte `"2026-09-25T08:00:00Z"`, appelée par
`forme --depuis 2026-09-25T10:00:00Z <chemin>` ➡️ `FORME 1 sous-agents`.

**Critère de fin**
`py scripts/test-vlp.py` : 0 échec, le compte avant et après écrit (un test de plus). Mutant :
remettre `m.depart(parent)` ➡️ le nouveau test tombe (`FORME 0 sous-agents`), puis rétablir.
<!-- /FICHE -->

---

<!-- FICHE:FOR2 -->
## FOR2 [ ] — Mesurer `GLO3` en session neuve

**Dépend de** : `FOR1`.
**Fichiers** : `context AI/08-etat.md` (fin du journal) — et rien d'autre.

**Prompt**
Mesure la forme des sous-agents lancés depuis l'ouverture du chantier FOR :

```bash
<python> "<kit>/scripts/vlp.py" forme --depuis <sha du commit « Chantier FOR ouvert »>
```

Le sha se lit par `git log --oneline -5`. Garde les lignes par sous-agent : ceux de `FOR1`
(fiche et relecteur) comptent ; le tien, encore en cours, se reconnaît à `tete 0` et s'écarte.
Vérifie que la session parente est neuve : sa première heure (1re ligne de
`<id de session>.jsonl`) est postérieure au commit d'ouverture.

Écris à la fin de `context AI/08-etat.md` une entrée `## <date du jour> — FOR2` : la commande,
la ligne `FORME` brute, les lignes des sous-agents comptés, et le compte avant `GLO3` pour
comparaison (journal `GLO2` : jauge 23 sur 36, « En résumé » 14 sur 36). Dis en une ligne que
l'échantillon est petit (2 sous-agents) : 0 sur 2 ne prouve pas que la phrase tient.

**Critère de fin** (visuel)
L'entrée `FOR2` est écrite, avec `resume <k>` et `jauge <k>` sur les sous-agents de `FOR1`.
L'utilisateur la lit et décide : `FOR3` se joue, ou il est abandonné.
<!-- /FICHE -->

---

<!-- FICHE:FOR3 -->
## FOR3 [ ] — Renvoyer la fin hors forme, fiche et relecteur

**Dépend de** : `FOR2`, et la décision de l'utilisateur de la jouer.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Sors de `lire_forme` (les deux lignes `resume = …` et `jauge = …`) une fonction
`forme_texte(texte)` qui rend `(resume, jauge)` ; `lire_forme` l'appelle. La mesure et le
gardien jugent ainsi la même chose.

Dans `cmd_gardien`, au `SubagentStop`, pour `vlp:fiche` **et** `vlp:relecture` : si le dernier
message porte « En résumé » ou un mot de `JAUGE`, et que `stop_hook_active` est faux, renvoie
une fois, raison d'une ligne : « Ton dernier message porte un « En résumé » ou une jauge : ton
lecteur est le chef (agents/<fiche|relecture>.md). Réécris-le sans eux, statut en tête. » Pour
`vlp:fiche`, les renvois existants de `verdict_fin` (tête, case, commit) passent **avant**. Pour
le relecteur, la tête reste non jugée (décision RLG) : seule la forme l'est. Corrige la
docstring du gardien (`scripts/vlp.py:197`).

Tests, au bloc `# gardien (chantier CON4)` : fiche `RETOUR — x\n\n---\n✅ Tout va bien` ➡️
renvoyée ; la même sous `stop_hook_active` ➡️ muet ; relecteur `ACCEPTÉE — ok\nEn résumé : y`
➡️ renvoyé ; relecteur `ACCEPTÉE — ok` ➡️ muet (les deux tests existants restent verts).

**Critère de fin**
`py scripts/test-vlp.py` : 0 échec, compte avant et après (quatre tests de plus). Mutant :
retirer l'appel à `forme_texte` du gardien ➡️ les deux tests « renvoyé » tombent, puis rétablir.
<!-- /FICHE -->
