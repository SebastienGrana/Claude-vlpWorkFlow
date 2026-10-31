"""REF10 : `vlp.py figer`, le hook `PreToolUse` (`Write|Edit`) qui fige les tests existants pendant une fiche (choix
`Q2` : « Hiding tests from agents reduces cheating success rate to near zero », ImpossibleBench, note `122`).

Les décisions se testent en mémoire ; le hook entier, sur un projet, sa transcription et son dépôt Git bâtis dans un
dossier temporaire.
"""
import io
import json
import os
import subprocess

from aides import ecrire, mod

H = mod.noyau.hooks

FICHE = """<!-- FICHE:%s -->
## %s [%s] — fiche %s

**Dépend de** : rien.
**Fichiers** : `tests/test_a.py`.
%s
**Prompt**
Fais-la.

**Critère de fin**
Fait.
<!-- /FICHE -->

"""
DECLARE = "**Tests** : modifiés — le libellé suit la règle\n"
TEST_A = "def test_a():\n    assert 1 == 1\n"


def fiches(f1=" ", f2=" ", declare_f1=""):
    """Le fichier de fiches du projet : F1, puis F2 qui déclare ses tests modifiés."""
    return ("# Chantier F — fiches\n\n**Ouvert.** le 2026-10-31.\n\n## Le socle commun\n\nRien.\n\n"
            + FICHE % ("F1", "F1", f1, "une", declare_f1) + FICHE % ("F2", "F2", f2, "deux", DECLARE))


def invocation(args):
    """La ligne de transcription que laisse `/vlp:tache <args>` : le corps de la commande, injecté par Claude Code."""
    texte = ("Base directory for this skill: C:\\kit\\skills\\tache\n\nArguments reçus :\n\n%s\n\n"
             "Exécute **une** fiche du chantier courant." % args)
    return json.dumps({"type": "user", "isMeta": True,
                       "message": {"role": "user", "content": [{"type": "text", "text": texte}]}}, ensure_ascii=False)


def message(texte):
    """Une ligne de transcription : un message utilisateur en texte simple."""
    return json.dumps({"type": "user", "message": {"role": "user", "content": texte}}, ensure_ascii=False)


def git(t, *args):
    subprocess.run(["git", "-C", t, *args], check=True, capture_output=True)


def projet(tmp_path, init_git):
    """Le projet : CHANTIER.md, ses fiches, un test existant ; commité, le tout. Rend son dossier."""
    t = str(tmp_path / "p")
    ecrire(os.path.join(t, "CHANTIER.md"), "# Chantier courant\n\n- **contexte** : .\n")
    ecrire(os.path.join(t, "fiches.md"), fiches())
    ecrire(os.path.join(t, "tests", "test_a.py"), TEST_A)
    ecrire(os.path.join(t, "scripts", "outil.py"), "X = 1\n")
    init_git(t)
    git(t, "add", "-A")
    git(t, "commit", "-q", "-m", "init")
    return t


def figer(t, outil, entree, transcription, **plus):
    """Lancer `vlp.py figer` sur l'entrée d'un hook `PreToolUse` : rend (code, sortie, erreur)."""
    d = {"hook_event_name": "PreToolUse", "tool_name": outil, "tool_input": entree, "cwd": t,
         "transcript_path": transcription, "session_id": "s", **plus}
    o, e = io.StringIO(), io.StringIO()
    code = mod.main(["figer"], o, io.StringIO(json.dumps(d)), e)
    return code, o.getvalue(), e.getvalue()


def test_figer_decisions():
    """Les décisions du hook, en mémoire : quel fichier est un test, quelle fiche est en cours, ce qu'est un ajout pur,
    et la déclaration `**Tests**`."""
    assert H.est_test("tests/test_a.py") and H.est_test("tests/sous/x.py") and H.est_test("scripts/test-vlp.py"), (
        "figer : tests/** et scripts/test-*.py sont des tests")
    assert not H.est_test("scripts/vlp.py") and not H.est_test("tests.md") and not H.est_test("../tests/x.py"), (
        "figer : le reste n'en est pas")
    assert H.fiche_de_transcription([message("bonjour"), invocation("F1"), invocation("vlp F2")]) == "F2", (
        "figer : la dernière invocation de /vlp:tache, son dernier code de fiche")
    assert H.fiche_de_transcription([invocation("")]) == "", "figer : /vlp:tache sans fiche → la prochaine"
    assert H.fiche_de_transcription([message("Fiche à jouer : F1 — Kit : k"), invocation("F2")]) == "F1", (
        "figer : un sous-agent joue la fiche de son premier message")
    assert H.fiche_de_transcription([message("bonjour")]) is None, "figer : sans /vlp:tache, aucune fiche"
    lignes = fiches(f1="x").split("\n")
    assert (H.fiche_en_cours(lignes, "F1"), H.fiche_en_cours(lignes, "F2"), H.fiche_en_cours(lignes, "")) == (
        None, "F2", "F2"), "figer : une fiche cochée n'est plus en cours ; sans code, la première non cochée"
    assert H.tests_declares(lignes, "F2") and not H.tests_declares(lignes, "F1"), (
        "figer : la ligne **Tests** de la fiche, et d'elle seule")
    assert H.ajout_pur({"old_string": "a\n", "new_string": "a\nb\n"}), "figer : old_string entier dans new_string"
    assert not H.ajout_pur({"old_string": "a\n", "new_string": "c\n"}), "figer : une ligne changée n'est pas un ajout"
    assert not H.ajout_pur({"content": "a"}), "figer : un Write n'est pas un ajout pur"


def test_figer_hook(tmp_path, init_git):
    """Le hook entier : modifier un test pendant une fiche → refusé, sortie 2, raison lue ; ajout pur, test neuf, fiche
    qui déclare `**Tests**`, hors fiche → accepté."""
    t = projet(tmp_path, init_git)
    trans = str(tmp_path / "s.jsonl")
    ecrire(trans, invocation("F1") + "\n")
    a = os.path.join(t, "tests", "test_a.py")
    change = {"file_path": a, "old_string": "1 == 1", "new_string": "2 == 2"}

    code, o, e = figer(t, "Edit", change, trans)
    assert code == 2 and "F1" in e and "tests/test_a.py" in e and "**Tests** : modifiés" in e and o == "", (
        "figer : modifier une ligne de test pendant une fiche, refusé, sortie 2, raison lue\n" + e)
    code, _o, e = figer(t, "Write", {"file_path": a, "content": "x\n"}, trans)
    assert code == 2, "figer : réécrire un test existant pendant une fiche, refusé\n" + e
    assert figer(t, "Edit", {"file_path": a, "old_string": "1 == 1\n", "new_string": "1 == 1\n    assert 2\n"},
                 trans)[0] == 0, "figer : un ajout pur passe"
    assert figer(t, "Write", {"file_path": os.path.join(t, "tests", "test_b.py"), "content": "x\n"}, trans)[0] == 0, (
        "figer : un test neuf passe")
    assert figer(t, "Edit", {"file_path": os.path.join(t, "scripts", "outil.py"), "old_string": "X = 1",
                             "new_string": "X = 2"}, trans)[0] == 0, "figer : un fichier qui n'est pas un test passe"

    ecrire(os.path.join(t, "fiches.md"), fiches(declare_f1=DECLARE))
    assert figer(t, "Edit", change, trans)[0] == 2, (
        "figer : une déclaration écrite pendant la fiche, pas commitée, ne compte pas")
    ecrire(trans, invocation("F2") + "\n")
    assert figer(t, "Edit", change, trans)[0] == 0, "figer : la fiche qui déclare **Tests** (commitée) passe"

    ecrire(os.path.join(t, "fiches.md"), fiches(f1="x"))
    ecrire(trans, invocation("F1") + "\n")
    assert figer(t, "Edit", change, trans)[0] == 0, "figer : une fiche cochée n'est plus en cours, rien ne bloque"
    ecrire(trans, message("bonjour") + "\n")
    assert figer(t, "Edit", change, trans)[0] == 0, "figer : hors fiche, rien ne bloque"

    o, e = io.StringIO(), io.StringIO()
    assert (mod.main(["figer"], o, io.StringIO("pas du json"), e), o.getvalue(), e.getvalue()) == (0, "", ""), (
        "figer : une entrée illisible, muet")


def test_figer_cas_limites(tmp_path, init_git, monkeypatch):
    """Ce qui ne se lit pas laisse passer : ligne de transcription illisible ou pas d'un utilisateur, fiche absente,
    transcription absente, hors d'un projet équipé, autre disque, deux chantiers ouverts."""
    assert H.fiche_de_transcription(["pas du json", json.dumps({"message": {"role": "assistant", "content": "F1"}})]) \
        is None, "figer : une ligne illisible ou de l'assistant ne nomme aucune fiche"
    assert H.fiche_en_cours(fiches().split("\n"), "ZZ9") is None, "figer : une fiche absente n'est pas en cours"
    assert H.lignes_transcription({}) == [] and H.lignes_transcription(
        {"transcript_path": str(tmp_path / "absente.jsonl")}) == [], "figer : sans transcription lisible, rien"

    dehors = str(tmp_path / "dehors")
    ecrire(os.path.join(dehors, "tests", "test_a.py"), TEST_A)
    change = {"file_path": os.path.join(dehors, "tests", "test_a.py"), "old_string": "1 == 1", "new_string": "2 == 2"}
    assert H.cible_test({"tool_input": change, "cwd": dehors}) is None, "figer : hors d'un projet équipé, rien"

    t = projet(tmp_path, init_git)
    trans = str(tmp_path / "s.jsonl")
    ecrire(trans, invocation("F1") + "\n")
    change["file_path"] = os.path.join(t, "tests", "test_a.py")
    ecrire(os.path.join(t, "autres.md"), fiches())
    assert figer(t, "Edit", change, trans)[0] == 0, "figer : deux chantiers ouverts, aucun courant, rien ne bloque"

    def autre_disque(*_a):
        raise ValueError("path is on mount 'C:', start on mount 'D:'")
    monkeypatch.setattr(H.os.path, "relpath", autre_disque)
    assert H.cible_test({"tool_input": change, "cwd": t}) is None, "figer : un autre disque que le projet, rien"


def test_figer_sous_agent(tmp_path, init_git):
    """Un sous-agent : sa fiche se lit dans sa propre transcription, `subagents/agent-<id>.jsonl` à côté de celle de la
    session."""
    t = projet(tmp_path, init_git)
    trans = str(tmp_path / "s.jsonl")
    ecrire(trans, message("bonjour") + "\n")
    ecrire(str(tmp_path / "s" / "subagents" / "agent-a1.jsonl"), message("Fiche à jouer : F1 — Kit : k") + "\n")
    change = {"file_path": os.path.join(t, "tests", "test_a.py"), "old_string": "1 == 1", "new_string": "2 == 2"}
    assert figer(t, "Edit", change, trans, agent_id="a1", agent_type="vlp:fiche")[0] == 2, (
        "figer : le sous-agent qui joue F1 ne modifie pas un test existant")
