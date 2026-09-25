> **QUAND LIRE** : on joue une fiche `ESS*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache ESS<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier ESS — Les essais `claude -p` dans le coût

**À quoi il sert.** Un essai `claude -p` tourne dans une autre session, que `vlp.py cout` ne
voit pas : ≈ 12,32 $ sur 14 chantiers clos, notés « hors total » à la main (TODO n° 47).

**Fait.** Rien. Ouvert le 2026-09-25, cadré en 4 fiches, `ESS1` à jouer.

**Session** : 2d0c4c56-7dba-4f2c-9091-7f8e63857158

## Le socle commun

**Le fait qui porte le chantier** (constaté au cadrage, `ls ~/.claude/projects`) : un essai
lancé depuis un bac du scratchpad laisse son transcript dans un dossier nommé
`<projet encodé>-<id de la session parente>-scratchpad-<bac>/<id essai>.jsonl`.
➡️ Le **dossier** relie l'essai à sa session parente ; son **heure** le range dans sa fiche.

| Symbole | Où | Ce qu'il rend |
|---|---|---|
| `sessions_de(lignes)` | `scripts/vlp.py:464` | les ids des lignes `Session` du fichier de fiches |
| `cmd_cout` | `scripts/vlp.py:511` | la sortie de `cout` : une ligne par fiche, `hors fiches`, `TOTAL` |
| `decouper` / `totaux` | `scripts/vlp.py:549`, `:564` | la découpe, et sa somme — `recompter` les relit |
| `parts_aux_commits` | `scripts/vlp.py:1652` | chaque transcript `(chemin, sorte)` mesuré par plage ; sorte 0 session, 1 sous-agent |
| `ligne_parts` / `plus` | `scripts/vlp.py:1706`, `:1700` | une ligne `<nom> · <somme> = session … + n sous-agents …` |
| `m.resoudre`, `m.mesurer`, `m.sous_agents` | `scripts/mesure-tokens.py` (via `mesure()`) | chemin d'une session ; ses tours dans une plage ; ses sous-agents |
| `cmd_recompter` | `scripts/vlp.py:2303` | chaque clos recompté par `cout`, sans rien écrire |

**Décidé au cadrage** (2026-09-25) :
- un essai se relie **par le dossier puis l'heure** — aucune trace à écrire dans la fiche ;
- il compte **dans le prix de sa fiche**, et une part `essais` le montre à côté ; `TOTAL` l'inclut ;
- un essai compte comme une session : ses propres sous-agents s'y ajoutent.

**Dehors** : les evals `claude plugin eval` (décision du cadrage) ; un bac hors du scratchpad,
qui ne porte pas l'id parent — ESS1 dit combien il y en a, il ne les rattrape pas ; la
republication des bilans et de la feuille de route (ESS4 compare, n'écrit pas).

Tests : `py scripts/test-vlp.py` ; `pyright` sur `scripts/vlp.py`, compte avant et après.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `ESS1` | Mesurer les bacs contre les essais notés | rien |
| `ESS2` | Trouver les essais d'une session | `ESS1` |
| `ESS3` | Compter les essais dans `cout` | `ESS2` |
| `ESS4` | Recompter les chantiers clos | `ESS3` |

Rien n'est parallélisable : chaque fiche lit ce que la précédente établit.

---

<!-- FICHE:ESS1 -->
## ESS1 [x] — Mesurer les bacs contre les essais notés

**Session** : f11bd1c7-b0df-49c4-8d78-4e609513bec3
**Dépend de** : rien.
**Fichiers** : `context AI/08-etat.md`, `context AI/30-ouvrir.md`, `context AI/40-cout-juste.md`,
`context AI/artefacts/feuille-de-route.html` (grep `hors total` seulement) ; `~/.claude/projects/`.

**Prompt**
Avant d'écrire du code, vérifie que le fait du socle tient. Script jetable dans le scratchpad,
rien dans `scripts/`. Pour chaque dossier `~/.claude/projects/*-scratchpad-*` : l'id parent tiré
du nom, le nombre de `.jsonl`, l'heure du premier tour. Puis relève chaque essai noté
« hors total » à la main (chantier, montant). Croise les deux : quel essai noté a son dossier,
lequel n'en a pas, et quel dossier ne correspond à aucune note. Regarde aussi si un essai lancé
par un sous-agent `vlp:fiche` porte l'id de la session du chef. Écris la table dans
`context AI/08-etat.md`, journal, une ligne datée par écart imprévu.

**Critère de fin**
Une table *essais notés → dossier trouvé / absent*, en comptes bruts (N notés, N trouvés,
N absents, N dossiers sans note) et la somme en $ de chaque colonne, à côté du ≈ 12,32 $ de la
TODO. Si plus d'un essai noté sur quatre n'a pas de dossier : s'arrêter, le mécanisme est à revoir.
<!-- /FICHE -->

---

<!-- FICHE:ESS2 -->
## ESS2 [x] — Trouver les essais d'une session

**Session** : f11bd1c7-b0df-49c4-8d78-4e609513bec3
**Dépend de** : `ESS1`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`.

**Prompt**
Écris dans `scripts/vlp.py` une fonction `essais_de(session)` : les chemins des transcripts
`~/.claude/projects/*-<session>-scratchpad-*/*.jsonl`, triés, sans doublon. `glob.escape` sur
l'id. Sans dossier : liste vide, pas d'erreur. Si ESS1 a trouvé une autre forme de nom, suis
ESS1. Pas encore de branchement dans `cout`. Ajoute son test dans `scripts/test-vlp.py`, sur
un faux `~/.claude/projects` en dossier temporaire (même procédé que les tests existants) :
deux bacs de la session A, un de la session B, un dossier sans `scratchpad`.

**Critère de fin**
`py scripts/test-vlp.py` passe, compte de tests avant/après affiché ; le test attend 2 chemins
pour A, 1 pour B, 0 pour une session inconnue. **Mutant** : le motif sans `-scratchpad-`
(il prend le dossier intrus) fait tomber le test. `pyright scripts/vlp.py` : pas une erreur de plus.
<!-- /FICHE -->

---

<!-- FICHE:ESS3 -->
## ESS3 [x] — Compter les essais dans `cout`

**Session** : f11bd1c7-b0df-49c4-8d78-4e609513bec3
**Dépend de** : `ESS2`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`.

**Prompt**
Dans `parts_aux_commits`, ajoute pour chaque session ses essais (`essais_de`) comme une sorte
2, chacun avec ses propres sous-agents : ils sont mesurés sur les mêmes plages que les
sessions. Une part devient (session, sous-agents, essais). Suis ce changement chez tous les
appelants — `grep -n "parts_aux_commits\|totaux(\|ligne_parts(" scripts/vlp.py` d'abord :
`totaux`, `ligne_parts`, `couts_aux_commits`, `cmd_recompter`, la page. `ligne_parts` écrit
`+ N essais <coût>` quand il y en a, rien sinon : une sortie sans essai ne change pas d'un octet.

**Critère de fin**
Un test dans `scripts/test-vlp.py` : une session à 1 essai dans la plage d'une fiche et 1 hors
plage → la fiche compte l'un, `hors fiches` l'autre, `TOTAL` les deux. **Mutant** : ne plus
ajouter la sorte 2 fait tomber le test. `py scripts/vlp.py cout "context AI/60-recompter.md"`
avant/après : sortie identique si REC n'a aucun essai, sinon l'écart affiché.
<!-- /FICHE -->

---

<!-- FICHE:ESS4 -->
## ESS4 [x] — Recompter les chantiers clos

**Session** : 770f94ec-a301-4b84-b75f-900295865046
**Dépend de** : `ESS3`.
**Fichiers** : `context AI/08-etat.md` (la table d'ESS1), `scripts/vlp.py`.

**Prompt**
Lance `py scripts/vlp.py recompter .`, sans `--ecrire`. Pour chaque chantier que la table
d'ESS1 porte, mets côte à côte : le montant noté à la main, la part `essais` que `cout` trouve
désormais, l'écart. Range chaque écart par cause (dossier absent, essai hors plage, sous-agent
de l'essai, arrondi), en comptes bruts. N'écris ni bilan ni feuille de route : c'est hors du
chantier. Écris la table au journal de `context AI/08-etat.md`, et une ligne TODO si les
bilans méritent d'être republiés.

**Critère de fin**
Une table *chantier → noté à la main / trouvé par `cout` / écart / cause*, sa somme à côté du
≈ 12,32 $ de la TODO, et le nombre de chantiers dont l'écart dépasse 0,05 $.
<!-- /FICHE -->
