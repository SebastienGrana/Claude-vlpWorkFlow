"""REF16 : aucune règle ne se perd quand on découpe ou range une doc — chaque ligne de texte d'avant (hors titres,
lignes vides et séparateurs) se retrouve, espaces de bord ôtés, dans un fichier d'après."""
import io
import os

import conserve


def ecrire(dossier, nom, texte):
    chemin = os.path.join(dossier, nom)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(texte)
    return chemin


def test_une_ligne_deplacee_est_conservee():
    perdues = conserve.perdues(["# Titre\n", "\n", "  - une règle\n", "---\n", "un récit\n"],
                               ["- une règle\n", "  un récit  \n"])
    assert perdues == []


def test_une_ligne_absente_est_perdue_avec_son_numero():
    perdues = conserve.perdues(["# Titre\n", "garde\n", "perdue\n", "```\n", "| --- | --- |\n"], ["garde\n"])
    assert perdues == [(3, "perdue")]


def test_principal_dit_le_compte_et_sort_1(tmp_path):
    avant = ecrire(str(tmp_path), "avant.md", "# T\n\nune\ndeux\n")
    apres = ecrire(str(tmp_path), "apres.md", "une\n")
    autre = ecrire(str(tmp_path), "autre.md", "rien\n")
    sortie = io.StringIO()
    code = conserve.principal([avant, "--apres", apres, autre], sortie)
    assert (code, sortie.getvalue()) == (1, "CONSERVE 2 lignes lues · 1 perdue(s)\nPERDUE %s:4 deux\n" % avant)


def test_principal_rien_de_perdu_sort_0(tmp_path):
    avant = ecrire(str(tmp_path), "avant.md", "une\n")
    sortie = io.StringIO()
    assert conserve.principal([avant, "--apres", avant], sortie) == 0
    assert sortie.getvalue() == "CONSERVE 1 lignes lues · 0 perdue(s)\n"


def test_un_fichier_absent_est_une_garde(tmp_path):
    sortie = io.StringIO()
    assert conserve.principal([str(tmp_path / "x.md"), "--apres", str(tmp_path / "y.md")], sortie) == 1
    assert sortie.getvalue().startswith("GARDE: conserve — ")
