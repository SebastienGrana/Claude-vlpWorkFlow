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
- Je propose six chantiers : réparer, mettre à l'abri le texte des notes (il
  n'existe aujourd'hui que dans la page), puis rendre les pages lisibles avec des
  blocs repliables et un sommaire.
- Rien n'est coupé : un bloc replié reste dans la page, et Claude y a accès comme
  avant. Plus court, oui ; plus pauvre pour Claude, non.
- Déplié, une page peut rester longue ; replié, elle retombe court : la plus
  grosse page de chantier tient alors en à peine plus d'un écran d'ordinateur
  (1,09, mesuré sur maquette ; un écran = 864 px, l'écran entier, § 1).
- Ces chantiers coûtent plus de tokens qu'ils n'en font gagner : leur intérêt est
  la lisibilité, pas l'économie.
- Trois relecteurs ont vérifié l'audit, le dernier après tes questions du
  2026-09-23 ; ce qui tenait est intégré (§ 6).

## Sommaire

| § | Section | Ce qu'on y trouve |
|---|---|---|
| 0 | En une minute | les cinq constats principaux |
| 1 | Comment c'est mesuré | les commandes pour rejouer chaque chiffre |
| 2 | Constats | 2.1 ce qui est cassé · 2.2 longueur, ordinateur et téléphone · 2.3 dyslexie · 2.4 tes cinq axes · 2.5 coût · 2.6 ce qui n'existe que dans la page · 2.7 ce qui va bien |
| 3 | Ce qui existe | ce qu'une page sait faire, ce qu'elle ne peut pas faire |
| 4 | Propositions | la règle « aucune perte pour Claude » ; les six chantiers A à F, leur ordre, leur coût ; ce qui est écarté |
| 5 | Relecture critique | ma propre relecture, et ce qu'elle a changé |
| 6 | Contre-expertise | les relectures de deux sous-agents neufs, point par point ; le troisième avis en 6 bis |
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
- 🔒 **Aucune perte pour Claude** (ta consigne du 2026-09-23) : aujourd'hui, les
  notes et le journal n'existent **que dans la page** — 0 bloc sur 198 retrouvé en
  entier ailleurs chez Cairn (§ 2.6). Replier ne perd rien, et fait retomber la
  page 30 de 9,0 à 1,1 écran d'ordinateur (maquette, § 4) ; couper perdrait pour
  de bon.
- 💡 **Six chantiers proposés**, ~23 fiches : réparer, mettre notes et journal à
  l'abri dans un `.md`, un essai pour alléger la republication (fichier joint, base
  de données), rendre lisibles les deux pages, puis des boutons.
- ⚠️ **Ils ne se remboursent pas en tokens** : le plan coûte plus que tout ce que
  les relectures ont coûté à Cairn. Leur but est la lisibilité. Ce qui allège sans
  rien faire perdre à Claude reste à l'essai (C) ou à ta décision (E).

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
| Texte d'une page retrouvé ailleurs : notes, journal, TODO (§ 2.6) | `python page_vs_source.py <racine du projet> "context AI"` |
| Nombres d'une page retrouvés ailleurs (§ 2.6) | `python chiffres_vs_source.py <racine du projet> "context AI"` |
| Hauteur repliée : maquettes « telle quelle », « une ligne par fiche », « tout replié » (§ 4) | `python replie.py <artefacts de Cairn> <sortie>`, puis chaque maquette au navigateur, comme ci-dessus |

- Les scripts sont rangés à côté de ce fichier, dans `38-audit-scripts/` (§ 8),
  Python 3 sans dépendance.
- Méthode du coût : écart de contexte (`input` + `cache_creation` + `cache_read`)
  entre le message qui appelle `Artifact read` et le message suivant.
- ⚠️ Limites : cet écart contient aussi le texte glissé entre deux tours (rappels
  système) et, quand la lecture partage son tour avec d'autres outils, leurs
  résultats. § 2.5 donne la fourchette corrigée.
- ⚠️ Unité « écran d'ordinateur » : 864 px, la hauteur de l'**écran entier**
  d'un portable courant, pas ce qu'on voit. Dans claude.ai, la barre des tâches,
  le navigateur et le cadre de la page en prennent une part, non mesurée : les
  vrais nombres d'écrans sont plus grands. D'une page à l'autre, la comparaison
  tient (même unité). 🟡 À mesurer : la hauteur visible d'une page ouverte dans
  claude.ai, sur ton écran.
- ⚠️ Précision : une même page, remesurée le lendemain, a bougé jusqu'à 0,4 écran
  (§ 5, cause non établie) ; d'un montage à l'autre, jusqu'à 1,55 écran (feuille :
  12,5 contre 14,05, § 4). Les décimales ne sont pas significatives, et on ne
  compare que dans un même montage. *Ajouté le 2026-09-23 (troisième avis).*

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
  pas moins cher. C'est aussi ce qui le rend sûr : rien de replié n'est perdu
  pour Claude (§ 2.6).

### 2.6 Ce qui n'existe que dans la page ⚠️

Ta question du 2026-09-23 : rendre les pages plus courtes ferait-il perdre de
l'information à Claude ? Car Claude les lit aussi.

Quand Claude lit une page : pour la republier. La lecture est imposée
(`skills/tache/references/tache-page.md:22`, `skills/enchainer/SKILL.md:105`,
`skills/chantier/SKILL.md:243`, `ARTEFACTS.md:70`), et Claude doit reporter ce
que la version publiée dit de plus que la page locale (`tache-page.md:23`–`:24`).
Et `vlp.py page` garde une note d'une régénération à l'autre en la **relisant
dans la page** elle-même (`scripts/vlp.py:856`, `:864`).

« Ailleurs » : tous les `.md` du dossier de contexte, `CHANTIER.md` et les
messages de commit. Comparaison sans accents, sans casse ni ponctuation.

| Ce que la page contient | Retrouvé en entier ailleurs | Mesure |
|---|---|---|
| Cairn : notes de fiches (118) et entrées de journal (80) | **0 / 198** ; 8 par leur début, 43 par un morceau de 40 caractères | `page_vs_source.py` |
| Le kit lui-même : notes et journal | 6 / 148 | idem |
| MapDecorator : notes et journal | 1 / 11 | idem |
| Les nombres de ces blocs, chez Cairn | 121 des 139 blocs chiffrés ont au moins la moitié de leurs nombres qui réapparaissent ailleurs — n'importe où, dates comprises ; sans les dates, 119 / 138 ; nombres d'au moins 1 000 seuls, 90 / 107 | `chiffres_vs_source.py` ; les deux variantes : troisième avis (§ 6 bis) |
| TODO de la feuille : Cairn, TrackGen, ProjetONZSM | ✅ **19 / 19**, 11 / 11, 8 / 8 rangs, chaque cellule entière (Cairn : dans `10-etat.md`) | `page_vs_source.py` |

- ❌ Les notes et le journal n'existent, en entier, **que dans la page** : le
  fichier local et ses versions publiées. Le dossier de contexte de Cairn n'est
  même pas suivi par git (`Cairn-VlpLib/.gitignore:13`), celui de MapDecorator
  non plus (0 fichier suivi) : pas d'historique.
- ❌ Pour le journal, une règle non appliquée : une entrée doit être « la
  **même ligne** que celle ajoutée au fichier d'état » (`tache-page.md:14`–`:15`).
  Chez Cairn : 0 entrée sur 80 retrouvée en entier.
- ⚠️ Pour les notes, un trou de conception, pas un écart : « La page dérive du
  fichier de fiches, jamais l'inverse » ne vise que les états, l'avancement, le
  comptage, les coûts et la date (`tache-page.md:5`–`:7`) ; la note est une option
  de jugement (`:10`–`:13`), que rien n'écrit ailleurs. *Corrigé le 2026-09-23
  (troisième avis) : ce point disait « l'inverse de la doctrine » pour les deux.*
- ➡️ Les faits chiffrés survivent en bonne partie ailleurs ; le texte qui les
  relie, non.
- ✅ La feuille de route, elle, est une vraie copie : sa TODO se retrouve en entier
  dans les fichiers d'état.
- ➡️ Conséquence : **replier ne perd rien** (le texte reste dans le HTML ; ce que
  Claude en lit dépend de la lecture, 🟡 § 2.5) ; **couper une note, ou reconstruire une page sans reprendre ses notes,
  la perd pour de bon**. Les chantiers B, D et E en tiennent compte (§ 4).
- ⚠️ Limites : les transcriptions de session contiennent aussi ce texte, mais
  Claude ne les relit pas en travail normal. Et la comparaison rate un texte
  reformulé : « absent » veut dire « pas recopié », pas « jamais dit ».

### 2.7 Ce qui va bien ✅

- La page se régénère par script (`vlp.py page`), jamais à la main.
- `vlp.py page --verifier` compare la page au fichier de fiches.
- Thème clair et sombre complet, jetons de couleur, largeur de lecture tenue.
- Une page neuve tient en 1,9 écran de téléphone (§ 2.2). Et repliée, même la plus
  grosse retombe plus bas qu'une page neuve, dans un même montage (maquettes,
  § 4) : page 30 tout repliée, 1,42 écran de téléphone contre 2,28 pour la page 41
  neuve telle quelle ; 1,09 contre 1,43 sur ordinateur.
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
| `db` | base de documents rattachée à la page, hébergée par claude.ai (rien à installer) ; écrite par l'outil `ArtifactData`, qui accepte un fichier JSON local | 🟡 à essayer, après B (chantier C) — une écriture ne demande pas de relire la page ; mais la page ne s'affiche plus sans la base |
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
plan complet coûte 48 à 88 M. Leur raison d'être est la **lisibilité** (longueur,
dyslexie). Seuls l'essai C, s'il tient, et l'option 🟡 de E allègent vraiment.

🔒 **Règle posée le 2026-09-23 : plus court, jamais au prix d'une information que
Claude relit.** Chaque chantier passé à ce crible :

| Chantier | Ce qui sort de ce que Claude lit |
|---|---|
| A · réparer | rien |
| B · mettre à l'abri | rien : le texte gagne une copie dans un `.md` |
| C · alléger la republication | le CSS (de la présentation, pas de l'information) ; la base de données seulement **après** B |
| D · page de chantier | rien : replié, le texte reste dans le HTML |
| E · feuille de route | rien en cartes repliées ; l'option 🟡 « sortir le détail » ne perd rien pour Claude (il est entier dans `10-etat.md`), mais toi, tu ne le verrais plus sur la page |
| F · boutons | rien |

Ta seconde consigne, même jour : **déplié, une page peut être aussi longue qu'il
faut ; replié, elle doit retomber court.** Mesuré sur des maquettes
(`replie.py`), aucune ne perdant un mot. En écrans :

| Page | Écran | Telle quelle | Une ligne par fiche, ou cartes | Tout replié |
|---|---|---|---|---|
| page 30 (27 fiches) | ordinateur | 9,02 | 3,19 | **1,09** |
| | téléphone | 19,24 | 6,08 | **1,42** |
| page 41 (neuve) | ordinateur | 1,43 | — | 1,00 |
| | téléphone | 2,28 | — | 1,04 |
| feuille de route | ordinateur | 14,05 | 5,20 (cartes et première phrase) | **3,84** (cartes, tête seule) |
| | téléphone | 20,94 | 6,93 | **5,20** |

- ✅ Repliée, la plus grosse page de chantier retombe **sous** une page neuve :
  1,09 écran d'ordinateur, contre 1,43 pour la page 41.
- ⚠️ La feuille retombe moins bas : 19 cartes restent 19 lignes.
- ⚠️ Montage : chaque maquette est enveloppée comme sur claude.ai (charset,
  viewport, marge nulle) et servie en local, le même jour. Les valeurs « telle
  quelle » ne sont pas celles du § 2.2 : page 30, 9,02 contre 9,0 sur ordinateur,
  mais 19,24 contre 20,3 sur téléphone ; feuille, 14,05 contre 13,1 (et 12,5 sans
  charset). La hauteur absolue dépend du montage, jusqu'à 1,5 écran (feuille : 12,5
  contre 14,05) ; la table de
  la feuille, qui ajuste ses colonnes au texte, y est la plus sensible. Cause
  exacte non établie. Les comparaisons ne se font donc qu'à l'intérieur d'un même
  montage.
- ✅ Aucune maquette ne perd de mot (contrôle par script) : seuls les trois titres
  de colonnes de la TODO disparaissent avec le tableau.
- « 1,00 » : la page tient dans un écran (le rapport ne descend pas sous 1).

| Ordre | Chantier | Fiches | Coût estimé | Pourquoi à ce rang |
|---|---|---|---|---|
| A | Réparer ce qui est cassé | ~4 | 8,7 à 14,6 M | défauts visibles, dans 4 projets |
| B | Mettre notes et journal à l'abri dans un `.md` | ~3 | 6,5 à 11,0 M | **avant** D : on ne remanie pas une page qui est la seule copie de son texte |
| C | Essai : alléger la republication (fichier joint, base de données) | 2 | 4,4 à 7,3 M | décide où vivent le CSS et les données **avant** que D et E les touchent |
| D | La page de chantier plus courte et lisible | ~5 | 10,9 à 18,3 M | après C |
| E | La feuille de route plus courte et lisible | ~4 | 8,7 à 14,6 M | après C ; 🟡 une décision à prendre |
| F | Des boutons (et le CSS joint partout, si C tient) | ~4 à 6 | 8,7 à 21,9 M | en dernier, optionnel |

Total ≈ 22 à 24 fiches, ≈ 48 à 88 M tokens, soit ≈ 40 à 73 $ au tarif moyen du kit.

### A — Réparer ce qui est cassé

➡️ Ouvert le 2026-09-23 : chantier `REP`, `39-reparer-pages.md`, 4 fiches.

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
  dit « fini ». ➡️ *Changé à l'ouverture de `REP` (2026-09-23, 🟡 à valider) :
  `rejeu.py` code Cairn en dur ; ses trois compteurs passent dans `vlp.py niveau`
  (`39-reparer-pages.md`, REP3).*
- **Fini quand** : sur les 5 projets, 0 `**`, 0 lien Markdown, 0 `href="&lt;`.

### B — Mettre notes et journal à l'abri dans un `.md`

Venu de la contre-expertise, **réécrit le 2026-09-23** : la première version
limitait la longueur des notes. Elle aurait coupé du texte qui n'existe nulle part
ailleurs (§ 2.6).

- `vlp.py page --note` et `--journal` écrivent **d'abord** le texte entier dans un
  `.md`, puis la page le recopie. La page devient dérivée pour eux aussi
  (`tache-page.md:5`–`:7` ne la dit dérivée que pour les états, l'avancement, le
  comptage, les coûts et la date). 🟡 L'endroit est à trancher : sous la fiche, dans le fichier
  de fiches ; ou, pour le journal, dans le fichier d'état, où il est déjà censé
  être (`tache-page.md:14`–`:15`).
- Une migration, une fois : les blocs existants passent de la page au `.md`, par
  script (Cairn 198, le kit 148, MapDecorator 11).
- Rien n'est coupé. La règle « une ligne » (`ARTEFACTS.md:111`–`:112`) devient une
  affaire d'affichage : la note entière, dans son bloc replié (D).
- ⚠️ Une note reste **une seule balise** : `lis_page` n'en relit qu'une
  (`scripts/vlp.py:736`), et `regenerer` recopie ce qu'il a relu (`:864`). Coupée
  en deux balises — la première phrase visible, la suite repliée —, sa suite
  serait perdue à la régénération suivante. Montrer la première phrase à part ne
  se fait donc qu'après B, quand la note vit entière dans le `.md`. *Précisé le
  2026-09-23 (troisième avis) : B disait « la page montre la première phrase ».*
- La garde de taille compte en **caractères**, plus en lignes, et garde aussi la
  feuille. Elle prévient ; elle ne coupe rien.
- **Fini quand** : `page_vs_source.py` retrouve **en entier** toutes les notes et
  entrées de journal des 5 projets (Cairn aujourd'hui : 0 sur 198) ; un test garde
  entière une note de 800 caractères ; la feuille de Cairn déclenche la garde.

### C — Essai : alléger la republication (deux fiches)

Deux pistes, mesurées l'une après l'autre. Avant : une lecture seule coûte 5 379
tokens (médiane, § 2.5).

**C1 · Le CSS en fichier joint**

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

**C2 · Les données en base (`db`)** — ajouté le 2026-09-23, sur ta question

- Une base de documents rattachée à la page, **hébergée par claude.ai** : rien à
  installer, ni Docker ni SQLite.
- La page ne porte plus que sa structure ; fiches, notes et journal viennent de la
  base. `vlp.py` écrit un fichier JSON ; `ArtifactData` l'envoie par `file_path`,
  sans le retaper.
- ✅ Une écriture ne demande pas de relire le document (`if_version` y est
  facultatif), alors que republier une page demande de la lire
  (`tache-page.md:22`). C'est là que serait le gain.
- ✅ C'est ce que la plateforme conseille pour un suivi ou un journal : écrire des
  lignes par `ArtifactData` plutôt que republier la page (description de l'outil
  Artifact, § 7).
- ❌ La page ne s'affiche plus sans la base : fichier ouvert en local, aperçu, et
  🟡 peut-être visiteur par lien public. `vlp.py page --verifier` ne peut pas lire
  la base.
- ❌ Le fichier local ne serait plus qu'une coquille : sans B, l'information ne
  vivrait plus que sur claude.ai. **Donc B d'abord** : la base n'est qu'une copie.
- ❌ La capacité dépend du compte : `db` n'existe que pour les comptes qui l'ont
  (liste des capacités, propre à chaque utilisateur) ; le kit sert à un groupe,
  chacun devrait l'avoir.
- ❌ Afficher depuis la base demande un script dans la page
  (`claude.use("db")`), relu à chaque fiche — alors que D se limite à un script
  court (« Tout replier »).
- 🟡 À prouver : ce que coûte une écriture, et si chaque écriture demande ton
  accord (ce qui gênerait `/vlp:enchainer`). C'est probable : l'outil regroupe
  plusieurs écritures « sous une seule approbation » par lot (`batch`), donc une
  par écriture hors lot. *Ces trois points : troisième avis, 2026-09-23.*

**Fini quand** : pour chaque piste, le coût d'une republication mesuré avant et
après, et une décision écrite : on l'adopte ou non.

### D — La page de chantier plus courte et lisible

Tout en HTML natif, sauf un script court : le bouton « Tout replier » (plus bas).
Aucune perte : replié, le texte reste dans le HTML (ce que Claude en lit dépend de
la lecture, 🟡 § 2.5). *Corrigé le 2026-09-23 (troisième avis) : disait « pas de
script » et « que Claude lit en entier ».*

- Chaque fiche dans un `<details>` : identifiant, titre et état visibles ; note
  et coût repliés ; la fiche en cours ouverte. Garder le `<li class="fiche">`
  autour, pour `LI_FICHE` (`scripts/vlp.py:665`), et la note en une seule balise,
  pour `lis_page` (`scripts/vlp.py:736`) : **B avant D** (voir B).
- Chantier clos : le bilan **monte sous l'en-tête**.
- Deux niveaux de pli : la liste des fiches et le journal se replient aussi,
  chacun en une ligne. Sur un chantier clos, tout est replié d'office sous le
  bilan ; sur un chantier en cours, la liste reste ouverte, une ligne par fiche.
- 💡 Le bouton « Tout replier » passe de F à D : ta consigne est de pouvoir
  retomber court à tout moment. Sans lui, recharger la page suffit (un pli
  ouvert ne survit pas au rechargement). Son script est court (une dizaine de
  lignes), relu à chaque fiche.
- Journal : les trois dernières entrées visibles, le reste replié. C'est le vrai
  levier : prototype du 2026-09-22 sur la page 30, en écrans de **téléphone** :
  notes repliées 20,3 → 14,2, puis journal réduit à 3 entrées → **5,4**. La
  maquette du 2026-09-23, même dessin, autre montage (§ 4) : 19,24 → 6,08 sur
  téléphone, 9,02 → 3,19 sur ordinateur.
- Un sommaire ; titres sans majuscules, au moins 1,2 fois le texte ; petites
  tailles relevées (§ 2.3).
- ⚠️ **Outil à écrire** : `vlp.py niveau` ne migre aucune page de chantier (il ne
  lance que `page --verifier` sur la page en cours), et `regenerer` ne touche ni
  au CSS ni à la structure. Il faut une migration des pages, et adapter l'ajout
  au journal (`regenerer`) et l'échange bilan/blocage (`clore`). Cette migration
  doit reprendre chaque note et chaque entrée de journal à l'identique : après B,
  elle les relit dans le `.md`.
- **Fini quand** : page 30 régénérée, **tout replié ≈ 1 écran d'ordinateur**
  (maquette du 2026-09-23 : 1,09 ; une ligne par fiche : 3,19 ; telle quelle :
  9,02, même montage), bilan visible sans défiler,
  `page --verifier` vert ; `page_vs_source.py` : aucun bloc perdu entre avant et
  après.

### E — La feuille de route plus courte et lisible

- La TODO en **cartes** : une ligne de tête (rang, repères, code, titre, coût,
  dépendance) et la première phrase visibles ; le reste replié.
- Un sommaire ; même typographie que D.
- ⚠️ **Ce qui casse**, à reprendre dans le même chantier : la zone
  `todo` lue entre `<tbody>` et `</tbody>` dans `feuille()` et dans la garde de
  `clore` (`scripts/vlp.py:1150`, `:1622`) ; le motif de la ligne en cours
  (`scripts/vlp.py:1152`) ; `migrer_feuille` ; les feuilles des 5 projets ;
  `rejeu.py`.
- **Fini quand** : feuille de Cairn repliée ≈ 4 à 5 écrans d'ordinateur
  (maquette du 2026-09-23, même montage : cartes, tête seule 3,84 ; cartes avec
  leur première phrase 5,20 ; telle quelle 14,05), plus aucun défilement de côté.
- 🟡 La première phrase de chaque carte, visible ou repliée : 5,20 contre 3,84
  écrans d'ordinateur. À trancher dans le chantier.
- 🟡 **À décider (toi)** : la feuille doit-elle porter **tout** le détail de la
  TODO ? La colonne « Ce qu'il apporte » pèse **58 %** de la page (29 785
  caractères sur 51 151). Sans elle, une lecture passerait d'environ 24 k à
  environ 10 k tokens (règle de trois, donc estimation).
  - ✅ Pour Claude, aucune perte : les 19 rangs de la TODO sont recopiés **en
    entier** de `10-etat.md`, cellule par cellule (`page_vs_source.py`,
    2026-09-23).
  - ⚠️ Pour toi, une perte sur la page : le détail n'y serait plus ; il faudrait
    ouvrir `10-etat.md`, ou demander à Claude.
  - 💡 **Ma recommandation change** (2026-09-23) : d'abord les cartes repliées —
    rien ne se perd, ni pour toi ni pour Claude. Sortir le détail seulement si le
    coût de relecture gêne. La contre-expertise préférait le sortir, pour le
    coût ; tu as dit lire la page toi aussi, et c'est ce qui me fait changer.

### F — Des boutons, en dernier

Optionnel. Leur script va dans le fichier joint si C tient ; sinon il reste en
ligne, relu à chaque fiche.

- 💬 « Commenter cette fiche » : `comments` en forme `composer_only`.
- « Tout déplier » (« Tout replier » passe en D).
- Filtres : 🔴 🟠 🟡 sur la TODO ; à faire / faites sur les fiches.
- « Copier la commande » : `/vlp:tache <fiche>` dans le presse-papiers.
- Un graphique des tokens par chantier clos, sur la feuille.
- 🟡 Option à essayer : « 🔊 Résumer simplement » (`sample`, payé par le lecteur,
  consentement au premier clic).
- Si C tient : le CSS joint sur les pages des 5 projets (~2 fiches de plus).

### Écarté, et pourquoi

- Couper les notes et le journal trop longs (première version de B) : ce texte
  n'existe que dans la page (§ 2.6) ; le couper le perdrait.
- Une base de données locale — SQLite (déjà dans Python) ou un serveur sous
  Docker : Claude lit un `.md` d'un seul coup, alors qu'une base demande une
  requête à chaque lecture ; un fichier `.db` ne se lit pas dans un diff git ; et
  Docker serait une dépendance de plus pour tout le groupe (règle 4 de
  `CLAUDE.md` : Python 3 sans dépendance). Le `.md` suffit pour ne rien perdre.
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
| Mes hauteurs d'écran se rejouent-elles ? | ❌ pas toutes : le 2026-09-23, page 30 20,6 → **20,3**, 29 : 7,8 → 7,7, 31 : 7,2 → 7,1, bilan de 30 : 20,1 → 19,7, médiane 4,75 → **4,7** ; feuille (19,6) et page 41 (1,9) identiques | remesurées en mode téléphone, polices chargées, pages inchangées depuis le 2026-09-22 ; valeurs remplacées. Cause de l'écart inconnue (polices pas encore chargées la première fois ? non prouvé) ; une mesure en iframe donne encore ±0,2 écran ; écarts de 0,1 à 0,4 écran, de l'ordre de la précision d'une remesure (§ 1) |
| Les cibles « ≤ 5 écrans » et « ≤ 4 écrans » sont-elles réalistes ? | ❌ non mesurées | prototype au navigateur : **5,4** et **5,4 à 5,9** ; cibles remplacées |
| Replier allège-t-il la relecture ? | ❌ non : le modèle lit aussi ce qui est replié | lisibilité (2, 3) et coût (4) séparés ; seule l'option « détail hors page » allège sans le chantier 4 |
| Le chantier 4 respecte-t-il « deux artefacts, et pas un de plus » ? | ❌ non, dans ma première version (un artefact « kit ») | copie locale déposée par `vlp.py`, jointe par `files` |
| Un script dans la page est-il gratuit ? | ❌ non : relu à chaque fiche | boutons de préférence après le chantier 4 |
| Où est le vrai volume de la page 30 ? | je pensais aux fiches | c'est le **journal** (25 entrées, jusqu'à 619 caractères) |
| Le bug du Markdown ne touche-t-il que Cairn ? | ❌ non | TrackGen (4) et ProjetONZSM (2) ajoutés au chantier 1 |
| Le « 35 $ » est-il un coût ? | ⚠️ un plafond | écrit comme plafond : surtout des relectures de cache |
| Ma source sur la dyslexie fait-elle autorité ? | ⚠️ à moitié | organisme public, cite le guide BDA 2023 ; le guide BDA lui-même n'a pas pu être lu (403) — dit en § 7 |
| Un bloc `<details>` casse-t-il `vlp.py page --verifier` ? | 🟡 probablement pas | `LI_FICHE` (`scripts/vlp.py:665`) cherche `<li class="fiche" …>…</li>` : garder ce `li` autour du `details` ; à couvrir par un test au chantier 2 |
| « Plus court » fait-il perdre de l'information à Claude ? (ta question du 2026-09-23) | ❌ oui, pour B dans sa première version : notes et journal n'existent que dans la page | § 2.6 ajouté ; B réécrit ; D et E : « rien ne se perd » écrit noir sur blanc ; recommandation d'E changée |
| Mon script de vérification est-il juste ? | ❌ non, sa première version : il retirait les `<…>` aussi dans le Markdown, un « < 10 » avalait du texte ; il trouvait 14 rangs de TODO sur 19 dans `10-etat.md`, au lieu de 19 | réécrit : comparaison sans accents ni ponctuation, trois niveaux ; chiffres remplacés |
| La base de données était-elle bien écartée ? (ta question du 2026-09-23) | ❌ trop vite : sa raison, « écrite par le modèle, pas par un script », est à moitié fausse — l'outil accepte un fichier JSON écrit par script | passée en 🟡 à essayer, dans l'essai C, après B |
| Repliée, une page retombe-t-elle court ? (ta consigne du 2026-09-23) | ✅ mesuré : page 30, 1,09 écran d'ordinateur tout replié, contre 9,02 | D : deux niveaux de pli, « Tout replier » avancé en D ; D et E : « Fini quand » mesuré replié |
| Mes hauteurs tiennent-elles d'un montage à l'autre ? | ❌ non : jusqu'à 1,5 écran d'écart (feuille : 12,5, 13,1, 14,05 ; « un écran » avant le troisième avis) | comparaisons dans un même montage seulement, écrit au § 1 et au § 4 |

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
| 7b | Chiffrage optimiste | ✅ | fiches × quartiles du kit : 44 à 80 M (48 à 88 M depuis le 2026-09-23) |
| 8 | Garde de taille muette ; règle « une ligne » non tenue ; fréquence de republication non étudiée | ✅ 246 lignes ; `ARTEFACTS.md:111` ; `ARTEFACTS.md:17` | chantier B (réécrit le 2026-09-23 : il ne coupe plus rien) ; fréquence en question ouverte |
| 9 | « 12 pt conforme » vaut pour le corps seulement | ✅ | § 2.3 |
| 10 | Comptes à reformuler ; page 41 changée après la mesure | ✅ page 41 : 2,35 écrans aujourd'hui | § 2.1, § 2.2 |
| 11 | Le catalogue n'a pas de source | ⚠️ en partie : la source existe (contrat de page de l'outil Artifact, liste des types) mais n'était pas citée | § 3 et § 7 la citent |
| 11b | « Mermaid rendu nativement » douteux | ❌ rejeté : le contrat le dit, par `<pre class="mermaid">` ; invisible en aperçu local, à voir sur la page publiée | — |
| 11c | « forme complète = page interne » extrapolé | ✅ | reformulé en § 3.2 |

Ce qu'il n'a pas pu vérifier : les hauteurs d'écran (remesurées par moi, voir
§ 5), les 641 px dans 319, le débordement de la page 29 (496 px, remesuré),
« 2 fois sur 128 », « version publiée identique ». Ces trois derniers restent
sur ma seule parole.

### 6 bis. Troisième avis (étape 6 : un second sous-agent neuf)

Demandé par toi le 2026-09-23, avant le push. Un autre sous-agent, sans
l'historique de la session, a relu le rapport, la page et les scripts après le
commit `11ba645`, avec la consigne de réfuter (191 499 tokens, environ 28 appels
d'outils ; interrompu une fois par un arrêt de l'application, puis repris). Son
verdict : « l'audit tient — ne pas pousser avant correction ». J'ai revérifié
chaque point avant de l'intégrer.

| # | Ce qu'il dit | Revérifié | Changement |
|---|---|---|---|
| 1 | La page dit « relu et validé » alors qu'une troisième relecture est en cours | 🟡 en partie : tu as validé le 2026-09-23, mais **avant** tes deux dernières questions (base de données, replier et retomber court) | page, étape 5 : « validé ; les deux dernières questions, après » ; étape 6 ajoutée |
| 2 | Du contenu de Cairn part dans un dépôt public : une vraie note (P1), le rang 18 de sa TODO, 9 totaux de chantiers, 37 lectures datées | ✅ et plus : le dépôt de Cairn est **privé** (API GitHub, 2026-09-23 : 404 ; le kit : 200), et son dossier de contexte est hors de git (`Cairn-VlpLib/.gitignore:13`) | 🟡 **à ta décision**, avant tout push |
| 3 | « Tient en un écran » : sa mesure dit 1,09 ; et 864 px est l'écran entier, pas ce qu'on voit | ✅ | résumé : « à peine plus d'un écran » ; l'unité et sa limite écrites au § 1 |
| 4 | « Que Claude lit en entier » n'est pas établi : le § 2.5 dit qu'une lecture peut ne rendre que le début (lecture complète : 2 fois sur 128) | ✅ | « reste dans le HTML », avec renvoi au 🟡 du § 2.5 (§ 2.6, D, page) ; la conclusion « replier ne perd rien » tient : replier ne retire rien du HTML |
| 5 | D dit « pas de script », puis avance « Tout replier » et son script | ✅ | D : « sauf un script court » |
| 6 | L'écart de montage va jusqu'à 1,55 écran, pas un ; le § 2.7 compare deux montages ; la page donne 13,1 puis 14,1 pour la feuille sans le dire | ✅ ; les corrections du § 5 (0,1 à 0,4 écran) sont de l'ordre de la précision d'une remesure | § 1 : précision écrite ; § 2.7 : même montage (1,42 contre 2,28) ; § 4 et § 5 : « jusqu'à 1,5 » ; page : une phrase |
| 7 | D cite un prototype en écrans de téléphone, sans le dire | ✅ | étiqueté « téléphone », la maquette ajoutée |
| 8 | « L'inverse de la doctrine » est faux pour les notes | ✅ `tache-page.md:5`–`:7` ne vise que états, avancement, comptage, coûts, date | § 2.6 : trou de conception (notes), règle non appliquée (journal) ; ancien énoncé marqué |
| 9 | B montre la première phrase, D replie la note entière ; deux balises casseraient `lis_page` | ✅ et plus : `regenerer` recopie ce que `lis_page` a lu (`scripts/vlp.py:736`, `:864`) — la suite de la note serait perdue | B et D : une note, une balise ; **B avant D** rappelé aux deux endroits |
| 10 | C2 : il manque trois « contre » | ✅ (descriptions des outils Artifact et `ArtifactData`) | C2 : le compte, le script, un accord par écriture |
| 11 | `rejeu.py` écrit `clos.json` dans le dépôt, fichier non ignoré | ✅ `rejeu.py:70` | n'écrit plus que si on lui donne un chemin ; ses 26 valeurs, rejouées : identiques (§ 8) |
| 12 | `chiffres_vs_source.py` compte un nombre trouvé n'importe où | ✅ rejoué : 121 / 139 ; sans les dates 119 / 138 ; nombres d'au moins 1 000 seuls 90 / 107 | § 2.6 reformulé, variantes écrites |
| 13 | Publication : l'URL d'un artefact privé (en tête), des morceaux d'identifiants d'artefacts de Cairn (`feuille_detail.py:31`), une source non publique au § 7 | ✅, mineur : un lien privé ne s'ouvre pas sans accès | § 7 : « non publique » |
| — | `ARTEFACTS.md:111` : la règle finit à la ligne 112 | ✅ | B : `:111`–`:112` |

Ce qu'il a rejoué et trouvé juste — son rejeu, pas le mien, sauf le n° 12 :
`page_vs_source.py` sur les 5 projets (0 / 198, 6 / 148, 1 / 11 ; TODO 19 / 19,
11 / 11, 8 / 8) ; le 0 / 198 tient sur un corpus élargi (166 fichiers et le
`git log`, suites de 5 mots : 2 blocs sur 198 retrouvés à 80 % ou plus) ;
`replie.py` ne perd aucun mot ; toutes les références `fichier:ligne` de
`11ba645` ; l'arithmétique du § 4 (47,96 et 87,6 M ; 40,15 et 73,33 $) ; les 26
valeurs de `rejeu.py` ; l'accord du rapport et de la page.

Ce qu'il n'a pas pu vérifier : les hauteurs d'écran (le navigateur intégré refuse
le JavaScript sur un fichier local), le coût du § 2.5 (il ne devait pas lire les
transcriptions), la version publiée.

## 7. Sources web

| Source | Rang | Consultée | Ce qu'elle établit |
|---|---|---|---|
| [Dyslexia-Friendly Style Guide, Ako Aotearoa, juillet 2023 (PDF)](https://ako.ac.nz/assets/Knowledge-centre/ALNACC-Resources/Dyslexia-resources/230907-Dyslexia-Friendly-Style-Guide.pdf) | organisme public | 2026-09-22 | majuscules, taille des titres, sommaire, abréviations, schémas |
| [BDA Dyslexia Style Guide 2023 (PDF)](https://cdn.bdadyslexia.org.uk/uploads/documents/Advice/style-guide/BDA-Style-Guide-2023.pdf) | association de référence | 2026-09-22 | ❌ non lu : accès refusé (403) |
| [MDN, `<details>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/details), modifiée le 2026-04-24 | doc officielle | 2026-09-22 | attribut `name` (accordéon), événement `toggle`, rôle `group` |
| [Chromium, « Intent to Ship: Auto-expand details elements »](https://groups.google.com/a/chromium.org/g/blink-dev/c/a6iO__pqI_E/m/Asj1sUABBAAJ), 2021-09-17 | source primaire | 2026-09-22 | Ctrl+F ouvre un bloc replié ; cible Chrome 96 |
| [Coywolf, auto-expand details](https://coywolf.com/news/seo/details-disclosure-element-can-now-auto-expand-using-the-browsers-find-on-page-feature/) | blog d'actualité | 2026-09-22, extrait de recherche | Firefox 139 et Safari 26.2 — ⚠️ une seule source, secondaire, page non ouverte |
| [GOV.UK Design System, Details](https://design-system.service.gov.uk/components/details/) | design system public | 2026-09-22, extrait de recherche | un seul bloc → Details ; plusieurs → accordéon |
| Contrat de page et de capacités de l'outil Artifact (contrat 0.2.54), liste des types de page ; description de l'outil `ArtifactData` | doc de la plateforme — ⚠️ non publique : lue dans la session, un lecteur du dépôt ne peut pas la vérifier | 2026-09-22 et 2026-09-23 | ce qu'une page peut et ne peut pas faire ; écriture en base sans relire la page, par `file_path` ; « suivi ou journal → base plutôt que republier » |
| [Smashing Magazine, tableaux responsives](https://www.smashingmagazine.com/2022/12/accessible-front-end-patterns-responsive-tables-part1/), 2022-12 | magazine | 2026-09-22, extrait de recherche | le motif « cartes empilées » sur téléphone |

Coût web : 4 recherches, 4 pages ouvertes (dont 1 refusée) ; les trois dernières
lignes ne sont connues que par l'extrait du moteur de recherche.

## 8. Annexe — les scripts de mesure

Rangés dans `context AI/38-audit-scripts/`, à côté de ce fichier. Python 3, sans
dépendance, zéro appel modèle.

| Script | Ce qu'il mesure |
|---|---|
| `rejeu.py <racine ProgPerso> [<clos.json>]` | les 26 valeurs tirées des fichiers de Cairn (§ 2.1 à 2.4) ; écrit les données du graphique des clos seulement si on lui donne un chemin (avant le troisième avis : toujours, à côté de lui, donc dans le dépôt) |
| `cout_lecture.py <transcriptions>` | l'écart de contexte autour de chaque `Artifact read` ou `publish` |
| `poids_reel.py <transcriptions>` | la méthode d'origine : écart × tours restants (surestimée, § 2.5) |
| `ce_biais.py`, `ce_poids2.py`, `ce_double.py` | les biais relevés par la contre-expertise, et la fourchette corrigée |
| `feuille_detail.py <transcriptions> <racine>` | les 37 lectures de la feuille ; le coût par fiche du kit (§ 4) |
| `page_vs_source.py <racine du projet> <dossier de contexte>` | le texte des notes, du journal et de la TODO, retrouvé ou non ailleurs que dans la page (§ 2.6) |
| `chiffres_vs_source.py <racine du projet> <dossier de contexte>` | les nombres de ces blocs, retrouvés ou non ailleurs (§ 2.6) |
| `replie.py <artefacts de Cairn> <sortie>` | les maquettes « telle quelle », « une ligne par fiche » et « tout replié » des pages 30, 41 et de la feuille, à mesurer au navigateur (§ 4) |

Hauteur d'écran, dans le navigateur intégré en mode téléphone (375 × 812), une
page à la fois :

```js
await document.fonts.ready;
document.documentElement.scrollHeight / 812
```

🟡 À ranger dans `scripts/` si le chantier A reprend `rejeu.py`. ➡️ *Non : ses
compteurs passent dans `vlp.py niveau` (chantier `REP`, fiche REP3 ; 2026-09-23,
🟡 à valider).*
