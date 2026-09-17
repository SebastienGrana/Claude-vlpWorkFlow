> **QUAND LIRE** : on joue une fiche `R*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache R<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier R — Réduire les tours de `/vlp:tache`

**À quoi il sert.** Une fiche coûte 28 à 66 tours (`12-audit.md`) : la facture
est dans les tours, pas dans les lignes. Le chantier retire à `/vlp:tache` les
tours de lecture qu'un texte mieux rangé rend inutiles, et le prouve en chiffres.

**Fait.** Rien. Ouvert le 2026-09-17, cadré en 4 fiches, `R1` à jouer.

## Le socle commun

**Résultat visible.** `commands/tache.md` : corps ≤ 150 lignes ; `CHANTIER.md`
injecté avant le 1er tour ; étapes 0 bis + 1 + 4 lues en un seul appel ;
blocage, page et contraintes partagées dans `references/` ; point 13 de
`12-audit.md` corrigé ; gain prouvé avant/après, comptes bruts à côté.

**Ancres mesurées au cadrage** (`commands/tache.md`, 385 lignes) :

| Quoi | Lignes | Lu ailleurs par |
|---|---|---|
| `allowed-tools` (frontmatter) | 4 | — |
| « `Bash` n'est ouvert que pour lire » — faux, point 13 | 29-36 | — |
| étape 0, trouver le projet + `cat CHANTIER.md` | 48-95 | `enchainer.md:26` (`sed '/^## 0\. /,/^## 1\. /'`) |
| étape 0 bis, titres des fiches | 97-123 | — |
| étape 1, extraire la fiche | 125-154 | — |
| étape 4, socle (`awk`) + trois contraintes | 170-191 | `agents/fiche.md:18` (`/^Trois contraintes/`) |
| bloc Tentatives + page bloquée | 211-241 | `agents/fiche.md:18` (`/^Ajoute donc/`), `enchainer.md:132` (`/marque le blocage/`) |
| coût de la fiche (`mesure-tokens.py`) | 264-279 | — |
| 6 bis, régénérer la page | 281-354 | `enchainer.md:126` (`sed '/^## 6 bis/,/^## 7\./'`) |
| 7, clôture (renvoie à `cloture.md`) | 356-385 | — |

**Mesure « avant »** (`12-audit.md`, six sessions `/vlp:tache`) : 28 à 66 tours,
22 à 82 appels, 1,06 à 5,73 $ ; 1er tour 81 903–83 021 tokens dont
commande + `CHANTIER.md` ≈ 6–7 k.

**Noms retenus.**

- Dossier `references/` à la racine du kit — le rare et le partagé, lus à la
  demande par `cat "${CLAUDE_PLUGIN_ROOT}/references/<nom>.md"`.
- **Appels prescrits** : le nombre d'appels d'outils qu'exige le chemin heureux
  d'une fiche (projet trouvé, fiche non bloquée, vérification scriptable),
  compté sur le texte de `tache.md`, étape par étape. Une mesure par lecture,
  pas un script : c'est du jugement.
- Coût d'une fiche R : l'écart du compteur de session depuis la fiche
  précédente (`scripts/mesure-tokens.py <id>`), comme en T2..T5 — les fiches
  sont jouées d'affilée dans la session du cadrage, à la demande.

**Invariants.**

- Une commande ne découpe jamais une autre commande au `sed` (`CHANTIER.md`) :
  ce que `enchainer.md` et `agents/fiche.md` lisent dans `tache.md` passe dans
  `references/`.
- Aucun nombre recopié : 250 vit dans `ARTEFACTS.md`/gabarit, la clôture dans
  `cloture.md`.
- `${CLAUDE_PLUGIN_ROOT}` dans le texte des commandes seulement.

**Dehors.** Le script `vlp.py` et la page calculée (TODO n° 4) ; la migration
`commands/` → `skills/` (n° 8) ; `chantier.md`, `init.md`, `check.md`. Le rejeu
réel de `/vlp:tache` dans une session neuve est un geste de l'utilisateur : il
se note « reste à faire », il ne se simule pas.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `R1` | Prouver l'injection, figer l'« avant » | rien |
| `R2` | Sortir le rare et le partagé dans `references/` | rien |
| `R3` | Injecter la carte, grouper les lectures, corriger le point 13 | `R1`, `R2` |
| `R4` | Tailler à ≤ 150 lignes, mesurer l'« après » | `R3` |

R1 et R2 sont indépendantes ; R3 et R4 non.

---

<!-- FICHE:R1 -->
## R1 [ ] — Prouver l'injection, figer l'« avant »

**Dépend de** : rien.
**Fichiers** : `commands/sonde.md` (jetable, créé puis retiré), `commands/tache.md` (lecture), `context AI/15-reduire.md` (socle), `context AI/08-etat.md`.

**Prompt**
Crée une commande jetable `commands/sonde.md` dont le corps injecte, par
`` !`…` `` : `pwd`, `echo "${CLAUDE_PLUGIN_ROOT}"`, et une boucle qui remonte
jusqu'au `CHANTIER.md` le plus proche puis le `cat` (la boucle de l'étape 0 de
`tache.md`). Mets le `allowed-tools` minimal qui l'autorise. Invoque-la
(`Skill`, `vlp:sonde`) et lis ce qu'elle a reçu. Si l'outil ne la voit pas sans
`/reload-plugins`, vérifie la syntaxe et ses limites dans la doc officielle des
commandes (WebFetch) et note le rejeu réel comme reste à faire.
Puis compte les **appels prescrits** de `tache.md` actuel, étape par étape, et
écris sous « Mesure « avant » » du socle : le total et le détail par étape.
Retire `commands/sonde.md`. Une ligne au fichier d'état : ce qui marche dans
`` !`…` `` et ce qui ne marche pas.

**Critère de fin**
La sortie brute de la sonde (ou la citation de la doc, avec l'URL) montre pour
chacun des trois essais « marche » ou « ne marche pas » ; le socle porte les
appels prescrits avant, total et détail ; `ls commands/sonde.md` échoue.
<!-- /FICHE -->

---

<!-- FICHE:R2 -->
## R2 [ ] — Sortir le rare et le partagé dans `references/`

**Dépend de** : rien.
**Fichiers** : `commands/tache.md`, `commands/enchainer.md`, `agents/fiche.md`, `references/tache-blocage.md`, `references/tache-page.md`, `references/tache-contraintes.md` (créés).

**Prompt**
Déplace sans reformuler le fond, dans trois fichiers de `references/` :
- `tache-contraintes.md` — les trois contraintes de l'étape 4 ;
- `tache-blocage.md` — le bloc « Tentatives » et le marquage de la page bloquée
  (étape 5, à partir de « Et dans ce cas ») ;
- `tache-page.md` — l'étape 6 bis entière.
Dans `tache.md`, chaque passage devient un renvoi d'une à trois lignes qui dit
quand lire le fichier. Dans `enchainer.md` (lignes 126 et 132 ; la 26 attend R3) et
`agents/fiche.md:18`, remplace les `sed`/`awk` sur `tache.md` par un `cat` du
fichier de référence. Ne touche pas encore à l'étape 0 : R3 la change.

**Critère de fin**
`grep -n "commands/tache.md" commands/enchainer.md agents/fiche.md` ne rend
plus que la ligne de l'étape 0 (`enchainer.md:26`) ; chaque `cat` de
`references/` exécuté rend un contenu non vide (nombre de lignes affiché) ;
`wc -l commands/tache.md` avant/après affiché.
<!-- /FICHE -->

---

<!-- FICHE:R3 -->
## R3 [ ] — Injecter la carte, grouper les lectures, corriger le point 13

**Dépend de** : `R1`, `R2`.
**Fichiers** : `commands/tache.md`, `commands/enchainer.md`, `references/tache-projet.md` (si R1 exige un repli).

**Prompt**
Selon ce que R1 a prouvé, fais injecter par `tache.md` avant le 1er tour la
racine du projet et son `CHANTIER.md` ; si l'injection ne tient pas dans tous
les cas (workspace, aucun projet), garde le repli à la main dans
`references/tache-projet.md`, lu seulement dans ces cas. `enchainer.md:26` lit
ce même repère, plus la plage `## 0.` de `tache.md`.
Fusionne en **un seul appel** : titres des fiches (0 bis), extraction de la
fiche (1) et socle (4), avec leurs trois gardes rendues visibles dans la même
sortie (comptes de lignes). Corrige le point 13 : `allowed-tools` n'interdit
rien, il dispense de permission — dis-le en une ligne, sans promesse fausse.
Exécute toi-même les blocs réécrits sur `15-reduire.md`.

**Critère de fin**
Le bloc groupé, exécuté sur `context AI/15-reduire.md` pour `R3`, rend en une
sortie les titres, la fiche et le socle, comptes de lignes affichés ;
`grep -n "que pour lire" commands/tache.md` ne rend rien.
<!-- /FICHE -->

---

<!-- FICHE:R4 -->
## R4 [ ] — Tailler à ≤ 150 lignes, mesurer l'« après »

**Dépend de** : `R3`.
**Fichiers** : `commands/tache.md`, `context AI/15-reduire.md` (socle), `context AI/08-etat.md`, `context AI/12-audit.md` (ligne de la TODO n° 3 seulement).

**Prompt**
Taille le corps de `tache.md` (sans le frontmatter) à 150 lignes au plus :
retire les redites, les justifications que `methode-chantier.md` porte déjà, et
les phrases qui répètent un nombre ou une règle vivant ailleurs. Ne retire
aucune garde. Compte ensuite les appels prescrits **après**, avec la même
définition que R1, et écris le tableau avant/après dans le socle ; mesure les
tours et le coût des fiches R jouées (`scripts/mesure-tokens.py`). Note au
fichier d'état le verdict avec ses comptes bruts, et le rejeu réel de
`/vlp:tache` dans une session neuve comme reste à faire.

**Critère de fin**
`awk 'NR>5' commands/tache.md | wc -l` ≤ 150 ; la table appels prescrits
avant/après est dans le socle, total et détail ; les tables brutes de
`mesure-tokens.py` sont affichées à côté du verdict.
<!-- /FICHE -->
