> **QUAND LIRE** : on joue une fiche `E*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache E<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier E — Enchaîner les fiches

**CLOS** le 2026-09-10. Ne se rejoue pas — ne sert plus qu'à relire son socle.
E7 et E8 restent non cochées, abandonnées : le chef de `/vlp:enchainer` (socle
de session ~70k, ~12 appels par fiche) coûtait plus que les fiches jouées à la
main. Commande, agent `fiche`, contrat et mode `enchaine` retirés du kit.

**À quoi il sert.** Aujourd'hui chaque fiche se lance à la main (`/clear`, puis
`/vlp:tache`). Le chantier ajoute `/vlp:enchainer` : un chef qui joue les fiches
non cochées une par une, chacune dans un sous-agent neuf, et s'arrête au premier
retour humain — questionnaire, puis reprise avec la réponse.

**Fait.** Rien. Ouvert le 2026-09-10, cadré en 8 fiches, `E1` à jouer.

## Le socle commun

**Noms retenus — ne pas en inventer d'autres.**

| Nom | Où | Rôle |
|---|---|---|
| `/vlp:enchainer` | `commands/enchainer.md` (nouveau) | le chef d'orchestre |
| argument `enchaine` | `commands/tache.md` | mode sans question : rend un statut et s'arrête |
| contrat de retour | `enchainement.md` (nouveau, racine du kit) | seul endroit du format ; tache et enchainer y renvoient, ne le recopient pas |
| `**Critère de fin** (visuel)` | gabarit `templates/context AI/fichier-de-fiches.md`, titre `**Critère de fin**` | marque grep-able d'un arrêt prévu ; sans la marque = scriptable |

**Fichiers du kit concernés** (chemins depuis la racine du kit = ce dépôt =
`${CLAUDE_PLUGIN_ROOT}`) : `commands/tache.md` (359 lignes ; `allowed-tools`
ligne 4 ; bloc Tentatives à l'étape 5 ; artefact à l'étape 6 bis ; clôture à
l'étape 7), `methode-chantier.md` (section « Les deux formes de critère de
fin »), `cloture.md` (lu, jamais modifié).

**Le contrat de retour — trois statuts, ~10 lignes, format fixe.** E4 en écrit
la forme exacte dans `enchainement.md` ; d'ici là, voici son contenu :

- `FAITE` — critère de fin constaté, avec ses comptes bruts ; case cochée.
- `RETOUR` — ce que la fiche attend d'un humain, et pourquoi ; case non cochée.
- `BLOQUÉE` — deux tentatives épuisées, erreur brute ; bloc Tentatives écrit.

**Les arrêts.**

- *Prévus* : fiche dont le critère porte `(visuel)`. Le chef les annonce avant
  de démarrer : « je joue E1 → E3, arrêt prévu à E4 : <critère> ».
- *Imprévus* : décision que la fiche ne tranche pas, dépendance non cochée,
  permission refusée, fiche portant déjà un bloc Tentatives.

**Invariants du chef.**

- Un sous-agent neuf par fiche ; jamais deux fiches dans un même contexte.
- Il ne lit jamais le fichier de fiches en entier : titres et lignes
  `**Critère de fin**` par `grep`, rien d'autre. Il ne garde que les comptes
  rendus.
- Au `RETOUR` : questionnaire (`AskUserQuestion`), coche ou non selon la
  réponse, puis reprend. Au `BLOQUÉE` : il s'arrête.
- Plafond : 5 fiches par lancement, puis arrêt avec bilan.

**Mesures — remplies par E2 et E3, relues par E4 à E6.** Tant qu'une ligne vaut
« à mesurer », aucune fiche n'en présume la réponse.

| Question | Réponse | Preuve |
|---|---|---|
| Frontmatter : `Agent` et `AskUserQuestion` ouvrables dans une commande de plugin ? | Oui — les deux sont des noms d'outils valides pour `allowed-tools`. | https://code.claude.com/docs/en/tools-reference — « `Agent` \| Spawns a subagent with its own context window to handle a task. » |
| Un sous-agent exécute tache.md : par `Skill` `vlp:tache`, ou par `Read` du fichier ? | Les deux marchent et rendent le même résultat sur S1 (fichier écrit, case cochée) — mesuré en vrai. `Skill vlp:tache S1` déroule normalement (repérage CHANTIER.md, fiche identifiée, exécution, arrêt en fin d'étape 6 pour confirmation avant de cocher — exactement comme prévu). `Read` de `commands/tache.md` suivi comme instructions ordinaires marche aussi, sans friction majeure ; seul accroc : `Edit` exige un `Read` préalable du fichier cible, contourné en lisant seulement la plage du titre. | Mesure directe (deux sous-agents, E3) |
| Un sous-agent peut-il `Artifact` read + publish avec `url` ? | Oui, les trois étapes réussissent sans refus : publish initial rend une URL, `read` de cette URL rend le HTML publié, republish avec `url` met à jour en place (même URL, pas de doublon). Le `read` intermédiaire n'était pas un prérequis technique signalé par l'outil — juste une étape de vérification. | Mesure directe (sous-agent, E3) : `"Published ... at https://claude.ai/code/artifact/cac2d626-…"` inchangée après republication |
| Permissions héritées ? Un refus : il bloque, ou il échoue proprement ? | Contredit la doctrine lue en E2 : une commande Bash hors de `allowed-tools` (`python --version`, absente de la liste de `tache.md`) s'est exécutée **normalement**, sans refus ni attente d'approbation. Explication probable : `Skill` rejoue `tache.md` comme contenu de conversation dans la session appelante, pas dans un sous-agent isolé au jeu d'outils restreint — le frontmatter `allowed-tools` ne contraint donc que l'exécution native en commande slash, pas le rejeu via `Skill`. | Mesure directe (sous-agent, E3) : `Python 3.14.6` rendu sans erreur ; contredit https://code.claude.com/docs/en/agents#available-tools et #permission-modes lus en E2 |
| Contexte du chef après 3 fiches | à mesurer (E7) | |

**Le bac à sable** : `../vlp-bac-a-sable`, à côté du kit, créé par E1. Chantier
de fiches `S1`–`S4` : S1 scriptable, S2 `(visuel)`, S3 bloque exprès, S4 dépend
de S3. Jamais Cairn : il a du travail non commité.

**Ce qu'on ne fait pas.** Pas de fiches en parallèle. Pas de reprise
automatique après `BLOQUÉE`. La clôture reste `cloture.md`, à l'identique de
`/vlp:tache`. L'usage manuel de `/vlp:tache` ne change pas : sans l'argument
`enchaine`, elle se comporte exactement comme avant.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `E1` | Monter le bac à sable | rien |
| `E2` | Vérifier la doc officielle des plugins et sous-agents | rien |
| `E3` | Mesurer un sous-agent en vrai dans le bac à sable | `E1`, `E2` |
| `E4` | Ajouter le mode `enchaine` à tache et le contrat de retour | `E3` |
| `E5` | Écrire la boucle nominale de `/vlp:enchainer` | `E4` |
| `E6` | Gérer les arrêts du chef | `E5` |
| `E7` | Rejouer sur le bac à sable et mesurer le coût du chef | `E6` |
| `E8` | Publier la cinquième commande | `E7` |

E1 et E2 sont indépendantes (l'une ou l'autre d'abord) ; tout le reste est en
file.

---

<!-- FICHE:E1 -->
## E1 [x] — Monter le bac à sable

**Dépend de** : rien.
**Fichiers** : `../vlp-bac-a-sable/` (nouveau) — et rien d'autre.

**Prompt**
Crée `../vlp-bac-a-sable`, à côté du kit, et équipe-le par `/vlp:init` (outil
`Skill`, `vlp:init`). Puis écris à la main, selon le gabarit
`templates/context AI/fichier-de-fiches.md` du kit, un fichier de fiches de
quatre fiches triviales, préfixe `S` :

- `S1` écrit `a.txt` avec trois lignes ; critère scriptable : `wc -l a.txt`
  rend 3.
- `S2` écrit `b.txt` ; critère `**Critère de fin** (visuel)` : l'utilisateur
  ouvre le fichier et confirme ce qu'il lit.
- `S3` bloque exprès : son critère exige une commande qui échoue toujours
  (`ls fichier-qui-n-existe-pas`).
- `S4` dépend de `S3` et n'a rien à faire d'autre.

Déclare le chantier dans son `CHANTIER.md` (fichier de fiches courant, plage
`S1..S4`). Ne publie aucune page : le bac à sable n'en a pas besoin, et la ligne
« artefact du chantier » y reste à « aucun ».

**Critère de fin**
`grep -c '^<!-- FICHE:S' ../vlp-bac-a-sable/"context AI"/*.md` rend 4, et
`grep -n '(visuel)' …` montre la seule ligne de S2 — comptes affichés.
<!-- /FICHE -->

---

<!-- FICHE:E2 -->
## E2 [x] — Vérifier la doc officielle des plugins et sous-agents

**Dépend de** : rien.
**Fichiers** : `context AI/09-enchainer.md` (table « Mesures » du socle) — et
rien d'autre.

**Prompt**
Réponds, **par la doc officielle de Claude Code** (WebFetch sur
docs.claude.com / code.claude.com), jamais de mémoire, à trois questions :

1. Le frontmatter `allowed-tools` d'une commande de plugin peut-il ouvrir
   `Agent` et `AskUserQuestion` ? Sous quel nom exact ?
2. Un sous-agent lancé par `Agent` peut-il invoquer une commande de plugin
   (`Skill`) ? A-t-il accès à `AskUserQuestion` ?
3. Un sous-agent hérite-t-il des permissions du projet
   (`.claude/settings.json`) et du mode de permission du parent ?

Pour chacune, remplis la ligne de la table « Mesures » : la réponse en une
ligne, et en preuve l'URL de la page et la phrase qui tranche (moins de quinze
mots, entre guillemets). Une question que la doc ne tranche pas reste « à
mesurer (E3) » : dis-le, ne comble pas.

**Critère de fin**
La table « Mesures » : la ligne frontmatter ne vaut plus « à mesurer », et
chaque réponse porte une URL — `grep -c 'https://' ` sur la table affiché.
<!-- /FICHE -->

---

<!-- FICHE:E3 -->
## E3 [x] — Mesurer un sous-agent en vrai dans le bac à sable

**Dépend de** : `E1`, `E2`.
**Fichiers** : `context AI/09-enchainer.md` (table « Mesures »),
`../vlp-bac-a-sable/` — et rien d'autre.

**Prompt**
Depuis la racine du bac à sable, lance des sous-agents (`Agent`) et **lis
leurs comptes rendus toi-même** :

1. Un sous-agent joue `S1` en invoquant `Skill` `vlp:tache S1` ; un second,
   après remise à zéro de S1, en lisant `commands/tache.md` du kit par `Read`
   et en le suivant. Note ce qui a marché, et ce que chacun a rendu.
2. Un sous-agent fait `Artifact` `action: "publish"` d'une page jetable, puis
   `read` et republie avec son `url`. Note l'URL et chaque retour d'outil.
3. Un sous-agent tente une commande que le bac à sable n'autorise pas. Note
   s'il attend une réponse, échoue proprement, ou contourne.

Remplis les lignes de la table « Mesures » : réponse, et en preuve la sortie
brute (trois lignes au plus). Si une réponse contredit ce que E2 a lu dans la
doc, la mesure gagne : écris les deux.

**Critère de fin**
Sur la seule table « Mesures » du socle (`sed -n '58,64p'` du fichier de
fiches) : `grep -c 'à mesurer (E3)'` rend 0, et `grep -c 'à mesurer'` rend 1
(la ligne E7) — les deux comptes affichés.
<!-- /FICHE -->

---

<!-- FICHE:E4 -->
## E4 [x] — Ajouter le mode `enchaine` à tache et le contrat de retour

**Dépend de** : `E3`.
**Fichiers** : `commands/tache.md`, `enchainement.md` (nouveau),
`templates/context AI/fichier-de-fiches.md`, `methode-chantier.md` — et rien
d'autre.

**Prompt**
Écris `enchainement.md` à la racine du kit : le contrat de retour du socle, en
format fixe (~10 lignes, premier mot `FAITE` / `RETOUR` / `BLOQUÉE`), et la
liste des arrêts imprévus. C'est son seul endroit.

Dans `commands/tache.md`, ajoute l'argument `enchaine` (et à
`argument-hint`) : dans ce mode, **chaque endroit où tache poserait une
question** rend `RETOUR` et s'arrête ; le critère `(visuel)` rend `RETOUR` ;
l'arrêt à deux tentatives rend `BLOQUÉE` ; la fin normale rend `FAITE`. Le
format se lit dans `enchainement.md`, il n'est pas recopié. L'artefact (6 bis)
suit la table « Mesures ». Sans `enchaine`, rien ne change : garde le diff
court.

Dans le gabarit de fiche et dans la section « Les deux formes de critère de
fin » de la méthode, ajoute la marque `**Critère de fin** (visuel)`, en une
ligne chacun.

**Critère de fin**
Un sous-agent joue `S1` du bac à sable en mode `enchaine` et rend `FAITE` avec
`wc -l` = 3 ; un autre joue `S2` et rend `RETOUR`. Les deux comptes rendus
affichés tels quels.
<!-- /FICHE -->

---

<!-- FICHE:E5 -->
## E5 [x] — Écrire la boucle nominale de `/vlp:enchainer`

**Dépend de** : `E4`.
**Fichiers** : `commands/enchainer.md` (nouveau), `commands/tache.md` (étapes
0 et 0 bis, en lecture), `enchainement.md` (en lecture) — et rien d'autre.

**Prompt**
Écris `commands/enchainer.md`, en français, autoportante. Frontmatter : ce que
la table « Mesures » a établi. Étapes :

1. Trouver le projet et le fichier de fiches courant : **renvoie** aux étapes
   0 et 0 bis de tache.md, ne les recopie pas.
2. Lister par `grep` les titres non cochés et leurs lignes `**Critère de
   fin**`. Annoncer le plan : les fiches à jouer, l'arrêt prévu (`(visuel)`),
   le plafond de 5.
3. Pour chaque fiche : un sous-agent neuf, qui joue tache en mode `enchaine` par
   la voie que E3 a prouvée ; lire son compte rendu ; à `FAITE`, passer à la
   suivante.
4. Au plafond, ou quand il n'y a plus de fiche : bilan — une ligne par fiche,
   statut et comptes bruts.

Ici, seul `FAITE` est traité : pour `RETOUR` et `BLOQUÉE`, le chef s'arrête et
affiche le compte rendu brut ; E6 fera mieux.

**Critère de fin**
`/vlp:enchainer` lancé dans le bac à sable (après `/reload-plugins`) annonce
son plan avec l'arrêt prévu à S2, joue S1 et s'arrête sur le `RETOUR` de S2 —
sortie recopiée.
<!-- /FICHE -->

---

<!-- FICHE:E6 -->
## E6 [x] — Gérer les arrêts du chef

**Dépend de** : `E5`.
**Fichiers** : `commands/enchainer.md`, `enchainement.md` (en lecture),
`cloture.md` (en lecture) — et rien d'autre.

**Prompt**
Complète `commands/enchainer.md` :

- `RETOUR` : un questionnaire (`AskUserQuestion`) construit depuis le compte
  rendu — ce qu'on attend, et pourquoi. Selon la réponse, le chef coche la case
  (une seule ligne `## <X>n [ ]` → `[x]`) ou la laisse, puis **reprend** la
  boucle.
- `BLOQUÉE` : arrêt, bilan, le bloc Tentatives est déjà dans la fiche.
- Imprévus : avant de lancer une fiche, le chef vérifie par `grep` ses
  dépendances cochées et l'absence de bloc Tentatives ; sinon, questionnaire.
- La page du chantier : régénérée par le sous-agent ou par le chef une fois par
  arrêt, selon la table « Mesures ».
- Dernière fiche faite : la clôture de `cloture.md`, à l'identique de tache.

**Critère de fin**
Dans le bac à sable remis à zéro, `/vlp:enchainer` joue S1, pose le
questionnaire de S2, reprend après « oui », et s'arrête sur `BLOQUÉE` à S3 sans
lancer S4 — sortie recopiée.
<!-- /FICHE -->

---

<!-- FICHE:E7 -->
## E7 [ ] — Diviser par 5 le coût d'une fiche enchaînée

**Dépend de** : `E6`.
**Fichiers** : `agents/fiche.md` (nouveau), `commands/enchainer.md`,
`enchainement.md` (en lecture), `../vlp-bac-a-sable/` — et rien d'autre.

**Mesure de départ** (2026-09-10) : S3 seul = 74 503 tokens, 11 appels
d'outils ; S2+S3 = 143,5k côté chef — jugé inacceptable. Coût ≈ contexte ×
tours : un `general-purpose` porte tous les outils (MCP, skills) et `tache.md`
entier (359 lignes), repayés à chaque tour.

**Doc lue** (https://code.claude.com/docs/en/sub-agents,
https://code.claude.com/docs/en/plugins-reference) : un agent de plugin reçoit
**son seul corps** comme prompt système, pas celui de Claude Code ; il hérite
`CLAUDE.md`, et les MCP sauf `tools:` restreint. Champs admis : `model`,
`effort`, `maxTurns`, `tools`, `disallowedTools` — pas `permissionMode`,
`hooks`, `mcpServers`. Nom d'appel : `vlp:fiche`.

**Prompt**
1. `agents/fiche.md` : `model: haiku`, `effort: low`, `maxTurns: 8`,
   `tools: Read, Edit, Write, Grep, Bash` (ni `Skill`, ni `Agent`, ni MCP).
   Corps ≤ 30 lignes : exécuter la fiche reçue, livrer, vérifier, deux
   tentatives au plus, bloc Tentatives si échec, cocher si `FAITE`, rendre le
   compte rendu de `${CLAUDE_PLUGIN_ROOT}/enchainement.md` — y renvoyer, ne pas
   le recopier. Aucun artefact.
2. `commands/enchainer.md` étape 3 : le chef extrait lui-même la fiche (`sed`
   des marqueurs), le socle (`awk` de `tache.md` étape 4) et les lignes
   livraison / vérification / contraintes de `CHANTIER.md`, et les passe dans
   le message d'`Agent` `subagent_type: vlp:fiche`. Le sous-agent ne relit ni
   `tache.md` ni `CHANTIER.md`.
3. Artefact : plus de régénération par fiche ; le chef la fait **une fois**,
   en fin de lancement (les quatre gestes de `tache.md` 6 bis).
4. Bilan : `subagent_tokens` et `tool_uses` par fiche, lus dans le `<usage>`
   que rend `Agent` — comptes bruts, jamais estimés.
5. Étape 3 bis : après un `RETOUR`, la série se prolonge jusqu'au prochain
   `(visuel)` ou au plafond — le texte d'E6 dit « fiche suivante de la série »
   alors que la série s'arrête au `(visuel)` ; le run d'E6 a joué S3 quand même.
6. Dire en une ligne ce que devient le mode `enchaine` de `tache.md` (garder,
   ou retirer en E8) — ne pas trancher seul.

**Critère de fin** (visuel)
Bac à sable remis à zéro, `/reload-plugins`, `/vlp:enchainer` : le bilan
affiche pour S1 et S3 un `subagent_tokens` **≤ 15 000** chacun (÷5 sur
74 503), S3 toujours `BLOQUÉE`, S4 non lancé. Au-delà, la fiche n'est pas
faite. Coût attendu de la vérification : ~3 × 15k + le chef.
<!-- /FICHE -->

---

<!-- FICHE:E8 -->
## E8 [ ] — Publier la cinquième commande

**Dépend de** : `E7`.
**Fichiers** : `README.md`, `INSTALLATION.md`, `TLDR README.txt`,
`.claude-plugin/plugin.json`, `CLAUDE.md` — et rien d'autre.

**Prompt**
Déclare `/vlp:enchainer` comme cinquième commande : une entrée courte dans
`README.md`, `INSTALLATION.md` et `TLDR README.txt`, au même format que les
quatre autres — `grep -n 'vlp:check'` dans chacun donne l'endroit. Dans
`CLAUDE.md`, « quatre commandes » devient « cinq ». Passe `version` de
`plugin.json` à `3.1.0`. Rien d'autre : pas de réécriture des docs.

**Critère de fin**
`grep -c 'vlp:enchainer'` rend au moins 1 dans chacun des quatre fichiers de
doc, et `grep '"version"' .claude-plugin/plugin.json` montre `3.1.0` — comptes
affichés.
<!-- /FICHE -->
