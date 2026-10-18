"""Les suites voisines, lancées par pytest (REF59, choix Q1 : A) : `test-boucle.py` (la boucle de nuit et son faux
`claude`), sa partie qui attend les variables de la nuit absentes, et `test-mesure-tokens.py` — jusque-là lancées par
l'ancienne suite maison. Puis l'option `--seul` de `conftest.py` (VIT10, choix Q2 : A)."""
import os
import subprocess
import sys
import tempfile
import time

from aides import RACINE, SCRIPTS, ecrire, mod, porte_motif


def suite_voisine(chemin):
    """Jouer jusqu'au bout la suite de tests `chemin` ; rendre (verte, sa sortie) — verte : elle sort 0 et dit `OK`
    en dernière ligne (VIT24)."""
    r = subprocess.run([sys.executable, chemin], capture_output=True, encoding="utf-8", errors="replace",
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    return r.returncode == 0 and r.stdout.strip().endswith("OK"), r.stdout + r.stderr


def test_boucle():
    """NUI2 : test-boucle.py joue boucle.py et faux-claude.py ; sa sortie passe en entier : son `ÉCART:` y remonte."""
    verte, texte = suite_voisine(os.path.join(SCRIPTS, "test-boucle.py"))
    assert verte, "boucle : test-boucle.py (boucle.py et son faux claude) sort OK" + "\n" + texte


def test_boucle_nuit():
    """ENV1 : `test-boucle.py` retire les variables de la nuit en tête ; ce test les lui pose, sur sa seule partie qui
    les attend absentes, pour que son propre retrait se voie."""
    debut = time.perf_counter()
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "test-boucle.py"), "--parties", "sans_nuit"],
                       capture_output=True, encoding="utf-8", errors="replace",
                       env=dict(os.environ, PYTHONIOENCODING="utf-8", VLP_NUIT="1", VLP_CANAL="B",
                                VLP_CARNET=os.path.join(tempfile.gettempdir(), "carnet-env1.jsonl")))
    texte = r.stdout + r.stderr   # une partie seule ne finit pas sur `OK` : sortie 0 et aucun `ÉCART`, comme avant
    assert r.returncode == 0 and "ÉCART" not in r.stdout, (
        "ENV1 : test-boucle.py --parties sans_nuit, sous les trois variables de la nuit, sort 0 sans ÉCART "
        "— mutant : le retrait en tête de test-boucle.py neutralisé") + "\n" + str((time.perf_counter() - debut, texte))


def test_voisine_rouge(tmp_path):
    """VIT24 : une voisine qui sort 1, même en disant `OK`, ou qui sort 0 sans le dire, n'est pas verte."""
    rate, muette = os.path.join(tmp_path, "test-rate.py"), os.path.join(tmp_path, "test-muette.py")
    ecrire(rate, 'print("ÉCART: semé")\nprint("OK")\nraise SystemExit(1)\n')
    ecrire(muette, 'print("FIN: 1 écart(s)")\n')
    rouges = [suite_voisine(rate), suite_voisine(muette)]
    assert [r[0] for r in rouges] == [False, False] and "ÉCART: semé" in rouges[0][1], (
        "VIT24 : une voisine qui sort 1, ou qui sort 0 sans OK, n'est pas verte — mutant : le code de sortie "
        "ignoré") + "\n" + str(rouges)


def test_mesure_tokens():
    verte, texte = suite_voisine(os.path.join(SCRIPTS, "test-mesure-tokens.py"))
    assert verte, "mesure-tokens : test-mesure-tokens.py sort OK" + "\n" + texte


def _temoin_nom():
    """Un témoin, retenu par son nom."""


def _temoin_aide():
    """Un témoin qui appelle une aide du module."""
    _aide_du_temoin()


def _aide_du_temoin():
    """Le libellé « une aide Vit10-Témoin » vit ici."""


def test_porte_motif():
    """VIT10 : le nom, le texte, ou celui d'une aide nommée, sans casse ; ni l'un ni l'autre, écarté."""
    assert porte_motif(_temoin_nom, "TEMOIN_NOM"), "seul : le nom porte le motif, sans casse — mutant : casse comptée"
    assert porte_motif(_temoin_nom, "retenu PAR son nom"), "seul : le texte porte le motif, sans casse"
    assert not porte_motif(_temoin_nom, "autre-motif"), "seul : ni le nom ni le texte, écarté"
    assert porte_motif(_temoin_aide, "vit10-témoin") and not porte_motif(_temoin_nom, "vit10-témoin"), \
        "seul : le texte d'une aide du module que le test appelle porte le motif — mutant : aides ignorées"
    assert porte_motif(_temoin_nom, "cas-b", "test_x[cas-b]"), "seul : l'id d'un test paramétré compte comme son nom"


def lancer_pytest(*args):
    """Lancer pytest sur ce kit avec `args` ; rendre (code de sortie, sortie)."""
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", *args], cwd=RACINE, capture_output=True,
                       encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    return r.returncode, r.stdout + r.stderr


def test_seul_ne_joue_que_ses_tests():
    """`--seul` garde les seuls tests qui portent le motif, et la session finit sur `OK`."""
    code, s = lancer_pytest("tests/test_commun.py", "--seul", "LEC :")
    assert code == 0 and "1 passed" in s and "deselected" in s and s.strip().endswith("OK"), \
        "seul : pytest ne joue que le test qui porte le motif, puis OK" + "\n" + s


def test_seul_sans_test_sort_1():
    """Un motif que rien ne porte : `GARDE:` et sortie 1 — un motif mal tapé ne passe pas pour une suite verte."""
    code, s = lancer_pytest("tests/test_commun.py", "--seul", "motif-que-rien-ne-porte")
    assert code == 1 and "GARDE: aucun groupe ne porte « motif-que-rien-ne-porte »" in s, \
        "seul : aucun test retenu → GARDE et sortie 1" + "\n" + s


def test_commande_suite():
    """La commande de la suite du kit : pytest par `uv`, dans l'environnement du projet nommé, sur 4 processus ou en
    série — ce que `rapide` et `mutant` lancent (REF59)."""
    entiere, serie = mod.commande_suite("K"), mod.commande_suite("K", parallele=False)
    assert entiere[1:] == ["run", "--frozen", "--project", "K", "pytest", "-q", "-n", "4"], entiere
    assert serie[1:] == ["run", "--frozen", "--project", "K", "pytest", "-q"] and serie[0] == entiere[0], serie


def test_sans_parallele():
    """`sans_parallele` ôte `-n <n>` et lui seul : `--seul` filtre à la collecte, que pytest-xdist fait ailleurs."""
    assert mod.sans_parallele(["uv", "run", "pytest", "-q", "-n", "4", "--seul", "x"]) == [
        "uv", "run", "pytest", "-q", "--seul", "x"]
    assert mod.sans_parallele(["py", "suite.py", "--seul", "-n"]) == ["py", "suite.py", "--seul"]   # -n sans valeur, en fin
    assert mod.sans_parallele(["py", "suite.py"]) == ["py", "suite.py"]