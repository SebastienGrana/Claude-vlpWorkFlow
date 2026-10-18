"""Les règles d'`enchainer` et du lanceur : l'arrière-plan, le rejeu, `commiter`, le parallèle, le tri du lanceur —
migré de `scripts/test-vlp.py` (REF51). Chaque `assert` garde le libellé d'origine de son `verifier` en tête de son
message (REF5), puis le diagnostic.
"""
import io
import json
import os
import subprocess
import sys
import tempfile
import time

from aides import RACINE, SCRIPTS, appel, ecrire, mod

ICI = SCRIPTS     # le dossier de scripts/test-vlp.py, d'où ces tests viennent

def test_ena2_arriere_plan():
    """ENA2 : la fiche et son relecteur partent par l'outil `Agent` en arrière-plan — la skill forkée
    attendait la fin même en `background: true` (bac `ENA2`, 2026-10-12), la conversation restait prise
    tout le temps de la fiche (≈ 45 min le 2026-10-03, `ENA1`) ; le chef lit le statut à la notification
    de fin, pas dans ce que l'appel rend tout de suite."""
    chef = io.open(os.path.join(RACINE, "skills", "enchainer", "SKILL.md"), encoding="utf-8").read()
    plat = " ".join(chef.split())
    assert ('subagent_type: "vlp:fiche"' in plat and 'subagent_type: "vlp:relecture"' in plat
             and plat.count("run_in_background: true") == 2), ("ENA2 : fiche et relecteur lancés par Agent, en arrière-plan") + "\n" + "skills/enchainer/SKILL.md"
    assert ("Fiche à jouer : <fiche> " in plat), ("ENA2 : le prompt de la fiche se lit par FICHE_A_JOUER (id suivi d'une espace, pas d'un point)") + "\n" + "skills/enchainer/SKILL.md"
    assert ("**notification de fin**" in chef), ("ENA2 : le chef lit le Result à la notification de fin") + "\n" + "absent de skills/enchainer/SKILL.md"


def test_gai1_rejeu():
    """GAI1 : le rejeu après `CONFLIT` sort du plafond et de `--tourne` — il repart aussitôt ; seul un 2ᵉ `CONFLIT`
    de la même fiche attend que plus rien ne tourne (les deux causes d'`ISO7`, tranchées le 2026-10-17)."""
    plat = " ".join(io.open(os.path.join(RACINE, "skills", "enchainer", "SKILL.md"), encoding="utf-8").read().split())
    assert ("plafond compte chaque fiche une fois, plus chaque rejeu après `REFUSÉE` ; un rejeu après `CONFLIT`, non"
             in plat and "chaque départ, rejeu compris" not in plat), ("GAI1 : le plafond compte chaque fiche une fois, le rejeu après CONFLIT hors plafond") + "\n" + "skills/enchainer/SKILL.md"
    assert ("`CONFLIT` : la fiche sort de `--tourne` et repart aussitôt" in plat
             and "à son 2ᵉ `CONFLIT`, elle y reste" in plat), ("GAI1 : CONFLIT sort de --tourne et repart aussitôt ; le 2ᵉ attend") + "\n" + "skills/enchainer/SKILL.md"


def test_ena4_commiter(tmp_path):
    """ENA4 : `commiter` — coche la fiche et ne commite que ses fichiers changés et le fichier de fiches ; un changé
    hors de sa ligne **Fichiers** se dit `HORS:` et reste hors du commit (jamais `git add -A`)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        d = os.path.join(t, "d")
        os.makedirs(os.path.join(d, "ctx"))
        fiches = os.path.join(d, "ctx", "fiches.md")
        ecrire(fiches, "# Essai\n\n## Le socle commun\n\nRien.\n\n---\n" + "".join(
            "<!-- FICHE:%s -->\n## %s [ ] — Toucher %s\n\n**Dépend de** : rien.\n**Fichiers** : `src/%s`%s.\n\n"
            "**Critère de fin**\nRien.\n<!-- /FICHE -->\n" % (f, f, n, n, p) for f, n, p in (
                ("C1", "a.py", " (la ligne « **b** » seule)"), ("C2", "b.py", ""))))
        for n in ("src/a.py", "src/b.py", "scripts/sante-base.json"):
            os.makedirs(os.path.dirname(os.path.join(d, n)), exist_ok=True)
            ecrire(os.path.join(d, n), "x = 1\n")
        vieux = dict(os.environ)
        os.environ.update(GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="t",
                          GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        try:
            ecrire(os.environ["GIT_CONFIG_GLOBAL"], "")
            for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "départ"]):
                subprocess.run(["git"] + args, cwd=d, check=True, capture_output=True)
            for n in ("src/a.py", "src/b.py", "scripts/sante-base.json"):
                ecrire(os.path.join(d, n), "x = 2\n")
            code, sortie = appel(["commiter", fiches, "C1"])
            montre = subprocess.run(["git", "show", "--name-only", "--format=%s", "HEAD"], cwd=d, capture_output=True,
                                    encoding="utf-8").stdout.split()
            reste = subprocess.run(["git", "status", "--porcelain"], cwd=d, capture_output=True, encoding="utf-8").stdout
            # Puis le même dépôt devient le kit (`est_kit`) : C2 y prend la base du cliquet, commun.
            marques = (".claude-plugin/plugin.json", "scripts/test-vlp.py")
            for n in marques:
                os.makedirs(os.path.dirname(os.path.join(d, n)), exist_ok=True)
                ecrire(os.path.join(d, n), "{}\n")
            for args in (["add", "--"] + list(marques), ["commit", "-q", "-m", "kit"]):
                subprocess.run(["git"] + args, cwd=d, check=True, capture_output=True)
            mod.noter_suite_verte(d, mod.empreinte_kit(d))  # cocher dans le kit exige la suite verte (VIT11)
            kit = appel(["commiter", fiches, "C2"])
            montre_kit = subprocess.run(["git", "show", "--name-only", "--format=%s", "HEAD"], cwd=d,
                                        capture_output=True, encoding="utf-8").stdout.split()
        finally:
            os.environ.clear()
            os.environ.update(vieux)
        assert (code == 0 and "src/a.py" in montre and "ctx/fiches.md" in montre and "src/b.py" not in montre
                 and "## C1 [x]" in io.open(fiches, encoding="utf-8").read()), ("ENA4 : commiter C1 ne prend que src/a.py et le fichier de fiches, coché") + "\n" + str(repr((code, sortie, montre)))
        assert ("src/b.py" in sortie.partition("HORS:")[2] and "M src/b.py" in reste), ("ENA4 : src/b.py dit HORS: et reste à commiter — le « **b** » de la prose n'est pas un motif (ENA5)") + "\n" + str(repr((sortie, reste)))
        assert ("scripts/sante-base.json" not in montre and "scripts/sante-base.json" in sortie.partition("HORS:")[2]
                 and "M scripts/sante-base.json" in reste), ("ENA4 : hors du kit, scripts/sante-base.json n'est pas un commun — HORS:, laissé hors du commit") + "\n" + str(repr((sortie, montre, reste)))
        assert ("scripts/sante-base.json" in montre_kit and "src/b.py" in montre_kit), ("ENA4 : dans le kit, scripts/sante-base.json est un commun — commité avec src/b.py") + "\n" + str(repr((kit, montre_kit)))


def test_lanceur_trie(tmp_path):
    """Lancer deux fois le vrai `vlp.py gardien` sur la même entrée, comme `python3` et `py` le font (VIT8) : le
    premier refuse le commit, le second sort 0, muet, sans importer `vlp_coeur` (`-X importtime`). `TMPDIR` neuf :
    le tampon y vit seul."""
    entree = json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash", "agent_type": "vlp:fiche",
                         "tool_input": {"command": "git commit -m 'VIT8 %f'" % time.time()}})
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        env = dict(os.environ, TMPDIR=t, PYTHONIOENCODING="utf-8")
        env.pop("VLP_SANS_TAMPON", None)
        r = [subprocess.run([sys.executable, "-X", "importtime", os.path.join(ICI, "vlp.py"), "gardien"], input=entree,
                            capture_output=True, text=True, encoding="utf-8", env=env) for _ in range(2)]
    assert ([x.returncode for x in r] == [0, 0] and "deny" in r[0].stdout and "vlp_coeur" in r[0].stderr
             and r[1].stdout == "" and "vlp_coeur" not in r[1].stderr), ("VIT8 : deux lanceurs, même entrée — le 1er refuse, le 2e sort muet sans charger le cœur") + "\n" + str("\n".join("code %d\n%s\n%s" % (x.returncode, x.stdout, x.stderr[-600:]) for x in r))


def test_iso6_parallele():
    """ISO6 : `/vlp:enchainer agents` lance en parallèle d'office — chaque fiche en worktree au rythme de `lancables`,
    puis `commiter` là-bas, `fusionner` ici, `etat` du bloc `ÉTAT:`, `CONFLIT` rejoué en fin ; `file`, le mode sans
    argument et `clear` restent ; le contrat dit `DOSSIER:` et `ÉTAT:`."""
    chef = io.open(os.path.join(RACINE, "skills", "enchainer", "SKILL.md"), encoding="utf-8").read()
    contrat = io.open(os.path.join(RACINE, "enchainement.md"), encoding="utf-8").read()
    indice = next((l for l in chef.splitlines() if l.startswith("argument-hint:")), "")
    debut, fin = chef.find("## 3. Jouer chaque fiche"), chef.find("## 3 bis.")
    trois = " ".join(chef[debut:fin].split()) if 0 <= debut < fin else ""
    attendus = ['isolation: "worktree"', 'lancables "<fichier de fiches courant>" --max <largeur> --tourne', "INDICE:",
                "DOSSIER:", 'fusionner "<fichier de fiches courant>" <fiche> --worktree "<dossier>"',
                'etat "<fichier d\'état>" --texte', "CONFLIT", 'postit "<dossier>" "<fichier de fiches courant>"']
    plat = " ".join(chef.split())
    assert ([a for a in attendus if a not in trois] == []), ("ISO6 : l'étape 3 lance en worktree par lancables, fusionne, écrit l'état et rejoue un CONFLIT") + "\n" + str([a for a in attendus if a not in trois])
    assert ("agents [<largeur>]" in indice and "agents file" in indice and "`agents file`" in plat
             and "**Sans argument (ou `main`) : aucun sous-agent.**" in plat and 'boucle.py" . --plafond' in plat
             and "Plafond : **5 fiches**" in plat), ("ISO6 : argument-hint dit la largeur et file ; main, clear et le plafond de 5 restent") + "\n" + str(indice)
    assert (all(m in contrat for m in ("DOSSIER: <chemin", "\nÉTAT:\n", "\n/ÉTAT\n"))), ("ISO6 : le contrat porte DOSSIER:, ÉTAT: et /ÉTAT") + "\n" + "enchainement.md"
