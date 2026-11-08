"""ALG4 : `vlp.py fin` — la fin de fiche en un appel : santé, palier (dans le kit), coche, note, coût, commit ; arrêt au
premier `GARDE:`, rien d'écrit après. Chaque test bâtit son propre dépôt dans un dossier temporaire."""
import os
import subprocess
import tempfile

import noyau.fin
import noyau.palier
from aides import appel, ecrire, lire

FICHES = "# Chantier Z — essai\n\n**Ouvert.** le 2026-01-01.\n\n## Le socle commun\n\nrien\n\n---\n\n" \
         "<!-- FICHE:Z1 -->\n## Z1 [ ] — Écrire le un\n\n**Dépend de** : rien.\n**Fichiers** : README.md, scripts/x.py\n\n**Prompt**\nx\n<!-- /FICHE -->\n"


def projet(d, kit=False):
    """Bâtir dans `d` un projet d'un commit (un faux kit si `kit`) avec le fichier de fiches `context AI/f.md`."""
    fichiers = {"context AI/f.md": FICHES, "README.md": "projet\n", "scripts/x.py": "x = 1\n"}
    if kit:
        fichiers.update({".claude-plugin/plugin.json": "{}", "tests/conftest.py": "", "tests/test_x.py": "\n"})
    for chemin, texte in fichiers.items():
        ecrire(os.path.join(d, *chemin.split("/")), texte)
    for args in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "0"]):
        subprocess.run(["git", *args], cwd=d, check=True, capture_output=True)
    return d


def git(d, *args):
    """La sortie de `git <args>` dans `d`, sans fin de ligne."""
    return subprocess.run(["git", *args], cwd=d, capture_output=True, encoding="utf-8", check=True).stdout.strip()


def fin(d, *options):
    """`vlp.py fin "<d>/context AI/f.md" Z1 --note vu <options>` : rend (code, sortie)."""
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    avant = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    try:
        return appel(["fin", os.path.join(d, "context AI", "f.md"), "Z1", "--note", "vu", *options])
    finally:
        for k, v in avant.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_fin_chemin_entier():
    with tempfile.TemporaryDirectory() as t:
        d = projet(t)
        ecrire(os.path.join(d, "README.md"), "projet changé\n")
        code, s = fin(d)
        assert code == 0, "fin : le chemin entier passe\n" + s
        assert "FIN Z1 · COMMIT " in s, "fin : il dit le commit\n" + s
        assert git(d, "log", "-1", "--format=%s") == "Z1 : Écrire le un", "fin : le commit de la fiche\n" + s
        fiches = lire(os.path.join(d, "context AI", "f.md"))
        assert "## Z1 [x]" in fiches, "fin : la fiche cochée\n" + fiches
        assert "**Constaté** : vu" in fiches, "fin : le critère constaté noté dans la fiche\n" + fiches
        assert git(d, "status", "--short") == "", "fin : tout est commité\n" + git(d, "status", "--short")


def test_fin_arret_coche():
    with tempfile.TemporaryDirectory() as t:
        d = projet(t)
        chemin = os.path.join(d, "context AI", "f.md")
        ecrire(chemin, FICHES.replace("## Z1 [ ]", "## Z1 [x]"))
        tete = git(d, "rev-parse", "HEAD")
        code, s = fin(d)
        assert code == 1, "fin : une fiche déjà cochée arrête\n" + s
        assert "FIN ARRÊT coche" in s, "fin : il dit l'étape\n" + s
        assert git(d, "rev-parse", "HEAD") == tete, "fin : aucun commit après l'arrêt"
        assert "**Constaté**" not in lire(chemin), "fin : rien d'écrit après l'arrêt"


def test_fin_arret_sante(monkeypatch):
    with tempfile.TemporaryDirectory() as t:
        d = projet(t)
        monkeypatch.setattr(noyau.fin, "etape", lambda argv: (1, "GARDE: une fonction empire\n")
                            if argv[0] == "sante" else (0, ""))
        code, s = fin(d)
        assert code == 1, "fin : la santé arrête\n" + s
        assert "FIN ARRÊT santé" in s, "fin : il dit l'étape\n" + s
        assert "## Z1 [ ]" in lire(os.path.join(d, "context AI", "f.md")), "fin : rien coché après la santé"


def test_fin_arret_palier_dans_le_kit(monkeypatch):
    with tempfile.TemporaryDirectory() as t:
        d = projet(t, kit=True)
        ecrire(os.path.join(d, "scripts", "x.py"), "x = 2\n")
        monkeypatch.setattr(noyau.palier, "lancer", lambda args, racine: 1)
        code, s = fin(d)
        assert code == 1, "fin : un palier rouge arrête\n" + s
        assert "FIN ARRÊT palier" in s, "fin : il dit l'étape\n" + s
        assert "## Z1 [ ]" in lire(os.path.join(d, "context AI", "f.md")), "fin : rien coché après le palier"


def test_fin_refuse_un_fichier_etranger():
    """Un fichier changé hors de la ligne **Fichiers** — celui d'une autre séance du même dossier — fait refuser, avant
    toute écriture : jamais `git add -A` (Emergence-Ants, ca8aed1, 2026-11-08)."""
    with tempfile.TemporaryDirectory() as t:
        d = projet(t)
        ecrire(os.path.join(d, "README.md"), "projet changé" + chr(10))
        ecrire(os.path.join(d, "autre.txt"), "le travail d'une autre séance" + chr(10))
        tete = git(d, "rev-parse", "HEAD")
        code, s = fin(d)
        assert code == 1, "fin : un fichier étranger arrête : " + s
        assert "FIN ARRÊT fichiers" in s, "fin : il dit l'étape : " + s
        assert "autre.txt" in s, "fin : il nomme le fichier étranger : " + s
        assert git(d, "rev-parse", "HEAD") == tete, "fin : aucun commit"
        assert "## Z1 [ ]" in lire(os.path.join(d, "context AI", "f.md")), "fin : rien coché"
