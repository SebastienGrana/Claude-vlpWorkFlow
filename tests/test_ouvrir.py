"""`noyau/ouvrir.py` : `ouvrir`, l'estimé d'un chantier, sa marque, les chevrons de la feuille — migré de
l'ancienne suite maison (REF51). Chaque `assert` garde le libellé d'origine de son `verifier` en tête de son message
(REF5), puis le diagnostic.
"""
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
from decimal import Decimal

import pytest
from aides import SCRIPTS, appel, ecrire, lire_texte, mod

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


CARTE_O = ("# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
           "- **artefact du chantier** : %s\n")


def decor_ouvrir(t, monkeypatch):
    """Le départ de chaque test d'`ouvrir`, posé dans `t` : une carte sans chantier, un index, un routage `CLAUDE.md`,
    `ctx/30-q.md` (Q1..Q2), et la session du cadrage à « cadre », que `ouvrir` note ; ne rend rien."""
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "cadre")
    ecrire(os.path.join(t, "CHANTIER.md"), CARTE_O % "aucun")
    ecrire(os.path.join(t, "ctx", "00-INDEX.md"), "| Fichier | Lire |\n|---|---|\n| `10-e.md` | on relit |\n| `05-d.md` | vieux |\n\nFin.\n")
    ecrire(os.path.join(t, "CLAUDE.md"), "| La tâche | Ouvrir |\n|---|---|\n| modifier | x |\n| relire le chantier E (e) | `ctx/10-e.md` — chantier **clos** |\n| relire un chantier clos | `ctx/00-INDEX.md` |\n")
    ecrire(os.path.join(t, "ctx", "30-q.md"), "# Chantier Q — Un titre\n\n## Q1 [ ] — a\n## Q2 [ ] — b\n")


def test_ouvrir(tmp_path, monkeypatch):
    """Contrôler `ouvrir` : bilan, fichier de fiches posé, ligne de l'état ; relancé avec un artefact, rien de doublé."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        lire = lire_texte
        decor_ouvrir(t, monkeypatch)
        code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un `titre`"])
        carte_lue, index_lu, claude_lu = lire(os.path.join(t, "CHANTIER.md")), lire(os.path.join(t, "ctx", "00-INDEX.md")), lire(os.path.join(t, "CLAUDE.md"))
        assert code == 0
        assert s == "OUVERT Q Q1..Q2 · index +1 · routage +1 · session +1 · artefact aucun — %s\n" % t
        assert (lire(os.path.join(t, "ctx", "30-q.md"))
                 == "# Chantier Q — Un titre\n\n%s\n\n**Session** : cadre\n\n## Q1 [ ] — a\n## Q2 [ ] — b\n"
                 % (mod.OUVERT_LIGNE % __import__("datetime").date.today().isoformat())), ("ouvrir : la session du cadrage, avant la première ligne ##") + "\n" + str(lire(os.path.join(t, "ctx", "30-q.md")))
        assert "fichier de fiches" not in carte_lue
        assert "- **artefact du chantier** : aucun\n" in carte_lue
        assert mod.courant_de(t) == "ctx/30-q.md"
        assert ("| `10-e.md` | on relit |\n| `30-q.md` | on joue une fiche `Q*` — chantier **ouvert** « Un `titre` », `Q1..Q2` |\n| `05-d.md`" in index_lu), ("ouvrir : index, après le plus grand numéro") + "\n" + str(index_lu)
        assert ("**clos** |\n| jouer une fiche du chantier Q (un `titre`) | `ctx/30-q.md` — chantier **ouvert**, par `/vlp:tache Q<n>` |\n| relire" in claude_lu), ("ouvrir : routage, avant « relire un chantier clos »") + "\n" + str(claude_lu)
        code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un `titre`", "--artefact", "https://exemple/q"])
        assert code == 0
        assert "index +0 · routage +0 · session +0 · artefact https://exemple/q" in s
        assert lire(os.path.join(t, "ctx", "30-q.md")).count("**Session**") == 1
        assert lire(os.path.join(t, "CLAUDE.md")) == claude_lu
        assert lire(os.path.join(t, "ctx", "00-INDEX.md")) == index_lu
        assert "**artefact du chantier** : https://exemple/q" in lire(os.path.join(t, "CHANTIER.md"))


def test_ouvrir_relance(tmp_path, monkeypatch):
    """`ouvrir` relancé sur le chantier ouvert : rien ne bouge ; un autre chantier refusé ; un titre neuf ne fait suivre
    que la plage, sur la même ligne d'index ; une ligne d'index écrite à la main gardée."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        lire = lire_texte
        decor_ouvrir(t, monkeypatch)
        appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un `titre`"])
        appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un `titre`", "--artefact", "https://exemple/q"])
        avant = lire(os.path.join(t, "CHANTIER.md"))
        code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un `titre`"])
        assert code == 0
        assert lire(os.path.join(t, "CHANTIER.md")) == avant
        ecrire(os.path.join(t, "ctx", "31-r.md"), "# Chantier R — r\n\n## R1 [ ] — a\n")
        code, s = appel(["ouvrir", t, "--fiches", "ctx/31-r.md", "--titre", "r"])
        assert code == 1
        assert s.startswith("GARDE: un chantier est déjà ouvert")
        assert lire(os.path.join(t, "CHANTIER.md")) == avant
        ecrire(os.path.join(t, "ctx", "30-q.md"), "# Chantier Q — Un titre\n\n## Q1 [ ] — a\n## Q2 [ ] — b\n## Q3 [ ] — c\n")
        # Relancé avec un autre titre : seule la plage suit, sur la même et unique ligne.
        code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un autre titre"])
        index_q = [l for l in lire(os.path.join(t, "ctx", "00-INDEX.md")).split("\n") if l.startswith("| `30-q.md` |")]
        assert code == 0
        assert "OUVERT Q Q1..Q3 · index ~1 · routage +0 · session +1" in s
        assert index_q == ["| `30-q.md` | on joue une fiche `Q*` — chantier **ouvert** « Un `titre` », `Q1..Q3` |"]
        assert mod.courant_de(t) == "ctx/30-q.md"
        index_main = lire(os.path.join(t, "ctx", "00-INDEX.md")).replace("chantier **ouvert** « Un `titre` », `Q1..Q3`", "à la main `Q1..Q2`")
        ecrire(os.path.join(t, "ctx", "00-INDEX.md"), index_main)
        code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un `titre`"])
        assert code == 0
        assert "index +0" in s
        assert lire(os.path.join(t, "ctx", "00-INDEX.md")) == index_main


def test_ouvrir_sans_claude(tmp_path, monkeypatch):
    """Sans `CLAUDE.md`, `ouvrir` ouvre quand même et le dit, routage +0 ; un fichier qui porte **CLOS** est refusé."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        lire = lire_texte
        decor_ouvrir(t, monkeypatch)
        appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Un `titre`"])
        ecrire(os.path.join(t, "ctx", "31-r.md"), "# Chantier R — r\n\n## R1 [ ] — a\n")
        sans_chantier(t, CARTE_O % "aucun")
        os.remove(os.path.join(t, "CLAUDE.md"))
        code, s = appel(["ouvrir", t, "--fiches", "ctx/31-r.md", "--titre", "r"])
        assert code == 0
        assert "GARDE: CLAUDE.md introuvable" in s
        assert "routage +0" in s
        assert "index +1" in s
        assert mod.courant_de(t) == "ctx/31-r.md"
        sans_chantier(t, CARTE_O % "aucun")
        ecrire(os.path.join(t, "ctx", "32-s.md"), "# Chantier S — s\n\n**CLOS** le 2026-01-01. Ne se rejoue pas.\n\n## S1 [x] — a\n")
        code, s = appel(["ouvrir", t, "--fiches", "ctx/32-s.md", "--titre", "s"])
        assert code == 1
        assert s.startswith("GARDE: ctx/32-s.md porte **CLOS**")
        assert "aucun" in lire(os.path.join(t, "CHANTIER.md"))


def test_ouvrir_session(tmp_path, monkeypatch):
    """La session du cadrage notée par `ouvrir` : avant `## Le socle commun`, jamais redoublée, rien pour un id vide."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        lire = lire_texte
        decor_ouvrir(t, monkeypatch)
        # Un vrai fichier : la session va avant `## Le socle commun`, jamais entre le marqueur d'une
        # fiche et son titre — la fiche extraite n'en porte pas. Déjà sur une ligne `**Session**`, même
        # d'une fiche, elle n'est pas redoublée ; un id vide ne note rien.
        vrai = ("# Chantier T — t\n\nÀ quoi il sert.\n\n## Le socle commun\n\n## L'ordre des fiches\n\n"
                "<!-- FICHE:T1 -->\n## T1 [ ] — a\n<!-- /FICHE -->\n")
        for nom, texte in (("33-t.md", vrai), ("34-u.md", "# Chantier U — u\n\n## U1 [x] — a\n**Session** : cadre\n"),
                           ("35-v.md", "# Chantier V — v\n\n## V1 [ ] — a\n")):
            ecrire(os.path.join(t, "ctx", nom), texte)
        sans_chantier(t, CARTE_O % "aucun")
        code, s = appel(["ouvrir", t, "--fiches", "ctx/33-t.md", "--titre", "t"])
        lu_o = lire(os.path.join(t, "ctx", "33-t.md"))
        assert code == 0
        assert "· session +1 ·" in s
        assert (lu_o == vrai.replace("## Le socle commun", "**Session** : cadre\n\n## Le socle commun")
                                 .replace("# Chantier T — t\n\n", "# Chantier T — t\n\n%s\n\n" % OUVERT_DU_JOUR))
        assert "**Session**" not in appel(["extraire", os.path.join(t, "ctx", "33-t.md"), "T1"])[1]
        sans_chantier(t, CARTE_O % "aucun")
        code, s = appel(["ouvrir", t, "--fiches", "ctx/34-u.md", "--titre", "u"])
        assert code == 0
        assert "· session +0 ·" in s
        assert lire(os.path.join(t, "ctx", "34-u.md")).count("**Session**") == 1
        sans_chantier(t, CARTE_O % "aucun")
        monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "")
        code, s = appel(["ouvrir", t, "--fiches", "ctx/35-v.md", "--titre", "v"])
        assert code == 0
        assert "· session +0 ·" in s
        assert lire(os.path.join(t, "ctx", "35-v.md")) == "# Chantier V — v\n\n%s\n\n## V1 [ ] — a\n" % OUVERT_DU_JOUR


RANG = ('          <tr>\n            <td>x</td>\n            <td class="mono">%s</td><td class="mono">2026-01-01</td>\n'
        '            <td class="mono">%s</td>\n            <td>y</td>\n          </tr>\n')


CARTE_E = ("# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
           "- **artefact du chantier** : aucun\n")


# Pas sous tmp_path : son nom porterait « estime », que ce test cherche absent de la sortie.
def test_estime(monkeypatch):
    """`ouvrir --estime-fiches` : sans feuille, une GARDE ; avec elle, l'estimé au prix moyen des clos, gardé au
    relancement (chantiers EST, TAU)."""
    with tempfile.TemporaryDirectory() as te:
        # `ouvrir --estime-fiches` (chantier EST) : A1–A3 à 3,00 $ et B1 à 1,00 $ (4 fiches, 4,00 $)
        # font 1,00 $/fiche — le prix mesuré des lignes, pas les tokens (chantier TAU). D1–D2, mesurée
        # en tokens mais sans `$`, ne compte ni dans la somme ni dans les fiches de la moyenne — mutant :
        # la compter comme 0 $ ferait 4,00 $ sur 6 fiches, ≈0,67 $/fiche au lieu de ≈1,00 $/fiche. La
        # ligne non mesurable (E) ne compte pas non plus.
        lire = lire_texte
        monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "")
        rang, carte_e = RANG, CARTE_E
        fiches_e = "# Chantier Q — q\n\n**Fait.** Rien.\n\n## Q1 [ ] — a\n"
        ecrire(os.path.join(te, "CHANTIER.md"), carte_e)
        ecrire(os.path.join(te, "ctx", "30-q.md"), fiches_e)
        code, s = appel(["ouvrir", te, "--fiches", "ctx/30-q.md", "--titre", "q", "--estime-fiches", "2"])
        assert code == 0
        assert "GARDE: feuille de route introuvable" in s
        assert "estimé" not in s.split("\n")[-2]
        assert "**Estimé.**" not in lire(os.path.join(te, "ctx", "30-q.md"))
        assert mod.courant_de(te) == "ctx/30-q.md"
        ecrire(os.path.join(te, "ctx", "artefacts", "feuille-de-route.html"),
               "<!-- ZONE:clos -->\n<tbody>\n" + rang % ("A1–A3", "3,00 $ · ≈3,0M (3 000 000)")
               + rang % ("B1", "1,00 $ · ≈1,0M (1 000 000)") + rang % ("D1–D2", "≈2,0M (2 000 000)")
               + rang % ("E1–E8", "non recompté — fichier introuvable · non mesurable") + "</tbody>\n")
        code, s = appel(["ouvrir", te, "--fiches", "ctx/30-q.md", "--titre", "q", "--estime-fiches", "2"])
        lu_e = lire(os.path.join(te, "ctx", "30-q.md"))
        assert code == 0
        assert "· estimé 2 fiches ≈2,00 $ — " in s
        assert "\n**Estimé.** 2 fiches · ≈2,00 $ — ≈1,00 $/fiche sur 3 clos (le " in lu_e
        assert lu_e.index("**Estimé.**") < lu_e.index("**Fait.**")
        code, s = appel(["ouvrir", te, "--fiches", "ctx/30-q.md", "--titre", "q", "--estime-fiches", "0,5"])
        assert code == 0
        assert "· estimé gardé — " in s
        assert lire(os.path.join(te, "ctx", "30-q.md")).count("**Estimé.**") == 1
        code, s = appel(["ouvrir", te, "--fiches", "ctx/30-q.md", "--titre", "q"])
        assert code == 0
        assert "estimé" not in s
        assert lire(os.path.join(te, "ctx", "30-q.md")) == lu_e
        assert mod.nombre_fiches("0,5") == mod.nombre_fiches("0.5") == 0.5
        assert mod.decimal_fr(0.5) == "0,5"
        assert mod.decimal_fr(2.0) == "2"


# Pas sous tmp_path, comme `test_estime`.
def test_estime_sans_prix(monkeypatch):
    """`ouvrir --estime-fiches` sans clos mesuré, puis sans clos au prix `$` : une GARDE, pas d'estimé (EST, TAU2)."""
    with tempfile.TemporaryDirectory() as te:
        lire = lire_texte
        monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "")
        rang, carte_e = RANG, CARTE_E
        ecrire(os.path.join(te, "ctx", "31-r.md"), "# Chantier R — r\n\n**Fait.** Rien.\n\n## R1 [ ] — a\n")
        sans_chantier(te, carte_e)
        ecrire(os.path.join(te, "ctx", "artefacts", "feuille-de-route.html"),
               "<!-- ZONE:clos -->\n<tbody>\n" + rang % ("E1–E8", "non mesurable") + "</tbody>\n")
        code, s = appel(["ouvrir", te, "--fiches", "ctx/31-r.md", "--titre", "r", "--estime-fiches", "1"])
        assert code == 0
        assert "GARDE: aucun chantier clos mesuré" in s
        assert mod.courant_de(te) == "ctx/31-r.md"
        # TAU2 : des clos mesurés en tokens, mais aucun au prix `$` — GARDE dédiée, pas d'estimé en $.
        sans_chantier(te, carte_e)
        ecrire(os.path.join(te, "ctx", "32-s.md"), "# Chantier S — s\n\n**Fait.** Rien.\n\n## S1 [ ] — a\n")
        ecrire(os.path.join(te, "ctx", "artefacts", "feuille-de-route.html"),
               "<!-- ZONE:clos -->\n<tbody>\n" + rang % ("D1–D2", "≈2,0M (2 000 000)") + "</tbody>\n")
        code, s = appel(["ouvrir", te, "--fiches", "ctx/32-s.md", "--titre", "s", "--estime-fiches", "1"])
        assert code == 0
        assert "GARDE: aucun chantier clos au prix mesuré sur la feuille de route — pas d'estimé" in s
        assert "**Estimé.**" not in lire(os.path.join(te, "ctx", "32-s.md"))
        assert mod.courant_de(te) == "ctx/32-s.md"


def test_estime_total():
    """Le total de la feuille sur trois clos, deux au prix `$` et un sans : `prix_clos`, `resume_clos`, `resommer`,
    `texte_cout_clos` (TAU2)."""
    rang = RANG
    # TAU2 : le total de la feuille (`resume_clos`, `resommer`) sur trois clos, deux avec `$` et un
    # sans — mutant : compter la ligne sans `$` comme 0 $ fausse la somme comme la moyenne.
    corps_mixte = (rang % ("A1–A3", "3,00 $ · ≈3,0M (3 000 000)") + rang % ("B1", "1,00 $ · ≈1,0M (1 000 000)")
                   + rang % ("D1–D2", "≈2,0M (2 000 000)"))
    assert (mod.prix_clos(corps_mixte) == (Decimal("4.00"), 2)), ("TAU2 : prix_clos — deux lignes sur trois portent un $, la troisième ignorée") + "\n" + str(mod.prix_clos(corps_mixte))
    assert (mod.resume_clos(3, 6_000_000, Decimal("4.00"), 2)
             == "3 chantiers clos · ≈6,0M (6 000 000) tokens · 4,00 $ sur 2 clos mesurés"), ("TAU2 : resume_clos — « sur 2 clos mesurés »") + "\n" + str(mod.resume_clos(3, 6_000_000, Decimal("4.00"), 2))
    gabarit_pied = ('<table><tbody>%s</tbody><tfoot><tr><td colspan="3">Total cumulé</td>'
                    '<td class="mono"><strong>x</strong></td><td class="mono">y</td></tr></tfoot></table>'
                    '<span class="resume-clos">z</span>' % corps_mixte)
    resomme = mod.resommer(gabarit_pied, 3, 6_000_000, *mod.prix_clos(corps_mixte))
    assert '<strong>≈6,0M (6 000 000)</strong></td><td class="mono">4,00 $ sur 2 clos mesurés</td>' in resomme
    assert '<span class="resume-clos">3 chantiers clos · ≈6,0M (6 000 000) tokens · 4,00 $ sur 2 clos mesurés</span>' in resomme
    corps_toutes = rang % ("A1–A3", "3,00 $ · ≈3,0M (3 000 000)") + rang % ("B1", "1,00 $ · ≈1,0M (1 000 000)")
    assert (mod.texte_cout_clos(*mod.prix_clos(corps_toutes), 2) == "4,00 $"), ("TAU2 : texte_cout_clos — toutes mesurées, sans « sur »") + "\n" + str(mod.texte_cout_clos(*mod.prix_clos(corps_toutes), 2))
    assert (mod.texte_cout_clos(None, 0, 1) == ""), ("TAU2 : texte_cout_clos — aucune mesurée, vide") + "\n" + str(mod.texte_cout_clos(None, 0, 1))


def test_estime_clore(monkeypatch):
    """`clore` d'un chantier ouvert avant EST, sans ligne **Estimé.** : « estimé non noté », sans GARDE d'estimé."""
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
    # `clore` sans ligne **Estimé.** (chantier ouvert avant EST) : « estimé non noté », sans GARDE
    # d'estimé ; le réel en dollars est le prix mesuré de la page, `? $` sans lui (chantiers EST, TAU).
    with tempfile.TemporaryDirectory() as te:
        ecrire(os.path.join(te, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **artefact du chantier** : aucun\n\n"
               "Lettres de fiche déjà prises : U (test).\n")
        ecrire(os.path.join(te, "ctx", "50-u.md"), ouvert("# Chantier U — u\n\n**Fait.** Rien.\n\n## U1 [x] — a\n## U2 [x] — b\n"))
        code, s = appel(["clore", te, "--livre", "fini", "--date", "2026-09-26"])
        assert code == 0
        assert " · estimé non noté · cadré 2 · joué 2 fiches ? $ — " in s
        assert "stim" not in s.split("CLOS ")[0]
        assert ("**Fait.** U1..U2 (2026-09-26) : fini — estimé non noté · cadré 2 · joué 2 fiches ? $.\n"
                 in pathlib.Path(os.path.join(te, "ctx", "50-u.md")).read_text(encoding="utf-8"))


def test_estime_clore_prix(monkeypatch):
    """`clore` : le joué au prix mesuré de la page, `? $` sans lui, et la cellule Tokens de la feuille (TAU)."""
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
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
                   pathlib.Path(os.path.join(ICI, "..", "templates", "artefact-chantier.html")).read_text(encoding="utf-8"))
            fdr = os.path.join(te, "ctx", "artefacts", "feuille-de-route.html")
            ecrire(fdr, pathlib.Path(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html")).read_text(encoding="utf-8"))
            regenerer_vrai = mod.noyau.page.regenerer
            def regenerer_faux(*x, p=prix, vrai=regenerer_vrai):
                r = vrai(*x)
                return r[:3] + ((2_000_000, 3, p), r[4])
            mod.noyau.page.regenerer = regenerer_faux
            try:
                code, s = appel(["clore", te, "--livre", "fini", "--date", "2026-09-26"])
            finally:
                mod.noyau.page.regenerer = regenerer_vrai
            texte = "estimé 3 fiches ≈9,00 $ · cadré 1 · joué 1 fiches " + joue
            lu = lambda c: pathlib.Path(c).read_text(encoding="utf-8")
            feuille = lu(fdr)
            assert code == 0
            assert " · " + texte + " — " in s
            assert "<p>Estimé : " + texte + "</p>" in lu(os.path.join(te, "ctx", "artefacts", "50-u.html"))
            assert "Estimé : " + texte + "\n" in lu(os.path.join(te, "ctx", "artefacts", "50-u.md"))
            assert "**Fait.** U1..U1 (2026-09-26) : fini — " + texte + ".\n" in lu(os.path.join(te, "ctx", "50-u.md"))
            attendu = (2_000_000, 1, 1, prix, 1 if prix is not None else 0)
            assert '<td class="mono">' + cellule + "</td>" in "".join(mod.lignes_clos(feuille))
            assert mod.couts_clos(feuille) == [("u", 2_000_000)]
            assert mod.moyenne_clos(feuille) == attendu
            assert prix is not None or "$ · ≈2,0M" not in feuille


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

        appel(["ouvrir", proj, "--fiches", "fiches.md", "--titre", "REP2", "--artefact", "<https://example.com/artifact>"])
        carte = pathlib.Path(os.path.join(proj, "CHANTIER.md")).read_text(encoding="utf-8")
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

        _code, _s = appel(["ouvrir", proj2, "--fiches", "fiches.md", "--titre", "REP2b", "--artefact", "https://example.com/artifact"])
        carte2 = pathlib.Path(os.path.join(proj2, "CHANTIER.md")).read_text(encoding="utf-8")
        assert ("- **artefact du chantier** : https://example.com/artifact" in carte2), ("REP2 : ouvrir accepte une URL sans chevrons") + "\n" + str(carte2)


def git_matin(d, *args):
    r = subprocess.run(["git"] + list(args), cwd=d, capture_output=True, encoding="utf-8", errors="replace", check=False)
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
        code1, _s1 = appel(["ouvrir", wt, "--fiches", "ctx/51-par.md", "--titre", "Par"])
        code1b, _s1b = appel(["ouvrir", wt, "--fiches", "ctx/51-par.md", "--titre", "Par"])
        carte_par = mod.lire(os.path.join(wt, "CHANTIER.md"))
        par = mod.lire(os.path.join(wt, "ctx", "51-par.md"))
        p_wt = mod.postit(wt) or ""
        nomme = mod.lire(p_wt).strip() if os.path.isfile(p_wt) else None
        ouverts_avant = mod.ouverts(wt)
        code2, _s2 = appel(["clore", wt, "--livre", "fini", "--date", "2026-10-04"])
        postit_reste = os.path.isfile(p_wt)
        ouverts_apres = mod.ouverts(wt)
        ecrire(os.path.join(d, "ctx", "52-q.md"), "# Chantier Q — q\n\n## Q1 [ ] — a\n")
        code3, s3 = appel(["ouvrir", d, "--fiches", "ctx/52-q.md", "--titre", "Q"])
        git_matin(d, "worktree", "remove", "--force", wt)
    assert (code1, code1b) == (0, 0)
    assert "- **artefact du chantier** : aucun\n" in carte_par
    assert par.count("**Ouvert.**") == 1
    assert nomme == "ctx/51-par.md"
    assert ouverts_avant == ["ctx/50-nui.md", "ctx/51-par.md"]
    assert code2 == 0
    assert not postit_reste
    assert ouverts_apres == ["ctx/50-nui.md"]
    assert code3 == 1
    assert s3.startswith("GARDE: un chantier est déjà ouvert : ctx/50-nui.md")


def courant_carte(dossier):
    """La ligne `COURANT=` (ou `GARDE:`) de `vlp.py carte` sur `dossier` ; "" s'il n'en rend aucune."""
    return next((l for l in appel(["carte", dossier])[1].split("\n") if l.startswith(("COURANT=", "GARDE:"))), "")


def decor_cairn(d, init_git):
    """Un projet à la Cairn dans `d` : cinq fichiers de fiches sans **CLOS** dont F, nommé courant par l'ancienne ligne
    de la carte, un clos Z, l'index, et un seul commit « Chantier F ouvert », daté du 2026-09-20 ; ne rend rien."""
    ecrire(os.path.join(d, "CHANTIER.md"), "- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
           "- **fichier de fiches courant** : ctx/59-f.md (F1..F1)\n- **artefact du chantier** : aucun\n")
    for n, code in (("22-a", "A"), ("23-b", "B"), ("34-h", "H"), ("58-m", "M"), ("59-f", "F")):
        ecrire(os.path.join(d, "ctx", n + ".md"), "# Chantier %s — x\n\n## %s1 [ ] — f\n" % (code, code))
    ecrire(os.path.join(d, "ctx", "21-z.md"), "# Chantier Z — x\n\n" + mod.CLOS_LIGNE % "2026-09-01" + "\n")
    ecrire(os.path.join(d, "ctx", "00-INDEX.md"), "# Index\n")
    init_git(d)
    git_matin(d, "add", "-A")
    git_matin(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--date=2026-09-20T12:00:00",
              "-m", "Chantier F ouvert : x")


# Pas sous tmp_path : son nom porterait « marque », que ce test cherche absent de la sortie.
def test_nui30_marque(init_git):
    """NUI30 : `niveau --ecrire` pose la marque d'un projet à la Cairn (5 fichiers sans CLOS, un courant), datée de son
    commit d'ouverture ; rejoué, rien. La pause : `test_nui30_pause`."""
    if not shutil.which("git"):
        pytest.skip("git absent — la marque de niveau et la pause ne sont pas testées")
        return
    with tempfile.TemporaryDirectory() as tr:
        d, sans_git, rien = os.path.join(tr, "ca"), os.path.join(tr, "sg"), os.path.join(tr, "rien")
        decor_cairn(d, init_git)
        for p_ in (sans_git, rien):
            ecrire(os.path.join(p_, "ctx", "00-INDEX.md"), "# Index\n")
        avant = courant_carte(d)
        _, s0 = appel(["niveau", d])
        _, s1 = appel(["niveau", d, "--ecrire", "--date", "2026-10-08"])
        apres, ouverts1, f1 = courant_carte(d), appel(["ouverts", d])[1], mod.lire(os.path.join(d, "ctx", "59-f.md"))
        carte1 = mod.lire(os.path.join(d, "CHANTIER.md"))
        _, s2 = appel(["niveau", d, "--ecrire", "--date", "2026-10-08"])
        f2 = mod.lire(os.path.join(d, "ctx", "59-f.md"))
        ecrire(os.path.join(sans_git, "CHANTIER.md"), "- **contexte** : ctx/\n- **fichier de fiches courant** : ctx/9-s.md\n")
        ecrire(os.path.join(sans_git, "ctx", "9-s.md"), "# Chantier S — x\n\n## S1 [ ] — f\n")
        _, s9 = appel(["niveau", sans_git, "--ecrire", "--date", "2026-10-08"])
        ecrire(os.path.join(rien, "CHANTIER.md"), "- **contexte** : ctx/\n")
        ecrire(os.path.join(rien, "ctx", "9-s.md"), "# Chantier S — x\n\n## S1 [ ] — f\n")
        _, s10 = appel(["niveau", rien, "--ecrire", "--date", "2026-10-08"])
    marque = "**Ouvert.** le 2026-09-20."
    assert "ÉCART: marque: ctx/59-f.md sans **Ouvert.**" in s0
    assert "CORRIGÉ: marque: **Ouvert.** le 2026-09-20 sur ctx/59-f.md — son commit d'ouverture" in s1
    assert f1.startswith("# Chantier F — x\n\n" + marque + "\n\n## F1")
    assert ouverts1 == "OUVERT ctx/59-f.md\n"
    assert "marque" not in s2
    assert f2 == f1
    assert avant == "COURANT=aucun"
    assert apres == "COURANT=ctx/59-f.md"
    assert ("ÉCART: ligne: CHANTIER.md:3 — « fichier de fiches courant » n'est plus lue (NUI31) — gardée tant que "
                 "la marque d'ouverture manque" in s0)
    assert "CORRIGÉ: ligne: « fichier de fiches courant » retirée de CHANTIER.md:3" in s1
    assert carte1 == "- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n- **artefact du chantier** : aucun\n"
    assert "ligne:" not in s2
    assert ("CORRIGÉ: marque: **Ouvert.** le 2026-10-08 sur ctx/9-s.md — date de l'appel, aucun commit « Chantier S "
             "ouvert »" in s9)
    assert "CORRIGÉ: ligne:" in s9
    assert "marque" not in s10
    assert "ligne:" not in s10


# Pas sous tmp_path, comme `test_nui30_marque`.
def test_nui30_pause(init_git):
    """NUI30 : `pause` pose sa marque, refuse un doublon, un clos, un fichier absent ; `ouvrir` la lève. Sans git,
    `init_git` saute le test."""
    with tempfile.TemporaryDirectory() as tr:
        d = os.path.join(tr, "ca")
        decor_cairn(d, init_git)
        appel(["niveau", d, "--ecrire", "--date", "2026-10-08"])
        code3, s3 = appel(["pause", os.path.join(d, "ctx", "34-h.md"), "en pause le soir même", "--date", "2026-09-20"])
        code4, s4 = appel(["pause", os.path.join(d, "ctx", "34-h.md"), "encore"])
        code5, _s5 = appel(["pause", os.path.join(d, "ctx", "59-f.md"), "attend"])
        ouverts2, f5 = appel(["ouverts", d])[1], mod.lire(os.path.join(d, "ctx", "59-f.md"))
        code6, s6 = appel(["ouvrir", d, "--fiches", "ctx/59-f.md", "--titre", "x"])
        ouverts3, f6 = appel(["ouverts", d])[1], mod.lire(os.path.join(d, "ctx", "59-f.md"))
        code7, s7 = appel(["pause", os.path.join(d, "ctx", "21-z.md"), "x"])
        code8, s8 = appel(["pause", os.path.join(d, "ctx", "absent.md"), "x"])
        h3 = mod.lire(os.path.join(d, "ctx", "34-h.md"))
    marque = "**Ouvert.** le 2026-09-20."
    assert (code3, s3) == (0, "PAUSE %s le 2026-09-20\n" % os.path.join(d, "ctx", "34-h.md").replace("\\", "/"))
    assert h3.startswith("# Chantier H — x\n\n**Pause.** le 2026-09-20 — en pause le soir même\n\n## H1")
    assert code4 == 1
    assert "porte déjà **Pause.**" in s4
    assert code5 == 0
    assert ouverts2 == "OUVERTS=0\n"
    assert "**Pause.**" in f5
    assert code6 == 0
    assert " · pause levée" in s6
    assert "**Pause.**" not in f6
    assert f6.startswith("# Chantier F — x\n\n" + marque + "\n\n## F1")
    assert ouverts3 == "OUVERT ctx/59-f.md\n"
    assert code7 == 1
    assert "porte déjà **CLOS**" in s7
    assert code8 == 1
    assert s8.startswith("GARDE: fichier de fiches")
