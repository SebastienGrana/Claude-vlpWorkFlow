> **QUAND LIRE** : on joue une fiche `PYT*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache PYT<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier PYT — Un hook n'agit qu'une fois

**À quoi il sert.** Chaque hook du plugin est déclaré deux fois, `python3` puis `py`, pour
tourner partout (TODO n° 39). Là où les deux existent, il agit deux fois : ce soir, chaque
renvoi du gardien et chaque `VALIDE` du hook d'écriture sont arrivés en double. PYT garde la
paire, et fait taire le second.

**Fait.** Rien. Ouvert le 2026-09-25, cadré en 2 fiches, `PYT1` à jouer. Cadré seul :
l'utilisateur dormait ; les 🟡 tranchés ici sont à valider au réveil.

**Session** : ca431cf8-167e-4c10-8bce-210c5f48a675

## Le socle commun

| Fait vérifié | Où |
|---|---|
| mesuré au cadrage, 2026-09-25 : `python3` → `…\WindowsApps\python3.exe`, qui lance `…\pythoncore-3.14-64\python.exe` ; `py` → `…\Programs\Python\Python314\python.exe`. Les deux marchent : le 🟡 « échouent à chaque appel » de la TODO est périmé | `Get-Command`, `sys.executable` |
| `hooks/hooks.json` : 10 entrées, chacune `python3` puis `py`, même `args` — `filet` (PostToolUse, PostToolUseFailure), `hook` (Write\|Edit), `gardien` (PreToolUse Bash\|PowerShell, SubagentStop) | `hooks/hooks.json` |
| les hooks d'un même groupe partent **en parallèle**, et reçoivent la **même** entrée JSON sur stdin | doc Claude Code, hooks ; vu en double le 2026-09-25 (`GAR3`, journal) |
| `cmd_hook(entree, sortie, erreur)`, `cmd_filet(entree, sortie, erreur)`, `cmd_gardien(entree, sortie)` ; aiguillage dans `repartir` | `scripts/vlp.py` |
| tests : `py scripts/test-vlp.py` ; `appel(argv)` appelle `mod.main` dans le même processus ; pyright sur les fichiers touchés ; une fiche de code nomme son mutant | `scripts/test-vlp.py`, `methode-chantier.md` |

Décidé au cadrage, seul : **le premier qui crée le tampon agit**. `repartir` lit l'entrée
d'un hook une fois, en prend l'empreinte, et crée `<temp>/vlp-hook-<empreinte>` en exclusif
(`os.O_CREAT | os.O_EXCL`) : créé, il agit ; déjà là, il se tait (sort 0, rien écrit). Un
tampon de plus de 60 s est retiré au passage. Pourquoi pas un tampon daté (`--relais` de la
carte) : les deux partent ensemble, un test « récent ? » laisse passer les deux.

**Dehors.** Retirer l'une des deux entrées : elle sert sous Linux (pas de `py`) ou sous un
Windows sans alias `python3` ; la paire reste.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `PYT1` | Faire taire le second lancement d'un hook | rien |
| `PYT2` | Le compter en vrai | `PYT1` |

---

<!-- FICHE:PYT1 -->
## PYT1 [x] — Faire taire le second lancement d'un hook

**Session** : ca431cf8-167e-4c10-8bce-210c5f48a675
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Ajoute à `vlp.py` une constante `TAMPON_HOOKS` (le dossier temporaire du système) et une
fonction `premier_lancement(texte)` : empreinte `sha1` du texte, puis création exclusive de
`<TAMPON_HOOKS>/vlp-hook-<empreinte>` ; rend vrai si créé, faux s'il existait ; retire au
passage les `vlp-hook-*` de plus de 60 s ; `TAMPON_HOOKS` à `None` : toujours vrai ; une
`OSError` autre que « existe » : vrai (mieux vaut deux fois que zéro). Dans `repartir`,
pour `hook`, `filet` et `gardien` : lis l'entrée une fois, rends 0 sans rien écrire si ce
n'est pas le premier lancement, sinon passe un `io.StringIO(texte)` à la commande. Mets la
règle dans la docstring du module, une phrase. En tête de `test-vlp.py`, après le chargement
de `mod`, pose `mod.TAMPON_HOOKS = None` (les tests rejouent des entrées identiques). Ajoute
un test : dans un dossier temporaire, deux appels `gardien` sur la même entrée `PreToolUse`
qui commite — le premier refuse, le second est muet ; une entrée différente parle encore.

**Critère de fin**
`py scripts/test-vlp.py` rend `OK`. Mutant : `premier_lancement` qui rend toujours vrai fait
tomber le nouveau test. pyright : 0 erreur sur les deux fichiers.
<!-- /FICHE -->

---

<!-- FICHE:PYT2 -->
## PYT2 [ ] — Le compter en vrai

**Dépend de** : `PYT1`.
**Fichiers** : `context AI/08-etat.md` (journal) — et rien d'autre.

**Prompt**
Se joue **à la main**, par le chef : le compte se lit dans sa propre session. Les hooks
relancent `vlp.py` depuis le disque à chaque appel : le correctif agit sans redémarrage.
Écris une fois un fichier de fiches (un `Edit` d'une ligne blanche, retiré aussitôt), puis
compte dans la transcription de la session les `hook additional context` `VALIDE` de cet
appel ; fais de même pour une écriture d'avant `PYT1`. Écris au journal
(`## 2026-09-25 — PYT2`) : avant / après, en comptes bruts, et la commande de comptage.

**Critère de fin**
Au journal : une écriture d'avant `PYT1` porte 2 `VALIDE`, une d'après en porte 1.
<!-- /FICHE -->
