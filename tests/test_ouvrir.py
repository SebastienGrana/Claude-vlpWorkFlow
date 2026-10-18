"""`noyau/ouvrir.py` : `ouvrir`, l'estimé d'un chantier, sa marque, les chevrons de la feuille — migré de
l'ancienne suite maison (REF51). Chaque `assert` garde le libellé d'origine de son `verifier` en tête de son message
(REF5), puis le diagnostic.
"""
import io
import os
import re
import shutil
import subprocess
import tempfile

import pytest
from aides import SCRIPTS, appel, ecrire, mod

ICI = SCRIPTS     # le dossier des scripts, d'où ces tests viennent

OUVERT = "**Ouvert.** le 2026-10-08."


def ouvert(texte):
    """`texte` d'un fichier de fiches, la marque d'ouverture sous son titre `# Chantier `, comme la pose `vlp.py
    ouvrir` : `courant_de` le lit (NUI31)."""
    return re.sub(r"^(# Chantier [^\n]*\n)", r"\g<1>\n%s\n" % OUVERT, texte, count=1, flags=re.M)


OUVERT_LIGNE = mod.OUVERT_LIGNE   # la seconde valeur d'`OUVERT` dans l'ancienne suite maison, lue par les groupes de sa fin


def ouvert_ligne(texte):
    """`ouvert`, tel que les groupes de la fin de l'ancienne suite maison l'appelaient : le gabarit `OUVERT_LIGNE` inséré
    brut, `%s` compris."""
    return re.sub(r"^(# Chantier [^\n]*\n)", r"\g<1>\n%s\n" % OUVERT_LIGNE, texte, count=1, flags=re.M)


def sans_chantier(racine, carte):
    """Plus aucun chantier ouvert dans `racine` : CHANTIER.md réécrit avec `carte`, et la marque d'ouverture que
    `ouvrir` a posée retirée des fiches — la ligne seule à « aucun » ne ferme plus rien (NUI23)."""
    ecrire(os.path.join(racine, "CHANTIER.md"), carte)
    ctx = os.path.join(racine, "ctx")
    for nom in os.listdir(ctx):
        chemin = os.path.join(ctx, nom)
        if nom.endswith(".md") and os.path.isfile(chemin):
            texte = mod.lire(chemin)
            ecrire(chemin, re.sub(r"\n\n\*\*Ouvert\.\*\* le [^\n]*", "", texte))


OUVERT_DU_JOUR = mod.OUVERT_LIGNE % __import__("datetime").date.today().isoformat()


def test_ouvrir(tmp_path):
    """Contrôler `ouvrir` : bilan, fichier de fiches posé, ligne de l'état."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        lire = lambda c: open(c, encoding="utf-8").read()
        os.environ["CLAUDE_CODE_SESSION_ID"] = "cadre"     # la session du cadrage, que `ouvrir` note
        carte_o = ("# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
                   "- **artefact du chantier** : %s\n")
        ecrire(os.path.join(t, "CHANTIER.md"), carte_o % "aucun")
        ecrire(os.path.join(t, "ctx", "00-INDEX.md"), "| Fichier | Lire |\n|---|---|\n| `10-e.md` | on relit |\n| `05-d.md` | vieux |\n\nFin.\n")
        ecrire(os.path.join(t, "CLAUDE.md"), "| La tâche | Ouvrir |\n|---|---|\n| modifier | x |\n| relire le chantier E (e) | `ctx/10-e.md` — chantier **clos** |\n| relire un chantier clos | `ctx/00-INDEX.md` |\n")
        ecrire(os.path.join(t, "ctx", "30-q.md"), "# Chantier Q — Un titre\n\n## Q1 [ ] — a\n## Q2 [ ] — b\n")
        code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un `titre`"])
        carte_lue, index_lu, claude_lu = lire(os.path.join(t, "CHANTIER.md")), lire(os.path.join(t, "ctx", "00-INDEX.md")), lire(os.path.join(t, "CLAUDE.md"))
        assert (code == 0 and s == "OUVERT Q Q1..Q2 · index +1 · routage +1 · session +1 · artefact aucun — %s\n" % t), ("ouvrir : bilan") + "\n" + str(s)
        assert (lire(os.path.join(t, "ctx", "30-q.md"))
                 == "# Chantier Q — Un titre\n\n%s\n\n**Session** : cadre\n\n## Q1 [ ] — a\n## Q2 [ ] — b\n"
                 % (mod.OUVERT_LIGNE % __import__("datetime").date.today().isoformat())), ("ouvrir : la session du cadrage, avant la première ligne ##") + "\n" + str(lire(os.path.join(t, "ctx", "30-q.md")))
        assert ("fichier de fiches" not in carte_lue and "- **artefact du chantier** : aucun\n" in carte_lue
                 and mod.courant_de(t) == "ctx/30-q.md"), ("ouvrir : CHANTIER.md, l'artefact seul — plus de ligne du fichier courant (NUI31)") + "\n" + str(carte_lue)
        assert ("| `10-e.md` | on relit |\n| `30-q.md` | on joue une fiche `Q*` — chantier **ouvert** « Un `titre` », `Q1..Q2` |\n| `05-d.md`" in index_lu), ("ouvrir : index, après le plus grand numéro") + "\n" + str(index_lu)
        assert ("**clos** |\n| jouer une fiche du chantier Q (un `titre`) | `ctx/30-q.md` — chantier **ouvert**, par `/vlp:tache Q<n>` |\n| relire" in claude_lu), ("ouvrir : routage, avant « relire un chantier clos »") + "\n" + str(claude_lu)
        code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un `titre`", "--artefact", "https://exemple/q"])
        assert (code == 0 and "index +0 · routage +0 · session +0 · artefact https://exemple/q" in s
                 and lire(os.path.join(t, "ctx", "30-q.md")).count("**Session**") == 1
                 and lire(os.path.join(t, "CLAUDE.md")) == claude_lu and lire(os.path.join(t, "ctx", "00-INDEX.md")) == index_lu
                 and "**artefact du chantier** : https://exemple/q" in lire(os.path.join(t, "CHANTIER.md"))), ("ouvrir : relance, artefact seul") + "\n" + str(s)
        avant = lire(os.path.join(t, "CHANTIER.md"))
        code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un `titre`"])
        assert (code == 0 and lire(os.path.join(t, "CHANTIER.md")) == avant), ("ouvrir : relance sans artefact, rien ne change") + "\n" + str(s)
        ecrire(os.path.join(t, "ctx", "31-r.md"), "# Chantier R — r\n\n## R1 [ ] — a\n")
        code, s = appel(["ouvrir", t, "--fiches", "ctx/31-r.md", "--titre", "r"])
        assert (code == 1 and s.startswith("GARDE: un chantier est déjà ouvert")
                 and lire(os.path.join(t, "CHANTIER.md")) == avant), ("ouvrir : autre chantier ouvert, refus") + "\n" + str(s)
        ecrire(os.path.join(t, "ctx", "30-q.md"), "# Chantier Q — Un titre\n\n## Q1 [ ] — a\n## Q2 [ ] — b\n## Q3 [ ] — c\n")
        # Relancé avec un autre titre : seule la plage suit, sur la même et unique ligne.
        code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un autre titre"])
        index_q = [l for l in lire(os.path.join(t, "ctx", "00-INDEX.md")).split("\n") if l.startswith("| `30-q.md` |")]
        assert (code == 0 and "OUVERT Q Q1..Q3 · index ~1 · routage +0 · session +1" in s
                 and index_q == ["| `30-q.md` | on joue une fiche `Q*` — chantier **ouvert** « Un `titre` », `Q1..Q3` |"]
                 and mod.courant_de(t) == "ctx/30-q.md"), ("ouvrir : relancé, la plage de l'index suit le fichier") + "\n" + str(s + repr(index_q))
        index_main = lire(os.path.join(t, "ctx", "00-INDEX.md")).replace("chantier **ouvert** « Un `titre` », `Q1..Q3`", "à la main `Q1..Q2`")
        ecrire(os.path.join(t, "ctx", "00-INDEX.md"), index_main)
        code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un `titre`"])
        assert (code == 0 and "index +0" in s
                 and lire(os.path.join(t, "ctx", "00-INDEX.md")) == index_main), ("ouvrir : relancé, une ligne d'index écrite à la main reste") + "\n" + str(s)
        sans_chantier(t, carte_o % "aucun")
        os.remove(os.path.join(t, "CLAUDE.md"))
        code, s = appel(["ouvrir", t, "--fiches", "ctx/31-r.md", "--titre", "r"])
        assert (code == 0 and "GARDE: CLAUDE.md introuvable" in s
                 and "routage +0" in s and "index +1" in s and mod.courant_de(t) == "ctx/31-r.md"), ("ouvrir : CLAUDE.md absent, garde, le reste écrit") + "\n" + str(s)
        sans_chantier(t, carte_o % "aucun")
        ecrire(os.path.join(t, "ctx", "32-s.md"), "# Chantier S — s\n\n**CLOS** le 2026-01-01. Ne se rejoue pas.\n\n## S1 [x] — a\n")
        code, s = appel(["ouvrir", t, "--fiches", "ctx/32-s.md", "--titre", "s"])
        assert (code == 1 and s.startswith("GARDE: ctx/32-s.md porte **CLOS**")
                 and "aucun" in lire(os.path.join(t, "CHANTIER.md"))), ("ouvrir : fichier CLOS, refus sans écrire") + "\n" + str(s)
        # Un vrai fichier : la session va avant `## Le socle commun`, jamais entre le marqueur d'une
        # fiche et son titre — la fiche extraite n'en porte pas. Déjà sur une ligne `**Session**`, même
        # d'une fiche, elle n'est pas redoublée ; un id vide ne note rien.
        vrai = ("# Chantier T — t\n\nÀ quoi il sert.\n\n## Le socle commun\n\n## L'ordre des fiches\n\n"
                "<!-- FICHE:T1 -->\n## T1 [ ] — a\n<!-- /FICHE -->\n")
        for nom, texte in (("33-t.md", vrai), ("34-u.md", "# Chantier U — u\n\n## U1 [x] — a\n**Session** : cadre\n"),
                           ("35-v.md", "# Chantier V — v\n\n## V1 [ ] — a\n")):
            ecrire(os.path.join(t, "ctx", nom), texte)
        sans_chantier(t, carte_o % "aucun")
        code, s = appel(["ouvrir", t, "--fiches", "ctx/33-t.md", "--titre", "t"])
        lu_o = lire(os.path.join(t, "ctx", "33-t.md"))
        assert (code == 0 and "· session +1 ·" in s
                 and lu_o == vrai.replace("## Le socle commun", "**Session** : cadre\n\n## Le socle commun")
                                 .replace("# Chantier T — t\n\n", "# Chantier T — t\n\n%s\n\n" % OUVERT_DU_JOUR)
                 and "**Session**" not in appel(["extraire", os.path.join(t, "ctx", "33-t.md"), "T1"])[1]), ("ouvrir : un vrai fichier, la session avant le socle, hors de toute fiche") + "\n" + str(s + lu_o)
        sans_chantier(t, carte_o % "aucun")
        code, s = appel(["ouvrir", t, "--fiches", "ctx/34-u.md", "--titre", "u"])
        assert (code == 0 and "· session +0 ·" in s
                 and lire(os.path.join(t, "ctx", "34-u.md")).count("**Session**") == 1), ("ouvrir : session déjà sur une ligne d'une fiche, pas redoublée") + "\n" + str(s)
        sans_chantier(t, carte_o % "aucun")
        os.environ["CLAUDE_CODE_SESSION_ID"] = ""
        code, s = appel(["ouvrir", t, "--fiches", "ctx/35-v.md", "--titre", "v"])
        assert (code == 0 and "· session +0 ·" in s
                 and lire(os.path.join(t, "ctx", "35-v.md")) == "# Chantier V — v\n\n%s\n\n## V1 [ ] — a\n" % OUVERT_DU_JOUR), ("ouvrir : id vide, rien de noté") + "\n" + str(s)
        os.environ.pop("CLAUDE_CODE_SESSION_ID", None)


# Pas sous tmp_path : son nom porterait « estime », que ce test cherche absent de la sortie.
def test_estime():
    with tempfile.TemporaryDirectory() as te:
        # `ouvrir --estime-fiches` (chantier EST) : A1–A3 à 3,00 $ et B1 à 1,00 $ (4 fiches, 4,00 $)
        # font 1,00 $/fiche — le prix mesuré des lignes, pas les tokens (chantier TAU). D1–D2, mesurée
        # en tokens mais sans `$`, ne compte ni dans la somme ni dans les fiches de la moyenne — mutant :
        # la compter comme 0 $ ferait 4,00 $ sur 6 fiches, ≈0,67 $/fiche au lieu de ≈1,00 $/fiche. La
        # ligne non mesurable (E) ne compte pas non plus.
        lire = lambda c: open(c, encoding="utf-8").read()
        os.environ["CLAUDE_CODE_SESSION_ID"] = ""
        rang = ('          <tr>\n            <td>x</td>\n            <td class="mono">%s</td><td class="mono">2026-01-01</td>\n'
                '            <td class="mono">%s</td>\n            <td>y</td>\n          </tr>\n')
        carte_e = ("# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
                   "- **artefact du chantier** : aucun\n")
        fiches_e = "# Chantier Q — q\n\n**Fait.** Rien.\n\n## Q1 [ ] — a\n"
        ecrire(os.path.join(te, "CHANTIER.md"), carte_e)
        ecrire(os.path.join(te, "ctx", "30-q.md"), fiches_e)
        code, s = appel(["ouvrir", te, "--fiches", "ctx/30-q.md", "--titre", "q", "--estime-fiches", "2"])
        assert (code == 0 and "GARDE: feuille de route introuvable" in s
                 and "estimé" not in s.split("\n")[-2] and "**Estimé.**" not in lire(os.path.join(te, "ctx", "30-q.md"))
                 and mod.courant_de(te) == "ctx/30-q.md"), ("EST1 : sans feuille, GARDE, le reste écrit") + "\n" + str(s)
        ecrire(os.path.join(te, "ctx", "artefacts", "feuille-de-route.html"),
               "<!-- ZONE:clos -->\n<tbody>\n" + rang % ("A1–A3", "3,00 $ · ≈3,0M (3 000 000)")
               + rang % ("B1", "1,00 $ · ≈1,0M (1 000 000)") + rang % ("D1–D2", "≈2,0M (2 000 000)")
               + rang % ("E1–E8", "non recompté — fichier introuvable · non mesurable") + "</tbody>\n")
        code, s = appel(["ouvrir", te, "--fiches", "ctx/30-q.md", "--titre", "q", "--estime-fiches", "2"])
        lu_e = lire(os.path.join(te, "ctx", "30-q.md"))
        assert (code == 0 and "· estimé 2 fiches ≈2,00 $ — " in s
                 and "\n**Estimé.** 2 fiches · ≈2,00 $ — ≈1,00 $/fiche sur 3 clos (le " in lu_e
                 and lu_e.index("**Estimé.**") < lu_e.index("**Fait.**")), ("EST1 : l'estimé avant **Fait.**, fiches lues sur la plage — mutant : D1–D2 comptée dans la moyenne $") + "\n" + str(s + lu_e)
        code, s = appel(["ouvrir", te, "--fiches", "ctx/30-q.md", "--titre", "q", "--estime-fiches", "0,5"])
        assert (code == 0 and "· estimé gardé — " in s
                 and lire(os.path.join(te, "ctx", "30-q.md")).count("**Estimé.**") == 1), ("EST1 : second appel, estimé gardé, une seule ligne") + "\n" + str(s)
        code, s = appel(["ouvrir", te, "--fiches", "ctx/30-q.md", "--titre", "q"])
        assert (code == 0 and "estimé" not in s
                 and lire(os.path.join(te, "ctx", "30-q.md")) == lu_e), ("EST1 : sans l'option, rien ne change") + "\n" + str(s)
        assert (mod.nombre_fiches("0,5") == mod.nombre_fiches("0.5") == 0.5
                 and mod.decimal_fr(0.5) == "0,5" and mod.decimal_fr(2.0) == "2"), ("EST1 : 0,5 et 0.5 acceptés") + "\n" + ""
        sans_chantier(te, carte_e)
        ecrire(os.path.join(te, "ctx", "31-r.md"), "# Chantier R — r\n\n**Fait.** Rien.\n\n## R1 [ ] — a\n")
        ecrire(os.path.join(te, "ctx", "artefacts", "feuille-de-route.html"),
               "<!-- ZONE:clos -->\n<tbody>\n" + rang % ("E1–E8", "non mesurable") + "</tbody>\n")
        code, s = appel(["ouvrir", te, "--fiches", "ctx/31-r.md", "--titre", "r", "--estime-fiches", "1"])
        assert (code == 0 and "GARDE: aucun chantier clos mesuré" in s
                 and mod.courant_de(te) == "ctx/31-r.md"), ("EST1 : aucun clos mesuré, GARDE, le reste écrit") + "\n" + str(s)
        # TAU2 : des clos mesurés en tokens, mais aucun au prix `$` — GARDE dédiée, pas d'estimé en $.
        sans_chantier(te, carte_e)
        ecrire(os.path.join(te, "ctx", "32-s.md"), "# Chantier S — s\n\n**Fait.** Rien.\n\n## S1 [ ] — a\n")
        ecrire(os.path.join(te, "ctx", "artefacts", "feuille-de-route.html"),
               "<!-- ZONE:clos -->\n<tbody>\n" + rang % ("D1–D2", "≈2,0M (2 000 000)") + "</tbody>\n")
        code, s = appel(["ouvrir", te, "--fiches", "ctx/32-s.md", "--titre", "s", "--estime-fiches", "1"])
        assert (code == 0
                 and "GARDE: aucun chantier clos au prix mesuré sur la feuille de route — pas d'estimé" in s
                 and "**Estimé.**" not in lire(os.path.join(te, "ctx", "32-s.md"))
                 and mod.courant_de(te) == "ctx/32-s.md"), ("TAU2 : mesuré en tokens, aucun au prix $ — GARDE dédiée, le reste écrit") + "\n" + str(s)
        os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
    # TAU2 : le total de la feuille (`resume_clos`, `resommer`) sur trois clos, deux avec `$` et un
    # sans — mutant : compter la ligne sans `$` comme 0 $ fausse la somme comme la moyenne.
    corps_mixte = (rang % ("A1–A3", "3,00 $ · ≈3,0M (3 000 000)") + rang % ("B1", "1,00 $ · ≈1,0M (1 000 000)")
                   + rang % ("D1–D2", "≈2,0M (2 000 000)"))
    from decimal import Decimal
    assert (mod.prix_clos(corps_mixte) == (Decimal("4.00"), 2)), ("TAU2 : prix_clos — deux lignes sur trois portent un $, la troisième ignorée") + "\n" + str(mod.prix_clos(corps_mixte))
    assert (mod.resume_clos(3, 6_000_000, Decimal("4.00"), 2)
             == "3 chantiers clos · ≈6,0M (6 000 000) tokens · 4,00 $ sur 2 clos mesurés"), ("TAU2 : resume_clos — « sur 2 clos mesurés »") + "\n" + str(mod.resume_clos(3, 6_000_000, Decimal("4.00"), 2))
    gabarit_pied = ('<table><tbody>%s</tbody><tfoot><tr><td colspan="3">Total cumulé</td>'
                    '<td class="mono"><strong>x</strong></td><td class="mono">y</td></tr></tfoot></table>'
                    '<span class="resume-clos">z</span>' % corps_mixte)
    resomme = mod.resommer(gabarit_pied, 3, 6_000_000, *mod.prix_clos(corps_mixte))
    assert ('<strong>≈6,0M (6 000 000)</strong></td><td class="mono">4,00 $ sur 2 clos mesurés</td>' in resomme
             and '<span class="resume-clos">3 chantiers clos · ≈6,0M (6 000 000) tokens · 4,00 $ sur 2 clos mesurés</span>' in resomme), ("TAU2 : resommer — pied « 4,00 $ sur 2 clos mesurés », toutes mesurées → sans le « sur »") + "\n" + str(resomme)
    corps_toutes = rang % ("A1–A3", "3,00 $ · ≈3,0M (3 000 000)") + rang % ("B1", "1,00 $ · ≈1,0M (1 000 000)")
    assert (mod.texte_cout_clos(*mod.prix_clos(corps_toutes), 2) == "4,00 $"), ("TAU2 : texte_cout_clos — toutes mesurées, sans « sur »") + "\n" + str(mod.texte_cout_clos(*mod.prix_clos(corps_toutes), 2))
    assert (mod.texte_cout_clos(None, 0, 1) == ""), ("TAU2 : texte_cout_clos — aucune mesurée, vide") + "\n" + str(mod.texte_cout_clos(None, 0, 1))
    # `clore` sans ligne **Estimé.** (chantier ouvert avant EST) : « estimé non noté », sans GARDE
    # d'estimé ; le réel en dollars est le prix mesuré de la page, `? $` sans lui (chantiers EST, TAU).
    with tempfile.TemporaryDirectory() as te:
        ecrire(os.path.join(te, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **artefact du chantier** : aucun\n\n"
               "Lettres de fiche déjà prises : U (test).\n")
        ecrire(os.path.join(te, "ctx", "50-u.md"), ouvert("# Chantier U — u\n\n**Fait.** Rien.\n\n## U1 [x] — a\n## U2 [x] — b\n"))
        code, s = appel(["clore", te, "--livre", "fini", "--date", "2026-09-26"])
        assert (code == 0
                 and " · estimé non noté · cadré 2 · joué 2 fiches ? $ — " in s and "stim" not in s.split("CLOS ")[0]
                 and "**Fait.** U1..U2 (2026-09-26) : fini — estimé non noté · cadré 2 · joué 2 fiches ? $.\n"
                 in open(os.path.join(te, "ctx", "50-u.md"), encoding="utf-8").read()), ("EST2 : sans **Estimé.**, estimé non noté, réel ≈? $") + "\n" + str(s)
    # Le prix mesuré (le pondéré de la page, ici 12,34 $ pour 2 M tokens — la louche en dirait
    # ≈1,67 $) : au joué, et en tête de la cellule Tokens de la feuille ; inconnu, `? $` et une
    # cellule sans `$` (chantier TAU). Mutant : remettre `estimation_usd` au joué — le test tombe.
    for prix, joue, cellule in ((Decimal("12.34"), "12,34 $", "12,34 $ · ≈2,0M (2 000 000)"),
                                (None, "? $", "≈2,0M (2 000 000)")):
        with tempfile.TemporaryDirectory() as te:
            ecrire(os.path.join(te, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
                   "- **fichier d'état** : ctx/08-etat.md\n"
                   "- **artefact du chantier** : aucun\n\n"
                   "Lettres de fiche déjà prises : U (test).\n")
            ecrire(os.path.join(te, "ctx", "08-etat.md"), "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n"
                   "|---|---|---|---|---|\n| 3 | Trois | a | 2 fiches | — |\n\n## Journal\n")
            ecrire(os.path.join(te, "ctx", "50-u.md"), ouvert("# Chantier U — u\n\n**Estimé.** 3 fiches · ≈9,00 $ — ≈3,00 $/fiche sur 2 clos (le 2026-09-01).\n\n**Fait.** Rien.\n\n## U1 [x] — a\n"))
            ecrire(os.path.join(te, "ctx", "artefacts", "50-u.html"),
                   open(os.path.join(ICI, "..", "templates", "artefact-chantier.html"), encoding="utf-8").read())
            fdr = os.path.join(te, "ctx", "artefacts", "feuille-de-route.html")
            ecrire(fdr, open(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html"), encoding="utf-8").read())
            regenerer_vrai = mod.noyau.page.regenerer
            mod.noyau.page.regenerer = lambda *x, p=prix: (lambda r: r[:3] + ((2_000_000, 3, p), r[4]))(regenerer_vrai(*x))
            try:
                code, s = appel(["clore", te, "--livre", "fini", "--date", "2026-09-26"])
            finally:
                mod.noyau.page.regenerer = regenerer_vrai
            texte = "estimé 3 fiches ≈9,00 $ · cadré 1 · joué 1 fiches " + joue
            lu = lambda c: open(c, encoding="utf-8").read()
            feuille = lu(fdr)
            assert (code == 0
                     and " · " + texte + " — " in s
                     and "<p>Estimé : " + texte + "</p>" in lu(os.path.join(te, "ctx", "artefacts", "50-u.html"))
                     and "Estimé : " + texte + "\n" in lu(os.path.join(te, "ctx", "artefacts", "50-u.md"))
                     and "**Fait.** U1..U1 (2026-09-26) : fini — " + texte + ".\n" in lu(os.path.join(te, "ctx", "50-u.md"))), ("TAU1 : joué au prix mesuré (%s) — CLOS, page, .md, **Fait.**" % joue) + "\n" + str(s)
            attendu = (2_000_000, 1, 1, prix, 1 if prix is not None else 0)
            assert ('<td class="mono">' + cellule + "</td>" in "".join(mod.lignes_clos(feuille))
                     and mod.couts_clos(feuille) == [("u", 2_000_000)] and mod.moyenne_clos(feuille) == attendu
                     and (prix is not None or "$ · ≈2,0M" not in feuille)), ("TAU1 : cellule Tokens « %s », brut relu par couts_clos et moyenne_clos" % cellule) + "\n" + str("%r %r %s" % (mod.couts_clos(feuille), mod.moyenne_clos(feuille), mod.lignes_clos(feuille)))


def test_rep2_chevrons(tmp_path):
    """Contrôler le retrait des chevrons d'une URL (REP2)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        # Test 1 : champ retire les chevrons d'une URL entre chevrons
        carte_avec_chevrons = """# Chantier REP2
- **artefact du chantier** : <https://example.com/path>
"""
        carte_sans_chevrons = """# Chantier REP2
- **artefact du chantier** : https://example.com/path
"""
        carte_autre_chevrons = """# Chantier REP2
- **artefact du chantier** : <contexte>
"""

        lignes = carte_avec_chevrons.strip().split('\n')
        val = mod.champ(lignes, "artefact du chantier")
        assert (val == "https://example.com/path"), ("REP2 : champ retire les chevrons d'une URL https") + "\n" + str("got: " + str(val))

        lignes = carte_sans_chevrons.strip().split('\n')
        val = mod.champ(lignes, "artefact du chantier")
        assert (val == "https://example.com/path"), ("REP2 : champ retourne une URL sans chevrons inchangée") + "\n" + str("got: " + str(val))

        lignes = carte_autre_chevrons.strip().split('\n')
        val = mod.champ(lignes, "artefact du chantier")
        assert (val == "<contexte>"), ("REP2 : champ retourne <contexte> inchangé") + "\n" + str("got: " + str(val))

        # Test 2 : ouvrir --artefact retire les chevrons
        proj = os.path.join(t, "proj-rep2")
        ecrire(os.path.join(proj, "CHANTIER.md"),
               """# Chantier courant
- **alias** : rep
- **artefact du chantier** : aucun
""")
        ecrire(os.path.join(proj, "fiches.md"), """# Chantier REP2

## Le socle

---

## REP2 [ ] — à faire
""")
        ecrire(os.path.join(proj, "CLAUDE.md"), """| relire un chantier clos | exemple |
""")
        ecrire(os.path.join(proj, "context AI", "00-index.md"), "| `a` | b |\n")

        code, s = appel(["ouvrir", proj, "--fiches", "fiches.md", "--titre", "REP2", "--artefact", "<https://example.com/artifact>"])
        carte = io.open(os.path.join(proj, "CHANTIER.md"), encoding="utf-8").read()
        assert ("- **artefact du chantier** : https://example.com/artifact" in carte), ("REP2 : ouvrir retire les chevrons de --artefact") + "\n" + str(carte)

        # Test 3 : cmd_ouvrir avec URL sans chevrons
        proj2 = os.path.join(t, "proj-rep2b")
        ecrire(os.path.join(proj2, "CHANTIER.md"),
               """# Chantier courant
- **alias** : rep
- **artefact du chantier** : aucun
""")
        ecrire(os.path.join(proj2, "fiches.md"), """# Chantier REP2

## Le socle

---

## REP2b [ ] — à faire
""")
        ecrire(os.path.join(proj2, "CLAUDE.md"), """| relire un chantier clos | exemple |
""")
        ecrire(os.path.join(proj2, "context AI", "00-index.md"), "| `a` | b |\n")

        code, s = appel(["ouvrir", proj2, "--fiches", "fiches.md", "--titre", "REP2b", "--artefact", "https://example.com/artifact"])
        carte2 = io.open(os.path.join(proj2, "CHANTIER.md"), encoding="utf-8").read()
        assert ("- **artefact du chantier** : https://example.com/artifact" in carte2), ("REP2 : ouvrir accepte une URL sans chevrons") + "\n" + str(carte2)


def git_matin(d, *args):
    r = subprocess.run(["git"] + list(args), cwd=d, capture_output=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise RuntimeError("git %s : %s" % (" ".join(args), r.stderr))
    return r.stdout


def test_ouvrir_marque(tmp_path, init_git):
    """NUI23 : `ouvrir` pose la marque et le post-it ; un worktree ouvre le sien sans la page de main ; `clore`
    efface le post-it ; un 2e chantier dans le même dossier est refusé."""
    if not shutil.which("git"):
        pytest.skip("git absent — ouvrir et clore par la marque ne sont pas testés")
        return
    signe = ("-c", "user.name=t", "-c", "user.email=t@t")
    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
        d, wt = os.path.join(tr, "om"), os.path.join(tr, "wt")
        ecrire(os.path.join(d, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **artefact du chantier** : https://exemple/nui\n\n"
               "Lettres de fiche déjà prises : N (nuit), P (par).\n")
        ecrire(os.path.join(d, "ctx", "50-nui.md"), ouvert_ligne("# Chantier N — nuit\n\n" + OUVERT_LIGNE % "2026-10-03" + "\n\n## N1 [ ] — a\n"))
        ecrire(os.path.join(d, "ctx", "51-par.md"), "# Chantier P — par\n\n**Fait.** Rien.\n\n## P1 [x] — a\n")
        init_git(d)
        git_matin(d, "add", "-A")
        git_matin(d, *signe, "commit", "-q", "-m", "base")
        git_matin(d, "worktree", "add", "-q", "-b", "par", wt)
        code1, s1 = appel(["ouvrir", wt, "--fiches", "ctx/51-par.md", "--titre", "Par"])
        code1b, s1b = appel(["ouvrir", wt, "--fiches", "ctx/51-par.md", "--titre", "Par"])
        carte_par = mod.lire(os.path.join(wt, "CHANTIER.md"))
        par = mod.lire(os.path.join(wt, "ctx", "51-par.md"))
        p_wt = mod.postit(wt) or ""
        nomme = mod.lire(p_wt).strip() if os.path.isfile(p_wt) else None
        ouverts_avant = mod.ouverts(wt)
        code2, s2 = appel(["clore", wt, "--livre", "fini", "--date", "2026-10-04"])
        postit_reste = os.path.isfile(p_wt)
        ouverts_apres = mod.ouverts(wt)
        ecrire(os.path.join(d, "ctx", "52-q.md"), "# Chantier Q — q\n\n## Q1 [ ] — a\n")
        code3, s3 = appel(["ouvrir", d, "--fiches", "ctx/52-q.md", "--titre", "Q"])
        git_matin(d, "worktree", "remove", "--force", wt)
    assert ((code1, code1b) == (0, 0) and "- **artefact du chantier** : aucun\n" in carte_par
             and par.count("**Ouvert.**") == 1 and nomme == "ctx/51-par.md"
             and ouverts_avant == ["ctx/50-nui.md", "ctx/51-par.md"]), ("NUI23 ouvrir : dans un worktree tiré de main où NUI est ouvert, PAR s'ouvre, artefact « aucun », une "
             "seule marque même relancé, post-it écrit — mutant : l'artefact toujours repris") + "\n" + str(s1 + s1b + carte_par + par)
    assert (code2 == 0 and not postit_reste and ouverts_apres == ["ctx/50-nui.md"]
             and code3 == 1 and s3.startswith("GARDE: un chantier est déjà ouvert : ctx/50-nui.md")), ("NUI23 clore : post-it effacé, PAR hors des ouverts ; ouvrir un 2e chantier dans le dossier → GARDE") + "\n" + str("\n".join((s2, repr(ouverts_apres), s3)))


# Pas sous tmp_path : son nom porterait « marque », que ce test cherche absent de la sortie.
def test_nui30_marque(init_git):
    """NUI30 : `niveau --ecrire` pose la marque d'un projet à la Cairn (5 fichiers sans CLOS, un courant), datée de son
    commit d'ouverture ; rejoué, rien ; `pause` la pose, `ouvrir` la lève."""
    if not shutil.which("git"):
        pytest.skip("git absent — la marque de niveau et la pause ne sont pas testées")
        return

    def courant(dossier):
        return next((l for l in appel(["carte", dossier])[1].split("\n") if l.startswith(("COURANT=", "GARDE:"))), "")

    with tempfile.TemporaryDirectory() as tr:
        d, sans_git, rien = os.path.join(tr, "ca"), os.path.join(tr, "sg"), os.path.join(tr, "rien")
        ecrire(os.path.join(d, "CHANTIER.md"), "- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **fichier de fiches courant** : ctx/59-f.md (F1..F1)\n- **artefact du chantier** : aucun\n")
        for n, code in (("22-a", "A"), ("23-b", "B"), ("34-h", "H"), ("58-m", "M"), ("59-f", "F")):
            ecrire(os.path.join(d, "ctx", n + ".md"), "# Chantier %s — x\n\n## %s1 [ ] — f\n" % (code, code))
        ecrire(os.path.join(d, "ctx", "21-z.md"), "# Chantier Z — x\n\n" + mod.CLOS_LIGNE % "2026-09-01" + "\n")
        for p_ in (d, sans_git, rien):
            ecrire(os.path.join(p_, "ctx", "00-INDEX.md"), "# Index\n")
        init_git(d)
        git_matin(d, "add", "-A")
        git_matin(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--date=2026-09-20T12:00:00",
                  "-m", "Chantier F ouvert : x")
        avant = courant(d)
        _, s0 = appel(["niveau", d])
        _, s1 = appel(["niveau", d, "--ecrire", "--date", "2026-10-08"])
        apres, ouverts1, f1 = courant(d), appel(["ouverts", d])[1], mod.lire(os.path.join(d, "ctx", "59-f.md"))
        carte1 = mod.lire(os.path.join(d, "CHANTIER.md"))
        _, s2 = appel(["niveau", d, "--ecrire", "--date", "2026-10-08"])
        f2 = mod.lire(os.path.join(d, "ctx", "59-f.md"))
        code3, s3 = appel(["pause", os.path.join(d, "ctx", "34-h.md"), "en pause le soir même", "--date", "2026-09-20"])
        code4, s4 = appel(["pause", os.path.join(d, "ctx", "34-h.md"), "encore"])
        code5, s5 = appel(["pause", os.path.join(d, "ctx", "59-f.md"), "attend"])
        ouverts2, f5 = appel(["ouverts", d])[1], mod.lire(os.path.join(d, "ctx", "59-f.md"))
        code6, s6 = appel(["ouvrir", d, "--fiches", "ctx/59-f.md", "--titre", "x"])
        ouverts3, f6 = appel(["ouverts", d])[1], mod.lire(os.path.join(d, "ctx", "59-f.md"))
        code7, s7 = appel(["pause", os.path.join(d, "ctx", "21-z.md"), "x"])
        code8, s8 = appel(["pause", os.path.join(d, "ctx", "absent.md"), "x"])
        h3 = mod.lire(os.path.join(d, "ctx", "34-h.md"))
        ecrire(os.path.join(sans_git, "CHANTIER.md"), "- **contexte** : ctx/\n- **fichier de fiches courant** : ctx/9-s.md\n")
        ecrire(os.path.join(sans_git, "ctx", "9-s.md"), "# Chantier S — x\n\n## S1 [ ] — f\n")
        _, s9 = appel(["niveau", sans_git, "--ecrire", "--date", "2026-10-08"])
        ecrire(os.path.join(rien, "CHANTIER.md"), "- **contexte** : ctx/\n")
        ecrire(os.path.join(rien, "ctx", "9-s.md"), "# Chantier S — x\n\n## S1 [ ] — f\n")
        _, s10 = appel(["niveau", rien, "--ecrire", "--date", "2026-10-08"])
    marque = "**Ouvert.** le 2026-09-20."
    assert ("ÉCART: marque: ctx/59-f.md sans **Ouvert.**" in s0
             and "CORRIGÉ: marque: **Ouvert.** le 2026-09-20 sur ctx/59-f.md — son commit d'ouverture" in s1
             and f1.startswith("# Chantier F — x\n\n" + marque + "\n\n## F1") and ouverts1 == "OUVERT ctx/59-f.md\n"
             and "marque" not in s2 and f2 == f1), ("NUI30 niveau : projet à la Cairn — ÉCART sans --ecrire ; --ecrire pose la marque du commit d'ouverture sous "
             "le titre ; rejoué → rien écrit — mutant : `migre` ignoré, la marque doublée") + "\n" + str("\n".join((avant, apres, s0, s1, s2, f1)))
    assert (avant == "COURANT=aucun" and apres == "COURANT=ctx/59-f.md"
             and "ÉCART: ligne: CHANTIER.md:3 — « fichier de fiches courant » n'est plus lue (NUI31) — gardée tant que "
                 "la marque d'ouverture manque" in s0
             and "CORRIGÉ: ligne: « fichier de fiches courant » retirée de CHANTIER.md:3" in s1
             and carte1 == "- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n- **artefact du chantier** : aucun\n"
             and "ligne:" not in s2), ("NUI31 niveau : la ligne « fichier de fiches courant » n'est plus lue (COURANT=aucun avant la marque) ; "
             "gardée sans --ecrire, retirée après la marque, le reste de CHANTIER.md intact ; rejoué → rien — mutant : "
             "retirée avant que la marque ne soit posée") + "\n" + str("\n".join((avant, apres, s0, s1, s2, carte1)))
    assert ("CORRIGÉ: marque: **Ouvert.** le 2026-10-08 sur ctx/9-s.md — date de l'appel, aucun commit « Chantier S "
             "ouvert »" in s9 and "CORRIGÉ: ligne:" in s9 and "marque" not in s10 and "ligne:" not in s10), ("NUI30 niveau : sans commit d'ouverture, la date de l'appel, dite, puis la ligne retirée ; sans ligne → rien") + "\n" + str(s9 + s10)
    assert ((code3, s3) == (0, "PAUSE %s le 2026-09-20\n" % os.path.join(d, "ctx", "34-h.md").replace("\\", "/"))
             and h3.startswith("# Chantier H — x\n\n**Pause.** le 2026-09-20 — en pause le soir même\n\n## H1")
             and code4 == 1 and "porte déjà **Pause.**" in s4 and code5 == 0 and ouverts2 == "OUVERTS=0\n"
             and "**Pause.**" in f5 and code6 == 0 and " · pause levée" in s6 and "**Pause.**" not in f6
             and f6.startswith("# Chantier F — x\n\n" + marque + "\n\n## F1") and ouverts3 == "OUVERT ctx/59-f.md\n"
             and code7 == 1 and "porte déjà **CLOS**" in s7 and code8 == 1 and s8.startswith("GARDE: fichier de fiches")), ("NUI30 pause : posée sous le titre, le chantier sort des ouverts ; en double, sur un clos, introuvable → GARDE ; "
             "ouvrir la lève — mutant : lever_pause ne rend rien") + "\n" + str("\n".join((s3, s4, s5, ouverts2, s6, ouverts3, f6, s7, s8, h3)))
