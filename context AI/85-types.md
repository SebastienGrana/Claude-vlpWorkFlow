> **QUAND LIRE** : on joue une fiche `TYP*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache TYP<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier TYP — pyright sans erreur, gardé au commit

**À quoi il sert.** `pyright scripts/` est à 0 depuis `8acfc79` (2026-09-25), mais rien ne le
garde : la règle ne vit que dans le `CLAUDE.md` de l'utilisateur. TYP la pose dans le dépôt —
un `pyrightconfig.json` et un bloc de `.githooks/pre-commit` qui refuse un commit en erreur.

**Estimé.** 1 fiches · ≈4,16 $ — ≈4,16 $/fiche sur 72 clos (le 2026-09-27).

**CLOS** le 2026-09-27. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** TYP1..TYP1 (2026-09-27) : pyrightconfig.json (scripts, mode standard) et un bloc pyright dans .githooks/pre-commit : un commit qui indexe un .py en erreur est refusé ; pyright absent, le hook le dit et laisse passer — estimé 1 fiches ≈4,16 $ (taux plat) · cadré 1 · joué 1 fiches 1,64 $.

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356

## Le socle commun

Mesuré au cadrage (2026-09-27) : `pyright 1.1.414` ; `pyright scripts/` → `0 errors`, 6 fichiers,
5 s ; `pyright "context AI/38-audit-scripts"` → `12 errors` sur 11 scripts ; sur les 200 derniers
commits, 66 touchent un `.py` (`scripts/test-vlp.py` 61, `scripts/vlp.py` 59, `boucle.py` et
`test-boucle.py` 2 chacun, `38-audit-scripts/rel1-carte.py` 2).

Tranché la nuit du 2026-09-27, l'utilisateur dormant (🟡 de la TODO n° 54) :

- **Quand** : seulement si le commit indexe un `.py` — 66 commits sur 200, 5 s chacun.
- **Quoi** : `pyrightconfig.json` à la racine, `include: ["scripts"]`, mode `standard` — celui du
  0 mesuré (le défaut de pyright). `38-audit-scripts` reste dehors : ses 12 erreurs sont d'avant,
  les nettoyer est un chantier à lui.
- **Absent** : le hook le dit sur une ligne et laisse passer — le kit est cloné en groupe.
- **Où** : avant le bloc `claude`, dont la branche « introuvable » sort par `exit 0`.

pyright lit l'arbre de travail, pas l'index : un fichier corrigé mais non indexé passe. Limite
connue, dite dans le commentaire du hook.

| Fichier | Rôle |
|---|---|
| `.githooks/pre-commit` | valide `plugin.json` et `marketplace.json` par `claude plugin validate` |
| `scripts/test-vlp.py`, `:2725` | le test du hook, dans un dépôt temporaire |

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `TYP1` | Garder pyright au commit | rien |

Une seule fiche.

---

<!-- FICHE:TYP1 -->
## TYP1 [x] — Garder pyright au commit

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356
**Dépend de** : rien.
**Fichiers** : `pyrightconfig.json` (neuf), `.githooks/pre-commit`, `scripts/test-vlp.py` — et
rien d'autre.

**Prompt**
Écris `pyrightconfig.json`. Dans `.githooks/pre-commit`, avant le bloc `claude` : si
`git diff --cached --name-only --diff-filter=ACMR` nomme un `.py`, lance `pyright` à la racine ;
sortie non nulle → sa sortie sur stderr, `pre-commit : pyright en erreur, commit refusé.`, exit
1 ; `pyright` introuvable → `pre-commit : pyright introuvable, vérification de types sautée.`
et la suite. Un test `tester_hook_pyright` dans un dépôt temporaire : `.githooks` copié, claude
caché (`APPDATA`, `LOCALAPPDATA` vides), un faux `pyright` en tête du `PATH` qui sort 1.

**Critère de fin**
Faux `pyright` : un `.py` indexé → code 1 et « pyright en erreur » ; un `.md` seul → code 0.
Sans `pyright` dans le `PATH` : un `.py` indexé → code 0 et « pyright introuvable ». Mutants : la
condition `.py` retirée → le `.md` seul est refusé ; le code de sortie ignoré → le `.py` passe.
Le vrai `pyright` à la racine : `0 errors`. `test-vlp.py` finit par `OK` ; pyright 0.
<!-- /FICHE -->
