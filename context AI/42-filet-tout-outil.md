> **QUAND LIRE** : on joue une fiche `FIL*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache FIL<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier FIL — Le filet tire après tout outil

**À quoi il sert.** Le filet de `SAG` ne prévient le sous-agent qu'après un `Write` ou un
`Edit`, et se tait sur un chemin de plus de 260 caractères. `FIL` le branche sur tout outil,
et lui fait lire les chemins longs.

**Fait.** Rien. Ouvert le 2026-09-24, cadré en 3 fiches, `FIL1` à jouer.

## Le socle commun

| Nom | Où | Ce qu'il fait ou rend |
|---|---|---|
| `cmd_filet` | `scripts/vlp.py:697` | muet hors sous-agent (`agent_type` sans `fiche`, ou pas d'`agent_id`) ; sinon compte les tours, et avertit si `0 < maxTurns − tours <= SEUIL_FILET` |
| `SEUIL_FILET` | `scripts/vlp.py:694` | 3 — ce nombre ne vit qu'ici |
| `comptoir_tours` | `scripts/vlp.py:752` | les `message.id` distincts porteurs d'`usage` |
| `lire_max_turns` | `scripts/vlp.py:777` | `maxTurns` du frontmatter de `agents/fiche.md` — lu, jamais recopié |
| la transcription du sous-agent | `<transcript_path sans .jsonl>/subagents/agent-<agent_id>.jsonl` | `transcript_path` est celle du chef (`SAG2`) |
| `ouvrir` | `scripts/mesure-tokens.py:111` | `open` avec le préfixe `\\?\` dès 260 caractères, sous Windows |
| `mesure()` | `scripts/vlp.py:815` | charge `mesure-tokens.py` une fois — le tiret interdit `import` |
| l'entrée `PostToolUse` | `hooks/hooks.json` | matcher `Write\|Edit`, quatre commandes : `python3` puis `py`, pour `filet` puis pour `hook` |
| les tests du filet | `scripts/test-vlp.py`, `filet_test` | `py scripts/test-vlp.py` → « OK » |

**Mesuré à l'ouverture, le 2026-09-24.**
- Filet à vide, hors sous-agent — `echo {} | py scripts/vlp.py filet` : 332 · 320 · 310 · 292 ·
  318 ms. `python3` qui échoue (alias du Microsoft Store) : 164 · 159 · 156 ms ; `py -c pass` :
  146 · 151 · 136 ms.
- Session d'ouverture : 145 appels d'outils, dont 18 `Edit` ; 18 `hook_non_blocking_error` au
  transcript, aucune reçue par le modèle.
- Essai `SAG4` : averti après le tour 8 (`Write`), « 2 tours restants » ; le tour 7 était un
  `Read`. Chemin du sous-agent : 254 caractères. Détail : journal du 2026-09-24.

**Décidé au cadrage.** Le filet passe sur tout outil, dans une entrée `PostToolUse` à lui ;
`vlp.py hook` garde la sienne. Son prix — un filet à vide et un `python3` qui échoue à chaque
appel d'outil, dans toute session — est accepté, et mesuré avant et après.

**Les règles du chantier.**
- Tout `claude -p` se chiffre en $ **avant**, et le chiffre s'annonce ; `--allowedTools "Skill"`,
  sinon `Skill` est refusé (`SAG4`) ; jamais `bypassPermissions` : il cache les refus.
- Le plugin est chargé en place : `hooks/hooks.json` changé ne se voit qu'après
  `/reload-plugins`, ou dans un processus neuf (`claude -p`).
- Après tout changement de `hooks/hooks.json`, `claude plugin validate`, comme le lance
  `.githooks/pre-commit` ; l'exécutable de l'app : `ls -d "$APPDATA"/Claude/claude-code/*/claude.exe`.
- Chaque verdict va au journal de `context AI/08-etat.md`, daté, comptes bruts et commande
  rejouable à côté.

**Ce qu'on ne fait pas.** Toucher au matcher de `vlp.py hook`, à `maxTurns`, au modèle du
sous-agent. Le bruit `python3` est le n° 39 `PYT` ; la case non relue par le chef, le n° 38 `CAS`.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `FIL1` | Vérifier et mesurer, avant d'écrire | rien |
| `FIL2` | Brancher le filet sur tout outil et sur les chemins longs | `FIL1` |
| `FIL3` | Éprouver le filet après un `Read`, à plafond bas | `FIL2` |

Rien ne se joue en parallèle : chaque fiche s'appuie sur ce que la précédente a établi.

---

<!-- FICHE:FIL1 -->
## FIL1 [ ] — Vérifier et mesurer, avant d'écrire

**Dépend de** : rien.
**Fichiers** : `hooks/hooks.json`, `scripts/mesure-tokens.py` (`ouvrir`) — et rien d'autre.

**Prompt**
Trois inconnues se tranchent ici, avant tout code. Aucune ne se devine.
1. **La syntaxe « tout outil ».** Lis la doc officielle des hooks
   (https://code.claude.com/docs/en/hooks) : quel `matcher` couvre tous les outils —
   `*`, vide, ou absent ? Cite la phrase, avec le lien et la date.
2. **Ensemble, ou l'une après l'autre.** Même page : les commandes d'une même entrée
   tournent-elles en parallèle ? Si la doc ne tranche pas, une sonde : une copie du plugin
   dans le scratchpad (comme la sonde de `SAG2`), deux commandes qui dorment 1 s en notant
   leur début et leur fin dans un fichier, un `claude -p` qui appelle un outil — chiffrée
   avant (≈ 0,09 $ : la tentative de `SAG4` sans sous-agent a coûté 0,0884613 $). Des
   intervalles qui se chevauchent : parallèle.
3. **Un vrai chemin de plus de 260 caractères.** Sous Windows, crée dans le scratchpad un
   fichier au bout d'un tel chemin (par le préfixe `\\?\`), puis note ce que rendent
   `os.path.isfile` et `open` sans préfixe, et `ouvrir`.
Enfin, rejoue cinq fois la mesure du filet à vide du socle : c'est la référence d'avant.
Au journal : les trois réponses et leurs preuves, ce que chacune impose à `FIL2`, et les
cinq temps. Rien ne change dans le kit.

**Critère de fin**
Le journal porte, datés : la syntaxe « tout outil » citée avec son lien ; « parallèle » ou
« en série », avec la phrase de la doc ou les heures de la sonde ; la longueur du chemin
long et ce que rendent `isfile`, `open` et `ouvrir` ; cinq temps du filet à vide, en ms.
<!-- /FICHE -->

---

<!-- FICHE:FIL2 -->
## FIL2 [ ] — Brancher le filet sur tout outil et sur les chemins longs

**Dépend de** : `FIL1`.
**Fichiers** : `hooks/hooks.json`, `scripts/vlp.py` (`cmd_filet`, `comptoir_tours`),
`scripts/test-vlp.py` (tests du filet), `scripts/mesure-tokens.py` (`ouvrir`) — et rien d'autre.

**Prompt**
Relis au journal ce que `FIL1` a établi ; ne le revérifie pas.
1. Dans `hooks/hooks.json`, sors les deux commandes de `filet` (`python3` puis `py`) dans une
   entrée `PostToolUse` à elles, au matcher « tout outil » de `FIL1`. L'entrée des écritures
   garde les deux commandes de `hook`, matcher inchangé.
2. Dans `cmd_filet`, la transcription du sous-agent se teste et se lit par le préfixe des
   chemins longs : `ouvrir` de `mesure-tokens.py`, chargé par `mesure()` — réutilisé, jamais
   recopié. Le chargement vient **après** le test « sous-agent ou non » : un filet à vide ne
   le paie pas.
3. Dans `scripts/test-vlp.py` : un test lit `hooks/hooks.json` et vérifie les deux entrées —
   `filet` sur tout outil, `hook` sur les écritures, chacun en paire `python3` + `py` ; un test
   fait avertir le filet sur une transcription au bout d'un vrai chemin de plus de 260
   caractères, construit comme dans `FIL1` — hors Windows, le test dit pourquoi il saute.
4. Remesure cinq fois le filet à vide, comme `FIL1` : le temps ne doit pas avoir grossi.

**Critère de fin**
`py scripts/test-vlp.py` rend « OK » avec les deux nouveaux tests ; `claude plugin validate`
passe ; le journal donne les cinq temps du filet à vide, avant (`FIL1`) et après, en ms.
<!-- /FICHE -->

---

<!-- FICHE:FIL3 -->
## FIL3 [ ] — Éprouver le filet après un `Read`, à plafond bas

**Dépend de** : `FIL2`.
**Fichiers** : `agents/fiche.md` (frontmatter) — et rien d'autre ; la commande de l'essai est
dans l'entrée `SAG4` du journal de `context AI/08-etat.md` (2026-09-24).

**Prompt**
Rejoue l'essai de `SAG4` pour prouver le cas qu'il a manqué : un avertissement juste après un
`Read`. Chiffre-le avant, et annonce le chiffre (`SAG4` : 0,0885 $).
1. Reconstruis le bac dans le scratchpad : un `CHANTIER.md` qui pointe un fichier de fiches, et
   une fiche factice où **chaque tour est un `Read`** — douze fichiers posés d'avance, lus un
   par tour, un seul appel d'outil par tour. Vérifie d'abord que `vlp.py extraire` y lit la fiche.
2. Abaisse `maxTurns` à 10 le temps de l'essai ; lance `claude -p` dans le bac, avec la commande
   de `SAG4` ; remets `maxTurns` à 80, et vérifie-le par `Read`.
3. Dans la transcription du sous-agent, compte : les tours ; l'outil du tour qui précède le
   premier avertissement, et ce que dit cet avertissement ; les avertissements en tout ; les
   `hook_non_blocking_error`, pour combien d'appels d'outils ; le premier mot et le
   `stop_reason` du dernier message.
4. Au journal : la commande, le coût réel, ces comptes bruts, et la dernière ligne du
   sous-agent, citée telle quelle.
**Filet muet après un `Read`** : rends `RETOUR` avec la transcription — c'est `FIL2` qui est
à reprendre.

**Critère de fin**
La transcription montre un premier avertissement, « 3 tours restants », juste après un `Read`,
puis un dernier message qui commence par `RETOUR`, sur `end_turn` ; le journal le cite avec ses
comptes bruts ; `maxTurns` est revenu à 80, vérifié par `Read`.
<!-- /FICHE -->
