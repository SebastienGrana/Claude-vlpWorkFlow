"""`noyau/relecture.py`. Deux étages (socle de `REF`, « La découpe sépare la décision de Git ») : les décisions qui ne
lancent pas `git` (REF47), chacune sur le texte qu'un `git` aurait rendu ; puis `relecture` et le retard du plugin
sur un vrai dépôt, migrés de l'ancienne suite maison (REF58), chaque `assert` migré au libellé d'origine de son
`verifier` (REF5).
"""
import io
import os
import shutil
import subprocess
import tempfile

import pytest
from aides import appel, ecrire, mod
from noyau import relecture


def test_relectures_de_garde_le_prefixe():
    liste = "\n".join(["worktree /d/kit", "HEAD abc", "", "worktree /t/vlp-relecture-W1-x", "detached", "",
                       "worktree /t/vlp-relecture-W2-y", "", "worktree /t/autre"])
    assert relecture.relectures_de(liste, "vlp-relecture-W1-") == ["/t/vlp-relecture-W1-x"], \
        "relecture : canaux — chacun ne retire que ses worktrees"
    assert relecture.relectures_de(liste, "vlp-relecture-") == ["/t/vlp-relecture-W1-x", "/t/vlp-relecture-W2-y"]
    assert relecture.relectures_de("", "vlp-relecture-") == []


def test_chemins_a_suivre_sans_le_cache_de_python():
    assert relecture.chemins_a_suivre("ctx/a.md\nctx/__pycache__/\n\nCLAUDE.md\n") == ["ctx/a.md", "CLAUDE.md"]


def test_meme_depot_ailleurs(tmp_path):
    commun, kit, arbre = (os.path.join(str(tmp_path), n) for n in ("depot/.git", "depot", "arbre"))
    assert relecture.meme_depot_ailleurs("%s\n%s\n" % (commun, kit), "%s\n%s\n" % (commun, arbre))
    assert not relecture.meme_depot_ailleurs("%s\n%s\n" % (commun, kit), "%s\n%s\n" % (commun, kit))   # même dossier
    assert not relecture.meme_depot_ailleurs("%s\n%s\n" % (commun, kit), "%s/autre/.git\n%s\n" % (tmp_path, arbre))
    assert not relecture.meme_depot_ailleurs("", "%s\n%s\n" % (commun, arbre))   # git muet


CHANTIER = "# Chantier courant\n\n- **alias** : %s\n- **contexte** : %s\n"


def _tester_canaux(g):
    # Deux canaux de nuit (chantier NUI) : chacun ne retire que ses worktrees.
    for canal in ("A", "B"):
        os.environ["VLP_CANAL"] = canal
        appel(["relecture", "X1"])
    noms = [os.path.basename(l.split(" ")[0].rstrip("/\\")) for l in g("worktree", "list").splitlines()[1:]]
    os.environ["VLP_CANAL"] = "B"
    retire_b = appel(["relecture", "--retirer"])
    reste_a = [os.path.basename(l.split(" ")[0].rstrip("/\\")) for l in g("worktree", "list").splitlines()[1:]]
    del os.environ["VLP_CANAL"]
    assert (len(noms) == 4 and sum(n.startswith("vlp-relecture-A-") for n in noms) == 2
             and sum(n.startswith("vlp-relecture-B-") for n in noms) == 2 and retire_b == (0, "RETIRÉ 2\n")
             and len(reste_a) == 2 and all(n.startswith("vlp-relecture-A-") for n in reste_a)), ("relecture : canaux — chacun ne retire que ses worktrees") + "\n" + str("%s %s %s" % (noms, retire_b, reste_a))
    assert (appel(["relecture", "--retirer"]) == (0, "RETIRÉ 2\n")
             and len(g("worktree", "list").splitlines()) == 1), ("relecture : sans canal, --retirer retire tout") + "\n" + str(g("worktree", "list"))


def test_relecture(tmp_path, init_git):
    """Contrôler `relecture` dans un dépôt à part : instantané, `--sha`, canaux (chantier REV)."""
    if not shutil.which("git"):
        pytest.skip("git absent — relecture n'est pas testée")
    else:
        with tempfile.TemporaryDirectory(dir=tmp_path) as t:
            env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                       GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
            ecrire(env["GIT_CONFIG_GLOBAL"], "")
            depot = os.path.join(t, "r")

            def g(*args):
                return subprocess.run(["git"] + list(args), cwd=depot, env=env, check=True, capture_output=True,
                                      encoding="utf-8").stdout

            def lu(*chemin):
                c = os.path.join(*chemin)
                return mod.lire(c) if os.path.isfile(c) else None

            FICHE_X = ("# Chantier X\n\n**Ouvert.** le 2026-10-08.\n\n## Le socle commun\n\nSocle X.\n\n## L'ordre des fiches\n\n---\n\n"
                       "<!-- FICHE:X1 -->\n## X1 %s — relire\n\n**Fichiers** : `a.py` — et rien d'autre.\n\n"
                       "**Prompt**\nb.py n'est pas nommé.\n<!-- /FICHE -->\n")
            ecrire(os.path.join(depot, "CHANTIER.md"), CHANTIER % ("px", ".") + "- **fichier d'état** : ctx d/etat.md\n")
            ecrire(os.path.join(depot, "f.md"), FICHE_X % "[ ]")
            ecrire(os.path.join(depot, "a.py"), "a\n")
            ecrire(os.path.join(depot, "ctx d", "etat.md"), "journal\n")
            init_git(depot)
            g("add", "-A")
            g("commit", "-q", "-m", "init")
            # Une fiche finie, pas encore commitée : a.py changé, b.py nouveau, la case cochée.
            ecrire(os.path.join(depot, "a.py"), "a2\n")
            ecrire(os.path.join(depot, "b.py"), "b\n")
            ecrire(os.path.join(depot, "f.md"), FICHE_X % "[x]")
            ecrire(os.path.join(depot, "ctx d", "etat.md"), "journal\nune décision\n")  # le journal, jamais hors fiche (REV7)
            tete, etat = g("rev-parse", "HEAD"), g("status", "--porcelain")
            ici, tmp = os.getcwd(), tempfile.tempdir
            tempfile.tempdir = t
            os.chdir(depot)
            try:
                code, s = appel(["relecture", "X1"])
                vu = dict(l.split("=", 1) for l in s.splitlines() if l.startswith(("APRÈS=", "AVANT=")))
                apres, avant = vu.get("APRÈS", "?"), vu.get("AVANT", "?")
                assert (code == 0
                         and g("rev-parse", "HEAD") == tete and g("status", "--porcelain") == etat
                         and lu(apres, "a.py") == "a2\n" and lu(apres, "b.py") == "b\n"
                         and lu(avant, "a.py") == "a\n" and lu(avant, "b.py") is None), ("relecture : l'instantané prend l'arbre sans bouger HEAD") + "\n" + str(s + g("status", "--porcelain"))
                reperes = [s.find(r) for r in ("APRÈS=", "AVANT=", "Socle X.", "--- socle, lignes : ", "## X1 [x] — relire",
                                               "--- fiche, lignes : ", "M\ta.py", "HORS FICHE", "diff --git")]
                assert ([l for l in s.splitlines() if l.startswith("HORS FICHE")] == ["HORS FICHE b.py"]
                         and -1 not in reperes and reperes == sorted(reperes)
                         and "\nFICHIER=" not in "\n" + s), ("relecture : un fichier hors fiche") + "\n" + str(s)  # FFE
                # Deux relecteurs lancés ensemble (chantier ISO, ISO7) : celui d'une autre fiche, même en GARDE:,
                # ne retire pas les copies de X1.
                autre = [appel(["relecture", "X9"]), appel(["relecture", "X9", "--retirer"])]
                noms = [os.path.basename(l.split(" ")[0].rstrip("/\\")) for l in g("worktree", "list").splitlines()[1:]]
                assert (autre[0][0] == 1 and autre[1] == (0, "RETIRÉ 0\n") and len(noms) == 2
                         and all(n.startswith("vlp-relecture-X1-") for n in noms)), ("relecture : deux fiches ensemble, chacune ne retire que ses copies (chantier ISO)") + "\n" + str("%s %s" % (autre, noms))
                code, s = appel(["relecture", "--retirer"])
                assert (code == 0 and s == "RETIRÉ 2\n"
                         and len(g("worktree", "list").splitlines()) == 1), ("relecture : --retirer") + "\n" + str(s + g("worktree", "list"))
                g("add", "-A")
                g("commit", "-q", "-m", "X1 : relire")
                appel(["relecture", "X1", "--sha", "HEAD"])
                code, s = appel(["relecture", "X1", "--sha", "HEAD"])
                liste = g("worktree", "list")
                assert (code == 0
                         and "M\ta.py\nA\tb.py\nM\tctx d/etat.md\nM\tf.md\nHORS FICHE b.py\ndiff --git" in s
                         and len(liste.splitlines()) == 3 and appel(["relecture", "--retirer"]) == (0, "RETIRÉ 2\n")), ("relecture --sha : le commit contre son parent, ceux de l'appel d'avant retirés") + "\n" + str(s + liste)
                _tester_canaux(g)
                gardes = [appel(["relecture", "X9"]), appel(["relecture", "X1", "--sha", "0badc0de"])]
                mod.etat.GIT = "git-absent-vlp"
                gardes.append(appel(["relecture", "X1"]))
                mod.etat.GIT = "git"
                assert (all(c == 1 and s.startswith("GARDE: ") for c, s in gardes)
                         and len(g("worktree", "list").splitlines()) == 1), ("relecture : fiche absente, commit inconnu, sans Git — GARDE, sort 1, aucun worktree") + "\n" + str(gardes)
            finally:
                mod.etat.GIT = "git"
                tempfile.tempdir = tmp
                os.chdir(ici)


def test_retard_plugin(tmp_path, init_git):
    """ESR1 : un worktree du kit en avance de code sur le kit chargé — la carte le dit."""
    if not shutil.which("git"):
        pytest.skip("git absent — retard_plugin n'est pas testé")
        return
    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(tr, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        ecrire(env["GIT_CONFIG_GLOBAL"], "")
        kit, wt, autre = (os.path.join(tr, x) for x in ("kit", "wt", "autre"))

        def git(d, *args):
            subprocess.run(["git"] + list(args), cwd=d, env=env, check=True, capture_output=True)

        def commit(d, chemin, texte):
            ecrire(os.path.join(d, chemin), texte)
            git(d, "add", "-A")
            git(d, "commit", "-q", "-m", chemin)
        for d in (kit, autre):
            os.makedirs(d)
            init_git(d)
            commit(d, "CHANTIER.md", "# C\n\n")
        git(kit, "worktree", "add", "-q", "-b", "fiche", wt)
        commit(wt, "scripts/x.py", "x = 1\n")
        r1 = mod.retard_plugin(wt, kit=kit)
        commit(wt, "context AI/n.md", "note\n")
        r2 = mod.retard_plugin(wt, kit=kit)
        muets = (mod.retard_plugin(kit, kit=kit), mod.retard_plugin(autre, kit=kit))
        garde, mod.etat.KIT = mod.etat.KIT, kit
        try:
            o = io.StringIO()
            mod.carte(wt, o)
        finally:
            mod.etat.KIT = garde
        lignes = [l for l in o.getvalue().split("\n") if l.startswith("PLUGIN_RETARD=")]
        assert (r1 is not None and r1[0] == 1 and r1[2] == "fiche" and r2 is not None and r2[0] == 1
                 and muets == (None, None) and len(lignes) == 1 and lignes[0].startswith("PLUGIN_RETARD=1 ")
                 and lignes[0].endswith("merge --ff-only fiche")), ("ESR1 : retard du plugin — 1 commit de scripts/ compté, context AI/ non, muet sur le kit "
                 "et un autre dépôt, une ligne dans la carte — mutant : chemins retirés du rev-list") + "\n" + str((r1, r2, muets, lignes))
        commit(wt, "nuit.md", "nuit\n")
        r3 = mod.retard_plugin(wt, kit=kit)
        assert (r3 is not None and r3[0] == 2 and r3[2] == "fiche"), ("NUI13 : nuit.md compte dans le code du plugin — scripts/x.py et nuit.md font 2, context AI/n.md "
                 "reste hors compte — mutant : nuit.md retiré de CODE_PLUGIN") + "\n" + str(r3)
