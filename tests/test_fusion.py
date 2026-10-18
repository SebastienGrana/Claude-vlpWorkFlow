"""`noyau/matin.py`, la fusion d'une fiche jouée en worktree (`fusionner`), le travail mis de côté, les lettres en
double — migré de l'ancienne suite maison (REF51). Chaque `assert` garde le libellé d'origine de son `verifier` en tête
de son message (REF5), puis le diagnostic.
"""
import os
import re
import shutil
import subprocess
import tempfile

import pytest
from aides import SCRIPTS, appel, ecrire, ligne_close, lire, mod

ICI = SCRIPTS     # le dossier des scripts, d'où ces tests viennent

OUVERT = "**Ouvert.** le 2026-10-08."


def ouvert(texte):
    """`texte` d'un fichier de fiches, la marque d'ouverture sous son titre `# Chantier `, comme la pose `vlp.py
    ouvrir` : `courant_de` le lit (NUI31)."""
    return re.sub(r"^(# Chantier [^\n]*\n)", r"\g<1>\n%s\n" % OUVERT, texte, count=1, flags=re.M)


OUVERT_LIGNE = mod.OUVERT_LIGNE   # la seconde valeur d'`OUVERT` dans l'ancienne suite maison, lue par les groupes de sa fin


def ouvert_ligne(texte):
    """`ouvert`, tel que les groupes de la fin de l'ancienne suite maison l'appelaient : le gabarit `OUVERT_LIGNE` inséré
    brut, `%s` compris."""
    return re.sub(r"^(# Chantier [^\n]*\n)", r"\g<1>\n%s\n" % OUVERT_LIGNE, texte, count=1, flags=re.M)


OUVERT_DU_JOUR = mod.OUVERT_LIGNE % __import__("datetime").date.today().isoformat()


GABARIT_FEUILLE = os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html")


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


def depot_matin(init_git, d, archive=True, etat=ETAT_MATIN):
    """Le dépôt de 2cef70f : `main` à courant LOC et son artefact, des lettres jusqu'à ENQ, une archive de deux clos
    (`archive` faux : ils restent sur la feuille), la feuille au rang 79 — un seul commit, à l'heure 0."""
    os.makedirs(d)
    init_git(d)
    ecrire(os.path.join(d, "CHANTIER.md"), CARTE_MATIN)
    ecrire(os.path.join(d, "ctx", "08-etat.md"), etat)
    ecrire(os.path.join(d, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n")
    ecrire(os.path.join(d, "ctx", "40-loc.md"), ouvert_ligne("# Chantier LOC — Publier\n\n## LOC1 [ ] — a\n"))
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


def test_wip_de_cote(tmp_path, init_git):
    """NUI24 : une pointe WIP sans chantier n'est jamais fusionnée ; une branche qui hérite du chantier ouvert de main
    sans en ajouter reste fusionnable."""
    if not shutil.which("git"):
        pytest.skip("git absent — la pointe WIP n'est pas testée")
        return
    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
        d = os.path.join(tr, "w")
        depot_matin(init_git, d)
        noms = {}
        for canal, code, sujet in (("A", "WIP", mod.WIP_SUJET % ("WIP", "découpage coupé")), ("B", "HER", "HER1 : her")):
            noms[code] = "nuit/%s-%s-%s" % (JOUR_MATIN, canal, code)
            git_matin(d, "switch", "-q", "-c", noms[code], "main")
            ecrire(os.path.join(d, "scripts", "%s.py" % code.lower()), "x = 1\n")
            commit_matin(d, sujet, 1)
            git_matin(d, "switch", "-q", "main")
        etat_wip, etat_her = mod.etat_branche_nuit(d, noms["WIP"]), mod.etat_branche_nuit(d, noms["HER"])
        code, s = appel(["matin", d, JOUR_MATIN])
        wip_fusionne = code_git(d, "merge-base", "--is-ancestor", noms["WIP"], "main") == 0
    assert (etat_wip == ("cote", "WIP WIP mis de côté : découpage coupé") and etat_her == ("fusion", None)
             and "DE CÔTÉ %s — WIP WIP mis de côté : découpage coupé\n" % noms["WIP"] in s and not wip_fusionne), ("NUI24 : pointe WIP, chantier aucun → DE CÔTÉ, jamais fusionnée ; héritière de LOC ouvert → fusionnable — "
             "mutant : la pointe WIP n'est plus lue") + "\n" + str(repr((etat_wip, etat_her, wip_fusionne)) + "\n" + s)


def test_fusionner(tmp_path, init_git):
    """NUI26 : `vlp.py fusionner <projet> <branche>`, la fusion du jour par le chemin de `matin` — un worktree qui clôt
    le chantier de main le libère ; un worktree qui ouvre puis clôt PAR laisse à main le sien ; six refus et `DÉJÀ`."""
    if not shutil.which("git"):
        pytest.skip("git absent — fusionner n'est pas testé")
        return
    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
        d, wt = os.path.join(tr, "f"), os.path.join(tr, "wt-clot")
        depot_matin(init_git, d)
        git_matin(d, "worktree", "add", "-q", "-b", "clot-loc", wt, "main")
        postit = mod.postit(wt)
        assert postit
        ecrire(postit, "ctx/40-loc.md\n")       # le worktree reprend le chantier de main : son post-it le nomme
        etat_wt = os.path.join(wt, "ctx", "08-etat.md")    # la clôture ôte sa ligne de la TODO (cloture.md, étape 1)
        ecrire(etat_wt, "".join(l for l in lire(etat_wt).splitlines(True) if not l.startswith("| 79 |")))
        code_clore, s_clore = appel(["clore", wt, "--livre", "LOC livré", "--date", JOUR_MATIN])
        commit_matin(wt, "Chantier LOC clos", 1)
        code, s = appel(["fusionner", d, "clot-loc"])
        carte_, courant_a = mod.lignes_de(os.path.join(d, "CHANTIER.md")), mod.courant_de(d)
        ecrire(os.path.join(d, "ctx", "50-neo.md"), "# Chantier NEO — Neuf\n\n## NEO1 [ ] — a\n")
        code_ouvrir, s_ouvrir = appel(["ouvrir", d, "--fiches", "ctx/50-neo.md", "--titre", "Neuf"])
        neo = lire(os.path.join(d, "ctx", "50-neo.md"))
    assert (code_clore == 0 and ('FUSIONNER depuis %s : ' % d.replace("\\", "/")) in s_clore.replace("\\", "/")
             and ' fusionner "' in s_clore and s_clore.rstrip().endswith(" clot-loc")
             and code == 0 and s == "FUSIONNÉE clot-loc\n"
             and courant_a is None and mod.champ(carte_, "artefact du chantier") == "aucun"
             and code_ouvrir == 0 and "**Ouvert.**" in neo), ("NUI26 (a) un worktree clôt LOC, le chantier de main : clore dit la ligne FUSIONNER ; fusionner depuis main "
             "→ FUSIONNÉE, commit « Fusion : clot-loc », main à aucun (courant et artefact) ; ouvrir passe ensuite ; "
             "la ligne 79 ôtée de la TODO par la clôture ne fait plus s'arrêter la feuille (dette NUI, 2026-10-08) — "
             "mutant : l'exception **CLOS** retirée") + "\n" + str((code_clore, s_clore, code, s, carte_, code_ouvrir, s_ouvrir))

    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
        d, vide = os.path.join(tr, "g"), os.path.join(tr, "vide")
        depot_matin(init_git, d)
        os.makedirs(vide)

        def branche(nom, fichier, corps, carte_aucun):
            """`nom`, depuis main, dans un worktree : `fichier` écrit avec `corps` ; `carte_aucun` : CHANTIER.md à
            `aucun` et la lettre PAR ajoutée, comme `clore` l'écrit."""
            w = os.path.join(tr, "wt-" + nom)
            git_matin(d, "worktree", "add", "-q", "-b", nom, w, "main")
            ecrire(os.path.join(w, fichier), corps)
            if carte_aucun:
                chemin = os.path.join(w, "CHANTIER.md")
                c = re.sub(r"(\*\*artefact du chantier\*\* : ).*", r"\g<1>aucun", lire(chemin))
                ecrire(chemin, c.replace(". Un nouveau chantier", ", PAR (Deux chantiers). Un nouveau chantier"))
            commit_matin(w, nom, 2)

        branche("par", "ctx/60-par.md", "# Chantier PAR — Deux\n\n%s\n\n**CLOS** le %s.\n\n## PAR1 [x] — a\n"
                % (OUVERT_DU_JOUR, JOUR_MATIN), True)
        branche("ouvre", "ctx/70-ouv.md", "# Chantier OUV — Ouvert\n\n%s\n\n## OUV1 [ ] — a\n" % OUVERT_DU_JOUR, False)
        refus = [appel(["fusionner", vide, "par"])]
        ecrire(os.path.join(d, "sous", "CHANTIER.md"), "# C\n")
        refus.append(appel(["fusionner", os.path.join(d, "sous"), "par"]))
        shutil.rmtree(os.path.join(d, "sous"))
        git_matin(d, "switch", "-q", "--detach")
        refus.append(appel(["fusionner", d, "par"]))
        git_matin(d, "switch", "-q", "main")
        git_matin(d, "merge", "-q", "--no-ff", "--no-commit", "ouvre")
        refus.append(appel(["fusionner", d, "par"]))
        git_matin(d, "merge", "--abort")
        ecrire(os.path.join(d, "scripts", "x.py"), "sale\n")
        refus.append(appel(["fusionner", d, "par"]))
        git_matin(d, "checkout", "-q", "--", ".")
        refus.append(appel(["fusionner", d, "nulle-part"]))
        refus.append(appel(["fusionner", d, "ouvre"]))
        ouvre_fusionne = code_git(d, "merge-base", "--is-ancestor", "ouvre", "main") == 0
        code, s = appel(["fusionner", d, "par"])
        carte_, courant_c = mod.lignes_de(os.path.join(d, "CHANTIER.md")), mod.courant_de(d)
        sujet = git_matin(d, "log", "-1", "--format=%s").strip()
        deja = appel(["fusionner", d, "par"])
    attendu = ("GARDE: pas de CHANTIER.md dans", "n'est pas la racine d'un dépôt Git", "GARDE: HEAD détachée",
               "GARDE: une fusion est déjà en cours (MERGE_HEAD)", "GARDE: arbre pas propre (1 chemin(s))",
               "GARDE: branche absente : nulle-part", "GARDE: ouvre garde un chantier ouvert (ctx/70-ouv.md) — clos-le")
    assert (len(refus) == len(attendu) and all(c == 1 and a in r and "rien fusionné" in r for (c, r), a in zip(refus, attendu))
             and not ouvre_fusionne), ("NUI26 (b) six refus, un cas chacun (non équipé, hors racine, HEAD détachée, MERGE_HEAD, arbre sale, branche "
             "absente) et la branche qui garde un chantier ouvert — sort 1, rien fusionné") + "\n" + str(refus)
    assert (code == 0 and s == "FUSIONNÉE par\n" and sujet == "Fusion : par"
             and courant_c == "ctx/40-loc.md"
             and mod.champ(carte_, "artefact du chantier") == "https://claude.ai/artifact/LOC"
             and mod.lettres_prises(carte_) == ["E", "ENQ", "PAR"] and deja == (0, "DÉJÀ par\n")), ("NUI26 (c) un worktree ouvre puis clôt PAR : fusionner → main garde LOC (courant et artefact), PAR ajouté aux "
             "lettres, commit « Fusion : par » ; rejoué → DÉJÀ par, sort 0") + "\n" + str((code, s, sujet, carte_, deja))


def noms_worktrees(d):
    """Les noms de dossier des worktrees du dépôt de `d`, le principal en tête (ISO4)."""
    return [os.path.basename(l[len("worktree "):].rstrip("/")) for l in git_matin(d, "worktree", "list", "--porcelain")
            .splitlines() if l.startswith("worktree ")]


def test_iso4_fusionner_fiche(tmp_path, init_git):
    """ISO4 : `fusionner <fichier> <fiche> --worktree <dossier>` sur un dépôt et deux worktrees — sans conflit,
    `FUSIONNÉ`, le fichier dans main, plus de worktree ni de branche ; même ligne changée des deux côtés, `CONFLIT`,
    sort 1, `git status` propre ; un dossier hors des worktrees, ou sans commit de la fiche : `GARDE:`, rien touché."""
    if not shutil.which("git"):
        pytest.skip("git absent — fusionner --worktree n'est pas testé")
        return
    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
        d, wa, wc = (os.path.join(tr, n) for n in ("d", "wt-a", "wt-c"))
        os.makedirs(d)
        init_git(d)
        fiches = os.path.join(d, "ctx", "f.md")
        ecrire(fiches, "# F\n\n## W1 [ ] — a\n\n## W2 [ ] — c\n")
        ecrire(os.path.join(d, "a.txt"), "1\n2\n3\n")
        commit_matin(d, "départ", 1)
        for nom, w in (("a", wa), ("c", wc)):
            git_matin(d, "worktree", "add", "-q", "-b", nom, w, "main")
        gardes = [appel(["fusionner", fiches, "W1", "--worktree", w]) for w in (wa, tr)]   # W1 pas encore commitée
        intact = noms_worktrees(d) == ["d", "wt-a", "wt-c"] and git_matin(d, "status", "--porcelain") == ""
        ecrire(os.path.join(wa, "b.txt"), "b\n")
        commit_matin(wa, "W1 : a", 2)
        ecrire(os.path.join(wc, "a.txt"), "1\nc\n3\n")
        commit_matin(wc, "W2 : c", 3)
        ecrire(os.path.join(d, "a.txt"), "1\nm\n3\n")
        commit_matin(d, "main change la ligne 2", 4)
        fus = appel(["fusionner", fiches, "W1", "--worktree", wa])
        apres_fus = (os.path.isfile(os.path.join(d, "b.txt")), noms_worktrees(d))
        conf = appel(["fusionner", fiches, "W2", "--worktree", wc])
        apres_conf = (git_matin(d, "status", "--porcelain"), code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD"),
                      lire(os.path.join(d, "a.txt")).replace("\r\n", "\n"), noms_worktrees(d),
                      git_matin(d, "branch", "--format=%(refname:short)").split())
    assert (fus[0] == 0 and re.fullmatch(r"FUSIONNÉ W1 [0-9a-f]{7,}\n", fus[1]) is not None
             and apres_fus == (True, ["d", "wt-c"])), ("ISO4 : sans conflit → FUSIONNÉ W1 <sha>, sort 0, b.txt dans main, le worktree wt-a retiré") + "\n" + str((fus, apres_fus))
    assert (conf == (1, "CONFLIT W2 a.txt\n") and apres_conf == ("", 1, "1\nm\n3\n", ["d"], ["main"])), ("ISO4 : même ligne changée des deux côtés → CONFLIT W2 a.txt, sort 1, git status propre, pas de "
             "MERGE_HEAD, la ligne de main gardée, plus de worktree ni de branche a ou c — mutant : pas d'abort") + "\n" + str((conf, apres_conf))
    assert ([c for c, _ in gardes] == [1, 1] and gardes[0][1].startswith("GARDE: aucun commit « W1 : »")
             and "n'est pas un autre worktree" in gardes[1][1] and intact), ("ISO4 : sans commit « W1 : » dans le worktree, ou un dossier hors des worktrees → GARDE:, sort 1, rien "
             "touché") + "\n" + str((gardes, intact))


def test_lettres_doublon(tmp_path, init_git):
    """NUI27 : un code pris deux fois n'est plus avalé — à la fusion, même lettre et titres différents → `GARDE:` avant
    toute écriture, même entrée → rien ; `ouvrir` refuse un code déjà ouvert dans un autre worktree, pas le sien hérité."""
    if not shutil.which("git"):
        pytest.skip("git absent — les lettres en double ne sont pas testées")
        return
    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
        d = os.path.join(tr, "l")
        depot_matin(init_git, d)

        def lettre(nom, entree):
            """`nom`, depuis main, dans un worktree : `entree` ajoutée à la liste des lettres et CHANTIER.md à `aucun`,
            comme `clore` l'écrit — sinon la branche garde LOC ouvert et `fusionner` la met de côté —, puis commitée."""
            w = os.path.join(tr, "wt-" + nom)
            git_matin(d, "worktree", "add", "-q", "-b", nom, w, "main")
            chemin = os.path.join(w, "CHANTIER.md")
            c = re.sub(r"(\*\*artefact du chantier\*\* : ).*", r"\g<1>aucun", lire(chemin))
            ecrire(chemin, c.replace(". Un nouveau chantier", ", %s. Un nouveau chantier" % entree))
            commit_matin(w, nom, 3)

        lettre("pa", "PAR (A)")
        lettre("pb", "PAR (B)")
        lettre("pc", "`PAR` (A)")
        code_a, s_a = appel(["fusionner", d, "pa"])
        tete = git_matin(d, "rev-parse", "HEAD")
        code_b, s_b = appel(["fusionner", d, "pb"])
        propre = git_matin(d, "status", "--porcelain") == "" and git_matin(d, "rev-parse", "HEAD") == tete
        en_cours = code_git(d, "rev-parse", "-q", "--verify", "MERGE_HEAD") == 0
        code_c, s_c = appel(["fusionner", d, "pc"])
        lettres = mod.lettres_prises(mod.lignes_de(os.path.join(d, "CHANTIER.md")))
    assert ((code_a, s_a) == (0, "FUSIONNÉE pa\n") and code_b == 1
             and s_b.startswith("GARDE: le code PAR est pris deux fois : « A » et « B »") and propre and not en_cours), ("NUI27 (a) PAR (A) fusionné, puis PAR (B) → GARDE: le code PAR est pris deux fois, sort 1, rien écrit "
             "(status vide, HEAD immobile, pas de MERGE_HEAD) — mutant : le saut silencieux remis") + "\n" + str((code_a, s_a, code_b, s_b, propre, en_cours))
    assert ((code_c, s_c) == (0, "FUSIONNÉE pc\n") and lettres == ["E", "ENQ", "PAR"]), ("NUI27 (b) la même entrée des deux côtés, aux backticks près → fusion sans garde, PAR compté une fois") + "\n" + str((code_c, s_c, lettres))

    with tempfile.TemporaryDirectory(dir=tmp_path) as tr:
        d, wz, wh = os.path.join(tr, "o"), os.path.join(tr, "wt-zed"), os.path.join(tr, "wt-her")
        depot_matin(init_git, d)
        loc = os.path.join(d, "ctx", "40-loc.md")      # main libre : LOC sans sa marque, l'artefact à aucun
        ecrire(loc, lire(loc).replace("\n%s\n" % OUVERT_LIGNE, ""))
        carte = os.path.join(d, "CHANTIER.md")
        ecrire(carte, re.sub(r"(\*\*artefact du chantier\*\* : ).*", r"\g<1>aucun", lire(carte)))
        commit_matin(d, "main libre", 3)
        git_matin(d, "worktree", "add", "-q", "-b", "zed", wz, "main")
        ecrire(os.path.join(wz, "ctx", "80-zed.md"), "# Chantier ZED — Un\n\n%s\n\n## ZED1 [ ] — a\n" % OUVERT_DU_JOUR)
        bis = os.path.join(d, "ctx", "81-zed.md")
        ecrire(bis, "# Chantier ZED — Bis\n\n## ZED1 [ ] — a\n")
        carte_avant = lire(os.path.join(d, "CHANTIER.md"))
        code_z, s_z = appel(["ouvrir", d, "--fiches", "ctx/81-zed.md", "--titre", "Bis"])
        intact = lire(os.path.join(d, "CHANTIER.md")) == carte_avant and "**Ouvert.**" not in lire(bis)
        os.remove(bis)
        ecrire(os.path.join(d, "ctx", "82-her.md"), "# Chantier HER — Hérité\n\n%s\n\n## HER1 [ ] — a\n" % OUVERT_DU_JOUR)
        commit_matin(d, "HER ouvert", 4)
        git_matin(d, "worktree", "add", "-q", "--detach", wh, "main")
        code_h, s_h = appel(["ouvrir", d, "--fiches", "ctx/82-her.md", "--titre", "Hérité"])
    assert (code_z == 1 and s_z.startswith("GARDE: le code ZED est déjà ouvert ailleurs : ctx/80-zed.md dans ")
             and "wt-zed" in s_z and intact and code_h == 0), ("NUI27 (c) ouvrir ZED quand un autre worktree a ZED ouvert → GARDE: déjà ouvert ailleurs, sort 1, rien écrit ; "
             "le même fichier hérité par un worktree détaché ne bloque pas sa réouverture") + "\n" + str((code_z, s_z, intact, code_h, s_h))
