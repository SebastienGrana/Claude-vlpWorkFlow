> **QUAND LIRE** : on joue une fiche `SAG*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache SAG<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier SAG — Le sous-agent ne bute plus sur 30 tours

**À quoi il sert.** Le sous-agent `vlp:fiche` est coupé à 30 tours sans rendre de
statut : quatre sous-agents sur cinq en REP. Le chantier relève son plafond, le
prévient avant la coupe, puis mesure une fiche de code enchaînée, sous-agent compris.

**Fait.** Rien. Ouvert le 2026-09-23, cadré en 5 fiches, `SAG1` à jouer.

## Le socle commun

| Quoi | Où | Ce qu'il dit ou rend |
|---|---|---|
| le plafond | frontmatter de `agents/fiche.md` | `maxTurns: 30` — ce nombre ne vit qu'ici : un script le lit, ne le recopie pas |
| le modèle | même frontmatter | `model: haiku`, `effort: low` |
| la consigne qui n'a pas suffi | `agents/fiche.md`, fin | « Garde un tour pour le compte rendu » |
| le contrat de retour | `enchainement.md` | `FAITE`, `RETOUR` ou `BLOQUÉE` en premier mot ; sans statut, le chef lit `RETOUR` |
| le lanceur | `skills/jouer/SKILL.md` | `context: fork`, `agent: vlp:fiche` : un sous-agent neuf par fiche |
| le coût par fiche | `scripts/vlp.py cout "<fichier de fiches>"` | session coupée aux commits de fiche, sous-agents compris ; puis hors fiches et TOTAL |
| les sous-agents sur une plage de temps | `scripts/mesure-tokens.py` | sa docstring donne la syntaxe |

**Les faits de départ.**
- Journal de `context AI/08-etat.md`, 2026-09-23, « clôture REP » : quatre
  sous-agents coupés à 30 tours pile, dernier message sur `tool_use` ; le seul
  qui a rendu son statut a fait 25 tours, fini sur `end_turn`.
- À la main, une fiche prend 28 à 66 tours (`CLAUDE.md`, « Économie de contexte »).
- Chantier Q (`context AI/34-agent-sans-git.md`) : 0,176 $ par fiche enchaînée
  contre 0,42 $ à la main, sur des fiches triviales, tiré de `total_cost_usd`
  (`claude -p`). Sous-agents comptés ou non : `SAG1` le dit.

**Les règles du chantier.**
- Tout lancement d'un sous-agent ou de `claude -p` se chiffre en $ **avant**, et
  le chiffre s'annonce.
- Le plugin est chargé en place : une modification de `agents/fiche.md` ou d'un
  hook ne se voit qu'après `/reload-plugins`, ou dans un processus neuf (`claude -p`).
- Le déterministe est un script dans `scripts/`, Python 3 sans dépendance,
  testé ; `${CLAUDE_PLUGIN_ROOT}` seulement dans le texte des commandes et
  `hooks/hooks.json` (`CLAUDE.md`, règle 4).
- Chaque verdict va au journal de `context AI/08-etat.md`, daté, les comptes
  bruts à côté et la commande rejouable.

**Ce qu'on ne fait pas.**
- Changer le modèle ou l'effort du sous-agent : le sujet est le plafond.
- Toucher au chef `/vlp:enchainer`, sauf si `SAG2` prouve qu'aucun hook
  n'atteint le sous-agent.
- Les autres points de la TODO.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `SAG1` | Recompter Q, sous-agents compris | rien |
| `SAG2` | Relever le plafond, et prouver qu'un hook atteint le sous-agent | `SAG1` |
| `SAG3` | Prévenir le sous-agent avant qu'il soit coupé | `SAG2` |
| `SAG4` | Éprouver le filet à plafond bas | `SAG3` |
| `SAG5` | Mesurer le témoin, et conclure | `SAG4` |

Rien n'est parallélisable : chaque fiche s'appuie sur ce que la précédente a
prouvé. **`SAG3` se joue par `/vlp:enchainer`** — c'est la fiche témoin : avant
elle, `/reload-plugins` et la commande bornée à une fiche que donne `SAG2` ;
après elle, un commit `SAG3 : …`, sans quoi `vlp.py cout` ne peut pas la couper.
Coupée quand même, on la finit par `/vlp:tache` : la coupe est un résultat, `SAG5`
la compte.

---

<!-- FICHE:SAG1 -->
## SAG1 [x] — Recompter Q, sous-agents compris

**Session** : 1cba232a-94a5-4599-9fce-b381f08f8a01
**Dépend de** : rien.
**Fichiers** : `context AI/34-agent-sans-git.md` (par grep : `0,176`, `0,42`,
`total_cost_usd`, `modelUsage`), `scripts/mesure-tokens.py` (sa docstring), le
journal de `context AI/08-etat.md`.

**Prompt**
Le 0,176 $ par fiche de Q vient de `total_cost_usd`, rendu par `claude -p`. Dis
s'il compte les sous-agents, puis recompte Q sous-agents compris.

1. La doc officielle d'abord : ce que couvre `total_cost_usd` (Claude Code en
   `--output-format json`, ou l'Agent SDK). Lien et date.
2. Dans `34-agent-sans-git.md`, la sortie brute de la mesure : un `modelUsage`
   qui liste Haiku à côté du modèle du chef dit que les sous-agents sont comptés.
   Dis aussi d'où vient le 0,42 $ à la main, et s'il se mesure pareil.
3. Recompte les deux fiches de Q par `mesure-tokens.py`, sous-agents compris,
   sur la plage de temps de leurs sessions (le projet bac que nomme
   `34-agent-sans-git.md`). Tokens et $, par fiche.
4. Au journal : le verdict, 0,176 $ et le recompte côte à côte, les commandes.

Ne corrige ni le bilan ni la mémoire : `SAG5` le fait, avec tous les chiffres.
Journaux de Q introuvables : rends `RETOUR`, ne reconstruis pas.

**Critère de fin**
Une entrée datée du journal dit si `total_cost_usd` compte les sous-agents,
source citée, et pose le coût recompté de Q par fiche à côté de 0,176 $, avec
la commande qui l'a produit.
<!-- /FICHE -->

---

<!-- FICHE:SAG2 -->
## SAG2 [x] — Relever le plafond, et prouver qu'un hook atteint le sous-agent

**Session** : 1cba232a-94a5-4599-9fce-b381f08f8a01
**Dépend de** : `SAG1`.
**Fichiers** : `agents/fiche.md`, `hooks/hooks.json`, `skills/enchainer/SKILL.md`
(par grep : comment borner le nombre de fiches), le journal de
`context AI/08-etat.md`, et la fiche `SAG3` de ce fichier (en écriture, son
seul bloc **Prouvé par SAG2**).

**Prompt**
`SAG3` attend deux choses : un plafond relevé, et la preuve qu'un hook peut
parler au sous-agent.

1. **Le hook.** Dans la doc officielle de Claude Code : un hook `PostToolUse`
   se déclenche-t-il sur les outils d'un sous-agent ? Se déclare-t-il dans le
   frontmatter de `agents/fiche.md`, ou seulement dans `hooks/hooks.json` ? Son
   entrée dit-elle qu'on est dans `vlp:fiche`, et où lire ses tours ? Sa sortie
   `additionalContext` arrive-t-elle au modèle ?
2. **L'essai.** Chiffré avant : un hook minimal qui injecte un mot témoin, un
   sous-agent `vlp:fiche` lancé par `claude -p` sur une tâche sans effet. Le mot
   dans la transcription du sous-agent est la preuve. Retire l'essai ensuite.
3. **Le plafond.** Relève `maxTurns` au-dessus du plus haut compte connu (66
   tours à la main), avec une marge justifiée au journal.
4. **Pour `SAG3`.** La commande qui borne `/vlp:enchainer` à une fiche, et son
   coût estimé, au journal. Puis, sous le prompt de `SAG3`, un bloc **Prouvé par
   SAG2** de cinq lignes au plus : où se déclare le hook, ce que son entrée
   donne, comment compter les tours, le fichier et la commande de test de `vlp.py`.

Aucun hook n'atteint le sous-agent : rends `RETOUR` — `SAG3` se redécoupe, le
filet passe du côté du chef.

**Critère de fin**
Le journal porte le verdict du hook, source et transcription de l'essai citées,
le nouveau `maxTurns` justifié, et la commande qui joue `SAG3` seule avec son
coût estimé ; `SAG3` porte son bloc **Prouvé par SAG2**.
<!-- /FICHE -->

---

<!-- FICHE:SAG3 -->
## SAG3 [x] — Prévenir le sous-agent avant qu'il soit coupé

**Session** : 1cba232a-94a5-4599-9fce-b381f08f8a01
**Dépend de** : `SAG2`.
**Fichiers** : `scripts/vlp.py` et le test que nomme le bloc **Prouvé par
SAG2**, `agents/fiche.md`, `hooks/hooks.json`.

**Prompt**
Le sous-agent ne sait pas combien de tours il lui reste : il est coupé en plein
travail, sans statut. Donne-lui un filet, sous la forme que le bloc **Prouvé
par SAG2** ci-dessous a établie.

- Écris la sous-commande `vlp.py filet`, que le hook appelle. Elle compte les
  tours déjà faits par le sous-agent — une ligne assistant n'est pas un tour —
  et lit `maxTurns` dans le frontmatter de `agents/fiche.md`.
- Quand il reste 3 tours ou moins, elle rend un `additionalContext` : combien il
  en reste, et l'ordre de rendre son statut maintenant — `RETOUR` avec ce qui est
  fait et ce qui reste, si la fiche n'est pas finie. Sinon, et hors de
  `vlp:fiche`, elle ne dit rien. Le 3 vit dans le script, en constante nommée.
- Câble le hook comme le bloc le dit.
- Dans `agents/fiche.md`, « Garde un tour pour le compte rendu » devient : un
  avertissement te dira quand rendre ton statut ; obéis-lui.
- Ajoute `filet` à la docstring de `vlp.py`, avec les autres sous-commandes.
- Le test : une transcription factice donne l'avertissement au bon tour, et rien
  avant ; hors sous-agent, rien.

**Prouvé par SAG2** (essai du 2026-09-23, détail au journal de `context AI/08-etat.md`) :
- Hook : `PostToolUse` dans `hooks/hooks.json` — le `hooks` du frontmatter est ignoré pour un sous-agent de plugin ; il rend `hookSpecificOutput.additionalContext` comme `cmd_hook` (`scripts/vlp.py:681`), et le sous-agent le reçoit.
- Entrée : `agent_type` = `<plugin>:fiche` (`vlp:fiche` ; `vlpt:fiche` dans l'essai) et `agent_id`, tous deux absents hors sous-agent ; `transcript_path` est la transcription du **chef**.
- Tours : dans `<transcript_path sans .jsonl>/subagents/agent-<agent_id>.jsonl`, un tour = un `message.id` distinct des lignes `assistant` (les `tours` de `mesure-tokens.py`) ; écrite en différé, elle peut manquer le tour en cours.
- Test : `scripts/test-vlp.py`, lancé par `py scripts/test-vlp.py` (« OK »).

**Critère de fin**
La commande de test du bloc passe, nombre de cas cité ; le hook est câblé ; la
consigne de `agents/fiche.md` est remplacée.
<!-- /FICHE -->

---

<!-- FICHE:SAG4 -->
## SAG4 [x] — Éprouver le filet à plafond bas

**Session** : 1cba232a-94a5-4599-9fce-b381f08f8a01
**Dépend de** : `SAG3`.
**Fichiers** : `agents/fiche.md` (le plafond, abaissé le temps de l'essai),
l'entrée `SAG2` du journal de `context AI/08-etat.md` (la forme de l'essai), le
journal en écriture.

**Prompt**
Le test de `SAG3` prouve le script ; reste à voir le filet marcher en vrai, une fois.

1. Chiffre l'essai, annonce le chiffre.
2. Abaisse `maxTurns` le temps de l'essai : assez pour lire une fiche, trop peu
   pour la finir.
3. Dans un processus neuf (`claude -p`, comme l'essai de `SAG2`), fais jouer au
   sous-agent une fiche factice qui demande plus de tours, dans le bac de Q :
   rien de durable.
4. Dans sa transcription : l'avertissement est-il arrivé ? Le dernier message
   commence-t-il par un statut, et finit-il sur `end_turn` ?
5. Remets `maxTurns` à la valeur de `SAG2`, et vérifie-le par `Read`.
6. Au journal : l'essai, sa commande, son coût réel, et la dernière ligne du
   sous-agent, citée telle quelle.

Filet muet — coupé sur `tool_use`, sans statut : rends `RETOUR` avec la
transcription. C'est `SAG3` qui est à reprendre.

**Critère de fin**
La transcription de l'essai montre l'avertissement, puis un dernier message qui
commence par `RETOUR` ; le journal le cite ; `maxTurns` est revenu à la valeur
de `SAG2`, vérifié par `Read`.
<!-- /FICHE -->

---

<!-- FICHE:SAG5 -->
## SAG5 [ ] — Mesurer le témoin, et conclure

**Dépend de** : `SAG4`.
**Fichiers** : ce fichier de fiches et `context AI/40-cout-juste.md` (par
`vlp.py cout`), `agents/fiche.md`, `context AI/35-bilan.md`, `CLAUDE.md`, le
journal de `context AI/08-etat.md`, et la mémoire de l'utilisateur si elle
cite 0,176 $.

**Prompt**
Mesure `SAG3`, la fiche témoin, et pose-la à côté de la main et de Q recompté.

1. `vlp.py cout` sur ce fichier : la ligne de `SAG3`, tokens et $, chef et
   sous-agent compris. Dans la transcription du sous-agent : ses tours, et sa
   fin — statut rendu (`end_turn`) ou coupé (`tool_use`).
2. `vlp.py cout` sur `40-cout-juste.md` : les fiches de code de CPT, jouées à la
   main — la référence.
3. Une table de trois lignes, comptes bruts : Q recompté (`SAG1`), `SAG3`
   enchaînée, CPT à la main — $ par fiche, tours, fin.
4. Réajuste `maxTurns` sur les tours de `SAG3` si l'écart le demande ; dis pourquoi.
5. Si `SAG1` a démenti le 0,176 $ : corrige `35-bilan.md`, `CLAUDE.md` et la
   mémoire qui le citent, par le chiffre recompté. Les entrées datées du
   journal ne se touchent pas.
6. Au journal : la table, le verdict en une phrase — sur une fiche de code,
   `/vlp:enchainer` coûte-t-il moins qu'à la main ? — et les commandes.

**Critère de fin**
Le journal porte la table à trois lignes, comptes bruts et commandes ;
`35-bilan.md`, `CLAUDE.md` et la mémoire ne citent plus de chiffre que `SAG1` a
démenti.
<!-- /FICHE -->
