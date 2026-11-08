"""ALG2 : `vlp.py palier` — les chemins changés choisissent les tests, par la table `REGLES_PALIER` de
`scripts/noyau/palier.py`, jamais au jugé (choix 5 A et C de l'utilisateur, 2026-11-08). Chaque test bâtit son
propre dépôt dans un dossier temporaire."""
import os
import subprocess
import tempfile

from aides import appel, ecrire

FICHIERS = {
    "README.md": "le kit\n",
    "cloture.md": "la clôture\n",
    "scripts/noyau/page.py": "def page():\n    return 1\n",
    "scripts/noyau/commun.py": "def lire():\n    return 1\n",
    "scripts/boucle.py": "def boucle():\n    return 1\n",
    "tests/conftest.py": "",
    "tests/test_regles.py": "def test_r():\n    pass\n",
    "tests/test_page.py": "def test_p():\n    pass\n",
    "tests/test_ref22_fiches_page.py": "def test_fp():\n    pass\n",
    "tests/test_photos_vlp.py": "def test_ph():\n    pass\n",
    "tests/test_noms_publics.py": "def test_n():\n    pass\n",
    "tests/test_boucle.py": "# lit scripts/noyau/page.py aussi\ndef test_b():\n    pass\n",
    "tests/test_clore.py": "# relit cloture.md\ndef test_c():\n    pass\n",
}


def depot(d):
    """Bâtir dans `d` un dépôt Git d'un commit, avec `FICHIERS` ; rend `d`."""
    for chemin, texte in FICHIERS.items():
        ecrire(os.path.join(d, *chemin.split("/")), texte)
    for args in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "départ"]):
        subprocess.run(["git", *args], cwd=d, check=True, capture_output=True)
    return d


def toucher(d, *chemins):
    """Ajouter une ligne à chaque fichier de `chemins` dans `d`."""
    for c in chemins:
        with open(os.path.join(d, *c.split("/")), "a", encoding="utf-8") as f:
            f.write("# changé\n")


def palier(d, *options):
    """`vlp.py palier --racine d <options>` : rend (code, sortie, la ligne PALIER, la ligne COMMANDE ou '')."""
    code, s = appel(["palier", "--racine", d, *options])
    lignes = s.splitlines()
    tete = next((l for l in lignes if l.startswith("PALIER")), "")
    commande = next((l for l in lignes if l.startswith("COMMANDE")), "")
    return code, s, tete, commande


def test_palier_aucun():
    with tempfile.TemporaryDirectory() as t:
        code, s, tete, commande = palier(depot(t))
        assert (code, tete, commande) == (0, "PALIER aucun", ""), "palier : rien de changé, aucun test\n" + s


def test_palier_doc():
    with tempfile.TemporaryDirectory() as t:
        d = depot(t)
        toucher(d, "cloture.md")
        code, s, tete, commande = palier(d)
        assert code == 0, "palier : doc\n" + s
        assert tete.startswith("PALIER doc · 2 fichier(s) de tests"), "palier : doc\n" + s
        assert commande == "COMMANDE uv run --frozen pytest -n 2 tests/test_clore.py tests/test_regles.py", \
            "palier : doc, test_regles et le test qui cite le chemin\n" + s


def test_palier_script_sans_les_lents():
    with tempfile.TemporaryDirectory() as t:
        d = depot(t)
        toucher(d, "scripts/noyau/page.py")
        code, s, tete, commande = palier(d)
        assert code == 0, "palier : script\n" + s
        assert tete.startswith("PALIER script · 5 fichier(s) de tests"), "palier : script\n" + s
        assert commande == ("COMMANDE uv run --frozen pytest -n 4 tests/test_noms_publics.py tests/test_page.py "
                            "tests/test_photos_vlp.py tests/test_ref22_fiches_page.py tests/test_regles.py"), \
            "palier : script, ses tests par leur nom, les photos, sans test_boucle\n" + s


def test_palier_boucle_ajoute_les_lents():
    with tempfile.TemporaryDirectory() as t:
        d = depot(t)
        toucher(d, "scripts/boucle.py")
        code, s, tete, commande = palier(d)
        assert code == 0, "palier : boucle\n" + s
        assert tete.startswith("PALIER boucle"), "palier : boucle\n" + s
        assert "tests/test_boucle.py" in commande, "palier : boucle joue les tests lents\n" + s


def test_palier_coeur_suite_entiere():
    with tempfile.TemporaryDirectory() as t:
        d = depot(t)
        toucher(d, "tests/conftest.py")
        code, s, tete, commande = palier(d)
        assert code == 0, "palier : coeur\n" + s
        assert tete.startswith("PALIER coeur"), "palier : coeur\n" + s
        assert commande == "COMMANDE uv run --frozen pytest -n 4", "palier : coeur, la suite entière\n" + s


def test_le_plus_haut_gagne():
    with tempfile.TemporaryDirectory() as t:
        d = depot(t)
        toucher(d, "README.md", "scripts/noyau/page.py")
        code, s, tete, _ = palier(d)
        assert code == 0, "palier : le plus haut gagne\n" + s
        assert tete.startswith("PALIER script"), "palier : le plus haut gagne\n" + s
        assert "RÈGLE README.md : doc — " in s, "palier : chaque chemin dit sa règle\n" + s
        assert "RÈGLE scripts/noyau/page.py : script — " in s, "palier : chaque chemin dit sa règle\n" + s


def test_un_fichier_neuf_non_suivi_compte():
    with tempfile.TemporaryDirectory() as t:
        d = depot(t)
        ecrire(os.path.join(d, "scripts", "noyau", "commun2.py"), "x = 1\n")
        code, s, tete, _ = palier(d)
        assert code == 0, "palier : un .py neuf compte\n" + s
        assert tete.startswith("PALIER script"), "palier : un .py neuf compte\n" + s


def test_depuis_une_revision():
    with tempfile.TemporaryDirectory() as t:
        d = depot(t)
        toucher(d, "scripts/noyau/commun.py")
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-am", "x"], cwd=d,
                       check=True, capture_output=True)
        assert palier(d)[2] == "PALIER aucun", "palier : contre HEAD, rien"
        code, s, tete, _ = palier(d, "--depuis", "HEAD~1")
        assert code == 0, "palier : --depuis voit le commit\n" + s
        assert tete.startswith("PALIER coeur"), "palier : --depuis voit le commit\n" + s


def test_hors_depot_garde():
    with tempfile.TemporaryDirectory() as t:
        code, s, _, _ = palier(t)
        assert (code, s[:6]) == (1, "GARDE:"), "palier : hors dépôt, une GARDE\n" + s


def test_le_registre_ne_cherche_pas_qui_le_cite():
    """Un test qui écrit son propre `CHANTIER.md` ne lit pas celui du kit : le registre ne fait jouer que les règles."""
    with tempfile.TemporaryDirectory() as t:
        d = depot(t)
        ecrire(os.path.join(d, "CHANTIER.md"), "le chantier\n")
        ecrire(os.path.join(d, "tests", "test_ouvrir.py"), "# bâtit son CHANTIER.md\ndef test_o():\n    pass\n")
        subprocess.run(["git", "add", "-A"], cwd=d, check=True, capture_output=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "y"], cwd=d,
                       check=True, capture_output=True)
        toucher(d, "CHANTIER.md")
        _, s, _, commande = palier(d)
        assert commande == "COMMANDE uv run --frozen pytest -n 1 tests/test_regles.py", "palier : registre\n" + s
