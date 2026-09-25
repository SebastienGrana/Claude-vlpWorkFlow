> **QUAND LIRE** : on joue une fiche `GAR*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache GAR<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier GAR — Le gardien renvoie pour de vrai

**À quoi il sert.** Le renvoi de `vlp.py gardien` sur `SubagentStop` a tiré en vrai sur
`GLO1` (« Excellent! »), mais le `FAITE` sur case vide qui a suivi est passé : un arrêt
déjà renvoyé n'est plus jugé (TODO n° 59). GAR ferme ce trou, retire la sonde, et le prouve.

**Fait.** Rien. Ouvert le 2026-09-25, cadré en 3 fiches, `GAR1` à jouer. Cadré seul :
l'utilisateur dormait ; les 🟡 tranchés ici sont à valider au réveil.

**Session** : ca431cf8-167e-4c10-8bce-210c5f48a675

## Le socle commun

| Fait vérifié | Où |
|---|---|
| `cmd_gardien` ne juge un `SubagentStop` que si `stop_hook_active` est faux | `scripts/vlp.py`, `def cmd_gardien` |
| `verdict_fin` : tête hors `STATUTS` → renvoi ; `FAITE` → `cocher --verifier`, `TÊTE ` ou `CASE <fiche> [ ]` → renvoi | `scripts/vlp.py`, `def verdict_fin` |
| la sonde de `CON3` : `SONDE`, `cmd_sonde`, sous-commande `sonde`, sa docstring, ses tests ; hors de `hooks/hooks.json` | `scripts/vlp.py`, `scripts/test-vlp.py` (« sonde (chantier CON3) ») |
| tests du gardien, dont « déjà renvoyé une fois, laissé » | `scripts/test-vlp.py`, « gardien (chantier CON4) » |
| le cas vrai : `GLO1`, transcription `agent-ac9db03f95e8ec2b0`, lignes 113–116 : deux `Stop hook feedback` sur « Excellent! », puis `FAITE` sur case vide non renvoyé | `~/.claude/projects/C--Users-znorr-Documents-ProgPerso-Claude-vlpWorkflow/ca431cf8-…/subagents/` |
| tests : `py scripts/test-vlp.py` ; pyright sur les fichiers touchés ; une fiche de code nomme son mutant | `methode-chantier.md`, « Anatomie d'une fiche » |

Décidé au cadrage, seul : sous `stop_hook_active`, on juge **encore** un `FAITE` (case
vide, `TÊTE`) mais **plus** la tête d'un message sans statut. Pourquoi : un `FAITE` a une
sortie honnête — `RETOUR` ou `BLOQUÉE` —, donc pas de boucle forcée ; une tête ratée deux
fois ne se corrige plus par un troisième renvoi, le chef la lit en « aucun statut ».

**Dehors.** Le doublon `python3` + `py` des hooks (chantier `PYT`) ; le gardien derrière
le relecteur (`RLG`).

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `GAR1` | Juger un FAITE même après un renvoi | rien |
| `GAR2` | Retirer la sonde | rien |
| `GAR3` | Le prouver sur un témoin | `GAR1` |

`GAR1` et `GAR2` sont indépendantes. `GAR3` se joue à la main : un sous-agent ne lance pas
de sous-agent.

---

<!-- FICHE:GAR1 -->
## GAR1 [ ] — Juger un FAITE même après un renvoi

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Dans `cmd_gardien`, un `SubagentStop` avec `stop_hook_active` vrai n'est plus laissé
d'office : il passe à `verdict_fin` avec un drapeau qui saute le seul contrôle de la tête
(message sans statut en tête → `None`). Le contrôle d'un `FAITE` — `TÊTE` et case vide —
s'applique dans les deux cas. Garde `verdict_fin` lisible : un paramètre nommé, pas une
copie de la fonction. Mets à jour la docstring du module (ligne `gardien`) en une phrase.
Dans les tests « gardien (chantier CON4) », garde « déjà renvoyé une fois, laissé »
(« Parfait. » sous `stop_hook_active`) et ajoute : `FAITE — X1.` sous `stop_hook_active`,
case vide → renvoyé, avec « case de X1 est vide » dans la raison.

**Critère de fin**
`py scripts/test-vlp.py` rend `OK`, avec les deux tests ci-dessus. Mutant : remettre
`and not d.get("stop_hook_active")` sur la branche `SubagentStop` fait tomber le nouveau
test (`ÉCART`). pyright : 0 erreur sur `scripts/vlp.py` et `scripts/test-vlp.py`.
<!-- /FICHE -->

---

<!-- FICHE:GAR2 -->
## GAR2 [ ] — Retirer la sonde

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
La sonde de `CON3` a servi ; elle est débranchée et ne sert plus. Retire de `vlp.py` la
constante `SONDE`, `cmd_sonde`, la sous-commande `sonde` (son `add_parser` et sa branche
dans `repartir`) et son paragraphe de la docstring du module. Retire de `test-vlp.py` le
bloc « sonde (chantier CON3) ». Ne touche à rien d'autre : le gardien et le filet restent.

**Critère de fin**
`py scripts/test-vlp.py` rend `OK` ; `py scripts/vlp.py sonde` sort en erreur d'argparse
(`invalid choice`) ; un grep `cmd_sonde|SONDE` sur `scripts/` ne rend rien ; pyright : 0
erreur sur les deux fichiers.
<!-- /FICHE -->

---

<!-- FICHE:GAR3 -->
## GAR3 [ ] — Le prouver sur un témoin

**Dépend de** : `GAR1`.
**Fichiers** : ce fichier de fiches (une fiche témoin ajoutée puis retirée), `context AI/08-etat.md` (journal).

**Prompt**
Se joue **à la main**, par le chef. Le renvoi sur la tête est déjà prouvé en vrai
(`GLO1`, socle) ; reste la séquence que `GAR1` ferme. Ajoute en fin de fichier une fiche
témoin triviale, `GAR9` : écrire une ligne dans un fichier du scratchpad, rien à
commiter ; finir d'abord par « Parfait, c'est fait. » sans statut ; renvoyé, rendre
`FAITE` **sans** lancer `vlp.py cocher`. Joue-la par la skill `vlp:jouer`. Dans sa
transcription, compte les `Stop hook feedback` et recopie leur texte. Retire le témoin et
son fichier. Écris au journal (`## 2026-09-25 — GAR3`) : le premier mot rendu au chef, les
renvois comptés et leur texte, et si la case de `GAR9` a fini cochée.

**Critère de fin**
Au journal : un `Stop hook feedback` sur la tête, **puis** un citant « case de GAR9 est
vide » — le second, sous `stop_hook_active`, est ce que `GAR1` ajoute. Le témoin est
retiré et `valider` rend `VALIDE 3 fiches`.
<!-- /FICHE -->
