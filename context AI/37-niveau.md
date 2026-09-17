> **QUAND LIRE** : on joue une fiche `NIV*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache NIV<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier NIV — Remettre les projets équipés à niveau

**À quoi il sert.** Les cinq projets équipés ont dérivé du kit : renvois morts,
fichiers de tête hors seuil, feuilles de route en écart ou absentes. Et la carte
injectée à chaque tour 1 crache le message du raccourci Microsoft Store. Le
chantier écrit de quoi diagnostiquer et remettre à niveau **par script**, au lieu
de le refaire à la main cinq fois.

**Fait.** Rien. Ouvert le 2026-09-17, cadré en 4 fiches, `NIV1` à jouer.

## Le socle commun

**Le kit.** `C:/Users/znorr/Documents/ProgPerso/Claude-vlpWorkflow`, lié dans
`~/.claude/skills/vlp`. Toute la mécanique est dans `scripts/vlp.py` (1576
lignes) ; les tests dans `scripts/test-vlp.py` — `py scripts/test-vlp.py`
imprime `OK` et sort 0, ou le premier écart et sort 1. Une fiche qui touche
`vlp.py` ajoute ses vérifications à ce fichier.

| Symbole | fichier:ligne | Ce qu'il rend |
|---|---|---|
| `carte_injectee` | `scripts/vlp.py:247` | la carte d'une injection ; tampon dans le dossier temporaire, `--relais` se tait si le tampon a moins de `RELAIS_SECONDES` |
| la ligne d'injection | `skills/chantier/SKILL.md:18`, `skills/tache/SKILL.md:17` | `py … --python py; python3 … --relais; py … --relais; echo fin` |
| `renvois <projet>` | `scripts/vlp.py:1493` | `ABSENT: <source>:<ligne>: <nom>`, `AVERTISSEMENT: <fichier> <n> lignes > <seuil>`, `POIDS …`, `RENVOIS <n> nommés · <n> absents` |
| `feuille <projet> --verifier` | `scripts/vlp.py:1495` | `identique|écart`, sort 1 sur écart, n'écrit rien |
| `page <fichier> --verifier` | `scripts/vlp.py:1479` | idem pour la page du chantier |
| `chemin_garde`, `lignes_gardees` | `scripts/vlp.py:148`, `:157` | toute lecture d'un chemin venu de `CHANTIER.md` : `GARDE: <phrase>` et sortie 1, jamais un traceback |
| `main` | `scripts/vlp.py:1453` | où une sous-commande s'ajoute (`sous.add_parser`) |
| les seuils | `scripts/vlp.py:469-474` | `SEUIL_FICHE` 50, `SEUIL_SOCLE` 80, `SEUIL_CLAUDE` 80, `SEUIL_CHANTIER` 50, `SEUIL_INDEX` 80 |

**Les cinq projets**, tous sous `C:/Users/znorr/Documents/ProgPerso/` :
`Cairn-VlpLib`, `MapDecorator`, `TrackGen`, `ProjetONZSM`, `vlp-bac-a-sable`.
Écarts déjà mesurés le 2026-09-17 : Cairn `CLAUDE.md` 89/80, index 111/80, table
des clos encore dans `CHANTIER.md`, 2 renvois absents ; MapDecorator 84/80 ;
TrackGen `CHANTIER.md` 51/50 ; feuille de route en écart sur 3, absente du bac ;
le bac pointe une variable dans un fichier de données.

**Ce qu'on ne fait pas.** On ne retire **pas** les copies locales de
`methode-chantier.md` : `methode-chantier.md` dit qu'un projet équipé avant la
règle garde la sienne, et c'est la TODO n° 22 qui se trompe — `NIV2` la corrige.
On ne compacte pas un fichier de tête par script : abréger relève du jugement,
c'est `NIV4`, à la main.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `NIV1` | Faire taire le relais de la carte | rien |
| `NIV2` | Diagnostiquer un projet équipé en un appel | rien |
| `NIV3` | Écrire ce que le diagnostic sait corriger | `NIV2` |
| `NIV4` | Passer les cinq projets à niveau | `NIV3` |

`NIV1` et `NIV2` sont indépendantes et peuvent se jouer dans n'importe quel
ordre ; `NIV3` puis `NIV4` s'enchaînent.

---

<!-- FICHE:NIV1 -->
## NIV1 [x] — Faire taire le relais de la carte

**Session** : 13d25719-7b36-44b8-81a7-5cb45dbbec0e
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `skills/chantier/SKILL.md`, `skills/tache/SKILL.md`,
`scripts/test-vlp.py` — et rien d'autre.

**Prompt**
La carte injectée au tour 1 contient le message « Python est introuvable ;
exécutez sans arguments à installer à partir du Microsoft Store… ». Il ne vient
pas de `vlp.py` mais du raccourci `python3` de `WindowsApps`, qui parle avant
que Python démarre. Commence par **mesurer** : lance la ligne d'injection de
`skills/chantier/SKILL.md:18` telle quelle sous PowerShell, et dis sur quel flux
(stdout ou stderr) le message part, en citant la sortie brute.
Corrige ensuite au bon endroit — probablement la ligne d'injection des deux
skills, pas `carte_injectee`. La correction doit tenir sous PowerShell **et**
sous bash/Ubuntu : le chantier Y a retenu cet ordre d'appels parce que sous
Ubuntu c'est `py` qui manque, avec un message symétrique. Fais taire les deux.
N'ajoute pas de dépendance et ne change pas `RELAIS_SECONDES`.
Ajoute à `scripts/test-vlp.py` une vérification de ce que la carte contient, ou
ne contient pas.

**Critère de fin**
La ligne d'injection lancée sous PowerShell dans le kit et dans un projet non
équipé ne contient plus aucun message de lanceur : montre la sortie avant et
après, avec le nombre de lignes de chaque. `py scripts/test-vlp.py` imprime `OK`.
<!-- /FICHE -->

---

<!-- FICHE:NIV2 -->
## NIV2 [x] — Diagnostiquer un projet équipé en un appel

**Session** : b697fc32-c187-4b57-9062-a5bccc79a190
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py`, `context AI/08-etat.md`
— et rien d'autre.

**Prompt**
Écris la sous-commande `vlp.py niveau <projet>`, qui **n'écrit rien** et dit en
quoi un projet équipé a dérivé du kit. Elle agrège ce qui existe déjà — `renvois`
(renvois absents, poids des fichiers de tête), `feuille --verifier`, `page
--verifier` sur le fichier de fiches courant — et ajoute ce que rien ne voit
encore : une variable `${…}` citée dans un fichier de données (`CHANTIER.md`,
index, fichier d'état), une table des chantiers clos restée dans `CHANTIER.md`,
une feuille de route absente. Chaque écart sort sur une ligne
`ÉCART: <catégorie>: <phrase>` ; le bilan final est `NIVEAU <n> écarts ·
<n> avertissements — <projet>`. Un écart : sort 1.
Lis les chemins du projet par `lignes_du_projet` pour hériter des `GARDE:`.
Ne compte **pas** une copie locale de `methode-chantier.md` comme un écart, et
corrige en même temps l'entrée n° 22 de la TODO de `context AI/08-etat.md`, qui
prétend l'inverse.

**Critère de fin**
`py scripts/vlp.py niveau <projet>` lancé sur les cinq projets retrouve les
écarts déjà mesurés (Cairn `CLAUDE.md` 89/80 et 2 renvois absents, TrackGen
`CHANTIER.md` 51/50, feuille absente du bac) : colle les cinq bilans bruts.
`py scripts/test-vlp.py` imprime `OK`.
<!-- /FICHE -->

---

<!-- FICHE:NIV3 -->
## NIV3 [ ] — Écrire ce que le diagnostic sait corriger

**Dépend de** : `NIV2`.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Ajoute `--ecrire` à `vlp.py niveau`. Elle corrige les seuls écarts **mécaniques**,
ceux dont la bonne valeur se déduit sans jugement : la table des chantiers clos
retirée de `CHANTIER.md` (`clore` le fait déjà à la clôture — réutilise son code,
ne le recopie pas), la feuille de route posée depuis le gabarit si elle manque
puis régénérée par `feuille`. Une feuille de route d'avant le 2026-09-17 n'a ni
le bloc repliable `<details class="clos">` ni la cellule d'estimation en dollars
du pied de table : pose-les aussi, avec le `<span class="resume-clos">` que
`clore` réécrit — sans changer l'indentation des lignes de `ZONE:clos`, que
`clore` repère à dix espaces. Elle **ne touche pas** aux fichiers de tête hors
seuil ni aux renvois absents : elle les laisse en `ÉCART:` et dit lesquels
restent à la main.
Tout se calcule avant la première écriture, comme `clore`. Le bilan devient
`NIVEAU <n> corrigés · <n> à la main — <projet>`.

**Critère de fin**
Sur un bac de test construit par les tests, un avant/après : `niveau` sans
`--ecrire` liste N écarts, `--ecrire` en corrige M, un second `niveau` n'en
trouve plus que N−M — les trois nombres affichés. `py scripts/test-vlp.py`
imprime `OK`.
<!-- /FICHE -->

---

<!-- FICHE:NIV4 -->
## NIV4 [ ] — Passer les cinq projets à niveau

**Dépend de** : `NIV3`.
**Fichiers** : les `CHANTIER.md`, `CLAUDE.md` et dossiers de contexte des cinq
projets listés au socle — et rien du kit.

**Prompt**
Lance `vlp.py niveau <projet> --ecrire` sur les cinq projets, l'un après
l'autre. Puis traite à la main ce que le script a laissé : les renvois absents
de Cairn-VlpLib (le fichier existe-t-il sous un autre nom, ou le renvoi est-il
mort ?) et les fichiers de tête hors seuil — Cairn `CLAUDE.md` 89/80 et index
111/80, MapDecorator 84/80, TrackGen `CHANTIER.md` 51/50. Abréger relève du
jugement : coupe ce qui est du volume, jamais une règle ; si une règle est
recopiée d'un autre fichier, remplace-la par un renvoi. Ne touche à aucun
chantier ouvert ni à aucune case cochée.
Ne publie ni ne republie aucune page sans le demander d'abord.

**Critère de fin**
`vlp.py niveau` sur les cinq projets rend `0 écarts` — ou, pour chaque écart
restant, une ligne disant pourquoi il est assumé. Colle les cinq bilans, et le
nombre de lignes avant/après de chaque fichier de tête retouché.
<!-- /FICHE -->
