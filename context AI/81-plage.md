> **QUAND LIRE** : on joue une fiche `PLG*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache PLG<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier PLG — La plage de l'en-tête et la dernière fiche

**À quoi il sert.** Une plage de fiches (`REV1–REV8`) prend la première et la dernière fiche
du fichier : `REV`, rangé REV1…REV3, REV5…REV8, REV4, s'affiche `REV1–REV4`. PLG la borne par
numéro, le plus bas et le plus haut, partout où `vlp.py` écrit une plage.

**Estimé.** 0,5 fiches · ≈2,12 $ — ≈4,24 $/fiche sur 68 clos (le 2026-09-27).

**Fait.** Rien. Ouvert le 2026-09-27, cadré en 1 fiche, `PLG1` à jouer.

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356

## Le socle commun

Tranché la nuit du 2026-09-27, l'utilisateur dormant (TODO n° 57, 🟡) : **le plus haut
numéro**. Raison : la plage dit combien de fiches existent, et `ouvrir --estime-fiches`
compte les fiches d'un clos sur sa plage — l'ordre du fichier en fait perdre.

| Symbole | `scripts/vlp.py` | Ce qu'il écrit |
|---|---|---|
| `plage(ids)` | `:2705` | `X1–Xn` : en-tête de page (`:2362`), ligne « en cours » de la feuille (`:2798`), ligne de `clore` (`:3831`) |
| `"%s..%s" % (ids[0], ids[-1])` | `:3687`, `:3694`, `:3722`, `:3936` | `X1..Xn` : `**Fait.**`, index et `CHANTIER.md` (`clore`, `ouvrir`) |

- Une règle, un endroit : une fonction `bornes(ids)` rend (plus bas, plus haut) par la valeur
  entière des chiffres de fin ; `plage` et les quatre `..` l'appellent.
- `PLAGE_CLOS` et `clos_du_projet` lisent le préfixe seul : non touchés.
- On ne réécrit pas les plages déjà écrites (pages, index) : elles se refont à leur prochaine
  écriture ; `comparer` les range en `PLAGE:` (dette HAB, `10dd168`).

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `PLG1` | Borner la plage par numéro | rien |

Une seule fiche.

---

<!-- FICHE:PLG1 -->
## PLG1 [x] — Borner la plage par numéro

**Session** : 5a12485e-8f92-4566-8eac-a08b630de356
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Écris `bornes(ids)` près de `plage` : la fiche au plus petit et au plus grand numéro (chiffres
de fin, en entier : `REV10` après `REV9`). `plage` l'appelle ; les quatre `"%s..%s" % (ids[0],
ids[-1])` de `clore` et `ouvrir` aussi. Une seule fiche : `plage` rend son id seul, comme avant.

**Critère de fin**
Test : `mod.plage(["REV1","REV2","REV3","REV5","REV8","REV4"])` vaut `REV1–REV8`,
`mod.plage(["X9","X10"])` vaut `X9–X10`, `mod.plage(["U1"])` vaut `U1` ; et un `ouvrir` sur un
fichier rangé Q2, Q1 écrit `Q1..Q2`. Mutant : `bornes` rend `ids[0], ids[-1]` → le premier
test tombe. `test-vlp.py` finit par `OK` ; pyright 0 erreur sur `scripts/`.
<!-- /FICHE -->
