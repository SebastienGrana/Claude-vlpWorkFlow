> **QUAND LIRE** : on joue une fiche `HAB*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache HAB<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier HAB — Repeindre une page sans recompter

**À quoi il sert.** 90 pages de chantiers clos sont à l'ancien format (67 du kit, 23 de
Cairn) ; `vlp.py page` les repeindrait, mais recompte leur coût. HAB repeint la forme seule,
chiffres inscrits gardés, et remet les pages en ligne par lots.

**Estimé.** 2 fiches · ≈8,09 $ — ≈4,05 $/fiche sur 67 clos (le 2026-09-27).

**CLOS** le 2026-09-27. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** HAB1..HAB6 (2026-09-27) : vlp.py page --forme et repeindre : 64 pages du kit et 17 de Cairn au format PLI, chiffres inchangés, toutes remises en ligne ; liens tirés dans chaque .md par vlp.py liens — estimé 2 fiches ≈8,09 $ · cadré 6 · joué 6 fiches ≈68 $.

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356

## Le socle commun

Mesuré au cadrage (2026-09-27) : `grep -L 'href="vlp.css"' "context AI/artefacts/"*.html`
→ kit 71 pages, 67 sans ; Cairn 26, 23 sans. Les liens des pages closes sont dans la
`ZONE:clos` de la feuille de route locale (`<a href="https://claude.ai/artifact/…">`) :
66 distincts (kit), 17 (Cairn) ; `Artifact` `list` s'arrête à 50, titrés « vlp — <titre> ».
Republier la feuille au cadrage : refusé tant que le fichier sauvé par `read` n'est pas lu
en entier (521 lignes), puis un second `read` — le coût d'une page, à mesurer en `HAB4`.

| Symbole | `scripts/vlp.py` | Ce qu'il fait |
|---|---|---|
| `cmd_page` | `:2464` | lit l'abri, appelle `regenerer`, remonte le bilan, écrit |
| `regenerer` | `:2241` | migre le style (`migrer_style`), replie fiches et journal ; **recompte** : `heures_commits` + `couts` (`:2253`–`:2257`) |
| `lis_page` | `:1879` | `{id: (état, note, coût html)}` d'une page, deux formes |
| `cout-total` / `cout-hors` | `:2251`, `:2281` | les `<p class="mono cout-…">` du total et du hors fiches |
| `chemin_abri`, `lire_abri`, `texte_abri` | `:2357`–`:2410` | le `.md` d'une page : Résultat, Notes, Journal, Bilan |
| `page_du_fichier` | `:2458` | fiches `NN-x.md` → `artefacts/NN-x.html` |
| `cmd_recompter` | `:2930` | parcourt `ZONE:clos` + l'index → fichier de fiches de chaque clos (`:2948`–`:2961`) |
| `vigile <fichier>` | docstring `:256` | `PAGE SAINE` ou `GARDE:` |
| `comparer <a> <b>` | docstring `:126` | `PERDU:` / `AJOUTÉ:` du texte visible |

- **`--forme`** : la forme de `regenerer`, sans `heures_commits` ni `couts` — coût de chaque
  fiche, `cout-total` et `cout-hors` recopiés tels quels de l'ancienne page.
- Le lien en ligne d'une page vit **dans son `.md`** (une section `## Lien`), nulle part ailleurs.
- Une page sans lien retrouvé : repeinte sur le disque, listée « sans lien », pas publiée.
- Republier : `Artifact` `read` sur le lien, `comparer` à la page en ligne (pas au disque),
  puis publish avec `url` et `files: vlp.css`. Par lots de ~15, `/clear` entre deux.
- Cairn est privé : rien de son contenu dans ce dépôt — comptes et noms de fichier seuls.
- Tests dans `scripts/test-vlp.py`, sur un projet bâti en dossier temporaire ; un `with`
  neuf ne réemploie pas la variable `t` d'un voisin.
- Dehors : le recompte des coûts (chantier `ECA`), la feuille de route (`FEU`).

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `HAB1` | Écrire `page --forme`, testé | rien |
| `HAB2` | Écrire `vlp.py repeindre <projet>` | `HAB1` |
| `HAB3` | Retrouver les liens en ligne | `HAB2` |
| `HAB4` | Kit : repeindre, et un premier lot en ligne mesuré | `HAB3` |
| `HAB5` | Kit : les lots suivants | `HAB4` |
| `HAB6` | Cairn : repeindre et remettre en ligne | `HAB4` |

Tout est en série jusqu'à `HAB4` ; `HAB5` et `HAB6` se jouent dans l'ordre qu'on veut, et
se redécoupent en lots selon la mesure de `HAB4`.

---

<!-- FICHE:HAB1 -->
## HAB1 [x] — Écrire `page --forme`, testé

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Ajoute l'option `--forme` à la sous-commande `page`. Avec elle, `regenerer` fait tout son
travail de forme (style lié, fiches et journal repliés, bilan en haut) mais n'appelle ni
`heures_commits` ni `couts` : le coût de chaque fiche vient de `lis_page` sur l'ancienne
page, et les lignes `cout-total` et `cout-hors` sont recopiées telles quelles. `--forme`
refuse `--creer` par une `GARDE:`. Mets à jour la docstring de `page`.

**Critère de fin**
Un test bâtit une page à l'ancien format (`<style>` inline, fiches non repliées, bilan en
bas) avec un total `11 262 523` et deux coûts de fiche, dans un dépôt Git temporaire dont
les commits de fiche feraient changer le coût. Après `page --forme` : le total et les deux
coûts sont identiques (comptes affichés), la page lie `vlp.css`, a ses `<details>` et son
bilan en haut, `vigile` dit `PAGE SAINE`. Mutant : `--forme` ignoré → le test du total tombe.
<!-- /FICHE -->

---

<!-- FICHE:HAB2 -->
## HAB2 [x] — Écrire `vlp.py repeindre <projet>`

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356
**Dépend de** : `HAB1`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Ajoute la sous-commande `repeindre <projet>` : chaque chantier clos (même parcours que
`cmd_recompter` — mets ce parcours en commun, ne le recopie pas) dont la page ne lie pas
encore `vlp.css` passe par `page --forme`, puis par `vigile`. Une ligne par page :
`REPEINTE <page> · lien <url>` ou `· sans lien` (lu dans la section `## Lien` du `.md`,
absente pour l'instant), ou `GARDE:` si `vigile` la refuse. Puis
`REPEINDRE <n> repeintes · <n> avec lien · <n> sans lien · <n> refusées`. `--a-blanc`
n'écrit rien. Déjà au format : ignorée, comptée `<n> déjà`.

**Critère de fin**
Un test bâtit un projet temporaire à trois clos (deux anciens, un déjà au format) : la
sortie dit `2 repeintes · 0 avec lien · 2 sans lien · 0 refusées` et `1 déjà` ; relancé, `0
repeintes`. `--a-blanc` ne change aucun octet. Mutant : ne pas filtrer les pages déjà au
format → le compte `déjà` tombe.
<!-- /FICHE -->

---

<!-- FICHE:HAB3 -->
## HAB3 [x] — Retrouver les liens en ligne

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356
**Dépend de** : `HAB2`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, les `.md` de `context AI/artefacts/`
du kit et de `../Cairn-VlpLib` — et rien d'autre.

**Prompt**
Ajoute à l'abri une section `## Lien` (une ligne, l'URL) : `lire_abri` et `texte_abri` la
lisent et l'écrivent, un `.md` sans elle reste valide. Ajoute `vlp.py lien <page.html>
<url>` qui l'écrit (crée l'abri par `abri_de_page` s'il manque), et `vlp.py liens
<projet>` qui les tire tous de la `ZONE:clos` de la feuille (lien de la ligne → page par sa
plage de fiches, comme `cmd_recompter`). Pour les pages restées sans lien : `Artifact`
`list` (titre = `<h1>`) ; un titre qui matche deux artefacts : ne l'écris pas, liste-le.

**Critère de fin**
Test : `lien` écrit l'URL, `lire_abri` la relit, les autres sections sont intactes ; mutant :
`texte_abri` qui oublie la section → le test tombe. Puis `repeindre --a-blanc` sur les deux
projets : compte brut « avec lien / sans lien » de chacun, et la liste des doublons.
<!-- /FICHE -->

---

<!-- FICHE:HAB4 -->
## HAB4 [x] — Kit : repeindre, et un premier lot en ligne mesuré

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356
**Dépend de** : `HAB3`.
**Fichiers** : `context AI/artefacts/` du kit — et rien d'autre.

**Prompt**
Lance `repeindre .` pour de vrai et commite les pages repeintes. Puis prends les 15 premières
pages « avec lien » : pour chacune, `Artifact` `read` sur son lien, `comparer` la version
en ligne à la page repeinte (un `PERDU:` arrête la page : ne la publie pas, note-la), puis
publish avec `url` et `files: vlp.css`, `label` `HAB : repeinte`. Mesure la session par
`mesure-tokens.py` et note le coût du lot et le coût par page.

**Critère de fin** (visuel)
La sortie de `repeindre` (comptes bruts), le nombre de pages publiées, arrêtées et le coût
du lot sont écrits dans la fiche ; tu ouvres une page repeinte en ligne et tu dis si elle
est lisible. La taille des lots suivants se fixe sur ce coût.
<!-- /FICHE -->

---

<!-- FICHE:HAB5 -->
## HAB5 [x] — Kit : les lots suivants

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356
**Dépend de** : `HAB4`.
**Fichiers** : `context AI/artefacts/` du kit — et rien d'autre.

**Prompt**
Redécoupe d'abord cette fiche en lots, à la taille que la mesure de `HAB4` a fixée (une
session par lot, `/clear` entre deux). Chaque lot suit la même boucle que `HAB4` : `read`,
`comparer`, publish, pages arrêtées notées.

**Critère de fin**
`repeindre . --a-blanc` dit `0 repeintes` ; chaque page « avec lien » du kit est publiée ou
notée arrêtée, comptes bruts : publiées, arrêtées, sans lien.
<!-- /FICHE -->

---

<!-- FICHE:HAB6 -->
## HAB6 [x] — Cairn : repeindre et remettre en ligne

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356
**Dépend de** : `HAB4`.
**Fichiers** : `../Cairn-VlpLib/context AI/artefacts/` — et rien d'autre.

**Prompt**
Même chemin que `HAB4` puis `HAB5`, sur `../Cairn-VlpLib` : `repeindre`, commit dans le
dépôt de Cairn, lots en ligne à la taille fixée par `HAB4`. Rien du contenu de Cairn
n'entre dans ce dépôt : ici, seulement des comptes.

**Critère de fin**
`repeindre ../Cairn-VlpLib --a-blanc` dit `0 repeintes` ; comptes bruts publiées, arrêtées,
sans lien, écrits dans cette fiche.
<!-- /FICHE -->
