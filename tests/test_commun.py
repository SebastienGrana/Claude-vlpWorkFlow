"""Les aides communes du noyau (noyau/commun.py) vues par leurs commandes : `archiver`, le chemin de l'archive
(`IDX1`), `premier_lancement` et le tampon des hooks, les copies du lecteur et des nombres recopiés, la règle de
`rapide` dans les agents, l'option `explique` de `chef page` — migré de l'ancienne suite maison (REF50). Chaque
`assert` garde le libellé d'origine de son `verifier` en tête de son message (REF5), puis le diagnostic.
"""
import io
import json
import os
import re
import shutil
import tempfile

from aides import SCRIPTS, appel, ecrire, ligne_close, mod

ICI = SCRIPTS     # le dossier des scripts, d'où ces tests viennent

def test_archiver(tmp_path):
    with tempfile.TemporaryDirectory(dir=tmp_path) as ta:
        def lu(c):
            with open(c, encoding="utf-8", newline="") as fh:
                return fh.read()
        def pose(c, x):
            os.makedirs(os.path.dirname(c), exist_ok=True)
            with open(c, "w", encoding="utf-8", newline="") as fh:
                fh.write(x)
        pose(os.path.join(ta, "CHANTIER.md"), "# C\n\n- **index** : ctx/00-INDEX.md\n")
        clos_a = "| `41-b.md` | on relit le socle du chantier B — **clos** « Bé  (deux blancs) », `B1..B2` |"
        clos_b = "| `39-a.md` | on relit le socle du chantier A — **clos** « A », `A1..A3` |"
        ouvert = "| `42-c.md` | on joue une fiche `C*` — chantier **ouvert** « C », `C1..C2` |"
        pose(os.path.join(ta, "ctx", "00-INDEX.md"), "# I\n\n| Fichier | Lire quand |\n|---|---|\n| `08-etat.md` | on reprend |\n%s\n%s\n%s\n" % (clos_a, clos_b, ouvert))
        code, s = appel(["archiver", ta])
        idx_a, arch_a = lu(os.path.join(ta, "ctx", "00-INDEX.md")), lu(os.path.join(ta, "ctx", "00-INDEX-archive.md"))
        assert (code == 0 and s.startswith("ARCHIVÉ 2 · index 7 lignes · archive 8 lignes")
                 and ouvert in idx_a and "**clos**" not in idx_a and idx_a.count("| `00-INDEX-archive.md` |") == 1), ("archiver : 2 clos déplacés, l'ouvert reste") + "\n" + str(s + idx_a)
        assert (arch_a.endswith("|---|---|\n%s\n%s\n" % (clos_b, clos_a)) and arch_a.startswith("# ") and "QUAND LIRE" in arch_a), ("archiver : lignes identiques à l'octet, triées par numéro — mutant : réécrire la ligne") + "\n" + str(arch_a)
        code, s = appel(["archiver", ta])
        assert (code == 0 and s.startswith("ARCHIVÉ 0 ·") and lu(os.path.join(ta, "ctx", "00-INDEX.md")) == idx_a
                 and lu(os.path.join(ta, "ctx", "00-INDEX-archive.md")) == arch_a), ("archiver : relancé, rien ne change — mutant : renvoi posé deux fois") + "\n" + str(s)
        pose(os.path.join(ta, "CHANTIER.md"), "# C\n")
        code, s = appel(["archiver", ta])
        assert (code == 1 and s.startswith("GARDE:")), ("archiver : pas de champ index, garde") + "\n" + str(s)


GABARIT_FEUILLE = os.path.join(ICI, "..", "templates", "artefact-feuille-de-route.html")


ETAT_NIV = ("# État\n\n"
            "Le plugin pose `${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py` — prose, pas un chemin lu.\n\n"
            "## TODO\n\n| # | Chantier | Ce qu'il apporte | Coût estimé | Dépend de |\n"
            "|---|---|---|---|---|\n| 1 | un truc | utile | bas | — |\n")


GABARIT_VLPCSS = os.path.join(ICI, "..", "templates", "vlp.css")


def feuille_ancienne():
    css = "".join(l for l in io.open(GABARIT_VLPCSS, encoding="utf-8").read().splitlines(True)
                  if not l.lstrip().startswith(("details.clos", ".resume-clos")))
    gabarit = io.open(GABARIT_FEUILLE, encoding="utf-8").read()
    gabarit = gabarit.replace('<link rel="stylesheet" href="vlp.css">', "<style>\n%s</style>" % css)
    lignes = gabarit.splitlines(True)
    return "".join(l for l in lignes
                   if not l.lstrip().startswith(("<details class=\"clos\">",
                                                 "<summary><span class=\"resume-clos\">", "</details>")))


CARTE_NIV3 = """# Chantier courant

- **alias** : niv3
- **contexte** : ctx/
- **index** : ctx/00-INDEX.md
- **fichier d'état** : ctx/08-etat.md

## Chantiers clos — ne se rejouent pas

| Fichier de fiches | Fiches | Clos le |
|---|---|---|
| ctx/10-a.md | `A1`..`A2` | 2026-01-01 |

Lettres de fiche déjà prises : A. Un nouveau chantier en choisit une autre.
"""


INDEX_NIV3 = ("# Index\n\n| Fichier | On l'ouvre quand |\n|---|---|\n"
              "| `10-a.md` | on relit le chantier A |\n"
              "| `99-fantome.md` | jamais, il n'existe pas |\n")


def bac_niv3(t, feuille=True, index=INDEX_NIV3):
    proj = os.path.join(t, "niv3")
    ecrire(os.path.join(proj, "CHANTIER.md"), CARTE_NIV3)
    ecrire(os.path.join(proj, "ctx", "00-INDEX.md"), index)
    ecrire(os.path.join(proj, "ctx", "08-etat.md"), ETAT_NIV)
    ecrire(os.path.join(proj, "ctx", "10-a.md"), "# Chantier A\n")
    if feuille:
        ecrire(os.path.join(proj, "ctx", "artefacts", "feuille-de-route.html"), feuille_ancienne())
    return proj


def test_idx1(tmp_path):
    assert (mod.chemin_archive("ctx/00-INDEX.md") == "ctx/00-INDEX-archive.md"
             and mod.chemin_archive("00-INDEX.md") == "00-INDEX-archive.md"), ("IDX1 : l'archive se dérive de l'index, dans son dossier") + "\n" + str(mod.chemin_archive("ctx/00-INDEX.md"))
    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        rc = os.path.join(t, "rc")
        ecrire(os.path.join(rc, "CHANTIER.md"), "# Chantier courant\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n")
        ecrire(os.path.join(rc, "ctx", "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n| `08-etat.md` | on reprend |\n")
        ecrire(os.path.join(rc, "ctx", "00-INDEX-archive.md"),
               "| Fichier | Lire quand |\n|---|---|\n| `n.md` | chantier **clos** « N », `N1..N1` |\n")
        ecrire(os.path.join(rc, "ctx", "n.md"), "# Chantier N\n\n**CLOS** le 2026-01-06.\n\n## Le socle commun\n\n"
               "<!-- FICHE:N1 -->\n## N1 [x] — Seule\n**Critère de fin**\n<!-- /FICHE -->\n")
        ecrire(os.path.join(rc, "ctx", "artefacts", "feuille-de-route.html"),
               '    <!-- ZONE:clos — test -->\n      <table>\n        <tbody>\n'
               + ligne_close(mod.arrondi(999)).replace("Q1–Q2", "N1") + "        </tbody>\n      </table>\n")
        code, s = appel(["recompter", rc])
        assert (code == 0 and s.splitlines()[0] == "N inscrit 999 · recompté gardé · écart +0 · gardé — sans session"), ("IDX1 : recompter trouve le fichier par l'archive — mutant : ne lire que l'index") + "\n" + str(s)

    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        proj = bac_niv3(t, index="# Index\n\n| Fichier | On l'ouvre quand |\n|---|---|\n| `08-etat.md` | on reprend |\n")
        ecrire(os.path.join(proj, "ctx", "00-INDEX-archive.md"),
               "| Fichier | Lire quand |\n|---|---|\n| `10-a.md` | chantier **clos** « A », `A1..A2` |\n")
        code, s = appel(["niveau", proj, "--ecrire", "--date", "2026-09-18"])
        assert ("CORRIGÉ: clos: table des chantiers clos retirée de CHANTIER.md:8" in s
                 and "| ctx/10-a.md |" not in io.open(os.path.join(proj, "CHANTIER.md"), encoding="utf-8").read()), ("IDX1 : niveau retire la table des clos que l'archive nomme — mutant : ne lire que l'index") + "\n" + str(s)

    with tempfile.TemporaryDirectory(dir=tmp_path) as t:
        ecrire(os.path.join(t, "CHANTIER.md"), "- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n")
        ecrire(os.path.join(t, "ctx", "01-a.md"), "a\n")
        ecrire(os.path.join(t, "ctx", "00-INDEX.md"), "| Fichier | Lire |\n|---|---|\n| `01-a.md` | on lit |\n")
        ecrire(os.path.join(t, "ctx", "00-INDEX-archive.md"),
               "| Fichier | Lire quand |\n|---|---|\n| `20-mort.md` | chantier **clos** « M », `M1..M1` |\n")
        code, s = appel(["renvois", t])
        assert (code == 1 and s == "ABSENT: ctx/00-INDEX-archive.md:3: 20-mort.md\n"
                 "POIDS CLAUDE.md absent/80 · CHANTIER.md 2/50 · index 3/80\nRENVOIS 2 nommés · 1 absents\n"), ("IDX1 : renvois lit l'archive, sans poids — mutant : archive non lue") + "\n" + str(s)


def gardien_test(texte):
    """Appelle vlp.py gardien avec l'entrée JSON."""
    o, e = io.StringIO(), io.StringIO()
    code = mod.main(["gardien"], o, io.StringIO(texte), e)
    return code, o.getvalue(), e.getvalue()


def test_premier_lancement():
    # Sauvegarder et restaurer TAMPON_HOOKS pour ce test
    ancien_tampon = mod.etat.TAMPON_HOOKS
    mod.etat.TAMPON_HOOKS = tempfile.mkdtemp()     # neuf : un tampon d'un run d'avant ferait taire le 1er appel

    try:
        # Entrée PreToolUse qui essaie de commiter
        entree_commit = json.dumps({
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "git commit -m 'test'"},
            "agent_type": "vlp:fiche"
        })

        # Entrée différente (PowerShell au lieu de Bash)
        entree_commit_ps = json.dumps({
            "hook_event_name": "PreToolUse",
            "tool_name": "PowerShell",
            "tool_input": {"command": "git commit -m 'test ps'"},
            "agent_type": "vlp:fiche"
        })

        # Premier appel : doit refuser (écrit en JSON)
        code1, out1, err1 = gardien_test(entree_commit)
        assert (code1 == 0 and "permissionDecision" in out1 and "deny" in out1 and err1 == ""), ("gardien : premier lancement, refuse le git commit") + "\n" + str(out1 + err1)

        # Deuxième appel avec la même entrée : doit être muet (retourne 0 sans rien écrire)
        code2, out2, err2 = gardien_test(entree_commit)
        assert (code2 == 0 and out2 == "" and err2 == ""), ("gardien : deuxième lancement de la même entrée, muet") + "\n" + str("out=%s err=%s" % (out2, err2))

        # Troisième appel avec une entrée différente : doit refuser (écrit en JSON)
        code3, out3, err3 = gardien_test(entree_commit_ps)
        assert (code3 == 0 and "permissionDecision" in out3 and "deny" in out3 and err3 == ""), ("gardien : entrée différente, refuse le git commit") + "\n" + str(out3 + err3)
        # PYT2 : sur une écriture, `filet` et `hook` reçoivent la même entrée — chacun agit une fois
        assert (mod.premier_lancement("{}", "cmd_filet") and mod.premier_lancement("{}", "cmd_hook")
                 and not mod.premier_lancement("{}", "cmd_hook")), ("premier_lancement : même entrée, deux sous-commandes, chacune une fois")
        # SON : VLP_SANS_TAMPON saute le tampon — la même entrée rejouée agit à chaque fois
        os.environ["VLP_SANS_TAMPON"] = "1"
        try:
            rejeux = [gardien_test(entree_commit)[1] for _ in range(2)]
        finally:
            del os.environ["VLP_SANS_TAMPON"]
        assert (all("deny" in r for r in rejeux)), ("SON : VLP_SANS_TAMPON, la même entrée rejouée deux fois refuse deux fois") + "\n" + str(repr(rejeux))
        assert (gardien_test(entree_commit)[1] == ""), ("SON : sans VLP_SANS_TAMPON, le tampon reprend (muet)")
    finally:
        # Restaurer TAMPON_HOOKS à None pour les tests suivants
        shutil.rmtree(mod.etat.TAMPON_HOOKS, ignore_errors=True)
        mod.etat.TAMPON_HOOKS = ancien_tampon


def test_lecteur_copie():
    """LEC : le lecteur à voix haute vit en deux copies — vlp.js et vlp.css pour les pages du kit, le gabarit des
    rapports pour les siens ; entre leurs repères LECTEUR, les deux restent pareilles à l'octet (2026-10-06). Les
    nombres insécables aussi, entre leurs repères INSECABLE (2026-10-07)."""
    def entre(nom, debut, fin):
        t = mod.lire(os.path.join(ICI, "..", "templates", nom))
        i = t.find(debut)
        j = t.find(fin, i) if i >= 0 else -1
        return t[i:j + len(fin)] if j >= 0 else None

    rapport = "rapport-choix.html"
    for genre, nom, debut, fin in (("script du lecteur", "vlp.js", "// LECTEUR — début", "// LECTEUR — fin"),
                                   ("style du lecteur", "vlp.css", "/* LECTEUR — début", "/* LECTEUR — fin */"),
                                   ("script des nombres insécables", "vlp.js", "// INSECABLE — début",
                                    "// INSECABLE — fin")):
        kit, copie = entre(nom, debut, fin), entre(rapport, debut, fin)
        assert (kit is not None and kit == copie), ("LEC : le %s, dans %s et %s, pareil à l'octet" % (genre, nom, rapport)) + "\n" + str("%s : %s ; %s : %s" % (
                     nom, "absent" if kit is None else "%d car." % len(kit),
                     rapport, "absent" if copie is None else "%d car." % len(copie)))


NOMBRES_RECOPIES = (
    ("tentatives avant BLOQUÉE",
     ("methode-chantier.md", r"s'arrête à (\w+) tentatives"),
     (("skills/tache/SKILL.md", r"\*\*(\w+) tentatives au maximum\*\*"),
      ("agents/fiche.md", r"revérifie — (\w+) tentatives au plus"),
      ("enchainement.md", r"`BLOQUÉE` — (\w+) tentatives épuisées"),
      ("skills/tache/references/tache-blocage.md", r"# Bloquée après (\w+) tentatives"),
      ("skills/tache/references/tache-blocage.md", r"\(étape 5, après (\w+) tentatives\)"),
      ("methode-chantier.md", r"\| (\w+) tentatives, puis arrêt"))),
    ("majuscules d'un préfixe de fiche",
     ("methode-chantier.md", r"Un préfixe s'écrit en (\w+) majuscules"),
     (("CHANTIER.md", r"\*\*(\w+) majuscules\*\* depuis"),
      ("skills/chantier/SKILL.md", r"les \*\*(\w+)\s+majuscules\*\* qui nommeront"))),
    ("lignes sous lesquelles une fiche extraite arrête",
     ("skills/tache/SKILL.md", r"Fiche à moins de (\w+) lignes"),
     (("skills/jouer/SKILL.md", r"une fiche de moins de (\w+) lignes"),
      ("skills/enchainer/SKILL.md", r"une fiche de moins de (\w+) lignes"))),
    ("tours d'un questionnaire",
     ("methode-chantier.md", r"Un questionnaire se pose en (\w+) tours"),
     (("skills/tache/references/tache-contraintes.md", r"\*\*(\w+) tours\*\* : la section"),)),
    ("fiches par lancement d'enchainer",
     ("skills/enchainer/SKILL.md", r"Plafond : \*\*(\w+) fiches\*\* par lancement"),
     (("skills/enchainer/references/refus.md", r"le plafond de (\w+)\."),)),
)


def ecarts_nombres(racine, table=NOMBRES_RECOPIES):
    """Une ligne `ÉCART:` par copie qui diffère de sa source, ou par motif introuvable (copie reformulée)."""
    def premier(fichier, motif):
        m = re.search(motif, mod.lire(os.path.join(racine, fichier)))
        return m.group(1).lower() if m else None

    ecarts = []
    for nom, (fsrc, msrc), copies in table:
        source = premier(fsrc, msrc)
        if source is None:
            ecarts.append("ÉCART: %s — source introuvable dans %s" % (nom, fsrc))
            continue
        for fichier, motif in copies:
            copie = premier(fichier, motif)
            if copie != source:
                ecarts.append("ÉCART: %s — %s dit %s, la source (%s) dit %s" % (
                    nom, fichier, "rien (motif introuvable)" if copie is None else "« %s »" % copie, fsrc, source))
    return ecarts


def test_nombres_recopies(tmp_path):
    """COP (REF30) : chaque nombre recopié dans les commandes, les agents et la méthode est égal à sa source ;
    un écart, ou une copie reformulée, sort en `ÉCART:`. Lit le dépôt seul, jamais la machine."""
    racine = os.path.join(ICI, "..")
    ecarts = ecarts_nombres(racine)
    copies = sum(len(c) for _, _, c in NOMBRES_RECOPIES)
    assert (ecarts == []), ("COP : les %d nombres recopiés (%d copies) égaux à leur source" % (len(NOMBRES_RECOPIES), copies)) + "\n" + str("\n".join(ecarts))
    with tempfile.TemporaryDirectory(dir=tmp_path) as tnr:
        os.makedirs(os.path.join(tnr, "skills"))
        with open(os.path.join(tnr, "a.md"), "w", encoding="utf-8") as f:
            f.write("en deux tours\n")
        with open(os.path.join(tnr, "skills", "b.md"), "w", encoding="utf-8") as f:
            f.write("en trois tours\n")
        faux = (("tours", ("a.md", r"en (\w+) tours"), (("skills/b.md", r"en (\w+) tours"),
                                                        ("skills/b.md", r"absent (\w+)"))),)
        e = ecarts_nombres(tnr, faux)
        assert (len(e) == 2 and "« trois »" in e[0] and "introuvable" in e[1]), ("COP : une copie qui diffère, et une copie introuvable, sortent chacune en ÉCART:") + "\n" + str("\n".join(e))


def test_agents_suite_rapide():
    """REF42 : les suites entières faisaient 67 % du temps des sous-agents (bilan REF28→REF31). La règle vit à
    l'étape 4 de `skills/tache/SKILL.md` (`rapide` avant toute suite entière) ; `agents/fiche.md` y renvoie et dit
    une seule suite entière, à la fin ; `agents/relecture.md` joue AVANT par `--seul`, APRÈS la suite entière."""
    racine = os.path.join(ICI, "..")
    textes = {f: mod.lire(os.path.join(racine, f)) for f in
              ("skills/tache/SKILL.md", "agents/fiche.md", "agents/relecture.md")}
    attendus = (("skills/tache/SKILL.md", "avant toute suite entière : `<python> \"${CLAUDE_PLUGIN_ROOT}/scripts/vlp.py\" rapide"),
                ("agents/fiche.md", "itère par `<python> \"<kit>/scripts/vlp.py\" rapide <fiche>"),
                ("agents/fiche.md", "(étape 4 de `skills/tache/SKILL.md`)"),
                ("agents/fiche.md", "la suite entière, **une seule fois**, à la fin, avant `FAITE`"),
                ("agents/relecture.md", "`uv run --frozen pytest --seul <motif>`"),
                ("agents/relecture.md", "Dans APRÈS, la suite **entière**"))
    manquants = ["%s : « %s »" % (f, t) for f, t in attendus if t not in textes[f]]
    assert (manquants == []), ("REF42 : les deux agents portent la règle de rapide et de la suite entière (%d textes)" % len(attendus)) + "\n" + str("\n".join(manquants))


def test_chef_page_explique(tmp_path):
    """chef page, `explique` (2026-10-06) : l'Explique-moi en option — `data-explique` sur la page et `CAPACITES sample`
    en sortie avec `true`, rien sans, `GARDE:` pour un autre genre."""
    gabarit = mod.lire(os.path.join(ICI, "..", "templates", "rapport-choix.html"))
    d = {"projet": "Demo", "sujet": "essai", "titre": "Rapport d'essai", "date": "2026-10-01",
         "choix": [{"titre": "Quelle suite ?", "options": [{"valeur": "oui", "libelle": "Oui", "effet": "on suit"},
                                                           {"valeur": "non", "libelle": "Non", "effet": "on arrête"}]}]}
    div = '<div class="page" data-cle="Demo-2026-10-01-essai"%s>'
    with tempfile.TemporaryDirectory(dir=tmp_path) as tex:
        rendus = []
        for nom, explique in (("avec", True), ("sans", None), ("oui", "oui")):
            q = dict(d, explique=explique) if explique is not None else d
            chemin = os.path.join(tex, nom + ".html")
            s = io.StringIO()
            code = mod.cmd_chef_page(json.dumps(q, ensure_ascii=False), chemin, s, gabarit)
            page = mod.lire(chemin) if os.path.exists(chemin) else ""
            rendus.append((code, s.getvalue(), page))
    (c1, s1, p1), (c2, s2, p2), (c3, s3, p3) = rendus
    assert (c1 == 0 and s1.endswith("CARTES Q1\nCAPACITES sample\n") and div % " data-explique" in p1), ("chef page explique=true : data-explique sur la page, CAPACITES sample après CARTES") + "\n" + str(s1)
    assert (c2 == 0 and "CAPACITES" not in s2 and div % "" in p2), ("chef page sans explique : ni data-explique sur la page, ni CAPACITES") + "\n" + str(s2)
    assert (c3 == 1 and s3 == "GARDE: racine : « explique » vaut true ou false\n" and p3 == ""), ("chef page explique=\"oui\" : GARDE, sort 1, rien d'écrit") + "\n" + str(s3)
