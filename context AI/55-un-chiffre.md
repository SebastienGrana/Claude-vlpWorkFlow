> **QUAND LIRE** : on joue une fiche `UNI*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache UNI<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier UNI — Un seul chiffre par clôture

**À quoi il sert.** `cloture.md` fait mesurer le total par `cout` à l'étape 1, puis
`clore --tokens N` l'écrit sur la feuille de route pendant que la page, régénérée quelques
tours plus tard, en affiche un autre (TODO n° 52). Ce soir encore : `GLO` 13 784 706 au
bilan, 15 182 315 sur sa page ; `GAR` 7 588 840 et 7 864 973. Un nombre, un seul endroit.

**Fait.** Rien. Ouvert le 2026-09-25, cadré en 2 fiches, `UNI1` à jouer. Cadré seul :
l'utilisateur dormait ; les 🟡 tranchés ici sont à valider au réveil.

**Session** : ca431cf8-167e-4c10-8bce-210c5f48a675

## Le socle commun

| Fait vérifié | Où |
|---|---|
| `regenerer(html, fichier, notes, journal, date, gardes)` rend `(html, fiches_, etat, total, hors)` ; `total` vaut `(tokens, tours, usd)` ou `None` | `scripts/vlp.py`, `def regenerer` |
| `cmd_clore` appelle `regenerer(...)[0]` (étape « 1 ter », `ZONE:bilan`) et ne garde que le HTML ; la ligne de la feuille prend `a.tokens` (« non mesuré » sans lui) | `scripts/vlp.py`, `def cmd_clore` |
| la ligne `CLOS … · total <n>` de `clore` donne le **cumul** de la feuille de route, pas le chantier | `scripts/vlp.py`, fin de `cmd_clore` |
| `arrondi`, `milliers` : formats d'un compte | `scripts/vlp.py` |
| la clôture, pas à pas : étape 1 (`cout`, bilan), étape 2 (`clore --tokens`) | `cloture.md`, « 1. Le fichier d'état » et « 2. Tout ce qui se déduit » |
| tests : `py scripts/test-vlp.py` (bloc `clore`) ; pyright sur les fichiers touchés ; une fiche de code nomme son mutant | `methode-chantier.md`, « Anatomie d'une fiche » |

Décidé au cadrage, seul : `--tokens` **reste**, comme contrôle — donné et différent du
total mesuré, `clore` écrit une ligne `ÉCART` et garde le mesuré. `cloture.md` cesse de le
passer. Pourquoi : un projet cloné en groupe peut l'avoir dans un script, et le retirer
casserait son appel sans rien gagner.

**Dehors.** Recompter les chantiers déjà clos (`RCP`) ; la rétro coût de fin de clôture
garde `cout` pour nommer la fiche la plus chère (le coût d'une fiche ne bouge plus après son
commit).

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `UNI1` | Faire mesurer le total par clore | rien |
| `UNI2` | Citer le chiffre de clore au bilan | `UNI1` |

`UNI2` lit la ligne que `UNI1` ajoute.

---

<!-- FICHE:UNI1 -->
## UNI1 [ ] — Faire mesurer le total par clore

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py`, `scripts/test-vlp.py` — et rien d'autre.

**Prompt**
Dans `cmd_clore`, garde le `total` que rend `regenerer` à l'étape « 1 ter ». La ligne du
chantier sur la feuille de route prend ce total mesuré (`total[0]`) ; sans page ou sans
mesure, elle retombe sur `--tokens`, puis sur « non mesuré ». Si `--tokens N` est donné et
diffère du mesuré, écris `ÉCART tokens <N> donné · <mesuré> mesuré — le mesuré est écrit`.
Ajoute à la ligne `CLOS` le champ `chantier <n>` (le compte écrit, en `milliers`, ou « non
mesuré »), avant `total`, et renomme ce dernier `cumul`. Mets à jour la docstring du module
(ligne `clore`). Adapte les tests existants du bloc `clore` qui lisent `total`, et ajoute :
un `--tokens` faux donne `ÉCART` et la feuille porte le mesuré.

**Critère de fin**
`py scripts/test-vlp.py` rend `OK`. Mutant : écrire `a.tokens` au lieu du mesuré sur la
feuille fait tomber le nouveau test. pyright : 0 erreur sur les deux fichiers.
<!-- /FICHE -->

---

<!-- FICHE:UNI2 -->
## UNI2 [ ] — Citer le chiffre de clore au bilan

**Dépend de** : `UNI1`.
**Fichiers** : `cloture.md` — et rien d'autre.

**Prompt**
Réordonne les deux premiers temps de `cloture.md` sans les allonger. D'abord, au fichier
d'état : retirer ou reformuler la ligne de la TODO (la feuille que `clore` écrit la relit).
Puis `clore`, **sans** `--tokens` : sa ligne `CLOS … · chantier <n>` donne le total. Puis
la ligne de bilan datée, qui cite ce `<n>` tel quel — plus de `cout` avant. Garde la phrase
sur la piste échouée. La rétro coût de fin garde `cout` pour nommer la fiche la plus chère.
Ne recopie aucun seuil ni aucune règle d'ailleurs.

**Critère de fin**
`Read` de `cloture.md` : `clore` y est appelé sans `--tokens` ; la ligne de bilan y vient
après `clore` et cite `chantier <n>` ; `vlp.py lignes cloture.md` rend au plus 125 lignes
(120 avant).
<!-- /FICHE -->
