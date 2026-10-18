"""`noyau/clos.py` : la zone des chantiers clos, l'estimé et le prix, le recompte, la vigie — migré de
l'ancienne suite maison (REF58). Chaque `assert` garde le libellé d'origine de son `verifier` en tête de son message
(REF5), puis le diagnostic.
"""
import io
import json
import os
import shutil
import subprocess
import tempfile
from decimal import Decimal

import pytest
from aides import SCRIPTS, appel, ecrire, ligne_close, lire, mod, transcript

ICI = SCRIPTS     # le dossier des scripts, d'où ces tests viennent

OUVERT = "**Ouvert.** le 2026-10-08."


def test_total_clos(tmp_path):
    """Contrôler `total_clos` et `couts` sur des lignes closes, dont un « ? $ » d'une ancienne page."""
    assert (mod.total_clos(ligne_close(mod.arrondi(950))) == 950 and
             mod.total_clos(ligne_close(mod.arrondi(1500)) + ligne_close(mod.arrondi(950))) == 2450), ("total_clos : une ligne close sous 1 000") + "\n" + str((mod.total_clos(ligne_close(mod.arrondi(950))),
              mod.total_clos(ligne_close(mod.arrondi(1500)) + ligne_close(mod.arrondi(950)))))

    assert (mod.total_clos(ligne_close("non mesuré")) == 0 and
             mod.total_clos('<td class="mono"><strong>≈3,8k (3 812)</strong></td><td class="mono">≈0,00 $</td>') == 0), ("total_clos : ni plage, ni date, ni pied") + "\n" + str((mod.total_clos(ligne_close("non mesuré")),
              mod.total_clos('<td class="mono"><strong>≈3,8k (3 812)</strong></td><td class="mono">≈0,00 $</td>')))

    # Un « ? $ » de l'ancienne page traverse les soustractions de couts : P1 garde son coût
    # affiché, P2 prend le reste, en « ? » puisque la part de P1 en dollars est inconnue.
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        s = os.path.join(t, "s.jsonl")
        transcript(s, 3)
        gardes = []
        cout, total, hors = mod.couts([("P1", "a", True, [s]), ("P2", "b", True, [s])],
                                      {"P1": ("faite", None, "≈100,0k (100 000) · 1 tours · ? $")},
                                      "Coût du chantier : ≈100,0k (100 000) · 1 tours · ? $", gardes)
        assert (cout == {"P1": "≈100,0k (100 000) · 1 tours · ? $", "P2": "≈200,0k (200 000) · 2 tours · ? $"}
                 and total == (300000, 3, Decimal("1.5")) and hors is None and not gardes), ("couts : « ? $ » relu sans planter") + "\n" + str((cout, total, hors, gardes))


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


def hook(texte):
    o, e = io.StringIO(), io.StringIO()
    code = mod.main(["hook"], o, io.StringIO(texte), e)
    return code, o.getvalue(), e.getvalue()


def test_prix(tmp_path):
    """prix (chantier TAU3) : le `$` de la page de chaque clos posé en tête de sa cellule Tokens,
    le vieux joué à la louche recalé dessus, le vieil estimé marqué `(taux plat)` — sur un projet
    à deux clos, X mesuré en $, Y jamais mesuré."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tp:
        ecrire(os.path.join(tp, "CHANTIER.md"), "# Chantier courant\n\n- **contexte** : ctx/\n"
               "- **index** : ctx/00-INDEX.md\n")
        ecrire(os.path.join(tp, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n"
               "| `x.md` | chantier **clos** « X », `X1..X1` |\n"
               "| `y.md` | chantier **clos** « Y », `Y1..Y1` |\n")
        seule = ("# Chantier %s\n\n**CLOS** le 2026-01-06.\n\n**Fait.** %s1..%s1 (2026-01-06) : fini —"
                 " estimé 1 fiches ≈%s $ · cadré 1 · joué 1 fiches %s.\n\n## Le socle commun\n\n"
                 "## L'ordre des fiches\n\n<!-- FICHE:%s1 -->\n## %s1 [x] — Seule\n**Critère de fin**\n<!-- /FICHE -->\n")
        ecrire(os.path.join(tp, "ctx", "x.md"), seule % ("X", "X", "X", "25", "≈25 $", "X", "X"))
        ecrire(os.path.join(tp, "ctx", "y.md"), seule % ("Y", "Y", "Y", "10", "? $", "Y", "Y"))
        ecrire(os.path.join(tp, "ctx", "artefacts", "x.html"),
               '<p class="mono cout-total">Coût du chantier : ≈50,0k (50 000) · 5 tours · 12,34 $</p>\n'
               '<div class="bilan"><p>Estimé : estimé 1 fiches ≈25 $ · cadré 1 · joué 1 fiches ≈25 $</p></div>\n')
        ecrire(os.path.join(tp, "ctx", "artefacts", "y.html"),
               '<p class="mono cout-total">Coût du chantier : ≈20,0k (20 000) · 3 tours · ? $</p>\n')
        ecrire(os.path.join(tp, "ctx", "artefacts", "x.md"),
               "# X — notes et journal\n\n## Résultat\nFini\n\n## Notes\n\n## Journal\n\n## Bilan\n"
               "- Estimé : estimé 1 fiches ≈25 $ · cadré 1 · joué 1 fiches ≈25 $\n")
        fdr = os.path.join(tp, "ctx", "artefacts", "feuille-de-route.html")
        ecrire(fdr, '    <!-- ZONE:clos — test -->\n'
               '    <details class="clos">\n      <summary><span class="resume-clos">vieux</span></summary>\n'
               '      <table>\n        <tbody>\n'
               + ligne_close(mod.arrondi(50000)).replace("Q1–Q2", "X1")
               + ligne_close(mod.arrondi(20000)).replace("Q1–Q2", "Y1")
               + '        </tbody>\n        <tfoot>\n          <tr><td colspan="3">Total cumulé</td>'
                 '<td class="mono"><strong>vieux</strong></td><td class="mono">vieux</td></tr>\n        </tfoot>\n'
               '      </table>\n    </details>\n')
        disque = lambda: {os.path.relpath(os.path.join(r, n), tp): lire(os.path.join(r, n))
                          for r, _, ns in os.walk(tp) for n in ns}
        avant = disque()
        code, s = appel(["prix", tp, "--a-blanc"])
        ligne = "PRIX 1 posés · 0 déjà · 1 sans prix · 1 joués recalés · 1 estimés marqués · à blanc, rien d'écrit"
        ok = code == 0 and s.splitlines()[-1] == ligne
        ok = ok and "ÉCRIT" not in s
        ok = ok and disque() == avant
        assert (ok), ("TAU3 : --a-blanc annonce sans rien écrire") + "\n" + str(s)
        code, s = appel(["prix", tp])
        ligne = "PRIX 1 posés · 0 déjà · 1 sans prix · 1 joués recalés · 1 estimés marqués"
        ok = code == 0 and s.splitlines()[-1] == ligne
        assert (ok), ("TAU3 : premier passage — 1 posé (X, en $), 1 sans prix (Y, ? $) — mutant : marquer"
                 " (taux plat) sans regarder s'il y est déjà") + "\n" + str(s)
        feuille = lire(fdr)
        ok = '<td class="mono">12,34 $ · ≈50,0k (50 000)</td>' in feuille
        ok = ok and '<td class="mono">≈20,0k (20 000)</td>' in feuille
        assert (ok), ("TAU3 : prix posé en tête de la cellule Tokens de X, Y intacte") + "\n" + str(feuille)
        assert ('<strong>%s</strong></td><td class="mono">12,34 $ sur 1 clos mesurés</td>' % mod.arrondi(70000) in feuille
                 and '<span class="resume-clos">%s</span>' % mod.resume_clos(2, 70000, __import__("decimal").Decimal("12.34"), 1)
                 in feuille), ("TAU4 : pied et résumé de la feuille resommés au premier passage (X mesuré, Y non) —"
                 " mutant : le résumé et le pied non resommés, restés « vieux »") + "\n" + str(feuille)
        recale = "estimé 1 fiches ≈25 $ (taux plat) · cadré 1 · joué 1 fiches 12,34 $"
        x_md = lire(os.path.join(tp, "ctx", "x.md"))
        assert (recale + "." in x_md), ("TAU3 : joué de X recalé sur le prix mesuré, estimé marqué (taux plat), fichier de fiches") + "\n" + str(x_md)
        x_page = lire(os.path.join(tp, "ctx", "artefacts", "x.html"))
        ok = recale in x_page
        ok = ok and "50 000) · 5 tours · 12,34 $</p>" in x_page
        assert (ok), ("TAU3 : la page de X recalée pareil, le cout-total intact") + "\n" + str(x_page)
        x_abri = lire(os.path.join(tp, "ctx", "artefacts", "x.md"))
        assert (recale in x_abri), ("TAU3 : le .md d'abri de X recalé pareil") + "\n" + str(x_abri)
        y_md = lire(os.path.join(tp, "ctx", "y.md"))
        assert ("estimé 1 fiches ≈10 $ · cadré 1 · joué 1 fiches ? $" in y_md), ("TAU3 : Y sans prix mesuré — rien recalé, rien marqué") + "\n" + str(y_md)
        apres = disque()
        code, s = appel(["prix", tp])
        ligne = "PRIX 0 posés · 1 déjà · 1 sans prix · 0 joués recalés · 0 estimés marqués"
        ok = code == 0 and s.splitlines()[-1] == ligne
        ok = ok and "ÉCRIT" not in s
        ok = ok and disque() == apres
        assert (ok), ("TAU3 : relancé, plus rien à écrire — fichiers identiques à l'octet") + "\n" + str(s)
        code, s = appel(["prix", os.path.join(tp, "ctx")])
        assert (code == 1 and s.startswith("GARDE: pas de CHANTIER.md")), ("TAU3 : pas de CHANTIER.md, une GARDE") + "\n" + str(s)


def test_cout_a_clore(tmp_path, init_git):
    """Contrôler `cout --a-clore` et `recompter --a-clore` (chantier APC)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        pr, dep = os.path.join(t, ".claude", "projects"), os.path.join(t, "depot")
        os.makedirs(os.path.join(pr, "p"))
        for s_, heures_ in (("sss", [T0 + 200, T0 + 400, T0 + 700, T0 + 800, T0 + 1000]), ("ttt", [T0 + 200, T0 + 400, T0 + 700])):
            chemin_ = os.path.join(pr, "p", s_ + ".jsonl")
            transcript(chemin_, len(heures_), heures_)
            if s_ == "sss":
                lignes_ = [json.loads(l) for l in lire(chemin_).splitlines()]
                for k in (2, 4):
                    lignes_[k]["message"]["content"] = [{"type": "tool_use", "id": "t%d" % k, "name": "Bash", "input": {
                        "command": 'py "C:/k/scripts/vlp.py" clore . --livre x'}}]
                lignes_[3]["message"]["content"] = [{"type": "tool_use", "id": "t3", "name": "Bash",
                                                     "input": {"command": 'grep -n "clore" scripts/vlp.py'}}]
                ecrire(chemin_, "".join(json.dumps(l) + "\n" for l in lignes_))
        ecrire(os.path.join(dep, "q.md"), QFICHES % ("sss", "sss"))
        ecrire(os.path.join(dep, "r.md"), QFICHES % ("ttt", "ttt"))
        if not shutil.which("git"):
            pytest.skip("git absent — cout --a-clore n'est pas testé")
        else:
            env = dict(os.environ, GIT_CONFIG_GLOBAL=os.path.join(t, "gitconfig"), GIT_CONFIG_NOSYSTEM="1",
                       GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
            ecrire(env["GIT_CONFIG_GLOBAL"], "")
            init_git(dep)
            for d, sujet in ((100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"), (600, "Q2 : Brancher"),
                             (900, "Chantier Q clos : fini")):
                date = "%d +0000" % (T0 + d)
                subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", sujet], cwd=dep, check=True,
                               capture_output=True, env=dict(env, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date))
            # APC2 : recompter --a-clore, un projet par fichier (q.md et r.md portent le même préfixe Q),
            # inscrit 250 000 : ni le recompté (400 000) ni l'à-clore (300 000).
            for p_, f_ in (("pq", "q.md"), ("pr", "r.md")):
                ecrire(os.path.join(dep, p_, "CHANTIER.md"), "# C\n\n- **contexte** : ./\n- **index** : 00-INDEX.md\n")
                ecrire(os.path.join(dep, p_, "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n"
                       "| `../%s` | chantier **clos** « Q », `Q1..Q2` |\n" % f_)
                ecrire(os.path.join(dep, p_, "artefacts", "feuille-de-route.html"),
                       "    <!-- ZONE:clos — test -->\n      <table>\n        <tbody>\n"
                       + ligne_close(mod.arrondi(250000)) + "        </tbody>\n      </table>\n")
            garde_env = dict(os.environ)
            os.environ.update(HOME=t, USERPROFILE=t)
            try:
                (code, s), (code2, s2) = (appel(["cout", os.path.join(dep, "q.md"), "--a-clore"]),
                                          appel(["cout", os.path.join(dep, "r.md"), "--a-clore"]))
                (code3, s3), (code4, s4), (code5, s5) = (appel(["recompter", os.path.join(dep, "pq"), "--a-clore"]),
                                                         appel(["recompter", os.path.join(dep, "pr"), "--a-clore"]),
                                                         appel(["recompter", os.path.join(dep, "pq")]))
            finally:
                os.environ.clear()
                os.environ.update(garde_env)
            lignes_ = s.splitlines()
            assert (code == 0 and len(lignes_) == 7 and lignes_[4].startswith("TOTAL ")
                     and mod.triplet(lignes_[4])[:2] == (400000, 4)
                     and lignes_[5].startswith("à clore · ") and mod.triplet(lignes_[5])[:2] == (300000, 3)
                     and lignes_[6].startswith("après clore · ") and mod.triplet(lignes_[6])[:3] == (100000, 1, Decimal("0.50"))), ("cout --a-clore : TOTAL 4 tours, à clore 3, après clore 1 — le clore hors plage et le grep ignorés") + "\n" + str(s)
            assert (code2 == 0
                     and s2.splitlines()[-1] == "GARDE: aucun appel « vlp.py clore » dans la dernière plage hors fiches"
                     " — pas de ligne à clore" and "à clore ·" not in s2), ("cout --a-clore : sans appel clore, une GARDE et pas de ligne") + "\n" + str(s2)
            assert (code3 == 0 and s3.splitlines()[0] ==
                     "Q inscrit 250 000 · recompté 400 000 · écart +150 000 · découpe · à clore 300 000 · après clore 100 000"), ("recompter --a-clore : à clore 300 000, après clore = recompté − à clore — mutant :"
                     " après clore = recompté − inscrit") + "\n" + str(s3)
            assert (code4 == 0 and s4.splitlines()[0] ==
                     "Q inscrit 250 000 · recompté 300 000 · écart +50 000 · découpe · sans appel clore"), ("recompter --a-clore : sans appel clore, la ligne le dit") + "\n" + str(s4)
            assert (code5 == 0 and s5.splitlines()[0] ==
                     "Q inscrit 250 000 · recompté 400 000 · écart +150 000 · découpe"), ("recompter sans --a-clore : la ligne d'avant APC2") + "\n" + str(s5)


def test_recompter_essais(tmp_path):
    """Contrôler `recompter --essais`, avec et sans `--ecrire` (chantier ESD)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        pr, rc = os.path.join(t, ".claude", "projects"), os.path.join(t, "rc")
        os.makedirs(os.path.join(pr, "p"))
        for s_ in ("sss", "ttt"):
            transcript(os.path.join(pr, "p", s_ + ".jsonl"), 1, [T0 + 200])
        os.makedirs(os.path.join(pr, "C--x-sss-scratchpad-b1", "e", "subagents"))
        transcript(os.path.join(pr, "C--x-sss-scratchpad-b1", "e.jsonl"), 1, [T0 + 250])
        transcript(os.path.join(pr, "C--x-sss-scratchpad-b1", "e", "subagents", "agent-a1.jsonl"), 1, [T0 + 260])
        seule = ("# Chantier %s\n\n**CLOS** le 2026-01-06.\n\n## Le socle commun\n\n## L'ordre des fiches\n\n"
                 "<!-- FICHE:%s1 -->\n## %s1 [x] — Seule\n**Session** : %s\n**Critère de fin**\n<!-- /FICHE -->\n")
        ecrire(os.path.join(rc, "CHANTIER.md"), "# Chantier courant\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n")
        ecrire(os.path.join(rc, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n"
               "| `m.md` | chantier **clos** « M », `M1..M1` |\n| `n.md` | chantier **clos** « N », `N1..N1` |\n")
        ecrire(os.path.join(rc, "ctx", "m.md"), seule % ("M", "M", "M", "sss"))
        ecrire(os.path.join(rc, "ctx", "n.md"), seule % ("N", "N", "N", "ttt"))
        fr = os.path.join(rc, "ctx", "artefacts", "feuille-de-route.html")
        ecrire(fr, '    <!-- ZONE:clos — test -->\n      <table>\n        <tbody>\n'
               + "".join(ligne_close(c).replace("Q1–Q2", pl) for pl, c in (("M1", mod.arrondi(300000)), ("N1", mod.arrondi(2000))))
               + "        </tbody>\n      </table>\n")
        garde_env = dict(os.environ)
        os.environ.update(HOME=t, USERPROFILE=t)
        try:
            initial = lire(fr)
            simule = appel(["recompter", rc, "--essais"])
            avant = lire(fr)
            un = appel(["recompter", rc, "--essais", "--ecrire"])
            feuille_ = lire(fr)
            deux = appel(["recompter", rc, "--essais", "--ecrire"])
            resimule = appel(["recompter", rc, "--essais"])
        finally:
            os.environ.clear()
            os.environ.update(garde_env)
        l_ = simule[1].splitlines()
        assert (simule[0] == 0 and len(l_) == 3 and avant == initial
                 and l_[0].startswith("M inscrit 300 000 · essais 200 000 · ajout +200 000 · gardé — DÉCOUPE aucune (")
                 and l_[1].startswith("N inscrit 2 000 · essais 0 · ajout +0 · gardé — DÉCOUPE aucune (")
                 and l_[2] == "ESSAIS 2 clos · 1 reçoivent · inscrit 302 000 · avec essais 502 000 · ajout +200 000"), ("recompter --essais : le gardé DÉCOUPE aucune reçoit ses essais, sous-agent compris ; l'autre +0 ;"
                 " rien d'écrit") + "\n" + str(simule[1])
        assert (un[0] == 0 and un[1].splitlines()[-1] == "ÉCRIT 1 cellules · total 302 000 → 502 000"
                 and '<td class="mono">essais (ESD) +200 000 · ≈500,0k (500 000)</td>' in feuille_
                 and '<td class="mono">≈2,0k (2 000)</td>' in feuille_ and mod.total_clos(feuille_) == 502000), ("recompter --essais --ecrire : le chiffre + l'essai, la marque en tête, BRUT le relit") + "\n" + str(un[1] + feuille_)
        assert (deux[0] == 0 and lire(fr) == feuille_ and deux[1].splitlines()[-1] == "ÉCRIT 0 cellules · total 502 000 → 502 000"), ("recompter --essais --ecrire, second passage : cellule identique — mutant : ignorer la marque") + "\n" + str(deux[1] + lire(fr))
        assert (resimule[0] == 0 and resimule[1].splitlines()[0].startswith("M inscrit 500 000 · essais 200 000 · ajout +0 · ")
                 and resimule[1].splitlines()[0].endswith(" · déjà ajoutés (ESD)")
                 and resimule[1].splitlines()[-1].endswith(" · 0 reçoivent · inscrit 502 000 · avec essais 502 000 · ajout +0")), ("recompter --essais après écriture : la simulation dit +0, déjà ajoutés") + "\n" + str(resimule[1])
        # La règle du découpé, en fonction pure : les essais sans passer le recompté.
        assert ([mod.ajout_essais("x", 100, 150, "découpe", 80), mod.ajout_essais("x", 100, 300, "découpe", 80),
                  mod.ajout_essais("x", 100, 90, "découpe", 80), mod.ajout_essais("x", 100, None, "gardé — sans session", 80),
                  mod.ajout_essais(mod.MARQUE_ESSAIS + "+5 · (105)", 105, None, "gardé — DÉCOUPE aucune (r)", 5)]
                 == [50, 80, 0, 0, 0]), ("ajout_essais : découpé borné par l'écart ; autre gardé, rien ; marque, rien") + "\n" + ""
        # Dette d'ESD : un `recompter --ecrire` sur une cellule marquée ESD garde la marque en tête.
        marques = [mod.marquer("essais (ESD) +200 000 · recompté (REC), était 650 000 · ≈850,0k (850 000)", 850000, 900000, "découpe"),
                   mod.marquer("essais (ESD) +50 000 · ≈700,0k (700 000)", 700000, 750000, "découpe")]
        assert (marques == [
            "essais (ESD) +200 000 · recompté (REC), était 650 000 · ≈900,0k (900 000)",
            "essais (ESD) +50 000 · recompté (REC), était 700 000 · ≈750,0k (750 000)"]), ("marquer : la marque ESD reste en tête — mutant : la marque ESD perdue") + "\n" + str(marques)


def test_recompter_un_clos(tmp_path):
    """`recompter --clos A --ecrire` (PRP3) : les quatre copies du coût de A écrites, B intact —
    `recompte` simulé (90 000 tokens, 7,50 $), la découpe a ses propres tests."""
    from decimal import Decimal
    with tempfile.TemporaryDirectory(dir=tmp_path) as tp:
        ecrire(os.path.join(tp, "CHANTIER.md"), "# Chantier courant\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n")
        ecrire(os.path.join(tp, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n"
               "| `a.md` | chantier **clos** « A », `A1..A1` |\n| `b.md` | chantier **clos** « B », `B1..B1` |\n")
        joue = "estimé 1 fiches ≈25 $ · cadré 1 · joué 1 fiches 12,34 $"
        for x in ("A", "B"):
            ecrire(os.path.join(tp, "ctx", x.lower() + ".md"),
                   "# Chantier %s\n\n**CLOS** le 2026-01-06.\n\n**Fait.** %s1..%s1 (2026-01-06) : fini — %s.\n\n"
                   "## Le socle commun\n\n<!-- FICHE:%s1 -->\n## %s1 [x] — Seule\n**Critère de fin**\n<!-- /FICHE -->\n"
                   % (x, x, x, joue, x, x))
            ecrire(os.path.join(tp, "ctx", "artefacts", x.lower() + ".html"),
                   '<p class="mono cout-total">Coût : 12,34 $</p>\n  <!-- ZONE:bilan -->\n  <section>\n'
                   '    <div class="bilan">\n      <p>Estimé : %s</p>\n    </div>\n  </section>\n' % joue)
            ecrire(os.path.join(tp, "ctx", "artefacts", x.lower() + ".md"),
                   "# %s — notes et journal\n## Résultat\nFini\n## Notes\n## Journal\n## Bilan\n- Estimé : %s\n" % (x, joue))
        fdr = os.path.join(tp, "ctx", "artefacts", "feuille-de-route.html")
        ecrire(fdr, '    <!-- ZONE:clos — test -->\n      <table>\n        <tbody>\n'
               + "".join(ligne_close("12,34 $ · " + mod.arrondi(50000)).replace("Q1–Q2", pl) for pl in ("A1", "B1"))
               + "        </tbody>\n      </table>\n")
        b = [os.path.join(tp, "ctx", n) for n in ("b.md", os.path.join("artefacts", "b.html"), os.path.join("artefacts", "b.md"))]
        avant_b = [lire(c) for c in b]
        vrai = mod.noyau.clos.recompte
        mod.noyau.clos.recompte = lambda chemin: (90000, "découpe", 0, Decimal("7.50"))
        try:
            absent = appel(["recompter", tp, "--clos", "Z", "--ecrire"])
            initiale = lire(fdr)
            un = appel(["recompter", tp, "--clos", "A", "--ecrire"])
            copies_a = [lire(os.path.join(tp, "ctx", n)) for n in
                        ("a.md", os.path.join("artefacts", "a.html"), os.path.join("artefacts", "a.md"))]
            feuille_ = lire(fdr)
            deux = appel(["recompter", tp, "--clos", "A", "--ecrire"])
        finally:
            mod.noyau.clos.recompte = vrai
        assert (absent[0] == 1 and absent[1].startswith("GARDE: clos Z absent")
                 and initiale.count("12,34 $ · %s" % mod.arrondi(50000)) == 2), ("PRP3 : --clos absent de ZONE:clos, une GARDE, rien d'écrit") + "\n" + str(absent[1])
        neuf = "joué 1 fiches 7,50 $"
        assert (un[0] == 0 and un[1].splitlines()[-1] == "COPIES 4 écrites · 0 inchangées · 0 introuvables"
                 and un[1].splitlines()[0].startswith("A inscrit 50 000 · recompté 90 000")
                 and '<td class="mono">7,50 $ · recompté (REC), était 50 000 · %s</td>' % mod.arrondi(90000) in feuille_
                 and all(neuf in c for c in copies_a)), ("PRP3 : recompter --clos A --ecrire — 4 copies écrites pour A (archive, **Fait.**, ZONE:bilan, abri)"
                 " — mutant : sauter l'écriture de la ZONE:bilan") + "\n" + str(un[1] + "\n".join(copies_a) + feuille_)
        assert ([lire(c) for c in b] == avant_b
                 and '<td class="mono">B1</td>' in feuille_
                 and feuille_.count('<td class="mono">12,34 $ · %s</td>' % mod.arrondi(50000)) == 1), ("PRP3 : B n'a pas bougé — 0 copie changée (fiches, page, abri, cellule d'archive)") + "\n" + str(feuille_)
        assert (deux[0] == 0 and deux[1].splitlines()[-1] == "COPIES 0 écrites · 4 inchangées · 0 introuvables"
                 and lire(fdr) == feuille_), ("PRP3 : relancé, les quatre copies inchangées") + "\n" + str(deux[1])


GABARIT_FEUILLE = os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html")


ETAT_Z = ("# État\n\n## TODO\n\n| n° | Chantier | Apport | Coût | Décidé |\n|---|---|---|---|---|\n"
          "| 1 | un truc | utile | bas | 2026-01-02 |\n")


CARTE_Z = ("# Chantier courant\n\n- **alias** : z\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
           "- **fichier d'état** : ctx/08-etat.md\n- **artefact du chantier** : aucun\n")


def test_page_clos(tmp_path):
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        proj = os.path.join(t, "proj")
        ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_Z
               + "\nLettres de fiche déjà prises : A (Arc). Un nouveau chantier en choisit une autre.\n")
        ecrire(os.path.join(proj, "ctx", "08-etat.md"), ETAT_Z)
        ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n"
               "| `x.md` | chantier **clos** « X », `X1..X1` |\n| `y.md` | chantier **clos** « Y », `Y1..Y1` |\n"
               "| `30-a.md` | chantier **ouvert** « A », `A1..A1` |\n")
        ecrire(os.path.join(proj, "ctx", "30-a.md"), "# Chantier A\n\n" + OUVERT + "\n\n**Fait.** Rien.\n\n## Le socle commun\n\n"
               "## L'ordre des fiches\n\n<!-- FICHE:A1 -->\n## A1 [x] — Seule\n**Critère de fin**\n<!-- /FICHE -->\n")
        gabarit = lire(GABARIT_FEUILLE)
        fdr = os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html")
        ecrire(fdr, gabarit)
        d, f = mod.zone(gabarit, "clos", "<tbody>\n", "        </tbody>")
        deux = (ligne_close("12,34 $ · " + mod.arrondi(50000)).replace("Q1–Q2", "X1")
                + ligne_close(mod.arrondi(20000)).replace("Q1–Q2", "Y1"))
        archive = os.path.join(proj, "ctx", "artefacts", mod.ARCHIVE_CLOS)
        ecrire(archive, gabarit[:d] + deux + gabarit[f:])
        assert (os.path.normpath(mod.page_clos(proj)) == os.path.normpath(archive)), ("ARC1 : page_clos rend l'archive") + "\n" + str(mod.page_clos(proj))
        code, s = appel(["recompter", proj])
        assert (code == 0 and "RECOMPTE 2 clos" in s), ("ARC1 : recompter lit les deux clos de l'archive") + "\n" + str(s)
        code, s = appel(["prix", proj, "--a-blanc"])
        assert (code == 0 and "2 sans prix" in s), ("ARC1 : prix lit l'archive") + "\n" + str(s)
        code, s = appel(["clore", proj, "--livre", "fini", "--tokens", "1000"])
        lignes_a, lignes_f = mod.lignes_clos(lire(archive)), mod.lignes_clos(lire(fdr))
        assert (code == 0 and len(lignes_a) == 3 and "A1" in lignes_a[0] and not lignes_f), ("ARC1 : clore ajoute sa ligne en tête de l'archive, la feuille n'en a aucune") + "\n" + str(s)
        svg = os.path.join(proj, "ctx", "artefacts", mod.COUTS_SVG)
        barres = lire(svg).count('class="barre"') if os.path.isfile(svg) else 0
        assert (barres == 3 and 'data-couts=' in lire(fdr)), ("ARC1 : couts.svg à côté de la feuille, trois barres lues dans l'archive") + "\n" + str("%d barres\n%s" % (barres, s))
        assert ("\nLIRE vlp.css vlp.js couts.svg\n" in s), ("REF29 : clore dit LIRE avec couts.svg joint — mutant : ligne LIRE retirée") + "\n" + str(s)
        ecrire(os.path.join(proj, "ctx", "31-b.md"), "# Chantier B\n\n**Fait.** Rien.\n\n## Le socle commun\n\n"
               "## L'ordre des fiches\n\n<!-- FICHE:B1 -->\n## B1 [ ] — Seule\n**Critère de fin**\n<!-- /FICHE -->\n")
        code, s = appel(["ouvrir", proj, "--fiches", "ctx/31-b.md", "--titre", "b", "--estime-fiches", "1"])
        assert ("estimé 1 fiches ≈12 $" in s), ("ARC1 : le prix moyen d'ouvrir se lit dans l'archive") + "\n" + str(s)


def avec_style_inline(html):
    """Une page déjà régénérée (donc liée à vlp.css), avec son <style> d'avant PLI3
    remis en place — comme une page publiée avant ce chantier, jamais régénérée depuis."""
    css = io.open(os.path.join(ICI, "..", "templates", "vlp.css"), encoding="utf-8").read()
    return html.replace('<link rel="stylesheet" href="vlp.css">', "<style>\n%s</style>" % css, 1)


def test_vigile(tmp_path):
    """vigile (chantier VID1) : une page cassée ne part pas — commentaire ouvert, aucun style, aucun bloc."""
    def hook(d):
        o = io.StringIO()
        code = mod.main(["vigile"], o, io.StringIO(d if isinstance(d, str) else json.dumps(d)))
        return code, o.getvalue()

    with tempfile.TemporaryDirectory(dir=tmp_path) as tvg:
        saine = os.path.join(tvg, "saine.html")
        ecrire(saine, "<!-- tête fermée -->\n<html><head><style>p{}</style></head>"
                      "<body><h1>Titre</h1><p>Un texte.</p></body></html>\n")
        cairn = os.path.join(tvg, "cairn.html")
        ecrire(cairn, "<!-- Gabarit : remplis les <…>\n<html><head><style>p{}</style></head>"
                      "<body><h1>Titre</h1><p>Un texte.</p></body></html>\n")
        sans_style = os.path.join(tvg, "sans-style.html")
        ecrire(sans_style, "<html><body><p>Un texte.</p></body></html>\n")
        sans_bloc = os.path.join(tvg, "sans-bloc.html")
        ecrire(sans_bloc, "<html><head><style>p{}</style></head><body><script>x()</script></body></html>\n")
        lien = os.path.join(tvg, "lien.html")
        ecrire(lien, '<html><head><link rel="stylesheet" href="vlp.css"></head><body><p>Un texte.</p></body></html>\n')

        code, s = appel(["vigile", saine])
        assert ((code, s) == (0, "PAGE SAINE 2 blocs\n")), ("vigile : page saine, PAGE SAINE 2 blocs") + "\n" + str(s)
        code, s = appel(["vigile", cairn])
        assert (code == 1 and "GARDE: %s — commentaire ouvert ligne 1" % cairn in s), ("vigile : page Cairn, commentaire ouvert ligne 1 — mutant : ne plus le chercher") + "\n" + str(s)
        assert ("aucun style" in s and "aucun bloc de texte visible" in s and s.count("GARDE:") == 3), ("vigile : page Cairn, style et texte cachés dans le commentaire comptent pour rien") + "\n" + str(s)
        code, s = appel(["vigile", sans_style])
        assert (code == 1 and s == "GARDE: %s — aucun style (ni balise style, ni link rel=\"stylesheet\")\n"
                 % sans_style), ("vigile : page sans style, GARDE — mutant : l'accepter") + "\n" + str(s)
        code, s = appel(["vigile", sans_bloc])
        assert (code == 1 and s == "GARDE: %s — aucun bloc de texte visible\n" % sans_bloc), ("vigile : page sans bloc, GARDE — mutant : accepter zéro bloc") + "\n" + str(s)
        code, s = appel(["vigile", lien])
        assert ((code, s) == (0, "PAGE SAINE 1 blocs\n")), ("vigile : page stylée par un seul link, saine") + "\n" + str(s)
        code, s = appel(["vigile", os.path.join(tvg, "absente.html")])
        assert (code == 1 and s.startswith("GARDE: introuvable")), ("vigile : fichier absent, GARDE introuvable") + "\n" + str(s)

        pub = {"hook_event_name": "PreToolUse", "tool_name": "Artifact"}
        code, s = hook(dict(pub, tool_input={"file_path": cairn}))
        assert (code == 0 and '"permissionDecision": "deny"' in s and json.dumps(cairn)[1:-1] in s
                 and "commentaire ouvert" in s and "aucun style" in s and "aucun bloc" in s), ("vigile : hook, page Cairn refusée, raison nomme fichier et défauts") + "\n" + str(s)
        code, s = hook(dict(pub, tool_input={"file_path": "sans-style.html"}, cwd=tvg))
        assert ('"permissionDecision": "deny"' in s), ("vigile : hook, chemin relatif au cwd refusé") + "\n" + str(s)
        assert (hook(dict(pub, tool_input={"file_path": saine})) == (0, "")), ("vigile : hook, page saine, muet") + "\n" + ""
        assert (hook(dict(pub, tool_input={"file_path": cairn, "asset": True})) == (0, "")), ("vigile : hook, asset vrai, muet") + "\n" + ""
        assert (hook({"hook_event_name": "PreToolUse", "tool_name": "Bash",
                                                       "tool_input": {"command": "cat %s" % cairn}}) == (0, "")), ("vigile : hook, un Bash, muet") + "\n" + ""
        md = os.path.join(tvg, "page.md")
        ecrire(md, "<!-- ouvert\n")
        assert (hook(dict(pub, tool_input={"file_path": md})) == (0, "")), ("vigile : hook, un .md, muet") + "\n" + ""
        assert (hook("pas du json") == (0, "") and hook('[1, "x"]') == (0, "")), ("vigile : hook, JSON illisible, muet") + "\n" + ""
        assert (hook(dict(pub, tool_input={"file_path": os.path.join(tvg, "absente.html")})) == (0, "")), ("vigile : hook, fichier illisible, muet") + "\n" + ""


def projet_clos(dossier, liens=()):
    """Un projet à trois clos A, B, C : A et B à l'ancien format, C déjà lié à vlp.css ; `liens` :
    (plage, url) de lignes de ZONE:clos à lien, en plus d'une ligne sans lien par clos."""
    seule = ("# Chantier %s\n\n**CLOS** le 2026-01-06.\n\n## Le socle commun\n\n## L'ordre des fiches\n\n"
             "<!-- FICHE:%s1 -->\n## %s1 [x] — Seule\n**Critère de fin**\n<!-- /FICHE -->\n")
    ecrire(os.path.join(dossier, "CHANTIER.md"), "# Chantier courant\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n")
    ecrire(os.path.join(dossier, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n"
           + "".join("| `%s.md` | chantier **clos** « %s », `%s1..%s1` |\n" % (x.lower(), x, x, x) for x in "ABC"))
    for x in "ABC":
        fiches = os.path.join(dossier, "ctx", "%s.md" % x.lower())
        page = os.path.join(dossier, "ctx", "artefacts", "%s.html" % x.lower())
        ecrire(fiches, seule % (x, x, x))
        appel(["page", fiches, page, "--creer", "--projet", "P", "--titre", x, "--resultat", "R"])
        if x != "C":
            ecrire(page, avec_style_inline(lire(page)))
    rangs = [ligne_close(mod.arrondi(1500)).replace("Q1–Q2", "%s1" % x) for x in "ABC" if "%s1" % x not in dict(liens)]
    rangs += [ligne_close(mod.arrondi(1500)).replace("Q1–Q2", pl).replace("<td>Test ", '<td><a href="%s">Test</a> ' % u)
              for pl, u in liens]
    ecrire(os.path.join(dossier, "ctx", "artefacts", "feuille-de-route.html"),
           '    <!-- ZONE:clos — test -->\n      <table>\n        <tbody>\n' + "".join(rangs)
           + "        </tbody>\n      </table>\n")


def test_repeindre(tmp_path):
    """repeindre (chantier HAB2) : les pages closes d'un projet, repeintes par page --forme."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as trp:
        projet_clos(trp)
        disque = lambda: {os.path.relpath(os.path.join(r, n), trp): lire(os.path.join(r, n))
                          for r, _, ns in os.walk(trp) for n in ns}
        avant = disque()
        code, s = appel(["repeindre", trp, "--a-blanc"])
        assert (code == 0 and "2 repeintes · 0 avec lien · 2 sans lien · 0 refusées · 1 déjà" in s
                 and disque() == avant), ("HAB2 : --a-blanc annonce 2 repeintes et ne change aucun octet") + "\n" + str(s)
        code, s = appel(["repeindre", trp])
        pages = [lire(os.path.join(trp, "ctx", "artefacts", "%s.html" % x)) for x in "ab"]
        assert (code == 0 and s.splitlines()[-1] == "REPEINDRE 2 repeintes · 0 avec lien · 2 sans lien"
                 " · 0 refusées · 1 déjà · 0 sans page" and s.count("REPEINTE ") == 2
                 and all("<style>" not in p and 'href="vlp.css"' in p for p in pages)), ("HAB2 : repeindre, 2 repeintes · 0 avec lien · 2 sans lien · 0 refusées, 1 déjà"
                 " — mutant : ne pas filtrer les pages déjà au format") + "\n" + str(s)
        code, s = appel(["repeindre", trp])
        assert (code == 0 and "0 repeintes" in s and "3 déjà" in s), ("HAB2 : relancé, 0 repeintes, 3 déjà") + "\n" + str(s)
        code, s = appel(["repeindre", os.path.join(trp, "ctx")])
        assert (code == 1 and s.startswith("GARDE: pas de CHANTIER.md")), ("HAB2 : pas de CHANTIER.md, une GARDE") + "\n" + str(s)
