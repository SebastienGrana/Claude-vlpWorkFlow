> **QUAND LIRE** : on joue une fiche `N*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache N<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier N — `/vlp:enchainer` : réparer ou retirer

**À quoi il sert.** Le chef de `/vlp:enchainer` relit tout son contexte à chaque appel : il coûte plus que
les fiches jouées à la main. On mesure la skill forkée, puis on répare ou on retire — aux chiffres.

**Fait.** Rien. Ouvert le 2026-09-17, cadré en 3 fiches, `N1` à jouer.

## Le socle commun

**Ce qui existe** (lu au cadrage, le 2026-09-17) :

| Fichier | Lignes | Ce qu'il porte |
|---|---|---|
| `skills/enchainer/SKILL.md` | 145 | le chef : carte, `valider`, `socle`, puis par fiche `extraire` + `Agent` `vlp:fiche`, bilan, page |
| `agents/fiche.md` | 35 | `model: haiku`, `effort: low`, `maxTurns: 8`, `tools: Read, Edit, Write, Bash` |
| `enchainement.md` | 14 | le contrat : premier mot `FAITE`, `RETOUR` ou `BLOQUÉE` |

**Mesures connues** (`context AI/08-etat.md`, journal) : chef à ~70 k de socle et ~12 appels par fiche (E,
2026-09-10) ; sous-agent 13 à 16 k par fiche ; `maxTurns: 8` a coupé D1 trois fois, V1 quatre fois.

**Le levier** : une skill à `context: fork` + `agent: vlp:fiche` tourne dans un sous-agent ; la session
principale n'en reçoit que le compte rendu. Doc : https://code.claude.com/docs/en/skills — à relire en N1,
rien n'est supposé. **Seuil de décision (TODO n° 9)** : chef ≤ 3 tours par fiche → réparer ; sinon retirer.

**La sonde** — jamais dans le kit :
- bac à sable dans le scratchpad de la session, avec son `CHANTIER.md` et un fichier de fiches factice ;
- `claude` n'est pas dans le PATH : `%APPDATA%/Claude/claude-code/2.1.271/claude.exe` ;
- lancement headless `claude -p … --output-format json` depuis le bac à sable ; coût = `total_cost_usd`,
  tours = `scripts/mesure-tokens.py <session_id>` (sous-agents compris) ;
- **plafond : 1 $ et deux lancements** pour tout N1 ; au-delà, arrêt et chiffres montrés.

**Renvois à `enchainer`, `fiche` ou `enchainement`** (grep du cadrage, hors `context AI/`) :
`README.md` 30, 77, 127, 129, 136 · `CLAUDE.md` 12, 64 · `methode-chantier.md` 42, 48, 76, 79, 80,
93, 186 · `ARTEFACTS.md` 16, 17, 112 · `cloture.md` 3 · `scripts/vlp.py` 300 ·
`skills/tache/references/tache-blocage.md` 1, `tache-page.md` 1. Recompter par
`grep -rn "enchain\|vlp:fiche" --include=*.md --include=*.py --include=*.json . | grep -v "context AI/"`.

**Outils de preuve** : `vlp.py renvois` (0 absent), `claude plugin validate .` (1 avertissement voulu :
`CLAUDE.md` à la racine), evals Windows lancées **toujours ainsi** (`context AI/18-evals.md`) :
`claude plugin eval . --tag check --tag init --tag hook --runs 1 --ablation none --no-publish --scaffold
--allow-tools Write Edit --trust-plugin --max-cost-usd 1.5 -j 3` ; tours et coût dans `aggregate-result.json`.

**Dehors** : WSL2 (TODO n° 11) ; le coût de `/vlp:tache` ; la marque `(visuel)`, gardée quoi qu'il arrive —
elle sert aussi à qui lit une fiche. Pas de `disable-model-invocation` (écarté en K1).

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `N1` | Mesurer une fiche jouée par une skill forkée | rien |
| `N2` | Réparer ou retirer `/vlp:enchainer`, aux chiffres de N1 | `N1` |
| `N3` | Aligner la doc, la version et les evals | `N2` |

Rien n'est parallélisable : chaque fiche lit la décision de la précédente.

---

<!-- FICHE:N1 -->
## N1 [x] — Mesurer une fiche jouée par une skill forkée

**Dépend de** : rien.
**Fichiers** : un bac à sable dans le scratchpad ; `agents/fiche.md` et `enchainement.md` en lecture.

**Prompt**
Relis la section `context: fork` et `agent:` de la doc des skills (URL du socle) : ce que reçoit le
sous-agent, si `$ARGUMENTS` et `` !`…` `` y passent, ce que la session principale reçoit en retour.
Pose un bac à sable : `CHANTIER.md` minimal, un fichier de fiches à deux fiches triviales (écrire un
fichier, cocher la case), et une skill de projet `.claude/skills/sonde/SKILL.md` en `context: fork` +
`agent: vlp:fiche`, qui transmet la fiche reçue en argument. Lance depuis le bac à sable, en headless,
un prompt qui joue les deux fiches par la sonde. Relève : tours et appels de la session principale,
tours et tokens du sous-agent, coût, fiches cochées, statut rendu. Plafond du socle : si le premier
lancement échoue pour une raison d'outillage (skill non vue, permission), corrige une fois, puis arrête.
Écris les comptes bruts dans le journal de `context AI/08-etat.md` (une ligne datée).

**Critère de fin**
Une ligne du journal donne, pour le lancement retenu : tours du chef par fiche, tours et tokens du
sous-agent, fiches cochées sur 2, coût total ≤ 1 $ — ou dit pourquoi la sonde n'a pas pu tourner.
<!-- /FICHE -->

---

<!-- FICHE:N2 -->
## N2 [ ] — Réparer ou retirer `/vlp:enchainer`, aux chiffres de N1

**Dépend de** : `N1`.
**Fichiers** : `skills/enchainer/SKILL.md`, `agents/fiche.md`, `enchainement.md`, `.claude-plugin/plugin.json`.

**Prompt**
Relis la ligne N1 du journal. Chef ≤ 3 tours par fiche et 2 fiches cochées sur 2 : **réparer** —
réécris `skills/enchainer/SKILL.md` pour qu'il joue chaque fiche par la skill forkée au lieu d'un
`Agent`, sans recopier `tache` ni `cloture.md`, et règle `maxTurns` de `agents/fiche.md` au vu des
tours mesurés. Sinon : **retirer** — supprime `skills/enchainer/`, `agents/fiche.md` et
`enchainement.md`. Dans les deux cas, écris la décision et ses chiffres dans le journal, et passe
le plugin en 3.3.0. Ne touche pas encore aux renvois de la doc : c'est N3.

**Critère de fin**
`claude plugin validate .` ne rend que l'avertissement voulu ; `wc -l` des fichiers touchés avant →
après, et la ligne de décision du journal cite le seuil et le chiffre de N1.
<!-- /FICHE -->

---

<!-- FICHE:N3 -->
## N3 [ ] — Aligner la doc, la version et les evals

**Dépend de** : `N2`.
**Fichiers** : les renvois listés au socle, `context AI/08-etat.md` (TODO n° 9), `CLAUDE.md`.

**Prompt**
Recompte les renvois par le grep du socle. Mets chaque renvoi d'accord avec la décision de N2 :
réparé, la doc dit comment `/vlp:enchainer` joue une fiche ; retiré, les renvois disparaissent (cinq
commandes → quatre, et plus d'agent). Ne recopie aucun chiffre : pointe vers le journal. Lance
`vlp.py renvois` et `vlp.py valider` sur ce fichier, puis les evals Windows, lancées comme le socle le
dit. Retire la ligne n° 9 de la TODO seulement à la clôture (`cloture.md`), pas ici.

**Critère de fin**
Grep des renvois avant → après, 0 renvoi mort ; `vlp.py renvois` 0 absent ; evals Windows 3/3, avec
tours et coût lus dans `aggregate-result.json`.
<!-- /FICHE -->
