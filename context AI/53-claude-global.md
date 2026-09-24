> **QUAND LIRE** : on joue une fiche `GLO*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache GLO<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier GLO — Le CLAUDE.md de l'utilisateur dans le sous-agent

**À quoi il sert.** Les sous-agents `vlp:fiche` et `vlp:relecture` reçoivent les
`CLAUDE.md` de l'utilisateur et du projet, et sa mémoire (TODO n° 44). GLO mesure ce
qu'ils pèsent et s'ils poussent à la forme (« En résumé », jauge) ; n'agit que si ça coûte.

**Fait.** Rien. Ouvert le 2026-09-25, cadré en 3 fiches, `GLO1` à jouer. Cadré seul :
l'utilisateur dormait ; les 🟡 tranchés ici sont à valider au réveil.

**Session** : ca431cf8-167e-4c10-8bce-210c5f48a675

## Le socle commun

| Fait vérifié | Où |
|---|---|
| une transcription porte une entrée `{"type":"attachment","attachment":{"type":"instructions","files":[…]}}` ; chaque fichier a `path`, `type`, `content` | sondé le 2026-09-25 sur 101 transcriptions `vlp:fiche` + `vlp:relecture` |
| `type` d'un fichier d'instructions : `User` (`~/.claude/CLAUDE.md`), `Project` (le `CLAUDE.md` du projet), `AutoMem` (le `MEMORY.md` de la mémoire) | même sonde : 98 `User`, 81 `Project`, 81 `AutoMem` |
| `lire_contrat`, `type_agent`, `cmd_contrat`, `STATUTS` | `scripts/vlp.py`, section « contrat (chantier CON) » |
| `mesure()` donne `mesure-tokens.py` : `ouvrir`, `depart`, `borne`, `SOUS_AGENTS` | `scripts/vlp.py`, `def mesure` |
| prix Haiku 4.5, $/MTok : entrée 1, sortie 5, lecture de cache 0,1, écriture 1,25 (5 min) ou 2 (1 h) | `scripts/mesure-tokens.py`, table `PRIX` |
| la jauge : cinq libellés — « Tout va bien », « Ça tient, mais », « Imprévu », « Pas bon », « Grosse erreur » | `~/.claude/CLAUDE.md`, « Fin de tâche » |
| tests : `py scripts/test-vlp.py` ; une fiche de code nomme son mutant | `methode-chantier.md`, « Anatomie d'une fiche » |

Décidé au cadrage, seul : le seuil d'action est **5 %** — si le `CLAUDE.md`
utilisateur coûte plus de 5 % d'un sous-agent, ou si plus d'un sous-agent récent
sur dix porte la forme, `GLO3` agit ; sinon elle écrit « rien à faire » et se coche.

**Dehors.** Retirer le `CLAUDE.md` du sous-agent par un réglage : la liste des champs
de frontmatter de https://code.claude.com/docs/en/sub-agents.md n'en porte aucun
(lue le 2026-09-25 par un agent `claude-code-guide` — résumé, pas mot pour mot). Toucher
`~/.claude/CLAUDE.md` : jamais — c'est le fichier privé de l'utilisateur.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `GLO1` | Lire la forme et le poids dans une transcription | rien |
| `GLO2` | Mesurer sur tous les sous-agents | `GLO1` |
| `GLO3` | Agir, ou écrire qu'il n'y a rien à faire | `GLO2` |

Rien n'est parallélisable : chaque fiche lit ce que la précédente a écrit.

---

<!-- FICHE:GLO1 -->
## GLO1 [x] — Lire la forme et le poids dans une transcription

**Session** : ca431cf8-167e-4c10-8bce-210c5f48a675
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Ajoute à `vlp.py` la sous-commande `forme [<transcription>…] [--depuis D]`, à côté
de `contrat` et sur le même modèle (réutilise `type_agent`, `mesure().ouvrir`,
`borne`, `depart` ; ne les recopie pas). Sans argument : les transcriptions dont
l'`agentType` vaut `vlp:fiche` ou `vlp:relecture`. Une ligne par transcription :
`<id> <type> <heure> user <c> projet <c> memoire <c> resume <0|1> jauge <0|1> tete <0|1>`,
où `<c>` est le nombre de caractères du `content` des fichiers d'instructions de
ce `type` (`User`, `Project`, `AutoMem`, somme si plusieurs, 0 si aucun) ;
`resume` vaut 1 si le dernier message texte contient « En résumé » ; `jauge` 1
s'il contient l'un des cinq libellés du socle ; `tete` 1 s'il commence par un
mot de `STATUTS`. Puis le bilan :
`FORME <n> sous-agents · user <moyenne> car. · resume <k> · jauge <k> · tete <k>`.
Mets-la dans la docstring du module, à côté de `contrat`.

**Critère de fin**
`py scripts/test-vlp.py` passe, avec un test sur deux transcriptions fabriquées :
une qui porte un `User` de 100 caractères et finit par « FAITE — … En résumé … Tout
va bien », une sans instructions qui finit par « Parfait ». Le bilan attendu est
`FORME 2 sous-agents · user 50 car. · resume 1 · jauge 1 · tete 1`. Mutant :
ne plus sommer le `type` `User` (le laisser à 0) fait tomber ce test.
<!-- /FICHE -->

---

<!-- FICHE:GLO2 -->
## GLO2 [x] — Mesurer sur tous les sous-agents

**Session** : ca431cf8-167e-4c10-8bce-210c5f48a675
**Dépend de** : `GLO1`.
**Fichiers** : `context AI/08-etat.md` (journal, en fin de fichier) — et rien d'autre.

**Prompt**
Lance `vlp.py forme` sans argument, puis `vlp.py forme --depuis 2026-09-24T00:07:40Z`
(le commit `f98ceec`, « aucun commit » entré dans `agents/fiche.md`). Garde les deux
bilans bruts. Puis calcule le poids du `CLAUDE.md` utilisateur, en borne haute :
tokens ≤ caractères ÷ 2 ; coût par sous-agent ≤ tokens × (1,25 + 30 × 0,1) ÷ 10⁶ $
(une écriture de cache, trente lectures, prix Haiku du socle). Compare à 0,176 $,
le prix d'une fiche triviale (mémoire du kit, `feedback_economie_tokens`) : donne le
pourcentage. Fais le même calcul pour `projet` et `memoire`.
Écris au journal, en fin de `context AI/08-etat.md`, une entrée datée du jour
(`## 2026-09-25 — GLO2`) : les deux commandes, leurs bilans bruts, les trois
calculs posés en entier, et le verdict selon le seuil du socle — « agir » ou
« rien à faire », en nommant la quantité qui le fonde.

**Critère de fin**
L'entrée du journal existe, cite les deux lignes `FORME` telles que la commande les
rend, pose les trois calculs avec leurs nombres, et finit par un verdict qui nomme
la quantité comparée au seuil de 5 %.
<!-- /FICHE -->

---

<!-- FICHE:GLO3 -->
## GLO3 [ ] — Agir, ou écrire qu'il n'y a rien à faire

**Dépend de** : `GLO2`.
**Fichiers** : `agents/fiche.md`, `agents/relecture.md`, `context AI/08-etat.md` (journal) — et rien d'autre.

**Prompt**
Lis le verdict de `GLO2` au journal (`## 2026-09-25 — GLO2`).
S'il dit « rien à faire » : ajoute sous cette entrée une ligne « GLO3 : rien à faire,
<la quantité et son seuil> », et coche.
S'il dit « agir » : ajoute **une** phrase à `agents/fiche.md` et **une** à
`agents/relecture.md`, là où chacun décrit son dernier message : les règles de
forme d'un `CLAUDE.md` — résumé, jauge, émojis, message à part — visent l'humain de
la session principale ; ton lecteur est le chef, ton compte rendu n'en porte
aucune. Puis écris au journal la phrase ajoutée et son emplacement
(`fichier:ligne`), et que la preuve viendra au prochain `/vlp:enchainer` d'une
session neuve : une définition d'agent se charge au démarrage.

**Critère de fin**
Selon le verdict : la ligne « GLO3 : rien à faire » au journal ; ou `Read` montre la
phrase dans les deux agents, et `py scripts/vlp.py valider "context AI/53-claude-global.md"`
rend `VALIDE`.
<!-- /FICHE -->
