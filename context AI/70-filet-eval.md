> **QUAND LIRE** : on joue une fiche `EVF*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache EVF<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier EVF — Le filet en eval rejouable

**État** : les deux essais de `FIL3` (le filet tire à plafond bas) deviennent des cas
d'eval du plugin, rejouables en un appel.

**Estimé.** 2 fiches · ≈7,79 $ — ≈3,89 $/fiche sur 57 clos (le 2026-09-26).

**Fait.** Rien. Ouvert le 2026-09-26, cadré en 3 fiches, `EVF1` à jouer.

**Session** : 81f28c74-89aa-4815-b804-db93de007ebc

## Le socle commun

Décidé au cadrage (2026-09-26) : **d'abord trancher**, en un essai minimal, si un eval
voit ce que fait un sous-agent ; puis un cas par essai de `FIL3`. Si `EVF1` répond
**non**, `EVF2` et `EVF3` se redécoupent en **plan B** (`/vlp:chantier`, « redécouper ») :
`vlp.py` compare la transcription aux chiffres attendus, le lancement `claude -p`
reste à la main — la règle 4 de `CLAUDE.md` (zéro appel modèle) ne bouge pas.

**Dehors** : `RAT` (TODO n° 43, un `Read` raté) ; toute modification de
`agents/fiche.md` dans le kit — le plafond bas se pose sur une **copie jetable** du kit,
jamais sur le vrai (`FIL3` l'avait baissé à la main, 80 → 10, puis remis) ; graders
payants (`llm`, `baseline`).

**Les evals** — le contrat, le binaire introuvable dans le PATH et la commande de
lancement vivent dans le socle de `context AI/18-evals.md` : s'y reporter, ne pas les
recopier. Ajouter à la commande : `--tag <le cas>`, `--keep-temp` (garde la trace et
le bac), et un `--max-cost-usd` à 0,5 par cas. Forme d'un cas : `evals/hook/case.yaml`
(grader `regex` à `target: trace`) ; d'un bac à sable : `evals/chantier/case.yaml` et son
`fixture.sh` (`scaffold_script`, lancé avec `--scaffold`).

**L'essai à rejouer** — entrée « 2026-09-24 — FIL3 » de `context AI/08-etat.md` : la
consigne `claude -p` (« Appelle l'outil Skill avec skill "vlp:jouer"… »), le texte de
l'avertissement, les chiffres de `F1` et `F2`. Le bac se pose par `vlp.py bac <dossier>` ;
une transcription se compte par `vlp.py transcription <jsonl>` (docstring de
`scripts/vlp.py`, puces `bac` et `transcription`).

**Invariants** : aucun cas ne touche un projet réel ni le kit sur disque ; chaque verdict
s'écrit au journal de `context AI/08-etat.md` avec `costUsd`, `turns` et la sortie brute
de chaque grader ; tout grader positif a son **témoin négatif** (même cas, attendu
absent, doit échouer) — un grader qui passe toujours ne prouve rien.

## L'ordre des fiches

- `EVF4` — la carte injectée n'écrit plus dans le dossier du plugin. Aucune dépendance ;
  ajoutée le 2026-09-26 après le blocage d'`EVF1`.
- `EVF1` — l'eval voit-il le sous-agent ? Dépend de `EVF4`.
- `EVF2` — le cas `F1` avec le filet, à plafond bas. Dépend de `EVF1` (réponse oui).
- `EVF3` — le cas `F2` (Bash, `exit 3`). Dépend de `EVF2`.

---

<!-- FICHE:EVF4 -->
## EVF4 [x] — La carte injectée n'écrit plus dans le dossier du plugin

**Session** : 81f28c74-89aa-4815-b804-db93de007ebc
**Dépend de** : rien.
**Fichiers** : les 7 `skills/*/SKILL.md` (ligne `` !` `` de la carte) ; `scripts/vlp.py`
(docstring de `carte_injectee`) ; `scripts/test-vlp.py` (tests NIV1 et dette REL, vers
la ligne 1812) ; `evals/filet-vue/` — et rien d'autre.

**Prompt**
Sous eval, le préambule `` !` `` de `vlp:jouer` est refusé même `--allow-tools Bash`
(`EVF1`, tentative 4) ; cause supposée : `2>"${CLAUDE_PLUGIN_ROOT}/relais-python.err"`,
écrit hors du workspace. Prouve-le d'abord, sur une **copie jetable** du kit sous WSL2,
cas `filet-vue` : variante A sans aucune redirection ; variante B vers
`${CLAUDE_PLUGIN_DATA}/relais-python.err` (doc plugins-reference : dossier du plugin,
créé à la première référence, substitué dans le corps d'une skill). Retiens la variante
qui laisse `vlp:jouer` forker ; applique-la aux 7 copies, au test et à la docstring.
Aucune ne passe : `RETOUR` avec les deux sorties brutes.

**Critère de fin**
Au journal : `costUsd`, `turns` et la première ligne de résultat de chaque variante.
`scripts/test-vlp.py` passe ; **mutant** : une copie qui garde
`${CLAUDE_PLUGIN_ROOT}/relais-python.err` fait tomber le test.
`pyright scripts/vlp.py scripts/test-vlp.py` : `0 errors`.
<!-- /FICHE -->

---

<!-- FICHE:EVF1 -->
## EVF1 [x] — L'eval voit-il le sous-agent ?

**Tentatives** (2026-09-26) — résolu par : EVF4 : injection sans redirection ; eval sous WSL2 avec --allow-tools Bash, Read ajouté au cas

**Session** : 81f28c74-89aa-4815-b804-db93de007ebc
**Dépend de** : `EVF4`.
**Fichiers** : `claude plugin eval --help` ; la doc https://code.claude.com/docs/en/plugin-evals
(mot pour mot, la partie graders et `target`) ; `evals/hook/case.yaml`,
`evals/chantier/case.yaml`, `evals/chantier/fixture.sh` — et rien d'autre.

**Prompt**
Crée le cas `evals/filet-vue/` (tag `filet-vue`) : le bac à sable pose le bac de `FIL3`
par `vlp.py bac` ; la consigne est celle de `F1` dans le journal de `FIL3` ; le chef n'a
droit qu'à `Skill`. Plafond normal (80) : on ne cherche pas le filet, seulement la vue.
Graders : `tool_used` `Read` (le chef n'en a pas le droit : s'il passe, c'est le
sous-agent qu'il voit) ; `regex` `target: trace` sur « fichier 05 » ; témoin négatif
`regex` sur « fichier 13 » (n'existe pas). Lance une fois, `--keep-temp`. Puis cherche,
dans le dossier gardé, une transcription de sous-agent (`subagents/*.jsonl`) et passe-la
à `vlp.py transcription` : c'est le chemin du plan B s'il faut y venir.
🟡 Note aussi si `allowed_tools` du cas bride le sous-agent.

**Critère de fin**
Au journal : verdict **oui** ou **non** en tête, la sortie brute des trois graders,
`costUsd` et `turns` de `aggregate-result.json`, la commande de lancement exacte, et la
sortie de `vlp.py transcription` (ou « aucun `subagents/*.jsonl` gardé »). Le témoin
négatif **échoue** — sinon le verdict ne vaut rien et la fiche rend `RETOUR`.
<!-- /FICHE -->

---

<!-- FICHE:EVF2 -->
## EVF2 [x] — Le cas `F1` avec le filet, à plafond bas

**Session** : 81f28c74-89aa-4815-b804-db93de007ebc
**Dépend de** : `EVF1`, réponse **oui**. Réponse non : ne pas jouer, redécouper.
**Fichiers** : `evals/filet-vue/` (d'`EVF1`) ; `agents/fiche.md` (lecture seule, la
ligne `maxTurns`) ; `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Ajoute `vlp.py kit-essai <dossier> --max-turns <n>` : copie le kit (ce que charge le
plugin) dans un dossier absent ou vide, et y réécrit `maxTurns` d'`agents/fiche.md`
(sinon `GARDE:`, rien d'écrit). Puce de docstring ; test dans un dossier temporaire.
Puis transforme `evals/filet-vue/` en `evals/filet/` (tag `filet`), lancé sur une copie à
plafond 10. Graders : `regex` `target: trace` sur « Attention : 3 tours restants » ;
`regex` `last_message` sur `RETOUR`. Lance une fois ; puis le témoin : même cas sur une
copie à plafond 80.

**Critère de fin** — réécrit le 2026-09-26 après mesure, la nuit, à valider : la trace de
l'eval ne porte pas le contexte des hooks (grader `filet-warns` muet à 6 comme à 80).
Plafond 6 : `vlp.py transcription` de la transcription gardée compte `AVERTISSEMENTS=1` ;
plafond 80 : `AVERTISSEMENTS=0` ; l'eval voit les `Read` du sous-agent. Test de `kit-essai` :
`maxTurns 6` dans la copie, inchangé dans le kit, 2ᵉ appel → `GARDE:`. **Mutant** : ne pas
réécrire `maxTurns` fait tomber le test. `pyright scripts/vlp.py scripts/test-vlp.py` : `0 errors`.
<!-- /FICHE -->

---

<!-- FICHE:EVF3 -->
## EVF3 [ ] — Le cas `F2` (Bash, `exit 3`)

**Dépend de** : `EVF2`.
**Fichiers** : `evals/filet/` (d'`EVF2`) ; `evals/tache/case.yaml` (forme d'un cas tag
`wsl2`) — et rien d'autre.

**Prompt**
Ajoute à `evals/filet/` le cas de `F2` : consigne `F2` du journal de `FIL3`, plafond 10
par `kit-essai`, tag `wsl2` — Bash est refusé aux evals sous Windows (socle de
`context AI/18-evals.md`). Graders : ceux d'`EVF2`, plus `tool_used` `Bash`. Témoin :
plafond 80, « Attention » doit échouer. Si WSL2 n'est pas jouable ce jour-là, rends
`RETOUR` avec l'erreur brute : 🟡 une variante PowerShell est à trancher par l'utilisateur,
pas ici.

**Critère de fin**
Plafond 10 : les trois graders passent ; plafond 80 : « Attention » échoue. Au journal :
sorties brutes, `costUsd` et `turns`, et **la commande qui rejoue les deux cas en un
appel** — c'est le résultat du chantier.
<!-- /FICHE -->
