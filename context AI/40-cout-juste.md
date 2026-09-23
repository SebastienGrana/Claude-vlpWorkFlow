> **QUAND LIRE** : on joue une fiche `CPT*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache CPT<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier CPT — Un coût juste, fiche par fiche et sous-agents compris

**À quoi il sert.** À la clôture de `REP`, le coût a menti trois fois : une ligne `? $` qui ne
se relit pas, Opus 5.5 sans prix, des sous-agents jamais lus. `CPT` coupe chaque session aux
heures des commits de fiche, sous-agents compris, et `vlp.py cout` le montre fiche par fiche.

**CLOS** le 2026-09-23. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** CPT1..CPT4 (2026-09-23) : vlp.py cout et la page coupent chaque session aux commits de fiche, sous-agents compris, avec une ligne hors fiches ; Opus 5.5 a son prix, une ligne ? $ se relit.

## Le socle commun

**Ce qui existe** — lu au cadrage, le 2026-09-23.

| Symbole | Où | Ce qu'il rend |
|---|---|---|
| `GRILLE` | `scripts/mesure-tokens.py:31` | prix par million, 7 modèles, sans `claude-opus-5-5` |
| `resoudre(argument)` | `scripts/mesure-tokens.py:57` | le chemin `<id>.jsonl`, jamais ses sous-agents |
| `mesurer(chemin)` | `scripts/mesure-tokens.py:115` | les comptes d'un fichier : `total`, `tours`, `usd_exact`… |
| `main(argv)` | `scripts/mesure-tokens.py:215` | une ligne par fichier, puis `TOTAL` |
| `COUT`, `triplet(texte)` | `scripts/vlp.py:671`, `:761` | `(total, tours, usd)` d'une ligne de coût, `None` sur `? $` |
| `ligne_cout(total, tours, usd)` | `scripts/vlp.py:716` | `≈X (n) · t tours · u $`, `?` si le prix manque |
| `couts(…)` | `scripts/vlp.py:770` | le coût par fiche, tiré de l'ancienne page |
| `regenerer(…)` | `scripts/vlp.py:855` | la page réécrite : états, coûts, total |
| `cmd_cout(chemin, session, sortie)` | `scripts/vlp.py:373` | les tables brutes de `mesure-tokens.py` |
| `sessions_de(lignes)` | `scripts/vlp.py:333` | les ids des lignes `**Session** : <id>` |
| `transcript()`, `home()` | `scripts/test-vlp.py:270`, `scripts/test-mesure-tokens.py:144` | un jsonl de test ; un `~` temporaire |

**Les décisions du cadrage** — prises par l'utilisateur le 2026-09-23.

- **Découpe.** Commit de fiche : sujet qui commence par `<ID> :`, heure d'auteur
  (`git log --format=%at`, secondes UTC). Une fiche = les tours `(commit d'avant, son commit]` ;
  le commit d'avant est celui de la fiche précédente — pour la première, le dernier commit
  antérieur qui nomme le préfixe (`REP`, `REP2`…), à défaut le début de la session. Une fiche
  sans commit va jusqu'au bout du transcript.
- **Heure** d'un tour : le `timestamp` de sa première ligne ; d'un sous-agent : la première
  ligne horodatée de son fichier.
- **Sous-agents.** `<dossier>/<id>/subagents/agent-*.jsonl` pour la session `<dossier>/<id>.jsonl` ;
  le `.meta.json` ne nomme pas la fiche. Un sous-agent compte entier dans la plage qui contient
  son heure de départ.
- **Hors fiches.** Les tours de la session hors de toute plage de fiche, jusqu'au dernier
  commit qui nomme le préfixe (cadrage joué dans la session, clôture) : une ligne à part,
  comptée dans le total. Après ce commit, rien ne compte.
- **Sans Git** (pas de `git`, pas de dépôt, aucun commit `<ID> :`) : l'ancienne logique de
  `couts`, sur l'ancienne page — avec `? $` relu.
- **Affichage.** La page garde un nombre par fiche, sous-agents compris ; le détail session /
  sous-agents vit dans `vlp.py cout`.
- **Preuve.** REP recalculé à l'écran ; la page close de REP n'est pas touchée.

**REP, mesuré au cadrage** — les chiffres de la preuve.

- `context AI/39-reparer-pages.md` : une seule session, `da8e3b04-adf4-426a-a7b1-3087bacb5724`,
  de 08:23:08 à 17:35:28 UTC.
- Commits, en UTC (git affiche +0200) : REP1 08:35:08 · REP2 09:00:02 · page 09:16:43 ·
  REP3 10:00:03 · REP4 10:13:57 · clos 10:23:33 · clôture 10:38:35.
- 5 sous-agents `vlp:fiche` : 2 entre REP1 et REP2, 3 entre REP2 et REP3.
- Avant, repris de git (`08-etat.md:118-119`) : REP1 2 702 105 · REP2 4 227 906 ·
  REP3 8 584 756 · REP4 4 840 313 (somme 20 355 080) ; total 23 126 264 tokens, sessions
  seules, dont 2 771 184 à aucune fiche. Sous-agents hors total : 8 161 098 tokens · 1,69 $
  (TODO n° 31).

**Invariants.**

- Python 3 sans dépendance ; `git` s'appelle par `subprocess` et n'est jamais requis : son
  absence mène au repli, jamais à un traceback.
- Tout ce que `ligne_cout` écrit, `triplet` le relit.
- Les tests ne lisent jamais le vrai `~/.claude` : dossiers temporaires.
- Au cadrage, `py scripts/test-vlp.py` et `py scripts/test-mesure-tokens.py` rendent `OK`.
- Une ligne de mesure nomme ce qu'elle compte (méthode).

**Dehors**, et pourquoi : le test aller-retour de tous les formats (`TAR`, n° 33, qui suit
`CPT`) ; le plafond de 30 tours du sous-agent (`SAG`, n° 32) ; le mode `fast` ; les pages des
autres projets ; la page de REP et sa ligne sur la feuille de route (décision « Preuve »).

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `CPT1` | Donner un prix à Opus 5.5, et relire la ligne `? $` | rien |
| `CPT2` | Compter les sous-agents dans `mesure-tokens.py`, sur une plage de temps | rien |
| `CPT3` | Couper la session aux heures des commits de fiche | `CPT1`, `CPT2` |
| `CPT4` | Montrer le coût fiche par fiche dans `vlp.py cout`, et recalculer REP | `CPT3` |

`CPT1` et `CPT2` sont indépendantes, dans l'ordre qu'on veut ; `CPT3` attend les deux, `CPT4`
attend `CPT3`.

---

<!-- FICHE:CPT1 -->
## CPT1 [x] — Donner un prix à Opus 5.5, et relire la ligne `? $`

**Session** : fc426e27-cf5c-499f-b5fb-34f4243ecd34
**Dépend de** : rien.
**Fichiers** : `scripts/mesure-tokens.py`, `scripts/test-mesure-tokens.py`, `scripts/vlp.py`,
`scripts/test-vlp.py` — et rien d'autre ; sur le web, la page des prix de la documentation
officielle d'Anthropic.

**Prompt**
Deux trous du socle, un par script.

La grille. Inventorie d'abord les modèles des transcripts de la machine, `subagents/` compris :
chaque modèle absent de `GRILLE`, avec son nombre de tours. Puis annonce ta recherche en une
ligne, et prends sur la page officielle des prix d'Anthropic les cinq prix de chaque modèle
absent : entrée, sortie, cache lu, cache écrit 5 min et 1 h. Recopie-les tels quels ; le
commentaire de `GRILLE`, qui cite aujourd'hui la skill claude-api, cite le lien et la date.
Relis sur la même page les prix déjà présents : un écart se dit à l'utilisateur, il ne se
corrige pas en silence.

La ligne `? $`. `COUT` refuse deux choses que `ligne_cout` écrit : `? $` quand le prix manque,
et un total sous 1 000, qu'`arrondi` écrit sans parenthèses. Fais-les relire par `triplet`,
qui rend alors `usd = None` ; `couts` porte ce `None` dans ses soustractions sans planter.

Tests : l'aller-retour `triplet(ligne_cout(t, n, u)) == (t, n, u)`, pour un total sous et
au-dessus de 1 000, `u` chiffré ou `None` ; un tour `claude-opus-5-5` dont `usd` n'est plus `?`.

**Critère de fin**
`py scripts/mesure-tokens.py --grille` liste `claude-opus-5-5` ;
`py scripts/mesure-tokens.py da8e3b04-adf4-426a-a7b1-3087bacb5724` ne dit plus « modèle absent
de la grille » et rend un `usd` chiffré ; les deux suites rendent `OK`, avec le nombre de
vérifications avant → après.
<!-- /FICHE -->

---

<!-- FICHE:CPT2 -->
## CPT2 [x] — Compter les sous-agents dans `mesure-tokens.py`, sur une plage de temps

**Session** : b8ed3e27-95e5-44f3-8eee-abebd7322646
**Dépend de** : rien.
**Fichiers** : `scripts/mesure-tokens.py`, `scripts/test-mesure-tokens.py` — et rien d'autre.

**Prompt**
Les sous-agents d'une session ne sont comptés nulle part (socle, « Sous-agents »). Donne à
`mesure-tokens.py` :

1. une fonction qui rend, pour un chemin de session, ses transcripts de sous-agents, triés —
   zéro, sans erreur, quand le dossier `subagents/` manque ;
2. dans `main`, une session passée par id ou par chemin qui amène ses sous-agents, une ligne
   chacun sous la sienne ; `TOTAL` les compte, et « déjà compté » vaut pour eux aussi ;
3. une plage `(debut, fin]` facultative pour `mesurer`, en secondes UTC — sans elle, rien ne
   change. Un tour se juge à son heure, un sous-agent à son heure de départ, entier (socle,
   « Heure »). Un tour sans heure compte, et se signale sur stderr.

Tests, dans des dossiers temporaires comme `home()` : une session et deux sous-agents ; une
session sans `subagents/` ; une plage qui coupe une session en deux ; un sous-agent parti
avant la plage et fini dedans, qui ne compte pas.

**Critère de fin**
`py scripts/mesure-tokens.py da8e3b04-adf4-426a-a7b1-3087bacb5724` rend la ligne de la
session, 5 lignes `agent-*.jsonl` et un `TOTAL` ; la somme des 5 sous-agents vaut 8 161 098
tokens (socle), ou l'écart est dit et expliqué ; `py scripts/test-mesure-tokens.py` rend `OK`,
vérifications avant → après.
<!-- /FICHE -->

---

<!-- FICHE:CPT3 -->
## CPT3 [x] — Couper la session aux heures des commits de fiche

**Session** : 32d8a7aa-6915-4674-b476-9e040f455c75
**Dépend de** : `CPT1` (le repli relit `? $`), `CPT2` (plage et sous-agents).
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `templates/artefact-chantier.html` —
et rien d'autre.

**Prompt**
`couts` tire le coût des fiches d'une session partagée de l'ancienne page : un coût perdu
l'est pour toujours. Fais-le couper la session aux heures des commits (socle, « Découpe »).

1. Une fonction lit par `git log`, lancé dans le dossier du fichier de fiches, l'heure du
   commit de chaque fiche et celles des commits qui nomment le préfixe. Sans `git`, sans
   dépôt ou sans commit de fiche, elle ne rend rien — jamais un traceback.
2. `couts` donne à chaque fiche sa plage de chaque session, sous-agents compris, par la plage
   de `CPT2`. Le reste, jusqu'au dernier commit du chantier, fait « hors fiches » ; la suite
   ne compte pas. Sans heures : l'ancienne logique, telle quelle.
3. La page garde un nombre par fiche ; « hors fiches » y prend une ligne à part, au format de
   `ligne_cout` — le gabarit la porte si besoin, une page sans elle reste lisible. Le total =
   fiches + hors fiches.

Tests : un dépôt git temporaire — sauté, et dit, si `git` manque — avec deux fiches sur une
session horodatée et un sous-agent ; le même sans `.git`, qui retombe sur l'ancienne page.

**Critère de fin**
`py scripts/test-vlp.py` rend `OK`, vérifications avant → après ; sur une copie de la page de
REP hors du projet, `vlp.py page "context AI/39-reparer-pages.md" <copie>` écrit 4 coûts de
fiche et une ligne « hors fiches » dont la somme égale le total affiché — montrer les 6 lignes.
<!-- /FICHE -->

---

<!-- FICHE:CPT4 -->
## CPT4 [x] — Montrer le coût fiche par fiche dans `vlp.py cout`, et recalculer REP

**Session** : 834d2ba1-31ad-4918-9af3-373e66606173
**Dépend de** : `CPT3`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `skills/tache/SKILL.md` (§ 6 bis),
`cloture.md` (le total du bilan), `context AI/08-etat.md` (bilan de REP) — et rien d'autre.

**Prompt**
`vlp.py cout <fichier>` rend aujourd'hui les tables brutes de sessions entières. Fais-lui
rendre, par la découpe de `CPT3`, une ligne par fiche — tours, tokens et dollars de la session,
des sous-agents, et leur somme —, puis « hors fiches », puis le total ; chaque ligne nomme ce
qu'elle compte. Sans heures de commit : la sortie d'avant, et une ligne qui dit pourquoi.
`--session` garde son rôle pour `/vlp:tache`.

Si la sortie change, les phrases qui la décrivent changent avec, courtes :
`skills/tache/SKILL.md` (« La première table est le coût de la session… ») et `cloture.md`
(le total gardé au bilan).

Puis la preuve, sur `context AI/39-reparer-pages.md` : une table avant / après, une ligne par
fiche, qui sépare les causes — plage coupée au commit, sous-agents ajoutés, clôture passée de
REP4 à « hors fiches ». « Avant » est au socle. Le bilan de REP dans `08-etat.md` garde son
chiffre, suivi d'un renvoi daté qui donne le recompte et sa cause (méthode, « énoncé renversé »).

**Critère de fin**
`py scripts/vlp.py cout "context AI/39-reparer-pages.md"` rend 4 lignes de fiche, 1 « hors
fiches » et 1 total ; REP2 porte 2 sous-agents, REP3 en porte 3, et leur somme vaut celle de
`CPT2` ; la table avant / après est montrée en comptes bruts ; `py scripts/test-vlp.py` rend `OK`.
<!-- /FICHE -->
