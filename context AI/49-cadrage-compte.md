> **QUAND LIRE** : on joue une fiche `CAD*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache CAD<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier CAD — Le cadrage compte dans le coût du chantier

**À quoi il sert.** Seul `cocher` pose une ligne `**Session**`, dans la fiche qu'il coche. Un
cadrage joué dans sa session, puis `/clear` (« une tâche, une session »), n'est donc mesuré nulle
part : `cout` et la page ne lisent que les sessions des fiches. Il pèse : celui de `VAL`, mesuré
par plage, fait 2 087 345 tokens · 7 tours, pour une fiche à 3 368 752 · 40 tours
(`45-cout-aux-bords.md:34` et `37`). Après ce chantier, `ouvrir` — que `/vlp:chantier` lance dans
la session du cadrage — note cette session en tête du fichier de fiches, et la découpe la mesure
comme les autres : ses tours d'avant l'ouverture vont dans « hors fiches » (TODO 50, `CAD`).

## Le socle commun

| Nom | Où | Ce qu'il fait ou rend |
|---|---|---|
| `cmd_ouvrir` | `scripts/vlp.py:2098` à `2191` | écrit `CHANTIER.md`, l'index et le routage, tout calculé avant la première écriture (la liste `ecritures`) ; sa ligne `OUVERT` en `2189` |
| `SESSION`, `sessions_de` | `scripts/vlp.py:159`, `345` | le motif `**Session** : <id>`, et les ids des lignes qui le portent, dédoublonnés |
| `TITRE` | `scripts/vlp.py:155` | un titre de fiche, `## X1 …` — `## Le socle commun` n'en est pas un |
| `cmd_cocher` | `scripts/vlp.py:451` | pose `**Session** : <id>` dans la fiche cochée, l'id tiré de `CLAUDE_CODE_SESSION_ID` s'il n'est pas vide (ligne 477) |
| `parts_aux_commits` | `scripts/vlp.py:1015` | mesure chaque session **des fiches** (lignes 1024-1025) et ses sous-agents sur les plages de `plages` (ligne 981) : une par fiche, puis hors fiches — de l'origine à l'ouverture, et de la dernière fiche à la clôture |
| ses appelants | `cmd_cout` (`scripts/vlp.py:385`, l'appel en 409) ; `regenerer` (1173), par `couts` (1085) puis `couts_aux_commits` (1072) | la découpe de `cout`, et celle de la page |
| la docstring | `scripts/vlp.py:25` (`cout`), `51` (`page`), `133` (`ouvrir`) | la syntaxe et la sortie de chaque sous-commande |
| les tests | `scripts/test-vlp.py` : `transcript` (271) ; `QFICHES` et la découpe (442 à 580 — les commits en 487, la page en 499, `cout` en 533) ; le bloc `ouvrir` (823 à 869) | `verifier(nom, condition, détail)` ; la suite s'arrête au premier écart et l'imprime |

Une fiche de code écrit ses tests **d'abord**, les lance, et cite l'écart qu'ils impriment sur le
code d'avant : c'est son mutant (`methode-chantier.md`, « Anatomie d'une fiche »). Puis elle
corrige, et relance : `OK`.

**Mesuré à l'ouverture, le 2026-09-24.** Une sonde reprend la découpe des tests : la session des
fiches, et une session de cadrage à part — deux tours avant « Chantier Q ouvert », un après la
clôture.
- `cout`, la session de cadrage en tête du fichier : `hors fiches · ≈200,0k (200 000) · 2 tours`,
  `TOTAL … ≈500,0k (500 000) · 5 tours` — les mêmes lignes que sans elle. Ses deux tours ne
  comptent nulle part.
- `ouvrir` avec `CLAUDE_CODE_SESSION_ID=cadre` : `OUVERT Q Q1..Q1 · index +1 · routage +0 ·
  artefact aucun`, et le fichier de fiches inchangé.

**Décidé seul, la nuit du 2026-09-24** (l'utilisateur dort ; à revoir au réveil).
- La session du cadrage se note par `ouvrir`, dans la forme des fiches : `**Session** : <id>`,
  juste avant la première ligne `## ` du fichier — `## Le socle commun` dans un vrai fichier.
- Une session d'en-tête se mesure comme celle d'une fiche : ses tours comptent dans la plage où
  ils tombent — avant l'ouverture, hors fiches.
- Une seule fiche : le code, ses tests et sa docstring vont ensemble.

**Ce qu'on ne fait pas.** Recompter les chantiers clos (n° 37 `RCP`) : les fichiers déjà écrits ne
reçoivent pas de ligne. `cocher`, `page --creer` et `feuille` ne notent rien de plus. Les bornes
de `plages` ne changent pas : un cadrage coupé par un commit étranger reste coupé.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `CAD1` | La session du cadrage notée et comptée | rien |

---

<!-- FICHE:CAD1 -->
## CAD1 [ ] — La session du cadrage notée et comptée

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (`cmd_ouvrir`, `parts_aux_commits` et ses appelants, la
docstring), `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
1. Tests d'abord, dans `scripts/test-vlp.py`.
   - Découpe (après la ligne 533) : une session de cadrage `c.jsonl` dans `t`, trois tours à
     `T0 + 20`, `T0 + 40` et `T0 + 1000`, sans sous-agent ; `qc.md` dans `avec`, c'est `QFICHES`
     avec `**Session** : <c.jsonl>` et une ligne vide juste avant `## Le socle commun`. Alors
     `cout` sur `qc.md` rend les lignes `Q1` et `Q2` de `attendu`, puis
     `hors fiches · ≈400,0k (400 000) · 4 tours · 2,00 $ = session ≈400,0k (400 000) · 4 tours · 2,00 $ + 0 sous-agent`
     et `TOTAL (fiches + hors fiches) · ≈900,0k (900 000) · 9 tours · 4,50 $ = session ≈700,0k (700 000) · 7 tours · 3,50 $ + 1 sous-agent ≈200,0k (200 000) · 2 tours · 1,00 $` ;
     `page` sur `qc.md` (`--creer --projet P --titre T --resultat R --date 2026-01-05`) porte
     `Hors fiches : ≈400,0k (400 000) · 4 tours · 2,00 $` et
     `Coût du chantier : ≈900,0k (900 000) · 9 tours · 4,50 $`.
   - Bloc `ouvrir` (ligne 823) : `CLAUDE_CODE_SESSION_ID` vaut `cadre` pour tout le bloc, et
     l'environnement est rendu à la fin (`try` / `finally`, comme lignes 878 à 895). Le premier
     `ouvrir` rend `OUVERT Q Q1..Q2 · index +1 · routage +1 · session +1 · artefact aucun — <t>`,
     et `ctx/30-q.md` vaut alors `# Chantier Q — Un titre\n\n**Session** : cadre\n\n## Q1 [ ] — a\n## Q2 [ ] — b\n`.
     La relance qui suit rend `session +0`, et le fichier garde une seule ligne `**Session**`.
     Un `ouvrir` sous `CLAUDE_CODE_SESSION_ID` vide rend `session +0`, son fichier inchangé.
   Le texte d'écart nomme le cas qui tombe. Lance `py scripts/test-vlp.py` ; cite l'écart qu'il
   imprime.
2. `ouvrir` : si `CLAUDE_CODE_SESSION_ID` n'est pas vide et n'est sur aucune ligne `**Session**`
   du fichier de fiches, `**Session** : <id>` puis une ligne vide vont juste avant la première
   ligne qui commence par `## `. Le fichier rejoint `ecritures` : rien ne s'écrit avant que tout
   soit calculé. La ligne `OUVERT` dit `· session +1` ou `· session +0`, juste après `routage`.
3. `parts_aux_commits` mesure aussi les sessions de l'en-tête — les lignes `**Session**` avant le
   premier `TITRE` —, après celles des fiches, sans doublon. `cmd_cout` et `regenerer` les lui
   passent, par `couts` et `couts_aux_commits`. Rien d'autre ne change.
4. La docstring : `ouvrir` dit la ligne qu'il pose et `session +<0|1>` ; `cout` et `page`, que les
   sessions de l'en-tête — le cadrage, notées par `ouvrir` — se mesurent comme celles des fiches.
Tu ne commites pas : le chef le fera.

**Critère de fin**
`py scripts/test-vlp.py` et `py scripts/test-mesure-tokens.py` rendent `OK` ; ton compte rendu
cite l'écart de l'étape 1.
<!-- /FICHE -->
