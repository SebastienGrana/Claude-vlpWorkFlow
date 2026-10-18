"""La décision d'`ecarts_git` (`noyau/niveau.py`), sans Git (REF47) : `source_ignore` lit `git check-ignore -v`."""
import aides  # noqa: F401 — charge la façade, qui pose `coeur` avant d'importer ses modules
from noyau import niveau


def test_source_ignore():
    assert niveau.source_ignore(".gitignore:3:context AI/\tcontext AI/a.md\n") == ".gitignore:3"   # le fichier et sa ligne : « ignoré par .gitignore:3 »
    assert niveau.source_ignore("C:/x/.git/info/exclude:1:*.md\tz.md") == "C:/x/.git/info/exclude:1"
    assert niveau.source_ignore("") == "?"
