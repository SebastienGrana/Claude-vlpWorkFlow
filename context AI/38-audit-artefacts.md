> **QUAND LIRE** : on choisit un chantier sur les pages publiées (artefacts),
> ou on cherche la preuve d'un défaut de page relevé le 2026-09-22. Pas besoin
> de ce fichier pour jouer une fiche : chaque chantier aura le sien.

# Audit des pages publiées — 2026-09-23

Terrain : les 17 pages de Cairn (16 chantiers + la feuille de route).
Cible : le kit, qui les fabrique (`ARTEFACTS.md`, les deux gabarits,
`vlp.py page`, `vlp.py feuille`, `vlp.py clore`). Rien n'a été modifié : audit seul.
Page publiée : <https://claude.ai/artifact/UaMrYTA1WGhJ9z1QSm2MPD> (privée).

Statuts : ✅ établi (source citée) · 🟡 à décider ou à prouver · 💡 proposé.

## En résumé

- Les pages publiées de Cairn marchent bien quand elles sont neuves.
- Mais elles deviennent trop longues : la feuille de route fait 13 écrans sur
  ordinateur, 20 sur téléphone. Et trois défauts s'y voient aujourd'hui.
- Je propose six chantiers : réparer, limiter la longueur des notes, puis rendre
  les pages lisibles avec des blocs repliables et un sommaire.
- Ces chantiers coûtent plus de tokens qu'ils n'en font gagner : leur intérêt est
  la lisibilité, pas l'économie.
- Deux relecteurs ont vérifié l'audit ; leurs corrections sont intégrées.

## Sommaire

| § | Section | Ce qu'on y trouve |
|---|---|---|
| 0 | En une minute | les cinq constats principaux |
| 1 | Comment c'est mesuré | les commandes pour rejouer chaque chiffre |
| 2 | Constats | 2.1 ce qui est cassé · 2.2 longueur, ordinateur et téléphone · 2.3 dyslexie · 2.4 tes cinq axes · 2.5 coût · 2.6 ce qui va bien |
| 3 | Ce qui existe | ce qu'une page sait faire, ce qu'elle ne peut pas faire |
| 4 | Propositions | les six chantiers A à F, leur ordre, leur coût ; ce qui est écarté |
| 5 | Relecture critique | ma propre relecture, et ce qu'elle a changé |
| 6 | Contre-expertise | la relecture du sous-agent, point par point |
| 7 | Sources web | les liens, leur date, leur rang |
| 8 | Annexe | les scripts de mesure |

## 0. En une minute

- ❌ **Trois défauts visibles aujourd'hui** sur la feuille de route de Cairn :
  426 `**` de Markdown affichés tels quels, un lien cassé, deux lignes ✅ restées dans la TODO.
  Le même lien cassé existe chez MapDecorator.
- ❌ **Trop long** quand un chantier grossit : sur ordinateur, la feuille fait
  13,1 écrans et la page du plus gros chantier 9,0 (sur téléphone : 19,6 et 20,3) ;
  et son bilan est tout en bas.
- ❌ **Tes cinq axes sont à zéro** : aucun sommaire, aucun bouton, aucun
  graphique ; un seul bloc repliable sur 17 pages.
- 💰 **Relire les pages coûte** 17 à 23 M tokens de poids réel à Cairn, soit 1,2 à
  1,65 % de ses sessions principales — et la feuille de route pèse de plus en plus
  lourd. Ma première estimation (41,8 M) comptait environ le double : la
  contre-expertise l'a relevé, le rejeu l'a confirmé (§ 6).
- 💡 **Six chantiers proposés**, ~20 fiches : réparer, borner la page par script,
  un essai de fichier joint, rendre lisibles les deux pages, puis des boutons.
- ⚠️ **Ils ne se remboursent pas en tokens** : le plan coûte plus que tout ce que
  les relectures ont coûté à Cairn. Leur but est la lisibilité. Le levier le moins
  cher : faire respecter par script la règle « une ligne par fiche ».

## 1. Comment c'est mesuré — tout est rejouable

| Mesure | Commande |
|---|---|
| Chiffres tirés des fichiers (tailles, balises, `**`, liens, bilans) | `python rejeu.py <racine ProgPerso>` |
| Hauteur en écrans d'ordinateur (1536 × 864) | navigateur intégré à cette taille, une page à la fois : `scrollHeight / innerHeight` |
| Hauteur en écrans de téléphone (375 × 812) | navigateur intégré en mode téléphone, une page à la fois, après `await document.fonts.ready` : `document.documentElement.scrollHeight / 812` |
| Coût d'une lecture de page | `python cout_lecture.py <dossier des transcriptions de Cairn>` |
| Poids réel (lecture × tours restants) | `python poids_reel.py <même dossier>` |
| Biais du coût : tours partagés, compactage, sous-agents, lectures doubles | `python ce_biais.py <même dossier>`, `ce_poids2.py`, `ce_double.py` (écrits par la contre-expertise) |
| Lectures de la feuille une par une ; coût par fiche du kit | `python feuille_detail.py <même dossier> <racine ProgPerso>` |

- Les scripts sont rangés à côté de ce fichier, dans `38-audit-scripts/` (§ 8),
  Python 3 sans dépendance.
- Méthode du coût : écart de contexte (`input` + `cache_creation` + `cache_read`)
  entre le message qui appelle `Artifact read` et le message suivant.
- ⚠️ Limites : cet écart contient aussi le texte glissé entre deux tours (rappels
  système) et, quand la lecture partage son tour avec d'autres outils, leurs
  résultats. § 2.5 donne la fourchette corrigée.

## 2. Constats

### 2.1 Ce qui est cassé ❌

| Défaut | Preuve | Cause |
|---|---|---|
| 426 `**` affichés tels quels dans la TODO | `rejeu.py` : `etoiles_markdown 426` ; version publiée identique (lue le 2026-09-22) | `cellule_md` ne convertit que les `` `code` `` — `scripts/vlp.py:1092` |
| 1 lien Markdown brut `[ses fiches](https://…)` | `liens_markdown 1` | même cause |
| Lien cassé `href="&lt;https://…&gt;"` sur une ligne de chantier clos | `href_chevrons 1` | une URL écrite entre chevrons dans le champ « artefact du chantier » de `CHANTIER.md` (exemple encore vivant : `MapDecorator/CHANTIER.md:16`) ; `champ()` la rend telle quelle (`scripts/vlp.py:1063`) ; `cmd_clore` l'échappe (`scripts/vlp.py:1605`) ; `ouvrir --artefact` l'écrit telle quelle (`scripts/vlp.py:1683`) |
| MapDecorator : même lien cassé, dans la zone « en cours » de sa feuille | `MapDecorator/context AI/artefacts/feuille-de-route.html:75` (contre-expertise, revérifié) | même cause, par le lien du chantier en cours (`scripts/vlp.py:1142`) |
| Page 23 : chantier clos, bilan jamais affiché | `p23_bilan_cache True` | page d'avant la `ZONE:bilan` remplie par `clore` |
| Page 24 : hors gabarit (aucune `ZONE:`) | `p24_sans_zone True` | page faite à la main avant le gabarit |
| Page 27 : le fichier local contient l'enveloppe de claude.ai (`<!doctype html>…<body>`) | `p27_enveloppe True` | une version lue a été réécrite sur le disque |
| 2 rangs ✅ (faits) restés dans la TODO (rangs 13 et 15) | `todo_rangs_coches 2` | donnée de `10-etat.md`, pas un bug de script |
| Accents perdus dans 6 lignes de chantiers clos (des mots écrits sans leurs accents) | colonne « livré » de six chantiers clos (comptée par script par la contre-expertise) | texte passé à `clore` sans accents |

- ⚠️ Mineur : les gabarits n'ont pas de `<meta charset>` (`gabarits_meta_charset 0`).
  Sur claude.ai, l'enveloppe l'ajoute ; ouvert en local, le fichier s'affiche avec
  des accents cassés (constaté au navigateur).

### 2.2 Longueur — sur ordinateur et sur téléphone ❌

Tu lis surtout sur ordinateur, rarement sur téléphone (dit le 2026-09-23).
Sur un écran d'ordinateur portable courant, 1536 × 864 px (un écran = 864 px) :

| Page | Ordinateur | Téléphone |
|---|---|---|
| feuille de route | **13,1** | 19,6 |
| page 30 | **9,0** (bilan à 8,6) | 20,3 (bilan à 19,7) |
| page 29 | 3,9 | 7,7 |
| page 31 | 3,5 | 7,1 |
| page 41 | 1,4 | 2,35 |

- ❌ Sur ordinateur aussi, la feuille et les gros chantiers sont trop longs, et
  le bilan reste tout en bas. Le problème est environ deux fois plus petit.
- ➡️ Les défauts de **largeur** (tableau qui défile de côté, page 29 qui déborde)
  ne touchent que le téléphone : priorité basse pour toi.

Sur téléphone, 375 × 812 px (un écran = 812 px) :

| Page | Écrans | Fiches | Journal | Bilan à |
|---|---|---|---|---|
| feuille de route | **19,6** | — | — | — |
| page 30 | **20,3** | 27 | 25 | 19,7 écrans |
| page 29 | 7,7 | 9 | 6 | (en pause) |
| page 31 | 7,1 | 9 | 9 | 6,3 |
| médiane des 16 pages de chantier | 4,7 | 6 | 4 | — |
| page 41 | **1,9** neuve (2026-09-22) · 2,35 après sa première fiche (2026-09-23) | 6 | 0 → 1 | — |

- ✅ Une page neuve est propre : 1,9 écran (page 41) ; 2,35 dès sa première
  entrée de journal.
- ❌ Elle se dégrade avec le chantier : notes jusqu'à 375 caractères, entrées de
  journal jusqu'à 619 (page 30). Et plus de 730 caractères dans une note de la
  page 39, un chantier de 6 fiches : ce n'est pas que la taille du chantier.
- ❌ Chantier clos : le bilan — ce qu'on veut lire en premier — est en bas.
- ❌ Feuille de route : la TODO fait **67 %** de la page (34 297 caractères sur
  51 151), 19 lignes de **1 102 à 2 657** caractères chacune (5 cellules,
  balises comprises).
- ❌ Sur téléphone, le tableau de la TODO fait 641 px dans une boîte de 319 px :
  il défile de côté, et la colonne « Dépend de » sort de l'écran.
- ⚠️ La page 29 déborde en largeur sur téléphone (constaté au navigateur :
  496 px de large pour un écran de 375).
- ❌ La garde de taille est muette : elle compte des **lignes**
  (`SEUIL_PAGE = 250`, `scripts/vlp.py:663`). La feuille fait 246 lignes pour
  52 Ko et 19,6 écrans, et `cmd_feuille` n'a aucun seuil (contre-expertise,
  revérifié).

### 2.3 Dyslexie — écarts avec un guide publié ❌

Source : *Dyslexia-Friendly Style Guide*, Ako Aotearoa (centre public
néo-zélandais d'enseignement supérieur), juillet 2023 — il cite le guide 2023 de
la British Dyslexia Association, dont le PDF a refusé l'accès (403).

| Le guide recommande | Nos gabarits | Preuve |
|---|---|---|
| Éviter les majuscules pour des mots entiers et les titres | titres de section, sur-titre et état en majuscules | `templates/artefact-chantier.html:25`, `:26`, `:42` ; `templates/artefact-feuille-de-route.html:36`, `:39`, `:49`, `:54` |
| Titres au moins 20 % plus grands que le texte | titres de section à 0,8 rem, **plus petits** que le texte (1 rem) | `templates/artefact-chantier.html:25` |
| Table des matières dans un long document | aucune (0 page) | `rejeu.py` : `nav_pages_avec 0`, `ancres_pages_avec 0` |
| Paragraphes courts | cellules de TODO jusqu'à 2 657 caractères | § 2.2 |
| Éviter les abréviations, ou les expliquer | codes de fiche (trois lettres et un numéro) jamais développés | lecture des pages |
| Schémas, flèches, icônes pour appuyer le texte | aucun schéma, aucun graphique | `svg_pages_avec 0` |
| Interligne 1,5 · police sans empattement · 12–14 pt ou plus | 1,55 ✅ · Source Sans 3 ✅ · corps 16 px = 12 pt ✅ ; mais notes 0,9 rem, coûts 0,78, état 0,68, titres 0,8, en-têtes de tableau 0,7 ❌ | `templates/artefact-chantier.html:25`, `:39`–`:42` ; `templates/artefact-feuille-de-route.html:49` |

### 2.4 Tes cinq axes — l'état actuel

| Axe | Pages qui l'ont | Commentaire |
|---|---|---|
| Mise en page | — | ✅ propre, thème clair/sombre ; ❌ ne tient pas la longueur (§ 2.2) |
| Blocs repliables | 1 / 17 | seule la table des chantiers clos de la feuille |
| Index (sommaire) | 0 / 17 | aucune ancre |
| Boutons | 0 / 17 | aucun script dans aucune page |
| Graphiques | 0 / 17 | les coûts existent (tokens par fiche, par chantier) mais ne sont que du texte |

### 2.5 Ce que coûte la relecture des pages 💰

Pourquoi ça compte : pour republier, le protocole impose de **lire** la page
d'abord (`ARTEFACTS.md`, « Republier : lire d'abord ») — et cette lecture reste
dans le contexte jusqu'à la fin de la session.

| Mesure (sessions principales de Cairn) | Valeur |
|---|---|
| Lectures de page (`Artifact read`) | **128**, dont 37 dans un tour partagé avec d'autres outils |
| Tokens ajoutés par une lecture | médiane 6 101 (toutes) · **5 379** (lectures seules, n = 91) · max 24 281 (un tour à deux lectures) |
| Poids réel, méthode d'origine (jusqu'à la fin de la session) | 41,8 M · 2,97 % — ❌ surestimé |
| Poids réel, arrêté au premier compactage | **23,2 M** · 1,65 % |
| idem, lectures seules | **17,0 M** · 1,20 % |
| Dénominateur | 1 408 384 645 tokens des sessions principales (rejeu du 2026-09-23) ; les 147 transcriptions de sous-agents (92,0 M) n'y sont pas |
| dont la feuille de route | 37 lectures (23 seules) · 14,8 M en méthode d'origine, donc surestimé |
| Lectures seules de la feuille | +4 796 (première lecture) → +21 383 (dix-sept jours plus tard) : ≈ ×4,5 |
| Ma propre lecture de la feuille (cette session) | +22 798 |
| Part du CSS dans une page de chantier | médiane **37 %** des caractères (pas des tokens) |
| Commentaires du gabarit, recopiés dans chaque page | 1 078 caractères |

- 💰 Corrigé : **17 à 23 M**, soit ≈ 14 à 19 $ au tarif moyen du kit
  (`scripts/vlp.py:691`, 0,8371 $ par million). ⚠️ Encore un **plafond** : ces
  tokens sont surtout des relectures de cache, le poste le moins cher.
- ⚠️ Les deux biais, relevés par la contre-expertise et confirmés par rejeu :
  un tour partagé met tout son écart sur le compte de la page ; une page lue avant
  un compactage ne pèse plus rien après. Le repérage du compactage (chute de
  contexte de plus de 40 %) reste une approximation.
- ⚠️ Le total bouge encore : une session de Cairn tournait pendant l'audit.
- 🟡 Ma lecture du 2026-09-22 a rendu : « the head below is NOT the whole artifact
  […] counts as viewed only once you have Read every line ». Si c'est désormais
  imposé, chaque republication coûtera en plus la lecture du fichier entier.
  Les sessions de Cairn ne l'ont fait que 2 fois sur 128 : à vérifier.
- ⚠️ Un bloc **replié** est lu quand même par le modèle : replier rend lisible,
  pas moins cher.

### 2.6 Ce qui va bien ✅

- La page se régénère par script (`vlp.py page`), jamais à la main.
- `vlp.py page --verifier` compare la page au fichier de fiches.
- Thème clair et sombre complet, jetons de couleur, largeur de lecture tenue.
- Une page neuve tient en 1,9 écran.
- La règle « un artefact ne bloque jamais une fiche » (`ARTEFACTS.md`).

## 3. Ce qui existe — le catalogue

### 3.1 En HTML, sans aucune capacité

| Outil | Ce qu'il fait | Coût à la relecture |
|---|---|---|
| `<details>` / `<summary>` | bloc repliable, sans script | quelques octets |
| `<details name="…">` | accordéon : un seul ouvert à la fois (MDN, § 7) | quelques octets |
| Recherche Ctrl+F dans un bloc replié | le navigateur l'ouvre tout seul — Chrome depuis 2021 (Chromium, § 7) | nul |
| Ancres `#fiches`, `#journal` | sommaire cliquable ; l'URL de l'artefact accepte un `#mot` simple | quelques octets |
| En-tête collant (`position: sticky`) | sommaire toujours visible | quelques octets |
| Boutons + script | tout déplier, filtrer, copier une commande | le script est relu à chaque fiche |
| Graphique SVG dessiné par script | barres des tokens par fiche ou par chantier | idem |
| Mermaid | schéma rendu nativement par claude.ai, sans bibliothèque (contrat de page, § 7) | le texte du schéma |
| `localStorage` | se souvenir d'un filtre, par lecteur | nul |

### 3.2 Les capacités de la plateforme (contrat 0.2.54)

| Capacité | Ce qu'elle fait | Utile au kit ? |
|---|---|---|
| **Fichiers joints** (`files` à la publication) | CSS, JS ou données publiés à côté de la page ; copiables d'un autre artefact **côté serveur** | ✅ **oui** — sortir CSS/JS/données de ce que le modèle relit (chantier C) |
| **`comments`** forme `composer_only` | un bouton « commenter ceci » ouvre le composeur ancré sur l'élément ; aucun consentement, partage public conservé | ✅ **oui** — le canal de retour existe déjà (`ARTEFACTS.md:114`) |
| `comments` forme complète | écrire, répondre, résoudre depuis la page ; « envoyer à Claude » | 🟡 plus tard — demande un consentement ; les visiteurs par lien public n'y ont pas accès |
| `sample` | la page pose une question à Claude (payée par le lecteur) | 🟡 à essayer — un bouton « 🔊 résumer simplement » |
| `db` | base de documents partagée, écrite par `ArtifactData` | ❌ non — seconde source de vérité, et écrite par le modèle, pas par script |
| `artifact` | la page se republie elle-même (sondage, liste) | ❌ non — une TODO modifiée depuis le téléphone ne rejoindrait pas le fichier |
| `files` (projet) | la page lit les fichiers d'un projet Claude Code | 🟡 inconnu — le dossier de contexte n'est pas dans git |
| `downloads`, `assets`, `room`, `user`, `mcp` | fichier à télécharger, stockage, présence, identité, connecteurs | ❌ sans usage ici |
| Types d'artefact | 4 de base : Design, Design System, Docs, Slides (`Artifact list scope:types`, 2026-09-22) | ❌ aucun ne suit un chantier |

### 3.3 Ce que la plateforme refuse

Source : le contrat de page de l'outil Artifact (§ 7).

- `window.print()` : aucun bouton « imprimer » ou « PDF » possible.
- `alert()`, `confirm()`, `prompt()` : inertes.
- Un lien de téléchargement `<a download>` : inerte.
- Intégrer un autre site en `<iframe>` : refusé.
- Un état dans l'URL `#cle=valeur` : refusé (seul `#mot` passe).

## 4. Propositions — six chantiers 💡

Chiffrage : nombre de fiches × coût par fiche des 26 chantiers clos **du kit**
(premier quartile 2,18 M, médiane 2,88 M, troisième quartile 3,65 M ;
`feuille_detail.py`). Une estimation, pas une mesure.

⚠️ **Avant tout : ces chantiers ne se remboursent pas en tokens.** Tout ce que les
relectures de pages ont coûté à Cairn depuis le début fait 17 à 23 M (§ 2.5) ; le
plan complet coûte 44 à 80 M. Leur raison d'être est la **lisibilité** (longueur,
dyslexie). Seuls B et la décision 🟡 de E allègent vraiment.

| Ordre | Chantier | Fiches | Coût estimé | Pourquoi à ce rang |
|---|---|---|---|---|
| A | Réparer ce qui est cassé | ~4 | 8,7 à 14,6 M | défauts visibles, dans 4 projets |
| B | Borner la page par script | ~2 | 4,4 à 7,3 M | le levier le moins cher, pour les écrans **et** le coût |
| C | Essai : le CSS en fichier joint | 1 | 2,2 à 3,7 M | décide où vit le CSS **avant** que D et E le touchent |
| D | La page de chantier plus courte et lisible | ~5 | 10,9 à 18,3 M | après C |
| E | La feuille de route plus courte et lisible | ~4 | 8,7 à 14,6 M | après C ; 🟡 une décision à prendre |
| F | Des boutons (et le CSS joint partout, si C tient) | ~4 à 6 | 8,7 à 21,9 M | en dernier, optionnel |

Total ≈ 20 à 22 fiches, ≈ 44 à 80 M tokens, soit ≈ 37 à 67 $ au tarif moyen du kit.

### A — Réparer ce qui est cassé

- `cellule_md` (`scripts/vlp.py:1092`) : `**x**` → `<strong>`, `[t](u)` → `<a>` ;
  un test par cas.
- Les chevrons d'une URL `<…>` : les retirer à la lecture (`champ()`,
  `scripts/vlp.py:1063`) **et** à l'écriture (`ouvrir --artefact`,
  `scripts/vlp.py:1683`) ; un test.
- Une migration dans `vlp.py niveau` pour les lignes **closes** : aucun script ne
  les réécrit (`feuille()` ne touche que les zones `todo` et `encours`,
  `scripts/vlp.py:1150`, `:1163` ; `clore` recopie les anciennes). Les corriger à
  la main contredirait « la page se régénère ».
- Projets touchés : Cairn (426 `**`, 1 lien Markdown, 1 lien cassé clos),
  TrackGen (4 `**`), ProjetONZSM (2 `**`), MapDecorator (1 lien cassé en cours).
- Signaler, sans réécrire à la main : pages 23 (bilan), 24 (hors gabarit),
  27 (enveloppe claude.ai), rangs ✅ de la TODO, accents perdus.
- Ranger `rejeu.py` dans `scripts/`, étendu aux 5 projets équipés : c'est lui qui
  dit « fini ».
- **Fini quand** : sur les 5 projets, 0 `**`, 0 lien Markdown, 0 `href="&lt;`.

### B — Borner la page par script

Venu de la contre-expertise.

- La règle existe déjà : une fiche « s'y résume à son identifiant, son titre, son
  état et une ligne » (`ARTEFACTS.md:111`). Rien ne la fait respecter (§ 2.2).
- `vlp.py page` : une longueur maximale pour `--note` et `--journal`, avec une
  `GARDE:` au-delà. 🟡 Le nombre est à fixer ; il vivra dans le script (règle 3).
- La garde de taille compte en **caractères**, plus en lignes, et garde aussi la
  feuille.
- **Fini quand** : une note trop longue est refusée par un test ; la feuille de
  Cairn déclenche la garde.

### C — Essai : le CSS en fichier joint (une fiche)

- Publier une page dont le CSS est un fichier joint, la republier, mesurer ce que
  coûte la relecture (avant : médiane 5 379 tokens pour une lecture seule).
- 🟡 **À prouver** : que republier ne demande pas de relire le fichier joint.
- Gain maximal : la part CSS, 37 % des caractères d'une page de chantier.
- Si l'essai tient, D et E écrivent leur CSS dans `vlp.css`, déposé par
  `vlp.py` dans `<contexte>/artefacts/` et joint par `files`. Sinon, il reste en
  ligne. Dans les deux cas, une seule migration.
- Pas d'artefact « kit » séparé : ce serait un troisième artefact, contraire à
  `ARTEFACTS.md:12`. Et l'outil n'accepte comme source qu'un fichier sous le
  dossier de travail : le chemin du plugin ne passe pas, la copie locale si.
- Effet de bord utile : le CSS, recopié aujourd'hui dans les deux gabarits, ne
  vivrait plus qu'à un endroit (règle 3 de `CLAUDE.md`).

### D — La page de chantier plus courte et lisible

Tout en HTML natif : pas de script.

- Chaque fiche dans un `<details>` : identifiant, titre et état visibles ; note
  et coût repliés ; la fiche en cours ouverte. Garder le `<li class="fiche">`
  autour, pour `LI_FICHE` (`scripts/vlp.py:665`).
- Chantier clos : le bilan **monte sous l'en-tête**.
- Journal : les trois dernières entrées visibles, le reste replié. C'est le vrai
  levier : prototype sur la page 30, notes repliées 20,3 → 14,2 écrans, puis
  journal réduit à 3 entrées → **5,4**.
- Un sommaire ; titres sans majuscules, au moins 1,2 fois le texte ; petites
  tailles relevées (§ 2.3).
- ⚠️ **Outil à écrire** : `vlp.py niveau` ne migre aucune page de chantier (il ne
  lance que `page --verifier` sur la page en cours), et `regenerer` ne touche ni
  au CSS ni à la structure. Il faut une migration des pages, et adapter l'ajout
  au journal (`regenerer`) et l'échange bilan/blocage (`clore`).
- **Fini quand** : page 30 régénérée ≈ 5,5 écrans de téléphone (prototype : 5,4 ;
  aujourd'hui : 20,3, soit 9,0 sur ordinateur), bilan visible sans défiler,
  `page --verifier` vert.

### E — La feuille de route plus courte et lisible

- La TODO en **cartes** : une ligne de tête (rang, repères, code, titre, coût,
  dépendance) et la première phrase visibles ; le reste replié.
- Un sommaire ; même typographie que D.
- ⚠️ **Ce qui casse**, à reprendre dans le même chantier : la zone
  `todo` lue entre `<tbody>` et `</tbody>` dans `feuille()` et dans la garde de
  `clore` (`scripts/vlp.py:1150`, `:1622`) ; le motif de la ligne en cours
  (`scripts/vlp.py:1152`) ; `migrer_feuille` ; les feuilles des 5 projets ;
  `rejeu.py`.
- **Fini quand** : feuille de Cairn ≈ 6 écrans de téléphone (prototype : 5,4 en
  tableau replié, 5,9 en cartes ; aujourd'hui : 19,6, soit 13,1 sur ordinateur),
  plus aucun défilement de côté.
- 🟡 **À décider (toi)** : la feuille doit-elle porter **tout** le détail de la
  TODO ? La colonne « Ce qu'il apporte » pèse **58 %** de la page (29 785
  caractères sur 51 151). Sans elle, une lecture passerait d'environ 24 k à
  environ 10 k tokens (règle de trois, donc estimation). Le détail resterait dans
  `10-etat.md`. 💡 La contre-expertise la juge plus rentable que C ; je suis
  d'accord : c'est presque gratuit, et elle allège sans fichier joint.

### F — Des boutons, en dernier

Optionnel. Leur script va dans le fichier joint si C tient ; sinon il reste en
ligne, relu à chaque fiche.

- 💬 « Commenter cette fiche » : `comments` en forme `composer_only`.
- « Tout déplier » / « Tout replier ».
- Filtres : 🔴 🟠 🟡 sur la TODO ; à faire / faites sur les fiches.
- « Copier la commande » : `/vlp:tache <fiche>` dans le presse-papiers.
- Un graphique des tokens par chantier clos, sur la feuille.
- 🟡 Option à essayer : « 🔊 Résumer simplement » (`sample`, payé par le lecteur,
  consentement au premier clic).
- Si C tient : le CSS joint sur les pages des 5 projets (~2 fiches de plus).

### Écarté, et pourquoi

- `db` pour les fiches : seconde source de vérité, écrite par le modèle et non par
  un script (règle 4 de `CLAUDE.md`).
- `artifact` pour modifier la TODO depuis le téléphone : la modification ne
  rejoindrait jamais `10-etat.md`.
- Bouton « imprimer / PDF » : la plateforme l'interdit.
- Bouton « thème sombre » : la plateforme gère déjà le thème.
- Découper une page en plusieurs artefacts : `ARTEFACTS.md:12`, « deux artefacts,
  et pas un de plus ».

🟡 **Pas étudié** : republier moins souvent. `/vlp:tache` republie la page à
chaque fiche (`ARTEFACTS.md:17`). Republier une fois sur deux diviserait les
lectures, mais le lecteur verrait la page avec du retard.

## 5. Relecture critique (étape 2 : moi)

Ce que j'ai remis en cause dans mon propre plan, et ce que ça a changé.
Numérotation d'avant la contre-expertise, reprise aussi au § 6 : 1 = A,
2 = D, 3 = E, 4 = C puis F, 5 = F.

| Question posée au plan | Verdict | Changement |
|---|---|---|
| Mes médianes et comptes écrits à la main sont-ils justes ? | ❌ deux faux : médiane 4,4 au lieu de 4,75 écrans (puis **4,7** au rejeu, ligne suivante), 6,5 au lieu de **6** fiches ; 5 lignes sans accents au lieu de **6** | corrigés, et recomptés par script |
| Mes hauteurs d'écran se rejouent-elles ? | ❌ pas toutes : le 2026-09-23, page 30 20,6 → **20,3**, 29 : 7,8 → 7,7, 31 : 7,2 → 7,1, bilan de 30 : 20,1 → 19,7, médiane 4,75 → **4,7** ; feuille (19,6) et page 41 (1,9) identiques | remesurées en mode téléphone, polices chargées, pages inchangées depuis le 2026-09-22 ; valeurs remplacées. Cause de l'écart inconnue (polices pas encore chargées la première fois ? non prouvé) ; une mesure en iframe donne encore ±0,2 écran |
| Les cibles « ≤ 5 écrans » et « ≤ 4 écrans » sont-elles réalistes ? | ❌ non mesurées | prototype au navigateur : **5,4** et **5,4 à 5,9** ; cibles remplacées |
| Replier allège-t-il la relecture ? | ❌ non : le modèle lit aussi ce qui est replié | lisibilité (2, 3) et coût (4) séparés ; seule l'option « détail hors page » allège sans le chantier 4 |
| Le chantier 4 respecte-t-il « deux artefacts, et pas un de plus » ? | ❌ non, dans ma première version (un artefact « kit ») | copie locale déposée par `vlp.py`, jointe par `files` |
| Un script dans la page est-il gratuit ? | ❌ non : relu à chaque fiche | boutons de préférence après le chantier 4 |
| Où est le vrai volume de la page 30 ? | je pensais aux fiches | c'est le **journal** (25 entrées, jusqu'à 619 caractères) |
| Le bug du Markdown ne touche-t-il que Cairn ? | ❌ non | TrackGen (4) et ProjetONZSM (2) ajoutés au chantier 1 |
| Le « 35 $ » est-il un coût ? | ⚠️ un plafond | écrit comme plafond : surtout des relectures de cache |
| Ma source sur la dyslexie fait-elle autorité ? | ⚠️ à moitié | organisme public, cite le guide BDA 2023 ; le guide BDA lui-même n'a pas pu être lu (403) — dit en § 7 |
| Un bloc `<details>` casse-t-il `vlp.py page --verifier` ? | 🟡 probablement pas | `LI_FICHE` (`scripts/vlp.py:665`) cherche `<li class="fiche" …>…</li>` : garder ce `li` autour du `details` ; à couvrir par un test au chantier 2 |

## 6. Contre-expertise (étape 3 : un sous-agent neuf)

Un sous-agent sans l'historique de la session a relu ce rapport, avec la
consigne de le réfuter (173 832 tokens, 44 appels d'outils). Son verdict : « le
plan tient en partie ». J'ai revérifié chaque point avant de l'intégrer.

| # | Ce qu'il dit | Revérifié | Changement |
|---|---|---|---|
| 1 | Le coût de relecture est surestimé environ du double | ✅ rejoué : 37 tours partagés sur 128 ; 23,2 M arrêté au compactage ; 17,0 M en lectures seules ; 147 transcriptions de sous-agents hors du dénominateur | § 0 et § 2.5 : 17 à 23 M, « sessions principales » |
| 1b | Le max 24 281 est un tour à deux lectures ; « ×5 » choisit ses bornes | ✅ 2 tours à deux lectures ; la première lecture est 4 796 | ≈ ×4,5 entre lectures seules |
| 2 | L'annexe est vide : rien n'est rejouable | ✅ | scripts rangés dans `38-audit-scripts/` (§ 8) |
| 3 | Lien cassé chez MapDecorator ; `CHANTIER.md:24` de Cairn mal cité (champ jamais lu) ; `ouvrir --artefact` oublié | ✅ ligne 75 ; `vlp.py` ne lit que « artefact du chantier » (`:1141`, `:1505`, `:1683`) | § 2.1 et chantier A |
| 4 | Le chantier 1 ne répare pas la ligne close ; page 27 oubliée | ✅ `feuille()` ne réécrit que `todo` et `encours` | A : migration dans `niveau`, page 27 ajoutée |
| 5 | `niveau` ne migre aucune page de chantier ; 3 fiches est optimiste | ✅ | D : outil à écrire, ~5 fiches |
| 5b | Prototype à 20,3 écrans, tableau à 20,6 | ✅ c'est le tableau qui ne se rejouait pas | § 2.2 remesuré, § 5 |
| 6 | Les cartes cassent la zone `todo`, le motif de la ligne en cours, `migrer_feuille` | ✅ `scripts/vlp.py:1150`, `:1152`, `:1622` | listé au chantier E |
| 7 | L'essai doit passer avant 2 et 3 ; le plan ne se rembourse pas | ✅ d'accord | ordre A → F ; avertissement en tête du § 4 |
| 7b | Chiffrage optimiste | ✅ | fiches × quartiles du kit : 44 à 80 M |
| 8 | Garde de taille muette ; règle « une ligne » non tenue ; fréquence de republication non étudiée | ✅ 246 lignes ; `ARTEFACTS.md:111` ; `ARTEFACTS.md:17` | chantier B ; fréquence en question ouverte |
| 9 | « 12 pt conforme » vaut pour le corps seulement | ✅ | § 2.3 |
| 10 | Comptes à reformuler ; page 41 changée après la mesure | ✅ page 41 : 2,35 écrans aujourd'hui | § 2.1, § 2.2 |
| 11 | Le catalogue n'a pas de source | ⚠️ en partie : la source existe (contrat de page de l'outil Artifact, liste des types) mais n'était pas citée | § 3 et § 7 la citent |
| 11b | « Mermaid rendu nativement » douteux | ❌ rejeté : le contrat le dit, par `<pre class="mermaid">` ; invisible en aperçu local, à voir sur la page publiée | — |
| 11c | « forme complète = page interne » extrapolé | ✅ | reformulé en § 3.2 |

Ce qu'il n'a pas pu vérifier : les hauteurs d'écran (remesurées par moi, voir
§ 5), les 641 px dans 319, le débordement de la page 29 (496 px, remesuré),
« 2 fois sur 128 », « version publiée identique ». Ces trois derniers restent
sur ma seule parole.

## 7. Sources web

| Source | Rang | Consultée | Ce qu'elle établit |
|---|---|---|---|
| [Dyslexia-Friendly Style Guide, Ako Aotearoa, juillet 2023 (PDF)](https://ako.ac.nz/assets/Knowledge-centre/ALNACC-Resources/Dyslexia-resources/230907-Dyslexia-Friendly-Style-Guide.pdf) | organisme public | 2026-09-22 | majuscules, taille des titres, sommaire, abréviations, schémas |
| [BDA Dyslexia Style Guide 2023 (PDF)](https://cdn.bdadyslexia.org.uk/uploads/documents/Advice/style-guide/BDA-Style-Guide-2023.pdf) | association de référence | 2026-09-22 | ❌ non lu : accès refusé (403) |
| [MDN, `<details>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/details), modifiée le 2026-04-24 | doc officielle | 2026-09-22 | attribut `name` (accordéon), événement `toggle`, rôle `group` |
| [Chromium, « Intent to Ship: Auto-expand details elements »](https://groups.google.com/a/chromium.org/g/blink-dev/c/a6iO__pqI_E/m/Asj1sUABBAAJ), 2021-09-17 | source primaire | 2026-09-22 | Ctrl+F ouvre un bloc replié ; cible Chrome 96 |
| [Coywolf, auto-expand details](https://coywolf.com/news/seo/details-disclosure-element-can-now-auto-expand-using-the-browsers-find-on-page-feature/) | blog d'actualité | 2026-09-22, extrait de recherche | Firefox 139 et Safari 26.2 — ⚠️ une seule source, secondaire, page non ouverte |
| [GOV.UK Design System, Details](https://design-system.service.gov.uk/components/details/) | design system public | 2026-09-22, extrait de recherche | un seul bloc → Details ; plusieurs → accordéon |
| [Smashing Magazine, tableaux responsives](https://www.smashingmagazine.com/2022/12/accessible-front-end-patterns-responsive-tables-part1/), 2022-12 | magazine | 2026-09-22, extrait de recherche | le motif « cartes empilées » sur téléphone |

Coût web : 4 recherches, 4 pages ouvertes (dont 1 refusée) ; les trois dernières
lignes ne sont connues que par l'extrait du moteur de recherche.

## 8. Annexe — les scripts de mesure

Rangés dans `context AI/38-audit-scripts/`, à côté de ce fichier. Python 3, sans
dépendance, zéro appel modèle.

| Script | Ce qu'il mesure |
|---|---|
| `rejeu.py <racine ProgPerso>` | les 26 valeurs tirées des fichiers de Cairn (§ 2.1 à 2.4) ; écrit `clos.json` |
| `cout_lecture.py <transcriptions>` | l'écart de contexte autour de chaque `Artifact read` ou `publish` |
| `poids_reel.py <transcriptions>` | la méthode d'origine : écart × tours restants (surestimée, § 2.5) |
| `ce_biais.py`, `ce_poids2.py`, `ce_double.py` | les biais relevés par la contre-expertise, et la fourchette corrigée |
| `feuille_detail.py <transcriptions> <racine>` | les 37 lectures de la feuille ; le coût par fiche du kit (§ 4) |

Hauteur d'écran, dans le navigateur intégré en mode téléphone (375 × 812), une
page à la fois :

```js
await document.fonts.ready;
document.documentElement.scrollHeight / 812
```

🟡 À ranger dans `scripts/` si le chantier A reprend `rejeu.py`.
