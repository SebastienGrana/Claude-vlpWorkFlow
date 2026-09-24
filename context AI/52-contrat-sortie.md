> **QUAND LIRE** : on joue une fiche `CON*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache CON<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier CON — Le contrat du sous-agent, vérifié à sa sortie

**À quoi il sert.** La nuit du 2026-09-24, 4 sous-agents `vlp:fiche` sur 14 ont
commité eux-mêmes, et le chef ne rattrape pas un commit (TODO n° 49). CON mesure
si la règle « aucun commit », maintenant chargée, tient ; puis essaie un hook qui
l'impose.

**Fait.** Rien. Ouvert le 2026-09-25, cadré en 5 fiches, `CON1` à jouer.

**Session** : 86153e75-a87d-48cf-97d5-2532aad54754

## Le socle commun

Le contrat, tel qu'`agents/fiche.md` le dit — on y renvoie, on ne le recopie pas :

| Clause | Où |
|---|---|
| mot-statut, premier caractère du dernier message | `agents/fiche.md:24` |
| coche par `vlp.py cocher` avant `FAITE` | `agents/fiche.md:44` |
| aucun commit | `agents/fiche.md:54` |

| Fait vérifié | Où |
|---|---|
| la règle « aucun commit » entre au commit `f98ceec`, 2026-09-24 02:07:40 +0200 | `git log -S"aucun commit" -- agents/fiche.md` |
| une définition d'agent se charge au démarrage de la session | TODO n° 49, `context AI/08-etat.md` (grep « \| 49 \| ») |
| transcription d'un sous-agent : `<session>/subagents/agent-<id>.jsonl` | `scripts/mesure-tokens.py:98`, `sous_agents` |
| son `.meta.json` voisin porte `"agentType":"vlp:fiche"` (lu le 2026-09-25) | à côté de chaque `agent-<id>.jsonl` |
| `mesure-tokens.py` s'importe par `mesure()` | `scripts/vlp.py:1052` |
| dans un sous-agent, l'entrée d'un hook `PostToolUse` porte `agent_type` et `agent_id` | `cmd_filet`, `scripts/vlp.py:927` |
| les hooks du plugin, chaque commande en double `python3` / `py` | `hooks/hooks.json` |
| tests : `py scripts/test-vlp.py` ; une fiche de code nomme son mutant | `methode-chantier.md`, « Anatomie d'une fiche » |

Décidé au cadrage : **seuil de 5** sous-agents `vlp:fiche` chargés — au-delà,
`CON2` est sautée.

🟡 Un `/reload-plugins` en cours de session charge aussi la règle, sans trace
connue dans la transcription : « session démarrée après `f98ceec` » est la
seule preuve qu'on sait lire.

**Dehors.** Le relecteur `vlp:relecture` : même risque peut-être, autre
chantier. Les contrôles du chef (étape 2 d'`/vlp:enchainer`, la case relue par
`CAS`) : ils restent tels quels.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `CON1` | Lire le contrat dans une transcription | rien |
| `CON2` | Jouer des témoins, si le compte est maigre | `CON1` |
| `CON3` | Essayer les deux hooks | `CON1` |
| `CON4` | Écrire le hook retenu | `CON3` |
| `CON5` | Le prouver sur un sous-agent | `CON4` |

`CON2` et `CON3` sont parallélisables. `CON4` et `CON5` sont écrites sous
réserve : l'arrêt de `CON3` peut les redécouper.

---

<!-- FICHE:CON1 -->
## CON1 [x] — Lire le contrat dans une transcription

**Session** : 0d303b02-229a-40df-824e-65d205a4141e
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `scripts/mesure-tokens.py` lignes 82–114 — et rien d'autre.

**Prompt**
Ajoute à `vlp.py` la sous-commande `contrat <transcription>…`. Pour chaque
transcription de sous-agent, une ligne : son id, son `agentType` (lu dans le
`.meta.json` voisin), l'heure de départ de sa session parente, le premier mot
de son dernier message texte, et le nombre d'appels `Bash` ou `PowerShell` qui
écrivent dans Git (`git commit`, `git add`, `git reset`, `git -C … commit`).
Sans argument : toutes les transcriptions `vlp:fiche` de
`~/.claude/projects/*/*/subagents/`. Réutilise `sous_agents` et `ouvrir` par
`mesure()`, ne les recopie pas. Mets-la dans la docstring du module.
Teste-la sur deux transcriptions fabriquées : une propre, une qui commite par
`git -C`. Puis lance-la sans argument, et écris au journal de ce chantier
(`context AI/08-etat.md`) : combien de sous-agents dont la session a démarré
après `f98ceec`, combien ont commité, combien n'ont pas le statut en tête.

**Critère de fin**
`py scripts/test-vlp.py` passe ; mutant : ne plus compter `git -C … commit`
fait tomber le test du témoin sale. Le journal porte les trois comptes bruts
et la commande qui les donne.
<!-- /FICHE -->

---

<!-- FICHE:CON2 -->
## CON2 [x] — Jouer des témoins, si le compte est maigre

**Session** : 0d303b02-229a-40df-824e-65d205a4141e
**Dépend de** : `CON1`.
**Fichiers** : `context AI/08-etat.md` (journal), et ce fichier de fiches pour trois fiches témoins ajoutées puis retirées.

**Prompt**
Lis au journal le compte de `CON1`. S'il atteint le seuil du socle, coche cette
fiche en écrivant « sautée : N sous-agents » et arrête-toi.
Sinon, cette fiche se joue **à la main**, par `/vlp:tache CON2` : un sous-agent
ne lance pas de sous-agent. Ajoute trois fiches témoins triviales en fin de
fichier (une ligne à écrire dans un fichier du dossier de contexte, rien à
commiter), joue chacune par la skill `vlp:jouer`, puis lance `vlp.py contrat`
sur leurs trois transcriptions. Retire les témoins et ce qu'ils ont écrit.
Écris au journal : les trois lignes de `contrat`, et le coût par
`vlp.py cout` sur la session.

**Critère de fin**
Le journal porte soit « sautée » et le compte de `CON1`, soit trois lignes de
`contrat` et un coût en $ ; `git status` ne montre aucun reste des témoins.
<!-- /FICHE -->

---

<!-- FICHE:CON3 -->
## CON3 [ ] — Essayer les deux hooks

**Dépend de** : `CON1`.
**Fichiers** : `hooks/hooks.json`, `scripts/vlp.py`, `context AI/08-etat.md` (journal).

**Prompt**
Lis la doc officielle des hooks de Claude Code, et cite-la avec lien et date :
`SubagentStop` peut-il renvoyer le sous-agent au travail, et avec quel champ ?
`PreToolUse` porte-t-il `agent_type` dans un sous-agent, et peut-il refuser un
appel ? Un événement au départ du sous-agent existe-t-il, pour noter `HEAD` ?
Puis vérifie en vrai : une sous-commande `vlp.py sonde` qui ajoute son entrée
JSON brute à un fichier du dossier temporaire, branchée sur `SubagentStop`,
`PreToolUse` et l'événement de départ s'il existe. Demande `/reload-plugins`,
fais jouer une fiche témoin, et recopie au journal les champs réellement reçus.
Débranche la sonde ensuite.
Rends la main avec un tableau : pour chaque hook, ce qu'il peut faire, prouvé
ou seulement lu.

**Critère de fin** (visuel)
L'utilisateur lit le tableau au journal et choisit le hook — `SubagentStop`,
`PreToolUse`, les deux, ou aucun ; `hooks/hooks.json` n'a plus la sonde.
<!-- /FICHE -->

---

<!-- FICHE:CON4 -->
## CON4 [ ] — Écrire le hook retenu

**Dépend de** : `CON3`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `hooks/hooks.json`.

**Prompt**
Écris le hook que l'utilisateur a choisi à `CON3`, comme sous-commande de
`vlp.py`, sur le modèle de `cmd_filet` : il ne fait rien hors d'un sous-agent
`vlp:fiche`. Selon le choix : refuser un appel qui écrit dans Git (réutilise
la détection de `contrat`), et/ou renvoyer le sous-agent quand le statut n'est
pas en tête, que `FAITE` tombe sur une case vide, ou que `HEAD` a bougé — avec
une raison d'une ligne qui dit quoi corriger. Branche-le dans
`hooks/hooks.json`, en double `python3` / `py`. Une entrée illisible ne bloque
jamais : le hook se tait.
Si `CON3` a dit « aucun », coche cette fiche en l'écrivant, et rends la main.

**Critère de fin**
`py scripts/test-vlp.py` passe, avec un test par cas refusé et un cas propre
laissé passer ; mutant : inverser le test d'`agent_type` fait tomber le test
du sous-agent `vlp:relecture` laissé passer.
<!-- /FICHE -->

---

<!-- FICHE:CON5 -->
## CON5 [ ] — Le prouver sur un sous-agent

**Dépend de** : `CON4`.
**Fichiers** : `context AI/08-etat.md` (journal), et ce fichier de fiches pour une fiche témoin ajoutée puis retirée.

**Prompt**
Cette fiche se joue à la main, après `/reload-plugins`. Ajoute une fiche
témoin qui pousse à rater le contrat : son prompt demande de commiter le
fichier qu'elle écrit. Joue-la par `vlp:jouer`. Puis `vlp.py contrat` sur sa
transcription, et `git log -1` avant et après.
Écris au journal : ce que le hook a fait (refus ou renvoi, cité depuis la
transcription), le statut rendu, `HEAD` avant et après, le coût. Retire le
témoin et ce qu'il a écrit.

**Critère de fin**
`HEAD` est le même avant et après le témoin, et la transcription montre le
hook qui a tiré ; les deux sont recopiés au journal avec la commande.
<!-- /FICHE -->
