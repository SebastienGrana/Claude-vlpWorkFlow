> **QUAND LIRE** : on joue une fiche `S*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache S<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier S — Un script `vlp.py` pour la mécanique

**À quoi il sert.** Les commandes extraient, valident et régénèrent à coups de
`sed`/`awk` et de HTML retapé par le modèle (points 9, 12, 15 de `12-audit.md`).
Le chantier met cette mécanique dans un script testé, que les commandes appellent.

**Fait.** Rien. Ouvert le 2026-09-17, cadré en 5 fiches, `S1` à jouer.

## Le socle commun

**Résultat visible.** `scripts/vlp.py` (testé par `scripts/test-vlp.py`) offre
`carte`, `extraire`, `socle`, `sessions`, `valider` et `page` ; `carte.py` est
retiré ; `tache`, `enchainer`, `chantier`, `init`, `check`, `agents/fiche.md`,
`references/tache-page.md` et `cloture.md` l'appellent au lieu des `sed`/`awk`
et du HTML retapé. Gain prouvé avant/après, comptes bruts à côté.

**Les sous-commandes** (noms retenus, ne pas renommer) :

| Appel | Rend | Sortie |
|---|---|---|
| `vlp.py carte [dossier]` | ce que rend `carte.py` aujourd'hui, à l'identique | toujours 0 |
| `vlp.py extraire <fichier> <fiche>` | la fiche entre ses marqueurs, puis `--- fiche, lignes : N` | 1 si absente |
| `vlp.py socle <fichier>` | la plage `## Le socle commun` → `## L'ordre des fiches`, puis `--- socle, lignes : N` | 1 si vide |
| `vlp.py sessions <fichier>` | un id `**Session**` par ligne, dédoublonnés, dans l'ordre | 0 |
| `vlp.py valider <fichier>…` | `fichier:ligne: message` par écart, puis un bilan | 1 si écart |
| `vlp.py page <fichier> <page.html> [options]` | réécrit la page locale, imprime un bilan | 1 si échec |

**Invariants.** Python 3 sans dépendance, zéro appel modèle ; `stdout` et
`stderr` reconfigurés en UTF-8 (Windows) ; lecture `\r\n` tolérée ; aucun
chemin de machine. Une commande l'appelle par
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" … 2>/dev/null || python "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" …`
— le repli prouvé en R3 (`python3` Windows = faux raccourci). Un test imprime
`OK` et sort 0, ou le premier écart et sort 1, sans fixture sur disque
(modèle : `scripts/test-carte.py`).

**Ce qui existe et se réutilise.** `scripts/carte.py` : `equipe`, `trouver`,
`fichier_courant`, `fiches`, `carte`. `scripts/mesure-tokens.py` : `resoudre(arg)`
→ (chemin, erreur) ; `mesurer(chemin)` → (dict `tours`, `total`, `usd`…, erreur),
importé par `importlib` (tiret dans le nom). Format du coût : convention en tête
de `templates/artefact-chantier.html` ; ligne réelle :
`≈1,5M (1 505 630) · 11 tours · 1,06 $`. Zones de page : `ZONE:avancement`,
`ZONE:fiches`, `ZONE:blocage`, `ZONE:journal`, `ZONE:bilan`.

**Mesure « avant »** (2026-09-17, cadrage) : lignes `sed`/`awk` dans les
commandes : 11 (tache 5, check 2, enchainer 2, chantier 1, cloture 1) ; appels
à `carte.py` : 4 (tache 2, enchainer 2) ; page retapée à chaque fiche :
130 lignes / 10 195 octets (`15-reduire.html`) ; 6 bis de `/vlp:tache` :
5 appels (grep, read, réécrire, wc, publier) ; étape 0 de `/vlp:chantier` :
2 appels (boucle `while`, `cat`), et la boucle prend `commands/chantier.md`
pour `CHANTIER.md` sous Windows et macOS. Appels prescrits de `/vlp:tache`
sur le chemin heureux : 9.

**Dehors.** Hooks (TODO 5), evals (6), migration `skills/` (8), `/vlp:init`
au-delà de sa détection de projet (10). Les fichiers de fiches et pages clos
(09 à 15) ne se réécrivent pas : ils servent de jeu d'essai, en lecture seule.
Le rejeu réel des commandes après `/reload-plugins` reste le geste de
l'utilisateur : noté au journal, pas simulé.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `S1` | Créer `vlp.py` : carte, extraire, socle, sessions | rien |
| `S2` | Ajouter `valider` | `S1` |
| `S3` | Ajouter `page` | `S1` |
| `S4` | Brancher `tache`, `enchainer`, `fiche`, `tache-page`, `cloture` | `S1`, `S3` |
| `S5` | Brancher `chantier`, `init`, `check`, mesurer l'« après » | `S2`, `S3`, `S4` |

S2 et S3 sont parallélisables ; S4 et S5 non.

---

<!-- FICHE:S1 -->
## S1 [ ] — Créer `vlp.py` : carte, extraire, socle, sessions

**Dépend de** : rien.
**Fichiers** : `scripts/carte.py`, `scripts/test-carte.py` (lus puis retirés),
`scripts/vlp.py`, `scripts/test-vlp.py` (créés), `commands/tache.md`,
`commands/enchainer.md` (les 4 appels à `carte.py` seulement).

**Prompt**
Crée `scripts/vlp.py`, un point d'entrée à sous-commandes (`argparse`). Reprends
`carte.py` tel quel dans `carte` — même sortie, octet pour octet. Ajoute
`extraire` (fiche entre `<!-- FICHE:X -->` et `<!-- /FICHE -->` ; sans
marqueurs, repli sur `## X ` → `---` précédé d'une ligne `GARDE:` ; absente :
sortie 1), `socle` et `sessions` (socle commun). Migre les cas de
`test-carte.py` dans `test-vlp.py`, ajoute ceux des trois nouvelles
sous-commandes (marqueurs présents, absents, `---` dans un bloc de code, fiche
absente). Avant de retirer `carte.py`, compare les deux sorties sur ce projet.
Remplace les 4 appels à `carte.py` dans `tache.md` et `enchainer.md`, puis
retire `carte.py` et `test-carte.py`.

**Critère de fin**
`python scripts/test-vlp.py` imprime `OK` ; `vlp.py carte` et l'ancien `carte.py`
rendent la même sortie sur ce dépôt (`diff` vide, lignes comptées) ;
`vlp.py extraire "context AI/15-reduire.md" R3` rend la même chose que le `sed`
de `tache.md` (lignes comptées des deux côtés) ; `grep -rn carte.py commands`
rend 0 ligne.
<!-- /FICHE -->

---

<!-- FICHE:S2 -->
## S2 [ ] — Ajouter `valider`

**Dépend de** : `S1`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `methode-chantier.md`
(lu : les règles d'un fichier de fiches) — et rien d'autre.

**Prompt**
Ajoute `vlp.py valider <fichier>…`. Écarts à relever, un par ligne
`fichier:ligne: message` : marqueur ouvrant sans fermant, ou imbriqué ;
identifiant du marqueur ≠ celui du titre qui le suit ; titre `## X1` sans
marqueurs ; identifiant en double ; `## Le socle commun` ou
`## L'ordre des fiches` absent, en double, ou après la première fiche ; fiche
sans ligne `**Critère de fin**` ; `(visuel)` ailleurs que sur la ligne
`**Critère de fin** (visuel)` (point 9). Fiche au-delà du seuil de
`methode-chantier.md` : avertissement, pas écart — le nombre y vit, le script
le cite en commentaire. Dernière ligne :
`VALIDE|INVALIDE <n> fiches · socle <n> lignes · <n> écarts · <n> avertissements`.
Teste chaque écart sur un fichier construit, et un fichier sain.

**Critère de fin**
`python scripts/test-vlp.py` imprime `OK` ; `vlp.py valider` sur
`context AI/09-enchainer.md` à `15-reduire.md` et `16-script.md` rend une ligne
de bilan par fichier, comptes affichés, et relève le `(visuel)` de C1 dans
`11-conso.md` ; les écarts trouvés sont listés, pas corrigés (archives).
<!-- /FICHE -->

---

<!-- FICHE:S3 -->
## S3 [ ] — Ajouter `page`

**Dépend de** : `S1`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`,
`templates/artefact-chantier.html`, `context AI/artefacts/15-reduire.html`
(lu : une page réelle) — et rien d'autre.

**Prompt**
Ajoute `vlp.py page <fichier> <page.html>`. La page est **régénérée** depuis le
fichier : `ZONE:fiches` (id et titre des titres `## X1`, `[x]` → faite, première
non cochée → encours, les autres à faire), `ZONE:avancement`, ligne de comptage,
date du pied de page (du jour). Gardé de la page existante : en-tête, notes,
journal, blocage, bilan. Options : `--note <fiche> <texte>` (remplace sa note),
`--journal <texte>` (ajoute une ligne datée), `--creer --projet P --titre T
--resultat R` (page absente : part du gabarit, journal vide, blocage et bilan
`hidden`). Blocage : masqué si sa fiche est `[x]`. Coûts : chaque session de
`**Session**` mesurée une fois par `mesurer` ; partagée par plusieurs fiches,
son coût va sur la dernière qui la porte ; `.cout-total` = somme dédoublonnée ;
format de la ligne réelle. Texte échappé HTML. Bilan imprimé : fiches, faites,
en cours, lignes de la page, total ; au-delà de 250 lignes, une ligne `GARDE:`
(le nombre vit dans `ARTEFACTS.md`, cité en commentaire). Option `--verifier` :
n'écrit rien, sort 1 si la page diffère.

**Critère de fin**
`python scripts/test-vlp.py` imprime `OK` ; `vlp.py page --verifier` sur
`15-reduire.md` / `15-reduire.html` (copie dans le bac à sable) : écarts listés
et expliqués ; `--creer` sur `16-script.md` rend une page de 5 fiches, lignes
comptées, sous 250.
<!-- /FICHE -->

---

<!-- FICHE:S4 -->
## S4 [ ] — Brancher `tache`, `enchainer`, `fiche`, `tache-page`, `cloture`

**Dépend de** : `S1`, `S3`.
**Fichiers** : `commands/tache.md`, `commands/enchainer.md`,
`agents/fiche.md`, `references/tache-page.md`, `cloture.md` — et rien d'autre.

**Prompt**
Remplace chaque `sed`/`awk`/`grep` de mécanique par `vlp.py` : étape 1 de
`tache.md` (`extraire` + `socle` dans le même appel), bloc de l'étape 6
(`sessions` au lieu du `sed`, puis `page` dans le même appel, avec `--note`),
`enchainer.md` (titres, socle, fiche), `cloture.md` (`sessions`).
`references/tache-page.md` ne garde que le jugement : quoi mettre en `--note`
et `--journal`, publier avec `url` (sans `read` préalable si la session a le
fichier à jour ; refus → relire, fusionner, republier), ne pas toucher la
feuille de route. Retire de `allowed-tools` ce qui n'est plus appelé. Compte
les appels prescrits de `/vlp:tache` sur le chemin heureux, même définition
que R4 (socle de `15-reduire.md`).

**Critère de fin**
`grep -nE "(sed|awk) " commands/tache.md commands/enchainer.md cloture.md`
rend 0 ligne de mécanique (comptes avant 8 → après) ; les blocs de l'étape 1
et de l'étape 6 exécutés tels qu'écrits sur ce projet rendent fiche, socle,
coût et page ; appels prescrits 9 → N, octets relus par fiche 11 518 → N.
<!-- /FICHE -->

---

<!-- FICHE:S5 -->
## S5 [ ] — Brancher `chantier`, `init`, `check`, mesurer l'« après »

**Dépend de** : `S2`, `S3`, `S4`.
**Fichiers** : `commands/chantier.md`, `commands/init.md`, `commands/check.md`,
`CLAUDE.md` (règle 4 seulement) — et rien d'autre.

**Prompt**
`chantier.md` : l'étape 0 devient la carte injectée (`` !`…` ``, comme
`tache.md`), l'étape 0 ter lit les titres dans la carte, l'étape 5 bis crée la
page par `vlp.py page --creer`, l'étape 6 mesure par `vlp.py valider` (socle
compté dans le bilan). `init.md` : sa détection d'un projet déjà équipé passe
par `vlp.py carte` (casse exacte). `check.md` : B par `valider`, C par
`page --verifier`, E par le bilan de `valider`. Dans `CLAUDE.md`, la règle 4
nomme `vlp.py` comme le script de la mécanique, sans recopier la table du
socle. Mesure l'« après » : lignes `sed`/`awk` dans `commands/` et
`cloture.md`, appels à `carte.py`, appels prescrits de `/vlp:chantier`
étape 0.

**Critère de fin**
`grep -rnE "(sed|awk) " commands cloture.md` et `grep -rn "carte.py" commands`
rendent leurs comptes (avant 11 et 4 → après) ; les blocs modifiés exécutés sur
ce projet rendent ce que la commande attend ; `vlp.py valider "context AI/16-script.md"`
rend `VALIDE`.
<!-- /FICHE -->
