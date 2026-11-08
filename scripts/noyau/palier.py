"""Le palier de tests d'un changement (ALG2, choix 5 A et C de l'utilisateur, 2026-11-08) : les chemins changés
choisissent les tests, par la table `REGLES_PALIER` — jamais au jugé. Le plus haut palier gagne ; le compte rendu
d'une fiche cite celui qui a joué, et la règle de chaque chemin.

Les tests de `boucle.py` (les plus lents de la suite : 329 s d'appels sans coverage, mesuré le 2026-11-08) ne jouent
qu'au palier `boucle` ou `coeur`.
"""
import fnmatch
import glob
import os

from noyau.commun import lire
from noyau.relecture import git_texte

__all__ = ["PALIERS", "REGISTRE", "REGLES_PALIER", "TESTS_LENTS", "TOUJOURS", "chemins_changes", "choisir", "cmd_palier",
           "commande", "regle_du_chemin"]

PALIERS = ("aucun", "doc", "script", "boucle", "coeur")   # du plus bas au plus haut

# (motif sur le chemin relatif, palier, raison) — la première qui colle gagne. `*` de fnmatch passe aussi les `/`.
REGLES_PALIER = [
    ("scripts/vlp.py", "coeur", "le lanceur : toute commande passe par lui"),
    ("scripts/vlp_coeur.py", "coeur", "la façade : elle ré-exporte tout noyau/"),
    ("scripts/noyau/commun.py", "coeur", "importé par 18 fichiers de scripts/ (mesuré le 2026-11-08)"),
    ("scripts/noyau/etat.py", "coeur", "l'état que les tests changent (REF44)"),
    ("scripts/noyau/facade.py", "coeur", "les noms que les modules lisent à l'appel (REF45)"),
    ("scripts/noyau/cli.py", "coeur", "la ligne de commande de toutes les sous-commandes"),
    ("tests/conftest.py", "coeur", "il règle toute la suite"),
    ("tests/aides*.py", "coeur", "les aides de tous les tests"),
    ("tests/faux_claude.py", "coeur", "le faux claude de la boucle et des photos"),
    ("pyproject.toml", "coeur", "les réglages de pytest, coverage et pyright"),
    ("uv.lock", "coeur", "les versions de l'atelier"),
    ("hooks/*", "coeur", "les hooks de toute séance"),
    (".githooks/*", "coeur", "les gardes de chaque commit"),
    ("scripts/boucle.py", "boucle", "la boucle de nuit : ses tests sont les plus lents"),
    ("scripts/boucle_noyau/*", "boucle", "la boucle de nuit : ses tests sont les plus lents"),
    ("tests/test_*.py", "script", "un fichier de tests changé se rejoue lui-même"),
    ("tests/*", "script", "une pièce des tests"),
    ("scripts/*", "script", "un script : ses tests par leur nom, et les photos"),
    ("*", "doc", "ni code ni test : les règles écrites, et les tests qui citent le chemin"),
]
# Le registre du kit : un test bâtit son propre `CHANTIER.md` dans un dossier temporaire, il ne lit pas celui-ci —
# chercher qui cite ces noms tirait 29 fichiers de tests pour une ligne de `CHANTIER.md` (mesuré le 2026-11-08).
REGISTRE = ("CHANTIER.md", "CLAUDE.md", "README.md", "context AI/*", "archive/*")
TOUJOURS = {"doc": ["tests/test_regles.py"],
            "script": ["tests/test_regles.py", "tests/test_photos_vlp.py", "tests/test_noms_publics.py"]}
TESTS_LENTS = ("tests/test_boucle*.py", "tests/test_photos_boucle.py", "tests/test_ref22*boucle*.py")
GENERIQUES = {"SKILL.md", "README.md", "__init__.py", "CLAUDE.md"}   # un nom trop commun pour désigner un fichier


def regle_du_chemin(chemin):
    """Rendre (palier, raison) de la première règle de `REGLES_PALIER` qui colle à `chemin` (relatif, en `/`) ; la
    dernière règle, `*`, colle à tout."""
    return next((p, r) for motif, p, r in REGLES_PALIER if fnmatch.fnmatch(chemin, motif))


def chemins_changes(racine, depuis=None):
    """Les chemins changés sous `racine` — index, arbre de travail et non suivis, contre `HEAD` ou `depuis` —,
    relatifs, triés, sans doublon ; `None` hors d'un dépôt ou si Git échoue."""
    code, diff = git_texte(["diff", "--name-only", depuis or "HEAD"], racine)
    code2, neufs = git_texte(["ls-files", "--others", "--exclude-standard"], racine)
    if code != 0 or code2 != 0:
        return None
    return sorted({c.strip() for c in (diff + "\n" + neufs).splitlines() if c.strip()})


def lent(test):
    """Vrai si `test` (chemin relatif) est un des tests lents de `TESTS_LENTS`."""
    return any(fnmatch.fnmatch(test, m) for m in TESTS_LENTS)


def nomme(test, stem):
    """Vrai si le nom du fichier de tests `test` porte le module `stem` comme un de ses morceaux (`test_page.py`,
    `test_ref22_fiches_page.py` pour `page`)."""
    nom = os.path.basename(test)[len("test_"):-len(".py")]
    return ("_%s_" % stem.replace("-", "_")) in ("_%s_" % nom)


def cite(texte, chemin):
    """Vrai si `texte` cite `chemin` : son chemin relatif, ou son nom quand il n'est pas trop commun."""
    nom = chemin.rsplit("/", 1)[-1]
    return chemin in texte or (nom not in GENERIQUES and nom in texte)


def tests_de(racine, chemin, palier, tous):
    """Les fichiers de tests (relatifs) que `chemin`, rangé au `palier`, fait jouer, parmi `tous` ; sans les lents
    sauf au palier `boucle` ; un chemin du `REGISTRE` ne fait jouer que ceux de `TOUJOURS`."""
    if palier == "script" and fnmatch.fnmatch(chemin, "tests/test_*.py"):
        return [chemin] if os.path.isfile(os.path.join(racine, chemin)) else []
    pris = list(TOUJOURS.get(palier if palier != "boucle" else "script", []))
    if any(fnmatch.fnmatch(chemin, m) for m in REGISTRE):
        return pris
    stem = os.path.splitext(chemin.rsplit("/", 1)[-1])[0]
    for t in tous:
        texte = lire(os.path.join(racine, t))
        if (palier in ("script", "boucle") and (nomme(t, stem) or "noyau.%s" % stem in texte
                                               or "noyau/%s" % stem in texte or "import %s" % stem in texte)) \
                or cite(texte, chemin):
            pris.append(t)
    if palier == "boucle":
        pris += [t for t in tous if lent(t)]
    return [t for t in pris if palier == "boucle" or not lent(t)]


def choisir(racine, chemins):
    """Rendre (palier, [(chemin, palier, raison)], fichiers de tests triés) pour `chemins` ; `coeur` : la liste vide
    vaut la suite entière ; aucun chemin : `aucun`."""
    regles = [(c,) + regle_du_chemin(c) for c in chemins]
    haut = max((p for _, p, _ in regles), key=PALIERS.index, default="aucun")
    if haut in ("aucun", "coeur"):
        return haut, regles, []
    tous = sorted(os.path.relpath(f, racine).replace(os.sep, "/")
                  for f in glob.glob(os.path.join(racine, "tests", "test_*.py")))
    fichiers = set()
    for c, p, _ in regles:
        fichiers.update(tests_de(racine, c, p, tous))
    if haut != "boucle":
        fichiers = {f for f in fichiers if not lent(f)}
    return haut, regles, sorted(f for f in fichiers if os.path.isfile(os.path.join(racine, f)))


def commande(palier, fichiers):
    """La commande pytest du palier : la suite entière à `-n 4` pour `coeur`, sinon ses fichiers, à `-n` le nombre
    de fichiers, 4 au plus ; `None` pour `aucun`."""
    if palier == "aucun":
        return None
    if palier == "coeur":
        return "uv run --frozen pytest -n 4"
    return "uv run --frozen pytest -n %d %s" % (min(4, max(1, len(fichiers))), " ".join(fichiers))


def cmd_palier(a, sortie):
    """`palier [--depuis R] [--racine D]` : `PALIER <nom> · <n> fichier(s) de tests · <chemins>`, une ligne
    `RÈGLE <chemin> : <palier> — <raison>` par chemin, puis `COMMANDE <pytest…>` ; rien de changé : `PALIER aucun`.
    Hors d'un dépôt : `GARDE:`, sort 1."""
    racine = os.path.abspath(a.racine or ".")
    chemins = chemins_changes(racine, a.depuis)
    if chemins is None:
        sortie.write("GARDE: palier — pas de dépôt Git lisible dans %s\n" % racine)
        return 1
    haut, regles, fichiers = choisir(racine, chemins)
    if haut == "aucun":
        sortie.write("PALIER aucun\n")
        return 0
    n = "suite entière" if haut == "coeur" else "%d fichier(s) de tests" % len(fichiers)
    sortie.write("PALIER %s · %s · %s\n" % (haut, n, ", ".join(chemins)))
    for c, p, r in regles:
        sortie.write("RÈGLE %s : %s — %s\n" % (c, p, r))
    sortie.write("COMMANDE %s\n" % commande(haut, fichiers))
    return 0
