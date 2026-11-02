"""REF22 (l'angle des bugs, passe 2) : deux défauts rejoués, un test chacun, écrit avant sa correction.

- le tri du soir : un chemin Windows cité entre accents graves garde ses antislashs (`fichiers_tri`), et deux rangs
  qui citent le même fichier en `\\` et en `/` restent liés (`groupes_tri`) ;
- le filet : un octet non UTF-8 dans le transcript ne remet pas le compte des tours à zéro (`comptoir_tours`).
"""
from aides import mod

H = mod.noyau.hooks
N = mod.noyau.nuit


def test_ref22_fichiers_tri_garde_les_antislashs():
    """REF22 : `` `scripts\\noyau\\nuit.py` `` donne `scripts\\noyau\\nuit.py`, pas `scriptsnoyaunuit.py` (le mode
    POSIX de `shlex` mangeait les antislashs) ; un rang qui cite le même fichier en `/` lui est lié par `groupes_tri`.
    Un chemin à espace entre guillemets reste entier, guillemets retirés, et `vlp.py archive` donne `vlp.py`."""
    assert N.fichiers_tri("touche `scripts\\noyau\\nuit.py`", "") == ["scripts\\noyau\\nuit.py"]
    assert N.fichiers_tri("`C:\\kit\\vlp.py archive`", "") == ["C:\\kit\\vlp.py"]
    assert N.fichiers_tri('cite `py "dossier x/m.py"`', "`vlp.py archive`") == ["dossier x/m.py", "vlp.py"]
    rangs = [["1", "`AAA` x", "touche `scripts\\noyau\\nuit.py`", "~2 fiches", "—"],
             ["2", "`BBB` y", "touche `scripts/noyau/nuit.py`", "~1 fiche", "—"]]
    codes = N.codes_todo(rangs)
    fichiers = [N.fichiers_tri(r[2], r[3]) for r in rangs]
    assert N.groupes_tri(rangs, codes, [0, 1], fichiers) == [([0, 1], ["fichier nuit.py : AAA, BBB"])]


def test_ref22_comptoir_tours_octet_non_utf8(tmp_path):
    """REF22 : dix tours écrits, un octet `\\xff` au quatrième : `comptoir_tours` en compte 10 — le compte n'est plus
    coupé à l'octet (il rendait 0, et `cmd_filet` croyait 80 tours restants). Un fichier absent rend toujours None."""
    p = tmp_path / "t.jsonl"
    with open(p, "wb") as f:
        for i in range(10):
            contenu = ',"content":"\xff"' if i == 3 else ""
            f.write(('{"message":{"id":"m%d","usage":{"a":1}%s}}\n' % (i, contenu)).encode("latin-1"))
    assert H.comptoir_tours(str(p)) == 10
    assert H.comptoir_tours(str(tmp_path / "absent.jsonl")) is None
