# Ce que les 22 chantiers ont changé — bilan chiffré

**QUAND LIRE** : on doit expliquer le kit à quelqu'un — d'où il vient, ce qu'il
sait faire aujourd'hui qu'il ne savait pas faire avant, et ce qu'il ne promet
toujours pas. Pour choisir le prochain chantier, c'est `12-audit.md` ; pour
reprendre le fil, `08-etat.md`.

**Périmètre** : du commit `cf59276` (l'audit) au commit `1589346` (clôture du
chantier Q). **128 commits · 22 chantiers ouverts et clos · plugin 3.1.0 →
3.4.2 · ≈ 245 M de tokens, ≈ 210 $** dont ≈ 15 $ de sondes et d'evals.

Chaque chiffre de ce fichier a sa source : le bloc **Mesuré** de la fiche qui
l'a produit, ou la table de `12-audit.md`. Rien n'est estimé sauf les deux
coûts marqués « ≈ » des chantiers Y et U, dont les pages ne portent pas de
montant.

**Page publiée** (la même chose, lisible sans ouvrir de session, à donner au
groupe) : <https://claude.ai/artifact/9bA9VftEvzmTi2t32VmYn3>

## 1. Le point de départ — ce que l'audit a trouvé

`12-audit.md`, écrit le 2026-09-17 avant le premier de ces chantiers :

- **11 bugs** : `/vlp:check` cherchait un libellé inexistant ; `$1`/`$2`
  étaient substitués avant que le modèle lise ; l'index d'un projet neuf
  citait des fichiers que `/vlp:init` ne créait pas ; deux formats de chemin
  dans les lignes `**Session**` ; pas de `.gitignore`.
- **7 fragilités** : les commandes se découpaient l'une l'autre au `sed` sur de
  la **prose** — ça cassait en silence à la première reformulation, et c'était
  déjà arrivé ; la même règle vivait dans 5 à 7 fichiers ; la page d'un
  chantier était **retapée à la main**, 130 lignes de HTML à 120 k de contexte ;
  le kit n'avait ni test ni eval.
- **Une mesure fausse** : la première table de coûts comptait les lignes
  `assistant` — erreur de **×1,7 à ×4,6**.
- **`/vlp:enchainer` abandonné**, coût connu mauvais, livré « tel quel » à un
  groupe qui clone.

Le constat qui a tout réorienté : **le coût est dans les tours, pas dans les
lignes**. Une fiche = 28 à 66 tours, 22 à 82 appels, 1,06 à 5,73 $ ; la
commande elle-même ne pèse que ~8 % du premier tour.

## 2. Les cinq bascules

**① Du bavardage au script.** `scripts/vlp.py` : 1 543 lignes, 17
sous-commandes, zéro appel modèle, 100 assertions dans `test-vlp.py`. Extraire
une fiche, valider des marqueurs, régénérer une page, resommer un total — c'est
déterministe, donc c'est du code, donc c'est testé.

**② De la règle répétée à la règle unique.** La doctrine tient en trois
documents (`README.md`, `methode-chantier.md`, `ARTEFACTS.md`) et chaque nombre
vit dans `vlp.py` seul : `SEUIL_CLAUDE 80`, `SEUIL_CHANTIER 50`,
`SEUIL_INDEX 80`, `CLOS_GARDES 5`, page 250 · fiche 50 · socle 80.

**③ De la mesure en lignes à la mesure en tours et en dollars.**
`mesure-tokens.py` compte un tour = un `message.id`, pondère sur la grille de
prix, et sort des dollars. C'est ce qui a permis d'écarter trois idées
séduisantes **aux chiffres** : `disable-model-invocation` (score 0,5 contre 1),
un hook `SessionStart` (+1 974 tokens par tour), et le chantier X entier —
sondé, puis **renoncé**, rien d'appliqué, la recette laissée en TODO.

**④ De « ça devrait marcher » à « c'est sondé ».** Quatre filets superposés :
le hook `PostToolUse` attrape un fichier de fiches invalide **à l'écriture** ;
`test-vlp.py` attrape une régression de la mécanique ; `claude plugin eval`
attrape une commande qui ne tient plus sa promesse (Windows 1/1, Ubuntu 4/4) ;
le **bac** attrape un refus de permission réel — il copie le plugin, écrit un
projet sans `.git`, et rejoue le kit avec `--tools` réduits. Retirer `Bash`
**est** la simulation d'un poste sans Git.

**⑤ Du kit « Windows + Git » au kit « Python seul ».**

| | Avant | Après |
|---|---|---|
| Prérequis | Git for Windows obligatoire | **Python 3 seul**, Git facultatif |
| Hook | `sh` muet (exit 1) sans Git Bash | paire `exec python3` + `py` |
| Corps des skills | 15 appels `sh` | **0** |
| `/vlp:tache` sous PowerShell | 9 refus | **1** |
| `/vlp:enchainer` sans Git | 3 refus, 0 fiche sur 2 | **0 refus, 2 sur 2** |

## 3. Ce qui n'était pas possible, et l'est devenu

| Avant | Maintenant |
|---|---|
| Faire tourner le kit sans Git | prouvé deux fois, en bac sans `.git` (chantiers Y, Q) |
| Savoir ce que coûte une fiche | tours, appels, contexte, tokens pondérés, dollars |
| Faire confiance à une page publiée | régénérée par script ; `--verifier` dit si elle a dérivé |
| Attraper un fichier de fiches cassé | le hook le dit à l'écriture |
| Modifier une commande sans en casser une autre | plus de `sed` sur la prose d'un voisin |
| Tester le kit | `validate` + 100 assertions + evals sur deux systèmes |
| Ouvrir ou clore sans 5 à 12 tours d'écriture | `vlp.py ouvrir` et `clore` : 1 à 3 tours |
| Empêcher les fichiers de tête de grossir | seuils + compaction : `CLAUDE.md` 118 → 79 |
| Poser un projet neuf sans lien mort | corrigé, vérifié par eval (`/vlp:init` score 1) |
| Utiliser `/vlp:enchainer` | réparé par la skill forkée `vlp:jouer` |

## 4. Les gains chiffrés

| Mesure | Avant | Après | Source |
|---|---|---|---|
| `/vlp:tache`, corps de la commande | 377 lignes | 150 | chantier R |
| `/vlp:tache`, appels prescrits par fiche | 14 | 5 | chantiers R, S |
| Découpage au `sed`/`awk` entre commandes | 11 | 0 | chantiers S, Y |
| Chef de `/vlp:enchainer` | 15 tours · 14 appels | 5 tours · 7 appels | chantiers L, A |
| Refus, `/vlp:tache` sous PowerShell | 9 | 1 | chantier U |
| Refus, `/vlp:enchainer` sans Git | 3 (0 fiche jouée) | 0 (2 sur 2) | chantier Q |
| Entrées `allowed-tools` | 55 | 36 | chantier Q |
| Entrées `allowed-tools` dépareillées | 11 | 0 | chantier Q |
| `CLAUDE.md` · `CHANTIER.md` | 118 · 71 | 79 · 47 | chantier J |
| Coût d'une fiche mécanique | 0,42 $ à la main | 0,176 $ enchaînée | chantiers U, Q |
| Assertions de la mécanique | 0 | 100 | chantiers S → Y |
| Evals | 0 | Windows 1/1, Ubuntu 4/4 | chantiers V, W |

## 5. Les cinq phrases pour expliquer le changement

1. **On ne corrige plus ce qu'on n'a pas mesuré.** Trois bonnes idées ont été
   rejetées sur un chiffre ; sans instrument, on les aurait gardées.
2. **Ce qui est déterministe est devenu du code.** Un modèle qui retape
   130 lignes de HTML à chaque fiche, c'est cher et ça dérive.
3. **Le kit ne demande plus que Python.** Avant, un collègue sans Git for
   Windows ne pouvait rien lancer — et personne ne le savait, parce que le hook
   échouait *en silence*.
4. **Une règle vit à un seul endroit.** Le kit avait souffert de six copies
   divergentes de la même règle.
5. **Le coût est dans les tours, pas dans les lignes.** C'est la phrase qui
   explique tout le reste.

## 6. Ce qui n'est toujours pas prouvé

- **macOS n'est pas sondé.** Écrit dans le `README.md`.
- **PowerShell 5.1 n'est pas sondable** tant que `pwsh` 7 est installé.
- **Le gain de `/vlp:enchainer` a deux conditions** : des fiches mécaniques, et
  aucun `RETOUR` — un seul annule le gain. Les deux mesures d'enchaînement
  complet portent sur des fiches triviales en `-p`, où le socle de session est
  mince ; en session réelle le chef démarre à ~78 000 tokens.
- **Le contexte d'un sous-agent forké n'est pas journalisé** : on ne peut pas
  relire ce qu'il a reçu, seulement son compte rendu.
- **Un `sed` reste dans la méthode** : `skills/tache/SKILL.md` apprend aux
  fiches à citer une plage par `sed -n 'A,Bp'`, inutilisable sans Git.
