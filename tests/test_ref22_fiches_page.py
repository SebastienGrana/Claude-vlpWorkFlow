"""REF22, l'angle des bugs : les défauts rejoués de `noyau/fiches.py`, `page.py`, `carte.py`, `clos.py` et `notes.py`,
chacun par le test qui le montrait rouge avant sa correction. `conftest.py` isole l'environnement et la config Git.
"""
import io
import os
import subprocess

from aides import appel, commits, ecrire, lire, transcript
from noyau import carte, clos, fiches, page, sessions

CASE_CITEE = ["# Fiches", "", "## F1 [x] — Fait", "", "## F2 [ ] — compter les cases `[x]`", "", "## F3 [ ] — Après"]


def test_ref22_case_citee_dans_le_titre_n_est_pas_cochee(tmp_path):
    """REF22 (1) : un `[x]` cité dans le titre ne coche pas la fiche — `fiches_du_fichier` et `carte.fiches` jugent la
    case elle-même."""
    vus = [(f[0], f[2]) for f in page.fiches_du_fichier(CASE_CITEE)]
    assert vus == [("F1", True), ("F2", False), ("F3", False)], "REF22 : page.fiches_du_fichier, case citée" + str(vus)
    chemin = os.path.join(tmp_path, "05-f.md")
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(CASE_CITEE) + "\n")
    assert carte.fiches(chemin)[2] == "F2", "REF22 : carte.fiches, PROCHAINE saute F2" + str(carte.fiches(chemin))


ERREUR_AU_MILIEU = """<!-- FICHE:VAL4 -->
## VAL4 [x] — Quatrième

**Tentatives** (2026-01-05) — non résolu.
1. a
2. b
Erreur : vieux
3. c
**Dépend de** : rien.
<!-- /FICHE -->
"""


def test_ref22_refuser_une_seule_ligne_erreur(tmp_path):
    """REF22 (2) : un bloc dont la ligne `Erreur :` n'est pas en dernier — `cocher --refuser` n'y laisse qu'une ligne
    `Erreur :`, au nouveau motif, et `refus_du_bloc` relit ce motif."""
    f = os.path.join(tmp_path, "ctx", "09-v4.md")
    ecrire(f, ERREUR_AU_MILIEU)
    code, s = appel(["cocher", f, "VAL4", "--refuser", "neuf", "--date", "2026-01-06"])
    texte = lire(f)
    attendu = ERREUR_AU_MILIEU.replace("## VAL4 [x]", "## VAL4 [ ]").replace(
        "2. b\nErreur : vieux\n3. c\n", "2. b\n3. c\n4. FAITE refusée à la relecture.\nErreur : neuf\n")
    assert (code, texte) == (0, attendu), "REF22 : cocher --refuser, une seule ligne Erreur\n" + s + texte
    bloc = texte.split("\n")[3:9]
    assert fiches.refus_du_bloc(bloc)[1] == "neuf", "REF22 : refus_du_bloc relit le nouveau motif" + str(bloc)


def test_ref22_commiter_statut_illisible_apres_la_coche(depot, monkeypatch):
    """REF22 (3) : `git status` en échec après la coche — `commiter` dit `GARDE:` et sort 1, sans commit vide."""
    f = os.path.join(depot, "ctx", "fiches.md")
    ecrire(f, "# Essai\n\n<!-- FICHE:C1 -->\n## C1 [ ] — Toucher a\n\n**Fichiers** : `src/a.py`.\n<!-- /FICHE -->\n")
    ecrire(os.path.join(depot, "src", "a.py"), "x = 1\n")
    for args in (["add", "-A"], ["commit", "-q", "-m", "départ"]):
        subprocess.run(["git"] + args, cwd=depot, check=True, capture_output=True)
    ecrire(os.path.join(depot, "src", "a.py"), "x = 2\n")
    vrai, appels = fiches.chemins_changes, []

    def statut(racine):
        """Le vrai statut au premier appel (avant la coche), None ensuite : `git status` en échec."""
        appels.append(racine)
        return vrai(racine) if len(appels) == 1 else None
    monkeypatch.setattr(fiches, "chemins_changes", statut)
    code, s = appel(["commiter", f, "C1"])
    sujets = subprocess.run(["git", "log", "--format=%s"], cwd=depot, capture_output=True, encoding="utf-8",
                            check=True).stdout.split("\n")
    assert (code, "\nGARDE: git status" in s, sujets[0]) == (1, True, "départ"), \
        "REF22 : commiter, statut illisible après la coche\n" + s + str(sujets)


def test_ref22_recompter_garde_le_prix_de_tete():
    """REF22 (4) : `recompter --ecrire` (`marquer`) et `--essais --ecrire` (`marquer_essais`) gardent le prix que
    `clore` pose en tête de cellule, toujours en tête — `PRIX_CLOS` le relit."""
    tete = "5,66 $ · "
    vus = [clos.marquer(tete + "recompté (REC), était 600 000 · ≈650,0k (650 000)", 650000, 700000, "découpe"),
           clos.marquer(tete + "≈650,0k (650 000)", 650000, 700000, "découpe"),
           clos.marquer(tete + "≈650,0k (650 000)", 650000, None, "gardé — sans session"),
           clos.marquer_essais(tete + "≈650,0k (650 000)", 650000, 50000)]
    assert vus == [tete + "recompté (REC), était 600 000 · ≈700,0k (700 000)",
                   tete + "recompté (REC), était 650 000 · ≈700,0k (700 000)",
                   tete + "non recompté — sans session · ≈650,0k (650 000)",
                   tete + "essais (ESD) +50 000 · ≈700,0k (700 000)"], "REF22 : le prix de tête survit, en tête" + str(vus)
    corps = "".join('          <tr>\n            <td class="mono">%s</td>\n          </tr>\n' % c for c in vus)
    assert clos.prix_clos(corps)[1] == 4, "REF22 : prix_clos relit chaque prix" + str(clos.prix_clos(corps))


def test_ref22_repeindre_compte_chaque_ligne_sans_page(tmp_path, monkeypatch):
    """REF22 (5) : trois lignes closes sans fichier de fiches — `repeindre` en compte trois « sans page », pas une."""
    rangs = [("<tr>", p, 0, None) for p in ("A", "B", "C")]
    monkeypatch.setattr(clos, "clos_du_projet", lambda projet, sortie: ("", 0, 0, rangs))
    s = io.StringIO()
    code = clos.cmd_repeindre(str(tmp_path), s, a_blanc=True)
    lignes = s.getvalue().splitlines()
    assert (code, len([l for l in lignes if l.startswith("SANS PAGE ")]), " 3 sans page" in lignes[-1]) == (0, 3, True), \
        "REF22 : repeindre, chaque ligne sans page comptée\n" + s.getvalue()


T0 = 1_700_000_000


def test_ref22_page_coupe_au_commit_au_titre_comme_cout(depot, monkeypatch):
    """REF22 (6) : deux commits `AVL1 : étape` puis `AVL1 : <titre>` — la page (`couts_du_fichier`) coupe la fiche au
    commit au titre, comme `cout` (`sessions.decoupe_et_heures`), pas à l'étape."""
    f = os.path.join(depot, "ctx", "05-avl.md")
    ecrire(f, "# Fiches\n\n## AVL1 [x] — Le titre\n\n**Session** : s1\n")
    commits(depot, [(0, "Chantier AVL ouvert"), (100, "AVL1 : étape"), (300, "AVL1 : Le titre")], T0)
    vues = []
    monkeypatch.setattr(page, "couts", lambda fiches_, anciens, total, gardes, heures=None, *r: vues.append(heures))
    page.couts_du_fichier(f, {}, None, [])
    assert [v and v[0] for v in vues] == [{"AVL1": T0 + 300}], "REF22 : la page coupe au commit au titre" + str(vues)
    assert vues[0] == sessions.decoupe_et_heures(f)[3][1], "REF22 : les heures de la page sont celles de cout" + str(vues)


def test_ref22_session_d_en_tete_mesuree_sans_session_de_fiche(depot):
    """REF22 (8) : aucune fiche n'a de session, l'en-tête en a une (deux tours, avant le commit de la fiche) —
    `couts_du_fichier`, ce que la page et `clore` sans page écrivent, la mesure comme `cout` (`decouper`)."""
    t = os.path.join(depot, "s0.jsonl")
    transcript(t, 2, heures=[T0 + 100, T0 + 200])
    f = os.path.join(depot, "ctx", "05-avl.md")
    ecrire(f, "# Fiches\n\n**Session** : %s\n\n## AVL1 [x] — Le titre\n" % t)
    commits(depot, [(0, "Chantier AVL ouvert"), (300, "AVL1 : Le titre")], T0)
    total = page.couts_du_fichier(f, {}, None, [])[1]
    cout = page.plus(*sessions.totaux(sessions.decouper(f)[0]))[0]
    assert (total and total[0], cout) == (200000, 200000), "REF22 : la session d'en-tête mesurée" + str((total, cout))


def test_ref22_creer_garde_les_antislashs(tmp_path):
    """REF22 (9) : un titre ou un nom de projet à antislash (`C:/Users`, `scripts/noyau` écrits à la Windows) passe
    tel quel dans la page neuve — ni `re.PatternError`, ni vrai saut de ligne."""
    titre, projet = r"C:\Users et scripts\noyau", r"P\nom"
    html = page.creer(os.path.join(tmp_path, "05-f.md"), projet, titre, "R")
    vus = ["<title>%s — %s</title>" % (projet, titre), "<h1>%s</h1>" % titre, '<div class="eyebrow">%s · fiches ' % projet]
    assert [v for v in vus if v not in html] == [], "REF22 : creer garde les antislashs"


def test_ref22_page_en_echec_n_ecrit_pas_l_abri(tmp_path):
    """REF22 (10) : `page` dont la régénération lève (un fichier sans titre de fiche) — `GARDE:`, sortie 1, et l'abri
    `.md` n'a rien reçu : la relance ne double pas l'entrée du journal."""
    f = os.path.join(tmp_path, "ctx", "05-f.md")
    ecrire(f, "# Fiches\n\nAucun titre de fiche.\n")
    pg = os.path.join(tmp_path, "ctx", "artefacts", "05-f.html")
    argv = ["page", f, pg, "--creer", "--projet", "P", "--titre", "T", "--resultat", "R", "--journal", "j1",
            "--date", "2026-01-02"]
    vus = [appel(argv), appel(argv)]
    md = os.path.splitext(pg)[0] + ".md"
    abri = lire(md) if os.path.exists(md) else ""
    assert [(c, s.startswith("GARDE:")) for c, s in vus] == [(1, True), (1, True)], "REF22 : page en échec" + str(vus)
    assert "j1" not in abri, "REF22 : page en échec, abri intact\n" + abri
