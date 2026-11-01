"""REF22 (l'angle des bugs) : les défauts rejoués de `noyau/feuille.py`, `noyau/ordre.py` et `noyau/niveau.py` —
chacun son test, écrit rouge avant sa correction. Aucun ne lit la machine ni ne lance Git."""
from noyau import feuille, niveau, ordre

CARTE_NOTES = [
    "# Chantier courant",
    "",
    "## Chantiers clos",
    "",
    "| Chantier | Fichier |",
    "|---|---|",
    "| A | `ctx/10-a.md` |",
    "",
    "## Notes importantes",
    "",
    "Une note qui doit rester.",
    "",
    "Lettres de fiche déjà prises : A.",
]


def test_ref22_sans_table_des_clos_garde_la_section_suivante():
    """REF22 : `sans_table_des_clos` ne retire que la table des clos ; une section `## Notes importantes` placée
    entre elle et la ligne des lettres prises reste, à sa place."""
    neuve = niveau.sans_table_des_clos(CARTE_NOTES, ["- `ctx/10-a.md`"])
    assert neuve is not None, "REF22 : la table se retire, l'index nomme son fichier"
    attendu = (["# Chantier courant", ""] + niveau.entete_clos()
               + ["## Notes importantes", "", "Une note qui doit rester.", "", "Lettres de fiche déjà prises : A."])
    assert neuve == attendu, "REF22 : la section d'après la table reste\n" + "\n".join(neuve)


def test_ref22_bornes_cout_apres_fleche_exige_des_fiches():
    """REF22 : après la dernière `→`, une date ou un nombre suivi d'une autre unité n'est pas une estimation en
    fiches ; la plage suivie de « fiche(s) » d'avant fait foi. Une plage nue après `→` reste lue (NUI38)."""
    lues = tuple(feuille.bornes_cout(c) for c in (
        "~3 fiches → 2026-10-12 : 5 fiches", "~3 fiches → 2 séances", "~1 fiche → 2 à 3 fiches, 7,4 à 11 $",
        "3,5 fiches → 7 à 10,5, 26 à 39 $"))
    assert lues == ((5.0, 5.0), (3.0, 3.0), (2.0, 3.0), (7.0, 10.5)), "REF22 : bornes_cout après `→`\n" + str(lues)


def pas_(numero, depend=""):
    """Un pas du chemin d'`ordre`, du projet `p`, de code `P<numero>`."""
    return {"projet": "p", "code": "P%s" % numero, "numero": str(numero), "depend": depend}


def test_ref22_deps_todo_lit_comme_la_feuille():
    """REF22 : `deps_todo` lit « Dépend de » comme `feuille.dependances` : `1..9` touche chaque ligne de 1 à 9 de la
    TODO (une ligne absente du milieu de la plage n'est pas une garde) ; `rien`, `aucune` ne sont pas illisibles."""
    pas = [pas_(1), pas_(4), pas_(9), pas_(12)]
    numeros = {"p": {"1", "4", "9", "12"}}
    deps, hors, gardes, illisible = ordre.deps_todo(pas_(12, "1..9"), pas, numeros)
    assert ([d["code"] for d in deps], hors, gardes, illisible) == (["P1", "P4", "P9"], 0, [], False), (
        "REF22 : deps_todo, plage 1..9\n" + str((deps, hors, gardes, illisible)))
    seul = ordre.deps_todo(pas_(12, "7, 1..2"), pas, numeros)
    assert seul == ([pas[0]], 0, ["pas P12 : dépend de la ligne 7, absente de la TODO de p"], False), (
        "REF22 : deps_todo, un numéro seul absent reste une garde, pas le bord d'une plage\n" + str(seul))
    vides = tuple(ordre.deps_todo(pas_(12, mot), pas, numeros) for mot in ("rien", "aucune", "Aucun"))
    assert vides == (([], 0, [], False),) * 3, "REF22 : deps_todo, « rien » et « aucune »\n" + str(vides)


def test_ref22_dependances_chiffre_colle_pas_un_rang():
    """REF22 : hors accents graves, un chiffre collé à une lettre ou à un tiret n'est pas un rang (`V2`, `V1-3`) ;
    un numéro seul et une plage le restent (FEU8)."""
    lus = (feuille.est_bloque("après la V2", [], {"2"}), feuille.dependances("V1-3 plus tard"),
           feuille.est_bloque("3", [], {"3"}), feuille.est_bloque("1..9", [], {"5"}), feuille.dependances("2, 4..5"))
    assert lus == (False, ([], set()), True, True, ([], {"2", "4", "5"})), "REF22 : dependances\n" + str(lus)


def test_ref22_poser_champ_garde_la_ligne_vide():
    """REF22 : `poser_champ` remplace la ligne du champ sans avaler la ligne vide au-dessus."""
    texte = "# Chantier\n\n- **artefact feuille de route** : a\n\n- **artefact archive** : vieux\n"
    neuf = feuille.poser_champ(texte, "artefact archive", "neuf", "artefact feuille de route")
    assert neuf == "# Chantier\n\n- **artefact feuille de route** : a\n\n- **artefact archive** : neuf\n", (
        "REF22 : poser_champ\n" + repr(neuf))
