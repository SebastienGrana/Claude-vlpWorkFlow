"""`noyau/fiches.py` : `extraire`, `socle`, `sessions`, `valider`, `cocher` et ses options (`--verifier`, `--refuser`,
`--resolu`, `--session`), le point unique des chemins (`Z2`).

Deux étages (socle de `REF`, « La découpe sépare la décision de Git ») : les décisions qui ne lancent pas `git`
(REF45), chacune sur le texte qu'un `git` aurait rendu ; puis les commandes, migrées de l'ancienne suite maison (REF50),
un seul test sur vrai dépôt par branchement. Chaque `assert` migré garde le libellé d'origine de son `verifier` en
tête de son message (REF5), puis le diagnostic.
"""
import os
import shutil
import subprocess
import tempfile

import pytest
from aides import SCRIPTS, appel, commits, ecrire, lire, mod
from noyau import fiches

ICI = SCRIPTS     # le dossier des scripts, d'où ces tests viennent
FICHES = ["# Fiches", "",
          "## W1 [ ] — Une fiche", "", "**Fichiers** : `src/a.py`, `docs/`, `src/*.txt`.", "",
          "## W2 [ ] — La suivante", "", "**Fichiers** : `src/b.py`."]


def test_tete_de_fiche_nomme_le_commit_du_sous_agent():
    for sujet in ("W1 : Une fiche", "W1: Une fiche"):
        assert fiches.tete_de_fiche("W1", "abc123 %s\n" % sujet) == "TÊTE abc123 %s\n" % sujet, \
            "cocher --verifier : un commit du sous-agent"

def test_tete_de_fiche_laisse_un_autre_commit():
    assert fiches.tete_de_fiche("W1", "abc123 W12 : une autre") is None
    assert fiches.tete_de_fiche("W1", "abc123 Fusion : W1") is None
    assert fiches.tete_de_fiche("W1", "") is None   # git log muet : rien à dire


def test_chemins_du_statut_suivis_non_suivis_et_renommes():
    texte = " M src/a.py\0?? docs/neuf.md\0R  nouveau.py\0ancien.py\0A  un nom à espace.txt\0"
    assert fiches.chemins_du_statut(texte) == ["src/a.py", "docs/neuf.md", "nouveau.py", "un nom à espace.txt"]


def test_chemins_du_statut_vide():
    assert fiches.chemins_du_statut("") == []


def test_partage_commit_ses_fichiers_et_les_communs():
    avant = ["src/a.py", "src/b.py", "docs/guide.md", "src/notes.txt", "autre.py"]
    apres = avant + ["fiches.md"]
    ajout, hors = fiches.partage_commit(FICHES, "W1", {"fiches.md"}, avant, apres)
    assert ajout == ["src/a.py", "docs/guide.md", "src/notes.txt", "fiches.md"]
    assert hors == ["src/b.py", "autre.py"]   # le fichier d'une autre fiche, et un inconnu


AVEC = """# Chantier Y

## Le socle commun

Socle, ligne 1.

## L'ordre des fiches

---

<!-- FICHE:Y1 -->
## Y1 [x] — faite
**Session** : aaa
**Prompt**
```
---
## pas un titre
```
<!-- /FICHE -->

---

<!-- FICHE:Y2 -->
## Y2 [ ] — à faire
**Session** : bbb
**Session** : aaa
<!-- /FICHE -->
"""


SANS = "## Z1 [ ] — ancien\nlong\n---\n## Z2 [ ] — dernier\nfin\n"


def test_extraire_socle(tmp_path):
    """Contrôler `extraire`, `socle` et `sessions` sur un fichier de fiches à marqueurs, et un marqueur fermant absent
    (chantier U)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        f = os.path.join(t, "y.md")
        ecrire(f, AVEC)
        code, s = appel(["extraire", f, "Y1"])
        assert code == 0
        assert s.startswith("<!-- FICHE:Y1 -->\n## Y1")
        assert "## pas un titre\n```\n<!-- /FICHE -->\n--- fiche, lignes : 9\n" in s
        assert "GARDE" not in s
        assert ("ARRÊT" not in s), ("extraire : fiche scriptable, pas d'ARRÊT") + "\n" + str(s)
        ecrire(f, AVEC.replace("**Prompt**\n", "**Critère de fin** (visuel)\n"))
        code, s = appel(["extraire", f, "Y1"])
        assert code == 0
        assert s.endswith("<!-- /FICHE -->\n" + mod.ARRET + "\n--- fiche, lignes : 9\n")
        ecrire(f, AVEC)
        code, s = appel(["extraire", f, "Y9"])
        assert code == 1
        assert "GARDE: fiche introuvable : Y9" in s
        code, s = appel(["socle", f])
        assert code == 0
        assert s == "## Le socle commun\n\nSocle, ligne 1.\n\n--- socle, lignes : 4\n"
        code, s = appel(["sessions", f])
        assert code == 0
        assert s == "aaa\nbbb\n"

        ecrire(f, AVEC.replace("<!-- /FICHE -->\n\n---\n\n<!-- FICHE:Y2", "\n---\n\n<!-- FICHE:Y2"))
        code, s = appel(["extraire", f, "Y1"])
        assert code == 0
        assert s.startswith("GARDE: marqueur fermant absent")
        assert "Y2" not in s
        assert s.endswith("```\n\n---\n\n--- fiche, lignes : 11\n")


def test_extraire_socle_sans_marqueurs(tmp_path):
    """`extraire`, `socle` et `sessions` sur un fichier sans marqueurs (repli), en CRLF, et sur un fichier absent
    (chantier U)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        f = os.path.join(t, "y.md")
        ecrire(f, SANS)
        code, s = appel(["extraire", f, "Z1"])
        assert code == 0
        assert "GARDE: pas de marqueurs" in s
        assert s.endswith("## Z1 [ ] — ancien\nlong\n---\n--- fiche, lignes : 3\n")
        code, s = appel(["extraire", f, "Z2"])
        assert (s.endswith("fin\n--- fiche, lignes : 2\n")), ("extraire : repli jusqu'à la fin") + "\n" + str(s)
        code, s = appel(["socle", f])
        assert code == 1
        assert s == "--- socle, lignes : 0\n"
        code, s = appel(["sessions", f])
        assert code == 0
        assert s == ""

        ecrire(f, AVEC.replace("\n", "\r\n"))
        code, s = appel(["socle", f])
        assert code == 0
        assert "\r" not in s
        assert s.endswith("--- socle, lignes : 4\n")
        code, s = appel(["extraire", os.path.join(t, "absent.md"), "Y1"])
        assert code == 1
        assert "GARDE: fichier introuvable" in s


def test_extraire_socle_carte(tmp_path):
    """`carte` hors d'un projet : AUCUN_PROJET, la ligne PYTHON=, et deux relais muets (U4)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        code, s = appel(["carte", os.path.join(t, "nulle-part")])
        assert code == 0
        assert s == "AUCUN_PROJET\n"
        nulle = os.path.join(t, "nulle-part")
        r1 = appel(["carte", nulle, "--python", "py -3"])
        r2 = appel(["carte", nulle, "--python", "python3", "--relais"])
        r3 = appel(["carte", nulle, "--python", "py -3", "--relais"])
        r4 = appel(["carte", os.path.join(t, "ailleurs"), "--python", "python3", "--relais"])
        assert ((r1, r2, r3, r4) == ((0, "\nPYTHON=py -3\nAUCUN_PROJET\n"), (0, ""), (0, ""), (0, "\nPYTHON=python3\nAUCUN_PROJET\n"))), ("carte --python : ligne vide, PYTHON=, deux relais muets (U4), relais seul") + "\n" + str((r1, r2, r3, r4))


SAIN = """# Chantier V

## Le socle commun

Un socle.

## L'ordre des fiches

---

<!-- FICHE:V1 -->
## V1 [ ] — scriptable
On parle de `(visuel)` entre accents graves : ce n'est pas le marqueur.
Un code en ligne `**Critère de
fin**` coupé, puis l'arrêt (`(visuel)`) : pas le marqueur.
**Critère de fin**
Une commande.
<!-- /FICHE -->

---

<!-- FICHE:V2 -->
## V2 [ ] — visuelle
**Critère de fin** (visuel)
L'utilisateur regarde.
<!-- /FICHE -->
"""


def valide(texte):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "v.md")
        ecrire(f, texte)
        code, s = appel(["valider", f])
        return code, s.replace(f, "F")


CAS_VALIDER = [
    ("fermant absent", SAIN.replace("L'utilisateur regarde.\n<!-- /FICHE -->", "L'utilisateur regarde."),
     "F:22: marqueur ouvrant sans fermant : <!-- FICHE:V2 -->"),
    ("imbriqué", SAIN.replace("Une commande.\n<!-- /FICHE -->", "Une commande."),
     "F:21: marqueur imbriqué : <!-- FICHE:V1 --> ouvert ligne 11 sans fermant"),
    ("fermant orphelin", SAIN + "<!-- /FICHE -->\n", "F:27: marqueur fermant sans ouvrant"),
    ("marqueur ≠ titre", SAIN.replace("<!-- FICHE:V2 -->", "<!-- FICHE:V9 -->"), "F:23: marqueur V9 ≠ titre V2"),
    ("titre sans marqueurs", SAIN + "\n---\n\n## V3 [ ] — nue\n**Critère de fin**\n", "F:30: titre sans marqueurs : V3"),
    ("double", SAIN.replace("## V2 [ ] — visuelle", "## V1 [ ] — visuelle").replace("FICHE:V2", "FICHE:V1"),
     "F:23: identifiant en double : V1 (déjà ligne 12)"),
    ("socle absent", SAIN.replace("## Le socle commun", "## Socle"), "F:1: section absente : ## Le socle commun"),
    ("ordre en double", SAIN + "\n## L'ordre des fiches\n", "F:28: section en double : ## L'ordre des fiches (déjà ligne 7)"),
    ("section après une fiche", SAIN.replace("## L'ordre des fiches\n", "").replace("L'utilisateur regarde.\n", "L'utilisateur regarde.\n## L'ordre des fiches\n"),
     "F:25: section après la première fiche : ## L'ordre des fiches"),
    ("sans critère", SAIN.replace("**Critère de fin**\nUne commande.", "Une commande."), "F:11: fiche V1 sans ligne **Critère de fin**"),
    ("visuel hors ligne (point 9)", SAIN.replace("**Critère de fin** (visuel)", "Voici le **Critère de fin** (visuel)"),
     "F:24: fiche V2 : (visuel) hors de la ligne"),
]


@pytest.mark.parametrize(("nom", "texte", "attendu"), CAS_VALIDER, ids=[c[0] for c in CAS_VALIDER])
def test_valider_ecart(nom, texte, attendu):
    """Chaque écart de `valider` dans son test : le libellé d'origine, « valider : » + le cas, en garde le nom."""
    code, s = valide(texte)
    assert code == 1
    assert attendu in s
    assert s.splitlines()[-1].startswith("INVALIDE")


def test_valider():
    """Contrôler `valider` : un fichier sain, les avertissements de longueur et de socle, un bilan par fichier."""
    code, s = valide(SAIN)
    assert code == 0
    assert s == "VALIDE 2 fiches · socle 4 lignes · 0 écarts · 0 avertissements — F\n"
    code, s = valide(SAIN.replace("Une commande.\n", "Une commande.\n" + "x\n" * 60))
    assert code == 0
    assert "F:11: avertissement : fiche V1 : 68 lignes, au-delà du seuil" in s
    assert "0 écarts · 1 avertissements" in s
    code, s = valide(SAIN.replace("Un socle.\n", "Un socle.\n" + "x\n" * 77))
    assert code == 0
    assert "F:3: avertissement : socle : 81 lignes, au-delà du seuil" in s
    assert "1 avertissements" in s
    code, s = valide(SAIN.replace("Un socle.\n", "Un socle.\n" + "x\n" * 76))
    assert code == 0
    assert "socle : 80 lignes" not in s
    assert "0 avertissements" in s
    code, s = appel(["valider", "absent-1.md", "absent-2.md"])
    assert code == 1
    assert s.count("INVALIDE 0 fiches") == 2


PAGE = """# Chantier P

## Le socle commun

## L'ordre des fiches

<!-- FICHE:P1 -->
## P1 [%s] — Créer `a.py`
%s**Critère de fin**
<!-- /FICHE -->
<!-- FICHE:P2 -->
## P2 [%s] — Brancher
%s**Critère de fin**
<!-- /FICHE -->
<!-- FICHE:P3 -->
## P3 [ ] — Finir
**Critère de fin**
<!-- /FICHE -->
"""


COCHE = """## L'ordre des fiches

<!-- FICHE:U1 -->
## U1 [ ] — Première
**Tentatives** (2026-01-01) — non résolu.
1. essai un
2. essai deux
Erreur : boum
**Dépend de** : rien.
**Prompt**
<!-- /FICHE -->
<!-- FICHE:U2 -->
## U2 [ ] — Seconde
**Dépend de** : `U1`.
<!-- /FICHE -->
"""


def _tester_cocher_session(f):
    # cocher --session --role (chantier NUI) : la session d'un rôle de la nuit, avec son suffixe.
    garde_env = dict(os.environ)
    ecrire(f, "# Chantier\n\n## Le socle commun\n\nSocle.\n\n<!-- FICHE:U1 -->\n## U1 [ ] — Première\n"
              "**Dépend de** : `U0`.\n<!-- /FICHE -->\n")
    try:
        os.environ["CLAUDE_CODE_SESSION_ID"] = "xyz"
        code, s = appel(["cocher", f, "U1", "--session", "abc", "--role", "relire"])
        une = lire(f)
        code2, s2 = appel(["cocher", f, "U1", "--session", "abc", "--role", "relire"])
        assert code == 0
        assert s == "NOTÉ U1 · **Session** : abc (relire)\n"
        assert "## U1 [ ]" in une
        assert une.count("**Session** : abc (relire)\n**Dépend de**") == 1
        assert (code2, s2) == (0, "DÉJÀ U1 · **Session** : abc (relire)\n")
        assert lire(f) == une
        appel(["cocher", f, "U1"])
        code, s = appel(["cocher", f, "U1", "--session", "cl1", "--role", "clore"])
        texte = lire(f)
        assert code == 0
        assert texte.index("**Session** : cl1 (clore)\n") < texte.index("## Le socle commun")
        assert mod.sessions_entete(mod.lignes_de(f)) == ["cl1"]
        assert "## U1 [x]" in texte
        assert "**Session** : abc (relire)\n**Session** : xyz\n**Dépend de**" in texte
        assert (appel(["sessions", f]) == (0, "cl1\nabc\nxyz\n")), ("cocher --session : sessions rend l'id sans suffixe, dédoublonné") + "\n" + str(appel(["sessions", f]))
        avant3 = lire(f)
        assert appel(["cocher", f, "U1", "--session", "abc"]) == (1, "GARDE: --session <uuid> --role <rôle>, sans espace ni parenthèse\n")
        assert lire(f) == avant3
    finally:
        os.environ.clear()
        os.environ.update(garde_env)


def test_cocher(tmp_path):
    """Contrôler `cocher` : la coche, les Tentatives réduites, la Session ; `page` sans chemin."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        f = os.path.join(t, "ctx", "05-u.md")
        ecrire(f, COCHE)
        garde_env = dict(os.environ)
        try:
            os.environ["CLAUDE_CODE_SESSION_ID"] = "abc"
            code, s = appel(["cocher", f, "U1", "--resolu", "lire par vlp.py", "--date", "2026-01-02"])
            assert code == 0
            assert s == "COCHÉ U1 · Session abc\n"
            assert (lire(f) == COCHE.replace("## U1 [ ]", "## U1 [x]").replace(
                         "**Tentatives** (2026-01-01) — non résolu.\n1. essai un\n2. essai deux\nErreur : boum\n",
                         "**Tentatives** (2026-01-02) — résolu par : lire par vlp.py\n**Session** : abc\n"))
            avant = lire(f)
            code, s = appel(["cocher", f, "U1"])
            assert code == 1
            assert s == "GARDE: U1 déjà cochée — rien écrit\n"
            assert lire(f) == avant
            assert (appel(["cocher", f, "U9"]) == (1, "GARDE: fiche introuvable : U9\n")), ("cocher : fiche introuvable") + "\n" + str(appel(["cocher", f, "U9"]))
            assert (appel(["cocher", f, "U1", "--verifier"]) == (0, "CASE U1 [x]\nSANS GIT\n")), ("cocher --verifier : cochée") + "\n" + str(appel(["cocher", f, "U1", "--verifier"]))
            avant2 = lire(f)
            assert appel(["cocher", f, "U2", "--verifier"]) == (1, "CASE U2 [ ]\nSANS GIT\n")
            assert lire(f) == avant2
            assert (appel(["cocher", f, "U9", "--verifier"]) == (1, "GARDE: fiche introuvable : U9\n")), ("cocher --verifier : fiche introuvable") + "\n" + str(appel(["cocher", f, "U9", "--verifier"]))
            os.environ["CLAUDE_CODE_SESSION_ID"] = ""
            code, s = appel(["cocher", f, "U2"])
            assert code == 0
            assert s == "COCHÉ U2 · Session absente\n"
            assert lire(f) == avant.replace("## U2 [ ]", "## U2 [x]")
        finally:
            os.environ.clear()
            os.environ.update(garde_env)

        _tester_cocher_session(f)

        ecrire(f, PAGE % (" ", "", " ", ""))
        page = os.path.join(t, "ctx", "artefacts", "05-u.html")
        code, s = appel(["page", f, "--creer", "--projet", "P", "--titre", "T", "--resultat", "R", "--date", "2026-01-02"])
        assert code == 0
        assert os.path.isfile(page)
        assert s.startswith("PAGE %s · 3 fiches" % page)
        code, s = appel(["page", f, "--verifier"])
        assert code == 0
        assert s.startswith("À JOUR 3 fiches")


REFUS = """<!-- FICHE:VAL1 -->
## VAL1 [x] — Valider

**Dépend de** : rien.
<!-- /FICHE -->
<!-- FICHE:VAL10 -->
## VAL10 [x] — Dixième
**Dépend de** : `VAL1`.
<!-- /FICHE -->
"""


def test_cocher_verifier_tete(depot):
    """Le branchement de `cocher --verifier` sur un vrai dépôt : un commit du sous-agent sort en `TÊTE`, sort 1. Les
    formes du sujet (`VAL1:`, `VAL1 :`, `VAL10 :`) sont jugées par `tete_de_fiche`, testée sans Git plus bas."""
    f = os.path.join(depot, "ctx", "06-v.md")
    ecrire(f, REFUS)
    commits(depot, [(0, "VAL1 : x")], 1_700_000_000)
    # Lu comme vlp.py le lit : même longueur d'abréviation.
    sha = subprocess.run(["git", "log", "-1", "--format=%h"], cwd=depot, capture_output=True,
                         encoding="utf-8", check=True).stdout.strip()
    vu = appel(["cocher", f, "VAL1", "--verifier"])
    assert (vu == (1, "CASE VAL1 [x]\nTÊTE %s VAL1 : x\n" % sha)), ("cocher --verifier : un commit du sous-agent, vu sur un vrai dépôt") + "\n" + str(vu)


def test_cocher_refuser(tmp_path):
    """Contrôler `cocher --verifier` et `cocher --refuser` (chantier REV)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        f = os.path.join(t, "ctx", "06-v.md")
        ecrire(f, REFUS)
        assert (appel(["cocher", f, "VAL1", "--verifier"]) == (0, "CASE VAL1 [x]\nSANS GIT\n")), ("cocher --verifier : sans Git") + "\n" + str(appel(["cocher", f, "VAL1", "--verifier"]))
        code, s = appel(["cocher", f, "VAL1", "--refuser", "motif un", "--date", "2026-01-03"])
        premier = lire(f)
        code2, s2 = appel(["cocher", f, "VAL1", "--refuser", "motif deux", "--date", "2026-01-04"])
        bloc = "**Tentatives** (2026-01-03) — non résolu.\n1. FAITE refusée à la relecture.\n"
        un = REFUS.replace("## VAL1 [x] — Valider\n\n", "## VAL1 [ ] — Valider\n\n" + bloc + "Erreur : motif un\n\n")
        deux = un.replace(bloc + "Erreur : motif un\n", bloc + "2. FAITE refusée à la relecture.\nErreur : motif deux\n")
        assert (code, s, code2, s2) == (0, "REFUSÉ VAL1 · refus 1\n", 0, "REFUSÉ VAL1 · refus 2\n")
        assert premier == un
        assert lire(f) == deux
        assert lire(f).count("**Tentatives**") == 1
        assert lire(f).count("Erreur :") == 1
        assert appel(["cocher", f, "VAL9", "--refuser", "m"]) == (1, "GARDE: fiche introuvable : VAL9\n")

    # refus dans un bloc déjà existant mais dont l'unique tentative n'est PAS un refus de
    # relecture (une piste écrite à la main, ou une BLOQUÉE) : le rang repart à 1, pas à 2 —
    # distingue de « <n> = toutes les lignes numérotées ».
    REFUS_PISTE = """<!-- FICHE:VAL2 -->
## VAL2 [x] — Deuxième

**Tentatives** (2026-01-05) — non résolu.
1. <une piste>
Erreur : blocage initial
**Dépend de** : rien.
<!-- /FICHE -->
"""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        f2 = os.path.join(t, "ctx", "07-v2.md")
        ecrire(f2, REFUS_PISTE)
        code3, s3 = appel(["cocher", f2, "VAL2", "--refuser", "motif trois", "--date", "2026-01-06"])
        attendu2 = REFUS_PISTE.replace("## VAL2 [x]", "## VAL2 [ ]").replace(
            "1. <une piste>\nErreur : blocage initial\n",
            "1. <une piste>\n2. FAITE refusée à la relecture.\nErreur : motif trois\n")
        assert (code3, s3) == (0, "REFUSÉ VAL2 · refus 1\n")
        assert lire(f2) == attendu2


def test_cocher_cycle(tmp_path):
    """Contrôler que le rang d'un refus et son motif survivent à `cocher --resolu` (ENA7), par `cocher` comme le chef."""
    cycle = """<!-- FICHE:VAL3 -->
## VAL3 [x] — Troisième

**Dépend de** : rien.
<!-- /FICHE -->
"""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        f = os.path.join(t, "ctx", "08-v3.md")
        ecrire(f, cycle)
        garde_env, vus, textes = dict(os.environ), [], []
        try:
            os.environ["CLAUDE_CODE_SESSION_ID"] = ""   # pas de ligne Session : seul le bloc change
            for k, motif in enumerate(("motif un", "motif deux", "motif trois")):
                vus.append(appel(["cocher", f, "VAL3", "--refuser", motif, "--date", "2026-01-1%d" % (2 * k)]))
                textes.append(lire(f))
                appel(["cocher", f, "VAL3", "--resolu", "repris %d" % (k + 1), "--date", "2026-01-1%d" % (2 * k + 1)])
                textes.append(lire(f))
        finally:
            os.environ.clear()
            os.environ.update(garde_env)
    deux = cycle.replace("## VAL3 [x] — Troisième\n\n", "## VAL3 [ ] — Troisième\n\n**Tentatives** (2026-01-12) — non résolu."
                         "\nRefus soldés : 1 · dernier : motif un\n2. FAITE refusée à la relecture.\nErreur : motif deux\n\n")
    assert (vus == [(0, "REFUSÉ VAL3 · refus 1\n"), (0, "REFUSÉ VAL3 · refus 2 · dernier : motif un\n"),
                     (0, "REFUSÉ VAL3 · refus 3 · dernier : motif deux\n")]), ("cocher --refuser après --resolu (ENA7) : refus 1, 2, 3, le motif d'avant sur la sortie") + "\n" + str(vus)
    assert "**Tentatives** (2026-01-11) — résolu par : repris 1\nRefus soldés : 1 · dernier : motif un\n\n" in textes[1]
    assert ("**Tentatives** (2026-01-15) — résolu par : repris 3\nRefus soldés : 3 · dernier : motif trois\n\n"
             in textes[5])
    assert textes[2] == deux
    assert textes[4].count("**Tentatives**") == 1
    assert ("— non résolu.\nRefus soldés : 2 · dernier : motif deux\n3. FAITE refusée à la relecture.\nErreur : motif trois\n"
             in textes[4])


def test_cocher_texte_libre(tmp_path):
    """Contrôler qu'un motif ou un texte de `--resolu` qui imite la tête ou ses comptes ne trompe pas `cocher` (ENA7)."""
    gabarit = "<!-- FICHE:VAL3 -->\n## VAL3 [%s] — Troisième\n\n%s**Dépend de** : rien.\n<!-- /FICHE -->\n"
    piste = "**Tentatives** (2026-01-01) — non résolu.\n1. essai un\nErreur : boum\n\n"
    bloque = "**Tentatives** (2026-01-01) — non résolu.\n1. FAITE refusée à la relecture.\n2. piste X\nErreur : blocage X\n\n"
    cas = {  # nom : (case, bloc de départ, étapes, sortie du dernier refus, extrait du fichier final)
        "un motif « non résolu »": ("x", "", [("--refuser", "la tête reste non résolu"), ("--resolu", "r1"), ("--refuser", "m2")],
                                    "REFUSÉ VAL3 · refus 2 · dernier : la tête reste non résolu\n",
                                    "(2026-02-03) — non résolu.\nRefus soldés : 1 · dernier : la tête reste non résolu\n2. FAITE"),
        "un --resolu « non résolu »": ("x", "", [("--refuser", "m1"), ("--resolu", "non résolu hier"), ("--refuser", "m2")],
                                       "REFUSÉ VAL3 · refus 2 · dernier : m1\n",
                                       "(2026-02-03) — non résolu.\nRefus soldés : 1 · dernier : m1\n2. FAITE"),
        "un --resolu « · refus 2 »": (" ", piste, [("--resolu", "cocher rend REFUSÉ X · refus 2"), ("--refuser", "m1")],
                                      "REFUSÉ VAL3 · refus 1\n",
                                      "(2026-02-02) — non résolu.\n1. FAITE refusée à la relecture.\nErreur : m1\n"),
        "un motif « · refus 9 · dernier : »": ("x", "", [("--refuser", "m1 · refus 9 · dernier : leurre"), ("--resolu", "r1"),
                                                         ("--refuser", "m2")],
                                               "REFUSÉ VAL3 · refus 2 · dernier : m1 · refus 9 · dernier : leurre\n",
                                               "\nRefus soldés : 1 · dernier : m1 · refus 9 · dernier : leurre\n2. FAITE"),
        "un blocage après un refus": (" ", bloque, [("--resolu", "r1"), ("--refuser", "m2")], "REFUSÉ VAL3 · refus 2\n",
                                      "(2026-02-02) — non résolu.\nRefus soldés : 1\n2. FAITE"),
    }
    vus = {}
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        garde_env = dict(os.environ)
        try:
            os.environ["CLAUDE_CODE_SESSION_ID"] = ""   # pas de ligne Session : seul le bloc change
            for k, (nom, (case, bloc, etapes, _, _)) in enumerate(cas.items()):
                f = os.path.join(t, "ctx", "08-v%d.md" % k)
                ecrire(f, gabarit % (case, bloc))
                sorties = [appel(["cocher", f, "VAL3", o, v, "--date", "2026-02-0%d" % (j + 1)])
                           for j, (o, v) in enumerate(etapes)]
                vus[nom] = (sorties[-1], lire(f))
        finally:
            os.environ.clear()
            os.environ.update(garde_env)
    for nom, (_, _, _, sortie, extrait) in cas.items():
        assert vus[nom][0] == (0, sortie)
        assert extrait in vus[nom][1]
        assert vus[nom][1].count("**Tentatives**") == 1


GABARIT_FEUILLE = os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html")


ETAT_Z = ("# État\n\n## TODO\n\n| n° | Chantier | Apport | Coût | Décidé |\n|---|---|---|---|---|\n"
          "| 1 | un truc | utile | bas | 2026-01-02 |\n")


CARTE_Z = ("# Chantier courant\n\n- **alias** : z\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
           "- **fichier d'état** : ctx/08-etat.md\n- **artefact du chantier** : aucun\n")


def test_z2_chemin(tmp_path):
    """Contrôler qu'un chemin de CHANTIER.md ne fait plus tomber une commande (Z2)."""
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        proj = os.path.join(t, "proj")
        ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_Z)
        ecrire(os.path.join(proj, "ctx", "08-etat.md"), ETAT_Z)
        os.makedirs(os.path.join(proj, "ctx", "artefacts"))
        shutil.copy(GABARIT_FEUILLE, os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html"))
        manque = "GARDE: fichier de fiches introuvable : ctx/absent.md\n"

        # Un fichier courant absent ne se nomme plus : seule la marque ouvre, sur un fichier qui existe (NUI31).
        code, s = appel(["ouvrir", proj, "--fiches", "ctx/absent.md", "--titre", "T"])
        assert code == 1
        assert s == manque

        absent = os.path.join(proj, "ctx", "absent.md")
        for sous in (["extraire", absent, "Z1"], ["socle", absent], ["cocher", absent, "Z1"],
                     ["cout", absent], ["page", absent]):
            code, s = appel(sous)
            assert code == 1
            assert s == "GARDE: fichier introuvable : %s\n" % absent

        try:
            mod.lignes_du_projet(proj, "ctx/absent.md", "fichier de fiches")
            assert (False), ("Z2 point unique : lève Absent") + "\nrien levé"
        except mod.Absent as e:
            assert isinstance(e, ValueError)
            assert str(e) == "fichier de fiches introuvable : ctx/absent.md"
