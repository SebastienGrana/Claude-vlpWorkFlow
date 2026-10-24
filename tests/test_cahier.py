"""`noyau/cahier.py` : le cahier d'essais (`vlp.py cahier`) — un `.md` d'essais que l'utilisateur fait lui-même,
bâti en une page à cocher, remplir et copier (`templates/cahier-essais.html`, `ARTEFACTS.md`).
"""
import json
import os
import re

from aides import RACINE, appel, lire
from noyau import cahier

GABARIT = lire(os.path.join(RACINE, "templates", "cahier-essais.html"))
CSS = lire(os.path.join(RACINE, "templates", "vlp.css"))
JS = lire(os.path.join(RACINE, "templates", "vlp.js"))
EXEMPLE = os.path.join(RACINE, "exemples", "cahier-essais.md")

MD = """# 🧪 Vos essais

## 📋 Sommaire

- [ ] Relancer
- [ ] [A · Un](#essai-a) — 💬 une phrase

<a id="essai-a"></a>

## ▶️ Essai A · Un

- [ ] Ça marche.
- Durée : …
"""


def bati(md=MD, **reglages):
    """La page bâtie de `md` avec le vrai gabarit, le vrai `vlp.css` et le vrai `vlp.js`."""
    reglages.setdefault("version", "2026-01-05")
    return cahier.page_cahier((GABARIT, CSS, JS), md, reglages)


def trouve(motif, texte, drapeaux=0):
    """Le premier groupe de `motif` dans `texte` ; absent, le test échoue en le disant."""
    m = re.search(motif, texte, drapeaux)
    assert m, "introuvable : %s" % motif
    return m.group(1)


def donnees(page):
    """Le `.md` embarqué dans la page, relu depuis son bloc JSON."""
    bloc = re.search(r'<script type="application/json" id="source-md">(.*?)</script>', page, re.S)
    assert bloc, "le bloc du .md manque"
    return json.loads(bloc.group(1))


def test_le_md_voyage_intact_meme_avec_une_balise_script():
    """Le `.md` se relit à l'identique, et un `</script>` qu'il contient ne ferme pas son bloc."""
    md = MD + "\n`</script><b>`\n"
    page = bati(md)
    assert donnees(page) == md
    assert page.count("</script>") == GABARIT.count("</script>")


def test_aucun_repere_ne_reste():
    """Chaque repère `__NOM__` du gabarit est remplacé."""
    assert re.findall(r"__[A-Z_]+__", bati()) == []


def test_le_style_vient_de_vlp_css():
    """Le style de `vlp.css` est posé tel quel dans la page, et le gabarit n'écrit aucune couleur à lui : une
    couleur changée dans `vlp.css` change aussi le cahier."""
    assert CSS.strip() in bati()
    style = re.sub(r"/\*.*?\*/", "", trouve(r"<style>(.*?)</style>", GABARIT, re.S), flags=re.S)
    assert re.findall(r"#[0-9a-fA-F]{3,6}\b|rgba?\(", style) == []


def test_les_nombres_insecables_viennent_de_vlp_js():
    """Le bloc INSECABLE de `vlp.js` est recopié à l'octet : un nombre ne se coupe pas en fin de ligne."""
    bloc = trouve(r"(// INSECABLE — début.*?// INSECABLE — fin)", JS, re.S)
    assert bloc in bati()


def test_titre_tire_du_premier_titre_sans_emoji_et_echappe():
    """Sans `--titre`, le premier titre `# ` du `.md`, émoji de tête ôté ; échappé dans `<title>`."""
    page = bati()
    assert "<title>Vos essais</title>" in page
    page = bati(titre="A & <B>")
    assert "<title>A &amp; &lt;B&gt;</title>" in page


def test_reglages_lus_par_le_script():
    """Titre, version et séance passent au script en JSON, pas collés dans son code."""
    page = bati(seance="la séance « X »")
    reglages = json.loads(trouve(r"const REGLAGES = (\{.*?\});", page))
    assert reglages == {"titre": "Vos essais", "version": "2026-01-05", "seance": "la séance « X »"}


def test_compter():
    """Les essais (`## ▶️`), les cases et les champs du `.md` — un « … » dans une puce, sauf une puce faite de « … » seul,
    que la page retire (la case Remarques la remplace)."""
    assert cahier.compter(MD) == (1, 3, 1)


def test_ancres_manquantes():
    """Un lien `#x` du `.md` sans `<a id="x">` : son nom, dans l'ordre."""
    assert cahier.ancres_manquantes(MD) == []
    assert cahier.ancres_manquantes(MD + "\n[z](#zut) [y](#essai-a) [w](#ailleurs)\n") == ["zut", "ailleurs"]


def test_commande_ecrit_la_page(tmp_path):
    """`vlp.py cahier` écrit la page et dit ce qu'elle porte."""
    sortie = tmp_path / "cahier.html"
    code, texte = appel(["cahier", EXEMPLE, str(sortie), "--version", "2026-01-05"])
    assert code == 0, texte
    page = lire(str(sortie))
    assert donnees(page) == lire(EXEMPLE)
    assert re.search(r"^CAHIER .*cahier\.html · 2 essais · 7 cases · 1 champs · \d+ octets$", texte, re.M), texte


def test_commande_garde_sans_essai(tmp_path):
    """Un `.md` sans titre `## ▶️` : `GARDE:`, rien d'écrit, sort 1."""
    source, sortie = tmp_path / "s.md", tmp_path / "p.html"
    source.write_text("# Rien\n\n- [ ] une case\n", encoding="utf-8")
    code, texte = appel(["cahier", str(source), str(sortie)])
    assert code == 1 and texte.startswith("GARDE:") and "rien d'écrit" in texte, texte
    assert not sortie.exists()


def test_commande_garde_source_absente(tmp_path):
    """Une source absente : `GARDE:`, sort 1."""
    code, texte = appel(["cahier", str(tmp_path / "absent.md"), str(tmp_path / "p.html")])
    assert code == 1 and texte.startswith("GARDE:"), texte


def test_commande_avertit_d_une_ancre_manquante(tmp_path):
    """Un lien du sommaire vers une ancre absente : `AVERTISSEMENT:`, la page s'écrit quand même."""
    source, sortie = tmp_path / "s.md", tmp_path / "p.html"
    source.write_text(MD + "\n[z](#zut)\n", encoding="utf-8")
    code, texte = appel(["cahier", str(source), str(sortie), "--version", "v"])
    assert code == 0 and "AVERTISSEMENT: lien sans ancre : #zut" in texte, texte
    assert sortie.exists()
