> **QUAND LIRE** : on joue une fiche `MUT*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache MUT<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier MUT — Le mutant par un outil du kit

**À quoi il sert.** Une fiche de code exige un mutant (`methode-chantier.md`, « Anatomie d'une
fiche ») ; il est joué par un script réécrit à la main à chaque fois. `vlp.py mutant` le remplace.

**Estimé.** 1 fiches · ≈3,01 $ — ≈3,01 $/fiche sur 83 clos (le 2026-09-29).

**CLOS** le 2026-09-29. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** MUT1..MUT1 (2026-09-29) : vlp.py mutant casse le code exprès (texte ou @fichier, CRLF suivi), joue les tests avec VLP_TOUS_ECARTS=1, liste tous les écarts et rend le fichier à l'octet dans un finally — estimé 1 fiches ≈3,01 $ · cadré 1 · joué 1 fiches 1,76 $.

**Session** : b293bb0b-835f-4938-bedc-3114bdb5643a

## Le socle commun

**Mesuré au cadrage (2026-09-29)** — compte brut, motif large (un appel `Bash`/`PowerShell`/`Write`
qui nomme un mutant ou un `mut*.py`, et une trace de test, `.bak`, `sha1sum` ou `replace(`) :
**72 transcriptions, 275 appels** (kit 49, Cairn 10, ce worktree 4). La session de cadrage en a
réécrit 5, dont 3 ratés : échappement de `\n`, `\\` et guillemets, et fichiers en CRLF sur disque.

**Tranché au cadrage (l'utilisateur)** :
- **fait maison**, sans dépendance — mutmut (BSD) et cosmic-ray (MIT) écartés : mutants au
  hasard sous pytest, et une dépendance, contraire à la règle 4 de `CLAUDE.md` ;
- `avant` et `après` en **texte, ou `@chemin`** (le contenu du fichier, tel quel) ;
- **tous les écarts** : `verifier` (`scripts/test-vlp.py:66`) sort au premier ; avec
  `VLP_TOUS_ECARTS=1` il l'imprime et continue, et la suite sort 1 à la fin sans `OK`.

**Invariants de `mutant`** : `avant` doit apparaître **une fois** exactement (sinon `GARDE:`,
rien écrit) ; ses `\n` suivent la fin de ligne du fichier (CRLF ou LF) ; le fichier est rendu **à
l'octet près dans un `finally`**, même si les tests plantent ; empreinte vérifiée avant/après.

**Dehors** : générer des mutants tout seul ; pytest ; les fiches déjà closes.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `MUT1` | Écrire `vlp.py mutant` et `VLP_TOUS_ECARTS` | rien |

Une seule fiche.

---

<!-- FICHE:MUT1 -->
## MUT1 [x] — Écrire `vlp.py mutant` et `VLP_TOUS_ECARTS`

**Session** : b293bb0b-835f-4938-bedc-3114bdb5643a
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `methode-chantier.md` — et rien d'autre.

**Prompt**
Dans `scripts/test-vlp.py`, `verifier` : avec `VLP_TOUS_ECARTS=1` dans l'environnement, imprime
l'`ÉCART:` et sa sortie, compte, continue ; la dernière ligne sort 1 sans `OK` s'il y en a eu.
Dans `scripts/vlp.py`, la sous-commande
`mutant <fichier> <avant> <après> [--test "<commande>"]` : `@chemin` lit l'argument dans un
fichier ; applique les invariants du socle ; lance la commande (défaut : le `test-vlp.py` voisin
de `vlp.py`, par `sys.executable`) avec `VLP_TOUS_ECARTS=1` ; imprime chaque ligne `ÉCART:`, puis
`MUTANT ATTRAPÉ <n> écart(s)` (sort 0) ou `MUTANT VIVANT` (sort 1), puis `RENDU <sha 12>` —
`GARDE:` si l'empreinte a bougé. Docstring de tête : la sous-commande. `methode-chantier.md`,
« Anatomie d'une fiche », exigence 3 : une phrase qui renvoie à `vlp.py mutant` pour le jouer.

**Critère de fin**
1. Tests dans `scripts/test-vlp.py`, dans un dossier temporaire (un `f.py` en CRLF et un test à
   deux `ÉCART` possibles) : mutant attrapé → `MUTANT ATTRAPÉ 2`, sort 0, fichier identique à
   l'octet ; mutant vivant → sort 1 ; `avant` absent ou double → `GARDE:`, rien écrit ; `@chemin`
   avec un `\n` sur un fichier CRLF → appliqué ; test qui plante → fichier rendu quand même.
2. Mutant du mutant, joué par `vlp.py mutant` lui-même : le `finally` retiré → un test tombe.
3. Rejouer par l'outil un mutant de VRB (`"stash"` ajouté à `LECTURE_GIT`) : la liste de ses
   `ÉCART:` — comptes bruts. `py scripts/test-vlp.py` : `OK` ; pyright 0 erreur.
<!-- /FICHE -->
