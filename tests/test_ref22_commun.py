"""REF22, l'angle des bugs : `noyau/commun.py` (`lire`, `numero_ligne`) et `noyau/ouvrir.py` (`cmd_ouvrir`) — le BOM
d'un fichier de fiches, un fichier non UTF-8 réécrit sans un mot, le numéro de fichier à trois chiffres.
"""
import os

from aides import appel, ecrire, mod

CARTE = "# C\n\n- **contexte** : ctx/\n- **index** : ctx/00-INDEX.md\n- **artefact du chantier** : aucun\n"
CLAUDE = "| La tâche | Ouvrir |\n|---|---|\n| relire un chantier clos | `ctx/00-INDEX.md` |\n"


def projet(t, index="| Fichier | Lire |\n|---|---|\n| `10-e.md` | on relit |\n"):
    """Un projet équipé minimal dans `t` : CHANTIER.md, l'index `index`, le routage de CLAUDE.md ; rend `t`."""
    ecrire(os.path.join(t, "CHANTIER.md"), CARTE)
    ecrire(os.path.join(t, "ctx", "00-INDEX.md"), index)
    ecrire(os.path.join(t, "CLAUDE.md"), CLAUDE)
    return t


def octets(chemin):
    """Les octets du fichier `chemin`."""
    with open(chemin, "rb") as fh:
        return fh.read()


def test_ref22_lire_retire_le_bom(tmp_path):
    """REF22 : un fichier de fiches écrit avec BOM (Bloc-notes, `Out-File -Encoding utf8`) garde son titre
    `# Chantier ` en tête : `ouvrir` y pose la marque, `courant_de` le voit."""
    t = projet(str(tmp_path / "p"))
    with open(os.path.join(t, "ctx", "30-q.md"), "w", encoding="utf-8-sig", newline="") as fh:
        fh.write("# Chantier Q — Un titre\n\n## Q1 [ ] — a\n")
    code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Q"])
    assert (code, "GARDE" in s, mod.courant_de(t)) == (0, False, "ctx/30-q.md"), s


def test_ref22_ouvrir_refuse_un_fichier_non_utf8(tmp_path):
    """REF22 : un fichier de fiches en cp1252 — ses `é` illisibles en UTF-8 — n'est pas réécrit par `ouvrir` :
    `GARDE:`, sort 1, ni lui ni CHANTIER.md ne bougent d'un octet."""
    t = projet(str(tmp_path / "p"))
    fiches = os.path.join(t, "ctx", "30-q.md")
    with open(fiches, "w", encoding="cp1252", newline="") as fh:
        fh.write("# Chantier Q — Un titre accentué\n\n## Q1 [ ] — été\n")
    avant = (octets(fiches), octets(os.path.join(t, "CHANTIER.md")))
    code, s = appel(["ouvrir", t, "--fiches", "ctx/30-q.md", "--titre", "Q"])
    apres = (octets(fiches), octets(os.path.join(t, "CHANTIER.md")))
    assert (code, s.startswith("GARDE:"), apres == avant) == (1, True, True), s


def test_ref22_numero_ligne_a_trois_chiffres():
    """REF22 : `numero_ligne` lit le numéro entier — `125-…` vaut 125, pas 12 —, et `archiver` trie l'archive
    `09, 35, 100, 118` ; une ligne sans numéro passe après toutes."""
    lignes = ["| `118-c.md` | x — **clos** |", "| `09-a.md` | x — **clos** |", "| `100-b.md` | x — **clos** |",
              "| `35-d.md` | x — **clos** |"]
    _, arch, _ = mod.archiver(lignes, None, "00-INDEX-archive.md")
    assert ([mod.numero_ligne(l) for l in arch[-4:]], mod.numero_ligne("| `999-z.md` |") < mod.numero_ligne("| x |")) \
        == ([9, 35, 100, 118], True), arch


def test_ref22_ouvrir_range_apres_le_plus_grand_numero(tmp_path):
    """REF22 : `ouvrir` pose la ligne du nouveau fichier après le plus grand numéro entier de l'index — après
    `125-a.md`, pas après `40-z.md`."""
    t = projet(str(tmp_path / "p"), "| Fichier | Lire |\n|---|---|\n| `40-z.md` | z |\n| `125-a.md` | a |\n| `05-d.md` | d |\n")
    ecrire(os.path.join(t, "ctx", "130-n.md"), "# Chantier N — n\n\n## N1 [ ] — a\n")
    code, s = appel(["ouvrir", t, "--fiches", "ctx/130-n.md", "--titre", "n"])
    idx = mod.lignes_de(os.path.join(t, "ctx", "00-INDEX.md"))
    assert (code, [l.split("`")[1] for l in idx[2:]]) == (0, ["40-z.md", "125-a.md", "130-n.md", "05-d.md"]), s
