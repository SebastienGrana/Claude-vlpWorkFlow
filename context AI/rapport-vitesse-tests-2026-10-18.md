# La vitesse des tests — où on en est (2026-10-18)

Rapport demandé pendant l'enchaînement `REF55 → REF10`. Rien n'est changé dans le code par ce rapport.

## 🖼️ L'image simple

- La suite de tests, c'est surtout **des milliers de petits lancements de `git`**.
- Chaque lancement coûte peu, environ **43 ms**, mais ils sont **plus de 5 000** : ça fait des minutes.
- Comme une caisse de supermarché : chaque article passe vite, mais **le caddie est énorme**.
- Le remède n'est pas de passer les articles « à la fin » : c'est **en passer moins**, ou **ouvrir plusieurs
  caisses** en même temps (le parallèle).

## ✅ Établi — ce qui a été mesuré

### Avant hier soir (2026-10-16, note `122`, section « Mesures de durée »)

- Suite entière : **313 s**, seule sur la machine, protection Windows coupée.
- **5 094 `git`** sur 5 139 sous-processus (**99 %**).
- Les **89 groupes qui appellent `git`** font **299,4 s sur 313** (**96 %**).
- `tester_matin` seul : **2 234 `git`** (**44 %**), **95,6 s**.
- La protection Windows coûte **+ 40 s** (313 → 353 s), surtout sur la lecture de fichiers, presque pas
  sur `git` (43 → 44 ms par appel).
- `test-boucle.py`, lancé en fond dès le début : **179 s**. C'est le **plancher** : la suite ne peut pas
  finir avant lui.

### Hier soir et cette nuit (`REF19`, note `122`, lignes 712–743)

| Ce qui tourne | Avant | Après |
|---|---|---|
| `test_matin.py` seul | 57 499 ms · 2 233 `git` | 53 156 ms · 2 119 `git` |
| pytest entier | 68 484 ms | **40 865 ms** (`-n 4`, 4 caisses) |
| suite entière (`test-vlp.py`) | **253 s** · 13 521 `git` | **200 s** · 13 395 `git` |

- ✅ Gain réel : **−53 s, soit −21 %**.
- ➡️ Il vient **surtout du parallèle** : pytest tourne en fond (le « pont ») pendant le reste de la suite.
- ⚠️ La copie du dépôt modèle n'a retiré que **126 `git`** sur 13 521 : **le nombre de `git` n'a presque
  pas baissé**.
- Pourquoi : les `git` de `matin` viennent de **`vlp.py matin` lui-même** (fusions, branches), pas de la
  préparation des tests.

⚠️ Deux comptes de `git` qui ne se comparent pas : **5 094** (2026-10-16, compté par groupe dans
`test-vlp.py`) et **13 521** (2026-10-18, compté sur tout Python, `test-boucle.py` et pont compris). La
méthode a changé entre les deux ; je ne les réconcilie pas.

## ❌ Un goulet que j'ai ajouté moi-même, aujourd'hui

- Après chaque `test-vlp.py`, j'ai relancé **`uv run pytest -q` en série** : **63,7 s** (REF55) et
  **67,1 s** (REF56), sorties lues.
- C'était **un doublon** : `test-vlp.py` lance déjà pytest en `-n 4` par son pont, et échoue si pytest
  échoue (note `122`, ligne 739).
- ➡️ Environ **65 s perdues par fiche**. Je l'arrête **dès la fiche en cours** (REF57).

## 🟡 « Les `git` à la fin, pas au milieu » — ce que je sais et ce que je ne sais pas

- ❓ **Je ne sais pas** ce qui s'est dit ce matin : je n'étais pas dans cette conversation.
- Le dépôt n'en garde **aucune trace** : le commit `66e6efa` (réponses au rapport de la nuit) ne touche la
  note `122` que pour garder la dépendance de `REF19`.
- 💡 Mon hypothèse : vous pensez au **pont**. Il part **au début** et se **récolte à la fin**. C'est lui
  qui a fait gagner les 53 s.
- Rien de mesuré ne dit qu'un `git` « au milieu » coûte plus qu'un `git` « à la fin ». Ce qui coûte, c'est
  **leur nombre**, et le fait que **la plupart tournent l'un après l'autre**.

## ➡️ Ce qui est prévu dans le chantier `REF`

| Fiche | Ce qu'elle fait pour la vitesse | Quand |
|---|---|---|
| `REF50`, `REF51` | migrer le reste de `test-vlp.py` (≈ **160 s** en série) vers pytest, donc en parallèle | après toute la découpe `REF44` → `REF49` |
| `REF52` | migrer les fichiers à tiret, dont `test-boucle.py` | après `REF51` |
| `REF8`, `REF10` | couverture, tests en lecture seule | ⚠️ **rien pour la vitesse** : la couverture peut même ralentir |

## 💡 Proposé — à trancher par vous, pas fait

1. **Remesurer `test-boucle.py`** : à 179 s le 2026-10-16, il est presque aussi long que la suite entière
   (200 s). S'il n'a pas baissé, migrer `test-vlp.py` en parallèle ne gagnera **presque rien** tant qu'il
   reste le plancher.
2. **Avancer `REF50`–`REF51`** avant `REF8` et `REF10` ? Impossible tel quel : ils dépendent de la découpe
   `REF44`–`REF49`. Changer cet ordre serait votre décision.
3. **Réduire les `git` de `vlp.py matin`** dans ses tests (dépôts plus petits, moins de cas qui fusionnent) :
   aucune fiche ne le prévoit aujourd'hui.

## ❓ Où part le temps — et pourquoi des « tests unitaires » si lents ?

Question de l'utilisateur, le 2026-10-18 après-midi.

- ✅ **La plupart de ces tests ne sont pas des tests unitaires** : ce sont des **tests d'intégration**.
- Un test unitaire essaie une fonction seule, avec des données en mémoire : quelques millisecondes.
- Ici, un test typique **crée un vrai dépôt Git**, y fait des commits, des branches, des worktrees, puis lance
  la vraie commande `vlp.py`, qui appelle `git` à son tour.

Les chiffres (passage B, 313 s, 2026-10-16) :

| Ce qui tourne | Temps | Part |
|---|---|---|
| les **89 groupes qui appellent `git`** | **299,4 s** | **96 %** |
| les **77 autres** | **13,4 s** | 4 % |
| dont 123 groupes sous 1 s | 30,3 s à eux tous | — |
| `test-boucle.py`, en parallèle dès le début | **179 s**, dont sa partie `canal` 160,5 s | le plancher |

- ➡️ Les vrais tests unitaires du kit existent et vont vite : **13,4 s** pour 77 groupes.
- ➡️ Le temps part dans **5 094 lancements de `git`** à **≈ 43 ms** chacun, et `76 git init`.

### Pourquoi le code oblige à tester ainsi

- 💡 Mon analyse, pas une mesure : dans `vlp_coeur.py`, **la décision et l'appel à `git` sont mêlés** dans la
  même fonction. Exemple : `retirer_worktree` lit `git status`, décide, puis appelle `git worktree remove`.
- Pour vérifier la décision, il faut donc un vrai dépôt.
- La méthode connue s'appelle « **noyau fonctionnel, coquille impérative** » (functional core, imperative shell) :
  - le **noyau** décide, à partir de textes en mémoire : testé en millisecondes, sans `git` ;
  - la **coquille** lance `git` et passe ses sorties au noyau : quelques tests d'intégration suffisent.
- 🟡 **Aucune fiche ne le prévoit aujourd'hui**. La découpe `REF44`–`REF49` déplace le code en modules, mais
  sans séparer décision et `git`. Ce serait un chantier à part, ou un ajout à la découpe : votre décision.

## Sources

- `context AI/122-qualite-code-tests.md` : « Mesures de durée — nuit du 2026-10-15 au 16 » (lignes 218–289),
  et le bilan de `REF19` (lignes 712–743).
- Cette séance : sorties de `uv run pytest -q`, 97 et 100 tests, 63,74 s et 67,08 s.
