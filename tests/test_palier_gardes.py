"""ALG3 : `cocher` et le `pre-commit` suivent le palier, la coverage se juge à la clôture et au `pre-push` (choix 5 B
de l'utilisateur, 2026-11-08). Chaque test bâtit son propre dépôt dans un dossier temporaire."""
import io
import os
import subprocess
import tempfile

import couverture
import noyau.clore
import noyau.palier
from aides import RACINE, appel, ecrire, lire, mod


def kit(d):
    """Faire de `d` un faux kit (plugin et suite) d'un commit, dans un dépôt Git ; rend `d`."""
    for chemin, texte in ((".claude-plugin/plugin.json", "{}"), ("tests/conftest.py", ""),
                          ("tests/test_regles.py", "def test_r():\n    pass\n"), ("README.md", "kit\n"),
                          ("scripts/x.py", "x = 1\n"), ("context AI/f.md", "# Z\n\n## Z1 [ ] — a\n\n## Z2 [ ] — b\n")):
        ecrire(os.path.join(d, *chemin.split("/")), texte)
    for args in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "0"]):
        subprocess.run(["git", *args], cwd=d, check=True, capture_output=True)
    return d


def toucher(d, chemin):
    """Ajouter une ligne à `chemin` dans `d`."""
    with open(os.path.join(d, *chemin.split("/")), "a", encoding="utf-8") as f:
        f.write("# changé\n")


def cocher(d, fiche):
    """`vlp.py cocher` sur le fichier de fiches du faux kit : rend (code, sortie)."""
    o = io.StringIO()
    return mod.main(["cocher", os.path.join(d, "context AI", "f.md"), fiche], o), o.getvalue()


def faux_lanceur(code, vus):
    """Un lanceur de pytest qui note sa commande dans `vus` et rend `code`, sans rien lancer."""
    def lancer(args, _racine):
        """Noter `args` et rendre `code`."""
        vus.append(args)
        return code
    return lancer


def test_palier_lancer_note_le_vert(monkeypatch):
    with tempfile.TemporaryDirectory() as t:
        d = kit(t)
        toucher(d, "README.md")
        vus = []
        monkeypatch.setattr(noyau.palier, "lancer", faux_lanceur(0, vus))
        code, s = appel(["palier", "--racine", d, "--lancer"])
        assert code == 0, "palier --lancer : vert\n" + s
        assert "PALIER VERT doc" in s, "palier --lancer : il dit le vert\n" + s
        assert (vus or [[None]])[0][-1] == "tests/test_regles.py", "palier --lancer : la commande du palier\n" + str(vus)
        assert noyau.palier.palier_vert_note(d) == (mod.empreinte_kit(d), "doc"), "palier --lancer : le vert noté"


def test_palier_lancer_rouge_ne_note_rien(monkeypatch):
    with tempfile.TemporaryDirectory() as t:
        d = kit(t)
        toucher(d, "README.md")
        monkeypatch.setattr(noyau.palier, "lancer", faux_lanceur(1, []))
        code, s = appel(["palier", "--racine", d, "--lancer"])
        assert code == 1, "palier --lancer : rouge, sort 1\n" + s
        assert "PALIER ROUGE doc" in s, "palier --lancer : il dit le rouge\n" + s
        assert noyau.palier.palier_vert_note(d) is None, "palier --lancer : rouge, rien noté"


def test_cocher_accepte_un_palier_vert_assez_haut(monkeypatch):
    with tempfile.TemporaryDirectory() as t:
        d = kit(t)
        toucher(d, "README.md")
        sans = cocher(d, "Z1")
        assert sans[0] == 1, "cocher : sans palier vert, refus\n" + sans[1]
        assert "palier --lancer" in sans[1], "cocher : la garde donne la commande\n" + sans[1]
        monkeypatch.setattr(noyau.palier, "lancer", faux_lanceur(0, []))
        appel(["palier", "--racine", d, "--lancer"])
        apres = cocher(d, "Z1")
        assert apres[0] == 0, "cocher : un palier vert sur ce code suffit\n" + apres[1]


def test_cocher_refuse_un_palier_trop_bas(monkeypatch):
    with tempfile.TemporaryDirectory() as t:
        d = kit(t)
        toucher(d, "README.md")
        monkeypatch.setattr(noyau.palier, "lancer", faux_lanceur(0, []))
        appel(["palier", "--racine", d, "--lancer"])
        toucher(d, "scripts/x.py")
        noyau.palier.noter_palier_vert(d, mod.empreinte_kit(d), "doc")   # le bon code, mais un palier trop bas
        refus = cocher(d, "Z1")
        assert refus[0] == 1, "cocher : un script changé veut le palier script, pas doc\n" + refus[1]
        assert "script" in refus[1], "cocher : la garde nomme le palier voulu\n" + refus[1]


def test_pre_commit_ne_juge_plus_la_couverture():
    texte = lire(os.path.join(RACINE, ".githooks", "pre-commit"))
    assert "vlp.py couverture" not in texte, "pre-commit : la coverage se juge à la clôture, plus à chaque commit"
    assert "pyright" in texte, "pre-commit : pyright reste"


def test_pre_push_exige_le_rapport():
    chemin = os.path.join(RACINE, ".githooks", "pre-push")
    assert os.path.isfile(chemin), "pre-push : le hook existe"
    assert "couverture --a-jour" in lire(chemin), "pre-push : il demande si le rapport est à jour"


def test_couverture_a_jour():
    with tempfile.TemporaryDirectory() as t:
        d = kit(t)
        s = io.StringIO()
        assert couverture.principal(["--racine", d, "--a-jour"], s) == 1, "couverture --a-jour : sans rapport\n" + s.getvalue()
        assert s.getvalue().startswith("GARDE:"), "couverture --a-jour : une GARDE\n" + s.getvalue()
        _, rapport, note = couverture.chemins(d)
        ecrire(rapport, "<coverage/>\n")
        ecrire(note, mod.empreinte_kit(d) + "\n")
        s = io.StringIO()
        assert couverture.principal(["--racine", d, "--a-jour"], s) == 0, "couverture --a-jour : à jour\n" + s.getvalue()


def test_couverture_depuis_sans_rapport_garde():
    with tempfile.TemporaryDirectory() as t:
        d = kit(t)
        toucher(d, "scripts/x.py")
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-am", "1"], cwd=d,
                       check=True, capture_output=True)
        s = io.StringIO()
        assert couverture.principal(["--racine", d, "--depuis", "HEAD~1"], s) == 1, "couverture --depuis\n" + s.getvalue()
        assert "pas de rapport" in s.getvalue(), "couverture --depuis : sans rapport, une GARDE\n" + s.getvalue()


def test_clore_garde_sans_couverture_dans_le_kit():
    with tempfile.TemporaryDirectory() as t:
        d = kit(t)
        assert "couverture" in (noyau.clore.garde_couverture_clore(d) or ""), "clore : le kit sans rapport à jour, refus"
        _, rapport, note = couverture.chemins(d)
        ecrire(rapport, "<coverage/>\n")
        ecrire(note, mod.empreinte_kit(d) + "\n")
        assert noyau.clore.garde_couverture_clore(d) is None, "clore : rapport à jour, rien à redire"
        os.remove(os.path.join(d, ".claude-plugin", "plugin.json"))
        os.remove(note)
        assert noyau.clore.garde_couverture_clore(d) is None, "clore : un projet équipé n'a pas cette garde"
