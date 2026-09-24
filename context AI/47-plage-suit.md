> **QUAND LIRE** : on joue une fiche `PLA*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache PLA<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier PLA — La plage des fiches suit le fichier

**CLOS** le 2026-09-24. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** PLA1..PLA2 (2026-09-24) : La plage des fiches suit le fichier : l'en-tête de la page et la ligne d'index d'un chantier ouvert suivent le fichier, et /vlp:chantier dit de relancer ouvrir, page et feuille après un redécoupage.

**À quoi il sert.** Une fiche ajoutée après l'ouverture — `CAS2`, la nuit du 2026-09-24 — laisse
deux traces figées : l'en-tête de la page (« fiches CAS1–CAS1 ») et la ligne d'index
(`CAS1..CAS1`), corrigés à la main. `CHANTIER.md` et la feuille de route, eux, suivent déjà le
fichier. Après ce chantier, `page` et `ouvrir` relancés remettent les deux à la plage du fichier,
et `/vlp:chantier` dit de les relancer après un redécoupage.

## Le socle commun

| Nom | Où | Ce qu'il fait ou rend |
|---|---|---|
| `creer` | `scripts/vlp.py:1150` | la page neuve depuis le gabarit ; l'en-tête `<projet> · fiches X1–Xn` (ligne 1156), plage calculée à part (ligne 1153) |
| `regenerer` | `scripts/vlp.py:1171` à `1224` | refait états, avancement, comptage, coûts, journal, date ; ne touche pas l'en-tête. `page` l'appelle après `creer` (ligne 1278), `clore` aussi (ligne 2003) |
| `plage` | `scripts/vlp.py:1429` | `X1–Xn`, ou `X1` seule pour une fiche — la forme de la feuille de route |
| `cmd_ouvrir` | `scripts/vlp.py:2092` ; l'index en `2129` à `2148` ; la sortie en `2175` | n'insère la ligne « on joue une fiche … `X1..Xn` » que si aucune ligne de l'index ne commence par le nom du fichier |
| la garde de `clore` | `scripts/vlp.py:1955` | ne réécrit que la ligne d'index qui porte `**ouvert**` |
| les docstrings | `scripts/vlp.py:51` à `59` (`page`), `132` à `140` (`ouvrir`) | la sortie et ce que chaque commande garde |
| `verifier` | `scripts/test-vlp.py:51` | imprime `ÉCART: <nom>` et sort au **premier** échec ; tout passe : `OK` |
| les tests voisins | `scripts/test-vlp.py:357` (« page --creer »), `418` (« page : blocage masqué une fois cochée »), `817` à `833` (« ouvrir : … ») | à laisser passer, noms gardés |

Chaque fiche écrit ses tests **d'abord**, lance `py scripts/test-vlp.py`, et cite la ligne
`ÉCART:` qu'il sort sur le code d'avant : c'est son mutant (`methode-chantier.md`, « Anatomie
d'une fiche »). Puis elle corrige, et relance : `OK`.

**Mesuré à l'ouverture, le 2026-09-24** (sonde jetable, dans un dossier temporaire).
- Une fiche `Q1`, puis `Q2` ajoutée : `page` rend 0, l'en-tête reste « fiches Q1–Q1 ».
- `ouvrir` relancé sur le même fichier : `OUVERT Q Q1..Q2 · index +0 · routage +0` —
  `CHANTIER.md` passe à `(Q1..Q2)`, la ligne d'index reste `Q1..Q1`. Il ne s'arrête pas sur
  « déjà ouvert » : la garde ne vaut que pour un **autre** fichier.
- Les 35 pages de chantier du dépôt : 34 plages justes, dont `09-enchainer.html` et
  `14-bugs.html` suivies de « · clos », écrit à la main — à garder ; `44-pre-commit.html`
  affiche « VAL1–VAL1 » pour une seule fiche.

**Décidé seul, la nuit du 2026-09-24** (l'utilisateur dormait ; validé au réveil).
- Seule la plage se réécrit — ni le titre, ni ce qui suit la plage : une ligne ou un en-tête
  retouchés à la main gardent le reste.
- `ouvrir` ne rafraîchit que la ligne qu'il a écrite (`**ouvert**`, la garde de `clore`) ; il le
  dit par `index ~1`, distinct de `index +1` (ligne ajoutée).

**Ce qu'on ne fait pas.** La ligne de routage de `CLAUDE.md` ne porte pas de plage : rien à
suivre. La feuille de route relit déjà les fiches du fichier courant (`scripts/vlp.py:1515`).
Les pages des chantiers clos ne se régénèrent pas : « VAL1–VAL1 » se corrige à la main, une fois,
après `PLA1`.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `PLA1` | L'en-tête de la page suit le fichier | rien |
| `PLA2` | `ouvrir` relancé : la plage de l'index suit le fichier | rien |

Les deux sont indépendantes ; jouées en série, pour que les numéros de ligne du socle restent
justes à une vingtaine près.

---

<!-- FICHE:PLA1 -->
## PLA1 [x] — L'en-tête de la page suit le fichier

**Session** : 1ba64929-8274-42d4-93bb-a2d22fbdd600
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (`creer`, `regenerer`, docstring de `page`),
`scripts/test-vlp.py` — et rien d'autre.

**Prompt**
1. Test d'abord, « page : l'en-tête suit la plage du fichier », juste après « page : blocage
   masqué une fois cochée » (`scripts/test-vlp.py:418` à `420`), avant « page absente sans
   --creer » :
   - dans `page`, remplace `Proj · fiches P1–P3` par `Proj · fiches P1–P3 · clos` ;
   - ajoute à `fiches` le bloc `<!-- FICHE:P4 -->\n## P4 [ ] — Ajoutée\n**Critère de fin**\n<!-- /FICHE -->\n`,
     puis lance `page` sur `fiches` et `page` ;
   - écris un fichier `u.md` (dans `t`) à une seule fiche : `# Chantier U\n\n<!-- FICHE:U1 -->\n## U1 [ ] — Seule\n**Critère de fin**\n<!-- /FICHE -->\n`,
     et crée sa page `u.html` par `page … --creer --projet Proj --titre U --resultat R.` ;
   - un seul `verifier` : les deux codes valent 0, `page` contient
     `<div class="eyebrow">Proj · fiches P1–P4 · clos</div>`, et `u.html`
     `<div class="eyebrow">Proj · fiches U1</div>`.
   Lance les tests ; cite la ligne `ÉCART:`.
2. `regenerer` réécrit la plage de l'en-tête depuis les fiches du fichier, par `plage()` : le seul
   jeton `X1–Xn` ou `X1` qui suit ` · fiches ` ; ce qui vient après reste. Sans en-tête de cette
   forme, rien ne change.
3. `creer` perd sa variable `plage` (ligne 1153) : il écrit l'en-tête avec `plage()` lui aussi.
4. La docstring de `page` (ligne 56) le dit : l'en-tête est gardé, sauf sa plage, refaite depuis
   le fichier.
Tu ne commites pas : le chef le fera.

**Critère de fin**
`py scripts/test-vlp.py` rend `OK` ; ton compte rendu cite l'`ÉCART:` de l'étape 1.
<!-- /FICHE -->

<!-- FICHE:PLA2 -->
## PLA2 [x] — `ouvrir` relancé : la plage de l'index suit le fichier

**Session** : 1ba64929-8274-42d4-93bb-a2d22fbdd600
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (`cmd_ouvrir`, docstring de `ouvrir`), `scripts/test-vlp.py`,
`skills/chantier/SKILL.md` — et rien d'autre.

**Prompt**
1. Tests d'abord, juste après « ouvrir : autre chantier ouvert, refus »
   (`scripts/test-vlp.py:832` à `833`), avant la ligne qui remet `CHANTIER.md` à « aucun » :
   - « ouvrir : relancé, la plage de l'index suit le fichier » : `ctx/30-q.md` prend une troisième
     fiche, `## Q3 [ ] — c` ; `ouvrir` relancé sur ce fichier, titre ``Un `titre` `` : code 0, la
     sortie contient `OUVERT Q Q1..Q3 · index ~1 · routage +0` ; l'index a **une seule** ligne qui
     commence par `` | `30-q.md` | ``, égale à
     ``| `30-q.md` | on joue une fiche `Q*` — chantier **ouvert** « Un `titre` », `Q1..Q3` |`` ;
     `CHANTIER.md` contient `ctx/30-q.md (Q1..Q3)` ;
   - « ouvrir : relancé, une ligne d'index écrite à la main reste » : dans l'index, remplace
     ``chantier **ouvert** « Un `titre` », `Q1..Q3` `` par ``à la main `Q1..Q2` `` ; relance le
     même `ouvrir` : code 0, la sortie contient `index +0`, l'index est inchangé.
   Lance les tests ; cite la ligne `ÉCART:`.
2. `cmd_ouvrir` (lignes 2129 à 2148) : si la ligne du fichier existe et porte `**ouvert**`, son
   dernier jeton entre backticks — la plage — devient `fait`. Si la ligne change, elle s'écrit et
   la sortie dit `index ~1` ; sinon `index +0`. L'insertion reste `index +1`.
3. La docstring de `ouvrir` (lignes 132 à 140) le dit, format de sortie compris.
4. `skills/chantier/SKILL.md`, étape 0 ter, juste avant « **Si c'est « clore tel quel »** » :
   un paragraphe — « **Si c'est « redécouper »**, réécris les fiches restantes dans le même
   fichier, puis relance `ouvrir` sur ce fichier, `page` et `feuille` : la plage suit le fichier
   dans `CHANTIER.md`, l'index, la page et la feuille de route. Republie la page et la feuille. »
   — suivi du bloc `bash` de ces trois appels, écrits comme ceux des lignes 220 et 238.
Tu ne commites pas : le chef le fera.

**Critère de fin**
`py scripts/test-vlp.py` rend `OK` ; ton compte rendu cite l'`ÉCART:` de l'étape 1.
<!-- /FICHE -->
