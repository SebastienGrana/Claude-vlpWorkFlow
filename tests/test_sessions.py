"""`noyau/sessions.py` : le coût d'une session et d'un chantier (`cout`), les essais `claude -p` comptés à leur fiche,
la découpe aux commits, le compteur d'une boucle — migré de l'ancienne suite maison (REF58). Chaque `assert` garde le
libellé d'origine de son `verifier` en tête de son message (REF5), puis le diagnostic.
"""
import datetime
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from decimal import Decimal

import pytest
from aides import appel, ecrire, lire, mod, transcript

OUVERT = "**Ouvert.** le 2026-10-08."


def ouvert(texte):
    """`texte` d'un fichier de fiches, la marque d'ouverture sous son titre `# Chantier `, comme la pose `vlp.py
    ouvrir` : `courant_de` le lit (NUI31)."""
    return re.sub(r"^(# Chantier [^\n]*\n)", r"\g<1>\n%s\n" % OUVERT, texte, count=1, flags=re.M)


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


SANS = "## Z1 [ ] — ancien\nlong\n---\n## Z2 [ ] — dernier\nfin\n"


def transcript_marque(chemin, marque, heures):
    """`transcript`, précédé d'une ligne `user` à la marque `turnOrigin` donnée (aucune si None), à la première heure (ESH)."""
    transcript(chemin, len(heures), heures)
    if marque:
        iso = datetime.datetime.fromtimestamp(heures[0], datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        with open(chemin, encoding="utf-8") as f:
            suite = f.read()
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(json.dumps({"type": "user", "turnOrigin": marque, "timestamp": iso,
                                "message": {"role": "user", "content": "x"}}) + "\n" + suite)


QFICHES = """# Chantier Q

## Le socle commun

## L'ordre des fiches

<!-- FICHE:Q1 -->
## Q1 [x] — Créer
**Session** : %s
**Critère de fin**
<!-- /FICHE -->
<!-- FICHE:Q2 -->
## Q2 [x] — Brancher
**Session** : %s
**Critère de fin**
<!-- /FICHE -->
"""


T0 = 1790000000


DECOUPE_TETE = ("DÉCOUPE aux commits de fiche — une fiche va du commit d'avant au sien, "
                "un sous-agent compte à la fiche que nomme son prompt, sinon à son départ\n")


def test_cout_sous_agent_nomme(tmp_path, init_git):
    """CPF1 : trois sous-agents partent pendant Q1 ; deux nomment Q2 (jouer, relire) et lui comptent en
    entier, le troisième ne nomme rien et reste à son départ, à Q1 ; le total ne change pas."""
    if not shutil.which("git"):
        pytest.skip("git absent — le sous-agent nommé n'est pas testé")
        return
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        sq = os.path.join(t, "s.jsonl")
        transcript(sq, 4, [T0 + d for d in (50, 200, 400, 700)])
        os.makedirs(os.path.join(t, "s", "subagents"))
        for nom, prompt, heures in (("a1", "Fiche à jouer : Q2 — Kit : k", [250, 260]),
                                    ("a2", "Fiche à relire, et le commit s'il y en a un :\nQ2 abc1234", [270]),
                                    ("a3", "Lis ceci", [280])):
            chemin = os.path.join(t, "s", "subagents", "agent-%s.jsonl" % nom)
            transcript(chemin, len(heures), [T0 + h for h in heures])
            iso = datetime.datetime.fromtimestamp(T0 + heures[0], datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            suite = lire(chemin)
            ecrire(chemin, json.dumps({"type": "user", "timestamp": iso,
                                       "message": {"role": "user", "content": prompt}}) + "\n" + suite)
        a2 = os.path.join(t, "s", "subagents", "agent-a2.jsonl")
        assert ((mod.fiche_jouee(a2), mod.fiche_jouee(a2, mod.FICHE_NOMMEE)) == (None, "Q2")), ("CPF1 : le filet ne lit que « Fiche à jouer », cout lit aussi « Fiche à relire »") + "\n" + str((mod.fiche_jouee(a2), mod.fiche_jouee(a2, mod.FICHE_NOMMEE)))
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        ecrire(env["GIT_CONFIG_GLOBAL"], "")
        depot = os.path.join(t, "d")
        os.makedirs(depot)
        init_git(depot)
        for d, sujet in ((100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"), (600, "Q2 : Brancher"),
                         (800, "Chantier Q clos : fini")):
            date = "%d +0000" % (T0 + d)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=depot, check=True,
                           capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
        ecrire(os.path.join(depot, "q.md"), QFICHES % (sq, sq))
        code, s = appel(["cout", os.path.join(depot, "q.md")])
        cent, deux = "≈100,0k (100 000) · 1 tours · 0,50 $", "≈200,0k (200 000) · 2 tours · 1,00 $"
        assert (code == 0
                 and s.startswith(DECOUPE_TETE)
                 and "\nQ1 · %s = session %s + 1 sous-agent %s\n" % (deux, cent, cent) in s
                 and "\nQ2 · ≈400,0k (400 000) · 4 tours · 2,00 $ = session %s + 2 sous-agents "
                     "≈300,0k (300 000) · 3 tours · 1,50 $\n" % cent in s
                 and "\nhors fiches · %s = session %s + 0 sous-agent\n" % (deux, deux) in s
                 and "\nTOTAL (fiches + hors fiches) · ≈800,0k (800 000) · 8 tours · 4,00 $ = " in s), ("CPF1 : un sous-agent compte à la fiche que nomme son prompt, sinon à son départ") + "\n" + str(s)


def test_commit_au_titre(tmp_path, init_git):
    """PRP4 : une fiche à deux commits `<id> :` va jusqu'à celui qui porte son titre — `NUI20`,
    coupée à son commit d'étape, perdait sa séance (2 tours au lieu de 35)."""
    if not shutil.which("git"):
        pytest.skip("git absent — le commit au titre n'est pas testé")
        return
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        d, sq = os.path.join(t, "q"), os.path.join(t, "s.jsonl")
        transcript(sq, 6, [T0 + x for x in (50, 200, 250, 400, 700, 1000)])
        os.makedirs(os.path.join(t, "s", "subagents"))
        transcript(os.path.join(t, "s", "subagents", "agent-a1.jsonl"), 2, [T0 + 450, T0 + 460])
        ecrire(os.path.join(d, "q.md"), QFICHES % (sq, sq))
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        ecrire(env["GIT_CONFIG_GLOBAL"], "")
        init_git(d)
        for x, sujet in ((100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"), (350, "Q2 : l'avant, relevé"),
                         (380, "Autre : un chantier voisin au milieu"), (600, "Q2 : Brancher"),
                         (800, "Chantier Q clos : fini"), (950, "Q1 : correctif d'après")):
            date = "%d +0000" % (T0 + x)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=d, check=True,
                           capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
        q = os.path.join(d, "q.md")
        h = mod.heures_commits(q, ["Q1", "Q2"], titres={"Q1": "Créer", "Q2": "Brancher"})
        assert (h is not None and h[0] == {"Q1": T0 + 300, "Q2": T0 + 600}), ("PRP4 commit au titre : Q2 au sien, pas à l'étape ; Q1 pas étiré par son correctif") + "\n" + str(h)
        h = mod.heures_commits(q, ["Q1", "Q2"])
        assert (h is not None and h[0] == {"Q1": T0 + 300, "Q2": T0 + 350}), ("PRP4 commit au titre : sans titres, le plus ancien, comme avant") + "\n" + str(h)
        code, s = appel(["cout", q])
        assert (code == 0
                 and "\nQ1 · ≈200,0k (200 000) · 2 tours · 1,00 $" in s
                 and "\nQ2 · ≈300,0k (300 000) · 3 tours · 1,50 $" in s
                 and "TOTAL (fiches + hors fiches) · ≈700,0k (700 000) · 7 tours" in s), ("PRP4 commit au titre : cout donne à Q2 sa séance, sous-agent compris, total inchangé") + "\n" + str(s)
        # PRF : un commit `Q1 : case cochée` posé juste avant `Q1 : Créer` ne devient pas le début de Q1.
        d2 = os.path.join(t, "q2")
        ecrire(os.path.join(d2, "q.md"), QFICHES % (sq, sq))
        init_git(d2)
        for x, sujet in ((100, "Chantier Q ouvert : cadré"), (298, "Q1 : case cochée, en route"), (300, "Q1 : Créer"),
                         (600, "Q2 : Brancher"), (800, "Chantier Q clos : fini")):
            date = "%d +0000" % (T0 + x)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=d2, check=True,
                           capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
        code, s = appel(["cout", os.path.join(d2, "q.md")])
        assert (code == 0 and "\nQ1 · ≈200,0k (200 000) · 2 tours · 1,00 $" in s
                 and "TOTAL (fiches + hors fiches) · ≈700,0k (700 000) · 7 tours" in s), ("PRF : la première fiche part de l'ouverture, pas d'un commit à elle posé avant le sien") + "\n" + str(s)
        # Dette GAI : en parallèle, `Fusion : Q2` suit `Q2 :` d'une seconde ; la clôture va jusqu'au commit qui clôt.
        d3 = os.path.join(t, "q3")
        ecrire(os.path.join(d3, "q.md"), QFICHES % (sq, sq))
        init_git(d3)
        for x, sujet in ((100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"), (301, "Fusion : Q1"),
                         (600, "Q2 : Brancher"), (601, "Fusion : Q2"), (800, "Chantier Q clos : fini")):
            date = "%d +0000" % (T0 + x)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=d3, check=True,
                           capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
        h = mod.heures_commits(os.path.join(d3, "q.md"), ["Q1", "Q2"])
        code, s = appel(["cout", os.path.join(d3, "q.md")])
        assert (h is not None and T0 + 601 not in h[1] and T0 + 601 in h[2] and code == 0
                 and "\nhors fiches · ≈200,0k (200 000) · 2 tours" in s
                 and "TOTAL (fiches + hors fiches) · ≈700,0k (700 000) · 7 tours" in s), ("dette GAI : un commit « Fusion : Q2 » ne ferme pas la clôture, son tour reste hors fiches") + "\n" + str((h, s))
        # Dette GAI : `clore` d'un projet sans page de chantier (le bac de GAI2) compte son total, comme `cout`.
        d4 = os.path.join(t, "q4")
        ecrire(os.path.join(d4, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **artefact du chantier** : aucun\n\n"
               "Lettres de fiche déjà prises : U (test).\n")
        ecrire(os.path.join(d4, "ctx", "q.md"), ouvert(QFICHES % (sq, sq)))
        init_git(d4)
        for x, sujet in ((100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"), (600, "Q2 : Brancher")):
            date = "%d +0000" % (T0 + x)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=d4, check=True,
                           capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
        code, s = appel(["clore", d4, "--livre", "fini", "--date", "2026-10-17"])
        assert (code == 0 and "CLOS Q " in s and "· chantier 800 000 ·" in s and "joué 2 fiches 4,00 $" in s
                 and "non mesuré" not in open(os.path.join(d4, "ctx", "q.md"), encoding="utf-8").read()), ("dette GAI : clore sans page de chantier écrit le total mesuré, pas « non mesuré »") + "\n" + str(s)


def test_cout_session(tmp_path):
    """cout --session, valider --plan, lignes, equiper — regroupés dans une fonction : un test de
    plus au niveau du module fait tomber pyright (« Code is too complex to analyze », chantier TAU3)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        f = os.path.join(t, "y.md")
        ecrire(f, SANS)
        assert (appel(["cout", f]) == (0, "SESSIONS 0 — pas de total\n")), ("cout : aucune session") + "\n" + str(appel(["cout", f]))
        ecrire(f, AVEC)
        for s_ in ("aaa", "bbb", "ccc"):
            os.makedirs(os.path.join(t, ".claude", "projects", "p"), exist_ok=True)
            transcript(os.path.join(t, ".claude", "projects", "p", s_ + ".jsonl"), 2)
        garde_env = dict(os.environ)
        os.environ.update(HOME=t, USERPROFILE=t, CLAUDE_CODE_SESSION_ID="ccc")
        try:
            code, s = appel(["cout", f])
            assert (code == 0 and "aaa.jsonl\t" in s and "bbb.jsonl\t" in s
                     and "ccc.jsonl\t" not in s and s.count("TOTAL\t") == 1 and s.startswith("DÉCOUPE aucune — ")), ("cout : toutes les sessions du fichier, un total") + "\n" + str(s)
            code, s = appel(["cout", f, "--session"])
            assert (code == 0 and s.startswith("SESSION=ccc\nfichier\t")
                     and s.split("TOTAL\t")[0].count("ccc.jsonl\t") == 3 and s.count("TOTAL\t") == 1
                     and s.count("\nDÉCOUPE aucune — ") == 1), ("cout --session : la session seule, puis le cumul") + "\n" + str(s)
            os.environ["CLAUDE_CODE_SESSION_ID"] = ""
            assert (appel(["cout", f, "--session"]) == (0, "SESSION=\n")), ("cout --session : id vide, rien mesuré") + "\n" + str(appel(["cout", f, "--session"]))
        finally:
            os.environ.clear()
            os.environ.update(garde_env)
        code, s = appel(["valider", f, "--plan"])
        assert (s.endswith("\n12:## Y1 [x] — faite\n24:## Y2 [ ] — à faire\n")
                 and "pas un titre" not in s), ("valider --plan : titres de fiche, grep -n") + "\n" + str(s)
        code, s = appel(["lignes", f, t, os.path.join(t, "absent.md"), os.path.join(t, "*.md")])
        assert (code == 0 and s == "%d %s\nDOSSIER %s\nABSENT %s\n%d %s\nSEUILS page %d · fiche %d · socle %d\n"
                 % (len(mod.lignes_de(f)), f, t, os.path.join(t, "absent.md"), len(mod.lignes_de(f)), f, mod.SEUIL_PAGE, mod.SEUIL_FICHE, mod.SEUIL_SOCLE)), ("lignes : fichier, dossier, absent, motif") + "\n" + str(s)
        d = os.path.join(t, "projet")
        for n in ("b", "A", ".cache"):
            os.makedirs(os.path.join(d, n))
        ecrire(os.path.join(d, "CLAUDE.md"), "# C\n")
        assert (appel(["equiper", d]) == (0, "DOSSIER=%s\nA/\nb/\nCLAUDE.md\nAUCUN_PROJET\nETAT=01-etat.md\n" % os.path.abspath(d))), ("equiper : dossier, sous-dossiers, CLAUDE.md, carte, état") + "\n" + str(appel(["equiper", d]))
        absent = os.path.join(t, "absent")
        try:
            vu = appel(["equiper", absent])
        except OSError as e:
            vu = (None, repr(e))
        assert (vu == (1, "GARDE: dossier absent : %s — rien lu\n" % os.path.abspath(absent))), ("equiper : un dossier absent → une GARDE, sort 1, pas de trace Python (chantier ISO)") + "\n" + str(vu)


def test_essais_de(tmp_path):
    """Contrôler `essais_de` : les bacs d'un projet, triés."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        pr = os.path.join(t, ".claude", "projects")
        for bac in ("C--tmp-sa-aaaa-1-scratchpad-b1", "C--tmp-sa-aaaa-1-scratchpad-b2", "C--tmp-sa-bbbb-2-scratchpad-b1",
                    "C--tmp-sa-aaaa-1-intrus"):     # le dernier n'est pas un bac : pas de `-scratchpad-`
            ecrire(os.path.join(pr, bac, "e.jsonl"), "{}\n")
        garde_env = dict(os.environ)
        os.environ.update(HOME=t, USERPROFILE=t)
        try:
            a, b, z = mod.essais_de("aaaa-1"), mod.essais_de("bbbb-2"), mod.essais_de("zzzz-9")
        finally:
            os.environ.clear()
            os.environ.update(garde_env)
        assert (a == [os.path.join(pr, "C--tmp-sa-aaaa-1-scratchpad-b1", "e.jsonl"),
                       os.path.join(pr, "C--tmp-sa-aaaa-1-scratchpad-b2", "e.jsonl")]), ("essais_de : les deux bacs de A, triés, sans l'intrus") + "\n" + str(a)
        assert (len(b) == 1 and "bbbb-2-scratchpad-b1" in b[0]), ("essais_de : le bac de B seul") + "\n" + str(b)
        assert (z == []), ("essais_de : session inconnue, liste vide") + "\n" + str(z)
        # MET2 : un essai hors bac (une copie du kit) se déclare au registre, par `vlp.py essai`.
        for copie in ("D--x-vlp-essai-v1", "D--x-vlp-essai-v2", "D--x-vlp-autre-w1"):
            ecrire(os.path.join(pr, copie, "e.jsonl"), "{}\n")
        o, refus = io.StringIO(), io.StringIO()
        os.environ.update(HOME=t, USERPROFILE=t)
        try:
            codes = (mod.main(["essai", "D--x-vlp-essai-*", "--session", "aaaa-1"], o),
                     mod.main(["essai", "D--x-vlp-essai-*", "--session", "aaaa-1"], o),
                     mod.main(["essai", "D--x-vlp-autre-w1", "--session", "bbbb-2"], o),
                     mod.main(["essai", "../x", "--session", "aaaa-1"], refus))
            a2, b2 = mod.essais_de("aaaa-1"), mod.essais_de("bbbb-2")
        finally:
            os.environ.clear()
            os.environ.update(garde_env)
        with open(os.path.join(t, ".claude", "vlp-essais.txt"), encoding="utf-8") as f:
            registre = f.read().splitlines()
        assert (codes == (0, 0, 0, 1)
                 and a2 == sorted(a + [os.path.join(pr, "D--x-vlp-essai-v1", "e.jsonl"),
                                       os.path.join(pr, "D--x-vlp-essai-v2", "e.jsonl")])
                 and b2 == sorted(b + [os.path.join(pr, "D--x-vlp-autre-w1", "e.jsonl")])
                 and "ESSAI aaaa-1 D--x-vlp-essai-* · 2 dossier(s) · 2 transcript(s)" in o.getvalue()), ("essai : un essai hors bac déclaré pour A est à A, pas à B") + "\n" + str((codes, a2, b2, o.getvalue()))
        assert (registre == ["aaaa-1 D--x-vlp-essai-*", "bbbb-2 D--x-vlp-autre-w1"]
                 and refus.getvalue().startswith("GARDE: essai non déclaré")), ("essai : déclaré une fois, un motif qui sort du dossier refusé") + "\n" + str((registre, refus.getvalue()))


def test_cout_essai_plage(tmp_path, init_git):
    """Contrôler `cout` : un essai dans la plage d'une fiche compte, sous-agent compris."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        pr, dep = os.path.join(t, ".claude", "projects"), os.path.join(t, "depot")
        os.makedirs(os.path.join(pr, "p"))
        transcript(os.path.join(pr, "p", "sss.jsonl"), 2, [T0 + 200, T0 + 400])
        for bac, h_ in (("b1", 250), ("b2", 700)):
            os.makedirs(os.path.join(pr, "C--x-sss-scratchpad-" + bac))
            transcript(os.path.join(pr, "C--x-sss-scratchpad-" + bac, "e.jsonl"), 1, [T0 + h_])
        os.makedirs(os.path.join(pr, "C--x-sss-scratchpad-b1", "e", "subagents"))
        transcript(os.path.join(pr, "C--x-sss-scratchpad-b1", "e", "subagents", "agent-a1.jsonl"), 1, [T0 + 260])
        os.makedirs(os.path.join(pr, "D--x-hors"))      # ESH : un essai hors bac, non déclaré — signalé, pas compté
        transcript_marque(os.path.join(pr, "D--x-hors", "h.jsonl"), "sdk", [T0 + 250])
        ecrire(os.path.join(dep, "q.md"), QFICHES % ("sss", "sss"))
        if not shutil.which("git"):
            pytest.skip("git absent — les essais dans la découpe ne sont pas testés")
        else:
            env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                       GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
            ecrire(env["GIT_CONFIG_GLOBAL"], "")
            init_git(dep)
            for d, sujet in ((100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"), (600, "Q2 : Brancher")):
                date = "%d +0000" % (T0 + d)
                subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=dep, check=True,
                               capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
            garde_env = dict(os.environ)
            os.environ.update(HOME=t, USERPROFILE=t)
            try:
                code, s = appel(["cout", os.path.join(dep, "q.md")])
            finally:
                os.environ.clear()
                os.environ.update(garde_env)
            cent, deux, trois = "≈100,0k (100 000) · 1 tours · 0,50 $", "≈200,0k (200 000) · 2 tours · 1,00 $", "≈300,0k (300 000) · 3 tours · 1,50 $"
            attendu = (DECOUPE_TETE +
                       "Q1 · %s = session %s + 0 sous-agent + 1 essai %s\n" % (trois, cent, deux)
                       + "Q2 · %s = session %s + 0 sous-agent\n" % (cent, cent)
                       + "hors fiches · %s = session 0 · 0 tours · 0,00 $ + 0 sous-agent + 1 essai %s\n" % (cent, cent)
                       + "TOTAL (fiches + hors fiches) · ≈500,0k (500 000) · 5 tours · 2,50 $ = session %s"
                         " + 0 sous-agent + 2 essais %s\n" % (deux, trois)
                       + "GARDE: essai claude -p hors bac, non déclaré : h · parti le %s · %s · dossier D--x-hors — le "
                         "déclarer : vlp.py essai D--x-hors --session sss (ESH)\n"
                         % (time.strftime("%Y-%m-%d %H:%M", time.localtime(T0 + 250)), cent))
            assert (code == 0 and s == attendu), ("cout : l'essai de la plage à Q1, sous-agent compris ; l'autre hors fiches ; TOTAL les deux ; "
                     "l'essai hors bac signalé en dernier, hors du TOTAL (ESH)") + "\n" + str(s)


def test_essais_hors_bac(tmp_path):
    """ESH : `cout` signale un essai `claude -p` (marque `turnOrigin` "sdk") parti pendant une session du fichier, hors
    bac, hors nuit, non déclaré ; et dit une plage sans marque, après `MARQUE_DEPUIS` seulement."""
    t1, jsonl = T0 + 5 * 86400, transcript_marque     # t1 : après MARQUE_DEPUIS (2026-09-22) ; T0 est avant
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        pr = os.path.join(t, ".claude", "projects")
        for dossier, nom, marque, heures in (
                ("p", "sss", "human", [t1 + 100, t1 + 1000]),           # la session du chantier
                ("D--x-essai", "e1", "sdk", [t1 + 500]),                # hors bac, non déclaré : signalé
                ("C--x-zzz-scratchpad-b1", "e2", "sdk", [t1 + 500]),    # dans le bac d'une autre session
                ("D--x-declare", "e3", "sdk", [t1 + 500]),              # déclaré au registre
                ("D--k-claude-worktrees-nuit-2026-10-01-A", "e4", "sdk", [t1 + 500]),   # une séance de nuit
                ("D--x-app", "h1", "human", [t1 + 500]),                # l'app : pas un essai
                ("D--x-tard", "e5", "sdk", [t1 + 5000])):               # parti après la session
            os.makedirs(os.path.join(pr, dossier), exist_ok=True)
            jsonl(os.path.join(pr, dossier, nom + ".jsonl"), marque, heures)
        ecrire(os.path.join(t, ".claude", "vlp-essais.txt"), "zzz D--x-declare\n")
        ecrire(os.path.join(t, "y.md"), "## Y1 [ ] — x\n**Session** : sss\n")
        for dossier, nom, marque, heures in (("q", "ttt", None, [t1 + 20000, t1 + 21000]),  # récente, seule, sans marque
                                             ("q", "vvv", None, [T0 + 100, T0 + 1000])):    # d'avant la marque
            os.makedirs(os.path.join(pr, dossier), exist_ok=True)
            jsonl(os.path.join(pr, dossier, nom + ".jsonl"), marque, heures)
        garde_env = dict(os.environ)
        os.environ.update(HOME=t, USERPROFILE=t)
        try:
            gardes = mod.essais_hors_bac(["sss"])
            coupe = mod.essais_hors_bac(["sss"], (t1 + 600, t1 + 2000))
            sans, avant = mod.essais_hors_bac(["ttt"]), mod.essais_hors_bac(["vvv"])
            code, s = appel(["cout", os.path.join(t, "y.md")])
        finally:
            os.environ.clear()
            os.environ.update(garde_env)
        parti = time.strftime("%Y-%m-%d %H:%M", time.localtime(t1 + 500))
        assert (gardes == ["GARDE: essai claude -p hors bac, non déclaré : e1 · parti le %s · ≈100,0k (100 000) · "
                            "1 tours · 0,50 $ · dossier D--x-essai — le déclarer : vlp.py essai D--x-essai --session sss "
                            "(ESH)" % parti]), ("ESH : un seul essai signalé, e1 — ni bac, ni déclaré, ni nuit, ni l'app, ni parti après la session ; "
                 "la commande qui le déclare — mutant : le filtre du bac retiré") + "\n" + str(gardes)
        assert (coupe == []), ("ESH : un essai parti avant les bornes de la plage n'est pas signalé") + "\n" + str(coupe)
        assert (sans == ["GARDE: aucune séance de la plage ne porte la marque turnOrigin — un essai claude -p hors bac "
                          "n'y serait pas vu (marque interne, non documentée ; ESH)"] and avant == []), ("ESH : une session récente sans marque turnOrigin, une GARDE ; d'avant la marque, rien") + "\n" + str((sans, avant))
        assert (code == 0 and s.splitlines()[-1] == gardes[0]), ("ESH : cout imprime la GARDE en dernière ligne, sort 0") + "\n" + str(s)


def test_cout_sans_decoupe(tmp_path):
    """Contrôler `cout` sans découpe : la ligne des essais, avec et sans essai (chantier ESD)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        pr, dep = os.path.join(t, ".claude", "projects"), os.path.join(t, "depot")
        os.makedirs(os.path.join(pr, "p"))
        for s_ in ("sss", "ttt"):
            transcript(os.path.join(pr, "p", s_ + ".jsonl"), 2, [T0 + 200, T0 + 400])
        for bac in ("b1", "b2"):
            os.makedirs(os.path.join(pr, "C--x-sss-scratchpad-" + bac))
            transcript(os.path.join(pr, "C--x-sss-scratchpad-" + bac, "e.jsonl"), 1, [T0 + 250])
        os.makedirs(os.path.join(pr, "C--x-sss-scratchpad-b1", "e", "subagents"))
        transcript(os.path.join(pr, "C--x-sss-scratchpad-b1", "e", "subagents", "agent-a1.jsonl"), 1, [T0 + 260])
        ecrire(os.path.join(dep, "avec.md"), QFICHES % ("sss", "sss"))
        ecrire(os.path.join(dep, "sans.md"), QFICHES % ("ttt", "ttt"))
        garde_env = dict(os.environ)
        os.environ.update(HOME=t, USERPROFILE=t)
        try:
            (code, s), (code2, s2) = appel(["cout", os.path.join(dep, "avec.md")]), appel(["cout", os.path.join(dep, "sans.md")])
        finally:
            os.environ.clear()
            os.environ.update(garde_env)
        assert (code == 0 and s.startswith("DÉCOUPE aucune — ") and "\nsss.jsonl\t2\t" in s
                 and s.endswith("\nessais · ≈300,0k (300 000) · 3 tours · 1,50 $ = session 0 · 0 tours · 0,00 $"
                                " + 0 sous-agent + 2 essais ≈300,0k (300 000) · 3 tours · 1,50 $\n")), ("cout sans découpe : une ligne essais, 2 essais sous-agent compris, après les tables") + "\n" + str(s)
        assert (code2 == 0
                 and s2.startswith("DÉCOUPE aucune — ") and "essai" not in s2 and s2.endswith("\n")), ("cout sans découpe, sans essai : pas de ligne essais") + "\n" + str(s2)


def test_lance_clore():
    """ECA1 : un appel `clore` est une commande lancée ; la ligne de bilan qui le cite n'en est pas un."""
    cas = [('py scripts/vlp.py clore . --livre x', True),
           ('cd "C:/k" && py "C:/k/scripts/vlp.py" clore .', True),
           ('export A=b; py scripts/vlp.py clore .', True),
           ("cat > f.py <<'EOF'\nprint(1)\nEOF\npy scripts/vlp.py clore .", True),
           ('$o = py "$kit/scripts/vlp.py" clore .', True),
           ('python3 -X utf8 scripts/vlp.py clore .', True),
           ('"C:/Program Files/Python/python.exe" "C:/Mes documents/kit/scripts/vlp.py" clore .', True),
           ('echo "- Coût du chantier : 8 (\\`vlp.py clore\\`)." >> "context AI/08-etat.md"', False),
           ("cat >> etat.md <<'EOF'\n- Coût du chantier : 8 (`vlp.py clore`).\nEOF", False),
           ('git commit -q -m "O3 faite : vlp.py clore écrit le bilan"', False),
           ('py scripts/vlp.py page . --resultat "À la clôture, vlp.py clore écrit l\'estimé"', False),
           ("cat > t.ps1 <<'EOF'\npy scripts/vlp.py clore .\nEOF", False),
           ('grep -n "clore" scripts/vlp.py', False)]
    faux = [(c, attendu) for c, attendu in cas if mod.lance_clore(c) != attendu]
    assert (not faux), ("ECA1 : lance_clore, %d cas — mutant : l'ancien motif (le texte cité compte)" % len(cas)) + "\n" + str(repr(faux))


def test_clos_sans_commit(tmp_path, init_git):
    """ECA2 : un clos dont Q2 n'a pas de commit « Q2 : » — son travail est dans « Journal : … Q2 ».
    Tours à 200 (Q1), 400 et 500 (Q2), l'appel clore à 700, puis 800, 1000, 1100 : la session a
    continué après la clôture (900). Q2 s'arrête au journal (600), hors fiches à l'appel clore."""
    if not shutil.which("git"):
        pytest.skip("git absent — ECA2 n'est pas testé")
        return
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        dep, sq = os.path.join(t, "depot"), os.path.join(t, "s.jsonl")
        transcript(sq, 7, [T0 + d for d in (200, 400, 500, 700, 800, 1000, 1100)])
        lignes_ = [json.loads(l) for l in lire(sq).splitlines()]
        lignes_[3]["message"]["content"] = [{"type": "tool_use", "id": "t3", "name": "Bash",
                                             "input": {"command": "py scripts/vlp.py clore . --livre x"}}]
        ecrire(sq, "".join(json.dumps(l) + "\n" for l in lignes_))
        ecrire(os.path.join(dep, "q.md"), (QFICHES % (sq, sq)).replace("# Chantier Q\n",
                                                                         "# Chantier Q\n\n**CLOS** le 2026-05-06.\n", 1))
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        ecrire(env["GIT_CONFIG_GLOBAL"], "")
        init_git(dep)
        for d, sujet in ((100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"),
                         (600, "Journal : la mesure de Q2"), (900, "Chantier Q clos : fini")):
            date = "%d +0000" % (T0 + d)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=dep, check=True,
                           capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
        code, s = appel(["cout", os.path.join(dep, "q.md")])
        lignes_ = s.splitlines()
        q2 = [l for l in lignes_ if l.startswith("Q2 · ")]
        total = [l for l in lignes_ if l.startswith("TOTAL ")]
        assert (code == 0 and len(q2) == 1 and mod.triplet(q2[0])[:2] == (200000, 2)
                 and len(total) == 1 and mod.triplet(total[0])[:2] == (400000, 4)), ("ECA2 : clos, Q2 sans commit — Q2 2 tours, TOTAL 400 000 · 4 tours — mutant : clos ignoré"
                 " (TOTAL 700 000 · 7 tours)") + "\n" + str(s)


def horodate(d):
    return datetime.datetime.fromtimestamp(T0 + d, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def tour_compteur(d, n, *blocs):
    """Une ligne assistant à T0 + d, son tour n (100 000 tokens d'entrée, 0,50 $), ses blocs."""
    return {"type": "assistant", "timestamp": horodate(d), "requestId": "r%d" % n, "message": {
        "id": "m%d" % n, "model": "claude-opus-5", "content": list(blocs),
        "usage": {"input_tokens": 100000, "output_tokens": 0, "cache_creation_input_tokens": 0,
                  "cache_read_input_tokens": 0}}}


def outil_compteur(ident, nom, **entree):
    return {"type": "tool_use", "id": ident, "name": nom, "input": entree}


def user_compteur(d, contenu, origine=None, **plus):
    ligne = dict({"type": "user", "message": {"role": "user", "content": contenu}}, **plus)
    if d is not None:
        ligne["timestamp"] = horodate(d)
    if origine:
        ligne["origin"] = {"kind": origine}
    return ligne


def sortie_compteur(d, ident, texte):
    return user_compteur(d, [{"type": "tool_result", "tool_use_id": ident, "content": texte}])


def notification_compteur(d, balise, texte):
    return user_compteur(d, "<task-notification>\n%s\n<summary>%s</summary>\n</task-notification>" % (balise, texte),
                         "task-notification")


def lignes_compteur():
    """La transcription faite main de VIT17, en secondes après T0 : chaque écart a sa part en face, et la somme des
    parts se fait à la main — modèle 127, outils 753, attente 80, autre 25 ; une pause (960 → 3000)."""
    sortie_b = '"C:/t/tasks/%s.output"'
    mutant = 'py -3 scripts/vlp.py mutant scripts/a.py "x" "y" --test "uv run pytest --seul z"'
    return [
        {"type": "queue-operation", "operation": "enqueue", "timestamp": horodate(0)},    # hors conversation
        user_compteur(0, "vas-y", "human"),                                                # attente 0
        tour_compteur(10, 1, outil_compteur("u1", "Bash", command="uv run --frozen pytest -n 4")),   # modèle 10
        sortie_compteur(70, "u1", "SAUTÉ: x\nOK"),                                        # suite 60, verte
        {"type": "attachment", "timestamp": horodate(80)},                                # hors conversation
        tour_compteur(90, 2, outil_compteur("u2", "AskUserQuestion", questions=[])),      # modèle 10 + 10
        sortie_compteur(150, "u2", "Your questions have been answered: oui"),              # attente 60
        tour_compteur(160, 3, outil_compteur("u3", "Bash", command=mutant, run_in_background=True)),   # modèle 10
        sortie_compteur(161, "u3", "Command running in background with ID: b1."),          # mutant 1, b1 noté
        tour_compteur(170, 4, outil_compteur("u7", "Bash", command="until grep -q ATTRAP %s; do sleep 5; done; cat %s"
                                             % (sortie_b % "b1", sortie_b % "b1"))),   # modèle 9
        sortie_compteur(400, "u7", "ÉCART: z\nMUTANT ATTRAPÉ 1 écart(s)"),                 # attend b1 : mutant 230
        notification_compteur(405, "<tool-use-id>u3</tool-use-id>", "fini (exit code 0)"),   # mutant 5, fond
        tour_compteur(410, 5, outil_compteur("u9", "Bash", command="uv run --frozen pytest -n 4", run_in_background=True)),
        sortie_compteur(411, "u9", "Command running in background with ID: b2."),          # suite 1, sans verdict
        tour_compteur(420, 6, outil_compteur("u8", "Monitor", command='until grep -q "^OK" %s; do sleep 5; done'
                                             % (sortie_b % "b2"))),   # modèle 9
        sortie_compteur(421, "u8", "Monitor started (task m1, expires in 5m)."),           # attend b2 : suite 1
        tour_compteur(430, 7),                                                             # modèle 9
        notification_compteur(700, "<task-id>m1</task-id>", "Monitor event"),             # par m1 : suite 270
        notification_compteur(710, "<tool-use-id>u9</tool-use-id>", "fini (exit code 1)"),   # suite 10, rouge
        tour_compteur(720, 8, outil_compteur("u11", "Bash", command="uv run --frozen pytest --seul compteur")),
        sortie_compteur(750, "u11", "ÉCART: w\nFIN: 1 écart(s)"),                          # --seul 30, rouge
        tour_compteur(760, 9, outil_compteur("u4", "Read", file_path="C:/t/x.md")),        # modèle 10
        sortie_compteur(770, "u4", "     1→MUTANT ATTRAPÉ 1 écart(s)\n     2→GARDE: x"),   # reste 10, rien de lu
        tour_compteur(780, 10, outil_compteur("u10", "Bash", command="py -3 scripts/vlp.py cocher f.md X1")),
        sortie_compteur(790, "u10", "GARDE: suite rouge"),                                 # reste 10, GARDE 1
        tour_compteur(800, 11, outil_compteur("u12", "Agent", subagent_type="vlp:relecture")),   # modèle 10
        sortie_compteur(900, "u12", "ACCEPTÉE — ok\nGARDE: q"),                            # reste 100, ACCEPTÉE 1
        user_compteur(910, "consigne", isMeta=True),                                       # autre 10
        user_compteur(920, "[Subagent hand-back] rapport :\n  REFUSÉE — copie", "peer", isMeta=True),   # autre 10
        sortie_compteur(930, "u99", "ÉCART: y"),                                           # appel inconnu : reste 10
        tour_compteur(940, 12, outil_compteur("u5", "Bash", command='git commit -m "Q1 : Créer"')),   # modèle 10
        sortie_compteur(945, "u5", "[main abc] Q1 : Créer"),                               # Git 5
        tour_compteur(950, 13, outil_compteur("u6", "Artifact", action="publish")),        # modèle 5
        sortie_compteur(960, "u6", "publié"),                                              # publication 10
        user_compteur(None, "sans heure"),                                                 # hors du temps
        tour_compteur(3000, 14),                                                           # pause de 2 040 s
        user_compteur(3020, "la suite", "human"),                                          # attente 20
        {"type": "system", "subtype": "stop_hook_summary", "timestamp": horodate(3025)},   # au reste, à la fin
    ]


def ecrire_compteur(chemin, cout_etat=None):
    """Écrire la transcription faite main ; `cout_etat` : une ligne `cost-state` posée après le tour de 760 s."""
    lignes = lignes_compteur()
    if cout_etat is not None:
        lignes.insert(22, dict(cout_etat, type="cost-state"))
    ecrire(chemin, "".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lignes))


TOUT_COMPTEUR = ("actif 16 = modèle 2 + outils 13 + attente 1 + autre 0 · outils : suite 6 (2), --seul 1 (1), "
                 "test-boucle 0 (0), mutant 4 (1), pyright 0 (0), Git 0 (1), publication 0 (1), relance 0 (0), reste 2 "
                 "(4) · 14 tours · 7,00 $ · garde-fous : suites 1/3, ÉCART 1, MUTANT ATTRAPÉ 1, GARDE 1, relecteur 1 ACCEPTÉE + 1 "
                 "REFUSÉE")


def test_compteur_lecture(tmp_path):
    """Contrôler la lecture de `compteur` (VIT17) sur la transcription faite main : les parts à la seconde, le temps
    et les appels par sorte d'outil, les garde-fous, ce qui manque, la ligne en minutes."""
    m = mod.mesure()
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        chemin = os.path.join(t, "sss.jsonl")
        ecrire_compteur(chemin)
        j, erreur = m.journal(chemin, mod.lire_sortie)
        assert (erreur is None and (j.sans_heure, j.sans_appel, j.users, j.origines) == (1, 1, 21, 6)), ("compteur : ce qui manque se compte — 1 ligne sans heure, 1 sortie sans appel, 21 user dont 6 à origin") + "\n" + str((erreur, j and vars(j).items()))
        mesure_ = mod.compter_plage([(chemin, j)], (-mod.INFINI, mod.INFINI))
    assert ((mesure_["parts"], mesure_["pauses"]) == ({"modèle": 127, "outils": 753, "attente": 80, "autre": 25}, 1)), ("compteur : un écart va à la ligne qui le ferme — modèle 127, outils 753, attente 80, autre 25, 1 pause") + "\n" + str(mesure_)
    assert (mesure_["outils"] == {"suite": 342, "--seul": 30, "test-boucle": 0, "mutant": 236, "pyright": 0, "Git": 5,
                                   "publication": 10, "relance": 0, "reste": 130} and mesure_["fond"] == 285), ("compteur : l'attente d'une tâche de fond va à l'appel qui l'a lancée — boucle, Monitor, notification") + "\n" + str(mesure_)
    assert (mesure_["appels"] == {"suite": 2, "--seul": 1, "test-boucle": 0, "mutant": 1, "pyright": 0, "Git": 1,
                                   "publication": 1, "relance": 0, "reste": 4}), ("compteur : un appel par sortie directe — ni la notification, ni l'attente, ni la réponse à une question") + "\n" + str(mesure_["appels"])
    assert ((mesure_["suites"], mesure_["garde_fous"]) == ([3, 1], [1, 1, 1, 1, 1])), ("compteur : les garde-fous lus là où ils disent vrai, les suites jugées sur leur verdict") + "\n" + str(mesure_)
    assert (mod.ligne_compteur("tout", mesure_, (0, 14, Decimal("7.00"), 1)) == "tout · durée - · " + TOUT_COMPTEUR), ("compteur : la ligne en minutes, chaque total juste à la minute (plus gros restes)") + "\n" + str(mod.ligne_compteur("tout", mesure_, (0, 14, Decimal("7.00"), 1)))
    vide = m.Journal(users=3)
    assert (mod.manques([("a/s.jsonl", vide)]) == ["AVERTISSEMENT: s.jsonl : 3 ligne(s) user, aucune avec origin — "
                                                    "l'attente tombe au reste"]), ("compteur : manques — une session sans origin, rien de tapé ne se lit, ça se dit") + "\n" + str(mod.manques([("a/s.jsonl", vide)]))
    agent = os.path.join("s", "subagents", "agent-a.jsonl")
    evenements = [(T0 + 5, m.MODELE, None), (T0 + 2000, m.MODELE, None)]
    assert ((m.tranche(agent, evenements, (T0, T0 + 10)), m.tranche(agent, evenements, (T0 + 10, T0 + 9000)))
             == (evenements, [])), ("compteur : un sous-agent tout entier ou pas du tout, à son départ") + "\n" + str(m.tranche(agent, evenements, (T0, T0 + 10)))


def test_compteur_sortes():
    """Contrôler les sortes d'outil, le verdict d'une suite, l'arrondi qui somme juste et la recoupe sans plage de
    `compteur` (VIT17)."""
    cas = [("Bash", "uv run --frozen pytest -n 4", "suite"), ("Bash", "py -3 -m pytest -q", "suite"), ("Bash", "uv run --frozen --project D:/kit pytest -q", "suite"),
           ("Bash", 'cd "D:/x" && uv run pytest --seul compteur', "--seul"),
           ("Bash", "uv run pytest > o.txt; grep -- --seul o.txt", "suite"),
           ("Bash", 'py -3 scripts/vlp.py mutant a.py "x" "y" --test "uv run pytest --seul z"', "mutant"),
           ("PowerShell", '& "C:/Python/python.exe" scripts/test-boucle.py', "test-boucle"),
           ("Bash", "pyright scripts/vlp.py", "pyright"), ("PowerShell", "git -C . log -1", "Git"),
           ("Bash", 'grep -n "pytest" scripts/x.py', "reste"),
           ("Bash", "cat > f.sh <<'EOF'\nuv run pytest\nEOF", "reste"),
           ("Artifact", "", "publication"), ("Read", "", "reste")]
    rendus = [mod.sorte_outil((nom, {"command": c})) for nom, c, _ in cas]
    assert (rendus == [s for _, _, s in cas]), ("compteur : la sorte d'un appel, à ce qu'il lance en tête d'un segment — ni cité, ni dans un heredoc") + "\n" + str(list(zip(rendus, [s for _, _, s in cas])))
    verdicts = [mod.verdict_suite(*a) for a in (("SAUTÉ: x\nOK", ""), ("ÉCART: x\nFIN: 1", ""), ("fini\n", ""),
                                                ("(exit code 0)", "fond"), ("(exit code 1)", "fond"), ("tué", "fond"),
                                                ("(exit code 0)", "fond attente"), ("OK", "attente"))]
    assert (verdicts == [True, False, None, True, False, None, None, None]), ("compteur : le verdict d'une suite — OK vert, ÉCART rouge, muet non jugé ; en fond, le code de sortie") + "\n" + str(verdicts)
    reparties = (mod.minutes_reparties([74, 326, 80, 25]), mod.minutes_reparties([60, 231, 20, 5, 10], 6),
                 mod.minutes_reparties([0, 0]))
    assert (reparties == ([1, 6, 1, 0], [1, 4, 1, 0, 0], [0, 0])), ("compteur : les minutes somment leur total — les plus gros restes prennent la minute") + "\n" + str(reparties)
    assert ((mod.ligne_recoupe("R", T0, {}, []), mod.ligne_recoupe("R", None, {"startTime": 1}, []))
             == ("R · pas de plage — startTime absent", "R · pas de plage — aucune ligne horodatée avant")), ("compteur : une cost-state sans startTime, ou sans ligne horodatée avant, n'a pas de plage — ça se dit") + "\n" + str(mod.ligne_recoupe("R", T0, {}, []))


def test_compteur_commande(tmp_path, init_git):
    """Contrôler `vlp.py compteur` de bout en bout (VIT17) : les plages de `cout`, fiches nommées, `--recoupe`, et la
    `GARDE:` sans découpe."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        pr, dep = os.path.join(t, ".claude", "projects", "p"), os.path.join(t, "depot")
        ecrire_compteur(os.path.join(pr, "sss.jsonl"), {"startTime": (T0 - 10) * 1000, "totalToolDuration": 300000,
                                                        "totalAPIDuration": 120000})
        ecrire(os.path.join(dep, "q.md"), QFICHES % ("sss", "sss"))
        mod.etat.GIT = "git-absent-vlp"
        try:
            sans_git = appel(["compteur", os.path.join(dep, "q.md")])
        finally:
            mod.etat.GIT = "git"
        assert (sans_git[0] == 1 and sans_git[1].startswith(
            "GARDE: pas de découpe — git ne se lance pas")), ("compteur : sans découpe, une GARDE: et 1") + "\n" + str(sans_git)
        if not shutil.which("git"):
            pytest.skip("git absent — compteur de bout en bout n'est pas testé")
            return
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        ecrire(env["GIT_CONFIG_GLOBAL"], "")
        init_git(dep)
        for d, sujet in ((-100, "Chantier Q ouvert : cadré"), (943, "Q1 : Créer"), (3010, "Q2 : Brancher")):
            date = "%d +0000" % (T0 + d)
            subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=dep, check=True,
                           capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
        garde_env = dict(os.environ)
        os.environ.update(HOME=t, USERPROFILE=t)
        try:
            rendus = [appel(["compteur", os.path.join(dep, "q.md")] + plus)
                      for plus in ([], ["Q2"], ["Q9"], ["--recoupe"])]
        finally:
            os.environ.clear()
            os.environ.update(garde_env)
        ecrire(os.path.join(dep, "CHANTIER.md"), "# Chantier\n\n- **alias** : q\n- **commandes longues** : "
                                                 "`vlp.py cocher`, `calcul.py`\n")
        os.environ.update(HOME=t, USERPROFILE=t)
        try:
            relance = appel(["compteur", os.path.join(dep, "q.md"), "Q1"])
        finally:
            os.environ.clear()
            os.environ.update(garde_env)
        declarees = (mod.relances_de(os.path.join(dep, "q.md")), mod.relances_de(os.path.join(t, "q.md")))
    rien = ("actif 0 = modèle 0 + outils 0 + attente 0 + autre 0 · outils : suite 0 (0), --seul 0 (0), test-boucle 0 "
            "(0), mutant 0 (0), pyright 0 (0), Git 0 (%d), publication 0 (%d), relance 0 (0), reste 0 (0) · %d tours · "
            "%s $ · "
            "garde-fous : suites -, ÉCART -, MUTANT ATTRAPÉ -, GARDE -, relecteur -")
    q2 = "Q2 · durée 34 · " + rien % (1, 1, 2, "1,00")
    lignes = ["AVERTISSEMENT: sss.jsonl : 1 ligne(s) de message sans heure, hors du temps",
              "AVERTISSEMENT: sss.jsonl : 1 sortie(s) sans appel connu, rangée(s) au reste",
              mod.ENTETE_COMPTEUR % 30,
              "Q1 · durée 17 · actif 16 = modèle 2 + outils 12 + attente 1 + autre 1 · outils : suite 6 (2), --seul 0 "
              "(1), test-boucle 0 (0), mutant 4 (1), pyright 0 (0), Git 0 (0), publication 0 (0), relance 0 (0), reste 2 "
              "(4) · 12 tours · 6,00 $ · garde-fous : suites 1/3, ÉCART 1, MUTANT ATTRAPÉ 1, GARDE 1, relecteur 1 ACCEPTÉE + 1 "
              "REFUSÉE", q2, "hors fiches · durée - · " + rien % (0, 0, 0, "0,00"),
              "TOTAL (fiches + hors fiches) · durée - · " + TOUT_COMPTEUR]
    assert (rendus[0] == (0, "\n".join(lignes) + "\n")), ("compteur : une ligne par fiche aux plages de cout, hors fiches, TOTAL — l'écart à cheval sur un commit "
             "ne compte nulle part") + "\n" + str(rendus[0][1])
    assert (rendus[1] == (0, "\n".join(
        lignes[:3] + [q2, "TOTAL (fiches nommées) · durée 34 · " + rien % (1, 1, 2, "1,00")]) + "\n")), ("compteur : les fiches nommées seules, et leur TOTAL") + "\n" + str(rendus[1][1])
    assert (rendus[2][0] == 1
             and "GARDE: fiche sans plage : Q9 — ni commit « Q9 : », ni session\n" in rendus[2][1]), ("compteur : une fiche nommée sans plage se dit, et sort 1") + "\n" + str(rendus[2])
    recoupe = ("RECOUPE sss.jsonl ligne 23 (minutes) · outils 10,1 contre totalToolDuration 5,0 (écart +5,1 ; sans les "
               "4,8 fermées par une notification de fond : +0,4) · modèle 1,5 contre totalAPIDuration 2,0 (écart -0,5) "
               "· durée 12,8 contre totalDuration absent\n")
    assert (rendus[3] == (0, "\n".join(lignes) + "\n" + recoupe)), ("compteur --recoupe : la cost-state face au compteur, du startTime à sa dernière ligne horodatée ; un "
             "champ absent se dit") + "\n" + str(rendus[3][1])
    assert (declarees == (("vlp.py cocher", "calcul.py"), ())), ("RLA : les commandes longues se lisent au CHANTIER.md du projet, entre accents graves ; sans carte, aucune") + "\n" + str(declarees)
    assert (relance[0] == 0 and "Git 0 (0), publication 0 (0), relance 0 (1), reste 2 (3) · " in relance[1]), ("RLA : une commande longue déclarée tombe en relance, plus au reste — la suite et Git gardent leur sorte") + "\n" + str(relance)
