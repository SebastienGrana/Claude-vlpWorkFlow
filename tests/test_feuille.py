"""`noyau/feuille.py` : la feuille de route, sa TODO, ses phases, ses cartes, les lettres prises — migré de
l'ancienne suite maison (REF58). Chaque `assert` garde le libellé d'origine de son `verifier` en tête de son message
(REF5), puis le diagnostic.
"""
import io
import os
import re
import tempfile

from aides import SCRIPTS, appel, ecrire, ligne_close, lire, mod

ICI = SCRIPTS     # le dossier des scripts, d'où ces tests viennent

OUVERT = "**Ouvert.** le 2026-10-08."


def ouvert(texte):
    """`texte` d'un fichier de fiches, la marque d'ouverture sous son titre `# Chantier `, comme la pose `vlp.py
    ouvrir` : `courant_de` le lit (NUI31)."""
    return re.sub(r"^(# Chantier [^\n]*\n)", r"\g<1>\n%s\n" % OUVERT, texte, count=1, flags=re.M)


def rendu(depart):
    s = io.StringIO()
    mod.carte(depart, s)
    return s.getvalue()


def test_gras_et_liens():
    """Contrôler `gras_et_liens` et `cellule` : le gras et les liens Markdown d'une cellule (chantier REP)."""
    gras_liens, cellule = mod.gras_et_liens, mod.cellule_md
    s = gras_liens("un **mot** fort")
    assert (s == "un <strong>mot</strong> fort"), ("gras_et_liens : un gras") + "\n" + str(s)
    s = gras_liens("**a** puis **b**")
    assert (s == "<strong>a</strong> puis <strong>b</strong>"), ("gras_et_liens : deux gras dans une cellule") + "\n" + str(s)
    s = gras_liens("note **importante")
    assert (s == "note **importante"), ("gras_et_liens : un ** sans paire, inchangé") + "\n" + str(s)
    s = cellule("**le `sh` seul**")
    assert (s == '<strong>le <span class="mono">sh</span> seul</strong>'), ("gras_et_liens : un gras qui contient du code") + "\n" + str(s)
    s = cellule("`**x**` puis `**` et z**")
    assert (s == '<span class="mono">**x**</span> puis <span class="mono">**</span> et z**'), ("gras_et_liens : un ** dans du code, inchangé, jamais apparié au-dehors") + "\n" + str(s)
    s = cellule("voir [la doc](https://exemple/a?b=1&c=2)")
    assert (s == 'voir <a href="https://exemple/a?b=1&amp;c=2">la doc</a>'), ("gras_et_liens : un lien https, l'URL échappée dans le href") + "\n" + str(s)
    s = gras_liens("[x](javascript:alert(1))")
    assert (s == "[x](javascript:alert(1))"), ("gras_et_liens : un lien javascript:, inchangé") + "\n" + str(s)
    s = cellule("`[t](https://u)`")
    assert (s == '<span class="mono">[t](https://u)</span>'), ("gras_et_liens : un lien dans du code, inchangé") + "\n" + str(s)
    s = cellule("**voir [la doc](https://u) et `x`** puis **y")
    assert (gras_liens(s) == s
             and s == '<strong>voir <a href="https://u">la doc</a> et <span class="mono">x</span></strong> puis **y'), ("gras_et_liens : deux passes = une, un gras englobe lien et code") + "\n" + str(s)
    s = gras_liens("[A](https://w/A_(b))")
    assert (s == '<a href="https://w/A_(b)">A</a>'), ("gras_et_liens : des parenthèses équilibrées dans l'URL") + "\n" + str(s)
    s = gras_liens('[t](https://u"x)')
    assert (s == '[t](https://u"x)'), ("gras_et_liens : un guillemet dans l'URL, inchangé") + "\n" + str(s)
    s = gras_liens('<td>**a</td><td>b**</td><a href="https://x/**y">t**</a>')
    assert (s == '<td>**a</td><td>b**</td><a href="https://x/**y">t**</a>'), ("gras_et_liens : une autre balise borne le gras, ses attributs intacts") + "\n" + str(s)


def test_feuille_phases():
    """Contrôler la TODO de la feuille en sous-listes (AVL12) : phase et score lus en tête de la case
    Coût, une pastille à gauche, une sous-liste par phase écrite, « Sans phase » en dernier."""
    assert (mod.phase_todo("**V1 · score 25 (5 × 5)** · 1 fiche") == ("V1", "25", "5 × 5", "1 fiche")
             and mod.phase_todo("**après · score ? (1 × ?)** · à cadrer") == ("après", "?", "1 × ?", "à cadrer")
             and mod.phase_todo("2 fiches") == (None, None, None, "2 fiches")), ("phase_todo : lue en tête, retirée du coût") + "\n" + str(mod.phase_todo("**V1 · score 25 (5 × 5)** · 1 fiche"))
    assert (sorted([None, "après", "V10", "V1", "V2"], key=mod.rang_phase) == ["V1", "V2", "V10", "après", None]), ("rang_phase : V1, V2, V10, après, puis sans phase") + "\n" + ""
    tailles = [mod.taille_todo(c) for c in ("1 fiche", "**V2 · score 12 (3 × 4)** · 3 fiches", "6 fiches", "à cadrer")]
    assert (tailles == ["petit", "moyen", "gros", "pas-estime"]), ("taille_todo : les parts du décompte, phase en tête comprise") + "\n" + str(tailles)
    rangs = [("5", "Cinq", "a", "**V2 · score 12 (3 × 4)** · 2 fiches", "—"),
             ("6", "Six", "b", "1 fiche", "—"),
             ("7", "Sept", "c", "**V1 · score 25 (5 × 5)** · 1 fiche", "5"),
             ("8", "Huit", "d", "**V1 · score ? (5 × ?)** · à cadrer", "—")]
    corps = mod.corps_todo(rangs, "8", [])
    ordre = re.findall(r'<li class="(?:phase-titre|carte-todo)"(?: data-phase="([^"]*)")?', corps)
    titres = re.findall(r"<h3>([^<]*)</h3>", corps)
    assert (titres == ["V1 · 2&nbsp;chantiers", "V2 · 1&nbsp;chantier", "Sans phase · 1&nbsp;chantier"]
             and corps.index('rang mono">7<') < corps.index('rang mono">8<') < corps.index('rang mono">5<') < corps.index('rang mono">6<')
             and ordre == ["V1", "V1", "V1", "V2", "V2", "aucune", ""]), ("corps_todo : V1, V2, puis Sans phase, l'ordre de la TODO gardé dans chacune — mutant : trier les cartes par score") + "\n" + str(corps)
    assert ('<span class="rang mono">7</span><span class="phase mono" data-phase="V1" title="score 25 = 5 × 5 (importance × facilité)">V1 · 25</span>'
             in corps and '<span class="meta"><span class="seg">1 fiche</span></span>' in corps and "score 25 (5" not in corps.split("title=")[-1]), ("carte_todo : pastille à gauche, détail en infobulle, la phase ôtée de droite") + "\n" + str(corps)
    seg = mod.carte_todo(("9", "Neuf", "e", "**V2 · score 6 (3 × 2)** · 5 fiches · ≈ 22 $ (estimé) · → 6 fiches en tout", "—"), "", False)
    assert ('<span class="meta"><span class="seg">5 fiches</span><span class="seg">≈ 22 $ (estimé)</span>'
             '<span class="seg">→ 6 fiches en tout</span></span>' in seg), ("carte_todo : le coût sous le titre, un segment ` · ` par ligne (dit « en pâtés » le 2026-10-12)") + "\n" + str(seg)
    methode = " ".join(open(os.path.join(ICI, "..", "methode-chantier.md"), encoding="utf-8").read().split())
    echelle = ("vaut %d en `V1`, %d en `V2`, %d en `V3`, %d `après`" % tuple(n for _, n in mod.IMPORTANCE_PHASE),
               " · ".join("%s → %d" % f for f in mod.FACILITE_FICHES), "« sans fiche » vaut 5", "note de 1 à 5")
    assert ([p for p, _ in mod.IMPORTANCE_PHASE] == ["V1", "V2", "V3", "après"] and all(e in methode for e in echelle)
             and "5 en V1, 3 en V2, 2 en V3, 1 après" in mod.aide_score() and "1 → 5 · 2 → 4 · 3 à 4 → 3 · 5 à 7 → 2 · 8 et plus → 1"
             in mod.aide_score()), ("aide du score : son échelle est celle de methode-chantier.md — mutant : changer un nombre d'un côté") + "\n" + str([e for e in echelle if e not in methode])
    assert (corps.startswith('          <li class="aide-score"><details class="aide">') and "aide-score" not in
             mod.corps_todo([r for r in rangs if r[0] == "6"], "", [])), ("aide du score : en tête des sous-listes, absente sans phase") + "\n" + str(corps[:200])
    assert ('<li class="carte-todo" data-phase="V1" data-score="25" data-taille="petit" data-pret="non">' in corps
             and '<li class="carte-todo" data-phase="V1" data-score="" data-taille="pas-estime" data-pret="oui">' in corps
             and '<li class="carte-todo" data-taille="petit" data-pret="oui">' in corps
             and '<span class="rang mono">8</span><span class="phase mono" data-phase="V1" title="score ? = 5 × ? (importance × facilité)">V1 · ?</span>'
             + mod.BADGE_COURS in corps), ("carte_todo : data- des filtres — prêt, bloqué, score ? vide, badge en cours") + "\n" + str(corps)
    sans = mod.corps_todo([r for r in rangs if r[0] == "6"], "", [])
    assert ("phase-titre" not in sans and sans.count('<li class="carte-todo"') == 1), ("corps_todo : aucune phase écrite, les cartes seules sans titre") + "\n" + str(sans)
    assert ("Rien en attente" in mod.corps_todo([], "", [])), ("corps_todo : TODO vide") + "\n" + ""
    carte_ = ["- **artefact du chantier** : aucun", "- **artefact archive** : https://a/b",
              "- **artefact enchaînement** : <https://c/d>"]
    page_ = "<header></header>\n" + mod.SOMMAIRE + "<p>x</p>\n"
    une = mod.liens_pages(page_, carte_)
    assert ('\n  <nav class="pages" aria-label="Les autres pages">Les autres pages : <a href="https://a/b">l\'archive des '
             'clos</a> · <a href="https://c/d">la page d\'enchaînement</a></nav>\n<p>x</p>' in une
             and mod.liens_pages(une, carte_) == une and mod.liens_pages(une, carte_[:1]) == page_
             and mod.liens_pages("<p>x</p>", carte_) == "<p>x</p>"), ("liens_pages : archive et enchaînement sous le sommaire, refaite sans doublon, ôtée sans lien (AVL10)") + "\n" + str(une)
    assert (mod.rang_en_cours(corps, "cartes") == "8"), ("feuille : rang en cours relu derrière la pastille") + "\n" + str(mod.rang_en_cours(corps, "cartes"))


GABARIT_FEUILLE = os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html")


ETAT_Z = ("# État\n\n## TODO\n\n| n° | Chantier | Apport | Coût | Décidé |\n|---|---|---|---|---|\n"
          "| 1 | un truc | utile | bas | 2026-01-02 |\n")


CARTE_Z = ("# Chantier courant\n\n- **alias** : z\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
           "- **fichier d'état** : ctx/08-etat.md\n- **artefact du chantier** : aucun\n")


def test_archive(tmp_path):
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        proj = os.path.join(t, "proj")
        ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_Z
               + "\nLettres de fiche déjà prises : A (Arc). Un nouveau chantier en choisit une autre.\n")
        ecrire(os.path.join(proj, "ctx", "08-etat.md"), ETAT_Z)
        ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n"
               "| `30-a.md` | chantier **ouvert** « A », `A1..A1` |\n")
        ecrire(os.path.join(proj, "ctx", "30-a.md"), "# Chantier A\n\n" + OUVERT + "\n\n**Fait.** Rien.\n\n## Le socle commun\n\n"
               "## L'ordre des fiches\n\n<!-- FICHE:A1 -->\n## A1 [x] — Seule\n**Critère de fin**\n<!-- /FICHE -->\n")
        gabarit = lire(GABARIT_FEUILLE)
        d, f = mod.zone(gabarit, "clos", "<tbody>\n", "        </tbody>")
        deux = (ligne_close("12,34 $ · " + mod.arrondi(50000)).replace("Q1–Q2", "X1")
                + ligne_close(mod.arrondi(20000)).replace("Q1–Q2", "Y1"))
        fdr = os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html")
        ecrire(fdr, mod.resommer(gabarit[:d] + deux + gabarit[f:], 2, 70000))
        archive = os.path.join(proj, "ctx", "artefacts", mod.ARCHIVE_CLOS)
        code, s = appel(["archive", proj])
        a_html, f_html = lire(archive) if os.path.isfile(archive) else "", lire(fdr)
        assert (code == 0 and "ARCHIVE 2 déplacées" in s and len(mod.lignes_clos(a_html)) == 2
                 and "Total cumulé" in a_html and "Total cumulé" not in f_html and "<!-- ZONE:clos" not in f_html), ("ARC2 : archive déplace les deux lignes et le pied") + "\n" + str(s)
        assert ("<!-- ZONE:archive" in f_html and "2 chantiers clos" in f_html and "pas encore publiée" in f_html
                 and "data-couts=" in f_html and "&lt;md&gt;" not in a_html), ("ARC2 : la feuille garde le bloc d'archive, son résumé et le graphique") + "\n" + str(f_html[-1500:])
        code, s = appel(["archive", proj])
        assert (code == 0 and "ARCHIVE 0 déplacées" in s and lire(fdr) == f_html and lire(archive) == a_html), ("ARC2 : relancé, rien ne bouge") + "\n" + str(s)
        code, s = appel(["archive", proj, "--url", "https://claude.ai/artifact/ARCH"])
        assert (code == 0 and "- **artefact archive** : https://claude.ai/artifact/ARCH" in lire(os.path.join(proj, "CHANTIER.md"))
                 and 'href="https://claude.ai/artifact/ARCH"' in lire(fdr)), ("ARC2 : --url écrit le champ et le lien") + "\n" + str(s)
        code, s = appel(["clore", proj, "--livre", "fini", "--tokens", "1000"])
        attente = os.path.join(proj, "ctx", "artefacts", "en-attente")
        assert (code == 0 and "3 chantiers clos" in lire(fdr) and "data-couts=" in lire(fdr) and len(mod.lignes_clos(lire(archive))) == 3
                 and os.path.isfile(attente) and mod.ARCHIVE_CLOS + "\thttps://claude.ai/artifact/ARCH" in lire(attente)), ("ARC2 : clore refait le bloc (3 clos) et met l'archive en attente") + "\n" + str(s)
        code, s = appel(["archive", proj])
        assert (code == 0 and "ARCHIVE 0 déplacées" in s), ("ARC2 : après clore, archive ne bouge plus rien") + "\n" + str(s)


def test_trois_lettres(tmp_path):
    """Contrôler le préfixe à trois lettres : titres lus par la carte, lettres prises."""
    CHANTIER_3 = """# Chantier courant

- **alias** : p3
- **contexte** : ctx

Lettres de fiche déjà prises : Z (Zed), RNV (Remise à niveau). Un nouveau chantier en choisit une autre.
"""

    FICHES_3 = """# Chantier RNV

## Le socle commun

rien

## L'ordre des fiches

RNV1 puis RNV2

<!-- FICHE:RNV1 -->
## RNV1 [ ] — première
**Dépend de** : rien
**Critère de fin** : rien
<!-- /FICHE -->

---

<!-- FICHE:RNV2 -->
## RNV2 [ ] — seconde
**Dépend de** : RNV1
**Critère de fin** : rien
<!-- /FICHE -->
"""

    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        proj = os.path.join(t, "p3")
        fiches3 = os.path.join(proj, "ctx", "30-rnv.md")
        ecrire(os.path.join(proj, "CHANTIER.md"), CHANTIER_3)
        ecrire(fiches3, ouvert(FICHES_3))

        s3 = rendu(proj)
        assert ("## RNV1 [ ] — première" in s3), ("3 lettres : titres lus par la carte") + "\n" + str(s3)
        assert (s3.rstrip().endswith("PROCHAINE=RNV1")), ("3 lettres : PROCHAINE") + "\n" + str(s3)

        code, s3 = appel(["valider", fiches3])
        assert (code == 0 and "VALIDE 2 fiches" in s3), ("3 lettres : marqueurs valides") + "\n" + str(s3)

        code, s3 = appel(["extraire", fiches3, "RNV2"])
        assert (code == 0 and "## RNV2 [ ] — seconde" in s3), ("3 lettres : extraire") + "\n" + str(s3)

        code, s3 = appel(["cocher", fiches3, "RNV1"])
        assert (code == 0 and "COCHÉ RNV1" in s3), ("3 lettres : cocher") + "\n" + str(s3)

        lettres3 = mod.lettres_prises(CHANTIER_3.splitlines())
        assert (lettres3 == ["Z", "RNV"]), ("3 lettres : lettres prises, une et trois lettres mêlées") + "\n" + str(repr(lettres3))

        prises = [mod.lettres_prises(["Lettres de fiche déjà prises : %s Un nouveau chantier en choisit une autre." % e])
                  for e in ("E (Un), Q (Tests, CI (rapide)).", "A.", "aucune.")]
        assert (prises == [["E", "Q"], ["A"], []]), ("lettres prises : titre à virgule, lettre sans titre") + "\n" + str(repr(prises))

        assert ((mod.lettre_de("RNV12"), mod.lettre_de("Z3")) == ("RNV", "Z")), ("3 lettres : lettre_de isole le préfixe") + "\n" + str(repr((mod.lettre_de("RNV12"), mod.lettre_de("Z3"))))

        assert (bool(mod.ENTREE_CLOS.match("- Clos le 2026-09-17 : un titre (chantier RNV)."))), ("3 lettres : une entrée de clos est reconnue") + "\n" + "non"


def test_zone_todo():
    CLOS_FEU2 = ('  <section>\n    <!-- ZONE:clos — les chantiers clos -->\n    <table><tbody>\n'
                 '          <tr><td>un clos</td></tr>\n        </tbody></table>\n  </section>\n')
    cartes_feu2 = ('  <section>\n    <!-- ZONE:todo — les chantiers possibles -->\n    <ol class="todo">\n'
                   '          <li class="carte-todo"><details><summary><span class="rang mono">29</span><span class="titre">'
                   '<span class="mono">FEU</span> — a</span><span class="meta mono">~4 fiches</span></summary>'
                   '<div class="detail">x</div></details></li>\n'
                   '          <li class="carte-todo"><details><summary><span class="rang mono">30</span><span class="titre">'
                   '<span class="mono">BTN</span> — b' + mod.BADGE_COURS + '</span><span class="meta mono">~5 fiches</span>'
                   '</summary><div class="detail">y</div></details></li>\n'
                   '        </ol>\n  </section>\n') + CLOS_FEU2
    d2, f2, forme2 = mod.zone_todo(cartes_feu2)
    assert (forme2 == "cartes" and f2 < cartes_feu2.index("<!-- ZONE:clos") and cartes_feu2[d2:f2].count("carte-todo") == 2
             and mod.rang_en_cours(cartes_feu2[d2:f2], forme2) == "30"), ("FEU2 : cartes → forme cartes, fin avant ZONE:clos, badge relu sur le rang 30") + "\n" + str((d2, f2, forme2, cartes_feu2[d2:f2]))
    tableau_feu2 = ('  <section>\n    <!-- ZONE:todo — les chantiers possibles -->\n    <table><tbody>\n'
                    '          <tr><td class="mono">29</td><td><span class="mono">FEU</span> — a</td><td>x</td></tr>\n'
                    '          <tr><td class="mono">30</td><td><span class="mono">BTN</span> — b' + mod.BADGE_COURS
                    + '</td><td>y</td></tr>\n        </tbody></table>\n  </section>\n') + CLOS_FEU2
    d2, f2, forme2 = mod.zone_todo(tableau_feu2)
    assert (forme2 == "tableau" and (d2, f2) == mod.zone(tableau_feu2, "todo", "<tbody>\n", "        </tbody>")
             and mod.rang_en_cours(tableau_feu2[d2:f2], forme2) == "30"), ("FEU2 : tableau → forme tableau, mêmes bornes que zone(), badge relu sur le rang 30") + "\n" + str((d2, f2, forme2))
    vide_feu2 = '  <section>\n    <!-- ZONE:todo — les chantiers possibles -->\n    <p>rien</p>\n  </section>\n' + CLOS_FEU2
    try:
        mod.zone_todo(vide_feu2)
        erreur_feu2 = None
    except ValueError as e:
        erreur_feu2 = str(e)
    assert (erreur_feu2 is not None and "ZONE:todo" in erreur_feu2), ("FEU2 : ni tableau ni cartes dans la zone → ValueError, jamais le <tbody> des clos") + "\n" + str(erreur_feu2)


def test_feuille_en_cartes(tmp_path):
    """FEU3 : une feuille d'avant, TODO en tableau et badge sur un rang, passe en cartes."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tc:
        ecrire(os.path.join(tc, "CHANTIER.md"),
               "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n"
               "- **artefact du chantier** : https://exemple/q\n\n"
               "Lettres de fiche déjà prises : E (Un). Un nouveau chantier en choisit une autre.\n")
        ecrire(os.path.join(tc, "ctx", "08-etat.md"),
               "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
               "| 3 | Le `sh` | a \\|\\| b <c> | 2 fiches | — |\n| 4 | **Quatre** | rien | 1 fiche | 3 |\n"
               "| 7 | Sept | [un lien](https://x/y) | à cadrer | `E` |\n\n## Journal\n")
        ecrire(os.path.join(tc, "ctx", "30-q.md"), ouvert("# Chantier Q — Un titre\n\n## Q1 [x] — a\n## Q2 [ ] — b\n"))
        gabarit = io.open(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html"), encoding="utf-8").read()
        d, f, _ = mod.zone_todo(gabarit)
        debut, fin = gabarit.rindex('<ol class="todo">', 0, d), f + len("        </ol>")
        tableau = ('<p>Un préambule gardé.</p>\n    <div class="tableau">\n      <table>\n        <thead>\n'
                   '          <tr><th>#</th><th>Chantier</th></tr>\n        </thead>\n        <tbody>\n'
                   '          <tr><td class="mono">3</td><td>vieux</td></tr>\n'
                   '          <tr><td class="mono">4</td><td>vieux' + mod.BADGE_COURS + '</td></tr>\n'
                   '        </tbody>\n      </table>\n    </div>')
        fdr = os.path.join(tc, "ctx", "artefacts", "feuille-de-route.html")
        ecrire(fdr, gabarit[:debut] + tableau + gabarit[fin:])
        code, s = appel(["feuille", tc, "--date", "2026-09-27"])
        html = io.open(fdr, encoding="utf-8").read()
        d, f, forme = mod.zone_todo(html)
        zone_t = html[html.index("<!-- ZONE:todo"):html.index("<!-- ZONE:clos")]
        rangs = mod.todo_du_fichier(mod.lignes_de(os.path.join(tc, "ctx", "08-etat.md")))
        # « Dépend de » (5e cellule) passe en flèche à gauche de la carte (gabarit en colonnes).
        absentes = ([c for r in rangs for c in r[:4] if mod.cellule_md(c) not in html[d:f]]
                    + [r[4] for r in rangs if mod.depend_todo(r[4]) not in html[d:f]])
        assert (code == 0 and forme == "cartes" and "<table" not in zone_t and "<tr" not in zone_t
                 and html[d:f].count('<li class="carte-todo"') == len(rangs) == 3 and not absentes
                 and html[d:f].count(mod.BADGE_COURS) == 1 and mod.rang_en_cours(html[d:f], forme) == "4"
                 and "<p>Un préambule gardé.</p>" in zone_t and zone_t.count("resume-todo") == 0), ("FEU3 : tableau → cartes, une par rang, chaque cellule telle quelle (« Dépend de » en flèche),"
                 " badge sur la carte 4, préambule gardé") + "\n" + str((s, absentes, zone_t))
        code, s = appel(["feuille", tc, "--date", "2026-09-28"])
        assert (code == 0 and "inchangée" in s), ("FEU3 : 2e appel inchangée") + "\n" + str(s)
        code, s = appel(["vigile", fdr])
        assert (code == 0 and s.startswith("PAGE SAINE")), ("FEU3 : vigile sur la page en cartes") + "\n" + str(s)


def test_bornes(tmp_path):
    """PLG1 : une plage va du plus petit au plus grand numéro, pas de la première à la
    dernière fiche du fichier."""
    assert (mod.plage(["REV1", "REV2", "REV3", "REV5", "REV8", "REV4"]) == "REV1–REV8"), ("PLG1 : plage par numéro — mutant : bornes rend ids[0], ids[-1]") + "\n" + str(mod.plage(["REV1", "REV2", "REV3", "REV5", "REV8", "REV4"]))
    assert (mod.plage(["X10", "X9"]) == "X9–X10"), ("PLG1 : numéro entier, X10 après X9") + "\n" + str(mod.plage(["X10", "X9"]))
    assert (mod.plage(["U1"]) == "U1"), ("PLG1 : une fiche seule, son id") + "\n" + str(mod.plage(["U1"]))
    with tempfile.TemporaryDirectory(dir=tmp_path) as tb:
        ecrire(os.path.join(tb, "CHANTIER.md"), "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **artefact du chantier** : aucun\n")
        ecrire(os.path.join(tb, "ctx", "00-INDEX.md"), "| Fichier | Lire |\n|---|---|\n| `10-e.md` | on relit |\n")
        ecrire(os.path.join(tb, "CLAUDE.md"), "| La tâche | Ouvrir |\n|---|---|\n| relire un chantier clos | `ctx/00-INDEX.md` |\n")
        ecrire(os.path.join(tb, "ctx", "30-q.md"), "# Chantier Q — q\n\n## Q2 [ ] — b\n## Q1 [ ] — a\n")
        c, sortie = appel(["ouvrir", tb, "--fiches", "ctx/30-q.md", "--titre", "q"])
        carte = open(os.path.join(tb, "CHANTIER.md"), encoding="utf-8").read()
        assert (c == 0 and "OUVERT Q Q1..Q2 " in sortie
                 and mod.courant_de(tb) == "ctx/30-q.md"), ("PLG1 : ouvrir sur Q2 puis Q1 écrit Q1..Q2") + "\n" + str(sortie + carte)


def test_voi3_lettres():
    """Contrôler les lettres entre backticks d'une ligne réelle (VOI3)."""
    LIGNE_MAPDECORATOR = "Lettres de fiche déjà prises : `T`, `U`, `R`, `M`. Un nouveau chantier en choisit"
    assert (mod.lettres_prises([LIGNE_MAPDECORATOR]) == ["T", "U", "R", "M"]), ("VOI3 : lettres entre backticks (ligne réelle de MapDecorator)") + "\n" + str(repr(mod.lettres_prises([LIGNE_MAPDECORATOR])))


def test_carte_en_colonnes(tmp_path):
    fiches_md = ("# Chantier Q\n\n## Le socle commun\n\n## L'ordre des fiches\n\n"
                 "<!-- FICHE:Q1 -->\n## Q1 [x] — Faite\n**Dépend de** : rien.\n**Critère de fin** (visuel)\nx\n"
                 "<!-- /FICHE -->\n\n"
                 "<!-- FICHE:Q2 -->\n## Q2 [ ] — Visuelle\n**Dépend de** : `Q1`.\n**Critère de fin** (visuel)\nx\n"
                 "<!-- /FICHE -->\n\n"
                 "<!-- FICHE:Q3 -->\n## Q3 [ ] — Trois dépendances\n**Dépend de** : `Q1`,\n`Q2` et `PLI3`.\n"
                 "**Critère de fin**\nx\n<!-- /FICHE -->\n")
    c1 = "≈1,1k (1 111) · 1 tours · 0,01 $"
    with tempfile.TemporaryDirectory(dir=tmp_path) as tcc:
        fiches = os.path.join(tcc, "q.md")
        page = os.path.join(tcc, "artefacts", "q.html")
        ecrire(fiches, fiches_md)
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0",
                         "--note", "Q2", "n2"])
        html = lire(page)
        li = {m.group(1): m.group(0)
              for m in re.finditer(r'<li class="fiche".*?<span class="id">(\w+)</span>.*?</li>', html, re.S)}
        assert (code == 0 and '<span class="gauche"><span class="id">Q2</span></span>' in li.get("Q2", "")
                 and '<summary><span class="titre">Visuelle</span><span class="etat">En cours</span></summary>'
                 in li.get("Q2", "")), ("colonnes : à gauche l'identifiant seul, l'état en une phrase sous le titre") + "\n" + str(s + html)
        assert ("Q1" in li and all('class="dep' not in c for c in li.values())), ("colonnes : une dépendance faite ne s'affiche plus, sur aucune fiche (Q2 dépend de Q1, faite)") + "\n" + str("%r" % li)
        assert ('<span class="etat">Après Q2</span>' in li.get("Q3", "") and " data-attend" in li.get("Q3", "")), ("colonnes : une dépendance sur la ligne suivante se lit — Q3 « Après Q2 »") + "\n" + str(li.get("Q3", ""))
        assert (mod.VISUEL in li.get("Q2", "") and mod.VISUEL not in li.get("Q1", "")
                 and mod.VISUEL not in li.get("Q3", "")), ("colonnes : « visuel » à droite d'une fiche à regarder et non faite, seulement"
                 " — mutant : la fiche faite l'a aussi") + "\n" + str("%r" % li)
        assert (('<details open><summary><span class="titre">Visuelle</span><span class="etat">En cours</span></summary>\n'
                  '        <span class="note">n2</span></details>\n        ' + mod.VISUEL + '</li>') in li.get("Q2", "")), ("colonnes : le titre et l'état dans le summary, la note dans le corps, « visuel » après") + "\n" + str(li.get("Q2", ""))
        # Le coût d'une page d'avant passe à droite : `--forme` le relit, puis le pose après le corps.
        q1 = '<span class="titre">Faite</span><span class="etat">Faite</span></summary></details>'
        ecrire(page, html.replace(q1 + '</li>', q1 + '\n        <span class="cout mono">%s</span></li>' % c1))
        code, s = appel(["page", fiches, page, "--forme"])
        apres = lire(page)
        assert (code == 0 and (q1 + '\n        <span class="cout mono">%s</span></li>' % c1) in apres
                 and mod.lis_page(apres)["Q1"][2] == c1), ("colonnes : --forme garde le coût, à droite, et le relit — mutant : coût gardé dans le corps") + "\n" + str(s + apres)
    pli5 = ('      <li class="fiche" data-etat="encours"><details open>\n'
            '        <summary><span class="id">Q2</span><span class="titre">Visuelle</span>\n'
            '        <span class="etat">en cours</span></summary>\n'
            '        <span class="note">n2</span>\n'
            '        <span class="cout mono">%s</span>\n'
            '      </details></li>\n' % c1)
    assert (mod.lis_page(pli5) == {"Q2": ("encours", "n2", c1)}), ("colonnes : une fiche de la forme PLI5, en ligne partout, se lit encore") + "\n" + str("%r" % mod.lis_page(pli5))
    neuve = ('<li class="carte-todo"><span class="gauche"><span class="rang mono">7</span></span><details><summary>'
             '<span class="titre">a</span></summary></details></li>\n<li class="carte-todo"><span class="gauche">'
             '<span class="rang mono">8</span>' + mod.BADGE_COURS + '</span><details><summary><span class="titre">b'
             '</span></summary></details></li>\n')
    ancienne = ('<li class="carte-todo"><details><summary><span class="rang mono">5</span><span class="titre">a'
                + mod.BADGE_COURS + '</span><span class="meta mono">1 fiche · dépend de : —</span></summary></details></li>\n')
    assert (mod.rang_en_cours(neuve, "cartes") == "8" and mod.rang_en_cours(ancienne, "cartes") == "5"), ("colonnes : le badge « en cours » se lit à gauche d'une carte, et dans le titre d'une carte d'avant"
             " — mutant : exiger le titre juste après le rang") + "\n" + str("%r %r" % (mod.rang_en_cours(neuve, "cartes"), mod.rang_en_cours(ancienne, "cartes")))
    assert (mod.depend_todo("`PLI`") == '<span class="dep mono">← PLI</span>'
             and mod.depend_todo("3") == '<span class="dep mono">← 3</span>' and mod.depend_todo("—") == ""
             and mod.depend_todo("`A`, `B`, `C`") == '<span class="dep mono" title="A, B, C">← 3 chantiers</span>'), ("colonnes : dépendances d'un chantier possible — code, rang, rien, et plus de deux codes") + "\n" + str("%r" % [mod.depend_todo(d) for d in ("`PLI`", "3", "—", "`A`, `B`, `C`")])


def test_decompte_todo(tmp_path):
    gabarit = lire(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html"))
    assert ([l.strip() for l in gabarit.splitlines() if "resume-todo" in l]
             == ['<p class="resume-todo"><strong>&lt;n&gt; chantiers possibles</strong></p>']), ("Dette BTN : le gabarit porte le décompte en valeur, sans style= (mutant : ancienne forme)") + "\n" + ""
    assert (mod.borne_haute_cout("~0,5 fiche") == 0.5 and mod.borne_haute_cout("~4 à 6 fiches") == 6.0
             and mod.borne_haute_cout("2-3 fiches") == 3.0 and mod.borne_haute_cout("à cadrer") is None
             and mod.borne_haute_cout("~½ fiche") == 0.5 and mod.borne_haute_cout("1½ fiche") == 1.5
             and mod.borne_haute_cout("🟡 pas estimé") is None and mod.borne_haute_cout("—") is None), ("FEU8 : borne_haute_cout — borne haute, ou None sans nombre avant « fiche »") + "\n" + str((mod.borne_haute_cout("~0,5 fiche"), mod.borne_haute_cout("~4 à 6 fiches")))
    # CLU : les cellules lues de travers à `AVL7`, recopiées de la TODO d'avant `AVL9` (69e47df~1)
    fautives = {
        "estimé comme `ACA` : 4 à 6 fiches, 15 à 22 $ (`AMD` : 7 fiches, 37,80 $ mesurés)": 6.0,
        "~3 fiches · 11 à 15 $ au taux de `MET10`, plus ≈ 4 $ de republication (2,98 $ pour 66 pages, `HAB5`) "
        "(estimé, non mesuré) · avec (0), ajouté le 2026-10-10 : 3 à 4 fiches (l'ajout estimé, non mesuré) · avec (4), "
        "ajouté le 2026-10-11 : ≈ +½ fiche (estimé, non mesuré) · avec (5), ajouté le 2026-10-11 : ≈ +½ fiche "
        "(estimé, non mesuré)": 5.0,
        "1 fiche · 3,68 $ au taux de `MET10` du kit (3,68 $ la fiche), estimé, non mesuré": 1.0,
        "1 fiche · 3,68 $ au taux de `MET10` du kit (3,68 $ la fiche), estimé, non mesuré · avec `c8`, ajouté le "
        "2026-10-11 : ≈ +½ fiche (estimé, non mesuré) · avec le contexte ignoré, ajouté le 2026-10-11 : ≈ +½ fiche "
        "(estimé, non mesuré)": 2.0,
        "2 fiches · 7,36 $ au taux de `MET10` du kit (3,68 $ la fiche), estimé, non mesuré": 2.0,
        "~1 fiche, sans code (estimé, non mesuré) · re-cadré à `MET10` : sans fiche": None,
    }
    lues_clu = {c: mod.borne_haute_cout(c) for c in fautives}
    assert (lues_clu == fautives), ("CLU : borne_haute_cout — un ajout « +½ » s'additionne, un prix par fiche et une parenthèse ne se lisent pas") + "\n" + str([(c[:40], v) for c, v in lues_clu.items() if v != fautives[c]])
    # les cellules « Coût » de la TODO du 2026-10-08, recopiées telles quelles (NUI38)
    cellules = {
        "~6 fiches, plus une nuit d'essai · ré-estimé à `MET10` (restent `NUI28` à `NUI32` et `NUI20`, `CLR` compris : "
        "7 fiches) : 14 à 21 fiches, 52 à 77 $, plus la nuit d'essai (borne 20 $)": 21.0,
        "~2 fiches de lecture et de mesure, sans code, plus un essai de Remote Build `(visuel)` : jeu ouvert, geste de "
        "l'utilisateur (estimé, non mesuré — les estimations sous-estiment) · ré-estimé à `MET10` : 4 à 6 fiches, 15 à 22 $": 6.0,
        "5 fiches, dont 2 qui demandent une réponse de l'utilisateur (REF2, REF5) et 1 de code (REF3, le script de mesure) "
        "· ré-estimé à `MET10`, re-cadré en 3 fiches : 6 à 9 fiches, 22 à 33 $ ; le refactoring, chiffré par son bilan": 9.0,
        "~1 fiche (estimé, non mesuré — les estimations sous-estiment) · ré-estimé à `MET10`, `CLV` et `OTE` compris : "
        "3,5 fiches → 7 à 10,5, 26 à 39 $": 10.5,
        "~1½ fiche (estimé, non mesuré ; ~½ avant la fonte) · ré-estimé à `MET10` : 3 à 4,5 fiches, 11 à 17 $": 4.5,
        "~1 fiche (estimé, non mesuré) · ré-estimé à `MET10` : 2 à 3 fiches, 7,4 à 11 $ · avec la recopie (clôture de "
        "`MET`) : 4 à 6 fiches, 15 à 22 $": 6.0,
        "≈ 10 $ d'essais et ≈ 1 h 45, estimés depuis `MET4`, non mesurés ; plus le juge, ~1 fiche → 2 à 3 fiches, 7,4 à "
        "11 $ · avec les 2 essais (clôture de `MET`) : +½ fiche → 2,5 à 3,5 fiches, 9 à 13 $": 3.5,
        "~5 fiches · ≈15 $ au taux du 2026-09-29 (3,03 $/fiche sur 80 clos ; estimé, non mesuré — les estimations "
        "sous-estiment : chantiers de pages joués `LOC` 5 fiches 11,74 $, `PLI` 7 fiches 17,96 $, `BTN` 7 fiches 47,08 $) "
        "· re-cadré à `MET10`, l'étape (1) seule : 1 à 1,5 fiche, 3,7 à 5,5 $ ; le reste, sur sa mesure": 1.5,
        "~1 fiche, sans code (estimé, non mesuré) · re-cadré à `MET10` : sans fiche, une séance courte, non chiffrée": None,
    }
    lues = {c: mod.borne_haute_cout(c) for c in cellules}
    assert (lues == cellules), ("NUI38 : borne_haute_cout — la dernière estimation fait foi (segment ` · `, puis `→`), ni somme ni durée, "
             "« sans fiche » → None") + "\n" + str([(c[:40], lues[c], v) for c, v in cellules.items() if lues[c] != v])
    assert (mod.est_bloque("`AAA`", ["AAA"], {"1", "2"}) is False
             and mod.est_bloque("`ZZZ`", ["AAA"], {"1", "2"}) is True
             and mod.est_bloque("3", ["AAA"], {"1", "3"}) is True
             and mod.est_bloque("1..9", ["AAA"], {"5"}) is True
             and mod.est_bloque("—", ["AAA"], {"1"}) is False
             and mod.est_bloque("`C1` de MapDecorator", ["AAA"], set()) is True), ("FEU8 : est_bloque — code absent, numéro ou plage d'un rang présent, tiret non bloquant") + "\n" + ""
    # Fichier d'état en mémoire, comme demandé par le critère de fin de FEU8 : 4 rangs, un de
    # chaque taille et un pas estimé ; deux bloqués (code `ZZZ` absent, numéro 1 encore présent).
    lignes = ["| # | Chantier | Apporte | Coût | Dépend |", "|---|---|---|---|---|",
              "| 1 | A | x | ~0,5 fiche | `AAA` |",
              "| 2 | B | x | ~4 à 6 fiches | `ZZZ` |",
              "| 3 | C | x | 2-3 fiches | 1 |",
              "| 4 | D | x | à cadrer | — |"]
    rangs = mod.todo_du_fichier(lignes)
    assert (len(rangs) == 4), ("FEU8 : todo_du_fichier lit les 4 rangs") + "\n" + str(rangs)
    ligne = mod.resume_todo(len(rangs), *mod.decompte_todo(rangs, ["AAA"]))
    assert (ligne == "4 chantiers possibles · 1 petit, 1 moyen, 1 gros, 1 pas estimé · 2 bloqués · ≈9,5 fiches estimées"), ("FEU8 : décompte de la TODO — tailles, bloqués, total estimé — mutant : borne basse au lieu de haute") + "\n" + str(ligne)
    # BTN7 : le décompte en valeur, le texte d'avant la liste replié. Ici et non au niveau du
    # module, déjà au seuil de pyright (BTN1, BTN5).
    with tempfile.TemporaryDirectory(dir=tmp_path) as tb:
        ecrire(os.path.join(tb, "CHANTIER.md"),
               "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n"
               "- **artefact du chantier** : aucun\n\n"
               "Lettres de fiche déjà prises : E (Un). Un nouveau chantier en choisit une autre.\n")
        ecrire(os.path.join(tb, "ctx", "08-etat.md"),
               "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
               "| 3 | Trois | a | 2 fiches | — |\n| 4 | Quatre | b | 1 fiche | 3 |\n\n## Journal\n")
        fdr = os.path.join(tb, "ctx", "artefacts", "feuille-de-route.html")
        lire_fdr = lambda: io.open(fdr, encoding="utf-8").read()
        # Le gabarit porte le décompte d'avant (`mono`, `style=`) : deux `feuille` n'en laissent qu'un.
        ecrire(fdr, io.open(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html"),
                            encoding="utf-8").read())
        appel(["feuille", tb, "--date", "2026-09-27"])
        code, s = appel(["feuille", tb, "--date", "2026-09-27"])
        sans = lire_fdr()
        decomptes = [l for l in sans.splitlines() if "resume-todo" in l]
        css = io.open(os.path.join(tb, "ctx", "artefacts", "vlp.css"), encoding="utf-8").read()
        assert (code == 0 and decomptes == ['    <p class="resume-todo"><strong>2 chantiers possibles</strong>'
                                             ' · 1 petit, 1 moyen · 1 bloqué · ≈3 fiches estimées</p>']
                 and ".resume-todo {" in css and ".resume-todo strong" in css), ("BTN7 : décompte en <strong>, sans style=, un seul après deux feuille sur la forme d'avant,"
                 " .resume-todo dans vlp.css — mutant : RESUME_TODO sans l'ancienne forme") + "\n" + str((s, decomptes))
        assert ('class="lecture"' not in sans), ("BTN7 : sans préambule, aucun details.lecture") + "\n" + ""
        i = sans.index('<ol class="todo">')
        ancienne = sans[:i] + "<p>Lire ainsi.</p>\n    <ul>\n      <li>un</li>\n    </ul>\n    " + sans[i:]
        vieille = os.path.join(tb, "ancienne.html")
        ecrire(vieille, ancienne)
        ecrire(fdr, ancienne)
        code, s = appel(["feuille", tb, "--date", "2026-09-27"])
        neuve = lire_fdr()
        code2, s2 = appel(["feuille", tb, "--date", "2026-09-27"])
        _, sc = appel(["comparer", vieille, fdr])
        assert (code == 0 and code2 == 0 and neuve.count('<details class="lecture">') == 1
                 and neuve == lire_fdr() and "inchangée" in s2 and "COMPARER 0 perdus" in sc
                 and ('<details class="lecture"><summary>Comment lire cette liste</summary>\n    <p>Lire ainsi.</p>\n'
                      '    <ul>\n      <li>un</li>\n    </ul>\n    </details>\n    <ol class="todo">') in neuve), ("BTN7 : préambule replié une fois dans un details.lecture fermé, texte intact, 2e feuille"
                 " inchangée — mutant : details posé sans vérifier qu'il y est") + "\n" + str((s, s2, sc))


def test_barre_todo(tmp_path):
    entete = ["| # | Chantier | Apporte | Coût | Dépend |", "|---|---|---|---|---|"]
    rangs = mod.todo_du_fichier(entete + ["| 1 | A | `sed x \\| sha256sum` | 2 fiches | — |"])
    assert (rangs == [["1", "A", "`sed x \\| sha256sum`", "2 fiches", "—"]]
             and mod.cellule_md(rangs[0][2]) == '<span class="mono">sed x | sha256sum</span>'), ("PIP1 : une barre échappée dans du code reste un caractère — 5 cellules, rendue sans \\") + "\n" + str(rangs)
    for ligne, n in (("| 2 | B | `sed x | sha256sum` | 2 fiches | — |", 6), ("| 3 | C | x | — |", 4)):
        try:
            mod.todo_du_fichier(entete + [ligne])
            dit = "aucune erreur"
        except ValueError as e:
            dit = str(e)
        assert (dit.startswith("ligne %s de la TODO : %d cellules au lieu de 5" % (ligne[2], n))), ("PIP1 : une ligne à %d cellules lève une ValueError qui la nomme — mutant : >= 5" % n) + "\n" + str(dit)
    with tempfile.TemporaryDirectory(dir=tmp_path) as tp:
        ecrire(os.path.join(tp, "CHANTIER.md"),
               "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n"
               "- **artefact du chantier** : aucun\n\n"
               "Lettres de fiche déjà prises : E (Un). Un nouveau chantier en choisit une autre.\n")
        etat = os.path.join(tp, "ctx", "08-etat.md")
        ecrire(etat, "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
                     "| 3 | Trois | a | 2 fiches | — |\n\n## Journal\n")
        fdr = os.path.join(tp, "ctx", "artefacts", "feuille-de-route.html")
        ecrire(fdr, io.open(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html"),
                            encoding="utf-8").read())
        code, s = appel(["feuille", tp, "--date", "2026-09-29"])
        avant = io.open(fdr, encoding="utf-8").read()
        assert (code == 0 and "GARDE" not in s), ("PIP1 : une TODO saine passe") + "\n" + str(s)
        ecrire(etat, "# État\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
                     "| 3 | Trois | `sed | sha256sum` | 2 fiches | — |\n\n## Journal\n")
        code, s = appel(["feuille", tp, "--date", "2026-09-29"])
        assert (code == 1 and "GARDE: ligne 3 de la TODO : 6 cellules" in s
                 and io.open(fdr, encoding="utf-8").read() == avant), ("PIP1 : feuille rend GARDE avec le numéro, sort 1, la page ne bouge pas") + "\n" + str(s)
        _, s = appel(["niveau", tp, "--date", "2026-09-29"])
        assert ("ÉCART: feuille: ligne 3 de la TODO : 6 cellules" in s), ("PIP1 : niveau compte la ligne comme un écart de la feuille") + "\n" + str(s)
