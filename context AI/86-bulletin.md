> **QUAND LIRE** : on joue une fiche `CHK*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache CHK<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier CHK — `/vlp:check` lit le contrat

**À quoi il sert.** `vlp.py contrat` (chantier `CON`) ne tourne qu'à la main. `/vlp:check` le
lancera depuis l'ouverture du chantier courant : combien de sous-agents, combien ont écrit dans
Git, combien sans statut en tête — le bulletin du gardien, sans rien rejouer.

**Estimé.** 0,5 fiches · ≈2,07 $ — ≈4,15 $/fiche sur 73 clos (le 2026-09-27).

**Fait.** Rien. Ouvert le 2026-09-27, cadré en 2 fiches, `CHK1` à jouer.

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356

## Le socle commun

Mesuré au cadrage (2026-09-27), `py scripts/vlp.py contrat` : `CONTRAT 103 sous-agents · 10
écrivent dans Git · 46 sans statut en tête`, 1,2 s. `--depuis` garde ceux dont la **session
parente** a démarré à D ou après — voulu par `CON` : la définition de l'agent se charge au départ
de la session.

Le 🟡 de la TODO n° 61 — commit d'ouverture, ou session du cadrage notée par `ouvrir` — tranché la
nuit du 2026-09-27, l'utilisateur dormant, par la mesure :

- 28 des 103 sous-agents sont partis dans une session qui était aussi un cadrage : la session
  parente démarre avant l'ouverture. Borne « commit, session parente » : REV en rate 3, RLG 2.
- Une session a cadré 5 chantiers (`53` à `57`). Borne « départ du cadrage » : elle range dans ZER
  14 sous-agents partis avant son ouverture.
- Le premier commit qui nomme le préfixe est souvent l'ajout à la TODO (ECA, TYP, HAB) : faux.
- Le commit qui **ajoute le fichier de fiches** est « Chantier X ouvert » pour 69 fichiers sur 80 ;
  les 11 autres sont des fichiers de tête ou d'avant la convention.

Retenu : l'heure d'auteur du plus ancien commit qui ajoute le fichier de fiches, comparée à
l'heure de départ **du sous-agent lui-même** — seule borne juste des deux côtés.

| Fichier | Rôle |
|---|---|
| `scripts/vlp.py` | `cmd_contrat`, `:1585` ; sa docstring, `:228` ; ses options, `:4384` |
| `scripts/test-vlp.py`, `:2498` | le test de `contrat`, deux sous-agents fabriqués |
| `skills/check/SKILL.md` | `/vlp:check`, huit vérifications de A à H |

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `CHK1` | `contrat --ouverture` : depuis l'ajout du fichier de fiches | rien |
| `CHK2` | `/vlp:check` rend le bulletin du gardien | `CHK1` |

---

<!-- FICHE:CHK1 -->
## CHK1 [x] — `contrat --ouverture` : depuis l'ajout du fichier de fiches

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
`contrat --ouverture F` : la borne est l'heure d'auteur du plus ancien commit qui ajoute F
(`git log --diff-filter=A`) ; ne garde que les sous-agents partis à cette heure ou après, par
leur première ligne horodatée à eux. Écrit d'abord `DEPUIS <heure UTC> · ouverture de F`. F dans
aucun commit : `GARDE:`, sort 1. Docstring de `contrat` à jour.

**Critère de fin**
Test dans un dépôt temporaire : F ajouté à T0 + 1000 ; session parente partie à T0 + 200 ; un
sous-agent parti à T0 + 500, un autre à T0 + 1500 → `CONTRAT 1`, seul le second listé, la ligne
`DEPUIS`. F non commité → `GARDE:`, code 1. Mutants : l'heure de la session parente au lieu de
celle du sous-agent → 0 listé ; le filtre retiré → 2 listés. Sur le vrai dépôt, `contrat
--ouverture "context AI/86-bulletin.md"` : sa sortie brute. `test-vlp.py` finit par `OK` ;
pyright 0.
<!-- /FICHE -->

---

<!-- FICHE:CHK2 -->
## CHK2 [x] — `/vlp:check` rend le bulletin du gardien

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356
**Dépend de** : `CHK1`.
**Fichiers** : `skills/check/SKILL.md` — et rien d'autre.

**Prompt**
Une vérification **I** : `contrat --ouverture "<fichier de fiches courant>"`, sautée si ce fichier
est « aucun ». Un sous-agent qui écrit dans Git ou sans statut en tête a enfreint
`agents/fiche.md` : le nommer. « huit » devient « neuf », « de A à H » devient « de A à I ».
Court : chaque ligne se paye à chaque `/vlp:check`.

**Critère de fin**
`grep -c "contrat --ouverture" skills/check/SKILL.md` → 1 ; « huit » absent. Le bloc de I, lancé
à la main avec le fichier de fiches courant : `DEPUIS` puis `CONTRAT`. Lignes ajoutées : leur
compte brut. Rejouer `/vlp:check` après `/reload-plugins` est un geste de l'utilisateur : il va
au rapport, pas au critère.
<!-- /FICHE -->
