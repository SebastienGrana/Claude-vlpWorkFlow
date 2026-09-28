> **QUAND LIRE** : on joue une fiche `ENQ*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache ENQ<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier ENQ — Les écritures Git des sous-agents, tranchées

**À quoi il sert.** `vlp.py contrat` compte une tentative bloquée comme une écriture, et un
sous-agent interrompu comme une faute ; le gardien bloque un `echo` qui ne fait qu'écrire des mots.

**Estimé.** 1 fiches · ≈2,97 $ — ≈2,97 $/fiche sur 77 clos (le 2026-09-28).

**Fait.** Rien. Ouvert le 2026-09-28, cadré en 3 fiches, `ENQ1` à jouer.

**Session** : 437ff3d7-4dc7-40d3-bb3e-034fb507bb56

## Le socle commun

Mesuré au cadrage (2026-09-28, TODO n° 78) — les deux constats sont tranchés :

- `contrat --ouverture "context AI/58-forme-sous-agent.md"` → `CONTRAT 11 sous-agents · 3 écrivent
  dans Git · 1 sans statut en tête`. Les 3 (`ae2c2983…` ESD2, `aa54df75…` et `abe40d9c…` LEC2) sont de
  vrais `git add` + `git commit`, **tous refusés** par le gardien (`PreToolUse:Bash hook error: Un
  sous-agent vlp:fiche n'écrit pas dans Git…`) : 0 écriture. Le sans-statut (`aff56043…`) finit sur un
  message utilisateur `[Request interrupted by user]` : interrompu, pas en faute.
- Corpus : 202 transcriptions de sous-agents, 14 appels attrapés par `ecrit_git` — 13 vraies écritures
  (6 passées avant le gardien, 7 refusées), **1 faux positif** : le relecteur `a860169308600a92b`,
  `echo '{…"command":"git add ."}' > <fichier>`, refusé à tort. `contrat` sur lui : `git 1`.
- `contrat` sans argument (tous les `vlp:fiche`) : `CONTRAT 103 sous-agents · 10 écrivent dans Git ·
  46 sans statut en tête`.
- L'interdit de commit est dans `agents/fiche.md:54-56` depuis `f98ceec` (2026-09-24, CAS2) ; les 3
  tentatives depuis `FOR` sont venues après.

| Symbole | Où | Ce qu'il fait |
|---|---|---|
| `ECRIT_GIT` | `scripts/vlp.py:1546` | le motif `git [-C/-c]… commit\|add\|reset` |
| `sans_heredoc` | `scripts/vlp.py:1552` | tait le corps d'un heredoc reçu par `cat`/`tee` (ECH) |
| `ecrit_git` | `scripts/vlp.py:1568` | le motif sur `sans_heredoc` — lu par `contrat` et le gardien |
| `lire_contrat` | `scripts/vlp.py:1574` | (premier mot du dernier texte, appels qui écrivent) |
| `cmd_contrat` | `scripts/vlp.py:1628` | une ligne par sous-agent, puis le bilan `CONTRAT …` |
| refus du gardien | `scripts/vlp.py:1876` | `permissionDecisionReason`, dans `cmd_gardien` |
| tests `contrat` | `scripts/test-vlp.py:2789`, `:4388` | transcriptions fabriquées, bilan attendu à l'octet |
| tests `ecrit_git` | `scripts/test-vlp.py:3449` | ECH1 : la liste `cas`, dont `ssh h 'git reset --hard'` → vrai |
| bulletin | `skills/check/SKILL.md:122-131` | section I : lit `contrat`, nomme qui a enfreint |

Invariants : `vlp.py` en LF, `test-vlp.py` en CRLF — garder la fin de ligne du fichier. Un nouveau
cas de test prend son propre dossier temporaire, jamais le `t` d'un `with` voisin. Un test ne lit
jamais les vraies transcriptions de la machine ; les mesures sur le corpus sont des comptes du
critère, pas des tests. Pas de chaîne citée blanchie en bloc : `ssh h 'git reset'` reste attrapé.

Dehors : les 46 sans-statut d'avant `FOR` (ENQ1 les recompte, ne les explique pas) ; toute preuve par
essai `claude -p` (payant) ; `agents/relecture.md`, dont aucun appel n'était une vraie écriture.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `ENQ1` | Faire lire à `contrat` la réponse de l'outil | rien |
| `ENQ2` | Taire le texte d'un `echo` envoyé dans un fichier | `ENQ1` |
| `ENQ3` | Mesurer les tentatives, puis déplacer l'interdit du sous-agent | `ENQ1` |

Rien de parallèle : `ENQ1` et `ENQ2` touchent les mêmes fichiers, `ENQ3` lit le compteur d'`ENQ1`.

---

<!-- FICHE:ENQ1 -->
## ENQ1 [ ] — Faire lire à `contrat` la réponse de l'outil

**Dépend de** : rien.
**Fichiers** : scripts/vlp.py, scripts/test-vlp.py, skills/check/SKILL.md — et rien d'autre.

**Prompt**
Sors le texte du refus du gardien en une constante, lue par `cmd_gardien` et par `lire_contrat`.
Dans `lire_contrat`, un appel qui écrit dans Git et dont le `tool_result` porte ce refus compte
en **bloqué**, sinon en **écrit** ; un message utilisateur qui commence par
`[Request interrupted by user`, après le dernier texte de l'assistant, marque l'agent **interrompu**.
Ligne par sous-agent : `… <mot | (interrompu)> git <écrits> bloqué <n>`. Bilan :
`CONTRAT <n> sous-agents · <e> écrivent dans Git · <b> bloqués par le gardien · <s> sans statut en tête · <i> interrompus`
— un interrompu ne compte pas en sans-statut. Mets à jour les bilans attendus des tests existants,
la docstring (`contrat` dans l'aide de `vlp.py`) et la section I de `skills/check/SKILL.md` : un
`git` non nul enfreint, un `bloqué` se nomme sans être une écriture, un interrompu n'est pas en faute.

**Critère de fin**
Un test ajouté à `test-vlp.py` fabrique trois transcriptions — une refusée par le gardien, une
qui écrit, une interrompue — et attend `1 écrivent · 1 bloqués · 0 sans statut · 1 interrompus` ;
mutant : compter un refus comme une écriture le fait tomber. `py scripts/test-vlp.py` OK, pyright
0 erreur. `contrat --ouverture "context AI/58-forme-sous-agent.md"` rend `11 sous-agents · 0
écrivent · 3 bloqués · 0 sans statut · 1 interrompus` ; `contrat` sans argument : le bilan brut,
avant (`103 · 10 · 46`) et après, recopié dans le compte rendu.
<!-- /FICHE -->

---

<!-- FICHE:ENQ2 -->
## ENQ2 [ ] — Taire le texte d'un `echo` envoyé dans un fichier

**Dépend de** : `ENQ1`.
**Fichiers** : scripts/vlp.py, scripts/test-vlp.py — et rien d'autre.

**Prompt**
Étends ce que `sans_heredoc` tait (ou ajoute une fonction voisine que `ecrit_git` appelle) : les
arguments cités d'un `echo` ou `printf` dont la sortie va dans un fichier par `>` ou `>>`, sans `|`
dans le même segment de commande, hors `$(…)` et accents graves. Seul le texte cité se tait : ce qui
suit le `;`, `&&` ou le retour à la ligne reste lu. Limite acceptée, à écrire dans la docstring :
`echo 'git add' > s.sh` puis `sh s.sh` passe — le gardien arrête une habitude, pas un attaquant.

**Critère de fin**
Ajoute à la liste `cas` d'ECH1 (ou à un test ENQ2 voisin) au moins : `echo '{"command":"git add ."}' > f`
→ faux ; `printf '%s' 'git commit' >> f` → faux ; `echo "git add ." | sh` → vrai ;
`echo x > f; git add f` → vrai ; `ssh h 'git reset --hard'` → vrai (déjà là). Mutant : retirer la
nouvelle règle fait tomber les deux « faux ». `py scripts/test-vlp.py` OK, pyright 0 erreur.
`contrat` sur `a860169308600a92b` (chemin : `ls ~/.claude/projects/*/*/subagents/agent-a860169308600a92b.jsonl`)
passe de `git 1` à `git 0` ; `contrat` sans argument : bilan brut avant/après.
<!-- /FICHE -->

---

<!-- FICHE:ENQ3 -->
## ENQ3 [ ] — Mesurer les tentatives, puis déplacer l'interdit du sous-agent

**Dépend de** : `ENQ1`.
**Fichiers** : agents/fiche.md, context AI/08-etat.md — et rien d'autre.

**Prompt**
Mesure d'abord, par `contrat` sans argument (colonne `bloqué` d'`ENQ1`) : combien de sous-agents
`vlp:fiche` ont au moins un appel bloqué, combien en ont plusieurs (retentes), et, par l'heure de
chaque ligne, combien sont venus après `f98ceec` (2026-09-24 02:07 +0200). Écris ces comptes bruts,
avec la commande, dans le journal de `context AI/08-etat.md`. Règle fixée au cadrage : au moins une
tentative après `f98ceec` → l'interdit ne suffit pas là où il est. Alors, dans `agents/fiche.md`,
mets-le à l'étape 5 (`5. Succès : coche en un appel, et rends FAITE`), là où le sous-agent finit :
une phrase, sans le recopier deux fois — retire-le de `:54-56` s'il y fait doublon. Ne touche ni au
statut, ni au format du compte rendu. Zéro tentative après `f98ceec` : ne change pas `fiche.md`,
écris seulement la mesure.

**Critère de fin**
Le journal de `08-etat.md` porte la commande et les trois comptes bruts. `grep -n "commit" agents/fiche.md`
montre l'interdit à l'étape 5, et une seule fois (ou la mesure dit zéro et `fiche.md` n'a pas bougé).
`py scripts/test-vlp.py` OK. L'effet ne se prouve pas ici : il se lira aux chantiers suivants, par
`/vlp:check` section I.
<!-- /FICHE -->
