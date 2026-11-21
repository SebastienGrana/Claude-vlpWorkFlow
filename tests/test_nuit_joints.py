"""`noyau/nuit.py` : les joints d'une page publiée et le graphique `couts.svg` de la feuille — sortis de
`test_nuit.py`, qui touchait le plafond de lignes (dette `RUF`, 2026-11-21)."""

import json
import os
import pathlib
import re
import tempfile

from aides import (
    FICHES_PLI2,
    GABARIT_VLPCSS,
    SCRIPTS,
    appel,
    ecrire,
    ligne_close,
    lire,
    mod,
)

ICI = SCRIPTS     # le dossier des scripts, d'où ces tests viennent


def contrastes_couts(barre, texte):
    """CTR1 : les variables de la ligne `:root` de vlp.css, et les rapports WCAG (luminance
    relative) de `barre` puis `texte`, chacune sur `--surface` puis `--ground`."""
    racine_css = next(l for l in lire(GABARIT_VLPCSS).splitlines() if l.startswith(":root"))
    css = dict(re.findall(r"(--[\w-]+):(#[0-9a-f]{6})", racine_css))

    def luminance(c):
        v = [int(c[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        v = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in v]
        return .2126 * v[0] + .7152 * v[1] + .0722 * v[2]

    def contraste(a, b):
        la, lb = sorted((luminance(a), luminance(b)), reverse=True)
        return (la + .05) / (lb + .05)
    return css, [contraste(c, css.get(f, "#000000")) for c in (barre, texte) for f in ("--surface", "--ground")]


META_BTN1 = '<meta charset="utf-8">'
SCRIPT_BTN1 = '<script src="vlp.js"></script>'
IMG_COUTS = '<img src="couts.svg"'


def files_de(s):
    """Le dict de la ligne `FILES` d'une sortie, ou None."""
    for l in s.splitlines():
        if l.startswith("FILES "):
            return json.loads(l[len("FILES "):])
    return None


def joints_recopies(s, dossier):
    """(a) : FILES a les clés `vlp.css` et `vlp.js`, chacune vers un fichier qui existe, en
    barres obliques, dans `dossier`, identique à l'octet à sa source de `templates/`."""
    files = files_de(s)
    return (files is not None and sorted(files) == ["vlp.css", "vlp.js"]
            and all("\\" not in c and os.path.isfile(c) and os.path.samefile(c, os.path.join(dossier, n))
                    and pathlib.Path(c).read_bytes() == pathlib.Path(os.path.join(ICI, "..", "templates", n)).read_bytes()
                    for n, c in files.items()))


def balises_une_fois(html):
    """(b) : le charset une fois, en première ligne ; le script une fois, en dernière."""
    lignes = html.rstrip("\n").split("\n")
    return (html.count(META_BTN1) == 1 and html.count(SCRIPT_BTN1) == 1
            and lignes[0] == META_BTN1 and lignes[-1] == SCRIPT_BTN1)


def sans_balises(html):
    """`html` sans sa ligne de charset ni sa ligne de script."""
    return html.replace(META_BTN1 + "\n", "").replace(SCRIPT_BTN1 + "\n", "")


def projet_btn1(tab):
    """Un projet équipé minimal, sa feuille posée depuis le gabarit (comme PLI2) ; rend `(projet, feuille)`."""
    proj = os.path.join(tab, "proj")
    ecrire(os.path.join(proj, "CHANTIER.md"),
           "# C\n\n- **contexte** : ctx/\n- **fichier d'état** : ctx/08-etat.md\n"
           ""
           "- **artefact du chantier** : aucun\n\nLettres de fiche déjà prises : U (test).\n")
    ecrire(os.path.join(proj, "ctx", "08-etat.md"),
           "# État\n\n## La TODO\n\n| # | Chantier | Apporte | Coût | Dépend |\n|---|---|---|---|---|\n")
    fdr = os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html")
    ecrire(fdr, pathlib.Path(os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html")).read_text(encoding="utf-8"))
    return proj, fdr


def test_joints(tmp_path):
    """(c) d'abord : une page d'avant, sans charset ni script, les reçoit une fois ; une seconde
    régénération n'en ajoute pas — page du chantier, puis feuille de route ; un charset cité dans un commentaire
    n'est pas un charset posé."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        fiches = os.path.join(tab, "p.md")
        page = os.path.join(tab, "artefacts", "p.html")
        ecrire(fiches, FICHES_PLI2)
        appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        ecrire(page, sans_balises(lire(page)))
        assert "<meta charset" not in lire(page)
        assert "vlp.js" not in lire(page)
        code, _s = appel(["page", fiches, page])
        assert code == 0
        assert balises_une_fois(lire(page))
        code, _s = appel(["page", fiches, page])
        assert code == 0
        assert balises_une_fois(lire(page))
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        proj, fdr = projet_btn1(tab)
        ecrire(fdr, sans_balises(lire(fdr)))
        code, _s = appel(["feuille", proj])
        assert code == 0
        assert balises_une_fois(lire(fdr))
        code, _s = appel(["feuille", proj])
        assert code == 0
        assert balises_une_fois(lire(fdr))
    cite = mod.migrer_joints("<!-- %s -->\n<p>x</p>\n" % META_BTN1)
    assert cite.startswith(META_BTN1 + "\n")
    assert cite.count(META_BTN1) == 2


def test_joints_page(tmp_path):
    """(a) et (b) : `page --creer`, puis `page` sans --creer ; vlp.js modifié à la main entre deux ; puis la feuille."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        fiches = os.path.join(tab, "p.md")
        art = os.path.join(tab, "artefacts")
        page = os.path.join(art, "p.html")
        ecrire(fiches, FICHES_PLI2)
        code, s = appel(["page", fiches, page, "--creer", "--projet", "Proj", "--titre", "T", "--resultat", "R0"])
        assert code == 0
        assert joints_recopies(s, art)
        assert "CSS %s\n" % os.path.join(art, "vlp.css") in s
        assert (balises_une_fois(lire(page))), ("BTN1 : (b) page --creer — charset et script une fois chacun") + "\n" + str(lire(page)[:300])
        with open(os.path.join(art, "vlp.js"), "wb") as f:
            f.write(b"/* modifie a la main */")
        code, s = appel(["page", fiches, page])
        assert code == 0
        assert joints_recopies(s, art)
        assert (balises_une_fois(lire(page))), ("BTN1 : (b) page régénérée — charset et script une fois chacun") + "\n" + str(lire(page)[:300])
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        proj, fdr = projet_btn1(tab)
        art = os.path.dirname(fdr)
        code, s = appel(["feuille", proj])
        assert code == 0
        assert joints_recopies(s, art)
        assert "CSS %s\n" % os.path.join(art, "vlp.css") in s
        assert (balises_une_fois(lire(fdr))), ("BTN1 : (b) feuille régénérée — charset et script une fois chacun") + "\n" + str(lire(fdr)[:300])


def test_joints_commande(tmp_path):
    """`joints <dossier>` : les deux copies, et la ligne FILES seule ; un dossier absent est gardé."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        code, s = appel(["joints", tab])
        assert code == 0
        assert joints_recopies(s, tab)
        assert len(s.splitlines()) == 1
        code, s = appel(["joints", os.path.join(tab, "absent")])
        assert code == 1
        assert s.startswith("GARDE: dossier introuvable")


def test_joints_gabarits():
    """Les deux gabarits : charset en première ligne, script en dernière, une fois chacun ; aucun lien local hors joints."""
    for nom in ("artefact-chantier.html", "artefact-feuille-de-route.html"):
        gabarit = pathlib.Path(os.path.join(ICI, "..", "templates", nom)).read_text(encoding="utf-8")
        assert (balises_une_fois(gabarit)), ("BTN1 : (b) gabarit %s — charset et script une fois chacun" % nom) + "\n" + str(gabarit[:300])
        # Dette BTN : /vlp:init publie la feuille remplie à la main, sans `feuille` — un lien local vers
        # autre chose qu'un joint y reste sans fichier (l'image couts.svg y restait, cassée).
        locaux = set(re.findall(r'(?:src|href)="(?!https?:|#|&lt;)([^"]+)"', gabarit))
        assert (locaux <= set(mod.JOINTS)), ("Dette BTN : gabarit %s — ne lie en local que les joints — mutant : image couts.svg remise"
                 % nom) + "\n" + str(str(sorted(locaux)))


# --- BTN5 : le coût des chantiers clos en image, `couts.svg` et sa balise.

def projet_btn5(tab, rangs):
    """Un projet équipé minimal, sa feuille posée depuis le gabarit, `rangs` en tête de ZONE:clos ; rend
    `(projet, feuille)`."""
    proj, fdr = projet_btn1(tab)
    gabarit = lire(fdr)
    i = gabarit.index("<tbody>\n", gabarit.index("<!-- ZONE:clos")) + len("<tbody>\n")
    ecrire(fdr, gabarit[:i] + "".join(rangs) + gabarit[i:])
    return proj, fdr


def rang_clos(nom, cout):
    """Une ligne de ZONE:clos au nom `nom` et au coût `cout`."""
    return ligne_close(cout).replace("<td>Test ", "<td>%s " % nom)


def barres(chemin):
    """[(x, hauteur)] des barres de `couts.svg`, de gauche à droite ; [] sans fichier."""
    if not os.path.isfile(chemin):
        return []
    return sorted((float(x), float(h)) for x, h in re.findall(
        r'<rect class="barre" x="([\d.]+)" y="[\d.]+" width="[\d.]+" height="([\d.]+)"', lire(chemin)))


def feuille_quatre_clos(tab):
    """Quatre lignes closes, la plus récente en haut : D 4 000, C sans coût, B 2 000, A 1 000 ; rend
    `(projet, feuille, couts.svg, code, sortie)` de la première `feuille`."""
    proj, fdr = projet_btn5(tab, [rang_clos("D", mod.arrondi(4000)), rang_clos("C", "non mesuré"),
                                  rang_clos("B", mod.arrondi(2000)), rang_clos("A", mod.arrondi(1000))])
    svg = os.path.join(os.path.dirname(fdr), "couts.svg")
    code, s = appel(["feuille", proj])
    return proj, fdr, svg, code, s


def test_couts_svg(tmp_path):
    """BTN5 : quatre lignes closes — trois barres à l'échelle, chacune colorée, la ligne FILES et la ligne LIRE."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        _proj, _fdr, svg, code, s = feuille_quatre_clos(tab)
        b = barres(svg)
        h = [x[1] for x in b]
        assert code == 0
        assert len(b) == 3
        r = sorted(h)
        assert abs(2 * r[0] - r[1]) <= 1
        assert abs(4 * r[0] - r[2]) <= 1
        assert b[-1][1] == max(h)
        assert b[0][1] == min(h)
        dessin = lire(svg)
        formes = re.findall(r"<(?:rect|text)\b[^>]*>", dessin)
        assert "%s tokens</text>" % mod.arrondi(4000) in dessin
        assert formes
        assert all('fill="#' in f for f in formes)
        files = files_de(s) or {}
        assert "couts.svg" in files
        assert "\\" not in files["couts.svg"]
        assert os.path.samefile(files["couts.svg"], svg)
        assert ("\nLIRE vlp.css vlp.js couts.svg\n" in s), ("REF29 : feuille dit LIRE avec couts.svg joint — mutant : ligne LIRE retirée") + "\n" + str(s)


def test_couts_svg_balise(tmp_path):
    """BTN5 : la balise de couts.svg, son texte de remplacement et ses données ; les contrastes (CTR1) ; une feuille
    d'avant, sans balise, la reçoit à sa régénération."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        proj, fdr, svg, _code, _s = feuille_quatre_clos(tab)
        dessin = lire(svg)
        html = lire(fdr)
        alt = re.search(r'<img src="couts\.svg" alt="([^"]*)"', html)
        assert html.count(IMG_COUTS) == 1
        assert html.index(IMG_COUTS) < html.index('<details class="clos">')
        assert alt is not None
        assert "3 barres" in alt.group(1)
        assert alt.group(1).endswith("le plus cher : D")
        donnees = re.search(r'<img src="couts\.svg"[^>]* data-couts="([^"]*)">', html)
        donnees = json.loads(mod.html.unescape(donnees.group(1))) if donnees else {}
        assert (donnees == {"couleur": mod.COUTS_BARRE, "barres": [[n, t, mod.arrondi(t)] for n, t in
                             (("A", 1000), ("B", 2000), ("D", 4000))]}), ("Graphique : data-couts porte la couleur et les barres [chantier, tokens, arrondi],"
                 " de la plus ancienne à la plus récente — mutant : attribut retiré") + "\n" + str(str(donnees))
        # CTR1 : l'image recopie `--cours` et `--doux` de vlp.css, lisibles à 4,5:1 sur les deux fonds.
        css, rapports = contrastes_couts(mod.COUTS_BARRE, mod.COUTS_TEXTE)
        assert mod.COUTS_BARRE == css.get("--cours")
        assert mod.COUTS_TEXTE == css.get("--doux")
        assert min(rapports) >= 4.5
        print("  CTR1 contrastes (barre/surface, barre/ground, texte/surface, texte/ground) : %s"
              % " ".join("%.2f" % r for r in rapports))
        ecrire(fdr, mod.BALISE_COUTS.sub("", html))
        appel(["feuille", proj])
        assert (lire(fdr).count(IMG_COUTS) == 1), ("BTN5 : une feuille d'avant, sans balise, la reçoit à sa régénération") + "\n" + str(lire(fdr)[-3000:])
        appel(["feuille", proj])
        assert lire(fdr).count(IMG_COUTS) == 1
        assert lire(svg) == dessin


def test_couts_svg_sans_cout(tmp_path):
    """Sans coût (les lignes d'exemple du gabarit seules) : ni fichier — un ancien est retiré —, ni balise ; des coûts
    mesurés, tous à 0 (dette BTN) : rien à dessiner, et pas de division par un maximum nul."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        proj, fdr = projet_btn5(tab, [rang_clos("C", "non mesuré")])
        svg = os.path.join(os.path.dirname(fdr), "couts.svg")
        ecrire(svg, "<svg/>")
        code, s = appel(["feuille", proj])
        assert code == 0
        assert not os.path.exists(svg)
        assert IMG_COUTS not in lire(fdr)
        assert "couts.svg" not in (files_de(s) or {})
        assert ("\nLIRE vlp.css vlp.js\n" in s), ("REF29 : feuille sans couts.svg dit LIRE sans lui") + "\n" + str(s)
    with tempfile.TemporaryDirectory(dir=tmp_path) as tab:
        proj, fdr = projet_btn5(tab, [rang_clos("B", mod.arrondi(0)), rang_clos("A", mod.arrondi(0))])
        code, s = appel(["feuille", proj])
        assert code == 0
        assert not os.path.exists(os.path.join(os.path.dirname(fdr), "couts.svg"))
        assert IMG_COUTS not in lire(fdr)
