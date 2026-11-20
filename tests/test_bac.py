"""`noyau/bac.py` : le bac d'essai, `claude`, le kit d'essai, la transcription, l'aperçu local, la suite verte, les
crochets Git du dépôt — migré de l'ancienne suite maison (REF51). Chaque `assert` garde le libellé d'origine de son
`verifier` en tête de son message (REF5), puis le diagnostic.
"""
import importlib.util
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile

import pytest
from aides import RACINE, SCRIPTS, appel, ecrire, lire, mod

ICI = SCRIPTS     # le dossier des scripts, d'où ces tests viennent

CHANTIER = "# Chantier courant\n\n- **alias** : %s\n- **contexte** : %s\n"


def test_pre_commit(tmp_path, init_git):
    """Contrôler le pre-commit, lancé par `git commit` dans un dépôt à part (chantier REV)."""
    if not shutil.which("git"):
        pytest.skip("git absent — le hook pre-commit n'est pas testé")
    else:
        with tempfile.TemporaryDirectory(dir=tmp_path) as t:
            env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                       GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
            ecrire(env["GIT_CONFIG_GLOBAL"], "")
            depot = os.path.join(t, "plugin")
            for nom in (".claude-plugin", ".githooks", "agents", "hooks", "scripts", "skills"):
                shutil.copytree(os.path.join(RACINE, nom), os.path.join(depot, nom))
            shutil.copy(os.path.join(RACINE, ".gitattributes"), depot)
            for dossier, _, noms in os.walk(depot):
                for nom in (n for n in noms if n.endswith(".md")):
                    with open(os.path.join(dossier, nom), "rb") as f:
                        octets = f.read().replace(b"\r\n", b"\n")
                    with open(os.path.join(dossier, nom), "wb") as f:
                        f.write(octets.replace(b"\n", b"\r\n"))

            def git(*args):
                r = subprocess.run(["git"] + list(args), cwd=depot, env=env, capture_output=True, encoding="utf-8",
                                   errors="replace", check=False)
                return r.returncode, r.stdout + r.stderr

            init_git(depot)
            git("config", "core.hooksPath", ".githooks")
            # Le hook lance `scripts/vlp.py claude` (VIT19) ; hors suivi, ses .py ne réveillent pas pyright.
            ecrire(os.path.join(depot, ".git", "info", "exclude"), "scripts/\n")
            git("add", "-A")
            code, s = git("commit", "-q", "-m", "copie")
            # Le claude que le hook trouve, ce test le demande au même `vlp.py claude`, sans recopier où l'app le range.
            _, trouve = appel(["claude"])
            if not trouve.startswith("CLAUDE "):
                print("SAUTÉ: %s — le hook pre-commit n'est pas testé" % trouve.strip())
            else:
                assert ("validate sauté" not in s), ("hook : claude trouvé, validate lancé") + "\n" + str(s)
                assert (code == 0), ("hook : une copie en CRLF passe") + "\n" + str(s)
                ecrire(os.path.join(depot, ".claude-plugin", "plugin.json"), "{")
                git("add", "-A")
                code, s = git("commit", "-q", "-m", "casse")
                assert code == 1
                assert "pre-commit : .claude-plugin/plugin.json invalide" in s
                assert "marketplace.json" not in s
            code, s = git("check-attr", "eol", "--", "skills/chantier/SKILL.md")
            assert (s == "skills/chantier/SKILL.md: eol: lf\n"), (".gitattributes : les .md en LF") + "\n" + str(s)
            # JNT2 : les joints publiés en LF dans tout clone — un worktree en CRLF changeait leurs octets
            code, s = git("check-attr", "eol", "--", "templates/vlp.css", "templates/vlp.js", "a/couts.svg")
            assert (s == "templates/vlp.css: eol: lf\n"
                     "templates/vlp.js: eol: lf\na/couts.svg: eol: lf\n"), (".gitattributes : les joints (.css, .js, .svg) en LF") + "\n" + str(s)


def test_suite_verte(tmp_path, init_git):
    """`cocher` dans le kit exige la suite entière verte sur le code du jour (VIT11) : refus sans empreinte, accord
    après `noter_suite_verte`, refus après un script touché — pas après `sante-base.json` ni `context AI/` ; un projet
    équipé, sans plugin, coche sans suite."""
    def cocher(fichier, fiche):
        """Cocher `fiche` par `main` ; rendre (code, sortie)."""
        o = io.StringIO()
        return mod.main(["cocher", fichier, fiche], o), o.getvalue()

    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        init_git(t)
        for chemin, texte in ((".claude-plugin/plugin.json", "{}"), ("tests/conftest.py", ""),
                              ("scripts/sante-base.json", "[]\n")):
            ecrire(os.path.join(t, chemin), texte)
        fiches = os.path.join(t, "context AI", "f.md")
        ecrire(fiches, "# Z\n\n## Z1 [ ] — a\n\n## Z2 [ ] — b\n\n## Z3 [ ] — c\n")
        sans = cocher(fiches, "Z1")
        mod.noter_suite_verte(t, mod.empreinte_kit(t))
        apres = cocher(fiches, "Z1")
        ecrire(os.path.join(t, "scripts", "sante-base.json"), "[1]\n")
        hors = cocher(fiches, "Z2")
        ecrire(os.path.join(t, "scripts", "x.py"), "x = 1\n")
        touche = cocher(fiches, "Z3")
        assert sans[0] == 1
        assert "GARDE: Z1 non cochée" in sans[1]
        assert apres[0] == 0
        assert hors[0] == 0
        assert touche[0] == 1
        assert "GARDE: Z3 non cochée" in touche[1]
        assert lire(fiches).count("[x]") == 2
        os.remove(os.path.join(t, ".claude-plugin", "plugin.json"))
        equipe = cocher(fiches, "Z3")
        assert (equipe[0] == 0), ("VIT11 : un projet équipé (sans plugin) coche sans suite verte") + "\n" + str(repr(equipe))


def test_bac(tmp_path):
    with tempfile.TemporaryDirectory(dir=tmp_path) as tbac:
        dbac = os.path.join(tbac, "bac")
        code, s = appel(["bac", dbac])
        assert code == 0
        assert s.startswith("BAC %s\n" % dbac)
        assert (s.count("claude -p") == 2), ("bac : deux commandes claude -p") + "\n" + str(s)
        fbac = os.path.join(dbac, mod.BAC_FICHES)
        code, sv = appel(["valider", fbac])
        assert (code == 0), ("bac : le fichier de fiches se valide") + "\n" + str(sv)
        for ident in ("F1", "F2"):
            code, se_ = appel(["extraire", fbac, ident])
            assert code == 0
            assert ("## %s [ ]" % ident) in se_
        ns = [n for n in os.listdir(dbac) if re.match(r"^n\d\d\.txt$", n)]
        assert (len(ns) == 12), ("bac : douze fichiers n*.txt") + "\n" + str(" ".join(sorted(ns)))
        with open(fbac, encoding="utf-8") as f:
            texte_bac = f.read()
        assert (texte_bac.count("un appel par message") == 2), ("bac : « un appel par message » deux fois") + "\n" + str(texte_bac)
        assert ("par tour" not in texte_bac), ("bac : jamais « par tour »") + "\n" + str(texte_bac)
        code, s2 = appel(["bac", dbac])
        assert code == 1
        assert s2.startswith("GARDE:")
        # Dette REG : `clore` refusait le bac, faute de la ligne des lettres (REG3, 2026-09-29)
        for ident in ("F1", "F2"):
            appel(["cocher", fbac, ident])
        code, s3 = appel(["clore", dbac, "--livre", "x", "--resume", "x"])
        assert code == 0
        assert "CLOS F F1..F2" in s3


def test_claude(tmp_path):
    noms = ("VLP_CLAUDE", "PATH", "LOCALAPPDATA", "APPDATA")
    avant = {n: os.environ.get(n) for n in noms}
    with tempfile.TemporaryDirectory(dir=tmp_path) as tcl:
        def faux(*parties):
            p = os.path.join(tcl, *parties, "claude.exe")
            os.makedirs(os.path.dirname(p))
            ecrire(p, "")
            return p
        paquet = ("loc", "Packages", "Claude_x1", "LocalCache", "Roaming", "Claude", "claude-code")
        faux(*paquet, "2.1.9")
        p10 = faux(*paquet, "2.1.10")
        a99 = faux("app", "Claude", "claude-code", "2.1.99")
        try:
            os.environ.pop("VLP_CLAUDE", None)
            os.environ["PATH"] = os.path.join(tcl, "vide")
            os.environ["APPDATA"] = os.path.join(tcl, "app")
            os.environ["LOCALAPPDATA"] = os.path.join(tcl, "loc")
            code, s = appel(["claude"])
            assert code == 0
            assert s == "CLAUDE %s\n" % p10
            dbac = os.path.join(tcl, "bac")
            code, s = appel(["bac", dbac])
            assert code == 0
            assert (s.endswith(
                'SESSION Set-Location "%s"; & "%s"\n' % (os.path.abspath(dbac), p10)))
            spec = importlib.util.spec_from_file_location("boucle", os.path.join(ICI, "boucle.py"))
            assert spec
            assert spec.loader
            boucle = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(boucle)
            assert (boucle.trouver_claude(None) == p10), ("claude : boucle.py rend le même chemin") + "\n" + str(str(boucle.trouver_claude(None)))
            os.environ["LOCALAPPDATA"] = os.path.join(tcl, "vide")
            code, s = appel(["claude"])
            assert code == 0
            assert s == "CLAUDE %s\n" % a99
            os.environ["VLP_CLAUDE"] = "mon-claude"
            code, s = appel(["claude"])
            assert code == 0
            assert s == "CLAUDE mon-claude\n"
            os.environ.pop("VLP_CLAUDE")
            os.environ["APPDATA"] = os.path.join(tcl, "vide")
            code, s = appel(["claude"])
            assert code == 1
            assert s.startswith("GARDE: claude.exe introuvable")
            code, s = appel(["bac", os.path.join(tcl, "bac2")])
            assert code == 0
            assert 'GARDE: claude.exe introuvable' in s
            assert s.endswith('; & "claude"\n')
            # VIT19 : l'app range claude.exe un dossier plus bas, sous une empreinte ; la version reste au-dessus
            faux("loc2", *paquet[1:], "2.1.99")
            p288 = faux("loc2", *paquet[1:], "2.1.288", "36aa8c97bf86")
            os.environ["LOCALAPPDATA"] = os.path.join(tcl, "loc2")
            code, s = appel(["claude"])
            assert code == 0
            assert s == "CLAUDE %s\n" % p288
            sans_exe = os.path.join(tcl, "app2", "Claude", "claude-code")
            os.makedirs(os.path.join(sans_exe, "2.1.288", "36aa8c97bf86"))
            os.environ["LOCALAPPDATA"] = os.path.join(tcl, "vide")
            os.environ["APPDATA"] = os.path.join(tcl, "app2")
            code, s = appel(["claude"])
            assert code == 1
            assert s.startswith("GARDE: claude.exe absent de l'app")
            assert sans_exe in s
        finally:
            for n, v in avant.items():
                if v is None:
                    os.environ.pop(n, None)
                else:
                    os.environ[n] = v


def test_kit_essai(tmp_path):
    with tempfile.TemporaryDirectory(dir=tmp_path) as tke:
        src = os.path.join(tke, "kit")
        for sous_dossier in ("agents", "scripts", ".git", "context AI", os.path.join("evals", "results"),
                             os.path.join("evals", "cas")):
            os.makedirs(os.path.join(src, sous_dossier))
        fiche_src = os.path.join(src, "agents", "fiche.md")
        with open(fiche_src, "w", encoding="utf-8") as f:
            f.write("---\nname: fiche\nmaxTurns: 80\ntools: Read\n---\n\nCorps.\n")
        for rel in ("scripts/x.py", ".git/HEAD", "context AI/08-etat.md", "evals/results/r.json", "evals/cas/case.yaml"):
            with open(os.path.join(src, rel), "w", encoding="utf-8") as f:
                f.write("x\n")
        dke = os.path.join(tke, "copie")
        code, s = appel(["kit-essai", dke, "--max-turns", "6", "--kit", src])
        assert code == 0
        assert s == "KIT %s · maxTurns 80 → 6\n" % dke
        assert (mod.lire_max_turns(os.path.join(dke, "agents", "fiche.md")) == 6), ("kit-essai : maxTurns 6 dans la copie") + "\n" + str(repr(mod.lire_max_turns(os.path.join(dke, "agents", "fiche.md"))))
        assert (mod.lire_max_turns(fiche_src) == 80), ("kit-essai : maxTurns inchangé dans le kit") + "\n" + ""
        presents = [rel for rel in ("scripts/x.py", "evals/cas/case.yaml") if os.path.exists(os.path.join(dke, rel))]
        absents = [rel for rel in (".git", "context AI", "evals/results") if not os.path.exists(os.path.join(dke, rel))]
        assert len(presents) == 2
        assert len(absents) == 3
        code, s2 = appel(["kit-essai", dke, "--max-turns", "6", "--kit", src])
        assert code == 1
        assert s2.startswith("GARDE:")


def test_transcription(tmp_path):
    u = {"input_tokens": 1}
    lignes = [
        {"type": "user", "message": {"role": "user", "content": "fiche"}},
        # tour 1 sur trois lignes assistant, deux appels : Bash en erreur, puis Read réussi
        {"type": "assistant", "message": {"id": "m1", "usage": u, "stop_reason": None,
                                          "content": [{"type": "thinking", "thinking": "…"}]}},
        {"type": "assistant", "message": {"id": "m1", "usage": u, "stop_reason": None,
                                          "content": [{"type": "tool_use", "id": "tA", "name": "Bash", "input": {}}]}},
        {"type": "assistant", "message": {"id": "m1", "usage": u, "stop_reason": "tool_use",
                                          "content": [{"type": "tool_use", "id": "tB", "name": "Read", "input": {}}]}},
        {"type": "user", "message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "tA", "is_error": True, "content": "Exit code 3"}]}},
        {"type": "user", "message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "tB", "content": "fichier 01"}]}},
        {"type": "attachment", "attachment": {"type": "hook_non_blocking_error",
                                              "hookName": "PostToolUseFailure:Bash", "toolUseID": "tA"}},
        {"type": "attachment", "attachment": {"type": "hook_non_blocking_error",
                                              "hookName": "PostToolUse:Read", "toolUseID": "tB"}},
        {"type": "attachment", "attachment": {"type": "hook_additional_context", "hookName": "PostToolUseFailure:Bash",
                                              "toolUseID": "tA", "content": ["Attention : 1 tour restant."]}},
        {"type": "assistant", "message": {"id": "m2", "usage": u, "stop_reason": "end_turn",
                                          "content": [{"type": "text", "text": "RETOUR — fait 1/2\n\nIl reste un appel.\n"}]}},
    ]
    with tempfile.TemporaryDirectory(dir=tmp_path) as ttr:
        jsonl = os.path.join(ttr, "agent.jsonl")
        with open(jsonl, "w", encoding="utf-8") as f:
            f.writelines(json.dumps(ligne, ensure_ascii=False) + "\n" for ligne in lignes)
        code, s = appel(["transcription", jsonl])
        attendu = ("TOURS=2\n"
                   "APPELS=2 — Bash 1, Read 1\n"
                   "AVERTISSEMENTS=1\n"
                   "AVERTIS_PAR_TOUR=1:1\n"
                   "PREMIER_AVERTISSEMENT tour=1 outil=Bash is_error=oui hook=PostToolUseFailure:Bash\n"
                   "TEXTE=Attention : 1 tour restant.\n"
                   "HOOK_ERREURS=2 pour 2 appels\n"
                   "DERNIER mot=RETOUR stop_reason=end_turn\n"
                   "DERNIERE_LIGNE=Il reste un appel.\n")
        assert code == 0
        assert s == attendu
        sans = os.path.join(ttr, "sans.jsonl")
        with open(sans, "w", encoding="utf-8") as f:
            f.write(json.dumps(lignes[-1]) + "\n")
        code, s = appel(["transcription", sans])
        assert code == 0
        assert "PREMIER_AVERTISSEMENT aucun\n" in s
        assert "TEXTE=" not in s
        assert "AVERTIS_PAR_TOUR=aucun\n" in s
        # TOU1 : 3 avertissements au tour 2 (une salve de trois Read), 1 au tour 3
        salve = [{"type": "assistant", "message": {"id": "m1", "usage": u, "stop_reason": "tool_use",
                                                   "content": [{"type": "tool_use", "id": "s0", "name": "Read"}]}}]
        salve += [{"type": "assistant", "message": {"id": "m2", "usage": u, "stop_reason": "tool_use",
                                                    "content": [{"type": "tool_use", "id": i, "name": "Read"}]}}
                  for i in ("s1", "s2", "s3")]
        salve.append({"type": "assistant", "message": {"id": "m3", "usage": u, "stop_reason": "tool_use",
                                                       "content": [{"type": "tool_use", "id": "s4", "name": "Read"}]}})
        salve += [{"type": "attachment", "attachment": {"type": "hook_additional_context", "hookName": "PostToolUse:Read",
                                                        "toolUseID": i, "content": "Attention"}}
                  for i in ("s1", "s2", "s3", "s4")]
        par_tour = os.path.join(ttr, "par-tour.jsonl")
        with open(par_tour, "w", encoding="utf-8") as f:
            f.writelines(json.dumps(ligne) + "\n" for ligne in salve)
        code, s = appel(["transcription", par_tour])
        assert code == 0
        assert "AVERTISSEMENTS=4\nAVERTIS_PAR_TOUR=2:3,3:1\n" in s
        code, s = appel(["transcription", os.path.join(ttr, "absent.jsonl")])
        assert code == 1
        assert s.startswith("GARDE:")


def hook_isole(init_git, t):
    """Rendre un dépôt neuf sous `t`, le hook du kit branché et `scripts/` copié hors suivi (le hook y lance
    `vlp.py claude`, VIT19), le PATH sans pyright, uv ni claude, et `git(chemins, *args, **env)` : claude caché,
    APPDATA et LOCALAPPDATA vides sauf `env`."""
    depot = os.path.join(t, "depot")
    for nom in (".githooks", "scripts"):
        shutil.copytree(os.path.join(RACINE, nom), os.path.join(depot, nom))
    sans = [d for d in os.environ.get("PATH", "").split(os.pathsep)
            if d and not any(shutil.which(n, path=d) for n in ("pyright", "uv", "claude"))]
    base = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
                APPDATA="", LOCALAPPDATA="")
    ecrire(base["GIT_CONFIG_GLOBAL"], "")

    def git(chemins, *args, **env):
        r = subprocess.run(["git"] + list(args), cwd=depot, env=dict(base, PATH=os.pathsep.join(chemins), **env),
                           capture_output=True, encoding="utf-8", errors="replace", check=False)
        return r.returncode, r.stdout + r.stderr

    init_git(depot)
    git(sans, "config", "core.hooksPath", ".githooks")
    ecrire(os.path.join(depot, ".git", "info", "exclude"), "scripts/\n")
    return depot, sans, git


def test_hook_pyright(tmp_path, init_git):
    # TYP1, REF3 : le hook lance `uv run --frozen pyright` quand un .py est indexé. claude, uv et pyright cachés
    # (`hook_isole`) ; un faux uv en tête du PATH — un script sh, que le hook lance, quand uv ne saurait pas lancer
    # un faux pyright sous Windows — rend le verdict de pyright.
    if not shutil.which("git"):
        pytest.skip("git absent — le bloc pyright du hook n'est pas testé")
        return
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        depot, sans, git = hook_isole(init_git, t)
        def faux_uv(nom, code):
            d = os.path.join(t, nom)
            ecrire(os.path.join(d, "uv"), '#!/bin/sh\necho "faux uv $* : sortie %d"\nexit %d\n' % (code, code))
            os.chmod(os.path.join(d, "uv"), 0o755)
            return d
        rouge, vert = faux_uv("rouge", 1), faux_uv("vert", 0)
        ecrire(os.path.join(depot, "a.md"), "a\n")
        git(sans, "add", "a.md")
        code, s = git([rouge] + sans, "commit", "-q", "-m", "md")
        assert code == 0
        assert "pyright" not in s
        ecrire(os.path.join(depot, "a.py"), "x = 1\n")
        git(sans, "add", "a.py")
        code, s = git([rouge] + sans, "commit", "-q", "-m", "py")
        assert code == 1
        assert "faux uv run --frozen pyright : sortie 1" in s
        assert "pre-commit : pyright en erreur ou absent de l'atelier (uv sync), commit refusé." in s
        code, s = git(sans, "commit", "-q", "-m", "py")
        assert code == 1
        assert "pre-commit : uv introuvable, pyright non lancé, commit refusé" in s
        code, s = git([vert] + sans, "commit", "-q", "-m", "py")
        assert code == 0
        assert "faux uv run --frozen pyright : sortie 0" not in s


def test_hook_chemin(tmp_path, init_git):
    # CHM : le hook refuse une ligne ajoutée qui porte un chemin de machine, sous ses trois formes ; `~` passe, et une
    # ligne ancienne, gardée telle quelle, ne bloque rien. Les chemins se bâtissent par morceaux : écrits d'un bloc
    # dans ce fichier, ils feraient refuser son propre commit.
    if not shutil.which("git"):
        pytest.skip("git absent — le bloc des chemins du hook n'est pas testé")
        return
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        depot, sans, git = hook_isole(init_git, t)
        ecrire(os.path.join(depot, "a.md"), "le kit : ~/.claude/skills/vlp\n")
        git(sans, "add", "a.md")
        code, s = git(sans, "commit", "-q", "-m", "tilde")
        assert code == 0
        assert "chemin de machine" not in s
        refus = []
        for forme in ("C:" + "/Users/bob/x", "C:" + "\\Users\\bob\\x", "/mnt/c/" + "Users/bob/x", "C-" + "-Users-bob-Documents"):
            ecrire(os.path.join(depot, "b.md"), "voir `%s`\n" % forme)
            git(sans, "add", "b.md")
            code, s = git(sans, "commit", "-q", "-m", "chemin")
            refus.append(code == 1 and "pre-commit : chemin de machine dans une ligne ajoutée" in s)
        assert (refus == [True] * 4), ("CHM : hook, les trois formes de chemin de machine refusées (4 cas)") + "\n" + str(refus)


def test_hook_claude(tmp_path, init_git):
    # VIT19 : le hook demande claude à `vlp.py claude`. L'app là sans son claude.exe refuse le commit, en le
    # disant ; ni app ni claude, il passe averti. claude trouvé, validate lancé : `tester_pre_commit`.
    if not shutil.which("git"):
        pytest.skip("git absent — le bloc claude du hook n'est pas testé")
        return
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        depot, sans, git = hook_isole(init_git, t)
        app = os.path.join(t, "loc", "Packages", "Claude_x1", "LocalCache", "Roaming", "Claude", "claude-code")
        os.makedirs(os.path.join(app, "2.1.288", "36aa8c97bf86"))
        ecrire(os.path.join(depot, "a.md"), "a\n")
        git(sans, "add", "a.md")
        code, s = git(sans, "commit", "-q", "-m", "md", LOCALAPPDATA=os.path.join(t, "loc"))
        assert code == 1
        assert "GARDE: claude.exe absent de l'app" in s
        assert app in s
        assert "pre-commit : l'app Claude est là sans claude.exe trouvé, validate impossible, commit refusé." in s
        code, s = git(sans, "commit", "-q", "-m", "md")
        assert code == 0
        assert "pre-commit : claude introuvable, ni dans le PATH ni dans l'app, validate sauté." in s


def test_apercu(tmp_path, init_git):
    """servir et apercu (chantier LOC4) : un serveur sans cache, et une seule entrée dans launch.json."""
    import contextlib
    import threading
    import urllib.error
    import urllib.request

    voisine = ('{"name": "gabarits", "runtimeExecutable": "py",\n'
               '      "runtimeArgs": ["-c", "print(1)"],   "port": 8792}')
    launch = '{\n  "version": "0.0.1",\n  "configurations": [\n    %s\n  ]\n}' % voisine
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        # Ni la config globale ni les exclusions de l'utilisateur ne masquent le `.gitignore` du test.
        anciens = {k: os.environ.get(k) for k in ("GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM", "XDG_CONFIG_HOME")}
        os.environ.update(GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                          XDG_CONFIG_HOME=os.path.join(t, "xdg"))
        ecrire(os.environ["GIT_CONFIG_GLOBAL"], "")
        try:
            p = os.path.join(t, "proj")
            ecrire(os.path.join(p, "CHANTIER.md"), CHANTIER % ("pz", "context AI/"))
            lancement = os.path.join(p, ".claude", "launch.json")
            lu = lambda: pathlib.Path(lancement).read_text(encoding="utf-8", newline="")
            entrees = lambda: [e for e in json.loads(lu())["configurations"] if e["name"].startswith("apercu-")]
            git_ok = bool(shutil.which("git"))
            if git_ok:
                init_git(p)

            code, s = appel(["apercu", p])
            assert code == 0
            assert s.startswith("APERCU écrit apercu-proj · port 8790 · ")
            assert [e["port"] for e in entrees()] == [8790]
            ecrire(lancement, launch)
            avant_voisine = lu().split(voisine)
            code, s = appel(["apercu", p])
            e = entrees()
            assert code == 0
            assert s.startswith("APERCU écrit apercu-proj · port 8790")
            assert len(e) == 1
            assert (e[0]["runtimeArgs"][1:] == ["servir", os.path.join(p, "context AI", "artefacts").replace("\\", "/"),
                                                     "8790"])
            une_fois = lu()
            code, s = appel(["apercu", p])
            assert code == 0
            assert s.startswith("APERCU déjà apercu-proj")
            assert lu() == une_fois
            assert len(entrees()) == 1
            assert lu().split(voisine)[0] == avant_voisine[0]
            assert voisine in lu()
            code, s = appel(["apercu", p, "--port", "8801"])
            assert code == 0
            assert "remplacé apercu-proj · port 8801" in s
            assert [x["port"] for x in entrees()] == [8801]
            assert voisine in lu()
            code, s = appel(["apercu", p])
            assert code == 0
            assert "déjà apercu-proj · port 8801" in s
            ecrire(lancement, '{"version": "0.0.1", "configurations": []}\r\n')
            code, s = appel(["apercu", p])
            assert code == 0
            assert len(entrees()) == 1
            assert "\r\n" in lu()
            assert "\n" not in lu().replace("\r\n", "")
            for nom, contenu in (("illisible", "{pas du json"), ("sans tableau", '{"version": "0.0.1"}'),
                                 ("deux entrées", '{"configurations": [{"name": "apercu-proj"}, {"name": "apercu-proj"}]}')):
                ecrire(lancement, contenu)
                code, s = appel(["apercu", p])
                assert code == 1
                assert s.startswith("GARDE:")
                assert lu() == contenu
            code, s = appel(["apercu", os.path.join(t, "nulle-part")])
            assert code == 1
            assert s.startswith("GARDE: pas de projet")
            if not git_ok:
                pytest.skip("git absent — la GARDE du .gitignore n'est pas testée")
            else:
                os.remove(lancement)
                code, s = appel(["apercu", p])
                assert code == 0
                assert len(entrees()) == 1
                assert s.splitlines()[-1].startswith("GARDE: .claude/launch.json")
                ecrire(os.path.join(p, ".gitignore"), ".claude/launch.json\n")
                code, s = appel(["apercu", p])
                assert code == 0
                assert s.startswith("APERCU déjà")
                assert "GARDE" not in s

            # servir : un vrai serveur, sur un port libre choisi par le système (port 0).
            art = os.path.join(t, "art")
            ecrire(os.path.join(art, "a.html"), "<p>é</p>")
            ecrire(os.path.join(art, "vlp.js"), "var x = 'é';")
            ecrire(os.path.join(art, "sous", "b.svg"), "<svg/>")
            serveur = mod.faire_serveur(art, 0)
            fil = threading.Thread(target=serveur.serve_forever, daemon=True)
            fil.start()
            base = "http://127.0.0.1:%d" % serveur.server_port

            def prendre(chemin):
                try:
                    with urllib.request.urlopen(base + chemin) as r:
                        return r.status, r.headers, r.read().decode("utf-8")
                except urllib.error.HTTPError as err:
                    return err.code, err.headers, ""
            try:
                with contextlib.redirect_stderr(io.StringIO()):     # le journal des requêtes
                    statut, tetes, corps = prendre("/a.html")
                    assert statut == 200
                    assert tetes["Cache-Control"] == "no-store"
                    assert tetes["Content-Type"] == "text/html; charset=utf-8"
                    assert corps == "<p>é</p>"
                    assert prendre("/vlp.js")[1]["Content-Type"] == "text/javascript; charset=utf-8"
                    assert prendre("/sous/b.svg")[1]["Content-Type"] == "image/svg+xml; charset=utf-8"
                    assert prendre("/vlp.js")[1]["Cache-Control"] == "no-store"
                    statut, tetes, corps = prendre("/_telephone?page=sous/b.svg")
                    assert statut == 200
                    assert 'src="/sous/b.svg"' in corps
                    assert "width:375px" in corps
                    assert tetes["Cache-Control"] == "no-store"
                    for mauvais in ("", "?page=../secret", "?page=/etc/passwd", "?page=<script>", "?page=a.html%22onload%3D1"):
                        assert (prendre("/_telephone" + mauvais)[0] == 400), ("servir : /_telephone%s → 400, jamais de cadre" % mauvais) + "\n" + str(mauvais)
                    assert (prendre("/nulle.html")[0] == 404), ("servir : page absente → 404 sans cache") + "\n" + "404"
            finally:
                serveur.shutdown()
                serveur.server_close()
            code, s = appel(["servir", os.path.join(t, "absent"), "8800"])
            assert code == 1
            assert s.startswith("GARDE: dossier introuvable")
            code, s = appel(["servir", art, "99999"])
            assert code == 1
            assert s.startswith("GARDE: port 99999")
        finally:
            for k, v in anciens.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v


def test_nuits(tmp_path, init_git):
    """NUI3 : `vlp.py nuits noter` écrit une `note`, ou le `stop`, au carnet de `VLP_CARNET`, sinon au
    carnet du jour du dépôt ; sans l'un ni l'autre : GARDE, sort 1."""
    env = {k: os.environ.pop(k, None) for k in ("VLP_CARNET", "VLP_CANAL")}
    try:
        with tempfile.TemporaryDirectory(dir=tmp_path) as t:
            c = os.path.join(t, "nuit.jsonl")
            os.environ["VLP_CARNET"] = c
            sortie = [io.StringIO() for _ in range(3)]
            codes = [mod.main(["nuits", "noter", "première", "--canal", "A"], sortie[0]),
                     mod.main(["nuits", "noter", "deuxième"], sortie[1])]
            os.environ["VLP_CANAL"] = "B"
            codes.append(mod.main(["nuits", "noter", "arrêtez", "--stop"], sortie[2]))
            lignes = mod.carnet.lire(c)
            assert codes == [0, 0, 0]
            assert [d["note"] for d in lignes] == ["première", "deuxième", None]
            assert [d["stop"] for d in lignes] == [None, None, "arrêtez"]
            assert [d["canal"] for d in lignes] == ["A", None, "B"]
            assert all(s.getvalue() == "NOTÉ %s\n" % c for s in sortie)
            assert all(d["nuit"] == "nuit" and d["role"] is None for d in lignes)
            del os.environ["VLP_CARNET"], os.environ["VLP_CANAL"]
            o = io.StringIO()
            code = mod.cmd_nuits_noter("sans dépôt", None, False, o, dossier=t)
            assert code == 1
            assert o.getvalue().startswith("GARDE:")
            assert os.listdir(t) == ["nuit.jsonl"]
            init_git(t)
            o = io.StringIO()
            code = mod.cmd_nuits_noter("du jour", "A", False, o, dossier=t)
            jour = mod.carnet.du_jour(t)
            assert code == 0
            assert jour
            assert o.getvalue() == "NOTÉ %s\n" % jour
            assert os.path.join(".git", "vlp-nuit") in jour
            assert [d["note"] for d in mod.carnet.lire(jour)] == ["du jour"]
    finally:
        for k, v in env.items():
            if v is not None:
                os.environ[k] = v
