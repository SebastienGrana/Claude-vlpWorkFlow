> **QUAND LIRE** : on joue une fiche `IDX*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache IDX<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier IDX — L'index ne garde que le vivant, les clos vont à l'archive

**À quoi il sert.** L'index du kit fait 104 lignes pour 80 permises (`vlp.py niveau`,
2026-09-26), dont 63 lignes de chantiers **clos** : chaque clôture en ajoute une. Les
lignes clos partent dans une archive voisine, sans perte, et `clore` le fait seul.

**Fait.** Rien. Ouvert le 2026-09-26, cadré en 3 fiches, `IDX1` à jouer.

**Session** : bb3d3301-a011-4a38-8cf4-76ba9d0f8933

## Le socle commun

Tranché avec l'utilisateur le 2026-09-26 :

- **Toutes** les lignes clos quittent l'index ; aucune n'est gardée. L'index garde les
  fichiers stables, le chantier ouvert, et **une** ligne qui renvoie à l'archive.
- **Aucune perte** : une ligne est déplacée telle quelle, jamais réécrite ni effacée.
- L'archive : `00-INDEX-archive.md`, **dans le même dossier que l'index** — son chemin
  se dérive de celui de l'index par une seule fonction de `vlp.py`, jamais retapé.
- Une ligne clos = une ligne de table qui contient `**clos**`. L'archive est une table
  `| Fichier | Lire quand |`, triée par numéro de fichier (2 premiers chiffres).
- Une seule fonction `archiver` déplace ; la sous-commande `archiver <projet>` et
  `clore` l'appellent. Relancée, elle ne change rien.

| Ce qui touche l'index | Où | Ce qu'il fait |
|---|---|---|
| `cmd_ouvrir` | `scripts/vlp.py`, « # 2. l'index » | insère la ligne **ouvert** après la ligne au plus grand numéro (`LIGNE_FICHIER`) |
| `cmd_clore` | `scripts/vlp.py`, « # 1 bis. » | passe la ligne **ouvert** à **clos** ; écrit `ROUTAGE_CLOS` dans `CLAUDE.md` |
| `cmd_recompter` | `scripts/vlp.py` | trouve le fichier de chaque clos par `PLAGE_INDEX` dans l'index |
| `sans_table_des_clos` | `scripts/vlp.py`, appelé par `cmd_niveau` | exige que l'index nomme chaque fichier de la table des clos |
| `cmd_renvois` | `scripts/vlp.py` | vérifie que les fichiers nommés existent ; poids `index <n>/SEUIL_INDEX` |
| `lignes_du_projet`, `lignes_de`, `champ` | `scripts/vlp.py` | lire un fichier du projet ; lire un champ de `CHANTIER.md` |

Tests : `scripts/test-vlp.py`, style `verifier("<nom> — mutant : <…>", cond, détail)`, chaque
cas dans son propre dossier temporaire — **ne pas réutiliser `t`** d'un `with` voisin, il
supprime le dossier en silence. Du Python touché : `pyright scripts/` à 0 erreur avant le commit.

**Hors du chantier** : le `CLAUDE.md` de Cairn (85/80, autre sujet, à faire dans Cairn) ;
l'index de Cairn (migré à sa prochaine clôture) ; les pages publiées (rien n'y change).

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `IDX1` | Faire lire l'archive aux lecteurs de l'index | rien |
| `IDX2` | Écrire `archiver`, et le faire appeler par `clore` | `IDX1` |
| `IDX3` | Archiver l'index du kit, et pointer la doctrine | `IDX2` |

Rien n'est parallélisable : sans `IDX1`, archiver casserait `recompter` et `niveau`.

---

<!-- FICHE:IDX1 -->
## IDX1 [ ] — Faire lire l'archive aux lecteurs de l'index

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Écris la fonction qui dérive le chemin de l'archive de celui de l'index (socle), puis
une lecture « index + archive » (archive absente : l'index seul, sans erreur). Branche-la
dans `cmd_recompter` (recherche `PLAGE_INDEX`) et dans l'appel de `sans_table_des_clos`
par `cmd_niveau`. Dans `cmd_renvois`, l'archive devient une source de plus (1re cellule),
sans poids ni seuil. N'écris rien dans l'archive : c'est `IDX2`.

**Critère de fin**
`py scripts/test-vlp.py` passe, comptes bruts affichés. Trois cas neufs, chacun avec un
index **sans** la ligne clos et une archive **qui la porte** : `recompter` trouve le fichier
(mutant : ne lire que l'index) ; `niveau` retire la table des clos (mutant : idem) ;
`renvois` signale un fichier absent nommé par l'archive (mutant : archive non lue). Sans
archive, les sorties des tests existants sont inchangées. `pyright scripts/` : 0 erreur.
<!-- /FICHE -->

---

<!-- FICHE:IDX2 -->
## IDX2 [ ] — Écrire `archiver`, et le faire appeler par `clore`

**Dépend de** : `IDX1`.
**Fichiers** : `scripts/vlp.py` (fonction, sous-commande, docstring), `scripts/test-vlp.py`.

**Prompt**
Écris `archiver` selon le socle : déplace chaque ligne `**clos**` de l'index vers l'archive
(créée au besoin avec un titre, une ligne « QUAND LIRE » et l'en-tête de table), triée par
numéro ; pose dans l'index une ligne unique qui renvoie à l'archive, si elle manque.
Sous-commande `archiver <projet>`, sortie `ARCHIVÉ <n> · index <n> lignes · archive <n> lignes`.
`cmd_clore` l'appelle après « # 1 bis. », et sa ligne `CLOS` gagne ` · archivé <n>` ;
`ROUTAGE_CLOS` pointe l'archive. Documente la sous-commande dans la docstring.

**Critère de fin**
`py scripts/test-vlp.py` passe, comptes bruts affichés. Cas neufs : `archiver` sur un index
à 2 clos + 1 ouvert → `ARCHIVÉ 2`, l'ouvert reste, chaque ligne archivée **identique** à
l'octet (mutant : réécrire la ligne) ; relancé → `ARCHIVÉ 0`, rien ne change (mutant :
renvoi posé deux fois) ; `clore` → sa ligne passe à l'archive, `archivé 1` (mutant : `clore`
n'appelle pas `archiver`). Le test `clore : index clos` existant est adapté, pas supprimé.
`pyright scripts/` : 0 erreur.
<!-- /FICHE -->

---

<!-- FICHE:IDX3 -->
## IDX3 [ ] — Archiver l'index du kit, et pointer la doctrine

**Dépend de** : `IDX2`.
**Fichiers** : `context AI/00-INDEX.md`, `context AI/00-INDEX-archive.md` (créé par le
script), `CLAUDE.md` (routage), `templates/CLAUDE.md`, `methode-chantier.md`, `cloture.md`.

**Prompt**
Mesure d'abord, sorties brutes gardées : `wc -l` de l'index, `grep -c '\*\*clos\*\*'`,
`vlp.py renvois .`, `vlp.py recompter .`. Lance `vlp.py archiver .` — jamais de déplacement
à la main. Remesure. Puis la doctrine : la ligne « relire un chantier clos » du routage
(`CLAUDE.md`, `templates/CLAUDE.md`) nomme l'archive ; `methode-chantier.md` et `cloture.md`
disent en une ligne où vont les clos, en pointant `vlp.py` — sans recopier sa mécanique.

**Critère de fin**
Avant/après affichés : index 104 → < 80 lignes ; clos dans l'index 63 → 0, dans l'archive
0 → 63 ; `renvois` 0 absent ; `recompter` : la ligne `RECOMPTE` **identique** avant et
après. `vlp.py archiver .` relancé : `ARCHIVÉ 0`.
<!-- /FICHE -->
