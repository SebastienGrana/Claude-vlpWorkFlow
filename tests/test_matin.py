"""NUI15 : `vlp.py matin <projet> <date>` fusionne dans main les branches de la nuit et répare ce que Git perd
sans conflit (methode-chantier.md:263-268) — migré de `tester_matin` (`scripts/test-vlp.py`, REF43). Un dépôt
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
from aides import RACINE, SCRIPTS, appel, ecrire, ligne_close, lire, mod, transcript

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git absent : matin n'est pas testé")
GABARIT_FEUILLE = os.path.join(RACINE, "templates", "artefact-feuille-de-route.html")

ICI = SCRIPTS     # le dossier de scripts/test-vlp.py, d'où ce test vient
OUVERT = "**Ouvert.** le 2026-10-08."
JOUR_MATIN = "2026-10-01"
CARTE_MATIN = ("# Chantier courant\n\n- **alias** : mt\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n"
               "- **fichier d'état** : ctx/08-etat.md\n"
               "- **artefact feuille de route** : https://claude.ai/artifact/FEU\n"
               "- **artefact du chantier** : https://claude.ai/artifact/LOC\n- **artefact archive** : aucune\n\n"
               "Lettres de fiche déjà prises : E (Enchaîner), ENQ (Les écritures Git). "
               "Un nouveau chantier en choisit un autre.\n")
ETAT_MATIN = ("# État\n\n## TODO\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n|---|---|---|---|---|\n"
              "| 79 | `LOC` — publier | a | 2 fiches | — |\n| 80 | `PAR` — deux chantiers | b | 3 fiches | — |\n\n"
              "## Journal\n")
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
    r = subprocess.run(["git"] + list(args), cwd=d, capture_output=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise RuntimeError("git %s : %s" % (" ".join(args), r.stderr))
    return r.stdout



def code_git(d, *args):
    return subprocess.run(["git"] + list(args), cwd=d, capture_output=True).returncode



def commit_matin(d, message, heure):
    """Un commit à `heure` (0 à 23) du jour de la nuit : la date de l'auteur et du commiteur est fixée."""
    os.environ["GIT_AUTHOR_DATE"] = os.environ["GIT_COMMITTER_DATE"] = "%sT%02d:00:00+00:00" % (JOUR_MATIN, heure)
    git_matin(d, "add", "-A")
    git_matin(d, "commit", "-q", "-m", message)



def depot_matin(d, archive=True, etat=ETAT_MATIN):
    """Le dépôt de 2cef70f : `main` à courant LOC et son artefact, des lettres jusqu'à ENQ, une archive de deux clos
    (`archive` faux : ils restent sur la feuille), la feuille au rang 79 — un seul commit, à l'heure 0."""
    os.makedirs(d)
    git_matin(d, "init", "-q", "-b", "main")
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



def matin_a(tr):
    """(a) 2cef70f rejoué, avec un `origin` nu (f) : la clôture de PAR rend à main son chantier ouvert, son rang, ses lettres."""
    d, origine = os.path.join(tr, "a"), os.path.join(tr, "origine.git")
    depot_matin(d)
    git_matin(tr, "init", "-q", "--bare", "-b", "main", origine)
    git_matin(d, "remote", "add", "origin", origine)
    git_matin(d, "push", "-q", "origin", "main")
    pousse = git_matin(origine, "rev-parse", "main").strip()
    nom = branche_matin(d, "A", "PAR", "PAR", 1, ligne="PAR1–PAR3", retire="80")
    code, s = appel(["matin", d, JOUR_MATIN])
    carte_, html, rang, archive = etat_matin(d)
    lettres = mod.lettres_prises(carte_)
    parents = git_matin(d, "rev-list", "--parents", "-n", "1", "HEAD").split()
    assert (code == 0 and s == ORDRE_ABSENT + "FUSIONNÉE %s\nMATIN 1 fusionnée(s) · 0 de côté\n" % nom
                 and mod.courant_de(d) == "ctx/40-loc.md"
                 and mod.champ(carte_, "artefact du chantier") == "https://claude.ai/artifact/LOC"
                 and lettres == ["E", "ENQ", "PAR"] and rang == "79" and "3 chantiers clos" in archive
                 and "<<<<<<<" not in "\n".join(carte_) + html and "Aucun chantier ouvert" not in html
                 and len(parents) == 3 and not git_matin(d, "status", "--porcelain")
                 and git_matin(d, "log", "-1", "--format=%s").strip() == "Matin %s : %s" % (JOUR_MATIN, nom)
                 and "| 80 |" not in lire(os.path.join(d, "ctx", "08-etat.md"))), ("NUI15 (a) 2cef70f rejoué : courant et artefact de LOC rendus, PAR une fois après ENQ, rang 79, archive à "
                 "3 clos, aucun conflit, HEAD à deux parents, arbre propre — mutants : lettres de la branche gardées, "
                 "todo laissé à None") + "\n" + str((code, s, carte_, rang, archive[:300]))
    assert (git_matin(origine, "rev-parse", "main").strip() == pousse != git_matin(d, "rev-parse", "main").strip()), ("NUI15 (f) un dépôt nu en origin : sa main n'a pas bougé, matin ne pousse rien") + "\n" + str((pousse, git_matin(d, "rev-parse", "main")))



def matin_b(tr):
    """(b) A et B ajoutent chacun une lettre sur la même ligne, la feuille change des deux côtés : les deux lettres
    restent ; le carnet met B avant A, bien que la pointe de B soit la plus récente."""
    d = os.path.join(tr, "b")
    depot_matin(d)
    a, b = branche_matin(d, "A", "AAA", "AAA", 1), branche_matin(d, "B", "BBB", "BBB", 2)
    carnet_ = mod.carnet.du_jour(d, JOUR_MATIN)
    os.makedirs(os.path.dirname(carnet_), exist_ok=True)
    for canal, code in (("B", "BBB"), ("A", "AAA")):
        mod.carnet.ecrire(carnet_, mod.carnet.ligne({"nuit": JOUR_MATIN, "canal": canal, "chantier": code, "role": "fiche"}))
    code, s = appel(["matin", d, JOUR_MATIN])
    carte_, html, rang, _ = etat_matin(d)
    sujets = git_matin(d, "log", "--first-parent", "--format=%s", "main").splitlines()
    assert (code == 0 and "ORDRE" not in s and s.endswith("MATIN 2 fusionnée(s) · 0 de côté\n")
                 and mod.lettres_prises(carte_) == ["E", "ENQ", "BBB", "AAA"] and rang == "79"
                 and 'Lettres de fiche prises : <span class="mono">E, ENQ, BBB, AAA, LOC</span>' in html
                 and [x for x in reversed(sujets) if x.startswith("Matin")]
                 == ["Matin %s : %s" % (JOUR_MATIN, b), "Matin %s : %s" % (JOUR_MATIN, a)]), ("NUI15 (b) deux nuits, une lettre chacune sur la même ligne, la feuille changée des deux côtés : les deux "
                 "lettres gardées, le badge au rang 79, B avant A comme au carnet (pointe de B plus récente) — mutant : "
                 "lettres de la branche gardées") + "\n" + str((code, s, mod.lettres_prises(carte_), rang, sujets))



def matin_c(tr):
    """(c) sans carnet : l'heure de la pointe ; une pointe à chantier ouvert (commit WIP) reste de côté."""
    d = os.path.join(tr, "c")
    depot_matin(d)
    wip = branche_matin(d, "A", "WIP", None, 1, clos=False, x="a = 1\nb = 2\nc = 30\n")
    ok = branche_matin(d, "B", "OKK", "OKK", 2)
    code, s = appel(["matin", d, JOUR_MATIN])
    assert (code == 0 and s == (ORDRE_ABSENT + "DE CÔTÉ %s — ctx/41-wip.md\nFUSIONNÉE %s\n"
                                     "MATIN 1 fusionnée(s) · 1 de côté\n" % (wip, ok))
                 and code_git(d, "merge-base", "--is-ancestor", wip, "main") == 1), ("NUI15 (c) sans carnet : ORDRE pointes, la pointe WIP DE CÔTÉ avant la suivante fusionnée, hors de main") + "\n" + str((code, s))



def matin_d(tr):
    """(d) un `.py` changé des deux côtés : ARRÊT qui le nomme, fusion en cours, la suivante intacte ; résolu, relancé."""
    d = os.path.join(tr, "d")
    depot_matin(d)
    a = branche_matin(d, "A", "AAA", "AAA", 1, x="a = 1\nb = 20\nc = 3\n")
    b = branche_matin(d, "B", "BBB", "BBB", 2)
    ecrire(os.path.join(d, "scripts", "x.py"), "a = 1\nb = 22\nc = 3\n")
    commit_matin(d, "main avance", 3)
    code, s = appel(["matin", d, JOUR_MATIN])
    carte_ = lire(os.path.join(d, "CHANTIER.md"))
    assert (code == 1 and s.startswith(ORDRE_ABSENT + "ARRÊT %s — conflit : scripts/x.py — après résolution : " % a)
                 and s.endswith(' feuille "%s" --todo 79\n' % d)
                 and code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD") == 0
                 and code_git(d, "merge-base", "--is-ancestor", b, "main") == 1
                 and "- **artefact du chantier** : https://claude.ai/artifact/LOC" in carte_ and "<<<<<<<" not in carte_), ("NUI15 (d) un .py changé des deux côtés : ARRÊT qui le nomme et donne feuille --todo 79, sort 1, MERGE_HEAD "
                 "là, CHANTIER.md réparé sans marque, la suivante pas fusionnée") + "\n" + str((code, s))
    ecrire(os.path.join(d, "scripts", "x.py"), "a = 1\nb = 22\nc = 3\n")
    appel(["feuille", d, "--todo", "79", "--date", JOUR_MATIN])
    commit_matin(d, "résolu", 4)
    code, s = appel(["matin", d, JOUR_MATIN])
    assert (code == 0 and s == ORDRE_ABSENT + "DÉJÀ %s\nFUSIONNÉE %s\nMATIN 1 fusionnée(s) · 0 de côté\n" % (a, b)), ("NUI15 (d) résolu, commité, relancé : DÉJÀ pour la branche résolue, la suivante fusionnée") + "\n" + str((code, s))



def matin_e(tr):
    """(e) un hook qui refuse (`core.hooksPath`) : ARRÊT, la fusion reste en cours."""
    d, hooks = os.path.join(tr, "e"), os.path.join(tr, "hooks-e")
    depot_matin(d)
    nom = branche_matin(d, "A", "AAA", "AAA", 1)
    for h in ("pre-commit", "pre-merge-commit"):
        ecrire(os.path.join(hooks, h), HOOK_REFUSE)
        os.chmod(os.path.join(hooks, h), 0o755)
    git_matin(d, "config", "core.hooksPath", hooks.replace("\\", "/"))
    code, s = appel(["matin", d, JOUR_MATIN])
    assert (code == 1 and s == ORDRE_ABSENT + "ARRÊT %s — commit refusé : hook : refusé\n" % nom
                 and code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD") == 0), ("NUI15 (e) hook exit 1 par core.hooksPath : ARRÊT … commit refusé, la 1re ligne du hook, fusion en cours") + "\n" + str((code, s))



def matin_h(tr):
    """(h) sans archive, les clos vivent sur la feuille : une feuille en conflit ne se reprend pas de main, ARRÊT."""
    d = os.path.join(tr, "h")
    depot_matin(d, archive=False)
    a, b = branche_matin(d, "A", "AAA", "AAA", 1), branche_matin(d, "B", "BBB", "BBB", 2)
    code, s = appel(["matin", d, JOUR_MATIN])
    assert (code == 1 and s.startswith(ORDRE_ABSENT + "FUSIONNÉE %s\nARRÊT %s — conflit : ctx/artefacts/feuille-de-route.html"
                                            " — après résolution : " % (a, b)) and s.endswith(" --todo 79\n")
                 and code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD") == 0), ("NUI15 (h) sans archive, feuille changée des deux côtés : la 1re fusionnée, ARRÊT sur la feuille pour la "
                 "2e, fusion en cours") + "\n" + str((code, s))



def matin_g(tr):
    """(g) les gardes : date, aucune branche, HEAD hors main, pas la racine, arbre sale, non équipé, CHANTIER.md sans
    libellés — chaque fois rien fusionné."""
    d, mini, vide = os.path.join(tr, "g"), os.path.join(tr, "mini"), os.path.join(tr, "vide")
    depot_matin(d)
    nom = branche_matin(d, "A", "AAA", "AAA", 1)
    os.makedirs(vide)
    os.makedirs(mini)
    git_matin(mini, "init", "-q", "-b", "main")
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
    assert (all(c == 1 and a in s and "GARDE:" in s for (c, s), a in zip(sorties, attendu))
                 and code_git(d, "merge-base", "--is-ancestor", nom, "main") == 1
                 and code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD") != 0), ("NUI15 (g) sept gardes : non équipé, date illisible, aucune branche, CHANTIER.md sans libellés, HEAD hors "
                 "main, pas la racine, arbre sale — sort 1, « rien fusionné », aucune fusion commencée") + "\n" + str(sorties)



def depot_nui16(d, fichiers=None, archive=True):
    """`depot_matin` sur l'état à quatre rangées et son journal, puis `fichiers` (`{chemin: texte}`) en un 2e commit."""
    depot_matin(d, archive=archive, etat=ETAT_NUI16)
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



def matin_n_a(tr):
    """(a) 2cef70f : A retire la rangée 58 de la TODO, B en ajoute une 83 ; puis la 82 changée des deux côtés."""
    d = os.path.join(tr, "na")
    depot_nui16(d)
    a = branche_matin(d, "A", "AAA", "AAA", 1, retire="58")
    b = branche_matin(d, "B", "BBB", "BBB", 2,
                      modifs=retoucher(ETAT, lambda t: t.replace(RANGEE_82, RANGEE_82 + "| 83 | `NEW` — neuf | d | 1 fiche | — |\n")))
    code, s = appel(["matin", d, JOUR_MATIN])
    etat = lire(os.path.join(d, ETAT))
    parents = git_matin(d, "rev-list", "--parents", "-n", "1", "HEAD").split()
    assert (code == 0 and s == ORDRE_ABSENT + "FUSIONNÉE %s\nFUSIONNÉE %s\nMATIN 2 fusionnée(s) · 0 de côté\n" % (a, b)
                 and re.findall(r"^\| (\d+) \|", etat, re.M) == ["79", "80", "82", "83"] and "<<<<<<<" not in etat
                 and code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD") != 0 and len(parents) == 3), ("NUI16 (a) 2cef70f : A retire la 58, B ajoute la 83 → 58 absente, 79, 80, 82, 83 là dans l'ordre, aucune marque, "
                 "MERGE_HEAD absent, HEAD à deux parents — mutant : retiré d'un côté gardé") + "\n" + str((code, s, etat))
    d = os.path.join(tr, "nb")
    depot_nui16(d)
    a = branche_matin(d, "A", "AAA", "AAA", 1, modifs=retoucher(ETAT, lambda t: t.replace("| c |", "| cA |")))
    b = branche_matin(d, "B", "BBB", "BBB", 2, modifs=retoucher(ETAT, lambda t: t.replace("| c |", "| cB |")))
    code, s = appel(["matin", d, JOUR_MATIN])
    assert (code == 1 and "GARDE: ctx/08-etat.md : TODO : la rangée n° 82 est changée des deux côtés" in s
                 and "FUSIONNÉE %s\n" % a in s and "ARRÊT %s — conflit : ctx/08-etat.md" % b in s
                 and code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD") == 0
                 and git_matin(d, "log", "-1", "--format=%s").strip() == "Matin %s : %s" % (JOUR_MATIN, a)), ("NUI16 (a) la 82 changée en A et en B : GARDE: qui la nomme, sort 1, la fusion de B reste en cours, aucun commit "
                 "pour B") + "\n" + str((code, s))



def matin_n_b(tr):
    """(b) 5d7fc42 : A et B ajoutent un bloc au journal, en fin de fichier."""
    d = os.path.join(tr, "nj")
    depot_nui16(d)
    a = branche_matin(d, "A", "AAA", "AAA", 1, modifs=retoucher(ETAT, lambda t: t + "## 2026-10-01 — AAA\nbloc de A\n"))
    b = branche_matin(d, "B", "BBB", "BBB", 2, modifs=retoucher(ETAT, lambda t: t + "## 2026-10-01 — BBB\nbloc de B\n"))
    code, s = appel(["matin", d, JOUR_MATIN])
    etat = lire(os.path.join(d, ETAT))
    assert (code == 0 and s.endswith("MATIN 2 fusionnée(s) · 0 de côté\n") and "<<<<<<<" not in etat
                 and etat.index("une ligne de base") < etat.index("bloc de A") < etat.index("bloc de B")
                 and etat.count("## 2026-10-01 — AAA") == etat.count("## 2026-10-01 — BBB") == 1
                 and re.findall(r"^\| (\d+) \|", etat, re.M) == ["58", "79", "80", "82"]), ("NUI16 (b) 5d7fc42 : le journal de A puis celui de B, après le journal de la base, aucune marque, la TODO intacte") + "\n" + str((code, s, etat))



def matin_n_c(tr):
    """(c) CLAUDE.md à `CLOS_GARDES` lignes « Clos le » : A et B en closent un chacun ; le reste de chacun change aussi."""
    d = os.path.join(tr, "nk")
    depot_nui16(d, {"CLAUDE.md": CLAUDE_NUI16})
    a = branche_matin(d, "A", "AAA", "AAA", 1,
                      modifs=retoucher("CLAUDE.md", lambda t: resumee("AAA", "fait A")(t).replace("le kit tient.", "le kit tient, A.")))
    b = branche_matin(d, "B", "BBB", "BBB", 2,
                      modifs=retoucher("CLAUDE.md", lambda t: resumee("BBB", "fait B")(t).replace("1. une règle.", "1. une règle, B.")))
    code, s = appel(["matin", d, JOUR_MATIN])
    claude = lire(os.path.join(d, "CLAUDE.md"))
    clos = [l for l in claude.splitlines() if mod.ENTREE_CLOS.match(l)]
    assert (code == 0 and len(clos) == mod.CLOS_GARDES and clos[-2].endswith("(chantier AAA).") and clos[-1].endswith("(chantier BBB).")
                 and "(chantier CCB)" not in claude and "(chantier CCC)" in claude and "le kit tient, A." in claude and "1. une règle, B." in claude
                 and "<<<<<<<" not in claude), ("NUI16 (c) CLAUDE.md : CLOS_GARDES lignes « Clos le », les deux neuves dont A avant B, les plus anciennes coupées, "
                 "le reste de A et de B gardé, aucune marque — mutant : coupe non appelée") + "\n" + str((code, s, claude))



def matin_n_d(tr):
    """(d) l'index, son archive (désordonnée) et `archive-clos.html` : A et B clôturent chacun un chantier."""
    d = os.path.join(tr, "ni")
    depot_nui16(d, {"ctx/00-INDEX.md": INDEX_NUI16, "ctx/00-INDEX-archive.md": ARCHIVE_NUI16})

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
    code, s = appel(["matin", d, JOUR_MATIN])
    index, archive = lire(os.path.join(d, "ctx", "00-INDEX.md")), lire(os.path.join(d, "ctx", "00-INDEX-archive.md"))
    clos = lire(os.path.join(d, "ctx", "artefacts", mod.ARCHIVE_CLOS))
    debut, fin = mod.zone(clos, "clos", "<tbody>\n", "        </tbody>")
    corps = clos[debut:fin]
    places = [corps.find(m) for m in ("BBB1", "AAA1–AAA2", "X1", "Y1")]
    pied = re.search(r'Total cumulé</td><td class="mono"><strong>(.*?)</strong>', clos)
    assert (code == 0 and rangees(index) == ["08", "00", "40", "43", "44"] and "<<<<<<<" not in index + archive
                 and rangees(archive) == ["10", "20", "41", "50"]), ("NUI16 (d) index : 41 et 42 retirées, 43 et 44 ajoutées une fois, A avant B, le reste intact ; archive : "
                 "10, 20, 41, 50 triées") + "\n" + str((code, s, index, archive))
    assert (len(mod.lignes_clos(corps)) == 4 and -1 not in places and places == sorted(places)
                 and pied is not None and pied.group(1) == mod.arrondi(mod.total_clos(corps)) and mod.total_clos(corps) == 72000
                 and "4 chantiers clos" in clos and "<<<<<<<" not in clos), ("NUI16 (d) archive-clos.html : 4 lignes, celle de B en tête puis celle de A puis celles de la base ; le pied est "
                 "`total_clos` de ces 4 lignes, le résumé en compte 4") + "\n" + str((code, s, corps, pied))



def matin_n_e(tr):
    """(e) `en-attente` : retirée par A et intacte en B ; changée des deux côtés ; vide ; non suivie."""
    def heure(h):
        return "2026-10-01T%02d:00+02:00" % h

    def attente(*entrees):
        return "".join("%s\turl%s\t%s\n" % (p, p, h) for p, h in entrees)
    d = os.path.join(tr, "ne1")
    depot_nui16(d, {ATTENTE: attente(("P", heure(8)), ("Q", heure(8)))})
    branche_matin(d, "A", "AAA", "AAA", 1, modifs=retoucher(ATTENTE, lambda t: attente(("Q", heure(11)))))
    branche_matin(d, "B", "BBB", "BBB", 2, modifs=retoucher(ATTENTE, lambda t: attente(("P", heure(8)), ("Q", heure(10)))))
    code, s = appel(["matin", d, JOUR_MATIN])
    assert (code == 0 and lire(os.path.join(d, ATTENTE)) == attente(("Q", heure(11)))), ("NUI16 (e) en-attente : P retirée par A et intacte en B → absente ; Q changée des deux côtés → l'heure la plus "
                 "récente, celle de A bien que B soit fusionnée après") + "\n" + str((code, s))
    d = os.path.join(tr, "ne2")
    depot_nui16(d, {ATTENTE: attente(("P", heure(8)), ("Q", heure(8)))})
    branche_matin(d, "A", "AAA", "AAA", 1, modifs=retoucher(ATTENTE, lambda t: attente(("Q", heure(8)))))
    branche_matin(d, "B", "BBB", "BBB", 2, modifs=retoucher(ATTENTE, lambda t: attente(("P", heure(8)))))
    code, s = appel(["matin", d, JOUR_MATIN])
    suivis = git_matin(d, "ls-tree", "-r", "--name-only", "HEAD").splitlines()
    assert (code == 0 and not os.path.exists(os.path.join(d, ATTENTE)) and ATTENTE not in suivis
                 and not git_matin(d, "status", "--porcelain")), ("NUI16 (e) en-attente : P retirée par A, Q par B → vide → le fichier est retiré, de l'arbre et de l'index — "
                 "mutant : retrait ignoré") + "\n" + str((code, s, suivis))
    d = os.path.join(tr, "ne3")
    depot_nui16(d)
    ecrire(os.path.join(d, ".git", "info", "exclude"), "en-attente\n")
    ecrire(os.path.join(d, ATTENTE), attente(("P", heure(9))))
    branche_matin(d, "A", "AAA", "AAA", 1)
    branche_matin(d, "B", "BBB", "BBB", 2)
    code, s = appel(["matin", d, JOUR_MATIN])
    assert (code == 0 and lire(os.path.join(d, ATTENTE)) == attente(("P", heure(9)))), ("NUI16 (e) en-attente non suivie, présente dans l'arbre de main : ni écrite ni retirée") + "\n" + str((code, s))



def publie_essai(tr, nom, base, ea, eb):
    """L'essai D2 : un dépôt à `publie merge=union`, deux branches écrites par `noter_publie` ; `(ce que Git en fait lu par
    lire_publie, ce que fusion_publie en fait, ses lignes imprimées)`."""
    d = os.path.join(tr, "pub-" + nom)
    art = os.path.join(d, "art")
    os.makedirs(art)
    git_matin(d, "init", "-q", "-b", "main")
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



def matin_n_f(tr):
    """(f) `publie` : l'essai D2 en quatre cas, l'état choisi verrouillé, puis `matin` de bout en bout."""
    h = {n: n * 64 for n in "123"}
    cas = (("disjointes", {"a": h["1"]}, {"b": h["2"]}, {"c": h["3"]}),
           ("meme", {"a": h["1"]}, {"b": h["2"]}, {"b": h["2"]}),
           ("differentes", {"a": h["1"]}, {"a": h["2"]}, {"a": h["3"]}),
           ("sans-base", None, {"a": h["1"], "k": h["2"]}, {"c": h["3"], "k": h["2"]}))
    mesures = [publie_essai(tr, nom, base, ea, eb) for nom, base, ea, eb in cas]
    gitattributes = lire(os.path.join(ICI, "..", ".gitattributes"))
    assert ([u == c for u, c, _ in mesures] == [True, True, False, True] and "merge=union" not in gitattributes
                 and mesures[2][1] == {} and list(mesures[2][0].values()) == [h["3"]]
                 and [len(i) for _, _, i in mesures] == [0, 0, 1, 0] and mesures[2][2][0].startswith("PUBLIE P a — ")), ("NUI16 (f) essai D2, 4 cas : `merge=union` donne comme la clé pour des clés disjointes, une même clé de même "
                 "empreinte et un fichier absent de la base, et non pour des empreintes différentes (deux lignes, la dernière lue ; "
                 "la clé dit : retirée) — d'où la fusion par clé, et aucune ligne `merge=union` au .gitattributes du kit") + "\n" + str([(u, c, i) for u, c, i in mesures])
    d = os.path.join(tr, "np")
    css, js = "feuille-de-route.html\tvlp.css\t", "feuille-de-route.html\tvlp.js\t"
    depot_nui16(d, {PUBLIE_MATIN: css + h["1"] + "\n" + js + h["1"] + "\n"})
    branche_matin(d, "A", "AAA", "AAA", 1, modifs=retoucher(PUBLIE_MATIN, lambda t: css + h["2"] + "\n" + js + h["1"] + "\n"))
    branche_matin(d, "B", "BBB", "BBB", 2, modifs=retoucher(PUBLIE_MATIN, lambda t: css + h["3"] + "\n" + js + h["2"] + "\n"))
    code, s = appel(["matin", d, JOUR_MATIN])
    assert (code == 0 and "PUBLIE feuille-de-route.html vlp.css — empreintes différentes des deux côtés, clé retirée" in s
                 and lire(os.path.join(d, PUBLIE_MATIN)) == js + h["2"] + "\n"), ("NUI16 (f) matin : vlp.css aux empreintes différentes → clé retirée et dite (`PUBLIE …`), vlp.js changée d'un seul "
                 "côté → la valeur de B") + "\n" + str((code, s))



def matin_r(tr):
    """NUI19 : `matin --rapport` — le carnet complété (sous-agents sommés, jamais 0), une ligne par chantier au fichier des
    nuits, le JSON de `chef page` ; rejoué, rien ne change. Un dépôt, un carnet de neuf lignes, un `HOME` à transcripts."""
    from decimal import ROUND_HALF_UP
    d, h = os.path.join(tr, "r"), os.path.join(tr, "home-r")
    depot_matin(d)
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

    def somme(*transcripts):
        usd, tours = Decimal(0), 0
        for p in transcripts:
            r = mod.mesure().mesurer(p)[0]
            usd, tours = usd + r["usd_exact"], tours + r["tours"]
        return float(usd.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)), tours

    def octets(chemin):
        with open(chemin, "rb") as f:
            return f.read()

    def ligne_c(**champs):
        mod.carnet.ajouter(c, nuit=JOUR_MATIN, **champs)

    sauve = {k: os.environ.get(k) for k in ("HOME", "USERPROFILE", "VLP_CARNET", "VLP_CANAL")}
    os.environ.update(HOME=h, USERPROFILE=h, VLP_CARNET=c)
    os.environ.pop("VLP_CANAL", None)
    try:
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
        assert (codes == [0, 0, 0] and sortes == [("verser ceci", "reste"), ("faire niveau", "case3"), ("oubli de sorte", None)]
                     and code_stop == 1 and s_stop.startswith("GARDE: --sorte") and len(mod.carnet.lire(c)) == 13), ("NUI19 (sorte) nuits noter --sorte : reste, case3 et sans sorte au carnet ; --sorte avec --stop → GARDE:, rien d'écrit") + "\n" + str((codes, sortes, s_stop))
        code, s = appel(["matin", d, JOUR_MATIN])
        assert (code == 0 and s.endswith("MATIN 1 fusionnée(s) · 1 de côté\n")), ("NUI19 (r) matin d'abord : la branche close fusionnée, PAR de côté") + "\n" + str((code, s))
        avant = git_matin(d, "rev-list", "--count", "HEAD")
        rapport = os.path.join(tr, "rapport-r.json")
        code1, s1 = appel(["matin", d, JOUR_MATIN, "--rapport", rapport])
        carnet1, json1 = octets(c), octets(rapport)
        nuits = mod.fichier_nuits(d)
        assert nuits
        nuits1 = octets(nuits)
        code2, s2 = appel(["matin", d, JOUR_MATIN, "--rapport", rapport])
        lignes = mod.carnet.lire(c)
        par_session = {x["session"]: x for x in lignes if mod.carnet.est_session(x)}
        u_a, t_a = somme(chemins["s-aaa-1"], sous["s-aaa-1"])
        u_r, t_r = somme(chemins["s-aaa-r"])
        u_p, t_p = somme(chemins["s-par-r"])
        assert (code1 == 0 and (par_session["s-aaa-1"]["usd_kit"], par_session["s-aaa-1"]["tours_kit"]) == (u_a, t_a)
                     and (par_session["s-aaa-r"]["usd_kit"], par_session["s-aaa-r"]["tours_kit"]) == (u_r, t_r)
                     and (par_session["s-par-r"]["usd_kit"], par_session["s-par-r"]["tours_kit"]) == (u_p, t_p)
                     and par_session["s-aaa-1"]["usd_cli"] == 7.77 and t_a == 3 and s1.startswith("KIT ? ")), ("NUI19 (a) usd_kit et tours_kit = la somme de mesurer sur la session et son sous-agent, au centime ; usd_cli gardé — "
                     "mutant : sous-agents non sommés") + "\n" + str((par_session, s1))
        assert (all(par_session[n]["usd_kit"] is None and par_session[n]["tours_kit"] is None for n in ("s-aaa-c", "s-par-1"))
                     and "KIT ? s-aaa-c — transcription introuvable\n" in s1
                     and "KIT ? s-par-1 — modèle hors grille (claude-inconnu-9)\n" in s1 and s1.count("KIT ? ") == 2), ("NUI19 (c) sans transcript, et sous-agent hors GRILLE : aucune clé _kit, une ligne KIT ? chacune, jamais 0 — "
                     "mutant : usd_exact None compté 0") + "\n" + str((par_session, s1))
        table = [l for l in octets(nuits).decode("utf-8").splitlines() if l.startswith("| " + JOUR_MATIN)]
        euros = lambda v: ("%.2f" % v).replace(".", ",")
        assert (code2 == 0 and carnet1 == octets(c) and nuits1 == octets(nuits) and json1 == octets(rapport)
                     and len(table) == 4 and "NUITS ctx/41-nuits.md · 4 ligne(s) ajoutée(s)\n" in s1
                     and "NUITS ctx/41-nuits.md · 0 ligne(s) ajoutée(s)\n" in s2
                     and "| %s | A | AAA | 1/1/0 | ≥ %s |" % (JOUR_MATIN, euros(u_a + u_r)) in table
                     and "| %s | B | PAR | 1/0/1 | ≥ %s |" % (JOUR_MATIN, euros(u_p)) in table
                     and not os.path.exists(c + ".verrou") and git_matin(d, "rev-list", "--count", "HEAD") == avant), ("NUI19 (b) --rapport rejoué : carnet, fichier des nuits et JSON identiques à l'octet, une ligne de table par chantier "
                     "(4), aucune ajoutée au rejeu, verrou absent, HEAD inchangé") + "\n" + str((code2, table, s1, s2))
        donnees = json.loads(json1.decode("utf-8"))
        choix = donnees.get("choix", [])
        titres = [q["titre"] for q in choix]
        cote =next((q for q in choix if q["titre"].startswith("Mis de côté : PAR")), {})
        reste = next((q for q in choix if q["titre"].startswith("Reste à verser")), {})
        case3 = next((q for q in choix if q["titre"].startswith("Case 3")), {})
        sans = [m for m in donnees.get("mal", []) if m["titre"] == "NOTE SANS SORTE"]
        assert ([len(q.get("options", [])) for q in (cote, reste, case3)] == [3, 3, 2]
                     and [o["valeur"] for o in cote["options"]] == ["reprendre", "abandonner", "rejouer"]
                     and [o["valeur"] for o in reste["options"]] == ["verser", "fondre", "abandonner"]
                     and len(sans) == 1 and "oubli de sorte" in sans[0]["texte"]
                     and "NOTE SANS SORTE A — oubli de sorte\n" in s1
                     and "ÉCART B-ZZZ — le carnet le met de côté, Git non" in s1 and s1.count("ÉCART ") == 1
                     and any("Chantiers sautés à cause de lui : DEP" in p for p in cote["puces"])
                     and any("la cause du refus" in p for p in cote["puces"]) and any("`git branch -D nuit/" in o["effet"] for o in cote["options"])
                     and "7,77" not in json1.decode("utf-8") and "7.77" not in json1.decode("utf-8")
                     and "push" not in json1.decode("utf-8").lower() and len(titres) == 4
                     and [t.startswith("Mis de côté : ") for t in titres].count(True) == 2 and any("ZZZ" in t for t in titres)), ("NUI19 (d) JSON : le mis de côté et le reste à trois réponses, la case 3 à deux, NOTE SANS SORTE une fois (les notes "
                     "de la boucle n'y sont pas), l'ÉCART de ZZZ dit, jamais un _cli ni un push") + "\n" + str((titres, cote, reste, case3, sans, s1))
        html = os.path.join(tr, "rapport-r.html")
        code, s = appel(["chef", "page", "--questions", "@" + rapport, "--sortie", html])
        assert (code == 0 and s.startswith("PAGE SAINE ")
                     and s.endswith("CARTES Q1 Q2 Q3 Q4\n")), ("NUI19 (d) le JSON passe `chef page` : PAGE SAINE, les cartes Q1 à Q4") + "\n" + str((code, s))
        code_h, s_h = appel(["nuits", "lecon", "hors forme", "--projet", d])
        lecon = "- %s · N=1 · cause un · jouées 3 sur 5 · nuits %s · sessions s-aaa-1" % (JOUR_MATIN, JOUR_MATIN)
        code_l, s_l = appel(["nuits", "lecon", lecon, "--projet", d])
        code_m, s_m = appel(["nuits", "lecon", lecon, "--projet", d])
        textes = octets(nuits).decode("utf-8").splitlines()
        assert (code_h == 1 and s_h.startswith("GARDE: leçon hors forme") and code_l == 0 and s_l == "LEÇON ctx/41-nuits.md · ajoutée\n"
                     and code_m == 0 and s_m == "LEÇON ctx/41-nuits.md · déjà là\n" and textes.count(lecon) == 1
                     and textes.index("## Leçons") < textes.index(lecon)), ("NUI19 (d) nuits lecon : hors forme → GARDE:, sort 1, rien d'écrit ; une leçon sous `## Leçons`, rejouée → déjà là") + "\n" + str((code_h, s_h, s_l, s_m))
        transcript(os.path.join(pr, "s-aaa-c.jsonl"), 1)     # la transcription qui manquait paraît : le chiffre de A/AAA changerait
        code3, s3 = appel(["matin", d, JOUR_MATIN, "--rapport", rapport])
        table3 = [l for l in octets(nuits).decode("utf-8").splitlines() if l.startswith("| " + JOUR_MATIN)]
        mesuree = next(x for x in mod.carnet.lire(c) if x["session"] == "s-aaa-c")
        assert (code3 == 0 and mesuree["usd_kit"] is not None and table3 == table
                     and "NUITS ctx/41-nuits.md · 0 ligne(s) ajoutée(s)\n" in s3 and "KIT ? s-aaa-c" not in s3), ("NUI19 (b) une ligne de table déjà là n'est pas refaite quand son chiffre aurait changé : toujours 4 lignes, "
                     "A/AAA inchangée, la session enfin mesurée au carnet — mutant : une ligne de table à chaque rejeu") + "\n" + str((code3, table, table3, s3))
        code_a, s_a = appel(["matin", d, "2026-10-02", "--rapport", rapport])
        assert (code_a == 1 and s_a.startswith("GARDE: carnet de la nuit 2026-10-02 absent ou vide")), ("NUI19 (r) --rapport sans carnet à cette date → GARDE:, sort 1") + "\n" + str((code_a, s_a))
    finally:
        for k, v in sauve.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v



def matin_s(tr):
    """(s) `matin` sans date : la seule nuit à ranger est prise et dite ; plusieurs nuits, ou aucune (tout fusionné, ou
    de côté), ne fusionnent rien ; `--rapport` veut la date."""
    d, wip_d, rapport = os.path.join(tr, "s"), os.path.join(tr, "swip"), os.path.join(tr, "s-rapport.json")
    depot_matin(d)
    nom = branche_matin(d, "A", "AAA", "AAA", 1)
    ancienne = "nuit/2026-09-30-A-OLD"
    git_matin(d, "branch", ancienne, nom)
    code2, s2 = appel(["matin", d])
    intacte = code_git(d, "merge-base", "--is-ancestor", nom, "main") == 1
    code_r, s_r = appel(["matin", d, "--rapport", rapport])
    git_matin(d, "branch", "-D", ancienne)
    code1, s1 = appel(["matin", d])
    code0, s0 = appel(["matin", d])
    depot_matin(wip_d)
    wip = branche_matin(wip_d, "A", "WIP", None, 1, clos=False, x="a = 1\nb = 2\nc = 30\n")
    codew, sw = appel(["matin", wip_d])
    aucune = "GARDE: aucune nuit à ranger (1 branche(s) nuit/* déjà fusionnée(s) ou de côté) — rien fusionné\n"
    assert (code2 == 1 and s2 == "GARDE: plusieurs nuits à ranger : 2026-09-30 (1), 2026-10-01 (1) — rien fusionné ; "
                 "donne la date\n" and intacte
                 and code_r == 1 and s_r.startswith("GARDE: --rapport veut la date de la nuit") and not os.path.exists(rapport)
                 and code1 == 0 and s1 == ("NUIT 2026-10-01 — la seule à ranger : 1 branche(s)\n" + ORDRE_ABSENT
                                           + "FUSIONNÉE %s\nMATIN 1 fusionnée(s) · 0 de côté\n" % nom)
                 and code_git(d, "merge-base", "--is-ancestor", nom, "main") == 0
                 and code0 == 1 and s0 == aucune and codew == 1 and sw == aucune
                 and code_git(wip_d, "merge-base", "--is-ancestor", wip, "main") == 1), ("NUI15 (s) matin sans date : deux nuits → GARDE qui les liste (la plus ancienne d'abord), rien fusionné ; "
                 "--rapport sans date → GARDE ; la seule nuit → NUIT <date> puis la fusion ; plus rien à ranger, ou une "
                 "branche de côté seule → GARDE aucune nuit, sort 1 — mutants : « plusieurs » prend la première, une "
                 "branche de côté compte comme à ranger") + "\n" + str((code2, s2, intacte, code_r, s_r, code1, s1, code0, s0, codew, sw))



def matin_t(tr):
    """(t) une fusion qui touche `scripts/` : `PLUGIN_RETARD=1` avant `MATIN` quand le projet est le kit chargé (`KIT`),
    rien pour un autre projet (RTD1)."""
    sorties = []
    for nom, est_kit in (("t-kit", True), ("t-autre", False)):
        d = os.path.join(tr, nom)
        depot_matin(d)
        branche = branche_matin(d, "A", "RTD", "RTD", 1, x="a = 1\nb = 2\nc = 31\n")
        garde, mod.KIT = mod.KIT, (d if est_kit else tr)
        try:
            sorties.append(appel(["matin", d, JOUR_MATIN]) + (branche,))
        finally:
            mod.KIT = garde
    (code_k, s_k, b_k), (code_a, s_a, _) = sorties
    retard = "PLUGIN_RETARD=1 commit(s) de code du plugin fusionné(s) — la session ouverte ne les voit qu'après /reload-plugins\n"
    assert (code_k == 0 and s_k.endswith(retard + "MATIN 1 fusionnée(s) · 0 de côté\n") and "FUSIONNÉE %s" % b_k in s_k
                 and code_a == 0 and "PLUGIN_RETARD" not in s_a), ("RTD1 (t) matin dit PLUGIN_RETARD= quand ses fusions touchent le code du kit chargé, rien pour un autre "
                 "projet — mutant : la condition « projet est KIT » forcée à faux") + "\n" + str(sorties)



def matin_u(tr):
    """(u) une branche qui laisse une page en attente : `matin` imprime son `ATTENTE=` avant `MATIN` (NPB1)."""
    d = os.path.join(tr, "u")
    depot_matin(d)
    attente = "50-x.html\thttps://claude.ai/artifact/x\t2026-10-01T01:00+02:00\n"
    branche_matin(d, "A", "NPB", "NPB", 1, modifs=lambda r: ecrire(os.path.join(r, "ctx", "artefacts", "en-attente"),
                                                                    attente))
    code, s = appel(["matin", d, JOUR_MATIN])
    assert (code == 0 and s.endswith("ATTENTE=50-x.html https://claude.ai/artifact/x\nMATIN 1 fusionnée(s) · 0 de côté\n")), ("NPB1 (b) matin imprime l'ATTENTE= qu'une branche de la nuit a laissée, avant MATIN — mutant : "
                 "l'appel à dire_attentes retiré") + "\n" + str((code, s))



def test_matin_a(tmp_path):
    matin_a(str(tmp_path))


def test_matin_b(tmp_path):
    matin_b(str(tmp_path))


def test_matin_c(tmp_path):
    matin_c(str(tmp_path))


def test_matin_d(tmp_path):
    matin_d(str(tmp_path))


def test_matin_e(tmp_path):
    matin_e(str(tmp_path))


def test_matin_h(tmp_path):
    matin_h(str(tmp_path))


def test_matin_g(tmp_path):
    matin_g(str(tmp_path))


def test_matin_n_a(tmp_path):
    matin_n_a(str(tmp_path))


def test_matin_n_b(tmp_path):
    matin_n_b(str(tmp_path))


def test_matin_n_c(tmp_path):
    matin_n_c(str(tmp_path))


def test_matin_n_d(tmp_path):
    matin_n_d(str(tmp_path))


def test_matin_n_e(tmp_path):
    matin_n_e(str(tmp_path))


def test_matin_n_f(tmp_path):
    matin_n_f(str(tmp_path))


def test_matin_r(tmp_path):
    matin_r(str(tmp_path))


def test_matin_s(tmp_path):
    matin_s(str(tmp_path))


def test_matin_t(tmp_path):
    matin_t(str(tmp_path))


def test_matin_u(tmp_path):
    matin_u(str(tmp_path))
