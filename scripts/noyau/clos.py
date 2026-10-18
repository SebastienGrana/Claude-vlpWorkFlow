"""La ZONE:clos d'une feuille de route, son recompte, et comparer (REF46 ; plan de `REF18`, note `122`).

Sorti de `vlp_coeur.py`, qui le ré-exporte. Un nom d'un module pas encore sorti se lit `coeur.<nom>`, au moment
de l'appel (`noyau/facade.py`) ; un nom d'un module chargé avant se lit par import.
"""
import html.parser
import io
import json
import os
import re

from noyau.facade import coeur
from noyau.commun import (lignes_de, lignes_index, lire)
from noyau.carte import (equipe)
from noyau.sessions import (decouper, sessions_de, totaux, totaux_a_clore)
from noyau.page import (arrondi, dollars, esc, essais_entiers, mesure, milliers, plus, recopier_joints)
from noyau.notes import (abri_de_page, chemin_abri, ecrire_abri, lire_abri, page_du_fichier)
from noyau.feuille import (champ, gras_et_liens, page_clos, page_feuille, rafraichir_couts, zone)

__all__ = [
    "BRUT", "RANG_CLOS", "PIED_CLOS", "GABARIT_FEUILLE", "PRIX_CLOS", "prix_clos", "texte_cout_clos", "lignes_clos",
    "total_clos", "COUTS_SVG", "COUTS_TAILLE", "COUTS_BARRE", "COUTS_TEXTE", "BALISE_COUTS", "DETAILS_CLOS",
    "couts_clos", "svg_couts", "donnees_couts", "balise_couts", "ecrire_couts", "PLAGE_CLOS", "PLAGE_INDEX",
    "signe", "recompte", "CELLULE_CLOS", "MARQUE_REC", "MARQUE_GARDE", "MARQUE_ESSAIS", "marquer", "ajout_essais",
    "marquer_essais", "clos_du_projet", "cmd_repeindre", "poser_lien", "cmd_lien", "cmd_liens", "cmd_recompter",
    "ecrire_clos", "cmd_recompter_clos", "marquer_prix", "copie_fait", "copie_bilan", "copie_abri", "ecrire_copies",
    "poser_prix", "JOUE_LOUCHE", "JOUE_PRIX", "ESTIME_NON_MARQUE", "recaler_texte", "cmd_prix", "resume_clos",
    "resommer", "migrer_feuille", "CHEVRONS_HREF", "migrer_clos", "BLOC", "Extracteur", "textes_visibles",
    "COMMENTAIRE", "BALISE_STYLE", "LIEN_CSS", "defauts_page", "cmd_vigile", "cmd_vigile_hook",
]


# --- la ZONE:clos d'une feuille de route -------------------------------------
# Lue par `clore`, qui y ajoute une ligne à chaque clôture, et par
# `niveau --ecrire`, qui pose sur une feuille d'avant le 2026-09-17 ce que le
# gabarit a depuis : le bloc repliable et l'estimation en dollars du pied — et
# convertit les lignes écrites avant `gras_et_liens`.

# Le coût brut d'une cellule : entre parenthèses (`≈1,5k (1 500)`), ou nu, fait de
# chiffres seuls, sous 1 000 (`arrondi`) — plage, date et pied n'en sont pas (chantier TAR).
BRUT = re.compile(r'<td class="mono">(?:[^<]*\((\d[\d ]*)\)|(\d+))</td>')
# `clore` écrit ses lignes à dix espaces, et les repère à dix espaces.
RANG_CLOS = re.compile(r"          <tr>\n.*?          </tr>\n", re.S)
PIED_CLOS = re.compile(r'(Total cumulé</td><td class="mono"><strong>.*?</strong></td>)<td[^>]*>([^<]*)</td>', re.S)
GABARIT_FEUILLE = "templates/artefact-feuille-de-route.html"
# Le prix mesuré en tête d'une cellule Tokens, posé par `clore` — `dollars` (chantier TAU).
PRIX_CLOS = re.compile(r'<td class="mono">(\d+,\d\d) \$ · ')


def prix_clos(corps):
    """(usd, n) : la somme des prix en tête de cellule Tokens des lignes de `corps`, et leur
    nombre ; `usd` vaut `None` si aucune n'en porte (chantier TAU)."""
    from decimal import Decimal
    prix = [Decimal(m.group(1).replace(",", ".")) for r in lignes_clos(corps) for m in [PRIX_CLOS.search(r)] if m]
    return (sum(prix) if prix else None), len(prix)


def texte_cout_clos(usd, n_usd, n):
    """`47,08 $` (toutes les lignes closes au prix mesuré), `47,08 $ sur 2 clos mesurés` (une
    partie), ou `""` (aucune) — partagé par `resommer` et `resume_clos` (chantier TAU)."""
    if usd is None:
        return ""
    return dollars(usd) if n_usd == n else "%s sur %d clos mesurés" % (dollars(usd), n_usd)


def lignes_clos(corps):
    """Les `<tr>` de chantiers clos d'un corps de table — les lignes d'exemple
    du gabarit, reconnaissables à leurs `<…>`, n'en sont pas."""
    return [r for r in RANG_CLOS.findall(corps) if '<td class="mono">&lt;' not in r]


def total_clos(corps):
    """La somme des coûts bruts — entre parenthèses, ou nus sous 1 000 — d'un corps de table."""
    return sum(int(re.sub(r"\D", "", entre or nu)) for entre, nu in BRUT.findall(corps))


# Le coût des chantiers clos en image (chantier BTN), joint à la feuille comme vlp.css. Une image
# ne lit pas les variables de la page : couleurs en dur, recopies de `--cours` (barres) et `--doux`
# (traits, chiffres) de vlp.css — un test garde l'égalité (CTR1) ; chaque forme porte son `fill`.
COUTS_SVG = "couts.svg"
COUTS_TAILLE = (640, 160, 24)  # largeur, hauteur, bandeau du maximum en haut
COUTS_BARRE, COUTS_TEXTE = "#8f5a0f", "#6e6151"
BALISE_COUTS = re.compile(r'[ \t]*<img src="couts\.svg"[^>]*>\n')
DETAILS_CLOS = re.compile(r'^([ \t]*)<details class="clos">', re.M)


def couts_clos(html):
    """[(chantier, tokens)] des lignes de `ZONE:clos` qui ont un coût brut (`BRUT`), du plus ancien
    au plus récent — la table met le plus récent en haut. Pas de zone, ou aucun coût au-dessus de 0 :
    [] — rien à dessiner, et `svg_couts` ne divise pas par un maximum nul (dette BTN)."""
    try:
        d, f = zone(html, "clos", "<tbody>\n", "        </tbody>")
    except ValueError:
        return []
    couts = []
    for r in lignes_clos(html[d:f]):
        if BRUT.search(r):
            nom = re.search(r"<td>(.*?)</td>", r, re.S)
            nom = re.sub(r'<span class="badge".*?</span>', "", nom.group(1) if nom else "")
            couts.append((re.sub(r"<[^>]+>", "", nom).strip(), total_clos(r)))
    return couts[::-1] if any(t for _, t in couts) else []


def svg_couts(html, couts=None):
    """Le SVG du coût des chantiers clos (`couts_clos`, ou `couts` donnés), ou None sans aucun coût :
    une barre par chantier, du plus ancien à gauche au plus récent à droite, hauteur proportionnelle
    aux tokens, la plus haute pleine hauteur ; en haut à gauche, le maximum (`arrondi`) suivi de
    « tokens »."""
    couts = couts_clos(html) if couts is None else couts
    if not couts:
        return None
    largeur, hauteur, bandeau = COUTS_TAILLE
    haut = max(t for _, t in couts)
    pas = largeur / len(couts)
    barres = "".join('<rect class="barre" x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
                     % (i * pas + pas * .1, hauteur - h, pas * .8, h, COUTS_BARRE)
                     for i, h in enumerate((hauteur - bandeau) * t / haut for _, t in couts))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d">'
            '<text x="0" y="16" font-family="system-ui,sans-serif" font-size="14" fill="%s">%s tokens</text>'
            '%s<rect x="0" y="%d" width="%d" height="1" fill="%s"/></svg>\n'
            % (largeur, hauteur, COUTS_TEXTE, arrondi(haut), barres, hauteur - 1, largeur, COUTS_TEXTE))


def donnees_couts(couts):
    """`data-couts` de la balise : le JSON `{"couleur", "barres": [[chantier, tokens, arrondi]]}`
    que `vlp.js` donne à Chart.js — la couleur et l'arrondi restent ici —, échappé pour un attribut."""
    brut = json.dumps({"couleur": COUTS_BARRE,
                       "barres": [[html.unescape(n), t, arrondi(t)] for n, t in couts]}, ensure_ascii=False)
    return brut.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def balise_couts(html, couts=None):
    """La balise `<img src="couts.svg">` de `#clos`, juste avant `details.clos` : posée une fois
    (une feuille d'avant la reçoit), son `alt` refait — nombre de barres, chantier le plus cher —
    et ses barres dans `data-couts` (`donnees_couts`) ; retirée sans aucun coût, ou sans
    `details.clos`. `couts` : les barres, lues ailleurs (`couts_du_projet`, chantier ARC)."""
    sans = BALISE_COUTS.sub("", html)
    couts, m = couts_clos(sans) if couts is None else couts, DETAILS_CLOS.search(sans)
    if not couts or not m:
        return sans
    nom = max(couts, key=lambda c: c[1])[0]
    alt = ("Coût des chantiers clos en tokens : %d barres, du plus ancien au plus récent ; le plus cher : %s"
           % (len(couts), nom)).replace('"', "&quot;")
    return sans[:m.start()] + '%s<img src="%s" alt="%s" data-couts="%s">\n' % (
        m.group(1), COUTS_SVG, alt, donnees_couts(couts)) + sans[m.start():]


def ecrire_couts(page, html, couts=None):
    """Écrit `couts.svg` à côté de la feuille `page` si `html` porte sa balise (`balise_couts`), le
    retire sinon. Rend `{"couts.svg": chemin}`, à joindre à la ligne `FILES`, ou {}."""
    chemin = os.path.join(os.path.dirname(os.path.abspath(page)), COUTS_SVG)
    svg = svg_couts(html, couts) if BALISE_COUTS.search(html) else None
    if svg is None:
        if os.path.isfile(chemin):
            os.remove(chemin)
        return {}
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write(svg)
    return {COUTS_SVG: chemin}


PLAGE_CLOS = re.compile(r'<td class="mono">([A-Z]{1,3})[0-9]+(?:–[A-Z]{1,3}[0-9]+)?</td>')
PLAGE_INDEX = re.compile(r"^\|\s*`([^`]+)`\s*\|.*`([A-Z]{1,3})[0-9]+\.\.[A-Z]{1,3}[0-9]+`")


def signe(n):
    return ("-" if n < 0 else "+") + milliers(abs(n))


def recompte(chemin):
    """(recompté ou None, méthode, essais, usd) d'un fichier de fiches clos : le nombre de la ligne `TOTAL` de
    `cout`, ou None et la raison de le garder — sans session, transcription absente, `DÉCOUPE
    aucune`, découpe à zéro (chantier REC). `essais` : les tokens de ses essais, ceux de la découpe
    ou, sans découpe, des sessions entières (`essais_entiers`) — pour `--essais` (chantier ESD).
    `usd` : le prix de la ligne `TOTAL`, None sans découpe — pour `--clos` (PRP3)."""
    lignes = lignes_de(chemin)
    ids = sessions_de(lignes)
    if not ids:
        return None, "gardé — sans session", 0, None
    for s in ids:
        if mesure().resoudre(s)[1]:
            return None, "gardé — transcription absente (%s)" % s, 0, None
    decoupe, pourquoi, gardes = decouper(chemin, lignes)
    if not decoupe:
        gardes = []
        essais = essais_entiers(ids, gardes)[0]
        manque = " · %d transcript(s) d'essai non mesuré(s)" % len(gardes) if gardes else ""
        return None, "gardé — DÉCOUPE aucune (%s)%s" % (pourquoi[0], manque), essais, None
    if any(g.startswith("GARDE: découpe à zéro") for g in gardes):
        return None, "gardé — découpe à zéro", 0, None
    total = plus(*totaux(decoupe))
    return total[0], "découpe", totaux(decoupe)[2][0], total[2]


# La cellule de coût d'une ligne close, seule sur sa ligne (`clore`), et les marques de
# `recompter --ecrire` : en tête, jamais après le brut, que `BRUT` ne lit qu'en fin de cellule.
CELLULE_CLOS = re.compile(r'(\n            <td class="mono">)([^<\n]*)(</td>\n)')
MARQUE_REC = "recompté (REC), était "
MARQUE_GARDE = "non recompté — "
MARQUE_ESSAIS = "essais (ESD) "


def marquer(cellule, brut, recompte_, methode):
    """La cellule de coût après `--ecrire` : le recompté au format de `clore` et l'ancien chiffre,
    ou le chiffre gardé et sa raison — la même cellule si rien n'est à marquer."""
    entre = lambda v: v if "(" in v or not v.isdigit() else "(%s)" % v   # un nu sous 1 000 reste lu
    if recompte_ is None:
        if MARQUE_GARDE in cellule:
            return cellule
        return "%s%s · %s" % (MARQUE_GARDE, esc(methode.replace("gardé — ", "", 1)), entre(cellule))
    if recompte_ == brut:
        return cellule
    esd = cellule.split(" · ")[0] + " · " if cellule.startswith(MARQUE_ESSAIS) else ""   # gardée en tête
    reste = cellule[len(esd):]
    marque = reste.split(" · ")[0] if reste.startswith(MARQUE_REC) else MARQUE_REC + milliers(brut)
    return "%s%s · %s" % (esd, marque, entre(arrondi(recompte_)))


def ajout_essais(cellule, brut, recompte_, methode, essais):
    """Ce que `recompter --essais` ajoute à une cellule close (chantier ESD) : rien si elle porte
    déjà la marque ; un gardé `DÉCOUPE aucune`, ses essais ; un découpé, ses essais sans passer
    le recompté ; tout autre gardé, rien. Seul endroit de la règle : l'affichage et l'écriture."""
    if MARQUE_ESSAIS in cellule:
        return 0
    if methode.startswith("gardé — DÉCOUPE aucune"):
        return essais
    if methode == "découpe":
        return max(0, min(essais, recompte_ - brut))
    return 0


def marquer_essais(cellule, brut, ajout):
    """La cellule après `recompter --essais --ecrire` : la marque et l'ajout en tête, la cellule
    d'avant sans son chiffre, puis le chiffre + l'ajout en fin, où `BRUT` le lit."""
    if not ajout:
        return cellule
    tete = cellule.rsplit(" · ", 1)[0] + " · " if " · " in cellule else ""
    n = arrondi(brut + ajout)
    return "%s%s · %s%s" % (MARQUE_ESSAIS, signe(ajout), tete, n if "(" in n else "(%s)" % n)


def clos_du_projet(projet, sortie):
    """Les chantiers clos d'un projet : `(feuille, début, fin de ZONE:clos, rangs)`, chaque rang
    `(ligne, préfixe, coût inscrit, fichier de fiches ou None)` — le fichier, que l'index (et son
    archive) nomme au même préfixe. None après une `GARDE:` (`recompter`, `repeindre`)."""
    if not equipe(projet):
        sortie.write("GARDE: pas de CHANTIER.md dans %s\n" % projet)
        return None
    page = page_clos(projet)
    if not os.path.isfile(page):
        sortie.write("GARDE: feuille de route introuvable : %s\n" % page)
        return None
    html = lire(page)
    try:
        d, f = zone(html, "clos", "<tbody>\n", "        </tbody>")
    except ValueError as e:
        sortie.write("GARDE: %s\n" % e)
        return None
    carte_ = lignes_de(os.path.join(projet, "CHANTIER.md"))
    contexte = champ(carte_, "contexte", "context AI/")
    index = champ(carte_, "index", os.path.join(contexte, "00-INDEX.md"))
    fichiers = {}
    for l in lignes_index(projet, index):
        m = PLAGE_INDEX.match(l)
        if m:
            fichiers.setdefault(m.group(2), os.path.join(projet, contexte, m.group(1)))
    rangs = []
    for r in lignes_clos(html[d:f]):
        m = PLAGE_CLOS.search(r)
        if m:
            chemin = fichiers.get(m.group(1))
            rangs.append((r, m.group(1), total_clos(r), chemin if chemin and os.path.isfile(chemin) else None))
    return html, d, f, rangs


def cmd_repeindre(projet, sortie, a_blanc=False):
    """Chaque page de chantier clos qui ne lie pas encore `vlp.css` passe par `page --forme`
    puis par `vigile`, dans une copie : refusée, l'originale ne bouge pas (chantier HAB)."""
    import shutil
    import tempfile
    parcours = clos_du_projet(projet, sortie)
    if parcours is None:
        return 1
    vues, n = set(), {"repeintes": 0, "avec lien": 0, "sans lien": 0, "refusées": 0, "déjà": 0, "sans page": 0}
    for _, prefixe, _, chemin in parcours[3]:
        page = page_du_fichier(chemin) if chemin else None
        if page in vues:
            continue
        vues.add(page)
        if not chemin or not page or not os.path.isfile(page):
            n["sans page"] += 1
            sortie.write("SANS PAGE %s · %s\n" % (prefixe, page or "fichier de fiches introuvable"))
            continue
        if 'href="vlp.css"' in lire(page):
            n["déjà"] += 1
            continue
        with tempfile.TemporaryDirectory() as tmp:
            copie = os.path.join(tmp, os.path.basename(page))
            shutil.copyfile(page, copie)
            if os.path.isfile(chemin_abri(page)):
                shutil.copyfile(chemin_abri(page), chemin_abri(copie))
            rendu = io.StringIO()
            code = coeur.main(["page", chemin, copie, "--forme"], rendu)
            if code == 0:
                rendu = io.StringIO()
                code = coeur.main(["vigile", copie], rendu)
            if code != 0:
                n["refusées"] += 1
                gardes = [l for l in rendu.getvalue().splitlines() if l.startswith("GARDE:")]
                sortie.write("".join("%s · %s\n" % (g, page) for g in gardes) or "GARDE: refusée · %s\n" % page)
                continue
            if not a_blanc:
                shutil.copyfile(copie, page)
                shutil.copyfile(chemin_abri(copie), chemin_abri(page))
                recopier_joints(os.path.dirname(os.path.abspath(page)))
            lien = lire_abri(chemin_abri(copie)).get("lien")
        n["repeintes"] += 1
        n["avec lien" if lien else "sans lien"] += 1
        sortie.write("REPEINTE %s · %s\n" % (page, "lien %s" % lien if lien else "sans lien"))
    sortie.write("REPEINDRE %s%s\n" % (" · ".join("%d %s" % (v, k) for k, v in n.items()),
                                        " · à blanc, rien d'écrit" if a_blanc else ""))
    return 0


def poser_lien(page, url):
    """Écrit `url` dans la section `## Lien` du `.md` de `page` (créé depuis la page s'il manque) ;
    rend "écrit" ou "déjà" (chantier HAB)."""
    md = chemin_abri(page)
    parts = lire_abri(md) if os.path.exists(md) else abri_de_page(lire(page))
    if parts.get("lien") == url and os.path.exists(md):
        return "déjà"
    parts["lien"] = url
    ecrire_abri(md, parts)
    return "écrit"


def cmd_lien(page, url, sortie):
    if not os.path.isfile(page):
        sortie.write("GARDE: page introuvable : %s\n" % page)
        return 1
    if not re.match(r"https://claude\.ai/\S+$", url):
        sortie.write("GARDE: lien inattendu : %s — une URL https://claude.ai/…\n" % url)
        return 1
    sortie.write("LIEN %s · %s · %s\n" % (poser_lien(page, url), chemin_abri(page), url))
    return 0


def cmd_liens(projet, sortie):
    """Le lien de chaque ligne de `ZONE:clos` posé dans le `.md` de sa page (parcours de
    `recompter`). Deux lignes, deux liens pour une page : rien d'écrit, `DOUBLON`."""
    parcours = clos_du_projet(projet, sortie)
    if parcours is None:
        return 1
    par_page, n = {}, {"écrits": 0, "déjà": 0, "doublons": 0, "sans lien": 0, "sans page": 0}
    for r, prefixe, _, chemin in parcours[3]:
        page = page_du_fichier(chemin) if chemin else None
        if not page or not os.path.isfile(page):
            n["sans page"] += 1
            continue
        m = re.search(r'<a href="(https://claude\.ai/[^"]+)"', r)
        if not m:
            n["sans lien"] += 1
            sortie.write("SANS LIEN %s · %s\n" % (prefixe, page))
            continue
        par_page.setdefault(page, set()).add(m.group(1))
    for page, urls in par_page.items():
        if len(urls) > 1:
            n["doublons"] += 1
            sortie.write("DOUBLON %s · %s\n" % (page, " · ".join(sorted(urls))))
            continue
        fait = poser_lien(page, urls.pop())
        n["écrits" if fait == "écrit" else "déjà"] += 1
    sortie.write("LIENS %s\n" % " · ".join("%d %s" % (v, k) for k, v in n.items()))
    return 0


def cmd_recompter(projet, sortie, ecrire=False, essais=False, a_clore=False):
    """Chaque ligne de `ZONE:clos` recomptée par `cout` sur son fichier de fiches, que l'index
    nomme au même préfixe ; n'écrit rien sans `ecrire` (chantier REC). Avec `--essais`,
    n'ajoute que la part essais (chantier ESD). `a_clore` : chaque ligne recomptée finit par
    `à clore` et `après clore` (`totaux_a_clore`), ou `sans appel clore` (chantier APC)."""
    parcours = clos_du_projet(projet, sortie)
    if parcours is None:
        return 1
    rangs = parcours[3]
    porteurs = {}
    for _, prefixe, _, chemin in rangs:
        for s in sessions_de(lignes_de(chemin)) if chemin else []:
            porteurs.setdefault(s, set()).add(prefixe)
    n = inscrit = ecart = recoivent = ajoute = 0
    neufs = {}      # chaque ligne et sa réécriture, toutes calculées avant d'écrire
    for r, prefixe, brut, chemin in rangs:
        recompte_, methode, part, _ = recompte(chemin) if chemin else (None, "gardé — fichier introuvable", 0, None)
        autres = sorted({p for s in (sessions_de(lignes_de(chemin)) if chemin else [])
                         for p in porteurs[s]} - {prefixe})
        partage = " · partagée avec %s" % ", ".join(autres) if autres else ""
        if essais:
            c = CELLULE_CLOS.search(r)
            a = ajout_essais(c.group(2), brut, recompte_, methode, part) if c else 0
            inscrit, recoivent, ajoute = inscrit + brut, recoivent + (a > 0), ajoute + a
            sortie.write("%s inscrit %s · essais %s · ajout %s · %s%s%s\n" % (
                prefixe, milliers(brut), milliers(part), signe(a), methode, partage,
                " · déjà ajoutés (ESD)" if c and MARQUE_ESSAIS in c.group(2) else ""))
            neufs[r] = CELLULE_CLOS.sub(lambda c: c.group(1) + marquer_essais(c.group(2), brut, a)
                                        + c.group(3), r, count=1)
            continue
        e = 0 if recompte_ is None else recompte_ - brut
        n, inscrit, ecart = n + (recompte_ is not None), inscrit + brut, ecart + e
        clore_ = ""
        if a_clore and recompte_ is not None:
            avant = totaux_a_clore(chemin, lignes_de(chemin))
            clore_ = " · sans appel clore" if avant is None else " · à clore %s · après clore %s" % (
                milliers(plus(*avant)[0]), milliers(recompte_ - plus(*avant)[0]))
        sortie.write("%s inscrit %s · recompté %s · écart %s · %s%s%s\n" % (
            prefixe, milliers(brut), "gardé" if recompte_ is None else milliers(recompte_), signe(e), methode,
            partage, clore_))
        neufs[r] = CELLULE_CLOS.sub(lambda c: c.group(1) + marquer(c.group(2), brut, recompte_, methode)
                                    + c.group(3), r, count=1)
    if essais:
        sortie.write("ESSAIS %d clos · %d reçoivent · inscrit %s · avec essais %s · ajout %s\n" % (
            len(rangs), recoivent, milliers(inscrit), milliers(inscrit + ajoute), signe(ajoute)))
    else:
        sortie.write("RECOMPTE %d clos · %d recomptés · %d gardés · inscrit %s · recompté %s · écart %s\n" % (
            len(rangs), n, len(rangs) - n, milliers(inscrit), milliers(inscrit + ecart), signe(ecart)))
    if ecrire:
        ecrire_clos(projet, parcours, neufs, sortie)
    return 0


def ecrire_clos(projet, parcours, neufs, sortie):
    """`ZONE:clos` avec chaque ligne de `neufs` remplacée, pied et résumé resommés, `couts.svg`
    refait — la fin de `recompter --ecrire`, `--clos` compris (PRP3)."""
    html, d, f, rangs = parcours
    page = page_clos(projet)
    corps = html[d:f]
    neuf_corps = RANG_CLOS.sub(lambda m: neufs.get(m.group(0), m.group(0)), corps)
    avant, apres = total_clos(corps), total_clos(neuf_corps)
    usd, n_usd = prix_clos(neuf_corps)
    neuf = resommer(html[:d] + neuf_corps + html[f:], len(lignes_clos(neuf_corps)), apres, usd, n_usd)
    neuf = balise_couts(neuf) if page == page_feuille(projet) else neuf
    if neuf != html:
        with open(page, "w", encoding="utf-8", newline="") as fh:
            fh.write(neuf)
    rafraichir_couts(projet, page, neuf)
    sortie.write("ÉCRIT %d cellules · total %s → %s\n" % (
        sum(neufs.get(r, r) != r for r, _, _, _ in rangs), milliers(avant), milliers(apres)))


def cmd_recompter_clos(projet, sortie, ecrire, clos):
    """`recompter --clos` : le seul clos `clos` recompté ; avec `ecrire`, ses quatre copies du coût —
    la cellule d'archive (`ecrire_clos`), puis `ecrire_copies` (PRP3)."""
    parcours = clos_du_projet(projet, sortie)
    if parcours is None:
        return 1
    rang = next((rg for rg in parcours[3] if rg[1] == clos), None)
    if rang is None:
        sortie.write("GARDE: clos %s absent de ZONE:clos — rien d'écrit\n" % clos)
        return 1
    r, _, brut, chemin = rang
    recompte_, methode, _, usd = recompte(chemin) if chemin else (None, "gardé — fichier introuvable", 0, None)
    sortie.write("%s inscrit %s · recompté %s · écart %s · %s\n" % (
        clos, milliers(brut), "gardé" if recompte_ is None else milliers(recompte_),
        signe(0 if recompte_ is None else recompte_ - brut), methode))
    if not ecrire:
        return 0
    neuf = CELLULE_CLOS.sub(lambda c: c.group(1) + marquer_prix(c.group(2), brut, recompte_, methode, usd)
                            + c.group(3), r, count=1)
    ecrire_clos(projet, parcours, {r: neuf}, sortie)
    ecrire_copies(chemin, usd, neuf != r, sortie)
    return 0


def marquer_prix(cellule, brut, recompte_, methode, usd):
    """`marquer` pour `--clos` : le prix d'en tête (`PRIX_CLOS`) mis à part, puis reposé — le
    recompté s'il est connu, sinon l'ancien (PRP3)."""
    m = re.match(r'(\d+,\d\d \$) · ', cellule)
    prix = dollars(usd) if usd is not None else (m.group(1) if m else None)
    marque = marquer(cellule[m.end():] if m else cellule, brut, recompte_, methode)
    return "%s · %s" % (prix, marque) if prix else marque


def copie_fait(chemin, usd):
    """La ligne `**Fait.**` de `chemin` recalée sur `usd` : écrite ou non ; ValueError sans ligne
    à joué (PRP3)."""
    lignes = lignes_de(chemin)
    k = next((k for k, l in enumerate(lignes) if l.startswith("**Fait.**") and JOUE_PRIX.search(l)), None)
    if k is None:
        raise ValueError("ligne **Fait.** avec un joué absente de %s" % chemin)
    vieille, lignes[k] = lignes[k], recaler_texte(lignes[k], usd, tout=True)[0]
    if lignes[k] != vieille:
        coeur.ecrire_par_tmp([(chemin, "\n".join(lignes) + "\n")])
    return lignes[k] != vieille


def copie_bilan(page, usd):
    """La `ZONE:bilan` de `page` recalée sur `usd` : écrite ou non ; ValueError sans page, sans zone
    ou sans joué dedans (PRP3)."""
    if not os.path.isfile(page):
        raise ValueError("page introuvable : %s" % page)
    pg = lire(page)
    d, f = zone(pg, "bilan", "\n", "  </section>")
    if not JOUE_PRIX.search(pg[d:f]):
        raise ValueError("ZONE:bilan sans joué : %s" % page)
    neuf = pg[:d] + recaler_texte(pg[d:f], usd, tout=True)[0] + pg[f:]
    if neuf != pg:
        coeur.ecrire_par_tmp([(page, neuf)])
    return neuf != pg


def copie_abri(md, usd):
    """Le bilan du `.md` d'abri `md` recalé sur `usd` (`ecrire_abri`) : écrit ou non ; ValueError sans
    `.md` ou sans joué au bilan (PRP3)."""
    parts = lire_abri(md) if os.path.isfile(md) else None
    if parts is None or not any(JOUE_PRIX.search(b) for b in parts["bilan"]):
        raise ValueError(".md d'abri sans joué au bilan : %s" % md)
    bilan = [recaler_texte(b, usd, tout=True)[0] for b in parts["bilan"]]
    if bilan != parts["bilan"]:
        ecrire_abri(md, dict(parts, bilan=bilan))
    return bilan != parts["bilan"]


def ecrire_copies(chemin, usd, archive, sortie):
    """Les trois autres copies du coût d'un clos recalées sur `usd` : `copie_fait`, `copie_bilan`,
    `copie_abri`. Une copie introuvable : `GARDE:`, les autres s'écrivent quand même. Puis
    `COPIES <n> écrites · <n> inchangées · <n> introuvables`, l'archive (`archive`, déjà écrite)
    comprise (PRP3)."""
    n = {"écrites": int(archive), "inchangées": int(not archive), "introuvables": 0}
    page = page_du_fichier(chemin) if chemin else ""
    for copie, cible in ((copie_fait, chemin), (copie_bilan, page), (copie_abri, chemin_abri(page) if page else "")):
        try:
            if usd is None or not cible:
                raise ValueError("prix non recompté")
            n["écrites" if copie(cible, usd) else "inchangées"] += 1
        except ValueError as e:
            n["introuvables"] += 1
            sortie.write("GARDE: %s — %s ; les autres copies s'écrivent\n" % (copie.__name__, e))
    sortie.write("COPIES %d écrites · %d inchangées · %d introuvables\n" % tuple(n.values()))


def poser_prix(cellule, prix):
    """La cellule de coût close avec le prix mesuré en tête — la même cellule s'il y est déjà
    (chantier TAU, `prix`)."""
    if re.match(r'\d+,\d\d \$ · ', cellule):
        return cellule
    return "%s · %s" % (dollars(prix), cellule)


# Le vieux joué à la louche (avec `≈`) et le vieil estimé non encore marqué — `prix` (chantier TAU).
JOUE_LOUCHE = re.compile(r'joué (\d+) fiches ≈[\d,]+ \$')
# Tout joué, mesuré, à la louche ou inconnu — `recompter --clos` (PRP3).
JOUE_PRIX = re.compile(r'joué (\d+) fiches (?:≈?[\d,]+|\?) \$')
ESTIME_NON_MARQUE = re.compile(r'(estimé \S+ fiches ≈[\d,]+ \$)(?! \(taux plat\))')


def recaler_texte(texte, prix, tout=False):
    """`texte` (`**Fait.**`, page ou `.md` d'abri) avec le joué à la louche recalé sur `prix` (le
    pondéré mesuré de sa page, `dollars`) et le vieil estimé marqué `(taux plat)` s'il ne l'est
    pas déjà — (nouveau texte, un joué a été recalé, un estimé a été marqué) ; inchangé et deux
    `False` si rien à faire (chantier TAU, `prix`). `tout` : tout joué recalé, mesuré compris
    (`JOUE_PRIX`, `recompter --clos`)."""
    neuf, n1 = (JOUE_PRIX if tout else JOUE_LOUCHE).subn(
        lambda m: "joué %s fiches %s" % (m.group(1), dollars(prix)), texte)
    neuf, n2 = ESTIME_NON_MARQUE.subn(lambda m: m.group(1) + " (taux plat)", neuf)
    return neuf, bool(n1), bool(n2)


def cmd_prix(projet, sortie, a_blanc=False):
    """Pose le prix mesuré — le `$` du `cout-total` de sa page — en tête de la cellule Tokens de
    chaque ligne de `ZONE:clos` qui ne l'a pas encore (parcours de `recompter`), recale son
    ancien `joué … ≈X $` sur ce prix et marque son vieil estimé `(taux plat)`, dans le fichier de
    fiches, la page et son `.md` d'abri. Une page sans `$` : rien d'écrit, comptée « sans prix ».
    Le résumé replié et le pied « Total cumulé » de la feuille (`resommer`) sont rafraîchis sur
    l'état final des cellules, posées ou déjà là — sinon ils restent à l'ancien total, à la louche
    (dette trouvée en clôture de TAU4). Relancé, plus rien à écrire (chantier TAU)."""
    parcours = clos_du_projet(projet, sortie)
    if parcours is None:
        return 1
    from decimal import Decimal
    html, d, f, rangs = parcours
    n = {"posés": 0, "déjà": 0, "sans prix": 0, "joués recalés": 0, "estimés marqués": 0}
    neufs, ecrits = {}, []
    for r, prefixe, brut, chemin in rangs:
        page = page_du_fichier(chemin) if chemin else None
        pg = lire(page) if page and os.path.isfile(page) else None
        m = re.search(r'<p class="mono cout-total">.*?(\d+,\d\d) \$</p>', pg) if pg else None
        if not m:
            n["sans prix"] += 1
            continue
        assert page is not None    # m ne matche que si `pg` (donc `page`) n'est pas None
        prix = Decimal(m.group(1).replace(",", "."))
        cellule = CELLULE_CLOS.search(r)
        if cellule and re.match(r'\d+,\d\d \$ · ', cellule.group(2)):
            n["déjà"] += 1
        elif cellule:
            neufs[r] = CELLULE_CLOS.sub(lambda c: c.group(1) + poser_prix(c.group(2), prix) + c.group(3), r, count=1)
            n["posés"] += 1
        texte = "\n".join(lignes_de(chemin))
        neuf_texte, joue_r, estime_m = recaler_texte(texte, prix)
        n["joués recalés"] += joue_r
        n["estimés marqués"] += estime_m
        if neuf_texte != texte:
            if not a_blanc:
                with open(chemin, "w", encoding="utf-8", newline="") as fh:
                    fh.write(neuf_texte + "\n")
            ecrits.append(chemin)
        pg_neuf = recaler_texte(pg, prix)[0]
        if pg_neuf != pg:
            if not a_blanc:
                with open(page, "w", encoding="utf-8", newline="") as fh:
                    fh.write(pg_neuf)
            ecrits.append(page)
        md_page = chemin_abri(page)
        if os.path.isfile(md_page):
            md_texte = lire(md_page)
            md_neuf = recaler_texte(md_texte, prix)[0]
            if md_neuf != md_texte:
                if not a_blanc:
                    with open(md_page, "w", encoding="utf-8", newline="") as fh:
                        fh.write(md_neuf)
                ecrits.append(md_page)
    corps = html[d:f]
    neuf_corps = RANG_CLOS.sub(lambda m: neufs.get(m.group(0), m.group(0)), corps)
    neuf_html = html[:d] + neuf_corps + html[f:]
    total = total_clos(neuf_corps)
    usd, n_usd = prix_clos(neuf_corps)
    neuf_html = resommer(neuf_html, len(lignes_clos(neuf_corps)), total, usd, n_usd)
    if neuf_html != html:
        page_route = page_clos(projet)
        if not a_blanc:
            with open(page_route, "w", encoding="utf-8", newline="") as fh:
                fh.write(neuf_html)
            if page_route != page_feuille(projet):
                rafraichir_couts(projet, page_route, neuf_html)   # le résumé du bloc d'archive (ARC)
        ecrits.append(page_route)
    if not a_blanc:
        for chemin_ecrit in ecrits:
            sortie.write("ÉCRIT %s\n" % chemin_ecrit)
    sortie.write("PRIX %d posés · %d déjà · %d sans prix · %d joués recalés · %d estimés marqués%s\n" % (
        n["posés"], n["déjà"], n["sans prix"], n["joués recalés"], n["estimés marqués"],
        " · à blanc, rien d'écrit" if a_blanc else ""))
    return 0


def resume_clos(n, total, usd=None, n_usd=0):
    """Ce que le bloc repliable montre sans être déplié — le prix mesuré des `n_usd` lignes qui
    en portent un, sur `n` (chantier TAU)."""
    if not n:
        return "aucun chantier clos"
    if not total:  # aucun des clos ne porte de coût mesuré : pas de 0 $ inventé.
        return "%d chantiers clos · coût non mesuré" % n
    return "%d chantiers clos · %s tokens · %s" % (n, arrondi(total), texte_cout_clos(usd, n_usd, n) or "coût non mesuré")


def resommer(html, n, total, usd=None, n_usd=0):
    """Le pied « Total cumulé » et le résumé du bloc repliable d'une feuille, pour `n` clos qui
    coûtent `total` tokens, dont `n_usd` au prix mesuré `usd` — écrits par `clore` et
    `recompter --ecrire` (chantier TAU ; plus la louche à tant par million)."""
    cout = texte_cout_clos(usd, n_usd, n)
    html = re.sub(r"(Total cumulé</td><td class=\"mono\"><strong>).*?(</strong></td><td[^>]*>).*?(</td>)",
                  lambda m: m.group(1) + arrondi(total) + m.group(2) + cout + m.group(3),
                  html, count=1)
    return re.sub(r"(<span class=\"resume-clos\">).*?(</span>)",
                  lambda m: m.group(1) + resume_clos(n, total, usd, n_usd) + m.group(2), html, count=1)


def migrer_feuille(html):
    """Une feuille de route d'avant le 2026-09-17 n'a ni bloc repliable ni
    cellule d'estimation au pied de la table des clos : poser le `<details class="clos">`
    manquant, sans toucher à l'indentation des lignes de `ZONE:clos`. Rend le HTML — le
    même s'il l'a déjà. Aucune règle CSS à poser ici (chantier PLI) : `migrer_style`,
    dans `regenerer`/`feuille`, remplace tout `<style>` par le `<link>` vers `vlp.css`,
    qui les porte déjà."""
    i = html.find("<!-- ZONE:clos")
    if i < 0:
        return html
    fin = html.find("  </section>", i)
    debut = html.find('    <div class="tableau">', i)
    if not 0 <= debut < fin:
        return html
    corps = html[debut:fin]
    total = total_clos(corps)
    usd, n_usd = prix_clos(corps)
    n_rows = len(lignes_clos(corps))
    # Une cellule qui porte déjà des dollars est celle que `clore` entretient.
    corps = PIED_CLOS.sub(lambda m: m.group(0) if "$" in m.group(2)
                          else m.group(1) + '<td class="mono">%s</td>' % texte_cout_clos(usd, n_usd, n_rows),
                          corps, count=1)
    if '<details class="clos">' not in html[i:fin]:
        corps = ('    <details class="clos">\n      <summary><span class="resume-clos">%s</span>'
                 '</summary>\n' % resume_clos(n_rows, total, usd, n_usd)) + corps + "    </details>\n"
    return html[:debut] + corps + html[fin:]


CHEVRONS_HREF = re.compile(r'href="&lt;([^"]*)&gt;"')


def migrer_clos(html):
    """(HTML, n) : les lignes de `ZONE:clos` écrites avant `gras_et_liens` y
    passent, et un `href="&lt;URL&gt;"` redevient `href="URL"` ; n lignes changées.
    Les dix espaces restent, la ligne d'exemple du gabarit aussi. Deux passes = une. Sans
    ZONE:clos (partie dans l'archive, chantier ARC) : rien à migrer."""
    if "<!-- ZONE:clos" not in html:
        return html, 0
    d, f = zone(html, "clos", "<tbody>\n", "        </tbody>")
    n = 0

    def rang(m):
        nonlocal n
        avant = m.group(0)
        if not lignes_clos(avant):  # la ligne d'exemple du gabarit
            return avant
        apres = CHEVRONS_HREF.sub(r'href="\1"', gras_et_liens(avant))
        n += apres != avant
        return apres
    corps = RANG_CLOS.sub(rang, html[d:f])
    return html[:d] + corps + html[f:], n


# --- comparer -----------------------------------------------------------------

BLOC = {"tr", "p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "section"}


class Extracteur(html.parser.HTMLParser):
    """Le texte visible d'une page, par ligne de tableau (`tr`) ou par bloc
    (`p`, `div`, `li`, un titre, `section`) — coupé à chaque frontière de
    bloc, imbriqué ou non : une page enveloppée dans un `div` ne fait pas un
    seul bloc. `convert_charrefs` décode les entités."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hors_texte = 0
        self.pile = []
        self.tampon = []
        self.blocs = []

    def couper(self):
        texte = " ".join("".join(self.tampon).split())
        if texte:
            self.blocs.append(texte)
        self.tampon = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hors_texte += 1
        elif not self.hors_texte and tag in BLOC:
            self.couper()
            self.pile.append(tag)

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hors_texte = max(0, self.hors_texte - 1)
        elif not self.hors_texte and tag in BLOC and tag in self.pile:
            while self.pile[-1] != tag:
                self.pile.pop()
            self.pile.pop()
            self.couper()

    def handle_data(self, data):
        if not self.hors_texte and self.pile:
            self.tampon.append(data)


def textes_visibles(html_):
    """Les blocs de texte visible d'une page, dans leur ordre d'apparition."""
    ex = Extracteur()
    ex.feed(html_)
    return ex.blocs


COMMENTAIRE = re.compile(r"<!--.*?(?:-->|\Z)", re.S)
BALISE_STYLE = re.compile(r"<style\b", re.I)
LIEN_CSS = re.compile(r"<link\b[^>]*\brel\s*=\s*[\"']?stylesheet\b", re.I)


def defauts_page(html_):
    """Les défauts qui interdisent de publier une page (chantier VID) : un commentaire
    ouvert sans `-->` après lui, aucun style hors commentaire (ni `style`, ni `link`
    `rel="stylesheet"`), aucun bloc de texte visible. Liste vide : la page est saine."""
    defauts = []
    i = html_.find("<!--")
    while i >= 0:
        j = html_.find("-->", i + 4)
        if j < 0:
            defauts.append("commentaire ouvert ligne %d (<!-- sans --> après lui)" % (html_.count("\n", 0, i) + 1))
            break
        i = html_.find("<!--", j + 3)
    hors_commentaires = COMMENTAIRE.sub("", html_)
    if not BALISE_STYLE.search(hors_commentaires) and not LIEN_CSS.search(hors_commentaires):
        defauts.append('aucun style (ni balise style, ni link rel="stylesheet")')
    if not textes_visibles(html_):
        defauts.append("aucun bloc de texte visible")
    return defauts


def cmd_vigile(chemin, sortie):
    """Le repli à la main : une ligne `GARDE:` par défaut (sort 1), ou `PAGE SAINE <n> blocs`."""
    if not os.path.isfile(chemin):
        sortie.write("GARDE: introuvable %s\n" % chemin)
        return 1
    html_ = lire(chemin)
    defauts = defauts_page(html_)
    for d in defauts:
        sortie.write("GARDE: %s — %s\n" % (chemin, d))
    if defauts:
        return 1
    sortie.write("PAGE SAINE %d blocs\n" % len(textes_visibles(html_)))
    return 0


def cmd_vigile_hook(entree, sortie):
    """Le hook `PreToolUse` sur `Artifact` : une page `.html` cassée est refusée (`deny`, la
    raison nomme le fichier et chaque défaut). Muet sur tout le reste, entrée illisible,
    `.md`, `asset` vrai ou fichier illisible compris : il ne bloque jamais ce qu'il ne lit pas."""
    try:
        d = json.loads(entree.read())
    except (ValueError, AttributeError, TypeError):
        return 0
    if not isinstance(d, dict) or d.get("hook_event_name") != "PreToolUse" or d.get("tool_name") != "Artifact":
        return 0
    outil = d.get("tool_input")
    if not isinstance(outil, dict) or outil.get("asset") is True:
        return 0
    chemin = outil.get("file_path")
    if not isinstance(chemin, str) or not chemin.lower().endswith(".html"):
        return 0
    cwd = d.get("cwd")
    if not os.path.isabs(chemin) and isinstance(cwd, str):
        chemin = os.path.join(cwd, chemin)
    try:
        defauts = defauts_page(lire(chemin))
    except OSError:
        return 0
    if defauts:
        sortie.write(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "deny",
            "permissionDecisionReason": "Page cassée, publication refusée (vlp.py vigile) — %s : %s. "
                                        "Corrige la page, puis republie." % (chemin, " ; ".join(defauts))}},
            ensure_ascii=False) + "\n")
    return 0
