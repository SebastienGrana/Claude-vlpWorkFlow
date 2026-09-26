> **QUAND LIRE** : on joue une fiche `TOU*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache TOU<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier TOU — Le filet n'avertit qu'une fois par tour

**À quoi il sert.** En `RAT1` (2026-09-26), le filet a averti 13 fois dans un même tour : une fois
par appel groupé. Le chantier le fait parler une fois par tour, mesures avant/après à l'appui.

**Estimé.** 0,5 fiches · ≈2,01 $ — ≈4,03 $/fiche sur 60 clos (le 2026-09-26).

**Fait.** Rien. Ouvert le 2026-09-26, cadré en 3 fiches, `TOU1` à jouer. TODO n° 71.

**Session** : d0070921-f1b2-4a16-b0ab-6929b6979afa

## Le socle commun

| Symbole | Où | Ce qu'il fait |
|---|---|---|
| `cmd_filet` | `scripts/vlp.py:1266` | lit le JSON du hook, compte les tours du sous-agent, avertit si `0 < restants <= SEUIL_FILET` |
| `comptoir_tours` | `scripts/vlp.py`, juste après | tours = `message.id` distincts du transcript `…/subagents/agent-<agent_id>.jsonl` |
| `premier_lancement` | `scripts/vlp.py:320` | tampon anti-jumeau (`python3` + `py`), clé = sha1 du nom + entrée exacte : ne fusionne **pas** deux appels différents |
| `TAMPON_HOOKS` | `scripts/vlp.py:285` ; `None` dans `scripts/test-vlp.py:34` | dossier des tampons ; un test qui en a besoin pose un `tempfile.mkdtemp()` neuf (modèle : `test-vlp.py:2725`) |
| `cmd_transcription` | `scripts/vlp.py:3491` | compte un transcript : `TOURS=`, `APPELS=`, `AVERTISSEMENTS=`, `PREMIER_AVERTISSEMENT tour=…` |
| `evals/filet-rate/` | `case.yaml`, `fixture.sh`, `prompt.md` | douze `Read` ratés ; rejoué en `RAT1` à plafond 5 (commande dans `context AI/08-etat.md`, journal `RAT1`) |
| `evals/filet/rejouer.sh` | — | copie de kit à plafond bas (`kit-essai`), eval, `transcription` de chaque sous-agent ; `--tag filet` seulement |

**Décidé au cadrage** (2026-09-26, avec l'utilisateur) :

- Un tour = un compte de `comptoir_tours` : les appels d'une même salve voient le même compte —
  à confirmer par `TOU1` avant d'écrire `TOU2`.
- Tous les événements du filet (`PostToolUse` et `PostToolUseFailure`), pas le seul `Read`.
- `VLP_SANS_TAMPON` saute aussi le nouveau tampon : un rejeu à la main avertit toujours (`SON`).
- Preuve : test + mutant, **et** l'eval `filet-rate` rejouée à plafond 5 avant et après (≈ 0,15 $ chacune).

**Hors chantier** : le texte de l'avertissement, `SEUIL_FILET`, le gardien, le hook `hook`.

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `TOU1` | Mesurer avant : les avertissements, tour par tour | rien |
| `TOU2` | Ne plus avertir qu'une fois par tour | `TOU1` |
| `TOU3` | Mesurer après, à plafond 5 | `TOU2` |

Rien n'est parallélisable : chaque fiche lit le résultat de la précédente.

---

<!-- FICHE:TOU1 -->
## TOU1 [x] — Mesurer avant : les avertissements, tour par tour

**Session** : 288997c5-3d54-4aaf-82c5-71c78fb6b9da
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (`cmd_transcription`), `scripts/test-vlp.py`, `evals/filet/rejouer.sh` — et rien d'autre.

**Prompt**
1. `cmd_transcription` écrit, après `AVERTISSEMENTS=`, une ligne `AVERTIS_PAR_TOUR=` : pour chaque
   tour qui en a, `tour:nombre`, séparés par des virgules (`aucun` sinon). Le tour d'un avertissement
   est celui de l'appel qu'il suit (`toolUseID` → `appels`), comme pour `PREMIER_AVERTISSEMENT`.
   Mets la ligne dans la docstring. Test dans `test-vlp.py`, sur un transcript fabriqué dans un
   dossier temporaire : 3 avertissements au tour 2 et 1 au tour 3 → `AVERTIS_PAR_TOUR=2:3,3:1`.
2. `rejouer.sh` prend un 2ᵉ argument, le tag (défaut `filet`) : il sert à `--tag` et au nom du `--json`.
3. Rejoue sous WSL2 : `bash evals/filet/rejouer.sh 5 filet-rate`. Note dans le journal de
   `context AI/08-etat.md` les lignes `TOURS=`, `AVERTISSEMENTS=`, `AVERTIS_PAR_TOUR=` et le coût.

**Critère de fin**
Le test passe ; le mutant « compter tous les avertissements au tour 1 » le fait tomber. L'eval
rejouée donne ses comptes bruts : si tous les avertissements groupés tombent sur un même tour, la
clé de `TOU2` est confirmée ; sinon, rends `RETOUR` et dis ce que tu as vu.
<!-- /FICHE -->

---

<!-- FICHE:TOU2 -->
## TOU2 [ ] — Ne plus avertir qu'une fois par tour

**Dépend de** : `TOU1` (clé confirmée).
**Fichiers** : `scripts/vlp.py` (`cmd_filet`), `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Avant d'écrire l'avertissement, `cmd_filet` crée en exclusif (`O_CREAT | O_EXCL`) un tampon
`vlp-filet-<agent_id>-<tours>` dans `TAMPON_HOOKS` : s'il existe déjà, le filet se tait. Même
repli que `premier_lancement` : `TAMPON_HOOKS` à `None` ou `VLP_SANS_TAMPON` non vide → toujours
avertir ; une autre `OSError` → avertir. Les tampons de plus de 60 s sont retirés comme les autres.
Dis-le en une ligne dans la docstring de `cmd_filet`.

Tests dans `test-vlp.py`, avec un `TAMPON_HOOKS` neuf (`tempfile.mkdtemp()`, rétabli après) et un
transcript à 3 tours restants : deux appels d'entrées différentes → une seule sortie ; un tour de
plus au transcript → le filet avertit de nouveau ; `VLP_SANS_TAMPON=1` → deux sorties.

**Critère de fin**
`py scripts/test-vlp.py` : 0 échec, compte brut donné. Le mutant « ne pas lire le tampon » fait
tomber le test « une seule sortie » ; le mutant « clé sans le tour » fait tomber « avertit de
nouveau ». `pyright scripts/vlp.py scripts/test-vlp.py` : 0 erreur.
<!-- /FICHE -->

---

<!-- FICHE:TOU3 -->
## TOU3 [ ] — Mesurer après, à plafond 5

**Dépend de** : `TOU2`.
**Fichiers** : `evals/filet/rejouer.sh` (lancé, pas modifié), `context AI/08-etat.md` — et rien d'autre.

**Prompt**
Rejoue sous WSL2 `bash evals/filet/rejouer.sh 5 filet-rate`, puis le témoin
`bash evals/filet/rejouer.sh 80 filet-rate`. Note dans le journal de `context AI/08-etat.md`,
à côté des chiffres de `TOU1` : `TOURS=`, `AVERTISSEMENTS=`, `AVERTIS_PAR_TOUR=` et le coût de chacun.

**Critère de fin**
Plafond 5 : chaque tour de `AVERTIS_PAR_TOUR=` vaut au plus 1, et au moins un avertissement existe
(le filet parle encore). Plafond 80 : `AVERTISSEMENTS=0`. Comptes bruts de `TOU1` et `TOU3` côte à côte.
<!-- /FICHE -->
