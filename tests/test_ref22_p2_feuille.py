"""REF22 (l'angle des bugs, passe 2) : les défauts rejoués de `noyau/feuille.py` et `noyau/ouvrir.py` — le badge
« en cours » relu dans l'ancienne page ou dans le gabarit, la liste des lettres coupée au mauvais endroit, le total
mesuré lu hors de sa cellule. Chacun son test, écrit rouge avant sa correction ; rien de la machine, `tmp_path`."""
import argparse
import io
import os
import re
import subprocess

from aides import ecrire, mod
from noyau import feuille, ouvrir

CARTE = ("# Carte\n\n- **contexte** : context AI/\n- **index** : context AI/00-INDEX.md\n"
         "- **fichier d'état** : context AI/08-etat.md\n- **artefact feuille de route** : aucun\n"
         "- **artefact du chantier** : aucun\n- **artefact enchaînement** : aucun\n\n## Chantiers clos\n\n"
         "Lettres de fiche déjà prises : ZZ (Zêta). Un nouveau chantier en choisit un autre.\n")
ENTETE_TODO = ("# État\n\n## Chantiers possibles\n\nD'où viennent les lignes.\n\n"
               "| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n")


def todo_(rangs):
    """Le fichier d'état : une ligne de TODO par `(rang, code)` de `rangs`."""
    return ENTETE_TODO + "".join("| %s | `%s` — Chantier %s | x | 1 fiche | — |\n" % (r, c, c) for r, c in rangs)


def fiches_(code, case=" "):
    """Le fichier de fiches d'un chantier `code` ouvert, deux fiches cochées de `case`."""
    return ("# Chantier %s — Chantier %s\n\n**Ouvert.** le 2026-11-01.\n\n**Fait.** Rien.\n\n"
            "## %s1 [%s] — une\n\n## %s2 [%s] — deux\n" % (code, code, code, case, code, case))


def gabarit():
    """Le texte du gabarit de la feuille de route, tel que `niveau` le pose quand la page est absente."""
    return mod.lire(os.path.join(mod.etat.KIT, "templates/artefact-feuille-de-route.html"))


def test_ref22_clore_deux_ouverts_ecrit_la_feuille(depot, monkeypatch):
    """REF22 : deux chantiers ouverts, le post-it nomme AA ; clore AA ôte sa rangée de la TODO, puis `feuille()` prend
    BB pour courant : le badge du rang 1 relu dans l'ancienne page n'est plus dans la TODO, il ne vaut plus rien — la
    feuille s'écrit, `clore` rend 0 ou des gardes seules, jamais « --todo 1 absent »."""
    monkeypatch.setattr(mod.etat, "SOURCE_ORDRE", None)
    d = str(depot)
    ecrire(os.path.join(d, "CHANTIER.md"), CARTE)
    ecrire(os.path.join(d, "context AI", "10-aa.md"), fiches_("AA", "x"))
    ecrire(os.path.join(d, "context AI", "11-bb.md"), fiches_("BB", "x"))
    ecrire(os.path.join(d, "context AI", "08-etat.md"), todo_([(1, "AA"), (2, "BB")]))
    subprocess.run([mod.etat.GIT, "add", "-A"], cwd=d, check=True, capture_output=True)
    subprocess.run([mod.etat.GIT, "commit", "-q", "-m", "init"], cwd=d, check=True, capture_output=True)
    ecrire(os.path.join(d, ".git", "vlp-chantier"), "context AI/10-aa.md\n")
    page = os.path.join(d, "context AI", "artefacts", "feuille-de-route.html")
    html, _ = feuille.feuille(d, gabarit(), "1", "2026-11-01")
    ecrire(page, html)
    s = io.StringIO()
    mod.cmd_clore(argparse.Namespace(projet=d, date="2026-11-02", abandon=None, fait=None, livre="livré",
                                     surpris=None, resume=None, tokens=None), s)
    assert "feuille non écrite" not in s.getvalue(), "REF22 : clore, deux ouverts\n" + s.getvalue()
    neuve = mod.lire(page)
    assert "Chantier AA" not in neuve[neuve.find("ZONE:encours"):][:600], "REF22 : AA reste « en cours »\n" + neuve


def projet_niveau(tmp_path, rangs):
    """Un projet équipé, chantier BB ouvert, feuille de route absente, la TODO de `rangs` ; rend son dossier."""
    d = str(tmp_path / "projet")
    ecrire(os.path.join(d, "CHANTIER.md"), CARTE)
    ecrire(os.path.join(d, "context AI", "00-INDEX.md"),
           "# Index\n\n| Fichier | Lire quand |\n|---|---|\n| `08-etat.md` | état |\n"
           "| `10-bb.md` | on joue `BB*` — chantier **ouvert** « Bêta », `BB1..BB2` |\n")
    ecrire(os.path.join(d, "context AI", "10-bb.md"), fiches_("BB"))
    ecrire(os.path.join(d, "context AI", "08-etat.md"), todo_(rangs))
    return d


def test_ref22_niveau_gabarit_sans_rang_1(tmp_path):
    """REF22 : page absente, `niveau` régénère le gabarit ; la carte d'exemple porte le rang 1 et le badge, mais le
    rang 1 n'est pas dans la TODO : aucun « ÉCART: feuille: --todo 1 absent »."""
    d = projet_niveau(tmp_path, [(2, "BB"), (3, "CC")])
    s = io.StringIO()
    mod.cmd_niveau(argparse.Namespace(projet=d, ecrire=False, date="2026-11-02"), s)
    assert "--todo 1 absent" not in s.getvalue(), "REF22 : niveau sur le gabarit\n" + s.getvalue()


def test_ref22_feuille_gabarit_ne_pose_pas_le_badge_d_exemple(tmp_path):
    """REF22 : rang 1 présent, chantier ouvert au rang 3 : le badge de la carte d'exemple du gabarit ne passe pas sur
    la carte du rang 1 de la page régénérée."""
    d = projet_niveau(tmp_path, [(1, "CC"), (3, "BB")])
    neuf, _ = feuille.feuille(d, gabarit(), None, "2026-11-02")
    badges = [m.group(1) for m in re.finditer(r'<span class="rang mono">(\d+)</span>(?:(?!</span></span>).)*?'
                                              r'data-etat="cours"', neuf)]
    assert "1" not in badges, "REF22 : badge d'exemple sur le rang 1\n" + str(badges)


LETTRES_A_LA_LIGNE = ("# Carte\n\nLettres de fiche déjà prises : A (Alpha), B (Bêta).\n"
                      "Un nouveau chantier en choisit un autre.\n")


def test_ref22_fin_lettres_phrase_a_la_ligne():
    """REF22 : « Un nouveau chantier » à la ligne suivante : `fin_lettres` s'arrête avant le point, l'ajout de
    `clore` donne `B (Bêta), C (Gamma).` ; `titre_entree` lit le titre d'une entrée suivie du point final."""
    j = LETTRES_A_LA_LIGNE.find(feuille.LETTRES)
    k = feuille.fin_lettres(LETTRES_A_LA_LIGNE, j)
    insere = LETTRES_A_LA_LIGNE[:k] + ", C (Gamma)" + LETTRES_A_LA_LIGNE[k:]
    assert "B (Bêta), C (Gamma).\nUn nouveau" in insere, "REF22 : fin_lettres\n" + repr(insere)
    assert feuille.titre_entree(" B (Bêta).") == "Bêta", "REF22 : titre_entree au point final"
    assert feuille.doublon_lettres(" : A (Alpha), B (Bêta), C (Gamma)", " : A (Alpha), B (Bêta).") is None, (
        "REF22 : doublon_lettres, faux doublon au point final")


def test_ref22_moyenne_clos_lit_la_cellule_tokens():
    """REF22 : une cellule « Ce qu'il a livré » qui finit par `(429)` ne remplace pas le total mesuré : `moyenne_clos`
    lit le nombre entre parenthèses de la cellule `mono` seule, comme `clos.total_clos`."""
    ligne = ('          <tr>\n            <td>Titre <span class="badge" data-etat="clos">clos</span></td>\n'
             '            <td class="mono">LOC1–LOC3</td><td class="mono">2026-10-01</td>\n'
             '            <td class="mono">4,88 $ · ≈13,0M (12 990 786)</td>\n'
             '            <td>la limite de publication du jour, relevée (429)</td>\n          </tr>\n')
    html = '<!-- ZONE:clos -->\n        <tbody>\n' + ligne + '        </tbody>\n'
    lu = ouvrir.moyenne_clos(html)
    assert lu[:3] == (12990786, 3, 1), "REF22 : moyenne_clos\n" + str(lu)
