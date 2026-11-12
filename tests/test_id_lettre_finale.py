"""Un id de fiche à lettre finale (`SEG4b`, fiche ajoutée en cours de chantier) est un id comme les autres.

Nuit SEG d'Emergence-Ants, 2026-11-12 : les motifs du kit écrits `[A-Z]{1,3}[0-9]+` le perdaient — la note de `SEG4b`
tombait sur `SEG3` (corrigé dans `notes.constates`), son commit `SEG4b : …` ne comptait pas comme commit de fiche (la
GARDE de coût « SEG4b porte une session sans commit »), ses titres, sa marque et sa plage échappaient aux crochets et à la
page. Le motif vit à un seul endroit, `noyau.commun.ID_FICHE` ; chaque test ici en sonde un usage.
"""
import re

import noyau.clore
import noyau.clos
import noyau.commun
import noyau.hooks
import noyau.niveau
import noyau.page

ID = "SEG4b"


def groupe(trouve, n=1):
    """Le groupe `n` d'une correspondance, après avoir vérifié qu'elle existe (un motif qui ne lit rien fait tomber le test)."""
    assert trouve is not None
    return trouve.group(n)


def test_le_motif_unique_lit_la_lettre_finale_et_rien_de_plus():
    """`ID_FICHE` prend `SEG4b` entier, `SEG4` aussi ; une majuscule après le chiffre ne fait pas partie de l'id."""
    motif = re.compile(r"^(%s)\b" % noyau.commun.ID_FICHE)
    assert groupe(motif.match("SEG4b : x")) == "SEG4b"
    assert groupe(motif.match("SEG4 : x")) == "SEG4"
    assert not motif.match("SEG4B : x")


def test_un_commit_de_fiche_a_lettre_finale_est_un_commit_de_fiche():
    """`SEG4b : …` est un commit de fiche (`COMMIT_FICHE`), et `prefixes_joues` en tire le préfixe `SEG`."""
    assert groupe(noyau.page.COMMIT_FICHE.match("SEG4b : Deux fourmilières jumelles")) == ID
    assert groupe(noyau.page.COMMIT_FUSION.match("Fusion : SEG4b")) == ID
    assert noyau.clore.prefixes_joues("SEG4b : un\nautre sujet\n") == ["SEG"]


def test_les_crochets_lisent_le_titre_la_marque_et_le_code():
    """Le crochet REF10 et ses voisins : titre `## SEG4b [ ]`, marque `<!-- FICHE:SEG4b -->`, code dans un texte."""
    titre = noyau.hooks.TITRE_FICHE.match("## SEG4b [ ] — Deux fourmilières")
    assert groupe(titre) == ID
    assert groupe(titre, 2) == " "
    assert noyau.hooks.MARQUE.match("<!-- FICHE:SEG4b -->")
    assert noyau.hooks.CODE_FICHE.findall("joue SEG4b puis SEG5") == [ID, "SEG5"]


def test_les_plages_acceptent_une_borne_a_lettre_finale():
    """Une plage dont la dernière fiche est `SEG4c` : la page, le niveau et l'index de clôture la lisent."""
    assert groupe(noyau.niveau.PLAGE_TEXTE.search("fiches SEG1–SEG4c"), 0) == "fiches SEG1–SEG4c"
    assert groupe(noyau.clos.PLAGE_CLOS.search('<td class="mono">SEG1–SEG4c</td>')) == "SEG"
    assert groupe(noyau.clos.PLAGE_INDEX.match("| `20` | x | `SEG1..SEG4c` |"), 2) == "SEG"
