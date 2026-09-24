> **QUAND LIRE** : on joue une fiche `CAS*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache CAS<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier CAS — Le chef relit la case avant de commiter

**À quoi il sert.** Dans `SAG3`, le sous-agent a rendu `FAITE` sans cocher, et le chef de
`/vlp:enchainer`, qui commite sur `FAITE` sans relire la case, a commité case vide. Après
`FAITE`, le chef relira la case par script, et lira `RETOUR` si elle est vide.

**Fait.** `CAS1` (2026-09-24). Cadrage revu après elle : `CAS2` ajoutée, à jouer.

## Le socle commun

| Nom | Où | Ce qu'il fait ou rend |
|---|---|---|
| `cmd_cocher` | `scripts/vlp.py:447` | `## <fiche> [ ]` → `[x]`, plus la ligne `**Session**` ; introuvable : `GARDE: fiche introuvable : <fiche>`, sort 1 ; déjà cochée : `GARDE: <fiche> déjà cochée — rien écrit`, sort 1 |
| l'entrée `cocher` de la docstring | `scripts/vlp.py:1`, section « Sous-commandes » | une phrase par option |
| les options de `cocher` | `scripts/vlp.py`, `main`, variable `co2` | `fichier`, `fiche`, `--resolu`, `--date` |
| les tests de `cocher` | `scripts/test-vlp.py`, section « chantier U » | `appel([...])` rend `(code, sortie)` ; `verifier(nom, condition, sortie)` |
| la puce `FAITE` du chef | `skills/enchainer/SKILL.md`, étape 3, puce 2 | commite sur `FAITE`, sans relire la case |
| le contrat de retour | `enchainement.md`, ligne `FAITE` | « case cochée » — rien ne dit ce que le chef fait d'une case vide |

**Décidé seul, la nuit du 2026-09-24** (l'utilisateur dort ; à revoir au réveil).
- Une option `--verifier` de `cocher`, pas une sous-commande neuve : l'idiome `--verifier`
  (n'écrit rien, sort 1 sur écart) existe déjà pour `page` et `feuille`, et la recherche du
  titre vit déjà dans `cmd_cocher`.
- Case vide après `FAITE` : le chef lit un `RETOUR` (étape 3 bis), comme le dit la TODO.

**Ce qu'on ne fait pas.** Provoquer un `FAITE` sans cocher dans un bac `claude -p` : rien ne
le déclenche à coup sûr ; les tests et l'usage du chef suffisent. **Revu après `CAS1`** :
`agents/fiche.md` reçoit une phrase — son sous-agent a commité lui-même (journal du 2026-09-24).

## L'ordre des fiches

| Fiche | Titre | Dépend de |
|---|---|---|
| `CAS1` | Relire la case avant de commiter | rien |
| `CAS2` | Reprendre la puce `FAITE`, et dire au sous-agent qu'il ne commite pas | `CAS1` |

`CAS2` reprend ce que `CAS1` a livré : rien à paralléliser.

---

<!-- FICHE:CAS1 -->
## CAS1 [x] — Relire la case avant de commiter

**Session** : 1ba64929-8274-42d4-93bb-a2d22fbdd600
**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (docstring, `cmd_cocher`, `main`), `scripts/test-vlp.py`
(tests de `cocher`, section « chantier U »), `skills/enchainer/SKILL.md` (étape 3),
`enchainement.md` — et rien d'autre.

**Prompt**
1. Dans `cmd_cocher`, ajoute l'option `--verifier`, qui n'écrit rien. Fiche introuvable : la
   `GARDE:` existante, sort 1. Sinon : `CASE <fiche> [x]`, sort 0, si le titre est coché ;
   `CASE <fiche> [ ]`, sort 1, s'il ne l'est pas. Déclare l'option sur `co2` dans `main`, et
   complète l'entrée `cocher` de la docstring d'une phrase.
2. Dans `scripts/test-vlp.py`, section « chantier U », juste après le test « cocher : fiche
   introuvable » (U1 y est cochée, U2 pas encore) : trois `verifier` — U1 rend
   `(0, "CASE U1 [x]\n")` ; U2 rend `(1, "CASE U2 [ ]\n")` et le fichier reste identique ;
   U9 rend `(1, "GARDE: fiche introuvable : U9\n")`.
3. Dans `skills/enchainer/SKILL.md`, étape 3, puce `FAITE` qui commite : avant le commit, le
   chef relit la case — `<python> "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py" cocher "<fichier de
   fiches courant>" <fiche> --verifier` ; `[ ]` : c'est un `RETOUR` (le sous-agent n'a pas
   coché), étape 3 bis ; `[x]` : commite. Deux lignes ajoutées au plus.
4. Dans `enchainement.md`, ligne `FAITE` : le chef lit une case vide comme un `RETOUR`.

**Critère de fin**
`py scripts/test-vlp.py` rend `OK` ; le compte des `verifier(` de `scripts/test-vlp.py`
(`py -c` qui compte la chaîne) passe de 200 à 203 ; avant ta coche,
`py scripts/vlp.py cocher "context AI/43-case-relue.md" CAS1 --verifier` rend
`CASE CAS1 [ ]` et sort 1 ; `git diff --stat` ne nomme que les quatre fichiers, plus ce
fichier de fiches.
<!-- /FICHE -->

---

<!-- FICHE:CAS2 -->
## CAS2 [ ] — Reprendre la puce `FAITE`, et dire au sous-agent qu'il ne commite pas

**Dépend de** : `CAS1`.
**Fichiers** : `skills/enchainer/SKILL.md` (étape 3, puce `FAITE` qui commite),
`agents/fiche.md`, `scripts/vlp.py` (docstring, entrée `cocher`) — et rien d'autre.

**Prompt**
Relu par le chef après `CAS1` (journal du 2026-09-24) : la puce `FAITE` tient sur une ligne de
414 caractères, et le sous-agent de `CAS1` a commité lui-même.
1. Dans `skills/enchainer/SKILL.md`, récris la puce `FAITE` qui commite, coupée comme ses
   voisines (retrait de cinq espaces sous le tiret). Garde le sens de `CAS1` : relire la case
   par `cocher --verifier` ; `[ ]` : `RETOUR`, étape 3 bis ; `[x]` : commit. Remets ce qu'elle a
   perdu : `(methode-chantier.md)` après « sans demander », la phrase « le sous-agent ne commite
   jamais », et `(vlp.py carte)` après « relance la carte ».
2. Dans `agents/fiche.md`, au paragraphe qui dit « Aucun artefact, aucune question, aucun
   sous-agent » : aucun commit non plus — le chef commite après ton statut, même si un
   `CLAUDE.md` demande un commit par tâche. Une phrase courte.
3. Dans la docstring de `scripts/vlp.py`, entrée `cocher` : `--verifier` n'écrit rien, et rend
   `CASE <fiche> [x]` (sort 0) ou `CASE <fiche> [ ]` (sort 1).
Tu ne commites pas : le chef le fera.

**Critère de fin**
`py scripts/test-vlp.py` rend `OK` ; la plus longue ligne de `skills/enchainer/SKILL.md`
(`py -c` qui la mesure) revient à 222 caractères au plus, contre 414 ; la puce porte
`--verifier`, `methode-chantier.md`, « ne commite jamais » et `vlp.py carte` ;
`agents/fiche.md` porte la phrase ; `git diff --stat` ne nomme que les trois fichiers, plus
ce fichier de fiches.
<!-- /FICHE -->
