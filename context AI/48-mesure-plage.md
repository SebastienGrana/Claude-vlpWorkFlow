> **QUAND LIRE** : on joue une fiche `MTK*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache MTK<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier MTK — mesure-tokens.py se lit et se borne en ligne de commande

**CLOS** le 2026-09-24. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** MTK1..MTK2 (2026-09-24) : mesure-tokens.py se borne en ligne de commande : --plage DEBUT FIN, heures ISO ou commits Git, une borne illisible sort 1 ; une docstring dit la syntaxe ; la phrase périmée de 34-agent-sans-git.md est marquée d'un renvoi vers CPT2.

**À quoi il sert.** `mesure-tokens.py` n'a pas de docstring : le socle de `SAG` y renvoyait
pour la syntaxe, il n'y a trouvé qu'une ligne `usage`. Sa ligne de commande n'expose pas la plage
que `mesurer()` accepte : la reprise de `SAG3` s'est mesurée par un `py -c` d'une ligne entière
(`08-etat.md:477`). Après ce chantier, `--plage DEBUT FIN` borne la mesure — heures ou commits —,
la docstring dit la syntaxe, et la ligne périmée de `34-agent-sans-git.md` est marquée (TODO 40
et 41, `MTK` et `PER`).

## Le socle commun

| Nom | Où | Ce qu'il fait ou rend |
|---|---|---|
| `main` | `scripts/mesure-tokens.py:316` à `386` | lit chaque argument comme fichier ou id de session (`resoudre`, ligne 61), mesure la session puis ses sous-agents (`sous_agents`, ligne 82) ; la ligne `usage` en `321` |
| `mesurer(chemin, plage=None)` | `scripts/mesure-tokens.py:182` | plage `(debut, fin]` en secondes UTC : un tour se juge à sa première ligne, un sous-agent compte entier à son départ (`depart`, ligne 122) |
| `COLONNES` | `scripts/mesure-tokens.py:12` | les colonnes de la sortie, séparées par des tabulations, après le nom du fichier |
| les tests | `scripts/test-mesure-tokens.py` : `iso`, `sec` (lignes 138, 142), `LIGNES_PLAGE` et `CAS_PLAGE` (146 à 170), `home` (206), `verifier_sous_agents` (255), `main` (311) | chaque bloc rend `None` ou le texte de l'écart ; `main` imprime le premier et sort 1, sinon `OK` |
| la ligne périmée | `context AI/34-agent-sans-git.md:56` à `57` | « `mesure-tokens.py` ne compte pas les sous-agents : pour eux, seul `total_cost_usd` du run `-p` fait foi. » |
| la règle | `methode-chantier.md:39` | un énoncé renversé se garde, marqué d'un renvoi daté vers ce qui le renverse, et par quoi |
| `CPT2` | `context AI/40-cout-juste.md:130` | le 2026-09-23 : `mesure-tokens.py` compte les sous-agents d'une session, sur une plage de temps |

Une fiche de code écrit ses tests **d'abord**, les lance, et cite l'écart qu'ils impriment sur le
code d'avant : c'est son mutant (`methode-chantier.md`, « Anatomie d'une fiche »). Puis elle
corrige, et relance : `OK`.

**Mesuré à l'ouverture, le 2026-09-24.**
- `py scripts/mesure-tokens.py --plage 2026-09-24T04:00:00+02:00 2026-09-24T04:13:00+02:00 <session>` :
  trois lignes `id introuvable` sur stderr — `--plage` et ses deux bornes lus comme des ids —,
  puis la session **entière** mesurée, code 0. L'échec est muet.
- `ast.get_docstring` du fichier : `None`.

**Décidé seul, la nuit du 2026-09-24** (l'utilisateur dormait ; validé au réveil).
- Une option, deux valeurs : `--plage DEBUT FIN`, comme la paire de `mesurer`.
- Une borne est une heure ISO 8601 — sans décalage, l'heure locale — ou un commit Git, pris à son
  heure de commit dans le dossier courant.
- `PER` (TODO 41) entre ici : une phrase à marquer, sur le même outil.

**Ce qu'on ne fait pas.** Pas de borne ouverte (`--depuis` seul) ni de syntaxe `A..B`. `vlp.py
cout` coupe déjà aux commits : il ne change pas. Les `divergents` des sous-agents, vus dans la
sonde, sont connus et bénins (`08-etat.md:560`).

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `MTK1` | La plage en ligne de commande | rien |
| `MTK2` | Une docstring, et la ligne périmée marquée | `MTK1` — la docstring dit sa syntaxe |

---

<!-- FICHE:MTK1 -->
## MTK1 [x] — La plage en ligne de commande

**Session** : 1ba64929-8274-42d4-93bb-a2d22fbdd600
**Dépend de** : rien.
**Fichiers** : `scripts/mesure-tokens.py` (`main`, une fonction `borne`),
`scripts/test-mesure-tokens.py` — et rien d'autre.

**Prompt**
1. Tests d'abord : un bloc `verifier_plage_cli()`, appelé par `main` après
   `verifier_chemin_long`. Dans un faux dossier personnel (`home(tmp)`), il écrit `LIGNES_PLAGE`
   comme session `sess-p.jsonl`, puis vérifie :
   - `mod.main(["--plage", iso(-60), iso(15), "sess-p"])` : code 0, et la ligne de
     `sess-p.jsonl` porte `tours` 3 et `total` 2022 — le cas « plage-avant » ;
   - la même ligne, bornes écrites en heure locale sans décalage :
     `(ORIGINE + datetime.timedelta(minutes=m)).astimezone().replace(tzinfo=None).isoformat()`,
     pour `m` = -60 et 15 ;
   - la même ligne, bornes en commits : un dépôt Git créé dans `tmp`, deux commits vides datés
     `iso(-60)` puis `iso(15)` (`GIT_AUTHOR_DATE`, `GIT_COMMITTER_DATE`), le dossier courant
     placé dans ce dépôt le temps de l'appel : `mod.main(["--plage", "HEAD~1", "HEAD", "sess-p"])` ;
   - `mod.main(["--plage", "ni-heure-ni-commit", iso(15), "sess-p"])` : code 1, et stderr
     nomme `ni-heure-ni-commit` ;
   - `mod.main(["--plage", iso(0)])` : code 1.
   Le texte d'écart nomme le cas qui tombe. Lance `py scripts/test-mesure-tokens.py` ; cite
   l'écart qu'il imprime.
2. `borne(texte)` rend `(secondes, None)` ou `(None, erreur)` : une heure ISO 8601
   (`datetime.fromisoformat` ; sans décalage, l'heure locale), sinon un commit Git
   (`git log -1 --format=%ct <texte>`, dans le dossier courant).
3. `main` prend `--plage DEBUT FIN` où qu'il soit dans les arguments, et passe la paire à
   `mesurer` pour chaque fichier, session et sous-agents. Une borne qui n'est ni l'un ni l'autre :
   son texte sur stderr, code 1, rien de mesuré. `--plage` sans deux valeurs : la ligne `usage`,
   code 1. La ligne `usage` (ligne 321) nomme `--plage DEBUT FIN`.
Tu ne commites pas : le chef le fera.

**Critère de fin**
`py scripts/test-mesure-tokens.py` et `py scripts/test-vlp.py` rendent `OK` ; ton compte rendu
cite l'écart de l'étape 1.
<!-- /FICHE -->

<!-- FICHE:MTK2 -->
## MTK2 [x] — Une docstring, et la ligne périmée marquée

**Session** : 1ba64929-8274-42d4-93bb-a2d22fbdd600
**Dépend de** : `MTK1`.
**Fichiers** : `scripts/mesure-tokens.py` (la docstring seule), `context AI/34-agent-sans-git.md`
— et rien d'autre.

**Prompt**
1. `scripts/mesure-tokens.py` prend une docstring de module, juste après la ligne `#!`, avant
   les imports, en vingt lignes au plus : ce qu'il mesure (les colonnes de `COLONNES`) ; ses deux
   syntaxes, `mesure-tokens.py [--plage DEBUT FIN] <fichier.jsonl | id de session> [...]` et
   `mesure-tokens.py --grille` ; ce qu'amène une session (ses sous-agents, une ligne chacun sous
   la sienne ; un fichier passé deux fois compte une fois) ; la plage (`(DEBUT, FIN]`, heure ISO
   ou commit ; un tour jugé à sa première ligne, un sous-agent entier à son départ) ; la sortie
   (tabulations, une ligne `TOTAL` au-delà d'un fichier, puis les lignes `appels` ; les remarques
   sur stderr) ; le code de sortie. Python 3 sans dépendance, zéro appel modèle.
2. `context AI/34-agent-sans-git.md:56` à `57` : la phrase reste. Juste après elle, son
   marquage, en italique : `*(Renversé le 2026-09-23 par CPT2 : …)*` — ce que `mesure-tokens.py`
   compte depuis, et où le lire (`40-cout-juste.md`, `CPT2`).
Tu ne commites pas : le chef le fera.

**Critère de fin**
`py -c "import ast;print(ast.get_docstring(ast.parse(open('scripts/mesure-tokens.py',encoding='utf-8').read())) is not None)"`
imprime `True` ; `py scripts/test-mesure-tokens.py` et `py scripts/test-vlp.py` rendent `OK` ;
`grep -c "Renversé le 2026-09-23" "context AI/34-agent-sans-git.md"` rend 1.
<!-- /FICHE -->
