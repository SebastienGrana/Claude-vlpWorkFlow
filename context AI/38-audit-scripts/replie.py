"""Fabrique des variantes repliées d'une page de Cairn, pour mesurer au navigateur
ce qu'une page « retombe » à faire quand tout est replié. Aucune variante ne
retire de texte : tout reste dans le HTML, seul l'affichage change.

Page de chantier :
  - tel-quel : la page d'aujourd'hui ;
  - D : chaque fiche repliée sur sa ligne (code, titre, état), les trois
    dernières entrées de journal visibles, les autres repliées, le bilan en haut ;
  - tout-replie : le bilan en haut, la liste des fiches et le journal repliés
    chacun en une ligne.
Feuille de route :
  - tel-quel ;
  - cartes : une carte par rang de TODO, la tête et la première phrase
    visibles, le détail replié ;
  - cartes-repliees : la tête seule, le détail replié.
Chaque variante est enveloppée comme sur claude.ai : charset, viewport, marge nulle.

    python replie.py <dossier artefacts de Cairn> <dossier de sortie>
"""
import glob, html as H, os, re, sys

src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)

ENVELOPPE = ('<!doctype html><html lang="fr"><head><meta charset="utf-8">'
             '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
             '<style>body{margin:0}[hidden]{display:none!important}</style></head><body>\n%s\n</body></html>')

CSS_PLIS = """<style>
  details > summary { cursor:pointer; }
  .fiche.pli { display:block; }
  .fiche.pli summary { display:flex; gap:.6rem; align-items:baseline; flex-wrap:wrap; }
  .fiche.pli .note, .fiche.pli .cout { display:block; margin-top:.3rem; }
  .pli-liste > summary { font-weight:600; padding:.4rem 0; }
  .carte-todo { background:var(--surface,#fff); border:1px solid var(--line,#ccc); border-radius:6px; padding:.6rem .8rem; display:flex; flex-direction:column; gap:.25rem; }
  .cartes-todo { display:flex; flex-direction:column; gap:.6rem; }
  .carte-todo .meta { font-size:.88rem; color:var(--doux,#555); }
</style>"""


def ecrire(nom, page):
    with open(os.path.join(dst, nom), "w", encoding="utf-8", newline="") as f:
        f.write(ENVELOPPE % page)


def bilan_en_haut(h):
    m = re.search(r"\n[ \t]*<!-- ZONE:bilan.*?</section>", h, re.S)
    if not m or 'class="bilan"' not in m.group(0):
        return h
    h = h[:m.start()] + h[m.end():]
    i = h.index("</header>") + len("</header>")
    return h[:i] + m.group(0) + h[i:]


def fiches_repliees(h):
    def une(m):
        li = m.group(0)
        etat = re.search(r'data-etat="(\w+)"', li)
        tete = "".join(re.findall(r'<span class="(?:id|titre|etat)">.*?</span>', li, re.S))
        reste = "".join(re.findall(r'<span class="(?:note|cout[^"]*)">.*?</span>', li, re.S))
        ouvert = " open" if etat and etat.group(1) in ("encours", "bloquee") else ""
        attr = ' data-etat="%s"' % etat.group(1) if etat else ""
        return '<li class="fiche pli"%s><details%s><summary>%s</summary>%s</details></li>' % (attr, ouvert, tete, reste)
    return re.sub(r'<li class="fiche".*?</li>', une, h, flags=re.S)


def journal_trois(h):
    m = re.search(r'(<ul class="journal">)(.*?)(\n[ \t]*</ul>)', h, re.S)
    lis = re.findall(r"<li>.*?</li>", m.group(2), re.S)
    if len(lis) <= 3:
        return h
    vieux, recents = lis[:-3], lis[-3:]
    bloc = ('<details class="pli-liste"><summary>%d entrées plus anciennes</summary><ul class="journal">%s</ul></details>'
            '<ul class="journal">%s</ul>' % (len(vieux), "".join(vieux), "".join(recents)))
    return h[:m.start()] + bloc + h[m.end():]


def liste_repliee(h, classe, titre):
    m = re.search(r'<ul class="%s">.*?\n[ \t]*</ul>' % classe, h, re.S)
    if not m:
        return h
    n = len(re.findall(r"<li[ >]", m.group(0)))
    return h[:m.start()] + '<details class="pli-liste"><summary>%s (%d)</summary>%s</details>' % (titre, n, m.group(0)) + h[m.end():]


def avec_css(h):
    return h.replace("</style>", "</style>\n" + CSS_PLIS, 1)


for n in (30, 41):
    # une page de chantier, par son numéro : son titre reste dans le dépôt de Cairn
    (chemin,) = glob.glob(os.path.join(src, "%d-*.html" % n))
    page = "page%d" % n
    h = open(chemin, encoding="utf-8").read()
    ecrire(page + "-tel-quel.html", h)
    ecrire(page + "-D.html", avec_css(journal_trois(fiches_repliees(bilan_en_haut(h)))))
    ecrire(page + "-tout-replie.html", avec_css(liste_repliee(liste_repliee(bilan_en_haut(h), "fiches", "Les fiches"), "journal", "Journal des décisions")))


def texte(s):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", "", s))).strip()


f = open(os.path.join(src, "feuille-de-route.html"), encoding="utf-8").read()
ecrire("feuille-tel-quel.html", f)
m = re.search(r"(<!-- ZONE:todo -->.*?)(<table>.*?</table>)", f, re.S)
for nom, phrase in (("feuille-cartes.html", True), ("feuille-cartes-repliees.html", False)):
    cartes = []
    for rang in re.findall(r"<tr>(.*?)</tr>", m.group(2), re.S):
        cel = re.findall(r"<td[^>]*>(.*?)</td>", rang, re.S)
        if len(cel) < 5:
            continue
        premiere = re.split(r"(?<=[.!?])\s", texte(cel[2]).replace("**", ""), maxsplit=1)[0]
        cartes.append('<div class="carte-todo"><strong>%s · %s</strong><span class="meta">%s · dépend de : %s</span>%s'
                      '<details><summary>Le détail</summary><div>%s</div></details></div>'
                      % (cel[0], cel[1], cel[3], cel[4], "<p>%s</p>" % premiere if phrase else "", cel[2]))
    g = f[:m.start()] + m.group(1) + '<div class="cartes-todo">%s</div>' % "".join(cartes) + f[m.end():]
    ecrire(nom, avec_css(g))

print("variantes écrites dans", dst, ":", len(os.listdir(dst)))
