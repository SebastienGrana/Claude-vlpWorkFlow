> **QUAND LIRE** : on joue une fiche `REC*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache REC<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier REC — Recompter les chantiers clos au coût juste

**À quoi il sert.** Le total de la feuille de route (48 clos, 681 541 003 tokens le
2026-09-25) additionne des chiffres comptés de trois façons ; REC les recompte d'une seule.

**CLOS** le 2026-09-25. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** REC1..REC4 (2026-09-25) : la feuille de route recomptée par cout : 23 clos recomptés, 25 gardés et marqués non recomptés, total 681 541 003 → 700 725 374 ; 22 bilans marqués (recompté par REC).

**Session** : b9600304-33a7-463b-a219-534ddbe25f1d

## Le socle commun

**Décidé au cadrage (2026-09-25), avec l'utilisateur :**

- Le recompté d'un clos = le `TOTAL (fiches + hors fiches)` que rend `vlp.py cout` sur son
  fichier de fiches : découpe aux commits, sous-agents et cadrage compris.
- **Gardé**, jamais recompté : un clos en `DÉCOUPE aucune` (les dix sans commit de fiche —
  M, C, T, S, L, W, X, F, O, Q —, qui retomberaient sur des sessions entières, sur-comptées :
  Q 33 003 302 contre 23 753 914 inscrits), sans ligne `**Session**`, ou dont une
  transcription manque. Il reste, marqué « non recompté », avec sa raison.
- Portée : la feuille de route locale, republiée une fois, et les bilans de
  `context AI/08-etat.md` dont le chiffre change. Les pages de chantier ne sont **pas**
  republiées. Hors chantier : les essais `claude -p` (chantier `ESS`).
- Un chiffre changé ne s'efface pas : l'ancien reste, marqué (« Un énoncé renversé se garde,
  marqué », `methode-chantier.md`).

**Ce qui existe, dans `scripts/vlp.py` :**

| Symbole | Ce qu'il fait |
|---|---|
| `cmd_cout` | la découpe d'un fichier : `sessions_de`, `fiches_du_fichier`, `heures_commits`, `parts_aux_commits`, `sessions_entete`, `plus` — à réutiliser, pas à recopier |
| `lignes_clos`, `total_clos`, `BRUT` | les `<tr>` de `ZONE:clos` ; la somme des bruts d'un corps de table |
| `resume_clos`, `PIED_CLOS`, `estimation_usd`, `arrondi` | le résumé du bloc repliable, le pied « Total cumulé », leurs formats |
| `page_feuille` | le chemin de `<contexte>/artefacts/feuille-de-route.html` |

- ⚠️ `BRUT` ne lit une cellule que si elle **finit** par `(<chiffres>)</td>` sans `<` avant :
  une balise ou une seconde parenthèse dans la cellule la retire du total, **en silence**.
- Lien ligne de feuille ↔ fichier : la plage (`JUG1–JUG3`) et celle de l'index
  (`JUG1..JUG3`, `context AI/00-INDEX.md`) portent le même préfixe.
- Tests dans `scripts/test-vlp.py`, forme `verifier(` ; chaque test nomme son mutant.
  pyright sur `scripts/` : 0 erreur avant, 0 après.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `REC1` | Recompter en lecture seule | rien |
| `REC2` | Ranger les écarts réels par cause | `REC1` |
| `REC3` | Écrire le recompte dans la feuille | `REC1` |
| `REC4` | Appliquer, marquer les bilans, republier | `REC2`, `REC3` |

`REC2` et `REC3` peuvent se jouer dans n'importe quel ordre ; `REC4` écrit sur le vrai kit.

---

<!-- FICHE:REC1 -->
## REC1 [x] — Recompter en lecture seule

**Session** : b05877e2-d5f3-4870-a05a-8489820bb815
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Ajoute la sous-commande `recompter <projet>`, qui **n'écrit rien**. Pour chaque ligne de
`ZONE:clos` de la feuille de route, elle retrouve le fichier de fiches par l'index
(même préfixe de plage), puis imprime une ligne :
`<préfixe> inscrit <n> · recompté <n|gardé> · écart <±n> · <méthode>`, la méthode étant
`découpe`, ou `gardé — <raison>` (`DÉCOUPE aucune`, sans session, transcription absente,
fichier introuvable). Ajoute `partagée avec <préfixes>` quand une de ses sessions figure
aussi dans le fichier d'un autre clos. Dernière ligne :
`RECOMPTE <n> clos · <n> recomptés · <n> gardés · inscrit <n> · recompté <n> · écart <±n>`,
où le recompté total = inscrit total + somme des écarts (gardés : écart 0).
Réutilise la découpe de `cmd_cout` en l'extrayant dans une fonction qui rend des nombres ;
`cout` doit imprimer exactement la même chose qu'avant. Documente la sous-commande dans la
docstring du module. Tests d'abord, sur un projet factice : un clos découpé, un gardé.

**Critère de fin**
`py scripts/test-vlp.py` passe, nombre de `verifier(` avant → après ; deux mutants tombent :
un gardé compté dans l'écart, et la somme finale faite sans les gardés. Sur le vrai kit,
`py scripts/vlp.py recompter .` rend pour JUG le même nombre que la ligne `TOTAL` de
`py scripts/vlp.py cout "context AI/59-juger-fin.md"` (les deux sorties recopiées), et
`git status` ne montre aucun fichier de contexte modifié. pyright : compte brut.
<!-- /FICHE -->

---

<!-- FICHE:REC2 -->
## REC2 [x] — Ranger les écarts réels par cause

**Session** : b05877e2-d5f3-4870-a05a-8489820bb815
**Dépend de** : `REC1`.
**Fichiers** : `context AI/08-etat.md` (journal seulement) — et rien d'autre.

**Prompt**
Lance `py scripts/vlp.py recompter .` sur le kit et recopie sa sortie brute au journal de
`context AI/08-etat.md`, sous une entrée datée `REC2`. Puis range **chaque écart non nul**
sous une cause, avec sa preuve : session partagée avec un autre clos (la sortie le dit),
sous-agents non comptés avant `CPT`, cadrage non compté avant `CAD`, autre. Les dates de
clôture de `CPT` et `CAD` se lisent dans `context AI/00-INDEX.md` ou le fichier d'état ;
ne les écris pas de mémoire. Une cause « autre » se dit telle, sans explication inventée.
Écris la table **avant / après par cause** : nombre de clos, inscrit, recompté, écart. Ne
change encore aucun chiffre publié.

**Critère de fin**
Au journal : la sortie brute de `recompter`, et la table par cause dont la somme des écarts
égale l'écart de la ligne `RECOMPTE` — les deux nombres écrits côte à côte. Aucun autre
fichier modifié (`git status`).
<!-- /FICHE -->

---

<!-- FICHE:REC3 -->
## REC3 [x] — Écrire le recompte dans la feuille

**Session** : b42199e6-9ed4-48b8-8da0-ea2aedff47d7
**Dépend de** : `REC1`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Ajoute `--ecrire` à `recompter`. Pour un clos recompté dont l'écart n'est pas nul, sa
cellule de tokens prend le recompté, au format de `clore`, et garde l'ancien chiffre,
marqué `recompté (REC), était <n>`. Pour un gardé, la cellule garde son chiffre et gagne
`non recompté — <raison>`. Dans les deux cas, la marque ne doit pas sortir la cellule du
total : relis la contrainte de `BRUT` au socle, et place la marque en conséquence. Puis le
pied « Total cumulé » et le résumé du bloc repliable sont resommés par `total_clos`,
`resume_clos` et `estimation_usd`. Relancé, `--ecrire` ne change plus rien. Tout se
calcule avant l'écriture. Dernière ligne : `ÉCRIT <n> cellules · total <avant> → <après>`.

**Critère de fin**
Tests sur une feuille factice, nombre de `verifier(` avant → après : après `--ecrire`,
`total_clos` égale le recompté de la ligne `RECOMPTE` ; un second passage rend `ÉCRIT 0`.
Trois mutants tombent : la marque posée en parenthèses, la marque dans une balise, le pied
non resommé. pyright : compte brut.
<!-- /FICHE -->

---

<!-- FICHE:REC4 -->
## REC4 [x] — Appliquer, marquer les bilans, republier

**Session** : 9f9f121e-06ec-4a28-b35f-ef220051ceb7
**Dépend de** : `REC2`, `REC3`.
**Fichiers** : `context AI/artefacts/feuille-de-route.html`, `context AI/08-etat.md` — et rien d'autre.

**Prompt**
Lance `py scripts/vlp.py recompter . --ecrire` sur le kit. Puis, pour chaque clos dont la
table de `REC2` donne un écart non nul, trouve son bilan daté dans « Où on en est » de
`context AI/08-etat.md` : s'il cite son chiffre de tokens, ajoute juste après
`(recompté par REC : <n>)`, sans rien effacer. Vérifie ensuite que la feuille est
cohérente : `py scripts/vlp.py feuille . --verifier` et `py scripts/vlp.py niveau .`.
Republie la feuille de route : son URL est la ligne **artefact feuille de route** de
`CHANTIER.md` ; `action: "read"` d'abord, puis publie le fichier local avec cette `url`,
sans `favicon`, `label` `REC recompté`.

**Critère de fin**
Les lignes `ÉCRIT` et `RECOMPTE` recopiées ; un second `recompter . --ecrire` rend
`ÉCRIT 0` ; le total du pied de la feuille égale le recompté de `RECOMPTE` ; le nombre de
bilans marqués égale le nombre de clos à écart non nul dont le bilan cite un chiffre (les
deux comptes côte à côte) ; `feuille --verifier` et `niveau` sans écart ; la publication
a répondu.
<!-- /FICHE -->
