"""REF7 : une photo par sous-commande de `vlp.py` (tests de caractérisation, D2, syrupy — REF6), pour que toute
différence de comportement crie pendant la découpe (REF18).

Chaque photo garde le code de sortie, la sortie, la sortie d'erreur, et les fichiers écrits — du projet comme du
dossier personnel du test —, filtrés par `propre`. Le projet, bâti une fois par session (`projet_vlp`), est celui
que `/vlp:init` poserait : les gabarits du kit remplis, un chantier `DEM` ouvert par `vlp.py ouvrir`, une fiche
faite et commitée, une session de trois tours. Chaque appel joue sur une copie neuve.

Une sous-commande qui ne peut pas tourner ici — un serveur qui bloque, un exécutable de la machine — est marquée
`skip` dans `SAUTEES`, avec sa raison.
"""
import datetime
import io
import os
import re
import shutil
import subprocess
import tempfile
from contextlib import redirect_stderr, redirect_stdout

import pytest

from aides import RACINE, ecrire, lire, mod, transcript

T0 = 1790000000
KIT = RACINE.replace("\\", "/")

FICHES = """# Chantier DEM — La démo

> **QUAND LIRE** : on joue une fiche `DEM*`.

## Le socle commun

Le projet de démonstration des photos : trois fiches, la première faite.

## L'ordre des fiches

<!-- FICHE:DEM1 -->
## DEM1 [x] — Écrire l'outil

**Dépend de** : rien.
**Fichiers** : `scripts/outil.py`.
**Session** : %s

**Prompt**
Écris `outil.py`.

**Critère de fin**
`py -3 scripts/outil.py` sort 0.
<!-- /FICHE -->

<!-- FICHE:DEM2 -->
## DEM2 [ ] — Le tester

**Dépend de** : `DEM1`.
**Fichiers** : `scripts/outil.py`.

**Prompt**
Teste-le.

**Critère de fin**
Le test passe.
<!-- /FICHE -->

<!-- FICHE:DEM3 -->
## DEM3 [ ] — Le montrer

**Dépend de** : `DEM2`.
**Fichiers** : `ctx/artefacts/feuille-de-route.html`.

**Prompt**
Montre-le.

**Critère de fin** (visuel)
La page le montre.
<!-- /FICHE -->
"""

CHANTIER = """# Chantier courant — Démo

> Fichier lu **en entier** par `/vlp:chantier` et `/vlp:tache`, depuis la racine du
> projet. C'est la seule table à tenir : rien à mettre à jour ailleurs quand un
> chantier s'ouvre ou se clôt. Garde-le sous le seuil de `scripts/vlp.py` : `renvois` avertit.
> Les libellés en gras se recopient **à l'identique** : ils sont lus tels quels.

- **alias** : demo
- **kit** : le plugin vlp — sans chemin de machine, ce fichier part dans Git
- **contexte** : ctx/
- **méthode** : methode-chantier.md, à la racine du kit — il voyage avec le plugin
- **chantiers possibles** : ctx/01-etat.md
- **fichier d'état** : ctx/01-etat.md
- **index** : ctx/00-INDEX.md
- **artefact feuille de route** : https://claude.ai/artifact/FEUILLE
- **artefact du chantier** : aucun
- **artefact enchaînement** : aucun
- **livraison** : aucune
- **vérification** : py -3 scripts/outil.py
- **contexte dans Git** : oui
- **commandes longues** : aucune


## Contraintes d'écriture

- Prose en français, code et commentaires de code en anglais.

## Chantiers clos — dans l'index, pas ici

Lettres de fiche déjà prises : DEM. Un nouveau chantier en choisit un autre —
trois majuscules, jamais réemployées, même après clôture.
"""

VALEURS = {"projet": "Démo", "contexte": "ctx", "NN": "10", "X": "DEM", "chantier": "dem", "date": "2026-01-05",
           "nom": "Une suite", "une ligne": "la suite de la démo", "n fiches": "3 fiches"}


def remplir(texte):
    """Remplir les `<…>` d'un gabarit markdown comme `/vlp:init` : les noms connus, `à remplir` ailleurs — les
    imbriqués d'abord."""
    avant, texte = None, texte.replace("<NN>-etat.md", "01-etat.md")
    while avant != texte:
        avant, texte = texte, re.sub(r"<([^<>]+)>", lambda m: VALEURS.get(m.group(1), "à remplir"), texte)
    return texte


def git(depot, *args, date=None):
    """Lancer git dans `depot`, à `date` (secondes après T0) pour l'auteur et le commiteur."""
    env = dict(os.environ)
    if date is not None:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = "%d +0000" % (T0 + date)
    subprocess.run(["git", *args], cwd=depot, env=env, check=True, capture_output=True)


@pytest.fixture(scope="session")
def projet_vlp(tmp_path_factory, depot_modele):
    """Le projet de démonstration, bâti une fois : gabarits remplis, chantier `DEM` ouvert, `DEM1` commitée."""
    racine = tmp_path_factory.mktemp("demo-modele")
    demo = racine / "demo"
    shutil.copytree(depot_modele, demo)
    session = racine / "s.jsonl"
    transcript(str(session), 3, [T0 + d for d in (50, 200, 400)])
    gabarits = os.path.join(RACINE, "templates")
    with pytest.MonkeyPatch.context() as mp:
        for nom in ("HOME", "USERPROFILE"):
            mp.setenv(nom, str(racine / "maison"))
        mp.setenv("GIT_CONFIG_GLOBAL", str(depot_modele.parent / "gitconfig"))
        mp.setenv("GIT_CONFIG_NOSYSTEM", "1")
        for nom in ("CLAUDE_CODE_SESSION_ID", *mod.carnet.VARIABLES_NUIT):
            mp.delenv(nom, raising=False)
        for nom, valeur in (("GIT_AUTHOR_NAME", "t"), ("GIT_AUTHOR_EMAIL", "t@t"), ("GIT_COMMITTER_NAME", "t"),
                            ("GIT_COMMITTER_EMAIL", "t@t")):
            mp.setenv(nom, valeur)
        ecrire(str(demo / "CHANTIER.md"), CHANTIER)
        ecrire(str(demo / "CLAUDE.md"), remplir(lire(os.path.join(gabarits, "CLAUDE.md"))))
        ecrire(str(demo / "ctx" / "00-INDEX.md"), remplir(lire(os.path.join(gabarits, "context AI", "00-INDEX.md"))))
        ecrire(str(demo / "ctx" / "01-etat.md"), remplir(lire(os.path.join(gabarits, "context AI", "NN-etat.md"))))
        ecrire(str(demo / "ctx" / "artefacts" / "feuille-de-route.html"),
               re.sub(r"&lt;[^&]*&gt;", "Démo", lire(os.path.join(gabarits, "artefact-feuille-de-route.html"))))
        ecrire(str(demo / "ctx" / "10-dem.md"), FICHES % session)
        ecrire(str(demo / "scripts" / "outil.py"), 'def principal():\n    """Rendre 0."""\n    return 0\n')
        ecrire(str(demo / "notes" / "etat.txt"), "- **2026-01-05** — une décision de la démo.\n")
        git(demo, "add", "-A")
        git(demo, "commit", "-q", "-m", "Départ", date=10)
        mp.chdir(demo)
        mod.main(["ouvrir", ".", "--fiches", "ctx/10-dem.md", "--titre", "La démo"], io.StringIO())
        git(demo, "add", "-A")
        git(demo, "commit", "-q", "-m", "Chantier DEM ouvert : La démo", date=100)
        ecrire(str(demo / "scripts" / "outil.py"), lire(str(demo / "scripts" / "outil.py")) + "\n\nprincipal()\n")
        git(demo, "add", "-A")
        git(demo, "commit", "-q", "-m", "DEM1 : Écrire l'outil", date=300)
    return demo


def arbre(dossier):
    """Chaque fichier sous `dossier`, hors `.git`, et ses octets."""
    fichiers = {}
    for r, ds, ns in os.walk(dossier):
        ds[:] = [d for d in ds if d != ".git"]
        for n in ns:
            with open(os.path.join(r, n), "rb") as f:
                fichiers[os.path.relpath(os.path.join(r, n), dossier).replace("\\", "/")] = f.read()
    return fichiers


def propre(texte, remplacements):
    """`texte` sans ce qui change d'un lancement ou d'une machine à l'autre : les dossiers (`remplacements`), en
    barres obliques ; la date du jour ; les sha de commit ; les durées."""
    for avant, apres in remplacements + [(tempfile.gettempdir(), "<TEMP>")]:
        for forme in (avant.replace("\\", "\\\\"), avant, avant.replace("\\", "/")):
            texte = texte.replace(forme, apres)
    texte = re.sub(r"<(P|TMP|MODELE|KIT|MAISON|TEMP)>[^\s\"'`|)]*",
                   lambda m: m.group(0).replace("\\\\", "/").replace("\\", "/"), texte)
    texte = re.sub(r"(vlp-relecture-\w+?-(?:avant|apres)-)\w+", r"\1<ALÉA>", texte)
    texte = re.sub(r"[^\s\"']*claude\.(?:EXE|exe)", "<CLAUDE>", texte)
    texte = texte.replace(datetime.date.today().isoformat(), "<AUJOURDHUI>")
    texte = re.sub(r"\b[0-9a-f]{7,40}\b", "<SHA>", texte)
    return re.sub(r"\b\d+[.,]\d+ ?s\b", "<DURÉE>", texte)


def gabarit_copie(chemin, octets):
    """`templates/<nom>` quand `octets` en est la copie à l'octet (`vlp.css`, `vlp.js`…) : la photo le dit sans
    recopier le contenu, qu'une retouche du style changerait sans que la commande change."""
    gabarit = os.path.join(RACINE, "templates", os.path.basename(chemin))
    if os.path.isfile(gabarit):
        with open(gabarit, "rb") as f:
            if f.read() == octets:
                return "templates/" + os.path.basename(chemin)
    return None


def ecrits(avant, apres):
    """Les fichiers ajoutés, changés ou retirés entre deux `arbre`, et leur texte d'après."""
    lignes = []
    for chemin in sorted(set(avant) | set(apres)):
        if chemin not in apres:
            lignes.append("== retiré %s" % chemin)
        elif avant.get(chemin) != apres[chemin] and gabarit_copie(chemin, apres[chemin]):
            lignes.append("== %s %s, copie à l'octet de %s" % ("changé" if chemin in avant else "ajouté", chemin,
                                                               gabarit_copie(chemin, apres[chemin])))
        elif avant.get(chemin) != apres[chemin]:
            corps = apres[chemin].decode("utf-8", "replace").replace("\r\n", "\n")
            lignes.append("== %s %s\n%s" % ("changé" if chemin in avant else "ajouté", chemin, corps))
    return lignes


# Une ligne par sous-commande : (nom, arguments, entrée standard). `{p}` : le projet ; `{t}` : le dossier du test ;
# `{s}` : la session de trois tours.
APPELS = [
    ("carte", ["carte"], None),
    ("extraire", ["extraire", "ctx/10-dem.md", "DEM2"], None),
    ("socle", ["socle", "ctx/10-dem.md"], None),
    ("sessions", ["sessions", "ctx/10-dem.md"], None),
    ("essai", ["essai", "demo", "--session", "s1"], None),
    ("cout", ["cout", "ctx/10-dem.md"], None),
    ("compteur", ["compteur", "ctx/10-dem.md"], None),
    ("lignes", ["lignes", "CHANTIER.md", "ctx/10-dem.md"], None),
    ("equiper", ["equiper", "."], None),
    ("valider", ["valider", "ctx/10-dem.md", "--plan"], None),
    ("page", ["page", "ctx/10-dem.md", "--creer", "--projet", "Démo", "--titre", "La démo", "--resultat", "R",
              "--note", "DEM1", "vu", "--date", "2026-01-05"], None),
    ("hook", ["hook"], "{}"),
    ("filet", ["filet"], "{}"),
    ("etat", ["etat", "ctx/01-etat.md", "--texte", "notes/etat.txt"], None),
    ("renvois", ["renvois", "."], None),
    ("niveau", ["niveau", ".", "--date", "2026-01-05"], None),
    ("comparer", ["comparer", "ctx/artefacts/feuille-de-route.html", "ctx/artefacts/feuille-de-route.html"], None),
    ("trier", ["trier", "."], None),
    ("feuille", ["feuille", ".", "--date", "2026-01-05"], None),
    ("clore", ["clore", ".", "--livre", "La démo", "--date", "2026-01-05"], None),
    ("oter", ["oter", ".", "DEM", "--raison", "essai", "--date", "2026-01-05"], None),
    ("archiver", ["archiver", "."], None),
    ("archive", ["archive", "."], None),
    ("abri", ["abri", "ctx/artefacts/feuille-de-route.html"], None),
    ("ouvrir", ["ouvrir", ".", "--fiches", "ctx/10-dem.md", "--titre", "Encore"], None),
    ("lire", ["lire", "{p}/CHANTIER.md"], None),
    ("cocher", ["cocher", "ctx/10-dem.md", "DEM2", "--date", "2026-01-05"], None),
    ("relecture", ["relecture", "DEM1"], None),
    ("contrat", ["contrat", "{s}"], None),
    ("forme", ["forme", "{s}"], None),
    ("gardien", ["gardien"], "{}"),
    ("vigile", ["vigile", "ctx/artefacts/feuille-de-route.html"], None),
    ("ouverts", ["ouverts", "."], None),
    ("postit", ["postit", ".", "ctx/10-dem.md"], None),
    ("pause", ["pause", "ctx/10-dem.md", "une raison", "--date", "2026-01-05"], None),
    ("attente", ["attente", "lister", "."], None),
    ("repeindre", ["repeindre", ".", "--a-blanc"], None),
    ("lien", ["lien", "ctx/artefacts/feuille-de-route.html", "https://claude.ai/artifact/LIEN"], None),
    ("liens", ["liens", "."], None),
    ("recompter", ["recompter", "."], None),
    ("prix", ["prix", ".", "--a-blanc"], None),
    ("lancables", ["lancables", "ctx/10-dem.md"], None),
    ("commiter", ["commiter", "ctx/10-dem.md", "DEM1"], None),
    ("bac", ["bac", "{t}/bac"], None),
    ("kit-essai", ["kit-essai", "{t}/ke", "--max-turns", "6"], None),
    ("symboles", ["symboles", "scripts/outil.py"], None),
    ("ordre", ["ordre", "--json", "--source", "{t}/absente.json"], None),
    ("rapide", ["rapide", "DEM1", "--racine", "."], None),
    ("cahier", ["cahier", "{t}/absent.md", "{t}/cahier.html"], None),
    ("joints", ["joints", "ctx/artefacts"], None),
    ("apercu", ["apercu", "."], None),
    ("nuits", ["nuits", "noter", "un texte"], None),
    ("plan", ["plan", "lire", ".", "--date", "2026-01-05"], None),
    ("fusionner", ["fusionner", ".", "inexistante"], None),
    ("matin", ["matin", ".", "2026-01-05"], None),
    ("chef", ["chef", "page", "--questions", "{t}/absentes.json", "--sortie", "{t}/q.html"], None),
    ("transcription", ["transcription", "{s}"], None),
    ("sante", ["sante", "--racine", ".", "--sans-ruff"], None),
]

SAUTEES = {
    "claude": "cherche claude.exe sur la machine : sa sortie dépend de l'installation",
    "servir": "lance un serveur HTTP qui ne rend pas la main",
    "mutant": "joue la suite entière du kit (plus de 4 min), dont le pont vers pytest : depuis une photo, il se "
              "relançait en chaîne (vu le 2026-10-18)",
}


@pytest.mark.parametrize("nom,argv,entree", APPELS, ids=[a[0] for a in APPELS])
def test_photo(nom, argv, entree, projet_vlp, tmp_path, isoler, monkeypatch, snapshot):
    """La sortie, la sortie d'erreur, le code et les fichiers écrits de `vlp.py <argv>`, égaux à leur photo."""
    projet = tmp_path / "demo"
    shutil.copytree(projet_vlp, projet)
    monkeypatch.chdir(projet)
    session = str(projet_vlp.parent / "s.jsonl")
    args = [a.format(p=projet, t=tmp_path, s=session) for a in argv]
    avant = (arbre(projet), arbre(isoler))
    sortie, erreur = io.StringIO(), io.StringIO()
    try:
        with redirect_stderr(erreur):
            code = mod.main(args, sortie, io.StringIO(entree) if entree is not None else None, erreur)
    except SystemExit as e:
        code = "SystemExit %s" % e.code
    except Exception as e:  # une photo de caractérisation garde aussi un défaut : il criera quand on le répare
        code = "EXCEPTION %s: %s" % (type(e).__name__, e)
    remplacements = [(str(projet), "<P>"), (str(isoler), "<MAISON>"), (str(tmp_path), "<TMP>"),
                     (str(projet_vlp.parent), "<MODELE>"), (RACINE, "<KIT>")]
    photo = "\n".join(["code %s" % code, "--- sortie", sortie.getvalue(), "--- erreur", erreur.getvalue(),
                       "--- écrits"] + ecrits(avant[0], arbre(projet))
                      + ["--- écrits sous le dossier personnel"] + ecrits(avant[1], arbre(isoler)))
    assert propre(photo, remplacements) == snapshot


@pytest.mark.parametrize("nom", sorted(SAUTEES))
def test_sautee(nom):
    """Les sous-commandes que ces photos ne jouent pas, chacune avec sa raison."""
    pytest.skip("%s : %s" % (nom, SAUTEES[nom]))


def test_chaque_sous_commande_a_sa_photo():
    """Les sous-commandes de `vlp.py -h`, toutes photographiées ou sautées avec raison — une sous-commande neuve
    sans photo fait échouer ce test."""
    sortie = io.StringIO()
    with pytest.raises(SystemExit), redirect_stdout(sortie), redirect_stderr(io.StringIO()):
        mod.main(["-h"], io.StringIO())
    liste = re.search(r"\{([^}]+)\}", sortie.getvalue())
    assert liste, sortie.getvalue()
    noms = set(liste.group(1).split(","))
    assert noms == {a[0] for a in APPELS} | set(SAUTEES), "photos : chaque sous-commande a sa photo"
