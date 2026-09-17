> **QUAND LIRE** : on joue une fiche `Z*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache Z<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier Z — Une GARDE au lieu d'un traceback

**À quoi il sert.** Une sous-commande de `vlp.py` qui lit un chemin venu de
`CHANTIER.md` plante quand ce chemin est faux, au lieu de rendre `GARDE:` —
mesuré sur Cairn-VlpLib : `carte` garde proprement, `feuille` rend un
`FileNotFoundError`. Après ce chantier, aucun chemin de `CHANTIER.md` ne peut
plus faire tomber une sous-commande.

**CLOS** le 2026-09-17. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** Z1..Z4 (2026-09-17) : Toute lecture d'un chemin venu de CHANTIER.md rend une GARDE: en clair et sort 1, au lieu d'un traceback — prouvé sur Cairn-VlpLib.

## Le socle commun

Le projet **est** le kit : `scripts/vlp.py` (1543 lignes) et sa suite
`scripts/test-vlp.py` (108 cas). La suite se lance `py scripts/test-vlp.py`
depuis la racine ; elle imprime `OK` et sort 0, ou le premier écart et sort 1.
Un cas s'ajoute avec `verifier(nom, cond, sortie)` (`test-vlp.py:50`) et
`appel(argv)` → `(code, sortie)` (`test-vlp.py:102`).

**La convention de garde, telle qu'elle existe déjà** : la sous-commande écrit
`GARDE: <phrase en clair>` sur sa sortie et **rend 1**. `vlp.py` en porte 45.
C'est la forme à tenir : ni exception, ni message sur `stderr`, ni code 0.

| Symbole | Où | Ce qu'il rend |
|---|---|---|
| `lire(chemin)` | `vlp.py:129` | le texte — **lève `FileNotFoundError`** si absent |
| `lignes_de(chemin)` | `vlp.py:134` | les lignes — même risque |
| `champ(lignes, nom, defaut)` | `vlp.py:992` | la valeur d'une ligne `- **nom** : valeur` |
| `fichier_courant(texte)` | `vlp.py:163` | le chemin « fichier de fiches courant » |
| `equipe(d)` | `vlp.py:143` | vrai si `d` porte `CHANTIER.md` |
| `feuille(...)` | `vlp.py:1051` | garde l'état par `ValueError`, **pas** le courant |
| `cmd_feuille` | `vlp.py:1101` | `try/except ValueError` seul — d'où le trou |
| `cmd_clore` / `cmd_ouvrir` | `vlp.py:1152` / `1327` | lisent `index`, `fichier d'état`, courant |
| `cmd_renvois` / `cmd_page` | `vlp.py:946` / `865` | mêmes lectures |

**Le tableau du recensement** — sous-commande, cas cassé, sortie et code
**avant** correction : écrit ici par `Z1`, lu par `Z2`.

| Cas | Sous-commande | Sortie | Code | Notes |
|---|---|---|---|---|
| 1 : fiches courant inexistant | carte | `GARDE: fichier de fiches introuvable` (code 0 aussi) | 0 | Ne garde pas proprement |
| 1 | feuille | `GARDE: feuille de route introuvable` | 1 | ✅ Garde bien |
| 1 | renvois | `POIDS ... · RENVOIS ...` | 0 | Ne teste pas fiches courant |
| 1 | page | `GARDE: page introuvable` | 1 | ✅ Garde bien |
| 1 | ouvrir | `GARDE: fichier de fiches introuvable : test.md` | 1 | ✅ Garde bien |
| 1 | clore | `FileNotFoundError: … context AI/nonexistent.md` | 1 | ❌ Traceback au lieu de GARDE |
| 2 : ligne déborde | carte | `PROCHAINE=aucune` | 0 | Parsing réussi malgré cassure |
| 2 | feuille | `GARDE: feuille de route introuvable` | 1 | ✅ Garde bien |
| 2 | renvois | `POIDS ... · RENVOIS ...` | 0 | Ne teste pas fiches courant |
| 2 | page | `GARDE: page introuvable` | 1 | ✅ Garde bien |
| 2 | ouvrir | `GARDE: fichier de fiches introuvable : test.md` | 1 | ✅ Garde bien |
| 2 | clore | `GARDE: aucune fiche dans context AI/36-gardes.md` | 1 | ✅ Garde bien |
| 3 : état inexistant | carte | `PROCHAINE=aucune` | 0 | Ne teste pas état |
| 3 | feuille | `GARDE: feuille de route introuvable` | 1 | ✅ Garde bien |
| 3 | renvois | `POIDS ... · RENVOIS ...` | 0 | Ne teste pas état |
| 3 | page | `GARDE: page introuvable` | 1 | ✅ Garde bien |
| 3 | ouvrir | `GARDE: fichier de fiches introuvable : test.md` | 1 | ✅ Garde bien |
| 3 | clore | `GARDE: aucune fiche dans context AI/36-gardes.md` | 1 | ✅ Garde bien |

**Ce qu'on ne fait pas ici.** Pas de refonte des sous-commandes ni de nouveau
format de sortie. Pas la remise à niveau des projets équipés (chantier n° 22 de
la TODO). Pas le bruit « Python est introuvable » du relais `python3` de la
carte : c'est un autre sujet, il reste en TODO.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `Z1` | Recenser le trou sur un bac cassé | rien |
| `Z2` | Garder toute lecture d'un chemin de `CHANTIER.md` | `Z1` |
| `Z3` | Retirer le `sed` de `skills/tache` | rien |
| `Z4` | Prouver la réparation sur Cairn-VlpLib | `Z2` |

`Z3` est indépendante : elle peut se jouer à n'importe quel moment. `Z1 → Z2 →
Z4` est une chaîne stricte.

---

<!-- FICHE:Z1 -->
## Z1 [x] — Recenser le trou sur un bac cassé

**Session** : d2d18d7b-ff08-4028-80c6-3923e21fedbc
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (lecture seule), `context AI/36-gardes.md` (le
socle, à compléter) — et rien d'autre. Le bac se crée dans le dossier
temporaire de la session, jamais dans un projet réel.

**Prompt**
Tu ne corriges rien dans cette fiche : tu mesures.

Fabrique trois bacs équipés, chacun cassé d'une seule façon :

1. la ligne « fichier de fiches courant » nomme un fichier qui n'existe pas ;
2. cette même ligne déborde sur plusieurs lignes (le cas réel de Cairn-VlpLib) ;
3. la ligne « fichier d'état » nomme un fichier qui n'existe pas.

Sur chacun, lance les sous-commandes qui lisent un chemin venu de
`CHANTIER.md` : `carte`, `feuille`, `renvois`, `page`, `ouvrir`, `clore`.
Relève pour chacune la **sortie brute** et le **code de sortie** — un traceback
compte comme sortie, recopie sa dernière ligne.

Remplis ensuite la table du socle commun de ce fichier, à la place de la ligne
« *(à mesurer par Z1)* » : une ligne par couple (sous-commande, cas), avec ce
qui sort et le code. Nomme en clair celles qui gardent déjà bien — elles
servent de modèle à `Z2`, elles ne seront pas touchées.

**Critère de fin**
Le socle porte la table remplie, et tu affiches le compte brut : « N couples
mesurés, G gardent déjà (`GARDE:` + code 1), P plantent ». La somme G + P vaut N.
<!-- /FICHE -->

---

<!-- FICHE:Z2 -->
## Z2 [x] — Garder toute lecture d'un chemin de `CHANTIER.md`

**Session** : 2d00d8f8-23cd-4d1e-a99a-0cf972af6abe
**Dépend de** : `Z1` — sa table, dans le socle, dit quoi corriger.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Fais en sorte qu'aucun chemin venu de `CHANTIER.md` ne puisse plus faire tomber
une sous-commande.

La règle vit à **un seul endroit** : n'ajoute pas un `try/except` par fonction.
Donne-toi un point de lecture unique — par exemple un `lire_du_projet(...)` qui
lève la même erreur gardée que `feuille()` utilise déjà pour le fichier d'état
— et fais passer par lui toutes les lectures relevées par `Z1`. Chaque
sous-commande concernée attrape cette erreur, écrit `GARDE: <phrase en clair
nommant le libellé fautif et le chemin>` et rend 1.

Ajoute un cas de test par ligne « plante » de la table de `Z1`, sur le modèle
des cas existants : le code attendu est 1 et la sortie commence par `GARDE:`.

**Critère de fin**
`py scripts/test-vlp.py` imprime `OK` et sort 0 ; tu affiches le compte de cas
avant et après (108 → N). Puis tu rejoues la table de `Z1` sur les mêmes bacs
et tu montres la nouvelle colonne : **0 traceback**, chaque couple qui plantait
rend maintenant `GARDE:` et sort 1.
<!-- /FICHE -->

---

<!-- FICHE:Z3 -->
## Z3 [x] — Retirer le `sed` de `skills/tache`

**Session** : cad30180-1d0e-470c-8ce8-a56b1e89a0f3
**Dépend de** : rien.
**Fichiers** : `skills/tache/SKILL.md` — et les autres fichiers de `skills/`
seulement si le grep ci-dessous les désigne.

**Prompt**
`skills/tache/SKILL.md` apprend encore aux fiches à citer une plage de fichier
par `sed` : inutilisable sur un poste sans Git (relevé hors frontière au
chantier Q). Le kit a déjà de quoi faire sans : `vlp.py extraire`, `vlp.py
socle`, `vlp.py lire`, `vlp.py valider --plan` pour repérer une ligne.

Compte d'abord les occurrences de `sed` et `awk` dans `skills/`, puis remplace
chacune par l'appel `vlp.py` qui rend la même chose. Si une occurrence est un
**exemple destiné à l'utilisateur** et non une consigne exécutée, dis-le et
laisse-la — en justifiant en une ligne.

Vérifie que le gabarit `templates/context AI/fichier-de-fiches.md` ne
contredit pas ce que tu écris : sa ligne « **Maquette** » montre un `sed`.
Aligne-la si elle reste un modèle à copier.

**Critère de fin**
`grep -rn "sed \|awk " skills/` ne rend plus que les occurrences justifiées ;
tu affiches le compte avant et après, et la liste de ce qui reste avec sa
raison.
<!-- /FICHE -->

---

<!-- FICHE:Z4 -->
## Z4 [x] — Prouver la réparation sur Cairn-VlpLib

**Session** : d98b430f-ec71-4508-9675-9ebb341b93ca
**Dépend de** : `Z2`.
**Fichiers** : `C:/Users/znorr/Documents/ProgPerso/Cairn-VlpLib/CHANTIER.md` —
et rien d'autre dans ce projet ; le kit n'est pas modifié par cette fiche.

**Prompt**
C'est le projet réel sur lequel le bug a été mesuré : sa ligne « fichier de
fiches courant » déborde sur plusieurs lignes.

Lance d'abord `carte`, `feuille` et `renvois` sur Cairn-VlpLib **sans rien
toucher**, et colle les sorties : elles doivent désormais rendre une `GARDE:`
en clair, plus aucun traceback.

Remets ensuite la ligne « fichier de fiches courant » droite — une seule ligne,
au format que `fichier_courant` (`vlp.py:163`) sait lire — sans rien changer
d'autre au projet. Relance les trois sous-commandes et colle les sorties.

Si `feuille` signale autre chose ensuite (feuille de route absente ou en
écart), **ne le répare pas** : c'est le chantier n° 22 de la TODO. Note-le en
une ligne.

**Critère de fin**
Les deux jeux de sorties sont affichés côte à côte : avant la remise droite,
`GARDE:` et code 1 ; après, `FEUILLE todo … · encours …` et code 0. Aucun
traceback dans aucun des deux.
<!-- /FICHE -->
