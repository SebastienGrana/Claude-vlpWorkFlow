"""REF44 : la photo des noms publics de la façade `vlp_coeur.py` — les siens et ceux de son état (`noyau/etat.py`),
sans les modules importés. Prise sur le code d'avant la découpe (744 noms, comparés au code de `HEAD` le
2026-10-18), elle reste la même à chaque pas : un nom perdu crie (plan de `REF18`, note `122`)."""
import types

from aides import mod


def noms_publics(m):
    """Les noms publics de `m` et de son module `etat` s'il en a un, sans modules, triés."""
    espaces = [vars(m)] + ([vars(m.etat)] if isinstance(getattr(m, "etat", None), types.ModuleType) else [])
    return sorted({n for e in espaces for n, v in e.items() if not n.startswith("_") and not isinstance(v, types.ModuleType)})


def test_noms_publics(snapshot):
    assert noms_publics(mod) == snapshot
