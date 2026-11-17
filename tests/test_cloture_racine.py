"""Dette de FIG (CWT) : à la clôture, `vlp.py couverture --depuis` juge la racine du projet clos, pas le dossier du
plugin chargé — lancé depuis un worktree, le plugin suit `main` et disait « aucun .py changé depuis <rev> », faux
(clôture de FIG, 2026-11-17 : 97 % de 72 lignes par le `vlp.py` du worktree)."""
import os

from aides import mod


def test_cloture_couverture_sur_la_racine_du_projet():
    """`cloture.md` passe `--racine .` à chaque appel de `couverture --depuis` : le projet que la clôture tient, celui
    du dossier courant."""
    with open(os.path.join(mod.etat.KIT, "cloture.md"), encoding="utf-8") as f:
        appels = [l for l in f.read().splitlines() if "couverture --depuis" in l]
    assert appels, "cloture.md : l'appel de couverture --depuis a disparu"
    assert all("--racine ." in l for l in appels), "cloture.md : couverture --depuis sans --racine .\n" + "\n".join(appels)
