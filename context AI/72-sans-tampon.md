> **QUAND LIRE** : on joue une fiche `SON*` de ce chantier, ou on se demande où
> il en est. `/vlp:tache SON<n>` n'en lit que le socle commun et sa fiche — jamais
> ce fichier en entier.

# Chantier SON — Rejouer un hook à la main sans le tampon

**À quoi il sert.** `une_fois` (chantier `PYT`) fait taire la même entrée rejouée en moins
de 60 s : un relecteur de `RLG1` a dû ajouter un `nonce` pour comparer avant et après.

**Estimé.** 0,5 fiches · ≈2,02 $ — ≈4,04 $/fiche sur 59 clos (le 2026-09-26).

**Fait.** Rien. Ouvert le 2026-09-26, la nuit, cadré seul en 1 fiche (à valider), `SON1` à jouer.

**Session** : 81f28c74-89aa-4815-b804-db93de007ebc

## Le socle commun

Cadré seul, la nuit du 2026-09-26, l'utilisateur dormant. Choix pris seul, à valider : une
**variable d'environnement** plutôt qu'une option — un hook est lancé par `hooks/hooks.json`,
qu'on ne veut pas toucher, et la même commande rejouée à la main n'a qu'à la poser.

`premier_lancement` et `une_fois` : `scripts/vlp.py`, vers la ligne 320 ; leur test :
`test_premier_lancement` de `scripts/test-vlp.py` (PYT1, PYT2).

## L'ordre des fiches

- `SON1` — `VLP_SANS_TAMPON`. Aucune dépendance.

---

<!-- FICHE:SON1 -->
## SON1 [ ] — `VLP_SANS_TAMPON` saute le tampon

**Dépend de** : rien.
**Fichiers** : `scripts/vlp.py` (docstring du module, `premier_lancement`) ;
`scripts/test-vlp.py` (`test_premier_lancement`) — et rien d'autre.

**Prompt**
`VLP_SANS_TAMPON` non vide dans l'environnement : `premier_lancement` rend toujours vrai,
comme `TAMPON_HOOKS = None` en test. Une phrase à la docstring du module, sous celle de `PYT`.

**Critère de fin**
Test : la même entrée `gardien` rejouée deux fois avec la variable refuse deux fois ; sans
elle, le tampon reprend (muet). **Mutant** : retirer la lecture de la variable fait tomber
le test. `pyright scripts/vlp.py scripts/test-vlp.py` : `0 errors`.
<!-- /FICHE -->
