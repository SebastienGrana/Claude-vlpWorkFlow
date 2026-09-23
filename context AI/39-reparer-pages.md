> **QUAND LIRE** : on joue une fiche `REP*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache REP<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier REP — Réparer les pages publiées

**À quoi il sert.** Les feuilles de route affichent du Markdown brut et deux liens cassés
(`38-audit-artefacts.md` § 2.1 ; chantier A de son § 4). REP les répare dans `vlp.py`,
puis sur les cinq projets équipés par `niveau --ecrire` — aucune page réécrite à la main.

**Fait.** Rien. Ouvert le 2026-09-23, cadré en 4 fiches, `REP1` à jouer.

## Le socle commun

Code : `scripts/vlp.py`. Tests : `scripts/test-vlp.py` — `verifier(nom, cond, sortie)`,
`appel(argv)` ; `py scripts/test-vlp.py` imprime `OK`, et le compte de `verifier(`
(`grep -c`) se donne avant → après. Lignes relevées le 2026-09-23 : elles bougent dès
`REP1`, se fier au nom.

| Symbole | Ligne | Ce qu'il fait aujourd'hui |
|---|---|---|
| `esc(texte)` | 683 | échappe `&`, `<`, `>` — pas `"` |
| `CODE` | 994 | la regex du `` `code` `` |
| `champ(lignes, nom)` | 1063 | la valeur d'une ligne `- **nom** : …` de `CHANTIER.md`, telle quelle, chevrons compris |
| `cellule_md(texte)` | 1092 | `esc`, puis `` `x` `` → `<span class="mono">x</span>` ; rien d'autre |
| `zone(html, nom, ouvre, ferme)` | 1116 | les bornes du contenu d'une `ZONE:` |
| `feuille(projet, html, todo, date)` | 1128 | régénère `ZONE:todo` et `ZONE:encours` ; lien du chantier en cours : `esc(url)`, 1142 |
| `RANG_CLOS`, `lignes_clos` | 1209, 1214 | les `<tr>` de `ZONE:clos`, à dix espaces ; aucun script ne les réécrit |
| `migrer_feuille(html)` | 1241 | une migration de la feuille en place : le modèle à suivre |
| `cmd_niveau` | 1341 | `ÉCART:` sans `--ecrire`, `CORRIGÉ:` avec ; la feuille : 1370–1404 |
| `cmd_clore` | 1482 | la ligne close : `'<a href="%s">' % esc(url)`, 1605 |
| `cmd_ouvrir` | 1661 | écrit `--artefact` tel quel dans `CHANTIER.md`, 1683 |

**Les trois compteurs** — ce qui dit « fini ». Sur la feuille, dans ses trois zones
(`todo`, `encours`, `clos`), en occurrences :

1. `**` hors `<span class="mono">` ;
2. liens Markdown : `](http` hors `<span class="mono">` ;
3. liens cassés : `href="&lt;`.

`niveau` les affiche toujours, même à zéro, sur une ligne à lui (`REP3`) :
`MARKDOWN <a> ** · <b> liens Markdown · <c> liens cassés — <page>`.

**Invariants.**

- Un `**` ou un `[t](u)` dans un `<span class="mono">` est du code cité : ni converti, ni compté.
- Un lien Markdown ne devient `<a>` que vers `http://` ou `https://`.
- Convertir est idempotent : deux passes = une ; `niveau --ecrire` peut repasser.
- Aucune perte : du texte visible, seules les marques Markdown (`**`, `[`, `](URL)`)
  disparaissent, et chaque URL retirée se retrouve dans un `href`.
- La page se régénère par script, jamais à la main (`methode-chantier.md`).
- Une feuille hors de git (le contexte de Cairn) se copie en `.avant-REP` avant d'écrire.
- Aucun commit ailleurs que dans le kit ; dans les autres projets, ne toucher que la
  feuille : du travail non commité y attend.

**Dehors, et pourquoi.**

- Cairn : pages 23 (bilan jamais affiché), 24 (hors gabarit), 27 (enveloppe claude.ai),
  rangs ✅ 13 et 15 de sa TODO, six lignes closes sans accents. `REP4` les signale ;
  les corriger serait écrire une page à la main.
- L'encodage des gabarits (`meta charset`), la longueur des pages : chantiers `PLI`, `FEU`.
- Les notes et le journal des pages de chantier : chantier `ABR`.
- `rejeu.py` reste dans `38-audit-scripts/` : il code Cairn en dur. Ses compteurs
  passent dans `niveau` — choix du cadrage, ✅ validé le 2026-09-23.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `REP1` | Convertir le gras et les liens Markdown dans `cellule_md` | rien |
| `REP2` | Retirer les chevrons d'une URL, à la lecture et à l'écriture | rien |
| `REP3` | Compter le Markdown brut et migrer `ZONE:clos` dans `niveau` | `REP1`, `REP2` |
| `REP4` | Remettre les cinq feuilles de route à niveau, et les republier | `REP3` |

`REP1` et `REP2` touchent deux fonctions distinctes : l'ordre entre elles est libre.
`REP3` réutilise les deux ; `REP4` ne touche plus au code.

---

<!-- FICHE:REP1 -->
## REP1 [x] — Convertir le gras et les liens Markdown dans `cellule_md`

**Session** : da8e3b04-adf4-426a-a7b1-3087bacb5724
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
`cellule_md` échappe puis ne convertit que le `` `code` `` : un `**gras**` ou un
`[titre](https://…)` de la TODO s'affiche tel quel sur la feuille de route.

Écris `gras_et_liens(html)`, qui prend du texte **déjà échappé** — c'est ce qui
permettra à `REP3` de la rejouer sur une ligne close déjà écrite — et rend :

- `**x**` → `<strong>x</strong>`, même quand `x` contient un `<span class="mono">` ;
- `[t](u)` → `<a href="u">t</a>`, si `u` commence par `http://` ou `https://` ;
- tout le reste tel quel, et rien à l'intérieur d'un `<span class="mono">…</span>`.

`cellule_md` l'appelle après la conversion du code. Respecte les invariants du socle.

Un `verifier` par cas : un gras ; deux gras dans une cellule ; un `**` sans paire
(inchangé) ; un gras qui contient un `` `code` `` ; un `**` dans un `` `code` ``
(inchangé) ; un lien `https` ; un lien `javascript:` (inchangé) ; un lien dans un
`` `code` `` (inchangé) ; deux passes = une.

**Critère de fin**
`py scripts/test-vlp.py` imprime `OK` ; `grep -c "verifier(" scripts/test-vlp.py`
avant → après, au moins neuf de plus.
<!-- /FICHE -->

---

<!-- FICHE:REP2 -->
## REP2 [ ] — Retirer les chevrons d'une URL, à la lecture et à l'écriture

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Une URL écrite entre chevrons dans `CHANTIER.md` — `<https://…>`, une forme
Markdown courante (exemple relevé par l'audit : `MapDecorator/CHANTIER.md:16`) —
sort de `champ` telle quelle, puis `esc` en fait `href="&lt;https://…&gt;"` : le
lien ne mène nulle part. `cmd_ouvrir` écrit de même `--artefact` tel quel.

- `champ` : une valeur qui est **entièrement** `<http://…>` ou `<https://…>` se
  rend sans ses chevrons ; toute autre valeur, telle quelle.
- `cmd_ouvrir` : retire ces chevrons de `--artefact` avant d'écrire.
- Ne réécris aucun `CHANTIER.md` existant : lu par `champ`, il suffit.

Un `verifier` par cas : `champ` sur `<https://a/b>`, sur `https://a/b`, sur
`<contexte>` (inchangé) ; `ouvrir --artefact "<https://a/b>"` sur un projet
temporaire écrit `https://a/b` ; puis `feuille` y rend `href="https://a/b"` et
aucun `href="&lt;`.

**Critère de fin**
`py scripts/test-vlp.py` imprime `OK` ; `grep -c "verifier(" scripts/test-vlp.py`
avant → après, au moins cinq de plus.
<!-- /FICHE -->

---

<!-- FICHE:REP3 -->
## REP3 [ ] — Compter le Markdown brut et migrer `ZONE:clos` dans `niveau`

**Dépend de** : `REP1`, `REP2`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Après `REP1` et `REP2`, `niveau --ecrire` régénère proprement `ZONE:todo` et
`ZONE:encours`. Mais une ligne de `ZONE:clos` est écrite une fois par `clore`,
puis recopiée telle quelle : son Markdown brut et son `href="&lt;…&gt;"` (Cairn,
une de ses lignes closes) y resteraient pour toujours.

Dans `cmd_niveau`, sur la feuille régénérée :

- affiche toujours la ligne des trois compteurs du socle ; une `ÉCART: feuille:`
  de plus s'ils ne sont pas tous nuls ;
- avec `--ecrire`, migre `ZONE:clos` en place, sur le modèle de `migrer_feuille` :
  chaque ligne passe par `gras_et_liens`, `href="&lt;URL&gt;"` devient
  `href="URL"`, l'indentation à dix espaces est gardée (`RANG_CLOS`) ; puis
  `CORRIGÉ: feuille: <n> lignes closes converties`.

Tests, sur une feuille temporaire dont une ligne close porte `**x**`,
`[t](https://u)` et `href="&lt;https://v&gt;"` : `niveau` compte 2 · 1 · 1 ;
après `--ecrire`, 0 · 0 · 0 ; le texte visible (balises retirées) n'a perdu que
les marques Markdown, et `u` et `v` sont dans des `href` ; une seconde passe
`--ecrire` n'écrit rien ; `clore` y ajoute encore sa ligne.

**Critère de fin**
`py scripts/test-vlp.py` imprime `OK` ; `grep -c "verifier(" scripts/test-vlp.py`
avant → après, au moins cinq de plus.
<!-- /FICHE -->

---

<!-- FICHE:REP4 -->
## REP4 [ ] — Remettre les cinq feuilles de route à niveau, et les republier

**Dépend de** : `REP3`.
**Fichiers** : la feuille de route seule, `<contexte>/artefacts/feuille-de-route.html`,
du kit (`.`) et des quatre projets voisins : `../Cairn-VlpLib`, `../MapDecorator`,
`../TrackGen`, `../ProjetONZSM`. Rien d'autre.

**Prompt**
Pour chaque projet, dans cet ordre :

1. `git status --short` sur sa feuille. Déjà modifiée et non commitée : arrête-toi,
   `BLOQUÉE` — elle n'est pas à toi. Hors de git (Cairn) : copie-la d'abord en
   `feuille-de-route.html.avant-REP`, à côté.
2. `py scripts/vlp.py niveau <projet>` : la ligne `MARKDOWN`, avant. Un autre
   écart que ceux de la feuille : n'écris rien dans ce projet, signale-le.
3. `py scripts/vlp.py niveau <projet> --ecrire`, puis `niveau` encore : après.
4. Feuille changée : `Artifact` `read` sur l'URL de sa ligne « artefact feuille
   de route » (`CHANTIER.md` du projet), puis republie le fichier local avec
   cette `url`, `label` « REP : Markdown et liens réparés ».

Rends un tableau : projet · compteurs avant · après · republiée. Compare les
« avant » à ceux de l'audit (`38-audit-artefacts.md` § 2.1) : un écart se dit, il
ne se corrige pas en silence. Signale, sans y toucher, ce que le socle met dehors.
Aucun commit hors du kit : dis quels dépôts gardent une feuille à commiter.

**Critère de fin**
Sur les cinq projets, la ligne `MARKDOWN` de `niveau` dit `0 ** · 0 liens Markdown
· 0 liens cassés`, les comptes d'avant à côté ; chaque feuille changée est
republiée (URL et version dans le tableau).
<!-- /FICHE -->
