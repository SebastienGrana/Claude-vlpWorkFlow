"""NUI15 : `vlp.py matin <projet> <date>` fusionne dans main les branches de la nuit et répare ce que Git perd
sans conflit (methode-chantier.md:263-268) — migré de `tester_matin` (l'ancienne suite maison, REF43). Un dépôt
temporaire par cas ; `conftest.py` isole la config Git et l'environnement. Chaque `assert` garde le libellé
d'origine de son `verifier` en tête de son message (REF5), puis le diagnostic.
"""
import json
import os
import re
import shutil
import subprocess
from decimal import Decimal

import pytest
from aides import (
    CARTE_MATIN,
    ETAT_MATIN,
    JOUR_MATIN,
    OUVERT,
    RACINE,
    SCRIPTS,
    appel,
    ecrire,
    ligne_close,
    lire,
    mod,
    transcript,
)

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git absent : matin n'est pas testé")
GABARIT_FEUILLE = os.path.join(RACINE, "templates", "artefact-feuille-de-route.html")

ICI = SCRIPTS     # le dossier des scripts, d'où ce test vient
HOOK_REFUSE = "#!/bin/sh\necho 'hook : refusé' >&2\nexit 1\n"
ORDRE_ABSENT = "ORDRE pointes — carnet absent\n"
ETAT = "ctx/08-etat.md"
ETAT_NUI16 = ("# État\n\n## TODO\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
              "| 58 | `OLD` — ancien | o | 1 fiche | — |\n| 79 | `LOC` — publier | a | 2 fiches | — |\n"
              "| 80 | `PAR` — deux chantiers | b | 3 fiches | — |\n| 82 | `ENQ` — écritures | c | 2 fiches | — |\n\n"
              "## Journal des décisions\n\n## 2026-09-30 — base\nune ligne de base\n")
RANGEE_82 = "| 82 | `ENQ` — écritures | c | 2 fiches | — |\n"
CLAUDE_NUI16 = ("# Projet\n\n## Où on en est — en cinq lignes\n\n- Prouvé : le kit tient.\n"
                + "".join("- Clos le 2026-09-2%d : fait %s (chantier CC%s).\n" % (n, c, c)
                        for n, c in enumerate("ABCDEFGH"[:mod.CLOS_GARDES]))
                + "\n## Règles\n\n1. une règle.\n")
INDEX_NUI16 = ("# Index\n\n## Stable\n\n| Fichier | Lire quand |\n|---|---|\n| `08-etat.md` | l'état |\n"
               "| `00-INDEX-archive.md` | on relit un chantier clos |\n\n## Chantiers\n\n| Fichier | Lire quand |\n|---|---|\n"
               "| `40-loc.md` | on joue LOC — chantier **ouvert** |\n| `41-aaa.md` | on joue AAA — chantier **ouvert** |\n"
               "| `42-bbb.md` | on joue BBB — chantier **ouvert** |\n")
ARCHIVE_NUI16 = ("# Archive\n\n| Fichier | Lire quand |\n|---|---|\n| `50-z.md` | chantier **clos** Z |\n"
                 "| `10-x.md` | chantier **clos** X |\n")
ATTENTE = "ctx/artefacts/en-attente"
PUBLIE_MATIN = "ctx/artefacts/publie"

def ouvert(texte):
    """`texte` d'un fichier de fiches, la marque d'ouverture sous son titre `# Chantier `, comme la pose `vlp.py
    ouvrir` : `courant_de` le lit (NUI31)."""
    return re.sub(r"^(# Chantier [^\n]*\n)", r"\g<1>\n%s\n" % OUVERT, texte, count=1, flags=re.M)


def git_matin(d, *args):
    r = subprocess.run(["git"] + list(args), cwd=d, capture_output=True, encoding="utf-8", errors="replace", check=False)
    if r.returncode:
        raise RuntimeError("git %s : %s" % (" ".join(args), r.stderr))
    return r.stdout


def code_git(d, *args):
    return subprocess.run(["git"] + list(args), cwd=d, capture_output=True, check=False).returncode


def commit_matin(d, message, heure):
    """Un commit à `heure` (0 à 23) du jour de la nuit : la date de l'auteur et du commiteur est fixée."""
    os.environ["GIT_AUTHOR_DATE"] = os.environ["GIT_COMMITTER_DATE"] = "%sT%02d:00:00+00:00" % (JOUR_MATIN, heure)
    git_matin(d, "add", "-A")
    git_matin(d, "commit", "-q", "-m", message)


class Fabrique:
    """Les dépôts d'essai de `matin`, tous tirés du dépôt modèle de `conftest.py` — aucun `git init` ici (REF50).
    `nu(d)` : une copie du dépôt vide ; `depot(d, …)` : une copie du dépôt de départ de `matin`, bâti une fois par
    réglage et par session (REF19)."""

    def __init__(self, vide, dossier):
        self.vide, self.dossier, self.modeles = vide, dossier, {}

    def nu(self, d):
        shutil.copytree(self.vide, d)

    def depot(self, d, archive=True, etat=ETAT_MATIN):
        """Le dépôt de 2cef70f : `main` à courant LOC et son artefact, des lettres jusqu'à ENQ, une archive de deux
        clos (`archive` faux : ils restent sur la feuille), la feuille au rang 79 — un seul commit, à l'heure 0. Bâti
        une fois par réglage, puis copié (`shutil.copytree`) : le commit, à date fixe, est le même octet pour octet."""
        if (archive, etat) not in self.modeles:
            self.modeles[archive, etat] = os.path.join(self.dossier, "modele-%d" % len(self.modeles))
            batir_depot_matin(self, self.modeles[archive, etat], archive, etat)
        shutil.copytree(self.modeles[archive, etat], d)


@pytest.fixture(scope="session")
def fab(tmp_path_factory, depot_modele):
    """La fabrique de la session : ses dépôts de départ vivent dans un dossier de pytest, effacé par lui."""
    return Fabrique(str(depot_modele), str(tmp_path_factory.mktemp("matin")))


def batir_depot_matin(fab, d, archive, etat):
    """Bâtir dans `d` le dépôt que `Fabrique.depot` copie."""
    fab.nu(d)
    ecrire(os.path.join(d, "CHANTIER.md"), CARTE_MATIN)
    ecrire(os.path.join(d, "ctx", "08-etat.md"), etat)
    ecrire(os.path.join(d, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n")
    ecrire(os.path.join(d, "ctx", "40-loc.md"), ouvert("# Chantier LOC — Publier\n\n## LOC1 [ ] — a\n"))
    ecrire(os.path.join(d, "scripts", "x.py"), "a = 1\nb = 2\nc = 3\n")
    gabarit = lire(GABARIT_FEUILLE)
    debut, fin = mod.zone(gabarit, "clos", "<tbody>\n", "        </tbody>")
    deux = (ligne_close("12,34 $ · " + mod.arrondi(50000)).replace("Q1–Q2", "X1")
            + ligne_close(mod.arrondi(20000)).replace("Q1–Q2", "Y1"))
    ecrire(os.path.join(d, "ctx", "artefacts", "feuille-de-route.html"),
           mod.resommer(gabarit[:debut] + deux + gabarit[fin:], 2, 70000))
    if archive:
        appel(["archive", d, "--url", "https://claude.ai/artifact/ARCH"])
    appel(["feuille", d, "--todo", "79", "--date", "2026-09-30"])
    commit_matin(d, "base", 0)


def branche_matin(d, canal, code, lettre, heure, clos=True, x=None, ligne=None, retire=None, modifs=None):
    """`nuit/<jour>-<canal>-<code>`, un commit à `heure` depuis `main` : `clos`, le chantier est clos (l'artefact à
    `aucun`), sinon ouvert sur la branche, `ctx/41-<code>.md` à sa marque — l'hérité de main ne compte pas (NUI31) et la feuille refaite sans badge ; `lettre`, sa lettre ajoutée à la liste ; `x`, le nouveau
    `scripts/x.py` ; `ligne`, la plage d'une ligne close de plus à l'archive ; `retire`, le rang ôté de la TODO ;
    `modifs(d)`, d'autres retouches, avant la feuille."""
    nom = "nuit/%s-%s-%s" % (JOUR_MATIN, canal, code)
    git_matin(d, "switch", "-q", "-c", nom, "main")
    chemin = os.path.join(d, "CHANTIER.md")
    carte_ = lire(chemin)
    if clos:
        carte_ = re.sub(r"(\*\*artefact du chantier\*\* : ).*", r"\g<1>aucun", carte_)
    else:
        ecrire(os.path.join(d, "ctx", "41-%s.md" % code.lower()), ouvert("# Chantier %s — c\n\n## %s1 [ ] — a\n"
                                                                          % (code, code)))
    if lettre:
        carte_ = carte_.replace(". Un nouveau chantier", ", %s (Chantier %s). Un nouveau chantier" % (lettre, code))
    ecrire(chemin, carte_)
    if retire:
        etat = os.path.join(d, "ctx", "08-etat.md")
        ecrire(etat, "".join(l for l in lire(etat).splitlines(True) if not l.startswith("| %s |" % retire)))
    if ligne:
        archive = os.path.join(d, "ctx", "artefacts", mod.ARCHIVE_CLOS)
        html = lire(archive)
        debut, _ = mod.zone(html, "clos", "<tbody>\n", "        </tbody>")
        ecrire(archive, html[:debut] + ligne_close(mod.arrondi(1000)).replace("Q1–Q2", ligne) + html[debut:])
    if x:
        ecrire(os.path.join(d, "scripts", "x.py"), x)
    if modifs:
        modifs(d)
    appel(["feuille", d, "--date", JOUR_MATIN])
    commit_matin(d, ("%s1 : %s" % (code, code)) if clos else "WIP %s" % code, heure)
    git_matin(d, "switch", "-q", "main")
    return nom


def etat_matin(d):
    """Ce que `matin` a laissé dans `d` : (lignes de CHANTIER.md, feuille, rang « en cours », zone d'archive)."""
    carte_ = mod.lignes_de(os.path.join(d, "CHANTIER.md"))
    html = lire(os.path.join(d, "ctx", "artefacts", "feuille-de-route.html"))
    debut, fin, forme = mod.zone_todo(html)
    return (carte_, html, mod.rang_en_cours(html[debut:fin], forme),
            html[html.index("<!-- ZONE:archive"):html.index("<!-- /ZONE:archive")])


def matin_a(tr, fab):
    """(a) 2cef70f rejoué, avec un `origin` nu (f) : la clôture de PAR rend à main son chantier ouvert, son rang, ses lettres."""
    d, origine = os.path.join(tr, "a"), os.path.join(tr, "origine.git")
    fab.depot(d)
    git_matin(tr, "init", "-q", "--bare", "-b", "main", origine)
    git_matin(d, "remote", "add", "origin", origine)
    git_matin(d, "push", "-q", "origin", "main")
    pousse = git_matin(origine, "rev-parse", "main").strip()
    nom = branche_matin(d, "A", "PAR", "PAR", 1, ligne="PAR1–PAR3", retire="80")
    code, s = appel(["matin", d, JOUR_MATIN])
    carte_, html, rang, archive = etat_matin(d)
    lettres = mod.lettres_prises(carte_)
    parents = git_matin(d, "rev-list", "--parents", "-n", "1", "HEAD").split()
    assert code == 0
    assert s == ORDRE_ABSENT + "FUSIONNÉE %s\nMATIN 1 fusionnée(s) · 0 de côté\n" % nom
    assert mod.courant_de(d) == "ctx/40-loc.md"
    assert mod.champ(carte_, "artefact du chantier") == "https://claude.ai/artifact/LOC"
    assert lettres == ["E", "ENQ", "PAR"]
    assert rang == "79"
    assert "3 chantiers clos" in archive
    assert "<<<<<<<" not in "\n".join(carte_) + html
    assert "Aucun chantier ouvert" not in html
    assert len(parents) == 3
    assert not git_matin(d, "status", "--porcelain")
    assert git_matin(d, "log", "-1", "--format=%s").strip() == "Matin %s : %s" % (JOUR_MATIN, nom)
    assert "| 80 |" not in lire(os.path.join(d, "ctx", "08-etat.md"))
    assert (git_matin(origine, "rev-parse", "main").strip() == pousse != git_matin(d, "rev-parse", "main").strip()), ("NUI15 (f) un dépôt nu en origin : sa main n'a pas bougé, matin ne pousse rien") + "\n" + str((pousse, git_matin(d, "rev-parse", "main")))


def matin_b(tr, fab):
    """(b) A et B ajoutent chacun une lettre sur la même ligne, la feuille change des deux côtés : les deux lettres
    restent ; le carnet met B avant A, bien que la pointe de B soit la plus récente."""
    d = os.path.join(tr, "b")
    fab.depot(d)
    a, b = branche_matin(d, "A", "AAA", "AAA", 1), branche_matin(d, "B", "BBB", "BBB", 2)
    carnet_ = mod.carnet.du_jour(d, JOUR_MATIN)
    os.makedirs(os.path.dirname(carnet_), exist_ok=True)
    for canal, code in (("B", "BBB"), ("A", "AAA")):
        mod.carnet.ecrire(carnet_, mod.carnet.ligne({"nuit": JOUR_MATIN, "canal": canal, "chantier": code, "role": "fiche"}))
    code, s = appel(["matin", d, JOUR_MATIN])
    carte_, html, rang, _ = etat_matin(d)
    sujets = git_matin(d, "log", "--first-parent", "--format=%s", "main").splitlines()
    assert code == 0
    assert "ORDRE" not in s
    assert s.endswith("MATIN 2 fusionnée(s) · 0 de côté\n")
    assert mod.lettres_prises(carte_) == ["E", "ENQ", "BBB", "AAA"]
    assert rang == "79"
    assert 'Lettres de fiche prises : <span class="mono">E, ENQ, BBB, AAA, LOC</span>' in html
    assert ([x for x in reversed(sujets) if x.startswith("Matin")]
                 == ["Matin %s : %s" % (JOUR_MATIN, b), "Matin %s : %s" % (JOUR_MATIN, a)])


def matin_c(tr, fab):
    """(c) sans carnet : l'heure de la pointe ; une pointe à chantier ouvert (commit WIP) reste de côté."""
    d = os.path.join(tr, "c")
    fab.depot(d)
    wip = branche_matin(d, "A", "WIP", None, 1, clos=False, x="a = 1\nb = 2\nc = 30\n")
    ok = branche_matin(d, "B", "OKK", "OKK", 2)
    code, s = appel(["matin", d, JOUR_MATIN])
    assert code == 0
    assert (s == (ORDRE_ABSENT + "DE CÔTÉ %s — ctx/41-wip.md\nFUSIONNÉE %s\n"
                                     "MATIN 1 fusionnée(s) · 1 de côté\n" % (wip, ok)))
    assert code_git(d, "merge-base", "--is-ancestor", wip, "main") == 1


def matin_d(tr, fab):
    """(d) un `.py` changé des deux côtés : ARRÊT qui le nomme, fusion en cours, la suivante intacte ; résolu, relancé."""
    d = os.path.join(tr, "d")
    fab.depot(d)
    a = branche_matin(d, "A", "AAA", "AAA", 1, x="a = 1\nb = 20\nc = 3\n")
    b = branche_matin(d, "B", "BBB", "BBB", 2)
    ecrire(os.path.join(d, "scripts", "x.py"), "a = 1\nb = 22\nc = 3\n")
    commit_matin(d, "main avance", 3)
    code, s = appel(["matin", d, JOUR_MATIN])
    carte_ = lire(os.path.join(d, "CHANTIER.md"))
    assert code == 1
    assert s.startswith(ORDRE_ABSENT + "ARRÊT %s — conflit : scripts/x.py — après résolution : " % a)
    assert s.endswith(' feuille "%s"\n' % d)
    assert code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD") == 0
    assert code_git(d, "merge-base", "--is-ancestor", b, "main") == 1
    assert "- **artefact du chantier** : https://claude.ai/artifact/LOC" in carte_
    assert "<<<<<<<" not in carte_
    ecrire(os.path.join(d, "scripts", "x.py"), "a = 1\nb = 22\nc = 3\n")
    appel(["feuille", d, "--todo", "79", "--date", JOUR_MATIN])
    commit_matin(d, "résolu", 4)
    code, s = appel(["matin", d, JOUR_MATIN])
    assert code == 0
    assert s == ORDRE_ABSENT + "DÉJÀ %s\nFUSIONNÉE %s\nMATIN 1 fusionnée(s) · 0 de côté\n" % (a, b)


def matin_e(tr, fab):
    """(e) un hook qui refuse (`core.hooksPath`) : ARRÊT, la fusion reste en cours."""
    d, hooks = os.path.join(tr, "e"), os.path.join(tr, "hooks-e")
    fab.depot(d)
    nom = branche_matin(d, "A", "AAA", "AAA", 1)
    for h in ("pre-commit", "pre-merge-commit"):
        ecrire(os.path.join(hooks, h), HOOK_REFUSE)
        os.chmod(os.path.join(hooks, h), 0o755)
    git_matin(d, "config", "core.hooksPath", hooks.replace("\\", "/"))
    code, s = appel(["matin", d, JOUR_MATIN])
    assert code == 1
    assert s == ORDRE_ABSENT + "ARRÊT %s — commit refusé : hook : refusé\n" % nom
    assert code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD") == 0


def matin_h(tr, fab):
    """(h) sans archive, les clos vivent sur la feuille : une feuille en conflit ne se reprend pas de main, ARRÊT."""
    d = os.path.join(tr, "h")
    fab.depot(d, archive=False)
    a, b = branche_matin(d, "A", "AAA", "AAA", 1), branche_matin(d, "B", "BBB", "BBB", 2)
    code, s = appel(["matin", d, JOUR_MATIN])
    assert code == 1
    assert (s.startswith(ORDRE_ABSENT + "FUSIONNÉE %s\nARRÊT %s — conflit : ctx/artefacts/feuille-de-route.html"
                                            " — après résolution : " % (a, b)))
    assert s.endswith(' feuille "%s"\n' % d)
    assert code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD") == 0


def matin_g(tr, fab):
    """(g) les gardes : date, aucune branche, HEAD hors main, pas la racine, arbre sale, non équipé, CHANTIER.md sans
    libellés — chaque fois rien fusionné."""
    d, mini, vide = os.path.join(tr, "g"), os.path.join(tr, "mini"), os.path.join(tr, "vide")
    fab.depot(d)
    nom = branche_matin(d, "A", "AAA", "AAA", 1)
    os.makedirs(vide)
    fab.nu(mini)
    ecrire(os.path.join(mini, "CHANTIER.md"), "# C\n\n- **alias** : m\n")
    commit_matin(mini, "mini", 5)
    sorties = [appel(["matin", vide, JOUR_MATIN]), appel(["matin", d, "hier"]), appel(["matin", d, "2026-01-01"]),
               appel(["matin", mini, JOUR_MATIN])]
    git_matin(d, "switch", "-q", "-c", "autre")
    sorties.append(appel(["matin", d, JOUR_MATIN]))
    git_matin(d, "switch", "-q", "main")
    ecrire(os.path.join(d, "sous", "CHANTIER.md"), "# C\n")
    sorties.append(appel(["matin", os.path.join(d, "sous"), JOUR_MATIN]))
    shutil.rmtree(os.path.join(d, "sous"))
    ecrire(os.path.join(d, "scripts", "x.py"), "sale\n")
    sorties.append(appel(["matin", d, JOUR_MATIN]))
    attendu = ("GARDE: pas de CHANTIER.md dans", "GARDE: AAAA-MM-JJ attendu : hier", "GARDE: aucune branche nuit/2026-01-01-*",
               "GARDE: CHANTIER.md de main sans sa ligne « artefact du chantier »", "GARDE: HEAD est sur autre, pas sur main",
               "n'est pas la racine d'un dépôt Git", "GARDE: arbre pas propre (1 chemin(s))")
    assert all(c == 1 and a in s and "GARDE:" in s for (c, s), a in zip(sorties, attendu))
    assert code_git(d, "merge-base", "--is-ancestor", nom, "main") == 1
    assert code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD") != 0


def depot_nui16(fab, d, fichiers=None, archive=True):
    """`depot_matin` sur l'état à quatre rangées et son journal, puis `fichiers` (`{chemin: texte}`) en un 2e commit."""
    fab.depot(d, archive=archive, etat=ETAT_NUI16)
    for chemin, texte in (fichiers or {}).items():
        ecrire(os.path.join(d, chemin), texte)
    if fichiers:
        commit_matin(d, "fichiers", 0)


def retoucher(chemin, f):
    """Une retouche pour `branche_matin(modifs=…)` : réécrit `chemin` (relatif au dépôt) par `f(texte)`."""
    def faire(d):
        complet = os.path.join(d, chemin)
        ecrire(complet, f(lire(complet)))
    return faire


def resumee(lettre, texte):
    """Ce que `clore --resume` fait de CLAUDE.md : `resume_claude`, qui coupe aux `CLOS_GARDES` dernières."""
    def faire(t):
        cl = t.split("\n")[:-1]
        mod.resume_claude(cl, lettre, texte, JOUR_MATIN, [])
        return "\n".join(cl) + "\n"
    return faire


def rangees(texte, motif=r"`(\d\d)-"):
    return re.findall(motif, "\n".join(l for l in texte.splitlines() if l.startswith("|")))


def matin_n_a(tr, fab):
    """(a) 2cef70f : A retire la rangée 58 de la TODO, B en ajoute une 83 ; puis la 82 changée des deux côtés."""
    d = os.path.join(tr, "na")
    depot_nui16(fab, d)
    a = branche_matin(d, "A", "AAA", "AAA", 1, retire="58")
    b = branche_matin(d, "B", "BBB", "BBB", 2,
                      modifs=retoucher(ETAT, lambda t: t.replace(RANGEE_82, RANGEE_82 + "| 83 | `NEW` — neuf | d | 1 fiche | — |\n")))
    code, s = appel(["matin", d, JOUR_MATIN])
    etat = lire(os.path.join(d, ETAT))
    parents = git_matin(d, "rev-list", "--parents", "-n", "1", "HEAD").split()
    assert code == 0
    assert s == ORDRE_ABSENT + "FUSIONNÉE %s\nFUSIONNÉE %s\nMATIN 2 fusionnée(s) · 0 de côté\n" % (a, b)
    assert re.findall(r"^\| (\d+) \|", etat, re.M) == ["79", "80", "82", "83"]
    assert "<<<<<<<" not in etat
    assert code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD") != 0
    assert len(parents) == 3
    d = os.path.join(tr, "nb")
    depot_nui16(fab, d)
    a = branche_matin(d, "A", "AAA", "AAA", 1, modifs=retoucher(ETAT, lambda t: t.replace("| c |", "| cA |")))
    b = branche_matin(d, "B", "BBB", "BBB", 2, modifs=retoucher(ETAT, lambda t: t.replace("| c |", "| cB |")))
    code, s = appel(["matin", d, JOUR_MATIN])
    assert code == 1
    assert "GARDE: ctx/08-etat.md : TODO : la rangée n° 82 est changée des deux côtés" in s
    assert "FUSIONNÉE %s\n" % a in s
    assert "ARRÊT %s — conflit : ctx/08-etat.md" % b in s
    assert code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD") == 0
    assert git_matin(d, "log", "-1", "--format=%s").strip() == "Matin %s : %s" % (JOUR_MATIN, a)


def matin_n_b(tr, fab):
    """(b) 5d7fc42 : A et B ajoutent un bloc au journal, en fin de fichier."""
    d = os.path.join(tr, "nj")
    depot_nui16(fab, d)
    branche_matin(d, "A", "AAA", "AAA", 1, modifs=retoucher(ETAT, lambda t: t + "## 2026-10-01 — AAA\nbloc de A\n"))
    branche_matin(d, "B", "BBB", "BBB", 2, modifs=retoucher(ETAT, lambda t: t + "## 2026-10-01 — BBB\nbloc de B\n"))
    code, s = appel(["matin", d, JOUR_MATIN])
    etat = lire(os.path.join(d, ETAT))
    assert code == 0
    assert s.endswith("MATIN 2 fusionnée(s) · 0 de côté\n")
    assert "<<<<<<<" not in etat
    assert etat.index("une ligne de base") < etat.index("bloc de A") < etat.index("bloc de B")
    assert etat.count("## 2026-10-01 — AAA") == etat.count("## 2026-10-01 — BBB") == 1
    assert re.findall(r"^\| (\d+) \|", etat, re.M) == ["58", "79", "80", "82"]


def matin_n_c(tr, fab):
    """(c) CLAUDE.md à `CLOS_GARDES` lignes « Clos le » : A et B en closent un chacun ; le reste de chacun change aussi."""
    d = os.path.join(tr, "nk")
    depot_nui16(fab, d, {"CLAUDE.md": CLAUDE_NUI16})
    branche_matin(d, "A", "AAA", "AAA", 1,
                  modifs=retoucher("CLAUDE.md", lambda t: resumee("AAA", "fait A")(t).replace("le kit tient.", "le kit tient, A.")))
    branche_matin(d, "B", "BBB", "BBB", 2,
                  modifs=retoucher("CLAUDE.md", lambda t: resumee("BBB", "fait B")(t).replace("1. une règle.", "1. une règle, B.")))
    code, _s = appel(["matin", d, JOUR_MATIN])
    claude = lire(os.path.join(d, "CLAUDE.md"))
    clos = [l for l in claude.splitlines() if mod.ENTREE_CLOS.match(l)]
    assert code == 0
    assert len(clos) == mod.CLOS_GARDES
    assert clos[-2].endswith("(chantier AAA).")
    assert clos[-1].endswith("(chantier BBB).")
    assert "(chantier CCB)" not in claude
    assert "(chantier CCC)" in claude
    assert "le kit tient, A." in claude
    assert "1. une règle, B." in claude
    assert "<<<<<<<" not in claude


def matin_n_d(tr, fab):
    """(d) l'index, son archive (désordonnée) et `archive-clos.html` : A et B clôturent chacun un chantier."""
    d = os.path.join(tr, "ni")
    depot_nui16(fab, d, {"ctx/00-INDEX.md": INDEX_NUI16, "ctx/00-INDEX-archive.md": ARCHIVE_NUI16})

    def clot(retire, ouvre, apres, rangee):
        def faire(d):
            retoucher("ctx/00-INDEX.md", lambda t: t.replace(retire, "") + ouvre)(d)
            retoucher("ctx/00-INDEX-archive.md", lambda t: t.replace(apres, apres + rangee))(d)
        return faire
    branche_matin(d, "A", "AAA", "AAA", 1, ligne="AAA1–AAA2", modifs=clot(
        "| `41-aaa.md` | on joue AAA — chantier **ouvert** |\n", "| `43-ccc.md` | on joue CCC — chantier **ouvert** |\n",
        "| `50-z.md` | chantier **clos** Z |\n", "| `41-aaa.md` | chantier **clos** AAA |\n"))
    branche_matin(d, "B", "BBB", "BBB", 2, ligne="BBB1", modifs=clot(
        "| `42-bbb.md` | on joue BBB — chantier **ouvert** |\n", "| `44-ddd.md` | on joue DDD — chantier **ouvert** |\n",
        "| `10-x.md` | chantier **clos** X |\n", "| `20-bbb.md` | chantier **clos** BBB |\n"))
    code, _s = appel(["matin", d, JOUR_MATIN])
    index, archive = lire(os.path.join(d, "ctx", "00-INDEX.md")), lire(os.path.join(d, "ctx", "00-INDEX-archive.md"))
    clos = lire(os.path.join(d, "ctx", "artefacts", mod.ARCHIVE_CLOS))
    debut, fin = mod.zone(clos, "clos", "<tbody>\n", "        </tbody>")
    corps = clos[debut:fin]
    places = [corps.find(m) for m in ("BBB1", "AAA1–AAA2", "X1", "Y1")]
    pied = re.search(r'Total cumulé</td><td class="mono"><strong>(.*?)</strong>', clos)
    assert code == 0
    assert rangees(index) == ["08", "00", "40", "43", "44"]
    assert "<<<<<<<" not in index + archive
    assert rangees(archive) == ["10", "20", "41", "50"]
    assert len(mod.lignes_clos(corps)) == 4
    assert -1 not in places
    assert places == sorted(places)
    assert pied is not None
    assert pied.group(1) == mod.arrondi(mod.total_clos(corps))
    assert mod.total_clos(corps) == 72000
    assert "4 chantiers clos" in clos
    assert "<<<<<<<" not in clos


def matin_n_e(tr, fab):
    """(e) `en-attente` : retirée par A et intacte en B ; changée des deux côtés ; vide ; non suivie."""
    def heure(h):
        return "2026-10-01T%02d:00+02:00" % h

    def attente(*entrees):
        return "".join("%s\turl%s\t%s\n" % (p, p, h) for p, h in entrees)
    d = os.path.join(tr, "ne1")
    depot_nui16(fab, d, {ATTENTE: attente(("P", heure(8)), ("Q", heure(8)))})
    branche_matin(d, "A", "AAA", "AAA", 1, modifs=retoucher(ATTENTE, lambda t: attente(("Q", heure(11)))))
    branche_matin(d, "B", "BBB", "BBB", 2, modifs=retoucher(ATTENTE, lambda t: attente(("P", heure(8)), ("Q", heure(10)))))
    code, _ = appel(["matin", d, JOUR_MATIN])
    assert code == 0
    assert lire(os.path.join(d, ATTENTE)) == attente(("Q", heure(11)))
    d = os.path.join(tr, "ne2")
    depot_nui16(fab, d, {ATTENTE: attente(("P", heure(8)), ("Q", heure(8)))})
    branche_matin(d, "A", "AAA", "AAA", 1, modifs=retoucher(ATTENTE, lambda t: attente(("Q", heure(8)))))
    branche_matin(d, "B", "BBB", "BBB", 2, modifs=retoucher(ATTENTE, lambda t: attente(("P", heure(8)))))
    code, _ = appel(["matin", d, JOUR_MATIN])
    suivis = git_matin(d, "ls-tree", "-r", "--name-only", "HEAD").splitlines()
    assert code == 0
    assert not os.path.exists(os.path.join(d, ATTENTE))
    assert ATTENTE not in suivis
    assert not git_matin(d, "status", "--porcelain")
    d = os.path.join(tr, "ne3")
    depot_nui16(fab, d)
    ecrire(os.path.join(d, ".git", "info", "exclude"), "en-attente\n")
    ecrire(os.path.join(d, ATTENTE), attente(("P", heure(9))))
    branche_matin(d, "A", "AAA", "AAA", 1)
    branche_matin(d, "B", "BBB", "BBB", 2)
    code, _s = appel(["matin", d, JOUR_MATIN])
    assert code == 0
    assert lire(os.path.join(d, ATTENTE)) == attente(("P", heure(9)))


def publie_essai(fab, tr, nom, base, ea, eb):
    """L'essai D2 : un dépôt à `publie merge=union`, deux branches écrites par `noter_publie` ; `(ce que Git en fait lu par
    lire_publie, ce que fusion_publie en fait, ses lignes imprimées)`."""
    d = os.path.join(tr, "pub-" + nom)
    art = os.path.join(d, "art")
    fab.nu(d)
    os.makedirs(art)
    ecrire(os.path.join(d, ".gitattributes"), "publie merge=union\n")
    ecrire(os.path.join(d, "x"), "x\n")
    if base:
        mod.noter_publie(art, "P", base)
    commit_matin(d, "base", 0)
    for branche, e in (("A", ea), ("B", eb)):
        git_matin(d, "switch", "-q", "-c", branche, "main")
        os.makedirs(art, exist_ok=True)
        mod.noter_publie(art, "P", e)
        commit_matin(d, branche, 1)
        git_matin(d, "switch", "-q", "main")
    git_matin(d, "merge", "-q", "--no-ff", "-m", "A", "A")
    textes = [mod.lire_rev(d, rev, "art/publie") for rev in (git_matin(d, "merge-base", "HEAD", "B").strip(), "HEAD", "B")]
    infos = []
    par_cle = mod.notes_publie(mod.fusion_publie(d, "B", textes, [], infos).split("\n"))
    code_git(d, "merge", "-q", "--no-edit", "B")
    return mod.lire_publie(art), par_cle, infos


def matin_n_f(tr, fab):
    """(f) `publie` : l'essai D2 en quatre cas, l'état choisi verrouillé, puis `matin` de bout en bout."""
    h = {n: n * 64 for n in "123"}
    cas = (("disjointes", {"a": h["1"]}, {"b": h["2"]}, {"c": h["3"]}),
           ("meme", {"a": h["1"]}, {"b": h["2"]}, {"b": h["2"]}),
           ("differentes", {"a": h["1"]}, {"a": h["2"]}, {"a": h["3"]}),
           ("sans-base", None, {"a": h["1"], "k": h["2"]}, {"c": h["3"], "k": h["2"]}))
    mesures = [publie_essai(fab, tr, nom, base, ea, eb) for nom, base, ea, eb in cas]
    gitattributes = lire(os.path.join(ICI, "..", ".gitattributes"))
    assert [u == c for u, c, _ in mesures] == [True, True, False, True]
    assert "merge=union" not in gitattributes
    assert mesures[2][1] == {}
    assert list(mesures[2][0].values()) == [h["3"]]
    assert [len(i) for _, _, i in mesures] == [0, 0, 1, 0]
    assert mesures[2][2][0].startswith("PUBLIE P a — ")
    d = os.path.join(tr, "np")
    css, js = "feuille-de-route.html\tvlp.css\t", "feuille-de-route.html\tvlp.js\t"
    depot_nui16(fab, d, {PUBLIE_MATIN: css + h["1"] + "\n" + js + h["1"] + "\n"})
    branche_matin(d, "A", "AAA", "AAA", 1, modifs=retoucher(PUBLIE_MATIN, lambda t: css + h["2"] + "\n" + js + h["1"] + "\n"))
    branche_matin(d, "B", "BBB", "BBB", 2, modifs=retoucher(PUBLIE_MATIN, lambda t: css + h["3"] + "\n" + js + h["2"] + "\n"))
    code, s = appel(["matin", d, JOUR_MATIN])
    assert code == 0
    assert "PUBLIE feuille-de-route.html vlp.css — empreintes différentes des deux côtés, clé retirée" in s
    assert lire(os.path.join(d, PUBLIE_MATIN)) == js + h["2"] + "\n"


def somme_transcripts(*transcripts):
    """`(usd, tours)` de `transcripts` mesurés par `mesure-tokens.py` : le dollar exact sommé puis arrondi au cent."""
    from decimal import ROUND_HALF_UP
    usd, tours = Decimal(0), 0
    for p in transcripts:
        r = mod.mesure().mesurer(p)[0]
        usd, tours = usd + r["usd_exact"], tours + r["tours"]
    return float(usd.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)), tours


def octets(chemin):
    """Les octets de `chemin`."""
    with open(chemin, "rb") as f:
        return f.read()


def decor_matin_r(tr, fab):
    """Le décor de `matin_r` : un dépôt à deux branches de nuit (A fusionnable, B de côté), le carnet du jour, et un
    `HOME` à transcriptions — dont un sous-agent d'un modèle hors GRILLE ; rend `(dépôt, home, carnet, chemins, sous)`."""
    d, h = os.path.join(tr, "r"), os.path.join(tr, "home-r")
    fab.depot(d)
    ecrire(os.path.join(d, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n| `40-loc.md` | x |\n")
    commit_matin(d, "index", 0)
    branche_matin(d, "A", "AAA", "AAA", 1)
    branche_matin(d, "B", "PAR", None, 2, clos=False, x="a = 1\nb = 2\nc = 30\n")
    c = mod.carnet.du_jour(d, JOUR_MATIN)
    assert c
    pr = os.path.join(h, ".claude", "projects", "p")
    chemins = {n: os.path.join(pr, n + ".jsonl") for n in ("s-aaa-1", "s-aaa-r", "s-par-1", "s-par-r")}
    sous = {n: os.path.join(pr, n, "subagents", "agent-a1.jsonl") for n in ("s-aaa-1", "s-par-1")}
    for p in sous.values():
        os.makedirs(os.path.dirname(p))
    transcript(chemins["s-aaa-1"], 2)
    transcript(sous["s-aaa-1"], 1)
    transcript(chemins["s-aaa-r"], 1)
    transcript(chemins["s-par-1"], 1)
    transcript(chemins["s-par-r"], 1)
    with open(sous["s-par-1"], "w", encoding="utf-8") as f:     # un sous-agent d'un modèle hors GRILLE
        f.write(json.dumps({"type": "assistant", "requestId": "r0", "message": {
            "id": "m0", "model": "claude-inconnu-9", "content": [], "usage": {
                "input_tokens": 1000, "output_tokens": 0, "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0}}}) + "\n")
    return d, h, c, chemins, sous


def carnet_matin_r(c):
    """Les neuf lignes du carnet de `matin_r` et sa note de base ; puis `nuits noter` : deux notes à sorte, une sans,
    et `--stop` refusé."""
    def ligne_c(**champs):
        mod.carnet.ajouter(c, nuit=JOUR_MATIN, **champs)

    ligne_c(canal="A", chantier="AAA", fiche="AAA1", note="depart jouer", session="s-aaa-1", plugin_retard=4)
    ligne_c(canal="A", chantier="AAA", role="jouer", fiche="AAA1", issue="jouée", modeles_vus=["claude-sonnet-5-5"],
            usd_cli=7.77, tours_cli=9, session="s-aaa-1", plugin_retard=4)
    ligne_c(canal="A", chantier="AAA", role="relire", fiche="AAA1", issue="jouée", session="s-aaa-r")
    ligne_c(canal="A", chantier="AAA", role="clore", issue="jouée", session="s-aaa-c")
    ligne_c(canal="B", chantier="PAR", role="jouer", fiche="PAR1", issue="jouée", session="s-par-1")
    ligne_c(canal="B", chantier="PAR", role="relire", fiche="PAR1", issue="jouée", refus_n=1, cause="la cause du refus",
            reecriture="RÉÉCRITURE : refaire le test", session="s-par-r")
    ligne_c(canal="B", chantier="PAR", garde="mis-de-cote:test cassé")
    ligne_c(canal="B", chantier="DEP", issue="pas partie", garde="saute:PAR")
    ligne_c(canal="B", chantier="ZZZ", garde="mis-de-cote:sans branche")
    mod.carnet.noter(c, "A", "base abc123")
    codes = [appel(["nuits", "noter", "verser ceci", "--canal", "A", "--sorte", "reste"])[0],
             appel(["nuits", "noter", "faire niveau", "--canal", "B", "--sorte", "case3"])[0],
             appel(["nuits", "noter", "oubli de sorte", "--canal", "A"])[0]]
    code_stop, s_stop = appel(["nuits", "noter", "x", "--stop", "--sorte", "reste"])
    sortes = [(x["note"], x["sorte"]) for x in mod.carnet.lire(c) if x["note"] and not x["note"].startswith(("depart", "base"))]
    assert codes == [0, 0, 0]
    assert sortes == [("verser ceci", "reste"), ("faire niveau", "case3"), ("oubli de sorte", None)]
    assert code_stop == 1
    assert s_stop.startswith("GARDE: --sorte")
    assert len(mod.carnet.lire(c)) == 13


def rapport_matin_r(d, c, rapport, chemins, sous):
    """`matin`, puis `matin --rapport` deux fois : le carnet complété (sous-agents sommés, jamais 0), une ligne par
    chantier au fichier des nuits ; rejoué, rien ne change. Rend `(fichier des nuits, sortie, JSON, table du jour)`."""
    code, s = appel(["matin", d, JOUR_MATIN])
    assert code == 0
    assert s.endswith("MATIN 1 fusionnée(s) · 1 de côté\n")
    avant = git_matin(d, "rev-list", "--count", "HEAD")
    code1, s1 = appel(["matin", d, JOUR_MATIN, "--rapport", rapport])
    carnet1, json1 = octets(c), octets(rapport)
    nuits = mod.fichier_nuits(d)
    assert nuits
    nuits1 = octets(nuits)
    code2, s2 = appel(["matin", d, JOUR_MATIN, "--rapport", rapport])
    lignes = mod.carnet.lire(c)
    par_session = {x["session"]: x for x in lignes if mod.carnet.est_session(x)}
    u_a, t_a = somme_transcripts(chemins["s-aaa-1"], sous["s-aaa-1"])
    u_r, t_r = somme_transcripts(chemins["s-aaa-r"])
    u_p, t_p = somme_transcripts(chemins["s-par-r"])
    assert code1 == 0
    assert (par_session["s-aaa-1"]["usd_kit"], par_session["s-aaa-1"]["tours_kit"]) == (u_a, t_a)
    assert (par_session["s-aaa-r"]["usd_kit"], par_session["s-aaa-r"]["tours_kit"]) == (u_r, t_r)
    assert (par_session["s-par-r"]["usd_kit"], par_session["s-par-r"]["tours_kit"]) == (u_p, t_p)
    assert par_session["s-aaa-1"]["usd_cli"] == 7.77
    assert t_a == 3
    assert s1.startswith("KIT ? ")
    assert all(par_session[n]["usd_kit"] is None and par_session[n]["tours_kit"] is None for n in ("s-aaa-c", "s-par-1"))
    assert "KIT ? s-aaa-c — transcription introuvable\n" in s1
    assert "KIT ? s-par-1 — modèle hors grille (claude-inconnu-9)\n" in s1
    assert s1.count("KIT ? ") == 2
    table = [l for l in octets(nuits).decode("utf-8").splitlines() if l.startswith("| " + JOUR_MATIN)]
    euros = lambda v: ("%.2f" % v).replace(".", ",")
    assert code2 == 0
    assert carnet1 == octets(c)
    assert nuits1 == octets(nuits)
    assert json1 == octets(rapport)
    assert len(table) == 4
    assert "NUITS ctx/41-nuits.md · 4 ligne(s) ajoutée(s)\n" in s1
    assert "NUITS ctx/41-nuits.md · 0 ligne(s) ajoutée(s)\n" in s2
    assert "| %s | A | AAA | 1/1/0 | ≥ %s |" % (JOUR_MATIN, euros(u_a + u_r)) in table
    assert "| %s | B | PAR | 1/0/1 | ≥ %s |" % (JOUR_MATIN, euros(u_p)) in table
    assert not os.path.exists(c + ".verrou")
    assert git_matin(d, "rev-list", "--count", "HEAD") == avant
    return nuits, s1, json1, table


def choix_matin_r(s1, json1):
    """Le JSON de `chef page` rendu par `matin --rapport` : les cartes de choix, la note sans sorte, l'écart, et aucun
    chiffre de la CLI ni push."""
    donnees = json.loads(json1.decode("utf-8"))
    choix = donnees.get("choix", [])
    titres = [q["titre"] for q in choix]
    cote =next((q for q in choix if q["titre"].startswith("Mis de côté : PAR")), {})
    reste = next((q for q in choix if q["titre"].startswith("Reste à verser")), {})
    case3 = next((q for q in choix if q["titre"].startswith("Case 3")), {})
    sans = [m for m in donnees.get("mal", []) if m["titre"] == "NOTE SANS SORTE"]
    assert [len(q.get("options", [])) for q in (cote, reste, case3)] == [3, 3, 2]
    assert [o["valeur"] for o in cote["options"]] == ["reprendre", "abandonner", "rejouer"]
    assert [o["valeur"] for o in reste["options"]] == ["verser", "fondre", "abandonner"]
    assert len(sans) == 1
    assert "oubli de sorte" in sans[0]["texte"]
    assert "NOTE SANS SORTE A — oubli de sorte\n" in s1
    assert "ÉCART B-ZZZ — le carnet le met de côté, Git non" in s1
    assert s1.count("ÉCART ") == 1
    assert any("Chantiers sautés à cause de lui : DEP" in p for p in cote["puces"])
    assert any("la cause du refus" in p for p in cote["puces"])
    assert any("`git branch -D nuit/" in o["effet"] for o in cote["options"])
    assert "7,77" not in json1.decode("utf-8")
    assert "7.77" not in json1.decode("utf-8")
    assert "push" not in json1.decode("utf-8").lower()
    assert len(titres) == 4
    assert [t.startswith("Mis de côté : ") for t in titres].count(True) == 2
    assert any("ZZZ" in t for t in titres)


def page_et_lecons_matin_r(tr, d, rapport, nuits):
    """Le JSON du rapport fait une page saine à quatre cartes ; `nuits lecon` refuse une leçon hors forme, ajoute la
    bonne une seule fois, sous « ## Leçons »."""
    html = os.path.join(tr, "rapport-r.html")
    code, s = appel(["chef", "page", "--questions", "@" + rapport, "--sortie", html])
    assert code == 0
    assert s.startswith("PAGE SAINE ")
    assert s.endswith("CARTES Q1 Q2 Q3 Q4\n")
    code_h, s_h = appel(["nuits", "lecon", "hors forme", "--projet", d])
    lecon = "- %s · N=1 · cause un · jouées 3 sur 5 · nuits %s · sessions s-aaa-1" % (JOUR_MATIN, JOUR_MATIN)
    code_l, s_l = appel(["nuits", "lecon", lecon, "--projet", d])
    code_m, s_m = appel(["nuits", "lecon", lecon, "--projet", d])
    textes = octets(nuits).decode("utf-8").splitlines()
    assert code_h == 1
    assert s_h.startswith("GARDE: leçon hors forme")
    assert code_l == 0
    assert s_l == "LEÇON ctx/41-nuits.md · ajoutée\n"
    assert code_m == 0
    assert s_m == "LEÇON ctx/41-nuits.md · déjà là\n"
    assert textes.count(lecon) == 1
    assert textes.index("## Leçons") < textes.index(lecon)


def transcription_parait_matin_r(h, d, c, rapport, table):
    """La transcription qui manquait paraît : le carnet la mesure, la table du jour ne change pas ; une nuit sans
    carnet est gardée."""
    transcript(os.path.join(h, ".claude", "projects", "p", "s-aaa-c.jsonl"), 1)     # le chiffre de A/AAA changerait
    code3, s3 = appel(["matin", d, JOUR_MATIN, "--rapport", rapport])
    nuits = mod.fichier_nuits(d)
    assert nuits
    table3 = [l for l in octets(nuits).decode("utf-8").splitlines() if l.startswith("| " + JOUR_MATIN)]
    mesuree = next(x for x in mod.carnet.lire(c) if x["session"] == "s-aaa-c")
    assert code3 == 0
    assert mesuree["usd_kit"] is not None
    assert table3 == table
    assert "NUITS ctx/41-nuits.md · 0 ligne(s) ajoutée(s)\n" in s3
    assert "KIT ? s-aaa-c" not in s3
    code_a, s_a = appel(["matin", d, "2026-10-02", "--rapport", rapport])
    assert code_a == 1
    assert s_a.startswith("GARDE: carnet de la nuit 2026-10-02 absent ou vide")


def matin_r(tr, fab):
    """NUI19 : `matin --rapport` — le carnet complété (sous-agents sommés, jamais 0), une ligne par chantier au fichier des
    nuits, le JSON de `chef page` ; rejoué, rien ne change. Un dépôt, un carnet de neuf lignes, un `HOME` à transcripts.
    Un seul scénario, dont chaque étape lit l'état laissé par la précédente : découpé en étapes, pas en tests."""
    d, h, c, chemins, sous = decor_matin_r(tr, fab)
    sauve = {k: os.environ.get(k) for k in ("HOME", "USERPROFILE", "VLP_CARNET", "VLP_CANAL")}
    os.environ.update(HOME=h, USERPROFILE=h, VLP_CARNET=c)
    os.environ.pop("VLP_CANAL", None)
    try:
        carnet_matin_r(c)
        rapport = os.path.join(tr, "rapport-r.json")
        nuits, s1, json1, table = rapport_matin_r(d, c, rapport, chemins, sous)
        choix_matin_r(s1, json1)
        page_et_lecons_matin_r(tr, d, rapport, nuits)
        transcription_parait_matin_r(h, d, c, rapport, table)
    finally:
        for k, v in sauve.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def matin_s(tr, fab):
    """(s) `matin` sans date : la seule nuit à ranger est prise et dite ; plusieurs nuits, ou aucune (tout fusionné, ou
    de côté), ne fusionnent rien ; `--rapport` veut la date."""
    d, wip_d, rapport = os.path.join(tr, "s"), os.path.join(tr, "swip"), os.path.join(tr, "s-rapport.json")
    fab.depot(d)
    nom = branche_matin(d, "A", "AAA", "AAA", 1)
    ancienne = "nuit/2026-09-30-A-OLD"
    git_matin(d, "branch", ancienne, nom)
    code2, s2 = appel(["matin", d])
    intacte = code_git(d, "merge-base", "--is-ancestor", nom, "main") == 1
    code_r, s_r = appel(["matin", d, "--rapport", rapport])
    git_matin(d, "branch", "-D", ancienne)
    code1, s1 = appel(["matin", d])
    code0, s0 = appel(["matin", d])
    fab.depot(wip_d)
    wip = branche_matin(wip_d, "A", "WIP", None, 1, clos=False, x="a = 1\nb = 2\nc = 30\n")
    codew, sw = appel(["matin", wip_d])
    aucune = "GARDE: aucune nuit à ranger (1 branche(s) nuit/* déjà fusionnée(s) ou de côté) — rien fusionné\n"
    assert code2 == 1
    assert (s2 == "GARDE: plusieurs nuits à ranger : 2026-09-30 (1), 2026-10-01 (1) — rien fusionné ; "
                 "donne la date\n")
    assert intacte
    assert code_r == 1
    assert s_r.startswith("GARDE: --rapport veut la date de la nuit")
    assert not os.path.exists(rapport)
    assert code1 == 0
    assert (s1 == ("NUIT 2026-10-01 — la seule à ranger : 1 branche(s)\n" + ORDRE_ABSENT
                                           + "FUSIONNÉE %s\nMATIN 1 fusionnée(s) · 0 de côté\n" % nom))
    assert code_git(d, "merge-base", "--is-ancestor", nom, "main") == 0
    assert code0 == 1
    assert s0 == aucune
    assert codew == 1
    assert sw == aucune
    assert code_git(wip_d, "merge-base", "--is-ancestor", wip, "main") == 1


def matin_t(tr, fab):
    """(t) une fusion qui touche `scripts/` : `PLUGIN_RETARD=1` avant `MATIN` quand le projet est le kit chargé (`KIT`),
    rien pour un autre projet (RTD1)."""
    sorties = []
    for nom, est_kit in (("t-kit", True), ("t-autre", False)):
        d = os.path.join(tr, nom)
        fab.depot(d)
        branche = branche_matin(d, "A", "RTD", "RTD", 1, x="a = 1\nb = 2\nc = 31\n")
        garde, mod.etat.KIT = mod.etat.KIT, (d if est_kit else tr)
        try:
            sorties.append(appel(["matin", d, JOUR_MATIN]) + (branche,))
        finally:
            mod.etat.KIT = garde
    (code_k, s_k, b_k), (code_a, s_a, _) = sorties
    retard = "PLUGIN_RETARD=1 commit(s) de code du plugin fusionné(s) — la session ouverte ne les voit qu'après /reload-plugins\n"
    assert code_k == 0
    assert s_k.endswith(retard + "MATIN 1 fusionnée(s) · 0 de côté\n")
    assert "FUSIONNÉE %s" % b_k in s_k
    assert code_a == 0
    assert "PLUGIN_RETARD" not in s_a


def matin_u(tr, fab):
    """(u) une branche qui laisse une page en attente : `matin` imprime son `ATTENTE=` avant `MATIN` (NPB1)."""
    d = os.path.join(tr, "u")
    fab.depot(d)
    attente = "50-x.html\thttps://claude.ai/artifact/x\t2026-10-01T01:00+02:00\n"
    branche_matin(d, "A", "NPB", "NPB", 1, modifs=lambda r: ecrire(os.path.join(r, "ctx", "artefacts", "en-attente"),
                                                                    attente))
    code, s = appel(["matin", d, JOUR_MATIN])
    assert code == 0
    assert s.endswith("ATTENTE=50-x.html https://claude.ai/artifact/x\nMATIN 1 fusionnée(s) · 0 de côté\n")


def test_matin_a(tmp_path, fab):
    matin_a(str(tmp_path), fab)


def test_matin_b(tmp_path, fab):
    matin_b(str(tmp_path), fab)


def test_matin_c(tmp_path, fab):
    matin_c(str(tmp_path), fab)


def test_matin_d(tmp_path, fab):
    matin_d(str(tmp_path), fab)


def test_matin_e(tmp_path, fab):
    matin_e(str(tmp_path), fab)


def test_matin_h(tmp_path, fab):
    matin_h(str(tmp_path), fab)


def test_matin_g(tmp_path, fab):
    matin_g(str(tmp_path), fab)


def test_matin_n_a(tmp_path, fab):
    matin_n_a(str(tmp_path), fab)


def test_matin_n_b(tmp_path, fab):
    matin_n_b(str(tmp_path), fab)


def test_matin_n_c(tmp_path, fab):
    matin_n_c(str(tmp_path), fab)


def test_matin_n_d(tmp_path, fab):
    matin_n_d(str(tmp_path), fab)


def test_matin_n_e(tmp_path, fab):
    matin_n_e(str(tmp_path), fab)


def test_matin_n_f(tmp_path, fab):
    matin_n_f(str(tmp_path), fab)


def test_matin_r(tmp_path, fab):
    matin_r(str(tmp_path), fab)


def test_matin_s(tmp_path, fab):
    matin_s(str(tmp_path), fab)


def test_matin_t(tmp_path, fab):
    matin_t(str(tmp_path), fab)


def test_matin_u(tmp_path, fab):
    matin_u(str(tmp_path), fab)
