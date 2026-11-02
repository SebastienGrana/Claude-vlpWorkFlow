"""REF22, passe 2 (angle des bugs) : la découpe d'un chantier clos sans appel `clore`, l'« après clore » d'un clos,
la ligne **Fichiers** normalisée pour `nomme`, une ligne de transcript dont `message` est une chaîne, un coût négatif
relu en entier. Chaque test rejoue le défaut qu'un relecteur a confirmé."""
import json
import os
from decimal import Decimal

from aides import appel, commits, ecrire, ligne_close, lire, mod, transcript

T0 = 1790000000

FICHES = """# Chantier Q

**CLOS** le 2026-05-06.

## Le socle commun

## L'ordre des fiches

<!-- FICHE:Q1 -->
## Q1 [x] — Créer
**Session** : %s
**Critère de fin**
<!-- /FICHE -->
<!-- FICHE:Q2 -->
## Q2 [x] — Brancher
**Session** : %s
**Critère de fin**
<!-- /FICHE -->
"""

CLORE = [{"type": "tool_use", "id": "t", "name": "Bash", "input": {"command": "py scripts/vlp.py clore . --livre x"}}]


def chantier_clos(tmp_path, init_git, heures, sujets, retouche=None):
    """Un dépôt jetable sous `tmp_path` : un transcript aux `heures` (secondes après T0), `retouche(lignes)` appliqué à
    ses lignes JSON s'il est donné, un fichier de fiches **CLOS** dont Q1 et Q2 portent cette session, et les commits
    `sujets` ; rendre le chemin du fichier de fiches."""
    dep, s = str(tmp_path / "depot"), str(tmp_path / "s.jsonl")
    transcript(s, len(heures), [T0 + d for d in heures])
    if retouche:
        lignes = [json.loads(l) for l in lire(s).splitlines()]
        retouche(lignes)
        ecrire(s, "".join(json.dumps(l) + "\n" for l in lignes))
    ecrire(os.path.join(dep, "q.md"), FICHES % (s, s))
    init_git(dep)
    commits(dep, sujets, T0)
    return os.path.join(dep, "q.md")


def ligne_de(sortie, tete):
    """Le triplet (total, tours, usd) de la seule ligne de `sortie` qui commence par `tete` ; échoue sans elle, ou
    si elle ne se relit pas."""
    lignes = [l for l in sortie.splitlines() if l.startswith(tete)]
    assert len(lignes) == 1, sortie
    t = mod.triplet(lignes[0])
    assert t is not None, lignes[0]
    return t


def test_clos_sans_appel_clore(tmp_path, init_git):
    """REF22 : un clos dont aucune session ne porte l'appel `clore` (clôture faite ailleurs) reste un clos : Q2, à
    session sans commit, s'arrête au commit suivant qui nomme le préfixe (le journal, 600), et la dernière plage hors
    fiches au commit de clôture (900). Q1 1 tour, Q2 2 (400, 500), hors fiches 2 (700, 800), TOTAL 5 — mutant : le
    chantier pris pour ouvert, Q2 court jusqu'au bout (6 tours)."""
    q = chantier_clos(tmp_path, init_git, (200, 400, 500, 700, 800, 1000, 1100),
                      [(100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"), (600, "Journal : la mesure de Q2"),
                       (900, "Chantier Q clos : fini")])
    code, s = appel(["cout", q])
    assert code == 0, s
    assert ligne_de(s, "Q2 · ")[:2] == (200000, 2), s
    assert ligne_de(s, "hors fiches · ")[:2] == (200000, 2), s
    assert ligne_de(s, "TOTAL ")[:2] == (500000, 5), s
    par_fiche, total, hors = mod.couts_du_fichier(q, {}, None, [])    # la page, même découpe (dette PLI)
    assert ligne_de(par_fiche["Q2"], "")[:2] == (200000, 2), par_fiche
    assert total is not None, par_fiche
    assert hors is not None, par_fiche
    assert (total[:2], hors[:2]) == ((500000, 5), (200000, 2)), (total, hors)


def test_apres_clore_d_un_clos(tmp_path, init_git):
    """REF22 : sur un clos, `cout --a-clore` et `recompter --a-clore` comparent l'« à clore » à la découpe non coupée :
    le tour de 800 suit l'appel `clore` (700) dans la dernière plage hors fiches (600, 900] — après clore 1 tour,
    100 000. Mutant : comparé au TOTAL déjà coupé à l'appel `clore`, après clore vaut 0 par construction."""
    def appel_clore(lignes):
        """Le 3e tour (700) lance `vlp.py clore`."""
        lignes[2]["message"]["content"] = CLORE
    q = chantier_clos(tmp_path, init_git, (200, 400, 700, 800),
                      [(100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"), (600, "Q2 : Brancher"),
                       (900, "Chantier Q clos : fini")], appel_clore)
    projet = str(tmp_path / "depot" / "pq")
    ecrire(os.path.join(projet, "CHANTIER.md"), "# C\n\n- **contexte** : ./\n- **index** : 00-INDEX.md\n")
    ecrire(os.path.join(projet, "00-INDEX.md"), "| Fichier | Lire quand |\n|---|---|\n"
           "| `../q.md` | chantier **clos** « Q », `Q1..Q2` |\n")
    ecrire(os.path.join(projet, "artefacts", "feuille-de-route.html"),
           "    <!-- ZONE:clos — test -->\n      <table>\n        <tbody>\n"
           + ligne_close(mod.arrondi(250000)) + "        </tbody>\n      </table>\n")
    (code, s), (code2, s2) = appel(["cout", q, "--a-clore"]), appel(["recompter", projet, "--a-clore"])
    assert code == 0, s
    assert ligne_de(s, "TOTAL ")[:2] == (300000, 3), s
    assert ligne_de(s, "à clore · ")[:2] == (300000, 3), s
    assert ligne_de(s, "après clore · ")[:3] == (100000, 1, Decimal("0.50")), s
    assert code2 == 0, s2
    assert s2.splitlines()[0].endswith(" · à clore 300 000 · après clore 100 000"), s2


def test_fichiers_normalises_pour_nomme():
    """REF22 : la ligne **Fichiers** se lit normalisée, comme `noms_ecrits` — `\\` en `/`, `./` ôté, casse — avant
    `nomme` : le chemin que rend `git diff` n'est pas `HORS FICHE` pour `scripts\\noyau\\x.py`, `./scripts/noyau/x.py`
    ni `Scripts/noyau/x.py`. Mutant : la ligne prise telle quelle."""
    formes = ("`scripts\\noyau\\x.py`", "`./scripts/noyau/x.py`", "`Scripts/noyau/x.py`", "`scripts/noyau/x.py`")
    rates = [f for f in formes if not mod.nomme("scripts/noyau/x.py", mod.noms_fichiers(["**Fichiers** : " + f]))]
    assert not rates, rates
    assert not mod.nomme("scripts/noyau/y.py", mod.noms_fichiers(["**Fichiers** : `scripts\\noyau\\x.py`"]))


def test_message_chaine_dans_le_transcript(tmp_path, init_git):
    """REF22 : une ligne de transcript qui contient « clore » et dont `message` est une chaîne ne fait pas tomber
    `heure_clore` (ni `cout` avec lui) : elle n'est pas un appel. Mutant : `message` supposé objet, AttributeError."""
    def ligne_systeme(lignes):
        """Une ligne `system` à 650, son `message` en chaîne qui cite « clore »."""
        lignes.insert(1, {"type": "system", "message": "clore ?", "timestamp": "2026-09-21T14:24:10.000Z"})
    q = chantier_clos(tmp_path, init_git, (200, 700),
                      [(100, "Chantier Q ouvert : cadré"), (300, "Q1 : Créer"), (600, "Q2 : Brancher"),
                       (900, "Chantier Q clos : fini")], ligne_systeme)
    assert mod.heure_clore(q, lire(q).splitlines()) is None
    code, s = appel(["cout", q])
    assert code == 0, s
    assert ligne_de(s, "TOTAL ")[:2] == (200000, 2), s


def test_cout_negatif_relu():
    """REF22 : `triplet` relit tout ce que `ligne_cout` écrit, tours négatifs compris (`couts` sans Git, chantier
    TAR). Mutant : `(\\d+) tours`, la ligne n'est plus relue (None)."""
    assert mod.triplet(mod.ligne_cout(-5, -3, Decimal("-0.10"))) == (-5, -3, Decimal("-0.10"))
    assert mod.triplet(mod.ligne_cout(1500, 2, Decimal("0.10"))) == (1500, 2, Decimal("0.10"))
