"""Le cahier d'essais (`vlp.py cahier`) : un `.md` d'essais, que l'utilisateur fait lui-même, bâti en une page à
cocher, remplir et copier — le gabarit `templates/cahier-essais.html`, le format du `.md` dans `ARTEFACTS.md`.

La page ne recopie aucun style : `vlp.css` y est posé tel quel, avec le bloc INSECABLE de `vlp.js`, au moment de
bâtir. Elle tient en un seul fichier, sans joint : une page ponctuelle ne se republie pas.
"""
import datetime
import html
import json
import os
import re

from noyau import etat
from noyau.commun import lire

GABARIT_CAHIER = "templates/cahier-essais.html"
INSECABLE = re.compile(r"// INSECABLE — début.*?// INSECABLE — fin", re.S)
ESSAI = re.compile(r"^## ▶️", re.M)
CASE = re.compile(r"^\s*[-*] \[[ xX]\] ", re.M)
PUCE = re.compile(r"^\s*[-*] (.*)$", re.M)
LIEN = re.compile(r"\]\(#([^)\s]+)\)")
ANCRE = re.compile(r"""<a id=["']([^"']+)["']""")
TITRE = re.compile(r"^# (.+)$", re.M)


def compter(md):
    """`(essais, cases, champs)` de `md` : ses titres `## ▶️`, ses cases `- [ ]`, et ses champs — un « … » dans une
    puce, sauf une puce faite de « … » seul, que la page retire."""
    champs = sum(p.count("…") for p in PUCE.findall(md) if p.strip() != "…")
    return len(ESSAI.findall(md)), len(CASE.findall(md)), champs


def ancres_manquantes(md):
    """Les cibles des liens `](#x)` de `md` sans `<a id="x">`, dans l'ordre, chacune une fois."""
    ancres = set(ANCRE.findall(md))
    return list(dict.fromkeys(c for c in LIEN.findall(md) if c not in ancres))


def titre_de(md):
    """Le premier titre `# ` de `md`, ce qui précède sa première lettre ou son premier chiffre ôté (l'émoji) ;
    sans titre : « Cahier d'essais »."""
    t = TITRE.search(md)
    return re.sub(r"^[^\w]+", "", t.group(1)).strip() if t else "Cahier d'essais"


def en_json(valeur):
    """`valeur` en JSON à poser dans un `<script>` : `</` échappé, qu'un `</script>` du texte ne ferme pas le bloc."""
    return json.dumps(valeur, ensure_ascii=False).replace("</", "<\\/")


def page_cahier(textes, md, choix=None):
    """La page du cahier : `textes` = `(gabarit, css, js)` ; le gabarit rempli de `css` (`vlp.css` entier), du bloc
    INSECABLE de `js` (`vlp.js`), du `.md` en JSON (`en_json`) et des réglages que lit son script — `choix` peut
    porter `titre`, `version` et `seance`, sinon leur défaut. `ValueError` : `js` sans bloc INSECABLE."""
    gabarit, css, js = textes
    choix = {k: v for k, v in (choix or {}).items() if v}
    bloc = INSECABLE.search(js)
    if not bloc:
        raise ValueError("vlp.js sans bloc INSECABLE")
    titre = choix.get("titre") or titre_de(md)
    reglages = {"titre": titre, "version": choix.get("version") or datetime.date.today().isoformat(),
                "seance": choix.get("seance") or "la séance Claude qui vous a donné ce cahier"}
    remplacements = {"__TITRE__": html.escape(titre), "/*__VLP_CSS__*/": css.strip(),
                     "/*__INSECABLE__*/": bloc.group(0), "__REGLAGES__": en_json(reglages), "__MARKDOWN__": en_json(md)}
    return re.sub("|".join(re.escape(k) for k in remplacements), lambda m: remplacements[m.group(0)], gabarit)


def cmd_cahier(a, sortie):
    """`cahier <source.md> <sortie.html> [--titre T] [--version V] [--seance S]` (docstring de `vlp.py`) : tout se lit
    et se vérifie avant d'écrire ; un `.md` sans essai, illisible, ou un gabarit cassé : `GARDE:`, rien d'écrit."""
    try:
        md = lire(a.source)
        textes = tuple(lire(os.path.join(etat.KIT, c)) for c in (GABARIT_CAHIER, "templates/vlp.css", "templates/vlp.js"))
    except OSError as e:
        sortie.write("GARDE: %s illisible : %s — rien d'écrit\n" % (getattr(e, "filename", None) or a.source, e))
        return 1
    essais, cases, champs = compter(md)
    if not essais:
        sortie.write("GARDE: %s n'a aucun essai (titre « ## ▶️ ») — rien d'écrit\n" % a.source)
        return 1
    try:
        page = page_cahier(textes, md, {"titre": a.titre, "version": a.version, "seance": a.seance})
    except ValueError as e:
        sortie.write("GARDE: %s — rien d'écrit\n" % e)
        return 1
    with open(a.sortie, "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    for cible in ancres_manquantes(md):
        sortie.write("AVERTISSEMENT: lien sans ancre : #%s\n" % cible)
    sortie.write("CAHIER %s · %d essais · %d cases · %d champs · %d octets\n"
                 % (a.sortie, essais, cases, champs, len(page.encode("utf-8"))))
    return 0
