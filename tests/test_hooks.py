"""`noyau/hooks.py` : le filet, le gardien, le contrat, la forme du sous-agent, `hooks.json`. Deux étages : la décision
d'`ouverture` sans Git (REF47), sur le texte de `git log` ; puis les commandes, migrées de l'ancienne suite maison
(REF58), chaque `assert` migré au libellé d'origine de son `verifier` (REF5).
"""
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import time

import pytest
from aides import RACINE, appel, ecrire, lire, mod
from noyau import hooks

SANS = "aucun commit n'ajoute ce fichier : l'ouverture n'est pas commitée"


def test_heure_d_ajout_le_plus_ancien():
    assert hooks.heure_d_ajout(0, "300\n200\n100\n") == (100, None)


def test_heure_d_ajout_sans_commit_ou_en_echec():
    assert hooks.heure_d_ajout(0, "") == (None, SANS), "CHK1 : fichier jamais commité, GARDE"
    assert hooks.heure_d_ajout(128, "100\n") == (None, SANS)


CHANTIER = "# Chantier courant\n\n- **alias** : %s\n- **contexte** : %s\n"


AVEC = """# Chantier Y

## Le socle commun

Socle, ligne 1.

## L'ordre des fiches

---

<!-- FICHE:Y1 -->
## Y1 [x] — faite
**Session** : aaa
**Prompt**
```
---
## pas un titre
```
<!-- /FICHE -->

---

<!-- FICHE:Y2 -->
## Y2 [ ] — à faire
**Session** : bbb
**Session** : aaa
<!-- /FICHE -->
"""


T0 = 1790000000


def hook(texte):
    o, e = io.StringIO(), io.StringIO()
    code = mod.main(["hook"], o, io.StringIO(texte), e)
    return code, o.getvalue(), e.getvalue()


def test_hook_fiches(tmp_path):
    """Contrôler le hook d'écriture sur un fichier de fiches : JSON illisible, .md ordinaire, fiches valides ou non."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        def json_de(nom):
            return '{"tool_input": {"file_path": "%s"}, "cwd": "%s"}' % (nom, t.replace("\\", "/"))

        code, o, e = hook("pas du json")
        assert ((code, o, e) == (0, "", "")), ("hook : JSON illisible, muet") + "\n" + str(o + e)
        ecrire(os.path.join(t, "notes.md"), "# Notes\n\n```\n<!-- FICHE:D1 -->\n## Le socle commun\n```\n")
        code, o, e = hook(json_de("notes.md"))
        assert ((code, o, e) == (0, "", "")), ("hook : .md ordinaire (marqueur en bloc de code), muet") + "\n" + str(o + e)
        ecrire(os.path.join(t, "y.md"), AVEC.replace("\n**Prompt**\n```\n---\n## pas un titre\n```", "\n**Critère de fin**")
               .replace("**Session** : bbb", "**Critère de fin**"))
        code, o, e = hook(json_de("y.md"))
        assert (code == 0 and e == ""
                 and '"additionalContext": "VALIDE 2 fiches' in o and '"hookEventName": "PostToolUse"' in o), ("hook : fiches valides, bilan en JSON, sort 0") + "\n" + str(o + e)
        ecrire(os.path.join(t, "y.md"), lire(os.path.join(t, "y.md")).replace("<!-- /FICHE -->\n\n---", "\n---", 1))
        code, o, e = hook(json_de("y.md"))
        assert (code == 2 and o == "" and "marqueur" in e
                 and "INVALIDE" in e and e.endswith("Corrige ce fichier de fiches avant de continuer.\n")), ("hook : fermant manquant, sort 2 sur stderr") + "\n" + str(o + e)
        ecrire(os.path.join(t, "y.md"), AVEC.replace("## Le socle commun", "## Socle"))
        code, o, e = hook(json_de("y.md"))
        assert (code == 2 and "section absente : ## Le socle commun" in e), ("hook : titre de section reformulé, sort 2") + "\n" + str(o + e)


def test_filet(tmp_path):
    """Contrôler le filet : sous-agent ou non, un avertissement par tour (chantier TOU)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        def filet_test(json_obj):
            """Appelle vlp.py filet avec l'entrée JSON."""
            o, e = io.StringIO(), io.StringIO()
            code = mod.main(["filet"], o, io.StringIO(json.dumps(json_obj)), e)
            return code, o.getvalue(), e.getvalue()

        def creer_trans(chemin, tours):
            """Crée un transcript factice."""
            os.makedirs(os.path.dirname(chemin), exist_ok=True)
            with open(chemin, "w", encoding="utf-8") as f:
                for n in range(tours):
                    d = {"message": {"id": f"m{n}", "usage": {"input_tokens": 100, "output_tokens": 50}}}
                    f.write(json.dumps(d) + "\n")

        # Pas d'agent_id
        code, o, e = filet_test({"agent_type": "vlp:fiche"})
        assert ((code, o, e) == (0, "", "")), ("filet : pas agent_id, muet") + "\n" + str(o + e)

        # agent_type ne contient pas 'fiche'
        code, o, e = filet_test({"agent_type": "autre", "agent_id": "a1"})
        assert ((code, o, e) == (0, "", "")), ("filet : agent_type sans 'fiche', muet") + "\n" + str(o + e)

        # Transcript absent
        t_fwd = t.replace(os.sep, '/')
        code, o, e = filet_test({"agent_type": "vlp:fiche", "agent_id": "a1", "transcript_path": t_fwd + "/chef.jsonl"})
        assert ((code, o, e) == (0, "", "")), ("filet : transcript absent, muet") + "\n" + str(o + e)

        # 77 tours / 80 max = 3 restants → avertissement
        sub_path = os.path.join(t, "s", "subagents", "agent-a1.jsonl")
        creer_trans(sub_path, 77)
        code, o, e = filet_test({"agent_type": "vlp:fiche", "agent_id": "a1", "transcript_path": t_fwd + "/s.jsonl"})
        assert (code == 0 and '"additionalContext": "Attention : 3 tours restants' in o), ("filet : 3 tours restants, avertissement") + "\n" + str(o + e)

        # 76 tours = 4 restants → muet
        creer_trans(sub_path, 76)
        code, o, e = filet_test({"agent_type": "vlp:fiche", "agent_id": "a1", "transcript_path": t_fwd + "/s.jsonl"})
        assert (code == 0 and o == ""), ("filet : 4 tours restants, muet") + "\n" + str(o + e)

        # 78 tours = 2 restants → avertissement
        creer_trans(sub_path, 78)
        code, o, e = filet_test({"agent_type": "vlp:fiche", "agent_id": "a1", "transcript_path": t_fwd + "/s.jsonl"})
        assert (code == 0 and '"additionalContext": "Attention : 2 tours restants' in o), ("filet : 2 tours restants, avertissement") + "\n" + str(o + e)

        # Après un échec (PostToolUseFailure) : même avertissement, au nom de l'événement reçu
        creer_trans(sub_path, 77)
        code, o, e = filet_test({"hook_event_name": "PostToolUseFailure", "agent_type": "vlp:fiche",
                                 "agent_id": "a1", "transcript_path": t_fwd + "/s.jsonl"})
        assert (code == 0 and '"hookEventName": "PostToolUseFailure"' in o
                 and '"additionalContext": "Attention : 3 tours restants' in o), ("filet : après un échec, avertissement au nom de PostToolUseFailure") + "\n" + str(o + e)

        # TOU2 : une fois par tour — tampon `vlp-filet-<agent_id>-<tours>` dans un TAMPON_HOOKS neuf
        ancien_tampon = mod.etat.TAMPON_HOOKS
        mod.etat.TAMPON_HOOKS = tempfile.mkdtemp()
        try:
            def salve(*ids):
                """Un appel par id d'outil (entrées différentes) ; rend le nombre de sorties non vides."""
                return sum(bool(filet_test({"agent_type": "vlp:fiche", "agent_id": "a1", "tool_use_id": i,
                                            "transcript_path": t_fwd + "/s.jsonl"})[1]) for i in ids)
            creer_trans(sub_path, 77)
            assert (salve("u1", "u2") == 1), ("TOU2 : deux appels du même tour, une seule sortie") + "\n" + ""
            creer_trans(sub_path, 78)
            assert (salve("u3") == 1), ("TOU2 : un tour de plus, le filet avertit de nouveau") + "\n" + ""
            creer_trans(sub_path, 77)
            os.environ["VLP_SANS_TAMPON"] = "1"
            try:
                n = salve("u4", "u5")
            finally:
                del os.environ["VLP_SANS_TAMPON"]
            assert (n == 2), ("TOU2 : VLP_SANS_TAMPON, deux sorties") + "\n" + str(str(n))
        finally:
            shutil.rmtree(mod.etat.TAMPON_HOOKS, ignore_errors=True)
            mod.etat.TAMPON_HOOKS = ancien_tampon

        # Un vrai chemin de plus de 260 caractères, bâti comme dans FIL1 : sans le préfixe,
        # isfile et open y disent absent un transcript présent ; le filet doit avertir quand même
        if os.name != "nt":
            pytest.skip("hors Windows — le chemin long du filet n'est pas testé (le préfixe est propre à Windows)")
        else:
            prefixe = chr(92) * 2 + "?" + chr(92)    # le préfixe des chemins longs, bâti sans échappement
            long_base = os.path.join(os.path.abspath(t), "l" * (254 - len(os.path.abspath(t))))
            long_sub = os.path.join(long_base, "subagents", "agent-a1.jsonl")
            os.makedirs(prefixe + os.path.dirname(long_sub))
            with open(prefixe + long_sub, "w", encoding="utf-8") as f:
                for n in range(77):
                    f.write(json.dumps({"message": {"id": f"m{n}", "usage": {"input_tokens": 1}}}) + "\n")
            try:
                code, o, e = filet_test({"agent_type": "vlp:fiche", "agent_id": "a1",
                                         "transcript_path": long_base.replace(os.sep, "/") + ".jsonl"})
                assert (len(long_sub) > 260 and '"additionalContext": "Attention : 3 tours restants' in o), (f"filet : transcript à {len(long_sub)} caractères, avertissement") + "\n" + str(o + e)
            finally:    # même après un écart : sans le préfixe, le nettoyage du dossier temporaire échouerait
                shutil.rmtree(prefixe + long_base)


def test_contrat(tmp_path):
    """Contrôler `contrat` : témoins propre et sale, bilan, bornes ; un refusé compté en bloqué (ENQ1)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        def agent(id_, texte, commandes, type_="vlp:fiche"):
            chemin = os.path.join(t, "p", "sess", "subagents", f"agent-{id_}.jsonl")
            lignes = [{"message": {"role": "assistant", "content": [
                {"type": "tool_use", "name": outil, "input": {"command": c}}]}} for outil, c in commandes]
            lignes.append({"message": {"role": "assistant", "content": [{"type": "text", "text": texte}]}})
            ecrire(chemin, "".join(json.dumps(d, ensure_ascii=False) + "\n" for d in lignes))
            ecrire(chemin[:-len(".jsonl")] + ".meta.json", json.dumps({"agentType": type_}))
            return chemin

        ecrire(os.path.join(t, "p", "sess.jsonl"), json.dumps({"timestamp": "2026-09-24T10:00:00Z"}) + "\n")
        propre = agent("propre", "FAITE — X1 cochée.", [("Bash", 'py vlp.py cocher "f.md" X1'),
                                                         ("PowerShell", "git status; git log -1")])
        sale = agent("sale", "✅ X1 faite", [("Bash", 'git -C "C:/a b/proj" commit -m "X1 : fin"'),
                                            ("PowerShell", "git add -A"), ("Bash", "echo git")])
        code, s = appel(["contrat", propre, sale])
        assert ("propre vlp:fiche 2026-09-24T10:00:00Z FAITE git 0 bloqué 0\n" in s), ("contrat : témoin propre, aucun appel qui écrit dans Git") + "\n" + str(s)
        assert ("sale vlp:fiche 2026-09-24T10:00:00Z ✅ git 2 bloqué 0\n" in s), ("contrat : témoin sale, git -C … commit et git add comptés, sans tool_result : écrits") + "\n" + str(s)
        assert (code == 0 and s.endswith(
            "CONTRAT 2 sous-agents · 1 écrivent dans Git · 0 bloqués par le gardien · "
            "1 sans statut en tête · 0 interrompus\n")), ("contrat : bilan") + "\n" + str(s)
        code, s = appel(["contrat", propre, "--depuis", "2026-09-24T10:00:01+00:00"])
        assert (code == 0 and s == "CONTRAT 0 sous-agents · 0 écrivent dans Git · 0 bloqués par le gardien · "
                 "0 sans statut en tête · 0 interrompus\n"), ("contrat : --depuis écarte une session partie avant") + "\n" + str(s)
        code, s = appel(["contrat", "--depuis", "pas-une-borne-zz"])
        assert (code == 1 and s.startswith("GARDE: --depuis pas-une-borne-zz")), ("contrat : borne illisible, GARDE") + "\n" + str(s)


    # ENQ1 : un appel refusé par le gardien compte en bloqué, pas en écrit ; un interrompu pas en sans-statut
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        def ligne_agent(id_, blocs):
            chemin = os.path.join(t, "p2", "sess", "subagents", f"agent-{id_}.jsonl")
            ecrire(chemin, "".join(json.dumps(d, ensure_ascii=False) + "\n" for d in blocs))
            ecrire(chemin[:-len(".jsonl")] + ".meta.json", json.dumps({"agentType": "vlp:fiche"}))
            return chemin

        ecrire(os.path.join(t, "p2", "sess.jsonl"), json.dumps({"timestamp": "2026-09-24T10:00:00Z"}) + "\n")
        refusee = ligne_agent("refusee", [
            {"message": {"role": "assistant", "content": [
                {"type": "tool_use", "id": "tu1", "name": "Bash", "input": {"command": "git add -A"}}]}},
            {"message": {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": "tu1", "content": mod.REFUS_GIT}]}},
            {"message": {"role": "assistant", "content": [{"type": "text", "text": "RETOUR — bloquée par le gardien."}]}}])
        ecrit = ligne_agent("ecrit", [
            {"message": {"role": "assistant", "content": [
                {"type": "tool_use", "id": "tu2", "name": "Bash", "input": {"command": "git add -A"}}]}},
            {"message": {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": "tu2", "content": "add 'f.md'"}]}},
            {"message": {"role": "assistant", "content": [{"type": "text", "text": "FAITE — X1 cochée."}]}}])
        avant = ligne_agent("avant", [
            {"message": {"role": "assistant", "content": [
                {"type": "tool_use", "id": "tu3", "name": "Bash", "input": {"command": "git commit -m x"}}]}},
            {"message": {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": "tu3", "content": mod.REFUS_GIT_AVANT}]}},
            {"message": {"role": "assistant", "content": [{"type": "text", "text": "RETOUR — bloquée."}]}}])
        interrompue = ligne_agent("interrompue", [
            {"message": {"role": "assistant", "content": [{"type": "text", "text": "Je lance le dernier essai…"}]}},
            {"message": {"role": "user", "content": "[Request interrupted by user]"}}])
        code, s = appel(["contrat", refusee, ecrit, avant, interrompue])
        assert (code == 0 and s.endswith("CONTRAT 4 sous-agents · 1 écrivent dans Git · 2 bloqués par le gardien · "
                                           "0 sans statut en tête · 1 interrompus\n")), ("ENQ1 : bilan — refusé compté en bloqué (phrase d'avant VRB comprise), interrompu pas en "
                 "sans-statut — mutant : compter un refus comme une écriture, ou oublier REFUS_GIT_AVANT, le fait tomber") + "\n" + str(s)
        assert ("refusee vlp:fiche 2026-09-24T10:00:00Z RETOUR git 0 bloqué 1\n" in s), ("ENQ1 : la ligne du refusé porte git 0 bloqué 1") + "\n" + str(s)
        assert ("interrompue vlp:fiche 2026-09-24T10:00:00Z (interrompu) git 0 bloqué 0\n" in s), ("ENQ1 : la ligne de l'interrompu porte (interrompu)") + "\n" + str(s)


def test_gardien(tmp_path, init_git):
    """Contrôler le gardien : ce qu'il refuse et laisse passer, entrées illisibles."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        def gardien(d):
            o = io.StringIO()
            code = mod.main(["gardien"], o, io.StringIO(d if isinstance(d, str) else json.dumps(d)))
            return code, o.getvalue()

        fiche = {"agent_id": "a1", "agent_type": "vlp:fiche"}
        relecture = {"agent_id": "a2", "agent_type": "vlp:relecture"}
        commit = {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                  "tool_input": {"command": 'git -C "C:/a b" commit -m "X1 : fin"'}}
        code, s = gardien(dict(commit, **relecture))
        assert (code == 0 and '"permissionDecision": "deny"' in s and "vlp:relecture" in s), ("gardien : sous-agent vlp:relecture git commit refusé") + "\n" + str(s)
        code, s = gardien(dict(fiche, **commit))
        assert (code == 0 and '"permissionDecision": "deny"' in s and "vlp:fiche" in s), ("gardien : git -C … commit refusé pour vlp:fiche") + "\n" + str(s)
        code, s = gardien(dict(relecture, hook_event_name="PreToolUse", tool_name="Bash",
                               tool_input={"command": "git diff HEAD~1"}))
        assert ((code, s) == (0, "")), ("gardien : relecteur git diff laissé passer") + "\n" + str(s)
        code, s = gardien(dict(fiche, hook_event_name="PreToolUse", tool_name="PowerShell",
                               tool_input={"command": "git status; git log -1"}))
        assert ((code, s) == (0, "")), ("gardien : fiche git status laissé passer") + "\n" + str(s)
        assert (gardien("pas du json") == (0, "")), ("gardien : entrée illisible, muet") + "\n" + ""
        assert (gardien('[43, "sonde"]') == (0, "") and gardien('"x"') == (0, "")), ("gardien : JSON qui n'est pas un objet, muet") + "\n" + ""
        assert (all(
            gardien(dict(agent, hook_event_name="PreToolUse", tool_name="Bash", tool_input=ti)) == (0, "")
            for agent in (fiche, relecture) for ti in ("git commit", ["git commit"], 7)) and gardien(dict(
                commit, agent_id="a3", agent_type=["vlp:relecture"])) == (0, "")), ("gardien : tool_input ou agent_type qui ne sont pas ce qu'on attend, muet") + "\n" + ""

        proj = os.path.join(t, "proj")
        ecrire(os.path.join(proj, "CHANTIER.md"), CHANTIER % ("px", "."))
        ecrire(os.path.join(proj, "f.md"), "# Chantier X\n\n**Ouvert.** le 2026-10-08.\n\n<!-- FICHE:X1 -->\n## X1 [ ] — une\n<!-- /FICHE -->\n")
        trans = os.path.join(t, "agent-a1.jsonl")
        ecrire(trans, json.dumps({"message": {"role": "user", "content": "Fiche à jouer :\n\nX1\n\nKit : k"}},
                                 ensure_ascii=False) + "\n")
        fin = dict(fiche, hook_event_name="SubagentStop", stop_hook_active=False, cwd=proj,
                   agent_transcript_path=trans)
        code, s = gardien(dict(fin, last_assistant_message="Parfait, la fiche est faite."))
        assert ('"decision": "block"' in s and "« Parfait, »" in s), ("gardien : statut absent, renvoyé") + "\n" + str(s)
        code, s = gardien(dict(fin, last_assistant_message="Parfait.", stop_hook_active=True))
        assert ((code, s) == (0, "")), ("gardien : déjà renvoyé une fois, laissé") + "\n" + str(s)
        code, s = gardien(dict(fin, last_assistant_message="FAITE — X1.", stop_hook_active=True))
        assert ('"decision": "block"' in s and "case de X1 est vide" in s), ("gardien : FAITE sur case vide sous stop_hook_active, renvoyé") + "\n" + str(s)
        code, s = gardien(dict(fin, last_assistant_message="FAITE — X1."))
        assert ('"decision": "block"' in s and "case de X1 est vide" in s), ("gardien : FAITE sur case vide, renvoyé") + "\n" + str(s)
        ecrire(os.path.join(proj, "f.md"), "# Chantier X\n\n**Ouvert.** le 2026-10-08.\n\n<!-- FICHE:X1 -->\n## X1 [x] — une\n<!-- /FICHE -->\n")
        if not shutil.which("git"):
            pytest.skip("git absent — le gardien sur HEAD n'est pas testé")
        else:
            env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                       GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
            ecrire(env["GIT_CONFIG_GLOBAL"], "")
            init_git(proj)
            for args in (["add", "-A"], ["commit", "-q", "-m", "départ"]):
                subprocess.run(["git"] + args, cwd=proj, env=env, check=True, capture_output=True)
            code, s = gardien(dict(fin, last_assistant_message="FAITE — X1."))
            assert ((code, s) == (0, "")), ("gardien : FAITE sur case cochée, sans commit de fiche, laissé") + "\n" + str(s)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", "X1 : une"], cwd=proj, env=env, check=True)
            code, s = gardien(dict(fin, last_assistant_message="FAITE — X1."))
            assert ('"decision": "block"' in s and "tu as commité" in s), ("gardien : HEAD nomme la fiche, renvoyé") + "\n" + str(s)
        fin_relecture = dict(relecture, hook_event_name="SubagentStop", stop_hook_active=False, cwd=proj,
                             agent_transcript_path=trans)
        code, s = gardien(dict(fin_relecture, last_assistant_message="ACCEPTÉE — tout va bien"))
        assert ((code, s) == (0, "")), ("gardien : relecteur ACCEPTÉE muet") + "\n" + str(s)
        code, s = gardien(dict(fin_relecture, last_assistant_message="REFUSÉE — erreur"))
        assert ((code, s) == (0, "")), ("gardien : relecteur REFUSÉE muet") + "\n" + str(s)
        code, s = gardien(dict(fin, last_assistant_message="RETOUR — x\n\n---\n✅ Tout va bien"))
        assert ('"decision": "block"' in s and "« En résumé » ou une jauge" in s), ("gardien : fiche jauge « Tout va bien », renvoyée") + "\n" + str(s)
        code, s = gardien(dict(fin, last_assistant_message="RETOUR — x\n\n---\n✅ Tout va bien", stop_hook_active=True))
        assert ((code, s) == (0, "")), ("gardien : fiche jauge sous stop_hook_active, muet") + "\n" + str(s)
        code, s = gardien(dict(fin_relecture, last_assistant_message="ACCEPTÉE — ok\nEn résumé : y"))
        assert ('"decision": "block"' in s and "« En résumé » ou une jauge" in s), ("gardien : relecteur « En résumé », renvoyé") + "\n" + str(s)
        code, s = gardien(dict(fin_relecture, last_assistant_message="ACCEPTÉE — ok"))
        assert ((code, s) == (0, "")), ("gardien : relecteur sans « En résumé » ni jauge, muet") + "\n" + str(s)
        # JUG2 : la pièce de JUG1 se lit au journal, jamais recopiée ici (elle porte des chemins de machine)
        with open(os.path.join(RACINE, "context AI", "08-etat.md"), encoding="utf-8") as f:
            piece = re.search(r"La pièce, pour `JUG2` :\n\n```text\n(.*?)\n```", f.read(), re.S)
        piece = piece.group(1) if piece else ""
        code, s = gardien(dict(fin_relecture, last_assistant_message=piece))
        assert (piece.startswith("ACCEPTÉE") and "« Tout va bien »" in piece and (code, s) == (0, "")), ("gardien : relecteur de FOR3 qui cite la jauge en prose (JUG1), muet") + "\n" + str(s or piece[:80])
        code, s = gardien(dict(fin_relecture, last_assistant_message=(
            "ACCEPTÉE — ok\n\n✅ **Tout va bien** — relu\n\n**En résumé**\n\nLa fiche tient.")))
        assert ('"decision": "block"' in s and "« En résumé » ou une jauge" in s), ("gardien : relecteur ACCEPTÉE puis résumé à part, renvoyé") + "\n" + str(s)
        # Mutation test : les tests « renvoyé » reposent sur forme_texte (chantier FOR3)
        code, s = gardien(dict(fin, last_assistant_message="RETOUR — Pas bonne action"))
        assert ((code, s) == (0, "")), ("gardien : fiche « Pas bonne » (pas jauge), muet — substring bug") + "\n" + str(s)
        code, s = gardien(dict(fin, last_assistant_message="RETOUR — Grosse bonne nouvelle"))
        assert ((code, s) == (0, "")), ("gardien : fiche « Grosse bonne » (pas jauge), muet — substring bug") + "\n" + str(s)


def paire(groupe, *sous):
    """Les deux commandes d'un groupe : python3 puis `py -3` (sans `-3`, `py` lit le `#!` et relance le
    `python3` du PATH, +77 ms, VIT8), sur `vlp.py <sous>`."""
    return [(h.get("type"), h.get("command"), h.get("args")) for h in groupe.get("hooks", [])] == [
        ("command", c, [*option, "${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py", *sous])
        for c, option in (("python3", []), ("py", ["-3"]))]


# hooks.json : le filet sur tout outil, après un succès et après un échec ; hook sur les écritures
with open(os.path.join(RACINE, "hooks", "hooks.json"), encoding="utf-8") as f:
    crochets = json.load(f)["hooks"]


def test_hooks_json():
    """Contrôler hooks.json : filet, hook d'écriture, attente, gardien et vigile."""
    succes, echec = crochets.get("PostToolUse", []), crochets.get("PostToolUseFailure", [])
    assert (len(succes) == 3 and len(echec) == 2
             and any(g.get("matcher") == "*" and paire(g, "filet") for g in succes)
             and any(g.get("matcher") == "Write|Edit" and paire(g, "hook") for g in succes)
             and echec[0].get("matcher") == "*" and paire(echec[0], "filet")), ("hooks.json : filet sur tout outil après un succès et après un échec, hook sur Write|Edit") + "\n" + str(json.dumps(crochets, ensure_ascii=False))
    assert (any(g.get("matcher") == "Artifact" and paire(g, "attente", "hook") for g in succes)
             and echec[1].get("matcher") == "Artifact" and paire(echec[1], "attente", "hook")), ("hooks.json : attente sur Artifact après un succès et après un échec (chantier LOC)") + "\n" + str(json.dumps(crochets, ensure_ascii=False))
    avant, arret = crochets.get("PreToolUse", []), crochets.get("SubagentStop", [])
    assert (len(avant) == 2 and avant[0].get("matcher") == "Bash|PowerShell" and paire(avant[0], "gardien")
             and len(arret) == 1 and arret[0].get("matcher") == "*" and paire(arret[0], "gardien")), ("hooks.json : gardien avant Bash|PowerShell et à l'arrêt d'un sous-agent") + "\n" + str(json.dumps(crochets, ensure_ascii=False))
    assert (avant[1].get("matcher") == "Artifact" and paire(avant[1], "vigile")), ("hooks.json : vigile avant Artifact (chantier VID)") + "\n" + str(json.dumps(crochets, ensure_ascii=False))


def test_forme_transcriptions(tmp_path):
    """Contrôler `forme` sur deux transcriptions (GLO1)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        sa = os.path.join(t, "sa.jsonl")
        sb = os.path.join(t, "sb.jsonl")
        # Transcription 1 : User de 100 caractères + "FAITE — … En résumé … Tout va bien"
        with open(sa, "w", encoding="utf-8") as f:
            # le format réel : une entrée de premier niveau, pas un champ de `message`
            f.write(json.dumps({"type": "attachment", "attachment": {
                "type": "instructions", "files": [{
                    "type": "User", "path": "user.md", "content": "x" * 100
                }]
            }}) + "\n")
            f.write(json.dumps({"type": "assistant", "requestId": "r2", "message": {
                "role": "assistant", "content": [{
                    "type": "text", "text": "FAITE — début En résumé détails Tout va bien fin"
                }]
            }}) + "\n")
        # Transcription 2 : sans attachements + "Parfait"
        with open(sb, "w", encoding="utf-8") as f:
            f.write(json.dumps({"type": "assistant", "requestId": "r1", "message": {
                "role": "assistant", "content": [{
                    "type": "text", "text": "Parfait"
                }]
            }}) + "\n")
        # Créer les .meta.json
        meta_a = sa[:-len(".jsonl")] + ".meta.json"
        meta_b = sb[:-len(".jsonl")] + ".meta.json"
        ecrire(meta_a, json.dumps({"agentType": "vlp:fiche"}))
        ecrire(meta_b, json.dumps({"agentType": "vlp:relecture"}))
        # Créer la structure de répertoires pour que le motif glob trouve les fichiers
        proj_dir = os.path.join(t, "projects", "test", "test", "subagents")
        os.makedirs(proj_dir)
        shutil.move(sa, os.path.join(proj_dir, "agent-id1.jsonl"))
        shutil.move(sb, os.path.join(proj_dir, "agent-id2.jsonl"))
        shutil.move(meta_a, os.path.join(proj_dir, "agent-id1.meta.json"))
        shutil.move(meta_b, os.path.join(proj_dir, "agent-id2.meta.json"))
        sa = os.path.join(proj_dir, "agent-id1.jsonl")
        sb = os.path.join(proj_dir, "agent-id2.jsonl")
        # Appel direct (pas par glob)
        code, s = appel(["forme", "--regle", "tout", sa, sb])     # le texte entier : la mesure d'avant JUG2
        lignes = s.strip().split("\n")
        assert (code == 0
                 and len(lignes) == 3  # deux lignes de données + une ligne de bilan
                 and lignes[2].startswith("FORME 2 sous-agents · user 50 car. · resume 1 · jauge 1 · tete 1")), ("forme : deux transcriptions, bilan attendu") + "\n" + str(s)


def test_forme_texte():
    """Contrôler que `forme_texte` ne juge que la fin du texte (JUG1)."""
    cite = "FAITE — la fiche cite « En résumé » et « Pas bon » en milieu de phrase."
    assert (mod.forme_texte(cite, "tete") == (0, 0)), ("forme_texte tete : une citation en milieu de phrase ne compte pas") + "\n" + str(mod.forme_texte(cite, "tete"))
    a_part = "✅ **Tout va bien** — fait\n\n**En résumé**\n\nLa fiche est faite."
    assert (mod.forme_texte(a_part, "tete") == (1, 1)), ("forme_texte tete : le résumé à part, jauge en tête") + "\n" + str(mod.forme_texte(a_part, "tete"))
    assert (mod.forme_texte("x\n---\n✅ Tout va bien", "tiret") == (0, 1)), ("forme_texte tiret : seul l'après-dernier --- est jugé") + "\n" + str(mod.forme_texte("x\n---\n✅ Tout va bien", "tiret"))


def test_forme_depuis(tmp_path):
    """Contrôler que `forme --depuis` filtre sur le départ du sous-agent (FOR1)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        # Créer la structure de répertoires pour que le motif glob trouve les fichiers
        proj_dir = os.path.join(t, "projects", "test", "test", "subagents")
        os.makedirs(proj_dir)
        # Transcription de sous-agent avec timestamp 2026-09-25T12:00:00Z
        sc = os.path.join(proj_dir, "agent-for1.jsonl")
        with open(sc, "w", encoding="utf-8") as f:
            f.write(json.dumps({"type": "attachment", "timestamp": "2026-09-25T12:00:00Z", "attachment": {
                "type": "instructions", "files": [{
                    "type": "User", "path": "user.md", "content": "test"
                }]
            }}) + "\n")
            f.write(json.dumps({"type": "assistant", "requestId": "r1", "message": {
                "role": "assistant", "content": [{
                    "type": "text", "text": "FAITE — test En résumé test Tout va bien"
                }]
            }}) + "\n")
        # Créer le .meta.json
        meta_c = sc[:-len(".jsonl")] + ".meta.json"
        ecrire(meta_c, json.dumps({"agentType": "vlp:fiche"}))
        # Parent session avec timestamp 2026-09-25T08:00:00Z (antérieur à --depuis 10:00:00Z)
        parent_session = os.path.join(t, "session.jsonl")
        with open(parent_session, "w", encoding="utf-8") as f:
            f.write(json.dumps({"type": "session", "timestamp": "2026-09-25T08:00:00Z"}) + "\n")
        # Appel avec --depuis après le timestamp du sous-agent mais avant celui de la parent session
        code, s = appel(["forme", "--depuis", "2026-09-25T10:00:00Z", sc])
        assert (code == 0
                 and "FORME 1 sous-agents" in s), ("forme --depuis filtre sur le départ du sous-agent") + "\n" + str(s)


def test_heredoc():
    """ECH1 : le corps d'un heredoc reçu par cat ou tee est une donnée ; le reste est lu.
    ENQ2 : pareil pour le texte cité d'un echo/printf envoyé dans un fichier."""
    def refuse(commande):
        o = io.StringIO()
        mod.main(["gardien"], o, io.StringIO(json.dumps({
            "agent_id": "a1", "agent_type": "vlp:fiche", "hook_event_name": "PreToolUse",
            "tool_name": "Bash", "tool_input": {"command": commande}})))
        return '"permissionDecision": "deny"' in o.getvalue()
    cas = [("cat > f <<'EOF'\ngit commit\nEOF", False),
           ("tee f <<EOF\ngit add x\nEOF", False),
           ("PYTHONUTF8=1 cat >> \"a b.md\" <<-\"FIN\"\n\tgit reset\n\tFIN\necho ok", False),
           ("py - <<'EOF'\nimport os; os.system('git commit -m x')\nEOF", True),
           ("cat <<'EOF' | bash\ngit commit\nEOF", True),
           ("bash -c \"$(cat <<'EOF'\ngit commit\nEOF\n)\"", True),
           ("cat > f <<'EOF'\nx\nEOF\ngit commit -m y", True),
           ("cat > f <<'EOF'\ngit commit", True),
           ("ssh h 'git reset --hard'", True),
           # ENQ2 : echo/printf tu vers un fichier, refusé si pipé ou si git suit ailleurs
           ('echo \'{"command":"git add ."}\' > f', False),
           ("printf '%s' 'git commit' >> f", False),
           ('echo "git add ." | sh', True),
           ("echo x > f; git add f", True),
           # dette VRB : echo à l'écran muet, "$(…)" lu, pipe ou && lu
           ('echo "git dans APRÈS: $?"; sh x', False), ('echo "git stash"', False),
           ('echo "$(git stash)"', True), ('echo "$(git stash)" > f', True),
           ('echo "a" && git stash', True), ('printf "git push\\n" | sh', True)]
    faux = [(c, attendu) for c, attendu in cas if refuse(c) != attendu]
    assert (not faux), ("ECH1/ENQ2 : heredoc de cat/tee et echo/printf vers un fichier muets, le reste refusé "
             "(%d cas) — mutant : rien retiré" % len(cas)) + "\n" + str(repr(faux))
    assert (mod.ecrit_git("cat > f <<'EOF'\ngit commit\nEOF") is False
             and mod.ecrit_git("git -C x commit -m y") is True), ("ECH1 : lire_contrat ne compte pas le heredoc de cat") + "\n" + ""
    assert (mod.ecrit_git('echo \'{"command":"git add ."}\' > f') is False
             and mod.ecrit_git("printf '%s' 'git commit' >> f") is False
             and mod.ecrit_git('echo "git add ." | sh') is True
             and mod.ecrit_git("ssh h 'git reset --hard'") is True), ("ENQ2 : lire_contrat ne compte pas le texte cité d'un echo/printf vers un fichier — "
             "mutant : retirer sans_echo fait tomber les deux « faux »") + "\n" + ""
    ecrit = ["git checkout f.py", "git checkout main", "git switch x", "git stash", "git -C x stash",
             "git restore f", "git clean -fd", "git push", "git rebase main", "git merge x",
             "cd x && git stash", "& git.exe push", "PYTHONUTF8=1 git commit -m x", "git --bare add x",
             '"C:/Program Files/Git/cmd/git.exe" push', "x=$(git stash)"]
    lit = ["git diff --cached", "git status", "git --no-pager log -1", "git show HEAD:f",
           "git rev-parse --show-toplevel", "git ls-files", "git -C x log", "grep -c git f",
           "ls .git", "echo git", "cd /c/git && ls", "git", "gitk --all", "py x.py # git stash"]
    faux = ([c for c in ecrit if not mod.ecrit_git(c)] + [c for c in lit if mod.ecrit_git(c)]
            + [c for c in ecrit + lit if refuse(c) != mod.ecrit_git(c)])
    assert (not faux), ("VRB1 : liste blanche — %d écritures refusées, %d lectures ou non-appels passent, "
             "gardien et contrat d'accord — mutants : `stash` dans LECTURE_GIT, ancrage retiré"
             % (len(ecrit), len(lit))) + "\n" + str(repr(faux))


def test_forme_jauge():
    """OUV1 : une ligne n'est une jauge que si elle en a la forme — émoji en tête, ou le mot
    suivi de —, … ou de la fin de ligne."""
    def renvoye(message):
        o = io.StringIO()
        mod.main(["gardien"], o, io.StringIO(json.dumps({
            "agent_id": "a2", "agent_type": "vlp:relecture", "hook_event_name": "SubagentStop",
            "last_assistant_message": message})))
        return '"decision": "block"' in o.getvalue()
    cas = [("REFUSÉE\n- Imprévu : j'ai dû relancer", False),
           ("ACCEPTÉE\nPas bonne idée de relancer", False),
           ("ACCEPTÉE\n⚠️ **Imprévu** : x", True),
           ("ACCEPTÉE\nÇa tient, mais…", True),
           ("ACCEPTÉE\nPas bon — y", True),
           ("ACCEPTÉE\n**Tout va bien.**", True),
           ("ACCEPTÉE\nGrosse erreur", True)]
    faux = [(m, attendu) for m, attendu in cas if renvoye(m) != attendu]
    assert (not faux), ("OUV1 : puce « Imprévu : » muette, vraies jauges renvoyées (%d cas) — mutant : forme ignorée"
             % len(cas)) + "\n" + str(repr(faux))


def test_contrat_ouverture(tmp_path, init_git):
    # CHK1 : --ouverture garde les sous-agents partis depuis l'ajout du fichier de fiches — leur heure à
    # eux : la session parente, partie avant, ne les écarte pas.
    if not shutil.which("git"):
        pytest.skip("git absent — contrat --ouverture n'est pas testé")
        return

    def iso(s):
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(T0 + s))

    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        depot = os.path.join(t, "depot")
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        ecrire(env["GIT_CONFIG_GLOBAL"], "")

        def git(quand, *args):
            date = "@%d +0000" % (T0 + quand)
            subprocess.run(["git"] + list(args), cwd=depot, capture_output=True, check=True,
                           env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))

        ecrire(os.path.join(depot, "a.md"), "a\n")
        init_git(depot)
        git(0, "add", "a.md")
        git(0, "commit", "-q", "-m", "TODO : Q ajouté")
        q = os.path.join(depot, "q.md")
        ecrire(q, "# Chantier Q\n")
        git(1000, "add", "q.md")
        git(1000, "commit", "-q", "-m", "Chantier Q ouvert")
        ecrire(os.path.join(t, "p", "sess.jsonl"), json.dumps({"timestamp": iso(200)}) + "\n")

        def agent(id_, quand):
            chemin = os.path.join(t, "p", "sess", "subagents", "agent-%s.jsonl" % id_)
            ecrire(chemin, json.dumps({"timestamp": iso(quand), "message": {"role": "assistant", "content": [
                {"type": "text", "text": "FAITE — Q1 cochée."}]}}, ensure_ascii=False) + "\n")
            ecrire(chemin[:-len(".jsonl")] + ".meta.json", json.dumps({"agentType": "vlp:fiche"}))
            return chemin

        avant, apres = agent("avant", 500), agent("apres", 1500)
        code, s = appel(["contrat", avant, apres, "--ouverture", q])
        assert (code == 0
                 and s == "DEPUIS %s · ouverture de %s\napres vlp:fiche %s FAITE git 0 bloqué 0\n"
                 "CONTRAT 1 sous-agents · 0 écrivent dans Git · 0 bloqués par le gardien · "
                 "0 sans statut en tête · 0 interrompus\n" % (iso(1000), q, iso(200))), ("CHK1 : --ouverture garde le sous-agent parti après, session parente partie avant") + "\n" + str(s)
        r = os.path.join(depot, "r.md")
        ecrire(r, "r\n")
        code, s = appel(["contrat", avant, "--ouverture", r])
        assert (code == 1 and s == "GARDE: --ouverture %s : aucun commit "
                 "n'ajoute ce fichier : l'ouverture n'est pas commitée\n" % r), ("CHK1 : fichier jamais commité, GARDE") + "\n" + str(s)
