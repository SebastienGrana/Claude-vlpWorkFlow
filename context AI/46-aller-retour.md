> **QUAND LIRE** : on joue une fiche `TAR*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache TAR<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier TAR — Ce que vlp.py écrit, il le relit

**À quoi il sert.** Deux fois dans `REP`, `vlp.py` a écrit un format qu'il ne savait pas relire :
les chevrons d'une URL (`REP2`), puis la ligne `? $` (`CPT`). Mesuré à l'ouverture, il en reste
quatre : un coût négatif, une ligne close sous 1 000 tokens, une lettre prise dans un titre ou
sans titre, un résumé sur deux lignes. Chaque format passera par son lecteur dans un test.

## Le socle commun

| Nom | Où | Ce qu'il fait ou rend |
|---|---|---|
| `COUT`, `ligne_cout`, `triplet` | `scripts/vlp.py:821` à `823`, `868`, `913` | `ligne_cout(total, tours, usd)` écrit `≈1,5M (1 505 630) · 3 tours · 1,25 $`, nu sous 1 000, `? $` sans prix ; `triplet` relit `(total, tours, usd)` par `COUT` |
| `arrondi` | `scripts/vlp.py:860` | la convention de coût : nu sous 1 000, sinon `≈<1 décimale><k\|M> (<brut>)` |
| `BRUT`, `lignes_clos`, `total_clos` | `scripts/vlp.py:1570`, `1577`, `1583` | relisent les lignes closes de la feuille de route ; `total_clos` somme les bruts entre parenthèses |
| la ligne close de `clore` | `scripts/vlp.py:2018` à `2033` | cellules `<td class="mono">` : plage, date, coût (`arrondi`) ; total en `2026` |
| `lettres_prises` | `scripts/vlp.py:1406` | les lettres de la ligne « Lettres de fiche déjà prises » ; `clore` y ajoute `, X (titre)` (`2003` à `2006`) |
| `ENTREE_CLOS`, `resume_claude` | `scripts/vlp.py:1866`, `1870` | la ligne `- Clos le <date> : <texte> (chantier X).` de `CLAUDE.md`, et son élagage |
| `verifier` | `scripts/test-vlp.py:51` | imprime `ÉCART: <nom>` et sort au **premier** échec ; tout passe : `OK` |
| les tests visés | `scripts/test-vlp.py:286` (« arrondi »), `291` à `294` (« triplet relit ligne_cout »), `743` à `753` (« résumé : … »), `1015` (« 3 lettres : … ») | à étendre, noms gardés |

Chaque fiche écrit ses tests **d'abord**, lance `py scripts/test-vlp.py`, et cite la ligne
`ÉCART:` qu'il sort sur le code d'avant : c'est son mutant (`methode-chantier.md`, « Anatomie
d'une fiche »). Puis elle corrige, et relance : `OK`.

**Mesuré à l'ouverture, le 2026-09-24** (sonde jetable, 198 allers pour le coût).
- Coût : 63 ratés sur 198, tous négatifs — `-5 · 0 tours · ? $` relu `(5, 0, None)`, le signe
  perdu ; un prix `-0,05 $` relu `None`, la ligne perdue. `couts` écrit un négatif sans Git,
  quand l'ancienne page affiche plus que la session mesurée.
- Ligne close : `total_clos` rend 0 pour 950, 1 500 pour 1 500. La vraie feuille : 439 668 779
  sur 34 lignes closes.
- Lettres : un titre « Tests, CI (rapide) » ajoute `CI` ; « A. » (le gabarit pose `<UNE>`) rend
  `[]`. Le vrai `CHANTIER.md` : 34 lettres.
- Résumé : « deux lignes\nici » écrit une entrée que `ENTREE_CLOS` ne relit pas — jamais élaguée.
- `arrondi(999 999)` écrit `≈1000,0k (999 999)` : relu juste, mais faux à l'œil.

**Décidé seul, la nuit du 2026-09-24** (l'utilisateur dort ; à revoir au réveil).
- Un coût négatif se relit avec son signe, au lieu d'être interdit : la somme garde son
  arithmétique, et la page montre l'anomalie au lieu de la taire.
- Sous 1 000, `clore` garde l'écriture nue du gabarit ; c'est la lecture qui s'élargit.

**Ce qu'on ne fait pas.** Rang de TODO et zone « en cours » : déjà relus par « feuille : badge
gardé sans --todo » et « feuille : ouvert, badge, lettre » (`scripts/test-vlp.py:704` à `716`).
La page régénérée deux fois est identique, note piégée comprise (`&`, `<`, backticks, `|`).

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `TAR1` | La ligne de coût garde son signe | rien |
| `TAR2` | La ligne close sous 1 000 tokens se recompte | rien |
| `TAR3` | Lettres prises et résumé : relus comme `clore` les écrit | rien |

Les trois sont indépendantes ; jouées en série, pour que les numéros de ligne du socle restent
justes à une vingtaine près.

---

<!-- FICHE:TAR1 -->
## TAR1 [x] — La ligne de coût garde son signe

**Session** : 1ba64929-8274-42d4-93bb-a2d22fbdd600
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (`COUT`, `triplet`, `arrondi`), `scripts/test-vlp.py` — et rien
d'autre.

**Prompt**
1. Tests d'abord, noms gardés :
   - « arrondi » (`scripts/test-vlp.py:286`) : `[mod.arrondi(n) for n in (999, 1000, 999949,
     999950, 1505630)]` rend `["999", "≈1,0k (1 000)", "≈999,9k (999 949)", "≈1,0M (999 950)",
     "≈1,5M (1 505 630)"]` ;
   - « triplet relit ligne_cout » (lignes 291 à 294) : `allers` devient tous les triplets de
     totaux 0, 7, 999, 1000, 999999, 1000000, 123456789, -5, -1500 ; tours 0, 1, 42 ; prix
     `None`, `Decimal("0")`, `Decimal("1.83")`, `Decimal("-0.05")` — 108 allers, tous relus égaux.
   Lance les tests ; cite la ligne `ÉCART:`.
2. `arrondi` passe au million dès que l'arrondi en milliers atteindrait 1000,0 (dès 999 950).
3. `COUT` accepte un signe moins devant le total nu et devant le prix ; son commentaire le dit.
   `triplet` rend l'un et l'autre avec leur signe.
Tu ne commites pas : le chef le fera.

**Critère de fin**
`py scripts/test-vlp.py` rend `OK` ; ton compte rendu cite l'`ÉCART:` de l'étape 1.
<!-- /FICHE -->

<!-- FICHE:TAR2 -->
## TAR2 [x] — La ligne close sous 1 000 tokens se recompte

**Session** : 1ba64929-8274-42d4-93bb-a2d22fbdd600
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (`BRUT`, `total_clos`, `cmd_clore`), `scripts/test-vlp.py` — et
rien d'autre.

**Prompt**
1. Tests d'abord, juste après « triplet relit ligne_cout » (`scripts/test-vlp.py:294`). Une
   ligne `l(c)` au format de `cmd_clore` (lignes 2020 à 2023), plage `Q1–Q2`, date `2026-05-06`,
   coût `c` :
   - « total_clos : une ligne close sous 1 000 » : `mod.total_clos(l(mod.arrondi(950)))` rend
     950, et `mod.total_clos(l(mod.arrondi(1500)) + l(mod.arrondi(950)))` rend 2450 ;
   - « total_clos : ni plage, ni date, ni pied » : `mod.total_clos(l("non mesuré"))` rend 0, et
     `mod.total_clos('<td class="mono"><strong>≈3,8k (3 812)</strong></td><td class="mono">≈0,00 $</td>')`
     rend 0.
   Lance les tests ; cite la ligne `ÉCART:`.
2. `BRUT` relit aussi une cellule `<td class="mono">` faite de chiffres seuls ; `total_clos` la
   somme. Son commentaire le dit.
3. `cmd_clore` perd son rattrapage (ligne 2026) : `total = total_clos(corps)`.
Tu ne commites pas : le chef le fera.

**Critère de fin**
`py scripts/test-vlp.py` rend `OK` ; ton compte rendu cite l'`ÉCART:` de l'étape 1. Sur la vraie
feuille, `total_clos` rend toujours 439 668 779 :
`py -c "import importlib.util as u;s=u.spec_from_file_location('v','scripts/vlp.py');m=u.module_from_spec(s);s.loader.exec_module(m);h=open('context AI/artefacts/feuille-de-route.html',encoding='utf-8').read();d,f=m.zone(h,'clos','<tbody>'+chr(10),'        </tbody>');print(m.total_clos(h[d:f]))"`
<!-- /FICHE -->

<!-- FICHE:TAR3 -->
## TAR3 [ ] — Lettres prises et résumé : relus comme `clore` les écrit

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (`lettres_prises`, `resume_claude`), `scripts/test-vlp.py` — et
rien d'autre.

**Prompt**
1. Tests d'abord :
   - après « 3 lettres : lettres prises, une et trois lettres mêlées » (`scripts/test-vlp.py:1015`),
     « lettres prises : titre à virgule, lettre sans titre » : `mod.lettres_prises([t])` rend
     `["E", "Q"]` pour `t` = `Lettres de fiche déjà prises : E (Un), Q (Tests, CI (rapide)). Un
     nouveau chantier en choisit une autre.` ; `["A"]` pour `… prises : A. Un nouveau chantier…` ;
     `[]` pour `… prises : aucune. Un nouveau chantier…` ;
   - après les tests « résumé : … » (lignes 743 à 753), « résumé : sur une ligne, relu par
     ENTREE_CLOS » : `resume_claude` avec le texte `"deux lignes\nici"`, lettre `Q`, date
     `2026-09-24`, écrit `- Clos le 2026-09-24 : deux lignes ici (chantier Q).`, et
     `mod.ENTREE_CLOS` la reconnaît.
   Lance les tests ; cite la ligne `ÉCART:`.
2. `lettres_prises` lit entrée par entrée : les entrées se séparent aux virgules **hors
   parenthèses** ; la lettre est le premier mot d'une entrée s'il fait 1 à 3 majuscules, suivi
   d'une parenthèse ouvrante ou de rien (le point final ôté).
3. `resume_claude` réduit les blancs du texte, retours à la ligne compris, à une espace.
Tu ne commites pas : le chef le fera.

**Critère de fin**
`py scripts/test-vlp.py` rend `OK` ; ton compte rendu cite l'`ÉCART:` de l'étape 1.
`py scripts/vlp.py feuille . --verifier` rend `lettres 35` (34 prises, plus `TAR` en cours) et
`identique`.
<!-- /FICHE -->
