"""Les noms du cœur pas encore sortis, lus au moment de l'appel (REF45, option 1 tranchée par l'utilisateur le 2026-10-18).

27 des 29 sections de `vlp_coeur.py` s'appellent en cycle : un module sorti lit encore des noms restés dans la
façade. Il les lit `coeur.<nom>`, jamais par import — la façade l'importe avant d'avoir défini ces noms. `coeur.noms`
est l'espace de la façade (`globals()`), posé par elle avant d'importer les modules : un test qui remplace
`mod.git_texte` remplace aussi ce que lisent les modules. Quand un nom sort à son tour (`REF46` à `REF49`), son
`coeur.` devient un import.
"""
from typing import Any


class Espace:
    """Un espace de noms lu à chaque accès : `coeur.champ` rend `noms["champ"]` au moment de l'appel."""

    def __init__(self):
        self.noms: dict[str, Any] = {}

    def __getattr__(self, nom: str) -> Any:
        try:
            return self.noms[nom]
        except KeyError:
            raise AttributeError("coeur.%s : nom absent de la façade" % nom) from None


coeur = Espace()
