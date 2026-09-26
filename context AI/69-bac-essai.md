> **QUAND LIRE** : on joue une fiche `BAC*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache BAC<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier BAC — Un bac d'essai par script

**À quoi il sert.** `SAG4` et `FIL3` ont rebâti leur bac à la main, puis compté la
transcription du sous-agent par un script jetable ; `FIL3` y a perdu 0,148 $.
`vlp.py bac` posera le bac en un appel, `vlp.py transcription` en rendra les comptes.

**Estimé.** 1 fiches · ≈3,90 $ — ≈3,90 $/fiche sur 56 clos (le 2026-09-26).

**CLOS** le 2026-09-26. Ne se rejoue pas — ne sert plus qu'à relire son socle.

**Fait.** BAC1..BAC2 (2026-09-26) : vlp.py bac pose le bac d'essai de FIL3 en un appel ; vlp.py transcription compte la transcription d'un sous-agent et retrouve, sur F1 et F2, les chiffres du journal FIL3 — estimé 1 fiches ≈3,90 $ · cadré 2 · joué 2 fiches ≈6,82 $.

**Session** : 109c68a9-2c11-4d5b-94aa-328578a50bff

## Le socle commun

Décidé au cadrage (2026-09-26) : bac **fixe et minimal** ; comptage bâti sur ce
que `vlp.py` lit déjà ; fini quand les tests passent **et** qu'un rejeu sur les
deux vraies transcriptions de `FIL3` retrouve les chiffres de son journal.

**Dehors** : lancer `claude -p`, et baisser `maxTurns` dans `agents/fiche.md` —
ça reste à la main, chiffré avant. Pas d'eval (`EVF`, qui dépend de ce chantier).

| Symbole | Où | Ce qu'il rend |
|---|---|---|
| `comptoir_tours(chemin)` | `scripts/vlp.py:1313` | tours = `message.id` distincts porteurs d'`usage` ; `None` si illisible |
| `mesure().ouvrir(chemin)` | `scripts/vlp.py:1685` | ouvre un transcript, chemins ≥ 260 caractères compris (`FIL1`) |
| `cmd_filet` | `scripts/vlp.py:1255` | le texte de l'avertissement, « Attention : <n> tours restants… » |
| `cmd_valider`, `cmd_extraire` | `scripts/vlp.py:1173`, `:628` | ce que le bac doit passer |
| parseur | `scripts/vlp.py:3377` (`sous = …`), aiguillage après `:3498` | une sous-commande = un `add_parser` + un `if a.cmd ==` |
| docstring | `scripts/vlp.py`, en tête | chaque sous-commande y a sa puce |
| `appel(argv)`, `verifier(nom, cond, sortie)` | `scripts/test-vlp.py:242`, `:64` | lancer une sous-commande, tester sa sortie |

**La transcription** (relevée le 2026-09-26 sur `F1` de `FIL3`) : une ligne JSON par
entrée. `type` `assistant` : `message.id`, `message.stop_reason`, `message.content`
(blocs `tool_use` avec `id` et `name`). `type` `user` : blocs `tool_result`,
`tool_use_id`, `is_error`. Les hooks sont des lignes à `attachment` :
`attachment.type` `hook_additional_context` = un avertissement (`content`,
`hookName`, `toolUseID`) ; `hook_non_blocking_error` = une erreur de hook
(`hookName`, `toolUseID`). Le `toolUseID` relie un hook à son appel d'outil.

**La sortie de `transcription`**, une clé par ligne, dans cet ordre :

```
TOURS=<n>
APPELS=<n> — <outil> <n>, <outil> <n>
AVERTISSEMENTS=<n>
PREMIER_AVERTISSEMENT tour=<n> outil=<nom> is_error=<oui|non> hook=<hookName>
TEXTE=<texte du premier avertissement>
HOOK_ERREURS=<n> pour <n> appels
DERNIER mot=<premier mot du dernier message> stop_reason=<valeur>
DERNIERE_LIGNE=<dernière ligne non vide du dernier message>
```

Aucun avertissement : `PREMIER_AVERTISSEMENT aucun`, pas de `TEXTE=`.

**Les transcriptions de `FIL3`**, pour le rejeu (journal, `context AI/08-etat.md`,
entrée « 2026-09-24 — FIL3 ») : sous `~/.claude/projects/*/`,
`0045d27f-a411-4e70-8344-bdf4c15cec1e/subagents/agent-a8139dad1034ad64a.jsonl` (`F1`) et
`707b23a4-8f0b-4d1b-9101-b70c64f73bb4/subagents/agent-a6a58391ed52b8c54.jsonl` (`F2`).

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `BAC1` | Poser le bac d'essai en un appel | rien |
| `BAC2` | Compter la transcription d'un sous-agent | rien |

Les deux fiches sont indépendantes : elles touchent les mêmes fichiers, donc on les joue l'une après l'autre.

---

<!-- FICHE:BAC1 -->
## BAC1 [x] — Poser le bac d'essai en un appel

**Session** : 20118231-b233-444d-82c2-f7a46302b131
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` ; pour la forme des fiches
factices et la commande, l'entrée « 2026-09-24 — FIL3 » de `context AI/08-etat.md` — et rien d'autre.

**Prompt**
Ajoute `vlp.py bac <dossier>`. Il pose, dans un dossier absent ou vide (sinon une
`GARDE:` et rien d'écrit) : un `CHANTIER.md` minimal qui pointe le fichier de fiches ;
un fichier de fiches valide — `## Le socle commun`, `## L'ordre des fiches`, deux
fiches `F1` et `F2` ; les douze fichiers `n01.txt`…`n12.txt`. `F1` fait lire les douze
fichiers par `Read`, `F2` lance douze fois `exit 3` par Bash — chacune dit « un appel
par message, d'affilée, dans cette même exécution », jamais « par tour » (`FIL3`).
Puis il imprime `BAC <dossier>` et les deux commandes `claude -p` du journal de `FIL3`,
sans les lancer. Le contenu est fixe, en constantes du script ; aucun chemin de machine.
Ajoute la puce de la docstring. Un test dans un dossier temporaire à lui.

**Critère de fin**
Le test de `scripts/test-vlp.py` passe : `valider` sur le fichier posé sort 0 ;
`extraire` rend `F1` et `F2` non vides ; 12 fichiers `n*.txt` ; « un appel par message »
compté 2 fois par `grep -o | wc -l` ; `claude -p` 2 fois dans la sortie ; un 2ᵉ appel sur
le même dossier rend une `GARDE:`. **Mutant** : ôter `## L'ordre des fiches` de la
constante fait tomber le test. `pyright scripts/vlp.py scripts/test-vlp.py` : `0 errors`.
<!-- /FICHE -->

---

<!-- FICHE:BAC2 -->
## BAC2 [x] — Compter la transcription d'un sous-agent

**Session** : ccc2f0b0-d24d-4d65-ace4-af7bdb655ba2
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` ; pour le rejeu, l'entrée
« 2026-09-24 — FIL3 » de `context AI/08-etat.md` — et rien d'autre.

**Prompt**
Ajoute `vlp.py transcription <jsonl>`, qui imprime la sortie décrite au socle. Les
tours se comptent comme `comptoir_tours`, dans l'ordre du fichier ; le tour d'un
avertissement est celui du `tool_use` que son `toolUseID` désigne, et `is_error`
vient du `tool_result` de ce même appel. Ouvre par `mesure().ouvrir`. Fichier
illisible : une `GARDE:`. Ajoute la puce de la docstring.
Teste sur une transcription factice écrite dans un dossier temporaire à lui : un tour
sur plusieurs lignes `assistant`, deux appels, un avertissement après un appel en erreur.
Puis rejoue la commande sur les deux transcriptions de `FIL3` (chemins au socle), et
écris au journal de `context AI/08-etat.md` les deux sorties, citées telles quelles.

**Critère de fin**
Le test passe ; **mutants** : compter les tours par ligne et non par `message.id`, puis
prendre `is_error` du dernier `tool_result` au lieu de celui du `toolUseID` — chacun fait
tomber le test. Rejeu : `F1` rend `TOURS=8`, 7 appels (PowerShell 2, Read 5), averti au
tour 7 après un `Read` `is_error=non`, `HOOK_ERREURS=7 pour 7 appels`, `mot=RETOUR`,
`stop_reason=end_turn` ; `F2` : 8 tours, 7 appels Bash, averti au tour 7 après un
`is_error=oui` par `PostToolUseFailure:Bash`, 7 pour 7, `RETOUR`, `end_turn`. Un écart
avec le journal : le dire, pas corriger le chiffre. `pyright` : `0 errors`.
<!-- /FICHE -->
